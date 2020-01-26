#include "validation_utils.h"

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

	v([&c](const intersection_validator::Box& a, const intersection_validator::Box& b) {
		std::ostringstream ss;

		ss << a.handle()->first->data().toString() << "x" << a.handle()->first->data().toString() << std::endl;
		auto x = a.handle()->second * b.handle()->second;
		if (x.is_empty()) {
			return;
		}

		c.convert(a.handle()->first);

		cgal_shape_t x_poly;
		x.convert_to_polyhedron(x_poly);

		for (auto& v : vertices(x_poly)) {
			// project onto axes
		}

		CGAL::Polygon_mesh_processing::triangulate_faces(x_poly);

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

