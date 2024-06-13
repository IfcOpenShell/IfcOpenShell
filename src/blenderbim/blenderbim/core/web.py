def generate_port_number(web):
    return web.generate_port_number()


def connect_websocket_server(web, port):
    # check if port already has a server listening to it
    if web.is_port_available(port):
        web.start_websocket_server(port)

    web.connect_websocket_server(port)


def disconnect_websocket_server(web):
    web.disconnect_websocket_server()


def kill_websocket_server(web):
    web.kill_websocket_server()


def open_web_browser(web):
    web.open_web_browser()
