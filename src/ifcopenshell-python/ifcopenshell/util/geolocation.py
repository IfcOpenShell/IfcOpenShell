def dms2dd(degrees, minutes, seconds, milliseconds=0):
    dd = float(degrees) + float(minutes)/60 + float(seconds)/(3600)
    return dd

def dd2dms(dd):
    dd = float(dd)
    sign = 1 if dd >= 0 else -1
    dd = abs(dd)
    minutes, seconds = divmod(dd*3600, 60)
    degrees, minutes = divmod(minutes, 60)
    if dd < 0:
        degrees = -degrees
    return (int(degrees) * sign, int(minutes) * sign, int(seconds) * sign)

def xyz2enh(x, y, z, eastings, northings, orthogonal_height, x_axis_abscissa, x_axis_ordinate, scale=None):
    if scale is None:
        scale = 1.
    rotation = atan2(x_axis_ordinate, x_axis_abscissa)
    a = scale * cos(rotation)
    b = scale * sin(rotation)
    eastings = (a * x) - (b * y) + eastings
    northings = (b * x) + (a * y) + northings
    height = z + orthogonal_height
    return (eastings, northings, height)
