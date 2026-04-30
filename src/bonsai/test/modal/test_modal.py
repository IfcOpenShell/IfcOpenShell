# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Bruno Perdigão <contact@brunopo.com>
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


import inspect
import os
import sys

import bpy
import ifcopenshell
import pytest

from bonsai import tool as tool
from bonsai.bim.ifc import IfcStore
from bonsai.bim.module.model.data import AuthoringData as Model

GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"


def _assert_pass(message: str) -> None:
    caller_name = inspect.stack()[1].function
    print(f"{GREEN}{caller_name} PASSED: {message}{RESET}")


def _handle_error(e: Exception, on_done) -> None:
    print(f"{RED}Assertion failed: {e}{RESET}")
    if on_done:
        on_done()


def run_iter_from_timer(event_iter, on_complete=None, on_error=None):
    i = iter(event_iter)
    done = False

    def event_step():
        nonlocal done, on_complete
        try:
            ret = next(i, "STOP")
            if ret in (None, "STOP", "FINISHED"):
                done = True
                if on_complete:
                    on_complete()
                return None
        except StopIteration:
            done = True
            if on_complete:
                on_complete()
            return None
        except Exception as e:
            done = True
            print(f"Exception: {e}")
            if on_error:
                on_error(e)
            elif on_complete:
                on_complete()
            return None
        return 0.0

    bpy.app.timers.register(event_step, first_interval=0.0)


def preset_event_simulate(window, event_type, value, x, y):
    if value == "TAP":
        yield window.event_simulate(event_type, "PRESS", x=x, y=y)
        yield window.event_simulate(event_type, "RELEASE", x=x, y=y)
    else:
        yield window.event_simulate(event_type, value, x=x, y=y)


def cleanup():
    bpy.app.use_event_simulate = False
    bpy.ops.wm.quit_blender()


def _get_valid_window() -> bpy.types.Window:
    win = bpy.context.window
    if win is not None:
        return win
    wm = getattr(bpy.context, "window_manager", None)
    if wm and wm.windows:
        return wm.windows[0]
    raise RuntimeError("Unable to locate a Blender UI window.")


def new_project():
    IfcStore.purge()
    bpy.ops.wm.read_homefile(app_template="", use_factory_startup=True)
    if len(bpy.data.objects) > 0:
        bpy.data.batch_remove(bpy.data.objects)
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
    if len(bpy.data.materials) > 0:
        bpy.data.batch_remove(bpy.data.materials)
    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.unit_settings.length_unit = "MILLIMETERS"
    props = tool.Project.get_project_props()
    props.template_file = "0"
    tool.Blender.get_addon_preferences().should_play_chaching_sound = False


def test_snap_object_detection(window, x, y):
    yield from preset_event_simulate(window, "ESC", "TAP", x, y)

    measure_settings = tool.Project.get_measure_tool_settings()
    measure_settings.measurement_type = "POLYLINE"
    for obj in tool.Blender.get_selected_objects():
        obj.select_set(False)
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            for region in area.regions:
                if region.type == "WINDOW":
                    with bpy.context.temp_override(area=area, region=region, space_data=area.spaces[0]):
                        bpy.ops.bim.measure_tool("INVOKE_DEFAULT", measure_type="POLYLINE")
                    break

    yield from preset_event_simulate(window, "MOUSEMOVE", "NOTHING", x, y)
    yield from preset_event_simulate(window, "LEFTMOUSE", "TAP", x, y)
    snap_point = tool.Model.get_polyline_props().snap_mouse_point[0]
    assert_msg = "First click should have a snap_object"
    assert snap_point.snap_object, assert_msg
    _assert_pass(assert_msg)
    assert_msg = "snap_object should be a string with the object name"
    assert type(snap_point.snap_object) == str, assert_msg
    _assert_pass(assert_msg)
    assert_msg = "Object should be an IfcWall"
    assert snap_point.snap_object.split("/")[0] == "IfcWall", assert_msg
    _assert_pass(assert_msg)

    offset = 200
    yield from preset_event_simulate(window, "MOUSEMOVE", "NOTHING", x - offset, y)
    yield from preset_event_simulate(window, "MOUSEMOVE", "NOTHING", x - offset, y)
    yield from preset_event_simulate(window, "MOUSEMOVE", "NOTHING", x - offset, y)
    yield from preset_event_simulate(window, "MOUSEMOVE", "NOTHING", x - offset, y)
    yield from preset_event_simulate(window, "LEFTMOUSE", "TAP", x - offset, y)
    snap_point = tool.Model.get_polyline_props().snap_mouse_point[0]
    assert_msg = "Second click should not have a snap_object"
    assert not snap_point.snap_object, assert_msg
    _assert_pass(assert_msg)

    yield from preset_event_simulate(window, "RET", "TAP", x, y)
    yield "FINISHED"


def test_snap_in_xray_mode(window, x, y):
    area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")
    area.spaces[0].shading.show_xray = True

    yield from preset_event_simulate(window, "ESC", "TAP", x, y)

    measure_settings = tool.Project.get_measure_tool_settings()
    measure_settings.measurement_type = "POLYLINE"
    for obj in tool.Blender.get_selected_objects():
        obj.select_set(False)
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            for region in area.regions:
                if region.type == "WINDOW":
                    with bpy.context.temp_override(area=area, region=region, space_data=area.spaces[0]):
                        bpy.ops.bim.measure_tool("INVOKE_DEFAULT", measure_type="POLYLINE")
                    break

    yield from preset_event_simulate(window, "MOUSEMOVE", "NOTHING", x, y)
    yield from preset_event_simulate(window, "LEFTMOUSE", "TAP", x, y)
    snap_point = tool.Model.get_polyline_props().snap_mouse_point[0]
    assert_msg = "First click should have a snap_object"
    assert snap_point.snap_object, assert_msg
    _assert_pass(assert_msg)
    assert_msg = "snap_object should be a string with the object name"
    assert type(snap_point.snap_object) == str, assert_msg
    _assert_pass(assert_msg)
    assert_msg = "Object should be an IfcFurniture"
    assert snap_point.snap_object.split("/")[0] == "IfcFurniture", assert_msg
    _assert_pass(assert_msg)
    yield "FINISHED"


def test_draw_polyline_wall(window, x, y):
    yield from preset_event_simulate(window, "ESC", "TAP", x, y)

    for obj in tool.Blender.get_selected_objects():
        obj.select_set(False)
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            for region in area.regions:
                if region.type == "WINDOW":
                    with bpy.context.temp_override(area=area, region=region, space_data=area.spaces[0]):
                        props = tool.Model.get_model_props()
                        ifc = tool.Ifc.get()
                        relating_type = ifc.by_type("IfcWallType")[0]

                        if tool.Model.get_usage_type(relating_type) == "LAYER2":
                            props.ifc_class = "IfcWallType"
                            props.relating_type_id = str(relating_type.id())

                        bpy.ops.bim.draw_polyline_wall("INVOKE_DEFAULT")
                    break

    yield from preset_event_simulate(window, "MOUSEMOVE", "NOTHING", x, y)
    yield from preset_event_simulate(window, "MOUSEMOVE", "NOTHING", x, y)
    yield from preset_event_simulate(window, "MOUSEMOVE", "NOTHING", x, y)
    yield from preset_event_simulate(window, "MOUSEMOVE", "NOTHING", x, y)
    yield from preset_event_simulate(window, "LEFTMOUSE", "TAP", x, y)
    yield from preset_event_simulate(window, "X", "TAP", x, y)

    offset = 200
    yield from preset_event_simulate(window, "MOUSEMOVE", "NOTHING", x + offset, y)
    yield from preset_event_simulate(window, "MOUSEMOVE", "NOTHING", x + offset, y)
    yield from preset_event_simulate(window, "MOUSEMOVE", "NOTHING", x + offset, y)
    yield from preset_event_simulate(window, "MOUSEMOVE", "NOTHING", x + offset, y)
    yield from preset_event_simulate(window, "LEFTMOUSE", "TAP", x + offset, y)

    yield from preset_event_simulate(window, "RET", "TAP", x, y)
    element = tool.Ifc.get_entity(bpy.context.selected_objects[0])

    assert_msg = "Created object should be IfcWall"
    assert element.is_a() == "IfcWall"
    _assert_pass(assert_msg)
    assert_msg = "Created object should be typed by IfcWallType"
    assert ifcopenshell.util.element.get_type(element).is_a() == "IfcWallType"
    _assert_pass(assert_msg)
    # TODO Asset the axis has the same X value

    yield "FINISHED"


def run_tests():
    module_name = os.getenv("MODULE", "snap")
    if module_name == "wall":
        filepath = f"./test/files/wall.ifc"
        bpy.ops.bim.load_project(filepath=filepath)
        window = _get_valid_window()
        test_queue = [lambda w=window: test_draw_polyline_wall(w, 960, 540)]
    elif module_name == "snap":
        filepath = f"./test/files/snap.ifc"
        bpy.ops.bim.load_project(filepath=filepath)
        window = _get_valid_window()
        test_queue = [
            lambda w=window: test_snap_object_detection(w, 960, 540),
            lambda w=window: test_snap_in_xray_mode(w, 1200, 540),
        ]
    else:
        cleanup()

    def _next():
        if not test_queue:
            cleanup()
            return
        test_fn = test_queue.pop(0)
        # use the shared timer infrastructure
        run_iter_from_timer(
            test_fn(),
            on_complete=_next,
            on_error=lambda e: _handle_error(e, lambda: None),
        )

    _next()

if __name__ == "__main__":
    new_project()
    run_tests()
