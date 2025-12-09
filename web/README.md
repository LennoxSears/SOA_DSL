# SOA Rule Creator - Web Interface

A user-friendly web interface for Silicon Reliability teams to create SOA (Safe Operating Area) rules without writing YAML manually.

**Pure Frontend** - No backend server or dependencies required! Just open the HTML file in your browser.

## Features

### 🎨 Intuitive Interface
- **Form-based rule creation** - No need to learn YAML syntax
- **Real-time validation** - Catch errors before generating
- **Live YAML preview** - See the generated YAML as you work
- **Rule management** - Add, view, and delete rules easily

### 📋 Rule Creation
- **Device selection** - Choose from 25+ device types
- **Constraint types** - Voltage (vhigh, vlow), Current (ihigh, ilow)
- **Expressions** - Support for mathematical expressions and conditions
- **Severity levels** - High, medium, low, review
- **Descriptions** - Document your rules

### ✅ Validation
- **Client-side validation** - Immediate feedback
- **Error reporting** - Clear error messages
- **No server required** - All processing happens in your browser

### 💾 Export
- **YAML download** - Download generated rules as .yaml file
- **Ready to use** - Generated files work with soa-dsl CLI tool

## Installation

**No installation required!** Just open the HTML file in your browser.

## Usage

### Option 1: Direct File Access (Easiest)

Simply **double-click** `web/index.html` to open it in your default browser.

Or right-click and select **"Open with"** → your preferred browser.

### Option 2: Local Web Server (Recommended for some browsers)

Some browsers have security restrictions on local files. If Option 1 doesn't work, serve the file with a simple web server:

**Python 3:**
```bash
cd SOA_DSL/web
python3 -m http.server 8080
```

**Python 2:**
```bash
cd SOA_DSL/web
python -m SimpleHTTPServer 8080
```

**Node.js (if installed):**
```bash
cd SOA_DSL/web
npx http-server -p 8080
```

Then open your browser and navigate to: [http://localhost:8080](http://localhost:8080)

### Create Rules

1. **Fill in the form:**
   - Rule Name (e.g., "NMOS Core VDS Limit")
   - Device Type (select from dropdown)
   - Parameter (e.g., "v[d,s]", "i[device]", "T")
   - Rule Type (vhigh, vlow, ihigh, etc.)
   - Severity (high, medium, low, review)
   - Constraints (vhigh, vlow, ihigh, ilow)

2. **Add constraints:**
   - Simple values: `1.65`, `-1.65`
   - Expressions: `0.9943 - 0.0006*(T - 25)`
   - Device parameters: `$w * 4.05e-3`
   - Functions: `min(90, 90 + v[p] - v[sub])`

3. **Click "Add Rule"** - Rule is added to the list

4. **View rules** - See all added rules in the "Rules" tab

5. **Preview YAML** - Switch to "YAML Preview" tab

6. **Validate** - Click "Validate" to check the YAML

7. **Download** - Click "Download YAML" to save the file

### Use Generated YAML

The downloaded YAML file can be used with the CLI tool:

**Linux/Mac:**
```bash
./soa-dsl validate soa_rules.yaml
./soa-dsl compile soa_rules.yaml -o output/soachecks_top.scs
```

**Windows:**
```cmd
soa-dsl.bat validate soa_rules.yaml
soa-dsl.bat compile soa_rules.yaml -o output\soachecks_top.scs
```

## Examples

### Simple Voltage Constraint

**Form Input:**
- Name: `NMOS Core VDS Limit`
- Device: `nmos_core`
- Parameter: `v[d,s]`
- Type: `vhigh`
- Severity: `high`
- V High: `1.65`

**Generated YAML:**
```yaml
- name: "NMOS Core VDS Limit"
  device: nmos_core
  parameter: "v[d,s]"
  type: vhigh
  severity: high
  constraint:
    vhigh: 1.65
```

### Temperature-Dependent Constraint

**Form Input:**
- Name: `Diode Temperature Dependent`
- Device: `dz5`
- Parameter: `v[p,n]`
- Type: `vhigh`
- Severity: `review`
- V High: `0.9943 - 0.0006*(T - 25)`

**Generated YAML:**
```yaml
- name: "Diode Temperature Dependent"
  device: dz5
  parameter: "v[p,n]"
  type: vhigh
  severity: review
  constraint:
    vhigh: "0.9943 - 0.0006*(T - 25)"
```

### Current with Device Parameters

**Form Input:**
- Name: `Metal Resistor Current`
- Device: `rm1_10hv`
- Parameter: `i[rm1_10hv]`
- Type: `ihigh`
- Severity: `high`
- I High: `$w * 4.05e-3`

**Generated YAML:**
```yaml
- name: "Metal Resistor Current"
  device: rm1_10hv
  parameter: "i[rm1_10hv]"
  type: ihigh
  severity: high
  constraint:
    ihigh: "$w * 4.05e-3"
```

## Architecture

### Pure Frontend Design
- **Single HTML file** - All code embedded (HTML, CSS, JavaScript)
- **No backend** - No Flask, no Python server needed
- **No dependencies** - Works offline, no npm/pip install
- **Client-side only** - All processing in browser

### File Structure
```
web/
  index.html          # Standalone web interface (open this!)
  README.md           # This file
```

### How It Works
1. User fills form with rule details
2. JavaScript validates input
3. JavaScript generates YAML structure
4. User downloads YAML file
5. YAML file used with CLI tool

## Browser Compatibility

Works in all modern browsers:
- ✅ Chrome/Edge (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Opera

**Note:** Internet Explorer is not supported.

## Troubleshooting

### File Won't Open
Try opening with a specific browser:
- Right-click `index.html`
- Select "Open with" → Chrome/Firefox/Edge

### Can't Download YAML
Some browsers block downloads from local files. Use Option 2 (local web server) instead.

### Blank Page
Check browser console (F12) for errors. Try a different browser or use a local web server.

### Port Already in Use (Option 2)
If port 8080 is taken, use a different port:
```bash
python3 -m http.server 8081
```

## Advantages of Pure Frontend

### ✅ No Installation
- No Python dependencies
- No Flask installation
- No pip/npm commands
- Just open and use

### ✅ Portable
- Copy single HTML file anywhere
- Email to colleagues
- Put on shared drive
- Works offline

### ✅ Secure
- No server to configure
- No network exposure
- All data stays local
- No authentication needed

### ✅ Simple
- One file to maintain
- No backend code
- No API endpoints
- Easy to understand

## Limitations

### Client-Side Only
- Basic validation (not as thorough as CLI validator)
- No integration with existing Python validator
- Cannot parse existing YAML files for editing

### Workaround
For full validation, download the YAML and use CLI:
```bash
./soa-dsl validate soa_rules.yaml
```

## Future Enhancements

Potential features for future versions:
- [ ] Import existing YAML for editing
- [ ] More advanced validation rules
- [ ] Template library (common rules)
- [ ] Rule duplication
- [ ] Export to Excel
- [ ] Save/load sessions (localStorage)
- [ ] Dark mode
- [ ] Keyboard shortcuts

## Support

For issues or questions:
- Check the main README.md
- Review DSL_DESIGN.md for rule syntax
- See CODE_GENERATION_EXAMPLES.md for examples

## License

Same as main SOA_DSL project.
