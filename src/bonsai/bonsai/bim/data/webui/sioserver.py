import sys
import os
import webbrowser

bonsai_lib_path = os.environ.get("BONSAI_LIB_PATH")
bonsai_version = os.environ.get("BONSAI_VERSION")

if bonsai_lib_path:
    sys.path.insert(0, bonsai_lib_path)

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
app = web.Application()
sio.attach(app)


# represents a caching for blender messages
blender_messages = {}
blender_theme = {}


# we define two namespaces, one for Bonsai and one for Web UI
# each namespace has its own event handlers that are called when an event is emitted by a client
# Web namespace
class WebNamespace(socketio.AsyncNamespace):
    def __init__(self, namespace):
        super().__init__(namespace)

    async def on_connect(self, sid, environ):
        print(f"Web client connected: {sid}")
        if blender_messages:
            await sio.emit("connected_clients", list(blender_messages.keys()), namespace="/web", room=sid)
            await sio.emit("theme_data", blender_theme, namespace="/web", room=sid)
            await self.send_cached_messages(sid)

    async def on_disconnect(self, sid):
        print(f"Web client disconnected: {sid}")

    async def on_web_operator(self, sid, data):
        await sio.emit(
            "web_operator",
            data,
            namespace="/blender",
            room=data.get("blenderId", None),
        )

    async def on_get_svg(self, sid, data):
        print("hello world!")
        file_path = data["path"]
        with open(file_path, "r") as file:
            svg_data = file.read()
        await sio.emit("svg_data", svg_data, room=sid, namespace="/web")

    async def send_cached_messages(self, sid):
        # Send cached messages to the connected web client
        for blenderId, messages in blender_messages.items():
            if "csv_data" in messages:
                await self.emit("csv_data", {"blenderId": blenderId, "data": messages["csv_data"]}, room=sid)
            if "gantt_data" in messages:
                await self.emit("gantt_data", {"blenderId": blenderId, "data": messages["gantt_data"]}, room=sid)
            if "demo_data" in messages:
                await self.emit("demo_data", {"blenderId": blenderId, "data": messages["demo_data"]}, room=sid)

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
        await sio.emit("default_data", {"blenderId": sid, "data": data}, namespace="/web")

    async def on_csv_data(self, sid, data):
        print(f"CSV data from Blender client {sid}")
        # Store the message and forward it to the web client
        blender_messages[sid]["csv_data"] = data
        await sio.emit("csv_data", {"blenderId": sid, "data": data}, namespace="/web")

    async def on_gantt_data(self, sid, data):
        print(f"Gant Chart data from Blender client {sid}")
        blender_messages[sid]["gantt_data"] = data
        await sio.emit("gantt_data", {"blenderId": sid, "data": data}, namespace="/web")

    async def on_drawings_data(self, sid, data):
        print(f"Drawings data from Blender client {sid}")
        blender_messages[sid]["drwings_data"] = data
        await sio.emit("drawings_data", {"blenderId": sid, "data": data}, namespace="/web")

    async def on_theme_data(self, sid, data):
        global blender_theme
        blender_theme = data
        await sio.emit("theme_data", data, namespace="/web")


    # this function will be called when the event demo_data is emitted 
    async def on_demo_data(self, sid, data):
        print(f"Demo data from Blender client {sid}")
        blender_messages[sid]["demo_data"] = data
        await sio.emit("demo_data", {"blenderId": sid, "data": data}, namespace="/web")


async def schedules(request):
    with open("templates/index.html", "r") as f:
        template = f.read()
    html_content = pystache.render(template, {"port": sio_port, "version": bonsai_version})
    return web.Response(text=html_content, content_type="text/html")


async def sequencing(request):
    with open("templates/gantt.html", "r") as f:
        template = f.read()
    html_content = pystache.render(template, {"port": sio_port, "version": bonsai_version})
    return web.Response(text=html_content, content_type="text/html")


async def documentation(request):
    with open("templates/drawings.html", "r") as f:
        template = f.read()
    html_content = pystache.render(template, {"port": sio_port, "version": bonsai_version})
    return web.Response(text=html_content, content_type="text/html")


# This is a request handler for the /demo URL endpoint.
# It serves the demo HTML file after using pystache to render the variables
async def demo(request):
    with open("templates/demo.html", "r") as f:
        template = f.read()
    html_content = pystache.render(template, {"port": sio_port, "version": bonsai_version})
    return web.Response(text=html_content, content_type="text/html")


async def on_startup(app):
    pid_file = "running_pid.json"

    if os.path.exists(pid_file):
        with open(pid_file, "r") as f:
            pids = json.load(f)
    else:
        pids = {}

    pids[str(os.getpid())] = sio_port

    with open(pid_file, "w") as f:
        json.dump(pids, f, indent=4)


# Add on startup function
app.on_startup.append(on_startup)

# Attach namespaces
sio.register_namespace(WebNamespace("/web"))
sio.register_namespace(BlenderNamespace("/blender"))

# Regsier routes
app.router.add_get("/", schedules)
app.router.add_get("/documentation", documentation)
app.router.add_get("/sequencing", sequencing)
app.router.add_get("/demo", demo)

# Add static files
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
