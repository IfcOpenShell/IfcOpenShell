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
 * This class is a subclass of the regular IfcFile class that implements        *
 * several convenience functions for creating geometrical representations and   *
 * spatial containers.                                                          *
 *                                                                              *
 ********************************************************************************/

#include "IfcHierarchyHelper.h"

#include <time.h>

using namespace std::string_literals;

template <typename Schema>
typename Schema::IfcAxis2Placement3D IfcHierarchyHelper<Schema>::addPlacement3d(
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
typename Schema::IfcAxis2Placement2D IfcHierarchyHelper<Schema>::addPlacement2d(
    double ox, double oy, double xx, double xy) {
    auto x = addDoublet<typename Schema::IfcDirection>(xx, xy);
    auto o = addDoublet<typename Schema::IfcCartesianPoint>(ox, oy);
    auto p2d = create<typename Schema::IfcAxis2Placement2D>();
    p2d.setLocation(o);
    p2d.setRefDirection(x);
    return p2d;
}

template <typename Schema>
typename Schema::IfcLocalPlacement IfcHierarchyHelper<Schema>::addLocalPlacement(typename Schema::IfcObjectPlacement parent,
                                                                                  double ox,
                                                                                  double oy,
                                                                                  double oz,
                                                                                  double zx,
                                                                                  double zy,
                                                                                  double zz,
                                                                                  double xx,
                                                                                  double xy,
                                                                                  double xz) {
    auto local_placement = create<Schema::IfcLocalPlacement>();
    if (parent) {
        local_placement.setPlacementRelTo(parent);
    }
    local_placement.setRelativePlacement(addPlacement3d(ox, oy, oz, zx, zy, zz, xx, xy, xz));
    return local_placement;
}

template <typename Schema>
typename Schema::IfcOwnerHistory IfcHierarchyHelper<Schema>::addOwnerHistory() {
    typename Schema::IfcPerson person = create<Schema::IfcPerson>();
    person.setIdentification("");

    auto organization = create<Schema::IfcOrganization>();
    organization.setName("IfcOpenShell");

    auto person_and_org = create<Schema::IfcPersonAndOrganization>();
    person_and_org.setThePerson(person);
    person_and_org.setTheOrganization(organization);

    auto application = create<Schema::IfcApplication>();
    application.setApplicationDeveloper(organization);
    application.setVersion(IFCOPENSHELL_VERSION);
    application.setApplicationFullName("IfcOpenShell");
    application.setApplicationIdentifier("IfcOpenShell");

    int timestamp = (int)time(0);
    auto owner_hist = create<Schema::IfcOwnerHistory>();
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
typename Schema::IfcProject IfcHierarchyHelper<Schema>::addProject(typename Schema::IfcOwnerHistory owner_hist) {
    std::vector<typename Schema::IfcRepresentationContext> rep_contexts;

    auto dimexp = create<Schema::IfcDimensionalExponents>();
    dimexp.setLengthExponent(0);
    dimexp.setMassExponent(0);
    dimexp.setTimeExponent(0);
    dimexp.setElectricCurrentExponent(0);
    dimexp.setThermodynamicTemperatureExponent(0);
    dimexp.setAmountOfSubstanceExponent(0);
    dimexp.setLuminousIntensityExponent(0);

    auto unit1 = create<Schema::IfcSIUnit>();
    unit1.setUnitType(Schema::IfcUnitEnum::IfcUnit_LENGTHUNIT);
    unit1.setPrefix(Schema::IfcSIPrefix::IfcSIPrefix_MILLI);
    unit1.setName(Schema::IfcSIUnitName::IfcSIUnitName_METRE);

    auto unit2a = create<Schema::IfcSIUnit>();
    unit2a.setUnitType(Schema::IfcUnitEnum::IfcUnit_PLANEANGLEUNIT);
    unit2a.setName(Schema::IfcSIUnitName::IfcSIUnitName_RADIAN);

    auto unit2b = create<Schema::IfcMeasureWithUnit>();
    auto measure = create<Schema::IfcPlaneAngleMeasure>();
    measure.set_attribute_value(0, 0.01745329251);
    unit2b.setValueComponent(measure);
    unit2b.setUnitComponent(unit2a);

    auto unit2 = create<Schema::IfcConversionBasedUnit>();
    unit2.setDimensions(dimexp);
    unit2.setUnitType(Schema::IfcUnitEnum::IfcUnit_PLANEANGLEUNIT);
    unit2.setName("Degrees");
    unit2.setConversionFactor(unit2b);
    
    std::vector<typename Schema::IfcUnit> units = {unit1, unit2};
    auto unit_assignment = create<Schema::IfcUnitAssignment>();
    unit_assignment.setUnits(units);

    auto project = create<Schema::IfcProject>();
    project.setGlobalId(IfcParse::IfcGlobalId());
    project.setOwnerHistory(owner_hist ? owner_hist : addOwnerHistory());
    project.setRepresentationContexts(rep_contexts);
    project.setUnitsInContext(unit_assignment);

    return project;
}

template <typename Schema>
void IfcHierarchyHelper<Schema>::relatePlacements(typename Schema::IfcProduct parent, typename Schema::IfcProduct product) {
    typename Schema::IfcObjectPlacement place = product.ObjectPlacement();
    if (place) {
        if (auto local_place = place.as<typename Schema::IfcLocalPlacement>()) {
            if (parent.ObjectPlacement()) {
                if (local_place != parent.ObjectPlacement()) {
                    local_place.setPlacementRelTo(parent.ObjectPlacement());
                } else {
                    Logger::Notice("Placement cannot be relative to self");
                }
            }
        }
    }
}

template <typename Schema>
typename Schema::IfcSite IfcHierarchyHelper<Schema>::addSite(typename Schema::IfcProject proj, typename Schema::IfcOwnerHistory owner_hist) {
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

    auto site = create<Schema::IfcSite>();
    site.setGlobalId(IfcParse::IfcGlobalId());
    site.setOwnerHistory(owner_hist);
    site.setObjectPlacement(addLocalPlacement());
    site.setCompositionType(Schema::IfcElementCompositionEnum::IfcElementComposition_ELEMENT);

    addRelatedObject<typename Schema::IfcRelAggregates>(proj, site, owner_hist);
    return site;
}

template <typename Schema>
typename Schema::IfcBuilding IfcHierarchyHelper<Schema>::addBuilding(typename Schema::IfcSite site, typename Schema::IfcOwnerHistory owner_hist) {
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

    auto building = create<Schema::IfcBuilding>();
    building.setGlobalId(IfcParse::IfcGlobalId());
    building.setOwnerHistory(owner_hist);
    building.setObjectPlacement(addLocalPlacement());
    building.setCompositionType(Schema::IfcElementCompositionEnum::IfcElementComposition_ELEMENT);

    addRelatedObject<typename Schema::IfcRelAggregates>(site, building, owner_hist);
    relatePlacements(site, building);

    return building;
}

template <typename Schema>
typename Schema::IfcBuildingStorey IfcHierarchyHelper<Schema>::addBuildingStorey(typename Schema::IfcBuilding building,
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

    auto storey = create<Schema::IfcBuildingStorey>();
    storey.setGlobalId(IfcParse::IfcGlobalId());
    storey.setOwnerHistory(owner_hist);
    storey.setObjectPlacement(addLocalPlacement());
    storey.setCompositionType(Schema::IfcElementCompositionEnum::IfcElementComposition_ELEMENT);

    addRelatedObject<typename Schema::IfcRelAggregates>(building, storey, owner_hist);
    relatePlacements(building, storey);

    return storey;
}

template <typename Schema>
typename Schema::IfcBuildingStorey IfcHierarchyHelper<Schema>::addBuildingProduct(typename Schema::IfcProduct product,
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
void IfcHierarchyHelper<Schema>::addExtrudedPolyline(typename Schema::IfcShapeRepresentation rep,
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

    auto line = create<Schema::IfcPolyline>();
    line.setPoints(cartesian_points);

    auto profile = create<Schema::IfcArbitraryClosedProfileDef>();
    profile.setProfileType(Schema::IfcProfileTypeEnum::IfcProfileType_AREA);
    profile.setOuterCurve(line);

    auto solid = create<Schema::IfcExtrudedAreaSolid>();
    solid.setSweptArea(profile);
    solid.setPosition(place2 ? place2 : addPlacement3d());
    solid.setExtrudedDirection(dir ? dir : addTriplet<typename Schema::IfcDirection>(0, 0, 1));
    
    // @nb this overwrites, not appends
    rep.setItems(std::vector<typename Schema::IfcRepresentationItem>{solid});
}

template <typename Schema>
typename Schema::IfcProductDefinitionShape IfcHierarchyHelper<Schema>::addExtrudedPolyline(const std::vector<std::pair<double, double>>& points,
                                                                                            double h,
                                                                                            typename Schema::IfcAxis2Placement2D place,
                                                                                            typename Schema::IfcAxis2Placement3D place2,
                                                                                            typename Schema::IfcDirection dir,
                                                                                            typename Schema::IfcRepresentationContext context) {
    auto rep = create<Schema::IfcShapeRepresentation>();
    rep.setContextOfItems(context ? context : getRepresentationContext("Model"));
    rep.setRepresentationIdentifier(std::string("Body"));
    rep.setRepresentationType(std::string("SweptSolid"));
    rep.setItems(std::vector<typename Schema::IfcRepresentationItem>{});

    auto shape = create<Schema::IfcProductDefinitionShape>();
    shape.setRepresentations(std::vector<typename Schema::IfcRepresentation>{rep});
    addExtrudedPolyline(rep, points, h, place, place2, dir, context);

    return shape;
}

template <typename Schema>
void IfcHierarchyHelper<Schema>::addBox(typename Schema::IfcShapeRepresentation rep,
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
void IfcHierarchyHelper<Schema>::addAxis(
    typename Schema::IfcShapeRepresentation rep,
    double l,
    typename Schema::IfcRepresentationContext /*context*/) 
{
    auto p1 = addDoublet<typename Schema::IfcCartesianPoint>(-l / 2., 0.);
    auto p2 = addDoublet<typename Schema::IfcCartesianPoint>(+l / 2., 0.);
    std::vector<Schema::IfcCartesianPoint> pts{p1, p2};

    auto poly = create<Schema::IfcPolyline>();
    poly.setPoints(pts);

    auto items = rep.Items();
    items.push_back(poly);
    rep.setItems(items);
}

template <typename Schema>
typename Schema::IfcProductDefinitionShape IfcHierarchyHelper<Schema>::addBox(double w,
                                                                               double d,
                                                                               double h,
                                                                               typename Schema::IfcAxis2Placement2D place,
                                                                               typename Schema::IfcAxis2Placement3D place2,
                                                                               typename Schema::IfcDirection dir,
                                                                               typename Schema::IfcRepresentationContext context) {
    typename Schema::IfcShapeRepresentation rep = create<Schema::IfcShapeRepresentation>();
    rep.setContextOfItems(context ? context : getRepresentationContext("Model"));
    rep.setRepresentationIdentifier(std::string("Body"));
    rep.setRepresentationType(std::string("SweptSolid"));
    rep.setItems(std::vector<typename Schema::IfcRepresentationItem>{});

    auto shape = create<Schema::IfcProductDefinitionShape>();
    shape.setRepresentations(std::vector<typename Schema::IfcRepresentation>{rep});
    
    addBox(rep, w, d, h, place, place2, dir, context);
    return shape;
}

template <typename Schema>
typename Schema::IfcProductDefinitionShape IfcHierarchyHelper<Schema>::addAxisBox(
    double w, double d, double h, typename Schema::IfcRepresentationContext context) {
    auto body_rep = create<Schema::IfcShapeRepresentation>();
    body_rep.setContextOfItems(context ? context : getRepresentationContext("Model"));
    body_rep.setRepresentationIdentifier(std::string("Body"));
    body_rep.setRepresentationType(std::string("SweptSolid"));
    body_rep.setItems(std::vector<typename Schema::IfcRepresentationItem>{});

    auto axis_rep = create<Schema::IfcShapeRepresentation>();
    axis_rep.setContextOfItems(context ? context : getRepresentationContext("Plan"));
    axis_rep.setRepresentationIdentifier(std::string("Axis"));
    axis_rep.setRepresentationType(std::string("Curve2D"));
    axis_rep.setItems(std::vector<typename Schema::IfcRepresentationItem>{});

    auto shape = create<Schema::IfcProductDefinitionShape>();
    shape.setRepresentations(std::vector<typename Schema::IfcRepresentation>{axis_rep, body_rep});

    addBox(body_rep, w, d, h, typename Schema::IfcAxis2Placement2D{}, typename Schema::IfcAxis2Placement3D{}, typename Schema::IfcDirection{}, context);
    addAxis(axis_rep, w);

    return shape;
}

template <typename Schema>
void IfcHierarchyHelper<Schema>::clipRepresentation(typename Schema::IfcProductRepresentation shape,
                                                    typename Schema::IfcAxis2Placement3D place,
                                                    bool agree) {
    auto reps = shape.Representations();
    for (auto& rep : reps) {
        clipRepresentation(rep, place, agree);
    }
}

template <typename Schema>
void IfcHierarchyHelper<Schema>::clipRepresentation(typename Schema::IfcRepresentation rep,
                                                    typename Schema::IfcAxis2Placement3D place,
                                                    bool agree) {
    if (!rep.RepresentationIdentifier() || *rep.RepresentationIdentifier() != "Body") {
        return;
    }

    auto plane = create<Schema::IfcPlane>();
    plane.setPosition(place);
    auto half_space = create<Schema::IfcHalfSpaceSolid>();
    half_space.setBaseSurface(plane);
    half_space.setAgreementFlag(agree);

    rep.setRepresentationType("Clipping"s);
    auto items = rep.Items();
    decltype(items) new_items;
    for (auto& item : items) {
        if (auto bop = item.as<typename Schema::IfcBooleanOperand>()) {
            auto clip = create<Schema::IfcBooleanClippingResult>();
            clip.setOperator(Schema::IfcBooleanOperator::IfcBooleanOperator_DIFFERENCE);
            clip.setFirstOperand(bop);
            clip.setSecondOperand(half_space);
            new_items.push_back(clip);
        }
    }
    rep.setItems(new_items);
}

template <typename Schema>
typename Schema::IfcSurfaceStyle getSurfaceStyle(IfcHierarchyHelper<Schema>& file, double r, double g, double b, double a = 1.0) {
    auto colour = file.create<typename Schema::IfcColourRgb>();
    colour.setRed(r);
    colour.setGreen(g);
    colour.setBlue(b);

    auto rendering = file.create<typename Schema::IfcSurfaceStyleRendering>();
    rendering.setSurfaceColour(colour);
    if (a != 1.0) {
        rendering.setTransparency(1.0 - a);
    }
    rendering.setReflectanceMethod(Schema::IfcReflectanceMethodEnum::IfcReflectanceMethod_FLAT);

    auto surface_style = file.create<typename Schema::IfcSurfaceStyle>();
    surface_style.setSide(Schema::IfcSurfaceSide::IfcSurfaceSide_BOTH);
    surface_style.setStyles(std::vector<typename Schema::IfcSurfaceStyleElementSelect>{rendering});

    return surface_style;
}

template <typename Schema>
typename Schema::IfcPresentationStyleAssignment addStyleAssignment_2x3(IfcHierarchyHelper<Schema>& file, double r, double g, double b, double a = 1.0) {
    auto surface_style = getSurfaceStyle<Schema>(file, r, g, b, a);
    auto style_assignment = file.create<typename Schema::IfcPresentationStyleAssignment>();
    style_assignment.setStyles(std::vector<typename Schema::IfcPresentationStyleSelect>{surface_style});
    return style_assignment;
}

template <typename Schema>
typename Schema::IfcPresentationStyle addStyleAssignment_4x3(IfcHierarchyHelper<Schema>& file, double r, double g, double b, double a = 1.0) {
    return getSurfaceStyle<Schema>(file, r, g, b, a);
}

template <typename Schema>
typename Schema::IfcPresentationStyleAssignment setSurfaceColour_2x3(IfcHierarchyHelper<Schema>& file, typename Schema::IfcProductRepresentation shape, double r, double g, double b, double a) {
    typename Schema::IfcPresentationStyleAssignment style_assignment = addStyleAssignment_2x3(file, r, g, b, a);
    setSurfaceColour_2x3(file, shape, style_assignment);
    return style_assignment;
}

template <typename Schema>
typename Schema::IfcPresentationStyle setSurfaceColour_4x3(IfcHierarchyHelper<Schema>& file, typename Schema::IfcProductRepresentation shape, double r, double g, double b, double a) {
    typename Schema::IfcPresentationStyle style_assignment = addStyleAssignment_4x3(file, r, g, b, a);
    setSurfaceColour_4x3(file, shape, style_assignment);
    return style_assignment;
}

template <typename Schema>
typename Schema::IfcPresentationStyleAssignment setSurfaceColour_2x3(IfcHierarchyHelper<Schema>& file, typename Schema::IfcRepresentation shape, double r, double g, double b, double a) {
    typename Schema::IfcPresentationStyleAssignment style_assignment = addStyleAssignment_2x3(file, r, g, b, a);
    setSurfaceColour_2x3(file, shape, style_assignment);
    return style_assignment;
}

template <typename Schema>
typename Schema::IfcPresentationStyle setSurfaceColour_4x3(IfcHierarchyHelper<Schema>& file, typename Schema::IfcRepresentation shape, double r, double g, double b, double a) {
    typename Schema::IfcPresentationStyle style_assignment = addStyleAssignment_4x3(file, r, g, b, a);
    setSurfaceColour_4x3(file, shape, style_assignment);
    return style_assignment;
}

template <typename Schema>
void setSurfaceColour_2x3(IfcHierarchyHelper<Schema>& file, typename Schema::IfcProductRepresentation shape, typename Schema::IfcPresentationStyleAssignment style_assignment) {
    auto reps = shape->Representations();
    for (auto& rep : reps) {
        setSurfaceColour_2x3(file, rep, style_assignment);
    }
}

template <typename Schema>
void setSurfaceColour_4x3(IfcHierarchyHelper<Schema>& file, typename Schema::IfcProductRepresentation shape, typename Schema::IfcPresentationStyle style) {
    auto reps = shape.Representations();
    for (auto& rep : reps) {
        setSurfaceColour_4x3(file, rep, style);
    }
}

#ifdef HAS_SCHEMA_2x3
Ifc2x3::IfcStyledItem create_styled_item(IfcParse::IfcFile* file, Ifc2x3::IfcRepresentationItem item, Ifc2x3::IfcPresentationStyleAssignment style_assignment) {
    auto sitem = file->create<Ifc2x3::IfcStyledItem>();
    sitem.setItem(item);
    sitem.setStyles(std::vector<Ifc2x3::IfcPresentationStyleAssignment>{style_assignment});
    return sitem;
}
#endif

#ifdef HAS_SCHEMA_4
Ifc4::IfcStyledItem create_styled_item(IfcParse::IfcFile* file, Ifc4::IfcRepresentationItem item, Ifc4::IfcPresentationStyleAssignment style_assignment) {
    auto sitem = file->create<Ifc4::IfcStyledItem>();
    sitem.setItem(item);
    sitem.setStyles(std::vector<Ifc4::IfcPresentationStyleAssignment>{style_assignment});
    return sitem;
}
#endif

#ifdef HAS_SCHEMA_4x1
Ifc4x1::IfcStyledItem create_styled_item(IfcParse::IfcFile* file, Ifc4x1::IfcRepresentationItem item, Ifc4x1::IfcPresentationStyleAssignment style_assignment) {
    auto sitem = file->create<Ifc4x1::IfcStyledItem>();
    sitem.setItem(item);
    sitem.setStyles(std::vector<Ifc4x1::IfcPresentationStyleAssignment>{style_assignment});
    return sitem;
}
#endif

#ifdef HAS_SCHEMA_4x2
Ifc4x2::IfcStyledItem create_styled_item(IfcParse::IfcFile* file, Ifc4x2::IfcRepresentationItem item, Ifc4x2::IfcPresentationStyleAssignment style_assignment) {
    auto sitem = file->create<Ifc4x2::IfcStyledItem>();
    sitem.setItem(item);
    sitem.setStyles(std::vector<Ifc4x2::IfcPresentationStyleAssignment>{style_assignment});
    return sitem;
}
#endif

#ifdef HAS_SCHEMA_4x3_rc1
Ifc4x3_rc1::IfcStyledItem create_styled_item(IfcParse::IfcFile* file, Ifc4x3_rc1::IfcRepresentationItem item, Ifc4x3_rc1::IfcPresentationStyleAssignment style_assignment) {
    auto sitem = file->create<Ifc4x3_rc1::IfcStyledItem>();
    sitem.setItem(item);
    sitem.setStyles(std::vector<Ifc4x3_rc1::IfcPresentationStyleAssignment>{style_assignment});
    return sitem;
}
#endif

#ifdef HAS_SCHEMA_4x3_rc2
Ifc4x3_rc2::IfcStyledItem create_styled_item(IfcParse::IfcFile* file, Ifc4x3_rc2::IfcRepresentationItem item, Ifc4x3_rc2::IfcPresentationStyleAssignment style_assignment) {
    auto sitem = file->create<Ifc4x3_rc2::IfcStyledItem>();
    sitem.setItem(item);
    sitem.setStyles(std::vector<Ifc4x3_rc2::IfcPresentationStyleAssignment>{style_assignment});
    return sitem;
}
#endif

#ifdef HAS_SCHEMA_4x3_rc3
Ifc4x3_rc3::IfcStyledItem create_styled_item(IfcParse::IfcFile* file, Ifc4x3_rc3::IfcRepresentationItem item, Ifc4x3_rc3::IfcPresentationStyle style) {
    auto sitem = file->create<Ifc4x3_rc3::IfcStyledItem>();
    sitem.setItem(item);
    sitem.setStyles(std::vector<Ifc4x3_rc3::IfcPresentationStyle>{style});
    return sitem;
}
#endif

#ifdef HAS_SCHEMA_4x3_rc4
Ifc4x3_rc4::IfcStyledItem create_styled_item(IfcParse::IfcFile* file, Ifc4x3_rc4::IfcRepresentationItem item, Ifc4x3_rc4::IfcPresentationStyle style) {
    auto sitem = file->create<Ifc4x3_rc4::IfcStyledItem>();
    sitem.setItem(item);
    sitem.setStyles(std::vector<Ifc4x3_rc4::IfcPresentationStyle>{style});
    return sitem;
}
#endif

#ifdef HAS_SCHEMA_4x3
Ifc4x3::IfcStyledItem create_styled_item(IfcParse::IfcFile* file, Ifc4x3::IfcRepresentationItem item, Ifc4x3::IfcPresentationStyle style) {
    auto sitem = file->create<Ifc4x3::IfcStyledItem>();
    sitem.setItem(item);
    sitem.setStyles(std::vector<Ifc4x3::IfcPresentationStyle>{style});
    return sitem;
}
#endif

#ifdef HAS_SCHEMA_4x3_tc1
Ifc4x3_tc1::IfcStyledItem create_styled_item(IfcParse::IfcFile* file, Ifc4x3_tc1::IfcRepresentationItem item, Ifc4x3_tc1::IfcPresentationStyle style) {
    auto sitem = file.crefile->createate<Ifc4x3_tc1::IfcStyledItem>();
    sitem.setItem(item);
    sitem.setStyles(std::vector<Ifc4x3_tc1::IfcPresentationStyle>{style});
    return sitem;
}
#endif

#ifdef HAS_SCHEMA_4x3_add1
Ifc4x3_add1::IfcStyledItem create_styled_item(IfcParse::IfcFile* file, Ifc4x3_add1::IfcRepresentationItem item, Ifc4x3_add1::IfcPresentationStyle style) {
    auto sitem = file->create<Ifc4x3_add1::IfcStyledItem>();
    sitem.setItem(item);
    sitem.setStyles(std::vector<Ifc4x3_add1::IfcPresentationStyle>{style});
    return sitem;
}
#endif

#ifdef HAS_SCHEMA_4x3_add2
Ifc4x3_add2::IfcStyledItem create_styled_item(IfcParse::IfcFile* file, Ifc4x3_add2::IfcRepresentationItem item, Ifc4x3_add2::IfcPresentationStyle style) {
    auto sitem = file->create<Ifc4x3_add2::IfcStyledItem>();
    sitem.setItem(item);
    sitem.setStyles(std::vector<Ifc4x3_add2::IfcPresentationStyle>{style});
    return sitem;
}
#endif

template <typename Schema>
void setSurfaceColour_2x3(IfcHierarchyHelper<Schema>& file, typename Schema::IfcRepresentation rep, typename Schema::IfcPresentationStyleAssignment style_assignment) {
    auto items = rep.Items();
    for (auto& item : items) {
        create_styled_item(&file, item, style_assignment);
    }
}

template <typename Schema>
void setSurfaceColour_4x3(IfcHierarchyHelper<Schema>& file, typename Schema::IfcRepresentation rep, typename Schema::IfcPresentationStyle style) {
    // @todo is there still a difference here?
    auto items = rep.Items();
    for (auto& item : items) {
        create_styled_item(&file, item, style);
    }
}

#ifdef HAS_SCHEMA_2x3
Ifc2x3::IfcPresentationStyleAssignment addStyleAssignment(IfcHierarchyHelper<Ifc2x3>& file, double r, double g, double b, double a) {
    return addStyleAssignment_2x3(file, r, g, b, a);
}

Ifc2x3::IfcPresentationStyleAssignment setSurfaceColour(IfcHierarchyHelper<Ifc2x3>& file, Ifc2x3::IfcProductRepresentation shape, double r, double g, double b, double a) {
    return setSurfaceColour_2x3(file, shape, r, g, b, a);
}

Ifc2x3::IfcPresentationStyleAssignment setSurfaceColour(IfcHierarchyHelper<Ifc2x3>& file, Ifc2x3::IfcRepresentation shape, double r, double g, double b, double a) {
    return setSurfaceColour_2x3(file, shape, r, g, b, a);
}

void setSurfaceColour(IfcHierarchyHelper<Ifc2x3>& file, Ifc2x3::IfcProductRepresentation shape, Ifc2x3::IfcPresentationStyleAssignment style_assignment) {
    setSurfaceColour_2x3(file, shape, style_assignment);
}

void setSurfaceColour(IfcHierarchyHelper<Ifc2x3>& file, Ifc2x3::IfcRepresentation shape, Ifc2x3::IfcPresentationStyleAssignment style_assignment) {
    setSurfaceColour_2x3(file, shape, style_assignment);
}
#endif

#ifdef HAS_SCHEMA_4
Ifc4::IfcPresentationStyleAssignment addStyleAssignment(IfcHierarchyHelper<Ifc4>& file, double r, double g, double b, double a) {
    return addStyleAssignment_2x3(file, r, g, b, a);
}

Ifc4::IfcPresentationStyleAssignment setSurfaceColour(IfcHierarchyHelper<Ifc4>& file, Ifc4::IfcProductRepresentation shape, double r, double g, double b, double a) {
    return setSurfaceColour_2x3(file, shape, r, g, b, a);
}

Ifc4::IfcPresentationStyleAssignment setSurfaceColour(IfcHierarchyHelper<Ifc4>& file, Ifc4::IfcRepresentation shape, double r, double g, double b, double a) {
    return setSurfaceColour_2x3(file, shape, r, g, b, a);
}

void setSurfaceColour(IfcHierarchyHelper<Ifc4>& file, Ifc4::IfcProductRepresentation shape, Ifc4::IfcPresentationStyleAssignment style_assignment) {
    setSurfaceColour_2x3(file, shape, style_assignment);
}

void setSurfaceColour(IfcHierarchyHelper<Ifc4>& file, Ifc4::IfcRepresentation shape, Ifc4::IfcPresentationStyleAssignment style_assignment) {
    setSurfaceColour_2x3(file, shape, style_assignment);
}
#endif

#ifdef HAS_SCHEMA_4x1
Ifc4x1::IfcPresentationStyleAssignment addStyleAssignment(IfcHierarchyHelper<Ifc4x1>& file, double r, double g, double b, double a) {
    return addStyleAssignment_2x3(file, r, g, b, a);
}

Ifc4x1::IfcPresentationStyleAssignment setSurfaceColour(IfcHierarchyHelper<Ifc4x1>& file, Ifc4x1::IfcProductRepresentation shape, double r, double g, double b, double a) {
    return setSurfaceColour_2x3(file, shape, r, g, b, a);
}

Ifc4x1::IfcPresentationStyleAssignment setSurfaceColour(IfcHierarchyHelper<Ifc4x1>& file, Ifc4x1::IfcRepresentation shape, double r, double g, double b, double a) {
    return setSurfaceColour_2x3(file, shape, r, g, b, a);
}

void setSurfaceColour(IfcHierarchyHelper<Ifc4x1>& file, Ifc4x1::IfcProductRepresentation shape, Ifc4x1::IfcPresentationStyleAssignment style_assignment) {
    setSurfaceColour_2x3(file, shape, style_assignment);
}

void setSurfaceColour(IfcHierarchyHelper<Ifc4x1>& file, Ifc4x1::IfcRepresentation shape, Ifc4x1::IfcPresentationStyleAssignment style_assignment) {
    setSurfaceColour_2x3(file, shape, style_assignment);
}
#endif

#ifdef HAS_SCHEMA_4x2
Ifc4x2::IfcPresentationStyleAssignment addStyleAssignment(IfcHierarchyHelper<Ifc4x2>& file, double r, double g, double b, double a) {
    return addStyleAssignment_2x3(file, r, g, b, a);
}

Ifc4x2::IfcPresentationStyleAssignment setSurfaceColour(IfcHierarchyHelper<Ifc4x2>& file, Ifc4x2::IfcProductRepresentation shape, double r, double g, double b, double a) {
    return setSurfaceColour_2x3(file, shape, r, g, b, a);
}

Ifc4x2::IfcPresentationStyleAssignment setSurfaceColour(IfcHierarchyHelper<Ifc4x2>& file, Ifc4x2::IfcRepresentation shape, double r, double g, double b, double a) {
    return setSurfaceColour_2x3(file, shape, r, g, b, a);
}

void setSurfaceColour(IfcHierarchyHelper<Ifc4x2>& file, Ifc4x2::IfcProductRepresentation shape, Ifc4x2::IfcPresentationStyleAssignment style_assignment) {
    setSurfaceColour_2x3(file, shape, style_assignment);
}

void setSurfaceColour(IfcHierarchyHelper<Ifc4x2>& file, Ifc4x2::IfcRepresentation shape, Ifc4x2::IfcPresentationStyleAssignment style_assignment) {
    setSurfaceColour_2x3(file, shape, style_assignment);
}
#endif

#ifdef HAS_SCHEMA_4x3_rc1
Ifc4x3_rc1::IfcPresentationStyleAssignment addStyleAssignment(IfcHierarchyHelper<Ifc4x3_rc1>& file, double r, double g, double b, double a) {
    return addStyleAssignment_2x3(file, r, g, b, a);
}

Ifc4x3_rc1::IfcPresentationStyleAssignment setSurfaceColour(IfcHierarchyHelper<Ifc4x3_rc1>& file, Ifc4x3_rc1::IfcProductRepresentation shape, double r, double g, double b, double a) {
    return setSurfaceColour_2x3(file, shape, r, g, b, a);
}

Ifc4x3_rc1::IfcPresentationStyleAssignment setSurfaceColour(IfcHierarchyHelper<Ifc4x3_rc1>& file, Ifc4x3_rc1::IfcRepresentation shape, double r, double g, double b, double a) {
    return setSurfaceColour_2x3(file, shape, r, g, b, a);
}

void setSurfaceColour(IfcHierarchyHelper<Ifc4x3_rc1>& file, Ifc4x3_rc1::IfcProductRepresentation shape, Ifc4x3_rc1::IfcPresentationStyleAssignment style_assignment) {
    setSurfaceColour_2x3(file, shape, style_assignment);
}

void setSurfaceColour(IfcHierarchyHelper<Ifc4x3_rc1>& file, Ifc4x3_rc1::IfcRepresentation shape, Ifc4x3_rc1::IfcPresentationStyleAssignment style_assignment) {
    setSurfaceColour_2x3(file, shape, style_assignment);
}
#endif

#ifdef HAS_SCHEMA_4x3_rc2
Ifc4x3_rc2::IfcPresentationStyleAssignment addStyleAssignment(IfcHierarchyHelper<Ifc4x3_rc2>& file, double r, double g, double b, double a) {
    return addStyleAssignment_2x3(file, r, g, b, a);
}

Ifc4x3_rc2::IfcPresentationStyleAssignment setSurfaceColour(IfcHierarchyHelper<Ifc4x3_rc2>& file, Ifc4x3_rc2::IfcProductRepresentation shape, double r, double g, double b, double a) {
    return setSurfaceColour_2x3(file, shape, r, g, b, a);
}

Ifc4x3_rc2::IfcPresentationStyleAssignment setSurfaceColour(IfcHierarchyHelper<Ifc4x3_rc2>& file, Ifc4x3_rc2::IfcRepresentation shape, double r, double g, double b, double a) {
    return setSurfaceColour_2x3(file, shape, r, g, b, a);
}

void setSurfaceColour(IfcHierarchyHelper<Ifc4x3_rc2>& file, Ifc4x3_rc2::IfcProductRepresentation shape, Ifc4x3_rc2::IfcPresentationStyleAssignment style_assignment) {
    setSurfaceColour_2x3(file, shape, style_assignment);
}

void setSurfaceColour(IfcHierarchyHelper<Ifc4x3_rc2>& file, Ifc4x3_rc2::IfcRepresentation shape, Ifc4x3_rc2::IfcPresentationStyleAssignment style_assignment) {
    setSurfaceColour_2x3(file, shape, style_assignment);
}
#endif

#ifdef HAS_SCHEMA_4x3_rc3
Ifc4x3_rc3::IfcPresentationStyle addStyleAssignment(IfcHierarchyHelper<Ifc4x3_rc3>& file, double r, double g, double b, double a) {
    return addStyleAssignment_4x3(file, r, g, b, a);
}

Ifc4x3_rc3::IfcPresentationStyle setSurfaceColour(IfcHierarchyHelper<Ifc4x3_rc3>& file, Ifc4x3_rc3::IfcProductRepresentation shape, double r, double g, double b, double a) {
    return setSurfaceColour_4x3(file, shape, r, g, b, a);
}

Ifc4x3_rc3::IfcPresentationStyle setSurfaceColour(IfcHierarchyHelper<Ifc4x3_rc3>& file, Ifc4x3_rc3::IfcRepresentation shape, double r, double g, double b, double a) {
    return setSurfaceColour_4x3(file, shape, r, g, b, a);
}

void setSurfaceColour(IfcHierarchyHelper<Ifc4x3_rc3>& file, Ifc4x3_rc3::IfcProductRepresentation shape, Ifc4x3_rc3::IfcPresentationStyle style) {
    setSurfaceColour_4x3(file, shape, style);
}

void setSurfaceColour(IfcHierarchyHelper<Ifc4x3_rc3>& file, Ifc4x3_rc3::IfcRepresentation shape, Ifc4x3_rc3::IfcPresentationStyle style) {
    setSurfaceColour_4x3(file, shape, style);
}
#endif

#ifdef HAS_SCHEMA_4x3_rc4
Ifc4x3_rc4::IfcPresentationStyle addStyleAssignment(IfcHierarchyHelper<Ifc4x3_rc4>& file, double r, double g, double b, double a) {
    return addStyleAssignment_4x3(file, r, g, b, a);
}

Ifc4x3_rc4::IfcPresentationStyle setSurfaceColour(IfcHierarchyHelper<Ifc4x3_rc4>& file, Ifc4x3_rc4::IfcProductRepresentation shape, double r, double g, double b, double a) {
    return setSurfaceColour_4x3(file, shape, r, g, b, a);
}

Ifc4x3_rc4::IfcPresentationStyle setSurfaceColour(IfcHierarchyHelper<Ifc4x3_rc4>& file, Ifc4x3_rc4::IfcRepresentation shape, double r, double g, double b, double a) {
    return setSurfaceColour_4x3(file, shape, r, g, b, a);
}

void setSurfaceColour(IfcHierarchyHelper<Ifc4x3_rc4>& file, Ifc4x3_rc4::IfcProductRepresentation shape, Ifc4x3_rc4::IfcPresentationStyle style) {
    setSurfaceColour_4x3(file, shape, style);
}

void setSurfaceColour(IfcHierarchyHelper<Ifc4x3_rc4>& file, Ifc4x3_rc4::IfcRepresentation shape, Ifc4x3_rc4::IfcPresentationStyle style) {
    setSurfaceColour_4x3(file, shape, style);
}
#endif

#ifdef HAS_SCHEMA_4x3
Ifc4x3::IfcPresentationStyle addStyleAssignment(IfcHierarchyHelper<Ifc4x3>& file, double r, double g, double b, double a) {
    return addStyleAssignment_4x3(file, r, g, b, a);
}

Ifc4x3::IfcPresentationStyle setSurfaceColour(IfcHierarchyHelper<Ifc4x3>& file, Ifc4x3::IfcProductRepresentation shape, double r, double g, double b, double a) {
    return setSurfaceColour_4x3(file, shape, r, g, b, a);
}

Ifc4x3::IfcPresentationStyle setSurfaceColour(IfcHierarchyHelper<Ifc4x3>& file, Ifc4x3::IfcRepresentation shape, double r, double g, double b, double a) {
    return setSurfaceColour_4x3(file, shape, r, g, b, a);
}

void setSurfaceColour(IfcHierarchyHelper<Ifc4x3>& file, Ifc4x3::IfcProductRepresentation shape, Ifc4x3::IfcPresentationStyle style) {
    setSurfaceColour_4x3(file, shape, style);
}

void setSurfaceColour(IfcHierarchyHelper<Ifc4x3>& file, Ifc4x3::IfcRepresentation shape, Ifc4x3::IfcPresentationStyle style) {
    setSurfaceColour_4x3(file, shape, style);
}
#endif

#ifdef HAS_SCHEMA_4x3_tc1
Ifc4x3_tc1::IfcPresentationStyle addStyleAssignment(IfcHierarchyHelper<Ifc4x3_tc1>& file, double r, double g, double b, double a) {
    return addStyleAssignment_4x3(file, r, g, b, a);
}

Ifc4x3_tc1::IfcPresentationStyle setSurfaceColour(IfcHierarchyHelper<Ifc4x3_tc1>& file, Ifc4x3_tc1::IfcProductRepresentation shape, double r, double g, double b, double a) {
    return setSurfaceColour_4x3(file, shape, r, g, b, a);
}

Ifc4x3_tc1::IfcPresentationStyle setSurfaceColour(IfcHierarchyHelper<Ifc4x3_tc1>& file, Ifc4x3_tc1::IfcRepresentation shape, double r, double g, double b, double a) {
    return setSurfaceColour_4x3(file, shape, r, g, b, a);
}

void setSurfaceColour(IfcHierarchyHelper<Ifc4x3_tc1>& file, Ifc4x3_tc1::IfcProductRepresentation shape, Ifc4x3_tc1::IfcPresentationStyle style) {
    setSurfaceColour_4x3(file, shape, style);
}

void setSurfaceColour(IfcHierarchyHelper<Ifc4x3_tc1>& file, Ifc4x3_tc1::IfcRepresentation shape, Ifc4x3_tc1::IfcPresentationStyle style) {
    setSurfaceColour_4x3(file, shape, style);
}
#endif

#ifdef HAS_SCHEMA_4x3_add1
Ifc4x3_add1::IfcPresentationStyle addStyleAssignment(IfcHierarchyHelper<Ifc4x3_add1>& file, double r, double g, double b, double a) {
    return addStyleAssignment_4x3(file, r, g, b, a);
}

Ifc4x3_add1::IfcPresentationStyle setSurfaceColour(IfcHierarchyHelper<Ifc4x3_add1>& file, Ifc4x3_add1::IfcProductRepresentation shape, double r, double g, double b, double a) {
    return setSurfaceColour_4x3(file, shape, r, g, b, a);
}

Ifc4x3_add1::IfcPresentationStyle setSurfaceColour(IfcHierarchyHelper<Ifc4x3_add1>& file, Ifc4x3_add1::IfcRepresentation shape, double r, double g, double b, double a) {
    return setSurfaceColour_4x3(file, shape, r, g, b, a);
}

void setSurfaceColour(IfcHierarchyHelper<Ifc4x3_add1>& file, Ifc4x3_add1::IfcProductRepresentation shape, Ifc4x3_add1::IfcPresentationStyle style) {
    setSurfaceColour_4x3(file, shape, style);
}

void setSurfaceColour(IfcHierarchyHelper<Ifc4x3_add1>& file, Ifc4x3_add1::IfcRepresentation shape, Ifc4x3_add1::IfcPresentationStyle style) {
    setSurfaceColour_4x3(file, shape, style);
}
#endif

#ifdef HAS_SCHEMA_4x3_add2
Ifc4x3_add2::IfcPresentationStyle addStyleAssignment(IfcHierarchyHelper<Ifc4x3_add2>& file, double r, double g, double b, double a) {
    return addStyleAssignment_4x3(file, r, g, b, a);
}

Ifc4x3_add2::IfcPresentationStyle setSurfaceColour(IfcHierarchyHelper<Ifc4x3_add2>& file, Ifc4x3_add2::IfcProductRepresentation shape, double r, double g, double b, double a) {
    return setSurfaceColour_4x3(file, shape, r, g, b, a);
}

Ifc4x3_add2::IfcPresentationStyle setSurfaceColour(IfcHierarchyHelper<Ifc4x3_add2>& file, Ifc4x3_add2::IfcRepresentation shape, double r, double g, double b, double a) {
    return setSurfaceColour_4x3(file, shape, r, g, b, a);
}

void setSurfaceColour(IfcHierarchyHelper<Ifc4x3_add2>& file, Ifc4x3_add2::IfcProductRepresentation shape, Ifc4x3_add2::IfcPresentationStyle style) {
    setSurfaceColour_4x3(file, shape, style);
}

void setSurfaceColour(IfcHierarchyHelper<Ifc4x3_add2>& file, Ifc4x3_add2::IfcRepresentation shape, Ifc4x3_add2::IfcPresentationStyle style) {
    setSurfaceColour_4x3(file, shape, style);
}
#endif

template <typename Schema>
typename Schema::IfcProductDefinitionShape IfcHierarchyHelper<Schema>::addMappedItem(
    typename Schema::IfcShapeRepresentation rep,
    typename Schema::IfcCartesianTransformationOperator3D transform,
    typename Schema::IfcProductDefinitionShape def)
{
    auto maps = rep.RepresentationMap();
    typename Schema::IfcRepresentationMap map;
    if (maps.size() == 1) {
        map = maps.front();
    } else {
        map = create<Schema::IfcRepresentationMap>();
        map.setMappingOrigin(addPlacement3d());
        map.setMappedRepresentation(rep);
    }

    std::vector<typename Schema::IfcRepresentation> representations;
    if (def) {
        representations = def.Representations();
    }

    if (!transform) {
        transform = create<Schema::IfcCartesianTransformationOperator3D>();
        transform.setLocalOrigin(addTriplet<typename Schema::IfcCartesianPoint>(0, 0, 0));
    }
    auto item = create<Schema::IfcMappedItem>();
    item.setMappingSource(map);
    item.setMappingTarget(transform);

    auto new_rep = create<Schema::IfcShapeRepresentation>();
    new_rep.setContextOfItems(rep.ContextOfItems());
    new_rep.setRepresentationType(std::string("MappedRepresentation"));
    new_rep.setItems(std::vector<typename Schema::IfcRepresentationItem>{item});

    if (rep.RepresentationIdentifier()) {
        new_rep.setRepresentationIdentifier(rep.RepresentationIdentifier());
    }

    representations.push_back(new_rep);

    if (!def) {
        def = create<Schema::IfcProductDefinitionShape>();
        def.setRepresentations(representations);
    } else {
        def.setRepresentations(representations);
    }

    return def;
}

template <typename Schema>
typename Schema::IfcProductDefinitionShape IfcHierarchyHelper<Schema>::addMappedItem(
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
typename Schema::IfcShapeRepresentation IfcHierarchyHelper<Schema>::addEmptyRepresentation(const std::string& repid, const std::string& reptype) {
    auto shape_rep = create<Schema::IfcShapeRepresentation>();
    shape_rep.setContextOfItems(getRepresentationContext(reptype == "Curve2D" ? "Plan" : "Model"));
    shape_rep.setRepresentationIdentifier(repid);
    shape_rep.setRepresentationType(reptype);
    shape_rep.setItems(std::vector<Schema::IfcRepresentationItem>{});
    addEntity(shape_rep);
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
typename Schema::IfcGeometricRepresentationContext IfcHierarchyHelper<Schema>::getRepresentationContext(const std::string& s) {
    auto iter = contexts_.find(s);
    if (iter != contexts_.end()) {
        return iter->second;
    }
    auto project = getSingle<typename Schema::IfcProject>();
    if (!project) {
        project = addProject();
    }
    auto project_contexts = project.RepresentationContexts();
    auto context = create<Schema::IfcGeometricRepresentationContext>();
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
typename Schema::IfcGeometricRepresentationSubContext IfcHierarchyHelper<Schema>::getRepresentationSubContext(const std::string& ident, const std::string& type) {
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
        rep_subcontext = create<Schema::IfcGeometricRepresentationSubContext>();
        rep_subcontext.setContextIdentifier(ident);
        rep_subcontext.setContextType(type);
        rep_subcontext.setParentContext(geometric_representation_context);
        rep_subcontext.setTargetView(Schema::IfcGeometricProjectionEnum::IfcGeometricProjection_MODEL_VIEW);
    }

    return rep_subcontext;
}

#ifdef HAS_SCHEMA_2x3
template IFC_PARSE_API class IfcHierarchyHelper<Ifc2x3>;
#endif
#ifdef HAS_SCHEMA_4
template IFC_PARSE_API class IfcHierarchyHelper<Ifc4>;
#endif
#ifdef HAS_SCHEMA_4x1
template IFC_PARSE_API class IfcHierarchyHelper<Ifc4x1>;
#endif
#ifdef HAS_SCHEMA_4x2
template IFC_PARSE_API class IfcHierarchyHelper<Ifc4x2>;
#endif
#ifdef HAS_SCHEMA_4x3_rc1
template IFC_PARSE_API class IfcHierarchyHelper<Ifc4x3_rc1>;
#endif
#ifdef HAS_SCHEMA_4x3_rc2
template IFC_PARSE_API class IfcHierarchyHelper<Ifc4x3_rc2>;
#endif
#ifdef HAS_SCHEMA_4x3_rc3
template IFC_PARSE_API class IfcHierarchyHelper<Ifc4x3_rc3>;
#endif
#ifdef HAS_SCHEMA_4x3_rc4
template IFC_PARSE_API class IfcHierarchyHelper<Ifc4x3_rc4>;
#endif
#ifdef HAS_SCHEMA_4x3
template IFC_PARSE_API class IfcHierarchyHelper<Ifc4x3>;
#endif
#ifdef HAS_SCHEMA_4x3_tc1
template IFC_PARSE_API class IfcHierarchyHelper<Ifc4x3_tc1>;
#endif
#ifdef HAS_SCHEMA_4x3_add1
template IFC_PARSE_API class IfcHierarchyHelper<Ifc4x3_add1>;
#endif
#ifdef HAS_SCHEMA_4x3_add2
template IFC_PARSE_API class IfcHierarchyHelper<Ifc4x3_add2>;
#endif
