import math
import numpy as np
import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.geolocation

from behave import step

from bimtester import util
from bimtester.ifc import IfcStore
from bimtester.lang import _


@step(u'There must be at least one "{ifc_class}" element')
def step_impl(context, ifc_class):
    assert len(IfcStore.file.by_type(ifc_class)) >= 1, _("An element of {} could not be found").format(ifc_class)


def check_ifc4_geolocation(entity_name, prop_name=None, value=None, should_assert=True):
    if entity_name not in IfcStore.bookmarks:
        has_entity = False
        project = IfcStore.file.by_type("IfcProject")[0]
        for context in project.RepresentationContexts:
            if entity_name == "IfcMapConversion":
                if (
                    context.is_a("IfcGeometricRepresentationContext")
                    and context.ContextType == "Model"
                    and context.HasCoordinateOperation
                ):
                    IfcStore.bookmarks[entity_name] = context.HasCoordinateOperation[0]
                    has_entity = True
            elif entity_name == "IfcProjectedCRS":
                if (
                    context.is_a("IfcGeometricRepresentationContext")
                    and context.ContextType == "Model"
                    and context.HasCoordinateOperation
                    and context.HasCoordinateOperation[0].TargetCRS
                ):
                    IfcStore.bookmarks[entity_name] = context.HasCoordinateOperation[0].TargetCRS
                    has_entity = True
        if not has_entity:
            assert False, _("No model geometric representation contexts refer to an {}").format(entity_name)
    if not prop_name:
        return
    actual_value = getattr(IfcStore.bookmarks[entity_name], prop_name)
    if should_assert:
        assert actual_value == value, _('We expected a value of "{}" but instead got "{}"').format(value, actual_value)
    else:
        return actual_value


@step(u"The project must have coordinate reference system data")
def step_impl(context):
    if IfcStore.file.schema == "IFC2X3":
        for site in IfcStore.file.by_type("IfcSite"):
            util.assert_pset(site, "EPset_ProjectedCRS")
        return
    check_ifc4_geolocation("IfcProjectedCRS")


@step(u'The name of the CRS must be "{coordinate_reference_name}"')
def step_impl(context, coordinate_reference_name):
    if IfcStore.file.schema == "IFC2X3":
        for site in IfcStore.file.by_type("IfcSite"):
            util.assert_pset(site, "EPset_ProjectedCRS", "Name", coordinate_reference_name)
        return
    check_ifc4_geolocation("IfcProjectedCRS", "Name", coordinate_reference_name)


@step(u'The description of the CRS must be "{value}"')
def step_impl(context, value):
    if IfcStore.file.schema == "IFC2X3":
        for site in IfcStore.file.by_type("IfcSite"):
            util.assert_pset(site, "EPset_ProjectedCRS", "Description", value)
        return
    check_ifc4_geolocation("IfcProjectedCRS", "Description", value)


@step(u'The geodetic datum must be "{coordinate_reference_name}"')
def step_impl(context, coordinate_reference_name):
    if IfcStore.file.schema == "IFC2X3":
        for site in IfcStore.file.by_type("IfcSite"):
            util.assert_pset(site, "EPset_ProjectedCRS", "GeodeticDatum", coordinate_reference_name)
        return
    check_ifc4_geolocation("IfcProjectedCRS", "GeodeticDatum", coordinate_reference_name)


@step(u'The vertical datum must be "{coordinate_reference_name}"')
def step_impl(context, coordinate_reference_name):
    if IfcStore.file.schema == "IFC2X3":
        for site in IfcStore.file.by_type("IfcSite"):
            util.assert_pset(site, "EPset_ProjectedCRS", "VerticalDatum", coordinate_reference_name)
        return
    check_ifc4_geolocation("IfcProjectedCRS", "VerticalDatum", coordinate_reference_name)


@step(u'The map projection must be "{coordinate_reference_name}"')
def step_impl(context, coordinate_reference_name):
    if IfcStore.file.schema == "IFC2X3":
        for site in IfcStore.file.by_type("IfcSite"):
            util.assert_pset(site, "EPset_ProjectedCRS", "MapProjection", coordinate_reference_name)
        return
    check_ifc4_geolocation("IfcProjectedCRS", "MapProjection", coordinate_reference_name)


@step(u'The map zone must be "{coordinate_reference_name}"')
def step_impl(context, coordinate_reference_name):
    if IfcStore.file.schema == "IFC2X3":
        for site in IfcStore.file.by_type("IfcSite"):
            util.assert_pset(site, "EPset_ProjectedCRS", "MapZone", coordinate_reference_name)
        return
    check_ifc4_geolocation("IfcProjectedCRS", "MapZone", coordinate_reference_name)


@step(u'The map unit must be "{unit}"')
def step_impl(context, unit):
    if IfcStore.file.schema == "IFC2X3":
        for site in IfcStore.file.by_type("IfcSite"):
            util.assert_pset(site, "EPset_ProjectedCRS", "MapUnit", unit)
        return
    actual_value = check_ifc4_geolocation("IfcProjectedCRS", "MapUnit", should_assert=False)
    if not actual_value:
        assert False, _("A unit was not provided in the projected CRS")
    if actual_value.is_a("IfcSIUnit"):
        prefix = actual_value.Prefix if actual_value.Prefix else ""
        actual_value = prefix + actual_value.Name
    elif actual_value.is_a("IfcConversionBasedUnit"):
        actual_value = actual_value.Name
    assert actual_value == unit, _('We expected a value of "{}" but instead got "{}"').format(unit, actual_value)


@step(u"The project must have coordinate transformations to convert from local to global coordinates")
def step_impl(context):
    if IfcStore.file.schema == "IFC2X3":
        for site in IfcStore.file.by_type("IfcSite"):
            util.assert_pset(site, "EPset_MapConversion")
    check_ifc4_geolocation("IfcMapConversion")


@step(u'The eastings of the model must be offset by "{number}" to derive its global coordinates')
def step_impl(context, number):
    number = util.assert_number(number)
    if IfcStore.file.schema == "IFC2X3":
        for site in IfcStore.file.by_type("IfcSite"):
            util.assert_pset(site, "EPset_MapConversion", "Eastings", number)
        return
    check_ifc4_geolocation("IfcMapConversion", "Eastings", number)


@step(u'The northings of the model must be offset by "{number}" to derive its global coordinates')
def step_impl(context, number):
    number = util.assert_number(number)
    if IfcStore.file.schema == "IFC2X3":
        for site in IfcStore.file.by_type("IfcSite"):
            util.assert_pset(site, "EPset_MapConversion", "Northings", number)
        return
    check_ifc4_geolocation("IfcMapConversion", "Northings", number)


@step(u'The height of the model must be offset by "{number}" to derive its global coordinates')
def step_impl(context, number):
    number = util.assert_number(number)
    if IfcStore.file.schema == "IFC2X3":
        for site in IfcStore.file.by_type("IfcSite"):
            util.assert_pset(site, "EPset_MapConversion", "OrthogonalHeight", number)
        return
    check_ifc4_geolocation("IfcMapConversion", "OrthogonalHeight", number)


@step(u'The model must be rotated clockwise by "{number}" to derive its global coordinates')
def step_impl(context, number):
    number = util.assert_number(number)
    if IfcStore.file.schema == "IFC2X3":
        return check_ifc2x3_geolocation("EPset_MapConversion", "Height", number)
    abscissa = check_ifc4_geolocation("IfcMapConversion", "XAxisAbscissa", should_assert=False)
    ordinate = check_ifc4_geolocation("IfcMapConversion", "XAxisOrdinate", should_assert=False)
    actual_value = round(ifcopenshell.util.geolocation.xaxis2angle(abscissa, ordinate), 3)
    value = round(number, 3)
    assert actual_value == value, _('We expected a value of "{}" but instead got "{}"').format(value, actual_value)


@step(u'The model must be scaled along the horizontal axis by "{number}" to derive its global coordinates')
def step_impl(context, number):
    number = util.assert_number(number)
    if IfcStore.file.schema == "IFC2X3":
        for site in IfcStore.file.by_type("IfcSite"):
            util.assert_pset(site, "EPset_MapConversion", "Scale", number)
        return
    check_ifc4_geolocation("IfcMapConversion", "Scale", number)


@step(u'The model must be rotated clockwise by "{number}" for true north to point up')
def step_impl(context, number):
    number = util.assert_number(number)
    project = IfcStore.file.by_type("IfcProject")[0]
    for c in project.RepresentationContexts:
        if c.TrueNorth:
            actual_value = round(
                ifcopenshell.util.geolocation.yaxis2angle(
                    c.TrueNorth.DirectionRatios[0], c.TrueNorth.DirectionRatios[1]
                ),
                3,
            )
            value = round(number, 3)
            assert actual_value == value, _('We expected a value of "{}" but instead got "{}"').format(
                value, actual_value
            )
            return
    assert False, _("True north is not defined in the file")


@step(u'The site "{guid}" has a longitude of "{number}"')
def step_impl(context, guid, number):
    number = util.assert_number(number)
    site = util.assert_guid(IfcStore.file, guid)
    util.assert_type(site, "IfcSite")
    ref = util.assert_attribute(site, "RefLongitude")
    number = ifcopenshell.util.geolocation.dd2dms(number, use_ms=(len(ref) == 4))
    util.assert_attribute(site, "RefLongitude", number)


@step(u'The site "{guid}" has a latitude of "{number}"')
def step_impl(context, guid, number):
    number = util.assert_number(number)
    site = util.assert_guid(IfcStore.file, guid)
    util.assert_type(site, "IfcSite")
    ref = util.assert_attribute(site, "RefLatitude")
    number = ifcopenshell.util.geolocation.dd2dms(number, use_ms=(len(ref) == 4))
    util.assert_attribute(site, "RefLatitude", number)


@step(u'The site "{guid}" has an elevation of "{number}"')
def step_impl(context, guid, number):
    number = util.assert_number(number)
    site = util.assert_guid(IfcStore.file, guid)
    util.assert_type(site, "IfcSite")
    util.assert_attribute(site, "RefElevation", number)


@step(u'The site "{guid}" must be coincident with the project origin')
def step_impl(context, guid):
    site = util.assert_guid(IfcStore.file, guid)
    util.assert_type(site, "IfcSite")
    if not site.ObjectPlacement:
        assert False, _("The site has no object placement")
    site_placement = ifcopenshell.util.placement.get_local_placement(site.ObjectPlacement)[:,3][0:3]
    origin = np.array([0, 0, 0])
    assert np.allclose(origin, site_placement), _('The site location is at "{}" instead of "{}"')
