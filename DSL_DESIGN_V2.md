# SOA DSL Design v2.0 - Monitor-Based Specification

**Version:** 2.0  
**Date:** December 16, 2024  
**Based on:** Actual Verilog-A monitors in `/spectre/soachecks_top.scs`

---

## Overview

Version 2.0 redesigns the SOA DSL to directly map to Verilog-A monitor modules. Instead of abstract "rule types," the YAML now specifies actual monitor types and their parameters.

### Key Changes from v1.0

| Aspect | v1.0 (Old) | v2.0 (New) |
|--------|------------|------------|
| **Concept** | Abstract "rules" | Concrete "monitors" |
| **Types** | vhigh, vlow, ihigh, ilow | ovcheck, ovcheck6, ovcheckva_mos2, etc. |
| **Parameters** | Generic constraints | Monitor-specific parameters |
| **Output** | Abstract code | Actual Spectre model definitions |
| **Mapping** | Indirect | Direct 1:1 mapping |

---

## YAML Structure

### Top Level

```yaml
version: "2.0"
process: "<process_name>"
date: "<YYYY-MM-DD>"

global:
  timing: {...}
  tmaxfrac: {...}

monitors:
  - name: "<monitor_name>"
    monitor_type: "<type>"
    ...
```

### Global Section

```yaml
global:
  timing:
    tmin: 0           # Minimum time outside SOA before warning
    tdelay: 0         # Delay after transient start
    vballmsg: 1.0     # Message verbosity (1=all, 0=summary)
    stop: 0           # Stop simulation on violation (1=yes, 0=no)
  
  tmaxfrac:
    level0: 0         # Never exceed
    level1: 0.01      # 1% of time
    level2: 0.10      # 10% of time
    level3: -1        # Review only
```

---

## Monitor Types

### 1. ovcheck (Single Branch)

**Purpose:** Single voltage branch checking  
**Verilog-A:** `ovcheck_mos_alt.va` or `ovcheck_pwl_alt.va`

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

**Generated Spectre:**
```spectre
section soacheck_cap_low_oxrisk_shared
model ovcheck_cap_low_oxrisk ovcheck
+ tmin=global_tmin tdelay=global_tdelay vballmsg=global_vballmsg stop=global_stop
+ tmaxfrac=tmaxfrac3
+ vlow=-1.32 vhigh=1.32 branch1="V(t,nw)" message1="Vtnw_OXrisk"
endsection soacheck_cap_low_oxrisk_shared
```

### 2. ovcheck6 (Multi-Branch)

**Purpose:** Up to 6 voltage branch checking  
**Verilog-A:** `ovcheck_mos_alt.va`

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
    branches:
      - vlow: -1.32
        vhigh: 1.32
        branch: "V(g,b)"
        message: "Vgb_OXrisk"
      - vlow: -1.32
        vhigh: 1.32
        branch: "V(g,s)"
        message: "Vgs_OXrisk"
```

**Generated Spectre:**
```spectre
section soacheck_mos_core_oxrisk_shared
model ovcheck_mos_core_oxrisk ovcheck6
+ tmin=global_tmin tdelay=global_tdelay vballmsg=global_vballmsg stop=global_stop
+ tmaxfrac=tmaxfrac3
+ vlow1=-1.32 vhigh1=1.32 branch1="V(g,b)" message1="Vgb_OXrisk"
+ vlow2=-1.32 vhigh2=1.32 branch2="V(g,s)" message2="Vgs_OXrisk"
endsection soacheck_mos_core_oxrisk_shared
```

### 3. ovcheckva_mos2 (MOS-Specific)

**Purpose:** MOS device with state-dependent limits  
**Verilog-A:** `ovcheck_mos_alt.va`

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
    vhigh_off: 3.00
    gate_control:
      vhigh_gc: 2.07
      vlow_gc: -2.07
    monitor_params:
      param: "vth"
      vgt: 0.0
```

### 4. ovcheckva_pwl (Piecewise Linear)

**Purpose:** Temperature-dependent voltage checking  
**Verilog-A:** `ovcheck_pwl_alt.va`

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

### 5. ovcheckva_ldmos_hci_tddb (Aging Check)

**Purpose:** HCI/TDDB aging monitoring  
**Verilog-A:** `ovcheck_ldmos_hci_tddb_alt.va`

```yaml
- name: "PMOS 90V HCI/TDDB"
  monitor_type: ovcheckva_ldmos_hci_tddb
  model_name: hcitddb_pmos90_10hv
  section: soacheck_pmos90_hci_tddb
  device_pattern: "pmos90_10hv"
  parameters:
    tmin: global_tmin
    tdelay: global_tdelay
    vballmsg: global_vballmsg
    stop: global_stop
    atype: atype
    hci_tddb_params:
      soa_hcitddb_a: 24
      soa_hcitddb_b: 0.38
      # ... up to soa_hcitddb_n
```

### 6. parcheckva3 (Parameter Check)

**Purpose:** Device parameter monitoring  
**Verilog-A:** `parcheck3.va`

```yaml
- name: "NMOS Core VTH Check"
  monitor_type: parcheckva3
  model_name: parcheck_nmos_core_vth
  section: soacheck_nmos_core_vth
  device_pattern: "nmos_core"
  parameters:
    tmin: global_tmin
    tdelay: global_tdelay
    vballmsg: global_vballmsg
    stop: global_stop
    tmaxfrac: tmaxfrac0
    param: "vth"
    vgt: 0.0
    vlow: 0.3
    vhigh: 0.7
```

### 7. Self-Heating Monitors

**Purpose:** Current monitoring with thermal effects  
**Verilog-A:** `selfheating_monitor_nofeedback.va`

```yaml
- name: "Metal-1 Resistor Self-Heating"
  monitor_type: ovcheck
  model_name: ish_rm1
  section: soacheck_rm1_heating
  device_pattern: "rm1_10hv"
  self_heating:
    dtmax: dtmax_rm
    theat: theat
    monitor: temperature
  parameters:
    tmin: global_tmin
    tdelay: global_tdelay
    vballmsg: global_vballmsg
    stop: global_stop
    constraints:
      - name: "DC Current"
        type: idc
        model: idc_rm1
        ihigh: "$w * 4.05e-3"
      - name: "Peak Current"
        type: ipeak
        model: ipeak_rm1
        ihigh: "$w * 4.05e-1"
      - name: "RMS Current"
        type: irms
        model: irms_rm1
        ihigh: "1.0e-3 * sqrt(367.8 * $w * ($w + 0.53))"
```

---

## Common Fields

All monitors share these fields:

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Human-readable monitor name |
| `monitor_type` | Yes | Verilog-A monitor type |
| `model_name` | Yes | Spectre model name |
| `section` | Yes | Spectre section name |
| `device_pattern` | Yes | Device name pattern to match |
| `parameters` | Yes | Monitor-specific parameters |

---

## Parameter References

### Global References
- `global_tmin` → `global.timing.tmin`
- `global_tdelay` → `global.timing.tdelay`
- `global_vballmsg` → `global.timing.vballmsg`
- `global_stop` → `global.timing.stop`
- `tmaxfrac0` → `global.tmaxfrac.level0`
- `tmaxfrac1` → `global.tmaxfrac.level1`
- `tmaxfrac2` → `global.tmaxfrac.level2`
- `tmaxfrac3` → `global.tmaxfrac.level3`

### Device Parameters
- `$w` - Device width
- `$l` - Device length
- `$np` - Number of parallel devices
- `T` - Temperature

---

## Code Generation

### Output Format

```spectre
simulator lang=spectre

section base
ahdl_include "./veriloga/ovcheck_mos_alt.va"
ahdl_include "./veriloga/ovcheck_pwl_alt.va"
ahdl_include "./veriloga/ovcheck_ldmos_hci_tddb_alt.va"
ahdl_include "./veriloga/parcheck3.va"
ahdl_include "./veriloga/selfheating_monitor_nofeedback.va"
endsection base

section <section_name>
model <model_name> <monitor_type>
+ <parameters>
endsection <section_name>
```

---

## Migration from v1.0

### Mapping Table

| v1.0 Type | v2.0 Monitor Type | Notes |
|-----------|-------------------|-------|
| `vhigh` | `ovcheck` | Single branch with vhigh only |
| `vlow` | `ovcheck` | Single branch with vlow only |
| `range` | `ovcheck` | Single branch with vlow + vhigh |
| `multi_branch` | `ovcheck6` | Multiple branches |
| `state_dependent` | `ovcheckva_mos2` | MOS-specific |
| `current_with_heating` | `ovcheck` + `self_heating` | Self-heating |

---

## Benefits of v2.0

1. **Direct Mapping:** YAML directly maps to Spectre code
2. **Clarity:** Users see actual monitor types
3. **Flexibility:** Can use any monitor parameter
4. **Accuracy:** Generated code matches actual usage
5. **Maintainability:** Easy to add new monitors
6. **Validation:** Can validate against monitor schemas

---

## See Also

- `MONITOR_ANALYSIS.md` - Detailed monitor analysis
- `examples/monitors_new.yaml` - Complete examples
- `/spectre/soachecks_top.scs` - Reference implementation
