# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

"""
Reads and writes encoded GlobalIds.

IFC entities may be identified using a unique ID (called a UUID or GUID).
This 128-bit label is often represented in the form
```
xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.
```
However, in IFC, it is also usually stored as a
22 character base 64 encoded string.
This module lets you convert between these representations and generate new UUIDs.

NOTE: The Ifc convention for Base64 encoding differs from the standard.

The "digits" of a standard Base64 encoding are as follows:
```
ABC...XYZ abc...XYZ 012...89 +/
```
(see <https://www.rfc-editor.org/rfc/rfc4648.txt>,
<https://base64.guru/learn/base64-characters>),
whereas the Ifc convention is
```
012...89 ABC...XYZ abc...XYZ _$
```
cf. <https://technical.buildingsmart.org/resources/ifcimplementationguidance/ifc-guid>.
"""

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from base64 import b64encode
from base64 import b64decode
from uuid import uuid4
import re
import string

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "compress",
    "expand",
    "new",
    "split",
]

# ----------------------------------------------------------------
# LOCAL CONSTANTS
# ----------------------------------------------------------------

# standard convention
_CHARS64_STD = string.ascii_uppercase + string.ascii_lowercase + string.digits + "+/"

# ifc convention
_CHARS64_IFC = string.digits + string.ascii_uppercase + string.ascii_lowercase + "_$"

# translators
_TRANS_IFC_TO_STD = str.maketrans(_CHARS64_IFC, _CHARS64_STD)
_TRANS_STD_TO_IFC = str.maketrans(_CHARS64_STD, _CHARS64_IFC)

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def compress(uuid: str, /) -> str:
    """
    Converts a hex-encoded UUID to a base64-encoded GUID in IFC-format.

    See <https://technical.buildingsmart.org/resources/ifcimplementationguidance/ifc-guid>
    """
    # remove possible separators
    uuid = uuid.lower()
    uuid = re.sub(pattern=r"\W", repl="", string=uuid)

    # pad with hex "zeroes"
    uuid = "0000" + uuid

    # convert to standard base 64
    uuid_bytes = bytes.fromhex(uuid)
    guid = b64encode(uuid_bytes).decode()

    # remove result of padding
    guid = guid[2:]

    # translate from standard-convention to ifc-convention
    guid = guid.translate(_TRANS_STD_TO_IFC)

    return guid


def expand(guid: str, /) -> str:
    """
    Converts a base64-encoded GUID in IFC-format to a hex-encoded UUID.

    See <https://technical.buildingsmart.org/resources/ifcimplementationguidance/ifc-guid>
    """
    # translate from ifc-convention to standard-convention
    guid = guid.translate(_TRANS_IFC_TO_STD)

    # pad with base64 "zeroes"
    guid = "AA" + guid

    # convert to hex
    uuid = b64decode(guid).hex()

    # remove result of padding
    uuid = uuid[4:]

    return uuid


def split(uuid: str, /) -> str:
    """
    Formats a UUID as
    ```
    xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    ```
    """
    return "-".join(
        [
            uuid[:8],
            uuid[8:12],
            uuid[12:16],
            uuid[16:20],
            uuid[20:],
        ]
    )


def new() -> str:
    """
    Generates a random UUID and compresses it to a Base 64 IFC GUID.
    """
    uuid = uuid4().hex
    guid = compress(uuid)
    return guid
