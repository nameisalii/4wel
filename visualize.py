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
            [L, W, 0.0],   
            [L, -W, 0.0],  
            [-L, -W, 0.0], 
            [-L, W, 0.0]   
        ])
        
        cos_theta = np.cos(state.theta)
        sin_theta = np.sin(state.theta)
        rotation = np.array([[cos_theta, -sin_theta, 0],
                            [sin_theta, cos_theta, 0],
                            [0, 0, 1]])
        
        corners_global = (rotation @ corners_robot.T).T
        corners_global[:, 0] += state.x
        corners_global[:, 1] += state.y
        
        # Format for Foxglove Studio visualization
        marker = {
            'type': 'robot_body',
            'robot_id': robot_id,
            'timestamp': timestamp,
            'pose': {
                'position': {'x': state.x, 'y': state.y, 'z': 0.0},
                'orientation': {
                    'x': 0.0,
                    'y': 0.0,
                    'z': np.sin(state.theta / 2.0),
                    'w': np.cos(state.theta / 2.0)
                }
            },
            'scale': {'x': params.wheelbase, 'y': params.track_width, 'z': 0.1},
            'corners': corners_global.tolist(),
            'color': {'r': 0.2, 'g': 0.6, 'b': 0.8, 'a': 1.0}
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
            
            # Format for Foxglove Studio visualization
            marker = {
                'type': 'wheel',
                'robot_id': robot_id,
                'wheel_name': name,
                'timestamp': timestamp,
                'pose': {
                    'position': {'x': pos[0], 'y': pos[1], 'z': 0.0},
                    'orientation': {
                        'x': 0.0,
                        'y': 0.0,
                        'z': np.sin(wheel_theta / 2.0),
                        'w': np.cos(wheel_theta / 2.0)
                    }
                },
                'steering_angle': angle,
                'scale': {'x': params.wheel_radius * 2, 'y': params.wheel_radius * 2, 'z': 0.1},
                'radius': params.wheel_radius,
                'color': {'r': color[0], 'g': color[1], 'b': color[2], 'a': color[3]}
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
            # Format for Foxglove Studio visualization (line marker)
            marker = {
                'type': 'link',
                'robot_id': robot_id,
                'timestamp': timestamp,
                'points': [
                    {'x': state.x, 'y': state.y, 'z': 0.0},
                    {'x': wheel_pos[0], 'y': wheel_pos[1], 'z': 0.0}
                ],
                'scale': {'x': 0.05, 'y': 0.0, 'z': 0.0},  # Line width
                'color': {'r': 0.5, 'g': 0.5, 'b': 0.5, 'a': 0.5}
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
        
        # Format for Foxglove Studio visualization (sphere marker)
        marker = {
            'type': 'icr',
            'robot_id': robot_id,
            'timestamp': timestamp,
            'pose': {
                'position': {'x': icr_pos[0], 'y': icr_pos[1], 'z': 0.0},
                'orientation': {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0}
            },
            'scale': {'x': 0.2, 'y': 0.2, 'z': 0.2},
            'color': {'r': 1.0, 'g': 0.0, 'b': 1.0, 'a': 1.0}
        }
        
        return marker
    
    def create_target_marker(self, target_x: float, target_y: float,
                            target_id: int = 0,
                            timestamp: Optional[float] = None) -> dict:
        if timestamp is None:
            timestamp = time.time()
        
        # Format for Foxglove Studio visualization (cylinder/sphere marker)
        marker = {
            'type': 'target',
            'target_id': target_id,
            'timestamp': timestamp,
            'pose': {
                'position': {'x': target_x, 'y': target_y, 'z': 0.0},
                'orientation': {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0}
            },
            'scale': {'x': 0.3, 'y': 0.3, 'z': 0.1},
            'radius': 0.3,
            'color': {'r': 0.0, 'g': 1.0, 'b': 0.0, 'a': 1.0}
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

