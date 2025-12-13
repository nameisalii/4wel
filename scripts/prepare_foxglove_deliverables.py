#!/usr/bin/env python3
"""
Prepare deliverables for lead: Convert to binary MCAP format and organize
"""

import sys
from pathlib import Path
import shutil
from mcap_writer import convert_json_to_mcap

def main():
    print("=" * 60)
    print("Preparing Foxglove-Compatible MCAP Deliverables")
    print("=" * 60)
    print()
    print("Converting JSON MCAP files to binary MCAP format for Foxglove Studio...")
    print()
    
    deliverables_dir = Path('deliverables')
    deliverables_dir.mkdir(exist_ok=True)
    
    converted_files = []
    
    # 1. Convert single-robot MCAP
    print("1️⃣  Single-Robot Training MCAP")
    print("-" * 60)
    
    single_json = Path('deliverables/single_robot_training.mcap.json')
    if not single_json.exists():
        single_json = Path('training.json')
    
    if single_json.exists():
        output_mcap = deliverables_dir / 'single_robot_training.mcap'
        print(f"   Converting: {single_json.name}")
        print(f"   This may take a while for large files...")
        result = convert_json_to_mcap(str(single_json), str(output_mcap))
        if result:
            converted_files.append(('Single-Robot', result))
    else:
        print("   ⚠️  Single-robot MCAP JSON not found")
    
    # 2. Convert multi-robot MCAP
    print("\n2️⃣  Multi-Robot Training MCAP")
    print("-" * 60)
    
    multi_json = Path('multi_robot_training.mcap.json')
    if multi_json.exists():
        output_mcap = deliverables_dir / 'multi_robot_training.mcap'
        print(f"   Converting: {multi_json.name}")
        result = convert_json_to_mcap(str(multi_json), str(output_mcap))
        if result:
            converted_files.append(('Multi-Robot', result))
    else:
        print("   ⚠️  Multi-robot MCAP JSON not found")
        print("   💡 To generate multi-robot MCAP, run:")
        print("      python train.py --mode multi --episodes 20000 --num_robots 3 \\")
        print("          --record --mcap_output multi_robot_training.mcap")
        print("      (This will automatically create a binary MCAP file)")
    
    # 3. Summary
    print("\n" + "=" * 60)
    print("📦 Deliverables Summary")
    print("=" * 60)
    
    if converted_files:
        print("\n✅ Binary MCAP files ready for Foxglove Studio:")
        for name, filepath in converted_files:
            size_mb = Path(filepath).stat().st_size / (1024 * 1024)
            print(f"   ✅ {name}: {Path(filepath).name} ({size_mb:.2f} MB)")
        
        print("\n📁 Location: deliverables/")
        print("\n🎯 Next Steps:")
        print("   1. Open Foxglove Studio (https://studio.foxglove.dev/)")
        print("   2. Click 'Open File' and select the .mcap files")
        print("   3. Visualize the robot training progress!")
        
    else:
        print("\n⚠️  No MCAP files were converted.")
        if not single_json.exists() and not multi_json.exists():
            print("   Make sure training was run with --record flag.")
        else:
            print("   The JSON files may be too large to convert.")
            print("   Try using a streaming approach or contact for assistance.")
    
    # Check if multi-robot training is needed
    if not multi_json.exists():
        print("\n" + "=" * 60)
        print("⚠️  Multi-Robot Training MCAP Missing")
        print("=" * 60)
        print("\nYour lead requested the multi-robot training MCAP.")
        print("To generate it, run:")
        print("\n  python train.py --mode multi --episodes 20000 --num_robots 3 \\")
        print("      --record --mcap_output multi_robot_training.mcap")
        print("\nThis will automatically create a binary MCAP file that can be opened in Foxglove.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
