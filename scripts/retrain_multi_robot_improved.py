#!/usr/bin/env python3
"""
Retrain multi-robot with improved reward shaping and hyperparameters
This script will create much better results for your job deliverable!
"""

import subprocess
import sys
import shutil
from pathlib import Path

def main():
    print("=" * 70)
    print("🚀 IMPROVED MULTI-ROBOT TRAINING")
    print("=" * 70)
    print()
    print("Improvements applied:")
    print("  ✅ Better reward shaping (progress rewards, scaled penalties)")
    print("  ✅ Optimized hyperparameters (lower LR, larger batch, more epochs)")
    print("  ✅ More exploration (increased entropy coefficient)")
    print("  ✅ Longer training (double the episodes)")
    print()
    print("This will train for ~40,000 episodes (double the previous)")
    print("Expected time: 2-4 hours depending on your hardware")
    print()
    
    # Backup old models
    old_model_dir = Path("models/multi_robot")
    if old_model_dir.exists():
        backup_dir = Path("models/multi_robot_old")
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        shutil.copytree(old_model_dir, backup_dir)
        print("📦 Backed up old models to models/multi_robot_old/")
        print()
    
    # Run improved training
    print("🏋️ Starting training...")
    print()
    
    cmd = [
        sys.executable, "train.py",
        "--mode", "multi",
        "--episodes", "40000",  # Double the training!
        "--num_robots", "3",
        "--record",
        "--mcap_output", "multi_robot_training_improved.mcap"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, check=True)
        
        print()
        print("=" * 70)
        print("✅ Training completed successfully!")
        print("=" * 70)
        print()
        
        # Regenerate MCAP files
        print("📦 Regenerating MCAP files for Foxglove...")
        subprocess.run([sys.executable, "create_mcap_from_logs.py"], check=True)
        
        print()
        print("=" * 70)
        print("🎉 ALL DONE!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("  1. Open deliverables/multi_robot_training.mcap in Foxglove")
        print("  2. Check the Plot panel - you should see:")
        print("     • Rewards closer to 0 or positive")
        print("     • Clearer upward trend")
        print("     • Less variance (more stable)")
        print()
        print("  3. Compare with single_robot_training.mcap")
        print("     • Multi-robot should now show similar learning curve")
        print()
        print("Your job deliverable is now much stronger! 🚀")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print()
        print("=" * 70)
        print(f"❌ Training failed with error code: {e.returncode}")
        print("=" * 70)
        return False
        
    except KeyboardInterrupt:
        print()
        print("⚠️  Training interrupted by user.")
        print("   You can resume or restart training anytime.")
        return False

if __name__ == "__main__":
    print()
    input("Press Enter to start improved training (or Ctrl+C to cancel)...")
    print()
    success = main()
    sys.exit(0 if success else 1)


