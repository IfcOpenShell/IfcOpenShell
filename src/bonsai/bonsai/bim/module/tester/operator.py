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

import os
import bpy
import time
import tempfile
import webbrowser
import traceback
import subprocess
import socket
import sys
import threading
import asyncio
import socketio
from aiohttp import web
import ifctester
import ifctester.ids
import ifctester.reporter
import ifcopenshell
import bonsai.tool as tool
import bonsai.bim.handler
from bpy_extras.io_utils import ExportHelper
from pathlib import Path
from typing import Union

webapp_process = None
websocket_server_thread = None
websocket_app = None
websocket_runner = None


class IfcTesterWebSocketServer:
    def __init__(self, port):
        self.port = port
        self.sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="aiohttp")
        self.app = web.Application()
        self.sio.attach(self.app)
        self.runner = None
        self.site = None
        self.loop = None
        self.shutdown_event = None

        # Register namespace
        self.sio.register_namespace(IfcTesterNamespace("/ifctester"))

        # Add health check route
        self.app.router.add_get("/health", self.health_check)

    async def health_check(self, request):
        return web.Response(text="OK", content_type="text/plain")

    async def start_server(self):
        self.loop = asyncio.get_event_loop()
        self.shutdown_event = asyncio.Event()

        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, "127.0.0.1", self.port)
        await self.site.start()
        print(f"IfcTester WebSocket server started on 127.0.0.1:{self.port}")

        try:
            # Wait for shutdown signal
            await self.shutdown_event.wait()
        except asyncio.CancelledError:
            print("WebSocket server received cancellation")
        finally:
            await self._cleanup()

    async def _cleanup(self):
        try:
            # Disconnect all clients
            print("Shutting down SocketIO...")

            try:
                await self.sio.shutdown()
            except Exception as e:
                print(f"Error shutting down socketio: {e}")

            # Stop the web server
            if self.site:
                print("Stopping web server...")
                await asyncio.wait_for(self.site.stop(), timeout=2.0)
                self.site = None

            # Clean up the runner
            if self.runner:
                print("Cleaning up runner...")
                await asyncio.wait_for(self.runner.cleanup(), timeout=2.0)
                self.runner = None

            print("IfcTester WebSocket server stopped")
        except TimeoutError:
            print("Websocket server cleanup timed out, forcing shutdown")
        except Exception as e:
            print(f"Error during websocket cleanup: {e}")

    def stop_server(self):
        if self.loop and self.shutdown_event and not self.shutdown_event.is_set():
            try:
                self.loop.call_soon_threadsafe(self.shutdown_event.set)
            except Exception as e:
                print(f"Error sending shutdown signal: {e}")


class IfcTesterNamespace(socketio.AsyncNamespace):
    def __init__(self, namespace):
        super().__init__(namespace)

    async def on_connect(self, sid, environ):
        print(f"IfcTester webapp client connected: {sid}")
        await self.emit("status", {"connected": True}, room=sid)

    async def on_disconnect(self, sid):
        print(f"IfcTester webapp client disconnected: {sid}")

    async def on_audit_ids(self, sid, data):
        request_id = None
        try:
            request_id = data.get("id")
            ids_string = data.get("ids")
            props = tool.Tester.get_tester_props()

            if not request_id:
                await self.emit("error", {"error": "No request ID provided"}, room=sid)
                return

            if not ids_string:
                await self.emit("error", {"id": request_id, "error": "No IDS XML string provided"}, room=sid)
                return

            print(f"Processing IDS audit request {request_id}")

            # Check if IFC is loaded in Bonsai
            ifc = tool.Ifc.get()
            if not ifc:
                await self.emit(
                    "error", {"id": request_id, "error": "No IFC model is currently loaded in Bonsai"}, room=sid
                )
                return

            # Parse IDS from string
            try:
                ids = ifctester.ids.from_string(ids_string)
            except Exception as e:
                await self.emit("error", {"id": request_id, "error": f"Failed to parse IDS XML: {str(e)}"}, room=sid)
                return

            # Validate IFC against IDS
            try:
                ids.validate(ifc)
            except Exception as e:
                await self.emit("error", {"id": request_id, "error": f"Validation failed: {str(e)}"}, room=sid)
                return

            # Generate reports
            try:
                # JSON report
                json_reporter = ifctester.reporter.Json(ids)
                json_reporter.report()
                json_report = json_reporter.to_string()

                # HTML report
                html_reporter = ifctester.reporter.Html(ids, hide_skipped=props.hide_skipped_specs)
                html_reporter.report()
                html_report = html_reporter.to_string()

                # Send results back
                await self.emit(
                    "audit_result", {"id": request_id, "json_report": json_report, "html_report": html_report}, room=sid
                )

                print(f"Successfully processed IDS audit request {request_id}")

            except Exception as e:
                await self.emit("error", {"id": request_id, "error": f"Failed to generate reports: {str(e)}"}, room=sid)

        except Exception as e:
            print(f"Error processing audit request: {str(e)}")
            import traceback

            print(traceback.format_exc())
            await self.emit("error", {"id": request_id, "error": f"Internal server error: {str(e)}"}, room=sid)

    async def on_ping(self, sid, data):
        await self.emit("pong", {"timestamp": data.get("timestamp")}, room=sid)


class ExecuteIfcTester(bpy.types.Operator):
    bl_idname = "bim.execute_ifc_tester"
    bl_label = "Execute IfcTester"

    @classmethod
    def poll(cls, context):
        props = tool.Tester.get_tester_props()
        if not props.should_load_from_memory and not props.ifc_files.single_file:
            cls.poll_message_set("Select an IFC file or use 'load from memory' if it's loaded in Bonsai.")
            return False
        if not props.specs:
            return False
        return True

    def execute(self, context):
        props = tool.Tester.get_tester_props()

        props.specifications.clear()

        if props.should_load_from_memory and tool.Ifc.get():
            ifc_data = tool.Ifc.get()
            ifc_path = tool.Ifc.get_path()

            for f in props.specs.file_list:
                self.execute_tester(ifc_data, ifc_path, f.name)
        else:
            for ifc_file in props.ifc_files.file_list:
                ifc_data = ifcopenshell.open(ifc_file.name)

                for f in props.specs.file_list:
                    self.execute_tester(ifc_data, ifc_file.name, f.name)

        bonsai.bim.handler.refresh_ui_data()
        return {"FINISHED"}

    def execute_tester(self, ifc_data: ifcopenshell.file, ifc_path: str, specs_path: str) -> Union[set[str], None]:
        props = tool.Tester.get_tester_props()
        props.failed_entities.clear()

        # No need for if-statement, just postponing lots of diffs.
        if True:
            dirpath = tempfile.mkdtemp(dir=tool.Blender.get_addon_preferences().tmp_dir or None)
            start = time.time()
            output = Path(os.path.join(dirpath, "{}_{}.html".format(Path(ifc_path).name, Path(specs_path).name)))

            try:
                specs = ifctester.ids.open(specs_path)
            except ifctester.ids.IdsXmlValidationError as e:
                traceback.print_exc()
                YELLOW = "\033[93m"
                RESET = "\033[0m"
                print("------------------\n" * 3)
                print(f"{YELLOW}Validation error details:\n\n{str(e.xml_error)}{RESET}")
                print("------------------\n" * 3)
                self.report(
                    {"ERROR"}, "Provided IDS file appears to be invalid. Open system console to see the details."
                )
                return {"CANCELLED"}
            print("Finished loading:", time.time() - start)
            start = time.time()
            specs.validate(ifc_data, filepath=ifc_path)

            print("Finished validating:", time.time() - start)
            start = time.time()

            if props.generate_html_report:
                engine = ifctester.reporter.Html(specs, props.hide_skipped_specs)
                engine.report()
                output_path = output.as_posix()
                engine.to_file(output_path)
                webbrowser.open(f"file://{output_path}")

            if props.generate_ods_report:
                engine = ifctester.reporter.Ods(specs)
                engine.report()
                output_path = output.with_suffix(".ods").as_posix()
                engine.to_file(output_path)

            report = None
            report = ifctester.reporter.Json(specs).report()["specifications"]
            if report:
                tool.Tester.specs = specs
                tool.Tester.report = report

            for spec in report:
                new_spec = props.specifications.add()
                new_spec.name = spec["name"]
                new_spec.description = spec["description"]
                new_spec.status = spec["status"]


class StartIfcTesterWebapp(bpy.types.Operator):
    bl_idname = "bim.start_ifc_tester_webapp"
    bl_label = "Start IfcTester Webapp"
    bl_description = "Start the IfcTester webapp server and open it in the default browser"

    def execute(self, context):
        global webapp_process, websocket_server_thread, websocket_app

        props = tool.Tester.get_tester_props()

        if webapp_process is not None or websocket_server_thread is not None:
            self.report({"WARNING"}, "IfcTester webapp is already running")
            return {"CANCELLED"}

        try:
            import ifctester.webapp.serve
        except ImportError:
            self.report(
                {"ERROR"}, "IfcTester webapp not available. Please ensure the latest version of ifctester is installed."
            )
            return {"CANCELLED"}

        webapp_port = self.find_free_port()
        websocket_port = self.find_free_port()

        # Get the path to the serve.py module
        webapp_serve_path = ifctester.webapp.serve.__file__

        try:
            # Start the websocket server in a thread
            websocket_app = IfcTesterWebSocketServer(websocket_port)

            def run_websocket_server():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(websocket_app.start_server())
                except Exception as e:
                    print(f"WebSocket server error: {e}")
                finally:
                    loop.close()

            websocket_server_thread = threading.Thread(target=run_websocket_server, daemon=True)
            websocket_server_thread.start()

            py_version = sys.version_info
            bonsai_lib_path = (
                Path(bpy.utils.user_resource("EXTENSIONS"))
                / ".local"
                / "lib"
                / f"python{py_version.major}.{py_version.minor}"
                / "site-packages"
            )
            env = os.environ.copy()
            env["BONSAI_LIB_PATH"] = str(bonsai_lib_path)
            env["BONSAI_VERSION"] = tool.Blender.get_bonsai_version()

            # Start the Flask server as subprocess
            webapp_process = subprocess.Popen(
                [sys.executable, webapp_serve_path, "--host", "127.0.0.1", "--port", str(webapp_port)], env=env
            )

            # Update properties
            props.webapp_server_port = webapp_port
            props.websocket_server_port = websocket_port
            props.webapp_is_running = True

            # Wait a moment for servers to start, then open browser
            def delayed_open_browser():
                import time

                time.sleep(1.5)
                webbrowser.open(f"http://127.0.0.1:{webapp_port}?bonsai_server={websocket_port}")

            browser_thread = threading.Thread(target=delayed_open_browser, daemon=True)
            browser_thread.start()

            self.report(
                {"INFO"}, f"IfcTester webapp started at http://127.0.0.1:{webapp_port} (Websocket: {websocket_port})"
            )
            return {"FINISHED"}

        except Exception as e:
            # Clean up on error
            if webapp_process:
                webapp_process.terminate()
                webapp_process = None
            if websocket_server_thread and websocket_app:
                # The websocket server will be cleaned up when the thread ends
                websocket_server_thread = None
                websocket_app = None

            self.report({"ERROR"}, f"Failed to start servers: {str(e)}")
            return {"CANCELLED"}

    def find_free_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port


class StopIfcTesterWebapp(bpy.types.Operator):
    bl_idname = "bim.stop_ifc_tester_webapp"
    bl_label = "Stop IfcTester Webapp"
    bl_description = "Stop the IfcTester webapp server"

    def execute(self, context):
        global webapp_process, websocket_server_thread, websocket_app

        props = tool.Tester.get_tester_props()

        if webapp_process is None and websocket_server_thread is None:
            self.report({"WARNING"}, "No IfcTester servers are running")
            return {"CANCELLED"}

        errors = []

        # Stop webapp server
        if webapp_process:
            try:
                webapp_process.terminate()
                webapp_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                webapp_process.kill()
            except Exception as e:
                errors.append(f"Error stopping webapp server: {str(e)}")
            finally:
                webapp_process = None

        # Stop websocket server
        if websocket_app and websocket_server_thread:
            try:
                print("Stopping WebSocket server...")

                # Signal shutdown using thread-safe method
                websocket_app.stop_server()

                # Wait for the websocket thread to finish
                websocket_server_thread.join(timeout=5)

            except Exception as e:
                errors.append(f"Error during websocket shutdown: {str(e)}")
            finally:
                websocket_app = None
                websocket_server_thread = None

        # Update properties
        props.webapp_server_port = 0
        props.websocket_server_port = 0
        props.webapp_is_running = False

        if errors:
            self.report({"WARNING"}, f"IfcTester webapp and server stopped with errors: {'; '.join(errors)}")
        else:
            self.report({"INFO"}, "IfcTester webapp and server stopped")

        return {"FINISHED"}


class OpenIfcTesterWebapp(bpy.types.Operator):
    bl_idname = "bim.open_ifc_tester_webapp"
    bl_label = "Open IfcTester Webapp"
    bl_description = "Open the IfcTester webapp in the default browser"

    def execute(self, context):
        props = tool.Tester.get_tester_props()

        if not props.webapp_is_running:
            self.report({"ERROR"}, "IfcTester webapp is not running. Please start it first.")
            return {"CANCELLED"}

        webbrowser.open(f"http://127.0.0.1:{props.webapp_server_port}?bonsai_server={props.websocket_server_port}")
        return {"FINISHED"}


class SelectRequirement(bpy.types.Operator):
    bl_idname = "bim.select_requirement"
    bl_label = "Select Specification"
    bl_options = {"REGISTER", "UNDO"}
    spec_index: bpy.props.IntProperty()
    req_index: bpy.props.IntProperty()

    def execute(self, context):
        props = tool.Tester.get_tester_props()
        report = tool.Tester.report
        props.old_index = self.spec_index
        failed_entities = report[self.spec_index]["requirements"][self.req_index]["failed_entities"]
        props.n_entities = len(failed_entities)
        props.has_entities = True if props.n_entities > 0 else False
        props.failed_entities.clear()
        props.active_requirement_index = self.req_index

        for e in failed_entities:
            new_entity = props.failed_entities.add()
            new_entity.ifc_id = e["id"]
            new_entity.element = f'{e["class"]} | {e["name"]}'
            new_entity.reason = e["reason"]

        if props.flag:
            area = next(area for area in context.screen.areas if area.type == "VIEW_3D")
            area.spaces[0].shading.color_type = "OBJECT"
            area.spaces[0].shading.show_xray = True
            failed_ids = [e["id"] for e in failed_entities]
            for obj in context.scene.objects:
                ifc_id = tool.Blender.get_ifc_definition_id(obj)
                if ifc_id in failed_ids:
                    obj.color = (1, 0, 0, 1)
                else:
                    obj.color = (1, 1, 1, 1)

        return {"FINISHED"}


class SelectFailedEntities(bpy.types.Operator):
    bl_idname = "bim.select_failed_entities"
    bl_label = "Select Failed Entities"
    bl_options = {"REGISTER", "UNDO"}
    spec_index: bpy.props.IntProperty()
    req_index: bpy.props.IntProperty()

    def execute(self, context):
        props = tool.Tester.get_tester_props()
        report = tool.Tester.report
        props.old_index = self.spec_index
        failed_entities = report[self.spec_index]["requirements"][self.req_index]["failed_entities"]
        props.n_entities = len(failed_entities)
        props.has_entities = True if props.n_entities > 0 else False

        failed_ids = [e["id"] for e in failed_entities]
        for obj in context.scene.objects:
            ifc_id = tool.Blender.get_ifc_definition_id(obj)
            if ifc_id in failed_ids:
                obj.select_set(True)
            else:
                obj.select_set(False)

        self.report({"INFO"}, f"{len(failed_ids)} failed entities found, {len(context.selected_objects)} selected.")
        return {"FINISHED"}


class ColorSpecefication(bpy.types.Operator):
    """Colors all entities red that failed each test and color all entities yellow that failed some tests"""

    bl_idname = "bim.color_specification"
    bl_label = "Color Failed Entities"
    bl_options = {"REGISTER", "UNDO"}
    spec_index: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.IfcTesterProperties
        report = tool.Tester.report

        failures = [
            {e["id"] for e in requirement["failed_entities"]} for requirement in report[self.spec_index]["requirements"]
        ]
        failed_all_ids = set.intersection(*failures)
        failed_some_ids = set.union(*failures) - failed_all_ids
        if props.flag:
            area = next(area for area in context.screen.areas if area.type == "VIEW_3D")
            area.spaces[0].shading.color_type = "OBJECT"
            area.spaces[0].shading.show_xray = True
            for obj in context.scene.objects:
                ifc_id = tool.Blender.get_ifc_definition_id(obj)
                if ifc_id in failed_all_ids:
                    obj.color = (1, 0, 0, 1)
                elif ifc_id in failed_some_ids:
                    obj.color = (1, 1, 0, 1)
                else:
                    obj.color = (1, 1, 1, 1)

        return {"FINISHED"}


class ExportBcf(bpy.types.Operator, ExportHelper):
    bl_idname = "bim.export_bcf"
    bl_label = "Export BCF"
    bl_description = "Save ifctester BCF report by the provided filepath."
    bl_options = {"REGISTER", "UNDO"}
    filter_glob: bpy.props.StringProperty(default="*.bcf", options={"HIDDEN"})
    filename_ext = ".bcf"

    def execute(self, context):
        bcf_reporter = ifctester.reporter.Bcf(tool.Tester.specs)
        bcf_reporter.report()
        bcf_reporter.to_file(self.filepath)
        self.report({"INFO"}, "Finished exporting!")
        return {"FINISHED"}
