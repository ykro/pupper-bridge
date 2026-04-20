"""
Controllers for the Eyes Animation system.

This package provides specialized controllers for different aspects
of the eye animation, including blinking, mood expressions, visual effects,
and eye movement.
"""

from .blink import BlinkController
from .mood import MoodController
from .effects import EffectsController
from .movement import MovementController

__all__ = ['BlinkController', 'MoodController', 'EffectsController', 'MovementController']