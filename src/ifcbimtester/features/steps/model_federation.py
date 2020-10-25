import numpy as np
import ifcopenshell.util.geolocation
from behave import step
from utils import IfcFile
from utils import IfcFile, assert_number, assert_type


def a2p(o, z, x):
    y = np.cross(z, x)
    r = np.eye(4)
    r[:-1,:-1] = x,y,z
    r[-1,:-1] = o
    return r.T


def get_axis2placement(plc):
    z = np.array(plc.Axis.DirectionRatios if plc.Axis else (0,0,1))
    x = np.array(plc.RefDirection.DirectionRatios if plc.RefDirection else (1,0,0))
    o = plc.Location.Coordinates
    return a2p(o,z,x)


def get_local_placement(plc):
    if plc is None:
        return np.eye(4)
    if plc.PlacementRelTo is None:
        parent = np.eye(4)
    else:
        parent = get_local_placement(plc.PlacementRelTo)
    return np.dot(get_axis2placement(plc.RelativePlacement), parent)


def get_decimal_points(value):
    try:
        return len(value.split('.')[1])
    except:
        return 0


def get_containing_spatial_elements(element):
    results = []
    if element.is_a('IfcSpatialElement'):
        results.append(element)
        for rel in element.Decomposes:
            if rel.is_a('IfcRelAggregates'):
                results.append(get_containing_spatial_elements(rel.RelatingObject))
    elif element.is_a('IfcElement'):
        for rel in element.ContainedInStructure:
            if rel.is_a('ifcRelContainedInSpatialStructure'):
                results.append(get_containing_spatial_elements(rel.RelatingStructure))
    return results


@step('There is a datum element {guid} as an {ifc_class}')
def step_impl(context, guid, ifc_class):
    element = IfcFile.by_guid(guid)
    assert_type(element, ifc_class)


@step('The element {guid} has a global easting, northing, and elevation of {easting}, {northing}, and {elevation} respectively')
def step_impl(context, guid, easting, northing, elevation):
    if IfcFile.get().schema == 'IFC2X3':
        if element.is_a('IfcSite'):
            site = element
        else:
            potential_sites = [s for s in get_containing_spatial_elements(element) if s.is_a('IfcSite')]
            if potential_sites:
                site = potential_sites[0]
            else:
                assert False, 'The datum element does not belong to a geolocated site'
        map_conversion = assert_pset(site, 'EPset_MapConversion')
    else:
        map_conversion = IfcFile.get().by_type('IfcMapConversion')
        if map_conversion:
            map_conversion = map_conversion[0].get_info()
        else:
            assert False, 'No map conversion was found in the file'

    element = IfcFile.by_guid(guid)
    if not element.ObjectPlacement:
        assert False, 'The element does not have an object placement: {}'.format(element)
    m = get_local_placement(element.ObjectPlacement)
    e, n, h = ifcopenshell.util.geolocation.xyz2enh(
        m[0][3], m[1][3], m[2][3],
        float(map_conversion['Eastings']),
        float(map_conversion['Northings']),
        float(map_conversion['OrthogonalHeight']),
        float(map_conversion['XAxisAbscissa']),
        float(map_conversion['XAxisOrdinate']),
        float(map_conversion['Scale']),
    )
    element_x = round(e, get_decimal_points(easting))
    element_y = round(n, get_decimal_points(northing))
    element_z = round(h, get_decimal_points(elevation))
    expected_placement = (assert_number(easting), assert_number(northing), assert_number(elevation))
    if (element_x, element_y, element_z) != expected_placement:
        assert False, 'The element {} is meant to have a location of {} but instead we found {}'.format(
            element, expected_placement, (element_x, element_y, element_z))


@step('The element {guid} has a local X, Y, and Z coordinate of {x}, {y}, and {z} respectively')
def step_impl(context, guid, x, y, z):
    element = IfcFile.by_guid(guid)
    if not element.ObjectPlacement:
        assert False, 'The element does not have an object placement: {}'.format(element)
    m = get_local_placement(element.ObjectPlacement)
    element_x = round(m[0][3], get_decimal_points(x))
    element_y = round(m[1][3], get_decimal_points(y))
    element_z = round(m[2][3], get_decimal_points(z))
    expected_placement = (assert_number(x), assert_number(y), assert_number(z))
    if (element_x, element_y, element_z) != expected_placement:
        assert False, 'The element {} is meant to have a location of {} but instead we found {}'.format(
            element, expected_placement, (element_x, element_y, element_z))
