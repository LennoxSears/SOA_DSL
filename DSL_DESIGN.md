# SOA DSL Design Specification

## Overview
Domain-Specific Language for describing Safe Operating Area (SOA) rules for semiconductor devices. The DSL compiles to Spectre netlist format with Verilog-A monitor instantiations.

Based on the proposal by Zhendong Ge, this DSL aims to:
- **Reduce manual effort by 95%**
- **Eliminate error-prone manual workflows**
- **Provide unified, human-readable rule specification**
- **Enable automated test generation and validation**
- **Vendor & simulator agnostic design**

## Design Goals
1. **Simple & Learnable**: Can be learned in 30 minutes
2. **Unified Grammar**: One syntax for all electrical/thermal SOA limits
3. **Human-readable & Machine-parsable**: Clear syntax for both humans and tools
4. **Comprehensive**: Support all rule types (voltage, current, temperature, conditional, multi-level)
5. **Automated Toolchain**: From DSL to implementation, tests, and documentation
6. **Generate production-ready soachecks_top.scs**

## Core DSL Grammar

### Language Primitives

**Variables:**
- `v[pin1,pin2]` or `v[pin]` - Voltage between pins or pin to ground
- `i[pin]` or `i[device]` - Current through pin or device
- `T` or `temp` - Temperature
- `$param` - Device parameters (e.g., `$w`, `$l`, `$np`)

**Operators:**
- Arithmetic: `+`, `-`, `*`, `/`, `^`, `(`, `)`
- Comparison: `<`, `<=`, `>`, `>=`, `==`, `!=`
- Boolean: `&&`, `||`, `!`
- Functions: `min`, `max`, `abs`, `sqrt`, `exp`, `log`

**Constraint Types:**
- Value: `v[g,s] < 2.5`
- Range: `0.8 < v[g,s] < 1.2`
- Equation: `v[d,s] - v[s,b] < 3.3`
- Conditional: `if T > 80 then v[g,s] < 2.5 else v[g,s] < 5.5`
- Multi-level: `tmaxfrac` with different limits for different time fractions

### Rule Structure

**Required Fields:**
- `name` - Rule identifier
- `device` - Device type
- `parameter` - What to monitor (voltage, current, etc.)
- `type` - Constraint type (vlow, vhigh, ilow, ihigh, custom)
- `severity` - Severity level (high, medium, low, review)
- `constraint` - The actual limit expression

**Optional Fields:**
- `tmaxfrac` - Time-based transient limits (multi-level rules)
- `metadata` - Additional information
- `description` - Human-readable description
- `condition` - When to enable this rule (e.g., `enable_soa == 1`)

## DSL Syntax Examples

### 1. Simple Numeric Limit
```
name: NMOS VDS Simple Limit
device: nmos_10hv
parameter: v[d,s]
type: vhigh
severity: high
constraint {
    vhigh: 1.65
}
```

### 2. Temperature Dependent
```
name: Diode Temperature Dependent Voltage
device: dz5
parameter: v[p,n]
type: vhigh
severity: review
constraint {
    vhigh: 0.9943 - 0.0006*(T - 25)
}
```

### 3. Multi-Pin with Functions
```
name: Diode Multi-Pin with Min Function
device: dz5
parameter: v[n,p]
type: vlow
severity: review
constraint {
    vlow: min(90, 90 + v[p] - v[sub])
}
```

### 4. Current with Device Parameters
```
name: Resistor Current Width Dependency
device: poly_10hv
parameter: i[poly_10hv]
type: ihigh
severity: low
constraint {
    ihigh: $w * $np * 2.12e-4
}
```

### 5. Conditional Logic
```
name: BJT Conditional Voltage Limit
device: npn_b
parameter: v[c,e]
type: vhigh
severity: high
constraint {
    vhigh: if T > 85 then 10.0 else 12.0
}
```

### 6. Multi-Level (tmaxfrac)
```
name: NMOS Core with tmaxfrac Levels
device: nmos_10hv
parameter: v[d,s]
type: vhigh
severity: low
constraint {
    vhigh: 1.65
}
tmaxfrac {
    0.1  : 1.71,    # 10% time allowed
    0.01 : 1.84,    # 1% time allowed
    0.0  : 1.65     # 0% time allowed (never)
}
```

## Extended DSL Syntax for Complex Devices

### 1. Global Configuration
```
global {
    tmin = 0                    // Minimum violation time
    tdelay = 0                  // Delay before checking starts
    vballmsg = 1.0              // Message verbosity
    stop = 0                    // Stop on violation
    tcelsius0 = 273.15          // Temperature offset
    
    // Duration limit levels
    tmaxfrac0 = 0               // No violations allowed
    tmaxfrac1 = 0.01            // 1% time allowed
    tmaxfrac2 = 0.10            // 10% time allowed
    tmaxfrac3 = -1              // Review required
    
    // Temperature reference
    tref_soa = 25
    
    // Junction limits (temperature-dependent)
    ap_fwd_ref = 0.9943
    ap_fwd_T = -0.0006          // -1.0mV/degC
    ap_fwd = ap_fwd_ref + ap_fwd_T * (temp - tref_soa)
    ap_no_check = 999.00
    
    // Oxide voltage limits
    ap_gc_lv = 1.65             // LV devices
    ap_gc_hv = 5.5              // HV devices
    ap_fwd_hv = 1.2             // HV forward junction
    ap_gc_lv_oxrisk = 1.32      // LV oxide risk
    ap_gc_hv_oxrisk = 4.4       // HV oxide risk
    
    // Resistor limits
    dtmax_rm = 5                // Max temperature rise (degC)
    theat = 1e-7                // Thermal time constant
}
```

### 2. Monitor Templates
Define reusable monitor configurations:

```
template ovcheck_mos_core_oxrisk {
    monitor = ovcheck6
    tmin = global.tmin
    tdelay = global.tdelay
    vballmsg = global.vballmsg
    stop = global.stop
    tmaxfrac = global.tmaxfrac3
    
    checks = [
        { branch = "V(g,b)", vlow = -1.32, vhigh = 1.32, message = "Vgb_OXrisk" },
        { branch = "V(g,s)", vlow = -1.32, vhigh = 1.32, message = "Vgs_OXrisk" },
        { branch = "V(g,d)", vlow = -1.32, vhigh = 1.32, message = "Vgd_OXrisk" }
    ]
}

template ovcheck_mos_5v_oxrisk {
    monitor = ovcheck6
    tmin = global.tmin
    tdelay = global.tdelay
    vballmsg = global.vballmsg
    stop = global.stop
    tmaxfrac = global.tmaxfrac3
    
    checks = [
        { branch = "V(g,b)", vlow = -4.4, vhigh = 4.4, message = "Vgb_OXrisk" },
        { branch = "V(g,s)", vlow = -4.4, vhigh = 4.4, message = "Vgs_OXrisk" },
        { branch = "V(g,d)", vlow = -4.4, vhigh = 4.4, message = "Vgd_OXrisk" }
    ]
}

template mosfet_sub_check {
    monitor = ovcheck6
    tmin = global.tmin
    tdelay = global.tdelay
    vballmsg = global.vballmsg
    stop = global.stop
    tmaxfrac = global.tmaxfrac0
    
    checks = [
        { branch = "V(d,sub)", vlow = -70.0, vhigh = 120.0 },
        { branch = "V(s,sub)", vlow = -70.0, vhigh = 120.0 },
        { branch = "V(b,sub)", vlow = -70.0, vhigh = 120.0 }
    ]
}
```

### 3. Device Rules
Define SOA rules for specific device types:

```
device nmos_core {
    type = "nmos"
    category = "core"
    
    // Multi-level checking with different severity
    rules = [
        {
            name = "ovcheck_0"
            monitor = ovcheckva_mos2
            severity = 0                    // tmaxfrac0
            params = {
                tmin = global.tmin
                tdelay = global.tdelay
                vballmsg = global.vballmsg
                stop = global.stop
                tmaxfrac = global.tmaxfrac0
                vhigh_ds_on = 1.84
                vhigh_ds_off = 3.00
                vhigh_gc = 2.07
                vlow_gc = -2.07
                vhigh_gb_on = global.ap_no_check
                vlow_gb_on = -global.ap_no_check
                message_vds = "AMR"
                message_vgs = "AMR"
                message_vgd = "AMR"
                message_vgb = "AMR"
                message_vsb = "AMR"
                message_vdb = "AMR"
                param = "vth"
                device = "device"
            }
        },
        {
            name = "ovcheck_1"
            monitor = ovcheckva_mos2
            severity = 1                    // tmaxfrac1 (1%)
            params = {
                tmin = global.tmin
                tdelay = global.tdelay
                vballmsg = global.vballmsg
                stop = global.stop
                tmaxfrac = global.tmaxfrac1
                vhigh_ds_on = 1.71
                vhigh_ds_off = 1.88
                vhigh_gc = 1.97
                vlow_gc = -1.97
                vhigh_gb_on = global.ap_no_check
                vlow_gb_on = -global.ap_no_check
                param = "vth"
                device = "device"
            }
        },
        {
            name = "ovcheck_2"
            monitor = ovcheckva_mos2
            severity = 2                    // tmaxfrac2 (10%)
            params = {
                tmin = global.tmin
                tdelay = global.tdelay
                vballmsg = global.vballmsg
                stop = global.stop
                tmaxfrac = global.tmaxfrac2
                vhigh_ds_on = 1.65
                vhigh_ds_off = 1.82
                vhigh_gc = 1.65
                vlow_gc = -1.65
                vhigh_gb_on = 3.30
                vlow_gb_on = -2.07
                vfwd_jun_on = global.ap_no_check
                vrev_jun_on = -3.30
                vfwd_jun_off = global.ap_no_check
                vrev_jun_off = -3.30
                param = "vth"
                device = "device"
            }
        }
    ]
    
    // Substrate checks
    substrate_check = use_template(mosfet_sub_check)
}

device pmos_core {
    type = "pmos"
    category = "core"
    
    rules = [
        {
            name = "ovcheck_0"
            monitor = ovcheckva_mos2
            severity = 0
            params = {
                tmin = global.tmin
                tdelay = global.tdelay
                vballmsg = global.vballmsg
                stop = global.stop
                tmaxfrac = global.tmaxfrac0
                vhigh_ds_on = 2.08
                vhigh_ds_off = 3.00
                vhigh_gc = 1.95
                vlow_gc = -1.95
                vhigh_gb_on = global.ap_no_check
                vlow_gb_on = -global.ap_no_check
                message_vds = "AMR"
                message_vgs = "AMR"
                message_vgd = "AMR"
                message_vgb = "AMR"
                message_vsb = "AMR"
                message_vdb = "AMR"
                param = "vth"
                device = "device"
                pmosvthsign = -1
            }
        },
        // Additional severity levels...
    ]
    
    substrate_check = use_template(mosfet_sub_check)
}

device nmos_5v {
    type = "nmos"
    category = "5v"
    voltage_class = "medium"
    
    rules = [
        {
            name = "ovcheck_0"
            monitor = ovcheckva_mos2
            severity = 0
            params = {
                tmin = global.tmin
                tdelay = global.tdelay
                vballmsg = global.vballmsg
                stop = global.stop
                tmaxfrac = global.tmaxfrac0
                vhigh_ds_on = 5.5
                vhigh_ds_off = 7.0
                vhigh_gc = global.ap_gc_hv
                vlow_gc = -global.ap_gc_hv
                vhigh_gb_on = global.ap_no_check
                vlow_gb_on = -global.ap_no_check
                param = "vth"
                device = "device"
            }
        }
    ]
}

device pmos90_10hv {
    type = "pmos"
    category = "high_voltage"
    voltage_rating = 90
    
    parameters = {
        soa_hv_vmax = 90
        soa_hv_vmax_oxrisk = 72
        soa_hcitddb_a = 24
        soa_hcitddb_b = 0.38
        soa_hcitddb_vdsref = -39.299
        soa_hcitddb_vgswc = -1.5006
        soa_hcitddb_tfac = 21098
        soa_hcitddb_tref = 298
        soa_hcitddb_wfac = 4.545
        soa_hcitddb_wref = 4.00E-05
        device = "pmos90"
    }
    
    rules = [
        {
            name = "ovcheck_1"
            monitor = ovcheck6
            severity = 0
            condition = "enable_soa == 1"
            params = {
                tmin = global.tmin
                tdelay = global.tdelay
                vballmsg = global.vballmsg
                stop = global.stop
                tmaxfrac = global.tmaxfrac0
            }
            checks = [
                { branch = "V(b,g)", vlow = -global.ap_gc_hv, vhigh = global.ap_gc_hv },
                { branch = "V(s,g)", vlow = -global.ap_gc_hv, vhigh = global.ap_gc_hv },
                { branch = "V(d,g)", vlow = -params.soa_hv_vmax, vhigh = global.ap_gc_hv },
                { branch = "V(b,s)", vlow = -global.ap_fwd_hv, vhigh = global.ap_gc_hv },
                { branch = "V(b,d)", vlow = -global.ap_no_check, vhigh = params.soa_hv_vmax },
                { branch = "V(s,d)", vlow = -global.ap_fwd_hv, vhigh = params.soa_hv_vmax }
            ]
            connections = "(b g s g d g b s b d s d)"
        },
        {
            name = "ovcheck_hv_pmos_sub"
            monitor = ovcheck6
            severity = 0
            condition = "enable_soa == 1"
            params = {
                tmin = global.tmin
                tdelay = global.tdelay
                vballmsg = global.vballmsg
                stop = global.stop
                tmaxfrac = global.tmaxfrac0
            }
            checks = [
                { branch = "V(b,sub)", vlow = -40, vhigh = 100 },
                { branch = "V(sub,d)", vlow = -global.ap_no_check, vhigh = 70 }
            ]
            connections = "(b sub sub d 0 0 0 0 0 0 0 0)"
        }
    ]
    
    aging_checks = [
        {
            type = "hci_tddb"
            variant = "atype"
            condition = "enable_soa == 1"
        }
    ]
    
    oxrisk_checks = [
        {
            name = "ovcheck_5"
            monitor = ovcheck6
            severity = 3
            condition = "enable_risk_assessment == 1"
            params = {
                tmin = global.tmin
                tdelay = global.tdelay
                vballmsg = global.vballmsg
                stop = global.stop
                tmaxfrac = global.tmaxfrac3
            }
            checks = [
                { branch = "V(b,g)", vlow = -global.ap_gc_hv_oxrisk, vhigh = global.ap_gc_hv_oxrisk, message = "Vbg_OXrisk" },
                { branch = "V(s,g)", vlow = -global.ap_gc_hv_oxrisk, vhigh = global.ap_gc_hv_oxrisk, message = "Vsg_OXrisk" },
                { branch = "V(d,g)", vlow = -params.soa_hv_vmax_oxrisk, vhigh = params.soa_hv_vmax_oxrisk, message = "Vdg_OXrisk" }
            ]
            connections = "(b g s g d g 0 0 0 0 0 0)"
        }
    ]
}
```

### 4. Resistor Rules
```
device_family metal_resistors {
    base_template = "rm_10hv_soa_shared"
    
    shared_code = {
        parameters = [
            "weff_soa = w + dw_um",
            "reff_soa = rsh_soa * leff_soa / weff_soa",
            "vmax_rm_dc = jdc_rm * weff1_soa * reff_soa",
            "vmax_rm_peak = jpeak_rm * weff1_soa * reff_soa",
            "irms_max = 1.0e-3 * sqrt(jdc_rms * weff1_soa * (weff1_soa + dw_rms))"
        ]
        
        monitors = [
            {
                name = "irms_rm"
                type = ovcheck
                params = {
                    tmin = global.tmin
                    tdelay = global.tdelay
                    vballmsg = global.vballmsg
                    stop = global.stop
                    tmaxfrac = global.tmaxfrac0
                    vlow = -1.0
                    vhigh = global.dtmax_rm
                    branch1 = "V(dt)"
                    message1 = "Irms: self heating exceeds 5 degC."
                }
            },
            {
                name = "idc_rm"
                type = ovcheck
                params = {
                    tmin = global.tmin
                    tdelay = global.tdelay
                    vballmsg = global.vballmsg
                    stop = global.stop
                    tmaxfrac = global.tmaxfrac0
                    vlow = -vmax_rm_dc
                    vhigh = vmax_rm_dc
                    branch1 = "V(d,s)"
                    message1 = "Max. dc-current exceeded (violations are allowed for limited time)."
                }
            },
            {
                name = "ipeak_rm"
                type = ovcheck
                params = {
                    tmin = global.tmin
                    tdelay = global.tdelay
                    vballmsg = global.vballmsg
                    stop = global.stop
                    tmaxfrac = global.tmaxfrac0
                    vlow = -vmax_rm_peak
                    vhigh = vmax_rm_peak
                    branch1 = "V(d,s)"
                    message1 = "Max. peak current exceeded (violations <100ns may be allowed)."
                }
            }
        ]
        
        subcircuits = [
            {
                name = "sh_dummy"
                type = "shmonitor_nofeedback"
                connections = "(d s dt)"
                params = {
                    r = "reff_soa"
                    irms_max = "irms_max"
                    dtmax = "global.dtmax_rm"
                    theat = "global.theat"
                }
            }
        ]
        
        instantiations = [
            "soacheck_rms (dt 0) irms_rm",
            "soacheck_dc (d s) idc_rm",
            "soacheck_peak (d s) ipeak_rm"
        ]
    }
}

device rm1_10hv extends metal_resistors {
    parameters = {
        weff1_soa = "w - 0.04"
        rsh_soa = "nom_rs_m1*delr_rs_m1"
        leff_soa = "l + dl_m1"
        jdc_rm = 4.05e-3
        jdc_rms = 367.8
        dw_rms = 0.53
        jpeak_rm = 4.05e-1
    }
    condition = "enable_soa == 1"
}

device rm2_10hv extends metal_resistors {
    parameters = {
        weff1_soa = "w - 0.04"
        rsh_soa = "nom_rs_m2*delr_rs_m2"
        leff_soa = "l + dl_m2"
        jdc_rm = 4.05e-3
        jdc_rms = 131.2
        dw_rms = 1.21
        jpeak_rm = 4.05e-1
    }
    condition = "enable_soa == 1"
}
```

### 5. Capacitor Rules
```
device cap_low_voltage {
    type = "capacitor"
    voltage_class = "low"
    
    rules = [
        {
            name = "ovcheck_cap_sub"
            monitor = ovcheck
            severity = 0
            params = {
                tmin = global.tmin
                tdelay = global.tdelay
                vballmsg = global.vballmsg
                stop = global.stop
                tmaxfrac = global.tmaxfrac0
                vlow = -70.0
                vhigh = 120.0
                branch1 = "V(nw,sub)"
            }
        }
    ]
    
    oxrisk_checks = [
        {
            name = "ovcheck_cap_low_oxrisk"
            monitor = ovcheck
            severity = 3
            params = {
                tmin = global.tmin
                tdelay = global.tdelay
                vballmsg = global.vballmsg
                stop = global.stop
                tmaxfrac = global.tmaxfrac3
                vlow = -1.32
                vhigh = 1.32
                branch1 = "V(t,nw)"
                message1 = "Vtnw_OXrisk"
            }
        }
    ]
}
```

### 6. Diode Rules
```
device diode_n {
    type = "diode"
    polarity = "n"
    
    rules = [
        {
            name = "ovcheck_diode_sub_n"
            monitor = ovcheck
            severity = 0
            params = {
                tmin = global.tmin
                tdelay = global.tdelay
                vballmsg = global.vballmsg
                stop = global.stop
                tmaxfrac = global.tmaxfrac0
                vlow = -70.0
                vhigh = 120.0
                branch1 = "V(n,sub)"
            }
        }
    ]
}

device diode_p {
    type = "diode"
    polarity = "p"
    
    rules = [
        {
            name = "ovcheck_diode_sub_p"
            monitor = ovcheck
            severity = 0
            params = {
                tmin = global.tmin
                tdelay = global.tdelay
                vballmsg = global.vballmsg
                stop = global.stop
                tmaxfrac = global.tmaxfrac0
                vlow = -70.0
                vhigh = 120.0
                branch1 = "V(p,sub)"
            }
        }
    ]
}
```

## Automated Toolchain Architecture

### Core Components

#### 1. SOA Rule Creator (DSL Generator)
Tool for SR team to generate perfectly-formed SOA-DSL from Excel or manual input.

**Features:**
- Excel parser for existing SOA rule spreadsheets
- Interactive rule builder with validation
- Template library for common patterns
- Export to DSL format

#### 2. DSL Parser
Convert DSL to Abstract Syntax Tree (AST).

**Responsibilities:**
- Lexical analysis (tokenization)
- Syntax parsing
- AST construction
- Error reporting with line numbers

#### 3. Rule Validator
Comprehensive validation of rules.

**Checks:**
- Syntax correctness
- Semantic validation (undefined variables, type mismatches)
- Device parameter existence
- Pin name validity
- Expression evaluation
- Constraint consistency

#### 4. Code Generator
Generate Spectre netlist from validated AST.

**Outputs:**
- `soachecks_top.scs` - Main SOA check file
- Section organization (global, shared, device-specific)
- Proper Verilog-A monitor instantiations
- Conditional compilation directives

#### 5. Test Case Generator
Automated comprehensive test creation.

**Generates:**
- Boundary test cases (at limits)
- Violation test cases (beyond limits)
- Temperature sweep tests
- Corner case tests
- Regression test suite

#### 6. Documentation Generator
Uniformly generated documentation.

**Outputs:**
- HTML/PDF rule documentation
- Cross-reference tables
- Device coverage reports
- Rule change history

### Workflow

```
┌─────────────────┐
│  Excel Rules    │
│  or Manual DSL  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  DSL Generator  │  ◄── SR Team
│  (Rule Creator) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   SOA-DSL File  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   DSL Parser    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│      AST        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Rule Validator  │  ◄── Automated validation
└────────┬────────┘
         │
         ├─────────────────┬─────────────────┬──────────────────┐
         ▼                 ▼                 ▼                  ▼
┌─────────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Code Generator  │ │ Test Gen     │ │ Doc Gen      │ │ CAD Tool     │
│                 │ │              │ │              │ │ Integration  │
└────────┬────────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
         │                 │                │                │
         ▼                 ▼                ▼                ▼
┌─────────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│soachecks_top.scs│ │ Test Cases   │ │ Documentation│ │ CAD Configs  │
└─────────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
         │                 │                │
         └─────────────────┴────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Model Team   │  ◄── Review & Deploy
                    │ Design Team  │
                    └──────────────┘
```

## Code Generation Strategy

### Input Files
- `soa_rules.dsl` - Main rule definitions
- `soa_global.dsl` - Global parameters and constants
- `soa_templates.dsl` - Reusable templates
- `soa_devices.dsl` - Device definitions and parameters

### Output Files
- `soachecks_top.scs` - Generated Spectre netlist
- `soa_tests/` - Test case directory
- `soa_docs/` - Documentation directory

### Generation Process

#### Phase 1: Parsing
1. **Lexical Analysis**: Tokenize DSL input
2. **Syntax Parsing**: Build parse tree
3. **AST Construction**: Create abstract syntax tree
4. **Symbol Table**: Build device, parameter, and variable tables

#### Phase 2: Validation
1. **Syntax Validation**: Check grammar correctness
2. **Semantic Validation**: 
   - Verify device types exist
   - Check parameter references
   - Validate pin names
   - Type checking for expressions
3. **Constraint Validation**:
   - Evaluate constant expressions
   - Check for contradictory constraints
   - Verify tmaxfrac ordering
4. **Cross-Reference Validation**:
   - Template references
   - Global parameter usage
   - Device inheritance

#### Phase 3: Code Generation
1. **Section Generation**:
   - Global parameters section
   - Shared model definitions
   - Device-specific sections
2. **Monitor Selection**:
   - Map DSL rules to appropriate Verilog-A monitors
   - `ovcheckva_mos2` for MOS with state-dependent limits
   - `ovcheck`/`ovcheck6` for simple voltage checks
   - `parcheck3` for parameter monitoring
   - `ovcheck_pwl` for piecewise-linear boundaries
3. **Parameter Mapping**:
   - DSL constraints → monitor parameters
   - Expression evaluation for computed values
   - Temperature dependency handling
4. **Instantiation Generation**:
   - Monitor model statements
   - Instance connections
   - Conditional compilation (`if enable_soa == 1`)
5. **Formatting**:
   - Proper Spectre syntax
   - Comments with DSL source reference
   - Consistent indentation

### Mapping DSL to Spectre

#### Simple Voltage Constraint
**DSL:**
```
name: NMOS VDS Limit
device: nmos_10hv
parameter: v[d,s]
type: vhigh
severity: high
constraint { vhigh: 1.65 }
```

**Generated Spectre:**
```spectre
section nmos_10hv_soa
model ovcheck_0 ovcheck
+ tmin=global_tmin tdelay=global_tdelay vballmsg=global_vballmsg stop=global_stop
+ tmaxfrac=tmaxfrac0
+ vlow=-999.0 vhigh=1.65 branch1="V(d,s)"
+ message1="NMOS VDS Limit"
soacheck0 (d s) ovcheck_0
endsection nmos_10hv_soa
```

#### Multi-Level Constraint
**DSL:**
```
name: NMOS Core Multi-Level
device: nmos_core
parameter: v[d,s]
type: vhigh
severity: low
constraint { vhigh: 1.65 }
tmaxfrac {
    0.1  : 1.71,
    0.01 : 1.84,
    0.0  : 1.65
}
```

**Generated Spectre:**
```spectre
section nmos_core_soa
model ovcheck_0 ovcheck
+ tmin=global_tmin tdelay=global_tdelay vballmsg=global_vballmsg stop=global_stop
+ tmaxfrac=tmaxfrac0
+ vlow=-999.0 vhigh=1.65 branch1="V(d,s)"
+ message1="NMOS Core Multi-Level (0%)"
model ovcheck_1 ovcheck
+ tmin=global_tmin tdelay=global_tdelay vballmsg=global_vballmsg stop=global_stop
+ tmaxfrac=tmaxfrac1
+ vlow=-999.0 vhigh=1.84 branch1="V(d,s)"
+ message1="NMOS Core Multi-Level (1%)"
model ovcheck_2 ovcheck
+ tmin=global_tmin tdelay=global_tdelay vballmsg=global_vballmsg stop=global_stop
+ tmaxfrac=tmaxfrac2
+ vlow=-999.0 vhigh=1.71 branch1="V(d,s)"
+ message1="NMOS Core Multi-Level (10%)"
soacheck0 (d s) ovcheck_0
soacheck1 (d s) ovcheck_1
soacheck2 (d s) ovcheck_2
endsection nmos_core_soa
```

#### Temperature-Dependent Constraint
**DSL:**
```
name: Diode Temp Dependent
device: dz5
parameter: v[p,n]
type: vhigh
severity: review
constraint {
    vhigh: 0.9943 - 0.0006*(T - 25)
}
```

**Generated Spectre:**
```spectre
section dz5_soa
parameters
+ vhigh_calc = 0.9943 - 0.0006*(temp - 25)
model ovcheck_0 ovcheck
+ tmin=global_tmin tdelay=global_tdelay vballmsg=global_vballmsg stop=global_stop
+ tmaxfrac=tmaxfrac3
+ vlow=-999.0 vhigh=vhigh_calc branch1="V(p,n)"
+ message1="Diode Temp Dependent"
soacheck0 (p n) ovcheck_0
endsection dz5_soa
```

#### MOS State-Dependent
**DSL:**
```
name: NMOS Core State Dependent
device: nmos_core
parameter: v[d,s]
type: vhigh
severity: high
constraint {
    vhigh_on: 1.84,
    vhigh_off: 3.00
}
gate_control {
    vhigh_gc: 2.07,
    vlow_gc: -2.07
}
```

**Generated Spectre:**
```spectre
section nmos_core_soa
model ovcheck_0 ovcheckva_mos2
+ tmin=global_tmin tdelay=global_tdelay vballmsg=global_vballmsg stop=global_stop
+ tmaxfrac=tmaxfrac0
+ vhigh_ds_on=1.84 vhigh_ds_off=3.00
+ vhigh_gc=2.07 vlow_gc=-2.07
+ vhigh_gb_on=ap_no_check vlow_gb_on=-ap_no_check
+ param="vth" device=device
soacheck0 (d g s b) ovcheck_0
endsection nmos_core_soa
```

## Implementation Plan

### Phase 1: Core Infrastructure (Weeks 1-3)
- [ ] Define formal DSL grammar (EBNF)
- [ ] Implement lexer/tokenizer
- [ ] Implement parser (recursive descent or parser combinator)
- [ ] Build AST data structures
- [ ] Create symbol table manager
- [ ] Implement basic validator

### Phase 2: Code Generation (Weeks 4-6)
- [ ] Design code generation templates
- [ ] Implement Spectre section generators
- [ ] Parameter resolution and expression evaluator
- [ ] Monitor type selection logic
- [ ] Conditional compilation handling
- [ ] Format and comment generation

### Phase 3: Excel Integration (Weeks 7-8)
- [ ] Excel parser for existing SOA rules
- [ ] Rule extraction and normalization
- [ ] DSL generation from Excel data
- [ ] Validation of extracted rules
- [ ] Batch conversion tool

### Phase 4: Test Generation (Weeks 9-10)
- [ ] Test case template system
- [ ] Boundary test generator
- [ ] Violation test generator
- [ ] Temperature sweep generator
- [ ] Test suite organization

### Phase 5: Documentation & Tooling (Weeks 11-12)
- [ ] Documentation generator (HTML/PDF)
- [ ] CLI tool with subcommands
- [ ] Syntax highlighting for editors (VSCode, Vim)
- [ ] Diff tool for validation
- [ ] Integration scripts for CAD tools

### Phase 6: Validation & Deployment (Weeks 13-16)
- [ ] Test on SMOS10HV rule set
- [ ] Compare generated vs. manual code
- [ ] Performance benchmarking
- [ ] User training materials
- [ ] Production deployment

## Example Usage

```bash
# Compile DSL to Spectre netlist
soa-compiler compile soa_rules.dsl -o soachecks_top.scs

# Validate DSL without generating
soa-compiler validate soa_rules.dsl

# Generate documentation
soa-compiler docs soa_rules.dsl -o soa_rules.html

# Compare with existing file
soa-compiler diff soa_rules.dsl soachecks_top.scs.original
```

## Benefits & ROI

### Quantitative Benefits

**Effort Reduction:**
- **95% manual effort reduction** overall
- **90% reduction** in rule extraction (Excel → Implementation)
- **90% reduction** in rule validation
- **90% reduction** in test case generation
- **60% reduction** in error-related debugging
- **30% reduction** in cross-department alignment

**Time Savings:**
- Current: 3+ weeks for full QA of SMOS10HV rules
- With DSL: ~1 day for generation + review
- **Annual AOP savings** across multiple projects

**Error Reduction:**
- Eliminate manual copy-paste errors
- Automated validation catches issues before simulation
- Consistent rule format reduces misinterpretation

### Qualitative Benefits

**Standardization:**
- Unified rule format across all devices
- Consistent documentation
- Department-agnostic specification

**Quality:**
- Automated validation ensures correctness
- Comprehensive test coverage
- Reproducible results

**Maintainability:**
- Single source of truth (DSL files)
- Easy to update and version control
- Clear change tracking

**Knowledge Preservation:**
- Rules documented in readable format
- Less dependency on individual expertise
- Easier onboarding for new team members

### Strategic Advantages

**Competitive Edge:**
- Faster time-to-market for new processes
- Higher quality with lower cost
- Industry-leading automation

**Resource Optimization:**
- Free up engineers for higher-value work
- Reduce manual, repetitive tasks
- Better resource allocation

**Risk Reduction:**
- Lower error rates
- Consistent quality
- Reduced schedule risk

**Scalability:**
- Easy to add new process nodes
- Reusable across projects
- Vendor-agnostic approach

### ROI Analysis

**Development Investment:**
- 0.6 - 0.8 AOP for initial development
- Includes toolchain, validation, and deployment

**Payback Period:**
- 1.5 - 2.0 AOP (Development + Deployment)
- Break-even after first 2-3 major projects

**5-Year Impact:**
- AOP reduction: 2+ AOP annually
- Significant error reduction
- Improved cross-team collaboration
- Foundation for future automation

## Future Extensions

1. **Excel Import**: Parse Excel SOA rules directly into DSL
2. **Multi-Process Support**: Generate rules for different process nodes
3. **Optimization**: Merge similar checks to reduce simulation overhead
4. **Visualization**: Generate graphical SOA boundaries
5. **Test Generation**: Auto-generate test cases for SOA violations
