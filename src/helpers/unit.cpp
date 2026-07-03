/********************************************************************************
 *                                                                              *
 * This file is part of IfcOpenShell.                                           *
 *                                                                              *
 * IfcOpenShell is free software: you can redistribute it and/or modify         *
 * it under the terms of the Lesser GNU General Public License as published by  *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * IfcOpenShell is distributed in the hope that it will be useful,              *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * Lesser GNU General Public License for more details.                          *
 *                                                                              *
 * You should have received a copy of the Lesser GNU General Public License     *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

#include "Unit.h"

#include "../ifcparse/file.h"
#include "../ifcparse/instance_data.h"
#include "../ifcparse/schema.h"

#include <algorithm>
#include <cctype>

const std::unordered_map<std::string, double> kSiPrefixes = {
    { "EXA",   1e18  },
    { "PETA",  1e15  },
    { "TERA",  1e12  },
    { "GIGA",  1e9   },
    { "MEGA",  1e6   },
    { "KILO",  1e3   },
    { "HECTO", 1e2   },
    { "DECA",  1e1   },
    { "DECI",  1e-1  },
    { "CENTI", 1e-2  },
    { "MILLI", 1e-3  },
    { "MICRO", 1e-6  },
    { "NANO",  1e-9  },
    { "PICO",  1e-12 },
    { "FEMTO", 1e-15 },
    { "ATTO",  1e-18 },
};

const std::unordered_map<std::string, std::string> kSiPrefixSymbols = {
    { "EXA",   "E"  },
    { "PETA",  "P"  },
    { "TERA",  "T"  },
    { "GIGA",  "G"  },
    { "MEGA",  "M"  },
    { "KILO",  "k"  },
    { "HECTO", "h"  },
    { "DECA",  "da" },
    { "DECI",  "d"  },
    { "CENTI", "c"  },
    { "MILLI", "m"  },
    { "MICRO", "\xCE\xBC" }, // μ (UTF-8)
    { "NANO",  "n"  },
    { "PICO",  "p"  },
    { "FEMTO", "f"  },
    { "ATTO",  "a"  },
};

const std::unordered_map<std::string, double> kSiConversions = {
    { "thou",            0.0000254     },
    { "inch",            0.0254        },
    { "foot",            0.3048        },
    { "yard",            0.914         },
    { "mile",            1609.0        },
    { "square thou",     6.4516e-10    },
    { "square inch",     0.0006452     },
    { "square foot",     0.09290304    },
    { "square yard",     0.83612736    },
    { "acre",            4046.86       },
    { "square mile",     2588881.0     },
    { "cubic thou",      1.6387064e-14 },
    { "cubic inch",      0.00001639    },
    { "cubic foot",      0.02831684671168849 },
    { "cubic yard",      0.7636        },
    { "cubic mile",      4165509529.0  },
    { "litre",           0.001         },
    { "fluid ounce uk",  0.0000284130625 },
    { "fluid ounce us",  0.00002957353 },
    { "pint uk",         0.000568      },
    { "pint us",         0.000473      },
    { "gallon uk",       0.004546      },
    { "gallon us",       0.003785      },
    { "degree",          0.0174532925199433 }, // pi / 180
    { "ounce",           0.02835       },
    { "pound",           0.454         },
    { "ton uk",          1016.0469088  },
    { "ton us",          907.18474     },
    { "tonne",           1000.0        },
    { "lbf",             4.4482216153  },
    { "kip",             4448.2216153  },
    { "psi",             6894.7572932  },
    { "ksi",             6894757.2932  },
    { "minute",          60.0          },
    { "hour",            3600.0        },
    { "day",             86400.0       },
    { "btu",             1055.056      },
    { "fahrenheit",      1.8           },
};

const std::unordered_map<std::string, std::string> kImperialTypes = {
    { "thou", "LENGTHUNIT" }, { "inch", "LENGTHUNIT" }, { "foot", "LENGTHUNIT" },
    { "yard", "LENGTHUNIT" }, { "mile", "LENGTHUNIT" },
    { "square thou", "AREAUNIT" }, { "square inch", "AREAUNIT" },
    { "square foot", "AREAUNIT" }, { "square yard", "AREAUNIT" },
    { "acre", "AREAUNIT" }, { "square mile", "AREAUNIT" },
    { "cubic thou", "VOLUMEUNIT" }, { "cubic inch", "VOLUMEUNIT" },
    { "cubic foot", "VOLUMEUNIT" }, { "cubic yard", "VOLUMEUNIT" },
    { "cubic mile", "VOLUMEUNIT" }, { "litre", "VOLUMEUNIT" },
    { "fluid ounce uk", "VOLUMEUNIT" }, { "fluid ounce us", "VOLUMEUNIT" },
    { "pint uk", "VOLUMEUNIT" }, { "pint us", "VOLUMEUNIT" },
    { "gallon uk", "VOLUMEUNIT" }, { "gallon us", "VOLUMEUNIT" },
    { "degree", "PLANEANGLEUNIT" },
    { "ounce", "MASSUNIT" }, { "pound", "MASSUNIT" },
    { "ton uk", "MASSUNIT" }, { "ton us", "MASSUNIT" }, { "tonne", "MASSUNIT" },
    { "lbf", "FORCEUNIT" }, { "kip", "FORCEUNIT" },
    { "psi", "PRESSUREUNIT" }, { "ksi", "PRESSUREUNIT" },
    { "minute", "TIMEUNIT" }, { "hour", "TIMEUNIT" }, { "day", "TIMEUNIT" },
    { "btu", "ENERGYUNIT" },
    { "fahrenheit", "THERMODYNAMICTEMPERATUREUNIT" },
};

const std::unordered_map<std::string, std::string> kUnitSymbols = {
    // SI base / derived
    { "CUBIC_METRE",  "m3" },
    { "GRAM",         "g"  },
    { "SECOND",       "s"  },
    { "SQUARE_METRE", "m2" },
    { "METRE",        "m"  },
    { "NEWTON",       "N"  },
    { "PASCAL",       "Pa" },
    // Conversion-based
    { "pound-force",                    "lbf" },
    { "pound-force per square inch",    "psi" },
    { "thou",         "th"  }, { "inch",  "in" }, { "foot", "ft" },
    { "yard",         "yd"  }, { "mile",  "mi" },
    { "square thou",  "th2" }, { "square inch", "in2" },
    { "square foot",  "ft2" }, { "square yard", "yd2" },
    { "acre",         "ac"  }, { "square mile", "mi2" },
    { "cubic thou",   "th3" }, { "cubic inch",  "in3" },
    { "cubic foot",   "ft3" }, { "cubic yard",  "yd3" },
    { "cubic mile",   "mi3" }, { "litre",       "L"   },
    { "fluid ounce uk", "fl oz" }, { "fluid ounce us", "fl oz" },
    { "pint uk",      "pt"  }, { "pint us", "pt" },
    { "gallon uk",    "gal" }, { "gallon us", "gal" },
    { "degree",       "\xC2\xB0" }, // °
    { "ounce",        "oz"  }, { "pound", "lb" },
    { "ton uk",       "ton" }, { "ton us", "ton" }, { "tonne", "t" },
    { "lbf",          "lbf" }, { "kip",   "kip" },
    { "psi",          "psi" }, { "ksi",   "ksi" },
    { "minute",       "min" }, { "hour",  "hr"  }, { "day", "day" },
    { "btu",          "btu" },
    { "fahrenheit",   "\xC2\xB0\x46" }, // °F
};

namespace {

std::string toLower(const std::string& s) {
    std::string r;
    r.resize(s.size());
    std::transform(s.begin(), s.end(), r.begin(),
                   [](unsigned char c) { return std::tolower(c); });
    return r;
}

// Pull an enumeration string off an attribute_value, or "" if null/invalid.
std::string enumString(const attribute_value& av) {
    if (av.isNull()) return {};
    if (av.type() != ifcopenshell::Argument_ENUMERATION) return {};
    enumeration_reference er = av;
    return std::string(er.value() ? er.value() : "");
}

}  // namespace

double getPrefixMultiplier(const std::string& prefix) {
    if (prefix.empty()) return 1.0;
    auto it = kSiPrefixes.find(prefix);
    return (it == kSiPrefixes.end()) ? 1.0 : it->second;
}

std::optional<double> siScaleFromNamedUnit(express::Base unit) {
    double scale = 1.0;
    while (unit && unit.declaration().is("IfcConversionBasedUnit")) {
        auto e = unit.as<express::Entity>();

        // Fast path: name in si_conversions table — matches python.
        std::string name;
        auto name_attr = e.get("Name");
        if (!name_attr.isNull()) name = (std::string) name_attr;
        if (auto it = kSiConversions.find(toLower(name));
            it != kSiConversions.end()) {
            return scale * it->second;
        }

        // Otherwise walk the ConversionFactor chain.
        auto cf_attr = e.get("ConversionFactor");
        if (cf_attr.isNull()) return std::nullopt;
        express::Base cf = cf_attr;
        auto cf_e = cf.as<express::Entity>();
        auto vc_attr = cf_e.get("ValueComponent");
        if (vc_attr.isNull()) return std::nullopt;
        express::Base vc = vc_attr;
        // ValueComponent is an IfcValue SELECT wrapping a measure.
        scale *= (double) vc.get_attribute_value(0);
        auto uc_attr = cf_e.get("UnitComponent");
        if (uc_attr.isNull()) return std::nullopt;
        unit = (express::Base) uc_attr;
    }

    if (unit && unit.declaration().is("IfcSIUnit")) {
        auto e = unit.as<express::Entity>();
        const std::string prefix = enumString(e.get("Prefix"));
        const std::string name   = enumString(e.get("Name"));
        double m = getPrefixMultiplier(prefix);
        // SQUARE_/CUBIC_-prefixed SI names: prefix multiplier squared/cubed.
        if (name.find("SQUARE") != std::string::npos) {
            m *= getPrefixMultiplier(prefix);
        } else if (name.find("CUBIC") != std::string::npos) {
            m *= getPrefixMultiplier(prefix);
            m *= getPrefixMultiplier(prefix);
        }
        return scale * m;
    }

    if (unit && unit.declaration().is("IfcContextDependentUnit")) {
        // No conversion to SI is possible for a context-dependent unit.
        return std::nullopt;
    }

    return scale;
}

std::optional<express::Base> getUnitAssignment(ifcopenshell::file* ifc_file) {
    auto projects = ifc_file->instances_by_type("IfcProject");
    if (projects.empty()) return std::nullopt;
    auto ua_attr = projects[0].as<express::Entity>().get("UnitsInContext");
    if (ua_attr.isNull()) return std::nullopt;
    return (express::Base) ua_attr;
}

std::optional<express::Base> getProjectUnit(ifcopenshell::file* ifc_file,
                                            const std::string& unit_type) {
    auto ua = getUnitAssignment(ifc_file);
    if (!ua) return std::nullopt;
    auto units_attr = ua->as<express::Entity>().get("Units");
    if (units_attr.isNull()) return std::nullopt;
    std::vector<express::Base> units = units_attr;
    for (const auto& unit : units) {
        // IfcMonetaryUnit has no UnitType — guard via declaration check.
        if (!unit.declaration().is("IfcNamedUnit") &&
            !unit.declaration().is("IfcDerivedUnit")) {
            continue;
        }
        auto ut = unit.as<express::Entity>().get("UnitType");
        if (enumString(ut) == unit_type) return unit;
    }
    return std::nullopt;
}

double calculateUnitScale(ifcopenshell::file* ifc_file,
                          const std::string& unit_type) {
    auto unit = getProjectUnit(ifc_file, unit_type);
    if (!unit) return 1.0;
    auto scale = siScaleFromNamedUnit(*unit);
    return scale.value_or(1.0);
}

double convert(double value,
               const std::string& from_prefix, const std::string& from_unit,
               const std::string& to_prefix,   const std::string& to_unit) {
    const std::string fl = toLower(from_unit);
    const std::string tl = toLower(to_unit);

    if (auto it = kSiConversions.find(fl); it != kSiConversions.end()) {
        value *= it->second;
    } else if (!from_prefix.empty()) {
        value *= getPrefixMultiplier(from_prefix);
        if (from_unit.find("SQUARE") != std::string::npos) {
            value *= getPrefixMultiplier(from_prefix);
        } else if (from_unit.find("CUBIC") != std::string::npos) {
            value *= getPrefixMultiplier(from_prefix);
            value *= getPrefixMultiplier(from_prefix);
        }
    }

    if (auto it = kSiConversions.find(tl); it != kSiConversions.end()) {
        return value * (1.0 / it->second);
    } else if (!to_prefix.empty()) {
        value *= 1.0 / getPrefixMultiplier(to_prefix);
        // NB: python ifcopenshell.util.unit.convert checks `from_unit` (not
        // `to_unit`) here.  Mirrored for parity — from_unit and to_unit are
        // always the same dimension in valid calls, so behaviour is the same.
        if (from_unit.find("SQUARE") != std::string::npos) {
            value *= 1.0 / getPrefixMultiplier(to_prefix);
        } else if (from_unit.find("CUBIC") != std::string::npos) {
            value *= 1.0 / getPrefixMultiplier(to_prefix);
            value *= 1.0 / getPrefixMultiplier(to_prefix);
        }
    }
    return value;
}

double convertUnit(double value, express::Base from_unit, express::Base to_unit) {
    auto pull = [](express::Base u, std::string& prefix, std::string& name) {
        auto e = u.as<express::Entity>();
        if (u.declaration().is("IfcSIUnit")) {
            prefix = enumString(e.get("Prefix"));
            name   = enumString(e.get("Name"));
        } else {
            // IfcConversionBasedUnit / IfcContextDependentUnit: no Prefix,
            // Name is a string attribute.
            prefix.clear();
            auto name_attr = e.get("Name");
            name = name_attr.isNull() ? "" : (std::string) name_attr;
        }
    };
    std::string fp, fn, tp, tn;
    pull(from_unit, fp, fn);
    pull(to_unit,   tp, tn);
    return convert(value, fp, fn, tp, tn);
}
