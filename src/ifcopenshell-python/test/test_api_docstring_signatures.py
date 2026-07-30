# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Petru Conduraru <petru@bimvoice.com>
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

"""Every :param: name in ifcopenshell.api docstrings must match the real signature.

wrap_usecase() (see ifcopenshell/api/__init__.py) sets wrapper.__signature__ and
wrapper.__doc__ from the underlying usecase function, so inspect.signature() and
.__doc__ on the module-level attribute already resolve to the real function; no
inspect.unwrap()/__wrapped__ needed.

This does not catch every kind of drift (e.g. a :param: entry documenting a
parameter that is present but under the wrong type, or a missing :param: entry
altogether), only the case where a documented name is not a parameter at all.
"""

import importlib
import inspect
import pkgutil
import re

import pytest

import ifcopenshell.api

PARAM_RE = re.compile(r"^\s*:param\s+([^:]+):")


def iter_documented_api_functions():
    api_dir = ifcopenshell.api.__path__
    for module_info in sorted(pkgutil.iter_modules(api_dir), key=lambda m: m.name):
        if not module_info.ispkg:
            continue
        try:
            module = importlib.import_module(f"ifcopenshell.api.{module_info.name}")
        except ImportError:
            # e.g. sequence.recalculate_schedule requires the optional networkx
            # dependency; skip modules we cannot even import.
            continue
        submodule_dir = [module.__path__[0]] if hasattr(module, "__path__") else None
        if submodule_dir is None:
            continue
        for usecase_info in sorted(pkgutil.iter_modules(submodule_dir), key=lambda m: m.name):
            if usecase_info.ispkg:
                continue
            func = getattr(module, usecase_info.name, None)
            if not callable(func):
                continue
            doc = func.__doc__
            if not doc or ":param" not in doc:
                continue
            yield f"{module_info.name}.{usecase_info.name}", func


def documented_param_names(doc: str) -> list[str]:
    names = []
    for line in doc.split("\n"):
        match = PARAM_RE.match(line)
        if match:
            names.append(match.group(1).strip())
    return names


@pytest.mark.parametrize(
    "path,func",
    list(iter_documented_api_functions()),
    ids=lambda x: x if isinstance(x, str) else "",
)
def test_documented_params_exist_in_signature(path, func):
    try:
        signature = inspect.signature(func)
    except (TypeError, ValueError):
        pytest.skip(f"{path}: signature could not be determined")
    sig_params = {p.name for p in signature.parameters.values() if p.name != "self"}
    documented = documented_param_names(func.__doc__)
    unknown = [name for name in documented if name not in sig_params]
    assert not unknown, (
        f"{path}: docstring documents {unknown!r}, which are not parameters of the "
        f"actual signature {list(sig_params)!r}. Likely a stale :param: entry left "
        f"behind after a rename."
    )
