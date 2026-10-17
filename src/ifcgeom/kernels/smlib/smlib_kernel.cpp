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

#include "../../../ifcgeom/taxonomy.h"
#include "smlib_utils.h"

#include <algorithm>
#include <cmath>
#include <limits>
#include <map>
#include <memory>
#include <set>
#include <SmApiBrep.h>
#include <SmApiCurves.h>
#include <SmApiGeneral.h>
#include <SmApiPrimitives.h>
#include <SmApiQueries.h>
#include <SmAxis2Placement.h>
#include <SmBrep.h>
#include <SmBrepData.h>
#include <SmBSplineCurve.h>
#include <SmBSplineSurface.h>
#include <SmCircle.h>
#include <SmContext.h>
#include <SmCurve.h>
#include <SmCurveClass.h>
#include <SmCylinder.h>
#include <SmEdge.h>
#include <SmEllipse.h>
#include <SmFace.h>
#include <SmLine.h>
#include <SmPlane.h>
#include <SmPointClass.h>
#include <SmRegion.h>
#include <SmSphere.h>
#include <SmSurface.h>
#include <SmTorus.h>
#include <SmVector3d.h>
#include <SmVertex.h>
#include <string>
#include <tuple>
#include <vector>

using namespace ifcopenshell::geom;
using namespace ifcopenshell::geom::kernels;

// Generated with the assistance of an AI coding tool.

namespace {
constexpr double PI = 3.14159265358979323846;
constexpr double TAU = 2. * PI;

SmPoint3d to_point(const Eigen::Vector3d& v) { return SmPoint3d(v.x(), v.y(), v.z()); }
Eigen::Vector3d to_eigen(const SmPoint3d& p) { return Eigen::Vector3d(p.x, p.y, p.z); }

using curve_owner = std::unique_ptr<SmCurve>;
using surface_owner = std::unique_ptr<SmSurface>;
using brep_owner = std::unique_ptr<SmBrep>;

bool checked(SmStatus status, const char* operation, std::string& error) {
    if (status == SM_SUCCESS) {
        return true;
    }
    error = std::string(operation) + " failed, status " + std::to_string(status);
    return false;
}

SmAxis2Placement frame_of(const taxonomy::geom_item::ptr& item) {
    SmAxis2Placement frame;
    if (item && item->matrix) {
        smlib_placement_from_matrix(item->matrix->ccomponents(), frame);
    }
    return frame;
}

SmBSplineCurve* create_nurbs_curve(
    const std::vector<Eigen::Vector3d>& control_points,
    const std::vector<double>& weights,
    const std::vector<double>& knots,
    const std::vector<int>& multiplicities,
    int degree) {
    smlib_ensure_context();
    if (degree < 1 || knots.empty() || knots.size() != multiplicities.size() || control_points.size() < (size_t)degree + 1 ||
        (!weights.empty() && weights.size() != control_points.size()) || !std::is_sorted(knots.begin(), knots.end())) {
        return nullptr;
    }
    size_t total = 0;
    for (const int m : multiplicities) {
        if (m <= 0 || m > degree + 1) {
            return nullptr;
        }
        total += m;
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
        knot_multiplicities.Add((ULONG)m);
    }
    SmTArray<double> unique_knots;
    for (const double k : knots) {
        unique_knots.Add(k);
    }

    SmBSplineCurve* result = nullptr;
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
        if (degree < 1 || control_points < (size_t)degree + 1) {
            return false;
        }
        size_t total = 0;
        for (const int m : multiplicities) {
            if (m <= 0 || m > degree + 1) {
                return false;
            }
            total += m;
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
    if (rational && (bspline->weights->size() != num_u || std::any_of(bspline->weights->begin(), bspline->weights->end(), [num_v](const auto& row) { return row.size() != num_v; }))) {
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
        u_multiplicities.Add((ULONG)m);
    }
    for (const int m : bspline->multiplicities[1]) {
        v_multiplicities.Add((ULONG)m);
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

struct native_edge {
    taxonomy::edge::ptr source;
    curve_owner curve;
    SmExtent1d interval;
    bool forward = true;

    curve_owner profile_curve(std::string& error) const {
        SmCurve* copy = nullptr;
        if (!checked(curve->Copy(*SmApiGetOrCreateContext(), copy), "Copy curve", error)) {
            return {};
        }
        curve_owner result(copy);
        SmExtent1d bounds = interval;
        if (!checked(result->Trim(bounds), "Trim profile curve", error)) {
            return {};
        }
        if (!forward) {
            SmExtent1d reversed;
            if (!checked(result->ReverseParameterization(bounds, reversed), "Reverse profile curve", error)) {
                return {};
            }
        }
        return result;
    }
};

using trim_value = decltype(taxonomy::edge::start);

bool curve_parameter(SmCurve* curve, const trim_value& trim, double fallback, bool conic, double precision, double& parameter, std::string& error) {
    parameter = fallback;
    if (trim.index() == 0) {
        return true;
    }
    if (trim.index() == 2) {
        parameter = std::get<double>(trim);
        if (!std::isfinite(parameter)) {
            error = "Non-finite curve parameter";
            return false;
        }
        return true;
    }
    SmPoint3d closest;
    double distance;
    const auto point = std::get<taxonomy::point3::ptr>(trim);
    if (!point || !checked(SmApiCurveClosestPoint(curve, to_point(point->ccomponents()), closest, parameter, distance), "Curve closest point", error)) {
        return false;
    }
    if (!std::isfinite(distance) || distance > precision) {
        error = "Cartesian trim is outside curve tolerance";
        return false;
    }
    if (conic) {
        double degrees;
        if (!checked(curve->ConvertTFromNURBSToSTEP(parameter, degrees), "Convert conic parameter", error)) {
            return false;
        }
        parameter = degrees * PI / 180.;
    }
    return true;
}

bool convert_edge(const taxonomy::edge::ptr& source, double precision, native_edge& result, std::string& error) {
    if (!source) {
        error = "Missing edge";
        return false;
    }
    result.source = source;
    auto basis = source->basis;
    auto start = source->start, end = source->end;
    bool sense = source->curve_sense.value_or(true);
    std::set<const taxonomy::item*> visited;
    while (basis && basis->kind() == taxonomy::EDGE) {
        if (!visited.insert(basis.get()).second) {
            error = "Cyclic curve basis";
            return false;
        }
        const auto inner = taxonomy::cast<taxonomy::edge>(basis);
        if (start.index() == 0 && end.index() == 0) {
            start = inner->start;
            end = inner->end;
            sense = sense == inner->curve_sense.value_or(true);
        }
        basis = inner->basis;
    }
    result.forward = source->orientation.value_or(true);
    if (!basis || basis->kind() == taxonomy::LINE) {
        SmLine* line = nullptr;
        if (start.index() == 1 && end.index() == 1) {
            const auto a = std::get<taxonomy::point3::ptr>(start), b = std::get<taxonomy::point3::ptr>(end);
            if (!a || !b || (a->ccomponents() - b->ccomponents()).norm() <= precision) {
                error = "Degenerate line edge";
                return false;
            }
            if (!checked(SmApiCreateLineSegment(to_point(a->ccomponents()), to_point(b->ccomponents()), line), "Create line segment", error)) {
                return false;
            }
        } else if (basis && start.index() == 2 && end.index() == 2) {
            const auto ln = taxonomy::cast<taxonomy::line>(basis);
            const auto& m = ln->matrix->ccomponents();
            // IFC line parameters use the taxonomy line's direction and scale.
            const Eigen::Vector3d a = m.block<3, 1>(0, 3) + std::get<double>(start) * m.block<3, 1>(0, 2);
            const Eigen::Vector3d b = m.block<3, 1>(0, 3) + std::get<double>(end) * m.block<3, 1>(0, 2);
            if ((b - a).norm() <= precision) {
                error = "Degenerate line edge";
                return false;
            }
            if (!checked(SmApiCreateLineSegment(to_point(a), to_point(b), line), "Create line segment", error)) {
                return false;
            }
        } else {
            error = "Line edge requires finite matching trims";
            return false;
        }
        result.curve.reset(line);
        result.interval = line->GetNaturalInterval();
        return true;
    }

    const bool conic = basis->kind() == taxonomy::CIRCLE || basis->kind() == taxonomy::ELLIPSE;
    if (conic) {
        const auto frame = frame_of(taxonomy::cast<taxonomy::geom_item>(basis));
        if (basis->kind() == taxonomy::CIRCLE) {
            SmCircle* circle = nullptr;
            if (!checked(SmCircle::CreateCanonical(*SmApiGetOrCreateContext(), frame, taxonomy::cast<taxonomy::circle>(basis)->radius, circle), "Create circle", error)) {
                return false;
            }
            result.curve.reset(circle);
        } else {
            const auto ellipse = taxonomy::cast<taxonomy::ellipse>(basis);
            SmEllipse* curve = nullptr;
            if (!checked(SmEllipse::CreateCanonical(*SmApiGetOrCreateContext(), frame, ellipse->radius, ellipse->radius2, curve), "Create ellipse", error)) {
                return false;
            }
            result.curve.reset(curve);
        }
    } else if (basis->kind() == taxonomy::BSPLINE_CURVE) {
        const auto spline = taxonomy::cast<taxonomy::bspline_curve>(basis);
        std::vector<Eigen::Vector3d> points;
        for (const auto& point : spline->control_points) {
            points.push_back(point->ccomponents());
        }
        result.curve.reset(create_nurbs_curve(points, spline->weights.value_or(std::vector<double>()), spline->knots, spline->multiplicities, spline->degree));
        if (!result.curve) {
            error = "Failed to create B-spline curve";
            return false;
        }
    } else {
        error = "Unsupported curve type";
        return false;
    }

    // The edge interval follows increasing curve parameters. Its use in a loop
    // carries the traversal direction independently of the supporting curve.
    if (!sense) {
        std::swap(start, end);
    }
    result.forward = sense == source->orientation.value_or(true);
    const auto natural = result.curve->GetNaturalInterval();
    double from, to;
    if (!curve_parameter(result.curve.get(), start, conic ? 0. : natural.GetMin(), conic, precision, from, error) ||
        !curve_parameter(result.curve.get(), end, conic ? TAU : natural.GetMax(), conic, precision, to, error)) {
        return false;
    }
    if (conic) {
        double sweep = std::fmod(to - from, TAU);
        if (sweep < 0.) {
            sweep += TAU;
        }
        if (sweep == 0.) {
            sweep = TAU;
        }
        // Put the seam at the edge's first parameter, retaining a full exact
        // supporting conic. Only the topological interval bounds the edge.
        double degrees = std::fmod(from * 180. / PI, 360.);
        if (degrees > 0.) {
            degrees -= 360.;
        }
        auto analytic = static_cast<SmBSplineCurve*>(result.curve.get());
        SmTArray<SmExtent1d> intervals;
        if (!checked(analytic->AdjustSTEPInterval(SmExtent1d(degrees, degrees + 360.)), "Set conic seam", error) ||
            !checked(result.curve->ConvertIvlFromSTEPToNURBS(SmExtent1d(degrees, degrees + sweep * 180. / PI), intervals), "Convert conic interval", error)) {
            return false;
        }
        if (intervals.GetSize() != 1) {
            error = "Ambiguous conic interval";
            return false;
        }
        result.interval = intervals[0];
    } else {
        if (from > to) {
            std::swap(from, to);
            result.forward = !result.forward;
        }
        if (from < natural.GetMin() || to > natural.GetMax() || !(to > from)) {
            error = "Curve trim outside natural interval";
            return false;
        }
        result.interval = SmExtent1d(from, to);
    }
    return true;
}

bool append_edges(const taxonomy::edge::ptr& edge, double precision, std::vector<native_edge>& result, std::string& error, std::set<const taxonomy::item*>& active) {
    if (!edge || !active.insert(edge.get()).second) {
        error = "Missing or cyclic edge";
        return false;
    }
    auto basis = edge->basis;
    std::set<const taxonomy::item*> visited;
    while (basis && basis->kind() == taxonomy::EDGE) {
        if (!visited.insert(basis.get()).second) {
            error = "Cyclic curve basis";
            return false;
        }
        basis = taxonomy::cast<taxonomy::edge>(basis)->basis;
    }
    if (basis && basis->kind() == taxonomy::LOOP) {
        if (edge->start.index() != 0 || edge->end.index() != 0) {
            error = "Trimmed composite curves are not supported";
            return false;
        }
        const auto loop = taxonomy::cast<taxonomy::loop>(basis);
        const size_t first = result.size();
        for (const auto& segment : loop->children) {
            if (!append_edges(segment, precision, result, error, active)) {
                return false;
            }
        }
        if (edge->curve_sense.value_or(true) != edge->orientation.value_or(true)) {
            std::reverse(result.begin() + first, result.end());
            for (size_t i = first; i < result.size(); ++i) {
                result[i].forward = !result[i].forward;
            }
        }
    } else {
        native_edge converted;
        if (!convert_edge(edge, precision, converted, error)) {
            return false;
        }
        result.push_back(std::move(converted));
    }
    active.erase(edge.get());
    return true;
}

bool loop_edges(const taxonomy::loop::ptr& loop, double precision, std::vector<native_edge>& result, std::string& error) {
    if (!loop || loop->children.empty()) {
        error = "Empty face boundary";
        return false;
    }
    std::set<const taxonomy::item*> active;
    for (const auto& edge : loop->children) {
        if (!append_edges(edge, precision, result, error, active)) {
            return false;
        }
    }
    return true;
}

// Sweep APIs borrow their input curves, so these owners outlive each call.
bool profile_curves(const taxonomy::face::ptr& face, double precision, std::vector<curve_owner>& owners, SmTArray<SmCurve*>& curves, std::string& error) {
    for (const auto& loop : face->children) {
        std::vector<native_edge> edges;
        if (!loop_edges(loop, precision, edges, error)) {
            return false;
        }
        for (const auto& edge : edges) {
            auto curve = edge.profile_curve(error);
            if (!curve) {
                return false;
            }
            curves.Add(curve.get());
            owners.push_back(std::move(curve));
        }
    }
    return !owners.empty();
}

const taxonomy::bspline_surface::ptr face_surface(const taxonomy::face::ptr& face) {
    return face && face->basis && face->basis->kind() == taxonomy::BSPLINE_SURFACE ? taxonomy::cast<taxonomy::bspline_surface>(face->basis) : nullptr;
}

// The face domain is a conservative evaluation window, not its boundary.
// All IFC boundaries are installed below as explicit loops and edgeuses.
surface_owner face_geometry(const taxonomy::face::ptr& face, std::vector<std::vector<native_edge>>& loops, double precision, SmExtent2d& domain, std::string& error) {
    if (auto spline = face_surface(face)) {
        surface_owner result(create_nurbs_surface(spline));
        if (!result) {
            error = "Failed to create B-spline surface";
            return {};
        }
        domain = result->GetNaturalUVDomain();
        return result;
    }
    SmExtent3d box;
    box.Init();
    for (const auto& loop : loops) {
        for (const auto& edge : loop) {
            SmExtent3d bounds;
            if (!checked(edge.curve->CalculateBoundingBox(edge.interval, &bounds), "Curve bounding box", error)) {
                return {};
            }
            box.Union(bounds, box);
        }
    }
    const auto basis = face->basis;
    SmAxis2Placement frame = frame_of(taxonomy::dcast<taxonomy::geom_item>(basis));
    if (!basis) {
        std::vector<curve_owner> owners;
        SmTArray<SmCurve*> curves;
        for (const auto& edge : loops.front()) {
            auto curve = edge.profile_curve(error);
            if (!curve) {
                return {};
            }
            curves.Add(curve.get());
            owners.push_back(std::move(curve));
        }
        SmPoint3d origin;
        SmVector3d normal;
        if (!curves[0]->AreCoPlanar(curves, precision, &origin, &normal) ||
            !checked(SmCurve::ComputeCrvsNormal(curves, normal), "Boundary normal", error)) {
            error = "Cannot determine a planar face from its boundary";
            return {};
        }
        SmPlane plane(origin, normal, SmApiGetOrCreateContext());
        if (!checked(plane.GetCanonical(frame), "Plane frame", error)) {
            return {};
        }
    }
    const auto minimum = box.GetMin(), maximum = box.GetMax();
    SmExtent2d plane_domain;
    plane_domain.Init();
    double axial_min = std::numeric_limits<double>::infinity(), axial_max = -axial_min;
    const auto x = to_eigen(frame.GetXAxis()), y = to_eigen(frame.GetYAxis()), z = to_eigen(frame.GetZAxis());
    const auto origin = to_eigen(frame.GetOrigin());
    for (int i = 0; i < 8; ++i) {
        const Eigen::Vector3d p = Eigen::Vector3d(i & 1 ? maximum.x : minimum.x, i & 2 ? maximum.y : minimum.y, i & 4 ? maximum.z : minimum.z) - origin;
        plane_domain.AddPoint2d(SmPoint2d(x.dot(p), y.dot(p)));
        axial_min = std::min(axial_min, z.dot(p));
        axial_max = std::max(axial_max, z.dot(p));
    }
    if (!basis || basis->kind() == taxonomy::PLANE) {
        SmPlane* plane = nullptr;
        if (!checked(SmPlane::CreateCanonical(*SmApiGetOrCreateContext(), frame, plane), "Create plane", error)) {
            return {};
        }
        domain = plane_domain;
        return surface_owner(plane);
    }
    if (basis->kind() == taxonomy::CYLINDER) {
        // Build a supporting cylinder large enough for the boundary. No
        // angular/axial outline is inferred from samples of that boundary.
        const double margin = std::max(precision, 0.05 * (axial_max - axial_min));
        const auto bottom = to_point(origin + (axial_min - margin) * z);
        surface_owner result(new (*SmApiGetOrCreateContext()) SmCylinder(bottom, frame.GetXAxis(), frame.GetYAxis(), taxonomy::cast<taxonomy::cylinder>(basis)->radius, 0., 360., axial_max - axial_min + 2. * margin, FALSE, FALSE, FALSE));
        domain = result->GetNaturalUVDomain();
        return result;
    }
    if (basis->kind() == taxonomy::TORUS) {
        const auto torus = taxonomy::cast<taxonomy::torus>(basis);
        SmTorus* surface = nullptr;
        if (!checked(SmTorus::CreateCanonical(*SmApiGetOrCreateContext(), frame, torus->radius1, torus->radius2, surface), "Create torus", error)) {
            return {};
        }
        domain = surface->GetNaturalUVDomain();
        return surface_owner(surface);
    }
    if (basis->kind() == taxonomy::SPHERE) {
        SmSphere* surface = nullptr;
        if (!checked(SmSphere::CreateCanonical(*SmApiGetOrCreateContext(), frame, taxonomy::cast<taxonomy::sphere>(basis)->radius, surface), "Create sphere", error)) {
            return {};
        }
        domain = surface->GetNaturalUVDomain();
        return surface_owner(surface);
    }
    error = "Unsupported face surface";
    return {};
}

class topology_builder {
    SmBrepConstructor builder_;
    brep_owner brep_;
    double precision_;
    bool void_region_ = false;
    using edge_key = std::tuple<const taxonomy::item*, trim_value, trim_value, bool>;
    std::map<edge_key, SmEdge*> edges_;
    std::map<const taxonomy::point3*, SmVertex*> vertices_;

    SmVertex* vertex(const trim_value& value, std::string& error) {
        if (value.index() != 1) {
            return nullptr;
        }
        const auto source = std::get<taxonomy::point3::ptr>(value);
        if (!source) {
            error = "Missing edge vertex";
            return nullptr;
        }
        auto& result = vertices_[source.get()];
        if (!result) {
            result = builder_.StartVertexOfLoop(to_point(source->ccomponents()));
        }
        if (!result) {
            error = "Failed to create vertex";
        }
        return result;
    }

    bool add_face(const taxonomy::face::ptr& face, std::string& error) {
        if (!face || face->children.empty()) {
            error = "Face without boundary";
            return false;
        }
        auto boundaries = face->children;
        // IFC's set of bounds need not list IfcFaceOuterBound first.
        auto outer = std::find_if(boundaries.begin(), boundaries.end(), [](const taxonomy::loop::ptr& loop) { return loop && loop->external.value_or(false); });
        if (outer != boundaries.end()) {
            std::rotate(boundaries.begin(), outer, outer + 1);
        }
        std::vector<std::vector<native_edge>> loops(boundaries.size());
        for (size_t i = 0; i < boundaries.size(); ++i) {
            if (!loop_edges(boundaries[i], precision_, loops[i], error)) {
                return false;
            }
            // Reject gaps before EndLoop can identify adjacent vertexuses.
            for (size_t j = 0; j < loops[i].size(); ++j) {
                const auto& a = loops[i][j];
                const auto& b = loops[i][(j + 1) % loops[i].size()];
                SmPoint3d end, start;
                if (!checked(a.curve->EvaluatePoint(a.forward ? a.interval.GetMax() : a.interval.GetMin(), end), "Evaluate edge end", error) ||
                    !checked(b.curve->EvaluatePoint(b.forward ? b.interval.GetMin() : b.interval.GetMax(), start), "Evaluate edge start", error)) {
                    return false;
                }
                if (end.DistanceBetweenSquared(start) > precision_ * precision_) {
                    error = "Face boundary is not closed within tolerance";
                    return false;
                }
            }
        }
        SmExtent2d domain;
        auto surface = face_geometry(face, loops, precision_, domain, error);
        if (!surface) {
            return false;
        }
        bool forward = face->orientation.value_or(true);
        if (face->basis) {
            forward = forward == face->basis->orientation.value_or(true);
        }
        const auto loop_orientation = forward ? SM_OT_SAME : SM_OT_OPPOSITE;
        if (void_region_) {
            // For a void, the constructor's new region is the cavity. IFC's
            // material-facing orientation therefore belongs to the other side.
            forward = !forward;
        }
        if (!builder_.StartFace(forward ? SM_OT_SAME : SM_OT_OPPOSITE)) {
            error = "Failed to start face";
            return false;
        }
        if (!checked(builder_.SetFaceSurface(surface.get(), domain), "Set face surface", error)) {
            return false;
        }
        surface.release();
        for (auto& loop : loops) {
            if (!builder_.StartLoop(loop_orientation)) {
                error = "Failed to start loop";
                return false;
            }
            for (auto& definition : loop) {
                const auto& source = definition.source;
                const edge_key key(source->basis.get(), source->start, source->end, source->curve_sense.value_or(true));
                auto& existing = edges_[key];
                // Cached edges were installed with their curve's positive
                // parameter direction, independently of the first edgeuse.
                const auto orientation = definition.forward ? SM_OT_SAME : SM_OT_OPPOSITE;
                auto a = source->start, b = source->end;
                // StartEdge swaps these vertices for an opposite edgeuse;
                // supply them in increasing curve-parameter order.
                if (source->basis && !source->curve_sense.value_or(true)) {
                    std::swap(a, b);
                }
                SmVertex* start = existing ? nullptr : vertex(a, error);
                SmVertex* end = existing ? nullptr : vertex(b, error);
                if (!error.empty()) {
                    return false;
                }
                SmEdge* edge = builder_.StartEdge(orientation, existing, start, end);
                if (!edge) {
                    error = "Failed to start edge";
                    return false;
                }
                if (!existing) {
                    if (!checked(builder_.SetEdgeCurve(definition.curve.get(), FALSE), "Set edge curve", error)) {
                        return false;
                    }
                    definition.curve.release();
                    if (!checked(builder_.SetLimits(SmVertexNode(definition.interval.GetMin()), SmVertexNode(definition.interval.GetMax())), "Set edge interval", error)) {
                        return false;
                    }
                    existing = edge;
                }
                if (!checked(builder_.EndEdge(), "End edge", error)) {
                    return false;
                }
            }
            if (!checked(builder_.EndLoop(), "End loop", error)) {
                return false;
            }
        }
        return checked(builder_.EndFace(), "End face", error);
    }

  public:
    explicit topology_builder(double precision) : precision_(precision) {
        brep_.reset(builder_.StartBrep(*SmApiGetOrCreateContext()));
        if (brep_) {
            brep_->SetTolerance(precision, FALSE);
        }
    }

    SmRegion* start_region(SmRegion* outer) {
        void_region_ = outer != nullptr;
        auto region = builder_.StartRegion(TRUE, outer);
        if (region) {
            region->SetIsVoid(outer != nullptr);
        }
        return region;
    }
    bool end_region(std::string& error) { return checked(builder_.EndRegion(), "End region", error); }

    bool add_shell(const taxonomy::shell::ptr& shell, std::string& error) {
        if (!brep_ || !shell || shell->children.empty()) {
            error = "Empty shell";
            return false;
        }
        edges_.clear();
        vertices_.clear();
        SmShell* outer = nullptr;
        SmShell* inner = nullptr;
        if (!checked(builder_.StartShell(outer, inner), "Start shell", error)) {
            return false;
        }
        for (const auto& face : shell->children) {
            if (!add_face(face, error)) {
                return false;
            }
        }
        // Preserve shared IFC entities; stitch only remaining coincident
        // edges (e.g. polygonal face sets without explicit edge identities).
        return checked(builder_.EndShell(TRUE), "Stitch shell", error);
    }

    SmBrep* finish(bool solid, std::string& error) {
        if (!checked(builder_.EndBrep(), "End B-rep", error)) {
            return nullptr;
        }
        // Complete periodic topology using the kernel's seam operations.
        SmTArray<SmFace*> faces;
        brep_->GetFaces(faces);
        brep_->m_bEditingEnabled = TRUE;
        for (ULONG i = 0; i < faces.GetSize(); ++i) {
            SmCurveClassification u, v;
            SmSurfParamType crossed, missing, near;
            if (faces[i]->HasSeamProblem(u, v, crossed, missing, near) &&
                !checked(faces[i]->SplitAtSeam(u, v, crossed, missing, near), "Complete face seams", error)) {
                return nullptr;
            }
        }
        brep_->m_bEditingEnabled = FALSE;
        faces.ReSet();
        brep_->GetFaces(faces);
        for (ULONG i = 0; i < faces.GetSize(); ++i) {
            double mean_curve, max_curve, mean_vertex, max_vertex, mean_uv, max_uv;
            if (!checked(faces[i]->CreateUVTrimCurves(FALSE, nullptr, nullptr, mean_curve, max_curve, mean_vertex, max_vertex, mean_uv, max_uv), "Create face UV curves", error)) {
                return nullptr;
            }
            if (max_curve > precision_ || max_vertex > precision_) {
                error = "Face geometry exceeds modeling tolerance";
                return nullptr;
            }
        }
        if (!checked(brep_->ValidatePointers(), "Validate B-rep topology", error)) {
            return nullptr;
        }
        if (solid && !brep_->IsManifoldSolid()) {
            error = "Closed shell did not produce a manifold solid";
            return nullptr;
        }
        return brep_.release();
    }
};

SmBrep* create_shell_brep(const taxonomy::shell::ptr& shell, double precision, std::string& error) {
    topology_builder builder(precision);
    const bool solid = shell->closed.value_or(false);
    if (solid && !builder.start_region(nullptr)) {
        error = "Failed to start solid region";
        return nullptr;
    }
    if (!builder.add_shell(shell, error) || (solid && !builder.end_region(error))) {
        return nullptr;
    }
    return builder.finish(solid, error);
}

SmBrep* create_solid_brep(const taxonomy::solid::ptr& solid, double precision, std::string& error) {
    topology_builder builder(precision);
    SmRegion* material = nullptr;
    for (size_t i = 0; i < solid->children.size(); ++i) {
        SmRegion* region = builder.start_region(i ? material : nullptr);
        if (!region) {
            error = "Failed to start solid region";
            return nullptr;
        }
        if (!i) {
            material = region;
        }
        if (!builder.add_shell(solid->children[i], error) || !builder.end_region(error)) {
            return nullptr;
        }
    }
    return builder.finish(true, error);
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

    std::vector<curve_owner> owners;
    SmTArray<SmCurve*> array;
    std::string error;
    auto profile = taxonomy::make<taxonomy::face>();
    profile->children.push_back(half_space.boundary);
    if (!profile_curves(profile, precision, owners, array, error)) {
        return nullptr;
    }
    SmBrep* prism = nullptr;
    if (SmApiCreateLinearSweep(array, SmVector3d(0., 0., 1.), zmax - zmin + 2. * margin, TRUE, prism) != SM_SUCCESS || !prism) {
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

    std::vector<curve_owner> owners;
    SmTArray<SmCurve*> arr;
    std::string error;
    if (!profile_curves(face, settings_.get<settings::Precision>().get(), owners, arr, error)) {
        logger_.warning("SMLib kernel: failed to convert extrusion: " + error, extrusion->instance);
        return false;
    }

    Eigen::Vector3d direction = extrusion->direction->ccomponents();
    if (direction.norm() < 1.e-12) {
        return false;
    }
    direction.normalize();

    SmBrep* brep = nullptr;
    const SmApiStatus status = SmApiCreateLinearSweep(arr, SmVector3d(direction(0), direction(1), direction(2)), depth, TRUE, brep);
    if (status != SM_SUCCESS || !brep) {
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

    std::vector<curve_owner> owners;
    SmTArray<SmCurve*> arr;
    std::string error;
    if (!profile_curves(face, settings_.get<settings::Precision>().get(), owners, arr, error)) {
        logger_.warning("SMLib kernel: failed to convert revolution: " + error, revolve->instance);
        return false;
    }

    const Eigen::Vector3d axis = revolve->direction->ccomponents();
    if (axis.norm() < 1.e-12) {
        return false;
    }
    const Eigen::Vector3d origin = revolve->axis_origin->ccomponents();
    const double angle_deg = revolve->angle.value_or(TAU) / PI * 180.;
    const bool capped = std::abs(std::abs(angle_deg) - 360.) > 1.e-6;

    SmBrep* brep = nullptr;
    const SmApiStatus status = SmApiCreateRotationalSweep(
        arr,
        to_point(origin),
        SmVector3d(axis(0), axis(1), axis(2)),
        angle_deg,
        capped ? TRUE : FALSE,
        brep);
    if (status != SM_SUCCESS || !brep) {
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
    auto shell = taxonomy::make<taxonomy::shell>();
    shell->children.push_back(face);
    SmBrep* brep = create_shell_brep(shell, settings_.get<settings::Precision>().get(), error);
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
    SmBrep* result = create_solid_brep(solid, settings_.get<settings::Precision>().get(), error);
    if (!result) {
        logger_.warning("SMLib kernel: failed to convert solid: " + error, solid->instance);
        return false;
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
                if (SmApiTransform(brep, placement) != SM_SUCCESS) {
                    delete brep;
                    for (auto* b : owned) {
                        delete b;
                    }
                    logger_.warning("SMLib kernel: failed to transform boolean operand", child->instance);
                    return false;
                }
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
