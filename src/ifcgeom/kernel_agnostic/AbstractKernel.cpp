#include "AbstractKernel.h"

#include "../../ifcgeom/schema_agnostic/IfcGeomElement.h"
#include "../../ifcgeom/kernels/opencascade/OpenCascadeKernel.h"

#undef Handle

#include "../../ifcgeom/kernels/cgal/CgalKernel.h"

namespace {
	/* A compile-time for loop over the taxonomy kinds */
	template <size_t N>
	struct dispatch_conversion {
		static bool dispatch(ifcopenshell::geometry::kernels::AbstractKernel* kernel, const ifcopenshell::geometry::taxonomy::item* item, ifcopenshell::geometry::ConversionResults& results) {
			if (N == item->kind()) {
				auto concrete_item = static_cast<const ifcopenshell::geometry::taxonomy::type_by_kind::type<N>*>(item);
				return kernel->convert_impl(concrete_item, results);
			} else {
				return dispatch_conversion<N + 1>::dispatch(kernel, item, results);
			}
		}
	};

	template <>
	struct dispatch_conversion<ifcopenshell::geometry::taxonomy::type_by_kind::max> {
		static bool dispatch(ifcopenshell::geometry::kernels::AbstractKernel*, const ifcopenshell::geometry::taxonomy::item* item, ifcopenshell::geometry::ConversionResults&) {
			Logger::Error("No conversion for " + std::to_string(item->kind()));
			return false;
		}
	};
}

bool ifcopenshell::geometry::kernels::AbstractKernel::convert(const taxonomy::item* item, ifcopenshell::geometry::ConversionResults& results) {
	try {
		return dispatch_conversion<0>::dispatch(this, item, results);
	} catch (std::exception& e) {
		Logger::Error(e, item->instance);
		return false;
	}
}

ifcopenshell::geometry::kernels::AbstractKernel* ifcopenshell::geometry::kernels::construct(const std::string& geometry_library, IfcParse::IfcFile* file) {
	const std::string geometry_library_lower = boost::to_lower_copy(geometry_library);
	if (geometry_library_lower == "opencascade") {
		return new OpenCascadeKernel;
	} else if (geometry_library_lower == "cgal") {
		return new CgalKernel;
	} else {
		throw IfcParse::IfcException("No geometry kernel registered for " + geometry_library);
	}
}

bool ifcopenshell::geometry::kernels::AbstractKernel::convert_impl(const taxonomy::collection* collection, ifcopenshell::geometry::ConversionResults& r) { 
	auto s = r.size();
	for (auto& c : collection->children) {
		convert(c, r);
	}
	return r.size() > s;
}

//void ifcopenshell::geometry::kernels::AbstractKernel::set_conversion_placement_rel_to(const IfcParse::declaration* type) {
//	placement_rel_to = type;
//}
//
//void ifcopenshell::geometry::kernels::AbstractKernel::setValue(GeomValue var, double value) {
//	switch (var) {
//	case GV_DEFLECTION_TOLERANCE:
//		deflection_tolerance = value;
//		break;
//	case GV_POINT_EQUALITY_TOLERANCE:
//		point_equality_tolerance = value;
//		break;
//	case GV_LENGTH_UNIT:
//		ifc_length_unit = value;
//		break;
//	case GV_PLANEANGLE_UNIT:
//		ifc_planeangle_unit = value;
//		break;
//	case GV_PRECISION:
//		modelling_precision = value;
//		break;
//	case GV_DIMENSIONALITY:
//		dimensionality = value;
//		break;
//	default:
//		assert(!"never reach here");
//	}
//}
//
//double ifcopenshell::geometry::kernels::AbstractKernel::getValue(GeomValue var) const {
//	switch (var) {
//	case GV_DEFLECTION_TOLERANCE:
//		return deflection_tolerance;
//	case GV_MINIMAL_FACE_AREA:
//		// Considering a right-angled triangle, this about the smallest
//		// area you can obtain without the vertices being confused.
//		return modelling_precision * modelling_precision / 2.;
//	case GV_POINT_EQUALITY_TOLERANCE:
//		return point_equality_tolerance;
//	case GV_LENGTH_UNIT:
//		return ifc_length_unit;
//		break;
//	case GV_PLANEANGLE_UNIT:
//		return ifc_planeangle_unit;
//		break;
//	case GV_PRECISION:
//		return modelling_precision;
//		break;
//	case GV_DIMENSIONALITY:
//		return dimensionality;
//		break;
//	}
//	assert(!"never reach here");
//	return 0;
//}
//
//
//
//
//template IFC_GEOM_API ifcopenshell::geometry::kernels::NativeElement<float, float>* ifcopenshell::geometry::kernels::AbstractKernel::create_brep_for_representation_and_product<float, float>(
//	const IteratorSettings& settings, IfcSchema::IfcRepresentation* representation, IfcSchema::IfcProduct* product);
//template IFC_GEOM_API ifcopenshell::geometry::kernels::NativeElement<float, double>* ifcopenshell::geometry::kernels::AbstractKernel::create_brep_for_representation_and_product<float, double>(
//	const IteratorSettings& settings, IfcSchema::IfcRepresentation* representation, IfcSchema::IfcProduct* product);
//template IFC_GEOM_API ifcopenshell::geometry::kernels::NativeElement<double, double>* ifcopenshell::geometry::kernels::AbstractKernel::create_brep_for_representation_and_product<double, double>(
//	const IteratorSettings& settings, IfcSchema::IfcRepresentation* representation, IfcSchema::IfcProduct* product);
//
//template IFC_GEOM_API ifcopenshell::geometry::kernels::NativeElement<float, float>* ifcopenshell::geometry::kernels::AbstractKernel::create_brep_for_processed_representation<float, float>(
//	const IteratorSettings& settings, IfcSchema::IfcRepresentation* representation, IfcSchema::IfcProduct* product, ifcopenshell::geometry::kernels::NativeElement<float, float>* brep);
//template IFC_GEOM_API ifcopenshell::geometry::kernels::NativeElement<float, double>* ifcopenshell::geometry::kernels::AbstractKernel::create_brep_for_processed_representation<float, double>(
//	const IteratorSettings& settings, IfcSchema::IfcRepresentation* representation, IfcSchema::IfcProduct* product, ifcopenshell::geometry::kernels::NativeElement<float, double>* brep);
//template IFC_GEOM_API ifcopenshell::geometry::kernels::NativeElement<double, double>* ifcopenshell::geometry::kernels::AbstractKernel::create_brep_for_processed_representation<double, double>(
//	const IteratorSettings& settings, IfcSchema::IfcRepresentation* representation, IfcSchema::IfcProduct* product, ifcopenshell::geometry::kernels::NativeElement<double, double>* brep);