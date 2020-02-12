#ifndef ITERATOR_IMPLEMENTATION_H
#define ITERATOR_IMPLEMENTATION_H

#include "../ifcgeom_schema_agnostic/IfcGeomFilter.h"
#include "../ifcparse/IfcFile.h"
#include "../ifcgeom/IfcGeomIteratorSettings.h"

#include <gp_XYZ.hxx>

#include <boost/function.hpp>

#include <map>
#include <string>

namespace IfcGeom {
	template <typename P, typename PP>
	class IteratorImplementation;

	template <typename P, typename PP>
	class Element;

	template <typename P, typename PP>
	class BRepElement;
}

typedef boost::function4<IfcGeom::IteratorImplementation<float, float>*, const IfcGeom::IteratorSettings&, IfcParse::IfcFile*, const std::vector<IfcGeom::filter_t>&, int> iterator_float_float_fn;
typedef boost::function4<IfcGeom::IteratorImplementation<float, double>*, const IfcGeom::IteratorSettings&, IfcParse::IfcFile*, const std::vector<IfcGeom::filter_t>&, int> iterator_float_double_fn;
typedef boost::function4<IfcGeom::IteratorImplementation<double, double>*, const IfcGeom::IteratorSettings&, IfcParse::IfcFile*, const std::vector<IfcGeom::filter_t>&, int> iterator_double_double_fn;

template <typename P, typename PP>
struct get_factory_type {};

template <>
struct get_factory_type<float, float> {
	typedef iterator_float_float_fn type;
};

template <>
struct get_factory_type<float, double> {
	typedef iterator_float_double_fn type;
};

template <>
struct get_factory_type<double, double> {
	typedef iterator_double_double_fn type;
};

template <typename P, typename PP>
class IteratorFactoryImplementation : public std::map<std::string, typename get_factory_type<P, PP>::type> {
public:
	IteratorFactoryImplementation();
	void bind(const std::string& schema_name, typename get_factory_type<P, PP>::type fn);
	IfcGeom::IteratorImplementation<P, PP>* construct(const std::string& schema_name, const IfcGeom::IteratorSettings&, IfcParse::IfcFile*, const std::vector<IfcGeom::filter_t>&, int);
};

template <typename P, typename PP>
IteratorFactoryImplementation<P, PP>& iterator_implementations();

namespace IfcGeom {

	template <typename P, typename PP>
	class IteratorImplementation {
	public:
		virtual bool initialize() = 0;
		virtual void compute_bounds(bool with_geometry) = 0;
		virtual const gp_XYZ& bounds_min() const = 0;
		virtual const gp_XYZ& bounds_max() const = 0;
		virtual int progress() const = 0;
		virtual const std::string& getUnitName() const = 0;
		virtual double getUnitMagnitude() const = 0;
		virtual IfcParse::IfcFile* file() const = 0;
		virtual IfcUtil::IfcBaseClass* next() = 0;
		virtual Element<P, PP>* get() = 0;
		virtual BRepElement<P, PP>* get_native() = 0;
		virtual const Element<P, PP>* get_object(int id) = 0;
		virtual IfcUtil::IfcBaseClass* create() = 0;
	};

}

#endif