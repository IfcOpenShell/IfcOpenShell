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
 * IfcGeom::Iterator::findContext()                                             *
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

#include "../ifcparse/IfcParse.h"

#include "../ifcgeom/IfcGeom.h"
#include "../ifcgeom/IfcGeomUtils.h"
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

		// A container and iterator for IfcShapeRepresentations
		IfcSchema::IfcRepresentation::list::ptr representations;
		IfcSchema::IfcRepresentation::list::it shaperep_iterator;

		// The object is fetched beforehand to be sure that get() returns a valid element
		TriangulationElement<P>* current_triangulation;
		ShapeModelElement<P>* current_shape_model;
		SerializedElement<P>* current_serialization;
		
		// A container and iterator for IfcBuildingElements for the current IfcRepresentation referenced by *shaperep_iterator
		IfcSchema::IfcProduct::list::ptr entities;
		IfcSchema::IfcProduct::list::it ifcproduct_iterator;

		int done;
		int total;

		std::string unit_name;
		// double?
		P unit_magnitude;

		// Store references to all returned non-geometric elements to be freed when the destructor is called
		std::vector<Element<P>*> returned_elements;

		void initUnits() {
			// Set default units, set length to meters, angles to undefined
			kernel.setValue(IfcGeom::Kernel::GV_LENGTH_UNIT, 1.0);
			kernel.setValue(IfcGeom::Kernel::GV_PLANEANGLE_UNIT, -1.0);
			
			IfcSchema::IfcUnitAssignment::list::ptr unit_assignments = ifc_file->EntitiesByType<IfcSchema::IfcUnitAssignment>();
			IfcUtil::IfcAbstractSelect::list::ptr units;
			try {
				if ( unit_assignments->Size() ) {
					IfcSchema::IfcUnitAssignment* unit_assignment = *unit_assignments->begin();
					units = unit_assignment->Units();
				}
			} catch (const IfcParse::IfcException&) {}

			if (!units || !units->Size()) {
				// No units eh... Since tolerances and deflection are specified internally in meters
				// we will try to find another indication of the model size.
				IfcSchema::IfcExtrudedAreaSolid::list::ptr extrusions = ifc_file->EntitiesByType<IfcSchema::IfcExtrudedAreaSolid>();
				if ( ! extrusions->Size() ) return;
				double max_height = -1.0f;
				for ( IfcSchema::IfcExtrudedAreaSolid::list::it it = extrusions->begin(); it != extrusions->end(); ++ it ) {
					try {
						const double depth = (*it)->Depth();
						if ( depth > max_height ) max_height = depth;
					} catch (const IfcParse::IfcException&) {}
				}
				if ( max_height > 100.0f ) {
					kernel.setValue(IfcGeom::Kernel::GV_LENGTH_UNIT, 0.001);
					Logger::Message(Logger::LOG_NOTICE, "Guessed length unit to be in millimeters based on extrusion depth");
				}
				return;
			}

			try {
				for ( IfcUtil::IfcAbstractSelect::list::it it = units->begin(); it != units->end(); ++ it ) {
					std::string current_unit_name = "";
					IfcUtil::IfcAbstractSelect* base = *it;
					IfcSchema::IfcSIUnit* unit = 0;
					double value = 1.f;
					if ( base->is(IfcSchema::Type::IfcConversionBasedUnit) ) {
						IfcSchema::IfcConversionBasedUnit* u = (IfcSchema::IfcConversionBasedUnit*)base;
						current_unit_name = u->Name();
						IfcSchema::IfcMeasureWithUnit* u2 = u->ConversionFactor();
						IfcSchema::IfcUnit u3 = u2->UnitComponent();
						if ( u3->is(IfcSchema::Type::IfcSIUnit) ) {
							unit = (IfcSchema::IfcSIUnit*) u3;
						}
						IfcSchema::IfcValue v = u2->ValueComponent();
						IfcUtil::IfcArgumentSelect* v2 = (IfcUtil::IfcArgumentSelect*) v;
						const double f = *v2->wrappedValue();
						value *= f;
					} else if ( base->is(IfcSchema::Type::IfcSIUnit) ) {
						unit = (IfcSchema::IfcSIUnit*)base;
					}
					if ( unit ) {
						if ( unit->hasPrefix() ) {
							value *= IfcGeom::Utils::UnitPrefixToValue(unit->Prefix());
						}
						IfcSchema::IfcUnitEnum::IfcUnitEnum type = unit->UnitType();
						if ( type == IfcSchema::IfcUnitEnum::IfcUnit_LENGTHUNIT ) {
							kernel.setValue(IfcGeom::Kernel::GV_LENGTH_UNIT,value);
							if (current_unit_name.empty()) {
								if (unit->hasPrefix()) {
									current_unit_name = IfcSchema::IfcSIPrefix::ToString(unit->Prefix());
								}
								current_unit_name += IfcSchema::IfcSIUnitName::ToString(unit->Name());
							}
							unit_magnitude = static_cast<P>(value);
							unit_name = current_unit_name;
						} else if ( type == IfcSchema::IfcUnitEnum::IfcUnit_PLANEANGLEUNIT ) {
							kernel.setValue(IfcGeom::Kernel::GV_PLANEANGLE_UNIT, value);
						}
					}
				}
			} catch (const IfcParse::IfcException& ex) {
				std::stringstream ss;
				ss << "Failed to determine unit information '" << ex.what() << "'";
				Logger::Message(Logger::LOG_ERROR, ss.str());
			}
		}

	public:
		bool findContext() {

			try {
				initUnits();
			} catch (...) {}

			// Really this should only be 'Model', as per 
			// the standard 'Design' is deprecated. So,
			// just for backwards compatibility:
			std::set<std::string> context_types;
			context_types.insert("model");
			context_types.insert("design");
			// DDS likes to output 'model view'
			context_types.insert("model view");

			double lowest_precision_encountered = std::numeric_limits<double>::infinity();
			bool any_precision_encountered = false;

			representations = IfcSchema::IfcRepresentation::list::ptr(new IfcSchema::IfcRepresentation::list);

			IfcSchema::IfcGeometricRepresentationContext::list::it it;
			IfcSchema::IfcGeometricRepresentationSubContext::list::it jt;
			IfcSchema::IfcGeometricRepresentationContext::list::ptr contexts = 
				ifc_file->EntitiesByType<IfcSchema::IfcGeometricRepresentationContext>();

			IfcSchema::IfcGeometricRepresentationContext::list::ptr filtered_contexts (new IfcSchema::IfcGeometricRepresentationContext::list);

 			for (it = contexts->begin(); it != contexts->end(); ++it) {
				IfcSchema::IfcGeometricRepresentationContext* context = *it;
				if (context->is(IfcSchema::Type::IfcGeometricRepresentationSubContext)) {
					// Continue, as the list of subcontexts will be considered
					// by the parent's context inverse attributes.
					continue;
				}
				std::string context_type_lc = context->ContextType();
				for (std::string::iterator c = context_type_lc.begin(); c != context_type_lc.end(); ++c) {
					*c = tolower(*c);
				}
				if (context->hasContextType() && context_types.find(context_type_lc) != context_types.end()) {
					filtered_contexts->push(context);
				}
			}

			if (filtered_contexts->Size() == 0) {
				filtered_contexts = contexts;
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
				kernel.setValue(IfcGeom::Kernel::GV_PRECISION, lowest_precision_encountered);
			} else {
				kernel.setValue(IfcGeom::Kernel::GV_PRECISION, 1.e-5);
			}

			if (representations->Size() == 0) return false;

			shaperep_iterator = representations->begin();
			entities.reset();

			if (!create()) {
				return false;
			}

			done = 0;
			total = representations->Size();

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

	private:
		// Move the the next IfcRepresentation
		void _nextShape() {
			entities.reset();
			++ shaperep_iterator;
			++ done;
		}

		int _getParentId(IfcSchema::IfcProduct* ifc_product) {
			int parent_id = -1;
			// In case of an opening element, parent to the RelatingBuildingElement
			if ( ifc_product->is(IfcSchema::Type::IfcOpeningElement ) ) {
				IfcSchema::IfcOpeningElement* opening = (IfcSchema::IfcOpeningElement*)ifc_product;
				IfcSchema::IfcRelVoidsElement::list::ptr voids = opening->VoidsElements();
				if ( voids->Size() ) {
					IfcSchema::IfcRelVoidsElement* ifc_void = *voids->begin();
					parent_id = ifc_void->RelatingBuildingElement()->entity->id();
				}
			} else if ( ifc_product->is(IfcSchema::Type::IfcElement ) ) {
				IfcSchema::IfcElement* element = (IfcSchema::IfcElement*)ifc_product;
				IfcSchema::IfcRelFillsElement::list::ptr fills = element->FillsVoids();
				// Incase of a RelatedBuildingElement parent to the opening element
				if ( fills->Size() ) {
					for ( IfcSchema::IfcRelFillsElement::list::it it = fills->begin(); it != fills->end(); ++ it ) {
						IfcSchema::IfcRelFillsElement* fill = *it;
						IfcSchema::IfcObjectDefinition* ifc_objectdef = fill->RelatingOpeningElement();
						if ( ifc_product == ifc_objectdef ) continue;
						parent_id = ifc_objectdef->entity->id();
					}
				} 
				// Else simply parent to the containing structure
				if ( parent_id == -1 ) {
					IfcSchema::IfcRelContainedInSpatialStructure::list::ptr parents = element->ContainedInStructure();
					if ( parents->Size() ) {
						IfcSchema::IfcRelContainedInSpatialStructure* parent = *parents->begin();
						parent_id = parent->RelatingStructure()->entity->id();
					}
				}
			}
			// Parent decompositions to the RelatingObject
			if ( parent_id == -1 ) {
				IfcEntityList::ptr parents = ifc_product->entity->getInverse(IfcSchema::Type::IfcRelAggregates);
				parents->push(ifc_product->entity->getInverse(IfcSchema::Type::IfcRelNests));
				for ( IfcEntityList::it it = parents->begin(); it != parents->end(); ++ it ) {
					IfcSchema::IfcRelDecomposes* decompose = (IfcSchema::IfcRelDecomposes*)*it;
					IfcSchema::IfcObjectDefinition* ifc_objectdef;
		#ifdef USE_IFC4
					if (decompose->is(IfcSchema::Type::IfcRelAggregates)) {
						ifc_objectdef = ((IfcSchema::IfcRelAggregates*)decompose)->RelatingObject();
					} else {
						continue;
					}
		#else
					ifc_objectdef = decompose->RelatingObject();
		#endif
					if ( ifc_product == ifc_objectdef ) continue;
					parent_id = ifc_objectdef->entity->id();
				}
			}
			return parent_id;
		}

		ShapeModelElement<P>* create_shape_model_for_next_entity() {
			while ( true ) {
				IfcSchema::IfcRepresentation* shaperep;

				// Have we reached the end of our list of representations?
				if ( shaperep_iterator == representations->end() ) {
					representations.reset();
					return 0;
				}
				shaperep = *shaperep_iterator;

				// Has the list of IfcProducts for this representation been initialized?
				if ( ! entities ) {
					
					IfcSchema::IfcProductRepresentation::list::ptr prodreps = shaperep->OfProductRepresentation();
					entities = IfcSchema::IfcProduct::list::ptr(new IfcSchema::IfcProduct::list);
					for ( IfcSchema::IfcProductRepresentation::list::it it = prodreps->begin(); it != prodreps->end(); ++it ) {
						if ( (*it)->is(IfcSchema::Type::IfcProductDefinitionShape) ) {
							IfcSchema::IfcProductDefinitionShape* pds = (IfcSchema::IfcProductDefinitionShape*)*it;
							entities->push(pds->ShapeOfProduct());
						} else {
							// http://buildingsmart-tech.org/ifc/IFC2x3/TC1/html/ifcrepresentationresource/lexical/ifcproductrepresentation.htm
							// IFC2x Edition 3 NOTE  Users should not instantiate the entity IfcProductRepresentation from IFC2x Edition 3 onwards. 
							// It will be changed into an ABSTRACT supertype in future releases of IFC.

							// IfcProductRepresentation also lacks the INVERSE relation to IfcProduct
							// Let's find the IfcProducts that reference the IfcProductRepresentation anyway
							IfcEntityList::ptr products = (*it)->entity->getInverse(IfcSchema::Type::IfcProduct);
							for ( IfcEntityList::it it = products->begin(); it != products->end(); ++ it ) {
								entities->push((IfcSchema::IfcProduct*)*it);
							}
						}
					}
					// Does this representation have any IfcProducts?
					if ( ! entities->Size() ) {
						_nextShape();
						continue;
					}
					ifcproduct_iterator = entities->begin();
				}
				// Have we reached the end of our list of IfcProducts?
				if ( ifcproduct_iterator == entities->end() ) {
					_nextShape();
					continue;
				}
						
				IfcGeom::Representation::BRep* shape;
				IfcGeom::IfcRepresentationShapeItems shapes;

				if ( !kernel.convert_shapes(shaperep,shapes) ) {
					_nextShape();
					continue;
				}

				IfcSchema::IfcProduct* ifc_product = *ifcproduct_iterator;

				int parent_id = -1;
				try {
					parent_id = _getParentId(ifc_product);
				} catch (...) {}
		
				const std::string name = ifc_product->hasName() ? ifc_product->Name() : "";
				const std::string guid = ifc_product->GlobalId();
		
				gp_Trsf trsf;
				try {
					kernel.convert(ifc_product->ObjectPlacement(),trsf);
				} catch (...) {}

				// Does the IfcElement have any IfcOpenings?
				// Note that openings for IfcOpeningElements are not processed
				IfcSchema::IfcRelVoidsElement::list::ptr openings;
				if ( ifc_product->is(IfcSchema::Type::IfcElement) && !ifc_product->is(IfcSchema::Type::IfcOpeningElement) ) {
					IfcSchema::IfcElement* element = (IfcSchema::IfcElement*)ifc_product;
					openings = element->HasOpenings();
				}
				// Is the IfcElement a decomposition of an IfcElement with any IfcOpeningElements?
				if ( ifc_product->is(IfcSchema::Type::IfcBuildingElementPart ) ) {
					IfcSchema::IfcBuildingElementPart* part = (IfcSchema::IfcBuildingElementPart*)ifc_product;
		#ifdef USE_IFC4
					IfcSchema::IfcRelAggregates::list::ptr decomposes = part->Decomposes();
					for ( IfcSchema::IfcRelAggregates::list::it it = decomposes->begin(); it != decomposes->end(); ++ it ) {
		#else
					IfcSchema::IfcRelDecomposes::list::ptr decomposes = part->Decomposes();
					for ( IfcSchema::IfcRelDecomposes::list::it it = decomposes->begin(); it != decomposes->end(); ++ it ) {
		#endif
						IfcSchema::IfcObjectDefinition* obdef = (*it)->RelatingObject();
						if ( obdef->is(IfcSchema::Type::IfcElement) ) {
							IfcSchema::IfcElement* element = (IfcSchema::IfcElement*)obdef;
							openings->push(element->HasOpenings());
						}
					}
				}

				const std::string product_type = IfcSchema::Type::ToString(ifc_product->type());
				ElementSettings element_settings(settings, unit_magnitude, product_type);

				if ( !settings.disable_opening_subtractions() && openings && openings->Size() ) {
					IfcGeom::IfcRepresentationShapeItems opened_shapes;
					try {
						if ( settings.faster_booleans() ) {
							bool succes = kernel.convert_openings_fast(ifc_product,openings,shapes,trsf,opened_shapes);
							if ( ! succes ) {
								opened_shapes.clear();
								kernel.convert_openings(ifc_product,openings,shapes,trsf,opened_shapes);
							}
						} else {
							kernel.convert_openings(ifc_product,openings,shapes,trsf,opened_shapes);
						}
					} catch(...) { 
						Logger::Message(Logger::LOG_ERROR,"Error processing openings for:",ifc_product->entity); 
					}
					if ( settings.use_world_coords() ) {
						for ( IfcGeom::IfcRepresentationShapeItems::iterator it = opened_shapes.begin(); it != opened_shapes.end(); ++ it ) {
							it->prepend(trsf);
						}
						trsf = gp_Trsf();
					}
					shape = new IfcGeom::Representation::BRep(element_settings, shaperep->entity->id(), opened_shapes);
				} else if ( settings.use_world_coords() ) {
					for ( IfcGeom::IfcRepresentationShapeItems::iterator it = shapes.begin(); it != shapes.end(); ++ it ) {
						it->prepend(trsf);
					}
					trsf = gp_Trsf();
					shape = new IfcGeom::Representation::BRep(element_settings, shaperep->entity->id(), shapes);
				} else {
					shape = new IfcGeom::Representation::BRep(element_settings, shaperep->entity->id(), shapes);
				}

				return new ShapeModelElement<P>(
					ifc_product->entity->id(),
					parent_id,
					name, 
					product_type,
					guid,
					trsf,
					shape
				);
			}	
		}

		public:

		bool next() {
			// Free all possible representations of the current geometrical entity
			delete current_triangulation;
			current_triangulation = 0;
			
			// Increment the iterator over the list of products using the current
			// shape representation
			if (entities) {
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
				const IfcUtil::IfcBaseClass* ifc_entity = ifc_file->EntityById(id);
				instance_type = IfcSchema::Type::ToString(ifc_entity->type());
				if ( ifc_entity->is(IfcSchema::Type::IfcProduct) ) {
					IfcSchema::IfcProduct* ifc_product = (IfcSchema::IfcProduct*)ifc_entity;
					
					product_guid = ifc_product->GlobalId();
					product_name = ifc_product->hasName() ? ifc_product->Name() : "";
					
					try {
						parent_id = _getParentId(ifc_product);
					} catch (...) {}
					
					try {
						kernel.convert(ifc_product->ObjectPlacement(), trsf);
					} catch (...) {}
				}
			} catch(...) {}

			ElementSettings element_settings(settings, unit_magnitude, instance_type);
			Element<P>* ifc_object = new Element<P>(element_settings, id, parent_id, product_name, instance_type, product_guid, trsf);
			
			returned_elements.push_back(ifc_object);
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
				return false;
			}
		}
	private:
		void initialize() {
			current_triangulation = 0;
			current_shape_model = 0;
			current_serialization = 0;
		
			unit_name = "METER";
			unit_magnitude = 1.f;

			kernel.setValue(IfcGeom::Kernel::GV_MAX_FACES_TO_SEW, settings.sew_shells() ? 1000 : -1);
			kernel.setValue(IfcGeom::Kernel::GV_FORCE_CCW_FACE_ORIENTATION, settings.force_ccw_face_orientation() ? 1 : -1);
		}
	public:
		Iterator(const IteratorSettings& settings, IfcParse::IfcFile* file)
			: settings(settings)
			, ifc_file(file)
		{
			initialize();
		}
		Iterator(const IteratorSettings& settings, const std::string& filename)
			: settings(settings)
			, ifc_file(new IfcParse::IfcFile)
		{
			ifc_file->Init(filename);
			initialize();
		}
		Iterator(const IteratorSettings& settings, void* data, int length)
			: settings(settings)
			, ifc_file(new IfcParse::IfcFile)
		{
			ifc_file->Init(data, length);
			initialize();
		}
		Iterator(const IteratorSettings& settings, std::istream& filestream, int length)
			: settings(settings)
			, ifc_file(new IfcParse::IfcFile)
		{
			ifc_file->Init(filestream, length);
			initialize();
		}

		~Iterator() {
			// TODO: Correctly implement destructor for IfcFile
			delete ifc_file;

			typename std::vector<Element<P>*>::const_iterator it;
			for (it = returned_elements.begin(); it != returned_elements.end(); ++ it ) {
				delete *it;
			}

			returned_elements.clear();
		}
	};
}


#endif
