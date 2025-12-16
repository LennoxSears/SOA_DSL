#!/usr/bin/env python3
"""
SOA DSL Command-Line Interface
Monitor-based specification for Spectre SOA checking.
"""

import sys
import argparse
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from soa_dsl.parser import parse_file, ParseError
from soa_dsl.generator import generate_code


def main():
    parser = argparse.ArgumentParser(
        description='SOA DSL - Monitor-based specification compiler'
    )
    parser.add_argument(
        'input',
        type=Path,
        help='Input YAML file with monitor specifications'
    )
    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output Spectre file (default: stdout)'
    )
    parser.add_argument(
        '-v', '--validate',
        action='store_true',
        help='Validate only, do not generate code'
    )
    
    args = parser.parse_args()
    
    try:
        # Parse input file
        doc = parse_file(args.input)
        
        if args.validate:
            print(f"✅ Validation successful")
            print(f"   Process: {doc.process}")
            print(f"   Monitors: {len(doc.monitors)}")
            return 0
        
        # Generate code
        if args.output:
            with open(args.output, 'w') as f:
                generate_code(doc, f)
            print(f"✅ Generated {args.output}")
        else:
            generate_code(doc, sys.stdout)
        
        return 0
        
    except ParseError as e:
        print(f"❌ Parse error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
