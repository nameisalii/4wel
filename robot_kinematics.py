import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class RobotState:
    x: float
    y: float
    theta: float
    v: float
    delta_fl: float
    delta_fr: float
    delta_rl: float
    delta_rr: float


@dataclass
class RobotParams:
    wheelbase: float = 0.5
    track_width: float = 0.4
    wheel_radius: float = 0.1
    max_steering_angle: float = np.pi / 3
    max_steering_rate: float = 0.5
    max_acceleration: float = 2.0
    max_velocity: float = 2.0  


class FourWheelKinematics:
    
    def __init__(self, params: Optional[RobotParams] = None):
        self.params = params or RobotParams()
        self.state = RobotState(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        
    def reset(self, x: float = 0.0, y: float = 0.0, theta: float = 0.0):
        self.state = RobotState(x, y, theta, 0.0, 0.0, 0.0, 0.0, 0.0)
        
    def get_icr_y(self, curvature: float) -> float:
        if abs(curvature) < 1e-6:
            return np.inf
        return 1.0 / curvature
    
    def compute_wheel_steering_angles(self, curvature: float) -> Tuple[float, float, float, float]:
        if abs(curvature) < 1e-6:
            return 0.0, 0.0, 0.0, 0.0
        
        R = 1.0 / curvature
        L_half = self.params.wheelbase / 2
        W_half = self.params.track_width / 2
        
        delta_fl = np.arctan2(L_half, R - W_half)
        delta_fr = np.arctan2(L_half, R + W_half)
        delta_rl = np.arctan2(-L_half, R - W_half)
        delta_rr = np.arctan2(-L_half, R + W_half)
        
        return delta_fl, delta_fr, delta_rl, delta_rr
    
    def apply_steering_rate_limit(self, desired_deltas: Tuple[float, float, float, float], 
                                  dt: float) -> Tuple[float, float, float, float]:
        current = (self.state.delta_fl, self.state.delta_fr, 
                   self.state.delta_rl, self.state.delta_rr)
        max_change = self.params.max_steering_rate * dt
        
        limited = []
        for desired, current_val in zip(desired_deltas, current):
            change = desired - current_val
            change = np.clip(change, -max_change, max_change)
            new_val = current_val + change
            new_val = np.clip(new_val, -self.params.max_steering_angle, self.params.max_steering_angle)
            limited.append(new_val)
        
        return tuple(limited)
    
    def apply_acceleration_limit(self, desired_velocity: float, dt: float) -> float:
        max_change = self.params.max_acceleration * dt
        change = desired_velocity - self.state.v
        change = np.clip(change, -max_change, max_change)
        new_velocity = self.state.v + change
        return np.clip(new_velocity, -self.params.max_velocity, self.params.max_velocity)
    
    def step(self, curvature: float, velocity: float, dt: float = 0.1):
        v_new = self.apply_acceleration_limit(velocity, dt)
        
        delta_fl_desired, delta_fr_desired, delta_rl_desired, delta_rr_desired = \
            self.compute_wheel_steering_angles(curvature)
        
        delta_fl, delta_fr, delta_rl, delta_rr = \
            self.apply_steering_rate_limit(
                (delta_fl_desired, delta_fr_desired, delta_rl_desired, delta_rr_desired),
                dt
            )
        
        self.state.delta_fl = delta_fl
        self.state.delta_fr = delta_fr
        self.state.delta_rl = delta_rl
        self.state.delta_rr = delta_rr
        self.state.v = v_new
        
        if abs(curvature) < 1e-6:
            dx = v_new * np.cos(self.state.theta) * dt
            dy = v_new * np.sin(self.state.theta) * dt
            dtheta = 0.0
        else:
            omega = v_new * curvature
            dtheta = omega * dt
            
            R = 1.0 / curvature
            sin_t = np.sin(self.state.theta)
            cos_t = np.cos(self.state.theta)
            sin_t_dt = np.sin(self.state.theta + dtheta)
            cos_t_dt = np.cos(self.state.theta + dtheta)
            
            dx = R * (sin_t_dt - sin_t)
            dy = -R * (cos_t_dt - cos_t)
        
        self.state.x += dx
        self.state.y += dy
        self.state.theta += dtheta
        
        self.state.theta = (self.state.theta + np.pi) % (2 * np.pi) - np.pi
    
    def get_state(self) -> RobotState:
        return self.state
    
    def get_wheel_positions(self) -> np.ndarray:
        L_half = self.params.wheelbase / 2
        W_half = self.params.track_width / 2
        
        wheel_positions_robot = np.array([
            [L_half, W_half],
            [L_half, -W_half],
            [-L_half, W_half],
            [-L_half, -W_half]
        ])
        
        cos_t = np.cos(self.state.theta)
        sin_t = np.sin(self.state.theta)
        R = np.array([[cos_t, -sin_t],
                      [sin_t, cos_t]])
        
        wheel_positions_global = (R @ wheel_positions_robot.T).T
        wheel_positions_global[:, 0] += self.state.x
        wheel_positions_global[:, 1] += self.state.y
        
        return wheel_positions_global
    
    def get_icr_position(self) -> Optional[Tuple[float, float]]:
        if abs(self.state.delta_fl) < 1e-3:
            return None
             
        L = self.params.wheelbase / 2
        W = self.params.track_width / 2
        y_icr_robot = L / np.tan(self.state.delta_fl) + W
        
        cos_t = np.cos(self.state.theta)
        sin_t = np.sin(self.state.theta)
        
        gx = -y_icr_robot * sin_t + self.state.x
        gy = y_icr_robot * cos_t + self.state.y
        
        return (gx, gy)
