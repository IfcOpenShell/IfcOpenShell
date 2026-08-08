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

#ifdef WITH_OPENCOLLADA

#ifndef COLLADASERIALIZER_H
#define COLLADASERIALIZER_H

#ifdef _MSC_VER
#pragma warning(push)
#pragma warning(disable : 4201 4512)
#else
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wignored-qualifiers"
#endif
#include <COLLADASWStreamWriter.h>
#include <COLLADASWNode.h>
#include <COLLADASWLibraryGeometries.h>
#include <COLLADASWLibraryVisualScenes.h>
#include <COLLADASWLibraryEffects.h>
#include <COLLADASWLibraryMaterials.h>
#ifdef _MSC_VER
#pragma warning(pop)
#else
#pragma GCC diagnostic pop
#endif

#include "../ifcgeom/Iterator.h"

#include "../serializers/serializers_api.h"
#include "../ifcgeom/GeometrySerializer.h"

#include <boost/numeric/ublas/matrix.hpp>
#include <boost/numeric/ublas/io.hpp>


class SERIALIZERS_API collada_serializer : public ifcopenshell::geom::write_only_geometry_serializer
{
	// TODO The vast amount of implement details of collada_serializer could be hidden to the cpp file.
private:
	std::stack<int> parentStackId;

	class collada_exporter
	{
	private:
		class collada_geometries : public COLLADASW::LibraryGeometries
		{
			collada_geometries(const collada_geometries&); //N/A
			collada_geometries& operator =(const collada_geometries&); //N/A
		public:
			explicit collada_geometries(COLLADASW::StreamWriter& stream, collada_serializer *_serializer)
				: COLLADASW::LibraryGeometries(&stream)
                , serializer(_serializer)
			{}
            void addFloatSource(const std::string& mesh_id, const std::string& suffix,
                const std::vector<double>& floats, const char* coords = "XYZ");
            /// @todo pass simply deferred_object?
            void write(
                const std::string &mesh_id, const std::string &default_material_name,
                const std::vector<double>& positions, const std::vector<double>& normals,
                const std::vector<int>& faces, const std::vector<int>& edges,
                const std::vector<int>& material_ids, const std::vector<ifcopenshell::geom::taxonomy::style::ptr>& materials,
                const std::vector<double>& uvs, const std::vector<std::string>& material_references);
			void close();
            collada_serializer *serializer;
		};
		class collada_scene : public COLLADASW::LibraryVisualScenes
		{
		private:
			collada_scene(const collada_scene&); //N/A
			collada_scene& operator =(const collada_scene&); //N/A

			const std::string scene_id;
			bool scene_opened;
			std::stack<COLLADASW::Node*> parentNodes;
			std::stack<ifcopenshell::geom::taxonomy::matrix4> matrixStack;
		public:
			collada_scene(const std::string& scene_id, COLLADASW::StreamWriter& stream, collada_serializer *_serializer)
				: COLLADASW::LibraryVisualScenes(&stream)
				, scene_id(scene_id)
				, scene_opened(false)
                , serializer(_serializer)
			{}
			void add(const std::string& node_id, const std::string& node_name, const std::string& geom_name,
                const std::vector<std::string>& material_ids, const ifcopenshell::geom::transformation& matrix);
			void addParent(const ifcopenshell::geom::element& parent);
			void closeParent();
			COLLADASW::Node* GetDirectParent();
			void write();
            collada_serializer *serializer;
		};
		class collada_materials : public COLLADASW::LibraryMaterials
		{
			collada_materials(const collada_materials&); //N/A
			collada_materials& operator =(const collada_materials&); //N/A
		private:
			class collada_effects : public COLLADASW::LibraryEffects
			{
				collada_effects(const collada_effects&); //N/A
				collada_effects& operator =(const collada_effects&); //N/A
			public:
				explicit collada_effects(COLLADASW::StreamWriter& stream)
					: COLLADASW::LibraryEffects(&stream)
				{}
				void write(const ifcopenshell::geom::taxonomy::style::ptr& material, const std::string &material_uri);
				void close();
                collada_serializer *serializer;
			};
			std::vector<ifcopenshell::geom::taxonomy::style::ptr> materials;
			std::vector<std::string> material_uris;
		public:
			explicit collada_materials(COLLADASW::StreamWriter& stream, collada_serializer *_serializer)
				: COLLADASW::LibraryMaterials(&stream)
				, serializer(_serializer)
		                , effects(stream)
			{}
			void add(const ifcopenshell::geom::taxonomy::style::ptr& material);
			std::string getMaterialUri(const ifcopenshell::geom::taxonomy::style::ptr& material);
			bool contains(const ifcopenshell::geom::taxonomy::style::ptr& material);
			void write();
            collada_serializer *serializer;
            collada_effects effects;
		};

		class deferred_object {
		
			friend bool operator < (const deferred_object& def_obj1, const deferred_object& def_obj2) {
				size_t size = (def_obj1.parents_.size() < def_obj2.parents_.size() ? def_obj1.parents_.size() : def_obj2.parents_.size());
				size_t cpt = 0;

				// Skip the shared parents
				while (cpt < size && *(def_obj1.parents_.at(cpt)) == *(def_obj2.parents_.at(cpt))) {
					cpt++;
				}

				// If a parent list container the other one
				if (cpt >= size) {
					return def_obj1.parents_.size() < def_obj2.parents_.size();
				} else {
					return *(def_obj1.parents_.at(cpt)) < *(def_obj2.parents_.at(cpt));
				}
			}

		public:
			std::string unique_id, representation_id, type;
			ifcopenshell::geom::transformation transformation;
			std::vector<double> vertices;
			std::vector<double> normals;
			std::vector<int> faces;
			std::vector<int> edges;
			std::vector<int> material_ids;
			std::vector<ifcopenshell::geom::taxonomy::style::ptr> materials;
			std::vector<std::string> material_references;
            std::vector<double> uvs;
			std::vector<const ifcopenshell::geom::element*> parents_;

			deferred_object(const std::string& unique_id, const std::string& representation_id, const std::string& type, const ifcopenshell::geom::transformation& transformation,
				const std::vector<double>& vertices, const std::vector<double>& normals, const std::vector<int>& faces,
				const std::vector<int>& edges, const std::vector<int>& material_ids, const std::vector<ifcopenshell::geom::taxonomy::style::ptr>& materials,
				const std::vector<std::string>& material_references, const std::vector<double>& uvs)
				: unique_id(unique_id)
				, representation_id(representation_id)
				, type(type)
				, transformation(transformation)
				, vertices(vertices)
				, normals(normals)
				, faces(faces)
				, edges(edges)
				, material_ids(material_ids)
				, materials(materials)
				, material_references(material_references)
				, uvs(uvs)
			{}

			std::vector<const ifcopenshell::geom::element*>& parents() { return parents_; }
			const std::vector<const ifcopenshell::geom::element*>& parents() const { return parents_; }
		};
		COLLADABU::NativeString filename;
		COLLADASW::StreamWriter stream;
		collada_scene scene;
	public:
        /// @param double_precision Whether to use "double precision" (up to 16 decimals) or not (6 or 7 decimals).
		collada_exporter(const std::string& scene_name, const std::string& fn, collada_serializer *_serializer,
            bool double_precision)
            : filename(fn)
            , stream(COLLADASW::NativeString(filename.c_str(), COLLADASW::NativeString::ENCODING_UTF8), double_precision)
			, scene(scene_name, stream, _serializer)
			, materials(stream, _serializer)
			, geometries(stream, _serializer)
			, serializer(_serializer)
		{
        }
        collada_materials materials;
        collada_geometries geometries;
        collada_serializer *serializer;
		std::vector<deferred_object> deferreds;
		virtual ~collada_exporter() {}
		void startDocument(const std::string& unit_name, float unit_magnitude);
		void write(const ifcopenshell::geom::triangulation_element* o);
		void endDocument();
	};
	collada_exporter exporter;
	std::string unit_name;
	float unit_magnitude;
public:
    collada_serializer(const std::string& dae_filename, const ifcopenshell::geom::settings& settings, ifcopenshell::logger* logger = nullptr)
        : ifcopenshell::geom::write_only_geometry_serializer(settings, logger)
		, exporter("IfcOpenShell", dae_filename, this, settings.get<ifcopenshell::geom::settings::FloatingPointDigits>().get() >= 15)
    {
        exporter.serializer = this;
        exporter.materials.serializer = this;
        exporter.materials.effects.serializer = this;
        exporter.geometries.serializer = this;
    }
	bool ready();
	void writeHeader();
	void write(const ifcopenshell::geom::triangulation_element* o);
    void write(const ifcopenshell::geom::brep_element* /*o*/) {}
	void finalize();
	bool isTesselated() const { return true; }
	void setUnitNameAndMagnitude(const std::string& name, float magnitude) {
		unit_name = name;
		unit_magnitude = magnitude;
	}
	void setFile(ifcopenshell::file&) {}

    std::string object_id(const ifcopenshell::geom::element* o) /*override*/;

private:
    static std::string differentiateSlabTypes(const express::entity& slab);
};

#endif

#endif
