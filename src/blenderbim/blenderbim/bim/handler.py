# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import json
import addon_utils
import ifcopenshell.api.owner.settings
import blenderbim.tool as tool
import blenderbim.core.owner as core_owner
from blenderbim.bim.module.drawing.prop import RasterStyleProperty
from bpy.app.handlers import persistent
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.owner.prop import get_user_person, get_user_organisation
from ifcopenshell.api.material.data import Data as MaterialData
from ifcopenshell.api.type.data import Data as TypeData


global_subscription_owner = object()


def mode_callback(obj, data):
    if not bpy.context.scene.BIMProjectProperties.is_authoring:
        return
    objects = bpy.context.selected_objects
    if bpy.context.active_object:
        objects += [bpy.context.active_object]
    for obj in objects:
        if (
            obj.mode != "EDIT"
            or not obj.data
            or not isinstance(obj.data, (bpy.types.Mesh, bpy.types.Curve, bpy.types.TextCurve))
            or not obj.BIMObjectProperties.ifc_definition_id
        ):
            continue
        if obj.data.BIMMeshProperties.ifc_definition_id:
            IfcStore.edited_objs.add(obj)
        elif IfcStore.get_file().by_id(obj.BIMObjectProperties.ifc_definition_id).is_a("IfcGridAxis"):
            IfcStore.edited_objs.add(obj)


def name_callback(obj, data):
    # TODO Do we still need this, now that we are monitoring the undo redo objects?
    try:
        obj.name
    except:
        return  # In case the object RNA is gone during an undo / redo operation
    # Blender names are up to 63 UTF-8 bytes
    if len(bytes(obj.name, "utf-8")) >= 63:
        return

    if isinstance(obj, bpy.types.Material):
        if obj.BIMObjectProperties.ifc_definition_id:
            IfcStore.get_file().by_id(obj.BIMObjectProperties.ifc_definition_id).Name = obj.name
            MaterialData.load_materials()
        if obj.BIMMaterialProperties.ifc_style_id:
            IfcStore.get_file().by_id(obj.BIMMaterialProperties.ifc_style_id).Name = obj.name
        refresh_ui_data()
        return

    if not obj.BIMObjectProperties.ifc_definition_id or "/" not in obj.name:
        return
    element = IfcStore.get_file().by_id(obj.BIMObjectProperties.ifc_definition_id)
    if not element.is_a("IfcRoot"):
        return
    if element.is_a("IfcSpatialStructureElement") or (hasattr(element, "IsDecomposedBy") and element.IsDecomposedBy):
        collection = obj.users_collection[0]
        collection.name = obj.name
    if element.is_a("IfcGrid"):
        axis_obj = IfcStore.get_element(element.UAxes[0].id())
        axis_collection = axis_obj.users_collection[0]
        grid_collection = None
        for collection in bpy.data.collections:
            if axis_collection.name in collection.children.keys():
                grid_collection = collection
                break
        if grid_collection:
            grid_collection.name = obj.name
    if element.is_a("IfcTypeProduct"):
        TypeData.purge()
    element.Name = "/".join(obj.name.split("/")[1:])
    refresh_ui_data()


def color_callback(obj, data):
    if obj.BIMMaterialProperties.ifc_style_id:
        IfcStore.edited_objs.add(obj)


def active_object_callback():
    refresh_ui_data()


def subscribe_to(object, data_path, callback):
    try:
        subscribe_to = object.path_resolve(data_path, False)
    except:
        return
    bpy.msgbus.subscribe_rna(
        key=subscribe_to,
        owner=object,
        args=(
            object,
            data_path,
        ),
        notify=callback,
        options={
            "PERSISTENT",
        },
    )


def refresh_ui_data():
    from blenderbim.bim import modules

    for name, value in modules.items():
        try:
            getattr(value, "data").refresh()
        except AttributeError:
            pass


def purge_module_data():
    from blenderbim.bim import modules

    refresh_ui_data()
    for name, value in modules.items():
        try:
            getattr(getattr(getattr(ifcopenshell.api, name), "data"), "Data").purge()
        except AttributeError:
            pass

        try:
            getattr(value, "prop").purge()
        except AttributeError:
            pass


@persistent
def loadIfcStore(scene):
    IfcStore.purge()
    purge_module_data()
    if not IfcStore.get_file():
        return
    IfcStore.get_schema()
    IfcStore.relink_all_objects()


@persistent
def undo_pre(scene):
    IfcStore.track_undo_redo_stack_object_map()


@persistent
def undo_post(scene):
    if IfcStore.last_transaction != bpy.context.scene.BIMProperties.last_transaction:
        IfcStore.last_transaction = bpy.context.scene.BIMProperties.last_transaction
        IfcStore.undo()
        purge_module_data()
    IfcStore.track_undo_redo_stack_selected_objects()
    IfcStore.reload_undo_redo_stack_objects()


@persistent
def redo_pre(scene):
    IfcStore.track_undo_redo_stack_object_map()


@persistent
def redo_post(scene):
    if IfcStore.last_transaction != bpy.context.scene.BIMProperties.last_transaction:
        IfcStore.last_transaction = bpy.context.scene.BIMProperties.last_transaction
        IfcStore.redo()
        purge_module_data()
    IfcStore.track_undo_redo_stack_selected_objects()
    IfcStore.reload_undo_redo_stack_objects()


@persistent
def ensureIfcExported(scene):
    if IfcStore.get_file() and not bpy.context.scene.BIMProperties.ifc_file:
        bpy.ops.export_ifc.bim("INVOKE_DEFAULT")


def get_application(ifc):
    # TODO: cache this for even faster application retrieval. It honestly makes a difference on long scripts.
    version = get_application_version()
    for element in ifc.by_type("IfcApplication"):
        if element.ApplicationIdentifier == "BlenderBIM" and element.Version == version:
            return element
    return ifcopenshell.api.run(
        "owner.add_application",
        ifc,
        version=version,
        application_full_name="BlenderBIM Add-on",
        application_identifier="BlenderBIM",
    )


def get_application_version():
    return ".".join(
        [
            str(x)
            for x in [
                addon.bl_info.get("version", (-1, -1, -1))
                for addon in addon_utils.modules()
                if addon.bl_info["name"] == "BlenderBIM"
            ][0]
        ]
    )


@persistent
def setDefaultProperties(scene):
    global global_subscription_owner
    active_object_key = bpy.types.LayerObjects, "active"
    bpy.msgbus.subscribe_rna(
        key=active_object_key, owner=global_subscription_owner, args=(), notify=active_object_callback
    )
    ifcopenshell.api.owner.settings.get_user = lambda ifc: core_owner.get_user(tool.Owner)
    ifcopenshell.api.owner.settings.get_application = get_application
    # TODO: Move to drawing module
    if len(bpy.context.scene.DocProperties.drawing_styles) == 0:
        drawing_style = bpy.context.scene.DocProperties.drawing_styles.add()
        drawing_style.name = "Technical"
        drawing_style.render_type = "VIEWPORT"
        drawing_style.raster_style = json.dumps(
            {
                RasterStyleProperty.WORLD_COLOR.value: (1, 1, 1),
                RasterStyleProperty.RENDER_ENGINE.value: "BLENDER_WORKBENCH",
                RasterStyleProperty.RENDER_TRANSPARENT.value: False,
                RasterStyleProperty.SHADING_SHOW_OBJECT_OUTLINE.value: True,
                RasterStyleProperty.SHADING_SHOW_CAVITY.value: False,
                RasterStyleProperty.SHADING_CAVITY_TYPE.value: "BOTH",
                RasterStyleProperty.SHADING_CURVATURE_RIDGE_FACTOR.value: 1,
                RasterStyleProperty.SHADING_CURVATURE_VALLEY_FACTOR.value: 1,
                RasterStyleProperty.VIEW_TRANSFORM.value: "Standard",
                RasterStyleProperty.SHADING_LIGHT.value: "FLAT",
                RasterStyleProperty.SHADING_COLOR_TYPE.value: "SINGLE",
                RasterStyleProperty.SHADING_SINGLE_COLOR.value: (1, 1, 1),
                RasterStyleProperty.SHADING_SHOW_SHADOWS.value: False,
                RasterStyleProperty.SHADING_SHADOW_INTENSITY.value: 0.5,
                RasterStyleProperty.DISPLAY_LIGHT_DIRECTION.value: (0.5, 0.5, 0.5),
                RasterStyleProperty.VIEW_USE_CURVE_MAPPING.value: False,
                RasterStyleProperty.OVERLAY_SHOW_WIREFRAMES.value: True,
                RasterStyleProperty.OVERLAY_WIREFRAME_THRESHOLD.value: 0,
                RasterStyleProperty.OVERLAY_SHOW_FLOOR.value: False,
                RasterStyleProperty.OVERLAY_SHOW_AXIS_X.value: False,
                RasterStyleProperty.OVERLAY_SHOW_AXIS_Y.value: False,
                RasterStyleProperty.OVERLAY_SHOW_AXIS_Z.value: False,
                RasterStyleProperty.OVERLAY_SHOW_OBJECT_ORIGINS.value: False,
                RasterStyleProperty.OVERLAY_SHOW_RELATIONSHIP_LINES.value: False,
            }
        )
        drawing_style = bpy.context.scene.DocProperties.drawing_styles.add()
        drawing_style.name = "Shaded"
        drawing_style.render_type = "VIEWPORT"
        drawing_style.raster_style = json.dumps(
            {
                RasterStyleProperty.WORLD_COLOR.value: (1, 1, 1),
                RasterStyleProperty.RENDER_ENGINE.value: "BLENDER_WORKBENCH",
                RasterStyleProperty.RENDER_TRANSPARENT.value: False,
                RasterStyleProperty.SHADING_SHOW_OBJECT_OUTLINE.value: True,
                RasterStyleProperty.SHADING_SHOW_CAVITY.value: True,
                RasterStyleProperty.SHADING_CAVITY_TYPE.value: "BOTH",
                RasterStyleProperty.SHADING_CURVATURE_RIDGE_FACTOR.value: 1,
                RasterStyleProperty.SHADING_CURVATURE_VALLEY_FACTOR.value: 1,
                RasterStyleProperty.VIEW_TRANSFORM.value: "Standard",
                RasterStyleProperty.SHADING_LIGHT.value: "STUDIO",
                RasterStyleProperty.SHADING_COLOR_TYPE.value: "MATERIAL",
                RasterStyleProperty.SHADING_SINGLE_COLOR.value: (1, 1, 1),
                RasterStyleProperty.SHADING_SHOW_SHADOWS.value: True,
                RasterStyleProperty.SHADING_SHADOW_INTENSITY.value: 0.5,
                RasterStyleProperty.DISPLAY_LIGHT_DIRECTION.value: (0.5, 0.5, 0.5),
                RasterStyleProperty.VIEW_USE_CURVE_MAPPING.value: False,
                RasterStyleProperty.OVERLAY_SHOW_WIREFRAMES.value: False,
                RasterStyleProperty.OVERLAY_WIREFRAME_THRESHOLD.value: 0,
                RasterStyleProperty.OVERLAY_SHOW_FLOOR.value: False,
                RasterStyleProperty.OVERLAY_SHOW_AXIS_X.value: False,
                RasterStyleProperty.OVERLAY_SHOW_AXIS_Y.value: False,
                RasterStyleProperty.OVERLAY_SHOW_AXIS_Z.value: False,
                RasterStyleProperty.OVERLAY_SHOW_OBJECT_ORIGINS.value: False,
                RasterStyleProperty.OVERLAY_SHOW_RELATIONSHIP_LINES.value: False,
            }
        )
        drawing_style = bpy.context.scene.DocProperties.drawing_styles.add()
        drawing_style.name = "Blender Default"
        drawing_style.render_type = "DEFAULT"
        bpy.ops.bim.save_drawing_style(index="2")
