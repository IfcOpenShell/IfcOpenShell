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

"""Texture UV maps must load on a plain project load (issue #6702).

The official buildingSMART texture examples (blob/image/pixel texture on a
tessellated shape) rendered untextured in Bonsai because the mesh UV layer
from IfcIndexedTriangleTextureMap was only applied behind the
"Load Indexed Colour Maps" advanced setting (default off). Texture UVs are
now always loaded; the setting only gates indexed colour maps."""

import bpy
import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.unit
import ifcopenshell.util.unit
from mathutils import Vector

import bonsai.tool as tool

from . import bootstrap

# One quad split in two triangles, textured with a 2x2 pixel texture.
VERTS = ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (0.0, 1.0, 0.0))
TRIANGLES = ((1, 2, 3), (1, 3, 4))
UV_COORDS = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))
TEX_COORD_INDEX = ((1, 2, 3), (1, 3, 4))


def create_textured_ifc(path: str) -> None:
    ifc = ifcopenshell.file(schema="IFC4")
    project = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject", name="Test")
    ifcopenshell.api.unit.assign_unit(ifc)
    model = ifcopenshell.api.context.add_context(ifc, context_type="Model")
    body = ifcopenshell.api.context.add_context(
        ifc, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
    )

    site = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcSite", name="Site")
    ifcopenshell.api.aggregate.assign_object(ifc, products=[site], relating_object=project)
    element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcBuildingElementProxy", name="Textured")
    ifcopenshell.api.spatial.assign_container(ifc, products=[element], relating_structure=site)

    coordinates = ifc.create_entity("IfcCartesianPointList3D", CoordList=VERTS)
    face_set = ifc.create_entity("IfcTriangulatedFaceSet", Coordinates=coordinates, CoordIndex=TRIANGLES)
    representation = ifc.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=body,
        RepresentationIdentifier="Body",
        RepresentationType="Tessellation",
        Items=[face_set],
    )
    ifcopenshell.api.geometry.assign_representation(ifc, product=element, representation=representation)
    ifcopenshell.api.geometry.edit_object_placement(ifc, product=element)

    # 2x2 RGBA pixel texture, self-contained (no external image file needed).
    texture = ifc.create_entity(
        "IfcPixelTexture",
        RepeatS=True,
        RepeatT=True,
        Mode="DIFFUSE",
        Width=2,
        Height=2,
        ColourComponents=4,
        # Bit-string encoding of RGBA pixels: red, green, blue, white.
        Pixel=[
            "".join(f"{byte:08b}" for byte in rgba)
            for rgba in ((255, 0, 0, 255), (0, 255, 0, 255), (0, 0, 255, 255), (255, 255, 255, 255))
        ],
    )
    uv_verts = ifc.create_entity("IfcTextureVertexList", TexCoordsList=UV_COORDS)
    ifc.create_entity(
        "IfcIndexedTriangleTextureMap",
        Maps=[texture],
        MappedTo=face_set,
        TexCoords=uv_verts,
        TexCoordIndex=TEX_COORD_INDEX,
    )

    rendering = ifc.create_entity(
        "IfcSurfaceStyleRendering",
        SurfaceColour=ifc.create_entity("IfcColourRgb", Red=1.0, Green=1.0, Blue=1.0),
        ReflectanceMethod="NOTDEFINED",
    )
    textures_style = ifc.create_entity("IfcSurfaceStyleWithTextures", Textures=[texture])
    style = ifc.create_entity("IfcSurfaceStyle", Name="Textured style", Side="BOTH", Styles=[rendering, textures_style])
    ifc.create_entity("IfcStyledItem", Item=face_set, Styles=[style], Name=None)

    ifc.write(path)


class TestTextureUVImport(bootstrap.NewFile):
    def test_texture_uvs_load_without_indexed_maps_setting(self, tmp_path):
        ifc_path = str(tmp_path / "textured.ifc")
        create_textured_ifc(ifc_path)

        props = tool.Project.get_project_props()
        assert not props.load_indexed_maps  # texture UVs must not depend on this setting
        bpy.ops.bim.load_project(filepath=ifc_path, should_start_fresh_session=False)

        obj = bpy.data.objects.get("IfcBuildingElementProxy/Textured")
        assert obj is not None
        mesh = obj.data
        assert isinstance(mesh, bpy.types.Mesh)

        # UV layer applied from IfcIndexedTriangleTextureMap.
        uv_layer = mesh.uv_layers.active
        assert uv_layer is not None
        expected = []
        for triangle, tex_coord_index in zip(TRIANGLES, TEX_COORD_INDEX):
            for vert_index, uv_index in zip(triangle, tex_coord_index):
                expected.append((VERTS[vert_index - 1], UV_COORDS[uv_index - 1]))
        assert len(uv_layer.data) == len(expected)
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        for poly in mesh.polygons:
            for loop_index in poly.loop_indices:
                vert = mesh.vertices[mesh.loops[loop_index].vertex_index]
                matches = [uv for co, uv in expected if (Vector(co) * unit_scale - vert.co).length < 1e-5]
                uv = uv_layer.data[loop_index].uv
                assert any((Vector(m) - uv).length < 1e-5 for m in matches)

        # Material has the decoded pixel texture wired to Base Color.
        material = next((m for m in mesh.materials if m), None)
        assert material is not None and material.use_nodes
        image_node = next(n for n in material.node_tree.nodes if n.type == "TEX_IMAGE")
        assert image_node.image is not None
        assert tuple(image_node.image.size) == (2, 2)
        (link,) = image_node.outputs[0].links
        assert link.to_socket.name == "Base Color"
