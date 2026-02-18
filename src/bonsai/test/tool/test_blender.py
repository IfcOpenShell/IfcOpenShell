# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

from typing import TYPE_CHECKING

import bpy
import ifcopenshell
import pytest

import bonsai.core.tool
import bonsai.tool as tool
import tempfile
from bonsai.tool.blender import Blender as subject
from test.bim.bootstrap import NewFile
from pathlib import Path

if TYPE_CHECKING:
    import bpy.stub_internal.rna_enums as rna_enums


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Blender)


class TestCopyNodeGraph(NewFile):
    def test_run(self):
        material_to = bpy.data.materials.new("material_to")
        tool.Style.set_use_nodes(material_to, True)
        assert material_to.node_tree
        material_to_nodes = material_to.node_tree.nodes
        assert len(material_to_nodes) == 2
        for node in material_to_nodes:
            material_to_nodes.remove(node)
        assert len(material_to_nodes) == 0

        material_from = bpy.data.materials.new("material_from")
        tool.Style.set_use_nodes(material_from, True)

        subject.copy_node_graph(material_to, material_from)
        assert len(material_to_nodes) == 2


class TestSortPanelsForRegister(NewFile):
    def test_run(self):
        items = ["A", "B", "C", "D"]
        items_to_parents = {"A": "D", "D": "C", "C": "B"}
        sorted_items = subject.sort_panels_for_register(items, items_to_parents)
        assert tuple(sorted_items) == ("B", "C", "D", "A")

        with pytest.raises(AssertionError):
            subject.sort_panels_for_register(items, {"A": "K"})

        with pytest.raises(AssertionError):
            subject.sort_panels_for_register(items, {"J": "A"})


class TestBlenderErrorMessageExtraction(NewFile):
    def test_extract_operator_reports(self) -> None:

        ERROR_REPORTS = ["ERROR!!!\nERROR", "ERROR"]

        class OBJECT_OT_test_fail_operator(bpy.types.Operator):
            bl_idname = "object.test_fail_operator"
            bl_label = "Test Fail Operator"

            def execute(self, context) -> "set[rna_enums.OperatorReturnItems]":
                self.report({"INFO"}, "Info message.")
                subject.report_operator_errors(self, ERROR_REPORTS)
                return {"FINISHED"}

        bpy.utils.register_class(OBJECT_OT_test_fail_operator)

        try:
            bpy.ops.object.test_fail_operator()
        except RuntimeError as e:
            error_reports = subject.extract_error_reports(e)
            assert error_reports == ERROR_REPORTS

        bpy.utils.unregister_class(OBJECT_OT_test_fail_operator)

    def test_ignore_actual_runtime_errors_from_operators(self) -> None:

        class OBJECT_OT_test_fail_operator(bpy.types.Operator):
            bl_idname = "object.test_fail_operator"
            bl_label = "Test Fail Operator"

            def execute(self, context):
                raise RuntimeError("Intentional runtime error.")

        bpy.utils.register_class(OBJECT_OT_test_fail_operator)

        try:
            bpy.ops.object.test_fail_operator()
        except RuntimeError as e:
            error_reports = subject.extract_error_reports(e)
            assert error_reports == []

        bpy.utils.unregister_class(OBJECT_OT_test_fail_operator)


class TestGetSelectedFiles(NewFile):
    def test_get_a_single_file(self) -> None:
        with tempfile.NamedTemporaryFile() as f:
            file = type("", (object,), {"name": f.name})()
            assert subject.get_selected_files(Path(f.name).parent, [file]) == [f.name]

    def test_get_multiple_files(self) -> None:
        with tempfile.NamedTemporaryFile() as f:
            with tempfile.NamedTemporaryFile() as g:
                file = type("", (object,), {"name": f.name})()
                file2 = type("", (object,), {"name": g.name})()
                assert subject.get_selected_files(Path(f.name).parent, [file, file2]) == [f.name, g.name]

    def test_exclude_directories(self) -> None:
        with tempfile.NamedTemporaryFile() as f:
            with tempfile.TemporaryDirectory() as d:
                file = type("", (object,), {"name": f.name})()
                directory = type("", (object,), {"name": d})()
                assert subject.get_selected_files(Path(f.name).parent, [file, directory]) == [f.name]

    def test_get_relative_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_path = Path(tmp_dir)
            with tempfile.NamedTemporaryFile(dir=tmp_dir, suffix=".ifc") as f:
                tool.Ifc.set_path(str(f.name))
                with tempfile.NamedTemporaryFile(dir=tmp_dir) as g:
                    file = type("", (object,), {"name": g.name})
                    assert subject.get_selected_files(Path(g.name).parent, [file], use_relative_path=True) == [
                        Path(g.name).name
                    ]
