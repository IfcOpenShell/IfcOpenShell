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

import os
import bpy
import ifcopenshell.util.element
import ifcopenshell.util.representation
import ifcopenshell.util.unit
import ifcopenshell.api.owner.settings
import bonsai.bim
import bonsai.tool as tool
import weakref
from bpy.app.handlers import persistent
from bonsai.bim.ifc import IfcStore
from bonsai.bim.module.model.data import AuthoringData
from bonsai.bim.module.aggregate.decorator import AggregateDecorator
from bonsai.bim.module.georeference.decorator import GeoreferenceDecorator
from bonsai.bim.module.model.decorator import WallAxisDecorator, SlabDirectionDecorator
from bonsai.bim.module.nest.decorator import NestDecorator
from mathutils import Vector
from math import cos
from typing import Union
from collections.abc import Callable


cwd = os.path.dirname(os.path.realpath(__file__))
global_subscription_owner = object()


def name_callback(obj: Union[bpy.types.Object, bpy.types.Material], data: str) -> None:
    try:
        obj.name
    except:
        # The object is invalid but somehow still has a callback. Clear all
        # msgbus subscriptions to prevent useless further triggers.
        bpy.msgbus.clear_by_owner(obj)
        return  # In case the object RNA is gone during an undo / redo operation
    # Blender names are up to 63 UTF-8 bytes
    if len(bytes(obj.name, "utf-8")) >= 63:
        return

    if isinstance(obj, bpy.types.Material):
        props = tool.Style.get_material_style_props(obj)
        if ifc_definition_id := props.ifc_definition_id:
            if props.is_renaming:
                props.is_renaming = False
                return
            tool.Ifc.get().by_id(ifc_definition_id).Name = obj.name
            refresh_ui_data()
        return

    props = tool.Blender.get_object_bim_props(obj)
    if not props.ifc_definition_id:
        return

    if props.is_renaming:
        props.is_renaming = False
        return

    element = tool.Ifc.get().by_id(props.ifc_definition_id)
    if "/" in obj.name:
        object_name = obj.name
        element_name = obj.name.split("/", 1)[1]
    else:
        element_name = obj.name
        object_name = element.is_a() + f"/{element_name}"
        obj.name = object_name  # NOTE: doesn't trigger infinite recursion

    if element.is_a("IfcGridAxis"):
        element.AxisTag = object_name.split("/")[1]
        refresh_ui_data()

    if not element.is_a("IfcRoot"):
        return
    element.Name = element_name
    if props.collection:
        props.collection.name = object_name
    refresh_ui_data()


def active_object_callback():
    refresh_ui_data()
    update_bim_tool_props()
    tool.Geometry.sync_item_positions()


def update_bim_tool_props():
    """update BIM Tools props (such as extrusion_depth, length and x_angle) when active object changes"""
    obj = bpy.context.active_object

    # bunch of checks to see if we're in a valid state
    if not obj:
        return
    mode = bpy.context.mode
    current_tool = bpy.context.workspace.tools.from_space_view3d_mode(mode)
    if not current_tool or current_tool.idname not in tool.Blender.get_list_of_tools():
        return
    element = tool.Ifc.get_entity(obj)
    if not element:
        return

    props = tool.Model.get_model_props()
    aprops = tool.Drawing.get_annotation_props()
    TOOLS_TO_CLASSES_MAP = tool.Blender.get_tools_to_classes_map()
    is_annotation_tool = current_tool.idname == "bim.annotation_tool"
    if element.is_a("IfcTypeProduct") or element.is_a("IfcProduct"):
        element_type = ifcopenshell.util.element.get_type(element)
        if element_type:
            is_bim_tool = current_tool.idname == "bim.bim_tool"

            if is_annotation_tool and (object_type := tool.Drawing.get_annotation_type_object_type(element_type)):
                aprops.object_type = object_type
                aprops.relating_type_id = str(element_type.id())
                return

            if is_bim_tool:
                props.ifc_class = element_type.is_a()

            if is_bim_tool or TOOLS_TO_CLASSES_MAP.get(current_tool.idname) == element_type.is_a():
                props.relating_type_id = str(element_type.id())

    if is_annotation_tool:
        return

    representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
    if not representation:
        return

    extrusion = tool.Model.get_extrusion(representation)
    if not extrusion:
        return

    def get_x_angle(extrusion: ifcopenshell.entity_instance) -> float:
        x, y, z = extrusion.ExtrudedDirection.DirectionRatios
        x_angle = Vector((0, 1)).angle_signed(Vector((y, z)))
        return x_angle

    si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
    if not AuthoringData.is_loaded:
        AuthoringData.load()

    if AuthoringData.data["active_material_usage"] == "LAYER2":
        x_angle = get_x_angle(extrusion)
        axis = tool.Model.get_wall_axis(obj)["reference"]
        props.extrusion_depth = abs(extrusion.Depth * si_conversion * cos(x_angle))
        props.length = (axis[1] - axis[0]).length
        props.x_angle = x_angle

    elif AuthoringData.data["active_material_usage"] == "LAYER3":
        x_angle = get_x_angle(extrusion)
        props.x_angle = x_angle

    elif AuthoringData.data["active_material_usage"] == "PROFILE":
        props.extrusion_depth = extrusion.Depth * si_conversion


def active_material_index_callback(obj, data):
    from bonsai.bim.module.style.data import BlenderMaterialStyleData

    # Simple UI for showing whether blender material is linked to IFC style,
    # no need to update the entire UI.
    BlenderMaterialStyleData.is_loaded = False


def subscribe_to(obj: bpy.types.ID, data_path: str, callback: Callable[[bpy.types.ID, str], None]):
    try:
        subscribe_to = obj.path_resolve(data_path, False)
    except:
        return
    bpy.msgbus.subscribe_rna(
        key=subscribe_to,
        owner=obj,
        args=(
            obj,
            data_path,
        ),
        notify=callback,
        options={
            "PERSISTENT",
        },
    )


def refresh_ui_data():
    """Refresh cached UI data.

    Note that calling non-ifc-operators by itself doesn't refresh the UI data
    and it need to be refreshed manually if needed.
    """
    from bonsai.bim import modules
    import bonsai.bim.ui

    bonsai.bim.ui.refresh()

    for name, value in modules.items():
        try:
            getattr(value, "data").refresh()
        except AttributeError:
            pass

        # TODO: deprecate prop purge functions and refactor into data classes.
        try:
            getattr(value, "prop").purge()
        except AttributeError:
            pass

    if isinstance(tool.Ifc.get(), ifcopenshell.sqlite):
        tool.Ifc.get().clear_cache()

    props = tool.Drawing.get_document_props()
    props.should_draw_decorations = props.should_draw_decorations
    if bpy.context.scene.WebProperties.is_connected:
        tool.Web.send_webui_data()


@persistent
def loadIfcStore(scene: bpy.types.Scene) -> None:
    IfcStore.purge()
    refresh_ui_data()
    if not tool.Ifc.get():
        return
    tool.Ifc.schema()
    IfcStore.relink_all_objects()


@persistent
def undo_post(scene: bpy.types.Scene) -> None:
    props = tool.Blender.get_bim_props()
    if IfcStore.last_transaction != props.last_transaction:
        IfcStore.last_transaction = props.last_transaction
        IfcStore.undo(until_key=props.last_transaction)
        refresh_ui_data()
    tool.Ifc.rebuild_element_maps()


@persistent
def redo_post(scene: bpy.types.Scene) -> None:
    props = tool.Blender.get_bim_props()
    if IfcStore.last_transaction != props.last_transaction:
        IfcStore.last_transaction = props.last_transaction
        IfcStore.redo(until_key=props.last_transaction)
        refresh_ui_data()
    tool.Ifc.rebuild_element_maps()


# Cache is important as those entities will be retrieved very often,
# for every IfcOwnerHistory creation or update.
class SettingsCache:
    APPLICATION_ID: Union[int, None] = None
    USER_ID: Union[int, None] = None

    _file: Union[weakref.ReferenceType[ifcopenshell.file], None] = None

    @classmethod
    def get_file(cls) -> Union[ifcopenshell.file, None]:
        if cls._file is None:
            return None
        return cls._file()

    @classmethod
    def set_file(cls, file: ifcopenshell.file) -> None:
        cls._file = weakref.ref(file)


def get_application(ifc: ifcopenshell.file) -> ifcopenshell.entity_instance:
    if SettingsCache.get_file() is ifc and SettingsCache.APPLICATION_ID is not None:
        try:
            app = ifc.by_id(SettingsCache.APPLICATION_ID)
            return app
        except RuntimeError:
            pass

    # Use only main part from the version to avoid flooding advanced users projects with IfcApplications.
    version = tool.Blender.get_bonsai_version().split("-")[0]
    for element in ifc.by_type("IfcApplication"):
        if element.ApplicationIdentifier == "Bonsai" and element.Version == version:
            return element
    application = ifcopenshell.api.owner.add_application(
        ifc,
        version=version,
        application_full_name="Bonsai",
        application_identifier="Bonsai",
    )
    SettingsCache.APPLICATION_ID = application.id()
    SettingsCache.set_file(ifc)
    return application


def get_user(ifc: ifcopenshell.file) -> Union[ifcopenshell.entity_instance, None]:
    # TODO: cache this for even faster application retrieval. It honestly makes a difference on long scripts.
    if SettingsCache.get_file() is ifc and SettingsCache.USER_ID is not None:
        try:
            user = ifc.by_id(SettingsCache.USER_ID)
            return user
        except RuntimeError:
            pass

    if pao := next(iter(ifc.by_type("IfcPersonAndOrganization")), None):
        SettingsCache.USER_ID = pao.id()
        SettingsCache.set_file(ifc)
        return pao
    elif ifc.schema == "IFC2X3":
        if (person := next(iter(ifc.by_type("IfcPerson")), None)) is None:
            person = ifcopenshell.api.owner.add_person(ifc)
        if (organization := next(iter(ifc.by_type("IfcOrganization")), None)) is None:
            organization = ifcopenshell.api.owner.add_organisation(ifc)
        pao = ifcopenshell.api.owner.add_person_and_organisation(ifc, person=person, organisation=organization)
        SettingsCache.USER_ID = pao.id()
        SettingsCache.set_file(ifc)
        return pao


def viewport_shading_changed_callback(area: bpy.types.Area) -> None:
    shading = area.spaces.active.shading.type
    if shading == "RENDERED":
        tool.Style.get_style_props().active_style_type = "External"


def subscribe_to_viewport_shading_changes():
    """Subscribe to changes in viewport shading mode"""
    # NOTE: couldn't find a way to make it work for new areas too
    # it starts working for them after blender restart though
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type != "VIEW_3D":
                continue
            shading = area.spaces.active.shading
            key = shading.path_resolve("type", False)

            bpy.msgbus.subscribe_rna(
                key=key, owner=global_subscription_owner, args=(area,), notify=viewport_shading_changed_callback
            )


@persistent
def load_post(scene):
    global global_subscription_owner
    active_object_key = bpy.types.LayerObjects, "active"
    bpy.msgbus.subscribe_rna(
        key=active_object_key, owner=global_subscription_owner, args=(), notify=active_object_callback
    )

    ifcopenshell.api.owner.settings.get_user = get_user
    ifcopenshell.api.owner.settings.get_application = get_application
    AuthoringData.type_thumbnails = {}

    preferences = tool.Blender.get_addon_preferences()
    if not preferences.should_setup_toolbar:
        tool.Blender.unregister_toolbar()

    if preferences.should_setup_workspace:
        if "BIM" in bpy.data.workspaces:
            if preferences.activate_workspace:
                bpy.context.window.workspace = bpy.data.workspaces["BIM"]
        else:
            bpy.ops.workspace.append_activate(idname="BIM", filepath=os.path.join(cwd, "data", "workspace.blend"))

    # After appending the workspace to ensure BIM viewport is affected.
    subscribe_to_viewport_shading_changes()

    # To improve usability for new users, we hijack the scene properties
    # tab. We override default scene properties panels with our own poll
    # to hide them unless the user has chosen to view Blender properties.
    for panel in tool.Blender.get_scene_panels_list():
        if panel in bonsai.bim.original_scene_panels_polls:
            continue
        tool.Blender.override_scene_panel(panel)
    tool.Blender.setup_tabs()

    if tool.Ifc.get() and bpy.data.is_saved:
        props = tool.Blender.get_bim_props()
        props.has_blend_warning = True

    # Bonsai overlays
    georeference_props = tool.Georeference.get_georeference_props()
    aggregate_props = tool.Aggregate.get_aggregate_props()
    nest_props = tool.Nest.get_nest_props()
    model_props = tool.Model.get_model_props()
    GeoreferenceDecorator.uninstall()
    AggregateDecorator.uninstall()
    NestDecorator.uninstall()
    WallAxisDecorator.uninstall()
    SlabDirectionDecorator.uninstall()
    if georeference_props.should_visualise:
        GeoreferenceDecorator.install(bpy.context)
    if aggregate_props.aggregate_decorator:
        AggregateDecorator.install(bpy.context)
    if nest_props.nest_decorator:
        NestDecorator.install(bpy.context)
    if model_props.show_wall_axis:
        WallAxisDecorator.install(bpy.context)
    if model_props.show_slab_direction:
        SlabDirectionDecorator.install(bpy.context)

    if preferences.should_use_snap and (scene := bpy.context.scene):
        # Snapping is off by default in Blender, but in BIM, it's more useful to be on
        scene.tool_settings.use_snap = True
        # Match default Bonsai snaps
        scene.tool_settings.snap_elements_base = {"EDGE", "EDGE_PERPENDICULAR", "VERTEX", "EDGE_MIDPOINT", "FACE"}
