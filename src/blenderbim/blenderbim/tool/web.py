# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>, 2022 Yassine Oualid <yassine@sigmadimensions.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
from blenderbim.bim.module.web.data import WebData
import blenderbim.core.tool
import blenderbim.tool as tool
import ifcopenshell.api.sequence
from typing import Any, Dict, Optional
import time
import socket
import sys
import os
import errno
import subprocess
import webbrowser
import asyncio
import socketio
import threading
import queue
import json
from time import sleep
from pathlib import Path

sio = None
ws_process = None
ws_thread = None
web_operator_queue = queue.Queue()

RECONNECTION_ATTEMPTS = 3
RECONNECTION_DELAY = 2
IFC_TASK_ATTRIBUTE_MAP = {
    "pStart": "ScheduleStart",
    "pEnd": "ScheduleFinish",
    "pName": "Name",
}


class Web(blenderbim.core.tool.Web):
    @classmethod
    def generate_port_number(cls) -> int:
        """
        Generate a free port number.

        This method creates a temporary socket to bind to a free port.
        It then retrieves the port number, and returns it.

        Returns:
            int: The port number that was generated.
        """
        print("Generating port number")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("localhost", 0))  # Bind to a free port
            port = s.getsockname()[1]  # get the bound port
            print(f"Port number: {port}")
            return port

    @classmethod
    def is_port_available(cls, port: int) -> bool:
        """
        Attempts to connect to the specified port on localhost.

        If the connection is refused, the port is available for use; otherwise, it is in use.

        Args:
           - port (int): The port number to check.

        Returns:
            bool: True if the port is available, False if it is in use.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # connect_ex returns errno.SUCCESS (0) if the connection succeeds
            # otherwise returns errno.ECONNREFUSED (111 or 10061) if no server is listening
            return s.connect_ex(("localhost", port)) == errno.ECONNREFUSED

    @classmethod
    def start_websocket_server(cls, port: int) -> None:
        """
        Starts a WebSocket server on the specified port.

        This method sets up the environment, locates paths, and starts
        the WebSocket server process. It also handles the creation and updating of a PID file to keep track
        of running server instances.

        Args:
           - port (int): The port number on which to start the WebSocket server.
        """
        import addon_utils

        global ws_process

        webui_path = os.path.join(bpy.context.scene.BIMProperties.data_dir, "webui")
        ws_path = os.path.join(webui_path, "sioserver.py")

        py_version = sys.version_info

        if bpy.app.version >= (4, 2, 0):
            blenderbim_lib_path = (
                Path(bpy.utils.user_resource("EXTENSIONS"))
                / ".local"
                / "lib"
                / f"python{py_version.major}.{py_version.minor}"
                / "site-packages"
            )
        else:
            addon = [a for a in addon_utils.modules() if a.bl_info["name"] == "BlenderBIM"][0]
            blenderbim_path = os.path.dirname(addon.__file__)
            blenderbim_lib_path = os.path.join(blenderbim_path, "libs", "site", "packages")

        env = os.environ.copy()
        env["BLENDERBIM_LIB_PATH"] = str(blenderbim_lib_path)
        env["BLENDERBIM_VERSION"] = tool.Blender.get_blenderbim_version()

        ws_process = subprocess.Popen(
            [sys.executable, ws_path, "--p", str(port), "--host", "127.0.0.1"],
            cwd=webui_path,
            env=env,
        )

        cls.set_is_running(True)

    @classmethod
    def connect_websocket_server(cls, port: int) -> None:
        """
        Connect to a WebSocket server on the specified port.

        This method sets up an asynchronous Socket.IO client with
        reconnection attempts, starts an asyncio thread, connects to the WebSocket server, and sets the connection status.

        Args:
           - port (int): The port number to connect to the WebSocket server.
        """
        global ws_thread, sio

        if bpy.context.scene.WebProperties.is_connected:
            print(f"Already connected to websocket server on port: {port}")
            return

        sio = socketio.AsyncClient(
            reconnection=True,
            reconnection_attempts=RECONNECTION_ATTEMPTS,
            reconnection_delay=RECONNECTION_DELAY,
            logger=True,
        )

        ws_thread = AsyncioThread()
        ws_thread.daemon = True
        ws_thread.start()

        ws_url = f"ws://localhost:{port}/blender"
        ws_thread.run_coro(cls.sio_connect(ws_url))
        cls.set_is_connected(True)
        bpy.app.timers.register(cls.check_operator_queue)

    @classmethod
    def disconnect_websocket_server(cls) -> None:
        """
        Disconnects the WebSocket server and stops the associated thread.

        This method is responsible for disconnecting the WebSocket server, stopping the asyncio thread,
        and resetting the global variables related to the WebSocket connection.
        """
        global ws_thread, sio
        ws_thread.run_coro(cls.sio_disconnect())
        ws_thread.stop()
        ws_thread = None
        sio = None
        cls.set_is_connected(False)

    @classmethod
    def kill_websocket_server(cls) -> None:
        """
        Terminate the currently running WebSocket server.

        This method checks if there is an active WebSocket server process. If so, it disconnects it (if connected),
        removes its PID from the PID file, terminates the process, and updates the server's running status.
        """
        global ws_process

        if ws_process is None:
            print("No Websocket server running")
            return

        if bpy.context.scene.WebProperties.is_connected:
            cls.disconnect_websocket_server()

        # sleep(0.5)
        webui_path = os.path.join(bpy.context.scene.BIMProperties.data_dir, "webui")
        pid_file = os.path.join(webui_path, "running_pid.json")
        with open(pid_file, "r") as f:
            pids = json.load(f)

        if str(ws_process.pid) in pids:
            del pids[str(ws_process.pid)]

        # Write the updated PIDs back to the file
        with open(pid_file, "w") as f:
            json.dump(pids, f, indent=4)

        ws_process.kill()
        ws_process = None

        cls.set_is_running(False)
        print("Websocket server killed successfully")

    @classmethod
    def has_started(cls, port):
        max_time = 5
        start = time.time()
        while True:
            if time.time() - start > max_time:
                return False
            webui_path = os.path.join(bpy.context.scene.BIMProperties.data_dir, "webui")
            pid_file = os.path.join(webui_path, "running_pid.json")
            try:
                with open(pid_file, "r") as f:
                    data = json.load(f)
                    if port in data.values():
                        return True
            except:
                pass
            time.sleep(0.1)

    @classmethod
    def send_webui_data(
        cls,
        data: Optional[Any] = None,
        data_key: str = "data",
        event: str = "data",
        namespace: str = "/blender",
        use_web_data: bool = True,
    ) -> None:
        """
        Sends data to the Web UI via Websocket connection.

        Args:
        - data (Optional[Any]): The data to send. If None, just sends data from WebData.
        - data_key (str): The key under which to store the data in the payload. Defaults to "data".
        - event (str): The WebSocket event to emit. Defaults to "data".
        - namespace (str): The namespace for the WebSocket event. Defaults to "/blender".
        - use_web_data (bool): Whether to use data from WebData. Defaults to True.
        """

        global ws_thread
        payload = {}

        if use_web_data:
            if not WebData.is_loaded:
                WebData.load()
            payload = WebData.data

        if data is not None:
            payload[data_key] = data

        if ws_thread is not None and bpy.context.scene.WebProperties.is_connected:
            ws_thread.run_coro(cls.sio_send(payload, event, namespace))

    @classmethod
    def check_operator_queue(cls) -> None | float:
        if not bpy.context.scene.WebProperties.is_connected:
            with web_operator_queue.mutex:
                web_operator_queue.queue.clear()
            return None  # unregister timer if not connected

        while not web_operator_queue.empty():
            operator = web_operator_queue.get_nowait()
            if not operator:
                continue
            if operator["sourcePage"] == "csv":
                cls.handle_csv_operator(operator["operator"])
            elif operator["sourcePage"] == "gantt":
                cls.handle_gantt_operator(operator["operator"])
            elif operator["sourcePage"] == "drawings":
                cls.handle_drawings_operator(operator["operator"])
        return 1.0

    @classmethod
    def handle_csv_operator(cls, operator_data: dict) -> None:
        if operator_data["type"] == "selection":
            bpy.ops.object.select_all(action="DESELECT")
            guid = operator_data["globalId"]
            ele = tool.Ifc.get().by_guid(guid)
            obj = tool.Ifc.get_object(ele)
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)

    @classmethod
    def handle_gantt_operator(cls, operator_data: dict) -> None:
        ifc_file = tool.Ifc.get()
        if operator_data["type"] == "editTask":
            task_id = int(operator_data["taskId"])
            task = ifc_file.by_id(task_id)
            task_time = task.TaskTime
            column = operator_data["column"]
            new_value = operator_data["value"]

            try:
                ifcopenshell.api.sequence.edit_task(
                    ifc_file, task, attributes={IFC_TASK_ATTRIBUTE_MAP[column]: str(new_value)}
                )
            except AttributeError:
                if task_time is None:
                    ifcopenshell.api.sequence.add_task_time(ifc_file, task)
                    task_time = task.TaskTime
                ifcopenshell.api.sequence.edit_task_time(
                    ifc_file, task_time=task_time, attributes={IFC_TASK_ATTRIBUTE_MAP[column]: str(new_value)}
                )

        bpy.ops.bim.load_task_properties()

        # after updating, send new gantt data to handle the case where
        # changing a task cascades and changes other tasks. as this wouldn't
        # be reflected in the web ui
        work_schedule = ifc_file.by_id(operator_data["workScheduleId"])
        task_json = tool.Sequence.create_tasks_json(work_schedule)
        gantt_data = {"tasks": task_json, "work_schedule": work_schedule.get_info(recursive=True)}
        cls.send_webui_data(data=gantt_data, data_key="gantt_data", event="gantt_data")

    @classmethod
    def handle_drawings_operator(cls, operator_data: dict) -> None:
        if operator_data["type"] == "getDrawings":
            drawings_data = []
            sheets_data = []
            ifc_file_dir = os.path.dirname(bpy.context.scene.BIMProperties.ifc_file)

            sheets = [d for d in tool.Ifc.get().by_type("IfcDocumentInformation") if d.Scope == "SHEET"]
            for sheet in sorted(sheets, key=lambda s: getattr(s, "Identification", getattr(s, "DocumentId", None))):
                for reference in tool.Drawing.get_document_references(sheet):
                    reference_description = tool.Drawing.get_reference_description(reference)
                    reference_location = tool.Drawing.get_reference_location(reference)
                    reference_name = os.path.basename(reference_location)
                    reference_path = os.path.join(ifc_file_dir, reference_location)
                    if reference_description == "SHEET":
                        sheets_data.append({"name": reference_name, "path": reference_path})
                    if reference_description == "DRAWING":
                        drawings_data.append({"name": reference_name, "path": reference_path})

            cls.send_webui_data(
                data={"drawings": drawings_data, "sheets": sheets_data}, data_key="drawings_data", event="drawings_data"
            )

    @classmethod
    def open_web_browser(cls, port: int) -> None:
        webbrowser.open(f"http://127.0.0.1:{port}/")

    @classmethod
    async def sio_connect(cls, url: str) -> None:
        await sio.connect(url, transports=["websocket"], namespaces="/blender")
        sio.on("web_operator", cls.sio_listen_web_operator, namespace="/blender")

    @classmethod
    async def sio_disconnect(cls) -> None:
        await sio.disconnect()

    @classmethod
    async def sio_send(cls, data: Any, event: str = "data", namespace: str = "/blender") -> None:
        await sio.emit(event, data, namespace=namespace)

    @classmethod
    async def sio_listen_web_operator(cls, data: dict) -> None:
        try:
            web_operator_queue.put_nowait(data)
        except queue.Full:
            pass

    @classmethod
    def set_is_running(cls, is_running: bool) -> None:
        bpy.context.scene.WebProperties.is_running = is_running

    @classmethod
    def set_is_connected(cls, is_connected: bool) -> None:
        bpy.context.scene.WebProperties.is_connected = is_connected


class AsyncioThread(threading.Thread):
    def __init__(self, *args, loop=None, **kwargs):
        """
        Initialize an instance of AsyncioThread.

        This class represents a thread that runs an asyncio event loop. It is used to handle asynchronous tasks
        in a separate thread from the main thread.

        Args:
           - *args: Variable length argument list. These arguments are passed to the superclass constructor.
           - loop: An existing asyncio event loop. If None, a new event loop is created.
           - **kwargs: Arbitrary keyword arguments. These arguments are passed to the superclass constructor.
        """
        super().__init__(*args, **kwargs)
        self.loop = loop or asyncio.new_event_loop()
        self.running = False

    def run(self):
        """
        Start the asyncio event loop and mark the thread as running.
        """
        self.running = True
        self.loop.run_forever()

    def run_coro(self, coro) -> Any:
        """
        Run a coroutine in the asyncio event loop from a separate thread.

        Args:
           - coro: The coroutine to be run.

        Returns:
            The result of the coroutine.
        """
        return asyncio.run_coroutine_threadsafe(coro, loop=self.loop).result()

    def stop(self) -> None:
        """
        Stop the asyncio event loop and join the thread.
        """
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.join()
        self.running = False
