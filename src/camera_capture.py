"""Camera frame capture for Mini Pupper 2.

Attempts to grab JPEG frames from:
1. The Pi's built-in web interface at http://localhost:8080
2. ROS2 camera topic (if rclpy available)
3. Mock frame generator (fallback for testing)
"""

import logging
from io import BytesIO

import cv2
import numpy as np

try:
    import httpx

    _HTTPX_AVAILABLE = True
except ImportError:
    _HTTPX_AVAILABLE = False

try:
    import rclpy
    from sensor_msgs.msg import CompressedImage

    _ROS_AVAILABLE = True
except ImportError:
    _ROS_AVAILABLE = False

logger = logging.getLogger(__name__)

_WEB_URL = "http://localhost:8080/stream?topic=/camera/image_raw&type=ros_compressed"
_latest_ros_frame: bytes | None = None


def _generate_mock_frame() -> bytes:
    """Generate a mock JPEG frame with a colored rectangle and text."""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frame[:] = (40, 40, 40)
    cv2.rectangle(frame, (100, 100), (540, 380), (0, 200, 0), 2)
    cv2.putText(
        frame,
        "MOCK CAMERA",
        (180, 250),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        (0, 200, 0),
        2,
    )
    cv2.putText(
        frame,
        "No camera available",
        (175, 300),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (150, 150, 150),
        1,
    )
    _, buf = cv2.imencode(".jpg", frame)
    return buf.tobytes()


async def capture_frame() -> bytes:
    """Capture a single JPEG frame from the best available source."""
    # Try the web interface first
    if _HTTPX_AVAILABLE:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.get("http://localhost:8080/snapshot?topic=/camera/image_raw")
                if resp.status_code == 200:
                    return resp.content
        except Exception:
            logger.debug("Web interface camera unavailable, trying alternatives")

    # Try ROS2 topic
    if _ROS_AVAILABLE and _latest_ros_frame is not None:
        return _latest_ros_frame

    # Fallback to mock
    logger.debug("Using mock camera frame")
    return _generate_mock_frame()


def update_ros_frame(frame_data: bytes) -> None:
    """Called by ROS controller when a new camera frame arrives."""
    global _latest_ros_frame
    _latest_ros_frame = frame_data
