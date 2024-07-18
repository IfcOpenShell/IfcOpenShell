from typing import Optional

import numpy as np
from numpy.typing import NDArray


def camera_vectors_from_element_placement(
    elem_placement: NDArray[np.float_],
) -> tuple[NDArray[np.float_], NDArray[np.float_], NDArray[np.float_]]:
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
    target_position: NDArray[np.float_], offset: Optional[NDArray[np.float_]] = None
) -> tuple[NDArray[np.float_], NDArray[np.float_], NDArray[np.float_]]:
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
    return camera_position, camera_direction, camera_up
    # rotation_transform = np.eye(4)
    # rotation_transform[0, :3] = camera_right
    # rotation_transform[1, :3] = camera_up
    # rotation_transform[2, :3] = camera_direction
    # translation_transform = np.eye(4)
    # translation_transform[:3, -1] = -camera_position
    # look_at_transform = np.matmul(rotation_transform, translation_transform)
    # mat = np.linalg.inv(look_at_transform)
    # return camera_position, -mat[:3, 2], mat[:3, 1]


def unit_vector(v: NDArray[np.float_]) -> NDArray[np.float_]:
    """
    Return the unit vector of a vector.

    Args:
        v: vector

    Returns:
        unit vector.
    """
    norm = np.linalg.norm(v)
    return v if norm == 0 else v / norm
