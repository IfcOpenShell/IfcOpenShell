# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

import multiprocessing
import os
import subprocess
import threading
import time
from pathlib import Path
from typing import Union

import bpy
import pyradiance as pr

import bonsai.tool as tool
import bonsai.bim.module.light.shared as shared

# pyradiance's bundled Radiance binaries
_PYRAD_BIN = Path(pr.__file__).parent / "bin"


class RadianceRender(bpy.types.Operator):
    """Radiance Rendering (runs in background thread)"""

    bl_idname = "render_scene.radiance"
    bl_label = "Render"
    bl_description = "Renders the scene using Radiance"

    _timer = None
    _thread: Union[threading.Thread, None] = None
    _result_image: Union[bytes, None] = None
    _error: Union[str, None] = None
    _start_time: float = 0.0

    @classmethod
    def poll(cls, context):
        props = tool.Blender.get_radiance_exporter_props()
        if not props.output_dir:
            cls.poll_message_set("Output directory is not set.")
            return False
        if props.is_rendering:
            cls.poll_message_set("A render is already in progress.")
            return False
        if shared.scene is None:
            cls.poll_message_set("Radiance scene not prepared. Please run 'Prepare Scene' (Step 2) first.")
            return False
        return True

    def execute(self, context):
        props = tool.Blender.get_radiance_exporter_props()
        resolution_x, resolution_y = props.radiance_resolution_x, props.radiance_resolution_y

        context.scene.render.resolution_x = resolution_x
        context.scene.render.resolution_y = resolution_y

        quality = props.radiance_quality.upper()
        detail = props.radiance_detail.upper()
        variability = props.radiance_variability.upper()
        ambient_bounces = props.ambient_bounces
        output_dir = props.output_dir

        props.is_rendering = True
        self._start_time = time.time()
        self._result_image = None
        self._error = None

        self._thread = threading.Thread(
            target=self._render_worker,
            args=(shared.scene, output_dir, resolution_x, resolution_y, quality, detail, variability, ambient_bounces),
            daemon=True,
        )
        self._thread.start()

        wm = context.window_manager
        self._timer = wm.event_timer_add(0.5, window=context.window)
        wm.modal_handler_add(self)

        self.report({"INFO"}, "Radiance render started in background...")
        context.window.cursor_set('WAIT')
        return {"RUNNING_MODAL"}

    def _render_worker(self, render_scene, output_dir, res_x, res_y, quality, detail, variability, ambient_bounces):
        """Runs in a background thread — no Blender API calls allowed here."""
        cwd_saved = os.getcwd()
        try:
            os.chdir(output_dir)
            self._result_image = pr.render(
                render_scene,
                ambbounce=ambient_bounces,
                resolution=(res_x, res_y),
                quality=quality,
                detail=detail,
                variability=variability,
                nproc=multiprocessing.cpu_count(),
            )
        except Exception as e:
            self._error = str(e)
        finally:
            os.chdir(cwd_saved)

    def modal(self, context, event):
        if event.type == 'TIMER':
            if self._thread is not None and self._thread.is_alive():
                return {"RUNNING_MODAL"}

            self._cleanup_timer(context)
            props = tool.Blender.get_radiance_exporter_props()
            props.is_rendering = False
            context.window.cursor_set('DEFAULT')

            if self._error:
                self.report({"ERROR"}, f"Radiance render failed: {self._error}")
                return {"CANCELLED"}

            elapsed = time.time() - self._start_time
            print(f"Render completed in {elapsed:.2f} seconds")

            output_dir = props.output_dir
            output_file_name = props.output_file_name
            output_file_format = props.output_file_format

            output_hdr_path = os.path.join(output_dir, f"{output_file_name}.hdr")
            print(f"Saving HDR output to: {output_hdr_path}")
            with open(output_hdr_path, "wb") as wtr:
                wtr.write(self._result_image)

            if output_file_format == "HDR_TIFF":
                print("Applying tone mapping...")
                pcond_image = pr.pcond(hdr=output_hdr_path, human=True)
                tiff_path = os.path.join(output_dir, f"{output_file_name}.tiff")
                print(f"Saving TIFF output to: {tiff_path}")
                pr.ra_tiff(inp=pcond_image, out=tiff_path, lzw=True)

            print("Radiance rendering process completed successfully.")
            self.report({"INFO"}, f"Radiance rendering completed. HDR Output: {output_hdr_path}")
            if output_file_format == "HDR_TIFF":
                self.report({"INFO"}, f"TIFF Output: {tiff_path}")

            for area in context.screen.areas:
                area.tag_redraw()

            return {"FINISHED"}

        elif event.type == 'ESC':
            self._cleanup_timer(context)
            props = tool.Blender.get_radiance_exporter_props()
            props.is_rendering = False
            context.window.cursor_set('DEFAULT')
            self.report({"WARNING"}, "Render cancelled by user. Background process may still be running.")
            return {"CANCELLED"}

        return {"PASS_THROUGH"}

    def _cleanup_timer(self, context):
        if self._timer is not None:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None


class FalseColorRadiance(bpy.types.Operator):
    """Generate false color HDR image for illuminance analysis"""

    bl_idname = "render_scene.false_color_radiance"
    bl_label = "Generate False Color Image"
    bl_description = "Generate a false color HDR image for illuminance analysis"

    @classmethod
    def poll(cls, context):
        props = tool.Blender.get_radiance_exporter_props()
        if not props.output_dir:
            cls.poll_message_set("Output directory is not set.")
            return False
        return True

    def execute(self, context):
        props = tool.Blender.get_radiance_exporter_props()
        output_dir = props.output_dir
        output_file_name = props.output_file_name

        hdr_path = os.path.join(output_dir, f"{output_file_name}.hdr")
        if not os.path.exists(hdr_path):
            self.report(
                {"ERROR"},
                f"HDR file not found at: {hdr_path}. Please run 'Radiance Render' first.",
            )
            return {"CANCELLED"}

        fc_scale = (
            str(int(props.false_color_scale))
            if props.false_color_scale == int(props.false_color_scale)
            else str(props.false_color_scale)
        )

        # Multiplier converts Radiance raw values to display units
        # fc (foot-candles) = 16.629..., lux & cd/m2 = 179.0
        multiplier = 179.0 if props.false_color_label in ("lux", "cd/m2") else 16.629505759940542

        print(f"False color parameters: label={props.false_color_label}, scale={fc_scale}, "
              f"steps={props.false_color_steps}, multiplier={multiplier}, "
              f"contour={props.false_color_contour_lines}")

        try:
            fc_output_name = props.false_color_output_name
            fc_hdr_path = os.path.join(output_dir, f"{fc_output_name}.hdr")

            # Find falsecolor binary from user-specified Radiance bin directory
            radiance_bin_dir = os.path.normpath(props.radiance_bin_dir) if props.radiance_bin_dir else ""
            if radiance_bin_dir:
                falsecolor_bin = os.path.join(radiance_bin_dir, "falsecolor.exe")
                if not os.path.exists(falsecolor_bin):
                    falsecolor_bin = os.path.join(radiance_bin_dir, "falsecolor")
                if not os.path.exists(falsecolor_bin):
                    self.report({"ERROR"}, f"falsecolor not found in: {radiance_bin_dir}")
                    return {"CANCELLED"}
            else:
                import shutil
                falsecolor_bin = shutil.which("falsecolor") or shutil.which("falsecolor.exe")
                if not falsecolor_bin:
                    self.report({"ERROR"}, "Set the Radiance Bin path in False Color settings, or add Radiance to system PATH.")
                    return {"CANCELLED"}
                radiance_bin_dir = os.path.dirname(falsecolor_bin)

            radiance_lib = os.path.join(os.path.dirname(radiance_bin_dir), "lib")
            print(f"Using falsecolor: {falsecolor_bin}")
            print(f"Radiance bin: {radiance_bin_dir}, lib: {radiance_lib}")

            cmd = [falsecolor_bin]
            cmd.extend(["-m", str(multiplier)])
            cmd.extend(["-s", fc_scale])
            cmd.extend(["-n", str(props.false_color_steps)])
            cmd.extend(["-l", props.false_color_label])

            if props.false_color_contour_lines:
                cmd.append("-cl")
                if props.false_color_contour_mode == "WITH_BG":
                    cmd.extend(["-ip", hdr_path])
                else:
                    cmd.extend(["-i", hdr_path])
            else:
                cmd.extend(["-ip", hdr_path])

            # Setup environment so falsecolor can find pcomb, psign, pcompos etc.
            env = os.environ.copy()
            if os.path.exists(radiance_bin_dir):
                env["PATH"] = radiance_bin_dir + os.pathsep + env.get("PATH", "")
            if os.path.exists(radiance_lib):
                env["RAYPATH"] = "." + os.pathsep + radiance_lib

            print(f"Running: {' '.join(cmd)}")
            # Write output to file via redirection to avoid Windows stdout binary corruption
            cmd_str = subprocess.list2cmdline(cmd) + f' > "{fc_hdr_path}"'
            result = subprocess.run(cmd_str, shell=True, stderr=subprocess.PIPE, env=env, cwd=output_dir)
            if result.returncode != 0:
                error_msg = result.stderr.decode() if result.stderr else "Unknown error"
                self.report({"ERROR"}, f"falsecolor failed: {error_msg}")
                return {"CANCELLED"}

            fc_size = os.path.getsize(fc_hdr_path) if os.path.exists(fc_hdr_path) else 0
            print(f"False color HDR generated: {fc_hdr_path} ({fc_size} bytes)")
            self.report({"INFO"}, f"False color image generated: {fc_hdr_path}")

            # Generate TIFF version
            try:
                pcond_fc_image = pr.pcond(hdr=fc_hdr_path, human=True)
                fc_tiff_path = os.path.join(output_dir, f"{fc_output_name}.tiff")
                pr.ra_tiff(inp=pcond_fc_image, out=fc_tiff_path, lzw=True)
                print(f"False color TIFF generated: {fc_tiff_path}")
                self.report({"INFO"}, f"False color TIFF also generated: {fc_tiff_path}")
            except Exception as e:
                self.report({"WARNING"}, f"TIFF generation failed: {str(e)}")

            return {"FINISHED"}

        except subprocess.CalledProcessError as e:
            # Clean up incomplete HDR file on failure
            if os.path.exists(fc_hdr_path):
                os.remove(fc_hdr_path)
            error_msg = f"falsecolor failed: {e.stderr.decode() if e.stderr else str(e)}"
            self.report({"ERROR"}, error_msg)
            return {"CANCELLED"}
        except FileNotFoundError:
            self.report({"ERROR"}, "falsecolor not found. Please install Radiance and add it to PATH.")
            return {"CANCELLED"}
        except Exception as e:
            self.report({"ERROR"}, f"Failed to generate false color image: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"CANCELLED"}
