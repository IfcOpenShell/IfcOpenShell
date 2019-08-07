###############################################################################
#                                                                             #
# This file is part of IfcOpenShell.                                          #
#                                                                             #
# IfcOpenShell is free software: you can redistribute it and/or modify        #
# it under the terms of the Lesser GNU General Public License as published by #
# the Free Software Foundation, either version 3.0 of the License, or         #
# (at your option) any later version.                                         #
#                                                                             #
# IfcOpenShell is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                #
# Lesser GNU General Public License for more details.                         #
#                                                                             #
# You should have received a copy of the Lesser GNU General Public License    #
# along with this program. If not, see <http://www.gnu.org/licenses/>.        #
#                                                                             #
###############################################################################

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys

from .. import ifcopenshell_wrapper
from ..file import file
from ..entity_instance import entity_instance


def has_occ():
    try:
        import OCC.BRepTools
    except BaseException:
        return False
    return True


has_occ = has_occ()


def wrap_shape_creation(settings, shape):
    return shape


if has_occ:
    from . import occ_utils as utils

    def wrap_shape_creation(settings, shape):
        if getattr(settings, 'use_python_opencascade', False):
            return utils.create_shape_from_serialization(shape)
        else:
            return shape


# Subclass the settings module to provide an additional
# setting to enable pythonOCC when available


class settings(ifcopenshell_wrapper.settings):
    if has_occ:
        USE_PYTHON_OPENCASCADE = -1

        def set(self, *args):
            setting, value = args
            if setting == settings.USE_PYTHON_OPENCASCADE:
                self.set(settings.USE_BREP_DATA, value)
                self.set(settings.USE_WORLD_COORDS, value)
                self.set(settings.DISABLE_TRIANGULATION, value)
                self.use_python_opencascade = value
            else:
                ifcopenshell_wrapper.settings.set(self, *args)


# Assert templated precision to match Python's internal float type
assert ifcopenshell_wrapper.iterator_double_precision.mantissa_size() == sys.float_info.mant_dig
_iterator = ifcopenshell_wrapper.iterator_double_precision

# Make sure people are able to use python's platform agnostic paths
class iterator(_iterator):
    def __init__(self, settings, file_or_filename, num_threads = 1):
        self.settings = settings
        if isinstance(file_or_filename, file):
            file_or_filename = file_or_filename.wrapped_data
        else:
            file_or_filename = os.path.abspath(file_or_filename)
        _iterator.__init__(self, settings, file_or_filename, num_threads)

    if has_occ:
        def get(self):
            return wrap_shape_creation(self.settings, _iterator.get(self))
            
    def __iter__(self):
        if self.initialize():
            while True:
                yield self.get()
                if not self.next(): break

class tree(ifcopenshell_wrapper.tree):

    def __init__(self, file=None, settings=None):
        args = [self]
        if file is not None:
            args.append(file.wrapped_data)
            if settings is not None:
                args.append(settings)
        ifcopenshell_wrapper.tree.__init__(*args)

    def add_file(self, file, settings):
        ifcopenshell_wrapper.tree.add_file(self, file.wrapped_data, settings)

    def select(self, value, **kwargs):
        def unwrap(value):
            if isinstance(value, entity_instance):
                return value.wrapped_data
            elif all(map(lambda v: hasattr(value, v), "XYZ")):
                return value.X(), value.Y(), value.Z()
            return value

        args = [self, unwrap(value)]
        if isinstance(value, entity_instance):
            args.append(kwargs.get("completely_within", False))
        elif has_occ:
            import OCC.TopoDS
            if isinstance(value, OCC.TopoDS.TopoDS_Shape):
                args[1] = utils.serialize_shape(value)
        return [entity_instance(e) for e in ifcopenshell_wrapper.tree.select(*args)]

    def select_box(self, value, **kwargs):
        def unwrap(value):
            if isinstance(value, entity_instance):
                return value.wrapped_data
            elif hasattr(value, "Get"):
                return value.Get()[:3], value.Get()[3:]
            return value

        args = [self, unwrap(value)]
        if "extend" in kwargs or "completely_within" in kwargs:
            args.append(kwargs.get("completely_within", False))
        if "extend" in kwargs:
            args.append(kwargs.get("extend", -1.e-5))
        return [entity_instance(e) for e in ifcopenshell_wrapper.tree.select_box(*args)]


def create_shape(settings, inst, repr=None):
    """
    Return a geometric representation from STEP-based IFCREPRESENTATIONSHAPE
    or
    Return an OpenCASCADE BRep if settings.USE_PYTHON_OPENCASCADE == True

    example:

    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_PYTHON_OPENCASCADE, True)

    ifc_file = ifcopenshell.open(file_path)
    products = ifc_file.by_type("IfcProduct")

    for i, product in enumerate(products):
        if product.Representation is not None:
            try:
                shape = geom.create_shape(settings, inst=product).geometry
                shape_gpXYZ = shape.Location().Transformation().TranslationPart() # These are methods of the TopoDS_Shape class from pythonOCC
                print(shape_gpXYZ.X(), shape_gpXYZ.Y(), shape_gpXYZ.Z()) # These are methods of the gpXYZ class from pythonOCC
    """
    return wrap_shape_creation(
        settings,
        ifcopenshell_wrapper.create_shape(
            settings,
            inst.wrapped_data,
            repr.wrapped_data if repr is not None else None
        ))


def iterate(settings, filename):
    it = iterator(settings, filename)
    if it.initialize():
        while True:
            yield it.get()
            if not it.next():
                break


def make_shape_function(fn):
    def entity_instance_or_none(e):
        return None if e is None else entity_instance(e)

    if has_occ:
        import OCC.TopoDS

        def _(schema, string_or_shape, *args):
            if isinstance(string_or_shape, OCC.TopoDS.TopoDS_Shape):
                string_or_shape = utils.serialize_shape(string_or_shape)
            return entity_instance_or_none(fn(schema, string_or_shape, *args))
    else:
        def _(schema, string, *args):
            return entity_instance_or_none(fn(schema, string, *args))
    return _


serialise = make_shape_function(ifcopenshell_wrapper.serialise)
tesselate = make_shape_function(ifcopenshell_wrapper.tesselate)
