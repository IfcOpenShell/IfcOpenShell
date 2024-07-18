"""
BCF - BCF Python library
Copyright (C) 2021 Prabhat Singh <singh01prabhat@gmail.com>
Copyright (C) 2022 Andrea Ghensi <andrea.ghensi@gmail.com>

This file is part of BCF.

BCF is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

BCF is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with BCF.  If not, see <http://www.gnu.org/licenses/>.
"""
import zipfile
from pathlib import Path
from typing import Optional, Union

from bcf.v2.bcfxml import BcfXml as BcfXml2
from bcf.v2.model import Version as Version2
from bcf.v3.bcfxml import BcfXml as BcfXml3
from bcf.v3.model import Version as Version3
from bcf.xml_parser import AbstractXmlParserSerializer, XmlParserSerializer


def load(
    filepath: Path, xml_handler: Optional[AbstractXmlParserSerializer] = None
) -> Optional[Union[BcfXml2, BcfXml3]]:
    """
    Load a BCF file.

    Args:
        filepath: The path to the BCF file.

    Returns:
        The loaded BCF file.

    Raises:
        ValueError: If the BCF version is not supported.
    """
    xml_handler = xml_handler or XmlParserSerializer()
    version_id = _get_version(filepath, xml_handler)
    if version_id in {"2.1", "2.0"}:
        return BcfXml2.load(filepath, xml_handler)
    if version_id == "3.0":
        return BcfXml3.load(filepath, xml_handler)
    raise ValueError(f"Version {version_id} not supported.")


def _get_version(filepath: Union[str, Path], xml_handler: Optional[AbstractXmlParserSerializer] = None) -> str:
    """
    Returns the version of the BCF file.

    Args:
        filepath: The path to the BCF file.
        xml_handler: The XML handler. If none is given, XmlParserSerializer is used.

    Returns:
        The version of the BCF file.
    """
    xml_handler = xml_handler or XmlParserSerializer()
    with zipfile.ZipFile(filepath) as bcf_zip:
        try:
            version = xml_handler.parse(bcf_zip.read("bcf.version"), Version3)
        except:
            version = xml_handler.parse(bcf_zip.read("bcf.version"), Version2)
        return version.version_id
