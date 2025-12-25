import ifcopenshell

def exists(v):
    if callable(v):
        try:
            return v() is not None
        except IndexError as e:
            return False
    else:
        return v is not None

def nvl(v, default):
    return v if v is not None else default

def is_entity(inst):
    if isinstance(inst, ifcopenshell.entity_instance):
        schema_name = inst.is_a(True).split('.')[0].lower()
        decl = ifcopenshell.ifcopenshell_wrapper.schema_by_name(schema_name).declaration_by_name(inst.is_a())
        return isinstance(decl, ifcopenshell.ifcopenshell_wrapper.entity)
    return False

def express_len(v):
    if isinstance(v, ifcopenshell.entity_instance) and (not is_entity(v)):
        v = v[0]
    elif v is None or v is INDETERMINATE:
        return INDETERMINATE
    return len(v)
old_range = range

def range(*args):
    if INDETERMINATE in args:
        return
    yield from old_range(*args)
sizeof = express_len
hiindex = express_len
blength = express_len
loindex = lambda x: 1
from math import *
unknown = 'UNKNOWN'

def usedin(inst, ref_name):
    if inst is None:
        return []
    (_, __, attr) = ref_name.split('.')

    def filter():
        for (ref, attr_idx) in inst.wrapped_data.file.get_inverse(inst, allow_duplicate=True, with_attribute_indices=True):
            if ref.wrapped_data.get_attribute_names()[attr_idx].lower() == attr:
                yield ref
    return list(filter())

class express_set(set):

    def __mul__(self, other):
        return express_set(set(other) & self)
    __rmul__ = __mul__

    def __add__(self, other):

        def make_list(v):
            if isinstance(v, (list, tuple, set, express_set)):
                return list(v)
            else:
                return [v]
        return express_set(list(self) + make_list(other))
    __radd__ = __add__

    def __repr__(self):
        return repr(set(self))

    def __getitem__(self, k):
        return express_getitem(list(self), k, INDETERMINATE)

def express_getitem(aggr, idx, default):
    if aggr is None:
        return default
    if isinstance(aggr, ifcopenshell.entity_instance) and (not is_entity(aggr)):
        aggr = aggr[0]
    try:
        return aggr[idx]
    except IndexError as e:
        return None

def express_getattr(aggr, name, default):
    v = getattr(aggr, name, default)
    if v is None:
        return default
    else:
        return v
EXPRESS_ONE_BASED_INDEXING = 1

def typeof(inst):
    if not inst:
        return express_set([])
    schema_name = inst.is_a(True).split('.')[0].lower()

    def inner():
        decl = ifcopenshell.ifcopenshell_wrapper.schema_by_name(schema_name).declaration_by_name(inst.is_a())
        while decl:
            yield '.'.join((schema_name, decl.name().lower()))
            if isinstance(decl, ifcopenshell.ifcopenshell_wrapper.entity):
                decl = decl.supertype()
            else:
                decl = decl.declared_type()
                while isinstance(decl, ifcopenshell.ifcopenshell_wrapper.named_type):
                    decl = decl.declared_type()
                if not isinstance(decl, ifcopenshell.ifcopenshell_wrapper.type_declaration):
                    break
    return express_set(inner())

class indeterminate_type:

    def __bool__(self):
        return False

    def bop(self, *other):
        return self
    __lt__ = bop
    __le__ = bop
    __eq__ = bop
    __ne__ = bop
    __gt__ = bop
    __ge__ = bop
    __add__ = bop
    __radd__ = bop
    __sub__ = bop
    __rsub__ = bop
    __mul__ = bop
    __rmul__ = bop
    __truediv__ = bop
    __floordiv__ = bop
    __rtruediv__ = bop
    __rfloordiv__ = bop
    __mod__ = bop
    __rmod__ = bop
    __pow__ = bop
    __rpow__ = bop
    __neg__ = bop
    __pos__ = bop
    __getitem__ = bop
    __getattr__ = bop

    def __iter__(self):
        return iter(())
INDETERMINATE = indeterminate_type()

class enum_namespace:

    def __getattr__(self, k):
        return express_getattr(k, 'upper', INDETERMINATE)()
IfcActionRequestTypeEnum = enum_namespace()
email = express_getattr(IfcActionRequestTypeEnum, 'EMAIL', INDETERMINATE)
fax = express_getattr(IfcActionRequestTypeEnum, 'FAX', INDETERMINATE)
phone = express_getattr(IfcActionRequestTypeEnum, 'PHONE', INDETERMINATE)
post = express_getattr(IfcActionRequestTypeEnum, 'POST', INDETERMINATE)
verbal = express_getattr(IfcActionRequestTypeEnum, 'VERBAL', INDETERMINATE)
userdefined = express_getattr(IfcActionRequestTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcActionRequestTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcActionSourceTypeEnum = enum_namespace()
dead_load_g = express_getattr(IfcActionSourceTypeEnum, 'DEAD_LOAD_G', INDETERMINATE)
completion_g1 = express_getattr(IfcActionSourceTypeEnum, 'COMPLETION_G1', INDETERMINATE)
live_load_q = express_getattr(IfcActionSourceTypeEnum, 'LIVE_LOAD_Q', INDETERMINATE)
snow_s = express_getattr(IfcActionSourceTypeEnum, 'SNOW_S', INDETERMINATE)
wind_w = express_getattr(IfcActionSourceTypeEnum, 'WIND_W', INDETERMINATE)
prestressing_p = express_getattr(IfcActionSourceTypeEnum, 'PRESTRESSING_P', INDETERMINATE)
settlement_u = express_getattr(IfcActionSourceTypeEnum, 'SETTLEMENT_U', INDETERMINATE)
temperature_t = express_getattr(IfcActionSourceTypeEnum, 'TEMPERATURE_T', INDETERMINATE)
earthquake_e = express_getattr(IfcActionSourceTypeEnum, 'EARTHQUAKE_E', INDETERMINATE)
fire = express_getattr(IfcActionSourceTypeEnum, 'FIRE', INDETERMINATE)
impulse = express_getattr(IfcActionSourceTypeEnum, 'IMPULSE', INDETERMINATE)
impact = express_getattr(IfcActionSourceTypeEnum, 'IMPACT', INDETERMINATE)
transport = express_getattr(IfcActionSourceTypeEnum, 'TRANSPORT', INDETERMINATE)
erection = express_getattr(IfcActionSourceTypeEnum, 'ERECTION', INDETERMINATE)
propping = express_getattr(IfcActionSourceTypeEnum, 'PROPPING', INDETERMINATE)
system_imperfection = express_getattr(IfcActionSourceTypeEnum, 'SYSTEM_IMPERFECTION', INDETERMINATE)
shrinkage = express_getattr(IfcActionSourceTypeEnum, 'SHRINKAGE', INDETERMINATE)
creep = express_getattr(IfcActionSourceTypeEnum, 'CREEP', INDETERMINATE)
lack_of_fit = express_getattr(IfcActionSourceTypeEnum, 'LACK_OF_FIT', INDETERMINATE)
buoyancy = express_getattr(IfcActionSourceTypeEnum, 'BUOYANCY', INDETERMINATE)
ice = express_getattr(IfcActionSourceTypeEnum, 'ICE', INDETERMINATE)
current = express_getattr(IfcActionSourceTypeEnum, 'CURRENT', INDETERMINATE)
wave = express_getattr(IfcActionSourceTypeEnum, 'WAVE', INDETERMINATE)
rain = express_getattr(IfcActionSourceTypeEnum, 'RAIN', INDETERMINATE)
brakes = express_getattr(IfcActionSourceTypeEnum, 'BRAKES', INDETERMINATE)
userdefined = express_getattr(IfcActionSourceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcActionSourceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcActionTypeEnum = enum_namespace()
permanent_g = express_getattr(IfcActionTypeEnum, 'PERMANENT_G', INDETERMINATE)
variable_q = express_getattr(IfcActionTypeEnum, 'VARIABLE_Q', INDETERMINATE)
extraordinary_a = express_getattr(IfcActionTypeEnum, 'EXTRAORDINARY_A', INDETERMINATE)
userdefined = express_getattr(IfcActionTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcActionTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcActuatorTypeEnum = enum_namespace()
electricactuator = express_getattr(IfcActuatorTypeEnum, 'ELECTRICACTUATOR', INDETERMINATE)
handoperatedactuator = express_getattr(IfcActuatorTypeEnum, 'HANDOPERATEDACTUATOR', INDETERMINATE)
hydraulicactuator = express_getattr(IfcActuatorTypeEnum, 'HYDRAULICACTUATOR', INDETERMINATE)
pneumaticactuator = express_getattr(IfcActuatorTypeEnum, 'PNEUMATICACTUATOR', INDETERMINATE)
thermostaticactuator = express_getattr(IfcActuatorTypeEnum, 'THERMOSTATICACTUATOR', INDETERMINATE)
userdefined = express_getattr(IfcActuatorTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcActuatorTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcAddressTypeEnum = enum_namespace()
office = express_getattr(IfcAddressTypeEnum, 'OFFICE', INDETERMINATE)
site = express_getattr(IfcAddressTypeEnum, 'SITE', INDETERMINATE)
home = express_getattr(IfcAddressTypeEnum, 'HOME', INDETERMINATE)
distributionpoint = express_getattr(IfcAddressTypeEnum, 'DISTRIBUTIONPOINT', INDETERMINATE)
userdefined = express_getattr(IfcAddressTypeEnum, 'USERDEFINED', INDETERMINATE)
IfcAirTerminalBoxTypeEnum = enum_namespace()
constantflow = express_getattr(IfcAirTerminalBoxTypeEnum, 'CONSTANTFLOW', INDETERMINATE)
variableflowpressuredependant = express_getattr(IfcAirTerminalBoxTypeEnum, 'VARIABLEFLOWPRESSUREDEPENDANT', INDETERMINATE)
variableflowpressureindependant = express_getattr(IfcAirTerminalBoxTypeEnum, 'VARIABLEFLOWPRESSUREINDEPENDANT', INDETERMINATE)
userdefined = express_getattr(IfcAirTerminalBoxTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcAirTerminalBoxTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcAirTerminalTypeEnum = enum_namespace()
diffuser = express_getattr(IfcAirTerminalTypeEnum, 'DIFFUSER', INDETERMINATE)
grille = express_getattr(IfcAirTerminalTypeEnum, 'GRILLE', INDETERMINATE)
louvre = express_getattr(IfcAirTerminalTypeEnum, 'LOUVRE', INDETERMINATE)
register = express_getattr(IfcAirTerminalTypeEnum, 'REGISTER', INDETERMINATE)
userdefined = express_getattr(IfcAirTerminalTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcAirTerminalTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcAirToAirHeatRecoveryTypeEnum = enum_namespace()
fixedplatecounterflowexchanger = express_getattr(IfcAirToAirHeatRecoveryTypeEnum, 'FIXEDPLATECOUNTERFLOWEXCHANGER', INDETERMINATE)
fixedplatecrossflowexchanger = express_getattr(IfcAirToAirHeatRecoveryTypeEnum, 'FIXEDPLATECROSSFLOWEXCHANGER', INDETERMINATE)
fixedplateparallelflowexchanger = express_getattr(IfcAirToAirHeatRecoveryTypeEnum, 'FIXEDPLATEPARALLELFLOWEXCHANGER', INDETERMINATE)
rotarywheel = express_getattr(IfcAirToAirHeatRecoveryTypeEnum, 'ROTARYWHEEL', INDETERMINATE)
runaroundcoilloop = express_getattr(IfcAirToAirHeatRecoveryTypeEnum, 'RUNAROUNDCOILLOOP', INDETERMINATE)
heatpipe = express_getattr(IfcAirToAirHeatRecoveryTypeEnum, 'HEATPIPE', INDETERMINATE)
twintowerenthalpyrecoveryloops = express_getattr(IfcAirToAirHeatRecoveryTypeEnum, 'TWINTOWERENTHALPYRECOVERYLOOPS', INDETERMINATE)
thermosiphonsealedtubeheatexchangers = express_getattr(IfcAirToAirHeatRecoveryTypeEnum, 'THERMOSIPHONSEALEDTUBEHEATEXCHANGERS', INDETERMINATE)
thermosiphoncoiltypeheatexchangers = express_getattr(IfcAirToAirHeatRecoveryTypeEnum, 'THERMOSIPHONCOILTYPEHEATEXCHANGERS', INDETERMINATE)
userdefined = express_getattr(IfcAirToAirHeatRecoveryTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcAirToAirHeatRecoveryTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcAlarmTypeEnum = enum_namespace()
bell = express_getattr(IfcAlarmTypeEnum, 'BELL', INDETERMINATE)
breakglassbutton = express_getattr(IfcAlarmTypeEnum, 'BREAKGLASSBUTTON', INDETERMINATE)
light = express_getattr(IfcAlarmTypeEnum, 'LIGHT', INDETERMINATE)
manualpullbox = express_getattr(IfcAlarmTypeEnum, 'MANUALPULLBOX', INDETERMINATE)
siren = express_getattr(IfcAlarmTypeEnum, 'SIREN', INDETERMINATE)
whistle = express_getattr(IfcAlarmTypeEnum, 'WHISTLE', INDETERMINATE)
railwaycrocodile = express_getattr(IfcAlarmTypeEnum, 'RAILWAYCROCODILE', INDETERMINATE)
railwaydetonator = express_getattr(IfcAlarmTypeEnum, 'RAILWAYDETONATOR', INDETERMINATE)
userdefined = express_getattr(IfcAlarmTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcAlarmTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcAlignmentCantSegmentTypeEnum = enum_namespace()
blosscurve = express_getattr(IfcAlignmentCantSegmentTypeEnum, 'BLOSSCURVE', INDETERMINATE)
constantcant = express_getattr(IfcAlignmentCantSegmentTypeEnum, 'CONSTANTCANT', INDETERMINATE)
cosinecurve = express_getattr(IfcAlignmentCantSegmentTypeEnum, 'COSINECURVE', INDETERMINATE)
helmertcurve = express_getattr(IfcAlignmentCantSegmentTypeEnum, 'HELMERTCURVE', INDETERMINATE)
lineartransition = express_getattr(IfcAlignmentCantSegmentTypeEnum, 'LINEARTRANSITION', INDETERMINATE)
sinecurve = express_getattr(IfcAlignmentCantSegmentTypeEnum, 'SINECURVE', INDETERMINATE)
viennesebend = express_getattr(IfcAlignmentCantSegmentTypeEnum, 'VIENNESEBEND', INDETERMINATE)
IfcAlignmentHorizontalSegmentTypeEnum = enum_namespace()
line = express_getattr(IfcAlignmentHorizontalSegmentTypeEnum, 'LINE', INDETERMINATE)
circulararc = express_getattr(IfcAlignmentHorizontalSegmentTypeEnum, 'CIRCULARARC', INDETERMINATE)
clothoid = express_getattr(IfcAlignmentHorizontalSegmentTypeEnum, 'CLOTHOID', INDETERMINATE)
cubic = express_getattr(IfcAlignmentHorizontalSegmentTypeEnum, 'CUBIC', INDETERMINATE)
helmertcurve = express_getattr(IfcAlignmentHorizontalSegmentTypeEnum, 'HELMERTCURVE', INDETERMINATE)
blosscurve = express_getattr(IfcAlignmentHorizontalSegmentTypeEnum, 'BLOSSCURVE', INDETERMINATE)
cosinecurve = express_getattr(IfcAlignmentHorizontalSegmentTypeEnum, 'COSINECURVE', INDETERMINATE)
sinecurve = express_getattr(IfcAlignmentHorizontalSegmentTypeEnum, 'SINECURVE', INDETERMINATE)
viennesebend = express_getattr(IfcAlignmentHorizontalSegmentTypeEnum, 'VIENNESEBEND', INDETERMINATE)
IfcAlignmentTypeEnum = enum_namespace()
userdefined = express_getattr(IfcAlignmentTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcAlignmentTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcAlignmentVerticalSegmentTypeEnum = enum_namespace()
constantgradient = express_getattr(IfcAlignmentVerticalSegmentTypeEnum, 'CONSTANTGRADIENT', INDETERMINATE)
circulararc = express_getattr(IfcAlignmentVerticalSegmentTypeEnum, 'CIRCULARARC', INDETERMINATE)
parabolicarc = express_getattr(IfcAlignmentVerticalSegmentTypeEnum, 'PARABOLICARC', INDETERMINATE)
clothoid = express_getattr(IfcAlignmentVerticalSegmentTypeEnum, 'CLOTHOID', INDETERMINATE)
IfcAnalysisModelTypeEnum = enum_namespace()
in_plane_loading_2d = express_getattr(IfcAnalysisModelTypeEnum, 'IN_PLANE_LOADING_2D', INDETERMINATE)
out_plane_loading_2d = express_getattr(IfcAnalysisModelTypeEnum, 'OUT_PLANE_LOADING_2D', INDETERMINATE)
loading_3d = express_getattr(IfcAnalysisModelTypeEnum, 'LOADING_3D', INDETERMINATE)
userdefined = express_getattr(IfcAnalysisModelTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcAnalysisModelTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcAnalysisTheoryTypeEnum = enum_namespace()
first_order_theory = express_getattr(IfcAnalysisTheoryTypeEnum, 'FIRST_ORDER_THEORY', INDETERMINATE)
second_order_theory = express_getattr(IfcAnalysisTheoryTypeEnum, 'SECOND_ORDER_THEORY', INDETERMINATE)
third_order_theory = express_getattr(IfcAnalysisTheoryTypeEnum, 'THIRD_ORDER_THEORY', INDETERMINATE)
full_nonlinear_theory = express_getattr(IfcAnalysisTheoryTypeEnum, 'FULL_NONLINEAR_THEORY', INDETERMINATE)
userdefined = express_getattr(IfcAnalysisTheoryTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcAnalysisTheoryTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcAnnotationTypeEnum = enum_namespace()
assumedpoint = express_getattr(IfcAnnotationTypeEnum, 'ASSUMEDPOINT', INDETERMINATE)
asbuiltarea = express_getattr(IfcAnnotationTypeEnum, 'ASBUILTAREA', INDETERMINATE)
asbuiltline = express_getattr(IfcAnnotationTypeEnum, 'ASBUILTLINE', INDETERMINATE)
non_physical_signal = express_getattr(IfcAnnotationTypeEnum, 'NON_PHYSICAL_SIGNAL', INDETERMINATE)
assumedline = express_getattr(IfcAnnotationTypeEnum, 'ASSUMEDLINE', INDETERMINATE)
widthevent = express_getattr(IfcAnnotationTypeEnum, 'WIDTHEVENT', INDETERMINATE)
assumedarea = express_getattr(IfcAnnotationTypeEnum, 'ASSUMEDAREA', INDETERMINATE)
superelevationevent = express_getattr(IfcAnnotationTypeEnum, 'SUPERELEVATIONEVENT', INDETERMINATE)
asbuiltpoint = express_getattr(IfcAnnotationTypeEnum, 'ASBUILTPOINT', INDETERMINATE)
userdefined = express_getattr(IfcAnnotationTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcAnnotationTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcArithmeticOperatorEnum = enum_namespace()
add = express_getattr(IfcArithmeticOperatorEnum, 'ADD', INDETERMINATE)
divide = express_getattr(IfcArithmeticOperatorEnum, 'DIVIDE', INDETERMINATE)
multiply = express_getattr(IfcArithmeticOperatorEnum, 'MULTIPLY', INDETERMINATE)
subtract = express_getattr(IfcArithmeticOperatorEnum, 'SUBTRACT', INDETERMINATE)
IfcAssemblyPlaceEnum = enum_namespace()
site = express_getattr(IfcAssemblyPlaceEnum, 'SITE', INDETERMINATE)
factory = express_getattr(IfcAssemblyPlaceEnum, 'FACTORY', INDETERMINATE)
notdefined = express_getattr(IfcAssemblyPlaceEnum, 'NOTDEFINED', INDETERMINATE)
IfcAudioVisualApplianceTypeEnum = enum_namespace()
amplifier = express_getattr(IfcAudioVisualApplianceTypeEnum, 'AMPLIFIER', INDETERMINATE)
camera = express_getattr(IfcAudioVisualApplianceTypeEnum, 'CAMERA', INDETERMINATE)
display = express_getattr(IfcAudioVisualApplianceTypeEnum, 'DISPLAY', INDETERMINATE)
microphone = express_getattr(IfcAudioVisualApplianceTypeEnum, 'MICROPHONE', INDETERMINATE)
player = express_getattr(IfcAudioVisualApplianceTypeEnum, 'PLAYER', INDETERMINATE)
projector = express_getattr(IfcAudioVisualApplianceTypeEnum, 'PROJECTOR', INDETERMINATE)
receiver = express_getattr(IfcAudioVisualApplianceTypeEnum, 'RECEIVER', INDETERMINATE)
speaker = express_getattr(IfcAudioVisualApplianceTypeEnum, 'SPEAKER', INDETERMINATE)
switcher = express_getattr(IfcAudioVisualApplianceTypeEnum, 'SWITCHER', INDETERMINATE)
telephone = express_getattr(IfcAudioVisualApplianceTypeEnum, 'TELEPHONE', INDETERMINATE)
tuner = express_getattr(IfcAudioVisualApplianceTypeEnum, 'TUNER', INDETERMINATE)
communicationterminal = express_getattr(IfcAudioVisualApplianceTypeEnum, 'COMMUNICATIONTERMINAL', INDETERMINATE)
recordingequipment = express_getattr(IfcAudioVisualApplianceTypeEnum, 'RECORDINGEQUIPMENT', INDETERMINATE)
userdefined = express_getattr(IfcAudioVisualApplianceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcAudioVisualApplianceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcBSplineCurveForm = enum_namespace()
polyline_form = express_getattr(IfcBSplineCurveForm, 'POLYLINE_FORM', INDETERMINATE)
circular_arc = express_getattr(IfcBSplineCurveForm, 'CIRCULAR_ARC', INDETERMINATE)
elliptic_arc = express_getattr(IfcBSplineCurveForm, 'ELLIPTIC_ARC', INDETERMINATE)
parabolic_arc = express_getattr(IfcBSplineCurveForm, 'PARABOLIC_ARC', INDETERMINATE)
hyperbolic_arc = express_getattr(IfcBSplineCurveForm, 'HYPERBOLIC_ARC', INDETERMINATE)
unspecified = express_getattr(IfcBSplineCurveForm, 'UNSPECIFIED', INDETERMINATE)
IfcBSplineSurfaceForm = enum_namespace()
plane_surf = express_getattr(IfcBSplineSurfaceForm, 'PLANE_SURF', INDETERMINATE)
cylindrical_surf = express_getattr(IfcBSplineSurfaceForm, 'CYLINDRICAL_SURF', INDETERMINATE)
conical_surf = express_getattr(IfcBSplineSurfaceForm, 'CONICAL_SURF', INDETERMINATE)
spherical_surf = express_getattr(IfcBSplineSurfaceForm, 'SPHERICAL_SURF', INDETERMINATE)
toroidal_surf = express_getattr(IfcBSplineSurfaceForm, 'TOROIDAL_SURF', INDETERMINATE)
surf_of_revolution = express_getattr(IfcBSplineSurfaceForm, 'SURF_OF_REVOLUTION', INDETERMINATE)
ruled_surf = express_getattr(IfcBSplineSurfaceForm, 'RULED_SURF', INDETERMINATE)
generalised_cone = express_getattr(IfcBSplineSurfaceForm, 'GENERALISED_CONE', INDETERMINATE)
quadric_surf = express_getattr(IfcBSplineSurfaceForm, 'QUADRIC_SURF', INDETERMINATE)
surf_of_linear_extrusion = express_getattr(IfcBSplineSurfaceForm, 'SURF_OF_LINEAR_EXTRUSION', INDETERMINATE)
unspecified = express_getattr(IfcBSplineSurfaceForm, 'UNSPECIFIED', INDETERMINATE)
IfcBeamTypeEnum = enum_namespace()
beam = express_getattr(IfcBeamTypeEnum, 'BEAM', INDETERMINATE)
joist = express_getattr(IfcBeamTypeEnum, 'JOIST', INDETERMINATE)
hollowcore = express_getattr(IfcBeamTypeEnum, 'HOLLOWCORE', INDETERMINATE)
lintel = express_getattr(IfcBeamTypeEnum, 'LINTEL', INDETERMINATE)
spandrel = express_getattr(IfcBeamTypeEnum, 'SPANDREL', INDETERMINATE)
t_beam = express_getattr(IfcBeamTypeEnum, 'T_BEAM', INDETERMINATE)
girder_segment = express_getattr(IfcBeamTypeEnum, 'GIRDER_SEGMENT', INDETERMINATE)
diaphragm = express_getattr(IfcBeamTypeEnum, 'DIAPHRAGM', INDETERMINATE)
piercap = express_getattr(IfcBeamTypeEnum, 'PIERCAP', INDETERMINATE)
hatstone = express_getattr(IfcBeamTypeEnum, 'HATSTONE', INDETERMINATE)
cornice = express_getattr(IfcBeamTypeEnum, 'CORNICE', INDETERMINATE)
edgebeam = express_getattr(IfcBeamTypeEnum, 'EDGEBEAM', INDETERMINATE)
userdefined = express_getattr(IfcBeamTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcBeamTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcBearingTypeDisplacementEnum = enum_namespace()
fixed_movement = express_getattr(IfcBearingTypeDisplacementEnum, 'FIXED_MOVEMENT', INDETERMINATE)
guided_longitudinal = express_getattr(IfcBearingTypeDisplacementEnum, 'GUIDED_LONGITUDINAL', INDETERMINATE)
guided_transversal = express_getattr(IfcBearingTypeDisplacementEnum, 'GUIDED_TRANSVERSAL', INDETERMINATE)
free_movement = express_getattr(IfcBearingTypeDisplacementEnum, 'FREE_MOVEMENT', INDETERMINATE)
notdefined = express_getattr(IfcBearingTypeDisplacementEnum, 'NOTDEFINED', INDETERMINATE)
IfcBearingTypeEnum = enum_namespace()
cylindrical = express_getattr(IfcBearingTypeEnum, 'CYLINDRICAL', INDETERMINATE)
spherical = express_getattr(IfcBearingTypeEnum, 'SPHERICAL', INDETERMINATE)
elastomeric = express_getattr(IfcBearingTypeEnum, 'ELASTOMERIC', INDETERMINATE)
pot = express_getattr(IfcBearingTypeEnum, 'POT', INDETERMINATE)
guide = express_getattr(IfcBearingTypeEnum, 'GUIDE', INDETERMINATE)
rocker = express_getattr(IfcBearingTypeEnum, 'ROCKER', INDETERMINATE)
roller = express_getattr(IfcBearingTypeEnum, 'ROLLER', INDETERMINATE)
disk = express_getattr(IfcBearingTypeEnum, 'DISK', INDETERMINATE)
userdefined = express_getattr(IfcBearingTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcBearingTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcBenchmarkEnum = enum_namespace()
greaterthan = express_getattr(IfcBenchmarkEnum, 'GREATERTHAN', INDETERMINATE)
greaterthanorequalto = express_getattr(IfcBenchmarkEnum, 'GREATERTHANOREQUALTO', INDETERMINATE)
lessthan = express_getattr(IfcBenchmarkEnum, 'LESSTHAN', INDETERMINATE)
lessthanorequalto = express_getattr(IfcBenchmarkEnum, 'LESSTHANOREQUALTO', INDETERMINATE)
equalto = express_getattr(IfcBenchmarkEnum, 'EQUALTO', INDETERMINATE)
notequalto = express_getattr(IfcBenchmarkEnum, 'NOTEQUALTO', INDETERMINATE)
includes = express_getattr(IfcBenchmarkEnum, 'INCLUDES', INDETERMINATE)
notincludes = express_getattr(IfcBenchmarkEnum, 'NOTINCLUDES', INDETERMINATE)
includedin = express_getattr(IfcBenchmarkEnum, 'INCLUDEDIN', INDETERMINATE)
notincludedin = express_getattr(IfcBenchmarkEnum, 'NOTINCLUDEDIN', INDETERMINATE)
IfcBoilerTypeEnum = enum_namespace()
water = express_getattr(IfcBoilerTypeEnum, 'WATER', INDETERMINATE)
steam = express_getattr(IfcBoilerTypeEnum, 'STEAM', INDETERMINATE)
userdefined = express_getattr(IfcBoilerTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcBoilerTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcBooleanOperator = enum_namespace()
union = express_getattr(IfcBooleanOperator, 'UNION', INDETERMINATE)
intersection = express_getattr(IfcBooleanOperator, 'INTERSECTION', INDETERMINATE)
difference = express_getattr(IfcBooleanOperator, 'DIFFERENCE', INDETERMINATE)
IfcBridgePartTypeEnum = enum_namespace()
abutment = express_getattr(IfcBridgePartTypeEnum, 'ABUTMENT', INDETERMINATE)
deck = express_getattr(IfcBridgePartTypeEnum, 'DECK', INDETERMINATE)
deck_segment = express_getattr(IfcBridgePartTypeEnum, 'DECK_SEGMENT', INDETERMINATE)
foundation = express_getattr(IfcBridgePartTypeEnum, 'FOUNDATION', INDETERMINATE)
pier = express_getattr(IfcBridgePartTypeEnum, 'PIER', INDETERMINATE)
pier_segment = express_getattr(IfcBridgePartTypeEnum, 'PIER_SEGMENT', INDETERMINATE)
pylon = express_getattr(IfcBridgePartTypeEnum, 'PYLON', INDETERMINATE)
substructure = express_getattr(IfcBridgePartTypeEnum, 'SUBSTRUCTURE', INDETERMINATE)
superstructure = express_getattr(IfcBridgePartTypeEnum, 'SUPERSTRUCTURE', INDETERMINATE)
surfacestructure = express_getattr(IfcBridgePartTypeEnum, 'SURFACESTRUCTURE', INDETERMINATE)
userdefined = express_getattr(IfcBridgePartTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcBridgePartTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcBridgeTypeEnum = enum_namespace()
arched = express_getattr(IfcBridgeTypeEnum, 'ARCHED', INDETERMINATE)
cable_stayed = express_getattr(IfcBridgeTypeEnum, 'CABLE_STAYED', INDETERMINATE)
cantilever = express_getattr(IfcBridgeTypeEnum, 'CANTILEVER', INDETERMINATE)
culvert = express_getattr(IfcBridgeTypeEnum, 'CULVERT', INDETERMINATE)
framework = express_getattr(IfcBridgeTypeEnum, 'FRAMEWORK', INDETERMINATE)
girder = express_getattr(IfcBridgeTypeEnum, 'GIRDER', INDETERMINATE)
suspension = express_getattr(IfcBridgeTypeEnum, 'SUSPENSION', INDETERMINATE)
truss = express_getattr(IfcBridgeTypeEnum, 'TRUSS', INDETERMINATE)
userdefined = express_getattr(IfcBridgeTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcBridgeTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcBuildingElementPartTypeEnum = enum_namespace()
insulation = express_getattr(IfcBuildingElementPartTypeEnum, 'INSULATION', INDETERMINATE)
precastpanel = express_getattr(IfcBuildingElementPartTypeEnum, 'PRECASTPANEL', INDETERMINATE)
apron = express_getattr(IfcBuildingElementPartTypeEnum, 'APRON', INDETERMINATE)
armourunit = express_getattr(IfcBuildingElementPartTypeEnum, 'ARMOURUNIT', INDETERMINATE)
safetycage = express_getattr(IfcBuildingElementPartTypeEnum, 'SAFETYCAGE', INDETERMINATE)
userdefined = express_getattr(IfcBuildingElementPartTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcBuildingElementPartTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcBuildingElementProxyTypeEnum = enum_namespace()
complex = express_getattr(IfcBuildingElementProxyTypeEnum, 'COMPLEX', INDETERMINATE)
element = express_getattr(IfcBuildingElementProxyTypeEnum, 'ELEMENT', INDETERMINATE)
partial = express_getattr(IfcBuildingElementProxyTypeEnum, 'PARTIAL', INDETERMINATE)
provisionforvoid = express_getattr(IfcBuildingElementProxyTypeEnum, 'PROVISIONFORVOID', INDETERMINATE)
provisionforspace = express_getattr(IfcBuildingElementProxyTypeEnum, 'PROVISIONFORSPACE', INDETERMINATE)
userdefined = express_getattr(IfcBuildingElementProxyTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcBuildingElementProxyTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcBuildingSystemTypeEnum = enum_namespace()
fenestration = express_getattr(IfcBuildingSystemTypeEnum, 'FENESTRATION', INDETERMINATE)
foundation = express_getattr(IfcBuildingSystemTypeEnum, 'FOUNDATION', INDETERMINATE)
loadbearing = express_getattr(IfcBuildingSystemTypeEnum, 'LOADBEARING', INDETERMINATE)
outershell = express_getattr(IfcBuildingSystemTypeEnum, 'OUTERSHELL', INDETERMINATE)
shading = express_getattr(IfcBuildingSystemTypeEnum, 'SHADING', INDETERMINATE)
transport = express_getattr(IfcBuildingSystemTypeEnum, 'TRANSPORT', INDETERMINATE)
reinforcing = express_getattr(IfcBuildingSystemTypeEnum, 'REINFORCING', INDETERMINATE)
prestressing = express_getattr(IfcBuildingSystemTypeEnum, 'PRESTRESSING', INDETERMINATE)
erosionprevention = express_getattr(IfcBuildingSystemTypeEnum, 'EROSIONPREVENTION', INDETERMINATE)
userdefined = express_getattr(IfcBuildingSystemTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcBuildingSystemTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcBuiltSystemTypeEnum = enum_namespace()
reinforcing = express_getattr(IfcBuiltSystemTypeEnum, 'REINFORCING', INDETERMINATE)
mooring = express_getattr(IfcBuiltSystemTypeEnum, 'MOORING', INDETERMINATE)
outershell = express_getattr(IfcBuiltSystemTypeEnum, 'OUTERSHELL', INDETERMINATE)
trackcircuit = express_getattr(IfcBuiltSystemTypeEnum, 'TRACKCIRCUIT', INDETERMINATE)
erosionprevention = express_getattr(IfcBuiltSystemTypeEnum, 'EROSIONPREVENTION', INDETERMINATE)
foundation = express_getattr(IfcBuiltSystemTypeEnum, 'FOUNDATION', INDETERMINATE)
loadbearing = express_getattr(IfcBuiltSystemTypeEnum, 'LOADBEARING', INDETERMINATE)
shading = express_getattr(IfcBuiltSystemTypeEnum, 'SHADING', INDETERMINATE)
fenestration = express_getattr(IfcBuiltSystemTypeEnum, 'FENESTRATION', INDETERMINATE)
transport = express_getattr(IfcBuiltSystemTypeEnum, 'TRANSPORT', INDETERMINATE)
prestressing = express_getattr(IfcBuiltSystemTypeEnum, 'PRESTRESSING', INDETERMINATE)
userdefined = express_getattr(IfcBuiltSystemTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcBuiltSystemTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcBurnerTypeEnum = enum_namespace()
userdefined = express_getattr(IfcBurnerTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcBurnerTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCableCarrierFittingTypeEnum = enum_namespace()
bend = express_getattr(IfcCableCarrierFittingTypeEnum, 'BEND', INDETERMINATE)
cross = express_getattr(IfcCableCarrierFittingTypeEnum, 'CROSS', INDETERMINATE)
reducer = express_getattr(IfcCableCarrierFittingTypeEnum, 'REDUCER', INDETERMINATE)
tee = express_getattr(IfcCableCarrierFittingTypeEnum, 'TEE', INDETERMINATE)
userdefined = express_getattr(IfcCableCarrierFittingTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcCableCarrierFittingTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCableCarrierSegmentTypeEnum = enum_namespace()
cableladdersegment = express_getattr(IfcCableCarrierSegmentTypeEnum, 'CABLELADDERSEGMENT', INDETERMINATE)
cabletraysegment = express_getattr(IfcCableCarrierSegmentTypeEnum, 'CABLETRAYSEGMENT', INDETERMINATE)
cabletrunkingsegment = express_getattr(IfcCableCarrierSegmentTypeEnum, 'CABLETRUNKINGSEGMENT', INDETERMINATE)
conduitsegment = express_getattr(IfcCableCarrierSegmentTypeEnum, 'CONDUITSEGMENT', INDETERMINATE)
cablebracket = express_getattr(IfcCableCarrierSegmentTypeEnum, 'CABLEBRACKET', INDETERMINATE)
catenarywire = express_getattr(IfcCableCarrierSegmentTypeEnum, 'CATENARYWIRE', INDETERMINATE)
dropper = express_getattr(IfcCableCarrierSegmentTypeEnum, 'DROPPER', INDETERMINATE)
userdefined = express_getattr(IfcCableCarrierSegmentTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcCableCarrierSegmentTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCableFittingTypeEnum = enum_namespace()
connector = express_getattr(IfcCableFittingTypeEnum, 'CONNECTOR', INDETERMINATE)
entry = express_getattr(IfcCableFittingTypeEnum, 'ENTRY', INDETERMINATE)
exit = express_getattr(IfcCableFittingTypeEnum, 'EXIT', INDETERMINATE)
junction = express_getattr(IfcCableFittingTypeEnum, 'JUNCTION', INDETERMINATE)
transition = express_getattr(IfcCableFittingTypeEnum, 'TRANSITION', INDETERMINATE)
fanout = express_getattr(IfcCableFittingTypeEnum, 'FANOUT', INDETERMINATE)
userdefined = express_getattr(IfcCableFittingTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcCableFittingTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCableSegmentTypeEnum = enum_namespace()
busbarsegment = express_getattr(IfcCableSegmentTypeEnum, 'BUSBARSEGMENT', INDETERMINATE)
cablesegment = express_getattr(IfcCableSegmentTypeEnum, 'CABLESEGMENT', INDETERMINATE)
conductorsegment = express_getattr(IfcCableSegmentTypeEnum, 'CONDUCTORSEGMENT', INDETERMINATE)
coresegment = express_getattr(IfcCableSegmentTypeEnum, 'CORESEGMENT', INDETERMINATE)
contactwiresegment = express_getattr(IfcCableSegmentTypeEnum, 'CONTACTWIRESEGMENT', INDETERMINATE)
fibersegment = express_getattr(IfcCableSegmentTypeEnum, 'FIBERSEGMENT', INDETERMINATE)
fibertube = express_getattr(IfcCableSegmentTypeEnum, 'FIBERTUBE', INDETERMINATE)
opticalcablesegment = express_getattr(IfcCableSegmentTypeEnum, 'OPTICALCABLESEGMENT', INDETERMINATE)
stitchwire = express_getattr(IfcCableSegmentTypeEnum, 'STITCHWIRE', INDETERMINATE)
wirepairsegment = express_getattr(IfcCableSegmentTypeEnum, 'WIREPAIRSEGMENT', INDETERMINATE)
userdefined = express_getattr(IfcCableSegmentTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcCableSegmentTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCaissonFoundationTypeEnum = enum_namespace()
well = express_getattr(IfcCaissonFoundationTypeEnum, 'WELL', INDETERMINATE)
caisson = express_getattr(IfcCaissonFoundationTypeEnum, 'CAISSON', INDETERMINATE)
userdefined = express_getattr(IfcCaissonFoundationTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcCaissonFoundationTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcChangeActionEnum = enum_namespace()
nochange = express_getattr(IfcChangeActionEnum, 'NOCHANGE', INDETERMINATE)
modified = express_getattr(IfcChangeActionEnum, 'MODIFIED', INDETERMINATE)
added = express_getattr(IfcChangeActionEnum, 'ADDED', INDETERMINATE)
deleted = express_getattr(IfcChangeActionEnum, 'DELETED', INDETERMINATE)
notdefined = express_getattr(IfcChangeActionEnum, 'NOTDEFINED', INDETERMINATE)
IfcChillerTypeEnum = enum_namespace()
aircooled = express_getattr(IfcChillerTypeEnum, 'AIRCOOLED', INDETERMINATE)
watercooled = express_getattr(IfcChillerTypeEnum, 'WATERCOOLED', INDETERMINATE)
heatrecovery = express_getattr(IfcChillerTypeEnum, 'HEATRECOVERY', INDETERMINATE)
userdefined = express_getattr(IfcChillerTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcChillerTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcChimneyTypeEnum = enum_namespace()
userdefined = express_getattr(IfcChimneyTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcChimneyTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCoilTypeEnum = enum_namespace()
dxcoolingcoil = express_getattr(IfcCoilTypeEnum, 'DXCOOLINGCOIL', INDETERMINATE)
electricheatingcoil = express_getattr(IfcCoilTypeEnum, 'ELECTRICHEATINGCOIL', INDETERMINATE)
gasheatingcoil = express_getattr(IfcCoilTypeEnum, 'GASHEATINGCOIL', INDETERMINATE)
hydroniccoil = express_getattr(IfcCoilTypeEnum, 'HYDRONICCOIL', INDETERMINATE)
steamheatingcoil = express_getattr(IfcCoilTypeEnum, 'STEAMHEATINGCOIL', INDETERMINATE)
watercoolingcoil = express_getattr(IfcCoilTypeEnum, 'WATERCOOLINGCOIL', INDETERMINATE)
waterheatingcoil = express_getattr(IfcCoilTypeEnum, 'WATERHEATINGCOIL', INDETERMINATE)
userdefined = express_getattr(IfcCoilTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcCoilTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcColumnTypeEnum = enum_namespace()
column = express_getattr(IfcColumnTypeEnum, 'COLUMN', INDETERMINATE)
pilaster = express_getattr(IfcColumnTypeEnum, 'PILASTER', INDETERMINATE)
pierstem = express_getattr(IfcColumnTypeEnum, 'PIERSTEM', INDETERMINATE)
pierstem_segment = express_getattr(IfcColumnTypeEnum, 'PIERSTEM_SEGMENT', INDETERMINATE)
standcolumn = express_getattr(IfcColumnTypeEnum, 'STANDCOLUMN', INDETERMINATE)
userdefined = express_getattr(IfcColumnTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcColumnTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCommunicationsApplianceTypeEnum = enum_namespace()
antenna = express_getattr(IfcCommunicationsApplianceTypeEnum, 'ANTENNA', INDETERMINATE)
computer = express_getattr(IfcCommunicationsApplianceTypeEnum, 'COMPUTER', INDETERMINATE)
fax = express_getattr(IfcCommunicationsApplianceTypeEnum, 'FAX', INDETERMINATE)
gateway = express_getattr(IfcCommunicationsApplianceTypeEnum, 'GATEWAY', INDETERMINATE)
modem = express_getattr(IfcCommunicationsApplianceTypeEnum, 'MODEM', INDETERMINATE)
networkappliance = express_getattr(IfcCommunicationsApplianceTypeEnum, 'NETWORKAPPLIANCE', INDETERMINATE)
networkbridge = express_getattr(IfcCommunicationsApplianceTypeEnum, 'NETWORKBRIDGE', INDETERMINATE)
networkhub = express_getattr(IfcCommunicationsApplianceTypeEnum, 'NETWORKHUB', INDETERMINATE)
printer = express_getattr(IfcCommunicationsApplianceTypeEnum, 'PRINTER', INDETERMINATE)
repeater = express_getattr(IfcCommunicationsApplianceTypeEnum, 'REPEATER', INDETERMINATE)
router = express_getattr(IfcCommunicationsApplianceTypeEnum, 'ROUTER', INDETERMINATE)
scanner = express_getattr(IfcCommunicationsApplianceTypeEnum, 'SCANNER', INDETERMINATE)
automaton = express_getattr(IfcCommunicationsApplianceTypeEnum, 'AUTOMATON', INDETERMINATE)
intelligentperipheral = express_getattr(IfcCommunicationsApplianceTypeEnum, 'INTELLIGENTPERIPHERAL', INDETERMINATE)
ipnetworkequipment = express_getattr(IfcCommunicationsApplianceTypeEnum, 'IPNETWORKEQUIPMENT', INDETERMINATE)
opticalnetworkunit = express_getattr(IfcCommunicationsApplianceTypeEnum, 'OPTICALNETWORKUNIT', INDETERMINATE)
telecommand = express_getattr(IfcCommunicationsApplianceTypeEnum, 'TELECOMMAND', INDETERMINATE)
telephonyexchange = express_getattr(IfcCommunicationsApplianceTypeEnum, 'TELEPHONYEXCHANGE', INDETERMINATE)
transitioncomponent = express_getattr(IfcCommunicationsApplianceTypeEnum, 'TRANSITIONCOMPONENT', INDETERMINATE)
transponder = express_getattr(IfcCommunicationsApplianceTypeEnum, 'TRANSPONDER', INDETERMINATE)
transportequipment = express_getattr(IfcCommunicationsApplianceTypeEnum, 'TRANSPORTEQUIPMENT', INDETERMINATE)
opticallineterminal = express_getattr(IfcCommunicationsApplianceTypeEnum, 'OPTICALLINETERMINAL', INDETERMINATE)
linesideelectronicunit = express_getattr(IfcCommunicationsApplianceTypeEnum, 'LINESIDEELECTRONICUNIT', INDETERMINATE)
radioblockcenter = express_getattr(IfcCommunicationsApplianceTypeEnum, 'RADIOBLOCKCENTER', INDETERMINATE)
userdefined = express_getattr(IfcCommunicationsApplianceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcCommunicationsApplianceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcComplexPropertyTemplateTypeEnum = enum_namespace()
p_complex = express_getattr(IfcComplexPropertyTemplateTypeEnum, 'P_COMPLEX', INDETERMINATE)
q_complex = express_getattr(IfcComplexPropertyTemplateTypeEnum, 'Q_COMPLEX', INDETERMINATE)
IfcCompressorTypeEnum = enum_namespace()
dynamic = express_getattr(IfcCompressorTypeEnum, 'DYNAMIC', INDETERMINATE)
reciprocating = express_getattr(IfcCompressorTypeEnum, 'RECIPROCATING', INDETERMINATE)
rotary = express_getattr(IfcCompressorTypeEnum, 'ROTARY', INDETERMINATE)
scroll = express_getattr(IfcCompressorTypeEnum, 'SCROLL', INDETERMINATE)
trochoidal = express_getattr(IfcCompressorTypeEnum, 'TROCHOIDAL', INDETERMINATE)
singlestage = express_getattr(IfcCompressorTypeEnum, 'SINGLESTAGE', INDETERMINATE)
booster = express_getattr(IfcCompressorTypeEnum, 'BOOSTER', INDETERMINATE)
opentype = express_getattr(IfcCompressorTypeEnum, 'OPENTYPE', INDETERMINATE)
hermetic = express_getattr(IfcCompressorTypeEnum, 'HERMETIC', INDETERMINATE)
semihermetic = express_getattr(IfcCompressorTypeEnum, 'SEMIHERMETIC', INDETERMINATE)
weldedshellhermetic = express_getattr(IfcCompressorTypeEnum, 'WELDEDSHELLHERMETIC', INDETERMINATE)
rollingpiston = express_getattr(IfcCompressorTypeEnum, 'ROLLINGPISTON', INDETERMINATE)
rotaryvane = express_getattr(IfcCompressorTypeEnum, 'ROTARYVANE', INDETERMINATE)
singlescrew = express_getattr(IfcCompressorTypeEnum, 'SINGLESCREW', INDETERMINATE)
twinscrew = express_getattr(IfcCompressorTypeEnum, 'TWINSCREW', INDETERMINATE)
userdefined = express_getattr(IfcCompressorTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcCompressorTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCondenserTypeEnum = enum_namespace()
aircooled = express_getattr(IfcCondenserTypeEnum, 'AIRCOOLED', INDETERMINATE)
evaporativecooled = express_getattr(IfcCondenserTypeEnum, 'EVAPORATIVECOOLED', INDETERMINATE)
watercooled = express_getattr(IfcCondenserTypeEnum, 'WATERCOOLED', INDETERMINATE)
watercooledbrazedplate = express_getattr(IfcCondenserTypeEnum, 'WATERCOOLEDBRAZEDPLATE', INDETERMINATE)
watercooledshellcoil = express_getattr(IfcCondenserTypeEnum, 'WATERCOOLEDSHELLCOIL', INDETERMINATE)
watercooledshelltube = express_getattr(IfcCondenserTypeEnum, 'WATERCOOLEDSHELLTUBE', INDETERMINATE)
watercooledtubeintube = express_getattr(IfcCondenserTypeEnum, 'WATERCOOLEDTUBEINTUBE', INDETERMINATE)
userdefined = express_getattr(IfcCondenserTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcCondenserTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcConnectionTypeEnum = enum_namespace()
atpath = express_getattr(IfcConnectionTypeEnum, 'ATPATH', INDETERMINATE)
atstart = express_getattr(IfcConnectionTypeEnum, 'ATSTART', INDETERMINATE)
atend = express_getattr(IfcConnectionTypeEnum, 'ATEND', INDETERMINATE)
notdefined = express_getattr(IfcConnectionTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcConstraintEnum = enum_namespace()
hard = express_getattr(IfcConstraintEnum, 'HARD', INDETERMINATE)
soft = express_getattr(IfcConstraintEnum, 'SOFT', INDETERMINATE)
advisory = express_getattr(IfcConstraintEnum, 'ADVISORY', INDETERMINATE)
userdefined = express_getattr(IfcConstraintEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcConstraintEnum, 'NOTDEFINED', INDETERMINATE)
IfcConstructionEquipmentResourceTypeEnum = enum_namespace()
demolishing = express_getattr(IfcConstructionEquipmentResourceTypeEnum, 'DEMOLISHING', INDETERMINATE)
earthmoving = express_getattr(IfcConstructionEquipmentResourceTypeEnum, 'EARTHMOVING', INDETERMINATE)
erecting = express_getattr(IfcConstructionEquipmentResourceTypeEnum, 'ERECTING', INDETERMINATE)
heating = express_getattr(IfcConstructionEquipmentResourceTypeEnum, 'HEATING', INDETERMINATE)
lighting = express_getattr(IfcConstructionEquipmentResourceTypeEnum, 'LIGHTING', INDETERMINATE)
paving = express_getattr(IfcConstructionEquipmentResourceTypeEnum, 'PAVING', INDETERMINATE)
pumping = express_getattr(IfcConstructionEquipmentResourceTypeEnum, 'PUMPING', INDETERMINATE)
transporting = express_getattr(IfcConstructionEquipmentResourceTypeEnum, 'TRANSPORTING', INDETERMINATE)
userdefined = express_getattr(IfcConstructionEquipmentResourceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcConstructionEquipmentResourceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcConstructionMaterialResourceTypeEnum = enum_namespace()
aggregates = express_getattr(IfcConstructionMaterialResourceTypeEnum, 'AGGREGATES', INDETERMINATE)
concrete = express_getattr(IfcConstructionMaterialResourceTypeEnum, 'CONCRETE', INDETERMINATE)
drywall = express_getattr(IfcConstructionMaterialResourceTypeEnum, 'DRYWALL', INDETERMINATE)
fuel = express_getattr(IfcConstructionMaterialResourceTypeEnum, 'FUEL', INDETERMINATE)
gypsum = express_getattr(IfcConstructionMaterialResourceTypeEnum, 'GYPSUM', INDETERMINATE)
masonry = express_getattr(IfcConstructionMaterialResourceTypeEnum, 'MASONRY', INDETERMINATE)
metal = express_getattr(IfcConstructionMaterialResourceTypeEnum, 'METAL', INDETERMINATE)
plastic = express_getattr(IfcConstructionMaterialResourceTypeEnum, 'PLASTIC', INDETERMINATE)
wood = express_getattr(IfcConstructionMaterialResourceTypeEnum, 'WOOD', INDETERMINATE)
notdefined = express_getattr(IfcConstructionMaterialResourceTypeEnum, 'NOTDEFINED', INDETERMINATE)
userdefined = express_getattr(IfcConstructionMaterialResourceTypeEnum, 'USERDEFINED', INDETERMINATE)
IfcConstructionProductResourceTypeEnum = enum_namespace()
assembly = express_getattr(IfcConstructionProductResourceTypeEnum, 'ASSEMBLY', INDETERMINATE)
formwork = express_getattr(IfcConstructionProductResourceTypeEnum, 'FORMWORK', INDETERMINATE)
userdefined = express_getattr(IfcConstructionProductResourceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcConstructionProductResourceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcControllerTypeEnum = enum_namespace()
floating = express_getattr(IfcControllerTypeEnum, 'FLOATING', INDETERMINATE)
programmable = express_getattr(IfcControllerTypeEnum, 'PROGRAMMABLE', INDETERMINATE)
proportional = express_getattr(IfcControllerTypeEnum, 'PROPORTIONAL', INDETERMINATE)
multiposition = express_getattr(IfcControllerTypeEnum, 'MULTIPOSITION', INDETERMINATE)
twoposition = express_getattr(IfcControllerTypeEnum, 'TWOPOSITION', INDETERMINATE)
userdefined = express_getattr(IfcControllerTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcControllerTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcConveyorSegmentTypeEnum = enum_namespace()
chuteconveyor = express_getattr(IfcConveyorSegmentTypeEnum, 'CHUTECONVEYOR', INDETERMINATE)
beltconveyor = express_getattr(IfcConveyorSegmentTypeEnum, 'BELTCONVEYOR', INDETERMINATE)
screwconveyor = express_getattr(IfcConveyorSegmentTypeEnum, 'SCREWCONVEYOR', INDETERMINATE)
bucketconveyor = express_getattr(IfcConveyorSegmentTypeEnum, 'BUCKETCONVEYOR', INDETERMINATE)
userdefined = express_getattr(IfcConveyorSegmentTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcConveyorSegmentTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCooledBeamTypeEnum = enum_namespace()
active = express_getattr(IfcCooledBeamTypeEnum, 'ACTIVE', INDETERMINATE)
passive = express_getattr(IfcCooledBeamTypeEnum, 'PASSIVE', INDETERMINATE)
userdefined = express_getattr(IfcCooledBeamTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcCooledBeamTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCoolingTowerTypeEnum = enum_namespace()
naturaldraft = express_getattr(IfcCoolingTowerTypeEnum, 'NATURALDRAFT', INDETERMINATE)
mechanicalinduceddraft = express_getattr(IfcCoolingTowerTypeEnum, 'MECHANICALINDUCEDDRAFT', INDETERMINATE)
mechanicalforceddraft = express_getattr(IfcCoolingTowerTypeEnum, 'MECHANICALFORCEDDRAFT', INDETERMINATE)
userdefined = express_getattr(IfcCoolingTowerTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcCoolingTowerTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCostItemTypeEnum = enum_namespace()
userdefined = express_getattr(IfcCostItemTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcCostItemTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCostScheduleTypeEnum = enum_namespace()
budget = express_getattr(IfcCostScheduleTypeEnum, 'BUDGET', INDETERMINATE)
costplan = express_getattr(IfcCostScheduleTypeEnum, 'COSTPLAN', INDETERMINATE)
estimate = express_getattr(IfcCostScheduleTypeEnum, 'ESTIMATE', INDETERMINATE)
tender = express_getattr(IfcCostScheduleTypeEnum, 'TENDER', INDETERMINATE)
pricedbillofquantities = express_getattr(IfcCostScheduleTypeEnum, 'PRICEDBILLOFQUANTITIES', INDETERMINATE)
unpricedbillofquantities = express_getattr(IfcCostScheduleTypeEnum, 'UNPRICEDBILLOFQUANTITIES', INDETERMINATE)
scheduleofrates = express_getattr(IfcCostScheduleTypeEnum, 'SCHEDULEOFRATES', INDETERMINATE)
userdefined = express_getattr(IfcCostScheduleTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcCostScheduleTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCourseTypeEnum = enum_namespace()
armour = express_getattr(IfcCourseTypeEnum, 'ARMOUR', INDETERMINATE)
filter = express_getattr(IfcCourseTypeEnum, 'FILTER', INDETERMINATE)
ballastbed = express_getattr(IfcCourseTypeEnum, 'BALLASTBED', INDETERMINATE)
core = express_getattr(IfcCourseTypeEnum, 'CORE', INDETERMINATE)
pavement = express_getattr(IfcCourseTypeEnum, 'PAVEMENT', INDETERMINATE)
protection = express_getattr(IfcCourseTypeEnum, 'PROTECTION', INDETERMINATE)
userdefined = express_getattr(IfcCourseTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcCourseTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCoveringTypeEnum = enum_namespace()
ceiling = express_getattr(IfcCoveringTypeEnum, 'CEILING', INDETERMINATE)
flooring = express_getattr(IfcCoveringTypeEnum, 'FLOORING', INDETERMINATE)
cladding = express_getattr(IfcCoveringTypeEnum, 'CLADDING', INDETERMINATE)
roofing = express_getattr(IfcCoveringTypeEnum, 'ROOFING', INDETERMINATE)
molding = express_getattr(IfcCoveringTypeEnum, 'MOLDING', INDETERMINATE)
skirtingboard = express_getattr(IfcCoveringTypeEnum, 'SKIRTINGBOARD', INDETERMINATE)
insulation = express_getattr(IfcCoveringTypeEnum, 'INSULATION', INDETERMINATE)
membrane = express_getattr(IfcCoveringTypeEnum, 'MEMBRANE', INDETERMINATE)
sleeving = express_getattr(IfcCoveringTypeEnum, 'SLEEVING', INDETERMINATE)
wrapping = express_getattr(IfcCoveringTypeEnum, 'WRAPPING', INDETERMINATE)
coping = express_getattr(IfcCoveringTypeEnum, 'COPING', INDETERMINATE)
userdefined = express_getattr(IfcCoveringTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcCoveringTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCrewResourceTypeEnum = enum_namespace()
office = express_getattr(IfcCrewResourceTypeEnum, 'OFFICE', INDETERMINATE)
site = express_getattr(IfcCrewResourceTypeEnum, 'SITE', INDETERMINATE)
userdefined = express_getattr(IfcCrewResourceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcCrewResourceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCurtainWallTypeEnum = enum_namespace()
userdefined = express_getattr(IfcCurtainWallTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcCurtainWallTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCurveInterpolationEnum = enum_namespace()
linear = express_getattr(IfcCurveInterpolationEnum, 'LINEAR', INDETERMINATE)
log_linear = express_getattr(IfcCurveInterpolationEnum, 'LOG_LINEAR', INDETERMINATE)
log_log = express_getattr(IfcCurveInterpolationEnum, 'LOG_LOG', INDETERMINATE)
notdefined = express_getattr(IfcCurveInterpolationEnum, 'NOTDEFINED', INDETERMINATE)
IfcDamperTypeEnum = enum_namespace()
backdraftdamper = express_getattr(IfcDamperTypeEnum, 'BACKDRAFTDAMPER', INDETERMINATE)
balancingdamper = express_getattr(IfcDamperTypeEnum, 'BALANCINGDAMPER', INDETERMINATE)
blastdamper = express_getattr(IfcDamperTypeEnum, 'BLASTDAMPER', INDETERMINATE)
controldamper = express_getattr(IfcDamperTypeEnum, 'CONTROLDAMPER', INDETERMINATE)
firedamper = express_getattr(IfcDamperTypeEnum, 'FIREDAMPER', INDETERMINATE)
firesmokedamper = express_getattr(IfcDamperTypeEnum, 'FIRESMOKEDAMPER', INDETERMINATE)
fumehoodexhaust = express_getattr(IfcDamperTypeEnum, 'FUMEHOODEXHAUST', INDETERMINATE)
gravitydamper = express_getattr(IfcDamperTypeEnum, 'GRAVITYDAMPER', INDETERMINATE)
gravityreliefdamper = express_getattr(IfcDamperTypeEnum, 'GRAVITYRELIEFDAMPER', INDETERMINATE)
reliefdamper = express_getattr(IfcDamperTypeEnum, 'RELIEFDAMPER', INDETERMINATE)
smokedamper = express_getattr(IfcDamperTypeEnum, 'SMOKEDAMPER', INDETERMINATE)
userdefined = express_getattr(IfcDamperTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcDamperTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcDataOriginEnum = enum_namespace()
measured = express_getattr(IfcDataOriginEnum, 'MEASURED', INDETERMINATE)
predicted = express_getattr(IfcDataOriginEnum, 'PREDICTED', INDETERMINATE)
simulated = express_getattr(IfcDataOriginEnum, 'SIMULATED', INDETERMINATE)
userdefined = express_getattr(IfcDataOriginEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcDataOriginEnum, 'NOTDEFINED', INDETERMINATE)
IfcDerivedUnitEnum = enum_namespace()
angularvelocityunit = express_getattr(IfcDerivedUnitEnum, 'ANGULARVELOCITYUNIT', INDETERMINATE)
areadensityunit = express_getattr(IfcDerivedUnitEnum, 'AREADENSITYUNIT', INDETERMINATE)
compoundplaneangleunit = express_getattr(IfcDerivedUnitEnum, 'COMPOUNDPLANEANGLEUNIT', INDETERMINATE)
dynamicviscosityunit = express_getattr(IfcDerivedUnitEnum, 'DYNAMICVISCOSITYUNIT', INDETERMINATE)
heatfluxdensityunit = express_getattr(IfcDerivedUnitEnum, 'HEATFLUXDENSITYUNIT', INDETERMINATE)
integercountrateunit = express_getattr(IfcDerivedUnitEnum, 'INTEGERCOUNTRATEUNIT', INDETERMINATE)
isothermalmoisturecapacityunit = express_getattr(IfcDerivedUnitEnum, 'ISOTHERMALMOISTURECAPACITYUNIT', INDETERMINATE)
kinematicviscosityunit = express_getattr(IfcDerivedUnitEnum, 'KINEMATICVISCOSITYUNIT', INDETERMINATE)
linearvelocityunit = express_getattr(IfcDerivedUnitEnum, 'LINEARVELOCITYUNIT', INDETERMINATE)
massdensityunit = express_getattr(IfcDerivedUnitEnum, 'MASSDENSITYUNIT', INDETERMINATE)
massflowrateunit = express_getattr(IfcDerivedUnitEnum, 'MASSFLOWRATEUNIT', INDETERMINATE)
moisturediffusivityunit = express_getattr(IfcDerivedUnitEnum, 'MOISTUREDIFFUSIVITYUNIT', INDETERMINATE)
molecularweightunit = express_getattr(IfcDerivedUnitEnum, 'MOLECULARWEIGHTUNIT', INDETERMINATE)
specificheatcapacityunit = express_getattr(IfcDerivedUnitEnum, 'SPECIFICHEATCAPACITYUNIT', INDETERMINATE)
thermaladmittanceunit = express_getattr(IfcDerivedUnitEnum, 'THERMALADMITTANCEUNIT', INDETERMINATE)
thermalconductanceunit = express_getattr(IfcDerivedUnitEnum, 'THERMALCONDUCTANCEUNIT', INDETERMINATE)
thermalresistanceunit = express_getattr(IfcDerivedUnitEnum, 'THERMALRESISTANCEUNIT', INDETERMINATE)
thermaltransmittanceunit = express_getattr(IfcDerivedUnitEnum, 'THERMALTRANSMITTANCEUNIT', INDETERMINATE)
vaporpermeabilityunit = express_getattr(IfcDerivedUnitEnum, 'VAPORPERMEABILITYUNIT', INDETERMINATE)
volumetricflowrateunit = express_getattr(IfcDerivedUnitEnum, 'VOLUMETRICFLOWRATEUNIT', INDETERMINATE)
rotationalfrequencyunit = express_getattr(IfcDerivedUnitEnum, 'ROTATIONALFREQUENCYUNIT', INDETERMINATE)
torqueunit = express_getattr(IfcDerivedUnitEnum, 'TORQUEUNIT', INDETERMINATE)
momentofinertiaunit = express_getattr(IfcDerivedUnitEnum, 'MOMENTOFINERTIAUNIT', INDETERMINATE)
linearmomentunit = express_getattr(IfcDerivedUnitEnum, 'LINEARMOMENTUNIT', INDETERMINATE)
linearforceunit = express_getattr(IfcDerivedUnitEnum, 'LINEARFORCEUNIT', INDETERMINATE)
planarforceunit = express_getattr(IfcDerivedUnitEnum, 'PLANARFORCEUNIT', INDETERMINATE)
modulusofelasticityunit = express_getattr(IfcDerivedUnitEnum, 'MODULUSOFELASTICITYUNIT', INDETERMINATE)
shearmodulusunit = express_getattr(IfcDerivedUnitEnum, 'SHEARMODULUSUNIT', INDETERMINATE)
linearstiffnessunit = express_getattr(IfcDerivedUnitEnum, 'LINEARSTIFFNESSUNIT', INDETERMINATE)
rotationalstiffnessunit = express_getattr(IfcDerivedUnitEnum, 'ROTATIONALSTIFFNESSUNIT', INDETERMINATE)
modulusofsubgradereactionunit = express_getattr(IfcDerivedUnitEnum, 'MODULUSOFSUBGRADEREACTIONUNIT', INDETERMINATE)
accelerationunit = express_getattr(IfcDerivedUnitEnum, 'ACCELERATIONUNIT', INDETERMINATE)
curvatureunit = express_getattr(IfcDerivedUnitEnum, 'CURVATUREUNIT', INDETERMINATE)
heatingvalueunit = express_getattr(IfcDerivedUnitEnum, 'HEATINGVALUEUNIT', INDETERMINATE)
ionconcentrationunit = express_getattr(IfcDerivedUnitEnum, 'IONCONCENTRATIONUNIT', INDETERMINATE)
luminousintensitydistributionunit = express_getattr(IfcDerivedUnitEnum, 'LUMINOUSINTENSITYDISTRIBUTIONUNIT', INDETERMINATE)
massperlengthunit = express_getattr(IfcDerivedUnitEnum, 'MASSPERLENGTHUNIT', INDETERMINATE)
modulusoflinearsubgradereactionunit = express_getattr(IfcDerivedUnitEnum, 'MODULUSOFLINEARSUBGRADEREACTIONUNIT', INDETERMINATE)
modulusofrotationalsubgradereactionunit = express_getattr(IfcDerivedUnitEnum, 'MODULUSOFROTATIONALSUBGRADEREACTIONUNIT', INDETERMINATE)
phunit = express_getattr(IfcDerivedUnitEnum, 'PHUNIT', INDETERMINATE)
rotationalmassunit = express_getattr(IfcDerivedUnitEnum, 'ROTATIONALMASSUNIT', INDETERMINATE)
sectionareaintegralunit = express_getattr(IfcDerivedUnitEnum, 'SECTIONAREAINTEGRALUNIT', INDETERMINATE)
sectionmodulusunit = express_getattr(IfcDerivedUnitEnum, 'SECTIONMODULUSUNIT', INDETERMINATE)
soundpowerlevelunit = express_getattr(IfcDerivedUnitEnum, 'SOUNDPOWERLEVELUNIT', INDETERMINATE)
soundpowerunit = express_getattr(IfcDerivedUnitEnum, 'SOUNDPOWERUNIT', INDETERMINATE)
soundpressurelevelunit = express_getattr(IfcDerivedUnitEnum, 'SOUNDPRESSURELEVELUNIT', INDETERMINATE)
soundpressureunit = express_getattr(IfcDerivedUnitEnum, 'SOUNDPRESSUREUNIT', INDETERMINATE)
temperaturegradientunit = express_getattr(IfcDerivedUnitEnum, 'TEMPERATUREGRADIENTUNIT', INDETERMINATE)
temperaturerateofchangeunit = express_getattr(IfcDerivedUnitEnum, 'TEMPERATURERATEOFCHANGEUNIT', INDETERMINATE)
thermalexpansioncoefficientunit = express_getattr(IfcDerivedUnitEnum, 'THERMALEXPANSIONCOEFFICIENTUNIT', INDETERMINATE)
warpingconstantunit = express_getattr(IfcDerivedUnitEnum, 'WARPINGCONSTANTUNIT', INDETERMINATE)
warpingmomentunit = express_getattr(IfcDerivedUnitEnum, 'WARPINGMOMENTUNIT', INDETERMINATE)
userdefined = express_getattr(IfcDerivedUnitEnum, 'USERDEFINED', INDETERMINATE)
IfcDirectionSenseEnum = enum_namespace()
positive = express_getattr(IfcDirectionSenseEnum, 'POSITIVE', INDETERMINATE)
negative = express_getattr(IfcDirectionSenseEnum, 'NEGATIVE', INDETERMINATE)
IfcDiscreteAccessoryTypeEnum = enum_namespace()
anchorplate = express_getattr(IfcDiscreteAccessoryTypeEnum, 'ANCHORPLATE', INDETERMINATE)
bracket = express_getattr(IfcDiscreteAccessoryTypeEnum, 'BRACKET', INDETERMINATE)
shoe = express_getattr(IfcDiscreteAccessoryTypeEnum, 'SHOE', INDETERMINATE)
expansion_joint_device = express_getattr(IfcDiscreteAccessoryTypeEnum, 'EXPANSION_JOINT_DEVICE', INDETERMINATE)
cablearranger = express_getattr(IfcDiscreteAccessoryTypeEnum, 'CABLEARRANGER', INDETERMINATE)
insulator = express_getattr(IfcDiscreteAccessoryTypeEnum, 'INSULATOR', INDETERMINATE)
lock = express_getattr(IfcDiscreteAccessoryTypeEnum, 'LOCK', INDETERMINATE)
tensioningequipment = express_getattr(IfcDiscreteAccessoryTypeEnum, 'TENSIONINGEQUIPMENT', INDETERMINATE)
railpad = express_getattr(IfcDiscreteAccessoryTypeEnum, 'RAILPAD', INDETERMINATE)
slidingchair = express_getattr(IfcDiscreteAccessoryTypeEnum, 'SLIDINGCHAIR', INDETERMINATE)
rail_lubrication = express_getattr(IfcDiscreteAccessoryTypeEnum, 'RAIL_LUBRICATION', INDETERMINATE)
panel_strengthening = express_getattr(IfcDiscreteAccessoryTypeEnum, 'PANEL_STRENGTHENING', INDETERMINATE)
railbrace = express_getattr(IfcDiscreteAccessoryTypeEnum, 'RAILBRACE', INDETERMINATE)
elastic_cushion = express_getattr(IfcDiscreteAccessoryTypeEnum, 'ELASTIC_CUSHION', INDETERMINATE)
soundabsorption = express_getattr(IfcDiscreteAccessoryTypeEnum, 'SOUNDABSORPTION', INDETERMINATE)
pointmachinemountingdevice = express_getattr(IfcDiscreteAccessoryTypeEnum, 'POINTMACHINEMOUNTINGDEVICE', INDETERMINATE)
point_machine_locking_device = express_getattr(IfcDiscreteAccessoryTypeEnum, 'POINT_MACHINE_LOCKING_DEVICE', INDETERMINATE)
rail_mechanical_equipment = express_getattr(IfcDiscreteAccessoryTypeEnum, 'RAIL_MECHANICAL_EQUIPMENT', INDETERMINATE)
birdprotection = express_getattr(IfcDiscreteAccessoryTypeEnum, 'BIRDPROTECTION', INDETERMINATE)
userdefined = express_getattr(IfcDiscreteAccessoryTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcDiscreteAccessoryTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcDistributionBoardTypeEnum = enum_namespace()
switchboard = express_getattr(IfcDistributionBoardTypeEnum, 'SWITCHBOARD', INDETERMINATE)
consumerunit = express_getattr(IfcDistributionBoardTypeEnum, 'CONSUMERUNIT', INDETERMINATE)
motorcontrolcentre = express_getattr(IfcDistributionBoardTypeEnum, 'MOTORCONTROLCENTRE', INDETERMINATE)
distributionframe = express_getattr(IfcDistributionBoardTypeEnum, 'DISTRIBUTIONFRAME', INDETERMINATE)
distributionboard = express_getattr(IfcDistributionBoardTypeEnum, 'DISTRIBUTIONBOARD', INDETERMINATE)
dispatchingboard = express_getattr(IfcDistributionBoardTypeEnum, 'DISPATCHINGBOARD', INDETERMINATE)
userdefined = express_getattr(IfcDistributionBoardTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcDistributionBoardTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcDistributionChamberElementTypeEnum = enum_namespace()
formedduct = express_getattr(IfcDistributionChamberElementTypeEnum, 'FORMEDDUCT', INDETERMINATE)
inspectionchamber = express_getattr(IfcDistributionChamberElementTypeEnum, 'INSPECTIONCHAMBER', INDETERMINATE)
inspectionpit = express_getattr(IfcDistributionChamberElementTypeEnum, 'INSPECTIONPIT', INDETERMINATE)
manhole = express_getattr(IfcDistributionChamberElementTypeEnum, 'MANHOLE', INDETERMINATE)
meterchamber = express_getattr(IfcDistributionChamberElementTypeEnum, 'METERCHAMBER', INDETERMINATE)
sump = express_getattr(IfcDistributionChamberElementTypeEnum, 'SUMP', INDETERMINATE)
trench = express_getattr(IfcDistributionChamberElementTypeEnum, 'TRENCH', INDETERMINATE)
valvechamber = express_getattr(IfcDistributionChamberElementTypeEnum, 'VALVECHAMBER', INDETERMINATE)
userdefined = express_getattr(IfcDistributionChamberElementTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcDistributionChamberElementTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcDistributionPortTypeEnum = enum_namespace()
cable = express_getattr(IfcDistributionPortTypeEnum, 'CABLE', INDETERMINATE)
cablecarrier = express_getattr(IfcDistributionPortTypeEnum, 'CABLECARRIER', INDETERMINATE)
duct = express_getattr(IfcDistributionPortTypeEnum, 'DUCT', INDETERMINATE)
pipe = express_getattr(IfcDistributionPortTypeEnum, 'PIPE', INDETERMINATE)
wireless = express_getattr(IfcDistributionPortTypeEnum, 'WIRELESS', INDETERMINATE)
userdefined = express_getattr(IfcDistributionPortTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcDistributionPortTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcDistributionSystemEnum = enum_namespace()
airconditioning = express_getattr(IfcDistributionSystemEnum, 'AIRCONDITIONING', INDETERMINATE)
audiovisual = express_getattr(IfcDistributionSystemEnum, 'AUDIOVISUAL', INDETERMINATE)
chemical = express_getattr(IfcDistributionSystemEnum, 'CHEMICAL', INDETERMINATE)
chilledwater = express_getattr(IfcDistributionSystemEnum, 'CHILLEDWATER', INDETERMINATE)
communication = express_getattr(IfcDistributionSystemEnum, 'COMMUNICATION', INDETERMINATE)
compressedair = express_getattr(IfcDistributionSystemEnum, 'COMPRESSEDAIR', INDETERMINATE)
condenserwater = express_getattr(IfcDistributionSystemEnum, 'CONDENSERWATER', INDETERMINATE)
control = express_getattr(IfcDistributionSystemEnum, 'CONTROL', INDETERMINATE)
conveying = express_getattr(IfcDistributionSystemEnum, 'CONVEYING', INDETERMINATE)
data = express_getattr(IfcDistributionSystemEnum, 'DATA', INDETERMINATE)
disposal = express_getattr(IfcDistributionSystemEnum, 'DISPOSAL', INDETERMINATE)
domesticcoldwater = express_getattr(IfcDistributionSystemEnum, 'DOMESTICCOLDWATER', INDETERMINATE)
domestichotwater = express_getattr(IfcDistributionSystemEnum, 'DOMESTICHOTWATER', INDETERMINATE)
drainage = express_getattr(IfcDistributionSystemEnum, 'DRAINAGE', INDETERMINATE)
earthing = express_getattr(IfcDistributionSystemEnum, 'EARTHING', INDETERMINATE)
electrical = express_getattr(IfcDistributionSystemEnum, 'ELECTRICAL', INDETERMINATE)
electroacoustic = express_getattr(IfcDistributionSystemEnum, 'ELECTROACOUSTIC', INDETERMINATE)
exhaust = express_getattr(IfcDistributionSystemEnum, 'EXHAUST', INDETERMINATE)
fireprotection = express_getattr(IfcDistributionSystemEnum, 'FIREPROTECTION', INDETERMINATE)
fuel = express_getattr(IfcDistributionSystemEnum, 'FUEL', INDETERMINATE)
gas = express_getattr(IfcDistributionSystemEnum, 'GAS', INDETERMINATE)
hazardous = express_getattr(IfcDistributionSystemEnum, 'HAZARDOUS', INDETERMINATE)
heating = express_getattr(IfcDistributionSystemEnum, 'HEATING', INDETERMINATE)
lighting = express_getattr(IfcDistributionSystemEnum, 'LIGHTING', INDETERMINATE)
lightningprotection = express_getattr(IfcDistributionSystemEnum, 'LIGHTNINGPROTECTION', INDETERMINATE)
municipalsolidwaste = express_getattr(IfcDistributionSystemEnum, 'MUNICIPALSOLIDWASTE', INDETERMINATE)
oil = express_getattr(IfcDistributionSystemEnum, 'OIL', INDETERMINATE)
operational = express_getattr(IfcDistributionSystemEnum, 'OPERATIONAL', INDETERMINATE)
powergeneration = express_getattr(IfcDistributionSystemEnum, 'POWERGENERATION', INDETERMINATE)
rainwater = express_getattr(IfcDistributionSystemEnum, 'RAINWATER', INDETERMINATE)
refrigeration = express_getattr(IfcDistributionSystemEnum, 'REFRIGERATION', INDETERMINATE)
security = express_getattr(IfcDistributionSystemEnum, 'SECURITY', INDETERMINATE)
sewage = express_getattr(IfcDistributionSystemEnum, 'SEWAGE', INDETERMINATE)
signal = express_getattr(IfcDistributionSystemEnum, 'SIGNAL', INDETERMINATE)
stormwater = express_getattr(IfcDistributionSystemEnum, 'STORMWATER', INDETERMINATE)
telephone = express_getattr(IfcDistributionSystemEnum, 'TELEPHONE', INDETERMINATE)
tv = express_getattr(IfcDistributionSystemEnum, 'TV', INDETERMINATE)
vacuum = express_getattr(IfcDistributionSystemEnum, 'VACUUM', INDETERMINATE)
vent = express_getattr(IfcDistributionSystemEnum, 'VENT', INDETERMINATE)
ventilation = express_getattr(IfcDistributionSystemEnum, 'VENTILATION', INDETERMINATE)
wastewater = express_getattr(IfcDistributionSystemEnum, 'WASTEWATER', INDETERMINATE)
watersupply = express_getattr(IfcDistributionSystemEnum, 'WATERSUPPLY', INDETERMINATE)
catenary_system = express_getattr(IfcDistributionSystemEnum, 'CATENARY_SYSTEM', INDETERMINATE)
overhead_contactline_system = express_getattr(IfcDistributionSystemEnum, 'OVERHEAD_CONTACTLINE_SYSTEM', INDETERMINATE)
return_circuit = express_getattr(IfcDistributionSystemEnum, 'RETURN_CIRCUIT', INDETERMINATE)
fixedtransmissionnetwork = express_getattr(IfcDistributionSystemEnum, 'FIXEDTRANSMISSIONNETWORK', INDETERMINATE)
operationaltelephonysystem = express_getattr(IfcDistributionSystemEnum, 'OPERATIONALTELEPHONYSYSTEM', INDETERMINATE)
mobilenetwork = express_getattr(IfcDistributionSystemEnum, 'MOBILENETWORK', INDETERMINATE)
monitoringsystem = express_getattr(IfcDistributionSystemEnum, 'MONITORINGSYSTEM', INDETERMINATE)
userdefined = express_getattr(IfcDistributionSystemEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcDistributionSystemEnum, 'NOTDEFINED', INDETERMINATE)
IfcDocumentConfidentialityEnum = enum_namespace()
public = express_getattr(IfcDocumentConfidentialityEnum, 'PUBLIC', INDETERMINATE)
restricted = express_getattr(IfcDocumentConfidentialityEnum, 'RESTRICTED', INDETERMINATE)
confidential = express_getattr(IfcDocumentConfidentialityEnum, 'CONFIDENTIAL', INDETERMINATE)
personal = express_getattr(IfcDocumentConfidentialityEnum, 'PERSONAL', INDETERMINATE)
userdefined = express_getattr(IfcDocumentConfidentialityEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcDocumentConfidentialityEnum, 'NOTDEFINED', INDETERMINATE)
IfcDocumentStatusEnum = enum_namespace()
draft = express_getattr(IfcDocumentStatusEnum, 'DRAFT', INDETERMINATE)
finaldraft = express_getattr(IfcDocumentStatusEnum, 'FINALDRAFT', INDETERMINATE)
final = express_getattr(IfcDocumentStatusEnum, 'FINAL', INDETERMINATE)
revision = express_getattr(IfcDocumentStatusEnum, 'REVISION', INDETERMINATE)
notdefined = express_getattr(IfcDocumentStatusEnum, 'NOTDEFINED', INDETERMINATE)
IfcDoorPanelOperationEnum = enum_namespace()
swinging = express_getattr(IfcDoorPanelOperationEnum, 'SWINGING', INDETERMINATE)
double_acting = express_getattr(IfcDoorPanelOperationEnum, 'DOUBLE_ACTING', INDETERMINATE)
sliding = express_getattr(IfcDoorPanelOperationEnum, 'SLIDING', INDETERMINATE)
folding = express_getattr(IfcDoorPanelOperationEnum, 'FOLDING', INDETERMINATE)
revolving = express_getattr(IfcDoorPanelOperationEnum, 'REVOLVING', INDETERMINATE)
rollingup = express_getattr(IfcDoorPanelOperationEnum, 'ROLLINGUP', INDETERMINATE)
fixedpanel = express_getattr(IfcDoorPanelOperationEnum, 'FIXEDPANEL', INDETERMINATE)
userdefined = express_getattr(IfcDoorPanelOperationEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcDoorPanelOperationEnum, 'NOTDEFINED', INDETERMINATE)
IfcDoorPanelPositionEnum = enum_namespace()
left = express_getattr(IfcDoorPanelPositionEnum, 'LEFT', INDETERMINATE)
middle = express_getattr(IfcDoorPanelPositionEnum, 'MIDDLE', INDETERMINATE)
right = express_getattr(IfcDoorPanelPositionEnum, 'RIGHT', INDETERMINATE)
notdefined = express_getattr(IfcDoorPanelPositionEnum, 'NOTDEFINED', INDETERMINATE)
IfcDoorStyleConstructionEnum = enum_namespace()
aluminium = express_getattr(IfcDoorStyleConstructionEnum, 'ALUMINIUM', INDETERMINATE)
high_grade_steel = express_getattr(IfcDoorStyleConstructionEnum, 'HIGH_GRADE_STEEL', INDETERMINATE)
steel = express_getattr(IfcDoorStyleConstructionEnum, 'STEEL', INDETERMINATE)
wood = express_getattr(IfcDoorStyleConstructionEnum, 'WOOD', INDETERMINATE)
aluminium_wood = express_getattr(IfcDoorStyleConstructionEnum, 'ALUMINIUM_WOOD', INDETERMINATE)
aluminium_plastic = express_getattr(IfcDoorStyleConstructionEnum, 'ALUMINIUM_PLASTIC', INDETERMINATE)
plastic = express_getattr(IfcDoorStyleConstructionEnum, 'PLASTIC', INDETERMINATE)
userdefined = express_getattr(IfcDoorStyleConstructionEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcDoorStyleConstructionEnum, 'NOTDEFINED', INDETERMINATE)
IfcDoorStyleOperationEnum = enum_namespace()
single_swing_left = express_getattr(IfcDoorStyleOperationEnum, 'SINGLE_SWING_LEFT', INDETERMINATE)
single_swing_right = express_getattr(IfcDoorStyleOperationEnum, 'SINGLE_SWING_RIGHT', INDETERMINATE)
double_door_single_swing = express_getattr(IfcDoorStyleOperationEnum, 'DOUBLE_DOOR_SINGLE_SWING', INDETERMINATE)
double_door_single_swing_opposite_left = express_getattr(IfcDoorStyleOperationEnum, 'DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_LEFT', INDETERMINATE)
double_door_single_swing_opposite_right = express_getattr(IfcDoorStyleOperationEnum, 'DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_RIGHT', INDETERMINATE)
double_swing_left = express_getattr(IfcDoorStyleOperationEnum, 'DOUBLE_SWING_LEFT', INDETERMINATE)
double_swing_right = express_getattr(IfcDoorStyleOperationEnum, 'DOUBLE_SWING_RIGHT', INDETERMINATE)
double_door_double_swing = express_getattr(IfcDoorStyleOperationEnum, 'DOUBLE_DOOR_DOUBLE_SWING', INDETERMINATE)
sliding_to_left = express_getattr(IfcDoorStyleOperationEnum, 'SLIDING_TO_LEFT', INDETERMINATE)
sliding_to_right = express_getattr(IfcDoorStyleOperationEnum, 'SLIDING_TO_RIGHT', INDETERMINATE)
double_door_sliding = express_getattr(IfcDoorStyleOperationEnum, 'DOUBLE_DOOR_SLIDING', INDETERMINATE)
folding_to_left = express_getattr(IfcDoorStyleOperationEnum, 'FOLDING_TO_LEFT', INDETERMINATE)
folding_to_right = express_getattr(IfcDoorStyleOperationEnum, 'FOLDING_TO_RIGHT', INDETERMINATE)
double_door_folding = express_getattr(IfcDoorStyleOperationEnum, 'DOUBLE_DOOR_FOLDING', INDETERMINATE)
revolving = express_getattr(IfcDoorStyleOperationEnum, 'REVOLVING', INDETERMINATE)
rollingup = express_getattr(IfcDoorStyleOperationEnum, 'ROLLINGUP', INDETERMINATE)
userdefined = express_getattr(IfcDoorStyleOperationEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcDoorStyleOperationEnum, 'NOTDEFINED', INDETERMINATE)
IfcDoorTypeEnum = enum_namespace()
door = express_getattr(IfcDoorTypeEnum, 'DOOR', INDETERMINATE)
gate = express_getattr(IfcDoorTypeEnum, 'GATE', INDETERMINATE)
trapdoor = express_getattr(IfcDoorTypeEnum, 'TRAPDOOR', INDETERMINATE)
boom_barrier = express_getattr(IfcDoorTypeEnum, 'BOOM_BARRIER', INDETERMINATE)
turnstile = express_getattr(IfcDoorTypeEnum, 'TURNSTILE', INDETERMINATE)
userdefined = express_getattr(IfcDoorTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcDoorTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcDoorTypeOperationEnum = enum_namespace()
single_swing_left = express_getattr(IfcDoorTypeOperationEnum, 'SINGLE_SWING_LEFT', INDETERMINATE)
single_swing_right = express_getattr(IfcDoorTypeOperationEnum, 'SINGLE_SWING_RIGHT', INDETERMINATE)
double_panel_single_swing = express_getattr(IfcDoorTypeOperationEnum, 'DOUBLE_PANEL_SINGLE_SWING', INDETERMINATE)
double_panel_single_swing_opposite_left = express_getattr(IfcDoorTypeOperationEnum, 'DOUBLE_PANEL_SINGLE_SWING_OPPOSITE_LEFT', INDETERMINATE)
double_panel_single_swing_opposite_right = express_getattr(IfcDoorTypeOperationEnum, 'DOUBLE_PANEL_SINGLE_SWING_OPPOSITE_RIGHT', INDETERMINATE)
double_swing_left = express_getattr(IfcDoorTypeOperationEnum, 'DOUBLE_SWING_LEFT', INDETERMINATE)
double_swing_right = express_getattr(IfcDoorTypeOperationEnum, 'DOUBLE_SWING_RIGHT', INDETERMINATE)
double_panel_double_swing = express_getattr(IfcDoorTypeOperationEnum, 'DOUBLE_PANEL_DOUBLE_SWING', INDETERMINATE)
sliding_to_left = express_getattr(IfcDoorTypeOperationEnum, 'SLIDING_TO_LEFT', INDETERMINATE)
sliding_to_right = express_getattr(IfcDoorTypeOperationEnum, 'SLIDING_TO_RIGHT', INDETERMINATE)
double_panel_sliding = express_getattr(IfcDoorTypeOperationEnum, 'DOUBLE_PANEL_SLIDING', INDETERMINATE)
folding_to_left = express_getattr(IfcDoorTypeOperationEnum, 'FOLDING_TO_LEFT', INDETERMINATE)
folding_to_right = express_getattr(IfcDoorTypeOperationEnum, 'FOLDING_TO_RIGHT', INDETERMINATE)
double_panel_folding = express_getattr(IfcDoorTypeOperationEnum, 'DOUBLE_PANEL_FOLDING', INDETERMINATE)
revolving_horizontal = express_getattr(IfcDoorTypeOperationEnum, 'REVOLVING_HORIZONTAL', INDETERMINATE)
rollingup = express_getattr(IfcDoorTypeOperationEnum, 'ROLLINGUP', INDETERMINATE)
swing_fixed_left = express_getattr(IfcDoorTypeOperationEnum, 'SWING_FIXED_LEFT', INDETERMINATE)
swing_fixed_right = express_getattr(IfcDoorTypeOperationEnum, 'SWING_FIXED_RIGHT', INDETERMINATE)
double_panel_lifting_vertical = express_getattr(IfcDoorTypeOperationEnum, 'DOUBLE_PANEL_LIFTING_VERTICAL', INDETERMINATE)
lifting_horizontal = express_getattr(IfcDoorTypeOperationEnum, 'LIFTING_HORIZONTAL', INDETERMINATE)
lifting_vertical_left = express_getattr(IfcDoorTypeOperationEnum, 'LIFTING_VERTICAL_LEFT', INDETERMINATE)
lifting_vertical_right = express_getattr(IfcDoorTypeOperationEnum, 'LIFTING_VERTICAL_RIGHT', INDETERMINATE)
revolving_vertical = express_getattr(IfcDoorTypeOperationEnum, 'REVOLVING_VERTICAL', INDETERMINATE)
userdefined = express_getattr(IfcDoorTypeOperationEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcDoorTypeOperationEnum, 'NOTDEFINED', INDETERMINATE)
IfcDuctFittingTypeEnum = enum_namespace()
bend = express_getattr(IfcDuctFittingTypeEnum, 'BEND', INDETERMINATE)
connector = express_getattr(IfcDuctFittingTypeEnum, 'CONNECTOR', INDETERMINATE)
entry = express_getattr(IfcDuctFittingTypeEnum, 'ENTRY', INDETERMINATE)
exit = express_getattr(IfcDuctFittingTypeEnum, 'EXIT', INDETERMINATE)
junction = express_getattr(IfcDuctFittingTypeEnum, 'JUNCTION', INDETERMINATE)
obstruction = express_getattr(IfcDuctFittingTypeEnum, 'OBSTRUCTION', INDETERMINATE)
transition = express_getattr(IfcDuctFittingTypeEnum, 'TRANSITION', INDETERMINATE)
userdefined = express_getattr(IfcDuctFittingTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcDuctFittingTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcDuctSegmentTypeEnum = enum_namespace()
rigidsegment = express_getattr(IfcDuctSegmentTypeEnum, 'RIGIDSEGMENT', INDETERMINATE)
flexiblesegment = express_getattr(IfcDuctSegmentTypeEnum, 'FLEXIBLESEGMENT', INDETERMINATE)
userdefined = express_getattr(IfcDuctSegmentTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcDuctSegmentTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcDuctSilencerTypeEnum = enum_namespace()
flatoval = express_getattr(IfcDuctSilencerTypeEnum, 'FLATOVAL', INDETERMINATE)
rectangular = express_getattr(IfcDuctSilencerTypeEnum, 'RECTANGULAR', INDETERMINATE)
round = express_getattr(IfcDuctSilencerTypeEnum, 'ROUND', INDETERMINATE)
userdefined = express_getattr(IfcDuctSilencerTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcDuctSilencerTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcEarthworksCutTypeEnum = enum_namespace()
trench = express_getattr(IfcEarthworksCutTypeEnum, 'TRENCH', INDETERMINATE)
dredging = express_getattr(IfcEarthworksCutTypeEnum, 'DREDGING', INDETERMINATE)
excavation = express_getattr(IfcEarthworksCutTypeEnum, 'EXCAVATION', INDETERMINATE)
overexcavation = express_getattr(IfcEarthworksCutTypeEnum, 'OVEREXCAVATION', INDETERMINATE)
topsoilremoval = express_getattr(IfcEarthworksCutTypeEnum, 'TOPSOILREMOVAL', INDETERMINATE)
stepexcavation = express_getattr(IfcEarthworksCutTypeEnum, 'STEPEXCAVATION', INDETERMINATE)
pavementmilling = express_getattr(IfcEarthworksCutTypeEnum, 'PAVEMENTMILLING', INDETERMINATE)
cut = express_getattr(IfcEarthworksCutTypeEnum, 'CUT', INDETERMINATE)
base_excavation = express_getattr(IfcEarthworksCutTypeEnum, 'BASE_EXCAVATION', INDETERMINATE)
userdefined = express_getattr(IfcEarthworksCutTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcEarthworksCutTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcEarthworksFillTypeEnum = enum_namespace()
backfill = express_getattr(IfcEarthworksFillTypeEnum, 'BACKFILL', INDETERMINATE)
counterweight = express_getattr(IfcEarthworksFillTypeEnum, 'COUNTERWEIGHT', INDETERMINATE)
subgrade = express_getattr(IfcEarthworksFillTypeEnum, 'SUBGRADE', INDETERMINATE)
embankment = express_getattr(IfcEarthworksFillTypeEnum, 'EMBANKMENT', INDETERMINATE)
transitionsection = express_getattr(IfcEarthworksFillTypeEnum, 'TRANSITIONSECTION', INDETERMINATE)
subgradebed = express_getattr(IfcEarthworksFillTypeEnum, 'SUBGRADEBED', INDETERMINATE)
slopefill = express_getattr(IfcEarthworksFillTypeEnum, 'SLOPEFILL', INDETERMINATE)
userdefined = express_getattr(IfcEarthworksFillTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcEarthworksFillTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcElectricApplianceTypeEnum = enum_namespace()
dishwasher = express_getattr(IfcElectricApplianceTypeEnum, 'DISHWASHER', INDETERMINATE)
electriccooker = express_getattr(IfcElectricApplianceTypeEnum, 'ELECTRICCOOKER', INDETERMINATE)
freestandingelectricheater = express_getattr(IfcElectricApplianceTypeEnum, 'FREESTANDINGELECTRICHEATER', INDETERMINATE)
freestandingfan = express_getattr(IfcElectricApplianceTypeEnum, 'FREESTANDINGFAN', INDETERMINATE)
freestandingwaterheater = express_getattr(IfcElectricApplianceTypeEnum, 'FREESTANDINGWATERHEATER', INDETERMINATE)
freestandingwatercooler = express_getattr(IfcElectricApplianceTypeEnum, 'FREESTANDINGWATERCOOLER', INDETERMINATE)
freezer = express_getattr(IfcElectricApplianceTypeEnum, 'FREEZER', INDETERMINATE)
fridge_freezer = express_getattr(IfcElectricApplianceTypeEnum, 'FRIDGE_FREEZER', INDETERMINATE)
handdryer = express_getattr(IfcElectricApplianceTypeEnum, 'HANDDRYER', INDETERMINATE)
kitchenmachine = express_getattr(IfcElectricApplianceTypeEnum, 'KITCHENMACHINE', INDETERMINATE)
microwave = express_getattr(IfcElectricApplianceTypeEnum, 'MICROWAVE', INDETERMINATE)
photocopier = express_getattr(IfcElectricApplianceTypeEnum, 'PHOTOCOPIER', INDETERMINATE)
refrigerator = express_getattr(IfcElectricApplianceTypeEnum, 'REFRIGERATOR', INDETERMINATE)
tumbledryer = express_getattr(IfcElectricApplianceTypeEnum, 'TUMBLEDRYER', INDETERMINATE)
vendingmachine = express_getattr(IfcElectricApplianceTypeEnum, 'VENDINGMACHINE', INDETERMINATE)
washingmachine = express_getattr(IfcElectricApplianceTypeEnum, 'WASHINGMACHINE', INDETERMINATE)
userdefined = express_getattr(IfcElectricApplianceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcElectricApplianceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcElectricDistributionBoardTypeEnum = enum_namespace()
consumerunit = express_getattr(IfcElectricDistributionBoardTypeEnum, 'CONSUMERUNIT', INDETERMINATE)
distributionboard = express_getattr(IfcElectricDistributionBoardTypeEnum, 'DISTRIBUTIONBOARD', INDETERMINATE)
motorcontrolcentre = express_getattr(IfcElectricDistributionBoardTypeEnum, 'MOTORCONTROLCENTRE', INDETERMINATE)
switchboard = express_getattr(IfcElectricDistributionBoardTypeEnum, 'SWITCHBOARD', INDETERMINATE)
userdefined = express_getattr(IfcElectricDistributionBoardTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcElectricDistributionBoardTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcElectricFlowStorageDeviceTypeEnum = enum_namespace()
battery = express_getattr(IfcElectricFlowStorageDeviceTypeEnum, 'BATTERY', INDETERMINATE)
capacitorbank = express_getattr(IfcElectricFlowStorageDeviceTypeEnum, 'CAPACITORBANK', INDETERMINATE)
harmonicfilter = express_getattr(IfcElectricFlowStorageDeviceTypeEnum, 'HARMONICFILTER', INDETERMINATE)
inductorbank = express_getattr(IfcElectricFlowStorageDeviceTypeEnum, 'INDUCTORBANK', INDETERMINATE)
ups = express_getattr(IfcElectricFlowStorageDeviceTypeEnum, 'UPS', INDETERMINATE)
capacitor = express_getattr(IfcElectricFlowStorageDeviceTypeEnum, 'CAPACITOR', INDETERMINATE)
compensator = express_getattr(IfcElectricFlowStorageDeviceTypeEnum, 'COMPENSATOR', INDETERMINATE)
inductor = express_getattr(IfcElectricFlowStorageDeviceTypeEnum, 'INDUCTOR', INDETERMINATE)
recharger = express_getattr(IfcElectricFlowStorageDeviceTypeEnum, 'RECHARGER', INDETERMINATE)
userdefined = express_getattr(IfcElectricFlowStorageDeviceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcElectricFlowStorageDeviceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcElectricFlowTreatmentDeviceTypeEnum = enum_namespace()
electronicfilter = express_getattr(IfcElectricFlowTreatmentDeviceTypeEnum, 'ELECTRONICFILTER', INDETERMINATE)
userdefined = express_getattr(IfcElectricFlowTreatmentDeviceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcElectricFlowTreatmentDeviceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcElectricGeneratorTypeEnum = enum_namespace()
chp = express_getattr(IfcElectricGeneratorTypeEnum, 'CHP', INDETERMINATE)
enginegenerator = express_getattr(IfcElectricGeneratorTypeEnum, 'ENGINEGENERATOR', INDETERMINATE)
standalone = express_getattr(IfcElectricGeneratorTypeEnum, 'STANDALONE', INDETERMINATE)
userdefined = express_getattr(IfcElectricGeneratorTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcElectricGeneratorTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcElectricMotorTypeEnum = enum_namespace()
dc = express_getattr(IfcElectricMotorTypeEnum, 'DC', INDETERMINATE)
induction = express_getattr(IfcElectricMotorTypeEnum, 'INDUCTION', INDETERMINATE)
polyphase = express_getattr(IfcElectricMotorTypeEnum, 'POLYPHASE', INDETERMINATE)
reluctancesynchronous = express_getattr(IfcElectricMotorTypeEnum, 'RELUCTANCESYNCHRONOUS', INDETERMINATE)
synchronous = express_getattr(IfcElectricMotorTypeEnum, 'SYNCHRONOUS', INDETERMINATE)
userdefined = express_getattr(IfcElectricMotorTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcElectricMotorTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcElectricTimeControlTypeEnum = enum_namespace()
timeclock = express_getattr(IfcElectricTimeControlTypeEnum, 'TIMECLOCK', INDETERMINATE)
timedelay = express_getattr(IfcElectricTimeControlTypeEnum, 'TIMEDELAY', INDETERMINATE)
relay = express_getattr(IfcElectricTimeControlTypeEnum, 'RELAY', INDETERMINATE)
userdefined = express_getattr(IfcElectricTimeControlTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcElectricTimeControlTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcElementAssemblyTypeEnum = enum_namespace()
accessory_assembly = express_getattr(IfcElementAssemblyTypeEnum, 'ACCESSORY_ASSEMBLY', INDETERMINATE)
arch = express_getattr(IfcElementAssemblyTypeEnum, 'ARCH', INDETERMINATE)
beam_grid = express_getattr(IfcElementAssemblyTypeEnum, 'BEAM_GRID', INDETERMINATE)
braced_frame = express_getattr(IfcElementAssemblyTypeEnum, 'BRACED_FRAME', INDETERMINATE)
girder = express_getattr(IfcElementAssemblyTypeEnum, 'GIRDER', INDETERMINATE)
reinforcement_unit = express_getattr(IfcElementAssemblyTypeEnum, 'REINFORCEMENT_UNIT', INDETERMINATE)
rigid_frame = express_getattr(IfcElementAssemblyTypeEnum, 'RIGID_FRAME', INDETERMINATE)
slab_field = express_getattr(IfcElementAssemblyTypeEnum, 'SLAB_FIELD', INDETERMINATE)
truss = express_getattr(IfcElementAssemblyTypeEnum, 'TRUSS', INDETERMINATE)
abutment = express_getattr(IfcElementAssemblyTypeEnum, 'ABUTMENT', INDETERMINATE)
pier = express_getattr(IfcElementAssemblyTypeEnum, 'PIER', INDETERMINATE)
pylon = express_getattr(IfcElementAssemblyTypeEnum, 'PYLON', INDETERMINATE)
cross_bracing = express_getattr(IfcElementAssemblyTypeEnum, 'CROSS_BRACING', INDETERMINATE)
deck = express_getattr(IfcElementAssemblyTypeEnum, 'DECK', INDETERMINATE)
mast = express_getattr(IfcElementAssemblyTypeEnum, 'MAST', INDETERMINATE)
signalassembly = express_getattr(IfcElementAssemblyTypeEnum, 'SIGNALASSEMBLY', INDETERMINATE)
grid = express_getattr(IfcElementAssemblyTypeEnum, 'GRID', INDETERMINATE)
shelter = express_getattr(IfcElementAssemblyTypeEnum, 'SHELTER', INDETERMINATE)
supportingassembly = express_getattr(IfcElementAssemblyTypeEnum, 'SUPPORTINGASSEMBLY', INDETERMINATE)
suspensionassembly = express_getattr(IfcElementAssemblyTypeEnum, 'SUSPENSIONASSEMBLY', INDETERMINATE)
traction_switching_assembly = express_getattr(IfcElementAssemblyTypeEnum, 'TRACTION_SWITCHING_ASSEMBLY', INDETERMINATE)
trackpanel = express_getattr(IfcElementAssemblyTypeEnum, 'TRACKPANEL', INDETERMINATE)
turnoutpanel = express_getattr(IfcElementAssemblyTypeEnum, 'TURNOUTPANEL', INDETERMINATE)
dilatationpanel = express_getattr(IfcElementAssemblyTypeEnum, 'DILATATIONPANEL', INDETERMINATE)
rail_mechanical_equipment_assembly = express_getattr(IfcElementAssemblyTypeEnum, 'RAIL_MECHANICAL_EQUIPMENT_ASSEMBLY', INDETERMINATE)
entranceworks = express_getattr(IfcElementAssemblyTypeEnum, 'ENTRANCEWORKS', INDETERMINATE)
sumpbuster = express_getattr(IfcElementAssemblyTypeEnum, 'SUMPBUSTER', INDETERMINATE)
traffic_calming_device = express_getattr(IfcElementAssemblyTypeEnum, 'TRAFFIC_CALMING_DEVICE', INDETERMINATE)
userdefined = express_getattr(IfcElementAssemblyTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcElementAssemblyTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcElementCompositionEnum = enum_namespace()
complex = express_getattr(IfcElementCompositionEnum, 'COMPLEX', INDETERMINATE)
element = express_getattr(IfcElementCompositionEnum, 'ELEMENT', INDETERMINATE)
partial = express_getattr(IfcElementCompositionEnum, 'PARTIAL', INDETERMINATE)
IfcEngineTypeEnum = enum_namespace()
externalcombustion = express_getattr(IfcEngineTypeEnum, 'EXTERNALCOMBUSTION', INDETERMINATE)
internalcombustion = express_getattr(IfcEngineTypeEnum, 'INTERNALCOMBUSTION', INDETERMINATE)
userdefined = express_getattr(IfcEngineTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcEngineTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcEvaporativeCoolerTypeEnum = enum_namespace()
directevaporativerandommediaaircooler = express_getattr(IfcEvaporativeCoolerTypeEnum, 'DIRECTEVAPORATIVERANDOMMEDIAAIRCOOLER', INDETERMINATE)
directevaporativerigidmediaaircooler = express_getattr(IfcEvaporativeCoolerTypeEnum, 'DIRECTEVAPORATIVERIGIDMEDIAAIRCOOLER', INDETERMINATE)
directevaporativeslingerspackagedaircooler = express_getattr(IfcEvaporativeCoolerTypeEnum, 'DIRECTEVAPORATIVESLINGERSPACKAGEDAIRCOOLER', INDETERMINATE)
directevaporativepackagedrotaryaircooler = express_getattr(IfcEvaporativeCoolerTypeEnum, 'DIRECTEVAPORATIVEPACKAGEDROTARYAIRCOOLER', INDETERMINATE)
directevaporativeairwasher = express_getattr(IfcEvaporativeCoolerTypeEnum, 'DIRECTEVAPORATIVEAIRWASHER', INDETERMINATE)
indirectevaporativepackageaircooler = express_getattr(IfcEvaporativeCoolerTypeEnum, 'INDIRECTEVAPORATIVEPACKAGEAIRCOOLER', INDETERMINATE)
indirectevaporativewetcoil = express_getattr(IfcEvaporativeCoolerTypeEnum, 'INDIRECTEVAPORATIVEWETCOIL', INDETERMINATE)
indirectevaporativecoolingtowerorcoilcooler = express_getattr(IfcEvaporativeCoolerTypeEnum, 'INDIRECTEVAPORATIVECOOLINGTOWERORCOILCOOLER', INDETERMINATE)
indirectdirectcombination = express_getattr(IfcEvaporativeCoolerTypeEnum, 'INDIRECTDIRECTCOMBINATION', INDETERMINATE)
userdefined = express_getattr(IfcEvaporativeCoolerTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcEvaporativeCoolerTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcEvaporatorTypeEnum = enum_namespace()
directexpansion = express_getattr(IfcEvaporatorTypeEnum, 'DIRECTEXPANSION', INDETERMINATE)
directexpansionshellandtube = express_getattr(IfcEvaporatorTypeEnum, 'DIRECTEXPANSIONSHELLANDTUBE', INDETERMINATE)
directexpansiontubeintube = express_getattr(IfcEvaporatorTypeEnum, 'DIRECTEXPANSIONTUBEINTUBE', INDETERMINATE)
directexpansionbrazedplate = express_getattr(IfcEvaporatorTypeEnum, 'DIRECTEXPANSIONBRAZEDPLATE', INDETERMINATE)
floodedshellandtube = express_getattr(IfcEvaporatorTypeEnum, 'FLOODEDSHELLANDTUBE', INDETERMINATE)
shellandcoil = express_getattr(IfcEvaporatorTypeEnum, 'SHELLANDCOIL', INDETERMINATE)
userdefined = express_getattr(IfcEvaporatorTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcEvaporatorTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcEventTriggerTypeEnum = enum_namespace()
eventrule = express_getattr(IfcEventTriggerTypeEnum, 'EVENTRULE', INDETERMINATE)
eventmessage = express_getattr(IfcEventTriggerTypeEnum, 'EVENTMESSAGE', INDETERMINATE)
eventtime = express_getattr(IfcEventTriggerTypeEnum, 'EVENTTIME', INDETERMINATE)
eventcomplex = express_getattr(IfcEventTriggerTypeEnum, 'EVENTCOMPLEX', INDETERMINATE)
userdefined = express_getattr(IfcEventTriggerTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcEventTriggerTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcEventTypeEnum = enum_namespace()
startevent = express_getattr(IfcEventTypeEnum, 'STARTEVENT', INDETERMINATE)
endevent = express_getattr(IfcEventTypeEnum, 'ENDEVENT', INDETERMINATE)
intermediateevent = express_getattr(IfcEventTypeEnum, 'INTERMEDIATEEVENT', INDETERMINATE)
userdefined = express_getattr(IfcEventTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcEventTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcExternalSpatialElementTypeEnum = enum_namespace()
external = express_getattr(IfcExternalSpatialElementTypeEnum, 'EXTERNAL', INDETERMINATE)
external_earth = express_getattr(IfcExternalSpatialElementTypeEnum, 'EXTERNAL_EARTH', INDETERMINATE)
external_water = express_getattr(IfcExternalSpatialElementTypeEnum, 'EXTERNAL_WATER', INDETERMINATE)
external_fire = express_getattr(IfcExternalSpatialElementTypeEnum, 'EXTERNAL_FIRE', INDETERMINATE)
userdefined = express_getattr(IfcExternalSpatialElementTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcExternalSpatialElementTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcFacilityPartCommonTypeEnum = enum_namespace()
segment = express_getattr(IfcFacilityPartCommonTypeEnum, 'SEGMENT', INDETERMINATE)
aboveground = express_getattr(IfcFacilityPartCommonTypeEnum, 'ABOVEGROUND', INDETERMINATE)
junction = express_getattr(IfcFacilityPartCommonTypeEnum, 'JUNCTION', INDETERMINATE)
levelcrossing = express_getattr(IfcFacilityPartCommonTypeEnum, 'LEVELCROSSING', INDETERMINATE)
belowground = express_getattr(IfcFacilityPartCommonTypeEnum, 'BELOWGROUND', INDETERMINATE)
substructure = express_getattr(IfcFacilityPartCommonTypeEnum, 'SUBSTRUCTURE', INDETERMINATE)
terminal = express_getattr(IfcFacilityPartCommonTypeEnum, 'TERMINAL', INDETERMINATE)
superstructure = express_getattr(IfcFacilityPartCommonTypeEnum, 'SUPERSTRUCTURE', INDETERMINATE)
userdefined = express_getattr(IfcFacilityPartCommonTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcFacilityPartCommonTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcFacilityUsageEnum = enum_namespace()
lateral = express_getattr(IfcFacilityUsageEnum, 'LATERAL', INDETERMINATE)
region = express_getattr(IfcFacilityUsageEnum, 'REGION', INDETERMINATE)
vertical = express_getattr(IfcFacilityUsageEnum, 'VERTICAL', INDETERMINATE)
longitudinal = express_getattr(IfcFacilityUsageEnum, 'LONGITUDINAL', INDETERMINATE)
userdefined = express_getattr(IfcFacilityUsageEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcFacilityUsageEnum, 'NOTDEFINED', INDETERMINATE)
IfcFanTypeEnum = enum_namespace()
centrifugalforwardcurved = express_getattr(IfcFanTypeEnum, 'CENTRIFUGALFORWARDCURVED', INDETERMINATE)
centrifugalradial = express_getattr(IfcFanTypeEnum, 'CENTRIFUGALRADIAL', INDETERMINATE)
centrifugalbackwardinclinedcurved = express_getattr(IfcFanTypeEnum, 'CENTRIFUGALBACKWARDINCLINEDCURVED', INDETERMINATE)
centrifugalairfoil = express_getattr(IfcFanTypeEnum, 'CENTRIFUGALAIRFOIL', INDETERMINATE)
tubeaxial = express_getattr(IfcFanTypeEnum, 'TUBEAXIAL', INDETERMINATE)
vaneaxial = express_getattr(IfcFanTypeEnum, 'VANEAXIAL', INDETERMINATE)
propelloraxial = express_getattr(IfcFanTypeEnum, 'PROPELLORAXIAL', INDETERMINATE)
userdefined = express_getattr(IfcFanTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcFanTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcFastenerTypeEnum = enum_namespace()
glue = express_getattr(IfcFastenerTypeEnum, 'GLUE', INDETERMINATE)
mortar = express_getattr(IfcFastenerTypeEnum, 'MORTAR', INDETERMINATE)
weld = express_getattr(IfcFastenerTypeEnum, 'WELD', INDETERMINATE)
userdefined = express_getattr(IfcFastenerTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcFastenerTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcFilterTypeEnum = enum_namespace()
airparticlefilter = express_getattr(IfcFilterTypeEnum, 'AIRPARTICLEFILTER', INDETERMINATE)
compressedairfilter = express_getattr(IfcFilterTypeEnum, 'COMPRESSEDAIRFILTER', INDETERMINATE)
odorfilter = express_getattr(IfcFilterTypeEnum, 'ODORFILTER', INDETERMINATE)
oilfilter = express_getattr(IfcFilterTypeEnum, 'OILFILTER', INDETERMINATE)
strainer = express_getattr(IfcFilterTypeEnum, 'STRAINER', INDETERMINATE)
waterfilter = express_getattr(IfcFilterTypeEnum, 'WATERFILTER', INDETERMINATE)
userdefined = express_getattr(IfcFilterTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcFilterTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcFireSuppressionTerminalTypeEnum = enum_namespace()
breechinginlet = express_getattr(IfcFireSuppressionTerminalTypeEnum, 'BREECHINGINLET', INDETERMINATE)
firehydrant = express_getattr(IfcFireSuppressionTerminalTypeEnum, 'FIREHYDRANT', INDETERMINATE)
hosereel = express_getattr(IfcFireSuppressionTerminalTypeEnum, 'HOSEREEL', INDETERMINATE)
sprinkler = express_getattr(IfcFireSuppressionTerminalTypeEnum, 'SPRINKLER', INDETERMINATE)
sprinklerdeflector = express_getattr(IfcFireSuppressionTerminalTypeEnum, 'SPRINKLERDEFLECTOR', INDETERMINATE)
firemonitor = express_getattr(IfcFireSuppressionTerminalTypeEnum, 'FIREMONITOR', INDETERMINATE)
userdefined = express_getattr(IfcFireSuppressionTerminalTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcFireSuppressionTerminalTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcFlowDirectionEnum = enum_namespace()
source = express_getattr(IfcFlowDirectionEnum, 'SOURCE', INDETERMINATE)
sink = express_getattr(IfcFlowDirectionEnum, 'SINK', INDETERMINATE)
sourceandsink = express_getattr(IfcFlowDirectionEnum, 'SOURCEANDSINK', INDETERMINATE)
notdefined = express_getattr(IfcFlowDirectionEnum, 'NOTDEFINED', INDETERMINATE)
IfcFlowInstrumentTypeEnum = enum_namespace()
pressuregauge = express_getattr(IfcFlowInstrumentTypeEnum, 'PRESSUREGAUGE', INDETERMINATE)
thermometer = express_getattr(IfcFlowInstrumentTypeEnum, 'THERMOMETER', INDETERMINATE)
ammeter = express_getattr(IfcFlowInstrumentTypeEnum, 'AMMETER', INDETERMINATE)
frequencymeter = express_getattr(IfcFlowInstrumentTypeEnum, 'FREQUENCYMETER', INDETERMINATE)
powerfactormeter = express_getattr(IfcFlowInstrumentTypeEnum, 'POWERFACTORMETER', INDETERMINATE)
phaseanglemeter = express_getattr(IfcFlowInstrumentTypeEnum, 'PHASEANGLEMETER', INDETERMINATE)
voltmeter_peak = express_getattr(IfcFlowInstrumentTypeEnum, 'VOLTMETER_PEAK', INDETERMINATE)
voltmeter_rms = express_getattr(IfcFlowInstrumentTypeEnum, 'VOLTMETER_RMS', INDETERMINATE)
combined = express_getattr(IfcFlowInstrumentTypeEnum, 'COMBINED', INDETERMINATE)
voltmeter = express_getattr(IfcFlowInstrumentTypeEnum, 'VOLTMETER', INDETERMINATE)
userdefined = express_getattr(IfcFlowInstrumentTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcFlowInstrumentTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcFlowMeterTypeEnum = enum_namespace()
energymeter = express_getattr(IfcFlowMeterTypeEnum, 'ENERGYMETER', INDETERMINATE)
gasmeter = express_getattr(IfcFlowMeterTypeEnum, 'GASMETER', INDETERMINATE)
oilmeter = express_getattr(IfcFlowMeterTypeEnum, 'OILMETER', INDETERMINATE)
watermeter = express_getattr(IfcFlowMeterTypeEnum, 'WATERMETER', INDETERMINATE)
userdefined = express_getattr(IfcFlowMeterTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcFlowMeterTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcFootingTypeEnum = enum_namespace()
caisson_foundation = express_getattr(IfcFootingTypeEnum, 'CAISSON_FOUNDATION', INDETERMINATE)
footing_beam = express_getattr(IfcFootingTypeEnum, 'FOOTING_BEAM', INDETERMINATE)
pad_footing = express_getattr(IfcFootingTypeEnum, 'PAD_FOOTING', INDETERMINATE)
pile_cap = express_getattr(IfcFootingTypeEnum, 'PILE_CAP', INDETERMINATE)
strip_footing = express_getattr(IfcFootingTypeEnum, 'STRIP_FOOTING', INDETERMINATE)
userdefined = express_getattr(IfcFootingTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcFootingTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcFurnitureTypeEnum = enum_namespace()
chair = express_getattr(IfcFurnitureTypeEnum, 'CHAIR', INDETERMINATE)
table = express_getattr(IfcFurnitureTypeEnum, 'TABLE', INDETERMINATE)
desk = express_getattr(IfcFurnitureTypeEnum, 'DESK', INDETERMINATE)
bed = express_getattr(IfcFurnitureTypeEnum, 'BED', INDETERMINATE)
filecabinet = express_getattr(IfcFurnitureTypeEnum, 'FILECABINET', INDETERMINATE)
shelf = express_getattr(IfcFurnitureTypeEnum, 'SHELF', INDETERMINATE)
sofa = express_getattr(IfcFurnitureTypeEnum, 'SOFA', INDETERMINATE)
technicalcabinet = express_getattr(IfcFurnitureTypeEnum, 'TECHNICALCABINET', INDETERMINATE)
userdefined = express_getattr(IfcFurnitureTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcFurnitureTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcGeographicElementTypeEnum = enum_namespace()
terrain = express_getattr(IfcGeographicElementTypeEnum, 'TERRAIN', INDETERMINATE)
soil_boring_point = express_getattr(IfcGeographicElementTypeEnum, 'SOIL_BORING_POINT', INDETERMINATE)
userdefined = express_getattr(IfcGeographicElementTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcGeographicElementTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcGeometricProjectionEnum = enum_namespace()
graph_view = express_getattr(IfcGeometricProjectionEnum, 'GRAPH_VIEW', INDETERMINATE)
sketch_view = express_getattr(IfcGeometricProjectionEnum, 'SKETCH_VIEW', INDETERMINATE)
model_view = express_getattr(IfcGeometricProjectionEnum, 'MODEL_VIEW', INDETERMINATE)
plan_view = express_getattr(IfcGeometricProjectionEnum, 'PLAN_VIEW', INDETERMINATE)
reflected_plan_view = express_getattr(IfcGeometricProjectionEnum, 'REFLECTED_PLAN_VIEW', INDETERMINATE)
section_view = express_getattr(IfcGeometricProjectionEnum, 'SECTION_VIEW', INDETERMINATE)
elevation_view = express_getattr(IfcGeometricProjectionEnum, 'ELEVATION_VIEW', INDETERMINATE)
userdefined = express_getattr(IfcGeometricProjectionEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcGeometricProjectionEnum, 'NOTDEFINED', INDETERMINATE)
IfcGlobalOrLocalEnum = enum_namespace()
global_coords = express_getattr(IfcGlobalOrLocalEnum, 'GLOBAL_COORDS', INDETERMINATE)
local_coords = express_getattr(IfcGlobalOrLocalEnum, 'LOCAL_COORDS', INDETERMINATE)
IfcGridTypeEnum = enum_namespace()
rectangular = express_getattr(IfcGridTypeEnum, 'RECTANGULAR', INDETERMINATE)
radial = express_getattr(IfcGridTypeEnum, 'RADIAL', INDETERMINATE)
triangular = express_getattr(IfcGridTypeEnum, 'TRIANGULAR', INDETERMINATE)
irregular = express_getattr(IfcGridTypeEnum, 'IRREGULAR', INDETERMINATE)
userdefined = express_getattr(IfcGridTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcGridTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcHeatExchangerTypeEnum = enum_namespace()
plate = express_getattr(IfcHeatExchangerTypeEnum, 'PLATE', INDETERMINATE)
shellandtube = express_getattr(IfcHeatExchangerTypeEnum, 'SHELLANDTUBE', INDETERMINATE)
turnoutheating = express_getattr(IfcHeatExchangerTypeEnum, 'TURNOUTHEATING', INDETERMINATE)
userdefined = express_getattr(IfcHeatExchangerTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcHeatExchangerTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcHumidifierTypeEnum = enum_namespace()
steaminjection = express_getattr(IfcHumidifierTypeEnum, 'STEAMINJECTION', INDETERMINATE)
adiabaticairwasher = express_getattr(IfcHumidifierTypeEnum, 'ADIABATICAIRWASHER', INDETERMINATE)
adiabaticpan = express_getattr(IfcHumidifierTypeEnum, 'ADIABATICPAN', INDETERMINATE)
adiabaticwettedelement = express_getattr(IfcHumidifierTypeEnum, 'ADIABATICWETTEDELEMENT', INDETERMINATE)
adiabaticatomizing = express_getattr(IfcHumidifierTypeEnum, 'ADIABATICATOMIZING', INDETERMINATE)
adiabaticultrasonic = express_getattr(IfcHumidifierTypeEnum, 'ADIABATICULTRASONIC', INDETERMINATE)
adiabaticrigidmedia = express_getattr(IfcHumidifierTypeEnum, 'ADIABATICRIGIDMEDIA', INDETERMINATE)
adiabaticcompressedairnozzle = express_getattr(IfcHumidifierTypeEnum, 'ADIABATICCOMPRESSEDAIRNOZZLE', INDETERMINATE)
assistedelectric = express_getattr(IfcHumidifierTypeEnum, 'ASSISTEDELECTRIC', INDETERMINATE)
assistednaturalgas = express_getattr(IfcHumidifierTypeEnum, 'ASSISTEDNATURALGAS', INDETERMINATE)
assistedpropane = express_getattr(IfcHumidifierTypeEnum, 'ASSISTEDPROPANE', INDETERMINATE)
assistedbutane = express_getattr(IfcHumidifierTypeEnum, 'ASSISTEDBUTANE', INDETERMINATE)
assistedsteam = express_getattr(IfcHumidifierTypeEnum, 'ASSISTEDSTEAM', INDETERMINATE)
userdefined = express_getattr(IfcHumidifierTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcHumidifierTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcImpactProtectionDeviceTypeEnum = enum_namespace()
crashcushion = express_getattr(IfcImpactProtectionDeviceTypeEnum, 'CRASHCUSHION', INDETERMINATE)
dampingsystem = express_getattr(IfcImpactProtectionDeviceTypeEnum, 'DAMPINGSYSTEM', INDETERMINATE)
fender = express_getattr(IfcImpactProtectionDeviceTypeEnum, 'FENDER', INDETERMINATE)
bumper = express_getattr(IfcImpactProtectionDeviceTypeEnum, 'BUMPER', INDETERMINATE)
userdefined = express_getattr(IfcImpactProtectionDeviceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcImpactProtectionDeviceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcInterceptorTypeEnum = enum_namespace()
cyclonic = express_getattr(IfcInterceptorTypeEnum, 'CYCLONIC', INDETERMINATE)
grease = express_getattr(IfcInterceptorTypeEnum, 'GREASE', INDETERMINATE)
oil = express_getattr(IfcInterceptorTypeEnum, 'OIL', INDETERMINATE)
petrol = express_getattr(IfcInterceptorTypeEnum, 'PETROL', INDETERMINATE)
userdefined = express_getattr(IfcInterceptorTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcInterceptorTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcInternalOrExternalEnum = enum_namespace()
internal = express_getattr(IfcInternalOrExternalEnum, 'INTERNAL', INDETERMINATE)
external = express_getattr(IfcInternalOrExternalEnum, 'EXTERNAL', INDETERMINATE)
external_earth = express_getattr(IfcInternalOrExternalEnum, 'EXTERNAL_EARTH', INDETERMINATE)
external_water = express_getattr(IfcInternalOrExternalEnum, 'EXTERNAL_WATER', INDETERMINATE)
external_fire = express_getattr(IfcInternalOrExternalEnum, 'EXTERNAL_FIRE', INDETERMINATE)
notdefined = express_getattr(IfcInternalOrExternalEnum, 'NOTDEFINED', INDETERMINATE)
IfcInventoryTypeEnum = enum_namespace()
assetinventory = express_getattr(IfcInventoryTypeEnum, 'ASSETINVENTORY', INDETERMINATE)
spaceinventory = express_getattr(IfcInventoryTypeEnum, 'SPACEINVENTORY', INDETERMINATE)
furnitureinventory = express_getattr(IfcInventoryTypeEnum, 'FURNITUREINVENTORY', INDETERMINATE)
userdefined = express_getattr(IfcInventoryTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcInventoryTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcJunctionBoxTypeEnum = enum_namespace()
data = express_getattr(IfcJunctionBoxTypeEnum, 'DATA', INDETERMINATE)
power = express_getattr(IfcJunctionBoxTypeEnum, 'POWER', INDETERMINATE)
userdefined = express_getattr(IfcJunctionBoxTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcJunctionBoxTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcKnotType = enum_namespace()
uniform_knots = express_getattr(IfcKnotType, 'UNIFORM_KNOTS', INDETERMINATE)
quasi_uniform_knots = express_getattr(IfcKnotType, 'QUASI_UNIFORM_KNOTS', INDETERMINATE)
piecewise_bezier_knots = express_getattr(IfcKnotType, 'PIECEWISE_BEZIER_KNOTS', INDETERMINATE)
unspecified = express_getattr(IfcKnotType, 'UNSPECIFIED', INDETERMINATE)
IfcLaborResourceTypeEnum = enum_namespace()
administration = express_getattr(IfcLaborResourceTypeEnum, 'ADMINISTRATION', INDETERMINATE)
carpentry = express_getattr(IfcLaborResourceTypeEnum, 'CARPENTRY', INDETERMINATE)
cleaning = express_getattr(IfcLaborResourceTypeEnum, 'CLEANING', INDETERMINATE)
concrete = express_getattr(IfcLaborResourceTypeEnum, 'CONCRETE', INDETERMINATE)
drywall = express_getattr(IfcLaborResourceTypeEnum, 'DRYWALL', INDETERMINATE)
electric = express_getattr(IfcLaborResourceTypeEnum, 'ELECTRIC', INDETERMINATE)
finishing = express_getattr(IfcLaborResourceTypeEnum, 'FINISHING', INDETERMINATE)
flooring = express_getattr(IfcLaborResourceTypeEnum, 'FLOORING', INDETERMINATE)
general = express_getattr(IfcLaborResourceTypeEnum, 'GENERAL', INDETERMINATE)
hvac = express_getattr(IfcLaborResourceTypeEnum, 'HVAC', INDETERMINATE)
landscaping = express_getattr(IfcLaborResourceTypeEnum, 'LANDSCAPING', INDETERMINATE)
masonry = express_getattr(IfcLaborResourceTypeEnum, 'MASONRY', INDETERMINATE)
painting = express_getattr(IfcLaborResourceTypeEnum, 'PAINTING', INDETERMINATE)
paving = express_getattr(IfcLaborResourceTypeEnum, 'PAVING', INDETERMINATE)
plumbing = express_getattr(IfcLaborResourceTypeEnum, 'PLUMBING', INDETERMINATE)
roofing = express_getattr(IfcLaborResourceTypeEnum, 'ROOFING', INDETERMINATE)
sitegrading = express_getattr(IfcLaborResourceTypeEnum, 'SITEGRADING', INDETERMINATE)
steelwork = express_getattr(IfcLaborResourceTypeEnum, 'STEELWORK', INDETERMINATE)
surveying = express_getattr(IfcLaborResourceTypeEnum, 'SURVEYING', INDETERMINATE)
userdefined = express_getattr(IfcLaborResourceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcLaborResourceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcLampTypeEnum = enum_namespace()
compactfluorescent = express_getattr(IfcLampTypeEnum, 'COMPACTFLUORESCENT', INDETERMINATE)
fluorescent = express_getattr(IfcLampTypeEnum, 'FLUORESCENT', INDETERMINATE)
halogen = express_getattr(IfcLampTypeEnum, 'HALOGEN', INDETERMINATE)
highpressuremercury = express_getattr(IfcLampTypeEnum, 'HIGHPRESSUREMERCURY', INDETERMINATE)
highpressuresodium = express_getattr(IfcLampTypeEnum, 'HIGHPRESSURESODIUM', INDETERMINATE)
led = express_getattr(IfcLampTypeEnum, 'LED', INDETERMINATE)
metalhalide = express_getattr(IfcLampTypeEnum, 'METALHALIDE', INDETERMINATE)
oled = express_getattr(IfcLampTypeEnum, 'OLED', INDETERMINATE)
tungstenfilament = express_getattr(IfcLampTypeEnum, 'TUNGSTENFILAMENT', INDETERMINATE)
userdefined = express_getattr(IfcLampTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcLampTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcLayerSetDirectionEnum = enum_namespace()
axis1 = express_getattr(IfcLayerSetDirectionEnum, 'AXIS1', INDETERMINATE)
axis2 = express_getattr(IfcLayerSetDirectionEnum, 'AXIS2', INDETERMINATE)
axis3 = express_getattr(IfcLayerSetDirectionEnum, 'AXIS3', INDETERMINATE)
IfcLightDistributionCurveEnum = enum_namespace()
type_a = express_getattr(IfcLightDistributionCurveEnum, 'TYPE_A', INDETERMINATE)
type_b = express_getattr(IfcLightDistributionCurveEnum, 'TYPE_B', INDETERMINATE)
type_c = express_getattr(IfcLightDistributionCurveEnum, 'TYPE_C', INDETERMINATE)
notdefined = express_getattr(IfcLightDistributionCurveEnum, 'NOTDEFINED', INDETERMINATE)
IfcLightEmissionSourceEnum = enum_namespace()
compactfluorescent = express_getattr(IfcLightEmissionSourceEnum, 'COMPACTFLUORESCENT', INDETERMINATE)
fluorescent = express_getattr(IfcLightEmissionSourceEnum, 'FLUORESCENT', INDETERMINATE)
highpressuremercury = express_getattr(IfcLightEmissionSourceEnum, 'HIGHPRESSUREMERCURY', INDETERMINATE)
highpressuresodium = express_getattr(IfcLightEmissionSourceEnum, 'HIGHPRESSURESODIUM', INDETERMINATE)
lightemittingdiode = express_getattr(IfcLightEmissionSourceEnum, 'LIGHTEMITTINGDIODE', INDETERMINATE)
lowpressuresodium = express_getattr(IfcLightEmissionSourceEnum, 'LOWPRESSURESODIUM', INDETERMINATE)
lowvoltagehalogen = express_getattr(IfcLightEmissionSourceEnum, 'LOWVOLTAGEHALOGEN', INDETERMINATE)
mainvoltagehalogen = express_getattr(IfcLightEmissionSourceEnum, 'MAINVOLTAGEHALOGEN', INDETERMINATE)
metalhalide = express_getattr(IfcLightEmissionSourceEnum, 'METALHALIDE', INDETERMINATE)
tungstenfilament = express_getattr(IfcLightEmissionSourceEnum, 'TUNGSTENFILAMENT', INDETERMINATE)
notdefined = express_getattr(IfcLightEmissionSourceEnum, 'NOTDEFINED', INDETERMINATE)
IfcLightFixtureTypeEnum = enum_namespace()
pointsource = express_getattr(IfcLightFixtureTypeEnum, 'POINTSOURCE', INDETERMINATE)
directionsource = express_getattr(IfcLightFixtureTypeEnum, 'DIRECTIONSOURCE', INDETERMINATE)
securitylighting = express_getattr(IfcLightFixtureTypeEnum, 'SECURITYLIGHTING', INDETERMINATE)
userdefined = express_getattr(IfcLightFixtureTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcLightFixtureTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcLiquidTerminalTypeEnum = enum_namespace()
loadingarm = express_getattr(IfcLiquidTerminalTypeEnum, 'LOADINGARM', INDETERMINATE)
hosereel = express_getattr(IfcLiquidTerminalTypeEnum, 'HOSEREEL', INDETERMINATE)
userdefined = express_getattr(IfcLiquidTerminalTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcLiquidTerminalTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcLoadGroupTypeEnum = enum_namespace()
load_group = express_getattr(IfcLoadGroupTypeEnum, 'LOAD_GROUP', INDETERMINATE)
load_case = express_getattr(IfcLoadGroupTypeEnum, 'LOAD_CASE', INDETERMINATE)
load_combination = express_getattr(IfcLoadGroupTypeEnum, 'LOAD_COMBINATION', INDETERMINATE)
userdefined = express_getattr(IfcLoadGroupTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcLoadGroupTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcLogicalOperatorEnum = enum_namespace()
logicaland = express_getattr(IfcLogicalOperatorEnum, 'LOGICALAND', INDETERMINATE)
logicalor = express_getattr(IfcLogicalOperatorEnum, 'LOGICALOR', INDETERMINATE)
logicalxor = express_getattr(IfcLogicalOperatorEnum, 'LOGICALXOR', INDETERMINATE)
logicalnotand = express_getattr(IfcLogicalOperatorEnum, 'LOGICALNOTAND', INDETERMINATE)
logicalnotor = express_getattr(IfcLogicalOperatorEnum, 'LOGICALNOTOR', INDETERMINATE)
IfcMarineFacilityTypeEnum = enum_namespace()
canal = express_getattr(IfcMarineFacilityTypeEnum, 'CANAL', INDETERMINATE)
waterwayshiplift = express_getattr(IfcMarineFacilityTypeEnum, 'WATERWAYSHIPLIFT', INDETERMINATE)
revetment = express_getattr(IfcMarineFacilityTypeEnum, 'REVETMENT', INDETERMINATE)
launchrecovery = express_getattr(IfcMarineFacilityTypeEnum, 'LAUNCHRECOVERY', INDETERMINATE)
marinedefence = express_getattr(IfcMarineFacilityTypeEnum, 'MARINEDEFENCE', INDETERMINATE)
hydrolift = express_getattr(IfcMarineFacilityTypeEnum, 'HYDROLIFT', INDETERMINATE)
shipyard = express_getattr(IfcMarineFacilityTypeEnum, 'SHIPYARD', INDETERMINATE)
shiplift = express_getattr(IfcMarineFacilityTypeEnum, 'SHIPLIFT', INDETERMINATE)
port = express_getattr(IfcMarineFacilityTypeEnum, 'PORT', INDETERMINATE)
quay = express_getattr(IfcMarineFacilityTypeEnum, 'QUAY', INDETERMINATE)
floatingdock = express_getattr(IfcMarineFacilityTypeEnum, 'FLOATINGDOCK', INDETERMINATE)
navigationalchannel = express_getattr(IfcMarineFacilityTypeEnum, 'NAVIGATIONALCHANNEL', INDETERMINATE)
breakwater = express_getattr(IfcMarineFacilityTypeEnum, 'BREAKWATER', INDETERMINATE)
drydock = express_getattr(IfcMarineFacilityTypeEnum, 'DRYDOCK', INDETERMINATE)
jetty = express_getattr(IfcMarineFacilityTypeEnum, 'JETTY', INDETERMINATE)
shiplock = express_getattr(IfcMarineFacilityTypeEnum, 'SHIPLOCK', INDETERMINATE)
barrierbeach = express_getattr(IfcMarineFacilityTypeEnum, 'BARRIERBEACH', INDETERMINATE)
slipway = express_getattr(IfcMarineFacilityTypeEnum, 'SLIPWAY', INDETERMINATE)
waterway = express_getattr(IfcMarineFacilityTypeEnum, 'WATERWAY', INDETERMINATE)
userdefined = express_getattr(IfcMarineFacilityTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcMarineFacilityTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcMarinePartTypeEnum = enum_namespace()
crest = express_getattr(IfcMarinePartTypeEnum, 'CREST', INDETERMINATE)
manufacturing = express_getattr(IfcMarinePartTypeEnum, 'MANUFACTURING', INDETERMINATE)
lowwaterline = express_getattr(IfcMarinePartTypeEnum, 'LOWWATERLINE', INDETERMINATE)
core = express_getattr(IfcMarinePartTypeEnum, 'CORE', INDETERMINATE)
waterfield = express_getattr(IfcMarinePartTypeEnum, 'WATERFIELD', INDETERMINATE)
cill_level = express_getattr(IfcMarinePartTypeEnum, 'CILL_LEVEL', INDETERMINATE)
berthingstructure = express_getattr(IfcMarinePartTypeEnum, 'BERTHINGSTRUCTURE', INDETERMINATE)
copelevel = express_getattr(IfcMarinePartTypeEnum, 'COPELEVEL', INDETERMINATE)
chamber = express_getattr(IfcMarinePartTypeEnum, 'CHAMBER', INDETERMINATE)
storagearea = express_getattr(IfcMarinePartTypeEnum, 'STORAGEAREA', INDETERMINATE)
approachchannel = express_getattr(IfcMarinePartTypeEnum, 'APPROACHCHANNEL', INDETERMINATE)
vehicleservicing = express_getattr(IfcMarinePartTypeEnum, 'VEHICLESERVICING', INDETERMINATE)
shiptransfer = express_getattr(IfcMarinePartTypeEnum, 'SHIPTRANSFER', INDETERMINATE)
gatehead = express_getattr(IfcMarinePartTypeEnum, 'GATEHEAD', INDETERMINATE)
gudingstructure = express_getattr(IfcMarinePartTypeEnum, 'GUDINGSTRUCTURE', INDETERMINATE)
belowwaterline = express_getattr(IfcMarinePartTypeEnum, 'BELOWWATERLINE', INDETERMINATE)
weatherside = express_getattr(IfcMarinePartTypeEnum, 'WEATHERSIDE', INDETERMINATE)
landfield = express_getattr(IfcMarinePartTypeEnum, 'LANDFIELD', INDETERMINATE)
protection = express_getattr(IfcMarinePartTypeEnum, 'PROTECTION', INDETERMINATE)
leewardside = express_getattr(IfcMarinePartTypeEnum, 'LEEWARDSIDE', INDETERMINATE)
abovewaterline = express_getattr(IfcMarinePartTypeEnum, 'ABOVEWATERLINE', INDETERMINATE)
anchorage = express_getattr(IfcMarinePartTypeEnum, 'ANCHORAGE', INDETERMINATE)
navigationalarea = express_getattr(IfcMarinePartTypeEnum, 'NAVIGATIONALAREA', INDETERMINATE)
highwaterline = express_getattr(IfcMarinePartTypeEnum, 'HIGHWATERLINE', INDETERMINATE)
userdefined = express_getattr(IfcMarinePartTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcMarinePartTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcMechanicalFastenerTypeEnum = enum_namespace()
anchorbolt = express_getattr(IfcMechanicalFastenerTypeEnum, 'ANCHORBOLT', INDETERMINATE)
bolt = express_getattr(IfcMechanicalFastenerTypeEnum, 'BOLT', INDETERMINATE)
dowel = express_getattr(IfcMechanicalFastenerTypeEnum, 'DOWEL', INDETERMINATE)
nail = express_getattr(IfcMechanicalFastenerTypeEnum, 'NAIL', INDETERMINATE)
nailplate = express_getattr(IfcMechanicalFastenerTypeEnum, 'NAILPLATE', INDETERMINATE)
rivet = express_getattr(IfcMechanicalFastenerTypeEnum, 'RIVET', INDETERMINATE)
screw = express_getattr(IfcMechanicalFastenerTypeEnum, 'SCREW', INDETERMINATE)
shearconnector = express_getattr(IfcMechanicalFastenerTypeEnum, 'SHEARCONNECTOR', INDETERMINATE)
staple = express_getattr(IfcMechanicalFastenerTypeEnum, 'STAPLE', INDETERMINATE)
studshearconnector = express_getattr(IfcMechanicalFastenerTypeEnum, 'STUDSHEARCONNECTOR', INDETERMINATE)
coupler = express_getattr(IfcMechanicalFastenerTypeEnum, 'COUPLER', INDETERMINATE)
railjoint = express_getattr(IfcMechanicalFastenerTypeEnum, 'RAILJOINT', INDETERMINATE)
railfastening = express_getattr(IfcMechanicalFastenerTypeEnum, 'RAILFASTENING', INDETERMINATE)
chain = express_getattr(IfcMechanicalFastenerTypeEnum, 'CHAIN', INDETERMINATE)
rope = express_getattr(IfcMechanicalFastenerTypeEnum, 'ROPE', INDETERMINATE)
userdefined = express_getattr(IfcMechanicalFastenerTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcMechanicalFastenerTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcMedicalDeviceTypeEnum = enum_namespace()
airstation = express_getattr(IfcMedicalDeviceTypeEnum, 'AIRSTATION', INDETERMINATE)
feedairunit = express_getattr(IfcMedicalDeviceTypeEnum, 'FEEDAIRUNIT', INDETERMINATE)
oxygengenerator = express_getattr(IfcMedicalDeviceTypeEnum, 'OXYGENGENERATOR', INDETERMINATE)
oxygenplant = express_getattr(IfcMedicalDeviceTypeEnum, 'OXYGENPLANT', INDETERMINATE)
vacuumstation = express_getattr(IfcMedicalDeviceTypeEnum, 'VACUUMSTATION', INDETERMINATE)
userdefined = express_getattr(IfcMedicalDeviceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcMedicalDeviceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcMemberTypeEnum = enum_namespace()
brace = express_getattr(IfcMemberTypeEnum, 'BRACE', INDETERMINATE)
chord = express_getattr(IfcMemberTypeEnum, 'CHORD', INDETERMINATE)
collar = express_getattr(IfcMemberTypeEnum, 'COLLAR', INDETERMINATE)
member = express_getattr(IfcMemberTypeEnum, 'MEMBER', INDETERMINATE)
mullion = express_getattr(IfcMemberTypeEnum, 'MULLION', INDETERMINATE)
plate = express_getattr(IfcMemberTypeEnum, 'PLATE', INDETERMINATE)
post = express_getattr(IfcMemberTypeEnum, 'POST', INDETERMINATE)
purlin = express_getattr(IfcMemberTypeEnum, 'PURLIN', INDETERMINATE)
rafter = express_getattr(IfcMemberTypeEnum, 'RAFTER', INDETERMINATE)
stringer = express_getattr(IfcMemberTypeEnum, 'STRINGER', INDETERMINATE)
strut = express_getattr(IfcMemberTypeEnum, 'STRUT', INDETERMINATE)
stud = express_getattr(IfcMemberTypeEnum, 'STUD', INDETERMINATE)
stiffening_rib = express_getattr(IfcMemberTypeEnum, 'STIFFENING_RIB', INDETERMINATE)
arch_segment = express_getattr(IfcMemberTypeEnum, 'ARCH_SEGMENT', INDETERMINATE)
suspension_cable = express_getattr(IfcMemberTypeEnum, 'SUSPENSION_CABLE', INDETERMINATE)
suspender = express_getattr(IfcMemberTypeEnum, 'SUSPENDER', INDETERMINATE)
stay_cable = express_getattr(IfcMemberTypeEnum, 'STAY_CABLE', INDETERMINATE)
structuralcable = express_getattr(IfcMemberTypeEnum, 'STRUCTURALCABLE', INDETERMINATE)
tiebar = express_getattr(IfcMemberTypeEnum, 'TIEBAR', INDETERMINATE)
userdefined = express_getattr(IfcMemberTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcMemberTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcMobileTelecommunicationsApplianceTypeEnum = enum_namespace()
e_utran_node_b = express_getattr(IfcMobileTelecommunicationsApplianceTypeEnum, 'E_UTRAN_NODE_B', INDETERMINATE)
remoteradiounit = express_getattr(IfcMobileTelecommunicationsApplianceTypeEnum, 'REMOTERADIOUNIT', INDETERMINATE)
accesspoint = express_getattr(IfcMobileTelecommunicationsApplianceTypeEnum, 'ACCESSPOINT', INDETERMINATE)
basetransceiverstation = express_getattr(IfcMobileTelecommunicationsApplianceTypeEnum, 'BASETRANSCEIVERSTATION', INDETERMINATE)
remoteunit = express_getattr(IfcMobileTelecommunicationsApplianceTypeEnum, 'REMOTEUNIT', INDETERMINATE)
basebandunit = express_getattr(IfcMobileTelecommunicationsApplianceTypeEnum, 'BASEBANDUNIT', INDETERMINATE)
masterunit = express_getattr(IfcMobileTelecommunicationsApplianceTypeEnum, 'MASTERUNIT', INDETERMINATE)
gateway_gprs_support_node = express_getattr(IfcMobileTelecommunicationsApplianceTypeEnum, 'GATEWAY_GPRS_SUPPORT_NODE', INDETERMINATE)
subscriberserver = express_getattr(IfcMobileTelecommunicationsApplianceTypeEnum, 'SUBSCRIBERSERVER', INDETERMINATE)
mobileswitchingcenter = express_getattr(IfcMobileTelecommunicationsApplianceTypeEnum, 'MOBILESWITCHINGCENTER', INDETERMINATE)
mscserver = express_getattr(IfcMobileTelecommunicationsApplianceTypeEnum, 'MSCSERVER', INDETERMINATE)
packetcontrolunit = express_getattr(IfcMobileTelecommunicationsApplianceTypeEnum, 'PACKETCONTROLUNIT', INDETERMINATE)
service_gprs_support_node = express_getattr(IfcMobileTelecommunicationsApplianceTypeEnum, 'SERVICE_GPRS_SUPPORT_NODE', INDETERMINATE)
userdefined = express_getattr(IfcMobileTelecommunicationsApplianceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcMobileTelecommunicationsApplianceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcMooringDeviceTypeEnum = enum_namespace()
linetensioner = express_getattr(IfcMooringDeviceTypeEnum, 'LINETENSIONER', INDETERMINATE)
magneticdevice = express_getattr(IfcMooringDeviceTypeEnum, 'MAGNETICDEVICE', INDETERMINATE)
mooringhooks = express_getattr(IfcMooringDeviceTypeEnum, 'MOORINGHOOKS', INDETERMINATE)
vacuumdevice = express_getattr(IfcMooringDeviceTypeEnum, 'VACUUMDEVICE', INDETERMINATE)
bollard = express_getattr(IfcMooringDeviceTypeEnum, 'BOLLARD', INDETERMINATE)
userdefined = express_getattr(IfcMooringDeviceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcMooringDeviceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcMotorConnectionTypeEnum = enum_namespace()
beltdrive = express_getattr(IfcMotorConnectionTypeEnum, 'BELTDRIVE', INDETERMINATE)
coupling = express_getattr(IfcMotorConnectionTypeEnum, 'COUPLING', INDETERMINATE)
directdrive = express_getattr(IfcMotorConnectionTypeEnum, 'DIRECTDRIVE', INDETERMINATE)
userdefined = express_getattr(IfcMotorConnectionTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcMotorConnectionTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcNavigationElementTypeEnum = enum_namespace()
beacon = express_getattr(IfcNavigationElementTypeEnum, 'BEACON', INDETERMINATE)
buoy = express_getattr(IfcNavigationElementTypeEnum, 'BUOY', INDETERMINATE)
userdefined = express_getattr(IfcNavigationElementTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcNavigationElementTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcObjectTypeEnum = enum_namespace()
product = express_getattr(IfcObjectTypeEnum, 'PRODUCT', INDETERMINATE)
process = express_getattr(IfcObjectTypeEnum, 'PROCESS', INDETERMINATE)
control = express_getattr(IfcObjectTypeEnum, 'CONTROL', INDETERMINATE)
resource = express_getattr(IfcObjectTypeEnum, 'RESOURCE', INDETERMINATE)
actor = express_getattr(IfcObjectTypeEnum, 'ACTOR', INDETERMINATE)
group = express_getattr(IfcObjectTypeEnum, 'GROUP', INDETERMINATE)
project = express_getattr(IfcObjectTypeEnum, 'PROJECT', INDETERMINATE)
notdefined = express_getattr(IfcObjectTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcObjectiveEnum = enum_namespace()
codecompliance = express_getattr(IfcObjectiveEnum, 'CODECOMPLIANCE', INDETERMINATE)
codewaiver = express_getattr(IfcObjectiveEnum, 'CODEWAIVER', INDETERMINATE)
designintent = express_getattr(IfcObjectiveEnum, 'DESIGNINTENT', INDETERMINATE)
external = express_getattr(IfcObjectiveEnum, 'EXTERNAL', INDETERMINATE)
healthandsafety = express_getattr(IfcObjectiveEnum, 'HEALTHANDSAFETY', INDETERMINATE)
mergeconflict = express_getattr(IfcObjectiveEnum, 'MERGECONFLICT', INDETERMINATE)
modelview = express_getattr(IfcObjectiveEnum, 'MODELVIEW', INDETERMINATE)
parameter = express_getattr(IfcObjectiveEnum, 'PARAMETER', INDETERMINATE)
requirement = express_getattr(IfcObjectiveEnum, 'REQUIREMENT', INDETERMINATE)
specification = express_getattr(IfcObjectiveEnum, 'SPECIFICATION', INDETERMINATE)
triggercondition = express_getattr(IfcObjectiveEnum, 'TRIGGERCONDITION', INDETERMINATE)
userdefined = express_getattr(IfcObjectiveEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcObjectiveEnum, 'NOTDEFINED', INDETERMINATE)
IfcOccupantTypeEnum = enum_namespace()
assignee = express_getattr(IfcOccupantTypeEnum, 'ASSIGNEE', INDETERMINATE)
assignor = express_getattr(IfcOccupantTypeEnum, 'ASSIGNOR', INDETERMINATE)
lessee = express_getattr(IfcOccupantTypeEnum, 'LESSEE', INDETERMINATE)
lessor = express_getattr(IfcOccupantTypeEnum, 'LESSOR', INDETERMINATE)
lettingagent = express_getattr(IfcOccupantTypeEnum, 'LETTINGAGENT', INDETERMINATE)
owner = express_getattr(IfcOccupantTypeEnum, 'OWNER', INDETERMINATE)
tenant = express_getattr(IfcOccupantTypeEnum, 'TENANT', INDETERMINATE)
userdefined = express_getattr(IfcOccupantTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcOccupantTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcOpeningElementTypeEnum = enum_namespace()
opening = express_getattr(IfcOpeningElementTypeEnum, 'OPENING', INDETERMINATE)
recess = express_getattr(IfcOpeningElementTypeEnum, 'RECESS', INDETERMINATE)
userdefined = express_getattr(IfcOpeningElementTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcOpeningElementTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcOutletTypeEnum = enum_namespace()
audiovisualoutlet = express_getattr(IfcOutletTypeEnum, 'AUDIOVISUALOUTLET', INDETERMINATE)
communicationsoutlet = express_getattr(IfcOutletTypeEnum, 'COMMUNICATIONSOUTLET', INDETERMINATE)
poweroutlet = express_getattr(IfcOutletTypeEnum, 'POWEROUTLET', INDETERMINATE)
dataoutlet = express_getattr(IfcOutletTypeEnum, 'DATAOUTLET', INDETERMINATE)
telephoneoutlet = express_getattr(IfcOutletTypeEnum, 'TELEPHONEOUTLET', INDETERMINATE)
userdefined = express_getattr(IfcOutletTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcOutletTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcPavementTypeEnum = enum_namespace()
flexible = express_getattr(IfcPavementTypeEnum, 'FLEXIBLE', INDETERMINATE)
rigid = express_getattr(IfcPavementTypeEnum, 'RIGID', INDETERMINATE)
userdefined = express_getattr(IfcPavementTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcPavementTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcPerformanceHistoryTypeEnum = enum_namespace()
userdefined = express_getattr(IfcPerformanceHistoryTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcPerformanceHistoryTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcPermeableCoveringOperationEnum = enum_namespace()
grill = express_getattr(IfcPermeableCoveringOperationEnum, 'GRILL', INDETERMINATE)
louver = express_getattr(IfcPermeableCoveringOperationEnum, 'LOUVER', INDETERMINATE)
screen = express_getattr(IfcPermeableCoveringOperationEnum, 'SCREEN', INDETERMINATE)
userdefined = express_getattr(IfcPermeableCoveringOperationEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcPermeableCoveringOperationEnum, 'NOTDEFINED', INDETERMINATE)
IfcPermitTypeEnum = enum_namespace()
access = express_getattr(IfcPermitTypeEnum, 'ACCESS', INDETERMINATE)
building = express_getattr(IfcPermitTypeEnum, 'BUILDING', INDETERMINATE)
work = express_getattr(IfcPermitTypeEnum, 'WORK', INDETERMINATE)
userdefined = express_getattr(IfcPermitTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcPermitTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcPhysicalOrVirtualEnum = enum_namespace()
physical = express_getattr(IfcPhysicalOrVirtualEnum, 'PHYSICAL', INDETERMINATE)
virtual = express_getattr(IfcPhysicalOrVirtualEnum, 'VIRTUAL', INDETERMINATE)
notdefined = express_getattr(IfcPhysicalOrVirtualEnum, 'NOTDEFINED', INDETERMINATE)
IfcPileConstructionEnum = enum_namespace()
cast_in_place = express_getattr(IfcPileConstructionEnum, 'CAST_IN_PLACE', INDETERMINATE)
composite = express_getattr(IfcPileConstructionEnum, 'COMPOSITE', INDETERMINATE)
precast_concrete = express_getattr(IfcPileConstructionEnum, 'PRECAST_CONCRETE', INDETERMINATE)
prefab_steel = express_getattr(IfcPileConstructionEnum, 'PREFAB_STEEL', INDETERMINATE)
userdefined = express_getattr(IfcPileConstructionEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcPileConstructionEnum, 'NOTDEFINED', INDETERMINATE)
IfcPileTypeEnum = enum_namespace()
bored = express_getattr(IfcPileTypeEnum, 'BORED', INDETERMINATE)
driven = express_getattr(IfcPileTypeEnum, 'DRIVEN', INDETERMINATE)
jetgrouting = express_getattr(IfcPileTypeEnum, 'JETGROUTING', INDETERMINATE)
cohesion = express_getattr(IfcPileTypeEnum, 'COHESION', INDETERMINATE)
friction = express_getattr(IfcPileTypeEnum, 'FRICTION', INDETERMINATE)
support = express_getattr(IfcPileTypeEnum, 'SUPPORT', INDETERMINATE)
userdefined = express_getattr(IfcPileTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcPileTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcPipeFittingTypeEnum = enum_namespace()
bend = express_getattr(IfcPipeFittingTypeEnum, 'BEND', INDETERMINATE)
connector = express_getattr(IfcPipeFittingTypeEnum, 'CONNECTOR', INDETERMINATE)
entry = express_getattr(IfcPipeFittingTypeEnum, 'ENTRY', INDETERMINATE)
exit = express_getattr(IfcPipeFittingTypeEnum, 'EXIT', INDETERMINATE)
junction = express_getattr(IfcPipeFittingTypeEnum, 'JUNCTION', INDETERMINATE)
obstruction = express_getattr(IfcPipeFittingTypeEnum, 'OBSTRUCTION', INDETERMINATE)
transition = express_getattr(IfcPipeFittingTypeEnum, 'TRANSITION', INDETERMINATE)
userdefined = express_getattr(IfcPipeFittingTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcPipeFittingTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcPipeSegmentTypeEnum = enum_namespace()
culvert = express_getattr(IfcPipeSegmentTypeEnum, 'CULVERT', INDETERMINATE)
flexiblesegment = express_getattr(IfcPipeSegmentTypeEnum, 'FLEXIBLESEGMENT', INDETERMINATE)
rigidsegment = express_getattr(IfcPipeSegmentTypeEnum, 'RIGIDSEGMENT', INDETERMINATE)
gutter = express_getattr(IfcPipeSegmentTypeEnum, 'GUTTER', INDETERMINATE)
spool = express_getattr(IfcPipeSegmentTypeEnum, 'SPOOL', INDETERMINATE)
userdefined = express_getattr(IfcPipeSegmentTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcPipeSegmentTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcPlateTypeEnum = enum_namespace()
curtain_panel = express_getattr(IfcPlateTypeEnum, 'CURTAIN_PANEL', INDETERMINATE)
sheet = express_getattr(IfcPlateTypeEnum, 'SHEET', INDETERMINATE)
flange_plate = express_getattr(IfcPlateTypeEnum, 'FLANGE_PLATE', INDETERMINATE)
web_plate = express_getattr(IfcPlateTypeEnum, 'WEB_PLATE', INDETERMINATE)
stiffener_plate = express_getattr(IfcPlateTypeEnum, 'STIFFENER_PLATE', INDETERMINATE)
gusset_plate = express_getattr(IfcPlateTypeEnum, 'GUSSET_PLATE', INDETERMINATE)
cover_plate = express_getattr(IfcPlateTypeEnum, 'COVER_PLATE', INDETERMINATE)
splice_plate = express_getattr(IfcPlateTypeEnum, 'SPLICE_PLATE', INDETERMINATE)
base_plate = express_getattr(IfcPlateTypeEnum, 'BASE_PLATE', INDETERMINATE)
userdefined = express_getattr(IfcPlateTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcPlateTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcPreferredSurfaceCurveRepresentation = enum_namespace()
curve3d = express_getattr(IfcPreferredSurfaceCurveRepresentation, 'CURVE3D', INDETERMINATE)
pcurve_s1 = express_getattr(IfcPreferredSurfaceCurveRepresentation, 'PCURVE_S1', INDETERMINATE)
pcurve_s2 = express_getattr(IfcPreferredSurfaceCurveRepresentation, 'PCURVE_S2', INDETERMINATE)
IfcProcedureTypeEnum = enum_namespace()
advice_caution = express_getattr(IfcProcedureTypeEnum, 'ADVICE_CAUTION', INDETERMINATE)
advice_note = express_getattr(IfcProcedureTypeEnum, 'ADVICE_NOTE', INDETERMINATE)
advice_warning = express_getattr(IfcProcedureTypeEnum, 'ADVICE_WARNING', INDETERMINATE)
calibration = express_getattr(IfcProcedureTypeEnum, 'CALIBRATION', INDETERMINATE)
diagnostic = express_getattr(IfcProcedureTypeEnum, 'DIAGNOSTIC', INDETERMINATE)
shutdown = express_getattr(IfcProcedureTypeEnum, 'SHUTDOWN', INDETERMINATE)
startup = express_getattr(IfcProcedureTypeEnum, 'STARTUP', INDETERMINATE)
userdefined = express_getattr(IfcProcedureTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcProcedureTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcProfileTypeEnum = enum_namespace()
curve = express_getattr(IfcProfileTypeEnum, 'CURVE', INDETERMINATE)
area = express_getattr(IfcProfileTypeEnum, 'AREA', INDETERMINATE)
IfcProjectOrderTypeEnum = enum_namespace()
changeorder = express_getattr(IfcProjectOrderTypeEnum, 'CHANGEORDER', INDETERMINATE)
maintenanceworkorder = express_getattr(IfcProjectOrderTypeEnum, 'MAINTENANCEWORKORDER', INDETERMINATE)
moveorder = express_getattr(IfcProjectOrderTypeEnum, 'MOVEORDER', INDETERMINATE)
purchaseorder = express_getattr(IfcProjectOrderTypeEnum, 'PURCHASEORDER', INDETERMINATE)
workorder = express_getattr(IfcProjectOrderTypeEnum, 'WORKORDER', INDETERMINATE)
userdefined = express_getattr(IfcProjectOrderTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcProjectOrderTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcProjectedOrTrueLengthEnum = enum_namespace()
projected_length = express_getattr(IfcProjectedOrTrueLengthEnum, 'PROJECTED_LENGTH', INDETERMINATE)
true_length = express_getattr(IfcProjectedOrTrueLengthEnum, 'TRUE_LENGTH', INDETERMINATE)
IfcProjectionElementTypeEnum = enum_namespace()
blister = express_getattr(IfcProjectionElementTypeEnum, 'BLISTER', INDETERMINATE)
deviator = express_getattr(IfcProjectionElementTypeEnum, 'DEVIATOR', INDETERMINATE)
userdefined = express_getattr(IfcProjectionElementTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcProjectionElementTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcPropertySetTemplateTypeEnum = enum_namespace()
pset_typedrivenonly = express_getattr(IfcPropertySetTemplateTypeEnum, 'PSET_TYPEDRIVENONLY', INDETERMINATE)
pset_typedrivenoverride = express_getattr(IfcPropertySetTemplateTypeEnum, 'PSET_TYPEDRIVENOVERRIDE', INDETERMINATE)
pset_occurrencedriven = express_getattr(IfcPropertySetTemplateTypeEnum, 'PSET_OCCURRENCEDRIVEN', INDETERMINATE)
pset_performancedriven = express_getattr(IfcPropertySetTemplateTypeEnum, 'PSET_PERFORMANCEDRIVEN', INDETERMINATE)
qto_typedrivenonly = express_getattr(IfcPropertySetTemplateTypeEnum, 'QTO_TYPEDRIVENONLY', INDETERMINATE)
qto_typedrivenoverride = express_getattr(IfcPropertySetTemplateTypeEnum, 'QTO_TYPEDRIVENOVERRIDE', INDETERMINATE)
qto_occurrencedriven = express_getattr(IfcPropertySetTemplateTypeEnum, 'QTO_OCCURRENCEDRIVEN', INDETERMINATE)
notdefined = express_getattr(IfcPropertySetTemplateTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcProtectiveDeviceTrippingUnitTypeEnum = enum_namespace()
electronic = express_getattr(IfcProtectiveDeviceTrippingUnitTypeEnum, 'ELECTRONIC', INDETERMINATE)
electromagnetic = express_getattr(IfcProtectiveDeviceTrippingUnitTypeEnum, 'ELECTROMAGNETIC', INDETERMINATE)
residualcurrent = express_getattr(IfcProtectiveDeviceTrippingUnitTypeEnum, 'RESIDUALCURRENT', INDETERMINATE)
thermal = express_getattr(IfcProtectiveDeviceTrippingUnitTypeEnum, 'THERMAL', INDETERMINATE)
userdefined = express_getattr(IfcProtectiveDeviceTrippingUnitTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcProtectiveDeviceTrippingUnitTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcProtectiveDeviceTypeEnum = enum_namespace()
circuitbreaker = express_getattr(IfcProtectiveDeviceTypeEnum, 'CIRCUITBREAKER', INDETERMINATE)
earthleakagecircuitbreaker = express_getattr(IfcProtectiveDeviceTypeEnum, 'EARTHLEAKAGECIRCUITBREAKER', INDETERMINATE)
earthingswitch = express_getattr(IfcProtectiveDeviceTypeEnum, 'EARTHINGSWITCH', INDETERMINATE)
fusedisconnector = express_getattr(IfcProtectiveDeviceTypeEnum, 'FUSEDISCONNECTOR', INDETERMINATE)
residualcurrentcircuitbreaker = express_getattr(IfcProtectiveDeviceTypeEnum, 'RESIDUALCURRENTCIRCUITBREAKER', INDETERMINATE)
residualcurrentswitch = express_getattr(IfcProtectiveDeviceTypeEnum, 'RESIDUALCURRENTSWITCH', INDETERMINATE)
varistor = express_getattr(IfcProtectiveDeviceTypeEnum, 'VARISTOR', INDETERMINATE)
anti_arcing_device = express_getattr(IfcProtectiveDeviceTypeEnum, 'ANTI_ARCING_DEVICE', INDETERMINATE)
sparkgap = express_getattr(IfcProtectiveDeviceTypeEnum, 'SPARKGAP', INDETERMINATE)
voltagelimiter = express_getattr(IfcProtectiveDeviceTypeEnum, 'VOLTAGELIMITER', INDETERMINATE)
userdefined = express_getattr(IfcProtectiveDeviceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcProtectiveDeviceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcPumpTypeEnum = enum_namespace()
circulator = express_getattr(IfcPumpTypeEnum, 'CIRCULATOR', INDETERMINATE)
endsuction = express_getattr(IfcPumpTypeEnum, 'ENDSUCTION', INDETERMINATE)
splitcase = express_getattr(IfcPumpTypeEnum, 'SPLITCASE', INDETERMINATE)
submersiblepump = express_getattr(IfcPumpTypeEnum, 'SUBMERSIBLEPUMP', INDETERMINATE)
sumppump = express_getattr(IfcPumpTypeEnum, 'SUMPPUMP', INDETERMINATE)
verticalinline = express_getattr(IfcPumpTypeEnum, 'VERTICALINLINE', INDETERMINATE)
verticalturbine = express_getattr(IfcPumpTypeEnum, 'VERTICALTURBINE', INDETERMINATE)
userdefined = express_getattr(IfcPumpTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcPumpTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcRailTypeEnum = enum_namespace()
rackrail = express_getattr(IfcRailTypeEnum, 'RACKRAIL', INDETERMINATE)
blade = express_getattr(IfcRailTypeEnum, 'BLADE', INDETERMINATE)
guardrail = express_getattr(IfcRailTypeEnum, 'GUARDRAIL', INDETERMINATE)
stockrail = express_getattr(IfcRailTypeEnum, 'STOCKRAIL', INDETERMINATE)
checkrail = express_getattr(IfcRailTypeEnum, 'CHECKRAIL', INDETERMINATE)
rail = express_getattr(IfcRailTypeEnum, 'RAIL', INDETERMINATE)
userdefined = express_getattr(IfcRailTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcRailTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcRailingTypeEnum = enum_namespace()
handrail = express_getattr(IfcRailingTypeEnum, 'HANDRAIL', INDETERMINATE)
guardrail = express_getattr(IfcRailingTypeEnum, 'GUARDRAIL', INDETERMINATE)
balustrade = express_getattr(IfcRailingTypeEnum, 'BALUSTRADE', INDETERMINATE)
fence = express_getattr(IfcRailingTypeEnum, 'FENCE', INDETERMINATE)
userdefined = express_getattr(IfcRailingTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcRailingTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcRailwayPartTypeEnum = enum_namespace()
trackstructure = express_getattr(IfcRailwayPartTypeEnum, 'TRACKSTRUCTURE', INDETERMINATE)
trackstructurepart = express_getattr(IfcRailwayPartTypeEnum, 'TRACKSTRUCTUREPART', INDETERMINATE)
linesidestructurepart = express_getattr(IfcRailwayPartTypeEnum, 'LINESIDESTRUCTUREPART', INDETERMINATE)
dilatationsuperstructure = express_getattr(IfcRailwayPartTypeEnum, 'DILATATIONSUPERSTRUCTURE', INDETERMINATE)
plaintracksupestructure = express_getattr(IfcRailwayPartTypeEnum, 'PLAINTRACKSUPESTRUCTURE', INDETERMINATE)
linesidestructure = express_getattr(IfcRailwayPartTypeEnum, 'LINESIDESTRUCTURE', INDETERMINATE)
superstructure = express_getattr(IfcRailwayPartTypeEnum, 'SUPERSTRUCTURE', INDETERMINATE)
turnoutsuperstructure = express_getattr(IfcRailwayPartTypeEnum, 'TURNOUTSUPERSTRUCTURE', INDETERMINATE)
userdefined = express_getattr(IfcRailwayPartTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcRailwayPartTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcRailwayTypeEnum = enum_namespace()
userdefined = express_getattr(IfcRailwayTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcRailwayTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcRampFlightTypeEnum = enum_namespace()
straight = express_getattr(IfcRampFlightTypeEnum, 'STRAIGHT', INDETERMINATE)
spiral = express_getattr(IfcRampFlightTypeEnum, 'SPIRAL', INDETERMINATE)
userdefined = express_getattr(IfcRampFlightTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcRampFlightTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcRampTypeEnum = enum_namespace()
straight_run_ramp = express_getattr(IfcRampTypeEnum, 'STRAIGHT_RUN_RAMP', INDETERMINATE)
two_straight_run_ramp = express_getattr(IfcRampTypeEnum, 'TWO_STRAIGHT_RUN_RAMP', INDETERMINATE)
quarter_turn_ramp = express_getattr(IfcRampTypeEnum, 'QUARTER_TURN_RAMP', INDETERMINATE)
two_quarter_turn_ramp = express_getattr(IfcRampTypeEnum, 'TWO_QUARTER_TURN_RAMP', INDETERMINATE)
half_turn_ramp = express_getattr(IfcRampTypeEnum, 'HALF_TURN_RAMP', INDETERMINATE)
spiral_ramp = express_getattr(IfcRampTypeEnum, 'SPIRAL_RAMP', INDETERMINATE)
userdefined = express_getattr(IfcRampTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcRampTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcRecurrenceTypeEnum = enum_namespace()
daily = express_getattr(IfcRecurrenceTypeEnum, 'DAILY', INDETERMINATE)
weekly = express_getattr(IfcRecurrenceTypeEnum, 'WEEKLY', INDETERMINATE)
monthly_by_day_of_month = express_getattr(IfcRecurrenceTypeEnum, 'MONTHLY_BY_DAY_OF_MONTH', INDETERMINATE)
monthly_by_position = express_getattr(IfcRecurrenceTypeEnum, 'MONTHLY_BY_POSITION', INDETERMINATE)
by_day_count = express_getattr(IfcRecurrenceTypeEnum, 'BY_DAY_COUNT', INDETERMINATE)
by_weekday_count = express_getattr(IfcRecurrenceTypeEnum, 'BY_WEEKDAY_COUNT', INDETERMINATE)
yearly_by_day_of_month = express_getattr(IfcRecurrenceTypeEnum, 'YEARLY_BY_DAY_OF_MONTH', INDETERMINATE)
yearly_by_position = express_getattr(IfcRecurrenceTypeEnum, 'YEARLY_BY_POSITION', INDETERMINATE)
IfcReferentTypeEnum = enum_namespace()
kilopoint = express_getattr(IfcReferentTypeEnum, 'KILOPOINT', INDETERMINATE)
milepoint = express_getattr(IfcReferentTypeEnum, 'MILEPOINT', INDETERMINATE)
station = express_getattr(IfcReferentTypeEnum, 'STATION', INDETERMINATE)
referencemarker = express_getattr(IfcReferentTypeEnum, 'REFERENCEMARKER', INDETERMINATE)
landmark = express_getattr(IfcReferentTypeEnum, 'LANDMARK', INDETERMINATE)
boundary = express_getattr(IfcReferentTypeEnum, 'BOUNDARY', INDETERMINATE)
intersection = express_getattr(IfcReferentTypeEnum, 'INTERSECTION', INDETERMINATE)
position = express_getattr(IfcReferentTypeEnum, 'POSITION', INDETERMINATE)
userdefined = express_getattr(IfcReferentTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcReferentTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcReflectanceMethodEnum = enum_namespace()
blinn = express_getattr(IfcReflectanceMethodEnum, 'BLINN', INDETERMINATE)
flat = express_getattr(IfcReflectanceMethodEnum, 'FLAT', INDETERMINATE)
glass = express_getattr(IfcReflectanceMethodEnum, 'GLASS', INDETERMINATE)
matt = express_getattr(IfcReflectanceMethodEnum, 'MATT', INDETERMINATE)
metal = express_getattr(IfcReflectanceMethodEnum, 'METAL', INDETERMINATE)
mirror = express_getattr(IfcReflectanceMethodEnum, 'MIRROR', INDETERMINATE)
phong = express_getattr(IfcReflectanceMethodEnum, 'PHONG', INDETERMINATE)
plastic = express_getattr(IfcReflectanceMethodEnum, 'PLASTIC', INDETERMINATE)
strauss = express_getattr(IfcReflectanceMethodEnum, 'STRAUSS', INDETERMINATE)
notdefined = express_getattr(IfcReflectanceMethodEnum, 'NOTDEFINED', INDETERMINATE)
IfcReinforcedSoilTypeEnum = enum_namespace()
surchargepreloaded = express_getattr(IfcReinforcedSoilTypeEnum, 'SURCHARGEPRELOADED', INDETERMINATE)
verticallydrained = express_getattr(IfcReinforcedSoilTypeEnum, 'VERTICALLYDRAINED', INDETERMINATE)
dynamicallycompacted = express_getattr(IfcReinforcedSoilTypeEnum, 'DYNAMICALLYCOMPACTED', INDETERMINATE)
replaced = express_getattr(IfcReinforcedSoilTypeEnum, 'REPLACED', INDETERMINATE)
rollercompacted = express_getattr(IfcReinforcedSoilTypeEnum, 'ROLLERCOMPACTED', INDETERMINATE)
grouted = express_getattr(IfcReinforcedSoilTypeEnum, 'GROUTED', INDETERMINATE)
userdefined = express_getattr(IfcReinforcedSoilTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcReinforcedSoilTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcReinforcingBarRoleEnum = enum_namespace()
main = express_getattr(IfcReinforcingBarRoleEnum, 'MAIN', INDETERMINATE)
shear = express_getattr(IfcReinforcingBarRoleEnum, 'SHEAR', INDETERMINATE)
ligature = express_getattr(IfcReinforcingBarRoleEnum, 'LIGATURE', INDETERMINATE)
stud = express_getattr(IfcReinforcingBarRoleEnum, 'STUD', INDETERMINATE)
punching = express_getattr(IfcReinforcingBarRoleEnum, 'PUNCHING', INDETERMINATE)
edge = express_getattr(IfcReinforcingBarRoleEnum, 'EDGE', INDETERMINATE)
ring = express_getattr(IfcReinforcingBarRoleEnum, 'RING', INDETERMINATE)
anchoring = express_getattr(IfcReinforcingBarRoleEnum, 'ANCHORING', INDETERMINATE)
userdefined = express_getattr(IfcReinforcingBarRoleEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcReinforcingBarRoleEnum, 'NOTDEFINED', INDETERMINATE)
IfcReinforcingBarSurfaceEnum = enum_namespace()
plain = express_getattr(IfcReinforcingBarSurfaceEnum, 'PLAIN', INDETERMINATE)
textured = express_getattr(IfcReinforcingBarSurfaceEnum, 'TEXTURED', INDETERMINATE)
IfcReinforcingBarTypeEnum = enum_namespace()
anchoring = express_getattr(IfcReinforcingBarTypeEnum, 'ANCHORING', INDETERMINATE)
edge = express_getattr(IfcReinforcingBarTypeEnum, 'EDGE', INDETERMINATE)
ligature = express_getattr(IfcReinforcingBarTypeEnum, 'LIGATURE', INDETERMINATE)
main = express_getattr(IfcReinforcingBarTypeEnum, 'MAIN', INDETERMINATE)
punching = express_getattr(IfcReinforcingBarTypeEnum, 'PUNCHING', INDETERMINATE)
ring = express_getattr(IfcReinforcingBarTypeEnum, 'RING', INDETERMINATE)
shear = express_getattr(IfcReinforcingBarTypeEnum, 'SHEAR', INDETERMINATE)
stud = express_getattr(IfcReinforcingBarTypeEnum, 'STUD', INDETERMINATE)
spacebar = express_getattr(IfcReinforcingBarTypeEnum, 'SPACEBAR', INDETERMINATE)
userdefined = express_getattr(IfcReinforcingBarTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcReinforcingBarTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcReinforcingMeshTypeEnum = enum_namespace()
userdefined = express_getattr(IfcReinforcingMeshTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcReinforcingMeshTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcRoadPartTypeEnum = enum_namespace()
roadsidepart = express_getattr(IfcRoadPartTypeEnum, 'ROADSIDEPART', INDETERMINATE)
bus_stop = express_getattr(IfcRoadPartTypeEnum, 'BUS_STOP', INDETERMINATE)
hardshoulder = express_getattr(IfcRoadPartTypeEnum, 'HARDSHOULDER', INDETERMINATE)
intersection = express_getattr(IfcRoadPartTypeEnum, 'INTERSECTION', INDETERMINATE)
passingbay = express_getattr(IfcRoadPartTypeEnum, 'PASSINGBAY', INDETERMINATE)
roadwayplateau = express_getattr(IfcRoadPartTypeEnum, 'ROADWAYPLATEAU', INDETERMINATE)
roadside = express_getattr(IfcRoadPartTypeEnum, 'ROADSIDE', INDETERMINATE)
refugeisland = express_getattr(IfcRoadPartTypeEnum, 'REFUGEISLAND', INDETERMINATE)
tollplaza = express_getattr(IfcRoadPartTypeEnum, 'TOLLPLAZA', INDETERMINATE)
centralreserve = express_getattr(IfcRoadPartTypeEnum, 'CENTRALRESERVE', INDETERMINATE)
sidewalk = express_getattr(IfcRoadPartTypeEnum, 'SIDEWALK', INDETERMINATE)
parkingbay = express_getattr(IfcRoadPartTypeEnum, 'PARKINGBAY', INDETERMINATE)
railwaycrossing = express_getattr(IfcRoadPartTypeEnum, 'RAILWAYCROSSING', INDETERMINATE)
pedestrian_crossing = express_getattr(IfcRoadPartTypeEnum, 'PEDESTRIAN_CROSSING', INDETERMINATE)
softshoulder = express_getattr(IfcRoadPartTypeEnum, 'SOFTSHOULDER', INDETERMINATE)
bicyclecrossing = express_getattr(IfcRoadPartTypeEnum, 'BICYCLECROSSING', INDETERMINATE)
centralisland = express_getattr(IfcRoadPartTypeEnum, 'CENTRALISLAND', INDETERMINATE)
shoulder = express_getattr(IfcRoadPartTypeEnum, 'SHOULDER', INDETERMINATE)
trafficlane = express_getattr(IfcRoadPartTypeEnum, 'TRAFFICLANE', INDETERMINATE)
roadsegment = express_getattr(IfcRoadPartTypeEnum, 'ROADSEGMENT', INDETERMINATE)
roundabout = express_getattr(IfcRoadPartTypeEnum, 'ROUNDABOUT', INDETERMINATE)
layby = express_getattr(IfcRoadPartTypeEnum, 'LAYBY', INDETERMINATE)
carriageway = express_getattr(IfcRoadPartTypeEnum, 'CARRIAGEWAY', INDETERMINATE)
trafficisland = express_getattr(IfcRoadPartTypeEnum, 'TRAFFICISLAND', INDETERMINATE)
userdefined = express_getattr(IfcRoadPartTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcRoadPartTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcRoadTypeEnum = enum_namespace()
userdefined = express_getattr(IfcRoadTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcRoadTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcRoleEnum = enum_namespace()
supplier = express_getattr(IfcRoleEnum, 'SUPPLIER', INDETERMINATE)
manufacturer = express_getattr(IfcRoleEnum, 'MANUFACTURER', INDETERMINATE)
contractor = express_getattr(IfcRoleEnum, 'CONTRACTOR', INDETERMINATE)
subcontractor = express_getattr(IfcRoleEnum, 'SUBCONTRACTOR', INDETERMINATE)
architect = express_getattr(IfcRoleEnum, 'ARCHITECT', INDETERMINATE)
structuralengineer = express_getattr(IfcRoleEnum, 'STRUCTURALENGINEER', INDETERMINATE)
costengineer = express_getattr(IfcRoleEnum, 'COSTENGINEER', INDETERMINATE)
client = express_getattr(IfcRoleEnum, 'CLIENT', INDETERMINATE)
buildingowner = express_getattr(IfcRoleEnum, 'BUILDINGOWNER', INDETERMINATE)
buildingoperator = express_getattr(IfcRoleEnum, 'BUILDINGOPERATOR', INDETERMINATE)
mechanicalengineer = express_getattr(IfcRoleEnum, 'MECHANICALENGINEER', INDETERMINATE)
electricalengineer = express_getattr(IfcRoleEnum, 'ELECTRICALENGINEER', INDETERMINATE)
projectmanager = express_getattr(IfcRoleEnum, 'PROJECTMANAGER', INDETERMINATE)
facilitiesmanager = express_getattr(IfcRoleEnum, 'FACILITIESMANAGER', INDETERMINATE)
civilengineer = express_getattr(IfcRoleEnum, 'CIVILENGINEER', INDETERMINATE)
commissioningengineer = express_getattr(IfcRoleEnum, 'COMMISSIONINGENGINEER', INDETERMINATE)
engineer = express_getattr(IfcRoleEnum, 'ENGINEER', INDETERMINATE)
owner = express_getattr(IfcRoleEnum, 'OWNER', INDETERMINATE)
consultant = express_getattr(IfcRoleEnum, 'CONSULTANT', INDETERMINATE)
constructionmanager = express_getattr(IfcRoleEnum, 'CONSTRUCTIONMANAGER', INDETERMINATE)
fieldconstructionmanager = express_getattr(IfcRoleEnum, 'FIELDCONSTRUCTIONMANAGER', INDETERMINATE)
reseller = express_getattr(IfcRoleEnum, 'RESELLER', INDETERMINATE)
userdefined = express_getattr(IfcRoleEnum, 'USERDEFINED', INDETERMINATE)
IfcRoofTypeEnum = enum_namespace()
flat_roof = express_getattr(IfcRoofTypeEnum, 'FLAT_ROOF', INDETERMINATE)
shed_roof = express_getattr(IfcRoofTypeEnum, 'SHED_ROOF', INDETERMINATE)
gable_roof = express_getattr(IfcRoofTypeEnum, 'GABLE_ROOF', INDETERMINATE)
hip_roof = express_getattr(IfcRoofTypeEnum, 'HIP_ROOF', INDETERMINATE)
hipped_gable_roof = express_getattr(IfcRoofTypeEnum, 'HIPPED_GABLE_ROOF', INDETERMINATE)
gambrel_roof = express_getattr(IfcRoofTypeEnum, 'GAMBREL_ROOF', INDETERMINATE)
mansard_roof = express_getattr(IfcRoofTypeEnum, 'MANSARD_ROOF', INDETERMINATE)
barrel_roof = express_getattr(IfcRoofTypeEnum, 'BARREL_ROOF', INDETERMINATE)
rainbow_roof = express_getattr(IfcRoofTypeEnum, 'RAINBOW_ROOF', INDETERMINATE)
butterfly_roof = express_getattr(IfcRoofTypeEnum, 'BUTTERFLY_ROOF', INDETERMINATE)
pavilion_roof = express_getattr(IfcRoofTypeEnum, 'PAVILION_ROOF', INDETERMINATE)
dome_roof = express_getattr(IfcRoofTypeEnum, 'DOME_ROOF', INDETERMINATE)
freeform = express_getattr(IfcRoofTypeEnum, 'FREEFORM', INDETERMINATE)
userdefined = express_getattr(IfcRoofTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcRoofTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcSIPrefix = enum_namespace()
exa = express_getattr(IfcSIPrefix, 'EXA', INDETERMINATE)
peta = express_getattr(IfcSIPrefix, 'PETA', INDETERMINATE)
tera = express_getattr(IfcSIPrefix, 'TERA', INDETERMINATE)
giga = express_getattr(IfcSIPrefix, 'GIGA', INDETERMINATE)
mega = express_getattr(IfcSIPrefix, 'MEGA', INDETERMINATE)
kilo = express_getattr(IfcSIPrefix, 'KILO', INDETERMINATE)
hecto = express_getattr(IfcSIPrefix, 'HECTO', INDETERMINATE)
deca = express_getattr(IfcSIPrefix, 'DECA', INDETERMINATE)
deci = express_getattr(IfcSIPrefix, 'DECI', INDETERMINATE)
centi = express_getattr(IfcSIPrefix, 'CENTI', INDETERMINATE)
milli = express_getattr(IfcSIPrefix, 'MILLI', INDETERMINATE)
micro = express_getattr(IfcSIPrefix, 'MICRO', INDETERMINATE)
nano = express_getattr(IfcSIPrefix, 'NANO', INDETERMINATE)
pico = express_getattr(IfcSIPrefix, 'PICO', INDETERMINATE)
femto = express_getattr(IfcSIPrefix, 'FEMTO', INDETERMINATE)
atto = express_getattr(IfcSIPrefix, 'ATTO', INDETERMINATE)
IfcSIUnitName = enum_namespace()
ampere = express_getattr(IfcSIUnitName, 'AMPERE', INDETERMINATE)
becquerel = express_getattr(IfcSIUnitName, 'BECQUEREL', INDETERMINATE)
candela = express_getattr(IfcSIUnitName, 'CANDELA', INDETERMINATE)
coulomb = express_getattr(IfcSIUnitName, 'COULOMB', INDETERMINATE)
cubic_metre = express_getattr(IfcSIUnitName, 'CUBIC_METRE', INDETERMINATE)
degree_celsius = express_getattr(IfcSIUnitName, 'DEGREE_CELSIUS', INDETERMINATE)
farad = express_getattr(IfcSIUnitName, 'FARAD', INDETERMINATE)
gram = express_getattr(IfcSIUnitName, 'GRAM', INDETERMINATE)
gray = express_getattr(IfcSIUnitName, 'GRAY', INDETERMINATE)
henry = express_getattr(IfcSIUnitName, 'HENRY', INDETERMINATE)
hertz = express_getattr(IfcSIUnitName, 'HERTZ', INDETERMINATE)
joule = express_getattr(IfcSIUnitName, 'JOULE', INDETERMINATE)
kelvin = express_getattr(IfcSIUnitName, 'KELVIN', INDETERMINATE)
lumen = express_getattr(IfcSIUnitName, 'LUMEN', INDETERMINATE)
lux = express_getattr(IfcSIUnitName, 'LUX', INDETERMINATE)
metre = express_getattr(IfcSIUnitName, 'METRE', INDETERMINATE)
mole = express_getattr(IfcSIUnitName, 'MOLE', INDETERMINATE)
newton = express_getattr(IfcSIUnitName, 'NEWTON', INDETERMINATE)
ohm = express_getattr(IfcSIUnitName, 'OHM', INDETERMINATE)
pascal = express_getattr(IfcSIUnitName, 'PASCAL', INDETERMINATE)
radian = express_getattr(IfcSIUnitName, 'RADIAN', INDETERMINATE)
second = express_getattr(IfcSIUnitName, 'SECOND', INDETERMINATE)
siemens = express_getattr(IfcSIUnitName, 'SIEMENS', INDETERMINATE)
sievert = express_getattr(IfcSIUnitName, 'SIEVERT', INDETERMINATE)
square_metre = express_getattr(IfcSIUnitName, 'SQUARE_METRE', INDETERMINATE)
steradian = express_getattr(IfcSIUnitName, 'STERADIAN', INDETERMINATE)
tesla = express_getattr(IfcSIUnitName, 'TESLA', INDETERMINATE)
volt = express_getattr(IfcSIUnitName, 'VOLT', INDETERMINATE)
watt = express_getattr(IfcSIUnitName, 'WATT', INDETERMINATE)
weber = express_getattr(IfcSIUnitName, 'WEBER', INDETERMINATE)
IfcSanitaryTerminalTypeEnum = enum_namespace()
bath = express_getattr(IfcSanitaryTerminalTypeEnum, 'BATH', INDETERMINATE)
bidet = express_getattr(IfcSanitaryTerminalTypeEnum, 'BIDET', INDETERMINATE)
cistern = express_getattr(IfcSanitaryTerminalTypeEnum, 'CISTERN', INDETERMINATE)
shower = express_getattr(IfcSanitaryTerminalTypeEnum, 'SHOWER', INDETERMINATE)
sink = express_getattr(IfcSanitaryTerminalTypeEnum, 'SINK', INDETERMINATE)
sanitaryfountain = express_getattr(IfcSanitaryTerminalTypeEnum, 'SANITARYFOUNTAIN', INDETERMINATE)
toiletpan = express_getattr(IfcSanitaryTerminalTypeEnum, 'TOILETPAN', INDETERMINATE)
urinal = express_getattr(IfcSanitaryTerminalTypeEnum, 'URINAL', INDETERMINATE)
washhandbasin = express_getattr(IfcSanitaryTerminalTypeEnum, 'WASHHANDBASIN', INDETERMINATE)
wcseat = express_getattr(IfcSanitaryTerminalTypeEnum, 'WCSEAT', INDETERMINATE)
userdefined = express_getattr(IfcSanitaryTerminalTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcSanitaryTerminalTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcSectionTypeEnum = enum_namespace()
uniform = express_getattr(IfcSectionTypeEnum, 'UNIFORM', INDETERMINATE)
tapered = express_getattr(IfcSectionTypeEnum, 'TAPERED', INDETERMINATE)
IfcSensorTypeEnum = enum_namespace()
cosensor = express_getattr(IfcSensorTypeEnum, 'COSENSOR', INDETERMINATE)
co2sensor = express_getattr(IfcSensorTypeEnum, 'CO2SENSOR', INDETERMINATE)
conductancesensor = express_getattr(IfcSensorTypeEnum, 'CONDUCTANCESENSOR', INDETERMINATE)
contactsensor = express_getattr(IfcSensorTypeEnum, 'CONTACTSENSOR', INDETERMINATE)
firesensor = express_getattr(IfcSensorTypeEnum, 'FIRESENSOR', INDETERMINATE)
flowsensor = express_getattr(IfcSensorTypeEnum, 'FLOWSENSOR', INDETERMINATE)
frostsensor = express_getattr(IfcSensorTypeEnum, 'FROSTSENSOR', INDETERMINATE)
gassensor = express_getattr(IfcSensorTypeEnum, 'GASSENSOR', INDETERMINATE)
heatsensor = express_getattr(IfcSensorTypeEnum, 'HEATSENSOR', INDETERMINATE)
humiditysensor = express_getattr(IfcSensorTypeEnum, 'HUMIDITYSENSOR', INDETERMINATE)
identifiersensor = express_getattr(IfcSensorTypeEnum, 'IDENTIFIERSENSOR', INDETERMINATE)
ionconcentrationsensor = express_getattr(IfcSensorTypeEnum, 'IONCONCENTRATIONSENSOR', INDETERMINATE)
levelsensor = express_getattr(IfcSensorTypeEnum, 'LEVELSENSOR', INDETERMINATE)
lightsensor = express_getattr(IfcSensorTypeEnum, 'LIGHTSENSOR', INDETERMINATE)
moisturesensor = express_getattr(IfcSensorTypeEnum, 'MOISTURESENSOR', INDETERMINATE)
movementsensor = express_getattr(IfcSensorTypeEnum, 'MOVEMENTSENSOR', INDETERMINATE)
phsensor = express_getattr(IfcSensorTypeEnum, 'PHSENSOR', INDETERMINATE)
pressuresensor = express_getattr(IfcSensorTypeEnum, 'PRESSURESENSOR', INDETERMINATE)
radiationsensor = express_getattr(IfcSensorTypeEnum, 'RADIATIONSENSOR', INDETERMINATE)
radioactivitysensor = express_getattr(IfcSensorTypeEnum, 'RADIOACTIVITYSENSOR', INDETERMINATE)
smokesensor = express_getattr(IfcSensorTypeEnum, 'SMOKESENSOR', INDETERMINATE)
soundsensor = express_getattr(IfcSensorTypeEnum, 'SOUNDSENSOR', INDETERMINATE)
temperaturesensor = express_getattr(IfcSensorTypeEnum, 'TEMPERATURESENSOR', INDETERMINATE)
windsensor = express_getattr(IfcSensorTypeEnum, 'WINDSENSOR', INDETERMINATE)
earthquakesensor = express_getattr(IfcSensorTypeEnum, 'EARTHQUAKESENSOR', INDETERMINATE)
foreignobjectdetectionsensor = express_getattr(IfcSensorTypeEnum, 'FOREIGNOBJECTDETECTIONSENSOR', INDETERMINATE)
obstaclesensor = express_getattr(IfcSensorTypeEnum, 'OBSTACLESENSOR', INDETERMINATE)
rainsensor = express_getattr(IfcSensorTypeEnum, 'RAINSENSOR', INDETERMINATE)
snowdepthsensor = express_getattr(IfcSensorTypeEnum, 'SNOWDEPTHSENSOR', INDETERMINATE)
trainsensor = express_getattr(IfcSensorTypeEnum, 'TRAINSENSOR', INDETERMINATE)
turnoutclosuresensor = express_getattr(IfcSensorTypeEnum, 'TURNOUTCLOSURESENSOR', INDETERMINATE)
wheelsensor = express_getattr(IfcSensorTypeEnum, 'WHEELSENSOR', INDETERMINATE)
userdefined = express_getattr(IfcSensorTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcSensorTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcSequenceEnum = enum_namespace()
start_start = express_getattr(IfcSequenceEnum, 'START_START', INDETERMINATE)
start_finish = express_getattr(IfcSequenceEnum, 'START_FINISH', INDETERMINATE)
finish_start = express_getattr(IfcSequenceEnum, 'FINISH_START', INDETERMINATE)
finish_finish = express_getattr(IfcSequenceEnum, 'FINISH_FINISH', INDETERMINATE)
userdefined = express_getattr(IfcSequenceEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcSequenceEnum, 'NOTDEFINED', INDETERMINATE)
IfcShadingDeviceTypeEnum = enum_namespace()
jalousie = express_getattr(IfcShadingDeviceTypeEnum, 'JALOUSIE', INDETERMINATE)
shutter = express_getattr(IfcShadingDeviceTypeEnum, 'SHUTTER', INDETERMINATE)
awning = express_getattr(IfcShadingDeviceTypeEnum, 'AWNING', INDETERMINATE)
userdefined = express_getattr(IfcShadingDeviceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcShadingDeviceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcSignTypeEnum = enum_namespace()
marker = express_getattr(IfcSignTypeEnum, 'MARKER', INDETERMINATE)
pictoral = express_getattr(IfcSignTypeEnum, 'PICTORAL', INDETERMINATE)
mirror = express_getattr(IfcSignTypeEnum, 'MIRROR', INDETERMINATE)
userdefined = express_getattr(IfcSignTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcSignTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcSignalTypeEnum = enum_namespace()
visual = express_getattr(IfcSignalTypeEnum, 'VISUAL', INDETERMINATE)
audio = express_getattr(IfcSignalTypeEnum, 'AUDIO', INDETERMINATE)
mixed = express_getattr(IfcSignalTypeEnum, 'MIXED', INDETERMINATE)
userdefined = express_getattr(IfcSignalTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcSignalTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcSimplePropertyTemplateTypeEnum = enum_namespace()
p_singlevalue = express_getattr(IfcSimplePropertyTemplateTypeEnum, 'P_SINGLEVALUE', INDETERMINATE)
p_enumeratedvalue = express_getattr(IfcSimplePropertyTemplateTypeEnum, 'P_ENUMERATEDVALUE', INDETERMINATE)
p_boundedvalue = express_getattr(IfcSimplePropertyTemplateTypeEnum, 'P_BOUNDEDVALUE', INDETERMINATE)
p_listvalue = express_getattr(IfcSimplePropertyTemplateTypeEnum, 'P_LISTVALUE', INDETERMINATE)
p_tablevalue = express_getattr(IfcSimplePropertyTemplateTypeEnum, 'P_TABLEVALUE', INDETERMINATE)
p_referencevalue = express_getattr(IfcSimplePropertyTemplateTypeEnum, 'P_REFERENCEVALUE', INDETERMINATE)
q_length = express_getattr(IfcSimplePropertyTemplateTypeEnum, 'Q_LENGTH', INDETERMINATE)
q_area = express_getattr(IfcSimplePropertyTemplateTypeEnum, 'Q_AREA', INDETERMINATE)
q_volume = express_getattr(IfcSimplePropertyTemplateTypeEnum, 'Q_VOLUME', INDETERMINATE)
q_count = express_getattr(IfcSimplePropertyTemplateTypeEnum, 'Q_COUNT', INDETERMINATE)
q_weight = express_getattr(IfcSimplePropertyTemplateTypeEnum, 'Q_WEIGHT', INDETERMINATE)
q_time = express_getattr(IfcSimplePropertyTemplateTypeEnum, 'Q_TIME', INDETERMINATE)
IfcSlabTypeEnum = enum_namespace()
floor = express_getattr(IfcSlabTypeEnum, 'FLOOR', INDETERMINATE)
roof = express_getattr(IfcSlabTypeEnum, 'ROOF', INDETERMINATE)
landing = express_getattr(IfcSlabTypeEnum, 'LANDING', INDETERMINATE)
baseslab = express_getattr(IfcSlabTypeEnum, 'BASESLAB', INDETERMINATE)
approach_slab = express_getattr(IfcSlabTypeEnum, 'APPROACH_SLAB', INDETERMINATE)
paving = express_getattr(IfcSlabTypeEnum, 'PAVING', INDETERMINATE)
wearing = express_getattr(IfcSlabTypeEnum, 'WEARING', INDETERMINATE)
sidewalk = express_getattr(IfcSlabTypeEnum, 'SIDEWALK', INDETERMINATE)
trackslab = express_getattr(IfcSlabTypeEnum, 'TRACKSLAB', INDETERMINATE)
userdefined = express_getattr(IfcSlabTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcSlabTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcSolarDeviceTypeEnum = enum_namespace()
solarcollector = express_getattr(IfcSolarDeviceTypeEnum, 'SOLARCOLLECTOR', INDETERMINATE)
solarpanel = express_getattr(IfcSolarDeviceTypeEnum, 'SOLARPANEL', INDETERMINATE)
userdefined = express_getattr(IfcSolarDeviceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcSolarDeviceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcSpaceHeaterTypeEnum = enum_namespace()
convector = express_getattr(IfcSpaceHeaterTypeEnum, 'CONVECTOR', INDETERMINATE)
radiator = express_getattr(IfcSpaceHeaterTypeEnum, 'RADIATOR', INDETERMINATE)
userdefined = express_getattr(IfcSpaceHeaterTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcSpaceHeaterTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcSpaceTypeEnum = enum_namespace()
space = express_getattr(IfcSpaceTypeEnum, 'SPACE', INDETERMINATE)
parking = express_getattr(IfcSpaceTypeEnum, 'PARKING', INDETERMINATE)
gfa = express_getattr(IfcSpaceTypeEnum, 'GFA', INDETERMINATE)
internal = express_getattr(IfcSpaceTypeEnum, 'INTERNAL', INDETERMINATE)
external = express_getattr(IfcSpaceTypeEnum, 'EXTERNAL', INDETERMINATE)
berth = express_getattr(IfcSpaceTypeEnum, 'BERTH', INDETERMINATE)
userdefined = express_getattr(IfcSpaceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcSpaceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcSpatialZoneTypeEnum = enum_namespace()
construction = express_getattr(IfcSpatialZoneTypeEnum, 'CONSTRUCTION', INDETERMINATE)
firesafety = express_getattr(IfcSpatialZoneTypeEnum, 'FIRESAFETY', INDETERMINATE)
lighting = express_getattr(IfcSpatialZoneTypeEnum, 'LIGHTING', INDETERMINATE)
occupancy = express_getattr(IfcSpatialZoneTypeEnum, 'OCCUPANCY', INDETERMINATE)
security = express_getattr(IfcSpatialZoneTypeEnum, 'SECURITY', INDETERMINATE)
thermal = express_getattr(IfcSpatialZoneTypeEnum, 'THERMAL', INDETERMINATE)
transport = express_getattr(IfcSpatialZoneTypeEnum, 'TRANSPORT', INDETERMINATE)
ventilation = express_getattr(IfcSpatialZoneTypeEnum, 'VENTILATION', INDETERMINATE)
reservation = express_getattr(IfcSpatialZoneTypeEnum, 'RESERVATION', INDETERMINATE)
interference = express_getattr(IfcSpatialZoneTypeEnum, 'INTERFERENCE', INDETERMINATE)
userdefined = express_getattr(IfcSpatialZoneTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcSpatialZoneTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcStackTerminalTypeEnum = enum_namespace()
birdcage = express_getattr(IfcStackTerminalTypeEnum, 'BIRDCAGE', INDETERMINATE)
cowl = express_getattr(IfcStackTerminalTypeEnum, 'COWL', INDETERMINATE)
rainwaterhopper = express_getattr(IfcStackTerminalTypeEnum, 'RAINWATERHOPPER', INDETERMINATE)
userdefined = express_getattr(IfcStackTerminalTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcStackTerminalTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcStairFlightTypeEnum = enum_namespace()
straight = express_getattr(IfcStairFlightTypeEnum, 'STRAIGHT', INDETERMINATE)
winder = express_getattr(IfcStairFlightTypeEnum, 'WINDER', INDETERMINATE)
spiral = express_getattr(IfcStairFlightTypeEnum, 'SPIRAL', INDETERMINATE)
curved = express_getattr(IfcStairFlightTypeEnum, 'CURVED', INDETERMINATE)
freeform = express_getattr(IfcStairFlightTypeEnum, 'FREEFORM', INDETERMINATE)
userdefined = express_getattr(IfcStairFlightTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcStairFlightTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcStairTypeEnum = enum_namespace()
straight_run_stair = express_getattr(IfcStairTypeEnum, 'STRAIGHT_RUN_STAIR', INDETERMINATE)
two_straight_run_stair = express_getattr(IfcStairTypeEnum, 'TWO_STRAIGHT_RUN_STAIR', INDETERMINATE)
quarter_winding_stair = express_getattr(IfcStairTypeEnum, 'QUARTER_WINDING_STAIR', INDETERMINATE)
quarter_turn_stair = express_getattr(IfcStairTypeEnum, 'QUARTER_TURN_STAIR', INDETERMINATE)
half_winding_stair = express_getattr(IfcStairTypeEnum, 'HALF_WINDING_STAIR', INDETERMINATE)
half_turn_stair = express_getattr(IfcStairTypeEnum, 'HALF_TURN_STAIR', INDETERMINATE)
two_quarter_winding_stair = express_getattr(IfcStairTypeEnum, 'TWO_QUARTER_WINDING_STAIR', INDETERMINATE)
two_quarter_turn_stair = express_getattr(IfcStairTypeEnum, 'TWO_QUARTER_TURN_STAIR', INDETERMINATE)
three_quarter_winding_stair = express_getattr(IfcStairTypeEnum, 'THREE_QUARTER_WINDING_STAIR', INDETERMINATE)
three_quarter_turn_stair = express_getattr(IfcStairTypeEnum, 'THREE_QUARTER_TURN_STAIR', INDETERMINATE)
spiral_stair = express_getattr(IfcStairTypeEnum, 'SPIRAL_STAIR', INDETERMINATE)
double_return_stair = express_getattr(IfcStairTypeEnum, 'DOUBLE_RETURN_STAIR', INDETERMINATE)
curved_run_stair = express_getattr(IfcStairTypeEnum, 'CURVED_RUN_STAIR', INDETERMINATE)
two_curved_run_stair = express_getattr(IfcStairTypeEnum, 'TWO_CURVED_RUN_STAIR', INDETERMINATE)
ladder = express_getattr(IfcStairTypeEnum, 'LADDER', INDETERMINATE)
userdefined = express_getattr(IfcStairTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcStairTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcStateEnum = enum_namespace()
readwrite = express_getattr(IfcStateEnum, 'READWRITE', INDETERMINATE)
readonly = express_getattr(IfcStateEnum, 'READONLY', INDETERMINATE)
locked = express_getattr(IfcStateEnum, 'LOCKED', INDETERMINATE)
readwritelocked = express_getattr(IfcStateEnum, 'READWRITELOCKED', INDETERMINATE)
readonlylocked = express_getattr(IfcStateEnum, 'READONLYLOCKED', INDETERMINATE)
IfcStructuralCurveActivityTypeEnum = enum_namespace()
const = express_getattr(IfcStructuralCurveActivityTypeEnum, 'CONST', INDETERMINATE)
linear = express_getattr(IfcStructuralCurveActivityTypeEnum, 'LINEAR', INDETERMINATE)
polygonal = express_getattr(IfcStructuralCurveActivityTypeEnum, 'POLYGONAL', INDETERMINATE)
equidistant = express_getattr(IfcStructuralCurveActivityTypeEnum, 'EQUIDISTANT', INDETERMINATE)
sinus = express_getattr(IfcStructuralCurveActivityTypeEnum, 'SINUS', INDETERMINATE)
parabola = express_getattr(IfcStructuralCurveActivityTypeEnum, 'PARABOLA', INDETERMINATE)
discrete = express_getattr(IfcStructuralCurveActivityTypeEnum, 'DISCRETE', INDETERMINATE)
userdefined = express_getattr(IfcStructuralCurveActivityTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcStructuralCurveActivityTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcStructuralCurveMemberTypeEnum = enum_namespace()
rigid_joined_member = express_getattr(IfcStructuralCurveMemberTypeEnum, 'RIGID_JOINED_MEMBER', INDETERMINATE)
pin_joined_member = express_getattr(IfcStructuralCurveMemberTypeEnum, 'PIN_JOINED_MEMBER', INDETERMINATE)
cable = express_getattr(IfcStructuralCurveMemberTypeEnum, 'CABLE', INDETERMINATE)
tension_member = express_getattr(IfcStructuralCurveMemberTypeEnum, 'TENSION_MEMBER', INDETERMINATE)
compression_member = express_getattr(IfcStructuralCurveMemberTypeEnum, 'COMPRESSION_MEMBER', INDETERMINATE)
userdefined = express_getattr(IfcStructuralCurveMemberTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcStructuralCurveMemberTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcStructuralSurfaceActivityTypeEnum = enum_namespace()
const = express_getattr(IfcStructuralSurfaceActivityTypeEnum, 'CONST', INDETERMINATE)
bilinear = express_getattr(IfcStructuralSurfaceActivityTypeEnum, 'BILINEAR', INDETERMINATE)
discrete = express_getattr(IfcStructuralSurfaceActivityTypeEnum, 'DISCRETE', INDETERMINATE)
isocontour = express_getattr(IfcStructuralSurfaceActivityTypeEnum, 'ISOCONTOUR', INDETERMINATE)
userdefined = express_getattr(IfcStructuralSurfaceActivityTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcStructuralSurfaceActivityTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcStructuralSurfaceMemberTypeEnum = enum_namespace()
bending_element = express_getattr(IfcStructuralSurfaceMemberTypeEnum, 'BENDING_ELEMENT', INDETERMINATE)
membrane_element = express_getattr(IfcStructuralSurfaceMemberTypeEnum, 'MEMBRANE_ELEMENT', INDETERMINATE)
shell = express_getattr(IfcStructuralSurfaceMemberTypeEnum, 'SHELL', INDETERMINATE)
userdefined = express_getattr(IfcStructuralSurfaceMemberTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcStructuralSurfaceMemberTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcSubContractResourceTypeEnum = enum_namespace()
purchase = express_getattr(IfcSubContractResourceTypeEnum, 'PURCHASE', INDETERMINATE)
work = express_getattr(IfcSubContractResourceTypeEnum, 'WORK', INDETERMINATE)
userdefined = express_getattr(IfcSubContractResourceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcSubContractResourceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcSurfaceFeatureTypeEnum = enum_namespace()
mark = express_getattr(IfcSurfaceFeatureTypeEnum, 'MARK', INDETERMINATE)
tag = express_getattr(IfcSurfaceFeatureTypeEnum, 'TAG', INDETERMINATE)
treatment = express_getattr(IfcSurfaceFeatureTypeEnum, 'TREATMENT', INDETERMINATE)
defect = express_getattr(IfcSurfaceFeatureTypeEnum, 'DEFECT', INDETERMINATE)
hatchmarking = express_getattr(IfcSurfaceFeatureTypeEnum, 'HATCHMARKING', INDETERMINATE)
linemarking = express_getattr(IfcSurfaceFeatureTypeEnum, 'LINEMARKING', INDETERMINATE)
pavementsurfacemarking = express_getattr(IfcSurfaceFeatureTypeEnum, 'PAVEMENTSURFACEMARKING', INDETERMINATE)
symbolmarking = express_getattr(IfcSurfaceFeatureTypeEnum, 'SYMBOLMARKING', INDETERMINATE)
nonskidsurfacing = express_getattr(IfcSurfaceFeatureTypeEnum, 'NONSKIDSURFACING', INDETERMINATE)
rumblestrip = express_getattr(IfcSurfaceFeatureTypeEnum, 'RUMBLESTRIP', INDETERMINATE)
transverserumblestrip = express_getattr(IfcSurfaceFeatureTypeEnum, 'TRANSVERSERUMBLESTRIP', INDETERMINATE)
userdefined = express_getattr(IfcSurfaceFeatureTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcSurfaceFeatureTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcSurfaceSide = enum_namespace()
positive = express_getattr(IfcSurfaceSide, 'POSITIVE', INDETERMINATE)
negative = express_getattr(IfcSurfaceSide, 'NEGATIVE', INDETERMINATE)
both = express_getattr(IfcSurfaceSide, 'BOTH', INDETERMINATE)
IfcSwitchingDeviceTypeEnum = enum_namespace()
contactor = express_getattr(IfcSwitchingDeviceTypeEnum, 'CONTACTOR', INDETERMINATE)
dimmerswitch = express_getattr(IfcSwitchingDeviceTypeEnum, 'DIMMERSWITCH', INDETERMINATE)
emergencystop = express_getattr(IfcSwitchingDeviceTypeEnum, 'EMERGENCYSTOP', INDETERMINATE)
keypad = express_getattr(IfcSwitchingDeviceTypeEnum, 'KEYPAD', INDETERMINATE)
momentaryswitch = express_getattr(IfcSwitchingDeviceTypeEnum, 'MOMENTARYSWITCH', INDETERMINATE)
selectorswitch = express_getattr(IfcSwitchingDeviceTypeEnum, 'SELECTORSWITCH', INDETERMINATE)
starter = express_getattr(IfcSwitchingDeviceTypeEnum, 'STARTER', INDETERMINATE)
switchdisconnector = express_getattr(IfcSwitchingDeviceTypeEnum, 'SWITCHDISCONNECTOR', INDETERMINATE)
toggleswitch = express_getattr(IfcSwitchingDeviceTypeEnum, 'TOGGLESWITCH', INDETERMINATE)
relay = express_getattr(IfcSwitchingDeviceTypeEnum, 'RELAY', INDETERMINATE)
start_and_stop_equipment = express_getattr(IfcSwitchingDeviceTypeEnum, 'START_AND_STOP_EQUIPMENT', INDETERMINATE)
userdefined = express_getattr(IfcSwitchingDeviceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcSwitchingDeviceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcSystemFurnitureElementTypeEnum = enum_namespace()
panel = express_getattr(IfcSystemFurnitureElementTypeEnum, 'PANEL', INDETERMINATE)
worksurface = express_getattr(IfcSystemFurnitureElementTypeEnum, 'WORKSURFACE', INDETERMINATE)
subrack = express_getattr(IfcSystemFurnitureElementTypeEnum, 'SUBRACK', INDETERMINATE)
userdefined = express_getattr(IfcSystemFurnitureElementTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcSystemFurnitureElementTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcTankTypeEnum = enum_namespace()
basin = express_getattr(IfcTankTypeEnum, 'BASIN', INDETERMINATE)
breakpressure = express_getattr(IfcTankTypeEnum, 'BREAKPRESSURE', INDETERMINATE)
expansion = express_getattr(IfcTankTypeEnum, 'EXPANSION', INDETERMINATE)
feedandexpansion = express_getattr(IfcTankTypeEnum, 'FEEDANDEXPANSION', INDETERMINATE)
pressurevessel = express_getattr(IfcTankTypeEnum, 'PRESSUREVESSEL', INDETERMINATE)
storage = express_getattr(IfcTankTypeEnum, 'STORAGE', INDETERMINATE)
vessel = express_getattr(IfcTankTypeEnum, 'VESSEL', INDETERMINATE)
oilretentiontray = express_getattr(IfcTankTypeEnum, 'OILRETENTIONTRAY', INDETERMINATE)
userdefined = express_getattr(IfcTankTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcTankTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcTaskDurationEnum = enum_namespace()
elapsedtime = express_getattr(IfcTaskDurationEnum, 'ELAPSEDTIME', INDETERMINATE)
worktime = express_getattr(IfcTaskDurationEnum, 'WORKTIME', INDETERMINATE)
notdefined = express_getattr(IfcTaskDurationEnum, 'NOTDEFINED', INDETERMINATE)
IfcTaskTypeEnum = enum_namespace()
attendance = express_getattr(IfcTaskTypeEnum, 'ATTENDANCE', INDETERMINATE)
construction = express_getattr(IfcTaskTypeEnum, 'CONSTRUCTION', INDETERMINATE)
demolition = express_getattr(IfcTaskTypeEnum, 'DEMOLITION', INDETERMINATE)
dismantle = express_getattr(IfcTaskTypeEnum, 'DISMANTLE', INDETERMINATE)
disposal = express_getattr(IfcTaskTypeEnum, 'DISPOSAL', INDETERMINATE)
installation = express_getattr(IfcTaskTypeEnum, 'INSTALLATION', INDETERMINATE)
logistic = express_getattr(IfcTaskTypeEnum, 'LOGISTIC', INDETERMINATE)
maintenance = express_getattr(IfcTaskTypeEnum, 'MAINTENANCE', INDETERMINATE)
move = express_getattr(IfcTaskTypeEnum, 'MOVE', INDETERMINATE)
operation = express_getattr(IfcTaskTypeEnum, 'OPERATION', INDETERMINATE)
removal = express_getattr(IfcTaskTypeEnum, 'REMOVAL', INDETERMINATE)
renovation = express_getattr(IfcTaskTypeEnum, 'RENOVATION', INDETERMINATE)
userdefined = express_getattr(IfcTaskTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcTaskTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcTendonAnchorTypeEnum = enum_namespace()
coupler = express_getattr(IfcTendonAnchorTypeEnum, 'COUPLER', INDETERMINATE)
fixed_end = express_getattr(IfcTendonAnchorTypeEnum, 'FIXED_END', INDETERMINATE)
tensioning_end = express_getattr(IfcTendonAnchorTypeEnum, 'TENSIONING_END', INDETERMINATE)
userdefined = express_getattr(IfcTendonAnchorTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcTendonAnchorTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcTendonConduitTypeEnum = enum_namespace()
duct = express_getattr(IfcTendonConduitTypeEnum, 'DUCT', INDETERMINATE)
coupler = express_getattr(IfcTendonConduitTypeEnum, 'COUPLER', INDETERMINATE)
grouting_duct = express_getattr(IfcTendonConduitTypeEnum, 'GROUTING_DUCT', INDETERMINATE)
trumpet = express_getattr(IfcTendonConduitTypeEnum, 'TRUMPET', INDETERMINATE)
diabolo = express_getattr(IfcTendonConduitTypeEnum, 'DIABOLO', INDETERMINATE)
userdefined = express_getattr(IfcTendonConduitTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcTendonConduitTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcTendonTypeEnum = enum_namespace()
bar = express_getattr(IfcTendonTypeEnum, 'BAR', INDETERMINATE)
coated = express_getattr(IfcTendonTypeEnum, 'COATED', INDETERMINATE)
strand = express_getattr(IfcTendonTypeEnum, 'STRAND', INDETERMINATE)
wire = express_getattr(IfcTendonTypeEnum, 'WIRE', INDETERMINATE)
userdefined = express_getattr(IfcTendonTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcTendonTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcTextPath = enum_namespace()
left = express_getattr(IfcTextPath, 'LEFT', INDETERMINATE)
right = express_getattr(IfcTextPath, 'RIGHT', INDETERMINATE)
up = express_getattr(IfcTextPath, 'UP', INDETERMINATE)
down = express_getattr(IfcTextPath, 'DOWN', INDETERMINATE)
IfcTimeSeriesDataTypeEnum = enum_namespace()
continuous = express_getattr(IfcTimeSeriesDataTypeEnum, 'CONTINUOUS', INDETERMINATE)
discrete = express_getattr(IfcTimeSeriesDataTypeEnum, 'DISCRETE', INDETERMINATE)
discretebinary = express_getattr(IfcTimeSeriesDataTypeEnum, 'DISCRETEBINARY', INDETERMINATE)
piecewisebinary = express_getattr(IfcTimeSeriesDataTypeEnum, 'PIECEWISEBINARY', INDETERMINATE)
piecewiseconstant = express_getattr(IfcTimeSeriesDataTypeEnum, 'PIECEWISECONSTANT', INDETERMINATE)
piecewisecontinuous = express_getattr(IfcTimeSeriesDataTypeEnum, 'PIECEWISECONTINUOUS', INDETERMINATE)
notdefined = express_getattr(IfcTimeSeriesDataTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcTrackElementTypeEnum = enum_namespace()
trackendofalignment = express_getattr(IfcTrackElementTypeEnum, 'TRACKENDOFALIGNMENT', INDETERMINATE)
blockingdevice = express_getattr(IfcTrackElementTypeEnum, 'BLOCKINGDEVICE', INDETERMINATE)
vehiclestop = express_getattr(IfcTrackElementTypeEnum, 'VEHICLESTOP', INDETERMINATE)
sleeper = express_getattr(IfcTrackElementTypeEnum, 'SLEEPER', INDETERMINATE)
half_set_of_blades = express_getattr(IfcTrackElementTypeEnum, 'HALF_SET_OF_BLADES', INDETERMINATE)
speedregulator = express_getattr(IfcTrackElementTypeEnum, 'SPEEDREGULATOR', INDETERMINATE)
derailer = express_getattr(IfcTrackElementTypeEnum, 'DERAILER', INDETERMINATE)
frog = express_getattr(IfcTrackElementTypeEnum, 'FROG', INDETERMINATE)
userdefined = express_getattr(IfcTrackElementTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcTrackElementTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcTransformerTypeEnum = enum_namespace()
current = express_getattr(IfcTransformerTypeEnum, 'CURRENT', INDETERMINATE)
frequency = express_getattr(IfcTransformerTypeEnum, 'FREQUENCY', INDETERMINATE)
inverter = express_getattr(IfcTransformerTypeEnum, 'INVERTER', INDETERMINATE)
rectifier = express_getattr(IfcTransformerTypeEnum, 'RECTIFIER', INDETERMINATE)
voltage = express_getattr(IfcTransformerTypeEnum, 'VOLTAGE', INDETERMINATE)
chopper = express_getattr(IfcTransformerTypeEnum, 'CHOPPER', INDETERMINATE)
combined = express_getattr(IfcTransformerTypeEnum, 'COMBINED', INDETERMINATE)
userdefined = express_getattr(IfcTransformerTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcTransformerTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcTransitionCode = enum_namespace()
discontinuous = express_getattr(IfcTransitionCode, 'DISCONTINUOUS', INDETERMINATE)
continuous = express_getattr(IfcTransitionCode, 'CONTINUOUS', INDETERMINATE)
contsamegradient = express_getattr(IfcTransitionCode, 'CONTSAMEGRADIENT', INDETERMINATE)
contsamegradientsamecurvature = express_getattr(IfcTransitionCode, 'CONTSAMEGRADIENTSAMECURVATURE', INDETERMINATE)
IfcTransportElementFixedTypeEnum = enum_namespace()
elevator = express_getattr(IfcTransportElementFixedTypeEnum, 'ELEVATOR', INDETERMINATE)
escalator = express_getattr(IfcTransportElementFixedTypeEnum, 'ESCALATOR', INDETERMINATE)
movingwalkway = express_getattr(IfcTransportElementFixedTypeEnum, 'MOVINGWALKWAY', INDETERMINATE)
craneway = express_getattr(IfcTransportElementFixedTypeEnum, 'CRANEWAY', INDETERMINATE)
liftinggear = express_getattr(IfcTransportElementFixedTypeEnum, 'LIFTINGGEAR', INDETERMINATE)
haulinggear = express_getattr(IfcTransportElementFixedTypeEnum, 'HAULINGGEAR', INDETERMINATE)
userdefined = express_getattr(IfcTransportElementFixedTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcTransportElementFixedTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcTransportElementNonFixedTypeEnum = enum_namespace()
vehicle = express_getattr(IfcTransportElementNonFixedTypeEnum, 'VEHICLE', INDETERMINATE)
vehicletracked = express_getattr(IfcTransportElementNonFixedTypeEnum, 'VEHICLETRACKED', INDETERMINATE)
rollingstock = express_getattr(IfcTransportElementNonFixedTypeEnum, 'ROLLINGSTOCK', INDETERMINATE)
vehiclewheeled = express_getattr(IfcTransportElementNonFixedTypeEnum, 'VEHICLEWHEELED', INDETERMINATE)
vehicleair = express_getattr(IfcTransportElementNonFixedTypeEnum, 'VEHICLEAIR', INDETERMINATE)
cargo = express_getattr(IfcTransportElementNonFixedTypeEnum, 'CARGO', INDETERMINATE)
vehiclemarine = express_getattr(IfcTransportElementNonFixedTypeEnum, 'VEHICLEMARINE', INDETERMINATE)
userdefined = express_getattr(IfcTransportElementNonFixedTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcTransportElementNonFixedTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcTrimmingPreference = enum_namespace()
cartesian = express_getattr(IfcTrimmingPreference, 'CARTESIAN', INDETERMINATE)
parameter = express_getattr(IfcTrimmingPreference, 'PARAMETER', INDETERMINATE)
unspecified = express_getattr(IfcTrimmingPreference, 'UNSPECIFIED', INDETERMINATE)
IfcTubeBundleTypeEnum = enum_namespace()
finned = express_getattr(IfcTubeBundleTypeEnum, 'FINNED', INDETERMINATE)
userdefined = express_getattr(IfcTubeBundleTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcTubeBundleTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcUnitEnum = enum_namespace()
absorbeddoseunit = express_getattr(IfcUnitEnum, 'ABSORBEDDOSEUNIT', INDETERMINATE)
amountofsubstanceunit = express_getattr(IfcUnitEnum, 'AMOUNTOFSUBSTANCEUNIT', INDETERMINATE)
areaunit = express_getattr(IfcUnitEnum, 'AREAUNIT', INDETERMINATE)
doseequivalentunit = express_getattr(IfcUnitEnum, 'DOSEEQUIVALENTUNIT', INDETERMINATE)
electriccapacitanceunit = express_getattr(IfcUnitEnum, 'ELECTRICCAPACITANCEUNIT', INDETERMINATE)
electricchargeunit = express_getattr(IfcUnitEnum, 'ELECTRICCHARGEUNIT', INDETERMINATE)
electricconductanceunit = express_getattr(IfcUnitEnum, 'ELECTRICCONDUCTANCEUNIT', INDETERMINATE)
electriccurrentunit = express_getattr(IfcUnitEnum, 'ELECTRICCURRENTUNIT', INDETERMINATE)
electricresistanceunit = express_getattr(IfcUnitEnum, 'ELECTRICRESISTANCEUNIT', INDETERMINATE)
electricvoltageunit = express_getattr(IfcUnitEnum, 'ELECTRICVOLTAGEUNIT', INDETERMINATE)
energyunit = express_getattr(IfcUnitEnum, 'ENERGYUNIT', INDETERMINATE)
forceunit = express_getattr(IfcUnitEnum, 'FORCEUNIT', INDETERMINATE)
frequencyunit = express_getattr(IfcUnitEnum, 'FREQUENCYUNIT', INDETERMINATE)
illuminanceunit = express_getattr(IfcUnitEnum, 'ILLUMINANCEUNIT', INDETERMINATE)
inductanceunit = express_getattr(IfcUnitEnum, 'INDUCTANCEUNIT', INDETERMINATE)
lengthunit = express_getattr(IfcUnitEnum, 'LENGTHUNIT', INDETERMINATE)
luminousfluxunit = express_getattr(IfcUnitEnum, 'LUMINOUSFLUXUNIT', INDETERMINATE)
luminousintensityunit = express_getattr(IfcUnitEnum, 'LUMINOUSINTENSITYUNIT', INDETERMINATE)
magneticfluxdensityunit = express_getattr(IfcUnitEnum, 'MAGNETICFLUXDENSITYUNIT', INDETERMINATE)
magneticfluxunit = express_getattr(IfcUnitEnum, 'MAGNETICFLUXUNIT', INDETERMINATE)
massunit = express_getattr(IfcUnitEnum, 'MASSUNIT', INDETERMINATE)
planeangleunit = express_getattr(IfcUnitEnum, 'PLANEANGLEUNIT', INDETERMINATE)
powerunit = express_getattr(IfcUnitEnum, 'POWERUNIT', INDETERMINATE)
pressureunit = express_getattr(IfcUnitEnum, 'PRESSUREUNIT', INDETERMINATE)
radioactivityunit = express_getattr(IfcUnitEnum, 'RADIOACTIVITYUNIT', INDETERMINATE)
solidangleunit = express_getattr(IfcUnitEnum, 'SOLIDANGLEUNIT', INDETERMINATE)
thermodynamictemperatureunit = express_getattr(IfcUnitEnum, 'THERMODYNAMICTEMPERATUREUNIT', INDETERMINATE)
timeunit = express_getattr(IfcUnitEnum, 'TIMEUNIT', INDETERMINATE)
volumeunit = express_getattr(IfcUnitEnum, 'VOLUMEUNIT', INDETERMINATE)
userdefined = express_getattr(IfcUnitEnum, 'USERDEFINED', INDETERMINATE)
IfcUnitaryControlElementTypeEnum = enum_namespace()
alarmpanel = express_getattr(IfcUnitaryControlElementTypeEnum, 'ALARMPANEL', INDETERMINATE)
controlpanel = express_getattr(IfcUnitaryControlElementTypeEnum, 'CONTROLPANEL', INDETERMINATE)
gasdetectionpanel = express_getattr(IfcUnitaryControlElementTypeEnum, 'GASDETECTIONPANEL', INDETERMINATE)
indicatorpanel = express_getattr(IfcUnitaryControlElementTypeEnum, 'INDICATORPANEL', INDETERMINATE)
mimicpanel = express_getattr(IfcUnitaryControlElementTypeEnum, 'MIMICPANEL', INDETERMINATE)
humidistat = express_getattr(IfcUnitaryControlElementTypeEnum, 'HUMIDISTAT', INDETERMINATE)
thermostat = express_getattr(IfcUnitaryControlElementTypeEnum, 'THERMOSTAT', INDETERMINATE)
weatherstation = express_getattr(IfcUnitaryControlElementTypeEnum, 'WEATHERSTATION', INDETERMINATE)
combined = express_getattr(IfcUnitaryControlElementTypeEnum, 'COMBINED', INDETERMINATE)
basestationcontroller = express_getattr(IfcUnitaryControlElementTypeEnum, 'BASESTATIONCONTROLLER', INDETERMINATE)
userdefined = express_getattr(IfcUnitaryControlElementTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcUnitaryControlElementTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcUnitaryEquipmentTypeEnum = enum_namespace()
airhandler = express_getattr(IfcUnitaryEquipmentTypeEnum, 'AIRHANDLER', INDETERMINATE)
airconditioningunit = express_getattr(IfcUnitaryEquipmentTypeEnum, 'AIRCONDITIONINGUNIT', INDETERMINATE)
dehumidifier = express_getattr(IfcUnitaryEquipmentTypeEnum, 'DEHUMIDIFIER', INDETERMINATE)
splitsystem = express_getattr(IfcUnitaryEquipmentTypeEnum, 'SPLITSYSTEM', INDETERMINATE)
rooftopunit = express_getattr(IfcUnitaryEquipmentTypeEnum, 'ROOFTOPUNIT', INDETERMINATE)
userdefined = express_getattr(IfcUnitaryEquipmentTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcUnitaryEquipmentTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcValveTypeEnum = enum_namespace()
airrelease = express_getattr(IfcValveTypeEnum, 'AIRRELEASE', INDETERMINATE)
antivacuum = express_getattr(IfcValveTypeEnum, 'ANTIVACUUM', INDETERMINATE)
changeover = express_getattr(IfcValveTypeEnum, 'CHANGEOVER', INDETERMINATE)
check = express_getattr(IfcValveTypeEnum, 'CHECK', INDETERMINATE)
commissioning = express_getattr(IfcValveTypeEnum, 'COMMISSIONING', INDETERMINATE)
diverting = express_getattr(IfcValveTypeEnum, 'DIVERTING', INDETERMINATE)
drawoffcock = express_getattr(IfcValveTypeEnum, 'DRAWOFFCOCK', INDETERMINATE)
doublecheck = express_getattr(IfcValveTypeEnum, 'DOUBLECHECK', INDETERMINATE)
doubleregulating = express_getattr(IfcValveTypeEnum, 'DOUBLEREGULATING', INDETERMINATE)
faucet = express_getattr(IfcValveTypeEnum, 'FAUCET', INDETERMINATE)
flushing = express_getattr(IfcValveTypeEnum, 'FLUSHING', INDETERMINATE)
gascock = express_getattr(IfcValveTypeEnum, 'GASCOCK', INDETERMINATE)
gastap = express_getattr(IfcValveTypeEnum, 'GASTAP', INDETERMINATE)
isolating = express_getattr(IfcValveTypeEnum, 'ISOLATING', INDETERMINATE)
mixing = express_getattr(IfcValveTypeEnum, 'MIXING', INDETERMINATE)
pressurereducing = express_getattr(IfcValveTypeEnum, 'PRESSUREREDUCING', INDETERMINATE)
pressurerelief = express_getattr(IfcValveTypeEnum, 'PRESSURERELIEF', INDETERMINATE)
regulating = express_getattr(IfcValveTypeEnum, 'REGULATING', INDETERMINATE)
safetycutoff = express_getattr(IfcValveTypeEnum, 'SAFETYCUTOFF', INDETERMINATE)
steamtrap = express_getattr(IfcValveTypeEnum, 'STEAMTRAP', INDETERMINATE)
stopcock = express_getattr(IfcValveTypeEnum, 'STOPCOCK', INDETERMINATE)
userdefined = express_getattr(IfcValveTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcValveTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcVibrationDamperTypeEnum = enum_namespace()
bending_yield = express_getattr(IfcVibrationDamperTypeEnum, 'BENDING_YIELD', INDETERMINATE)
shear_yield = express_getattr(IfcVibrationDamperTypeEnum, 'SHEAR_YIELD', INDETERMINATE)
axial_yield = express_getattr(IfcVibrationDamperTypeEnum, 'AXIAL_YIELD', INDETERMINATE)
friction = express_getattr(IfcVibrationDamperTypeEnum, 'FRICTION', INDETERMINATE)
viscous = express_getattr(IfcVibrationDamperTypeEnum, 'VISCOUS', INDETERMINATE)
rubber = express_getattr(IfcVibrationDamperTypeEnum, 'RUBBER', INDETERMINATE)
userdefined = express_getattr(IfcVibrationDamperTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcVibrationDamperTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcVibrationIsolatorTypeEnum = enum_namespace()
compression = express_getattr(IfcVibrationIsolatorTypeEnum, 'COMPRESSION', INDETERMINATE)
spring = express_getattr(IfcVibrationIsolatorTypeEnum, 'SPRING', INDETERMINATE)
base = express_getattr(IfcVibrationIsolatorTypeEnum, 'BASE', INDETERMINATE)
userdefined = express_getattr(IfcVibrationIsolatorTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcVibrationIsolatorTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcVoidingFeatureTypeEnum = enum_namespace()
cutout = express_getattr(IfcVoidingFeatureTypeEnum, 'CUTOUT', INDETERMINATE)
notch = express_getattr(IfcVoidingFeatureTypeEnum, 'NOTCH', INDETERMINATE)
hole = express_getattr(IfcVoidingFeatureTypeEnum, 'HOLE', INDETERMINATE)
miter = express_getattr(IfcVoidingFeatureTypeEnum, 'MITER', INDETERMINATE)
chamfer = express_getattr(IfcVoidingFeatureTypeEnum, 'CHAMFER', INDETERMINATE)
edge = express_getattr(IfcVoidingFeatureTypeEnum, 'EDGE', INDETERMINATE)
userdefined = express_getattr(IfcVoidingFeatureTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcVoidingFeatureTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcWallTypeEnum = enum_namespace()
movable = express_getattr(IfcWallTypeEnum, 'MOVABLE', INDETERMINATE)
parapet = express_getattr(IfcWallTypeEnum, 'PARAPET', INDETERMINATE)
partitioning = express_getattr(IfcWallTypeEnum, 'PARTITIONING', INDETERMINATE)
plumbingwall = express_getattr(IfcWallTypeEnum, 'PLUMBINGWALL', INDETERMINATE)
shear = express_getattr(IfcWallTypeEnum, 'SHEAR', INDETERMINATE)
solidwall = express_getattr(IfcWallTypeEnum, 'SOLIDWALL', INDETERMINATE)
standard = express_getattr(IfcWallTypeEnum, 'STANDARD', INDETERMINATE)
polygonal = express_getattr(IfcWallTypeEnum, 'POLYGONAL', INDETERMINATE)
elementedwall = express_getattr(IfcWallTypeEnum, 'ELEMENTEDWALL', INDETERMINATE)
retainingwall = express_getattr(IfcWallTypeEnum, 'RETAININGWALL', INDETERMINATE)
wavewall = express_getattr(IfcWallTypeEnum, 'WAVEWALL', INDETERMINATE)
userdefined = express_getattr(IfcWallTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcWallTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcWasteTerminalTypeEnum = enum_namespace()
floortrap = express_getattr(IfcWasteTerminalTypeEnum, 'FLOORTRAP', INDETERMINATE)
floorwaste = express_getattr(IfcWasteTerminalTypeEnum, 'FLOORWASTE', INDETERMINATE)
gullysump = express_getattr(IfcWasteTerminalTypeEnum, 'GULLYSUMP', INDETERMINATE)
gullytrap = express_getattr(IfcWasteTerminalTypeEnum, 'GULLYTRAP', INDETERMINATE)
roofdrain = express_getattr(IfcWasteTerminalTypeEnum, 'ROOFDRAIN', INDETERMINATE)
wastedisposalunit = express_getattr(IfcWasteTerminalTypeEnum, 'WASTEDISPOSALUNIT', INDETERMINATE)
wastetrap = express_getattr(IfcWasteTerminalTypeEnum, 'WASTETRAP', INDETERMINATE)
userdefined = express_getattr(IfcWasteTerminalTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcWasteTerminalTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcWindowPanelOperationEnum = enum_namespace()
sidehungrighthand = express_getattr(IfcWindowPanelOperationEnum, 'SIDEHUNGRIGHTHAND', INDETERMINATE)
sidehunglefthand = express_getattr(IfcWindowPanelOperationEnum, 'SIDEHUNGLEFTHAND', INDETERMINATE)
tiltandturnrighthand = express_getattr(IfcWindowPanelOperationEnum, 'TILTANDTURNRIGHTHAND', INDETERMINATE)
tiltandturnlefthand = express_getattr(IfcWindowPanelOperationEnum, 'TILTANDTURNLEFTHAND', INDETERMINATE)
tophung = express_getattr(IfcWindowPanelOperationEnum, 'TOPHUNG', INDETERMINATE)
bottomhung = express_getattr(IfcWindowPanelOperationEnum, 'BOTTOMHUNG', INDETERMINATE)
pivothorizontal = express_getattr(IfcWindowPanelOperationEnum, 'PIVOTHORIZONTAL', INDETERMINATE)
pivotvertical = express_getattr(IfcWindowPanelOperationEnum, 'PIVOTVERTICAL', INDETERMINATE)
slidinghorizontal = express_getattr(IfcWindowPanelOperationEnum, 'SLIDINGHORIZONTAL', INDETERMINATE)
slidingvertical = express_getattr(IfcWindowPanelOperationEnum, 'SLIDINGVERTICAL', INDETERMINATE)
removablecasement = express_getattr(IfcWindowPanelOperationEnum, 'REMOVABLECASEMENT', INDETERMINATE)
fixedcasement = express_getattr(IfcWindowPanelOperationEnum, 'FIXEDCASEMENT', INDETERMINATE)
otheroperation = express_getattr(IfcWindowPanelOperationEnum, 'OTHEROPERATION', INDETERMINATE)
notdefined = express_getattr(IfcWindowPanelOperationEnum, 'NOTDEFINED', INDETERMINATE)
IfcWindowPanelPositionEnum = enum_namespace()
left = express_getattr(IfcWindowPanelPositionEnum, 'LEFT', INDETERMINATE)
middle = express_getattr(IfcWindowPanelPositionEnum, 'MIDDLE', INDETERMINATE)
right = express_getattr(IfcWindowPanelPositionEnum, 'RIGHT', INDETERMINATE)
bottom = express_getattr(IfcWindowPanelPositionEnum, 'BOTTOM', INDETERMINATE)
top = express_getattr(IfcWindowPanelPositionEnum, 'TOP', INDETERMINATE)
notdefined = express_getattr(IfcWindowPanelPositionEnum, 'NOTDEFINED', INDETERMINATE)
IfcWindowStyleConstructionEnum = enum_namespace()
aluminium = express_getattr(IfcWindowStyleConstructionEnum, 'ALUMINIUM', INDETERMINATE)
high_grade_steel = express_getattr(IfcWindowStyleConstructionEnum, 'HIGH_GRADE_STEEL', INDETERMINATE)
steel = express_getattr(IfcWindowStyleConstructionEnum, 'STEEL', INDETERMINATE)
wood = express_getattr(IfcWindowStyleConstructionEnum, 'WOOD', INDETERMINATE)
aluminium_wood = express_getattr(IfcWindowStyleConstructionEnum, 'ALUMINIUM_WOOD', INDETERMINATE)
plastic = express_getattr(IfcWindowStyleConstructionEnum, 'PLASTIC', INDETERMINATE)
other_construction = express_getattr(IfcWindowStyleConstructionEnum, 'OTHER_CONSTRUCTION', INDETERMINATE)
notdefined = express_getattr(IfcWindowStyleConstructionEnum, 'NOTDEFINED', INDETERMINATE)
IfcWindowStyleOperationEnum = enum_namespace()
single_panel = express_getattr(IfcWindowStyleOperationEnum, 'SINGLE_PANEL', INDETERMINATE)
double_panel_vertical = express_getattr(IfcWindowStyleOperationEnum, 'DOUBLE_PANEL_VERTICAL', INDETERMINATE)
double_panel_horizontal = express_getattr(IfcWindowStyleOperationEnum, 'DOUBLE_PANEL_HORIZONTAL', INDETERMINATE)
triple_panel_vertical = express_getattr(IfcWindowStyleOperationEnum, 'TRIPLE_PANEL_VERTICAL', INDETERMINATE)
triple_panel_bottom = express_getattr(IfcWindowStyleOperationEnum, 'TRIPLE_PANEL_BOTTOM', INDETERMINATE)
triple_panel_top = express_getattr(IfcWindowStyleOperationEnum, 'TRIPLE_PANEL_TOP', INDETERMINATE)
triple_panel_left = express_getattr(IfcWindowStyleOperationEnum, 'TRIPLE_PANEL_LEFT', INDETERMINATE)
triple_panel_right = express_getattr(IfcWindowStyleOperationEnum, 'TRIPLE_PANEL_RIGHT', INDETERMINATE)
triple_panel_horizontal = express_getattr(IfcWindowStyleOperationEnum, 'TRIPLE_PANEL_HORIZONTAL', INDETERMINATE)
userdefined = express_getattr(IfcWindowStyleOperationEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcWindowStyleOperationEnum, 'NOTDEFINED', INDETERMINATE)
IfcWindowTypeEnum = enum_namespace()
window = express_getattr(IfcWindowTypeEnum, 'WINDOW', INDETERMINATE)
skylight = express_getattr(IfcWindowTypeEnum, 'SKYLIGHT', INDETERMINATE)
lightdome = express_getattr(IfcWindowTypeEnum, 'LIGHTDOME', INDETERMINATE)
userdefined = express_getattr(IfcWindowTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcWindowTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcWindowTypePartitioningEnum = enum_namespace()
single_panel = express_getattr(IfcWindowTypePartitioningEnum, 'SINGLE_PANEL', INDETERMINATE)
double_panel_vertical = express_getattr(IfcWindowTypePartitioningEnum, 'DOUBLE_PANEL_VERTICAL', INDETERMINATE)
double_panel_horizontal = express_getattr(IfcWindowTypePartitioningEnum, 'DOUBLE_PANEL_HORIZONTAL', INDETERMINATE)
triple_panel_vertical = express_getattr(IfcWindowTypePartitioningEnum, 'TRIPLE_PANEL_VERTICAL', INDETERMINATE)
triple_panel_bottom = express_getattr(IfcWindowTypePartitioningEnum, 'TRIPLE_PANEL_BOTTOM', INDETERMINATE)
triple_panel_top = express_getattr(IfcWindowTypePartitioningEnum, 'TRIPLE_PANEL_TOP', INDETERMINATE)
triple_panel_left = express_getattr(IfcWindowTypePartitioningEnum, 'TRIPLE_PANEL_LEFT', INDETERMINATE)
triple_panel_right = express_getattr(IfcWindowTypePartitioningEnum, 'TRIPLE_PANEL_RIGHT', INDETERMINATE)
triple_panel_horizontal = express_getattr(IfcWindowTypePartitioningEnum, 'TRIPLE_PANEL_HORIZONTAL', INDETERMINATE)
userdefined = express_getattr(IfcWindowTypePartitioningEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcWindowTypePartitioningEnum, 'NOTDEFINED', INDETERMINATE)
IfcWorkCalendarTypeEnum = enum_namespace()
firstshift = express_getattr(IfcWorkCalendarTypeEnum, 'FIRSTSHIFT', INDETERMINATE)
secondshift = express_getattr(IfcWorkCalendarTypeEnum, 'SECONDSHIFT', INDETERMINATE)
thirdshift = express_getattr(IfcWorkCalendarTypeEnum, 'THIRDSHIFT', INDETERMINATE)
userdefined = express_getattr(IfcWorkCalendarTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcWorkCalendarTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcWorkPlanTypeEnum = enum_namespace()
actual = express_getattr(IfcWorkPlanTypeEnum, 'ACTUAL', INDETERMINATE)
baseline = express_getattr(IfcWorkPlanTypeEnum, 'BASELINE', INDETERMINATE)
planned = express_getattr(IfcWorkPlanTypeEnum, 'PLANNED', INDETERMINATE)
userdefined = express_getattr(IfcWorkPlanTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcWorkPlanTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcWorkScheduleTypeEnum = enum_namespace()
actual = express_getattr(IfcWorkScheduleTypeEnum, 'ACTUAL', INDETERMINATE)
baseline = express_getattr(IfcWorkScheduleTypeEnum, 'BASELINE', INDETERMINATE)
planned = express_getattr(IfcWorkScheduleTypeEnum, 'PLANNED', INDETERMINATE)
userdefined = express_getattr(IfcWorkScheduleTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = express_getattr(IfcWorkScheduleTypeEnum, 'NOTDEFINED', INDETERMINATE)

def IfcActionRequest(*args, **kwargs):
    return ifcopenshell.create_entity('IfcActionRequest', 'IFC4X3_RC4', *args, **kwargs)

def IfcActor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcActor', 'IFC4X3_RC4', *args, **kwargs)

def IfcActorRole(*args, **kwargs):
    return ifcopenshell.create_entity('IfcActorRole', 'IFC4X3_RC4', *args, **kwargs)

def IfcActuator(*args, **kwargs):
    return ifcopenshell.create_entity('IfcActuator', 'IFC4X3_RC4', *args, **kwargs)

def IfcActuatorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcActuatorType', 'IFC4X3_RC4', *args, **kwargs)

def IfcAddress(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAddress', 'IFC4X3_RC4', *args, **kwargs)

def IfcAdvancedBrep(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAdvancedBrep', 'IFC4X3_RC4', *args, **kwargs)

def IfcAdvancedBrepWithVoids(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAdvancedBrepWithVoids', 'IFC4X3_RC4', *args, **kwargs)

def IfcAdvancedFace(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAdvancedFace', 'IFC4X3_RC4', *args, **kwargs)

def IfcAirTerminal(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAirTerminal', 'IFC4X3_RC4', *args, **kwargs)

def IfcAirTerminalBox(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAirTerminalBox', 'IFC4X3_RC4', *args, **kwargs)

def IfcAirTerminalBoxType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAirTerminalBoxType', 'IFC4X3_RC4', *args, **kwargs)

def IfcAirTerminalType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAirTerminalType', 'IFC4X3_RC4', *args, **kwargs)

def IfcAirToAirHeatRecovery(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAirToAirHeatRecovery', 'IFC4X3_RC4', *args, **kwargs)

def IfcAirToAirHeatRecoveryType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAirToAirHeatRecoveryType', 'IFC4X3_RC4', *args, **kwargs)

def IfcAlarm(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlarm', 'IFC4X3_RC4', *args, **kwargs)

def IfcAlarmType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlarmType', 'IFC4X3_RC4', *args, **kwargs)

def IfcAlignment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlignment', 'IFC4X3_RC4', *args, **kwargs)

def IfcAlignmentCant(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlignmentCant', 'IFC4X3_RC4', *args, **kwargs)

def IfcAlignmentCantSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlignmentCantSegment', 'IFC4X3_RC4', *args, **kwargs)

def IfcAlignmentHorizontal(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlignmentHorizontal', 'IFC4X3_RC4', *args, **kwargs)

def IfcAlignmentHorizontalSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlignmentHorizontalSegment', 'IFC4X3_RC4', *args, **kwargs)

def IfcAlignmentParameterSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlignmentParameterSegment', 'IFC4X3_RC4', *args, **kwargs)

def IfcAlignmentSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlignmentSegment', 'IFC4X3_RC4', *args, **kwargs)

def IfcAlignmentVertical(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlignmentVertical', 'IFC4X3_RC4', *args, **kwargs)

def IfcAlignmentVerticalSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlignmentVerticalSegment', 'IFC4X3_RC4', *args, **kwargs)

def IfcAnnotation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAnnotation', 'IFC4X3_RC4', *args, **kwargs)

def IfcAnnotationFillArea(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAnnotationFillArea', 'IFC4X3_RC4', *args, **kwargs)

def IfcApplication(*args, **kwargs):
    return ifcopenshell.create_entity('IfcApplication', 'IFC4X3_RC4', *args, **kwargs)

def IfcAppliedValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAppliedValue', 'IFC4X3_RC4', *args, **kwargs)

def IfcApproval(*args, **kwargs):
    return ifcopenshell.create_entity('IfcApproval', 'IFC4X3_RC4', *args, **kwargs)

def IfcApprovalRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcApprovalRelationship', 'IFC4X3_RC4', *args, **kwargs)

def IfcArbitraryClosedProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcArbitraryClosedProfileDef', 'IFC4X3_RC4', *args, **kwargs)

def IfcArbitraryOpenProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcArbitraryOpenProfileDef', 'IFC4X3_RC4', *args, **kwargs)

def IfcArbitraryProfileDefWithVoids(*args, **kwargs):
    return ifcopenshell.create_entity('IfcArbitraryProfileDefWithVoids', 'IFC4X3_RC4', *args, **kwargs)

def IfcAsset(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAsset', 'IFC4X3_RC4', *args, **kwargs)

def IfcAsymmetricIShapeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAsymmetricIShapeProfileDef', 'IFC4X3_RC4', *args, **kwargs)

def IfcAudioVisualAppliance(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAudioVisualAppliance', 'IFC4X3_RC4', *args, **kwargs)

def IfcAudioVisualApplianceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAudioVisualApplianceType', 'IFC4X3_RC4', *args, **kwargs)

def IfcAxis1Placement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAxis1Placement', 'IFC4X3_RC4', *args, **kwargs)

def IfcAxis2Placement2D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAxis2Placement2D', 'IFC4X3_RC4', *args, **kwargs)

def IfcAxis2Placement3D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAxis2Placement3D', 'IFC4X3_RC4', *args, **kwargs)

def IfcAxis2PlacementLinear(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAxis2PlacementLinear', 'IFC4X3_RC4', *args, **kwargs)

def IfcBSplineCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBSplineCurve', 'IFC4X3_RC4', *args, **kwargs)

def IfcBSplineCurveWithKnots(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBSplineCurveWithKnots', 'IFC4X3_RC4', *args, **kwargs)

def IfcBSplineSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBSplineSurface', 'IFC4X3_RC4', *args, **kwargs)

def IfcBSplineSurfaceWithKnots(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBSplineSurfaceWithKnots', 'IFC4X3_RC4', *args, **kwargs)

def IfcBeam(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBeam', 'IFC4X3_RC4', *args, **kwargs)

def IfcBeamStandardCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBeamStandardCase', 'IFC4X3_RC4', *args, **kwargs)

def IfcBeamType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBeamType', 'IFC4X3_RC4', *args, **kwargs)

def IfcBearing(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBearing', 'IFC4X3_RC4', *args, **kwargs)

def IfcBearingType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBearingType', 'IFC4X3_RC4', *args, **kwargs)

def IfcBlobTexture(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBlobTexture', 'IFC4X3_RC4', *args, **kwargs)

def IfcBlock(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBlock', 'IFC4X3_RC4', *args, **kwargs)

def IfcBoiler(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoiler', 'IFC4X3_RC4', *args, **kwargs)

def IfcBoilerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoilerType', 'IFC4X3_RC4', *args, **kwargs)

def IfcBooleanClippingResult(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBooleanClippingResult', 'IFC4X3_RC4', *args, **kwargs)

def IfcBooleanResult(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBooleanResult', 'IFC4X3_RC4', *args, **kwargs)

def IfcBorehole(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBorehole', 'IFC4X3_RC4', *args, **kwargs)

def IfcBoundaryCondition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundaryCondition', 'IFC4X3_RC4', *args, **kwargs)

def IfcBoundaryCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundaryCurve', 'IFC4X3_RC4', *args, **kwargs)

def IfcBoundaryEdgeCondition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundaryEdgeCondition', 'IFC4X3_RC4', *args, **kwargs)

def IfcBoundaryFaceCondition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundaryFaceCondition', 'IFC4X3_RC4', *args, **kwargs)

def IfcBoundaryNodeCondition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundaryNodeCondition', 'IFC4X3_RC4', *args, **kwargs)

def IfcBoundaryNodeConditionWarping(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundaryNodeConditionWarping', 'IFC4X3_RC4', *args, **kwargs)

def IfcBoundedCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundedCurve', 'IFC4X3_RC4', *args, **kwargs)

def IfcBoundedSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundedSurface', 'IFC4X3_RC4', *args, **kwargs)

def IfcBoundingBox(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundingBox', 'IFC4X3_RC4', *args, **kwargs)

def IfcBoxedHalfSpace(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoxedHalfSpace', 'IFC4X3_RC4', *args, **kwargs)

def IfcBridge(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBridge', 'IFC4X3_RC4', *args, **kwargs)

def IfcBuilding(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuilding', 'IFC4X3_RC4', *args, **kwargs)

def IfcBuildingElementPart(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuildingElementPart', 'IFC4X3_RC4', *args, **kwargs)

def IfcBuildingElementPartType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuildingElementPartType', 'IFC4X3_RC4', *args, **kwargs)

def IfcBuildingElementProxy(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuildingElementProxy', 'IFC4X3_RC4', *args, **kwargs)

def IfcBuildingElementProxyType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuildingElementProxyType', 'IFC4X3_RC4', *args, **kwargs)

def IfcBuildingStorey(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuildingStorey', 'IFC4X3_RC4', *args, **kwargs)

def IfcBuildingSystem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuildingSystem', 'IFC4X3_RC4', *args, **kwargs)

def IfcBuiltElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuiltElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcBuiltElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuiltElementType', 'IFC4X3_RC4', *args, **kwargs)

def IfcBuiltSystem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuiltSystem', 'IFC4X3_RC4', *args, **kwargs)

def IfcBurner(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBurner', 'IFC4X3_RC4', *args, **kwargs)

def IfcBurnerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBurnerType', 'IFC4X3_RC4', *args, **kwargs)

def IfcCShapeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCShapeProfileDef', 'IFC4X3_RC4', *args, **kwargs)

def IfcCableCarrierFitting(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCableCarrierFitting', 'IFC4X3_RC4', *args, **kwargs)

def IfcCableCarrierFittingType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCableCarrierFittingType', 'IFC4X3_RC4', *args, **kwargs)

def IfcCableCarrierSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCableCarrierSegment', 'IFC4X3_RC4', *args, **kwargs)

def IfcCableCarrierSegmentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCableCarrierSegmentType', 'IFC4X3_RC4', *args, **kwargs)

def IfcCableFitting(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCableFitting', 'IFC4X3_RC4', *args, **kwargs)

def IfcCableFittingType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCableFittingType', 'IFC4X3_RC4', *args, **kwargs)

def IfcCableSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCableSegment', 'IFC4X3_RC4', *args, **kwargs)

def IfcCableSegmentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCableSegmentType', 'IFC4X3_RC4', *args, **kwargs)

def IfcCaissonFoundation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCaissonFoundation', 'IFC4X3_RC4', *args, **kwargs)

def IfcCaissonFoundationType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCaissonFoundationType', 'IFC4X3_RC4', *args, **kwargs)

def IfcCartesianPoint(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianPoint', 'IFC4X3_RC4', *args, **kwargs)

def IfcCartesianPointList(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianPointList', 'IFC4X3_RC4', *args, **kwargs)

def IfcCartesianPointList2D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianPointList2D', 'IFC4X3_RC4', *args, **kwargs)

def IfcCartesianPointList3D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianPointList3D', 'IFC4X3_RC4', *args, **kwargs)

def IfcCartesianTransformationOperator(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianTransformationOperator', 'IFC4X3_RC4', *args, **kwargs)

def IfcCartesianTransformationOperator2D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianTransformationOperator2D', 'IFC4X3_RC4', *args, **kwargs)

def IfcCartesianTransformationOperator2DnonUniform(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianTransformationOperator2DnonUniform', 'IFC4X3_RC4', *args, **kwargs)

def IfcCartesianTransformationOperator3D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianTransformationOperator3D', 'IFC4X3_RC4', *args, **kwargs)

def IfcCartesianTransformationOperator3DnonUniform(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianTransformationOperator3DnonUniform', 'IFC4X3_RC4', *args, **kwargs)

def IfcCenterLineProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCenterLineProfileDef', 'IFC4X3_RC4', *args, **kwargs)

def IfcChiller(*args, **kwargs):
    return ifcopenshell.create_entity('IfcChiller', 'IFC4X3_RC4', *args, **kwargs)

def IfcChillerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcChillerType', 'IFC4X3_RC4', *args, **kwargs)

def IfcChimney(*args, **kwargs):
    return ifcopenshell.create_entity('IfcChimney', 'IFC4X3_RC4', *args, **kwargs)

def IfcChimneyType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcChimneyType', 'IFC4X3_RC4', *args, **kwargs)

def IfcCircle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCircle', 'IFC4X3_RC4', *args, **kwargs)

def IfcCircleHollowProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCircleHollowProfileDef', 'IFC4X3_RC4', *args, **kwargs)

def IfcCircleProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCircleProfileDef', 'IFC4X3_RC4', *args, **kwargs)

def IfcCivilElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCivilElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcCivilElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCivilElementType', 'IFC4X3_RC4', *args, **kwargs)

def IfcClassification(*args, **kwargs):
    return ifcopenshell.create_entity('IfcClassification', 'IFC4X3_RC4', *args, **kwargs)

def IfcClassificationReference(*args, **kwargs):
    return ifcopenshell.create_entity('IfcClassificationReference', 'IFC4X3_RC4', *args, **kwargs)

def IfcClosedShell(*args, **kwargs):
    return ifcopenshell.create_entity('IfcClosedShell', 'IFC4X3_RC4', *args, **kwargs)

def IfcClothoid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcClothoid', 'IFC4X3_RC4', *args, **kwargs)

def IfcCoil(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCoil', 'IFC4X3_RC4', *args, **kwargs)

def IfcCoilType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCoilType', 'IFC4X3_RC4', *args, **kwargs)

def IfcColourRgb(*args, **kwargs):
    return ifcopenshell.create_entity('IfcColourRgb', 'IFC4X3_RC4', *args, **kwargs)

def IfcColourRgbList(*args, **kwargs):
    return ifcopenshell.create_entity('IfcColourRgbList', 'IFC4X3_RC4', *args, **kwargs)

def IfcColourSpecification(*args, **kwargs):
    return ifcopenshell.create_entity('IfcColourSpecification', 'IFC4X3_RC4', *args, **kwargs)

def IfcColumn(*args, **kwargs):
    return ifcopenshell.create_entity('IfcColumn', 'IFC4X3_RC4', *args, **kwargs)

def IfcColumnStandardCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcColumnStandardCase', 'IFC4X3_RC4', *args, **kwargs)

def IfcColumnType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcColumnType', 'IFC4X3_RC4', *args, **kwargs)

def IfcCommunicationsAppliance(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCommunicationsAppliance', 'IFC4X3_RC4', *args, **kwargs)

def IfcCommunicationsApplianceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCommunicationsApplianceType', 'IFC4X3_RC4', *args, **kwargs)

def IfcComplexProperty(*args, **kwargs):
    return ifcopenshell.create_entity('IfcComplexProperty', 'IFC4X3_RC4', *args, **kwargs)

def IfcComplexPropertyTemplate(*args, **kwargs):
    return ifcopenshell.create_entity('IfcComplexPropertyTemplate', 'IFC4X3_RC4', *args, **kwargs)

def IfcCompositeCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCompositeCurve', 'IFC4X3_RC4', *args, **kwargs)

def IfcCompositeCurveOnSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCompositeCurveOnSurface', 'IFC4X3_RC4', *args, **kwargs)

def IfcCompositeCurveSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCompositeCurveSegment', 'IFC4X3_RC4', *args, **kwargs)

def IfcCompositeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCompositeProfileDef', 'IFC4X3_RC4', *args, **kwargs)

def IfcCompressor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCompressor', 'IFC4X3_RC4', *args, **kwargs)

def IfcCompressorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCompressorType', 'IFC4X3_RC4', *args, **kwargs)

def IfcCondenser(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCondenser', 'IFC4X3_RC4', *args, **kwargs)

def IfcCondenserType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCondenserType', 'IFC4X3_RC4', *args, **kwargs)

def IfcConic(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConic', 'IFC4X3_RC4', *args, **kwargs)

def IfcConnectedFaceSet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConnectedFaceSet', 'IFC4X3_RC4', *args, **kwargs)

def IfcConnectionCurveGeometry(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConnectionCurveGeometry', 'IFC4X3_RC4', *args, **kwargs)

def IfcConnectionGeometry(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConnectionGeometry', 'IFC4X3_RC4', *args, **kwargs)

def IfcConnectionPointEccentricity(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConnectionPointEccentricity', 'IFC4X3_RC4', *args, **kwargs)

def IfcConnectionPointGeometry(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConnectionPointGeometry', 'IFC4X3_RC4', *args, **kwargs)

def IfcConnectionSurfaceGeometry(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConnectionSurfaceGeometry', 'IFC4X3_RC4', *args, **kwargs)

def IfcConnectionVolumeGeometry(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConnectionVolumeGeometry', 'IFC4X3_RC4', *args, **kwargs)

def IfcConstraint(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstraint', 'IFC4X3_RC4', *args, **kwargs)

def IfcConstructionEquipmentResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstructionEquipmentResource', 'IFC4X3_RC4', *args, **kwargs)

def IfcConstructionEquipmentResourceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstructionEquipmentResourceType', 'IFC4X3_RC4', *args, **kwargs)

def IfcConstructionMaterialResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstructionMaterialResource', 'IFC4X3_RC4', *args, **kwargs)

def IfcConstructionMaterialResourceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstructionMaterialResourceType', 'IFC4X3_RC4', *args, **kwargs)

def IfcConstructionProductResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstructionProductResource', 'IFC4X3_RC4', *args, **kwargs)

def IfcConstructionProductResourceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstructionProductResourceType', 'IFC4X3_RC4', *args, **kwargs)

def IfcConstructionResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstructionResource', 'IFC4X3_RC4', *args, **kwargs)

def IfcConstructionResourceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstructionResourceType', 'IFC4X3_RC4', *args, **kwargs)

def IfcContext(*args, **kwargs):
    return ifcopenshell.create_entity('IfcContext', 'IFC4X3_RC4', *args, **kwargs)

def IfcContextDependentUnit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcContextDependentUnit', 'IFC4X3_RC4', *args, **kwargs)

def IfcControl(*args, **kwargs):
    return ifcopenshell.create_entity('IfcControl', 'IFC4X3_RC4', *args, **kwargs)

def IfcController(*args, **kwargs):
    return ifcopenshell.create_entity('IfcController', 'IFC4X3_RC4', *args, **kwargs)

def IfcControllerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcControllerType', 'IFC4X3_RC4', *args, **kwargs)

def IfcConversionBasedUnit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConversionBasedUnit', 'IFC4X3_RC4', *args, **kwargs)

def IfcConversionBasedUnitWithOffset(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConversionBasedUnitWithOffset', 'IFC4X3_RC4', *args, **kwargs)

def IfcConveyorSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConveyorSegment', 'IFC4X3_RC4', *args, **kwargs)

def IfcConveyorSegmentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConveyorSegmentType', 'IFC4X3_RC4', *args, **kwargs)

def IfcCooledBeam(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCooledBeam', 'IFC4X3_RC4', *args, **kwargs)

def IfcCooledBeamType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCooledBeamType', 'IFC4X3_RC4', *args, **kwargs)

def IfcCoolingTower(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCoolingTower', 'IFC4X3_RC4', *args, **kwargs)

def IfcCoolingTowerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCoolingTowerType', 'IFC4X3_RC4', *args, **kwargs)

def IfcCoordinateOperation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCoordinateOperation', 'IFC4X3_RC4', *args, **kwargs)

def IfcCoordinateReferenceSystem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCoordinateReferenceSystem', 'IFC4X3_RC4', *args, **kwargs)

def IfcCosine(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCosine', 'IFC4X3_RC4', *args, **kwargs)

def IfcCostItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCostItem', 'IFC4X3_RC4', *args, **kwargs)

def IfcCostSchedule(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCostSchedule', 'IFC4X3_RC4', *args, **kwargs)

def IfcCostValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCostValue', 'IFC4X3_RC4', *args, **kwargs)

def IfcCourse(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCourse', 'IFC4X3_RC4', *args, **kwargs)

def IfcCourseType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCourseType', 'IFC4X3_RC4', *args, **kwargs)

def IfcCovering(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCovering', 'IFC4X3_RC4', *args, **kwargs)

def IfcCoveringType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCoveringType', 'IFC4X3_RC4', *args, **kwargs)

def IfcCrewResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCrewResource', 'IFC4X3_RC4', *args, **kwargs)

def IfcCrewResourceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCrewResourceType', 'IFC4X3_RC4', *args, **kwargs)

def IfcCsgPrimitive3D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCsgPrimitive3D', 'IFC4X3_RC4', *args, **kwargs)

def IfcCsgSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCsgSolid', 'IFC4X3_RC4', *args, **kwargs)

def IfcCurrencyRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurrencyRelationship', 'IFC4X3_RC4', *args, **kwargs)

def IfcCurtainWall(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurtainWall', 'IFC4X3_RC4', *args, **kwargs)

def IfcCurtainWallType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurtainWallType', 'IFC4X3_RC4', *args, **kwargs)

def IfcCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurve', 'IFC4X3_RC4', *args, **kwargs)

def IfcCurveBoundedPlane(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurveBoundedPlane', 'IFC4X3_RC4', *args, **kwargs)

def IfcCurveBoundedSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurveBoundedSurface', 'IFC4X3_RC4', *args, **kwargs)

def IfcCurveSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurveSegment', 'IFC4X3_RC4', *args, **kwargs)

def IfcCurveStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurveStyle', 'IFC4X3_RC4', *args, **kwargs)

def IfcCurveStyleFont(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurveStyleFont', 'IFC4X3_RC4', *args, **kwargs)

def IfcCurveStyleFontAndScaling(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurveStyleFontAndScaling', 'IFC4X3_RC4', *args, **kwargs)

def IfcCurveStyleFontPattern(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurveStyleFontPattern', 'IFC4X3_RC4', *args, **kwargs)

def IfcCylindricalSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCylindricalSurface', 'IFC4X3_RC4', *args, **kwargs)

def IfcDamper(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDamper', 'IFC4X3_RC4', *args, **kwargs)

def IfcDamperType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDamperType', 'IFC4X3_RC4', *args, **kwargs)

def IfcDeepFoundation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDeepFoundation', 'IFC4X3_RC4', *args, **kwargs)

def IfcDeepFoundationType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDeepFoundationType', 'IFC4X3_RC4', *args, **kwargs)

def IfcDerivedProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDerivedProfileDef', 'IFC4X3_RC4', *args, **kwargs)

def IfcDerivedUnit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDerivedUnit', 'IFC4X3_RC4', *args, **kwargs)

def IfcDerivedUnitElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDerivedUnitElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcDimensionalExponents(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDimensionalExponents', 'IFC4X3_RC4', *args, **kwargs)

def IfcDirection(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDirection', 'IFC4X3_RC4', *args, **kwargs)

def IfcDirectrixCurveSweptAreaSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDirectrixCurveSweptAreaSolid', 'IFC4X3_RC4', *args, **kwargs)

def IfcDirectrixDerivedReferenceSweptAreaSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDirectrixDerivedReferenceSweptAreaSolid', 'IFC4X3_RC4', *args, **kwargs)

def IfcDiscreteAccessory(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDiscreteAccessory', 'IFC4X3_RC4', *args, **kwargs)

def IfcDiscreteAccessoryType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDiscreteAccessoryType', 'IFC4X3_RC4', *args, **kwargs)

def IfcDistributionBoard(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionBoard', 'IFC4X3_RC4', *args, **kwargs)

def IfcDistributionBoardType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionBoardType', 'IFC4X3_RC4', *args, **kwargs)

def IfcDistributionChamberElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionChamberElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcDistributionChamberElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionChamberElementType', 'IFC4X3_RC4', *args, **kwargs)

def IfcDistributionCircuit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionCircuit', 'IFC4X3_RC4', *args, **kwargs)

def IfcDistributionControlElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionControlElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcDistributionControlElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionControlElementType', 'IFC4X3_RC4', *args, **kwargs)

def IfcDistributionElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcDistributionElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionElementType', 'IFC4X3_RC4', *args, **kwargs)

def IfcDistributionFlowElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionFlowElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcDistributionFlowElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionFlowElementType', 'IFC4X3_RC4', *args, **kwargs)

def IfcDistributionPort(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionPort', 'IFC4X3_RC4', *args, **kwargs)

def IfcDistributionSystem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionSystem', 'IFC4X3_RC4', *args, **kwargs)

def IfcDocumentInformation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDocumentInformation', 'IFC4X3_RC4', *args, **kwargs)

def IfcDocumentInformationRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDocumentInformationRelationship', 'IFC4X3_RC4', *args, **kwargs)

def IfcDocumentReference(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDocumentReference', 'IFC4X3_RC4', *args, **kwargs)

def IfcDoor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDoor', 'IFC4X3_RC4', *args, **kwargs)

def IfcDoorLiningProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDoorLiningProperties', 'IFC4X3_RC4', *args, **kwargs)

def IfcDoorPanelProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDoorPanelProperties', 'IFC4X3_RC4', *args, **kwargs)

def IfcDoorStandardCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDoorStandardCase', 'IFC4X3_RC4', *args, **kwargs)

def IfcDoorStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDoorStyle', 'IFC4X3_RC4', *args, **kwargs)

def IfcDoorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDoorType', 'IFC4X3_RC4', *args, **kwargs)

def IfcDraughtingPreDefinedColour(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDraughtingPreDefinedColour', 'IFC4X3_RC4', *args, **kwargs)

def IfcDraughtingPreDefinedCurveFont(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDraughtingPreDefinedCurveFont', 'IFC4X3_RC4', *args, **kwargs)

def IfcDuctFitting(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDuctFitting', 'IFC4X3_RC4', *args, **kwargs)

def IfcDuctFittingType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDuctFittingType', 'IFC4X3_RC4', *args, **kwargs)

def IfcDuctSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDuctSegment', 'IFC4X3_RC4', *args, **kwargs)

def IfcDuctSegmentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDuctSegmentType', 'IFC4X3_RC4', *args, **kwargs)

def IfcDuctSilencer(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDuctSilencer', 'IFC4X3_RC4', *args, **kwargs)

def IfcDuctSilencerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDuctSilencerType', 'IFC4X3_RC4', *args, **kwargs)

def IfcEarthworksCut(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEarthworksCut', 'IFC4X3_RC4', *args, **kwargs)

def IfcEarthworksElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEarthworksElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcEarthworksFill(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEarthworksFill', 'IFC4X3_RC4', *args, **kwargs)

def IfcEdge(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEdge', 'IFC4X3_RC4', *args, **kwargs)

def IfcEdgeCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEdgeCurve', 'IFC4X3_RC4', *args, **kwargs)

def IfcEdgeLoop(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEdgeLoop', 'IFC4X3_RC4', *args, **kwargs)

def IfcElectricAppliance(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricAppliance', 'IFC4X3_RC4', *args, **kwargs)

def IfcElectricApplianceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricApplianceType', 'IFC4X3_RC4', *args, **kwargs)

def IfcElectricDistributionBoard(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricDistributionBoard', 'IFC4X3_RC4', *args, **kwargs)

def IfcElectricDistributionBoardType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricDistributionBoardType', 'IFC4X3_RC4', *args, **kwargs)

def IfcElectricFlowStorageDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricFlowStorageDevice', 'IFC4X3_RC4', *args, **kwargs)

def IfcElectricFlowStorageDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricFlowStorageDeviceType', 'IFC4X3_RC4', *args, **kwargs)

def IfcElectricFlowTreatmentDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricFlowTreatmentDevice', 'IFC4X3_RC4', *args, **kwargs)

def IfcElectricFlowTreatmentDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricFlowTreatmentDeviceType', 'IFC4X3_RC4', *args, **kwargs)

def IfcElectricGenerator(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricGenerator', 'IFC4X3_RC4', *args, **kwargs)

def IfcElectricGeneratorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricGeneratorType', 'IFC4X3_RC4', *args, **kwargs)

def IfcElectricMotor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricMotor', 'IFC4X3_RC4', *args, **kwargs)

def IfcElectricMotorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricMotorType', 'IFC4X3_RC4', *args, **kwargs)

def IfcElectricTimeControl(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricTimeControl', 'IFC4X3_RC4', *args, **kwargs)

def IfcElectricTimeControlType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricTimeControlType', 'IFC4X3_RC4', *args, **kwargs)

def IfcElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcElementAssembly(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElementAssembly', 'IFC4X3_RC4', *args, **kwargs)

def IfcElementAssemblyType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElementAssemblyType', 'IFC4X3_RC4', *args, **kwargs)

def IfcElementComponent(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElementComponent', 'IFC4X3_RC4', *args, **kwargs)

def IfcElementComponentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElementComponentType', 'IFC4X3_RC4', *args, **kwargs)

def IfcElementQuantity(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElementQuantity', 'IFC4X3_RC4', *args, **kwargs)

def IfcElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElementType', 'IFC4X3_RC4', *args, **kwargs)

def IfcElementarySurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElementarySurface', 'IFC4X3_RC4', *args, **kwargs)

def IfcEllipse(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEllipse', 'IFC4X3_RC4', *args, **kwargs)

def IfcEllipseProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEllipseProfileDef', 'IFC4X3_RC4', *args, **kwargs)

def IfcEnergyConversionDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEnergyConversionDevice', 'IFC4X3_RC4', *args, **kwargs)

def IfcEnergyConversionDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEnergyConversionDeviceType', 'IFC4X3_RC4', *args, **kwargs)

def IfcEngine(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEngine', 'IFC4X3_RC4', *args, **kwargs)

def IfcEngineType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEngineType', 'IFC4X3_RC4', *args, **kwargs)

def IfcEvaporativeCooler(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEvaporativeCooler', 'IFC4X3_RC4', *args, **kwargs)

def IfcEvaporativeCoolerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEvaporativeCoolerType', 'IFC4X3_RC4', *args, **kwargs)

def IfcEvaporator(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEvaporator', 'IFC4X3_RC4', *args, **kwargs)

def IfcEvaporatorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEvaporatorType', 'IFC4X3_RC4', *args, **kwargs)

def IfcEvent(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEvent', 'IFC4X3_RC4', *args, **kwargs)

def IfcEventTime(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEventTime', 'IFC4X3_RC4', *args, **kwargs)

def IfcEventType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEventType', 'IFC4X3_RC4', *args, **kwargs)

def IfcExtendedProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExtendedProperties', 'IFC4X3_RC4', *args, **kwargs)

def IfcExternalInformation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExternalInformation', 'IFC4X3_RC4', *args, **kwargs)

def IfcExternalReference(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExternalReference', 'IFC4X3_RC4', *args, **kwargs)

def IfcExternalReferenceRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExternalReferenceRelationship', 'IFC4X3_RC4', *args, **kwargs)

def IfcExternalSpatialElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExternalSpatialElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcExternalSpatialStructureElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExternalSpatialStructureElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcExternallyDefinedHatchStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExternallyDefinedHatchStyle', 'IFC4X3_RC4', *args, **kwargs)

def IfcExternallyDefinedSurfaceStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExternallyDefinedSurfaceStyle', 'IFC4X3_RC4', *args, **kwargs)

def IfcExternallyDefinedTextFont(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExternallyDefinedTextFont', 'IFC4X3_RC4', *args, **kwargs)

def IfcExtrudedAreaSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExtrudedAreaSolid', 'IFC4X3_RC4', *args, **kwargs)

def IfcExtrudedAreaSolidTapered(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExtrudedAreaSolidTapered', 'IFC4X3_RC4', *args, **kwargs)

def IfcFace(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFace', 'IFC4X3_RC4', *args, **kwargs)

def IfcFaceBasedSurfaceModel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFaceBasedSurfaceModel', 'IFC4X3_RC4', *args, **kwargs)

def IfcFaceBound(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFaceBound', 'IFC4X3_RC4', *args, **kwargs)

def IfcFaceOuterBound(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFaceOuterBound', 'IFC4X3_RC4', *args, **kwargs)

def IfcFaceSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFaceSurface', 'IFC4X3_RC4', *args, **kwargs)

def IfcFacetedBrep(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFacetedBrep', 'IFC4X3_RC4', *args, **kwargs)

def IfcFacetedBrepWithVoids(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFacetedBrepWithVoids', 'IFC4X3_RC4', *args, **kwargs)

def IfcFacility(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFacility', 'IFC4X3_RC4', *args, **kwargs)

def IfcFacilityPart(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFacilityPart', 'IFC4X3_RC4', *args, **kwargs)

def IfcFailureConnectionCondition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFailureConnectionCondition', 'IFC4X3_RC4', *args, **kwargs)

def IfcFan(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFan', 'IFC4X3_RC4', *args, **kwargs)

def IfcFanType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFanType', 'IFC4X3_RC4', *args, **kwargs)

def IfcFastener(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFastener', 'IFC4X3_RC4', *args, **kwargs)

def IfcFastenerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFastenerType', 'IFC4X3_RC4', *args, **kwargs)

def IfcFeatureElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFeatureElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcFeatureElementAddition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFeatureElementAddition', 'IFC4X3_RC4', *args, **kwargs)

def IfcFeatureElementSubtraction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFeatureElementSubtraction', 'IFC4X3_RC4', *args, **kwargs)

def IfcFillAreaStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFillAreaStyle', 'IFC4X3_RC4', *args, **kwargs)

def IfcFillAreaStyleHatching(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFillAreaStyleHatching', 'IFC4X3_RC4', *args, **kwargs)

def IfcFillAreaStyleTiles(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFillAreaStyleTiles', 'IFC4X3_RC4', *args, **kwargs)

def IfcFilter(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFilter', 'IFC4X3_RC4', *args, **kwargs)

def IfcFilterType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFilterType', 'IFC4X3_RC4', *args, **kwargs)

def IfcFireSuppressionTerminal(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFireSuppressionTerminal', 'IFC4X3_RC4', *args, **kwargs)

def IfcFireSuppressionTerminalType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFireSuppressionTerminalType', 'IFC4X3_RC4', *args, **kwargs)

def IfcFixedReferenceSweptAreaSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFixedReferenceSweptAreaSolid', 'IFC4X3_RC4', *args, **kwargs)

def IfcFlowController(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowController', 'IFC4X3_RC4', *args, **kwargs)

def IfcFlowControllerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowControllerType', 'IFC4X3_RC4', *args, **kwargs)

def IfcFlowFitting(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowFitting', 'IFC4X3_RC4', *args, **kwargs)

def IfcFlowFittingType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowFittingType', 'IFC4X3_RC4', *args, **kwargs)

def IfcFlowInstrument(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowInstrument', 'IFC4X3_RC4', *args, **kwargs)

def IfcFlowInstrumentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowInstrumentType', 'IFC4X3_RC4', *args, **kwargs)

def IfcFlowMeter(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowMeter', 'IFC4X3_RC4', *args, **kwargs)

def IfcFlowMeterType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowMeterType', 'IFC4X3_RC4', *args, **kwargs)

def IfcFlowMovingDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowMovingDevice', 'IFC4X3_RC4', *args, **kwargs)

def IfcFlowMovingDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowMovingDeviceType', 'IFC4X3_RC4', *args, **kwargs)

def IfcFlowSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowSegment', 'IFC4X3_RC4', *args, **kwargs)

def IfcFlowSegmentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowSegmentType', 'IFC4X3_RC4', *args, **kwargs)

def IfcFlowStorageDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowStorageDevice', 'IFC4X3_RC4', *args, **kwargs)

def IfcFlowStorageDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowStorageDeviceType', 'IFC4X3_RC4', *args, **kwargs)

def IfcFlowTerminal(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowTerminal', 'IFC4X3_RC4', *args, **kwargs)

def IfcFlowTerminalType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowTerminalType', 'IFC4X3_RC4', *args, **kwargs)

def IfcFlowTreatmentDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowTreatmentDevice', 'IFC4X3_RC4', *args, **kwargs)

def IfcFlowTreatmentDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowTreatmentDeviceType', 'IFC4X3_RC4', *args, **kwargs)

def IfcFooting(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFooting', 'IFC4X3_RC4', *args, **kwargs)

def IfcFootingType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFootingType', 'IFC4X3_RC4', *args, **kwargs)

def IfcFurnishingElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFurnishingElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcFurnishingElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFurnishingElementType', 'IFC4X3_RC4', *args, **kwargs)

def IfcFurniture(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFurniture', 'IFC4X3_RC4', *args, **kwargs)

def IfcFurnitureType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFurnitureType', 'IFC4X3_RC4', *args, **kwargs)

def IfcGeographicElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeographicElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcGeographicElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeographicElementType', 'IFC4X3_RC4', *args, **kwargs)

def IfcGeometricCurveSet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeometricCurveSet', 'IFC4X3_RC4', *args, **kwargs)

def IfcGeometricRepresentationContext(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeometricRepresentationContext', 'IFC4X3_RC4', *args, **kwargs)

def IfcGeometricRepresentationItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeometricRepresentationItem', 'IFC4X3_RC4', *args, **kwargs)

def IfcGeometricRepresentationSubContext(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeometricRepresentationSubContext', 'IFC4X3_RC4', *args, **kwargs)

def IfcGeometricSet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeometricSet', 'IFC4X3_RC4', *args, **kwargs)

def IfcGeomodel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeomodel', 'IFC4X3_RC4', *args, **kwargs)

def IfcGeoslice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeoslice', 'IFC4X3_RC4', *args, **kwargs)

def IfcGeotechnicalAssembly(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeotechnicalAssembly', 'IFC4X3_RC4', *args, **kwargs)

def IfcGeotechnicalElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeotechnicalElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcGeotechnicalStratum(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeotechnicalStratum', 'IFC4X3_RC4', *args, **kwargs)

def IfcGradientCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGradientCurve', 'IFC4X3_RC4', *args, **kwargs)

def IfcGrid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGrid', 'IFC4X3_RC4', *args, **kwargs)

def IfcGridAxis(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGridAxis', 'IFC4X3_RC4', *args, **kwargs)

def IfcGridPlacement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGridPlacement', 'IFC4X3_RC4', *args, **kwargs)

def IfcGroup(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGroup', 'IFC4X3_RC4', *args, **kwargs)

def IfcHalfSpaceSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcHalfSpaceSolid', 'IFC4X3_RC4', *args, **kwargs)

def IfcHeatExchanger(*args, **kwargs):
    return ifcopenshell.create_entity('IfcHeatExchanger', 'IFC4X3_RC4', *args, **kwargs)

def IfcHeatExchangerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcHeatExchangerType', 'IFC4X3_RC4', *args, **kwargs)

def IfcHumidifier(*args, **kwargs):
    return ifcopenshell.create_entity('IfcHumidifier', 'IFC4X3_RC4', *args, **kwargs)

def IfcHumidifierType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcHumidifierType', 'IFC4X3_RC4', *args, **kwargs)

def IfcIShapeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIShapeProfileDef', 'IFC4X3_RC4', *args, **kwargs)

def IfcImageTexture(*args, **kwargs):
    return ifcopenshell.create_entity('IfcImageTexture', 'IFC4X3_RC4', *args, **kwargs)

def IfcImpactProtectionDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcImpactProtectionDevice', 'IFC4X3_RC4', *args, **kwargs)

def IfcImpactProtectionDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcImpactProtectionDeviceType', 'IFC4X3_RC4', *args, **kwargs)

def IfcIndexedColourMap(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIndexedColourMap', 'IFC4X3_RC4', *args, **kwargs)

def IfcIndexedPolyCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIndexedPolyCurve', 'IFC4X3_RC4', *args, **kwargs)

def IfcIndexedPolygonalFace(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIndexedPolygonalFace', 'IFC4X3_RC4', *args, **kwargs)

def IfcIndexedPolygonalFaceWithVoids(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIndexedPolygonalFaceWithVoids', 'IFC4X3_RC4', *args, **kwargs)

def IfcIndexedTextureMap(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIndexedTextureMap', 'IFC4X3_RC4', *args, **kwargs)

def IfcIndexedTriangleTextureMap(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIndexedTriangleTextureMap', 'IFC4X3_RC4', *args, **kwargs)

def IfcInterceptor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcInterceptor', 'IFC4X3_RC4', *args, **kwargs)

def IfcInterceptorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcInterceptorType', 'IFC4X3_RC4', *args, **kwargs)

def IfcIntersectionCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIntersectionCurve', 'IFC4X3_RC4', *args, **kwargs)

def IfcInventory(*args, **kwargs):
    return ifcopenshell.create_entity('IfcInventory', 'IFC4X3_RC4', *args, **kwargs)

def IfcIrregularTimeSeries(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIrregularTimeSeries', 'IFC4X3_RC4', *args, **kwargs)

def IfcIrregularTimeSeriesValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIrregularTimeSeriesValue', 'IFC4X3_RC4', *args, **kwargs)

def IfcJunctionBox(*args, **kwargs):
    return ifcopenshell.create_entity('IfcJunctionBox', 'IFC4X3_RC4', *args, **kwargs)

def IfcJunctionBoxType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcJunctionBoxType', 'IFC4X3_RC4', *args, **kwargs)

def IfcKerb(*args, **kwargs):
    return ifcopenshell.create_entity('IfcKerb', 'IFC4X3_RC4', *args, **kwargs)

def IfcKerbType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcKerbType', 'IFC4X3_RC4', *args, **kwargs)

def IfcLShapeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLShapeProfileDef', 'IFC4X3_RC4', *args, **kwargs)

def IfcLaborResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLaborResource', 'IFC4X3_RC4', *args, **kwargs)

def IfcLaborResourceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLaborResourceType', 'IFC4X3_RC4', *args, **kwargs)

def IfcLagTime(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLagTime', 'IFC4X3_RC4', *args, **kwargs)

def IfcLamp(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLamp', 'IFC4X3_RC4', *args, **kwargs)

def IfcLampType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLampType', 'IFC4X3_RC4', *args, **kwargs)

def IfcLibraryInformation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLibraryInformation', 'IFC4X3_RC4', *args, **kwargs)

def IfcLibraryReference(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLibraryReference', 'IFC4X3_RC4', *args, **kwargs)

def IfcLightDistributionData(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightDistributionData', 'IFC4X3_RC4', *args, **kwargs)

def IfcLightFixture(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightFixture', 'IFC4X3_RC4', *args, **kwargs)

def IfcLightFixtureType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightFixtureType', 'IFC4X3_RC4', *args, **kwargs)

def IfcLightIntensityDistribution(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightIntensityDistribution', 'IFC4X3_RC4', *args, **kwargs)

def IfcLightSource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightSource', 'IFC4X3_RC4', *args, **kwargs)

def IfcLightSourceAmbient(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightSourceAmbient', 'IFC4X3_RC4', *args, **kwargs)

def IfcLightSourceDirectional(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightSourceDirectional', 'IFC4X3_RC4', *args, **kwargs)

def IfcLightSourceGoniometric(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightSourceGoniometric', 'IFC4X3_RC4', *args, **kwargs)

def IfcLightSourcePositional(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightSourcePositional', 'IFC4X3_RC4', *args, **kwargs)

def IfcLightSourceSpot(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightSourceSpot', 'IFC4X3_RC4', *args, **kwargs)

def IfcLine(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLine', 'IFC4X3_RC4', *args, **kwargs)

def IfcLinearElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLinearElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcLinearPlacement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLinearPlacement', 'IFC4X3_RC4', *args, **kwargs)

def IfcLinearPositioningElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLinearPositioningElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcLiquidTerminal(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLiquidTerminal', 'IFC4X3_RC4', *args, **kwargs)

def IfcLiquidTerminalType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLiquidTerminalType', 'IFC4X3_RC4', *args, **kwargs)

def IfcLocalPlacement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLocalPlacement', 'IFC4X3_RC4', *args, **kwargs)

def IfcLoop(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLoop', 'IFC4X3_RC4', *args, **kwargs)

def IfcManifoldSolidBrep(*args, **kwargs):
    return ifcopenshell.create_entity('IfcManifoldSolidBrep', 'IFC4X3_RC4', *args, **kwargs)

def IfcMapConversion(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMapConversion', 'IFC4X3_RC4', *args, **kwargs)

def IfcMappedItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMappedItem', 'IFC4X3_RC4', *args, **kwargs)

def IfcMarineFacility(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMarineFacility', 'IFC4X3_RC4', *args, **kwargs)

def IfcMaterial(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterial', 'IFC4X3_RC4', *args, **kwargs)

def IfcMaterialClassificationRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialClassificationRelationship', 'IFC4X3_RC4', *args, **kwargs)

def IfcMaterialConstituent(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialConstituent', 'IFC4X3_RC4', *args, **kwargs)

def IfcMaterialConstituentSet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialConstituentSet', 'IFC4X3_RC4', *args, **kwargs)

def IfcMaterialDefinition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialDefinition', 'IFC4X3_RC4', *args, **kwargs)

def IfcMaterialDefinitionRepresentation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialDefinitionRepresentation', 'IFC4X3_RC4', *args, **kwargs)

def IfcMaterialLayer(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialLayer', 'IFC4X3_RC4', *args, **kwargs)

def IfcMaterialLayerSet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialLayerSet', 'IFC4X3_RC4', *args, **kwargs)

def IfcMaterialLayerSetUsage(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialLayerSetUsage', 'IFC4X3_RC4', *args, **kwargs)

def IfcMaterialLayerWithOffsets(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialLayerWithOffsets', 'IFC4X3_RC4', *args, **kwargs)

def IfcMaterialList(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialList', 'IFC4X3_RC4', *args, **kwargs)

def IfcMaterialProfile(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialProfile', 'IFC4X3_RC4', *args, **kwargs)

def IfcMaterialProfileSet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialProfileSet', 'IFC4X3_RC4', *args, **kwargs)

def IfcMaterialProfileSetUsage(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialProfileSetUsage', 'IFC4X3_RC4', *args, **kwargs)

def IfcMaterialProfileSetUsageTapering(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialProfileSetUsageTapering', 'IFC4X3_RC4', *args, **kwargs)

def IfcMaterialProfileWithOffsets(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialProfileWithOffsets', 'IFC4X3_RC4', *args, **kwargs)

def IfcMaterialProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialProperties', 'IFC4X3_RC4', *args, **kwargs)

def IfcMaterialRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialRelationship', 'IFC4X3_RC4', *args, **kwargs)

def IfcMaterialUsageDefinition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialUsageDefinition', 'IFC4X3_RC4', *args, **kwargs)

def IfcMeasureWithUnit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMeasureWithUnit', 'IFC4X3_RC4', *args, **kwargs)

def IfcMechanicalFastener(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMechanicalFastener', 'IFC4X3_RC4', *args, **kwargs)

def IfcMechanicalFastenerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMechanicalFastenerType', 'IFC4X3_RC4', *args, **kwargs)

def IfcMedicalDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMedicalDevice', 'IFC4X3_RC4', *args, **kwargs)

def IfcMedicalDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMedicalDeviceType', 'IFC4X3_RC4', *args, **kwargs)

def IfcMember(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMember', 'IFC4X3_RC4', *args, **kwargs)

def IfcMemberStandardCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMemberStandardCase', 'IFC4X3_RC4', *args, **kwargs)

def IfcMemberType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMemberType', 'IFC4X3_RC4', *args, **kwargs)

def IfcMetric(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMetric', 'IFC4X3_RC4', *args, **kwargs)

def IfcMirroredProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMirroredProfileDef', 'IFC4X3_RC4', *args, **kwargs)

def IfcMobileTelecommunicationsAppliance(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMobileTelecommunicationsAppliance', 'IFC4X3_RC4', *args, **kwargs)

def IfcMobileTelecommunicationsApplianceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMobileTelecommunicationsApplianceType', 'IFC4X3_RC4', *args, **kwargs)

def IfcMonetaryUnit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMonetaryUnit', 'IFC4X3_RC4', *args, **kwargs)

def IfcMooringDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMooringDevice', 'IFC4X3_RC4', *args, **kwargs)

def IfcMooringDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMooringDeviceType', 'IFC4X3_RC4', *args, **kwargs)

def IfcMotorConnection(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMotorConnection', 'IFC4X3_RC4', *args, **kwargs)

def IfcMotorConnectionType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMotorConnectionType', 'IFC4X3_RC4', *args, **kwargs)

def IfcNamedUnit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcNamedUnit', 'IFC4X3_RC4', *args, **kwargs)

def IfcNavigationElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcNavigationElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcNavigationElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcNavigationElementType', 'IFC4X3_RC4', *args, **kwargs)

def IfcObject(*args, **kwargs):
    return ifcopenshell.create_entity('IfcObject', 'IFC4X3_RC4', *args, **kwargs)

def IfcObjectDefinition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcObjectDefinition', 'IFC4X3_RC4', *args, **kwargs)

def IfcObjectPlacement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcObjectPlacement', 'IFC4X3_RC4', *args, **kwargs)

def IfcObjective(*args, **kwargs):
    return ifcopenshell.create_entity('IfcObjective', 'IFC4X3_RC4', *args, **kwargs)

def IfcOccupant(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOccupant', 'IFC4X3_RC4', *args, **kwargs)

def IfcOffsetCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOffsetCurve', 'IFC4X3_RC4', *args, **kwargs)

def IfcOffsetCurve2D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOffsetCurve2D', 'IFC4X3_RC4', *args, **kwargs)

def IfcOffsetCurve3D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOffsetCurve3D', 'IFC4X3_RC4', *args, **kwargs)

def IfcOffsetCurveByDistances(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOffsetCurveByDistances', 'IFC4X3_RC4', *args, **kwargs)

def IfcOpenCrossProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOpenCrossProfileDef', 'IFC4X3_RC4', *args, **kwargs)

def IfcOpenShell(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOpenShell', 'IFC4X3_RC4', *args, **kwargs)

def IfcOpeningElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOpeningElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcOpeningStandardCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOpeningStandardCase', 'IFC4X3_RC4', *args, **kwargs)

def IfcOrganization(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOrganization', 'IFC4X3_RC4', *args, **kwargs)

def IfcOrganizationRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOrganizationRelationship', 'IFC4X3_RC4', *args, **kwargs)

def IfcOrientedEdge(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOrientedEdge', 'IFC4X3_RC4', *args, **kwargs)

def IfcOuterBoundaryCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOuterBoundaryCurve', 'IFC4X3_RC4', *args, **kwargs)

def IfcOutlet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOutlet', 'IFC4X3_RC4', *args, **kwargs)

def IfcOutletType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOutletType', 'IFC4X3_RC4', *args, **kwargs)

def IfcOwnerHistory(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOwnerHistory', 'IFC4X3_RC4', *args, **kwargs)

def IfcParameterizedProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcParameterizedProfileDef', 'IFC4X3_RC4', *args, **kwargs)

def IfcPath(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPath', 'IFC4X3_RC4', *args, **kwargs)

def IfcPavement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPavement', 'IFC4X3_RC4', *args, **kwargs)

def IfcPavementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPavementType', 'IFC4X3_RC4', *args, **kwargs)

def IfcPcurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPcurve', 'IFC4X3_RC4', *args, **kwargs)

def IfcPerformanceHistory(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPerformanceHistory', 'IFC4X3_RC4', *args, **kwargs)

def IfcPermeableCoveringProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPermeableCoveringProperties', 'IFC4X3_RC4', *args, **kwargs)

def IfcPermit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPermit', 'IFC4X3_RC4', *args, **kwargs)

def IfcPerson(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPerson', 'IFC4X3_RC4', *args, **kwargs)

def IfcPersonAndOrganization(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPersonAndOrganization', 'IFC4X3_RC4', *args, **kwargs)

def IfcPhysicalComplexQuantity(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPhysicalComplexQuantity', 'IFC4X3_RC4', *args, **kwargs)

def IfcPhysicalQuantity(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPhysicalQuantity', 'IFC4X3_RC4', *args, **kwargs)

def IfcPhysicalSimpleQuantity(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPhysicalSimpleQuantity', 'IFC4X3_RC4', *args, **kwargs)

def IfcPile(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPile', 'IFC4X3_RC4', *args, **kwargs)

def IfcPileType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPileType', 'IFC4X3_RC4', *args, **kwargs)

def IfcPipeFitting(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPipeFitting', 'IFC4X3_RC4', *args, **kwargs)

def IfcPipeFittingType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPipeFittingType', 'IFC4X3_RC4', *args, **kwargs)

def IfcPipeSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPipeSegment', 'IFC4X3_RC4', *args, **kwargs)

def IfcPipeSegmentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPipeSegmentType', 'IFC4X3_RC4', *args, **kwargs)

def IfcPixelTexture(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPixelTexture', 'IFC4X3_RC4', *args, **kwargs)

def IfcPlacement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPlacement', 'IFC4X3_RC4', *args, **kwargs)

def IfcPlanarBox(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPlanarBox', 'IFC4X3_RC4', *args, **kwargs)

def IfcPlanarExtent(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPlanarExtent', 'IFC4X3_RC4', *args, **kwargs)

def IfcPlane(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPlane', 'IFC4X3_RC4', *args, **kwargs)

def IfcPlant(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPlant', 'IFC4X3_RC4', *args, **kwargs)

def IfcPlate(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPlate', 'IFC4X3_RC4', *args, **kwargs)

def IfcPlateStandardCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPlateStandardCase', 'IFC4X3_RC4', *args, **kwargs)

def IfcPlateType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPlateType', 'IFC4X3_RC4', *args, **kwargs)

def IfcPoint(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPoint', 'IFC4X3_RC4', *args, **kwargs)

def IfcPointByDistanceExpression(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPointByDistanceExpression', 'IFC4X3_RC4', *args, **kwargs)

def IfcPointOnCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPointOnCurve', 'IFC4X3_RC4', *args, **kwargs)

def IfcPointOnSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPointOnSurface', 'IFC4X3_RC4', *args, **kwargs)

def IfcPolyLoop(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPolyLoop', 'IFC4X3_RC4', *args, **kwargs)

def IfcPolygonalBoundedHalfSpace(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPolygonalBoundedHalfSpace', 'IFC4X3_RC4', *args, **kwargs)

def IfcPolygonalFaceSet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPolygonalFaceSet', 'IFC4X3_RC4', *args, **kwargs)

def IfcPolyline(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPolyline', 'IFC4X3_RC4', *args, **kwargs)

def IfcPolynomialCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPolynomialCurve', 'IFC4X3_RC4', *args, **kwargs)

def IfcPort(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPort', 'IFC4X3_RC4', *args, **kwargs)

def IfcPositioningElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPositioningElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcPostalAddress(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPostalAddress', 'IFC4X3_RC4', *args, **kwargs)

def IfcPreDefinedColour(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPreDefinedColour', 'IFC4X3_RC4', *args, **kwargs)

def IfcPreDefinedCurveFont(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPreDefinedCurveFont', 'IFC4X3_RC4', *args, **kwargs)

def IfcPreDefinedItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPreDefinedItem', 'IFC4X3_RC4', *args, **kwargs)

def IfcPreDefinedProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPreDefinedProperties', 'IFC4X3_RC4', *args, **kwargs)

def IfcPreDefinedPropertySet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPreDefinedPropertySet', 'IFC4X3_RC4', *args, **kwargs)

def IfcPreDefinedTextFont(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPreDefinedTextFont', 'IFC4X3_RC4', *args, **kwargs)

def IfcPresentationItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPresentationItem', 'IFC4X3_RC4', *args, **kwargs)

def IfcPresentationLayerAssignment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPresentationLayerAssignment', 'IFC4X3_RC4', *args, **kwargs)

def IfcPresentationLayerWithStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPresentationLayerWithStyle', 'IFC4X3_RC4', *args, **kwargs)

def IfcPresentationStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPresentationStyle', 'IFC4X3_RC4', *args, **kwargs)

def IfcProcedure(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProcedure', 'IFC4X3_RC4', *args, **kwargs)

def IfcProcedureType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProcedureType', 'IFC4X3_RC4', *args, **kwargs)

def IfcProcess(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProcess', 'IFC4X3_RC4', *args, **kwargs)

def IfcProduct(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProduct', 'IFC4X3_RC4', *args, **kwargs)

def IfcProductDefinitionShape(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProductDefinitionShape', 'IFC4X3_RC4', *args, **kwargs)

def IfcProductRepresentation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProductRepresentation', 'IFC4X3_RC4', *args, **kwargs)

def IfcProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProfileDef', 'IFC4X3_RC4', *args, **kwargs)

def IfcProfileProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProfileProperties', 'IFC4X3_RC4', *args, **kwargs)

def IfcProject(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProject', 'IFC4X3_RC4', *args, **kwargs)

def IfcProjectLibrary(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProjectLibrary', 'IFC4X3_RC4', *args, **kwargs)

def IfcProjectOrder(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProjectOrder', 'IFC4X3_RC4', *args, **kwargs)

def IfcProjectedCRS(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProjectedCRS', 'IFC4X3_RC4', *args, **kwargs)

def IfcProjectionElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProjectionElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcProperty(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProperty', 'IFC4X3_RC4', *args, **kwargs)

def IfcPropertyAbstraction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyAbstraction', 'IFC4X3_RC4', *args, **kwargs)

def IfcPropertyBoundedValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyBoundedValue', 'IFC4X3_RC4', *args, **kwargs)

def IfcPropertyDefinition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyDefinition', 'IFC4X3_RC4', *args, **kwargs)

def IfcPropertyDependencyRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyDependencyRelationship', 'IFC4X3_RC4', *args, **kwargs)

def IfcPropertyEnumeratedValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyEnumeratedValue', 'IFC4X3_RC4', *args, **kwargs)

def IfcPropertyEnumeration(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyEnumeration', 'IFC4X3_RC4', *args, **kwargs)

def IfcPropertyListValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyListValue', 'IFC4X3_RC4', *args, **kwargs)

def IfcPropertyReferenceValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyReferenceValue', 'IFC4X3_RC4', *args, **kwargs)

def IfcPropertySet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertySet', 'IFC4X3_RC4', *args, **kwargs)

def IfcPropertySetDefinition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertySetDefinition', 'IFC4X3_RC4', *args, **kwargs)

def IfcPropertySetTemplate(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertySetTemplate', 'IFC4X3_RC4', *args, **kwargs)

def IfcPropertySingleValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertySingleValue', 'IFC4X3_RC4', *args, **kwargs)

def IfcPropertyTableValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyTableValue', 'IFC4X3_RC4', *args, **kwargs)

def IfcPropertyTemplate(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyTemplate', 'IFC4X3_RC4', *args, **kwargs)

def IfcPropertyTemplateDefinition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyTemplateDefinition', 'IFC4X3_RC4', *args, **kwargs)

def IfcProtectiveDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProtectiveDevice', 'IFC4X3_RC4', *args, **kwargs)

def IfcProtectiveDeviceTrippingUnit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProtectiveDeviceTrippingUnit', 'IFC4X3_RC4', *args, **kwargs)

def IfcProtectiveDeviceTrippingUnitType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProtectiveDeviceTrippingUnitType', 'IFC4X3_RC4', *args, **kwargs)

def IfcProtectiveDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProtectiveDeviceType', 'IFC4X3_RC4', *args, **kwargs)

def IfcProxy(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProxy', 'IFC4X3_RC4', *args, **kwargs)

def IfcPump(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPump', 'IFC4X3_RC4', *args, **kwargs)

def IfcPumpType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPumpType', 'IFC4X3_RC4', *args, **kwargs)

def IfcQuantityArea(*args, **kwargs):
    return ifcopenshell.create_entity('IfcQuantityArea', 'IFC4X3_RC4', *args, **kwargs)

def IfcQuantityCount(*args, **kwargs):
    return ifcopenshell.create_entity('IfcQuantityCount', 'IFC4X3_RC4', *args, **kwargs)

def IfcQuantityLength(*args, **kwargs):
    return ifcopenshell.create_entity('IfcQuantityLength', 'IFC4X3_RC4', *args, **kwargs)

def IfcQuantitySet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcQuantitySet', 'IFC4X3_RC4', *args, **kwargs)

def IfcQuantityTime(*args, **kwargs):
    return ifcopenshell.create_entity('IfcQuantityTime', 'IFC4X3_RC4', *args, **kwargs)

def IfcQuantityVolume(*args, **kwargs):
    return ifcopenshell.create_entity('IfcQuantityVolume', 'IFC4X3_RC4', *args, **kwargs)

def IfcQuantityWeight(*args, **kwargs):
    return ifcopenshell.create_entity('IfcQuantityWeight', 'IFC4X3_RC4', *args, **kwargs)

def IfcRail(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRail', 'IFC4X3_RC4', *args, **kwargs)

def IfcRailType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRailType', 'IFC4X3_RC4', *args, **kwargs)

def IfcRailing(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRailing', 'IFC4X3_RC4', *args, **kwargs)

def IfcRailingType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRailingType', 'IFC4X3_RC4', *args, **kwargs)

def IfcRailway(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRailway', 'IFC4X3_RC4', *args, **kwargs)

def IfcRamp(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRamp', 'IFC4X3_RC4', *args, **kwargs)

def IfcRampFlight(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRampFlight', 'IFC4X3_RC4', *args, **kwargs)

def IfcRampFlightType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRampFlightType', 'IFC4X3_RC4', *args, **kwargs)

def IfcRampType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRampType', 'IFC4X3_RC4', *args, **kwargs)

def IfcRationalBSplineCurveWithKnots(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRationalBSplineCurveWithKnots', 'IFC4X3_RC4', *args, **kwargs)

def IfcRationalBSplineSurfaceWithKnots(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRationalBSplineSurfaceWithKnots', 'IFC4X3_RC4', *args, **kwargs)

def IfcRectangleHollowProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRectangleHollowProfileDef', 'IFC4X3_RC4', *args, **kwargs)

def IfcRectangleProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRectangleProfileDef', 'IFC4X3_RC4', *args, **kwargs)

def IfcRectangularPyramid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRectangularPyramid', 'IFC4X3_RC4', *args, **kwargs)

def IfcRectangularTrimmedSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRectangularTrimmedSurface', 'IFC4X3_RC4', *args, **kwargs)

def IfcRecurrencePattern(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRecurrencePattern', 'IFC4X3_RC4', *args, **kwargs)

def IfcReference(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReference', 'IFC4X3_RC4', *args, **kwargs)

def IfcReferent(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReferent', 'IFC4X3_RC4', *args, **kwargs)

def IfcRegularTimeSeries(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRegularTimeSeries', 'IFC4X3_RC4', *args, **kwargs)

def IfcReinforcedSoil(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReinforcedSoil', 'IFC4X3_RC4', *args, **kwargs)

def IfcReinforcementBarProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReinforcementBarProperties', 'IFC4X3_RC4', *args, **kwargs)

def IfcReinforcementDefinitionProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReinforcementDefinitionProperties', 'IFC4X3_RC4', *args, **kwargs)

def IfcReinforcingBar(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReinforcingBar', 'IFC4X3_RC4', *args, **kwargs)

def IfcReinforcingBarType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReinforcingBarType', 'IFC4X3_RC4', *args, **kwargs)

def IfcReinforcingElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReinforcingElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcReinforcingElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReinforcingElementType', 'IFC4X3_RC4', *args, **kwargs)

def IfcReinforcingMesh(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReinforcingMesh', 'IFC4X3_RC4', *args, **kwargs)

def IfcReinforcingMeshType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReinforcingMeshType', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelAdheresToElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAdheresToElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelAggregates(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAggregates', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelAssigns(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssigns', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelAssignsToActor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssignsToActor', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelAssignsToControl(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssignsToControl', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelAssignsToGroup(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssignsToGroup', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelAssignsToGroupByFactor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssignsToGroupByFactor', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelAssignsToProcess(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssignsToProcess', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelAssignsToProduct(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssignsToProduct', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelAssignsToResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssignsToResource', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelAssociates(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssociates', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelAssociatesApproval(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssociatesApproval', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelAssociatesClassification(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssociatesClassification', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelAssociatesConstraint(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssociatesConstraint', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelAssociatesDocument(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssociatesDocument', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelAssociatesLibrary(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssociatesLibrary', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelAssociatesMaterial(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssociatesMaterial', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelAssociatesProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssociatesProfileDef', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelConnects(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnects', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelConnectsElements(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsElements', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelConnectsPathElements(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsPathElements', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelConnectsPortToElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsPortToElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelConnectsPorts(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsPorts', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelConnectsStructuralActivity(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsStructuralActivity', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelConnectsStructuralMember(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsStructuralMember', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelConnectsWithEccentricity(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsWithEccentricity', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelConnectsWithRealizingElements(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsWithRealizingElements', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelContainedInSpatialStructure(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelContainedInSpatialStructure', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelCoversBldgElements(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelCoversBldgElements', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelCoversSpaces(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelCoversSpaces', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelDeclares(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelDeclares', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelDecomposes(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelDecomposes', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelDefines(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelDefines', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelDefinesByObject(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelDefinesByObject', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelDefinesByProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelDefinesByProperties', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelDefinesByTemplate(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelDefinesByTemplate', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelDefinesByType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelDefinesByType', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelFillsElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelFillsElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelFlowControlElements(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelFlowControlElements', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelInterferesElements(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelInterferesElements', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelNests(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelNests', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelPositions(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelPositions', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelProjectsElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelProjectsElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelReferencedInSpatialStructure(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelReferencedInSpatialStructure', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelSequence(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelSequence', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelServicesBuildings(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelServicesBuildings', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelSpaceBoundary(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelSpaceBoundary', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelSpaceBoundary1stLevel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelSpaceBoundary1stLevel', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelSpaceBoundary2ndLevel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelSpaceBoundary2ndLevel', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelVoidsElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelVoidsElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelationship', 'IFC4X3_RC4', *args, **kwargs)

def IfcReparametrisedCompositeCurveSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReparametrisedCompositeCurveSegment', 'IFC4X3_RC4', *args, **kwargs)

def IfcRepresentation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRepresentation', 'IFC4X3_RC4', *args, **kwargs)

def IfcRepresentationContext(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRepresentationContext', 'IFC4X3_RC4', *args, **kwargs)

def IfcRepresentationItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRepresentationItem', 'IFC4X3_RC4', *args, **kwargs)

def IfcRepresentationMap(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRepresentationMap', 'IFC4X3_RC4', *args, **kwargs)

def IfcResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcResource', 'IFC4X3_RC4', *args, **kwargs)

def IfcResourceApprovalRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcResourceApprovalRelationship', 'IFC4X3_RC4', *args, **kwargs)

def IfcResourceConstraintRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcResourceConstraintRelationship', 'IFC4X3_RC4', *args, **kwargs)

def IfcResourceLevelRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcResourceLevelRelationship', 'IFC4X3_RC4', *args, **kwargs)

def IfcResourceTime(*args, **kwargs):
    return ifcopenshell.create_entity('IfcResourceTime', 'IFC4X3_RC4', *args, **kwargs)

def IfcRevolvedAreaSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRevolvedAreaSolid', 'IFC4X3_RC4', *args, **kwargs)

def IfcRevolvedAreaSolidTapered(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRevolvedAreaSolidTapered', 'IFC4X3_RC4', *args, **kwargs)

def IfcRightCircularCone(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRightCircularCone', 'IFC4X3_RC4', *args, **kwargs)

def IfcRightCircularCylinder(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRightCircularCylinder', 'IFC4X3_RC4', *args, **kwargs)

def IfcRoad(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRoad', 'IFC4X3_RC4', *args, **kwargs)

def IfcRoof(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRoof', 'IFC4X3_RC4', *args, **kwargs)

def IfcRoofType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRoofType', 'IFC4X3_RC4', *args, **kwargs)

def IfcRoot(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRoot', 'IFC4X3_RC4', *args, **kwargs)

def IfcRoundedRectangleProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRoundedRectangleProfileDef', 'IFC4X3_RC4', *args, **kwargs)

def IfcSIUnit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSIUnit', 'IFC4X3_RC4', *args, **kwargs)

def IfcSanitaryTerminal(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSanitaryTerminal', 'IFC4X3_RC4', *args, **kwargs)

def IfcSanitaryTerminalType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSanitaryTerminalType', 'IFC4X3_RC4', *args, **kwargs)

def IfcSchedulingTime(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSchedulingTime', 'IFC4X3_RC4', *args, **kwargs)

def IfcSeamCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSeamCurve', 'IFC4X3_RC4', *args, **kwargs)

def IfcSecondOrderPolynomialSpiral(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSecondOrderPolynomialSpiral', 'IFC4X3_RC4', *args, **kwargs)

def IfcSectionProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSectionProperties', 'IFC4X3_RC4', *args, **kwargs)

def IfcSectionReinforcementProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSectionReinforcementProperties', 'IFC4X3_RC4', *args, **kwargs)

def IfcSectionedSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSectionedSolid', 'IFC4X3_RC4', *args, **kwargs)

def IfcSectionedSolidHorizontal(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSectionedSolidHorizontal', 'IFC4X3_RC4', *args, **kwargs)

def IfcSectionedSpine(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSectionedSpine', 'IFC4X3_RC4', *args, **kwargs)

def IfcSectionedSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSectionedSurface', 'IFC4X3_RC4', *args, **kwargs)

def IfcSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSegment', 'IFC4X3_RC4', *args, **kwargs)

def IfcSegmentedReferenceCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSegmentedReferenceCurve', 'IFC4X3_RC4', *args, **kwargs)

def IfcSensor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSensor', 'IFC4X3_RC4', *args, **kwargs)

def IfcSensorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSensorType', 'IFC4X3_RC4', *args, **kwargs)

def IfcSeventhOrderPolynomialSpiral(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSeventhOrderPolynomialSpiral', 'IFC4X3_RC4', *args, **kwargs)

def IfcShadingDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcShadingDevice', 'IFC4X3_RC4', *args, **kwargs)

def IfcShadingDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcShadingDeviceType', 'IFC4X3_RC4', *args, **kwargs)

def IfcShapeAspect(*args, **kwargs):
    return ifcopenshell.create_entity('IfcShapeAspect', 'IFC4X3_RC4', *args, **kwargs)

def IfcShapeModel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcShapeModel', 'IFC4X3_RC4', *args, **kwargs)

def IfcShapeRepresentation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcShapeRepresentation', 'IFC4X3_RC4', *args, **kwargs)

def IfcShellBasedSurfaceModel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcShellBasedSurfaceModel', 'IFC4X3_RC4', *args, **kwargs)

def IfcSign(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSign', 'IFC4X3_RC4', *args, **kwargs)

def IfcSignType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSignType', 'IFC4X3_RC4', *args, **kwargs)

def IfcSignal(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSignal', 'IFC4X3_RC4', *args, **kwargs)

def IfcSignalType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSignalType', 'IFC4X3_RC4', *args, **kwargs)

def IfcSimpleProperty(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSimpleProperty', 'IFC4X3_RC4', *args, **kwargs)

def IfcSimplePropertyTemplate(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSimplePropertyTemplate', 'IFC4X3_RC4', *args, **kwargs)

def IfcSine(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSine', 'IFC4X3_RC4', *args, **kwargs)

def IfcSite(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSite', 'IFC4X3_RC4', *args, **kwargs)

def IfcSlab(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSlab', 'IFC4X3_RC4', *args, **kwargs)

def IfcSlabElementedCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSlabElementedCase', 'IFC4X3_RC4', *args, **kwargs)

def IfcSlabStandardCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSlabStandardCase', 'IFC4X3_RC4', *args, **kwargs)

def IfcSlabType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSlabType', 'IFC4X3_RC4', *args, **kwargs)

def IfcSlippageConnectionCondition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSlippageConnectionCondition', 'IFC4X3_RC4', *args, **kwargs)

def IfcSolarDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSolarDevice', 'IFC4X3_RC4', *args, **kwargs)

def IfcSolarDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSolarDeviceType', 'IFC4X3_RC4', *args, **kwargs)

def IfcSolidModel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSolidModel', 'IFC4X3_RC4', *args, **kwargs)

def IfcSolidStratum(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSolidStratum', 'IFC4X3_RC4', *args, **kwargs)

def IfcSpace(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpace', 'IFC4X3_RC4', *args, **kwargs)

def IfcSpaceHeater(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpaceHeater', 'IFC4X3_RC4', *args, **kwargs)

def IfcSpaceHeaterType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpaceHeaterType', 'IFC4X3_RC4', *args, **kwargs)

def IfcSpaceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpaceType', 'IFC4X3_RC4', *args, **kwargs)

def IfcSpatialElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpatialElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcSpatialElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpatialElementType', 'IFC4X3_RC4', *args, **kwargs)

def IfcSpatialStructureElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpatialStructureElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcSpatialStructureElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpatialStructureElementType', 'IFC4X3_RC4', *args, **kwargs)

def IfcSpatialZone(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpatialZone', 'IFC4X3_RC4', *args, **kwargs)

def IfcSpatialZoneType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpatialZoneType', 'IFC4X3_RC4', *args, **kwargs)

def IfcSphere(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSphere', 'IFC4X3_RC4', *args, **kwargs)

def IfcSphericalSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSphericalSurface', 'IFC4X3_RC4', *args, **kwargs)

def IfcSpiral(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpiral', 'IFC4X3_RC4', *args, **kwargs)

def IfcStackTerminal(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStackTerminal', 'IFC4X3_RC4', *args, **kwargs)

def IfcStackTerminalType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStackTerminalType', 'IFC4X3_RC4', *args, **kwargs)

def IfcStair(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStair', 'IFC4X3_RC4', *args, **kwargs)

def IfcStairFlight(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStairFlight', 'IFC4X3_RC4', *args, **kwargs)

def IfcStairFlightType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStairFlightType', 'IFC4X3_RC4', *args, **kwargs)

def IfcStairType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStairType', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralAction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralAction', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralActivity(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralActivity', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralAnalysisModel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralAnalysisModel', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralConnection(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralConnection', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralConnectionCondition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralConnectionCondition', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralCurveAction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralCurveAction', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralCurveConnection(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralCurveConnection', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralCurveMember(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralCurveMember', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralCurveMemberVarying(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralCurveMemberVarying', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralCurveReaction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralCurveReaction', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralItem', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralLinearAction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLinearAction', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralLoad(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoad', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralLoadCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadCase', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralLoadConfiguration(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadConfiguration', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralLoadGroup(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadGroup', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralLoadLinearForce(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadLinearForce', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralLoadOrResult(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadOrResult', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralLoadPlanarForce(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadPlanarForce', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralLoadSingleDisplacement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadSingleDisplacement', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralLoadSingleDisplacementDistortion(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadSingleDisplacementDistortion', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralLoadSingleForce(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadSingleForce', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralLoadSingleForceWarping(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadSingleForceWarping', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralLoadStatic(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadStatic', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralLoadTemperature(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadTemperature', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralMember(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralMember', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralPlanarAction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralPlanarAction', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralPointAction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralPointAction', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralPointConnection(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralPointConnection', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralPointReaction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralPointReaction', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralReaction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralReaction', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralResultGroup(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralResultGroup', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralSurfaceAction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralSurfaceAction', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralSurfaceConnection(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralSurfaceConnection', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralSurfaceMember(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralSurfaceMember', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralSurfaceMemberVarying(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralSurfaceMemberVarying', 'IFC4X3_RC4', *args, **kwargs)

def IfcStructuralSurfaceReaction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralSurfaceReaction', 'IFC4X3_RC4', *args, **kwargs)

def IfcStyleModel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStyleModel', 'IFC4X3_RC4', *args, **kwargs)

def IfcStyledItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStyledItem', 'IFC4X3_RC4', *args, **kwargs)

def IfcStyledRepresentation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStyledRepresentation', 'IFC4X3_RC4', *args, **kwargs)

def IfcSubContractResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSubContractResource', 'IFC4X3_RC4', *args, **kwargs)

def IfcSubContractResourceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSubContractResourceType', 'IFC4X3_RC4', *args, **kwargs)

def IfcSubedge(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSubedge', 'IFC4X3_RC4', *args, **kwargs)

def IfcSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurface', 'IFC4X3_RC4', *args, **kwargs)

def IfcSurfaceCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceCurve', 'IFC4X3_RC4', *args, **kwargs)

def IfcSurfaceCurveSweptAreaSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceCurveSweptAreaSolid', 'IFC4X3_RC4', *args, **kwargs)

def IfcSurfaceFeature(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceFeature', 'IFC4X3_RC4', *args, **kwargs)

def IfcSurfaceOfLinearExtrusion(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceOfLinearExtrusion', 'IFC4X3_RC4', *args, **kwargs)

def IfcSurfaceOfRevolution(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceOfRevolution', 'IFC4X3_RC4', *args, **kwargs)

def IfcSurfaceReinforcementArea(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceReinforcementArea', 'IFC4X3_RC4', *args, **kwargs)

def IfcSurfaceStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceStyle', 'IFC4X3_RC4', *args, **kwargs)

def IfcSurfaceStyleLighting(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceStyleLighting', 'IFC4X3_RC4', *args, **kwargs)

def IfcSurfaceStyleRefraction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceStyleRefraction', 'IFC4X3_RC4', *args, **kwargs)

def IfcSurfaceStyleRendering(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceStyleRendering', 'IFC4X3_RC4', *args, **kwargs)

def IfcSurfaceStyleShading(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceStyleShading', 'IFC4X3_RC4', *args, **kwargs)

def IfcSurfaceStyleWithTextures(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceStyleWithTextures', 'IFC4X3_RC4', *args, **kwargs)

def IfcSurfaceTexture(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceTexture', 'IFC4X3_RC4', *args, **kwargs)

def IfcSweptAreaSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSweptAreaSolid', 'IFC4X3_RC4', *args, **kwargs)

def IfcSweptDiskSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSweptDiskSolid', 'IFC4X3_RC4', *args, **kwargs)

def IfcSweptDiskSolidPolygonal(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSweptDiskSolidPolygonal', 'IFC4X3_RC4', *args, **kwargs)

def IfcSweptSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSweptSurface', 'IFC4X3_RC4', *args, **kwargs)

def IfcSwitchingDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSwitchingDevice', 'IFC4X3_RC4', *args, **kwargs)

def IfcSwitchingDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSwitchingDeviceType', 'IFC4X3_RC4', *args, **kwargs)

def IfcSystem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSystem', 'IFC4X3_RC4', *args, **kwargs)

def IfcSystemFurnitureElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSystemFurnitureElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcSystemFurnitureElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSystemFurnitureElementType', 'IFC4X3_RC4', *args, **kwargs)

def IfcTShapeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTShapeProfileDef', 'IFC4X3_RC4', *args, **kwargs)

def IfcTable(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTable', 'IFC4X3_RC4', *args, **kwargs)

def IfcTableColumn(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTableColumn', 'IFC4X3_RC4', *args, **kwargs)

def IfcTableRow(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTableRow', 'IFC4X3_RC4', *args, **kwargs)

def IfcTank(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTank', 'IFC4X3_RC4', *args, **kwargs)

def IfcTankType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTankType', 'IFC4X3_RC4', *args, **kwargs)

def IfcTask(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTask', 'IFC4X3_RC4', *args, **kwargs)

def IfcTaskTime(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTaskTime', 'IFC4X3_RC4', *args, **kwargs)

def IfcTaskTimeRecurring(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTaskTimeRecurring', 'IFC4X3_RC4', *args, **kwargs)

def IfcTaskType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTaskType', 'IFC4X3_RC4', *args, **kwargs)

def IfcTelecomAddress(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTelecomAddress', 'IFC4X3_RC4', *args, **kwargs)

def IfcTendon(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTendon', 'IFC4X3_RC4', *args, **kwargs)

def IfcTendonAnchor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTendonAnchor', 'IFC4X3_RC4', *args, **kwargs)

def IfcTendonAnchorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTendonAnchorType', 'IFC4X3_RC4', *args, **kwargs)

def IfcTendonConduit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTendonConduit', 'IFC4X3_RC4', *args, **kwargs)

def IfcTendonConduitType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTendonConduitType', 'IFC4X3_RC4', *args, **kwargs)

def IfcTendonType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTendonType', 'IFC4X3_RC4', *args, **kwargs)

def IfcTessellatedFaceSet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTessellatedFaceSet', 'IFC4X3_RC4', *args, **kwargs)

def IfcTessellatedItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTessellatedItem', 'IFC4X3_RC4', *args, **kwargs)

def IfcTextLiteral(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextLiteral', 'IFC4X3_RC4', *args, **kwargs)

def IfcTextLiteralWithExtent(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextLiteralWithExtent', 'IFC4X3_RC4', *args, **kwargs)

def IfcTextStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextStyle', 'IFC4X3_RC4', *args, **kwargs)

def IfcTextStyleFontModel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextStyleFontModel', 'IFC4X3_RC4', *args, **kwargs)

def IfcTextStyleForDefinedFont(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextStyleForDefinedFont', 'IFC4X3_RC4', *args, **kwargs)

def IfcTextStyleTextModel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextStyleTextModel', 'IFC4X3_RC4', *args, **kwargs)

def IfcTextureCoordinate(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextureCoordinate', 'IFC4X3_RC4', *args, **kwargs)

def IfcTextureCoordinateGenerator(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextureCoordinateGenerator', 'IFC4X3_RC4', *args, **kwargs)

def IfcTextureMap(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextureMap', 'IFC4X3_RC4', *args, **kwargs)

def IfcTextureVertex(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextureVertex', 'IFC4X3_RC4', *args, **kwargs)

def IfcTextureVertexList(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextureVertexList', 'IFC4X3_RC4', *args, **kwargs)

def IfcThirdOrderPolynomialSpiral(*args, **kwargs):
    return ifcopenshell.create_entity('IfcThirdOrderPolynomialSpiral', 'IFC4X3_RC4', *args, **kwargs)

def IfcTimePeriod(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTimePeriod', 'IFC4X3_RC4', *args, **kwargs)

def IfcTimeSeries(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTimeSeries', 'IFC4X3_RC4', *args, **kwargs)

def IfcTimeSeriesValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTimeSeriesValue', 'IFC4X3_RC4', *args, **kwargs)

def IfcTopologicalRepresentationItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTopologicalRepresentationItem', 'IFC4X3_RC4', *args, **kwargs)

def IfcTopologyRepresentation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTopologyRepresentation', 'IFC4X3_RC4', *args, **kwargs)

def IfcToroidalSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcToroidalSurface', 'IFC4X3_RC4', *args, **kwargs)

def IfcTrackElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTrackElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcTrackElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTrackElementType', 'IFC4X3_RC4', *args, **kwargs)

def IfcTransformer(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTransformer', 'IFC4X3_RC4', *args, **kwargs)

def IfcTransformerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTransformerType', 'IFC4X3_RC4', *args, **kwargs)

def IfcTransportElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTransportElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcTransportElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTransportElementType', 'IFC4X3_RC4', *args, **kwargs)

def IfcTrapeziumProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTrapeziumProfileDef', 'IFC4X3_RC4', *args, **kwargs)

def IfcTriangulatedFaceSet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTriangulatedFaceSet', 'IFC4X3_RC4', *args, **kwargs)

def IfcTriangulatedIrregularNetwork(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTriangulatedIrregularNetwork', 'IFC4X3_RC4', *args, **kwargs)

def IfcTrimmedCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTrimmedCurve', 'IFC4X3_RC4', *args, **kwargs)

def IfcTubeBundle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTubeBundle', 'IFC4X3_RC4', *args, **kwargs)

def IfcTubeBundleType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTubeBundleType', 'IFC4X3_RC4', *args, **kwargs)

def IfcTypeObject(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTypeObject', 'IFC4X3_RC4', *args, **kwargs)

def IfcTypeProcess(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTypeProcess', 'IFC4X3_RC4', *args, **kwargs)

def IfcTypeProduct(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTypeProduct', 'IFC4X3_RC4', *args, **kwargs)

def IfcTypeResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTypeResource', 'IFC4X3_RC4', *args, **kwargs)

def IfcUShapeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcUShapeProfileDef', 'IFC4X3_RC4', *args, **kwargs)

def IfcUnitAssignment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcUnitAssignment', 'IFC4X3_RC4', *args, **kwargs)

def IfcUnitaryControlElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcUnitaryControlElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcUnitaryControlElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcUnitaryControlElementType', 'IFC4X3_RC4', *args, **kwargs)

def IfcUnitaryEquipment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcUnitaryEquipment', 'IFC4X3_RC4', *args, **kwargs)

def IfcUnitaryEquipmentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcUnitaryEquipmentType', 'IFC4X3_RC4', *args, **kwargs)

def IfcValve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcValve', 'IFC4X3_RC4', *args, **kwargs)

def IfcValveType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcValveType', 'IFC4X3_RC4', *args, **kwargs)

def IfcVector(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVector', 'IFC4X3_RC4', *args, **kwargs)

def IfcVertex(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVertex', 'IFC4X3_RC4', *args, **kwargs)

def IfcVertexLoop(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVertexLoop', 'IFC4X3_RC4', *args, **kwargs)

def IfcVertexPoint(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVertexPoint', 'IFC4X3_RC4', *args, **kwargs)

def IfcVibrationDamper(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVibrationDamper', 'IFC4X3_RC4', *args, **kwargs)

def IfcVibrationDamperType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVibrationDamperType', 'IFC4X3_RC4', *args, **kwargs)

def IfcVibrationIsolator(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVibrationIsolator', 'IFC4X3_RC4', *args, **kwargs)

def IfcVibrationIsolatorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVibrationIsolatorType', 'IFC4X3_RC4', *args, **kwargs)

def IfcVirtualElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVirtualElement', 'IFC4X3_RC4', *args, **kwargs)

def IfcVirtualGridIntersection(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVirtualGridIntersection', 'IFC4X3_RC4', *args, **kwargs)

def IfcVoidStratum(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVoidStratum', 'IFC4X3_RC4', *args, **kwargs)

def IfcVoidingFeature(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVoidingFeature', 'IFC4X3_RC4', *args, **kwargs)

def IfcWall(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWall', 'IFC4X3_RC4', *args, **kwargs)

def IfcWallElementedCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWallElementedCase', 'IFC4X3_RC4', *args, **kwargs)

def IfcWallStandardCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWallStandardCase', 'IFC4X3_RC4', *args, **kwargs)

def IfcWallType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWallType', 'IFC4X3_RC4', *args, **kwargs)

def IfcWasteTerminal(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWasteTerminal', 'IFC4X3_RC4', *args, **kwargs)

def IfcWasteTerminalType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWasteTerminalType', 'IFC4X3_RC4', *args, **kwargs)

def IfcWaterStratum(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWaterStratum', 'IFC4X3_RC4', *args, **kwargs)

def IfcWindow(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWindow', 'IFC4X3_RC4', *args, **kwargs)

def IfcWindowLiningProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWindowLiningProperties', 'IFC4X3_RC4', *args, **kwargs)

def IfcWindowPanelProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWindowPanelProperties', 'IFC4X3_RC4', *args, **kwargs)

def IfcWindowStandardCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWindowStandardCase', 'IFC4X3_RC4', *args, **kwargs)

def IfcWindowStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWindowStyle', 'IFC4X3_RC4', *args, **kwargs)

def IfcWindowType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWindowType', 'IFC4X3_RC4', *args, **kwargs)

def IfcWorkCalendar(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWorkCalendar', 'IFC4X3_RC4', *args, **kwargs)

def IfcWorkControl(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWorkControl', 'IFC4X3_RC4', *args, **kwargs)

def IfcWorkPlan(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWorkPlan', 'IFC4X3_RC4', *args, **kwargs)

def IfcWorkSchedule(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWorkSchedule', 'IFC4X3_RC4', *args, **kwargs)

def IfcWorkTime(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWorkTime', 'IFC4X3_RC4', *args, **kwargs)

def IfcZShapeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcZShapeProfileDef', 'IFC4X3_RC4', *args, **kwargs)

def IfcZone(*args, **kwargs):
    return ifcopenshell.create_entity('IfcZone', 'IFC4X3_RC4', *args, **kwargs)

class IfcBoxAlignment_WR1:
    SCOPE = 'type'
    TYPE_NAME = 'IfcBoxAlignment'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (express_getattr(self, 'lower', INDETERMINATE)() in ['top-left', 'top-middle', 'top-right', 'middle-left', 'center', 'middle-right', 'bottom-left', 'bottom-middle', 'bottom-right']) is not False

class IfcCardinalPointReference_GreaterThanZero:
    SCOPE = 'type'
    TYPE_NAME = 'IfcCardinalPointReference'
    RULE_NAME = 'GreaterThanZero'

    @staticmethod
    def __call__(self):
        assert (self > 0) is not False

class IfcCompoundPlaneAngleMeasure_MinutesInRange:
    SCOPE = 'type'
    TYPE_NAME = 'IfcCompoundPlaneAngleMeasure'
    RULE_NAME = 'MinutesInRange'

    @staticmethod
    def __call__(self):
        assert (abs(express_getitem(self, 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) < 60) is not False

class IfcCompoundPlaneAngleMeasure_SecondsInRange:
    SCOPE = 'type'
    TYPE_NAME = 'IfcCompoundPlaneAngleMeasure'
    RULE_NAME = 'SecondsInRange'

    @staticmethod
    def __call__(self):
        assert (abs(express_getitem(self, 3 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) < 60) is not False

class IfcCompoundPlaneAngleMeasure_MicrosecondsInRange:
    SCOPE = 'type'
    TYPE_NAME = 'IfcCompoundPlaneAngleMeasure'
    RULE_NAME = 'MicrosecondsInRange'

    @staticmethod
    def __call__(self):
        assert (sizeof(self) == 3 or abs(express_getitem(self, 4 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) < 1000000) is not False

class IfcCompoundPlaneAngleMeasure_ConsistentSign:
    SCOPE = 'type'
    TYPE_NAME = 'IfcCompoundPlaneAngleMeasure'
    RULE_NAME = 'ConsistentSign'

    @staticmethod
    def __call__(self):
        assert (express_getitem(self, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) >= 0 and express_getitem(self, 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) >= 0 and (express_getitem(self, 3 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) >= 0) and (sizeof(self) == 3 or express_getitem(self, 4 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) >= 0) or (express_getitem(self, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) <= 0 and express_getitem(self, 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) <= 0 and (express_getitem(self, 3 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) <= 0) and (sizeof(self) == 3 or express_getitem(self, 4 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) <= 0))) is not False

class IfcDayInMonthNumber_ValidRange:
    SCOPE = 'type'
    TYPE_NAME = 'IfcDayInMonthNumber'
    RULE_NAME = 'ValidRange'

    @staticmethod
    def __call__(self):
        assert (1 <= self <= 31) is not False

class IfcDayInWeekNumber_ValidRange:
    SCOPE = 'type'
    TYPE_NAME = 'IfcDayInWeekNumber'
    RULE_NAME = 'ValidRange'

    @staticmethod
    def __call__(self):
        assert (1 <= self <= 7) is not False

class IfcDimensionCount_WR1:
    SCOPE = 'type'
    TYPE_NAME = 'IfcDimensionCount'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (0 < self <= 3) is not False

class IfcFontStyle_WR1:
    SCOPE = 'type'
    TYPE_NAME = 'IfcFontStyle'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (express_getattr(self, 'lower', INDETERMINATE)() in ['normal', 'italic', 'oblique']) is not False

class IfcFontVariant_WR1:
    SCOPE = 'type'
    TYPE_NAME = 'IfcFontVariant'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (express_getattr(self, 'lower', INDETERMINATE)() in ['normal', 'small-caps']) is not False

class IfcFontWeight_WR1:
    SCOPE = 'type'
    TYPE_NAME = 'IfcFontWeight'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (express_getattr(self, 'lower', INDETERMINATE)() in ['normal', 'small-caps', '100', '200', '300', '400', '500', '600', '700', '800', '900']) is not False

class IfcHeatingValueMeasure_WR1:
    SCOPE = 'type'
    TYPE_NAME = 'IfcHeatingValueMeasure'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (self > 0.0) is not False

class IfcMonthInYearNumber_ValidRange:
    SCOPE = 'type'
    TYPE_NAME = 'IfcMonthInYearNumber'
    RULE_NAME = 'ValidRange'

    @staticmethod
    def __call__(self):
        assert (1 <= self <= 12) is not False

class IfcNonNegativeLengthMeasure_NotNegative:
    SCOPE = 'type'
    TYPE_NAME = 'IfcNonNegativeLengthMeasure'
    RULE_NAME = 'NotNegative'

    @staticmethod
    def __call__(self):
        assert (self >= 0.0) is not False

class IfcNormalisedRatioMeasure_WR1:
    SCOPE = 'type'
    TYPE_NAME = 'IfcNormalisedRatioMeasure'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (0.0 <= self <= 1.0) is not False

class IfcPHMeasure_WR21:
    SCOPE = 'type'
    TYPE_NAME = 'IfcPHMeasure'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        assert (0.0 <= self <= 14.0) is not False

class IfcPositiveInteger_WR1:
    SCOPE = 'type'
    TYPE_NAME = 'IfcPositiveInteger'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (self > 0) is not False

class IfcPositiveLengthMeasure_WR1:
    SCOPE = 'type'
    TYPE_NAME = 'IfcPositiveLengthMeasure'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (self > 0.0) is not False

class IfcPositivePlaneAngleMeasure_WR1:
    SCOPE = 'type'
    TYPE_NAME = 'IfcPositivePlaneAngleMeasure'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (self > 0.0) is not False

class IfcPositiveRatioMeasure_WR1:
    SCOPE = 'type'
    TYPE_NAME = 'IfcPositiveRatioMeasure'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (self > 0.0) is not False

class IfcSpecularRoughness_WR1:
    SCOPE = 'type'
    TYPE_NAME = 'IfcSpecularRoughness'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (0.0 <= self <= 1.0) is not False

class IfcTextAlignment_WR1:
    SCOPE = 'type'
    TYPE_NAME = 'IfcTextAlignment'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (express_getattr(self, 'lower', INDETERMINATE)() in ['left', 'right', 'center', 'justify']) is not False

class IfcTextDecoration_WR1:
    SCOPE = 'type'
    TYPE_NAME = 'IfcTextDecoration'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (express_getattr(self, 'lower', INDETERMINATE)() in ['none', 'underline', 'overline', 'line-through', 'blink']) is not False

class IfcTextTransformation_WR1:
    SCOPE = 'type'
    TYPE_NAME = 'IfcTextTransformation'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (express_getattr(self, 'lower', INDETERMINATE)() in ['capitalize', 'uppercase', 'lowercase', 'none']) is not False

class IfcActorRole_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcActorRole'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        role = express_getattr(self, 'Role', INDETERMINATE)
        assert (role != express_getattr(IfcRoleEnum, 'USERDEFINED', INDETERMINATE) or (role == express_getattr(IfcRoleEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'UserDefinedRole', INDETERMINATE)))) is not False

class IfcActuator_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcActuator'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcActuatorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcActuatorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcActuator_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcActuator'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcactuatortype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcActuatorType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcActuatorType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcActuatorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcActuatorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcAddress_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAddress'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        purpose = express_getattr(self, 'Purpose', INDETERMINATE)
        assert (not exists(purpose) or (purpose != express_getattr(IfcAddressTypeEnum, 'USERDEFINED', INDETERMINATE) or (purpose == express_getattr(IfcAddressTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'UserDefinedPurpose', INDETERMINATE))))) is not False

class IfcAdvancedBrep_HasAdvancedFaces:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAdvancedBrep'
    RULE_NAME = 'HasAdvancedFaces'

    @staticmethod
    def __call__(self):
        assert (sizeof([afs for afs in express_getattr(express_getattr(self, 'Outer', INDETERMINATE), 'CfsFaces', INDETERMINATE) if not 'ifc4x3_rc4.ifcadvancedface' in typeof(afs)]) == 0) is not False

class IfcAdvancedBrepWithVoids_VoidsHaveAdvancedFaces:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAdvancedBrepWithVoids'
    RULE_NAME = 'VoidsHaveAdvancedFaces'

    @staticmethod
    def __call__(self):
        voids = express_getattr(self, 'Voids', INDETERMINATE)
        assert (sizeof([vsh for vsh in voids if sizeof([afs for afs in express_getattr(vsh, 'CfsFaces', INDETERMINATE) if not 'ifc4x3_rc4.ifcadvancedface' in typeof(afs)]) == 0]) == 0) is not False

class IfcAdvancedFace_ApplicableSurface:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAdvancedFace'
    RULE_NAME = 'ApplicableSurface'

    @staticmethod
    def __call__(self):
        assert (sizeof(['ifc4x3_rc4.ifcelementarysurface', 'ifc4x3_rc4.ifcsweptsurface', 'ifc4x3_rc4.ifcbsplinesurface'] * typeof(express_getattr(self, 'FaceSurface', INDETERMINATE))) == 1) is not False

class IfcAdvancedFace_RequiresEdgeCurve:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAdvancedFace'
    RULE_NAME = 'RequiresEdgeCurve'

    @staticmethod
    def __call__(self):
        assert (sizeof([elpfbnds for elpfbnds in [bnds for bnds in express_getattr(self, 'Bounds', INDETERMINATE) if 'ifc4x3_rc4.ifcedgeloop' in typeof(express_getattr(bnds, 'Bound', INDETERMINATE))] if not sizeof([oe for oe in express_getattr(express_getattr(elpfbnds, 'Bound', INDETERMINATE), 'EdgeList', INDETERMINATE) if not 'ifc4x3_rc4.ifcedgecurve' in typeof(express_getattr(oe, 'EdgeElement', INDETERMINATE))]) == 0]) == 0) is not False

class IfcAdvancedFace_ApplicableEdgeCurves:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAdvancedFace'
    RULE_NAME = 'ApplicableEdgeCurves'

    @staticmethod
    def __call__(self):
        assert (sizeof([elpfbnds for elpfbnds in [bnds for bnds in express_getattr(self, 'Bounds', INDETERMINATE) if 'ifc4x3_rc4.ifcedgeloop' in typeof(express_getattr(bnds, 'Bound', INDETERMINATE))] if not sizeof([oe for oe in express_getattr(express_getattr(elpfbnds, 'Bound', INDETERMINATE), 'EdgeList', INDETERMINATE) if not sizeof(['ifc4x3_rc4.ifcline', 'ifc4x3_rc4.ifcconic', 'ifc4x3_rc4.ifcpolyline', 'ifc4x3_rc4.ifcbsplinecurve'] * typeof(express_getattr(express_getattr(oe, 'EdgeElement', INDETERMINATE), 'EdgeGeometry', INDETERMINATE))) == 1]) == 0]) == 0) is not False

class IfcAirTerminal_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAirTerminal'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcAirTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcAirTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcAirTerminal_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAirTerminal'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcairterminaltype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcAirTerminalBox_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAirTerminalBox'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcAirTerminalBoxTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcAirTerminalBoxTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcAirTerminalBox_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAirTerminalBox'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcairterminalboxtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcAirTerminalBoxType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAirTerminalBoxType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcAirTerminalBoxTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcAirTerminalBoxTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcAirTerminalType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAirTerminalType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcAirTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcAirTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcAirToAirHeatRecovery_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAirToAirHeatRecovery'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcAirToAirHeatRecoveryTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcAirToAirHeatRecoveryTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcAirToAirHeatRecovery_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAirToAirHeatRecovery'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcairtoairheatrecoverytype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcAirToAirHeatRecoveryType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAirToAirHeatRecoveryType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcAirToAirHeatRecoveryTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcAirToAirHeatRecoveryTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcAlarm_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAlarm'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcAlarmTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcAlarmTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcAlarm_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAlarm'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcalarmtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcAlarmType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAlarmType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcAlarmTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcAlarmTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcApproval_HasIdentifierOrName:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcApproval'
    RULE_NAME = 'HasIdentifierOrName'

    @staticmethod
    def __call__(self):
        identifier = express_getattr(self, 'Identifier', INDETERMINATE)
        name = express_getattr(self, 'Name', INDETERMINATE)
        assert (exists(identifier) or exists(name)) is not False

class IfcArbitraryClosedProfileDef_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcArbitraryClosedProfileDef'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        outercurve = express_getattr(self, 'OuterCurve', INDETERMINATE)
        assert (express_getattr(outercurve, 'Dim', INDETERMINATE) == 2) is not False

class IfcArbitraryClosedProfileDef_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcArbitraryClosedProfileDef'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        outercurve = express_getattr(self, 'OuterCurve', INDETERMINATE)
        assert (not 'ifc4x3_rc4.ifcline' in typeof(outercurve)) is not False

class IfcArbitraryClosedProfileDef_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcArbitraryClosedProfileDef'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        outercurve = express_getattr(self, 'OuterCurve', INDETERMINATE)
        assert (not 'ifc4x3_rc4.ifcoffsetcurve2d' in typeof(outercurve)) is not False

class IfcArbitraryOpenProfileDef_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcArbitraryOpenProfileDef'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        assert ('ifc4x3_rc4.ifccenterlineprofiledef' in typeof(self) or express_getattr(self, 'ProfileType', INDETERMINATE) == express_getattr(IfcProfileTypeEnum, 'CURVE', INDETERMINATE)) is not False

class IfcArbitraryOpenProfileDef_WR12:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcArbitraryOpenProfileDef'
    RULE_NAME = 'WR12'

    @staticmethod
    def __call__(self):
        curve = express_getattr(self, 'Curve', INDETERMINATE)
        assert (express_getattr(curve, 'Dim', INDETERMINATE) == 2) is not False

class IfcArbitraryProfileDefWithVoids_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcArbitraryProfileDefWithVoids'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (express_getattr(self, 'ProfileType', INDETERMINATE) == area) is not False

class IfcArbitraryProfileDefWithVoids_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcArbitraryProfileDefWithVoids'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        innercurves = express_getattr(self, 'InnerCurves', INDETERMINATE)
        assert (sizeof([temp for temp in innercurves if express_getattr(temp, 'Dim', INDETERMINATE) != 2]) == 0) is not False

class IfcArbitraryProfileDefWithVoids_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcArbitraryProfileDefWithVoids'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        innercurves = express_getattr(self, 'InnerCurves', INDETERMINATE)
        assert (sizeof([temp for temp in innercurves if 'ifc4x3_rc4.ifcline' in typeof(temp)]) == 0) is not False

class IfcAsymmetricIShapeProfileDef_ValidFlangeThickness:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAsymmetricIShapeProfileDef'
    RULE_NAME = 'ValidFlangeThickness'

    @staticmethod
    def __call__(self):
        overalldepth = express_getattr(self, 'OverallDepth', INDETERMINATE)
        bottomflangethickness = express_getattr(self, 'BottomFlangeThickness', INDETERMINATE)
        topflangethickness = express_getattr(self, 'TopFlangeThickness', INDETERMINATE)
        assert (not exists(topflangethickness) or bottomflangethickness + topflangethickness < overalldepth) is not False

class IfcAsymmetricIShapeProfileDef_ValidWebThickness:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAsymmetricIShapeProfileDef'
    RULE_NAME = 'ValidWebThickness'

    @staticmethod
    def __call__(self):
        bottomflangewidth = express_getattr(self, 'BottomFlangeWidth', INDETERMINATE)
        webthickness = express_getattr(self, 'WebThickness', INDETERMINATE)
        topflangewidth = express_getattr(self, 'TopFlangeWidth', INDETERMINATE)
        assert (webthickness < bottomflangewidth and webthickness < topflangewidth) is not False

class IfcAsymmetricIShapeProfileDef_ValidBottomFilletRadius:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAsymmetricIShapeProfileDef'
    RULE_NAME = 'ValidBottomFilletRadius'

    @staticmethod
    def __call__(self):
        bottomflangewidth = express_getattr(self, 'BottomFlangeWidth', INDETERMINATE)
        webthickness = express_getattr(self, 'WebThickness', INDETERMINATE)
        bottomflangefilletradius = express_getattr(self, 'BottomFlangeFilletRadius', INDETERMINATE)
        assert (not exists(bottomflangefilletradius) or bottomflangefilletradius <= (bottomflangewidth - webthickness) / 2.0) is not False

class IfcAsymmetricIShapeProfileDef_ValidTopFilletRadius:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAsymmetricIShapeProfileDef'
    RULE_NAME = 'ValidTopFilletRadius'

    @staticmethod
    def __call__(self):
        webthickness = express_getattr(self, 'WebThickness', INDETERMINATE)
        topflangewidth = express_getattr(self, 'TopFlangeWidth', INDETERMINATE)
        topflangefilletradius = express_getattr(self, 'TopFlangeFilletRadius', INDETERMINATE)
        assert (not exists(topflangefilletradius) or topflangefilletradius <= (topflangewidth - webthickness) / 2.0) is not False

class IfcAudioVisualAppliance_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAudioVisualAppliance'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcAudioVisualApplianceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcAudioVisualApplianceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcAudioVisualAppliance_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAudioVisualAppliance'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcaudiovisualappliancetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcAudioVisualApplianceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAudioVisualApplianceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcAudioVisualApplianceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcAudioVisualApplianceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcAxis1Placement_AxisIs3D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis1Placement'
    RULE_NAME = 'AxisIs3D'

    @staticmethod
    def __call__(self):
        axis = express_getattr(self, 'Axis', INDETERMINATE)
        assert (not exists(axis) or express_getattr(axis, 'Dim', INDETERMINATE) == 3) is not False

class IfcAxis1Placement_LocationIs3D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis1Placement'
    RULE_NAME = 'LocationIs3D'

    @staticmethod
    def __call__(self):
        assert (express_getattr(express_getattr(self, 'Location', INDETERMINATE), 'Dim', INDETERMINATE) == 3) is not False

class IfcAxis1Placement_LocationIsCP:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis1Placement'
    RULE_NAME = 'LocationIsCP'

    @staticmethod
    def __call__(self):
        assert ('ifc4x3_rc4.ifccartesianpoint' in typeof(express_getattr(self, 'Location', INDETERMINATE))) is not False

def calc_IfcAxis1Placement_Z(self):
    axis = express_getattr(self, 'Axis', INDETERMINATE)
    return nvl(IfcNormalise(axis), IfcDirection(DirectionRatios=[0.0, 0.0, 1.0]))

class IfcAxis2Placement2D_RefDirIs2D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis2Placement2D'
    RULE_NAME = 'RefDirIs2D'

    @staticmethod
    def __call__(self):
        refdirection = express_getattr(self, 'RefDirection', INDETERMINATE)
        assert (not exists(refdirection) or express_getattr(refdirection, 'Dim', INDETERMINATE) == 2) is not False

class IfcAxis2Placement2D_LocationIs2D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis2Placement2D'
    RULE_NAME = 'LocationIs2D'

    @staticmethod
    def __call__(self):
        assert (express_getattr(express_getattr(self, 'Location', INDETERMINATE), 'Dim', INDETERMINATE) == 2) is not False

class IfcAxis2Placement2D_LocationIsCP:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis2Placement2D'
    RULE_NAME = 'LocationIsCP'

    @staticmethod
    def __call__(self):
        assert ('ifc4x3_rc4.ifccartesianpoint' in typeof(express_getattr(self, 'Location', INDETERMINATE))) is not False

def calc_IfcAxis2Placement2D_P(self):
    refdirection = express_getattr(self, 'RefDirection', INDETERMINATE)
    return IfcBuild2Axes(refdirection)

class IfcAxis2Placement3D_LocationIs3D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis2Placement3D'
    RULE_NAME = 'LocationIs3D'

    @staticmethod
    def __call__(self):
        assert (express_getattr(express_getattr(self, 'Location', INDETERMINATE), 'Dim', INDETERMINATE) == 3) is not False

class IfcAxis2Placement3D_AxisIs3D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis2Placement3D'
    RULE_NAME = 'AxisIs3D'

    @staticmethod
    def __call__(self):
        axis = express_getattr(self, 'Axis', INDETERMINATE)
        assert (not exists(axis) or express_getattr(axis, 'Dim', INDETERMINATE) == 3) is not False

class IfcAxis2Placement3D_RefDirIs3D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis2Placement3D'
    RULE_NAME = 'RefDirIs3D'

    @staticmethod
    def __call__(self):
        refdirection = express_getattr(self, 'RefDirection', INDETERMINATE)
        assert (not exists(refdirection) or express_getattr(refdirection, 'Dim', INDETERMINATE) == 3) is not False

class IfcAxis2Placement3D_AxisToRefDirPosition:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis2Placement3D'
    RULE_NAME = 'AxisToRefDirPosition'

    @staticmethod
    def __call__(self):
        axis = express_getattr(self, 'Axis', INDETERMINATE)
        refdirection = express_getattr(self, 'RefDirection', INDETERMINATE)
        assert (not exists(axis) or not exists(refdirection) or express_getattr(IfcCrossProduct(axis, refdirection), 'Magnitude', INDETERMINATE) > 0.0) is not False

class IfcAxis2Placement3D_AxisAndRefDirProvision:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis2Placement3D'
    RULE_NAME = 'AxisAndRefDirProvision'

    @staticmethod
    def __call__(self):
        axis = express_getattr(self, 'Axis', INDETERMINATE)
        refdirection = express_getattr(self, 'RefDirection', INDETERMINATE)
        assert (not exists(axis) ^ exists(refdirection)) is not False

class IfcAxis2Placement3D_LocationIsCP:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis2Placement3D'
    RULE_NAME = 'LocationIsCP'

    @staticmethod
    def __call__(self):
        assert ('ifc4x3_rc4.ifccartesianpoint' in typeof(express_getattr(self, 'Location', INDETERMINATE))) is not False

def calc_IfcAxis2Placement3D_P(self):
    axis = express_getattr(self, 'Axis', INDETERMINATE)
    refdirection = express_getattr(self, 'RefDirection', INDETERMINATE)
    return IfcBuildAxes(axis, refdirection)

class IfcAxis2PlacementLinear_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis2PlacementLinear'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert ('ifc4x3_rc4.ifcpointbydistanceexpression' in typeof(express_getattr(self, 'Location', INDETERMINATE))) is not False

class IfcAxis2PlacementLinear_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis2PlacementLinear'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        axis = express_getattr(self, 'Axis', INDETERMINATE)
        refdirection = express_getattr(self, 'RefDirection', INDETERMINATE)
        assert (not exists(axis) or not exists(refdirection) or express_getattr(IfcCrossProduct(axis, refdirection), 'Magnitude', INDETERMINATE) > 0.0) is not False

class IfcBSplineCurve_SameDim:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBSplineCurve'
    RULE_NAME = 'SameDim'

    @staticmethod
    def __call__(self):
        controlpointslist = express_getattr(self, 'ControlPointsList', INDETERMINATE)
        assert (sizeof([temp for temp in controlpointslist if express_getattr(temp, 'Dim', INDETERMINATE) != express_getattr(express_getitem(controlpointslist, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)]) == 0) is not False

def calc_IfcBSplineCurve_UpperIndexOnControlPoints(self):
    controlpointslist = express_getattr(self, 'ControlPointsList', INDETERMINATE)
    return sizeof(controlpointslist) - 1

def calc_IfcBSplineCurve_ControlPoints(self):
    controlpointslist = express_getattr(self, 'ControlPointsList', INDETERMINATE)
    upperindexoncontrolpoints = express_getattr(self, 'UpperIndexOnControlPoints', INDETERMINATE)
    return IfcListToArray(controlpointslist, 0, upperindexoncontrolpoints)

class IfcBSplineCurveWithKnots_ConsistentBSpline:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBSplineCurveWithKnots'
    RULE_NAME = 'ConsistentBSpline'

    @staticmethod
    def __call__(self):
        degree = express_getattr(self, 'Degree', INDETERMINATE)
        upperindexoncontrolpoints = express_getattr(self, 'UpperIndexOnControlPoints', INDETERMINATE)
        knotmultiplicities = express_getattr(self, 'KnotMultiplicities', INDETERMINATE)
        knots = express_getattr(self, 'Knots', INDETERMINATE)
        upperindexonknots = express_getattr(self, 'UpperIndexOnKnots', INDETERMINATE)
        assert IfcConstraintsParamBSpline(degree, upperindexonknots, upperindexoncontrolpoints, knotmultiplicities, knots) is not False

class IfcBSplineCurveWithKnots_CorrespondingKnotLists:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBSplineCurveWithKnots'
    RULE_NAME = 'CorrespondingKnotLists'

    @staticmethod
    def __call__(self):
        knotmultiplicities = express_getattr(self, 'KnotMultiplicities', INDETERMINATE)
        upperindexonknots = express_getattr(self, 'UpperIndexOnKnots', INDETERMINATE)
        assert (sizeof(knotmultiplicities) == upperindexonknots) is not False

def calc_IfcBSplineCurveWithKnots_UpperIndexOnKnots(self):
    knots = express_getattr(self, 'Knots', INDETERMINATE)
    return sizeof(knots)

def calc_IfcBSplineSurface_UUpper(self):
    controlpointslist = express_getattr(self, 'ControlPointsList', INDETERMINATE)
    return sizeof(controlpointslist) - 1

def calc_IfcBSplineSurface_VUpper(self):
    controlpointslist = express_getattr(self, 'ControlPointsList', INDETERMINATE)
    return sizeof(express_getitem(controlpointslist, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) - 1

def calc_IfcBSplineSurface_ControlPoints(self):
    controlpointslist = express_getattr(self, 'ControlPointsList', INDETERMINATE)
    uupper = express_getattr(self, 'UUpper', INDETERMINATE)
    vupper = express_getattr(self, 'VUpper', INDETERMINATE)
    return IfcMakeArrayOfArray(controlpointslist, 0, uupper, 0, vupper)

class IfcBSplineSurfaceWithKnots_UDirectionConstraints:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBSplineSurfaceWithKnots'
    RULE_NAME = 'UDirectionConstraints'

    @staticmethod
    def __call__(self):
        umultiplicities = express_getattr(self, 'UMultiplicities', INDETERMINATE)
        uknots = express_getattr(self, 'UKnots', INDETERMINATE)
        knotuupper = express_getattr(self, 'KnotUUpper', INDETERMINATE)
        assert IfcConstraintsParamBSpline(express_getattr(self, 'UDegree', INDETERMINATE), knotuupper, express_getattr(self, 'UUpper', INDETERMINATE), umultiplicities, uknots) is not False

class IfcBSplineSurfaceWithKnots_VDirectionConstraints:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBSplineSurfaceWithKnots'
    RULE_NAME = 'VDirectionConstraints'

    @staticmethod
    def __call__(self):
        vmultiplicities = express_getattr(self, 'VMultiplicities', INDETERMINATE)
        vknots = express_getattr(self, 'VKnots', INDETERMINATE)
        knotvupper = express_getattr(self, 'KnotVUpper', INDETERMINATE)
        assert IfcConstraintsParamBSpline(express_getattr(self, 'VDegree', INDETERMINATE), knotvupper, express_getattr(self, 'VUpper', INDETERMINATE), vmultiplicities, vknots) is not False

class IfcBSplineSurfaceWithKnots_CorrespondingULists:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBSplineSurfaceWithKnots'
    RULE_NAME = 'CorrespondingULists'

    @staticmethod
    def __call__(self):
        umultiplicities = express_getattr(self, 'UMultiplicities', INDETERMINATE)
        knotuupper = express_getattr(self, 'KnotUUpper', INDETERMINATE)
        assert (sizeof(umultiplicities) == knotuupper) is not False

class IfcBSplineSurfaceWithKnots_CorrespondingVLists:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBSplineSurfaceWithKnots'
    RULE_NAME = 'CorrespondingVLists'

    @staticmethod
    def __call__(self):
        vmultiplicities = express_getattr(self, 'VMultiplicities', INDETERMINATE)
        knotvupper = express_getattr(self, 'KnotVUpper', INDETERMINATE)
        assert (sizeof(vmultiplicities) == knotvupper) is not False

def calc_IfcBSplineSurfaceWithKnots_KnotVUpper(self):
    vknots = express_getattr(self, 'VKnots', INDETERMINATE)
    return sizeof(vknots)

def calc_IfcBSplineSurfaceWithKnots_KnotUUpper(self):
    uknots = express_getattr(self, 'UKnots', INDETERMINATE)
    return sizeof(uknots)

class IfcBeam_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBeam'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcBeamTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcBeamTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcBeam_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBeam'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcbeamtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcBeamStandardCase_HasMaterialProfileSetUsage:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBeamStandardCase'
    RULE_NAME = 'HasMaterialProfileSetUsage'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in usedin(self, 'ifc4x3_rc4.ifcrelassociates.relatedobjects') if 'ifc4x3_rc4.ifcrelassociatesmaterial' in typeof(temp) and 'ifc4x3_rc4.ifcmaterialprofilesetusage' in typeof(express_getattr(temp, 'RelatingMaterial', INDETERMINATE))]) == 1) is not False

class IfcBeamType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBeamType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcBeamTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcBeamTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcBearing_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBearing'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcBearingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcBearingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcBearing_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBearing'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcbearingtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcBearingType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBearingType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcBearingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcBearingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcBlobTexture_SupportedRasterFormat:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBlobTexture'
    RULE_NAME = 'SupportedRasterFormat'

    @staticmethod
    def __call__(self):
        assert (express_getattr(express_getattr(self, 'RasterFormat', INDETERMINATE), 'lower', INDETERMINATE)() in ['bmp', 'jpg', 'gif', 'png']) is not False

class IfcBlobTexture_RasterCodeByteStream:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBlobTexture'
    RULE_NAME = 'RasterCodeByteStream'

    @staticmethod
    def __call__(self):
        rastercode = express_getattr(self, 'RasterCode', INDETERMINATE)
        assert (blength(rastercode) % 8 == 0) is not False

class IfcBoiler_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBoiler'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcBoilerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcBoilerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcBoiler_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBoiler'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcboilertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcBoilerType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBoilerType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcBoilerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcBoilerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcBooleanClippingResult_FirstOperandType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBooleanClippingResult'
    RULE_NAME = 'FirstOperandType'

    @staticmethod
    def __call__(self):
        firstoperand = express_getattr(self, 'FirstOperand', INDETERMINATE)
        assert ('ifc4x3_rc4.ifcsweptareasolid' in typeof(firstoperand) or 'ifc4x3_rc4.ifcsweptdiscsolid' in typeof(firstoperand) or 'ifc4x3_rc4.ifcbooleanclippingresult' in typeof(firstoperand)) is not False

class IfcBooleanClippingResult_SecondOperandType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBooleanClippingResult'
    RULE_NAME = 'SecondOperandType'

    @staticmethod
    def __call__(self):
        secondoperand = express_getattr(self, 'SecondOperand', INDETERMINATE)
        assert ('ifc4x3_rc4.ifchalfspacesolid' in typeof(secondoperand)) is not False

class IfcBooleanClippingResult_OperatorType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBooleanClippingResult'
    RULE_NAME = 'OperatorType'

    @staticmethod
    def __call__(self):
        operator = express_getattr(self, 'Operator', INDETERMINATE)
        assert (operator == difference) is not False

class IfcBooleanResult_SameDim:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBooleanResult'
    RULE_NAME = 'SameDim'

    @staticmethod
    def __call__(self):
        firstoperand = express_getattr(self, 'FirstOperand', INDETERMINATE)
        secondoperand = express_getattr(self, 'SecondOperand', INDETERMINATE)
        assert (express_getattr(firstoperand, 'Dim', INDETERMINATE) == express_getattr(secondoperand, 'Dim', INDETERMINATE)) is not False

class IfcBooleanResult_FirstOperandClosed:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBooleanResult'
    RULE_NAME = 'FirstOperandClosed'

    @staticmethod
    def __call__(self):
        firstoperand = express_getattr(self, 'FirstOperand', INDETERMINATE)
        assert (not 'ifc4x3_rc4.ifctessellatedfaceset' in typeof(firstoperand) or (exists(express_getattr(firstoperand, 'Closed', INDETERMINATE)) and express_getattr(firstoperand, 'Closed', INDETERMINATE))) is not False

class IfcBooleanResult_SecondOperandClosed:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBooleanResult'
    RULE_NAME = 'SecondOperandClosed'

    @staticmethod
    def __call__(self):
        secondoperand = express_getattr(self, 'SecondOperand', INDETERMINATE)
        assert (not 'ifc4x3_rc4.ifctessellatedfaceset' in typeof(secondoperand) or (exists(express_getattr(secondoperand, 'Closed', INDETERMINATE)) and express_getattr(secondoperand, 'Closed', INDETERMINATE))) is not False

def calc_IfcBooleanResult_Dim(self):
    firstoperand = express_getattr(self, 'FirstOperand', INDETERMINATE)
    return express_getattr(firstoperand, 'Dim', INDETERMINATE)

class IfcBoundaryCurve_IsClosed:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBoundaryCurve'
    RULE_NAME = 'IsClosed'

    @staticmethod
    def __call__(self):
        assert express_getattr(self, 'ClosedCurve', INDETERMINATE) is not False

def calc_IfcBoundingBox_Dim(self):
    return 3

class IfcBoxedHalfSpace_UnboundedSurface:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBoxedHalfSpace'
    RULE_NAME = 'UnboundedSurface'

    @staticmethod
    def __call__(self):
        assert (not 'ifc4x3_rc4.ifccurveboundedplane' in typeof(express_getattr(self, 'BaseSurface', INDETERMINATE))) is not False

class IfcBridge_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBridge'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcBridgeTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcBridgeTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcBuildingElementPart_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBuildingElementPart'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcBuildingElementPartTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcBuildingElementPartTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcBuildingElementPart_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBuildingElementPart'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcbuildingelementparttype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcBuildingElementPartType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBuildingElementPartType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcBuildingElementPartTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcBuildingElementPartTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcBuildingElementProxy_HasObjectName:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBuildingElementProxy'
    RULE_NAME = 'HasObjectName'

    @staticmethod
    def __call__(self):
        assert exists(express_getattr(self, 'Name', INDETERMINATE)) is not False

class IfcBuildingElementProxy_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBuildingElementProxy'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcBuildingElementProxyTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcBuildingElementProxyTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcBuildingElementProxy_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBuildingElementProxy'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcbuildingelementproxytype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcBuildingElementProxyType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBuildingElementProxyType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcBuildingElementProxyTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcBuildingElementProxyTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcBuiltElement_MaxOneMaterialAssociation:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBuiltElement'
    RULE_NAME = 'MaxOneMaterialAssociation'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in express_getattr(self, 'HasAssociations', INDETERMINATE) if 'ifc4x3_rc4.ifcrelassociatesmaterial' in typeof(temp)]) <= 1) is not False

class IfcBuiltSystem_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBuiltSystem'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcBuiltSystemTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcBuiltSystemTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcBurner_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBurner'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcBurnerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcBurnerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcBurner_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBurner'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcburnertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcBurnerType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBurnerType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcBurnerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcBurnerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCShapeProfileDef_ValidGirth:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCShapeProfileDef'
    RULE_NAME = 'ValidGirth'

    @staticmethod
    def __call__(self):
        depth = express_getattr(self, 'Depth', INDETERMINATE)
        girth = express_getattr(self, 'Girth', INDETERMINATE)
        assert (girth < depth / 2.0) is not False

class IfcCShapeProfileDef_ValidInternalFilletRadius:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCShapeProfileDef'
    RULE_NAME = 'ValidInternalFilletRadius'

    @staticmethod
    def __call__(self):
        depth = express_getattr(self, 'Depth', INDETERMINATE)
        width = express_getattr(self, 'Width', INDETERMINATE)
        wallthickness = express_getattr(self, 'WallThickness', INDETERMINATE)
        internalfilletradius = express_getattr(self, 'InternalFilletRadius', INDETERMINATE)
        assert (not exists(internalfilletradius) or (internalfilletradius <= width / 2.0 - wallthickness and internalfilletradius <= depth / 2.0 - wallthickness)) is not False

class IfcCShapeProfileDef_ValidWallThickness:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCShapeProfileDef'
    RULE_NAME = 'ValidWallThickness'

    @staticmethod
    def __call__(self):
        depth = express_getattr(self, 'Depth', INDETERMINATE)
        width = express_getattr(self, 'Width', INDETERMINATE)
        wallthickness = express_getattr(self, 'WallThickness', INDETERMINATE)
        assert (wallthickness < width / 2.0 and wallthickness < depth / 2.0) is not False

class IfcCableCarrierFitting_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCableCarrierFitting'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcCableCarrierFittingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCableCarrierFittingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcCableCarrierFitting_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCableCarrierFitting'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifccablecarrierfittingtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcCableCarrierFittingType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCableCarrierFittingType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcCableCarrierFittingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCableCarrierFittingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCableCarrierSegment_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCableCarrierSegment'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcCableCarrierSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCableCarrierSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcCableCarrierSegment_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCableCarrierSegment'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifccablecarriersegmenttype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcCableCarrierSegmentType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCableCarrierSegmentType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcCableCarrierSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCableCarrierSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCableFitting_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCableFitting'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcCableFittingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCableFittingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcCableFitting_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCableFitting'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifccablefittingtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcCableFittingType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCableFittingType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcCableFittingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCableFittingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCableSegment_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCableSegment'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcCableSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCableSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcCableSegment_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCableSegment'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifccablesegmenttype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcCableSegmentType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCableSegmentType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcCableSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCableSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCaissonFoundation_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCaissonFoundation'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcCaissonFoundationTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCaissonFoundationTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcCaissonFoundation_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCaissonFoundation'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifccaissonfoundationtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcCaissonFoundationType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCaissonFoundationType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcCaissonFoundationTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCaissonFoundationTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCartesianPoint_CP2Dor3D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianPoint'
    RULE_NAME = 'CP2Dor3D'

    @staticmethod
    def __call__(self):
        coordinates = express_getattr(self, 'Coordinates', INDETERMINATE)
        assert (hiindex(coordinates) >= 2) is not False

def calc_IfcCartesianPoint_Dim(self):
    coordinates = express_getattr(self, 'Coordinates', INDETERMINATE)
    return hiindex(coordinates)

def calc_IfcCartesianPointList_Dim(self):
    return IfcPointListDim(self)

class IfcCartesianTransformationOperator_ScaleGreaterZero:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator'
    RULE_NAME = 'ScaleGreaterZero'

    @staticmethod
    def __call__(self):
        scl = express_getattr(self, 'Scl', INDETERMINATE)
        assert (scl > 0.0) is not False

def calc_IfcCartesianTransformationOperator_Scl(self):
    scale = express_getattr(self, 'Scale', INDETERMINATE)
    return nvl(scale, 1.0)

def calc_IfcCartesianTransformationOperator_Dim(self):
    localorigin = express_getattr(self, 'LocalOrigin', INDETERMINATE)
    return express_getattr(localorigin, 'Dim', INDETERMINATE)

class IfcCartesianTransformationOperator2D_DimEqual2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator2D'
    RULE_NAME = 'DimEqual2'

    @staticmethod
    def __call__(self):
        assert (express_getattr(self, 'Dim', INDETERMINATE) == 2) is not False

class IfcCartesianTransformationOperator2D_Axis1Is2D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator2D'
    RULE_NAME = 'Axis1Is2D'

    @staticmethod
    def __call__(self):
        assert (not exists(express_getattr(self, 'Axis1', INDETERMINATE)) or express_getattr(express_getattr(self, 'Axis1', INDETERMINATE), 'Dim', INDETERMINATE) == 2) is not False

class IfcCartesianTransformationOperator2D_Axis2Is2D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator2D'
    RULE_NAME = 'Axis2Is2D'

    @staticmethod
    def __call__(self):
        assert (not exists(express_getattr(self, 'Axis2', INDETERMINATE)) or express_getattr(express_getattr(self, 'Axis2', INDETERMINATE), 'Dim', INDETERMINATE) == 2) is not False

def calc_IfcCartesianTransformationOperator2D_U(self):
    return IfcBaseAxis(2, express_getattr(self, 'Axis1', INDETERMINATE), express_getattr(self, 'Axis2', INDETERMINATE), None)

class IfcCartesianTransformationOperator2DnonUniform_Scale2GreaterZero:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator2DnonUniform'
    RULE_NAME = 'Scale2GreaterZero'

    @staticmethod
    def __call__(self):
        scl2 = express_getattr(self, 'Scl2', INDETERMINATE)
        assert (scl2 > 0.0) is not False

def calc_IfcCartesianTransformationOperator2DnonUniform_Scl2(self):
    scale2 = express_getattr(self, 'Scale2', INDETERMINATE)
    return nvl(scale2, express_getattr(self, 'Scl', INDETERMINATE))

class IfcCartesianTransformationOperator3D_DimIs3D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator3D'
    RULE_NAME = 'DimIs3D'

    @staticmethod
    def __call__(self):
        assert (express_getattr(self, 'Dim', INDETERMINATE) == 3) is not False

class IfcCartesianTransformationOperator3D_Axis1Is3D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator3D'
    RULE_NAME = 'Axis1Is3D'

    @staticmethod
    def __call__(self):
        assert (not exists(express_getattr(self, 'Axis1', INDETERMINATE)) or express_getattr(express_getattr(self, 'Axis1', INDETERMINATE), 'Dim', INDETERMINATE) == 3) is not False

class IfcCartesianTransformationOperator3D_Axis2Is3D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator3D'
    RULE_NAME = 'Axis2Is3D'

    @staticmethod
    def __call__(self):
        assert (not exists(express_getattr(self, 'Axis2', INDETERMINATE)) or express_getattr(express_getattr(self, 'Axis2', INDETERMINATE), 'Dim', INDETERMINATE) == 3) is not False

class IfcCartesianTransformationOperator3D_Axis3Is3D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator3D'
    RULE_NAME = 'Axis3Is3D'

    @staticmethod
    def __call__(self):
        axis3 = express_getattr(self, 'Axis3', INDETERMINATE)
        assert (not exists(axis3) or express_getattr(axis3, 'Dim', INDETERMINATE) == 3) is not False

def calc_IfcCartesianTransformationOperator3D_U(self):
    axis3 = express_getattr(self, 'Axis3', INDETERMINATE)
    return IfcBaseAxis(3, express_getattr(self, 'Axis1', INDETERMINATE), express_getattr(self, 'Axis2', INDETERMINATE), axis3)

class IfcCartesianTransformationOperator3DnonUniform_Scale2GreaterZero:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator3DnonUniform'
    RULE_NAME = 'Scale2GreaterZero'

    @staticmethod
    def __call__(self):
        scl2 = express_getattr(self, 'Scl2', INDETERMINATE)
        assert (scl2 > 0.0) is not False

class IfcCartesianTransformationOperator3DnonUniform_Scale3GreaterZero:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator3DnonUniform'
    RULE_NAME = 'Scale3GreaterZero'

    @staticmethod
    def __call__(self):
        scl3 = express_getattr(self, 'Scl3', INDETERMINATE)
        assert (scl3 > 0.0) is not False

def calc_IfcCartesianTransformationOperator3DnonUniform_Scl2(self):
    scale2 = express_getattr(self, 'Scale2', INDETERMINATE)
    return nvl(scale2, express_getattr(self, 'Scl', INDETERMINATE))

def calc_IfcCartesianTransformationOperator3DnonUniform_Scl3(self):
    scale3 = express_getattr(self, 'Scale3', INDETERMINATE)
    return nvl(scale3, express_getattr(self, 'Scl', INDETERMINATE))

class IfcChiller_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcChiller'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcChillerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcChillerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcChiller_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcChiller'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcchillertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcChillerType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcChillerType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcChillerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcChillerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcChimney_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcChimney'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcChimneyTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcChimneyTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcChimney_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcChimney'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcchimneytype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcChimneyType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcChimneyType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcChimneyTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcChimneyTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCircleHollowProfileDef_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCircleHollowProfileDef'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        wallthickness = express_getattr(self, 'WallThickness', INDETERMINATE)
        assert (wallthickness < express_getattr(self, 'Radius', INDETERMINATE)) is not False

class IfcCoil_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCoil'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcCoilTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCoilTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcCoil_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCoil'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifccoiltype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcCoilType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCoilType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcCoilTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCoilTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcColumn_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcColumn'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcColumnTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcColumnTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcColumn_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcColumn'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifccolumntype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcColumnStandardCase_HasMaterialProfileSetUsage:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcColumnStandardCase'
    RULE_NAME = 'HasMaterialProfileSetUsage'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in usedin(self, 'ifc4x3_rc4.ifcrelassociates.relatedobjects') if 'ifc4x3_rc4.ifcrelassociatesmaterial' in typeof(temp) and 'ifc4x3_rc4.ifcmaterialprofilesetusage' in typeof(express_getattr(temp, 'RelatingMaterial', INDETERMINATE))]) == 1) is not False

class IfcColumnType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcColumnType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcColumnTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcColumnTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCommunicationsAppliance_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCommunicationsAppliance'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcCommunicationsApplianceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCommunicationsApplianceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcCommunicationsAppliance_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCommunicationsAppliance'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifccommunicationsappliancetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcCommunicationsApplianceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCommunicationsApplianceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcCommunicationsApplianceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCommunicationsApplianceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcComplexProperty_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcComplexProperty'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        hasproperties = express_getattr(self, 'HasProperties', INDETERMINATE)
        assert (sizeof([temp for temp in hasproperties if self == temp]) == 0) is not False

class IfcComplexProperty_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcComplexProperty'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        hasproperties = express_getattr(self, 'HasProperties', INDETERMINATE)
        assert IfcUniquePropertyName(hasproperties) is not False

class IfcComplexPropertyTemplate_UniquePropertyNames:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcComplexPropertyTemplate'
    RULE_NAME = 'UniquePropertyNames'

    @staticmethod
    def __call__(self):
        haspropertytemplates = express_getattr(self, 'HasPropertyTemplates', INDETERMINATE)
        assert IfcUniquePropertyTemplateNames(haspropertytemplates) is not False

class IfcComplexPropertyTemplate_NoSelfReference:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcComplexPropertyTemplate'
    RULE_NAME = 'NoSelfReference'

    @staticmethod
    def __call__(self):
        haspropertytemplates = express_getattr(self, 'HasPropertyTemplates', INDETERMINATE)
        assert (sizeof([temp for temp in haspropertytemplates if self == temp]) == 0) is not False

class IfcCompositeCurve_CurveContinuous:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCompositeCurve'
    RULE_NAME = 'CurveContinuous'

    @staticmethod
    def __call__(self):
        segments = express_getattr(self, 'Segments', INDETERMINATE)
        closedcurve = express_getattr(self, 'ClosedCurve', INDETERMINATE)
        assert (not closedcurve and sizeof([temp for temp in segments if express_getattr(temp, 'Transition', INDETERMINATE) == discontinuous]) == 1 or (closedcurve and sizeof([temp for temp in segments if express_getattr(temp, 'Transition', INDETERMINATE) == discontinuous]) == 0)) is not False

class IfcCompositeCurve_SameDim:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCompositeCurve'
    RULE_NAME = 'SameDim'

    @staticmethod
    def __call__(self):
        segments = express_getattr(self, 'Segments', INDETERMINATE)
        assert (sizeof([temp for temp in segments if express_getattr(temp, 'Dim', INDETERMINATE) != express_getattr(express_getitem(segments, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)]) == 0) is not False

def calc_IfcCompositeCurve_NSegments(self):
    segments = express_getattr(self, 'Segments', INDETERMINATE)
    return sizeof(segments)

def calc_IfcCompositeCurve_ClosedCurve(self):
    segments = express_getattr(self, 'Segments', INDETERMINATE)
    nsegments = express_getattr(self, 'NSegments', INDETERMINATE)
    return express_getattr(express_getitem(segments, nsegments - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Transition', INDETERMINATE) != discontinuous

class IfcCompositeCurveOnSurface_SameSurface:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCompositeCurveOnSurface'
    RULE_NAME = 'SameSurface'

    @staticmethod
    def __call__(self):
        basissurface = express_getattr(self, 'BasisSurface', INDETERMINATE)
        assert (sizeof(basissurface) > 0) is not False

def calc_IfcCompositeCurveOnSurface_BasisSurface(self):
    return IfcGetBasisSurface(self)

class IfcCompositeCurveSegment_ParentIsBoundedCurve:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCompositeCurveSegment'
    RULE_NAME = 'ParentIsBoundedCurve'

    @staticmethod
    def __call__(self):
        parentcurve = express_getattr(self, 'ParentCurve', INDETERMINATE)
        assert ('ifc4x3_rc4.ifcboundedcurve' in typeof(parentcurve)) is not False

def calc_IfcCompositeCurveSegment_Dim(self):
    parentcurve = express_getattr(self, 'ParentCurve', INDETERMINATE)
    return express_getattr(parentcurve, 'Dim', INDETERMINATE)

class IfcCompositeProfileDef_InvariantProfileType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCompositeProfileDef'
    RULE_NAME = 'InvariantProfileType'

    @staticmethod
    def __call__(self):
        profiles = express_getattr(self, 'Profiles', INDETERMINATE)
        assert (sizeof([temp for temp in profiles if express_getattr(temp, 'ProfileType', INDETERMINATE) != express_getattr(express_getitem(profiles, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'ProfileType', INDETERMINATE)]) == 0) is not False

class IfcCompositeProfileDef_NoRecursion:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCompositeProfileDef'
    RULE_NAME = 'NoRecursion'

    @staticmethod
    def __call__(self):
        profiles = express_getattr(self, 'Profiles', INDETERMINATE)
        assert (sizeof([temp for temp in profiles if 'ifc4x3_rc4.ifccompositeprofiledef' in typeof(temp)]) == 0) is not False

class IfcCompressor_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCompressor'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcCompressorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCompressorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcCompressor_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCompressor'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifccompressortype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcCompressorType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCompressorType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcCompressorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCompressorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCondenser_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCondenser'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcCondenserTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCondenserTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcCondenser_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCondenser'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifccondensertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcCondenserType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCondenserType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcCondenserTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCondenserTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcConstraint_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConstraint'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        constraintgrade = express_getattr(self, 'ConstraintGrade', INDETERMINATE)
        assert (constraintgrade != express_getattr(IfcConstraintEnum, 'USERDEFINED', INDETERMINATE) or (constraintgrade == express_getattr(IfcConstraintEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'UserDefinedGrade', INDETERMINATE)))) is not False

class IfcConstructionEquipmentResource_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConstructionEquipmentResource'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcConstructionEquipmentResourceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcConstructionEquipmentResourceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcConstructionEquipmentResourceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConstructionEquipmentResourceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcConstructionEquipmentResourceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcConstructionEquipmentResourceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ResourceType', INDETERMINATE)))) is not False

class IfcConstructionMaterialResource_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConstructionMaterialResource'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcConstructionMaterialResourceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcConstructionMaterialResourceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcConstructionMaterialResourceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConstructionMaterialResourceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcConstructionMaterialResourceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcConstructionMaterialResourceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ResourceType', INDETERMINATE)))) is not False

class IfcConstructionProductResource_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConstructionProductResource'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcConstructionProductResourceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcConstructionProductResourceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcConstructionProductResourceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConstructionProductResourceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcConstructionProductResourceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcConstructionProductResourceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ResourceType', INDETERMINATE)))) is not False

class IfcController_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcController'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcControllerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcControllerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcController_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcController'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifccontrollertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcControllerType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcControllerType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcControllerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcControllerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcConveyorSegment_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConveyorSegment'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcConveyorSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcConveyorSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcConveyorSegment_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConveyorSegment'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcconveyorsegmenttype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcConveyorSegmentType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConveyorSegmentType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcConveyorSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcConveyorSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCooledBeam_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCooledBeam'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcCooledBeamTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCooledBeamTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcCooledBeam_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCooledBeam'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifccooledbeamtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcCooledBeamType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCooledBeamType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcCooledBeamTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCooledBeamTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCoolingTower_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCoolingTower'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcCoolingTowerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCoolingTowerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcCoolingTower_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCoolingTower'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifccoolingtowertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcCoolingTowerType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCoolingTowerType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcCoolingTowerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCoolingTowerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCourse_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCourse'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcCourseTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCourseTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcCourse_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCourse'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifccoursetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcCourseType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCourseType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcCourseTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCourseTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCovering_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCovering'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcCoveringTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCoveringTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcCovering_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCovering'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifccoveringtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcCoveringType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCoveringType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcCoveringTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCoveringTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCrewResource_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCrewResource'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcCrewResourceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCrewResourceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcCrewResourceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCrewResourceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcCrewResourceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCrewResourceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ResourceType', INDETERMINATE)))) is not False

def calc_IfcCsgPrimitive3D_Dim(self):
    return 3

class IfcCurtainWall_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCurtainWall'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcCurtainWallTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCurtainWallTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcCurtainWall_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCurtainWall'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifccurtainwalltype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcCurtainWallType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCurtainWallType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcCurtainWallTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCurtainWallTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

def calc_IfcCurve_Dim(self):
    return IfcCurveDim(self)

def calc_IfcCurveSegment_Dim(self):
    parentcurve = express_getattr(self, 'ParentCurve', INDETERMINATE)
    return express_getattr(parentcurve, 'Dim', INDETERMINATE)

class IfcCurveStyle_MeasureOfWidth:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCurveStyle'
    RULE_NAME = 'MeasureOfWidth'

    @staticmethod
    def __call__(self):
        curvewidth = express_getattr(self, 'CurveWidth', INDETERMINATE)
        assert (not exists(curvewidth) or 'ifc4x3_rc4.ifcpositivelengthmeasure' in typeof(curvewidth) or ('ifc4x3_rc4.ifcdescriptivemeasure' in typeof(curvewidth) and curvewidth == 'bylayer')) is not False

class IfcCurveStyle_IdentifiableCurveStyle:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCurveStyle'
    RULE_NAME = 'IdentifiableCurveStyle'

    @staticmethod
    def __call__(self):
        curvefont = express_getattr(self, 'CurveFont', INDETERMINATE)
        curvewidth = express_getattr(self, 'CurveWidth', INDETERMINATE)
        curvecolour = express_getattr(self, 'CurveColour', INDETERMINATE)
        assert (exists(curvefont) or exists(curvewidth) or exists(curvecolour)) is not False

class IfcCurveStyleFontPattern_VisibleLengthGreaterEqualZero:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCurveStyleFontPattern'
    RULE_NAME = 'VisibleLengthGreaterEqualZero'

    @staticmethod
    def __call__(self):
        visiblesegmentlength = express_getattr(self, 'VisibleSegmentLength', INDETERMINATE)
        assert (visiblesegmentlength >= 0.0) is not False

class IfcDamper_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDamper'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcDamperTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcDamperTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcDamper_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDamper'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcdampertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcDamperType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDamperType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcDamperTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcDamperTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcDeepFoundation_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDeepFoundation'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcdeepfoundationtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcDerivedProfileDef_InvariantProfileType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDerivedProfileDef'
    RULE_NAME = 'InvariantProfileType'

    @staticmethod
    def __call__(self):
        parentprofile = express_getattr(self, 'ParentProfile', INDETERMINATE)
        assert (express_getattr(self, 'ProfileType', INDETERMINATE) == express_getattr(parentprofile, 'ProfileType', INDETERMINATE)) is not False

class IfcDerivedUnit_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDerivedUnit'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        elements = express_getattr(self, 'Elements', INDETERMINATE)
        assert (sizeof(elements) > 1 or (sizeof(elements) == 1 and express_getattr(express_getitem(elements, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Exponent', INDETERMINATE) != 1)) is not False

class IfcDerivedUnit_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDerivedUnit'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        unittype = express_getattr(self, 'UnitType', INDETERMINATE)
        assert (unittype != express_getattr(IfcDerivedUnitEnum, 'USERDEFINED', INDETERMINATE) or (unittype == express_getattr(IfcDerivedUnitEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'UserDefinedType', INDETERMINATE)))) is not False

def calc_IfcDerivedUnit_Dimensions(self):
    elements = express_getattr(self, 'Elements', INDETERMINATE)
    return IfcDeriveDimensionalExponents(elements)

class IfcDirection_MagnitudeGreaterZero:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDirection'
    RULE_NAME = 'MagnitudeGreaterZero'

    @staticmethod
    def __call__(self):
        directionratios = express_getattr(self, 'DirectionRatios', INDETERMINATE)
        assert (sizeof([tmp for tmp in directionratios if tmp != 0.0]) > 0) is not False

def calc_IfcDirection_Dim(self):
    directionratios = express_getattr(self, 'DirectionRatios', INDETERMINATE)
    return hiindex(directionratios)

class IfcDirectrixCurveSweptAreaSolid_DirectrixBounded:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDirectrixCurveSweptAreaSolid'
    RULE_NAME = 'DirectrixBounded'

    @staticmethod
    def __call__(self):
        directrix = express_getattr(self, 'Directrix', INDETERMINATE)
        startparam = express_getattr(self, 'StartParam', INDETERMINATE)
        endparam = express_getattr(self, 'EndParam', INDETERMINATE)
        assert (exists(startparam) and exists(endparam) or sizeof(['ifc4x3_rc4.ifcconic', 'ifc4x3_rc4.ifcboundedcurve'] * typeof(directrix)) == 1) is not False

class IfcDiscreteAccessory_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDiscreteAccessory'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcDiscreteAccessoryTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcDiscreteAccessoryTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcDiscreteAccessory_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDiscreteAccessory'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcdiscreteaccessorytype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcDiscreteAccessoryType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDiscreteAccessoryType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcDiscreteAccessoryTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcDiscreteAccessoryTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcDistributionBoard_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDistributionBoard'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcDistributionBoardTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcDistributionBoardTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcDistributionBoard_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDistributionBoard'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcdistributionboardtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcDistributionBoardType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDistributionBoardType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcDistributionBoardTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcDistributionBoardTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcDistributionChamberElement_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDistributionChamberElement'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcDistributionChamberElementTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcDistributionChamberElementTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcDistributionChamberElement_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDistributionChamberElement'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcdistributionchamberelementtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcDistributionChamberElementType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDistributionChamberElementType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcDistributionChamberElementTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcDistributionChamberElementTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcDistributionSystem_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDistributionSystem'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcDistributionSystemEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcDistributionSystemEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcDocumentReference_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDocumentReference'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        name = express_getattr(self, 'Name', INDETERMINATE)
        referenceddocument = express_getattr(self, 'ReferencedDocument', INDETERMINATE)
        assert exists(name) ^ exists(referenceddocument) is not False

class IfcDoor_CorrectStyleAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDoor'
    RULE_NAME = 'CorrectStyleAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcdoortype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcDoor_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDoor'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcDoorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcDoorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcDoor_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDoor'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcdoortype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcDoorLiningProperties_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDoorLiningProperties'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        liningdepth = express_getattr(self, 'LiningDepth', INDETERMINATE)
        liningthickness = express_getattr(self, 'LiningThickness', INDETERMINATE)
        assert (not (exists(liningdepth) and (not exists(liningthickness)))) is not False

class IfcDoorLiningProperties_WR32:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDoorLiningProperties'
    RULE_NAME = 'WR32'

    @staticmethod
    def __call__(self):
        thresholddepth = express_getattr(self, 'ThresholdDepth', INDETERMINATE)
        thresholdthickness = express_getattr(self, 'ThresholdThickness', INDETERMINATE)
        assert (not (exists(thresholddepth) and (not exists(thresholdthickness)))) is not False

class IfcDoorLiningProperties_WR33:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDoorLiningProperties'
    RULE_NAME = 'WR33'

    @staticmethod
    def __call__(self):
        transomthickness = express_getattr(self, 'TransomThickness', INDETERMINATE)
        transomoffset = express_getattr(self, 'TransomOffset', INDETERMINATE)
        assert (exists(transomoffset) and exists(transomthickness)) ^ (not exists(transomoffset) and (not exists(transomthickness))) is not False

class IfcDoorLiningProperties_WR34:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDoorLiningProperties'
    RULE_NAME = 'WR34'

    @staticmethod
    def __call__(self):
        casingthickness = express_getattr(self, 'CasingThickness', INDETERMINATE)
        casingdepth = express_getattr(self, 'CasingDepth', INDETERMINATE)
        assert (exists(casingdepth) and exists(casingthickness)) ^ (not exists(casingdepth) and (not exists(casingthickness))) is not False

class IfcDoorLiningProperties_WR35:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDoorLiningProperties'
    RULE_NAME = 'WR35'

    @staticmethod
    def __call__(self):
        assert (exists(lambda : express_getitem(express_getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and ('ifc4x3_rc4.ifcdoortype' in typeof(express_getitem(express_getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) or 'ifc4x3_rc4.ifcdoorstyle' in typeof(express_getitem(express_getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)))) is not False

class IfcDoorPanelProperties_ApplicableToType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDoorPanelProperties'
    RULE_NAME = 'ApplicableToType'

    @staticmethod
    def __call__(self):
        assert (exists(lambda : express_getitem(express_getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and ('ifc4x3_rc4.ifcdoortype' in typeof(express_getitem(express_getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) or 'ifc4x3_rc4.ifcdoorstyle' in typeof(express_getitem(express_getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)))) is not False

class IfcDoorType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDoorType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcDoorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcDoorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcDraughtingPreDefinedColour_PreDefinedColourNames:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDraughtingPreDefinedColour'
    RULE_NAME = 'PreDefinedColourNames'

    @staticmethod
    def __call__(self):
        assert (express_getattr(express_getattr(self, 'Name', INDETERMINATE), 'lower', INDETERMINATE)() in ['black', 'red', 'green', 'blue', 'yellow', 'magenta', 'cyan', 'white', 'bylayer']) is not False

class IfcDraughtingPreDefinedCurveFont_PreDefinedCurveFontNames:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDraughtingPreDefinedCurveFont'
    RULE_NAME = 'PreDefinedCurveFontNames'

    @staticmethod
    def __call__(self):
        assert (express_getattr(express_getattr(self, 'Name', INDETERMINATE), 'lower', INDETERMINATE)() in ['continuous', 'chain', 'chaindoubledash', 'dashed', 'dotted', 'bylayer']) is not False

class IfcDuctFitting_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDuctFitting'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcDuctFittingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcDuctFittingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcDuctFitting_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDuctFitting'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcductfittingtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcDuctFittingType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDuctFittingType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcDuctFittingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcDuctFittingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcDuctSegment_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDuctSegment'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcDuctSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcDuctSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcDuctSegment_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDuctSegment'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcductsegmenttype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcDuctSegmentType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDuctSegmentType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcDuctSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcDuctSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcDuctSilencer_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDuctSilencer'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcDuctSilencerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcDuctSilencerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcDuctSilencer_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDuctSilencer'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcductsilencertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcDuctSilencerType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDuctSilencerType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcDuctSilencerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcDuctSilencerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcEarthworksCut_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEarthworksCut'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcEarthworksCutTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcEarthworksCutTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcEarthworksFill_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEarthworksFill'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcEarthworksFillTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcEarthworksFillTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcEdgeLoop_IsClosed:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEdgeLoop'
    RULE_NAME = 'IsClosed'

    @staticmethod
    def __call__(self):
        edgelist = express_getattr(self, 'EdgeList', INDETERMINATE)
        ne = express_getattr(self, 'Ne', INDETERMINATE)
        assert (express_getattr(express_getitem(edgelist, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'EdgeStart', INDETERMINATE) == express_getattr(express_getitem(edgelist, ne - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'EdgeEnd', INDETERMINATE)) is not False

class IfcEdgeLoop_IsContinuous:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEdgeLoop'
    RULE_NAME = 'IsContinuous'

    @staticmethod
    def __call__(self):
        assert IfcLoopHeadToTail(self) is not False

def calc_IfcEdgeLoop_Ne(self):
    edgelist = express_getattr(self, 'EdgeList', INDETERMINATE)
    return sizeof(edgelist)

class IfcElectricAppliance_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricAppliance'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcElectricApplianceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcElectricApplianceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcElectricAppliance_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricAppliance'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcelectricappliancetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcElectricApplianceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricApplianceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcElectricApplianceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcElectricApplianceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcElectricDistributionBoard_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricDistributionBoard'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcElectricDistributionBoardTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcElectricDistributionBoardTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcElectricDistributionBoard_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricDistributionBoard'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcelectricdistributionboardtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcElectricDistributionBoardType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricDistributionBoardType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcElectricDistributionBoardTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcElectricDistributionBoardTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcElectricFlowStorageDevice_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricFlowStorageDevice'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcElectricFlowStorageDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcElectricFlowStorageDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcElectricFlowStorageDevice_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricFlowStorageDevice'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcelectricflowstoragedevicetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcElectricFlowStorageDeviceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricFlowStorageDeviceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcElectricFlowStorageDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcElectricFlowStorageDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcElectricFlowTreatmentDevice_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricFlowTreatmentDevice'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcElectricFlowTreatmentDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcElectricFlowTreatmentDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcElectricFlowTreatmentDevice_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricFlowTreatmentDevice'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcelectricflowtreatmentdevicetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcElectricFlowTreatmentDeviceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricFlowTreatmentDeviceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcElectricFlowTreatmentDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcElectricFlowTreatmentDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcElectricGenerator_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricGenerator'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcElectricGeneratorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcElectricGeneratorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcElectricGenerator_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricGenerator'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcelectricgeneratortype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcElectricGeneratorType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricGeneratorType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcElectricGeneratorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcElectricGeneratorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcElectricMotor_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricMotor'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcElectricMotorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcElectricMotorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcElectricMotor_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricMotor'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcelectricmotortype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcElectricMotorType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricMotorType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcElectricMotorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcElectricMotorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcElectricTimeControl_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricTimeControl'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcElectricTimeControlTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcElectricTimeControlTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcElectricTimeControl_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricTimeControl'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcelectrictimecontroltype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcElectricTimeControlType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricTimeControlType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcElectricTimeControlTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcElectricTimeControlTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcElementAssembly_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElementAssembly'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcElementAssemblyTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcElementAssemblyTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcElementAssembly_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElementAssembly'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcelementassemblytype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcElementAssemblyType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElementAssemblyType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcElementAssemblyTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcElementAssemblyTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcElementQuantity_UniqueQuantityNames:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElementQuantity'
    RULE_NAME = 'UniqueQuantityNames'

    @staticmethod
    def __call__(self):
        quantities = express_getattr(self, 'Quantities', INDETERMINATE)
        assert IfcUniqueQuantityNames(quantities) is not False

class IfcEngine_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEngine'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcEngineTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcEngineTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcEngine_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEngine'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcenginetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcEngineType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEngineType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcEngineTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcEngineTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcEvaporativeCooler_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEvaporativeCooler'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcEvaporativeCoolerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcEvaporativeCoolerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcEvaporativeCooler_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEvaporativeCooler'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcevaporativecoolertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcEvaporativeCoolerType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEvaporativeCoolerType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcEvaporativeCoolerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcEvaporativeCoolerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcEvaporator_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEvaporator'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcEvaporatorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcEvaporatorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcEvaporator_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEvaporator'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcevaporatortype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcEvaporatorType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEvaporatorType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcEvaporatorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcEvaporatorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcEvent_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEvent'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcEventTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcEventTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcEvent_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEvent'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        eventtriggertype = express_getattr(self, 'EventTriggerType', INDETERMINATE)
        userdefinedeventtriggertype = express_getattr(self, 'UserDefinedEventTriggerType', INDETERMINATE)
        assert (not exists(eventtriggertype) or eventtriggertype != express_getattr(IfcEventTriggerTypeEnum, 'USERDEFINED', INDETERMINATE) or (eventtriggertype == express_getattr(IfcEventTriggerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(userdefinedeventtriggertype))) is not False

class IfcEventType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEventType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcEventTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcEventTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ProcessType', INDETERMINATE)))) is not False

class IfcEventType_CorrectEventTriggerType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEventType'
    RULE_NAME = 'CorrectEventTriggerType'

    @staticmethod
    def __call__(self):
        eventtriggertype = express_getattr(self, 'EventTriggerType', INDETERMINATE)
        userdefinedeventtriggertype = express_getattr(self, 'UserDefinedEventTriggerType', INDETERMINATE)
        assert (eventtriggertype != express_getattr(IfcEventTriggerTypeEnum, 'USERDEFINED', INDETERMINATE) or (eventtriggertype == express_getattr(IfcEventTriggerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(userdefinedeventtriggertype))) is not False

class IfcExternalReference_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcExternalReference'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        location = express_getattr(self, 'Location', INDETERMINATE)
        identification = express_getattr(self, 'Identification', INDETERMINATE)
        name = express_getattr(self, 'Name', INDETERMINATE)
        assert (exists(identification) or exists(location) or exists(name)) is not False

class IfcExtrudedAreaSolid_ValidExtrusionDirection:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcExtrudedAreaSolid'
    RULE_NAME = 'ValidExtrusionDirection'

    @staticmethod
    def __call__(self):
        assert (IfcDotProduct(IfcDirection(DirectionRatios=[0.0, 0.0, 1.0]), express_getattr(self, 'ExtrudedDirection', INDETERMINATE)) != 0.0) is not False

class IfcExtrudedAreaSolidTapered_CorrectProfileAssignment:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcExtrudedAreaSolidTapered'
    RULE_NAME = 'CorrectProfileAssignment'

    @staticmethod
    def __call__(self):
        assert IfcTaperedSweptAreaProfiles(express_getattr(self, 'SweptArea', INDETERMINATE), express_getattr(self, 'EndSweptArea', INDETERMINATE)) is not False

class IfcFace_HasOuterBound:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFace'
    RULE_NAME = 'HasOuterBound'

    @staticmethod
    def __call__(self):
        bounds = express_getattr(self, 'Bounds', INDETERMINATE)
        assert (sizeof([temp for temp in bounds if 'ifc4x3_rc4.ifcfaceouterbound' in typeof(temp)]) <= 1) is not False

def calc_IfcFaceBasedSurfaceModel_Dim(self):
    return 3

class IfcFacilityPart_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFacilityPart'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert ((predefinedtype != express_getattr(IfcBridgePartTypeEnum, 'USERDEFINED', INDETERMINATE) or predefinedtype != express_getattr(IfcRailwayPartTypeEnum, 'USERDEFINED', INDETERMINATE) or predefinedtype != express_getattr(IfcRoadPartTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype != express_getattr(IfcMarinePartTypeEnum, 'USERDEFINED', INDETERMINATE)) or (predefinedtype != express_getattr(IfcFacilityPartCommonTypeEnum, 'USERDEFINED', INDETERMINATE))) or ((predefinedtype == express_getattr(IfcBridgePartTypeEnum, 'USERDEFINED', INDETERMINATE) or predefinedtype == express_getattr(IfcRailwayPartTypeEnum, 'USERDEFINED', INDETERMINATE) or predefinedtype == express_getattr(IfcRoadPartTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcMarinePartTypeEnum, 'USERDEFINED', INDETERMINATE)) or (predefinedtype == express_getattr(IfcFacilityPartCommonTypeEnum, 'USERDEFINED', INDETERMINATE))) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcFan_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFan'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcFanTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcFanTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcFan_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFan'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcfantype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcFanType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFanType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcFanTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcFanTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcFastener_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFastener'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcFastenerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcFastenerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcFastener_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFastener'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcfastenertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcFastenerType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFastenerType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcFastenerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcFastenerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcFeatureElement_NotContained:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFeatureElement'
    RULE_NAME = 'NotContained'

    @staticmethod
    def __call__(self):
        containedinstructure = express_getattr(self, 'ContainedInStructure', INDETERMINATE)
        assert (sizeof(containedinstructure) == 0) is not False

class IfcFeatureElementSubtraction_HasNoSubtraction:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFeatureElementSubtraction'
    RULE_NAME = 'HasNoSubtraction'

    @staticmethod
    def __call__(self):
        assert (sizeof(express_getattr(self, 'HasOpenings', INDETERMINATE)) == 0) is not False

class IfcFeatureElementSubtraction_IsNotFilling:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFeatureElementSubtraction'
    RULE_NAME = 'IsNotFilling'

    @staticmethod
    def __call__(self):
        assert (sizeof(express_getattr(self, 'FillsVoids', INDETERMINATE)) == 0) is not False

class IfcFillAreaStyle_MaxOneColour:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFillAreaStyle'
    RULE_NAME = 'MaxOneColour'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in express_getattr(self, 'FillStyles', INDETERMINATE) if 'ifc4x3_rc4.ifccolour' in typeof(style)]) <= 1) is not False

class IfcFillAreaStyle_MaxOneExtHatchStyle:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFillAreaStyle'
    RULE_NAME = 'MaxOneExtHatchStyle'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in express_getattr(self, 'FillStyles', INDETERMINATE) if 'ifc4x3_rc4.ifcexternallydefinedhatchstyle' in typeof(style)]) <= 1) is not False

class IfcFillAreaStyle_ConsistentHatchStyleDef:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFillAreaStyle'
    RULE_NAME = 'ConsistentHatchStyleDef'

    @staticmethod
    def __call__(self):
        assert IfcCorrectFillAreaStyle(express_getattr(self, 'FillStyles', INDETERMINATE)) is not False

class IfcFillAreaStyleHatching_PatternStart2D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFillAreaStyleHatching'
    RULE_NAME = 'PatternStart2D'

    @staticmethod
    def __call__(self):
        patternstart = express_getattr(self, 'PatternStart', INDETERMINATE)
        assert (not exists(patternstart) or express_getattr(patternstart, 'Dim', INDETERMINATE) == 2) is not False

class IfcFillAreaStyleHatching_RefHatchLine2D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFillAreaStyleHatching'
    RULE_NAME = 'RefHatchLine2D'

    @staticmethod
    def __call__(self):
        pointofreferencehatchline = express_getattr(self, 'PointOfReferenceHatchLine', INDETERMINATE)
        assert (not exists(pointofreferencehatchline) or express_getattr(pointofreferencehatchline, 'Dim', INDETERMINATE) == 2) is not False

class IfcFilter_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFilter'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcFilterTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcFilterTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcFilter_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFilter'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcfiltertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcFilterType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFilterType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcFilterTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcFilterTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcFireSuppressionTerminal_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFireSuppressionTerminal'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcFireSuppressionTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcFireSuppressionTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcFireSuppressionTerminal_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFireSuppressionTerminal'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcfiresuppressionterminaltype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcFireSuppressionTerminalType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFireSuppressionTerminalType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcFireSuppressionTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcFireSuppressionTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcFlowInstrument_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFlowInstrument'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcFlowInstrumentTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcFlowInstrumentTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcFlowInstrument_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFlowInstrument'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcflowinstrumenttype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcFlowInstrumentType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFlowInstrumentType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcFlowInstrumentTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcFlowInstrumentTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcFlowMeter_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFlowMeter'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcFlowMeterTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcFlowMeterTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcFlowMeter_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFlowMeter'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcflowmetertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcFlowMeterType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFlowMeterType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcFlowMeterTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcFlowMeterTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcFooting_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFooting'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcFootingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcFootingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcFooting_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFooting'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcfootingtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcFootingType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFootingType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcFootingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcFootingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcFurniture_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFurniture'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcFurnitureTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcFurnitureTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcFurniture_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFurniture'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcfurnituretype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcFurnitureType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFurnitureType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcFurnitureTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcFurnitureTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcGeographicElement_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGeographicElement'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcGeographicElementTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcGeographicElementTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcGeographicElement_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGeographicElement'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcgeographicelementtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcGeographicElementType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGeographicElementType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcGeographicElementTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcGeographicElementTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcGeometricCurveSet_NoSurfaces:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGeometricCurveSet'
    RULE_NAME = 'NoSurfaces'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in express_getattr(self, 'Elements', INDETERMINATE) if 'ifc4x3_rc4.ifcsurface' in typeof(temp)]) == 0) is not False

class IfcGeometricRepresentationContext_North2D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGeometricRepresentationContext'
    RULE_NAME = 'North2D'

    @staticmethod
    def __call__(self):
        truenorth = express_getattr(self, 'TrueNorth', INDETERMINATE)
        assert (not exists(truenorth) or hiindex(express_getattr(truenorth, 'DirectionRatios', INDETERMINATE)) == 2) is not False

class IfcGeometricRepresentationSubContext_ParentNoSub:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGeometricRepresentationSubContext'
    RULE_NAME = 'ParentNoSub'

    @staticmethod
    def __call__(self):
        parentcontext = express_getattr(self, 'ParentContext', INDETERMINATE)
        assert (not 'ifc4x3_rc4.ifcgeometricrepresentationsubcontext' in typeof(parentcontext)) is not False

class IfcGeometricRepresentationSubContext_UserTargetProvided:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGeometricRepresentationSubContext'
    RULE_NAME = 'UserTargetProvided'

    @staticmethod
    def __call__(self):
        targetview = express_getattr(self, 'TargetView', INDETERMINATE)
        userdefinedtargetview = express_getattr(self, 'UserDefinedTargetView', INDETERMINATE)
        assert (targetview != express_getattr(IfcGeometricProjectionEnum, 'USERDEFINED', INDETERMINATE) or (targetview == express_getattr(IfcGeometricProjectionEnum, 'USERDEFINED', INDETERMINATE) and exists(userdefinedtargetview))) is not False

class IfcGeometricRepresentationSubContext_NoCoordOperation:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGeometricRepresentationSubContext'
    RULE_NAME = 'NoCoordOperation'

    @staticmethod
    def __call__(self):
        assert (sizeof(express_getattr(self, 'HasCoordinateOperation', INDETERMINATE)) == 0) is not False

def calc_IfcGeometricRepresentationSubContext_WorldCoordinateSystem(self):
    parentcontext = express_getattr(self, 'ParentContext', INDETERMINATE)
    return express_getattr(parentcontext, 'WorldCoordinateSystem', INDETERMINATE)

def calc_IfcGeometricRepresentationSubContext_CoordinateSpaceDimension(self):
    parentcontext = express_getattr(self, 'ParentContext', INDETERMINATE)
    return express_getattr(parentcontext, 'CoordinateSpaceDimension', INDETERMINATE)

def calc_IfcGeometricRepresentationSubContext_TrueNorth(self):
    parentcontext = express_getattr(self, 'ParentContext', INDETERMINATE)
    return nvl(express_getattr(parentcontext, 'TrueNorth', INDETERMINATE), IfcConvertDirectionInto2D(express_getitem(express_getattr(express_getattr(self, 'WorldCoordinateSystem', INDETERMINATE), 'P', INDETERMINATE), 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)))

def calc_IfcGeometricRepresentationSubContext_Precision(self):
    parentcontext = express_getattr(self, 'ParentContext', INDETERMINATE)
    return nvl(express_getattr(parentcontext, 'Precision', INDETERMINATE), 1)

class IfcGeometricSet_ConsistentDim:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGeometricSet'
    RULE_NAME = 'ConsistentDim'

    @staticmethod
    def __call__(self):
        elements = express_getattr(self, 'Elements', INDETERMINATE)
        assert (sizeof([temp for temp in elements if express_getattr(temp, 'Dim', INDETERMINATE) != express_getattr(express_getitem(elements, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)]) == 0) is not False

def calc_IfcGeometricSet_Dim(self):
    elements = express_getattr(self, 'Elements', INDETERMINATE)
    return express_getattr(express_getitem(elements, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)

def calc_IfcGradientCurve_RelativeElevation(self):
    return IfcGradient(self)

class IfcGridAxis_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGridAxis'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        axiscurve = express_getattr(self, 'AxisCurve', INDETERMINATE)
        assert (express_getattr(axiscurve, 'Dim', INDETERMINATE) == 2) is not False

class IfcGridAxis_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGridAxis'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        partofw = express_getattr(self, 'PartOfW', INDETERMINATE)
        partofv = express_getattr(self, 'PartOfV', INDETERMINATE)
        partofu = express_getattr(self, 'PartOfU', INDETERMINATE)
        assert (sizeof(partofu) == 1) ^ (sizeof(partofv) == 1) ^ (sizeof(partofw) == 1) is not False

def calc_IfcHalfSpaceSolid_Dim(self):
    return 3

class IfcHeatExchanger_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcHeatExchanger'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcHeatExchangerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcHeatExchangerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcHeatExchanger_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcHeatExchanger'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcheatexchangertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcHeatExchangerType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcHeatExchangerType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcHeatExchangerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcHeatExchangerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcHumidifier_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcHumidifier'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcHumidifierTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcHumidifierTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcHumidifier_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcHumidifier'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifchumidifiertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcHumidifierType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcHumidifierType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcHumidifierTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcHumidifierTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcIShapeProfileDef_ValidFlangeThickness:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcIShapeProfileDef'
    RULE_NAME = 'ValidFlangeThickness'

    @staticmethod
    def __call__(self):
        overalldepth = express_getattr(self, 'OverallDepth', INDETERMINATE)
        flangethickness = express_getattr(self, 'FlangeThickness', INDETERMINATE)
        assert (2.0 * flangethickness < overalldepth) is not False

class IfcIShapeProfileDef_ValidWebThickness:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcIShapeProfileDef'
    RULE_NAME = 'ValidWebThickness'

    @staticmethod
    def __call__(self):
        overallwidth = express_getattr(self, 'OverallWidth', INDETERMINATE)
        webthickness = express_getattr(self, 'WebThickness', INDETERMINATE)
        assert (webthickness < overallwidth) is not False

class IfcIShapeProfileDef_ValidFilletRadius:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcIShapeProfileDef'
    RULE_NAME = 'ValidFilletRadius'

    @staticmethod
    def __call__(self):
        overallwidth = express_getattr(self, 'OverallWidth', INDETERMINATE)
        overalldepth = express_getattr(self, 'OverallDepth', INDETERMINATE)
        webthickness = express_getattr(self, 'WebThickness', INDETERMINATE)
        flangethickness = express_getattr(self, 'FlangeThickness', INDETERMINATE)
        filletradius = express_getattr(self, 'FilletRadius', INDETERMINATE)
        assert (not exists(filletradius) or (filletradius <= (overallwidth - webthickness) / 2.0 and filletradius <= (overalldepth - 2.0 * flangethickness) / 2.0)) is not False

class IfcImpactProtectionDevice_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcImpactProtectionDevice'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or (predefinedtype != express_getattr(IfcImpactProtectionDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or predefinedtype != express_getattr(IfcVibrationDamperTypeEnum, 'USERDEFINED', INDETERMINATE) or predefinedtype != express_getattr(IfcVibrationIsolatorTypeEnum, 'USERDEFINED', INDETERMINATE)) or ((predefinedtype == express_getattr(IfcImpactProtectionDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or predefinedtype == express_getattr(IfcVibrationDamperTypeEnum, 'USERDEFINED', INDETERMINATE) or predefinedtype == express_getattr(IfcVibrationIsolatorTypeEnum, 'USERDEFINED', INDETERMINATE)) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcImpactProtectionDevice_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcImpactProtectionDevice'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcimpactprotectiondevicetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcImpactProtectionDeviceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcImpactProtectionDeviceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert ((predefinedtype != express_getattr(IfcImpactProtectionDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or predefinedtype != express_getattr(IfcVibrationDamperTypeEnum, 'USERDEFINED', INDETERMINATE) or predefinedtype != express_getattr(IfcVibrationIsolatorTypeEnum, 'USERDEFINED', INDETERMINATE)) or ((predefinedtype == express_getattr(IfcImpactProtectionDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or predefinedtype == express_getattr(IfcVibrationDamperTypeEnum, 'USERDEFINED', INDETERMINATE) or predefinedtype == express_getattr(IfcVibrationIsolatorTypeEnum, 'USERDEFINED', INDETERMINATE)) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcIndexedPolyCurve_Consecutive:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcIndexedPolyCurve'
    RULE_NAME = 'Consecutive'

    @staticmethod
    def __call__(self):
        segments = express_getattr(self, 'Segments', INDETERMINATE)
        assert (not exists(segments) or IfcConsecutiveSegments(segments)) is not False

class IfcInterceptor_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcInterceptor'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcInterceptorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcInterceptorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcInterceptor_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcInterceptor'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcinterceptortype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcInterceptorType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcInterceptorType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcInterceptorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcInterceptorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcIntersectionCurve_TwoPCurves:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcIntersectionCurve'
    RULE_NAME = 'TwoPCurves'

    @staticmethod
    def __call__(self):
        assert (sizeof(express_getattr(self, 'AssociatedGeometry', INDETERMINATE)) == 2) is not False

class IfcIntersectionCurve_DistinctSurfaces:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcIntersectionCurve'
    RULE_NAME = 'DistinctSurfaces'

    @staticmethod
    def __call__(self):
        assert (IfcAssociatedSurface(express_getitem(express_getattr(self, 'AssociatedGeometry', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) != IfcAssociatedSurface(express_getitem(express_getattr(self, 'AssociatedGeometry', INDETERMINATE), 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))) is not False

class IfcJunctionBox_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcJunctionBox'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcJunctionBoxTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcJunctionBoxTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcJunctionBox_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcJunctionBox'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcjunctionboxtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcJunctionBoxType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcJunctionBoxType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcJunctionBoxTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcJunctionBoxTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcLShapeProfileDef_ValidThickness:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLShapeProfileDef'
    RULE_NAME = 'ValidThickness'

    @staticmethod
    def __call__(self):
        depth = express_getattr(self, 'Depth', INDETERMINATE)
        width = express_getattr(self, 'Width', INDETERMINATE)
        thickness = express_getattr(self, 'Thickness', INDETERMINATE)
        assert (thickness < depth and (not exists(width) or thickness < width)) is not False

class IfcLaborResource_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLaborResource'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcLaborResourceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcLaborResourceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcLaborResourceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLaborResourceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcLaborResourceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcLaborResourceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ResourceType', INDETERMINATE)))) is not False

class IfcLamp_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLamp'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcLampTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcLampTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcLamp_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLamp'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifclamptype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcLampType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLampType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcLampTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcLampTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcLightFixture_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLightFixture'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcLightFixtureTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcLightFixtureTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcLightFixture_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLightFixture'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifclightfixturetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcLightFixtureType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLightFixtureType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcLightFixtureTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcLightFixtureTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcLine_SameDim:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLine'
    RULE_NAME = 'SameDim'

    @staticmethod
    def __call__(self):
        pnt = express_getattr(self, 'Pnt', INDETERMINATE)
        dir = express_getattr(self, 'Dir', INDETERMINATE)
        assert (express_getattr(dir, 'Dim', INDETERMINATE) == express_getattr(pnt, 'Dim', INDETERMINATE)) is not False

class IfcLiquidTerminal_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLiquidTerminal'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcLiquidTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcLiquidTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcLiquidTerminal_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLiquidTerminal'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcliquidterminaltype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcLiquidTerminalType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLiquidTerminalType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcLiquidTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcLiquidTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcLocalPlacement_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLocalPlacement'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        placementrelto = express_getattr(self, 'PlacementRelTo', INDETERMINATE)
        relativeplacement = express_getattr(self, 'RelativePlacement', INDETERMINATE)
        assert IfcCorrectLocalPlacement(relativeplacement, placementrelto) is not False

class IfcMarineFacility_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMarineFacility'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcMarineFacilityTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcMarineFacilityTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcMaterialDefinitionRepresentation_OnlyStyledRepresentations:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMaterialDefinitionRepresentation'
    RULE_NAME = 'OnlyStyledRepresentations'

    @staticmethod
    def __call__(self):
        representations = express_getattr(self, 'Representations', INDETERMINATE)
        assert (sizeof([temp for temp in representations if not 'ifc4x3_rc4.ifcstyledrepresentation' in typeof(temp)]) == 0) is not False

class IfcMaterialLayer_NormalizedPriority:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMaterialLayer'
    RULE_NAME = 'NormalizedPriority'

    @staticmethod
    def __call__(self):
        priority = express_getattr(self, 'Priority', INDETERMINATE)
        assert (not exists(priority) or 0 <= priority <= 100) is not False

def calc_IfcMaterialLayerSet_TotalThickness(self):
    return IfcMlsTotalThickness(self)

class IfcMaterialProfile_NormalizedPriority:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMaterialProfile'
    RULE_NAME = 'NormalizedPriority'

    @staticmethod
    def __call__(self):
        priority = express_getattr(self, 'Priority', INDETERMINATE)
        assert (not exists(priority) or 0 <= priority <= 100) is not False

class IfcMechanicalFastener_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMechanicalFastener'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcMechanicalFastenerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcMechanicalFastenerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcMechanicalFastener_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMechanicalFastener'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcmechanicalfastenertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcMechanicalFastenerType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMechanicalFastenerType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcMechanicalFastenerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcMechanicalFastenerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcMedicalDevice_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMedicalDevice'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcMedicalDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcMedicalDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcMedicalDevice_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMedicalDevice'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcmedicaldevicetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcMedicalDeviceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMedicalDeviceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcMedicalDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcMedicalDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcMember_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMember'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcMemberTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcMemberTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcMember_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMember'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcmembertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcMemberStandardCase_HasMaterialProfileSetUsage:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMemberStandardCase'
    RULE_NAME = 'HasMaterialProfileSetUsage'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in usedin(self, 'ifc4x3_rc4.ifcrelassociates.relatedobjects') if 'ifc4x3_rc4.ifcrelassociatesmaterial' in typeof(temp) and 'ifc4x3_rc4.ifcmaterialprofilesetusage' in typeof(express_getattr(temp, 'RelatingMaterial', INDETERMINATE))]) == 1) is not False

class IfcMemberType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMemberType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcMemberTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcMemberTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

def calc_IfcMirroredProfileDef_Operator(self):
    return IfcCartesianTransformationOperator2D(Axis1=IfcDirection(DirectionRatios=[-1.0, 0.0]), Axis2=IfcDirection(DirectionRatios=[0.0, 1.0]), LocalOrigin=IfcCartesianPoint(Coordinates=[0.0, 0.0]), Scale=1.0)

class IfcMobileTelecommunicationsAppliance_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMobileTelecommunicationsAppliance'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcMobileTelecommunicationsApplianceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcMobileTelecommunicationsApplianceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcMobileTelecommunicationsAppliance_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMobileTelecommunicationsAppliance'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcmobiletelecommunicationsappliancetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcMobileTelecommunicationsApplianceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMobileTelecommunicationsApplianceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcMobileTelecommunicationsApplianceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcMobileTelecommunicationsApplianceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcMooringDevice_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMooringDevice'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcMooringDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcMooringDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcMooringDevice_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMooringDevice'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcmooringdevicetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcMooringDeviceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMooringDeviceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcMooringDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcMooringDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcMotorConnection_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMotorConnection'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcMotorConnectionTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcMotorConnectionTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcMotorConnection_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMotorConnection'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcmotorconnectiontype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcMotorConnectionType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMotorConnectionType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcMotorConnectionTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcMotorConnectionTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcNamedUnit_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcNamedUnit'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert IfcCorrectDimensions(express_getattr(self, 'UnitType', INDETERMINATE), express_getattr(self, 'Dimensions', INDETERMINATE)) is not False

class IfcNavigationElement_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcNavigationElement'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcNavigationElementTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcNavigationElementTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcNavigationElement_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcNavigationElement'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcnavigationelementtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcNavigationElementType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcNavigationElementType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcNavigationElementTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcNavigationElementTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcObject_UniquePropertySetNames:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcObject'
    RULE_NAME = 'UniquePropertySetNames'

    @staticmethod
    def __call__(self):
        isdefinedby = express_getattr(self, 'IsDefinedBy', INDETERMINATE)
        assert (sizeof(isdefinedby) == 0 or IfcUniqueDefinitionNames(isdefinedby)) is not False

class IfcObjective_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcObjective'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        objectivequalifier = express_getattr(self, 'ObjectiveQualifier', INDETERMINATE)
        assert (objectivequalifier != express_getattr(IfcObjectiveEnum, 'USERDEFINED', INDETERMINATE) or (objectivequalifier == express_getattr(IfcObjectiveEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'UserDefinedQualifier', INDETERMINATE)))) is not False

class IfcOccupant_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcOccupant'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not predefinedtype == express_getattr(IfcOccupantTypeEnum, 'USERDEFINED', INDETERMINATE) or exists(express_getattr(self, 'ObjectType', INDETERMINATE))) is not False

class IfcOffsetCurve2D_DimIs2D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcOffsetCurve2D'
    RULE_NAME = 'DimIs2D'

    @staticmethod
    def __call__(self):
        basiscurve = express_getattr(self, 'BasisCurve', INDETERMINATE)
        assert (express_getattr(basiscurve, 'Dim', INDETERMINATE) == 2) is not False

class IfcOffsetCurve3D_DimIs2D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcOffsetCurve3D'
    RULE_NAME = 'DimIs2D'

    @staticmethod
    def __call__(self):
        basiscurve = express_getattr(self, 'BasisCurve', INDETERMINATE)
        assert (express_getattr(basiscurve, 'Dim', INDETERMINATE) == 3) is not False

class IfcOpenCrossProfileDef_CorrectProfileType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcOpenCrossProfileDef'
    RULE_NAME = 'CorrectProfileType'

    @staticmethod
    def __call__(self):
        assert (express_getattr(self, 'ProfileType', INDETERMINATE) == express_getattr(IfcProfileTypeEnum, 'CURVE', INDETERMINATE)) is not False

class IfcOpenCrossProfileDef_CorrespondingSlopeWidths:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcOpenCrossProfileDef'
    RULE_NAME = 'CorrespondingSlopeWidths'

    @staticmethod
    def __call__(self):
        widths = express_getattr(self, 'Widths', INDETERMINATE)
        slopes = express_getattr(self, 'Slopes', INDETERMINATE)
        assert (sizeof(slopes) == sizeof(widths)) is not False

class IfcOpenCrossProfileDef_CorrespondingTags:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcOpenCrossProfileDef'
    RULE_NAME = 'CorrespondingTags'

    @staticmethod
    def __call__(self):
        slopes = express_getattr(self, 'Slopes', INDETERMINATE)
        tags = express_getattr(self, 'Tags', INDETERMINATE)
        assert (not exists(tags) or sizeof(tags) == sizeof(slopes) + 1) is not False

class IfcOpeningElement_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcOpeningElement'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcOpeningElementTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcOpeningElementTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcOrientedEdge_EdgeElementNotOriented:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcOrientedEdge'
    RULE_NAME = 'EdgeElementNotOriented'

    @staticmethod
    def __call__(self):
        edgeelement = express_getattr(self, 'EdgeElement', INDETERMINATE)
        assert (not 'ifc4x3_rc4.ifcorientededge' in typeof(edgeelement)) is not False

def calc_IfcOrientedEdge_EdgeStart(self):
    edgeelement = express_getattr(self, 'EdgeElement', INDETERMINATE)
    orientation = express_getattr(self, 'Orientation', INDETERMINATE)
    return IfcBooleanChoose(orientation, express_getattr(edgeelement, 'EdgeStart', INDETERMINATE), express_getattr(edgeelement, 'EdgeEnd', INDETERMINATE))

def calc_IfcOrientedEdge_EdgeEnd(self):
    edgeelement = express_getattr(self, 'EdgeElement', INDETERMINATE)
    orientation = express_getattr(self, 'Orientation', INDETERMINATE)
    return IfcBooleanChoose(orientation, express_getattr(edgeelement, 'EdgeEnd', INDETERMINATE), express_getattr(edgeelement, 'EdgeStart', INDETERMINATE))

class IfcOutlet_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcOutlet'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcOutletTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcOutletTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcOutlet_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcOutlet'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcoutlettype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcOutletType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcOutletType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcOutletTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcOutletTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcOwnerHistory_CorrectChangeAction:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcOwnerHistory'
    RULE_NAME = 'CorrectChangeAction'

    @staticmethod
    def __call__(self):
        changeaction = express_getattr(self, 'ChangeAction', INDETERMINATE)
        lastmodifieddate = express_getattr(self, 'LastModifiedDate', INDETERMINATE)
        assert (exists(lastmodifieddate) or (not exists(lastmodifieddate) and (not exists(changeaction))) or (not exists(lastmodifieddate) and exists(changeaction) and (changeaction == express_getattr(IfcChangeActionEnum, 'NOTDEFINED', INDETERMINATE) or changeaction == express_getattr(IfcChangeActionEnum, 'NOCHANGE', INDETERMINATE)))) is not False

class IfcPath_IsContinuous:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPath'
    RULE_NAME = 'IsContinuous'

    @staticmethod
    def __call__(self):
        assert IfcPathHeadToTail(self) is not False

class IfcPavement_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPavement'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcPavementTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcPavementTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcPavement_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPavement'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcpavementtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcPavementType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPavementType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcPavementTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcPavementTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcPcurve_DimIs2D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPcurve'
    RULE_NAME = 'DimIs2D'

    @staticmethod
    def __call__(self):
        referencecurve = express_getattr(self, 'ReferenceCurve', INDETERMINATE)
        assert (express_getattr(referencecurve, 'Dim', INDETERMINATE) == 2) is not False

class IfcPerson_IdentifiablePerson:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPerson'
    RULE_NAME = 'IdentifiablePerson'

    @staticmethod
    def __call__(self):
        identification = express_getattr(self, 'Identification', INDETERMINATE)
        familyname = express_getattr(self, 'FamilyName', INDETERMINATE)
        givenname = express_getattr(self, 'GivenName', INDETERMINATE)
        assert (exists(identification) or exists(familyname) or exists(givenname)) is not False

class IfcPerson_ValidSetOfNames:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPerson'
    RULE_NAME = 'ValidSetOfNames'

    @staticmethod
    def __call__(self):
        familyname = express_getattr(self, 'FamilyName', INDETERMINATE)
        givenname = express_getattr(self, 'GivenName', INDETERMINATE)
        middlenames = express_getattr(self, 'MiddleNames', INDETERMINATE)
        assert (not exists(middlenames) or exists(familyname) or exists(givenname)) is not False

class IfcPhysicalComplexQuantity_NoSelfReference:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPhysicalComplexQuantity'
    RULE_NAME = 'NoSelfReference'

    @staticmethod
    def __call__(self):
        hasquantities = express_getattr(self, 'HasQuantities', INDETERMINATE)
        assert (sizeof([temp for temp in hasquantities if self == temp]) == 0) is not False

class IfcPhysicalComplexQuantity_UniqueQuantityNames:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPhysicalComplexQuantity'
    RULE_NAME = 'UniqueQuantityNames'

    @staticmethod
    def __call__(self):
        hasquantities = express_getattr(self, 'HasQuantities', INDETERMINATE)
        assert IfcUniqueQuantityNames(hasquantities) is not False

class IfcPile_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPile'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcPileTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcPileTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcPile_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPile'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcpiletype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcPileType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPileType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcPileTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcPileTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcPipeFitting_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPipeFitting'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcPipeFittingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcPipeFittingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcPipeFitting_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPipeFitting'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcpipefittingtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcPipeFittingType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPipeFittingType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcPipeFittingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcPipeFittingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcPipeSegment_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPipeSegment'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcPipeSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcPipeSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcPipeSegment_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPipeSegment'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcpipesegmenttype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcPipeSegmentType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPipeSegmentType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcPipeSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcPipeSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcPixelTexture_MinPixelInS:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPixelTexture'
    RULE_NAME = 'MinPixelInS'

    @staticmethod
    def __call__(self):
        width = express_getattr(self, 'Width', INDETERMINATE)
        assert (width >= 1) is not False

class IfcPixelTexture_MinPixelInT:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPixelTexture'
    RULE_NAME = 'MinPixelInT'

    @staticmethod
    def __call__(self):
        height = express_getattr(self, 'Height', INDETERMINATE)
        assert (height >= 1) is not False

class IfcPixelTexture_NumberOfColours:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPixelTexture'
    RULE_NAME = 'NumberOfColours'

    @staticmethod
    def __call__(self):
        colourcomponents = express_getattr(self, 'ColourComponents', INDETERMINATE)
        assert (1 <= colourcomponents <= 4) is not False

class IfcPixelTexture_SizeOfPixelList:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPixelTexture'
    RULE_NAME = 'SizeOfPixelList'

    @staticmethod
    def __call__(self):
        width = express_getattr(self, 'Width', INDETERMINATE)
        height = express_getattr(self, 'Height', INDETERMINATE)
        pixel = express_getattr(self, 'Pixel', INDETERMINATE)
        assert (sizeof(pixel) == width * height) is not False

class IfcPixelTexture_PixelAsByteAndSameLength:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPixelTexture'
    RULE_NAME = 'PixelAsByteAndSameLength'

    @staticmethod
    def __call__(self):
        pixel = express_getattr(self, 'Pixel', INDETERMINATE)
        assert (sizeof([temp for temp in pixel if blength(temp) % 8 == 0 and blength(temp) == blength(express_getitem(pixel, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))]) == sizeof(pixel)) is not False

def calc_IfcPlacement_Dim(self):
    location = express_getattr(self, 'Location', INDETERMINATE)
    return express_getattr(location, 'Dim', INDETERMINATE)

class IfcPlate_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPlate'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcPlateTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcPlateTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcPlate_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPlate'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcplatetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcPlateStandardCase_HasMaterialLayerSetUsage:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPlateStandardCase'
    RULE_NAME = 'HasMaterialLayerSetUsage'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in usedin(self, 'ifc4x3_rc4.ifcrelassociates.relatedobjects') if 'ifc4x3_rc4.ifcrelassociatesmaterial' in typeof(temp) and 'ifc4x3_rc4.ifcmateriallayersetusage' in typeof(express_getattr(temp, 'RelatingMaterial', INDETERMINATE))]) == 1) is not False

class IfcPlateType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPlateType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcPlateTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcPlateTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

def calc_IfcPointByDistanceExpression_Dim(self):
    basiscurve = express_getattr(self, 'BasisCurve', INDETERMINATE)
    return express_getattr(basiscurve, 'Dim', INDETERMINATE)

def calc_IfcPointOnCurve_Dim(self):
    basiscurve = express_getattr(self, 'BasisCurve', INDETERMINATE)
    return express_getattr(basiscurve, 'Dim', INDETERMINATE)

def calc_IfcPointOnSurface_Dim(self):
    basissurface = express_getattr(self, 'BasisSurface', INDETERMINATE)
    return express_getattr(basissurface, 'Dim', INDETERMINATE)

class IfcPolyLoop_AllPointsSameDim:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPolyLoop'
    RULE_NAME = 'AllPointsSameDim'

    @staticmethod
    def __call__(self):
        polygon = express_getattr(self, 'Polygon', INDETERMINATE)
        assert (sizeof([temp for temp in polygon if express_getattr(temp, 'Dim', INDETERMINATE) != express_getattr(express_getitem(polygon, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)]) == 0) is not False

class IfcPolygonalBoundedHalfSpace_BoundaryDim:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPolygonalBoundedHalfSpace'
    RULE_NAME = 'BoundaryDim'

    @staticmethod
    def __call__(self):
        polygonalboundary = express_getattr(self, 'PolygonalBoundary', INDETERMINATE)
        assert (express_getattr(polygonalboundary, 'Dim', INDETERMINATE) == 2) is not False

class IfcPolygonalBoundedHalfSpace_BoundaryType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPolygonalBoundedHalfSpace'
    RULE_NAME = 'BoundaryType'

    @staticmethod
    def __call__(self):
        polygonalboundary = express_getattr(self, 'PolygonalBoundary', INDETERMINATE)
        assert (sizeof(typeof(polygonalboundary) * ['ifc4x3_rc4.ifcpolyline', 'ifc4x3_rc4.ifccompositecurve']) == 1) is not False

class IfcPolyline_SameDim:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPolyline'
    RULE_NAME = 'SameDim'

    @staticmethod
    def __call__(self):
        points = express_getattr(self, 'Points', INDETERMINATE)
        assert (sizeof([temp for temp in points if express_getattr(temp, 'Dim', INDETERMINATE) != express_getattr(express_getitem(points, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)]) == 0) is not False

class IfcPolynomialCurve_ValidCoefficients:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPolynomialCurve'
    RULE_NAME = 'ValidCoefficients'

    @staticmethod
    def __call__(self):
        coefficientsx = express_getattr(self, 'CoefficientsX', INDETERMINATE)
        coefficientsy = express_getattr(self, 'CoefficientsY', INDETERMINATE)
        coefficientsz = express_getattr(self, 'CoefficientsZ', INDETERMINATE)
        assert (exists(coefficientsx) and exists(coefficientsy) or (exists(coefficientsx) and exists(coefficientsz)) or (exists(coefficientsy) and exists(coefficientsz)) or (exists(coefficientsx) and exists(coefficientsy) and exists(coefficientsz))) is not False

class IfcPolynomialCurve_CorrectPositionDim:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPolynomialCurve'
    RULE_NAME = 'CorrectPositionDim'

    @staticmethod
    def __call__(self):
        position = express_getattr(self, 'Position', INDETERMINATE)
        coefficientsz = express_getattr(self, 'CoefficientsZ', INDETERMINATE)
        assert (express_getattr(position, 'Dim', INDETERMINATE) == 2 and (not exists(coefficientsz)) or express_getattr(position, 'Dim', INDETERMINATE) == 3) is not False

class IfcPositioningElement_HasPlacement:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPositioningElement'
    RULE_NAME = 'HasPlacement'

    @staticmethod
    def __call__(self):
        assert exists(express_getattr(self, 'ObjectPlacement', INDETERMINATE)) is not False

class IfcPostalAddress_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPostalAddress'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        internallocation = express_getattr(self, 'InternalLocation', INDETERMINATE)
        addresslines = express_getattr(self, 'AddressLines', INDETERMINATE)
        postalbox = express_getattr(self, 'PostalBox', INDETERMINATE)
        town = express_getattr(self, 'Town', INDETERMINATE)
        region = express_getattr(self, 'Region', INDETERMINATE)
        postalcode = express_getattr(self, 'PostalCode', INDETERMINATE)
        country = express_getattr(self, 'Country', INDETERMINATE)
        assert (exists(internallocation) or exists(addresslines) or exists(postalbox) or exists(postalcode) or exists(town) or exists(region) or exists(country)) is not False

class IfcPresentationLayerAssignment_ApplicableItems:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPresentationLayerAssignment'
    RULE_NAME = 'ApplicableItems'

    @staticmethod
    def __call__(self):
        assigneditems = express_getattr(self, 'AssignedItems', INDETERMINATE)
        assert (sizeof([temp for temp in assigneditems if sizeof(typeof(temp) * ['ifc4x3_rc4.ifcshaperepresentation', 'ifc4x3_rc4.ifcgeometricrepresentationitem', 'ifc4x3_rc4.ifcmappeditem']) == 1]) == sizeof(assigneditems)) is not False

class IfcPresentationLayerWithStyle_ApplicableOnlyToItems:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPresentationLayerWithStyle'
    RULE_NAME = 'ApplicableOnlyToItems'

    @staticmethod
    def __call__(self):
        assigneditems = express_getattr(self, 'AssignedItems', INDETERMINATE)
        assert (sizeof([temp for temp in assigneditems if sizeof(typeof(temp) * ['ifc4x3_rc4.ifcgeometricrepresentationitem', 'ifc4x3_rc4.ifcmappeditem']) >= 1]) == sizeof(assigneditems)) is not False

class IfcProcedure_HasName:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProcedure'
    RULE_NAME = 'HasName'

    @staticmethod
    def __call__(self):
        assert exists(express_getattr(self, 'Name', INDETERMINATE)) is not False

class IfcProcedure_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProcedure'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcProcedureTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcProcedureTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcProcedureType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProcedureType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcProcedureTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcProcedureTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ProcessType', INDETERMINATE)))) is not False

class IfcProduct_PlacementForShapeRepresentation:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProduct'
    RULE_NAME = 'PlacementForShapeRepresentation'

    @staticmethod
    def __call__(self):
        objectplacement = express_getattr(self, 'ObjectPlacement', INDETERMINATE)
        representation = express_getattr(self, 'Representation', INDETERMINATE)
        assert (exists(representation) and exists(objectplacement) or (exists(representation) and sizeof([temp for temp in express_getattr(representation, 'Representations', INDETERMINATE) if 'ifc4x3_rc4.ifcshaperepresentation' in typeof(temp)]) == 0) or (not exists(representation))) is not False

class IfcProductDefinitionShape_OnlyShapeModel:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProductDefinitionShape'
    RULE_NAME = 'OnlyShapeModel'

    @staticmethod
    def __call__(self):
        representations = express_getattr(self, 'Representations', INDETERMINATE)
        assert (sizeof([temp for temp in representations if not 'ifc4x3_rc4.ifcshapemodel' in typeof(temp)]) == 0) is not False

class IfcProject_HasName:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProject'
    RULE_NAME = 'HasName'

    @staticmethod
    def __call__(self):
        assert exists(express_getattr(self, 'Name', INDETERMINATE)) is not False

class IfcProject_CorrectContext:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProject'
    RULE_NAME = 'CorrectContext'

    @staticmethod
    def __call__(self):
        assert (not exists(express_getattr(self, 'RepresentationContexts', INDETERMINATE)) or sizeof([temp for temp in express_getattr(self, 'RepresentationContexts', INDETERMINATE) if 'ifc4x3_rc4.ifcgeometricrepresentationsubcontext' in typeof(temp)]) == 0) is not False

class IfcProject_NoDecomposition:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProject'
    RULE_NAME = 'NoDecomposition'

    @staticmethod
    def __call__(self):
        assert (sizeof(express_getattr(self, 'Decomposes', INDETERMINATE)) == 0) is not False

class IfcProjectedCRS_IsLengthUnit:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProjectedCRS'
    RULE_NAME = 'IsLengthUnit'

    @staticmethod
    def __call__(self):
        mapunit = express_getattr(self, 'MapUnit', INDETERMINATE)
        assert (not exists(mapunit) or express_getattr(mapunit, 'UnitType', INDETERMINATE) == express_getattr(IfcUnitEnum, 'LENGTHUNIT', INDETERMINATE)) is not False

class IfcProjectionElement_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProjectionElement'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcProjectionElementTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcProjectionElementTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcPropertyBoundedValue_SameUnitUpperLower:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyBoundedValue'
    RULE_NAME = 'SameUnitUpperLower'

    @staticmethod
    def __call__(self):
        upperboundvalue = express_getattr(self, 'UpperBoundValue', INDETERMINATE)
        lowerboundvalue = express_getattr(self, 'LowerBoundValue', INDETERMINATE)
        assert (not exists(upperboundvalue) or not exists(lowerboundvalue) or typeof(upperboundvalue) == typeof(lowerboundvalue)) is not False

class IfcPropertyBoundedValue_SameUnitUpperSet:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyBoundedValue'
    RULE_NAME = 'SameUnitUpperSet'

    @staticmethod
    def __call__(self):
        upperboundvalue = express_getattr(self, 'UpperBoundValue', INDETERMINATE)
        setpointvalue = express_getattr(self, 'SetPointValue', INDETERMINATE)
        assert (not exists(upperboundvalue) or not exists(setpointvalue) or typeof(upperboundvalue) == typeof(setpointvalue)) is not False

class IfcPropertyBoundedValue_SameUnitLowerSet:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyBoundedValue'
    RULE_NAME = 'SameUnitLowerSet'

    @staticmethod
    def __call__(self):
        lowerboundvalue = express_getattr(self, 'LowerBoundValue', INDETERMINATE)
        setpointvalue = express_getattr(self, 'SetPointValue', INDETERMINATE)
        assert (not exists(lowerboundvalue) or not exists(setpointvalue) or typeof(lowerboundvalue) == typeof(setpointvalue)) is not False

class IfcPropertyDependencyRelationship_NoSelfReference:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyDependencyRelationship'
    RULE_NAME = 'NoSelfReference'

    @staticmethod
    def __call__(self):
        dependingproperty = express_getattr(self, 'DependingProperty', INDETERMINATE)
        dependantproperty = express_getattr(self, 'DependantProperty', INDETERMINATE)
        assert (dependingproperty != dependantproperty) is not False

class IfcPropertyEnumeratedValue_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyEnumeratedValue'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        enumerationvalues = express_getattr(self, 'EnumerationValues', INDETERMINATE)
        enumerationreference = express_getattr(self, 'EnumerationReference', INDETERMINATE)
        assert (not exists(enumerationreference) or not exists(enumerationvalues) or sizeof([temp for temp in enumerationvalues if temp in express_getattr(enumerationreference, 'EnumerationValues', INDETERMINATE)]) == sizeof(enumerationvalues)) is not False

class IfcPropertyEnumeration_WR01:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyEnumeration'
    RULE_NAME = 'WR01'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in express_getattr(self, 'EnumerationValues', INDETERMINATE) if not typeof(express_getitem(express_getattr(self, 'EnumerationValues', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) == typeof(temp)]) == 0) is not False

class IfcPropertyListValue_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyListValue'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in express_getattr(self, 'ListValues', INDETERMINATE) if not typeof(express_getitem(express_getattr(self, 'ListValues', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) == typeof(temp)]) == 0) is not False

class IfcPropertySet_ExistsName:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertySet'
    RULE_NAME = 'ExistsName'

    @staticmethod
    def __call__(self):
        assert exists(express_getattr(self, 'Name', INDETERMINATE)) is not False

class IfcPropertySet_UniquePropertyNames:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertySet'
    RULE_NAME = 'UniquePropertyNames'

    @staticmethod
    def __call__(self):
        hasproperties = express_getattr(self, 'HasProperties', INDETERMINATE)
        assert IfcUniquePropertyName(hasproperties) is not False

class IfcPropertySetTemplate_ExistsName:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertySetTemplate'
    RULE_NAME = 'ExistsName'

    @staticmethod
    def __call__(self):
        assert exists(express_getattr(self, 'Name', INDETERMINATE)) is not False

class IfcPropertySetTemplate_UniquePropertyNames:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertySetTemplate'
    RULE_NAME = 'UniquePropertyNames'

    @staticmethod
    def __call__(self):
        haspropertytemplates = express_getattr(self, 'HasPropertyTemplates', INDETERMINATE)
        assert IfcUniquePropertyTemplateNames(haspropertytemplates) is not False

class IfcPropertyTableValue_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyTableValue'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        definingvalues = express_getattr(self, 'DefiningValues', INDETERMINATE)
        definedvalues = express_getattr(self, 'DefinedValues', INDETERMINATE)
        assert (not exists(definingvalues) and (not exists(definedvalues)) or sizeof(definingvalues) == sizeof(definedvalues)) is not False

class IfcPropertyTableValue_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyTableValue'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        definingvalues = express_getattr(self, 'DefiningValues', INDETERMINATE)
        assert (not exists(definingvalues) or sizeof([temp for temp in express_getattr(self, 'DefiningValues', INDETERMINATE) if typeof(temp) != typeof(express_getitem(express_getattr(self, 'DefiningValues', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))]) == 0) is not False

class IfcPropertyTableValue_WR23:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyTableValue'
    RULE_NAME = 'WR23'

    @staticmethod
    def __call__(self):
        definedvalues = express_getattr(self, 'DefinedValues', INDETERMINATE)
        assert (not exists(definedvalues) or sizeof([temp for temp in express_getattr(self, 'DefinedValues', INDETERMINATE) if typeof(temp) != typeof(express_getitem(express_getattr(self, 'DefinedValues', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))]) == 0) is not False

class IfcProtectiveDevice_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProtectiveDevice'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcProtectiveDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcProtectiveDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcProtectiveDevice_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProtectiveDevice'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcprotectivedevicetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcProtectiveDeviceTrippingUnit_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProtectiveDeviceTrippingUnit'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcProtectiveDeviceTrippingUnitTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcProtectiveDeviceTrippingUnitTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcProtectiveDeviceTrippingUnit_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProtectiveDeviceTrippingUnit'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcprotectivedevicetrippingunittype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcProtectiveDeviceTrippingUnitType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProtectiveDeviceTrippingUnitType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcProtectiveDeviceTrippingUnitTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcProtectiveDeviceTrippingUnitTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcProtectiveDeviceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProtectiveDeviceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcProtectiveDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcProtectiveDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcProxy_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProxy'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert exists(express_getattr(self, 'Name', INDETERMINATE)) is not False

class IfcPump_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPump'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcPumpTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcPumpTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcPump_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPump'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcpumptype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcPumpType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPumpType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcPumpTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcPumpTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcQuantityArea_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcQuantityArea'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        assert (not exists(express_getattr(self, 'Unit', INDETERMINATE)) or express_getattr(express_getattr(self, 'Unit', INDETERMINATE), 'UnitType', INDETERMINATE) == express_getattr(IfcUnitEnum, 'AREAUNIT', INDETERMINATE)) is not False

class IfcQuantityArea_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcQuantityArea'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        areavalue = express_getattr(self, 'AreaValue', INDETERMINATE)
        assert (areavalue >= 0.0) is not False

class IfcQuantityCount_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcQuantityCount'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        countvalue = express_getattr(self, 'CountValue', INDETERMINATE)
        assert (countvalue >= 0.0) is not False

class IfcQuantityLength_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcQuantityLength'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        assert (not exists(express_getattr(self, 'Unit', INDETERMINATE)) or express_getattr(express_getattr(self, 'Unit', INDETERMINATE), 'UnitType', INDETERMINATE) == express_getattr(IfcUnitEnum, 'LENGTHUNIT', INDETERMINATE)) is not False

class IfcQuantityLength_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcQuantityLength'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        lengthvalue = express_getattr(self, 'LengthValue', INDETERMINATE)
        assert (lengthvalue >= 0.0) is not False

class IfcQuantityTime_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcQuantityTime'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        assert (not exists(express_getattr(self, 'Unit', INDETERMINATE)) or express_getattr(express_getattr(self, 'Unit', INDETERMINATE), 'UnitType', INDETERMINATE) == express_getattr(IfcUnitEnum, 'TIMEUNIT', INDETERMINATE)) is not False

class IfcQuantityTime_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcQuantityTime'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        timevalue = express_getattr(self, 'TimeValue', INDETERMINATE)
        assert (timevalue >= 0.0) is not False

class IfcQuantityVolume_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcQuantityVolume'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        assert (not exists(express_getattr(self, 'Unit', INDETERMINATE)) or express_getattr(express_getattr(self, 'Unit', INDETERMINATE), 'UnitType', INDETERMINATE) == express_getattr(IfcUnitEnum, 'VOLUMEUNIT', INDETERMINATE)) is not False

class IfcQuantityVolume_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcQuantityVolume'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        volumevalue = express_getattr(self, 'VolumeValue', INDETERMINATE)
        assert (volumevalue >= 0.0) is not False

class IfcQuantityWeight_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcQuantityWeight'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        assert (not exists(express_getattr(self, 'Unit', INDETERMINATE)) or express_getattr(express_getattr(self, 'Unit', INDETERMINATE), 'UnitType', INDETERMINATE) == express_getattr(IfcUnitEnum, 'MASSUNIT', INDETERMINATE)) is not False

class IfcQuantityWeight_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcQuantityWeight'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        weightvalue = express_getattr(self, 'WeightValue', INDETERMINATE)
        assert (weightvalue >= 0.0) is not False

class IfcRail_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRail'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcRailTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcRailTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcRail_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRail'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcrailtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcRailType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRailType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcRailTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcRailTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcRailing_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRailing'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcRailingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcRailingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcRailing_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRailing'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcrailingtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcRailingType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRailingType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcRailingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcRailingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcRailway_HasObjectType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRailway'
    RULE_NAME = 'HasObjectType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcRailwayTypeEnum, 'USERDEFINED', INDETERMINATE) or exists(express_getattr(self, 'ObjectType', INDETERMINATE))) is not False

class IfcRamp_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRamp'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcRampTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcRampTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcRamp_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRamp'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcramptype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcRampFlight_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRampFlight'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcRampFlightTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcRampFlightTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcRampFlight_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRampFlight'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcrampflighttype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcRampFlightType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRampFlightType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcRampFlightTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcRampFlightTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcRampType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRampType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcRampTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcRampTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcRationalBSplineCurveWithKnots_SameNumOfWeightsAndPoints:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRationalBSplineCurveWithKnots'
    RULE_NAME = 'SameNumOfWeightsAndPoints'

    @staticmethod
    def __call__(self):
        weightsdata = express_getattr(self, 'WeightsData', INDETERMINATE)
        assert (sizeof(weightsdata) == sizeof(express_getattr(self, 'ControlPointsList', INDETERMINATE))) is not False

class IfcRationalBSplineCurveWithKnots_WeightsGreaterZero:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRationalBSplineCurveWithKnots'
    RULE_NAME = 'WeightsGreaterZero'

    @staticmethod
    def __call__(self):
        assert IfcCurveWeightsPositive(self) is not False

def calc_IfcRationalBSplineCurveWithKnots_Weights(self):
    weightsdata = express_getattr(self, 'WeightsData', INDETERMINATE)
    return IfcListToArray(weightsdata, 0, express_getattr(self, 'UpperIndexOnControlPoints', INDETERMINATE))

class IfcRationalBSplineSurfaceWithKnots_CorrespondingWeightsDataLists:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRationalBSplineSurfaceWithKnots'
    RULE_NAME = 'CorrespondingWeightsDataLists'

    @staticmethod
    def __call__(self):
        weightsdata = express_getattr(self, 'WeightsData', INDETERMINATE)
        assert (sizeof(weightsdata) == sizeof(express_getattr(self, 'ControlPointsList', INDETERMINATE)) and sizeof(express_getitem(weightsdata, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) == sizeof(express_getitem(express_getattr(self, 'ControlPointsList', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))) is not False

class IfcRationalBSplineSurfaceWithKnots_WeightValuesGreaterZero:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRationalBSplineSurfaceWithKnots'
    RULE_NAME = 'WeightValuesGreaterZero'

    @staticmethod
    def __call__(self):
        assert IfcSurfaceWeightsPositive(self) is not False

def calc_IfcRationalBSplineSurfaceWithKnots_Weights(self):
    uupper = express_getattr(self, 'UUpper', INDETERMINATE)
    vupper = express_getattr(self, 'VUpper', INDETERMINATE)
    weightsdata = express_getattr(self, 'WeightsData', INDETERMINATE)
    return IfcMakeArrayOfArray(weightsdata, 0, uupper, 0, vupper)

class IfcRectangleHollowProfileDef_ValidWallThickness:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRectangleHollowProfileDef'
    RULE_NAME = 'ValidWallThickness'

    @staticmethod
    def __call__(self):
        wallthickness = express_getattr(self, 'WallThickness', INDETERMINATE)
        assert (wallthickness < express_getattr(self, 'XDim', INDETERMINATE) / 2.0 and wallthickness < express_getattr(self, 'YDim', INDETERMINATE) / 2.0) is not False

class IfcRectangleHollowProfileDef_ValidInnerRadius:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRectangleHollowProfileDef'
    RULE_NAME = 'ValidInnerRadius'

    @staticmethod
    def __call__(self):
        wallthickness = express_getattr(self, 'WallThickness', INDETERMINATE)
        innerfilletradius = express_getattr(self, 'InnerFilletRadius', INDETERMINATE)
        assert (not exists(innerfilletradius) or (innerfilletradius <= express_getattr(self, 'XDim', INDETERMINATE) / 2.0 - wallthickness and innerfilletradius <= express_getattr(self, 'YDim', INDETERMINATE) / 2.0 - wallthickness)) is not False

class IfcRectangleHollowProfileDef_ValidOuterRadius:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRectangleHollowProfileDef'
    RULE_NAME = 'ValidOuterRadius'

    @staticmethod
    def __call__(self):
        outerfilletradius = express_getattr(self, 'OuterFilletRadius', INDETERMINATE)
        assert (not exists(outerfilletradius) or (outerfilletradius <= express_getattr(self, 'XDim', INDETERMINATE) / 2.0 and outerfilletradius <= express_getattr(self, 'YDim', INDETERMINATE) / 2.0)) is not False

class IfcRectangularTrimmedSurface_U1AndU2Different:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRectangularTrimmedSurface'
    RULE_NAME = 'U1AndU2Different'

    @staticmethod
    def __call__(self):
        u1 = express_getattr(self, 'U1', INDETERMINATE)
        u2 = express_getattr(self, 'U2', INDETERMINATE)
        assert (u1 != u2) is not False

class IfcRectangularTrimmedSurface_V1AndV2Different:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRectangularTrimmedSurface'
    RULE_NAME = 'V1AndV2Different'

    @staticmethod
    def __call__(self):
        v1 = express_getattr(self, 'V1', INDETERMINATE)
        v2 = express_getattr(self, 'V2', INDETERMINATE)
        assert (v1 != v2) is not False

class IfcRectangularTrimmedSurface_UsenseCompatible:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRectangularTrimmedSurface'
    RULE_NAME = 'UsenseCompatible'

    @staticmethod
    def __call__(self):
        basissurface = express_getattr(self, 'BasisSurface', INDETERMINATE)
        u1 = express_getattr(self, 'U1', INDETERMINATE)
        u2 = express_getattr(self, 'U2', INDETERMINATE)
        usense = express_getattr(self, 'Usense', INDETERMINATE)
        assert ('ifc4x3_rc4.ifcelementarysurface' in typeof(basissurface) and (not 'ifc4x3_rc4.ifcplane' in typeof(basissurface)) or 'ifc4x3_rc4.ifcsurfaceofrevolution' in typeof(basissurface) or usense == (u2 > u1)) is not False

class IfcRectangularTrimmedSurface_VsenseCompatible:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRectangularTrimmedSurface'
    RULE_NAME = 'VsenseCompatible'

    @staticmethod
    def __call__(self):
        v1 = express_getattr(self, 'V1', INDETERMINATE)
        v2 = express_getattr(self, 'V2', INDETERMINATE)
        vsense = express_getattr(self, 'Vsense', INDETERMINATE)
        assert (vsense == (v2 > v1)) is not False

class IfcReinforcedSoil_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcReinforcedSoil'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcReinforcedSoilTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcReinforcedSoilTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcReinforcingBar_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcReinforcingBar'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcReinforcingBarTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcReinforcingBarTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcReinforcingBar_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcReinforcingBar'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcreinforcingbartype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcReinforcingBarType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcReinforcingBarType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcReinforcingBarTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcReinforcingBarTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcReinforcingBarType_BendingShapeCodeProvided:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcReinforcingBarType'
    RULE_NAME = 'BendingShapeCodeProvided'

    @staticmethod
    def __call__(self):
        bendingshapecode = express_getattr(self, 'BendingShapeCode', INDETERMINATE)
        bendingparameters = express_getattr(self, 'BendingParameters', INDETERMINATE)
        assert (not exists(bendingparameters) or exists(bendingshapecode)) is not False

class IfcReinforcingMesh_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcReinforcingMesh'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcReinforcingMeshTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcReinforcingMeshTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcReinforcingMesh_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcReinforcingMesh'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcreinforcingmeshtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcReinforcingMeshType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcReinforcingMeshType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcReinforcingMeshTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcReinforcingMeshTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcReinforcingMeshType_BendingShapeCodeProvided:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcReinforcingMeshType'
    RULE_NAME = 'BendingShapeCodeProvided'

    @staticmethod
    def __call__(self):
        bendingshapecode = express_getattr(self, 'BendingShapeCode', INDETERMINATE)
        bendingparameters = express_getattr(self, 'BendingParameters', INDETERMINATE)
        assert (not exists(bendingparameters) or exists(bendingshapecode)) is not False

class IfcRelAggregates_NoSelfReference:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAggregates'
    RULE_NAME = 'NoSelfReference'

    @staticmethod
    def __call__(self):
        relatingobject = express_getattr(self, 'RelatingObject', INDETERMINATE)
        relatedobjects = express_getattr(self, 'RelatedObjects', INDETERMINATE)
        assert (sizeof([temp for temp in relatedobjects if relatingobject == temp]) == 0) is not False

class IfcRelAssigns_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssigns'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        relatedobjects = express_getattr(self, 'RelatedObjects', INDETERMINATE)
        relatedobjectstype = express_getattr(self, 'RelatedObjectsType', INDETERMINATE)
        assert IfcCorrectObjectAssignment(relatedobjectstype, relatedobjects) is not False

class IfcRelAssignsToActor_NoSelfReference:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssignsToActor'
    RULE_NAME = 'NoSelfReference'

    @staticmethod
    def __call__(self):
        relatingactor = express_getattr(self, 'RelatingActor', INDETERMINATE)
        assert (sizeof([temp for temp in express_getattr(self, 'RelatedObjects', INDETERMINATE) if relatingactor == temp]) == 0) is not False

class IfcRelAssignsToControl_NoSelfReference:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssignsToControl'
    RULE_NAME = 'NoSelfReference'

    @staticmethod
    def __call__(self):
        relatingcontrol = express_getattr(self, 'RelatingControl', INDETERMINATE)
        assert (sizeof([temp for temp in express_getattr(self, 'RelatedObjects', INDETERMINATE) if relatingcontrol == temp]) == 0) is not False

class IfcRelAssignsToGroup_NoSelfReference:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssignsToGroup'
    RULE_NAME = 'NoSelfReference'

    @staticmethod
    def __call__(self):
        relatinggroup = express_getattr(self, 'RelatingGroup', INDETERMINATE)
        assert (sizeof([temp for temp in express_getattr(self, 'RelatedObjects', INDETERMINATE) if relatinggroup == temp]) == 0) is not False

class IfcRelAssignsToProcess_NoSelfReference:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssignsToProcess'
    RULE_NAME = 'NoSelfReference'

    @staticmethod
    def __call__(self):
        relatingprocess = express_getattr(self, 'RelatingProcess', INDETERMINATE)
        assert (sizeof([temp for temp in express_getattr(self, 'RelatedObjects', INDETERMINATE) if relatingprocess == temp]) == 0) is not False

class IfcRelAssignsToProduct_NoSelfReference:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssignsToProduct'
    RULE_NAME = 'NoSelfReference'

    @staticmethod
    def __call__(self):
        relatingproduct = express_getattr(self, 'RelatingProduct', INDETERMINATE)
        assert (sizeof([temp for temp in express_getattr(self, 'RelatedObjects', INDETERMINATE) if relatingproduct == temp]) == 0) is not False

class IfcRelAssignsToResource_NoSelfReference:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssignsToResource'
    RULE_NAME = 'NoSelfReference'

    @staticmethod
    def __call__(self):
        relatingresource = express_getattr(self, 'RelatingResource', INDETERMINATE)
        assert (sizeof([temp for temp in express_getattr(self, 'RelatedObjects', INDETERMINATE) if relatingresource == temp]) == 0) is not False

class IfcRelAssociatesMaterial_NoVoidElement:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssociatesMaterial'
    RULE_NAME = 'NoVoidElement'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in express_getattr(self, 'RelatedObjects', INDETERMINATE) if 'ifc4x3_rc4.ifcfeatureelementsubtraction' in typeof(temp) or 'ifc4x3_rc4.ifcvirtualelement' in typeof(temp)]) == 0) is not False

class IfcRelAssociatesMaterial_AllowedElements:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssociatesMaterial'
    RULE_NAME = 'AllowedElements'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in express_getattr(self, 'RelatedObjects', INDETERMINATE) if sizeof(typeof(temp) * ['ifc4x3_rc4.ifcelement', 'ifc4x3_rc4.ifcelementtype', 'ifc4x3_rc4.ifcwindowstyle', 'ifc4x3_rc4.ifcdoorstyle', 'ifc4x3_rc4.ifcstructuralmember', 'ifc4x3_rc4.ifcport']) == 0]) == 0) is not False

class IfcRelConnectsElements_NoSelfReference:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelConnectsElements'
    RULE_NAME = 'NoSelfReference'

    @staticmethod
    def __call__(self):
        relatingelement = express_getattr(self, 'RelatingElement', INDETERMINATE)
        relatedelement = express_getattr(self, 'RelatedElement', INDETERMINATE)
        assert (relatingelement != relatedelement) is not False

class IfcRelConnectsPathElements_NormalizedRelatingPriorities:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelConnectsPathElements'
    RULE_NAME = 'NormalizedRelatingPriorities'

    @staticmethod
    def __call__(self):
        relatingpriorities = express_getattr(self, 'RelatingPriorities', INDETERMINATE)
        assert (sizeof(relatingpriorities) == 0 or sizeof([temp for temp in relatingpriorities if 0 <= temp <= 100]) == sizeof(relatingpriorities)) is not False

class IfcRelConnectsPathElements_NormalizedRelatedPriorities:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelConnectsPathElements'
    RULE_NAME = 'NormalizedRelatedPriorities'

    @staticmethod
    def __call__(self):
        relatedpriorities = express_getattr(self, 'RelatedPriorities', INDETERMINATE)
        assert (sizeof(relatedpriorities) == 0 or sizeof([temp for temp in relatedpriorities if 0 <= temp <= 100]) == sizeof(relatedpriorities)) is not False

class IfcRelConnectsPorts_NoSelfReference:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelConnectsPorts'
    RULE_NAME = 'NoSelfReference'

    @staticmethod
    def __call__(self):
        relatingport = express_getattr(self, 'RelatingPort', INDETERMINATE)
        relatedport = express_getattr(self, 'RelatedPort', INDETERMINATE)
        assert (relatingport != relatedport) is not False

class IfcRelContainedInSpatialStructure_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelContainedInSpatialStructure'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        relatedelements = express_getattr(self, 'RelatedElements', INDETERMINATE)
        assert (sizeof([temp for temp in relatedelements if 'ifc4x3_rc4.ifcspatialstructureelement' in typeof(temp)]) == 0) is not False

class IfcRelDeclares_NoSelfReference:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelDeclares'
    RULE_NAME = 'NoSelfReference'

    @staticmethod
    def __call__(self):
        relatingcontext = express_getattr(self, 'RelatingContext', INDETERMINATE)
        relateddefinitions = express_getattr(self, 'RelatedDefinitions', INDETERMINATE)
        assert (sizeof([temp for temp in relateddefinitions if relatingcontext == temp]) == 0) is not False

class IfcRelDefinesByProperties_NoRelatedTypeObject:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelDefinesByProperties'
    RULE_NAME = 'NoRelatedTypeObject'

    @staticmethod
    def __call__(self):
        assert (sizeof([types for types in express_getattr(self, 'RelatedObjects', INDETERMINATE) if 'ifc4x3_rc4.ifctypeobject' in typeof(types)]) == 0) is not False

class IfcRelInterferesElements_NoSelfReference:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelInterferesElements'
    RULE_NAME = 'NoSelfReference'

    @staticmethod
    def __call__(self):
        relatingelement = express_getattr(self, 'RelatingElement', INDETERMINATE)
        relatedelement = express_getattr(self, 'RelatedElement', INDETERMINATE)
        assert (relatingelement != relatedelement) is not False

class IfcRelNests_NoSelfReference:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelNests'
    RULE_NAME = 'NoSelfReference'

    @staticmethod
    def __call__(self):
        relatingobject = express_getattr(self, 'RelatingObject', INDETERMINATE)
        relatedobjects = express_getattr(self, 'RelatedObjects', INDETERMINATE)
        assert (sizeof([temp for temp in relatedobjects if relatingobject == temp]) == 0) is not False

class IfcRelPositions_NoSelfReference:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelPositions'
    RULE_NAME = 'NoSelfReference'

    @staticmethod
    def __call__(self):
        relatingpositioningelement = express_getattr(self, 'RelatingPositioningElement', INDETERMINATE)
        relatedproducts = express_getattr(self, 'RelatedProducts', INDETERMINATE)
        assert (sizeof([temp for temp in relatedproducts if relatingpositioningelement == temp]) == 0) is not False

class IfcRelReferencedInSpatialStructure_AllowedRelatedElements:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelReferencedInSpatialStructure'
    RULE_NAME = 'AllowedRelatedElements'

    @staticmethod
    def __call__(self):
        relatedelements = express_getattr(self, 'RelatedElements', INDETERMINATE)
        assert (sizeof([temp for temp in relatedelements if 'ifc4x3_rc4.ifcspatialstructureelement' in typeof(temp) and (not 'ifc4x3_rc4.ifcspace' in typeof(temp))]) == 0) is not False

class IfcRelSequence_AvoidInconsistentSequence:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelSequence'
    RULE_NAME = 'AvoidInconsistentSequence'

    @staticmethod
    def __call__(self):
        relatingprocess = express_getattr(self, 'RelatingProcess', INDETERMINATE)
        relatedprocess = express_getattr(self, 'RelatedProcess', INDETERMINATE)
        assert (relatingprocess != relatedprocess) is not False

class IfcRelSequence_CorrectSequenceType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelSequence'
    RULE_NAME = 'CorrectSequenceType'

    @staticmethod
    def __call__(self):
        sequencetype = express_getattr(self, 'SequenceType', INDETERMINATE)
        userdefinedsequencetype = express_getattr(self, 'UserDefinedSequenceType', INDETERMINATE)
        assert (sequencetype != express_getattr(IfcSequenceEnum, 'USERDEFINED', INDETERMINATE) or (sequencetype == express_getattr(IfcSequenceEnum, 'USERDEFINED', INDETERMINATE) and exists(userdefinedsequencetype))) is not False

class IfcRelSpaceBoundary_CorrectPhysOrVirt:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelSpaceBoundary'
    RULE_NAME = 'CorrectPhysOrVirt'

    @staticmethod
    def __call__(self):
        relatedbuildingelement = express_getattr(self, 'RelatedBuildingElement', INDETERMINATE)
        physicalorvirtualboundary = express_getattr(self, 'PhysicalOrVirtualBoundary', INDETERMINATE)
        assert (physicalorvirtualboundary == express_getattr(IfcPhysicalOrVirtualEnum, 'Physical', INDETERMINATE) and (not 'ifc4x3_rc4.ifcvirtualelement' in typeof(relatedbuildingelement)) or (physicalorvirtualboundary == express_getattr(IfcPhysicalOrVirtualEnum, 'Virtual', INDETERMINATE) and ('ifc4x3_rc4.ifcvirtualelement' in typeof(relatedbuildingelement) or 'ifc4x3_rc4.ifcopeningelement' in typeof(relatedbuildingelement))) or physicalorvirtualboundary == express_getattr(IfcPhysicalOrVirtualEnum, 'NotDefined', INDETERMINATE)) is not False

class IfcReparametrisedCompositeCurveSegment_PositiveLengthParameter:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcReparametrisedCompositeCurveSegment'
    RULE_NAME = 'PositiveLengthParameter'

    @staticmethod
    def __call__(self):
        paramlength = express_getattr(self, 'ParamLength', INDETERMINATE)
        assert (paramlength > 0.0) is not False

class IfcRepresentationMap_ApplicableMappedRepr:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRepresentationMap'
    RULE_NAME = 'ApplicableMappedRepr'

    @staticmethod
    def __call__(self):
        mappedrepresentation = express_getattr(self, 'MappedRepresentation', INDETERMINATE)
        assert ('ifc4x3_rc4.ifcshapemodel' in typeof(mappedrepresentation)) is not False

class IfcRevolvedAreaSolid_AxisStartInXY:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRevolvedAreaSolid'
    RULE_NAME = 'AxisStartInXY'

    @staticmethod
    def __call__(self):
        axis = express_getattr(self, 'Axis', INDETERMINATE)
        assert (express_getitem(express_getattr(express_getattr(axis, 'Location', INDETERMINATE), 'Coordinates', INDETERMINATE), 3 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) == 0.0) is not False

class IfcRevolvedAreaSolid_AxisDirectionInXY:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRevolvedAreaSolid'
    RULE_NAME = 'AxisDirectionInXY'

    @staticmethod
    def __call__(self):
        axis = express_getattr(self, 'Axis', INDETERMINATE)
        assert (express_getitem(express_getattr(express_getattr(axis, 'Z', INDETERMINATE), 'DirectionRatios', INDETERMINATE), 3 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) == 0.0) is not False

def calc_IfcRevolvedAreaSolid_AxisLine(self):
    axis = express_getattr(self, 'Axis', INDETERMINATE)
    return IfcLine(Pnt=express_getattr(axis, 'Location', INDETERMINATE), Dir=IfcVector(Orientation=express_getattr(axis, 'Z', INDETERMINATE), Magnitude=1.0))

class IfcRevolvedAreaSolidTapered_CorrectProfileAssignment:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRevolvedAreaSolidTapered'
    RULE_NAME = 'CorrectProfileAssignment'

    @staticmethod
    def __call__(self):
        assert IfcTaperedSweptAreaProfiles(express_getattr(self, 'SweptArea', INDETERMINATE), express_getattr(self, 'EndSweptArea', INDETERMINATE)) is not False

class IfcRoad_HasObjectType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRoad'
    RULE_NAME = 'HasObjectType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcRoadTypeEnum, 'USERDEFINED', INDETERMINATE) or exists(express_getattr(self, 'ObjectType', INDETERMINATE))) is not False

class IfcRoof_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRoof'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcRoofTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcRoofTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcRoof_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRoof'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcrooftype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcRoofType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRoofType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcRoofTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcRoofTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcRoundedRectangleProfileDef_ValidRadius:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRoundedRectangleProfileDef'
    RULE_NAME = 'ValidRadius'

    @staticmethod
    def __call__(self):
        roundingradius = express_getattr(self, 'RoundingRadius', INDETERMINATE)
        assert (roundingradius <= express_getattr(self, 'XDim', INDETERMINATE) / 2.0 and roundingradius <= express_getattr(self, 'YDim', INDETERMINATE) / 2.0) is not False

def calc_IfcSIUnit_Dimensions(self):
    return IfcDimensionsForSiUnit(express_getattr(self, 'Name', INDETERMINATE))

class IfcSanitaryTerminal_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSanitaryTerminal'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcSanitaryTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcSanitaryTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcSanitaryTerminal_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSanitaryTerminal'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcsanitaryterminaltype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcSanitaryTerminalType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSanitaryTerminalType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcSanitaryTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcSanitaryTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcSeamCurve_TwoPCurves:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSeamCurve'
    RULE_NAME = 'TwoPCurves'

    @staticmethod
    def __call__(self):
        assert (sizeof(express_getattr(self, 'AssociatedGeometry', INDETERMINATE)) == 2) is not False

class IfcSeamCurve_SameSurface:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSeamCurve'
    RULE_NAME = 'SameSurface'

    @staticmethod
    def __call__(self):
        assert (IfcAssociatedSurface(express_getitem(express_getattr(self, 'AssociatedGeometry', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) == IfcAssociatedSurface(express_getitem(express_getattr(self, 'AssociatedGeometry', INDETERMINATE), 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))) is not False

class IfcSectionedSolid_DirectrixIs3D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSectionedSolid'
    RULE_NAME = 'DirectrixIs3D'

    @staticmethod
    def __call__(self):
        directrix = express_getattr(self, 'Directrix', INDETERMINATE)
        assert (express_getattr(directrix, 'Dim', INDETERMINATE) == 3) is not False

class IfcSectionedSolid_ConsistentProfileTypes:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSectionedSolid'
    RULE_NAME = 'ConsistentProfileTypes'

    @staticmethod
    def __call__(self):
        crosssections = express_getattr(self, 'CrossSections', INDETERMINATE)
        assert (sizeof([temp for temp in crosssections if express_getattr(express_getitem(crosssections, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'ProfileType', INDETERMINATE) != express_getattr(temp, 'ProfileType', INDETERMINATE)]) == 0) is not False

class IfcSectionedSolid_SectionsSameType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSectionedSolid'
    RULE_NAME = 'SectionsSameType'

    @staticmethod
    def __call__(self):
        crosssections = express_getattr(self, 'CrossSections', INDETERMINATE)
        assert (sizeof([temp for temp in crosssections if typeof(express_getitem(crosssections, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) != typeof(temp)]) == 0) is not False

class IfcSectionedSolidHorizontal_CorrespondingSectionPositions:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSectionedSolidHorizontal'
    RULE_NAME = 'CorrespondingSectionPositions'

    @staticmethod
    def __call__(self):
        crosssections = express_getattr(self, 'CrossSections', INDETERMINATE)
        crosssectionpositions = express_getattr(self, 'CrossSectionPositions', INDETERMINATE)
        assert (sizeof(crosssections) == sizeof(crosssectionpositions)) is not False

class IfcSectionedSolidHorizontal_NoLongitudinalOffsets:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSectionedSolidHorizontal'
    RULE_NAME = 'NoLongitudinalOffsets'

    @staticmethod
    def __call__(self):
        crosssectionpositions = express_getattr(self, 'CrossSectionPositions', INDETERMINATE)
        assert (sizeof([temp for temp in crosssectionpositions if exists(express_getattr(express_getattr(temp, 'Location', INDETERMINATE), 'OffsetLongitudinal', INDETERMINATE))]) == 0) is not False

class IfcSectionedSpine_CorrespondingSectionPositions:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSectionedSpine'
    RULE_NAME = 'CorrespondingSectionPositions'

    @staticmethod
    def __call__(self):
        crosssections = express_getattr(self, 'CrossSections', INDETERMINATE)
        crosssectionpositions = express_getattr(self, 'CrossSectionPositions', INDETERMINATE)
        assert (sizeof(crosssections) == sizeof(crosssectionpositions)) is not False

class IfcSectionedSpine_ConsistentProfileTypes:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSectionedSpine'
    RULE_NAME = 'ConsistentProfileTypes'

    @staticmethod
    def __call__(self):
        crosssections = express_getattr(self, 'CrossSections', INDETERMINATE)
        assert (sizeof([temp for temp in crosssections if express_getattr(express_getitem(crosssections, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'ProfileType', INDETERMINATE) != express_getattr(temp, 'ProfileType', INDETERMINATE)]) == 0) is not False

class IfcSectionedSpine_SpineCurveDim:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSectionedSpine'
    RULE_NAME = 'SpineCurveDim'

    @staticmethod
    def __call__(self):
        spinecurve = express_getattr(self, 'SpineCurve', INDETERMINATE)
        assert (express_getattr(spinecurve, 'Dim', INDETERMINATE) == 3) is not False

def calc_IfcSectionedSpine_Dim(self):
    return 3

class IfcSensor_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSensor'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcSensorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcSensorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcSensor_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSensor'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcsensortype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcSensorType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSensorType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcSensorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcSensorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcShadingDevice_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcShadingDevice'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcShadingDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcShadingDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcShadingDevice_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcShadingDevice'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcshadingdevicetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcShadingDeviceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcShadingDeviceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcShadingDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcShadingDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcShapeModel_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcShapeModel'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        ofshapeaspect = express_getattr(self, 'OfShapeAspect', INDETERMINATE)
        assert (sizeof(express_getattr(self, 'OfProductRepresentation', INDETERMINATE)) == 1) ^ (sizeof(express_getattr(self, 'RepresentationMap', INDETERMINATE)) == 1) ^ (sizeof(ofshapeaspect) == 1) is not False

class IfcShapeRepresentation_CorrectContext:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcShapeRepresentation'
    RULE_NAME = 'CorrectContext'

    @staticmethod
    def __call__(self):
        assert ('ifc4x3_rc4.ifcgeometricrepresentationcontext' in typeof(express_getattr(self, 'ContextOfItems', INDETERMINATE))) is not False

class IfcShapeRepresentation_NoTopologicalItem:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcShapeRepresentation'
    RULE_NAME = 'NoTopologicalItem'

    @staticmethod
    def __call__(self):
        items = express_getattr(self, 'Items', INDETERMINATE)
        assert (sizeof([temp for temp in items if 'ifc4x3_rc4.ifctopologicalrepresentationitem' in typeof(temp) and (not sizeof(['ifc4x3_rc4.ifcvertexpoint', 'ifc4x3_rc4.ifcedgecurve', 'ifc4x3_rc4.ifcfacesurface'] * typeof(temp)) == 1)]) == 0) is not False

class IfcShapeRepresentation_HasRepresentationType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcShapeRepresentation'
    RULE_NAME = 'HasRepresentationType'

    @staticmethod
    def __call__(self):
        assert exists(express_getattr(self, 'RepresentationType', INDETERMINATE)) is not False

class IfcShapeRepresentation_HasRepresentationIdentifier:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcShapeRepresentation'
    RULE_NAME = 'HasRepresentationIdentifier'

    @staticmethod
    def __call__(self):
        assert exists(express_getattr(self, 'RepresentationIdentifier', INDETERMINATE)) is not False

class IfcShapeRepresentation_CorrectItemsForType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcShapeRepresentation'
    RULE_NAME = 'CorrectItemsForType'

    @staticmethod
    def __call__(self):
        assert IfcShapeRepresentationTypes(express_getattr(self, 'RepresentationType', INDETERMINATE), express_getattr(self, 'Items', INDETERMINATE)) is not False

def calc_IfcShellBasedSurfaceModel_Dim(self):
    return 3

class IfcSign_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSign'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcSignTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcSignTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcSign_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSign'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcsigntype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcSignType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSignType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcSignTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcSignTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcSignal_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSignal'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcSignalTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcSignalTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcSignal_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSignal'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcsignaltype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcSignalType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSignalType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcSignalTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcSignalTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcSlab_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSlab'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcSlabTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcSlabTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcSlab_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSlab'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcslabtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcSlabElementedCase_HasDecomposition:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSlabElementedCase'
    RULE_NAME = 'HasDecomposition'

    @staticmethod
    def __call__(self):
        assert (hiindex(express_getattr(self, 'IsDecomposedBy', INDETERMINATE)) > 0) is not False

class IfcSlabStandardCase_HasMaterialLayerSetusage:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSlabStandardCase'
    RULE_NAME = 'HasMaterialLayerSetusage'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in usedin(self, 'ifc4x3_rc4.ifcrelassociates.relatedobjects') if 'ifc4x3_rc4.ifcrelassociatesmaterial' in typeof(temp) and 'ifc4x3_rc4.ifcmateriallayersetusage' in typeof(express_getattr(temp, 'RelatingMaterial', INDETERMINATE))]) == 1) is not False

class IfcSlabType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSlabType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcSlabTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcSlabTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcSolarDevice_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSolarDevice'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcSolarDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcSolarDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcSolarDevice_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSolarDevice'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcsolardevicetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcSolarDeviceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSolarDeviceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcSolarDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcSolarDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

def calc_IfcSolidModel_Dim(self):
    return 3

class IfcSpace_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSpace'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcSpaceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcSpaceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcSpace_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSpace'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcspacetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcSpaceHeater_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSpaceHeater'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcSpaceHeaterTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcSpaceHeaterTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcSpaceHeater_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSpaceHeater'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcspaceheatertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcSpaceHeaterType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSpaceHeaterType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcSpaceHeaterTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcSpaceHeaterTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcSpaceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSpaceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcSpaceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcSpaceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcSpatialStructureElement_WR41:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSpatialStructureElement'
    RULE_NAME = 'WR41'

    @staticmethod
    def __call__(self):
        assert (hiindex(express_getattr(self, 'Decomposes', INDETERMINATE)) == 1 and 'ifc4x3_rc4.ifcrelaggregates' in typeof(express_getitem(express_getattr(self, 'Decomposes', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and ('ifc4x3_rc4.ifcproject' in typeof(express_getattr(express_getitem(express_getattr(self, 'Decomposes', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingObject', INDETERMINATE)) or 'ifc4x3_rc4.ifcspatialstructureelement' in typeof(express_getattr(express_getitem(express_getattr(self, 'Decomposes', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingObject', INDETERMINATE)))) is not False

class IfcSpatialZone_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSpatialZone'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcSpatialZoneTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcSpatialZoneTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcSpatialZone_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSpatialZone'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcspatialzonetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcSpatialZoneType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSpatialZoneType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcSpatialZoneTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcSpatialZoneTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcStackTerminal_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStackTerminal'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcStackTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcStackTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcStackTerminal_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStackTerminal'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcstackterminaltype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcStackTerminalType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStackTerminalType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcStackTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcStackTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcStair_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStair'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcStairTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcStairTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcStair_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStair'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcstairtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcStairFlight_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStairFlight'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcStairFlightTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcStairFlightTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcStairFlight_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStairFlight'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcstairflighttype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcStairFlightType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStairFlightType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcStairFlightTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcStairFlightTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcStairType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStairType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcStairTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcStairTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcStructuralAnalysisModel_HasObjectType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralAnalysisModel'
    RULE_NAME = 'HasObjectType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcAnalysisModelTypeEnum, 'USERDEFINED', INDETERMINATE) or exists(express_getattr(self, 'ObjectType', INDETERMINATE))) is not False

class IfcStructuralAnalysisModel_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralAnalysisModel'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcAnalysisModelTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcAnalysisModelTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcStructuralCurveAction_ProjectedIsGlobal:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralCurveAction'
    RULE_NAME = 'ProjectedIsGlobal'

    @staticmethod
    def __call__(self):
        projectedortrue = express_getattr(self, 'ProjectedOrTrue', INDETERMINATE)
        assert (not exists(projectedortrue) or (projectedortrue != projected_length or express_getattr(self, 'GlobalOrLocal', INDETERMINATE) == global_coords)) is not False

class IfcStructuralCurveAction_HasObjectType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralCurveAction'
    RULE_NAME = 'HasObjectType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcStructuralCurveActivityTypeEnum, 'USERDEFINED', INDETERMINATE) or exists(express_getattr(self, 'ObjectType', INDETERMINATE))) is not False

class IfcStructuralCurveAction_SuitablePredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralCurveAction'
    RULE_NAME = 'SuitablePredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcStructuralCurveActivityTypeEnum, 'EQUIDISTANT', INDETERMINATE)) is not False

class IfcStructuralCurveMember_HasObjectType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralCurveMember'
    RULE_NAME = 'HasObjectType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcStructuralCurveMemberTypeEnum, 'USERDEFINED', INDETERMINATE) or exists(express_getattr(self, 'ObjectType', INDETERMINATE))) is not False

class IfcStructuralCurveReaction_HasObjectType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralCurveReaction'
    RULE_NAME = 'HasObjectType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcStructuralCurveActivityTypeEnum, 'USERDEFINED', INDETERMINATE) or exists(express_getattr(self, 'ObjectType', INDETERMINATE))) is not False

class IfcStructuralCurveReaction_SuitablePredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralCurveReaction'
    RULE_NAME = 'SuitablePredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcStructuralCurveActivityTypeEnum, 'SINUS', INDETERMINATE) and predefinedtype != express_getattr(IfcStructuralCurveActivityTypeEnum, 'PARABOLA', INDETERMINATE)) is not False

class IfcStructuralLinearAction_SuitableLoadType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralLinearAction'
    RULE_NAME = 'SuitableLoadType'

    @staticmethod
    def __call__(self):
        assert (sizeof(['ifc4x3_rc4.ifcstructuralloadlinearforce', 'ifc4x3_rc4.ifcstructuralloadtemperature'] * typeof(express_getattr(self, 'AppliedLoad', INDETERMINATE))) == 1) is not False

class IfcStructuralLinearAction_ConstPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralLinearAction'
    RULE_NAME = 'ConstPredefinedType'

    @staticmethod
    def __call__(self):
        assert (express_getattr(self, 'PredefinedType', INDETERMINATE) == express_getattr(IfcStructuralCurveActivityTypeEnum, 'CONST', INDETERMINATE)) is not False

class IfcStructuralLoadCase_IsLoadCasePredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralLoadCase'
    RULE_NAME = 'IsLoadCasePredefinedType'

    @staticmethod
    def __call__(self):
        assert (express_getattr(self, 'PredefinedType', INDETERMINATE) == express_getattr(IfcLoadGroupTypeEnum, 'LOAD_CASE', INDETERMINATE)) is not False

class IfcStructuralLoadConfiguration_ValidListSize:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralLoadConfiguration'
    RULE_NAME = 'ValidListSize'

    @staticmethod
    def __call__(self):
        values = express_getattr(self, 'Values', INDETERMINATE)
        locations = express_getattr(self, 'Locations', INDETERMINATE)
        assert (not exists(locations) or sizeof(locations) == sizeof(values)) is not False

class IfcStructuralLoadGroup_HasObjectType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralLoadGroup'
    RULE_NAME = 'HasObjectType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        actiontype = express_getattr(self, 'ActionType', INDETERMINATE)
        actionsource = express_getattr(self, 'ActionSource', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcLoadGroupTypeEnum, 'USERDEFINED', INDETERMINATE) and actiontype != express_getattr(IfcActionTypeEnum, 'USERDEFINED', INDETERMINATE) and (actionsource != express_getattr(IfcActionSourceTypeEnum, 'USERDEFINED', INDETERMINATE)) or exists(express_getattr(self, 'ObjectType', INDETERMINATE))) is not False

class IfcStructuralPlanarAction_SuitableLoadType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralPlanarAction'
    RULE_NAME = 'SuitableLoadType'

    @staticmethod
    def __call__(self):
        assert (sizeof(['ifc4x3_rc4.ifcstructuralloadplanarforce', 'ifc4x3_rc4.ifcstructuralloadtemperature'] * typeof(express_getattr(self, 'AppliedLoad', INDETERMINATE))) == 1) is not False

class IfcStructuralPlanarAction_ConstPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralPlanarAction'
    RULE_NAME = 'ConstPredefinedType'

    @staticmethod
    def __call__(self):
        assert (express_getattr(self, 'PredefinedType', INDETERMINATE) == express_getattr(IfcStructuralSurfaceActivityTypeEnum, 'CONST', INDETERMINATE)) is not False

class IfcStructuralPointAction_SuitableLoadType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralPointAction'
    RULE_NAME = 'SuitableLoadType'

    @staticmethod
    def __call__(self):
        assert (sizeof(['ifc4x3_rc4.ifcstructuralloadsingleforce', 'ifc4x3_rc4.ifcstructuralloadsingledisplacement'] * typeof(express_getattr(self, 'AppliedLoad', INDETERMINATE))) == 1) is not False

class IfcStructuralPointReaction_SuitableLoadType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralPointReaction'
    RULE_NAME = 'SuitableLoadType'

    @staticmethod
    def __call__(self):
        assert (sizeof(['ifc4x3_rc4.ifcstructuralloadsingleforce', 'ifc4x3_rc4.ifcstructuralloadsingledisplacement'] * typeof(express_getattr(self, 'AppliedLoad', INDETERMINATE))) == 1) is not False

class IfcStructuralResultGroup_HasObjectType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralResultGroup'
    RULE_NAME = 'HasObjectType'

    @staticmethod
    def __call__(self):
        theorytype = express_getattr(self, 'TheoryType', INDETERMINATE)
        assert (theorytype != express_getattr(IfcAnalysisTheoryTypeEnum, 'USERDEFINED', INDETERMINATE) or exists(express_getattr(self, 'ObjectType', INDETERMINATE))) is not False

class IfcStructuralSurfaceAction_ProjectedIsGlobal:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralSurfaceAction'
    RULE_NAME = 'ProjectedIsGlobal'

    @staticmethod
    def __call__(self):
        projectedortrue = express_getattr(self, 'ProjectedOrTrue', INDETERMINATE)
        assert (not exists(projectedortrue) or (projectedortrue != projected_length or express_getattr(self, 'GlobalOrLocal', INDETERMINATE) == global_coords)) is not False

class IfcStructuralSurfaceAction_HasObjectType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralSurfaceAction'
    RULE_NAME = 'HasObjectType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcStructuralSurfaceActivityTypeEnum, 'USERDEFINED', INDETERMINATE) or exists(express_getattr(self, 'ObjectType', INDETERMINATE))) is not False

class IfcStructuralSurfaceMember_HasObjectType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralSurfaceMember'
    RULE_NAME = 'HasObjectType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcStructuralSurfaceMemberTypeEnum, 'USERDEFINED', INDETERMINATE) or exists(express_getattr(self, 'ObjectType', INDETERMINATE))) is not False

class IfcStructuralSurfaceReaction_HasPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralSurfaceReaction'
    RULE_NAME = 'HasPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcStructuralSurfaceActivityTypeEnum, 'USERDEFINED', INDETERMINATE) or exists(express_getattr(self, 'ObjectType', INDETERMINATE))) is not False

class IfcStyledItem_ApplicableItem:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStyledItem'
    RULE_NAME = 'ApplicableItem'

    @staticmethod
    def __call__(self):
        item = express_getattr(self, 'Item', INDETERMINATE)
        assert (not 'ifc4x3_rc4.ifcstyleditem' in typeof(item)) is not False

class IfcStyledRepresentation_OnlyStyledItems:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStyledRepresentation'
    RULE_NAME = 'OnlyStyledItems'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in express_getattr(self, 'Items', INDETERMINATE) if not 'ifc4x3_rc4.ifcstyleditem' in typeof(temp)]) == 0) is not False

class IfcSubContractResource_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSubContractResource'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcSubContractResourceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcSubContractResourceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcSubContractResourceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSubContractResourceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcSubContractResourceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcSubContractResourceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ResourceType', INDETERMINATE)))) is not False

def calc_IfcSurface_Dim(self):
    return 3

class IfcSurfaceCurve_CurveIs3D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceCurve'
    RULE_NAME = 'CurveIs3D'

    @staticmethod
    def __call__(self):
        curve3d = express_getattr(self, 'Curve3D', INDETERMINATE)
        assert (express_getattr(curve3d, 'Dim', INDETERMINATE) == 3) is not False

class IfcSurfaceCurve_CurveIsNotPcurve:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceCurve'
    RULE_NAME = 'CurveIsNotPcurve'

    @staticmethod
    def __call__(self):
        curve3d = express_getattr(self, 'Curve3D', INDETERMINATE)
        assert (not 'ifc4x3_rc4.ifcpcurve' in typeof(curve3d)) is not False

def calc_IfcSurfaceCurve_BasisSurface(self):
    return IfcGetBasisSurface(self)

class IfcSurfaceFeature_HasObjectType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceFeature'
    RULE_NAME = 'HasObjectType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcSurfaceFeatureTypeEnum, 'USERDEFINED', INDETERMINATE) or exists(express_getattr(self, 'ObjectType', INDETERMINATE))) is not False

class IfcSurfaceOfLinearExtrusion_DepthGreaterZero:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceOfLinearExtrusion'
    RULE_NAME = 'DepthGreaterZero'

    @staticmethod
    def __call__(self):
        depth = express_getattr(self, 'Depth', INDETERMINATE)
        assert (depth > 0.0) is not False

def calc_IfcSurfaceOfLinearExtrusion_ExtrusionAxis(self):
    extrudeddirection = express_getattr(self, 'ExtrudedDirection', INDETERMINATE)
    depth = express_getattr(self, 'Depth', INDETERMINATE)
    return IfcVector(Orientation=extrudeddirection, Magnitude=depth)

def calc_IfcSurfaceOfRevolution_AxisLine(self):
    axisposition = express_getattr(self, 'AxisPosition', INDETERMINATE)
    return IfcLine(Pnt=express_getattr(axisposition, 'Location', INDETERMINATE), Dir=IfcVector(Orientation=express_getattr(axisposition, 'Z', INDETERMINATE), Magnitude=1.0))

class IfcSurfaceReinforcementArea_SurfaceAndOrShearAreaSpecified:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceReinforcementArea'
    RULE_NAME = 'SurfaceAndOrShearAreaSpecified'

    @staticmethod
    def __call__(self):
        surfacereinforcement1 = express_getattr(self, 'SurfaceReinforcement1', INDETERMINATE)
        surfacereinforcement2 = express_getattr(self, 'SurfaceReinforcement2', INDETERMINATE)
        shearreinforcement = express_getattr(self, 'ShearReinforcement', INDETERMINATE)
        assert (exists(surfacereinforcement1) or exists(surfacereinforcement2) or exists(shearreinforcement)) is not False

class IfcSurfaceReinforcementArea_NonnegativeArea1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceReinforcementArea'
    RULE_NAME = 'NonnegativeArea1'

    @staticmethod
    def __call__(self):
        surfacereinforcement1 = express_getattr(self, 'SurfaceReinforcement1', INDETERMINATE)
        assert (not exists(surfacereinforcement1) or (express_getitem(surfacereinforcement1, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) >= 0.0 and express_getitem(surfacereinforcement1, 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) >= 0.0 and (sizeof(surfacereinforcement1) == 1 or express_getitem(surfacereinforcement1, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) >= 0.0))) is not False

class IfcSurfaceReinforcementArea_NonnegativeArea2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceReinforcementArea'
    RULE_NAME = 'NonnegativeArea2'

    @staticmethod
    def __call__(self):
        surfacereinforcement2 = express_getattr(self, 'SurfaceReinforcement2', INDETERMINATE)
        assert (not exists(surfacereinforcement2) or (express_getitem(surfacereinforcement2, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) >= 0.0 and express_getitem(surfacereinforcement2, 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) >= 0.0 and (sizeof(surfacereinforcement2) == 1 or express_getitem(surfacereinforcement2, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) >= 0.0))) is not False

class IfcSurfaceReinforcementArea_NonnegativeArea3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceReinforcementArea'
    RULE_NAME = 'NonnegativeArea3'

    @staticmethod
    def __call__(self):
        shearreinforcement = express_getattr(self, 'ShearReinforcement', INDETERMINATE)
        assert (not exists(shearreinforcement) or shearreinforcement >= 0.0) is not False

class IfcSurfaceStyle_MaxOneShading:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceStyle'
    RULE_NAME = 'MaxOneShading'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in express_getattr(self, 'Styles', INDETERMINATE) if 'ifc4x3_rc4.ifcsurfacestyleshading' in typeof(style)]) <= 1) is not False

class IfcSurfaceStyle_MaxOneLighting:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceStyle'
    RULE_NAME = 'MaxOneLighting'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in express_getattr(self, 'Styles', INDETERMINATE) if 'ifc4x3_rc4.ifcsurfacestylelighting' in typeof(style)]) <= 1) is not False

class IfcSurfaceStyle_MaxOneRefraction:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceStyle'
    RULE_NAME = 'MaxOneRefraction'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in express_getattr(self, 'Styles', INDETERMINATE) if 'ifc4x3_rc4.ifcsurfacestylerefraction' in typeof(style)]) <= 1) is not False

class IfcSurfaceStyle_MaxOneTextures:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceStyle'
    RULE_NAME = 'MaxOneTextures'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in express_getattr(self, 'Styles', INDETERMINATE) if 'ifc4x3_rc4.ifcsurfacestylewithtextures' in typeof(style)]) <= 1) is not False

class IfcSurfaceStyle_MaxOneExtDefined:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceStyle'
    RULE_NAME = 'MaxOneExtDefined'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in express_getattr(self, 'Styles', INDETERMINATE) if 'ifc4x3_rc4.ifcexternallydefinedsurfacestyle' in typeof(style)]) <= 1) is not False

class IfcSweptAreaSolid_SweptAreaType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSweptAreaSolid'
    RULE_NAME = 'SweptAreaType'

    @staticmethod
    def __call__(self):
        sweptarea = express_getattr(self, 'SweptArea', INDETERMINATE)
        assert (express_getattr(sweptarea, 'ProfileType', INDETERMINATE) == express_getattr(IfcProfileTypeEnum, 'Area', INDETERMINATE)) is not False

class IfcSweptDiskSolid_DirectrixDim:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSweptDiskSolid'
    RULE_NAME = 'DirectrixDim'

    @staticmethod
    def __call__(self):
        directrix = express_getattr(self, 'Directrix', INDETERMINATE)
        assert (express_getattr(directrix, 'Dim', INDETERMINATE) == 3) is not False

class IfcSweptDiskSolid_InnerRadiusSize:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSweptDiskSolid'
    RULE_NAME = 'InnerRadiusSize'

    @staticmethod
    def __call__(self):
        radius = express_getattr(self, 'Radius', INDETERMINATE)
        innerradius = express_getattr(self, 'InnerRadius', INDETERMINATE)
        assert (not exists(innerradius) or radius > innerradius) is not False

class IfcSweptDiskSolid_DirectrixBounded:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSweptDiskSolid'
    RULE_NAME = 'DirectrixBounded'

    @staticmethod
    def __call__(self):
        directrix = express_getattr(self, 'Directrix', INDETERMINATE)
        startparam = express_getattr(self, 'StartParam', INDETERMINATE)
        endparam = express_getattr(self, 'EndParam', INDETERMINATE)
        assert (exists(startparam) and exists(endparam) or sizeof(['ifc4x3_rc4.ifcconic', 'ifc4x3_rc4.ifcboundedcurve'] * typeof(directrix)) == 1) is not False

class IfcSweptDiskSolidPolygonal_CorrectRadii:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSweptDiskSolidPolygonal'
    RULE_NAME = 'CorrectRadii'

    @staticmethod
    def __call__(self):
        filletradius = express_getattr(self, 'FilletRadius', INDETERMINATE)
        assert (not exists(filletradius) or filletradius >= express_getattr(self, 'Radius', INDETERMINATE)) is not False

class IfcSweptDiskSolidPolygonal_DirectrixIsPolyline:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSweptDiskSolidPolygonal'
    RULE_NAME = 'DirectrixIsPolyline'

    @staticmethod
    def __call__(self):
        assert ('ifc4x3_rc4.ifcpolyline' in typeof(express_getattr(self, 'Directrix', INDETERMINATE)) or ('ifc4x3_rc4.ifcindexedpolycurve' in typeof(express_getattr(self, 'Directrix', INDETERMINATE)) and (not exists(express_getattr(express_getattr(self, 'Directrix', INDETERMINATE), 'Segments', INDETERMINATE))))) is not False

class IfcSweptSurface_SweptCurveType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSweptSurface'
    RULE_NAME = 'SweptCurveType'

    @staticmethod
    def __call__(self):
        sweptcurve = express_getattr(self, 'SweptCurve', INDETERMINATE)
        assert (express_getattr(sweptcurve, 'ProfileType', INDETERMINATE) == express_getattr(IfcProfileTypeEnum, 'Curve', INDETERMINATE)) is not False

class IfcSwitchingDevice_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSwitchingDevice'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcSwitchingDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcSwitchingDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcSwitchingDevice_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSwitchingDevice'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcswitchingdevicetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcSwitchingDeviceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSwitchingDeviceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcSwitchingDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcSwitchingDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcSystemFurnitureElement_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSystemFurnitureElement'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcSystemFurnitureElementTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcSystemFurnitureElementTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcSystemFurnitureElement_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSystemFurnitureElement'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcsystemfurnitureelementtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcSystemFurnitureElementType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSystemFurnitureElementType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcSystemFurnitureElementTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcSystemFurnitureElementTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcTShapeProfileDef_ValidFlangeThickness:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTShapeProfileDef'
    RULE_NAME = 'ValidFlangeThickness'

    @staticmethod
    def __call__(self):
        depth = express_getattr(self, 'Depth', INDETERMINATE)
        flangethickness = express_getattr(self, 'FlangeThickness', INDETERMINATE)
        assert (flangethickness < depth) is not False

class IfcTShapeProfileDef_ValidWebThickness:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTShapeProfileDef'
    RULE_NAME = 'ValidWebThickness'

    @staticmethod
    def __call__(self):
        flangewidth = express_getattr(self, 'FlangeWidth', INDETERMINATE)
        webthickness = express_getattr(self, 'WebThickness', INDETERMINATE)
        assert (webthickness < flangewidth) is not False

class IfcTable_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTable'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        rows = express_getattr(self, 'Rows', INDETERMINATE)
        assert (sizeof([temp for temp in rows if hiindex(express_getattr(temp, 'RowCells', INDETERMINATE)) != hiindex(express_getattr(express_getitem(rows, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RowCells', INDETERMINATE))]) == 0) is not False

class IfcTable_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTable'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        numberofheadings = express_getattr(self, 'NumberOfHeadings', INDETERMINATE)
        assert (0 <= numberofheadings <= 1) is not False

def calc_IfcTable_NumberOfCellsInRow(self):
    rows = express_getattr(self, 'Rows', INDETERMINATE)
    return hiindex(express_getattr(express_getitem(rows, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RowCells', INDETERMINATE))

def calc_IfcTable_NumberOfHeadings(self):
    rows = express_getattr(self, 'Rows', INDETERMINATE)
    return sizeof([temp for temp in rows if express_getattr(temp, 'IsHeading', INDETERMINATE)])

def calc_IfcTable_NumberOfDataRows(self):
    rows = express_getattr(self, 'Rows', INDETERMINATE)
    return sizeof([temp for temp in rows if not express_getattr(temp, 'IsHeading', INDETERMINATE)])

class IfcTank_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTank'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcTankTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcTankTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcTank_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTank'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifctanktype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcTankType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTankType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcTankTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcTankTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcTask_HasName:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTask'
    RULE_NAME = 'HasName'

    @staticmethod
    def __call__(self):
        assert exists(express_getattr(self, 'Name', INDETERMINATE)) is not False

class IfcTask_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTask'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcTaskTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcTaskTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcTaskType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTaskType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcTaskTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcTaskTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ProcessType', INDETERMINATE)))) is not False

class IfcTelecomAddress_MinimumDataProvided:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTelecomAddress'
    RULE_NAME = 'MinimumDataProvided'

    @staticmethod
    def __call__(self):
        telephonenumbers = express_getattr(self, 'TelephoneNumbers', INDETERMINATE)
        facsimilenumbers = express_getattr(self, 'FacsimileNumbers', INDETERMINATE)
        pagernumber = express_getattr(self, 'PagerNumber', INDETERMINATE)
        electronicmailaddresses = express_getattr(self, 'ElectronicMailAddresses', INDETERMINATE)
        wwwhomepageurl = express_getattr(self, 'WWWHomePageURL', INDETERMINATE)
        messagingids = express_getattr(self, 'MessagingIDs', INDETERMINATE)
        assert (exists(telephonenumbers) or exists(facsimilenumbers) or exists(pagernumber) or exists(electronicmailaddresses) or exists(wwwhomepageurl) or exists(messagingids)) is not False

class IfcTendon_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTendon'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcTendonTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcTendonTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcTendon_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTendon'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifctendontype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcTendonAnchor_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTendonAnchor'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcTendonAnchorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcTendonAnchorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcTendonAnchor_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTendonAnchor'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifctendonanchortype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcTendonAnchorType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTendonAnchorType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcTendonAnchorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcTendonAnchorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcTendonConduit_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTendonConduit'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcTendonConduitTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcTendonConduitTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcTendonConduit_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTendonConduit'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifctendonconduittype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcTendonConduitType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTendonConduitType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcTendonConduitTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcTendonConduitTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcTendonType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTendonType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcTendonTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcTendonTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

def calc_IfcTessellatedFaceSet_Dim(self):
    return 3

class IfcTextLiteralWithExtent_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTextLiteralWithExtent'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        extent = express_getattr(self, 'Extent', INDETERMINATE)
        assert (not 'ifc4x3_rc4.ifcplanarbox' in typeof(extent)) is not False

class IfcTextStyleFontModel_MeasureOfFontSize:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTextStyleFontModel'
    RULE_NAME = 'MeasureOfFontSize'

    @staticmethod
    def __call__(self):
        assert ('ifc4x3_rc4.ifclengthmeasure' in typeof(express_getattr(self, 'FontSize', INDETERMINATE)) and express_getattr(self, 'FontSize', INDETERMINATE) > 0.0) is not False

class IfcTopologyRepresentation_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTopologyRepresentation'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in express_getattr(self, 'Items', INDETERMINATE) if not 'ifc4x3_rc4.ifctopologicalrepresentationitem' in typeof(temp)]) == 0) is not False

class IfcTopologyRepresentation_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTopologyRepresentation'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        assert exists(express_getattr(self, 'RepresentationType', INDETERMINATE)) is not False

class IfcTopologyRepresentation_WR23:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTopologyRepresentation'
    RULE_NAME = 'WR23'

    @staticmethod
    def __call__(self):
        assert IfcTopologyRepresentationTypes(express_getattr(self, 'RepresentationType', INDETERMINATE), express_getattr(self, 'Items', INDETERMINATE)) is not False

class IfcToroidalSurface_MajorLargerMinor:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcToroidalSurface'
    RULE_NAME = 'MajorLargerMinor'

    @staticmethod
    def __call__(self):
        majorradius = express_getattr(self, 'MajorRadius', INDETERMINATE)
        minorradius = express_getattr(self, 'MinorRadius', INDETERMINATE)
        assert (minorradius < majorradius) is not False

class IfcTrackElement_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTrackElement'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcTrackElementTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcTrackElementTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcTrackElement_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTrackElement'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifctrackelementtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcTrackElementType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTrackElementType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcTrackElementTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcTrackElementTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcTransformer_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTransformer'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcTransformerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcTransformerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcTransformer_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTransformer'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifctranformertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcTransformerType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTransformerType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcTransformerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcTransformerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcTransportElement_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTransportElement'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or (predefinedtype != express_getattr(IfcTransportElementFixedTypeEnum, 'USERDEFINED', INDETERMINATE) and predefinedtype != express_getattr(IfcTransportElementNonFixedTypeEnum, 'USERDEFINED', INDETERMINATE)) or ((predefinedtype == express_getattr(IfcTransportElementFixedTypeEnum, 'USERDEFINED', INDETERMINATE) or predefinedtype == express_getattr(IfcTransportElementNonFixedTypeEnum, 'USERDEFINED', INDETERMINATE)) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcTransportElement_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTransportElement'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifctransportelementtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcTransportElementType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTransportElementType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcTransportElementFixedTypeEnum, 'USERDEFINED', INDETERMINATE) and predefinedtype != express_getattr(IfcTransportElementNonFixedTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcTransportElementFixedTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcTransportElementNonFixedTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE))))) is not False

def calc_IfcTriangulatedFaceSet_NumberOfTriangles(self):
    coordindex = express_getattr(self, 'CoordIndex', INDETERMINATE)
    return sizeof(coordindex)

class IfcTriangulatedIrregularNetwork_NotClosed:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTriangulatedIrregularNetwork'
    RULE_NAME = 'NotClosed'

    @staticmethod
    def __call__(self):
        assert (express_getattr(self, 'Closed', INDETERMINATE) == False) is not False

class IfcTrimmedCurve_Trim1ValuesConsistent:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTrimmedCurve'
    RULE_NAME = 'Trim1ValuesConsistent'

    @staticmethod
    def __call__(self):
        trim1 = express_getattr(self, 'Trim1', INDETERMINATE)
        assert (hiindex(trim1) == 1 or typeof(express_getitem(trim1, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) != typeof(express_getitem(trim1, 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))) is not False

class IfcTrimmedCurve_Trim2ValuesConsistent:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTrimmedCurve'
    RULE_NAME = 'Trim2ValuesConsistent'

    @staticmethod
    def __call__(self):
        trim2 = express_getattr(self, 'Trim2', INDETERMINATE)
        assert (hiindex(trim2) == 1 or typeof(express_getitem(trim2, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) != typeof(express_getitem(trim2, 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))) is not False

class IfcTrimmedCurve_NoTrimOfBoundedCurves:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTrimmedCurve'
    RULE_NAME = 'NoTrimOfBoundedCurves'

    @staticmethod
    def __call__(self):
        basiscurve = express_getattr(self, 'BasisCurve', INDETERMINATE)
        assert (not 'ifc4x3_rc4.ifcboundedcurve' in typeof(basiscurve)) is not False

class IfcTubeBundle_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTubeBundle'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcTubeBundleTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcTubeBundleTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcTubeBundle_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTubeBundle'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifctubebundletype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcTubeBundleType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTubeBundleType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcTubeBundleTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcTubeBundleTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcTypeObject_NameRequired:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTypeObject'
    RULE_NAME = 'NameRequired'

    @staticmethod
    def __call__(self):
        assert exists(express_getattr(self, 'Name', INDETERMINATE)) is not False

class IfcTypeObject_UniquePropertySetNames:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTypeObject'
    RULE_NAME = 'UniquePropertySetNames'

    @staticmethod
    def __call__(self):
        haspropertysets = express_getattr(self, 'HasPropertySets', INDETERMINATE)
        assert (not exists(haspropertysets) or IfcUniquePropertySetNames(haspropertysets)) is not False

class IfcTypeProduct_ApplicableOccurrence:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTypeProduct'
    RULE_NAME = 'ApplicableOccurrence'

    @staticmethod
    def __call__(self):
        assert (not exists(lambda : express_getitem(express_getattr(self, 'Types', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) or sizeof([temp for temp in express_getattr(express_getitem(express_getattr(self, 'Types', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatedObjects', INDETERMINATE) if not 'ifc4x3_rc4.ifcproduct' in typeof(temp)]) == 0) is not False

class IfcUShapeProfileDef_ValidFlangeThickness:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcUShapeProfileDef'
    RULE_NAME = 'ValidFlangeThickness'

    @staticmethod
    def __call__(self):
        depth = express_getattr(self, 'Depth', INDETERMINATE)
        flangethickness = express_getattr(self, 'FlangeThickness', INDETERMINATE)
        assert (flangethickness < depth / 2.0) is not False

class IfcUShapeProfileDef_ValidWebThickness:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcUShapeProfileDef'
    RULE_NAME = 'ValidWebThickness'

    @staticmethod
    def __call__(self):
        flangewidth = express_getattr(self, 'FlangeWidth', INDETERMINATE)
        webthickness = express_getattr(self, 'WebThickness', INDETERMINATE)
        assert (webthickness < flangewidth) is not False

class IfcUnitAssignment_WR01:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcUnitAssignment'
    RULE_NAME = 'WR01'

    @staticmethod
    def __call__(self):
        units = express_getattr(self, 'Units', INDETERMINATE)
        assert IfcCorrectUnitAssignment(units) is not False

class IfcUnitaryControlElement_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcUnitaryControlElement'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcUnitaryControlElementTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcUnitaryControlElementTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcUnitaryControlElement_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcUnitaryControlElement'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcunitarycontrolelementtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcUnitaryControlElementType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcUnitaryControlElementType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcUnitaryControlElementTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcUnitaryControlElementTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcUnitaryEquipment_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcUnitaryEquipment'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcUnitaryEquipmentTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcUnitaryEquipmentTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcUnitaryEquipment_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcUnitaryEquipment'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcunitaryequipmenttype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcUnitaryEquipmentType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcUnitaryEquipmentType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcUnitaryEquipmentTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcUnitaryEquipmentTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcValve_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcValve'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcValveTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcValveTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcValve_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcValve'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcvalvetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcValveType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcValveType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcValveTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcValveTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcVector_MagGreaterOrEqualZero:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcVector'
    RULE_NAME = 'MagGreaterOrEqualZero'

    @staticmethod
    def __call__(self):
        magnitude = express_getattr(self, 'Magnitude', INDETERMINATE)
        assert (magnitude >= 0.0) is not False

def calc_IfcVector_Dim(self):
    orientation = express_getattr(self, 'Orientation', INDETERMINATE)
    return express_getattr(orientation, 'Dim', INDETERMINATE)

class IfcVibrationDamper_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcVibrationDamper'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcVibrationDamperTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcVibrationDamperTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcVibrationDamper_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcVibrationDamper'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcvibrationdampertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcVibrationDamperType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcVibrationDamperType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcVibrationDamperTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcVibrationDamperTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcVibrationIsolator_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcVibrationIsolator'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcVibrationIsolatorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcVibrationIsolatorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcVibrationIsolator_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcVibrationIsolator'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcvibrationisolatortype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcVibrationIsolatorType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcVibrationIsolatorType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcVibrationIsolatorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcVibrationIsolatorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcVoidingFeature_HasObjectType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcVoidingFeature'
    RULE_NAME = 'HasObjectType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcVoidingFeatureTypeEnum, 'USERDEFINED', INDETERMINATE) or exists(express_getattr(self, 'ObjectType', INDETERMINATE))) is not False

class IfcWall_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWall'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcWallTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcWallTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcWall_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWall'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcwalltype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcWallElementedCase_HasDecomposition:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWallElementedCase'
    RULE_NAME = 'HasDecomposition'

    @staticmethod
    def __call__(self):
        assert (hiindex(express_getattr(self, 'IsDecomposedBy', INDETERMINATE)) > 0) is not False

class IfcWallStandardCase_HasMaterialLayerSetUsage:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWallStandardCase'
    RULE_NAME = 'HasMaterialLayerSetUsage'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in usedin(self, 'ifc4x3_rc4.ifcrelassociates.relatedobjects') if 'ifc4x3_rc4.ifcrelassociatesmaterial' in typeof(temp) and 'ifc4x3_rc4.ifcmateriallayersetusage' in typeof(express_getattr(temp, 'RelatingMaterial', INDETERMINATE))]) == 1) is not False

class IfcWallType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWallType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcWallTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcWallTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcWasteTerminal_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWasteTerminal'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcWasteTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcWasteTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcWasteTerminal_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWasteTerminal'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcwasteterminaltype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcWasteTerminalType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWasteTerminalType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcWasteTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcWasteTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcWindow_CorrectStyleAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWindow'
    RULE_NAME = 'CorrectStyleAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcwindowtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcWindow_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWindow'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcWindowTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcWindowTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcWindow_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWindow'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x3_rc4.ifcwindowtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcWindowLiningProperties_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWindowLiningProperties'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        liningdepth = express_getattr(self, 'LiningDepth', INDETERMINATE)
        liningthickness = express_getattr(self, 'LiningThickness', INDETERMINATE)
        assert (not (exists(liningdepth) and (not exists(liningthickness)))) is not False

class IfcWindowLiningProperties_WR32:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWindowLiningProperties'
    RULE_NAME = 'WR32'

    @staticmethod
    def __call__(self):
        firsttransomoffset = express_getattr(self, 'FirstTransomOffset', INDETERMINATE)
        secondtransomoffset = express_getattr(self, 'SecondTransomOffset', INDETERMINATE)
        assert (not (not exists(firsttransomoffset) and exists(secondtransomoffset))) is not False

class IfcWindowLiningProperties_WR33:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWindowLiningProperties'
    RULE_NAME = 'WR33'

    @staticmethod
    def __call__(self):
        firstmullionoffset = express_getattr(self, 'FirstMullionOffset', INDETERMINATE)
        secondmullionoffset = express_getattr(self, 'SecondMullionOffset', INDETERMINATE)
        assert (not (not exists(firstmullionoffset) and exists(secondmullionoffset))) is not False

class IfcWindowLiningProperties_WR34:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWindowLiningProperties'
    RULE_NAME = 'WR34'

    @staticmethod
    def __call__(self):
        assert (exists(lambda : express_getitem(express_getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and ('ifc4x3_rc4.ifcwindowtype' in typeof(express_getitem(express_getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) or 'ifc4x3_rc4.ifcwindowstyle' in typeof(express_getitem(express_getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)))) is not False

class IfcWindowPanelProperties_ApplicableToType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWindowPanelProperties'
    RULE_NAME = 'ApplicableToType'

    @staticmethod
    def __call__(self):
        assert (exists(lambda : express_getitem(express_getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and ('ifc4x3_rc4.ifcwindowtype' in typeof(express_getitem(express_getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) or 'ifc4x3_rc4.ifcwindowstyle' in typeof(express_getitem(express_getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)))) is not False

class IfcWindowType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWindowType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcWindowTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcWindowTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcWorkCalendar_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWorkCalendar'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcWorkCalendarTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcWorkCalendarTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcWorkPlan_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWorkPlan'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcWorkPlanTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcWorkPlanTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcWorkSchedule_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWorkSchedule'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcWorkScheduleTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcWorkScheduleTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcZShapeProfileDef_ValidFlangeThickness:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcZShapeProfileDef'
    RULE_NAME = 'ValidFlangeThickness'

    @staticmethod
    def __call__(self):
        depth = express_getattr(self, 'Depth', INDETERMINATE)
        flangethickness = express_getattr(self, 'FlangeThickness', INDETERMINATE)
        assert (flangethickness < depth / 2.0) is not False

class IfcZone_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcZone'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (sizeof(express_getattr(self, 'IsGroupedBy', INDETERMINATE)) == 0 or sizeof([temp for temp in express_getattr(express_getitem(express_getattr(self, 'IsGroupedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatedObjects', INDETERMINATE) if not ('ifc4x3_rc4.ifczone' in typeof(temp) or 'ifc4x3_rc4.ifcspace' in typeof(temp) or 'ifc4x3_rc4.ifcspatialzone' in typeof(temp))]) == 0) is not False

class IfcRepresentationContextSameWCS:
    SCOPE = 'file'

    @staticmethod
    def __call__(file):
        IfcGeometricRepresentationContext = express_getattr(file, 'by_type', INDETERMINATE)('IfcGeometricRepresentationContext')
        isdifferent = False
        if sizeof(IfcGeometricRepresentationContext) > 1:
            for i in range(2, hiindex(IfcGeometricRepresentationContext) + 1):
                if express_getattr(express_getitem(IfcGeometricRepresentationContext, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'WorldCoordinateSystem', INDETERMINATE) != express_getattr(express_getitem(IfcGeometricRepresentationContext, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'WorldCoordinateSystem', INDETERMINATE):
                    isdifferent = not IfcSameValidPrecision(express_getattr(express_getitem(IfcGeometricRepresentationContext, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Precision', INDETERMINATE), express_getattr(express_getitem(IfcGeometricRepresentationContext, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Precision', INDETERMINATE)) or not IfcSameAxis2Placement(express_getattr(express_getitem(IfcGeometricRepresentationContext, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'WorldCoordinateSystem', INDETERMINATE), express_getattr(express_getitem(IfcGeometricRepresentationContext, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'WorldCoordinateSystem', INDETERMINATE), express_getattr(express_getitem(IfcGeometricRepresentationContext, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Precision', INDETERMINATE))
                    if isdifferent == True:
                        break
        assert (isdifferent == False) is not False

class IfcSingleProjectInstance:
    SCOPE = 'file'

    @staticmethod
    def __call__(file):
        IfcProject = express_getattr(file, 'by_type', INDETERMINATE)('IfcProject')
        assert (sizeof(IfcProject) <= 1) is not False

def IfcAssociatedSurface(arg):
    surf = express_getattr(arg, 'BasisSurface', INDETERMINATE)
    return surf

def IfcBaseAxis(dim, axis1, axis2, axis3):
    if dim == 3:
        d1 = nvl(IfcNormalise(axis3), IfcDirection(DirectionRatios=[0.0, 0.0, 1.0]))
        d2 = IfcFirstProjAxis(d1, axis1)
        u = [d2, IfcSecondProjAxis(d1, d2, axis2), d1]
    elif exists(axis1):
        d1 = IfcNormalise(axis1)
        u = [d1, IfcOrthogonalComplement(d1)]
        if exists(axis2):
            factor = IfcDotProduct(axis2, express_getitem(u, 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))
            if factor < 0.0:
                u[2 - EXPRESS_ONE_BASED_INDEXING].DirectionRatios[1 - EXPRESS_ONE_BASED_INDEXING] = -express_getitem(express_getattr(express_getitem(u, 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'DirectionRatios', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
                u[2 - EXPRESS_ONE_BASED_INDEXING].DirectionRatios[2 - EXPRESS_ONE_BASED_INDEXING] = -express_getitem(express_getattr(express_getitem(u, 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'DirectionRatios', INDETERMINATE), 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    elif exists(axis2):
        d1 = IfcNormalise(axis2)
        u = [IfcOrthogonalComplement(d1), d1]
        u[1 - EXPRESS_ONE_BASED_INDEXING].DirectionRatios[1 - EXPRESS_ONE_BASED_INDEXING] = -express_getitem(express_getattr(express_getitem(u, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'DirectionRatios', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
        u[1 - EXPRESS_ONE_BASED_INDEXING].DirectionRatios[2 - EXPRESS_ONE_BASED_INDEXING] = -express_getitem(express_getattr(express_getitem(u, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'DirectionRatios', INDETERMINATE), 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    else:
        u = [IfcDirection(DirectionRatios=[1.0, 0.0]), IfcDirection(DirectionRatios=[0.0, 1.0])]
    return u

def IfcBooleanChoose(b, choice1, choice2):
    if b:
        return choice1
    else:
        return choice2

def IfcBuild2Axes(refdirection):
    d = nvl(IfcNormalise(refdirection), IfcDirection(DirectionRatios=[1.0, 0.0]))
    return [d, IfcOrthogonalComplement(d)]

def IfcBuildAxes(axis, refdirection):
    d1 = nvl(IfcNormalise(axis), IfcDirection(DirectionRatios=[0.0, 0.0, 1.0]))
    d2 = IfcFirstProjAxis(d1, refdirection)
    return [d2, express_getattr(IfcNormalise(IfcCrossProduct(d1, d2)), 'Orientation', INDETERMINATE), d1]

def IfcConsecutiveSegments(segments):
    result = True
    for i in range(1, hiindex(segments) - 1 + 1):
        if express_getitem(express_getitem(segments, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), hiindex(segments[i - EXPRESS_ONE_BASED_INDEXING]) - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) != express_getitem(express_getitem(segments, i + 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE):
            result = False
            break
    return result

def IfcConstraintsParamBSpline(degree, upknots, upcp, knotmult, knots):
    result = True
    sum = express_getitem(knotmult, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    for i in range(2, upknots + 1):
        sum = sum + express_getitem(knotmult, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    if degree < 1 or upknots < 2 or upcp < degree or (sum != degree + upcp + 2):
        result = False
        return result
    k = express_getitem(knotmult, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    if k < 1 or k > degree + 1:
        result = False
        return result
    for i in range(2, upknots + 1):
        if express_getitem(knotmult, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) < 1 or express_getitem(knots, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) <= express_getitem(knots, i - 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE):
            result = False
            return result
        k = express_getitem(knotmult, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
        if i < upknots and k > degree:
            result = False
            return result
        if i == upknots and k > degree + 1:
            result = False
            return result
    return result

def IfcConvertDirectionInto2D(direction):
    direction2d = IfcDirection(DirectionRatios=[0.0, 1.0])
    temp = list(express_getattr(direction2d, 'DirectionRatios', INDETERMINATE))
    temp[1 - EXPRESS_ONE_BASED_INDEXING] = express_getitem(express_getattr(direction, 'DirectionRatios', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    direction2d.DirectionRatios = temp
    temp = list(express_getattr(direction2d, 'DirectionRatios', INDETERMINATE))
    temp[2 - EXPRESS_ONE_BASED_INDEXING] = express_getitem(express_getattr(direction, 'DirectionRatios', INDETERMINATE), 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    direction2d.DirectionRatios = temp
    return direction2d

def IfcCorrectDimensions(m, dim):
    if m == lengthunit:
        if dim == IfcDimensionalExponents(1, 0, 0, 0, 0, 0, 0):
            return True
        else:
            return False
    elif m == massunit:
        if dim == IfcDimensionalExponents(0, 1, 0, 0, 0, 0, 0):
            return True
        else:
            return False
    elif m == timeunit:
        if dim == IfcDimensionalExponents(0, 0, 1, 0, 0, 0, 0):
            return True
        else:
            return False
    elif m == electriccurrentunit:
        if dim == IfcDimensionalExponents(0, 0, 0, 1, 0, 0, 0):
            return True
        else:
            return False
    elif m == thermodynamictemperatureunit:
        if dim == IfcDimensionalExponents(0, 0, 0, 0, 1, 0, 0):
            return True
        else:
            return False
    elif m == amountofsubstanceunit:
        if dim == IfcDimensionalExponents(0, 0, 0, 0, 0, 1, 0):
            return True
        else:
            return False
    elif m == luminousintensityunit:
        if dim == IfcDimensionalExponents(0, 0, 0, 0, 0, 0, 1):
            return True
        else:
            return False
    elif m == planeangleunit:
        if dim == IfcDimensionalExponents(0, 0, 0, 0, 0, 0, 0):
            return True
        else:
            return False
    elif m == solidangleunit:
        if dim == IfcDimensionalExponents(0, 0, 0, 0, 0, 0, 0):
            return True
        else:
            return False
    elif m == areaunit:
        if dim == IfcDimensionalExponents(2, 0, 0, 0, 0, 0, 0):
            return True
        else:
            return False
    elif m == volumeunit:
        if dim == IfcDimensionalExponents(3, 0, 0, 0, 0, 0, 0):
            return True
        else:
            return False
    elif m == absorbeddoseunit:
        if dim == IfcDimensionalExponents(2, 0, -2, 0, 0, 0, 0):
            return True
        else:
            return False
    elif m == radioactivityunit:
        if dim == IfcDimensionalExponents(0, 0, -1, 0, 0, 0, 0):
            return True
        else:
            return False
    elif m == electriccapacitanceunit:
        if dim == IfcDimensionalExponents(-2, -1, 4, 2, 0, 0, 0):
            return True
        else:
            return False
    elif m == doseequivalentunit:
        if dim == IfcDimensionalExponents(2, 0, -2, 0, 0, 0, 0):
            return True
        else:
            return False
    elif m == electricchargeunit:
        if dim == IfcDimensionalExponents(0, 0, 1, 1, 0, 0, 0):
            return True
        else:
            return False
    elif m == electricconductanceunit:
        if dim == IfcDimensionalExponents(-2, -1, 3, 2, 0, 0, 0):
            return True
        else:
            return False
    elif m == electricvoltageunit:
        if dim == IfcDimensionalExponents(2, 1, -3, -1, 0, 0, 0):
            return True
        else:
            return False
    elif m == electricresistanceunit:
        if dim == IfcDimensionalExponents(2, 1, -3, -2, 0, 0, 0):
            return True
        else:
            return False
    elif m == energyunit:
        if dim == IfcDimensionalExponents(2, 1, -2, 0, 0, 0, 0):
            return True
        else:
            return False
    elif m == forceunit:
        if dim == IfcDimensionalExponents(1, 1, -2, 0, 0, 0, 0):
            return True
        else:
            return False
    elif m == frequencyunit:
        if dim == IfcDimensionalExponents(0, 0, -1, 0, 0, 0, 0):
            return True
        else:
            return False
    elif m == inductanceunit:
        if dim == IfcDimensionalExponents(2, 1, -2, -2, 0, 0, 0):
            return True
        else:
            return False
    elif m == illuminanceunit:
        if dim == IfcDimensionalExponents(-2, 0, 0, 0, 0, 0, 1):
            return True
        else:
            return False
    elif m == luminousfluxunit:
        if dim == IfcDimensionalExponents(0, 0, 0, 0, 0, 0, 1):
            return True
        else:
            return False
    elif m == magneticfluxunit:
        if dim == IfcDimensionalExponents(2, 1, -2, -1, 0, 0, 0):
            return True
        else:
            return False
    elif m == magneticfluxdensityunit:
        if dim == IfcDimensionalExponents(0, 1, -2, -1, 0, 0, 0):
            return True
        else:
            return False
    elif m == powerunit:
        if dim == IfcDimensionalExponents(2, 1, -3, 0, 0, 0, 0):
            return True
        else:
            return False
    elif m == pressureunit:
        if dim == IfcDimensionalExponents(-1, 1, -2, 0, 0, 0, 0):
            return True
        else:
            return False
    else:
        return unknown

def IfcCorrectFillAreaStyle(styles):
    hatching = 0
    tiles = 0
    colour = 0
    external = 0
    external = sizeof([style for style in styles if 'ifc4x3_rc4.ifcexternallydefinedhatchstyle' in typeof(style)])
    hatching = sizeof([style for style in styles if 'ifc4x3_rc4.ifcfillareastylehatching' in typeof(style)])
    tiles = sizeof([style for style in styles if 'ifc4x3_rc4.ifcfillareastyletiles' in typeof(style)])
    colour = sizeof([style for style in styles if 'ifc4x3_rc4.ifccolour' in typeof(style)])
    if external > 1:
        return False
    if external == 1 and (hatching > 0 or tiles > 0 or colour > 0):
        return False
    if colour > 1:
        return False
    if hatching > 0 and tiles > 0:
        return False
    return True

def IfcCorrectLocalPlacement(axisplacement, relplacement):
    if exists(relplacement):
        if 'ifc4x3_rc4.ifcgridplacement' in typeof(relplacement):
            return None
        if 'ifc4x3_rc4.ifclocalplacement' in typeof(relplacement):
            if 'ifc4x3_rc4.ifcaxis2placement2d' in typeof(axisplacement):
                return True
            if 'ifc4x3_rc4.ifcaxis2placement3d' in typeof(axisplacement):
                if express_getattr(express_getattr(relplacement, 'RelativePlacement', INDETERMINATE), 'Dim', INDETERMINATE) == 3:
                    return True
                else:
                    return False
        return True
    return None

def IfcCorrectObjectAssignment(constraint, objects):
    count = 0
    if not exists(constraint):
        return True
    if constraint == express_getattr(IfcObjectTypeEnum, 'NOTDEFINED', INDETERMINATE):
        return True
    elif constraint == express_getattr(IfcObjectTypeEnum, 'PRODUCT', INDETERMINATE):
        count = sizeof([temp for temp in objects if not 'ifc4x3_rc4.ifcproduct' in typeof(temp)])
        return count == 0
    elif constraint == express_getattr(IfcObjectTypeEnum, 'PROCESS', INDETERMINATE):
        count = sizeof([temp for temp in objects if not 'ifc4x3_rc4.ifcprocess' in typeof(temp)])
        return count == 0
    elif constraint == express_getattr(IfcObjectTypeEnum, 'CONTROL', INDETERMINATE):
        count = sizeof([temp for temp in objects if not 'ifc4x3_rc4.ifccontrol' in typeof(temp)])
        return count == 0
    elif constraint == express_getattr(IfcObjectTypeEnum, 'RESOURCE', INDETERMINATE):
        count = sizeof([temp for temp in objects if not 'ifc4x3_rc4.ifcresource' in typeof(temp)])
        return count == 0
    elif constraint == express_getattr(IfcObjectTypeEnum, 'ACTOR', INDETERMINATE):
        count = sizeof([temp for temp in objects if not 'ifc4x3_rc4.ifcactor' in typeof(temp)])
        return count == 0
    elif constraint == express_getattr(IfcObjectTypeEnum, 'GROUP', INDETERMINATE):
        count = sizeof([temp for temp in objects if not 'ifc4x3_rc4.ifcgroup' in typeof(temp)])
        return count == 0
    elif constraint == express_getattr(IfcObjectTypeEnum, 'PROJECT', INDETERMINATE):
        count = sizeof([temp for temp in objects if not 'ifc4x3_rc4.ifcproject' in typeof(temp)])
        return count == 0
    else:
        return None

def IfcCorrectUnitAssignment(units):
    namedunitnumber = 0
    derivedunitnumber = 0
    monetaryunitnumber = 0
    namedunitnames = express_set([])
    derivedunitnames = express_set([])
    namedunitnumber = sizeof([temp for temp in units if 'ifc4x3_rc4.ifcnamedunit' in typeof(temp) and (not express_getattr(temp, 'UnitType', INDETERMINATE) == express_getattr(IfcUnitEnum, 'USERDEFINED', INDETERMINATE))])
    derivedunitnumber = sizeof([temp for temp in units if 'ifc4x3_rc4.ifcderivedunit' in typeof(temp) and (not express_getattr(temp, 'UnitType', INDETERMINATE) == express_getattr(IfcDerivedUnitEnum, 'USERDEFINED', INDETERMINATE))])
    monetaryunitnumber = sizeof([temp for temp in units if 'ifc4x3_rc4.ifcmonetaryunit' in typeof(temp)])
    for i in range(1, sizeof(units) + 1):
        if 'ifc4x3_rc4.ifcnamedunit' in typeof(express_getitem(units, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and (not express_getattr(express_getitem(units, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'UnitType', INDETERMINATE) == express_getattr(IfcUnitEnum, 'USERDEFINED', INDETERMINATE)):
            namedunitnames = namedunitnames + express_getattr(express_getitem(units, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'UnitType', INDETERMINATE)
        if 'ifc4x3_rc4.ifcderivedunit' in typeof(express_getitem(units, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and (not express_getattr(express_getitem(units, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'UnitType', INDETERMINATE) == express_getattr(IfcDerivedUnitEnum, 'USERDEFINED', INDETERMINATE)):
            derivedunitnames = derivedunitnames + express_getattr(express_getitem(units, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'UnitType', INDETERMINATE)
    return sizeof(namedunitnames) == namedunitnumber and sizeof(derivedunitnames) == derivedunitnumber and (monetaryunitnumber <= 1)

def IfcCrossProduct(arg1, arg2):
    if (not exists(arg1) or express_getattr(arg1, 'Dim', INDETERMINATE) == 2) or (not exists(arg2) or express_getattr(arg2, 'Dim', INDETERMINATE) == 2):
        return None
    else:
        v1 = express_getattr(IfcNormalise(arg1), 'DirectionRatios', INDETERMINATE)
        v2 = express_getattr(IfcNormalise(arg2), 'DirectionRatios', INDETERMINATE)
        res = IfcDirection(DirectionRatios=[express_getitem(v1, 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) * express_getitem(v2, 3 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) - express_getitem(v1, 3 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) * express_getitem(v2, 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), express_getitem(v1, 3 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) * express_getitem(v2, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) - express_getitem(v1, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) * express_getitem(v2, 3 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), express_getitem(v1, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) * express_getitem(v2, 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) - express_getitem(v1, 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) * express_getitem(v2, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)])
        mag = 0.0
        for i in range(1, 3 + 1):
            mag = mag + express_getitem(express_getattr(res, 'DirectionRatios', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) * express_getitem(express_getattr(res, 'DirectionRatios', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
        if mag > 0.0:
            result = IfcVector(Orientation=res, Magnitude=sqrt(mag))
        else:
            result = IfcVector(Orientation=arg1, Magnitude=0.0)
        return result

def IfcCurveDim(curve):
    if 'ifc4x3_rc4.ifcline' in typeof(curve):
        return express_getattr(express_getattr(curve, 'Pnt', INDETERMINATE), 'Dim', INDETERMINATE)
    if 'ifc4x3_rc4.ifcconic' in typeof(curve):
        return express_getattr(express_getattr(curve, 'Position', INDETERMINATE), 'Dim', INDETERMINATE)
    if 'ifc4x3_rc4.ifcpolyline' in typeof(curve):
        return express_getattr(express_getitem(express_getattr(curve, 'Points', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)
    if 'ifc4x3_rc4.ifctrimmedcurve' in typeof(curve):
        return IfcCurveDim(express_getattr(curve, 'BasisCurve', INDETERMINATE))
    if 'ifc4x3_rc4.ifcgradientcurve' in typeof(curve):
        return 3
    if 'ifc4x3_rc4.ifcsegmentedreferencecurve' in typeof(curve):
        return 3
    if 'ifc4x3_rc4.ifccompositecurve' in typeof(curve):
        return express_getattr(express_getitem(express_getattr(curve, 'Segments', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)
    if 'ifc4x3_rc4.ifcbsplinecurve' in typeof(curve):
        return express_getattr(express_getitem(express_getattr(curve, 'ControlPointsList', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)
    if 'ifc4x3_rc4.ifcoffsetcurve2d' in typeof(curve):
        return 2
    if 'ifc4x3_rc4.ifcoffsetcurve3d' in typeof(curve):
        return 3
    if 'ifc4x3_rc4.ifcoffsetcurvebydistances' in typeof(curve):
        return 3
    if 'ifc4x3_rc4.ifccurvesegment2d' in typeof(curve):
        return 2
    if 'ifc4x3_rc4.ifcpolynomialcurve' in typeof(curve):
        if not exists(express_getattr(curve, 'CoefficientsZ', INDETERMINATE)) and express_getattr(express_getattr(curve, 'Position', INDETERMINATE), 'Dim', INDETERMINATE) == 2:
            return 2
        return 3
    if 'ifc4x3_rc4.ifcpcurve' in typeof(curve):
        return 3
    if 'ifc4x3_rc4.ifcindexedpolycurve' in typeof(curve):
        return express_getattr(express_getattr(curve, 'Points', INDETERMINATE), 'Dim', INDETERMINATE)
    return None

def IfcCurveWeightsPositive(b):
    result = True
    for i in range(0, express_getattr(b, 'UpperIndexOnControlPoints', INDETERMINATE) + 1):
        if express_getitem(express_getattr(b, 'Weights', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) <= 0.0:
            result = False
            return result
    return result

def IfcDeriveDimensionalExponents(unitelements):
    result = IfcDimensionalExponents(0, 0, 0, 0, 0, 0, 0)
    for i in range(loindex(unitelements), hiindex(unitelements) + 1):
        result.LengthExponent = express_getattr(result, 'LengthExponent', INDETERMINATE) + express_getattr(express_getitem(unitelements, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Exponent', INDETERMINATE) * express_getattr(express_getattr(express_getattr(express_getitem(unitelements, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Unit', INDETERMINATE), 'Dimensions', INDETERMINATE), 'LengthExponent', INDETERMINATE)
        result.MassExponent = express_getattr(result, 'MassExponent', INDETERMINATE) + express_getattr(express_getitem(unitelements, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Exponent', INDETERMINATE) * express_getattr(express_getattr(express_getattr(express_getitem(unitelements, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Unit', INDETERMINATE), 'Dimensions', INDETERMINATE), 'MassExponent', INDETERMINATE)
        result.TimeExponent = express_getattr(result, 'TimeExponent', INDETERMINATE) + express_getattr(express_getitem(unitelements, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Exponent', INDETERMINATE) * express_getattr(express_getattr(express_getattr(express_getitem(unitelements, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Unit', INDETERMINATE), 'Dimensions', INDETERMINATE), 'TimeExponent', INDETERMINATE)
        result.ElectricCurrentExponent = express_getattr(result, 'ElectricCurrentExponent', INDETERMINATE) + express_getattr(express_getitem(unitelements, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Exponent', INDETERMINATE) * express_getattr(express_getattr(express_getattr(express_getitem(unitelements, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Unit', INDETERMINATE), 'Dimensions', INDETERMINATE), 'ElectricCurrentExponent', INDETERMINATE)
        result.ThermodynamicTemperatureExponent = express_getattr(result, 'ThermodynamicTemperatureExponent', INDETERMINATE) + express_getattr(express_getitem(unitelements, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Exponent', INDETERMINATE) * express_getattr(express_getattr(express_getattr(express_getitem(unitelements, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Unit', INDETERMINATE), 'Dimensions', INDETERMINATE), 'ThermodynamicTemperatureExponent', INDETERMINATE)
        result.AmountOfSubstanceExponent = express_getattr(result, 'AmountOfSubstanceExponent', INDETERMINATE) + express_getattr(express_getitem(unitelements, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Exponent', INDETERMINATE) * express_getattr(express_getattr(express_getattr(express_getitem(unitelements, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Unit', INDETERMINATE), 'Dimensions', INDETERMINATE), 'AmountOfSubstanceExponent', INDETERMINATE)
        result.LuminousIntensityExponent = express_getattr(result, 'LuminousIntensityExponent', INDETERMINATE) + express_getattr(express_getitem(unitelements, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Exponent', INDETERMINATE) * express_getattr(express_getattr(express_getattr(express_getitem(unitelements, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Unit', INDETERMINATE), 'Dimensions', INDETERMINATE), 'LuminousIntensityExponent', INDETERMINATE)
    return result

def IfcDimensionsForSiUnit(n):
    if n == metre:
        return IfcDimensionalExponents(1, 0, 0, 0, 0, 0, 0)
    elif n == square_metre:
        return IfcDimensionalExponents(2, 0, 0, 0, 0, 0, 0)
    elif n == cubic_metre:
        return IfcDimensionalExponents(3, 0, 0, 0, 0, 0, 0)
    elif n == gram:
        return IfcDimensionalExponents(0, 1, 0, 0, 0, 0, 0)
    elif n == second:
        return IfcDimensionalExponents(0, 0, 1, 0, 0, 0, 0)
    elif n == ampere:
        return IfcDimensionalExponents(0, 0, 0, 1, 0, 0, 0)
    elif n == kelvin:
        return IfcDimensionalExponents(0, 0, 0, 0, 1, 0, 0)
    elif n == mole:
        return IfcDimensionalExponents(0, 0, 0, 0, 0, 1, 0)
    elif n == candela:
        return IfcDimensionalExponents(0, 0, 0, 0, 0, 0, 1)
    elif n == radian:
        return IfcDimensionalExponents(0, 0, 0, 0, 0, 0, 0)
    elif n == steradian:
        return IfcDimensionalExponents(0, 0, 0, 0, 0, 0, 0)
    elif n == hertz:
        return IfcDimensionalExponents(0, 0, -1, 0, 0, 0, 0)
    elif n == newton:
        return IfcDimensionalExponents(1, 1, -2, 0, 0, 0, 0)
    elif n == pascal:
        return IfcDimensionalExponents(-1, 1, -2, 0, 0, 0, 0)
    elif n == joule:
        return IfcDimensionalExponents(2, 1, -2, 0, 0, 0, 0)
    elif n == watt:
        return IfcDimensionalExponents(2, 1, -3, 0, 0, 0, 0)
    elif n == coulomb:
        return IfcDimensionalExponents(0, 0, 1, 1, 0, 0, 0)
    elif n == volt:
        return IfcDimensionalExponents(2, 1, -3, -1, 0, 0, 0)
    elif n == farad:
        return IfcDimensionalExponents(-2, -1, 4, 2, 0, 0, 0)
    elif n == ohm:
        return IfcDimensionalExponents(2, 1, -3, -2, 0, 0, 0)
    elif n == siemens:
        return IfcDimensionalExponents(-2, -1, 3, 2, 0, 0, 0)
    elif n == weber:
        return IfcDimensionalExponents(2, 1, -2, -1, 0, 0, 0)
    elif n == tesla:
        return IfcDimensionalExponents(0, 1, -2, -1, 0, 0, 0)
    elif n == henry:
        return IfcDimensionalExponents(2, 1, -2, -2, 0, 0, 0)
    elif n == degree_celsius:
        return IfcDimensionalExponents(0, 0, 0, 0, 1, 0, 0)
    elif n == lumen:
        return IfcDimensionalExponents(0, 0, 0, 0, 0, 0, 1)
    elif n == lux:
        return IfcDimensionalExponents(-2, 0, 0, 0, 0, 0, 1)
    elif n == becquerel:
        return IfcDimensionalExponents(0, 0, -1, 0, 0, 0, 0)
    elif n == gray:
        return IfcDimensionalExponents(2, 0, -2, 0, 0, 0, 0)
    elif n == sievert:
        return IfcDimensionalExponents(2, 0, -2, 0, 0, 0, 0)
    else:
        return IfcDimensionalExponents(0, 0, 0, 0, 0, 0, 0)

def IfcDotProduct(arg1, arg2):
    if not exists(arg1) or not exists(arg2):
        scalar = None
    elif express_getattr(arg1, 'Dim', INDETERMINATE) != express_getattr(arg2, 'Dim', INDETERMINATE):
        scalar = None
    else:
        vec1 = IfcNormalise(arg1)
        vec2 = IfcNormalise(arg2)
        ndim = express_getattr(arg1, 'Dim', INDETERMINATE)
        scalar = 0.0
        for i in range(1, ndim + 1):
            scalar = scalar + express_getitem(express_getattr(vec1, 'DirectionRatios', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) * express_getitem(express_getattr(vec2, 'DirectionRatios', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    return scalar

def IfcFirstProjAxis(zaxis, arg):
    if not exists(zaxis):
        return None
    else:
        z = IfcNormalise(zaxis)
        if not exists(arg):
            if express_getattr(z, 'DirectionRatios', INDETERMINATE) != [1.0, 0.0, 0.0]:
                v = IfcDirection(DirectionRatios=[1.0, 0.0, 0.0])
            else:
                v = IfcDirection(DirectionRatios=[0.0, 1.0, 0.0])
        else:
            if express_getattr(arg, 'Dim', INDETERMINATE) != 3:
                return None
            if express_getattr(IfcCrossProduct(arg, z), 'Magnitude', INDETERMINATE) == 0.0:
                return None
            else:
                v = IfcNormalise(arg)
        xvec = IfcScalarTimesVector(IfcDotProduct(v, z), z)
        xaxis = express_getattr(IfcVectorDifference(v, xvec), 'Orientation', INDETERMINATE)
        xaxis = IfcNormalise(xaxis)
    return xaxis

def IfcGetBasisSurface(c):
    surfs = []
    if 'ifc4x3_rc4.ifcpcurve' in typeof(c):
        surfs = [express_getattr(c, 'BasisSurface', INDETERMINATE)]
    elif 'ifc4x3_rc4.ifcsurfacecurve' in typeof(c):
        n = sizeof(express_getattr(c, 'AssociatedGeometry', INDETERMINATE))
        for i in range(1, n + 1):
            surfs = surfs + IfcAssociatedSurface(express_getitem(express_getattr(c, 'AssociatedGeometry', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))
    if 'ifc4x3_rc4.ifccompositecurveonsurface' in typeof(c):
        n = sizeof(express_getattr(c, 'Segments', INDETERMINATE))
        surfs = IfcGetBasisSurface(express_getattr(express_getitem(express_getattr(c, 'Segments', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'ParentCurve', INDETERMINATE))
        if n > 1:
            for i in range(2, n + 1):
                surfs = surfs * IfcGetBasisSurface(express_getattr(express_getitem(express_getattr(c, 'Segments', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'ParentCurve', INDETERMINATE))
    return surfs

def IfcGradient(gradientcurve):
    return 1

def IfcListToArray(lis, low, u):
    n = sizeof(lis)
    if n != u - low + 1:
        return None
    else:
        res = [express_getitem(lis, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)] * n
        for i in range(2, n + 1):
            temp = list(res)
            temp[low + i - 1 - EXPRESS_ONE_BASED_INDEXING] = express_getitem(lis, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
            res = temp
        return res

def IfcLoopHeadToTail(aloop):
    p = True
    n = sizeof(express_getattr(aloop, 'EdgeList', INDETERMINATE))
    for i in range(2, n + 1):
        p = p and express_getattr(express_getitem(express_getattr(aloop, 'EdgeList', INDETERMINATE), i - 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'EdgeEnd', INDETERMINATE) == express_getattr(express_getitem(express_getattr(aloop, 'EdgeList', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'EdgeStart', INDETERMINATE)
    return p

def IfcMakeArrayOfArray(lis, low1, u1, low2, u2):
    if u1 - low1 + 1 != sizeof(lis):
        return None
    if u2 - low2 + 1 != sizeof(express_getitem(lis, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)):
        return None
    res = [IfcListToArray(express_getitem(lis, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), low2, u2)] * u1 - low1 + 1
    for i in range(2, hiindex(lis) + 1):
        if u2 - low2 + 1 != sizeof(express_getitem(lis, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)):
            return None
        temp = list(res)
        temp[low1 + i - 1 - EXPRESS_ONE_BASED_INDEXING] = IfcListToArray(express_getitem(lis, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), low2, u2)
        res = temp
    return res

def IfcMlsTotalThickness(layerset):
    max = express_getattr(express_getitem(express_getattr(layerset, 'MaterialLayers', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'LayerThickness', INDETERMINATE)
    if sizeof(express_getattr(layerset, 'MaterialLayers', INDETERMINATE)) > 1:
        for i in range(2, hiindex(express_getattr(layerset, 'MaterialLayers', INDETERMINATE)) + 1):
            max = max + express_getattr(express_getitem(express_getattr(layerset, 'MaterialLayers', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'LayerThickness', INDETERMINATE)
    return max

def IfcNormalise(arg):
    v = IfcDirection(DirectionRatios=[1.0, 0.0])
    vec = IfcVector(Orientation=IfcDirection(DirectionRatios=[1.0, 0.0]), Magnitude=1.0)
    result = v
    if not exists(arg):
        return None
    else:
        if 'ifc4x3_rc4.ifcvector' in typeof(arg):
            ndim = express_getattr(arg, 'Dim', INDETERMINATE)
            v.DirectionRatios = express_getattr(express_getattr(arg, 'Orientation', INDETERMINATE), 'DirectionRatios', INDETERMINATE)
            vec.Magnitude = express_getattr(arg, 'Magnitude', INDETERMINATE)
            vec.Orientation = v
            if express_getattr(arg, 'Magnitude', INDETERMINATE) == 0.0:
                return None
            else:
                vec.Magnitude = 1.0
        else:
            ndim = express_getattr(arg, 'Dim', INDETERMINATE)
            v.DirectionRatios = express_getattr(arg, 'DirectionRatios', INDETERMINATE)
        mag = 0.0
        for i in range(1, ndim + 1):
            mag = mag + express_getitem(express_getattr(v, 'DirectionRatios', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) * express_getitem(express_getattr(v, 'DirectionRatios', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
        if mag > 0.0:
            mag = sqrt(mag)
            for i in range(1, ndim + 1):
                temp = list(express_getattr(v, 'DirectionRatios', INDETERMINATE))
                temp[i - EXPRESS_ONE_BASED_INDEXING] = express_getitem(express_getattr(v, 'DirectionRatios', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) / mag
                v.DirectionRatios = temp
            if 'ifc4x3_rc4.ifcvector' in typeof(arg):
                vec.Orientation = v
                result = vec
            else:
                result = v
        else:
            return None
    return result

def IfcOrthogonalComplement(vec):
    if not exists(vec) or express_getattr(vec, 'Dim', INDETERMINATE) != 2:
        return None
    else:
        result = IfcDirection(DirectionRatios=[-express_getitem(express_getattr(vec, 'DirectionRatios', INDETERMINATE), 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), express_getitem(express_getattr(vec, 'DirectionRatios', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)])
        return result

def IfcPathHeadToTail(apath):
    n = 0
    p = unknown
    n = sizeof(express_getattr(apath, 'EdgeList', INDETERMINATE))
    for i in range(2, n + 1):
        p = p and express_getattr(express_getitem(express_getattr(apath, 'EdgeList', INDETERMINATE), i - 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'EdgeEnd', INDETERMINATE) == express_getattr(express_getitem(express_getattr(apath, 'EdgeList', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'EdgeStart', INDETERMINATE)
    return p

def IfcPointListDim(pointlist):
    if 'ifc4x3_rc4.ifccartesianpointlist2d' in typeof(pointlist):
        return 2
    if 'ifc4x3_rc4.ifccartesianpointlist3d' in typeof(pointlist):
        return 3
    return None

def IfcSameAxis2Placement(ap1, ap2, epsilon):
    return IfcSameDirection(express_getitem(express_getattr(ap1, 'P', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), express_getitem(express_getattr(ap2, 'P', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), epsilon) and IfcSameDirection(express_getitem(express_getattr(ap1, 'P', INDETERMINATE), 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), express_getitem(express_getattr(ap2, 'P', INDETERMINATE), 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), epsilon) and IfcSameCartesianPoint(express_getattr(ap1, 'Location', INDETERMINATE), express_getattr(ap1, 'Location', INDETERMINATE), epsilon)

def IfcSameCartesianPoint(cp1, cp2, epsilon):
    cp1x = express_getitem(express_getattr(cp1, 'Coordinates', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    cp1y = express_getitem(express_getattr(cp1, 'Coordinates', INDETERMINATE), 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    cp1z = 0
    cp2x = express_getitem(express_getattr(cp2, 'Coordinates', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    cp2y = express_getitem(express_getattr(cp2, 'Coordinates', INDETERMINATE), 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    cp2z = 0
    if sizeof(express_getattr(cp1, 'Coordinates', INDETERMINATE)) > 2:
        cp1z = express_getitem(express_getattr(cp1, 'Coordinates', INDETERMINATE), 3 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    if sizeof(express_getattr(cp2, 'Coordinates', INDETERMINATE)) > 2:
        cp2z = express_getitem(express_getattr(cp2, 'Coordinates', INDETERMINATE), 3 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    return IfcSameValue(cp1x, cp2x, epsilon) and IfcSameValue(cp1y, cp2y, epsilon) and IfcSameValue(cp1z, cp2z, epsilon)

def IfcSameDirection(dir1, dir2, epsilon):
    dir1x = express_getitem(express_getattr(dir1, 'DirectionRatios', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    dir1y = express_getitem(express_getattr(dir1, 'DirectionRatios', INDETERMINATE), 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    dir1z = 0
    dir2x = express_getitem(express_getattr(dir2, 'DirectionRatios', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    dir2y = express_getitem(express_getattr(dir2, 'DirectionRatios', INDETERMINATE), 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    dir2z = 0
    if sizeof(express_getattr(dir1, 'DirectionRatios', INDETERMINATE)) > 2:
        dir1z = express_getitem(express_getattr(dir1, 'DirectionRatios', INDETERMINATE), 3 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    if sizeof(express_getattr(dir2, 'DirectionRatios', INDETERMINATE)) > 2:
        dir2z = express_getitem(express_getattr(dir2, 'DirectionRatios', INDETERMINATE), 3 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    return IfcSameValue(dir1x, dir2x, epsilon) and IfcSameValue(dir1y, dir2y, epsilon) and IfcSameValue(dir1z, dir2z, epsilon)

def IfcSameValidPrecision(epsilon1, epsilon2):
    defaulteps = 1e-06
    derivationofeps = 1.001
    uppereps = 1.0
    valideps1 = nvl(epsilon1, defaulteps)
    valideps2 = nvl(epsilon2, defaulteps)
    return 0.0 < valideps1 and valideps1 <= derivationofeps * valideps2 and (valideps2 <= derivationofeps * valideps1) and (valideps2 < uppereps)

def IfcSameValue(value1, value2, epsilon):
    defaulteps = 1e-06
    valideps = nvl(epsilon, defaulteps)
    return value1 + valideps > value2 and value1 < value2 + valideps

def IfcScalarTimesVector(scalar, vec):
    if not exists(scalar) or not exists(vec):
        return None
    else:
        if 'ifc4x3_rc4.ifcvector' in typeof(vec):
            v = express_getattr(vec, 'Orientation', INDETERMINATE)
            mag = scalar * express_getattr(vec, 'Magnitude', INDETERMINATE)
        else:
            v = vec
            mag = scalar
        if mag < 0.0:
            for i in range(1, sizeof(express_getattr(v, 'DirectionRatios', INDETERMINATE)) + 1):
                temp = list(express_getattr(v, 'DirectionRatios', INDETERMINATE))
                temp[i - EXPRESS_ONE_BASED_INDEXING] = -express_getitem(express_getattr(v, 'DirectionRatios', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
                v.DirectionRatios = temp
            mag = -mag
        result = IfcVector(Orientation=IfcNormalise(v), Magnitude=mag)
    return result

def IfcSecondProjAxis(zaxis, xaxis, arg):
    if not exists(arg):
        v = IfcDirection(DirectionRatios=[0.0, 1.0, 0.0])
    else:
        v = arg
    temp = IfcScalarTimesVector(IfcDotProduct(v, zaxis), zaxis)
    yaxis = IfcVectorDifference(v, temp)
    temp = IfcScalarTimesVector(IfcDotProduct(v, xaxis), xaxis)
    yaxis = IfcVectorDifference(yaxis, temp)
    yaxis = IfcNormalise(yaxis)
    return express_getattr(yaxis, 'Orientation', INDETERMINATE)

def IfcShapeRepresentationTypes(reptype, items):
    count = 0
    if express_getattr(reptype, 'lower', INDETERMINATE)() == 'point':
        count = sizeof([temp for temp in items if 'ifc4x3_rc4.ifcpoint' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'pointcloud':
        count = sizeof([temp for temp in items if 'ifc4x3_rc4.ifccartesianpointlist3d' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'curve':
        count = sizeof([temp for temp in items if 'ifc4x3_rc4.ifccurve' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'curve2d':
        count = sizeof([temp for temp in items if 'ifc4x3_rc4.ifccurve' in typeof(temp) and express_getattr(temp, 'Dim', INDETERMINATE) == 2])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'curve3d':
        count = sizeof([temp for temp in items if 'ifc4x3_rc4.ifccurve' in typeof(temp) and express_getattr(temp, 'Dim', INDETERMINATE) == 3])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'surface':
        count = sizeof([temp for temp in items if 'ifc4x3_rc4.ifcsurface' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'surface2d':
        count = sizeof([temp for temp in items if 'ifc4x3_rc4.ifcsurface' in typeof(temp) and express_getattr(temp, 'Dim', INDETERMINATE) == 2])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'surface3d':
        count = sizeof([temp for temp in items if 'ifc4x3_rc4.ifcsurface' in typeof(temp) and express_getattr(temp, 'Dim', INDETERMINATE) == 3])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'fillarea':
        count = sizeof([temp for temp in items if 'ifc4x3_rc4.ifcannotationfillarea' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'text':
        count = sizeof([temp for temp in items if 'ifc4x3_rc4.ifctextliteral' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'advancedsurface':
        count = sizeof([temp for temp in items if 'ifc4x3_rc4.ifcbsplinesurface' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'annotation2d':
        count = sizeof([temp for temp in items if sizeof(typeof(temp) * ['ifc4x3_rc4.ifcpoint', 'ifc4x3_rc4.ifccurve', 'ifc4x3_rc4.ifcgeometriccurveset', 'ifc4x3_rc4.ifcannotationfillarea', 'ifc4x3_rc4.ifctextliteral']) == 1])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'geometricset':
        count = sizeof([temp for temp in items if 'ifc4x3_rc4.ifcgeometricset' in typeof(temp) or 'ifc4x3_rc4.ifcpoint' in typeof(temp) or 'ifc4x3_rc4.ifccurve' in typeof(temp) or ('ifc4x3_rc4.ifcsurface' in typeof(temp))])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'geometriccurveset':
        count = sizeof([temp for temp in items if 'ifc4x3_rc4.ifcgeometriccurveset' in typeof(temp) or 'ifc4x3_rc4.ifcgeometricset' in typeof(temp) or 'ifc4x3_rc4.ifcpoint' in typeof(temp) or ('ifc4x3_rc4.ifccurve' in typeof(temp))])
        for i in range(1, hiindex(items) + 1):
            if 'ifc4x3_rc4.ifcgeometricset' in typeof(express_getitem(items, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)):
                if sizeof([temp for temp in express_getattr(express_getitem(items, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Elements', INDETERMINATE) if 'ifc4x3_rc4.ifcsurface' in typeof(temp)]) > 0:
                    count = count - 1
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'tessellation':
        count = sizeof([temp for temp in items if 'ifc4x3_rc4.ifctessellateditem' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'surfaceorsolidmodel':
        count = sizeof([temp for temp in items if sizeof(['ifc4x3_rc4.ifctessellateditem', 'ifc4x3_rc4.ifcshellbasedsurfacemodel', 'ifc4x3_rc4.ifcfacebasedsurfacemodel', 'ifc4x3_rc4.ifcsolidmodel'] * typeof(temp)) >= 1])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'surfacemodel':
        count = sizeof([temp for temp in items if sizeof(['ifc4x3_rc4.ifctessellateditem', 'ifc4x3_rc4.ifcshellbasedsurfacemodel', 'ifc4x3_rc4.ifcfacebasedsurfacemodel'] * typeof(temp)) >= 1])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'solidmodel':
        count = sizeof([temp for temp in items if 'ifc4x3_rc4.ifcsolidmodel' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'sweptsolid':
        count = sizeof([temp for temp in items if sizeof(['ifc4x3_rc4.ifcextrudedareasolid', 'ifc4x3_rc4.ifcrevolvedareasolid'] * typeof(temp)) >= 1 and sizeof(['ifc4x3_rc4.ifcextrudedareasolidtapered', 'ifc4x3_rc4.ifcrevolvedareasolidtapered'] * typeof(temp)) == 0])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'advancedsweptsolid':
        count = sizeof([temp for temp in items if sizeof(['ifc4x3_rc4.ifcsweptareasolid', 'ifc4x3_rc4.ifcsweptdisksolid', 'ifc4x3_rc4.ifcsectionedsolidhorizontal'] * typeof(temp)) >= 1])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'csg':
        count = sizeof([temp for temp in items if sizeof(['ifc4x3_rc4.ifcbooleanresult', 'ifc4x3_rc4.ifccsgprimitive3d', 'ifc4x3_rc4.ifccsgsolid'] * typeof(temp)) >= 1])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'clipping':
        count = sizeof([temp for temp in items if sizeof(['ifc4x3_rc4.ifccsgsolid', 'ifc4x3_rc4.ifcbooleanclippingresult'] * typeof(temp)) >= 1])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'brep':
        count = sizeof([temp for temp in items if 'ifc4x3_rc4.ifcfacetedbrep' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'advancedbrep':
        count = sizeof([temp for temp in items if 'ifc4x3_rc4.ifcmanifoldsolidbrep' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'boundingbox':
        count = sizeof([temp for temp in items if 'ifc4x3_rc4.ifcboundingbox' in typeof(temp)])
        if sizeof(items) > 1:
            count = 0
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'sectionedspine':
        count = sizeof([temp for temp in items if 'ifc4x3_rc4.ifcsectionedspine' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'lightsource':
        count = sizeof([temp for temp in items if 'ifc4x3_rc4.ifclightsource' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'mappedrepresentation':
        count = sizeof([temp for temp in items if 'ifc4x3_rc4.ifcmappeditem' in typeof(temp)])
    else:
        return None
    return count == sizeof(items)

def IfcSurfaceWeightsPositive(b):
    result = True
    weights = express_getattr(b, 'Weights', INDETERMINATE)
    for i in range(0, express_getattr(b, 'UUpper', INDETERMINATE) + 1):
        for j in range(0, express_getattr(b, 'VUpper', INDETERMINATE) + 1):
            if express_getitem(express_getitem(weights, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), j - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) <= 0.0:
                result = False
                return result
    return result

def IfcTaperedSweptAreaProfiles(startarea, endarea):
    result = False
    if 'ifc4x3_rc4.ifcparameterizedprofiledef' in typeof(startarea):
        if 'ifc4x3_rc4.ifcderivedprofiledef' in typeof(endarea):
            result = startarea == express_getattr(endarea, 'ParentProfile', INDETERMINATE)
        else:
            result = typeof(startarea) == typeof(endarea)
    elif 'ifc4x3_rc4.ifcderivedprofiledef' in typeof(endarea):
        result = startarea == express_getattr(endarea, 'ParentProfile', INDETERMINATE)
    else:
        result = False
    return result

def IfcTopologyRepresentationTypes(reptype, items):
    count = 0
    if express_getattr(reptype, 'lower', INDETERMINATE)() == 'vertex':
        count = sizeof([temp for temp in items if 'ifc4x3_rc4.ifcvertex' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'edge':
        count = sizeof([temp for temp in items if 'ifc4x3_rc4.ifcedge' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'path':
        count = sizeof([temp for temp in items if 'ifc4x3_rc4.ifcpath' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'face':
        count = sizeof([temp for temp in items if 'ifc4x3_rc4.ifcface' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'shell':
        count = sizeof([temp for temp in items if 'ifc4x3_rc4.ifcopenshell' in typeof(temp) or 'ifc4x3_rc4.ifcclosedshell' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'undefined':
        return True
    else:
        return None
    return count == sizeof(items)

def IfcUniqueDefinitionNames(relations):
    properties = express_set([])
    if sizeof(relations) == 0:
        return True
    for i in range(1, hiindex(relations) + 1):
        definition = express_getattr(express_getitem(relations, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingPropertyDefinition', INDETERMINATE)
        if 'ifc4x3_rc4.ifcpropertysetdefinition' in typeof(definition):
            properties = properties + definition
        elif 'ifc4x3_rc4.ifcpropertysetdefinitionset' in typeof(definition):
            definitionset = definition
            for j in range(1, hiindex(definitionset) + 1):
                properties = properties + express_getitem(definitionset, j - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    result = IfcUniquePropertySetNames(properties)
    return result

def IfcUniquePropertyName(properties):
    names = express_set([])
    for i in range(1, hiindex(properties) + 1):
        names = names + express_getattr(express_getitem(properties, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Name', INDETERMINATE)
    return sizeof(names) == sizeof(properties)

def IfcUniquePropertySetNames(properties):
    names = express_set([])
    unnamed = 0
    for i in range(1, hiindex(properties) + 1):
        if 'ifc4x3_rc4.ifcpropertyset' in typeof(express_getitem(properties, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)):
            names = names + express_getattr(express_getitem(properties, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Name', INDETERMINATE)
        else:
            unnamed = unnamed + 1
    return sizeof(names) + unnamed == sizeof(properties)

def IfcUniquePropertyTemplateNames(properties):
    names = express_set([])
    for i in range(1, hiindex(properties) + 1):
        names = names + express_getattr(express_getitem(properties, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Name', INDETERMINATE)
    return sizeof(names) == sizeof(properties)

def IfcUniqueQuantityNames(properties):
    names = express_set([])
    for i in range(1, hiindex(properties) + 1):
        names = names + express_getattr(express_getitem(properties, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Name', INDETERMINATE)
    return sizeof(names) == sizeof(properties)

def IfcVectorDifference(arg1, arg2):
    if (not exists(arg1) or not exists(arg2)) or express_getattr(arg1, 'Dim', INDETERMINATE) != express_getattr(arg2, 'Dim', INDETERMINATE):
        return None
    else:
        if 'ifc4x3_rc4.ifcvector' in typeof(arg1):
            mag1 = express_getattr(arg1, 'Magnitude', INDETERMINATE)
            vec1 = express_getattr(arg1, 'Orientation', INDETERMINATE)
        else:
            mag1 = 1.0
            vec1 = arg1
        if 'ifc4x3_rc4.ifcvector' in typeof(arg2):
            mag2 = express_getattr(arg2, 'Magnitude', INDETERMINATE)
            vec2 = express_getattr(arg2, 'Orientation', INDETERMINATE)
        else:
            mag2 = 1.0
            vec2 = arg2
        vec1 = IfcNormalise(vec1)
        vec2 = IfcNormalise(vec2)
        ndim = sizeof(express_getattr(vec1, 'DirectionRatios', INDETERMINATE))
        mag = 0.0
        res = IfcDirection(DirectionRatios=[0.0] * ndim)
        for i in range(1, ndim + 1):
            temp = list(express_getattr(res, 'DirectionRatios', INDETERMINATE))
            temp[i - EXPRESS_ONE_BASED_INDEXING] = mag1 * express_getitem(express_getattr(vec1, 'DirectionRatios', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) - mag2 * express_getitem(express_getattr(vec2, 'DirectionRatios', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
            res.DirectionRatios = temp
            mag = mag + express_getitem(express_getattr(res, 'DirectionRatios', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) * express_getitem(express_getattr(res, 'DirectionRatios', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
        if mag > 0.0:
            result = IfcVector(Orientation=res, Magnitude=sqrt(mag))
        else:
            result = IfcVector(Orientation=vec1, Magnitude=0.0)
    return result

def IfcVectorSum(arg1, arg2):
    if (not exists(arg1) or not exists(arg2)) or express_getattr(arg1, 'Dim', INDETERMINATE) != express_getattr(arg2, 'Dim', INDETERMINATE):
        return None
    else:
        if 'ifc4x3_rc4.ifcvector' in typeof(arg1):
            mag1 = express_getattr(arg1, 'Magnitude', INDETERMINATE)
            vec1 = express_getattr(arg1, 'Orientation', INDETERMINATE)
        else:
            mag1 = 1.0
            vec1 = arg1
        if 'ifc4x3_rc4.ifcvector' in typeof(arg2):
            mag2 = express_getattr(arg2, 'Magnitude', INDETERMINATE)
            vec2 = express_getattr(arg2, 'Orientation', INDETERMINATE)
        else:
            mag2 = 1.0
            vec2 = arg2
        vec1 = IfcNormalise(vec1)
        vec2 = IfcNormalise(vec2)
        ndim = sizeof(express_getattr(vec1, 'DirectionRatios', INDETERMINATE))
        mag = 0.0
        res = IfcDirection(DirectionRatios=[0.0] * ndim)
        for i in range(1, ndim + 1):
            temp = list(express_getattr(res, 'DirectionRatios', INDETERMINATE))
            temp[i - EXPRESS_ONE_BASED_INDEXING] = mag1 * express_getitem(express_getattr(vec1, 'DirectionRatios', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) + mag2 * express_getitem(express_getattr(vec2, 'DirectionRatios', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
            res.DirectionRatios = temp
            mag = mag + express_getitem(express_getattr(res, 'DirectionRatios', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) * express_getitem(express_getattr(res, 'DirectionRatios', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
        if mag > 0.0:
            result = IfcVector(Orientation=res, Magnitude=sqrt(mag))
        else:
            result = IfcVector(Orientation=vec1, Magnitude=0.0)
    return result