#include <algorithm>
#include <memory>
#include <sstream>
#include <string>
#include <vector>

#include <catch2/catch_approx.hpp>
#include <catch2/catch_test_macros.hpp>
#include <catch2/matchers/catch_matchers.hpp>

#include "ifcgeom/converter.h"
#include "ifcgeom/kernel_registry.h"
#include "ifcgeom/profile_helper.h"
#include "ifcgeom/infra_sweep_helper.h"
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

TEST_CASE("Curved profiles on a gradient directrix agree across geometry kernels", "[kernels][infra-sweep][curved-loft]") {
    using namespace ifcopenshell::geom;
    namespace tx = ifcopenshell::geom::taxonomy;
    if (std::string(STRINGIFY(IfcSchema)) != "Ifc4x3_add2") {
        SKIP("fixture is authored for IFC4X3_ADD2");
    }
    std::string profile;
    double profile_area = 0., perimeter = 0.;
    const double pi = boost::math::constants::pi<double>();
    SECTION("Circular profile") {
        profile = "#19=IFCCIRCLEPROFILEDEF(.AREA.,$,$,1.);\n";
        profile_area = pi;
        perimeter = 2. * pi;
    }
    SECTION("Rounded rectangle profile") {
        profile = "#19=IFCROUNDEDRECTANGLEPROFILEDEF(.AREA.,$,$,4.,2.,0.25);\n";
        profile_area = 8. - (4. - pi) * 0.25 * 0.25;
        perimeter = 12. - 8. * 0.25 + 2. * pi * 0.25;
    }
    const std::string spf = R"IFC(ISO-10303-21;
HEADER;
FILE_DESCRIPTION((''),'2;1');
FILE_NAME('','',(''),(''),'','','');
FILE_SCHEMA(('IFC4X3_ADD2'));
ENDSEC;
DATA;
#1=IFCPROJECT('0RYK8PV8D0ee9DDm77xcTZ',$,'T',$,$,$,$,(#6),$);
#2=IFCCARTESIANPOINT((0.,0.,0.));
#5=IFCAXIS2PLACEMENT3D(#2,$,$);
#6=IFCGEOMETRICREPRESENTATIONCONTEXT($,'Model',3,1.E-05,#5,$);
#7=IFCGEOMETRICREPRESENTATIONSUBCONTEXT('Body','Model',*,*,*,*,#6,$,.MODEL_VIEW.,$);
#8=IFCCARTESIANPOINT((0.,0.));
#9=IFCAXIS2PLACEMENT2D(#8,$);
#10=IFCCOMPOSITECURVE((#14),.F.);
#11=IFCDIRECTION((1.,0.));
#12=IFCVECTOR(#11,1.);
#13=IFCLINE(#8,#12);
#14=IFCCURVESEGMENT(.CONTINUOUS.,#9,IFCLENGTHMEASURE(0.),IFCLENGTHMEASURE(10.),#13);
#15=IFCGRADIENTCURVE((#14),.F.,#10,$);
#20=IFCPOINTBYDISTANCEEXPRESSION(IFCLENGTHMEASURE(0.),$,$,$,#15);
#21=IFCAXIS2PLACEMENTLINEAR(#20,$,$);
#22=IFCPOINTBYDISTANCEEXPRESSION(IFCLENGTHMEASURE(10.),$,$,$,#15);
#23=IFCAXIS2PLACEMENTLINEAR(#22,$,$);
#30=IFCSECTIONEDSOLIDHORIZONTAL(#15,(#34,#36),(#21,#23));
#31=IFCBUILDINGELEMENTPROXY('3cWcr4$892GAeKwryhDILR',$,'curved profile',$,$,$,#33,$,$);
#32=IFCSHAPEREPRESENTATION(#7,'Body','AdvancedSweptSolid',(#30));
#33=IFCPRODUCTDEFINITIONSHAPE($,$,(#32));
#34=IFCDERIVEDPROFILEDEF(.AREA.,$,#19,#35,$);
#35=IFCCARTESIANTRANSFORMATIONOPERATOR2D($,$,#8,$);
#36=IFCDERIVEDPROFILEDEF(.AREA.,$,#19,#37,$);
#37=IFCCARTESIANTRANSFORMATIONOPERATOR2D($,$,#38,$);
#38=IFCCARTESIANPOINT((0.,0.25));
)IFC" + profile + "ENDSEC;\nEND-ISO-10303-21;\n";
    std::istringstream stream(spf);
    ifcopenshell::logger logger;
    logger.output_format(ifcopenshell::logger::FMT_INMEMORY);
    ifcopenshell::file file(stream, static_cast<int>(spf.size()), logger);
    REQUIRE(file.good());
    settings settings;
    REQUIRE_FALSE(settings.get<settings::LoftUseRuledSurfaces>().get());
    settings.set("circle-segments", 128);
    settings.set("reorient-shells", true);
    converter mapper(kernels::construct(&file, "passthrough", settings, logger), &file, settings, logger);
    auto loft = std::dynamic_pointer_cast<tx::loft>(mapper.mapping()->map(file.instance_by_id(30)));
    REQUIRE(loft);
    REQUIRE_FALSE(loft->axis);
    // sections are placed by deflection: along a straight, between sections that differ only by an offset,
    // the end sections are enough
    REQUIRE(loft->children.size() >= 2);
    REQUIRE_FALSE(loft->is_polygonal());
    const auto original_section = loft->children.front();
    const auto original_loop = std::static_pointer_cast<tx::face>(original_section)->children.front();
    const auto original_edge = original_loop->children.front();
    const auto original_basis = original_edge->basis;
    auto polygonal = loft->make_polygonal_sections(settings);
    std::ostringstream section_diagnostics;
    for (const auto& section : loft->children) {
        const auto face = std::static_pointer_cast<tx::face>(section);
        const auto loop = face->children.front();
        section_diagnostics << "edges=" << loop->children.size() << " samples=" << loop->to_polygon(settings).size()
            << " basis=" << (face->basis ? tx::kind_to_string(face->basis->kind()) : "none") << "; ";
    }
    INFO(section_diagnostics.str());
    REQUIRE(polygonal != loft);
    REQUIRE(polygonal->is_polygonal());
    REQUIRE(polygonal->instance == loft->instance);
    REQUIRE(polygonal->children.front() != original_section);
    REQUIRE(std::static_pointer_cast<tx::face>(polygonal->children.front())->matrix == original_section->matrix);

    std::vector<std::string> backends = {"passthrough"};
#ifdef TAXONOMY_TEST_OPENCASCADE
    backends.push_back("opencascade");
#endif
#ifdef TAXONOMY_TEST_MANIFOLD
    backends.push_back("manifold");
#endif
#ifdef TAXONOMY_TEST_CGAL
    backends.push_back("cgal");
#endif
#ifdef TAXONOMY_TEST_CGAL_SIMPLE
    backends.push_back("cgal-simple");
#endif
    double reference_volume = 0., reference_area = 0.;
    for (bool ruled : {false, true}) {
        settings.set("loft-use-ruled-surfaces", ruled);
        for (const auto& backend : backends) {
            CAPTURE(backend, ruled);
            auto kernel = kernels::construct(nullptr, backend, settings, logger);
            kernel->propagate_exceptions = true;
            std::vector<conversion_result> converted;
            const bool success = kernel->convert(loft, converted);
            INFO(logger.get_log());
            REQUIRE(success);
            REQUIRE(converted.size() == 1);
            const auto& shape = converted.front().shape();
            REQUIRE(shape->is_manifold());
            const double volume = shape->volume().to_double();
            const double area = shape->area().to_double();
            REQUIRE(volume == Catch::Approx(profile_area * 10.).epsilon(0.002));
            REQUIRE(area == Catch::Approx(profile_area * 2. + perimeter * 10.).epsilon(0.002));
            if (reference_volume == 0.) {
                reference_volume = volume;
                reference_area = area;
            } else {
                const double tolerance = ruled && backend == "opencascade" ? 0.002 : 1.e-6;
                REQUIRE(volume == Catch::Approx(reference_volume).epsilon(tolerance));
                REQUIRE(area == Catch::Approx(reference_area).epsilon(tolerance));
            }
        }
    }
    REQUIRE(loft->children.front() == original_section);
    REQUIRE(original_loop->children.front() == original_edge);
    REQUIRE(original_edge->basis == original_basis);
    REQUIRE_FALSE(loft->is_polygonal());
}

TEST_CASE("Loft profile tessellation keeps first-section sampling without mutating profiles", "[taxonomy][curved-loft]") {
    using namespace ifcopenshell::geom;
    namespace tx = ifcopenshell::geom::taxonomy;
    auto loft = tx::make<tx::loft>();
    loft->matrix = tx::make<tx::matrix4>();
    loft->matrix->components()(0, 3) = 10.;
    for (double radius : {1., 2.}) {
        auto circle = tx::make<tx::circle>();
        circle->radius = radius;
        circle->matrix = tx::make<tx::matrix4>();
        auto edge = tx::make<tx::edge>();
        edge->basis = circle;
        edge->start = 0.;
        edge->end = 2. * boost::math::constants::pi<double>();
        auto loop = tx::make<tx::loop>();
        loop->children = {edge};
        loop->external = true;
        loop->matrix = tx::make<tx::matrix4>();
        loop->matrix->components()(1, 3) = 3.;
        loop->orientation = false;
        auto face = tx::make<tx::face>();
        face->children = {loop};
        face->matrix = tx::make<tx::matrix4>();
        face->matrix->components()(2, 3) = radius - 1.;
        loft->children.push_back(face);
    }
    settings coarse;
    coarse.set("mesher-linear-deflection", 0.1);
    settings fine;
    fine.set("mesher-linear-deflection", 0.001);
    auto low = loft->make_polygonal_sections(coarse);
    auto high = loft->make_polygonal_sections(fine);
    auto boundary = [](const tx::loft::ptr& loft, size_t index) {
        return std::static_pointer_cast<tx::face>(loft->children[index])->children.front();
    };
    REQUIRE(high->matrix == loft->matrix);
    REQUIRE(boundary(high, 0)->children.size() == boundary(high, 1)->children.size());
    REQUIRE(boundary(high, 0)->children.size() == boundary(loft, 0)->children.front()->to_polygon(fine).size() - 1);
    REQUIRE(boundary(high, 0)->children.size() > boundary(low, 0)->children.size());
    REQUIRE(boundary(high, 0)->closed.value());
    REQUIRE_FALSE(boundary(high, 0)->matrix);
    REQUIRE(boundary(high, 0)->orientation.value());
    REQUIRE(std::get<tx::point3::ptr>(boundary(high, 0)->children.front()->start)->ccomponents().y() == Catch::Approx(3.));
    REQUIRE(high->to_polyhedron()->closed.value());
    REQUIRE(boundary(loft, 0)->children.size() == 1);
    REQUIRE(boundary(loft, 0)->matrix->ccomponents()(1, 3) == 3.);
    REQUIRE_FALSE(boundary(loft, 0)->orientation.value());
    REQUIRE(boundary(loft, 0)->children.front()->basis->kind() == tx::CIRCLE);

    auto original = boundary(loft, 0);
    original->external = false;
    auto promoted = tx::cast<tx::face>(original);
    REQUIRE(promoted->matrix == original->matrix);
    REQUIRE(promoted->children.front() != original);
    REQUIRE_FALSE(promoted->children.front()->matrix);
    REQUIRE(promoted->children.front()->external.value());
    REQUIRE_FALSE(original->external.value());
}

TEST_CASE("Taxonomy edge equality includes trims senses bases and local placements", "[taxonomy][edge-interpolation]") {
    namespace tx = ifcopenshell::geom::taxonomy;
    auto circle = tx::make<tx::circle>();
    circle->radius = 1.;
    auto a = tx::make<tx::edge>();
    a->basis = circle;
    a->start = 0.;
    a->end = boost::math::constants::pi<double>();
    auto b = tx::make<tx::edge>(*a);
    auto equal = tx::equal_functor{};
    REQUIRE(equal(a, b));
    b->basis = tx::make<tx::circle>(*circle);
    std::static_pointer_cast<tx::circle>(b->basis)->matrix = tx::make<tx::matrix4>();
    REQUIRE(equal(a, b)); // Missing placement is identity.
    b->curve_sense = false;
    REQUIRE_FALSE(equal(a, b));
    b->curve_sense = true;
    REQUIRE(equal(a, b));
    b->orientation = false;
    REQUIRE_FALSE(equal(a, b));
    b->orientation = true;
    b->end = 1.;
    REQUIRE_FALSE(equal(a, b));
    b->end = a->end;
    b->basis = nullptr;
    REQUIRE_FALSE(equal(a, b));
    REQUIRE_FALSE(equal(b, a));
    b->basis = circle;
    b->matrix = tx::make<tx::matrix4>();
    REQUIRE(equal(a, b));
    b->matrix->components()(0, 3) = 1.;
    REQUIRE_FALSE(equal(a, b));
    b->matrix = nullptr;
    b->start = tx::make<tx::point3>(1., 0., 0.);
    REQUIRE_FALSE(equal(a, b));
    auto spline = tx::make<tx::bspline_curve>();
    spline->degree = 1;
    spline->control_points = {tx::make<tx::point3>(0., 0., 0.), tx::make<tx::point3>(1., 0., 0.)};
    spline->knots = {0., 1.};
    spline->multiplicities = {2, 2};
    auto other = tx::make<tx::bspline_curve>(*spline);
    REQUIRE(equal(spline, other));
    other->control_points.back() = tx::make<tx::point3>(2., 0., 0.);
    REQUIRE_FALSE(equal(spline, other));
    auto fa = tx::make<tx::face>(), fb = tx::make<tx::face>();
    auto la = tx::make<tx::loop>(), lb = tx::make<tx::loop>();
    auto period_a = tx::make<tx::edge>();
    period_a->basis = circle;
    period_a->start = 0.;
    period_a->end = 2. * boost::math::constants::pi<double>();
    auto period_b = tx::make<tx::edge>(*period_a);
    period_b->start = 1.;
    period_b->end = 1. + 2. * boost::math::constants::pi<double>();
    la->children = {period_a};
    lb->children = {period_b};
    fa->children = {la};
    fb->children = {lb};
    auto loft = tx::make<tx::loft>();
    loft->children = {fa, fb};
    ifcopenshell::geom::settings settings;
    REQUIRE_THROWS_WITH(loft->make_compatible_sections(settings), "Loft closed-edge seams or sweep directions do not correspond");
    period_b->start = period_a->start;
    period_b->end = period_a->end;
    period_b->curve_sense = false;
    REQUIRE_THROWS_WITH(loft->make_compatible_sections(settings), "Loft closed-edge seams or sweep directions do not correspond");
}

TEST_CASE("Loft edge planning handles mixed bases and rejects incompatible correspondence", "[taxonomy][edge-interpolation]") {
    using namespace ifcopenshell::geom;
    namespace tx = ifcopenshell::geom::taxonomy;
    auto a = profile_helper(nullptr, {{{0., 0.}}, {{2., 0.}}, {{2., 2.}}, {{0., 2.}}});
    auto b = tx::make<tx::loop>(*a);
    b->children.front() = tx::make<tx::edge>(*a->children.front());
    b->children.front()->basis = tx::circle::from_3_points({0., 0., 0.}, {1., -0.2, 0.}, {2., 0., 0.});
    auto fa = tx::make<tx::face>(), fb = tx::make<tx::face>();
    fa->children = {a};
    fb->children = {b};
    auto loft = tx::make<tx::loft>();
    loft->children = {fa, fb};
    settings settings;
    auto prepared = loft->make_compatible_sections(settings);
    auto first = std::static_pointer_cast<tx::face>(prepared->children.front())->children.front();
    auto last = std::static_pointer_cast<tx::face>(prepared->children.back())->children.front();
    REQUIRE(first->children.size() == last->children.size());
    REQUIRE(first->children.size() == 6); // Three intervals for the mixed edge, then three original edges.
    REQUIRE_FALSE(first->children.front()->basis);
    REQUIRE_FALSE(last->children.front()->basis);
    REQUIRE(std::get<tx::point3::ptr>(last->children[1]->start)->ccomponents().y() < 0.);
    REQUIRE(a->children.size() == 4);
    REQUIRE(b->children.front()->basis);
    b->orientation = false;
    REQUIRE_THROWS_WITH(loft->make_compatible_sections(settings), "Incompatible loft boundary 1: tags, closure, exterior or orientation differ");
    b->orientation = true;
    b->children.pop_back();
    REQUIRE_THROWS_WITH(loft->make_compatible_sections(settings), "Loft boundary 1 edge counts differ without corresponding tags");
}

TEST_CASE("Loft interpolation retains equal curves and samples changing edges consistently", "[kernels][edge-interpolation]") {
    using namespace ifcopenshell::geom;
    namespace tx = ifcopenshell::geom::taxonomy;
    hierarchy_helper<IfcSchema> file;
    auto instance = file.create<IfcSchema::IfcBuildingElementProxy>();
    auto path = tx::make<tx::functor_item>(10., [](double u) {
        Eigen::Matrix4d m = Eigen::Matrix4d::Identity();
        m(0, 3) = u;
        return m;
    });
    std::vector<cross_section> sections;
    double expected_volume = 0.;
    bool retained_curves = false;
    const double pi = boost::math::constants::pi<double>();
    auto circle_profile = [&](double radius) {
        auto c = tx::make<tx::circle>();
        c->radius = radius;
        c->matrix = tx::make<tx::matrix4>();
        auto e = tx::make<tx::edge>();
        e->basis = c;
        e->start = 0.;
        e->end = 2. * pi;
        auto l = tx::make<tx::loop>();
        l->external = true;
        l->closed = true;
        l->children = {e};
        auto f = tx::make<tx::face>();
        f->children = {l};
        return f;
    };
    SECTION("Changing circular radius across three authored sections") {
        for (auto entry : {std::pair<double, double>{0., 1.}, {5., 1.}, {10., 3.}}) {
            sections.push_back({entry.first, circle_profile(entry.second), Eigen::Vector3d::Zero(), {}, {}});
        }
        expected_volume = pi * (5. + 5. * (1. + 3. + 9.) / 3.);
    }
    SECTION("Rounded rectangle with only the right curved edges changing") {
        for (auto entry : {std::pair<double, double>{0., 4.}, {10., 6.}}) {
            auto face = tx::make<tx::face>();
            face->children = {profile_helper(nullptr, {{{0., 0.}, 0.25}, {{entry.second, 0.}, 0.25},
                {{entry.second, 2.}, 0.25}, {{0., 2.}, 0.25}})};
            sections.push_back({entry.first, face, Eigen::Vector3d::Zero(), {}, {}});
        }
        expected_volume = (10. - (4. - pi) * 0.25 * 0.25) * 10.;
        retained_curves = true;
    }
    SECTION("Equivalent circles at changing parent placements") {
        for (double distance : {0., 10.}) {
            auto face = circle_profile(1.);
            face->matrix = tx::make<tx::matrix4>();
            face->matrix->components()(1, 3) = distance / 40.;
            sections.push_back({distance, face, Eigen::Vector3d::Zero(), {}, {}});
        }
        expected_volume = pi * 10.;
        retained_curves = true;
    }
    settings settings;
    settings.set("circle-segments", 64);
    settings.set("cache-shapes", false);
    settings.set("reorient-shells", true);
    ifcopenshell::logger logger;
    logger.output_format(ifcopenshell::logger::FMT_INMEMORY);
    const auto original = sections.front().section_geometry;
    const auto original_loop = std::static_pointer_cast<tx::face>(original)->children.front();
    const auto original_edges = original_loop->children;
    auto loft = make_loft(settings, instance, path, sections, logger);
    REQUIRE(loft);
    loft->instance = instance;
    REQUIRE(loft->is_polygonal() != retained_curves);
    size_t count = 0;
    auto polygonal = loft->make_polygonal_sections(settings);
    for (const auto& section : polygonal->children) {
        auto loop = std::static_pointer_cast<tx::face>(section)->children.front();
        if (count == 0) count = loop->children.size();
        REQUIRE(loop->children.size() == count);
    }
    std::vector<std::string> backends = {"passthrough"};
#ifdef TAXONOMY_TEST_OPENCASCADE
    backends.push_back("opencascade");
#endif
#ifdef TAXONOMY_TEST_MANIFOLD
    backends.push_back("manifold");
#endif
#ifdef TAXONOMY_TEST_CGAL
    backends.push_back("cgal");
#endif
#ifdef TAXONOMY_TEST_CGAL_SIMPLE
    backends.push_back("cgal-simple");
#endif
    double reference_volume = 0.;
    for (bool ruled : {false, true}) {
        settings.set("loft-use-ruled-surfaces", ruled);
        for (const auto& backend : backends) {
            CAPTURE(backend, ruled);
            auto kernel = kernels::construct(nullptr, backend, settings, logger);
            kernel->propagate_exceptions = true;
            std::vector<conversion_result> shapes;
            REQUIRE(kernel->convert(loft, shapes));
            REQUIRE(shapes.size() == 1);
            const double volume = shapes.front().shape()->volume().to_double();
            REQUIRE(volume == Catch::Approx(expected_volume).epsilon(0.005));
            if (!reference_volume) reference_volume = volume;
            REQUIRE(volume == Catch::Approx(reference_volume).epsilon(ruled && backend == "opencascade" ? 0.005 : 1.e-6));
        }
    }
    REQUIRE(sections.front().section_geometry == original);
    REQUIRE(original_loop->children == original_edges);
    REQUIRE_FALSE(original_edges.front()->polygon_segments);
}

#ifdef TAXONOMY_TEST_OPENCASCADE
TEST_CASE("OpenCascade logs unsupported loft section counts", "[kernels][opencascade]") {
    namespace tx = ifcopenshell::geom::taxonomy;
    using namespace ifcopenshell::geom;
    hierarchy_helper<IfcSchema> file;
    auto loft = tx::make<tx::loft>();
    loft->instance = file.create<IfcSchema::IfcBuildingElementProxy>();
    // Analytic, non-polygonal directrices remain outside the interpolated route.
    loft->axis = tx::make<tx::circle>();
    for (double z : {0., 1., 2.}) {
        auto circle = tx::make<tx::circle>();
        circle->radius = 1.;
        circle->matrix = tx::make<tx::matrix4>();
        circle->matrix->components()(2, 3) = z;
        auto edge = tx::make<tx::edge>();
        edge->basis = circle;
        edge->start = 0.;
        edge->end = 2. * boost::math::constants::pi<double>();
        auto loop = tx::make<tx::loop>();
        loop->external = true;
        loop->children = {edge};
        auto face = tx::make<tx::face>();
        face->children = {loop};
        loft->children.push_back(face);
    }
    settings settings;
    settings.set("cache-shapes", false);
    ifcopenshell::logger logger;
    std::ostringstream log;
    logger.set_output(nullptr, &log);
    auto kernel = kernels::construct(nullptr, "opencascade", settings, logger);
    std::vector<conversion_result> converted;
    REQUIRE_FALSE(kernel->convert(loft, converted));
    REQUIRE(converted.empty());
    REQUIRE(logger.max_severity() == ifcopenshell::logger::LOG_ERROR);
    REQUIRE(log.str().find("lofting more than two non-polygonal sections is not supported; got 3 sections") != std::string::npos);
    REQUIRE(log.str().find("#" + std::to_string(loft->instance.id())) != std::string::npos);

    loft->children.resize(1);
    REQUIRE_FALSE(kernel->convert(loft, converted));
    REQUIRE(log.str().find("loft requires at least two sections; got 1") != std::string::npos);
}
#endif

#ifdef TAXONOMY_TEST_MANIFOLD
TEST_CASE("Manifold skips degenerate faces and preserves valid faces", "[kernels][manifold]") {
    namespace tx = ifcopenshell::geom::taxonomy;
    using namespace ifcopenshell::geom;
    hierarchy_helper<IfcSchema> file;
    auto make_face = [](std::initializer_list<Eigen::Vector3d> coordinates) {
        std::vector<tx::point3::ptr> points;
        for (const auto& coordinate : coordinates) {
            points.push_back(tx::make<tx::point3>(coordinate));
        }
        points.push_back(points.front());
        auto face = tx::make<tx::face>();
        face->children.push_back(polygon_from_points(points));
        return face;
    };
    auto valid = make_face({{0., 0., 0.}, {1., 0., 0.}, {0., 1., 0.}});
    tx::face::ptr degenerate;
    SECTION("Collinear vertices") {
        degenerate = make_face({{0., 0., 0.}, {1., 0., 0.}, {2., 0., 0.}});
    }
    SECTION("Coincident vertices") {
        degenerate = make_face({{0., 0., 0.}, {0., 0., 0.}, {0., 0., 0.}});
    }
    SECTION("Fewer than three vertices") {
        degenerate = make_face({{0., 0., 0.}, {1., 0., 0.}});
    }
    SECTION("Vertices collapse at conversion precision") {
        degenerate = make_face({{0., 0., 0.}, {1.e-7, 0., 0.}, {0., 1.e-7, 0.}});
    }
    auto shell = tx::make<tx::shell>();
    shell->instance = file.create<IfcSchema::IfcBuildingElementProxy>();
    shell->children = {degenerate, valid};
    settings settings;
    settings.set("cache-shapes", false);
    settings.set("precision", 1.e-5);
    ifcopenshell::logger logger;
    std::ostringstream log;
    logger.set_output(nullptr, &log);
    auto kernel = kernels::construct(nullptr, "manifold", settings, logger);
    std::vector<conversion_result> converted;
    REQUIRE(kernel->convert(shell, converted));
    REQUIRE(converted.size() == 1);
    REQUIRE(converted.front().shape()->num_faces() == 1);
    REQUIRE(logger.max_severity() == ifcopenshell::logger::LOG_WARNING);
    REQUIRE(log.str().find("skipping degenerate shell face 1/2") != std::string::npos);

    shell->children = {degenerate};
    converted.clear();
    REQUIRE_FALSE(kernel->convert(shell, converted));
    REQUIRE(converted.empty());
    REQUIRE(log.str().find("no non-degenerate faces") != std::string::npos);

    valid->children.front()->children.front()->basis = tx::make<tx::circle>();
    shell->children = {valid};
    REQUIRE_FALSE(kernel->convert(shell, converted));
    REQUIRE(log.str().find("unsupported face boundary") != std::string::npos);
}
#endif

namespace {

// A wall whose box sits 3 km east and 4 km north of its own placement, which
// itself is 1 m east and 2 m north of the storey origin. Lengths are in mm.
IfcSchema::IfcWallStandardCase add_far_away_wall(hierarchy_helper<IfcSchema>& file) {
    auto wall = file.create<IfcSchema::IfcWallStandardCase>();
    wall.setGlobalId(ifcopenshell::global_id());
    file.addBuildingProduct(wall);
    const auto storey_placement = file.getSingle<IfcSchema::IfcBuildingStorey>().ObjectPlacement();
    wall.setObjectPlacement(file.addLocalPlacement(storey_placement, 1000.0, 2000.0, 0.0));
    wall.setRepresentation(file.addBox(
        400.0, 300.0, 2500.0,
        IfcSchema::IfcAxis2Placement2D{},
        file.addPlacement3d(3000000.0, 4000000.0, 0.0)));
    return wall;
}

std::unique_ptr<ifcopenshell::geom::native_element> convert_wall(
    hierarchy_helper<IfcSchema>& file,
    const IfcSchema::IfcWallStandardCase& wall,
    ifcopenshell::geom::settings settings)
{
    ifcopenshell::logger log;
    log.output_format(ifcopenshell::logger::FMT_INMEMORY);
    ifcopenshell::geom::converter converter(
        ifcopenshell::geom::kernels::construct(&file, "opencascade", settings, log), &file, settings, log);
    std::unique_ptr<ifcopenshell::geom::native_element> element(
        converter.create_brep_for_representation_and_product(wall.Representation().Representations().back(), wall));
    REQUIRE(element);
    return element;
}

using Vertices = Eigen::Map<const Eigen::Matrix<double, 3, Eigen::Dynamic>>;

Vertices vertices_of(const ifcopenshell::geom::triangulation& geometry) {
    REQUIRE(geometry.verts().size() >= 3);
    return Vertices(geometry.verts().data(), 3, geometry.verts().size() / 3);
}

Eigen::Vector3d bbox_centre(const ifcopenshell::geom::triangulation& geometry) {
    const auto verts = vertices_of(geometry);
    return (verts.rowwise().minCoeff() + verts.rowwise().maxCoeff()) / 2.0;
}

Eigen::Vector3d rebase_offset_of(const ifcopenshell::geom::triangulation& geometry) {
    REQUIRE(geometry.rebase_offset().size() == 3);
    return Eigen::Map<const Eigen::Vector3d>(geometry.rebase_offset().data());
}

Eigen::Vector3d translation_of(const ifcopenshell::geom::element& element) {
    return element.transformation().data()->ccomponents().block<3, 1>(0, 3);
}

Eigen::Vector3d world_first_vertex(const ifcopenshell::geom::triangulation_element& element) {
    const Eigen::Vector4d local = vertices_of(element.geometry()).col(0).homogeneous();
    return (element.transformation().data()->ccomponents() * local).head<3>();
}

} // namespace

TEST_CASE("IfcGeom vertex rebase is off by default", "[ifcgeom][rebase]") {
    hierarchy_helper<IfcSchema> file;
    auto wall = add_far_away_wall(file);
    ifcopenshell::geom::settings settings;
    ifcopenshell::geom::triangulation_element element(*convert_wall(file, wall, settings));

    REQUIRE(vertices_of(element.geometry()).cwiseAbs().maxCoeff() > 3000.0);
    REQUIRE(rebase_offset_of(element.geometry()).isZero());
    REQUIRE(translation_of(element).isApprox(Eigen::Vector3d(1.0, 2.0, 0.0)));
}

TEST_CASE("IfcGeom vertex rebase shifts vertices and folds the offset into the placement", "[ifcgeom][rebase]") {
    hierarchy_helper<IfcSchema> file;
    auto wall = add_far_away_wall(file);
    ifcopenshell::geom::settings settings;
    ifcopenshell::geom::triangulation_element original(*convert_wall(file, wall, settings));
    settings.set("vertex-rebase-distance", 1000.0);
    const auto native = convert_wall(file, wall, settings);
    ifcopenshell::geom::triangulation_element rebased(*native);

    const Eigen::Vector3d original_centre = bbox_centre(original.geometry());
    REQUIRE(rebase_offset_of(rebased.geometry()).isApprox(original_centre));
    REQUIRE(bbox_centre(rebased.geometry()).isZero(1e-9));
    REQUIRE(vertices_of(rebased.geometry()).cwiseAbs().maxCoeff() < 10.0);
    REQUIRE(rebased.geometry().verts().size() == original.geometry().verts().size());
    REQUIRE(translation_of(rebased).isApprox(Eigen::Vector3d(1.0, 2.0, 0.0) + original_centre));
    REQUIRE(world_first_vertex(rebased).isApprox(world_first_vertex(original)));

    SECTION("an element reusing the geometry gets the same placement fold") {
        ifcopenshell::geom::triangulation_element reused(*native, rebased.geometry_pointer());
        REQUIRE(reused.geometry_pointer() == rebased.geometry_pointer());
        REQUIRE(translation_of(reused).isApprox(translation_of(rebased)));
    }
}

TEST_CASE("IfcGeom vertex rebase keeps vertices, offset and placement in file units", "[ifcgeom][rebase]") {
    hierarchy_helper<IfcSchema> file;
    auto wall = add_far_away_wall(file);
    ifcopenshell::geom::settings settings;
    settings.set("convert-back-units", true);
    ifcopenshell::geom::triangulation_element original(*convert_wall(file, wall, settings));
    settings.set("vertex-rebase-distance", 1000.0);
    ifcopenshell::geom::triangulation_element rebased(*convert_wall(file, wall, settings));

    const Eigen::Vector3d original_centre = bbox_centre(original.geometry());
    REQUIRE(original_centre.norm() > 3000000.0);
    REQUIRE(rebase_offset_of(rebased.geometry()).isApprox(original_centre));
    REQUIRE(vertices_of(rebased.geometry()).cwiseAbs().maxCoeff() < 10000.0);
    REQUIRE(translation_of(rebased).isApprox(Eigen::Vector3d(1000.0, 2000.0, 0.0) + original_centre, 1e-9));
    REQUIRE(world_first_vertex(rebased).isApprox(world_first_vertex(original), 1e-9));
}
