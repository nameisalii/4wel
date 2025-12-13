
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import argparse


def plot_from_evaluations(eval_file: str, output_file: str, mode: str = "single"):
    print(f"\n{'='*60}")
    print(f"Generating metrics plots for {mode}-robot training")
    print(f"{'='*60}")
    
    eval_path = Path(eval_file)
    if not eval_path.exists():
        print(f" Evaluation file not found: {eval_file}")
        return None
    
    print(f" Loading evaluation data from {eval_file}...")
    data = np.load(eval_file, allow_pickle=True)
    
    timesteps = data.get('timesteps', [])
    results = data.get('results', [])
    ep_lengths = data.get('ep_lengths', [])
    
    print(f"   Found {len(timesteps)} evaluation checkpoints")
    
    if hasattr(results, '__len__') and len(results) > 0:
        if hasattr(results[0], '__len__'):
            mean_rewards = [float(np.mean(r)) for r in results]
            std_rewards = [float(np.std(r)) for r in results]
        else:
            mean_rewards = [float(r) for r in results]
            std_rewards = [0.0] * len(results)
    else:
        print(" No results data found")
        return None
    
    if hasattr(ep_lengths, '__len__') and len(ep_lengths) > 0:
        if hasattr(ep_lengths[0], '__len__'):
            mean_ep_lengths = [float(np.mean(e)) for e in ep_lengths]
        else:
            mean_ep_lengths = [float(e) for e in ep_lengths]
    else:
        mean_ep_lengths = [0.0] * len(timesteps)
    
    success_rate = [1.0 if r > 0 else 0.0 for r in mean_rewards]
    
    print(f" Creating plots...")
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'{mode.capitalize()}-Robot Training Metrics', fontsize=16, fontweight='bold')
    
    axes[0, 0].plot(timesteps, mean_rewards, 'b-', alpha=0.6, linewidth=1.5, label='Mean Reward')
    if len(mean_rewards) > 1:
        axes[0, 0].fill_between(timesteps, 
                               np.array(mean_rewards) - np.array(std_rewards),
                               np.array(mean_rewards) + np.array(std_rewards),
                               alpha=0.2, color='blue', label='±1 Std Dev')
    
    if len(mean_rewards) > 10:
        window = min(20, len(mean_rewards) // 5)
        if window > 1:
            moving_avg = np.convolve(mean_rewards, np.ones(window)/window, mode='valid')
            moving_avg_steps = timesteps[window-1:]
            axes[0, 0].plot(moving_avg_steps, moving_avg, 'r-', linewidth=2.5, 
                           label=f'Moving Avg (window={window})')
    
    axes[0, 0].set_xlabel('Training Timestep', fontsize=11)
    axes[0, 0].set_ylabel('Mean Episode Reward', fontsize=11)
    axes[0, 0].set_title('Episode Rewards Over Time', fontsize=12, fontweight='bold')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    if len(success_rate) > 10:
        window = min(20, len(success_rate) // 5)
        if window > 1:
            success_moving_avg = np.convolve(success_rate, np.ones(window)/window, mode='valid')
            success_steps = timesteps[window-1:]
            axes[0, 1].plot(success_steps, success_moving_avg, 'g-', linewidth=2.5, 
                           label=f'Success Rate (window={window})')
        else:
            axes[0, 1].plot(timesteps, success_rate, 'g-', linewidth=1.5, alpha=0.6)
    else:
        axes[0, 1].plot(timesteps, success_rate, 'go', markersize=4)
    
    axes[0, 1].axhline(y=1.0, color='r', linestyle='--', linewidth=1.5, label='100% Success')
    axes[0, 1].set_xlabel('Training Timestep', fontsize=11)
    axes[0, 1].set_ylabel('Success Rate', fontsize=11)
    axes[0, 1].set_title('Success Rate Over Time', fontsize=12, fontweight='bold')
    axes[0, 1].set_ylim([-0.1, 1.1])
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    axes[1, 0].plot(timesteps, mean_ep_lengths, 'purple', alpha=0.6, linewidth=1.5, label='Mean Episode Length')
    
    if len(mean_ep_lengths) > 10:
        window = min(20, len(mean_ep_lengths) // 5)
        if window > 1:
            ep_moving_avg = np.convolve(mean_ep_lengths, np.ones(window)/window, mode='valid')
            ep_steps = timesteps[window-1:]
            axes[1, 0].plot(ep_steps, ep_moving_avg, 'r-', linewidth=2.5, 
                           label=f'Moving Avg (window={window})')
    
    axes[1, 0].set_xlabel('Training Timestep', fontsize=11)
    axes[1, 0].set_ylabel('Mean Episode Length (steps)', fontsize=11)
    axes[1, 0].set_title('Episode Length Over Time', fontsize=12, fontweight='bold')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    axes[1, 1].hist(mean_rewards, bins=min(30, len(mean_rewards)//2), 
                   color='skyblue', edgecolor='black', alpha=0.7)
    axes[1, 1].axvline(x=np.mean(mean_rewards), color='r', linestyle='--', 
                      linewidth=2, label=f'Mean: {np.mean(mean_rewards):.2f}')
    axes[1, 1].axvline(x=np.median(mean_rewards), color='g', linestyle='--', 
                      linewidth=2, label=f'Median: {np.median(mean_rewards):.2f}')
    axes[1, 1].set_xlabel('Episode Reward', fontsize=11)
    axes[1, 1].set_ylabel('Frequency', fontsize=11)
    axes[1, 1].set_title('Reward Distribution', fontsize=12, fontweight='bold')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✅ Plot saved to: {output_file}")
    
    print(f"\n Summary Statistics:")
    print(f"   Total evaluations: {len(timesteps)}")
    print(f"   Final mean reward: {mean_rewards[-1]:.2f} ± {std_rewards[-1]:.2f}")
    print(f"   Best mean reward: {max(mean_rewards):.2f}")
    print(f"   Final success rate: {np.mean(success_rate[-10:]):.1%}")
    print(f"   Final mean episode length: {mean_ep_lengths[-1]:.1f} steps")
    
    return output_file


def main():
    parser = argparse.ArgumentParser(description="Generate metrics plots from evaluation logs")
    parser.add_argument("--single", type=str, default="logs/single_robot/evaluations.npz",
                       help="Path to single robot evaluation file")
    parser.add_argument("--multi", type=str, default="logs/multi_robot/evaluations.npz",
                       help="Path to multi robot evaluation file")
    parser.add_argument("--output_dir", type=str, default="deliverables",
                       help="Output directory for plots")
    
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    generated_plots = []
    
    if Path(args.single).exists():
        output = output_dir / "single_robot_metrics.png"
        result = plot_from_evaluations(args.single, str(output), "single")
        if result:
            generated_plots.append(result)
    else:
        print(f" Single robot evaluation file not found: {args.single}")
    
    if Path(args.multi).exists():
        output = output_dir / "multi_robot_metrics.png"
        result = plot_from_evaluations(args.multi, str(output), "multi")
        if result:
            generated_plots.append(result)
    else:
        print(f"  Multi robot evaluation file not found: {args.multi}")
    
    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    
    if generated_plots:
        print(f"\n Generated {len(generated_plots)} plot(s):")
        for plot in generated_plots:
            size_kb = Path(plot).stat().st_size / 1024
            print(f"   • {plot} ({size_kb:.1f} KB)")
        print(f"\n Plots are ready to be included with deliverables!")
    else:
        print("\nNo plots were generated. Check that evaluation files exist.")
    
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

