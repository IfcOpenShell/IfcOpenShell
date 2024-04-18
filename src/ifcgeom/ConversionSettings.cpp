#include "ConversionSettings.h"

/*
void ifcopenshell::geometry::ConversionSettings::setValue(GeomValue var, double value) {
	values_[var] = value;
}

double ifcopenshell::geometry::ConversionSettings::getValue(GeomValue var) const {
	return values_[var];
}
*/

template <typename T>
void istream_helper(std::istream& in, std::set<T>& ints) {
	std::string tokens;
	in >> tokens;
	std::vector<std::string> strs;
	boost::split(strs, tokens, boost::is_any_of(","));
	for (auto& s : strs) {
		if constexpr (std::is_same_v<T, std::string>) {
			ints.insert(s);
		} else {
			ints.insert(boost::lexical_cast<T>(s));
		}
	}
}

std::istream& std::operator>>(istream& in, set<int>& ints) {
	istream_helper<int>(in, ints);
	return in;
}

std::istream& std::operator>>(istream& in, set<string>& strs) {
	istream_helper<std::string>(in, strs);
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
