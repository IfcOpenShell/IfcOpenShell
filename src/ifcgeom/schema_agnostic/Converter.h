#ifndef ITERATOR_KERNEL_H
#define ITERATOR_KERNEL_H

#include "../../ifcparse/IfcFile.h"
#include "../../ifcgeom/settings.h"
#include "../../ifcgeom/schema_agnostic/ConversionResult.h"
#include "../../ifcgeom/abstract_mapping.h"
#include "../../ifcgeom/ConversionSettings.h"
#include "../../ifcgeom/kernel_agnostic/AbstractKernel.h"

#include <boost/function.hpp>

namespace ifcopenshell { namespace geometry {

	class NativeElement;

	class Converter {
	public:
		typedef boost::shared_ptr<ifcopenshell::geometry::Representation::BRep> brep_ptr;
	private:
		std::string geometry_library_;
		abstract_mapping* mapping_;
		kernels::AbstractKernel* kernel_;
		ifcopenshell::geometry::settings settings_;
		std::map<ifcopenshell::geometry::taxonomy::item*, brep_ptr, ifcopenshell::geometry::taxonomy::less_functor> cache_;

	public:
		ConversionSettings settings;

		kernels::AbstractKernel* kernel() { return kernel_; }

		Converter(const std::string& geometry_library, IfcParse::IfcFile* file, ifcopenshell::geometry::settings& settings);
		
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

		ifcopenshell::geometry::ConversionResults convert(IfcUtil::IfcBaseClass* item) {
			std::clock_t map_start = std::clock();
			auto geom_item = mapping_->map(item);
			std::clock_t geom_start = std::clock();
			ifcopenshell::geometry::ConversionResults results;
			kernel_->convert(geom_item, results);
			std::clock_t geom_end = std::clock();
			total_map_time += (geom_start - map_start) / (double) CLOCKS_PER_SEC;
			total_geom_time += (geom_end - geom_start) / (double) CLOCKS_PER_SEC;
			return results;
		}

		ifcopenshell::geometry::NativeElement* create_brep_for_representation_and_product(IfcUtil::IfcBaseEntity* representation, IfcUtil::IfcBaseEntity* product);
		ifcopenshell::geometry::NativeElement* create_brep_for_processed_representation(IfcUtil::IfcBaseEntity* representation, IfcUtil::IfcBaseEntity* product, ifcopenshell::geometry::NativeElement* brep);

		ifcopenshell::geometry::NativeElement* create_brep_for_representation_and_product(taxonomy::item*, const taxonomy::matrix4&);
		ifcopenshell::geometry::NativeElement* create_brep_for_processed_representation(IfcUtil::IfcBaseEntity*, const taxonomy::matrix4&, ifcopenshell::geometry::NativeElement*);

		/*
		static int count(const ifcopenshell::geometry::ConversionResultShape*, int, bool unique=false);
		static int surface_genus(const ifcopenshell::geometry::ConversionResultShape*);

		static bool is_manifold(const ifcopenshell::geometry::ConversionResultShape*);
		static IfcUtil::IfcBaseEntity* get_decomposing_entity(IfcUtil::IfcBaseEntity*, bool include_openings=true);
		static IfcEntityList::ptr find_openings(IfcUtil::IfcBaseEntity* product);
		*/
	};
}}

#endif