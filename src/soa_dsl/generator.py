"""
SOA Code Generator - Monitor-Based
Generates Spectre netlist code from monitor-based YAML.
"""

from typing import List, TextIO
from .parser import SOADocument, Monitor


class CodeGenerator:
    """Generates Spectre code from SOA specification."""
    
    def __init__(self, document: SOADocument):
        self.document = document
    
    def generate(self, output_file: TextIO):
        """Generate complete Spectre code."""
        self._write_header(output_file)
        self._write_base_section(output_file)
        self._write_monitors(output_file)
    
    def _write_header(self, f: TextIO):
        """Write file header."""
        f.write("simulator lang=spectre\n")
        f.write(f"// Generated from SOA DSL\n")
        f.write(f"// Process: {self.document.process}\n")
        f.write(f"// Date: {self.document.date}\n")
        f.write("\n")
    
    def _write_base_section(self, f: TextIO):
        """Write base section with Verilog-A includes and parameters."""
        f.write("section base\n\n")
        f.write('ahdl_include "./veriloga/ovcheck_mos_alt.va"\n')
        f.write('ahdl_include "./veriloga/ovcheck_pwl_alt.va"\n')
        f.write('ahdl_include "./veriloga/ovcheck_ldmos_hci_tddb_alt.va"\n')
        f.write('ahdl_include "./veriloga/parcheck3.va"\n')
        f.write('ahdl_include "./veriloga/selfheating_monitor_nofeedback.va"\n\n')
        
        # Write parameters if defined in global config
        if hasattr(self.document, 'parameters') and self.document.parameters:
            f.write("parameters\n")
            for key, value in self.document.parameters.items():
                f.write(f"+ {key} = {value}\n")
            f.write("\n")
        
        f.write("endsection base\n\n")
    
    def _write_monitors(self, f: TextIO):
        """Write all monitor definitions."""
        for monitor in self.document.monitors:
            self._write_monitor(f, monitor)
            f.write("\n")
    
    def _write_monitor(self, f: TextIO, monitor: Monitor):
        """Write a single monitor definition."""
        f.write(f"section {monitor.section}\n")
        f.write(f"model {monitor.model_name} {monitor.monitor_type}\n")
        
        # Write common parameters
        params = monitor.parameters
        f.write(f"+ tmin={params.tmin} tdelay={params.tdelay} ")
        f.write(f"vballmsg={params.vballmsg} stop={params.stop}\n")
        
        # Write tmaxfrac if present
        if params.tmaxfrac:
            f.write(f"+ tmaxfrac={params.tmaxfrac}\n")
        
        # Write monitor-specific parameters
        if monitor.monitor_type == 'ovcheck':
            self._write_ovcheck_params(f, monitor)
        elif monitor.monitor_type == 'ovcheck6':
            self._write_ovcheck6_params(f, monitor)
        elif monitor.monitor_type == 'ovcheckva_mos2':
            self._write_mos2_params(f, monitor)
        elif monitor.monitor_type == 'ovcheckva_pwl':
            self._write_pwl_params(f, monitor)
        elif monitor.monitor_type == 'ovcheckva_ldmos_hci_tddb':
            self._write_hci_tddb_params(f, monitor)
        elif monitor.monitor_type == 'parcheckva3':
            self._write_parcheck_params(f, monitor)
        
        f.write(f"endsection {monitor.section}\n")
    
    def _write_ovcheck_params(self, f: TextIO, monitor: Monitor):
        """Write ovcheck monitor parameters."""
        extra = monitor.parameters.extra
        
        # Single branch parameters
        if 'vlow' in extra:
            f.write(f"+ vlow={self._format_value(extra['vlow'])}")
        if 'vhigh' in extra:
            f.write(f" vhigh={self._format_value(extra['vhigh'])}")
        if 'branch1' in extra:
            f.write(f' branch1="{extra["branch1"]}"')
        if 'message1' in extra:
            f.write(f' message1="{extra["message1"]}"')
        f.write("\n")
        
        # Self-heating parameters
        if monitor.self_heating:
            sh = monitor.self_heating
            if 'dtmax' in sh:
                f.write(f"+ dtmax={sh['dtmax']}")
            if 'theat' in sh:
                f.write(f" theat={sh['theat']}")
            if 'monitor' in sh:
                f.write(f" monitor={sh['monitor']}")
            f.write("\n")
        
        # Current constraints for self-heating
        if monitor.constraints:
            for constraint in monitor.constraints:
                ctype = constraint.get('type', '')
                model = constraint.get('model', '')
                ihigh = constraint.get('ihigh', '')
                if ctype and model and ihigh:
                    f.write(f"+ {ctype}_high={self._format_value(ihigh)}\n")
    
    def _write_ovcheck6_params(self, f: TextIO, monitor: Monitor):
        """Write ovcheck6 (multi-branch) parameters."""
        if monitor.branches:
            for i, branch in enumerate(monitor.branches, 1):
                vlow = branch.get('vlow')
                vhigh = branch.get('vhigh')
                branch_name = branch.get('branch')
                message = branch.get('message')
                
                f.write(f"+ vlow{i}={self._format_value(vlow)}")
                f.write(f" vhigh{i}={self._format_value(vhigh)}")
                f.write(f' branch{i}="{branch_name}"')
                f.write(f' message{i}="{message}"\n')
    
    def _write_mos2_params(self, f: TextIO, monitor: Monitor):
        """Write ovcheckva_mos2 parameters."""
        extra = monitor.parameters.extra
        
        # State-dependent limits
        if 'vhigh_on' in extra:
            f.write(f"+ vhigh_on={self._format_value(extra['vhigh_on'])}\n")
        if 'vhigh_off' in extra:
            f.write(f"+ vhigh_off={self._format_value(extra['vhigh_off'])}\n")
        
        # Gate control
        if monitor.gate_control:
            gc = monitor.gate_control
            if 'vhigh_gc' in gc:
                f.write(f"+ vhigh_gc={self._format_value(gc['vhigh_gc'])}\n")
            if 'vlow_gc' in gc:
                f.write(f"+ vlow_gc={self._format_value(gc['vlow_gc'])}\n")
        
        # Monitor parameters
        if monitor.monitor_params:
            mp = monitor.monitor_params
            if 'param' in mp:
                f.write(f'+ param="{mp["param"]}"\n')
            if 'vgt' in mp:
                f.write(f"+ vgt={self._format_value(mp['vgt'])}\n")
    
    def _write_pwl_params(self, f: TextIO, monitor: Monitor):
        """Write ovcheckva_pwl parameters."""
        extra = monitor.parameters.extra
        
        if 'vlow' in extra:
            f.write(f'+ vlow="{extra["vlow"]}"\n')
        if 'vhigh' in extra:
            f.write(f'+ vhigh="{extra["vhigh"]}"\n')
        if 'branch1' in extra:
            f.write(f'+ branch1="{extra["branch1"]}"\n')
        if 'message1' in extra:
            f.write(f'+ message1="{extra["message1"]}"\n')
    
    def _write_hci_tddb_params(self, f: TextIO, monitor: Monitor):
        """Write HCI/TDDB aging parameters."""
        extra = monitor.parameters.extra
        
        if 'atype' in extra:
            f.write(f"+ atype={extra['atype']}\n")
        
        if monitor.hci_tddb_params:
            params = monitor.hci_tddb_params
            for key, value in params.items():
                f.write(f"+ {key}={self._format_value(value)}\n")
    
    def _write_parcheck_params(self, f: TextIO, monitor: Monitor):
        """Write parcheckva3 parameters."""
        extra = monitor.parameters.extra
        
        if 'param' in extra:
            f.write(f'+ param="{extra["param"]}"\n')
        if 'vgt' in extra:
            f.write(f"+ vgt={self._format_value(extra['vgt'])}\n")
        if 'vlow' in extra:
            f.write(f"+ vlow={self._format_value(extra['vlow'])}\n")
        if 'vhigh' in extra:
            f.write(f"+ vhigh={self._format_value(extra['vhigh'])}\n")
    
    def _format_value(self, value) -> str:
        """Format a value for Spectre output."""
        if isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            # If it's an expression or reference, return as-is
            # If it's a simple number string, return as-is
            # Otherwise, it should already be quoted if needed
            return value
        else:
            return str(value)


def generate_code(document: SOADocument, output_file: TextIO):
    """Convenience function to generate code."""
    generator = CodeGenerator(document)
    generator.generate(output_file)
