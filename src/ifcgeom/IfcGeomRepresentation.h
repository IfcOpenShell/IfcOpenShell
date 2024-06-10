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

#include "../ifcgeom/ConversionSettings.h"
#include "../ifcgeom/ConversionResult.h"

#include <map>

namespace IfcGeom {

	namespace Representation {

		class IFC_GEOM_API Representation {
			Representation(const Representation&); //N/A
			Representation& operator =(const Representation&); //N/A
		protected:
			const ifcopenshell::geometry::Settings settings_;
			const std::string entity_;
		public:
			explicit Representation(const ifcopenshell::geometry::Settings& settings, const std::string& entity)
				: settings_(settings)
				, entity_(entity)
			{}
			const ifcopenshell::geometry::Settings& settings() const { return settings_; }
			const std::string& entity() const {
				return entity_;
			}
			virtual ~Representation() {}
		};

		class IFC_GEOM_API BRep : public Representation {
		private:
			std::string id_;
			const IfcGeom::ConversionResults shapes_;
			BRep(const BRep& other);
			BRep& operator=(const BRep& other);
		public:
			BRep(const ifcopenshell::geometry::Settings& settings, const std::string& entity, const std::string& id, const IfcGeom::ConversionResults& shapes)
				: Representation(settings, entity)
				, id_(id)
				, shapes_(shapes)
			{}
			virtual ~BRep() {}
			IfcGeom::ConversionResults::const_iterator begin() const { return shapes_.begin(); }
			IfcGeom::ConversionResults::const_iterator end() const { return shapes_.end(); }
			const IfcGeom::ConversionResults& shapes() const { return shapes_; }
			const std::string& id() const { return id_; }
			IfcGeom::ConversionResultShape* as_compound(bool force_meters = false) const;

			bool calculate_volume(double&) const;
			bool calculate_surface_area(double&) const;
			bool calculate_projected_surface_area(const ifcopenshell::geometry::taxonomy::matrix4& ax, double& along_x, double& along_y, double& along_z) const;

			int size() const { return (int) shapes_.size(); }
			const IfcGeom::ConversionResultShape* item(int i) const;
			int item_id(int i) const;
		};

		class IFC_GEOM_API Serialization : public Representation  {
		private:
			std::string id_;
			std::string brep_data_;
			std::vector<double> surface_styles_;
			std::vector<int> surface_style_ids_;
		public:
			const std::string& brep_data() const { return brep_data_; }
			const std::vector<double>& surface_styles() const { return surface_styles_; }
			const std::vector<int>& surface_style_ids() const { return surface_style_ids_; }
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
			// A tuple of <item, material, x, y, z> to store as a key in a map.
			typedef typename std::tuple<int, int, double, double, double> VertexKey;
			typedef std::map<VertexKey, int> VertexKeyMap;
			typedef std::pair<int, int> Edge;

			std::string id_;
			std::vector<double> _verts;
			std::vector<int> _faces;
			std::vector<int> _edges;
			std::vector<double> _normals;
			std::vector<double> uvs_;
			std::vector<int> _material_ids;
			std::vector<ifcopenshell::geometry::taxonomy::style::ptr> _materials;
			std::vector<int> _item_ids;
			size_t weld_offset_;
			VertexKeyMap welds;

			Triangulation(const ifcopenshell::geometry::Settings& settings, const std::string& entity)
				: Representation(settings, entity)
				, weld_offset_(0)
				{}

		public:
			const std::string& id() const { return id_; }
			const std::vector<double>& verts() const { return _verts; }
			const std::vector<int>& faces() const { return _faces; }
			const std::vector<int>& edges() const { return _edges; }
			const std::vector<double>& normals() const { return _normals; }
			std::vector<double>& uvs() { return uvs_; }
			const std::vector<double>& uvs() const { return uvs_; }
			const std::vector<int>& material_ids() const { return _material_ids; }
			const std::vector<ifcopenshell::geometry::taxonomy::style::ptr>& materials() const { return _materials; }
			const std::vector<int>& item_ids() const { return _item_ids; }

			Triangulation(const BRep& shape_model);

			Triangulation(
				const ifcopenshell::geometry::Settings& settings,
				const std::string& entity,
				const std::string& id,
				const std::vector<double>& verts,
				const std::vector<int>& faces,
				const std::vector<int>& edges,
				const std::vector<double>& normals,
				const std::vector<double>& uvs,
				const std::vector<int>& material_ids,
				const std::vector<ifcopenshell::geometry::taxonomy::style::ptr>& materials,
				const std::vector<int>& item_ids
			)
				: Representation(settings, entity)
				, id_(id)
				, _verts(verts)
				, _faces(faces)
				, _edges(edges)
				, _normals(normals)
				, uvs_(uvs)
				, _material_ids(material_ids)
				, _materials(materials)
				, _item_ids(item_ids)
			{}

			virtual ~Triangulation() {}

            /// Generates UVs for a single mesh using box projection.
            /// @todo Very simple impl. Assumes that input vertices and normals match 1:1.
			static std::vector<double> box_project_uvs(const std::vector<double> &vertices, const std::vector<double> &normals);

			static Triangulation* empty(const ifcopenshell::geometry::Settings& settings) { return new Triangulation(settings, ""); }

			/// Welds vertices that belong to different faces
			int addVertex(int item_index, int material_index, double X, double Y, double Z);

			void addNormal(double X, double Y, double Z) {
				_normals.push_back(X);
				_normals.push_back(Y);
				_normals.push_back(Z);
			}

			void addFace(int item_id, int style, int i0, int i1, int i2) {
				_faces.push_back(i0);
				_faces.push_back(i1);
				_faces.push_back(i2);

				_item_ids.push_back(item_id);
				_material_ids.push_back(style);
			}

			void addEdge(int style, int i0, int i1) {
				_edges.push_back(i0);
				_edges.push_back(i1);

				_material_ids.push_back(style);
			}

			void registerEdge(int i0, int i1) {
				_edges.push_back(i0);
				_edges.push_back(i1);
			}

			void addEdge(int n1, int n2, std::map<std::pair<int, int>, int>& edgecount);

			void resetWelds() {
				weld_offset_ += welds.size();
				welds.clear();
			}

		private:
			Triangulation();
			Triangulation(const Triangulation&);
			Triangulation& operator=(const Triangulation&);
		};

	}
}

#endif
