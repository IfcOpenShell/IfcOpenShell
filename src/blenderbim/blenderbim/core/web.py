def open_web_ui(web):
    web.open_web_ui()


def generate_port_number(web):
    return web.generate_port_number()


def connect_websocket_server(web, port):
    # check if port already has a server listening to it
    if web.is_port_available(port):
        web.start_websocket_server(port)
        web.show_webserver_running()
    else:
        web.hide_webserver_running()

    web.connect_websocket_server(port)


def kill_websocket_server(web):
    web.kill_websocket_server()
    web.hide_webserver_running()
