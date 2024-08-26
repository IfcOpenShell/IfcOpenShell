# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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
import bpy
import bcf
import bcf.bcfxml
import bcf.v2.bcfxml
from typing import Union


class BcfStore:
    bcfxml: Union[bcf.bcfxml.BcfXml, None] = None

    @classmethod
    def get_bcfxml(cls) -> Union[bcf.bcfxml.BcfXml, None]:
        if not cls.bcfxml:
            bcf_filepath = bpy.context.scene.BCFProperties.bcf_file
            if not os.path.isabs(bcf_filepath):
                bcf_filepath = os.path.abspath(os.path.join(bpy.path.abspath("//"), bcf_filepath))
            if bcf_filepath:
                try:
                    cls.bcfxml = bcf.bcfxml.load(bcf_filepath)
                except:
                    # there will be a plenty of "Permission denied" errors
                    # as many poll() methods will try to access the bcfxml simultaneously
                    # the first time it's loaded
                    pass
        return cls.bcfxml

    @classmethod
    def set(cls, bcfxml: Union[bcf.bcfxml.BcfXml, None], filepath: str) -> None:
        cls.bcfxml = bcfxml
        props = bpy.context.scene.BCFProperties
        props.bcf_file = filepath

        # Set bcf_version prop on load.
        if filepath or bcfxml:
            bcfxml = cls.get_bcfxml()
            assert bcfxml
            bcf_v2 = (bcfxml.version.version_id or "").startswith("2")
            props.bcf_version = "2" if bcf_v2 else "3"

    @classmethod
    def set_by_filepath(cls, filepath: str) -> None:
        cls.set(None, filepath)

    @classmethod
    def unload_bcfxml(cls) -> None:
        cls.set(None, "")
