
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from pathlib import Path
from stable_baselines3 import PPO
from robot_env import RobotNavigationEnv
from robot_kinematics import FourWheelKinematics
from visualize import MCAPVisualizer
from mcap_writer import MCAPWriter
import time
import argparse


def create_visualization_mcap(model_path: str, 
                             output_file: str,
                             mode: str = "single",
                             num_episodes: int = 20,
                             num_robots: int = 1,
                             record_every_n_steps: int = 1):
    print(f"\n{'='*70}")
    print(f"Creating Visualization MCAP: {mode}-robot mode")
    print(f"{'='*70}")
    print(f"Model: {model_path}")
    print(f"Output: {output_file}")
    print(f"Episodes: {num_episodes}")
    print(f"Record every {record_every_n_steps} step(s)")
    print(f"{'='*70}\n")
    
    if not Path(model_path).exists():
        print(f"❌ Model not found: {model_path}")
        return None
    
    print(f"📦 Loading model from {model_path}...")
    try:
        model = PPO.load(model_path)
        print("✅ Model loaded successfully")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None
    
    print(f"🌍 Creating environment ({num_robots} robot(s))...")
    env = RobotNavigationEnv(num_robots=num_robots)
    print("✅ Environment created")
    
    print(f"📝 Initializing MCAP writer...")
    mcap_writer = MCAPWriter(output_file)
    visualizer = MCAPVisualizer()
    print("✅ MCAP writer ready")
    
    total_steps = 0
    successful_episodes = 0
    episode_rewards = []
    
    print(f"\n🎬 Starting {num_episodes} evaluation episodes...\n")
    
    for episode in range(num_episodes):
        obs, info = env.reset()
        done = False
        episode_reward = 0.0
        episode_steps = 0
        episode_start_time = time.time()
        
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            episode_reward += reward
            episode_steps += 1
            total_steps += 1
            
            if episode_steps % record_every_n_steps == 0:
                robots = env.robots
                targets = env.targets
                
                markers = visualizer.create_all_markers(robots, targets, timestamp=time.time())
                
                mcap_writer.add_marker_message(markers, timestamp=time.time())
            
            if done:
                success = info.get('success', False)
                if success:
                    successful_episodes += 1
                
                distances = []
                for i, robot in enumerate(env.robots):
                    state = robot.get_state()
                    target = env.targets[i]
                    dist = np.sqrt((state.x - target[0])**2 + (state.y - target[1])**2)
                    distances.append(dist)
                final_distance = np.mean(distances) if distances else 0.0
                
                mcap_writer.add_metrics(
                    step=total_steps,
                    reward=episode_reward,
                    distance=final_distance,
                    success=success,
                    episode_length=episode_steps
                )
                
                episode_rewards.append(episode_reward)
                
                status = "✅ SUCCESS" if success else "❌ FAILED"
                print(f"Episode {episode+1:3d}/{num_episodes}: {status} | "
                      f"Reward: {episode_reward:7.2f} | "
                      f"Steps: {episode_steps:3d} | "
                      f"Distance: {final_distance:.2f}m")
        
        markers = visualizer.create_all_markers(env.robots, env.targets, timestamp=time.time())
        mcap_writer.add_marker_message(markers, timestamp=time.time())
    
    print(f"\n💾 Saving MCAP file...")
    result = mcap_writer.save()
    
    if result:
        file_size_mb = Path(output_file).stat().st_size / (1024 * 1024)
        
        print(f"\n{'='*70}")
        print("✅ MCAP File Created Successfully!")
        print(f"{'='*70}")
        print(f"📁 File: {output_file}")
        print(f"📊 Size: {file_size_mb:.2f} MB")
        print(f"📈 Episodes: {num_episodes}")
        print(f"👣 Total steps: {total_steps}")
        print(f"✅ Successful episodes: {successful_episodes}/{num_episodes} ({100*successful_episodes/num_episodes:.1f}%)")
        print(f"💰 Mean reward: {np.mean(episode_rewards):.2f} ± {np.std(episode_rewards):.2f}")
        print(f"🎯 Best reward: {max(episode_rewards):.2f}")
        print(f"\n📝 This file contains:")
        print(f"   • Robot body markers")
        print(f"   • Wheel markers with steering angles")
        print(f"   • Link markers (body to wheels)")
        print(f"   • Target markers")
        print(f"   • ICR markers")
        print(f"   • Training metrics")
        print(f"\n🎬 Ready to view in Foxglove Studio!")
        print(f"{'='*70}\n")
        
        return output_file
    else:
        print(f"\n❌ Failed to save MCAP file")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Create MCAP files with robot visualization from trained models"
    )
    parser.add_argument("--mode", type=str, choices=["single", "multi"], 
                       default="single", help="Single or multi-robot mode")
    parser.add_argument("--model", type=str, default=None,
                       help="Path to model file (auto-detected if not provided)")
    parser.add_argument("--output", type=str, default=None,
                       help="Output MCAP file path (auto-generated if not provided)")
    parser.add_argument("--episodes", type=int, default=20,
                       help="Number of episodes to record")
    parser.add_argument("--num_robots", type=int, default=1,
                       help="Number of robots (for multi-robot mode)")
    parser.add_argument("--record_every", type=int, default=1,
                       help="Record every N steps (1 = every step, 2 = every other step)")
    
    args = parser.parse_args()
    
    if args.model is None:
        if args.mode == "single":
            model_path = "models/single_robot/best_model.zip"
            if not Path(model_path).exists():
                model_path = "models/single_robot/final_model.zip"
        else:
            model_path = "models/multi_robot/best_model.zip"
            if not Path(model_path).exists():
                model_path = "models/multi_robot/final_model.zip"
    else:
        model_path = args.model
    
    if args.output is None:
        output_file = f"deliverables/{args.mode}_robot_training_with_viz.mcap"
    else:
        output_file = args.output
    
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    if args.mode == "multi" and args.num_robots == 1:
        args.num_robots = 3
    
    result = create_visualization_mcap(
        model_path=model_path,
        output_file=output_file,
        mode=args.mode,
        num_episodes=args.episodes,
        num_robots=args.num_robots,
        record_every_n_steps=args.record_every
    )
    
    if result:
        print(f"\n✅ Success! MCAP file created: {result}")
        print(f"\n📖 Next steps:")
        print(f"   1. Open Foxglove Studio")
        print(f"   2. Click 'Open local file'")
        print(f"   3. Select: {result}")
        print(f"   4. You'll see robot visualization with body, wheels, links, and targets!")
    else:
        print(f"\n❌ Failed to create MCAP file")
        sys.exit(1)


if __name__ == "__main__":
    main()

