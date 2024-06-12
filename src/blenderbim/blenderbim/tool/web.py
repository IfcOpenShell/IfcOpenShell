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
import threading
import websockets
import json

CONNECTION_CHECK_DELAY = 10
connected_sockets = set()
websocket_server: websockets.WebSocketServer
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
        pass

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
    def show_webserver_running(cls):
        bpy.context.scene.WebProperties.show_webserver_running = True

    @classmethod
    def hide_webserver_running(cls):
        bpy.context.scene.WebProperties.show_webserver_running = False

    @classmethod
    def get_webui_data(cls):
        data = {}
        data["ifc_file"] = bpy.context.scene.BIMProperties.ifc_file
        return json.dumps(data)

    @classmethod
    async def broadcast(cls, message):
        for sock in connected_sockets:
            await sock.send(message)

    @classmethod
    async def ws_server_handler(cls, websocket):
        connected_sockets.add(websocket)
        intial_data = cls.get_webui_data()
        await cls.broadcast(intial_data)
        try:
            async for message in websocket:
                # TODO: handle incoming messages
                continue
        finally:
            connected_sockets.remove(websocket)

    @classmethod
    async def run_ws_server(cls):
        websocket_server = await websockets.serve(cls.ws_server_handler, "localhost", 8765)
        print("Web-UI WebSocket server started.")

        # Check if a client is connected every 10 seconds
        async def check_connections():
            while True:
                await asyncio.sleep(CONNECTION_CHECK_DELAY)
                if not connected_sockets:
                    print("No Web-UI connected, shutting down the WebSocket server")
                    websocket_server.close()
                    break

        await check_connections()
        await websocket_server.wait_closed()

    @classmethod
    def open_web_ui(cls):
        def set_thread_loop():
            asyncio.set_event_loop(ws_thread_loop)
            asyncio.run(cls.run_ws_server())

        wserver_thread = threading.Thread(target=set_thread_loop)
        wserver_thread.daemon = True
        wserver_thread.start()

        def open_browser():
            webbrowser.open("file://" + os.path.join(bpy.context.scene.BIMProperties.data_dir, "webui", "index.html"))

        # Delay for 2 seconds before openning browser
        timer = threading.Timer(2.0, open_browser)
        timer.start()
