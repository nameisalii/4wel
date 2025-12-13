#!/usr/bin/env python3
"""
Convert existing JSON MCAP files to proper binary MCAP format for Foxglove Studio
"""

import sys
from pathlib import Path
from mcap_writer import convert_json_to_mcap

def main():
    print("=" * 60)
    print("Converting JSON MCAP files to Binary MCAP format")
    print("=" * 60)
    print()
    
    # Files to convert
    files_to_convert = [
        ('deliverables/single_robot_training.mcap.json', 'deliverables/single_robot_training.mcap'),
        ('training.json', 'single_robot_training.mcap'),
    ]
    
    # Check for multi-robot files
    multi_robot_json = Path('multi_robot_training.mcap.json')
    if multi_robot_json.exists():
        files_to_convert.append(
            ('multi_robot_training.mcap.json', 'multi_robot_training.mcap')
        )
    
    converted_files = []
    
    for json_file, mcap_file in files_to_convert:
        json_path = Path(json_file)
        mcap_path = Path(mcap_file)
        
        if not json_path.exists():
            print(f"⚠️  Skipping {json_file} (not found)")
            continue
        
        print(f"\n📦 Converting: {json_file}")
        print(f"   Output: {mcap_file}")
        
        result = convert_json_to_mcap(str(json_path), str(mcap_path))
        
        if result:
            converted_files.append(result)
            # Also copy to deliverables if not already there
            if 'deliverables' not in str(mcap_path):
                deliverables_path = Path('deliverables') / mcap_path.name
                deliverables_path.parent.mkdir(exist_ok=True)
                import shutil
                shutil.copy2(mcap_path, deliverables_path)
                print(f"   ✅ Also copied to: {deliverables_path}")
    
    print("\n" + "=" * 60)
    if converted_files:
        print("✅ Conversion Complete!")
        print("\nConverted files:")
        for f in converted_files:
            size_mb = Path(f).stat().st_size / (1024 * 1024)
            print(f"  ✅ {f} ({size_mb:.2f} MB)")
        print("\nThese binary MCAP files can now be opened in Foxglove Studio!")
    else:
        print("⚠️  No files were converted.")
        print("   Make sure the JSON MCAP files exist.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()


