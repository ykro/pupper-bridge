"""
Main animation module for the Eyes Animation system.

This module provides the primary Eyes class that integrates all controllers
and handles the rendering and animation of the robot eyes.
"""
import math
import pygame
from .config import (
    MoodState, LookDirection, COLOR_SCHEMES, MIN_EYE_SIZE, MAX_EYE_SIZE,
    DEFAULT_EYE_WIDTH, DEFAULT_EYE_HEIGHT, DEFAULT_EYE_SPACING,
    SCREEN_WIDTH, SCREEN_HEIGHT, IDLE_MOVE_INTERVAL, BLINK_INTERVAL
)
from .controllers import MovementController, MoodController, BlinkController, EffectsController
from .logging.logger import EyeLogger


class Eyes:
    """
    Main class for the Eyes Animation system.
    
    This class integrates all animation controllers and provides methods for 
    drawing, updating, and customizing the animated eyes.
    """
    
    def __init__(self, enable_logging=False, screen_width=None, screen_height=None):
        """
        Initialize eye animation system.
        
        Args:
            enable_logging (bool): Whether to enable logging. Defaults to False.
            screen_width (int): Override default screen width from config
            screen_height (int): Override default screen height from config
        """
        # Override config dimensions if provided
        self.screen_width = screen_width if screen_width is not None else SCREEN_WIDTH
        self.screen_height = screen_height if screen_height is not None else SCREEN_HEIGHT
        
        # Logging setup
        self.enable_logging = enable_logging
        self.logger = EyeLogger() if enable_logging else None
        
        # Eye dimensions
        self.EYE_WIDTH = DEFAULT_EYE_WIDTH
        self.EYE_HEIGHT = DEFAULT_EYE_HEIGHT
        self.EYE_SPACING = DEFAULT_EYE_SPACING
        
        # Initialize controllers with overridden screen dimensions
        self.movement = MovementController(
            eye_width=self.EYE_WIDTH,
            eye_height=self.EYE_HEIGHT,
            eye_spacing=self.EYE_SPACING,
            screen_width=self.screen_width,
            screen_height=self.screen_height
        )
        self.mood = MoodController()
        self.blink = BlinkController()
        self.effects = EffectsController()
        
        # Initial logging if enabled
        if self.enable_logging:
            self._log_initial_state()

    def _log_initial_state(self):
        """Log the initial state of the eyes."""
        if not self.enable_logging:
            return
        
        self.logger.log_event("Initialization", "Eyes created")
        self.logger.log_eye_state(
            compass_location=self.movement.current_direction.value,
            eye_size=(self.EYE_WIDTH, self.EYE_HEIGHT),
            exact_location=(self.movement.left_pos, self.movement.right_pos),
            mood=self.mood.current_mood.value,
            blinking_state=self.blink.is_blinking
        )

    def _ease_in_out(self, t):
        """
        Simple easing function for smoother animations.
        
        Args:
            t (float): Input value between 0.0 and 1.0
            
        Returns:
            float: Eased value between 0.0 and 1.0
        """
        return t * t * (3 - 2 * t)

    def _draw_grid(self, screen):
        """
        Draw a reference grid on the screen for positioning.
        
        Args:
            screen (pygame.Surface): Screen surface to draw on
        """
        # Light gray color for grid lines
        grid_color = (100, 100, 100)
        
        # Get screen dimensions
        screen_width, screen_height = screen.get_size()
        
        # Calculate grid cell dimensions with some padding
        grid_width = screen_width * 0.9  # 90% of screen width
        grid_height = screen_height * 0.9  # 90% of screen height
        
        # Calculate starting position to center the grid
        start_x = (screen_width - grid_width) / 2
        start_y = (screen_height - grid_height) / 2
        
        # Calculate cell dimensions
        cell_width = grid_width / 3
        cell_height = grid_height / 3
        
        # Draw vertical lines
        for x in range(1, 3):
            line_x = start_x + x * cell_width
            pygame.draw.line(screen, grid_color, 
                             (line_x, start_y), 
                             (line_x, start_y + grid_height), 
                             2)  # Line thickness of 2
        
        # Draw horizontal lines
        for y in range(1, 3):
            line_y = start_y + y * cell_height
            pygame.draw.line(screen, grid_color, 
                             (start_x, line_y), 
                             (start_x + grid_width, line_y), 
                             2)  # Line thickness of 2

    def update(self):
        """
        Update all animation states for the current frame.
        
        This method should be called once per frame to update all
        controllers and handle idle movements.
        """
        current_time = pygame.time.get_ticks()
        
        # Update all controllers
        self.movement.update(current_time, self._ease_in_out)
        self.mood.update(current_time)
        self.blink.update()
        
        # Handle idle movement
        if not self.movement.is_moving and current_time - self.movement.last_movement > IDLE_MOVE_INTERVAL:
            self.movement.start_movement()
        
        # Log state if logging is enabled
        if self.enable_logging:
            self._log_state()

    def _log_state(self):
        """Log current eye state if logging is enabled."""
        if not self.enable_logging:
            return
        
        self.logger.log_eye_state(
            compass_location=self.movement.current_direction.value,
            eye_size=(self.EYE_WIDTH, self.EYE_HEIGHT),
            exact_location=(self.movement.left_pos, self.movement.right_pos),
            mood=self.mood.current_mood.value,
            blinking_state=self.blink.is_blinking
        )

    def draw(self, screen):
        """
        Draw eyes with current mood and blink state.
        
        Args:
            screen (pygame.Surface): Pygame surface to draw on
        """
        # Get current color scheme
        colors = COLOR_SCHEMES[self.effects.current_scheme]
        
        # Base eye height (affected by blinking)
        current_height = int(self.EYE_HEIGHT * self.blink.blink_state)
        
        # Initialize basic dimensions
        left_height = right_height = current_height
        left_width = right_width = self.EYE_WIDTH
        crescent_curve = 0
        
        # Apply transitions based on mood
        transition = self._ease_in_out(self.mood.mood_transition_progress)
        
        # Adjust dimensions based on mood
        if self.mood.current_mood == MoodState.HAPPY:
            crescent_curve = transition
        elif self.mood.current_mood == MoodState.CONFUSED:
            target_height = current_height * 0.7
            left_height = int(current_height + (target_height - current_height) * transition)
        elif self.mood.current_mood == MoodState.SURPRISED:
            target_width = self.EYE_WIDTH * 1.2
            target_height = current_height * 1.2
            left_width = right_width = int(self.EYE_WIDTH + (target_width - self.EYE_WIDTH) * transition)
            left_height = right_height = int(current_height + (target_height - current_height) * transition)
        
        # Apply directional size variation
        size_variation_factor = self.effects.size_variation_factor
        if self.movement.current_direction in [LookDirection.LEFT, LookDirection.UP_LEFT, LookDirection.DOWN_LEFT]:
            left_width = int(left_width * (1 + size_variation_factor))
            left_height = int(left_height * (1 + size_variation_factor))
        elif self.movement.current_direction in [LookDirection.RIGHT, LookDirection.UP_RIGHT, LookDirection.DOWN_RIGHT]:
            right_width = int(right_width * (1 + size_variation_factor))
            right_height = int(right_height * (1 + size_variation_factor))

        bounce_y_offset = int(self.mood.bounce_offset)
        
        def create_crescent_mask(width, height):
            """Create a mask surface for the crescent shape."""
            mask = pygame.Surface((width, height), pygame.SRCALPHA)
            
            if crescent_curve > 0 and self.blink.blink_state > 0.3:
                # Draw the main circle in white
                pygame.draw.ellipse(mask, (255, 255, 255, 255), (0, 0, width, height))
                
                # Mask out bottom portion with larger circle
                mask_width = int(width * 1.2)
                mask_height = height
                mask_x = int((width - mask_width) / 2)
                mask_y = int(height * 0.5)
                pygame.draw.ellipse(mask, (0, 0, 0, 0), 
                                (mask_x, mask_y, mask_width, mask_height))
            else:
                pygame.draw.ellipse(mask, (255, 255, 255, 255), (0, 0, width, height))
            
            return mask
        
        def draw_smooth_crescent(surface, x, y, width, height, color, is_border=False):
            """Draw a smooth crescent shape using masking."""
            if is_border:
                # For border, draw on a temporary surface
                temp = pygame.Surface((width + self.effects.border_thickness * 2,
                                    height + self.effects.border_thickness * 2), pygame.SRCALPHA)
                pygame.draw.ellipse(temp, color, (0, 0, temp.get_width(), temp.get_height()))
                
# Create and scale mask for border
                mask = create_crescent_mask(temp.get_width(), temp.get_height())
                temp.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                
                # Draw border by using two different sized ellipses
                inner = pygame.Surface(temp.get_size(), pygame.SRCALPHA)
                pygame.draw.ellipse(inner, (0, 0, 0, 255), 
                                (self.effects.border_thickness, self.effects.border_thickness,
                                width, height))
                temp.blit(inner, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
                
                surface.blit(temp, (x - self.effects.border_thickness,
                                y + bounce_y_offset - self.effects.border_thickness))
            else:
                # For fill, draw the shape and apply mask
                temp = pygame.Surface((width, height), pygame.SRCALPHA)
                pygame.draw.ellipse(temp, color, (0, 0, width, height))
                
                # Apply mask
                mask = create_crescent_mask(width, height)
                temp.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                
                surface.blit(temp, (x, y + bounce_y_offset))
        
        # Create glow surface
        glow_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        
        # Draw glow layers
        for i in range(5):
            layer_alpha = int((self.effects.glow_intensity * (5 - i)) / 5)
            glow_color = (*colors['glow'], layer_alpha)
            size_increase = int((i * self.effects.glow_radius) / 2)
            
            # Create a temporary surface for each glow layer
            temp_glow = pygame.Surface((left_width + size_increase * 2,
                                    left_height + size_increase * 2), pygame.SRCALPHA)
            
            # Draw and mask left eye glow
            draw_smooth_crescent(
                glow_surface,
                self.movement.left_pos[0] - size_increase,
                self.movement.left_pos[1] - size_increase,
                left_width + size_increase * 2,
                left_height + size_increase * 2,
                glow_color
            )
            
            # Draw and mask right eye glow
            draw_smooth_crescent(
                glow_surface,
                self.movement.right_pos[0] - size_increase,
                self.movement.right_pos[1] - size_increase,
                right_width + size_increase * 2,
                right_height + size_increase * 2,
                glow_color
            )
        
        # Apply glow
        screen.blit(glow_surface, (0, 0))
        
        # Draw both eyes
        for eye_pos, width, height in [
            (self.movement.left_pos, left_width, left_height),
            (self.movement.right_pos, right_width, right_height)
        ]:
            # Draw border
            draw_smooth_crescent(screen, eye_pos[0], eye_pos[1], width, height,
                            colors['secondary'], True)
            
            # Draw main eye color
            draw_smooth_crescent(screen, eye_pos[0], eye_pos[1], width, height,
                            colors['primary'])
            
    def start_blink(self):
        """Start blinking animation."""
        if self.enable_logging:
            self.logger.log_event("Blink", "Blink started")
        self.blink.start_blink()

    def set_mood(self, mood: MoodState):
        """
        Set mood and log the event if logging is enabled.
        
        Args:
            mood (MoodState): The mood state to transition to.
        """
        if self.enable_logging:
            self.logger.log_event("Mood Change", f"Mood changed to {mood.value}")
        self.mood.set_mood(mood)

    def start_movement(self, direction: LookDirection = None):
        """
        Start eye movement and log the event if logging is enabled.
        
        Args:
            direction (LookDirection, optional): Specific direction to move.
                                               If None, direction is chosen automatically.
        """
        if self.enable_logging:
            log_direction = direction.value if direction else "Random"
            self.logger.log_event("Movement", f"Started moving {log_direction}")
        self.movement.start_movement(direction)
        
    def adjust_size(self, change: int):
        """
        Adjust eye size with constraints and log the event.
        
        Args:
            change (int): Amount to change eye size in pixels.
            
        Returns:
            tuple: New eye dimensions (width, height).
        """
        new_width = max(MIN_EYE_SIZE, min(MAX_EYE_SIZE, self.EYE_WIDTH + change))
        new_height = max(MIN_EYE_SIZE, min(MAX_EYE_SIZE, self.EYE_HEIGHT + change))
        
        if new_width != self.EYE_WIDTH or new_height != self.EYE_HEIGHT:
            self.EYE_WIDTH = new_width
            self.EYE_HEIGHT = new_height
            self.movement = MovementController(
                eye_width=self.EYE_WIDTH,
                eye_height=self.EYE_HEIGHT,
                eye_spacing=self.EYE_SPACING,
                screen_width=self.screen_width,
                screen_height=self.screen_height
            )
            
            if self.enable_logging:
                self.logger.log_event("Size Adjustment", 
                                      f"Eye size changed to {self.EYE_WIDTH}x{self.EYE_HEIGHT}")
            
            print(f"Eye size adjusted to: {self.EYE_WIDTH}x{self.EYE_HEIGHT}")
        
        return (self.EYE_WIDTH, self.EYE_HEIGHT)

    # Effect adjustment methods
    def adjust_glow_size(self, change: int):
        """
        Adjust glow size and log the event.
        
        Args:
            change (int): Amount to change the glow radius.
            
        Returns:
            int: The new glow radius value.
        """
        radius = self.effects.adjust_glow_size(change)
        
        if self.enable_logging:
            self.logger.log_event("Glow Adjustment", f"Glow size changed to {radius}")
        
        print(f"Glow size: {radius}")
        return radius

    def adjust_glow_intensity(self, change: int):
        """
        Adjust glow intensity and log the event.
        
        Args:
            change (int): Amount to change the glow intensity.
            
        Returns:
            int: The new glow intensity value.
        """
        intensity = self.effects.adjust_glow_intensity(change)
        
        if self.enable_logging:
            self.logger.log_event("Glow Intensity", f"Intensity changed to {intensity}")
        
        print(f"Glow intensity: {intensity}")
        return intensity

    def adjust_border_thickness(self, change: int):
        """
        Adjust border thickness and log the event.
        
        Args:
            change (int): Amount to change the border thickness.
            
        Returns:
            int: The new border thickness value.
        """
        thickness = self.effects.adjust_border_thickness(change)
        
        if self.enable_logging:
            self.logger.log_event("Border Adjustment", f"Thickness changed to {thickness}")
        
        print(f"Border thickness: {thickness}")
        return thickness

    def cycle_color_scheme(self):
        """
        Cycle color scheme and log the event.
        
        Returns:
            str: The name of the new color scheme.
        """
        scheme = self.effects.cycle_color_scheme()
        
        if self.enable_logging:
            self.logger.log_event("Color Scheme", f"Scheme changed to {scheme}")
        
        print(f"Color scheme changed to: {scheme}")
        return scheme

    def adjust_size_variation(self, change: float):
        """
        Adjust the size variation factor for directional eye sizing.
        
        Args:
            change (float): Amount to change size variation factor.
            
        Returns:
            float: The new size variation factor.
        """
        variation = self.effects.adjust_size_variation(change)
        
        if self.enable_logging:
            self.logger.log_event("Size Variation", f"Variation changed to {variation:.2f}")
        
        print(f"Size variation factor: {variation:.2f}")
        return variation