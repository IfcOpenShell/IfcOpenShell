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

#ifndef OPENCASCADEKERNEL_H
#define OPENCASCADEKERNEL_H

#include <cmath>

static const double ALMOST_ZERO = 1.e-9;

template <typename T>
inline static bool ALMOST_THE_SAME(const T& a, const T& b, double tolerance=ALMOST_ZERO) {
	return fabs(a-b) < tolerance; 
}

#include <gp_Pnt.hxx>
#include <gp_Vec.hxx>
#include <gp_Mat.hxx>
#include <gp_Mat2d.hxx>
#include <gp_GTrsf.hxx>
#include <gp_GTrsf2d.hxx>
#include <gp_Trsf.hxx>
#include <gp_Trsf2d.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Wire.hxx>
#include <TopoDS_Face.hxx>
#include <Geom_Curve.hxx>
#include <gp_Pln.hxx>
#include <TColgp_SequenceOfPnt.hxx>
#include <TopTools_ListOfShape.hxx>
#include <BOPAlgo_Operation.hxx>
#include <BRep_Builder.hxx>
#include <BRepBuilderAPI_MakeEdge.hxx>

#include "../../../ifcgeom/kernel_agnostic/AbstractKernel.h" 

#include "../../../ifcgeom/schema_agnostic/IfcGeomElement.h" 
#include "../../../ifcgeom/schema_agnostic/IfcGeomRepresentation.h" 
#include "../../../ifcgeom/schema_agnostic/ConversionResult.h"
#include "../../../ifcgeom/kernels/opencascade/IfcGeomShapeType.h"

#include "../../../ifcgeom/kernels/opencascade/OpenCascadeConversionResult.h"

#include "../../../ifcgeom/schema_agnostic/ifc_geom_api.h"

#include "../../../ifcgeom/taxonomy.h"

// Define this in case you want to conserve memory usage at all cost. This has been
// benchmarked extensively: https://github.com/IfcOpenShell/IfcOpenShell/pull/47
// #define NO_CACHE

#ifdef NO_CACHE

#define IN_CACHE(T,E,t,e)
#define CACHE(T,E,e)

#else

#define IN_CACHE(T,E,t,e) std::map<int,t>::const_iterator it = cache.T.find(E->data().id());\
if ( it != cache.T.end() ) { e = it->second; return true; }
#define CACHE(T,E,e) cache.T[E->data().id()] = e;

#endif

namespace ifcopenshell {
namespace geometry {
namespace kernels {

	class IFC_GEOM_API geometry_exception : public std::exception {
	protected:
		std::string message;
	public:
		geometry_exception(const std::string& m)
			: message(m) {}
		virtual ~geometry_exception() throw () {}
		virtual const char* what() const throw() {
			return message.c_str();
		}
	};

	class IFC_GEOM_API too_many_faces_exception : public geometry_exception {
	public:
		too_many_faces_exception()
			: geometry_exception("Too many faces for operation") {}
	};

	/*
	class IFC_GEOM_API POSTFIX_SCHEMA(Cache) {
	public:
#include "IfcRegisterCreateCache.h"
		std::map<int, TopoDS_Shape> Shape;
	};
	*/

	
	class IFC_GEOM_API OpenCascadeKernel : public AbstractKernel {
	private:
		/*
		// faceset_helper traverses the forward instance references of IfcConnectedFaceSet and then provides a mapping
		// M of (IfcCartesianPoint, IfcCartesianPoint) -> TopoDS_Edge, where M(a, b) is a partner of M(b, a), ie share
		// the same underlying edge but with orientation reversed. This then later speeds op the process of creating a
		// manifold Shell / Solid from this set of faces. Only IfcPolyLoop instances are used. Points within the tolerance
		// threshiold are merged, so consider points a, b, c, distance(a, b) < eps then M(a, b) = Null, M(a, b) = M(a, c).
		class faceset_helper {
		private:
			OpenCascadeKernel* kernel_;
			std::set<const IfcSchema::IfcPolyLoop*> duplicates_;
			std::map<int, int> vertex_mapping_;
			std::map<std::pair<int, int>, TopoDS_Edge> edges_;
			double eps_;
			bool non_manifold_;

			template <typename Fn>
			void loop_(IfcSchema::IfcCartesianPoint::list::ptr& ps, const Fn& callback) {
				if (ps->size() < 3) {
					return;
				}

				auto a = *(ps->end() - 1);
				auto A = a->data().id();
				for (auto& b : *ps) {
					auto B = b->data().id();
					auto C = vertex_mapping_[A], D = vertex_mapping_[B];
					bool fwd = C < D;
					if (!fwd) {
						std::swap(C, D);
					}
					if (C != D) {
						callback(C, D, fwd);
						A = B;
					}
				}
			}
		public:
			faceset_helper(OpenCascadeKernel* kernel, const IfcSchema::IfcConnectedFaceSet* l);

			~faceset_helper();

			bool non_manifold() const { return non_manifold_; }
			bool& non_manifold() { return non_manifold_; }

			bool edge(const IfcSchema::IfcCartesianPoint* a, const IfcSchema::IfcCartesianPoint* b, TopoDS_Edge& e) {
				int A = vertex_mapping_[a->data().id()];
				int B = vertex_mapping_[b->data().id()];
				if (A == B) {
					return false;
				}

				return edge(A, B, e);
			}

			bool edge(int A, int B, TopoDS_Edge& e) {
				auto it = edges_.find({ A, B });
				if (it == edges_.end()) {
					return false;
				}
				e = it->second;
				return true;
			}

			bool wire(const IfcSchema::IfcPolyLoop* loop, TopoDS_Wire& wire) {
				if (duplicates_.find(loop) != duplicates_.end()) {
					return false;
				}
				BRep_Builder builder;
				builder.MakeWire(wire);
				int count = 0;
				auto ps = loop->Polygon();
				loop_(ps, [this, &builder, &wire, &count](int A, int B, bool fwd) {
					TopoDS_Edge e;
					if (edge(A, B, e)) {
						if (!fwd) {
							e.Reverse();
						}
						builder.Add(wire, e);
						count += 1;
					}
				});
				if (count >= 3) {
					wire.Closed(true);

					TopTools_ListOfShape results;
					if (kernel_->wire_intersections(wire, results)) {
						Logger::Warning("Self-intersections with " + boost::lexical_cast<std::string>(results.Extent()) + " cycles detected", loop);
						kernel_->select_largest(results, wire);
						non_manifold_ = true;
					}

					return true;
				} else {
					return false;
				}
			}

			double epsilon() const {
				return eps_;
			}
		};		

#ifndef NO_CACHE
		POSTFIX_SCHEMA(Cache) cache;
#endif
*/

	class faceset_helper {};
	
	faceset_helper* faceset_helper_;
	double precision_;

	public:
		OpenCascadeKernel()
			: AbstractKernel("opencascade")
			, faceset_helper_(nullptr) {}

		OpenCascadeKernel(const OpenCascadeKernel& other)
			: AbstractKernel("opencascade") {
			*this = other;
		}

		bool convert(const geometry::taxonomy::extrusion&, TopoDS_Shape&);
		bool convert(const geometry::taxonomy::face&, TopoDS_Shape&);
		bool convert(const geometry::taxonomy::matrix4&, gp_Trsf&);
		bool convert(const geometry::taxonomy::direction3&, gp_Dir&);
	};

	/*
	IfcUtil::IfcBaseClass* POSTFIX_SCHEMA(tesselate_)(const TopoDS_Shape& shape, double deflection);
	IfcUtil::IfcBaseClass* POSTFIX_SCHEMA(serialise_)(const TopoDS_Shape& shape, bool advanced);
	*/

}
}
}

#endif
