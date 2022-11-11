#include "OpenCascadeKernel.h"

using namespace ifcopenshell::geometry;
using namespace ifcopenshell::geometry::kernels;

bool OpenCascadeKernel::convert_impl(const taxonomy::shell *shell, ifcopenshell::geometry::ConversionResults& results) {
	TopoDS_Shape shape;
	if (!convert(shell, shape)) {
		return false;
	}
	results.emplace_back(ConversionResult(
		shell->instance->data().id(),
		shell->matrix,
		new OpenCascadeShape(shape),
		shell->surface_style
	));
	return true;
}
