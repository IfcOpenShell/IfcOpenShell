#include "IteratorImplementation.h"

#include <boost/algorithm/string/case_conv.hpp>

template <typename P>
IteratorFactoryImplementation<P>& iterator_implementations() {
	static IteratorFactoryImplementation<P> impl;
	return impl;
}

template IteratorFactoryImplementation<float>& iterator_implementations<float>();
template IteratorFactoryImplementation<double>& iterator_implementations<double>();

template <typename P>
extern void init_IteratorImplementation_Ifc2x3(IteratorFactoryImplementation<P>*);

template <typename P>
extern void init_IteratorImplementation_Ifc4(IteratorFactoryImplementation<P>*);

template <typename P>
IteratorFactoryImplementation<P>::IteratorFactoryImplementation() {
	init_IteratorImplementation_Ifc2x3(this);
	init_IteratorImplementation_Ifc4(this);
}

template <class P>
void IteratorFactoryImplementation<P>::bind(const std::string& schema_name, typename get_factory_type<P>::type fn) {
	const std::string schema_name_lower = boost::to_lower_copy(schema_name);
	this->insert(std::make_pair(schema_name_lower, fn));
}

template <class P>
IfcGeom::IteratorImplementation<P>* IteratorFactoryImplementation<P>::construct(const std::string& schema_name, const IfcGeom::IteratorSettings& settings, IfcParse::IfcFile* file) {
	const std::string schema_name_lower = boost::to_lower_copy(schema_name);
	std::map<std::string, typename get_factory_type<P>::type>::const_iterator it;
	it = this->find(schema_name_lower);
	if (it == end()) {
		throw IfcParse::IfcException("No geometry iterator registered for " + schema_name);
	}
	return it->second(settings, file);
}


template IteratorFactoryImplementation<float>;
template IteratorFactoryImplementation<double>;
