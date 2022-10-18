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


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import operator

from .. import ifcopenshell_wrapper
from ..file import file
from ..entity_instance import entity_instance

from . import has_occ


def wrap_shape_creation(settings, shape):
    return shape


if has_occ:
    from . import occ_utils as utils

    try:
        from OCC.Core import TopoDS
    except ImportError:
        from OCC import TopoDS

    def wrap_shape_creation(settings, shape):
        if getattr(settings, "use_python_opencascade", False):
            return utils.create_shape_from_serialization(shape)
        else:
            return shape


# Subclass the settings module to provide an additional
# setting to enable pythonOCC when available

# nb: we just subclass serializer settings, so in python
# we do not differentiate between the two setting types


class settings(ifcopenshell_wrapper.SerializerSettings):
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
                ifcopenshell_wrapper.SerializerSettings.set(self, *args)


# Make sure people are able to use python's platform agnostic paths
class iterator(ifcopenshell_wrapper.Iterator):
    def __init__(self, settings, file_or_filename, num_threads=1, include=None, exclude=None):
        self.settings = settings
        if isinstance(file_or_filename, file):
            file_or_filename = file_or_filename.wrapped_data
        else:
            file_or_filename = os.path.abspath(file_or_filename)

        if include is not None and exclude is not None:
            raise ValueError("include and exclude cannot be specified simultaneously")

        if include is not None or exclude is not None:
            # Couldn't get the typemaps properly applied using %extend so we
            # replicate the SWIG-generated __init__ call on the output of a
            # free function.
            # @todo verify this works with SWIG 4

            include_or_exclude = include if exclude is None else exclude
            include_or_exclude_type = set(x.__class__.__name__ for x in include_or_exclude)

            if include_or_exclude_type == {"entity_instance"}:
                if not all(inst.is_a("IfcProduct") for inst in include_or_exclude):
                    raise ValueError("include and exclude need to be an aggregate of IfcProduct")

                initializer = ifcopenshell_wrapper.construct_iterator_with_include_exclude_id

                include_or_exclude = [i.id() for i in include_or_exclude]
            else:
                initializer = ifcopenshell_wrapper.construct_iterator_with_include_exclude

            self.this = initializer(
                self.settings, file_or_filename, include_or_exclude, include is not None, num_threads
            )
        else:
            ifcopenshell_wrapper.Iterator.__init__(self, settings, file_or_filename, num_threads)

    if has_occ:

        def get(self):
            return wrap_shape_creation(self.settings, ifcopenshell_wrapper.Iterator.get(self))

    def __iter__(self):
        if self.initialize():
            while True:
                yield self.get()
                if not self.next():
                    break


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

    def add_iterator(self, iterator):
        ifcopenshell_wrapper.tree.add_file(self, iterator)

    def select(self, value, **kwargs):
        def unwrap(value):
            if isinstance(value, entity_instance):
                return value.wrapped_data
            elif all(map(lambda v: hasattr(value, v), "XYZ")):
                return value.X(), value.Y(), value.Z()
            return value

        args = [self, unwrap(value)]
        if isinstance(value, (entity_instance, ifcopenshell_wrapper.BRepElement)):
            args.append(kwargs.get("completely_within", False))
            if "extend" in kwargs:
                args.append(kwargs["extend"])
        elif isinstance(value, (list, tuple)) and len(value) == 3 and set(map(type, value)) == {float}:
            if "extend" in kwargs:
                args.append(kwargs["extend"])
        elif has_occ:
            if isinstance(value, TopoDS.TopoDS_Shape):
                args[1] = utils.serialize_shape(value)
                args.append(kwargs.get("completely_within", False))
                if "extend" in kwargs:
                    args.append(kwargs["extend"])
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
            args.append(kwargs.get("extend", -1.0e-5))
        return [entity_instance(e) for e in ifcopenshell_wrapper.tree.select_box(*args)]


def create_shape(settings, inst, repr=None):
    """
    Return a geometric representation from STEP-based IFCREPRESENTATIONSHAPE
    or
    Return an OpenCASCADE BRep if settings.USE_PYTHON_OPENCASCADE == True

    Note that in Python, you must store a reference to the element returned by this function to prevent garbage
    collection when you access its children. See #1124.

    example:

    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_PYTHON_OPENCASCADE, True)

    ifc_file = ifcopenshell.open(file_path)
    products = ifc_file.by_type("IfcProduct")

    for i, product in enumerate(products):
        if product.Representation is not None:
            try:
                created_shape = geom.create_shape(settings, inst=product)
                shape = created_shape.geometry # see #1124
                shape_gpXYZ = shape.Location().Transformation().TranslationPart() # These are methods of the TopoDS_Shape class from pythonOCC
                print(shape_gpXYZ.X(), shape_gpXYZ.Y(), shape_gpXYZ.Z()) # These are methods of the gpXYZ class from pythonOCC
            except:
                print("Shape creation failed")
    """
    return wrap_shape_creation(
        settings,
        ifcopenshell_wrapper.create_shape(settings, inst.wrapped_data, repr.wrapped_data if repr is not None else None),
    )


def consume_iterator(it, with_progress=False):
    if it.initialize():
        while True:
            if with_progress:
                yield it.progress(), it.get()
            else:
                yield it.get()
            if not it.next():
                break


def iterate(settings, file_or_filename, num_threads=1, include=None, exclude=None, with_progress=False, cache=None):
    it = iterator(settings, file_or_filename, num_threads, include, exclude)
    if cache:
        hdf5_cache = serializers.hdf5(cache, settings)
        it.set_cache(hdf5_cache)
    yield from consume_iterator(it, with_progress=with_progress)


def make_shape_function(fn):
    def entity_instance_or_none(e):
        return None if e is None else entity_instance(e)

    if has_occ:

        def _(schema, string_or_shape, *args):
            if isinstance(string_or_shape, TopoDS.TopoDS_Shape):
                string_or_shape = utils.serialize_shape(string_or_shape)
            return entity_instance_or_none(fn(schema, string_or_shape, *args))

    else:

        def _(schema, string, *args):
            return entity_instance_or_none(fn(schema, string, *args))

    return _


serialise = make_shape_function(ifcopenshell_wrapper.serialise)
tesselate = make_shape_function(ifcopenshell_wrapper.tesselate)


def wrap_buffer_creation(fn):
    """
    Python does not have automatic casts. The C++ serializers accept a stream_or_filename
    which in C++ can be automatically constructed from a filename string. In Python we
    have to implement this cast/construction explicitly.
    """

    def transform_string(v):
        if isinstance(v, str):
            return ifcopenshell_wrapper.buffer(v)
        else:
            return v

    def inner(*args):
        return fn(*map(transform_string, args))

    return inner


# Hdf- Xml- and glTF- serializers don't support writing to a buffer, only to filename
# so no wrap_buffer_creation() for these serializers
serializer_dict = {}
serializer_dict["obj"] = wrap_buffer_creation(ifcopenshell_wrapper.WaveFrontOBJSerializer)
serializer_dict["svg"] = wrap_buffer_creation(ifcopenshell_wrapper.SvgSerializer)
serializer_dict["xml"] = ifcopenshell_wrapper.XmlSerializer
serializer_dict["buffer"] = ifcopenshell_wrapper.buffer

# gltf and hdf5 availability depend on IfcOpenShell configuration settings
try:
    serializer_dict["gltf"] = ifcopenshell_wrapper.GltfSerializer
except: pass

try:
    serializer_dict["hdf5"] = ifcopenshell_wrapper.HdfSerializer
except:
    pass

serializers = type("serializers", (), serializer_dict)
