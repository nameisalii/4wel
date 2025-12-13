import numpy as np
from typing import List, Tuple, Optional
from robot_kinematics import FourWheelKinematics, RobotState
import time


class MCAPVisualizer:
    
    def __init__(self):
        self.messages = []
    
    def create_robot_body_marker(self, robot: FourWheelKinematics, 
                                 robot_id: int = 0, 
                                 timestamp: Optional[float] = None) -> dict:
        state = robot.get_state()
        params = robot.params
        
        if timestamp is None:
            timestamp = time.time()
        
        L = params.wheelbase / 2
        W = params.track_width / 2
        
        corners_robot = np.array([
            [L, W],   
            [L, -W],  
            [-L, -W], 
            [-L, W]   
        ])
        
        cos_theta = np.cos(state.theta)
        sin_theta = np.sin(state.theta)
        rotation = np.array([[cos_theta, -sin_theta],
                            [sin_theta, cos_theta]])
        
        corners_global = (rotation @ corners_robot.T).T
        corners_global[:, 0] += state.x
        corners_global[:, 1] += state.y
        
        marker = {
            'type': 'robot_body',
            'robot_id': robot_id,
            'timestamp': timestamp,
            'pose': {
                'x': state.x,
                'y': state.y,
                'theta': state.theta
            },
            'corners': corners_global.tolist(),
            'color': [0.2, 0.6, 0.8, 1.0]
        }
        
        return marker
    
    def create_wheel_markers(self, robot: FourWheelKinematics,
                            robot_id: int = 0,
                            timestamp: Optional[float] = None) -> List[dict]:
        state = robot.get_state()
        params = robot.params
        wheel_positions = robot.get_wheel_positions()
        
        if timestamp is None:
            timestamp = time.time()
        
        wheel_names = ['fl', 'fr', 'rl', 'rr']
        wheel_colors = [
            [1.0, 0.0, 0.0, 1.0],
            [0.0, 1.0, 0.0, 1.0],
            [0.0, 0.0, 1.0, 1.0],
            [1.0, 1.0, 0.0, 1.0]
        ]
        
        steering_angles = [state.delta_fl, state.delta_fr, state.delta_rl, state.delta_rr]
        
        markers = []
        for i, (name, pos, angle, color) in enumerate(zip(wheel_names, wheel_positions, steering_angles, wheel_colors)):
            wheel_theta = state.theta + angle
            
            marker = {
                'type': 'wheel',
                'robot_id': robot_id,
                'wheel_name': name,
                'timestamp': timestamp,
                'position': {
                    'x': pos[0],
                    'y': pos[1],
                    'theta': wheel_theta
                },
                'steering_angle': angle,
                'radius': params.wheel_radius,
                'color': color
            }
            markers.append(marker)
        
        return markers
    
    def create_link_markers(self, robot: FourWheelKinematics,
                           robot_id: int = 0,
                           timestamp: Optional[float] = None) -> List[dict]:
        state = robot.get_state()
        wheel_positions = robot.get_wheel_positions()
        
        if timestamp is None:
            timestamp = time.time()
        
        markers = []
        for i, wheel_pos in enumerate(wheel_positions):
            marker = {
                'type': 'link',
                'robot_id': robot_id,
                'timestamp': timestamp,
                'start': {
                    'x': state.x,
                    'y': state.y
                },
                'end': {
                    'x': wheel_pos[0],
                    'y': wheel_pos[1]
                },
                'color': [0.5, 0.5, 0.5, 0.5]
            }
            markers.append(marker)
        
        return markers
    
    def create_icr_marker(self, robot: FourWheelKinematics,
                         robot_id: int = 0,
                         timestamp: Optional[float] = None) -> Optional[dict]:
        icr_pos = robot.get_icr_position()
        
        if icr_pos is None:
            return None
        
        if timestamp is None:
            timestamp = time.time()
        
        marker = {
            'type': 'icr',
            'robot_id': robot_id,
            'timestamp': timestamp,
            'position': {
                'x': icr_pos[0],
                'y': icr_pos[1]
            },
            'color': [1.0, 0.0, 1.0, 1.0]
        }
        
        return marker
    
    def create_target_marker(self, target_x: float, target_y: float,
                            target_id: int = 0,
                            timestamp: Optional[float] = None) -> dict:
        if timestamp is None:
            timestamp = time.time()
        
        marker = {
            'type': 'target',
            'target_id': target_id,
            'timestamp': timestamp,
            'position': {
                'x': target_x,
                'y': target_y
            },
            'color': [0.0, 1.0, 0.0, 1.0],
            'radius': 0.3
        }
        
        return marker
    
    def create_all_markers(self, robots: List[FourWheelKinematics],
                          targets: np.ndarray,
                          timestamp: Optional[float] = None) -> List[dict]:
        if timestamp is None:
            timestamp = time.time()
        
        markers = []
        
        for i, robot in enumerate(robots):
            markers.append(self.create_robot_body_marker(robot, i, timestamp))
            markers.extend(self.create_wheel_markers(robot, i, timestamp))
            markers.extend(self.create_link_markers(robot, i, timestamp))
            icr_marker = self.create_icr_marker(robot, i, timestamp)
            if icr_marker:
                markers.append(icr_marker)
        
        for i, target in enumerate(targets):
            markers.append(self.create_target_marker(target[0], target[1], i, timestamp))
        
        return markers


def save_markers_to_mcap(markers: List[dict], filename: str):
    try:
        from mcap.writer import Writer
        from mcap_ros2.writer import Writer as Ros2Writer
        import struct
        
        import json
        with open(filename.replace('.mcap', '_markers.json'), 'w') as f:
            json.dump(markers, f, indent=2)
        
        print(f"Markers saved to {filename.replace('.mcap', '_markers.json')}")
        print("Note: Full MCAP implementation requires ROS2 message types")
        
    except ImportError:
        import json
        with open(filename.replace('.mcap', '_markers.json'), 'w') as f:
            json.dump(markers, f, indent=2)
        print(f"Markers saved as JSON (MCAP library not available): {filename.replace('.mcap', '_markers.json')}")

