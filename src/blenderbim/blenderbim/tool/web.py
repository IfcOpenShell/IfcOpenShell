import bpy
import json
import blenderbim.core.tool
from typing import Union, Literal
import os
import webbrowser
import asyncio
import threading
import websockets
import json

CONNECTION_CHECK_DELAY = 10
connected_sockets = set()
websocket_server: websockets.WebSocketServer
ws_thread_loop = asyncio.new_event_loop()

class Web(blenderbim.core.tool.Web):
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
