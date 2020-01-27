#include "validation_utils.h"

#include <algorithm>

using namespace ifcopenshell::geometry;

void fix_wallconnectivity(IfcParse::IfcFile& f, bool no_progress, bool quiet, bool stderr_progress) {
	intersection_validator v(f, { "IfcWall" }, no_progress, quiet, stderr_progress);


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

	v([&c, &rel_by_elem, &rels_encounted](const intersection_validator::Box& a, const intersection_validator::Box& b) {
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
		auto x = a.handle()->second * b.handle()->second;
		if (x.is_empty()) {
			return;
		}

		cgal_shape_t x_poly;
		x.convert_to_polyhedron(x_poly);

		auto get_axis_parameter_min_max = [&c, &x_poly](IfcUtil::IfcBaseEntity* inst) {
			auto item = c.mapping()->map(inst);
			auto shaperep = ((taxonomy::collection*) item)->children[0];
			auto loop = ((taxonomy::collection*) shaperep)->children[0];

			if (loop->kind() != taxonomy::LOOP) {
				std::wcout << "no suitable axis" << std::endl;
			} else {
				auto first_vertex = ((taxonomy::edge*) ((taxonomy::loop*) loop)->children.front())->start;
				auto last_vertex = ((taxonomy::edge*) ((taxonomy::loop*) loop)->children.back())->end;

				if (first_vertex.which() != 0 || last_vertex.which() != 0) {
					std::wcout << "trims not supported" << std::endl;
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
					return std::make_pair(len, std::make_pair(CGAL::to_double(*pit.first), CGAL::to_double(*pit.first)));
				}				
			}
			const auto& nan = std::numeric_limits<double>::quiet_NaN();
			return std::make_pair(nan, std::make_pair(nan, nan));
		};

		auto qualify_connection_type = [](double l, const std::pair<double, double>& p) {
			if (p.first < 1.e-5) {
				return "ATSTART";
			} else if (p.second > l - 1.e-5) {
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
				auto rel_str = rel->data().toString();
				std::wcout << "ERROR: " << rel_str.c_str() << " " << atype_computed << " " << btype_computed << std::endl;
			} else {
				auto A_str = A->data().toString();
				auto B_str = B->data().toString();
				std::wcout << "ERROR: no rel " << A_str.c_str() << " x " << B_str.c_str() << " " << atype_computed << " " << btype_computed << std::endl;
			}
		}
	});

	std::for_each(rels->begin(), rels->end(), [&rels_encounted](const IfcUtil::IfcBaseClass* rel) {
		if (rels_encounted.find(rel) == rels_encounted.end()) {
			auto rel_str = rel->data().toString();
			std::wcout << "ERROR: " << rel_str.c_str() << " not found" << std::endl;
		}
	});
}

