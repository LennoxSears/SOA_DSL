"""
Spectre Code Generator for SOA DSL.

Generates Spectre netlist code from validated AST.
"""

from typing import List, Dict, Any, TextIO
from .ast_nodes import SOADocument, SOARule, GlobalConfig
from .expression import ExpressionEvaluator


class SpectreGenerator:
    """Generates Spectre netlist code from SOA rules."""
    
    def __init__(self):
        self.evaluator = ExpressionEvaluator()
        self.indent = "    "
    
    def generate(self, document: SOADocument, output_file: str):
        """Generate Spectre code and write to file."""
        with open(output_file, 'w') as f:
            self._write_header(f, document)
            self._write_global_section(f, document.global_config)
            self._write_rules(f, document)
    
    def _write_header(self, f: TextIO, doc: SOADocument):
        """Write file header."""
        f.write("simulator lang=spectre\n")
        f.write(f"// Generated from SOA DSL\n")
        f.write(f"// Process: {doc.process}\n")
        f.write(f"// Version: {doc.version}\n")
        f.write(f"// Date: {doc.date}\n\n")
    
    def _write_global_section(self, f: TextIO, config: GlobalConfig):
        """Write global parameters section."""
        f.write("section base\n\n")
        f.write("parameters\n")
        
        # Timing parameters
        timing = config.timing
        f.write(f"+ global_tmin      = {timing.get('tmin', 0)}\n")
        f.write(f"+ global_tdelay    = {timing.get('tdelay', 0)}\n")
        f.write(f"+ global_vballmsg  = {timing.get('vballmsg', 1.0)}\n")
        f.write(f"+ global_stop      = {timing.get('stop', 0)}\n")
        
        # Temperature
        temp = config.temperature
        f.write(f"+ tcelsius0        = {temp.get('tcelsius0', 273.15)}\n")
        f.write(f"+ tref_soa         = {temp.get('tref_soa', 25)}\n\n")
        
        # tmaxfrac levels
        tmaxfrac = config.tmaxfrac
        f.write("// duration limits\n")
        f.write(f"+ tmaxfrac0 = {tmaxfrac.get('level0', 0)}\n")
        f.write(f"+ tmaxfrac1 = {tmaxfrac.get('level1', 0.01)}\n")
        f.write(f"+ tmaxfrac2 = {tmaxfrac.get('level2', 0.10)}\n")
        f.write(f"+ tmaxfrac3 = {tmaxfrac.get('level3', -1)}\n\n")
        
        # Limits
        f.write("// SOA limits\n")
        for name, value in config.limits.items():
            f.write(f"+ {name} = {value}\n")
        
        f.write("\nendsection base\n\n")
    
    def _write_rules(self, f: TextIO, doc: SOADocument):
        """Write all rules grouped by device."""
        devices = doc.get_devices()
        
        for device in sorted(devices):
            rules = doc.get_rules_by_device(device)
            self._write_device_section(f, device, rules, doc.global_config)
    
    def _write_device_section(self, f: TextIO, device: str, 
                              rules: List[SOARule], config: GlobalConfig):
        """Write section for a specific device."""
        f.write(f"section {device}_soa\n")
        
        for rule in rules:
            self._write_rule(f, rule, config)
        
        f.write(f"endsection {device}_soa\n\n")
    
    def _write_rule(self, f: TextIO, rule: SOARule, config: GlobalConfig):
        """Write a single rule."""
        f.write(f"// Rule: {rule.name}\n")
        if rule.description:
            f.write(f"// {rule.description}\n")
        
        # Handle different rule types
        if rule.is_multi_level():
            self._write_multi_level_rule(f, rule)
        elif rule.is_state_dependent():
            self._write_state_dependent_rule(f, rule)
        elif rule.is_multi_branch():
            self._write_multi_branch_rule(f, rule)
        else:
            self._write_simple_rule(f, rule)
        
        f.write("\n")
    
    def _write_simple_rule(self, f: TextIO, rule: SOARule):
        """Write simple voltage/current check."""
        model_name = f"ovcheck_{rule.name.replace(' ', '_')}"
        
        f.write(f"model {model_name} ovcheck\n")
        f.write(f"+ tmin=global_tmin tdelay=global_tdelay\n")
        f.write(f"+ vballmsg=global_vballmsg stop=global_stop\n")
        f.write(f"+ tmaxfrac=tmaxfrac0\n")
        
        if rule.constraint:
            vhigh = rule.constraint.vhigh or 999.0
            vlow = rule.constraint.vlow or -999.0
            f.write(f"+ vlow={vlow} vhigh={vhigh}\n")
            f.write(f"+ branch1=\"{rule.parameter}\"\n")
        
        f.write("\n")
    
    def _write_multi_level_rule(self, f: TextIO, rule: SOARule):
        """Write multi-level rule with tmaxfrac."""
        levels = sorted([(float(k), v) for k, v in rule.tmaxfrac.items()])
        
        for i, (frac, value) in enumerate(levels):
            f.write(f"model ovcheck_{i} ovcheck\n")
            f.write(f"+ tmin=global_tmin tdelay=global_tdelay\n")
            f.write(f"+ vballmsg=global_vballmsg stop=global_stop\n")
            f.write(f"+ tmaxfrac=tmaxfrac{i}\n")
            f.write(f"+ vlow=-999.0 vhigh={value}\n")
            f.write(f"+ branch1=\"{rule.parameter}\"\n\n")
    
    def _write_state_dependent_rule(self, f: TextIO, rule: SOARule):
        """Write MOS state-dependent rule."""
        f.write(f"model ovcheck_0 ovcheckva_mos2\n")
        f.write(f"+ tmin=global_tmin tdelay=global_tdelay\n")
        f.write(f"+ vballmsg=global_vballmsg stop=global_stop\n")
        f.write(f"+ tmaxfrac=tmaxfrac0\n")
        
        if rule.constraint:
            if rule.constraint.vhigh_on:
                f.write(f"+ vhigh_ds_on={rule.constraint.vhigh_on}\n")
            if rule.constraint.vhigh_off:
                f.write(f"+ vhigh_ds_off={rule.constraint.vhigh_off}\n")
        
        if rule.gate_control:
            f.write(f"+ vhigh_gc={rule.gate_control.vhigh_gc}\n")
            f.write(f"+ vlow_gc={rule.gate_control.vlow_gc}\n")
        
        f.write(f"+ param=\"vth\" device=device\n\n")
    
    def _write_multi_branch_rule(self, f: TextIO, rule: SOARule):
        """Write multi-branch rule."""
        f.write(f"model ovcheck_1 ovcheck6\n")
        f.write(f"+ tmin=global_tmin tdelay=global_tdelay\n")
        f.write(f"+ vballmsg=global_vballmsg stop=global_stop\n")
        f.write(f"+ tmaxfrac=tmaxfrac0\n")
        
        for i, branch in enumerate(rule.branches[:6], 1):
            vhigh = branch.vhigh or 999.0
            vlow = branch.vlow or -999.0
            f.write(f"+ vlow{i}={vlow} vhigh{i}={vhigh}\n")
            f.write(f"+ branch{i}=\"{branch.branch}\"\n")
        
        f.write("\n")
