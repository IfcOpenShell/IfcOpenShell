import bpy
import json
import addon_utils
import ifcopenshell.api.owner.settings
from bpy.app.handlers import persistent
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.attribute.data import Data as AttributeData
from ifcopenshell.api.type.data import Data as TypeData


global_subscription_owner = object()


def mode_callback(obj, data):
    objects = bpy.context.selected_objects
    if bpy.context.active_object:
        objects += [bpy.context.active_object]
    for obj in objects:
        if (
            obj.mode != "EDIT"
            or not obj.data
            or not isinstance(obj.data, (bpy.types.Mesh, bpy.types.Curve, bpy.types.TextCurve))
            or not obj.BIMObjectProperties.ifc_definition_id
            or not bpy.context.scene.BIMProjectProperties.is_authoring
        ):
            return
        if obj.data.BIMMeshProperties.ifc_definition_id:
            representation = IfcStore.get_file().by_id(obj.data.BIMMeshProperties.ifc_definition_id)
            if representation.RepresentationType in ["Tessellation", "Brep", "Annotation2D"]:
                IfcStore.edited_objs.add(obj)
        elif IfcStore.get_file().by_id(obj.BIMObjectProperties.ifc_definition_id).is_a("IfcGridAxis"):
            IfcStore.edited_objs.add(obj)


def name_callback(obj, data):
    try:
        oby.type
    except:
        return  # In case the object RNA is gone during an undo / redo operation
    # Blender material names are up to 63 UTF-8 bytes
    if not obj.BIMObjectProperties.ifc_definition_id or "/" not in obj.name or len(bytes(obj.name, "utf-8")) >= 63:
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
    AttributeData.load(IfcStore.get_file(), obj.BIMObjectProperties.ifc_definition_id)


def active_object_callback():
    obj = bpy.context.active_object
    for obj in bpy.context.selected_objects:
        if not obj.BIMObjectProperties.ifc_definition_id:
            continue
        stored_obj = IfcStore.get_element(obj.BIMObjectProperties.ifc_definition_id)
        if stored_obj and stored_obj != obj:
            bpy.ops.bim.copy_class(obj=obj.name)


def subscribe_to(object, data_path, callback):
    subscribe_to = object.path_resolve(data_path, False)
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


def purge_module_data():
    from blenderbim.bim import modules

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
    ifc_file = IfcStore.get_file()
    if not ifc_file:
        return
    IfcStore.get_schema()
    IfcStore.reload_linked_elements()
    purge_module_data()


@persistent
def undo_pre(scene):
    IfcStore.update_undo_redo_stack_objects()


@persistent
def undo_post(scene):
    if IfcStore.last_transaction != bpy.context.scene.BIMProperties.last_transaction:
        IfcStore.last_transaction = bpy.context.scene.BIMProperties.last_transaction
        IfcStore.undo()
        purge_module_data()
    IfcStore.update_undo_redo_stack_objects()
    IfcStore.reload_linked_elements(objects=[bpy.data.objects.get(o) for o in IfcStore.undo_redo_stack_objects])


@persistent
def redo_pre(scene):
    IfcStore.update_undo_redo_stack_objects()


@persistent
def redo_post(scene):
    if IfcStore.last_transaction != bpy.context.scene.BIMProperties.last_transaction:
        IfcStore.last_transaction = bpy.context.scene.BIMProperties.last_transaction
        IfcStore.redo()
        purge_module_data()
    IfcStore.update_undo_redo_stack_objects()
    IfcStore.reload_linked_elements(objects=[bpy.data.objects.get(o) for o in IfcStore.undo_redo_stack_objects])


@persistent
def ensureIfcExported(scene):
    if IfcStore.get_file() and not bpy.context.scene.BIMProperties.ifc_file:
        bpy.ops.export_ifc.bim("INVOKE_DEFAULT")


def get_application(ifc):
    version = get_application_version()
    for element in ifc.by_type("IfcApplication"):
        if element.ApplicationIdentifier == "BlenderBIM" and element.Version == version:
            return element
    return ifcopenshell.api.run(
        "owner.add_application",
        ifc,
        version=get_application_version(),
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
    ifcopenshell.api.owner.settings.get_person = (
        lambda ifc: ifc.by_id(int(bpy.context.scene.BIMOwnerProperties.user_person))
        if bpy.context.scene.BIMOwnerProperties.user_person
        else None
    )
    ifcopenshell.api.owner.settings.get_organisation = (
        lambda ifc: ifc.by_id(int(bpy.context.scene.BIMOwnerProperties.user_organisation))
        if bpy.context.scene.BIMOwnerProperties.user_organisation
        else None
    )
    ifcopenshell.api.owner.settings.get_application = get_application
    if len(bpy.context.scene.DocProperties.drawing_styles) == 0:
        drawing_style = bpy.context.scene.DocProperties.drawing_styles.add()
        drawing_style.name = "Technical"
        drawing_style.render_type = "VIEWPORT"
        drawing_style.raster_style = json.dumps(
            {
                "bpy.data.worlds[0].color": (1, 1, 1),
                "bpy.context.scene.render.engine": "BLENDER_WORKBENCH",
                "bpy.context.scene.render.film_transparent": False,
                "bpy.context.scene.display.shading.show_object_outline": True,
                "bpy.context.scene.display.shading.show_cavity": False,
                "bpy.context.scene.display.shading.cavity_type": "BOTH",
                "bpy.context.scene.display.shading.curvature_ridge_factor": 1,
                "bpy.context.scene.display.shading.curvature_valley_factor": 1,
                "bpy.context.scene.view_settings.view_transform": "Standard",
                "bpy.context.scene.display.shading.light": "FLAT",
                "bpy.context.scene.display.shading.color_type": "SINGLE",
                "bpy.context.scene.display.shading.single_color": (1, 1, 1),
                "bpy.context.scene.display.shading.show_shadows": False,
                "bpy.context.scene.display.shading.shadow_intensity": 0.5,
                "bpy.context.scene.display.light_direction": (0.5, 0.5, 0.5),
                "bpy.context.scene.view_settings.use_curve_mapping": False,
                "space.overlay.show_wireframes": True,
                "space.overlay.wireframe_threshold": 0,
                "space.overlay.show_floor": False,
                "space.overlay.show_axis_x": False,
                "space.overlay.show_axis_y": False,
                "space.overlay.show_axis_z": False,
                "space.overlay.show_object_origins": False,
                "space.overlay.show_relationship_lines": False,
            }
        )
        drawing_style = bpy.context.scene.DocProperties.drawing_styles.add()
        drawing_style.name = "Shaded"
        drawing_style.render_type = "VIEWPORT"
        drawing_style.raster_style = json.dumps(
            {
                "bpy.data.worlds[0].color": (1, 1, 1),
                "bpy.context.scene.render.engine": "BLENDER_WORKBENCH",
                "bpy.context.scene.render.film_transparent": False,
                "bpy.context.scene.display.shading.show_object_outline": True,
                "bpy.context.scene.display.shading.show_cavity": True,
                "bpy.context.scene.display.shading.cavity_type": "BOTH",
                "bpy.context.scene.display.shading.curvature_ridge_factor": 1,
                "bpy.context.scene.display.shading.curvature_valley_factor": 1,
                "bpy.context.scene.view_settings.view_transform": "Standard",
                "bpy.context.scene.display.shading.light": "STUDIO",
                "bpy.context.scene.display.shading.color_type": "MATERIAL",
                "bpy.context.scene.display.shading.single_color": (1, 1, 1),
                "bpy.context.scene.display.shading.show_shadows": True,
                "bpy.context.scene.display.shading.shadow_intensity": 0.5,
                "bpy.context.scene.display.light_direction": (0.5, 0.5, 0.5),
                "bpy.context.scene.view_settings.use_curve_mapping": False,
                "space.overlay.show_wireframes": True,
                "space.overlay.wireframe_threshold": 0,
                "space.overlay.show_floor": False,
                "space.overlay.show_axis_x": False,
                "space.overlay.show_axis_y": False,
                "space.overlay.show_axis_z": False,
                "space.overlay.show_object_origins": False,
                "space.overlay.show_relationship_lines": False,
            }
        )
        drawing_style = bpy.context.scene.DocProperties.drawing_styles.add()
        drawing_style.name = "Blender Default"
        drawing_style.render_type = "DEFAULT"
        bpy.ops.bim.save_drawing_style(index="2")
