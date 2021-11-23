import ifcopenshell.util.geolocation
import ifcopenshell.util.placement

from behave import step

from bimtester import util
from bimtester.ifc import IfcStore
from bimtester.lang import _


def get_decimal_points(value):
    try:
        return len(value.split(".")[1])
    except:
        return 0


def get_containing_spatial_elements(element):
    results = []
    if element.is_a("IfcSpatialElement"):
        results.append(element)
        for rel in element.Decomposes:
            if rel.is_a("IfcRelAggregates"):
                results.append(get_containing_spatial_elements(rel.RelatingObject))
    elif element.is_a("IfcElement"):
        for rel in element.ContainedInStructure:
            if rel.is_a("ifcRelContainedInSpatialStructure"):
                results.append(get_containing_spatial_elements(rel.RelatingStructure))
    return results


@step('There is a datum element "{guid}" as an "{ifc_class}"')
def step_impl(context, guid, ifc_class):
    element = util.assert_guid(IfcStore.file, guid)
    util.assert_type(element, ifc_class)


@step(
    'The element "{guid}" has a global easting, northing, and elevation of "{easting}", "{northing}", and "{elevation}" respectively'
)
def step_impl(context, guid, easting, northing, elevation):
    if IfcStore.file.schema == "IFC2X3":
        if element.is_a("IfcSite"):
            site = element
        else:
            potential_sites = [s for s in get_containing_spatial_elements(element) if s.is_a("IfcSite")]
            if potential_sites:
                site = potential_sites[0]
            else:
                assert False, _("The datum element does not belong to a geolocated site")
        map_conversion = util.assert_pset(site, "EPset_MapConversion")
    else:
        map_conversion = IfcStore.file.by_type("IfcMapConversion")
        if map_conversion:
            map_conversion = map_conversion[0].get_info()
        else:
            assert False, _("No map conversion was found in the file")

    element = util.assert_guid(IfcStore.file, guid)
    if not element.ObjectPlacement:
        assert False, _("The element does not have an object placement: {}").format(element)
    m = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
    e, n, h = ifcopenshell.util.geolocation.xyz2enh(
        m[0][3],
        m[1][3],
        m[2][3],
        float(map_conversion["Eastings"]),
        float(map_conversion["Northings"]),
        float(map_conversion["OrthogonalHeight"]),
        float(map_conversion["XAxisAbscissa"]),
        float(map_conversion["XAxisOrdinate"]),
        float(map_conversion["Scale"]),
    )
    element_x = round(e, get_decimal_points(easting))
    element_y = round(n, get_decimal_points(northing))
    element_z = round(h, get_decimal_points(elevation))
    expected_placement = (util.assert_number(easting), util.assert_number(northing), util.assert_number(elevation))
    if (element_x, element_y, element_z) != expected_placement:
        assert False, _("The element {} is meant to have a location of {} but instead we found {}").format(
            element, expected_placement, (element_x, element_y, element_z)
        )


@step('The element "{guid}" has a local X, Y, and Z coordinate of "{x}", "{y}", and "{z}" respectively')
def step_impl(context, guid, x, y, z):
    element = util.assert_guid(IfcStore.file, guid)
    if not element.ObjectPlacement:
        assert False, _("The element does not have an object placement: {}").format(element)
    m = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
    element_x = round(m[0][3], get_decimal_points(x))
    element_y = round(m[1][3], get_decimal_points(y))
    element_z = round(m[2][3], get_decimal_points(z))
    expected_placement = (util.assert_number(x), util.assert_number(y), util.assert_number(z))
    if (element_x, element_y, element_z) != expected_placement:
        assert False, _("The element {} is meant to have a location of {} but instead we found {}").format(
            element, expected_placement, (element_x, element_y, element_z)
        )
