# ifc_cli/src/ifcmcp/ifcmcp/__main__.py
from ifcmcp.server import build_server

server = build_server()
server.run(transport="stdio")