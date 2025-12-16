// SOA Monitor Creator - JavaScript

// State
let monitors = [];
let globalConfig = {
    version: "1.0",
    process: "SMOS10HV",
    date: new Date().toISOString().split('T')[0],
    global: {
        timing: {
            tmin: 0,
            tdelay: 0,
            vballmsg: 1.0,
            stop: 0
        },
        tmaxfrac: {
            level0: 0,
            level1: 0.01,
            level2: 0.10,
            level3: -1
        }
    },
    parameters: {
        global_tmin: 0,
        global_tdelay: 0,
        global_vballmsg: 1.0,
        global_stop: 0,
        tmaxfrac0: 0,
        tmaxfrac1: 0.01,
        tmaxfrac2: 0.10,
        tmaxfrac3: -1
    }
};

// Monitor type configurations
const monitorConfigs = {
    ovcheck: {
        name: "Single Branch Voltage Check",
        params: [
            { id: "vlow", label: "vlow", type: "text", placeholder: "-1.32" },
            { id: "vhigh", label: "vhigh", type: "text", placeholder: "1.32" },
            { id: "branch1", label: "branch1", type: "text", placeholder: 'V(t,nw)' },
            { id: "message1", label: "message1", type: "text", placeholder: "Vtnw_OXrisk" }
        ]
    },
    ovcheck6: {
        name: "Multi-Branch Voltage Check",
        params: [
            { id: "vlow1", label: "vlow1", type: "text", placeholder: "-1.32" },
            { id: "vhigh1", label: "vhigh1", type: "text", placeholder: "1.32" },
            { id: "branch1", label: "branch1", type: "text", placeholder: 'V(g,b)' },
            { id: "message1", label: "message1", type: "text", placeholder: "Vgb_OXrisk" },
            { id: "vlow2", label: "vlow2", type: "text", placeholder: "-1.32" },
            { id: "vhigh2", label: "vhigh2", type: "text", placeholder: "1.32" },
            { id: "branch2", label: "branch2", type: "text", placeholder: 'V(g,s)' },
            { id: "message2", label: "message2", type: "text", placeholder: "Vgs_OXrisk" },
            { id: "vlow3", label: "vlow3", type: "text", placeholder: "-1.32" },
            { id: "vhigh3", label: "vhigh3", type: "text", placeholder: "1.32" },
            { id: "branch3", label: "branch3", type: "text", placeholder: 'V(g,d)' },
            { id: "message3", label: "message3", type: "text", placeholder: "Vgd_OXrisk" }
        ]
    },
    ovcheckva_mos2: {
        name: "MOS State-Dependent Check",
        params: [
            { id: "vhigh_on", label: "vhigh_on", type: "text", placeholder: "1.84" },
            { id: "vhigh_off", label: "vhigh_off", type: "text", placeholder: "3.0" },
            { id: "vhigh_gc", label: "vhigh_gc", type: "text", placeholder: "2.07" },
            { id: "vlow_gc", label: "vlow_gc", type: "text", placeholder: "-2.07" },
            { id: "param", label: "param", type: "text", placeholder: "vth" },
            { id: "vgt", label: "vgt", type: "text", placeholder: "0.0" }
        ]
    },
    ovcheckva_pwl: {
        name: "Piecewise Linear Check",
        params: [
            { id: "vlow", label: "vlow", type: "text", placeholder: '"-ap_fwd_ref - ap_fwd_T * (T - 25)"' },
            { id: "vhigh", label: "vhigh", type: "text", placeholder: '"ap_fwd_ref + ap_fwd_T * (T - 25)"' },
            { id: "branch1", label: "branch1", type: "text", placeholder: 'V(p,n)' },
            { id: "message1", label: "message1", type: "text", placeholder: "Vpn_temp" }
        ]
    },
    ovcheckva_ldmos_hci_tddb: {
        name: "HCI/TDDB Aging Check",
        params: [
            { id: "atype", label: "atype", type: "text", placeholder: "atype" },
            { id: "soa_hcitddb_a", label: "soa_hcitddb_a", type: "text", placeholder: "24" },
            { id: "soa_hcitddb_b", label: "soa_hcitddb_b", type: "text", placeholder: "0.38" }
        ]
    },
    parcheckva3: {
        name: "Parameter Check",
        params: [
            { id: "param", label: "param", type: "text", placeholder: "vth" },
            { id: "vgt", label: "vgt", type: "text", placeholder: "0.0" },
            { id: "vlow", label: "vlow", type: "text", placeholder: "0.3" },
            { id: "vhigh", label: "vhigh", type: "text", placeholder: "0.7" }
        ]
    }
};

// DOM Elements
const monitorForm = document.getElementById('monitorForm');
const monitorTypeSelect = document.getElementById('monitorType');
const specificParamsDiv = document.getElementById('specificParams');
const specificParamsContent = document.getElementById('specificParamsContent');
const yamlPreview = document.getElementById('yamlPreview');
const monitorList = document.getElementById('monitorList');
const monitorCount = document.getElementById('monitorCount');

// Event Listeners
monitorTypeSelect.addEventListener('change', updateSpecificParams);
monitorForm.addEventListener('submit', handleSubmit);
document.getElementById('clearForm').addEventListener('click', clearForm);
document.getElementById('copyYaml').addEventListener('click', copyYaml);
document.getElementById('downloadYaml').addEventListener('click', downloadYaml);

// Update specific parameters based on monitor type
function updateSpecificParams() {
    const monitorType = monitorTypeSelect.value;
    
    if (!monitorType) {
        specificParamsDiv.style.display = 'none';
        return;
    }
    
    const config = monitorConfigs[monitorType];
    if (!config) return;
    
    specificParamsDiv.style.display = 'block';
    specificParamsContent.innerHTML = '';
    
    config.params.forEach(param => {
        const formGroup = document.createElement('div');
        formGroup.className = 'form-group';
        
        const label = document.createElement('label');
        label.setAttribute('for', param.id);
        label.textContent = param.label;
        
        const input = document.createElement('input');
        input.type = param.type;
        input.id = param.id;
        input.placeholder = param.placeholder;
        
        formGroup.appendChild(label);
        formGroup.appendChild(input);
        specificParamsContent.appendChild(formGroup);
    });
}

// Handle form submission
function handleSubmit(e) {
    e.preventDefault();
    
    const monitorType = document.getElementById('monitorType').value;
    const config = monitorConfigs[monitorType];
    
    // Collect common parameters
    const monitor = {
        name: document.getElementById('monitorName').value,
        monitor_type: monitorType,
        model_name: document.getElementById('modelName').value,
        section: document.getElementById('section').value,
        device_pattern: document.getElementById('devicePattern').value,
        parameters: {
            tmin: document.getElementById('tmin').value,
            tdelay: document.getElementById('tdelay').value,
            vballmsg: document.getElementById('vballmsg').value,
            stop: document.getElementById('stop').value
        }
    };
    
    // Add tmaxfrac if specified
    const tmaxfrac = document.getElementById('tmaxfrac').value;
    if (tmaxfrac) {
        monitor.parameters.tmaxfrac = tmaxfrac;
    }
    
    // Collect monitor-specific parameters
    config.params.forEach(param => {
        const value = document.getElementById(param.id).value;
        if (value) {
            monitor.parameters[param.id] = value;
        }
    });
    
    // Add to monitors list
    monitors.push(monitor);
    
    // Update UI
    updateMonitorList();
    updateYamlPreview();
    clearForm();
    
    // Show success message
    alert('Monitor added successfully!');
}

// Clear form
function clearForm() {
    monitorForm.reset();
    specificParamsDiv.style.display = 'none';
    specificParamsContent.innerHTML = '';
}

// Update monitor list
function updateMonitorList() {
    monitorCount.textContent = monitors.length;
    
    if (monitors.length === 0) {
        monitorList.innerHTML = '<p class="empty-state">No monitors added yet. Use the form above to create monitors.</p>';
        return;
    }
    
    monitorList.innerHTML = monitors.map((monitor, index) => `
        <div class="monitor-item">
            <div class="monitor-header">
                <h4>${monitor.name}</h4>
                <button class="btn btn-small btn-danger" onclick="removeMonitor(${index})">Remove</button>
            </div>
            <div class="monitor-details">
                <span class="badge">${monitor.monitor_type}</span>
                <span class="detail">Model: ${monitor.model_name}</span>
                <span class="detail">Device: ${monitor.device_pattern}</span>
            </div>
        </div>
    `).join('');
}

// Remove monitor
function removeMonitor(index) {
    monitors.splice(index, 1);
    updateMonitorList();
    updateYamlPreview();
}

// Update YAML preview
function updateYamlPreview() {
    const yaml = generateYaml();
    yamlPreview.textContent = yaml;
}

// Generate YAML
function generateYaml() {
    let yaml = `version: "${globalConfig.version}"\n`;
    yaml += `process: "${globalConfig.process}"\n`;
    yaml += `date: "${globalConfig.date}"\n\n`;
    
    yaml += `global:\n`;
    yaml += `  timing:\n`;
    yaml += `    tmin: ${globalConfig.global.timing.tmin}\n`;
    yaml += `    tdelay: ${globalConfig.global.timing.tdelay}\n`;
    yaml += `    vballmsg: ${globalConfig.global.timing.vballmsg}\n`;
    yaml += `    stop: ${globalConfig.global.timing.stop}\n`;
    yaml += `  tmaxfrac:\n`;
    yaml += `    level0: ${globalConfig.global.tmaxfrac.level0}\n`;
    yaml += `    level1: ${globalConfig.global.tmaxfrac.level1}\n`;
    yaml += `    level2: ${globalConfig.global.tmaxfrac.level2}\n`;
    yaml += `    level3: ${globalConfig.global.tmaxfrac.level3}\n\n`;
    
    yaml += `parameters:\n`;
    Object.entries(globalConfig.parameters).forEach(([key, value]) => {
        yaml += `  ${key}: ${value}\n`;
    });
    yaml += `\n`;
    
    yaml += `monitors:\n`;
    
    if (monitors.length === 0) {
        yaml += `  # Add monitors using the form\n`;
    } else {
        monitors.forEach(monitor => {
            yaml += `  - name: "${monitor.name}"\n`;
            yaml += `    monitor_type: ${monitor.monitor_type}\n`;
            yaml += `    model_name: ${monitor.model_name}\n`;
            yaml += `    section: ${monitor.section}\n`;
            yaml += `    device_pattern: "${monitor.device_pattern}"\n`;
            yaml += `    parameters:\n`;
            
            Object.entries(monitor.parameters).forEach(([key, value]) => {
                // Check if value needs quotes
                if (typeof value === 'string' && (value.includes(' ') || value.includes('(') || value.includes('"'))) {
                    yaml += `      ${key}: "${value}"\n`;
                } else {
                    yaml += `      ${key}: ${value}\n`;
                }
            });
            yaml += `\n`;
        });
    }
    
    return yaml;
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
    a.download = `soa_monitors_${globalConfig.date}.yaml`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Initialize
updateYamlPreview();
