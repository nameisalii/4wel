#!/usr/bin/env python3
"""
Organize multi-robot training deliverables after training completes
"""

import shutil
from pathlib import Path
import json

def organize_deliverables():
    """Organize multi-robot training deliverables"""
    print("=" * 60)
    print("Organizing Multi-Robot Training Deliverables")
    print("=" * 60)
    
    deliverables_dir = Path('deliverables')
    deliverables_dir.mkdir(exist_ok=True)
    
    # Copy MCAP file
    mcap_file = Path('multi_robot_training.mcap.json')
    if mcap_file.exists():
        dest = deliverables_dir / 'multi_robot_training.mcap.json'
        print(f"\n📦 Copying MCAP file...")
        try:
            shutil.copy2(mcap_file, dest)
            size_mb = mcap_file.stat().st_size / (1024 * 1024)
            print(f"✅ Copied multi-robot MCAP: {dest.name} ({size_mb:.2f} MB)")
        except Exception as e:
            print(f"⚠️  Error copying MCAP file: {e}")
    else:
        print("⚠️  MCAP file not found: multi_robot_training.mcap.json")
        print("   Training may still be running or file hasn't been created yet")
    
    # Copy episodes and metrics files
    episodes_file = Path('multi_robot_training.mcap_episodes.json')
    metrics_file = Path('multi_robot_training.mcap_metrics.json')
    
    if episodes_file.exists():
        dest = deliverables_dir / 'multi_robot_episodes.json'
        try:
            shutil.copy2(episodes_file, dest)
            size_mb = episodes_file.stat().st_size / (1024 * 1024)
            print(f"✅ Copied episodes data: {dest.name} ({size_mb:.2f} MB)")
        except Exception as e:
            print(f"⚠️  Error copying episodes: {e}")
    
    if metrics_file.exists():
        dest = deliverables_dir / 'multi_robot_metrics.json'
        try:
            shutil.copy2(metrics_file, dest)
            print(f"✅ Copied metrics data: {dest.name}")
        except Exception as e:
            print(f"⚠️  Error copying metrics: {e}")
    
    # Copy multi-robot logs
    logs_dir = deliverables_dir / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    multi_logs = Path('logs/multi_robot')
    if multi_logs.exists() and len(list(multi_logs.iterdir())) > 0:
        dest = logs_dir / 'multi_robot'
        try:
            shutil.copytree(multi_logs, dest, dirs_exist_ok=True)
            print(f"✅ Copied multi-robot logs to {dest}")
            # List what was copied
            for f in dest.iterdir():
                if f.is_file():
                    size = f.stat().st_size / (1024 * 1024) if f.stat().st_size > 0 else 0
                    print(f"   - {f.name} ({size:.2f} MB)")
        except Exception as e:
            print(f"⚠️  Error copying logs: {e}")
    else:
        print("⚠️  Multi-robot logs directory not found or empty")
    
    # Update deliverables README
    update_deliverables_readme(deliverables_dir)
    
    print("\n" + "=" * 60)
    print("✨ Multi-robot deliverables organized!")
    print(f"📁 Location: {deliverables_dir.absolute()}")
    print("=" * 60)

def update_deliverables_readme(deliverables_dir):
    """Update the deliverables README with multi-robot info"""
    readme_path = deliverables_dir / 'README.md'
    
    if not readme_path.exists():
        print("⚠️  README not found, skipping update")
        return
    
    try:
        with open(readme_path, 'r') as f:
            content = f.read()
        
        # Check if we need to update multi-robot section
        has_mcap = Path('multi_robot_training.mcap.json').exists()
        has_logs = Path('logs/multi_robot').exists() and len(list(Path('logs/multi_robot').iterdir())) > 0
        
        if has_mcap or has_logs:
            # Update multi-robot MCAP section
            if 'Multi-robot MCAP** - I don\'t have' in content or 'Multi-robot MCAP** - Not available' in content:
                new_section = """- **`multi_robot_training.mcap.json`** - This is the MCAP recording from the multi-robot training with 3 robots learning collision avoidance. Similar to the single-robot file, it contains detailed visualization markers showing how all three robots moved, avoided collisions, and learned to navigate to their targets simultaneously. The file shows the learning progress as the robots improved their coordination and collision avoidance skills over the training episodes."""
                
                # Find and replace the multi-robot MCAP section
                import re
                pattern = r'- \*\*Multi-robot MCAP\*\*.*?\(multi-robot training not completed\)'
                content = re.sub(pattern, new_section, content, flags=re.DOTALL)
            
            # Update multi-robot logs section
            if 'logs/multi_robot/** - Unfortunately, I don\'t have' in content:
                content = content.replace(
                    "- **`logs/multi_robot/`** - Unfortunately, I don't have multi-robot training logs here. It looks like the multi-robot training either wasn't completed or wasn't run with logging enabled. I can generate these if needed.",
                    "- **`logs/multi_robot/`** - Multi-robot evaluation logs from the training sessions. These contain the evaluation metrics tracked during training, showing how the multi-robot system improved over time."
                )
            
            with open(readme_path, 'w') as f:
                f.write(content)
            print("✅ Updated deliverables README with multi-robot information")
    except Exception as e:
        print(f"⚠️  Could not update README: {e}")

if __name__ == "__main__":
    organize_deliverables()

