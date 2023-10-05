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
    """Convert degrees, minutes, and (milli)seconds to decimal degrees

    :param degrees: The degrees component
    :type degrees: int
    :param minutes: The minutes component
    :type minutes: int
    :param seconds: The seconds component
    :type seconds: int
    :param ms: The milliseconds component
    :type ms: int
    :return: The angle in decimal degrees.
    :rtype: float
    """
    dd = float(degrees) + float(minutes) / 60.0 + float(seconds) / (3600.0) + float(ms / 3600000000.0)
    return dd


def dd2dms(dd, use_ms=False):
    """Convert decimal degrees to degrees, minutes, and (milli)seconds format

    :param dd: The decimal degrees
    :type dd: float
    :param use_ms: True if to include milliseconds and false otherwise. Defaults to false.
    :type use_ms: bool
    :return: The angle in a tuple of either 3 or 4 values, being degrees,
        minutes, seconds, and optionally milliseconds.
    :rtype: tuple[float]
    """
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
    """Manually convert local XYZ coordinates to map eastings, northings, and height

    This function is for advanced users as it allows you to specify your own
    helmert transformation parameters (i.e. those typically stored in
    IfcMapConversion). This manual approach is useful for tests or in case your
    are setting your helmert transformations in non-standard locations, or if
    you are applying your own temporary false origin (such as when federating
    models for digital twins of large cities).

    No unit conversion is performed.

    For most scenarios you should use ``auto_xyz2enh`` instead.

    :param x: The X local engineering coordinate.
    :type x: float
    :param y: The Y local engineering coordinate.
    :type y: float
    :param z: The Z local engineering coordinate.
    :type z: float
    :param eastings: The eastings offset to apply.
    :type eastings: float
    :param northings: The northings offset to apply.
    :type northings: float
    :param orthogonal_height: The orthogonal height offset to apply.
    :type orthogonal_height: float
    :param x_axis_abscissa: The X axis abscissa (i.e. first coordinate) of the
        2D vector that points to the local X axis when in map coordinates.
    :type x_axis_abscissa: float
    :param x_axis_ordinate: The X axis ordinate (i.e. second coordinate) of the
        2D vector that points to the local X axis when in map coordinates.
    :type x_axis_ordinate: float
    :param scale: The combined scale factor to convert from local coordinates
        to map coordinates.
    :type scale: float
    :return: A tuple of three ordinates representing the easting, northing and height.
    :rtype: tuple[float]
    """
    if scale is None:
        scale = 1.0
    rotation = math.atan2(x_axis_ordinate, x_axis_abscissa)
    a = scale * math.cos(rotation)
    b = scale * math.sin(rotation)
    eastings = (a * x) - (b * y) + eastings
    northings = (b * x) + (a * y) + northings
    height = z + orthogonal_height
    return (eastings, northings, height)


def xyz2enh_ifc4x3(
    x,
    y,
    z,
    eastings,
    northings,
    orthogonal_height,
    x_axis_abscissa,
    x_axis_ordinate,
    scale=1.0,
    factor_x=1.0,
    factor_y=1.0,
    factor_z=1.0,
):
    theta = math.atan2(x_axis_ordinate, x_axis_abscissa)
    eastings = (scale * factor_x * math.cos(theta) * x) - (scale * factor_y * math.sin(theta) * y) + eastings
    northings = (scale * factor_x * math.sin(theta) * x) + (scale * factor_y * math.cos(theta) * y) + northings
    height = (scale * factor_z * z) + orthogonal_height
    return (eastings, northings, height)


def auto_xyz2enh(ifc_file, x, y, z):
    """Convert from local XYZ coordinates to global map coordinate eastings, northings, and heights

    The necessary georeferencing map conversion is automatically detected from
    the IFC map conversion parameters present in the IFC model. If no map
    conversion is present, then the Z coordinate is returned unchanged.

    For IFC2X3, the map conversion is detected from the IfcProject's
    ePSet_MapConversion. See the "User Guide for Geo-referencing in IFC":
    https://www.buildingsmart.org/standards/bsi-standards/standards-library/

    :param ifc_file: The IFC file
    :type ifc_file: ifcopenshell.file.file
    :param x: The X local engineering coordinate provided in project length units.
    :type x: float
    :param y: The Y local engineering coordinate provided in project length units.
    :type y: float
    :param z: The Z local engineering coordinate provided in project length units.
    :type z: float
    :return: The global map coordinate eastings, northings, and height in map units.
    :rtype: tuple[float]
    """
    conversion = None
    try:
        conversion = ifc_file.by_type("IfcMapConversion")
    except:
        pass

    if conversion:
        conversion = conversion[0]
        e = conversion.Eastings or 0
        n = conversion.Northings or 0
        h = conversion.OrthogonalHeight or 0
        xaa = conversion.XAxisAbscissa or 0
        xao = conversion.XAxisOrdinate or 0
        scale = conversion.Scale or 1
        map_unit = conversion.TargetCRS.MapUnit
    else:
        project = ifc_file.by_type("IfcProject")[0]
        conversion = ifcopenshell.util.element.get_pset(project, "ePSet_MapConversion")
        if not conversion:
            return (x, y, z)

        e = conversion.get("Eastings", None) or 0
        n = conversion.get("Northings", None) or 0
        h = conversion.get("OrthogonalHeight", None) or 0
        xaa = conversion.get("XAxisAbscissa", None) or 0
        xao = conversion.get("XAxisOrdinate", None) or 0
        scale = conversion.get("Scale", None) or 1
        map_unit = None

    if not xaa and not xao:
        xaa = 1.0
        xao = 0.0

    if map_unit:
        # Warning! This definition has changed in IFC4X3 such that map_unit no
        # longer affects unit conversion, only the Scale attribute affects unit
        # conversion. TODO: consolidate once IFC4X3 confirmed.
        project_unit = ifcopenshell.util.unit.get_project_unit(ifc_file, "LENGTHUNIT")
        map_prefix = getattr(map_unit, "Prefix", None)
        project_prefix = getattr(project_unit, "Prefix", None)
        e = ifcopenshell.util.unit.convert(e, map_prefix, map_unit.Name, project_prefix, project_unit.Name)
        n = ifcopenshell.util.unit.convert(n, map_prefix, map_unit.Name, project_prefix, project_unit.Name)
        h = ifcopenshell.util.unit.convert(h, map_prefix, map_unit.Name, project_prefix, project_unit.Name)
    return xyz2enh(x, y, z, e, n, h, xaa, xao, scale)


def auto_enh2xyz(ifc_file, easting, northing, height):
    """Convert from global map coordinate eastings, northings, and heights to local XYZ coordinates

    The necessary georeferencing map conversion is automatically detected from
    the IFC map conversion parameters present in the IFC model. If no map
    conversion is present, then the Z coordinate is returned unchanged.

    For IFC2X3, the map conversion is detected from the IfcProject's
    ePSet_MapConversion. See the "User Guide for Geo-referencing in IFC":
    https://www.buildingsmart.org/standards/bsi-standards/standards-library/

    :param ifc_file: The IFC file
    :type ifc_file: ifcopenshell.file.file
    :param easting: The global easting map coordinate provided in map units.
    :type easting: float
    :param northing: The global northing map coordinate provided in map units.
    :type northing: float
    :param height: The global height map coordinate provided in map units.
    :type height: float
    :return: The local engineering XYZ coordinates in project length units.
    :rtype: tuple[float]
    """
    conversion = None
    try:
        conversion = ifc_file.by_type("IfcMapConversion")
    except:
        pass

    if conversion:
        conversion = conversion[0]
        e = conversion.Eastings or 0
        n = conversion.Northings or 0
        h = conversion.OrthogonalHeight or 0
        xaa = conversion.XAxisAbscissa or 0
        xao = conversion.XAxisOrdinate or 0
        scale = conversion.Scale or 1
        map_unit = conversion.TargetCRS.MapUnit
    else:
        project = ifc_file.by_type("IfcProject")[0]
        conversion = ifcopenshell.util.element.get_pset(project, "ePSet_MapConversion")
        if not conversion:
            return (easting, northing, height)

        e = conversion.get("Eastings", None) or 0
        n = conversion.get("Northings", None) or 0
        h = conversion.get("OrthogonalHeight", None) or 0
        xaa = conversion.get("XAxisAbscissa", None) or 0
        xao = conversion.get("XAxisOrdinate", None) or 0
        scale = conversion.get("Scale", None) or 1
        map_unit = None

    if not xaa and not xao:
        xaa = 1.0
        xao = 0.0

    if map_unit:
        # Warning! This definition has changed in IFC4X3 such that map_unit no
        # longer affects unit conversion, only the Scale attribute affects unit
        # conversion. TODO: consolidate once IFC4X3 confirmed.
        project_unit = ifcopenshell.util.unit.get_project_unit(ifc_file, "LENGTHUNIT")
        map_prefix = getattr(map_unit, "Prefix", None)
        project_prefix = getattr(project_unit, "Prefix", None)
        e = ifcopenshell.util.unit.convert(e, map_prefix, map_unit.Name, project_prefix, project_unit.Name)
        n = ifcopenshell.util.unit.convert(n, map_prefix, map_unit.Name, project_prefix, project_unit.Name)
        h = ifcopenshell.util.unit.convert(h, map_prefix, map_unit.Name, project_prefix, project_unit.Name)
    return enh2xyz(easting, northing, height, e, n, h, xaa, xao, scale)


def auto_z2e(ifc_file, z):
    """Convert a Z coordinate to an elevation using model georeferencing data

    The necessary georeferencing map conversion is automatically detected from
    the IFC map conversion parameters present in the IFC model. If no map
    conversion is present, then the Z coordinate is returned unchanged.

    For IFC2X3, the map conversion is detected from the IfcProject's
    ePSet_MapConversion. See the "User Guide for Geo-referencing in IFC":
    https://www.buildingsmart.org/standards/bsi-standards/standards-library/

    :param ifc_file: The IFC file
    :type ifc_file: ifcopenshell.file.file
    :param z: The Z local engineering coordinate provided in project length units.
    :type z: float
    :return: The elevation in project length units.
    :rtype: float
    """
    conversion = None
    try:
        conversion = ifc_file.by_type("IfcMapConversion")
    except:
        pass

    if conversion and not conversion[0].OrthogonalHeight:
        conversion = conversion[0]
        h = conversion.OrthogonalHeight
        map_unit = conversion.TargetCRS.MapUnit
    else:
        project = ifc_file.by_type("IfcProject")[0]
        conversion = ifcopenshell.util.element.get_pset(project, "ePSet_MapConversion")
        if not conversion:
            return z

        h = conversion.get("OrthogonalHeight", None) or 0
        map_unit = None

    if map_unit:
        # Warning! This definition has changed in IFC4X3 such that map_unit no
        # longer affects unit conversion, only the Scale attribute affects unit
        # conversion. TODO: consolidate once IFC4X3 confirmed.
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
    """Manually convert a Z coordinate to an elevation

    This function is for advanced users as it allows you to specify your own
    orthogonal height offset.

    For most scenarios you should use ``auto_z2e`` instead.

    :param z: The Z local engineering coordinate provided in project length units.
    :type z: float
    :param h: The orthogonal height offset in project length units.
    :type h: float
    :return: The elevation in project length units.
    :rtype: float
    """
    return z + h


def enh2xyz(e, n, h, eastings, northings, orthogonal_height, x_axis_abscissa, x_axis_ordinate, scale=None):
    """Manually convert  map eastings, northings, and height to local XYZ coordinates

    This function is for advanced users as it allows you to specify your own
    helmert transformation parameters (i.e. those typically stored in
    IfcMapConversion). This manual approach is useful for tests or in case your
    are setting your helmert transformations in non-standard locations, or if
    you are applying your own temporary false origin (such as when federating
    models for digital twins of large cities).

    No unit conversion is performed.

    For most scenarios you should use ``auto_enh2xyz`` instead.

    :param e: The global easting map coordinate.
    :type e: float
    :param n: The global northing map coordinate.
    :type n: float
    :param h: The global height map coordinate.
    :type h: float
    :param eastings: The eastings offset to apply.
    :type eastings: float
    :param northings: The northings offset to apply.
    :type northings: float
    :param orthogonal_height: The orthogonal height offset to apply.
    :type orthogonal_height: float
    :param x_axis_abscissa: The X axis abscissa (i.e. first coordinate) of the
        2D vector that points to the local X axis when in map coordinates.
    :type x_axis_abscissa: float
    :param x_axis_ordinate: The X axis ordinate (i.e. second coordinate) of the
        2D vector that points to the local X axis when in map coordinates.
    :type x_axis_ordinate: float
    :param scale: The combined scale factor to convert from local coordinates
        to map coordinates.
    :type scale: float
    :return: A tuple of three ordinates representing XYZ.
    :rtype: tuple[float]
    """
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
    """Manually convert a 4x4 matrix from local to global coordinates

    This function is for advanced users as it allows you to specify your own
    helmert transformation parameters (i.e. those typically stored in
    IfcMapConversion). This manual approach is useful for tests or in case your
    are setting your helmert transformations in non-standard locations, or if
    you are applying your own temporary false origin (such as when federating
    models for digital twins of large cities).

    No unit conversion is performed.

    :param matrix: A 4x4 numpy matrix representing local coordinates.
    :type matrix: np.array
    :param eastings: The eastings offset to apply.
    :type eastings: float
    :param northings: The northings offset to apply.
    :type northings: float
    :param orthogonal_height: The orthogonal height offset to apply.
    :type orthogonal_height: float
    :param x_axis_abscissa: The X axis abscissa (i.e. first coordinate) of the
        2D vector that points to the local X axis when in map coordinates.
    :type x_axis_abscissa: float
    :param x_axis_ordinate: The X axis ordinate (i.e. second coordinate) of the
        2D vector that points to the local X axis when in map coordinates.
    :type x_axis_ordinate: float
    :param scale: The combined scale factor to convert from local coordinates
        to map coordinates.
    :type scale: float
    :return: A numpy 4x4 array matrix representing global coordinates.
    :rtype: np.array
    """
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


def local2global_ifc4x3(
    matrix,
    eastings,
    northings,
    orthogonal_height,
    x_axis_abscissa,
    x_axis_ordinate,
    scale=1.0,
    factor_x=1.0,
    factor_y=1.0,
    factor_z=1.0,
):
    # Matrix is a 4x4 matrix typically describing the object placement of an element.
    theta = math.atan2(x_axis_ordinate, x_axis_abscissa)
    scale_and_factor_matrix = np.array(
        [
            [scale * factor_x, 0, 0, 0],
            [0, scale * factor_y, 0, 0],
            [0, 0, scale * factor_z, 0],
            [0, 0, 0, 1],
        ]
    )
    rotation_matrix = np.array(
        [
            [math.cos(theta), -math.sin(theta), 0, 0],
            [math.sin(theta), math.cos(theta), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ]
    )
    result = rotation_matrix @ scale_and_factor_matrix @ matrix
    result[:, 0][0:3] /= np.linalg.norm(result[:, 0][0:3])
    result[:, 1][0:3] /= np.linalg.norm(result[:, 1][0:3])
    result[:, 2][0:3] /= np.linalg.norm(result[:, 2][0:3])
    result[0][3] += eastings
    result[1][3] += northings
    result[2][3] += orthogonal_height
    return result


def global2local(matrix, eastings, northings, orthogonal_height, x_axis_abscissa, x_axis_ordinate, scale=None):
    """Manually convert a 4x4 matrix from global to local coordinates

    This function is for advanced users as it allows you to specify your own
    helmert transformation parameters (i.e. those typically stored in
    IfcMapConversion). This manual approach is useful for tests or in case your
    are setting your helmert transformations in non-standard locations, or if
    you are applying your own temporary false origin (such as when federating
    models for digital twins of large cities).

    No unit conversion is performed.

    :param matrix: A 4x4 numpy matrix representing global coordinates.
    :type matrix: np.array
    :param eastings: The eastings offset to apply.
    :type eastings: float
    :param northings: The northings offset to apply.
    :type northings: float
    :param orthogonal_height: The orthogonal height offset to apply.
    :type orthogonal_height: float
    :param x_axis_abscissa: The X axis abscissa (i.e. first coordinate) of the
        2D vector that points to the local X axis when in map coordinates.
    :type x_axis_abscissa: float
    :param x_axis_ordinate: The X axis ordinate (i.e. second coordinate) of the
        2D vector that points to the local X axis when in map coordinates.
    :type x_axis_ordinate: float
    :param scale: The combined scale factor to convert from local coordinates
        to map coordinates.
    :type scale: float
    :return: A numpy 4x4 array matrix representing local coordinates.
    :rtype: np.array
    """
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


def xaxis2angle(x, y):
    """Converts X axis abscissa and ordinates to an angle in decimal degrees

    :param x: The X axis abscissa
    :type x: float
    :param y: The X axis ordinate
    :type y: float
    :return: The equivalent angle in decimal degrees from the X axis
    :rtype: float
    """
    return math.degrees(math.atan2(y, x)) * -1


def yaxis2angle(x, y):
    """Converts Y axis abscissa and ordinates to an angle in decimal degrees

    The Y axis abscissa and ordinate is how IFC stores true north.

    :param x: The Y axis abscissa
    :type x: float
    :param y: The Y axis ordinate
    :type y: float
    :return: The equivalent angle in decimal degrees from the Y axis
    :rtype: float
    """
    angle = math.degrees(math.atan2(y, x)) - 90
    if angle < -180:
        angle += 360
    elif angle > 180:
        angle -= 360
    return angle


def get_grid_north(ifc_file):
    """Get an angle pointing to map grid north

    Anticlockwise is positive.

    The necessary georeferencing map conversion is automatically detected from
    the IFC map conversion parameters present in the IFC model. If no map
    conversion is present, then the Z coordinate is returned unchanged.

    For IFC2X3, the map conversion is detected from the IfcProject's
    ePSet_MapConversion. See the "User Guide for Geo-referencing in IFC":
    https://www.buildingsmart.org/standards/bsi-standards/standards-library/

    :param ifc_file: The IFC file
    :type ifc_file: ifcopenshell.file.file
    :return: An angle to grid north in decimal degrees
    :rtype: float
    """
    conversion = None
    try:
        conversion = ifc_file.by_type("IfcMapConversion")[0]
    except:
        pass
    if conversion:
        if not conversion.XAxisAbscissa or not conversion.XAxisOrdinate:
            return 0
        xaa = conversion.XAxisAbscissa
        xao = conversion.XAxisOrdinate
    else:
        project = ifc_file.by_type("IfcProject")[0]
        conversion = ifcopenshell.util.element.get_pset(project, "ePSet_MapConversion")
        if not conversion:
            return 0
        xaa = conversion.get("XAxisAbscissa", None) or 0
        xao = conversion.get("XAxisOrdinate", None) or 0
    return xaxis2angle(xaa, xao)


def get_true_north(ifc_file):
    """Get an angle pointing to global true north

    Anticlockwise is positive.

    Always remember that true north is not a constant! (Unless you are working
    in polar coordinates) This true north is only a reference value useful for
    things like solar analysis on small sites (<1km). If you're after the north
    that your surveyor is using, you're probably after ``get_grid_north``
    instead.

    :param ifc_file: The IFC file
    :type ifc_file: ifcopenshell.file.file
    :return: An angle to true north in decimal degrees
    :rtype: float
    """
    try:
        for context in ifc_file.by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if context.TrueNorth:
                return yaxis2angle(*context.TrueNorth.DirectionRatios[0:2])
    except:
        return 0
    return 0


def angle2xaxis(angle):
    """Converts an angle into an X axis abscissa and ordinate

    The inverse of ``xaxis2angle``.

    :param angle: The angle in decimal degrees where anticlockwise is positive.
    :type angle: float
    :return: A tuple of X axis abscissa and ordinate
    :rtype: tuple[float]
    """
    angle_rad = math.radians(angle)
    x = math.cos(angle_rad)
    y = -math.sin(angle_rad)
    return x, y


def angle2yaxis(angle):
    """Converts an angle into an Y axis abscissa and ordinate

    The inverse of ``yaxis2angle``.

    :param angle: The angle in decimal degrees where anticlockwise is positive.
    :type angle: float
    :return: A tuple of Y axis abscissa and ordinate
    :rtype: tuple[float]
    """
    angle_rad = math.radians(angle)
    x = -math.sin(angle_rad)
    y = math.cos(angle_rad)
    return x, y
