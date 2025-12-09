# SOA DSL Format Comparison

## Overview
This document compares three structured data formats for the SOA DSL: JSON, XML, and YAML.

## Format Comparison

### JSON (JavaScript Object Notation)
**Pros:**
- ✅ Widely supported across all programming languages
- ✅ Native support in JavaScript/TypeScript
- ✅ Strict syntax reduces parsing errors
- ✅ Good tooling support (validators, formatters, editors)
- ✅ Compact and efficient
- ✅ Easy to generate programmatically

**Cons:**
- ❌ No comments support (requires workarounds)
- ❌ Verbose with quotes and braces
- ❌ Less human-readable for complex structures
- ❌ No multi-line strings without escaping

**Best For:**
- Machine-to-machine communication
- API integration
- Programmatic generation from Excel
- Web-based tools

### XML (eXtensible Markup Language)
**Pros:**
- ✅ Self-documenting with tags
- ✅ Supports attributes and nested elements
- ✅ Schema validation (XSD)
- ✅ Comments supported
- ✅ Industry standard for many EDA tools
- ✅ Good for hierarchical data

**Cons:**
- ❌ Very verbose (opening/closing tags)
- ❌ More difficult to read and write manually
- ❌ Larger file sizes
- ❌ More complex parsing

**Best For:**
- Integration with existing EDA tools
- Formal schema validation
- Complex hierarchical structures
- Industry standard compliance

### YAML (YAML Ain't Markup Language)
**Pros:**
- ✅ Most human-readable format
- ✅ Minimal syntax (indentation-based)
- ✅ Comments supported
- ✅ Multi-line strings easy
- ✅ Less verbose than JSON/XML
- ✅ Easy to write and maintain manually
- ✅ Supports anchors and references (DRY principle)

**Cons:**
- ❌ Indentation-sensitive (can cause errors)
- ❌ Less strict parsing (can be ambiguous)
- ❌ Slightly slower parsing than JSON
- ❌ Less universal support than JSON

**Best For:**
- Human-written configuration
- Manual rule creation
- Documentation
- Version control (readable diffs)

## Side-by-Side Example

### Simple Rule

**JSON:**
```json
{
  "name": "NMOS Core VDS Limit",
  "device": "nmos_core",
  "parameter": "v[d,s]",
  "type": "vhigh",
  "severity": "high",
  "constraint": {
    "vhigh": 1.65
  },
  "description": "Drain-source voltage limit"
}
```

**XML:**
```xml
<rule name="NMOS Core VDS Limit" device="nmos_core" severity="high">
  <parameter>v[d,s]</parameter>
  <type>vhigh</type>
  <constraint>
    <vhigh>1.65</vhigh>
  </constraint>
  <description>Drain-source voltage limit</description>
</rule>
```

**YAML:**
```yaml
name: "NMOS Core VDS Limit"
device: nmos_core
parameter: "v[d,s]"
type: vhigh
severity: high
constraint:
  vhigh: 1.65
description: "Drain-source voltage limit"
```

### Complex Rule with Multi-Level

**JSON:**
```json
{
  "name": "NMOS Core Multi-Level",
  "device": "nmos_core",
  "parameter": "v[d,s]",
  "type": "vhigh",
  "severity": "low",
  "constraint": {
    "vhigh": 1.65
  },
  "tmaxfrac": {
    "0.0": 1.65,
    "0.01": 1.84,
    "0.1": 1.71
  }
}
```

**XML:**
```xml
<rule name="NMOS Core Multi-Level" device="nmos_core" severity="low">
  <parameter>v[d,s]</parameter>
  <type>vhigh</type>
  <constraint>
    <vhigh>1.65</vhigh>
  </constraint>
  <tmaxfrac>
    <level frac="0.0" value="1.65"/>
    <level frac="0.01" value="1.84"/>
    <level frac="0.1" value="1.71"/>
  </tmaxfrac>
</rule>
```

**YAML:**
```yaml
name: "NMOS Core Multi-Level"
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

## File Size Comparison

For the same rule set (20 rules):
- **YAML**: ~8 KB (baseline)
- **JSON**: ~10 KB (+25%)
- **XML**: ~15 KB (+87%)

## Parsing Performance

Relative parsing speed (approximate):
- **JSON**: 1.0x (fastest)
- **YAML**: 0.8x
- **XML**: 0.6x

## Recommendation

### Primary Format: **YAML**

**Rationale:**
1. **Human-Centric**: Engineers will write and review rules manually
2. **Readability**: Critical for cross-department communication
3. **Comments**: Essential for documenting complex rules
4. **Maintainability**: Easy to update and version control
5. **Learning Curve**: Can be learned in 30 minutes (per PPT goal)

### Secondary Format: **JSON**

**Rationale:**
1. **Tool Integration**: For automated Excel conversion
2. **API Communication**: For web-based rule creator tools
3. **Validation**: Easier to validate programmatically
4. **Generation**: Easy to generate from Python/JavaScript

### Strategy: **Multi-Format Support**

Implement converters:
```
YAML ←→ JSON ←→ XML
  ↓       ↓       ↓
    Spectre Netlist
```

**Workflow:**
1. **Manual Creation**: Engineers write YAML
2. **Excel Import**: Tool generates JSON
3. **Conversion**: JSON ↔ YAML as needed
4. **Code Generation**: All formats → Spectre
5. **EDA Integration**: XML for tool compatibility

## Implementation Priority

### Phase 1: YAML Support
- YAML parser
- YAML validator
- YAML → Spectre code generator
- YAML examples and templates

### Phase 2: JSON Support
- JSON parser
- JSON ↔ YAML converter
- Excel → JSON tool
- JSON schema validation

### Phase 3: XML Support (Optional)
- XML parser
- XML ↔ JSON converter
- XSD schema
- EDA tool integration

## Example Files

All three formats are provided in the `examples/` directory:
- `soa_rules.yaml` - Primary format (recommended)
- `soa_rules.json` - Secondary format (tool integration)
- `soa_rules.xml` - Tertiary format (EDA compatibility)

## Tooling Recommendations

### YAML
- **Parser**: PyYAML (Python), js-yaml (JavaScript)
- **Validator**: yamllint, custom schema validator
- **Editor**: VSCode with YAML extension

### JSON
- **Parser**: Built-in (Python, JavaScript)
- **Validator**: jsonschema (Python), ajv (JavaScript)
- **Editor**: Any text editor with JSON support

### XML
- **Parser**: lxml (Python), xml2js (JavaScript)
- **Validator**: xmlschema, XSD validation
- **Editor**: VSCode with XML extension

## Conclusion

**Primary recommendation: YAML** for its balance of human-readability, expressiveness, and ease of use. Support JSON for tool integration and optionally XML for EDA tool compatibility.

The DSL should be format-agnostic internally, with parsers for each format feeding into a common AST representation.
