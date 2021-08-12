import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.date
from ifcopenshell.api.pset.data import Data as PsetData


def calculate_quantities(usecase_path, ifc_file, settings):
    if not set(["ScheduleStart", "ScheduleFinish", "ScheduleDuration"]).intersection(
        set(settings["attributes"].keys())
    ):
        return
    element = settings["task_time"]
    if not element.ScheduleDuration:
        return
    task = [e for e in ifc_file.get_inverse(element) if e.is_a("IfcTask")][0]
    qto = ifcopenshell.api.run(
        "pset.add_qto", ifc_file, should_run_listeners=False, product=task, name="Qto_TaskBaseQuantities"
    )
    ifcopenshell.api.run(
        "pset.edit_qto",
        ifc_file,
        should_run_listeners=False,
        qto=qto,
        properties={
            "StandardWork": ifcopenshell.util.date.ifc2datetime(element.ScheduleDuration).days,
        },
    )
    PsetData.load(ifc_file, task.id())
