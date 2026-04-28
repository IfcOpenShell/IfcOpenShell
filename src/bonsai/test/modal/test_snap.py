import inspect
import time

import bpy
import pytest

import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore


def _assert_pass(message: str) -> None:
    caller_name = inspect.stack()[1].function
    GREEN = "\033[32m"
    RESET = "\033[0m"
    print(f"{GREEN}{caller_name} PASSED: {message}{RESET}")


def _handle_error(e: Exception, on_done) -> None:
    RED = "\033[31m"
    RESET = "\033[0m"
    print(f"{RED}Assertion failed: {e}{RESET}")
    on_done()


def run_iter_from_timer(event_iter, on_complete=None, on_error=None):
    i = iter(event_iter)
    done = False

    def event_step():
        nonlocal done, on_complete
        try:
            ret = next(i, "STOP")
            # print(f"Iter step returned: {ret!r}")
            if ret is None or ret == "STOP" or ret == "FINISHED":
                done = True
                # print("Iterator done, calling on_complete")
                if on_complete:
                    on_complete()
                return None
        except StopIteration:
            done = True
            # print("StopIteration, calling on_complete")
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
                    with bpy.context.temp_override(
                        area=area, region=region, space_data=area.spaces[0]
                    ):
                        bpy.ops.bim.measure_tool("INVOKE_DEFAULT", measure_type="POLYLINE")
            break

    yield from preset_event_simulate(window, "MOUSEMOVE", "NOTHING", x, y)
    yield from preset_event_simulate(window, "LEFTMOUSE", "TAP", x, y)
    snap_point = tool.Model.get_polyline_props().snap_mouse_point[0]
    assert snap_point.snap_object, "First click should have a snap_object"
    _assert_pass("First click should have a snap_object")
    assert type(snap_point.snap_object) == str, "snap_object should be an object name string."
    _assert_pass("snap_object should be an object name string.")
    assert snap_point.snap_object.split("/")[0] == "IfcWall", "Object should be an IfcWall"
    _assert_pass("Object should be an IfcWall")

    offset = 200
    yield from preset_event_simulate(window, "MOUSEMOVE", "NOTHING", x-offset, y)
    yield from preset_event_simulate(window, "MOUSEMOVE", "NOTHING", x-offset, y)
    yield from preset_event_simulate(window, "MOUSEMOVE", "NOTHING", x-offset, y)
    yield from preset_event_simulate(window, "MOUSEMOVE", "NOTHING", x-offset, y)
    yield from preset_event_simulate(window, "LEFTMOUSE", "TAP", x-offset, y)
    snap_point = tool.Model.get_polyline_props().snap_mouse_point[0]
    assert not snap_point.snap_object, "Second click should not have a snap_object"
    _assert_pass("Second click should not have a snap_object")

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
                    with bpy.context.temp_override(
                        area=area, region=region, space_data=area.spaces[0]
                    ):
                        bpy.ops.bim.measure_tool("INVOKE_DEFAULT", measure_type="POLYLINE")
            break

    yield from preset_event_simulate(window, "MOUSEMOVE", "NOTHING", x, y)
    yield from preset_event_simulate(window, "LEFTMOUSE", "TAP", x, y)
    snap_point = tool.Model.get_polyline_props().snap_mouse_point[0]
    assert snap_point.snap_object, "First click should have a snap_object"
    _assert_pass("First click should have a snap_object")
    assert type(snap_point.snap_object) == str, "snap_object should be an object name string."
    _assert_pass("snap_object should be an object name string.")
    assert snap_point.snap_object.split("/")[0] == "IfcFurniture", "Object should be an IfcFurniture"
    _assert_pass("Object should be an IfcFurniture")
    yield "FINISHED"


def cleanup():
    # print("CLEANUP CALLED")
    bpy.app.use_event_simulate = False
    bpy.ops.wm.quit_blender()


def get_test_queue(window):
    """Returns a list of test callables to run sequentially, each in its own timer."""
    return [
        lambda w=window: test_snap_object_detection(w, 960, 540),
        lambda w=window: test_snap_in_xray_mode(w, 1200, 540),
    ]

def _get_valid_window() -> bpy.types.Window:
    """Return a Blender window that works even when ``bpy.context.window``
    is ``None`` (e.g. during a temporary operator context)."""
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


@pytest.mark.snap
def run_tests(window):
    tests = get_test_queue(window)
    def run_next():
        # print(f"run_next called, {len(tests)} tests remaining, id={id(tests)}")
        if not tests:
            # print("No tests left, calling cleanup")
            cleanup()
            return
        test_fn = tests.pop(0)
        # print(f"Running test: {test_fn}")
        current_tests = list(tests)
        def on_done():
            # print(f"on_done called, tests had {len(current_tests)} items")
            if current_tests:
                run_next()
            else:
                cleanup()
        run_iter_from_timer(
            test_fn(),
            on_complete=on_done,
            on_error=lambda e: _handle_error(e, on_done),
        )

    run_next()


if __name__ == "__main__":
    new_project()
    filepath = "./test/files/snap.ifc"
    bpy.ops.bim.load_project(filepath=filepath)
    # load_project may clear the context.window; reacquire a valid one.
    window = _get_valid_window()
    run_tests(window)

