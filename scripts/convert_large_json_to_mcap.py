#!/usr/bin/env python3
"""
Convert large JSON MCAP files to binary MCAP using streaming approach
"""

import json
import sys
from pathlib import Path
from mcap.writer import Writer
import time

def convert_large_json_to_mcap(json_file: str, output_mcap: str, max_messages: int = None):
    """
    Convert large JSON MCAP file to binary MCAP using streaming.
    For very large files, we'll extract what we can.
    """
    try:
        json_path = Path(json_file)
        if not json_path.exists():
            print(f"File not found: {json_file}")
            return None
        
        file_size_mb = json_path.stat().st_size / (1024 * 1024)
        print(f"Converting {json_file} ({file_size_mb:.2f} MB) to binary MCAP...")
        
        print("   Reading JSON file (this may take a while for large files)...")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                chunk = f.read(10_000_000)
                
                if '"messages"' not in chunk and '"metrics"' not in chunk:
                    print("   File doesn't appear to be MCAP JSON format")
                    return None
                
                print("   File is very large. Using streaming parser...")
                
                try:
                    import ijson
                    use_streaming = True
                except ImportError:
                    print("   ijson not available. Installing...")
                    import subprocess
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', 'ijson'])
                    import ijson
                    use_streaming = True
                
                messages_count = 0
                metrics_count = 0
                
                with open(json_file, 'rb') as f:
                    mcap_file = open(output_mcap, 'wb')
                    writer = Writer(mcap_file)
                    writer.start()
                    
                    markers_channel_id = writer.register_channel(
                        topic='/visualization_markers',
                        message_encoding='json',
                        schema_id=0,
                        metadata={'description': 'Robot visualization markers'}
                    )
                    
                    metrics_channel_id = writer.register_channel(
                        topic='/training_metrics',
                        message_encoding='json',
                        schema_id=0,
                        metadata={'description': 'Training metrics'}
                    )
                    
                    print("   Processing messages...")
                    messages = ijson.items(f, 'messages.item')
                    for msg in messages:
                        if max_messages and messages_count >= max_messages:
                            break
                        timestamp_ns = int(msg['timestamp'] * 1e9)
                        data_bytes = json.dumps(msg['data']).encode('utf-8')
                        writer.add_message(
                            channel_id=markers_channel_id,
                            log_time=timestamp_ns,
                            data=data_bytes,
                            publish_time=timestamp_ns
                        )
                        messages_count += 1
                        if messages_count % 10000 == 0:
                            print(f"      Processed {messages_count} messages...")
                    
                    print("   Processing metrics...")
                    f.seek(0)
                    metrics = ijson.items(f, 'metrics.item')
                    for metric in metrics:
                        timestamp_ns = int(metric['timestamp'] * 1e9)
                        data_bytes = json.dumps(metric).encode('utf-8')
                        writer.add_message(
                            channel_id=metrics_channel_id,
                            log_time=timestamp_ns,
                            data=data_bytes,
                            publish_time=timestamp_ns
                        )
                        metrics_count += 1
                    
                    writer.finish()
                    mcap_file.close()
                
                file_size_mb = Path(output_mcap).stat().st_size / (1024 * 1024)
                print(f"Converted to binary MCAP: {output_mcap}")
                print(f"   Messages: {messages_count}")
                print(f"   Metrics: {metrics_count}")
                print(f"   File size: {file_size_mb:.2f} MB")
                
                return output_mcap
                
        except Exception as e:
            print(f"   Error during conversion: {e}")
            print("   Trying alternative approach...")
            
            # Alternative: Create a sample MCAP from available data
            return create_sample_mcap_from_available_data(json_file, output_mcap)
            
    except Exception as e:
        print(f" Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_sample_mcap_from_available_data(json_file: str, output_mcap: str):
    """Create MCAP from what we can extract"""
    print("   Creating MCAP from available data...")
    
    try:
        import numpy as np
        from pathlib import Path
        
        log_file = Path('logs/single_robot/evaluations.npz')
        if log_file.exists():
            data = np.load(log_file, allow_pickle=True)
            
            mcap_file = open(output_mcap, 'wb')
            writer = Writer(mcap_file)
            writer.start()
            
            metrics_channel_id = writer.register_channel(
                topic='/training_metrics',
                message_encoding='json',
                schema_id=0,
                metadata={}
            )
            
            if 'timesteps' in data and 'results' in data:
                timesteps = data['timesteps']
                results = data['results']
                
                for i, (ts, result) in enumerate(zip(timesteps, results)):
                    metric = {
                        'step': int(ts),
                        'timestamp': time.time() + i,
                        'reward': float(result[0]) if len(result) > 0 else 0.0,
                        'distance': float(result[1]) if len(result) > 1 else 0.0,
                        'success': bool(result[2]) if len(result) > 2 else False,
                        'episode_length': int(result[3]) if len(result) > 3 else 0
                    }
                    
                    timestamp_ns = int(metric['timestamp'] * 1e9)
                    data_bytes = json.dumps(metric).encode('utf-8')
                    writer.add_message(
                        channel_id=metrics_channel_id,
                        log_time=timestamp_ns,
                        data=data_bytes,
                        publish_time=timestamp_ns
                    )
            
            writer.finish()
            mcap_file.close()
            
            print(f"Created MCAP from evaluation logs: {output_mcap}")
            return output_mcap
    except Exception as e:
        print(f"Could not create from logs: {e}")
    
    return None

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python convert_large_json_to_mcap.py <input.json> <output.mcap>")
        sys.exit(1)
    
    convert_large_json_to_mcap(sys.argv[1], sys.argv[2])

