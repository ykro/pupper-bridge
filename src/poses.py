"""Pose definitions for Mini Pupper 2.

Joint angles as 3x4 numpy arrays (radians).
Row 0 = abduction, Row 1 = hip, Row 2 = knee.
Columns = legs 0-3 (FL, FR, BL, BR).
"""

import numpy as np

POSES = {
    "stand": np.array([
        [0.0, 0.0, 0.0, 0.0],
        [0.88, 0.88, 0.88, 0.88],
        [-0.70, -0.70, -0.70, -0.70],
    ]),
    "sit": np.array([
        [0.0, 0.0, 0.0, 0.0],
        [0.5, 0.5, 1.2, 1.2],
        [-0.3, -0.3, -1.4, -1.4],
    ]),
    "greet": np.array([
        [0.0, 0.0, 0.0, 0.0],
        [1.5, 0.88, 0.88, 0.88],
        [0.0, -0.70, -0.70, -0.70],
    ]),
    "excited": np.array([
        [0.15, -0.15, 0.15, -0.15],
        [1.0, 1.0, 1.0, 1.0],
        [-0.5, -0.5, -0.5, -0.5],
    ]),
    "sad": np.array([
        [0.0, 0.0, 0.0, 0.0],
        [0.4, 0.4, 0.4, 0.4],
        [-0.2, -0.2, -0.2, -0.2],
    ]),
}
