# Check if we are running in Blender before loading, to allow for multiprocessing
import sys

bpy = sys.modules.get("bpy")

if bpy is not None:
    import bpy
    import importlib
    from . import handler, ui, prop, operator

    modules = {
        "project": None,
        "search": None,
        "bcf": None,
        "root": None,
        "unit": None,
        "model": None,
        "georeference": None,
        "context": None,
        "drawing": None,
        "attribute": None,
        "type": None,
        "spatial": None,
        "void": None,
        "aggregate": None,
        "geometry": None,
        "cobie": None,
        "resource": None,
        "cost": None,
        "sequence": None,
        "group": None,
        "structural": None,
        "boundary": None,
        "material": None,
        "style": None,
        "layer": None,
        "owner": None,
        "pset": None,
        "qto": None,
        "classification": None,
        "constraint": None,
        "document": None,
        "pset_template": None,
        "clash": None,
        "csv": None,
        "bimtester": None,
        "diff": None,
        "patch": None,
        "covetool": None,
        "augin": None,
        "debug": None,
    }

    for name in modules.keys():
        modules[name] = importlib.import_module(f"blenderbim.bim.module.{name}")

    classes = [
        operator.OpenUri,
        operator.SelectDataDir,
        operator.SelectSchemaDir,
        operator.SelectIfcFile,
        operator.ExportIFC,
        operator.ImportIFC,
        operator.OpenUpstream,
        operator.AddSectionPlane,
        operator.RemoveSectionPlane,
        operator.ReloadIfcFile,
        operator.AddIfcFile,
        operator.RemoveIfcFile,
        operator.SetOverrideColour,
        operator.SetViewportShadowFromSun,
        operator.LinkIfc,
        operator.SnapSpacesTogether,
        prop.StrProperty,
        prop.Attribute,
        prop.BIMProperties,
        prop.IfcParameter,
        prop.PsetQto,
        prop.GlobalId,
        prop.BIMObjectProperties,
        prop.BIMMaterialProperties,
        prop.BIMMeshProperties,
        ui.BIM_PT_section_plane,
        ui.BIM_UL_generic,
        ui.BIM_UL_topics,
        ui.BIM_ADDON_preferences,
    ]

    for module in modules.values():
        classes.extend(module.classes)

    def menu_func_export(self, context):
        self.layout.operator(operator.ExportIFC.bl_idname, text="Industry Foundation Classes (.ifc/.ifczip/.ifcjson)")

    def menu_func_import(self, context):
        self.layout.operator(operator.ImportIFC.bl_idname, text="Industry Foundation Classes (.ifc/.ifczip/.ifcxml)")

    def on_register(scene):
        handler.setDefaultProperties(scene)
        bpy.app.handlers.depsgraph_update_post.remove(on_register)

    def register():
        for cls in classes:
            bpy.utils.register_class(cls)
        bpy.app.handlers.depsgraph_update_post.append(on_register)
        bpy.app.handlers.undo_pre.append(handler.undo_pre)
        bpy.app.handlers.undo_post.append(handler.undo_post)
        bpy.app.handlers.redo_pre.append(handler.redo_pre)
        bpy.app.handlers.redo_post.append(handler.redo_post)
        bpy.app.handlers.load_post.append(handler.setDefaultProperties)
        bpy.app.handlers.load_post.append(handler.loadIfcStore)
        bpy.app.handlers.save_pre.append(handler.ensureIfcExported)
        bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
        bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
        bpy.types.Scene.BIMProperties = bpy.props.PointerProperty(type=prop.BIMProperties)
        bpy.types.Object.BIMObjectProperties = bpy.props.PointerProperty(type=prop.BIMObjectProperties)
        bpy.types.Material.BIMObjectProperties = bpy.props.PointerProperty(type=prop.BIMObjectProperties)
        bpy.types.Collection.BIMObjectProperties = bpy.props.PointerProperty(
            type=prop.BIMObjectProperties
        )  # Check if we need this
        bpy.types.Material.BIMMaterialProperties = bpy.props.PointerProperty(type=prop.BIMMaterialProperties)
        bpy.types.Mesh.BIMMeshProperties = bpy.props.PointerProperty(type=prop.BIMMeshProperties)
        bpy.types.Curve.BIMMeshProperties = bpy.props.PointerProperty(type=prop.BIMMeshProperties)
        bpy.types.Camera.BIMMeshProperties = bpy.props.PointerProperty(type=prop.BIMMeshProperties)
        bpy.types.PointLight.BIMMeshProperties = bpy.props.PointerProperty(type=prop.BIMMeshProperties)
        bpy.types.SCENE_PT_unit.append(ui.ifc_units)

        for module in modules.values():
            module.register()

    def unregister():
        for cls in reversed(classes):
            bpy.utils.unregister_class(cls)
        bpy.app.handlers.load_post.remove(handler.setDefaultProperties)
        bpy.app.handlers.load_post.remove(handler.loadIfcStore)
        bpy.app.handlers.save_pre.remove(handler.ensureIfcExported)
        bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
        bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
        del bpy.types.Scene.BIMProperties
        del bpy.types.Object.BIMObjectProperties
        del bpy.types.Material.BIMObjectProperties
        del bpy.types.Collection.BIMObjectProperties  # Check if we need this
        del bpy.types.Material.BIMMaterialProperties
        del bpy.types.Mesh.BIMMeshProperties
        del bpy.types.Curve.BIMMeshProperties
        del bpy.types.Camera.BIMMeshProperties
        del bpy.types.PointLight.BIMMeshProperties
        bpy.types.SCENE_PT_unit.remove(ui.ifc_units)

        for module in reversed(list(modules.values())):
            module.unregister()
