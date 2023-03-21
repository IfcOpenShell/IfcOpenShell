#include "ConversionSettings.h"

void ifcopenshell::geometry::ConversionSettings::setValue(GeomValue var, double value) {
	values_[var] = value;
}

double ifcopenshell::geometry::ConversionSettings::getValue(GeomValue var) const {
	return values_[var];
}
