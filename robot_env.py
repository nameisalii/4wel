import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Tuple, Optional, Dict, Any
from robot_kinematics import FourWheelKinematics, RobotParams, RobotState


class RobotNavigationEnv(gym.Env):
    
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 10}
    
    def __init__(self, 
                 num_robots: int = 1,
                 max_episode_steps: int = 500,
                 success_threshold: float = 0.3,
                 initial_range: float = 10.0,
                 render_mode: Optional[str] = None):
        super().__init__()
        
        self.num_robots = num_robots
        self.max_episode_steps = max_episode_steps
        self.success_threshold = success_threshold
        self.initial_range = initial_range
        self.render_mode = render_mode
   
        if num_robots == 1:
            state_dim = 10
        else:
            per_robot_dim = 10 + (num_robots - 1) * 2
            state_dim = per_robot_dim * num_robots
        
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(state_dim,), dtype=np.float32
        )
        
        if num_robots == 1:
            self.action_space = spaces.Box(
                low=np.array([-2.0, -2.0], dtype=np.float32),
                high=np.array([2.0, 2.0], dtype=np.float32),
                dtype=np.float32
            )
        else:
            self.action_space = spaces.Box(
                low=np.array([-2.0, -2.0] * num_robots, dtype=np.float32),
                high=np.array([2.0, 2.0] * num_robots, dtype=np.float32),
                dtype=np.float32
            )
        
        self.robots = [FourWheelKinematics() for _ in range(num_robots)]
        self.targets = np.zeros((num_robots, 2))
        self.step_count = 0
        
    def reset(self, seed: Optional[int] = None, options: Optional[Dict] = None) -> Tuple[np.ndarray, Dict]:
        super().reset(seed=seed)
        
        self.step_count = 0
        self._prev_distances = [float('inf')] * self.num_robots
        
        for i, robot in enumerate(self.robots):
            x = self.np_random.uniform(-self.initial_range, self.initial_range)
            y = self.np_random.uniform(-self.initial_range, self.initial_range)
            theta = self.np_random.uniform(-np.pi, np.pi)
            robot.reset(x, y, theta)
        
        if self.num_robots == 1:
            self.targets[0] = self.np_random.uniform(-self.initial_range, self.initial_range, 2)
        else:
            min_separation = 3.0
            for i in range(self.num_robots):
                while True:
                    target = self.np_random.uniform(-self.initial_range, self.initial_range, 2)
                    too_close = False
                    for j in range(i):
                        if np.linalg.norm(target - self.targets[j]) < min_separation:
                            too_close = True
                            break
                    if not too_close:
                        self.targets[i] = target
                        break
        
        obs = self._get_observation()
        info = self._get_info()
        
        return obs, info
    
    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        dt = 0.1
        
        action = np.asarray(action, dtype=np.float32)
        if self.num_robots == 1:
            actions = [action]
        else:
            if action.shape == (self.num_robots * 2,):
                actions = [action[i*2:(i+1)*2] for i in range(self.num_robots)]
            elif action.shape == (self.num_robots, 2):
                actions = [action[i] for i in range(self.num_robots)]
            else:
                if action.shape == (2,):
                    actions = [action] * self.num_robots
                else:
                    raise ValueError(f"Unexpected action shape: {action.shape}")
        
        for robot, (curvature, velocity) in zip(self.robots, actions):
            robot.step(curvature, velocity, dt)
        
        self.step_count += 1
        
        reward = self._compute_reward()
        terminated = self._check_success()
        truncated = self.step_count >= self.max_episode_steps
        
        obs = self._get_observation()
        info = self._get_info()
        info['success'] = terminated
        
        return obs, reward, terminated, truncated, info
    
    def _get_observation(self) -> np.ndarray:
        obs_list = []
        
        for i, robot in enumerate(self.robots):
            state = robot.get_state()
            target = self.targets[i]
            
            robot_obs = np.array([
                state.x, state.y, state.theta, state.v,
                state.delta_fl, state.delta_fr, state.delta_rl, state.delta_rr
            ], dtype=np.float32)
            
            target_rel = target - np.array([state.x, state.y])
            robot_obs = np.concatenate([robot_obs, target_rel])
            
            obs_list.append(robot_obs)
        
        if self.num_robots > 1:
            for i in range(self.num_robots):
                relative_positions = []
                for j in range(self.num_robots):
                    if i != j:
                        state_i = self.robots[i].get_state()
                        state_j = self.robots[j].get_state()
                        rel_pos = np.array([state_j.x - state_i.x, state_j.y - state_i.y])
                        relative_positions.append(rel_pos)
                obs_list[i] = np.concatenate([obs_list[i], *relative_positions])
        
        if self.num_robots == 1:
            return obs_list[0]
        else:
            return np.concatenate(obs_list).astype(np.float32)
    
    def _compute_reward(self) -> float:
        total_reward = 0.0
        
        for i, robot in enumerate(self.robots):
            state = robot.get_state()
            target = self.targets[i]
            
            distance = np.sqrt((state.x - target[0])**2 + (state.y - target[1])**2)
            
            if self.num_robots == 1:
                distance_reward = -distance
            else:
                distance_reward = -0.5 * distance
                if not hasattr(self, '_prev_distances') or self._prev_distances[i] == float('inf'):
                    progress = 0.0
                else:
                    progress = self._prev_distances[i] - distance
                    progress = np.clip(progress, -5.0, 5.0)
                distance_reward += 2.0 * progress
                self._prev_distances[i] = distance
            
            success_bonus = 200.0 if distance < self.success_threshold else 0.0
            
            velocity_penalty = -0.1 * abs(state.v)
            steering_penalty = -0.05 * (abs(state.delta_fl) + abs(state.delta_fr) + 
                                      abs(state.delta_rl) + abs(state.delta_rr))
            
            robot_reward = distance_reward + success_bonus + velocity_penalty + steering_penalty
            total_reward += robot_reward
        
        if self.num_robots > 1:
            collision_penalty = 0.0
            min_distance = float('inf')
            for i in range(self.num_robots):
                for j in range(i + 1, self.num_robots):
                    state_i = self.robots[i].get_state()
                    state_j = self.robots[j].get_state()
                    dist = np.sqrt((state_i.x - state_j.x)**2 + (state_i.y - state_j.y)**2)
                    min_distance = min(min_distance, dist)
                    
                    if dist < 0.5:
                        collision_penalty -= 50.0
                    elif dist < 1.0:
                        collision_penalty -= 10.0 * (1.0 - dist)
            
            total_reward += collision_penalty
            
            if min_distance > 1.5:
                total_reward += 1.0
        
        total_reward = np.clip(total_reward, -10000.0, 10000.0)
        
        if np.isnan(total_reward) or np.isinf(total_reward):
            total_reward = -100.0
        
        return float(total_reward)
    
    def _check_success(self) -> bool:
        for i, robot in enumerate(self.robots):
            state = robot.get_state()
            target = self.targets[i]
            distance = np.sqrt((state.x - target[0])**2 + (state.y - target[1])**2)
            if distance > self.success_threshold:
                return False
        return True
    
    def _get_info(self) -> Dict[str, Any]:
        info = {}
        distances = []
        for i, robot in enumerate(self.robots):
            state = robot.get_state()
            target = self.targets[i]
            distance = np.sqrt((state.x - target[0])**2 + (state.y - target[1])**2)
            distances.append(distance)
        info['distances'] = distances
        info['step'] = self.step_count
        return info
    
    def render(self):
        if self.render_mode == "human":
            pass

