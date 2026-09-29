/********************************************************************************
 *                                                                              *
 * This file is part of IfcOpenShell.                                           *
 *                                                                              *
 * IfcOpenShell is free software: you can redistribute it and/or modify         *
 * it under the terms of the Lesser GNU General Public License as published by  *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * IfcOpenShell is distributed in the hope that it will be useful,              *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * Lesser GNU General Public License for more details.                          *
 *                                                                              *
 * You should have received a copy of the Lesser GNU General Public License     *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

/********************************************************************************
 *                                                                              *
 * This class is a subclass of the regular file class that implements        *
 * several convenience functions for creating geometrical representations and   *
 * spatial containers.                                                          *
 *                                                                              *
 ********************************************************************************/

#include "hierarchy_helper.h"

#include <time.h>

using namespace std::string_literals;

namespace {
template <typename Person>
auto set_person_identification(Person& person, const std::string& value, int)
    -> decltype(person.setIdentification(value), void()) {
    person.setIdentification(value);
}

template <typename Person>
void set_person_identification(Person& person, const std::string& value, ...) {
    person.setId(value);
}
} // namespace

template <typename Schema>
typename Schema::IfcAxis2Placement3D hierarchy_helper<Schema>::addPlacement3d(
    double ox, double oy, double oz, double zx, double zy, double zz, double xx, double xy, double xz) {
    auto x = addTriplet<typename Schema::IfcDirection>(xx, xy, xz);
    auto z = addTriplet<typename Schema::IfcDirection>(zx, zy, zz);
    auto o = addTriplet<typename Schema::IfcCartesianPoint>(ox, oy, oz);
    auto p3d = create<typename Schema::IfcAxis2Placement3D>();
    p3d.setLocation(o);
    p3d.setAxis(z);
    p3d.setRefDirection(x);
    return p3d;
}

template <typename Schema>
typename Schema::IfcAxis2Placement2D hierarchy_helper<Schema>::addPlacement2d(
    double ox, double oy, double xx, double xy) {
    auto x = addDoublet<typename Schema::IfcDirection>(xx, xy);
    auto o = addDoublet<typename Schema::IfcCartesianPoint>(ox, oy);
    auto p2d = create<typename Schema::IfcAxis2Placement2D>();
    p2d.setLocation(o);
    p2d.setRefDirection(x);
    return p2d;
}

template <typename Schema>
typename Schema::IfcLocalPlacement hierarchy_helper<Schema>::addLocalPlacement(typename Schema::IfcObjectPlacement parent,
                                                                                  double ox,
                                                                                  double oy,
                                                                                  double oz,
                                                                                  double zx,
                                                                                  double zy,
                                                                                  double zz,
                                                                                  double xx,
                                                                                  double xy,
                                                                                  double xz) {
    auto local_placement = create<typename Schema::IfcLocalPlacement>();
    if (parent) {
        local_placement.setPlacementRelTo(parent);
    }
    local_placement.setRelativePlacement(addPlacement3d(ox, oy, oz, zx, zy, zz, xx, xy, xz));
    return local_placement;
}

template <typename Schema>
typename Schema::IfcOwnerHistory hierarchy_helper<Schema>::addOwnerHistory() {
    typename Schema::IfcPerson person = create<typename Schema::IfcPerson>();
    set_person_identification(person, "", 0);

    auto organization = create<typename Schema::IfcOrganization>();
    organization.setName("IfcOpenShell");

    auto person_and_org = create<typename Schema::IfcPersonAndOrganization>();
    person_and_org.setThePerson(person);
    person_and_org.setTheOrganization(organization);

    auto application = create<typename Schema::IfcApplication>();
    application.setApplicationDeveloper(organization);
    application.setVersion(IFCOPENSHELL_VERSION);
    application.setApplicationFullName("IfcOpenShell");
    application.setApplicationIdentifier("IfcOpenShell");

    int timestamp = (int)time(0);
    auto owner_hist = create<typename Schema::IfcOwnerHistory>();
    owner_hist.setOwningUser(person_and_org);
    owner_hist.setOwningApplication(application);
    owner_hist.setChangeAction(Schema::IfcChangeActionEnum::IfcChangeAction_ADDED);
    owner_hist.setLastModifiedDate(timestamp);
    owner_hist.setLastModifyingUser(person_and_org);
    owner_hist.setLastModifyingApplication(application);
    owner_hist.setCreationDate(timestamp);

    return owner_hist;
}

template <typename Schema>
typename Schema::IfcProject hierarchy_helper<Schema>::addProject(typename Schema::IfcOwnerHistory owner_hist) {
    std::vector<typename Schema::IfcRepresentationContext> rep_contexts;

    auto dimexp = create<typename Schema::IfcDimensionalExponents>();
    dimexp.setLengthExponent(0);
    dimexp.setMassExponent(0);
    dimexp.setTimeExponent(0);
    dimexp.setElectricCurrentExponent(0);
    dimexp.setThermodynamicTemperatureExponent(0);
    dimexp.setAmountOfSubstanceExponent(0);
    dimexp.setLuminousIntensityExponent(0);

    auto unit1 = create<typename Schema::IfcSIUnit>();
    unit1.setUnitType(Schema::IfcUnitEnum::IfcUnit_LENGTHUNIT);
    unit1.setPrefix(Schema::IfcSIPrefix::IfcSIPrefix_MILLI);
    unit1.setName(Schema::IfcSIUnitName::IfcSIUnitName_METRE);

    auto unit2a = create<typename Schema::IfcSIUnit>();
    unit2a.setUnitType(Schema::IfcUnitEnum::IfcUnit_PLANEANGLEUNIT);
    unit2a.setName(Schema::IfcSIUnitName::IfcSIUnitName_RADIAN);

    auto unit2b = create<typename Schema::IfcMeasureWithUnit>();
    auto measure = create<typename Schema::IfcPlaneAngleMeasure>();
    measure.set_attribute_value(0, 0.01745329251);
    unit2b.setValueComponent(measure);
    unit2b.setUnitComponent(unit2a);

    auto unit2 = create<typename Schema::IfcConversionBasedUnit>();
    unit2.setDimensions(dimexp);
    unit2.setUnitType(Schema::IfcUnitEnum::IfcUnit_PLANEANGLEUNIT);
    unit2.setName("Degrees");
    unit2.setConversionFactor(unit2b);

    std::vector<typename Schema::IfcUnit> units = {unit1, unit2};
    auto unit_assignment = create<typename Schema::IfcUnitAssignment>();
    unit_assignment.setUnits(units);

    auto project = create<typename Schema::IfcProject>();
    project.setGlobalId(ifcopenshell::global_id());
    project.setOwnerHistory(owner_hist ? owner_hist : addOwnerHistory());
    project.setRepresentationContexts(rep_contexts);
    project.setUnitsInContext(unit_assignment);

    return project;
}

template <typename Schema>
void hierarchy_helper<Schema>::relatePlacements(typename Schema::IfcProduct parent, typename Schema::IfcProduct product) {
    typename Schema::IfcObjectPlacement place = product.ObjectPlacement();
    if (place) {
        if (auto local_place = place.template as<typename Schema::IfcLocalPlacement>()) {
            if (parent.ObjectPlacement()) {
                if (local_place != parent.ObjectPlacement()) {
                    local_place.setPlacementRelTo(parent.ObjectPlacement());
                } else {
                    ifcopenshell::logger::root().notice("Placement cannot be relative to self");
                }
            }
        }
    }
}

template <typename Schema>
typename Schema::IfcSite hierarchy_helper<Schema>::addSite(typename Schema::IfcProject proj, typename Schema::IfcOwnerHistory owner_hist) {
    if (!owner_hist) {
        owner_hist = getSingle<typename Schema::IfcOwnerHistory>();
    }
    if (!owner_hist) {
        owner_hist = addOwnerHistory();
    }
    if (!proj) {
        proj = getSingle<typename Schema::IfcProject>();
    }
    if (!proj) {
        proj = addProject(owner_hist);
    }

    auto site = create<typename Schema::IfcSite>();
    site.setGlobalId(ifcopenshell::global_id());
    site.setOwnerHistory(owner_hist);
    site.setObjectPlacement(addLocalPlacement());
    site.setCompositionType(Schema::IfcElementCompositionEnum::IfcElementComposition_ELEMENT);

    addRelatedObject<typename Schema::IfcRelAggregates>(proj, site, owner_hist);
    return site;
}

template <typename Schema>
typename Schema::IfcBuilding hierarchy_helper<Schema>::addBuilding(typename Schema::IfcSite site, typename Schema::IfcOwnerHistory owner_hist) {
    if (!owner_hist) {
        owner_hist = getSingle<typename Schema::IfcOwnerHistory>();
    }
    if (!owner_hist) {
        owner_hist = addOwnerHistory();
    }
    if (!site) {
        site = getSingle<typename Schema::IfcSite>();
    }
    if (!site) {
        site = addSite(typename Schema::IfcProject{}, owner_hist);
    }

    auto building = create<typename Schema::IfcBuilding>();
    building.setGlobalId(ifcopenshell::global_id());
    building.setOwnerHistory(owner_hist);
    building.setObjectPlacement(addLocalPlacement());
    building.setCompositionType(Schema::IfcElementCompositionEnum::IfcElementComposition_ELEMENT);

    addRelatedObject<typename Schema::IfcRelAggregates>(site, building, owner_hist);
    relatePlacements(site, building);

    return building;
}

template <typename Schema>
typename Schema::IfcBuildingStorey hierarchy_helper<Schema>::addBuildingStorey(typename Schema::IfcBuilding building,
                                                                                  typename Schema::IfcOwnerHistory owner_hist) {
    if (!owner_hist) {
        owner_hist = getSingle<typename Schema::IfcOwnerHistory>();
    }
    if (!owner_hist) {
        owner_hist = addOwnerHistory();
    }
    if (!building) {
        building = getSingle<typename Schema::IfcBuilding>();
    }
    if (!building) {
        building = addBuilding(typename Schema::IfcSite{}, owner_hist);
    }

    auto storey = create<typename Schema::IfcBuildingStorey>();
    storey.setGlobalId(ifcopenshell::global_id());
    storey.setOwnerHistory(owner_hist);
    storey.setObjectPlacement(addLocalPlacement());
    storey.setCompositionType(Schema::IfcElementCompositionEnum::IfcElementComposition_ELEMENT);

    addRelatedObject<typename Schema::IfcRelAggregates>(building, storey, owner_hist);
    relatePlacements(building, storey);

    return storey;
}

template <typename Schema>
typename Schema::IfcBuildingStorey hierarchy_helper<Schema>::addBuildingProduct(typename Schema::IfcProduct product,
                                                                                   typename Schema::IfcBuildingStorey storey,
                                                                                   typename Schema::IfcOwnerHistory owner_hist) {
    if (!owner_hist) {
        owner_hist = getSingle<typename Schema::IfcOwnerHistory>();
    }
    if (!owner_hist) {
        owner_hist = addOwnerHistory();
    }
    if (!storey) {
        storey = getSingle<typename Schema::IfcBuildingStorey>();
    }
    if (!storey) {
        storey = addBuildingStorey(typename Schema::IfcBuilding{}, owner_hist);
    }

    // CV-2x3-158: Don't add decompositions directly to a building storey
    const bool is_decomposition = !product.Decomposes().empty();

    if (!is_decomposition) {
        addRelatedObject<typename Schema::IfcRelContainedInSpatialStructure>(storey, product, owner_hist);
        relatePlacements(storey, product);
    }
    return storey;
}

template <typename Schema>
void hierarchy_helper<Schema>::addExtrudedPolyline(typename Schema::IfcShapeRepresentation rep,
                                                     const std::vector<std::pair<double, double>>& points,
                                                     double h,
                                                     typename Schema::IfcAxis2Placement2D /*place1*/,
                                                     typename Schema::IfcAxis2Placement3D place2,
                                                     typename Schema::IfcDirection dir,
                                                     typename Schema::IfcRepresentationContext /*context*/)
{
    std::vector<typename Schema::IfcCartesianPoint> cartesian_points;
    for (auto& i : points) {
        cartesian_points.push_back(addDoublet<typename Schema::IfcCartesianPoint>(i.first, i.second));
    }
    if (!cartesian_points.empty()) {
        cartesian_points.push_back(cartesian_points.front());
    }

    auto line = create<typename Schema::IfcPolyline>();
    line.setPoints(cartesian_points);

    auto profile = create<typename Schema::IfcArbitraryClosedProfileDef>();
    profile.setProfileType(Schema::IfcProfileTypeEnum::IfcProfileType_AREA);
    profile.setOuterCurve(line);

    auto solid = create<typename Schema::IfcExtrudedAreaSolid>();
    solid.setSweptArea(profile);
    solid.setPosition(place2 ? place2 : addPlacement3d());
    solid.setExtrudedDirection(dir ? dir : addTriplet<typename Schema::IfcDirection>(0, 0, 1));
    solid.setDepth(h);

    std::vector<typename Schema::IfcRepresentationItem> items;
    try {
        auto existing_items = rep.Items();
        items.insert(items.end(), existing_items.begin(), existing_items.end());
    } catch (...) {
        // ignore
    }
    items.push_back(solid);
    rep.setItems(items);
}

template <typename Schema>
typename Schema::IfcProductDefinitionShape hierarchy_helper<Schema>::addExtrudedPolyline(const std::vector<std::pair<double, double>>& points,
                                                                                            double h,
                                                                                            typename Schema::IfcAxis2Placement2D place,
                                                                                            typename Schema::IfcAxis2Placement3D place2,
                                                                                            typename Schema::IfcDirection dir,
                                                                                            typename Schema::IfcRepresentationContext context) {
    auto rep = create<typename Schema::IfcShapeRepresentation>();
    rep.setContextOfItems(context ? context : getRepresentationContext("Model"));
    rep.setRepresentationIdentifier(std::string("Body"));
    rep.setRepresentationType(std::string("SweptSolid"));
    rep.setItems(std::vector<typename Schema::IfcRepresentationItem>{});

    auto shape = create<typename Schema::IfcProductDefinitionShape>();
    shape.setRepresentations(std::vector<typename Schema::IfcRepresentation>{rep});
    addExtrudedPolyline(rep, points, h, place, place2, dir, context);

    return shape;
}

template <typename Schema>
void hierarchy_helper<Schema>::addBox(typename Schema::IfcShapeRepresentation rep,
                                        double w,
                                        double d,
                                        double h,
                                        typename Schema::IfcAxis2Placement2D place,
                                        typename Schema::IfcAxis2Placement3D place2,
                                        typename Schema::IfcDirection dir,
                                        typename Schema::IfcRepresentationContext context)
{
    std::vector<std::pair<double, double>> points;
    points.push_back(std::make_pair(-w / 2, -d / 2));
    points.push_back(std::make_pair(w / 2, -d / 2));
    points.push_back(std::make_pair(w / 2, d / 2));
    points.push_back(std::make_pair(-w / 2, d / 2));
    // The call to addExtrudedPolyline() closes the polyline
    addExtrudedPolyline(rep, points, h, place, place2, dir, context);
}

template <typename Schema>
void hierarchy_helper<Schema>::addAxis(
    typename Schema::IfcShapeRepresentation rep,
    double l,
    typename Schema::IfcRepresentationContext /*context*/)
{
    auto p1 = addDoublet<typename Schema::IfcCartesianPoint>(-l / 2., 0.);
    auto p2 = addDoublet<typename Schema::IfcCartesianPoint>(+l / 2., 0.);
    std::vector<typename Schema::IfcCartesianPoint> pts{p1, p2};

    auto poly = create<typename Schema::IfcPolyline>();
    poly.setPoints(pts);

    auto items = rep.Items();
    items.push_back(poly);
    rep.setItems(items);
}

template <typename Schema>
typename Schema::IfcProductDefinitionShape hierarchy_helper<Schema>::addBox(double w,
                                                                               double d,
                                                                               double h,
                                                                               typename Schema::IfcAxis2Placement2D place,
                                                                               typename Schema::IfcAxis2Placement3D place2,
                                                                               typename Schema::IfcDirection dir,
                                                                               typename Schema::IfcRepresentationContext context) {
    typename Schema::IfcShapeRepresentation rep = create<typename Schema::IfcShapeRepresentation>();
    rep.setContextOfItems(context ? context : getRepresentationContext("Model"));
    rep.setRepresentationIdentifier(std::string("Body"));
    rep.setRepresentationType(std::string("SweptSolid"));
    rep.setItems(std::vector<typename Schema::IfcRepresentationItem>{});

    auto shape = create<typename Schema::IfcProductDefinitionShape>();
    shape.setRepresentations(std::vector<typename Schema::IfcRepresentation>{rep});

    addBox(rep, w, d, h, place, place2, dir, context);
    return shape;
}

template <typename Schema>
typename Schema::IfcProductDefinitionShape hierarchy_helper<Schema>::addAxisBox(
    double w, double d, double h, typename Schema::IfcRepresentationContext context) {
    auto body_rep = create<typename Schema::IfcShapeRepresentation>();
    body_rep.setContextOfItems(context ? context : getRepresentationContext("Model"));
    body_rep.setRepresentationIdentifier(std::string("Body"));
    body_rep.setRepresentationType(std::string("SweptSolid"));
    body_rep.setItems(std::vector<typename Schema::IfcRepresentationItem>{});

    auto axis_rep = create<typename Schema::IfcShapeRepresentation>();
    axis_rep.setContextOfItems(context ? context : getRepresentationContext("Plan"));
    axis_rep.setRepresentationIdentifier(std::string("Axis"));
    axis_rep.setRepresentationType(std::string("Curve2D"));
    axis_rep.setItems(std::vector<typename Schema::IfcRepresentationItem>{});

    auto shape = create<typename Schema::IfcProductDefinitionShape>();
    shape.setRepresentations(std::vector<typename Schema::IfcRepresentation>{axis_rep, body_rep});

    addBox(body_rep, w, d, h, typename Schema::IfcAxis2Placement2D{}, typename Schema::IfcAxis2Placement3D{}, typename Schema::IfcDirection{}, context);
    addAxis(axis_rep, w);

    return shape;
}

template <typename Schema>
void hierarchy_helper<Schema>::clipRepresentation(typename Schema::IfcProductRepresentation shape,
                                                    typename Schema::IfcAxis2Placement3D place,
                                                    bool agree) {
    auto reps = shape.Representations();
    for (auto& rep : reps) {
        clipRepresentation(rep, place, agree);
    }
}

template <typename Schema>
void hierarchy_helper<Schema>::clipRepresentation(typename Schema::IfcRepresentation rep,
                                                    typename Schema::IfcAxis2Placement3D place,
                                                    bool agree) {
    if (!rep.RepresentationIdentifier() || *rep.RepresentationIdentifier() != "Body") {
        return;
    }

    auto plane = create<typename Schema::IfcPlane>();
    plane.setPosition(place);
    auto half_space = create<typename Schema::IfcHalfSpaceSolid>();
    half_space.setBaseSurface(plane);
    half_space.setAgreementFlag(agree);

    rep.setRepresentationType("Clipping"s);
    auto items = rep.Items();
    decltype(items) new_items;
    for (auto& item : items) {
        if (auto bop = item.template as<typename Schema::IfcBooleanOperand>()) {
            auto clip = create<typename Schema::IfcBooleanClippingResult>();
            clip.setOperator(Schema::IfcBooleanOperator::IfcBooleanOperator_DIFFERENCE);
            clip.setFirstOperand(bop);
            clip.setSecondOperand(half_space);
            new_items.push_back(clip);
        }
    }
    rep.setItems(new_items);
}

template <typename Schema>
typename Schema::IfcSurfaceStyle getSurfaceStyle(hierarchy_helper<Schema>& file, double r, double g, double b, double a = 1.0) {
    auto colour = file.template create<typename Schema::IfcColourRgb>();
    colour.setRed(r);
    colour.setGreen(g);
    colour.setBlue(b);

    auto rendering = file.template create<typename Schema::IfcSurfaceStyleRendering>();
    rendering.setSurfaceColour(colour);
    if (a != 1.0) {
        rendering.setTransparency(1.0 - a);
    }
    rendering.setReflectanceMethod(Schema::IfcReflectanceMethodEnum::IfcReflectanceMethod_FLAT);

    auto surface_style = file.template create<typename Schema::IfcSurfaceStyle>();
    surface_style.setSide(Schema::IfcSurfaceSide::IfcSurfaceSide_BOTH);
    surface_style.setStyles(std::vector<typename Schema::IfcSurfaceStyleElementSelect>{rendering});

    return surface_style;
}

template <typename Schema>
ifcopenshell::hierarchy_detail::surface_style_type<Schema>
addStyleAssignment(hierarchy_helper<Schema>& file, double r, double g, double b, double a) {
    auto surface_style = getSurfaceStyle<Schema>(file, r, g, b, a);
    if constexpr (ifcopenshell::hierarchy_detail::styled_item_accepts_presentation_style<Schema>::value) {
        return surface_style;
    } else {
        auto style_assignment = file.template create<typename Schema::IfcPresentationStyleAssignment>();
        style_assignment.setStyles(std::vector<typename Schema::IfcPresentationStyleSelect>{surface_style});
        return style_assignment;
    }
}

namespace {
template <typename Schema, typename = void>
struct styled_item_accepts_style_assignment_select : std::false_type {};

template <typename Schema>
struct styled_item_accepts_style_assignment_select<Schema,
    std::void_t<typename Schema::IfcStyleAssignmentSelect>> : std::true_type {};

template <typename Schema>
typename Schema::IfcStyledItem create_styled_item(
    ifcopenshell::file* file,
    const typename Schema::IfcRepresentationItem& item,
    const ifcopenshell::hierarchy_detail::surface_style_type<Schema>& style) {
    auto sitem = file->template create<typename Schema::IfcStyledItem>();
    sitem.setItem(item);
    if constexpr (ifcopenshell::hierarchy_detail::styled_item_accepts_presentation_style<Schema>::value) {
        sitem.setStyles(std::vector<typename Schema::IfcPresentationStyle>{style});
    } else if constexpr (styled_item_accepts_style_assignment_select<Schema>::value) {
        sitem.setStyles(std::vector<typename Schema::IfcStyleAssignmentSelect>{style});
    } else {
        sitem.setStyles(std::vector<typename Schema::IfcPresentationStyleAssignment>{style});
    }
    return sitem;
}
} // namespace

template <typename Schema>
ifcopenshell::hierarchy_detail::surface_style_type<Schema>
setSurfaceColour(hierarchy_helper<Schema>& file,
                 const typename Schema::IfcProductRepresentation& shape,
                 double r,
                 double g,
                 double b,
                 double a) {
    auto style = addStyleAssignment<Schema>(file, r, g, b, a);
    setSurfaceColour(file, shape, style);
    return style;
}

template <typename Schema>
ifcopenshell::hierarchy_detail::surface_style_type<Schema>
setSurfaceColour(hierarchy_helper<Schema>& file,
                 const typename Schema::IfcRepresentation& shape,
                 double r,
                 double g,
                 double b,
                 double a) {
    auto style = addStyleAssignment<Schema>(file, r, g, b, a);
    setSurfaceColour(file, shape, style);
    return style;
}

template <typename Schema>
void setSurfaceColour(
    hierarchy_helper<Schema>& file,
    const typename Schema::IfcProductRepresentation& shape,
    const ifcopenshell::hierarchy_detail::surface_style_type<Schema>& style) {
    auto reps = shape.Representations();
    for (auto& rep : reps) {
        setSurfaceColour(file, rep, style);
    }
}

template <typename Schema>
void setSurfaceColour(
    hierarchy_helper<Schema>& file,
    const typename Schema::IfcRepresentation& rep,
    const ifcopenshell::hierarchy_detail::surface_style_type<Schema>& style) {
    auto items = rep.Items();
    for (auto& item : items) {
        create_styled_item<Schema>(&file, item, style);
    }
}

template <typename Schema>
typename Schema::IfcProductDefinitionShape hierarchy_helper<Schema>::addMappedItem(
    typename Schema::IfcShapeRepresentation rep,
    typename Schema::IfcCartesianTransformationOperator3D transform,
    typename Schema::IfcProductDefinitionShape def)
{
    auto maps = rep.RepresentationMap();
    typename Schema::IfcRepresentationMap map;
    if (maps.size() == 1) {
        map = maps.front();
    } else {
        map = create<typename Schema::IfcRepresentationMap>();
        map.setMappingOrigin(addPlacement3d());
        map.setMappedRepresentation(rep);
    }

    std::vector<typename Schema::IfcRepresentation> representations;
    if (def) {
        representations = def.Representations();
    }

    if (!transform) {
        transform = create<typename Schema::IfcCartesianTransformationOperator3D>();
        transform.setLocalOrigin(addTriplet<typename Schema::IfcCartesianPoint>(0, 0, 0));
    }
    auto item = create<typename Schema::IfcMappedItem>();
    item.setMappingSource(map);
    item.setMappingTarget(transform);

    auto new_rep = create<typename Schema::IfcShapeRepresentation>();
    new_rep.setContextOfItems(rep.ContextOfItems());
    new_rep.setRepresentationType(std::string("MappedRepresentation"));
    new_rep.setItems(std::vector<typename Schema::IfcRepresentationItem>{item});

    if (rep.RepresentationIdentifier()) {
        new_rep.setRepresentationIdentifier(rep.RepresentationIdentifier());
    }

    representations.push_back(new_rep);

    if (!def) {
        def = create<typename Schema::IfcProductDefinitionShape>();
        def.setRepresentations(representations);
    } else {
        def.setRepresentations(representations);
    }

    return def;
}

template <typename Schema>
typename Schema::IfcProductDefinitionShape hierarchy_helper<Schema>::addMappedItem(
    std::vector<typename Schema::IfcShapeRepresentation>& reps,
    typename Schema::IfcCartesianTransformationOperator3D transform)
{
    typename Schema::IfcProductDefinitionShape def;
    for (auto& r : reps) {
        def = addMappedItem(r, transform, def);
    }
    return def;
}

template <typename Schema>
typename Schema::IfcShapeRepresentation hierarchy_helper<Schema>::addEmptyRepresentation(const std::string& repid, const std::string& reptype) {
    auto shape_rep = create<typename Schema::IfcShapeRepresentation>();
    shape_rep.setContextOfItems(getRepresentationContext(reptype == "Curve2D" ? "Plan" : "Model"));
    shape_rep.setRepresentationIdentifier(repid);
    shape_rep.setRepresentationType(reptype);
    shape_rep.setItems(std::vector<typename Schema::IfcRepresentationItem>{});
    add_entity(shape_rep);
    return shape_rep;
}

namespace {
template <typename T, typename U>
void push_back_to_maybe_optional(T& t, const U& u) {
    t.push_back(u);
}

// In IFC4 the IfcContext.RepresentationContexts has been made optional, so we need
// some boiler plate to push back to a list that might be optional.
template <typename T, typename U>
void push_back_to_maybe_optional(std::optional<std::vector<T>>& t, const U& u) {
    if (!t) {
        t.emplace();
    }
    t->push_back(u);
}
} // namespace

template <typename Schema>
typename Schema::IfcGeometricRepresentationContext hierarchy_helper<Schema>::getRepresentationContext(const std::string& s) {
    auto iter = contexts_.find(s);
    if (iter != contexts_.end()) {
        return iter->second;
    }
    auto project = getSingle<typename Schema::IfcProject>();
    if (!project) {
        project = addProject();
    }
    auto project_contexts = project.RepresentationContexts();
    auto context = create<typename Schema::IfcGeometricRepresentationContext>();
    context.setContextIdentifier(s);
    context.setCoordinateSpaceDimension(3);
    context.setPrecision(1.e-5);
    context.setWorldCoordinateSystem(addPlacement3d());
    context.setTrueNorth(addDoublet<typename Schema::IfcDirection>(0, 1));

    push_back_to_maybe_optional(project_contexts, context);
    project.setRepresentationContexts(project_contexts);

    return contexts_[s] = context;
}

template <typename Schema>
typename Schema::IfcGeometricRepresentationSubContext hierarchy_helper<Schema>::getRepresentationSubContext(const std::string& ident, const std::string& type) {
    auto geometric_representation_context = getRepresentationContext(type); // creates the representation context if it doesn't already exist

    // search for a subcontext that matches the ContextIdentifier
    auto subcontexts = geometric_representation_context.HasSubContexts();
    typename Schema::IfcGeometricRepresentationSubContext rep_subcontext;
    for (auto subcontext : subcontexts) {
        if (subcontext.ContextIdentifier().value_or("") == ident) {
            rep_subcontext = subcontext;
            break; // found it, break out of the loop
        }
    }

    if (!rep_subcontext) {
        // didn't find the subcontext, create it
        rep_subcontext = create<typename Schema::IfcGeometricRepresentationSubContext>();
        rep_subcontext.setContextIdentifier(ident);
        rep_subcontext.setContextType(type);
        rep_subcontext.setParentContext(geometric_representation_context);
        rep_subcontext.setTargetView(Schema::IfcGeometricProjectionEnum::IfcGeometricProjection_MODEL_VIEW);
    }

    return rep_subcontext;
}

template class IFC_SCHEMA_API hierarchy_helper<IfcSchema>;

template IFC_SCHEMA_API ifcopenshell::hierarchy_detail::surface_style_type<IfcSchema>
addStyleAssignment<IfcSchema>(hierarchy_helper<IfcSchema>&, double, double, double, double);

template IFC_SCHEMA_API ifcopenshell::hierarchy_detail::surface_style_type<IfcSchema>
setSurfaceColour<IfcSchema>(
    hierarchy_helper<IfcSchema>&,
    const IfcSchema::IfcProductRepresentation&,
    double,
    double,
    double,
    double);

template IFC_SCHEMA_API ifcopenshell::hierarchy_detail::surface_style_type<IfcSchema>
setSurfaceColour<IfcSchema>(
    hierarchy_helper<IfcSchema>&,
    const IfcSchema::IfcRepresentation&,
    double,
    double,
    double,
    double);

template IFC_SCHEMA_API void setSurfaceColour<IfcSchema>(
    hierarchy_helper<IfcSchema>&,
    const IfcSchema::IfcProductRepresentation&,
    const ifcopenshell::hierarchy_detail::surface_style_type<IfcSchema>&);

template IFC_SCHEMA_API void setSurfaceColour<IfcSchema>(
    hierarchy_helper<IfcSchema>&,
    const IfcSchema::IfcRepresentation&,
    const ifcopenshell::hierarchy_detail::surface_style_type<IfcSchema>&);
