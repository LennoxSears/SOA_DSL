/**
 * SOA Rule Creator - Application Logic
 * Pure frontend JavaScript for creating SOA rules
 */

// Constants
const DEVICE_TYPES = [
    "nmos_core", "pmos_core", "nmos_5v", "pmos_5v",
    "nmos90_10hv", "pmos90_10hv", "nmos90b_10hv", "pmos90b_10hv",
    "nmoshs45_10hv", "pmoshs45_10hv",
    "dz5", "npn_b", "pnp_b",
    "poly_10hv", "rm1_10hv", "rm2_10hv", "rm3_10hv", "rm4_10hv",
    "cap_low", "cap_mid", "cap_high",
    "diode_n", "diode_p",
    "bandgap_ref", "temp_sensor"
];

const RULE_TYPES = [
    "vhigh", "vlow", "ihigh", "ilow", "range",
    "state_dependent", "multi_branch", "current_with_heating"
];

const SEVERITIES = ["high", "medium", "low", "review"];

// Global state
let rules = [];
let currentYAML = '';

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    populateDropdowns();
    document.getElementById('ruleForm').addEventListener('submit', handleAddRule);
    document.getElementById('clearFormBtn').addEventListener('click', clearForm);
    document.getElementById('validateBtn').addEventListener('click', validateYAML);
    document.getElementById('downloadBtn').addEventListener('click', downloadYAML);
    
    // Tab switching with event delegation
    document.querySelector('.tabs').addEventListener('click', function(e) {
        if (e.target.classList.contains('tab-btn') || e.target.closest('.tab-btn')) {
            const btn = e.target.classList.contains('tab-btn') ? e.target : e.target.closest('.tab-btn');
            const tabName = btn.dataset.tab;
            if (tabName) {
                showTab(tabName, btn);
            }
        }
    });
    
    // Rule deletion with event delegation
    document.getElementById('rulesList').addEventListener('click', function(e) {
        if (e.target.classList.contains('delete-btn')) {
            const index = parseInt(e.target.dataset.index);
            if (!isNaN(index)) {
                deleteRule(index);
            }
        }
    });
    
    updateRulesList();
});

// Populate dropdowns
function populateDropdowns() {
    const deviceSelect = document.getElementById('device');
    DEVICE_TYPES.forEach(device => {
        const option = document.createElement('option');
        option.value = device;
        option.textContent = device;
        deviceSelect.appendChild(option);
    });

    const ruleTypeSelect = document.getElementById('ruleType');
    RULE_TYPES.forEach(type => {
        const option = document.createElement('option');
        option.value = type;
        option.textContent = type;
        ruleTypeSelect.appendChild(option);
    });

    const severitySelect = document.getElementById('severity');
    SEVERITIES.forEach(sev => {
        const option = document.createElement('option');
        option.value = sev;
        option.textContent = sev;
        severitySelect.appendChild(option);
    });
}

// Handle form submission
function handleAddRule(e) {
    e.preventDefault();
    
    try {
        const rule = {
            name: document.getElementById('ruleName').value,
            device: document.getElementById('device').value,
            parameter: document.getElementById('parameter').value,
            type: document.getElementById('ruleType').value,
            severity: document.getElementById('severity').value,
            description: document.getElementById('description').value || '',
            constraint: {}
        };
        
        // Add constraints
        const vhigh = document.getElementById('vhigh').value;
        const vlow = document.getElementById('vlow').value;
        const ihigh = document.getElementById('ihigh').value;
        const ilow = document.getElementById('ilow').value;
        
        if (vhigh) rule.constraint.vhigh = parseValue(vhigh);
        if (vlow) rule.constraint.vlow = parseValue(vlow);
        if (ihigh) rule.constraint.ihigh = parseValue(ihigh);
        if (ilow) rule.constraint.ilow = parseValue(ilow);
        
        // Add condition if specified
        const condition = document.getElementById('condition').value;
        if (condition) rule.condition = condition;
        
        // Validate rule
        const validation = validateRule(rule);
        if (validation.valid) {
            rules.push(rule);
            updateRulesList();
            updateYAMLPreview();
            clearForm();
            showNotification('Rule added successfully!', 'success');
        } else {
            showNotification('Validation errors: ' + validation.errors.join(', '), 'error');
        }
    } catch (error) {
        console.error('Error adding rule:', error);
        showNotification('Error adding rule: ' + error.message, 'error');
    }
}

// Validate rule
function validateRule(rule) {
    const errors = [];
    
    if (!rule.name) errors.push("Rule name is required");
    if (!rule.device) errors.push("Device type is required");
    if (!rule.parameter) errors.push("Parameter is required");
    if (!rule.type) errors.push("Rule type is required");
    if (!rule.severity) errors.push("Severity is required");
    
    // Check if at least one constraint is provided
    if (!rule.constraint.vhigh && !rule.constraint.vlow &&
        !rule.constraint.ihigh && !rule.constraint.ilow) {
        errors.push("At least one constraint value is required");
    }
    
    return {
        valid: errors.length === 0,
        errors: errors
    };
}

// Parse value (convert to number if possible)
function parseValue(value) {
    const trimmed = value.trim();
    const num = parseFloat(trimmed);
    return isNaN(num) ? trimmed : num;
}

// Update rules list display
function updateRulesList() {
    try {
        const rulesList = document.getElementById('rulesList');
        const ruleCount = document.getElementById('ruleCount');
        
        ruleCount.textContent = rules.length;
        
        if (rules.length === 0) {
            rulesList.innerHTML = '<p class="empty-state">No rules added yet. Create your first rule!</p>';
            return;
        }
        
        rulesList.innerHTML = rules.map((rule, index) => {
            const details = [];
            details.push(`<div class="rule-detail"><strong>Device:</strong> ${escapeHtml(rule.device)}</div>`);
            details.push(`<div class="rule-detail"><strong>Type:</strong> ${escapeHtml(rule.type)}</div>`);
            details.push(`<div class="rule-detail"><strong>Parameter:</strong> ${escapeHtml(rule.parameter)}</div>`);
            details.push(`<div class="rule-detail"><strong>Severity:</strong> ${escapeHtml(rule.severity)}</div>`);
            
            if (rule.constraint.vhigh !== undefined) {
                details.push(`<div class="rule-detail"><strong>V High:</strong> ${escapeHtml(String(rule.constraint.vhigh))}</div>`);
            }
            if (rule.constraint.vlow !== undefined) {
                details.push(`<div class="rule-detail"><strong>V Low:</strong> ${escapeHtml(String(rule.constraint.vlow))}</div>`);
            }
            if (rule.constraint.ihigh !== undefined) {
                details.push(`<div class="rule-detail"><strong>I High:</strong> ${escapeHtml(String(rule.constraint.ihigh))}</div>`);
            }
            if (rule.constraint.ilow !== undefined) {
                details.push(`<div class="rule-detail"><strong>I Low:</strong> ${escapeHtml(String(rule.constraint.ilow))}</div>`);
            }
            
            return `
                <div class="rule-card">
                    <button class="delete-btn" data-index="${index}">Delete</button>
                    <h4>${escapeHtml(rule.name)}</h4>
                    <div class="rule-details">
                        ${details.join('')}
                    </div>
                    ${rule.description ? `<p class="rule-description">${escapeHtml(rule.description)}</p>` : ''}
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Error updating rules list:', error);
        showNotification('Error displaying rules: ' + error.message, 'error');
    }
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Delete rule
function deleteRule(index) {
    try {
        if (confirm('Are you sure you want to delete this rule?')) {
            rules.splice(index, 1);
            updateRulesList();
            updateYAMLPreview();
            showNotification('Rule deleted', 'success');
        }
    } catch (error) {
        console.error('Error deleting rule:', error);
        showNotification('Error deleting rule: ' + error.message, 'error');
    }
}

// Update YAML preview
function updateYAMLPreview() {
    try {
        const processName = document.getElementById('processName').value || 'CUSTOM';
        currentYAML = generateYAML(processName, rules);
        document.getElementById('yamlPreview').textContent = currentYAML;
    } catch (error) {
        console.error('Error updating YAML preview:', error);
        document.getElementById('yamlPreview').textContent = `Error generating YAML: ${error.message}`;
    }
}

// Escape YAML string
function escapeYamlString(str) {
    if (typeof str !== 'string') {
        return str;
    }
    
    // Check if string needs escaping
    const needsEscaping = str.includes('"') || str.includes('\\') || 
                         str.includes('\n') || str.includes('\r') ||
                         str.includes('\t') || str.startsWith(' ') || 
                         str.endsWith(' ');
    
    if (needsEscaping) {
        // Escape special characters
        const escaped = str
            .replace(/\\/g, '\\\\')
            .replace(/"/g, '\\"')
            .replace(/\n/g, '\\n')
            .replace(/\r/g, '\\r')
            .replace(/\t/g, '\\t');
        return `"${escaped}"`;
    }
    
    return `"${str}"`;
}

// Generate YAML
function generateYAML(process, rules) {
    if (rules.length === 0) {
        return 'No rules to preview';
    }

    try {
        const date = new Date().toISOString().split('T')[0];
        
        let yaml = `version: '1.0'\n`;
        yaml += `process: ${escapeYamlString(process)}\n`;
        yaml += `date: ${date}\n\n`;
        
        yaml += `global:\n`;
        yaml += `  timing:\n`;
        yaml += `    tmin: 0\n`;
        yaml += `    tdelay: 0\n`;
        yaml += `    vballmsg: 1.0\n`;
        yaml += `    stop: 0\n`;
        yaml += `  temperature:\n`;
        yaml += `    tcelsius0: 273.15\n`;
        yaml += `    tref_soa: 25\n`;
        yaml += `  tmaxfrac:\n`;
        yaml += `    level0: 0\n`;
        yaml += `    level1: 0.01\n`;
        yaml += `    level2: 0.10\n`;
        yaml += `    level3: -1\n`;
        yaml += `  limits:\n`;
        yaml += `    ap_fwd_ref: 0.9943\n`;
        yaml += `    ap_fwd_T: -0.0006\n`;
        yaml += `    ap_no_check: 999.00\n`;
        yaml += `    ap_gc_lv: 1.65\n`;
        yaml += `    ap_gc_hv: 5.5\n\n`;
        
        yaml += `rules:\n`;
        rules.forEach(rule => {
            yaml += `  - name: ${escapeYamlString(rule.name)}\n`;
            yaml += `    device: ${rule.device}\n`;
            yaml += `    parameter: ${escapeYamlString(rule.parameter)}\n`;
            yaml += `    type: ${rule.type}\n`;
            yaml += `    severity: ${rule.severity}\n`;
            
            if (rule.description) {
                yaml += `    description: ${escapeYamlString(rule.description)}\n`;
            }
            
            yaml += `    constraint:\n`;
            if (rule.constraint.vhigh !== undefined) {
                yaml += `      vhigh: ${formatValue(rule.constraint.vhigh)}\n`;
            }
            if (rule.constraint.vlow !== undefined) {
                yaml += `      vlow: ${formatValue(rule.constraint.vlow)}\n`;
            }
            if (rule.constraint.ihigh !== undefined) {
                yaml += `      ihigh: ${formatValue(rule.constraint.ihigh)}\n`;
            }
            if (rule.constraint.ilow !== undefined) {
                yaml += `      ilow: ${formatValue(rule.constraint.ilow)}\n`;
            }
            
            if (rule.condition) {
                yaml += `    condition: ${escapeYamlString(rule.condition)}\n`;
            }
        });
        
        return yaml;
    } catch (error) {
        console.error('Error generating YAML:', error);
        return `Error generating YAML: ${error.message}`;
    }
}

// Format value for YAML
function formatValue(value) {
    if (typeof value === 'number') {
        return value;
    }
    // For string expressions, escape them
    return escapeYamlString(value);
}

// Validate YAML
function validateYAML() {
    try {
        if (!currentYAML || currentYAML === 'No rules to preview') {
            showNotification('No YAML to validate', 'error');
            return;
        }
        
        const resultDiv = document.getElementById('validationResult');
        const errors = [];
        const warnings = [];
        
        // Basic validation
        if (rules.length === 0) {
            errors.push('No rules defined');
        }
        
        // Validate each rule
        rules.forEach((rule, index) => {
            if (!rule.name) errors.push(`Rule ${index + 1}: Missing name`);
            if (!rule.device) errors.push(`Rule ${index + 1}: Missing device`);
            if (!rule.parameter) errors.push(`Rule ${index + 1}: Missing parameter`);
            if (!rule.type) errors.push(`Rule ${index + 1}: Missing type`);
            if (!rule.severity) errors.push(`Rule ${index + 1}: Missing severity`);
            
            const hasConstraint = rule.constraint.vhigh !== undefined ||
                                rule.constraint.vlow !== undefined ||
                                rule.constraint.ihigh !== undefined ||
                                rule.constraint.ilow !== undefined;
            
            if (!hasConstraint) {
                errors.push(`Rule ${index + 1}: No constraints defined`);
            }
        });
        
        if (errors.length === 0) {
            resultDiv.className = 'validation-result success';
            resultDiv.innerHTML = `
                <h4>✅ Validation Passed</h4>
                <p>Successfully validated ${rules.length} rule(s)</p>
                ${warnings.length > 0 ? `
                    <p><strong>Warnings:</strong></p>
                    <ul>${warnings.map(w => `<li>${escapeHtml(w)}</li>`).join('')}</ul>
                ` : ''}
            `;
        } else {
            resultDiv.className = 'validation-result error';
            resultDiv.innerHTML = `
                <h4>❌ Validation Failed</h4>
                <p><strong>Errors:</strong></p>
                <ul>${errors.map(e => `<li>${escapeHtml(e)}</li>`).join('')}</ul>
            `;
        }
    } catch (error) {
        console.error('Error validating YAML:', error);
        showNotification('Error validating YAML: ' + error.message, 'error');
    }
}

// Download YAML
function downloadYAML() {
    try {
        if (!currentYAML || currentYAML === 'No rules to preview') {
            showNotification('No YAML to download', 'error');
            return;
        }
        
        const blob = new Blob([currentYAML], {type: 'text/yaml'});
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'soa_rules.yaml';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showNotification('YAML downloaded successfully!', 'success');
    } catch (error) {
        console.error('Error downloading YAML:', error);
        showNotification('Error downloading YAML: ' + error.message, 'error');
    }
}

// Clear form
function clearForm() {
    document.getElementById('ruleForm').reset();
}

// Show tab
function showTab(tabName, clickedButton) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    if (clickedButton) {
        clickedButton.classList.add('active');
    }
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    if (tabName === 'rules') {
        document.getElementById('rulesTab').classList.add('active');
    } else if (tabName === 'yaml') {
        document.getElementById('yamlTab').classList.add('active');
        updateYAMLPreview();
    }
}

// Show notification
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}
