# Debug script to see what's happening with colorType values

import bpy
import bonsai.tool as tool

def debug_colortype_values(operation_name):
    """Debug function to see current colorType values"""
    print(f"\n=== DEBUG {operation_name} ===")

    try:
        tprops = tool.Sequence.get_task_tree_props()
        if not tprops:
            print("No task tree properties found")
            return

        print(f"Total tasks in UI: {len(tprops.tasks)}")

        for i, task in enumerate(tprops.tasks):
            task_id = getattr(task, 'ifc_definition_id', 0)
            animation_color_schemes = getattr(task, 'animation_color_schemes', '')
            selected_colortype = getattr(task, 'selected_colortype_in_active_group', '')

            if animation_color_schemes or selected_colortype:
                print(f"Task {i}: ID={task_id}")
                print(f"  animation_color_schemes: '{animation_color_schemes}'")
                print(f"  selected_colortype_in_active_group: '{selected_colortype}'")

    except Exception as e:
        print(f"Debug failed: {e}")

    print(f"=== END DEBUG {operation_name} ===\n")


class DebugColorTypeOperator(bpy.types.Operator):
    bl_idname = "debug.colortype_values"
    bl_label = "Debug ColorType Values"

    def execute(self, context):
        debug_colortype_values("MANUAL DEBUG")
        return {"FINISHED"}


# Register for testing
def register():
    bpy.utils.register_class(DebugColorTypeOperator)

def unregister():
    bpy.utils.unregister_class(DebugColorTypeOperator)