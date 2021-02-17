import ifcopenshell
import ifcopenshell.util.date
import xml.etree.ElementTree as ET


class P6ToIfc:
    def __init__(self):
        self.project = {}
        self.wbs = {}

    def execute(self):
        self.parse_xml()
        self.create_ifc()

    def parse_xml(self):
        tree = ET.parse("p6.xml")
        ns = {"pr": "http://xmlns.oracle.com/Primavera/P6/V19.12/API/BusinessObjects"}
        root = tree.getroot()
        project = root.find("pr:Project", ns)
        self.project["Name"] = project.find("pr:Name", ns).text

        for wbs in project.findall("pr:WBS", ns):
            self.wbs[wbs.find("pr:ObjectId", ns).text] = {
                "Name": wbs.find("pr:Name", ns).text,
                "ParentObjectId": wbs.find("pr:ParentObjectId", ns).text,
                "ifc": None,
                "rel": None,
                "activities": [],
            }

        for activity in project.findall("pr:Activity", ns):
            self.wbs[activity.find("pr:WBSObjectId", ns).text]["activities"].append(
                {
                    "Name": activity.find("pr:Name", ns).text,
                    "StartDate": activity.find("pr:StartDate", ns).text,
                    "FinishDate": activity.find("pr:FinishDate", ns).text,
                    "ifc": None,
                }
            )

    def get_wbs(self, wbs):
        return {"Name": wbs.find("pr:Name", ns).text, "subtasks": []}

    def create_ifc(self):
        self.file = ifcopenshell.file(schema="IFC4")
        #self.file = ifcopenshell.file(schema="IFC2X3")
        self.root = self.file.create_entity(
            "IfcTask", **{"GlobalId": ifcopenshell.guid.new(), "Name": self.project["Name"]}
        )
        self.root_rel = self.create_rel_nests(self.root)

        for wbs in self.wbs.values():
            wbs["ifc"] = self.file.create_entity(
                "IfcTask", **{"GlobalId": ifcopenshell.guid.new(), "Name": wbs["Name"]}
            )
            if wbs["ParentObjectId"]:
                parent_wbs = self.wbs[wbs["ParentObjectId"]]
                if not parent_wbs["rel"]:
                    parent_wbs["rel"] = self.create_rel_nests(parent_wbs["ifc"])
                rel = parent_wbs["rel"]
            else:
                rel = self.root_rel
            self.append_to_rel(rel, wbs["ifc"])

            for activity in wbs["activities"]:
                if not wbs["rel"]:
                    wbs["rel"] = self.create_rel_nests(wbs["ifc"])

                if self.file.schema == "IFC2X3":
                    activity["TimeForTask"] = self.file.create_entity(
                        "IfcScheduleTimeControl",
                        **{
                            "ScheduleStart": self.file.create_entity(
                                "IfcCalendarDate",
                                **ifcopenshell.util.date.datetime2ifc(activity["StartDate"], "IfcCalendarDate")
                            ),
                            "ScheduleFinish": self.file.create_entity(
                                "IfcCalendarDate",
                                **ifcopenshell.util.date.datetime2ifc(activity["FinishDate"], "IfcCalendarDate")
                            ),
                        }
                    )
                else:
                    activity["TaskTime"] = self.file.create_entity(
                        "IfcTaskTime",
                        **{"ScheduleStart": activity["StartDate"], "ScheduleFinish": activity["FinishDate"]}
                    )

                is_milestone = activity["StartDate"] == activity["FinishDate"]
                activity["ifc"] = self.file.create_entity(
                    "IfcTask",
                    **{"GlobalId": ifcopenshell.guid.new(), "Name": activity["Name"], "IsMilestone": is_milestone}
                )

                if self.file.schema == "IFC2X3":
                    # Invalid, but reading the IFC2X3 docs gives me a headache
                    self.file.create_entity("IfcRelAssignsTasks", **{
                        "GlobalId": ifcopenshell.guid.new(),
                        "RelatedObjects": [activity["ifc"]],
                        "TimeForTask": activity["TimeForTask"]
                    })
                else:
                    activity["ifc"].TaskTime = activity["TaskTime"]

                self.append_to_rel(wbs["rel"], activity["ifc"])
        self.file.write("p6.ifc")

    def create_rel_nests(self, relating_object):
        return self.file.create_entity(
            "IfcRelNests", **{"GlobalId": ifcopenshell.guid.new(), "RelatingObject": relating_object}
        )

    def append_to_rel(self, rel, element):
        related_objects = list(rel.RelatedObjects or [])
        related_objects.append(element)
        rel.RelatedObjects = related_objects


p6_to_ifc = P6ToIfc()
p6_to_ifc.execute()
