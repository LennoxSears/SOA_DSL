# SOA DSL - Windows Setup Guide

## Installation on Windows

### Prerequisites
- Python 3.8 or higher
- pip (comes with Python)

### Step 1: Install Python
If you don't have Python installed:
1. Download from https://www.python.org/downloads/
2. Run installer and **check "Add Python to PATH"**
3. Verify installation:
   ```cmd
   python --version
   ```

### Step 2: Clone Repository
```cmd
git clone https://github.com/LennoxSears/SOA_DSL.git
cd SOA_DSL
```

### Step 3: Install Dependencies
```cmd
pip install pyyaml
```

Or use requirements.txt:
```cmd
pip install -r requirements.txt
```

### Step 4: Verify Installation
```cmd
python src\soa_dsl\cli.py --help
```

---

## Usage on Windows

### Method 1: Using Batch File (Recommended)

Use the provided `soa-dsl.bat` file:

```cmd
REM Validate
soa-dsl.bat validate examples\soa_rules.yaml

REM Generate
soa-dsl.bat compile examples\soa_rules.yaml -o output\soachecks_top.scs
```

### Method 2: Direct Python Invocation

Run the CLI module directly:

```cmd
REM Validate
python src\soa_dsl\cli.py validate examples\soa_rules.yaml

REM Generate
python src\soa_dsl\cli.py generate examples\soa_rules.yaml -o output\soachecks_top.scs

REM Compile (validate + generate)
python src\soa_dsl\cli.py compile examples\soa_rules.yaml -o output\soachecks_top.scs
```

### Method 3: Python API

Create a Python script:

```python
# my_soa_script.py
import sys
sys.path.insert(0, 'src')

from soa_dsl import parse_file, SOAValidator, SpectreGenerator

# Parse YAML
doc = parse_file('examples/soa_rules.yaml')

# Validate
validator = SOAValidator()
if validator.validate(doc):
    print("✅ Validation passed")
    
    # Generate
    generator = SpectreGenerator()
    generator.generate(doc, 'output/soachecks_top.scs')
    print("✅ Generated output/soachecks_top.scs")
else:
    print("❌ Validation failed")
    validator.print_report()
```

Run it:
```cmd
python my_soa_script.py
```

---

## Common Commands

### Validate a YAML file
```cmd
python src\soa_dsl\cli.py validate examples\soa_rules.yaml
```

### Generate Spectre code
```cmd
python src\soa_dsl\cli.py generate examples\soa_rules.yaml -o output\soachecks.scs
```

### Compile (validate + generate)
```cmd
python src\soa_dsl\cli.py compile examples\soa_rules.yaml -o output\soachecks.scs
```

### Strict validation (warnings as errors)
```cmd
python src\soa_dsl\cli.py validate examples\soa_rules.yaml --strict
```

---

## Troubleshooting

### Error: "python is not recognized"
**Solution**: Add Python to PATH
1. Find Python installation (usually `C:\Python3X\`)
2. Add to PATH:
   - Right-click "This PC" → Properties
   - Advanced system settings → Environment Variables
   - Edit "Path" → Add Python directory

### Error: "No module named 'yaml'"
**Solution**: Install PyYAML
```cmd
pip install pyyaml
```

### Error: "No module named 'soa_dsl'"
**Solution**: Run from project root directory
```cmd
cd E:\SOA_DSL
python src\soa_dsl\cli.py --help
```

### Path Issues
Windows uses backslashes (`\`) instead of forward slashes (`/`):
- ✅ Correct: `examples\soa_rules.yaml`
- ❌ Wrong: `examples/soa_rules.yaml`

However, Python accepts both, so forward slashes also work.

---

## Creating a Shortcut

### Option 1: Add to PATH
1. Copy `soa-dsl.bat` to a directory in your PATH
2. Run from anywhere:
   ```cmd
   soa-dsl validate examples\soa_rules.yaml
   ```

### Option 2: Create Alias (PowerShell)
Add to your PowerShell profile:
```powershell
function soa-dsl { python E:\SOA_DSL\src\soa_dsl\cli.py $args }
```

### Option 3: Install as Package
```cmd
cd E:\SOA_DSL
pip install -e .
```

Then use:
```cmd
soa-dsl validate examples\soa_rules.yaml
```

---

## Example Workflow on Windows

```cmd
REM Navigate to project
cd E:\SOA_DSL

REM Validate your rules
python src\soa_dsl\cli.py validate examples\soa_rules.yaml

REM Generate Spectre code
python src\soa_dsl\cli.py compile examples\soa_rules.yaml -o output\my_soachecks.scs

REM Check the output
type output\my_soachecks.scs
```

---

## PowerShell vs Command Prompt

Both work, but syntax differs slightly:

### Command Prompt (cmd.exe)
```cmd
python src\soa_dsl\cli.py validate examples\soa_rules.yaml
```

### PowerShell
```powershell
python src\soa_dsl\cli.py validate examples\soa_rules.yaml
```

Both are equivalent for this tool.

---

## Virtual Environment (Optional but Recommended)

### Create virtual environment
```cmd
python -m venv venv
```

### Activate (Command Prompt)
```cmd
venv\Scripts\activate.bat
```

### Activate (PowerShell)
```powershell
venv\Scripts\Activate.ps1
```

### Install dependencies
```cmd
pip install pyyaml
```

### Deactivate
```cmd
deactivate
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Validate | `python src\soa_dsl\cli.py validate examples\soa_rules.yaml` |
| Generate | `python src\soa_dsl\cli.py generate examples\soa_rules.yaml -o output\out.scs` |
| Compile | `python src\soa_dsl\cli.py compile examples\soa_rules.yaml -o output\out.scs` |
| Help | `python src\soa_dsl\cli.py --help` |
| Version | `python src\soa_dsl\cli.py validate --help` |

---

## Next Steps

1. ✅ Verify Python installation: `python --version`
2. ✅ Install PyYAML: `pip install pyyaml`
3. ✅ Test the tool: `python src\soa_dsl\cli.py validate examples\soa_rules.yaml`
4. ✅ Create your own rules in YAML format
5. ✅ Generate Spectre code

---

## Support

If you encounter issues:
1. Check Python version: `python --version` (should be 3.8+)
2. Check PyYAML: `pip show pyyaml`
3. Verify you're in the project directory: `cd E:\SOA_DSL`
4. Check file paths use backslashes on Windows

For more help, see:
- README.md - Project overview
- DSL_DESIGN.md - DSL syntax guide
- CODE_GENERATION_EXAMPLES.md - Examples
