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

namespace {
	struct MAKE_TYPE_NAME(factory_t) {
		IfcGeom::Kernel* operator()(IfcParse::IfcFile* file) const {
			IfcGeom::MAKE_TYPE_NAME(CgalKernel)* k = new IfcGeom::MAKE_TYPE_NAME(CgalKernel);
			return k;
		}
	};
}

void MAKE_INIT_FN(KernelImplementation_cgal_)(IfcGeom::impl::KernelFactoryImplementation* mapping) {
	static const std::string schema_name = STRINGIFY(IfcSchema);
	MAKE_TYPE_NAME(factory_t) factory;
	mapping->bind(schema_name, "cgal", factory);
}

#define CgalKernel MAKE_TYPE_NAME(CgalKernel)

bool IfcGeom::CgalKernel::is_identity_transform(const IfcUtil::IfcBaseClass* l) {
	Logger::Message(Logger::LOG_ERROR, "Not implemented is_identity_transform()");
	return false;
	/*
	// OpenCascade kernel code below

	IfcSchema::IfcAxis2Placement2D* ax2d;
	IfcSchema::IfcAxis2Placement3D* ax3d;

	IfcSchema::IfcCartesianTransformationOperator2D* op2d;
	IfcSchema::IfcCartesianTransformationOperator3D* op3d;
	IfcSchema::IfcCartesianTransformationOperator2DnonUniform* op2dnonu;
	IfcSchema::IfcCartesianTransformationOperator3DnonUniform* op3dnonu;

	if ((op2dnonu = l->as<IfcSchema::IfcCartesianTransformationOperator2DnonUniform>()) != 0) {
		gp_GTrsf2d gtrsf2d;
		convert(op2dnonu, gtrsf2d);
		return gtrsf2d.Form() == gp_Identity;
	} else if ((op2d = l->as<IfcSchema::IfcCartesianTransformationOperator2D>()) != 0) {
		gp_Trsf2d trsf2d;
		convert(op2d, trsf2d);
		return trsf2d.Form() == gp_Identity;
	} else if ((op3dnonu = l->as<IfcSchema::IfcCartesianTransformationOperator3DnonUniform>()) != 0) {
		gp_GTrsf gtrsf;
		convert(op3dnonu, gtrsf);
		return gtrsf.Form() == gp_Identity;
	} else if ((op3d = l->as<IfcSchema::IfcCartesianTransformationOperator3D>()) != 0) {
		gp_Trsf trsf;
		convert(op3d, trsf);
		return trsf.Form() == gp_Identity;
	} else if ((ax2d = l->as<IfcSchema::IfcAxis2Placement2D>()) != 0) {
		gp_Trsf2d trsf2d;
		convert(ax2d, trsf2d);
		return trsf2d.Form() == gp_Identity;
	} else if ((ax3d = l->as<IfcSchema::IfcAxis2Placement3D>()) != 0) {
		gp_Trsf trsf;
		convert(ax3d, trsf);
		return trsf.Form() == gp_Identity;
	} else {
		throw IfcParse::IfcException("Invalid valuation for IfcAxis2Placement / IfcCartesianTransformationOperator");
	}
	*/
}

bool IfcGeom::CgalKernel::apply_layerset(const IfcSchema::IfcProduct* product, IfcGeom::ConversionResults& shapes) {
	throw std::runtime_error("not implemented");
}

bool IfcGeom::CgalKernel::validate_quantities(const IfcSchema::IfcProduct* product, const IfcGeom::Representation::BRep& brep) {
	throw std::runtime_error("not implemented");
}

bool IfcGeom::CgalKernel::convert_openings(const IfcSchema::IfcProduct* product, const IfcSchema::IfcRelVoidsElement::list::ptr& openings, const IfcGeom::ConversionResults& shapes, const IfcGeom::ConversionResultPlacement* trsf, IfcGeom::ConversionResults& opened_shapes) {
	throw std::runtime_error("not implemented");
}

