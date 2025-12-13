#!/usr/bin/env python3
"""
Extended training script for multi-robot - trains for much longer to improve performance
"""

import subprocess
import sys
import os

def main():
    print("=" * 70)
    print("🚀 EXTENDED MULTI-ROBOT TRAINING")
    print("=" * 70)
    print()
    print("Training parameters:")
    print("  - Episodes: 100000 (100,000,000 timesteps)")
    print("  - Number of robots: 3")
    print("  - MCAP recording: Enabled")
    print()
    print("⚠️  This will take MANY hours (possibly 10+ hours).")
    print("Checkpoints will be saved every 20,000 steps.")
    print("You can stop and resume from checkpoints if needed.")
    print()
    
    os.makedirs("./models/multi_robot", exist_ok=True)
    os.makedirs("./logs/multi_robot", exist_ok=True)
    os.makedirs("./checkpoints/multi_robot", exist_ok=True)
    
    cmd = [
        sys.executable, "train.py",
        "--mode", "multi",
        "--episodes", "100000",
        "--num_robots", "3",
        "--record",
        "--mcap_output", "multi_robot_training_extended.mcap"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    print()
    
    try:
        subprocess.run(cmd, check=True)
        print()
        print("=" * 70)
        print("✅ Multi-robot training completed successfully!")
        print("=" * 70)
    except subprocess.CalledProcessError as e:
        print(f"❌ Training failed with error code: {e.returncode}")
    except KeyboardInterrupt:
        print("\n⚠️  Training interrupted by user.")
        print("You can resume from the latest checkpoint in ./checkpoints/multi_robot/")

if __name__ == "__main__":
    main()

