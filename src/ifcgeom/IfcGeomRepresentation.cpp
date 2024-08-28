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

#ifdef IFOPSH_WITH_OPENCASCADE
#include "../ifcparse/IfcLogger.h"
#include "../ifcgeom/kernels/opencascade/OpenCascadeConversionResult.h"
#include "../ifcgeom/kernels/opencascade/base_utils.h"

#include <BRep_Tool.hxx>
#include <BRepTools.hxx>
#include <BRep_Builder.hxx>
#include <Geom_Plane.hxx>
#include <TopoDS_Compound.hxx>
#include <BRepGProp.hxx>
#include <GProp_GProps.hxx>
#include <TopoDS.hxx>

#include <BRepBuilderAPI_Transform.hxx>
#include <BRepBuilderAPI_GTransform.hxx>

TopoDS_Shape apply_transformation(const TopoDS_Shape& s, const gp_Trsf& t) {
	if (t.Form() == gp_Identity) {
		return s;
	} else {
		/// @todo set to 1. and exactly 1. or use epsilon?
		if (t.ScaleFactor() != 1.) {
			return BRepBuilderAPI_Transform(s, t, true);
		} else {
			return s.Moved(t);
		}
	}
}

TopoDS_Shape apply_transformation(const TopoDS_Shape& s, const gp_GTrsf& t) {
	if (t.Form() == gp_Other) {
		return BRepBuilderAPI_GTransform(s, t, true);
	} else {
		return apply_transformation(s, t.Trsf());
	}
}

namespace {
	void accumulate(const gp_Ax3& ax, const gp_Dir& normal, double area, double& along_x, double& along_y, double& along_z) {
		along_x += area * fabs(ax.XDirection().Dot(normal));
		along_y += area * fabs(ax.YDirection().Dot(normal));
		along_z += area * fabs(ax.Direction().Dot(normal));
	}

	void surface_area_along_direction(double tol, const TopoDS_Shape& s, const gp_Ax3& ax, double& along_x, double& along_y, double& along_z) {
		along_x = along_y = along_z = 0.;

		bool meshed = false;

		TopExp_Explorer exp(s, TopAbs_FACE);
		for (; exp.More(); exp.Next()) {
			const TopoDS_Face& face = TopoDS::Face(exp.Current());
			Handle(Geom_Surface) surf = BRep_Tool::Surface(face);
			Handle(Geom_Plane) plane = Handle(Geom_Plane)::DownCast(surf);

			if (surf->DynamicType() == STANDARD_TYPE(Geom_Plane)) {
				GProp_GProps prop_area;
				BRepGProp::SurfaceProperties(face, prop_area);
				const double area = prop_area.Mass();

				accumulate(ax, plane->Position().Direction(), area, along_x, along_y, along_z);
			} else {

				if (!meshed) {
					try {
						BRepMesh_IncrementalMesh(s, tol);
					} catch (...) {
						Logger::Message(Logger::LOG_ERROR, "Failed to triangulate shape");
						return;
					}
					meshed = true;
				}

				TopLoc_Location loc;
				Handle(Poly_Triangulation) tri = BRep_Tool::Triangulation(face, loc);
				if (!tri.IsNull()) {
					std::vector<gp_XYZ> coords;
					coords.reserve(tri->NbNodes());

					for (int i = 1; i <= tri->NbNodes(); ++i) {
						coords.push_back(tri->Node(i).Transformed(loc).XYZ());
					}

					const Poly_Array1OfTriangle& triangles = tri->Triangles();
					for (int i = 1; i <= triangles.Length(); ++i) {
						int n1, n2, n3;

						if (face.Orientation() == TopAbs_REVERSED) {
							triangles(i).Get(n3, n2, n1);
						} else {
							triangles(i).Get(n1, n2, n3);
						}

						const gp_XYZ& pt1 = coords[n1 - 1];
						const gp_XYZ& pt2 = coords[n2 - 1];
						const gp_XYZ& pt3 = coords[n3 - 1];
						const gp_Vec v1 = pt2 - pt1;
						const gp_Vec v2 = pt3 - pt2;
						const gp_Vec v3 = pt1 - pt3;
						const gp_Vec normal_vector = v1 ^ v2;
						if (normal_vector.Magnitude() > 1.e-7) {
							gp_Dir normal = gp_Dir();

							double edge_lengths[3] = { v1.Magnitude(), v2.Magnitude(), v3.Magnitude() };
							std::sort(&edge_lengths[0], &edge_lengths[2]);

							const double& a = edge_lengths[0];
							const double& b = edge_lengths[1];
							const double& c = edge_lengths[2];

							const double area = 0.25 * sqrt((a + (b + c))*(c - (a - b))*(c + (a - b))*(a + (b - c)));
							accumulate(ax, normal, area, along_x, along_y, along_z);
						}
					}
				}
			}
		}
	}
}
#endif

IfcGeom::Representation::Serialization::Serialization(const BRep& brep)
	: Representation(brep.settings(), brep.entity())
	, id_(brep.id())
{
	for (auto it = brep.begin(); it != brep.end(); ++it) {
		int sid = -1;

		if (it->hasStyle()) {
			const auto& clr = it->Style().diffuse.ccomponents();
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

	if (brep.begin() != brep.end()) {
		if (std::dynamic_pointer_cast<ifcopenshell::geometry::OpenCascadeShape>(brep.begin()->Shape())) {
			ConversionResultShape* shape = brep.as_compound();
			ifcopenshell::geometry::taxonomy::matrix4 identity;
			shape->Serialize(identity, brep_data_);
			delete shape;
		} else {
			for (auto it = brep.begin(); it != brep.end(); ++it) {
				std::string part;
				it->Shape()->Serialize(*it->Placement(), part);
				if (brep_data_.size()) {
					brep_data_ = brep_data_ + "\n---\n" + part;
				} else {
					brep_data_ = part;
				}
			}
		}
	}

}

IfcGeom::ConversionResultShape* IfcGeom::Representation::BRep::as_compound(bool force_meters) const {
#ifdef IFOPSH_WITH_OPENCASCADE
	TopoDS_Compound compound;
	BRep_Builder builder;
	builder.MakeCompound(compound);

	for (auto it = begin(); it != end(); ++it) {
		const TopoDS_Shape& s = *std::static_pointer_cast<ifcopenshell::geometry::OpenCascadeShape>(it->Shape());

		// @todo, check
		gp_GTrsf trsf;
		if (it->Placement()->components_) {
			gp_Trsf tr;
			const auto& m = it->Placement()->ccomponents();
			tr.SetValues(
				m(0, 0), m(0, 1), m(0, 2), m(0, 3),
				m(1, 0), m(1, 1), m(1, 2), m(1, 3),
				m(2, 0), m(2, 1), m(2, 2), m(2, 3)
			);
			trsf = tr;
		}

		if (!force_meters && settings().get<ifcopenshell::geometry::settings::ConvertBackUnits>().get()) {
			gp_Trsf scale;
			scale.SetScaleFactor(1.0 / settings().get<ifcopenshell::geometry::settings::LengthUnit>().get());
			trsf.PreMultiply(scale);
		}

		const TopoDS_Shape moved_shape = apply_transformation(s, trsf);
		builder.Add(compound, moved_shape);
	}

	return new ifcopenshell::geometry::OpenCascadeShape(compound);
#else
        throw std::runtime_error("Not available without Open Cascade");
#endif
}


bool IfcGeom::Representation::BRep::calculate_surface_area(double& area) const {
#ifdef IFOPSH_WITH_OPENCASCADE
	try {
		area = 0.;

		for (IfcGeom::ConversionResults::const_iterator it = begin(); it != end(); ++it) {
			GProp_GProps prop;
			BRepGProp::SurfaceProperties(*std::static_pointer_cast<ifcopenshell::geometry::OpenCascadeShape>(it->Shape()), prop);
			area += prop.Mass();
		}

		return true;
	} catch (...) {
		Logger::Error("Error during calculation of surface area");
		return false;
	}
#else
        throw std::runtime_error("Not available without Open Cascade");
#endif
}

bool IfcGeom::Representation::BRep::calculate_volume(double& volume) const {
#ifdef IFOPSH_WITH_OPENCASCADE
	try {
		volume = 0.;

		for (IfcGeom::ConversionResults::const_iterator it = begin(); it != end(); ++it) {
			if (util::is_manifold(*std::static_pointer_cast<ifcopenshell::geometry::OpenCascadeShape>(it->Shape()))) {
				GProp_GProps prop;
				BRepGProp::VolumeProperties(*std::static_pointer_cast<ifcopenshell::geometry::OpenCascadeShape>(it->Shape()), prop);
				volume += prop.Mass();
			} else {
				return false;
			}
		}

		return true;
	} catch (...) {
		Logger::Error("Error during calculation of volume");
		return false;
	}
#else
        throw std::runtime_error("Not available without Open Cascade");
#endif
}

bool IfcGeom::Representation::BRep::calculate_projected_surface_area(const ifcopenshell::geometry::taxonomy::matrix4& place, double & along_x, double & along_y, double & along_z) const {
#ifdef IFOPSH_WITH_OPENCASCADE
	try {
		gp_GTrsf trsf;

		if (place.components_) {
			gp_Trsf tr;
			const auto& m = place.ccomponents();
			tr.SetValues(
				m(0, 0), m(0, 1), m(0, 2), m(0, 3),
				m(1, 0), m(1, 1), m(1, 2), m(1, 3),
				m(2, 0), m(2, 1), m(2, 2), m(2, 3)
			);
			trsf = tr;
		}

		gp_Mat mat = trsf.Trsf().HVectorialPart();
		gp_Ax3 ax(trsf.TranslationPart(), mat.Column(3), mat.Column(1));

		along_x = along_y = along_z = 0.;

		for (IfcGeom::ConversionResults::const_iterator it = begin(); it != end(); ++it) {
			double x, y, z;
			surface_area_along_direction(settings().get<ifcopenshell::geometry::settings::MesherLinearDeflection>().get(), *std::static_pointer_cast<ifcopenshell::geometry::OpenCascadeShape>(it->Shape()), ax, x, y, z);

			if (util::is_manifold(*std::static_pointer_cast<ifcopenshell::geometry::OpenCascadeShape>(it->Shape()))) {
				x /= 2.;
				y /= 2.;
				z /= 2.;
			}

			along_x += x;
			along_y += y;
			along_z += z;
		}

		return true;
	} catch (...) {
		Logger::Error("Error during calculation of projected surface area");
		return false;
	}
#else
        throw std::runtime_error("Not available without Open Cascade");
#endif
}

IfcGeom::Representation::Triangulation::Triangulation(const BRep& shape_model)
	: Representation(shape_model.settings(), shape_model.entity())
	, id_(shape_model.id())
	, weld_offset_(0)
{
	for (IfcGeom::ConversionResults::const_iterator iit = shape_model.begin(); iit != shape_model.end(); ++iit) {
		
		// Don't weld vertices that belong to different items to prevent non-manifold situations.
		resetWelds();

		int surface_style_id = -1;
		if (iit->hasStyle()) {
			auto jt = std::find(_materials.begin(), _materials.end(), iit->StylePtr());
			if (jt == _materials.end()) {
				surface_style_id = (int)_materials.size();
				_materials.push_back(iit->StylePtr());
			} else {
				surface_style_id = (int)(jt - _materials.begin());
			}
		}

		if (settings().get<ifcopenshell::geometry::settings::ApplyDefaultMaterials>().get() && surface_style_id == -1) {
			const auto& material = IfcGeom::get_default_style(shape_model.entity());
			auto mit = std::find(_materials.begin(), _materials.end(), material);
			if (mit == _materials.end()) {
				surface_style_id = (int)_materials.size();
				_materials.push_back(material);
			} else {
				surface_style_id = (int)(mit - _materials.begin());
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
	int i = (int)_verts.size() / 3;
	if (settings().get<ifcopenshell::geometry::settings::WeldVertices>().get()) {
		const VertexKey key = std::make_tuple(item_id, material_index, X, Y, Z);
		typename VertexKeyMap::const_iterator it = welds.find(key);
		if (it != welds.end()) return it->second;
		i = (int)(welds.size() + weld_offset_);
		welds[key] = i;
	}
	_verts.push_back(X);
	_verts.push_back(Y);
	_verts.push_back(Z);
	return i;
}

void IfcGeom::Representation::Triangulation::addEdge(int n1, int n2, std::map<std::pair<int, int>, int>& edgecount) {
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
