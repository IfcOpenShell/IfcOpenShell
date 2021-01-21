import numpy as np

def a2p(o, z, x):
    y = np.cross(z, x)
    r = np.eye(4)
    r[:-1, :-1] = x, y, z
    r[-1, :-1] = o
    return r.T


def get_axis2placement(plc):
    z = np.array(plc.Axis.DirectionRatios if plc.Axis else (0, 0, 1))
    x = np.array(plc.RefDirection.DirectionRatios if plc.RefDirection else (1, 0, 0))
    o = plc.Location.Coordinates
    return a2p(o, z, x)


def get_local_placement(plc):
    if plc is None:
        return np.eye(4)
    if plc.PlacementRelTo is None:
        parent = np.eye(4)
    else:
        parent = get_local_placement(plc.PlacementRelTo)
    return np.dot(get_axis2placement(plc.RelativePlacement), parent)
