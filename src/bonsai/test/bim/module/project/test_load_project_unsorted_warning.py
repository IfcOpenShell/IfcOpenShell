from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import bpy

import bonsai.bim.handler as bim_handler
import bonsai.bim.import_ifc as import_ifc
import bonsai.tool as tool
from bonsai.bim.module.project.operator import LoadProjectElements


class TestLoadProjectUnsortedWarning:
    def test_warns_when_unsorted_collection_has_objects(self):
        op = LoadProjectElements()
        op.props = SimpleNamespace(
            filter_mode="NONE",
            should_filter_spatial_elements=False,
            pending_opening_recut=MagicMock(),
            pending_array_repair=MagicMock(),
            is_loading=True,
        )
        op.file = MagicMock()

        reported = []
        op.report = lambda level, msg: reported.append((level, msg))

        unsorted_col = MagicMock()
        unsorted_col.objects = [MagicMock(), MagicMock(), MagicMock()]

        importer = MagicMock()
        importer.gross_elements = []
        importer.broken_arrays = []

        context = MagicMock()
        context.scene = MagicMock()

        with (
            patch.object(tool.Project, "get_project_props", return_value=op.props),
            patch.object(tool.Ifc, "get", return_value=op.file),
            patch.object(tool.Blender, "get_data_dir_path", return_value=MagicMock(parent=MagicMock())),
            patch("os.access", return_value=True),
            patch("logging.basicConfig"),
            patch.object(tool.Blender, "get_bim_props", return_value=SimpleNamespace(ifc_file="test.ifc")),
            patch.object(import_ifc.IfcImportSettings, "factory", return_value=MagicMock(logger=MagicMock())),
            patch.object(import_ifc, "IfcImporter", return_value=importer),
            patch.object(bpy.data, "collections") as mock_collections,
            patch.object(tool.Project, "load_default_thumbnails"),
            patch.object(tool.Project, "set_default_context"),
            patch.object(tool.Project, "set_default_modeling_dimensions"),
            patch.object(tool.Root, "reload_grid_decorator"),
            patch.object(bim_handler, "refresh_ui_data"),
        ):
            mock_collections.get.return_value = unsorted_col
            result = op.execute(context)

        assert result == {"FINISHED"}
        assert any(level == {"WARNING"} and "Unsorted" in msg and "3 element(s)" in msg for level, msg in reported)
