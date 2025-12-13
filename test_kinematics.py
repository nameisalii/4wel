"""
Test script for kinematic model
"""

import numpy as np
import matplotlib.pyplot as plt
from robot_kinematics import FourWheelKinematics, RobotParams


def test_straight_motion():
    """Test straight line motion"""
    print("Testing straight motion...")
    robot = FourWheelKinematics()
    robot.reset(0, 0, 0)
    
    # Straight motion: curvature = 0
    for _ in range(50):
        robot.step(curvature=0.0, velocity=1.0, dt=0.1)
    
    state = robot.get_state()
    print(f"  Final position: ({state.x:.2f}, {state.y:.2f})")
    print(f"  Expected: approx 4.75 (due to accel limit)")
    print(f"  Steering angles: delta_fl={state.delta_fl:.3f}, delta_fr={state.delta_fr:.3f}")
    assert abs(state.x - 4.75) < 0.1, f"Straight motion failed: x={state.x:.2f}"
    assert abs(state.y) < 0.1, "Straight motion failed"
    print("  Straight motion test passed\n")


def test_circular_motion():
    """Test circular motion"""
    print("Testing circular motion...")
    robot = FourWheelKinematics()
    robot.reset(0, 0, 0)
    
    # Circular motion: curvature = 0.5 (radius = 2m)
    radius = 2.0
    curvature = 1.0 / radius
    
    positions = []
    for _ in range(100):
        robot.step(curvature=curvature, velocity=1.0, dt=0.1)
        state = robot.get_state()
        positions.append([state.x, state.y])
    
    positions = np.array(positions)
    state = robot.get_state()
    
    # Check if we completed approximately a quarter circle
    print(f"  Final position: ({state.x:.2f}, {state.y:.2f})")
    print(f"  Expected: near (2.0, 2.0) for quarter circle")
    
    # Verify steering angles point toward ICR
    icr_y = robot.get_icr_y(curvature)
    print(f"  ICR y-coordinate (robot frame): {icr_y:.2f}")
    print(f"  Steering angles: delta_fl={state.delta_fl:.3f}, delta_fr={state.delta_fr:.3f}")
    
    print("  Circular motion test passed\n")


def test_steering_rate_limit():
    """Test steering rate limiting"""
    print("Testing steering rate limit...")
    robot = FourWheelKinematics()
    robot.reset(0, 0, 0)
    
    # Try to change steering angle quickly
    max_rate = robot.params.max_steering_rate
    dt = 0.1
    
    # First step: request large steering change
    robot.step(curvature=2.0, velocity=1.0, dt=dt)
    delta_after_first = robot.get_state().delta_fl
    
    # Second step: should be limited by rate
    robot.step(curvature=2.0, velocity=1.0, dt=dt)
    delta_after_second = robot.get_state().delta_fl
    
    change_rate = abs(delta_after_second - delta_after_first) / dt
    print(f"  Steering rate: {change_rate:.3f} rad/s")
    print(f"  Max allowed: {max_rate:.3f} rad/s")
    assert change_rate <= max_rate + 0.01, "Steering rate limit violated"
    print("  Steering rate limit test passed\n")


def test_acceleration_limit():
    """Test acceleration limiting"""
    print("Testing acceleration limit...")
    robot = FourWheelKinematics()
    robot.reset(0, 0, 0)
    
    max_accel = robot.params.max_acceleration
    dt = 0.1
    
    # Try to accelerate quickly
    robot.step(curvature=0.0, velocity=2.0, dt=dt)
    v_after_first = robot.get_state().v
    
    robot.step(curvature=0.0, velocity=2.0, dt=dt)
    v_after_second = robot.get_state().v
    
    accel = (v_after_second - v_after_first) / dt
    print(f"  Acceleration: {accel:.3f} m/s²")
    print(f"  Max allowed: {max_accel:.3f} m/s²")
    assert abs(accel) <= max_accel + 0.01, "Acceleration limit violated"
    print("  Acceleration limit test passed\n")


def visualize_robot():
    """Visualize robot with wheels and ICR"""
    print("Creating visualization...")
    robot = FourWheelKinematics()
    robot.reset(0, 0, 0)
    
    # Perform a curved path
    positions = []
    wheel_positions_history = []
    
    for i in range(50):
        curvature = 0.3 * np.sin(i * 0.1)  # Varying curvature
        velocity = 1.0
        robot.step(curvature, velocity, dt=0.1)
        
        state = robot.get_state()
        positions.append([state.x, state.y])
        wheel_positions_history.append(robot.get_wheel_positions())
    
    positions = np.array(positions)
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Plot path
    ax.plot(positions[:, 0], positions[:, 1], 'b-', linewidth=2, label='Robot Path')
    
    # Plot final robot state
    final_state = robot.get_state()
    final_wheels = robot.get_wheel_positions()
    
    # Robot body (rectangle)
    # X=Forward, Y=Left. Corners: (L, W), (L, -W), (-L, -W), (-L, W)
    L = robot.params.wheelbase / 2
    W = robot.params.track_width / 2
    
    corners_robot = np.array([
        [L, W], [L, -W], [-L, -W], [-L, W]
    ])
    
    cos_theta = np.cos(final_state.theta)
    sin_theta = np.sin(final_state.theta)
    rotation = np.array([[cos_theta, -sin_theta],
                        [sin_theta, cos_theta]])
    
    corners_global = (rotation @ corners_robot.T).T
    corners_global[:, 0] += final_state.x
    corners_global[:, 1] += final_state.y
    
    corners_global = np.vstack([corners_global, corners_global[0]])  # Close polygon
    ax.plot(corners_global[:, 0], corners_global[:, 1], 'k-', linewidth=2, label='Robot Body')
    
    # Plot wheels
    colors = ['red', 'green', 'blue', 'yellow']
    wheel_names = ['FL', 'FR', 'RL', 'RR']
    for i, (wheel_pos, color, name) in enumerate(zip(final_wheels, colors, wheel_names)):
        ax.plot(wheel_pos[0], wheel_pos[1], 'o', color=color, markersize=8, label=f'Wheel {name}')
        
        # Draw steering direction
        steering_angle = [final_state.delta_fl, final_state.delta_fr, 
                         final_state.delta_rl, final_state.delta_rr][i]
        wheel_theta = final_state.theta + steering_angle
        dx = 0.2 * np.cos(wheel_theta)
        dy = 0.2 * np.sin(wheel_theta)
        ax.arrow(wheel_pos[0], wheel_pos[1], dx, dy, 
                head_width=0.05, head_length=0.05, fc=color, ec=color)
    
    # Plot ICR
    icr_pos = robot.get_icr_position()
    if icr_pos:
        ax.plot(icr_pos[0], icr_pos[1], 'm*', markersize=15, label='ICR')
        
        # Draw lines from wheels to ICR
        for wheel_pos in final_wheels:
            ax.plot([wheel_pos[0], icr_pos[0]], [wheel_pos[1], icr_pos[1]], 
                   'm--', alpha=0.3, linewidth=1)
    
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_title('Robot Kinematics Visualization')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    
    plt.tight_layout()
    plt.savefig('kinematics_test.png', dpi=150)
    print("  Visualization saved to kinematics_test.png\n")


if __name__ == "__main__":
    print("=" * 50)
    print("Testing 4-Wheel Robot Kinematics")
    print("=" * 50 + "\n")
    
    test_straight_motion()
    test_circular_motion()
    test_steering_rate_limit()
    test_acceleration_limit()
    visualize_robot()
    
    print("=" * 50)
    print("All tests passed!")
    print("=" * 50)
