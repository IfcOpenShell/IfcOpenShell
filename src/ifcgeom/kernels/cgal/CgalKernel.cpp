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

#include "../../../ifcgeom/IfcGeomShapeType.h"
#include "../../../ifcgeom/IfcGeom.h"

#include "CgalKernel.h"
#include "CgalConversionResult.h"

namespace {
	struct MAKE_TYPE_NAME(factory_t) {
		IfcGeom::Kernel* operator()(IfcParse::IfcFile* file) const {
			IfcGeom::MAKE_TYPE_NAME(Kernel)* k = new IfcGeom::MAKE_TYPE_NAME(Kernel);
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

bool IfcGeom::CgalKernel::is_identity_transform(IfcUtil::IfcBaseClass* l) {
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

IfcGeom::NativeElement<double>* IfcGeom::CgalKernel::create_brep_for_representation_and_product(
	const IteratorSettings& settings, IfcSchema::IfcRepresentation* representation, IfcSchema::IfcProduct* product)
{
	IfcGeom::Representation::BRep* shape;
	IfcGeom::ConversionResults shapes, shapes2;

	if (!convert_shapes(representation, shapes)) {
		return 0;
	}

	if (settings.get(IteratorSettings::APPLY_LAYERSETS)) {
		Logger::Message(Logger::LOG_ERROR, "Not implemented APPLY_LAYERSETS");
	}

	int parent_id = -1;
	try {
		IfcUtil::IfcBaseEntity* parent_object = get_decomposing_entity(product);
		if (parent_object && parent_object->as<IfcSchema::IfcObjectDefinition>()) {
			parent_id = parent_object->data().id();
		}
	} catch (const std::exception& e) {
		Logger::Error(e);
	}

	const std::string name = product->hasName() ? product->Name() : "";
	const std::string guid = product->GlobalId();

	cgal_placement_t trsf;
	try {
		// convert(product->ObjectPlacement(), trsf);
	} catch (...) {}

	std::stringstream representation_id_builder;
	representation_id_builder << representation->data().id();

	// Does the IfcElement have any IfcOpenings?
	// Note that openings for IfcOpeningElements are not processed
	IfcSchema::IfcRelVoidsElement::list::ptr openings = find_openings(product)->as<IfcSchema::IfcRelVoidsElement>();

	const std::string product_type = product->declaration().name();
	ElementSettings element_settings(settings, getValue(GV_LENGTH_UNIT), product_type);

	if (!settings.get(IfcGeom::IteratorSettings::DISABLE_OPENING_SUBTRACTIONS) && openings && openings->size()) {
		Logger::Message(Logger::LOG_ERROR, "Not implemented opening subtractions");
	}
	
	shape = new IfcGeom::Representation::BRep(element_settings, representation_id_builder.str(), shapes);
	
	std::string context_string = "";
	if (representation->hasRepresentationIdentifier()) {
		context_string = representation->RepresentationIdentifier();
	} else if (representation->ContextOfItems()->hasContextType()) {
		context_string = representation->ContextOfItems()->ContextType();
	}

	return new NativeElement<double>(
		product->data().id(),
		parent_id,
		name,
		product_type,
		guid,
		context_string,
		new CgalPlacement(trsf),
		boost::shared_ptr<IfcGeom::Representation::BRep>(shape),
		product
	);
}

IfcGeom::NativeElement<double>* IfcGeom::CgalKernel::create_brep_for_processed_representation(
	const IteratorSettings& /*settings*/, IfcSchema::IfcRepresentation* representation, IfcSchema::IfcProduct* product,
	IfcGeom::NativeElement<double>* brep)
{
	int parent_id = -1;
	try {
		IfcUtil::IfcBaseEntity* parent_object = get_decomposing_entity(product);
		if (parent_object && parent_object->as<IfcSchema::IfcObjectDefinition>()) {
			parent_id = parent_object->data().id();
		}
	} catch (const std::exception& e) {
		Logger::Error(e);
	}

	const std::string name = product->hasName() ? product->Name() : "";
	const std::string guid = product->GlobalId();

	cgal_placement_t trsf;
	try {
		// convert(product->ObjectPlacement(), trsf);
	} catch (...) {}

	std::string context_string = "";
	if (representation->hasRepresentationIdentifier()) {
		context_string = representation->RepresentationIdentifier();
	} else if (representation->ContextOfItems()->hasContextType()) {
		context_string = representation->ContextOfItems()->ContextType();
	}

	const std::string product_type = product->declaration().name();

	return new NativeElement<double>(
		product->data().id(),
		parent_id,
		name,
		product_type,
		guid,
		context_string,
		new CgalPlacement(trsf),
		brep->geometry_pointer(),
		product
	);
}
