# Training Results and Deliverables

This directory contains training results from the robot navigation reinforcement learning experiments. The data is organized and ready for analysis in Foxglove Studio.

## MCAP Recording Files

The training results are recorded in MCAP format for visualization in Foxglove Studio.

### MCAP Files with Full Robot Visualization ⭐ RECOMMENDED

These files contain complete robot state visualization including robot body, wheels, links, and targets.

#### single_robot_training_with_viz.mcap
**Complete visualization MCAP for single robot training.** This file contains full robot state visualization during evaluation episodes, showing the robot body, wheels, steering links, and target positions.

File details:
- Contains: Robot body, wheels, links, targets, ICR markers
- Channels: /visualization_markers and /training_metrics
- Format: Binary MCAP (opens in Foxglove Studio)
- **This is the recommended file for viewing robot visualization**

#### multi_robot_training_with_viz.mcap
**Complete visualization MCAP for multi-robot training.** This file contains full visualization for all 3 robots during evaluation episodes, showing how they navigate and avoid collisions.

File details:
- Contains: All 3 robots with full visualization (body, wheels, links, targets)
- Channels: /visualization_markers and /training_metrics
- Format: Binary MCAP (opens in Foxglove Studio)
- **This is the recommended file for viewing multi-robot visualization**

### MCAP Files with Metrics Only

These files contain training metrics but not robot visualization markers.

#### single_robot_training.mcap
Training data for single robot navigation. This file contains 189 evaluation checkpoints captured during training, totaling 208 messages across 2 channels. The data shows the progression of learning as the robot improves at navigating to target positions.

File details:
- Size: 12 KB
- Total messages: 208
- Evaluation checkpoints: 189
- Channels: /training_metrics and /episode_visualization
- **Note:** Does not contain robot visualization markers

#### multi_robot_training.mcap
Training data for three-robot navigation with collision avoidance. This file contains 96 evaluation checkpoints, totaling 106 messages across 2 channels. The data demonstrates how multiple robots learn to navigate to individual targets while avoiding collisions with each other.

File details:
- Size: 6.3 KB
- Total messages: 106
- Evaluation checkpoints: 96
- Channels: /training_metrics and /episode_visualization
- **Note:** Does not contain robot visualization markers

## Metrics Plots

### single_robot_metrics.png
Training metrics visualization for single robot navigation. Contains:
- Episode rewards over time
- Success rate over time
- Episode length over time
- Reward distribution histogram

### multi_robot_metrics.png
Training metrics visualization for multi-robot navigation. Contains:
- Episode rewards over time
- Success rate over time
- Episode length over time
- Reward distribution histogram

## Viewing in Foxglove Studio

### Recommended: View Visualization MCAP Files

To view the complete robot visualization:

1. Download Foxglove Studio from https://foxglove.dev/download
2. Open Foxglove Studio
3. Click "Open local file"
4. Select `single_robot_training_with_viz.mcap` or `multi_robot_training_with_viz.mcap`
5. Add visualization panels:
   - Add "3D" or "Image" panel for robot visualization
   - Select `/visualization_markers` channel
   - Scrub timeline to see robot movement
6. Add "Plot" panel for metrics:
   - Select `/training_metrics` channel
   - View rewards, episode lengths, etc.

**What you'll see:**
- Robot body (rectangular body)
- 4 wheels with steering angles
- Links connecting body to wheels
- Target positions (green circles)
- ICR (instantaneous center of rotation)
- Training metrics over time

### Viewing Metrics-Only MCAP Files

To view training metrics only:

1. Open Foxglove Studio
2. Click "Open local file"
3. Select `single_robot_training.mcap` or `multi_robot_training.mcap`
4. Add "Plot" panel
5. Select `/training_metrics` channel

**What you'll see:**
- Training progress over time
- Reward values at each evaluation
- Episode length statistics
- Success indicators with color coding

**Note:** These files do not contain robot visualization markers.

## Channel Information

### Visualization MCAP Files (with_viz.mcap)

#### /visualization_markers
Contains complete robot state visualization:
- Robot body markers (rectangular body with corners)
- Wheel markers (4 wheels with positions and steering angles)
- Link markers (connecting body center to each wheel)
- Target markers (green circles at target positions)
- ICR markers (instantaneous center of rotation)

#### /training_metrics
Contains quantitative training data:
- Episode reward
- Distance to target
- Success indicator
- Episode length
- Training timestep

### Metrics-Only MCAP Files

#### /training_metrics
Contains quantitative training data:
- Current training timestep
- Mean reward across evaluation episodes
- Standard deviation of rewards
- Mean episode length
- Evaluation index number

#### /episode_visualization
Contains visual markers:
- Evaluation checkpoint markers
- Color-coded indicators (green for positive rewards, red for negative)
- Text annotations with reward values

## Training Logs

### logs/single_robot/evaluations.npz
Raw evaluation data from single robot training. This NumPy compressed file contains arrays for timesteps, results, and episode lengths. The data can be loaded in Python using numpy.load().

Evaluation checkpoints: 189

### logs/multi_robot/evaluations.npz
Raw evaluation data from multi-robot training. Contains timesteps, results, and episode lengths for the three-robot collision avoidance training.

Evaluation checkpoints: 96

### logs/tensorboard_logs/
TensorBoard event files from multiple training runs. These files contain detailed training metrics including rewards, losses, and policy performance data.

To view TensorBoard logs:
```bash
tensorboard --logdir logs/tensorboard_logs/
```

Then open http://localhost:6006 in your browser.

## Training Summary

### Single Robot Training
The single robot was trained to navigate from random starting positions to random target positions. Training shows clear improvement over time, with rewards increasing and episode lengths decreasing as the robot learns efficient navigation strategies.

### Multi-Robot Training
Three robots were trained simultaneously to navigate to individual targets while avoiding collisions. The training required optimized hyperparameters including reduced learning rate, increased batch size, and enhanced exploration coefficient to handle the increased complexity of multi-agent coordination.

## Data Format Details

### MCAP Files
- Format: Binary MCAP
- Schema: JSON encoding
- Timestamp precision: Nanoseconds
- Compatible with: Foxglove Studio

### NPZ Files
- Format: NumPy compressed
- Arrays: timesteps (int), results (float), episode_lengths (int)
- Load with: np.load('filename.npz')

### TensorBoard Files
- Format: TensorBoard event files
- View with: TensorBoard web interface

## File Validation

All MCAP files have been validated for format correctness and can be opened directly in Foxglove Studio. The files contain properly formatted messages with valid timestamps and channel information.
