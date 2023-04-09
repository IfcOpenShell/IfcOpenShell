#include "OpenCascadeConversionResult.h"

#include "../../../ifcparse/IfcLogger.h"
#include "../../../ifcgeom/IfcGeomRepresentation.h"

#include <TopoDS.hxx>
#include <Geom_SphericalSurface.hxx>

#include <map>

namespace {
	// We bypass the conversion to gp_GTrsf, because it does not work
	void taxonomy_transform(const Eigen::Matrix4d* m, gp_XYZ& xyz) {
		if (m) {
			Eigen::Vector4d v(xyz.X(), xyz.Y(), xyz.Z(), 1.0);
			auto v2 = (*m * v).eval();
			xyz.ChangeData()[0] = v2(0);
			xyz.ChangeData()[1] = v2(1);
			xyz.ChangeData()[2] = v2(2);
		}
	}
}

void ifcopenshell::geometry::OpenCascadeShape::Triangulate(const IfcGeom::IteratorSettings& settings, const ifcopenshell::geometry::taxonomy::matrix4& place, IfcGeom::Representation::Triangulation* t, int surface_style_id) const {

	// @todo remove duplication with OpenCascadeKernel::convert(const taxonomy::matrix4* matrix, gp_GTrsf& trsf);
	// above can be static?

	// A 3x3 matrix to rotate the vertex normals
	boost::optional<gp_Mat> rotation_matrix;
	
	if (place.components_) {
		const auto& m = *place.components_;
		rotation_matrix.emplace(
			m(0, 0), m(0, 1), m(0, 2),
			m(1, 0), m(1, 1), m(1, 2),
			m(2, 0), m(2, 1), m(2, 2)
		);
	}

	// Triangulate the shape
	try {
		BRepMesh_IncrementalMesh(shape_, settings.deflection_tolerance(), false, settings.angular_tolerance());
	} catch (...) {
		Logger::Message(Logger::LOG_ERROR, "Failed to triangulate shape");
		return;
	}

	// Iterates over the faces of the shape
	int num_faces = 0;
	TopExp_Explorer exp;
	for (exp.Init(shape_, TopAbs_FACE); exp.More(); exp.Next(), ++num_faces) {
		TopoDS_Face face = TopoDS::Face(exp.Current());
		TopLoc_Location loc;
		Handle_Poly_Triangulation tri = BRep_Tool::Triangulation(face, loc);

		if (tri.IsNull()) {
			Logger::Message(Logger::LOG_ERROR, "Triangulation missing for face");
		} else {
			// Keep track of the number of times an edge is used
			// Manifold edges (i.e. edges used twice) are deemed invisible
			std::map<std::pair<int, int>, int> edgecount;
			std::vector<std::pair<int, int> > edges_temp;

			std::vector<gp_XYZ> coords;
			BRepGProp_Face prop(face);
			std::map<int, int> dict;

			// Vertex normals are only calculated if vertices are not welded and calculation is not disable explicitly.
			const bool calculate_normals = !settings.get(IfcGeom::IteratorSettings::WELD_VERTICES) &&
				!settings.get(IfcGeom::IteratorSettings::NO_NORMALS);

			for (int i = 1; i <= tri->NbNodes(); ++i) {
				coords.push_back(tri->Node(i).Transformed(loc).XYZ());
				taxonomy_transform(place.components_, *coords.rbegin());
				const gp_XYZ& last = *coords.rbegin();
				dict[i] = t->addVertex(surface_style_id, last.X(), last.Y(), last.Z());

				if (calculate_normals) {
					const gp_Pnt2d& uv = tri->UVNode(i);
					gp_Pnt p;
					gp_Vec normal_direction;
					prop.Normal(uv.X(), uv.Y(), p, normal_direction);
					gp_Vec normal(0., 0., 0.);
					if (normal_direction.Magnitude() > 1.e-9) {
						if (rotation_matrix) {
							normal = gp_Dir(normal_direction.XYZ() * *rotation_matrix);
						} else {
							normal = normal_direction;
						}
					} else {
						Handle_Geom_Surface surf = BRep_Tool::Surface(face);
						// Special case the normal at the poles of a spherical surface
						if (surf->DynamicType() == STANDARD_TYPE(Geom_SphericalSurface)) {
							if (fabs(fabs(uv.Y()) - M_PI / 2.) < 1.e-9) {
								const bool is_top = uv.Y() > 0;
								const bool is_forward = face.Orientation() == TopAbs_FORWARD;
								const double z = (is_top == is_forward) ? 1. : -1.;
								if (rotation_matrix) {
									normal = gp_Dir(gp_XYZ(0, 0, z) * *rotation_matrix);
								} else {
									normal = gp_Dir(gp_XYZ(0, 0, z));
								}
							}
						}
						// TODO: Do the same for conical surfaces, but they are rare in IFC.
					}
					t->addNormal(normal.X(), normal.Y(), normal.Z());
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

				t->addFace(surface_style_id, dict[n1], dict[n2], dict[n3]);

				t->addEdge(dict[n1], dict[n2], edgecount, edges_temp);
				t->addEdge(dict[n2], dict[n3], edgecount, edges_temp);
				t->addEdge(dict[n3], dict[n1], edgecount, edges_temp);
			}
			for (std::vector<std::pair<int, int> >::const_iterator jt = edges_temp.begin(); jt != edges_temp.end(); ++jt) {
				if (edgecount[*jt] == 1) {
					// non manifold edge, face boundary
					t->registerEdge(jt->first, jt->second);
				}
			}
		}
	}

	if (!t->normals().empty() && settings.get(IfcGeom::IteratorSettings::GENERATE_UVS)) {
		t->uvs() = IfcGeom::Representation::Triangulation::box_project_uvs(t->verts(), t->normals());
	}

	if (num_faces == 0) {
		// Edges are only emitted if there are no faces. A mixed representation of faces
		// and loose edges is discouraged by the standard. An alternative would be to use
		// TopExp_Explorer texp(s, TopAbs_EDGE, TopAbs_FACE) to find edges that do not
		// belong to any face.
		for (TopExp_Explorer texp(shape_, TopAbs_EDGE); texp.More(); texp.Next()) {
			BRepAdaptor_Curve crv(TopoDS::Edge(texp.Current()));
			GCPnts_QuasiUniformDeflection tessellater(crv, settings.deflection_tolerance());
			int n = tessellater.NbPoints();
			int previous = -1;

			for (int i = 1; i <= n; ++i) {
				gp_XYZ p = tessellater.Value(i).XYZ();

				taxonomy_transform(place.components_, p);

				int current = t->addVertex(surface_style_id, p.X(), p.Y(), p.Z());

				std::vector<std::pair<int, int>> segments;
				if (i > 1) {
					segments.push_back(std::make_pair(previous, current));
				}

				if (settings.get(IfcGeom::IteratorSettings::EDGE_ARROWS)) {
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

					taxonomy_transform(place.components_, p2);
					taxonomy_transform(place.components_, p3);
					taxonomy_transform(place.components_, p);

					int left = t->addVertex(surface_style_id, p2.X(), p2.Y(), p2.Z());
					int right = t->addVertex(surface_style_id, p3.X(), p3.Y(), p3.Z());

					segments.push_back(std::make_pair(left, current));
					segments.push_back(std::make_pair(right, current));
				}

				for (auto& sgmt : segments) {
					t->addEdge(surface_style_id, sgmt.first, sgmt.second);
				}

				previous = current;
			}
		}
	}

	BRepTools::Clean(shape_);
}

int ifcopenshell::geometry::OpenCascadeShape::surface_genus() const {
	throw std::runtime_error("Not implemented");
}

bool ifcopenshell::geometry::OpenCascadeShape::is_manifold() const {
	throw std::runtime_error("Not implemented");
}