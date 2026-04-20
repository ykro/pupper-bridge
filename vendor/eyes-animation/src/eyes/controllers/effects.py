"""
Effects controller for the Eyes Animation system.

This module provides the controller for managing visual effects
like glow, border thickness, color schemes, and size variations.
"""
from ..config import (
    ColorScheme, DEFAULT_GLOW_RADIUS, DEFAULT_GLOW_INTENSITY,
    DEFAULT_BORDER_THICKNESS, MIN_GLOW_RADIUS, MAX_GLOW_RADIUS,
    MIN_GLOW_INTENSITY, MAX_GLOW_INTENSITY, MIN_BORDER_THICKNESS,
    MAX_BORDER_THICKNESS
)


class EffectsController:
    """
    Controls the visual effects for the eyes animation.
    
    The controller manages glow effects, border thickness, color schemes,
    and eye size variations to create diverse visual styles.
    """
    
    def __init__(self):
        """Initialize the effects controller with default settings."""
        # Glow settings
        self.glow_radius = DEFAULT_GLOW_RADIUS
        self.glow_intensity = DEFAULT_GLOW_INTENSITY
        
        # Border settings
        self.border_thickness = DEFAULT_BORDER_THICKNESS
        
        # Color scheme
        self.current_scheme = ColorScheme.CYBER
        
        # Size variation for directional effects
        self.size_variation_factor = 0.2  # Default 20% size variation
        self.MIN_SIZE_VARIATION = 0.0
        self.MAX_SIZE_VARIATION = 0.5  # 50% max variation

    def adjust_glow_size(self, change):
        """
        Adjust the glow radius with constraints.
        
        Args:
            change (int): Amount to change the glow radius.
            
        Returns:
            int: The new glow radius value.
        """
        self.glow_radius = max(MIN_GLOW_RADIUS, min(MAX_GLOW_RADIUS, self.glow_radius + change))
        return self.glow_radius

    def adjust_glow_intensity(self, change):
        """
        Adjust the glow intensity with constraints.
        
        Args:
            change (int): Amount to change the glow intensity.
            
        Returns:
            int: The new glow intensity value.
        """
        self.glow_intensity = max(MIN_GLOW_INTENSITY, min(MAX_GLOW_INTENSITY, self.glow_intensity + change))
        return self.glow_intensity

    def adjust_border_thickness(self, change):
        """
        Adjust the border thickness with constraints.
        
        Args:
            change (int): Amount to change the border thickness.
            
        Returns:
            int: The new border thickness value.
        """
        self.border_thickness = max(MIN_BORDER_THICKNESS, min(MAX_BORDER_THICKNESS, self.border_thickness + change))
        return self.border_thickness

    def adjust_size_variation(self, change):
        """
        Adjust the size variation factor with min/max constraints.
        
        Args:
            change (float): Amount to change the size variation factor.
            
        Returns:
            float: The new size variation factor.
        """
        self.size_variation_factor = max(
            self.MIN_SIZE_VARIATION, 
            min(self.MAX_SIZE_VARIATION, 
                self.size_variation_factor + change)
        )
        return self.size_variation_factor

    def cycle_color_scheme(self):
        """
        Cycle to the next color scheme in the enum.
        
        Returns:
            str: The name of the new color scheme.
        """
        schemes = list(ColorScheme)
        current_index = schemes.index(self.current_scheme)
        next_index = (current_index + 1) % len(schemes)
        self.current_scheme = schemes[next_index]
        return self.current_scheme.value