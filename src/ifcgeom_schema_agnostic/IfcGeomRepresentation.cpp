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

#include <BRep_Tool.hxx>
#include <BRepTools.hxx>
#include <BRep_Builder.hxx>
#include <Geom_Plane.hxx>
#include <TopoDS_Compound.hxx>
#include <BRepGProp.hxx>
#include <GProp_GProps.hxx>

#include "../ifcparse/IfcLogger.h"
#include "../ifcgeom_schema_agnostic/Kernel.h"

IfcGeom::Representation::Serialization::Serialization(const BRep& brep)
	: Representation(brep.settings())
	, id_(brep.id())
{
	TopoDS_Compound compound = brep.as_compound();
	for (IfcGeom::IfcRepresentationShapeItems::const_iterator it = brep.begin(); it != brep.end(); ++ it) {
		int sid = -1;
		
		if (it->hasStyle() && it->Style().Diffuse()) {
			const IfcGeom::SurfaceStyle::ColorComponent& clr = *it->Style().Diffuse();
			surface_styles_.push_back(clr.R());
			surface_styles_.push_back(clr.G());
			surface_styles_.push_back(clr.B());

			sid = it->Style().Id().get_value_or(-1);
		} else {
			surface_styles_.push_back(-1.);
			surface_styles_.push_back(-1.);
			surface_styles_.push_back(-1.);
		}

		if (it->hasStyle() && it->Style().Transparency()) {
			surface_styles_.push_back(1. - *it->Style().Transparency());
		} else {
			surface_styles_.push_back(1.);
		}

		surface_style_ids_.push_back(sid);
	}
	std::stringstream sstream;
	BRepTools::Write(compound,sstream);
	brep_data_ = sstream.str();
}

// todo copied from kernel
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

TopoDS_Compound IfcGeom::Representation::BRep::as_compound(bool force_meters) const {
	TopoDS_Compound compound;
	BRep_Builder builder;
	builder.MakeCompound(compound);
	for (IfcGeom::IfcRepresentationShapeItems::const_iterator it = begin(); it != end(); ++it) {
		const TopoDS_Shape& s = it->Shape();
		gp_GTrsf trsf = it->Placement();

		if (!force_meters && settings().get(IteratorSettings::CONVERT_BACK_UNITS)) {
			gp_Trsf scale;
			scale.SetScaleFactor(1.0 / settings().unit_magnitude());
			trsf.PreMultiply(scale);
		}

		const TopoDS_Shape moved_shape = apply_transformation(s, trsf);
		builder.Add(compound, moved_shape);
	}
	return compound;
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
						if (normal_vector.Magnitude() > ALMOST_ZERO) {
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

bool IfcGeom::Representation::BRep::calculate_surface_area(double& area) const {
	try {
		area = 0.;

		for (IfcGeom::IfcRepresentationShapeItems::const_iterator it = begin(); it != end(); ++it) {
			GProp_GProps prop;
			BRepGProp::SurfaceProperties(it->Shape(), prop);
			area += prop.Mass();
		}

		return true;
	} catch (...) {
		Logger::Error("Error during calculation of surface area");
		return false;
	}
}

bool IfcGeom::Representation::BRep::calculate_volume(double& volume) const {
	try {
		volume = 0.;

		for (IfcGeom::IfcRepresentationShapeItems::const_iterator it = begin(); it != end(); ++it) {
			if (Kernel::is_manifold(it->Shape())) {
				GProp_GProps prop;
				BRepGProp::VolumeProperties(it->Shape(), prop);
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
}

bool IfcGeom::Representation::BRep::calculate_projected_surface_area(const gp_Ax3 & ax, double & along_x, double & along_y, double & along_z) const {
	try {
		along_x = along_y = along_z = 0.;

		for (IfcGeom::IfcRepresentationShapeItems::const_iterator it = begin(); it != end(); ++it) {
			double x, y, z;
			surface_area_along_direction(settings().deflection_tolerance(), it->Shape(), ax, x, y, z);

			if (Kernel::is_manifold(it->Shape())) {
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
}

IfcGeom::Representation::Triangulation::Triangulation(const BRep& shape_model)
	: Representation(shape_model.settings())
	, id_(shape_model.id())
	, weld_offset_(0)
{
	for (IfcGeom::IfcRepresentationShapeItems::const_iterator iit = shape_model.begin(); iit != shape_model.end(); ++iit) {

		// Don't weld vertices that belong to different items to prevent non-manifold situations.
		weld_offset_ += welds.size();
		welds.clear();

		int surface_style_id = -1;
		if (iit->hasStyle()) {
			Material adapter(iit->StylePtr());
			std::vector<Material>::const_iterator jt = std::find(_materials.begin(), _materials.end(), adapter);
			if (jt == _materials.end()) {
				surface_style_id = (int)_materials.size();
				_materials.push_back(adapter);
			} else {
				surface_style_id = (int)(jt - _materials.begin());
			}
		}

		if (settings().get(IteratorSettings::APPLY_DEFAULT_MATERIALS) && surface_style_id == -1) {
			Material material(IfcGeom::get_default_style(settings().element_type()));
			std::vector<Material>::const_iterator mit = std::find(_materials.begin(), _materials.end(), material);
			if (mit == _materials.end()) {
				surface_style_id = (int)_materials.size();
				_materials.push_back(material);
			} else {
				surface_style_id = (int)(mit - _materials.begin());
			}
		}

		const TopoDS_Shape& s = iit->Shape();
		const gp_GTrsf& trsf = iit->Placement();

		// Triangulate the shape
		try {
			BRepMesh_IncrementalMesh(s, settings().deflection_tolerance(), false, settings().angular_tolerance());
		} catch (...) {
			Logger::Message(Logger::LOG_ERROR, "Failed to triangulate shape");
			continue;
		}

		// Iterates over the faces of the shape
		int num_faces = 0;
		TopExp_Explorer exp;
		for (exp.Init(s, TopAbs_FACE); exp.More(); exp.Next(), ++num_faces) {
			TopoDS_Face face = TopoDS::Face(exp.Current());
			TopLoc_Location loc;
			Handle_Poly_Triangulation tri = BRep_Tool::Triangulation(face, loc);

			if (tri.IsNull()) {
				Logger::Message(Logger::LOG_ERROR, "Triangulation missing for face");
			} else {
				// A 3x3 matrix to rotate the vertex normals
				const gp_Mat rotation_matrix = trsf.VectorialPart();

				// Keep track of the number of times an edge is used
				// Manifold edges (i.e. edges used twice) are deemed invisible
				std::map<std::pair<int, int>, int> edgecount;
				std::vector<std::pair<int, int> > edges_temp;

				std::vector<gp_XYZ> coords;
				BRepGProp_Face prop(face);
				std::map<int, int> dict;

				// Vertex normals are only calculated if vertices are not welded and calculation is not disable explicitly.
				const bool calculate_normals = !settings().get(IteratorSettings::WELD_VERTICES) &&
					!settings().get(IteratorSettings::NO_NORMALS);

				for (int i = 1; i <= tri->NbNodes(); ++i) {
					coords.push_back(tri->Node(i).Transformed(loc).XYZ());
					trsf.Transforms(*coords.rbegin());
					dict[i] = addVertex(surface_style_id, *coords.rbegin());

					if (calculate_normals) {
						const gp_Pnt2d& uv = tri->UVNode(i);
						gp_Pnt p;
						gp_Vec normal_direction;
						prop.Normal(uv.X(), uv.Y(), p, normal_direction);
						gp_Vec normal(0., 0., 0.);
						if (normal_direction.Magnitude() > 1.e-9) {
							normal = gp_Dir(normal_direction.XYZ() * rotation_matrix);
						} else {
							Handle_Geom_Surface surf = BRep_Tool::Surface(face);
							// Special case the normal at the poles of a spherical surface
							if (surf->DynamicType() == STANDARD_TYPE(Geom_SphericalSurface)) {
								if (fabs(fabs(uv.Y()) - M_PI / 2.) < 1.e-9) {
									const bool is_top = uv.Y() > 0;
									const bool is_forward = face.Orientation() == TopAbs_FORWARD;
									const double z = (is_top == is_forward) ? 1. : -1.;
									normal = gp_Dir(gp_XYZ(0, 0, z) * rotation_matrix);
								}
							}
							// TODO: Do the same for conical surfaces, but they are rare in IFC.
						}
						_normals.push_back(normal.X());
						_normals.push_back(normal.Y());
						_normals.push_back(normal.Z());
					}
				}

				const Poly_Array1OfTriangle& triangles = tri->Triangles();
				for (int i = 1; i <= triangles.Length(); ++i) {
					int n1, n2, n3;
					if (face.Orientation() == TopAbs_REVERSED)
						triangles(i).Get(n3, n2, n1);
					else triangles(i).Get(n1, n2, n3);

					/* An alternative would be to calculate normals based
						* on the coordinates of the mesh vertices */
						/*
						const gp_XYZ pt1 = coords[n1-1];
						const gp_XYZ pt2 = coords[n2-1];
						const gp_XYZ pt3 = coords[n3-1];
						const gp_XYZ v1 = pt2-pt1;
						const gp_XYZ v2 = pt3-pt2;
						gp_Dir normal = gp_Dir(v1^v2);
						_normals.push_back((float)normal.X());
						_normals.push_back((float)normal.Y());
						_normals.push_back((float)normal.Z());
						*/

					_faces.push_back(dict[n1]);
					_faces.push_back(dict[n2]);
					_faces.push_back(dict[n3]);

					_material_ids.push_back(surface_style_id);

					addEdge(dict[n1], dict[n2], edgecount, edges_temp);
					addEdge(dict[n2], dict[n3], edgecount, edges_temp);
					addEdge(dict[n3], dict[n1], edgecount, edges_temp);
				}
				for (std::vector<std::pair<int, int> >::const_iterator jt = edges_temp.begin(); jt != edges_temp.end(); ++jt) {
					if (edgecount[*jt] == 1) {
						// non manifold edge, face boundary
						_edges.push_back(jt->first);
						_edges.push_back(jt->second);
					}
				}
			}
		}

		if (!_normals.empty() && settings().get(IfcGeom::IteratorSettings::GENERATE_UVS)) {
			uvs_ = box_project_uvs(_verts, _normals);
		}

		if (num_faces == 0) {
			// Edges are only emitted if there are no faces. A mixed representation of faces
			// and loose edges is discouraged by the standard. An alternative would be to use
			// TopExp_Explorer texp(s, TopAbs_EDGE, TopAbs_FACE) to find edges that do not
			// belong to any face.
			for (TopExp_Explorer texp(s, TopAbs_EDGE); texp.More(); texp.Next()) {
				BRepAdaptor_Curve crv(TopoDS::Edge(texp.Current()));
				GCPnts_QuasiUniformDeflection tessellater(crv, settings().deflection_tolerance());
				int n = tessellater.NbPoints();
				int previous = -1;

				for (int i = 1; i <= n; ++i) {
					gp_XYZ p = tessellater.Value(i).XYZ();

					int current = addVertex(surface_style_id, p);

					std::vector<std::pair<int, int>> segments;
					if (i > 1) {
						segments.push_back(std::make_pair(previous, current));
					}

					if (settings().get(IfcGeom::IteratorSettings::EDGE_ARROWS)) {
						// In case you want direction arrows on your edges
						double u = tessellater.Parameter(i);
						gp_XYZ p2, p3;
						gp_Pnt tmp;
						gp_Vec tmp2;
						crv.D1(u, tmp, tmp2);
						gp_Dir d1, d2, d3, d4;
						d1 = tmp2;
						if (texp.Current().Orientation() == TopAbs_REVERSED) {
							d1 = -d1;
						}
						if (fabs(d1.Z()) < 0.5) {
							d2 = d1.Crossed(gp::DZ());
						} else {
							d2 = d1.Crossed(gp::DY());
						}
						d3 = d1.XYZ() + d2.XYZ();
						d4 = d1.XYZ() - d2.XYZ();
						p2 = p - d3.XYZ() / 10.;
						p3 = p - d4.XYZ() / 10.;
						trsf.Transforms(p2);
						trsf.Transforms(p3);
						trsf.Transforms(p);

						int left = addVertex(surface_style_id, p2);
						int right = addVertex(surface_style_id, p3);

						segments.push_back(std::make_pair(left, current));
						segments.push_back(std::make_pair(right, current));
					}

					for (auto& sgmt : segments) {
						_edges.push_back(sgmt.first);
						_edges.push_back(sgmt.second);
						_material_ids.push_back(surface_style_id);
					}

					previous = current;
				}
			}
		}

		BRepTools::Clean(s);
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

int IfcGeom::Representation::Triangulation::addVertex(int material_index, const gp_XYZ & p) {
	const bool convert = settings().get(IteratorSettings::CONVERT_BACK_UNITS);
	const double X = convert ? (p.X() / settings().unit_magnitude()) : p.X();
	const double Y = convert ? (p.Y() / settings().unit_magnitude()) : p.Y();
	const double Z = convert ? (p.Z() / settings().unit_magnitude()) : p.Z();
	int i = (int)_verts.size() / 3;
	if (settings().get(IteratorSettings::WELD_VERTICES)) {
		const VertexKey key = std::make_pair(material_index, std::make_pair(X, std::make_pair(Y, Z)));
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

void IfcGeom::Representation::Triangulation::addEdge(int n1, int n2, std::map<std::pair<int, int>, int>& edgecount, std::vector<std::pair<int, int>>& edges_temp) {
	const Edge e = Edge((std::min)(n1, n2), (std::max)(n1, n2));
	if (edgecount.find(e) == edgecount.end()) edgecount[e] = 1;
	else edgecount[e] ++;
	edges_temp.push_back(e);
}
