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

#include "smlib_utils.h"

#include <SmApiBrep.h>
#include <SmApiGeneral.h>
#include <SmApiQueries.h>

#include <SmAxis2Placement.h>
#include <SmBrep.h>
#include <SmPointClass.h>

#include <atomic>
#include <cmath>

using namespace ifcopenshell::geom;

void ifcopenshell::geom::smlib_ensure_context() {
	// SmApiCreateContext() is not safe to call concurrently and creates the
	// context unconditionally, so remember whether it has been called.
	static std::atomic<bool> created{ false };
	bool expected = false;
	if (created.compare_exchange_strong(expected, true)) {
		SmApiCreateContext();
	}
}

SmTessellationParams ifcopenshell::geom::smlib_tessellation_params(const ifcopenshell::geom::settings& settings) {
	SmTessellationParams params;
	params.dChordHeightTol = settings.get<settings::MesherLinearDeflection>().get();
	params.dCurveAngleTolDeg = settings.get<settings::MesherAngularDeflection>().get() * 180. / SMLIB_PI;
	params.dSurfaceAngleTolDeg = params.dCurveAngleTolDeg;
	if (params.dChordHeightTol < 0.) {
		params.dChordHeightTol = 0.;
	}
	if (params.dCurveAngleTolDeg < 0.) {
		params.dCurveAngleTolDeg = 0.;
		params.dSurfaceAngleTolDeg = 0.;
	}
	return params;
}

void ifcopenshell::geom::smlib_placement_from_matrix(const Eigen::Matrix4d& matrix, SmAxis2Placement& placement) {
	// SmAxis2Placement stores the axes as rows, followed by the origin.
	double values[16] = {
		matrix(0, 0), matrix(1, 0), matrix(2, 0), 0.,
		matrix(0, 1), matrix(1, 1), matrix(2, 1), 0.,
		0., 0., 0., 0.,
		matrix(0, 3), matrix(1, 3), matrix(2, 3), 1.
	};
	placement.SetFrom4x4(values);
}

SmBrep* ifcopenshell::geom::smlib_brep_boolean(SmBrep* a, SmBrep* b, long operation) {
	if (!a || !b) {
		return nullptr;
	}
	SmBrep* a_copy = nullptr;
	SmBrep* b_copy = nullptr;
	if (SmApiBrepCopy(a, a_copy) != SM_SUCCESS || !a_copy) {
		return nullptr;
	}
	if (SmApiBrepCopy(b, b_copy) != SM_SUCCESS || !b_copy) {
		delete a_copy;
		return nullptr;
	}
	SmBrep* result = nullptr;
	const SmApiStatus status = SmApiBoolean(a_copy, b_copy, static_cast<SmBooleanOperationType>(operation), result);
	if (status != SM_SUCCESS) {
		// A failed boolean leaves the operands allocated, but their state is
		// unspecified; do not touch them beyond releasing them.
		return nullptr;
	}
	return result;
}
