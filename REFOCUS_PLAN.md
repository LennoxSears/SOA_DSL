# Project Refocus Plan

**Goal:** Redesign SOA DSL to directly map to Verilog-A monitors in `/spectre/soachecks_top.scs`

---

## Current Situation

### What We Have
- Abstract YAML spec with "rule types" (vhigh, vlow, ihigh, ilow, etc.)
- Parser that validates abstract rules
- Code generator that creates Spectre code
- Web interface for creating abstract rules

### The Problem
- Current spec doesn't match actual monitor structure
- Monitors in `soachecks_top.scs` have specific parameters
- Gap between YAML and actual Spectre code

---

## What Needs to Change

### 1. YAML Spec Redesign
**Current:**
```yaml
rules:
  - name: "NMOS Core VDS Limit"
    device: nmos_core
    parameter: "v[d,s]"
    type: vhigh
    severity: high
    constraint:
      vhigh: 1.65
```

**New (Monitor-Based):**
```yaml
monitors:
  - name: "NMOS Core VDS Check"
    monitor_type: ovcheck
    model_name: ovcheck_nmos_core_vds
    device_pattern: "nmos_core"
    parameters:
      tmin: "global_tmin"
      tdelay: "global_tdelay"
      vballmsg: "global_vballmsg"
      stop: "global_stop"
      tmaxfrac: "tmaxfrac0"
      vlow: -1.65
      vhigh: 1.65
      branch1: "V(d,s)"
      message1: "Vds"
```

### 2. Monitor Types to Support

#### ovcheck (single branch)
```yaml
monitor_type: ovcheck
parameters:
  - tmin, tdelay, vballmsg, stop
  - tmaxfrac
  - vlow, vhigh, branch1, message1
```

#### ovcheck6 (6 branches)
```yaml
monitor_type: ovcheck6
parameters:
  - tmin, tdelay, vballmsg, stop
  - tmaxfrac
  - vlow1, vhigh1, branch1, message1
  - vlow2, vhigh2, branch2, message2
  - ... up to 6
```

#### ovcheckva_mos2 (MOS-specific)
```yaml
monitor_type: ovcheckva_mos2
parameters:
  - tmin, tdelay, vballmsg, stop
  - tmaxfrac
  - vhigh_on, vhigh_off
  - vhigh_gc, vlow_gc
  - param, vgt
```

#### ovcheckva_pwl (piecewise linear)
```yaml
monitor_type: ovcheckva_pwl
parameters:
  - tmin, tdelay, vballmsg, stop
  - tmaxfrac
  - vlow, vhigh, branch1, message1
```

#### ovcheckva_ldmos_hci_tddb (aging)
```yaml
monitor_type: ovcheckva_ldmos_hci_tddb
parameters:
  - tmin, tdelay, vballmsg, stop
  - atype
  - soa_hcitddb_a through soa_hcitddb_n
```

#### parcheckva3 (parameter check)
```yaml
monitor_type: parcheckva3
parameters:
  - tmin, tdelay, vballmsg, stop
  - tmaxfrac
  - param, vgt
  - vlow, vhigh
```

#### ovcheck with self-heating
```yaml
monitor_type: ovcheck
self_heating:
  dtmax: "dtmax_rm"
  theat: "theat"
  monitor: "temperature"
parameters:
  - idc_high, ipeak_high, irms_high
```

### 3. Code Generation Changes

**Current:** Generates abstract rules  
**New:** Generates actual model definitions

**Output should be:**
```spectre
section <section_name>
model <model_name> <monitor_type>
+ tmin=global_tmin tdelay=global_tdelay vballmsg=global_vballmsg stop=global_stop
+ tmaxfrac=tmaxfrac0
+ vlow=<value> vhigh=<value> branch1="<branch>" message1="<msg>"
endsection <section_name>
```

### 4. Parser Changes

- Validate monitor_type against known types
- Validate parameters for each monitor type
- Check required vs optional parameters
- Validate parameter values (expressions, numbers, strings)

### 5. Web Interface Changes

- Change from "rule types" to "monitor types"
- Show monitor-specific parameters
- Dynamic form based on selected monitor
- Preview shows actual Spectre model definition

---

## Implementation Steps

### Phase 1: New YAML Spec ✅
- [x] Analyze soachecks_top.scs
- [x] Document monitor types
- [ ] Design new YAML schema
- [ ] Create examples for each monitor type

### Phase 2: Update Parser
- [ ] Define monitor type schemas
- [ ] Update validation logic
- [ ] Add monitor-specific parameter validation
- [ ] Update error messages

### Phase 3: Update Code Generator
- [ ] Generate model definitions
- [ ] Generate section blocks
- [ ] Handle global parameters
- [ ] Format output to match soachecks_top.scs

### Phase 4: Update Web Interface
- [ ] Change UI to monitor-based
- [ ] Add monitor type selector
- [ ] Dynamic parameter forms
- [ ] Update YAML preview

### Phase 5: Documentation
- [ ] Update DSL_DESIGN.md
- [ ] Update examples
- [ ] Update README
- [ ] Create monitor reference guide

### Phase 6: Testing
- [ ] Test each monitor type
- [ ] Validate generated code
- [ ] Compare with soachecks_top.scs
- [ ] Integration testing

---

## Benefits of New Approach

1. **Direct Mapping:** YAML directly maps to Spectre model definitions
2. **Clarity:** Users understand what monitors they're using
3. **Accuracy:** Generated code matches actual usage
4. **Flexibility:** Can use any monitor parameter
5. **Maintainability:** Easy to add new monitor types

---

## Migration Path

### For Existing Users
1. Provide conversion tool from old YAML to new YAML
2. Document mapping between old "rule types" and new "monitor types"
3. Keep examples showing both formats

### Backward Compatibility
- Option 1: Support both formats (detect and convert)
- Option 2: Clean break (recommended - project is new)

---

## Next Steps

1. ✅ Complete monitor analysis
2. Create new YAML schema with examples
3. Update parser for new schema
4. Update code generator
5. Update web interface
6. Update all documentation
7. Test thoroughly

---

**Decision Point:** Should we maintain backward compatibility or make a clean break?

**Recommendation:** Clean break - project is new, better to get it right now.
