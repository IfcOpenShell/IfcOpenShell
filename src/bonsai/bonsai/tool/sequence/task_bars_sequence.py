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
import mathutils
import ifcopenshell
import bonsai.tool as tool
from .props_sequence import PropsSequence

from .date_utils_sequence import DateUtilsSequence

class TaskBarsSequence:
    """Mixin class for managing 3D task bars visualization."""

    @classmethod
    def get_task_bar_list(cls) -> list[int]:
        """
        Gets the list of task IDs that should display a visual bar.
        Returns a list of task IDs.
        """
        props = tool.Sequence.get_work_schedule_props()
        try:
            task_bars = json.loads(props.task_bars)
            return task_bars if isinstance(task_bars, list) else []
        except Exception:
            return []

    @classmethod
    def add_task_bar(cls, task_id: int) -> None:
        """Adds a task to the list of visual bars."""
        props = tool.Sequence.get_work_schedule_props()
        try:
            task_bars = json.loads(props.task_bars)
        except Exception:
            task_bars = []
        if task_id not in task_bars:
            task_bars.append(task_id)
            props.task_bars = json.dumps(task_bars)

    @classmethod
    def remove_task_bar(cls, task_id: int) -> None:
        """Removes a task from the list of visual bars."""
        props = tool.Sequence.get_work_schedule_props()
        try:
            task_bars = json.loads(props.task_bars)
        except Exception:
            task_bars = []
        if task_id in task_bars:
            task_bars.remove(task_id)
            props.task_bars = json.dumps(task_bars)

    @classmethod
    def get_animation_bar_tasks(cls) -> list:
        """Gets the IFC tasks that have visual bars enabled."""
        task_ids = cls.get_task_bar_list()
        tasks = []
        ifc_file = tool.Ifc.get()
        if ifc_file:
            for task_id in task_ids:
                try:
                    task = ifc_file.by_id(task_id)
                    if task and cls.validate_task_object(task, "get_animation_bar_tasks"):
                        tasks.append(task)
                except Exception as e:
                    pass
        return tasks

    @classmethod
    def refresh_task_bars(cls) -> None:
        """Updates the visualization of task bars in the viewport."""
        try:
            # Check if animation is active for safer operations
            try:
                anim_props = tool.Sequence.get_animation_props()
                is_animation_active = getattr(anim_props, 'is_animation_created', False)
                if is_animation_active:
                    # Continue but with more care.
                    pass
            except Exception:
                pass  # If it cannot be verified, continue normally.

            tasks = cls.get_animation_bar_tasks()
            if not tasks:
                if "Bar Visual" in bpy.data.collections:
                    collection = bpy.data.collections["Bar Visual"]
                    for obj in list(collection.objects):
                        bpy.data.objects.remove(obj)
                return
            cls.create_bars(tasks)
        except Exception:
            # Do not re-raise to avoid crashes - just log the error.
            import traceback
            traceback.print_exc()

    @classmethod
    def clear_task_bars(cls) -> None:
        """Clears and removes all 3D task bars and resets the state in the UI."""
        import bpy

        # 1. Clear the list of tasks marked to have bars.
        props = tool.Sequence.get_work_schedule_props()
        props.task_bars = "[]"  # Reset to an empty JSON list.

        # 2. Uncheck all checkboxes in the user interface.
        tprops = tool.Sequence.get_task_tree_props()
        for task in getattr(tprops, "tasks", []):
            if getattr(task, "has_bar_visual", False):
                task.has_bar_visual = False

        # 3. Remove the 3D objects collection from the bars.
        collection_name = "Bar Visual"
        if collection_name in bpy.data.collections:
            collection = bpy.data.collections[collection_name]
            # Remove all objects within the collection.
            for obj in list(collection.objects):
                bpy.data.objects.remove(obj, do_unlink=True)
            # Remove the empty collection.
            bpy.data.collections.remove(collection)

    @classmethod
    def create_bars(cls, tasks):
        full_bar_thickness = 0.2
        size = 1.0
        vertical_spacing = 3.5
        vertical_increment = 0
        size_to_duration_ratio = 1 / 30
        margin = 0.2

        # Filter invalid tasks before any use.
        if tasks:
            _valid = []
            for _t in tasks:
                if cls.validate_task_object(_t, "create_bars"):
                    _valid.append(_t)
                else:
                    pass
            if not _valid:
                return
            tasks = _valid
        else:
            print("[WARNING]️ Warning: No tasks provided to create_bars")
            return

        def process_task_data(task, settings):
            # Verify valid task.
            if not cls.validate_task_object(task, "process_task_data"):
                return None

            try:
                task_start_date = ifcopenshell.util.sequence.derive_date(task, "ScheduleStart", is_earliest=True)
                finish_date = ifcopenshell.util.sequence.derive_date(task, "ScheduleFinish", is_latest=True)
            except Exception as e:
                print(f"[WARNING]️ Error deriving dates for task {getattr(task, 'Name', 'Unknown')}: {e}")
                return None

            if not (task_start_date and finish_date):
                print(f"[WARNING]️ Warning: Task {getattr(task, 'Name', 'Unknown')} has no valid dates")
                return None

            try:
                # Use the schedule dates for calculations.
                schedule_start = settings["viz_start"]
                schedule_finish = settings["viz_finish"]
                schedule_duration = schedule_finish - schedule_start

                if schedule_duration.total_seconds() <= 0:
                    print(f"[WARNING]️ Invalid schedule duration: {schedule_duration}")
                    return None

                total_frames = settings["end_frame"] - settings["start_frame"]

                # Calculate task position within the full schedule.
                task_start_progress = (task_start_date - schedule_start).total_seconds() / schedule_duration.total_seconds()
                task_finish_progress = (finish_date - schedule_start).total_seconds() / schedule_duration.total_seconds()

                # Convert to frames.
                task_start_frame = round(settings["start_frame"] + (task_start_progress * total_frames))
                task_finish_frame = round(settings["start_frame"] + (task_finish_progress * total_frames))

                # Validate that frames are in valid range.
                task_start_frame = max(settings["start_frame"], min(settings["end_frame"], task_start_frame))
                task_finish_frame = max(settings["start_frame"], min(settings["end_frame"], task_finish_frame))

                return {
                    "name": getattr(task, "Name", "Unnamed"),
                    "start_date": task_start_date,
                    "finish_date": finish_date,
                    "start_frame": task_start_frame,
                    "finish_frame": task_finish_frame,
                }
            except Exception as e:
                print(f"[WARNING]️ Error calculating frames for task {getattr(task, 'Name', 'Unknown')}: {e}")
                return None

        def create_task_bar_data(tasks, vertical_increment, collection):
            # Use active schedule dates, NOT visualization dates.
            schedule_start, schedule_finish = cls.get_schedule_date_range()

            if not (schedule_start and schedule_finish):
                # Fallback: if there are no schedule dates, show message and abort.
                print("[ERROR] Cannot create Task Bars: schedule dates not available")
                return None

            settings = {
                # Use schedule dates instead of visualization.
                "viz_start": schedule_start,
                "viz_finish": schedule_finish,
                "start_frame": bpy.context.scene.frame_start,
                "end_frame": bpy.context.scene.frame_end,
            }

            print(f"🎯 Task Bars using schedule dates:")
            print(f"   Schedule Start: {schedule_start.strftime('%Y-%m-%d')}")
            print(f"   Schedule Finish: {schedule_finish.strftime('%Y-%m-%d')}")
            print(f"   Timeline: frames {settings['start_frame']} to {settings['end_frame']}")

            material_progress, material_full = get_animation_materials()
            empty = bpy.data.objects.new("collection_origin", None)
            link_collection(empty, collection)

            for task in tasks:
                task_data = process_task_data(task, settings)
                if task_data:
                    position_shift = task_data["start_frame"] * size_to_duration_ratio
                    bar_size = (task_data["finish_frame"] - task_data["start_frame"]) * size_to_duration_ratio

                    anim_props = tool.Sequence.get_animation_props()
                    color_progress = anim_props.color_progress
                    bar = add_bar(
                        material=material_progress,
                        vertical_increment=vertical_increment,
                        collection=collection,
                        parent=empty,
                        task=task_data,
                        scale=True,
                        color=(color_progress[0], color_progress[1], color_progress[2], 1.0),
                        shift_x=position_shift,
                        name=task_data["name"] + "/Progress Bar",
                    )

                    color_full = anim_props.color_full
                    bar2 = add_bar(
                        material=material_full,
                        vertical_increment=vertical_increment,
                        parent=empty,
                        collection=collection,
                        task=task_data,
                        color=(color_full[0], color_full[1], color_full[2], 1.0),
                        shift_x=position_shift,
                        name=task_data["name"] + "/Full Bar",
                    )
                    bar2.color = (color_full[0], color_full[1], color_full[2], 1.0)

                    bar2.scale = (full_bar_thickness, bar_size, 1)
                    shift_object(bar2, y=((size + full_bar_thickness) / 2))

                    start_text = add_text(
                        task_data["start_date"].strftime("%d/%m/%y"),
                        0,
                        "RIGHT",
                        vertical_increment,
                        parent=empty,
                        collection=collection,
                    )
                    start_text.name = task_data["name"] + "/Start Date"
                    shift_object(start_text, x=position_shift - margin, y=-(size + full_bar_thickness))

                    task_text = add_text(
                        task_data["name"],
                        0,
                        "RIGHT",
                        vertical_increment,
                        parent=empty,
                        collection=collection,
                    )
                    task_text.name = task_data["name"] + "/Task Name"
                    shift_object(task_text, x=position_shift, y=0.2)

                    finish_text = add_text(
                        task_data["finish_date"].strftime("%d/%m/%y"),
                        bar_size,
                        "LEFT",
                        vertical_increment,
                        parent=empty,
                        collection=collection,
                    )
                    finish_text.name = task_data["name"] + "/Finish Date"
                    shift_object(finish_text, x=position_shift + margin, y=-(size + full_bar_thickness))

                vertical_increment += vertical_spacing

            return empty.select_set(True) if empty else None

        def set_material(name, r, g, b):
            material = bpy.data.materials.new(name)
            material.use_nodes = True
            tool.Blender.get_material_node(material, "BSDF_PRINCIPLED").inputs[0].default_value = (r, g, b, 1.0)
            return material

        def get_animation_materials():
            if "color_progress" in bpy.data.materials:
                material_progress = bpy.data.materials["color_progress"]
            else:
                material_progress = set_material("color_progress", 0.0, 1.0, 0.0)
            if "color_full" in bpy.data.materials:
                material_full = bpy.data.materials["color_full"]
            else:
                material_full = set_material("color_full", 1.0, 0.0, 0.0)
            return material_progress, material_full

        def animate_scale(bar, task):
            scale = (1, size_to_duration_ratio, 1)
            bar.scale = scale
            bar.keyframe_insert(data_path="scale", frame=task["start_frame"])
            scale2 = (1, (task["finish_frame"] - task["start_frame"]) * size_to_duration_ratio, 1)
            bar.scale = scale2
            bar.keyframe_insert(data_path="scale", frame=task["finish_frame"])

        def animate_color(bar, task, color):
            bar.keyframe_insert(data_path="color", frame=task["start_frame"])
            bar.color = color
            bar.keyframe_insert(data_path="color", frame=task["start_frame"] + 1)
            bar.color = color

        def place_bar(bar, vertical_increment):
            for vertex in bar.data.vertices:
                vertex.co[1] += 0.5
            bar.rotation_euler[2] = -1.5708
            shift_object(bar, y=-vertical_increment)

        def shift_object(obj, x=0.0, y=0.0, z=0.0):
            vec = mathutils.Vector((x, y, z))
            inv = obj.matrix_world.copy()
            inv.invert()
            vec_rot = vec @ inv
            obj.location = obj.location + vec_rot

        def link_collection(obj, collection):
            if collection:
                collection.objects.link(obj)
                if obj.name in bpy.context.scene.collection.objects.keys():
                    bpy.context.scene.collection.objects.unlink(obj)
            return obj

        def create_plane(material, collection, vertical_increment):
            x = 0.5
            y = 0.5
            vert = [(-x, -y, 0.0), (x, -y, 0.0), (-x, y, 0.0), (x, y, 0.0)]
            fac = [(0, 1, 3, 2)]
            mesh = bpy.data.meshes.new("PL")
            mesh.from_pydata(vert, [], fac)
            obj = bpy.data.objects.new("PL", mesh)
            obj.data.materials.append(material)
            place_bar(obj, vertical_increment)
            link_collection(obj, collection)
            return obj

        def add_text(text, x_position, align, vertical_increment, parent=None, collection=None):
            data = bpy.data.curves.new(type="FONT", name="Timeline")
            data.align_x = align
            data.align_y = "CENTER"

            data.body = text
            obj = bpy.data.objects.new(name="Unnamed", object_data=data)
            link_collection(obj, collection)
            shift_object(obj, x=x_position, y=-(vertical_increment - 1))
            if parent:
                obj.parent = parent
            return obj

        def add_bar(
            material,
            vertical_increment,
            parent=None,
            collection=None,
            task=None,
            color=False,
            scale=False,
            shift_x=None,
            name=None,
        ):
            plane = create_plane(material, collection, vertical_increment)
            if parent:
                plane.parent = parent
            if color:
                animate_color(plane, task, color)
            if scale:
                animate_scale(plane, task)
            if shift_x:
                shift_object(plane, x=shift_x)
            if name:
                plane.name = name
            return plane

        if "Bar Visual" in bpy.data.collections:
            collection = bpy.data.collections["Bar Visual"]
            for obj in collection.objects:
                bpy.data.objects.remove(obj)

        else:
            collection = bpy.data.collections.new("Bar Visual")
            bpy.context.scene.collection.children.link(collection)

        if tasks:
            create_task_bar_data(tasks, vertical_increment, collection)