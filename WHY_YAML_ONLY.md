# Why YAML Only?

## Decision: Single Format Support

After comprehensive analysis of YAML, JSON, TOML, and XML, we decided to support **YAML only** for the SOA DSL.

## Rationale

### 1. Simplicity
- **One format to learn** - Engineers only need to know YAML syntax
- **One parser to maintain** - Reduced code complexity (350 lines → 180 lines)
- **One set of examples** - Clearer documentation
- **Faster development** - No need to maintain multiple parsers

### 2. YAML is the Clear Winner

| Criterion | YAML | JSON | TOML | XML |
|-----------|------|------|------|-----|
| Human Readable | ✅ Best | ❌ Verbose | ✅ Good | ❌ Worst |
| Comments | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes |
| Minimal Syntax | ✅ Best | ❌ Quotes | ✅ Good | ❌ Tags |
| Learning Curve | ✅ 30 min | ✅ Easy | ✅ Easy | ❌ Complex |
| Industry Adoption | ✅ High | ✅ High | ⚠️ Medium | ⚠️ Legacy |

### 3. Comments are Essential

SOA rules need extensive documentation:
```yaml
# This limit is based on reliability testing at 125°C
# See report: SOA-2024-001
constraint:
  vhigh: 1.65  # Maximum safe voltage
```

JSON doesn't support comments - this alone disqualifies it.

### 4. Human-Centric Design

Engineers will:
- **Write rules manually** - YAML's minimal syntax reduces errors
- **Review rules** - YAML is most readable
- **Maintain rules** - Comments explain complex logic
- **Collaborate** - YAML diffs are clean in version control

### 5. Proven in Industry

YAML is the standard for:
- **Kubernetes** - Container orchestration
- **Docker Compose** - Service definitions
- **CI/CD** - GitHub Actions, GitLab CI, CircleCI
- **Ansible** - Infrastructure automation
- **OpenAPI** - API specifications

Engineers already know YAML.

### 6. No Need for Multiple Formats

**Original thinking**: Support multiple formats for flexibility
**Reality**: 
- 95% of users will use YAML
- Multiple formats add complexity without value
- Conversion between formats is rarely needed
- Maintenance burden outweighs benefits

### 7. Code Simplicity

**Before** (multi-format):
- 4 parsers (YAML, JSON, TOML, XML)
- Factory pattern for format selection
- Format-specific error handling
- 350+ lines of parser code

**After** (YAML-only):
- 1 parser (YAML)
- Direct instantiation
- Unified error handling
- 180 lines of parser code

**Result**: 50% code reduction, easier to maintain

## What About Tool Integration?

**Q**: Don't we need JSON for programmatic generation?

**A**: No. YAML is just as easy to generate programmatically:

```python
import yaml

rules = {
    'version': '1.0',
    'rules': [
        {'name': 'Rule 1', 'device': 'nmos_core', ...}
    ]
}

with open('rules.yaml', 'w') as f:
    yaml.dump(rules, f)
```

## What About Excel Import?

**Q**: Should Excel import generate JSON?

**A**: No. Excel import should generate YAML directly:

```python
# Excel → YAML (direct)
excel_data = parse_excel('rules.xlsx')
yaml_rules = convert_to_yaml(excel_data)
save_yaml('rules.yaml', yaml_rules)
```

No intermediate format needed.

## What About EDA Tool Compatibility?

**Q**: Don't EDA tools use XML?

**A**: We generate **Spectre netlist**, not XML. The DSL format is internal to our toolchain.

```
Excel/Manual → YAML DSL → Parser → Validator → Generator → Spectre Netlist
```

EDA tools never see the YAML - they only see the generated Spectre code.

## Migration Path

**For existing JSON/TOML/XML files** (if any):

```bash
# One-time conversion (if needed)
python3 -c "
import yaml, json
data = json.load(open('rules.json'))
yaml.dump(data, open('rules.yaml', 'w'))
"
```

## Benefits of YAML-Only

### For Users
- ✅ **Simpler** - One format to learn
- ✅ **Clearer** - No format confusion
- ✅ **Faster** - Less decision-making
- ✅ **Better docs** - Focused examples

### For Developers
- ✅ **Less code** - 50% reduction
- ✅ **Easier maintenance** - One parser
- ✅ **Faster development** - No format juggling
- ✅ **Better testing** - Focused test cases

### For the Project
- ✅ **Cleaner** - No format comparison docs
- ✅ **Focused** - Energy on features, not formats
- ✅ **Professional** - Clear, opinionated design
- ✅ **Maintainable** - Long-term sustainability

## Conclusion

**YAML-only is the right choice** because:

1. ✅ YAML is objectively the best format for this use case
2. ✅ Comments are essential (eliminates JSON)
3. ✅ Human-readability is critical (eliminates XML)
4. ✅ Industry standard (engineers already know it)
5. ✅ Simpler codebase (50% less parser code)
6. ✅ No real need for multiple formats
7. ✅ Easier to maintain and extend

**Decision**: Support YAML only. Period.

---

*"Perfection is achieved not when there is nothing more to add, but when there is nothing left to take away."* - Antoine de Saint-Exupéry
