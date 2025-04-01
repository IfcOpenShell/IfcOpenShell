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


from __future__ import annotations
import os
import sys
import operator

from .. import ifcopenshell_wrapper
from ..file import file
from ..entity_instance import entity_instance

from . import has_occ

from typing import TypeVar, Union, Optional, Generator, Any, Literal, overload, TYPE_CHECKING, Iterable, cast

if TYPE_CHECKING:
    from OCC.Core import TopoDS

    IteratorOutput = Union["ShapeElementType", "utils.shape_tuple"]

T = TypeVar("T")
ShapeElementType = Union[
    ifcopenshell_wrapper.BRepElement, ifcopenshell_wrapper.TriangulationElement, ifcopenshell_wrapper.SerializedElement
]
ShapeType = Union[ifcopenshell_wrapper.BRep, ifcopenshell_wrapper.Triangulation, ifcopenshell_wrapper.Serialization]


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


SETTING = Literal[
    "angle-unit",
    "apply-default-materials",
    "boolean-attempt-2d",
    "building-local-placement",
    "cgal-original-edges",
    "circle-segments",
    "compute-curvature",
    "context-identifiers",
    "context-ids",
    "context-types",
    "convert-back-units",
    "debug",
    "dimensionality",
    "disable-boolean-result",
    "disable-opening-subtractions",
    "edge-arrows",
    "element-hierarchy",
    "enable-layerset-slicing",
    "force-space-transparency",
    "function-step-param",
    "function-step-type",
    "generate-uvs",
    "iterator-output",
    "keep-bounding-boxes",
    "layerset-first",
    "length-unit",
    "mesher-angular-deflection",
    "mesher-linear-deflection",
    "model-offset",
    "model-rotation",
    "no-normals",
    "no-parallel-mapping",
    "no-wire-intersection-check",
    "no-wire-intersection-tolerance",
    "precision",
    "precision-factor",
    "reorient-shells",
    "site-local-placement",
    "surface-colour",
    "triangulation-type",
    "unify-shapes",
    "use-material-names",
    "use-python-opencascade",
    "use-world-coords",
    "validate",
    "weld-vertices",
]
SERIALIZER_SETTING = Literal[
    "base-uri",
    "use-element-names",
    "use-element-guids",
    "use-element-step-ids",
    "use-element-types",
    "y-up",
    "ecef",
    "digits",
    "wkt-use-section",
]

# NOTE: hybrid-cgal-simple-opencascade is added just as an example
# It's possible to use any hybrid combination by the format below:
# "hybrid-library1-library2".
# List is updated from AbstractKernel.cpp.
GEOMETRY_LIBRARY = Literal["cgal", "cgal-simple", "opencascade", "hybrid-cgal-simple-opencascade"]


class missing_setting:
    def __repr__(self):
        return "-"


class settings_mixin:
    """
    Pythonic interface mixin to the settings modules and
    to provide an additional setting to enable pythonOCC
    when available
    """

    def __init__(self, **kwargs):
        super(settings_mixin, self).__init__()
        for k, v in kwargs.items():
            self.set(getattr(self, k), v)

    def __repr__(self):
        def safe_get(x):
            try:
                return self.get(x)
            except RuntimeError:
                return missing_setting()

        fmt_pair = lambda x: "%s = %r" % (self.rname(x), safe_get(x))
        return "%s(%s)" % (type(self).__name__, ", ".join(map(fmt_pair, self.setting_names())))

    @staticmethod
    def name(k: str) -> Union[SETTING, SERIALIZER_SETTING]:
        return k.lower().replace("_", "-")

    @staticmethod
    def rname(k: Union[SETTING, SERIALIZER_SETTING]) -> str:
        return k.upper().replace("-", "_")

    @overload
    def set(self: settings, k: SETTING, v: Any) -> None: ...
    @overload
    def set(self: serializer_settings, k: SERIALIZER_SETTING, v: Any) -> None: ...
    def set(self, k: SETTING, v: Any) -> None:
        """
        Set value of the setting named `k` to `v`.

        :raises RuntimeError: If there is no setting with name `k`.
        """
        k = self.name(k)
        if isinstance(self, settings) and k == "use-python-opencascade":
            if not has_occ:
                raise AttributeError("Python OpenCASCADE is not installed")
            if v:
                self.set_("iterator-output", ifcopenshell_wrapper.SERIALIZED)
                self.set_("use-world-coords", True)
                self.use_python_opencascade = True
        else:
            self.set_(self.name(k), v)

    @overload
    def get(self: settings, k: SETTING) -> Any: ...
    @overload
    def get(self: serializer_settings, k: SERIALIZER_SETTING) -> Any: ...
    def get(self, k: str) -> Any:
        """
        Return value of the setting named `k`.

        :raises RuntimeError: If there is no setting with name `k`.
        """
        k = self.name(k)
        if isinstance(self, settings) and k == "use-python-opencascade":
            return self.use_python_opencascade
        return self.get_(k)

    @overload
    def setting_names(self: settings) -> tuple[SETTING, ...]: ...
    @overload
    def setting_names(self: serializer_settings) -> tuple[SERIALIZER_SETTING, ...]: ...
    def setting_names(self) -> tuple[str, ...]:
        setting_names = super().setting_names()
        if isinstance(self, settings):
            setting_names += ("use-python-opencascade",)
        return setting_names

    @overload
    def __getattr__(self: settings, k: str) -> SETTING: ...
    @overload
    def __getattr__(self: serializer_settings, k: str) -> SERIALIZER_SETTING: ...
    def __getattr__(self, k: str) -> str:
        # Swig wrapper will try to access "this",
        # ensure we won't accidentally call any c-extension methods
        # like .setting_names() until wrapper is not completely initialized.
        # See #4861.
        if k == "this":
            raise AttributeError("Swig wrapper's 'this' is unset.")
        if k in map(self.rname, self.setting_names()):
            return k
        else:
            raise AttributeError("'Settings' object has no attribute '%s'" % k)

    def build_parser(self, parser) -> None:
        """
        Accepts an argparse.ArgumentParser object, enumerates the settings in this container and
        adds argument parser rules for each.
        """
        type_factories = {
            "bool": bool,
            "int": int,
            "double": float,
            "std::string": str,
            "std::set<int>": lambda s: list(map(int, s.split(";"))),
            "std::set<std::string>": lambda s: s.split(";"),
            "std::vector<double>": lambda s: list(map(float, s.split(";"))),
            "IteratorOutputOptions": int,
            "FunctionStepMethod": int,
            "OutputDimensionalityTypes": int,
            "TriangulationMethod": int,
        }
        for nm in self.setting_names():
            if nm == "use-python-opencascade":
                ty == "bool"
            else:
                ty = self.get_type(nm)
            if ty == "bool":
                group = parser.add_mutually_exclusive_group()
                group.add_argument(
                    f"--{nm}",
                    dest=nm.replace("-", "_"),
                    action="store_true",
                )
                group.add_argument(
                    f"--no-{nm}",
                    dest=nm.replace("-", "_"),
                    action="store_false",
                )
                parser.set_defaults(**{nm.replace("-", "_"): None})
            else:
                parser.add_argument(f"--{nm}", dest=nm.replace("-", "_"), type=type_factories[ty])

    def apply_namespace(self, namespace) -> None:
        """
        Accepts an argparse.Namespace object, enumerates over the values in this namespace and
        writes them to the settings when available
        """
        names = set(self.setting_names())
        for k, v in namespace._get_kwargs():
            if k.replace("_", "-") in names and v is not None:
                self.set(k.replace("_", "-"), v)


class serializer_settings(settings_mixin, ifcopenshell_wrapper.SerializerSettings):
    pass


class settings(settings_mixin, ifcopenshell_wrapper.Settings):
    use_python_opencascade = False


class iterator(ifcopenshell_wrapper.Iterator):
    def __init__(
        self,
        settings: settings,
        file_or_filename: Union[file, str],
        num_threads: int = 1,
        include: Optional[Union[list[entity_instance], list[str]]] = None,
        exclude: Optional[Union[list[entity_instance], list[str]]] = None,
        geometry_library: GEOMETRY_LIBRARY = "opencascade",
    ):
        self.settings = settings
        if isinstance(file_or_filename, file):
            file_or_filename = file_or_filename.wrapped_data
        else:
            # Makes sure people are able to use python's platform agnostic paths
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
                include_or_exclude = cast(set[entity_instance], include_or_exclude)

                if not all(inst.is_a("IfcProduct") for inst in include_or_exclude):
                    raise ValueError("include and exclude need to be an aggregate of IfcProduct")

                initializer = ifcopenshell_wrapper.construct_iterator_with_include_exclude_id

                include_or_exclude = [i.id() for i in include_or_exclude]
            else:
                initializer = ifcopenshell_wrapper.construct_iterator_with_include_exclude

            self.this = initializer(
                geometry_library, self.settings, file_or_filename, include_or_exclude, include is not None, num_threads
            )
        else:
            ifcopenshell_wrapper.Iterator.__init__(self, geometry_library, settings, file_or_filename, num_threads)

    if has_occ:

        def get(self):
            return wrap_shape_creation(self.settings, ifcopenshell_wrapper.Iterator.get(self))

    def __iter__(self) -> Generator[IteratorOutput, None, None]:
        if self.initialize():
            while True:
                yield self.get()
                if not self.next():
                    break


class tree(ifcopenshell_wrapper.tree):
    def __init__(self, file: Optional[file] = None, settings: Optional[settings] = None):
        args = [self]
        if file is not None:
            args.append(file.wrapped_data)
            if settings is not None:
                args.append(settings)
        ifcopenshell_wrapper.tree.__init__(*args)

    def add_file(self, file: file, settings: settings) -> None:
        ifcopenshell_wrapper.tree.add_file(self, file.wrapped_data, settings)

    def add_iterator(self, iterator: iterator) -> None:
        ifcopenshell_wrapper.tree.add_file(self, iterator)

    def select(
        self,
        value: Union[
            entity_instance, ifcopenshell_wrapper.BRepElement, tuple[float, float, float], "TopoDS.TopoDS_Shape"
        ],
        **kwargs,
    ) -> list[entity_instance]:
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

    def select_box(self, value, **kwargs) -> list[entity_instance]:
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

    def clash_intersection_many(
        self,
        set_a: Iterable[entity_instance],
        set_b: Iterable[entity_instance],
        tolerance: float = 0.002,
        check_all: bool = True,
    ):
        args = [self, [e.wrapped_data for e in set_a], [e.wrapped_data for e in set_b], tolerance, check_all]
        return ifcopenshell_wrapper.tree.clash_intersection_many(*args)

    def clash_collision_many(
        self, set_a: Iterable[entity_instance], set_b: Iterable[entity_instance], allow_touching=False
    ):
        args = [self, [e.wrapped_data for e in set_a], [e.wrapped_data for e in set_b], allow_touching]
        return ifcopenshell_wrapper.tree.clash_collision_many(*args)

    def clash_clearance_many(
        self,
        set_a: Iterable[entity_instance],
        set_b: Iterable[entity_instance],
        clearance: float = 0.05,
        check_all: bool = False,
    ):
        args = [self, [e.wrapped_data for e in set_a], [e.wrapped_data for e in set_b], clearance, check_all]
        return ifcopenshell_wrapper.tree.clash_clearance_many(*args)


def create_shape(
    settings: settings,
    inst: entity_instance,
    repr: Optional[entity_instance] = None,
    geometry_library: GEOMETRY_LIBRARY = "opencascade",
) -> Union[ShapeType, ShapeElementType, ifcopenshell_wrapper.Transformation, utils.shape_tuple, TopoDS.TopoDS_Shape]:
    """
    Return a geometric representation from STEP-based IFCREPRESENTATIONSHAPE
    or
    Return an OpenCASCADE BRep if 'use-python-opencascade' is True

    Note that in Python, you must store a reference to the element returned by this function to prevent garbage
    collection when you access its children. See #1124.

    :raises RuntimeError: If failed to process shape. You can turn detailed logging to get more details.

    :return:
        - `inst` is IfcProduct and `repr` provided / None -> ShapeElementType\n
        - `inst` is IfcRepresentation and `repr` is None -> ShapeType\n
        - `inst` is IfcRepresentationItem and `repr` is None -> ShapeType\n
        - `inst` is IfcProfileDef and `repr` is None -> ShapeType\n
        - `inst` is IfcPlacement / IfcObjectPlacement -> Transformation\n
        - `inst` is IfcTypeProduct and `repr` is None -> None\n
        - `inst` is IfcTypeProduct and `repr` is provided -> RuntimeError
        (for IfcTypeProducts provide just IfcRepresentation as `inst`).\n

        If 'use-python-opencascade' is enabled in settings then\n
        - instead of ShapeElementType it returns shape_tuple, \n
        - instead of ShapeType it returns TopoDS.TopoDS_Shape.

    Example:

    .. code:: python

        settings = ifcopenshell.geom.settings()
        settings.set("use-python-opencascade", True)

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
        ifcopenshell_wrapper.create_shape(
            settings, inst.wrapped_data, repr.wrapped_data if repr is not None else None, geometry_library
        ),
    )


@overload
def consume_iterator(it: iterator, with_progress: Literal[False] = False) -> Generator[IteratorOutput, None, None]: ...
@overload
def consume_iterator(
    it: iterator, with_progress: Literal[True]
) -> Generator[tuple[int, IteratorOutput], None, None]: ...
@overload
def consume_iterator(
    it: iterator, with_progress: bool
) -> Generator[Union[IteratorOutput, tuple[int, IteratorOutput]], None, None]: ...
def consume_iterator(
    it: iterator, with_progress: bool = False
) -> Generator[Union[IteratorOutput, tuple[int, IteratorOutput]], None, None]:
    if it.initialize():
        while True:
            if with_progress:
                yield it.progress(), it.get()
            else:
                yield it.get()
            if not it.next():
                break


# Overloads need to cover different return types
# based on `with_progress` argument.
@overload
def iterate(
    settings: settings,
    file_or_filename: Union[file, str],
    num_threads: int = 1,
    include: Optional[Union[list[entity_instance], list[str]]] = None,
    exclude: Optional[Union[list[entity_instance], list[str]]] = None,
    *,
    with_progress: Literal[False] = False,
    cache: Optional[str] = None,
    serializer_settings: Optional[serializer_settings] = None,
    geometry_library: GEOMETRY_LIBRARY = "opencascade",
) -> Generator[IteratorOutput, None, None]: ...
@overload
def iterate(
    settings: settings,
    file_or_filename: Union[file, str],
    num_threads: int = 1,
    include: Optional[Union[list[entity_instance], list[str]]] = None,
    exclude: Optional[Union[list[entity_instance], list[str]]] = None,
    *,
    with_progress: Literal[True] = True,
    cache: Optional[str] = None,
    serializer_settings: Optional[serializer_settings] = None,
    geometry_library: GEOMETRY_LIBRARY = "opencascade",
) -> Generator[tuple[int, IteratorOutput], None, None]: ...
@overload
def iterate(
    settings: settings,
    file_or_filename: Union[file, str],
    num_threads: int = 1,
    include: Optional[Union[list[entity_instance], list[str]]] = None,
    exclude: Optional[Union[list[entity_instance], list[str]]] = None,
    *,
    with_progress: bool = False,
    cache: Optional[str] = None,
    serializer_settings: Optional[serializer_settings] = None,
    geometry_library: GEOMETRY_LIBRARY = "opencascade",
) -> Generator[Union[IteratorOutput, tuple[int, IteratorOutput]], None, None]: ...
def iterate(
    settings: settings,
    file_or_filename: Union[file, str],
    num_threads: int = 1,
    include: Optional[Union[list[entity_instance], list[str]]] = None,
    exclude: Optional[Union[list[entity_instance], list[str]]] = None,
    *,
    with_progress: bool = False,
    cache: Optional[str] = None,
    serializer_settings: Optional[serializer_settings] = None,
    geometry_library: GEOMETRY_LIBRARY = "opencascade",
) -> Generator[Union[IteratorOutput, tuple[int, IteratorOutput]], None, None]:
    """Get a geometry iterator for the provided file.

    :param cache: .h5 cache filepath (might not exist, will be created).
    :param serializer_settings: Settings for cache serializer. Required if `cache` is provided.
    """
    it = iterator(settings, file_or_filename, num_threads, include, exclude, geometry_library)
    if cache:
        assert serializer_settings, "`serializer_settings` argument is not optional if `cache` is provided."
        hdf5_cache = serializers.hdf5(cache, settings, serializer_settings)
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


def transform_string(v: Union[str, serializers.buffer]) -> serializers.buffer:
    if isinstance(v, str):
        return ifcopenshell_wrapper.buffer(v)
    return v


class serializers:
    # Python does not have automatic casts. The C++ serializers accept a stream_or_filename
    # which in C++ can be automatically constructed from a filename string. In Python we
    # have to implement this cast/construction explicitly by transform_string.
    @staticmethod
    def obj(
        out_filename: Union[str, serializers.buffer],
        mtl_filename: Union[str, serializers.buffer],
        geometry_settings: settings,
        settings: serializer_settings,
    ) -> ifcopenshell_wrapper.WaveFrontOBJSerializer:
        out_filename = transform_string(out_filename)
        mtl_filename = transform_string(mtl_filename)
        return ifcopenshell_wrapper.WaveFrontOBJSerializer(out_filename, mtl_filename, geometry_settings, settings)

    @staticmethod
    def svg(
        out_filename: Union[str, serializers.buffer], geometry_settings: settings, settings: serializer_settings
    ) -> ifcopenshell_wrapper.SvgSerializer:
        out_filename = transform_string(out_filename)
        return ifcopenshell_wrapper.SvgSerializer(out_filename, geometry_settings, settings)

    # Hdf- Xml- and glTF- serializers don't support writing to a buffer, only to filename
    # so no wrap_buffer_creation() for these serializers
    xml = ifcopenshell_wrapper.XmlSerializer
    buffer = ifcopenshell_wrapper.buffer
    # gltf and hdf5 availability depend on IfcOpenShell configuration settings
    try:
        gltf = ifcopenshell_wrapper.GltfSerializer
    except:
        pass
    try:
        hdf5 = ifcopenshell_wrapper.HdfSerializer
    except:
        pass
    try:
        collada = ifcopenshell_wrapper.ColladaSerializer
    except:
        pass
    # ttl is always available since it doesn't depend on any C++ libraries,
    # just people might be using an outdated binary
    if hasattr(ifcopenshell_wrapper, "TtlWktSerializer"):

        @staticmethod
        def ttl(
            out_filename: Union[str, serializers.buffer], geometry_settings: settings, settings: serializer_settings
        ) -> ifcopenshell_wrapper.SvgSerializer:
            out_filename = transform_string(out_filename)
            return ifcopenshell_wrapper.TtlWktSerializer(out_filename, geometry_settings, settings)

    @classmethod
    def guess_from_extension(cls, filepath: str):
        ext = filepath.split(".")[-1]
        mapping = {
            "glb": "gltf",
            "hdf": "hdf5",
            "h5": "hdf5",
            "hdf5": "hdf5",
            "obj": "obj",
            "svg": "svg",
            "ttl": "ttl",
            "xml": "xml",
            "dae": "collada",
        }
        serializer_name = mapping.get(ext)
        if not serializer_name:
            raise ValueError(f"No serializer available for .{ext} file")
        return getattr(cls, serializer_name)
