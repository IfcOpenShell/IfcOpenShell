#include <algorithm>
#include <string>
#include <vector>

#include <catch2/catch_test_macros.hpp>

#include "ifcgeom/Converter.h"
#include "ifcgeom/kernel_registry.h"
#define IfcSchema Ifc2x3
#include "ifcparse/hierarchy_helper.h"
#include "ifcparse/macros.h"
#include "ifcparse/schemas/Ifc2x3.h"

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
    ifcopenshell::geometry::Settings settings;
    settings.set("max-voids-per-element", MAX_VOIDS);

    logger log;
    log.output_format(logger::FMT_INMEMORY);
    ifcopenshell::geometry::Converter converter(
        ifcopenshell::geometry::kernels::construct(&file, "opencascade", settings), &file, settings, log);
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
    ifcopenshell::geometry::Settings settings;
    settings.set("context-priorities", std::vector<std::string>(context_priorities));

    logger log;
    log.output_format(logger::FMT_INMEMORY);
    ifcopenshell::geometry::Converter converter(
        ifcopenshell::geometry::kernels::construct(&file, "passthrough", settings), &file, settings, log);

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

std::vector<ifcopenshell::geometry::geometry_conversion_task> representation_tasks(
    hierarchy_helper<IfcSchema>& file,
    const std::vector<std::string>& context_priorities)
{
    ifcopenshell::geometry::Settings settings;
    settings.set("context-priorities", std::vector<std::string>(context_priorities));

    logger log;
    log.output_format(logger::FMT_INMEMORY);
    ifcopenshell::geometry::Converter converter(
        ifcopenshell::geometry::kernels::construct(&file, "passthrough", settings), &file, settings, log);

    std::vector<ifcopenshell::geometry::geometry_conversion_task> tasks;
    std::vector<ifcopenshell::geometry::filter_t> filters;
    converter.mapping()->get_representations(tasks, filters);
    return tasks;
}

const ifcopenshell::geometry::geometry_conversion_task* task_for_product(
    const std::vector<ifcopenshell::geometry::geometry_conversion_task>& tasks,
    const express::Base& product)
{
    for (const auto& task : tasks) {
        if (std::any_of(task.products.begin(), task.products.end(), [&](const express::Base& task_product) {
                return task_product.id() == product.id();
            })) {
            return &task;
        }
    }
    return nullptr;
}

} // namespace

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
