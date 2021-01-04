import bpy
import blenderbim.bim.module.spatial.assign_container as assign_container
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.spatial.data import Data


class AssignContainer(bpy.types.Operator):
    bl_idname = "bim.assign_container"
    bl_label = "Assign Container"

    def execute(self, context):
        self.file = IfcStore.get_file()
        obj = bpy.context.active_object
        props = obj.BIMObjectProperties
        relating_structure = None
        for collection in obj.users_collection:
            if "Ifc" in collection.name:
                relating_structure = self.file.by_id(
                    bpy.data.objects.get(collection.name).BIMObjectProperties.ifc_definition_id
                )
        if not relating_structure:
            return {"FINISHED"}
        usecase = assign_container.Usecase(
            self.file,
            {
                "product": self.file.by_id(props.ifc_definition_id),
                "relating_structure": relating_structure,
            },
        )
        usecase.execute()
        Data.load(props.ifc_definition_id)
        return {"FINISHED"}
