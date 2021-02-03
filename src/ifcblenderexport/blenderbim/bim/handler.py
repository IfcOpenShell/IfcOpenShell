import bpy
import json
import blenderbim.bim.decoration as decoration
from bpy.app.handlers import persistent
from blenderbim.bim.ifc import IfcStore


@persistent
def loadIfcStore(scene):
    IfcStore.file = None
    IfcStore.schema = None
    props = bpy.context.scene.BIMProperties
    IfcStore.id_map = {int(k): bpy.data.objects.get(v) for k, v in json.loads(props.id_map).items()} if props.id_map else {}
    IfcStore.guid_map = (
        {k: bpy.data.objects.get(v) for k, v in json.loads(props.guid_map).items()} if props.id_map else {}
    )

    # Purge data cache
    from blenderbim.bim import modules
    for module in modules.values():
        if not module:
            continue
        try:
            getattr(getattr(module, 'data'), 'Data').purge()
        except AttributeError:
            pass


@persistent
def storeIdMap(scene):
    bpy.context.scene.BIMProperties.id_map = json.dumps({k: v.name for k, v in IfcStore.id_map.items()})
    bpy.context.scene.BIMProperties.guid_map = json.dumps({k: v.name for k, v in IfcStore.guid_map.items()})


@persistent
def setDefaultProperties(scene):
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
