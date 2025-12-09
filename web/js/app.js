/**
 * SOA Rule Creator - Advanced Application Logic
 * Supports all rule types including complex multi-level, state-dependent, etc.
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
    "state_dependent", "multi_branch", "current_with_heating",
    "idc", "ipeak", "irms"
];

const SEVERITIES = ["high", "medium", "low", "review"];

// Global state
let rules = [];
let currentYAML = '';
let tmaxfracLevels = [];
let branches = [];
let voltBranches = [];
let currentConstraints = [];

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    populateDropdowns();
    setupEventListeners();
    updateRulesList();
});

function setupEventListeners() {
    document.getElementById('ruleForm').addEventListener('submit', handleAddRule);
    document.getElementById('clearFormBtn').addEventListener('click', clearForm);
    document.getElementById('validateBtn').addEventListener('click', validateYAML);
    document.getElementById('downloadBtn').addEventListener('click', downloadYAML);
    document.getElementById('ruleType').addEventListener('change', handleRuleTypeChange);
    
    // Tab switching
    document.querySelector('.tabs').addEventListener('click', function(e) {
        if (e.target.classList.contains('tab-btn') || e.target.closest('.tab-btn')) {
            const btn = e.target.classList.contains('tab-btn') ? e.target : e.target.closest('.tab-btn');
            const tabName = btn.dataset.tab;
            if (tabName) showTab(tabName, btn);
        }
    });
    
    // Rule deletion
    document.getElementById('rulesList').addEventListener('click', function(e) {
        if (e.target.classList.contains('delete-btn')) {
            const index = parseInt(e.target.dataset.index);
            if (!isNaN(index)) deleteRule(index);
        }
    });
    
    // Dynamic list buttons (will be added dynamically)
    if (document.getElementById('addTmaxfracBtn')) {
        document.getElementById('addTmaxfracBtn').addEventListener('click', addTmaxfracLevel);
    }
    if (document.getElementById('addBranchBtn')) {
        document.getElementById('addBranchBtn').addEventListener('click', addBranch);
    }
    if (document.getElementById('addVoltBranchBtn')) {
        document.getElementById('addVoltBranchBtn').addEventListener('click', addVoltBranch);
    }
    if (document.getElementById('addCurrentConstraintBtn')) {
        document.getElementById('addCurrentConstraintBtn').addEventListener('click', addCurrentConstraint);
    }
}

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

// Handle rule type change - show/hide relevant sections
function handleRuleTypeChange() {
    const ruleType = document.getElementById('ruleType').value;
    
    // Hide all optional sections
    document.getElementById('simpleConstraintsSection').classList.add('hidden');
    document.getElementById('tmaxfracSection').classList.add('hidden');
    document.getElementById('stateDependentSection').classList.add('hidden');
    document.getElementById('multiBranchSection').classList.add('hidden');
    document.getElementById('currentHeatingSection').classList.add('hidden');
    document.getElementById('agingCheckSection').classList.add('hidden');
    document.getElementById('branchesSection').classList.add('hidden');
    
    // Show relevant sections based on rule type
    if (['vhigh', 'vlow', 'ihigh', 'ilow', 'range'].includes(ruleType)) {
        document.getElementById('simpleConstraintsSection').classList.remove('hidden');
    } else if (ruleType === 'state_dependent') {
        document.getElementById('stateDependentSection').classList.remove('hidden');
    } else if (ruleType === 'multi_branch') {
        document.getElementById('multiBranchSection').classList.remove('hidden');
    } else if (ruleType === 'current_with_heating') {
        document.getElementById('currentHeatingSection').classList.remove('hidden');
    }
}

// Dynamic list management
function addTmaxfracLevel() {
    const container = document.getElementById('tmaxfracList');
    const index = tmaxfracLevels.length;
    const item = document.createElement('div');
    item.className = 'dynamic-item';
    item.innerHTML = `
        <button type="button" class="remove-btn" onclick="removeTmaxfracLevel(${index})">Remove</button>
        <div class="form-row">
            <div class="form-group">
                <label>Level</label>
                <select class="tmaxfrac-level">
                    <option value="0.0">0.0 (Never exceed)</option>
                    <option value="0.01">0.01 (1% of time)</option>
                    <option value="0.1">0.1 (10% of time)</option>
                    <option value="-1">-1 (Always)</option>
                </select>
            </div>
            <div class="form-group">
                <label>Value</label>
                <input type="text" class="tmaxfrac-value" placeholder="e.g., 1.65">
            </div>
        </div>
    `;
    container.appendChild(item);
    tmaxfracLevels.push({level: '0.0', value: ''});
}

function removeTmaxfracLevel(index) {
    tmaxfracLevels.splice(index, 1);
    renderTmaxfracLevels();
}

function renderTmaxfracLevels() {
    const container = document.getElementById('tmaxfracList');
    container.innerHTML = '';
    tmaxfracLevels.forEach((_, index) => addTmaxfracLevel());
}

function addBranch() {
    const container = document.getElementById('branchList');
    const index = branches.length;
    const item = document.createElement('div');
    item.className = 'dynamic-item';
    item.innerHTML = `
        <button type="button" class="remove-btn" onclick="removeBranch(${index})">Remove</button>
        <div class="form-group">
            <label>Branch</label>
            <input type="text" class="branch-name" placeholder='e.g., V(g,b)'>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>V High</label>
                <input type="text" class="branch-vhigh" placeholder="e.g., ap_gc_hv">
            </div>
            <div class="form-group">
                <label>V Low</label>
                <input type="text" class="branch-vlow" placeholder="e.g., -ap_gc_hv">
            </div>
        </div>
    `;
    container.appendChild(item);
    branches.push({branch: '', vhigh: '', vlow: ''});
}

function removeBranch(index) {
    branches.splice(index, 1);
    renderBranches();
}

function renderBranches() {
    const container = document.getElementById('branchList');
    container.innerHTML = '';
    branches.forEach((_, index) => addBranch());
}

function addVoltBranch() {
    const container = document.getElementById('voltBranchList');
    const index = voltBranches.length;
    const item = document.createElement('div');
    item.className = 'dynamic-item';
    item.innerHTML = `
        <button type="button" class="remove-btn" onclick="removeVoltBranch(${index})">Remove</button>
        <div class="form-group">
            <label>Branch</label>
            <input type="text" class="voltbranch-name" placeholder='e.g., V(g,b)'>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>V High</label>
                <input type="text" class="voltbranch-vhigh" placeholder="e.g., 1.65">
            </div>
            <div class="form-group">
                <label>V Low</label>
                <input type="text" class="voltbranch-vlow" placeholder="e.g., -1.65">
            </div>
        </div>
        <div class="form-group">
            <label>Message</label>
            <input type="text" class="voltbranch-message" placeholder="e.g., Vgb_OXrisk">
        </div>
    `;
    container.appendChild(item);
    voltBranches.push({branch: '', vhigh: '', vlow: '', message: ''});
}

function removeVoltBranch(index) {
    voltBranches.splice(index, 1);
    renderVoltBranches();
}

function renderVoltBranches() {
    const container = document.getElementById('voltBranchList');
    container.innerHTML = '';
    voltBranches.forEach((_, index) => addVoltBranch());
}

function addCurrentConstraint() {
    const container = document.getElementById('currentConstraintsList');
    const index = currentConstraints.length;
    const item = document.createElement('div');
    item.className = 'dynamic-item';
    item.innerHTML = `
        <button type="button" class="remove-btn" onclick="removeCurrentConstraint(${index})">Remove</button>
        <div class="form-row">
            <div class="form-group">
                <label>Name</label>
                <input type="text" class="current-name" placeholder="e.g., DC Current">
            </div>
            <div class="form-group">
                <label>Type</label>
                <select class="current-type">
                    <option value="idc">idc (DC)</option>
                    <option value="ipeak">ipeak (Peak)</option>
                    <option value="irms">irms (RMS)</option>
                </select>
            </div>
        </div>
        <div class="form-group">
            <label>I High</label>
            <input type="text" class="current-ihigh" placeholder="e.g., $w * 4.05e-3">
        </div>
    `;
    container.appendChild(item);
    currentConstraints.push({name: '', type: 'idc', ihigh: ''});
}

function removeCurrentConstraint(index) {
    currentConstraints.splice(index, 1);
    renderCurrentConstraints();
}

function renderCurrentConstraints() {
    const container = document.getElementById('currentConstraintsList');
    container.innerHTML = '';
    currentConstraints.forEach((_, index) => addCurrentConstraint());
}

// Handle form submission
function handleAddRule(e) {
    e.preventDefault();
    
    try {
        const ruleType = document.getElementById('ruleType').value;
        const rule = {
            name: document.getElementById('ruleName').value,
            device: document.getElementById('device').value,
            parameter: document.getElementById('parameter').value,
            type: ruleType,
            severity: document.getElementById('severity').value,
            description: document.getElementById('description').value || ''
        };
        
        // Add condition if specified
        const condition = document.getElementById('condition').value;
        if (condition) rule.condition = condition;
        
        // Build constraint based on rule type
        if (['vhigh', 'vlow', 'ihigh', 'ilow', 'range'].includes(ruleType)) {
            rule.constraint = {};
            const vhigh = document.getElementById('vhigh').value;
            const vlow = document.getElementById('vlow').value;
            const ihigh = document.getElementById('ihigh').value;
            const ilow = document.getElementById('ilow').value;
            
            if (vhigh) rule.constraint.vhigh = parseValue(vhigh);
            if (vlow) rule.constraint.vlow = parseValue(vlow);
            if (ihigh) rule.constraint.ihigh = parseValue(ihigh);
            if (ilow) rule.constraint.ilow = parseValue(ilow);
        } else if (ruleType === 'state_dependent') {
            rule.constraint = {};
            const vhigh_on = document.getElementById('vhigh_on').value;
            const vhigh_off = document.getElementById('vhigh_off').value;
            if (vhigh_on) rule.constraint.vhigh_on = parseValue(vhigh_on);
            if (vhigh_off) rule.constraint.vhigh_off = parseValue(vhigh_off);
            
            // Gate control
            const vhigh_gc = document.getElementById('vhigh_gc').value;
            const vlow_gc = document.getElementById('vlow_gc').value;
            if (vhigh_gc || vlow_gc) {
                rule.gate_control = {};
                if (vhigh_gc) rule.gate_control.vhigh_gc = parseValue(vhigh_gc);
                if (vlow_gc) rule.gate_control.vlow_gc = parseValue(vlow_gc);
            }
            
            // Monitor params
            const monitor_param = document.getElementById('monitor_param').value;
            const monitor_vgt = document.getElementById('monitor_vgt').value;
            if (monitor_param || monitor_vgt) {
                rule.monitor_params = {};
                if (monitor_param) rule.monitor_params.param = monitor_param;
                if (monitor_vgt) rule.monitor_params.vgt = parseValue(monitor_vgt);
            }
        } else if (ruleType === 'multi_branch') {
            rule.branches = collectBranches();
            const connections = document.getElementById('connections').value;
            if (connections) rule.connections = connections;
        } else if (ruleType === 'current_with_heating') {
            rule.constraints = collectCurrentConstraints();
            const dtmax = document.getElementById('dtmax').value;
            const theat = document.getElementById('theat').value;
            if (dtmax || theat) {
                rule.self_heating = {};
                if (dtmax) rule.self_heating.dtmax = dtmax;
                if (theat) rule.self_heating.theat = theat;
            }
        }
        
        // Aging check
        const aging_type = document.getElementById('aging_type').value;
        if (aging_type) {
            rule.aging_check = {type: aging_type};
            const aging_variant = document.getElementById('aging_variant').value;
            if (aging_variant) rule.aging_check.variant = aging_variant;
        }
        
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

function collectBranches() {
    const items = document.querySelectorAll('#branchList .dynamic-item');
    const result = [];
    items.forEach(item => {
        const branch = item.querySelector('.branch-name').value;
        const vhigh = item.querySelector('.branch-vhigh').value;
        const vlow = item.querySelector('.branch-vlow').value;
        if (branch) {
            const b = {branch};
            if (vhigh) b.vhigh = parseValue(vhigh);
            if (vlow) b.vlow = parseValue(vlow);
            result.push(b);
        }
    });
    return result;
}

function collectCurrentConstraints() {
    const items = document.querySelectorAll('#currentConstraintsList .dynamic-item');
    const result = [];
    items.forEach(item => {
        const name = item.querySelector('.current-name').value;
        const type = item.querySelector('.current-type').value;
        const ihigh = item.querySelector('.current-ihigh').value;
        if (name && ihigh) {
            result.push({
                name,
                type,
                ihigh: parseValue(ihigh)
            });
        }
    });
    return result;
}

function validateRule(rule) {
    const errors = [];
    
    if (!rule.name) errors.push("Rule name is required");
    if (!rule.device) errors.push("Device name is required");
    if (!rule.parameter) errors.push("Parameter is required");
    if (!rule.type) errors.push("Rule type is required");
    if (!rule.severity) errors.push("Severity is required");
    
    // Type-specific validation
    if (['vhigh', 'vlow', 'ihigh', 'ilow', 'range'].includes(rule.type)) {
        if (!rule.constraint || Object.keys(rule.constraint).length === 0) {
            errors.push("At least one constraint value is required");
        }
    }
    
    return {
        valid: errors.length === 0,
        errors: errors
    };
}

function parseValue(value) {
    const trimmed = value.trim();
    const num = parseFloat(trimmed);
    return isNaN(num) ? trimmed : num;
}

// Continue in next message due to length...

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

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

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

function escapeYamlString(str) {
    if (typeof str !== 'string') return str;
    
    const needsEscaping = str.includes('"') || str.includes('\\') || 
                         str.includes('\n') || str.includes('\r') ||
                         str.includes('\t') || str.startsWith(' ') || 
                         str.endsWith(' ');
    
    if (needsEscaping) {
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

function generateYAML(process, rules) {
    if (rules.length === 0) return 'No rules to preview';

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
            
            // Simple constraints
            if (rule.constraint) {
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
                if (rule.constraint.vhigh_on !== undefined) {
                    yaml += `      vhigh_on: ${formatValue(rule.constraint.vhigh_on)}\n`;
                }
                if (rule.constraint.vhigh_off !== undefined) {
                    yaml += `      vhigh_off: ${formatValue(rule.constraint.vhigh_off)}\n`;
                }
            }
            
            // Gate control
            if (rule.gate_control) {
                yaml += `    gate_control:\n`;
                if (rule.gate_control.vhigh_gc !== undefined) {
                    yaml += `      vhigh_gc: ${formatValue(rule.gate_control.vhigh_gc)}\n`;
                }
                if (rule.gate_control.vlow_gc !== undefined) {
                    yaml += `      vlow_gc: ${formatValue(rule.gate_control.vlow_gc)}\n`;
                }
            }
            
            // Monitor params
            if (rule.monitor_params) {
                yaml += `    monitor_params:\n`;
                if (rule.monitor_params.param) {
                    yaml += `      param: ${escapeYamlString(rule.monitor_params.param)}\n`;
                }
                if (rule.monitor_params.vgt !== undefined) {
                    yaml += `      vgt: ${formatValue(rule.monitor_params.vgt)}\n`;
                }
            }
            
            // Branches (multi-branch)
            if (rule.branches && rule.branches.length > 0) {
                yaml += `    branches:\n`;
                rule.branches.forEach(branch => {
                    yaml += `      - branch: ${escapeYamlString(branch.branch)}\n`;
                    if (branch.vhigh !== undefined) {
                        yaml += `        vhigh: ${formatValue(branch.vhigh)}\n`;
                    }
                    if (branch.vlow !== undefined) {
                        yaml += `        vlow: ${formatValue(branch.vlow)}\n`;
                    }
                    if (branch.message) {
                        yaml += `        message: ${escapeYamlString(branch.message)}\n`;
                    }
                });
            }
            
            // Connections
            if (rule.connections) {
                yaml += `    connections: ${escapeYamlString(rule.connections)}\n`;
            }
            
            // Constraints (current_with_heating)
            if (rule.constraints && rule.constraints.length > 0) {
                yaml += `    constraints:\n`;
                rule.constraints.forEach(constraint => {
                    yaml += `      - name: ${escapeYamlString(constraint.name)}\n`;
                    yaml += `        type: ${constraint.type}\n`;
                    if (constraint.ihigh !== undefined) {
                        yaml += `        ihigh: ${formatValue(constraint.ihigh)}\n`;
                    }
                });
            }
            
            // Self heating
            if (rule.self_heating) {
                yaml += `    self_heating:\n`;
                if (rule.self_heating.dtmax) {
                    yaml += `      dtmax: ${escapeYamlString(rule.self_heating.dtmax)}\n`;
                }
                if (rule.self_heating.theat) {
                    yaml += `      theat: ${escapeYamlString(rule.self_heating.theat)}\n`;
                }
            }
            
            // Aging check
            if (rule.aging_check) {
                yaml += `    aging_check:\n`;
                yaml += `      type: ${rule.aging_check.type}\n`;
                if (rule.aging_check.variant) {
                    yaml += `      variant: ${escapeYamlString(rule.aging_check.variant)}\n`;
                }
            }
            
            // Condition
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

function formatValue(value) {
    if (typeof value === 'number') return value;
    return escapeYamlString(value);
}

function validateYAML() {
    try {
        if (!currentYAML || currentYAML === 'No rules to preview') {
            showNotification('No YAML to validate', 'error');
            return;
        }
        
        const resultDiv = document.getElementById('validationResult');
        const errors = [];
        
        if (rules.length === 0) errors.push('No rules defined');
        
        rules.forEach((rule, index) => {
            if (!rule.name) errors.push(`Rule ${index + 1}: Missing name`);
            if (!rule.device) errors.push(`Rule ${index + 1}: Missing device`);
            if (!rule.parameter) errors.push(`Rule ${index + 1}: Missing parameter`);
            if (!rule.type) errors.push(`Rule ${index + 1}: Missing type`);
            if (!rule.severity) errors.push(`Rule ${index + 1}: Missing severity`);
        });
        
        if (errors.length === 0) {
            resultDiv.className = 'validation-result success';
            resultDiv.innerHTML = `
                <h4>✅ Validation Passed</h4>
                <p>Successfully validated ${rules.length} rule(s)</p>
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

function clearForm() {
    document.getElementById('ruleForm').reset();
    tmaxfracLevels = [];
    branches = [];
    voltBranches = [];
    currentConstraints = [];
    document.getElementById('tmaxfracList').innerHTML = '';
    document.getElementById('branchList').innerHTML = '';
    document.getElementById('voltBranchList').innerHTML = '';
    document.getElementById('currentConstraintsList').innerHTML = '';
}

function showTab(tabName, clickedButton) {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    if (clickedButton) {
        clickedButton.classList.add('active');
    }
    
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

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}
