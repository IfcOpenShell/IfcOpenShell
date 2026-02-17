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
from datetime import datetime
import ifcopenshell
import ifcopenshell.util.date
import bonsai.tool as tool

class AnimationSetupSequence:
    """Mixin class for the 4D animation setup and general utilities."""

    @classmethod
    def set_object_shading(cls):
        area = tool.Blender.get_view3d_area()
        if area:
            # Use area.spaces.active for stability in newer Blender versions
            space = area.spaces.active
            if space and space.type == 'VIEW_3D':
                space.shading.color_type = "OBJECT"

    @classmethod
    def get_animation_settings(cls):
        """
        CORRECTION: Ensure that it uses the configured visualization dates,
        not dates derived from tasks.
        """
        def calculate_total_frames(fps):
            if props.speed_types == "FRAME_SPEED":
                return calculate_using_frames(
                    start,
                    finish,
                    props.speed_animation_frames,
                    ifcopenshell.util.date.parse_duration(props.speed_real_duration),
                )
            elif props.speed_types == "DURATION_SPEED":
                animation_duration = ifcopenshell.util.date.parse_duration(props.speed_animation_duration)
                real_duration = ifcopenshell.util.date.parse_duration(props.speed_real_duration)
                return calculate_using_duration(
                    start,
                    finish,
                    fps,
                    animation_duration,
                    real_duration,
                )
            elif props.speed_types == "MULTIPLIER_SPEED":
                return calculate_using_multiplier(
                    start,
                    finish,
                    1,
                    props.speed_multiplier,
                )

        def calculate_using_multiplier(start, finish, fps, multiplier):
            animation_time = (finish - start) / multiplier
            return animation_time.total_seconds() * fps

        def calculate_using_duration(start, finish, fps, animation_duration, real_duration):
            return calculate_using_multiplier(start, finish, fps, real_duration / animation_duration)

        def calculate_using_frames(start, finish, animation_frames, real_duration):
            return ((finish - start) / real_duration) * animation_frames

        props = tool.Sequence.get_work_schedule_props()
        # Get visualization dates: first UI, if missing, infer from active schedule
        viz_start_prop = getattr(props, "visualisation_start", None)
        viz_finish_prop = getattr(props, "visualisation_finish", None)

        inferred_start = None
        inferred_finish = None
        if not (viz_start_prop and viz_finish_prop):
            try:
                ws = cls.get_active_work_schedule()
                if ws:
                    inferred_start, inferred_finish = cls.guess_date_range(ws)
            except Exception:
                inferred_start, inferred_finish = (None, None)

        def _to_dt(v):
            try:
                from datetime import datetime as _dt, date as _d
                if isinstance(v, _dt):
                    return v.replace(microsecond=0)
                if isinstance(v, _d):
                    return _dt(v.year, v.month, v.day)
                s = str(v)
                try:
                    if "T" in s or " " in s:
                        s2 = s.replace(" ", "T")
                        return _dt.fromisoformat(s2[:19])
                    if len(s) >= 10 and s[4] == "-" and s[7] == "-":
                        return _dt.fromisoformat(s[:10])
                except Exception:
                    pass
                from dateutil import parser as _p
                return _p.parse(s, yearfirst=True, dayfirst=False, fuzzy=True)
            except Exception:
                try:
                    from dateutil import parser as _p
                    return _p.parse(str(v), yearfirst=True, dayfirst=True, fuzzy=True)
                except Exception:
                    return None

        if viz_start_prop and viz_finish_prop:
            start = cls.get_start_date()
            finish = cls.get_finish_date()
        else:
            start = _to_dt(inferred_start)
            finish = _to_dt(inferred_finish)
            try:
                if start and finish:
                    props.visualisation_start = ifcopenshell.util.date.canonicalise_time(start)
                    props.visualisation_finish = ifcopenshell.util.date.canonicalise_time(finish)
            except Exception:
                pass

        if not start or not finish:
            print("[ERROR] Could not determine visualization dates (neither UI nor inferred)")
            return None

        try:
            start = start.replace(microsecond=0)
            finish = finish.replace(microsecond=0)
        except Exception:
            pass

        if finish <= start:
            try:
                from datetime import timedelta as _td
                if finish == start:
                    finish = start + _td(days=1)
                else:
                    print(f"[ERROR] Error: Finish date ({finish}) must be after start date ({start})")
                    return None
            except Exception:
                print(f"[ERROR] Error adjusting date range: start={start}, finish={finish}")
                return None

        duration = finish - start
        # Use frame_start from the scene if it exists; default 1
        try:
            start_frame = int(getattr(bpy.context.scene, 'frame_start', 1) or 1)
        except Exception:
            start_frame = 1

        # Calculate total frames based on speed settings
        try:
            fps = int(getattr(bpy.context.scene.render, 'fps', 24) or 24)
        except Exception:
            fps = 24
        total_frames = int(round(calculate_total_frames(fps)))

        print(f"[INFO] Animation Settings:")
        try:
            print(f"   Start Date: {start.strftime('%Y-%m-%d')}")
            print(f"   Finish Date: {finish.strftime('%Y-%m-%d')}")
        except Exception:
            print(f"   Start Date: {start}")
            print(f"   Finish Date: {finish}")
        print(f"   Duration: {duration.days} days")
        print(f"   Start Frame: {start_frame}")
        print(f"   Total Frames: {total_frames}")

        return {
            "start": start,
            "finish": finish,
            "duration": duration,
            "start_frame": start_frame,
            "total_frames": total_frames,
            "schedule_start": None,
            "schedule_finish": None,
        }

    @classmethod
    def _get_best_ColorType_for_task(cls, task, anim_props):
        """Determines the most appropriate profile for a task considering the group stack and task choice."""
        try:
            # Determine the active group (first enabled group in the stack) or DEFAULT
            agn = None
            for it in getattr(anim_props, 'animation_group_stack', []):
                if getattr(it, 'enabled', False) and getattr(it, 'group', None):
                    agn = it.group
                    break
            if not agn:
                agn = 'DEFAULT'
            ColorType = tool.Sequence.get_assigned_ColorType_for_task(task, anim_props, agn)
            if ColorType:
                return ColorType
        except Exception:
            pass
        predefined_type = task.PredefinedType or "NOTDEFINED"
        # Try in DEFAULT
        try:
            prof = cls.load_ColorType_from_group("DEFAULT", predefined_type)
            if prof:
                return prof
        except Exception:
            pass
        # Fallback to NotDefined
        try:
            prof = cls.load_ColorType_from_group("DEFAULT", "NOTDEFINED")
            if prof:
                return prof
        except Exception:
            pass
        # Final fallback: return DEFAULT profile with all flags set to False
        from types import SimpleNamespace
        return SimpleNamespace(
            name="DEFAULT",
            consider_start=False,
            consider_active=True,
            consider_end=True,
        )

    @classmethod
    def debug_ColorType_application(cls, obj, ColorType, frame_data):
        """Debug helper to verify profile application"""
        print("ColorType Application Check:")
        print(f"   Object: {obj.name}")
        print(f"   ColorType: {getattr(ColorType, 'name', 'Unknown')}")
        print(f"   consider_start: {getattr(ColorType, 'consider_start', False)}")
        print(f"   consider_active: {getattr(ColorType, 'consider_active', True)}")
        print(f"   consider_end: {getattr(ColorType, 'consider_end', True)}")
        print(f"   Frame states: {frame_data.get('states', {})}")
        print(f"   Relationship: {frame_data.get('relationship', 'unknown')}")

    @classmethod
    def _task_has_consider_start_ColorType(cls, task):
        """Helper to check if a task's resolved ColorType has consider_start=True."""
        try:
            # Re-use existing logic to find the best ColorType for the task
            anim_props = tool.Sequence.get_animation_props()
            ColorType = tool.Sequence._get_best_ColorType_for_task(task, anim_props)
            return getattr(ColorType, 'consider_start', False)
        except Exception as e:
            print(f"[WARNING] Error in _task_has_consider_start_ColorType for task {getattr(task, 'Name', 'N/A')}: {e}")
            return False