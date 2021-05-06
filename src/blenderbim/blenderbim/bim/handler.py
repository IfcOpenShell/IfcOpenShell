import bpy
import json
import addon_utils
import blenderbim.bim.decoration as decoration
import ifcopenshell.api.owner.settings
from bpy.app.handlers import persistent
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.attribute.data import Data as AttributeData
from ifcopenshell.api.type.data import Data as TypeData


def mode_callback(obj, data):
    for obj in bpy.context.selected_objects:
        if (
            obj.mode != "EDIT"
            or not obj.data
            or not isinstance(obj.data, bpy.types.Mesh)
            or not obj.data.BIMMeshProperties.ifc_definition_id
            or not bpy.context.scene.BIMProjectProperties.is_authoring
        ):
            return
        representation = IfcStore.get_file().by_id(obj.data.BIMMeshProperties.ifc_definition_id)
        if representation.RepresentationType == "Tessellation" or representation.RepresentationType == "Brep":
            IfcStore.edited_objs.add(obj.name)


def name_callback(obj, data):
    # Blender material names are up to 63 UTF-8 bytes
    if not obj.BIMObjectProperties.ifc_definition_id or "/" not in obj.name or len(bytes(obj.name, "utf-8")) >= 63:
        return
    element = IfcStore.get_file().by_id(obj.BIMObjectProperties.ifc_definition_id)
    if not element.is_a("IfcRoot"):
        return
    if element.is_a("IfcSpatialStructureElement") or (hasattr(element, "IsDecomposedBy") and element.IsDecomposedBy):
        collection = obj.users_collection[0]
        collection.name = obj.name
    if element.is_a("IfcTypeProduct"):
        TypeData.purge()
    element.Name = "/".join(obj.name.split("/")[1:])
    AttributeData.load(IfcStore.get_file(), obj.BIMObjectProperties.ifc_definition_id)


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
    IfcStore.get_schema()
    [
        IfcStore.link_element(ifc_file.by_id(o.BIMObjectProperties.ifc_definition_id), o)
        for o in bpy.data.objects
        if o.BIMObjectProperties.ifc_definition_id
    ]
    purge_module_data()


@persistent
def ensureIfcExported(scene):
    if IfcStore.get_file() and not bpy.context.scene.BIMProperties.ifc_file:
        bpy.ops.export_ifc.bim("INVOKE_DEFAULT")


def get_application(ifc):
    version = get_application_version()
    for element in ifc.by_type("IfcApplication"):
        if element.ApplicationIdentifier == "BlenderBIM" and element.Version == version:
            return element
    return ifc.create_entity(
        "IfcApplication",
        **{
            "ApplicationDeveloper": create_application_organisation(ifc),
            "Version": get_application_version(),
            "ApplicationFullName": "BlenderBIM Add-on",
            "ApplicationIdentifier": "BlenderBIM",
        },
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


def create_application_organisation(ifc):
    return ifc.create_entity(
        "IfcOrganization",
        **{
            "Name": "IfcOpenShell",
            "Description": "IfcOpenShell is an open source (LGPL) software library that helps users and software developers to work with the IFC file format.",
            "Roles": [ifc.create_entity("IfcActorRole", **{"Role": "USERDEFINED", "UserDefinedRole": "CONTRIBUTOR"})],
            "Addresses": [
                ifc.create_entity(
                    "IfcTelecomAddress",
                    **{
                        "Purpose": "USERDEFINED",
                        "UserDefinedPurpose": "WEBPAGE",
                        "Description": "The main webpage of the software collection.",
                        "WWWHomePageURL": "https://ifcopenshell.org",
                    },
                ),
                ifc.create_entity(
                    "IfcTelecomAddress",
                    **{
                        "Purpose": "USERDEFINED",
                        "UserDefinedPurpose": "WEBPAGE",
                        "Description": "The BlenderBIM Add-on webpage of the software collection.",
                        "WWWHomePageURL": "https://blenderbim.org",
                    },
                ),
                ifc.create_entity(
                    "IfcTelecomAddress",
                    **{
                        "Purpose": "USERDEFINED",
                        "UserDefinedPurpose": "REPOSITORY",
                        "Description": "The source code repository of the software collection.",
                        "WWWHomePageURL": "https://github.com/IfcOpenShell/IfcOpenShell.git",
                    },
                ),
            ],
        },
    )


@persistent
def setDefaultProperties(scene):
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


@persistent
def toggleDecorationsOnLoad(*args):
    toggle = bpy.context.scene.DocProperties.should_draw_decorations
    if toggle:
        decoration.DecorationsHandler.install(bpy.context)
    else:
        decoration.DecorationsHandler.uninstall()
