#ifndef ITERATOR_KERNEL_H
#define ITERATOR_KERNEL_H

#include "../ifcparse/IfcFile.h"
#include "../ifcgeom/ConversionSettings.h"
#include "../ifcgeom/ConversionResult.h"
#include "../ifcgeom/abstract_mapping.h"
#include "../ifcgeom/ConversionSettings.h"
#include "../ifcgeom/AbstractKernel.h"
#include "../ifcgeom/IfcGeomElement.h"

#include <boost/function.hpp>

namespace ifcopenshell { namespace geometry {

	class Converter {
	public:
		typedef boost::shared_ptr<IfcGeom::Representation::BRep> brep_ptr;
	private:
		std::string geometry_library_;
		abstract_mapping* mapping_;
		kernels::AbstractKernel* kernel_;
		IfcGeom::IteratorSettings settings_;
		std::map<ifcopenshell::geometry::taxonomy::ptr, brep_ptr, ifcopenshell::geometry::taxonomy::less_functor> cache_;

	public:
		kernels::AbstractKernel* kernel() { return kernel_; }

		Converter(const std::string& geometry_library, IfcParse::IfcFile* file, IfcGeom::IteratorSettings& settings);
		
		~Converter() {}

		abstract_mapping* mapping() const { return mapping_; }

		/*
		virtual NativeElement<double, double>* convert(
			const IteratorSettings& settings, IfcUtil::IfcBaseClass* representation,
			IfcUtil::IfcBaseClass* product)
		{
			return implementation_->convert(settings, representation, product);
		}
		*/

		double total_map_time = 0.;
		double total_geom_time = 0.;

		IfcGeom::ConversionResults convert(IfcUtil::IfcBaseClass* item);

		IfcGeom::BRepElement* create_brep_for_representation_and_product(const IfcUtil::IfcBaseEntity* representation, const IfcUtil::IfcBaseEntity* product);
		// IfcGeom::BRepElement* create_brep_for_processed_representation(const IfcUtil::IfcBaseEntity* representation, const IfcUtil::IfcBaseEntity* product, IfcGeom::BRepElement* brep);

		IfcGeom::BRepElement* create_brep_for_representation_and_product(taxonomy::ptr, const IfcUtil::IfcBaseEntity* product, const taxonomy::matrix4::ptr& place);
		IfcGeom::BRepElement* create_brep_for_processed_representation(const IfcUtil::IfcBaseEntity* product, const taxonomy::matrix4::ptr& place, IfcGeom::BRepElement*);
	};
}}

#endif