# ifccityjson - Python CityJSON to IFC converter
# Copyright (C) 2021 Laurens J.N. Oostwegel <l.oostwegel@gmail.com>
#
# This file is part of ifccityjson.
#
# ifccityjson is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ifccityjson is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ifccityjson.  If not, see <http://www.gnu.org/licenses/>.

import argparse
from cjio import cityjson
from .cityjson2ifc import Cityjson2ifc


def cmdline():
    # Example:
    # python ifccityjson.py -i example/3DBAG_example.json -o example/output.ifc -n identificatie
    # python ifccityjson.py -i example/geometries.json -o example/geometry_output.ifc
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-i", "--input", type=str, help="input CityJSON file", required=True)
    parser.add_argument("-o", "--output", type=str, help="output IFC file. Standard is output.ifc")
    parser.add_argument("-n", "--name", type=str, help="Attribute containing the name")
    parser.add_argument("--split-lod", dest="split", action="store_true", help="Split the file in multiple LoDs")
    parser.add_argument(
        "--no-split-lod", dest="split", action="store_false", help="Do not split the file in multiple LoDs"
    )
    parser.add_argument("--lod", type=str, help="extract LOD value (example: 1.2)")
    parser.set_defaults(split=True)
    args = parser.parse_args()

    city_model = cityjson.load(args.input, transform=False)
    data = {}
    if args.name:
        data["name_attribute"] = args.name
    if args.output:
        data["file_destination"] = args.output
    if args.lod:
        data["lod"] = args.lod
    data["split"] = args.split

    converter = Cityjson2ifc()
    converter.configuration(**data)
    converter.convert(city_model)


if __name__ == "__main__":
    cmdline()
