
import sys
import os
import subprocess
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    print("=" * 70)
    print("Generating All Deliverables")
    print("=" * 70)
    print()
    print("This will create:")
    print("  1. MCAP files with robot visualization")
    print("  2. Metrics plots")
    print()
    print("=" * 70)
    print()
    
    deliverables_dir = Path("deliverables")
    deliverables_dir.mkdir(exist_ok=True)
    
    scripts_dir = Path("scripts")
    
    print("📊 Step 1: Generating metrics plots...")
    print("-" * 70)
    try:
        result = subprocess.run(
            [sys.executable, str(scripts_dir / "generate_metrics_plots.py")],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(result.stdout)
            print("✅ Metrics plots generated successfully")
        else:
            print("⚠️  Error generating metrics plots:")
            print(result.stderr)
    except Exception as e:
        print(f"⚠️  Error running metrics plot script: {e}")
    print()
    
    print("🤖 Step 2: Creating single robot visualization MCAP...")
    print("-" * 70)
    single_model = Path("models/single_robot/best_model.zip")
    if not single_model.exists():
        single_model = Path("models/single_robot/final_model.zip")
    
    if single_model.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(scripts_dir / "create_visualization_mcap.py"),
                 "--mode", "single",
                 "--model", str(single_model),
                 "--output", str(deliverables_dir / "single_robot_training_with_viz.mcap"),
                 "--episodes", "20"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(result.stdout)
                print("✅ Single robot visualization MCAP created")
            else:
                print("⚠️  Error creating single robot MCAP:")
                print(result.stderr)
        except Exception as e:
            print(f"⚠️  Error running visualization script: {e}")
    else:
        print(f"⚠️  Single robot model not found: {single_model}")
    print()
    
    print("🤖🤖🤖 Step 3: Creating multi robot visualization MCAP...")
    print("-" * 70)
    multi_model = Path("models/multi_robot/best_model.zip")
    if not multi_model.exists():
        multi_model = Path("models/multi_robot/final_model.zip")
    
    if multi_model.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(scripts_dir / "create_visualization_mcap.py"),
                 "--mode", "multi",
                 "--model", str(multi_model),
                 "--output", str(deliverables_dir / "multi_robot_training_with_viz.mcap"),
                 "--episodes", "15",
                 "--num_robots", "3"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(result.stdout)
                print("✅ Multi robot visualization MCAP created")
            else:
                print("⚠️  Error creating multi robot MCAP:")
                print(result.stderr)
        except Exception as e:
            print(f"⚠️  Error running visualization script: {e}")
    else:
        print(f"⚠️  Multi robot model not found: {multi_model}")
    print()
    
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print()
    
    deliverables = []
    
    single_plot = deliverables_dir / "single_robot_metrics.png"
    multi_plot = deliverables_dir / "multi_robot_metrics.png"
    if single_plot.exists():
        deliverables.append(("Single Robot Metrics Plot", single_plot))
    if multi_plot.exists():
        deliverables.append(("Multi Robot Metrics Plot", multi_plot))
    
    single_viz_mcap = deliverables_dir / "single_robot_training_with_viz.mcap"
    multi_viz_mcap = deliverables_dir / "multi_robot_training_with_viz.mcap"
    if single_viz_mcap.exists():
        size_mb = single_viz_mcap.stat().st_size / (1024 * 1024)
        deliverables.append(("Single Robot Visualization MCAP", single_viz_mcap, f"{size_mb:.2f} MB"))
    if multi_viz_mcap.exists():
        size_mb = multi_viz_mcap.stat().st_size / (1024 * 1024)
        deliverables.append(("Multi Robot Visualization MCAP", multi_viz_mcap, f"{size_mb:.2f} MB"))
    
    if deliverables:
        print("✅ Generated deliverables:")
        for item in deliverables:
            if len(item) == 3:
                name, path, size = item
                print(f"   • {name}: {path.name} ({size})")
            else:
                name, path = item
                print(f"   • {name}: {path.name}")
    else:
        print("⚠️  No deliverables were generated. Check errors above.")
    
    print()
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()

