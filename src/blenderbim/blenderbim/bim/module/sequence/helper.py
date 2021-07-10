import bpy
import math
import isodate
import datetime
from dateutil import parser
from ifcopenshell.api.sequence.data import Data


def derive_date(ifc_definition_id, attribute_name, date=None, is_earliest=False, is_latest=False):
    task = Data.tasks[ifc_definition_id]
    if task["TaskTime"]:
        current_date = Data.task_times[task["TaskTime"]][attribute_name]
        if current_date:
            return current_date
    for subtask in task["RelatedObjects"]:
        current_date = derive_date(subtask, attribute_name, date=date, is_earliest=is_earliest, is_latest=is_latest)
        if is_earliest:
            if current_date and (date is None or current_date < date):
                date = current_date
        if is_latest:
            if current_date and (date is None or current_date > date):
                date = current_date
    return date


def derive_duration(ifc_definition_id, attribute_name):
    task = Data.tasks[ifc_definition_id]
    if task["TaskTime"]:
        current_date = Data.task_times[task["TaskTime"]][attribute_name]
        if current_date:
            return current_date
    for subtask in task["RelatedObjects"]:
        current_date = derive_date(subtask, attribute_name, date=date, is_earliest=is_earliest, is_latest=is_latest)
        if is_earliest:
            if current_date and (date is None or current_date < date):
                date = current_date
        if is_latest:
            if current_date and (date is None or current_date > date):
                date = current_date
    return date


def parse_datetime(value):
    try:
        return parser.isoparse(value)
    except:
        try:
            return parser.parse(value, dayfirst=True, fuzzy=True)
        except:
            return None


def parse_duration(value):
    try:
        return isodate.parse_duration(value)
    except:
        return None


def canonicalise_time(time):
    if not time:
        return "-"
    return time.strftime("%d/%m/%y")


def get_scene_prop(prop_path):
    prop = bpy.context.scene.get(prop_path.split(".")[0])
    for part in prop_path.split(".")[1:]:
        if part:
            prop = prop.get(part)
    return prop


def set_scene_prop(prop_path, value):
    parent = get_scene_prop(prop_path[: prop_path.rfind(".")])
    prop = prop_path.split(".")[-1]
    parent[prop] = value