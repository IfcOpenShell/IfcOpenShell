#include "IteratorImplementation.h"

template <typename P>
IteratorFactoryImplementation<P>& iterator_implementations() {
	static IteratorFactoryImplementation<P> impl;
	return impl;
}

template IteratorFactoryImplementation<float>& iterator_implementations<float>();
template IteratorFactoryImplementation<double>& iterator_implementations<double>();

#define INIT(a) extern void init_##a(); init_##a();

template <typename P>
IteratorFactoryImplementation<P>::IteratorFactoryImplementation() {
	INIT(IteratorImplementation_Ifc2x3);
	INIT(IteratorImplementation_Ifc4);
}

template <class P>
void IteratorFactoryImplementation<P>::bind(const std::string& schema_name, typename get_factory_type<P>::type fn) {
	this->insert(std::make_pair(schema_name, fn));
}

template IteratorFactoryImplementation<float>;
template IteratorFactoryImplementation<double>;
