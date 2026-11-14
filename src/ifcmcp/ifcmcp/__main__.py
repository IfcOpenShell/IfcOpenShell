# This file was generated with the assistance of an AI coding tool.
import argparse
import importlib.util

from ifcmcp import __version__


def execute_allowed(transport: str, no_execute: bool) -> bool:
    """Offer ifc_execute only over stdio, where the client is the process that started the server.

    Over the network transports anyone who can reach the port could run code.
    """
    return transport == "stdio" and not no_execute


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
    parser.add_argument(
        "--bonsai",
        nargs="?",
        type=int,
        const=9877,
        metavar="PORT",
        help=(
            "Work on the model open in Bonsai instead of a file, through its MCP bridge "
            "(default port 9877). Offers the query tools and ifc_edit, ifc_shape, "
            "ifc_quantify, ifc_undo and ifc_redo, and the bonsai_ tools on its selection and viewport"
        ),
    )
    parser.add_argument(
        "--no-execute",
        action="store_true",
        help="Don't offer ifc_execute, which runs arbitrary Python sent by the client (only offered over stdio)",
    )

    args = parser.parse_args()

    if importlib.util.find_spec("mcp") is None:
        import sys

        print(
            "error: the 'mcp' package is required to run the server.\nInstall it with:  pip install mcp",
            file=sys.stderr,
        )
        sys.exit(1)

    from ifcmcp.server import build_server

    server = build_server(allow_execute=execute_allowed(args.transport, args.no_execute), bonsai_port=args.bonsai)
    server.run(transport=args.transport)


if __name__ == "__main__":
    main()
