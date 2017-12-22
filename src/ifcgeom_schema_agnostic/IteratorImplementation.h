#ifndef ITERATOR_IMPLEMENTATION_H
#define ITERATOR_IMPLEMENTATION_H

#include "../ifcparse/IfcFile.h"
#include "../ifcgeom/IfcGeomIteratorSettings.h"

#include <boost/function.hpp>

#include <map>
#include <string>

namespace IfcGeom {
	template <typename P>
	class IteratorImplementation;

	template <typename P>
	class Element;

	template <typename P>
	class BRepElement;
}

typedef boost::function2<IfcGeom::IteratorImplementation<float>*, const IfcGeom::IteratorSettings&, IfcParse::IfcFile*> iterator_float_fn;
typedef boost::function2<IfcGeom::IteratorImplementation<double>*, const IfcGeom::IteratorSettings&, IfcParse::IfcFile*> iterator_double_fn;

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
	IfcGeom::IteratorImplementation<P>* construct(const std::string& schema_name, const IfcGeom::IteratorSettings&, IfcParse::IfcFile*);
};

template <typename P>
IteratorFactoryImplementation<P>& iterator_implementations();

namespace IfcGeom {

	template <typename P>
	class IteratorImplementation {
	public:
		virtual bool initialize() = 0;
		virtual int progress() const = 0;
		virtual const std::string& getUnitName() const = 0;
		virtual double getUnitMagnitude() const = 0;
		virtual IfcParse::IfcFile* file() const = 0;
		virtual IfcUtil::IfcBaseClass* next() = 0;
		virtual Element<P>* get() = 0;
		virtual BRepElement<P>* get_native() = 0;
		virtual const Element<P>* get_object(int id) = 0;
		virtual IfcUtil::IfcBaseClass* create() = 0;
	};

}

#endif