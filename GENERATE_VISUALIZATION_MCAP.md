# Generating Visualization MCAP Files

This document explains how to generate MCAP files with robot visualization (body, wheels, links) for viewing in Foxglove Studio.

## Overview

The visualization MCAP files contain:
- **Robot body markers** - Rectangular body showing robot position and orientation
- **Wheel markers** - 4 wheels per robot with steering angles
- **Link markers** - Lines connecting body center to each wheel
- **Target markers** - Green circles showing target positions
- **ICR markers** - Instantaneous center of rotation
- **Training metrics** - Episode rewards, distances, success rates

## Quick Start

### Generate Visualization MCAP Files

To create visualization MCAP files from your trained models:

```bash
# For single robot
python scripts/generate_visualization_mcap.py --mode single --episodes 30

# For multi-robot (3 robots)
python scripts/generate_visualization_mcap.py --mode multi --episodes 30
```

This will create:
- `deliverables/single_robot_training_with_viz.mcap`
- `deliverables/multi_robot_training_with_viz.mcap`

### Options

- `--mode`: `single` or `multi` (default: `single`)
- `--episodes`: Number of evaluation episodes to record (default: 30)
- `--model`: Path to model file (auto-detected if not provided)
- `--output`: Output MCAP file path (auto-generated if not provided)
- `--record_every`: Record every N steps (default: 1, use 2-5 for larger files)

### Example with Custom Settings

```bash
# Record 50 episodes, every 2 steps
python scripts/generate_visualization_mcap.py \
    --mode single \
    --episodes 50 \
    --record_every 2 \
    --output deliverables/custom_viz.mcap
```

## Recording During Training

To record visualization markers **during training** (not just evaluation), use the `--record` flag:

```bash
# Single robot training with visualization recording
python train.py --mode single --record --mcap_output training_with_viz.mcap

# Multi-robot training with visualization recording
python train.py --mode multi --record --mcap_output training_multi_with_viz.mcap
```

This will record robot states throughout the entire training process, not just during evaluation episodes.

**Note:** Recording during training can create very large MCAP files. The code records every 10 steps by default to manage file size.

## Viewing in Foxglove Studio

1. **Open Foxglove Studio** (download from https://foxglove.dev/download)

2. **Open the MCAP file:**
   - Click "Open local file"
   - Select your visualization MCAP file (e.g., `single_robot_training_with_viz.mcap`)

3. **Add visualization panels:**
   - Click "+" to add a new panel
   - Select "3D" panel type
   - In the panel settings, select the `/visualization_markers` channel
   - You should now see the robot visualization

4. **Add metrics panel:**
   - Add a "Plot" panel
   - Select the `/training_metrics` channel
   - View rewards, episode lengths, etc.

### What You'll See

- **Robot body**: Blue rectangular body showing position and orientation
- **Wheels**: 4 colored wheels (red, green, blue, yellow) with steering angles
- **Links**: Gray lines connecting body center to each wheel
- **Targets**: Green circles at target positions
- **ICR**: Magenta sphere showing instantaneous center of rotation

## File Locations

- **Generated visualization MCAP files**: `deliverables/*_with_viz.mcap`
- **Metrics-only MCAP files**: `deliverables/*_training.mcap`
- **Trained models**: `models/single_robot/` and `models/multi_robot/`

## Troubleshooting

### "ModuleNotFoundError: No module named 'stable_baselines3'"

Install dependencies:
```bash
pip install -r requirements.txt
```

### MCAP file is too large

Use `--record_every` to record less frequently:
```bash
python scripts/generate_visualization_mcap.py --mode single --record_every 5
```

### Model not found

Check that models exist:
```bash
ls models/single_robot/*.zip
ls models/multi_robot/*.zip
```

If models don't exist, train them first:
```bash
python train.py --mode single
python train.py --mode multi
```

## Technical Details

### Marker Format

The markers are formatted as JSON objects compatible with Foxglove Studio:
- **Pose**: Position (x, y, z) and orientation (quaternion)
- **Scale**: Size in x, y, z dimensions
- **Color**: RGBA values (0.0-1.0)
- **Type**: Marker type (robot_body, wheel, link, target, icr)

### MCAP Structure

- **Channel**: `/visualization_markers` - Contains all robot visualization markers
- **Channel**: `/training_metrics` - Contains episode metrics (reward, distance, success, etc.)

### Recording Frequency

- **During training**: Records every 10 steps (configurable in `TrainingCallback`)
- **During evaluation**: Records every step by default (configurable with `--record_every`)

## Next Steps

1. Generate visualization MCAP files using the script above
2. Open in Foxglove Studio to verify visualization
3. Share the MCAP files with your team for review
4. For future training runs, use `--record` flag to capture visualization during training

