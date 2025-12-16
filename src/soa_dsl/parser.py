"""
SOA DSL Parser - Monitor-Based Specification
Parses YAML files that directly map to Verilog-A monitors.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


class ParseError(Exception):
    """Exception raised for parsing errors."""
    pass


@dataclass
class MonitorParameters:
    """Monitor-specific parameters."""
    tmin: str
    tdelay: str
    vballmsg: str
    stop: str
    tmaxfrac: Optional[str] = None
    # Additional parameters stored as dict
    extra: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.extra is None:
            self.extra = {}


@dataclass
class Monitor:
    """Represents a single monitor definition."""
    name: str
    monitor_type: str
    model_name: str
    section: str
    device_pattern: str
    parameters: MonitorParameters
    self_heating: Optional[Dict[str, Any]] = None
    branches: Optional[List[Dict[str, Any]]] = None
    gate_control: Optional[Dict[str, Any]] = None
    monitor_params: Optional[Dict[str, Any]] = None
    hci_tddb_params: Optional[Dict[str, Any]] = None
    constraints: Optional[List[Dict[str, Any]]] = None


@dataclass
class GlobalConfig:
    """Global configuration."""
    timing: Dict[str, Any]
    tmaxfrac: Dict[str, Any]


@dataclass
class SOADocument:
    """Root document containing all monitors."""
    version: str
    process: str
    date: str
    global_config: GlobalConfig
    monitors: List[Monitor]
    parameters: Optional[Dict[str, Any]] = None


class SOAParser:
    """YAML parser for SOA DSL (monitor-based)."""
    
    VALID_MONITOR_TYPES = {
        'ovcheck',
        'ovcheck6',
        'ovcheckva_mos2',
        'ovcheckva_pwl',
        'ovcheckva_ldmos_hci_tddb',
        'parcheckva3',
    }
    
    def parse_file(self, filepath: Path) -> SOADocument:
        """Parse a YAML file and return SOADocument."""
        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
            return self.parse(data)
        except yaml.YAMLError as e:
            raise ParseError(f"YAML parsing error: {e}")
        except FileNotFoundError:
            raise ParseError(f"File not found: {filepath}")
    
    def parse(self, data: Dict[str, Any]) -> SOADocument:
        """Parse YAML data into SOADocument."""
        # Get version (optional)
        version = data.get('version', '1.0')
        
        # Parse required fields
        process = data.get('process')
        if not process:
            raise ParseError("Missing required field: process")
        
        date = data.get('date')
        if not date:
            raise ParseError("Missing required field: date")
        
        # Parse global config
        global_config = self._parse_global_config(data)
        
        # Parse monitors
        monitors_data = data.get('monitors', [])
        if not monitors_data:
            raise ParseError("No monitors defined")
        
        monitors = [self._parse_monitor(m) for m in monitors_data]
        
        # Parse parameters if present
        parameters = data.get('parameters')
        
        return SOADocument(
            version=version,
            process=process,
            date=date,
            global_config=global_config,
            monitors=monitors,
            parameters=parameters
        )
    
    def _parse_global_config(self, data: Dict[str, Any]) -> GlobalConfig:
        """Parse global configuration section."""
        global_data = data.get('global', {})
        
        timing = global_data.get('timing', {})
        tmaxfrac = global_data.get('tmaxfrac', {})
        
        # Validate required timing parameters
        required_timing = ['tmin', 'tdelay', 'vballmsg', 'stop']
        for param in required_timing:
            if param not in timing:
                raise ParseError(f"Missing required timing parameter: {param}")
        
        # Validate tmaxfrac levels
        required_levels = ['level0', 'level1', 'level2', 'level3']
        for level in required_levels:
            if level not in tmaxfrac:
                raise ParseError(f"Missing required tmaxfrac level: {level}")
        
        return GlobalConfig(timing=timing, tmaxfrac=tmaxfrac)
    
    def _parse_monitor(self, data: Dict[str, Any]) -> Monitor:
        """Parse a single monitor definition."""
        # Validate required fields
        required_fields = ['name', 'monitor_type', 'model_name', 'section', 
                          'device_pattern', 'parameters']
        for field in required_fields:
            if field not in data:
                raise ParseError(f"Monitor missing required field: {field}")
        
        name = data['name']
        monitor_type = data['monitor_type']
        
        # Validate monitor type
        if monitor_type not in self.VALID_MONITOR_TYPES:
            raise ParseError(
                f"Invalid monitor_type '{monitor_type}'. "
                f"Valid types: {', '.join(self.VALID_MONITOR_TYPES)}"
            )
        
        # Parse parameters
        params_data = data['parameters']
        parameters = self._parse_parameters(params_data, monitor_type)
        
        # Parse optional sections
        self_heating = data.get('self_heating')
        branches = data.get('parameters', {}).get('branches')
        gate_control = data.get('parameters', {}).get('gate_control')
        monitor_params = data.get('parameters', {}).get('monitor_params')
        hci_tddb_params = data.get('parameters', {}).get('hci_tddb_params')
        constraints = data.get('parameters', {}).get('constraints')
        
        return Monitor(
            name=name,
            monitor_type=monitor_type,
            model_name=data['model_name'],
            section=data['section'],
            device_pattern=data['device_pattern'],
            parameters=parameters,
            self_heating=self_heating,
            branches=branches,
            gate_control=gate_control,
            monitor_params=monitor_params,
            hci_tddb_params=hci_tddb_params,
            constraints=constraints
        )
    
    def _parse_parameters(self, data: Dict[str, Any], monitor_type: str) -> MonitorParameters:
        """Parse monitor parameters."""
        # Common parameters
        required_common = ['tmin', 'tdelay', 'vballmsg', 'stop']
        for param in required_common:
            if param not in data:
                raise ParseError(f"Missing required parameter: {param}")
        
        # Extract common parameters
        params = MonitorParameters(
            tmin=str(data['tmin']),
            tdelay=str(data['tdelay']),
            vballmsg=str(data['vballmsg']),
            stop=str(data['stop']),
            tmaxfrac=str(data.get('tmaxfrac', ''))
        )
        
        # Store all other parameters in extra
        extra = {}
        for key, value in data.items():
            if key not in required_common and key != 'tmaxfrac':
                extra[key] = value
        
        params.extra = extra
        
        return params


def parse_file(filepath: Path) -> SOADocument:
    """Convenience function to parse a file."""
    parser = SOAParser()
    return parser.parse_file(filepath)


def parse(data: Dict[str, Any]) -> SOADocument:
    """Convenience function to parse data."""
    parser = SOAParser()
    return parser.parse(data)
