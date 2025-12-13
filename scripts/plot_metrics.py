"""
Plot training metrics from MCAP/JSON data
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Optional


def plot_training_metrics(json_file: str, output_file: Optional[str] = None):
    """Plot training metrics from JSON file"""
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    metrics = data.get('metrics', [])
    
    if not metrics:
        print("No metrics found in file")
        return
    
    # Extract metrics
    steps = [m['step'] for m in metrics]
    rewards = [m['reward'] for m in metrics]
    distances = [m['distance'] for m in metrics]
    successes = [m['success'] for m in metrics]
    episode_lengths = [m['episode_length'] for m in metrics]
    
    # Create plots
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Reward over time
    axes[0, 0].plot(steps, rewards, alpha=0.6, linewidth=0.5)
    if len(rewards) > 100:
        # Moving average
        window = min(100, len(rewards) // 10)
        moving_avg = np.convolve(rewards, np.ones(window)/window, mode='valid')
        axes[0, 0].plot(steps[window-1:], moving_avg, 'r-', linewidth=2, label='Moving Avg')
        axes[0, 0].legend()
    axes[0, 0].set_xlabel('Step')
    axes[0, 0].set_ylabel('Reward')
    axes[0, 0].set_title('Episode Rewards')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Distance to target
    axes[0, 1].plot(steps, distances, alpha=0.6, linewidth=0.5, color='green')
    if len(distances) > 100:
        window = min(100, len(distances) // 10)
        moving_avg = np.convolve(distances, np.ones(window)/window, mode='valid')
        axes[0, 1].plot(steps[window-1:], moving_avg, 'r-', linewidth=2, label='Moving Avg')
        axes[0, 1].legend()
    axes[0, 1].set_xlabel('Step')
    axes[0, 1].set_ylabel('Distance to Target (m)')
    axes[0, 1].set_title('Distance to Target')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Success rate
    if len(successes) > 100:
        window = min(100, len(successes) // 10)
        success_rate = np.convolve(successes, np.ones(window)/window, mode='valid')
        axes[1, 0].plot(steps[window-1:], success_rate, 'g-', linewidth=2)
        axes[1, 0].axhline(y=1.0, color='r', linestyle='--', label='100%')
        axes[1, 0].legend()
    else:
        axes[1, 0].plot(steps, successes, 'go', markersize=3)
    axes[1, 0].set_xlabel('Step')
    axes[1, 0].set_ylabel('Success Rate')
    axes[1, 0].set_title('Success Rate (Moving Average)')
    axes[1, 0].set_ylim([-0.1, 1.1])
    axes[1, 0].grid(True, alpha=0.3)
    
    # Episode length
    axes[1, 1].plot(steps, episode_lengths, alpha=0.6, linewidth=0.5, color='purple')
    if len(episode_lengths) > 100:
        window = min(100, len(episode_lengths) // 10)
        moving_avg = np.convolve(episode_lengths, np.ones(window)/window, mode='valid')
        axes[1, 1].plot(steps[window-1:], moving_avg, 'r-', linewidth=2, label='Moving Avg')
        axes[1, 1].legend()
    axes[1, 1].set_xlabel('Step')
    axes[1, 1].set_ylabel('Episode Length')
    axes[1, 1].set_title('Episode Length')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=150)
        print(f"Plot saved to {output_file}")
    else:
        plt.show()


def plot_episode_trajectory(json_file: str, episode_idx: int = -1, output_file: Optional[str] = None):
    """Plot robot trajectory for a specific episode"""
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    messages = data.get('messages', [])
    
    # Find episode markers
    episode_markers = []
    for msg in messages:
        if msg.get('channel') == 'visualization_markers':
            episode_markers.append(msg)
    
    if not episode_markers:
        print("No episode markers found")
        return
    
    # Get specified episode (default: last)
    if episode_idx < 0:
        episode_idx = len(episode_markers) + episode_idx
    
    if episode_idx >= len(episode_markers):
        print(f"Episode {episode_idx} not found")
        return
    
    markers = episode_markers[episode_idx]['data']
    
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Extract robot and target positions
    robot_positions = []
    target_positions = []
    
    for marker in markers:
        if marker['type'] == 'robot_body':
            pose = marker['pose']
            robot_positions.append([pose['x'], pose['y']])
        elif marker['type'] == 'target':
            pos = marker['position']
            target_positions.append([pos['x'], pos['y']])
    
    if robot_positions:
        robot_positions = np.array(robot_positions)
        ax.plot(robot_positions[:, 0], robot_positions[:, 1], 'b-', linewidth=2, label='Robot Path')
        ax.plot(robot_positions[0, 0], robot_positions[0, 1], 'go', markersize=10, label='Start')
        ax.plot(robot_positions[-1, 0], robot_positions[-1, 1], 'ro', markersize=10, label='End')
    
    if target_positions:
        target_positions = np.array(target_positions)
        for i, target in enumerate(target_positions):
            circle = plt.Circle(target, 0.3, color='green', alpha=0.3, label='Target' if i == 0 else '')
            ax.add_patch(circle)
            ax.plot(target[0], target[1], 'gx', markersize=15, markeredgewidth=3)
    
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_title(f'Episode {episode_idx} Trajectory')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=150)
        print(f"Trajectory plot saved to {output_file}")
    else:
        plt.show()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Plot training metrics")
    parser.add_argument("json_file", type=str, help="JSON file with training data")
    parser.add_argument("--plot_type", type=str, choices=["metrics", "trajectory", "both"], 
                       default="both", help="Type of plot to generate")
    parser.add_argument("--episode", type=int, default=-1, help="Episode index for trajectory plot")
    parser.add_argument("--output", type=str, default=None, help="Output file path")
    
    args = parser.parse_args()
    
    if args.plot_type in ["metrics", "both"]:
        plot_training_metrics(args.json_file, 
                            args.output if args.plot_type == "metrics" else None)
    
    if args.plot_type in ["trajectory", "both"]:
        traj_output = args.output if args.plot_type == "trajectory" else None
        plot_episode_trajectory(args.json_file, args.episode, traj_output)

