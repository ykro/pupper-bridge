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

# Lazy OpenCV capture handle (primary source — direct Pi camera access).
_cv_cap = None
_cv_tried = False


def _get_cv_cap():
    """Lazy-open /dev/video0 via OpenCV. Returns None if unavailable."""
    global _cv_cap, _cv_tried
    if _cv_tried:
        return _cv_cap
    _cv_tried = True
    try:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            logger.info("OpenCV camera opened (device 0)")
            _cv_cap = cap
        else:
            logger.info("OpenCV device 0 not openable — falling back")
    except Exception as exc:
        logger.warning("OpenCV camera init failed: %s", exc)
    return _cv_cap


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
    # Primary: direct OpenCV access to /dev/video0 (Pi camera).
    cap = _get_cv_cap()
    if cap is not None:
        ret, frame = cap.read()
        if ret:
            frame = cv2.resize(frame, (640, 480))
            ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            if ok:
                return buf.tobytes()
        logger.warning("OpenCV read failed, trying fallbacks")

    # Fallback: web interface stream (ROS camera HTTP snapshot).
    if _HTTPX_AVAILABLE:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.get("http://localhost:8080/snapshot?topic=/camera/image_raw")
                if resp.status_code == 200:
                    return resp.content
        except Exception:
            logger.debug("Web interface camera unavailable, trying alternatives")

    # Fallback: ROS2 topic (if rclpy running).
    if _ROS_AVAILABLE and _latest_ros_frame is not None:
        return _latest_ros_frame

    # Last resort: mock frame.
    logger.debug("Using mock camera frame")
    return _generate_mock_frame()


def update_ros_frame(frame_data: bytes) -> None:
    """Called by ROS controller when a new camera frame arrives."""
    global _latest_ros_frame
    _latest_ros_frame = frame_data
