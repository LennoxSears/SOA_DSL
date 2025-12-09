"""
SOA DSL - Safe Operating Area Domain-Specific Language

A comprehensive toolchain for parsing, validating, and generating
Spectre netlist code from SOA rule specifications.
"""

__version__ = "1.0.0"
__author__ = "SOA DSL Team"

from .parser import SOAParser, parse_file
from .validator import SOAValidator
from .generator import SpectreGenerator
from .ast_nodes import SOARule, GlobalConfig, Constraint

__all__ = [
    "SOAParser",
    "parse_file",
    "SOAValidator",
    "SpectreGenerator",
    "SOARule",
    "GlobalConfig",
    "Constraint",
]
