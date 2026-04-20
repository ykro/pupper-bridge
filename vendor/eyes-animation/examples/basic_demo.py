#!/usr/bin/env python3
"""
Basic demonstration of the Robot Eyes animation with automated
mood changes and movement patterns.

This script provides a simple automated demonstration of the 
eyes animation capabilities without requiring user interaction.
"""
import pygame
import random
import sys
import os
import time

# Add the parent directory to the path so we can import the src package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.eyes import Eyes, MoodState, LookDirection, ColorScheme
from src.eyes.config import (
    BLACK, BLINK_INTERVAL, RANDOM_MOOD_INTERVAL, 
    RANDOM_COLOR_INTERVAL, RANDOM_SIZE_INTERVAL
)


def main():
    """Run a basic automated demo of the robot eyes animation."""
    # Initialize Pygame
    pygame.init()
    
    # Set up display
    SCREEN_WIDTH = 720
    SCREEN_HEIGHT = 480
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Robot Eyes - Basic Demo")
    clock = pygame.time.Clock()
    
    # Initialize the eyes
    eyes = Eyes(screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)
    
    # Timing variables for random effects
    last_blink = pygame.time.get_ticks()
    last_mood_change = pygame.time.get_ticks()
    last_color_change = pygame.time.get_ticks()
    last_size_change = pygame.time.get_ticks()
    
    # Set next intervals
    next_mood_interval = random.randint(*RANDOM_MOOD_INTERVAL)
    next_color_interval = random.randint(*RANDOM_COLOR_INTERVAL)
    next_size_interval = random.randint(*RANDOM_SIZE_INTERVAL)
    
    # Available moods for random selection
    moods = [MoodState.NORMAL, MoodState.HAPPY, MoodState.CONFUSED, MoodState.SURPRISED]
    
    # Main demo loop
    running = True
    print("Basic Robot Eyes Demo")
    print("Press 'Q' to quit, 'P' to toggle pattern mode")
    
    while running:
        current_time = pygame.time.get_ticks()
        
        # Handle events (just for quitting and basic controls)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_p:
                    pattern_mode = eyes.movement.toggle_movement_mode()
                    pattern = eyes.movement.current_pattern if pattern_mode else "None"
                    print(f"Pattern mode: {pattern_mode}, Current pattern: {pattern}")
        
        # Random blinking
        if current_time - last_blink > BLINK_INTERVAL:
            eyes.start_blink()
            last_blink = current_time
            interval_variation = random.randint(-1000, 1000)
            last_blink += interval_variation
        
        # Random mood changes
        if current_time - last_mood_change > next_mood_interval:
            # Select a new random mood
            new_mood = random.choice(moods)
            eyes.set_mood(new_mood)
            print(f"Mood changed to: {new_mood.value}")
            
            # Schedule next mood change
            last_mood_change = current_time
            next_mood_interval = random.randint(*RANDOM_MOOD_INTERVAL)
        
        # Random color scheme changes
        if current_time - last_color_change > next_color_interval:
            # Change to a new color scheme
            new_scheme = eyes.cycle_color_scheme()
            print(f"Color scheme changed to: {new_scheme}")
            
            # Schedule next color change
            last_color_change = current_time
            next_color_interval = random.randint(*RANDOM_COLOR_INTERVAL)
        
        # Random size changes
        if current_time - last_size_change > next_size_interval:
            # Randomly increase or decrease eye size
            size_change = random.choice([-50, 50])
            new_size = eyes.adjust_size(size_change)
            print(f"Size changed to: {new_size[0]}x{new_size[1]}")
            
            # Schedule next size change
            last_size_change = current_time
            next_size_interval = random.randint(*RANDOM_SIZE_INTERVAL)
        
        # Update and draw
        eyes.update()
        screen.fill(BLACK)
        eyes.draw(screen)
        pygame.display.flip()
        
        # Control frame rate
        clock.tick(60)
    
    pygame.quit()


if __name__ == "__main__":
    main()