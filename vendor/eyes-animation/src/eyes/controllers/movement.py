"""
Movement controller for the Eyes Animation system.

This module provides the controller for managing eye movement,
including direction, position, transitions, and movement patterns.
"""
import random
import math
import pygame
from ..config import LookDirection, MOVE_AMOUNT, MOVE_DURATION


class MovementController:
    """
    Controls the eye movement animation with natural dynamics.
    
    The controller manages eye positions, movement transitions, 
    directional variations, and supports both random and pattern-based movements.
    """
    
    def __init__(self, eye_width, eye_height, eye_spacing, screen_width, screen_height):
        """
        Initialize movement controller with custom screen dimensions.
        
        Args:
            eye_width (int): Width of each eye in pixels.
            eye_height (int): Height of each eye in pixels.
            eye_spacing (int): Spacing between eyes in pixels.
            screen_width (int): Width of the display area in pixels.
            screen_height (int): Height of the display area in pixels.
        """
        # Movement state attributes
        self.is_moving = False
        self.current_direction = LookDirection.CENTER
        self.move_transition_progress = 0.0
        self.move_start_time = 0
        self.last_movement = 0
        self.movement_duration = 0

        # Store screen dimensions
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Screen positioning calculations
        screen_center_x = self.screen_width // 2
        screen_center_y = self.screen_height // 2

        # Precise horizontal centering
        total_width = eye_width * 2 + eye_spacing
        left_x = screen_center_x - (total_width // 2)
        right_x = left_x + eye_width + eye_spacing

        # Vertical centering
        base_y = screen_center_y - (eye_height // 2)

        # Set base positions
        self.base_left_pos = (left_x, base_y)
        self.base_right_pos = (right_x, base_y)

        # Current and target positions
        self.left_pos = list(self.base_left_pos)
        self.right_pos = list(self.base_right_pos)
        self.target_left_pos = list(self.base_left_pos)
        self.target_right_pos = list(self.base_right_pos)

        # Movement variation parameters
        self.movement_variation = 0.2  # 20% random variation

        # Pattern system
        self.pattern_mode = False
        self.current_pattern = None
        self.pattern_index = 0
        
        # Direction tracking for statistics
        self.direction_counts = {direction: 0 for direction in LookDirection}
        self.recent_history = []
        self.max_history = 10
        
        # Movement patterns
        self.movement_patterns = {
            'square': [
                LookDirection.UP,
                LookDirection.RIGHT,
                LookDirection.DOWN,
                LookDirection.LEFT
            ],
            'diamond': [
                LookDirection.UP,
                LookDirection.UP_RIGHT,
                LookDirection.RIGHT,
                LookDirection.DOWN_RIGHT,
                LookDirection.DOWN,
                LookDirection.DOWN_LEFT,
                LookDirection.LEFT,
                LookDirection.UP_LEFT
            ]
        }

    def get_direction_offsets(self, direction):
        """
        Get movement offsets with added natural variation.
        
        Args:
            direction (LookDirection): The direction to calculate offsets for.
            
        Returns:
            tuple: (x_offset, y_offset) movement values
        """
        base_offsets = {
            LookDirection.CENTER: (0, 0),
            LookDirection.UP: (0, -MOVE_AMOUNT),
            LookDirection.DOWN: (0, MOVE_AMOUNT),
            LookDirection.LEFT: (-MOVE_AMOUNT, 0),
            LookDirection.RIGHT: (MOVE_AMOUNT, 0),
            LookDirection.UP_LEFT: (-MOVE_AMOUNT, -MOVE_AMOUNT),
            LookDirection.UP_RIGHT: (MOVE_AMOUNT, -MOVE_AMOUNT),
            LookDirection.DOWN_LEFT: (-MOVE_AMOUNT, MOVE_AMOUNT),
            LookDirection.DOWN_RIGHT: (MOVE_AMOUNT, MOVE_AMOUNT)
        }
        
        # Get base offset
        base_offset = base_offsets.get(direction, (0, 0))
        
        # Add natural variation
        variation_x = base_offset[0] * (1 + random.uniform(-self.movement_variation, self.movement_variation))
        variation_y = base_offset[1] * (1 + random.uniform(-self.movement_variation, self.movement_variation))
        
        return (variation_x, variation_y)

    def start_movement(self, direction=None):
        """
        Start eye movement with pattern support and natural timing.
        
        Args:
            direction (LookDirection, optional): Specific direction to move.
                                              If None, direction is chosen 
                                              based on current mode.
        """
        if self.is_moving:
            return

        if direction is None:
            if self.pattern_mode and self.current_pattern:
                # Get next direction from current pattern
                pattern = self.movement_patterns[self.current_pattern]
                direction = pattern[self.pattern_index]
                self.pattern_index = (self.pattern_index + 1) % len(pattern)
            else:
                # Use weighted random selection for more natural movement
                directions = list(LookDirection)
                weights = [
                    0.3,   # More likely to stay near center
                    0.1,   # Up
                    0.1,   # Down
                    0.1,   # Left
                    0.1,   # Right
                    0.1,   # Up Left
                    0.1,   # Up Right
                    0.05,  # Down Left
                    0.05   # Down Right
                ]
                
                # Avoid repeating the exact same direction
                current_index = directions.index(self.current_direction)
                weights[current_index] *= 0.5
                
                direction = random.choices(directions, weights=weights)[0]

        # Update direction tracking
        self.current_direction = direction
        self.direction_counts[direction] += 1
        
        # Update movement history
        self.recent_history.append(direction)
        if len(self.recent_history) > self.max_history:
            self.recent_history.pop(0)
            
        # Calculate directional offsets
        offset_x, offset_y = self.get_direction_offsets(direction)

        # Set dynamic movement duration with slight randomness
        self.movement_duration = random.uniform(MOVE_DURATION * 0.8, MOVE_DURATION * 1.2)

        # Calculate target positions with variation
        self.target_left_pos = [
            self.base_left_pos[0] + offset_x, 
            self.base_left_pos[1] + offset_y
        ]
        self.target_right_pos = [
            self.base_right_pos[0] + offset_x, 
            self.base_right_pos[1] + offset_y
        ]
        
        self.is_moving = True
        self.move_start_time = pygame.time.get_ticks()
        self.move_transition_progress = 0.0

    def toggle_movement_mode(self):
        """
        Toggle between pattern and random movement modes.
        
        Returns:
            bool: True if now in pattern mode, False if in random mode.
        """
        self.pattern_mode = not self.pattern_mode
        if self.pattern_mode:
            # Select a random pattern when entering pattern mode
            self.current_pattern = random.choice(list(self.movement_patterns.keys()))
            self.pattern_index = 0
        else:
            self.current_pattern = None
        return self.pattern_mode

    def get_movement_stats(self):
        """
        Get current movement statistics.
        
        Returns:
            dict: Dictionary with current movement statistics
        """
        return {
            'current_mode': 'Pattern-based' if self.pattern_mode else 'Random',
            'current_pattern': self.current_pattern if self.pattern_mode else None,
            'direction_counts': {d.value: c for d, c in self.direction_counts.items()},
            'recent_history': [d.value for d in self.recent_history]
        }

    def smooth_interpolation(self, start, end, progress):
        """
        Create a more natural movement interpolation with a slight elastic effect.
        
        Args:
            start (float): Starting value
            end (float): Ending value
            progress (float): Progress from 0.0 to 1.0
            
        Returns:
            float: Interpolated value with elastic effect
        """
        # Smooth interpolation with slight elastic effect
        t = progress
        return start + (end - start) * (1 - math.exp(-5 * t) * math.cos(10 * t))

    def update(self, current_time, ease_func):
        """
        Update eye movement with natural transitions.
        
        Args:
            current_time (int): Current time in milliseconds, typically from
                                pygame.time.get_ticks().
            ease_func (callable): Easing function to use for interpolation.
        """
        if self.is_moving:
            elapsed = current_time - self.move_start_time
            self.move_transition_progress = min(1.0, elapsed / self.movement_duration)
            
            if self.move_transition_progress >= 1.0:
                self.is_moving = False
                self.last_movement = current_time
                self.left_pos = list(self.target_left_pos)
                self.right_pos = list(self.target_right_pos)
            else:
                # Use custom smooth interpolation
                progress = self.smooth_interpolation(0, 1, self.move_transition_progress)
                
                for i in range(2):
                    self.left_pos[i] = self.base_left_pos[i] + (
                        self.target_left_pos[i] - self.base_left_pos[i]
                    ) * progress
                    
                    self.right_pos[i] = self.base_right_pos[i] + (
                        self.target_right_pos[i] - self.base_right_pos[i]
                    ) * progress