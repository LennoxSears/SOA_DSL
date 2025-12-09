#!/usr/bin/env python3
"""
SOA DSL Command-Line Interface Entry Point

This script can be run directly without package installation.
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run CLI
from soa_dsl.cli import main

if __name__ == '__main__':
    sys.exit(main())
