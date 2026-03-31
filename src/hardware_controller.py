"""Hardware controller for Mini Pupper 2.

Uses MangDang HardwareInterface for direct servo control (no ROS2).
Falls back to MockHardwareController when hardware is unavailable.
"""

import asyncio
import logging
from dataclasses import dataclass

from src.poses import POSES

logger = logging.getLogger(__name__)

DANCES = {
    "default": [("stand", 0.6), ("sit", 0.6), ("stand", 0.6), ("greet", 0.6), ("stand", 0.6)],
    "wiggle": [("stand", 0.4), ("excited", 0.4), ("stand", 0.4), ("excited", 0.4), ("stand", 0.4)],
}


@dataclass
class NavState:
    """Current navigation state."""

    state: str = "idle"  # idle | navigating | arrived | stuck
    goal_x: float = 0.0
    goal_y: float = 0.0
    goal_theta: float = 0.0


class HardwareController:
    """Real controller using MangDang HardwareInterface for direct servo control."""

    def __init__(self) -> None:
        self.current_pose: str = "stand"
        self.tracking_active: bool = False
        self.nav_state = NavState()
        self._hw = None
        self._busy = False
        self._active_tasks: list[asyncio.Task] = []

    async def initialize(self) -> None:
        """Initialize the HardwareInterface and set stand pose."""
        try:
            from MangDang.mini_pupper.HardwareInterface import HardwareInterface
            self._hw = HardwareInterface()
            self._hw.set_actuator_postions(POSES["stand"])
            logger.info("HardwareInterface initialized")
        except ImportError:
            logger.warning("MangDang HardwareInterface not available — servos disabled")
        except Exception as exc:
            logger.warning("HardwareInterface init failed: %s", exc)

    async def shutdown(self) -> None:
        """Cancel active tasks and return to stand pose."""
        for task in self._active_tasks:
            task.cancel()
        self._active_tasks.clear()
        if self._hw is not None:
            self._hw.set_actuator_postions(POSES["stand"])

    async def send_cmd_vel(
        self, linear_x: float, linear_y: float, angular_z: float, duration: float
    ) -> None:
        """Velocity commands not supported with direct hardware — log and ignore."""
        logger.info(
            "cmd_vel not supported in hardware mode: lx=%.2f ly=%.2f az=%.2f dur=%.1f",
            linear_x, linear_y, angular_z, duration,
        )
        if duration > 0:
            await asyncio.sleep(duration)

    async def send_zero_twist(self) -> None:
        """No-op — velocity commands not used in hardware mode."""
        pass

    async def set_pose(self, pose_name: str) -> bool:
        """Set robot to a predefined pose via HardwareInterface."""
        if pose_name not in POSES:
            return False
        self.current_pose = pose_name
        if self._hw is not None:
            self._hw.set_actuator_postions(POSES[pose_name])
        logger.info("Pose set: %s", pose_name)
        return True

    async def start_dance(self, style: str) -> None:
        """Execute a dance sequence by cycling through poses."""
        sequence = DANCES.get(style)
        if not sequence:
            logger.warning("Unknown dance style: %s", style)
            return

        task = asyncio.current_task()
        if task:
            self._active_tasks.append(task)
        self._busy = True
        try:
            for pose_name, duration in sequence:
                await self.set_pose(pose_name)
                await asyncio.sleep(duration)
        finally:
            self._busy = False
            if task and task in self._active_tasks:
                self._active_tasks.remove(task)

    async def stop_all(self) -> None:
        """Stop all active motions and return to stand."""
        for task in self._active_tasks:
            task.cancel()
        self._active_tasks.clear()
        await self.set_pose("stand")

    async def start_tracking(self) -> None:
        """Enable person tracking (placeholder)."""
        self.tracking_active = True
        logger.info("Person tracking enabled")

    async def stop_tracking(self) -> None:
        """Disable person tracking."""
        self.tracking_active = False
        logger.info("Person tracking disabled")

    async def navigate_to(self, x: float, y: float, theta: float) -> None:
        """Navigation not supported without ROS2 Nav2 — simulate."""
        self.nav_state = NavState(state="navigating", goal_x=x, goal_y=y, goal_theta=theta)
        logger.info("Nav goal (simulated): x=%.2f y=%.2f theta=%.2f", x, y, theta)
        await asyncio.sleep(5.0)
        self.nav_state.state = "arrived"

    async def cancel_navigation(self) -> None:
        """Cancel navigation."""
        self.nav_state.state = "idle"
        logger.info("Navigation cancelled")

    def get_status(self) -> dict:
        """Return current robot status."""
        return {
            "battery": -1.0,
            "pose": self.current_pose,
            "active_nodes": ["hardware_controller"],
            "hardware_available": self._hw is not None,
        }

    def get_nav_status(self) -> dict:
        """Return current navigation status."""
        return {
            "state": self.nav_state.state,
            "goal_x": self.nav_state.goal_x,
            "goal_y": self.nav_state.goal_y,
            "goal_theta": self.nav_state.goal_theta,
        }


class MockHardwareController:
    """Mock controller for development/testing without hardware."""

    def __init__(self) -> None:
        self.current_pose: str = "stand"
        self.tracking_active: bool = False
        self.nav_state = NavState()
        self._active_tasks: list[asyncio.Task] = []
        logger.info("Hardware not available — running in mock mode")

    async def initialize(self) -> None:
        """No-op initialization for mock mode."""
        pass

    async def shutdown(self) -> None:
        """Cancel any active tasks."""
        for task in self._active_tasks:
            task.cancel()
        self._active_tasks.clear()

    async def send_cmd_vel(
        self, linear_x: float, linear_y: float, angular_z: float, duration: float
    ) -> None:
        """Simulate velocity command."""
        logger.info(
            "MOCK cmd_vel: lx=%.2f ly=%.2f az=%.2f dur=%.1f",
            linear_x, linear_y, angular_z, duration,
        )
        if duration > 0:
            await asyncio.sleep(duration)
            logger.info("MOCK cmd_vel: stopped after duration")

    async def send_zero_twist(self) -> None:
        """Simulate stop command."""
        logger.info("MOCK: zero twist sent")

    async def set_pose(self, pose_name: str) -> bool:
        """Simulate setting a pose."""
        if pose_name not in POSES:
            return False
        self.current_pose = pose_name
        logger.info("MOCK pose set: %s", pose_name)
        return True

    async def start_dance(self, style: str) -> None:
        """Simulate a dance sequence."""
        sequence = DANCES.get(style, DANCES["default"])
        logger.info("MOCK dance started: %s", style)
        for pose_name, duration in sequence:
            logger.info("MOCK dance pose: %s", pose_name)
            await asyncio.sleep(duration)
        logger.info("MOCK dance finished: %s", style)

    async def stop_all(self) -> None:
        """Stop all mock motions."""
        await self.shutdown()
        await self.send_zero_twist()
        logger.info("MOCK: all motions stopped")

    async def start_tracking(self) -> None:
        """Enable mock person tracking."""
        self.tracking_active = True
        logger.info("MOCK: person tracking enabled")

    async def stop_tracking(self) -> None:
        """Disable mock person tracking."""
        self.tracking_active = False
        logger.info("MOCK: person tracking disabled")

    async def navigate_to(self, x: float, y: float, theta: float) -> None:
        """Simulate navigation goal."""
        self.nav_state = NavState(state="navigating", goal_x=x, goal_y=y, goal_theta=theta)
        logger.info("MOCK nav goal: x=%.2f y=%.2f theta=%.2f", x, y, theta)
        await asyncio.sleep(5.0)
        self.nav_state.state = "arrived"
        logger.info("MOCK nav: arrived")

    async def cancel_navigation(self) -> None:
        """Cancel mock navigation."""
        self.nav_state.state = "idle"
        logger.info("MOCK nav: cancelled")

    def get_status(self) -> dict:
        """Return mock robot status."""
        return {
            "battery": 85.0,
            "pose": self.current_pose,
            "active_nodes": ["mock_controller"],
            "hardware_available": False,
        }

    def get_nav_status(self) -> dict:
        """Return mock navigation status."""
        return {
            "state": self.nav_state.state,
            "goal_x": self.nav_state.goal_x,
            "goal_y": self.nav_state.goal_y,
            "goal_theta": self.nav_state.goal_theta,
        }


def create_controller() -> HardwareController | MockHardwareController:
    """Factory: return real controller if HardwareInterface importable, else mock."""
    try:
        from MangDang.mini_pupper.HardwareInterface import HardwareInterface
        return HardwareController()
    except ImportError:
        return MockHardwareController()
