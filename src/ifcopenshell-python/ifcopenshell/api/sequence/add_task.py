import ifcopenshell.api
import ifcopenshell


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "work_schedule": None,
            "parent_task": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        task = ifcopenshell.api.run(
            "root.create_entity",
            self.file,
            ifc_class="IfcTask",
            name=None,
            predefined_type="NOTDEFINED",
        )
        task.IsMilestone = False
        if self.settings["work_schedule"]:
            self.file.create_entity(
                "IfcRelAssignsToControl",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                    "RelatedObjects": [task],
                    "RelatingControl": self.settings["work_schedule"],
                }
            )
        elif self.settings["parent_task"]:
            rel = ifcopenshell.api.run(
                "nest.assign_object", self.file, related_object=task, relating_object=self.settings["parent_task"]
            )
            if self.settings["parent_task"].Identification:
                task.Identification = self.settings["parent_task"].Identification + "." + str(len(rel.RelatedObjects))
        return task
