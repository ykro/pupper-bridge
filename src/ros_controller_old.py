"""ROS2 controller for Mini Pupper 2.

Wraps all ROS2 interactions: publishing Twist messages, setting poses,
subscribing to camera/LiDAR topics, and interfacing with Nav2.

All rclpy imports are wrapped in try/except so the server can run
in mock mode on machines without ROS2.
"""

import asyncio
import logging
import math
import time
from dataclasses import dataclass

from src.camera_capture import update_ros_frame
from src.lidar_reader import ScanData, update_scan
from src.poses import POSES, PoseDefinition

try:
    import rclpy
    from rclpy.node import Node
    from geometry_msgs.msg import Twist, PoseStamped
    from sensor_msgs.msg import LaserScan, CompressedImage, JointState
    from std_msgs.msg import String
    from nav2_msgs.action import NavigateToPose
    from rclpy.action import ActionClient

    _ROS_AVAILABLE = True
except ImportError:
    _ROS_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class NavState:
    """Current navigation state."""

    state: str = "idle"  # idle | navigating | arrived | stuck
    goal_x: float = 0.0
    goal_y: float = 0.0
    goal_theta: float = 0.0


class MockRosController:
    """Mock controller for development/testing without ROS2."""

    def __init__(self) -> None:
        self.current_pose: str = "stand"
        self.tracking_active: bool = False
        self.nav_state = NavState()
        self._active_tasks: list[asyncio.Task] = []
        logger.info("ROS2 not available — running in mock mode")

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
        """Simulate velocity command with duration."""
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
        logger.info("MOCK dance started: %s", style)
        await asyncio.sleep(3.0)
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
            "ros_available": False,
        }

    def get_nav_status(self) -> dict:
        """Return mock navigation status."""
        return {
            "state": self.nav_state.state,
            "goal_x": self.nav_state.goal_x,
            "goal_y": self.nav_state.goal_y,
            "goal_theta": self.nav_state.goal_theta,
        }


class RosController:
    """Real ROS2 controller for Mini Pupper 2."""

    def __init__(self) -> None:
        self.current_pose: str = "stand"
        self.tracking_active: bool = False
        self.nav_state = NavState()
        self._node: "Node | None" = None
        self._cmd_vel_pub = None
        self._joint_pub = None
        self._nav_client = None
        self._active_tasks: list[asyncio.Task] = []

    async def initialize(self) -> None:
        """Initialize the ROS2 node and publishers/subscribers."""
        if not _ROS_AVAILABLE:
            return

        rclpy.init()
        self._node = rclpy.create_node("pupper_bridge")

        # Publishers
        self._cmd_vel_pub = self._node.create_publisher(Twist, "/cmd_vel", 10)
        self._joint_pub = self._node.create_publisher(JointState, "/joint_states_cmd", 10)

        # Subscribers
        self._node.create_subscription(
            CompressedImage, "/camera/image_raw/compressed", self._camera_callback, 10
        )
        self._node.create_subscription(
            LaserScan, "/scan", self._lidar_callback, 10
        )

        # Nav2 action client
        self._nav_client = ActionClient(self._node, NavigateToPose, "navigate_to_pose")

        logger.info("ROS2 node initialized")

    async def shutdown(self) -> None:
        """Shut down the ROS2 node."""
        for task in self._active_tasks:
            task.cancel()
        self._active_tasks.clear()

        if self._node is not None:
            self._node.destroy_node()
        if _ROS_AVAILABLE:
            rclpy.shutdown()

    def _camera_callback(self, msg: "CompressedImage") -> None:
        """Handle incoming camera frames."""
        update_ros_frame(bytes(msg.data))

    def _lidar_callback(self, msg: "LaserScan") -> None:
        """Handle incoming LiDAR scans."""
        angles = [
            msg.angle_min + i * msg.angle_increment
            for i in range(len(msg.ranges))
        ]
        scan = ScanData(
            distances=list(msg.ranges),
            angles=angles,
            angle_min=msg.angle_min,
            angle_max=msg.angle_max,
            timestamp=time.time(),
        )
        update_scan(scan)

    async def send_cmd_vel(
        self, linear_x: float, linear_y: float, angular_z: float, duration: float
    ) -> None:
        """Publish a Twist message, optionally for a set duration."""
        if self._cmd_vel_pub is None:
            return

        twist = Twist()
        twist.linear.x = linear_x
        twist.linear.y = linear_y
        twist.angular.z = angular_z
        self._cmd_vel_pub.publish(twist)

        if duration > 0:
            await asyncio.sleep(duration)
            await self.send_zero_twist()

    async def send_zero_twist(self) -> None:
        """Publish a zero Twist to stop motion."""
        if self._cmd_vel_pub is None:
            return
        twist = Twist()
        self._cmd_vel_pub.publish(twist)

    async def set_pose(self, pose_name: str) -> bool:
        """Set robot pose by publishing joint positions."""
        if pose_name not in POSES:
            return False

        pose_def = POSES[pose_name]
        self.current_pose = pose_name

        if self._joint_pub is None:
            return True

        msg = JointState()
        joint_names = []
        positions = []

        for leg_name in ("FL", "FR", "BL", "BR"):
            leg = pose_def[leg_name]
            joint_names.extend([
                f"{leg_name}_shoulder",
                f"{leg_name}_elbow",
                f"{leg_name}_wrist",
            ])
            positions.extend([
                leg["shoulder"],
                leg["elbow"],
                leg["wrist"],
            ])

        msg.name = joint_names
        msg.position = positions
        self._joint_pub.publish(msg)
        logger.info("Pose set: %s", pose_name)
        return True

    async def start_dance(self, style: str) -> None:
        """Execute a dance by cycling through poses."""
        sequences = {
            "default": ["stand", "sit", "stand", "greet", "stand"],
            "wiggle": ["stand", "excited", "stand", "excited", "stand"],
            "spin": ["stand", "greet", "stand", "greet", "stand"],
        }
        seq = sequences.get(style, sequences["default"])

        for pose_name in seq:
            await self.set_pose(pose_name)
            await asyncio.sleep(0.8)

            # For spin style, also rotate
            if style == "spin":
                await self.send_cmd_vel(0.0, 0.0, 2.0, 0.5)

        await self.set_pose("stand")

    async def stop_all(self) -> None:
        """Stop all active motions."""
        for task in self._active_tasks:
            task.cancel()
        self._active_tasks.clear()
        await self.send_zero_twist()
        await self.set_pose("stand")

    async def start_tracking(self) -> None:
        """Enable YOLO11 person tracking."""
        self.tracking_active = True
        logger.info("Person tracking enabled")

    async def stop_tracking(self) -> None:
        """Disable person tracking."""
        self.tracking_active = False
        logger.info("Person tracking disabled")

    async def navigate_to(self, x: float, y: float, theta: float) -> None:
        """Send a Nav2 navigation goal."""
        self.nav_state = NavState(state="navigating", goal_x=x, goal_y=y, goal_theta=theta)

        if self._nav_client is None:
            # Simulate if Nav2 not available
            await asyncio.sleep(5.0)
            self.nav_state.state = "arrived"
            return

        goal = NavigateToPose.Goal()
        goal.pose = PoseStamped()
        goal.pose.header.frame_id = "map"
        goal.pose.pose.position.x = x
        goal.pose.pose.position.y = y
        goal.pose.pose.orientation.z = math.sin(theta / 2)
        goal.pose.pose.orientation.w = math.cos(theta / 2)

        self._nav_client.wait_for_server(timeout_sec=5.0)
        result = await asyncio.get_event_loop().run_in_executor(
            None, lambda: self._nav_client.send_goal(goal)
        )
        self.nav_state.state = "arrived"

    async def cancel_navigation(self) -> None:
        """Cancel current navigation goal."""
        if self._nav_client is not None:
            self._nav_client.cancel_all_goals()
        self.nav_state.state = "idle"

    def get_status(self) -> dict:
        """Return current robot status."""
        active_nodes = []
        if self._node is not None:
            try:
                active_nodes = self._node.get_node_names()
            except Exception:
                active_nodes = ["pupper_bridge"]

        return {
            "battery": -1.0,  # TODO: read from hardware
            "pose": self.current_pose,
            "active_nodes": active_nodes,
            "ros_available": True,
        }

    def get_nav_status(self) -> dict:
        """Return current navigation status."""
        return {
            "state": self.nav_state.state,
            "goal_x": self.nav_state.goal_x,
            "goal_y": self.nav_state.goal_y,
            "goal_theta": self.nav_state.goal_theta,
        }


def create_controller() -> MockRosController | "RosController":
    """Factory: return real controller if ROS2 available, else mock."""
    if _ROS_AVAILABLE:
        return RosController()
    return MockRosController()
