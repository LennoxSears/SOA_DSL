// SOA Rule Creator - JavaScript
// Loads device and monitor libraries, generates universal YAML

// State
let deviceLibrary = null;
let monitorLibrary = null;
let rules = [];

// DOM Elements
const loading = document.getElementById('loading');
const mainContent = document.getElementById('mainContent');
const ruleForm = document.getElementById('ruleForm');
const checkTypeSelect = document.getElementById('checkType');
const checkTypeHelp = document.getElementById('checkTypeHelp');
const deviceMethodRadios = document.getElementsByName('deviceMethod');
const directSubcircuits = document.getElementById('directSubcircuits');
const level1Groups = document.getElementById('level1Groups');
const level2Groups = document.getElementById('level2Groups');
const subcircuitList = document.getElementById('subcircuitList');
const level1GroupSelect = document.getElementById('level1GroupSelect');
const level2GroupSelect = document.getElementById('level2GroupSelect');
const selectedDevicesDisplay = document.getElementById('selectedDevicesDisplay');
const checkConfigContent = document.getElementById('checkConfigContent');
const limitsConfig = document.getElementById('limitsConfig');
const yamlPreview = document.getElementById('yamlPreview');
const ruleListPanel = document.getElementById('ruleListPanel');
const ruleList = document.getElementById('ruleList');
const ruleCount = document.getElementById('ruleCount');

// Load libraries on page load
window.addEventListener('DOMContentLoaded', async () => {
    try {
        await loadLibraries();
        initializeForm();
        loading.style.display = 'none';
        mainContent.style.display = 'grid';
    } catch (error) {
        loading.innerHTML = `<p style="color: red;">Error loading libraries: ${error.message}</p>`;
    }
});

// Load device and monitor libraries
async function loadLibraries() {
    try {
        // Load device library
        const deviceResponse = await fetch('../config/device_library.yaml');
        const deviceYaml = await deviceResponse.text();
        deviceLibrary = jsyaml.load(deviceYaml);
        
        // Load monitor library
        const monitorResponse = await fetch('../config/monitor_library.yaml');
        const monitorYaml = await monitorResponse.text();
        monitorLibrary = jsyaml.load(monitorYaml);
        
        console.log('Libraries loaded successfully');
    } catch (error) {
        throw new Error(`Failed to load libraries: ${error.message}`);
    }
}

// Initialize form with library data
function initializeForm() {
    populateCheckTypes();
    populateSubcircuits();
    populateGroups();
    setupEventListeners();
}

// Populate check types from monitor library
function populateCheckTypes() {
    const monitors = monitorLibrary.monitors;
    
    for (const [monitorType, config] of Object.entries(monitors)) {
        const option = document.createElement('option');
        option.value = monitorType;
        option.textContent = `${monitorType} - ${config.description}`;
        option.dataset.capabilities = JSON.stringify(config.capabilities);
        checkTypeSelect.appendChild(option);
    }
}

// Populate subcircuits list
function populateSubcircuits() {
    const subcircuits = deviceLibrary.subcircuits;
    
    // Group by type
    const grouped = {};
    for (const [name, info] of Object.entries(subcircuits)) {
        const type = info.type;
        if (!grouped[type]) grouped[type] = [];
        grouped[type].push({ name, info });
    }
    
    // Create checkboxes grouped by type
    for (const [type, items] of Object.entries(grouped)) {
        const groupDiv = document.createElement('div');
        groupDiv.className = 'checkbox-group';
        
        const groupLabel = document.createElement('div');
        groupLabel.className = 'group-label';
        groupLabel.textContent = type.toUpperCase();
        groupDiv.appendChild(groupLabel);
        
        items.forEach(({ name, info }) => {
            const label = document.createElement('label');
            label.className = 'checkbox-label';
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.value = name;
            checkbox.dataset.nodes = JSON.stringify(info.nodes);
            checkbox.dataset.parameters = JSON.stringify(info.parameters);
            
            const span = document.createElement('span');
            span.textContent = `${name} - ${info.description}`;
            
            label.appendChild(checkbox);
            label.appendChild(span);
            groupDiv.appendChild(label);
        });
        
        subcircuitList.appendChild(groupDiv);
    }
}

// Populate group selects
function populateGroups() {
    // Level 1 groups
    const level1 = deviceLibrary.level1_groups;
    for (const [name, info] of Object.entries(level1)) {
        const option = document.createElement('option');
        option.value = name;
        option.textContent = `${name} - ${info.description}`;
        option.dataset.subcircuits = JSON.stringify(info.subcircuits);
        level1GroupSelect.appendChild(option);
    }
    
    // Level 2 groups
    const level2 = deviceLibrary.level2_groups;
    for (const [name, info] of Object.entries(level2)) {
        const option = document.createElement('option');
        option.value = name;
        option.textContent = `${name} - ${info.description}`;
        option.dataset.level1Groups = JSON.stringify(info.level1_groups);
        level2GroupSelect.appendChild(option);
    }
}

// Setup event listeners
function setupEventListeners() {
    checkTypeSelect.addEventListener('change', onCheckTypeChange);
    
    deviceMethodRadios.forEach(radio => {
        radio.addEventListener('change', onDeviceMethodChange);
    });
    
    subcircuitList.addEventListener('change', updateSelectedDevices);
    level1GroupSelect.addEventListener('change', updateSelectedDevices);
    level2GroupSelect.addEventListener('change', updateSelectedDevices);
    
    ruleForm.addEventListener('submit', handleSubmit);
    document.getElementById('clearForm').addEventListener('click', clearForm);
    document.getElementById('copyYaml').addEventListener('click', copyYaml);
    document.getElementById('downloadYaml').addEventListener('click', downloadYaml);
}

// Handle check type change
function onCheckTypeChange() {
    const monitorType = checkTypeSelect.value;
    if (!monitorType) return;
    
    const config = monitorLibrary.monitors[monitorType];
    checkTypeHelp.textContent = config.description;
    
    // Update check config based on type
    updateCheckConfig(monitorType, config);
    updateLimitsConfig(monitorType, config);
}

// Update check configuration UI
function updateCheckConfig(monitorType, config) {
    checkConfigContent.innerHTML = '';
    
    // Voltage check (ovcheck, ovcheck6)
    if (config.capabilities.includes('voltage_check')) {
        if (config.capabilities.includes('multi_branch')) {
            // Multi-branch voltage check
            checkConfigContent.innerHTML = `
                <div class="form-group">
                    <label>Number of Branches</label>
                    <select id="numBranches" onchange="updateBranchFields()">
                        <option value="1">1 Branch</option>
                        <option value="2">2 Branches</option>
                        <option value="3" selected>3 Branches</option>
                        <option value="4">4 Branches</option>
                        <option value="5">5 Branches</option>
                        <option value="6">6 Branches</option>
                    </select>
                </div>
                <div id="branchFields"></div>
            `;
            setTimeout(() => updateBranchFields(), 0);
        } else {
            // Single branch voltage check
            checkConfigContent.innerHTML = `
                <div class="form-group">
                    <label for="signalMeasure">Signal to Measure *</label>
                    <input type="text" id="signalMeasure" placeholder="e.g., V(g,s)" required>
                    <small>Example: V(g,s), V(d,s), V(t,nw)</small>
                </div>
                <div class="form-group">
                    <label for="signalMessage">Message</label>
                    <input type="text" id="signalMessage" placeholder="e.g., Vgs_OXrisk">
                </div>
            `;
        }
    }
    // State-dependent check (ovcheckva_mos2)
    else if (config.capabilities.includes('state_dependent')) {
        checkConfigContent.innerHTML = `
            <div class="form-group">
                <label for="signalMeasure">Signal to Measure *</label>
                <input type="text" id="signalMeasure" placeholder="e.g., V(d,s)" required>
                <small>Typically drain-source voltage V(d,s)</small>
            </div>
            <div class="form-group">
                <label for="stateParameter">State Detection Parameter *</label>
                <input type="text" id="stateParameter" value="vth" required>
                <small>Parameter used to detect transistor state (usually vth)</small>
            </div>
            <div class="form-group">
                <label for="stateThreshold">State Threshold</label>
                <input type="number" id="stateThreshold" value="0.0" step="any">
                <small>Threshold for state detection (usually 0.0)</small>
            </div>
        `;
    }
    // Temperature-dependent check (ovcheckva_pwl)
    else if (config.capabilities.includes('temperature_dependent')) {
        checkConfigContent.innerHTML = `
            <div class="form-group">
                <label for="signalMeasure">Signal to Measure *</label>
                <input type="text" id="signalMeasure" placeholder="e.g., V(p,n)" required>
                <small>Typically diode voltage V(p,n)</small>
            </div>
            <div class="form-group">
                <label for="signalMessage">Message</label>
                <input type="text" id="signalMessage" placeholder="e.g., Vpn_temp">
            </div>
            <div class="form-group">
                <label for="refTemp">Reference Temperature (°C)</label>
                <input type="number" id="refTemp" value="25" step="any">
            </div>
            <div class="form-group">
                <label for="refValue">Reference Value</label>
                <input type="number" id="refValue" placeholder="e.g., 0.9943" step="any">
            </div>
            <div class="form-group">
                <label for="tempCoeff">Temperature Coefficient</label>
                <input type="number" id="tempCoeff" placeholder="e.g., -0.0006" step="any">
                <small>Generates: refValue + tempCoeff * (T - refTemp)</small>
            </div>
        `;
    }
    // Parameter check (parcheckva3)
    else if (config.capabilities.includes('parameter_check')) {
        checkConfigContent.innerHTML = `
            <div class="form-group">
                <label for="parameterName">Parameter Name *</label>
                <input type="text" id="parameterName" placeholder="e.g., vth" required>
                <small>Device parameter to check (e.g., vth, w, l)</small>
            </div>
            <div class="form-group">
                <label for="gateThreshold">Gate Threshold</label>
                <input type="number" id="gateThreshold" value="0.0" step="any">
            </div>
        `;
    }
    // Aging check (ovcheckva_ldmos_hci_tddb)
    else if (config.capabilities.includes('aging_check')) {
        checkConfigContent.innerHTML = `
            <div class="form-group">
                <label>Aging Mechanism</label>
                <select id="agingMechanism">
                    <option value="hci_tddb">HCI/TDDB (Hot Carrier Injection / Time-Dependent Dielectric Breakdown)</option>
                </select>
            </div>
            <div class="form-group">
                <label for="agingCoeffA">Coefficient A</label>
                <input type="number" id="agingCoeffA" placeholder="e.g., 24" step="any">
            </div>
            <div class="form-group">
                <label for="agingCoeffB">Coefficient B</label>
                <input type="number" id="agingCoeffB" placeholder="e.g., 0.38" step="any">
            </div>
            <small>Additional coefficients (c-n) can be added if needed</small>
        `;
    }
    // Self-heating check
    else if (config.capabilities.includes('self_heating')) {
        checkConfigContent.innerHTML = `
            <div class="form-group">
                <label for="maxTempRise">Max Temperature Rise (°C)</label>
                <input type="number" id="maxTempRise" value="5" step="any">
            </div>
            <div class="form-group">
                <label for="thermalTimeConst">Thermal Time Constant (s)</label>
                <input type="number" id="thermalTimeConst" value="1e-7" step="any">
            </div>
            <div class="form-group">
                <label for="dcCurrentMax">DC Current Max (expression)</label>
                <input type="text" id="dcCurrentMax" placeholder="e.g., $w * 4.05e-3">
                <small>Use $w, $l for device parameters</small>
            </div>
        `;
    }
}

// Update branch fields for multi-branch checks
function updateBranchFields() {
    const numBranches = parseInt(document.getElementById('numBranches').value);
    const branchFields = document.getElementById('branchFields');
    
    let html = '';
    for (let i = 1; i <= numBranches; i++) {
        html += `
            <div class="branch-group">
                <h4>Branch ${i}</h4>
                <div class="form-row">
                    <div class="form-group">
                        <label for="branch${i}Signal">Signal *</label>
                        <input type="text" id="branch${i}Signal" placeholder="e.g., V(g,${i === 1 ? 'b' : i === 2 ? 's' : 'd'})" required>
                    </div>
                    <div class="form-group">
                        <label for="branch${i}Message">Message</label>
                        <input type="text" id="branch${i}Message" placeholder="e.g., Vg${i === 1 ? 'b' : i === 2 ? 's' : 'd'}_OXrisk">
                    </div>
                </div>
            </div>
        `;
    }
    branchFields.innerHTML = html;
}

// Update limits configuration UI
function updateLimitsConfig(monitorType, config) {
    limitsConfig.innerHTML = '';
    
    // Voltage/Current checks - simple min/max
    if (config.capabilities.includes('voltage_check') || config.capabilities.includes('current_check')) {
        if (!config.capabilities.includes('state_dependent') && !config.capabilities.includes('temperature_dependent')) {
            limitsConfig.innerHTML = `
                <div class="form-row">
                    <div class="form-group">
                        <label for="limitMin">Minimum</label>
                        <input type="number" id="limitMin" step="any" placeholder="e.g., -1.32">
                    </div>
                    <div class="form-group">
                        <label for="limitMax">Maximum *</label>
                        <input type="number" id="limitMax" step="any" placeholder="e.g., 1.32" required>
                    </div>
                </div>
            `;
        }
    }
    
    // State-dependent checks
    if (config.capabilities.includes('state_dependent')) {
        limitsConfig.innerHTML = `
            <div class="form-group">
                <label for="limitOnMax">Maximum (ON state) *</label>
                <input type="number" id="limitOnMax" step="any" placeholder="e.g., 1.84" required>
                <small>Voltage limit when transistor is ON (Vgs > Vth)</small>
            </div>
            <div class="form-group">
                <label for="limitOffMax">Maximum (OFF state) *</label>
                <input type="number" id="limitOffMax" step="any" placeholder="e.g., 3.0" required>
                <small>Voltage limit when transistor is OFF (Vgs < Vth)</small>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label for="limitGateMax">Gate Control Max</label>
                    <input type="number" id="limitGateMax" step="any" placeholder="e.g., 2.07">
                </div>
                <div class="form-group">
                    <label for="limitGateMin">Gate Control Min</label>
                    <input type="number" id="limitGateMin" step="any" placeholder="e.g., -2.07">
                </div>
            </div>
        `;
    }
    
    // Temperature-dependent checks (limits already in check config)
    if (config.capabilities.includes('temperature_dependent')) {
        limitsConfig.innerHTML = `
            <p><em>Limits are temperature-dependent (configured above)</em></p>
        `;
    }
    
    // Parameter checks
    if (config.capabilities.includes('parameter_check')) {
        limitsConfig.innerHTML = `
            <div class="form-row">
                <div class="form-group">
                    <label for="paramMin">Minimum *</label>
                    <input type="number" id="paramMin" step="any" placeholder="e.g., 0.3" required>
                </div>
                <div class="form-group">
                    <label for="paramMax">Maximum *</label>
                    <input type="number" id="paramMax" step="any" placeholder="e.g., 0.7" required>
                </div>
            </div>
        `;
    }
    
    // Aging checks (no limits, uses coefficients)
    if (config.capabilities.includes('aging_check')) {
        limitsConfig.innerHTML = `
            <p><em>Aging limits are determined by coefficients (configured above)</em></p>
        `;
    }
    
    // Self-heating checks (no limits, uses current expressions)
    if (config.capabilities.includes('self_heating')) {
        limitsConfig.innerHTML = `
            <p><em>Current limits are configured above</em></p>
        `;
    }
}

// Handle device method change
function onDeviceMethodChange() {
    const method = document.querySelector('input[name="deviceMethod"]:checked').value;
    
    directSubcircuits.style.display = method === 'direct' ? 'block' : 'none';
    level1Groups.style.display = method === 'level1' ? 'block' : 'none';
    level2Groups.style.display = method === 'level2' ? 'block' : 'none';
    
    updateSelectedDevices();
}

// Update selected devices display
function updateSelectedDevices() {
    const method = document.querySelector('input[name="deviceMethod"]:checked').value;
    let selected = [];
    
    if (method === 'direct') {
        const checkboxes = subcircuitList.querySelectorAll('input[type="checkbox"]:checked');
        selected = Array.from(checkboxes).map(cb => cb.value);
    } else if (method === 'level1') {
        const groupName = level1GroupSelect.value;
        if (groupName) {
            const option = level1GroupSelect.selectedOptions[0];
            selected = JSON.parse(option.dataset.subcircuits);
        }
    } else if (method === 'level2') {
        const groupName = level2GroupSelect.value;
        if (groupName) {
            const option = level2GroupSelect.selectedOptions[0];
            const level1Groups = JSON.parse(option.dataset.level1Groups);
            // Expand level1 groups to subcircuits
            level1Groups.forEach(l1 => {
                const l1Data = deviceLibrary.level1_groups[l1];
                if (l1Data) selected.push(...l1Data.subcircuits);
            });
        }
    }
    
    selectedDevicesDisplay.textContent = selected.length > 0 ? selected.join(', ') : 'None';
}

// Handle form submission
function handleSubmit(e) {
    e.preventDefault();
    
    const method = document.querySelector('input[name="deviceMethod"]:checked').value;
    const checkType = checkTypeSelect.value;
    
    // Build rule object
    const rule = {
        name: document.getElementById('ruleName').value,
        description: document.getElementById('ruleDescription').value,
        applies_to: {},
        check: {
            type: mapCheckType(checkType)
        },
        limits: {}
    };
    
    // Add device selection
    if (method === 'direct') {
        const checkboxes = subcircuitList.querySelectorAll('input[type="checkbox"]:checked');
        rule.applies_to.subcircuits = Array.from(checkboxes).map(cb => cb.value);
    } else if (method === 'level1') {
        rule.applies_to.level1_group = level1GroupSelect.value;
    } else if (method === 'level2') {
        rule.applies_to.level2_group = level2GroupSelect.value;
    }
    
    // Add check configuration
    const signalMeasure = document.getElementById('signalMeasure');
    if (signalMeasure) {
        rule.check.measure = signalMeasure.value;
    }
    
    const signalMessage = document.getElementById('signalMessage');
    if (signalMessage && signalMessage.value) {
        rule.message = signalMessage.value;
    }
    
    // Add limits
    const timeLimit = document.getElementById('timeLimit').value;
    rule.limits.time_limit = timeLimit;
    
    const limitMin = document.getElementById('limitMin');
    const limitMax = document.getElementById('limitMax');
    if (limitMin || limitMax) {
        rule.limits.steady = {};
        if (limitMin && limitMin.value) rule.limits.steady.min = parseFloat(limitMin.value);
        if (limitMax && limitMax.value) rule.limits.steady.max = parseFloat(limitMax.value);
    }
    
    // Add rule to list
    rules.push(rule);
    updateRuleList();
    updateYamlPreview();
    clearForm();
    
    alert('Rule added successfully!');
}

// Map check type to universal type
function mapCheckType(monitorType) {
    const config = monitorLibrary.monitors[monitorType];
    if (config.capabilities.includes('voltage_check')) return 'voltage';
    if (config.capabilities.includes('current_check')) return 'current';
    if (config.capabilities.includes('parameter_check')) return 'parameter';
    if (config.capabilities.includes('aging_check')) return 'aging';
    return 'voltage';
}

// Clear form
function clearForm() {
    ruleForm.reset();
    checkConfigContent.innerHTML = '';
    limitsConfig.innerHTML = '';
    checkTypeHelp.textContent = '';
}

// Update rule list
function updateRuleList() {
    ruleCount.textContent = rules.length;
    
    if (rules.length === 0) {
        ruleList.innerHTML = '<p class="empty-state">No rules added yet. Use the form above to create rules.</p>';
        ruleListPanel.style.display = 'none';
        return;
    }
    
    ruleListPanel.style.display = 'block';
    ruleList.innerHTML = rules.map((rule, index) => `
        <div class="rule-item">
            <div class="rule-header">
                <h4>${rule.name}</h4>
                <button class="btn btn-small btn-danger" onclick="removeRule(${index})">Remove</button>
            </div>
            <div class="rule-details">
                <span class="badge">${rule.check.type}</span>
                <span class="detail">Devices: ${getDeviceDisplay(rule.applies_to)}</span>
            </div>
        </div>
    `).join('');
}

// Get device display text
function getDeviceDisplay(appliesTo) {
    if (appliesTo.subcircuits) return appliesTo.subcircuits.join(', ');
    if (appliesTo.level1_group) return `Level1: ${appliesTo.level1_group}`;
    if (appliesTo.level2_group) return `Level2: ${appliesTo.level2_group}`;
    return 'Unknown';
}

// Remove rule
function removeRule(index) {
    rules.splice(index, 1);
    updateRuleList();
    updateYamlPreview();
}

// Update YAML preview
function updateYamlPreview() {
    const doc = {
        version: "1.0",
        process: "SMOS10HV",
        date: new Date().toISOString().split('T')[0],
        globals: {
            timing: {
                tmin: 0,
                tdelay: 0,
                vballmsg: 1.0,
                stop: 0
            },
            time_limits: {
                steady: 0,
                transient_1pct: 0.01,
                transient_10pct: 0.10,
                review: -1
            }
        },
        rules: rules
    };
    
    yamlPreview.textContent = jsyaml.dump(doc, { indent: 2, lineWidth: -1 });
}

// Copy YAML to clipboard
function copyYaml() {
    const yaml = yamlPreview.textContent;
    navigator.clipboard.writeText(yaml).then(() => {
        alert('YAML copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy:', err);
        alert('Failed to copy YAML');
    });
}

// Download YAML file
function downloadYaml() {
    const yaml = yamlPreview.textContent;
    const blob = new Blob([yaml], { type: 'text/yaml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `soa_rules_${new Date().toISOString().split('T')[0]}.yaml`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
