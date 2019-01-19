#include "IteratorImplementation.h"

#include <boost/algorithm/string/case_conv.hpp>

template <typename P, typename PP>
IteratorFactoryImplementation<P, PP>& iterator_implementations() {
	static IteratorFactoryImplementation<P, PP> impl;
	return impl;
}

template IteratorFactoryImplementation<float, float>& iterator_implementations<float, float>();
template IteratorFactoryImplementation<float, double>& iterator_implementations<float, double>();
template IteratorFactoryImplementation<double, double>& iterator_implementations<double, double>();

template <typename P, typename PP>
extern void init_IteratorImplementation_Ifc2x3(IteratorFactoryImplementation<P, PP>*);

template <typename P, typename PP>
extern void init_IteratorImplementation_Ifc4(IteratorFactoryImplementation<P, PP>*);

template <typename P, typename PP>
IteratorFactoryImplementation<P, PP>::IteratorFactoryImplementation() {
	init_IteratorImplementation_Ifc2x3(this);
	init_IteratorImplementation_Ifc4(this);
}

template <typename P, typename PP>
void IteratorFactoryImplementation<P, PP>::bind(const std::string& schema_name, typename get_factory_type<P, PP>::type fn) {
	const std::string schema_name_lower = boost::to_lower_copy(schema_name);
	this->insert(std::make_pair(schema_name_lower, fn));
}

template <typename P, typename PP>
IfcGeom::IteratorImplementation<P, PP>* IteratorFactoryImplementation<P, PP>::construct(const std::string& schema_name, const std::string& geometry_library, const IfcGeom::IteratorSettings& settings, IfcParse::IfcFile* file, const std::vector<IfcGeom::filter_t>& filters) {
	const std::string schema_name_lower = boost::to_lower_copy(schema_name);
	typename std::map<std::string, typename get_factory_type<P, PP>::type>::const_iterator it;
	it = this->find(schema_name_lower);
	if (it == this->end()) {
		throw IfcParse::IfcException("No geometry iterator registered for " + schema_name);
	}
	return it->second(geometry_library, settings, file, filters);
}


template class IteratorFactoryImplementation<float, float>;
template class IteratorFactoryImplementation<float, double>;
template class IteratorFactoryImplementation<double, double>;
