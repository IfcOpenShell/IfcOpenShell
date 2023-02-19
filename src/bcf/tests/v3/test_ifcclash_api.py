import numpy as np
import pytest

from bcf.v3.bcfxml import BcfXml


def test_create_clash_set_bcf() -> None:
    bcfxml = BcfXml.create_new("Clash Test")
    topic = bcfxml.add_topic("Test", "Test topic", "IfcClash")
    topic.add_viewpoint_from_point_and_guids(
        np.array([10, 10, 10]),
        "firstId",
        "secondId",
    )
    assert len(topic.viewpoints) == 1
    guid, vi_handler = next((k, v) for k, v in topic.viewpoints.items())
    v_info = vi_handler.visualization_info
    assert f"{v_info.guid}.bcfv" == guid
    components = v_info.components.selection.component
    assert {c.ifc_guid for c in components} == {"firstId", "secondId"}
    camera = v_info.perspective_camera
    viewpoint = camera.camera_view_point
    assert viewpoint.x == 15
    assert viewpoint.y == 15
    assert viewpoint.z == 15
    # default direction is the unit vector of -1, -1, -1
    direction = camera.camera_direction
    assert direction.x == pytest.approx(-1 / 3**0.5)
    assert direction.y == pytest.approx(-1 / 3**0.5)
    assert direction.z == pytest.approx(-1 / 3**0.5)
    # default
    up_vector = camera.camera_up_vector
    assert up_vector.x == pytest.approx(-1 / 6**0.5)
    assert up_vector.y == pytest.approx(-1 / 6**0.5)
    assert up_vector.z == pytest.approx(1 / 1.5**0.5)
    assert camera.field_of_view == 60
