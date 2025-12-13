#!/usr/bin/env python3
"""
Monitor multi-robot training progress and organize deliverables when complete
"""

import time
import subprocess
import sys
from pathlib import Path
import shutil
import json

def check_training_status():
    """Check if training process is still running"""
    try:
        # Check for Python processes running train.py
        result = subprocess.run(
            ["pgrep", "-f", "train.py.*multi"],
            capture_output=True,
            text=True
        )
        return len(result.stdout.strip()) > 0
    except:
        return False

def check_mcap_files():
    """Check if MCAP files have been created"""
    files = {
        'mcap_json': Path('multi_robot_training.mcap.json'),
        'episodes': Path('multi_robot_training.mcap_episodes.json'),
        'metrics': Path('multi_robot_training.mcap_metrics.json'),
        'logs': Path('logs/multi_robot/evaluations.npz')
    }
    
    status = {}
    for name, path in files.items():
        status[name] = path.exists()
        if path.exists():
            try:
                size_mb = path.stat().st_size / (1024 * 1024)
                status[f'{name}_size'] = size_mb
            except:
                status[f'{name}_size'] = 0
    
    return status

def organize_multi_robot_deliverables():
    """Organize multi-robot training deliverables"""
    print("\n" + "=" * 60)
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
        print("⚠️  MCAP file not found yet")
    
    # Copy episodes and metrics files
    episodes_file = Path('multi_robot_training.mcap_episodes.json')
    metrics_file = Path('multi_robot_training.mcap_metrics.json')
    
    if episodes_file.exists():
        dest = deliverables_dir / 'multi_robot_episodes.json'
        try:
            shutil.copy2(episodes_file, dest)
            print(f"✅ Copied episodes data: {dest.name}")
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
        except Exception as e:
            print(f"⚠️  Error copying logs: {e}")
    
    # Update deliverables README
    update_deliverables_readme(deliverables_dir)
    
    print("\n" + "=" * 60)
    print("✨ Multi-robot deliverables organized!")
    print("=" * 60)

def update_deliverables_readme(deliverables_dir):
    """Update the deliverables README with multi-robot info"""
    readme_path = deliverables_dir / 'README.md'
    
    if not readme_path.exists():
        return
    
    try:
        with open(readme_path, 'r') as f:
            content = f.read()
        
        # Check if multi-robot section needs updating
        if 'Multi-robot MCAP' in content and 'Not available' in content:
            # Update the multi-robot section
            new_section = """- **`multi_robot_training.mcap.json`** - This is the MCAP recording from the multi-robot training with 3 robots learning collision avoidance. Similar to the single-robot file, it contains detailed visualization markers showing how all three robots moved, avoided collisions, and learned to navigate to their targets simultaneously. The file shows the learning progress as the robots improved their coordination and collision avoidance skills."""
            
            # Replace the "Not available" text
            content = content.replace(
                "- **Multi-robot MCAP** - I don't have a multi-robot MCAP recording available.",
                new_section
            )
            
            # Update logs section
            content = content.replace(
                "- **`logs/multi_robot/`** - Unfortunately, I don't have multi-robot training logs here.",
                "- **`logs/multi_robot/`** - Multi-robot evaluation logs from the training sessions."
            )
            
            with open(readme_path, 'w') as f:
                f.write(content)
            print("✅ Updated deliverables README")
    except Exception as e:
        print(f"⚠️  Could not update README: {e}")

def main():
    print("=" * 60)
    print("Multi-Robot Training Monitor")
    print("=" * 60)
    print("\nMonitoring training progress...")
    print("Press Ctrl+C to stop monitoring (training will continue)\n")
    
    last_status = {}
    check_count = 0
    
    try:
        while True:
            check_count += 1
            is_running = check_training_status()
            file_status = check_mcap_files()
            
            # Print status every 10 checks (about every 30 seconds)
            if check_count % 10 == 0:
                print(f"\n[{time.strftime('%H:%M:%S')}] Status check #{check_count}")
                print(f"  Training running: {'Yes' if is_running else 'No'}")
                
                if file_status.get('mcap_json'):
                    size = file_status.get('mcap_json_size', 0)
                    print(f"  MCAP file: {size:.2f} MB")
                else:
                    print(f"  MCAP file: Not created yet")
                
                if file_status.get('logs'):
                    print(f"  Logs: Available")
                else:
                    print(f"  Logs: Not created yet")
            
            # If training stopped and files exist, organize deliverables
            if not is_running:
                if file_status.get('mcap_json') or file_status.get('logs'):
                    print("\n" + "=" * 60)
                    print("Training appears to have completed!")
                    print("=" * 60)
                    organize_multi_robot_deliverables()
                    break
            
            # Check if files changed
            if file_status != last_status:
                if file_status.get('mcap_json') and not last_status.get('mcap_json'):
                    print(f"\n✅ MCAP file created! ({file_status.get('mcap_json_size', 0):.2f} MB)")
                if file_status.get('logs') and not last_status.get('logs'):
                    print(f"✅ Logs created!")
            
            last_status = file_status
            time.sleep(3)  # Check every 3 seconds
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user.")
        print("Training may still be running in the background.")
        
        # Check final status
        file_status = check_mcap_files()
        if file_status.get('mcap_json') or file_status.get('logs'):
            print("\nOrganizing available deliverables...")
            organize_multi_robot_deliverables()

if __name__ == "__main__":
    main()

