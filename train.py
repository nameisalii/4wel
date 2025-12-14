import argparse
import numpy as np
import torch
import torch.nn as nn
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import EvalCallback, CheckpointCallback, BaseCallback
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.logger import configure
import os
from typing import List, Optional
import json
import time

from robot_env import RobotNavigationEnv
from robot_kinematics import FourWheelKinematics
from visualize import MCAPVisualizer, save_markers_to_mcap
from mcap_writer import MCAPWriter


class TrainingCallback(BaseCallback):
    
    def __init__(self, recorder, env, verbose=0, record_every_n_steps=10):
        super().__init__(verbose)
        self.recorder = recorder
        self.env = env
        self.record_every_n_steps = record_every_n_steps
        self.step_count = 0
    
    def _on_step(self) -> bool:
        self.step_count += 1
        # Record visualization markers during training
        if self.recorder.record and self.step_count % self.record_every_n_steps == 0:
            if hasattr(self.env, 'envs') and len(self.env.envs) > 0:
                if hasattr(self.env.envs[0], 'unwrapped'):
                    env_unwrapped = self.env.envs[0].unwrapped
                    if isinstance(env_unwrapped, RobotNavigationEnv):
                        robots = env_unwrapped.robots
                        targets = env_unwrapped.targets
                        self.recorder.record_step(robots, targets)
        return True


class TrainingRecorder:
    
    def __init__(self, record: bool = False, output_file: str = "training.mcap"):
        self.record = record
        self.output_file = output_file
        self.episodes = []
        self.visualizer = MCAPVisualizer()
        self.mcap_writer = MCAPWriter(output_file) if record else None
        self.metrics = {
            'episode_rewards': [],
            'episode_lengths': [],
            'success_rate': [],
            'distances': []
        }
        self.current_episode_markers = []
    
    def record_step(self, robots: List[FourWheelKinematics], targets: np.ndarray):
        if not self.record or self.mcap_writer is None:
            return
        
        markers = self.visualizer.create_all_markers(robots, targets)
        self.mcap_writer.add_marker_message(markers)
        self.current_episode_markers.append(markers)
    
    def record_episode(self, robots: List[FourWheelKinematics], 
                      targets: np.ndarray,
                      episode_reward: float,
                      episode_length: int,
                      success: bool,
                      distance: float):
   
        if not self.record:
            return
        
        episode_data = {
            'timestamp': time.time(),
            'robots': [],
            'targets': targets.tolist(),
            'reward': episode_reward,
            'length': episode_length,
            'success': success
        }
        
        for robot in robots:
            state = robot.get_state()
            episode_data['robots'].append({
                'x': state.x,
                'y': state.y,
                'theta': state.theta,
                'v': state.v,
                'delta_fl': state.delta_fl,
                'delta_fr': state.delta_fr,
                'delta_rl': state.delta_rl,
                'delta_rr': state.delta_rr
            })
        
        self.episodes.append(episode_data)
        
        if self.mcap_writer:
            self.mcap_writer.add_metrics(
                step=len(self.episodes),
                reward=episode_reward,
                distance=distance,
                success=success,
                episode_length=episode_length
            )
        
        self.current_episode_markers = []
    
    def record_metrics(self, reward: float, length: int, success: bool, distance: float):
        self.metrics['episode_rewards'].append(reward)
        self.metrics['episode_lengths'].append(length)
        self.metrics['success_rate'].append(1.0 if success else 0.0)
        self.metrics['distances'].append(distance)
    
    def save(self):
        if not self.record:
            return
        
        if self.mcap_writer:
            self.mcap_writer.save()
        
        output_json = self.output_file.replace('.mcap', '_episodes.json')
        with open(output_json, 'w') as f:
            json.dump(self.episodes, f, indent=2)
        
        metrics_file = self.output_file.replace('.mcap', '_metrics.json')
        with open(metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        print(f"Training data saved:")
        print(f"  MCAP: {self.output_file.replace('.mcap', '.json')}")
        print(f"  Episodes: {output_json}")
        print(f"  Metrics: {metrics_file}")


def make_env(num_robots: int = 1, rank: int = 0, seed: int = 0):
    def _init():
        env = RobotNavigationEnv(num_robots=num_robots)
        env = Monitor(env, filename=None, allow_early_resets=True)
        env.reset(seed=seed + rank)
        return env
    return _init


def train_single_robot(total_timesteps: int = 5000000,  # Changed from 100000 to 5000000
                      record: bool = False,
                      output_file: str = "training.mcap"):
    print("Training single robot navigation...")
    
    env = DummyVecEnv([make_env(num_robots=1, seed=42)])
    eval_env = DummyVecEnv([make_env(num_robots=1, seed=123)])
    recorder = TrainingRecorder(record=record, output_file=output_file)
    
    policy_kwargs = dict(
        net_arch=[256, 256, 128],
        activation_fn=nn.Tanh
    )
    
    model = PPO(
        "MlpPolicy",
        env,
        policy_kwargs=policy_kwargs,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.01,
        vf_coef=0.5,
        verbose=1,
        tensorboard_log="./tensorboard_logs/"
    )
    
    
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path="./models/single_robot/",
        log_path="./logs/single_robot/",
        eval_freq=5000,
        deterministic=True,
        render=False
    )
    
    checkpoint_callback = CheckpointCallback(
        save_freq=10000,
        save_path="./checkpoints/single_robot/",
        name_prefix="ppo_single"
    )
    
    # Record visualization every 10 steps during training to avoid too much data
    training_callback = TrainingCallback(recorder, env, record_every_n_steps=10)
    
    try:
        model.learn(
            total_timesteps=total_timesteps,
            callback=[eval_callback, checkpoint_callback, training_callback],
            progress_bar=True
        )
    except ImportError:
        model.learn(
            total_timesteps=total_timesteps,
            callback=[eval_callback, checkpoint_callback, training_callback],
            progress_bar=False
        )
    
    if record:
        recorder.save()
    
    model.save("./models/single_robot/final_model")
    print("Training complete! Model saved to ./models/single_robot/final_model")
    
    return model


def train_multi_robot(num_robots: int = 3,
                     total_timesteps: int = 10000000,  # Changed from 200000 to 10000000
                     record: bool = False,
                     output_file: str = "training_multi.mcap"):
    print(f"Training {num_robots} robots with collision avoidance...")
    
    env = DummyVecEnv([make_env(num_robots=num_robots, seed=42)])
    eval_env = DummyVecEnv([make_env(num_robots=num_robots, seed=123)])    
    recorder = TrainingRecorder(record=record, output_file=output_file)
    
    policy_kwargs = dict(
        net_arch=[512, 512, 256],
        activation_fn=nn.Tanh
    )
    
    model = PPO(
        "MlpPolicy",
        env,
        policy_kwargs=policy_kwargs,
        learning_rate=1e-4,
        n_steps=4096, 
        batch_size=256,
        n_epochs=15,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.02,
        vf_coef=0.5,
        max_grad_norm=0.5,
        verbose=1,
        tensorboard_log="./tensorboard_logs/"
    )
    
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path="./models/multi_robot/",
        log_path="./logs/multi_robot/",
        eval_freq=10000,
        deterministic=True,
        render=False
    )
    
    checkpoint_callback = CheckpointCallback(
        save_freq=20000,
        save_path="./checkpoints/multi_robot/",
        name_prefix="ppo_multi"
    )
    
    # Record visualization every 10 steps during training to avoid too much data
    training_callback = TrainingCallback(recorder, env, record_every_n_steps=10)
    
    try:
        model.learn(
            total_timesteps=total_timesteps,
            callback=[eval_callback, checkpoint_callback, training_callback],
            progress_bar=True
        )
    except ImportError:
        model.learn(
            total_timesteps=total_timesteps,
            callback=[eval_callback, checkpoint_callback, training_callback],
            progress_bar=False
        )
    
    if record:
        recorder.save()
    
    model.save("./models/multi_robot/final_model")
    print(f"Training complete! Model saved to ./models/multi_robot/final_model")
    
    return model


def test_model(model_path: str, num_robots: int = 1, num_episodes: int = 10):
    print(f"Testing model: {model_path}")
    model = PPO.load(model_path)
    
    env = RobotNavigationEnv(num_robots=num_robots)
    recorder = TrainingRecorder(record=True, output_file="test.mcap")
    
    successes = 0
    total_reward = 0
    
    for episode in range(num_episodes):
        obs, info = env.reset()
        episode_reward = 0
        episode_length = 0
        
        robots_before = [env.robots[i].get_state() for i in range(num_robots)]
        
        done = False
        while not done:
            if num_robots == 1:
                action, _ = model.predict(obs, deterministic=True)
            else:
                action, _ = model.predict(obs, deterministic=True)
                if action.shape == (num_robots * 2,):
                    action = action.reshape(num_robots, 2)
            
            obs, reward, terminated, truncated, info = env.step(action)
            episode_reward += reward
            episode_length += 1
            done = terminated or truncated
        
        robots_after = [env.robots[i] for i in range(num_robots)]
        targets = env.targets
        success = info.get('success', False)
        distance = info.get('distances', [float('inf')])[0] if num_robots == 1 else max(info.get('distances', [float('inf')]))
        
        recorder.record_episode(robots_after, targets, episode_reward, episode_length, success, distance)
        
        if success:
            successes += 1
        total_reward += episode_reward
        
        print(f"Episode {episode + 1}: Reward={episode_reward:.2f}, Length={episode_length}, Success={success}")
    
    recorder.save()
    
    print(f"\nTest Results:")
    print(f"  Success Rate: {successes}/{num_episodes} ({100*successes/num_episodes:.1f}%)")
    print(f"  Average Reward: {total_reward/num_episodes:.2f}")


def main():
    parser = argparse.ArgumentParser(description="Train 4-wheel robot navigation")
    parser.add_argument("--mode", type=str, choices=["single", "multi"], default="single",
                       help="Training mode: single or multi robot")
    parser.add_argument("--episodes", type=int, default=30000,  # Changed from 10000 to 30000
                       help="Number of training episodes (approximate)")
    parser.add_argument("--num_robots", type=int, default=3,
                       help="Number of robots for multi-robot mode")
    parser.add_argument("--record", action="store_true",
                       help="Record training process to MCAP")
    parser.add_argument("--mcap_output", type=str, default="training.mcap",
                       help="Output MCAP file")
    parser.add_argument("--test", type=str, default=None,
                       help="Test a trained model (provide path)")
    parser.add_argument("--test_episodes", type=int, default=10,
                       help="Number of test episodes")
    
    args = parser.parse_args()
    
    os.makedirs("./models/single_robot", exist_ok=True)
    os.makedirs("./models/multi_robot", exist_ok=True)
    os.makedirs("./logs", exist_ok=True)
    os.makedirs("./checkpoints", exist_ok=True)
    os.makedirs("./tensorboard_logs", exist_ok=True)
    
    if args.test:
        num_robots = 1 if args.mode == "single" else args.num_robots
        test_model(args.test, num_robots, args.test_episodes)
    elif args.mode == "single":
        timesteps = args.episodes * 500  
        train_single_robot(timesteps, args.record, args.mcap_output)
    else:
        timesteps = args.episodes * 1000  
        train_multi_robot(args.num_robots, timesteps, args.record, args.mcap_output)


if __name__ == "__main__":
    main()

