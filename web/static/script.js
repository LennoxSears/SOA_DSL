// Global state
let rules = [];
let currentYAML = '';

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('ruleForm').addEventListener('submit', handleAddRule);
    updateRulesList();
});

// Handle form submission
function handleAddRule(e) {
    e.preventDefault();
    
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
    if (ihigh) rule.constraint.ihigh = ihigh; // Keep as string for expressions
    if (ilow) rule.constraint.ilow = parseValue(ilow);
    
    // Add condition if specified
    const condition = document.getElementById('condition').value;
    if (condition) rule.condition = condition;
    
    // Validate rule
    fetch('/api/validate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(rule)
    })
    .then(response => response.json())
    .then(data => {
        if (data.valid) {
            rules.push(rule);
            updateRulesList();
            updateYAMLPreview();
            clearForm();
            showNotification('Rule added successfully!', 'success');
        } else {
            showNotification('Validation errors: ' + data.errors.join(', '), 'error');
        }
    })
    .catch(error => {
        showNotification('Error: ' + error.message, 'error');
    });
}

// Parse value (convert to number if possible)
function parseValue(value) {
    const trimmed = value.trim();
    const num = parseFloat(trimmed);
    return isNaN(num) ? trimmed : num;
}

// Update rules list display
function updateRulesList() {
    const rulesList = document.getElementById('rulesList');
    const ruleCount = document.getElementById('ruleCount');
    
    ruleCount.textContent = rules.length;
    
    if (rules.length === 0) {
        rulesList.innerHTML = '<p class="empty-state">No rules added yet. Create your first rule!</p>';
        return;
    }
    
    rulesList.innerHTML = rules.map((rule, index) => `
        <div class="rule-card">
            <button class="delete-btn" onclick="deleteRule(${index})">Delete</button>
            <h4>${rule.name}</h4>
            <div class="rule-details">
                <div class="rule-detail"><strong>Device:</strong> ${rule.device}</div>
                <div class="rule-detail"><strong>Type:</strong> ${rule.type}</div>
                <div class="rule-detail"><strong>Parameter:</strong> ${rule.parameter}</div>
                <div class="rule-detail"><strong>Severity:</strong> ${rule.severity}</div>
                ${rule.constraint.vhigh ? `<div class="rule-detail"><strong>V High:</strong> ${rule.constraint.vhigh}</div>` : ''}
                ${rule.constraint.vlow ? `<div class="rule-detail"><strong>V Low:</strong> ${rule.constraint.vlow}</div>` : ''}
                ${rule.constraint.ihigh ? `<div class="rule-detail"><strong>I High:</strong> ${rule.constraint.ihigh}</div>` : ''}
                ${rule.constraint.ilow ? `<div class="rule-detail"><strong>I Low:</strong> ${rule.constraint.ilow}</div>` : ''}
            </div>
            ${rule.description ? `<p style="margin-top: 10px; font-size: 13px; color: #666;">${rule.description}</p>` : ''}
        </div>
    `).join('');
}

// Delete rule
function deleteRule(index) {
    if (confirm('Are you sure you want to delete this rule?')) {
        rules.splice(index, 1);
        updateRulesList();
        updateYAMLPreview();
        showNotification('Rule deleted', 'success');
    }
}

// Update YAML preview
function updateYAMLPreview() {
    const processName = document.getElementById('processName').value || 'CUSTOM';
    
    fetch('/api/generate-yaml', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            process: processName,
            rules: rules
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            currentYAML = data.yaml;
            document.getElementById('yamlPreview').textContent = data.yaml;
        } else {
            showNotification('Error generating YAML: ' + data.error, 'error');
        }
    })
    .catch(error => {
        showNotification('Error: ' + error.message, 'error');
    });
}

// Validate YAML
function validateYAML() {
    if (!currentYAML) {
        showNotification('No YAML to validate', 'error');
        return;
    }
    
    fetch('/api/validate-yaml', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({yaml: currentYAML})
    })
    .then(response => response.json())
    .then(data => {
        const resultDiv = document.getElementById('validationResult');
        
        if (data.valid) {
            resultDiv.className = 'validation-result success';
            resultDiv.innerHTML = `
                <h4>✅ Validation Passed</h4>
                <p>Successfully validated ${data.rule_count} rule(s)</p>
                ${data.warnings.length > 0 ? `
                    <p><strong>Warnings:</strong></p>
                    <ul>${data.warnings.map(w => `<li>${w}</li>`).join('')}</ul>
                ` : ''}
            `;
        } else {
            resultDiv.className = 'validation-result error';
            resultDiv.innerHTML = `
                <h4>❌ Validation Failed</h4>
                <p><strong>Errors:</strong></p>
                <ul>${data.errors.map(e => `<li>${e}</li>`).join('')}</ul>
            `;
        }
    })
    .catch(error => {
        showNotification('Error: ' + error.message, 'error');
    });
}

// Download YAML
function downloadYAML() {
    if (!currentYAML) {
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
}

// Clear form
function clearForm() {
    document.getElementById('ruleForm').reset();
}

// Show tab
function showTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
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
    // Simple alert for now - could be enhanced with a toast notification
    if (type === 'success') {
        console.log('✅', message);
    } else {
        alert(message);
    }
}
