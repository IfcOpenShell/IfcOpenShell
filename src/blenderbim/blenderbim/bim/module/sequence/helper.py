import isodate
from dateutil import parser
from ifcopenshell.api.sequence.data import Data


def derive_date(ifc_definition_id, attribute_name, date=None, is_earliest=False, is_latest=False):
    task = Data.tasks[ifc_definition_id]
    if task["TaskTime"]:
        current_date = Data.task_times[task["TaskTime"]][attribute_name]
        if current_date:
            return current_date
    for subtask in task["RelatedObjects"]:
        current_date = derive_date(
            subtask, attribute_name, date=date, is_earliest=is_earliest, is_latest=is_latest
        )
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
