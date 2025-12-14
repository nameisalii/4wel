import json
import time
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path
import struct


class MCAPWriter:
    
    def __init__(self, output_file: str):
        self.output_file = Path(output_file)
        if self.output_file.suffix != '.mcap':
            self.output_file = self.output_file.with_suffix('.mcap')
        
        self.messages = []
        self.metrics = []
        self.timestamps = []
        self.start_time = time.time()
        
        self.use_binary = False
        try:
            from mcap.writer import Writer as MCAPBinaryWriter
            self.MCAPBinaryWriter = MCAPBinaryWriter
            self.use_binary = True
        except ImportError:
            self.use_binary = False
            print("Warning: mcap library not available. Will save as JSON backup.")
    
    def add_marker_message(self, markers: List[Dict], timestamp: Optional[float] = None):
        if timestamp is None:
            timestamp = time.time()
        
        self.timestamps.append(timestamp)
        
        message = {
            'channel': 'visualization_markers',
            'timestamp': timestamp,
            'data': markers
        }
        self.messages.append(message)
    
    def add_metrics(self, step: int, reward: float, distance: float, 
                   success: bool, episode_length: int):
        metric = {
            'step': step,
            'timestamp': time.time(),
            'reward': reward,
            'distance': distance,
            'success': success,
            'episode_length': episode_length
        }
        self.metrics.append(metric)
    
    def save(self):
        if self.use_binary:
            return self._save_binary_mcap()
        else:
            return self._save_json_backup()
    
    def _save_binary_mcap(self):
        try:
            from mcap.writer import Writer
            import json as json_lib
            
            output_file = str(self.output_file)
            file_handle = open(output_file, 'wb')
            writer = Writer(file_handle)
            writer.start()
            
            markers_schema = json_lib.dumps({
                "type": "object"
            }).encode('utf-8')
            markers_schema_id = writer.register_schema(
                name='visualization_markers',
                encoding='jsonschema',
                data=markers_schema
            )
            
            metrics_schema = json_lib.dumps({
                "type": "object",
                "properties": {
                    "step": {"type": "integer"},
                    "timestamp": {"type": "number"},
                    "reward": {"type": "number"},
                    "distance": {"type": "number"},
                    "success": {"type": "boolean"},
                    "episode_length": {"type": "integer"}
                }
            }).encode('utf-8')
            metrics_schema_id = writer.register_schema(
                name='training_metrics',
                encoding='jsonschema',
                data=metrics_schema
            )
            
            markers_channel_id = writer.register_channel(
                topic='/visualization_markers',
                message_encoding='json',
                schema_id=markers_schema_id,
                metadata={}
            )
            
            metrics_channel_id = writer.register_channel(
                topic='/training_metrics',
                message_encoding='json',
                schema_id=metrics_schema_id,
                metadata={}
            )
            
            for msg in self.messages:
                timestamp_ns = int(msg['timestamp'] * 1e9)
                # Convert numpy types to native Python types for JSON serialization
                data_dict = self._convert_numpy_types(msg['data'])
                data = json_lib.dumps(data_dict, default=self._json_serializer).encode('utf-8')
                writer.add_message(
                    channel_id=markers_channel_id,
                    log_time=timestamp_ns,
                    data=data,
                    publish_time=timestamp_ns
                )
            
            for metric in self.metrics:
                timestamp_ns = int(metric['timestamp'] * 1e9)
                # Convert numpy types to native Python types for JSON serialization
                metric_dict = self._convert_numpy_types(metric)
                data = json_lib.dumps(metric_dict, default=self._json_serializer).encode('utf-8')
                writer.add_message(
                    channel_id=metrics_channel_id,
                    log_time=timestamp_ns,
                    data=data,
                    publish_time=timestamp_ns
                )
            
            writer.finish()
            file_handle.close()
            
            print(f"  Binary MCAP file saved to {output_file}")
            print(f"  Messages: {len(self.messages)}")
            print(f"  Metrics: {len(self.metrics)}")
            print(f"  File size: {Path(output_file).stat().st_size / (1024*1024):.2f} MB")
            
            return output_file
            
        except Exception as e:
            print(f"  Error creating binary MCAP: {e}")
            import traceback
            traceback.print_exc()
            print("   Falling back to JSON format...")
            return self._save_json_backup()
    
    def _save_json_backup(self):
        data = {
            'metadata': {
                'created_at': self.start_time,
                'format': 'mcap-like-json',
                'version': '1.0'
            },
            'messages': self.messages,
            'metrics': self.metrics
        }
        
        output_json = self.output_file.with_suffix('.json')
        with open(output_json, 'w') as f:
            json.dump(data, f, indent=2, default=self._json_serializer)
        
        print(f"MCAP library not available. Saved as JSON: {output_json}")
        print(f"Messages: {len(self.messages)}")
        print(f"Metrics: {len(self.metrics)}")
        print("Note: Install 'mcap' package for binary MCAP format")
        
        return str(output_json)
    
    def _convert_numpy_types(self, obj):
        """Recursively convert numpy types to native Python types."""
        if isinstance(obj, dict):
            return {key: self._convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._convert_numpy_types(item) for item in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        else:
            return obj
    
    def _json_serializer(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        raise TypeError(f"Type {type(obj)} not serializable")


def convert_json_to_mcap(json_file: str, output_mcap: str):
    try:
        from mcap.writer import Writer
        import json as json_lib
        
        print(f"Loading {json_file}...")
        with open(json_file, 'r') as f:
            data = json_lib.load(f)
        
        messages = data.get('messages', [])
        metrics = data.get('metrics', [])
        
        print(f"Converting to binary MCAP...")
        print(f"Messages: {len(messages)}")
        print(f"Metrics: {len(metrics)}")
        
        file_handle = open(output_mcap, 'wb')
        writer = Writer(file_handle)
        writer.start()
        
        markers_schema = json_lib.dumps({
            "type": "object"
        }).encode('utf-8')
        markers_schema_id = writer.register_schema(
            name='visualization_markers',
            encoding='jsonschema',
            data=markers_schema
        )
        
        metrics_schema = json_lib.dumps({
            "type": "object",
            "properties": {
                "step": {"type": "integer"},
                "timestamp": {"type": "number"},
                "reward": {"type": "number"},
                "distance": {"type": "number"},
                "success": {"type": "boolean"},
                "episode_length": {"type": "integer"}
            }
        }).encode('utf-8')
        metrics_schema_id = writer.register_schema(
            name='training_metrics',
            encoding='jsonschema',
            data=metrics_schema
        )
        
        markers_channel_id = writer.register_channel(
            topic='/visualization_markers',
            message_encoding='json',
            schema_id=markers_schema_id,
            metadata={}
        )
        
        metrics_channel_id = writer.register_channel(
            topic='/training_metrics',
            message_encoding='json',
            schema_id=metrics_schema_id,
            metadata={}
        )
        
        print("Writing marker messages...")
        for i, msg in enumerate(messages):
            timestamp_ns = int(msg['timestamp'] * 1e9)
            data_bytes = json_lib.dumps(msg['data']).encode('utf-8')
            writer.add_message(
                channel_id=markers_channel_id,
                log_time=timestamp_ns,
                data=data_bytes,
                publish_time=timestamp_ns
            )
            if (i + 1) % 10000 == 0:
                print(f"Processed {i + 1}/{len(messages)} messages...")
        
        print("  Writing metric messages...")
        for metric in metrics:
            timestamp_ns = int(metric['timestamp'] * 1e9)
            data_bytes = json_lib.dumps(metric).encode('utf-8')
            writer.add_message(
                channel_id=metrics_channel_id,
                log_time=timestamp_ns,
                data=data_bytes,
                publish_time=timestamp_ns
            )
        
        writer.finish()
        file_handle.close()
        
        file_size_mb = Path(output_mcap).stat().st_size / (1024 * 1024)
        print(f" Converted to binary MCAP: {output_mcap}")
        print(f" File size: {file_size_mb:.2f} MB")
        
        return output_mcap
        
    except ImportError:
        print(" Error: mcap library not installed.")
        print("  Install with: pip install mcap")
        return None
    except json_lib.JSONDecodeError as e:
        print(f" Error: JSON file is corrupted or too large: {e}")
        print("   The file may be too large to load into memory.")
        print("   Try using convert_large_json_to_mcap.py for streaming conversion.")
        return None
    except Exception as e:
        print(f" Error converting file: {e}")
        import traceback
        traceback.print_exc()
        return None
