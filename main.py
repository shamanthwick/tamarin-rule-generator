#!/usr/bin/env python3
"""
Tamarin Rule Generator - CLI
Command-line interface for generating Tamarin models from protocol diagrams.
"""

import argparse
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.generator import TamarinGenerator, generate_from_file


def main():
    parser = argparse.ArgumentParser(
        description="Generate Tamarin rules from protocol sequence diagrams",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s examples/digilocker_aadhar.json -o output/digilocker.spthy
  %(prog)s protocol.json --summary
  %(prog)s protocol.json --output model.spthy --no-comments
        """
    )
    
    parser.add_argument(
        "input",
        help="Input JSON file with protocol definition"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output .spthy file (default: output/<protocol_name>.spthy)"
    )
    
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print protocol summary only, don't generate file"
    )
    
    parser.add_argument(
        "--no-comments",
        action="store_true",
        help="Generate without detailed comments"
    )
    
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate input, don't generate"
    )
    
    args = parser.parse_args()
    
    # Check input file exists
    if not os.path.exists(args.input):
        print(f"❌ Error: Input file not found: {args.input}")
        sys.exit(1)
    
    # Create generator
    generator = TamarinGenerator()
    
    try:
        protocol = generator.load_protocol(args.input)
    except Exception as e:
        print(f"❌ Error loading protocol: {e}")
        sys.exit(1)
    
    # Validate only
    if args.validate_only:
        print("✅ Protocol validation successful")
        sys.exit(0)
    
    # Print summary
    print(generator.summary())
    
    if args.summary:
        sys.exit(0)
    
    # Determine output path
    output_path = args.output
    if not output_path:
        output_dir = os.path.join(os.path.dirname(__file__), 'output')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(
            output_dir,
            f"{protocol.name}.spthy"
        )
    
    # Generate
    try:
        if args.no_comments:
            content = generator.generate()
        else:
            content = generator.generate_with_comments()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Generated: {output_path}")
        
    except Exception as e:
        print(f"❌ Error generating model: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
