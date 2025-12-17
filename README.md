# SOA DSL - Three-Layer Architecture

## Overview

SOA DSL provides a three-layer architecture for defining Safe Operating Area (SOA) rules for semiconductor devices. The system separates user-facing specifications from monitor implementations, enabling portability and maintainability.

```
Universal Spec (YAML) → Middleware → Monitor Spec (YAML) → Generator → Spectre (.scs)
     Layer 1                            Layer 2                          Layer 3
```

## Key Features

- **Universal Specification**: Write physics-based rules without monitor knowledge
- **Automatic Monitor Selection**: Middleware selects appropriate Verilog-A monitors
- **Configuration-Driven**: Device and monitor libraries in YAML
- **No AST Processing**: Declarative patterns, simple and fast
- **Backward Compatible**: Existing monitor YAML format still works
- **Extensible**: Easy to add new devices or monitor types

## Quick Start

### Installation

```bash
git clone https://github.com/LennoxSears/SOA_DSL.git
cd SOA_DSL

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install pyyaml
```

### Usage

#### Option 1: One-Step Compile (Recommended)
```bash
# Universal YAML → Spectre .scs (one command)
python soa_dsl_cli.py compile examples/soa_rules_universal.yaml -o output/soachecks.scs
```

#### Option 2: Two-Step Process
```bash
# Step 1: Convert universal spec to monitor spec
python soa_dsl_cli.py convert examples/soa_rules_universal.yaml -o output/monitors.yaml

# Step 2: Generate Spectre code from monitor spec
python soa_dsl_cli.py generate output/monitors.yaml -o output/soachecks.scs
```

#### Validate Monitor Spec
```bash
python soa_dsl_cli.py validate examples/soa_monitors.yaml
```

## Three-Layer Architecture

### Layer 1: Universal Specification (User Input)

**File**: `examples/soa_rules_universal.yaml`

User-friendly format that describes SOA rules in terms of physics and electrical constraints.

**Example:**
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
      time_limit: review
```

**Features:**
- Device-centric (nmos_core, cap_low, etc.)
- Physics-based (voltage, current, temperature, aging)
- No monitor knowledge required
- Portable across different monitor sets

### Middleware: Converter

**Files**: 
- `src/soa_dsl/converter.py` - Conversion logic
- `config/device_library.yaml` - Device definitions
- `config/monitor_library.yaml` - Monitor capabilities

**Responsibilities:**
- Selects appropriate monitor type based on rule characteristics
- Maps universal parameters to monitor-specific parameters
- Generates monitor-specific expressions
- Handles device node name mappings

**Monitor Selection:**
| Rule Type | Monitor Selected |
|-----------|-----------------|
| Single voltage/current | `ovcheck` |
| Multiple signals | `ovcheck6` |
| State-dependent | `ovcheckva_mos2` |
| Temperature-dependent | `ovcheckva_pwl` |
| Aging (HCI/TDDB) | `ovcheckva_ldmos_hci_tddb` |
| Parameter check | `parcheckva3` |

### Layer 2: Monitor Specification (Intermediate)

**File**: `output/monitors_generated.yaml` (or `examples/soa_monitors.yaml`)

Monitor-aware format that directly maps to Verilog-A monitor implementations.

**Example:**
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

**Features:**
- Direct mapping to Verilog-A monitors
- Can be generated or written manually
- Useful for debugging and inspection

### Layer 3: Spectre Code (Final Output)

**File**: `output/soachecks.scs`

Executable Spectre netlist with Verilog-A monitor instantiations.

**Example:**
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

## Supported Patterns

The universal spec supports all common SOA patterns:

1. ✅ **Simple voltage limits** (single branch)
2. ✅ **Multi-branch voltage checks** (up to 6 branches)
3. ✅ **State-dependent limits** (MOS on/off states)
4. ✅ **Temperature-dependent limits** (linear with temperature)
5. ✅ **Self-heating current limits** (width-dependent)
6. ✅ **Aging checks** (HCI/TDDB)
7. ✅ **Parameter checks** (e.g., threshold voltage)
8. ✅ **Multi-level time limits** (steady-state vs transient)

## Supported Monitor Types

All 6 monitor types from `spectre/soachecks_top.scs`:

| Monitor Type | Count | Purpose |
|-------------|-------|---------|
| `ovcheck6` | 105 | Multi-branch voltage check (up to 6) |
| `ovcheck` | 57 | Single branch voltage/current check |
| `ovcheckva_pwl` | 18 | Piecewise linear (temperature-dependent) |
| `ovcheckva_mos2` | 12 | MOS state-dependent check |
| `parcheckva3` | 3 | Parameter checking |
| `ovcheckva_ldmos_hci_tddb` | 1 | HCI/TDDB aging check |

## Project Structure

```
SOA_DSL/
├── config/
│   ├── device_library.yaml      # Device definitions (SMOS10HV)
│   └── monitor_library.yaml     # Monitor capabilities
├── examples/
│   ├── soa_rules_universal.yaml # Layer 1: Universal spec (8 examples)
│   └── soa_monitors.yaml        # Layer 2: Monitor spec (7 examples)
├── output/                      # Generated files
│   └── .gitkeep
├── spectre/
│   ├── soachecks_top.scs       # Reference: Production monitors (196)
│   └── veriloga/               # Verilog-A implementations
├── src/soa_dsl/
│   ├── __init__.py             # Package exports
│   ├── converter.py            # Universal → Monitor converter
│   ├── parser.py               # Monitor YAML parser
│   └── generator.py            # Monitor → Spectre generator
├── web/                        # Web interface (future)
├── soa_dsl_cli.py             # Command-line interface
├── requirements.txt            # Dependencies (PyYAML)
├── ARCHITECTURE.md             # Detailed architecture documentation
├── IMPLEMENTATION_SUMMARY.md   # Implementation summary
└── README.md                   # This file
```

## CLI Commands

### convert
Convert universal spec to monitor spec.

```bash
python soa_dsl_cli.py convert INPUT.yaml -o OUTPUT.yaml [OPTIONS]

Options:
  --device-lib PATH   Device library (default: config/device_library.yaml)
  --monitor-lib PATH  Monitor library (default: config/monitor_library.yaml)
```

### generate
Generate Spectre code from monitor spec.

```bash
python soa_dsl_cli.py generate INPUT.yaml -o OUTPUT.scs
```

### compile
One-step: Universal spec directly to Spectre code.

```bash
python soa_dsl_cli.py compile INPUT.yaml -o OUTPUT.scs [OPTIONS]

Options:
  --device-lib PATH   Device library (default: config/device_library.yaml)
  --monitor-lib PATH  Monitor library (default: config/monitor_library.yaml)
```

### validate
Validate monitor spec.

```bash
python soa_dsl_cli.py validate INPUT.yaml
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
```

## Python API

```python
from pathlib import Path
from soa_dsl.converter import convert_universal_to_monitor
from soa_dsl.parser import parse_file
from soa_dsl.generator import generate_code

# Convert universal to monitor
convert_universal_to_monitor(
    Path('examples/soa_rules_universal.yaml'),
    Path('config/device_library.yaml'),
    Path('config/monitor_library.yaml'),
    Path('output/monitors.yaml')
)

# Generate Spectre code
doc = parse_file(Path('output/monitors.yaml'))
with open('output/soachecks.scs', 'w') as f:
    generate_code(doc, f)
```

## Benefits

- **User-Friendly**: Write physics-based rules, not monitor code
- **Portable**: Universal spec can target different monitor sets
- **Maintainable**: Device/monitor libraries separate from code
- **Extensible**: Easy to add new devices or monitors
- **Debuggable**: Intermediate format can be inspected
- **Flexible**: Can use universal or monitor format
- **Simple**: No AST processing, ~400 lines of converter code

## Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed architecture documentation
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Implementation summary
- **[SPEC_by GJ.yaml](SPEC_by GJ.yaml)** - Original proposal by GJ (reference)

## Examples

See `examples/` directory:
- `soa_rules_universal.yaml` - 8 universal spec examples
- `soa_monitors.yaml` - 7 monitor spec examples

## License

[To be determined]

## Contact

For questions or contributions, please contact the project team.
