"""
Mood controller for the Eyes Animation system.

This module provides the controller for managing different emotional
states and their visual representations in the eye animation.
"""
import math
import pygame
from ..config import MoodState, MOOD_DURATION, TRANSITION_DURATION
from ..config import HAPPY_BOUNCE_SPEED, HAPPY_BOUNCE_AMPLITUDE


class MoodController:
    """
    Controls the mood expressions for the eyes animation.
    
    The controller manages transitions between different mood states,
    handles animation timing, and provides visual effects specific to each mood.
    """
    
    def __init__(self):
        """Initialize the mood controller with default settings."""
        self.current_mood = MoodState.NORMAL
        self.mood_start_time = 0
        self.mood_duration_progress = 0.0  # Track overall mood duration
        self.mood_transition_progress = 0.0  # Track transition animation
        
        # Animation properties for happy mood
        self.bounce_offset = 0
        self.bounce_speed = HAPPY_BOUNCE_SPEED
        self.bounce_amplitude = HAPPY_BOUNCE_AMPLITUDE

    def set_mood(self, mood):
        """
        Set the current mood with appropriate transition.
        
        Args:
            mood (MoodState): The mood state to transition to.
        """
        if mood != self.current_mood:
            self.current_mood = mood
            self.mood_start_time = pygame.time.get_ticks()
            self.mood_duration_progress = 0.0
            self.mood_transition_progress = 0.0

    def update(self, current_time):
        """
        Update the mood state for the current frame.
        
        Args:
            current_time (int): Current time in milliseconds, typically from
                                pygame.time.get_ticks().
        """
        elapsed = current_time - self.mood_start_time
        
        # Update transition animation progress
        if self.mood_transition_progress < 1.0:
            self.mood_transition_progress = min(1.0, elapsed / TRANSITION_DURATION)
        
        # Update overall mood duration and reset if needed
        if self.current_mood != MoodState.NORMAL:
            self.mood_duration_progress = elapsed / MOOD_DURATION
            # Automatically return to normal mood after duration
            if self.mood_duration_progress >= 1.0:
                self.set_mood(MoodState.NORMAL)
        
        # Update bounce animation for happy mood
        if self.current_mood == MoodState.HAPPY:
            time_factor = (elapsed * self.bounce_speed) / 100
            self.bounce_offset = math.sin(time_factor) * self.bounce_amplitude
        else:
            self.bounce_offset = 0