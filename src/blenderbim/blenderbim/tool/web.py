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
import socket
import os
import subprocess
import webbrowser
import asyncio
import socketio
import threading

sio = None
ws_process = None
ws_thread = None


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
        ws_path = os.path.join(bpy.context.scene.BIMProperties.data_dir, "webui", "sioserver.py")
        ws_process = subprocess.Popen(["python", ws_path, "--p", str(port), "--host", "127.0.0.1"])
        cls.open_web_browser(port)
        cls.set_is_running(True)

    @classmethod
    def connect_websocket_server(cls, port):
        global ws_thread, sio

        if bpy.context.scene.WebProperties.is_connected:
            print(f"Already connected to websocket server on port: {port}")
            return

        sio = socketio.AsyncClient(reconnection=True, reconnection_attempts=3, reconnection_delay=2, logger=True)

        ws_thread = AsyncioThread()
        ws_thread.daemon = True
        ws_thread.start()

        ws_url = f"ws://localhost:{port}/blender"
        ws_thread.run_coro(cls.sio_connect(ws_url))
        cls.set_is_connected(True)
        cls.send_webui_data()

    @classmethod
    def disconnect_websocket_server(cls):
        global ws_thread, sio
        ws_thread.run_coro(cls.sio_disconnect())
        ws_thread.stop()
        ws_thread = None
        sio = None
        cls.set_is_connected(False)

    @classmethod
    def kill_websocket_server(cls):
        global ws_process

        if ws_process is None:
            print("No Websocket server running")
            return

        if bpy.context.scene.WebProperties.is_connected:
            cls.disconnect_websocket_server()

        ws_process.terminate()
        ws_process.wait()
        ws_process = None
        cls.set_is_running(False)

        print("Websocket server terminated successfully")

    @classmethod
    def send_webui_data(cls):
        global ws_thread

        if not WebData.is_loaded:
            WebData.load()

        ws_thread.run_coro(cls.sio_send(WebData.data))

    @classmethod
    def open_web_browser(cls, port):
        webbrowser.open(f"http://127.0.0.1:{port}/")

    @classmethod
    async def sio_connect(cls, url):
        await sio.connect(url, transports=["websocket"], namespaces="/blender")

        # TODO: register event handlers to handle incoming messages
        # sio.on("data", test.message_handler, namespace="/blender")

        # await sio.emit("data", {"from": "client"}, namespace="/blender")

    @classmethod
    async def sio_disconnect(cls):
        await sio.disconnect()

    @classmethod
    async def sio_send(cls, data):
        await sio.emit("data", data, namespace="/blender")

    @classmethod
    def set_is_running(cls, is_running):
        bpy.context.scene.WebProperties.is_running = is_running

    @classmethod
    def set_is_connected(cls, is_connected):
        bpy.context.scene.WebProperties.is_connected = is_connected


class AsyncioThread(threading.Thread):
    def __init__(self, *args, loop=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop = loop or asyncio.new_event_loop()
        self.running = False

    def run(self):
        self.running = True
        self.loop.run_forever()

    def run_coro(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, loop=self.loop).result()

    def stop(self):
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.join()
        self.running = False
