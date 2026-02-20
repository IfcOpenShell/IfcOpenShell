# ifc_cli/src/ifcmcp/ifcmcp/__main__.py
from ifcmcp.server import build_server


def main():
    server = build_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()