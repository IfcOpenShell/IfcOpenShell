import bpy
import json
import blenderbim.bim.module.person.add_person as add_person
import blenderbim.bim.module.person.edit_person as edit_person
import blenderbim.bim.module.person.remove_person as remove_person
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.person.data import Data


class EnableEditingPerson(bpy.types.Operator):
    bl_idname = "bim.enable_editing_person"
    bl_label = "Enable Editing Person"
    person_id: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMProperties
        props.active_person_id = self.person_id
        data = Data.people[self.person_id]
        name = data["Id"] if self.file.schema == "IFC2X3" else data["Identification"]
        props.person.name = name or ""
        props.person.family_name = data["FamilyName"] or ""
        props.person.given_name = data["GivenName"] or ""
        props.person.middle_names = json.dumps(data["MiddleNames"]) if data["MiddleNames"] else ""
        props.person.prefix_titles = json.dumps(data["PrefixTitles"]) if data["PrefixTitles"] else ""
        props.person.suffix_titles = json.dumps(data["SuffixTitles"]) if data["SuffixTitles"] else ""
        return {"FINISHED"}


class DisableEditingPerson(bpy.types.Operator):
    bl_idname = "bim.disable_editing_person"
    bl_label = "Disable Editing Person"

    def execute(self, context):
        context.scene.BIMProperties.active_person_id = 0
        return {"FINISHED"}


class AddPerson(bpy.types.Operator):
    bl_idname = "bim.add_person"
    bl_label = "Add Person"

    def execute(self, context):
        add_person.Usecase(IfcStore.get_file()).execute()
        Data.load()
        return {"FINISHED"}


class EditPerson(bpy.types.Operator):
    bl_idname = "bim.edit_person"
    bl_label = "Edit Person"

    def execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMProperties
        attributes = {
            "Identification": props.person.name or None,
            "FamilyName": props.person.family_name or None,
            "GivenName": props.person.given_name or None,
            "MiddleNames": json.loads(props.person.middle_names) if props.person.middle_names else None,
            "PrefixTitles": json.loads(props.person.prefix_titles) if props.person.prefix_titles else None,
            "SuffixTitles": json.loads(props.person.suffix_titles) if props.person.suffix_titles else None,
        }
        if self.file.schema == "IFC2X3":
            attributes["Id"] = attributes["Identification"]
            del attributes["Identification"]
        edit_person.Usecase(
            self.file, {"person": self.file.by_id(props.active_person_id), "attributes": attributes}
        ).execute()
        Data.load()
        bpy.ops.bim.disable_editing_person()
        return {"FINISHED"}


class RemovePerson(bpy.types.Operator):
    bl_idname = "bim.remove_person"
    bl_label = "Remove Person"
    person_id: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        remove_person.Usecase(self.file, {"person": self.file.by_id(self.person_id)}).execute()
        Data.load()
        return {"FINISHED"}
