#include "OpenCascadeKernel.h"

#include <Geom_BSplineSurface.hxx>

using namespace ifcopenshell::geometry;
using namespace ifcopenshell::geometry::kernels;
using namespace IfcGeom;

bool OpenCascadeKernel::convert(const taxonomy::bspline_surface::ptr bs, Handle(Geom_Surface) surf) {
	const bool is_rational = !!bs->weights;

	TColgp_Array2OfPnt Poles(0, (int)bs->control_points.size() - 1, 0, (int)(*bs->control_points.begin()).size() - 1);
	TColStd_Array2OfReal Weights(0, (int)bs->control_points.size() - 1, 0, (int)(*bs->control_points.begin()).size() - 1);
	TColStd_Array1OfReal UKnots(0, (int)bs->knots[0].size() - 1);
	TColStd_Array1OfReal VKnots(0, (int)bs->knots[1].size() - 1);
	TColStd_Array1OfInteger UMults(0, (int)bs->multiplicities[0].size() - 1);
	TColStd_Array1OfInteger VMults(0, (int)bs->multiplicities[1].size() - 1);
	Standard_Integer UDegree = bs->degree[0];
	Standard_Integer VDegree = bs->degree[1];

	int i = 0, j;
	for (auto it = bs->control_points.begin(); it != bs->control_points.end(); ++it, ++i) {
		j = 0;
		for (auto jt = (*it).begin(); jt != (*it).end(); ++jt, ++j) {
			Poles(i, j) = convert_xyz<gp_Pnt>(**jt);
		}
	}

	i = 0;
	for (std::vector<double>::const_iterator it = bs->knots[0].begin(); it != bs->knots[0].end(); ++it, ++i) {
		UKnots(i) = *it;
	}
	i = 0;
	for (std::vector<double>::const_iterator it = bs->knots[1].begin(); it != bs->knots[1].end(); ++it, ++i) {
		VKnots(i) = *it;
	}
	i = 0;
	for (std::vector<int>::const_iterator it = bs->multiplicities[0].begin(); it != bs->multiplicities[0].end(); ++it, ++i) {
		UMults(i) = *it;
	}
	i = 0;
	for (std::vector<int>::const_iterator it = bs->multiplicities[1].begin(); it != bs->multiplicities[1].end(); ++it, ++i) {
		VMults(i) = *it;
	}

	if (is_rational) {
		for (auto it = bs->weights->begin(); it != bs->weights->end(); ++it, ++i) {
			j = 0;
			for (auto jt = (*it).begin(); jt != (*it).end(); ++jt, ++j) {
				Weights(i, j) = *jt;
			}
		}
		surf = new Geom_BSplineSurface(Poles, Weights, UKnots, VKnots, UMults, VMults, UDegree, VDegree);
	} else {
		surf = new Geom_BSplineSurface(Poles, UKnots, VKnots, UMults, VMults, UDegree, VDegree);
	}

	return true;
}
