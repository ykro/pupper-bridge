"""FastAPI bridge server for Mini Pupper 2.

Runs on the Raspberry Pi and translates HTTP requests into direct servo
commands via MangDang HardwareInterface, and renders eye expressions on
the ST7789 LCD.
Port: 9090
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from enum import Enum

from fastapi import BackgroundTasks, FastAPI, Response
from pydantic import BaseModel, Field

from src.camera_capture import capture_frame
from src.eye_renderer import EyeRenderer
from src.hardware_controller import MockHardwareController, create_controller
from src.lidar_reader import detect_people, get_latest_scan

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

controller = create_controller()
_is_mock = isinstance(controller, MockHardwareController)
eye_renderer: EyeRenderer | None = None

# Mood -> body action mapping (from pupper-sentiment).
MOOD_ACTIONS = {
    "happy": {"pose": "excited", "dance": "wiggle"},
    "sad": {"pose": "sad"},
    "angry": {"pose": "stand"},
    "surprised": {"pose": "greet", "dance": "default"},
    "neutral": {"pose": "stand"},
    "curious": {"pose": "greet"},
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and shut down the controller and eye renderer with the app."""
    global eye_renderer
    await controller.initialize()
    yield
    if eye_renderer is not None:
        eye_renderer.stop()
    await controller.shutdown()


app = FastAPI(
    title="Mini Pupper 2 Bridge",
    description="HTTP bridge for Mini Pupper 2 — direct servo control + LCD eyes",
    version="0.2.0",
    lifespan=lifespan,
)


# --- Request/Response models ---


class CmdVelRequest(BaseModel):
    linear_x: float = Field(default=0.0, description="Forward/backward velocity (m/s)")
    linear_y: float = Field(default=0.0, description="Left/right velocity (m/s)")
    angular_z: float = Field(default=0.0, description="Rotation velocity (rad/s)")
    duration: float = Field(default=0.0, ge=0, description="Duration in seconds (0 = single publish)")


class PoseName(str, Enum):
    sit = "sit"
    stand = "stand"
    greet = "greet"
    excited = "excited"
    sad = "sad"


class PoseRequest(BaseModel):
    pose: PoseName


class DanceStyle(str, Enum):
    default = "default"
    wiggle = "wiggle"


class DanceRequest(BaseModel):
    style: DanceStyle = DanceStyle.default


class MoodRequest(BaseModel):
    mood: str = Field(description="Mood name: happy, sad, angry, surprised, neutral, curious")


class NavGoalRequest(BaseModel):
    x: float = Field(description="Target X position in map frame (meters)")
    y: float = Field(description="Target Y position in map frame (meters)")
    theta: float = Field(default=0.0, description="Target orientation (radians)")


# --- Endpoints ---


@app.post("/cmd_vel")
async def cmd_vel(req: CmdVelRequest, background_tasks: BackgroundTasks):
    """Send velocity command. If duration > 0, runs in background and auto-stops."""
    if req.duration > 0:
        background_tasks.add_task(
            controller.send_cmd_vel, req.linear_x, req.linear_y, req.angular_z, req.duration
        )
        return {"status": "started", "duration": req.duration}

    await controller.send_cmd_vel(req.linear_x, req.linear_y, req.angular_z, 0)
    return {"status": "sent"}


@app.post("/pose")
async def set_pose(req: PoseRequest):
    """Set robot to a predefined pose."""
    success = await controller.set_pose(req.pose.value)
    if not success:
        return {"status": "error", "message": f"Unknown pose: {req.pose}"}
    return {"status": "ok", "pose": req.pose.value}


@app.post("/dance")
async def dance(req: DanceRequest, background_tasks: BackgroundTasks):
    """Start a dance sequence in the background."""
    background_tasks.add_task(controller.start_dance, req.style.value)
    return {"status": "started", "style": req.style.value}


@app.post("/stop")
async def stop():
    """Emergency stop: zero twist and cancel all active motions."""
    await controller.stop_all()
    return {"status": "stopped"}


def _ensure_eyes() -> EyeRenderer:
    """Lazy-init the EyeRenderer on first use."""
    global eye_renderer
    if eye_renderer is None:
        eye_renderer = EyeRenderer(mock=_is_mock)
        eye_renderer.start()
    return eye_renderer


@app.post("/eyes")
async def set_eyes(req: MoodRequest):
    """Update LCD eye expression based on mood."""
    _ensure_eyes().set_mood(req.mood)
    return {"status": "ok", "mood": req.mood}


@app.post("/react")
async def react(req: MoodRequest, background_tasks: BackgroundTasks):
    """Combined reaction: eyes + pose + dance for a given mood."""
    # Update eyes on first /react call (lazy init).
    _ensure_eyes().set_mood(req.mood)

    # Look up body action.
    action = MOOD_ACTIONS.get(req.mood, {"pose": "stand"})
    pose = action.get("pose", "stand")
    dance_style = action.get("dance")

    # Set pose.
    await controller.set_pose(pose)

    # Start dance in background if specified.
    if dance_style:
        background_tasks.add_task(controller.start_dance, dance_style)

    return {
        "status": "ok",
        "mood": req.mood,
        "pose": pose,
        "dance": dance_style,
    }


@app.get("/camera/frame")
async def camera_frame():
    """Capture and return a JPEG frame from the camera."""
    frame_bytes = await capture_frame()
    return Response(content=frame_bytes, media_type="image/jpeg")


@app.get("/lidar/scan")
async def lidar_scan():
    """Return the latest LiDAR scan data."""
    scan = get_latest_scan()
    return {
        "distances": scan.distances,
        "angles": scan.angles,
        "angle_min": scan.angle_min,
        "angle_max": scan.angle_max,
        "num_points": len(scan.distances),
    }


@app.get("/lidar/people")
async def lidar_people():
    """Detect and return nearby people from LiDAR data."""
    people = detect_people()
    return {
        "count": len(people),
        "people": [
            {
                "distance": p.distance,
                "angle": p.angle,
                "x": p.x,
                "y": p.y,
            }
            for p in people
        ],
    }


@app.get("/status")
async def status():
    """Return current robot status."""
    return controller.get_status()


@app.post("/tracking/start")
async def tracking_start():
    """Enable YOLO11 person tracking."""
    await controller.start_tracking()
    return {"status": "tracking_enabled"}


@app.post("/tracking/stop")
async def tracking_stop():
    """Disable person tracking."""
    await controller.stop_tracking()
    return {"status": "tracking_disabled"}


@app.post("/nav/goto")
async def nav_goto(req: NavGoalRequest, background_tasks: BackgroundTasks):
    """Send a navigation goal."""
    background_tasks.add_task(controller.navigate_to, req.x, req.y, req.theta)
    return {"status": "navigating", "goal": {"x": req.x, "y": req.y, "theta": req.theta}}


@app.get("/nav/status")
async def nav_status():
    """Return current navigation status."""
    return controller.get_nav_status()


@app.post("/nav/cancel")
async def nav_cancel():
    """Cancel the current navigation goal."""
    await controller.cancel_navigation()
    return {"status": "cancelled"}
