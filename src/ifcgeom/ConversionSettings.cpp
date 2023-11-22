#include "ConversionSettings.h"

/*
void ifcopenshell::geometry::ConversionSettings::setValue(GeomValue var, double value) {
	values_[var] = value;
}

double ifcopenshell::geometry::ConversionSettings::getValue(GeomValue var) const {
	return values_[var];
}
*/

std::istream& std::operator>>(istream& in, set<int>& ints) {
	string tokens;
	in >> tokens;
	vector<string> strs;
	boost::split(strs, tokens, boost::is_any_of(","));
	for (auto& s : strs) {
		ints.insert(boost::lexical_cast<int>(s));
	}
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
