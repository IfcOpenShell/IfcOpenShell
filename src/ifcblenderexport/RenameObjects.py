import bpy
from bpy.types import Operator

class Object_OT_RenameObjects(Operator):
    bl_idname = "object.renameobjects"
    bl_label = "Rename Object(s)"

    # Multi Object rename UI
    BNameCB   : bpy.props.BoolProperty(name = "Base Name:")
    BaseName  : bpy.props.StringProperty(name = "")
    PreFixCB  : bpy.props.BoolProperty(name = "Prefix:")
    PreFix    : bpy.props.StringProperty(name = "")
    RemFrst   : bpy.props.BoolProperty(name = "Remove First")
    DgtFrst   : bpy.props.IntProperty(name = "Digits")
    SuffixCB  : bpy.props.BoolProperty(name = "Suffix")
    Suffix    : bpy.props.StringProperty(name = "")
    RemLast   : bpy.props.BoolProperty(name = "Remove Last")
    DgtLast   : bpy.props.IntProperty(name = "Digits")
    NumbredCB : bpy.props.BoolProperty(name = "Numbred")
    BaseNum   : bpy.props.IntProperty(name = "Base Number")
    Step      : bpy.props.IntProperty(name = "Step", default = 1)
    findCB    : bpy.props.BoolProperty(name = "Replace")
    find      : bpy.props.StringProperty(name = "")
    replace   : bpy.props.StringProperty(name = "")
    # Single rename UI
    Name : bpy.props.StringProperty(name="Name")

    def draw(self, ctx):
        SelCount = len(bpy.context.selected_objects)
        if SelCount > 1:
            box = self.layout.box()
            row = box.row()
            row.prop(self, "BNameCB")
            row.prop(self, "BaseName")
            row = box.row()
            row.prop(self, "PreFixCB")
            row.prop(self, "PreFix")
            row = box.row()
            row.prop(self, "RemFrst")
            row.prop(self, "DgtFrst")
            row = box.row()
            row.prop(self, "SuffixCB")
            row.prop(self, "Suffix")
            row = box.row()
            row.prop(self, "RemLast")
            row.prop(self, "DgtLast")
            row = box.row(align=True)
            row.prop(self, "NumbredCB")
            row.prop(self, "BaseNum")
            row.prop(self, "Step")
            row = box.row(align=True)
            row.prop(self, "findCB")
            row.prop(self, "find")
            row.prop(self, "replace")
        if SelCount == 1:
            box = self.layout.box()
            row = box.row()
            row.prop(self, "Name")
        if SelCount == 0:
            box = self.layout.box()
            row = box.row()
            row.label("No Selected Object")

    def __init__(self):
        if len(bpy.context.selected_objects) == 1:
            self.Name = bpy.context.selected_objects[0].name

    def execute(self, context):
        SelCount = len(bpy.context.selected_objects)
        if SelCount > 1:
            SelObj = bpy.context.selected_objects
            Index = self.BaseNum
            for i in range(0,SelCount):
                # Get Object Original Name #
                NewName = SelObj[i].name
                # Set the Base name #
                if self.BNameCB:
                    NewName = self.BaseName
                # Remove First characters #
                if self.RemFrst:
                    NewName = NewName[self.DgtFrst : self.DgtFrst + len(NewName)]
                # Remove Last Characters #
                if self.RemLast:
                    NewName = NewName[1 : len(NewName) - self.DgtLast]
                # Add Prefix to the new name #
                if self.PreFixCB:
                    NewName = self.PreFix + NewName
                # Add Suffix to the new name #
                if self.SuffixCB:
                    NewName = NewName + self.Suffix
                # Add Digits to end of new name #
                if self.NumbredCB:
                        NewName += str(Index)
                        Index += self.Step
                # Find and Replace #
                if self.findCB:
                    NewName = NewName.replace(self.find, self.replace)
                # Set the new name to the object #
                SelObj[i].name = NewName
        elif SelCount == 1:
            bpy.context.selected_objects[0].name = self.Name
        return {'FINISHED'}
       
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

def register():
    bpy.utils.register_class(Object_OT_RenameObjects)

def unregister():
    bpy.utils.unregister_class(Object_OT_RenameObjects)

if __name__ == "__main__":
    register()