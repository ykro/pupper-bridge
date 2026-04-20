"""
Eyes Animation package for robot eye visualization.

This package provides a comprehensive framework for creating expressive
animated robot eyes with customizable mood states, movements, and visual effects.
"""

from .animation import Eyes
from .config import MoodState, LookDirection, ColorScheme

__all__ = ['Eyes', 'MoodState', 'LookDirection', 'ColorScheme']