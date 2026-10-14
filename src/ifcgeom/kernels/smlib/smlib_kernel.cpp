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

#include "smlib_kernel.h"
#include "smlib_utils.h"

#include "../../../ifcgeom/taxonomy.h"

#include <SmApiBrep.h>
#include <SmApiCurves.h>
#include <SmApiGeneral.h>
#include <SmApiPrimitives.h>
#include <SmApiQueries.h>
#include <SmApiSurfaces.h>
#include <SmApiTrimmedSurfaces.h>

#include <SmAxis2Placement.h>
#include <SmBSplineCurve.h>
#include <SmBSplineSurface.h>
#include <SmBrep.h>
#include <SmCircle.h>
#include <SmContext.h>
#include <SmCurve.h>
#include <SmEllipse.h>
#include <SmLine.h>
#include <SmNurbsCrv.h>
#include <SmNurbsSrf.h>
#include <SmPlane.h>
#include <SmPointClass.h>
#include <SmSurface.h>
#include <SmVector3d.h>

#include <nurbs.h>

#include <algorithm>
#include <cmath>
#include <limits>
#include <memory>
#include <string>
#include <vector>

using namespace ifcopenshell::geom;
using namespace ifcopenshell::geom::kernels;

namespace {

	constexpr double PI = 3.14159265358979323846;
	constexpr double TAU = 2. * PI;

	SmPoint3d to_point(const Eigen::Vector3d& v) {
		return SmPoint3d(v(0), v(1), v(2));
	}

	Eigen::Vector3d to_eigen(const SmPoint3d& p) {
		return Eigen::Vector3d(p.x, p.y, p.z);
	}

	/// Evaluates a polynomial or rational B-spline curve. The knots are given as
	/// unique values with their multiplicities, the control points are matched
	/// with the optional weights.
	Eigen::Vector3d evaluate_bspline(
		const std::vector<Eigen::Vector3d>& control_points,
		const std::vector<double>& weights,
		const std::vector<double>& knots,
		const std::vector<int>& multiplicities,
		int degree,
		double u) {
		std::vector<double> flat_knots;
		for (size_t i = 0; i < knots.size(); ++i) {
			for (int j = 0; j < std::max(1, multiplicities[i]); ++j) {
				flat_knots.push_back(knots[i]);
			}
		}
		const int n = (int)control_points.size() - 1;
		u = std::max(flat_knots.front(), std::min(flat_knots.back(), u));
		int span = degree;
		for (int i = degree; i <= n; ++i) {
			if (u >= flat_knots[i] && u < flat_knots[i + 1]) {
				span = i;
				break;
			}
		}
		if (u >= flat_knots[n + 1]) {
			span = n;
		}

		std::vector<double> N((size_t)degree + 1, 1.);
		std::vector<double> left((size_t)degree + 1, 0.), right((size_t)degree + 1, 0.);
		for (int j = 1; j <= degree; ++j) {
			left[(size_t)j] = u - flat_knots[(size_t)(span + 1 - j)];
			right[(size_t)j] = flat_knots[(size_t)(span + j)] - u;
			double saved = 0.;
			for (int r = 0; r < j; ++r) {
				const double denominator = right[(size_t)(r + 1)] + left[(size_t)(j - r)];
				const double temp = denominator == 0. ? 0. : N[(size_t)r] / denominator;
				N[(size_t)r] = saved + right[(size_t)(r + 1)] * temp;
				saved = left[(size_t)(j - r)] * temp;
			}
			N[(size_t)j] = saved;
		}

		const bool rational = weights.size() == control_points.size();
		Eigen::Vector4d sum = Eigen::Vector4d::Zero();
		for (int j = 0; j <= degree; ++j) {
			const int index = span - degree + j;
			const double w = rational ? weights[(size_t)index] : 1.;
			const double coefficient = N[(size_t)j] * w;
			sum.head<3>() += coefficient * control_points[(size_t)index];
			sum(3) += coefficient;
		}
		if (sum(3) == 0.) {
			return control_points.front();
		}
		return sum.head<3>() / sum(3);
	}

	bool evaluate_curve(const taxonomy::item::ptr& basis, double u, Eigen::Vector3d& p) {
		if (!basis) {
			return false;
		}
		switch (basis->kind()) {
		case taxonomy::LINE: {
			const auto line = taxonomy::cast<taxonomy::line>(basis);
			const auto& m = line->matrix->ccomponents();
			p = m.block<3, 1>(0, 3) + u * m.block<3, 1>(0, 2);
			return true;
		}
		case taxonomy::CIRCLE: {
			const auto circle = taxonomy::cast<taxonomy::circle>(basis);
			const auto& m = circle->matrix->ccomponents();
			const Eigen::Vector3d center = m.block<3, 1>(0, 3);
			p = center + circle->radius * (std::cos(u) * m.block<3, 1>(0, 0) + std::sin(u) * m.block<3, 1>(0, 1));
			return true;
		}
		case taxonomy::ELLIPSE: {
			const auto ellipse = taxonomy::cast<taxonomy::ellipse>(basis);
			const auto& m = ellipse->matrix->ccomponents();
			const Eigen::Vector3d center = m.block<3, 1>(0, 3);
			p = center + ellipse->radius * std::cos(u) * m.block<3, 1>(0, 0) + ellipse->radius2 * std::sin(u) * m.block<3, 1>(0, 1);
			return true;
		}
		case taxonomy::BSPLINE_CURVE: {
			const auto bspline = taxonomy::cast<taxonomy::bspline_curve>(basis);
			std::vector<Eigen::Vector3d> control_points;
			control_points.reserve(bspline->control_points.size());
			for (const auto& cp : bspline->control_points) {
				control_points.push_back(cp->ccomponents());
			}
			p = evaluate_bspline(
				control_points,
				bspline->weights ? *bspline->weights : std::vector<double>(),
				bspline->knots,
				bspline->multiplicities,
				bspline->degree,
				u);
			return true;
		}
		default:
			return false;
		}
	}

	bool curve_parameter_range(const taxonomy::item::ptr& basis, double& lo, double& hi) {
		if (!basis) {
			return false;
		}
		switch (basis->kind()) {
		case taxonomy::LINE:
			lo = -1.e6;
			hi = 1.e6;
			return true;
		case taxonomy::CIRCLE:
		case taxonomy::ELLIPSE:
			lo = 0.;
			hi = TAU;
			return true;
		case taxonomy::BSPLINE_CURVE: {
			const auto bspline = taxonomy::cast<taxonomy::bspline_curve>(basis);
			if (bspline->knots.empty()) {
				return false;
			}
			lo = bspline->knots.front();
			hi = bspline->knots.back();
			return true;
		}
		default:
			return false;
		}
	}

	/// Finds the parameter of the point on the curve that is closest to `p`.
	bool project_point(const taxonomy::item::ptr& basis, const Eigen::Vector3d& p, double& u) {
		double lo, hi;
		if (!curve_parameter_range(basis, lo, hi)) {
			return false;
		}
		if (hi - lo > 1.e5) {
			// Unbounded curves cannot be projected robustly.
			return false;
		}
		const int num_samples = 256;
		double best = lo;
		double best_distance = std::numeric_limits<double>::max();
		for (int i = 0; i <= num_samples; ++i) {
			const double candidate = lo + (hi - lo) * (double)i / (double)num_samples;
			Eigen::Vector3d q;
			if (!evaluate_curve(basis, candidate, q)) {
				return false;
			}
			const double distance = (q - p).squaredNorm();
			if (distance < best_distance) {
				best_distance = distance;
				best = candidate;
			}
		}
		const double step = (hi - lo) / (double)num_samples;
		for (int i = 0; i < 40; ++i) {
			const double delta = step * std::pow(0.5, (double)i);
			for (const double candidate : { best - delta, best + delta }) {
				Eigen::Vector3d q;
				if (!evaluate_curve(basis, candidate, q)) {
					break;
				}
				const double distance = (q - p).squaredNorm();
				if (distance < best_distance) {
					best_distance = distance;
					best = candidate;
				}
			}
		}
		u = best;
		return true;
	}

	struct trim {
		// 0 = entire curve, 1 = a point, 2 = a parameter value
		int type = 0;
		Eigen::Vector3d point = Eigen::Vector3d::Zero();
		double value = 0.;
	};

	trim convert_trim(const std::variant<boost::blank, taxonomy::point3::ptr, double>& t) {
		trim result;
		if (t.index() == 1) {
			result.type = 1;
			result.point = std::get<taxonomy::point3::ptr>(t)->ccomponents();
		} else if (t.index() == 2) {
			result.type = 2;
			result.value = std::get<double>(t);
		}
		return result;
	}

	SmTArray<SmPoint3d> to_point_array(const std::vector<Eigen::Vector3d>& points) {
		SmTArray<SmPoint3d> result;
		for (const auto& p : points) {
			result.Add(to_point(p));
		}
		return result;
	}

	/// Builds a B-spline curve from its definition. The canonical constructor is
	/// used because SMLib reads out of bounds on knot vectors that are not
	/// clamped, which is what periodic curves of free form breps have.
	SmBSplineCurve* create_nurbs_curve(
		const std::vector<Eigen::Vector3d>& control_points,
		const std::vector<double>& weights,
		const std::vector<double>& knots,
		const std::vector<int>& multiplicities,
		int degree) {
		smlib_ensure_context();
		if (knots.empty() || knots.size() != multiplicities.size() || control_points.size() < (size_t)degree + 1) {
			return nullptr;
		}
		size_t total = 0;
		for (const int m : multiplicities) {
			total += std::max(1, m);
		}
		if (total != control_points.size() + (size_t)degree + 1) {
			return nullptr;
		}

		SmTArray<SmPoint3d> points;
		SmTArray<double> point_weights;
		const bool rational = weights.size() == control_points.size();
		for (size_t i = 0; i < control_points.size(); ++i) {
			points.Add(SmPoint3d(control_points[i](0), control_points[i](1), control_points[i](2)));
			if (rational) {
				point_weights.Add(weights[i]);
			}
		}
		SmTArray<ULONG> knot_multiplicities;
		for (const int m : multiplicities) {
			knot_multiplicities.Add((ULONG)std::max(1, m));
		}
		SmTArray<double> unique_knots;
		for (const double k : knots) {
			unique_knots.Add(k);
		}

		SmBSplineCurve* result = nullptr;
		SmTArray<SmBSplineCurve*> curves;
		if (SmBSplineCurve::CreateCanonical(
				*SmApiGetOrCreateContext(),
				3,
				(ULONG)degree,
				points,
				SM_CF_UNSPECIFIED,
				knot_multiplicities,
				unique_knots,
				SM_KT_UNSPECIFIED,
				rational ? &point_weights : nullptr,
				nullptr,
				result) != SM_SUCCESS ||
			!result) {
			return nullptr;
		}
		return result;
	}

	/// Approximates a portion of a curve by an interpolating B-spline.
	SmCurve* create_sampled_curve(const taxonomy::item::ptr& basis, double u0, double u1, double tolerance) {
		// The curve is sampled in the direction in which it is traversed, so
		// that the resulting curve follows the loop it belongs to.
		const int num_samples = (int)std::max(8., std::min(256., std::ceil(std::abs(u1 - u0) * 32.)));
		std::vector<Eigen::Vector3d> points;
		points.reserve((size_t)num_samples + 1);
		for (int i = 0; i <= num_samples; ++i) {
			Eigen::Vector3d p;
			if (!evaluate_curve(basis, u0 + (u1 - u0) * (double)i / (double)num_samples, p)) {
				return nullptr;
			}
			points.push_back(p);
		}
		if ((points.back() - points.front()).norm() <= tolerance) {
			// The curve is closed; repeat the first point to allow the fitter to
			// create a closed curve.
			SmBSplineCurve* curve = nullptr;
			if (SmApiCreateCurve(to_point_array(points), curve) == SM_SUCCESS) {
				return curve;
			}
			return nullptr;
		}
		SmCurve* curve = nullptr;
		if (SmApiCreateCurveApproxPoints(to_point_array(points), curve) != SM_SUCCESS) {
			return nullptr;
		}
		return curve;
	}

	/// Moves a curve that was created in the XY plane onto the frame of the
	/// taxonomy curve it was created for.
	SmApiStatus place_in_frame(SmObject* object, const taxonomy::item::ptr& basis) {
		Eigen::Matrix4d m = Eigen::Matrix4d::Identity();
		switch (basis->kind()) {
		case taxonomy::CIRCLE:
			m = taxonomy::cast<taxonomy::circle>(basis)->matrix->ccomponents();
			break;
		case taxonomy::ELLIPSE:
			m = taxonomy::cast<taxonomy::ellipse>(basis)->matrix->ccomponents();
			break;
		default:
			return SM_SUCCESS;
		}
		SmAxis2Placement placement;
		smlib_placement_from_matrix(m, placement);
		return SmApiTransform(object, placement);
	}

	/// Creates the curve of a single edge, including the trim from the edge.
	/// The curve is created in the direction in which the edge is traversed.
	/// Resolves the curve of an edge and the parameters at which it is trimmed.
	bool resolve_edge_range(const taxonomy::edge::ptr& edge, taxonomy::item::ptr& basis, double& u0, double& u1, trim& start, trim& end, std::string& error) {
		basis = edge->basis;
		if (!basis) {
			return false;
		}

		// IfcTrimmedCurve wraps the actual curve in another edge.
		for (int i = 0; i < 8 && basis->kind() == taxonomy::EDGE; ++i) {
			auto inner = taxonomy::cast<taxonomy::edge>(basis);
			if (!inner || !inner->basis) {
				break;
			}
			basis = inner->basis;
		}

		if (basis->kind() == taxonomy::OFFSET_CURVE) {
			error = "Offset curves are not supported";
			return false;
		}
		if (basis->kind() == taxonomy::LOOP) {
			error = "The curve of the edge is a polyline";
			return false;
		}

		double lo = 0., hi = 0.;
		if (!curve_parameter_range(basis, lo, hi)) {
			error = "Unsupported curve type in loop";
			return false;
		}

		start = convert_trim(edge->start);
		end = convert_trim(edge->end);
		// The curve of the edge is traversed in the direction of the edge when
		// it is not oriented against the curve it is defined on.
		if (!edge->orientation.value_or(true)) {
			std::swap(start, end);
		}

		u0 = lo;
		u1 = hi;
		if (start.type == 1) {
			if (!project_point(basis, start.point, u0)) {
				// Fall back to the exact point for lines.
				if (basis->kind() != taxonomy::LINE) {
					error = "Unable to project the start point onto the curve";
					return false;
				}
			}
		} else if (start.type == 2) {
			u0 = start.value;
		}
		if (end.type == 1) {
			if (!project_point(basis, end.point, u1)) {
				if (basis->kind() != taxonomy::LINE) {
					error = "Unable to project the end point onto the curve";
					return false;
				}
			}
		} else if (end.type == 2) {
			u1 = end.value;
		}
		return true;
	}

	/// Points on the curve of an edge, used to determine the extent of a face.
	void sample_edge(const taxonomy::item::ptr& basis, double u0, double u1, const trim& start, const trim& end, std::vector<Eigen::Vector3d>& points) {
		const int num_samples = 16;
		if (basis->kind() == taxonomy::LINE) {
			// The parameter range of a line is unbounded, so trimmed lines are
			// sampled at their trims only.
			for (const auto& t : { start, end }) {
				Eigen::Vector3d p;
				if (t.type == 1) {
					p = t.point;
				} else if (t.type == 2) {
					if (!evaluate_curve(basis, t.value, p)) {
						continue;
					}
				} else {
					continue;
				}
				points.push_back(p);
			}
			return;
		}
		if (std::isfinite(u0) && std::isfinite(u1) && std::abs(u1 - u0) < 1.e5) {
			for (int i = 0; i <= num_samples; ++i) {
				Eigen::Vector3d p;
				if (evaluate_curve(basis, u0 + (u1 - u0) * (double)i / (double)num_samples, p)) {
					points.push_back(p);
				}
			}
		}
		for (const auto& t : { start, end }) {
			if (t.type == 1) {
				points.push_back(t.point);
			}
		}
	}

	/// The signed angular extent in radians between two trims of a conic curve.
	/// Conics are periodic, so the extent is the rotation between the trims in
	/// the direction in which the curve is traversed.
	double conic_sweep(double u0, double u1, bool forward) {
		double sweep = std::fmod(forward ? u1 - u0 : u0 - u1, TAU);
		if (sweep < 0.) {
			sweep += TAU;
		}
		return forward ? sweep : -sweep;
	}

	/// Whether an angular extent describes the entire curve, which IFC denotes
	/// with trims that coincide or that differ by a full turn.
	bool whole_conic(double sweep) {
		return std::abs(sweep) <= 1.e-6 || std::abs(std::abs(sweep) - TAU) <= 1.e-6;
	}

	/// The angular extent of a conic curve as SMLib wants it: both angles within
	/// [-360, 360] degrees, with a negative sweep expressing a traversal in the
	/// reverse direction of the curve.
	void conic_angles(double u0, double sweep, double& start_deg, double& end_deg) {
		start_deg = std::fmod(u0 * 180. / PI, 360.);
		end_deg = start_deg + sweep * 180. / PI;
		if (end_deg > 360.) {
			end_deg -= 360.;
		} else if (end_deg < -360.) {
			end_deg += 360.;
		}
	}

	/// Whether the curve of an edge is traversed in the direction of the curve
	/// it is defined on. The orientation of an edge is toggled when a loop
	/// traverses it in reverse, the curve sense is the sense of the curve with
	/// respect to its basis curve.
	bool traverses_forward(const taxonomy::edge::ptr& edge) {
		return edge->curve_sense.value_or(true) == edge->orientation.value_or(true);
	}

	SmCurve* create_edge_curve(const taxonomy::edge::ptr& edge, double precision, std::string& error) {
		if (!edge->basis) {
			if (edge->start.index() != 1 || edge->end.index() != 1) {
				error = "Edge without curve only supports cartesian trims";
				return nullptr;
			}
			const Eigen::Vector3d a = std::get<taxonomy::point3::ptr>(edge->start)->ccomponents();
			const Eigen::Vector3d b = std::get<taxonomy::point3::ptr>(edge->end)->ccomponents();
			SmLine* line = nullptr;
			if (SmApiCreateLineSegment(to_point(a), to_point(b), line) != SM_SUCCESS) {
				error = "Failed to create line segment";
				return nullptr;
			}
			return line;
		}

		taxonomy::item::ptr basis;
		double u0 = 0., u1 = 0.;
		trim start, end;
		if (!resolve_edge_range(edge, basis, u0, u1, start, end, error)) {
			return nullptr;
		}

		const double tolerance = 1.e-9;
		// Edges of closed curves, such as the seam of a cylinder, start and end
		// in the same point and describe the entire curve.
		const bool closed = start.type == 1 && end.type == 1 && (start.point - end.point).norm() <= precision;
		// Conics are traversed in the direction in which they are defined only
		// when the edge is not oriented against them.
		const bool forward = traverses_forward(edge);
		switch (basis->kind()) {
		case taxonomy::LINE: {
			Eigen::Vector3d a, b;
			if (start.type == 1) {
				a = start.point;
			} else if (!evaluate_curve(basis, u0, a)) {
				error = "Unable to evaluate line";
				return nullptr;
			}
			if (end.type == 1) {
				b = end.point;
			} else if (!evaluate_curve(basis, u1, b)) {
				error = "Unable to evaluate line";
				return nullptr;
			}
			if ((b - a).norm() <= tolerance) {
				error = "Degenerate line segment";
				return nullptr;
			}
			SmLine* line = nullptr;
			if (SmApiCreateLineSegment(to_point(a), to_point(b), line) != SM_SUCCESS) {
				error = "Failed to create line segment";
				return nullptr;
			}
			return line;
		}
		case taxonomy::CIRCLE: {
			const auto circle = taxonomy::cast<taxonomy::circle>(basis);
			const double sweep = conic_sweep(u0, u1, forward);
			double start_deg = 0., end_deg = 0.;
			conic_angles(u0, sweep, start_deg, end_deg);
			const bool whole = closed || whole_conic(sweep) || (start.type == 0 && end.type == 0);
			SmObject* curve = nullptr;
			if (whole) {
				SmCircle* c = nullptr;
				if (SmApiCreateCircle(SmPoint3d(0., 0., 0.), circle->radius, c) != SM_SUCCESS) {
					error = "Failed to create circle";
					return nullptr;
				}
				curve = c;
			} else {
				// SMLib sweeps counter clockwise from the start angle to the end
				// angle, so an arc that is traversed in the opposite direction is
				// created in reverse and has its parameterization reversed.
				SmBSplineCurve* arc = nullptr;
				const double from_deg = sweep < 0. ? end_deg : start_deg;
				const double to_deg = sweep < 0. ? start_deg : end_deg;
				if (SmApiCreateArc(SmPoint3d(0., 0., 0.), circle->radius, from_deg, to_deg, arc) != SM_SUCCESS) {
					error = "Failed to create circular arc";
					return nullptr;
				}
				if (sweep < 0.) {
					const SmExtent1d interval = arc->GetNaturalInterval();
					SmExtent1d reversed;
					if (arc->ReverseParameterization(interval, reversed) != SM_SUCCESS) {
						delete arc;
						error = "Failed to reverse circular arc";
						return nullptr;
					}
				}
				curve = arc;
			}
			const SmApiStatus status = place_in_frame(curve, basis);
			if (status != SM_SUCCESS) {
				delete curve;
				error = "Failed to place circular arc";
				return nullptr;
			}
			return static_cast<SmCurve*>(curve);
		}
		case taxonomy::ELLIPSE: {
			const auto ellipse = taxonomy::cast<taxonomy::ellipse>(basis);
			const double sweep = conic_sweep(u0, u1, forward);
			const bool whole = closed || whole_conic(sweep) || (start.type == 0 && end.type == 0);
			if (whole) {
				SmEllipse* e = nullptr;
				if (SmApiCreateEllipse(SmPoint3d(0., 0., 0.), ellipse->radius, ellipse->radius2, e) != SM_SUCCESS) {
					error = "Failed to create ellipse";
					return nullptr;
				}
				const SmApiStatus status = place_in_frame(e, basis);
				if (status != SM_SUCCESS) {
					delete e;
					error = "Failed to place ellipse";
					return nullptr;
				}
				return e;
			}
			// SMLib has no analytic elliptical arc; approximate the trimmed
			// portion with an interpolating spline.
			SmCurve* sampled = create_sampled_curve(basis, u0, u0 + sweep, tolerance);
			if (!sampled) {
				error = "Failed to approximate elliptical arc";
				return nullptr;
			}
			return sampled;
		}
		case taxonomy::BSPLINE_CURVE: {
			const auto bspline = taxonomy::cast<taxonomy::bspline_curve>(basis);
			std::vector<Eigen::Vector3d> control_points;
			for (const auto& cp : bspline->control_points) {
				control_points.push_back(cp->ccomponents());
			}
			const std::vector<double> weights = bspline->weights ? *bspline->weights : std::vector<double>();
			const bool whole = closed || (start.type == 0 && end.type == 0);
			if (whole) {
				SmBSplineCurve* curve = create_nurbs_curve(control_points, weights, bspline->knots, bspline->multiplicities, bspline->degree);
				if (!curve) {
					error = "Failed to create B-spline curve";
					return nullptr;
				}
				return curve;
			}
			SmCurve* sampled = create_sampled_curve(basis, u0, u1, tolerance);
			if (!sampled) {
				error = "Failed to approximate trimmed B-spline curve";
				return nullptr;
			}
			return sampled;
		}
		default:
			error = "Unsupported curve type in loop";
			return nullptr;
		}
	}

	void delete_curves(std::vector<SmCurve*>& curves) {
		for (auto* c : curves) {
			delete c;
		}
		curves.clear();
	}

	/// Creates the curves of an edge. An edge whose curve is a polyline, which is
	/// what IfcPolyLine maps to, contributes a curve for each of its segments.
	bool append_edge_curves(const taxonomy::edge::ptr& edge, std::vector<SmCurve*>& curves, double precision, std::string& error) {
		auto basis = edge->basis;
		for (int i = 0; i < 8 && basis && basis->kind() == taxonomy::EDGE; ++i) {
			basis = taxonomy::cast<taxonomy::edge>(basis)->basis;
		}
		if (basis && basis->kind() == taxonomy::LOOP) {
			const auto polyline = taxonomy::cast<taxonomy::loop>(basis);
			// The curve of the edge is traversed in the reverse direction of the
			// polyline when the edge is reversed.
			const bool reversed = !edge->curve_sense.value_or(true) || !edge->orientation.value_or(true);
			std::vector<SmCurve*> segments;
			for (const auto& segment : polyline->children) {
				taxonomy::edge::ptr to_create = segment;
				if (reversed) {
					// A copy is reversed so that the shared input is left alone.
					to_create = taxonomy::make<taxonomy::edge>(*segment);
					to_create->reverse();
				}
				if (!append_edge_curves(to_create, segments, precision, error)) {
					delete_curves(segments);
					return false;
				}
			}
			if (reversed) {
				std::reverse(segments.begin(), segments.end());
			}
			curves.insert(curves.end(), segments.begin(), segments.end());
			return true;
		}

		SmCurve* curve = create_edge_curve(edge, precision, error);
		if (!curve) {
			return false;
		}
		curves.push_back(curve);
		return true;
	}

	bool create_loop_curves(const taxonomy::loop::ptr& loop, double precision, std::vector<SmCurve*>& curves, std::string& error) {
		if (!loop) {
			error = "Missing loop";
			return false;
		}
		std::vector<SmCurve*> created;
		for (const auto& e : loop->children) {
			if (!append_edge_curves(e, created, precision, error)) {
				delete_curves(created);
				return false;
			}
		}
		curves.insert(curves.end(), created.begin(), created.end());
		return true;
	}

	/// Whether the face is bounded by planar curves only (as opposed to a face
	/// on a free form surface).
	const taxonomy::bspline_surface::ptr face_surface(const taxonomy::face::ptr& face) {
		if (!face || !face->basis) {
			return nullptr;
		}
		if (face->basis->kind() == taxonomy::BSPLINE_SURFACE) {
			return taxonomy::cast<taxonomy::bspline_surface>(face->basis);
		}
		return nullptr;
	}

	/// Samples the boundary of a face, and whether it contains an edge that is
	/// closed in itself, which happens on surfaces that wrap around an axis.
	bool face_points(const taxonomy::face::ptr& face, double precision, std::vector<Eigen::Vector3d>& points, bool& has_closed_edge, std::string& error) {
		has_closed_edge = false;
		for (const auto& loop : face->children) {
			for (const auto& edge : loop->children) {
				taxonomy::item::ptr basis;
				double u0 = 0., u1 = 0.;
				trim start, end;
				if (!resolve_edge_range(edge, basis, u0, u1, start, end, error)) {
					auto polyline_basis = edge->basis;
					for (int i = 0; i < 8 && polyline_basis && polyline_basis->kind() == taxonomy::EDGE; ++i) {
						polyline_basis = taxonomy::cast<taxonomy::edge>(polyline_basis)->basis;
					}
					if (!polyline_basis || polyline_basis->kind() != taxonomy::LOOP) {
						return false;
					}
					// The curve of the edge is a polyline: sample its segments.
					const auto polyline = taxonomy::cast<taxonomy::loop>(polyline_basis);
					error.clear();
					for (const auto& segment : polyline->children) {
						taxonomy::item::ptr segment_basis;
						double s0 = 0., s1 = 0.;
						trim segment_start, segment_end;
						if (!resolve_edge_range(segment, segment_basis, s0, s1, segment_start, segment_end, error)) {
							return false;
						}
						sample_edge(segment_basis, s0, s1, segment_start, segment_end, points);
					}
					continue;
				}
				const bool conic = basis->kind() == taxonomy::CIRCLE || basis->kind() == taxonomy::ELLIPSE;
				// Conics are periodic, so the extent between the trims is the
				// rotation between them in the direction of the edge.
				const double span = conic ? conic_sweep(u0, u1, traverses_forward(edge)) : u1 - u0;
				if (conic || basis->kind() == taxonomy::BSPLINE_CURVE) {
					// Edges of closed curves begin and end in the same point, and
					// conics that are not trimmed describe their entire curve.
					const bool coincident = start.type == 1 && end.type == 1 && (start.point - end.point).norm() <= precision;
					has_closed_edge = has_closed_edge || coincident || std::abs(span) >= TAU - 1.e-6;
				}
				sample_edge(basis, u0, u0 + span, start, end, points);
			}
		}
		return true;
	}

	bool face_points(const taxonomy::face::ptr& face, double precision, std::vector<Eigen::Vector3d>& points, std::string& error) {
		bool has_closed_edge = false;
		return face_points(face, precision, points, has_closed_edge, error);
	}

	/// The extent of the boundary of a face, in the frame the face is defined in.
	bool face_extent(const taxonomy::face::ptr& face, double precision, Eigen::Vector3d& min, Eigen::Vector3d& max, std::string& error) {
		std::vector<Eigen::Vector3d> points;
		if (!face_points(face, precision, points, error)) {
			return false;
		}
		if (points.empty()) {
			error = "Failed to determine the extent of the face";
			return false;
		}
		min.setConstant(std::numeric_limits<double>::infinity());
		max.setConstant(-std::numeric_limits<double>::infinity());
		for (const auto& p : points) {
			min = min.cwiseMin(p);
			max = max.cwiseMax(p);
		}
		return true;
	}

	/// The arc of a surface of revolution a face occupies, in the frame of the
	/// surface, and the extent of the face along the axis of revolution.
	struct revolution_arc {
		double from = 0.;
		double to = 0.;
		bool full = false;
		double axial_from = 0.;
		double axial_to = 0.;
	};

	/// Determines which part of a surface of revolution a face occupies. The
	/// boundary curves of a face on such a surface span the arc it covers, and
	/// the largest gap between them marks the part of the surface without a face.
	bool revolution_arc_of(const taxonomy::face::ptr& face, const Eigen::Matrix4d& frame, double precision, revolution_arc& arc, std::string& error) {
		std::vector<Eigen::Vector3d> points;
		bool has_closed_edge = false;
		if (!face_points(face, precision, points, has_closed_edge, error)) {
			return false;
		}
		if (points.size() < 2) {
			error = "Failed to determine the extent of the face";
			return false;
		}

		const Eigen::Matrix4d inverse = frame.inverse();
		std::vector<double> angles;
		angles.reserve(points.size());
		arc.axial_from = std::numeric_limits<double>::infinity();
		arc.axial_to = -arc.axial_from;
		for (const auto& p : points) {
			const Eigen::Vector4d local = inverse * Eigen::Vector4d(p(0), p(1), p(2), 1.);
			double angle = std::atan2(local(1), local(0));
			if (angle < 0.) {
				angle += TAU;
			}
			angles.push_back(angle);
			arc.axial_from = std::min(arc.axial_from, local(2));
			arc.axial_to = std::max(arc.axial_to, local(2));
		}
		std::sort(angles.begin(), angles.end());

		size_t widest = 0;
		double widest_gap = 0.;
		for (size_t i = 0; i < angles.size(); ++i) {
			const double next = (i + 1 < angles.size()) ? angles[i + 1] : angles[0] + TAU;
			if (next - angles[i] > widest_gap) {
				widest_gap = next - angles[i];
				widest = i;
			}
		}
		arc.full = has_closed_edge || widest_gap < 4. * TAU / (double)angles.size();
		arc.from = angles[(widest + 1) % angles.size()];
		arc.to = angles[widest];
		while (arc.to < arc.from) {
			arc.to += TAU;
		}
		return true;
	}

	/// The distance of a point to the polyline through a range of points.
	double distance_to_polyline(const Eigen::Vector3d& p, const std::vector<Eigen::Vector3d>& points) {
		double best = std::numeric_limits<double>::infinity();
		for (size_t i = 0; i + 1 < points.size(); ++i) {
			const Eigen::Vector3d a = points[i];
			const Eigen::Vector3d d = points[i + 1] - a;
			const double length = d.squaredNorm();
			if (length <= 0.) {
				best = std::min(best, (p - a).norm());
				continue;
			}
			double t = (p - a).dot(d) / length;
			t = std::max(0., std::min(1., t));
			best = std::min(best, (p - (a + t * d)).norm());
		}
		return best;
	}

	/// Creates the face of a surface as its entire parameter domain. Faces whose
	/// boundary runs along the edges of that domain cover it exactly, such as the
	/// bore of a hole or the tube of a bottle; whether that is the case is
	/// verified unless the caller passes `boundaries_must_match` as false, which
	/// it does for faces of surfaces that SMLib cannot trim.
	bool domain_face_of(const taxonomy::face::ptr& face, SmSurface* surface, double precision, bool boundaries_must_match, SmBrep*& brep, std::string& error) {
		brep = nullptr;
		const SmExtent2d domain = surface->GetNaturalUVDomain();
		if (!domain.IsBounded()) {
			error = "unbounded domain";
			return false;
		}
		std::vector<Eigen::Vector3d> points;
		bool has_closed_edge = false;
		if (!face_points(face, precision, points, has_closed_edge, error) || points.empty()) {
			if (error.empty()) {
				error = "no boundary points";
			}
			return false;
		}

		// The images of the edges of the parameter domain of the surface.
		const double u0 = domain.GetMin().x, u1 = domain.GetMax().x;
		const double v0 = domain.GetMin().y, v1 = domain.GetMax().y;
		const int num_samples = 64;
		std::vector<Eigen::Vector3d> boundary;
		for (int edge = 0; edge < 4; ++edge) {
			boundary.clear();
			for (int i = 0; i <= num_samples; ++i) {
				const double t = (double)i / (double)num_samples;
				double u = u0 + t * (u1 - u0), v = v0;
				switch (edge) {
				case 1: u = u1; v = v0 + t * (v1 - v0); break;
				case 2: u = u1 - t * (u1 - u0); v = v1; break;
				case 3: u = u0; v = v1 - t * (v1 - v0); break;
				}
				SmVector3d p;
				if (SmApiEvaluateSurfacePoint(surface, SmVector2d(u, v), p) == SM_SUCCESS) {
					boundary.push_back(Eigen::Vector3d(p[0], p[1], p[2]));
				}
			}
			if (boundary.size() < 2) {
				error = "boundary of the domain is empty";
				return false;
			}
			if (!boundaries_must_match) {
				continue;
			}
			auto min = boundary.front();
			auto max = boundary.front();
			for (const auto& p : boundary) {
				min = min.cwiseMin(p);
				max = max.cwiseMax(p);
			}
			const double tolerance = std::max(precision, 1.e-6 * (max - min).norm());
			for (const auto& p : points) {
				const double distance = distance_to_polyline(p, boundary);
				if (distance > tolerance) {
					error = "the boundary of the face is not on the boundary of the domain";
					return false;
				}
			}
		}

		SmBrep* result = new (*SmApiGetOrCreateContext()) SmBrep();
		SmFace* new_face = nullptr;
		if (result->CreateFaceFromSurface(surface, domain, new_face) != SM_SUCCESS || !new_face) {
			delete result;
			error = "CreateFaceFromSurface failed";
			return false;
		}
		brep = result;
		return true;
	}

	/// Whether a surface wraps around in either of its parameter directions, in
	/// which case SMLib cannot trim it.
	bool surface_wraps(SmSurface* surface, const SmExtent2d& domain, double tolerance) {
		const SmPoint2d min = domain.GetMin();
		const SmPoint2d max = domain.GetMax();
		if (!domain.IsBounded()) {
			return false;
		}
		const double umid = 0.5 * (min.x + max.x);
		const double vmid = 0.5 * (min.y + max.y);
		SmVector3d a, b;
		if (SmApiEvaluateSurfacePoint(surface, SmVector2d(min.x, vmid), a) == SM_SUCCESS &&
			SmApiEvaluateSurfacePoint(surface, SmVector2d(max.x, vmid), b) == SM_SUCCESS &&
			(a - b).LengthSquared() <= tolerance * tolerance) {
			return true;
		}
		if (SmApiEvaluateSurfacePoint(surface, SmVector2d(umid, min.y), a) == SM_SUCCESS &&
			SmApiEvaluateSurfacePoint(surface, SmVector2d(umid, max.y), b) == SM_SUCCESS &&
			(a - b).LengthSquared() <= tolerance * tolerance) {
			return true;
		}
		return false;
	}

	/// Creates the sheet of a face on a cylinder by sweeping the cross section
	/// of the face along the axis, as SMLib trims surfaces of revolution that
	/// wrap around their axis incompletely or not at all.
	SmBrep* create_cylinder_sheet(const taxonomy::face::ptr& face, const taxonomy::cylinder::ptr& cylinder, double precision, std::string& error) {
		if (face->children.size() != 1) {
			return nullptr;
		}
		smlib_ensure_context();
		const Eigen::Matrix4d frame = cylinder->matrix->ccomponents();
		revolution_arc arc;
		if (!revolution_arc_of(face, frame, precision, arc, error)) {
			return nullptr;
		}
		const double extent = arc.axial_to - arc.axial_from;
		if (extent <= precision) {
			error = "Degenerate cylindrical face";
			return nullptr;
		}

		SmAxis2Placement placement;
		smlib_placement_from_matrix(frame, placement);

		SmObject* profile = nullptr;
		if (arc.full) {
			SmCircle* circle = nullptr;
			if (SmApiCreateCircle(SmPoint3d(0., 0., arc.axial_from), cylinder->radius, circle) != SM_SUCCESS || !circle) {
				error = "Failed to create the profile of a cylindrical face";
				return nullptr;
			}
			profile = circle;
		} else {
			SmBSplineCurve* segment = nullptr;
			if (SmApiCreateArc(
					SmPoint3d(0., 0., arc.axial_from), cylinder->radius, arc.from * 180. / PI, arc.to * 180. / PI, segment) != SM_SUCCESS ||
				!segment) {
				error = "Failed to create the profile of a cylindrical face";
				return nullptr;
			}
			profile = segment;
		}
		if (SmApiTransform(profile, placement) != SM_SUCCESS) {
			delete profile;
			error = "Failed to place the profile of a cylindrical face";
			return nullptr;
		}

		const Eigen::Vector3d axis = frame.block<3, 1>(0, 2);
		SmTArray<SmCurve*> profiles;
		profiles.Add(static_cast<SmCurve*>(profile));
		SmBrep* brep = nullptr;
		const SmApiStatus status = SmApiCreateLinearSweep(
			profiles, SmVector3d(axis(0), axis(1), axis(2)), extent, FALSE, brep);
		if (status != SM_SUCCESS || !brep) {
			error = "Failed to sweep the profile of a cylindrical face";
			return nullptr;
		}
		return brep;
	}

	/// The extent of a bounding box along the axis of a frame, in which the
	/// axis is the third column.
	void axial_extent(const Eigen::Matrix4d& frame, const Eigen::Vector3d& min, const Eigen::Vector3d& max, double& from, double& to) {
		const Eigen::Vector3d origin = frame.block<3, 1>(0, 3);
		const Eigen::Vector3d axis = frame.block<3, 1>(0, 2);
		from = std::numeric_limits<double>::infinity();
		to = -from;
		for (int i = 0; i < 8; ++i) {
			const Eigen::Vector3d corner(
				(i & 1) ? max(0) : min(0),
				(i & 2) ? max(1) : min(1),
				(i & 4) ? max(2) : min(2));
			const double t = (corner - origin).dot(axis);
			from = std::min(from, t);
			to = std::max(to, t);
		}
	}

	/// The frame of an analytic surface of revolution, which is the placement
	/// of the cylinder, cone or torus the face lies on.
	bool revolution_frame(const taxonomy::item::ptr& basis, Eigen::Matrix4d& frame) {
		if (basis->kind() == taxonomy::CYLINDER) {
			frame = taxonomy::cast<taxonomy::cylinder>(basis)->matrix->ccomponents();
			return true;
		}
		if (basis->kind() == taxonomy::TORUS) {
			frame = taxonomy::cast<taxonomy::torus>(basis)->matrix->ccomponents();
			return true;
		}
		return false;
	}

	/// Creates the analytic surface a face lies on. In the frame of the surface
	/// the axis of revolution is the Z axis, as SmApi places it there.
	SmSurface* create_revolution_surface(const taxonomy::item::ptr& basis, const Eigen::Vector3d& min, const Eigen::Vector3d& max, double precision, std::string& error) {
		smlib_ensure_context();
		Eigen::Matrix4d frame;
		if (!revolution_frame(basis, frame)) {
			error = "Unsupported surface";
			return nullptr;
		}
		SmSurface* surface = nullptr;
		if (basis->kind() == taxonomy::CYLINDER) {
			const double radius = taxonomy::cast<taxonomy::cylinder>(basis)->radius;
			double from = 0., to = 0.;
			axial_extent(frame, min, max, from, to);
			const double margin = precision + 0.05 * (to - from);
			// The extent along the axis is derived from the boundary of the
			// face, as SmApi creates cylinders with a finite height.
			if (SmApiCreateCylinder(SmVector3d(0., 0., from - margin), radius, (to - from) + 2. * margin, surface) != SM_SUCCESS || !surface) {
				error = "Failed to create cylindrical surface";
				return nullptr;
			}
		} else {
			const auto torus = taxonomy::cast<taxonomy::torus>(basis);
			if (SmApiCreateTorus(SmVector3d(0., 0., 0.), torus->radius1, torus->radius2, surface) != SM_SUCCESS || !surface) {
				error = "Failed to create toroidal surface";
				return nullptr;
			}
		}
		SmAxis2Placement placement;
		smlib_placement_from_matrix(frame, placement);
		if (SmApiTransform(surface, placement) != SM_SUCCESS) {
			delete surface;
			error = "Failed to place the surface";
			return nullptr;
		}
		return surface;
	}

	/// Creates the surface of a face from its control net. Knot vectors that are
	/// not clamped are only supported by the canonical constructor, as SMLib
	/// reads out of bounds on those otherwise, which happens for the periodic
	/// surfaces of free form breps.
	SmBSplineSurface* create_nurbs_surface(const taxonomy::bspline_surface::ptr& bspline) {
		smlib_ensure_context();
		if (!bspline || bspline->knots[0].empty() || bspline->knots[1].empty()) {
			return nullptr;
		}
		const size_t num_u = bspline->control_points.size();
		const size_t num_v = num_u ? bspline->control_points.front().size() : 0;
		if (!num_u || !num_v || bspline->multiplicities[0].size() != bspline->knots[0].size() ||
			bspline->multiplicities[1].size() != bspline->knots[1].size()) {
			return nullptr;
		}
		for (const auto& row : bspline->control_points) {
			if (row.size() != num_v) {
				return nullptr;
			}
		}
		const auto knots_are_consistent = [](const std::vector<int>& multiplicities, size_t control_points, int degree) {
			size_t total = 0;
			for (const int m : multiplicities) {
				total += std::max(1, m);
			}
			return total == control_points + (size_t)degree + 1;
		};
		if (!knots_are_consistent(bspline->multiplicities[0], num_u, bspline->degree[0]) ||
			!knots_are_consistent(bspline->multiplicities[1], num_v, bspline->degree[1])) {
			return nullptr;
		}

		SmTArray<SmPoint3d> control_points;
		SmTArray<double> weights;
		const bool rational = bspline->weights.has_value();
		if (rational && (bspline->weights->size() != num_u || bspline->weights->front().size() != num_v)) {
			return nullptr;
		}
		for (size_t i = 0; i < num_u; ++i) {
			for (size_t j = 0; j < num_v; ++j) {
				const Eigen::Vector3d p = bspline->control_points[i][j]->ccomponents();
				control_points.Add(SmPoint3d(p(0), p(1), p(2)));
				if (rational) {
					weights.Add((*bspline->weights)[i][j]);
				}
			}
		}
		SmTArray<ULONG> u_multiplicities, v_multiplicities;
		for (const int m : bspline->multiplicities[0]) {
			u_multiplicities.Add((ULONG)std::max(1, m));
		}
		for (const int m : bspline->multiplicities[1]) {
			v_multiplicities.Add((ULONG)std::max(1, m));
		}
		SmTArray<double> u_knots, v_knots;
		for (const double k : bspline->knots[0]) {
			u_knots.Add(k);
		}
		for (const double k : bspline->knots[1]) {
			v_knots.Add(k);
		}

		SmBSplineSurface* surface = nullptr;
		if (SmBSplineSurface::CreateCanonical(
				*SmApiGetOrCreateContext(),
				(ULONG)bspline->degree[0],
				(ULONG)bspline->degree[1],
				control_points,
				SM_SF_UNSPECIFIED,
				u_multiplicities,
				v_multiplicities,
				u_knots,
				v_knots,
				SM_KT_UNSPECIFIED,
				rational ? &weights : nullptr,
				nullptr,
				surface) != SM_SUCCESS ||
			!surface) {
			return nullptr;
		}
		return surface;
	}

	/// Creates the sheet of a face on a plane by trimming a patch of that plane
	/// with the boundary of the face.
	SmBrep* trim_plane_with(
		const taxonomy::face::ptr& face,
		const taxonomy::plane::ptr& plane,
		const std::vector<SmCurve*>& curves,
		const std::vector<ULONG>& loop_sizes,
		double precision,
		std::string& error) {
		smlib_ensure_context();
		std::vector<Eigen::Vector3d> points;
		bool has_closed_edge = false;
		if (!face_points(face, precision, points, has_closed_edge, error) || points.empty()) {
			return nullptr;
		}
		const Eigen::Matrix4d frame = plane->matrix->ccomponents();
		const Eigen::Matrix4d inverse = frame.inverse();
		Eigen::Vector2d min(0., 0.), max(0., 0.);
		bool first = true;
		for (const auto& p : points) {
			const Eigen::Vector4d local = inverse * Eigen::Vector4d(p(0), p(1), p(2), 1.);
			const Eigen::Vector2d uv(local(0), local(1));
			min = first ? uv : min.cwiseMin(uv);
			max = first ? uv : max.cwiseMax(uv);
			first = false;
		}
		// The patch is larger than the face so that trimming cannot run out of it.
		const double margin = std::max(precision, 0.05 * (max - min).norm());
		SmPlane* surface = nullptr;
		if (SmApiCreatePlane(
				SmVector3d(min(0) - margin, min(1) - margin, 0.), (max(0) - min(0)) + 2. * margin, (max(1) - min(1)) + 2. * margin, surface) !=
				SM_SUCCESS ||
			!surface) {
			error = "Failed to create a plane to trim";
			return nullptr;
		}
		SmAxis2Placement placement;
		smlib_placement_from_matrix(frame, placement);
		if (SmApiTransform(surface, placement) != SM_SUCCESS) {
			delete surface;
			error = "Failed to place the plane of the face";
			return nullptr;
		}

		SmTArray<ULONG> loops;
		for (auto loop_size : loop_sizes) {
			loops.Add(loop_size);
		}
		SmTArray<SmCurve*> arr;
		for (auto* c : curves) {
			arr.Add(c);
		}
		SmBrep* brep = nullptr;
		if (SmApiTrimSurfaceWith3dCurves(surface, loops, arr, brep) != SM_SUCCESS || !brep) {
			error = "Failed to trim the plane of the face";
			return nullptr;
		}
		return brep;
	}

	SmBrep* create_face_brep(const taxonomy::face::ptr& face, double precision, std::string& error);

	/// The point an edge starts at when it is traversed within its loop.
	taxonomy::point3::ptr start_point_of(const taxonomy::edge::ptr& edge) {
		const auto& value = edge->orientation.value_or(true) ? edge->start : edge->end;
		if (value.index() == 1) {
			return std::get<taxonomy::point3::ptr>(value);
		}
		return nullptr;
	}

	/// Splits a loop where it visits one of its points more than once. A
	/// tessellated model expresses a slit in a face that way, and SMLib turns
	/// the enclosed sliver into a face of its own, which invalidates the shell
	/// the face belongs to.
	void split_loop_at_repeats(const taxonomy::loop::ptr& loop, std::vector<taxonomy::loop::ptr>& parts) {
		std::vector<taxonomy::edge::ptr> path;
		std::vector<taxonomy::point3::ptr> visited;
		for (const auto& edge : loop->children) {
			auto point = start_point_of(edge);
			if (point) {
				auto end_point = edge->orientation.value_or(true) ? edge->end : edge->start;
				if (end_point.index() == 1 && std::get<taxonomy::point3::ptr>(end_point) == point) {
					// A closed edge returns to the point it started at by itself,
					// so it does not make the loop visit that point twice.
					point = nullptr;
				}
			}
			if (point) {
					const auto found = std::find(visited.begin(), visited.end(), point);
					if (found != visited.end()) {
					const size_t index = (size_t)(found - visited.begin());
					auto part = taxonomy::make<taxonomy::loop>();
					part->instance = loop->instance;
					part->external = loop->external;
					part->children.assign(path.begin() + index, path.end());
					parts.push_back(part);
					path.resize(index);
					visited.resize(index);
				}
			}
			path.push_back(edge);
			if (point) {
				visited.push_back(point);
			}
		}
		if (parts.empty()) {
			return;
		}
		auto part = taxonomy::make<taxonomy::loop>();
		part->instance = loop->instance;
		part->external = loop->external;
		part->children = path;
		parts.push_back(part);
	}

	/// Creates the boundary representations of a single face. A face of which
	/// the outer boundary walks through a point twice is split into one face
	/// per lobe it delineates.
	bool create_face_breps(const taxonomy::face::ptr& face, double precision, std::string& error, std::vector<SmBrep*>& breps) {
		std::vector<taxonomy::loop::ptr> lobes;
		if (!face->children.empty()) {
			split_loop_at_repeats(face->children.front(), lobes);
		}
		if (lobes.size() < 2) {
			SmBrep* brep = create_face_brep(face, precision, error);
			if (!brep) {
				return false;
			}
			breps.push_back(brep);
			return true;
		}
		for (const auto& lobe : lobes) {
			auto split_face = taxonomy::make<taxonomy::face>();
			split_face->instance = face->instance;
			split_face->matrix = face->matrix;
			split_face->basis = face->basis;
			split_face->surface_style = face->surface_style;
			split_face->children.push_back(lobe);
			for (size_t i = 1; i < face->children.size(); ++i) {
				split_face->children.push_back(face->children[i]);
			}
			SmBrep* brep = create_face_brep(split_face, precision, error);
			if (!brep) {
				for (auto* b : breps) {
					delete b;
				}
				breps.clear();
				return false;
			}
			breps.push_back(brep);
		}
		return true;
	}

	/// Combines boundary representations by inserting their topology as it is,
	/// which keeps the faces with inner loops intact. Merging them as a boolean
	/// splits them along the surfaces of the other faces instead.
	SmBrep* combine_breps(std::vector<SmBrep*>& breps, std::string& error) {
		SmBrep* combined = nullptr;
		if (SmApiBrepCopy(breps.front(), combined) != SM_SUCCESS || !combined) {
			error = "Failed to copy a face of the shell";
			return nullptr;
		}
		for (size_t i = 1; i < breps.size(); ++i) {
			if (combined->MergeBrep(*breps[i]) != SM_SUCCESS) {
				delete combined;
				error = "Failed to combine the faces of the shell";
				return nullptr;
			}
		}
		for (auto* b : breps) {
			delete b;
		}
		breps.clear();
		combined->StitchAndOrient();
		return combined;
	}

	/// Creates a boundary representation for a single face.
	SmBrep* create_face_brep(const taxonomy::face::ptr& face, double precision, std::string& error) {
		std::vector<SmCurve*> curves;
		std::vector<ULONG> loop_sizes;
		for (const auto& loop : face->children) {
			const size_t before = curves.size();
			if (!create_loop_curves(loop, precision, curves, error)) {
				delete_curves(curves);
				return nullptr;
			}
			loop_sizes.push_back((ULONG)(curves.size() - before));
		}
		if (curves.empty()) {
			error = "Face without boundary";
			return nullptr;
		}

		auto surface = face_surface(face);
		SmSurface* analytic = nullptr;
		if (!surface && face->basis && face->basis->kind() == taxonomy::CYLINDER) {
			SmBrep* sheet = create_cylinder_sheet(face, taxonomy::cast<taxonomy::cylinder>(face->basis), precision, error);
			if (sheet) {
				delete_curves(curves);
				return sheet;
			}
		}
		if (!surface && face->basis && face->basis->kind() == taxonomy::TORUS) {
			Eigen::Vector3d min, max;
			if (face_extent(face, precision, min, max, error)) {
				analytic = create_revolution_surface(face->basis, min, max, precision, error);
			}
		}
		if (surface || analytic) {
			SmSurface* s = surface ? create_nurbs_surface(surface) : analytic;
			if (!s) {
				delete_curves(curves);
				error = "Failed to create surface";
				return nullptr;
			}
			// A face that follows the edges of the parameter domain of its
			// surface covers that entire domain, which is what SMLib creates
			// without trimming it.
			SmBrep* brep = nullptr;
			if (domain_face_of(face, s, precision, true, brep, error)) {
				delete_curves(curves);
				return brep;
			}
			const SmExtent2d domain = s->GetNaturalUVDomain();
			Eigen::Vector3d min, max;
			const double size = face_extent(face, precision, min, max, error) ? (max - min).norm() : 0.;
			const std::string domain_error = error;
			if (surface_wraps(s, domain, std::max(precision, 1.e-6 * size))) {
				// SMLib corrupts its data structures when trimming a surface
				// that wraps around its parameter domain. A face with a single
				// loop covers such a surface entirely, which is what the
				// boundary of a bore or a tube expresses.
				bool closed_boundary = false;
				std::vector<Eigen::Vector3d> boundary_points;
				face_points(face, precision, boundary_points, closed_boundary, error);
				if (face->children.size() == 1 && closed_boundary && domain_face_of(face, s, precision, false, brep, error)) {
					delete_curves(curves);
					return brep;
				}
				delete s;
				delete_curves(curves);
				error = "Cannot trim a surface that wraps around its axis (" + domain_error + ")";
				return nullptr;
			}
			SmTArray<ULONG> loops;
			for (auto loop_size : loop_sizes) {
				loops.Add(loop_size);
			}
			SmTArray<SmCurve*> arr;
			for (auto* c : curves) {
				arr.Add(c);
			}
			const SmApiStatus status = SmApiTrimSurfaceWith3dCurves(s, loops, arr, brep);
			if (status != SM_SUCCESS || !brep) {
				error = "Failed to trim surface";
				return nullptr;
			}
			curves.clear();
			return brep;
		}

		SmTArray<SmCurve*> arr;
		for (auto* c : curves) {
			arr.Add(c);
		}
		SmBrep* brep = nullptr;
		const SmApiStatus status = SmApiCreatePlanarFaces(arr, brep);
		if (status != SM_SUCCESS || !brep) {
			// SMLib builds faces from coplanar curves of which the end points
			// meet exactly, which is not always the case for free form curves.
			// The plane the face lies on is trimmed with them instead.
			if (face->basis && face->basis->kind() == taxonomy::PLANE) {
				SmBrep* sheet = trim_plane_with(face, taxonomy::cast<taxonomy::plane>(face->basis), curves, loop_sizes, precision, error);
				if (sheet) {
					curves.clear();
					return sheet;
				}
			}
			delete_curves(curves);
			error = "Failed to create planar face";
			return nullptr;
		}
		// The curves are consumed on success.
		curves.clear();
		return brep;
	}

	/// Merges the faces of a shell into a single boundary representation and
	/// stitches them into a solid when they form a closed volume.
	SmBrep* create_shell_brep(const taxonomy::shell::ptr& shell, double precision, std::string& error) {
		std::vector<SmBrep*> created;
		for (const auto& face : shell->children) {
			if (!create_face_breps(face, precision, error, created)) {
				for (auto* b : created) {
					delete b;
				}
				return nullptr;
			}
		}
		if (created.empty()) {
			error = "Shell without faces";
			return nullptr;
		}
		if (created.size() == 1) {
			return created.front();
		}
		SmBrep* merged = combine_breps(created, error);
		if (!merged) {
			return nullptr;
		}
		SmBoolean produces_solid = FALSE;
		ULONG stitched_edges = 0;
		double max_vertex_gap = 0., max_edge_gap = 0.;
		SmApiStitchIntoSolid(merged, produces_solid, stitched_edges, max_vertex_gap, max_edge_gap);
		return merged;
	}

	/// The profile of a swept solid. A profile that is mapped to a loop is
	/// upgraded to a face, the way the taxonomy conversion does, but a profile
	/// that is not a planar face is reported as unsupported instead of throwing.
	taxonomy::face::ptr profile_face(const taxonomy::item::ptr& item) {
		if (!item) {
			return nullptr;
		}
		if (item->kind() != taxonomy::FACE && item->kind() != taxonomy::LOOP) {
			return nullptr;
		}
		return taxonomy::cast<taxonomy::face>(item);
	}

	/// A half space is mapped to a solid with a single face that has no
	/// boundary, which cannot be subtracted from anything. Such an operand is
	/// replaced by a box that covers the operands it is applied to.
	struct halfspace {
		taxonomy::plane::ptr plane;
		/// The material of the half space is on the negative side of the plane's
		/// normal unless the face points that way.
		bool negative_side = true;
		/// The loop a polygonal bounded half space is restricted to, and the
		/// frame its coordinates are given in.
		taxonomy::loop::ptr boundary;
		taxonomy::matrix4::ptr boundary_frame;
	};

	std::optional<halfspace> halfspace_of(const taxonomy::item::ptr& item) {
		const auto solid = taxonomy::dcast<taxonomy::solid>(item);
		if (!solid || solid->children.size() != 1) {
			return std::nullopt;
		}
		const auto& shell = solid->children.front();
		if (!shell || shell->children.size() != 1) {
			return std::nullopt;
		}
		const auto& face = shell->children.front();
		if (!face) {
			return std::nullopt;
		}
		const auto plane = taxonomy::dcast<taxonomy::plane>(face->basis);
		if (!plane) {
			return std::nullopt;
		}
		halfspace result{plane, !face->orientation.value_or(false), nullptr, nullptr};
		if (!face->children.empty()) {
			// The boundary loop of a polygonal bounded half space is the only
			// child of the face that stands in for it.
			if (face->children.size() != 1 || !solid->instance.declaration().is("IfcHalfSpaceSolid")) {
				return std::nullopt;
			}
			result.boundary = taxonomy::dcast<taxonomy::loop>(face->children.front());
			result.boundary_frame = face->matrix;
		}
		return result;
	}

	/// Creates the box that stands in for a half space when a boolean is
	/// applied to the shapes in `breps`. The box lies on the half space's side
	/// of its boundary plane and is large enough to cover the shapes.
	SmBrep* halfspace_box(const taxonomy::plane::ptr& plane, bool negative_side, const std::vector<SmBrep*>& breps, double precision) {
		const Eigen::Matrix4d frame = plane->matrix ? plane->matrix->ccomponents() : Eigen::Matrix4d::Identity();
		const Eigen::Matrix3d axes = frame.block<3, 3>(0, 0);
		const Eigen::Vector3d origin = frame.block<3, 1>(0, 3);

		double umin = std::numeric_limits<double>::max(), umax = -umin;
		double vmin = umin, vmax = -umin;
		double wmax = -umin;
		bool any = false;
		for (auto* brep : breps) {
			SmVector3d min, max;
			if (SmApiBrepBoundingBox(brep, TRUE, min, max) != SM_SUCCESS) {
				continue;
			}
			for (int i = 0; i < 8; ++i) {
				const Eigen::Vector3d corner(
					i & 1 ? max.x : min.x,
					i & 2 ? max.y : min.y,
					i & 4 ? max.z : min.z);
				const Eigen::Vector3d local = axes.transpose() * (corner - origin);
				umin = std::min(umin, local(0));
				umax = std::max(umax, local(0));
				vmin = std::min(vmin, local(1));
				vmax = std::max(vmax, local(1));
				wmax = std::max(wmax, negative_side ? -local(2) : local(2));
			}
			any = true;
		}
		if (!any) {
			return nullptr;
		}
		// A half space that does not reach the shapes leaves them unchanged.
		if (wmax <= precision) {
			return nullptr;
		}
		// The box reaches slightly past the shapes so that it is not tangent to
		// them, and its far side is far enough away to contain all of them.
		const double margin = std::max(precision, 0.05 * std::max(umax - umin, vmax - vmin));
		const double height = wmax + margin;

		SmBrep* box = nullptr;
		const double z0 = negative_side ? -height : 0.;
		if (SmApiCreateBox(SmVector3d(0., 0., z0), umax - umin + 2. * margin, vmax - vmin + 2. * margin, height, box) != SM_SUCCESS || !box) {
			return nullptr;
		}
		Eigen::Matrix4d placement = Eigen::Matrix4d::Identity();
		placement.block<3, 3>(0, 0) = axes;
		placement.block<3, 1>(0, 3) = origin + axes * Eigen::Vector3d(umin - margin, vmin - margin, 0.);
		SmAxis2Placement axis2placement;
		smlib_placement_from_matrix(placement, axis2placement);
		if (SmApiTransform(box, axis2placement) != SM_SUCCESS) {
			delete box;
			return nullptr;
		}
		return box;
	}

	/// Creates the prism a polygonal bounded half space is restricted to, by
	/// extruding its boundary loop along the axis of the frame the boundary is
	/// given in, far enough to cover the shapes in `breps`.
	SmBrep* halfspace_prism(const halfspace& half_space, const std::vector<SmBrep*>& breps, double precision) {
		if (!half_space.boundary) {
			return nullptr;
		}
		const Eigen::Matrix4d frame = half_space.boundary_frame ? half_space.boundary_frame->ccomponents() : Eigen::Matrix4d::Identity();
		const Eigen::Matrix3d axes = frame.block<3, 3>(0, 0);
		const Eigen::Vector3d origin = frame.block<3, 1>(0, 3);
		const Eigen::Vector3d axis = axes.col(2);

		double zmin = std::numeric_limits<double>::max(), zmax = -zmin;
		bool any = false;
		for (auto* brep : breps) {
			SmVector3d min, max;
			if (SmApiBrepBoundingBox(brep, TRUE, min, max) != SM_SUCCESS) {
				continue;
			}
			for (int i = 0; i < 8; ++i) {
				const Eigen::Vector3d corner(
					i & 1 ? max.x : min.x,
					i & 2 ? max.y : min.y,
					i & 4 ? max.z : min.z);
				const double z = axis.dot(corner - origin);
				zmin = std::min(zmin, z);
				zmax = std::max(zmax, z);
			}
			any = true;
		}
		if (!any) {
			return nullptr;
		}
		const double margin = std::max(precision, 0.05 * (zmax - zmin));

		std::vector<SmCurve*> curves;
		std::string error;
		if (!create_loop_curves(half_space.boundary, precision, curves, error) || curves.empty()) {
			delete_curves(curves);
			return nullptr;
		}
		SmTArray<SmCurve*> array;
		for (auto* curve : curves) {
			array.Add(curve);
		}
		// The sweeping of the loop consumes the curves.
		SmBrep* prism = nullptr;
		if (SmApiCreateLinearSweep(array, SmVector3d(0., 0., 1.), zmax - zmin + 2. * margin, TRUE, prism) != SM_SUCCESS || !prism) {
			delete_curves(curves);
			return nullptr;
		}
		Eigen::Matrix4d placement = frame;
		placement.block<3, 1>(0, 3) = origin + axis * (zmin - margin);
		SmAxis2Placement axis2placement;
		smlib_placement_from_matrix(placement, axis2placement);
		if (SmApiTransform(prism, axis2placement) != SM_SUCCESS) {
			delete prism;
			return nullptr;
		}
		return prism;
	}

	/// Creates the shape that stands in for a half space: a box on the side of
	/// its boundary plane, restricted to the prism of a polygonal bounded half
	/// space when it has one.
	SmBrep* halfspace_solid(const halfspace& half_space, const std::vector<SmBrep*>& breps, double precision) {
		SmBrep* box = halfspace_box(half_space.plane, half_space.negative_side, breps, precision);
		if (!box || !half_space.boundary) {
			return box;
		}
		SmBrep* prism = halfspace_prism(half_space, breps, precision);
		if (!prism) {
			return box;
		}
		SmBrep* result = nullptr;
		if (SmApiBooleanIntersection(prism, box, result) != SM_SUCCESS || !result) {
			delete prism;
			delete box;
			return nullptr;
		}
		return result;
	}

} // namespace

bool smlib_kernel::convert_impl(const taxonomy::extrusion::ptr extrusion, std::vector<ifcopenshell::geom::conversion_result>& results) {
	if (!extrusion || !extrusion->direction) {
		return false;
	}
	const double depth = extrusion->depth;
	if (depth < settings_.get<settings::Precision>().get()) {
		logger_.error("GEO", 89, "Non-positive extrusion height encountered for:", extrusion->instance);
		return false;
	}
	auto face = profile_face(extrusion->basis);
	if (!face || face_surface(face)) {
		// Extrusions with free form profiles are not supported.
		return false;
	}
	smlib_ensure_context();

	std::vector<SmCurve*> curves;
	std::string error;
	for (const auto& loop : face->children) {
		if (!create_loop_curves(loop, settings_.get<settings::Precision>().get(), curves, error)) {
			delete_curves(curves);
			logger_.warning("SMLib kernel: failed to convert extrusion: " + error, extrusion->instance);
			return false;
		}
	}
	if (curves.empty()) {
		return false;
	}

	Eigen::Vector3d direction = extrusion->direction->ccomponents();
	if (direction.norm() < 1.e-12) {
		delete_curves(curves);
		return false;
	}
	direction.normalize();

	SmTArray<SmCurve*> arr;
	for (auto* c : curves) {
		arr.Add(c);
	}

	SmBrep* brep = nullptr;
	const SmApiStatus status = SmApiCreateLinearSweep(arr, SmVector3d(direction(0), direction(1), direction(2)), depth, TRUE, brep);
	if (status != SM_SUCCESS || !brep) {
		delete_curves(curves);
		logger_.warning("SMLib kernel: failed to sweep extrusion profile", extrusion->instance);
		return false;
	}

	results.emplace_back(ifcopenshell::geom::conversion_result(
		extrusion->instance.id(),
		extrusion->matrix,
		new ifcopenshell::geom::smlib_shape(brep),
		extrusion->surface_style));
	return true;
}

bool smlib_kernel::convert_impl(const taxonomy::revolve::ptr revolve, std::vector<ifcopenshell::geom::conversion_result>& results) {
	if (!revolve || !revolve->axis_origin || !revolve->direction) {
		return false;
	}
	auto face = profile_face(revolve->basis);
	if (!face || face_surface(face)) {
		return false;
	}
	smlib_ensure_context();

	std::vector<SmCurve*> curves;
	std::string error;
	for (const auto& loop : face->children) {
		if (!create_loop_curves(loop, settings_.get<settings::Precision>().get(), curves, error)) {
			delete_curves(curves);
			logger_.warning("SMLib kernel: failed to convert revolution: " + error, revolve->instance);
			return false;
		}
	}
	if (curves.empty()) {
		return false;
	}

	const Eigen::Vector3d axis = revolve->direction->ccomponents();
	if (axis.norm() < 1.e-12) {
		delete_curves(curves);
		return false;
	}
	const Eigen::Vector3d origin = revolve->axis_origin->ccomponents();
	const double angle_deg = revolve->angle.value_or(TAU) / PI * 180.;
	const bool capped = std::abs(std::abs(angle_deg) - 360.) > 1.e-6;

	SmTArray<SmCurve*> arr;
	for (auto* c : curves) {
		arr.Add(c);
	}

	SmBrep* brep = nullptr;
	const SmApiStatus status = SmApiCreateRotationalSweep(
		arr,
		to_point(origin),
		SmVector3d(axis(0), axis(1), axis(2)),
		angle_deg,
		capped ? TRUE : FALSE,
		brep);
	if (status != SM_SUCCESS || !brep) {
		delete_curves(curves);
		logger_.warning("SMLib kernel: failed to revolve profile", revolve->instance);
		return false;
	}

	results.emplace_back(ifcopenshell::geom::conversion_result(
		revolve->instance.id(),
		revolve->matrix,
		new ifcopenshell::geom::smlib_shape(brep),
		revolve->surface_style));
	return true;
}

bool smlib_kernel::convert_impl(const taxonomy::face::ptr face, std::vector<ifcopenshell::geom::conversion_result>& results) {
	if (!face) {
		return false;
	}
	smlib_ensure_context();
	std::string error;
	std::vector<SmBrep*> breps;
	if (!create_face_breps(face, settings_.get<settings::Precision>().get(), error, breps)) {
		logger_.warning("SMLib kernel: failed to convert face: " + error, face->instance);
		return false;
	}
	SmBrep* brep = breps.size() == 1 ? breps.front() : combine_breps(breps, error);
	if (!brep) {
		logger_.warning("SMLib kernel: failed to convert face: " + error, face->instance);
		return false;
	}
	auto shape = new ifcopenshell::geom::smlib_shape(brep);
	shape->set_solid(false);
	results.emplace_back(ifcopenshell::geom::conversion_result(
		face->instance.id(),
		face->matrix,
		shape,
		face->surface_style));
	return true;
}

bool smlib_kernel::convert_impl(const taxonomy::shell::ptr shell, std::vector<ifcopenshell::geom::conversion_result>& results) {
	if (!shell) {
		return false;
	}
	smlib_ensure_context();
	std::string error;
	SmBrep* brep = create_shell_brep(shell, settings_.get<settings::Precision>().get(), error);
	if (!brep) {
		logger_.warning("SMLib kernel: failed to convert shell: " + error, shell->instance);
		return false;
	}
	auto shape = new ifcopenshell::geom::smlib_shape(brep);
	shape->set_solid(shell->closed.value_or(false));
	results.emplace_back(ifcopenshell::geom::conversion_result(
		shell->instance.id(),
		shell->matrix,
		shape,
		shell->surface_style));
	return true;
}

bool smlib_kernel::convert_impl(const taxonomy::solid::ptr solid, std::vector<ifcopenshell::geom::conversion_result>& results) {
	if (!solid || solid->children.empty()) {
		return false;
	}
	smlib_ensure_context();

	std::string error;
	SmBrep* result = nullptr;
	std::vector<SmBrep*> outer;
	for (size_t i = 0; i < solid->children.size(); ++i) {
		SmBrep* brep = create_shell_brep(solid->children[i], settings_.get<settings::Precision>().get(), error);
		if (!brep) {
			logger_.warning("SMLib kernel: failed to convert solid shell: " + error, solid->children[i]->instance);
			delete result;
			for (auto* b : outer) {
				delete b;
			}
			return false;
		}
		if (i == 0) {
			result = brep;
		} else {
			// Subsequent shells are voids; they are subtracted from the outer
			// shell, as SMLib has no explicit shell topology.
			SmBrep* next = smlib_brep_boolean(result, brep, SM_BO_DIFFERENCE);
			delete brep;
			delete result;
			if (!next) {
				logger_.warning("SMLib kernel: failed to subtract inner shell", solid->children[i]->instance);
				return false;
			}
			result = next;
		}
		outer.push_back(nullptr);
	}

	auto shape = new ifcopenshell::geom::smlib_shape(result);
	shape->set_solid(true);
	results.emplace_back(ifcopenshell::geom::conversion_result(
		solid->instance.id(),
		solid->matrix,
		shape,
		solid->surface_style));
	return true;
}

bool smlib_kernel::convert_impl(const taxonomy::boolean_result::ptr br, std::vector<ifcopenshell::geom::conversion_result>& results) {
	if (!br || br->children.empty()) {
		return false;
	}
	smlib_ensure_context();

	long operation = SM_BO_UNION;
	switch (br->operation) {
	case taxonomy::boolean_result::UNION:
		operation = SM_BO_UNION;
		break;
	case taxonomy::boolean_result::SUBTRACTION:
		operation = SM_BO_DIFFERENCE;
		break;
	case taxonomy::boolean_result::INTERSECTION:
		operation = SM_BO_INTERSECTION;
		break;
	}

	std::vector<SmBrep*> operands;
	std::vector<SmBrep*> owned;
	taxonomy::style::ptr style;
	// A half space operand is remembered with its position so that its stand in
	// box is inserted where it was listed, keeping the order of the operands.
	std::vector<std::pair<size_t, halfspace>> halfspaces;
	for (size_t i = 0; i < br->children.size(); ++i) {
		const auto& child = br->children[i];
		if (auto halfspace = halfspace_of(child)) {
			halfspaces.emplace_back(operands.size(), *halfspace);
			continue;
		}
		std::vector<ifcopenshell::geom::conversion_result> converted;
		if (!abstract_kernel::convert(child, converted) || converted.empty()) {
			logger_.warning("SMLib kernel: failed to convert boolean operand", child->instance);
			for (auto* b : owned) {
				delete b;
			}
			return false;
		}
		for (const auto& result : converted) {
			auto* shape = dynamic_cast<ifcopenshell::geom::smlib_shape*>(result.shape().get());
			if (!shape || !shape->brep()) {
				logger_.warning("SMLib kernel: boolean operand is not a SMLib shape", child->instance);
				for (auto* b : owned) {
					delete b;
				}
				return false;
			}
			SmBrep* brep = nullptr;
			if (SmApiBrepCopy(shape->brep(), brep) != SM_SUCCESS || !brep) {
				for (auto* b : owned) {
					delete b;
				}
				return false;
			}
			if (result.placement() && !result.placement()->is_identity()) {
				SmAxis2Placement placement;
				smlib_placement_from_matrix(result.placement()->ccomponents(), placement);
				SmApiTransform(brep, placement);
			}
			owned.push_back(brep);
			operands.push_back(brep);
			if (!style) {
				style = result.hasStyle() ? result.style_ptr() : child->surface_style;
			}
		}
	}

	if (operands.empty()) {
		logger_.warning("SMLib kernel: not enough boolean operands", br->instance);
		for (auto* b : owned) {
			delete b;
		}
		return false;
	}
	for (const auto& halfspace : halfspaces) {
		SmBrep* box = halfspace_solid(halfspace.second, operands, settings_.get<settings::Precision>().get());
		if (!box) {
			// The half space does not reach the operands, so it leaves them
			// unchanged.
			continue;
		}
		owned.push_back(box);
		operands.insert(operands.begin() + std::min(halfspace.first, operands.size()), box);
	}

	if (operands.size() < 2) {
		// A single operand that was not cut by anything is the result itself.
		results.emplace_back(ifcopenshell::geom::conversion_result(
			br->instance.id(),
			br->matrix,
			new ifcopenshell::geom::smlib_shape(operands.front()),
			br->surface_style ? br->surface_style : style));
		return true;
	}

	SmTArray<SmBrep*> breps;
	// SmApiMergeBreps folds the operation in last-to-first order, so the
	// operands are passed in reverse to obtain a left to right evaluation.
	for (auto it = operands.rbegin(); it != operands.rend(); ++it) {
		breps.Add(*it);
	}
	SmBrep* result = nullptr;
	const SmApiStatus status = SmApiMergeBreps(breps, (SmBooleanOperationType)operation, result);
	if (status != SM_SUCCESS || !result) {
		logger_.warning("SMLib kernel: boolean operation failed", br->instance);
		// The operands are consumed once the merge has accepted them, also when
		// it fails afterwards, so they are not deleted here.
		return false;
	}

	results.emplace_back(ifcopenshell::geom::conversion_result(
		br->instance.id(),
		br->matrix,
		new ifcopenshell::geom::smlib_shape(result),
		br->surface_style ? br->surface_style : style));
	return true;
}

bool smlib_kernel::convert_openings(const express::base& entity, const std::vector<std::pair<taxonomy::ptr, taxonomy::matrix4>>& openings, const std::vector<ifcopenshell::geom::conversion_result>& entity_shapes, const taxonomy::matrix4& entity_trsf, std::vector<ifcopenshell::geom::conversion_result>& cut_shapes) {
    smlib_ensure_context();

    std::vector<SmBrep*> opening_breps;
    std::vector<express::base> opening_instances;
    const auto cleanup = [&opening_breps]() {
        for (auto* b : opening_breps) {
            delete b;
        }
        opening_breps.clear();
    };

    for (const auto& opening : openings) {
        const Eigen::Matrix4d relative = entity_trsf.ccomponents().inverse() * opening.second.ccomponents();
        std::vector<ifcopenshell::geom::conversion_result> converted;
        if (!abstract_kernel::convert(opening.first, converted) || converted.empty()) {
            logger_.error("SMLib kernel: failed to convert opening operand", opening.first->instance);
            cleanup();
            return false;
        }
        for (const auto& result : converted) {
            auto* shape = dynamic_cast<ifcopenshell::geom::smlib_shape*>(result.shape().get());
            if (!shape || !shape->brep()) {
                logger_.error("SMLib kernel: opening is not a SMLib shape", opening.first->instance);
                cleanup();
                return false;
            }
            SmBrep* brep = nullptr;
            const SmApiStatus copy_status = SmApiBrepCopy(shape->brep(), brep);
            if (copy_status != SM_SUCCESS || !brep) {
                logger_.error("SMLib kernel: opening copy failed, status " + std::to_string(copy_status), opening.first->instance);
                cleanup();
                return false;
            }
            const Eigen::Matrix4d m = relative * (result.placement() ? result.placement()->ccomponents() : Eigen::Matrix4d::Identity());
            SmAxis2Placement placement;
            smlib_placement_from_matrix(m, placement);
            const SmApiStatus transform_status = SmApiTransform(brep, placement);
            if (transform_status != SM_SUCCESS) {
                logger_.error("SMLib kernel: opening transform failed, status " + std::to_string(transform_status), opening.first->instance);
                delete brep;
                cleanup();
                return false;
            }
            opening_breps.push_back(brep);
            opening_instances.push_back(opening.first->instance);
        }
    }

    if (opening_breps.empty()) {
        logger_.error("SMLib kernel: no opening operands converted", entity);
        return false;
    }

    bool success = true;
    for (const auto& entity_shape : entity_shapes) {
        auto* shape = dynamic_cast<ifcopenshell::geom::smlib_shape*>(entity_shape.shape().get());
        if (!shape || !shape->brep()) {
            logger_.error("GEO", 187, "Null operand", entity);
            success = false;
            continue;
        }
        // The openings are subtracted one by one: a single merge of all the
        // operands at once makes the kernel fail on walls with many openings.
        SmBrep* current = nullptr;
        const SmApiStatus copy_status = SmApiBrepCopy(shape->brep(), current);
        if (copy_status != SM_SUCCESS || !current) {
            logger_.error("SMLib kernel: host copy failed, status " + std::to_string(copy_status), entity);
            success = false;
            break;
        }
        // The openings are expressed relative to the product, so the shape is
        // moved into that frame, which is also what the result is placed in.
        if (entity_shape.placement() && !entity_shape.placement()->is_identity()) {
            SmAxis2Placement placement;
            smlib_placement_from_matrix(entity_shape.placement()->ccomponents(), placement);
            const SmApiStatus transform_status = SmApiTransform(current, placement);
            if (transform_status != SM_SUCCESS) {
                logger_.error("SMLib kernel: host transform failed, status " + std::to_string(transform_status), entity);
                delete current;
                success = false;
                break;
            }
        }
        size_t failed = 0;
        size_t completed = 0;
        size_t limit = opening_breps.size();
        for (size_t i = 0; i < limit; ++i) {
            auto* b = opening_breps[i];
            SmBrep* operand = nullptr;
            const SmApiStatus operand_status = SmApiBrepCopy(b, operand);
            if (operand_status != SM_SUCCESS || !operand) {
                logger_.error("SMLib kernel: opening copy failed, status " + std::to_string(operand_status), opening_instances[i]);
                ++failed;
                break;
            }
            // Failed SMLib booleans may modify both operands. Keep the previous
            // result intact rather than returning a damaged partial shape.
            SmBrep* trial = nullptr;
            const SmApiStatus trial_status = SmApiBrepCopy(current, trial);
            if (trial_status != SM_SUCCESS || !trial) {
                logger_.error("SMLib kernel: host copy for opening " + std::to_string(i + 1) + " failed, status " + std::to_string(trial_status), entity);
                delete operand;
                ++failed;
                break;
            }
            SmBrep* next = nullptr;
            const SmApiStatus status = SmApiBooleanDifference(trial, operand, next);
            if (status != SM_SUCCESS || !next) {
                logger_.error("SMLib kernel: subtraction of opening operand " + std::to_string(i + 1) + "/" + std::to_string(limit) + " failed, status " + std::to_string(status) + "; previous shape retained, remaining operands not attempted", opening_instances[i]);
                delete trial;
                delete operand;
                ++failed;
                break;
            }
            logger_.message(ifcopenshell::logger::LOG_DEBUG, "SMLib kernel: subtracted opening operand " + std::to_string(i + 1) + "/" + std::to_string(limit) + ", faces " + std::to_string(current->GetNumFaces()) + " -> " + std::to_string(next->GetNumFaces()), opening_instances[i]);
            delete current;
            current = next;
            ++completed;
        }
        if (failed) {
            logger_.error("SMLib kernel: " + std::to_string(completed) + "/" + std::to_string(limit) + " opening operands completed; " + std::to_string(limit - completed) + " unapplied, previous cut shape retained", entity);
            success = false;
        }
        cut_shapes.emplace_back(ifcopenshell::geom::conversion_result(
            entity_shape.ItemId(),
            new ifcopenshell::geom::smlib_shape(current),
            entity_shape.style_ptr()));
    }

    cleanup();
    return success;
}
