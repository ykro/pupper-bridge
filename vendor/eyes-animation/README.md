# Eyes Animation

A sophisticated and customizable animation framework for creating expressive robot eyes with Python and Pygame.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![Demo Animation](docs/images/eyes_demo.gif)

## Demo Video

Watch a demonstration of the Eyes Animation system in action:

[![Eyes Animation Demo](https://img.youtube.com/vi/gdqVSGmf2uk/0.jpg)](https://youtu.be/gdqVSGmf2uk)

## Features

- Smooth, natural eye animations with realistic blinking
- Multiple mood expressions (normal, happy, confused, surprised)
- Directional eye movement with pattern support
- Customizable visual effects (glow, border thickness, color schemes)
- Comprehensive logging system for animation states
- Interactive demo with full keyboard controls
- Video recording functionality to capture animations

## Requirements

- Python 3.7+
- Pygame
- Loguru
- OpenCV (for recording functionality)

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/eyes-animation.git
cd eyes-animation

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

Run the interactive demo:

```bash
python -m examples.interactive_demo
```

For the version with recording capabilities:

```bash
python -m examples.interactive_demo_record
```

Basic usage in your own code:

```python
from src.eyes import Eyes, MoodState, LookDirection

# Initialize the eyes
eyes = Eyes()

# Set a mood
eyes.set_mood(MoodState.HAPPY)

# Start eye movement
eyes.start_movement(LookDirection.UP)

# In your game/animation loop:
while running:
    eyes.update()
    eyes.draw(screen)
    pygame.display.flip()
    clock.tick(60)
```

## Documentation

- [Getting Started](docs/getting_started.md)
- [Controllers](docs/controllers.md)
- [Examples](docs/examples.md)

## Controls for Interactive Demo

| Key       | Action                       |
|-----------|------------------------------|
| Arrow Keys | Control eye direction        |
| 1-4        | Change mood                  |
| Space      | Force blink                  |
| +/-        | Adjust eye size              |
| [/]        | Adjust glow size             |
| ,/.        | Adjust glow intensity        |
| O/P        | Adjust border thickness      |
| C          | Cycle color scheme           |
| G          | Toggle grid                  |
| R          | Reset to center              |
| M          | Toggle movement pattern mode |
| L          | Toggle logging               |
| H          | Show help                    |
| Q          | Quit                         |

Recording demo also includes:
- Record button: Start recording animation
- Stop button: Stop recording and save MP4 file

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by [FluxGarage's RoboEyes](https://github.com/FluxGarage/RoboEyes) Arduino library
- Created with assistance from AI models (Claude & ChatGPT)
- Special thanks to the Pygame community
