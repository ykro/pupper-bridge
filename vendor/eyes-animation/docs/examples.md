# Examples Guide

This document provides examples of how to use the Eyes Animation library for different scenarios and applications.

## Basic Examples

### 1. Creating a Simple Eye Animation

```python
import pygame
import sys
from src.eyes import Eyes

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Basic Eye Animation")
clock = pygame.time.Clock()

# Create eyes
eyes = Eyes()

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Update and draw
    eyes.update()
    screen.fill((0, 0, 0))
    eyes.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
```

### 2. Adding Basic User Interaction

```python
import pygame
import sys
from src.eyes import Eyes, MoodState, LookDirection

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Interactive Eye Animation")
clock = pygame.time.Clock()

# Create eyes
eyes = Eyes()

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # Mood controls
            if event.key == pygame.K_1:
                eyes.set_mood(MoodState.NORMAL)
            elif event.key == pygame.K_2:
                eyes.set_mood(MoodState.HAPPY)
            elif event.key == pygame.K_3:
                eyes.set_mood(MoodState.CONFUSED)
            elif event.key == pygame.K_4:
                eyes.set_mood(MoodState.SURPRISED)
            
            # Direction controls
            elif event.key == pygame.K_UP:
                eyes.start_movement(LookDirection.UP)
            elif event.key == pygame.K_DOWN:
                eyes.start_movement(LookDirection.DOWN)
            elif event.key == pygame.K_LEFT:
                eyes.start_movement(LookDirection.LEFT)
            elif event.key == pygame.K_RIGHT:
                eyes.start_movement(LookDirection.RIGHT)
            
            # Special controls
            elif event.key == pygame.K_SPACE:
                eyes.start_blink()
            elif event.key == pygame.K_c:
                eyes.cycle_color_scheme()
    
    # Update and draw
    eyes.update()
    screen.fill((0, 0, 0))
    eyes.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
```

## Advanced Examples

### 1. Creating Character Expressions

This example shows how to create different character expressions by combining mood and effect settings:

```python
import pygame
import sys
import time
from src.eyes import Eyes, MoodState, LookDirection, ColorScheme

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Character Expressions")
clock = pygame.time.Clock()

# Create eyes
eyes = Eyes()

# Define character expressions
expressions = [
    # Curious
    {
        "mood": MoodState.NORMAL,
        "direction": LookDirection.UP_RIGHT,
        "scheme": ColorScheme.CYBER,
        "size_variation": 0.15,
        "glow_size": 20,
        "glow_intensity": 100
    },
    # Angry
    {
        "mood": MoodState.NORMAL,
        "direction": LookDirection.DOWN,
        "scheme": ColorScheme.BLOOD,
        "size_variation": 0.3,
        "glow_size": 30,
        "glow_intensity": 150
    },
    # Sleepy
    {
        "mood": MoodState.NORMAL,
        "direction": LookDirection.CENTER,
        "scheme": ColorScheme.AMBER,
        "size_variation": 0.1,
        "glow_size": 15,
        "glow_intensity": 50
    },
    # Excited
    {
        "mood": MoodState.SURPRISED,
        "direction": LookDirection.CENTER,
        "scheme": ColorScheme.ENERGY,
        "size_variation": 0.2,
        "glow_size": 25,
        "glow_intensity": 200
    }
]

# Function to apply expression
def apply_expression(eyes, expression):
    eyes.set_mood(expression["mood"])
    eyes.start_movement(expression["direction"])
    eyes.effects.current_scheme = expression["scheme"]
    eyes.effects.glow_radius = expression["glow_size"]
    eyes.effects.glow_intensity = expression["glow_intensity"]
    eyes.effects.size_variation_factor = expression["size_variation"]

# Main loop
running = True
current_expression = 0
next_change = time.time() + 3  # Change every 3 seconds

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Change expression every few seconds
    if time.time() > next_change:
        current_expression = (current_expression + 1) % len(expressions)
        apply_expression(eyes, expressions[current_expression])
        next_change = time.time() + 3
    
    # Update and draw
    eyes.update()
    screen.fill((0, 0, 0))
    eyes.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
```

### 2. Responding to External Data

This example shows how to make the eyes respond to external data (like sensor readings):

```python
import pygame
import sys
import random
import math
from src.eyes import Eyes, MoodState, LookDirection, ColorScheme

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Data Responsive Eyes")
clock = pygame.time.Clock()

# Create eyes
eyes = Eyes()

# Simulated data class (in a real app, this would get data from sensors)
class DataSource:
    def __init__(self):
        self.temperature = 75  # Degrees F
        self.light_level = 50  # Percent
        self.motion_detected = False
        self.noise_level = 30  # Decibels
    
    def update(self):
        # Simulate changing data
        self.temperature += random.uniform(-1, 1)
        self.light_level += random.uniform(-5, 5)
        self.light_level = max(0, min(100, self.light_level))
        self.motion_detected = random.random() < 0.1  # 10% chance
        self.noise_level = max(10, min(90, self.noise_level + random.uniform(-3, 3)))

# Create data source
data_source = DataSource()

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Update simulated data
    data_source.update()
    
    # Respond to temperature
    if data_source.temperature > 85:
        eyes.effects.current_scheme = ColorScheme.BLOOD
    elif data_source.temperature < 65:
        eyes.effects.current_scheme = ColorScheme.ICE
    else:
        eyes.effects.current_scheme = ColorScheme.CYBER
    
    # Respond to light level
    eyes.effects.glow_intensity = int(data_source.light_level * 2.55)  # Convert to 0-255
    
    # Respond to motion
    if data_source.motion_detected:
        eyes.set_mood(MoodState.SURPRISED)
    else:
        eyes.set_mood(MoodState.NORMAL)
    
    # Respond to noise (changes eye size)
    base_size = 150
    size_factor = 1 + (data_source.noise_level / 100)
    new_size = int(base_size * size_factor)
    eyes.adjust_size(new_size - eyes.EYE_WIDTH)
    
    # Update and draw
    eyes.update()
    screen.fill((0, 0, 0))
    
    # Draw data overlay
    font = pygame.font.Font(None, 24)
    data_text = (
        f"Temperature: {data_source.temperature:.1f}°F | "
        f"Light: {data_source.light_level:.0f}% | "
        f"Noise: {data_source.noise_level:.0f}dB | "
        f"Motion: {'Yes' if data_source.motion_detected else 'No'}"
    )
    text_surf = font.render(data_text, True, (255, 255, 255))
    screen.blit(text_surf, (10, 10))
    
    eyes.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
```

## Practical Applications

### 1. Robot Interface

The library includes a complete robot interface example in `src/applications/robot_interface.py`. You can run it directly:

```python
from src.applications.robot_interface import main

main()
```

This application demonstrates how to:
- Integrate eyes with a user interface
- Create interactive controls
- Simulate external input (object detection)
- Build a practical UI around the eye animations

### 2. Creating a Virtual Pet

Here's how you could use the library to create a simple virtual pet:

```python
import pygame
import sys
import random
import time
from src.eyes import Eyes, MoodState, LookDirection

class VirtualPet:
    def __init__(self):
        # Pet state
        self.happiness = 50  # 0-100
        self.energy = 100    # 0-100
        self.last_interaction = time.time()
        
        # Create eyes for the pet
        self.eyes = Eyes()
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Virtual Pet")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
    
    def update_pet_state(self):
        current_time = time.time()
        
        # Decrease happiness over time
        time_since_interaction = current_time - self.last_interaction
        self.happiness = max(0, self.happiness - (time_since_interaction * 0.01))
        
        # Decrease energy over time
        self.energy = max(0, self.energy - 0.01)
        
        # Update eye expression based on pet state
        if self.happiness > 75:
            self.eyes.set_mood(MoodState.HAPPY)
        elif self.happiness < 25:
            self.eyes.set_mood(MoodState.CONFUSED)
        elif self.energy < 20:
            self.eyes.set_mood(MoodState.SURPRISED)
            self.eyes.start_blink()  # Blink more when tired
        else:
            self.eyes.set_mood(MoodState.NORMAL)
    
    def handle_interaction(self, interaction_type):
        self.last_interaction = time.time()
        
        if interaction_type == "pet":
            self.happiness = min(100, self.happiness + 10)
            self.eyes.set_mood(MoodState.HAPPY)
            self.eyes.start_movement(LookDirection.UP)
        
        elif interaction_type == "feed":
            self.energy = min(100, self.energy + 20)
            self.happiness = min(100, self.happiness + 5)
            self.eyes.set_mood(MoodState.HAPPY)
        
        elif interaction_type == "play":
            if self.energy > 30:
                self.happiness = min(100, self.happiness + 15)
                self.energy = max(0, self.energy - 10)
                self.eyes.set_mood(MoodState.SURPRISED)
            else:
                # Too tired to play
                self.eyes.set_mood(MoodState.CONFUSED)
                self.eyes.start_movement(LookDirection.DOWN)
    
    def run(self):
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.handle_interaction("pet")
                    elif event.key == pygame.K_f:
                        self.handle_interaction("feed")
                    elif event.key == pygame.K_SPACE:
                        self.handle_interaction("play")
            
            # Update pet state and eyes
            self.update_pet_state()
            self.eyes.update()
            
            # Draw everything
            self.screen.fill((0, 0, 0))
            
            # Draw status bars
            pygame.draw.rect(self.screen, (255, 0, 0), (50, 500, int(self.happiness * 3), 20))
            happiness_text = self.font.render("Happiness", True, (255, 255, 255))
            self.screen.blit(happiness_text, (50, 470))
            
            pygame.draw.rect(self.screen, (0, 0, 255), (450, 500, int(self.energy * 3), 20))
            energy_text = self.font.render("Energy", True, (255, 255, 255))
            self.screen.blit(energy_text, (450, 470))
            
            # Draw instructions
            instructions = self.font.render("P: Pet | F: Feed | Space: Play", True, (255, 255, 255))
            self.screen.blit(instructions, (200, 550))
            
            # Draw eyes
            self.eyes.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

# Run the virtual pet
if __name__ == "__main__":
    pet = VirtualPet()
    pet.run()
```

## More Examples

For more examples, explore the `examples` directory in the repository. The interactive_demo.py file in particular demonstrates a comprehensive range of the library's capabilities.