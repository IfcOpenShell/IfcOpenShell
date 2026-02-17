# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021, 2022 Dion Moult <dion@thinkmoult.com>, Yassine Oualid <yassine@sigmadimensions.com>, Federico Eraso <feraso@svisuals.net
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.


from __future__ import annotations
import bpy
import json
from datetime import datetime
from typing import Any, List
import ifcopenshell
import bonsai.tool as tool
# Try to import SequenceCache for optimization, fallback if not available
try:
    from bonsai.bim.module.sequence.data import SequenceCache
except ImportError:
    try:
        import bonsai.data
        SequenceCache = bonsai.data.SequenceCache
    except ImportError:
        # Fallback: Create a dummy SequenceCache that returns None
        class SequenceCache:
            @staticmethod
            def get_vectorized_task_states(*args, **kwargs):
                return None
            @staticmethod
            def get_schedule_dates(*args, **kwargs):
                return None
            @staticmethod
            def get_task_products(*args, **kwargs):
                return None

class SnapshotSequence:
    """Mixin class for processing and displaying construction state snapshots."""

    to_build = set()
    in_construction = set()
    completed = set()
    to_demolish = set()
    in_demolition = set()
    demolished = set()


    @classmethod
    def process_construction_state(
        cls,
        work_schedule: ifcopenshell.entity_instance,
        date: datetime,
        viz_start: datetime = None,
        viz_finish: datetime = None,
        date_source: str = "SCHEDULE") -> dict[str, Any]:
        """
        OPTIMIZED: Processes states considering the configured visualization range.
        Now uses cached data structures for massive performance improvement.

        Args:
            work_schedule: Work schedule
            date: Current date of the snapshot
            viz_start: Visualization start date (optional)
            date_source: The type of date to use ('SCHEDULE', 'ACTUAL', etc.)
            viz_finish: Visualization end date (optional)
        """
        # Initialize state sets
        cls.to_build = set()
        cls.in_construction = set()
        cls.completed = set()
        cls.to_demolish = set()
        cls.in_demolition = set()
        cls.demolished = set()

        # Try NumPy vectorized computation with fallbacks
        work_schedule_id = work_schedule.id()

        try:
            vectorized_result = SequenceCache.get_vectorized_task_states(
                work_schedule_id, date, date_source, viz_start, viz_finish
            )

            if vectorized_result and vectorized_result.get('vectorized'):
                cls.to_build = vectorized_result["TO_BUILD"]
                cls.in_construction = vectorized_result["IN_CONSTRUCTION"]
                cls.completed = vectorized_result["COMPLETED"]
                cls.to_demolish = vectorized_result.get("TO_DEMOLISH", set())
                cls.in_demolition = vectorized_result.get("IN_DEMOLITION", set())
                cls.demolished = vectorized_result.get("DEMOLISHED", set())
                return
        except Exception:
            pass

        try:
            cached_dates = SequenceCache.get_schedule_dates(work_schedule_id, date_source)
            cached_products = SequenceCache.get_task_products(work_schedule_id)

            if cached_dates and cached_products:
                tasks_data = cached_dates.get('tasks_dates', [])

                for task_id, start_date, finish_date in tasks_data:
                    if not start_date or not finish_date:
                        continue

                    if viz_start and viz_finish:
                        if finish_date < viz_start:
                            cls.completed.update(cached_products.get(task_id, []))
                            continue
                        elif start_date > viz_finish:
                            continue

                    if start_date > date:
                        cls.to_build.update(cached_products.get(task_id, []))
                    elif finish_date < date:
                        cls.completed.update(cached_products.get(task_id, []))
                    else:
                        cls.in_construction.update(cached_products.get(task_id, []))

                return
        except Exception:
            pass
        for rel in work_schedule.Controls or []:
            for related_object in rel.RelatedObjects:
                if related_object.is_a("IfcTask"):
                    cls.process_task_status(related_object, date, viz_start, viz_finish, date_source=date_source)

        return {
            "TO_BUILD": cls.to_build,
            "IN_CONSTRUCTION": cls.in_construction,
            "COMPLETED": cls.completed,
            "TO_DEMOLISH": cls.to_demolish,
            "IN_DEMOLITION": cls.in_demolition,
            "DEMOLISHED": cls.demolished,
        }

    @classmethod
    def _process_task_status_cached(
        cls,
        task_id: int,
        product_ids: List[int],
        start_date: datetime,
        finish_date: datetime,
        current_date: datetime,
        viz_start: datetime = None,
        viz_finish: datetime = None
    ):
        """Fast version of task status processing using cached data."""
        if not product_ids:
            return
        
        if viz_start and finish_date < viz_start:
            cls.completed.update(product_ids)
            return

        if viz_finish and start_date > viz_finish:
            return

        if current_date < start_date:
            cls.to_build.update(product_ids)
        elif start_date <= current_date <= finish_date:
            cls.in_construction.update(product_ids)
        else:
            cls.completed.update(product_ids)

    @classmethod
    def process_task_status(
        cls,
        task: ifcopenshell.entity_instance,
        date: datetime,
        viz_start: datetime = None,
        viz_finish: datetime = None,
        date_source: str = "SCHEDULE"
    ) -> None:
        """Process a task's state considering the visualization range."""
        for rel in task.IsNestedBy or []:
            [cls.process_task_status(related_object, date, viz_start, viz_finish, date_source=date_source) for related_object in rel.RelatedObjects]

        start_date_type = f"{date_source.capitalize()}Start"
        finish_date_type = f"{date_source.capitalize()}Finish"

        start = ifcopenshell.util.sequence.derive_date(task, start_date_type, is_earliest=True)
        finish = ifcopenshell.util.sequence.derive_date(task, finish_date_type, is_latest=True)

        if not start or not finish:
            return

        outputs = ifcopenshell.util.sequence.get_task_outputs(task) or []
        inputs = tool.Sequence.get_task_inputs(task) or []

        if viz_finish and start > viz_finish:
            return

        if viz_start and finish < viz_start:
            [cls.completed.add(tool.Ifc.get_object(output)) for output in outputs]
            [cls.demolished.add(tool.Ifc.get_object(input)) for input in inputs]
            return

        if date < start:
            [cls.to_build.add(tool.Ifc.get_object(output)) for output in outputs]
            [cls.to_demolish.add(tool.Ifc.get_object(input)) for input in inputs]
        elif date <= finish:
            [cls.in_construction.add(tool.Ifc.get_object(output)) for output in outputs]
            [cls.in_demolition.add(tool.Ifc.get_object(input)) for input in inputs]
        else:
            [cls.completed.add(tool.Ifc.get_object(output)) for output in outputs]
            [cls.demolished.add(tool.Ifc.get_object(input)) for input in inputs]


    @classmethod
    def show_snapshot(cls, product_states):
        """Display a visual snapshot of all IFC objects at the specified date."""
        import bpy
        import json

        if not bpy.context.scene.get('BIM_VarianceOriginalObjectColors'):
            cls._save_original_object_colors()

        original_properties = {}
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and tool.Ifc.get_entity(obj):
                original_color = None
                try:
                    if obj.material_slots and obj.material_slots[0].material:
                        material = obj.material_slots[0].material
                        if material.use_nodes:
                            principled = tool.Blender.get_material_node(material, "BSDF_PRINCIPLED")
                            if principled and principled.inputs.get("Base Color"):
                                base_color = principled.inputs["Base Color"].default_value
                                original_color = [base_color[0], base_color[1], base_color[2], base_color[3]]
                except Exception:
                    pass

                if original_color is None:
                    original_color = list(obj.color)

                original_properties[obj.name] = {
                    "color": original_color,
                    "hide_viewport": obj.hide_viewport,
                    "hide_render": obj.hide_render,
                }

        bpy.context.scene['bonsai_snapshot_original_props'] = json.dumps(original_properties)

        for obj in bpy.data.objects:
            if getattr(obj, "animation_data", None):
                obj.animation_data_clear()

        ws_props = tool.Sequence.get_work_schedule_props()
        snapshot_date_str = getattr(ws_props, "visualisation_start", None)
        if not snapshot_date_str or snapshot_date_str == "-":
            return
        try:
            snapshot_date = tool.Sequence.parse_isodate_datetime(snapshot_date_str)
        except Exception:
            return
        date_source = getattr(ws_props, "date_source_type", "SCHEDULE")

        anim_props = tool.Sequence.get_animation_props()
        active_group_name = None
        for item in anim_props.animation_group_stack:
            if item.enabled and item.group:
                active_group_name = item.group
                break
        if not active_group_name:
            active_group_name = "DEFAULT"

        applied_count = 0
        for obj in bpy.data.objects:
            element = tool.Ifc.get_entity(obj)
            if not element or not obj.type == 'MESH':
                continue

            task = cls.get_task_for_product(element)
            if not task:
                obj.hide_viewport = True
                obj.hide_render = True
                continue

            start_attr = f"{date_source.capitalize()}Start"
            finish_attr = f"{date_source.capitalize()}Finish"
            task_start = ifcopenshell.util.sequence.derive_date(task, start_attr, is_earliest=True)
            task_finish = ifcopenshell.util.sequence.derive_date(task, finish_attr, is_latest=True)

            if not task_start or not task_finish:
                obj.hide_viewport = True
                obj.hide_render = True
                continue

            state = ""
            if snapshot_date < task_start:
                state = "start"
            elif task_start <= snapshot_date <= task_finish:
                state = "in_progress"
            else:
                state = "end"

            ColorType = tool.Sequence.get_assigned_ColorType_for_task(task, anim_props, active_group_name)
            original_color = original_properties.get(obj.name, {}).get("color", [1,1,1,1])

            consider_start = getattr(ColorType, 'consider_start', False)
            consider_active = getattr(ColorType, 'consider_active', True)
            consider_end = getattr(ColorType, 'consider_end', True)
            is_priority_mode = (consider_start and not consider_active and not consider_end)

            is_demolition = (getattr(task, "PredefinedType", "") or "").upper() in {"DEMOLITION", "REMOVAL", "DISPOSAL", "DISMANTLE"}
            is_construction = not is_demolition

            if is_priority_mode:
                obj.hide_viewport = False
                state = "start"
            else:
                if state == "start":
                    if consider_start:
                        obj.hide_viewport = False
                    else:
                        if is_construction:
                            obj.hide_viewport = True
                        else:
                            obj.hide_viewport = False
                elif state == "in_progress" and not consider_active:
                    obj.hide_viewport = True
                elif state == "end":
                    if not consider_end:
                        obj.hide_viewport = True
                    elif getattr(ColorType, 'hide_at_end', False):
                        obj.hide_viewport = True
                    else:
                        obj.hide_viewport = False
                else:
                    if is_demolition:
                        if state == "start":
                            obj.hide_viewport = False
                        elif state == "in_progress":
                            obj.hide_viewport = False
                        else:
                            obj.hide_viewport = True
                    else:
                        if state == "start":
                            obj.hide_viewport = True
                        else:
                            obj.hide_viewport = False

            if not obj.hide_viewport:
                color_to_apply = original_color
                transparency = 0.0

                if state == "start":
                    if not getattr(ColorType, 'use_start_original_color', False):
                        color_to_apply = list(ColorType.start_color)
                    transparency = getattr(ColorType, 'start_transparency', 0.0)
                elif state == "in_progress":
                    if not getattr(ColorType, 'use_active_original_color', False):
                        color_to_apply = list(ColorType.in_progress_color)
                    transparency = getattr(ColorType, 'active_start_transparency', 0.0)
                else:
                    if getattr(ColorType, 'hide_at_end', False):
                        obj.hide_viewport = True
                    elif not getattr(ColorType, 'use_end_original_color', True):
                        color_to_apply = list(ColorType.end_color)
                    transparency = getattr(ColorType, 'end_transparency', 0.0)

                if not obj.hide_viewport:
                    alpha = 1.0 - transparency
                    color_rgb = list(color_to_apply[:3])
                    while len(color_rgb) < 3:
                        color_rgb.append(1.0)
                    obj.color = (color_rgb[0], color_rgb[1], color_rgb[2], alpha)

            obj.hide_render = obj.hide_viewport
            applied_count += 1

        cls.set_object_shading()

    @classmethod
    def get_task_for_product(cls, product):
        """Get the task associated with an IFC product."""
        element = tool.Ifc.get_entity(product) if hasattr(product, 'name') else product
        if not element:
            return None

        # Search in outputs
        for rel in element.ReferencedBy or []:
            if rel.is_a("IfcRelAssignsToProduct"):
                for task in rel.RelatedObjects:
                    if task.is_a("IfcTask"):
                        return task

        # Search in inputs
        for rel in element.HasAssignments or []:
            if rel.is_a("IfcRelAssignsToProcess"):
                task = rel.RelatingProcess
                if task.is_a("IfcTask"):
                    return task

        return None

    @classmethod
    def _save_original_object_colors(cls):
        """Save original object colors for restoration."""
        import bpy
        import json

        original_properties = {}
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and tool.Ifc.get_entity(obj):
                original_color = None
                try:
                    if obj.material_slots and obj.material_slots[0].material:
                        material = obj.material_slots[0].material
                        if material.use_nodes:
                            principled = tool.Blender.get_material_node(material, "BSDF_PRINCIPLED")
                            if principled and principled.inputs.get("Base Color"):
                                base_color = principled.inputs["Base Color"].default_value
                                original_color = [base_color[0], base_color[1], base_color[2], base_color[3]]
                except Exception:
                    pass

                if original_color is None:
                    original_color = list(obj.color)

                original_properties[obj.name] = {
                    "color": original_color,
                    "hide_viewport": obj.hide_viewport,
                    "hide_render": obj.hide_render,
                }

        bpy.context.scene['BIM_VarianceOriginalObjectColors'] = json.dumps(original_properties)

    @classmethod
    def set_object_shading(cls):
        """Set proper object shading for visualization."""
        import bpy

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'SOLID'
                        space.shading.color_type = 'OBJECT'