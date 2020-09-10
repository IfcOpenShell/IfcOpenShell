import math

def dms2dd(degrees, minutes, seconds, ms=0):
    dd = float(degrees) + float(minutes)/60.0 + float(seconds)/(3600.0) + float(ms/3600000000.0)
    return dd

def dd2dms(dd, use_ms=False):
    dd = float(dd)
    sign = 1 if dd >= 0 else -1
    dd = abs(dd)
    if use_ms:
        seconds, ms = divmod(dd*60*60*1000000, 1000000)
    minutes, seconds = divmod(dd*60*60, 60)
    degrees, minutes = divmod(minutes, 60)
    if dd < 0:
        degrees = -degrees
    if use_ms:
        return (int(degrees) * sign, int(minutes) * sign, int(seconds) * sign, int(ms) * sign)
    return (int(degrees) * sign, int(minutes) * sign, int(seconds) * sign)

def xyz2enh(x, y, z, eastings, northings, orthogonal_height, x_axis_abscissa, x_axis_ordinate, scale=None):
    if scale is None:
        scale = 1.
    rotation = math.atan2(x_axis_ordinate, x_axis_abscissa)
    a = scale * math.cos(rotation)
    b = scale * math.sin(rotation)
    eastings = (a * x) - (b * y) + eastings
    northings = (b * x) + (a * y) + northings
    height = z + orthogonal_height
    return (eastings, northings, height)

# Used for converting the X and Y vectors of the X Axis in IFC geolocation
def xy2angle(x, y):
    return math.degrees(math.atan2(y, x))
