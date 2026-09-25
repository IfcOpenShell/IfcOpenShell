<!-- This file was generated with the assistance of an AI coding tool. -->

# Alignment authoring: development test scripts

**Temporary. Remove this whole directory before the PR for the final alignment work is posted.**
The reminder is also in `../REQUIREMENTS.md`, under "Status and work plan".

These are scratch Blender scripts used while developing the alignment authoring UI. They run
against the Bonsai extension installed in Blender 5.1 (loading this source tree). They are not
pytest tests.

## Headless (`bl_*.py`)

    blender --background --python-exit-code 1 --python bl_xxx.py

Exit code 0 means pass, and scripts that print "ALL OK" print it on success. Don't pass
`--factory-startup`, because it disables the Bonsai extension.

The regression set last run (all passing on 2026-09-25):

- bl_cant_follow, bl_pi_keep, bl_tables_keep, bl_insert_delete, bl_exact
- bl_multi_vertical_cant, bl_extend, bl_key_points, bl_drag_vertical, bl_move_marker
- bl_straight_repro, bl_offset, bl_offset_flow2, bl_join_distance, bl_polyline_flow
- bl_vertical_typed

`bl_panel_render_rec.py` is a helper imported by the panel tests.

Headless mode can't invoke modal operators (you get "Invalid operator call"). Use the UI harness for
those.

## UI mode (`ui_*.py`)

- `ui_invoke.py` invokes one draw, extend or move operator on a real 3D viewport. Choose the
  operator with the `ALIGN_UI_TEST` environment variable (e.g. draw_horizontal_alignment,
  move_pi_marker). The result is written to `%TEMP%\align_ui_invoke_result.txt`.

      ALIGN_UI_TEST=move_pi_marker blender --window-geometry 0 0 1400 900 --python ui_invoke.py

- `ui_pick.py` simulates clicks near a PI marker placed over a mesh, and needs
  `--enable-event-simulate`. Set `PICK_CONTROL=1` to disable the PI pick keymap for comparison. The
  result is written to `%TEMP%\align_ui_pick_result.txt`.
