# Getting Started with Eyes Animation

This guide will walk you through the basic setup and usage of the Eyes Animation library.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/eyes-animation.git
cd eyes-animation
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Basic Usage

### Running the Demos

The easiest way to see the library in action is to run one of the included demos:

```bash
# Run the interactive demo with full controls
python -m examples.interactive_demo

# Run the basic automated demo
python -m examples.basic_demo
```

### Creating Your Own Animation

Here's a simple example of how to use the Eyes Animation library in your own code:

```python
import pygame
import sys
from src.eyes import Eyes, MoodState, LookDirection

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("My Eye Animation")
clock = pygame.time.Clock()

# Create the eyes
eyes = Eyes()

# Set initial properties
eyes.set_mood(MoodState.HAPPY)
eyes.cycle_color_scheme()  # Cycle to a different color scheme

# Main loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                eyes.start_blink()
    
    # Update and draw
    eyes.update()
    screen.fill((0, 0, 0))
    eyes.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
```

## Key Components

The library is structured around these main components:

1. **Eyes**: The main class that brings together all controllers and handles rendering.
2. **Controllers**:
   - **MovementController**: Manages eye positions and movements
   - **MoodController**: Handles emotional expressions
   - **BlinkController**: Controls blinking animations
   - **EffectsController**: Manages visual effects like glow and colors

3. **Configuration**:
   - **MoodState**: Enum of possible mood states
   - **LookDirection**: Enum of possible eye directions
   - **ColorScheme**: Available color schemes

## Basic Customization

Here are some key methods for customizing the eyes:

```python
# Change mood
eyes.set_mood(MoodState.SURPRISED)

# Start a blink
eyes.start_blink()

# Move eyes in a specific direction
eyes.start_movement(LookDirection.UP_RIGHT)

# Adjust size
eyes.adjust_size(50)  # Make eyes bigger

# Change colors
eyes.cycle_color_scheme()

# Adjust effects
eyes.adjust_glow_size(10)
eyes.adjust_glow_intensity(50)
eyes.adjust_border_thickness(2)
```

## Logging

The library includes optional logging capability:

```python
# Create eyes with logging enabled
eyes = Eyes(enable_logging=True)
```

This will create log files in a `logs` directory that track eye states, movements, and events.

## Next Steps

- Check out the [Controllers](controllers.md) documentation for more advanced customization.
- See the [Examples](examples.md) guide for more detailed usage examples.