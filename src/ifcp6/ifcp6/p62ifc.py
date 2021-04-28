import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.date
import xml.etree.ElementTree as ET
from datetime import datetime


class P62Ifc:
    def __init__(self):
        self.xml = None
        self.file = None
        self.work_plan = None
        self.project = {}
        self.wbs = {}
        self.activities = {}
        self.relationships = {}

    def execute(self):
        self.parse_xml()
        self.create_ifc()

    def parse_xml(self):
        tree = ET.parse(self.xml)
        ns = {"pr": "http://xmlns.oracle.com/Primavera/P6/V19.12/API/BusinessObjects"}
        root = tree.getroot()
        project = root.find("pr:Project", ns)
        self.project["Name"] = project.find("pr:Name", ns).text

        for wbs in project.findall("pr:WBS", ns):
            self.wbs[wbs.find("pr:ObjectId", ns).text] = {
                "Name": wbs.find("pr:Name", ns).text,
                "Code": wbs.find("pr:Code", ns).text,
                "ParentObjectId": wbs.find("pr:ParentObjectId", ns).text,
                "ifc": None,
                "rel": None,
                "activities": [],
            }

        for activity in project.findall("pr:Activity", ns):
            activity_id = activity.find("pr:ObjectId", ns).text
            wbs_id = activity.find("pr:WBSObjectId", ns).text
            if not wbs_id:
                print("No WBS ID found for activity", activity_id)
                continue
            self.wbs[wbs_id]["activities"].append(activity_id)
            self.activities[activity_id] = {
                "Name": activity.find("pr:Name", ns).text,
                "Identification": activity.find("pr:Id", ns).text,
                "StartDate": datetime.fromisoformat(activity.find("pr:StartDate", ns).text),
                "FinishDate": datetime.fromisoformat(activity.find("pr:FinishDate", ns).text),
                "Status": activity.find("pr:Status", ns).text,
                "ifc": None,
            }

        for relationship in project.findall("pr:Relationship", ns):
            self.relationships[relationship.find("pr:ObjectId", ns).text] = {
                "PredecessorActivity": relationship.find("pr:PredecessorActivityObjectId", ns).text,
                "SuccessorActivity": relationship.find("pr:SuccessorActivityObjectId", ns).text,
            }

    def get_wbs(self, wbs):
        return {"Name": wbs.find("pr:Name", ns).text, "subtasks": []}

    def create_ifc(self):
        if not self.file:
            self.file = self.create_boilerplate_ifc()
        work_schedule = self.create_work_schedule()
        self.create_tasks(work_schedule)
        self.create_rel_sequences()

    def create_work_schedule(self):
        return ifcopenshell.api.run(
            "sequence.add_work_schedule", self.file, name=self.project["Name"], work_plan=self.work_plan
        )

    def create_tasks(self, work_schedule):
        for wbs in self.wbs.values():
            self.create_task_from_wbs(wbs, work_schedule)

    def create_task_from_wbs(self, wbs, work_schedule):
        wbs["ifc"] = ifcopenshell.api.run(
            "sequence.add_task",
            self.file,
            work_schedule=None if wbs["ParentObjectId"] else work_schedule,
            parent_task=self.wbs[wbs["ParentObjectId"]]["ifc"] if wbs["ParentObjectId"] else None,
        )
        ifcopenshell.api.run(
            "sequence.edit_task",
            self.file,
            task=wbs["ifc"],
            attributes={"Name": wbs["Name"], "Identification": wbs["Code"]},
        )
        for activity_id in wbs["activities"]:
            self.create_task_from_activity(self.activities[activity_id], wbs, work_schedule)

    def create_task_from_activity(self, activity, wbs, work_schedule):
        activity["ifc"] = ifcopenshell.api.run(
            "sequence.add_task",
            self.file,
            parent_task=wbs["ifc"],
        )
        ifcopenshell.api.run(
            "sequence.edit_task",
            self.file,
            task=activity["ifc"],
            attributes={
                "Name": activity["Name"],
                "Identification": activity["Identification"],
                "Status": activity["Status"],
                "IsMilestone": activity["StartDate"] == activity["FinishDate"],
            },
        )
        task_time = ifcopenshell.api.run("sequence.add_task_time", self.file, task=activity["ifc"])
        ifcopenshell.api.run(
            "sequence.edit_task_time",
            self.file,
            task_time=task_time,
            attributes={
                "ScheduleStart": activity["StartDate"],
                "ScheduleFinish": activity["FinishDate"],
            },
        )

    def create_rel_sequences(self):
        for relationship in self.relationships.values():
            ifcopenshell.api.run(
                "sequence.assign_sequence",
                self.file,
                relating_process=self.activities[relationship["PredecessorActivity"]]["ifc"],
                related_process=self.activities[relationship["SuccessorActivity"]]["ifc"],
            )

    def create_boilerplate_ifc(self):
        self.file = ifcopenshell.file(schema="IFC4")
        self.work_plan = self.file.create_entity("IfcWorkPlan")
