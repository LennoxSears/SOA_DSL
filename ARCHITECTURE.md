# SOA DSL Architecture - Three-Layer Design

## Overview

The SOA DSL uses a three-layer architecture that separates concerns between user-facing specifications, monitor implementations, and final code generation.

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Universal Specification (User Input)             │
│  ─────────────────────────────────────────────────────────  │
│  Model/Monitor Agnostic - Describes WHAT to check          │
│  - Device types (nmos_core, cap_low, etc.)                 │
│  - Check types (voltage, current, temperature, aging)      │
│  - Limits (min/max, steady/transient)                      │
│  - Conditions (state-dependent, temp-dependent)            │
│                                                             │
│  File: examples/soa_rules_universal.yaml                   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Middleware: Converter                                      │
│  ─────────────────────────────────────────────────────────  │
│  Uses:                                                      │
│  - config/device_library.yaml (device characteristics)     │
│  - config/monitor_library.yaml (monitor capabilities)      │
│                                                             │
│  Logic:                                                     │
│  - Selects appropriate monitor type                        │
│  - Maps universal parameters to monitor parameters         │
│  - Generates monitor-specific expressions                  │
│                                                             │
│  Tool: src/soa_dsl/converter.py                            │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Monitor Specification (Intermediate)             │
│  ─────────────────────────────────────────────────────────  │
│  Monitor/Model Aware - Describes HOW to check              │
│  - Monitor types (ovcheck, ovcheck6, ovcheckva_mos2, etc.) │
│  - Model names and sections                                │
│  - Monitor-specific parameters                             │
│  - Branch expressions                                       │
│                                                             │
│  File: output/monitors_generated.yaml                      │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Generator                                                  │
│  ─────────────────────────────────────────────────────────  │
│  Generates Spectre netlist code                            │
│  - Verilog-A includes                                      │
│  - Parameter definitions                                    │
│  - Monitor instantiations                                   │
│                                                             │
│  Tool: src/soa_dsl/generator.py                            │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: Spectre Code (Final Output)                      │
│  ─────────────────────────────────────────────────────────  │
│  Executable Spectre netlist                                 │
│  - simulator lang=spectre                                   │
│  - section base with includes                               │
│  - model definitions                                        │
│                                                             │
│  File: output/soachecks.scs                                │
└─────────────────────────────────────────────────────────────┘
```

## Layer 1: Universal Specification

### Purpose
User-facing format that describes SOA rules in terms of physics and electrical constraints, without knowledge of specific monitor implementations.

### Key Features
- **Device-centric**: Rules apply to device types (nmos_core, cap_low)
- **Physics-based**: Describes voltage, current, temperature, aging
- **Declarative**: No expressions to parse, structured data only
- **Portable**: Can target different monitor sets or simulators

### Example
```yaml
rules:
  - name: "NMOS Core Oxide Risk"
    applies_to:
      devices: [nmos_core]
    check:
      type: voltage
      measure:
        - signal: V(g,b)
          message: "Vgb_OXrisk"
        - signal: V(g,s)
          message: "Vgs_OXrisk"
    limits:
      steady:
        min: -1.32
        max: 1.32
```

## Configuration Files

### device_library.yaml
Defines device characteristics and node mappings.

```yaml
devices:
  nmos_core:
    type: mosfet
    polarity: n
    nodes: [g, d, s, b]
    subcircuit: [nch_mac, nch_lvt_mac, nch_hvt_mac]
    has_states: true
    state_parameter: vth
```

### monitor_library.yaml
Defines monitor capabilities and parameter mappings.

```yaml
monitors:
  ovcheck6:
    description: "Multi-branch voltage check (up to 6 branches)"
    capabilities:
      - voltage_check
      - multi_branch
    branch_limit: 6
    parameter_patterns:
      voltage:
        min: "vlow{N}"
        max: "vhigh{N}"
```

## Middleware: Converter

### Monitor Selection Logic

The converter automatically selects the appropriate monitor type based on rule characteristics:

| Rule Characteristic | Monitor Type |
|-------------------|--------------|
| Single voltage/current signal | `ovcheck` |
| Multiple voltage/current signals | `ovcheck6` |
| State-dependent (on/off) | `ovcheckva_mos2` |
| Temperature-dependent | `ovcheckva_pwl` |
| Aging (HCI/TDDB) | `ovcheckva_ldmos_hci_tddb` |
| Parameter check | `parcheckva3` |
| Self-heating | `ovcheck` (with thermal params) |

### Parameter Mapping

Universal parameters are mapped to monitor-specific parameters:

```
Universal                    Monitor (ovcheck6)
─────────────────────────   ──────────────────────
steady.min: -1.32      →    vlow1: -1.32
steady.max: 1.32       →    vhigh1: 1.32
measure[0].signal      →    branch1: "V(g,b)"
measure[0].message     →    message1: "Vgb_OXrisk"
time_limit: review     →    tmaxfrac: tmaxfrac3
```

### Expression Generation

For temperature-dependent limits:
```yaml
# Universal
temperature_dependent:
  reference_temp: 25
  reference_value: 0.9943
  temp_coefficient: -0.0006

# Generated
vhigh: "0.9943 - 0.0006 * (T - 25)"
```

## Layer 2: Monitor Specification

### Purpose
Intermediate format that directly maps to Verilog-A monitor implementations. Can be:
- Generated by converter (from universal spec)
- Written manually (for advanced users)
- Used for debugging/inspection

### Example
```yaml
monitors:
  - name: "NMOS Core Oxide Risk"
    monitor_type: ovcheck6
    model_name: ovcheck6_nmos_core_nmos_core_oxide_risk
    section: soacheck_nmos_core_nmos_core_oxide_risk_shared
    device_pattern: nmos_core
    parameters:
      tmin: global_tmin
      tdelay: global_tdelay
      vballmsg: global_vballmsg
      stop: global_stop
      tmaxfrac: tmaxfrac3
      vlow1: -1.32
      vhigh1: 1.32
      branch1: "V(g,b)"
      message1: "Vgb_OXrisk"
```

## Layer 3: Spectre Code

### Purpose
Final executable Spectre netlist code with Verilog-A monitor instantiations.

### Example
```spectre
simulator lang=spectre

section base
ahdl_include "./veriloga/ovcheck_mos_alt.va"
parameters
+ global_tmin = 0
+ tmaxfrac3 = -1
endsection base

section soacheck_nmos_core_nmos_core_oxide_risk_shared
model ovcheck6_nmos_core_nmos_core_oxide_risk ovcheck6
+ tmin=global_tmin tmaxfrac=tmaxfrac3
+ vlow1=-1.32 vhigh1=1.32 branch1="V(g,b)" message1="Vgb_OXrisk"
endsection soacheck_nmos_core_nmos_core_oxide_risk_shared
```

## CLI Commands

### Convert: Universal → Monitor
```bash
python soa_dsl_cli.py convert \
  examples/soa_rules_universal.yaml \
  -o output/monitors.yaml
```

### Generate: Monitor → Spectre
```bash
python soa_dsl_cli.py generate \
  output/monitors.yaml \
  -o output/soachecks.scs
```

### Compile: Universal → Spectre (One-Step)
```bash
python soa_dsl_cli.py compile \
  examples/soa_rules_universal.yaml \
  -o output/soachecks.scs
```

### Validate: Check Monitor Spec
```bash
python soa_dsl_cli.py validate \
  examples/soa_monitors.yaml
```

## File Organization

```
SOA_DSL/
├── config/
│   ├── device_library.yaml      # Device definitions
│   └── monitor_library.yaml     # Monitor capabilities
├── examples/
│   ├── soa_rules_universal.yaml # Layer 1 (user input)
│   └── soa_monitors.yaml        # Layer 2 (monitor spec)
├── output/
│   ├── monitors_generated.yaml  # Layer 2 (generated)
│   └── soachecks.scs           # Layer 3 (final output)
├── src/soa_dsl/
│   ├── converter.py            # Universal → Monitor
│   ├── parser.py               # Parse monitor YAML
│   └── generator.py            # Monitor → Spectre
└── soa_dsl_cli.py              # Command-line interface
```

## Benefits of Three-Layer Architecture

### Separation of Concerns
- **Layer 1**: User focuses on physics/electrical constraints
- **Layer 2**: Middleware handles monitor selection and mapping
- **Layer 3**: Generator produces correct Spectre syntax

### Flexibility
- Can support multiple monitor sets (Spectre, HSPICE, custom)
- Can add new monitor types without changing user-facing format
- Can optimize monitor selection independently

### Debuggability
- Layer 2 (monitor spec) can be inspected/modified
- Each layer can be tested independently
- Clear transformation at each step

### Maintainability
- Device library can be updated independently
- Monitor library tracks available monitors
- Conversion logic is centralized

### Extensibility
- New device types: add to device_library.yaml
- New monitor types: add to monitor_library.yaml
- New check patterns: extend converter logic

## Design Principles

### No AST Processing
- Universal spec uses structured data (dicts, lists)
- No expression parsing required
- Patterns are recognized, not parsed

### Declarative Over Imperative
- Users declare what to check, not how
- Middleware decides implementation details
- Templates for common patterns

### Configuration Over Code
- Device and monitor characteristics in YAML
- Easy to update without code changes
- Process-specific configurations possible

### Fail Fast
- Validation at each layer
- Clear error messages
- Type checking with dataclasses
