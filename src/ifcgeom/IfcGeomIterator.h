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

/********************************************************************************
 *                                                                              *
 * Geometrical data in an IFC file consists of shapes (IfcShapeRepresentation)  *
 * and instances (SUBTYPE OF IfcBuildingElement e.g. IfcWindow).                *
 *                                                                              *
 * IfcGeom::Representation::Triangulation is a class that represents a          *
 * triangulated IfcShapeRepresentation.                                         *
 *   Triangulation.verts is a 1 dimensional vector of float defining the        *
 *      cartesian coordinates of the vertices of the triangulated shape in the  *
 *      format of [x1,y1,z1,..,xn,yn,zn]                                        *
 *   Triangulation.faces is a 1 dimensional vector of int containing the        *
 *     indices of the triangles referencing positions in Triangulation.verts    *
 *   Triangulation.edges is a 1 dimensional vector of int in {0,1} that dictates*
 *	   the visibility of the edges that span the faces in Triangulation.faces   *
 *                                                                              *
 * IfcGeom::Element represents the actual IfcBuildingElements.                  *
 *   IfcGeomObject.name is the GUID of the element                              *
 *   IfcGeomObject.type is the datatype of the element e.g. IfcWindow           *
 *   IfcGeomObject.mesh is a pointer to an IfcMesh                              *
 *   IfcGeomObject.transformation.matrix is a 4x3 matrix that defines the       *
 *     orientation and translation of the mesh in relation to the world origin  *
 *                                                                              *
 * IfcGeom::Iterator::initialize()                                              *
 *   finds the most suitable representation contexts. Returns true iff          *
 *   at least a single representation will process successfully                 *
 *                                                                              *
 * IfcGeom::Iterator::get()                                                     *
 *   returns a pointer to the current IfcGeom::Element                          *
 *                                                                              * 
 * IfcGeom::Iterator::next()                                                    *
 *   returns true iff a following entity is available for a successive call to  *
 *   IfcGeom::Iterator::get()                                                   *
 *                                                                              *
 * IfcGeom::Iterator::progress()                                                *
 *   returns an int in [0..100] that indicates the overall progress             *
 *                                                                              *
 ********************************************************************************/

#ifndef IFCGEOMITERATOR_H
#define IFCGEOMITERATOR_H

#include <map>
#include <set>
#include <vector>
#include <limits>
#include <algorithm>

#include <gp_Mat.hxx>
#include <gp_Mat2d.hxx>
#include <gp_GTrsf.hxx>
#include <gp_GTrsf2d.hxx>
#include <gp_Trsf.hxx>
#include <gp_Trsf2d.hxx>

#include "../ifcparse/IfcFile.h"

#include "../ifcgeom/IfcGeom.h"
#include "../ifcgeom/IfcGeomElement.h"
#include "../ifcgeom/IfcGeomMaterial.h"
#include "../ifcgeom/IfcGeomIteratorSettings.h"
#include "../ifcgeom/IfcRepresentationShapeItem.h"

namespace IfcGeom {
	
	template <typename P>
	class Iterator {
	private:
		Kernel kernel;
		IteratorSettings settings;

		IfcParse::IfcFile* ifc_file;

		// A container and iterator for IfcRepresentations
		IfcSchema::IfcRepresentation::list::ptr representations;
		IfcSchema::IfcRepresentation::list::it representation_iterator;

		// The object is fetched beforehand to be sure that get() returns a valid element
		TriangulationElement<P>* current_triangulation;
		BRepElement<P>* current_shape_model;
		SerializedElement<P>* current_serialization;
		
		// A container and iterator for IfcBuildingElements for the current IfcRepresentation referenced by *representation_iterator
		IfcSchema::IfcProduct::list::ptr ifcproducts;
		IfcSchema::IfcProduct::list::it ifcproduct_iterator;

		int done;
		int total;

		std::string unit_name;
		// double?
		P unit_magnitude;

		void initUnits() {
			IfcSchema::IfcProject::list::ptr projects = ifc_file->entitiesByType<IfcSchema::IfcProject>();
			if (projects->size() == 1) {
				IfcSchema::IfcProject* project = *projects->begin();
				std::pair<std::string, double> length_unit = kernel.initializeUnits(project->UnitsInContext());
				unit_name = length_unit.first;
				unit_magnitude = static_cast<P>(length_unit.second);
			}
		}

		std::set<IfcSchema::Type::Enum> entities_to_include_or_exclude;
		bool include_entities_in_processing;

		void populate_set(const std::set<std::string>& include_or_ignore) {
			entities_to_include_or_exclude.clear();
			for (std::set<std::string>::const_iterator it = include_or_ignore.begin(); it != include_or_ignore.end(); ++it) {
				std::string uppercase_type = *it;
				for (std::string::iterator c = uppercase_type.begin(); c != uppercase_type.end(); ++c) {
					*c = toupper(*c);
				}
				IfcSchema::Type::Enum ty;
				try {
					ty = IfcSchema::Type::FromString(uppercase_type);
				} catch (const IfcParse::IfcException&) {
					std::stringstream ss;
					ss << "'" << *it << "' does not name a valid IFC entity";
					throw IfcParse::IfcException(ss.str());
				}
				entities_to_include_or_exclude.insert(ty);
				// TODO: Add child classes so that containment in set can be in O(log n)
			}
		}

	public:
		bool initialize() {
			try {
				initUnits();
			} catch (...) {}

			std::set<std::string> context_types;
			if (!settings.exclude_solids_and_surfaces()) {
				// Really this should only be 'Model', as per 
				// the standard 'Design' is deprecated. So,
				// just for backwards compatibility:
				context_types.insert("model");
				context_types.insert("design");
				// DDS likes to output 'model view'
				context_types.insert("model view");
			}
			if (settings.include_curves()) {
				context_types.insert("plan");
			}			

			double lowest_precision_encountered = std::numeric_limits<double>::infinity();
			bool any_precision_encountered = false;

			representations = IfcSchema::IfcRepresentation::list::ptr(new IfcSchema::IfcRepresentation::list);

			IfcSchema::IfcGeometricRepresentationContext::list::it it;
			IfcSchema::IfcGeometricRepresentationSubContext::list::it jt;
			IfcSchema::IfcGeometricRepresentationContext::list::ptr contexts = 
				ifc_file->entitiesByType<IfcSchema::IfcGeometricRepresentationContext>();

			IfcSchema::IfcGeometricRepresentationContext::list::ptr filtered_contexts (new IfcSchema::IfcGeometricRepresentationContext::list);

 			for (it = contexts->begin(); it != contexts->end(); ++it) {
				IfcSchema::IfcGeometricRepresentationContext* context = *it;
				if (context->is(IfcSchema::Type::IfcGeometricRepresentationSubContext)) {
					// Continue, as the list of subcontexts will be considered
					// by the parent's context inverse attributes.
					continue;
				}
				if (context->hasContextType()) {
					std::string context_type_lc = context->ContextType();
					for (std::string::iterator c = context_type_lc.begin(); c != context_type_lc.end(); ++c) {
						*c = tolower(*c);
					}
					if (context_types.find(context_type_lc) != context_types.end()) {
						filtered_contexts->push(context);
					}
				}
			}

			// In case no contexts are identified based on their ContextType, all contexts are
			// considered. Note that sub contexts are excluded as they are considered later on.
			if (filtered_contexts->size() == 0) {
				for (it = contexts->begin(); it != contexts->end(); ++it) {
					IfcSchema::IfcGeometricRepresentationContext* context = *it;
					if (!context->is(IfcSchema::Type::IfcGeometricRepresentationSubContext)) {
						filtered_contexts->push(context);
					}
				}
			}

			for (it = filtered_contexts->begin(); it != filtered_contexts->end(); ++it) {
				IfcSchema::IfcGeometricRepresentationContext* context = *it;

				representations->push(context->RepresentationsInContext());
				if (context->hasPrecision() && context->Precision() < lowest_precision_encountered) {
					lowest_precision_encountered = context->Precision();
					any_precision_encountered = true;
				}
				IfcSchema::IfcGeometricRepresentationSubContext::list::ptr sub_contexts = context->HasSubContexts();
				for (jt = sub_contexts->begin(); jt != sub_contexts->end(); ++jt) {
					representations->push((*jt)->RepresentationsInContext());
				}
				// There is no need for full recursion as the following is governed by the schema:
				// WR31: The parent context shall not be another geometric representation sub context. 
			}

			if (any_precision_encountered) {
				// Some arbitrary factor that has proven to work better for the models in the set of test files.
				lowest_precision_encountered *= 10.;

				lowest_precision_encountered *= unit_magnitude;
				if (lowest_precision_encountered < 1.e-7) {
					Logger::Message(Logger::LOG_WARNING, "Precision lower than 0.0000001 meter not enforced");
					kernel.setValue(IfcGeom::Kernel::GV_PRECISION, 1.e-7);
				} else {
					kernel.setValue(IfcGeom::Kernel::GV_PRECISION, lowest_precision_encountered);
				}
			} else {
				kernel.setValue(IfcGeom::Kernel::GV_PRECISION, 1.e-5);
			}

			if (representations->size() == 0) return false;

			representation_iterator = representations->begin();
			ifcproducts.reset();

			if (!create()) {
				return false;
			}

			done = 0;
			total = representations->size();

			return true;
		}

		int progress() {
			return 100 * done / total;
		}

		const std::string& getUnitName() {
			return unit_name;
		}

		const P getUnitMagnitude() {
			return unit_magnitude;
		}
	
		const std::string getLog() {
			return Logger::GetLog();
		}

		IfcParse::IfcFile* getFile() {
			return ifc_file;
		}

		void includeEntities(const std::set<std::string>& entities) {
			populate_set(entities);
			include_entities_in_processing = true;
		}

		void excludeEntities(const std::set<std::string>& entities) {
			populate_set(entities);
			include_entities_in_processing = false;
		}

	private:
		// Move to the next IfcRepresentation
		void _nextShape() {
			ifcproducts.reset();
			++ representation_iterator;
			++ done;
		}

		BRepElement<P>* create_shape_model_for_next_entity() {
			while ( true ) {
				IfcSchema::IfcRepresentation* representation;

				// Have we reached the end of our list of representations?
				if ( representation_iterator == representations->end() ) {
					representations.reset();
					return 0;
				}
				representation = *representation_iterator;

				// Has the list of IfcProducts for this representation been initialized?
				if (!ifcproducts) {
					
					IfcSchema::IfcProductRepresentation::list::ptr prodreps = representation->OfProductRepresentation();
					ifcproducts = IfcSchema::IfcProduct::list::ptr(new IfcSchema::IfcProduct::list);
					IfcSchema::IfcProduct::list::ptr unfiltered_products(new IfcSchema::IfcProduct::list);

					for ( IfcSchema::IfcProductRepresentation::list::it it = prodreps->begin(); it != prodreps->end(); ++it ) {
						if ( (*it)->is(IfcSchema::Type::IfcProductDefinitionShape) ) {
							IfcSchema::IfcProductDefinitionShape* pds = (IfcSchema::IfcProductDefinitionShape*)*it;
							unfiltered_products->push(pds->ShapeOfProduct());
						} else {
							// http://buildingsmart-tech.org/ifc/IFC2x3/TC1/html/ifcrepresentationresource/lexical/ifcproductrepresentation.htm
							// IFC2x Edition 3 NOTE  Users should not instantiate the entity IfcProductRepresentation from IFC2x Edition 3 onwards. 
							// It will be changed into an ABSTRACT supertype in future releases of IFC.

							// IfcProductRepresentation also lacks the INVERSE relation to IfcProduct
							// Let's find the IfcProducts that reference the IfcProductRepresentation anyway
							unfiltered_products->push((*it)->entity->getInverse(IfcSchema::Type::IfcProduct, -1)->as<IfcSchema::IfcProduct>());
						}

						// Filter the products based on the set of entities being included or excluded for
						// processing. The set is iterated over te able to filter on subtypes.
						for ( IfcSchema::IfcProduct::list::it it = unfiltered_products->begin(); it != unfiltered_products->end(); ++it ) {
							bool found = false;
							for (std::set<IfcSchema::Type::Enum>::const_iterator jt = entities_to_include_or_exclude.begin(); jt != entities_to_include_or_exclude.end(); ++jt) {
								if ((*it)->is(*jt)) {
									found = true;
									break;
								}
							}
							if (found == include_entities_in_processing) {
								ifcproducts->push(*it);
							}
						}

					}
					// Does this representation have any IfcProducts?
					if (!ifcproducts->size()) {
						_nextShape();
						continue;
					}
					ifcproduct_iterator = ifcproducts->begin();
				}
				// Have we reached the end of our list of IfcProducts?
				if ( ifcproduct_iterator == ifcproducts->end() ) {
					_nextShape();
					continue;
				}

				IfcSchema::IfcProduct* product = *ifcproduct_iterator;

				BRepElement<P>* element = kernel.create_brep_for_representation_and_product<P>(settings, representation, product);

				if ( !element ) {
					_nextShape();
					continue;
				}

				return element;
			}	
		}

		public:

		bool next() {
			// Free all possible representations of the current geometrical entity
			delete current_triangulation;
			current_triangulation = 0;
			delete current_serialization;
			current_serialization = 0;
			delete current_shape_model;
			current_shape_model = 0;
			
			// Increment the iterator over the list of products using the current
			// shape representation
			if (ifcproducts) {
				++ifcproduct_iterator;
			}

			return create();
		}

		Element<P>* get() {
			// TODO: Test settings and throw
			if (current_triangulation) return current_triangulation;
			else if (current_serialization) return current_serialization;
			else if (current_shape_model) return current_shape_model;
			else return 0;
		}

		const Element<P>* getObject(int id) {

			gp_Trsf trsf;
			int parent_id = -1;
			std::string instance_type, product_name, product_guid;
			
			try {
				const IfcUtil::IfcBaseClass* ifc_entity = ifc_file->entityById(id);
				instance_type = IfcSchema::Type::ToString(ifc_entity->type());
				if ( ifc_entity->is(IfcSchema::Type::IfcProduct) ) {
					IfcSchema::IfcProduct* ifc_product = (IfcSchema::IfcProduct*)ifc_entity;
					
					product_guid = ifc_product->GlobalId();
					product_name = ifc_product->hasName() ? ifc_product->Name() : "";
					
					parent_id = -1;
					try {
						IfcSchema::IfcObjectDefinition* parent_object = kernel.get_decomposing_entity(ifc_product);
						if (parent_object) {
							parent_id = parent_object->entity->id();
						}
					} catch (...) {}
					
					try {
						kernel.convert(ifc_product->ObjectPlacement(), trsf);
					} catch (...) {}
				}
			} catch(...) {}

			ElementSettings element_settings(settings, unit_magnitude, instance_type);
			Element<P>* ifc_object = new Element<P>(element_settings, id, parent_id, product_name, instance_type, product_guid, "", trsf);
			
			return ifc_object;
		}

		bool create() {
			try {
				current_shape_model = create_shape_model_for_next_entity();
			} catch (...) {}
			if (!current_shape_model) return false;
			if (settings.use_brep_data()) {
				try {
					current_serialization = new SerializedElement<P>(*current_shape_model);
				} catch (...) {}
				return !!current_serialization;
			} else if (!settings.disable_triangulation()) {
				try {
					current_triangulation = new TriangulationElement<P>(*current_shape_model);
				} catch (...) {}
				return !!current_triangulation;
			} else {
				return true;
			}
		}
	private:
		void _initialize() {
			current_triangulation = 0;
			current_shape_model = 0;
			current_serialization = 0;

			// Upon initialisation, the (empty) set of entity names,
			// should be excluded, or no products would be processed.
			include_entities_in_processing = false;
		
			unit_name = "METER";
			unit_magnitude = 1.f;

			kernel.setValue(IfcGeom::Kernel::GV_MAX_FACES_TO_SEW, settings.sew_shells() ? 1000 : -1);
			kernel.setValue(IfcGeom::Kernel::GV_DIMENSIONALITY, (settings.include_curves() ? (settings.exclude_solids_and_surfaces() ? -1. : 0.) : +1.));
		}

		bool owns_ifc_file;
	public:
		Iterator(const IteratorSettings& settings, IfcParse::IfcFile* file)
			: settings(settings)
			, ifc_file(file)
			, owns_ifc_file(false)
		{
			_initialize();
		}
		Iterator(const IteratorSettings& settings, const std::string& filename)
			: settings(settings)
			, ifc_file(new IfcParse::IfcFile)
			, owns_ifc_file(true)
		{
			ifc_file->Init(filename);
			_initialize();
		}
		Iterator(const IteratorSettings& settings, void* data, int length)
			: settings(settings)
			, ifc_file(new IfcParse::IfcFile)
			, owns_ifc_file(true)
		{
			ifc_file->Init(data, length);
			_initialize();
		}
		Iterator(const IteratorSettings& settings, std::istream& filestream, int length)
			: settings(settings)
			, ifc_file(new IfcParse::IfcFile)
			, owns_ifc_file(true)
		{
			ifc_file->Init(filestream, length);
			_initialize();
		}

		~Iterator() {
			if (owns_ifc_file) {
				delete ifc_file;
			}

			delete current_triangulation;
			current_triangulation = 0;
			delete current_serialization;
			current_serialization = 0;
			delete current_shape_model;
			current_shape_model = 0;
		}
	};
}

#endif
