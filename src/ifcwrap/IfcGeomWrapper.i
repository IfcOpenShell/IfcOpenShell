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
%ignore boost::hash_value;
%ignore IfcGeom::BRepElement::geometry_pointer;
%ignore IfcGeom::TriangulationElement::geometry_pointer;

// This is only used for RGB colours, hence the size of 3
%typemap(out) const double* {
	$result = PyTuple_New(3);
	for (int i = 0; i < 3; ++i) {
		PyTuple_SetItem($result, i, PyFloat_FromDouble($1[i]));
	}
}

%typemap(out) Eigen::Matrix4d {
	$result = PyTuple_New(4);
	for (int i = 0; i < 4; ++i) {
		auto row = PyTuple_New(4);
		for (int j = 0; j < 4; ++j) {
			PyTuple_SetItem(row, j, PyFloat_FromDouble($1(i, j)));
		}
		PyTuple_SetItem($result, i, row);
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

%typemap(out) IfcGeom::OpaqueNumber {
	$result = SWIG_NewPointerObj(SWIG_as_voidptr(new IfcGeom::OpaqueNumber($1)), SWIGTYPE_p_IfcGeom__OpaqueNumber, SWIG_POINTER_OWN);
}

%typemap(in) const IfcGeom::OpaqueNumber& (IfcGeom::OpaqueNumber temp) {
	void* argp = nullptr;
	int res = SWIG_ConvertPtr($input, &argp, SWIGTYPE_p_IfcGeom__OpaqueNumber, 0);
	if (!SWIG_IsOK(res) || !argp) {
		SWIG_exception_fail(SWIG_ArgError(res), "Expected IfcGeom::OpaqueNumber");
	}
	temp = *reinterpret_cast<IfcGeom::OpaqueNumber*>(argp);
	$1 = &temp;
}

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
%newobject IfcGeom::Representation::BRep::as_compound;

%newobject IfcGeom::ConversionResultShape::halfspaces;
%newobject IfcGeom::ConversionResultShape::box;
%newobject IfcGeom::ConversionResultShape::solid;
%newobject IfcGeom::ConversionResultShape::add;
%newobject IfcGeom::ConversionResultShape::subtract;
%newobject IfcGeom::ConversionResultShape::intersect;
%newobject IfcGeom::ConversionResultShape::concat;
%newobject IfcGeom::ConversionResultShape::moved;
%newobject IfcGeom::ConversionResultShape::wrap_in_compound;


%newobject nary_union;


%inline %{
template <typename T>
std::pair<char const*, size_t> vector_to_buffer(const T& t) {
    using V = typename std::remove_reference<decltype(t)>::type;
    return { reinterpret_cast<const char*>(t.data()), t.size() * sizeof(typename V::value_type) };
}
%}

%ignore ifcopenshell::geometry::taxonomy::item::print;

%typemap(out) std::variant<boost::blank, ifcopenshell::geometry::taxonomy::point3::ptr, double> {
	if ($1.index() == 0) {
		Py_INCREF(Py_None);
		return Py_None;
	} else if ($1.index() == 1) {
		return SWIG_NewPointerObj(SWIG_as_voidptr(new std::shared_ptr<ifcopenshell::geometry::taxonomy::point3>(std::get<ifcopenshell::geometry::taxonomy::point3::ptr>($1))), SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__point3_t, 0 | SWIG_POINTER_OWN);
	} else {
		return PyFloat_FromDouble(std::get<double>($1));
	}
}

%typemap(out) std::optional<bool> {
    if ($1) {
        $result = PyBool_FromLong(*$1 ? 1 : 0);
    } else {
        Py_INCREF(Py_None);
        $result = Py_None;
    }
}

%typemap(in) ifcopenshell::geometry::taxonomy::item::ptr {
	// @this is really annoying, but apparently inheritance
	// is lost in swig in the shared_ptr type hiearchy
	using namespace ifcopenshell::geometry::taxonomy;
	if (!$1) $1 = try_upcast<boolean_result>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__boolean_result_t);
	if (!$1) $1 = try_upcast<bspline_curve>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__bspline_curve_t);
	if (!$1) $1 = try_upcast<bspline_surface>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__bspline_surface_t);
	if (!$1) $1 = try_upcast<circle>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__circle_t);
	if (!$1) $1 = try_upcast<collection>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__collection_t);
	if (!$1) $1 = try_upcast<colour>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__colour_t);
	if (!$1) $1 = try_upcast<cylinder>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__cylinder_t);
	if (!$1) $1 = try_upcast<direction3>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__direction3_t);
	if (!$1) $1 = try_upcast<edge>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__edge_t);
	if (!$1) $1 = try_upcast<ellipse>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__ellipse_t);
	if (!$1) $1 = try_upcast<extrusion>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__extrusion_t);
	if (!$1) $1 = try_upcast<face>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__face_t);
	if (!$1) $1 = try_upcast<line>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__line_t);
	if (!$1) $1 = try_upcast<loft>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__loft_t);
	if (!$1) $1 = try_upcast<loop>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__loop_t);
	if (!$1) $1 = try_upcast<matrix4>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__matrix4_t);
	if (!$1) $1 = try_upcast<node>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__node_t);
	if (!$1) $1 = try_upcast<offset_curve>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__offset_curve_t);
	if (!$1) $1 = try_upcast<function_item>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__function_item_t);
	if (!$1) $1 = try_upcast<functor_item>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__functor_item_t);
	if (!$1) $1 = try_upcast<piecewise_function>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__piecewise_function_t);
	if (!$1) $1 = try_upcast<gradient_function>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__gradient_function_t);
	if (!$1) $1 = try_upcast<cant_function>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__cant_function_t);
	if (!$1) $1 = try_upcast<offset_function>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__offset_function_t);
	if (!$1) $1 = try_upcast<plane>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__plane_t);
	if (!$1) $1 = try_upcast<point3>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__point3_t);
	if (!$1) $1 = try_upcast<revolve>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__revolve_t);
	if (!$1) $1 = try_upcast<shell>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__shell_t);
	if (!$1) $1 = try_upcast<solid>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__solid_t);
	if (!$1) $1 = try_upcast<sphere>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__sphere_t);
	if (!$1) $1 = try_upcast<torus>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__torus_t);
	if (!$1) $1 = try_upcast<style>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__style_t);
	if (!$1) $1 = try_upcast<sweep_along_curve>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__sweep_along_curve_t);
}

%inline %{
std::string taxonomy_item_repr(ifcopenshell::geometry::taxonomy::item::ptr i) {
	std::ostringstream oss;
	i->print(oss);
	std::string result = oss.str();

	// Strip new line at the end of the printed result.
	// result is probably always ends with \n but just to be safe.
	if (!result.empty() && result.back() == '\n') {
		result.pop_back();
	}
	return result;  
}
%}

%{


namespace {
    // Helper function to create a Python tuple from an Eigen matrix/vector
    template <typename T>
    PyObject* eigen_to_python_tuple(const Eigen::MatrixBase<T>& mat) {
        constexpr auto rows = T::RowsAtCompileTime;
        constexpr auto cols = T::ColsAtCompileTime;

        if constexpr (rows == 1 || cols == 1) {
            // Eigen::Vector (1D array)
            PyObject* tuple = PyTuple_New(rows * cols);
            for (int i = 0; i < mat.size(); ++i) {
                PyTuple_SetItem(tuple, i, PyFloat_FromDouble(mat(i)));
            }
            return tuple;
        } else {
            // Eigen::Matrix (2D array)
            PyObject* tuple = PyTuple_New(rows);
            for (int i = 0; i < rows; ++i) {
                PyObject* row = PyTuple_New(cols);
                for (int j = 0; j < cols; ++j) {
                    PyTuple_SetItem(row, j, PyFloat_FromDouble(mat(i, j)));
                }
                PyTuple_SetItem(tuple, i, row);
            }
            return tuple;
        }
    }
}

%}

%shared_ptr(ifcopenshell::geometry::taxonomy::boolean_result);
%shared_ptr(ifcopenshell::geometry::taxonomy::item);
%shared_ptr(ifcopenshell::geometry::taxonomy::implicit_item);
%shared_ptr(ifcopenshell::geometry::taxonomy::function_item);
%shared_ptr(ifcopenshell::geometry::taxonomy::functor_item);
%shared_ptr(ifcopenshell::geometry::taxonomy::piecewise_function);
%shared_ptr(ifcopenshell::geometry::taxonomy::gradient_function);
%shared_ptr(ifcopenshell::geometry::taxonomy::cant_function);
%shared_ptr(ifcopenshell::geometry::taxonomy::offset_function);
%shared_ptr(ifcopenshell::geometry::taxonomy::less_functor);
%shared_ptr(ifcopenshell::geometry::taxonomy::eigen_base);
%shared_ptr(ifcopenshell::geometry::taxonomy::matrix4);
%shared_ptr(ifcopenshell::geometry::taxonomy::colour);
%shared_ptr(ifcopenshell::geometry::taxonomy::style);
%shared_ptr(ifcopenshell::geometry::taxonomy::geom_item);
%shared_ptr(ifcopenshell::geometry::taxonomy::cartesian_base);
%shared_ptr(ifcopenshell::geometry::taxonomy::point3);
%shared_ptr(ifcopenshell::geometry::taxonomy::direction3);
%shared_ptr(ifcopenshell::geometry::taxonomy::curve);
%shared_ptr(ifcopenshell::geometry::taxonomy::line);
%shared_ptr(ifcopenshell::geometry::taxonomy::circle);
%shared_ptr(ifcopenshell::geometry::taxonomy::ellipse);
%shared_ptr(ifcopenshell::geometry::taxonomy::bspline_curve);
%shared_ptr(ifcopenshell::geometry::taxonomy::offset_curve);
%shared_ptr(ifcopenshell::geometry::taxonomy::trimmed_curve);
%shared_ptr(ifcopenshell::geometry::taxonomy::edge);
%shared_ptr(ifcopenshell::geometry::taxonomy::collection_base);
%shared_ptr(ifcopenshell::geometry::taxonomy::collection);
%shared_ptr(ifcopenshell::geometry::taxonomy::loop);
%shared_ptr(ifcopenshell::geometry::taxonomy::face);
%shared_ptr(ifcopenshell::geometry::taxonomy::shell);
%shared_ptr(ifcopenshell::geometry::taxonomy::solid);
%shared_ptr(ifcopenshell::geometry::taxonomy::loft);
%shared_ptr(ifcopenshell::geometry::taxonomy::surface);
%shared_ptr(ifcopenshell::geometry::taxonomy::plane);
%shared_ptr(ifcopenshell::geometry::taxonomy::cylinder);
%shared_ptr(ifcopenshell::geometry::taxonomy::sphere);
%shared_ptr(ifcopenshell::geometry::taxonomy::torus);
%shared_ptr(ifcopenshell::geometry::taxonomy::bspline_surface);
%shared_ptr(ifcopenshell::geometry::taxonomy::sweep);
%shared_ptr(ifcopenshell::geometry::taxonomy::extrusion);
%shared_ptr(ifcopenshell::geometry::taxonomy::revolve);
%shared_ptr(ifcopenshell::geometry::taxonomy::sweep_along_curve);
%shared_ptr(ifcopenshell::geometry::taxonomy::node);

%include "../ifcgeom/ifc_geom_api.h"
%include "../ifcgeom/ConversionResult.h"
%include "../ifcgeom/ConversionSettings.h"
%include "../ifcgeom/IfcGeomElement.h"
%include "../ifcgeom/IfcGeomRepresentation.h"
%include "../ifcgeom/Iterator.h"
%include "../ifcgeom/GeometrySerializer.h"
%include "../ifcgeom/taxonomy.h"
%include "../ifcgeom/function_item_evaluator.h"

%{
#include "../serializers/geometry_serializer_plugin.h"

class PythonPluginGeometrySerializer : public GeometrySerializer {
public:
	PythonPluginGeometrySerializer(
		const std::string& extension,
		const std::string& output_filename,
		const std::string& output_temp_filename,
		ifcopenshell::geometry::Settings& geometry_settings,
		const ifcopenshell::geometry::SerializerSettings& serializer_settings
	)
		: GeometrySerializer(geometry_settings, serializer_settings)
	{
		ifcopenshell::serializers::geometry_serializer_context context{
			output_filename,
			output_temp_filename.empty() ? output_filename : output_temp_filename,
			geometry_settings,
			serializer_settings
		};

		initialize_serializer(extension, context);
	}

	PythonPluginGeometrySerializer(
		const std::string& extension,
		const stream_or_filename& output_filename,
		const stream_or_filename& output_temp_filename,
		ifcopenshell::geometry::Settings& geometry_settings,
		const ifcopenshell::geometry::SerializerSettings& serializer_settings
	)
		: GeometrySerializer(geometry_settings, serializer_settings)
	{
		const auto output_filename_string = output_filename.filename().value_or("");
		const auto output_temp_filename_string = output_temp_filename.filename().value_or(output_filename_string);
		ifcopenshell::serializers::geometry_serializer_context context{
			output_filename_string,
			output_temp_filename_string,
			geometry_settings,
			serializer_settings,
			&output_filename,
			&output_temp_filename
		};

		initialize_serializer(extension, context);
	}

private:
	void initialize_serializer(
		const std::string& extension,
		ifcopenshell::serializers::geometry_serializer_context& context
	) {
		auto& registry = ifcopenshell::serializers::geometry_serializer_registry_instance();
		registry.configure(extension, context);
		geometry_settings_ = context.geometry_settings;
		serializer_ = registry.create(extension, context);
	}

public:

	bool ready() override {
		return serializer_->ready();
	}

	bool is_streaming() const override {
		return serializer_->is_streaming();
	}

	void writeHeader() override {
		serializer_->writeHeader();
	}

	void finalize() override {
		serializer_->finalize();
	}

	void setFile(ifcopenshell::file& file) override {
		serializer_->setFile(file);
	}

	bool isTesselated() const override {
		return serializer_->isTesselated();
	}

	void write(const IfcGeom::TriangulationElement* element) override {
		serializer_->write(element);
	}

	void write(const IfcGeom::BRepElement* element) override {
		serializer_->write(element);
	}

	void setUnitNameAndMagnitude(const std::string& name, float magnitude) override {
		serializer_->setUnitNameAndMagnitude(name, magnitude);
	}

	IfcGeom::Element* read(
		ifcopenshell::file& file,
		const std::string& guid,
		const std::string& representation_id,
		read_type rt = READ_BREP
	) override {
		return serializer_->read(file, guid, representation_id, rt);
	}

	std::string object_id(const IfcGeom::Element* element) override {
		return serializer_->object_id(element);
	}

private:
	boost::shared_ptr<GeometrySerializer> serializer_;
};
%}

%extend GeometrySerializer {
	bool ready() {
		return $self->ready();
	}

	bool is_streaming() const {
		return $self->is_streaming();
	}

	void writeHeader() {
		$self->writeHeader();
	}

	void finalize() {
		$self->finalize();
	}

	void setFile(ifcopenshell::file& file) {
		$self->setFile(file);
	}
}

%extend ifcopenshell::geometry::taxonomy::style {
	size_t instance_id() const {
		if (!self->instance) {
			return 0;
		}
		return self->instance.id();
	}
}


%define assign_component_acccess(item_name)

%extend ifcopenshell::geometry::taxonomy::item_name {
	PyObject* components_() const {
		return eigen_to_python_tuple(self->ccomponents());
	}

	%pythoncode %{
		components = property(components_)
	%}
};

%enddef

assign_component_acccess(point3);
assign_component_acccess(direction3);
assign_component_acccess(matrix4);
assign_component_acccess(colour);

%define assign_children_access(item_name, children_type)

%extend ifcopenshell::geometry::taxonomy::item_name {
	// swig does not accept auto here as the return type
	const std::vector<ifcopenshell::geometry::taxonomy::children_type::ptr>& children_() const {
		return $self->children;
	}

	const ifcopenshell::geometry::taxonomy::children_type::ptr& __getitem__(int index) const {
		if (index < 0 || index >= $self->children.size()) {
			throw std::runtime_error("Index " + std::to_string(index) + " is out of bounds for an array of length " + std::to_string($self->children.size()));
		}
		return $self->children[index];
	}

	%pythoncode %{
		children = property(children_)
		def __iter__(self):
			return iter(self.children)
	%}
};

%enddef

assign_children_access(collection, geom_item);
assign_children_access(loop, edge);
assign_children_access(face, loop);
assign_children_access(shell, face);
assign_children_access(solid, shell);
assign_children_access(loft, geom_item);
assign_children_access(boolean_result, geom_item);

%define assign_matrix_access(item_name)

%extend ifcopenshell::geometry::taxonomy::item_name {
	// swig does not accept auto here as the return type
	const ifcopenshell::geometry::taxonomy::matrix4::ptr& matrix_() const {
		return $self->matrix;
	}

	%pythoncode %{
		matrix = property(matrix_)
	%}
};

%enddef

assign_matrix_access(line);
assign_matrix_access(circle);
assign_matrix_access(ellipse);
assign_matrix_access(collection);
assign_matrix_access(solid);
assign_matrix_access(face);
assign_matrix_access(plane);
assign_matrix_access(cylinder);
assign_matrix_access(sphere);
assign_matrix_access(torus);
assign_matrix_access(extrusion);
assign_matrix_access(revolve);

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
	void set_(const std::string& name, ifcopenshell::geometry::settings::FunctionStepMethod val) {
		return $self->set(name, val);
	}
	void set_(const std::string& name, ifcopenshell::geometry::settings::OutputDimensionalityTypes val) {
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
	void set_(const std::string& name, const std::vector<double>& val) {
		return $self->set(name, val);
	}
	void set_(const std::string& name, const std::vector<std::string>& val) {
		// Python sequences cannot distinguish std::vector<std::string> from std::set<std::string>.
		if ($self->get_type(name) == "std::set<std::string>") {
			return $self->set(name, std::set<std::string>(val.begin(), val.end()));
		}
		return $self->set(name, val);
	}
	ifcopenshell::geometry::Settings::value_variant_t get_(const std::string& name) {
		return $self->get(name);
	}
	std::vector<std::string> setting_names() {
		return $self->setting_names();
	}
	std::string get_type(const std::string& name) {
		return $self->get_type(name);
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
	std::string get_type(const std::string& name) {
		return $self->get_type(name);
	}
}

%template(ray_intersection_results) std::vector<IfcGeom::ray_intersection_result>;

%template(clashes) std::vector<IfcGeom::clash>;

%ignore IfcGeom::tree::uint8_to_b64;

%include "../ifcgeom/tree.h"

%extend IfcGeom::tree {

	std::vector<express::Base> select_box(const express::Base& e, bool completely_within = false, double extend=-1.e-5) const {
		if (!e.declaration().is("IfcProduct")) {
			throw ifcopenshell::exception("Instance should be an IfcProduct");
		}
		return cast_vector<express::Base>($self->select_box(e.as<express::Entity>(), completely_within, extend));
	}

	std::vector<express::Base> select_box(const std::vector<double>& p) const {
		if (p.size() != 3) {
			throw ifcopenshell::exception("Point should be a sequence of 3 floats");
		}
		IfcGeom::tree_point point = {{ p[0], p[1], p[2] }};
		return cast_vector<express::Base>($self->select_box(point));
	}

	std::vector<express::Base> select_box(const std::vector<std::vector<double>>& b, bool completely_within = false) const {
		if (b.size() != 2 || b[0].size() != 3 || b[1].size() != 3) {
			throw ifcopenshell::exception("Bounding box should be a sequence of 2 x 3 floats");
		}
		IfcGeom::tree_box box = {{
			{ b[0][0], b[0][1], b[0][2] },
			{ b[1][0], b[1][1], b[1][2] }
		}};
		return cast_vector<express::Base>($self->select_box(box, completely_within));
	}

	std::vector<express::Base> select(const express::Base& e, bool completely_within = false, double extend = 0.0) const {
		if (!e.declaration().is("IfcProduct")) {
			throw ifcopenshell::exception("Instance should be an IfcProduct");
		}
		return cast_vector<express::Base>($self->select(e.as<express::Entity>(), completely_within, extend));
	}

	std::vector<express::Base> select(const std::vector<double>& p, double extend=0.0) const {
		if (p.size() != 3) {
			throw ifcopenshell::exception("Point should be a sequence of 3 floats");
		}
		IfcGeom::tree_point point = {{ p[0], p[1], p[2] }};
		return cast_vector<express::Base>($self->select(point, extend));
	}

	std::vector<express::Base> select(const IfcGeom::Element* elem, bool completely_within = false, double extend = -1.e-5) const {
		return cast_vector<express::Base>($self->select(elem, completely_within, extend));
	}

	std::vector<IfcGeom::ray_intersection_result> select_ray(const std::vector<double>& p0, const std::vector<double>& d, double length = 1000.) const {
		if (p0.size() != 3 || d.size() != 3) {
			throw ifcopenshell::exception("Origin and direction should be sequences of 3 floats");
		}
		IfcGeom::tree_point origin = {{ p0[0], p0[1], p0[2] }};
		IfcGeom::tree_point direction = {{ d[0], d[1], d[2] }};
		return $self->select_ray(origin, direction, length);
	}

}

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
	PyObject* operator()(IfcGeom::Transformation* transformation) const {
		return SWIG_NewPointerObj(SWIG_as_voidptr(transformation), SWIGTYPE_p_IfcGeom__Transformation, SWIG_POINTER_OWN);
	}
};
%}

// Note that these elements ARE to be owned by SWIG/Python
%typemap(out) std::variant<IfcGeom::Element*, IfcGeom::Representation::Representation*, IfcGeom::Transformation*> {
	// See which type is set and return appropriate
	$result = std::visit(ShapeRTTI(), (std::variant<IfcGeom::Element*, IfcGeom::Representation::Representation*, IfcGeom::Transformation*>) $1);
}

%newobject construct_iterator;
%newobject construct_iterator_with_include_exclude;
%newobject construct_iterator_with_include_exclude_globalid;
%newobject construct_iterator_with_include_exclude_id;
%newobject create_geometry_serializer;

// I couldn't get the vector<string> typemap to be applied when %extending Iterator constructor.
// anyway it does not matter as SWIG generates C code without actual constructors
%inline %{
	GeometrySerializer* create_geometry_serializer(
		const std::string& extension,
		const std::string& output_filename,
		const std::string& output_temp_filename,
		ifcopenshell::geometry::Settings& geometry_settings,
		const ifcopenshell::geometry::SerializerSettings& serializer_settings
	) {
		return new PythonPluginGeometrySerializer(
			extension,
			output_filename,
			output_temp_filename,
			geometry_settings,
			serializer_settings
		);
	}

	GeometrySerializer* create_geometry_serializer(
		const std::string& extension,
		const stream_or_filename& output_filename,
		const stream_or_filename& output_temp_filename,
		ifcopenshell::geometry::Settings& geometry_settings,
		const ifcopenshell::geometry::SerializerSettings& serializer_settings
	) {
		return new PythonPluginGeometrySerializer(
			extension,
			output_filename,
			output_temp_filename,
			geometry_settings,
			serializer_settings
		);
	}

	// I couldn't get the vector<string> typemap to be applied when %extending Iterator constructor.
	// anyway it does not matter as SWIG generates C code without actual constructors
	IfcGeom::Iterator* construct_iterator(const std::string& geometry_library, ifcopenshell::geometry::Settings settings, ifcopenshell::file* file, int num_threads, logger* logger = nullptr) {
		::logger& logger_ = logger_or_root(logger);
		return new IfcGeom::Iterator(ifcopenshell::geometry::kernels::construct(file, geometry_library, settings), settings, file, num_threads, logger_);
	}

	IfcGeom::Iterator* construct_iterator_with_include_exclude(const std::string& geometry_library, ifcopenshell::geometry::Settings settings, ifcopenshell::file* file, std::vector<std::string> elems, bool include, int num_threads, logger* logger = nullptr) {
		::logger& logger_ = logger_or_root(logger);
		std::set<std::string> elems_set(elems.begin(), elems.end());
		IfcGeom::entity_filter ef{ include, false, elems_set };
		return new IfcGeom::Iterator(ifcopenshell::geometry::kernels::construct(file, geometry_library, settings), settings, file, {ef}, num_threads, logger_);
	}

	IfcGeom::Iterator* construct_iterator_with_include_exclude_globalid(const std::string& geometry_library, ifcopenshell::geometry::Settings settings, ifcopenshell::file* file, std::vector<std::string> elems, bool include, int num_threads, logger* logger = nullptr) {
		::logger& logger_ = logger_or_root(logger);
		std::set<std::string> elems_set(elems.begin(), elems.end());
		IfcGeom::attribute_filter af;
		af.attribute_name = "GlobalId";
		af.populate(elems_set);
		af.include = include;
		return new IfcGeom::Iterator(ifcopenshell::geometry::kernels::construct(file, geometry_library, settings), settings, file, {af}, num_threads, logger_);
	}

	IfcGeom::Iterator* construct_iterator_with_include_exclude_id(const std::string& geometry_library, ifcopenshell::geometry::Settings settings, ifcopenshell::file* file, std::vector<int> elems, bool include, int num_threads, logger* logger = nullptr) {
		::logger& logger_ = logger_or_root(logger);
		std::set<int> elems_set(elems.begin(), elems.end());
		IfcGeom::instance_id_filter af(include, false, elems_set);
		return new IfcGeom::Iterator(ifcopenshell::geometry::kernels::construct(file, geometry_library, settings), settings, file, {af}, num_threads, logger_);
	}
%}

%extend IfcGeom::Representation::Triangulation {

	std::pair<const char*, size_t> faces_buffer() const {
		return vector_to_buffer(self->faces());
	}

	std::pair<const char*, size_t> edges_buffer() const {
		return vector_to_buffer(self->edges());
	}

	std::pair<const char*, size_t> material_ids_buffer() const {
		return vector_to_buffer(self->material_ids());
	}

	std::pair<const char*, size_t> item_ids_buffer() const {
		return vector_to_buffer(self->item_ids());
	}

	std::pair<const char*, size_t> edges_item_ids_buffer() const {
		return vector_to_buffer(self->edges_item_ids());
	}

	std::pair<const char*, size_t> verts_buffer() const {
		return vector_to_buffer(self->verts());
	}

	std::pair<const char*, size_t> normals_buffer() const {
		return vector_to_buffer(self->normals());
	}

    PyObject* colors_buffer() const {
        std::vector<double> clrs;
        clrs.reserve(self->materials().size() * 4);
        for (auto& mptr : self->materials()) {
			auto& m = *mptr;
            if (m.diffuse) {
                clrs.push_back(m.diffuse.ccomponents()[0]);
                clrs.push_back(m.diffuse.ccomponents()[1]);
                clrs.push_back(m.diffuse.ccomponents()[2]);
            } else {
                clrs.push_back(0.);
                clrs.push_back(0.);
                clrs.push_back(0.);
            }
            if (m.has_transparency()) {
                clrs.push_back(1. - m.transparency);
            } else {
                clrs.push_back(1.);
            }
        }
        auto p = vector_to_buffer(clrs);
        return PyBytes_FromStringAndSize(p.first, p.second);
    }

    %pythoncode %{
        # Hide the getters with read-only property implementations
        faces_tri = property(faces)
        polyhedral_faces_without_holes = property(polyhedral_faces_without_holes)
        polyhedral_faces_with_holes = property(polyhedral_faces_with_holes)
        def get_faces(self):
            if self.faces_tri: 
                return self.faces_tri
            elif self.polyhedral_faces_without_holes:
                return self.polyhedral_faces_without_holes
            else:
                return self.polyhedral_faces_with_holes
        faces = property(get_faces)
        edges = property(edges)
        material_ids = property(material_ids)
        materials = property(materials)
        verts = property(verts)
        normals = property(normals)
        item_ids = property(item_ids)
        uvs = property(uvs)
        edges_item_ids = property(edges_item_ids)

        faces_buffer = property(faces_buffer)
        edges_buffer = property(edges_buffer)
        material_ids_buffer = property(material_ids_buffer)
        item_ids_buffer = property(item_ids_buffer)
        edges_item_ids_buffer = property(edges_item_ids_buffer)
        verts_buffer = property(verts_buffer)
        normals_buffer = property(normals_buffer)
        colors_buffer = property(colors_buffer)
    %}
};

%extend IfcGeom::Representation::Representation {
	%pythoncode %{
        # Hide the getters with read-only property implementations
        id = property(id)
	%}
};

%extend IfcGeom::Representation::Serialization {
	%pythoncode %{
        # Hide the getters with read-only property implementations
        brep_data = property(brep_data)
        surface_styles = property(surface_styles)
        surface_style_ids = property(surface_style_ids)
	%}
};

%extend IfcGeom::Element {
    std::pair<const char*, size_t> transformation_buffer() const {
        // @todo check whether needs to be transposed
        const double* data = self->transformation().data()->ccomponents().data();
        return { reinterpret_cast<const char*>(data), 16 * sizeof(double) };
    }

    const express::Base product_() const {
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

        transformation_buffer = property(transformation_buffer)
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

	static std::variant<IfcGeom::Element*, IfcGeom::Representation::Representation*, IfcGeom::Transformation*> helper_fn_create_shape(logger& logger, const std::string& geometry_library, ifcopenshell::geometry::Settings& st, const express::Base& instance, const express::Base& representation = express::Base()) {
		ifcopenshell::file* file = instance.file();

		ifcopenshell::geometry::Converter kernel(ifcopenshell::geometry::kernels::construct(file, geometry_library, st), file, st, logger);
		if (instance.declaration().is("IfcProduct")) {
			if (representation && !representation.declaration().is("IfcRepresentation")) {
				throw ifcopenshell::exception("Supplied representation not of type IfcRepresentation");
			}

			auto selected_representation = representation ? representation : kernel.mapping()->representation_of(instance);
			if (!selected_representation) {
				throw ifcopenshell::exception("No suitable IfcRepresentation found");
			}

			IfcGeom::BRepElement* brep = kernel.create_brep_for_representation_and_product(selected_representation, instance);
			if (!brep) {
				std::ostringstream oss_repr, oss_product;
				selected_representation.to_string(oss_repr);
				instance.to_string(oss_product);
				throw ifcopenshell::exception("Failed to process shape. Product: " + oss_product.str() + ", representation: " + oss_repr.str());
			}
			if (st.get<ifcopenshell::geometry::settings::IteratorOutput>().get() == ifcopenshell::geometry::settings::SERIALIZED) {
				IfcGeom::SerializedElement* serialization = new IfcGeom::SerializedElement(*brep);
				delete brep;
				return serialization;
			} else if (st.get<ifcopenshell::geometry::settings::IteratorOutput>().get() == ifcopenshell::geometry::settings::TRIANGULATED) {
				IfcGeom::TriangulationElement* triangulation = new IfcGeom::TriangulationElement(*brep);
				delete brep;
				return triangulation;
			} else {
				return brep;
			}
		} else if (instance.declaration().is("IfcPlacement") || instance.declaration().is("IfcObjectPlacement")) {
			auto item = ifcopenshell::geometry::taxonomy::cast<ifcopenshell::geometry::taxonomy::matrix4>(kernel.mapping()->map(instance));
			if (item == nullptr) {
				throw ifcopenshell::exception("Failed to convert placement");
			}
            if (st.get<ifcopenshell::geometry::settings::ConvertBackUnits>().get()) {
                // we pass the settings to the Transformation object, but access the data just offloads to the
                // generic cartesian_base<Matrix4> so there's no time to apply the settings to the translation part.
                item = ifcopenshell::geometry::taxonomy::matrix4::ptr(item->clone_());
                item->components().col(3).head<3>() /= kernel.settings().get<ifcopenshell::geometry::settings::LengthUnit>().get();
			}
			return new IfcGeom::Transformation(kernel.settings(), item);
		} else {
			if (!representation) {
				if (instance.declaration().is("IfcRepresentationItem") ||
					instance.declaration().is("IfcRepresentation") ||
					// https://github.com/IfcOpenShell/IfcOpenShell/issues/1649
					instance.declaration().is("IfcProfileDef")
				) {
					IfcGeom::ConversionResults shapes;
					try {
						shapes = kernel.convert(instance);
					} catch (...) {
						std::ostringstream oss;
						instance.to_string(oss);
						throw ifcopenshell::exception("Failed to process shape. Instance: " + oss.str());
					}

					IfcGeom::Representation::BRep brep(kernel.settings(), instance.declaration().name(), to_locale_invariant_string(instance.id()), shapes);
					try {
						if (st.get<ifcopenshell::geometry::settings::IteratorOutput>().get() == ifcopenshell::geometry::settings::SERIALIZED) {
							return new IfcGeom::Representation::Serialization(brep);
						} else if (st.get<ifcopenshell::geometry::settings::IteratorOutput>().get() == ifcopenshell::geometry::settings::TRIANGULATED) {
							return new IfcGeom::Representation::Triangulation(brep);
						}
					} catch (...) {
						throw ifcopenshell::exception("error during shape serialization");
					}
				}
			} else {
				throw ifcopenshell::exception("Invalid additional representation specified");
			}
		}
		return std::variant<IfcGeom::Element*, IfcGeom::Representation::Representation*, IfcGeom::Transformation*>();
	}
%}

%typemap(out) ifcopenshell::geometry::taxonomy::item::ptr {
	$result = item_to_pyobject($1);
}

%{
template <typename T>
ifcopenshell::geometry::taxonomy::item::ptr try_upcast(PyObject* obj0, swig_type_info* info) {
    typename T::ptr *arg1 = 0 ;
    void *argp1 ;
    typename T::ptr tempshared1 ;

    int newmem = 0;
    auto res1 = SWIG_ConvertPtrAndOwn(obj0, &argp1, info,  0 , &newmem);
    if (SWIG_IsOK(res1)) {
        if (newmem & SWIG_CAST_NEW_MEMORY) {
            if (argp1) tempshared1 = *reinterpret_cast< typename T::ptr * >(argp1);
            delete reinterpret_cast< typename T::ptr * >(argp1);
            arg1 = &tempshared1;
        } else {
            arg1 = (argp1) ? reinterpret_cast< typename T::ptr * >(argp1) : &tempshared1;
        }
        return std::static_pointer_cast<ifcopenshell::geometry::taxonomy::item>(*arg1);
    }
    return nullptr;
}
%}

%inline %{
	ifcopenshell::geometry::taxonomy::item::ptr map_shape(ifcopenshell::geometry::Settings& settings, const express::Base& instance) {
        std::unique_ptr<ifcopenshell::geometry::abstract_mapping> mapping(ifcopenshell::geometry::impl::mapping_implementations().construct(instance.file(), settings));
		return mapping->map(instance);
	}
%}

%inline %{
	static std::variant<IfcGeom::Element*, IfcGeom::Representation::Representation*, IfcGeom::Transformation*> create_shape(ifcopenshell::geometry::Settings& settings, const express::Base& instance, const express::Base& representation, const char* const geometry_library="opencascade", logger* logger = nullptr) {
		return helper_fn_create_shape(logger_or_root(logger), geometry_library, settings, instance, representation);
	}

	// Manual definition of overload without representation argument
	static std::variant<IfcGeom::Element*, IfcGeom::Representation::Representation*, IfcGeom::Transformation*> create_shape(ifcopenshell::geometry::Settings& settings, const express::Base& instance, const char* const geometry_library="opencascade", logger* logger = nullptr) {
		return create_shape(settings, instance, express::Base(), geometry_library, logger);
	}
%}

// @todo bring back serialization OCCT -> IFC by means of opencascade_geometry_ifc_writer_registry

%template(OpaqueCoordinate_3) IfcGeom::OpaqueCoordinate<3>;
%template(OpaqueCoordinate_4) IfcGeom::OpaqueCoordinate<4>;

%newobject create_epeck;

%inline %{
	IfcGeom::OpaqueNumber* create_epeck(int i) {
		return new IfcGeom::OpaqueNumber(i);
	}
	IfcGeom::OpaqueNumber* create_epeck(double d) {
		return new IfcGeom::OpaqueNumber(d);
	}
	IfcGeom::OpaqueNumber* create_epeck(const std::string& s) {
		return new IfcGeom::OpaqueNumber(std::stod(s));
	}
%}

%inline %{
	IfcGeom::ConversionResultShape* nary_union(PyObject* sequence) {
		IfcGeom::ConversionResultShape* result = nullptr;
		std::string backend_id;
		auto identity = ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::matrix4>();
		for(Py_ssize_t i = 0; i < PySequence_Size(sequence); ++i) {
			PyObject* element = PySequence_GetItem(sequence, i);
			void* argp1 = nullptr;
			auto res1 = SWIG_ConvertPtr(element, &argp1, SWIGTYPE_p_IfcGeom__ConversionResultShape, 0);
			if (SWIG_IsOK(res1)) {
				auto arg1 = reinterpret_cast<IfcGeom::ConversionResultShape*>(argp1);
				auto element_backend_id = std::string(arg1->backend_id());
				if (backend_id.empty()) {
					backend_id = element_backend_id;
					result = arg1->moved(identity);
				} else {
					if (element_backend_id != backend_id) {
						delete result;
						throw ifcopenshell::exception("nary_union requires shapes from the same geometry backend");
					}
					auto next = result->add(arg1);
					if (!next) {
						delete result;
						throw ifcopenshell::exception("nary_union failed for backend " + backend_id);
					}
					delete result;
					result = next;
				}
			}
		}
		if (!result) {
			throw ifcopenshell::exception("nary_union requires at least one shape");
		}
		return result;
	}
%}

%extend IfcGeom::ConversionResultShape {
	std::string serialize_obj() {
		ifcopenshell::geometry::Settings settings;
		std::unique_ptr<IfcGeom::Representation::Triangulation> triangulation($self->Triangulate(settings));
		std::ostringstream result;

		for (auto it = triangulation->verts().begin(); it != triangulation->verts().end();) {
			result << "v " << *(it++) << " " << *(it++) << " " << *(it++) << "\n";
		}
		for (auto it = triangulation->normals().begin(); it != triangulation->normals().end();) {
			result << "vn " << *(it++) << " " << *(it++) << " " << *(it++) << "\n";
		}

		const bool has_normals = !triangulation->normals().empty();
		for (auto it = triangulation->faces().begin(); it != triangulation->faces().end();) {
			const auto v1 = *(it++) + 1;
			const auto v2 = *(it++) + 1;
			const auto v3 = *(it++) + 1;
			if (has_normals) {
				result << "f "
					<< v1 << "//" << v1 << " "
					<< v2 << "//" << v2 << " "
					<< v3 << "//" << v3 << "\n";
			} else {
				result << "f " << v1 << " " << v2 << " " << v3 << "\n";
			}
		}

		return result.str();
	}

	void convex_tag(bool b) {
		(void)b;
		throw ifcopenshell::exception("convex_tag is not available through the generic conversion result interface");
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

#ifdef IFOPSH_WITH_CGAL

%ignore hlr_writer;
%ignore hlr_calc;
%ignore occt_join;
%ignore prefiltered_hlr;
%ignore svgfill::svg_to_line_segments;
%ignore svgfill::line_segments_to_polygons;
%ignore svgfill::svg_to_polygons;
%ignore svgfill::arrange_polygons;
%ignore svgfill::abstract_arrangement;
%ignore svgfill::context::delete_same_facet_edge_pairs;

%template(svg_line_segments) std::vector<std::array<svgfill::point_2, 2>>;
%template(svg_groups_of_line_segments) std::vector<std::vector<std::array<svgfill::point_2, 2>>>;
%template(svg_point) std::array<double, 2>;
%template(line_segment) std::array<svgfill::point_2, 2>;
%template(svg_polygons) std::vector<svgfill::polygon_2>;
%template(svg_groups_of_polygons) std::vector<std::vector<svgfill::polygon_2>>;
%template(svg_loop) std::vector<std::array<double, 2>>;
%template(svg_loops) std::vector<std::vector<std::array<double, 2>>>;

%extend IfcGeom::OpaqueCoordinate {
	%pythoncode %{
		__len__ = size
		def __iter__(self):
			yield from (self.get(i) for i in range(len(self)))
	%}
}

%extend IfcGeom::OpaqueNumber {
	%pythoncode %{
		__abs__ = abs
	%}
}

%template(OpaqueCoordinate_3) IfcGeom::OpaqueCoordinate<3>;
%template(OpaqueCoordinate_4) IfcGeom::OpaqueCoordinate<4>;

#if 0
%inline %{
	IfcGeom::OpaqueNumber create_epeck(int i) {
		return ifcopenshell::geometry::NumberEpeck(i);
	}
	IfcGeom::OpaqueNumber create_epeck(double d) {
		return ifcopenshell::geometry::NumberEpeck(d);
	}
	IfcGeom::OpaqueNumber create_epeck(const std::string& s) {
		return ifcopenshell::geometry::NumberEpeck(typename CGAL::Epeck::FT::ET(s));
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
#endif

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
	std::vector<std::vector<svgfill::line_segment_2>> svg_to_line_segments(const std::string& data, const std::optional<std::string>& class_name) {
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
			throw std::runtime_error("Failed process line segments");
		}
	}

	std::vector<svgfill::polygon_2> svg_to_polygons(const std::string& data, const std::optional<std::string>& class_name) {
		std::vector<svgfill::polygon_2> r;
		if (svgfill::svg_to_polygons(data, class_name, r)) {
			return r;
		} else {
			throw std::runtime_error("Failed to read SVG");
		}	
	}

	std::vector<svgfill::polygon_2> arrange_polygons(svgfill::arrange_polygon_settings settings, const std::vector<svgfill::polygon_2>& polygons, logger* logger = nullptr) {
		std::vector<svgfill::polygon_2> r;
		if (svgfill::arrange_polygons(settings, polygons, r, logger_or_root(logger))) {
			return r;
		} else {
			throw std::runtime_error("Failed to arrange polygons");
		}
	}
%}

%define assign_repr(item_name)

%extend item_name {
	%pythoncode %{
		__repr__ = taxonomy_item_repr
	%}
};

%enddef

assign_repr(ifcopenshell::geometry::taxonomy::boolean_result)
assign_repr(ifcopenshell::geometry::taxonomy::bspline_curve)
assign_repr(ifcopenshell::geometry::taxonomy::bspline_surface)
assign_repr(ifcopenshell::geometry::taxonomy::circle)
assign_repr(ifcopenshell::geometry::taxonomy::collection)
assign_repr(ifcopenshell::geometry::taxonomy::colour)
assign_repr(ifcopenshell::geometry::taxonomy::cylinder)
assign_repr(ifcopenshell::geometry::taxonomy::direction3)
assign_repr(ifcopenshell::geometry::taxonomy::edge)
assign_repr(ifcopenshell::geometry::taxonomy::ellipse)
assign_repr(ifcopenshell::geometry::taxonomy::extrusion)
assign_repr(ifcopenshell::geometry::taxonomy::face)
assign_repr(ifcopenshell::geometry::taxonomy::line)
assign_repr(ifcopenshell::geometry::taxonomy::loft)
assign_repr(ifcopenshell::geometry::taxonomy::loop)
assign_repr(ifcopenshell::geometry::taxonomy::matrix4)
assign_repr(ifcopenshell::geometry::taxonomy::node)
assign_repr(ifcopenshell::geometry::taxonomy::offset_curve)
assign_repr(ifcopenshell::geometry::taxonomy::function_item)
assign_repr(ifcopenshell::geometry::taxonomy::functor_item)
assign_repr(ifcopenshell::geometry::taxonomy::piecewise_function)
assign_repr(ifcopenshell::geometry::taxonomy::gradient_function)
assign_repr(ifcopenshell::geometry::taxonomy::cant_function)
assign_repr(ifcopenshell::geometry::taxonomy::offset_function)
assign_repr(ifcopenshell::geometry::taxonomy::plane)
assign_repr(ifcopenshell::geometry::taxonomy::point3)
assign_repr(ifcopenshell::geometry::taxonomy::revolve)
assign_repr(ifcopenshell::geometry::taxonomy::shell)
assign_repr(ifcopenshell::geometry::taxonomy::solid)
assign_repr(ifcopenshell::geometry::taxonomy::sphere)
assign_repr(ifcopenshell::geometry::taxonomy::torus)
assign_repr(ifcopenshell::geometry::taxonomy::style)
assign_repr(ifcopenshell::geometry::taxonomy::sweep_along_curve)


#endif
