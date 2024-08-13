# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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

import os
import ifcfm
import importlib


def refresh():
    FMData.is_loaded = False


class FMData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {}
        cls.data["engine"] = cls.engine()

    @classmethod
    def engine(cls):
        results = []
        fm_dir = os.path.dirname(ifcfm.__file__)
        for f in os.listdir(fm_dir):
            if f.endswith(".py") and not f.startswith("_"):
                preset = os.path.splitext(f)[0]
                module = importlib.import_module(f"ifcfm.{preset}")
                config = getattr(module, "config")
                results.append((preset, config["name"], config["description"]))
        return results
