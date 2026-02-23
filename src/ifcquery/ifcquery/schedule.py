# This file was generated with the assistance of an AI coding tool.
from __future__ import annotations

from typing import Any

import ifcopenshell
import ifcopenshell.util.sequence as seq


def _task_to_dict(task: ifcopenshell.entity_instance, max_depth: int | None, depth: int) -> dict[str, Any]:
    task_time = task.TaskTime
    start = None
    finish = None
    if task_time:
        start = task_time.ScheduleStart
        finish = task_time.ScheduleFinish

    outputs = []
    for product in seq.get_task_outputs(task):
        outputs.append({"id": product.id(), "type": product.is_a(), "name": getattr(product, "Name", None)})

    if max_depth is not None and depth >= max_depth:
        child_count = len(seq.get_nested_tasks(task))
        subtasks = {"truncated": True, "count": child_count} if child_count else []
    else:
        subtasks = [_task_to_dict(sub, max_depth, depth + 1) for sub in seq.get_nested_tasks(task)]

    return {
        "id": task.id(),
        "name": getattr(task, "Name", None),
        "start": start,
        "finish": finish,
        "is_milestone": bool(task.IsMilestone) if hasattr(task, "IsMilestone") else False,
        "outputs": outputs,
        "subtasks": subtasks,
    }


def schedule(model: ifcopenshell.file, max_depth: int | None = None) -> list[dict[str, Any]]:
    """Return a list of IfcWorkSchedule entries with nested task trees.

    max_depth limits how many levels of subtasks are expanded (None = unlimited).
    At the cutoff level, subtasks is replaced with {"truncated": True, "count": N}.
    """
    result = []
    for work_schedule in model.by_type("IfcWorkSchedule"):
        tasks = [_task_to_dict(t, max_depth, depth=1) for t in seq.get_root_tasks(work_schedule)]
        result.append(
            {
                "id": work_schedule.id(),
                "name": getattr(work_schedule, "Name", None),
                "predefined_type": getattr(work_schedule, "PredefinedType", None),
                "tasks": tasks,
            }
        )
    return result
