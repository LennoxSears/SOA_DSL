"""
SOA Rule Creator - Web Interface
Flask backend for creating SOA rules through a web UI
"""

from flask import Flask, render_template, request, jsonify, send_file
import yaml
import sys
from pathlib import Path
from io import BytesIO
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from soa_dsl import SOAValidator, parse_file
from soa_dsl.parser import SOAParser

app = Flask(__name__)

# Device types
DEVICE_TYPES = [
    "nmos_core", "pmos_core", "nmos_5v", "pmos_5v",
    "nmos90_10hv", "pmos90_10hv", "nmos90b_10hv", "pmos90b_10hv",
    "nmoshs45_10hv", "pmoshs45_10hv",
    "dz5", "npn_b", "pnp_b",
    "poly_10hv", "rm1_10hv", "rm2_10hv", "rm3_10hv", "rm4_10hv",
    "cap_low", "cap_mid", "cap_high",
    "diode_n", "diode_p",
    "bandgap_ref", "temp_sensor"
]

# Rule types
RULE_TYPES = [
    "vhigh", "vlow", "ihigh", "ilow", "range",
    "state_dependent", "multi_branch", "current_with_heating"
]

# Severity levels
SEVERITIES = ["high", "medium", "low", "review"]


@app.route('/')
def index():
    """Main page - rule creator interface"""
    return render_template('index.html',
                         device_types=DEVICE_TYPES,
                         rule_types=RULE_TYPES,
                         severities=SEVERITIES)


@app.route('/api/validate', methods=['POST'])
def validate_rule():
    """Validate a single rule"""
    try:
        rule_data = request.json
        
        # Basic validation
        errors = []
        warnings = []
        
        if not rule_data.get('name'):
            errors.append("Rule name is required")
        if not rule_data.get('device'):
            errors.append("Device type is required")
        if not rule_data.get('parameter'):
            errors.append("Parameter is required")
        if not rule_data.get('type'):
            errors.append("Rule type is required")
        if not rule_data.get('severity'):
            errors.append("Severity is required")
        
        # Validate constraint
        constraint = rule_data.get('constraint', {})
        if not any([constraint.get('vhigh'), constraint.get('vlow'),
                   constraint.get('ihigh'), constraint.get('ilow')]):
            errors.append("At least one constraint value is required")
        
        return jsonify({
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        })
    
    except Exception as e:
        return jsonify({
            'valid': False,
            'errors': [str(e)],
            'warnings': []
        }), 400


@app.route('/api/generate-yaml', methods=['POST'])
def generate_yaml():
    """Generate YAML from rule data"""
    try:
        rules_data = request.json
        
        # Create YAML structure
        yaml_data = {
            'version': '1.0',
            'process': rules_data.get('process', 'CUSTOM'),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'global': {
                'timing': {
                    'tmin': 0,
                    'tdelay': 0,
                    'vballmsg': 1.0,
                    'stop': 0
                },
                'temperature': {
                    'tcelsius0': 273.15,
                    'tref_soa': 25
                },
                'tmaxfrac': {
                    'level0': 0,
                    'level1': 0.01,
                    'level2': 0.10,
                    'level3': -1
                },
                'limits': {
                    'ap_fwd_ref': 0.9943,
                    'ap_fwd_T': -0.0006,
                    'ap_no_check': 999.00,
                    'ap_gc_lv': 1.65,
                    'ap_gc_hv': 5.5
                }
            },
            'rules': rules_data.get('rules', [])
        }
        
        # Convert to YAML
        yaml_str = yaml.dump(yaml_data, default_flow_style=False, sort_keys=False)
        
        return jsonify({
            'yaml': yaml_str,
            'success': True
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/download-yaml', methods=['POST'])
def download_yaml():
    """Download YAML file"""
    try:
        yaml_content = request.json.get('yaml', '')
        
        # Create file in memory
        buffer = BytesIO()
        buffer.write(yaml_content.encode('utf-8'))
        buffer.seek(0)
        
        return send_file(
            buffer,
            mimetype='text/yaml',
            as_attachment=True,
            download_name='soa_rules.yaml'
        )
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/validate-yaml', methods=['POST'])
def validate_yaml():
    """Validate complete YAML document"""
    try:
        yaml_content = request.json.get('yaml', '')
        
        # Parse YAML
        parser = SOAParser()
        doc = parser.parse_string(yaml_content)
        
        # Validate
        validator = SOAValidator(strict=False)
        is_valid = validator.validate(doc)
        
        errors = [str(e) for e in validator.get_errors()]
        warnings = [str(w) for w in validator.get_warnings()]
        
        return jsonify({
            'valid': is_valid,
            'errors': errors,
            'warnings': warnings,
            'rule_count': len(doc.rules)
        })
    
    except Exception as e:
        return jsonify({
            'valid': False,
            'errors': [str(e)],
            'warnings': []
        }), 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
