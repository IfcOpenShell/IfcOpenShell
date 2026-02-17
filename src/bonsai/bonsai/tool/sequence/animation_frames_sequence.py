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
import ifcopenshell
import ifcopenshell.util.sequence
import ifcopenshell.util.date
import bonsai.tool as tool
from typing import Any

# Try to import data module for interpolate_ColorType_values function
try:
    from bonsai.bim.module.sequence.data import interpolate_ColorType_values
    class _seq_data:
        interpolate_ColorType_values = staticmethod(interpolate_ColorType_values)
except ImportError:
    try:
        import bonsai.data as _seq_data
    except ImportError:
        # Fallback: Create a dummy data module
        class _seq_data:
            @staticmethod
            def interpolate_ColorType_values(ColorType, state, progress=0.0):
                # Return default values if optimization is not available
                return {'alpha': 1.0}

class AnimationFramesSequence:
    """Mixin class for calculating animation frame data for IFC products."""

    @classmethod
    def get_task_for_product(cls, product):
        """Gets the task associated with an IFC product."""
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

    def get_animation_product_frames(self, work_schedule, settings):
        """
        Calculates animation frames with a high-performance approach.
        Uses date caching and drastically reduces repetitive operations.
        """
        import time
        from datetime import datetime

        print("Starting frame calculation with final optimization...")
        start_time = time.time()

        # Get all products from the work schedule by collecting from all tasks
        import ifcopenshell.util.sequence
        products = []

        def get_all_tasks_recursive(tasks):
            all_tasks = []
            for task in tasks:
                all_tasks.append(task)
                nested = ifcopenshell.util.sequence.get_nested_tasks(task)
                if nested:
                    all_tasks.extend(get_all_tasks_recursive(nested))
            return all_tasks

        root_tasks = ifcopenshell.util.sequence.get_root_tasks(work_schedule)
        all_tasks = get_all_tasks_recursive(root_tasks)

        # Collect all products from tasks (outputs and inputs)
        for task in all_tasks:
            task_outputs = ifcopenshell.util.sequence.get_task_outputs(task)
            if task_outputs:
                products.extend(task_outputs)
            task_inputs = ifcopenshell.util.sequence.get_task_inputs(task)
            if task_inputs:
                products.extend(task_inputs)

        # Remove duplicates
        products = list(set(products))

        if not products:
            return {}

        start_date_str = settings.get("start")
        finish_date_str = settings.get("finish")

        if not start_date_str or not finish_date_str:
            print("   - No start/end dates provided. Calculating from tasks...")
            all_dates = []
            for task in all_tasks:
                task_start = ifcopenshell.util.sequence.derive_date(task, "ScheduleStart", is_earliest=True)
                task_end = ifcopenshell.util.sequence.derive_date(task, "ScheduleFinish", is_latest=True)
                if task_start: all_dates.append(task_start)
                if task_end: all_dates.append(task_end)

            if not all_dates: return {}
            start_date = min(all_dates)
            finish_date = max(all_dates)
        else:
            start_date = datetime.fromisoformat(start_date_str)
            finish_date = datetime.fromisoformat(finish_date_str)

        duration = (finish_date - start_date).total_seconds()
        if duration <= 0:
            return {}

        total_frames = settings.get("total_frames", 250)
        start_frame = settings.get("start_frame", 1)

        # --- KEY OPTIMIZATION: DATE CACHE ---
        date_to_frame_cache = {}
        def date_to_frame(d):
            # Avoid recalculating if the date was already processed
            if d in date_to_frame_cache:
                return date_to_frame_cache[d]

            progress = (d - start_date).total_seconds() / duration
            frame = start_frame + (total_frames * progress)
            result = max(start_frame, min(start_frame + total_frames, frame))
            date_to_frame_cache[d] = result
            return result

        result = {}

        # --- OPTIMIZED LOOP ---
        for product in products:
            # Find tasks that have this product as input or output
            tasks = {}
            for task in all_tasks:
                task_outputs = ifcopenshell.util.sequence.get_task_outputs(task)
                if product in task_outputs:
                    tasks[task] = "output"

                task_inputs = ifcopenshell.util.sequence.get_task_inputs(task)
                if product in task_inputs:
                    tasks[task] = "input"

            if not tasks:
                continue

            product_frames = []
            for task, rel in tasks.items():
                task_start = ifcopenshell.util.sequence.derive_date(task, "ScheduleStart", is_earliest=True)
                task_end = ifcopenshell.util.sequence.derive_date(task, "ScheduleFinish", is_latest=True)

                if not task_start or not task_end or task_start >= task_end:
                    continue

                frame_start = date_to_frame(task_start)
                frame_end = date_to_frame(task_end)

                product_frames.append({
                    "task": task,
                    "relationship": rel,
                    "states": {
                        "before_start": (start_frame, frame_start - 1),
                        "active": (frame_start, frame_end),
                        "after_end": (frame_end + 1, start_frame + total_frames),
                    },
                })

            if product_frames:
                result[product.id()] = product_frames

        end_time = time.time()
        print(f"   - TOOL: Frame calculation completed in {end_time - start_time:.3f}s for {len(result)} products.")
        return result

    @classmethod
    def get_animation_product_frames_enhanced(cls, work_schedule: ifcopenshell.entity_instance, settings: dict[str, Any]):
        animation_start = int(settings["start_frame"])
        animation_end = int(settings["start_frame"] + settings["total_frames"])
        viz_start = settings["start"]
        viz_finish = settings["finish"]
        viz_duration = settings["duration"]
        product_frames: dict[int, list] = {}

        # --- Get the date source from properties ---
        props = tool.Sequence.get_work_schedule_props()
        date_source = getattr(props, "date_source_type", "SCHEDULE")
        start_date_type = f"{date_source.capitalize()}Start"
        finish_date_type = f"{date_source.capitalize()}Finish"

        def add_product_frame_enhanced(product_id, task, start_date, finish_date, start_frame, finish_frame, relationship):
            if finish_date < viz_start:
                states = {
                    "before_start": (animation_start, animation_start - 1),
                    "active": (animation_start, animation_start - 1),
                    "after_end": (animation_start, animation_end),
                }
            elif start_date > viz_finish:
                return
            else:
                s_vis = max(animation_start, int(start_frame))
                f_vis = min(animation_end, int(finish_frame))
                if f_vis < s_vis:
                    s_vis = max(animation_start, min(animation_end, s_vis))
                    f_vis = s_vis
                before_end = s_vis - 1
                after_start = f_vis + 1
                states = {
                    "before_start": (animation_start, before_end) if before_end >= animation_start else (animation_start, animation_start - 1),
                    "active": (s_vis, f_vis),
                    "after_end": (after_start if after_start <= animation_end else animation_end + 1, animation_end),
                }

            product_frames.setdefault(product_id, []).append({
                "task": task, "task_id": task.id(),
                "type": getattr(task, "PredefinedType", "NOTDEFINED"),
                "relationship": relationship,
                "start_date": start_date, "finish_date": finish_date,
                "STARTED": int(start_frame), "COMPLETED": int(finish_frame),
                "start_frame": max(animation_start, int(start_frame)),
                "finish_frame": min(animation_end, int(finish_frame)),
                "states": states,
            })

        def add_product_frame_full_range(product_id, task, relationship):
            states = { "active": (animation_start, animation_end) }
            frame_data = {
                "task": task, "task_id": task.id(),
                "type": getattr(task, "PredefinedType", "NOTDEFINED"),
                "relationship": relationship,
                "start_date": viz_start, "finish_date": viz_finish,
                "STARTED": animation_start, "COMPLETED": animation_end,
                "start_frame": animation_start, "finish_frame": animation_end,
                "states": states,
                "consider_start_active": True,
            }
            product_frames.setdefault(product_id, []).append(frame_data)
            # Product created with consider_start_active=True
            print(f"   Task: {task.Name}")
            print(f"   Relationship: {relationship}")
            print(f"   States: {states}")
            print(f"   Frame data: {frame_data}")

        def preprocess_task(task):
            for subtask in ifcopenshell.util.sequence.get_nested_tasks(task):
                preprocess_task(subtask)

            # --- Use the selected date source ---
            task_start = ifcopenshell.util.sequence.derive_date(task, start_date_type, is_earliest=True)
            task_finish = ifcopenshell.util.sequence.derive_date(task, finish_date_type, is_latest=True)
            if not task_start or not task_finish:
                return

            # Get the complete profile to verify the state combination, not just 'consider_start'.
            ColorType = tool.Sequence._get_best_ColorType_for_task(task, tool.Sequence.get_animation_props())
            consider_start = getattr(ColorType, 'consider_start', False)
            consider_active = getattr(ColorType, 'consider_active', True)
            consider_end = getattr(ColorType, 'consider_end', True)

            is_priority_mode = (consider_start and not consider_active and not consider_end)

            # Task processing started
            print(f"   ColorType: {getattr(ColorType, 'name', 'Unknown')}")
            print(f"   consider_start: {consider_start}")
            print(f"   consider_active: {consider_active}")
            print(f"   consider_end: {consider_end}")
            print(f"   is_priority_mode: {is_priority_mode}")

            # If it is priority mode, IGNORE DATES and use the full range.
            if is_priority_mode:
                print(f"🔒 Task '{task.Name}' in priority mode. Ignoring dates.")
                for output in ifcopenshell.util.sequence.get_task_outputs(task):
                    add_product_frame_full_range(output.id(), task, "output")
                for input_prod in tool.Sequence.get_task_inputs(task):
                    add_product_frame_full_range(input_prod.id(), task, "input")
                return

            # If it is NOT priority mode, use the task dates to calculate the frames.
            if task_start > viz_finish:
                return

            if viz_duration.total_seconds() > 0:
                start_progress = (task_start - viz_start).total_seconds() / viz_duration.total_seconds()
                finish_progress = (task_finish - viz_start).total_seconds() / viz_duration.total_seconds()
            else:
                start_progress, finish_progress = 0.0, 1.0

            sf = int(round(settings["start_frame"] + (start_progress * settings["total_frames"])))
            ff = int(round(settings["start_frame"] + (finish_progress * settings["total_frames"])))

            for output in ifcopenshell.util.sequence.get_task_outputs(task):
                add_product_frame_enhanced(output.id(), task, task_start, task_finish, sf, ff, "output")
            for input_prod in tool.Sequence.get_task_inputs(task):
                add_product_frame_enhanced(input_prod.id(), task, task_start, task_finish, sf, ff, "input")

        for root_task in ifcopenshell.util.sequence.get_root_tasks(work_schedule):
            preprocess_task(root_task)

        return product_frames

    @classmethod
    def get_product_frames_with_ColorTypes(cls, work_schedule, settings):
        """Enhanced version with profile support and compatible 'states'.
        If the 'get_animation_product_frames_enhanced' method exists, it uses it and returns its structure,
        thus ensuring compatibility with apply_ColorType_animation.
        """
        # Guarantees the DEFAULT group exists if the user has not configured anything
        try:
            from bonsai.bim.module.sequence.prop import UnifiedColorTypeManager
            UnifiedColorTypeManager.ensure_default_group(bpy.context)
        except Exception:
            pass

        # We prefer the existing 'enhanced' path to maintain compatibility
        try:
            frames = cls.get_animation_product_frames_enhanced(work_schedule, settings)
            if isinstance(frames, dict):
                return frames
        except Exception:
            pass

        # Fallback: build product->frames with minimal states from the basic method
        basic = cls.get_animation_product_frames(work_schedule, settings)
        product_frames = {}
        for pid, items in (basic or {}).items():
            product_frames[pid] = []
            for it in items:
                start_f = it.get("STARTED")
                finish_f = it.get("COMPLETED")
                if start_f is None or finish_f is None:
                    continue
                product_frames[pid].append({
                    "task": None,
                    "task_id": 0,
                    "type": it.get("type") or "NOTDEFINED",
                    "relationship": it.get("relationship") or "output",
                    "start_date": settings.get("start"),
                    "finish_date": settings.get("finish"),
                    "STARTED": start_f,
                    "COMPLETED": finish_f,
                    "start_frame": start_f,
                    "finish_frame": finish_f,
                    "states": {
                        "before_start": (settings["start_frame"], max(settings["start_frame"], int(start_f) - 1)),
                        "active": (int(start_f), int(finish_f)),
                        "after_end": (min(int(finish_f) + 1, int(settings["start_frame"] + settings["total_frames"])), int(settings["start_frame"] + settings["total_frames"])),
                    },
                })
        return product_frames

    @classmethod
    def get_animation_product_frames_enhanced_optimized(cls, work_schedule, settings, lookup_optimizer, date_cache):
        """ULTRA-OPTIMIZED version using pre-computed lookup tables and cache"""
        import time
        start_time = time.time()
        print("Using optimized animation product frames with priority mode support")

        animation_start = int(settings["start_frame"])
        animation_end = int(settings["start_frame"] + settings["total_frames"])
        viz_start = settings["start"]
        viz_finish = settings["finish"]
        viz_duration = settings["duration"]
        product_frames = {}

        # Get date source from properties
        props = tool.Sequence.get_work_schedule_props()
        date_source = getattr(props, "date_source_type", "SCHEDULE")
        start_date_type = f"{date_source.capitalize()}Start"
        finish_date_type = f"{date_source.capitalize()}Finish"

        all_tasks = lookup_optimizer.get_all_tasks()
        print(f"[OPTIMIZED] OPTIMIZED FRAMES: Processing {len(all_tasks)} tasks")

        # Debug: Check if lookup optimizer has products
        total_products_in_lookup = len(lookup_optimizer.product_ids) if hasattr(lookup_optimizer, 'product_ids') else 0
        print(f"[DEBUG] Total products in lookup optimizer: {total_products_in_lookup}")

        tasks_processed = 0
        for task in all_tasks:
            try:
                print(f"[DEBUG] Processing task {task.id()}: {getattr(task, 'Name', 'N/A')}")

                # Check for priority mode
                ColorType = tool.Sequence._get_best_ColorType_for_task(task, tool.Sequence.get_animation_props())
                is_priority_mode = (
                    getattr(ColorType, 'consider_start', False) and
                    not getattr(ColorType, 'consider_active', True) and
                    not getattr(ColorType, 'consider_end', True)
                )

                # If priority mode, use full range and skip date-based logic
                if is_priority_mode:
                    print(f"🔒 OPTIMIZED PRIORITY MODE DETECTED: Task '{task.Name}' in priority mode.")
                    print(f"   ColorType: {getattr(ColorType, 'name', 'Unknown')}")
                    print(f"   consider_start: {getattr(ColorType, 'consider_start', False)}")
                    print(f"   consider_active: {getattr(ColorType, 'consider_active', True)}")
                    print(f"   consider_end: {getattr(ColorType, 'consider_end', True)}")

                    outputs_processed = 0
                    for output in lookup_optimizer.get_outputs_for_task(task.id()):
                        print(f"     - Adding OUTPUT product {output.id()} in PRIORITY mode")
                        cls._add_optimized_priority_frame(
                            product_frames, output.id(), task, "output", animation_start, animation_end
                        )
                        outputs_processed += 1

                    inputs_processed = 0
                    for input_prod in lookup_optimizer.get_inputs_for_task(task.id()):
                        print(f"     - Adding INPUT product {input_prod.id()} in PRIORITY mode")
                        cls._add_optimized_priority_frame(
                            product_frames, input_prod.id(), task, "input", animation_start, animation_end
                        )
                        inputs_processed += 1

                    print(f"   Products added: {outputs_processed} outputs, {inputs_processed} inputs")
                    print(f"   - Current product_frames count: {len(product_frames)}")
                    continue

                # Use date cache for instant access
                task_start = date_cache.get_date(task, start_date_type, is_earliest=True)
                task_finish = date_cache.get_date(task, finish_date_type, is_latest=True)

                if not task_start or not task_finish or task_start > viz_finish:
                    continue

                # Calculate frame positions with cache
                if viz_duration.total_seconds() > 0:
                    start_progress = (task_start - viz_start).total_seconds() / viz_duration.total_seconds()
                    finish_progress = (task_finish - viz_start).total_seconds() / viz_duration.total_seconds()
                else:
                    start_progress, finish_progress = 0.0, 1.0

                sf = int(round(settings["start_frame"] + (start_progress * settings["total_frames"])))
                ff = int(round(settings["start_frame"] + (finish_progress * settings["total_frames"])))

                outputs_added = 0
                for output in lookup_optimizer.get_outputs_for_task(task.id()):
                    print(f"     - Adding OUTPUT product {output.id()} in NORMAL mode")
                    cls._add_optimized_product_frame(
                        product_frames, output.id(), task, task_start, task_finish,
                        sf, ff, "output", animation_start, animation_end, viz_start, viz_finish
                    )
                    outputs_added += 1

                inputs_added = 0
                for input_prod in lookup_optimizer.get_inputs_for_task(task.id()):
                    print(f"     - Adding INPUT product {input_prod.id()} in NORMAL mode")
                    cls._add_optimized_product_frame(
                        product_frames, input_prod.id(), task, task_start, task_finish,
                        sf, ff, "input", animation_start, animation_end, viz_start, viz_finish
                    )
                    inputs_added += 1

                print(f"   - Added {outputs_added} outputs, {inputs_added} inputs in NORMAL mode")
                print(f"[DEBUG]   - Current product_frames count: {len(product_frames)}")

                tasks_processed += 1

            except Exception as e:
                print(f"[WARNING] Error processing task {task.id()}: {e}")
                continue

        elapsed = time.time() - start_time
        print(f"[OPTIMIZED] Optimized frames calculation completed in {elapsed:.3f}s")
        print(f"[OPTIMIZED] Tasks processed: {tasks_processed}")
        print(f"[OPTIMIZED] Product frames created: {len(product_frames)}")

        return product_frames

    @classmethod
    def _add_optimized_priority_frame(cls, product_frames, product_id, task, relationship, animation_start, animation_end):
        """Add priority mode frame (START only activated) to optimized product frames"""
        states = { "active": (animation_start, animation_end) }

        frame_data = {
            "task": task, "task_id": task.id(),
            "type": getattr(task, "PredefinedType", "NOTDEFINED"),
            "relationship": relationship,
            "start_date": None, "finish_date": None,  # Dates ignored in priority mode
            "STARTED": animation_start, "COMPLETED": animation_end,
            "start_frame": animation_start, "finish_frame": animation_end,
            "states": states,
            "consider_start_active": True,  # KEY FLAG for priority mode
        }

        product_frames.setdefault(product_id, []).append(frame_data)
        print(f"   Added priority frame for product {product_id}: consider_start_active={frame_data['consider_start_active']}")

    @classmethod
    def _add_optimized_product_frame(cls, product_frames, product_id, task, start_date, finish_date,
                                   start_frame, finish_frame, relationship, animation_start, animation_end,
                                   viz_start, viz_finish):
        """Optimized version of add_product_frame_enhanced"""
        # Fast state calculation
        if finish_date < viz_start:
            states = {
                "before_start": (animation_start, animation_start - 1),
                "active": (animation_start, animation_start - 1),
                "after_end": (animation_start, animation_end),
            }
        elif start_date > viz_finish:
            return
        else:
            s_vis = max(animation_start, int(start_frame))
            f_vis = min(animation_end, int(finish_frame))
            if f_vis < s_vis:
                s_vis = max(animation_start, min(animation_end, s_vis))
                f_vis = s_vis
            before_end = s_vis - 1
            after_start = f_vis + 1
            states = {
                "before_start": (animation_start, before_end) if before_end >= animation_start else (animation_start, animation_start - 1),
                "active": (s_vis, f_vis),
                "after_end": (after_start if after_start <= animation_end else animation_end + 1, animation_end),
            }

        # Create optimized frame data
        frame_data = {
            "task": task,
            "task_id": task.id(),
            "type": getattr(task, "PredefinedType", "NOTDEFINED"),
            "relationship": relationship,
            "start_date": start_date,
            "finish_date": finish_date,
            "STARTED": int(start_frame),
            "COMPLETED": int(finish_frame),
            "start_frame": max(animation_start, int(start_frame)),
            "finish_frame": min(animation_end, int(finish_frame)),
            "states": states,
        }

        product_frames.setdefault(product_id, []).append(frame_data)

    @classmethod
    def _process_task_with_ColorTypes(cls, task, settings, product_frames, anim_props, ColorType_cache):
        """Recursively processes a task, adding frames with states.
        Maintains compatibility with the 'enhanced' structure."""
        for subtask in ifcopenshell.util.sequence.get_nested_tasks(task):
            cls._process_task_with_ColorTypes(subtask, settings, product_frames, anim_props, ColorType_cache)

        # Dates
        start = ifcopenshell.util.sequence.derive_date(task, "ScheduleStart", is_earliest=True)
        finish = ifcopenshell.util.sequence.derive_date(task, "ScheduleFinish", is_latest=True)
        if not start or not finish:
            return

        start_frame = int(round(settings["start_frame"] + ((start - settings["start"]).total_seconds() / settings["duration"].total_seconds()) * settings["total_frames"]))
        finish_frame = int(round(settings["start_frame"] + ((finish - settings["start"]).total_seconds() / settings["duration"].total_seconds()) * settings["total_frames"]))

        # ColorType Cache
        task_id = task.id()
        if task_id not in ColorType_cache:
            ColorType_cache[task_id] = tool.Sequence._get_best_ColorType_for_task(task, anim_props)

        def _add(pid, relationship):
            product_frames.setdefault(pid, []).append({
                "task": task,
                "task_id": task.id(),
                "type": task.PredefinedType or "NOTDEFINED",
                "relationship": relationship,
                "start_date": start,
                "finish_date": finish,
                "STARTED": start_frame,
                "COMPLETED": finish_frame,
                "start_frame": start_frame,
                "finish_frame": finish_frame,
                "states": {
                    "before_start": (settings["start_frame"], max(settings["start_frame"], start_frame - 1)),
                    "active": (start_frame, finish_frame),
                    "after_end": (min(finish_frame + 1, int(settings["start_frame"] + settings["total_frames"])), int(settings["start_frame"] + settings["total_frames"])),
                },
            })

        # Add outputs and inputs
        for output in ifcopenshell.util.sequence.get_task_outputs(task):
            _add(output.id(), "output")
        for input_product in tool.Sequence.get_task_inputs(task):
            _add(input_product.id(), "input")