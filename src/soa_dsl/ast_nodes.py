"""
Abstract Syntax Tree (AST) node definitions for SOA DSL.

These classes represent the parsed structure of SOA rules.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union


@dataclass
class GlobalConfig:
    """Global configuration parameters."""
    timing: Dict[str, Any] = field(default_factory=dict)
    temperature: Dict[str, Any] = field(default_factory=dict)
    tmaxfrac: Dict[str, float] = field(default_factory=dict)
    limits: Dict[str, Union[float, str]] = field(default_factory=dict)
    
    def get_limit(self, name: str) -> Union[float, str, None]:
        """Get a limit value by name."""
        return self.limits.get(name)
    
    def get_tmaxfrac(self, level: int) -> float:
        """Get tmaxfrac value for a given level."""
        return self.tmaxfrac.get(f"level{level}", 0.0)


@dataclass
class Constraint:
    """Represents a constraint (voltage, current, etc.)."""
    vhigh: Optional[Union[float, str]] = None
    vlow: Optional[Union[float, str]] = None
    ihigh: Optional[Union[float, str]] = None
    ilow: Optional[Union[float, str]] = None
    vhigh_on: Optional[Union[float, str]] = None
    vhigh_off: Optional[Union[float, str]] = None
    vlow_on: Optional[Union[float, str]] = None
    vlow_off: Optional[Union[float, str]] = None
    
    def has_voltage(self) -> bool:
        """Check if constraint has voltage limits."""
        return any([self.vhigh, self.vlow, self.vhigh_on, self.vhigh_off])
    
    def has_current(self) -> bool:
        """Check if constraint has current limits."""
        return any([self.ihigh, self.ilow])
    
    def is_state_dependent(self) -> bool:
        """Check if constraint is state-dependent (on/off)."""
        return any([self.vhigh_on, self.vhigh_off, self.vlow_on, self.vlow_off])


@dataclass
class Branch:
    """Represents a voltage/current branch to monitor."""
    branch: str
    vhigh: Optional[Union[float, str]] = None
    vlow: Optional[Union[float, str]] = None
    message: Optional[str] = None


@dataclass
class GateControl:
    """Gate control parameters for MOS devices."""
    vhigh_gc: Union[float, str] = 0.0
    vlow_gc: Union[float, str] = 0.0


@dataclass
class GateBulk:
    """Gate-bulk parameters for MOS devices."""
    vhigh_gb_on: Union[float, str] = 0.0
    vlow_gb_on: Union[float, str] = 0.0


@dataclass
class Junction:
    """Junction parameters for MOS devices."""
    vfwd_jun_on: Union[float, str] = 0.0
    vrev_jun_on: Union[float, str] = 0.0
    vfwd_jun_off: Union[float, str] = 0.0
    vrev_jun_off: Union[float, str] = 0.0


@dataclass
class MonitorParams:
    """Monitor-specific parameters."""
    param: str = "vth"
    vgt: float = 0.0
    pmosvthsign: int = 1
    inst2probe: str = "fet"


@dataclass
class Messages:
    """Message strings for different branches."""
    vds: Optional[str] = None
    vgs: Optional[str] = None
    vgd: Optional[str] = None
    vgb: Optional[str] = None
    vsb: Optional[str] = None
    vdb: Optional[str] = None


@dataclass
class AgingCheck:
    """Aging reliability check parameters."""
    type: str = ""
    variant: str = ""
    params: Dict[str, float] = field(default_factory=dict)


@dataclass
class SelfHeating:
    """Self-heating monitor parameters."""
    dtmax: Union[float, str] = 0.0
    theat: Union[float, str] = 0.0
    monitor: str = "shmonitor_nofeedback"


@dataclass
class CurrentConstraint:
    """Individual current constraint for resistors."""
    name: str
    type: str  # idc, ipeak, irms
    ihigh: Union[float, str]
    message: str = ""


@dataclass
class SOARule:
    """Represents a complete SOA rule."""
    name: str
    device: str
    parameter: str
    type: str
    severity: str
    description: str = ""
    condition: Optional[str] = None
    
    # Constraints
    constraint: Optional[Constraint] = None
    tmaxfrac: Dict[str, float] = field(default_factory=dict)
    
    # Multi-branch
    branches: List[Branch] = field(default_factory=list)
    connections: Optional[str] = None
    
    # MOS-specific
    gate_control: Optional[GateControl] = None
    gate_bulk: Optional[GateBulk] = None
    junction: Optional[Junction] = None
    monitor_params: Optional[MonitorParams] = None
    messages: Optional[Messages] = None
    
    # Aging
    aging_check: Optional[AgingCheck] = None
    
    # Resistor-specific
    constraints: List[CurrentConstraint] = field(default_factory=list)
    self_heating: Optional[SelfHeating] = None
    device_params: Dict[str, Union[float, str]] = field(default_factory=dict)
    
    def is_multi_level(self) -> bool:
        """Check if rule has multiple tmaxfrac levels."""
        return len(self.tmaxfrac) > 0
    
    def is_multi_branch(self) -> bool:
        """Check if rule monitors multiple branches."""
        return len(self.branches) > 0
    
    def is_state_dependent(self) -> bool:
        """Check if rule is state-dependent."""
        return self.type == "state_dependent" or (
            self.constraint and self.constraint.is_state_dependent()
        )
    
    def is_current_with_heating(self) -> bool:
        """Check if rule is current monitoring with self-heating."""
        return self.type == "current_with_heating"
    
    def has_aging_check(self) -> bool:
        """Check if rule has aging reliability check."""
        return self.aging_check is not None
    
    def get_monitor_type(self) -> str:
        """Determine the appropriate Verilog-A monitor type."""
        if self.is_state_dependent():
            return "ovcheckva_mos2"
        elif self.is_multi_branch():
            return "ovcheck6"
        elif self.is_current_with_heating():
            return "ovcheck"  # Multiple instances
        elif self.type == "parameter":
            return "parcheck3"
        elif self.type == "pwl":
            return "ovcheck_pwl"
        elif self.has_aging_check():
            return "ovcheck_ldmos_hci_tddb"
        else:
            return "ovcheck"


@dataclass
class SOADocument:
    """Top-level document containing all SOA rules and configuration."""
    version: str
    process: str
    date: str
    global_config: GlobalConfig
    rules: List[SOARule] = field(default_factory=list)
    
    def get_rules_by_device(self, device: str) -> List[SOARule]:
        """Get all rules for a specific device."""
        return [rule for rule in self.rules if rule.device == device]
    
    def get_rules_by_severity(self, severity: str) -> List[SOARule]:
        """Get all rules with a specific severity."""
        return [rule for rule in self.rules if rule.severity == severity]
    
    def get_devices(self) -> List[str]:
        """Get list of all unique devices."""
        return list(set(rule.device for rule in self.rules))
