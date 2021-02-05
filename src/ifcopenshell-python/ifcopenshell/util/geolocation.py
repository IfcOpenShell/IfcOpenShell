import math
import numpy as np


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
        np.matrix(
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
            np.matrix(
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


# Used for converting the X and Y vectors of the X Axis in IFC geolocation
def xy2angle(x, y):
    return math.degrees(math.atan2(y, x))
