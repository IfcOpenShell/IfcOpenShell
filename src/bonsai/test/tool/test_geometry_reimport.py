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

import multiprocessing

import bpy
import ifcopenshell.geom
import ifcopenshell.util.representation

import bonsai.tool as tool
from bonsai.tool.geometry import Geometry as subject
from test.bim.bootstrap import NewFile


class TestReimportElementRepresentations(NewFile):
    def test_the_cpu_multiprocessing_toggle_sets_the_iterator_thread_count(self, monkeypatch):
        thread_counts = []

        class RecordingIterator(ifcopenshell.geom.iterator):
            def __init__(self, settings, file_or_filename, num_threads=1, **kwargs):
                thread_counts.append(num_threads)
                super().__init__(settings, file_or_filename, num_threads, **kwargs)

        bpy.ops.bim.create_project()
        bpy.ops.mesh.primitive_cube_add()
        obj = bpy.context.active_object
        bpy.ops.bim.assign_class(obj=obj.name, ifc_class="IfcWall")
        element = tool.Ifc.get_entity(obj)
        representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        monkeypatch.setattr(multiprocessing, "cpu_count", lambda: 3)
        monkeypatch.setattr(ifcopenshell.geom, "iterator", RecordingIterator)
        props = tool.Project.get_project_props()

        props.should_use_cpu_multiprocessing = False
        subject.reimport_element_representations(obj, representation)
        assert thread_counts == [1]
        assert len(tool.Ifc.get_object(element).data.polygons) > 0

        props.should_use_cpu_multiprocessing = True
        subject.reimport_element_representations(obj, representation)
        assert thread_counts == [1, 3]
        assert len(tool.Ifc.get_object(element).data.polygons) > 0
