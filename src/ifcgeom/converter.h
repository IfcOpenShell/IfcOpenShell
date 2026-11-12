#ifndef ITERATOR_KERNEL_H
#define ITERATOR_KERNEL_H

#include "../ifcparse/file.h"
#include "../ifcgeom/conversion_settings.h"
#include "../ifcgeom/conversion_result.h"
#include "../ifcgeom/abstract_mapping.h"
#include "../ifcgeom/conversion_settings.h"
#include "../ifcgeom/abstract_kernel.h"
#include "../ifcgeom/element.h"

#include <memory>

namespace ifcopenshell { namespace geom {

	class IFC_GEOM_API converter {
	public:
		typedef std::shared_ptr<ifcopenshell::geom::native> brep_ptr;
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

		std::vector<ifcopenshell::geom::conversion_result> convert(express::base item);

		ifcopenshell::geom::native_element* create_brep_for_representation_and_product(const express::base representation, const express::base product);
		// ifcopenshell::geom::native_element* create_brep_for_processed_representation(const express::base representation, const express::base product, ifcopenshell::geom::native_element* brep);

		ifcopenshell::geom::native_element* create_brep_for_representation_and_product(ifcopenshell::geom::taxonomy::ptr, const express::base product, const ifcopenshell::geom::taxonomy::matrix4::ptr& place);
		ifcopenshell::geom::native_element* create_brep_for_processed_representation(const express::base product, const ifcopenshell::geom::taxonomy::matrix4::ptr& place, ifcopenshell::geom::native_element*);

		const ifcopenshell::geom::settings& settings() { return settings_; }
	};
}}

#endif
