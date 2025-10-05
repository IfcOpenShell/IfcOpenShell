# IfcTester - IDS based model auditing
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcTester.
#
# IfcTester is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcTester is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcTester.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import argparse
import mimetypes

bonsai_lib_path = os.environ.get("BONSAI_LIB_PATH")
print(os.environ)
print(bonsai_lib_path)
bonsai_version = os.environ.get("BONSAI_VERSION")

if bonsai_lib_path:
    sys.path.insert(0, bonsai_lib_path)

from flask import Flask, send_from_directory, send_file

# Browsers expecting this specific MIME type for .mjs files,
# otherwise they fail to load.
mimetypes.add_type("text/javascript", ".mjs")

app = Flask(__name__)


def get_static_folder():
    base_dir = os.path.dirname(__file__)
    dist_dir = os.path.join(base_dir, "dist")
    www_dir = os.path.join(base_dir, "www")

    if os.path.exists(dist_dir) and os.path.isdir(dist_dir):
        return dist_dir
    elif os.path.exists(www_dir) and os.path.isdir(www_dir):
        return www_dir
    else:
        return dist_dir


STATIC_FOLDER = get_static_folder()


@app.route("/")
def index():
    return send_file(os.path.join(STATIC_FOLDER, "index.html"))


@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(STATIC_FOLDER, filename)


@app.route("/assets/<path:filename>")
def assets(filename):
    return send_from_directory(os.path.join(STATIC_FOLDER, "assets"), filename)


@app.errorhandler(404)
def not_found(error):
    return send_file(os.path.join(STATIC_FOLDER, "index.html"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start IfcTester webapp")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind to (default: 5000)")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--dist-dir", default=STATIC_FOLDER, help="Directory containing built files")

    args = parser.parse_args()

    STATIC_FOLDER = args.dist_dir

    print(f"Serving IfcTester webapp from: {STATIC_FOLDER}")
    print(f"Server running at: http://{args.host}:{args.port}")

    app.run(host=args.host, port=args.port, debug=args.debug)
