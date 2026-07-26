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
#
# This file was modified with the assistance of an AI coding tool.

import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import bpy
import ifcopenshell
import numpy as np
import pytest

import bonsai
import bonsai.core.tool
import bonsai.tool as tool
from bonsai.tool.blender import Blender as subject
from test.bim.bootstrap import NewFile

if TYPE_CHECKING:
    import bpy.stub_internal.rna_enums as rna_enums


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Blender)


class TestTransparentColor(NewFile):
    def test_default_alpha_overrides_to_zero_one(self):
        assert subject.transparent_color([1.0, 0.5, 0.25, 1.0]) == [1.0, 0.5, 0.25, 0.1]

    def test_explicit_alpha_is_applied(self):
        assert subject.transparent_color([1.0, 0.5, 0.25, 1.0], alpha=0.5) == [1.0, 0.5, 0.25, 0.5]

    def test_does_not_mutate_input(self):
        original = [1.0, 0.5, 0.25, 1.0]
        subject.transparent_color(original)
        assert original == [1.0, 0.5, 0.25, 1.0]

    def test_returns_new_list_instance(self):
        original = [1.0, 0.5, 0.25, 1.0]
        result = subject.transparent_color(original)
        assert result is not original


class TestViewportDecoratorDrawBatch(NewFile):
    def test_empty_content_pos_skips_shader_calls(self):
        from unittest.mock import MagicMock

        decorator = subject.ViewportDecorator()
        decorator.line_shader = MagicMock()
        decorator.shader = MagicMock()
        decorator.draw_batch("LINES", [], (1.0, 1.0, 1.0, 1.0))
        decorator.line_shader.uniform_float.assert_not_called()
        decorator.shader.uniform_float.assert_not_called()

    def test_empty_indices_skips_shader_calls(self):
        from unittest.mock import MagicMock

        decorator = subject.ViewportDecorator()
        decorator.line_shader = MagicMock()
        decorator.shader = MagicMock()
        decorator.draw_batch("LINES", [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)], (1.0, 1.0, 1.0, 1.0), indices=[])
        decorator.line_shader.uniform_float.assert_not_called()
        decorator.shader.uniform_float.assert_not_called()


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


class TestGetDebugInfo(NewFile):
    # Only keys that are safe to set if Bonsai fails to load.
    EXPECTED_KEYS = {
        "os",
        "os_version",
        "python_version",
        "architecture",
        "machine",
        "processor",
        "blender_version",
        "bonsai_version",
        "bonsai_commit_hash",
        "bonsai_commit_date",
        "bonsai_git_branch",
        "last_actions",
        "last_error",
    }

    def test_failed_to_load_returns_only_base_keys(self):
        info = bonsai.get_debug_info(bonsai_failed_to_load=True)
        assert set(info.keys()) == self.EXPECTED_KEYS


class TestNpFrombufferLegacy(NewFile):
    """Decoding ``n`` floats from a buffer must yield a length-``n`` array
    regardless of whether the buffer was written as ``float32`` or ``float64``."""

    @pytest.mark.parametrize("n", [3, 9])
    @pytest.mark.parametrize("dtype", [np.float32, np.float64])
    def test_decodes_to_n_elements(self, n, dtype):
        data = np.arange(n, dtype=dtype).tobytes()
        result = subject.np_frombuffer_legacy(data, n)
        assert result.shape == (n,)
        np.testing.assert_allclose(result, np.arange(n))


class TestGetObjectFromGuidMissing(NewFile):
    """``get_object_from_guid`` must honour its ``Optional[Object]`` return
    contract: a GUID that does not resolve in the current IFC file yields
    ``None``, not a ``RuntimeError``. Callers iterate stored GUID lists
    (array children, library refs, …) and rely on the falsy return to
    skip stale entries."""

    def test_returns_none_when_guid_not_in_file(self):
        bpy.ops.bim.create_project()
        assert tool.Ifc.get() is not None
        assert subject.get_object_from_guid("3iyt7r$Hf4_hQYNhBIDJI4") is None
