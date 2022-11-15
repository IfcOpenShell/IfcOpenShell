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
 * Geometrical data in an IFC file consists of shapes (IfcShapeRepresentation)  *
 * and instances (SUBTYPE OF IfcBuildingElement e.g. IfcWindow).                *
 *                                                                              *
 * IfcGeom::Representation::Triangulation is a class that represents a          *
 * triangulated IfcShapeRepresentation.                                         *
 *   Triangulation.verts is a 1 dimensional vector of float defining the        *
 *      cartesian coordinates of the vertices of the triangulated shape in the  *
 *      format of [x1,y1,z1,..,xn,yn,zn]                                        *
 *   Triangulation.faces is a 1 dimensional vector of int containing the        *
 *     indices of the triangles referencing positions in Triangulation.verts    *
 *   Triangulation.edges is a 1 dimensional vector of int in {0,1} that dictates*
 *	   the visibility of the edges that span the faces in Triangulation.faces   *
 *                                                                              *
 * IfcGeom::Element represents the actual IfcBuildingElements.                  *
 *   IfcGeomObject.name is the GUID of the element                              *
 *   IfcGeomObject.type is the datatype of the element e.g. IfcWindow           *
 *   IfcGeomObject.mesh is a pointer to an IfcMesh                              *
 *   IfcGeomObject.transformation.matrix is a 4x3 matrix that defines the       *
 *     orientation and translation of the mesh in relation to the world origin  *
 *                                                                              *
 * IfcGeom::Iterator::initialize()                                              *
 *   finds the most suitable representation contexts. Returns true iff          *
 *   at least a single representation will process successfully                 *
 *                                                                              *
 * IfcGeom::Iterator::get()                                                     *
 *   returns a pointer to the current IfcGeom::Element                          *
 *                                                                              *
 * IfcGeom::Iterator::next()                                                    *
 *   returns true iff a following entity is available for a successive call to  *
 *   IfcGeom::Iterator::get()                                                   *
 *                                                                              *
 * IfcGeom::Iterator::progress()                                                *
 *   returns an int in [0..100] that indicates the overall progress             *
 *                                                                              *
 ********************************************************************************/

#ifndef IFCGEOMITERATOR_H
#define IFCGEOMITERATOR_H

#include "../ifcgeom_schema_agnostic/IteratorImplementation.h"

// The infamous min & max Win32 #defines can leak here from OCE depending on the build configuration
#ifdef min
#undef min
#endif
#ifdef max
#undef max
#endif

namespace IfcGeom {

	class IFC_GEOM_API Iterator {
	private:
		Iterator(const Iterator&); // N/I
		Iterator& operator=(const Iterator&); // N/I

		IfcParse::IfcFile* file_;
		IfcGeom::IteratorSettings settings_;
		std::vector<IfcGeom::filter_t> filters_;

		IteratorImplementation* implementation_;

	public:
		Iterator(const IfcGeom::IteratorSettings& settings, IfcParse::IfcFile* file, int num_threads = 1)
			: file_(file)
			, settings_(settings)
		{
			try {
				implementation_ = iterator_implementations().construct(file_->schema()->name(), settings, file, filters_, num_threads);
			} catch (const std::exception& e) {
				Logger::Error(e);
				implementation_ = nullptr;
			}
		}

		Iterator(const IfcGeom::IteratorSettings& settings, IfcParse::IfcFile* file, const std::vector<IfcGeom::filter_t>& filters, int num_threads = 1)
			: file_(file)
			, settings_(settings)
			, filters_(filters)
		{
			try {
				implementation_ = iterator_implementations().construct(file_->schema()->name(), settings, file, filters_, num_threads);
			} catch (const std::exception& e) {
				Logger::Error(e);
				implementation_ = nullptr;
			}
		}

		bool initialize() {
			if (implementation_) {
				return implementation_->initialize();
			} else {
				return false;
			}
		}

		int progress() const { return implementation_->progress(); }

		void compute_bounds(bool with_geometry) { implementation_->compute_bounds(with_geometry); }

		const gp_XYZ& bounds_min() const { return implementation_->bounds_min(); }
		const gp_XYZ& bounds_max() const { return implementation_->bounds_max(); }

		const std::string& unit_name() const { return implementation_->getUnitName(); }

		double unit_magnitude() const { return implementation_->getUnitMagnitude(); }

		IfcParse::IfcFile* file() const { return implementation_->file(); }

		IfcUtil::IfcBaseClass* next() const { return implementation_->next(); }

		Element* get() { return implementation_->get(); }

		BRepElement* get_native() { return implementation_->get_native(); }

		const Element* get_object(int id) { return implementation_->get_object(id); }

		IfcUtil::IfcBaseClass* create() { return implementation_->create(); }

		void set_cache(GeometrySerializer* cache) { return implementation_->set_cache(cache); }
	};
}

#endif
