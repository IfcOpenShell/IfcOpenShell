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
import random
import operator
import warnings
import ifcopenshell.ifcopenshell_wrapper as ifcopenshell_wrapper

from typing import NamedTuple, Any, Union
from typing_extensions import assert_never
from collections.abc import Iterable

import OCC

try:
    from OCC.Core import V3d, TopoDS, gp, AIS, Quantity, BRepTools, Graphic3d

    USE_OCCT_HANDLE = False
except ImportError:
    from OCC import V3d, TopoDS, gp, AIS, Quantity, BRepTools, Graphic3d

    USE_OCCT_HANDLE = True


class shape_tuple(NamedTuple):
    """A tuple containing IfcOpenShell serialized element/shape and pythonOCC shape."""

    data: Union[ifcopenshell_wrapper.SerializedElement, ifcopenshell_wrapper.Serialization]
    geometry: TopoDS.TopoDS_Shape
    styles: tuple[tuple[float, float, float, float], ...]
    style_ids: tuple[int, ...]


handle, main_loop, add_menu, add_function_to_menu = None, None, None, None

DEFAULT_STYLES = {
    "DEFAULT": (0.7, 0.7, 0.7),
    "IfcSite": (0.75, 0.8, 0.65),
    "IfcSlab": (0.4, 0.4, 0.4),
    "IfcWallStandardCase": (0.9, 0.9, 0.9),
    "IfcWall": (0.9, 0.9, 0.9),
    "IfcWindow": (0.75, 0.8, 0.75, 0.3),
    "IfcDoor": (0.55, 0.3, 0.15),
    "IfcBeam": (0.75, 0.7, 0.7),
    "IfcRailing": (0.65, 0.6, 0.6),
    "IfcMember": (0.65, 0.6, 0.6),
    "IfcPlate": (0.8, 0.8, 0.8),
}


def initialize_display():
    import OCC.Display.SimpleGui

    global handle, main_loop, add_menu, add_function_to_menu
    handle, main_loop, add_menu, add_function_to_menu = OCC.Display.SimpleGui.init_display()

    def setup():
        viewer_handle = handle.GetViewer()
        viewer = viewer_handle.GetObject() if hasattr(viewer_handle, "GetObject") else viewer_handle

        def lights():
            viewer.InitActiveLights()
            for _ in range(2):
                try:
                    active_light = viewer.ActiveLight()
                except BaseException:
                    break
                yield active_light
                viewer.NextActiveLights()

        lights = list(lights())
        for l in lights:
            viewer.DelLight(l)

        if hasattr(V3d, "V3d_TypeOfOrientation_Yup_AxoRight"):
            dirs = [[V3d.V3d_TypeOfOrientation_Yup_AxoRight], [V3d.V3d_TypeOfOrientation_Zup_AxoRight]]
        else:
            dirs = [(3, 2, 1), (-1, -2, -3)]

        for dir in dirs:
            if OCC.VERSION < "7.5":
                light = V3d.V3d_DirectionalLight(viewer_handle)
                light.SetDirection(*dir)
            else:
                light = V3d.V3d_DirectionalLight(*dir)
            viewer.SetLightOn(light.GetHandle() if USE_OCCT_HANDLE else light)

    setup()
    return handle


def yield_subshapes(shape):
    it = TopoDS.TopoDS_Iterator(shape)
    while it.More():
        yield it.Value()
        it.Next()


def display_shape(shape, clr=None, viewer_handle=None):
    if viewer_handle is None:
        viewer_handle = handle

    if isinstance(shape, shape_tuple):
        shape, representation = shape.geometry, shape
    else:
        representation = None

    material = Graphic3d.Graphic3d_MaterialAspect(Graphic3d.Graphic3d_NOM_PLASTER)

    if representation and not clr:
        if len(set(representation.styles)) == 1:
            clr = representation.styles[0]
            if min(clr) < 0.0 or max(clr) > 1.0:
                clr = DEFAULT_STYLES.get(representation.data.type, DEFAULT_STYLES["DEFAULT"])

    if clr:
        ais = AIS.AIS_Shape(shape)
        ais.SetMaterial(material)

        if isinstance(clr, str):
            qclr = getattr(
                Quantity, "Quantity_NOC_%s" % clr.upper(), getattr(Quantity, "Quantity_NOC_%s1" % clr.upper(), None)
            )
            if qclr is None:
                raise Exception("No color named '%s'" % clr.upper())
        elif isinstance(clr, Iterable):
            clr = tuple(clr)
            if len(clr) < 3 or len(clr) > 4:
                raise Exception("Need 3 or 4 color components. Got '%r'." % len(clr))
            qclr = Quantity.Quantity_Color(clr[0], clr[1], clr[2], Quantity.Quantity_TOC_RGB)
        elif isinstance(clr, Quantity.Quantity_Color):
            qclr = clr
        else:
            raise Exception("Object of type %r cannot be used as a color." % type(clr))

        ais.SetColor(qclr)
        if isinstance(clr, tuple) and len(clr) == 4 and clr[3] < 1.0:
            ais.SetTransparency(1.0 - clr[3])

    elif representation and hasattr(AIS, "AIS_MultipleConnectedShape"):
        default_style_applied = None

        ais = AIS.AIS_MultipleConnectedShape(shape)

        subshapes = list(yield_subshapes(shape))
        lens = len(representation.styles), len(subshapes)
        if lens[0] != lens[1]:
            warnings.warn("Unable to assign styles to subshapes. Encountered %d styles for %d shapes." % lens)
        else:
            for shp, stl in zip(subshapes, representation.styles):
                subshape = AIS.AIS_Shape(shp)
                if min(stl) < 0.0 or max(stl) > 1.0:
                    default_style_applied = stl = DEFAULT_STYLES.get(
                        representation.data.type, DEFAULT_STYLES["DEFAULT"]
                    )
                subshape.SetColor(Quantity.Quantity_Color(stl[0], stl[1], stl[2], Quantity.Quantity_TOC_RGB))
                subshape.SetMaterial(material)
                if len(stl) == 4 and stl[3] < 1.0:
                    subshape.SetTransparency(1.0 - stl[3])
                ais.Connect(subshape.GetHandle())

        # For some reason it is necessary to set transparency here again
        # in order for transparency to be rendered on the subshape.
        applied_styles = representation.styles
        if default_style_applied:
            if len(default_style_applied) == 3:
                default_style_applied += (1.0,)
            applied_styles += (default_style_applied,)

        if len(applied_styles):
            # The only way for this not to be true if is the entire shape is NULL
            min_transp = min(map(operator.itemgetter(3), applied_styles))
            if min_transp < 1.0:
                ais.SetTransparency(1.0)

    else:
        ais = AIS.AIS_Shape(shape)
        ais.SetMaterial(material)

        def r():
            return random.random() * 0.3 + 0.7

        clr = Quantity.Quantity_Color(r(), r(), r(), Quantity.Quantity_TOC_RGB)
        ais.SetColor(clr)

    ais_handle = ais.GetHandle() if USE_OCCT_HANDLE else ais
    viewer_handle.Context.Display(ais_handle, False)

    return ais_handle


def set_shape_transparency(ais, t, update_viewer=True):
    handle.Context.SetTransparency(ais, t, update_viewer)


def get_bounding_box_center(bbox):
    bbmin = [0.0] * 3
    bbmax = [0.0] * 3
    bbmin[0], bbmin[1], bbmin[2], bbmax[0], bbmax[1], bbmax[2] = bbox.Get()
    return gp.gp_Pnt(*map(lambda xy: (xy[0] + xy[1]) / 2.0, zip(bbmin, bbmax)))


def serialize_shape(shape):
    shapes = BRepTools.BRepTools_ShapeSet()

    # @todo provide method to get ifcopenshell's built-in occt version to
    # see whether this is necessary
    shapes.SetFormatNb(2)

    shapes.Add(shape)
    if hasattr(shapes, "WriteToString"):
        return shapes.WriteToString()
    else:
        return shapes.Write()


def create_shape_from_serialization(
    brep_object: Union[ifcopenshell_wrapper.SerializedElement, ifcopenshell_wrapper.Serialization],
) -> Union[shape_tuple, TopoDS.TopoDS_Shape]:
    brep_data, occ_shape, styles, style_ids = None, None, (), ()

    is_product_shape = True
    if isinstance(brep_object, ifcopenshell_wrapper.SerializedElement):
        brep_data = brep_object.geometry.brep_data
        styles = brep_object.geometry.surface_styles
        style_ids = brep_object.geometry.surface_style_ids
    elif isinstance(brep_object, ifcopenshell_wrapper.Serialization):
        try:
            brep_data = brep_object.brep_data
            styles = brep_object.surface_styles
            style_ids = brep_object.surface_style_ids
            is_product_shape = False
        except BaseException as e:
            print("Error occurred creating a shape:", e)
    else:
        assert_never(brep_object)

    styles = tuple(styles[i : i + 4] for i in range(0, len(styles), 4))

    if not brep_data:
        return shape_tuple(brep_object, None, styles, style_ids)

    try:
        if OCC.VERSION < "7.8":
            ss = BRepTools.BRepTools_ShapeSet()
            ss.ReadFromString(brep_data)
            occ_shape = ss.Shape(ss.NbShapes())
        else:
            ss = BRepTools.breptools()
            occ_shape = ss.ReadFromString(brep_data)
    except BaseException as e:
        print("Error occurred parsing a shape from a string:", e)

    if is_product_shape:
        return shape_tuple(brep_object, occ_shape, styles, style_ids)
    else:
        return occ_shape
