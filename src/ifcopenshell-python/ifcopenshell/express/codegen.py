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

import itertools
import functools
from pathlib import Path


def indent(n, s):
    if isinstance(s, str):
        strs = [s]
    else:
        strs = s
    splitted = itertools.chain.from_iterable(map(functools.partial(str.split, sep="\n"), map(str, strs)))
    return "\n".join(" " * n + l for l in splitted)


class Base:
    """
    A base class for all code generation classes. Currently only working around
    some python 2/3 incompatibilities in terms of unicode file handling.
    """

    def emit(self):
        Path(self.file_name).write_text(repr(self), encoding="utf-8")
