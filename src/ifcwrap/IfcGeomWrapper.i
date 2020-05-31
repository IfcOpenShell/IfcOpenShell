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

%rename("settings") IteratorSettings;

// This is only used for RGB colours, hence the size of 3
%typemap(out) const double* {
	$result = PyTuple_New(3);
	for (int i = 0; i < 3; ++i) {
		PyTuple_SetItem($result, i, PyFloat_FromDouble($1[i]));
	}
}

// SWIG does not support bool references in a meaningful way, so the
// IfcGeom::IteratorSettings functions degrade to return a read only value
%typemap(out) double& {
	$result = SWIG_From_double(*$1);
}
%typemap(out) bool& {
	$result = PyBool_FromLong(static_cast<long>(*$1));
}

%ignore IfcGeom::impl::tree::selector;

%include "../ifcgeom/ifc_geom_api.h"
%include "../ifcgeom/IfcGeomIteratorSettings.h"
%include "../ifcgeom/IfcGeomElement.h"
%include "../ifcgeom_schema_agnostic/IfcGeomMaterial.h"
%include "../ifcgeom/IfcGeomRepresentation.h"
%include "../ifcgeom_schema_agnostic/IfcGeomIterator.h"

// A Template instantantation should be defined before it is used as a base class. 
// But frankly I don't care as most methods are subtlely different anyway.
%include "../ifcgeom/IfcGeomTree.h"

%extend IfcGeom::tree {

	static IfcEntityList::ptr vector_to_list(const std::vector<IfcUtil::IfcBaseEntity*>& ps) {
		IfcEntityList::ptr r(new IfcEntityList);
		for (std::vector<IfcUtil::IfcBaseEntity*>::const_iterator it = ps.begin(); it != ps.end(); ++it) {
			r->push(*it);
		}
		return r;
	}

	IfcEntityList::ptr select_box(IfcUtil::IfcBaseClass* e, bool completely_within = false, double extend=-1.e-5) const {
		if (!e->declaration().is("IfcProduct")) {
			throw IfcParse::IfcException("Instance should be an IfcProduct");
		}
		std::vector<IfcUtil::IfcBaseEntity*> ps = $self->select_box((IfcUtil::IfcBaseEntity*)e, completely_within, extend);
		return IfcGeom_tree_vector_to_list(ps);
	}

	IfcEntityList::ptr select_box(const gp_Pnt& p) const {
		std::vector<IfcUtil::IfcBaseEntity*> ps = $self->select_box(p);
		return IfcGeom_tree_vector_to_list(ps);
	}

	IfcEntityList::ptr select_box(const Bnd_Box& b, bool completely_within = false) const {
		std::vector<IfcUtil::IfcBaseEntity*> ps = $self->select_box(b, completely_within);
		return IfcGeom_tree_vector_to_list(ps);
	}

	IfcEntityList::ptr select(IfcUtil::IfcBaseClass* e, bool completely_within = false) const {
		if (!e->declaration().is("IfcProduct")) {
			throw IfcParse::IfcException("Instance should be an IfcProduct");
		}
		std::vector<IfcUtil::IfcBaseEntity*> ps = $self->select((IfcUtil::IfcBaseEntity*)e, completely_within);
		return IfcGeom_tree_vector_to_list(ps);
	}

	IfcEntityList::ptr select(const gp_Pnt& p) const {
		std::vector<IfcUtil::IfcBaseEntity*> ps = $self->select(p);
		return IfcGeom_tree_vector_to_list(ps);
	}

	IfcEntityList::ptr select(const std::string& shape_serialization) const {
		std::stringstream stream(shape_serialization);
		BRepTools_ShapeSet shapes;
		shapes.Read(stream);
		const TopoDS_Shape& shp = shapes.Shape(shapes.NbShapes());

		std::vector<IfcUtil::IfcBaseEntity*> ps = $self->select(shp);
		return IfcGeom_tree_vector_to_list(ps);
	}

}

// Using RTTI return a more specialized type of Element
// Note that these elements are not to be owned by SWIG/Python as they will be freed automatically upon the next iteration
// except for the IfcGeom::Element instances which are returned by Iterator::getObject() calls
%typemap(out) IfcGeom::Element<double>* {
	IfcGeom::SerializedElement<double>* serialized_elem = dynamic_cast<IfcGeom::SerializedElement<double>*>($1);
	IfcGeom::TriangulationElement<double>* triangulation_elem = dynamic_cast<IfcGeom::TriangulationElement<double>*>($1);
	if (triangulation_elem) {
		$result = SWIG_NewPointerObj(SWIG_as_voidptr(triangulation_elem), SWIGTYPE_p_IfcGeom__TriangulationElementT_double_double_t, 0);
	} else if (serialized_elem) {
		$result = SWIG_NewPointerObj(SWIG_as_voidptr(serialized_elem), SWIGTYPE_p_IfcGeom__SerializedElementT_double_double_t, 0);
	} else {
		$result = SWIG_NewPointerObj(SWIG_as_voidptr($1), SWIGTYPE_p_IfcGeom__ElementT_double_double_t, SWIG_POINTER_OWN);
	}
}

// A visitor
%{
struct ShapeRTTI : public boost::static_visitor<PyObject*>
{
    PyObject* operator()(IfcGeom::Element<double>* elem) const {
		IfcGeom::SerializedElement<double>* serialized_elem = dynamic_cast<IfcGeom::SerializedElement<double>*>(elem);
		IfcGeom::TriangulationElement<double>* triangulation_elem = dynamic_cast<IfcGeom::TriangulationElement<double>*>(elem);
		if (triangulation_elem) {
			return SWIG_NewPointerObj(SWIG_as_voidptr(triangulation_elem), SWIGTYPE_p_IfcGeom__TriangulationElementT_double_double_t, SWIG_POINTER_OWN);
		} else if (serialized_elem) {
			return SWIG_NewPointerObj(SWIG_as_voidptr(serialized_elem), SWIGTYPE_p_IfcGeom__SerializedElementT_double_double_t, SWIG_POINTER_OWN);
		} else {
			throw std::runtime_error("Invalid element encountered");
		}
	}
    PyObject* operator()(IfcGeom::Representation::Representation* representation) const {
		IfcGeom::Representation::Serialization* serialized_representation = dynamic_cast<IfcGeom::Representation::Serialization*>(representation);
		IfcGeom::Representation::Triangulation<double>* triangulated_representation = dynamic_cast<IfcGeom::Representation::Triangulation<double>*>(representation);
		if (serialized_representation) {
			return SWIG_NewPointerObj(SWIG_as_voidptr(serialized_representation), SWIGTYPE_p_IfcGeom__Representation__Serialization, SWIG_POINTER_OWN);
		} else if (triangulated_representation) {
			return SWIG_NewPointerObj(SWIG_as_voidptr(triangulated_representation), SWIGTYPE_p_IfcGeom__Representation__TriangulationT_double_t, SWIG_POINTER_OWN);
		} else {
			throw std::runtime_error("Invalid element encountered");
		}
	}
};
%}

// Note that these elements ARE to be owned by SWIG/Python
%typemap(out) boost::variant<IfcGeom::Element<double>*, IfcGeom::Representation::Representation*> {
	// See which type is set and return appropriate
	$result = boost::apply_visitor(ShapeRTTI(), $1);
}

%extend IfcGeom::IteratorSettings {
	%pythoncode %{
		attrs = ("convert_back_units", "deflection_tolerance", "disable_opening_subtractions", "disable_triangulation", "faster_booleans", "sew_shells", "use_brep_data", "use_world_coords", "weld_vertices")
		def __repr__(self):
			return "%s(%s)"%(self.__class__.__name__, ",".join(tuple("%s=%r"%(a, getattr(self, a)()) for a in self.attrs)))
	%}
}


// I couldn't get the vector<string> typemap to be applied when %extending Iterator constructor.
// anyway it does not matter as SWIG generates C code without actual constructors
%inline %{
	template <typename T>
	IfcGeom::Iterator<T>* construct_iterator_with_include_exclude_(IfcGeom::IteratorSettings settings, IfcParse::IfcFile* file, std::vector<std::string> elems, bool include, int num_threads) {
		std::set<std::string> elems_set(elems.begin(), elems.end());
		IfcGeom::entity_filter ef{ include, false, elems_set };
		return new IfcGeom::Iterator<T>(settings, file, {ef}, num_threads);
	}

	template <typename T>
	IfcGeom::Iterator<T>* construct_iterator_with_include_exclude_globalid_(IfcGeom::IteratorSettings settings, IfcParse::IfcFile* file, std::vector<std::string> elems, bool include, int num_threads) {
		std::set<std::string> elems_set(elems.begin(), elems.end());
		IfcGeom::attribute_filter af;
		af.attribute_name = "GlobalId";
		af.populate(elems_set);
		af.include = include;
		return new IfcGeom::Iterator<T>(settings, file, {af}, num_threads);
	}

	IfcGeom::Iterator<float>* construct_iterator_single_precision_with_include_exclude(IfcGeom::IteratorSettings settings, IfcParse::IfcFile* file, std::vector<std::string> elems, bool include, int num_threads) {
		return construct_iterator_with_include_exclude_<float>(settings, file, elems, include, num_threads);
	}

	IfcGeom::Iterator<double>* construct_iterator_double_precision_with_include_exclude(IfcGeom::IteratorSettings settings, IfcParse::IfcFile* file, std::vector<std::string> elems, bool include, int num_threads) {
		return construct_iterator_with_include_exclude_<double>(settings, file, elems, include, num_threads);
	}

	IfcGeom::Iterator<float>* construct_iterator_single_precision_with_include_exclude_globalid(IfcGeom::IteratorSettings settings, IfcParse::IfcFile* file, std::vector<std::string> elems, bool include, int num_threads) {
		return construct_iterator_with_include_exclude_globalid_<float>(settings, file, elems, include, num_threads);
	}

	IfcGeom::Iterator<double>* construct_iterator_double_precision_with_include_exclude_globalid(IfcGeom::IteratorSettings settings, IfcParse::IfcFile* file, std::vector<std::string> elems, bool include, int num_threads) {
		return construct_iterator_with_include_exclude_globalid_<double>(settings, file, elems, include, num_threads);
	}
%}

%ignore construct_iterator_with_include_exclude_;
%newobject construct_iterator_single_precision_with_include_exclude;
%newobject construct_iterator_double_precision_with_include_exclude;
%newobject construct_iterator_single_precision_with_include_exclude_globalid;
%newobject construct_iterator_double_precision_with_include_exclude_globalid;

%extend IfcGeom::Iterator<float> {
	static int mantissa_size() {
		return std::numeric_limits<float>::digits;
	}
};

%extend IfcGeom::Iterator<double> {
	static int mantissa_size() {
		return std::numeric_limits<double>::digits;
	}
};

%extend IfcGeom::Representation::Triangulation {
	%pythoncode %{
        # Hide the getters with read-only property implementations
        id = property(id)
        faces = property(faces)
        edges = property(edges)
        material_ids = property(material_ids)
        materials = property(materials)
	%}
};

// Specialized accessors follow later, for otherwise property definitions
// would appear before templated getter functions are defined.
%extend IfcGeom::Representation::Triangulation<float> {
	%pythoncode %{
        # Hide the getters with read-only property implementations
        verts = property(verts)
        normals = property(normals)
	%}
};
%extend IfcGeom::Representation::Triangulation<double> {
	%pythoncode %{
        # Hide the getters with read-only property implementations
        verts = property(verts)
        normals = property(normals)
	%}
};

%extend IfcGeom::Representation::Serialization {
	%pythoncode %{
        # Hide the getters with read-only property implementations
        id = property(id)
        brep_data = property(brep_data)
        surface_styles = property(surface_styles)
	%}
};

%extend IfcGeom::Element {

	IfcUtil::IfcBaseClass* product_() const {
		return $self->product();
	}

	%pythoncode %{
        # Hide the getters with read-only property implementations
        id = property(id)
        parent_id = property(parent_id)
        name = property(name)
        type = property(type)
        guid = property(guid)
        context = property(context)
        unique_id = property(unique_id)
        transformation = property(transformation)
        product = property(product_)
	%}

};

%extend IfcGeom::TriangulationElement {
	%pythoncode %{
        # Hide the getters with read-only property implementations
        geometry = property(geometry)
	%}
};

%extend IfcGeom::SerializedElement {
	%pythoncode %{
        # Hide the getters with read-only property implementations
        geometry = property(geometry)
	%}
};

%extend IfcGeom::Material {
	%pythoncode %{
        # Hide the getters with read-only property implementations
        has_diffuse = property(hasDiffuse)
        has_specular = property(hasSpecular)
        has_transparency = property(hasTransparency)
        has_specularity = property(hasSpecularity)
        diffuse = property(diffuse)
        specular = property(specular)
        transparency = property(transparency)
        specularity = property(specularity)
        name = property(name)
	%}
};

%extend IfcGeom::Transformation {
	%pythoncode %{
        # Hide the getters with read-only property implementations
        matrix = property(matrix)
	%}
};

%extend IfcGeom::Matrix {
	%pythoncode %{
        # Hide the getters with read-only property implementations
        data = property(data)
	%}
};

%{
	template <typename Schema>
	static boost::variant<IfcGeom::Element<double>*, IfcGeom::Representation::Representation*> helper_fn_create_shape(IfcGeom::IteratorSettings& settings, IfcUtil::IfcBaseClass* instance, IfcUtil::IfcBaseClass* representation = 0) {
		IfcParse::IfcFile* file = instance->data().file;
			
		IfcGeom::Kernel kernel(file);
		kernel.setValue(IfcGeom::Kernel::GV_MAX_FACES_TO_ORIENT, settings.get(IfcGeom::IteratorSettings::SEW_SHELLS) ? std::numeric_limits<double>::infinity() : -1);
		kernel.setValue(IfcGeom::Kernel::GV_DIMENSIONALITY, (settings.get(IfcGeom::IteratorSettings::INCLUDE_CURVES) ? (settings.get(IfcGeom::IteratorSettings::EXCLUDE_SOLIDS_AND_SURFACES) ? -1. : 0.) : +1.));
			
		if (instance->declaration().is(Schema::IfcProduct::Class())) {
			if (representation) {
				if (!representation->declaration().is(Schema::IfcRepresentation::Class())) {
					throw IfcParse::IfcException("Supplied representation not of type IfcRepresentation");
				}
			}
		
			typename Schema::IfcProduct* product = (typename Schema::IfcProduct*) instance;

			if (!representation && !product->hasRepresentation()) {
				throw IfcParse::IfcException("Representation is NULL");
			}
			
			typename Schema::IfcProductRepresentation* prodrep = product->Representation();
			typename Schema::IfcRepresentation::list::ptr reps = prodrep->Representations();
			typename Schema::IfcRepresentation* ifc_representation = (typename Schema::IfcRepresentation*) representation;
			
			if (!ifc_representation) {
				// First, try to find a representation based on the settings
				for (typename Schema::IfcRepresentation::list::it it = reps->begin(); it != reps->end(); ++it) {
					typename Schema::IfcRepresentation* rep = *it;
					if (!rep->hasRepresentationIdentifier()) {
						continue;
					}
					if (!settings.get(IfcGeom::IteratorSettings::EXCLUDE_SOLIDS_AND_SURFACES)) {
						if (rep->RepresentationIdentifier() == "Body") {
							ifc_representation = rep;
							break;
						}
					}
					if (settings.get(IfcGeom::IteratorSettings::INCLUDE_CURVES)) {
						if (rep->RepresentationIdentifier() == "Plan" || rep->RepresentationIdentifier() == "Axis") {
							ifc_representation = rep;
							break;
						}
					}
				}
			}

			// Otherwise, find a representation within the 'Model' or 'Plan' context
			if (!ifc_representation) {
				for (typename Schema::IfcRepresentation::list::it it = reps->begin(); it != reps->end(); ++it) {
					typename Schema::IfcRepresentation* rep = *it;
					typename Schema::IfcRepresentationContext* context = rep->ContextOfItems();
					
					// TODO: Remove redundancy with IfcGeomIterator.h
					if (context->hasContextType()) {
						std::set<std::string> context_types;
						if (!settings.get(IfcGeom::IteratorSettings::EXCLUDE_SOLIDS_AND_SURFACES)) {
							context_types.insert("model");
							context_types.insert("design");
							context_types.insert("model view");
							context_types.insert("detail view");
						}
						if (settings.get(IfcGeom::IteratorSettings::INCLUDE_CURVES)) {
							context_types.insert("plan");
						}			

						std::string context_type_lc = context->ContextType();
						for (std::string::iterator c = context_type_lc.begin(); c != context_type_lc.end(); ++c) {
							*c = tolower(*c);
						}
						if (context_types.find(context_type_lc) != context_types.end()) {
							ifc_representation = rep;
						}
					}
				}
			}

			if (!ifc_representation) {
				if (reps->size()) {
					// Return a random representation
					ifc_representation = *reps->begin();
				} else {
					throw IfcParse::IfcException("No suitable IfcRepresentation found");
				}
			}

			IfcGeom::BRepElement<double>* brep = kernel.convert(settings, ifc_representation, product);
			if (!brep) {
				throw IfcParse::IfcException("Failed to process shape");
			}
			if (settings.get(IfcGeom::IteratorSettings::USE_BREP_DATA)) {
				IfcGeom::SerializedElement<double>* serialization = new IfcGeom::SerializedElement<double>(*brep);
				delete brep;
				return serialization;
			} else if (!settings.get(IfcGeom::IteratorSettings::DISABLE_TRIANGULATION)) {
				IfcGeom::TriangulationElement<double>* triangulation = new IfcGeom::TriangulationElement<double>(*brep);
				delete brep;
				return triangulation;
			} else {
				throw IfcParse::IfcException("No element to return based on provided settings");
			}
		} else {
			if (!representation) {
				if (instance->declaration().is(Schema::IfcRepresentationItem::Class()) || instance->declaration().is(Schema::IfcRepresentation::Class())) {
					IfcGeom::IfcRepresentationShapeItems shapes = kernel.convert(instance);

					IfcGeom::ElementSettings element_settings(settings, kernel.getValue(IfcGeom::Kernel::GV_LENGTH_UNIT), instance->declaration().name());
					IfcGeom::Representation::BRep brep(element_settings, boost::lexical_cast<std::string>(instance->data().id()), shapes);
					try {
						if (settings.get(IfcGeom::IteratorSettings::USE_BREP_DATA)) {
							return new IfcGeom::Representation::Serialization(brep);
						} else if (!settings.get(IfcGeom::IteratorSettings::DISABLE_TRIANGULATION)) {
							return new IfcGeom::Representation::Triangulation<double>(brep);
						}
					} catch (...) {
						throw IfcParse::IfcException("Error during shape serialization");
					}
				}
			} else {
				throw IfcParse::IfcException("Invalid additional representation specified");
			}
		}
		return boost::variant<IfcGeom::Element<double>*, IfcGeom::Representation::Representation*>();
	}
%}

%inline %{
	static boost::variant<IfcGeom::Element<double>*, IfcGeom::Representation::Representation*> create_shape(IfcGeom::IteratorSettings& settings, IfcUtil::IfcBaseClass* instance, IfcUtil::IfcBaseClass* representation = 0) {
		const std::string& schema_name = instance->declaration().schema()->name();
		if (schema_name == "IFC2X3") {
			return helper_fn_create_shape<Ifc2x3>(settings, instance, representation);
		} else if (schema_name == "IFC4") {
			return helper_fn_create_shape<Ifc4>(settings, instance, representation);
		} else {
			throw IfcParse::IfcException("No geometry support for " + schema_name);
		}
	}
%}

%inline %{
	IfcUtil::IfcBaseClass* serialise(const std::string& schema_name, const std::string& shape_str, bool advanced=true) {
		std::stringstream stream(shape_str);
		BRepTools_ShapeSet shapes;
		shapes.Read(stream);
		const TopoDS_Shape& shp = shapes.Shape(shapes.NbShapes());

		return IfcGeom::serialise(schema_name, shp, advanced);
	}

	IfcUtil::IfcBaseClass* tesselate(const std::string& schema_name, const std::string& shape_str, double d) {
		std::stringstream stream(shape_str);
		BRepTools_ShapeSet shapes;
		shapes.Read(stream);
		const TopoDS_Shape& shp = shapes.Shape(shapes.NbShapes());

		return IfcGeom::tesselate(schema_name, shp, d);
	}
%}

namespace IfcGeom {
	%template(iterator_double_precision) Iterator<double>;
	%template(element_double_precision) Element<double>;
	%template(triangulation_element_double_precision) TriangulationElement<double>;
	%template(serialized_element_double_precision) SerializedElement<double>;
	%template(transformation_double_precision) Transformation<double>;
	%template(matrix_double_precision) Matrix<double>;
	namespace Representation {
		%template(triangulation_double_precision) Triangulation<double>;
	};
};
