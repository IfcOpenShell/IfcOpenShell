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

#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

static taxonomy::point3::ptr mk_point(const Eigen::Vector3d& p) {
    return taxonomy::make<taxonomy::point3>(p);
}

static taxonomy::circle::ptr mk_circle(const Eigen::Vector3d& C,
                                       const Eigen::Vector3d& Z,
                                       const Eigen::Vector3d& X,
                                       double R) {
    auto c = taxonomy::make<taxonomy::circle>();
    c->radius = R;
    c->matrix = taxonomy::make<taxonomy::matrix4>(C, Z, X); // u=0 aligned with X
    return c;
}

static taxonomy::line::ptr mk_line(const Eigen::Vector3d& A, const Eigen::Vector3d& B) {
    auto l = taxonomy::make<taxonomy::line>();
    l->matrix = taxonomy::make<taxonomy::matrix4>(A, (B - A)); // direction inferred in matrix ctor
    return l;
}

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcRightCircularCylinder* inst) {
    const double pi2 = 2.0 * boost::math::constants::pi<double>();

    auto O = Eigen::Vector3d::Zero();
    auto X = Eigen::Vector3d::UnitX();
    auto Y = Eigen::Vector3d::UnitY();
    auto Z = Eigen::Vector3d::UnitZ();

    auto R = inst->Radius() * length_unit_;
    auto H = inst->Height() * length_unit_;

    // Seam vertices at u=0 (and u=2pi, coincident) on bottom/top
    const Eigen::Vector3d P0 = O + X * R;         // (u=0, v=0)
    const Eigen::Vector3d P1 = O + Z * H + X * R; // (u=0, v=H)

    auto cyl = taxonomy::make<taxonomy::cylinder>();
    cyl->radius = R;
    cyl->matrix = taxonomy::make<taxonomy::matrix4>(O, Z, X);

    auto pl_bot = taxonomy::make<taxonomy::plane>();
    pl_bot->matrix = taxonomy::make<taxonomy::matrix4>(O, -Z, X); // outward normal

    auto pl_top = taxonomy::make<taxonomy::plane>();
    pl_top->matrix = taxonomy::make<taxonomy::matrix4>(O + Z * H, Z, X); // outward normal

    // Boundary 3D curves
    auto c_bot = mk_circle(O, Z, X, R);
    auto c_top = mk_circle(O + Z * H, Z, X, R);
    auto seam = mk_line(P0, P1); // coincident seam geometry for u=0 and u=2π

    auto v00 = mk_point(P0);
    auto v01 = mk_point(P1);

    // Edges
    auto e_bot = taxonomy::make<taxonomy::edge>();
    e_bot->basis = c_bot;
    e_bot->start = v00; // closed circle: start=end = seam vertex
    e_bot->end = v00;
    e_bot->curve_sense = true; // forward umin->umax

    auto e_top = taxonomy::make<taxonomy::edge>();
    e_top->basis = c_top;
    e_top->start = v01;
    e_top->end = v01;
    e_top->curve_sense = false; // reversed umax->umin

    auto e_seam_u0 = taxonomy::make<taxonomy::edge>();
    e_seam_u0->basis = seam;
    e_seam_u0->start = v00;
    e_seam_u0->end = v01;

    // Duplicate seam edge for periodic closure (u=2π). Same 3D geometry, distinct topological edge.
    auto e_seam_u2pi = taxonomy::make<taxonomy::edge>();
    e_seam_u2pi->basis = seam;
    e_seam_u2pi->start = v01;
    e_seam_u2pi->end = v00;

    // Lateral loop (order matches the conceptual rectangle in (u,v))
    auto loop_lat = taxonomy::make<taxonomy::loop>();
    loop_lat->external = true;
    loop_lat->closed = true;
    loop_lat->children = {e_bot, e_seam_u0, e_top, e_seam_u2pi};

    auto face_lat = taxonomy::make<taxonomy::face>();
    face_lat->basis = cyl;
    face_lat->children = {loop_lat};

    // Bottom cap
    auto loop_bot = taxonomy::make<taxonomy::loop>();
    loop_bot->external = true;
    loop_bot->closed = true;
    loop_bot->children = {e_bot};

    auto face_bot = taxonomy::make<taxonomy::face>();
    face_bot->basis = pl_bot;
    face_bot->children = {loop_bot};

    // Top cap
    auto loop_top = taxonomy::make<taxonomy::loop>();
    loop_top->external = true;
    loop_top->closed = true;
    loop_top->children = {e_top};

    auto face_top = taxonomy::make<taxonomy::face>();
    face_top->basis = pl_top;
    face_top->children = {loop_top};

    // Shell + solid
    auto sh = taxonomy::make<taxonomy::shell>();
    sh->closed = true;
    sh->children = {face_lat, face_bot, face_top};

    auto so = taxonomy::make<taxonomy::solid>();
    so->children = {sh};
    return so;
}
