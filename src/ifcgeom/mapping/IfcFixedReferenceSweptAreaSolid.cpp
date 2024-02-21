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

#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

#ifdef SCHEMA_HAS_IfcFixedReferenceSweptAreaSolid

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcFixedReferenceSweptAreaSolid* inst) {
	auto dir = map(inst->Directrix());
	auto ref = taxonomy::cast<taxonomy::direction3>(map(inst->FixedReference()));
	auto profile = taxonomy::cast<taxonomy::face>(map(inst->SweptArea()));

	auto loft = taxonomy::make<taxonomy::loft>();
	// @todo intialize as default
	loft->axis = nullptr;

	// @todo currently only the case is handled where directrix returns a piecewise_function
	if (auto pwf = taxonomy::dcast<taxonomy::piecewise_function>(dir)) {
		double start = 0;
		double end = pwf->length();
#ifdef SCHEMA_HAS_IfcDirectrixCurveSweptAreaSolid
		// IfcDirectrixCurveSweptAreaSolid introduced in 4.3 changed attribute type
		// from optional IfcParamValue to optional IfcCurveMeasureSelect.
		// Invocation of mapping on pre-4.3 models can never result in a piecewise_function.
		if (inst->StartParam()) { // && inst->StartParam()->as<IfcSchema::IfcLengthMeasure>()) {
			double s = *inst->StartParam()->as<IfcSchema::IfcLengthMeasure>();
			if (s > start) {
				start = s;
			}
		}
		if (inst->EndParam()) { // && inst->EndParam()->as<IfcSchema::IfcLengthMeasure>()) {
			double e = *inst->EndParam()->as<IfcSchema::IfcLengthMeasure>();
			if (e < end) {
				end = e;
			}
		}
#endif
		auto len = end - start;
		auto nsteps = (size_t)ceil(len);
		for (size_t i = 0; i <= nsteps; ++i) {
			auto m4 = pwf->evaluate(start + len / nsteps * i);
			std::stringstream ss;
			ss << m4;
			auto s = ss.str();
			std::wcout << s.c_str() << std::endl;

			Eigen::Vector3d tangent = m4.col(0).head<3>().normalized();
			Eigen::Vector3d proj = (ref->components() - tangent * tangent.dot(ref->components()));
			proj.normalize();
			auto ref = proj.cross(tangent);
			auto pos = m4.col(3).head<3>();

			Eigen::Matrix4d m4b = Eigen::Matrix4d::Identity();
			m4b.col(0).head<3>() = ref;
			m4b.col(1).head<3>() = proj;
			m4b.col(2).head<3>() = tangent;
			m4b.col(3).head<3>() = pos;

			// @todo taxonomy::clone() does not actually clone. That's really confusing.
			// loft->children.push_back(taxonomy::clone(profile));
			loft->children.push_back(taxonomy::face::ptr(profile->clone_()));
			loft->children.back()->matrix = taxonomy::make<taxonomy::matrix4>(m4b);
		}
	}

	return loft;
}

#endif
