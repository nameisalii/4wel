import json
import shutil
import os
from pathlib import Path
import numpy as np

def extract_mcap_from_training_json():
    print("Extracting MCAP data from training.json")
    
    training_json = Path('training.json')
    if not training_json.exists():
        print("training.json not found")
        return None
    
    deliverables_dir = Path('deliverables')
    deliverables_dir.mkdir(exist_ok=True)
    
    try:
        print("Reading training.json (this may take a while for large files)...")
        with open(training_json, 'r') as f:
            chunk = f.read(5000)
            if 'mcap-like-json' in chunk or 'metadata' in chunk:
                print("Found MCAP-like structure in training.json")
                
                output_mcap = deliverables_dir / 'single_robot_training.mcap.json'
                
                size_mb = training_json.stat().st_size / (1024 * 1024)
                if size_mb > 500:
                    print(f"File is very large ({size_mb:.2f} MB). Copying directly...")
                    shutil.copy2(training_json, output_mcap)
                    print(f"Copied to {output_mcap}")
                    
                    try:
                        print("Attempting to extract metrics for plotting...")
                        return extract_metrics_streaming(training_json, deliverables_dir)
                    except Exception as e:
                        print(f"Could not extract metrics: {e}")
                        print("You can still use the full MCAP file")
                        return output_mcap
                else:
                    with open(training_json, 'r') as f:
                        data = json.load(f)
                    
                    #save as MCAP
                    with open(output_mcap, 'w') as f:
                        json.dump(data, f, indent=2)
                    
                    print(f"Saved MCAP data to {output_mcap}")
                    
                    #extracting metrics if available
                    if 'metrics' in data and len(data['metrics']) > 0:
                        metrics_file = deliverables_dir / 'single_robot_metrics.json'
                        with open(metrics_file, 'w') as f:
                            json.dump({'metrics': data['metrics']}, f, indent=2)
                        print(f"Extracted metrics to {metrics_file}")
                        return output_mcap, metrics_file
                    
                    return output_mcap
            else:
                print("training.json doesn't appear to be MCAP format")
                return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print("   File may be corrupted or incomplete")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def extract_metrics_streaming(json_file, output_dir):
    """Extract metrics using streaming approach for large files"""
    print("Using streaming extraction (simplified)...")
    return None

def copy_logs(deliverables_dir):
    print("\nCopying training logs...")
    
    logs_dir = deliverables_dir / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    single_logs = Path('logs/single_robot')
    if single_logs.exists():
        dest = logs_dir / 'single_robot'
        shutil.copytree(single_logs, dest, dirs_exist_ok=True)
        print(f"Copied single robot logs to {dest}")
    
    tb_logs = Path('tensorboard_logs')
    if tb_logs.exists():
        dest = logs_dir / 'tensorboard_logs'
        shutil.copytree(tb_logs, dest, dirs_exist_ok=True)
        print(f"Copied TensorBoard logs to {dest}")
    
    multi_logs = Path('logs/multi_robot')
    if multi_logs.exists() and len(list(multi_logs.iterdir())) > 0:
        dest = logs_dir / 'multi_robot'
        shutil.copytree(multi_logs, dest, dirs_exist_ok=True)
        print(f"Copied multi robot logs to {dest}")
    else:
        print("Multi-robot logs not found")

def generate_metrics_plot(mcap_file, output_dir):
    print("\nGenerating metrics plot...")
    
    try:
        from plot_metrics import plot_training_metrics
        
        output_plot = output_dir / 'training_metrics_plot.png'
        
        size_mb = Path(mcap_file).stat().st_size / (1024 * 1024)
        if size_mb > 500:
            print(f"MCAP file is very large ({size_mb:.2f} MB)")
            print("Skipping plot generation (would require streaming parser)")
            print("You can manually extract metrics and plot them")
            return None
        
        plot_training_metrics(str(mcap_file), str(output_plot))
        print(f"Generated plot: {output_plot}")
        return output_plot
    except ImportError:
        print("plot_metrics module not available")
        return None
    except Exception as e:
        print(f"Error generating plot: {e}")
        return None

def create_readme(deliverables_dir, has_single_mcap, has_multi_mcap, has_plot):
    readme_content = f"""# Training Deliverables

This folder contains the training logs and MCAP recordings as requested.

## Contents

### Training Logs
- `logs/single_robot/` - Single robot evaluation logs
- `logs/tensorboard_logs/` - TensorBoard training logs
{f"- `logs/multi_robot/` - Multi-robot evaluation logs" if Path(deliverables_dir / 'logs' / 'multi_robot').exists() else "- `logs/multi_robot/` - Not available (multi-robot training not completed)"}

### MCAP Recordings
{f"- `single_robot_training.mcap.json` - Single robot training MCAP recording" if has_single_mcap else "- Single robot MCAP - Not available"}
{f"- `multi_robot_training.mcap.json` - Multi-robot training MCAP recording" if has_multi_mcap else "- Multi-robot MCAP - Not available (multi-robot training not completed)"}

### Metrics Plots
{f"- `training_metrics_plot.png` - Training metrics visualization" if has_plot else "- Metrics plot - Could not generate (MCAP file too large or missing metrics)"}

## Notes

- MCAP files are in JSON format (MCAP-like structure) as generated by the training script
- For very large MCAP files (>500MB), full extraction may require specialized tools
- TensorBoard logs can be viewed with: `tensorboard --logdir logs/tensorboard_logs/`

## Missing Items

- Multi-robot training logs and MCAP: These were not found. If multi-robot training was performed, it may not have been run with the `--record` flag.

To generate multi-robot MCAP recordings, run:
```bash
python train.py --mode multi --episodes 20000 --num_robots 3 --record --mcap_output multi_robot_training.mcap
```
"""
    
    readme_path = deliverables_dir / 'README.md'
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    print(f"\n Created README: {readme_path}")

def main():
    print("=" * 60)
    print("PREPARING DELIVERABLES FOR LEAD")
    
    deliverables_dir = Path('deliverables')
    deliverables_dir.mkdir(exist_ok=True)
    
    mcap_result = extract_mcap_from_training_json()
    has_single_mcap = mcap_result is not None
    
    copy_logs(deliverables_dir)
    
    has_plot = False
    if mcap_result and isinstance(mcap_result, (str, Path)):
        plot_result = generate_metrics_plot(mcap_result, deliverables_dir)
        has_plot = plot_result is not None
    elif isinstance(mcap_result, tuple):
        mcap_file, metrics_file = mcap_result
        plot_result = generate_metrics_plot(metrics_file, deliverables_dir)
        has_plot = plot_result is not None
    
    has_multi_mcap = False
    multi_mcap_files = list(Path('.').glob('*multi*mcap*.json')) + list(Path('.').glob('*multi*.mcap'))
    if multi_mcap_files:
        for f in multi_mcap_files:
            dest = deliverables_dir / f.name
            shutil.copy2(f, dest)
            print(f"Copied multi-robot MCAP: {dest}")
            has_multi_mcap = True
    
    create_readme(deliverables_dir, has_single_mcap, has_multi_mcap, has_plot)
    
    print("\n" + "=" * 60)
    print("DELIVERABLES PREPARED")

    print(f"\n Deliverables folder: {deliverables_dir.absolute()}")
    print("\nYou can now share the 'deliverables' folder with your lead.")

if __name__ == "__main__":
    main()

