#include "conversion_settings.h"

template <typename T>
void istream_helper(std::istream& in, T& vs) {
	std::string tokens;
	in >> tokens;
	std::vector<std::string> strs;
	boost::split(strs, tokens, boost::is_any_of(","));
	for (auto& s : strs) {
		if constexpr (std::is_same_v<std::decay_t<T>, std::set<std::string>>) {
			vs.insert(s);
		} else if constexpr (std::is_same_v<std::decay_t<T>, std::set<int>>) {
			vs.insert(boost::lexical_cast<typename T::value_type>(s));
		} else if constexpr (std::is_same_v<std::decay_t<T>, std::vector<double>>) {
			vs.push_back(boost::lexical_cast<typename T::value_type>(s));
		}
	}
}

std::istream& std::operator>>(istream& in, set<int>& ints) {
	istream_helper<std::set<int>>(in, ints);
	return in;
}

std::istream& std::operator>>(istream& in, set<string>& strs) {
	istream_helper<std::set<std::string>>(in, strs);
	return in;
}

std::istream& std::operator>>(istream& in, vector<double>& ds) {
	istream_helper<std::vector<double>>(in, ds);
	return in;
}

namespace {
	template <typename Enum, std::size_t N>
	std::istream& read_enum(std::istream& in, Enum& value, const std::array<const char* const, N>& names) {
		std::string token;
		if (!(in >> token)) {
			return in;
		}
		boost::to_upper(token);
		for (std::size_t i = 0; i < N; ++i) {
			if (token == names[i]) {
				value = static_cast<Enum>(i);
				return in;
			}
		}
		in.setstate(std::ios_base::failbit);
		return in;
	}
}

std::istream& ifcopenshell::geom::settings_detail::operator>>(std::istream& in, IteratorOutputOptions& value) {
	return read_enum(in, value, iterator_output_names);
}

std::istream& ifcopenshell::geom::settings_detail::operator>>(std::istream& in, OutputDimensionalityTypes& value) {
	return read_enum(in, value, output_dimensionality_names);
}

std::istream& ifcopenshell::geom::settings_detail::operator>>(std::istream& in, TriangulationMethod& value) {
	return read_enum(in, value, triangulation_method_names);
}

ifcopenshell::geom::geometry_exception::~geometry_exception() = default;

ifcopenshell::geom::too_many_faces_exception::~too_many_faces_exception() = default;
