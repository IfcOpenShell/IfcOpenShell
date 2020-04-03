#include "validation_utils.h"

using namespace ifcopenshell::geometry;

#include <CGAL/AABB_tree.h>
#include <CGAL/AABB_traits.h>
#include <CGAL/Polyhedron_3.h>
#include <CGAL/AABB_face_graph_triangle_primitive.h>

typedef Kernel_::FT FT;
typedef Kernel_::Point_3 Point;
typedef Kernel_::Segment_3 Segment;
typedef CGAL::Polyhedron_3<Kernel_> Polyhedron;
typedef CGAL::AABB_face_graph_triangle_primitive<Polyhedron> Primitive;
typedef CGAL::AABB_traits<Kernel_, Primitive> Traits;
typedef CGAL::AABB_tree<Traits> Tree;
typedef Tree::Point_and_primitive_id Point_and_primitive_id;

void fix_spaceboundaries(IfcParse::IfcFile& f, bool no_progress, bool quiet, bool stderr_progress) {
	intersection_validator v(f, { "IfcWall", "IfcSpace", "IfcSlab", "IfcCovering" }, 1.e-5, no_progress, quiet, stderr_progress);

	auto rels = f.instances_by_type("IfcRelSpaceBoundary");

	std::map<std::pair<const IfcUtil::IfcBaseClass*, const IfcUtil::IfcBaseClass*>, const IfcUtil::IfcBaseClass*> rel_by_space_elem;


	if (rels) {
		std::for_each(rels->begin(), rels->end(), [&rel_by_space_elem](const IfcUtil::IfcBaseClass* rel) {
			auto x = ((IfcUtil::IfcBaseEntity*)rel)->get_value<IfcUtil::IfcBaseClass*>("RelatingSpace");
			try {
				auto y = ((IfcUtil::IfcBaseEntity*)rel)->get_value<IfcUtil::IfcBaseClass*>("RelatedBuildingElement");
				rel_by_space_elem.insert({ { x,y }, rel });
			} catch (IfcParse::IfcException&) {
				// RelatedBuildingElement can be NULL
			}
		});
	}

	std::set<const IfcUtil::IfcBaseClass*> rels_encounted;

	IfcParse::IfcFile f2("boundaries-triangulated.ifc");
	if (!f2.good()) {
		return;
	}

	ifcopenshell::geometry::settings settings;

	settings.set(ifcopenshell::geometry::settings::USE_WORLD_COORDS, false);
	settings.set(ifcopenshell::geometry::settings::WELD_VERTICES, false);
	settings.set(ifcopenshell::geometry::settings::SEW_SHELLS, true);
	settings.set(ifcopenshell::geometry::settings::CONVERT_BACK_UNITS, true);
	settings.set(ifcopenshell::geometry::settings::DISABLE_TRIANGULATION, true);
	settings.set(ifcopenshell::geometry::settings::DISABLE_OPENING_SUBTRACTIONS, true);

	ifcopenshell::geometry::Converter c("cgal", &f2, settings);

	std::map<std::set<std::string>, std::vector<Kernel_::Point_3>> elem_to_space_boundary_coords;

	for (auto& i : *f2.instances_by_type("IfcProduct")) {
		auto n = ((IfcUtil::IfcBaseEntity*)i)->get_value<std::string>("Name");
		auto g1 = n.substr(0, 22);
		auto g2 = n.substr(23);
		auto item = c.mapping()->map(i);
		if (((ifcopenshell::geometry::taxonomy::collection*) item)->children[0] == nullptr) {
			continue;
		}
		auto shell = (taxonomy::shell*) ((taxonomy::collection*)((taxonomy::collection*) item)->children[0])->children[0];
		for (auto& f : shell->children) {
			auto face = (taxonomy::face*) f;
			for (auto& w : face->children) {
				auto wire = (taxonomy::loop*) w;
				for (auto& e : wire->children) {
					auto edge = (taxonomy::edge*) e;
					auto p3 = boost::get<taxonomy::point3>(edge->start);
					auto p4 = ((taxonomy::geom_item*)item)->matrix.components * p3.components.homogeneous();
					Kernel_::Point_3 P(p4(0), p4(1), p4(2));
					elem_to_space_boundary_coords[{g1, g2}].emplace_back(P);
				}
			}
		}
	}

	std::set< std::set<std::string> > guid_pairs_visited;

	v([&rel_by_space_elem, &elem_to_space_boundary_coords, &guid_pairs_visited](const intersection_validator::Box& a, const intersection_validator::Box& b) {
		std::ostringstream ss;
		// ss << id_map[a.id()]->first->data().toString() << "x" << id_map[b.id()]->first->data().toString() << std::endl;
		// auto x = id_map[a.id()]->second * id_map[b.id()]->second;

		auto A = a.handle()->first;
		auto B = b.handle()->first;

		auto Aguid = A->get_value<std::string>("GlobalId");
		auto Bguid = B->get_value<std::string>("GlobalId");

		int space_count = 0;
		if (A->declaration().name() == "IfcSpace") {
			space_count += 1;
		}
		if (B->declaration().name() == "IfcSpace") {
			space_count += 1;
		}
		if (space_count != 1) {
			return;
		}

		ss << a.handle()->first->data().toString() << "x" << a.handle()->first->data().toString() << std::endl;
		auto x = a.handle()->second * b.handle()->second;

		if (x.is_empty()) {
			return;
		}

		guid_pairs_visited.insert({ Aguid, Bguid });

		cgal_shape_t x_poly;
		x.convert_to_polyhedron(x_poly);

		{
			std::string fn = "computed_boundaries_" + Aguid + "_" + Bguid + ".off";
			std::ofstream computed_boundaries(fn.c_str());
			computed_boundaries.precision(17);
			computed_boundaries << x_poly;
		}

		Tree tree(faces(x_poly).first, faces(x_poly).second, x_poly);
		tree.accelerate_distance_queries();

		auto itelem = elem_to_space_boundary_coords.find({ Aguid, Bguid });

		if (itelem == elem_to_space_boundary_coords.end()) {
			Logger::Error("Missing space boundary relationship " + Aguid + " " + Bguid);
			return;
		}

		const auto& coords = itelem->second;
		std::vector<double> distances;
		std::transform(coords.begin(), coords.end(), std::back_inserter(distances), [&tree](const Kernel_::Point_3& p) {
			return std::sqrt(CGAL::to_double(tree.squared_distance(p)));
		});

		bool valid = *std::max_element(distances.begin(), distances.end()) < 0.4;

		if (!valid) {
			Logger::Error("Wrong connection geometry " + Aguid + " " + Bguid);
		}

		/*{
			remove_thickness r(x_poly);
			std::string fn = "thin_computed_boundaries_" + Aguid + "_" + Bguid + ".off";
			std::ofstream computed_boundaries(fn.c_str());
			computed_boundaries.precision(17);
			computed_boundaries << r.flattened;
		}*/

		/*
		{
			auto FN = s0 + "-" + s1 + "-" + std::to_string(i0) + "-" + std::to_string(i1) + "-sides-sb.off";
			std::ofstream os(FN.c_str());
			os.precision(17);
			os << r.polyhedron2;
		}
		{
			auto FN = s0 + "-" + s1 + "-" + std::to_string(i0) + "-" + std::to_string(i1) + "-flat-sb.off";
			std::ofstream os(FN.c_str());
			os.precision(17);
			os << r.flattened;
		}
		*/
	});

	auto is_wall_space_or_slab = [&f](const std::string& g) {
		auto decl = f.instance_by_guid(g)->declaration();
		return decl.is("IfcWall") || decl.is("IfcSpace") || decl.is("IfcSlab");
	};

	for (auto& i : *f2.instances_by_type("IfcProduct")) {
		auto n = ((IfcUtil::IfcBaseEntity*)i)->get_value<std::string>("Name");
		auto g1 = n.substr(0, 22);
		auto g2 = n.substr(23);
		if (is_wall_space_or_slab(g1) && is_wall_space_or_slab(g2) && guid_pairs_visited.find({ g1, g2 }) == guid_pairs_visited.end()) {
			Logger::Error("Space boundary for non-bounding geometry " + g1 + " " + g2);
		}
	}
}
