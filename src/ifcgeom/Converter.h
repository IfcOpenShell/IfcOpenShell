#ifndef ITERATOR_KERNEL_H
#define ITERATOR_KERNEL_H

#include "../ifcparse/file.h"
#include "../ifcgeom/ConversionSettings.h"
#include "../ifcgeom/ConversionResult.h"
#include "../ifcgeom/abstract_mapping.h"
#include "../ifcgeom/ConversionSettings.h"
#include "../ifcgeom/AbstractKernel.h"
#include "../ifcgeom/IfcGeomElement.h"

#include <boost/function.hpp>

namespace ifcopenshell { namespace geom {

	class IFC_GEOM_API converter {
	public:
		typedef boost::shared_ptr<ifcopenshell::geom::Representation::brep> brep_ptr;
	private:
		ifcopenshell::geom::abstract_mapping* mapping_;
		std::unique_ptr<ifcopenshell::geom::kernels::abstract_kernel> kernel_;
		ifcopenshell::geom::settings settings_;
		std::map<ifcopenshell::geom::taxonomy::ptr, brep_ptr, ifcopenshell::geom::taxonomy::less_functor> cache_;
		ifcopenshell::logger& logger_;

	public:
		ifcopenshell::geom::kernels::abstract_kernel* kernel() { return &*kernel_; }

		converter(std::unique_ptr<ifcopenshell::geom::kernels::abstract_kernel>&& geometry_library, ifcopenshell::file* file, ifcopenshell::geom::settings& settings, ifcopenshell::logger& logger = ifcopenshell::logger::root());
		
		~converter();

		ifcopenshell::geom::abstract_mapping* mapping() const { return mapping_; }
		ifcopenshell::logger& logger() const { return logger_; }

		/*
		virtual NativeElement<double, double>* convert(
			const IteratorSettings& settings, express::base representation,
			express::base product)
		{
			return implementation_->convert(settings, representation, product);
		}
		*/

		double total_map_time = 0.;
		double total_geom_time = 0.;

		ifcopenshell::geom::conversion_results convert(express::base item);

		ifcopenshell::geom::brep_element* create_brep_for_representation_and_product(const express::base representation, const express::base product);
		// ifcopenshell::geom::brep_element* create_brep_for_processed_representation(const express::base representation, const express::base product, ifcopenshell::geom::brep_element* brep);

		ifcopenshell::geom::brep_element* create_brep_for_representation_and_product(ifcopenshell::geom::taxonomy::ptr, const express::base product, const ifcopenshell::geom::taxonomy::matrix4::ptr& place);
		ifcopenshell::geom::brep_element* create_brep_for_processed_representation(const express::base product, const ifcopenshell::geom::taxonomy::matrix4::ptr& place, ifcopenshell::geom::brep_element*);

		const ifcopenshell::geom::settings& settings() { return settings_; }
	};
}}

#endif
