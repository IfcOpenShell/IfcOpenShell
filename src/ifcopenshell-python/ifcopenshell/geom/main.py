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

from collections.abc import Generator, Iterable
from os import PathLike, fspath
from typing import TYPE_CHECKING, Any, Literal, Optional, TypeVar, Union, cast, overload

import ifcopenshell

from .. import entity_instance, file, ifcopenshell_wrapper, open
from . import has_occ

if TYPE_CHECKING:
    from OCC.Core import TopoDS  # pyright: ignore[reportMissingImports]  # ty:ignore[unresolved-import]

    IteratorOutput = Union["ShapeElementType", "utils.shape_tuple"]

T = TypeVar("T")
ShapeElementType = Union[
    ifcopenshell_wrapper.native_element,
    ifcopenshell_wrapper.triangulation_element,
    ifcopenshell_wrapper.serialized_element,
]
ShapeType = Union[ifcopenshell_wrapper.native, ifcopenshell_wrapper.triangulation, ifcopenshell_wrapper.serialization]


def wrap_shape_creation(settings, shape):
    return shape


if has_occ:
    from . import occ_utils as utils

    try:
        from OCC.Core import TopoDS  # pyright: ignore[reportMissingImports]  # ty:ignore[unresolved-import]
    except ImportError:
        from OCC import TopoDS  # pyright: ignore[reportMissingImports]  # ty:ignore[unresolved-import]

    def wrap_shape_creation(settings: settings, shape: ifcopenshell_wrapper.element):
        if getattr(settings, "use_python_opencascade", False):
            return utils.create_shape_from_serialization(shape)
        else:
            return shape


SETTING = Literal[
    "angle-unit",
    "apply-default-materials",
    "apply-offset",
    "auto-elevation",
    "auto-section",
    "base-uri",
    "boolean-attempt-2d",
    "building-local-placement",
    "bounds",
    "cache-shapes",
    "cgal-original-edges",
    "cgal-smooth-angle-degrees",
    "circle-segments",
    "compute-curvature",
    "context-identifiers",
    "context-ids",
    "context-priorities",
    "context-types",
    "convert-back-units",
    "debug",
    "defer-processing-first-element",
    "dimensionality",
    "digits",
    "disable-boolean-result",
    "disable-opening-subtractions",
    "edge-arrows",
    "ecef",
    "elevation-ref",
    "elevation-ref-guid",
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
    "make-volume",
    "max-offset-deviation",
    "max-offset",
    "max-voids-per-element",
    "mesher-angular-deflection",
    "mesher-linear-deflection",
    "model-offset",
    "model-rotation",
    "no-clean-triangulation",
    "no-normals",
    "no-parallel-mapping",
    "no-wire-intersection-check",
    "no-wire-intersection-tolerance",
    "permissive-shape-reuse",
    "print-space-areas",
    "print-space-names",
    "precision-factor",
    "precision",
    "profile-threshold",
    "reorient-shells",
    "site-local-placement",
    "scale",
    "section-height",
    "section-height-from-storeys",
    "section-ref",
    "separate-z-up-node",
    "space-name-transform",
    "storey-height-line-length",
    "surface-colour",
    "svg-emit-flush-edges",
    "svg-mirror-x",
    "svg-mirror-y",
    "svg-no-css",
    "svg-poly",
    "svg-prefilter",
    "svg-project",
    "svg-render-crease-edges",
    "svg-render-sharp-edges",
    "svg-ridge-angle-min-degrees",
    "svg-segment-projection",
    "svg-subtract-before",
    "svg-unify-inputs",
    "svg-use-edge-classification",
    "svg-valley-angle-min-degrees",
    "svg-without-storeys",
    "svg-write-poly",
    "svg-xmlns",
    "triangulation-type",
    "unify-shapes",
    "use-material-names",
    "use-element-guids",
    "use-element-names",
    "use-element-step-ids",
    "use-element-types",
    "use-python-opencascade",
    "use-world-coords",
    "validate",
    "weld-vertices",
    "y-up",
    "wkt-use-section",
    "center",
    "draw-storey-heights",
    "door-arcs",
]

# NOTE: hybrid-cgal-simple-opencascade is added just as an example
# It's possible to use any hybrid combination by the format below:
# "hybrid-library1-library2".
# List is updated from abstract_kernel.cpp.
GEOMETRY_LIBRARY = Literal["cgal", "cgal-simple", "manifold", "opencascade", "hybrid-cgal-simple-opencascade"]


def has_geometry_library(geometry_library: str) -> bool:
    """Return whether a geometry kernel library can be loaded."""
    return ifcopenshell_wrapper.has_geometry_library(geometry_library)


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
        super().__init__()
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
    def name(k: str) -> SETTING:
        return k.lower().replace("_", "-")

    @staticmethod
    def rname(k: SETTING) -> str:
        return k.upper().replace("-", "_")

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

    def get(self, k: str) -> Any:
        """
        Return value of the setting named `k`.

        :raises RuntimeError: If there is no setting with name `k`.
        """
        k = self.name(k)
        if isinstance(self, settings) and k == "use-python-opencascade":
            return self.use_python_opencascade
        return self.get_(k)

    def setting_names(self) -> tuple[str, ...]:
        setting_names = super().setting_names()
        if isinstance(self, settings):
            setting_names += ("use-python-opencascade",)
        return setting_names

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
            raise AttributeError("'settings' object has no attribute '%s'" % k)

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
                ty = "bool"
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


class settings(settings_mixin, ifcopenshell_wrapper.settings):
    use_python_opencascade = False


class iterator(ifcopenshell_wrapper.iterator):
    def __init__(
        self,
        settings: settings,
        file_or_filename: Union[file, str],
        num_threads: int = 1,
        include: Optional[Union[list[entity_instance], list[str]]] = None,
        exclude: Optional[Union[list[entity_instance], list[str]]] = None,
        geometry_library: GEOMETRY_LIBRARY = "opencascade",
        logger=None,
    ):
        self.settings = settings
        logger = ifcopenshell.logger_or_root(logger)
        if isinstance(file_or_filename, file):
            self.file = file
            file_or_filename = file_or_filename
        else:
            file_or_filename = self.file = open(file_or_filename, logger=logger)

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

                for inst in include_or_exclude:
                    if not inst.is_a("IfcProduct"):
                        raise ValueError(
                            f"include and exclude need to be an aggregate of IfcProduct. Violating element: '{inst}'."
                        )

                initializer = ifcopenshell_wrapper.construct_iterator_with_include_exclude_id

                include_or_exclude = [i.id() for i in include_or_exclude]
            else:
                initializer = ifcopenshell_wrapper.construct_iterator_with_include_exclude

            args = (
                geometry_library,
                self.settings,
                file_or_filename,
                include_or_exclude,
                include is not None,
                num_threads,
            )
            self.this = initializer(*args, *ifcopenshell.optional_logger_args(logger))
        else:
            args = (geometry_library, self.settings, file_or_filename, num_threads)
            self.this = ifcopenshell_wrapper.construct_iterator(*args, *ifcopenshell.optional_logger_args(logger))

    if has_occ:

        def get(self):
            return wrap_shape_creation(self.settings, ifcopenshell_wrapper.iterator.get(self))

    def __iter__(self) -> Generator[IteratorOutput, None, None]:
        if self.initialize():
            while True:
                yield self.get()
                if not self.next():
                    break

    def get_task_products(self):
        return entity_instance.wrap_value(ifcopenshell_wrapper.iterator.get_task_products(self), self.file)


ClashType = Literal["protrusion", "pierce", "collision", "clearance"]
CLASH_TYPE_ITEMS = ("protrusion", "pierce", "collision", "clearance")


class tree(ifcopenshell_wrapper.tree):
    def __init__(self, file: Optional[file] = None, settings: Optional[settings] = None):
        args = [self]
        if file is not None:
            args.append(file)
            if settings is not None:
                args.append(settings)
        ifcopenshell_wrapper.tree.__init__(*args)

    def add_file(self, file: file, settings: settings) -> None:
        ifcopenshell_wrapper.tree.add_file(self, file, settings)

    def add_iterator(self, iterator: iterator) -> None:
        ifcopenshell_wrapper.tree.add_file(self, iterator)

    def select(
        self,
        value: Union[entity_instance, ifcopenshell_wrapper.native_element, tuple[float, float, float]],
        **kwargs,
    ) -> list[entity_instance]:
        def unwrap(value):
            if isinstance(value, entity_instance):
                return value
            elif all(map(lambda v: hasattr(value, v), "XYZ")):
                return value.X(), value.Y(), value.Z()
            return value

        args = [self, unwrap(value)]
        if isinstance(value, (entity_instance, ifcopenshell_wrapper.native_element)):
            args.append(kwargs.get("completely_within", False))
            if "extend" in kwargs:
                args.append(kwargs["extend"])
        elif isinstance(value, (list, tuple)) and len(value) == 3 and set(map(type, value)) == {float}:
            if "extend" in kwargs:
                args.append(kwargs["extend"])
        return ifcopenshell_wrapper.tree.select(*args)

    def select_box(self, value, **kwargs) -> list[entity_instance]:
        def unwrap(value):
            if isinstance(value, entity_instance):
                return value
            elif hasattr(value, "Get"):
                return value.Get()[:3], value.Get()[3:]
            return value

        args = [self, unwrap(value)]
        if "extend" in kwargs or "completely_within" in kwargs:
            args.append(kwargs.get("completely_within", False))
        if "extend" in kwargs:
            args.append(kwargs.get("extend", -1.0e-5))
        return ifcopenshell_wrapper.tree.select_box(*args)

    def clash_intersection_many(
        self,
        set_a: Iterable[entity_instance],
        set_b: Iterable[entity_instance],
        tolerance: float = 0.002,
        check_all: bool = True,
    ) -> tuple[ifcopenshell_wrapper.clash, ...]:
        args = [self, set_a, set_b, tolerance, check_all]
        return ifcopenshell_wrapper.tree.clash_intersection_many(*args)

    def clash_collision_many(
        self, set_a: Iterable[entity_instance], set_b: Iterable[entity_instance], allow_touching=False
    ) -> tuple[ifcopenshell_wrapper.clash, ...]:
        args = [self, set_a, set_b, allow_touching]
        return ifcopenshell_wrapper.tree.clash_collision_many(*args)

    def clash_clearance_many(
        self,
        set_a: Iterable[entity_instance],
        set_b: Iterable[entity_instance],
        clearance: float = 0.05,
        check_all: bool = False,
    ) -> tuple[ifcopenshell_wrapper.clash, ...]:
        args = [self, set_a, set_b, clearance, check_all]
        return ifcopenshell_wrapper.tree.clash_clearance_many(*args)

    @staticmethod
    def get_clash_type(clash_type_i: int) -> ClashType:
        """Convert clash type index to a readable string format.

        :param clash_type_i: Type index that comes from ``clash.clash_type``.
        """
        return CLASH_TYPE_ITEMS[clash_type_i]


def create_shape(
    settings: settings,
    inst: entity_instance,
    repr: Optional[entity_instance] = None,
    geometry_library: GEOMETRY_LIBRARY = "opencascade",
    logger: Optional[ifcopenshell.logger] = None,
) -> Union[ShapeType, ShapeElementType, ifcopenshell_wrapper.transformation, utils.shape_tuple, TopoDS.TopoDS_Shape]:
    """
    Returns a geometric interpretation of the IFC entity instance

    The returned element's ``geometry`` keeps a reference to its owning element, so accessing children
    (e.g. ``create_shape(...).geometry.verts``) no longer requires holding onto the element. See #1124.

    :raises RuntimeError: If failed to process shape. You can turn detailed logging to get more details.

    :return:
        - `inst` is IfcProduct and `repr` provided / None -> ShapeElementType\n
        - `inst` is IfcRepresentation and `repr` is None -> ShapeType\n
        - `inst` is IfcRepresentationItem and `repr` is None -> ShapeType\n
        - `inst` is IfcProfileDef and `repr` is None -> ShapeType\n
        - `inst` is IfcPlacement / IfcObjectPlacement -> transformation\n
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
        (
            ifcopenshell_wrapper.create_shape(
                settings,
                inst,
                repr,
                geometry_library,
                *ifcopenshell.optional_logger_args(logger),
            )
            if repr
            else ifcopenshell_wrapper.create_shape(
                settings,
                inst,
                geometry_library,
                *ifcopenshell.optional_logger_args(logger),
            )
        ),
    )


class kernel:
    """A reusable geometry kernel bound to a (geometry library, file, settings) triple.

    ``ifcopenshell.geom.create_shape`` constructs a new geometry kernel on every
    call, which repeats the backend resolution (including plugin discovery for
    hybrid kernels) and discards the mapping and conversion caches afterwards.
    This class performs that construction once so that converting many products
    one by one reuses the same kernel, mapping and caches, similar to what
    ``ifcopenshell.geom.iterator`` does internally.

    The kernel is bound at construction: the settings are copied and the file
    reference is kept, so later changes to the settings object do not affect an
    existing kernel and instances passed to :meth:`create_shape` must belong to
    the bound file.

    Example:

    .. code:: python

        settings = ifcopenshell.geom.settings()
        k = ifcopenshell.geom.kernel(settings, ifc_file, geometry_library="hybrid-cgal-simple-opencascade")
        for product in ifc_file.by_type("IfcProduct"):
            if product.Representation:
                shape = k.create_shape(product)
    """

    def __init__(
        self,
        settings: settings,
        file: file,
        geometry_library: GEOMETRY_LIBRARY = "opencascade",
        logger: Optional[ifcopenshell.logger] = None,
    ):
        self.settings = settings
        self.file = file
        self.wrapped = ifcopenshell_wrapper.geometry_kernel(
            geometry_library, file, settings, *ifcopenshell.optional_logger_args(logger)
        )

    def create_shape(
        self,
        inst: entity_instance,
        repr: Optional[entity_instance] = None,
    ) -> Union[
        ShapeType, ShapeElementType, ifcopenshell_wrapper.transformation, utils.shape_tuple, TopoDS.TopoDS_Shape
    ]:
        """Identical to :func:`create_shape` but reuses this kernel across calls.

        See :func:`create_shape` for the possible return types; the settings and
        geometry library bound at construction are used for every call.
        """
        return wrap_shape_creation(
            self.settings,
            self.wrapped.create_shape(inst, repr) if repr else self.wrapped.create_shape(inst),
        )


def map_shape(settings: settings, inst: entity_instance) -> ifcopenshell_wrapper.item:
    """
    Returns an interpretation of the geometry encoded as per IfcOpenShell's taxonomy layer.
    In many cases this is somewhat equivalent to the raw IFC data (but schema-agnostic in C++), but
    in other cases such as IfcParameterizedProfileDef the returned item is the equivalent
    of an explicit composite curve.

    >>> point = ifc_file.by_type('IfcCartesianPoint')[0]
    >>> ifcopenshell.geom.map_shape(ifcopenshell.geom.settings(), point).components
    (0.0, 0.0, 0.0)
    """
    return ifcopenshell_wrapper.map_shape(settings, inst)


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
    geometry_library: GEOMETRY_LIBRARY = "opencascade",
    logger=None,
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
    geometry_library: GEOMETRY_LIBRARY = "opencascade",
    logger=None,
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
    geometry_library: GEOMETRY_LIBRARY = "opencascade",
    logger=None,
) -> Generator[Union[IteratorOutput, tuple[int, IteratorOutput]], None, None]: ...
def iterate(
    settings: settings,
    file_or_filename: Union[file, str],
    num_threads: int = 1,
    include: Optional[Union[list[entity_instance], list[str]]] = None,
    exclude: Optional[Union[list[entity_instance], list[str]]] = None,
    *,
    with_progress: bool = False,
    geometry_library: GEOMETRY_LIBRARY = "opencascade",
    logger=None,
) -> Generator[Union[IteratorOutput, tuple[int, IteratorOutput]], None, None]:
    """Get a geometry iterator for the provided file."""
    it = iterator(settings, file_or_filename, num_threads, include, exclude, geometry_library)
    yield from consume_iterator(it, with_progress=with_progress)


def make_shape_function(fn):
    if has_occ:

        def _(schema, string_or_shape, *args):
            if isinstance(string_or_shape, TopoDS.TopoDS_Shape):
                string_or_shape = utils.serialize_shape(string_or_shape)
            return fn(schema, string_or_shape, *args)

    else:

        def _(schema, string, *args):
            return fn(schema, string, *args)

    return _


# @todo, plug-ins now
# serialise = make_shape_function(ifcopenshell_wrapper.serialise)
# tesselate = make_shape_function(ifcopenshell_wrapper.tesselate)


class _serializer_factory:
    _stream_serializers = {"obj", "svg", "ttl"}

    def __init__(self, name: str, extension: str):
        self.name = name
        self.extension = extension
        self.__name__ = name

    def __call__(self, out_filename: Union[str, PathLike[str]], *args: Any) -> ifcopenshell_wrapper.geometry_serializer:
        if self.name == "obj" and len(args) == 2:
            output_filename = args[0]
            output_temp_filename = out_filename
            settings = args[1]
        elif len(args) == 1:
            output_filename = out_filename
            output_temp_filename = out_filename
            settings = args[0]
        else:
            obj_signature = " or (out_filename, mtl_filename, settings)"
            raise TypeError(
                f"serializers.{self.name}() expects (out_filename, settings)"
                + (obj_signature if self.name == "obj" else "")
            )

        if self._is_buffer(output_filename) or self._is_buffer(output_temp_filename):
            if self.name not in self._stream_serializers:
                raise TypeError(f"serializers.{self.name}() requires a filesystem path")
            output_filename = self._buffer(output_filename)
            output_temp_filename = self._buffer(output_temp_filename)
        else:
            output_filename = self._path(output_filename)
            output_temp_filename = self._path(output_temp_filename)

        return ifcopenshell_wrapper.create_geometry_serializer(
            self.extension, output_filename, output_temp_filename, settings
        )

    def _is_buffer(self, value: Any) -> bool:
        return isinstance(value, ifcopenshell_wrapper.buffer)

    def _buffer(self, value: Union[str, PathLike[str], ifcopenshell_wrapper.buffer]) -> ifcopenshell_wrapper.buffer:
        if self._is_buffer(value):
            return value
        return ifcopenshell_wrapper.buffer(self._path(value))

    def _path(self, value: Union[str, PathLike[str]]) -> str:
        try:
            path = fspath(value)
        except TypeError:
            raise TypeError(f"serializers.{self.name}() requires a filesystem path") from None
        if not isinstance(path, str):
            raise TypeError(f"serializers.{self.name}() requires a text filesystem path")
        return path


class _serializers_meta(type):
    _extensions = {
        "obj": "obj",
        "svg": "svg",
        "ttl": "ttl",
        "gltf": "glb",
        "glb": "glb",
        "collada": "dae",
        "dae": "dae",
        "stp": "stp",
        "step": "stp",
        "igs": "igs",
        "iges": "igs",
        "usd": "usd",
        "usda": "usd",
        "usdc": "usd",
    }

    def __getattr__(cls, name: str) -> _serializer_factory:
        extension = cls._extensions.get(name)
        if extension is None:
            raise AttributeError(f"type object 'serializers' has no attribute '{name}'")
        factory = _serializer_factory(name, extension)
        setattr(cls, name, factory)
        return factory

    def __dir__(cls) -> list[str]:
        return sorted(set(super().__dir__()) | set(cls._extensions))


class serializers(metaclass=_serializers_meta):
    buffer = ifcopenshell_wrapper.buffer

    @classmethod
    def guess_from_extension(cls, filepath: str):
        ext = filepath.rsplit(".", 1)[-1].lower()
        mapping = {
            "glb": "gltf",
            "obj": "obj",
            "svg": "svg",
            "ttl": "ttl",
            "dae": "collada",
            "stp": "stp",
            "step": "step",
            "igs": "igs",
            "iges": "iges",
            "usd": "usd",
            "usda": "usda",
            "usdc": "usdc",
        }
        serializer_name = mapping.get(ext)
        if not serializer_name:
            raise ValueError(f"No serializer available for .{ext} file")
        return getattr(cls, serializer_name)
