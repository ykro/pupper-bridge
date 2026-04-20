"""
Configuration for the Eyes Animation system.

This module contains all the enums, constants, and settings 
for the animation system including colors, sizes, and timing parameters.
"""
from enum import Enum


class MoodState(Enum):
    """Defines possible mood states for the eyes."""
    NORMAL = "normal"
    HAPPY = "happy"
    CONFUSED = "confused"
    SURPRISED = "surprised"


class LookDirection(Enum):
    """Defines possible eye direction states."""
    CENTER = "center"
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    UP_LEFT = "up_left"
    UP_RIGHT = "up_right"
    DOWN_LEFT = "down_left"
    DOWN_RIGHT = "down_right"


class ColorScheme(Enum):
    """Defines possible color schemes for the eyes."""
    CYBER = "cyber"        # Blue-green holographic
    NEON = "neon"          # Teal cyberpunk
    AMBER = "amber"        # Classic amber
    PLASMA = "plasma"      # Purple energy
    ICE = "ice"            # Ice white
    ENERGY = "energy"      # Power green
    BLOOD = "blood"        # Blood red
    VOID = "void"          # Dark void
    INFERNO = "inferno"    # Hellfire orange


# Display settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Eye size constraints and defaults
MIN_EYE_SIZE = 20
MAX_EYE_SIZE = 600
DEFAULT_EYE_WIDTH = 300
DEFAULT_EYE_HEIGHT = 300
DEFAULT_EYE_SPACING = 40

# Border settings
MIN_BORDER_THICKNESS = 1
MAX_BORDER_THICKNESS = 20
DEFAULT_BORDER_THICKNESS = 4

# Glow settings
MIN_GLOW_RADIUS = 5
MAX_GLOW_RADIUS = 50
DEFAULT_GLOW_RADIUS = 20

MIN_GLOW_INTENSITY = 0
MAX_GLOW_INTENSITY = 255
DEFAULT_GLOW_INTENSITY = 128

# Animation timings (in milliseconds)
BLINK_INTERVAL = 3000
MOOD_DURATION = 2000
IDLE_MOVE_INTERVAL = 2000
MOVE_DURATION = 500
TRANSITION_DURATION = 200

# Mood animation settings
HAPPY_BOUNCE_SPEED = 2.0  # Speed of bouncing in happy mood
HAPPY_BOUNCE_AMPLITUDE = 15  # Maximum bounce height in pixels

# Movement settings
MOVE_AMOUNT = 60

# Default Animation Values
DEFAULT_BLINK_SPEED = 0.2

# Random animation intervals
RANDOM_MOOD_INTERVAL = (2000, 5000)    # Random mood change every 2-5 seconds
RANDOM_COLOR_INTERVAL = (5000, 10000)  # Random color change every 5-10 seconds
RANDOM_SIZE_INTERVAL = (3000, 7000)    # Random size change every 3-7 seconds
RANDOM_EFFECT_INTERVAL = (1000, 4000)  # Random effect change every 1-4 seconds

# Effect change amounts
GLOW_CHANGE_AMOUNT = 5      # Amount to change glow size by
BORDER_CHANGE_AMOUNT = 1    # Amount to change border thickness by
SIZE_CHANGE_AMOUNT = 50     # Amount to change eye size by
INTENSITY_CHANGE_AMOUNT = 25 # Amount to change glow intensity by

# Color schemes
COLOR_SCHEMES = {
    ColorScheme.CYBER: {
        'primary': (0, 180, 255),      # Electric blue
        'secondary': (0, 140, 200),    # Darker blue for depth
        'glow': (100, 200, 255)        # Soft blue glow
    },
    ColorScheme.NEON: {
        'primary': (0, 255, 200),      # Cyberpunk teal
        'secondary': (0, 200, 160),    # Deeper teal
        'glow': (100, 255, 220)        # Soft teal glow
    },
    ColorScheme.AMBER: {
        'primary': (255, 160, 0),      # Classic amber
        'secondary': (200, 120, 0),    # Darker amber for depth
        'glow': (255, 200, 100)        # Warm amber glow
    },
    ColorScheme.PLASMA: {
        'primary': (147, 51, 255),     # Deep purple
        'secondary': (106, 27, 224),   # Darker purple for depth
        'glow': (180, 120, 255)        # Soft purple plasma glow
    },
    ColorScheme.ICE: {
        'primary': (220, 240, 255),    # Ice white with blue tint
        'secondary': (180, 220, 255),  # Soft blue ice
        'glow': (200, 230, 255)        # Crystalline glow
    },
    ColorScheme.ENERGY: {
        'primary': (50, 255, 50),      # Energy green
        'secondary': (30, 200, 30),    # Deeper green
        'glow': (150, 255, 150)        # Radioactive-style glow
    },
    ColorScheme.BLOOD: {
        'primary': (255, 0, 0),        # Pure red
        'secondary': (180, 0, 0),      # Dark blood red
        'glow': (255, 30, 30)          # Menacing red glow
    },
    ColorScheme.VOID: {
        'primary': (100, 0, 200),      # Deep violet
        'secondary': (60, 0, 120),     # Dark void purple
        'glow': (140, 0, 255)          # Ethereal violet glow
    },
    ColorScheme.INFERNO: {
        'primary': (255, 60, 0),       # Bright orange-red
        'secondary': (200, 30, 0),     # Dark fire red
        'glow': (255, 100, 0)          # Burning orange glow
    }
}