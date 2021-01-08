from bpy.types import Panel
from blenderbim.bim.module.person.data import Data
from blenderbim.bim.ifc import IfcStore


class BIM_PT_people(Panel):
    bl_label = "IFC People"
    bl_idname = "BIM_PT_people"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        if not Data.is_loaded:
            Data.load()

        self.file = IfcStore.get_file()
        self.layout.use_property_split = True
        props = context.scene.BIMProperties

        row = self.layout.row()
        row.operator("bim.add_person")

        for person_id, person in Data.people.items():
            if props.active_person_id == person_id:
                blender_person = props.person
                box = self.layout.box()
                row = box.row(align=True)
                row.prop(blender_person, "name", icon="USER", text="")
                row.operator("bim.edit_person", icon="CHECKMARK", text="")
                row.operator("bim.disable_editing_person", icon="X", text="")
                row = box.row()
                row.prop(blender_person, "family_name")
                row = box.row()
                row.prop(blender_person, "given_name")
                row = box.row()
                row.prop(blender_person, "middle_names")
                row = box.row()
                row.prop(blender_person, "prefix_titles")
                row = box.row()
                row.prop(blender_person, "suffix_titles")
            else:
                row = self.layout.row(align=True)
                name = person["Id"] if self.file.schema == "IFC2X3" else person["Identification"]
                name = name or "*"
                if person["GivenName"] or person["FamilyName"]:
                    full_name = "{} {}".format(person["GivenName"] or "", person["FamilyName"] or "").strip()
                    name += f" ({full_name})"
                row.label(text=name)
                if person["Roles"]:
                    row.label(text=", ".join([r.Role for r in person["Roles"]]))
                row.operator("bim.enable_editing_person", icon="GREASEPENCIL", text="").person_id = person_id
                if not person["is_engaged"]:
                    row.operator("bim.remove_person", icon="X", text="").person_id = person_id
        return


        if props.people:
            if props.active_person_index < len(props.people):
                self.layout.label(text="Roles:")
                draw_roles_ui(self.layout, person, "person")
                self.layout.label(text="Addresses:")
                draw_addresses_ui(self.layout, person, "person")

