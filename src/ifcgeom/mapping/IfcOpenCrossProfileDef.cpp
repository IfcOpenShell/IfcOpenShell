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

#include "../../ifcgeom/profile_helper.h"
#include "../../ifcgeom/infra_sweep_helper.h"

#include <boost/math/constants/constants.hpp>
const double PI = boost::math::constants::pi<double>();

#ifdef SCHEMA_HAS_IfcOpenCrossProfileDef


taxonomy::ptr mapping::map_impl(const IfcSchema::IfcOpenCrossProfileDef* inst) {
    if (inst->ProfileType() != IfcSchema::IfcProfileTypeEnum::IfcProfileType_CURVE) {
        logger_.Warning("GEO", 274, "Expected IfcOpenCrossProfileDef.ProfileType to be CURVE", inst);
        return nullptr;
    }

    std::vector<taxonomy::point3::ptr> points;
    taxonomy::point3::ptr start;
    if (inst->OffsetPoint()) {
       start = taxonomy::cast<taxonomy::point3>(map(inst->OffsetPoint()));
    } else {
        start = taxonomy::make<taxonomy::point3>(0., 0., 0.);
    }
    points.push_back(start);

    boost::optional<std::vector<std::string>> tags = inst->Tags();
    boost::optional<std::string> tag = boost::none;
    if (tags.has_value() && !tags.get().empty()) {
        tag = tags.get()[0];
    }

    auto widths = inst->Widths();
    auto angles = inst->Slopes(); // these are actually angles, but the attribute is called Slopes

	if (widths.size() != angles.size()) {
        logger_.Warning("GEO", 275, "Expected Widths and Slopes to be equal length, but got " + std::to_string(widths.size()) + " and " + std::to_string(angles.size()) + " respectively", inst);
        return nullptr;
    }

   auto horizontal_widths = inst->HorizontalWidths();

    double x = start->ccomponents().x();
    double y = start->ccomponents().y();
    double z = start->ccomponents().z();
    for (size_t i = 0; i < widths.size(); ++i) {
        double w = widths[i] * length_unit_;
        double a = PI - angles[i] * angle_unit_;
        double dx = (horizontal_widths ? w : w * std::cos(a));
        double dy = (horizontal_widths ? w * std::tan(a) : w * std::sin(a));
        double dz = 0.;
        x -= dx; // subtract because X is positive to the left
        y += dy;
        z += dz;

        if (tags.has_value() && !tags.get().empty()) {
            tag = tags.get()[i+1];
        }

        points.push_back(taxonomy::make<taxonomy::point3>(x, y, z));
    }

    auto mapped = polygon_from_points(points);
    mapped->closed = false;
    mapped->tags = tags;

    return mapped;
}

#endif
