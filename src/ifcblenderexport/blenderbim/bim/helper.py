import math
import bpy

# TODO: Deprecate this in favour of ifcopenshell.util.unit

class SIUnitHelper:
    prefixes = {"EXA": 1e18, "PETA": 1e15, "TERA": 1e12, "GIGA": 1e9, "MEGA":
        1e6, "KILO": 1e3, "HECTO": 1e2, "DECA": 1e1, "DECI": 1e-1, "CENTI":
        1e-2, "MILLI": 1e-3, "MICRO": 1e-6, "NANO": 1e-9, "PICO": 1e-12,
        "FEMTO": 1e-15, "ATTO": 1e-18}
    unit_names = ["AMPERE", "BECQUEREL", "CANDELA", "COULOMB",
        "CUBIC_METRE", "DEGREE CELSIUS", "FARAD", "GRAM", "GRAY", "HENRY",
        "HERTZ", "JOULE", "KELVIN", "LUMEN", "LUX", "MOLE", "NEWTON", "OHM",
        "PASCAL", "RADIAN", "SECOND", "SIEMENS", "SIEVERT", "SQUARE METRE",
        "METRE", "STERADIAN", "TESLA", "VOLT", "WATT", "WEBER"]
    si_conversions = {
        'inch': 0.0254,
        'foot': 0.3048,
        'yard': 0.914,
        'mile': 1609,
        'square inch': 0.0006452,
        'square foot': 0.09290304,
        'square yard': 0.83612736,
        'acre': 4046.86,
        'square mile': 2588881,
        'cubic inch': 0.00001639,
        'cubic foot': 0.02831684671168849,
        'cubic yard': 0.7636,
        'litre': 0.001,
        'fluid ounce UK': 0.0000284130625,
        'fluid ounce US': 0.00002957353,
        'pint UK': 0.000568,
        'pint US': 0.000473,
        'gallon UK': 0.004546,
        'gallon US': 0.003785,
        'degree': math.pi/180,
        'ounce': 0.02835,
        'pound': 0.454,
        'ton UK': 1016.0469088,
        'ton US': 907.18474,
        'lbf': 4.4482216153,
        'kip': 4448.2216153,
        'psi': 6894.7572932,
        'ksi': 6894757.2932,
        'minute': 60,
        'hour': 3600,
        'day': 86400,
        'btu': 1055.056}

    @staticmethod
    def get_prefix(text):
        for prefix in SIUnitHelper.prefixes.keys():
            if prefix in text.upper():
                return prefix

    @staticmethod
    def get_prefix_multiplier(text):
        if not text:
            return 1
        prefix = SIUnitHelper.get_prefix(text)
        if prefix:
            return SIUnitHelper.prefixes[prefix]
        return 1

    @staticmethod
    def get_unit_name(text):
        for name in SIUnitHelper.unit_names:
            if name in text.upper().replace('METER', 'METRE'):
                return name

    @staticmethod
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
        if from_unit in SIUnitHelper.si_conversions:
            value *= SIUnitHelper.si_conversions[from_unit]
        elif from_prefix:
            value *= SIUnitHelper.get_prefix_multiplier(from_prefix)
            if 'SQUARE' in from_unit:
                value *= SIUnitHelper.get_prefix_multiplier(from_prefix)
            elif 'CUBIC' in from_unit:
                value *= SIUnitHelper.get_prefix_multiplier(from_prefix)
                value *= SIUnitHelper.get_prefix_multiplier(from_prefix)
        if to_unit in SIUnitHelper.si_conversions:
            return value * (1 / SIUnitHelper.si_conversions[to_unit])
        elif to_prefix:
            value *= (1 / SIUnitHelper.get_prefix_multiplier(to_prefix))
            if 'SQUARE' in from_unit:
                value *= (1 / SIUnitHelper.get_prefix_multiplier(to_prefix))
            elif 'CUBIC' in from_unit:
                value *= (1 / SIUnitHelper.get_prefix_multiplier(to_prefix))
                value *= (1 / SIUnitHelper.get_prefix_multiplier(to_prefix))
        return value


# This function stolen from https://github.com/kevancress/MeasureIt_ARCH/blob/dcf607ce0896aa2284463c6b4ae9cd023fc54cbe/measureit_arch_baseclass.py
# MeasureIt-ARCH is GPL-v3
# In the future I will need to rewrite this to allow the user to have custom
# settings for each annotation object, not read from Blender.
def format_distance(value, isArea=False, hide_units=True):
    s_code = "\u00b2"  # Superscript two THIS IS LEGACY (but being kept for when Area Measurements are re-implimented)

    # Get Scene Unit Settings
    scaleFactor = bpy.context.scene.unit_settings.scale_length
    unit_system = bpy.context.scene.unit_settings.system
    unit_length = bpy.context.scene.unit_settings.length_unit
    imperial_precision = 32
    # (('1', "1\"", "1 Inch"),
    # ('2', "1/2\"", "1/2 Inch"),
    # ('4', "1/4\"", "1/4 Inch"),
    # ('8', "1/8\"", "1/8th Inch"),
    # ('16', "1/16\"", "1/16th Inch"),
    # ('32', "1/32\"", "1/32th Inch"),
    # ('64', "1/64\"", "1/64th Inch")),

    toInches = 39.3700787401574887
    inPerFoot = 11.999

    if isArea:
        toInches = 1550
        inPerFoot = 143.999

    value *= scaleFactor

    # Imperial Formating
    if unit_system == "IMPERIAL":
        base = int(imperial_precision)
        decInches = value * toInches

        # Seperate ft and inches
        # Unless Inches are the specified Length Unit
        if unit_length != 'INCHES':
            feet = math.floor(decInches/inPerFoot)
            decInches -= feet*inPerFoot
        else:
            feet = 0


        #Seperate Fractional Inches
        inches = math.floor(decInches)
        if inches != 0:
            frac = round(base*(decInches-inches))
        else:
            frac = round(base*(decInches))

        #Set proper numerator and denominator
        if frac != base:
            numcycles = int(math.log2(base))
            for i in range(numcycles):
                if frac%2 == 0:
                    frac = int(frac/2)
                    base = int(base/2)
                else:
                    break
        else:
            frac = 0
            inches += 1

        # Check values and compose string
        if inches == 12:
            feet += 1
            inches = 0

        if inches !=0:
            inchesString = str(inches)
            if frac != 0: inchesString += "-"
            else: inchesString += "\""
        else: inchesString = ""

        if feet != 0:
            feetString = str(feet) + "' "
        else: feetString = ""

        if frac != 0:
            fracString = str(frac) + "/" + str(base) +"\""
        else: fracString = ""

        if not isArea:
            tx_dist = feetString + inchesString + fracString
        else:
            tx_dist = str('%1.3f' % (value*toInches/inPerFoot)) + " sq. ft."


    # METRIC FORMATING
    elif unit_system == "METRIC":

        # Meters
        if unit_length == 'METERS':
            fmt = '%1.3f'
            if hide_units is False:
                fmt += " m"
            tx_dist = fmt % value
        # Centimeters
        elif unit_length == 'CENTIMETERS':
            fmt = '%1.1f'
            if hide_units is False:
                fmt += " cm"
            d_cm = value * (100)
            tx_dist = fmt % d_cm
        #Millimeters
        elif unit_length == 'MILLIMETERS':
            fmt = '%1.0f'
            if hide_units is False:
                fmt += " mm"
            d_mm = value * (1000)
            tx_dist = fmt % d_mm

        # Otherwise Use Adaptive Units
        else:
            if round(value, 2) >= 1.0:
                fmt = '%1.3f'
                if hide_units is False:
                    fmt += " m"
                tx_dist = fmt % value
            else:
                if round(value, 2) >= 0.01:
                    fmt = '%1.1f'
                    if hide_units is False:
                        fmt += " cm"
                    d_cm = value * (100)
                    tx_dist = fmt % d_cm
                else:
                    fmt = '%1.0f'
                    if hide_units is False:
                        fmt += " mm"
                    d_mm = value * (1000)
                    tx_dist = fmt % d_mm
        if isArea:
            tx_dist += s_code
    else:
        tx_dist = fmt % value


    return tx_dist
