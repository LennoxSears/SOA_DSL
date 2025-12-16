"""
SOA DSL - Safe Operating Area Domain-Specific Language

Monitor-based specification for Spectre SOA checking.
Direct mapping to Verilog-A monitor implementations.
"""

__version__ = "1.0.0"
__author__ = "SOA DSL Team"

from .parser import parse_file, SOADocument, Monitor, ParseError
from .generator import generate_code, CodeGenerator

__all__ = [
    "parse_file",
    "generate_code",
    "SOADocument",
    "Monitor",
    "ParseError",
    "CodeGenerator",
]
