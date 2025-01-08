# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import ifcopenshell
import ifcpatch
import bonsai.core.tool
from typing import Any


class Patch(bonsai.core.tool.Patch):
    @classmethod
    def run_migrate_patch(cls, infile: str, outfile: str, schema: str) -> None:
        output = ifcpatch.execute(
            {"input": infile, "file": ifcopenshell.open(infile), "recipe": "Migrate", "arguments": [schema]}
        )
        ifcpatch.write(output, outfile)

    @classmethod
    def is_filepath_argument(cls, recipe: str, arg_name: str) -> bool:
        # TODO: Temporary hack to identify filepath arguments.
        # Should mark them as such in the patches documentation
        # and process it later.
        return recipe == "SplitByBuildingStorey" and arg_name == "output_dir"

    @classmethod
    def does_patch_has_output(cls, recipe: str) -> bool:
        return recipe != "SplitByBuildingStorey"

    @classmethod
    def post_process_patch_arguments(cls, recipe: str, args: list[Any]) -> list[Any]:
        if recipe == "ExtractElements":
            query = args[0]
            assert isinstance(query, str)
            if "bpy.data.texts" in query:
                text_name = query.split("bpy.data.texts")[1][2:-2]
                args[0] = bpy.data.texts[text_name].as_string()
        return args
