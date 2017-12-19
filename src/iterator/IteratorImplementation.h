#ifndef ITERATOR_IMPLEMENTATION_H
#define ITERATOR_IMPLEMENTATION_H

#include "../ifcparse/IfcFile.h"
#include "../ifcgeom/IfcGeomIteratorSettings.h"

#include <boost/function.hpp>

#include <map>
#include <string>

template <typename P>
class IteratorImplementation;

typedef boost::function2<IteratorImplementation<float>*, const IfcGeom::IteratorSettings&, IfcParse::IfcFile*> iterator_float_fn;
typedef boost::function2<IteratorImplementation<double>*, const IfcGeom::IteratorSettings&, IfcParse::IfcFile*> iterator_double_fn;

template <typename P>
struct get_factory_type {};

template <>
struct get_factory_type<float> {
	typedef iterator_float_fn type;
};

template <>
struct get_factory_type<double> {
	typedef iterator_double_fn type;
};

template <typename P>
class IteratorFactoryImplementation : public std::map<std::string, typename get_factory_type<P>::type> {
public:
	IteratorFactoryImplementation();
	void bind(const std::string& schema_name, typename get_factory_type<P>::type fn);
};

template <typename P>
IteratorFactoryImplementation<P>& iterator_implementations();

template <class T>
class Registrar {
public:
	Registrar(const std::string& schema_name, const typename get_factory_type<typename T::Precision>::type& fn) {
		iterator_implementations<typename T::Precision>().bind(schema_name, fn);
	}
};

template <typename T>
class IteratorImplementation {

};

#endif