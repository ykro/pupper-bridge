"""Eye renderer — wraps sidikalamini/eyes-animation for the ST7789 LCD.

Runs Pygame in a background thread. Renders to an off-screen Pygame surface,
converts to PIL Image, and sends to the ST7789 LCD via MangDang.LCD.ST7789
(SPI, no framebuffer needed).

In mock mode it logs mood changes without requiring Pygame or LCD hardware.
"""

import logging
import queue
import sys
import threading
import time

logger = logging.getLogger(__name__)

# ST7789 LCD on Mini Pupper 2
LCD_WIDTH = 320
LCD_HEIGHT = 240
TARGET_FPS = 30
BLINK_INTERVAL = 4.0  # seconds between automatic blinks

# Map 6 sentiment moods to eyes-animation MoodState + ColorScheme.
MOOD_MAP = {
    "happy": {"mood": "HAPPY", "color": "ENERGY"},
    "sad": {"mood": "NORMAL", "color": "ICE"},
    "angry": {"mood": "CONFUSED", "color": "BLOOD"},
    "surprised": {"mood": "SURPRISED", "color": "NEON"},
    "neutral": {"mood": "NORMAL", "color": "CYBER"},
    "curious": {"mood": "CONFUSED", "color": "AMBER"},
}


def _add_eyes_to_path():
    """Add the vendored eyes-animation library to sys.path."""
    import pathlib
    vendor_dir = pathlib.Path(__file__).parent.parent / "vendor" / "eyes-animation" / "src"
    if str(vendor_dir) not in sys.path:
        sys.path.insert(0, str(vendor_dir))


def _add_bsp_to_path():
    """Add Mini Pupper BSP packages to sys.path (installed in system Python)."""
    bsp_dir = "/usr/local/lib/python3.10/dist-packages"
    if bsp_dir not in sys.path:
        sys.path.insert(0, bsp_dir)


class EyeRenderer:
    """Manages the Pygame eye animation loop in a dedicated thread."""

    def __init__(self, mock: bool = False):
        self._mock = mock
        self._mood_queue: queue.Queue[str] = queue.Queue()
        self._thread: threading.Thread | None = None
        self._running = False
        self._current_mood = "neutral"

    def start(self) -> None:
        """Start the eye rendering in a background thread."""
        if self._mock:
            logger.info("EyeRenderer started in mock mode (no Pygame/LCD)")
            self._running = True
            return

        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info("EyeRenderer thread started")

    def stop(self) -> None:
        """Signal the rendering loop to stop."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=3.0)
            logger.info("EyeRenderer thread stopped")

    def set_mood(self, mood: str) -> None:
        """Thread-safe mood change. Called from the asyncio loop."""
        if self._mock:
            if mood != self._current_mood:
                self._current_mood = mood
                logger.info("MOCK eyes mood: %s", mood)
            return

        self._mood_queue.put(mood)
        logger.info("Mood queued: %s", mood)

    def _create_lcd(self):
        """Create the ST7789 LCD driver (only on real hardware)."""
        _add_bsp_to_path()
        try:
            from MangDang.LCD.ST7789 import ST7789
            lcd = ST7789()
            logger.info("ST7789 LCD initialized")
            return lcd
        except ImportError:
            logger.error(
                "MangDang.LCD.ST7789 not found — is the Mini Pupper BSP installed?"
            )
            raise
        except Exception as exc:
            logger.error("Failed to init ST7789: %s", exc)
            raise

    def _surface_to_pil(self, surface):
        """Convert a Pygame surface to a PIL Image for the LCD."""
        import pygame
        from PIL import Image

        raw = pygame.image.tobytes(surface, "RGB")
        return Image.frombytes("RGB", (LCD_WIDTH, LCD_HEIGHT), raw)

    def _run(self) -> None:
        """Pygame main loop — runs in its own thread."""
        _add_eyes_to_path()

        import os
        # No X11 on the Pi — use dummy video driver for off-screen rendering.
        if not self._mock:
            os.environ["SDL_VIDEODRIVER"] = "dummy"

        import pygame
        from eyes.animation import Eyes
        from eyes.config import ColorScheme, MoodState

        pygame.init()

        # Off-screen rendering — no display window needed.
        screen = pygame.Surface((LCD_WIDTH, LCD_HEIGHT))
        lcd = self._create_lcd()

        clock = pygame.time.Clock()

        eyes = Eyes(screen_width=LCD_WIDTH, screen_height=LCD_HEIGHT)
        # Shrink eyes to fit the 320x240 display.
        target_eye_size = 80
        eyes.adjust_size(target_eye_size - eyes.EYE_WIDTH)

        current_mood = None  # Don't render until first mood arrives.
        last_blink = time.monotonic()
        last_mood_refresh = time.monotonic()

        logger.info("Pygame initialized, waiting for first mood")

        while self._running:
            # Check for mood changes from the async side.
            try:
                while True:
                    new_mood = self._mood_queue.get_nowait()
                    current_mood = new_mood
            except queue.Empty:
                pass

            # Wait for first mood before rendering anything.
            if current_mood is None:
                # Show black screen while idle.
                screen.fill((0, 0, 0))
                if lcd is not None:
                    lcd.display(self._surface_to_pil(screen))
                clock.tick(TARGET_FPS)
                continue

            # Apply mood + color scheme.
            mapping = MOOD_MAP.get(current_mood, MOOD_MAP["neutral"])
            mood_enum = getattr(MoodState, mapping["mood"], MoodState.NORMAL)
            color_enum = getattr(
                ColorScheme, mapping["color"], ColorScheme.CYBER
            )
            eyes.set_mood(mood_enum)
            eyes.effects.current_scheme = color_enum

            # Re-send mood every 1.5s to prevent auto-decay (library decays
            # non-normal moods back to NORMAL after 2s).
            now = time.monotonic()
            if now - last_mood_refresh > 1.5:
                eyes.set_mood(mood_enum)
                last_mood_refresh = now

            # Automatic blinking.
            if now - last_blink > BLINK_INTERVAL:
                eyes.start_blink()
                last_blink = now

            # Update + draw.
            eyes.update()
            screen.fill((0, 0, 0))
            eyes.draw(screen)

            if lcd is not None:
                # Send frame to the ST7789 LCD via SPI.
                pil_image = self._surface_to_pil(screen)
                lcd.display(pil_image)

            clock.tick(TARGET_FPS)

        pygame.quit()
        logger.info("Pygame shut down")
