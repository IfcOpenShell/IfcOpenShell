#ifndef ABSTRACT_KERNEL_H
#define ABSTRACT_KERNEL_H

#include "../../ifcparse/macros.h"
#include "../../ifcgeom/schema_agnostic/ifc_geom_api.h"
#include "../../ifcgeom/schema_agnostic/Kernel.h"
#include "../../ifcgeom/schema_agnostic/IfcGeomRepresentation.h"

#define INCLUDE_SCHEMA(x) STRINGIFY(../../ifcparse/x.h)
#include INCLUDE_SCHEMA(IfcSchema)
#undef INCLUDE_SCHEMA

namespace IfcGeom {

	class IFC_GEOM_API MAKE_TYPE_NAME(AbstractKernel) : public IfcGeom::Kernel {
	protected:
		// For stopping PlacementRelTo recursion in convert(const IfcSchema::IfcObjectPlacement* l, gp_Trsf& trsf)
		const IfcParse::declaration* placement_rel_to;

		double deflection_tolerance;
		double wire_creation_tolerance;
		double point_equality_tolerance;
		double max_faces_to_sew;
		double ifc_length_unit;
		double ifc_planeangle_unit;
		double modelling_precision;
		double dimensionality;

		std::map<int, SurfaceStyle> style_cache;

	public:
		MAKE_TYPE_NAME(AbstractKernel)(const std::string& geometry_library)
			: IfcGeom::Kernel(geometry_library, nullptr)
			, deflection_tolerance(0.001)
			, wire_creation_tolerance(0.0001)
			, point_equality_tolerance(0.00001)
			, max_faces_to_sew(-1.0)
			, ifc_length_unit(1.0)
			, ifc_planeangle_unit(-1.0)
			, modelling_precision(0.00001)
			, dimensionality(1.)
			, placement_rel_to(0) 
		{}

		void set_conversion_placement_rel_to(const IfcParse::declaration* type);
		virtual void setValue(GeomValue var, double value);
		virtual double getValue(GeomValue var) const;

		const IfcSchema::IfcMaterial* get_single_material_association(const IfcSchema::IfcProduct*);
		IfcSchema::IfcRepresentation* representation_mapped_to(const IfcSchema::IfcRepresentation* representation);
		IfcSchema::IfcProduct::list::ptr products_represented_by(const IfcSchema::IfcRepresentation*);
		const SurfaceStyle* get_style(const IfcSchema::IfcRepresentationItem*);
		const SurfaceStyle* get_style(const IfcSchema::IfcMaterial*);

		virtual bool is_identity_transform(const IfcUtil::IfcBaseClass*) = 0;
		virtual bool convert_shapes(const IfcUtil::IfcBaseClass*, IfcGeom::ConversionResults&) = 0;
		virtual bool apply_layerset(const IfcSchema::IfcProduct* product, IfcGeom::ConversionResults& shapes) = 0;
		virtual bool validate_quantities(const IfcSchema::IfcProduct* product, const IfcGeom::Representation::BRep& brep) = 0;
		virtual bool convert_openings(const IfcSchema::IfcProduct* product, const IfcSchema::IfcRelVoidsElement::list::ptr& openings, const IfcGeom::ConversionResults& shapes, const ConversionResultPlacement* trsf, IfcGeom::ConversionResults& opened_shapes) = 0;

		const SurfaceStyle* internalize_surface_style(const std::pair<IfcUtil::IfcBaseClass*, IfcUtil::IfcBaseClass*>& shading_style);

		template <typename P, typename PP>
		IfcGeom::NativeElement<P, PP>* create_brep_for_representation_and_product(
			const IteratorSettings&, IfcSchema::IfcRepresentation*, IfcSchema::IfcProduct*);

		template <typename P, typename PP>
		IfcGeom::NativeElement<P, PP>* create_brep_for_processed_representation(
			const IteratorSettings&, IfcSchema::IfcRepresentation*, IfcSchema::IfcProduct*, IfcGeom::NativeElement<P, PP>*);
	};

}

#endif