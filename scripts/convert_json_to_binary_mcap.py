#!/usr/bin/env python3
"""
Convert JSON MCAP files to binary MCAP format for Foxglove Studio
Uses the working MCAP writer API
"""

import sys
from pathlib import Path
from mcap_writer import convert_json_to_mcap

def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_json_to_binary_mcap.py <input.json> [output.mcap]")
        print("\nOr run prepare_foxglove_deliverables.py to convert all files")
        sys.exit(1)
    
    json_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_mcap = sys.argv[2]
    else:
        output_mcap = Path(json_file).with_suffix('.mcap')
    
    print(f"Converting {json_file} to binary MCAP...")
    result = convert_json_to_mcap(json_file, str(output_mcap))
    
    if result:
        print(f"\n✅ Success! Binary MCAP file: {result}")
        print("   You can now open this file in Foxglove Studio!")
    else:
        print("\n❌ Conversion failed. Check the error messages above.")

if __name__ == "__main__":
    main()


