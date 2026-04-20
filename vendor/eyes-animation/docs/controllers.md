# Controllers Documentation

The Eyes Animation system is built around a set of specialized controllers that handle different aspects of the animation. This modular approach allows for fine-grained control and customization of the eye behavior.

## Overview of Controllers

The system uses four primary controllers:

1. **MovementController**: Handles eye positioning and motion
2. **BlinkController**: Manages natural blinking behavior
3. **MoodController**: Controls emotional expressions
4. **EffectsController**: Manages visual effects like glow and color schemes

## MovementController

The MovementController manages the position and movement of the eyes, including both random natural movements and pattern-based sequences.

### Key Methods

```python
# Start movement in a specific direction
eyes.movement.start_movement(LookDirection.UP)

# Toggle between random and pattern-based movement
is_pattern_mode = eyes.movement.toggle_movement_mode()

# Get current movement statistics
stats = eyes.movement.get_movement_stats()
```

### Movement Patterns

The controller supports predefined movement patterns:

- **Square**: Cycles through up, right, down, left directions
- **Diamond**: Creates a diamond pattern using diagonal movements

Example:
```python
# Enable pattern movement mode
eyes.movement.toggle_movement_mode()  # Returns True when enabled

# Movement will now follow patterns automatically
```

### Customizing Movement

You can adjust movement variation to create more natural, less mechanical movements:

```python
# Access movement variation directly
eyes.movement.movement_variation = 0.3  # 30% random variation
```

## BlinkController

The BlinkController manages natural blinking behaviors with randomized timing and duration.

### Key Methods

```python
# Trigger a blink manually
eyes.blink.start_blink()

# Check if currently blinking
is_blinking = eyes.blink.is_blinking
```

### Blinking Parameters

The controller offers several adjustable parameters:

- **blink_state**: Current state of eyelid (1.0 = fully open, 0.0 = fully closed)
- **blink_speed**: Speed of blinking motion (adjustable for different effects)

Example:
```python
# Speed up blinking motion
eyes.blink.blink_speed = 0.3  # Default is 0.2

# Access current blink state (useful for custom rendering)
current_openness = eyes.blink.blink_state
```

## MoodController

The MoodController manages emotional expressions through eye shape modifications and animations.

### Key Methods

```python
# Set a specific mood
eyes.mood.set_mood(MoodState.HAPPY)

# Check current mood
current_mood = eyes.mood.current_mood
```

### Available Moods

- **NORMAL**: Default neutral expression
- **HAPPY**: Upward curved eyes with slight bouncing
- **CONFUSED**: Asymmetrical eyes with one slightly squinted
- **SURPRISED**: Enlarged eyes

### Mood Transitions

The controller handles smooth transitions between mood states:

```python
# Access transition progress (useful for custom rendering)
transition_progress = eyes.mood.mood_transition_progress
```

## EffectsController

The EffectsController manages visual effects including glow, border thickness, color schemes, and size variations.

### Key Methods

```python
# Adjust glow radius
eyes.effects.adjust_glow_size(5)  # Increase by 5px

# Adjust glow intensity
eyes.effects.adjust_glow_intensity(25)  # Increase by 25 units

# Adjust border thickness
eyes.effects.adjust_border_thickness(1)  # Increase by 1px

# Cycle color scheme
new_scheme = eyes.effects.cycle_color_scheme()

# Adjust size variation for directional effects
eyes.effects.adjust_size_variation(0.05)  # Increase by 5%
```

### Color Schemes

The system includes several predefined color schemes:

- **CYBER**: Blue-green holographic
- **NEON**: Teal cyberpunk
- **AMBER**: Classic amber terminal
- **PLASMA**: Purple energy
- **ICE**: Ice white
- **ENERGY**: Power green
- **BLOOD**: Blood red
- **VOID**: Dark void
- **INFERNO**: Hellfire orange

Example:
```python
# Set a specific color scheme directly
eyes.effects.current_scheme = ColorScheme.PLASMA
```

## Advanced Usage: Combining Controllers

The power of the controller system comes from combining effects:

```python
# Create a surprised, glowing red expression
eyes.set_mood(MoodState.SURPRISED)
eyes.effects.current_scheme = ColorScheme.BLOOD
eyes.effects.adjust_glow_intensity(50)
eyes.effects.adjust_glow_size(10)

# Create a confused, looking upward expression
eyes.set_mood(MoodState.CONFUSED)
eyes.movement.start_movement(LookDirection.UP)
```

## Extending Controllers

You can extend the controllers by subclassing them for custom behaviors:

```python
from src.eyes.controllers import BlinkController

class CustomBlinker(BlinkController):
    def __init__(self):
        super().__init__()
        # Custom initialization
    
    def update(self):
        # Custom update logic
        super().update()
        # Additional effects
```

Then use your custom controller:

```python
custom_blinker = CustomBlinker()
eyes.blink = custom_blinker
```