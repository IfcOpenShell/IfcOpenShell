#include <algorithm>
#include <sstream>
#include <string>
#include <vector>

#include <catch2/catch_approx.hpp>
#include <catch2/catch_test_macros.hpp>

#include "ifcgeom/converter.h"
#include "ifcgeom/kernel_registry.h"
#include "ifcparse/hierarchy_helper.h"
#include "ifcparse/macros.h"
#include IFCGEOM_TEST_SCHEMA_HEADER

namespace {

constexpr int MAX_VOIDS = 30;

IfcSchema::IfcWallStandardCase create_wall_with_voids(hierarchy_helper<IfcSchema>& file, int void_count) {
    file.header().file_name().setname("wall-with-voids.ifc");

    auto wall = file.create<IfcSchema::IfcWallStandardCase>();
    wall.setGlobalId(ifcopenshell::global_id());
    wall.setName("Wall with " + std::to_string(void_count) + " voids");
    file.addBuildingProduct(wall);

    const auto owner_history = file.getSingle<IfcSchema::IfcOwnerHistory>();
    const auto storey_placement = file.getSingle<IfcSchema::IfcBuildingStorey>().ObjectPlacement();
    const double opening_spacing = 350.0;
    const double wall_width = std::max(12000.0, void_count * opening_spacing + 1000.0);
    const double wall_depth = 360.0;
    const double wall_height = 3000.0;

    wall.setOwnerHistory(owner_history);
    wall.setObjectPlacement(file.addLocalPlacement(storey_placement));
    wall.setRepresentation(file.addAxisBox(wall_width, wall_depth, wall_height));

    const double first_opening_x = -((void_count - 1) * opening_spacing) / 2.0;
    for (int i = 0; i < void_count; ++i) {
        auto opening = file.create<IfcSchema::IfcOpeningElement>();
        opening.setGlobalId(ifcopenshell::global_id());
        opening.setOwnerHistory(owner_history);
        opening.setName("Opening " + std::to_string(i + 1));
        opening.setObjectPlacement(file.addLocalPlacement(
            wall.ObjectPlacement(),
            first_opening_x + i * opening_spacing,
            0.0,
            900.0));
        opening.setRepresentation(file.addBox(200.0, wall_depth + 40.0, 1200.0));

        auto void_element = file.create<IfcSchema::IfcRelVoidsElement>();
        void_element.setGlobalId(ifcopenshell::global_id());
        void_element.setOwnerHistory(owner_history);
        void_element.setRelatingBuildingElement(wall);
        void_element.setRelatedOpeningElement(opening);
    }

    return wall;
}

std::size_t count_geo403_for_wall(hierarchy_helper<IfcSchema>& file, const IfcSchema::IfcWallStandardCase& wall) {
    ifcopenshell::geom::settings settings;
    settings.set("max-voids-per-element", MAX_VOIDS);

    ifcopenshell::logger log;
    log.output_format(ifcopenshell::logger::FMT_INMEMORY);
    ifcopenshell::geom::converter converter(
        ifcopenshell::geom::kernels::construct(&file, "opencascade", settings, log), &file, settings, log);
    delete converter.create_brep_for_representation_and_product(wall.Representation().Representations().back(), wall);
    return log.count("GEO403");
}

IfcSchema::IfcShapeRepresentation add_box_representation(
    hierarchy_helper<IfcSchema>& file,
    IfcSchema::IfcRepresentationContext context,
    const std::string& identifier,
    double size)
{
    auto representation = file.create<IfcSchema::IfcShapeRepresentation>();
    representation.setContextOfItems(context);
    representation.setRepresentationIdentifier(identifier);
    representation.setRepresentationType("SweptSolid");
    representation.setItems(std::vector<IfcSchema::IfcRepresentationItem>{});
    file.addBox(representation, size, size, size);
    return representation;
}

IfcSchema::IfcRepresentation select_representation(
    hierarchy_helper<IfcSchema>& file,
    const IfcSchema::IfcWallStandardCase& wall,
    const std::vector<std::string>& context_priorities)
{
    ifcopenshell::geom::settings settings;
    settings.set("context-priorities", std::vector<std::string>(context_priorities));

    ifcopenshell::logger log;
    log.output_format(ifcopenshell::logger::FMT_INMEMORY);
    ifcopenshell::geom::converter converter(
        ifcopenshell::geom::kernels::construct(&file, "passthrough", settings, log), &file, settings, log);

    auto selected = converter.mapping()->representation_of(wall).as<IfcSchema::IfcRepresentation>();
    REQUIRE(selected);
    return selected;
}

IfcSchema::IfcWallStandardCase add_wall_with_representations(
    hierarchy_helper<IfcSchema>& file,
    const std::vector<IfcSchema::IfcRepresentation>& representations)
{
    auto wall = file.create<IfcSchema::IfcWallStandardCase>();
    wall.setGlobalId(ifcopenshell::global_id());
    file.addBuildingProduct(wall);

    auto shape = file.create<IfcSchema::IfcProductDefinitionShape>();
    shape.setRepresentations(representations);
    wall.setRepresentation(shape);

    return wall;
}

std::vector<ifcopenshell::geom::geometry_conversion_task> representation_tasks(
    hierarchy_helper<IfcSchema>& file,
    const std::vector<std::string>& context_priorities)
{
    ifcopenshell::geom::settings settings;
    settings.set("context-priorities", std::vector<std::string>(context_priorities));

    ifcopenshell::logger log;
    log.output_format(ifcopenshell::logger::FMT_INMEMORY);
    ifcopenshell::geom::converter converter(
        ifcopenshell::geom::kernels::construct(&file, "passthrough", settings, log), &file, settings, log);

    std::vector<ifcopenshell::geom::geometry_conversion_task> tasks;
    std::vector<ifcopenshell::geom::filter_function> filters;
    converter.mapping()->get_representations(tasks, filters);
    return tasks;
}

const ifcopenshell::geom::geometry_conversion_task* task_for_product(
    const std::vector<ifcopenshell::geom::geometry_conversion_task>& tasks,
    const express::base& product)
{
    for (const auto& task : tasks) {
        if (std::any_of(task.products.begin(), task.products.end(), [&](const express::base& task_product) {
                return task_product.id() == product.id();
            })) {
            return &task;
        }
    }
    return nullptr;
}

// A minimal IfcSectionedSolidHorizontal (IFC4X3_ADD2) whose two
// IfcAxis2PlacementLinear cross section positions use direction vectors
// inconsistently: the near position carries a raked RefDirection and a
// 1/cos(theta) wider profile, the far position carries neither. Before the
// make_loft() fix this logged GEO 42 and dropped the rotation, lofting a wedge.
constexpr const char* RAKED_SECTIONED_SOLID_SPF = R"IFC(ISO-10303-21;
HEADER;
FILE_DESCRIPTION((''),'2;1');
FILE_NAME('','',(''),(''),'','','');
FILE_SCHEMA(('IFC4X3_ADD2'));
ENDSEC;
DATA;
#1=IFCPROJECT('0RYK8PV8D0ee9DDm77xcTZ',$,'T',$,$,$,$,(#6),$);
#2=IFCCARTESIANPOINT((0.,0.,0.));
#3=IFCDIRECTION((0.,0.,1.));
#4=IFCDIRECTION((1.,0.,0.));
#5=IFCAXIS2PLACEMENT3D(#2,#3,#4);
#6=IFCGEOMETRICREPRESENTATIONCONTEXT($,'Model',3,1.E-05,#5,$);
#7=IFCGEOMETRICREPRESENTATIONSUBCONTEXT('Body','Model',*,*,*,*,#6,$,.MODEL_VIEW.,$);
#8=IFCCARTESIANPOINT((0.,0.,0.));
#9=IFCCARTESIANPOINT((40.,0.,0.));
#10=IFCPOLYLINE((#8,#9));
#11=IFCDIRECTION((0.,0.,1.));
#12=IFCDIRECTION((0.9034641832977311,-0.42866358545853134,0.));
#13=IFCPOINTBYDISTANCEEXPRESSION(IFCLENGTHMEASURE(0.),$,$,$,#10);
#14=IFCAXIS2PLACEMENTLINEAR(#13,#11,#12);
#15=IFCPOINTBYDISTANCEEXPRESSION(IFCLENGTHMEASURE(40.),$,$,$,#10);
#16=IFCAXIS2PLACEMENTLINEAR(#15,#11,$);
#17=IFCCARTESIANPOINTLIST2D(((-0.9223756168081689,0.),(0.9223756168081689,0.),(0.9223756168081689,6.),(-0.9223756168081689,6.),(-0.9223756168081689,0.)),$);
#18=IFCINDEXEDPOLYCURVE(#17,$,.F.);
#19=IFCARBITRARYCLOSEDPROFILEDEF(.AREA.,$,#18);
#20=IFCCARTESIANPOINTLIST2D(((-0.8333333333333334,0.),(0.8333333333333334,0.),(0.8333333333333334,6.),(-0.8333333333333334,6.),(-0.8333333333333334,0.)),$);
#21=IFCINDEXEDPOLYCURVE(#20,$,.F.);
#22=IFCARBITRARYCLOSEDPROFILEDEF(.AREA.,$,#21);
#23=IFCSECTIONEDSOLIDHORIZONTAL(#10,(#19,#22),(#14,#16));
#24=IFCBUILDINGELEMENTPROXY('3cWcr4$892GAeKwryhDILR',$,'wingwall',$,$,$,#26,$,$);
#25=IFCSHAPEREPRESENTATION(#7,'Body','AdvancedSweptSolid',(#23));
#26=IFCPRODUCTDEFINITIONSHAPE($,$,(#25));
ENDSEC;
END-ISO-10303-21;
)IFC";

struct sectioned_solid_result {
    std::size_t geo42_count = 0;
    bool produced_brep = false;
    double projected_area_x = 0.0;
    double projected_area_y = 0.0;
    double projected_area_z = 0.0;
};

sectioned_solid_result convert_sectioned_solid(const std::string& spf) {
    std::istringstream stream(spf);
    ifcopenshell::logger log;
    log.output_format(ifcopenshell::logger::FMT_INMEMORY);
    ifcopenshell::file file(stream, static_cast<int>(spf.size()), log);
    REQUIRE(file.good());

    ifcopenshell::geom::settings settings;
    ifcopenshell::geom::converter converter(
        ifcopenshell::geom::kernels::construct(&file, "opencascade", settings, log), &file, settings, log);

    std::vector<ifcopenshell::geom::geometry_conversion_task> tasks;
    std::vector<ifcopenshell::geom::filter_function> filters;
    converter.mapping()->get_representations(tasks, filters);
    REQUIRE(!tasks.empty());

    sectioned_solid_result result;
    for (const auto& task : tasks) {
        REQUIRE(!task.products.empty());
        auto* elem = converter.create_brep_for_representation_and_product(task.representation, task.products.front());
        if (elem) {
            result.produced_brep = true;
            elem->calculate_projected_surface_area(
                result.projected_area_x, result.projected_area_y, result.projected_area_z);
        }
        delete elem;
    }
    result.geo42_count = log.count("GEO42");
    return result;
}

std::size_t count_geo42_converting(const std::string& spf) {
    return convert_sectioned_solid(spf).geo42_count;
}

// A minimal IfcSectionedSolidHorizontal (IFC4X3_ADD2) whose cross section
// placements carry an explicit Axis = (0,0,1) but no RefDirection, on a
// directrix that runs along +Y (not the global +X). Per buildingSMART
// IFC4.x-IF #147 the profile normal follows the directrix tangent, so the
// 12 x 0.5 rectangle sweeps 60 along +Y: a plan (Z) projected area of ~720.
// Before the fix the profile was placed with a fixed axis permutation that
// ignored the directrix and the solid collapsed.
constexpr const char* AXIS_ALIGNED_SECTIONED_SOLID_SPF = R"IFC(ISO-10303-21;
HEADER;
FILE_DESCRIPTION((''),'2;1');
FILE_NAME('','',(''),(''),'','','');
FILE_SCHEMA(('IFC4X3_ADD2'));
ENDSEC;
DATA;
#1=IFCPROJECT('0RYK8PV8D0ee9DDm77xcTZ',$,'T',$,$,$,$,(#6),$);
#2=IFCCARTESIANPOINT((0.,0.,0.));
#3=IFCDIRECTION((0.,0.,1.));
#4=IFCDIRECTION((1.,0.,0.));
#5=IFCAXIS2PLACEMENT3D(#2,#3,#4);
#6=IFCGEOMETRICREPRESENTATIONCONTEXT($,'Model',3,1.E-05,#5,$);
#7=IFCGEOMETRICREPRESENTATIONSUBCONTEXT('Body','Model',*,*,*,*,#6,$,.MODEL_VIEW.,$);
#8=IFCCARTESIANPOINT((0.,0.,0.));
#9=IFCCARTESIANPOINT((0.,60.,0.));
#10=IFCPOLYLINE((#8,#9));
#11=IFCDIRECTION((0.,0.,1.));
#13=IFCPOINTBYDISTANCEEXPRESSION(IFCLENGTHMEASURE(0.),$,$,$,#10);
#14=IFCAXIS2PLACEMENTLINEAR(#13,#11,$);
#15=IFCPOINTBYDISTANCEEXPRESSION(IFCLENGTHMEASURE(60.),$,$,$,#10);
#16=IFCAXIS2PLACEMENTLINEAR(#15,#11,$);
#17=IFCCARTESIANPOINTLIST2D(((-6.,0.),(6.,0.),(6.,0.5),(-6.,0.5),(-6.,0.)),$);
#18=IFCINDEXEDPOLYCURVE(#17,$,.F.);
#19=IFCARBITRARYCLOSEDPROFILEDEF(.AREA.,$,#18);
#23=IFCSECTIONEDSOLIDHORIZONTAL(#10,(#19,#19),(#14,#16));
#24=IFCBUILDINGELEMENTPROXY('3cWcr4$892GAeKwryhDILR',$,'pavement',$,$,$,#26,$,$);
#25=IFCSHAPEREPRESENTATION(#7,'Body','AdvancedSweptSolid',(#23));
#26=IFCPRODUCTDEFINITIONSHAPE($,$,(#25));
ENDSEC;
END-ISO-10303-21;
)IFC";

} // namespace

TEST_CASE("IfcSectionedSolidHorizontal raked end cut does not log GEO 42", "[ifcgeom][infra-sweep]") {
    if (std::string(STRINGIFY(IfcSchema)) != "Ifc4x3_add2") {
        SKIP("fixture is authored for IFC4X3_ADD2");
    }
    CHECK(count_geo42_converting(RAKED_SECTIONED_SOLID_SPF) == 0);
}

TEST_CASE("IfcSectionedSolidHorizontal follows a non-axis-aligned directrix", "[ifcgeom][infra-sweep]") {
    if (std::string(STRINGIFY(IfcSchema)) != "Ifc4x3_add2") {
        SKIP("fixture is authored for IFC4X3_ADD2");
    }
    const auto result = convert_sectioned_solid(AXIS_ALIGNED_SECTIONED_SOLID_SPF);
    CHECK(result.geo42_count == 0);
    REQUIRE(result.produced_brep);
    // Plan projection is the top plus the bottom of the slab, 2 x width x length;
    // a collapsed sweep (the pre-fix behaviour) is nowhere near this.
    CHECK(result.projected_area_z == Catch::Approx(2.0 * 12.0 * 60.0).margin(2.0));
}

TEST_CASE("IfcGeom C++ fixture creates walls below and above the void limit", "[ifcgeom][voids]") {
    hierarchy_helper<IfcSchema> below_limit_file;
    const auto below_limit_wall = create_wall_with_voids(below_limit_file, MAX_VOIDS - 1);
    REQUIRE(count_geo403_for_wall(below_limit_file, below_limit_wall) == 0);

    hierarchy_helper<IfcSchema> above_limit_file;
    const auto above_limit_wall = create_wall_with_voids(above_limit_file, MAX_VOIDS + 1);
    REQUIRE(count_geo403_for_wall(above_limit_file, above_limit_wall) == 1);
}

TEST_CASE("IfcGeom context priorities select representations by subcontext filter", "[ifcgeom][context]") {
    hierarchy_helper<IfcSchema> file;

    auto body_context = file.getRepresentationSubContext("Body", "Model");
    auto tesselation_context = file.getRepresentationSubContext("Tesselation", "Model");

    auto wall = file.create<IfcSchema::IfcWallStandardCase>();
    wall.setGlobalId(ifcopenshell::global_id());
    file.addBuildingProduct(wall);

    const auto body_representation = add_box_representation(file, body_context, "Body", 1000.0);
    const auto tesselation_representation = add_box_representation(file, tesselation_context, "Tesselation", 500.0);
    REQUIRE(body_context.RepresentationsInContext().size() == 1);
    REQUIRE(tesselation_context.RepresentationsInContext().size() == 1);

    auto shape = file.create<IfcSchema::IfcProductDefinitionShape>();
    shape.setRepresentations(
        std::vector<IfcSchema::IfcRepresentation>{tesselation_representation, body_representation});
    wall.setRepresentation(shape);

    REQUIRE(select_representation(file, wall, {"body"}).id() == body_representation.id());
    REQUIRE(select_representation(file, wall, {"tesselation"}).id() == tesselation_representation.id());
    REQUIRE(
        select_representation(file, wall, {"tesselation[context-identifier=Tesselation]"}).id() ==
        tesselation_representation.id());
    REQUIRE(
        select_representation(file, wall, {"tesselation[targetview=MODEL_VIEW]"}).id() ==
        tesselation_representation.id());
    REQUIRE(
        select_representation(file, wall, {"tesselation[target_view=MODEL_VIEW]"}).id() ==
        tesselation_representation.id());
    REQUIRE(
        select_representation(file, wall, {"body", "tesselation[targetview=MODEL_VIEW]"}).id() ==
        body_representation.id());
    REQUIRE(
        select_representation(file, wall, {"tesselation[targetview=MODEL_VIEW]", "body"}).id() ==
        tesselation_representation.id());
}

TEST_CASE("IfcGeom context priorities create tasks from highest priority representation", "[ifcgeom][context]") {
    hierarchy_helper<IfcSchema> file;

    auto body_context = file.getRepresentationSubContext("Body", "Model");
    auto tesselation_context = file.getRepresentationSubContext("Tesselation", "Model");

    const auto body_representation = add_box_representation(file, body_context, "Body", 1000.0);
    const auto tesselation_representation = add_box_representation(file, tesselation_context, "Tesselation", 500.0);
    const auto body_only_representation = add_box_representation(file, body_context, "Body", 750.0);

    const auto wall_with_both = add_wall_with_representations(
        file,
        std::vector<IfcSchema::IfcRepresentation>{body_representation, tesselation_representation});
    const auto wall_with_body_only = add_wall_with_representations(
        file,
        std::vector<IfcSchema::IfcRepresentation>{body_only_representation});

    auto tesselation_first_tasks = representation_tasks(file, {"tesselation[target_view=MODEL_VIEW]", "body"});
    REQUIRE(tesselation_first_tasks.size() == 2);
    REQUIRE(tesselation_first_tasks[0].representation.id() == tesselation_representation.id());
    REQUIRE(tesselation_first_tasks[0].products.size() == 1);
    REQUIRE(tesselation_first_tasks[0].products.front().id() == wall_with_both.id());
    REQUIRE(tesselation_first_tasks[1].representation.id() == body_only_representation.id());
    REQUIRE(tesselation_first_tasks[1].products.size() == 1);
    REQUIRE(tesselation_first_tasks[1].products.front().id() == wall_with_body_only.id());

    auto body_first_tasks = representation_tasks(file, {"body", "tesselation[targetview=MODEL_VIEW]"});
    REQUIRE(body_first_tasks.size() == 2);

    const auto* wall_with_both_task = task_for_product(body_first_tasks, wall_with_both);
    REQUIRE(wall_with_both_task != nullptr);
    REQUIRE(wall_with_both_task->representation.id() == body_representation.id());

    const auto* wall_with_body_only_task = task_for_product(body_first_tasks, wall_with_body_only);
    REQUIRE(wall_with_body_only_task != nullptr);
    REQUIRE(wall_with_body_only_task->representation.id() == body_only_representation.id());
}
