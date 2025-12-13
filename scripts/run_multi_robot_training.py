#!/usr/bin/env python3
"""
Script to run multi-robot training with MCAP recording and organize deliverables
"""

import subprocess
import sys
import time
from pathlib import Path
import shutil
import os

def run_training():
    """Run multi-robot training with MCAP recording"""
    print("=" * 60)
    print("Starting Multi-Robot Training with MCAP Recording")
    print("=" * 60)
    print()
    print("This will train 3 robots with collision avoidance.")
    print("Training parameters:")
    print("  - Episodes: 20000 (converted to timesteps)")
    print("  - Number of robots: 3")
    print("  - MCAP recording: Enabled")
    print()
    print("Note: This may take several hours depending on your hardware.")
    print("The training will save checkpoints periodically.")
    print()
    
    # Ensure directories exist
    os.makedirs("./models/multi_robot", exist_ok=True)
    os.makedirs("./logs/multi_robot", exist_ok=True)
    os.makedirs("./checkpoints/multi_robot", exist_ok=True)
    
    # Run training
    cmd = [
        sys.executable, "train.py",
        "--mode", "multi",
        "--episodes", "20000",
        "--num_robots", "3",
        "--record",
        "--mcap_output", "multi_robot_training.mcap"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, check=True)
        print()
        print("=" * 60)
        print("Training completed successfully!")
        print("=" * 60)
        return True
    except subprocess.CalledProcessError as e:
        print()
        print("=" * 60)
        print(f"Training failed with error code: {e.returncode}")
        print("=" * 60)
        return False
    except KeyboardInterrupt:
        print()
        print("Training interrupted by user.")
        return False

def organize_deliverables():
    """Organize multi-robot training deliverables"""
    print()
    print("=" * 60)
    print("Organizing Multi-Robot Training Deliverables")
    print("=" * 60)
    
    deliverables_dir = Path('deliverables')
    deliverables_dir.mkdir(exist_ok=True)
    
    # Copy MCAP file
    mcap_file = Path('multi_robot_training.mcap.json')
    if mcap_file.exists():
        dest = deliverables_dir / 'multi_robot_training.mcap.json'
        print(f"Copying MCAP file...")
        shutil.copy2(mcap_file, dest)
        size_mb = mcap_file.stat().st_size / (1024 * 1024)
        print(f"✅ Copied multi-robot MCAP: {dest} ({size_mb:.2f} MB)")
    else:
        print("⚠️  MCAP file not found. It may still be generating...")
    
    # Copy episodes and metrics files
    episodes_file = Path('multi_robot_training.mcap_episodes.json')
    metrics_file = Path('multi_robot_training.mcap_metrics.json')
    
    if episodes_file.exists():
        dest = deliverables_dir / 'multi_robot_episodes.json'
        shutil.copy2(episodes_file, dest)
        print(f"✅ Copied episodes data: {dest}")
    
    if metrics_file.exists():
        dest = deliverables_dir / 'multi_robot_metrics.json'
        shutil.copy2(metrics_file, dest)
        print(f"✅ Copied metrics data: {dest}")
    
    # Copy multi-robot logs
    logs_dir = deliverables_dir / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    multi_logs = Path('logs/multi_robot')
    if multi_logs.exists() and len(list(multi_logs.iterdir())) > 0:
        dest = logs_dir / 'multi_robot'
        shutil.copytree(multi_logs, dest, dirs_exist_ok=True)
        print(f"✅ Copied multi-robot logs to {dest}")
    
    print()
    print("=" * 60)
    print("Deliverables organized in: deliverables/")
    print("=" * 60)

if __name__ == "__main__":
    success = run_training()
    
    if success:
        organize_deliverables()
        print()
        print("✨ Multi-robot training complete! All deliverables are ready.")
    else:
        print()
        print("❌ Training did not complete successfully.")
        print("You can still check for partial results in the output files.")

