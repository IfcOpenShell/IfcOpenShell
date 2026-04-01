# This file was generated with the assistance of an AI coding tool.
import argparse

from ifcmcp import __version__


def main():
    parser = argparse.ArgumentParser(
        prog="python3 -m ifcmcp",
        description=(
            "ifcmcp — MCP server for IFC building models.\n\n"
            "Runs a Model Context Protocol server over stdio so that MCP clients\n"
            "can query and edit IFC files without writing them to disk between\n"
            "operations.\n\n"
            "Add to .mcp.json to configure:\n"
            '  {"mcpServers": {"ifc": {"type": "stdio", "command": "python3", "args": ["-m", "ifcmcp"]}}}'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"ifcmcp {__version__}")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="MCP transport to use (default: stdio)",
    )

    args = parser.parse_args()

    try:
        from mcp.server.fastmcp import FastMCP  # noqa: F401
    except ImportError:
        import sys

        print(
            "error: the 'mcp' package is required to run the server.\n" "Install it with:  pip install mcp",
            file=sys.stderr,
        )
        sys.exit(1)

    from ifcmcp.server import build_server

    server = build_server()
    server.run(transport=args.transport)


if __name__ == "__main__":
    main()
