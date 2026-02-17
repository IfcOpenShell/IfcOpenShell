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
from datetime import timedelta, datetime
from .props_sequence import PropsSequence
# Import the date utility class that we will create next
from .date_utils_sequence import DateUtilsSequence

import bonsai.tool as tool
class TextSequence:
    """Mixin class for creating and managing 3D schedule texts."""

    _frame_change_handler = None


    @classmethod
    def _create_basic_snapshot_texts(cls, schedule_name):
        """Creates basic 3D texts manually when animation settings are not available."""
        import bpy
        
        # Create or get collection
        collection_name = "Schedule_Display_Texts"
        if collection_name not in bpy.data.collections:
            collection = bpy.data.collections.new(collection_name)
            try:
                bpy.context.scene.collection.children.link(collection)
            except Exception:
                pass
        else:
            collection = bpy.data.collections[collection_name]
        
        # Basic text configurations for snapshot
        text_configs = [
            {"name": "Schedule_Name", "position": (0, 10, 6), "content": f"Schedule: {schedule_name}", "type": "schedule_name"},
            {"name": "Schedule_Date", "position": (0, 10, 5), "content": "Date: [Dynamic]", "type": "date"},
            {"name": "Schedule_Week", "position": (0, 10, 4), "content": "Week: [Dynamic]", "type": "week"},
            {"name": "Schedule_Day_Counter", "position": (0, 10, 3), "content": "Day: [Dynamic]", "type": "day_counter"},
            {"name": "Schedule_Progress", "position": (0, 10, 2), "content": "Progress: [Dynamic]", "type": "progress"},
        ]
        
        for config in text_configs:
            try:
                # Create text data
                text_data = bpy.data.curves.new(name=config["name"], type='FONT')
                text_obj = bpy.data.objects.new(name=config["name"], object_data=text_data)
                
                # Set content and properties
                text_data.body = config["content"]
                text_data['text_type'] = config["type"]
                
                # Set alignment for consistent positioning
                if hasattr(text_data, 'align_x'):
                    text_data.align_x = 'CENTER'
                if hasattr(text_data, 'align_y'):
                    text_data.align_y = 'BOTTOM_BASELINE'
                
                # Position the text
                text_obj.location = config["position"]
                
                # Add to collection
                collection.objects.link(text_obj)


            except Exception as e:
                pass


    @classmethod
    def add_text_animation_handler(cls, settings):
        """Creates multiple animated text objects to display schedule information"""
        from datetime import timedelta

        collection_name = "Schedule_Display_Texts"
        if collection_name in bpy.data.collections:
            collection = bpy.data.collections[collection_name]
            for obj in list(collection.objects):
                try:
                    bpy.data.objects.remove(obj, do_unlink=True)
                except Exception:
                    pass
        else:
            collection = bpy.data.collections.new(collection_name)
            try:
                bpy.context.scene.collection.children.link(collection)
            except Exception:
                pass

        schedule_name = "Unknown Schedule"
        try:
            import bonsai.tool as tool
            ws_props = tool.Sequence.get_work_schedule_props()
            if ws_props and hasattr(ws_props, 'active_work_schedule_id'):
                ws_id = ws_props.active_work_schedule_id
                if ws_id:
                    work_schedule = tool.Ifc.get().by_id(ws_id)
                    if work_schedule and hasattr(work_schedule, 'Name'):
                        schedule_name = work_schedule.Name or "Unnamed Schedule"
        except Exception:
            pass

        text_configs = [
            {"name": "Schedule_Name", "position": (0, 10, 6), "size": 1.4, "align": "CENTER", "color": (1, 1, 1, 1), "type": "schedule_name", "content": f"Schedule: {schedule_name}"},
            {"name": "Schedule_Date", "position": (0, 10, 5), "size": 1.2, "align": "CENTER", "color": (1, 1, 1, 1), "type": "date"},
            {"name": "Schedule_Week", "position": (0, 10, 4), "size": 1.0, "align": "CENTER", "color": (1, 1, 1, 1), "type": "week"},
            {"name": "Schedule_Day_Counter", "position": (0, 10, 3), "size": 0.8, "align": "CENTER", "color": (1, 1, 1, 1), "type": "day_counter"},
            {"name": "Schedule_Progress", "position": (0, 10, 2), "size": 1.0, "align": "CENTER", "color": (1, 1, 1, 1), "type": "progress"},
        ]

        created_texts = []
        for config in text_configs:
            try:
                text_obj = cls._create_animated_text(config, settings, collection)
                created_texts.append(text_obj)
            except Exception:
                pass

        try:
            scene = bpy.context.scene
            if scene.camera and "4D_Animation_Camera" in scene.camera.name:
                anim_props = tool.Sequence.get_animation_props()
                camera_props = anim_props.camera_orbit

                if not getattr(camera_props, "enable_text_hud", False):
                    camera_props.enable_text_hud = True

                    def setup_hud_deferred():
                        try:
                            bpy.ops.bim.setup_text_hud()
                        except Exception:
                            pass

                    bpy.app.timers.register(setup_hud_deferred, first_interval=0.3)
                else:
                    def update_hud_deferred():
                        try:
                            bpy.ops.bim.update_text_hud_positions()
                        except Exception:
                            pass

                    bpy.app.timers.register(update_hud_deferred, first_interval=0.1)

        except Exception:
            pass

        try:
            cls._register_multi_text_handler(settings)
        except Exception:
            pass

        return created_texts

    @classmethod
    def create_text_objects_static(cls, settings):
        """Creates static 3D text objects for snapshot mode (NO animation handler registration)"""
        from datetime import timedelta

        collection_name = "Schedule_Display_Texts"
        if collection_name in bpy.data.collections:
            collection = bpy.data.collections[collection_name]
            for obj in list(collection.objects):
                try:
                    bpy.data.objects.remove(obj, do_unlink=True)
                except Exception:
                    pass
        else:
            collection = bpy.data.collections.new(collection_name)
            try:
                bpy.context.scene.collection.children.link(collection)
            except Exception:
                pass

        schedule_name = "Unknown Schedule"
        try:
            import bonsai.tool as tool
            ws_props = tool.Sequence.get_work_schedule_props()
            if ws_props and hasattr(ws_props, 'active_work_schedule_id'):
                ws_id = ws_props.active_work_schedule_id
                if ws_id:
                    work_schedule = tool.Ifc.get().by_id(ws_id)
                    if work_schedule and hasattr(work_schedule, 'Name'):
                        schedule_name = work_schedule.Name or "Unnamed Schedule"
        except Exception:
            pass

        text_configs = [
            {"name": "Schedule_Name", "position": (0, 10, 6), "size": 1.4, "align": "CENTER", "color": (1, 1, 1, 1), "type": "schedule_name", "content": f"Schedule: {schedule_name}"},
            {"name": "Schedule_Date", "position": (0, 10, 5), "size": 1.2, "align": "CENTER", "color": (1, 1, 1, 1), "type": "date"},
            {"name": "Schedule_Week", "position": (0, 10, 4), "size": 1.0, "align": "CENTER", "color": (1, 1, 1, 1), "type": "week"},
            {"name": "Schedule_Day_Counter", "position": (0, 10, 3), "size": 0.8, "align": "CENTER", "color": (1, 1, 1, 1), "type": "day_counter"},
            {"name": "Schedule_Progress", "position": (0, 10, 2), "size": 1.0, "align": "CENTER", "color": (1, 1, 1, 1), "type": "progress"},
        ]
        created_texts = []
        for config in text_configs:
            text_obj = cls._create_static_text(config, settings, collection)
            created_texts.append(text_obj)

        parent_name = "Schedule_Display_Parent"
        parent_empty = bpy.data.objects.get(parent_name)
        if not parent_empty:
            parent_empty = bpy.data.objects.new(parent_name, None)
            collection.objects.link(parent_empty)
            parent_empty.empty_display_type = 'PLAIN_AXES'
            parent_empty.empty_display_size = 2
            parent_empty.location = (0, 0, 0)

        for text_obj in created_texts:
            if text_obj and text_obj.parent != parent_empty:
                try:
                    text_obj.parent = parent_empty
                except Exception:
                    pass

        return created_texts

    @classmethod
    def _create_static_text(cls, config, settings, collection):
        """Creates a single static 3D text object with fixed content based on snapshot date"""
        text_curve = bpy.data.curves.new(name=config["name"], type='FONT')
        text_curve.size = config["size"]
        text_curve.align_x = config["align"]
        text_curve.align_y = 'CENTER'
        text_curve["text_type"] = config["type"]

        # Get the snapshot date from settings
        snapshot_date = settings.get("start") if isinstance(settings, dict) else getattr(settings, "start", None)

        # Set the text content based on the type and snapshot date
        text_type = config["type"].lower()

        # Check if content is pre-defined in config (for schedule_name)
        if "content" in config:
            text_curve.body = config["content"]
        elif text_type == "date":
            if snapshot_date:
                try:
                    text_curve.body = snapshot_date.strftime("%d/%m/%Y")
                except Exception:
                    text_curve.body = str(snapshot_date).split("T")[0]
            else:
                text_curve.body = "Date: --"
        elif text_type == "week":
            text_curve.body = cls._calculate_static_week_text(snapshot_date)
        elif text_type == "day_counter":
            text_curve.body = cls._calculate_static_day_text(snapshot_date)
        elif text_type == "progress":
            text_curve.body = cls._calculate_static_progress_text(snapshot_date)
        elif text_type == "schedule_name":
            text_curve.body = "Schedule: Unknown"
        else:
            text_curve.body = f"Static {config['type']}"

        # Create the text object
        text_obj = bpy.data.objects.new(config["name"], text_curve)
        text_obj.location = config["position"]

        # Set color if available
        if "color" in config:
            color = config["color"]
            if hasattr(text_obj, "color"):
                text_obj.color = color

        collection.objects.link(text_obj)

        # NOTE: Parenting is handled in the main create_text_objects_static method
        return text_obj

    @classmethod
    def _calculate_static_week_text(cls, snapshot_date):
        """Calculate static week text for snapshot mode"""
        try:
            if not snapshot_date:
                return "Week --"

            # Get schedule range for week calculation
            sch_start, sch_finish = tool.Sequence.get_schedule_date_range()
            if not sch_start:
                return "Week --"

            cd_d = snapshot_date.date()
            fss_d = sch_start.date()
            delta_days = (cd_d - fss_d).days

            if cd_d < fss_d:
                week_number = 0
            else:
                week_number = max(1, (delta_days // 7) + 1)

            return f"Week {week_number}"
        except Exception:
            return "Week --"

    @classmethod
    def _calculate_static_day_text(cls, snapshot_date):
        """Calculate static day text for snapshot mode"""
        try:
            if not snapshot_date:
                return "Day --"

            # Get schedule range for day calculation
            sch_start, sch_finish = tool.Sequence.get_schedule_date_range()
            if not sch_start:
                return "Day --"

            cd_d = snapshot_date.date()
            fss_d = sch_start.date()
            delta_days = (cd_d - fss_d).days

            if cd_d < fss_d:
                day_number = 0
            else:
                day_number = max(1, delta_days + 1)

            return f"Day {day_number}"
        except Exception:
            return "Day --"


    @classmethod
    def _calculate_static_progress_text(cls, snapshot_date):
        """Calculate static progress text for snapshot mode"""
        try:
            if not snapshot_date:
                return "Progress: --%"

            # Get schedule range for progress calculation
            sch_start, sch_finish = tool.Sequence.get_schedule_date_range()
            if not (sch_start and sch_finish):
                return "Progress: --%"

            cd_d = snapshot_date.date()
            fss_d = sch_start.date()
            fse_d = sch_finish.date()

            if cd_d < fss_d:
                progress_pct = 0
            elif cd_d >= fse_d:
                progress_pct = 100
            else:
                total_schedule_days = (fse_d - fss_d).days
                if total_schedule_days <= 0:
                    progress_pct = 100
                else:
                    delta_days = (cd_d - fss_d).days
                    progress_pct = (delta_days / total_schedule_days) * 100
                    progress_pct = round(progress_pct)
                    progress_pct = max(0, min(100, progress_pct))

            return f"Progress: {progress_pct}%"
        except Exception:
            return "Progress: --%"


    @classmethod
    def _create_animated_text(cls, config, settings, collection):
        try:
            text_curve = bpy.data.curves.new(name=config["name"], type='FONT')
            text_curve.size = config["size"]
            text_curve.align_x = config["align"]
            text_curve.align_y = 'CENTER'

            text_curve["text_type"] = config["type"]

            if config["type"] == "schedule_name" and "content" in config:
                text_curve["content"] = config["content"]

            try:
                start = settings.get("start") if isinstance(settings, dict) else getattr(settings, "start", None)
                finish = settings.get("finish") if isinstance(settings, dict) else getattr(settings, "finish", None)
                start_frame = int(settings.get("start_frame", 1)) if isinstance(settings, dict) else int(getattr(settings, "start_frame", 1))
                total_frames = int(settings.get("total_frames", 250)) if isinstance(settings, dict) else int(getattr(settings, "total_frames", 250))
                if hasattr(start, "isoformat"):
                    start_iso = start.isoformat()
                else:
                    start_iso = str(start)
                if hasattr(finish, "isoformat"):
                    finish_iso = finish.isoformat()
                else:
                    finish_iso = str(finish)
            except Exception:
                start_iso = ""
                finish_iso = ""

            text_curve["animation_settings"] = {
                "start_frame": start_frame,
                "total_frames": total_frames,
                "start_date": start_iso,
                "finish_date": finish_iso,
            }

            text_obj = bpy.data.objects.new(name=config["name"], object_data=text_curve)
            try:
                collection.objects.link(text_obj)
            except Exception:
                try:
                    bpy.context.scene.collection.objects.link(text_obj)
                except Exception:
                    pass

            text_obj.location = config["position"]

            cls._setup_text_material_colored(text_obj, config["color"], config["name"])

            cls._animate_text_by_type(text_obj, config["type"], settings)

            return text_obj

        except Exception as e:
            raise

    @classmethod
    def _setup_text_material_colored(cls, text_obj, color, mat_name_suffix):

            mat_name = f"Schedule_Text_Mat_{mat_name_suffix}"
            mat = bpy.data.materials.get(mat_name) or bpy.data.materials.new(name=mat_name)
            try:
                mat.use_nodes = True
                nt = mat.node_tree
                bsdf = nt.nodes.get("Principled BSDF")
                if bsdf:
                    bsdf.inputs["Base Color"].default_value = tuple(list(color[:3]) + [1.0])
                    bsdf.inputs["Emission"].default_value = tuple(list(color[:3]) + [1.0])
                    bsdf.inputs["Emission Strength"].default_value = 1.5
            except Exception:
                pass
            try:
                text_obj.data.materials.clear()
                text_obj.data.materials.append(mat)
            except Exception:
                pass

    @classmethod
    def _animate_text_by_type(cls, text_obj, text_type, settings):
        try:
            from datetime import timedelta, datetime as _dt

            start_date = settings.get("start") if isinstance(settings, dict) else getattr(settings, "start", None)
            finish_date = settings.get("finish") if isinstance(settings, dict) else getattr(settings, "finish", None)
            start_frame = int(settings.get("start_frame", 1)) if isinstance(settings, dict) else int(getattr(settings, "start_frame", 1))
            total_frames = int(settings.get("total_frames", 250)) if isinstance(settings, dict) else int(getattr(settings, "total_frames", 250))

            if isinstance(start_date, str):
                try:
                    from dateutil import parser as _parser
                    start_date = _dt.fromisoformat(start_date.replace(' ', 'T')[:19]) if '-' in start_date else _parser.parse(start_date, yearfirst=True)
                except Exception:
                    start_date = _dt.now()
            if isinstance(finish_date, str):
                try:
                    from dateutil import parser as _parser
                    finish_date = _dt.fromisoformat(finish_date.replace(' ', 'T')[:19]) if '-' in finish_date else _parser.parse(finish_date, yearfirst=True)
                except Exception:
                    finish_date = start_date

            duration = finish_date - start_date
            step_days = 7 if duration.days > 365 else (3 if duration.days > 90 else 1)

            current_date = start_date
            while current_date <= finish_date:
                if duration.total_seconds() > 0:
                    progress = (current_date - start_date).total_seconds() / duration.total_seconds()
                else:
                    progress = 0.0
                frame = start_frame + (progress * total_frames)

                if text_type == "date":
                    text_content = cls._format_date(current_date)
                elif text_type == "week":
                    text_content = cls._format_week(current_date, start_date)
                elif text_type == "day_counter":
                    text_content = cls._format_day_counter(current_date, start_date, finish_date)
                elif text_type == "progress":
                    text_content = cls._format_progress(current_date, start_date, finish_date)
                else:
                    text_content = ""

                text_obj.data.body = text_content
                try:
                    text_obj.data.keyframe_insert(data_path="body", frame=int(frame))
                except Exception:
                    pass

                current_date += timedelta(days=step_days)
                if current_date > finish_date and current_date - timedelta(days=step_days) < finish_date:
                    current_date = finish_date

        except Exception as e:
            raise


    @classmethod
    def _format_date(cls, current_date):
                try:
                    return current_date.strftime("%d/%m/%Y")
                except Exception:
                    return str(current_date)


    @classmethod
    def _format_week(cls, current_date, start_date):
            try:
                # Get full schedule dates (same as HUD logic)
                try:
                    sch_start, sch_finish = tool.Sequence.get_schedule_date_range()
                    if sch_start and sch_finish:
                        # Use same logic as HUD Schedule
                        cd_d = current_date.date()
                        fss_d = sch_start.date()
                        delta_days = (cd_d - fss_d).days
                        
                        if cd_d < fss_d:
                            week_number = 0
                        else:
                            week_number = max(1, (delta_days // 7) + 1)
                        
                        return f"Week {week_number}"
                except Exception:
                    pass
                
                # Fallback: use animation range
                days_elapsed = (current_date - start_date).days
                current_week = (days_elapsed // 7) + 1
                return f"Week {current_week}"
            except Exception:
                return "Week ?"
            

    @classmethod
    def _format_day_counter(cls, current_date, start_date, finish_date):
            try:
                # Get full schedule dates (same as HUD logic)
                try:
                    sch_start, sch_finish = tool.Sequence.get_schedule_date_range()
                    if sch_start and sch_finish:
                        # Use same logic as HUD Schedule
                        cd_d = current_date.date()
                        fss_d = sch_start.date()
                        delta_days = (cd_d - fss_d).days
                        
                        if cd_d < fss_d:
                            day_from_schedule = 0
                        else:
                            day_from_schedule = max(1, delta_days + 1)
                        
                        return f"Day {day_from_schedule}"
                except Exception:
                    pass
                
                # Fallback: use animation range
                days_elapsed = (current_date - start_date).days + 1
                return f"Day {days_elapsed}"
            except Exception:
                return "Day ?"
            
    @classmethod
    def _format_progress(cls, current_date, start_date, finish_date):
            try:
                # Get full schedule dates (same as HUD logic)
                try:
                    sch_start, sch_finish = tool.Sequence.get_schedule_date_range()
                    if sch_start and sch_finish:
                        # Use same logic as HUD Schedule
                        cd_d = current_date.date()
                        fss_d = sch_start.date()
                        fse_d = sch_finish.date()
                        
                        if cd_d < fss_d:
                            progress_pct = 0
                        elif cd_d >= fse_d:
                            progress_pct = 100
                        else:
                            total_schedule_days = (fse_d - fss_d).days
                            if total_schedule_days <= 0:
                                progress_pct = 100
                            else:
                                delta_days = (cd_d - fss_d).days
                                progress_pct = (delta_days / total_schedule_days) * 100
                                progress_pct = round(progress_pct)
                                progress_pct = max(0, min(100, progress_pct))
                        
                        return f"Progress: {progress_pct}%"
                except Exception:
                    pass
                
                # Fallback: use animation range
                total = (finish_date - start_date).days
                if total > 0:
                    progress = ((current_date - start_date).days / total) * 100.0
                else:
                    progress = 100.0
                return f"Progress: {progress:.0f}%"
            except Exception:
                return "Progress: ?%"
            
    @classmethod
    def _register_multi_text_handler(cls, settings):

            from datetime import datetime as _dt

            cls._unregister_frame_change_handler()

            def update_all_schedule_texts(scene):
                collection_name = "Schedule_Display_Texts"
                coll = bpy.data.collections.get(collection_name)
                if not coll:
                    return
                current_frame = int(scene.frame_current)
                for text_obj in list(coll.objects):
                    anim_settings = text_obj.data.get("animation_settings") if getattr(text_obj, "data", None) else None
                    if not anim_settings:
                        continue
                    start_frame = int(anim_settings.get("start_frame", 1))
                    total_frames = int(anim_settings.get("total_frames", 250))
                    if current_frame < start_frame:
                        progress = 0.0
                    elif current_frame > start_frame + total_frames:
                        progress = 1.0
                    else:
                        progress = (current_frame - start_frame) / float(total_frames or 1)

                    try:
                        start_date = _dt.fromisoformat(anim_settings.get("start_date"))
                        finish_date = _dt.fromisoformat(anim_settings.get("finish_date"))
                    except Exception:
                        continue
                    duration = finish_date - start_date
                    current_date = start_date + (duration * progress)

                    ttype = text_obj.data.get("text_type", "date")
                    if ttype == "date":
                        text_obj.data.body = cls._format_date(current_date)
                    elif ttype == "week":
                        text_obj.data.body = cls._format_week(current_date, start_date)
                    elif ttype == "day_counter":
                        text_obj.data.body = cls._format_day_counter(current_date, start_date, finish_date)
                    elif ttype == "progress":
                        text_obj.data.body = cls._format_progress(current_date, start_date, finish_date)
                    elif ttype == "schedule_name":
                        # Schedule name is static, get it from the original content if available
                        if "content" in text_obj.data:
                            text_obj.data.body = text_obj.data["content"]
                        else:
                            # Fallback: get schedule name dynamically
                            try:
                                import bonsai.tool as tool
                                ws_props = tool.Sequence.get_work_schedule_props()
                                if ws_props and hasattr(ws_props, 'active_work_schedule_id'):
                                    ws_id = ws_props.active_work_schedule_id
                                    if ws_id:
                                        work_schedule = tool.Ifc.get().by_id(ws_id)
                                        if work_schedule and hasattr(work_schedule, 'Name'):
                                            schedule_name = work_schedule.Name or "Unnamed Schedule"
                                            text_obj.data.body = f"Schedule: {schedule_name}"
                                        else:
                                            text_obj.data.body = "Schedule: Unknown"
                                    else:
                                        text_obj.data.body = "Schedule: Unknown"
                                else:
                                    text_obj.data.body = "Schedule: Unknown"
                            except Exception:
                                text_obj.data.body = "Schedule: Unknown"

            bpy.app.handlers.frame_change_post.append(update_all_schedule_texts)
            cls._frame_change_handler = update_all_schedule_texts

    @classmethod
    def _unregister_frame_change_handler(cls):
            try:

                if getattr(cls, "_frame_change_handler", None) in bpy.app.handlers.frame_change_post:
                    bpy.app.handlers.frame_change_post.remove(cls._frame_change_handler)
            except Exception:
                pass
            cls._frame_change_handler = None
