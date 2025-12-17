# SOA DSL Architecture

## Overview

SOA DSL separates device-specific details from monitor-specific details, allowing users to create universal SOA rules without needing to know about Verilog-A monitor implementations.

## Three Key Components

### 1. Device Library (`config/device_library.yaml`)

**Purpose:** Model-specific details

Defines:
- **Subcircuits**: Actual model names (e.g., `nch_mac`, `pch_lvt_mac`, `cap_low_model`)
- **Node names**: Terminal names for each device (e.g., `[g, d, s, b]` for MOSFET)
- **Parameters**: Available instance parameters (e.g., `[w, l, m, vth]`)
- **Hierarchy level**: Where SOA checks are inserted (transistor, device, etc.)

Grouping:
- **Level 1 Groups**: Direct grouping of subcircuits (e.g., `nmos_core_variants: [nch_mac, nch_lvt_mac, nch_hvt_mac]`)
- **Level 2 Groups**: Groups of level 1 groups (e.g., `all_nmos: [nmos_core_variants, nmos_5v_variants]`)

**Example:**
```yaml
subcircuits:
  nch_mac:
    type: nmos
    nodes: [g, d, s, b]
    parameters: [w, l, m, vth]
    hierarchy_level: transistor

level1_groups:
  nmos_core_variants:
    subcircuits: [nch_mac, nch_lvt_mac, nch_hvt_mac]

level2_groups:
  all_nmos:
    level1_groups: [nmos_core_variants, nmos_5v_variants]
```

### 2. Monitor Library (`config/monitor_library.yaml`)

**Purpose:** Monitor-specific details

Defines:
- **Monitor types**: Available Verilog-A monitors (e.g., `ovcheck`, `ovcheck6`, `ovcheckva_mos2`)
- **Capabilities**: What each monitor can check (voltage, current, state-dependent, etc.)
- **Parameters**: Required and optional parameters for each monitor
- **Descriptions**: User-friendly descriptions

**Example:**
```yaml
monitors:
  ovcheck:
    description: "Single branch voltage or current check"
    capabilities:
      - voltage_check
      - current_check
      - single_branch
    required_parameters:
      - tmin
      - tdelay
      - vballmsg
      - stop
```

### 3. Web Interface (`web/index.html`)

**Purpose:** Generate universal SOA YAML

Workflow:
1. **Load libraries** on page load
2. **User selects check type** (from monitor library)
3. **User selects devices** (from device library - direct subcircuits or groups)
4. **User configures check** (form adapts based on monitor type)
5. **User sets limits** (min/max values, time limits)
6. **Generate universal YAML** (ready to use with CLI)

**Output:** `examples/soa_rules_universal.yaml` format

## Data Flow

```
┌─────────────────────────────────────────────────────────┐
│  Device Library                Monitor Library          │
│  (model details)               (monitor details)        │
└────────────┬──────────────────────────┬─────────────────┘
             │                          │
             └──────────┬───────────────┘
                        ↓
             ┌──────────────────────┐
             │   Web Interface      │
             │   (combines both)    │
             └──────────┬───────────┘
                        ↓
             ┌──────────────────────┐
             │  Universal SOA YAML  │
             │  (user-friendly)     │
             └──────────┬───────────┘
                        ↓
             ┌──────────────────────┐
             │   CLI Converter      │
             │   (middleware)       │
             └──────────┬───────────┘
                        ↓
             ┌──────────────────────┐
             │  Monitor YAML        │
             │  (monitor-aware)     │
             └──────────┬───────────┘
                        ↓
             ┌──────────────────────┐
             │  Spectre Generator   │
             └──────────┬───────────┘
                        ↓
             ┌──────────────────────┐
             │  Spectre .scs file   │
             │  (final output)      │
             └──────────────────────┘
```

## Key Design Principles

### Separation of Concerns
- **Device library**: Knows about models, nodes, parameters
- **Monitor library**: Knows about Verilog-A monitors, capabilities
- **Universal YAML**: Knows about physics (voltage, current, limits)
- **User**: Doesn't need to know about monitors or model details

### User Experience
Users write:
```yaml
rules:
  - name: "NMOS Core Oxide Risk"
    applies_to:
      subcircuits: [nch_mac, nch_lvt_mac, nch_hvt_mac]
    check:
      type: voltage
      measure: V(g,s)
    limits:
      steady:
        max: 1.32
```

Not:
```yaml
monitors:
  - monitor_type: ovcheck6
    model_name: ovcheck_mos_core_oxrisk
    section: soacheck_nmos_core_oxrisk_shared
    parameters:
      vhigh1: 1.32
      branch1: "V(g,s)"
```

### Flexibility
- Add new devices → update device library only
- Add new monitors → update monitor library only
- Change monitor selection logic → update converter only
- User specifications remain unchanged

## Benefits

1. **Simple for users**: Write physics-based rules, not monitor code
2. **Maintainable**: Model and monitor details in separate files
3. **Extensible**: Easy to add new devices or monitors
4. **Portable**: Universal YAML can target different monitor sets
5. **Web-friendly**: Libraries are YAML, easy to load in browser

## Files

```
SOA_DSL/
├── config/
│   ├── device_library.yaml      # Model-specific details
│   └── monitor_library.yaml     # Monitor-specific details
├── examples/
│   ├── soa_rules_universal.yaml # User-facing format
│   └── soa_monitors.yaml        # Monitor-aware format
├── web/
│   ├── index.html               # Web interface
│   ├── js/app.js                # Loads libraries, generates YAML
│   └── css/style.css            # Styling
├── src/soa_dsl/
│   ├── converter.py             # Universal → Monitor
│   ├── parser.py                # Parse monitor YAML
│   └── generator.py             # Monitor → Spectre
└── soa_dsl_cli.py               # CLI tool
```

## Usage

### Web Interface
1. Open `web/index.html` in browser
2. Select check type (from monitor library)
3. Select devices (from device library)
4. Configure check and limits
5. Download universal YAML

### Command Line
```bash
# Generate Spectre from universal YAML
python soa_dsl_cli.py compile examples/soa_rules_universal.yaml -o output/soachecks.scs
```

That's it! Simple separation of concerns makes the system flexible and maintainable.
