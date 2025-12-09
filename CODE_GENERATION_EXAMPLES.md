# Code Generation Examples: DSL → Spectre

This document shows concrete examples of how DSL rules are translated into Spectre netlist code with Verilog-A monitor instantiations.

## Example 1: Simple Voltage Constraint

### Input DSL (YAML)
```yaml
name: "NMOS Core VDS Simple Limit"
device: nmos_core
parameter: "v[d,s]"
type: vhigh
severity: high
constraint:
  vhigh: 1.65
description: "Drain-source voltage must not exceed 1.65V"
```

### Generated Spectre Code
```spectre
section nmos_core_soa
// Rule: NMOS Core VDS Simple Limit
// Description: Drain-source voltage must not exceed 1.65V
model ovcheck_0 ovcheck
+ tmin=global_tmin tdelay=global_tdelay vballmsg=global_vballmsg stop=global_stop
+ tmaxfrac=tmaxfrac0
+ vlow=-999.0 vhigh=1.65 branch1="V(d,s)"
+ message1="NMOS Core VDS Simple Limit"
soacheck0 (d s) ovcheck_0
endsection nmos_core_soa
```

---

## Example 2: Temperature-Dependent Constraint

### Input DSL (YAML)
```yaml
name: "Diode Temperature Dependent Voltage"
device: dz5
parameter: "v[p,n]"
type: vhigh
severity: review
constraint:
  vhigh: "0.9943 - 0.0006*(T - 25)"
description: "Forward voltage limit decreases with temperature"
```

### Generated Spectre Code
```spectre
section dz5_soa
// Rule: Diode Temperature Dependent Voltage
// Description: Forward voltage limit decreases with temperature
parameters
+ vhigh_calc = 0.9943 - 0.0006*(temp - 25)
model ovcheck_0 ovcheck
+ tmin=global_tmin tdelay=global_tdelay vballmsg=global_vballmsg stop=global_stop
+ tmaxfrac=tmaxfrac3
+ vlow=-999.0 vhigh=vhigh_calc branch1="V(p,n)"
+ message1="Diode Temperature Dependent Voltage"
soacheck0 (p n) ovcheck_0
endsection dz5_soa
```

---

## Example 3: Multi-Level (tmaxfrac) Constraint

### Input DSL (YAML)
```yaml
name: "NMOS Core Multi-Level VDS"
device: nmos_core
parameter: "v[d,s]"
type: vhigh
severity: low
constraint:
  vhigh: 1.65
tmaxfrac:
  0.0: 1.65    # Never exceed
  0.01: 1.84   # 1% time allowed
  0.1: 1.71    # 10% time allowed
```

### Generated Spectre Code
```spectre
section nmos_core_soa
// Rule: NMOS Core Multi-Level VDS
// Multi-level checking with time-dependent relaxation

// Level 0: Never exceed 1.65V (tmaxfrac=0.0)
model ovcheck_0 ovcheck
+ tmin=global_tmin tdelay=global_tdelay vballmsg=global_vballmsg stop=global_stop
+ tmaxfrac=tmaxfrac0
+ vlow=-999.0 vhigh=1.65 branch1="V(d,s)"
+ message1="NMOS Core Multi-Level VDS (0%)"

// Level 1: Can exceed to 1.84V for 1% of time (tmaxfrac=0.01)
model ovcheck_1 ovcheck
+ tmin=global_tmin tdelay=global_tdelay vballmsg=global_vballmsg stop=global_stop
+ tmaxfrac=tmaxfrac1
+ vlow=-999.0 vhigh=1.84 branch1="V(d,s)"
+ message1="NMOS Core Multi-Level VDS (1%)"

// Level 2: Can exceed to 1.71V for 10% of time (tmaxfrac=0.1)
model ovcheck_2 ovcheck
+ tmin=global_tmin tdelay=global_tdelay vballmsg=global_vballmsg stop=global_stop
+ tmaxfrac=tmaxfrac2
+ vlow=-999.0 vhigh=1.71 branch1="V(d,s)"
+ message1="NMOS Core Multi-Level VDS (10%)"

soacheck0 (d s) ovcheck_0
soacheck1 (d s) ovcheck_1
soacheck2 (d s) ovcheck_2
endsection nmos_core_soa
```

---

## Example 4: MOS State-Dependent Constraint

### Input DSL (YAML)
```yaml
name: "NMOS Core State Dependent"
device: nmos_core
parameter: "v[d,s]"
type: state_dependent
severity: high
constraint:
  vhigh_on: 1.84      # When device is ON
  vhigh_off: 3.00     # When device is OFF
gate_control:
  vhigh_gc: 2.07
  vlow_gc: -2.07
junction:
  vfwd_jun_on: "ap_no_check"
  vrev_jun_on: -3.30
  vfwd_jun_off: "ap_no_check"
  vrev_jun_off: -3.30
monitor_params:
  param: "vth"
  vgt: 0.0
messages:
  vds: "AMR"
  vgs: "AMR"
  vgd: "AMR"
```

### Generated Spectre Code
```spectre
section nmos_core_soa
// Rule: NMOS Core State Dependent
// Drain-source voltage depends on device on/off state
model ovcheck_0 ovcheckva_mos2
+ tmin=global_tmin tdelay=global_tdelay vballmsg=global_vballmsg stop=global_stop
+ tmaxfrac=tmaxfrac0
+ vhigh_ds_on=1.84 vhigh_ds_off=3.00
+ vhigh_gc=2.07 vlow_gc=-2.07
+ vhigh_gb_on=ap_no_check vlow_gb_on=-ap_no_check
+ vfwd_jun_on=ap_no_check vrev_jun_on=-3.30
+ vfwd_jun_off=ap_no_check vrev_jun_off=-3.30
+ message_vds="AMR"
+ message_vgs="AMR"
+ message_vgd="AMR"
+ param="vth"
+ vgt=0.0
+ device=device
soacheck0 (d g s b) ovcheck_0
endsection nmos_core_soa
```

---

## Example 5: Multi-Branch Rule

### Input DSL (YAML)
```yaml
name: "NMOS 90V Multi-Branch"
device: nmos90_10hv
parameter: multi
type: multi_branch
severity: high
branches:
  - branch: "V(g,b)"
    vhigh: "ap_gc_hv"
    vlow: "-ap_gc_hv"
  - branch: "V(g,s)"
    vhigh: "ap_gc_hv"
    vlow: "-ap_gc_hv"
  - branch: "V(d,s)"
    vhigh: 90
    vlow: "-ap_gc_hv"
connections: "(g b g s d s)"
condition: "enable_soa == 1"
```

### Generated Spectre Code
```spectre
section nmos90_10hv_soa
// Rule: NMOS 90V Multi-Branch
// All voltage limits for 90V NMOS
parameters
+ soa_hv_vmax = 90
if (enable_soa == 1) {
model ovcheck_1 ovcheck6
+ tmin=global_tmin tdelay=global_tdelay vballmsg=global_vballmsg stop=global_stop
+ tmaxfrac=tmaxfrac0
+ vlow1=-ap_gc_hv         vhigh1=ap_gc_hv           branch1="V(g,b)"
+ vlow2=-ap_gc_hv         vhigh2=ap_gc_hv           branch2="V(g,s)"
+ vlow3=-ap_gc_hv         vhigh3=90                 branch3="V(d,s)"
soacheck1 (g b g s d s) ovcheck_1
}
endsection nmos90_10hv_soa
```

---

## Example 6: Resistor with Self-Heating

### Input DSL (YAML)
```yaml
name: "Metal-1 Resistor with Self-Heating"
device: rm1_10hv
parameter: "i[rm1_10hv]"
type: current_with_heating
severity: high
constraints:
  - name: "DC Current"
    type: idc
    ihigh: "$w * 4.05e-3"
    message: "Max. dc-current exceeded"
  - name: "Peak Current"
    type: ipeak
    ihigh: "$w * 4.05e-1"
    message: "Max. peak current exceeded"
  - name: "RMS Current"
    type: irms
    ihigh: "1.0e-3 * sqrt(367.8 * $w * ($w + 0.53))"
    message: "Self heating exceeds 5 degC"
self_heating:
  dtmax: "dtmax_rm"
  theat: "theat"
  monitor: "shmonitor_nofeedback"
device_params:
  weff1_soa: "$w - 0.04"
  rsh_soa: "nom_rs_m1*delr_rs_m1"
  leff_soa: "$l + dl_m1"
  jdc_rm: 4.05e-3
  jdc_rms: 367.8
  dw_rms: 0.53
  jpeak_rm: 4.05e-1
condition: "enable_soa == 1"
```

### Generated Spectre Code
```spectre
section rm1_10hv_soa
// Rule: Metal-1 Resistor with Self-Heating
// Metal-1 resistor with DC, peak, and RMS current limits
parameters
+ weff1_soa = w - 0.04
+ rsh_soa = nom_rs_m1*delr_rs_m1
+ leff_soa = l + dl_m1
+ jdc_rm = 4.05e-3
+ jdc_rms = 367.8
+ dw_rms = 0.53
+ jpeak_rm = 4.05e-1
parameters
+ weff_soa = w + dw_um
+ reff_soa = rsh_soa * leff_soa / weff_soa
parameters // Idc, IPeak, Irms
+ vmax_rm_dc = jdc_rm * weff1_soa * reff_soa
+ vmax_rm_peak = jpeak_rm * weff1_soa * reff_soa
+ irms_max = 1.0e-3 * sqrt(jdc_rms * weff1_soa * (weff1_soa + dw_rms))

if (enable_soa == 1) {
model irms_rm ovcheck
+ tmin=global_tmin tdelay=global_tdelay vballmsg=global_vballmsg stop=global_stop
+ tmaxfrac=tmaxfrac0
+ vlow=-1.0  vhigh=dtmax_rm branch1="V(dt)" message1="Self heating exceeds 5 degC"

model idc_rm ovcheck
+ tmin=global_tmin tdelay=global_tdelay vballmsg=global_vballmsg stop=global_stop
+ tmaxfrac=tmaxfrac0
+ vlow=-vmax_rm_dc vhigh=vmax_rm_dc branch1="V(d,s)"
+ message1="Max. dc-current exceeded"

model ipeak_rm ovcheck
+ tmin=global_tmin tdelay=global_tdelay vballmsg=global_vballmsg stop=global_stop
+ tmaxfrac=tmaxfrac0
+ vlow=-vmax_rm_peak vhigh=vmax_rm_peak branch1="V(d,s)"
+ message1="Max. peak current exceeded"

sh_dummy (d s dt) shmonitor_nofeedback
+ r=reff_soa
+ irms_max=irms_max
+ dtmax=dtmax_rm
+ theat=theat

soacheck_rms (dt 0) irms_rm
soacheck_dc (d s) idc_rm
soacheck_peak (d s) ipeak_rm
}
endsection rm1_10hv_soa
```

---

## Example 7: Oxide Risk Assessment

### Input DSL (YAML)
```yaml
name: "NMOS Core Oxide Risk"
device: nmos_core
parameter: "v[g,b]"
type: vhigh
severity: review
branches:
  - branch: "V(g,b)"
    vhigh: "ap_gc_lv_oxrisk"
    vlow: "-ap_gc_lv_oxrisk"
    message: "Vgb_OXrisk"
  - branch: "V(g,s)"
    vhigh: "ap_gc_lv_oxrisk"
    vlow: "-ap_gc_lv_oxrisk"
    message: "Vgs_OXrisk"
  - branch: "V(g,d)"
    vhigh: "ap_gc_lv_oxrisk"
    vlow: "-ap_gc_lv_oxrisk"
    message: "Vgd_OXrisk"
condition: "enable_risk_assessment == 1"
```

### Generated Spectre Code
```spectre
section nmos_core_oxrisk_soa
// Rule: NMOS Core Oxide Risk
// Gate oxide risk assessment for core NMOS
if (enable_risk_assessment == 1) {
model ovcheck_5 ovcheck6
+ tmin=global_tmin tdelay=global_tdelay vballmsg=global_vballmsg stop=global_stop
+ tmaxfrac=tmaxfrac3
+ vlow1=-ap_gc_lv_oxrisk  vhigh1=ap_gc_lv_oxrisk  branch1="V(g,b)"  message1="Vgb_OXrisk"
+ vlow2=-ap_gc_lv_oxrisk  vhigh2=ap_gc_lv_oxrisk  branch2="V(g,s)"  message2="Vgs_OXrisk"
+ vlow3=-ap_gc_lv_oxrisk  vhigh3=ap_gc_lv_oxrisk  branch3="V(g,d)"  message3="Vgd_OXrisk"
soacheck5 (g b g s g d 0 0 0 0 0 0) ovcheck_5
}
endsection nmos_core_oxrisk_soa
```

---

## Example 8: Conditional Constraint

### Input DSL (YAML)
```yaml
name: "BJT Conditional Voltage Limit"
device: npn_b
parameter: "v[c,e]"
type: vhigh
severity: high
constraint:
  vhigh: "if T > 85 then 10.0 else 12.0"
description: "Collector-emitter voltage reduced at high temperature"
```

### Generated Spectre Code
```spectre
section npn_b_soa
// Rule: BJT Conditional Voltage Limit
// Description: Collector-emitter voltage reduced at high temperature
parameters
+ vhigh_calc = (temp > 85) ? 10.0 : 12.0
model ovcheck_0 ovcheck
+ tmin=global_tmin tdelay=global_tdelay vballmsg=global_vballmsg stop=global_stop
+ tmaxfrac=tmaxfrac0
+ vlow=-999.0 vhigh=vhigh_calc branch1="V(c,e)"
+ message1="BJT Conditional Voltage Limit"
soacheck0 (c e) ovcheck_0
endsection npn_b_soa
```

---

## Monitor Type Selection Logic

The code generator automatically selects the appropriate Verilog-A monitor based on the rule type:

| Rule Type | Monitor | Use Case |
|-----------|---------|----------|
| `vhigh`, `vlow`, `range` | `ovcheck` | Simple voltage checking (1 branch) |
| `multi_branch` | `ovcheck6` | Multiple voltage branches (up to 6) |
| `state_dependent` | `ovcheckva_mos2` | MOS with on/off state detection |
| `current_with_heating` | `ovcheck` + `shmonitor_nofeedback` | Current with self-heating |
| `parameter` | `parcheck3` | Device parameter monitoring |
| `pwl` | `ovcheck_pwl` | Piecewise-linear boundaries |
| `aging` | `ovcheck_ldmos_hci_tddb` | HCI/TDDB aging checks |

---

## Global Section Generation

### Input DSL (YAML)
```yaml
global:
  timing:
    tmin: 0
    tdelay: 0
    vballmsg: 1.0
    stop: 0
  temperature:
    tcelsius0: 273.15
    tref_soa: 25
  tmaxfrac:
    level0: 0
    level1: 0.01
    level2: 0.10
    level3: -1
  limits:
    ap_gc_lv: 1.65
    ap_gc_hv: 5.5
```

### Generated Spectre Code
```spectre
simulator lang=spectre

section base

parameters
// global SOA parameters
+ global_tmin      = 0
+ global_tdelay    = 0
+ global_vballmsg  = 1.0
+ global_stop      = 0
+ tcelsius0        = 273.15

// duration limits
+ tmaxfrac0 = 0
+ tmaxfrac1 = 0.01
+ tmaxfrac2 = 0.10
+ tmaxfrac3 = -1

// temperature reference
+ tref_soa        = 25

// oxide voltage limits
+ ap_gc_lv        = 1.65
+ ap_gc_hv        = 5.5

endsection base
```

---

## Summary

The code generator:
1. **Parses DSL** → Builds AST
2. **Validates rules** → Checks syntax and semantics
3. **Selects monitors** → Maps rule types to Verilog-A monitors
4. **Generates parameters** → Evaluates expressions and creates parameter sections
5. **Creates instantiations** → Generates monitor instances with proper connections
6. **Adds comments** → Includes DSL source reference for traceability
7. **Formats output** → Proper Spectre syntax with consistent indentation

All generated code is production-ready and directly usable in Spectre simulations.
