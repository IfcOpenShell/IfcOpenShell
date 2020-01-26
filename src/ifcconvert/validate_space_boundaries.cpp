#include "validation_utils.h"

void fix_spaceboundaries(IfcParse::IfcFile& f, bool no_progress, bool quiet, bool stderr_progress) {
	intersection_validator v(f, { "IfcWall", "IfcSpace" }, no_progress, quiet, stderr_progress);
	
	v([](const intersection_validator::Box& a, const intersection_validator::Box& b) {
		std::ostringstream ss;
		// ss << id_map[a.id()]->first->data().toString() << "x" << id_map[b.id()]->first->data().toString() << std::endl;
		// auto x = id_map[a.id()]->second * id_map[b.id()]->second;

		ss << a.handle()->first->data().toString() << "x" << a.handle()->first->data().toString() << std::endl;
		auto x = a.handle()->second * b.handle()->second;
		cgal_shape_t x_poly;
		x.convert_to_polyhedron(x_poly);

		CGAL::Polygon_mesh_processing::triangulate_faces(x_poly);

		auto vs = vertices(x_poly);
		if (std::distance(vs.begin(), vs.end()) == 0) {
			return;
		}

		auto s0 = a.handle()->first->declaration().name();
		auto s1 = b.handle()->first->declaration().name();
		auto i0 = a.handle()->first->data().id();
		auto i1 = b.handle()->first->data().id();

		if (s0 < s1) {
			std::swap(s1, s0);
			std::swap(i0, i1);
		}

		{
			auto FN = s0 + "-" + s1 + "-" + std::to_string(i0) + "-" + std::to_string(i1) + "sb.off";

			std::ofstream os(FN.c_str());
			os.precision(17);
			os << x_poly;
		}

		remove_thickness r(x_poly);

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
	});
}
