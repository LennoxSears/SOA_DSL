# SOA Rule Creator - Advanced Features Implementation

**Status:** In Progress  
**Goal:** Support all rule types from examples/soa_rules.yaml

---

## Rule Types to Support

### ✅ Currently Supported (Simple Rules)
1. **vhigh** - Simple voltage high limit
2. **vlow** - Simple voltage low limit
3. **ihigh** - Simple current high limit
4. **ilow** - Simple current low limit
5. **range** - Voltage/current range (vlow + vhigh)

### 🚧 To Be Implemented (Complex Rules)

#### 1. Multi-Level (tmaxfrac)
**Example:** NMOS Core Multi-Level VDS
```yaml
tmaxfrac:
  0.0: 1.65      # Never exceed
  0.01: 1.84     # 1% of time
  0.1: 1.71      # 10% of time
```

**UI Approach:**
- Dynamic list of level/value pairs
- Add/remove buttons for levels
- Validation: levels must be 0.0, 0.01, 0.1, or -1

#### 2. State-Dependent
**Example:** NMOS Core State Dependent
```yaml
type: state_dependent
constraint:
  vhigh_on: 1.84
  vhigh_off: 3.00
gate_control:
  vhigh_gc: 2.07
  vlow_gc: -2.07
monitor_params:
  param: "vth"
  vgt: 0.0
```

**UI Approach:**
- Show/hide section based on rule type
- Fields for ON/OFF constraints
- Gate control section
- Monitor parameters section
- Optional: gate_bulk, junction sections

#### 3. Multi-Branch
**Example:** NMOS 90V Multi-Branch
```yaml
type: multi_branch
parameter: multi
branches:
  - branch: "V(g,b)"
    vhigh: "ap_gc_hv"
    vlow: "-ap_gc_hv"
  - branch: "V(g,s)"
    vhigh: "ap_gc_hv"
    vlow: "-ap_gc_hv"
connections: "(g b g s g d s b d b d s)"
```

**UI Approach:**
- Dynamic list of branches
- Each branch has: name, vhigh, vlow
- Connections field
- Add/remove branch buttons

#### 4. Current with Self-Heating
**Example:** Metal-1 Resistor with Self-Heating
```yaml
type: current_with_heating
constraints:
  - name: "DC Current"
    type: idc
    ihigh: "$w * 4.05e-3"
  - name: "Peak Current"
    type: ipeak
    ihigh: "$w * 4.05e-1"
  - name: "RMS Current"
    type: irms
    ihigh: "1.0e-3 * sqrt(367.8 * $w * ($w + 0.53))"
self_heating:
  dtmax: "dtmax_rm"
  theat: "theat"
```

**UI Approach:**
- Dynamic list of current constraints
- Each constraint: name, type (idc/ipeak/irms), ihigh, message
- Self-heating section with dtmax, theat, monitor
- Optional: device_params section

#### 5. Aging Check
**Example:** PMOS 90V with HCI/TDDB Check
```yaml
aging_check:
  type: hci_tddb
  variant: atype
  params:
    soa_hcitddb_a: 24
    soa_hcitddb_b: 0.38
    ...
```

**UI Approach:**
- Optional aging check section
- Type selector (hci_tddb)
- Variant field
- Dynamic params list (key-value pairs)

#### 6. Branches (Oxide Risk)
**Example:** NMOS Core Oxide Risk
```yaml
branches:
  - branch: "V(g,b)"
    vhigh: "ap_gc_lv_oxrisk"
    vlow: "-ap_gc_lv_oxrisk"
    message: "Vgb_OXrisk"
  - branch: "V(g,s)"
    vhigh: "ap_gc_lv_oxrisk"
    vlow: "-ap_gc_lv_oxrisk"
    message: "Vgs_OXrisk"
```

**UI Approach:**
- Similar to multi-branch but with message field
- Used for oxide risk assessment
- Can be combined with simple vhigh type

---

## Implementation Strategy

### Phase 1: Dynamic Form Architecture ✅
- [x] Create HTML structure with collapsible sections
- [x] Add CSS for dynamic sections
- [x] Update header to indicate advanced support

### Phase 2: Rule Type Selector (In Progress)
- [ ] Implement rule type change handler
- [ ] Show/hide relevant sections based on type
- [ ] Map rule types to required sections:
  - `vhigh, vlow, ihigh, ilow, range` → Simple Constraints
  - `vhigh, vlow` + tmaxfrac checkbox → Multi-Level
  - `state_dependent` → State-Dependent Section
  - `multi_branch` → Multi-Branch Section
  - `current_with_heating` → Current Heating Section

### Phase 3: Dynamic Lists
- [ ] Implement tmaxfrac level management
- [ ] Implement branch management (multi-branch)
- [ ] Implement voltage branch management (oxide risk)
- [ ] Implement current constraints management
- [ ] Add/remove functionality for all lists

### Phase 4: YAML Generation
- [ ] Update generateYAML() to handle all rule types
- [ ] Add proper indentation for nested structures
- [ ] Handle optional sections (aging_check, device_params, etc.)
- [ ] Escape strings properly

### Phase 5: Validation
- [ ] Validate required fields per rule type
- [ ] Check tmaxfrac levels are valid (0.0, 0.01, 0.1, -1)
- [ ] Validate branch structures
- [ ] Validate current constraint types

### Phase 6: Testing
- [ ] Test each rule type from examples
- [ ] Verify generated YAML matches examples
- [ ] Test with CLI validator
- [ ] Cross-browser testing

---

## Technical Challenges

### 1. Complex Nested Structures
**Challenge:** YAML has deeply nested structures (state_dependent with gate_control, gate_bulk, junction, monitor_params, messages)

**Solution:** 
- Use collapsible sections
- Only show relevant fields
- Provide good defaults

### 2. Dynamic Arrays
**Challenge:** Branches, constraints, tmaxfrac levels are arrays of varying length

**Solution:**
- Use JavaScript to manage dynamic lists
- Add/remove buttons
- Store in arrays, render to YAML

### 3. Optional Fields
**Challenge:** Many fields are optional (aging_check, device_params, connections, etc.)

**Solution:**
- Only include in YAML if filled
- Provide checkboxes to enable optional sections
- Clear documentation of what's required vs optional

### 4. Expression Validation
**Challenge:** Values can be numbers or expressions

**Solution:**
- Accept any string
- Let CLI validator handle expression validation
- Provide examples in placeholders

---

## User Experience Considerations

### Progressive Disclosure
- Start with basic fields visible
- Show advanced sections only when rule type selected
- Use collapsible sections for complex features

### Guidance
- Tooltips for complex fields
- Examples in placeholders
- Link to documentation
- Show example rules

### Validation Feedback
- Real-time validation where possible
- Clear error messages
- Highlight missing required fields

---

## Current Status

### Completed
- ✅ HTML structure with all sections
- ✅ CSS for dynamic sections
- ✅ Basic form layout
- ✅ Changed "Device Type" to "Device Name"

### In Progress
- 🚧 JavaScript for dynamic form behavior
- 🚧 Rule type selector logic
- 🚧 Dynamic list management

### Not Started
- ⏳ YAML generation for complex types
- ⏳ Comprehensive validation
- ⏳ Testing with all rule types

---

## Next Steps

1. Implement rule type selector in JavaScript
2. Add dynamic list management functions
3. Update YAML generation for all types
4. Test with examples from soa_rules.yaml
5. Update documentation

---

## Estimated Complexity

| Rule Type | Complexity | Estimated Lines of JS |
|-----------|------------|----------------------|
| Simple (current) | Low | ~500 (done) |
| Multi-level | Medium | +100 |
| State-dependent | High | +200 |
| Multi-branch | Medium | +150 |
| Current heating | High | +200 |
| Aging check | Medium | +100 |
| Branches | Medium | +100 |
| **Total** | **High** | **~1,350** |

---

## Alternative Approach

Given the complexity, consider:

1. **Hybrid Approach:** 
   - Web UI for simple rules (80% of use cases)
   - CLI for complex rules (20% of use cases)
   - Web UI can import/export YAML for editing

2. **Template-Based:**
   - Provide templates for each rule type
   - User fills in values
   - Less flexible but simpler

3. **Wizard-Based:**
   - Multi-step wizard for complex rules
   - One step per section
   - Better UX for complex workflows

---

**Recommendation:** Implement full support incrementally, starting with most common rule types (simple, multi-level, state-dependent), then add others based on user feedback.
