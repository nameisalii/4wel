#!/usr/bin/env python3
"""
Create proper binary MCAP files from training logs for Foxglove Studio.
This creates two MCAP files:
1. single_robot_training.mcap - From single robot training logs
2. multi_robot_training.mcap - From multi-robot training logs
"""

import numpy as np
from pathlib import Path
from mcap.writer import Writer
import json
import time

def create_mcap_from_evaluations(eval_file: str, output_mcap: str, mode: str):
    """
    Create a binary MCAP file from evaluation logs.
    
    Args:
        eval_file: Path to evaluations.npz file
        output_mcap: Path to output MCAP file
        mode: 'single' or 'multi' robot mode
    """
    print(f"\n{'='*60}")
    print(f"Creating {mode}-robot MCAP file from evaluation logs")
    print(f"{'='*60}")
    
    eval_path = Path(eval_file)
    if not eval_path.exists():
        print(f" Evaluation file not found: {eval_file}")
        return None
    
    # Load evaluation data
    print(f" Loading evaluation data from {eval_file}...")
    data = np.load(eval_file, allow_pickle=True)
    
    print(f"   Available keys: {list(data.keys())}")
    
    timesteps = data.get('timesteps', [])
    results = data.get('results', [])
    ep_lengths = data.get('ep_lengths', [])
    
    print(f"   Timesteps: {len(timesteps)}")
    print(f"   Results shape: {results.shape if hasattr(results, 'shape') else len(results)}")
    print(f"   Episode lengths shape: {ep_lengths.shape if hasattr(ep_lengths, 'shape') else len(ep_lengths)}")
    
    print(f"\n Creating binary MCAP file: {output_mcap}")
    
    with open(output_mcap, 'wb') as mcap_file:
        writer = Writer(mcap_file)
        writer.start()
        
        # Define JSON schema for training metrics
        metrics_schema = json.dumps({
            "type": "object",
            "properties": {
                "timestep": {"type": "integer"},
                "mean_reward": {"type": "number"},
                "std_reward": {"type": "number"},
                "mean_episode_length": {"type": "number"},
                "evaluation_index": {"type": "integer"},
                "mode": {"type": "string"}
            }
        }).encode('utf-8')
        
        metrics_schema_id = writer.register_schema(
            name='training_metrics',
            encoding='jsonschema',
            data=metrics_schema
        )
        
        # Define JSON schema for visualization
        viz_schema = json.dumps({
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "timestep": {"type": "integer"},
                "mean_reward": {"type": "number"},
                "episode": {"type": "integer"},
                "marker_text": {"type": "string"},
                "color": {
                    "type": "array",
                    "items": {"type": "number"}
                }
            }
        }).encode('utf-8')
        
        viz_schema_id = writer.register_schema(
            name='episode_visualization',
            encoding='jsonschema',
            data=viz_schema
        )
        
        metrics_channel_id = writer.register_channel(
            topic='/training_metrics',
            message_encoding='json',
            schema_id=metrics_schema_id,
            metadata={
                'description': f'Training metrics for {mode} robot navigation',
                'mode': mode
            }
        )
        
        viz_channel_id = writer.register_channel(
            topic='/episode_visualization',
            message_encoding='json',
            schema_id=viz_schema_id,
            metadata={
                'description': f'Episode visualization data for {mode} robot',
                'mode': mode
            }
        )
        
        base_time = eval_path.stat().st_mtime
        
        print(f"   Writing {len(timesteps)} metric messages...")
        
        for i, (ts, result_data, ep_len) in enumerate(zip(timesteps, results, ep_lengths)):
            if hasattr(result_data, '__len__'):
                mean_reward = float(np.mean(result_data))
                std_reward = float(np.std(result_data))
            else:
                mean_reward = float(result_data)
                std_reward = 0.0
            
            metric = {
                'timestep': int(ts),
                'mean_reward': mean_reward,
                'std_reward': std_reward,
                'mean_episode_length': float(np.mean(ep_len)) if hasattr(ep_len, '__len__') else float(ep_len),
                'evaluation_index': i,
                'mode': mode
            }
            
            timestamp = base_time + (i * 60)  
            timestamp_ns = int(timestamp * 1e9)
            
            data_bytes = json.dumps(metric).encode('utf-8')
            writer.add_message(
                channel_id=metrics_channel_id,
                log_time=timestamp_ns,
                data=data_bytes,
                publish_time=timestamp_ns
            )
            
            if i % 10 == 0:
                viz_data = {
                    'type': 'evaluation_marker',
                    'timestep': int(ts),
                    'mean_reward': mean_reward,
                    'episode': i,
                    'marker_text': f"Eval {i}: Reward {mean_reward:.2f}",
                    'color': [0.0, 1.0, 0.0, 1.0] if mean_reward > 0 else [1.0, 0.0, 0.0, 1.0]
                }
                
                data_bytes = json.dumps(viz_data).encode('utf-8')
                writer.add_message(
                    channel_id=viz_channel_id,
                    log_time=timestamp_ns,
                    data=data_bytes,
                    publish_time=timestamp_ns
                )
            
            if (i + 1) % 100 == 0:
                print(f"      Processed {i + 1}/{len(timesteps)} evaluations...")
        
        writer.finish()
    
    file_size_mb = Path(output_mcap).stat().st_size / (1024 * 1024)
    
    print(f"\n Binary MCAP file created successfully!")
    print(f"   Output: {output_mcap}")
    print(f"   Size: {file_size_mb:.2f} MB")
    print(f"   Messages: {len(timesteps)}")
    print(f"   Channels: 2 (metrics + visualization)")
    print(f"\n   This file can now be opened in Foxglove Studio!")
    
    return output_mcap


def main():
    """Create MCAP files for both single and multi robot training"""
    print("=" * 60)
    print("Creating Binary MCAP Files from Training Logs")
    print("=" * 60)
    print()
    print("This will create proper binary MCAP files that can be opened")
    print("in Foxglove Studio to visualize training progress.")
    print()
    
    created_files = []
    
    # 1. Create single robot MCAP
    single_eval = 'logs/single_robot/evaluations.npz'
    if Path(single_eval).exists():
        output = 'deliverables/single_robot_training.mcap'
        result = create_mcap_from_evaluations(single_eval, output, 'single')
        if result:
            created_files.append(result)
    else:
        print(f"  Single robot evaluation logs not found: {single_eval}")
    
    # 2. Create multi robot MCAP
    multi_eval = 'logs/multi_robot/evaluations.npz'
    if Path(multi_eval).exists():
        output = 'deliverables/multi_robot_training.mcap'
        result = create_mcap_from_evaluations(multi_eval, output, 'multi')
        if result:
            created_files.append(result)
    else:
        print(f"  Multi-robot evaluation logs not found: {multi_eval}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    if created_files:
        print(f"\n Created {len(created_files)} binary MCAP file(s):")
        for f in created_files:
            size_mb = Path(f).stat().st_size / (1024 * 1024)
            print(f" {f} ({size_mb:.2f} MB)")
        
        print("\n📖 How to use:")
        print("   1. Open Foxglove Studio (https://foxglove.dev)")
        print("   2. Click 'Open local file'")
        print("   3. Select one of the MCAP files above")
        print("   4. You'll see the training metrics plotted over time")
        print("\n   The files contain:")
        print("   - Training metrics (rewards, episode lengths)")
        print("   - Evaluation markers showing progress")
        print("   - Timestep information")
    else:
        print(" No MCAP files were created.")
        print("   Check that evaluation logs exist in logs/ directory")
    
    print("=" * 60)

if __name__ == "__main__":
    main()

