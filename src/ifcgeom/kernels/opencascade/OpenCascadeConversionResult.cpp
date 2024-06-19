#include <map>

#include <TopoDS.hxx>
#include <TopExp.hxx>
#include <BRepGProp.hxx>
#include <GProp_GProps.hxx>
#include <Geom_SphericalSurface.hxx>

#include "OpenCascadeConversionResult.h"

#include "../../../ifcparse/IfcLogger.h"
#include "../../../ifcgeom/IfcGeomRepresentation.h"
#include "base_utils.h"
#include "boolean_utils.h"

#include <Standard_Version.hxx>

#if OCC_VERSION_HEX >= 0x70600
#include <TopTools_FormatVersion.hxx>
#endif

using IfcGeom::OpaqueNumber;
using IfcGeom::OpaqueCoordinate;
using IfcGeom::NumberNativeDouble;
using IfcGeom::ConversionResultShape;

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

void ifcopenshell::geometry::OpenCascadeShape::Triangulate(ifcopenshell::geometry::Settings settings, const ifcopenshell::geometry::taxonomy::matrix4& place, IfcGeom::Representation::Triangulation* t, int item_id, int surface_style_id) const {

	// @todo remove duplication with OpenCascadeKernel::convert(const taxonomy::matrix4::ptr matrix, gp_GTrsf& trsf);
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
	
	// When welding vertices, vertex coords will be shared among faces so we need to per-shape set
	// to keep track of which edges were already emitted.
	std::set<std::pair<int, int>> emitted_edges;

	// Triangulate the shape
	try {
		BRepMesh_IncrementalMesh(shape_, settings.get<settings::MesherLinearDeflection>().get(), false, settings.get<settings::MesherAngularDeflection>().get());
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

			std::vector<gp_XYZ> coords;
			BRepGProp_Face prop(face);
			std::map<int, int> dict;

			// Vertex normals are only calculated if vertices are not welded and calculation is not disable explicitly.
			const bool calculate_normals = !settings.get<settings::WeldVertices>().get() &&
				!settings.get<settings::DontEmitNormals>().get();

			for (int i = 1; i <= tri->NbNodes(); ++i) {
				coords.push_back(tri->Node(i).Transformed(loc).XYZ());
				taxonomy_transform(place.components_, *coords.rbegin());
				const gp_XYZ& last = *coords.rbegin();
				dict[i] = t->addVertex(item_id, surface_style_id, last.X(), last.Y(), last.Z());

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

				if (dict[n1] == dict[n2] || dict[n2] == dict[n3] || dict[n3] == dict[n1]) {
					Logger::Warning("Mesher generated a degenerate triangle, ignoring");
					continue;
				}

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

				t->addFace(item_id, surface_style_id, dict[n1], dict[n2], dict[n3]);

				t->addEdge(dict[n1], dict[n2], edgecount);
				t->addEdge(dict[n2], dict[n3], edgecount);
				t->addEdge(dict[n3], dict[n1], edgecount);
			}
			for (auto& p : edgecount) {
				// @todo should be != 2?
				if (p.second == 1 && emitted_edges.find(p.first) == emitted_edges.end()) {
					// non manifold edge, face boundary
					t->registerEdge(p.first.first, p.first.second);
					if (settings.get<settings::WeldVertices>().get()) {
						// only relevant while welding, because otherwise vertices are not shared among distinct faces
						emitted_edges.insert(p.first);
					}
				}
			}
		}
	}

	if (!t->normals().empty() && settings.get<settings::GenerateUvs>().get()) {
		t->uvs() = IfcGeom::Representation::Triangulation::box_project_uvs(t->verts(), t->normals());
	}

	if (num_faces == 0) {
		// Edges are only emitted if there are no faces. A mixed representation of faces
		// and loose edges is discouraged by the standard. An alternative would be to use
		// TopExp_Explorer texp(s, TopAbs_EDGE, TopAbs_FACE) to find edges that do not
		// belong to any face.
		for (TopExp_Explorer texp(shape_, TopAbs_EDGE); texp.More(); texp.Next()) {
			BRepAdaptor_Curve crv(TopoDS::Edge(texp.Current()));
			GCPnts_QuasiUniformDeflection tessellater(crv, settings.get<settings::MesherLinearDeflection>().get());
			int n = tessellater.NbPoints();
			int previous = -1;

			for (int i = 1; i <= n; ++i) {
				gp_XYZ p = tessellater.Value(i).XYZ();
				auto p_local = p;
				taxonomy_transform(place.components_, p);

				int current = t->addVertex(item_id, surface_style_id, p.X(), p.Y(), p.Z());

				std::vector<std::pair<int, int>> segments;
				if (i > 1) {
					segments.push_back(std::make_pair(previous, current));
				}

				if (settings.get<settings::EdgeArrows>().get()) {
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
					p2 = p_local - d3.XYZ() / 10.;
					p3 = p_local - d4.XYZ() / 10.;

					taxonomy_transform(place.components_, p2);
					taxonomy_transform(place.components_, p3);

					int left = t->addVertex(item_id, surface_style_id, p2.X(), p2.Y(), p2.Z());
					int right = t->addVertex(item_id, surface_style_id, p3.X(), p3.Y(), p3.Z());

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

void ifcopenshell::geometry::OpenCascadeShape::Serialize(const ifcopenshell::geometry::taxonomy::matrix4& place, std::string& r) const {
	auto s = IfcGeom::util::apply_transformation(shape_, place);
	std::stringstream sstream;
#if OCC_VERSION_HEX >= 0x70600
	BRepTools::Write(s, sstream, false, false, TopTools_FormatVersion_VERSION_2);
#else
	BRepTools::Write(s, sstream);
#endif
	r = sstream.str();
}

int ifcopenshell::geometry::OpenCascadeShape::surface_genus() const {
	return IfcGeom::util::surface_genus(shape_);
}

bool ifcopenshell::geometry::OpenCascadeShape::is_manifold() const {
	return IfcGeom::util::is_manifold(shape_);
}

int ifcopenshell::geometry::OpenCascadeShape::num_vertices() const
{
	return IfcGeom::util::count(shape_, TopAbs_VERTEX);
}

int ifcopenshell::geometry::OpenCascadeShape::num_edges() const
{
	return IfcGeom::util::count(shape_, TopAbs_EDGE);
}

int ifcopenshell::geometry::OpenCascadeShape::num_faces() const
{
	return IfcGeom::util::count(shape_, TopAbs_FACE);
}

OpaqueNumber* ifcopenshell::geometry::OpenCascadeShape::OpenCascadeShape::length()
{
	GProp_GProps prop;
	BRepGProp::LinearProperties(shape_, prop);
	double l = prop.Mass();
	return new NumberNativeDouble(l);
}

OpaqueNumber* ifcopenshell::geometry::OpenCascadeShape::area()
{
	GProp_GProps prop;
	BRepGProp::SurfaceProperties(shape_, prop);
	double l = prop.Mass();
	return new NumberNativeDouble(l);
}

OpaqueNumber* ifcopenshell::geometry::OpenCascadeShape::volume()
{
	GProp_GProps prop;
	BRepGProp::VolumeProperties(shape_, prop);
	double l = prop.Mass();
	return new NumberNativeDouble(l);
}

#include <Geom_Plane.hxx>

OpaqueCoordinate<3> ifcopenshell::geometry::OpenCascadeShape::position()
{
	if (shape_.ShapeType() == TopAbs_FACE) {
		auto surf = BRep_Tool::Surface(TopoDS::Face(shape_));
		auto plane = Handle(Geom_Plane)::DownCast(surf);
		if (plane) {
			auto loc = plane->Location();
			return OpaqueCoordinate<3>(
				new NumberNativeDouble(loc.X()),
				new NumberNativeDouble(loc.Y()),
				new NumberNativeDouble(loc.Z())
			);
		}
	}
	throw std::runtime_error("Invalid shape type");
}

OpaqueCoordinate<3> ifcopenshell::geometry::OpenCascadeShape::axis()
{
	if (shape_.ShapeType() == TopAbs_FACE) {
		auto surf = BRep_Tool::Surface(TopoDS::Face(shape_));
		auto plane = Handle(Geom_Plane)::DownCast(surf);
		if (plane) {
			auto dir = plane->Axis().Direction();
			return OpaqueCoordinate<3>(
				new NumberNativeDouble(dir.X()),
				new NumberNativeDouble(dir.Y()),
				new NumberNativeDouble(dir.Z())
			);
		}
	}
	throw std::runtime_error("Invalid shape type");
}

OpaqueCoordinate<4> ifcopenshell::geometry::OpenCascadeShape::plane_equation()
{
	if (shape_.ShapeType() == TopAbs_FACE) {
		auto surf = BRep_Tool::Surface(TopoDS::Face(shape_));
		auto plane = Handle(Geom_Plane)::DownCast(surf);
		if (plane) {
			double a, b, c, d;
			plane->Pln().Coefficients(a, b, c, d);
			return OpaqueCoordinate<4>(
				new NumberNativeDouble(a),
				new NumberNativeDouble(b),
				new NumberNativeDouble(c),
				new NumberNativeDouble(d)
			);
		}
	}
	throw std::runtime_error("Invalid shape type");
}

std::vector<ConversionResultShape*> ifcopenshell::geometry::OpenCascadeShape::convex_decomposition()
{
	throw std::runtime_error("Not implemented");
}

ConversionResultShape * ifcopenshell::geometry::OpenCascadeShape::halfspaces()
{
	throw std::runtime_error("Not implemented");
}

ConversionResultShape* ifcopenshell::geometry::OpenCascadeShape::solid()
{
	throw std::runtime_error("Not implemented");
}

ConversionResultShape * ifcopenshell::geometry::OpenCascadeShape::box()
{
	throw std::runtime_error("Not implemented");
}

std::vector<ConversionResultShape*> ifcopenshell::geometry::OpenCascadeShape::vertices()
{
	TopTools_IndexedMapOfShape map;
	TopExp::MapShapes(shape_, TopAbs_VERTEX, map);
	std::vector<ConversionResultShape*> vec;
	for (int i = 1; i <= map.Extent(); ++i) {
		vec.push_back(new OpenCascadeShape(map.FindKey(i)));
	}
	return vec;
}

std::vector<ConversionResultShape*> ifcopenshell::geometry::OpenCascadeShape::edges()
{
	TopTools_IndexedMapOfShape map;
	TopExp::MapShapes(shape_, TopAbs_EDGE, map);
	std::vector<ConversionResultShape*> vec;
	for (int i = 1; i <= map.Extent(); ++i) {
		vec.push_back(new OpenCascadeShape(map.FindKey(i)));
	}
	return vec;
}

std::vector<ConversionResultShape*> ifcopenshell::geometry::OpenCascadeShape::facets()
{
	TopTools_IndexedMapOfShape map;
	TopExp::MapShapes(shape_, TopAbs_FACE, map);
	std::vector<ConversionResultShape*> vec;
	for (int i = 1; i <= map.Extent(); ++i) {
		vec.push_back(new OpenCascadeShape(map.FindKey(i)));
	}
	return vec;
}

namespace {
	ConversionResultShape* boolean_op(BOPAlgo_Operation op, const TopoDS_Shape& shape_, const TopoDS_Shape& other_shape) {
		IfcGeom::util::boolean_settings st;
		st.attempt_2d = true;
		st.debug = false;
		st.precision = 1.e-5;

		TopoDS_Shape result;
		if (IfcGeom::util::boolean_operation(st, shape_, other_shape, op, result)) {
			return new ifcopenshell::geometry::OpenCascadeShape(result);
		} else {
			throw std::runtime_error("Failed to process boolean operation");
		}
	}
}

ConversionResultShape* ifcopenshell::geometry::OpenCascadeShape::add(ConversionResultShape* other)
{
	return boolean_op(BOPAlgo_FUSE, shape_, ((ifcopenshell::geometry::OpenCascadeShape*)other)->shape_);
}

ConversionResultShape* ifcopenshell::geometry::OpenCascadeShape::subtract(ConversionResultShape* other)
{
	return boolean_op(BOPAlgo_CUT, shape_, ((ifcopenshell::geometry::OpenCascadeShape*)other)->shape_);
}

ConversionResultShape* ifcopenshell::geometry::OpenCascadeShape::intersect(ConversionResultShape* other)
{
	return boolean_op(BOPAlgo_COMMON, shape_, ((ifcopenshell::geometry::OpenCascadeShape*)other)->shape_);
}

std::pair<OpaqueCoordinate<3>, OpaqueCoordinate<3>> ifcopenshell::geometry::OpenCascadeShape::bounding_box() const
{
	throw std::runtime_error("Not implemented");
}

ConversionResultShape* ifcopenshell::geometry::OpenCascadeShape::moved(ifcopenshell::geometry::taxonomy::matrix4::ptr t) const
{
	return new OpenCascadeShape(IfcGeom::util::apply_transformation(shape_, *t));
}

void ifcopenshell::geometry::OpenCascadeShape::map(OpaqueCoordinate<4>&, OpaqueCoordinate<4>&) {
	throw std::runtime_error("Not implemented");
}

void ifcopenshell::geometry::OpenCascadeShape::map(const std::vector<OpaqueCoordinate<4>>&, const std::vector<OpaqueCoordinate<4>>&) {
	throw std::runtime_error("Not implemented");
}
