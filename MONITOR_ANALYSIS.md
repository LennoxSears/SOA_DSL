# Verilog-A Monitor Analysis

**Based on:** `/spectre/soachecks_top.scs`

---

## Verilog-A Monitor Modules

The file includes 5 Verilog-A monitor modules:

### 1. `ovcheck_mos_alt.va`
**Purpose:** MOS device voltage checking (alternative version)  
**Model name:** `ovcheckva_mos2`  
**Parameters:**
- `tmin`, `tdelay`, `vballmsg`, `stop` - timing and control
- `tmaxfrac` - time fraction limits
- `vlow1`, `vhigh1`, `branch1`, `message1` - first voltage check
- `vlow2`, `vhigh2`, `branch2`, `message2` - second voltage check
- Additional branches up to 6

### 2. `ovcheck_pwl_alt.va`
**Purpose:** Piecewise linear voltage checking  
**Model name:** `ovcheckva_pwl`  
**Parameters:**
- `tmin`, `tdelay`, `vballmsg`, `stop`
- `tmaxfrac`
- `vlow`, `vhigh`, `branch1`, `message1`
- Supports temperature-dependent limits

### 3. `ovcheck_ldmos_hci_tddb_alt.va`
**Purpose:** LDMOS HCI/TDDB aging check  
**Model name:** `ovcheckva_ldmos_hci_tddb`  
**Parameters:**
- `tmin`, `tdelay`, `vballmsg`, `stop`
- `atype` - aging type variant
- HCI/TDDB specific parameters (a, b, c, d, e, f, g, h, i, j, k, l, m, n)

### 4. `parcheck3.va`
**Purpose:** Parameter checking (3-parameter version)  
**Model name:** `parcheckva3`  
**Parameters:**
- `tmin`, `tdelay`, `vballmsg`, `stop`
- `tmaxfrac`
- `param` - parameter to monitor (e.g., "vth")
- `vgt` - gate voltage threshold
- `vlow`, `vhigh` - limits

### 5. `selfheating_monitor_nofeedback.va`
**Purpose:** Self-heating monitoring without feedback  
**Model name:** `ovcheck` (with self-heating parameters)  
**Parameters:**
- `tmin`, `tdelay`, `vballmsg`, `stop`
- `dtmax` - maximum temperature rise
- `theat` - thermal time constant
- `monitor` - what to monitor
- Current limits: `idc`, `ipeak`, `irms`

---

## Monitor Types Used in soachecks_top.scs

Based on the model definitions, the monitors are used for:

### Voltage Monitors (ovcheck, ovcheck6)
- **ovcheck** - Single voltage branch check
- **ovcheck6** - Up to 6 voltage branches check

**Common parameters:**
```
+ tmin=global_tmin 
+ tdelay=global_tdelay 
+ vballmsg=global_vballmsg 
+ stop=global_stop
+ tmaxfrac=<level>
+ vlow=<value>  vhigh=<value>  branch1="V(pin1,pin2)"  message1="<msg>"
```

### MOS-specific Monitors (ovcheckva_mos2)
**Parameters:**
```
+ tmin, tdelay, vballmsg, stop
+ tmaxfrac
+ vhigh_on, vhigh_off  // state-dependent limits
+ vhigh_gc, vlow_gc    // gate control limits
+ param, vgt           // monitor parameters
```

### PWL Monitors (ovcheckva_pwl)
**Parameters:**
```
+ tmin, tdelay, vballmsg, stop
+ tmaxfrac
+ vlow, vhigh, branch1, message1
+ Temperature-dependent expressions
```

### HCI/TDDB Monitors (ovcheckva_ldmos_hci_tddb)
**Parameters:**
```
+ tmin, tdelay, vballmsg, stop
+ atype
+ soa_hcitddb_a through soa_hcitddb_n (14 parameters)
```

### Parameter Monitors (parcheckva3)
**Parameters:**
```
+ tmin, tdelay, vballmsg, stop
+ tmaxfrac
+ param="<parameter_name>"
+ vgt=<value>
+ vlow, vhigh
```

### Self-Heating Monitors (ovcheck with heating)
**Parameters:**
```
+ tmin, tdelay, vballmsg, stop
+ dtmax=<temp_rise>
+ theat=<time_constant>
+ monitor=<what_to_monitor>
+ idc_high, ipeak_high, irms_high
```

---

## Key Observations

### 1. All monitors share common control parameters:
- `tmin` - minimum time outside SOA before warning
- `tdelay` - delay after transient start
- `vballmsg` - message verbosity (1=all, 0=summary)
- `stop` - stop simulation on violation

### 2. Time fraction levels (tmaxfrac):
- `tmaxfrac0 = 0` - never exceed
- `tmaxfrac1 = 0.01` - 1% of time
- `tmaxfrac2 = 0.10` - 10% of time
- `tmaxfrac3 = -1` - review only

### 3. Monitor instantiation pattern:
```spectre
model <model_name> <monitor_type>
+ <common_parameters>
+ <specific_parameters>
```

### 4. Actual usage in circuit:
The monitors are instantiated as models, then referenced in subcircuits.

---

## Proposed YAML Structure

Based on the actual monitors, the YAML should describe:

1. **Which monitor to use** (ovcheck, ovcheck6, ovcheckva_mos2, etc.)
2. **Monitor parameters** (specific to each monitor type)
3. **Device mapping** (which devices use which monitors)

### Example:
```yaml
monitors:
  - name: "NMOS Core VDS Check"
    monitor_type: ovcheck
    device: nmos_core
    parameters:
      tmin: global_tmin
      tdelay: global_tdelay
      vballmsg: global_vballmsg
      stop: global_stop
      tmaxfrac: tmaxfrac0
      vlow: -1.65
      vhigh: 1.65
      branch1: "V(d,s)"
      message1: "Vds"
```

---

## Next Steps

1. Redesign YAML spec to match monitor structure
2. Each rule should specify:
   - Monitor type (ovcheck, ovcheck6, ovcheckva_mos2, etc.)
   - Monitor parameters
   - Device/subcircuit to apply to
3. Code generator should create model definitions
4. Parser should validate against monitor types

---

**Conclusion:** The current YAML spec is too abstract. It should directly map to the Verilog-A monitors and their parameters as used in `soachecks_top.scs`.
