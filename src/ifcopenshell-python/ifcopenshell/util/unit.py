from math import pi

prefixes = {
    "EXA": 1e18,
    "PETA": 1e15,
    "TERA": 1e12,
    "GIGA": 1e9,
    "MEGA": 1e6,
    "KILO": 1e3,
    "HECTO": 1e2,
    "DECA": 1e1,
    "DECI": 1e-1,
    "CENTI": 1e-2,
    "MILLI": 1e-3,
    "MICRO": 1e-6,
    "NANO": 1e-9,
    "PICO": 1e-12,
    "FEMTO": 1e-15,
    "ATTO": 1e-18,
}

unit_names = [
    "AMPERE",
    "BECQUEREL",
    "CANDELA",
    "COULOMB",
    "CUBIC_METRE",
    "DEGREE CELSIUS",
    "FARAD",
    "GRAM",
    "GRAY",
    "HENRY",
    "HERTZ",
    "JOULE",
    "KELVIN",
    "LUMEN",
    "LUX",
    "MOLE",
    "NEWTON",
    "OHM",
    "PASCAL",
    "RADIAN",
    "SECOND",
    "SIEMENS",
    "SIEVERT",
    "SQUARE METRE",
    "METRE",
    "STERADIAN",
    "TESLA",
    "VOLT",
    "WATT",
    "WEBER",
]

si_conversions = {
    "inch": 0.0254,
    "foot": 0.3048,
    "yard": 0.914,
    "mile": 1609,
    "square inch": 0.0006452,
    "square foot": 0.09290304,
    "square yard": 0.83612736,
    "acre": 4046.86,
    "square mile": 2588881,
    "cubic inch": 0.00001639,
    "cubic foot": 0.02831684671168849,
    "cubic yard": 0.7636,
    "litre": 0.001,
    "fluid ounce UK": 0.0000284130625,
    "fluid ounce US": 0.00002957353,
    "pint UK": 0.000568,
    "pint US": 0.000473,
    "gallon UK": 0.004546,
    "gallon US": 0.003785,
    "degree": pi / 180,
    "ounce": 0.02835,
    "pound": 0.454,
    "ton UK": 1016.0469088,
    "ton US": 907.18474,
    "lbf": 4.4482216153,
    "kip": 4448.2216153,
    "psi": 6894.7572932,
    "ksi": 6894757.2932,
    "minute": 60,
    "hour": 3600,
    "day": 86400,
    "btu": 1055.056,
}


def get_prefix(text):
    if text:
        for prefix in prefixes.keys():
            if prefix in text.upper():
                return prefix


def get_prefix_multiplier(text):
    if not text:
        return 1
    prefix = get_prefix(text)
    if prefix:
        return prefixes[prefix]
    return 1


def get_unit_name(text):
    for name in unit_names:
        if name in text.upper().replace("METER", "METRE"):
            return name


def convert(value, from_prefix, from_unit, to_prefix, to_unit):
    """Converts between length, area, and volume units

    :param value: The numeric value you want to convert
    :type value: float
    :param from_prefix: A prefix from IfcSIPrefix. Can be None.
    :type from_prefix: string
    :param from_unit: IfcSIUnitName or IfcConversionBasedUnit.Name
    :type from_unit: string
    :param to_prefix: A prefix from IfcSIPrefix. Can be None.
    :type to_prefix: string
    :param to_unit: IfcSIUnitName or IfcConversionBasedUnit.Name
    :type to_unit: string
    """
    if from_unit in si_conversions:
        value *= si_conversions[from_unit]
    elif from_prefix:
        value *= get_prefix_multiplier(from_prefix)
        if "SQUARE" in from_unit:
            value *= get_prefix_multiplier(from_prefix)
        elif "CUBIC" in from_unit:
            value *= get_prefix_multiplier(from_prefix)
            value *= get_prefix_multiplier(from_prefix)
    if to_unit in si_conversions:
        return value * (1 / si_conversions[to_unit])
    elif to_prefix:
        value *= 1 / get_prefix_multiplier(to_prefix)
        if "SQUARE" in from_unit:
            value *= 1 / get_prefix_multiplier(to_prefix)
        elif "CUBIC" in from_unit:
            value *= 1 / get_prefix_multiplier(to_prefix)
            value *= 1 / get_prefix_multiplier(to_prefix)
    return value


def calculate_unit_scale(file):
    units = file.by_type("IfcUnitAssignment")[0]
    unit_scale = 1
    for unit in units.Units:
        if not hasattr(unit, "UnitType") or unit.UnitType != "LENGTHUNIT":
            continue
        while unit.is_a("IfcConversionBasedUnit"):
            unit_scale *= unit.ConversionFactor.ValueComponent.wrappedValue
            unit = unit.ConversionFactor.UnitComponent
        if unit.is_a("IfcSIUnit"):
            unit_scale *= get_prefix_multiplier(unit.Prefix)
    return unit_scale
