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

#include "IfcGeomRepresentation.h"

IfcGeom::Representation::Serialization::Serialization(const BRep& brep)
	: Representation(brep.settings(), brep.entity(), brep.id())
{
	for (auto it = brep.begin(); it != brep.end(); ++it) {
		int sid = -1;

		if (it->hasStyle()) {
            const auto& clr = it->Style().get_color().ccomponents();
			surface_styles_.push_back(clr(0));
			surface_styles_.push_back(clr(1));
			surface_styles_.push_back(clr(2));

			sid = it->Style().instance ? it->Style().instance->as<IfcUtil::IfcBaseEntity>()->id() : -1;
		} else {
			surface_styles_.push_back(-1.);
			surface_styles_.push_back(-1.);
			surface_styles_.push_back(-1.);
		}

		if (it->hasStyle() && it->Style().has_transparency()) {
			surface_styles_.push_back(1. - it->Style().transparency);
		} else {
			surface_styles_.push_back(1.);
		}

		surface_style_ids_.push_back(sid);
	}

	ifcopenshell::geometry::taxonomy::matrix4 identity;
	auto* comp = brep.as_compound();
	comp->Serialize(identity, brep_data_);
	delete comp;
}

IfcGeom::ConversionResultShape* IfcGeom::Representation::BRep::as_compound(bool force_meters) const {
	ConversionResultShape* accum = nullptr;

	for (auto it = begin(); it != end(); ++it) {
		double unit_scale = 1.0;
		if (!force_meters && settings().get<ifcopenshell::geometry::settings::ConvertBackUnits>().get()) {
			unit_scale = 1.0 / settings().get<ifcopenshell::geometry::settings::LengthUnit>().get();
		}
		auto s = it->apply_transform(unit_scale);
		if (accum) {
			auto n = accum->concat(s);
			delete s;
			delete accum;
			accum = n;
		} else {
			accum = s->wrap_in_compound();
		}
	}

	return accum;
}

bool IfcGeom::Representation::BRep::calculate_surface_area(double& area) const {
	std::unique_ptr<ConversionResultShape> s(as_compound());
	if (!s) {
		area = 0.;
		return false;
	}
	area = s->area()->to_double();
	return true;
}

bool IfcGeom::Representation::BRep::calculate_volume(double& volume) const {
	std::unique_ptr<ConversionResultShape> s(as_compound());
	if (!s) {
		volume = 0.;
		return false;
	}
	volume = s->area()->to_double();
	return true;
}

bool IfcGeom::Representation::BRep::calculate_projected_surface_area(const ifcopenshell::geometry::taxonomy::matrix4::ptr& place, double& along_x, double& along_y, double& along_z) const {
	along_x = along_y = along_z = 0.;

	for (IfcGeom::ConversionResults::const_iterator it = begin(); it != end(); ++it) {
		double x, y, z;
		it->Shape()->surface_area_along_direction(settings().get<ifcopenshell::geometry::settings::MesherLinearDeflection>().get(), place, x, y, z);

		if (it->Shape()->is_manifold()) {
			x /= 2.;
			y /= 2.;
			z /= 2.;
		}

		along_x += x;
		along_y += y;
		along_z += z;
	}

	return true;
}

IfcGeom::Representation::Triangulation::Triangulation(const BRep& shape_model)
	: Representation(shape_model.settings(), shape_model.entity(), shape_model.id())
	, weld_offset_(0)
{
	for (IfcGeom::ConversionResults::const_iterator iit = shape_model.begin(); iit != shape_model.end(); ++iit) {
		
		// Don't weld vertices that belong to different items to prevent non-manifold situations.
		resetWelds();

		int surface_style_id = -1;
		if (iit->hasStyle()) {
			auto jt = std::find(materials_.begin(), materials_.end(), iit->StylePtr());
			if (jt == materials_.end()) {
				surface_style_id = (int)materials_.size();
				materials_.push_back(iit->StylePtr());
			} else {
				surface_style_id = (int)(jt - materials_.begin());
			}
		}

		if (settings().get<ifcopenshell::geometry::settings::ApplyDefaultMaterials>().get() && surface_style_id == -1) {
			const auto& material = IfcGeom::get_default_style(shape_model.entity());
			auto mit = std::find(materials_.begin(), materials_.end(), material);
			if (mit == materials_.end()) {
				surface_style_id = (int)materials_.size();
				materials_.push_back(material);
			} else {
				surface_style_id = (int)(mit - materials_.begin());
			}
		}

		iit->Shape()->Triangulate(settings(), *iit->Placement(), this, iit->ItemId(), surface_style_id);
	}
}

/// Generates UVs for a single mesh using box projection.
/// @todo Very simple impl. Assumes that input vertices and normals match 1:1.

std::vector<double> IfcGeom::Representation::Triangulation::box_project_uvs(const std::vector<double>& vertices, const std::vector<double>& normals)
{
	std::vector<double> uvs;
	uvs.resize(vertices.size() / 3 * 2);
	for (size_t uv_idx = 0, v_idx = 0;
		uv_idx < uvs.size() && v_idx < vertices.size() && v_idx < normals.size();
		uv_idx += 2, v_idx += 3) {

		double n_x = normals[v_idx], n_y = normals[v_idx + 1], n_z = normals[v_idx + 2];
		double v_x = vertices[v_idx], v_y = vertices[v_idx + 1], v_z = vertices[v_idx + 2];

		if (std::abs(n_x) > std::abs(n_y) && std::abs(n_x) > std::abs(n_z)) {
			uvs[uv_idx] = v_z;
			uvs[uv_idx + 1] = v_y;
		}
		if (std::abs(n_y) > std::abs(n_x) && std::abs(n_y) > std::abs(n_z)) {
			uvs[uv_idx] = v_x;
			uvs[uv_idx + 1] = v_z;
		}
		if (std::abs(n_z) > std::abs(n_x) && std::abs(n_z) > std::abs(n_y)) {
			uvs[uv_idx] = v_x;
			uvs[uv_idx + 1] = v_y;
		}
	}

	return uvs;
}

int IfcGeom::Representation::Triangulation::addVertex(int item_id, int material_index, double pX, double pY, double pZ) {
	const bool convert = settings().get<ifcopenshell::geometry::settings::ConvertBackUnits>().get();
	auto unit_magnitude = settings().get<ifcopenshell::geometry::settings::LengthUnit>().get();
	const double X = convert ? (pX /unit_magnitude) : pX;
	const double Y = convert ? (pY /unit_magnitude) : pY;
	const double Z = convert ? (pZ /unit_magnitude) : pZ;
	int i = (int)verts_.size() / 3;
	if (settings().get<ifcopenshell::geometry::settings::WeldVertices>().get()) {
		const VertexKey key = std::make_tuple(item_id, material_index, X, Y, Z);
		typename VertexKeyMap::const_iterator it = welds.find(key);
		if (it != welds.end()) {
			// Return index for previously encountered point
			return it->second;
		}
		i = (int)(welds.size() + weld_offset_);
		welds[key] = i;
	}
	verts_.push_back(X);
	verts_.push_back(Y);
	verts_.push_back(Z);
	return i;
}

void IfcGeom::Representation::Triangulation::registerEdgeCount(int n1, int n2, std::map<std::pair<int, int>, int>& edgecount) {
	const Edge e = Edge((std::min)(n1, n2), (std::max)(n1, n2));
	edgecount[e] ++;
}

const IfcGeom::ConversionResultShape* IfcGeom::Representation::BRep::item(int i) const {
	if (i >= 0 && i < shapes_.size()) {
		return shapes_[i].Shape()->moved(shapes_[i].Placement());
	} else {
		return nullptr;
	}
}

int IfcGeom::Representation::BRep::item_id(int i) const {
	if (i >= 0 && i < shapes_.size()) {
		return shapes_[i].ItemId();
	} else {
		return 0;
	}
}
