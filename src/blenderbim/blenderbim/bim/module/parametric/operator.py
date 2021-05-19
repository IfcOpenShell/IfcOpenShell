import bpy
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.representation
from blenderbim.bim.ifc import IfcStore


def generate_box(usecase_path, ifc_file, **settings):
    box_context = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Box", "MODEL_VIEW")
    if not box_context:
        return
    obj = settings["blender_object"]
    product = ifc_file.by_id(obj.BIMObjectProperties.ifc_definition_id)
    old_box = ifcopenshell.util.representation.get_representation(product, "Model", "Box", "MODEL_VIEW")
    if settings["context"].ContextType == "Model" and getattr(settings["context"], "ContextIdentifier") == "Body":
        if old_box:
            bpy.ops.bim.remove_representation(representation_id=old_box.id(), obj=obj.name)

        new_settings = settings.copy()
        new_settings["context"] = box_context
        new_box = ifcopenshell.api.run(
            "geometry.add_representation", ifc_file, should_run_listeners=False, **new_settings
        )
        ifcopenshell.api.run(
            "geometry.assign_representation",
            ifc_file,
            should_run_listeners=False,
            **{"product": product, "representation": new_box}
        )


class ActivateParametricEngine(bpy.types.Operator):
    bl_idname = "bim.activate_parametric_engine"
    bl_label = "Activate Parametric Engine"

    def execute(self, context):
        ifcopenshell.api.add_post_listener("geometry.add_representation", IfcStore.get_file(), generate_box)
        return {"FINISHED"}
