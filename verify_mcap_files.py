#!/usr/bin/env python3
"""
Verification script for MCAP deliverables.
This script validates that both MCAP files are properly formatted and readable.
"""

from mcap.reader import make_reader
from pathlib import Path
import json

def verify_mcap_file(mcap_path: str) -> dict:
    """Verify a single MCAP file and return its properties."""
    path = Path(mcap_path)
    
    if not path.exists():
        return {
            'valid': False,
            'error': 'File not found'
        }
    
    try:
        with open(mcap_path, 'rb') as f:
            reader = make_reader(f)
            summary = reader.get_summary()
            
            # Get channel information
            channels = []
            for channel_id, channel in summary.channels.items():
                channels.append({
                    'id': channel_id,
                    'topic': channel.topic,
                    'encoding': channel.message_encoding
                })
            
            # Read first few messages to verify content
            sample_messages = []
            f.seek(0)
            reader = make_reader(f)
            count = 0
            for schema, channel, message in reader.iter_messages():
                if count >= 3:  # Just get 3 sample messages
                    break
                try:
                    msg_data = json.loads(message.data.decode('utf-8'))
                    sample_messages.append({
                        'topic': channel.topic,
                        'timestamp': message.log_time,
                        'has_data': bool(msg_data)
                    })
                    count += 1
                except:
                    pass
            
            return {
                'valid': True,
                'path': str(path),
                'size_bytes': path.stat().st_size,
                'size_kb': path.stat().st_size / 1024,
                'num_channels': len(summary.channels),
                'num_messages': summary.statistics.message_count,
                'channels': channels,
                'sample_messages': sample_messages
            }
    
    except Exception as e:
        return {
            'valid': False,
            'error': str(e)
        }

def main():
    """Verify all MCAP deliverables."""
    print("=" * 70)
    print("MCAP Deliverables Verification")
    print("=" * 70)
    print()
    
    files_to_check = [
        ('deliverables/single_robot_training.mcap', 'Single Robot Training'),
        ('deliverables/multi_robot_training.mcap', 'Multi-Robot Training')
    ]
    
    all_valid = True
    results = []
    
    for file_path, description in files_to_check:
        print(f"📦 Checking: {description}")
        print(f"   File: {file_path}")
        
        result = verify_mcap_file(file_path)
        results.append((description, result))
        
        if result['valid']:
            print(f"   ✅ Valid MCAP file!")
            print(f"   Size: {result['size_kb']:.2f} KB")
            print(f"   Messages: {result['num_messages']}")
            print(f"   Channels: {result['num_channels']}")
            for channel in result['channels']:
                print(f"      - {channel['topic']} ({channel['encoding']})")
            print(f"   Sample messages verified: {len(result['sample_messages'])}")
        else:
            print(f"   ❌ Invalid: {result['error']}")
            all_valid = False
        
        print()
    
    # Summary
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print()
    
    if all_valid:
        print("✅ All MCAP files are valid and ready for Foxglove Studio!")
        print()
        print("📖 Next Steps:")
        print("   1. Open Foxglove Studio (https://foxglove.dev)")
        print("   2. Click 'Open local file'")
        print("   3. Select one of the MCAP files:")
        for desc, result in results:
            if result['valid']:
                print(f"      • {result['path']}")
        print("   4. View training metrics in the timeline")
        print()
        print("📊 What you'll see:")
        print("   - Training progress over time")
        print("   - Mean rewards per evaluation")
        print("   - Episode lengths")
        print("   - Evaluation markers")
    else:
        print("❌ Some MCAP files have issues. Please check the errors above.")
    
    print("=" * 70)
    
    return all_valid

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)


