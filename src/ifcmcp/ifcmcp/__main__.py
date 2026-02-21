# This file was generated with the assistance of an AI coding tool.
from ifcmcp.server import build_server

def main():
    server = build_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()