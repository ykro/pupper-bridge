"""
Logging module for the Eyes Animation system.

This module provides specialized logging functionality for tracking
animation states, eye positions, and other relevant events during execution.
"""
import time
import os
from loguru import logger


class EyeLogger:
    """
    Custom logger for the Eyes Animation system.
    
    Provides sophisticated logging capabilities for tracking eye states,
    movement, and animation events with optimized output formats and
    filtering to reduce redundant log entries.
    """
    
    def __init__(self, log_file='eye_animation.log', log_level='INFO'):
        """
        Initialize logger with custom configuration.
        
        Args:
            log_file (str): Path to log file. Defaults to 'eye_animation.log'
            log_level (str): Logging level. Defaults to 'INFO'
        """
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)
        full_log_path = os.path.join('logs', log_file)
        
        # Configure logger
        self.logger = logger
        self.logger.remove()  # Remove default handler
        
        # Console output with minimal, clean format
        self.logger.add(
            sink=lambda msg: print(msg, end=''),
            format="<level>{time:HH:mm:ss} | {level} | {message}</level>",
            level=log_level,
            diagnose=False  # Disable detailed tracebacks
        )
        
        # File output with more detailed logging
        self.logger.add(
            sink=full_log_path, 
            rotation="1 MB",  # Rotate log file when it reaches 1 MB
            compression="zip",  # Compress rotated logs
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            level="DEBUG",
            diagnose=False
        )
        
        # Track start time
        self.start_time = time.time()
        
        # Tracking last logged state to reduce redundant logging
        self._last_logged_state = {}
        
        # Log initialization
        self.logger.info(f"Logging started at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
    def _should_log_state(self, state_details):
        """
        Determine if the current state is significantly different from the last logged state.
        
        Args:
            state_details (dict): Current state details
        
        Returns:
            bool: Whether the state should be logged
        """
        # Always log first entry
        if not self._last_logged_state:
            return True
        
        # Define thresholds for logging
        position_threshold = 10  # pixels
        size_threshold = 5  # pixels
        
        # Compare current state with last logged state
        state_changed = (
            abs(state_details.get('left_x', 0) - self._last_logged_state.get('left_x', 0)) > position_threshold or
            abs(state_details.get('right_x', 0) - self._last_logged_state.get('right_x', 0)) > position_threshold or
            abs(state_details.get('left_size', 0) - self._last_logged_state.get('left_size', 0)) > size_threshold or
            abs(state_details.get('right_size', 0) - self._last_logged_state.get('right_size', 0)) > size_threshold or
            state_details.get('mood') != self._last_logged_state.get('mood', None) or
            state_details.get('blinking') != self._last_logged_state.get('blinking', None)
        )
        
        return state_changed

    def log_eye_state(self, 
                    compass_location, 
                    eye_size, 
                    exact_location, 
                    mood, 
                    blinking_state):
        """
        Log comprehensive eye state with position metrics.
        
        Args:
            compass_location (str): Direction eyes are looking
            eye_size (tuple): Width and height of eyes
            exact_location (list): Coordinates of both eyes
            mood (str): Current mood state
            blinking_state (bool): Whether eyes are blinking
        """
        # Calculate eye centers
        left_eye_center = (
            exact_location[0][0] + eye_size[0] / 2, 
            exact_location[0][1] + eye_size[1] / 2
        )
        right_eye_center = (
            exact_location[1][0] + eye_size[0] / 2, 
            exact_location[1][1] + eye_size[1] / 2
        )
        
        # Screen center calculations
        screen_center_x = 400  # SCREEN_WIDTH / 2
        screen_center_y = 150  # SCREEN_HEIGHT / 4
        
        # Calculate distance from screen center
        left_x_offset = left_eye_center[0] - screen_center_x
        left_y_offset = left_eye_center[1] - screen_center_y
        right_x_offset = right_eye_center[0] - screen_center_x
        right_y_offset = right_eye_center[1] - screen_center_y
        
        # Prepare state details for logging decision
        state_details = {
            'left_x': exact_location[0][0],
            'right_x': exact_location[1][0],
            'left_size': eye_size[0],
            'right_size': eye_size[0],
            'mood': mood,
            'blinking': blinking_state,
            'left_offset_x': left_x_offset,
            'right_offset_x': right_x_offset
        }
        
        # Log only if state has changed significantly
        if self._should_log_state(state_details):
            # Create a detailed log message
            log_message = (
                f"Dir:{compass_location} | "
                f"Size:{eye_size[0]}x{eye_size[1]} | "
                f"Left: Pos:{exact_location[0]}, "
                f"Center:({left_eye_center[0]:.2f}, {left_eye_center[1]:.2f}), "
                f"Offset(x,y):({left_x_offset:.2f}, {left_y_offset:.2f}) | "
                f"Right: Pos:{exact_location[1]}, "
                f"Center:({right_eye_center[0]:.2f}, {right_eye_center[1]:.2f}), "
                f"Offset(x,y):({right_x_offset:.2f}, {right_y_offset:.2f}) | "
                f"Mood:{mood} | "
                f"Blink:{blinking_state}"
            )
            
            self.logger.info(log_message)
            
            # Update last logged state
            self._last_logged_state = state_details

    def log_event(self, event_type, details):
        """
        Log specific events in the animation.
        
        Args:
            event_type (str): Type of event
            details (str): Event details
        """
        elapsed_time = time.time() - self.start_time
        log_message = f"Event: {event_type} | {details}"
        self.logger.debug(log_message)

    def exception(self, error):
        """
        Log exceptions with traceback.
        
        Args:
            error (Exception): Exception to log
        """
        self.logger.exception(error)