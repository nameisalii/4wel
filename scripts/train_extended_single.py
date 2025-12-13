#!/usr/bin/env python3
"""
Extended training script for single robot - trains for much longer to improve performance
"""

import subprocess
import sys
import os

def main():
    print("=" * 70)
    print("🚀 EXTENDED SINGLE ROBOT TRAINING")
    print("=" * 70)
    print()
    print("Training parameters:")
    print("  - Episodes: 40000 (20,000,000 timesteps)")
    print("  - MCAP recording: Enabled")
    print()
    print("This will take several hours. Checkpoints will be saved every 10,000 steps.")
    print()
    
    os.makedirs("./models/single_robot", exist_ok=True)
    os.makedirs("./logs/single_robot", exist_ok=True)
    os.makedirs("./checkpoints/single_robot", exist_ok=True)
    
    cmd = [
        sys.executable, "train.py",
        "--mode", "single",
        "--episodes", "40000",
        "--record",
        "--mcap_output", "single_robot_training_extended.mcap"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    print()
    
    try:
        subprocess.run(cmd, check=True)
        print()
        print("=" * 70)
        print("✅ Single robot training completed successfully!")
        print("=" * 70)
    except subprocess.CalledProcessError as e:
        print(f"❌ Training failed with error code: {e.returncode}")
    except KeyboardInterrupt:
        print("\n⚠️  Training interrupted by user.")

if __name__ == "__main__":
    main()

