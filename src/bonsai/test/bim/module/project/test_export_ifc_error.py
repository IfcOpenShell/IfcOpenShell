from unittest.mock import MagicMock, patch

import bpy

import bonsai.bim.export_ifc as export_ifc
from bonsai.bim.module.project.operator import ExportIFC


class TestExportIFCWriteError:
    def test_reports_error_and_cancels_when_export_fails(self, tmp_path):
        op = ExportIFC()
        op.filepath = str(tmp_path / "ExampleSimpleBuilding.ifc")
        op.json_version = "4"
        op.json_compact = False
        op.skip_recent = True

        reported = []
        op.report = lambda level, msg: reported.append((level, msg))

        context = MagicMock()
        context.scene = MagicMock()

        failing_exporter = MagicMock()
        failing_exporter.export.side_effect = RuntimeError(
            f"Failed to write to path: '{op.filepath}', check folder and file permissions."
        )

        with (
            patch.object(bpy.path, "ensure_ext", side_effect=lambda p, ext: p if p.endswith(ext) else p + ext),
            patch.object(export_ifc.IfcExportSettings, "factory", return_value=MagicMock()),
            patch.object(export_ifc, "IfcExporter", return_value=failing_exporter),
        ):
            result = op._execute(context)

        assert result == {"CANCELLED"}
        assert len(reported) == 1
        assert reported[0][0] == {"ERROR"}
        assert "Failed to write IFC file:" in reported[0][1]
