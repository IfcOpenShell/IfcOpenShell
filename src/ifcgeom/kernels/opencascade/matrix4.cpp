#include "OpenCascadeKernel.h"

using namespace ifcopenshell::geometry;
using namespace ifcopenshell::geometry::kernels;
using namespace IfcGeom;
using namespace IfcGeom::util;

bool OpenCascadeKernel::convert(const taxonomy::matrix4::ptr matrix, gp_GTrsf& trsf) {
	// @todo check
	const auto& m = matrix->ccomponents();
	gp_Mat mat(
		m(0, 0), m(0, 1), m(0, 2),
		m(1, 0), m(1, 1), m(1, 2),
		m(2, 0), m(2, 1), m(2, 2)
	);

	if (matrix->instance && matrix->instance->declaration().name() == "IfcCartesianTransformationOperator3DnonUniform") {
		// std::wcout << "non uniform" << std::endl;
	}

	// @nb SetVectorialPart() sets gp_GTrsf.scale to 0.0, causing an non-invertable
	// matrix later on which cannot be in TopLoc_Location.

	std::array<double, 3> ms{ {
		mat.Column(1).Modulus(),
		mat.Column(2).Modulus(),
		mat.Column(3).Modulus()
	} };
	std::sort(ms.begin(), ms.end());

	if (std::fabs(ms.front() - ms.back()) < 1.e-7) {
		gp_Trsf tr;
		tr.SetValues(
			m(0, 0), m(0, 1), m(0, 2), m(0, 3),
			m(1, 0), m(1, 1), m(1, 2), m(1, 3),
			m(2, 0), m(2, 1), m(2, 2), m(2, 3)
		);
		trsf = tr;
	} else {
		trsf.SetVectorialPart(mat);
		trsf.SetTranslationPart(gp_XYZ(m(0, 3), m(1, 3), m(2, 3)));
		trsf.SetForm();
	}

	return true;
}