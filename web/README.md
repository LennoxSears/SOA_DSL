# SOA Rule Creator - Web Interface

A user-friendly web interface for Silicon Reliability teams to create SOA (Safe Operating Area) rules without writing YAML manually.

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
- **Server-side validation** - Uses the same validator as CLI
- **Error reporting** - Clear error messages
- **Warning display** - Shows potential issues

### 💾 Export
- **YAML download** - Download generated rules as .yaml file
- **Ready to use** - Generated files work with soa-dsl CLI tool

## Installation

### Prerequisites
- Python 3.8 or higher
- pip

### Install Dependencies

```bash
cd SOA_DSL
pip install -r requirements.txt
```

This installs:
- PyYAML (for YAML generation)
- Flask (for web server)

## Usage

### Start the Web Server

**Linux/Mac:**
```bash
cd SOA_DSL/web
python3 run.py
```

**Windows:**
```cmd
cd SOA_DSL\web
python run.py
```

### Access the Interface

Open your browser and navigate to:
```
http://localhost:5000
```

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

```bash
# Validate
python soa_dsl_cli.py validate soa_rules.yaml

# Generate Spectre code
python soa_dsl_cli.py compile soa_rules.yaml -o output/soachecks_top.scs
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

### Backend (Flask)
- **app.py** - Flask application with REST API
- **Routes:**
  - `GET /` - Main interface
  - `POST /api/validate` - Validate single rule
  - `POST /api/generate-yaml` - Generate YAML from rules
  - `POST /api/validate-yaml` - Validate complete YAML
  - `POST /api/download-yaml` - Download YAML file

### Frontend
- **index.html** - Main interface template
- **style.css** - Responsive styling
- **script.js** - Client-side logic and API calls

### Integration
- Uses the same parser and validator as CLI tool
- Generates YAML compatible with soa-dsl CLI
- No data stored on server (all client-side)

## API Endpoints

### POST /api/validate
Validate a single rule before adding.

**Request:**
```json
{
  "name": "NMOS Core VDS Limit",
  "device": "nmos_core",
  "parameter": "v[d,s]",
  "type": "vhigh",
  "severity": "high",
  "constraint": {
    "vhigh": 1.65
  }
}
```

**Response:**
```json
{
  "valid": true,
  "errors": [],
  "warnings": []
}
```

### POST /api/generate-yaml
Generate YAML from rules list.

**Request:**
```json
{
  "process": "SMOS10HV",
  "rules": [...]
}
```

**Response:**
```json
{
  "success": true,
  "yaml": "version: 1.0\n..."
}
```

### POST /api/validate-yaml
Validate complete YAML document.

**Request:**
```json
{
  "yaml": "version: 1.0\n..."
}
```

**Response:**
```json
{
  "valid": true,
  "errors": [],
  "warnings": [],
  "rule_count": 5
}
```

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, edit `web/run.py` and change:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Use different port
```

### Module Not Found
Make sure you're running from the correct directory:
```bash
cd SOA_DSL/web
python run.py
```

### Flask Not Installed
```bash
pip install flask
```

### Cannot Access from Other Machines
The server binds to `0.0.0.0` which allows access from other machines on the network.
Access via: `http://<your-ip>:5000`

## Development

### Run in Debug Mode
Debug mode is enabled by default in `run.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

### Modify Templates
Edit `templates/index.html` for UI changes.
Changes are reflected immediately in debug mode.

### Modify Styles
Edit `static/style.css` for styling changes.
Refresh browser to see changes.

### Modify Logic
Edit `static/script.js` for client-side logic.
Edit `app.py` for server-side logic.

## Security Notes

### Production Deployment
For production use:
1. Set `debug=False` in `run.py`
2. Use a production WSGI server (gunicorn, uwsgi)
3. Add authentication if needed
4. Use HTTPS
5. Add rate limiting

### Example Production Setup
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
cd SOA_DSL
gunicorn -w 4 -b 0.0.0.0:5000 web.app:app
```

## Future Enhancements

Potential features for future versions:
- [ ] Multi-level (tmaxfrac) support in UI
- [ ] State-dependent rule builder
- [ ] Multi-branch rule builder
- [ ] Template library (common rules)
- [ ] Import existing YAML for editing
- [ ] Rule duplication
- [ ] Bulk operations
- [ ] Export to Excel
- [ ] User authentication
- [ ] Save/load sessions
- [ ] Rule validation history

## Support

For issues or questions:
- Check the main README.md
- Review DSL_DESIGN.md for rule syntax
- See CODE_GENERATION_EXAMPLES.md for examples

## License

Same as main SOA_DSL project.
