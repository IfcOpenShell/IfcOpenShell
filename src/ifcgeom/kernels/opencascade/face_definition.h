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

#ifndef FACE_DEFINITION_H
#define FACE_DEFINITION_H

#include <TopoDS_Wire.hxx>
#include <Geom_Surface.hxx>

#include <map>
#include <vector>

namespace IfcGeom {
	namespace util {

		/* Returns whether wire conforms to a polyhedron, i.e. only edges with linear curves*/
		bool is_polyhedron(const TopoDS_Wire& wire);

		/* A temporary structure to store the intermediate data for the face conversion */
		class face_definition {
		private:
			Handle(Geom_Surface) surface_;
			std::vector<TopoDS_Wire> wires_;
			bool all_outer_;
		public:
			face_definition() : surface_(), all_outer_(false) {}

			typedef std::vector<TopoDS_Wire>::const_iterator wire_it;

			bool& all_outer() {
				return all_outer_;
			}

			bool all_outer() const {
				return all_outer_;
			}

			Handle(Geom_Surface)& surface() {
				return surface_;
			}

			const Handle(Geom_Surface)& surface() const {
				return surface_;
			}

			std::vector<TopoDS_Wire>& wires() {
				return wires_;
			}

			const TopoDS_Wire& outer_wire() const {
				return wires_.front();
			}

			std::pair<wire_it, wire_it> inner_wires() const {
				return { wires_.begin() + 1, wires_.end() };
			}
		};	

	}
}

#endif
