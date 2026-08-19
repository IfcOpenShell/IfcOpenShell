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

#include "../ifcgeom/conversion_settings.h"
#include "../ifcgeom/conversion_result.h"

#include <map>

namespace ifcopenshell::geom {

		class IFC_GEOM_API representation {
			representation(const representation&); //N/A
			representation& operator =(const representation&); //N/A
		protected:
			const ifcopenshell::geom::settings settings_;
			const std::string entity_;
			std::string id_;
		public:
			explicit representation(const ifcopenshell::geom::settings& settings, const std::string& entity, const std::string& id)
				: settings_(settings)
				, entity_(entity)
				, id_(id)
			{}
			const ifcopenshell::geom::settings& settings() const { return settings_; }
			const std::string& entity() const {
				return entity_;
			}
			// id starts with representation id and then it may have the following dash separated elements:
			// - layerset-layerset_id
			// - material-material_id
			// - openings-opening0_id-...-openingN_id
			const std::string& id() const { return id_; }
			virtual ~representation() {}
		};

		class IFC_GEOM_API native : public representation {
		private:
			const std::vector<ifcopenshell::geom::conversion_result> shapes_;
			native(const native& other);
			native& operator=(const native& other);
		public:
			native(const ifcopenshell::geom::settings& settings, const std::string& entity, const std::string& id, const std::vector<ifcopenshell::geom::conversion_result>& shapes)
				: representation(settings, entity, id)
				, shapes_(shapes)
			{}
			virtual ~native() {}
			std::vector<ifcopenshell::geom::conversion_result>::const_iterator begin() const { return shapes_.begin(); }
			std::vector<ifcopenshell::geom::conversion_result>::const_iterator end() const { return shapes_.end(); }
			const std::vector<ifcopenshell::geom::conversion_result>& shapes() const { return shapes_; }
			ifcopenshell::geom::conversion_result_shape* as_compound(bool force_meters = false) const;

			bool calculate_volume(double&) const;
			bool calculate_surface_area(double&) const;
			bool calculate_projected_surface_area(const ifcopenshell::geom::taxonomy::matrix4::ptr& ax, double& along_x, double& along_y, double& along_z) const;

			int size() const { return (int) shapes_.size(); }
			const ifcopenshell::geom::conversion_result_shape* item(int i) const;
			int item_id(int i) const;
		};

		class IFC_GEOM_API serialization : public representation  {
		private:
			std::string brep_data_;
			std::vector<double> surface_styles_;
			std::vector<int> surface_style_ids_;
		public:
			const std::string& brep_data() const { return brep_data_; }
			const std::vector<double>& surface_styles() const { return surface_styles_; }
			const std::vector<int>& surface_style_ids() const { return surface_style_ids_; }
			serialization(const native& native_geometry);
			virtual ~serialization() {}
		private:
			serialization();
			serialization(const serialization&);
			serialization& operator=(const serialization&);
		};

		class triangulation : public representation {
		private:
			// A tuple of <item, material, x, y, z> to store as a key in a map.
			typedef typename std::tuple<int, int, double, double, double> vertex_key;
			typedef std::map<vertex_key, int> vertex_key_map;
			typedef std::pair<int, int> edge;

			std::vector<double> verts_;

			// @nb only one of these is populated based on settings, we didn't want to go
			// all in with templates or subtypes because of reduced ease of use.
			std::vector<int> faces_;
			std::vector<std::vector<int>> polyhedral_faces_without_holes_;
			std::vector<std::vector<std::vector<int>>> polyhedral_faces_with_holes_;

			std::vector<int> edges_;
			std::vector<double> normals_;
			std::vector<double> uvs_;
			std::vector<int> material_ids_;
			std::vector<ifcopenshell::geom::taxonomy::style::ptr> materials_;
			std::vector<int> item_ids_;
			std::vector<int> edges_item_ids_;
			size_t weld_offset_;
			vertex_key_map welds;

			triangulation(const ifcopenshell::geom::settings& settings, const std::string& entity,  const std::string& id)
				: representation(settings, entity, id)
				, weld_offset_(0)
				{}

		public:
			const std::vector<double>& verts() const { return verts_; }
			const std::vector<int>& faces() const { return faces_; }
			const std::vector<std::vector<int>>& polyhedral_faces_without_holes() const { return polyhedral_faces_without_holes_; }
			const std::vector<std::vector<std::vector<int>>>& polyhedral_faces_with_holes() const { return polyhedral_faces_with_holes_; }
			const std::vector<int>& edges() const { return edges_; }
			const std::vector<double>& normals() const { return normals_; }
			const std::vector<double>& uvs() const { return uvs_; }
			std::vector<double>& uvs_ref() { return uvs_; }
			const std::vector<int>& material_ids() const { return material_ids_; }
			const std::vector<ifcopenshell::geom::taxonomy::style::ptr>& materials() const { return materials_; }
			const std::vector<int>& item_ids() const { return item_ids_; }
			const std::vector<int>& edges_item_ids() const { return edges_item_ids_; }

			triangulation(const native& shape_model);

			triangulation(
				const ifcopenshell::geom::settings& settings,
				const std::string& entity,
				const std::string& id,
				const std::vector<double>& verts,
				const std::vector<int>& faces,
				const std::vector<int>& edges,
				const std::vector<double>& normals,
				const std::vector<double>& uvs,
				const std::vector<int>& material_ids,
				const std::vector<ifcopenshell::geom::taxonomy::style::ptr>& materials,
				const std::vector<int>& item_ids
				, const std::vector<int>& edges_item_ids
			)
				: representation(settings, entity, id)
				, verts_(verts)
				, faces_(faces)
				, edges_(edges)
				, normals_(normals)
				, uvs_(uvs)
				, material_ids_(material_ids)
				, materials_(materials)
				, item_ids_(item_ids)
				, edges_item_ids_(edges_item_ids)
			{}

			virtual ~triangulation() {}

            /// Generates UVs for a single mesh using box projection.
            /// @todo Very simple impl. Assumes that input vertices and normals match 1:1.
			static std::vector<double> box_project_uvs(const std::vector<double> &vertices, const std::vector<double> &normals);

			static triangulation* empty(const ifcopenshell::geom::settings& settings) { return new triangulation(settings, "", ""); }

			/// Welds vertices that belong to different faces
			int addVertex(int item_index, int material_index, double X, double Y, double Z);

			void addNormal(double X, double Y, double Z) {
				normals_.push_back(X);
				normals_.push_back(Y);
				normals_.push_back(Z);
			}

			void addFace(int item_id, int style, int i0, int i1, int i2) {
				faces_.push_back(i0);
				faces_.push_back(i1);
				faces_.push_back(i2);

				item_ids_.push_back(item_id);
				material_ids_.push_back(style);
			}

			void addFace(int item_id, int style, const std::vector<int>& outer_bound) {
				polyhedral_faces_without_holes_.push_back(outer_bound);

				item_ids_.push_back(item_id);
				material_ids_.push_back(style);
			}

			void addFace(int item_id, int style, const std::vector<std::vector<int>>& bounds) {
				polyhedral_faces_with_holes_.push_back(bounds);

				item_ids_.push_back(item_id);
				material_ids_.push_back(style);
			}

			void addEdge(int item_id, int style, int i0, int i1) {
				edges_.push_back(i0);
				edges_.push_back(i1);

				material_ids_.push_back(style);
				edges_item_ids_.push_back(item_id);
			}

			void registerEdge(int item_id, int i0, int i1) {
				edges_.push_back(i0);
				edges_.push_back(i1);
				edges_item_ids_.push_back(item_id);
			}

			void registerEdgeCount(int n1, int n2, std::map<std::pair<int, int>, int>& edgecount);

			void resetWelds() {
				weld_offset_ += welds.size();
				welds.clear();
			}

		private:
			triangulation();
			triangulation(const triangulation&);
			triangulation& operator=(const triangulation&);
		};

}

#endif
