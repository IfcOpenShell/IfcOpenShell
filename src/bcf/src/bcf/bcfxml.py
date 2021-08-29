# BCF - BCF Python library
# Copyright (C) 2021 Prabhat Singh <singh01prabhat@gmail.com>
#
# This file is part of BCF.
#
# BCF is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BCF is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with BCF.  If not, see <http://www.gnu.org/licenses/>.


import os.path
import zipfile
import tempfile
from xml.dom import minidom


def load(filepath):
    filepath = extract_project(filepath)
    if os.path.isfile(os.path.join(filepath, "bcf.version")):
        version_path = os.path.join(filepath, "bcf.version")
        version_id = get_version(version_path)
        # TODO: we actually coded it for 2.1, let's check the difference between 2.0 and 2.1
        if version_id == "2.1" or version_id == "2.0":
            from bcf.v2.bcfxml import BcfXml

            bcfxml = BcfXml()
            bcfxml.filepath = filepath
            return bcfxml
        elif version_id == "3.0":
            from bcf.v3.bcfxml import BcfXml

            bcfxml = BcfXml()
            bcfxml.filepath = filepath
            return bcfxml
        else:
            raise Exception(f"Version {version_id} not supported.")


def get_version(version_path):
    xmlparse = minidom.parse(version_path)
    version_el = xmlparse.getElementsByTagName("Version")[0]
    version = version_el.getAttribute("VersionId")
    return version


def extract_project(filepath):
    if not filepath:
        return
    zip_file = zipfile.ZipFile(filepath)
    filepath = tempfile.mkdtemp()
    zip_file.extractall(filepath)
    return filepath
