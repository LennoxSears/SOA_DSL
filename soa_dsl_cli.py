#!/usr/bin/env python3
"""
SOA DSL Command-Line Interface
Universal and monitor-based specification for Spectre SOA checking.
"""

import sys
import argparse
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from soa_dsl.parser import parse_file, ParseError
from soa_dsl.generator import generate_code
from soa_dsl.converter import convert_universal_to_monitor, ConversionError


def main():
    parser = argparse.ArgumentParser(
        description='SOA DSL - Universal and monitor-based specification compiler',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert universal spec to monitor spec
  %(prog)s convert examples/soa_rules_universal.yaml -o output/monitors.yaml
  
  # Generate Spectre from monitor spec
  %(prog)s generate examples/soa_monitors.yaml -o output/soachecks.scs
  
  # One-step: universal spec to Spectre
  %(prog)s compile examples/soa_rules_universal.yaml -o output/soachecks.scs
  
  # Validate monitor spec
  %(prog)s validate examples/soa_monitors.yaml
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Convert command: universal → monitor
    convert_parser = subparsers.add_parser(
        'convert',
        help='Convert universal spec to monitor spec'
    )
    convert_parser.add_argument(
        'input',
        type=Path,
        help='Input universal YAML file'
    )
    convert_parser.add_argument(
        '-o', '--output',
        type=Path,
        required=True,
        help='Output monitor YAML file'
    )
    convert_parser.add_argument(
        '--device-lib',
        type=Path,
        default=Path('config/device_library.yaml'),
        help='Device library YAML (default: config/device_library.yaml)'
    )
    convert_parser.add_argument(
        '--monitor-lib',
        type=Path,
        default=Path('config/monitor_library.yaml'),
        help='Monitor library YAML (default: config/monitor_library.yaml)'
    )
    
    # Generate command: monitor → Spectre
    generate_parser = subparsers.add_parser(
        'generate',
        help='Generate Spectre code from monitor spec'
    )
    generate_parser.add_argument(
        'input',
        type=Path,
        help='Input monitor YAML file'
    )
    generate_parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output Spectre file (default: stdout)'
    )
    
    # Compile command: universal → Spectre (one-step)
    compile_parser = subparsers.add_parser(
        'compile',
        help='Compile universal spec directly to Spectre (one-step)'
    )
    compile_parser.add_argument(
        'input',
        type=Path,
        help='Input universal YAML file'
    )
    compile_parser.add_argument(
        '-o', '--output',
        type=Path,
        required=True,
        help='Output Spectre file'
    )
    compile_parser.add_argument(
        '--device-lib',
        type=Path,
        default=Path('config/device_library.yaml'),
        help='Device library YAML (default: config/device_library.yaml)'
    )
    compile_parser.add_argument(
        '--monitor-lib',
        type=Path,
        default=Path('config/monitor_library.yaml'),
        help='Monitor library YAML (default: config/monitor_library.yaml)'
    )
    
    # Validate command
    validate_parser = subparsers.add_parser(
        'validate',
        help='Validate monitor spec'
    )
    validate_parser.add_argument(
        'input',
        type=Path,
        help='Input monitor YAML file'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'convert':
            return cmd_convert(args)
        elif args.command == 'generate':
            return cmd_generate(args)
        elif args.command == 'compile':
            return cmd_compile(args)
        elif args.command == 'validate':
            return cmd_validate(args)
        
    except (ParseError, ConversionError) as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def cmd_convert(args):
    """Convert universal spec to monitor spec."""
    print(f"Converting {args.input} → {args.output}")
    
    convert_universal_to_monitor(
        args.input,
        args.device_lib,
        args.monitor_lib,
        args.output
    )
    
    print(f"✅ Converted to {args.output}")
    return 0


def cmd_generate(args):
    """Generate Spectre code from monitor spec."""
    doc = parse_file(args.input)
    
    if args.output:
        with open(args.output, 'w') as f:
            generate_code(doc, f)
        print(f"✅ Generated {args.output}")
    else:
        generate_code(doc, sys.stdout)
    
    return 0


def cmd_compile(args):
    """Compile universal spec directly to Spectre (one-step)."""
    import tempfile
    
    print(f"Compiling {args.input} → {args.output}")
    
    # Step 1: Convert to monitor spec (temporary)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp:
        tmp_path = Path(tmp.name)
    
    try:
        print("  Step 1: Converting to monitor spec...")
        convert_universal_to_monitor(
            args.input,
            args.device_lib,
            args.monitor_lib,
            tmp_path
        )
        
        # Step 2: Generate Spectre code
        print("  Step 2: Generating Spectre code...")
        doc = parse_file(tmp_path)
        with open(args.output, 'w') as f:
            generate_code(doc, f)
        
        print(f"✅ Compiled to {args.output}")
        return 0
        
    finally:
        # Clean up temporary file
        if tmp_path.exists():
            tmp_path.unlink()


def cmd_validate(args):
    """Validate monitor spec."""
    doc = parse_file(args.input)
    
    print(f"✅ Validation successful")
    print(f"   Process: {doc.process}")
    print(f"   Monitors: {len(doc.monitors)}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
