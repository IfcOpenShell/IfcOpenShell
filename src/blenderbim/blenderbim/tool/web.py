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
import json
import blenderbim.core.tool
from typing import Union, Literal
import socket
import os
import subprocess
import webbrowser
import asyncio
import socketio
import threading
import json


sio = socketio.AsyncClient(reconnection=True, reconnection_attempts=3, reconnection_delay=2, logger=True)
ws_thread_loop = asyncio.new_event_loop()
ws_process = None


class Web(blenderbim.core.tool.Web):
    @classmethod
    def generate_port_number(cls):
        print("Generating port number")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("localhost", 0))  # Bind to a free port
            port = s.getsockname()[1]  # get the bound port
            print(f"Port number: {port}")
            return port

    @classmethod
    def is_port_available(cls, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # connect_ex returns 0 if the connection succeeds
            # indicating the port is in use
            # otherwise returns 10061 if no server is listening
            # indicating the port is available for use
            return s.connect_ex(("localhost", port)) == 10061

    @classmethod
    def start_websocket_server(cls, port):
        global ws_process
        ws_path = os.path.join(bpy.context.scene.BIMProperties.data_dir, "webui", "app.py")

        env = os.environ.copy()
        env["FLASK_APP"] = ws_path

        ws_process = subprocess.Popen(["flask", "run", "-p", str(port)], env=env)

    @classmethod
    def connect_websocket_server(cls, port):
        def start_thread_loop(url):
            global ws_thread_loop
            ws_thread_loop = asyncio.new_event_loop()
            ws_thread_loop.run_until_complete(cls.sio_connect(url))

        ws_url = f"ws://localhost:{port}/blender"
        wserver_thread = threading.Thread(target=start_thread_loop, args=(ws_url,))
        wserver_thread.daemon = True
        wserver_thread.start()

    @classmethod
    async def sio_connect(cls, url):
        await sio.connect(url, transports=["websocket"], namespaces="/blender")

        # TODO: register event handlers to handle incoming messages
        # sio.on("data", test.message_handler, namespace="/blender")

        # await sio.emit("data", {"from": "client"}, namespace="/blender")

    @classmethod
    def disconnect_websocket_server(cls):
        ws_thread_loop.run_until_complete(cls.sio_disconnect())
        print("Disconnected from websocket server")

    @classmethod
    async def sio_disconnect(cls):
        await sio.disconnect()

    @classmethod
    def kill_websocket_server(cls):
        global ws_process

        if ws_process is None:
            print("No webserver running")
            return

        ws_process.terminate()
        ws_process.wait()
        ws_process = None
        print("Webserver terminated successfully")

    @classmethod
    def set_is_running(cls, is_running):
        bpy.context.scene.WebProperties.is_running = is_running

    @classmethod
    def set_is_connected(cls, is_connected):
        bpy.context.scene.WebProperties.is_connected = is_connected

    @classmethod
    def get_webui_data(cls):
        data = {}
        data["ifc_file"] = bpy.context.scene.BIMProperties.ifc_file
        return json.dumps(data)
