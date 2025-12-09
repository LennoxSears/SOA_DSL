"""
SOA DSL Validator - Validates parsed AST for correctness.

Performs syntax, semantic, and consistency checks.
"""

import re
from typing import List, Set, Dict, Any
from dataclasses import dataclass

from .ast_nodes import SOADocument, SOARule, Constraint


@dataclass
class ValidationError:
    """Represents a validation error."""
    rule_name: str
    severity: str  # error, warning, info
    message: str
    line: int = 0
    
    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.rule_name}: {self.message}"


class SOAValidator:
    """Validates SOA DSL documents."""
    
    # Valid device types
    VALID_DEVICE_TYPES = {
        "nmos_core", "pmos_core", "nmos_5v", "pmos_5v",
        "nmos90_10hv", "pmos90_10hv", "nmos90b_10hv", "pmos90b_10hv",
        "nmoshs45_10hv", "pmoshs45_10hv", "nmoshs45b_10hv", "pmoshs45b_10hv",
        "dz5", "npn_b", "pnp_b",
        "poly_10hv", "rm1_10hv", "rm2_10hv", "rm3_10hv", "rm4_10hv",
        "rulm_10hv", "ralcap_10hv", "rphv_10hv",
        "cap_low", "cap_mid", "cap_high",
        "diode_n", "diode_p",
        "bandgap_ref", "temp_sensor"
    }
    
    # Valid rule types
    VALID_RULE_TYPES = {
        "vhigh", "vlow", "ihigh", "ilow", "range",
        "state_dependent", "multi_branch", "current_with_heating",
        "parameter", "pwl", "aging"
    }
    
    # Valid severity levels
    VALID_SEVERITIES = {"high", "medium", "low", "review"}
    
    # Valid pin names for different device types
    DEVICE_PINS = {
        "nmos": ["d", "g", "s", "b", "sub"],
        "pmos": ["d", "g", "s", "b", "sub"],
        "diode": ["p", "n", "sub"],
        "bjt": ["c", "b", "e", "sub"],
        "resistor": ["d", "s"],
        "capacitor": ["t", "b", "nw", "well", "sub"]
    }
    
    def __init__(self, strict: bool = True):
        """
        Initialize validator.
        
        Args:
            strict: If True, treat warnings as errors
        """
        self.strict = strict
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
        self.global_params: Set[str] = set()
    
    def validate(self, document: SOADocument) -> bool:
        """
        Validate an SOA document.
        
        Returns:
            True if validation passes, False otherwise
        """
        self.errors = []
        self.warnings = []
        
        # Collect global parameters
        self._collect_global_params(document.global_config)
        
        # Validate global configuration
        self._validate_global_config(document.global_config)
        
        # Validate each rule
        for rule in document.rules:
            self._validate_rule(rule)
        
        # Check for duplicate rule names
        self._check_duplicate_names(document.rules)
        
        # Return validation result
        has_errors = len(self.errors) > 0
        has_warnings = len(self.warnings) > 0
        
        if self.strict:
            return not (has_errors or has_warnings)
        else:
            return not has_errors
    
    def get_errors(self) -> List[ValidationError]:
        """Get all validation errors."""
        return self.errors
    
    def get_warnings(self) -> List[ValidationError]:
        """Get all validation warnings."""
        return self.warnings
    
    def print_report(self):
        """Print validation report."""
        if self.errors:
            print(f"\n❌ {len(self.errors)} Error(s):")
            for error in self.errors:
                print(f"  {error}")
        
        if self.warnings:
            print(f"\n⚠️  {len(self.warnings)} Warning(s):")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ Validation passed - no errors or warnings")
    
    def _collect_global_params(self, config: Any):
        """Collect all global parameter names."""
        if hasattr(config, 'limits'):
            self.global_params.update(config.limits.keys())
        if hasattr(config, 'timing'):
            self.global_params.update(config.timing.keys())
        if hasattr(config, 'temperature'):
            self.global_params.update(config.temperature.keys())
    
    def _validate_global_config(self, config: Any):
        """Validate global configuration."""
        # Check required timing parameters
        required_timing = ["tmin", "tdelay", "vballmsg", "stop"]
        if hasattr(config, 'timing'):
            for param in required_timing:
                if param not in config.timing:
                    self._add_warning("global", f"Missing timing parameter: {param}")
        
        # Check tmaxfrac levels
        if hasattr(config, 'tmaxfrac'):
            for level in ["level0", "level1", "level2", "level3"]:
                if level not in config.tmaxfrac:
                    self._add_warning("global", f"Missing tmaxfrac: {level}")
    
    def _validate_rule(self, rule: SOARule):
        """Validate a single rule."""
        # Check required fields
        if not rule.name:
            self._add_error(rule.name or "unnamed", "Rule name is required")
        
        if not rule.device:
            self._add_error(rule.name, "Device type is required")
        
        if not rule.parameter:
            self._add_error(rule.name, "Parameter is required")
        
        if not rule.type:
            self._add_error(rule.name, "Rule type is required")
        
        if not rule.severity:
            self._add_error(rule.name, "Severity is required")
        
        # Validate device type
        if rule.device and not self._is_valid_device(rule.device):
            self._add_warning(rule.name, f"Unknown device type: {rule.device}")
        
        # Validate rule type
        if rule.type and rule.type not in self.VALID_RULE_TYPES:
            self._add_error(rule.name, f"Invalid rule type: {rule.type}")
        
        # Validate severity
        if rule.severity and rule.severity not in self.VALID_SEVERITIES:
            self._add_error(rule.name, f"Invalid severity: {rule.severity}")
        
        # Validate parameter syntax
        if rule.parameter:
            self._validate_parameter(rule.name, rule.parameter)
        
        # Validate constraint
        if rule.constraint:
            self._validate_constraint(rule.name, rule.constraint)
        
        # Validate branches
        if rule.branches:
            self._validate_branches(rule.name, rule.branches, rule.device)
        
        # Validate tmaxfrac
        if rule.tmaxfrac:
            self._validate_tmaxfrac(rule.name, rule.tmaxfrac)
        
        # Validate expressions in constraint
        if rule.constraint:
            self._validate_expressions(rule.name, rule.constraint)
        
        # Type-specific validation
        if rule.is_state_dependent():
            self._validate_state_dependent(rule)
        
        if rule.is_multi_branch():
            self._validate_multi_branch(rule)
        
        if rule.is_current_with_heating():
            self._validate_current_with_heating(rule)
    
    def _validate_parameter(self, rule_name: str, parameter: str):
        """Validate parameter syntax."""
        # Check for valid parameter format: v[pin1,pin2], i[device], T, temp
        patterns = [
            r'^v\[[a-z_]+,[a-z_]+\]$',  # v[pin1,pin2]
            r'^v\[[a-z_]+\]$',           # v[pin]
            r'^i\[[a-z_0-9]+\]$',        # i[device]
            r'^i_rms\[[a-z_0-9]+\]$',    # i_rms[device]
            r'^T$',                       # T
            r'^temp$',                    # temp
            r'^multi$'                    # multi (for multi-branch)
        ]
        
        if not any(re.match(pattern, parameter) for pattern in patterns):
            self._add_warning(rule_name, f"Unusual parameter format: {parameter}")
    
    def _validate_constraint(self, rule_name: str, constraint: Constraint):
        """Validate constraint values."""
        # Check that at least one limit is specified
        has_limit = any([
            constraint.vhigh is not None,
            constraint.vlow is not None,
            constraint.ihigh is not None,
            constraint.ilow is not None,
            constraint.vhigh_on is not None,
            constraint.vhigh_off is not None
        ])
        
        if not has_limit:
            self._add_error(rule_name, "Constraint must specify at least one limit")
        
        # Check for contradictory limits
        if constraint.vhigh is not None and constraint.vlow is not None:
            if isinstance(constraint.vhigh, (int, float)) and isinstance(constraint.vlow, (int, float)):
                if constraint.vhigh <= constraint.vlow:
                    self._add_error(rule_name, f"vhigh ({constraint.vhigh}) must be greater than vlow ({constraint.vlow})")
    
    def _validate_branches(self, rule_name: str, branches: List, device: str):
        """Validate branch specifications."""
        if not branches:
            self._add_error(rule_name, "Multi-branch rule must have at least one branch")
            return
        
        # Check branch syntax
        for i, branch in enumerate(branches):
            if not hasattr(branch, 'branch') or not branch.branch:
                self._add_error(rule_name, f"Branch {i+1} missing branch specification")
                continue
            
            # Validate branch format: V(pin1,pin2) or V(pin)
            if not re.match(r'^V\([a-z_]+(?:,[a-z_]+)?\)$', branch.branch):
                self._add_warning(rule_name, f"Unusual branch format: {branch.branch}")
            
            # Check that at least vhigh or vlow is specified
            if branch.vhigh is None and branch.vlow is None:
                self._add_error(rule_name, f"Branch {branch.branch} must specify vhigh or vlow")
    
    def _validate_tmaxfrac(self, rule_name: str, tmaxfrac: Dict[str, float]):
        """Validate tmaxfrac levels."""
        # Check that values are in ascending order
        levels = sorted([(float(k), v) for k, v in tmaxfrac.items()])
        
        for i in range(len(levels) - 1):
            frac1, val1 = levels[i]
            frac2, val2 = levels[i + 1]
            
            if frac1 >= frac2:
                self._add_error(rule_name, f"tmaxfrac levels must be in ascending order")
                break
    
    def _validate_expressions(self, rule_name: str, constraint: Constraint):
        """Validate expressions in constraints."""
        expressions = []
        
        # Collect all expression strings
        for attr in ['vhigh', 'vlow', 'ihigh', 'ilow', 'vhigh_on', 'vhigh_off']:
            value = getattr(constraint, attr, None)
            if isinstance(value, str):
                expressions.append((attr, value))
        
        for attr_name, expr in expressions:
            self._validate_expression(rule_name, attr_name, expr)
    
    def _validate_expression(self, rule_name: str, attr_name: str, expr: str):
        """Validate a single expression."""
        # Check for valid operators
        valid_operators = ['+', '-', '*', '/', '^', '(', ')', '<', '>', '=', '!']
        valid_functions = ['min', 'max', 'abs', 'sqrt', 'exp', 'log', 'if', 'then', 'else']
        
        # Check for undefined variables
        # Extract variable names (simple heuristic)
        tokens = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', expr)
        
        for token in tokens:
            if token in valid_functions:
                continue
            if token in ['T', 'temp']:
                continue
            if token.startswith('v[') or token.startswith('i['):
                continue
            if token.startswith('$'):  # Device parameter
                continue
            if token not in self.global_params:
                self._add_warning(rule_name, f"Undefined variable in {attr_name}: {token}")
    
    def _validate_state_dependent(self, rule: SOARule):
        """Validate state-dependent rule."""
        if not rule.constraint:
            self._add_error(rule.name, "State-dependent rule must have constraint")
            return
        
        # Check for on/off limits
        if rule.constraint.vhigh_on is None and rule.constraint.vhigh_off is None:
            self._add_error(rule.name, "State-dependent rule must specify vhigh_on or vhigh_off")
        
        # Check for gate control
        if not rule.gate_control:
            self._add_warning(rule.name, "State-dependent rule should have gate_control")
    
    def _validate_multi_branch(self, rule: SOARule):
        """Validate multi-branch rule."""
        if not rule.branches:
            self._add_error(rule.name, "Multi-branch rule must have branches")
        
        if len(rule.branches) > 6:
            self._add_error(rule.name, f"Too many branches ({len(rule.branches)}), maximum is 6")
    
    def _validate_current_with_heating(self, rule: SOARule):
        """Validate current with self-heating rule."""
        if not rule.constraints:
            self._add_error(rule.name, "Current with heating rule must have constraints")
        
        if not rule.self_heating:
            self._add_warning(rule.name, "Current with heating rule should have self_heating")
    
    def _check_duplicate_names(self, rules: List[SOARule]):
        """Check for duplicate rule names."""
        names = {}
        for rule in rules:
            if rule.name in names:
                self._add_error(rule.name, f"Duplicate rule name (also at rule {names[rule.name]})")
            else:
                names[rule.name] = rule.name
    
    def _is_valid_device(self, device: str) -> bool:
        """Check if device type is valid."""
        # Exact match
        if device in self.VALID_DEVICE_TYPES:
            return True
        
        # Partial match (e.g., nmos_core matches nmos)
        for valid_device in self.VALID_DEVICE_TYPES:
            if device.startswith(valid_device) or valid_device.startswith(device):
                return True
        
        return False
    
    def _add_error(self, rule_name: str, message: str):
        """Add a validation error."""
        self.errors.append(ValidationError(
            rule_name=rule_name,
            severity="error",
            message=message
        ))
    
    def _add_warning(self, rule_name: str, message: str):
        """Add a validation warning."""
        self.warnings.append(ValidationError(
            rule_name=rule_name,
            severity="warning",
            message=message
        ))
