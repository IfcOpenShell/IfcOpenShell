#ifndef ITERATOR_KERNEL_H
#define ITERATOR_KERNEL_H

#include "../ifcparse/IfcFile.h"
#include "../ifcgeom/IfcGeomIteratorSettings.h"
#include "../ifcgeom/IfcRepresentationShapeItem.h"

#include "../ifcparse/Ifc2x3.h"
#include "../ifcparse/Ifc4.h"

#include <boost/function.hpp>

#include <TopExp_Explorer.hxx>

namespace {
	// LayerAssignments renamed from plural to singular, LayerAssignment, so work around that
	IfcEntityList::ptr getLayerAssignments(Ifc2x3::IfcRepresentationItem* item) {
		return item->LayerAssignments()->generalize();
	}
	IfcEntityList::ptr getLayerAssignments(Ifc4::IfcRepresentationItem* item) {
		return item->LayerAssignment()->generalize();
	}
}

namespace IfcGeom {

	template <typename T>
	class BRepElement;

	class Kernel {
	private:
		Kernel* implementation_;

	public:
		// Tolerances and settings for various geometrical operations:
		enum GeomValue {
			// Specifies the deflection of the mesher
			// Default: 0.001m / 1mm
			GV_DEFLECTION_TOLERANCE,
			// Specifies the tolerance of the wire builder, most notably for trimmed curves
			// Defailt: 0.0001m / 0.1mm
			GV_WIRE_CREATION_TOLERANCE,
			// Specifies the minimal area of a face to be included in an IfcConnectedFaceset
			// Read-only
			GV_MINIMAL_FACE_AREA,
			// Specifies the treshold distance under which cartesian points are deemed equal
			// Default: 0.00001m / 0.01mm
			GV_POINT_EQUALITY_TOLERANCE,
			// Specifies maximum number of faces for a shell to be sewed. Sewing shells
			// that consist of many faces is really detrimental for the performance.
			// Default: 1000
			GV_MAX_FACES_TO_SEW,
			// The length unit used the creation of TopoDS_Shapes, primarily affects the
			// interpretation of IfcCartesianPoints and IfcVector magnitudes
			// DefaultL 1.0
			GV_LENGTH_UNIT,
			// The plane angle unit used for the creation of TopoDS_Shapes, primarily affects
			// the interpretation of IfcParamaterValues of IfcTrimmedCurves
			// Default: -1.0 (= not set, fist try degrees, then radians)
			GV_PLANEANGLE_UNIT,
			// The precision used in boolean operations, setting this value too low results
			// in artefacts and potentially modelling failures
			// Default: 0.00001 (obtained from IfcGeometricRepresentationContext if available)
			GV_PRECISION,
			// Whether to process shapes of type Face or higher (1) Wire or lower (-1) or all (0)
			GV_DIMENSIONALITY
		};

		Kernel(IfcParse::IfcFile* file_ = 0);
		
		virtual ~Kernel() {}

		virtual void setValue(GeomValue var, double value) {
			implementation_->setValue(var, value);
		}

		virtual double getValue(GeomValue var) const {
			return implementation_->getValue(var);
		}

		virtual BRepElement<double>* convert(
			const IteratorSettings& settings, IfcUtil::IfcBaseClass* representation,
			IfcUtil::IfcBaseClass* product)
		{
			return implementation_->convert(settings, representation, product);
		}

		virtual IfcRepresentationShapeItems convert(IfcUtil::IfcBaseClass* item) {
			return implementation_->convert(item);
		}

		virtual bool convert(IfcUtil::IfcBaseClass* item, gp_Trsf& trsf) {
			return implementation_->convert(item, trsf);
		}

		static int count(const TopoDS_Shape&, TopAbs_ShapeEnum);

		template <typename Schema>
		static std::map<std::string, typename Schema::IfcPresentationLayerAssignment*> get_layers(typename Schema::IfcProduct* prod) {
			std::map<std::string, typename Schema::IfcPresentationLayerAssignment*> layers;
			if (prod->hasRepresentation()) {
				IfcEntityList::ptr r = IfcParse::traverse(prod->Representation());
				typename Schema::IfcRepresentation::list::ptr representations = r->as<typename Schema::IfcRepresentation>();
				for (typename Schema::IfcRepresentation::list::it it = representations->begin(); it != representations->end(); ++it) {
					typename Schema::IfcPresentationLayerAssignment::list::ptr a = (*it)->LayerAssignments();
					for (typename Schema::IfcPresentationLayerAssignment::list::it jt = a->begin(); jt != a->end(); ++jt) {
						layers[(*jt)->Name()] = *jt;
					}
				}

				typename Schema::IfcRepresentationItem::list::ptr items = r->as<typename Schema::IfcRepresentationItem>();
				for (typename Schema::IfcRepresentationItem::list::it it = items->begin(); it != items->end(); ++it) {
					typename Schema::IfcPresentationLayerAssignment::list::ptr a = getLayerAssignments(*it)->template as<typename Schema::IfcPresentationLayerAssignment>();
					for (typename Schema::IfcPresentationLayerAssignment::list::it jt = a->begin(); jt != a->end(); ++jt) {
						layers[(*jt)->Name()] = *jt;
					}
				}
			}
			return layers;
		}

	};

	namespace impl {
		typedef boost::function1<Kernel*, IfcParse::IfcFile*> kernel_fn;

		class KernelFactoryImplementation : public std::map<std::string, kernel_fn> {
		public:
			KernelFactoryImplementation();
			void bind(const std::string& schema_name, kernel_fn);
			Kernel* construct(const std::string& schema_name, IfcParse::IfcFile*);
		};

		KernelFactoryImplementation& kernel_implementations();
	}
}

#endif