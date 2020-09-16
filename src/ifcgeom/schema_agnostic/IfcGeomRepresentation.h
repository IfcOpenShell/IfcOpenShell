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

#include "../../ifcgeom/settings.h"
#include "../../ifcgeom/schema_agnostic/ConversionResult.h"

#include <map>

#include <iostream>

namespace ifcopenshell { namespace geometry {

	namespace Representation {

		class IFC_GEOM_API Representation {
			Representation(const Representation&); //N/A
			Representation& operator =(const Representation&); //N/A
		protected:
			const element_settings settings_;
		public:
			explicit Representation(const element_settings& settings)
				: settings_(settings) 
			{}
			const element_settings& settings() const { return settings_; }
			virtual ~Representation() {}
		};

		class IFC_GEOM_API BRep : public Representation {
		private:
			std::string id_;
			const ifcopenshell::geometry::ConversionResults shapes_;
			BRep(const BRep& other);
			BRep& operator=(const BRep& other);
		public:
			BRep(const element_settings& settings, const std::string& id, const ifcopenshell::geometry::ConversionResults& shapes)
				: Representation(settings)
				, id_(id)
				, shapes_(shapes)
			{}
			virtual ~BRep() {}
			ifcopenshell::geometry::ConversionResults::const_iterator begin() const { return shapes_.begin(); }
			ifcopenshell::geometry::ConversionResults::const_iterator end() const { return shapes_.end(); }
			const ifcopenshell::geometry::ConversionResults& shapes() const { return shapes_; }
			const std::string& id() const { return id_; }
			ifcopenshell::geometry::ConversionResultShape* as_compound(bool force_meters = false) const;

			bool calculate_volume(double&) const;
			bool calculate_surface_area(double&) const;
			bool calculate_projected_surface_area(const ifcopenshell::geometry::taxonomy::matrix4& ax, double& along_x, double& along_y, double& along_z) const;
		};

		class IFC_GEOM_API Serialization : public Representation  {
		private:
			std::string id_;
			std::string brep_data_;
			std::vector<double> surface_styles_;
		public:
			const std::string& brep_data() const { return brep_data_; }
			const std::vector<double>& surface_styles() const { return surface_styles_; }
			Serialization(const BRep& brep);
			virtual ~Serialization() {}
			const std::string& id() const { return id_; }
		private:
			Serialization();
			Serialization(const Serialization&);
			Serialization& operator=(const Serialization&);
		};

		class Triangulation : public Representation {
		private:
			// A nested pair of floats and a material index to be able to store an XYZ coordinate in a map.
			// TODO: Make this a std::tuple when compilers add support for that.
			typedef typename std::pair<double, std::pair<double, double> > Coordinate;
			typedef typename std::pair<int, Coordinate> VertexKey;
			typedef std::map<VertexKey, int> VertexKeyMap;
			typedef std::pair<int, int> Edge;

			std::string id_;
			std::vector<double> _verts;
			std::vector<int> _faces;
			std::vector<int> _edges;
			std::vector<double> _normals;
            std::vector<double> uvs_;
			std::vector<int> _material_ids;
			std::vector<ifcopenshell::geometry::taxonomy::style> _materials;
			VertexKeyMap welds;

		public:
			const std::string& id() const { return id_; }
			const std::vector<double>& verts() const { return _verts; }
			const std::vector<int>& faces() const { return _faces; }
			const std::vector<int>& edges() const { return _edges; }
			const std::vector<double>& normals() const { return _normals; }
            const std::vector<double>& uvs() const { return uvs_; }
			const std::vector<int>& material_ids() const { return _material_ids; }
			const std::vector<ifcopenshell::geometry::taxonomy::style>& materials() const { return _materials; }

			Triangulation(const BRep& shape_model)
					: Representation(shape_model.settings())
					, id_(shape_model.id())
			{
				for ( ifcopenshell::geometry::ConversionResults::const_iterator iit = shape_model.begin(); iit != shape_model.end(); ++ iit ) {

					int surface_style_id = -1;
					if (iit->hasStyle()) {
						std::vector<ifcopenshell::geometry::taxonomy::style>::const_iterator jt = std::find(_materials.begin(), _materials.end(), iit->Style());
						if (jt == _materials.end()) {
							surface_style_id = (int)_materials.size();
							_materials.push_back(iit->Style());
						} else {
							surface_style_id = (int)(jt - _materials.begin());
						}
					}

					if (settings().get(ifcopenshell::geometry::settings::APPLY_DEFAULT_MATERIALS) && surface_style_id == -1) {
						const ifcopenshell::geometry::taxonomy::style& material = IfcGeom::get_default_style(settings().element_type());
						std::vector<ifcopenshell::geometry::taxonomy::style>::const_iterator mit = std::find(_materials.begin(), _materials.end(), material);
						if (mit == _materials.end()) {
							surface_style_id = (int)_materials.size();
							_materials.push_back(material);
						} else {
							surface_style_id = (int)(mit - _materials.begin());
						}
					}

					iit->Shape()->Triangulate(settings(), iit->Placement(), this, surface_style_id);
				}
			}
			virtual ~Triangulation() {}

            /// Generates UVs for a single mesh using box projection.
            /// @todo Very simple impl. Assumes that input vertices and normals match 1:1.
            static std::vector<double> box_project_uvs(const std::vector<double> &vertices, const std::vector<double> &normals)
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

		public:

			// Welds vertices that belong to different faces
			int addVertex(int material_index, double X, double Y, double Z) {
                const bool convert = settings().get(ifcopenshell::geometry::settings::CONVERT_BACK_UNITS);
				X = static_cast<double>(convert ? (X / settings().unit_magnitude()) : X);
				Y = static_cast<double>(convert ? (Y / settings().unit_magnitude()) : Y);
				Z = static_cast<double>(convert ? (Z / settings().unit_magnitude()) : Z);
				int i = (int) _verts.size() / 3;
				if (settings().get(ifcopenshell::geometry::settings::WELD_VERTICES)) {
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

			inline void addNormal(double X, double Y, double Z) {
				_normals.push_back(X);
				_normals.push_back(Y);
				_normals.push_back(Z);
			}

			inline void addFace(int style, int i0, int i1, int i2) {
				_faces.push_back(i0);
				_faces.push_back(i1);
				_faces.push_back(i2);

				_material_ids.push_back(style);
			}

			inline void registerEdge(int i0, int i1) {
				_edges.push_back(i0);
				_edges.push_back(i1);
			}

		private:
			Triangulation();
			Triangulation(const Triangulation&);
			Triangulation& operator=(const Triangulation&);
		};

	}
}}

#endif
