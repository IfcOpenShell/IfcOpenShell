#include "OpenCascadeConversionResult.h"

#include "../ifcparse/IfcLogger.h"
#include "../ifcgeom_schema_agnostic/IfcGeomRepresentation.h"

#include "IfcGeom.h"

#include <TopoDS.hxx>

#include <map>

template <typename Precision>
void triangulate_helper(const TopoDS_Shape& s, const IfcGeom::IteratorSettings& settings, const IfcGeom::ConversionResultPlacement* place, IfcGeom::Representation::Triangulation<Precision>* t, int surface_style_id) {

	gp_GTrsf trsf;
	if (place) {
		trsf = dynamic_cast<const IfcGeom::OpenCascadePlacement*>(place)->trsf();
	}

	// Triangulate the shape
	try {
		BRepMesh_IncrementalMesh(s, settings.deflection_tolerance());
	} catch (...) {

		// TODO: Catch outside
		// Logger::Message(Logger::LOG_ERROR,"Failed to triangulate shape:",ifc_file->entityById(_id)->entity);
		Logger::Message(Logger::LOG_ERROR, "Failed to triangulate shape");
		return;
	}

	// Iterates over the faces of the shape
	int num_faces = 0;
	TopExp_Explorer exp;
	for (exp.Init(s, TopAbs_FACE); exp.More(); exp.Next(), ++num_faces) {
		TopoDS_Face face = TopoDS::Face(exp.Current());
		TopLoc_Location loc;
		Handle_Poly_Triangulation tri = BRep_Tool::Triangulation(face, loc);

		if (!tri.IsNull()) {

			// A 3x3 matrix to rotate the vertex normals
			const gp_Mat rotation_matrix = trsf.VectorialPart();

			// Keep track of the number of times an edge is used
			// Manifold edges (i.e. edges used twice) are deemed invisible
			std::map<std::pair<int, int>, int> edgecount;
			std::vector<std::pair<int, int> > edges_temp;

			const TColgp_Array1OfPnt& nodes = tri->Nodes();
			const TColgp_Array1OfPnt2d& uvs = tri->UVNodes();
			std::vector<gp_XYZ> coords;
			BRepGProp_Face prop(face);
			std::map<int, int> dict;

			// Vertex normals are only calculated if vertices are not welded and calculation is not disable explicitly.
			const bool calculate_normals = !settings.get(IfcGeom::IteratorSettings::WELD_VERTICES) &&
				!settings.get(IfcGeom::IteratorSettings::NO_NORMALS);

			for (int i = 1; i <= nodes.Length(); ++i) {
				coords.push_back(nodes(i).Transformed(loc).XYZ());
				trsf.Transforms(*coords.rbegin());
				const gp_XYZ& last = *coords.rbegin();
				dict[i] = t->addVertex(surface_style_id, last.X(), last.Y(), last.Z());

				if (calculate_normals) {
					const gp_Pnt2d& uv = uvs(i);
					gp_Pnt p;
					gp_Vec normal_direction;
					prop.Normal(uv.X(), uv.Y(), p, normal_direction);
					gp_Vec normal(0., 0., 0.);
					if (normal_direction.Magnitude() > 1.e-9) {
						normal = gp_Dir(normal_direction.XYZ() * rotation_matrix);
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

	/*
	TODO: Unimplemented
	if (!t.normals().empty() && settings().get(IfcGeom::IteratorSettings::GENERATE_UVS)) {
		t.uvs() = box_project_uvs(t.verts(), t.normals());
	}
	
	if (num_faces == 0) {
		// Edges are only emitted if there are no faces. A mixed representation of faces
		// and loose edges is discouraged by the standard. An alternative would be to use
		// TopExp_Explorer texp(s, TopAbs_EDGE, TopAbs_FACE) to find edges that do not
		// belong to any face.
		for (TopExp_Explorer texp(s, TopAbs_EDGE); texp.More(); texp.Next()) {
			BRepAdaptor_Curve crv(TopoDS::Edge(texp.Current()));
			GCPnts_QuasiUniformDeflection tessellater(crv, settings.deflection_tolerance());
			int n = tessellater.NbPoints();
			int start = (int)t->verts().size() / 3;
			for (int i = 1; i <= n; ++i) {
				gp_XYZ p = tessellater.Value(i).XYZ();

				// // In case you want direction arrows on your edges
				// double u = tessellater.Parameter(i);
				// gp_XYZ p2, p3;
				// gp_Pnt tmp;
				// gp_Vec tmp2;
				// crv.D1(u, tmp, tmp2);
				// gp_Dir d1, d2, d3, d4;
				// d1 = tmp2;
				// if (texp.Current().Orientation() == TopAbs_REVERSED) {
				// d1 = -d1;
				// }
				// if (fabs(d1.Z()) < 0.5) {
				// d2 = d1.Crossed(gp::DZ());
				// } else {
				// d2 = d1.Crossed(gp::DY());
				// }
				// d3 = d1.XYZ() + d2.XYZ();
				// d4 = d1.XYZ() - d2.XYZ();
				// p2 = p - d3.XYZ() / 10.;
				// p3 = p - d4.XYZ() / 10.;
				// trsf.Transforms(p2);
				// trsf.Transforms(p3);
				// _material_ids.push_back(surface_style_id);
				// _material_ids.push_back(surface_style_id);
				// _verts.push_back(static_cast<P>(p2.X()));
				// _verts.push_back(static_cast<P>(p2.Y()));
				// _verts.push_back(static_cast<P>(p2.Z()));
				// _verts.push_back(static_cast<P>(p3.X()));
				// _verts.push_back(static_cast<P>(p3.Y()));
				// _verts.push_back(static_cast<P>(p3.Z()));

				trsf.Transforms(p);

				t->material_ids().push_back(surface_style_id);

				t->verts().push_back(static_cast<double>(p.X()));
				t->verts().push_back(static_cast<double>(p.Y()));
				t->verts().push_back(static_cast<double>(p.Z()));

				if (i > 1) {
					t->edges().push_back(start + i - 2);
					t->edges().push_back(start + i - 1);
					// _edges.push_back(start + 3 * (i - 2) + 2);
					// _edges.push_back(start + 3 * (i - 1) + 2);
				}

				// _edges.push_back(start + 3 * (i - 1) + 0);
				// _edges.push_back(start + 3 * (i - 1) + 2);
				// _edges.push_back(start + 3 * (i - 1) + 1);
				// _edges.push_back(start + 3 * (i - 1) + 2);
			}
		}
	}

	*/

	BRepTools::Clean(s);
}

void IfcGeom::OpenCascadeShape::Triangulate(const IfcGeom::IteratorSettings & settings, const IfcGeom::ConversionResultPlacement * place, IfcGeom::Representation::Triangulation<float>* t, int surface_style_id) const {
	triangulate_helper(shape_, settings, place, t, surface_style_id);
}

void IfcGeom::OpenCascadeShape::Triangulate(const IfcGeom::IteratorSettings & settings, const IfcGeom::ConversionResultPlacement * place, IfcGeom::Representation::Triangulation<double>* t, int surface_style_id) const {
	triangulate_helper(shape_, settings, place, t, surface_style_id);
}

int IfcGeom::OpenCascadeShape::surface_genus() const {
	return IfcGeom::Kernel::surface_genus(shape_);
}