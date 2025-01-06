# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

import bpy
import bonsai.tool as tool
from bonsai.bim.prop import StrProperty, Attribute, ObjProperty
from bonsai.bim.module.geometry.data import RepresentationsData, ViewportData
from bpy.types import PropertyGroup
from bpy.props import (
    PointerProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    CollectionProperty,
)


def get_contexts(self, context):
    if not RepresentationsData.is_loaded:
        RepresentationsData.load()
    return RepresentationsData.data["contexts"]


def update_mode(self, context):
    if self.is_changing_mode:
        return
    if context.mode.startswith("EDIT"):
        if self.mode == "OBJECT":
            bpy.ops.bim.override_mode_set_object("INVOKE_DEFAULT")
            tool.Geometry.disable_item_mode()
        elif self.mode == "ITEM":
            bpy.ops.bim.override_mode_set_object("INVOKE_DEFAULT")
        elif self.mode == "EDIT":
            pass
    else:
        if self.mode == "OBJECT":
            tool.Geometry.disable_item_mode()
        elif self.mode == "ITEM":
            if not self.representation_obj:
                bpy.ops.bim.import_representation_items()
        elif self.mode == "EDIT":
            bpy.ops.bim.override_mode_set_edit("INVOKE_DEFAULT")


def update_representation_obj(self, context):
    for item_obj in self.item_objs:
        if item_obj.obj:
            data = item_obj.obj.data
            bpy.data.objects.remove(item_obj.obj)
            if data and not data.users:
                bpy.data.meshes.remove(data)
    self.item_objs.clear()
    if not self.representation_obj and self.mode != "OBJECT":
        self.is_changing_mode = True
        self.mode = "OBJECT"
        self.is_changing_mode = False


def get_mode(self, context):
    if not ViewportData.is_loaded:
        ViewportData.load()
    return ViewportData.data["mode"]


def get_styles(self, context):
    # postponed import to avoid circular import
    from bonsai.bim.module.material.data import MaterialsData

    if not MaterialsData.is_loaded:
        MaterialsData.load()
    return MaterialsData.data["styles"]


def get_shape_aspects(self, context):
    if not RepresentationsData.is_loaded:
        RepresentationsData.load()
    return RepresentationsData.data["shape_aspects"]


def get_material_constituents(self, context, edit_text):
    from bonsai.bim.module.material.data import ObjectMaterialData

    if not ObjectMaterialData.is_loaded:
        ObjectMaterialData.load()
    return ObjectMaterialData.data["active_material_constituents"]


def update_shape_aspect(self, context):
    shape_aspect_id = self.representation_item_shape_aspect
    attrs = self.shape_aspect_attrs

    if shape_aspect_id == "NEW":  # new shape aspect
        attrs.name = tool.Blender.get_blender_prop_default_value(attrs, "name")
        attrs.description = tool.Blender.get_blender_prop_default_value(attrs, "description")
    else:
        shape_aspect = tool.Ifc.get().by_id(int(shape_aspect_id))
        attrs.name = shape_aspect.Name or ""
        attrs.description = shape_aspect.Description or ""


class RepresentationItem(PropertyGroup):
    name: StringProperty(name="Name")
    surface_style: StringProperty(name="Surface Style")
    surface_style_id: IntProperty(name="Surface Style ID")
    layer: StringProperty(name="Layer")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    shape_aspect: StringProperty(name="Shape Aspect")
    shape_aspect_id: IntProperty(name="Shape Aspect IFC ID")
    tags: StringProperty(name="Tags")


class RepresentationItemObject(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    obj: PointerProperty(type=bpy.types.Object)
    verts: StringProperty(name="Verts")
    edges: StringProperty(name="Edges")
    special_verts: StringProperty(name="Special Verts")
    special_edges: StringProperty(name="Special Edges")


class ShapeAspect(PropertyGroup):
    name: StringProperty(
        name="Name",
        description=(
            "Note that IfcMaterialConstituent is applied based on shape aspects using the same name as material constituent.\n"
            "In dropdown suggestions you can see names of existing material constituents."
        ),
        **({} if bpy.app.version < (3, 3, 0) else {"search": get_material_constituents}),
    )
    description: StringProperty(
        name="Description",
    )


class BIMObjectGeometryProperties(PropertyGroup):
    contexts: EnumProperty(items=get_contexts, name="Contexts")
    is_editing: BoolProperty(name="Is Editing", default=False)
    items: CollectionProperty(name="Representation Items", type=RepresentationItem)
    active_item_index: IntProperty(name="Active Representation Item Index")
    is_editing_item_style: BoolProperty(name="Is Editing Item's Style", default=False)
    representation_item_style: EnumProperty(items=get_styles, name="Representation Item Style")
    is_editing_item_shape_aspect: BoolProperty(name="Is Editing Item's Shape Aspect", default=False)
    representation_item_shape_aspect: EnumProperty(
        items=get_shape_aspects, name="Representation Item Shape Aspect", update=update_shape_aspect
    )
    shape_aspect_attrs: PointerProperty(type=ShapeAspect)


class BIMGeometryProperties(PropertyGroup):
    # Revit workaround
    should_use_presentation_style_assignment: BoolProperty(name="Force Presentation Style Assignment", default=False)
    # RIB iTwo, DESITE BIM workaround
    should_force_faceted_brep: BoolProperty(name="Force Faceted Breps", default=False)
    # Navisworks workaround
    should_force_triangulation: BoolProperty(name="Force Triangulation", default=False)
    is_changing_mode: BoolProperty(name="Is Changing Mode", default=False)
    mode: EnumProperty(items=get_mode, name="IFC Interaction Mode", update=update_mode)
    representation_obj: PointerProperty(
        name="Representation Object", type=bpy.types.Object, update=update_representation_obj
    )
    item_objs: CollectionProperty(name="Item Objects", type=RepresentationItemObject)

    def is_object_valid_for_representation_copy(self, obj: bpy.types.Object) -> bool:
        return bool(obj != bpy.context.active_object and obj.data)

    representation_from_object: PointerProperty(
        name="Object to copy a representation from.\nIt doesn't have to be an IFC object.",
        type=bpy.types.Object,
        poll=is_object_valid_for_representation_copy,
    )
