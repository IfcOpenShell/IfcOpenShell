from behave import step
from utils import IfcFile, assert_number, assert_pset, assert_attribute
import math
import ifcopenshell.util
import ifcopenshell.util.element
import ifcopenshell.util.geolocation


@step(u"There must be at least one {ifc_class} element")
def step_impl(context, ifc_class):
    assert len(IfcFile.get().by_type(ifc_class)) >= 1, "An element of {} could not be found".format(ifc_class)


def check_ifc4_geolocation(entity_name, prop_name=None, value=None, should_assert=True):
    if entity_name not in IfcFile.bookmarks:
        has_entity = False
        project = IfcFile.get().by_type("IfcProject")[0]
        for context in project.RepresentationContexts:
            if entity_name == "IfcMapConversion":
                if (
                    context.is_a("IfcGeometricRepresentationContext")
                    and context.ContextType == "Model"
                    and context.HasCoordinateOperation
                ):
                    IfcFile.bookmarks[entity_name] = context.HasCoordinateOperation[0]
                    has_entity = True
            elif entity_name == "IfcProjectedCRS":
                if (
                    context.is_a("IfcGeometricRepresentationContext")
                    and context.ContextType == "Model"
                    and context.HasCoordinateOperation
                    and context.HasCoordinateOperation[0].TargetCRS
                ):
                    IfcFile.bookmarks[entity_name] = context.HasCoordinateOperation[0].TargetCRS
                    has_entity = True
        if not has_entity:
            assert False, "No model geometric representation contexts refer to an {}".format(entity_name)
    if not prop_name:
        return
    actual_value = getattr(IfcFile.bookmarks[entity_name], prop_name)
    if should_assert:
        assert actual_value == value, 'We expected a value of "{}" but instead got "{}"'.format(value, actual_value)
    else:
        return actual_value


@step(u"The project must have coordinate reference system data")
def step_impl(context):
    if IfcFile.get().schema == "IFC2X3":
        for site in IfcFile.get().by_type("IfcSite"):
            assert_pset(site, "EPset_ProjectedCRS")
        return
    check_ifc4_geolocation("IfcProjectedCRS")


@step(u"The name of the CRS must be {coordinate_reference_name}")
def step_impl(context, coordinate_reference_name):
    if IfcFile.get().schema == "IFC2X3":
        for site in IfcFile.get().by_type("IfcSite"):
            assert_pset(site, "EPset_ProjectedCRS", "Name", coordinate_reference_name)
        return
    check_ifc4_geolocation("IfcProjectedCRS", "Name", coordinate_reference_name)


@step(u"The description of the CRS must be {value}")
def step_impl(context, value):
    if IfcFile.get().schema == "IFC2X3":
        for site in IfcFile.get().by_type("IfcSite"):
            assert_pset(site, "EPset_ProjectedCRS", "Description", value)
        return
    check_ifc4_geolocation("IfcProjectedCRS", "Description", value)


@step(u"The geodetic datum must be {coordinate_reference_name}")
def step_impl(context, coordinate_reference_name):
    if IfcFile.get().schema == "IFC2X3":
        for site in IfcFile.get().by_type("IfcSite"):
            assert_pset(site, "EPset_ProjectedCRS", "GeodeticDatum", coordinate_reference_name)
        return
    check_ifc4_geolocation("IfcProjectedCRS", "GeodeticDatum", coordinate_reference_name)


@step(u"The vertical datum must be {coordinate_reference_name}")
def step_impl(context, coordinate_reference_name):
    if IfcFile.get().schema == "IFC2X3":
        for site in IfcFile.get().by_type("IfcSite"):
            assert_pset(site, "EPset_ProjectedCRS", "VerticalDatum", coordinate_reference_name)
        return
    check_ifc4_geolocation("IfcProjectedCRS", "VerticalDatum", coordinate_reference_name)


@step(u"The map projection must be {coordinate_reference_name}")
def step_impl(context, coordinate_reference_name):
    if IfcFile.get().schema == "IFC2X3":
        for site in IfcFile.get().by_type("IfcSite"):
            assert_pset(site, "EPset_ProjectedCRS", "MapProjection", coordinate_reference_name)
        return
    check_ifc4_geolocation("IfcProjectedCRS", "MapProjection", coordinate_reference_name)


@step(u"The map zone must be {coordinate_reference_name}")
def step_impl(context, coordinate_reference_name):
    if IfcFile.get().schema == "IFC2X3":
        for site in IfcFile.get().by_type("IfcSite"):
            assert_pset(site, "EPset_ProjectedCRS", "MapZone", coordinate_reference_name)
        return
    check_ifc4_geolocation("IfcProjectedCRS", "MapZone", coordinate_reference_name)


@step(u"The map unit must be {unit}")
def step_impl(context, unit):
    if IfcFile.get().schema == "IFC2X3":
        for site in IfcFile.get().by_type("IfcSite"):
            assert_pset(site, "EPset_ProjectedCRS", "MapUnit", unit)
        return
    actual_value = check_ifc4_geolocation("IfcProjectedCRS", "MapUnit", should_assert=False)
    if not actual_value:
        assert False, "A unit was not provided in the projected CRS"
    if actual_value.is_a("IfcSIUnit"):
        prefix = actual_value.Prefix if actual_value.Prefix else ""
        actual_value = prefix + actual_value.Name
    elif actual_value.is_a("IfcConversionBasedUnit"):
        actual_value = actual_value.Name
    assert actual_value == unit, 'We expected a value of "{}" but instead got "{}"'.format(unit, actual_value)


@step(u"The project must have coordinate transformations to convert from local to global coordinates")
def step_impl(context):
    if IfcFile.get().schema == "IFC2X3":
        for site in IfcFile.get().by_type("IfcSite"):
            assert_pset(site, "EPset_MapConversion")
    check_ifc4_geolocation("IfcMapConversion")


@step(u"The eastings of the model must be offset by {number} to derive its global coordinates")
def step_impl(context, number):
    number = assert_number(number)
    if IfcFile.get().schema == "IFC2X3":
        for site in IfcFile.get().by_type("IfcSite"):
            assert_pset(site, "EPset_MapConversion", "Eastings", number)
        return
    check_ifc4_geolocation("IfcMapConversion", "Eastings", number)


@step(u"The northings of the model must be offset by {number} to derive its global coordinates")
def step_impl(context, number):
    number = assert_number(number)
    if IfcFile.get().schema == "IFC2X3":
        for site in IfcFile.get().by_type("IfcSite"):
            assert_pset(site, "EPset_MapConversion", "Northings", number)
        return
    check_ifc4_geolocation("IfcMapConversion", "Northings", number)


@step(u"The height of the model must be offset by {number} to derive its global coordinates")
def step_impl(context, number):
    number = assert_number(number)
    if IfcFile.get().schema == "IFC2X3":
        for site in IfcFile.get().by_type("IfcSite"):
            assert_pset(site, "EPset_MapConversion", "OrthogonalHeight", number)
        return
    check_ifc4_geolocation("IfcMapConversion", "OrthogonalHeight", number)


@step(u"The model must be rotated clockwise by {number} to derive its global coordinates")
def step_impl(context, number):
    number = assert_number(number)
    if IfcFile.get().schema == "IFC2X3":
        return check_ifc2x3_geolocation("EPset_MapConversion", "Height", number)
    abscissa = check_ifc4_geolocation("IfcMapConversion", "XAxisAbscissa", should_assert=False)
    ordinate = check_ifc4_geolocation("IfcMapConversion", "XAxisOrdinate", should_assert=False)
    actual_value = round(ifcopenshell.util.geolocation.xy2angle(abscissa, ordinate), 3)
    value = round(number, 3)
    assert actual_value == value, 'We expected a value of "{}" but instead got "{}"'.format(value, actual_value)


@step(u"The model must be scaled along the horizontal axis by {number} to derive its global coordinates")
def step_impl(context, number):
    number = assert_number(number)
    if IfcFile.get().schema == "IFC2X3":
        for site in IfcFile.get().by_type("IfcSite"):
            assert_pset(site, "EPset_MapConversion", "Scale", number)
        return
    check_ifc4_geolocation("IfcMapConversion", "Scale", number)


@step(u"The site {guid} has a longitude of {number}")
def step_impl(context, guid, number):
    number = assert_number(number)
    site = IfcFile.by_guid(guid)
    if not site.is_a("IfcSite"):
        assert False, "The element {} is not an IfcSite".format(site)
    ref = assert_attribute(site, "RefLongitude")
    number = ifcopenshell.util.geolocation.dd2dms(number, use_ms=(len(ref) == 4))
    assert_attribute(site, "RefLongitude", number)


@step(u"The site {guid} has a latitude of {number}")
def step_impl(context, guid, number):
    number = assert_number(number)
    site = IfcFile.by_guid(guid)
    if not site.is_a("IfcSite"):
        assert False, "The element {} is not an IfcSite".format(site)
    ref = assert_attribute(site, "RefLatitude")
    number = ifcopenshell.util.geolocation.dd2dms(number, use_ms=(len(ref) == 4))
    assert_attribute(site, "RefLatitude", number)


@step(u"The site {guid} has an elevation of {number}")
def step_impl(context, guid, number):
    number = assert_number(number)
    site = IfcFile.by_guid(guid)
    if not site.is_a("IfcSite"):
        assert False, "The element {} is not an IfcSite".format(site)
    assert_attribute(site, "RefElevation", number)
