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

#ifndef IFCGEOMREPRESENTATION_H
#define IFCGEOMREPRESENTATION_H

#include <BRepMesh_IncrementalMesh.hxx>
#include <BRepGProp_Face.hxx>

#include <Poly_Triangulation.hxx>
#include <TColgp_Array1OfPnt.hxx>
#include <TColgp_Array1OfPnt2d.hxx>

#include <TopExp_Explorer.hxx>

#include <BRepAdaptor_Curve.hxx>
#include <GCPnts_QuasiUniformDeflection.hxx>

#include "../ifcgeom/IfcGeomIteratorSettings.h"
#include "../ifcgeom/IfcGeomMaterial.h"
#include "../ifcgeom/IfcRepresentationShapeItem.h"

namespace IfcGeom {

	namespace Representation {

		class Representation {
		protected:
			const ElementSettings _settings;
		public:
			explicit Representation(const ElementSettings& settings)
				: _settings(settings) 
			{}
			const ElementSettings& settings() const { return _settings; }
			virtual ~Representation() {}
		};

		class BRep : public Representation {
		private:
			unsigned int id;
			const IfcGeom::IfcRepresentationShapeItems _shapes;
			BRep(const BRep& other);
			BRep& operator=(const BRep& other);
		public:
			BRep(const ElementSettings& settings, unsigned int id, const IfcGeom::IfcRepresentationShapeItems& shapes)
				: Representation(settings)
				, id(id)
				, _shapes(shapes)
			{}
			virtual ~BRep() {}
			IfcGeom::IfcRepresentationShapeItems::const_iterator begin() const { return _shapes.begin(); }
			IfcGeom::IfcRepresentationShapeItems::const_iterator end() const { return _shapes.end(); }
			const IfcGeom::IfcRepresentationShapeItems& shapes() const { return _shapes; }
			const unsigned int& getId() const { return id; }
		};

		class Serialization : public Representation  {
		private:
			int _id;
			std::string _brep_data;
		public:
			int id() const { return _id; }
			const std::string& brep_data() const { return _brep_data; }
			Serialization(const BRep& brep);
			virtual ~Serialization() {}
		private:
			Serialization();
			Serialization(const Serialization&);
			Serialization& operator=(const Serialization&);
		};

		template <typename P>
		class Triangulation : public Representation {
		private:
			// A nested pair of floats and a material index to be able to store an XYZ coordinate in a map.
			// TODO: Make this a std::tuple when compilers add support for that.
			typedef typename std::pair<P, std::pair<P, P> > Coordinate;
			typedef typename std::pair<int, Coordinate> VertexKey;
			typedef std::map<VertexKey, int> VertexKeyMap;
			typedef std::pair<int, int> Edge;

			int _id;
			std::vector<P> _verts;
			std::vector<int> _faces;
			std::vector<int> _edges;
			std::vector<P> _normals;
			std::vector<int> _material_ids;
			std::vector<Material> _materials;
			VertexKeyMap welds;

		public:
			int id() const { return _id; }
			const std::vector<P>& verts() const { return _verts; }
			const std::vector<int>& faces() const { return _faces; }
			const std::vector<int>& edges() const { return _edges; }
			const std::vector<P>& normals() const { return _normals; }
			const std::vector<int>& material_ids() const { return _material_ids; }
			const std::vector<Material>& materials() const { return _materials; }
			Triangulation(const BRep& shape_model)
					: Representation(shape_model.settings())
					, _id(shape_model.getId())
			{
				for ( IfcGeom::IfcRepresentationShapeItems::const_iterator it = shape_model.begin(); it != shape_model.end(); ++ it ) {

					int surface_style_id = -1;
					if (it->hasStyle()) {
						Material adapter(&it->Style());
						std::vector<Material>::const_iterator jt = std::find(_materials.begin(), _materials.end(), adapter);
						if (jt == _materials.end()) {
							surface_style_id = _materials.size();
							_materials.push_back(adapter);
						} else {
							surface_style_id = jt - _materials.begin();
						}
					}

					if (settings().apply_default_materials() && surface_style_id == -1) {
						Material material(IfcGeom::get_default_style(settings().element_type()));
						std::vector<Material>::const_iterator it = std::find(_materials.begin(), _materials.end(), material);
						if (it == _materials.end()) {
							surface_style_id = _materials.size();
							_materials.push_back(material);
						} else {
							surface_style_id = it - _materials.begin();
						}
					}

					const TopoDS_Shape& s = it->Shape();
					const gp_GTrsf& trsf = it->Placement();

					// Triangulate the shape
					try {
						BRepMesh_IncrementalMesh(s, settings().deflection_tolerance());
					} catch(...) {

						// TODO: Catch outside
						// Logger::Message(Logger::LOG_ERROR,"Failed to triangulate shape:",ifc_file->entityById(_id)->entity);
						Logger::Message(Logger::LOG_ERROR,"Failed to triangulate shape");
						continue;
					}

					// Iterates over the faces of the shape
					int num_faces = 0;
					TopExp_Explorer exp;
					for ( exp.Init(s,TopAbs_FACE); exp.More(); exp.Next(), ++num_faces ) {
						TopoDS_Face face = TopoDS::Face(exp.Current());
						TopLoc_Location loc;
						Handle_Poly_Triangulation tri = BRep_Tool::Triangulation(face,loc);

						if ( ! tri.IsNull() ) {

							// A 3x3 matrix to rotate the vertex normals
							const gp_Mat rotation_matrix = trsf.VectorialPart();
			
							// Keep track of the number of times an edge is used
							// Manifold edges (i.e. edges used twice) are deemed invisible
							std::map<std::pair<int,int>,int> edgecount;
							std::vector<std::pair<int,int> > edges_temp;

							const TColgp_Array1OfPnt& nodes = tri->Nodes();
							const TColgp_Array1OfPnt2d& uvs = tri->UVNodes();
							std::vector<gp_XYZ> coords;
							BRepGProp_Face prop(face);
							std::map<int,int> dict;

							// Vertex normals are only calculated if vertices are not welded
							const bool calculate_normals = !settings().weld_vertices();

							for( int i = 1; i <= nodes.Length(); ++ i ) {
								coords.push_back(nodes(i).Transformed(loc).XYZ());
								trsf.Transforms(*coords.rbegin());
								dict[i] = addVertex(surface_style_id, *coords.rbegin());
					
								if ( calculate_normals ) {
									const gp_Pnt2d& uv = uvs(i);
									gp_Pnt p;
									gp_Vec normal_direction;
									prop.Normal(uv.X(),uv.Y(),p,normal_direction);
									gp_Vec normal(0., 0., 0.);
									if (normal_direction.Magnitude() > ALMOST_ZERO) {
										normal = gp_Dir(normal_direction.XYZ() * rotation_matrix);
									}
									_normals.push_back(static_cast<P>(normal.X()));
									_normals.push_back(static_cast<P>(normal.Y()));
									_normals.push_back(static_cast<P>(normal.Z()));
								}
							}

							const Poly_Array1OfTriangle& triangles = tri->Triangles();			
							for( int i = 1; i <= triangles.Length(); ++ i ) {
								int n1,n2,n3;
								if ( face.Orientation() == TopAbs_REVERSED )
									triangles(i).Get(n3,n2,n1);
								else triangles(i).Get(n1,n2,n3);

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
							for ( std::vector<std::pair<int,int> >::const_iterator it = edges_temp.begin(); it != edges_temp.end(); ++it ) {
								if (edgecount[*it] == 1) {
									// non manifold edge, face boundary
									_edges.push_back(it->first);
									_edges.push_back(it->second);
								}
							}
						}
					}

					if (num_faces == 0) {
						// Edges are only emitted if there are no faces. A mixed representation of faces
						// and loose edges is discouraged by the standard. An alternative would be to use
						// TopExp::MapShapesAndAncestors() to find edges that do not belong to any face.
						for (TopExp_Explorer exp(s, TopAbs_EDGE); exp.More(); exp.Next()) {
							BRepAdaptor_Curve crv(TopoDS::Edge(exp.Current()));
							GCPnts_QuasiUniformDeflection tessellater(crv, settings().deflection_tolerance());
							int n = tessellater.NbPoints();
							int start = _verts.size() / 3;
							for (int i = 1; i <= n; ++i) {
								gp_XYZ p = tessellater.Value(i).XYZ();
								trsf.Transforms(p);
								
								_material_ids.push_back(surface_style_id);

								_verts.push_back(static_cast<P>(p.X()));
								_verts.push_back(static_cast<P>(p.Y()));
								_verts.push_back(static_cast<P>(p.Z()));

								if (i > 1) {
									_edges.push_back(start + i - 2);
									_edges.push_back(start + i - 1);
								}
							}
						}
					}

				}
			}
			virtual ~Triangulation() {}
		private:
			// Welds vertices that belong to different faces
			int addVertex(int material_index, const gp_XYZ& p) {
				const P X = static_cast<P>(settings().convert_back_units() ? (p.X() / settings().unit_magnitude()) : p.X());
				const P Y = static_cast<P>(settings().convert_back_units() ? (p.Y() / settings().unit_magnitude()) : p.Y());
				const P Z = static_cast<P>(settings().convert_back_units() ? (p.Z() / settings().unit_magnitude()) : p.Z());
				int i = (int) _verts.size() / 3;
				if (settings().weld_vertices()) {
					const VertexKey key = std::make_pair(material_index, std::make_pair(X, std::make_pair(Y, Z)));
					typename VertexKeyMap::const_iterator it = welds.find(key);
					if ( it != welds.end() ) return it->second;
					i = (int) welds.size();
					welds[key] = i;
				}
				_verts.push_back(X);
				_verts.push_back(Y);
				_verts.push_back(Z);
				return i;
			}
			inline void addEdge(int n1, int n2, std::map<std::pair<int,int>,int>& edgecount, std::vector<std::pair<int,int> >& edges_temp) {
				const Edge e = Edge( (std::min)(n1,n2),(std::max)(n1,n2) );
				if ( edgecount.find(e) == edgecount.end() ) edgecount[e] = 1;
				else edgecount[e] ++;
				edges_temp.push_back(e);
			}
			Triangulation();
			Triangulation(const Triangulation&);
			Triangulation& operator=(const Triangulation&);
		};

	}
}

#endif