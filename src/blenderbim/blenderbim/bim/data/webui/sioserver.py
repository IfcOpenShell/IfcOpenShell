import sys
import os

blenderbim_path = os.environ.get("blenderbim_path")
if blenderbim_path:
    blenderbim_lib_path = os.path.join(blenderbim_path, "libs", "site", "packages")
    sys.path.insert(0, blenderbim_lib_path)

import argparse
from aiohttp import web
import socketio
import pystache
import json

sio_port = 8080  # default port

sio = socketio.AsyncServer(
    cors_allowed_origins="*",
    async_mode="aiohttp",
)

# sio.instrument(
#     auth={
#         "username": "admin",
#         "password": "admin",
#     }
# )

app = web.Application()
sio.attach(app)

blender_messages = {}


# Web namespace
class WebNamespace(socketio.AsyncNamespace):
    def __init__(self, namespace):
        super().__init__(namespace)

    async def on_connect(self, sid, environ):
        print(f"Web client connected: {sid}")

    async def on_disconnect(self, sid):
        print(f"Web client disconnected: {sid}")

    async def on_web_operator(self, sid, data):
        await sio.emit(
            "web_operator",
            data,
            namespace="/blender",
            room=data["blenderId"],
        )


# Blender namespace
class BlenderNamespace(socketio.AsyncNamespace):
    def __init__(self, namespace):
        super().__init__(namespace)

    async def on_connect(self, sid, environ):
        print(f"Blender client connected: {sid}")
        # Notify web client about new connection
        blender_messages[sid] = {}
        await sio.emit("blender_connect", sid, namespace="/web")

    async def on_disconnect(self, sid):
        print(f"Blender client disconnected: {sid}")
        # Remove client message and notify web client about disconnection
        if sid in blender_messages:
            del blender_messages[sid]
        await sio.emit("blender_disconnect", sid, namespace="/web")

    async def on_data(self, sid, data):
        print(f"Data from Blender client {sid}")
        # blender_messages[sid]["default_data"] = data
        # await sio.emit("default_data", {"blenderId": sid, "data": data}, namespace="/web")

    async def on_csv_data(self, sid, data):
        print(f"CSV data from Blender client {sid}")
        # Store the message and forward it to the web client
        blender_messages[sid]["csv_data"] = data
        await sio.emit("csv_data", {"blenderId": sid, "data": data}, namespace="/web")

    async def on_gantt_data(self, sid, data):
        print(f"Gant Chart data from Blender client {sid}")
        blender_messages[sid]["gantt_data"] = data
        await sio.emit("gantt_data", {"blenderId": sid, "data": data}, namespace="/web")


# Attach namespaces
sio.register_namespace(WebNamespace("/web"))
sio.register_namespace(BlenderNamespace("/blender"))


# Define a route to render the index.html template
async def index(request):
    with open("templates/index.html", "r") as f:
        template = f.read()
    html_content = pystache.render(template, {"port": sio_port})
    return web.Response(text=html_content, content_type="text/html")


async def gantt(request):
    with open("templates/gantt.html", "r") as f:
        template = f.read()
    html_content = pystache.render(template, {"port": sio_port})
    return web.Response(text=html_content, content_type="text/html")


app.router.add_get("/", index)
app.router.add_get("/gantt", gantt)
app.router.add_static("/jsgantt/", path="../gantt", name="jsgantt")
app.router.add_static("/static/", path="./static", name="static")


def main():
    global sio_port

    parser = argparse.ArgumentParser(description="SocketIO server")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=8080, help="Port to run the server on")

    args = parser.parse_args()
    sio_port = args.port
    web.run_app(app, host=args.host, port=sio_port)


if __name__ == "__main__":
    main()
    # web.run_app(app, host="127.0.0.1", port=sio_port)
