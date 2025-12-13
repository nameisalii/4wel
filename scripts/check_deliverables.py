import os
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional

def check_file_structure():
    """
    Check what files exist in the project
    """
    print("=" * 60)
    print("CHECKING AVAILABLE DELIVERABLES")
    
    deliverables = {
        'single_robot_logs': Path('logs/single_robot/evaluations.npz').exists(),
        'multi_robot_logs': Path('logs/multi_robot').exists() and len(list(Path('logs/multi_robot').iterdir())) > 0,
        'tensorboard_logs': Path('tensorboard_logs').exists() and len(list(Path('tensorboard_logs').iterdir())) > 0,
        'single_robot_mcap': False,
        'multi_robot_mcap': False,
        'training_metrics_json': Path('training_metrics.json').exists(),
        'training_episodes_json': Path('training_episodes.json').exists(),
        'training_json': Path('training.json').exists(),
    }
    
    mcap_files = list(Path('.').glob('*.mcap')) + list(Path('.').glob('*mcap*.json'))
    if mcap_files:
        for f in mcap_files:
            if 'single' in f.name.lower() or 'training' in f.name.lower():
                deliverables['single_robot_mcap'] = True
            if 'multi' in f.name.lower():
                deliverables['multi_robot_mcap'] = True
    
    print("\n DELIVERABLES STATUS:")
    print("-" * 60)
    for key, exists in deliverables.items():
        status = "yes" if exists else "no"
        print(f"{status} {key.replace('_', ' ').title()}")
    
    return deliverables

def check_tensorboard_logs():
    """
    Check Tensorboard logs
    """
    print("\n" + "=" * 60)
    print("TENSORBOARD LOGS")
    
    tb_dir = Path('tensorboard_logs')
    if tb_dir.exists():
        runs = list(tb_dir.iterdir())
        print(f"Found {len(runs)} TensorBoard runs:")
        for run in runs:
            events = list(run.glob('events.out.tfevents.*'))
            print(f"  - {run.name}: {len(events)} event file(s)")
    else:
        print("TensorBoard directory not found")

def check_evaluation_logs():
    """
    Check evaluation logs
    """
    print("\n" + "=" * 60)
    print("EVALUATION LOGS")
    
    single_log = Path('logs/single_robot/evaluations.npz')
    if single_log.exists():
        try:
            data = np.load(single_log, allow_pickle=True)
            print(f"Single robot logs found: {single_log}")
            print(f"keys: {list(data.keys())}")
            for key in data.keys():
                print(f"   - {key}: shape {data[key].shape if hasattr(data[key], 'shape') else 'scalar'}")
        except Exception as e:
            print(f"Error reading single robot logs: {e}")
    else:
        print("Single robot evaluation logs not found")
    
    multi_log_dir = Path('logs/multi_robot')
    if multi_log_dir.exists() and len(list(multi_log_dir.iterdir())) > 0:
        print(f"Multi robot logs directory exists")
        for f in multi_log_dir.iterdir():
            print(f"- {f.name}")
    else:
        print("Multi robot logs not found")

def check_mcap_files():
    """
    Check for MCAP files
    """
    print("\n" + "=" * 60)
    print("MCAP RECORDINGS")
    
    #code looks for MCAP-Json files
    json_files = list(Path('.').glob('*.json'))
    mcap_candidates = []
    
    for json_file in json_files:
        if json_file.name in ['training_metrics.json', 'training_episodes.json', 'training.json']:
            try:
                with open(json_file, 'r') as f:
                    first_line = f.readline()
                    f.seek(0)
                    
                    if json_file.stat().st_size < 10_000_000:  #we check only small files here
                        try:
                            data = json.load(f)
                            if isinstance(data, dict):
                                if 'metrics' in data or 'messages' in data or 'metadata' in data:
                                    mcap_candidates.append((json_file, 'MCAP-like structure'))
                                elif 'episode_rewards' in data or 'episode_lengths' in data:
                                    mcap_candidates.append((json_file, 'Metrics data'))
                        except:
                            pass
            except Exception as e:
                pass
    
    if mcap_candidates:
        print("Found potential MCAP/metrics files:")
        for file, desc in mcap_candidates:
            size_mb = file.stat().st_size / (1024 * 1024)
            print(f"{file.name} ({desc}, {size_mb:.2f} MB)")
    else:
        print("No MCAP recordings found")
        print("MCAP files should be generated with --record flag during training")
    
    mcap_files = list(Path('.').glob('*.mcap'))
    if mcap_files:
        print("\nFound .mcap files:")
        for f in mcap_files:
            size_mb = f.stat().st_size / (1024 * 1024)
            print(f"{f.name} ({size_mb:.2f} MB)")
    else:
        print("\n No .mcap files found")

def check_training_json():
    """
    Check the large training.json file
    """
    print("\n" + "=" * 60)
    print("TRAINING.JSON FILE")
    
    training_json = Path('training.json')
    if training_json.exists():
        size_mb = training_json.stat().st_size / (1024 * 1024)
        print(f"Found training.json ({size_mb:.2f} MB)")
        print("File is very large - may be corrupted or contain raw training data")
        print("Attempting to check structure...")
        
        try:
            with open(training_json, 'r', encoding='utf-8') as f:
                first_chunk = f.read(1000)
                if first_chunk.strip().startswith('{'):
                    print("Appears to be JSON format")
                    print(f"First 200 chars: {first_chunk[:200]}...")
                elif first_chunk.strip().startswith('['):
                    print("Appears to be JSON array format")
                else:
                    print("Unknown format")
        except Exception as e:
            print(f"Error reading file: {e}")
    else:
        print("training.json not found")


if __name__ == "__main__":
    check_file_structure()
    check_tensorboard_logs()
    check_evaluation_logs()
    check_mcap_files()
    check_training_json()
    generate_summary()

