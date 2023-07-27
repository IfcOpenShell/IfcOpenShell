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

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcCartesianTransformationOperator3D* inst) {

	Eigen::Vector4d origin;
	Eigen::Vector4d axis1(1., 0., 0., 0.);
	Eigen::Vector4d axis2(0., 1., 0., 0.);
	Eigen::Vector4d axis3(0., 0., 1., 0.);

	taxonomy::point3::ptr O = taxonomy::cast<taxonomy::point3>(map(inst->LocalOrigin()));
	origin << *O->components_, 1.0;

	if (inst->Axis1()) {
		taxonomy::direction3::ptr ax1 = taxonomy::cast<taxonomy::direction3>(map(inst->Axis1()));
		axis1 << *ax1->components_, 0.0;
	}
	if (inst->Axis2()) {
		taxonomy::direction3::ptr ax2 = taxonomy::cast<taxonomy::direction3>(map(inst->Axis2()));
		axis2 << *ax2->components_, 0.0;
	}
	if (inst->Axis3()) {
		taxonomy::direction3::ptr ax3 = taxonomy::cast<taxonomy::direction3>(map(inst->Axis3()));
		axis3 << *ax3->components_, 0.0;
	}

	auto m4 = taxonomy::make<taxonomy::matrix4>(origin.head<3>(), axis3.head<3>(), axis1.head<3>());
	if (m4->ccomponents().col(1).dot(axis2) < 0.) {
		m4->components().col(1) *= -1.;
	}

	double scale1, scale2, scale3;
	scale1 = scale2 = scale3 = 1.;

	if (inst->Scale()) {
		scale1 = *inst->Scale();
	}
	if (inst->as<IfcSchema::IfcCartesianTransformationOperator3DnonUniform>()) {
		auto nu = inst->as<IfcSchema::IfcCartesianTransformationOperator3DnonUniform>();
		scale2 = nu->Scale2() ? *nu->Scale2() : scale1;
		scale3 = nu->Scale3() ? *nu->Scale3() : scale1;
	}

	if (scale1 != 1.) {
		m4->components().col(0) *= scale1;
	}
	if (scale2 != 1.) {
		m4->components().col(1) *= scale2;
	}
	if (scale3 != 1.) {
		m4->components().col(2) *= scale3;
	}

	return m4;

	/*
	auto m = new taxonomy::matrix4;

	// @todo is this necessary?
	m->components() = m->components().inverse();
	m->components().transposeInPlace();

	// @todo tag identity?

	return m;
	*/
}
