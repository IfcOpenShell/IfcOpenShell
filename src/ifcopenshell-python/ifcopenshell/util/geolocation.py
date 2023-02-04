# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

import math
import numpy as np
import ifcopenshell
import ifcopenshell.util.unit


def dms2dd(degrees, minutes, seconds, ms=0):
    dd = float(degrees) + float(minutes) / 60.0 + float(seconds) / (3600.0) + float(ms / 3600000000.0)
    return dd


def dd2dms(dd, use_ms=False):
    dd = float(dd)
    sign = 1 if dd >= 0 else -1
    dd = abs(dd)
    if use_ms:
        seconds, ms = divmod(dd * 60 * 60 * 1000000, 1000000)
    minutes, seconds = divmod(dd * 60 * 60, 60)
    degrees, minutes = divmod(minutes, 60)
    if dd < 0:
        degrees = -degrees
    if use_ms:
        return (int(degrees) * sign, int(minutes) * sign, int(seconds) * sign, int(ms) * sign)
    return (int(degrees) * sign, int(minutes) * sign, int(seconds) * sign)


def xyz2enh(x, y, z, eastings, northings, orthogonal_height, x_axis_abscissa, x_axis_ordinate, scale=None):
    if scale is None:
        scale = 1.0
    rotation = math.atan2(x_axis_ordinate, x_axis_abscissa)
    a = scale * math.cos(rotation)
    b = scale * math.sin(rotation)
    eastings = (a * x) - (b * y) + eastings
    northings = (b * x) + (a * y) + northings
    height = z + orthogonal_height
    return (eastings, northings, height)


def auto_z2e(ifc_file, z):
    """Convert a Z coordinate to an elevation using model georeferencing data

    The necessary georeferencing map conversion is automatically detected from
    the IFC map conversion parameters present in the IFC model. If no map
    conversion is present, then the Z coordinate is returned unchanged.

    :param ifc_file: The IFC file
    :type ifc_file: ifcopenshell.file.file
    :param z: The Z local engineering coordinate provided in project length units.
    :type z: float
    :return: The elevation in project length units.
    :rtype: float
    """
    try:
        conversion = ifc_file.by_type("IfcMapConversion")
    except:
        return z
    if not conversion or not conversion[0].OrthogonalHeight:
        return z
    conversion = conversion[0]
    h = conversion.OrthogonalHeight
    map_unit = conversion.TargetCRS.MapUnit
    if map_unit:
        project_unit = ifcopenshell.util.unit.get_project_unit(ifc_file, "LENGTHUNIT")
        h = ifcopenshell.util.unit.convert(
            h,
            getattr(map_unit, "Prefix", None),
            map_unit.Name,
            getattr(project_unit, "Prefix", None),
            project_unit.Name,
        )
    return z2e(z, h)


def z2e(z, h):
    return z + h


def enh2xyz(e, n, h, eastings, northings, orthogonal_height, x_axis_abscissa, x_axis_ordinate, scale=None):
    if scale is None:
        scale = 1.0
    rotation = math.atan2(x_axis_ordinate, x_axis_abscissa)
    a = scale * math.cos(rotation)
    b = scale * math.sin(rotation)
    x = ((b * n) - (b * northings) - (a * eastings) + (a * e)) / ((a * a) + (b * b))
    y = ((a * n) - (a * northings) + (b * eastings) - (b * e)) / ((a * a) + (b * b))
    z = h - orthogonal_height
    return (x, y, z)


def local2global(matrix, eastings, northings, orthogonal_height, x_axis_abscissa, x_axis_ordinate, scale=None):
    if scale is None:
        scale = 1.0
    x = np.array([x_axis_abscissa, x_axis_ordinate, 0])
    x /= np.linalg.norm(x)
    y = np.cross(np.array([0, 0, 1]), x)
    intermediate = (
        np.array(
            [
                [x[0], y[0], 0, 0],
                [x[1], y[1], 0, 0],
                [x[2], y[2], 1, 0],
                [0, 0, 0, 1],
            ]
        )
        @ matrix
    )
    intermediate[0, 3] = (intermediate[0, 3] * scale) + eastings
    intermediate[1, 3] = (intermediate[1, 3] * scale) + northings
    intermediate[2, 3] = (intermediate[2, 3] * scale) + orthogonal_height
    return intermediate


def global2local(matrix, eastings, northings, orthogonal_height, x_axis_abscissa, x_axis_ordinate, scale=None):
    if scale is None:
        scale = 1.0
    x = np.array([x_axis_abscissa, x_axis_ordinate, 0])
    x /= np.linalg.norm(x)
    y = np.cross(np.array([0, 0, 1]), x)
    result = matrix.copy()
    result[0, 3] = (result[0, 3] - eastings) / scale
    result[1, 3] = (result[1, 3] - northings) / scale
    result[2, 3] = (result[2, 3] - orthogonal_height) / scale
    return (
        np.linalg.inv(
            np.array(
                [
                    [x[0], y[0], 0, 0],
                    [x[1], y[1], 0, 0],
                    [x[2], y[2], 1, 0],
                    [0, 0, 0, 1],
                ]
            )
        )
        @ result
    )


# Used for converting the X and Y vectors of the X Axis in IFC grid north geolocation
def xaxis2angle(x, y):
    return math.degrees(math.atan2(y, x)) * -1


# Used for converting the X and Y vectors of the Y Axis in IFC true north geolocation
def yaxis2angle(x, y):
    angle = math.degrees(math.atan2(y, x)) - 90
    if angle < -180:
        angle += 360
    elif angle > 180:
        angle -= 360
    return angle
