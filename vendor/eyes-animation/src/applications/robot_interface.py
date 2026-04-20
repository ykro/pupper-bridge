"""
Robot interface application for the Eyes Animation system.

This module provides a practical application that integrates the eye animation
system with a robot interface, including camera input and state management.
"""
import pygame
import time
import random
from ..eyes import Eyes, MoodState, LookDirection, ColorScheme
from ..eyes.config import BLACK, BLINK_INTERVAL, COLOR_SCHEMES


class Button:
    """
    Interactive button for the robot interface.
    
    This class provides buttons with hover effects and click detection
    for controlling the robot interface.
    """
    
    def __init__(self, x, y, width, height, text, color, hover_color):
        """
        Initialize a button with position, size, and style.
        
        Args:
            x (int): X-coordinate of the button
            y (int): Y-coordinate of the button
            width (int): Width of the button
            height (int): Height of the button
            text (str): Text to display on the button
            color (tuple): RGB color for the button
            hover_color (tuple): RGB color for hover state
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.is_hovered = False
        self.font = pygame.font.Font(None, 42)  # Font size

    def draw(self, screen):
        """
        Draw the button on the screen.
        
        Args:
            screen (pygame.Surface): Screen surface to draw on
        """
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=12)
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        """
        Handle mouse events for the button.
        
        Args:
            event (pygame.event.Event): Event to process
            
        Returns:
            bool: True if the button was clicked, False otherwise
        """
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            self.current_color = self.hover_color if self.is_hovered else self.color
        return event.type == pygame.MOUSEBUTTONDOWN and self.is_hovered and event.button == 1


class RobotInterface:
    """
    Interface for controlling a robot with animated eyes.
    
    This class provides a complete interface for robot control with animated
    eyes, status display, and mock detection capabilities.
    """
    
    def __init__(self):
        """Initialize the robot interface and its components."""
        pygame.init()
        self.SCREEN_WIDTH = 720
        self.SCREEN_HEIGHT = 1280
        self.EYES_HEIGHT = 640
        self.VIDEO_HEIGHT = 640
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Robot Interface")
        self.clock = pygame.time.Clock()

        # App state
        self.is_welcome_screen = True
        self.is_running = False
        self.is_paused = False

        # Initialize font for status text
        self.font = pygame.font.Font(None, 48)
        self.welcome_font = pygame.font.Font(None, 64)

        # Initialize buttons
        button_width = 180
        button_height = 60
        button_spacing = 25
        
        # Position buttons at the bottom of eyes area
        buttons_y = self.EYES_HEIGHT - button_height - 30
        
        # Calculate total width of all buttons and spacing
        total_width = 3 * button_width + 2 * button_spacing
        start_x = (self.SCREEN_WIDTH - total_width) // 2

        # Button colors
        start_color = COLOR_SCHEMES[ColorScheme.CYBER]['primary']
        start_hover = COLOR_SCHEMES[ColorScheme.CYBER]['secondary']
        
        pause_color = COLOR_SCHEMES[ColorScheme.ICE]['primary']
        pause_hover = COLOR_SCHEMES[ColorScheme.ICE]['secondary']
        
        quit_color = COLOR_SCHEMES[ColorScheme.BLOOD]['primary']
        quit_hover = COLOR_SCHEMES[ColorScheme.BLOOD]['secondary']

        # Create buttons
        self.start_button = Button(
            start_x,
            buttons_y,
            button_width, button_height,
            "Start", start_color, start_hover
        )

        self.pause_button = Button(
            start_x + button_width + button_spacing,
            buttons_y,
            button_width, button_height,
            "Pause", pause_color, pause_hover
        )

        self.quit_button = Button(
            start_x + 2 * (button_width + button_spacing),
            buttons_y,
            button_width, button_height,
            "Quit", quit_color, quit_hover
        )

        # Initialize eyes animation
        self.eyes = Eyes(
            enable_logging=False, 
            screen_width=self.SCREEN_WIDTH, 
            screen_height=self.EYES_HEIGHT
        )
        
        # Set thicker border for eyes
        self.eyes.effects.adjust_border_thickness(8)

        # Mock detection state
        self.detection_interval = 2.0  # 2 seconds
        self.last_detection_time = time.time()
        self.current_detection = None
        self.mock_frame = None
        
        # Status and animation state
        self.last_blink = pygame.time.get_ticks()
        self.show_grid = False
        self.status_text = "Welcome!"
        self.status_color = COLOR_SCHEMES[ColorScheme.NEON]['primary']
        
        # Initialize default state
        self._set_normal_state()

    def _set_normal_state(self):
        """Set the default visual state for the robot eyes."""
        self.eyes.set_mood(MoodState.NORMAL)
        self.eyes.adjust_size(300 - self.eyes.EYE_WIDTH)
        self.eyes.effects.current_scheme = ColorScheme.NEON
        self.status_color = COLOR_SCHEMES[ColorScheme.NEON]['primary']
        self.eyes.effects.adjust_border_thickness(8)
        if not self.is_paused:
            self.status_text = "Monitoring..."

    def start_operation(self):
        """Start the robot operation mode."""
        self.is_welcome_screen = False
        self.is_running = True
        self.is_paused = False
        self.pause_button.text = "Pause"
        self.status_text = "Monitoring..."
        
        # Create a mock video frame (black surface)
        self.mock_frame = pygame.Surface((self.SCREEN_WIDTH, self.VIDEO_HEIGHT))
        self.mock_frame.fill((0, 0, 0))
        
# Draw grid lines on mock frame
        for i in range(0, self.SCREEN_WIDTH, 40):
            pygame.draw.line(self.mock_frame, (30, 30, 30), (i, 0), (i, self.VIDEO_HEIGHT))
        for i in range(0, self.VIDEO_HEIGHT, 40):
            pygame.draw.line(self.mock_frame, (30, 30, 30), (0, i), (self.SCREEN_WIDTH, i))

    def toggle_pause(self):
        """Toggle the pause state of the robot interface."""
        self.is_paused = not self.is_paused
        self.pause_button.text = "Continue" if self.is_paused else "Pause"
        if self.is_paused:
            self.status_text = "Paused"
        else:
            self.status_text = "Monitoring..."
            self._set_normal_state()

    def process_events(self):
        """
        Process pygame events and handle user input.
        
        Returns:
            bool: False if the application should exit, True otherwise
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # Handle button events
            if self.is_welcome_screen:
                if self.start_button.handle_event(event):
                    self.start_operation()
                elif self.quit_button.handle_event(event):
                    return False
            else:
                if self.pause_button.handle_event(event):
                    self.toggle_pause()
                elif self.quit_button.handle_event(event):
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_g:
                        self.show_grid = not self.show_grid
                    elif event.key == pygame.K_q:
                        return False
        return True
    
    def _simulate_detection(self):
        """Simulate object detection with random results."""
        if time.time() - self.last_detection_time >= self.detection_interval:
            self.last_detection_time = time.time()
            
            # 30% chance of a detection
            if random.random() < 0.3:
                detection_type = random.choice(['person', 'object', 'animal'])
                confidence = random.uniform(0.7, 0.99)
                
                self.current_detection = {
                    'type': detection_type,
                    'confidence': confidence,
                    'position': (
                        random.randint(50, self.SCREEN_WIDTH - 100),
                        random.randint(50, self.VIDEO_HEIGHT - 100)
                    ),
                    'size': (
                        random.randint(80, 150),
                        random.randint(80, 150)
                    )
                }
                
                # Update eye state based on detection
                self.eyes.set_mood(MoodState.HAPPY)
                
                if detection_type == 'person':
                    self.eyes.effects.current_scheme = ColorScheme.CYBER
                    self.status_text = "Person Detected!"
                    self.status_color = COLOR_SCHEMES[ColorScheme.CYBER]['primary']
                elif detection_type == 'object':
                    self.eyes.effects.current_scheme = ColorScheme.AMBER
                    self.status_text = "Object Detected!"
                    self.status_color = COLOR_SCHEMES[ColorScheme.AMBER]['primary']
                elif detection_type == 'animal':
                    self.eyes.effects.current_scheme = ColorScheme.ENERGY
                    self.status_text = "Animal Detected!"
                    self.status_color = COLOR_SCHEMES[ColorScheme.ENERGY]['primary']
            else:
                # No detection
                self.current_detection = None
                self._set_normal_state()
    
    def _draw_detection_overlay(self):
        """Draw detection overlay on the mock video frame."""
        if self.current_detection:
            detection = self.current_detection
            color = self.status_color
            
            # Draw detection box
            pygame.draw.rect(
                self.mock_frame, 
                color, 
                (
                    detection['position'][0], 
                    detection['position'][1],
                    detection['size'][0],
                    detection['size'][1]
                ),
                2  # Line thickness
            )
            
            # Draw label
            label = f"{detection['type']} ({detection['confidence']:.2f})"
            label_surface = pygame.font.Font(None, 24).render(
                label, 
                True, 
                color
            )
            self.mock_frame.blit(
                label_surface, 
                (
                    detection['position'][0],
                    detection['position'][1] - 20
                )
            )

    def update(self):
        """Update the state of the robot interface and animations."""
        current_time = pygame.time.get_ticks()
        
        # Handle blinking
        if current_time - self.last_blink > BLINK_INTERVAL:
            self.eyes.start_blink()
            self.last_blink = current_time + random.randint(-1000, 1000)
        
        # Update eyes animation
        self.eyes.update()

        # Handle detection in active state
        if not self.is_welcome_screen and self.is_running and not self.is_paused:
            self._simulate_detection()
            self._draw_detection_overlay()

    def draw_welcome_screen(self):
        """Draw the welcome screen with title and buttons."""
        # Draw welcome text
        welcome_text = "Robot Interface"
        text_surface = self.welcome_font.render(welcome_text, True, COLOR_SCHEMES[ColorScheme.NEON]['primary'])
        text_rect = text_surface.get_rect(center=(self.SCREEN_WIDTH // 2, self.EYES_HEIGHT + 150))
        self.screen.blit(text_surface, text_rect)

        # Draw buttons
        self.start_button.draw(self.screen)
        self.quit_button.draw(self.screen)

    def draw_main_screen(self):
        """Draw the main operation screen with status and video feed."""
        # Draw status text at the top of the eye area
        text_surface = self.font.render(self.status_text, True, self.status_color)
        text_rect = text_surface.get_rect(center=(self.SCREEN_WIDTH // 2, 50))
        self.screen.blit(text_surface, text_rect)
        
        # Draw mock video feed
        if self.mock_frame is not None:
            self.screen.blit(self.mock_frame, (0, self.EYES_HEIGHT))
        
        # Draw control buttons
        self.pause_button.draw(self.screen)
        self.quit_button.draw(self.screen)

    def draw(self):
        """Draw the complete robot interface."""
        self.screen.fill(BLACK)
        
        # Draw eyes with optional grid
        if self.show_grid:
            self.eyes._draw_grid(self.screen)
        self.eyes.draw(self.screen)
        
        # Draw the appropriate screen
        if self.is_welcome_screen:
            self.draw_welcome_screen()
        else:
            self.draw_main_screen()
        
        # Update the display
        pygame.display.flip()

    def run(self):
        """Run the main robot interface application loop."""
        running = True
        try:
            while running:
                running = self.process_events()
                self.update()
                self.draw()
                self.clock.tick(60)  # Maintain 60 FPS
        finally:
            pygame.quit()


def main():
    """Entry point function to start the robot interface."""
    app = RobotInterface()
    app.run()


if __name__ == "__main__":
    main()