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

#ifndef SWEEP_UTILS_H
#define SWEEP_UTILS_H

#include <TopoDS_Wire.hxx>
#include <TopoDS_Edge.hxx>

#include <vector>

namespace IfcGeom {
	namespace util {

		bool wire_is_c1_continuous(const TopoDS_Wire& w, double tol);

		bool wire_to_ax(const TopoDS_Wire& wire, gp_Ax2& directrix);

		bool is_single_linear_edge(const TopoDS_Wire& wire);

		bool is_single_circular_edge(const TopoDS_Wire& wire);

		void process_sweep_as_extrusion(const TopoDS_Wire& wire, const TopoDS_Wire& section, TopoDS_Shape& result);

		void process_sweep_as_revolution(const TopoDS_Wire& wire, const TopoDS_Wire& section, TopoDS_Shape& result);

		void process_sweep_as_pipe(const TopoDS_Wire& wire, const TopoDS_Wire& section, TopoDS_Shape& result, bool force_transformed = false);

		void sort_edges(const TopoDS_Wire& wire, std::vector<TopoDS_Edge>& sorted_edges);


		// #939: a closed loop causes failed triangulation in 7.3 and artefacts
		// in 7.4 so we break up a closed wire into two equal parts.
		void break_closed(const TopoDS_Wire& wire, std::vector<TopoDS_Wire>& wires);

		void segment_adjacent_non_linear(const TopoDS_Wire& wire, std::vector<TopoDS_Wire>& wires);

		// @todo make this generic for other sweeps not just swept disk
		void process_sweep(const TopoDS_Wire& wire, double radius, TopoDS_Shape& result);
	}
}

#endif
