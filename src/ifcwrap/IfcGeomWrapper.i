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

%rename("buffer") stream_or_filename;

%ignore stream_or_filename::stream;

// This is only used for RGB colours, hence the size of 3
%typemap(out) const double* {
	$result = PyTuple_New(3);
	for (int i = 0; i < 3; ++i) {
		PyTuple_SetItem($result, i, PyFloat_FromDouble($1[i]));
	}
}

// SWIG does not support bool references in a meaningful way, so the
// ifcopenshell::geometry::Settings functions degrade to return a read only value
%typemap(out) double& {
	$result = SWIG_From_double(*$1);
}
%typemap(out) bool& {
	$result = PyBool_FromLong(static_cast<long>(*$1));
}

%ignore IfcGeom::impl::tree::selector;

// Using RTTI return a more specialized type of Element
// Note that these elements are not to be owned by SWIG/Python as they will be freed automatically upon the next iteration
// except for the IfcGeom::Element instances which are returned by Iterator::getObject() calls
%typemap(out) IfcGeom::Element* {
	IfcGeom::SerializedElement* serialized_elem = dynamic_cast<IfcGeom::SerializedElement*>($1);
	IfcGeom::TriangulationElement* triangulation_elem = dynamic_cast<IfcGeom::TriangulationElement*>($1);
	IfcGeom::BRepElement* brep_elem = dynamic_cast<IfcGeom::BRepElement*>($1);
	if (triangulation_elem) {
		$result = SWIG_NewPointerObj(SWIG_as_voidptr(triangulation_elem), SWIGTYPE_p_IfcGeom__TriangulationElement, 0);
	} else if (serialized_elem) {
		$result = SWIG_NewPointerObj(SWIG_as_voidptr(serialized_elem), SWIGTYPE_p_IfcGeom__SerializedElement, 0);
	} else if (brep_elem) {
		$result = SWIG_NewPointerObj(SWIG_as_voidptr(brep_elem), SWIGTYPE_p_IfcGeom__BRepElement, 0);
	} else {
		$result = SWIG_NewPointerObj(SWIG_as_voidptr($1), SWIGTYPE_p_IfcGeom__Element, SWIG_POINTER_OWN);
	}
}

%newobject IfcGeom::Representation::BRep::item;

%newobject IfcGeom::ConversionResultShape::halfspaces;
%newobject IfcGeom::ConversionResultShape::box;
%newobject IfcGeom::ConversionResultShape::solid;
%newobject IfcGeom::ConversionResultShape::add;
%newobject IfcGeom::ConversionResultShape::subtract;
%newobject IfcGeom::ConversionResultShape::intersect;
%newobject IfcGeom::ConversionResultShape::moved;

%newobject IfcGeom::ConversionResultShape::area;
%newobject IfcGeom::ConversionResultShape::volume;
%newobject IfcGeom::ConversionResultShape::length;

%newobject nary_union;

%newobject IfcGeom::OpaqueNumber::operator+;
%newobject IfcGeom::OpaqueNumber::operator-;
%newobject IfcGeom::OpaqueNumber::operator*;
%newobject IfcGeom::OpaqueNumber::operator/;

%include "../ifcgeom/ifc_geom_api.h"
%include "../ifcgeom/Converter.h"
%include "../ifcgeom/ConversionResult.h"
%include "../ifcgeom/IteratorSettings.h"
%include "../ifcgeom/ConversionSettings.h"
%include "../ifcgeom/IfcGeomElement.h"
%include "../ifcgeom/IfcGeomRepresentation.h"
%include "../ifcgeom/Iterator.h"
%include "../ifcgeom/GeometrySerializer.h"
%include "../ifcgeom/taxonomy.h"

%include "../serializers/SvgSerializer.h"
%include "../serializers/HdfSerializer.h"
%include "../serializers/WavefrontObjSerializer.h"
%include "../serializers/XmlSerializer.h"
%include "../serializers/GltfSerializer.h"


%extend ifcopenshell::geometry::Settings {
	void set_(const std::string& name, bool val) {
		return $self->set(name, val);
	}
	void set_(const std::string& name, int val) {
		return $self->set(name, val);
	}
	void set_(const std::string& name, ifcopenshell::geometry::settings::IteratorOutputOptions val) {
		return $self->set(name, val);
	}	
	void set_(const std::string& name, double val) {
		return $self->set(name, val);
	}
	void set_(const std::string& name, const std::string& val) {
		return $self->set(name, val);
	}
	void set_(const std::string& name, const std::set<int>& val) {
		return $self->set(name, val);
	}
	ifcopenshell::geometry::Settings::value_variant_t get_(const std::string& name) {
		return $self->get(name);
	}
	std::vector<std::string> setting_names() {
		return $self->setting_names();
	}
}

%extend ifcopenshell::geometry::SerializerSettings {
	void set_(const std::string& name, bool val) {
		return $self->set(name, val);
	}
	void set_(const std::string& name, int val) {
		return $self->set(name, val);
	}
	void set_(const std::string& name, double val) {
		return $self->set(name, val);
	}
	void set_(const std::string& name, const std::string& val) {
		return $self->set(name, val);
	}
	void set_(const std::string& name, const std::set<int>& val) {
		return $self->set(name, val);
	}
	ifcopenshell::geometry::SerializerSettings::value_variant_t get_(const std::string& name) {
		return $self->get(name);
	}
	std::vector<std::string> setting_names() {
		return $self->setting_names();
	}
}

#ifdef IFOPSH_WITH_OPENCASCADE

%template(ray_intersection_results) std::vector<IfcGeom::ray_intersection_result>;

// A Template instantantation should be defined before it is used as a base class. 
// But frankly I don't care as most methods are subtlely different anyway.
%include "../ifcgeom/kernels/opencascade/IfcGeomTree.h"

%extend IfcGeom::tree {

	static aggregate_of_instance::ptr vector_to_list(const std::vector<const IfcUtil::IfcBaseEntity*>& ps) {
		aggregate_of_instance::ptr r(new aggregate_of_instance);
		for (auto it = ps.begin(); it != ps.end(); ++it) {
			// @todo
			r->push(const_cast<IfcUtil::IfcBaseEntity*>(*it));
		}
		return r;
	}

	aggregate_of_instance::ptr select_box(IfcUtil::IfcBaseClass* e, bool completely_within = false, double extend=-1.e-5) const {
		if (!e->declaration().is("IfcProduct")) {
			throw IfcParse::IfcException("Instance should be an IfcProduct");
		}
		std::vector<const IfcUtil::IfcBaseEntity*> ps = $self->select_box((IfcUtil::IfcBaseEntity*)e, completely_within, extend);
		return IfcGeom_tree_vector_to_list(ps);
	}

	aggregate_of_instance::ptr select_box(const gp_Pnt& p) const {
		std::vector<const IfcUtil::IfcBaseEntity*> ps = $self->select_box(p);
		return IfcGeom_tree_vector_to_list(ps);
	}

	aggregate_of_instance::ptr select_box(const Bnd_Box& b, bool completely_within = false) const {
		std::vector<const IfcUtil::IfcBaseEntity*> ps = $self->select_box(b, completely_within);
		return IfcGeom_tree_vector_to_list(ps);
	}

	aggregate_of_instance::ptr select(IfcUtil::IfcBaseClass* e, bool completely_within = false, double extend = 0.0) const {
		if (!e->declaration().is("IfcProduct")) {
			throw IfcParse::IfcException("Instance should be an IfcProduct");
		}
		std::vector<const IfcUtil::IfcBaseEntity*> ps = $self->select((IfcUtil::IfcBaseEntity*)e, completely_within, extend);
		return IfcGeom_tree_vector_to_list(ps);
	}

	aggregate_of_instance::ptr select(const gp_Pnt& p, double extend=0.0) const {
		std::vector<const IfcUtil::IfcBaseEntity*> ps = $self->select(p, extend);
		return IfcGeom_tree_vector_to_list(ps);
	}

	aggregate_of_instance::ptr select(const std::string& shape_serialization, bool completely_within = false, double extend = -1.e-5) const {
		std::stringstream stream(shape_serialization);
		BRepTools_ShapeSet shapes;
		shapes.Read(stream);
		const TopoDS_Shape& shp = shapes.Shape(shapes.NbShapes());

		std::vector<const IfcUtil::IfcBaseEntity*> ps = $self->select(shp, completely_within, extend);
		return IfcGeom_tree_vector_to_list(ps);
	}

	aggregate_of_instance::ptr select(const IfcGeom::BRepElement* elem, bool completely_within = false, double extend = -1.e-5) const {
		std::vector<const IfcUtil::IfcBaseEntity*> ps = $self->select(elem, completely_within, extend);
		return IfcGeom_tree_vector_to_list(ps);
	}

}

#endif

// A visitor
%{
struct ShapeRTTI : public boost::static_visitor<PyObject*>
{
    PyObject* operator()(IfcGeom::Element* elem) const {
		IfcGeom::SerializedElement* serialized_elem = dynamic_cast<IfcGeom::SerializedElement*>(elem);
		IfcGeom::TriangulationElement* triangulation_elem = dynamic_cast<IfcGeom::TriangulationElement*>(elem);
		IfcGeom::BRepElement* brep_elem = dynamic_cast<IfcGeom::BRepElement*>(elem);
		if (triangulation_elem) {
			return SWIG_NewPointerObj(SWIG_as_voidptr(triangulation_elem), SWIGTYPE_p_IfcGeom__TriangulationElement, SWIG_POINTER_OWN);
		} else if (serialized_elem) {
			return SWIG_NewPointerObj(SWIG_as_voidptr(serialized_elem), SWIGTYPE_p_IfcGeom__SerializedElement, SWIG_POINTER_OWN);
		} else if (brep_elem) {
			return SWIG_NewPointerObj(SWIG_as_voidptr(brep_elem), SWIGTYPE_p_IfcGeom__BRepElement, SWIG_POINTER_OWN);
		} else {
			return SWIG_Py_Void();
		}
	}
    PyObject* operator()(IfcGeom::Representation::Representation* representation) const {
		IfcGeom::Representation::Serialization* serialized_representation = dynamic_cast<IfcGeom::Representation::Serialization*>(representation);
		IfcGeom::Representation::Triangulation* triangulated_representation = dynamic_cast<IfcGeom::Representation::Triangulation*>(representation);
		IfcGeom::Representation::BRep* brep_representation = dynamic_cast<IfcGeom::Representation::BRep*>(representation);
		if (serialized_representation) {
			return SWIG_NewPointerObj(SWIG_as_voidptr(serialized_representation), SWIGTYPE_p_IfcGeom__Representation__Serialization, SWIG_POINTER_OWN);
		} else if (triangulated_representation) {
			return SWIG_NewPointerObj(SWIG_as_voidptr(triangulated_representation), SWIGTYPE_p_IfcGeom__Representation__Triangulation, SWIG_POINTER_OWN);
		} else if (brep_representation) {
			return SWIG_NewPointerObj(SWIG_as_voidptr(brep_representation), SWIGTYPE_p_IfcGeom__Representation__BRep, SWIG_POINTER_OWN);
		} else {
			return SWIG_Py_Void();
		}
	}
};
%}

// Note that these elements ARE to be owned by SWIG/Python
%typemap(out) boost::variant<IfcGeom::Element*, IfcGeom::Representation::Representation*> {
	// See which type is set and return appropriate
	$result = boost::apply_visitor(ShapeRTTI(), $1);
}

%newobject construct_iterator_with_include_exclude;
%newobject construct_iterator_with_include_exclude_globalid;
%newobject construct_iterator_with_include_exclude_id;

// I couldn't get the vector<string> typemap to be applied when %extending Iterator constructor.
// anyway it does not matter as SWIG generates C code without actual constructors
%inline %{
	IfcGeom::Iterator* construct_iterator_with_include_exclude(const std::string& geometry_library, ifcopenshell::geometry::Settings settings, IfcParse::IfcFile* file, std::vector<std::string> elems, bool include, int num_threads) {
		std::set<std::string> elems_set(elems.begin(), elems.end());
		IfcGeom::entity_filter ef{ include, false, elems_set };
		return new IfcGeom::Iterator(geometry_library, settings, file, {ef}, num_threads);
	}

	IfcGeom::Iterator* construct_iterator_with_include_exclude_globalid(const std::string& geometry_library, ifcopenshell::geometry::Settings settings, IfcParse::IfcFile* file, std::vector<std::string> elems, bool include, int num_threads) {
		std::set<std::string> elems_set(elems.begin(), elems.end());
		IfcGeom::attribute_filter af;
		af.attribute_name = "GlobalId";
		af.populate(elems_set);
		af.include = include;
		return new IfcGeom::Iterator(geometry_library, settings, file, {af}, num_threads);
	}

	IfcGeom::Iterator* construct_iterator_with_include_exclude_id(const std::string& geometry_library, ifcopenshell::geometry::Settings settings, IfcParse::IfcFile* file, std::vector<int> elems, bool include, int num_threads) {
		std::set<int> elems_set(elems.begin(), elems.end());
		IfcGeom::instance_id_filter af(include, false, elems_set);
		return new IfcGeom::Iterator(geometry_library, settings, file, {af}, num_threads);
	}
%}

%extend IfcGeom::Representation::Triangulation {
    %pythoncode %{
        # Hide the getters with read-only property implementations
        id = property(id)
        faces = property(faces)
        edges = property(edges)
        material_ids = property(material_ids)
        materials = property(materials)
        verts = property(verts)
        normals = property(normals)
        item_ids = property(item_ids)
    %}
};

%extend IfcGeom::Representation::Serialization {
	%pythoncode %{
        # Hide the getters with read-only property implementations
        id = property(id)
        brep_data = property(brep_data)
        surface_styles = property(surface_styles)
        surface_style_ids = property(surface_style_ids)
	%}
};

%extend IfcGeom::Element {

	const IfcUtil::IfcBaseClass* product_() const {
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

%extend IfcGeom::BRepElement {
    double calc_volume_() const {
        double v;
        if ($self->geometry().calculate_volume(v)) {
            return v;
        } else {
            return std::numeric_limits<double>::quiet_NaN();
        }
    }

    double calc_surface_area_() const {
        double v;
        if ($self->geometry().calculate_surface_area(v)) {
            return v;
        } else {
            return std::numeric_limits<double>::quiet_NaN();
        }
    }

    %pythoncode %{
        # Hide the getters with read-only property implementations
        geometry = property(geometry)
        volume = property(calc_volume_)
        surface_area = property(calc_surface_area_)
    %}    
};

/*
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
*/

%extend IfcGeom::Transformation {
	PyObject* matrix_() const {
		auto result = PyTuple_New(16);
		for (int i = 0; i < 16; ++i) {
			PyTuple_SET_ITEM(result, i, PyFloat_FromDouble(self->data()->ccomponents().data()[i]));
		}
		return result;
	}
	%pythoncode %{
        # Hide the getters with read-only property implementations
        matrix = property(matrix_)
	%}
};

%extend IfcGeom::Matrix {
	%pythoncode %{
        # Hide the getters with read-only property implementations
        data = property(data)
	%}
};

%{
	template <typename T>
	std::string to_locale_invariant_string(const T& t) {
		std::ostringstream oss;
		oss.imbue(std::locale::classic());
		oss << t;
		return oss.str();
	}

	template <typename Schema>
	static boost::variant<IfcGeom::Element*, IfcGeom::Representation::Representation*> helper_fn_create_shape(const std::string& geometry_library, ifcopenshell::geometry::Settings& settings, IfcUtil::IfcBaseClass* instance, IfcUtil::IfcBaseClass* representation = 0) {
		IfcParse::IfcFile* file = instance->data().file;
			
		ifcopenshell::geometry::Converter kernel(geometry_library, file, settings);
			
		if (instance->declaration().is(Schema::IfcProduct::Class())) {
			if (representation) {
				if (!representation->declaration().is(Schema::IfcRepresentation::Class())) {
					throw IfcParse::IfcException("Supplied representation not of type IfcRepresentation");
				}
			}
		
			typename Schema::IfcProduct* product = (typename Schema::IfcProduct*) instance;

			if (!representation && !product->Representation()) {
				throw IfcParse::IfcException("Representation is NULL");
			}
			
			typename Schema::IfcProductRepresentation* prodrep = product->Representation();
			typename Schema::IfcRepresentation::list::ptr reps = prodrep->Representations();
			typename Schema::IfcRepresentation* ifc_representation = (typename Schema::IfcRepresentation*) representation;
			
			if (!ifc_representation) {
				// First, try to find a representation based on the settings
				for (typename Schema::IfcRepresentation::list::it it = reps->begin(); it != reps->end(); ++it) {
					typename Schema::IfcRepresentation* rep = *it;
					if (!rep->RepresentationIdentifier()) {
						continue;
					}
					if (settings.get<ifcopenshell::geometry::settings::IncludeSurfaces>().get()) {
						if (*rep->RepresentationIdentifier() == "Body") {
							ifc_representation = rep;
							break;
						}
					}
					if (settings.get<ifcopenshell::geometry::settings::IncludeCurves>().get()) {
						if (*rep->RepresentationIdentifier() == "Plan" || *rep->RepresentationIdentifier() == "Axis") {
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
					if (context->ContextType()) {
						std::set<std::string> context_types;
						if (settings.get<ifcopenshell::geometry::settings::IncludeSurfaces>().get()) {
							context_types.insert("model");
							context_types.insert("design");
							context_types.insert("model view");
							context_types.insert("detail view");
						}
						if (settings.get<ifcopenshell::geometry::settings::IncludeCurves>().get()) {
							context_types.insert("plan");
						}			

						std::string context_type_lc = *context->ContextType();
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

			IfcGeom::BRepElement* brep = kernel.create_brep_for_representation_and_product(ifc_representation, product);
			if (!brep) {
				throw IfcParse::IfcException("Failed to process shape");
			}
			if (settings.get<ifcopenshell::geometry::settings::IteratorOutput>().get() == ifcopenshell::geometry::settings::SERIALIZED) {
				IfcGeom::SerializedElement* serialization = new IfcGeom::SerializedElement(*brep);
				delete brep;
				return serialization;
			} else if (settings.get<ifcopenshell::geometry::settings::IteratorOutput>().get() == ifcopenshell::geometry::settings::TRIANGULATED) {
				IfcGeom::TriangulationElement* triangulation = new IfcGeom::TriangulationElement(*brep);
				delete brep;
				return triangulation;
			} else {
				throw IfcParse::IfcException("No element to return based on provided settings");
			}
		} else {
			if (!representation) {
				if (instance->declaration().is(Schema::IfcRepresentationItem::Class()) || 
					instance->declaration().is(Schema::IfcRepresentation::Class()) ||
					// https://github.com/IfcOpenShell/IfcOpenShell/issues/1649
					instance->declaration().is(Schema::IfcProfileDef::Class())
				) {
					IfcGeom::ConversionResults shapes = kernel.convert(instance);

					IfcGeom::Representation::BRep brep(settings, instance->declaration().name(), to_locale_invariant_string(instance->data().id()), shapes);
					try {
						if (settings.get<ifcopenshell::geometry::settings::IteratorOutput>().get() == ifcopenshell::geometry::settings::SERIALIZED) {
							return new IfcGeom::Representation::Serialization(brep);
						} else if (settings.get<ifcopenshell::geometry::settings::IteratorOutput>().get() == ifcopenshell::geometry::settings::TRIANGULATED) {
							return new IfcGeom::Representation::Triangulation(brep);
						}
					} catch (...) {
						throw IfcParse::IfcException("Error during shape serialization");
					}
				}
			} else {
				throw IfcParse::IfcException("Invalid additional representation specified");
			}
		}
		return boost::variant<IfcGeom::Element*, IfcGeom::Representation::Representation*>();
	}
%}

%inline %{
	static boost::variant<IfcGeom::Element*, IfcGeom::Representation::Representation*> create_shape(ifcopenshell::geometry::Settings& settings, IfcUtil::IfcBaseClass* instance, IfcUtil::IfcBaseClass* representation = 0, const char* const geometry_library="opencascade") {
		const std::string& schema_name = instance->declaration().schema()->name();

		#ifdef HAS_SCHEMA_2x3
		if (schema_name == "IFC2X3") {
			return helper_fn_create_shape<Ifc2x3>(geometry_library, settings, instance, representation);
		}
		#endif
		#ifdef HAS_SCHEMA_4
		if (schema_name == "IFC4") {
			return helper_fn_create_shape<Ifc4>(geometry_library, settings, instance, representation);
		}
		#endif
		#ifdef HAS_SCHEMA_4x1
		if (schema_name == "IFC4X1") {
			return helper_fn_create_shape<Ifc4x1>(geometry_library, settings, instance, representation);
		}
		#endif
		#ifdef HAS_SCHEMA_4x2
		if (schema_name == "IFC4X2") {
			return helper_fn_create_shape<Ifc4x2>(geometry_library, settings, instance, representation);
		}
		#endif
		#ifdef HAS_SCHEMA_4x3_rc1
		if (schema_name == "IFC4X3_RC1") {
			return helper_fn_create_shape<Ifc4x3_rc1>(geometry_library, settings, instance, representation);
		}
		#endif
		#ifdef HAS_SCHEMA_4x3_rc2
		if (schema_name == "IFC4X3_RC2") {
			return helper_fn_create_shape<Ifc4x3_rc2>(geometry_library, settings, instance, representation);
		}
		#endif
		#ifdef HAS_SCHEMA_4x3_rc3
		if (schema_name == "IFC4X3_RC3") {
			return helper_fn_create_shape<Ifc4x3_rc3>(geometry_library, settings, instance, representation);
		}
		#endif
		#ifdef HAS_SCHEMA_4x3_rc4
		if (schema_name == "IFC4X3_RC4") {
			return helper_fn_create_shape<Ifc4x3_rc4>(geometry_library, settings, instance, representation);
		}
		#endif
		#ifdef HAS_SCHEMA_4x3
		if (schema_name == "IFC4X3") {
			return helper_fn_create_shape<Ifc4x3>(geometry_library, settings, instance, representation);
		}
		#endif
		#ifdef HAS_SCHEMA_4x3_tc1
		if (schema_name == "IFC4X3_TC1") {
			return helper_fn_create_shape<Ifc4x3_tc1>(geometry_library, settings, instance, representation);
		}
		#endif
        #ifdef HAS_SCHEMA_4x3_add1
		if (schema_name == "IFC4X3_ADD1") {
			return helper_fn_create_shape<Ifc4x3_add1>(geometry_library, settings, instance, representation);
		}
		#endif
        #ifdef HAS_SCHEMA_4x3_add2
		if (schema_name == "IFC4X3_ADD2") {
			return helper_fn_create_shape<Ifc4x3_add2>(geometry_library, settings, instance, representation);
		}
		#endif

		throw IfcParse::IfcException("No geometry support for " + schema_name);
	}
%}

#ifdef IFOPSH_WITH_OPENCASCADE

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

#endif

#ifdef IFOPSH_WITH_CGAL

%ignore hlr_writer;
%ignore hlr_calc;
%ignore occt_join;
%ignore prefiltered_hlr;
%ignore svgfill::svg_to_line_segments;
%ignore svgfill::line_segments_to_polygons;

%template(svg_line_segments) std::vector<std::array<svgfill::point_2, 2>>;
%template(svg_groups_of_line_segments) std::vector<std::vector<std::array<svgfill::point_2, 2>>>;
%template(svg_point) std::array<double, 2>;
%template(line_segment) std::array<svgfill::point_2, 2>;
%template(svg_polygons) std::vector<svgfill::polygon_2>;
%template(svg_groups_of_polygons) std::vector<std::vector<svgfill::polygon_2>>;
%template(svg_loop) std::vector<std::array<double, 2>>;
%template(svg_loops) std::vector<std::vector<std::array<double, 2>>>;

%template(OpaqueCoordinate_3) IfcGeom::OpaqueCoordinate<3>;
%template(OpaqueCoordinate_4) IfcGeom::OpaqueCoordinate<4>;

%newobject create_epeck;

%inline %{
	IfcGeom::OpaqueNumber* create_epeck(int i) {
		return new ifcopenshell::geometry::NumberEpeck(i);
	}
	IfcGeom::OpaqueNumber* create_epeck(double d) {
		return new ifcopenshell::geometry::NumberEpeck(d);
	}
	IfcGeom::OpaqueNumber* create_epeck(const std::string& s) {
		return new ifcopenshell::geometry::NumberEpeck(typename CGAL::Epeck::FT::ET(s));
	}
%}

%inline %{
	IfcGeom::ConversionResultShape* nary_union(PyObject* sequence) {
		std::vector<const CGAL::Nef_polyhedron_3<CGAL::Epeck>*> nefs;
		for(Py_ssize_t i = 0; i < PySequence_Size(sequence); ++i) {
			PyObject* element = PySequence_GetItem(sequence, i);
			void* argp1 = nullptr;
			auto res1 = SWIG_ConvertPtr(element, &argp1, SWIGTYPE_p_IfcGeom__ConversionResultShape, 0);
			if (SWIG_IsOK(res1)) {
				auto arg1 = reinterpret_cast<IfcGeom::ConversionResultShape*>(argp1);
				auto cgs = dynamic_cast<ifcopenshell::geometry::CgalShape*>(arg1);
				if (cgs) {
					nefs.push_back(&cgs->nef());
				}
			}
		}
		ifcopenshell::geometry::CgalShape* shp;
		Py_BEGIN_ALLOW_THREADS;
		CGAL::Nef_nary_union_3< CGAL::Nef_polyhedron_3<CGAL::Epeck> > accum;
		for (auto& n : nefs) {
			accum.add_polyhedron(*n);
		}
		shp = new ifcopenshell::geometry::CgalShape(accum.get_union());
		Py_END_ALLOW_THREADS;
		return shp;
	}
%}

%extend IfcGeom::ConversionResultShape {
	std::string serialize_obj() {
		std::ostringstream result;
		auto cgs = dynamic_cast<ifcopenshell::geometry::CgalShape*>($self);
		if (cgs) {
			write_to_obj(cgs->nef(), result, std::numeric_limits<size_t>::max());
		}		
		return result.str();
	}

	void convex_tag(bool b) {
		auto cgs = dynamic_cast<ifcopenshell::geometry::CgalShape*>($self);
		if (cgs) {
			cgs->convex_tag() = b;
		}		
	}

	std::string serialize() {
		std::string result;
		ifcopenshell::geometry::taxonomy::matrix4 iden;
		$self->Serialize(iden, result);
		return result;
	}

	ConversionResultShape* solid_mt() {
		IfcGeom::ConversionResultShape* r;
		Py_BEGIN_ALLOW_THREADS;
		r = $self->solid();
		Py_END_ALLOW_THREADS;
		return r;
	}
}

%naturalvar svgfill::polygon_2::boundary;
%naturalvar svgfill::polygon_2::inner_boundaries;
%naturalvar svgfill::polygon_2::point_inside;

%include "../svgfill/src/svgfill.h"

%inline %{
	std::vector<std::vector<svgfill::line_segment_2>> svg_to_line_segments(const std::string& data, const boost::optional<std::string>& class_name) {
		std::vector<std::vector<svgfill::line_segment_2>> r;
		if (svgfill::svg_to_line_segments(data, class_name, r)) {
			return r;
		} else {
			throw std::runtime_error("Failed to read SVG");
		}
	}

	std::vector<std::vector<svgfill::polygon_2>> line_segments_to_polygons(svgfill::solver s, double eps, const std::vector<std::vector<svgfill::line_segment_2>>& segments) {
		std::vector<std::vector<svgfill::polygon_2>> r;
		if (svgfill::line_segments_to_polygons(s, eps, segments, r)) {
			return r;
		} else {
			throw std::runtime_error("Failed to read SVG");
		}
	}
%}

#endif
