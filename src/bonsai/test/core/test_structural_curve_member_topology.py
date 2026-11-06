# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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

import sys
import types
from unittest.mock import MagicMock, patch

import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.material
import ifcopenshell.api.root
import ifcopenshell.api.unit
import numpy as np


def _create_structural_curve_member_with_edge():
    ifc_file = ifcopenshell.file(schema="IFC4")
    ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject")
    ifcopenshell.api.unit.assign_unit(ifc_file)
    model = ifcopenshell.api.context.add_context(ifc_file, context_type="Model")
    body = ifcopenshell.api.context.add_context(
        ifc_file,
        context_type="Model",
        context_identifier="Body",
        target_view="MODEL_VIEW",
        parent=model,
    )
    ifcopenshell.api.context.add_context(
        ifc_file,
        context_type="Model",
        context_identifier="Axis",
        target_view="GRAPH_VIEW",
        parent=model,
    )

    member = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcStructuralCurveMember")
    member.Axis = ifc_file.createIfcDirection((0.0, 0.0, 1.0))
    v1 = ifc_file.createIfcVertexPoint(ifc_file.createIfcCartesianPoint((0.0, 0.0, 0.0)))
    v2 = ifc_file.createIfcVertexPoint(ifc_file.createIfcCartesianPoint((5.0, 0.0, 0.0)))
    edge = ifc_file.createIfcEdge(v1, v2)
    topo_rep = ifc_file.createIfcTopologyRepresentation(body, "Body", "Edge", [edge])
    member.Representation = ifc_file.createIfcProductDefinitionShape(None, None, [topo_rep])

    profile = ifc_file.create_entity(
        "IfcIShapeProfileDef",
        ProfileName="HEA100",
        ProfileType="AREA",
        OverallWidth=0.1,
        OverallDepth=0.096,
        WebThickness=0.005,
        FlangeThickness=0.008,
    )
    material_set = ifcopenshell.api.material.add_material_set(ifc_file, set_type="IfcMaterialProfileSet")
    ifcopenshell.api.material.add_profile(ifc_file, profile_set=material_set, profile=profile)
    ifcopenshell.api.material.assign_material(ifc_file, products=[member], type="IfcMaterialProfileSetUsage")
    rel = member.HasAssociations[0]
    rel.RelatingMaterial.ForProfileSet = material_set

    return ifc_file, member, topo_rep, edge


def _mock_blender_modules():
    mock_bpy = MagicMock()
    mock_bpy.__path__ = []
    mock_bpy.types.Operator = type("Operator", (), {})
    mock_bpy.types.Panel = type("Panel", (), {})
    mock_bpy.types.PropertyGroup = type("PropertyGroup", (), {})
    mock_bpy.types.UIList = type("UIList", (), {})
    mock_mathutils = MagicMock()
    mock_mathutils.__path__ = []

    import pathlib

    bonsai_root = pathlib.Path(__file__).resolve().parents[2] / "bonsai"
    bim_pkg = types.ModuleType("bonsai.bim")
    bim_pkg.__path__ = [str(bonsai_root / "bim")]
    bim_pkg.ifc = MagicMock()
    module_pkg = types.ModuleType("bonsai.bim.module")
    module_pkg.__path__ = [str(bonsai_root / "bim" / "module")]
    model_pkg = types.ModuleType("bonsai.bim.module.model")
    model_pkg.__path__ = [str(bonsai_root / "bim" / "module" / "model")]
    structural_pkg = types.ModuleType("bonsai.bim.module.structural")
    structural_pkg.__path__ = [str(bonsai_root / "bim" / "module" / "structural")]
    mock_tool = MagicMock()
    mock_tool.Ifc.Operator = type("IfcOperator", (), {})
    mock_polyline = MagicMock()
    mock_polyline.PolylineOperator = type("PolylineOperator", (), {})

    return {
        "bpy": mock_bpy,
        "bpy.types": mock_bpy.types,
        "bpy.props": mock_bpy.props,
        "bpy.utils": mock_bpy.utils,
        "bpy.utils.previews": mock_bpy.utils.previews,
        "bpy.app": mock_bpy.app,
        "bpy.app.handlers": mock_bpy.app.handlers,
        "bpy_extras": MagicMock(),
        "bpy_extras.io_utils": MagicMock(),
        "mathutils": mock_mathutils,
        "mathutils.geometry": mock_mathutils.geometry,
        "bmesh": MagicMock(),
        "blf": MagicMock(),
        "gpu": MagicMock(),
        "gpu_extras": MagicMock(),
        "gpu_extras.batch": MagicMock(),
        "bonsai.bim": bim_pkg,
        "bonsai.bim.ifc": bim_pkg.ifc,
        "bonsai.bim.helper": MagicMock(),
        "bonsai.bim.module": module_pkg,
        "bonsai.bim.module.model": model_pkg,
        "bonsai.bim.module.model.data": MagicMock(),
        "bonsai.bim.module.model.decorator": MagicMock(),
        "bonsai.bim.module.model.opening": MagicMock(),
        "bonsai.bim.module.model.polyline": mock_polyline,
        "bonsai.bim.module.model.product": MagicMock(),
        "bonsai.bim.module.structural": structural_pkg,
        "bonsai.bim.module.structural.data": MagicMock(),
        "bonsai.bim.module.structural.decorator": MagicMock(),
        "bonsai.bim.module.structural.shader": MagicMock(),
        "bonsai.tool": mock_tool,
    }


def test_recreate_profile_preserves_structural_curve_member_edge_topology():
    ifc_file, member, topo_rep, edge = _create_structural_curve_member_with_edge()

    with patch.dict(sys.modules, _mock_blender_modules()):
        import bonsai.bim.module.model.profile as profile_mod
        import bonsai.tool as tool

        with patch.object(tool.Ifc, "get", return_value=ifc_file), patch.object(
            tool.Ifc, "get_entity", return_value=member
        ):
            obj = MagicMock()
            joiner = profile_mod.DumbProfileJoiner()
            joiner.recreate_profile(member, obj)

            recalculator = profile_mod.DumbProfileRecalculator()
            recalculator.recalculate([obj])

            regenerator = profile_mod.DumbProfileRegenerator()
            regenerator.file = ifc_file
            profile_def = ifc_file.by_type("IfcIShapeProfileDef")[0]
            assert member not in regenerator.get_elements_using_profile(profile_def)

    assert len(member.Representation.Representations) == 1
    assert member.Representation.Representations[0] == topo_rep
    assert member.Representation.Representations[0].is_a("IfcTopologyRepresentation")
    assert member.Representation.Representations[0].Items[0] == edge


def test_get_curve_member_rotation_handles_edge_and_non_edge_representations():
    ifc_file, member, topo_rep, _ = _create_structural_curve_member_with_edge()

    with patch.dict(sys.modules, _mock_blender_modules()):
        from bonsai.bim.module.structural.load_decoration_data import ShaderInfo

        data = ShaderInfo.__new__(ShaderInfo)

        # 1. Valid IfcEdge topology representation
        rot = data.get_curve_member_rotation(member)
        assert rot.shape == (3, 3)
        assert np.allclose(rot, np.eye(3))

        # 2. Corrupted representation (e.g. IfcExtrudedAreaSolid in first slot) does not raise AttributeError
        profile_def = ifc_file.by_type("IfcIShapeProfileDef")[0]
        body_ctx = topo_rep.ContextOfItems
        swept_rep = ifcopenshell.api.geometry.add_profile_representation(
            ifc_file, context=body_ctx, profile=profile_def, depth=1.0
        )
        member.Representation.Representations = [swept_rep]
        ifcopenshell.api.geometry.edit_object_placement(ifc_file, product=member, matrix=np.eye(4))

        fallback_rot = data.get_curve_member_rotation(member)
        assert fallback_rot.shape == (3, 3)
        assert np.allclose(fallback_rot, np.eye(3))


def test_add_structural_member_connection_noop_when_member_unset():
    with patch.dict(sys.modules, _mock_blender_modules()):
        import bonsai.bim.module.structural.operator as structural_op
        import bonsai.tool as tool

        ifc_file = ifcopenshell.file(schema="IFC4")
        conn = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcStructuralPointConnection")

        context = MagicMock()
        context.active_object = MagicMock()
        oprops = types.SimpleNamespace(ifc_definition_id=conn.id())
        props = types.SimpleNamespace(relating_structural_member=None)

        with patch.object(tool.Blender, "get_object_bim_props", return_value=oprops), patch.object(
            tool.Structural, "get_object_structural_props", return_value=props
        ), patch.object(tool.Ifc, "get", return_value=ifc_file):
            op = structural_op.AddStructuralMemberConnection()
            result = op._execute(context)
            assert result == {"FINISHED"}
