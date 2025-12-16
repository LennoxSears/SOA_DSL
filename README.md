# SOA DSL - Monitor-Based Specification

## Overview

SOA DSL provides a YAML-based specification language that directly maps to Verilog-A monitors used in Spectre circuit simulation for Safe Operating Area (SOA) checking. The tool generates Spectre netlist code from YAML specifications, providing a maintainable and type-safe way to define SOA monitors.

## Key Features

- **Direct Monitor Mapping**: YAML specifications map 1:1 to Verilog-A monitor implementations
- **6 Monitor Types**: Support for all monitors used in production
- **Type-Safe**: Validates monitor parameters against actual Verilog-A implementations
- **Production-Ready**: Generates Spectre code matching existing production format

## Supported Monitor Types

Based on `/spectre/soachecks_top.scs` (196 monitors):

| Monitor Type | Count | Purpose |
|-------------|-------|---------|
| `ovcheck6` | 105 | Multi-branch voltage check (up to 6 branches) |
| `ovcheck` | 57 | Single branch voltage check |
| `ovcheckva_pwl` | 18 | Piecewise linear voltage check |
| `ovcheckva_mos2` | 12 | MOS state-dependent check |
| `parcheckva3` | 3 | Parameter checking |
| `ovcheckva_ldmos_hci_tddb` | 1 | HCI/TDDB aging check |

## Installation

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

## Quick Start

### Command Line

```bash
# Validate a YAML specification
python soa_dsl_cli.py examples/soa_monitors.yaml -v

# Generate Spectre code
python soa_dsl_cli.py examples/soa_monitors.yaml -o output/soachecks.scs
```

### Web Interface

Open `web/index.html` in your browser for a graphical interface to create monitor specifications.

## YAML Specification Format

### Basic Structure

```yaml
version: "1.0"
process: "SMOS10HV"
date: "2024-12-16"

global:
  timing:
    tmin: 0
    tdelay: 0
    vballmsg: 1.0
    stop: 0
  tmaxfrac:
    level0: 0      # Never exceed
    level1: 0.01   # 1% of time
    level2: 0.10   # 10% of time
    level3: -1     # Review only

parameters:
  global_tmin: 0
  global_tdelay: 0
  global_vballmsg: 1.0
  global_stop: 0
  tmaxfrac0: 0
  tmaxfrac1: 0.01
  tmaxfrac2: 0.10
  tmaxfrac3: -1

monitors:
  - name: "Monitor Name"
    monitor_type: ovcheck
    model_name: ovcheck_model
    section: soacheck_section
    device_pattern: "device_pattern"
    parameters:
      # Monitor-specific parameters
```

### Monitor Examples

#### Single Branch Voltage Check (`ovcheck`)

```yaml
- name: "Cap Low Oxide Risk"
  monitor_type: ovcheck
  model_name: ovcheck_cap_low_oxrisk
  section: soacheck_cap_low_oxrisk_shared
  device_pattern: "cap_low"
  parameters:
    tmin: global_tmin
    tdelay: global_tdelay
    vballmsg: global_vballmsg
    stop: global_stop
    tmaxfrac: tmaxfrac3
    vlow: -1.32
    vhigh: 1.32
    branch1: "V(t,nw)"
    message1: "Vtnw_OXrisk"
```

#### Multi-Branch Voltage Check (`ovcheck6`)

```yaml
- name: "NMOS Core Oxide Risk"
  monitor_type: ovcheck6
  model_name: ovcheck_mos_core_oxrisk
  section: soacheck_mos_core_oxrisk_shared
  device_pattern: "nmos_core"
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
    vlow2: -1.32
    vhigh2: 1.32
    branch2: "V(g,s)"
    message2: "Vgs_OXrisk"
```

#### MOS State-Dependent Check (`ovcheckva_mos2`)

```yaml
- name: "NMOS Core State Dependent"
  monitor_type: ovcheckva_mos2
  model_name: ovcheck_nmos_core_state
  section: soacheck_nmos_core_state_shared
  device_pattern: "nmos_core"
  parameters:
    tmin: global_tmin
    tdelay: global_tdelay
    vballmsg: global_vballmsg
    stop: global_stop
    tmaxfrac: tmaxfrac0
    vhigh_on: 1.84
    vhigh_off: 3.0
    vhigh_gc: 2.07
    vlow_gc: -2.07
    param: "vth"
    vgt: 0.0
```

#### Piecewise Linear Check (`ovcheckva_pwl`)

```yaml
- name: "Diode Temperature Dependent"
  monitor_type: ovcheckva_pwl
  model_name: ovcheck_dz5_temp
  section: soacheck_dz5_temp
  device_pattern: "dz5"
  parameters:
    tmin: global_tmin
    tdelay: global_tdelay
    vballmsg: global_vballmsg
    stop: global_stop
    tmaxfrac: tmaxfrac0
    vlow: "-ap_fwd_ref - ap_fwd_T * (T - 25)"
    vhigh: "ap_fwd_ref + ap_fwd_T * (T - 25)"
    branch1: "V(p,n)"
    message1: "Vpn_temp"
```

## Generated Spectre Code

```spectre
simulator lang=spectre
// Generated from SOA DSL
// Process: SMOS10HV
// Date: 2024-12-16

section base

ahdl_include "./veriloga/ovcheck_mos_alt.va"
ahdl_include "./veriloga/ovcheck_pwl_alt.va"
ahdl_include "./veriloga/ovcheck_ldmos_hci_tddb_alt.va"
ahdl_include "./veriloga/parcheck3.va"
ahdl_include "./veriloga/selfheating_monitor_nofeedback.va"

parameters
+ global_tmin = 0
+ global_tdelay = 0
+ global_vballmsg = 1.0
+ global_stop = 0

endsection base

section soacheck_cap_low_oxrisk_shared
model ovcheck_cap_low_oxrisk ovcheck
+ tmin=global_tmin tdelay=global_tdelay vballmsg=global_vballmsg stop=global_stop
+ tmaxfrac=tmaxfrac3
+ vlow=-1.32 vhigh=1.32 branch1="V(t,nw)" message1="Vtnw_OXrisk"
endsection soacheck_cap_low_oxrisk_shared
```

## Project Structure

```
SOA_DSL/
├── src/soa_dsl/
│   ├── __init__.py           # Package initialization
│   ├── parser.py             # YAML parser for monitor specs
│   └── generator.py          # Spectre code generator
├── examples/
│   └── soa_monitors.yaml     # Example monitor specifications
├── web/
│   ├── index.html            # Web interface
│   ├── css/style.css         # Styles
│   └── js/app.js             # JavaScript application
├── spectre/
│   ├── soachecks_top.scs     # Reference production file
│   └── veriloga/             # Verilog-A monitor implementations
├── output/                   # Generated Spectre files
├── soa_dsl_cli.py           # Command-line interface
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Python API

```python
from soa_dsl import parse_file, generate_code
from pathlib import Path

# Parse YAML specification
doc = parse_file(Path('examples/soa_monitors.yaml'))

# Generate Spectre code
with open('output/soachecks.scs', 'w') as f:
    generate_code(doc, f)
```

## Benefits

- **Direct Mapping**: No abstraction layer between YAML and Spectre
- **Type Safety**: Validates against actual Verilog-A monitor parameters
- **Production Match**: Generated code matches existing production format
- **Maintainable**: Clear correspondence to underlying implementation
- **Extensible**: Easy to add new monitor types as they're developed

## License

[To be determined]

## Contact

For questions or contributions, please contact the project team.
