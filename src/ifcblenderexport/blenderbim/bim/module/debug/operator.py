import bpy
import logging
import ifcopenshell
import blenderbim.bim.import_ifc as import_ifc
from blenderbim.bim.ifc import IfcStore


class ProfileImportIFC(bpy.types.Operator):
    bl_idname = "bim.profile_import_ifc"
    bl_label = "Profile Import IFC"

    def execute(self, context):
        import cProfile
        import pstats

        cProfile.run(
            f"import bpy; bpy.ops.import_ifc.bim(filepath='{bpy.context.scene.BIMProperties.ifc_file}')", "blender.prof"
        )
        p = pstats.Stats("blender.prof")
        p.sort_stats("cumulative").print_stats(50)
        return {"FINISHED"}


class CreateAllShapes(bpy.types.Operator):
    bl_idname = "bim.create_all_shapes"
    bl_label = "Create All Shapes"

    def execute(self, context):
        self.file = IfcStore.get_file()
        elements = self.file.by_type("IfcElement") + self.file.by_type("IfcSpace")
        total = len(elements)
        settings = ifcopenshell.geom.settings()
        failures = []
        excludes = () # For the developer to debug with
        for i, element in enumerate(elements):
            if element.GlobalId in excludes:
                continue
            print(f'{i}/{total}:', element)
            try:
                shape = ifcopenshell.geom.create_shape(settings, element)
                print("Success", len(shape.geometry.verts), len(shape.geometry.edges), len(shape.geometry.faces))
            except:
                failures.append(element)
                print('***** FAILURE *****')
        print('Failures:')
        for failure in failures:
            print(failure)
        return {"FINISHED"}


class CreateShapeFromStepId(bpy.types.Operator):
    bl_idname = "bim.create_shape_from_step_id"
    bl_label = "Create Shape From STEP ID"

    def execute(self, context):
        logger = logging.getLogger("ImportIFC")
        self.ifc_import_settings = import_ifc.IfcImportSettings.factory(bpy.context, IfcStore.path, logger)
        self.file = IfcStore.get_file()
        element = self.file.by_id(int(bpy.context.scene.BIMDebugProperties.step_id))
        settings = ifcopenshell.geom.settings()
        # settings.set(settings.INCLUDE_CURVES, True)
        shape = ifcopenshell.geom.create_shape(settings, element)
        ifc_importer = import_ifc.IfcImporter(self.ifc_import_settings)
        ifc_importer.file = self.file
        mesh = ifc_importer.create_mesh(element, shape)
        obj = bpy.data.objects.new("Debug", mesh)
        bpy.context.scene.collection.objects.link(obj)
        return {"FINISHED"}


class SelectHighPolygonMeshes(bpy.types.Operator):
    bl_idname = "bim.select_high_polygon_meshes"
    bl_label = "Select High Polygon Meshes"

    def execute(self, context):
        results = {}
        for obj in bpy.data.objects:
            if not isinstance(obj.data, bpy.types.Mesh) or len(obj.data.polygons) < int(
                bpy.context.scene.BIMDebugProperties.number_of_polygons
            ):
                continue
            try:
                obj.select_set(True)
            except:
                # If it is not in the view layer
                pass
        return {"FINISHED"}


class RewindInspector(bpy.types.Operator):
    bl_idname = "bim.rewind_inspector"
    bl_label = "Rewind Inspector"

    def execute(self, context):
        props = bpy.context.scene.BIMDebugProperties
        total_breadcrumbs = len(props.step_id_breadcrumb)
        if total_breadcrumbs < 2:
            return {"FINISHED"}
        previous_step_id = int(props.step_id_breadcrumb[total_breadcrumbs - 2].name)
        props.step_id_breadcrumb.remove(total_breadcrumbs - 1)
        props.step_id_breadcrumb.remove(total_breadcrumbs - 2)
        bpy.ops.bim.inspect_from_step_id(step_id=previous_step_id)
        return {"FINISHED"}


class InspectFromStepId(bpy.types.Operator):
    bl_idname = "bim.inspect_from_step_id"
    bl_label = "Inspect From STEP ID"
    step_id: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        bpy.context.scene.BIMDebugProperties.active_step_id = self.step_id
        crumb = bpy.context.scene.BIMDebugProperties.step_id_breadcrumb.add()
        crumb.name = str(self.step_id)
        element = self.file.by_id(self.step_id)
        while len(bpy.context.scene.BIMDebugProperties.attributes) > 0:
            bpy.context.scene.BIMDebugProperties.attributes.remove(0)
        while len(bpy.context.scene.BIMDebugProperties.inverse_attributes) > 0:
            bpy.context.scene.BIMDebugProperties.inverse_attributes.remove(0)
        for key, value in element.get_info().items():
            self.add_attribute(bpy.context.scene.BIMDebugProperties.attributes, key, value)
        for key in dir(element):
            if (
                not key[0].isalpha()
                or key[0] != key[0].upper()
                or key in element.get_info()
                or not getattr(element, key)
            ):
                continue
            self.add_attribute(bpy.context.scene.BIMDebugProperties.inverse_attributes, key, getattr(element, key))
        return {"FINISHED"}

    def add_attribute(self, prop, key, value):
        if isinstance(value, tuple) and len(value) < 10:
            for i, item in enumerate(value):
                self.add_attribute(prop, key + f"[{i}]", item)
            return
        elif isinstance(value, tuple) and len(value) >= 10:
            key = key + "({})".format(len(value))
        new = prop.add()
        new.name = key
        new.string_value = str(value)
        if isinstance(value, ifcopenshell.entity_instance):
            new.int_value = int(value.id())


class InspectFromObject(bpy.types.Operator):
    bl_idname = "bim.inspect_from_object"
    bl_label = "Inspect From Object"

    def execute(self, context):
        ifc_definition_id = bpy.context.active_object.BIMObjectProperties.ifc_definition_id
        if not ifc_definition_id:
            return {"FINISHED"}
        bpy.ops.bim.inspect_from_step_id(step_id=ifc_definition_id)
        return {"FINISHED"}
