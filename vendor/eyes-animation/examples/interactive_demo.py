#!/usr/bin/env python3
"""
Interactive demonstration of the Robot Eyes animation
with full user controls for various eye parameters.
"""
import pygame
import random
import sys
import os

# Add the parent directory to the path so we can import the src package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.eyes import Eyes, MoodState, LookDirection
from src.eyes.config import BLINK_INTERVAL, BLACK


def print_controls():
    """Print the control instructions to the console."""
    print("\nRobot Eyes Demo Controls:")
    print("=" * 50)
    print("Movement Controls:")
    print("  Arrow Keys: Control eye direction")
    print("  R: Reset to center")
    print("  M: Toggle between pattern/random movement")
    print("  T: Show current movement statistics")
    
    print("\nMood Controls:")
    print("  1: Normal mood")
    print("  2: Happy mood")
    print("  3: Confused mood")
    print("  4: Surprised mood")
    
    print("\nAnimation Controls:")
    print("  Space: Force blink")
    print("  +/-: Adjust eye size")
    print("  O/P: Adjust border thickness")
    print("  [/]: Adjust glow size")
    print("  ,/.: Adjust glow intensity")
    
    print("\nVisual Controls:")
    print("  C: Cycle color scheme")
    print("  A/S: Adjust directional size variation")
    print("  G: Toggle grid")
    print("  L: Toggle logging")
    
    print("\nOther Controls:")
    print("  H: Show this help menu")
    print("  Q: Quit")
    print("=" * 50)


def main():
    """Run the interactive robot eyes demo."""
    # Initialize Pygame
    pygame.init()
    
    # Set up display with specific dimensions
    DEMO_WIDTH = 720
    DEMO_HEIGHT = 640
    screen = pygame.display.set_mode((DEMO_WIDTH, DEMO_HEIGHT))
    pygame.display.set_caption("Robot Eyes Demo")
    clock = pygame.time.Clock()
    
    # Create eyes with demo-specific screen dimensions
    eyes = Eyes(
        enable_logging=False,
        screen_width=DEMO_WIDTH,
        screen_height=DEMO_HEIGHT
    )
    
    # Track timing and state
    last_blink = pygame.time.get_ticks()
    running = True
    
    # Display and debugging toggles
    show_grid = False
    logging_enabled = False
    show_stats = False  # Toggle for movement statistics
    
    # Show initial instructions
    print_controls()
    
    while running:
        current_time = pygame.time.get_ticks()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Mood controls
                if event.key == pygame.K_1:
                    eyes.set_mood(MoodState.NORMAL)
                    print("Mood: Normal")
                elif event.key == pygame.K_2:
                    eyes.set_mood(MoodState.HAPPY)
                    print("Mood: Happy")
                elif event.key == pygame.K_3:
                    eyes.set_mood(MoodState.CONFUSED)
                    print("Mood: Confused")
                elif event.key == pygame.K_4:
                    eyes.set_mood(MoodState.SURPRISED)
                    print("Mood: Surprised")
                
                # Movement controls
                elif event.key == pygame.K_SPACE:
                    eyes.start_blink()
                elif event.key == pygame.K_r:
                    eyes.start_movement(LookDirection.CENTER)
                    print("Eyes centered")
                elif event.key == pygame.K_UP:
                    eyes.start_movement(LookDirection.UP)
                elif event.key == pygame.K_DOWN:
                    eyes.start_movement(LookDirection.DOWN)
                elif event.key == pygame.K_LEFT:
                    eyes.start_movement(LookDirection.LEFT)
                elif event.key == pygame.K_RIGHT:
                    eyes.start_movement(LookDirection.RIGHT)
                elif event.key == pygame.K_m:
                    is_pattern_mode = eyes.movement.toggle_movement_mode()
                    print(f"Movement mode: {'Pattern-based' if is_pattern_mode else 'Balanced Random'}")
                elif event.key == pygame.K_t:
                    show_stats = not show_stats
                    if show_stats:
                        stats = eyes.movement.get_movement_stats()
                        print("\nCurrent Movement Statistics:")
                        print(f"Mode: {stats['current_mode']}")
                        print(f"Current Pattern: {stats['current_pattern']}")
                        print(f"Direction Counts: {stats['direction_counts']}")
                        print(f"Recent History: {stats['recent_history']}")
                
                # Size and effect controls
                elif event.key in (pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS):
                    eyes.adjust_size(50)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    eyes.adjust_size(-50)
                elif event.key == pygame.K_c:
                    eyes.cycle_color_scheme()
                elif event.key == pygame.K_LEFTBRACKET:
                    eyes.adjust_glow_size(-5)
                elif event.key == pygame.K_RIGHTBRACKET:
                    eyes.adjust_glow_size(5)
                elif event.key == pygame.K_o:
                    eyes.adjust_border_thickness(-1)
                elif event.key == pygame.K_p:
                    eyes.adjust_border_thickness(1)
                elif event.key == pygame.K_COMMA:
                    eyes.adjust_glow_intensity(-25)
                elif event.key == pygame.K_PERIOD:
                    eyes.adjust_glow_intensity(25)
                elif event.key == pygame.K_a:
                    eyes.adjust_size_variation(-0.05)
                elif event.key == pygame.K_s:
                    eyes.adjust_size_variation(0.05)
                
                # Display toggles
                elif event.key == pygame.K_g:
                    show_grid = not show_grid
                    print(f"Grid {'enabled' if show_grid else 'disabled'}")
                elif event.key == pygame.K_l:
                    logging_enabled = not logging_enabled
                    eyes = Eyes(
                        enable_logging=logging_enabled,
                        screen_width=DEMO_WIDTH,
                        screen_height=DEMO_HEIGHT
                    )
                    print(f"Logging {'enabled' if logging_enabled else 'disabled'}")
                elif event.key == pygame.K_h:
                    print_controls()
                elif event.key == pygame.K_q:
                    if show_grid:
                        show_grid = False
                    else:
                        running = False
        
        # Random blinking
        if current_time - last_blink > BLINK_INTERVAL:
            eyes.start_blink()
            last_blink = current_time
            # Randomize next blink interval between 2 and 4 seconds
            interval_variation = random.randint(-1000, 1000)
            last_blink += interval_variation
        
        # Update and draw
        eyes.update()
        screen.fill(BLACK)
        
        # Draw grid if enabled
        if show_grid:
            eyes._draw_grid(screen)
        
        eyes.draw(screen)
        pygame.display.flip()
        
        # Control frame rate
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()