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

#ifndef BOOLEAN_UTILS_H
#define BOOLEAN_UTILS_H

#include <TopoDS_Shape.hxx>
#include <TopTools_ListOfShape.hxx>
#include <Geom_Surface.hxx>
#include <TopoDS_Face.hxx>
#include <BRepTopAdaptor_FClass2d.hxx>
#include <BRep_Tool.hxx>
#include <BRepTools.hxx>
#include <TopTools_IndexedMapOfShape.hxx>
#include <BOPAlgo_Operation.hxx>

namespace IfcGeom {
	namespace util {

		void copy_operand(const TopTools_ListOfShape& l, TopTools_ListOfShape& r);

		TopoDS_Shape copy_operand(const TopoDS_Shape& s);

		double min_edge_length(const TopoDS_Shape& a);

		double min_vertex_edge_distance(const TopoDS_Shape& a, double min_search, double max_search);

		class points_on_planar_face_generator {
		private:
			const TopoDS_Face& f_;
			Handle(Geom_Surface) plane_;
			BRepTopAdaptor_FClass2d cls_;
			double u0, u1, v0, v1;
			int i, j;
			bool inset_;
			static const int N = 10;

		public:
			points_on_planar_face_generator(const TopoDS_Face& f, bool inset = false)
				: f_(f)
				, plane_(BRep_Tool::Surface(f_))
				, cls_(f_, BRep_Tool::Tolerance(f_))
				, i((int)inset), j((int)inset)
				, inset_(inset)
			{
				BRepTools::UVBounds(f_, u0, u1, v0, v1);
			}

			void reset();

			bool operator()(gp_Pnt& p);
		};

		bool faces_overlap(const TopoDS_Face& f, const TopoDS_Face& g);

		double min_face_face_distance(const TopoDS_Shape& a, double max_search);

		int bounding_box_overlap(double p, const TopoDS_Shape& a, const TopTools_ListOfShape& b, TopTools_ListOfShape& c);

		bool get_edge_axis(const TopoDS_Edge& e, gp_Ax1& ax);

		bool is_subset(const TopTools_IndexedMapOfShape& lhs, const TopTools_IndexedMapOfShape& rhs);

		bool is_extrusion(const gp_Vec& v, const TopoDS_Shape& s, TopoDS_Face& base, std::pair<double, double>& interval);

		int eliminate_touching_operands(double prec, const TopoDS_Shape& a, const TopTools_ListOfShape& bs, TopTools_ListOfShape& c);

		int eliminate_narrow_operands(double prec, const TopTools_ListOfShape& bs, TopTools_ListOfShape & c);

		TopoDS_Shape unify(const TopoDS_Shape& s, double tolerance);

		bool boolean_subtraction_2d_using_builder(const TopoDS_Shape& a_input, const TopTools_ListOfShape& b_input, TopoDS_Shape& result, double eps);

		struct boolean_settings {
			bool debug, attempt_2d;
			double precision;
		};

		bool boolean_operation(const boolean_settings& settings, const TopoDS_Shape&, const TopTools_ListOfShape&, BOPAlgo_Operation, TopoDS_Shape&, double fuzziness = -1.);

		bool boolean_operation(const boolean_settings& settings, const TopoDS_Shape&, const TopoDS_Shape&, BOPAlgo_Operation, TopoDS_Shape&, double fuzziness = -1.);

		TopoDS_Shape ensure_fit_for_subtraction(const TopoDS_Shape& shape, double tol);
	}
}

#endif