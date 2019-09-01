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

#include "CgalKernel.h"

#include "../../../ifcparse/IfcLogger.h"
#include "../../../ifcgeom/kernels/cgal/CgalConversionResult.h"

using namespace ifcopenshell::geometry; 
using namespace ifcopenshell::geometry::kernels;

void CgalKernel::remove_duplicate_points_from_loop(cgal_wire_t& polygon) {
	std::set<cgal_point_t> points;
	for (int i = 0; i < polygon.size(); ++i) {
		if (points.count(polygon[i])) {
			polygon.erase(polygon.begin() + i);
			--i;
		} else points.insert(polygon[i]);
	}
}

CGAL::Polyhedron_3<Kernel_> CgalKernel::create_polyhedron(std::list<cgal_face_t> &face_list) {

	// Naive creation
	CGAL::Polyhedron_3<Kernel_> polyhedron;
	PolyhedronBuilder builder(&face_list);
	polyhedron.delegate(builder);

	// Stitch edges
	//  std::cout << "Before: " << polyhedron.size_of_vertices() << " vertices and " << polyhedron.size_of_facets() << " facets" << std::endl;
	CGAL::Polygon_mesh_processing::stitch_borders(polyhedron);
	if (!polyhedron.is_valid()) {
		Logger::Message(Logger::LOG_ERROR, "create_polyhedron: Polyhedron not valid!");
		//    std::ofstream fresult;
		//    fresult.open("/Users/ken/Desktop/invalid.off");
		//    fresult << polyhedron << std::endl;
		//    fresult.close();
		return CGAL::Polyhedron_3<Kernel_>();
	} if (polyhedron.is_closed()) {
		if (!CGAL::Polygon_mesh_processing::is_outward_oriented(polyhedron)) {
			CGAL::Polygon_mesh_processing::reverse_face_orientations(polyhedron);
		}
	}

	//  std::cout << "After: " << polyhedron.size_of_vertices() << " vertices and " << polyhedron.size_of_facets() << " facets" << std::endl;

	return polyhedron;
}

CGAL::Polyhedron_3<Kernel_> CgalKernel::create_polyhedron(CGAL::Nef_polyhedron_3<Kernel_> &nef_polyhedron) {
	if (nef_polyhedron.is_simple()) {
		try {
			CGAL::Polyhedron_3<Kernel_> polyhedron;
			nef_polyhedron.convert_to_polyhedron(polyhedron);
			return polyhedron;
		} catch (...) {
			Logger::Message(Logger::LOG_ERROR, "Conversion from Nef to polyhedron failed!");
			return CGAL::Polyhedron_3<Kernel_>();
		}
	} else {
		Logger::Message(Logger::LOG_ERROR, "Nef polyhedron not simple: cannot create polyhedron!");
		return CGAL::Polyhedron_3<Kernel_>();
	}
}

CGAL::Nef_polyhedron_3<Kernel_> CgalKernel::create_nef_polyhedron(std::list<cgal_face_t> &face_list) {
	CGAL::Polyhedron_3<Kernel_> polyhedron = create_polyhedron(face_list);
	CGAL::Polygon_mesh_processing::triangulate_faces(polyhedron);
	CGAL::Nef_polyhedron_3<Kernel_> nef_polyhedron;
	try {
		nef_polyhedron = CGAL::Nef_polyhedron_3<Kernel_>(polyhedron);
	} catch (...) {
		Logger::Message(Logger::LOG_ERROR, "Conversion to Nef polyhedron failed!");
		return nef_polyhedron;
	} return nef_polyhedron;
}

CGAL::Nef_polyhedron_3<Kernel_> CgalKernel::create_nef_polyhedron(CGAL::Polyhedron_3<Kernel_> &polyhedron) {
	if (polyhedron.is_valid()) {
		CGAL::Polygon_mesh_processing::triangulate_faces(polyhedron);
		CGAL::Nef_polyhedron_3<Kernel_> nef_polyhedron;
		try {
			nef_polyhedron = CGAL::Nef_polyhedron_3<Kernel_>(polyhedron);
		} catch (...) {
			Logger::Message(Logger::LOG_ERROR, "Conversion to Nef polyhedron failed!");
			return nef_polyhedron;
		} return nef_polyhedron;
	} else {
		Logger::Message(Logger::LOG_ERROR, "Polyhedron not valid: cannot create Nef polyhedron!");
		return CGAL::Nef_polyhedron_3<Kernel_>();
	}
}

bool CgalKernel::convert(const taxonomy::shell* l, cgal_shape_t& shape) {
	auto faces = l->children_as<taxonomy::face>();

	std::list<cgal_face_t> face_list;
	for (auto& f : faces) {
		bool success = false;
		cgal_face_t face;

		try {
			success = convert(f, face);
		} catch (...) {}

		if (!success) {
			Logger::Message(Logger::LOG_WARNING, "Failed to convert face:", f->instance);
			continue;
		}

		//    std::cout << "Face in ConnectedFaceSet: " << std::endl;
		//    for (auto &point: face.outer) {
		//      std::cout << "\tPoint(" << point << ")" << std::endl;
		//    }

		face_list.push_back(face);
	}

	shape = create_polyhedron(face_list);
	return true;
}

bool CgalKernel::convert(const taxonomy::face* face, cgal_face_t& result) {
	auto bounds = face->children_as<taxonomy::loop>();

	int num_outer_bounds = 0;

	for (auto& bound : bounds) {
		if (bound->external.get_value_or(false)) num_outer_bounds++;
	}

	if (num_outer_bounds != 1) {
		Logger::Message(Logger::LOG_ERROR, "Invalid configuration of boundaries for:", face->instance);
		return false;
	}

	cgal_face_t mf;

	for (auto& bound : bounds) {

		const bool is_interior = !bound->external.get_value_or(false);

		cgal_wire_t wire;
		if (!convert(bound, wire)) {
			Logger::Message(Logger::LOG_ERROR, "Failed to process face boundary loop", bound->instance);
			return false;
		}

		if (!is_interior) {
			mf.outer = wire;
		} else {
			mf.inner.push_back(wire);
		}
	}

	result = mf;

	//  std::cout << "Face: " << std::endl;
	//  for (auto &point: face.outer) {
	//    std::cout << "\tPoint(" << point << ")" << std::endl;
	//  }

	return true;
}

bool CgalKernel::convert(const taxonomy::loop* loop, cgal_wire_t& result) {
	// @todo only implement polygonal loops

	auto edges = loop->children_as<taxonomy::edge>();
	std::vector<taxonomy::point3> points;

	for (auto& e : edges) {
		if (e->basis) {
			return false;
		}
		points.push_back(boost::get<taxonomy::point3>(e->start));
	}

	// Parse and store the points in a sequence
	cgal_wire_t polygon = std::vector<Kernel_::Point_3>();
	for (auto& p : points) {
		cgal_point_t pnt(p.components(0), p.components(1), p.components(2));
		polygon.push_back(pnt);
	}

	// A loop should consist of at least three vertices
	std::size_t original_count = polygon.size();
	if (original_count < 3) {
		Logger::Message(Logger::LOG_ERROR, "Not enough edges for:", loop->instance);
		return false;
	}

	// Remove points that are too close to one another
	remove_duplicate_points_from_loop(polygon);

	std::size_t count = polygon.size();
	if (original_count - count != 0) {
		std::stringstream ss; ss << (original_count - count) << " edges removed for:";
		Logger::Message(Logger::LOG_WARNING, ss.str(), loop->instance);
	}

	if (count < 3) {
		Logger::Message(Logger::LOG_ERROR, "Not enough edges for:", loop->instance);
		return false;
	}

	result = polygon;

	//  std::cout << "PolyLoop: " << std::endl;
	//  for (auto &point: polygon) {
	//    std::cout << "\tPoint(" << point << ")" << std::endl;
	//  }

	return true;
}


bool CgalKernel::convert_impl(const taxonomy::shell *shell, ifcopenshell::geometry::ConversionResults& results) {
	cgal_shape_t shape;
	if (!convert(shell, shape)) {
		return false;
	}
	results.emplace_back(ConversionResult(
		shell->instance->data().id(),
		shell->matrix,
		new CgalShape(shape),
		shell->surface_style
	));
	return true;
}
