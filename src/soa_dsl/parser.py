"""
SOA DSL Parser - Converts YAML DSL files to AST.

YAML is the single supported format for its human-readability,
comments support, and minimal syntax.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional

from .ast_nodes import (
    SOADocument, SOARule, GlobalConfig, Constraint, Branch,
    GateControl, GateBulk, Junction, MonitorParams, Messages,
    AgingCheck, SelfHeating, CurrentConstraint
)


class ParseError(Exception):
    """Exception raised for parsing errors."""
    pass


class SOAParser:
    """YAML parser for SOA DSL."""
    
    def _parse_global_config(self, data: Dict[str, Any]) -> GlobalConfig:
        """Parse global configuration section."""
        global_data = data.get("global", {})
        return GlobalConfig(
            timing=global_data.get("timing", {}),
            temperature=global_data.get("temperature", {}),
            tmaxfrac=global_data.get("tmaxfrac", {}),
            limits=global_data.get("limits", {})
        )
    
    def _parse_constraint(self, data: Dict[str, Any]) -> Optional[Constraint]:
        """Parse constraint section."""
        if not data:
            return None
        
        return Constraint(
            vhigh=data.get("vhigh"),
            vlow=data.get("vlow"),
            ihigh=data.get("ihigh"),
            ilow=data.get("ilow"),
            vhigh_on=data.get("vhigh_on"),
            vhigh_off=data.get("vhigh_off"),
            vlow_on=data.get("vlow_on"),
            vlow_off=data.get("vlow_off")
        )
    
    def _parse_branches(self, data: List[Dict[str, Any]]) -> List[Branch]:
        """Parse branches section."""
        branches = []
        for branch_data in data:
            branches.append(Branch(
                branch=branch_data.get("branch", ""),
                vhigh=branch_data.get("vhigh"),
                vlow=branch_data.get("vlow"),
                message=branch_data.get("message")
            ))
        return branches
    
    def _parse_gate_control(self, data: Dict[str, Any]) -> Optional[GateControl]:
        """Parse gate_control section."""
        if not data:
            return None
        return GateControl(
            vhigh_gc=data.get("vhigh_gc", 0.0),
            vlow_gc=data.get("vlow_gc", 0.0)
        )
    
    def _parse_gate_bulk(self, data: Dict[str, Any]) -> Optional[GateBulk]:
        """Parse gate_bulk section."""
        if not data:
            return None
        return GateBulk(
            vhigh_gb_on=data.get("vhigh_gb_on", 0.0),
            vlow_gb_on=data.get("vlow_gb_on", 0.0)
        )
    
    def _parse_junction(self, data: Dict[str, Any]) -> Optional[Junction]:
        """Parse junction section."""
        if not data:
            return None
        return Junction(
            vfwd_jun_on=data.get("vfwd_jun_on", 0.0),
            vrev_jun_on=data.get("vrev_jun_on", 0.0),
            vfwd_jun_off=data.get("vfwd_jun_off", 0.0),
            vrev_jun_off=data.get("vrev_jun_off", 0.0)
        )
    
    def _parse_monitor_params(self, data: Dict[str, Any]) -> Optional[MonitorParams]:
        """Parse monitor_params section."""
        if not data:
            return None
        return MonitorParams(
            param=data.get("param", "vth"),
            vgt=data.get("vgt", 0.0),
            pmosvthsign=data.get("pmosvthsign", 1),
            inst2probe=data.get("inst2probe", "fet")
        )
    
    def _parse_messages(self, data: Dict[str, Any]) -> Optional[Messages]:
        """Parse messages section."""
        if not data:
            return None
        return Messages(
            vds=data.get("vds"),
            vgs=data.get("vgs"),
            vgd=data.get("vgd"),
            vgb=data.get("vgb"),
            vsb=data.get("vsb"),
            vdb=data.get("vdb")
        )
    
    def _parse_aging_check(self, data: Dict[str, Any]) -> Optional[AgingCheck]:
        """Parse aging_check section."""
        if not data:
            return None
        return AgingCheck(
            type=data.get("type", ""),
            variant=data.get("variant", ""),
            params=data.get("params", {})
        )
    
    def _parse_self_heating(self, data: Dict[str, Any]) -> Optional[SelfHeating]:
        """Parse self_heating section."""
        if not data:
            return None
        return SelfHeating(
            dtmax=data.get("dtmax", 0.0),
            theat=data.get("theat", 0.0),
            monitor=data.get("monitor", "shmonitor_nofeedback")
        )
    
    def _parse_current_constraints(self, data: List[Dict[str, Any]]) -> List[CurrentConstraint]:
        """Parse current constraints for resistors."""
        constraints = []
        for constraint_data in data:
            constraints.append(CurrentConstraint(
                name=constraint_data.get("name", ""),
                type=constraint_data.get("type", ""),
                ihigh=constraint_data.get("ihigh", 0.0),
                message=constraint_data.get("message", "")
            ))
        return constraints
    
    def _parse_rule(self, rule_data: Dict[str, Any]) -> SOARule:
        """Parse a single rule."""
        return SOARule(
            name=rule_data.get("name", ""),
            device=rule_data.get("device", ""),
            parameter=rule_data.get("parameter", ""),
            type=rule_data.get("type", ""),
            severity=rule_data.get("severity", ""),
            description=rule_data.get("description", ""),
            condition=rule_data.get("condition"),
            constraint=self._parse_constraint(rule_data.get("constraint", {})),
            tmaxfrac=rule_data.get("tmaxfrac", {}),
            branches=self._parse_branches(rule_data.get("branches", [])),
            connections=rule_data.get("connections"),
            gate_control=self._parse_gate_control(rule_data.get("gate_control", {})),
            gate_bulk=self._parse_gate_bulk(rule_data.get("gate_bulk", {})),
            junction=self._parse_junction(rule_data.get("junction", {})),
            monitor_params=self._parse_monitor_params(rule_data.get("monitor_params", {})),
            messages=self._parse_messages(rule_data.get("messages", {})),
            aging_check=self._parse_aging_check(rule_data.get("aging_check", {})),
            constraints=self._parse_current_constraints(rule_data.get("constraints", [])),
            self_heating=self._parse_self_heating(rule_data.get("self_heating", {})),
            device_params=rule_data.get("device_params", {})
        )


    def parse(self, file_path: Path) -> SOADocument:
        """Parse a YAML file."""
        with open(file_path, 'r') as f:
            content = f.read()
        return self.parse_string(content)
    
    def parse_string(self, content: str) -> SOADocument:
        """Parse YAML content from a string."""
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise ParseError(f"YAML parsing error: {e}")
        
        return self._build_document(data)
    
    def _build_document(self, data: Dict[str, Any]) -> SOADocument:
        """Build SOADocument from parsed data."""
        global_config = self._parse_global_config(data)
        
        rules = []
        for rule_data in data.get("rules", []):
            rules.append(self._parse_rule(rule_data))
        
        return SOADocument(
            version=data.get("version", "1.0"),
            process=data.get("process", ""),
            date=data.get("date", ""),
            global_config=global_config,
            rules=rules
        )


def parse_file(file_path: str) -> SOADocument:
    """Parse a YAML DSL file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Only support YAML
    ext = path.suffix.lower()
    if ext not in ['.yaml', '.yml']:
        raise ValueError(f"Only YAML format is supported. Got: {ext}")
    
    parser = SOAParser()
    return parser.parse(path)
