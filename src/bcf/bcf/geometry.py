from typing import Optional

import numpy as np
from numpy.typing import NDArray


def camera_vectors_from_element_placement(
    elem_placement: NDArray[np.float64],
) -> tuple[list[float], list[float], list[float]]:
    """
    Calculate the vectors of a camera pointing to an element.

    Args:
        elem_placement: Placement matrix of an element.

    Returns:
        Camera position, direction and up vectors
    """
    target_position = elem_placement[:3, 3]
    return camera_vectors_from_target_position(target_position)


def camera_vectors_from_target_position(
    target_position: NDArray[np.float64], offset: Optional[NDArray[np.float64]] = None
) -> tuple[list[float], list[float], list[float]]:
    """
    Calculate the vectors of a camera pointing to a target point.

    Args:
        target_position: point the camera is pointing to.
        camera_offset: offset of the camera from the target point.

    Returns:
        Camera position, direction and up vectors
    """
    camera_offset = np.array((5, 5, 5)) if offset is None else offset
    camera_position = target_position + camera_offset
    camera_direction = unit_vector(-camera_offset)  # pylint: disable=invalid-unary-operand-type
    camera_right = unit_vector(np.cross(np.array([0.0, 0.0, 1.0]), camera_direction))
    camera_up = unit_vector(np.cross(camera_direction, camera_right))
    return camera_position.tolist(), camera_direction.tolist(), camera_up.tolist()


def unit_vector(v: NDArray[np.float64]) -> NDArray[np.float64]:
    """
    Return the unit vector of a vector.

    Args:
        v: vector

    Returns:
        unit vector.
    """
    norm = np.linalg.norm(v)
    return v if norm == 0 else v / norm
