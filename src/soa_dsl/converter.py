"""
SOA DSL Converter - Universal to Monitor-Aware Specification
Converts user-friendly universal YAML to monitor-specific YAML.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


class ConversionError(Exception):
    """Exception raised for conversion errors."""
    pass


@dataclass
class ConversionContext:
    """Context for conversion process."""
    device_library: Dict[str, Any]
    monitor_library: Dict[str, Any]
    global_config: Dict[str, Any]
    time_limit_map: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        # Build time limit mapping
        if 'time_limit_mapping' in self.monitor_library:
            self.time_limit_map = self.monitor_library['time_limit_mapping']


class UniversalToMonitorConverter:
    """Converts universal SOA spec to monitor-aware spec."""
    
    def __init__(self, device_library_path: Path, monitor_library_path: Path):
        self.device_lib = self._load_yaml(device_library_path)
        self.monitor_lib = self._load_yaml(monitor_library_path)
        
    def _load_yaml(self, filepath: Path) -> Dict[str, Any]:
        """Load YAML file."""
        try:
            with open(filepath, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise ConversionError(f"Failed to load {filepath}: {e}")
    
    def convert(self, universal_spec_path: Path) -> Dict[str, Any]:
        """Convert universal YAML to monitor YAML."""
        universal = self._load_yaml(universal_spec_path)
        
        # Create conversion context
        ctx = ConversionContext(
            device_library=self.device_lib,
            monitor_library=self.monitor_lib,
            global_config=universal.get('globals', {})
        )
        
        # Build monitor document
        monitor_doc = {
            'version': universal.get('version', '1.0'),
            'process': universal.get('process', 'UNKNOWN'),
            'date': universal.get('date', '2024-12-16'),
            'global': self._build_global_section(ctx),
            'parameters': self._build_parameters_section(ctx),
            'monitors': []
        }
        
        # Convert each rule to monitor(s)
        for rule in universal.get('rules', []):
            monitors = self._convert_rule(rule, ctx)
            monitor_doc['monitors'].extend(monitors)
        
        return monitor_doc
    
    def _build_global_section(self, ctx: ConversionContext) -> Dict[str, Any]:
        """Build global section for monitor YAML."""
        timing = ctx.global_config.get('timing', {})
        time_limits = ctx.global_config.get('time_limits', {})
        
        return {
            'timing': {
                'tmin': timing.get('tmin', 0),
                'tdelay': timing.get('tdelay', 0),
                'vballmsg': timing.get('vballmsg', 1.0),
                'stop': timing.get('stop', 0)
            },
            'tmaxfrac': {
                'level0': time_limits.get('steady', 0),
                'level1': time_limits.get('transient_1pct', 0.01),
                'level2': time_limits.get('transient_10pct', 0.10),
                'level3': time_limits.get('review', -1)
            }
        }
    
    def _build_parameters_section(self, ctx: ConversionContext) -> Dict[str, Any]:
        """Build parameters section for monitor YAML."""
        timing = ctx.global_config.get('timing', {})
        time_limits = ctx.global_config.get('time_limits', {})
        params = ctx.global_config.get('parameters', {})
        
        return {
            'global_tmin': timing.get('tmin', 0),
            'global_tdelay': timing.get('tdelay', 0),
            'global_vballmsg': timing.get('vballmsg', 1.0),
            'global_stop': timing.get('stop', 0),
            'tmaxfrac0': time_limits.get('steady', 0),
            'tmaxfrac1': time_limits.get('transient_1pct', 0.01),
            'tmaxfrac2': time_limits.get('transient_10pct', 0.10),
            'tmaxfrac3': time_limits.get('review', -1),
            **params
        }
    
    def _convert_rule(self, rule: Dict[str, Any], ctx: ConversionContext) -> List[Dict[str, Any]]:
        """Convert a single rule to one or more monitors."""
        monitors = []
        
        # Get device info
        device_names = rule['applies_to']['devices']
        
        # For each device, create a monitor
        for device_name in device_names:
            device_info = self._get_device_info(device_name, ctx)
            
            # Select monitor type
            monitor_type = self._select_monitor_type(rule, device_info, ctx)
            
            # Generate monitor definition
            monitor = self._generate_monitor(rule, device_name, device_info, monitor_type, ctx)
            
            monitors.append(monitor)
        
        return monitors
    
    def _get_device_info(self, device_name: str, ctx: ConversionContext) -> Dict[str, Any]:
        """Get device information from library."""
        devices = ctx.device_library.get('devices', {})
        
        if device_name not in devices:
            raise ConversionError(f"Unknown device: {device_name}")
        
        return devices[device_name]
    
    def _select_monitor_type(self, rule: Dict[str, Any], device_info: Dict[str, Any], 
                            ctx: ConversionContext) -> str:
        """Select appropriate monitor type based on rule characteristics."""
        check = rule['check']
        check_type = check['type']
        
        # State-dependent check?
        if check.get('state_dependent'):
            return 'ovcheckva_mos2'
        
        # Temperature-dependent check?
        if check.get('temperature_dependent'):
            return 'ovcheckva_pwl'
        
        # Aging check?
        if check_type == 'aging':
            return 'ovcheckva_ldmos_hci_tddb'
        
        # Parameter check?
        if check_type == 'parameter':
            return 'parcheckva3'
        
        # Self-heating check?
        if check_type == 'self_heating':
            return 'ovcheck'
        
        # Voltage/current check - single or multi-branch?
        if check_type in ['voltage', 'current']:
            measure = check['measure']
            if isinstance(measure, list):
                return 'ovcheck6'  # multi-branch
            else:
                return 'ovcheck'   # single-branch
        
        raise ConversionError(f"Cannot determine monitor type for rule: {rule['name']}")
    
    def _generate_monitor(self, rule: Dict[str, Any], device_name: str, 
                         device_info: Dict[str, Any], monitor_type: str,
                         ctx: ConversionContext) -> Dict[str, Any]:
        """Generate monitor definition."""
        # Generate names
        rule_slug = self._slugify(rule['name'])
        model_name = f"{monitor_type}_{device_name}_{rule_slug}"
        section = f"soacheck_{device_name}_{rule_slug}_shared"
        
        # Build monitor
        monitor = {
            'name': rule['name'],
            'monitor_type': monitor_type,
            'model_name': model_name,
            'section': section,
            'device_pattern': device_name,
            'parameters': self._generate_parameters(rule, monitor_type, ctx)
        }
        
        return monitor
    
    def _generate_parameters(self, rule: Dict[str, Any], monitor_type: str,
                            ctx: ConversionContext) -> Dict[str, Any]:
        """Generate monitor-specific parameters."""
        params = {
            'tmin': 'global_tmin',
            'tdelay': 'global_tdelay',
            'vballmsg': 'global_vballmsg',
            'stop': 'global_stop'
        }
        
        # Add time limit
        time_limit = rule['limits'].get('time_limit', 'steady')
        if time_limit in ctx.time_limit_map:
            tmaxfrac_name = ctx.time_limit_map[time_limit]
            params['tmaxfrac'] = tmaxfrac_name
        
        # Monitor-specific parameters
        if monitor_type == 'ovcheck':
            self._add_ovcheck_params(params, rule, ctx)
        elif monitor_type == 'ovcheck6':
            self._add_ovcheck6_params(params, rule, ctx)
        elif monitor_type == 'ovcheckva_mos2':
            self._add_mos2_params(params, rule, ctx)
        elif monitor_type == 'ovcheckva_pwl':
            self._add_pwl_params(params, rule, ctx)
        elif monitor_type == 'ovcheckva_ldmos_hci_tddb':
            self._add_hci_tddb_params(params, rule, ctx)
        elif monitor_type == 'parcheckva3':
            self._add_parcheck_params(params, rule, ctx)
        
        return params
    
    def _add_ovcheck_params(self, params: Dict[str, Any], rule: Dict[str, Any],
                           ctx: ConversionContext):
        """Add ovcheck-specific parameters."""
        check = rule['check']
        limits = rule['limits']
        
        # Self-heating check?
        if check['type'] == 'self_heating':
            current_limits = limits.get('current_limits', {})
            params['dtmax'] = limits.get('max_temp_rise', 5)
            params['theat'] = limits.get('thermal_time_constant', 1e-7)
            params['monitor'] = 'temperature'
            
            # DC current
            if 'dc_max' in current_limits:
                params['idc_high'] = self._generate_expression(current_limits['dc_max'])
            
            # Peak current
            if 'peak_max' in current_limits:
                params['ipeak_high'] = self._generate_expression(current_limits['peak_max'])
            
            # RMS current
            if 'rms_max' in current_limits:
                params['irms_high'] = self._generate_expression(current_limits['rms_max'])
        else:
            # Regular voltage/current check
            measure = check['measure']
            params['branch1'] = measure
            
            if 'message' in rule:
                params['message1'] = rule['message']
            
            # Add limits
            if 'steady' in limits:
                if 'min' in limits['steady']:
                    params['vlow'] = limits['steady']['min']
                if 'max' in limits['steady']:
                    params['vhigh'] = limits['steady']['max']
    
    def _add_ovcheck6_params(self, params: Dict[str, Any], rule: Dict[str, Any],
                            ctx: ConversionContext):
        """Add ovcheck6-specific parameters (multi-branch)."""
        check = rule['check']
        limits = rule['limits']
        measures = check['measure']
        
        for i, measure_spec in enumerate(measures, 1):
            signal = measure_spec['signal']
            message = measure_spec.get('message', f"Branch{i}")
            
            params[f'branch{i}'] = signal
            params[f'message{i}'] = message
            
            # Add limits
            if 'steady' in limits:
                if 'min' in limits['steady']:
                    params[f'vlow{i}'] = limits['steady']['min']
                if 'max' in limits['steady']:
                    params[f'vhigh{i}'] = limits['steady']['max']
    
    def _add_mos2_params(self, params: Dict[str, Any], rule: Dict[str, Any],
                        ctx: ConversionContext):
        """Add ovcheckva_mos2-specific parameters (state-dependent)."""
        limits = rule['limits']
        state_detection = rule.get('state_detection', {})
        
        # State limits
        if 'when_on' in limits and 'max' in limits['when_on']:
            params['vhigh_on'] = limits['when_on']['max']
        
        if 'when_off' in limits and 'max' in limits['when_off']:
            params['vhigh_off'] = limits['when_off']['max']
        
        # Gate control limits
        if 'gate_control' in limits:
            if 'max' in limits['gate_control']:
                params['vhigh_gc'] = limits['gate_control']['max']
            if 'min' in limits['gate_control']:
                params['vlow_gc'] = limits['gate_control']['min']
        
        # State detection
        params['param'] = state_detection.get('parameter', 'vth')
        params['vgt'] = state_detection.get('threshold', 0.0)
    
    def _add_pwl_params(self, params: Dict[str, Any], rule: Dict[str, Any],
                       ctx: ConversionContext):
        """Add ovcheckva_pwl-specific parameters (temperature-dependent)."""
        check = rule['check']
        limits = rule['limits']
        
        measure = check['measure']
        params['branch1'] = measure
        
        if 'message' in rule:
            params['message1'] = rule['message']
        
        # Temperature-dependent expression
        if 'temperature_dependent' in limits:
            td = limits['temperature_dependent']
            ref_temp = td.get('reference_temp', 25)
            ref_value = td.get('reference_value', 0)
            coeff = td.get('temp_coefficient', 0)
            
            # Generate expression
            if coeff >= 0:
                expr = f'"{ref_value} + {coeff} * (T - {ref_temp})"'
            else:
                expr = f'"{ref_value} - {abs(coeff)} * (T - {ref_temp})"'
            
            params['vlow'] = f'"-{ref_value} - {abs(coeff)} * (T - {ref_temp})"'
            params['vhigh'] = expr
    
    def _add_hci_tddb_params(self, params: Dict[str, Any], rule: Dict[str, Any],
                            ctx: ConversionContext):
        """Add ovcheckva_ldmos_hci_tddb-specific parameters (aging)."""
        limits = rule['limits']
        
        if 'aging_parameters' in limits:
            aging = limits['aging_parameters']
            params['atype'] = 'atype'
            
            # Add all aging coefficients
            for key in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n']:
                if key in aging:
                    params[f'soa_hcitddb_{key}'] = aging[key]
    
    def _add_parcheck_params(self, params: Dict[str, Any], rule: Dict[str, Any],
                            ctx: ConversionContext):
        """Add parcheckva3-specific parameters (parameter check)."""
        check = rule['check']
        limits = rule['limits']
        
        params['param'] = check.get('parameter', 'vth')
        
        if 'gate_threshold' in limits:
            params['vgt'] = limits['gate_threshold']
        
        if 'steady' in limits:
            if 'min' in limits['steady']:
                params['vlow'] = limits['steady']['min']
            if 'max' in limits['steady']:
                params['vhigh'] = limits['steady']['max']
    
    def _generate_expression(self, spec: Dict[str, Any]) -> str:
        """Generate expression from specification."""
        if 'expression' in spec:
            return spec['expression']
        
        if 'formula' in spec:
            formula = spec['formula']
            params_list = spec.get('parameters', [])
            coeffs = spec.get('coefficients', [])
            
            if formula == 'linear':
                # Generate: $param * coeff
                parts = []
                for param, coeff in zip(params_list, coeffs):
                    parts.append(f"${param} * {coeff}")
                return " * ".join(parts)
        
        return "0"
    
    def _slugify(self, text: str) -> str:
        """Convert text to slug (lowercase, underscores)."""
        return text.lower().replace(' ', '_').replace('-', '_')


def convert_universal_to_monitor(universal_path: Path, device_lib_path: Path,
                                 monitor_lib_path: Path, output_path: Path):
    """Convenience function to convert universal spec to monitor spec."""
    converter = UniversalToMonitorConverter(device_lib_path, monitor_lib_path)
    monitor_doc = converter.convert(universal_path)
    
    with open(output_path, 'w') as f:
        yaml.dump(monitor_doc, f, default_flow_style=False, sort_keys=False)
    
    return monitor_doc
