"""
Command-line interface for SOA DSL toolchain.
"""

import argparse
import sys
from pathlib import Path

from .parser import parse_file, ParseError
from .validator import SOAValidator
from .generator import SpectreGenerator


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SOA DSL - Safe Operating Area Domain-Specific Language Toolchain",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate a DSL file
  soa-dsl validate rules.yaml
  
  # Generate Spectre code
  soa-dsl generate rules.yaml -o soachecks_top.scs
  
  # Validate and generate
  soa-dsl compile rules.yaml -o soachecks_top.scs
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate YAML DSL file')
    validate_parser.add_argument('input', help='Input YAML file (.yaml or .yml)')
    validate_parser.add_argument('--strict', action='store_true', 
                                help='Treat warnings as errors')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate Spectre code')
    generate_parser.add_argument('input', help='Input YAML file')
    generate_parser.add_argument('-o', '--output', required=True,
                                help='Output Spectre file')
    generate_parser.add_argument('--no-validate', action='store_true',
                                help='Skip validation')
    
    # Compile command (validate + generate)
    compile_parser = subparsers.add_parser('compile', 
                                          help='Validate and generate (default)')
    compile_parser.add_argument('input', help='Input YAML file')
    compile_parser.add_argument('-o', '--output', required=True,
                               help='Output Spectre file')
    compile_parser.add_argument('--strict', action='store_true',
                               help='Treat warnings as errors')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'validate':
            return cmd_validate(args)
        elif args.command == 'generate':
            return cmd_generate(args)
        elif args.command == 'compile':
            return cmd_compile(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


def cmd_validate(args):
    """Validate command."""
    print(f"Validating {args.input}...")
    
    try:
        # Parse
        document = parse_file(args.input)
        print(f"✅ Parsed successfully ({len(document.rules)} rules)")
        
        # Validate
        validator = SOAValidator(strict=args.strict)
        is_valid = validator.validate(document)
        
        validator.print_report()
        
        if is_valid:
            print(f"\n✅ Validation passed")
            return 0
        else:
            print(f"\n❌ Validation failed")
            return 1
    
    except ParseError as e:
        print(f"❌ Parse error: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print(f"❌ {e}", file=sys.stderr)
        return 1


def cmd_generate(args):
    """Generate command."""
    print(f"Generating Spectre code from {args.input}...")
    
    try:
        # Parse
        document = parse_file(args.input)
        print(f"✅ Parsed successfully ({len(document.rules)} rules)")
        
        # Validate (unless skipped)
        if not args.no_validate:
            validator = SOAValidator(strict=False)
            is_valid = validator.validate(document)
            
            if not is_valid:
                print("⚠️  Validation errors found, but continuing...")
                validator.print_report()
        
        # Generate
        generator = SpectreGenerator()
        generator.generate(document, args.output)
        
        print(f"✅ Generated {args.output}")
        return 0
    
    except ParseError as e:
        print(f"❌ Parse error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Generation error: {e}", file=sys.stderr)
        return 1


def cmd_compile(args):
    """Compile command (validate + generate)."""
    print(f"Compiling {args.input}...")
    
    try:
        # Parse
        document = parse_file(args.input)
        print(f"✅ Parsed successfully ({len(document.rules)} rules)")
        
        # Validate
        validator = SOAValidator(strict=args.strict)
        is_valid = validator.validate(document)
        
        validator.print_report()
        
        if not is_valid:
            print(f"\n❌ Validation failed, aborting generation")
            return 1
        
        # Generate
        generator = SpectreGenerator()
        generator.generate(document, args.output)
        
        print(f"\n✅ Successfully compiled to {args.output}")
        return 0
    
    except ParseError as e:
        print(f"❌ Parse error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
