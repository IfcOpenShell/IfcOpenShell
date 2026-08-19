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
%ignore ifcopenshell::geom::conversion_result::shape;
%ignore boost::hash_value;
%ignore ifcopenshell::geom::native_element::geometry_pointer;
%ignore ifcopenshell::geom::triangulation_element::geometry_pointer;
%ignore ifcopenshell::geom::geometry_conversion_result::native_elements;
%ignore ifcopenshell::geom::geometry_conversion_result::elements;

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
// ifcopenshell::geom::settings functions degrade to return a read only value
%typemap(out) double& {
	$result = SWIG_From_double(*$1);
}
%typemap(out) bool& {
	$result = PyBool_FromLong(static_cast<long>(*$1));
}

%typemap(out) ifcopenshell::geom::opaque_number {
	$result = SWIG_NewPointerObj(SWIG_as_voidptr(new ifcopenshell::geom::opaque_number($1)), SWIGTYPE_p_ifcopenshell__geom__opaque_number, SWIG_POINTER_OWN);
}

%typemap(in) const ifcopenshell::geom::opaque_number& (ifcopenshell::geom::opaque_number temp) {
	void* argp = nullptr;
	int res = SWIG_ConvertPtr($input, &argp, SWIGTYPE_p_ifcopenshell__geom__opaque_number, 0);
	if (!SWIG_IsOK(res) || !argp) {
		SWIG_exception_fail(SWIG_ArgError(res), "Expected ifcopenshell::geom::opaque_number");
	}
	temp = *reinterpret_cast<ifcopenshell::geom::opaque_number*>(argp);
	$1 = &temp;
}

// Use RTTI to return the most specialized element proxy. The ownership flag is
// supplied by the wrapped function, so iterator results can transfer ownership
// while borrowed serializer results remain non-owning.
%typemap(out) ifcopenshell::geom::element* {
	ifcopenshell::geom::serialized_element* serialized_elem = dynamic_cast<ifcopenshell::geom::serialized_element*>($1);
	ifcopenshell::geom::triangulation_element* triangulation_elem = dynamic_cast<ifcopenshell::geom::triangulation_element*>($1);
	ifcopenshell::geom::native_element* brep_elem = dynamic_cast<ifcopenshell::geom::native_element*>($1);
	if (triangulation_elem) {
		$result = SWIG_NewPointerObj(SWIG_as_voidptr(triangulation_elem), SWIGTYPE_p_ifcopenshell__geom__triangulation_element, $owner);
	} else if (serialized_elem) {
		$result = SWIG_NewPointerObj(SWIG_as_voidptr(serialized_elem), SWIGTYPE_p_ifcopenshell__geom__serialized_element, $owner);
	} else if (brep_elem) {
		$result = SWIG_NewPointerObj(SWIG_as_voidptr(brep_elem), SWIGTYPE_p_ifcopenshell__geom__native_element, $owner);
	} else {
		$result = SWIG_NewPointerObj(SWIG_as_voidptr($1), SWIGTYPE_p_ifcopenshell__geom__element, $owner);
	}
}

%newobject ifcopenshell::geom::native::item;
%newobject ifcopenshell::geom::native::as_compound;

%newobject ifcopenshell::geom::conversion_result_shape::halfspaces;
%newobject ifcopenshell::geom::conversion_result_shape::box;
%newobject ifcopenshell::geom::conversion_result_shape::solid;
%newobject ifcopenshell::geom::conversion_result_shape::add;
%newobject ifcopenshell::geom::conversion_result_shape::subtract;
%newobject ifcopenshell::geom::conversion_result_shape::intersect;
%newobject ifcopenshell::geom::conversion_result_shape::concat;
%newobject ifcopenshell::geom::conversion_result_shape::moved;
%newobject ifcopenshell::geom::conversion_result_shape::wrap_in_compound;


%newobject nary_union;


%inline %{
template <typename T>
std::pair<char const*, size_t> vector_to_buffer(const T& t) {
    using v = typename std::remove_reference<decltype(t)>::type;
    return { reinterpret_cast<const char*>(t.data()), t.size() * sizeof(typename v::value_type) };
}
%}

%ignore ifcopenshell::geom::taxonomy::item::print;

%typemap(out) std::variant<boost::blank, ifcopenshell::geom::taxonomy::point3::ptr, double> {
	if ($1.index() == 0) {
		Py_INCREF(Py_None);
		return Py_None;
	} else if ($1.index() == 1) {
		return SWIG_NewPointerObj(SWIG_as_voidptr(new std::shared_ptr<ifcopenshell::geom::taxonomy::point3>(std::get<ifcopenshell::geom::taxonomy::point3::ptr>($1))), SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__point3_t, 0 | SWIG_POINTER_OWN);
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

%typemap(in) ifcopenshell::geom::taxonomy::item::ptr {
	// @this is really annoying, but apparently inheritance
	// is lost in swig in the shared_ptr type hiearchy
	using namespace ifcopenshell::geom::taxonomy;
	if (!$1) $1 = try_upcast<boolean_result>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__boolean_result_t);
	if (!$1) $1 = try_upcast<bspline_curve>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__bspline_curve_t);
	if (!$1) $1 = try_upcast<bspline_surface>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__bspline_surface_t);
	if (!$1) $1 = try_upcast<circle>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__circle_t);
	if (!$1) $1 = try_upcast<collection>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__collection_t);
	if (!$1) $1 = try_upcast<colour>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__colour_t);
	if (!$1) $1 = try_upcast<cylinder>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__cylinder_t);
	if (!$1) $1 = try_upcast<direction3>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__direction3_t);
	if (!$1) $1 = try_upcast<edge>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__edge_t);
	if (!$1) $1 = try_upcast<ellipse>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__ellipse_t);
	if (!$1) $1 = try_upcast<extrusion>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__extrusion_t);
	if (!$1) $1 = try_upcast<face>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__face_t);
	if (!$1) $1 = try_upcast<line>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__line_t);
	if (!$1) $1 = try_upcast<loft>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__loft_t);
	if (!$1) $1 = try_upcast<loop>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__loop_t);
	if (!$1) $1 = try_upcast<matrix4>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__matrix4_t);
	if (!$1) $1 = try_upcast<node>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__node_t);
	if (!$1) $1 = try_upcast<offset_curve>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__offset_curve_t);
	if (!$1) $1 = try_upcast<function_item>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__function_item_t);
	if (!$1) $1 = try_upcast<functor_item>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__functor_item_t);
	if (!$1) $1 = try_upcast<piecewise_function>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__piecewise_function_t);
	if (!$1) $1 = try_upcast<gradient_function>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__gradient_function_t);
	if (!$1) $1 = try_upcast<cant_function>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__cant_function_t);
	if (!$1) $1 = try_upcast<offset_function>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__offset_function_t);
	if (!$1) $1 = try_upcast<plane>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__plane_t);
	if (!$1) $1 = try_upcast<point3>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__point3_t);
	if (!$1) $1 = try_upcast<revolve>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__revolve_t);
	if (!$1) $1 = try_upcast<shell>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__shell_t);
	if (!$1) $1 = try_upcast<solid>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__solid_t);
	if (!$1) $1 = try_upcast<sphere>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__sphere_t);
	if (!$1) $1 = try_upcast<torus>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__torus_t);
	if (!$1) $1 = try_upcast<style>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__style_t);
	if (!$1) $1 = try_upcast<sweep_along_curve>($input, SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geom__taxonomy__sweep_along_curve_t);
}

%inline %{
std::string taxonomy_item_repr(ifcopenshell::geom::taxonomy::item::ptr i) {
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

%shared_ptr(ifcopenshell::geom::taxonomy::boolean_result);
%shared_ptr(ifcopenshell::geom::taxonomy::item);
%shared_ptr(ifcopenshell::geom::taxonomy::implicit_item);
%shared_ptr(ifcopenshell::geom::taxonomy::function_item);
%shared_ptr(ifcopenshell::geom::taxonomy::functor_item);
%shared_ptr(ifcopenshell::geom::taxonomy::piecewise_function);
%shared_ptr(ifcopenshell::geom::taxonomy::gradient_function);
%shared_ptr(ifcopenshell::geom::taxonomy::cant_function);
%shared_ptr(ifcopenshell::geom::taxonomy::offset_function);
%shared_ptr(ifcopenshell::geom::taxonomy::less_functor);
%shared_ptr(ifcopenshell::geom::taxonomy::eigen_base);
%shared_ptr(ifcopenshell::geom::taxonomy::matrix4);
%shared_ptr(ifcopenshell::geom::taxonomy::colour);
%shared_ptr(ifcopenshell::geom::taxonomy::style);
%shared_ptr(ifcopenshell::geom::taxonomy::geom_item);
%shared_ptr(ifcopenshell::geom::taxonomy::cartesian_base);
%shared_ptr(ifcopenshell::geom::taxonomy::point3);
%shared_ptr(ifcopenshell::geom::taxonomy::direction3);
%shared_ptr(ifcopenshell::geom::taxonomy::curve);
%shared_ptr(ifcopenshell::geom::taxonomy::line);
%shared_ptr(ifcopenshell::geom::taxonomy::circle);
%shared_ptr(ifcopenshell::geom::taxonomy::ellipse);
%shared_ptr(ifcopenshell::geom::taxonomy::bspline_curve);
%shared_ptr(ifcopenshell::geom::taxonomy::offset_curve);
%shared_ptr(ifcopenshell::geom::taxonomy::trimmed_curve);
%shared_ptr(ifcopenshell::geom::taxonomy::edge);
%shared_ptr(ifcopenshell::geom::taxonomy::collection_base);
%shared_ptr(ifcopenshell::geom::taxonomy::collection);
%shared_ptr(ifcopenshell::geom::taxonomy::loop);
%shared_ptr(ifcopenshell::geom::taxonomy::face);
%shared_ptr(ifcopenshell::geom::taxonomy::shell);
%shared_ptr(ifcopenshell::geom::taxonomy::solid);
%shared_ptr(ifcopenshell::geom::taxonomy::loft);
%shared_ptr(ifcopenshell::geom::taxonomy::surface);
%shared_ptr(ifcopenshell::geom::taxonomy::plane);
%shared_ptr(ifcopenshell::geom::taxonomy::cylinder);
%shared_ptr(ifcopenshell::geom::taxonomy::sphere);
%shared_ptr(ifcopenshell::geom::taxonomy::torus);
%shared_ptr(ifcopenshell::geom::taxonomy::bspline_surface);
%shared_ptr(ifcopenshell::geom::taxonomy::sweep);
%shared_ptr(ifcopenshell::geom::taxonomy::extrusion);
%shared_ptr(ifcopenshell::geom::taxonomy::revolve);
%shared_ptr(ifcopenshell::geom::taxonomy::sweep_along_curve);
%shared_ptr(ifcopenshell::geom::taxonomy::node);

%include "../ifcgeom/ifc_geom_api.h"
%include "../ifcgeom/conversion_result.h"

%extend ifcopenshell::geom::conversion_result {
	ifcopenshell::geom::conversion_result_shape* _shape() const {
		return $self->shape().get();
	}

	%pythoncode %{
		def shape(self):
			result = self._shape()
			result._parent = self
			return result
	%}
}
// The implementation tuple is intentionally opaque to Python. Letting SWIG
// emit a type token for all setting descriptors exceeds MSVC's token limit.
%ignore ifcopenshell::geom::settings_container;
%ignore ifcopenshell::geom::geometry_setting_types;
%ignore ifcopenshell::geom::settings::settings_tuple;
%include "../ifcgeom/conversion_settings.h"

// Keep the owning element alive while its geometry is referenced (#1124).
%define GEOMETRY_WITH_BACKREF(cls)
%feature("shadow") cls::geometry %{
	@property
	def geometry(self):
		result = $action(self)
		result._parent = self
		return result
%}
%enddef

GEOMETRY_WITH_BACKREF(ifcopenshell::geom::triangulation_element)
GEOMETRY_WITH_BACKREF(ifcopenshell::geom::serialized_element)
GEOMETRY_WITH_BACKREF(ifcopenshell::geom::native_element)

%include "../ifcgeom/element.h"
%include "../ifcgeom/representation.h"
%ignore ifcopenshell::geom::iterator::get;
%ignore ifcopenshell::geom::iterator::get_native;
%ignore ifcopenshell::geom::iterator::get_object;
%newobject ifcopenshell::geom::iterator::_get;
%newobject ifcopenshell::geom::iterator::_get_native;
%newobject ifcopenshell::geom::iterator::_get_object;
%include "../ifcgeom/iterator.h"

%extend ifcopenshell::geom::iterator {
	ifcopenshell::geom::element* _get() {
		return $self->get().release();
	}

	ifcopenshell::geom::native_element* _get_native() {
		return $self->get_native().release();
	}

	ifcopenshell::geom::element* _get_object(int id) {
		return $self->get_object(id).release();
	}

	%pythoncode %{
		def get(self):
			return self._get()

		def get_native(self):
			return self._get_native()

		def get_object(self, id):
			return self._get_object(id)
	%}
}

%include "../ifcgeom/geometry_serializer.h"
%include "../ifcgeom/taxonomy.h"
%include "../ifcgeom/function_item_evaluator.h"

%{
#include "../serializers/geometry_serializer_plugin.h"

class python_plugin_geometry_serializer : public ifcopenshell::geom::geometry_serializer {
public:
	python_plugin_geometry_serializer(
		const std::string& extension,
		const std::string& output_filename,
		const std::string& output_temp_filename,
		ifcopenshell::geom::settings& settings
	)
		: ifcopenshell::geom::geometry_serializer(settings)
	{
		ifcopenshell::serializers::geometry_serializer_context context{
			output_filename,
			output_temp_filename.empty() ? output_filename : output_temp_filename,
			settings
		};

		initialize_serializer(extension, context);
	}

	python_plugin_geometry_serializer(
		const std::string& extension,
		const stream_or_filename& output_filename,
		const stream_or_filename& output_temp_filename,
		ifcopenshell::geom::settings& settings
	)
		: ifcopenshell::geom::geometry_serializer(settings)
	{
		const auto output_filename_string = output_filename.filename().value_or("");
		const auto output_temp_filename_string = output_temp_filename.filename().value_or(output_filename_string);
		ifcopenshell::serializers::geometry_serializer_context context{
			output_filename_string,
			output_temp_filename_string,
			settings,
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
		settings_ = context.settings;
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

	void write(const ifcopenshell::geom::triangulation_element* element) override {
		serializer_->write(element);
	}

	void write(const ifcopenshell::geom::native_element* element) override {
		serializer_->write(element);
	}

	void setUnitNameAndMagnitude(const std::string& name, float magnitude) override {
		serializer_->setUnitNameAndMagnitude(name, magnitude);
	}

	ifcopenshell::geom::element* read(
		ifcopenshell::file& file,
		const std::string& guid,
		const std::string& representation_id,
		ifcopenshell::geom::geometry_serializer::read_type rt = ifcopenshell::geom::geometry_serializer::READ_BREP
	) override {
		return serializer_->read(file, guid, representation_id, rt);
	}

	std::string object_id(const ifcopenshell::geom::element* element) override {
		return serializer_->object_id(element);
	}

private:
	std::shared_ptr<ifcopenshell::geom::geometry_serializer> serializer_;
};
%}

%extend ifcopenshell::geom::geometry_serializer {
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

%extend ifcopenshell::geom::taxonomy::style {
	size_t instance_id() const {
		if (!self->instance) {
			return 0;
		}
		return self->instance.id();
	}
}


%define assign_component_acccess(item_name)

%extend ifcopenshell::geom::taxonomy::item_name {
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

%extend ifcopenshell::geom::taxonomy::item_name {
	// swig does not accept auto here as the return type
	const std::vector<ifcopenshell::geom::taxonomy::children_type::ptr>& children_() const {
		return $self->children;
	}

	const ifcopenshell::geom::taxonomy::children_type::ptr& __getitem__(int index) const {
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

%extend ifcopenshell::geom::taxonomy::item_name {
	// swig does not accept auto here as the return type
	const ifcopenshell::geom::taxonomy::matrix4::ptr& matrix_() const {
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

%extend ifcopenshell::geom::settings {
	void set_(const std::string& name, bool val) {
		return $self->set(name, val);
	}
	void set_(const std::string& name, int val) {
		return $self->set(name, val);
	}
	void set_(const std::string& name, ifcopenshell::geom::settings::IteratorOutputOptions val) {
		return $self->set(name, val);
	}
	void set_(const std::string& name, ifcopenshell::geom::settings::FunctionStepMethod val) {
		return $self->set(name, val);
	}
	void set_(const std::string& name, ifcopenshell::geom::settings::OutputDimensionalityTypes val) {
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
	ifcopenshell::geom::settings::value_variant_t get_(const std::string& name) {
		return $self->get(name);
	}
	std::vector<std::string> setting_names() {
		return $self->setting_names();
	}
	std::string get_type(const std::string& name) {
		return $self->get_type(name);
	}
}

%template(ray_intersection_results) std::vector<ifcopenshell::geom::ray_intersection_result>;

%template(clashes) std::vector<ifcopenshell::geom::clash>;

%ignore ifcopenshell::geom::tree::uint8_to_b64;

%include "../ifcgeom/tree.h"

%extend ifcopenshell::geom::tree {

	std::vector<express::base> select_box(const express::base& e, bool completely_within = false, double extend=-1.e-5) const {
		if (!e.declaration().is("IfcProduct")) {
			throw ifcopenshell::exception("Instance should be an IfcProduct");
		}
		return cast_vector<express::base>($self->select_box(e.as<express::entity>(), completely_within, extend));
	}

	std::vector<express::base> select_box(const std::vector<double>& p) const {
		if (p.size() != 3) {
			throw ifcopenshell::exception("Point should be a sequence of 3 floats");
		}
		ifcopenshell::geom::tree_point point = {{ p[0], p[1], p[2] }};
		return cast_vector<express::base>($self->select_box(point));
	}

	std::vector<express::base> select_box(const std::vector<std::vector<double>>& b, bool completely_within = false) const {
		if (b.size() != 2 || b[0].size() != 3 || b[1].size() != 3) {
			throw ifcopenshell::exception("Bounding box should be a sequence of 2 x 3 floats");
		}
		ifcopenshell::geom::tree_box box = {{
			{ b[0][0], b[0][1], b[0][2] },
			{ b[1][0], b[1][1], b[1][2] }
		}};
		return cast_vector<express::base>($self->select_box(box, completely_within));
	}

	std::vector<express::base> select(const express::base& e, bool completely_within = false, double extend = 0.0) const {
		if (!e.declaration().is("IfcProduct")) {
			throw ifcopenshell::exception("Instance should be an IfcProduct");
		}
		return cast_vector<express::base>($self->select(e.as<express::entity>(), completely_within, extend));
	}

	std::vector<express::base> select(const std::vector<double>& p, double extend=0.0) const {
		if (p.size() != 3) {
			throw ifcopenshell::exception("Point should be a sequence of 3 floats");
		}
		ifcopenshell::geom::tree_point point = {{ p[0], p[1], p[2] }};
		return cast_vector<express::base>($self->select(point, extend));
	}

	std::vector<express::base> select(const ifcopenshell::geom::element* elem, bool completely_within = false, double extend = -1.e-5) const {
		return cast_vector<express::base>($self->select(elem, completely_within, extend));
	}

	std::vector<ifcopenshell::geom::ray_intersection_result> select_ray(const std::vector<double>& p0, const std::vector<double>& d, double length = 1000.) const {
		if (p0.size() != 3 || d.size() != 3) {
			throw ifcopenshell::exception("Origin and direction should be sequences of 3 floats");
		}
		ifcopenshell::geom::tree_point origin = {{ p0[0], p0[1], p0[2] }};
		ifcopenshell::geom::tree_point direction = {{ d[0], d[1], d[2] }};
		return $self->select_ray(origin, direction, length);
	}

}

// A visitor
%{
struct shape_rtti : public boost::static_visitor<PyObject*>
{
    PyObject* operator()(ifcopenshell::geom::element* elem) const {
		ifcopenshell::geom::serialized_element* serialized_elem = dynamic_cast<ifcopenshell::geom::serialized_element*>(elem);
		ifcopenshell::geom::triangulation_element* triangulation_elem = dynamic_cast<ifcopenshell::geom::triangulation_element*>(elem);
		ifcopenshell::geom::native_element* brep_elem = dynamic_cast<ifcopenshell::geom::native_element*>(elem);
		if (triangulation_elem) {
			return SWIG_NewPointerObj(SWIG_as_voidptr(triangulation_elem), SWIGTYPE_p_ifcopenshell__geom__triangulation_element, SWIG_POINTER_OWN);
		} else if (serialized_elem) {
			return SWIG_NewPointerObj(SWIG_as_voidptr(serialized_elem), SWIGTYPE_p_ifcopenshell__geom__serialized_element, SWIG_POINTER_OWN);
		} else if (brep_elem) {
			return SWIG_NewPointerObj(SWIG_as_voidptr(brep_elem), SWIGTYPE_p_ifcopenshell__geom__native_element, SWIG_POINTER_OWN);
		} else {
			return SWIG_Py_Void();
		}
	}
    PyObject* operator()(ifcopenshell::geom::representation* representation) const {
		ifcopenshell::geom::serialization* serialized_representation = dynamic_cast<ifcopenshell::geom::serialization*>(representation);
		ifcopenshell::geom::triangulation* triangulated_representation = dynamic_cast<ifcopenshell::geom::triangulation*>(representation);
		ifcopenshell::geom::native* brep_representation = dynamic_cast<ifcopenshell::geom::native*>(representation);
		if (serialized_representation) {
			return SWIG_NewPointerObj(SWIG_as_voidptr(serialized_representation), SWIGTYPE_p_ifcopenshell__geom__serialization, SWIG_POINTER_OWN);
		} else if (triangulated_representation) {
			return SWIG_NewPointerObj(SWIG_as_voidptr(triangulated_representation), SWIGTYPE_p_ifcopenshell__geom__triangulation, SWIG_POINTER_OWN);
		} else if (brep_representation) {
			return SWIG_NewPointerObj(SWIG_as_voidptr(brep_representation), SWIGTYPE_p_ifcopenshell__geom__native, SWIG_POINTER_OWN);
		} else {
			return SWIG_Py_Void();
		}
	}
	PyObject* operator()(ifcopenshell::geom::transformation* transformation) const {
		return SWIG_NewPointerObj(SWIG_as_voidptr(transformation), SWIGTYPE_p_ifcopenshell__geom__transformation, SWIG_POINTER_OWN);
	}
};
%}

// Note that these elements ARE to be owned by SWIG/Python
%typemap(out) std::variant<ifcopenshell::geom::element*, ifcopenshell::geom::representation*, ifcopenshell::geom::transformation*> {
	// See which type is set and return appropriate
	$result = std::visit(shape_rtti(), (std::variant<ifcopenshell::geom::element*, ifcopenshell::geom::representation*, ifcopenshell::geom::transformation*>) $1);
}

%newobject construct_iterator;
%newobject construct_iterator_with_include_exclude;
%newobject construct_iterator_with_include_exclude_globalid;
%newobject construct_iterator_with_include_exclude_id;
%newobject create_geometry_serializer;

// I couldn't get the vector<string> typemap to be applied when %extending Iterator constructor.
// anyway it does not matter as SWIG generates C code without actual constructors
%inline %{
	ifcopenshell::geom::geometry_serializer* create_geometry_serializer(
		const std::string& extension,
		const std::string& output_filename,
		const std::string& output_temp_filename,
		ifcopenshell::geom::settings& settings
	) {
		return new python_plugin_geometry_serializer(
			extension,
			output_filename,
			output_temp_filename,
			settings
		);
	}

	ifcopenshell::geom::geometry_serializer* create_geometry_serializer(
		const std::string& extension,
		const stream_or_filename& output_filename,
		const stream_or_filename& output_temp_filename,
		ifcopenshell::geom::settings& settings
	) {
		return new python_plugin_geometry_serializer(
			extension,
			output_filename,
			output_temp_filename,
			settings
		);
	}

	// I couldn't get the vector<string> typemap to be applied when %extending Iterator constructor.
	// anyway it does not matter as SWIG generates C code without actual constructors
	ifcopenshell::geom::iterator* construct_iterator(const std::string& geometry_library, ifcopenshell::geom::settings settings, ifcopenshell::file* file, int num_threads, ifcopenshell::logger* logger = nullptr) {
		ifcopenshell::logger& logger_ = ifcopenshell::logger_or_root(logger);
		return new ifcopenshell::geom::iterator(ifcopenshell::geom::kernels::construct(file, geometry_library, settings, logger_), settings, file, num_threads, logger_);
	}

	ifcopenshell::geom::iterator* construct_iterator_with_include_exclude(const std::string& geometry_library, ifcopenshell::geom::settings settings, ifcopenshell::file* file, std::vector<std::string> elems, bool include, int num_threads, ifcopenshell::logger* logger = nullptr) {
		ifcopenshell::logger& logger_ = ifcopenshell::logger_or_root(logger);
		std::set<std::string> elems_set(elems.begin(), elems.end());
		ifcopenshell::geom::entity_filter ef{ include, false, elems_set };
		return new ifcopenshell::geom::iterator(ifcopenshell::geom::kernels::construct(file, geometry_library, settings, logger_), settings, file, {ef}, num_threads, logger_);
	}

	ifcopenshell::geom::iterator* construct_iterator_with_include_exclude_globalid(const std::string& geometry_library, ifcopenshell::geom::settings settings, ifcopenshell::file* file, std::vector<std::string> elems, bool include, int num_threads, ifcopenshell::logger* logger = nullptr) {
		ifcopenshell::logger& logger_ = ifcopenshell::logger_or_root(logger);
		std::set<std::string> elems_set(elems.begin(), elems.end());
		ifcopenshell::geom::attribute_filter af;
		af.attribute_name = "GlobalId";
		af.populate(elems_set);
		af.include = include;
		return new ifcopenshell::geom::iterator(ifcopenshell::geom::kernels::construct(file, geometry_library, settings, logger_), settings, file, {af}, num_threads, logger_);
	}

	ifcopenshell::geom::iterator* construct_iterator_with_include_exclude_id(const std::string& geometry_library, ifcopenshell::geom::settings settings, ifcopenshell::file* file, std::vector<int> elems, bool include, int num_threads, ifcopenshell::logger* logger = nullptr) {
		ifcopenshell::logger& logger_ = ifcopenshell::logger_or_root(logger);
		std::set<int> elems_set(elems.begin(), elems.end());
		ifcopenshell::geom::instance_id_filter af(include, false, elems_set);
		return new ifcopenshell::geom::iterator(ifcopenshell::geom::kernels::construct(file, geometry_library, settings, logger_), settings, file, {af}, num_threads, logger_);
	}
%}

%extend ifcopenshell::geom::triangulation {

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

%extend ifcopenshell::geom::representation {
	%pythoncode %{
        # Hide the getters with read-only property implementations
        id = property(id)
	%}
};

%extend ifcopenshell::geom::serialization {
	%pythoncode %{
        # Hide the getters with read-only property implementations
        brep_data = property(brep_data)
        surface_styles = property(surface_styles)
        surface_style_ids = property(surface_style_ids)
	%}
};

%extend ifcopenshell::geom::element {
    std::pair<const char*, size_t> transformation_buffer() const {
        // @todo check whether needs to be transposed
        const double* data = self->transformation().data()->ccomponents().data();
        return { reinterpret_cast<const char*>(data), 16 * sizeof(double) };
    }

    const express::base product_() const {
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

%extend ifcopenshell::geom::triangulation_element {
};

%extend ifcopenshell::geom::serialized_element {
};

%extend ifcopenshell::geom::native_element {
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
        volume = property(calc_volume_)
        surface_area = property(calc_surface_area_)
    %}
};

/*
%extend ifcopenshell::geom::Material {
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

%extend ifcopenshell::geom::transformation {
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

%{
	template <typename T>
	std::string to_locale_invariant_string(const T& t) {
		std::ostringstream oss;
		oss.imbue(std::locale::classic());
		oss << t;
		return oss.str();
	}

	static std::variant<ifcopenshell::geom::element*, ifcopenshell::geom::representation*, ifcopenshell::geom::transformation*> helper_fn_create_shape(ifcopenshell::logger& logger, const std::string& geometry_library, ifcopenshell::geom::settings& settings, const express::base& instance, const express::base& representation = express::base()) {
		ifcopenshell::file* file = instance.file();

		ifcopenshell::geom::converter kernel(ifcopenshell::geom::kernels::construct(file, geometry_library, settings, logger), file, settings, logger);
		if (instance.declaration().is("IfcProduct")) {
			if (representation && !representation.declaration().is("IfcRepresentation")) {
				throw ifcopenshell::exception("Supplied representation not of type IfcRepresentation");
			}

			auto selected_representation = representation ? representation : kernel.mapping()->representation_of(instance);
			if (!selected_representation) {
				throw ifcopenshell::exception("No suitable IfcRepresentation found");
			}

			ifcopenshell::geom::native_element* brep = kernel.create_brep_for_representation_and_product(selected_representation, instance);
			if (!brep) {
				std::ostringstream oss_repr, oss_product;
				selected_representation.to_string(oss_repr);
				instance.to_string(oss_product);
				throw ifcopenshell::exception("Failed to process shape. Product: " + oss_product.str() + ", representation: " + oss_repr.str());
			}
			if (settings.get<ifcopenshell::geom::settings::IteratorOutput>().get() == ifcopenshell::geom::settings::SERIALIZED) {
				ifcopenshell::geom::serialized_element* serialization = new ifcopenshell::geom::serialized_element(*brep);
				delete brep;
				return serialization;
			} else if (settings.get<ifcopenshell::geom::settings::IteratorOutput>().get() == ifcopenshell::geom::settings::TRIANGULATED) {
				ifcopenshell::geom::triangulation_element* triangulation = new ifcopenshell::geom::triangulation_element(*brep);
				delete brep;
				return triangulation;
			} else {
				return brep;
			}
		} else if (instance.declaration().is("IfcPlacement") || instance.declaration().is("IfcObjectPlacement")) {
			auto item = ifcopenshell::geom::taxonomy::cast<ifcopenshell::geom::taxonomy::matrix4>(kernel.mapping()->map(instance));
			if (item == nullptr) {
				throw ifcopenshell::exception("Failed to convert placement");
			}
			/*
            if (settings.get<ifcopenshell::geom::settings::ConvertBackUnits>().get()) {
                // we pass the settings to the Transformation object, but access the data just offloads to the
                // generic cartesian_base<Matrix4> so there's no time to apply the settings to the translation part.
                item = ifcopenshell::geom::taxonomy::matrix4::ptr(item->clone_());
                item->components().col(3).head<3>() /= kernel.settings().get<ifcopenshell::geom::settings::LengthUnit>().get();
			}
			*/
			return new ifcopenshell::geom::transformation(kernel.settings(), item);
		} else {
			if (!representation) {
				if (instance.declaration().is("IfcRepresentationItem") ||
					instance.declaration().is("IfcRepresentation") ||
					// https://github.com/IfcOpenShell/IfcOpenShell/issues/1649
					instance.declaration().is("IfcProfileDef")
				) {
					std::vector<ifcopenshell::geom::conversion_result> shapes;
					try {
						shapes = kernel.convert(instance);
					} catch (...) {
						std::ostringstream oss;
						instance.to_string(oss);
						throw ifcopenshell::exception("Failed to process shape. Instance: " + oss.str());
					}

					ifcopenshell::geom::native brep(kernel.settings(), instance.declaration().name(), to_locale_invariant_string(instance.id()), shapes);
					try {
						if (settings.get<ifcopenshell::geom::settings::IteratorOutput>().get() == ifcopenshell::geom::settings::SERIALIZED) {
							return new ifcopenshell::geom::serialization(brep);
						} else if (settings.get<ifcopenshell::geom::settings::IteratorOutput>().get() == ifcopenshell::geom::settings::TRIANGULATED) {
							return new ifcopenshell::geom::triangulation(brep);
						}
					} catch (...) {
						throw ifcopenshell::exception("error during shape serialization");
					}
				}
			} else {
				throw ifcopenshell::exception("Invalid additional representation specified");
			}
		}
		return std::variant<ifcopenshell::geom::element*, ifcopenshell::geom::representation*, ifcopenshell::geom::transformation*>();
	}
%}

%typemap(out) ifcopenshell::geom::taxonomy::item::ptr {
	$result = item_to_pyobject($1);
}

%{
template <typename T>
ifcopenshell::geom::taxonomy::item::ptr try_upcast(PyObject* obj0, swig_type_info* info) {
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
        return std::static_pointer_cast<ifcopenshell::geom::taxonomy::item>(*arg1);
    }
    return nullptr;
}
%}

%inline %{
	ifcopenshell::geom::taxonomy::item::ptr map_shape(ifcopenshell::geom::settings& settings, const express::base& instance) {
        std::unique_ptr<ifcopenshell::geom::abstract_mapping> mapping(ifcopenshell::geom::impl::mapping_implementations().construct(instance.file(), settings));
		return mapping->map(instance);
	}
%}

%inline %{
	static std::variant<ifcopenshell::geom::element*, ifcopenshell::geom::representation*, ifcopenshell::geom::transformation*> create_shape(ifcopenshell::geom::settings& settings, const express::base& instance, const express::base& representation, const char* const geometry_library="opencascade", ifcopenshell::logger* logger = nullptr) {
		return helper_fn_create_shape(ifcopenshell::logger_or_root(logger), geometry_library, settings, instance, representation);
	}

	// Manual definition of overload without representation argument
	static std::variant<ifcopenshell::geom::element*, ifcopenshell::geom::representation*, ifcopenshell::geom::transformation*> create_shape(ifcopenshell::geom::settings& settings, const express::base& instance, const char* const geometry_library="opencascade", ifcopenshell::logger* logger = nullptr) {
		return create_shape(settings, instance, express::base(), geometry_library, logger);
	}
%}

// @todo bring back serialization OCCT -> IFC by means of opencascade_geometry_ifc_writer_registry

%template(OpaqueCoordinate_3) ifcopenshell::geom::opaque_coordinate<3>;
%template(OpaqueCoordinate_4) ifcopenshell::geom::opaque_coordinate<4>;

%newobject create_epeck;

%inline %{
	ifcopenshell::geom::opaque_number* create_epeck(int i) {
		return new ifcopenshell::geom::opaque_number(i);
	}
	ifcopenshell::geom::opaque_number* create_epeck(double d) {
		return new ifcopenshell::geom::opaque_number(d);
	}
	ifcopenshell::geom::opaque_number* create_epeck(const std::string& s) {
		return new ifcopenshell::geom::opaque_number(std::stod(s));
	}
%}

%inline %{
	ifcopenshell::geom::conversion_result_shape* nary_union(PyObject* sequence) {
		ifcopenshell::geom::conversion_result_shape* result = nullptr;
		std::string backend_id;
		auto identity = ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::matrix4>();
		for(Py_ssize_t i = 0; i < PySequence_Size(sequence); ++i) {
			PyObject* element = PySequence_GetItem(sequence, i);
			void* argp1 = nullptr;
			auto res1 = SWIG_ConvertPtr(element, &argp1, SWIGTYPE_p_ifcopenshell__geom__conversion_result_shape, 0);
			if (SWIG_IsOK(res1)) {
				auto arg1 = reinterpret_cast<ifcopenshell::geom::conversion_result_shape*>(argp1);
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

%extend ifcopenshell::geom::conversion_result_shape {
	std::string serialize_obj() {
		ifcopenshell::geom::settings settings;
		std::unique_ptr<ifcopenshell::geom::triangulation> triangulation($self->triangulate(settings));
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
		ifcopenshell::geom::taxonomy::matrix4 iden;
		$self->serialize(iden, result);
		return result;
	}

	conversion_result_shape* solid_mt() {
		ifcopenshell::geom::conversion_result_shape* r;
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

%extend ifcopenshell::geom::opaque_coordinate {
	%pythoncode %{
		__len__ = size
		def __iter__(self):
			yield from (self.get(i) for i in range(len(self)))
	%}
}

%extend ifcopenshell::geom::opaque_number {
	%pythoncode %{
		__abs__ = abs
	%}
}

%template(OpaqueCoordinate_3) ifcopenshell::geom::opaque_coordinate<3>;
%template(OpaqueCoordinate_4) ifcopenshell::geom::opaque_coordinate<4>;

#if 0
%inline %{
	ifcopenshell::geom::opaque_number create_epeck(int i) {
		return ifcopenshell::geom::number_epeck(i);
	}
	ifcopenshell::geom::opaque_number create_epeck(double d) {
		return ifcopenshell::geom::number_epeck(d);
	}
	ifcopenshell::geom::opaque_number create_epeck(const std::string& s) {
		return ifcopenshell::geom::number_epeck(typename CGAL::Epeck::FT::ET(s));
	}
%}

%inline %{
	ifcopenshell::geom::conversion_result_shape* nary_union(PyObject* sequence) {
		std::vector<const CGAL::Nef_polyhedron_3<CGAL::Epeck>*> nefs;
		for(Py_ssize_t i = 0; i < PySequence_Size(sequence); ++i) {
			PyObject* element = PySequence_GetItem(sequence, i);
			void* argp1 = nullptr;
			auto res1 = SWIG_ConvertPtr(element, &argp1, SWIGTYPE_p_ifcopenshell__geom__conversion_result_shape, 0);
			if (SWIG_IsOK(res1)) {
				auto arg1 = reinterpret_cast<ifcopenshell::geom::conversion_result_shape*>(argp1);
				auto cgs = dynamic_cast<ifcopenshell::geom::cgal_shape*>(arg1);
				if (cgs) {
					nefs.push_back(&cgs->nef());
				}
			}
		}
		ifcopenshell::geom::cgal_shape* shp;
		Py_BEGIN_ALLOW_THREADS;
		CGAL::Nef_nary_union_3< CGAL::Nef_polyhedron_3<CGAL::Epeck> > accum;
		for (auto& n : nefs) {
			accum.add_polyhedron(*n);
		}
		shp = new ifcopenshell::geom::cgal_shape(accum.get_union());
		Py_END_ALLOW_THREADS;
		return shp;
	}
%}
#endif

%extend ifcopenshell::geom::conversion_result_shape {
	std::string serialize_obj() {
		std::ostringstream result;
		auto cgs = dynamic_cast<ifcopenshell::geom::cgal_shape*>($self);
		if (cgs) {
			write_to_obj(cgs->nef(), result, std::numeric_limits<size_t>::max());
		}
		return result.str();
	}

	void convex_tag(bool b) {
		auto cgs = dynamic_cast<ifcopenshell::geom::cgal_shape*>($self);
		if (cgs) {
			cgs->convex_tag() = b;
		}
	}

	std::string serialize() {
		std::string result;
		ifcopenshell::geom::taxonomy::matrix4 iden;
		$self->serialize(iden, result);
		return result;
	}

	conversion_result_shape* solid_mt() {
		ifcopenshell::geom::conversion_result_shape* r;
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

	std::vector<svgfill::polygon_2> arrange_polygons(svgfill::arrange_polygon_settings settings, const std::vector<svgfill::polygon_2>& polygons, ifcopenshell::logger* logger = nullptr) {
		std::vector<svgfill::polygon_2> r;
		if (svgfill::arrange_polygons(settings, polygons, r, ifcopenshell::logger_or_root(logger))) {
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

assign_repr(ifcopenshell::geom::taxonomy::boolean_result)
assign_repr(ifcopenshell::geom::taxonomy::bspline_curve)
assign_repr(ifcopenshell::geom::taxonomy::bspline_surface)
assign_repr(ifcopenshell::geom::taxonomy::circle)
assign_repr(ifcopenshell::geom::taxonomy::collection)
assign_repr(ifcopenshell::geom::taxonomy::colour)
assign_repr(ifcopenshell::geom::taxonomy::cylinder)
assign_repr(ifcopenshell::geom::taxonomy::direction3)
assign_repr(ifcopenshell::geom::taxonomy::edge)
assign_repr(ifcopenshell::geom::taxonomy::ellipse)
assign_repr(ifcopenshell::geom::taxonomy::extrusion)
assign_repr(ifcopenshell::geom::taxonomy::face)
assign_repr(ifcopenshell::geom::taxonomy::line)
assign_repr(ifcopenshell::geom::taxonomy::loft)
assign_repr(ifcopenshell::geom::taxonomy::loop)
assign_repr(ifcopenshell::geom::taxonomy::matrix4)
assign_repr(ifcopenshell::geom::taxonomy::node)
assign_repr(ifcopenshell::geom::taxonomy::offset_curve)
assign_repr(ifcopenshell::geom::taxonomy::function_item)
assign_repr(ifcopenshell::geom::taxonomy::functor_item)
assign_repr(ifcopenshell::geom::taxonomy::piecewise_function)
assign_repr(ifcopenshell::geom::taxonomy::gradient_function)
assign_repr(ifcopenshell::geom::taxonomy::cant_function)
assign_repr(ifcopenshell::geom::taxonomy::offset_function)
assign_repr(ifcopenshell::geom::taxonomy::plane)
assign_repr(ifcopenshell::geom::taxonomy::point3)
assign_repr(ifcopenshell::geom::taxonomy::revolve)
assign_repr(ifcopenshell::geom::taxonomy::shell)
assign_repr(ifcopenshell::geom::taxonomy::solid)
assign_repr(ifcopenshell::geom::taxonomy::sphere)
assign_repr(ifcopenshell::geom::taxonomy::torus)
assign_repr(ifcopenshell::geom::taxonomy::style)
assign_repr(ifcopenshell::geom::taxonomy::sweep_along_curve)


#endif
