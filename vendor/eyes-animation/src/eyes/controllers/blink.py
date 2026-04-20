"""
Blink controller for the Eyes Animation system.

This module provides the controller for handling eye blinking animation.
It manages blink state, timing, and provides natural blinking patterns.
"""
import random
from ..config import DEFAULT_BLINK_SPEED


class BlinkController:
    """
    Controls the blinking animation for the eyes with natural timing and dynamics.
    
    The controller manages blink state, schedules natural blinking patterns,
    and provides a realistic eyelid movement during blinks.
    """
    
    def __init__(self):
        """Initialize the blink controller with default settings."""
        self.blink_state = 1.0  # Fully open
        self.blink_speed = DEFAULT_BLINK_SPEED
        self.is_blinking = False
        self.next_blink_time = 0
        
    def _get_next_blink_interval(self):
        """
        Generate a natural interval until the next blink.
        
        Returns:
            float: Time in seconds until the next blink should occur.
        """
        # Average blink every 3-4 seconds with variation
        base_interval = random.uniform(2.5, 4.5)
        
        # Add slight randomness to create more natural timing
        variation = random.gauss(0, 0.5)
        return max(1.5, base_interval + variation)

    def start_blink(self):
        """
        Initiate a blink with natural variation in speed.
        
        Starts the blink animation if not already blinking.
        """
        if not self.is_blinking:
            self.is_blinking = True
            
            # Vary blink duration slightly for more natural effect
            self.blink_speed = random.uniform(0.15, 0.25)
            self.blink_state = 1.0  # Start from fully open

    def update(self):
        """
        Update the blink state for the current frame.
        
        This method should be called once per frame to update the 
        blink animation state.
        """
        if self.is_blinking:
            # Update blink state based on speed
            self.blink_state -= self.blink_speed
            
            if self.blink_state <= 0:
                # Reached fully closed, begin opening
                self.blink_state = 0
                self.blink_speed = -self.blink_speed  # Reverse direction
            elif self.blink_state >= 1:
                # Reached fully open, complete blink
                self.blink_state = 1
                self.is_blinking = False
                self.blink_speed = abs(self.blink_speed)  # Ensure positive for next blink
                
                # Schedule next blink
                self.next_blink_time = self._get_next_blink_interval()