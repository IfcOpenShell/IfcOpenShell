#include "ConversionSettings.h"

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

std::istream& ifcopenshell::geometry::settings::operator>>(std::istream& in, IteratorOutputOptions& ioo)
{
	std::string token;
	in >> token;
	boost::to_upper(token);
	if (token == "TRIANGULATED") {
		ioo = TRIANGULATED;
	} else if (token == "NATIVE") {
		ioo = NATIVE;
	} else if (token == "SERIALIZED") {
		ioo = SERIALIZED;
	} else {
		in.setstate(std::ios_base::failbit);
	}
	return in;
}

std::istream& ifcopenshell::geometry::settings::operator>>(std::istream& in, PiecewiseStepMethod& ioo) {
    std::string token;
    in >> token;
    boost::to_upper(token);
    if (token == "MAXSTEPSIZE") {
        ioo = MAXSTEPSIZE;
    } else if (token == "MINSTEPS") {
        ioo = MINSTEPS;
    } else {
        in.setstate(std::ios_base::failbit);
    }
    return in;
}

std::istream& ifcopenshell::geometry::settings::operator>>(std::istream& in, OutputDimensionalityTypes& v) {
	std::string token;
	in >> token;
	boost::to_upper(token);
	if (token == "CURVES") {
		v = CURVES;
	} else if (token == "SURFACES_AND_SOLIDS") {
		v = SURFACES_AND_SOLIDS;
	} else if (token == "CURVES_SURFACES_AND_SOLIDS") {
		v = CURVES_SURFACES_AND_SOLIDS;
	} else {
		in.setstate(std::ios_base::failbit);
	}
	return in;
}

std::istream& ifcopenshell::geometry::settings::operator>>(std::istream& in, TriangulationMethod& v) {
	std::string token;
	in >> token;
	boost::to_upper(token);
	if (token == "TRIANGLE_MESH") {
		v = TRIANGLE_MESH;
	} else if (token == "POLYHEDRON_WITHOUT_HOLES") {
		v = POLYHEDRON_WITHOUT_HOLES;
	} else if (token == "POLYHEDRON_WITH_HOLES") {
		v = POLYHEDRON_WITH_HOLES;
	} else {
		in.setstate(std::ios_base::failbit);
	}
	return in;
}
