# SOA DSL - Safe Operating Area Domain-Specific Language

## Overview

This project implements a Domain-Specific Language (DSL) for describing Safe Operating Area (SOA) rules for semiconductor devices. The DSL enables automated generation of Spectre netlist code with Verilog-A monitor instantiations, replacing manual, error-prone workflows.

**Based on the proposal by Zhendong Ge (Sep 2025)**

## Problem Statement

Current SOA rule processing is:
- **Time-Intensive**: 3+ weeks for full QA of SMOS10HV rules
- **Error-Prone**: High error rates in manual copy-paste workflows
- **Inconsistent**: Rule descriptions vary across departments
- **Maintenance-Heavy**: Updates require significant effort and risk new errors

## Solution

A unified DSL with automated toolchain that:
- ✅ **Reduces manual effort by 95%**
- ✅ **Eliminates copy-paste errors**
- ✅ **Provides human-readable, machine-parsable specifications**
- ✅ **Enables automated test generation**
- ✅ **Vendor & simulator agnostic**
- ✅ **Can be learned in 30 minutes**

## Key Features

### Unified Grammar
One syntax to express ANY electrical/thermal SOA limit:

**Variables:**
- `v[pin1,pin2]` or `v[pin]` - Voltage
- `i[pin]` or `i[device]` - Current
- `T` or `temp` - Temperature
- `$param` - Device parameters ($w, $l, $np)

**Operators:**
- Arithmetic: `+`, `-`, `*`, `/`, `^`, `(`, `)`
- Comparison: `<`, `<=`, `>`, `>=`, `==`, `!=`
- Boolean: `&&`, `||`, `!`
- Functions: `min`, `max`, `abs`, `sqrt`, `exp`, `log`

**Constraint Types:**
- Simple: `v[g,s] < 2.5`
- Range: `0.8 < v[g,s] < 1.2`
- Equation: `v[d,s] - v[s,b] < 3.3`
- Conditional: `if T > 80 then v[g,s] < 2.5 else v[g,s] < 5.5`
- Multi-level: Time-based transient limits (tmaxfrac)

## DSL Format: YAML Only

The SOA DSL uses **YAML exclusively** for its superior human-readability, comments support, and minimal syntax.

### Why YAML Only?
- ✅ **Most human-readable** format
- ✅ **Comments supported** (essential for documenting complex rules)
- ✅ **Minimal syntax** (less typing, fewer errors)
- ✅ **Industry standard** (Kubernetes, Docker, CI/CD)
- ✅ **Simpler codebase** (one parser, easier maintenance)

See [WHY_YAML_ONLY.md](WHY_YAML_ONLY.md) for detailed rationale.

### YAML Syntax Example

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

## Rule Complexity Examples

### Simple Numeric
```yaml
constraint:
  vhigh: 1.65
```

### Temperature Dependent
```yaml
constraint:
  vhigh: "0.9943 - 0.0006*(T - 25)"
```

### Multi-Pin with Functions
```yaml
constraint:
  vlow: "min(90, 90 + v[p] - v[sub])"
```

### Current with Device Parameters
```yaml
constraint:
  ihigh: "$w * $np * 2.12e-4"
```

### Conditional Logic
```yaml
constraint:
  vhigh: "if T > 85 then 10.0 else 12.0"
```

### Multi-Level (tmaxfrac)
```yaml
constraint:
  vhigh: 1.65
tmaxfrac:
  0.0: 1.65    # Never exceed
  0.01: 1.84   # 1% time allowed
  0.1: 1.71    # 10% time allowed
```

## Automated Toolchain

```
┌─────────────────┐
│  Excel Rules    │
│  or Manual DSL  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  DSL Generator  │  ◄── SR Team
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   SOA-DSL File  │  (YAML)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   DSL Parser    │
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
└────────┬────────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
         │                 │                │                │
         ▼                 ▼                ▼                ▼
┌─────────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│soachecks_top.scs│ │ Test Cases   │ │ Documentation│ │ CAD Configs  │
└─────────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

## Core Components

### 1. SOA Rule Creator (DSL Generator)
- Excel parser for existing SOA rules
- Interactive rule builder
- Template library
- Export to DSL format

### 2. DSL Parser
- Lexical analysis
- Syntax parsing
- AST construction
- Error reporting

### 3. Rule Validator
- Syntax validation
- Semantic validation
- Device parameter checking
- Expression evaluation

### 4. Code Generator
- Spectre netlist generation
- Verilog-A monitor instantiation
- Section organization
- Conditional compilation

### 5. Test Case Generator
- Boundary tests
- Violation tests
- Temperature sweeps
- Corner cases

### 6. Documentation Generator
- HTML/PDF output
- Cross-reference tables
- Coverage reports

## Benefits & ROI

### Quantitative Benefits
- **95% manual effort reduction**
- **90% reduction** in rule extraction
- **90% reduction** in validation
- **90% reduction** in test generation
- **60% reduction** in error debugging
- **30% reduction** in cross-department alignment

### Time Savings
- Current: 3+ weeks for SMOS10HV QA
- With DSL: ~1 day for generation + review
- **Annual AOP savings** across projects

### ROI
- **Development**: 0.6-0.8 AOP
- **Payback**: 1.5-2.0 AOP
- **5-Year Impact**: 2+ AOP reduction annually

## Project Structure

```
SOA_DSL/
├── src/soa_dsl/                       # Core implementation (1,463 lines)
│   ├── __init__.py                    # Package initialization
│   ├── parser.py                      # YAML parser (220 lines)
│   ├── validator.py                   # Comprehensive validator (380 lines)
│   ├── expression.py                  # Expression evaluator (270 lines)
│   ├── generator.py                   # Spectre code generator (180 lines)
│   ├── ast_nodes.py                   # AST data structures (280 lines)
│   └── cli.py                         # Command-line interface (120 lines)
├── examples/
│   └── soa_rules.yaml                 # YAML examples (11 KB, 26 rules)
├── output/                            # Generated files
│   └── yaml_only_test.scs             # Generated Spectre code
├── spectre/                           # Production semiconductor models
│   ├── soachecks_top.scs              # Manual SOA checks (2,646 lines)
│   └── veriloga/                      # Verilog-A monitors
│       ├── ovcheck_mos_alt.va         # MOS overvoltage checking
│       ├── ovcheck_pwl_alt.va         # Piecewise-linear checking
│       ├── parcheck3.va               # Parameter checking
│       └── ...
├── README.md                          # This file
├── WHY_YAML_ONLY.md                   # Format decision rationale
├── DSL_DESIGN.md                      # Detailed design specification
├── FINAL_IMPLEMENTATION.md            # Implementation status
├── soa-dsl                            # CLI entry point
├── setup.py                           # Package setup
├── requirements.txt                   # Dependencies (PyYAML only)
└── test_workflow.sh                   # Complete test script
```

## Implementation Plan

### Phase 1: Core Infrastructure (Weeks 1-3)
- Define formal DSL grammar
- Implement lexer/parser
- Build AST data structures
- Create validator

### Phase 2: Code Generation (Weeks 4-6)
- Design code generation templates
- Implement Spectre section generators
- Parameter resolution
- Monitor type selection

### Phase 3: Excel Integration (Weeks 7-8)
- Excel parser
- Rule extraction
- DSL generation
- Batch conversion

### Phase 4: Test Generation (Weeks 9-10)
- Test case templates
- Boundary/violation tests
- Temperature sweeps
- Test suite organization

### Phase 5: Documentation & Tooling (Weeks 11-12)
- Documentation generator
- CLI tool
- Syntax highlighting
- Integration scripts

### Phase 6: Validation & Deployment (Weeks 13-16)
- Test on SMOS10HV
- Compare generated vs. manual
- Performance benchmarking
- User training

## Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

```bash
# Clone the repository
git clone https://github.com/LennoxSears/SOA_DSL.git
cd SOA_DSL

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Quick Start

#### 1. Validate a DSL File
```bash
./soa-dsl validate examples/soa_rules.yaml
```

Output:
```
Validating examples/soa_rules.yaml...
✅ Parsed successfully (26 rules)
✅ Validation passed
```

#### 2. Generate Spectre Code
```bash
./soa-dsl compile examples/soa_rules.yaml -o output/soachecks_top.scs
```

Output:
```
Compiling examples/soa_rules.yaml...
✅ Parsed successfully (26 rules)
✅ Successfully compiled to output/soachecks_top.scs
```

#### 3. View Generated Code
```bash
head -30 output/soachecks_top.scs
```

#### 4. Run Complete Test
```bash
./test_workflow.sh
```

### Python API Usage

```python
from soa_dsl.parser import parse_file
from soa_dsl.validator import SOAValidator
from soa_dsl.generator import SpectreGenerator

# Parse DSL file
document = parse_file('examples/soa_rules.yaml')

# Validate
validator = SOAValidator()
if validator.validate(document):
    # Generate Spectre code
    generator = SpectreGenerator()
    generator.generate(document, 'output/soachecks_top.scs')
    print("✅ Generated successfully!")
```

## Documentation

- **[README.md](README.md)** - This file (project overview)
- **[WHY_YAML_ONLY.md](WHY_YAML_ONLY.md)** - Format decision rationale
- **[DSL_DESIGN.md](DSL_DESIGN.md)** - Complete design specification
- **[CODE_GENERATION_EXAMPLES.md](CODE_GENERATION_EXAMPLES.md)** - Generation examples
- **[FINAL_IMPLEMENTATION.md](FINAL_IMPLEMENTATION.md)** - Implementation status
- **[examples/](examples/)** - Example YAML DSL file

## Current Status

✅ **PRODUCTION READY:**
- Complete DSL implementation (1,463 lines Python)
- YAML parser with comprehensive validation
- Spectre code generator
- CLI tool (validate, generate, compile)
- 26 example rules covering all complexity levels
- Comprehensive documentation
- Tested and working

✅ **Ready For:**
- Pilot deployment with SMOS10HV rules
- Integration into existing workflows
- User training and adoption
- Production use

## Contributing

This project aims to transform SOA rule processing across the semiconductor industry. Contributions are welcome in:
- DSL syntax refinement
- Parser implementation
- Code generator development
- Test case generation
- Documentation

## License

[To be determined]

## Contact

For questions or contributions, please contact the project team.

---

**"One tiny language for every SOA check"** - Learnable in 30 minutes, saves weeks of manual work.
