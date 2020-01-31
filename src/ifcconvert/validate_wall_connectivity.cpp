#include "validation_utils.h"

#include <CGAL/Polygon_mesh_processing/bbox.h>
#include <CGAL/Polygon_mesh_processing/measure.h>

#include <algorithm>

using namespace ifcopenshell::geometry;

void fix_wallconnectivity(IfcParse::IfcFile& f, bool no_progress, bool quiet, bool stderr_progress) {
	intersection_validator v(f, { "IfcWall" }, 1.e-3, no_progress, quiet, stderr_progress);


	ifcopenshell::geometry::settings settings;
	settings.set(ifcopenshell::geometry::settings::USE_WORLD_COORDS, false);
	settings.set(ifcopenshell::geometry::settings::WELD_VERTICES, false);
	settings.set(ifcopenshell::geometry::settings::SEW_SHELLS, true);
	settings.set(ifcopenshell::geometry::settings::CONVERT_BACK_UNITS, true);
	settings.set(ifcopenshell::geometry::settings::DISABLE_TRIANGULATION, true);
	settings.set(ifcopenshell::geometry::settings::DISABLE_OPENING_SUBTRACTIONS, true);

	settings.set(ifcopenshell::geometry::settings::INCLUDE_CURVES, true);
	settings.set(ifcopenshell::geometry::settings::EXCLUDE_SOLIDS_AND_SURFACES, true);
	
	ifcopenshell::geometry::Converter c("cgal", &f, settings);

	auto rels = f.instances_by_type("IfcRelConnectsPathElements");
	std::map<std::set<const IfcUtil::IfcBaseClass*>, const IfcUtil::IfcBaseClass*> rel_by_elem;
	std::for_each(rels->begin(), rels->end(), [&rel_by_elem](const IfcUtil::IfcBaseClass* rel) {
		auto x = ((IfcUtil::IfcBaseEntity*)rel)->get_value<IfcUtil::IfcBaseClass*>("RelatingElement");
		auto y = ((IfcUtil::IfcBaseEntity*)rel)->get_value<IfcUtil::IfcBaseClass*>("RelatedElement");
		rel_by_elem.insert({{ x,y }, rel});
	});

	std::set<const IfcUtil::IfcBaseClass*> rels_encounted;

	double total_nef_intersection_time = 0.;
	double conversion_to_poly = 0.;

	v([&c, &rel_by_elem, &rels_encounted, &total_nef_intersection_time, &conversion_to_poly](const intersection_validator::Box& a, const intersection_validator::Box& b) {
		auto A = a.handle()->first;
		auto B = b.handle()->first;

		const IfcUtil::IfcBaseClass* rel = nullptr;
		std::string a_type, b_type;

		auto rit = rel_by_elem.find({ A, B });
		if (rit != rel_by_elem.end()) {
			rel = rit->second;
			const bool a_is_relating = A == ((IfcUtil::IfcBaseEntity*)rel)->get_value<IfcUtil::IfcBaseClass*>("RelatingElement");
			a_type = ((IfcUtil::IfcBaseEntity*)rel)->get_value<std::string>("RelatingConnectionType");
			b_type = ((IfcUtil::IfcBaseEntity*)rel)->get_value<std::string>("RelatedConnectionType");
			if (!a_is_relating) {
				std::swap(a_type, b_type);
			}
		}		

#if 0
		auto a_poly = ifcopenshell::geometry::utils::create_polyhedron(a.handle()->second);
		auto b_poly = ifcopenshell::geometry::utils::create_polyhedron(b.handle()->second);

		std::wcout << "a" << std::endl;
		for (auto& v : vertices(a_poly)) {
			for (int i = 0; i < 3; ++i) {
				std::wcout << CGAL::to_double(v->point().cartesian(i)) << " ";
			}
			std::wcout << std::endl;
		}

		std::wcout << "b" << std::endl;
		for (auto& v : vertices(b_poly)) {
			for (int i = 0; i < 3; ++i) {
				std::wcout << CGAL::to_double(v->point().cartesian(i)) << " ";
			}
			std::wcout << std::endl;
		}
#endif

		std::ostringstream ss;
		ss << A->data().toString() << "x" << B->data().toString() << std::endl;
		std::clock_t intersection_begin = std::clock();
		auto x = a.handle()->second * b.handle()->second;
		std::clock_t intersection_end = std::clock();

		total_nef_intersection_time += (intersection_end - intersection_begin) / (double) CLOCKS_PER_SEC;

		if (x.is_empty()) {
			return;
		}

		std::clock_t poly_begin = std::clock();
		cgal_shape_t x_poly;
		x.convert_to_polyhedron(x_poly);
		std::clock_t poly_end = std::clock();
		conversion_to_poly += (poly_end - poly_begin) / (double)CLOCKS_PER_SEC;

		auto dza = a.bbox().zmax() - a.bbox().zmin();
		auto dzb = b.bbox().zmax() - b.bbox().zmin();
		auto bb = CGAL::Polygon_mesh_processing::bbox_3(x_poly);
		if (bb.zmax() - bb.zmin() < std::min(dza, dzb) / 3.) {
			return;
		}

		CGAL::Polygon_mesh_processing::triangulate_faces(x_poly);
		if (CGAL::Polygon_mesh_processing::area(x_poly) > 4.0) {
			return;
		}

		auto get_axis_parameter_min_max = [&c, &x_poly](IfcUtil::IfcBaseEntity* inst) {
			auto item = c.mapping()->map(inst);
			auto shaperep = ((taxonomy::collection*) item)->children[0];
			auto loop = ((taxonomy::collection*) shaperep)->children[0];

			if (loop->kind() != taxonomy::LOOP) {
				// std::wcout << "no suitable axis" << std::endl;
			} else {
				auto first_vertex = ((taxonomy::edge*) ((taxonomy::loop*) loop)->children.front())->start;
				auto last_vertex = ((taxonomy::edge*) ((taxonomy::loop*) loop)->children.back())->end;

				if (first_vertex.which() != 0 || last_vertex.which() != 0) {
					// std::wcout << "trims not supported" << std::endl;
				} else {
					auto p0 = boost::get<taxonomy::point3>(first_vertex);
					auto p1 = boost::get<taxonomy::point3>(last_vertex);
					
					auto v0 = ((taxonomy::geom_item*)item)->matrix.components * p0.components.homogeneous();
					auto v1 = ((taxonomy::geom_item*)item)->matrix.components * p1.components.homogeneous();

					auto P0 = Kernel_::Point_3(v0(0), v0(1), v0(2));
					auto P1 = Kernel_::Point_3(v1(0), v1(1), v1(2));

					auto D = P1 - P0;
					auto len = std::sqrt(CGAL::to_double(D.squared_length()));
					D /= len;

					std::vector<Kernel_::FT> parameters;

					std::transform(vertices(x_poly).begin(), vertices(x_poly).end(), std::back_inserter(parameters), [&P0, D](auto& v) {
						return (v->point() - P0) * D;
					});

					auto pit = std::minmax_element(parameters.begin(), parameters.end());
					return std::make_pair(len, std::make_pair(CGAL::to_double(*pit.first), CGAL::to_double(*pit.second)));
				}				
			}
			const auto& nan = std::numeric_limits<double>::quiet_NaN();
			return std::make_pair(nan, std::make_pair(nan, nan));
		};

		auto qualify_connection_type = [](double l, const std::pair<double, double>& p) {
			if (p.first < 1.e-3) {
				return "ATSTART";
			} else if (p.second > l - 1.e-3) {
				return "ATEND";
			} else {
				return "ATPATH";
			}
		};

		auto alu0u1 = get_axis_parameter_min_max(A);
		auto blu0u1 = get_axis_parameter_min_max(B);

		auto atype_computed = qualify_connection_type(alu0u1.first, alu0u1.second);
		auto btype_computed = qualify_connection_type(blu0u1.first, blu0u1.second);

		rels_encounted.insert(rel);

		if (a_type != atype_computed || b_type != btype_computed) {
			if (rel) {
				Logger::Error(std::string("Connection type ") + atype_computed + " " + btype_computed + " for:", rel);
			} else {
				auto A_str = A->get_value<std::string>("GlobalId");
				auto B_str = B->get_value<std::string>("GlobalId");
				Logger::Error("No connection for adjacent " + A_str + " " + B_str);
			}
		}
	});

	std::for_each(rels->begin(), rels->end(), [&rels_encounted, &v](const IfcUtil::IfcBaseClass* rel) {
		if (rels_encounted.find(rel) == rels_encounted.end()) {
			auto x = (IfcUtil::IfcBaseEntity*)((IfcUtil::IfcBaseEntity*)rel)->get_value<IfcUtil::IfcBaseClass*>("RelatingElement");
			auto y = (IfcUtil::IfcBaseEntity*)((IfcUtil::IfcBaseEntity*)rel)->get_value<IfcUtil::IfcBaseClass*>("RelatedElement");
			if (v.succesfully_processed.find(x) != v.succesfully_processed.end() && v.succesfully_processed.find(y) != v.succesfully_processed.end()) {
				Logger::Error("Connection for non-adjacent walls", rel);
			}
		}
	});

	std::wcout << std::setprecision(14);
	std::wcout << "total_map_time " << v.total_map_time << std::endl;
	std::wcout << "total_geom_time " << v.total_geom_time << std::endl;
	std::wcout << "total_nef_time " << v.total_nef_time << std::endl;
	std::wcout << "total_minkowsky_time " << v.total_minkowsky_time << std::endl;
	std::wcout << "total_box_time " << v.total_box_time << std::endl;
	std::wcout << "total_nef_intersection_time " << total_nef_intersection_time << std::endl;
	std::wcout << "total_conversion_to_poly_time " << conversion_to_poly << std::endl;
}

