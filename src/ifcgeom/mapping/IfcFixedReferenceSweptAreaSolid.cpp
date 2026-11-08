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

#include "../function_item_evaluator.h"
#include "../infra_sweep_helper.h"
#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geom;

#ifdef SCHEMA_HAS_IfcFixedReferenceSweptAreaSolid

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcFixedReferenceSweptAreaSolid& inst) {
    auto dir = map(inst.Directrix());
    auto ref = taxonomy::cast<taxonomy::direction3>(map(inst.FixedReference()));
    auto profile = taxonomy::cast<taxonomy::face>(map(inst.SweptArea()));

    auto loft = taxonomy::make<taxonomy::loft>();
    // @todo intialize as default
    loft->axis = nullptr;
    // Check if this instance has alignment elements
    // @todo currently only the case is handled where directrix returns a piecewise_function
    if (auto fn = std::dynamic_pointer_cast<taxonomy::function_item>(dir)) {
        function_item_evaluator evaluator(settings_, fn);

        bool is_directrix_derived = false;
#ifdef SCHEMA_HAS_IfcDirectrixDerivedReferenceSweptAreaSolid
        if (inst.as<IfcSchema::IfcDirectrixDerivedReferenceSweptAreaSolid>()) {
            is_directrix_derived = true;
        }
#endif

        // the profile placed at dist_along
        const auto place = [&](double dist_along) -> taxonomy::face::ptr {
            auto m4 = evaluator.evaluate(dist_along);
            Eigen::Matrix4d m4b = Eigen::Matrix4d::Identity();
            auto pos = m4.col(3).head<3>();
            if (is_directrix_derived) {
                m4b.col(0).head<3>() = m4.col(1).head<3>();
                m4b.col(1).head<3>() = m4.col(0).head<3>().cross(m4.col(1).head<3>());
                m4b.col(2).head<3>() = m4.col(0).head<3>();
                m4b.col(3).head<3>() = pos;
            } else {
                Eigen::Vector3d tangent = m4.col(0).head<3>().normalized();
                Eigen::Vector3d proj = (ref->components() - tangent * tangent.dot(ref->components()));
                proj.normalize();
                auto binormal = proj.cross(tangent);
                m4b.col(0).head<3>() = proj;
                m4b.col(1).head<3>() = binormal;
                m4b.col(2).head<3>() = tangent;
                m4b.col(3).head<3>() = pos;
            }
            // @todo taxonomy::clone() does not actually clone. That's really confusing.
            auto section = taxonomy::face::ptr(profile->clone_());
            section->matrix = taxonomy::make<taxonomy::matrix4>();
            if (profile->matrix) {
                section->matrix->components() = (m4b * profile->matrix->ccomponents()).eval();
            } else {
                section->matrix->components() = m4b;
            }
            return section;
        };

        // sections at every span boundary of the directrix, and between them as needed for the
        // profile to follow it within the deflection settings (see deflection_samples)
        const auto samples = deflection_samples(
            evaluator.boundaries(),
            [&](double u) {
                return sampled_section{evaluator.evaluate(u).col(3).head<3>(), section_points(place(u))};
            },
            settings_.get<ifcopenshell::geom::settings::MesherLinearDeflection>().get(),
            settings_.get<ifcopenshell::geom::settings::MesherAngularDeflection>().get(),
            settings_.get<ifcopenshell::geom::settings::Precision>().get());
        for (double dist_along : samples) {
            loft->children.push_back(place(dist_along));
        }
    } else {
        taxonomy::matrix4::ptr matrix;
        if (inst.Position()) {
            matrix = taxonomy::cast<taxonomy::matrix4>(map(inst.Position()));
        }
        // TODO: Implement handling for non-alignment curves using sweep_along_curve
        auto sweep = taxonomy::make<taxonomy::sweep_along_curve>(
            matrix,  // matrix4::ptr - no transformation needed
            profile, // face::ptr - the profile to sweep
            dir,     // item::ptr curve - the directrix curve
            ref);

        return sweep;
    }

    return loft;
}

#endif
