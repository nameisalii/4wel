# Four-Wheel Robot Navigation with Reinforcement Learning

This project implements navigation control for a four-wheel robot with independent steering. The robot uses kinematic modeling and reinforcement learning to navigate to target positions, with support for both single-robot and multi-robot scenarios with collision avoidance.

## Project Overview

The system includes a kinematic model for a four-wheel robot where each wheel can steer independently, and the instantaneous center of rotation lies on the robot's y-axis. The robot learns to navigate using PPO reinforcement learning with realistic physical constraints including steering rate limits and wheel acceleration limits.

## Requirements

Install dependencies using pip:

```bash
pip install -r requirements.txt
```

Required packages:
- torch (2.0.0 or higher)
- gymnasium (0.29.0 or higher)
- numpy (1.24.0 or higher)
- matplotlib (3.7.0 or higher)
- mcap (0.1.0 or higher)
- stable-baselines3 (2.0.0 or higher)
- tensorboard (2.13.0 or higher)

## Core Components

### robot_kinematics.py
Implements the four-wheel robot kinematic model with independent steering. The model uses curvature and velocity as control inputs and calculates individual wheel steering angles based on the instantaneous center of rotation constraint.

### robot_env.py
Gymnasium environment for reinforcement learning. Provides observation space that includes robot pose, wheel states, and target position. For multi-robot scenarios, includes relative positions of other robots.

### train.py
Main training script supporting both single and multi-robot training modes. Uses PPO algorithm with custom network architectures and hyperparameters tuned for each scenario.

### visualize.py
Creates visualization markers for robot body, wheels, steering links, and targets. Supports MCAP format for visualization in Foxglove Studio.

## Usage

### Training a Single Robot

Train a policy for single robot navigation:

```bash
python train.py --mode single --episodes 10000
```

To record training data in MCAP format:

```bash
python train.py --mode single --episodes 10000 --record --mcap_output single_robot.mcap
```

### Training Multiple Robots

Train a policy for three robots with collision avoidance:

```bash
python train.py --mode multi --episodes 20000 --num_robots 3 --record --mcap_output multi_robot.mcap
```

### Testing a Trained Model

Test a trained model on new episodes:

```bash
python train.py --test ./models/single_robot/final_model --mode single --test_episodes 10
```

### Monitoring Training Progress

Use TensorBoard to monitor training metrics:

```bash
tensorboard --logdir ./tensorboard_logs/
```

Then open http://localhost:6006 in your browser.

## Robot Model Details

The robot kinematic model has the following characteristics:

- Control inputs: curvature and velocity
- Four independently steered wheels
- Instantaneous center of rotation constrained to robot y-axis
- Steering rate limit: 0.5 rad/s
- Wheel acceleration limit: 2.0 m/s²
- Maximum velocity: 2.0 m/s
- Maximum steering angle: 60 degrees

## Environment Details

### Observation Space

Single robot (10 dimensions):
- Robot position: x, y
- Robot orientation: theta
- Robot velocity: v
- Wheel steering angles: delta_fl, delta_fr, delta_rl, delta_rr
- Target relative position: target_x, target_y

Multi-robot: Each robot's observation includes the above plus relative positions of all other robots.

### Action Space

Continuous action space with two values per robot:
- Curvature: range [-2.0, 2.0]
- Velocity: range [-2.0, 2.0]

### Reward Function

The reward function includes:
- Distance to target (negative reward that decreases as robot approaches)
- Success bonus when reaching target
- Small penalties for excessive velocity and steering
- For multi-robot: collision penalties and separation rewards

### Episode Termination

Episodes terminate when:
- All robots reach their targets within 0.3m threshold (success)
- Maximum episode length of 500 steps is reached

## File Structure

- Core implementation files (robot_kinematics.py, robot_env.py, train.py, visualize.py)
- Training utilities (mcap_writer.py, example_usage.py, test_kinematics.py)
- Trained models in models/ directory
- Training logs in logs/ directory
- Model checkpoints in checkpoints/ directory
- TensorBoard logs in tensorboard_logs/ directory
- Deliverables in deliverables/ directory

## Code Documentation

For simple explanations of what each code file does, see [CODE_DOCUMENTATION.md](CODE_DOCUMENTATION.md).

## Training Results

The project includes trained models and evaluation data for both single-robot and multi-robot navigation scenarios. Training data is recorded in MCAP format and can be visualized in Foxglove Studio or analyzed using the included Python scripts.

## Hyperparameters

Single robot training uses standard PPO hyperparameters with a [256, 256, 128] network architecture.

Multi-robot training uses optimized hyperparameters:
- Lower learning rate (1e-4) for training stability
- Larger batch size (256) for better gradient estimates
- Increased entropy coefficient (0.02) for better exploration
- Gradient clipping (0.5) to prevent instability
- Deeper network [512, 512, 256] to handle increased complexity
