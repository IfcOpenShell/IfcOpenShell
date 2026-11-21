# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.
#
# This file was generated with the assistance of an AI coding tool.

import bcf.v2.bcfxml
import bpy
import numpy as np
import pytest

import bonsai.tool as tool
from bonsai.bim.module.bcf import bcfstore
from test.bim.bootstrap import NewFile


@pytest.fixture
def primary_viewpoint_topic(tmp_path):
    NewFile()
    bcfxml = bcf.v2.bcfxml.BcfXml.create_new("Test")
    topic = bcfxml.add_topic("Clash", "Clash", "IfcClash")
    topic.add_viewpoint_from_point_and_guids(np.array([10, 10, 10]), "firstId", "secondId")
    topic.add_viewpoint_from_point_and_guids(np.array([1, 1, 1]), "firstId")
    filepath = tmp_path / "test.bcf"
    bcfxml.save(filepath)
    bcfstore.BcfStore.set_by_filepath(str(filepath))
    bpy.ops.bim.load_bcf_topics()
    yield bcfstore.BcfStore.get_bcfxml().topics[topic.guid]
    bcfstore.BcfStore.unload_bcfxml()


def test_activate_primary_viewpoint_by_guid(primary_viewpoint_topic):
    topic = primary_viewpoint_topic
    assert "viewpoint.bcfv" in topic.viewpoints
    guid = topic.viewpoints["viewpoint.bcfv"].guid
    assert bpy.ops.bim.activate_bcf_viewpoint(viewpoint_guid=guid) == {"FINISHED"}


def test_activate_unknown_viewpoint_reports_error(primary_viewpoint_topic):
    with pytest.raises(RuntimeError, match="No such viewpoint"):
        bpy.ops.bim.activate_bcf_viewpoint(viewpoint_guid="unknown")


def test_remove_primary_viewpoint(primary_viewpoint_topic):
    topic = primary_viewpoint_topic
    props = tool.Bcf.get_bcf_props()
    props.active_topic.viewpoints = "viewpoint.bcfv"
    assert bpy.ops.bim.remove_bcf_viewpoint() == {"FINISHED"}
    assert "viewpoint.bcfv" not in topic.viewpoints
    assert len(topic.markup.viewpoints) == 1
