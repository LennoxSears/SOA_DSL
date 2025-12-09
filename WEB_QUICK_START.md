# SOA Rule Creator - Web Interface Quick Start

## 🚀 Get Started in 1 Step

### Just Open the File!

**Double-click** `web/index.html` to open it in your browser.

That's it! No installation, no dependencies, no server needed.

---

## 📝 Creating Your First Rule

### Example: NMOS Core VDS Limit

1. **Fill in the form:**
   - **Rule Name:** `NMOS Core VDS Limit`
   - **Device Type:** Select `nmos_core` from dropdown
   - **Parameter:** `v[d,s]`
   - **Rule Type:** Select `vhigh`
   - **Severity:** Select `high`
   - **V High:** `1.65`
   - **Description:** `Drain-source voltage must not exceed 1.65V`

2. **Click "Add Rule"**

3. **See your rule** in the "Rules" tab

4. **Switch to "YAML Preview"** tab to see the generated YAML

5. **Click "Validate"** to check the YAML

6. **Click "Download YAML"** to save the file

---

## 🎯 Common Use Cases

### Simple Voltage Limit
- **Parameter:** `v[d,s]`, `v[g,s]`, `v[d,g]`
- **V High:** `1.65`, `2.5`, `5.5`
- **V Low:** `-1.65`, `0`

### Temperature-Dependent
- **V High:** `0.9943 - 0.0006*(T - 25)`
- **V High:** `if T > 85 then 10.0 else 12.0`

### Current with Device Parameters
- **Parameter:** `i[rm1_10hv]`
- **I High:** `$w * 4.05e-3`
- **I High:** `$w * $np * 2.12e-4`

### With Functions
- **V Low:** `min(90, 90 + v[p] - v[sub])`
- **V High:** `max(70, min(120, 90 + v[sub]))`

---

## 💡 Tips

### Parameter Syntax
- **Voltage:** `v[pin1,pin2]` or `v[pin]`
- **Current:** `i[device]`
- **Temperature:** `T` or `temp`
- **Device params:** `$w`, `$l`, `$np`

### Expressions
- **Math:** `+`, `-`, `*`, `/`, `^`
- **Functions:** `min()`, `max()`, `abs()`, `sqrt()`
- **Conditionals:** `if CONDITION then VALUE1 else VALUE2`

### Validation
- Click "Validate" in YAML Preview tab
- Green = Success ✅
- Red = Errors ❌
- Fix errors before downloading

---

## 🔧 Troubleshooting

### File Won't Open
Right-click `index.html` and select "Open with" → Chrome/Firefox/Edge

### Can't Download YAML
Some browsers block downloads from local files. Use a local web server:

```bash
cd SOA_DSL/web
python3 -m http.server 8080
```

Then open: [http://localhost:8080](http://localhost:8080)

### Blank Page
Try a different browser or use the local web server method above.

---

## 📥 Using Generated YAML

After downloading `soa_rules.yaml`, use it with the CLI:

**Linux/Mac:**
```bash
# Using shell script
./soa-dsl validate soa_rules.yaml
./soa-dsl compile soa_rules.yaml -o output/soachecks_top.scs

# Or using Python directly
python3 soa_dsl_cli.py validate soa_rules.yaml
python3 soa_dsl_cli.py compile soa_rules.yaml -o output/soachecks_top.scs
```

**Windows:**
```cmd
# Using batch file
soa-dsl.bat validate soa_rules.yaml
soa-dsl.bat compile soa_rules.yaml -o output\soachecks_top.scs

# Or using Python directly
python soa_dsl_cli.py validate soa_rules.yaml
python soa_dsl_cli.py compile soa_rules.yaml -o output\soachecks_top.scs
```

---

## 📚 More Information

- **Full Web Guide:** [web/README.md](web/README.md)
- **DSL Syntax:** [DSL_DESIGN.md](DSL_DESIGN.md)
- **Examples:** [CODE_GENERATION_EXAMPLES.md](CODE_GENERATION_EXAMPLES.md)
- **Main README:** [README.md](README.md)

---

## 🎉 You're Ready!

The web interface makes it easy to create SOA rules without learning YAML syntax. Just fill in the form, validate, and download!

**No installation. No dependencies. Just open and use.**
