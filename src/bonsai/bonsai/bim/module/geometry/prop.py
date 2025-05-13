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

import ifcopenshell
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
from typing import Optional, TYPE_CHECKING, Union, Literal


def get_contexts(self: "BIMObjectGeometryProperties", context: bpy.types.Context) -> list[tuple[str, str, str]]:
    if not RepresentationsData.is_loaded:
        RepresentationsData.load()
    return RepresentationsData.data["contexts"]


def update_mode(self: "BIMGeometryProperties", context: bpy.types.Context) -> None:
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


def update_representation_obj(self: "BIMGeometryProperties", context: bpy.types.Context) -> None:
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


def get_mode(self: "BIMGeometryProperties", context: bpy.types.Context) -> list[tuple[str, str, str, str, int]]:
    if not ViewportData.is_loaded:
        ViewportData.load()
    return ViewportData.data["mode"]


def get_styles(self: "BIMObjectGeometryProperties", context: bpy.types.Context) -> list[tuple[str, str, str]]:
    # postponed import to avoid circular import
    from bonsai.bim.module.material.data import MaterialsData

    if not MaterialsData.is_loaded:
        MaterialsData.load()
    return MaterialsData.data["styles"]


def get_shape_aspects(self: "BIMObjectGeometryProperties", context: bpy.types.Context) -> list[tuple[str, str, str]]:
    if not RepresentationsData.is_loaded:
        RepresentationsData.load()
    return RepresentationsData.data["shape_aspects"]


def get_material_constituents(self: "ShapeAspect", context: bpy.types.Context, edit_text: str) -> list[str]:
    from bonsai.bim.module.material.data import ObjectMaterialData

    if not ObjectMaterialData.is_loaded:
        ObjectMaterialData.load()
    return ObjectMaterialData.data["active_material_constituents"]


def get_layers(self: "BIMObjectGeometryProperties", context: bpy.types.Context) -> list[tuple[str, str, str]]:
    from bonsai.bim.module.layer.data import LayersData

    if not LayersData.is_loaded:
        LayersData.load()
    return LayersData.data["layers_enum"]


def get_layers_no_active(self: "BIMObjectGeometryProperties", context: bpy.types.Context) -> list[tuple[str, str, str]]:
    from bonsai.bim.module.layer.data import LayersData

    if not LayersData.is_loaded:
        LayersData.load()
    return LayersData.data["layers_enum_no_active"]


def update_shape_aspect(self: "BIMObjectGeometryProperties", context: bpy.types.Context) -> None:
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
    layer_id: IntProperty(name="Layer ID")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    shape_aspect: StringProperty(name="Shape Aspect")
    shape_aspect_id: IntProperty(name="Shape Aspect IFC ID")
    tags: StringProperty(name="Tags")

    if TYPE_CHECKING:
        name: str
        surface_style: str
        surface_style_id: int
        layer: str
        layer_id: int
        ifc_definition_id: int
        shape_aspect: str
        shape_aspect_id: int
        tags: str


class RepresentationItemObject(PropertyGroup):
    name: StringProperty(name="Name")
    obj: PointerProperty(type=bpy.types.Object)
    ifc_definition_id: IntProperty()

    if TYPE_CHECKING:
        name: str
        obj: Union[bpy.types.Object, None]
        ifc_definition_id: int


class ShapeAspect(PropertyGroup):
    name: StringProperty(
        name="Name",
        description=(
            "If applicable, shape aspect names should correlate with names of material constituents.\n"
            "Click to see autocompletion for constituent names."
        ),
        search=get_material_constituents,
    )
    description: StringProperty(
        name="Description",
    )


def update_is_adding_representation_layer(self: "BIMObjectGeometryProperties", context: bpy.types.Context) -> None:
    if self.is_adding_representation_layer:
        ifc_file = tool.Ifc.get()
        if not ifc_file.by_type("IfcPresentationLayerAssignment"):
            tool.Blender.show_info_message(
                "Cannot edit presentation layer - no presentation layers found in the project."
            )
            del self["is_adding_representation_layer"]
            return
        return

    if "representation_layer" in self:
        del self["representation_layer"]
        del self["is_adding_representation_layer"]


def update_is_editing_item_layer(self: "BIMObjectGeometryProperties", context: bpy.types.Context) -> None:
    if self.is_editing_item_layer:
        ifc_file = tool.Ifc.get()

        if not ifc_file.by_type("IfcPresentationLayerAssignment"):
            tool.Blender.show_info_message(
                "Cannot edit presentation layer - no presentation layers found in the project."
            )
            del self["is_editing_item_layer"]
            return

        active_ui_item = self.active_item
        assert active_ui_item
        item = ifc_file.by_id(active_ui_item.ifc_definition_id)
        if layer := next(iter(item.LayerAssignment), None):
            self.representation_item_layer = str(layer.id())
        return

    if "representation_item_layer" in self:
        del self["representation_item_layer"]
        del self["is_editing_item_layer"]


class BIMObjectGeometryProperties(PropertyGroup):
    # Representations UI.
    contexts: EnumProperty(items=get_contexts, name="Contexts")
    is_adding_representation_layer: BoolProperty(
        name="Is Adding Representation's Layer",
        description="Toggle adding presentation layer for the representation.",
        default=False,
        update=update_is_adding_representation_layer,
    )
    representation_layer: EnumProperty(
        items=get_layers_no_active,
        name="Representation's Presentation Layer",
        description="Presentation layer to add.",
    )

    # Representation items UI.
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
    is_editing_item_layer: BoolProperty(
        name="Is Editing Item's Presentation Layer",
        description="Toggle editing presentation layer for the item.",
        default=False,
        update=update_is_editing_item_layer,
    )
    representation_item_layer: EnumProperty(items=get_layers, name="Representation Item's Layer")

    @property
    def active_item(self) -> Union[RepresentationItem, None]:
        return tool.Blender.get_active_uilist_element(self.items, self.active_item_index)

    if TYPE_CHECKING:
        contexts: str
        is_adding_representation_layer: bool
        representation_layer: str
        is_editing: bool
        items: bpy.types.bpy_prop_collection_idprop[RepresentationItem]
        active_item_index: int
        is_editing_item_style: bool
        representation_item_style: str
        is_editing_item_shape_aspect: bool
        representation_item_shape_aspect: str
        shape_aspect_attrs: ShapeAspect
        is_editing_item_layer: bool
        representation_item_layer: str


GeometryMode = Literal["OBJECT", "ITEM", "EDIT"]


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
        name="Representation Object",
        description=(
            "Only used for Item Mode. When element is in Item Mode, new objects are imported "
            "for each element's representation item, original element's object is hidden and "
            "representation_obj pointing to it. None if no object in Item Mode."
        ),
        type=bpy.types.Object,
        update=update_representation_obj,
    )
    item_objs: CollectionProperty(name="Item Objects", type=RepresentationItemObject)

    def add_item_object(
        self, obj: bpy.types.Object, item: ifcopenshell.entity_instance, name: Optional[str] = None
    ) -> RepresentationItemObject:
        blender_item = self.item_objs.add()
        blender_item.obj = obj
        blender_item.ifc_definition_id = item.id()
        if name is not None:
            blender_item.name = name
        return blender_item

    def remove_item_object_by_entity(self, item: ifcopenshell.entity_instance) -> None:
        ifc_id = item.id()
        for i, item_obj in enumerate(self.item_objs):
            if item_obj.ifc_definition_id == ifc_id:
                self.item_objs.remove(i)
                return
        assert False

    def is_object_valid_for_representation_copy(self, obj: bpy.types.Object) -> bool:
        return bool(obj != bpy.context.active_object and obj.data)

    representation_from_object: PointerProperty(
        name="Object to copy a representation from.\nIt doesn't have to be an IFC object.",
        type=bpy.types.Object,
        poll=is_object_valid_for_representation_copy,
    )

    if TYPE_CHECKING:
        should_use_presentation_style_assignment: bool
        should_force_faceted_brep: bool
        should_force_triangulation: bool
        is_changing_mode: bool
        mode: GeometryMode
        representation_obj: Union[bpy.types.Object, None]
        item_objs: bpy.types.bpy_prop_collection_idprop[RepresentationItemObject]
        representation_from_object: Union[bpy.types.Object, None]
