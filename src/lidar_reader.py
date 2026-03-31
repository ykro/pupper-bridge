"""LiDAR scan reading and simple people detection for Mini Pupper 2.

Reads from the ldlidar_stl_ros2 package via ROS2 topic.
Falls back to mock data when ROS2 is not available.
"""

import logging
import math
import random
from dataclasses import dataclass, field

import numpy as np

try:
    import rclpy
    from sensor_msgs.msg import LaserScan

    _ROS_AVAILABLE = True
except ImportError:
    _ROS_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class ScanData:
    """Processed LiDAR scan data."""

    distances: list[float] = field(default_factory=list)
    angles: list[float] = field(default_factory=list)
    angle_min: float = 0.0
    angle_max: float = 2 * math.pi
    timestamp: float = 0.0


@dataclass
class PersonDetection:
    """A detected person from LiDAR clustering."""

    distance: float  # meters from robot
    angle: float  # radians
    x: float  # meters, relative to robot
    y: float  # meters, relative to robot


_latest_scan: ScanData | None = None


def update_scan(scan_data: ScanData) -> None:
    """Called by ROS controller when a new LiDAR scan arrives."""
    global _latest_scan
    _latest_scan = scan_data


def _generate_mock_scan() -> ScanData:
    """Generate a mock LiDAR scan with some simulated obstacles."""
    num_points = 360
    angles = [i * 2 * math.pi / num_points for i in range(num_points)]
    distances = []

    for i in range(num_points):
        base_dist = 3.0 + random.uniform(-0.1, 0.1)
        # Simulate a person-like cluster around 45 degrees
        if 40 <= i <= 50:
            base_dist = 1.2 + random.uniform(-0.05, 0.05)
        # Another cluster around 200 degrees
        if 195 <= i <= 210:
            base_dist = 2.0 + random.uniform(-0.05, 0.05)
        distances.append(base_dist)

    return ScanData(distances=distances, angles=angles)


def get_latest_scan() -> ScanData:
    """Return the latest LiDAR scan, or mock data if unavailable."""
    if _latest_scan is not None:
        return _latest_scan
    return _generate_mock_scan()


def detect_people(scan: ScanData | None = None) -> list[PersonDetection]:
    """Simple people detection from LiDAR scan data.

    Algorithm:
    1. Find points significantly closer than their neighbors (foreground clusters).
    2. Group consecutive close points into clusters.
    3. Filter clusters by size (person-sized: ~0.2-0.8m wide).
    4. Return center of each cluster as a person detection.
    """
    if scan is None:
        scan = get_latest_scan()

    if not scan.distances or not scan.angles:
        return []

    distances = np.array(scan.distances)
    angles = np.array(scan.angles)

    # Compute median distance as background reference
    median_dist = np.median(distances[distances > 0.1])

    # Find foreground points (significantly closer than background)
    foreground_threshold = median_dist * 0.6
    foreground_mask = (distances > 0.1) & (distances < foreground_threshold)

    if not np.any(foreground_mask):
        return []

    # Cluster consecutive foreground points
    clusters: list[list[int]] = []
    current_cluster: list[int] = []

    for i in range(len(foreground_mask)):
        if foreground_mask[i]:
            if current_cluster and (i - current_cluster[-1]) > 3:
                clusters.append(current_cluster)
                current_cluster = [i]
            else:
                current_cluster.append(i)
        else:
            if current_cluster:
                clusters.append(current_cluster)
                current_cluster = []

    if current_cluster:
        clusters.append(current_cluster)

    # Filter by cluster size and convert to detections
    people: list[PersonDetection] = []
    for cluster in clusters:
        if len(cluster) < 3 or len(cluster) > 40:
            continue

        cluster_dists = distances[cluster]
        cluster_angles = angles[cluster]

        mean_dist = float(np.mean(cluster_dists))
        mean_angle = float(np.mean(cluster_angles))

        # Check angular width corresponds to person-sized object (0.2-0.8m)
        angular_width = cluster_angles[-1] - cluster_angles[0]
        physical_width = angular_width * mean_dist
        if physical_width < 0.15 or physical_width > 1.0:
            continue

        x = mean_dist * math.cos(mean_angle)
        y = mean_dist * math.sin(mean_angle)

        people.append(
            PersonDetection(distance=mean_dist, angle=mean_angle, x=x, y=y)
        )

    return people
