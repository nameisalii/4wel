import numpy as np
from robot_kinematics import FourWheelKinematics
from robot_env import RobotNavigationEnv


def example_kinematic_control():
    print("=" * 60)
    print("Example: Manual Kinematic Control")

    robot = FourWheelKinematics()
    robot.reset(0, 0, 0)
    
    print("\nInitial state:")
    state = robot.get_state()
    print(f"  Position: ({state.x:.2f}, {state.y:.2f})")
    print(f"  Orientation: {state.theta:.2f} rad")
    
    maneuvers = [
        (0.0, 1.0, 20),
        (0.5, 1.0, 30),
        (0.0, 1.0, 20),
        (-0.5, 1.0, 30),
    ]
    
    print("\nExecuting maneuvers...")
    for i, (curvature, velocity, steps) in enumerate(maneuvers):
        print(f"\nManeuver {i+1}: curvature={curvature:.1f}, velocity={velocity:.1f}")
        for _ in range(steps):
            robot.step(curvature, velocity, dt=0.1)
        
        state = robot.get_state()
        print(f"  Position: ({state.x:.2f}, {state.y:.2f})")
        print(f"  Steering angles: delta_fl={state.delta_fl:.3f}, delta_fr={state.delta_fr:.3f}")
        
        icr = robot.get_icr_position()
        if icr:
            print(f"  ICR: ({icr[0]:.2f}, {icr[1]:.2f})")
    
    print("\nFinal state:")
    state = robot.get_state()
    print(f"  Position: ({state.x:.2f}, {state.y:.2f})")
    print(f"  Orientation: {state.theta:.2f} rad ({np.degrees(state.theta):.1f}°)")
    print("=" * 60 + "\n")


def example_rl_environment():
    print("=" * 60)
    print("Example: RL Environment")

    env = RobotNavigationEnv(num_robots=1, initial_range=5.0)
    
    obs, info = env.reset()
    print(f"\nObservation shape: {obs.shape}")
    print(f"Observation space: {env.observation_space}")
    print(f"Action space: {env.action_space}")
    
    robot = env.robots[0]
    state = robot.get_state()
    target = env.targets[0]
    
    print(f"\nInitial robot position: ({state.x:.2f}, {state.y:.2f})")
    print(f"Target position: ({target[0]:.2f}, {target[1]:.2f})")
    
    print("\nTaking random actions...")
    for step in range(10):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        
        state = robot.get_state()
        distance = np.sqrt((state.x - target[0])**2 + (state.y - target[1])**2)
        
        print(f"Step {step+1}: action=({action[0]:.2f}, {action[1]:.2f}), "
              f"reward={reward:.2f}, distance={distance:.2f}m")
        
        if terminated:
            print("  Target reached!")
            break
    
    print("=" * 60 + "\n")


def example_multi_robot():
    print("=" * 60)
    print("Example: Multi-Robot Environment")
    print("=" * 60)
    
    env = RobotNavigationEnv(num_robots=3, initial_range=8.0)
    obs, info = env.reset()
    
    print(f"\nNumber of robots: {env.num_robots}")
    print(f"Observation shape: {obs.shape}")
    print(f"Action space: {env.action_space}")
    
    print("\nInitial positions:")
    for i, robot in enumerate(env.robots):
        state = robot.get_state()
        target = env.targets[i]
        distance = np.sqrt((state.x - target[0])**2 + (state.y - target[1])**2)
        print(f"  Robot {i+1}: pos=({state.x:.2f}, {state.y:.2f}), "
              f"target=({target[0]:.2f}, {target[1]:.2f}), distance={distance:.2f}m")
    
    print("\nTaking actions...")
    for step in range(5):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        
        print(f"\nStep {step+1}:")
        for i, robot in enumerate(env.robots):
            state = robot.get_state()
            target = env.targets[i]
            distance = np.sqrt((state.x - target[0])**2 + (state.y - target[1])**2)
            print(f"  Robot {i+1}: pos=({state.x:.2f}, {state.y:.2f}), distance={distance:.2f}m")
        
        if terminated:
            print("  All robots reached targets!")
            break
    
    print("=" * 60 + "\n")


if __name__ == "__main__":
    example_kinematic_control()
    example_rl_environment()
    example_multi_robot()

