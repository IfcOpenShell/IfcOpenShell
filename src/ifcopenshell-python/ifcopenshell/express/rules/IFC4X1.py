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
INDETERMINATE = indeterminate_type()

class enum_namespace:

    def __getattr__(self, k):
        return getattr(k, 'upper', INDETERMINATE)()
IfcActionRequestTypeEnum = enum_namespace()
email = getattr(IfcActionRequestTypeEnum, 'EMAIL', INDETERMINATE)
fax = getattr(IfcActionRequestTypeEnum, 'FAX', INDETERMINATE)
phone = getattr(IfcActionRequestTypeEnum, 'PHONE', INDETERMINATE)
post = getattr(IfcActionRequestTypeEnum, 'POST', INDETERMINATE)
verbal = getattr(IfcActionRequestTypeEnum, 'VERBAL', INDETERMINATE)
userdefined = getattr(IfcActionRequestTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcActionRequestTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcActionSourceTypeEnum = enum_namespace()
dead_load_g = getattr(IfcActionSourceTypeEnum, 'DEAD_LOAD_G', INDETERMINATE)
completion_g1 = getattr(IfcActionSourceTypeEnum, 'COMPLETION_G1', INDETERMINATE)
live_load_q = getattr(IfcActionSourceTypeEnum, 'LIVE_LOAD_Q', INDETERMINATE)
snow_s = getattr(IfcActionSourceTypeEnum, 'SNOW_S', INDETERMINATE)
wind_w = getattr(IfcActionSourceTypeEnum, 'WIND_W', INDETERMINATE)
prestressing_p = getattr(IfcActionSourceTypeEnum, 'PRESTRESSING_P', INDETERMINATE)
settlement_u = getattr(IfcActionSourceTypeEnum, 'SETTLEMENT_U', INDETERMINATE)
temperature_t = getattr(IfcActionSourceTypeEnum, 'TEMPERATURE_T', INDETERMINATE)
earthquake_e = getattr(IfcActionSourceTypeEnum, 'EARTHQUAKE_E', INDETERMINATE)
fire = getattr(IfcActionSourceTypeEnum, 'FIRE', INDETERMINATE)
impulse = getattr(IfcActionSourceTypeEnum, 'IMPULSE', INDETERMINATE)
impact = getattr(IfcActionSourceTypeEnum, 'IMPACT', INDETERMINATE)
transport = getattr(IfcActionSourceTypeEnum, 'TRANSPORT', INDETERMINATE)
erection = getattr(IfcActionSourceTypeEnum, 'ERECTION', INDETERMINATE)
propping = getattr(IfcActionSourceTypeEnum, 'PROPPING', INDETERMINATE)
system_imperfection = getattr(IfcActionSourceTypeEnum, 'SYSTEM_IMPERFECTION', INDETERMINATE)
shrinkage = getattr(IfcActionSourceTypeEnum, 'SHRINKAGE', INDETERMINATE)
creep = getattr(IfcActionSourceTypeEnum, 'CREEP', INDETERMINATE)
lack_of_fit = getattr(IfcActionSourceTypeEnum, 'LACK_OF_FIT', INDETERMINATE)
buoyancy = getattr(IfcActionSourceTypeEnum, 'BUOYANCY', INDETERMINATE)
ice = getattr(IfcActionSourceTypeEnum, 'ICE', INDETERMINATE)
current = getattr(IfcActionSourceTypeEnum, 'CURRENT', INDETERMINATE)
wave = getattr(IfcActionSourceTypeEnum, 'WAVE', INDETERMINATE)
rain = getattr(IfcActionSourceTypeEnum, 'RAIN', INDETERMINATE)
brakes = getattr(IfcActionSourceTypeEnum, 'BRAKES', INDETERMINATE)
userdefined = getattr(IfcActionSourceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcActionSourceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcActionTypeEnum = enum_namespace()
permanent_g = getattr(IfcActionTypeEnum, 'PERMANENT_G', INDETERMINATE)
variable_q = getattr(IfcActionTypeEnum, 'VARIABLE_Q', INDETERMINATE)
extraordinary_a = getattr(IfcActionTypeEnum, 'EXTRAORDINARY_A', INDETERMINATE)
userdefined = getattr(IfcActionTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcActionTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcActuatorTypeEnum = enum_namespace()
electricactuator = getattr(IfcActuatorTypeEnum, 'ELECTRICACTUATOR', INDETERMINATE)
handoperatedactuator = getattr(IfcActuatorTypeEnum, 'HANDOPERATEDACTUATOR', INDETERMINATE)
hydraulicactuator = getattr(IfcActuatorTypeEnum, 'HYDRAULICACTUATOR', INDETERMINATE)
pneumaticactuator = getattr(IfcActuatorTypeEnum, 'PNEUMATICACTUATOR', INDETERMINATE)
thermostaticactuator = getattr(IfcActuatorTypeEnum, 'THERMOSTATICACTUATOR', INDETERMINATE)
userdefined = getattr(IfcActuatorTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcActuatorTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcAddressTypeEnum = enum_namespace()
office = getattr(IfcAddressTypeEnum, 'OFFICE', INDETERMINATE)
site = getattr(IfcAddressTypeEnum, 'SITE', INDETERMINATE)
home = getattr(IfcAddressTypeEnum, 'HOME', INDETERMINATE)
distributionpoint = getattr(IfcAddressTypeEnum, 'DISTRIBUTIONPOINT', INDETERMINATE)
userdefined = getattr(IfcAddressTypeEnum, 'USERDEFINED', INDETERMINATE)
IfcAirTerminalBoxTypeEnum = enum_namespace()
constantflow = getattr(IfcAirTerminalBoxTypeEnum, 'CONSTANTFLOW', INDETERMINATE)
variableflowpressuredependant = getattr(IfcAirTerminalBoxTypeEnum, 'VARIABLEFLOWPRESSUREDEPENDANT', INDETERMINATE)
variableflowpressureindependant = getattr(IfcAirTerminalBoxTypeEnum, 'VARIABLEFLOWPRESSUREINDEPENDANT', INDETERMINATE)
userdefined = getattr(IfcAirTerminalBoxTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcAirTerminalBoxTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcAirTerminalTypeEnum = enum_namespace()
diffuser = getattr(IfcAirTerminalTypeEnum, 'DIFFUSER', INDETERMINATE)
grille = getattr(IfcAirTerminalTypeEnum, 'GRILLE', INDETERMINATE)
louvre = getattr(IfcAirTerminalTypeEnum, 'LOUVRE', INDETERMINATE)
register = getattr(IfcAirTerminalTypeEnum, 'REGISTER', INDETERMINATE)
userdefined = getattr(IfcAirTerminalTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcAirTerminalTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcAirToAirHeatRecoveryTypeEnum = enum_namespace()
fixedplatecounterflowexchanger = getattr(IfcAirToAirHeatRecoveryTypeEnum, 'FIXEDPLATECOUNTERFLOWEXCHANGER', INDETERMINATE)
fixedplatecrossflowexchanger = getattr(IfcAirToAirHeatRecoveryTypeEnum, 'FIXEDPLATECROSSFLOWEXCHANGER', INDETERMINATE)
fixedplateparallelflowexchanger = getattr(IfcAirToAirHeatRecoveryTypeEnum, 'FIXEDPLATEPARALLELFLOWEXCHANGER', INDETERMINATE)
rotarywheel = getattr(IfcAirToAirHeatRecoveryTypeEnum, 'ROTARYWHEEL', INDETERMINATE)
runaroundcoilloop = getattr(IfcAirToAirHeatRecoveryTypeEnum, 'RUNAROUNDCOILLOOP', INDETERMINATE)
heatpipe = getattr(IfcAirToAirHeatRecoveryTypeEnum, 'HEATPIPE', INDETERMINATE)
twintowerenthalpyrecoveryloops = getattr(IfcAirToAirHeatRecoveryTypeEnum, 'TWINTOWERENTHALPYRECOVERYLOOPS', INDETERMINATE)
thermosiphonsealedtubeheatexchangers = getattr(IfcAirToAirHeatRecoveryTypeEnum, 'THERMOSIPHONSEALEDTUBEHEATEXCHANGERS', INDETERMINATE)
thermosiphoncoiltypeheatexchangers = getattr(IfcAirToAirHeatRecoveryTypeEnum, 'THERMOSIPHONCOILTYPEHEATEXCHANGERS', INDETERMINATE)
userdefined = getattr(IfcAirToAirHeatRecoveryTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcAirToAirHeatRecoveryTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcAlarmTypeEnum = enum_namespace()
bell = getattr(IfcAlarmTypeEnum, 'BELL', INDETERMINATE)
breakglassbutton = getattr(IfcAlarmTypeEnum, 'BREAKGLASSBUTTON', INDETERMINATE)
light = getattr(IfcAlarmTypeEnum, 'LIGHT', INDETERMINATE)
manualpullbox = getattr(IfcAlarmTypeEnum, 'MANUALPULLBOX', INDETERMINATE)
siren = getattr(IfcAlarmTypeEnum, 'SIREN', INDETERMINATE)
whistle = getattr(IfcAlarmTypeEnum, 'WHISTLE', INDETERMINATE)
userdefined = getattr(IfcAlarmTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcAlarmTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcAlignmentTypeEnum = enum_namespace()
userdefined = getattr(IfcAlignmentTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcAlignmentTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcAnalysisModelTypeEnum = enum_namespace()
in_plane_loading_2d = getattr(IfcAnalysisModelTypeEnum, 'IN_PLANE_LOADING_2D', INDETERMINATE)
out_plane_loading_2d = getattr(IfcAnalysisModelTypeEnum, 'OUT_PLANE_LOADING_2D', INDETERMINATE)
loading_3d = getattr(IfcAnalysisModelTypeEnum, 'LOADING_3D', INDETERMINATE)
userdefined = getattr(IfcAnalysisModelTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcAnalysisModelTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcAnalysisTheoryTypeEnum = enum_namespace()
first_order_theory = getattr(IfcAnalysisTheoryTypeEnum, 'FIRST_ORDER_THEORY', INDETERMINATE)
second_order_theory = getattr(IfcAnalysisTheoryTypeEnum, 'SECOND_ORDER_THEORY', INDETERMINATE)
third_order_theory = getattr(IfcAnalysisTheoryTypeEnum, 'THIRD_ORDER_THEORY', INDETERMINATE)
full_nonlinear_theory = getattr(IfcAnalysisTheoryTypeEnum, 'FULL_NONLINEAR_THEORY', INDETERMINATE)
userdefined = getattr(IfcAnalysisTheoryTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcAnalysisTheoryTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcArithmeticOperatorEnum = enum_namespace()
add = getattr(IfcArithmeticOperatorEnum, 'ADD', INDETERMINATE)
divide = getattr(IfcArithmeticOperatorEnum, 'DIVIDE', INDETERMINATE)
multiply = getattr(IfcArithmeticOperatorEnum, 'MULTIPLY', INDETERMINATE)
subtract = getattr(IfcArithmeticOperatorEnum, 'SUBTRACT', INDETERMINATE)
IfcAssemblyPlaceEnum = enum_namespace()
site = getattr(IfcAssemblyPlaceEnum, 'SITE', INDETERMINATE)
factory = getattr(IfcAssemblyPlaceEnum, 'FACTORY', INDETERMINATE)
notdefined = getattr(IfcAssemblyPlaceEnum, 'NOTDEFINED', INDETERMINATE)
IfcAudioVisualApplianceTypeEnum = enum_namespace()
amplifier = getattr(IfcAudioVisualApplianceTypeEnum, 'AMPLIFIER', INDETERMINATE)
camera = getattr(IfcAudioVisualApplianceTypeEnum, 'CAMERA', INDETERMINATE)
display = getattr(IfcAudioVisualApplianceTypeEnum, 'DISPLAY', INDETERMINATE)
microphone = getattr(IfcAudioVisualApplianceTypeEnum, 'MICROPHONE', INDETERMINATE)
player = getattr(IfcAudioVisualApplianceTypeEnum, 'PLAYER', INDETERMINATE)
projector = getattr(IfcAudioVisualApplianceTypeEnum, 'PROJECTOR', INDETERMINATE)
receiver = getattr(IfcAudioVisualApplianceTypeEnum, 'RECEIVER', INDETERMINATE)
speaker = getattr(IfcAudioVisualApplianceTypeEnum, 'SPEAKER', INDETERMINATE)
switcher = getattr(IfcAudioVisualApplianceTypeEnum, 'SWITCHER', INDETERMINATE)
telephone = getattr(IfcAudioVisualApplianceTypeEnum, 'TELEPHONE', INDETERMINATE)
tuner = getattr(IfcAudioVisualApplianceTypeEnum, 'TUNER', INDETERMINATE)
userdefined = getattr(IfcAudioVisualApplianceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcAudioVisualApplianceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcBSplineCurveForm = enum_namespace()
polyline_form = getattr(IfcBSplineCurveForm, 'POLYLINE_FORM', INDETERMINATE)
circular_arc = getattr(IfcBSplineCurveForm, 'CIRCULAR_ARC', INDETERMINATE)
elliptic_arc = getattr(IfcBSplineCurveForm, 'ELLIPTIC_ARC', INDETERMINATE)
parabolic_arc = getattr(IfcBSplineCurveForm, 'PARABOLIC_ARC', INDETERMINATE)
hyperbolic_arc = getattr(IfcBSplineCurveForm, 'HYPERBOLIC_ARC', INDETERMINATE)
unspecified = getattr(IfcBSplineCurveForm, 'UNSPECIFIED', INDETERMINATE)
IfcBSplineSurfaceForm = enum_namespace()
plane_surf = getattr(IfcBSplineSurfaceForm, 'PLANE_SURF', INDETERMINATE)
cylindrical_surf = getattr(IfcBSplineSurfaceForm, 'CYLINDRICAL_SURF', INDETERMINATE)
conical_surf = getattr(IfcBSplineSurfaceForm, 'CONICAL_SURF', INDETERMINATE)
spherical_surf = getattr(IfcBSplineSurfaceForm, 'SPHERICAL_SURF', INDETERMINATE)
toroidal_surf = getattr(IfcBSplineSurfaceForm, 'TOROIDAL_SURF', INDETERMINATE)
surf_of_revolution = getattr(IfcBSplineSurfaceForm, 'SURF_OF_REVOLUTION', INDETERMINATE)
ruled_surf = getattr(IfcBSplineSurfaceForm, 'RULED_SURF', INDETERMINATE)
generalised_cone = getattr(IfcBSplineSurfaceForm, 'GENERALISED_CONE', INDETERMINATE)
quadric_surf = getattr(IfcBSplineSurfaceForm, 'QUADRIC_SURF', INDETERMINATE)
surf_of_linear_extrusion = getattr(IfcBSplineSurfaceForm, 'SURF_OF_LINEAR_EXTRUSION', INDETERMINATE)
unspecified = getattr(IfcBSplineSurfaceForm, 'UNSPECIFIED', INDETERMINATE)
IfcBeamTypeEnum = enum_namespace()
beam = getattr(IfcBeamTypeEnum, 'BEAM', INDETERMINATE)
joist = getattr(IfcBeamTypeEnum, 'JOIST', INDETERMINATE)
hollowcore = getattr(IfcBeamTypeEnum, 'HOLLOWCORE', INDETERMINATE)
lintel = getattr(IfcBeamTypeEnum, 'LINTEL', INDETERMINATE)
spandrel = getattr(IfcBeamTypeEnum, 'SPANDREL', INDETERMINATE)
t_beam = getattr(IfcBeamTypeEnum, 'T_BEAM', INDETERMINATE)
userdefined = getattr(IfcBeamTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcBeamTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcBenchmarkEnum = enum_namespace()
greaterthan = getattr(IfcBenchmarkEnum, 'GREATERTHAN', INDETERMINATE)
greaterthanorequalto = getattr(IfcBenchmarkEnum, 'GREATERTHANOREQUALTO', INDETERMINATE)
lessthan = getattr(IfcBenchmarkEnum, 'LESSTHAN', INDETERMINATE)
lessthanorequalto = getattr(IfcBenchmarkEnum, 'LESSTHANOREQUALTO', INDETERMINATE)
equalto = getattr(IfcBenchmarkEnum, 'EQUALTO', INDETERMINATE)
notequalto = getattr(IfcBenchmarkEnum, 'NOTEQUALTO', INDETERMINATE)
includes = getattr(IfcBenchmarkEnum, 'INCLUDES', INDETERMINATE)
notincludes = getattr(IfcBenchmarkEnum, 'NOTINCLUDES', INDETERMINATE)
includedin = getattr(IfcBenchmarkEnum, 'INCLUDEDIN', INDETERMINATE)
notincludedin = getattr(IfcBenchmarkEnum, 'NOTINCLUDEDIN', INDETERMINATE)
IfcBoilerTypeEnum = enum_namespace()
water = getattr(IfcBoilerTypeEnum, 'WATER', INDETERMINATE)
steam = getattr(IfcBoilerTypeEnum, 'STEAM', INDETERMINATE)
userdefined = getattr(IfcBoilerTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcBoilerTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcBooleanOperator = enum_namespace()
union = getattr(IfcBooleanOperator, 'UNION', INDETERMINATE)
intersection = getattr(IfcBooleanOperator, 'INTERSECTION', INDETERMINATE)
difference = getattr(IfcBooleanOperator, 'DIFFERENCE', INDETERMINATE)
IfcBuildingElementPartTypeEnum = enum_namespace()
insulation = getattr(IfcBuildingElementPartTypeEnum, 'INSULATION', INDETERMINATE)
precastpanel = getattr(IfcBuildingElementPartTypeEnum, 'PRECASTPANEL', INDETERMINATE)
userdefined = getattr(IfcBuildingElementPartTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcBuildingElementPartTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcBuildingElementProxyTypeEnum = enum_namespace()
complex = getattr(IfcBuildingElementProxyTypeEnum, 'COMPLEX', INDETERMINATE)
element = getattr(IfcBuildingElementProxyTypeEnum, 'ELEMENT', INDETERMINATE)
partial = getattr(IfcBuildingElementProxyTypeEnum, 'PARTIAL', INDETERMINATE)
provisionforvoid = getattr(IfcBuildingElementProxyTypeEnum, 'PROVISIONFORVOID', INDETERMINATE)
provisionforspace = getattr(IfcBuildingElementProxyTypeEnum, 'PROVISIONFORSPACE', INDETERMINATE)
userdefined = getattr(IfcBuildingElementProxyTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcBuildingElementProxyTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcBuildingSystemTypeEnum = enum_namespace()
fenestration = getattr(IfcBuildingSystemTypeEnum, 'FENESTRATION', INDETERMINATE)
foundation = getattr(IfcBuildingSystemTypeEnum, 'FOUNDATION', INDETERMINATE)
loadbearing = getattr(IfcBuildingSystemTypeEnum, 'LOADBEARING', INDETERMINATE)
outershell = getattr(IfcBuildingSystemTypeEnum, 'OUTERSHELL', INDETERMINATE)
shading = getattr(IfcBuildingSystemTypeEnum, 'SHADING', INDETERMINATE)
transport = getattr(IfcBuildingSystemTypeEnum, 'TRANSPORT', INDETERMINATE)
userdefined = getattr(IfcBuildingSystemTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcBuildingSystemTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcBurnerTypeEnum = enum_namespace()
userdefined = getattr(IfcBurnerTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcBurnerTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCableCarrierFittingTypeEnum = enum_namespace()
bend = getattr(IfcCableCarrierFittingTypeEnum, 'BEND', INDETERMINATE)
cross = getattr(IfcCableCarrierFittingTypeEnum, 'CROSS', INDETERMINATE)
reducer = getattr(IfcCableCarrierFittingTypeEnum, 'REDUCER', INDETERMINATE)
tee = getattr(IfcCableCarrierFittingTypeEnum, 'TEE', INDETERMINATE)
userdefined = getattr(IfcCableCarrierFittingTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcCableCarrierFittingTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCableCarrierSegmentTypeEnum = enum_namespace()
cableladdersegment = getattr(IfcCableCarrierSegmentTypeEnum, 'CABLELADDERSEGMENT', INDETERMINATE)
cabletraysegment = getattr(IfcCableCarrierSegmentTypeEnum, 'CABLETRAYSEGMENT', INDETERMINATE)
cabletrunkingsegment = getattr(IfcCableCarrierSegmentTypeEnum, 'CABLETRUNKINGSEGMENT', INDETERMINATE)
conduitsegment = getattr(IfcCableCarrierSegmentTypeEnum, 'CONDUITSEGMENT', INDETERMINATE)
userdefined = getattr(IfcCableCarrierSegmentTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcCableCarrierSegmentTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCableFittingTypeEnum = enum_namespace()
connector = getattr(IfcCableFittingTypeEnum, 'CONNECTOR', INDETERMINATE)
entry = getattr(IfcCableFittingTypeEnum, 'ENTRY', INDETERMINATE)
exit = getattr(IfcCableFittingTypeEnum, 'EXIT', INDETERMINATE)
junction = getattr(IfcCableFittingTypeEnum, 'JUNCTION', INDETERMINATE)
transition = getattr(IfcCableFittingTypeEnum, 'TRANSITION', INDETERMINATE)
userdefined = getattr(IfcCableFittingTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcCableFittingTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCableSegmentTypeEnum = enum_namespace()
busbarsegment = getattr(IfcCableSegmentTypeEnum, 'BUSBARSEGMENT', INDETERMINATE)
cablesegment = getattr(IfcCableSegmentTypeEnum, 'CABLESEGMENT', INDETERMINATE)
conductorsegment = getattr(IfcCableSegmentTypeEnum, 'CONDUCTORSEGMENT', INDETERMINATE)
coresegment = getattr(IfcCableSegmentTypeEnum, 'CORESEGMENT', INDETERMINATE)
userdefined = getattr(IfcCableSegmentTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcCableSegmentTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcChangeActionEnum = enum_namespace()
nochange = getattr(IfcChangeActionEnum, 'NOCHANGE', INDETERMINATE)
modified = getattr(IfcChangeActionEnum, 'MODIFIED', INDETERMINATE)
added = getattr(IfcChangeActionEnum, 'ADDED', INDETERMINATE)
deleted = getattr(IfcChangeActionEnum, 'DELETED', INDETERMINATE)
notdefined = getattr(IfcChangeActionEnum, 'NOTDEFINED', INDETERMINATE)
IfcChillerTypeEnum = enum_namespace()
aircooled = getattr(IfcChillerTypeEnum, 'AIRCOOLED', INDETERMINATE)
watercooled = getattr(IfcChillerTypeEnum, 'WATERCOOLED', INDETERMINATE)
heatrecovery = getattr(IfcChillerTypeEnum, 'HEATRECOVERY', INDETERMINATE)
userdefined = getattr(IfcChillerTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcChillerTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcChimneyTypeEnum = enum_namespace()
userdefined = getattr(IfcChimneyTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcChimneyTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCoilTypeEnum = enum_namespace()
dxcoolingcoil = getattr(IfcCoilTypeEnum, 'DXCOOLINGCOIL', INDETERMINATE)
electricheatingcoil = getattr(IfcCoilTypeEnum, 'ELECTRICHEATINGCOIL', INDETERMINATE)
gasheatingcoil = getattr(IfcCoilTypeEnum, 'GASHEATINGCOIL', INDETERMINATE)
hydroniccoil = getattr(IfcCoilTypeEnum, 'HYDRONICCOIL', INDETERMINATE)
steamheatingcoil = getattr(IfcCoilTypeEnum, 'STEAMHEATINGCOIL', INDETERMINATE)
watercoolingcoil = getattr(IfcCoilTypeEnum, 'WATERCOOLINGCOIL', INDETERMINATE)
waterheatingcoil = getattr(IfcCoilTypeEnum, 'WATERHEATINGCOIL', INDETERMINATE)
userdefined = getattr(IfcCoilTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcCoilTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcColumnTypeEnum = enum_namespace()
column = getattr(IfcColumnTypeEnum, 'COLUMN', INDETERMINATE)
pilaster = getattr(IfcColumnTypeEnum, 'PILASTER', INDETERMINATE)
userdefined = getattr(IfcColumnTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcColumnTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCommunicationsApplianceTypeEnum = enum_namespace()
antenna = getattr(IfcCommunicationsApplianceTypeEnum, 'ANTENNA', INDETERMINATE)
computer = getattr(IfcCommunicationsApplianceTypeEnum, 'COMPUTER', INDETERMINATE)
fax = getattr(IfcCommunicationsApplianceTypeEnum, 'FAX', INDETERMINATE)
gateway = getattr(IfcCommunicationsApplianceTypeEnum, 'GATEWAY', INDETERMINATE)
modem = getattr(IfcCommunicationsApplianceTypeEnum, 'MODEM', INDETERMINATE)
networkappliance = getattr(IfcCommunicationsApplianceTypeEnum, 'NETWORKAPPLIANCE', INDETERMINATE)
networkbridge = getattr(IfcCommunicationsApplianceTypeEnum, 'NETWORKBRIDGE', INDETERMINATE)
networkhub = getattr(IfcCommunicationsApplianceTypeEnum, 'NETWORKHUB', INDETERMINATE)
printer = getattr(IfcCommunicationsApplianceTypeEnum, 'PRINTER', INDETERMINATE)
repeater = getattr(IfcCommunicationsApplianceTypeEnum, 'REPEATER', INDETERMINATE)
router = getattr(IfcCommunicationsApplianceTypeEnum, 'ROUTER', INDETERMINATE)
scanner = getattr(IfcCommunicationsApplianceTypeEnum, 'SCANNER', INDETERMINATE)
userdefined = getattr(IfcCommunicationsApplianceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcCommunicationsApplianceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcComplexPropertyTemplateTypeEnum = enum_namespace()
p_complex = getattr(IfcComplexPropertyTemplateTypeEnum, 'P_COMPLEX', INDETERMINATE)
q_complex = getattr(IfcComplexPropertyTemplateTypeEnum, 'Q_COMPLEX', INDETERMINATE)
IfcCompressorTypeEnum = enum_namespace()
dynamic = getattr(IfcCompressorTypeEnum, 'DYNAMIC', INDETERMINATE)
reciprocating = getattr(IfcCompressorTypeEnum, 'RECIPROCATING', INDETERMINATE)
rotary = getattr(IfcCompressorTypeEnum, 'ROTARY', INDETERMINATE)
scroll = getattr(IfcCompressorTypeEnum, 'SCROLL', INDETERMINATE)
trochoidal = getattr(IfcCompressorTypeEnum, 'TROCHOIDAL', INDETERMINATE)
singlestage = getattr(IfcCompressorTypeEnum, 'SINGLESTAGE', INDETERMINATE)
booster = getattr(IfcCompressorTypeEnum, 'BOOSTER', INDETERMINATE)
opentype = getattr(IfcCompressorTypeEnum, 'OPENTYPE', INDETERMINATE)
hermetic = getattr(IfcCompressorTypeEnum, 'HERMETIC', INDETERMINATE)
semihermetic = getattr(IfcCompressorTypeEnum, 'SEMIHERMETIC', INDETERMINATE)
weldedshellhermetic = getattr(IfcCompressorTypeEnum, 'WELDEDSHELLHERMETIC', INDETERMINATE)
rollingpiston = getattr(IfcCompressorTypeEnum, 'ROLLINGPISTON', INDETERMINATE)
rotaryvane = getattr(IfcCompressorTypeEnum, 'ROTARYVANE', INDETERMINATE)
singlescrew = getattr(IfcCompressorTypeEnum, 'SINGLESCREW', INDETERMINATE)
twinscrew = getattr(IfcCompressorTypeEnum, 'TWINSCREW', INDETERMINATE)
userdefined = getattr(IfcCompressorTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcCompressorTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCondenserTypeEnum = enum_namespace()
aircooled = getattr(IfcCondenserTypeEnum, 'AIRCOOLED', INDETERMINATE)
evaporativecooled = getattr(IfcCondenserTypeEnum, 'EVAPORATIVECOOLED', INDETERMINATE)
watercooled = getattr(IfcCondenserTypeEnum, 'WATERCOOLED', INDETERMINATE)
watercooledbrazedplate = getattr(IfcCondenserTypeEnum, 'WATERCOOLEDBRAZEDPLATE', INDETERMINATE)
watercooledshellcoil = getattr(IfcCondenserTypeEnum, 'WATERCOOLEDSHELLCOIL', INDETERMINATE)
watercooledshelltube = getattr(IfcCondenserTypeEnum, 'WATERCOOLEDSHELLTUBE', INDETERMINATE)
watercooledtubeintube = getattr(IfcCondenserTypeEnum, 'WATERCOOLEDTUBEINTUBE', INDETERMINATE)
userdefined = getattr(IfcCondenserTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcCondenserTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcConnectionTypeEnum = enum_namespace()
atpath = getattr(IfcConnectionTypeEnum, 'ATPATH', INDETERMINATE)
atstart = getattr(IfcConnectionTypeEnum, 'ATSTART', INDETERMINATE)
atend = getattr(IfcConnectionTypeEnum, 'ATEND', INDETERMINATE)
notdefined = getattr(IfcConnectionTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcConstraintEnum = enum_namespace()
hard = getattr(IfcConstraintEnum, 'HARD', INDETERMINATE)
soft = getattr(IfcConstraintEnum, 'SOFT', INDETERMINATE)
advisory = getattr(IfcConstraintEnum, 'ADVISORY', INDETERMINATE)
userdefined = getattr(IfcConstraintEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcConstraintEnum, 'NOTDEFINED', INDETERMINATE)
IfcConstructionEquipmentResourceTypeEnum = enum_namespace()
demolishing = getattr(IfcConstructionEquipmentResourceTypeEnum, 'DEMOLISHING', INDETERMINATE)
earthmoving = getattr(IfcConstructionEquipmentResourceTypeEnum, 'EARTHMOVING', INDETERMINATE)
erecting = getattr(IfcConstructionEquipmentResourceTypeEnum, 'ERECTING', INDETERMINATE)
heating = getattr(IfcConstructionEquipmentResourceTypeEnum, 'HEATING', INDETERMINATE)
lighting = getattr(IfcConstructionEquipmentResourceTypeEnum, 'LIGHTING', INDETERMINATE)
paving = getattr(IfcConstructionEquipmentResourceTypeEnum, 'PAVING', INDETERMINATE)
pumping = getattr(IfcConstructionEquipmentResourceTypeEnum, 'PUMPING', INDETERMINATE)
transporting = getattr(IfcConstructionEquipmentResourceTypeEnum, 'TRANSPORTING', INDETERMINATE)
userdefined = getattr(IfcConstructionEquipmentResourceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcConstructionEquipmentResourceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcConstructionMaterialResourceTypeEnum = enum_namespace()
aggregates = getattr(IfcConstructionMaterialResourceTypeEnum, 'AGGREGATES', INDETERMINATE)
concrete = getattr(IfcConstructionMaterialResourceTypeEnum, 'CONCRETE', INDETERMINATE)
drywall = getattr(IfcConstructionMaterialResourceTypeEnum, 'DRYWALL', INDETERMINATE)
fuel = getattr(IfcConstructionMaterialResourceTypeEnum, 'FUEL', INDETERMINATE)
gypsum = getattr(IfcConstructionMaterialResourceTypeEnum, 'GYPSUM', INDETERMINATE)
masonry = getattr(IfcConstructionMaterialResourceTypeEnum, 'MASONRY', INDETERMINATE)
metal = getattr(IfcConstructionMaterialResourceTypeEnum, 'METAL', INDETERMINATE)
plastic = getattr(IfcConstructionMaterialResourceTypeEnum, 'PLASTIC', INDETERMINATE)
wood = getattr(IfcConstructionMaterialResourceTypeEnum, 'WOOD', INDETERMINATE)
notdefined = getattr(IfcConstructionMaterialResourceTypeEnum, 'NOTDEFINED', INDETERMINATE)
userdefined = getattr(IfcConstructionMaterialResourceTypeEnum, 'USERDEFINED', INDETERMINATE)
IfcConstructionProductResourceTypeEnum = enum_namespace()
assembly = getattr(IfcConstructionProductResourceTypeEnum, 'ASSEMBLY', INDETERMINATE)
formwork = getattr(IfcConstructionProductResourceTypeEnum, 'FORMWORK', INDETERMINATE)
userdefined = getattr(IfcConstructionProductResourceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcConstructionProductResourceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcControllerTypeEnum = enum_namespace()
floating = getattr(IfcControllerTypeEnum, 'FLOATING', INDETERMINATE)
programmable = getattr(IfcControllerTypeEnum, 'PROGRAMMABLE', INDETERMINATE)
proportional = getattr(IfcControllerTypeEnum, 'PROPORTIONAL', INDETERMINATE)
multiposition = getattr(IfcControllerTypeEnum, 'MULTIPOSITION', INDETERMINATE)
twoposition = getattr(IfcControllerTypeEnum, 'TWOPOSITION', INDETERMINATE)
userdefined = getattr(IfcControllerTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcControllerTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCooledBeamTypeEnum = enum_namespace()
active = getattr(IfcCooledBeamTypeEnum, 'ACTIVE', INDETERMINATE)
passive = getattr(IfcCooledBeamTypeEnum, 'PASSIVE', INDETERMINATE)
userdefined = getattr(IfcCooledBeamTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcCooledBeamTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCoolingTowerTypeEnum = enum_namespace()
naturaldraft = getattr(IfcCoolingTowerTypeEnum, 'NATURALDRAFT', INDETERMINATE)
mechanicalinduceddraft = getattr(IfcCoolingTowerTypeEnum, 'MECHANICALINDUCEDDRAFT', INDETERMINATE)
mechanicalforceddraft = getattr(IfcCoolingTowerTypeEnum, 'MECHANICALFORCEDDRAFT', INDETERMINATE)
userdefined = getattr(IfcCoolingTowerTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcCoolingTowerTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCostItemTypeEnum = enum_namespace()
userdefined = getattr(IfcCostItemTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcCostItemTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCostScheduleTypeEnum = enum_namespace()
budget = getattr(IfcCostScheduleTypeEnum, 'BUDGET', INDETERMINATE)
costplan = getattr(IfcCostScheduleTypeEnum, 'COSTPLAN', INDETERMINATE)
estimate = getattr(IfcCostScheduleTypeEnum, 'ESTIMATE', INDETERMINATE)
tender = getattr(IfcCostScheduleTypeEnum, 'TENDER', INDETERMINATE)
pricedbillofquantities = getattr(IfcCostScheduleTypeEnum, 'PRICEDBILLOFQUANTITIES', INDETERMINATE)
unpricedbillofquantities = getattr(IfcCostScheduleTypeEnum, 'UNPRICEDBILLOFQUANTITIES', INDETERMINATE)
scheduleofrates = getattr(IfcCostScheduleTypeEnum, 'SCHEDULEOFRATES', INDETERMINATE)
userdefined = getattr(IfcCostScheduleTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcCostScheduleTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCoveringTypeEnum = enum_namespace()
ceiling = getattr(IfcCoveringTypeEnum, 'CEILING', INDETERMINATE)
flooring = getattr(IfcCoveringTypeEnum, 'FLOORING', INDETERMINATE)
cladding = getattr(IfcCoveringTypeEnum, 'CLADDING', INDETERMINATE)
roofing = getattr(IfcCoveringTypeEnum, 'ROOFING', INDETERMINATE)
molding = getattr(IfcCoveringTypeEnum, 'MOLDING', INDETERMINATE)
skirtingboard = getattr(IfcCoveringTypeEnum, 'SKIRTINGBOARD', INDETERMINATE)
insulation = getattr(IfcCoveringTypeEnum, 'INSULATION', INDETERMINATE)
membrane = getattr(IfcCoveringTypeEnum, 'MEMBRANE', INDETERMINATE)
sleeving = getattr(IfcCoveringTypeEnum, 'SLEEVING', INDETERMINATE)
wrapping = getattr(IfcCoveringTypeEnum, 'WRAPPING', INDETERMINATE)
userdefined = getattr(IfcCoveringTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcCoveringTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCrewResourceTypeEnum = enum_namespace()
office = getattr(IfcCrewResourceTypeEnum, 'OFFICE', INDETERMINATE)
site = getattr(IfcCrewResourceTypeEnum, 'SITE', INDETERMINATE)
userdefined = getattr(IfcCrewResourceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcCrewResourceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCurtainWallTypeEnum = enum_namespace()
userdefined = getattr(IfcCurtainWallTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcCurtainWallTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCurveInterpolationEnum = enum_namespace()
linear = getattr(IfcCurveInterpolationEnum, 'LINEAR', INDETERMINATE)
log_linear = getattr(IfcCurveInterpolationEnum, 'LOG_LINEAR', INDETERMINATE)
log_log = getattr(IfcCurveInterpolationEnum, 'LOG_LOG', INDETERMINATE)
notdefined = getattr(IfcCurveInterpolationEnum, 'NOTDEFINED', INDETERMINATE)
IfcDamperTypeEnum = enum_namespace()
backdraftdamper = getattr(IfcDamperTypeEnum, 'BACKDRAFTDAMPER', INDETERMINATE)
balancingdamper = getattr(IfcDamperTypeEnum, 'BALANCINGDAMPER', INDETERMINATE)
blastdamper = getattr(IfcDamperTypeEnum, 'BLASTDAMPER', INDETERMINATE)
controldamper = getattr(IfcDamperTypeEnum, 'CONTROLDAMPER', INDETERMINATE)
firedamper = getattr(IfcDamperTypeEnum, 'FIREDAMPER', INDETERMINATE)
firesmokedamper = getattr(IfcDamperTypeEnum, 'FIRESMOKEDAMPER', INDETERMINATE)
fumehoodexhaust = getattr(IfcDamperTypeEnum, 'FUMEHOODEXHAUST', INDETERMINATE)
gravitydamper = getattr(IfcDamperTypeEnum, 'GRAVITYDAMPER', INDETERMINATE)
gravityreliefdamper = getattr(IfcDamperTypeEnum, 'GRAVITYRELIEFDAMPER', INDETERMINATE)
reliefdamper = getattr(IfcDamperTypeEnum, 'RELIEFDAMPER', INDETERMINATE)
smokedamper = getattr(IfcDamperTypeEnum, 'SMOKEDAMPER', INDETERMINATE)
userdefined = getattr(IfcDamperTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcDamperTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcDataOriginEnum = enum_namespace()
measured = getattr(IfcDataOriginEnum, 'MEASURED', INDETERMINATE)
predicted = getattr(IfcDataOriginEnum, 'PREDICTED', INDETERMINATE)
simulated = getattr(IfcDataOriginEnum, 'SIMULATED', INDETERMINATE)
userdefined = getattr(IfcDataOriginEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcDataOriginEnum, 'NOTDEFINED', INDETERMINATE)
IfcDerivedUnitEnum = enum_namespace()
angularvelocityunit = getattr(IfcDerivedUnitEnum, 'ANGULARVELOCITYUNIT', INDETERMINATE)
areadensityunit = getattr(IfcDerivedUnitEnum, 'AREADENSITYUNIT', INDETERMINATE)
compoundplaneangleunit = getattr(IfcDerivedUnitEnum, 'COMPOUNDPLANEANGLEUNIT', INDETERMINATE)
dynamicviscosityunit = getattr(IfcDerivedUnitEnum, 'DYNAMICVISCOSITYUNIT', INDETERMINATE)
heatfluxdensityunit = getattr(IfcDerivedUnitEnum, 'HEATFLUXDENSITYUNIT', INDETERMINATE)
integercountrateunit = getattr(IfcDerivedUnitEnum, 'INTEGERCOUNTRATEUNIT', INDETERMINATE)
isothermalmoisturecapacityunit = getattr(IfcDerivedUnitEnum, 'ISOTHERMALMOISTURECAPACITYUNIT', INDETERMINATE)
kinematicviscosityunit = getattr(IfcDerivedUnitEnum, 'KINEMATICVISCOSITYUNIT', INDETERMINATE)
linearvelocityunit = getattr(IfcDerivedUnitEnum, 'LINEARVELOCITYUNIT', INDETERMINATE)
massdensityunit = getattr(IfcDerivedUnitEnum, 'MASSDENSITYUNIT', INDETERMINATE)
massflowrateunit = getattr(IfcDerivedUnitEnum, 'MASSFLOWRATEUNIT', INDETERMINATE)
moisturediffusivityunit = getattr(IfcDerivedUnitEnum, 'MOISTUREDIFFUSIVITYUNIT', INDETERMINATE)
molecularweightunit = getattr(IfcDerivedUnitEnum, 'MOLECULARWEIGHTUNIT', INDETERMINATE)
specificheatcapacityunit = getattr(IfcDerivedUnitEnum, 'SPECIFICHEATCAPACITYUNIT', INDETERMINATE)
thermaladmittanceunit = getattr(IfcDerivedUnitEnum, 'THERMALADMITTANCEUNIT', INDETERMINATE)
thermalconductanceunit = getattr(IfcDerivedUnitEnum, 'THERMALCONDUCTANCEUNIT', INDETERMINATE)
thermalresistanceunit = getattr(IfcDerivedUnitEnum, 'THERMALRESISTANCEUNIT', INDETERMINATE)
thermaltransmittanceunit = getattr(IfcDerivedUnitEnum, 'THERMALTRANSMITTANCEUNIT', INDETERMINATE)
vaporpermeabilityunit = getattr(IfcDerivedUnitEnum, 'VAPORPERMEABILITYUNIT', INDETERMINATE)
volumetricflowrateunit = getattr(IfcDerivedUnitEnum, 'VOLUMETRICFLOWRATEUNIT', INDETERMINATE)
rotationalfrequencyunit = getattr(IfcDerivedUnitEnum, 'ROTATIONALFREQUENCYUNIT', INDETERMINATE)
torqueunit = getattr(IfcDerivedUnitEnum, 'TORQUEUNIT', INDETERMINATE)
momentofinertiaunit = getattr(IfcDerivedUnitEnum, 'MOMENTOFINERTIAUNIT', INDETERMINATE)
linearmomentunit = getattr(IfcDerivedUnitEnum, 'LINEARMOMENTUNIT', INDETERMINATE)
linearforceunit = getattr(IfcDerivedUnitEnum, 'LINEARFORCEUNIT', INDETERMINATE)
planarforceunit = getattr(IfcDerivedUnitEnum, 'PLANARFORCEUNIT', INDETERMINATE)
modulusofelasticityunit = getattr(IfcDerivedUnitEnum, 'MODULUSOFELASTICITYUNIT', INDETERMINATE)
shearmodulusunit = getattr(IfcDerivedUnitEnum, 'SHEARMODULUSUNIT', INDETERMINATE)
linearstiffnessunit = getattr(IfcDerivedUnitEnum, 'LINEARSTIFFNESSUNIT', INDETERMINATE)
rotationalstiffnessunit = getattr(IfcDerivedUnitEnum, 'ROTATIONALSTIFFNESSUNIT', INDETERMINATE)
modulusofsubgradereactionunit = getattr(IfcDerivedUnitEnum, 'MODULUSOFSUBGRADEREACTIONUNIT', INDETERMINATE)
accelerationunit = getattr(IfcDerivedUnitEnum, 'ACCELERATIONUNIT', INDETERMINATE)
curvatureunit = getattr(IfcDerivedUnitEnum, 'CURVATUREUNIT', INDETERMINATE)
heatingvalueunit = getattr(IfcDerivedUnitEnum, 'HEATINGVALUEUNIT', INDETERMINATE)
ionconcentrationunit = getattr(IfcDerivedUnitEnum, 'IONCONCENTRATIONUNIT', INDETERMINATE)
luminousintensitydistributionunit = getattr(IfcDerivedUnitEnum, 'LUMINOUSINTENSITYDISTRIBUTIONUNIT', INDETERMINATE)
massperlengthunit = getattr(IfcDerivedUnitEnum, 'MASSPERLENGTHUNIT', INDETERMINATE)
modulusoflinearsubgradereactionunit = getattr(IfcDerivedUnitEnum, 'MODULUSOFLINEARSUBGRADEREACTIONUNIT', INDETERMINATE)
modulusofrotationalsubgradereactionunit = getattr(IfcDerivedUnitEnum, 'MODULUSOFROTATIONALSUBGRADEREACTIONUNIT', INDETERMINATE)
phunit = getattr(IfcDerivedUnitEnum, 'PHUNIT', INDETERMINATE)
rotationalmassunit = getattr(IfcDerivedUnitEnum, 'ROTATIONALMASSUNIT', INDETERMINATE)
sectionareaintegralunit = getattr(IfcDerivedUnitEnum, 'SECTIONAREAINTEGRALUNIT', INDETERMINATE)
sectionmodulusunit = getattr(IfcDerivedUnitEnum, 'SECTIONMODULUSUNIT', INDETERMINATE)
soundpowerlevelunit = getattr(IfcDerivedUnitEnum, 'SOUNDPOWERLEVELUNIT', INDETERMINATE)
soundpowerunit = getattr(IfcDerivedUnitEnum, 'SOUNDPOWERUNIT', INDETERMINATE)
soundpressurelevelunit = getattr(IfcDerivedUnitEnum, 'SOUNDPRESSURELEVELUNIT', INDETERMINATE)
soundpressureunit = getattr(IfcDerivedUnitEnum, 'SOUNDPRESSUREUNIT', INDETERMINATE)
temperaturegradientunit = getattr(IfcDerivedUnitEnum, 'TEMPERATUREGRADIENTUNIT', INDETERMINATE)
temperaturerateofchangeunit = getattr(IfcDerivedUnitEnum, 'TEMPERATURERATEOFCHANGEUNIT', INDETERMINATE)
thermalexpansioncoefficientunit = getattr(IfcDerivedUnitEnum, 'THERMALEXPANSIONCOEFFICIENTUNIT', INDETERMINATE)
warpingconstantunit = getattr(IfcDerivedUnitEnum, 'WARPINGCONSTANTUNIT', INDETERMINATE)
warpingmomentunit = getattr(IfcDerivedUnitEnum, 'WARPINGMOMENTUNIT', INDETERMINATE)
userdefined = getattr(IfcDerivedUnitEnum, 'USERDEFINED', INDETERMINATE)
IfcDirectionSenseEnum = enum_namespace()
positive = getattr(IfcDirectionSenseEnum, 'POSITIVE', INDETERMINATE)
negative = getattr(IfcDirectionSenseEnum, 'NEGATIVE', INDETERMINATE)
IfcDiscreteAccessoryTypeEnum = enum_namespace()
anchorplate = getattr(IfcDiscreteAccessoryTypeEnum, 'ANCHORPLATE', INDETERMINATE)
bracket = getattr(IfcDiscreteAccessoryTypeEnum, 'BRACKET', INDETERMINATE)
shoe = getattr(IfcDiscreteAccessoryTypeEnum, 'SHOE', INDETERMINATE)
userdefined = getattr(IfcDiscreteAccessoryTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcDiscreteAccessoryTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcDistributionChamberElementTypeEnum = enum_namespace()
formedduct = getattr(IfcDistributionChamberElementTypeEnum, 'FORMEDDUCT', INDETERMINATE)
inspectionchamber = getattr(IfcDistributionChamberElementTypeEnum, 'INSPECTIONCHAMBER', INDETERMINATE)
inspectionpit = getattr(IfcDistributionChamberElementTypeEnum, 'INSPECTIONPIT', INDETERMINATE)
manhole = getattr(IfcDistributionChamberElementTypeEnum, 'MANHOLE', INDETERMINATE)
meterchamber = getattr(IfcDistributionChamberElementTypeEnum, 'METERCHAMBER', INDETERMINATE)
sump = getattr(IfcDistributionChamberElementTypeEnum, 'SUMP', INDETERMINATE)
trench = getattr(IfcDistributionChamberElementTypeEnum, 'TRENCH', INDETERMINATE)
valvechamber = getattr(IfcDistributionChamberElementTypeEnum, 'VALVECHAMBER', INDETERMINATE)
userdefined = getattr(IfcDistributionChamberElementTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcDistributionChamberElementTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcDistributionPortTypeEnum = enum_namespace()
cable = getattr(IfcDistributionPortTypeEnum, 'CABLE', INDETERMINATE)
cablecarrier = getattr(IfcDistributionPortTypeEnum, 'CABLECARRIER', INDETERMINATE)
duct = getattr(IfcDistributionPortTypeEnum, 'DUCT', INDETERMINATE)
pipe = getattr(IfcDistributionPortTypeEnum, 'PIPE', INDETERMINATE)
userdefined = getattr(IfcDistributionPortTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcDistributionPortTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcDistributionSystemEnum = enum_namespace()
airconditioning = getattr(IfcDistributionSystemEnum, 'AIRCONDITIONING', INDETERMINATE)
audiovisual = getattr(IfcDistributionSystemEnum, 'AUDIOVISUAL', INDETERMINATE)
chemical = getattr(IfcDistributionSystemEnum, 'CHEMICAL', INDETERMINATE)
chilledwater = getattr(IfcDistributionSystemEnum, 'CHILLEDWATER', INDETERMINATE)
communication = getattr(IfcDistributionSystemEnum, 'COMMUNICATION', INDETERMINATE)
compressedair = getattr(IfcDistributionSystemEnum, 'COMPRESSEDAIR', INDETERMINATE)
condenserwater = getattr(IfcDistributionSystemEnum, 'CONDENSERWATER', INDETERMINATE)
control = getattr(IfcDistributionSystemEnum, 'CONTROL', INDETERMINATE)
conveying = getattr(IfcDistributionSystemEnum, 'CONVEYING', INDETERMINATE)
data = getattr(IfcDistributionSystemEnum, 'DATA', INDETERMINATE)
disposal = getattr(IfcDistributionSystemEnum, 'DISPOSAL', INDETERMINATE)
domesticcoldwater = getattr(IfcDistributionSystemEnum, 'DOMESTICCOLDWATER', INDETERMINATE)
domestichotwater = getattr(IfcDistributionSystemEnum, 'DOMESTICHOTWATER', INDETERMINATE)
drainage = getattr(IfcDistributionSystemEnum, 'DRAINAGE', INDETERMINATE)
earthing = getattr(IfcDistributionSystemEnum, 'EARTHING', INDETERMINATE)
electrical = getattr(IfcDistributionSystemEnum, 'ELECTRICAL', INDETERMINATE)
electroacoustic = getattr(IfcDistributionSystemEnum, 'ELECTROACOUSTIC', INDETERMINATE)
exhaust = getattr(IfcDistributionSystemEnum, 'EXHAUST', INDETERMINATE)
fireprotection = getattr(IfcDistributionSystemEnum, 'FIREPROTECTION', INDETERMINATE)
fuel = getattr(IfcDistributionSystemEnum, 'FUEL', INDETERMINATE)
gas = getattr(IfcDistributionSystemEnum, 'GAS', INDETERMINATE)
hazardous = getattr(IfcDistributionSystemEnum, 'HAZARDOUS', INDETERMINATE)
heating = getattr(IfcDistributionSystemEnum, 'HEATING', INDETERMINATE)
lighting = getattr(IfcDistributionSystemEnum, 'LIGHTING', INDETERMINATE)
lightningprotection = getattr(IfcDistributionSystemEnum, 'LIGHTNINGPROTECTION', INDETERMINATE)
municipalsolidwaste = getattr(IfcDistributionSystemEnum, 'MUNICIPALSOLIDWASTE', INDETERMINATE)
oil = getattr(IfcDistributionSystemEnum, 'OIL', INDETERMINATE)
operational = getattr(IfcDistributionSystemEnum, 'OPERATIONAL', INDETERMINATE)
powergeneration = getattr(IfcDistributionSystemEnum, 'POWERGENERATION', INDETERMINATE)
rainwater = getattr(IfcDistributionSystemEnum, 'RAINWATER', INDETERMINATE)
refrigeration = getattr(IfcDistributionSystemEnum, 'REFRIGERATION', INDETERMINATE)
security = getattr(IfcDistributionSystemEnum, 'SECURITY', INDETERMINATE)
sewage = getattr(IfcDistributionSystemEnum, 'SEWAGE', INDETERMINATE)
signal = getattr(IfcDistributionSystemEnum, 'SIGNAL', INDETERMINATE)
stormwater = getattr(IfcDistributionSystemEnum, 'STORMWATER', INDETERMINATE)
telephone = getattr(IfcDistributionSystemEnum, 'TELEPHONE', INDETERMINATE)
tv = getattr(IfcDistributionSystemEnum, 'TV', INDETERMINATE)
vacuum = getattr(IfcDistributionSystemEnum, 'VACUUM', INDETERMINATE)
vent = getattr(IfcDistributionSystemEnum, 'VENT', INDETERMINATE)
ventilation = getattr(IfcDistributionSystemEnum, 'VENTILATION', INDETERMINATE)
wastewater = getattr(IfcDistributionSystemEnum, 'WASTEWATER', INDETERMINATE)
watersupply = getattr(IfcDistributionSystemEnum, 'WATERSUPPLY', INDETERMINATE)
userdefined = getattr(IfcDistributionSystemEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcDistributionSystemEnum, 'NOTDEFINED', INDETERMINATE)
IfcDocumentConfidentialityEnum = enum_namespace()
public = getattr(IfcDocumentConfidentialityEnum, 'PUBLIC', INDETERMINATE)
restricted = getattr(IfcDocumentConfidentialityEnum, 'RESTRICTED', INDETERMINATE)
confidential = getattr(IfcDocumentConfidentialityEnum, 'CONFIDENTIAL', INDETERMINATE)
personal = getattr(IfcDocumentConfidentialityEnum, 'PERSONAL', INDETERMINATE)
userdefined = getattr(IfcDocumentConfidentialityEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcDocumentConfidentialityEnum, 'NOTDEFINED', INDETERMINATE)
IfcDocumentStatusEnum = enum_namespace()
draft = getattr(IfcDocumentStatusEnum, 'DRAFT', INDETERMINATE)
finaldraft = getattr(IfcDocumentStatusEnum, 'FINALDRAFT', INDETERMINATE)
final = getattr(IfcDocumentStatusEnum, 'FINAL', INDETERMINATE)
revision = getattr(IfcDocumentStatusEnum, 'REVISION', INDETERMINATE)
notdefined = getattr(IfcDocumentStatusEnum, 'NOTDEFINED', INDETERMINATE)
IfcDoorPanelOperationEnum = enum_namespace()
swinging = getattr(IfcDoorPanelOperationEnum, 'SWINGING', INDETERMINATE)
double_acting = getattr(IfcDoorPanelOperationEnum, 'DOUBLE_ACTING', INDETERMINATE)
sliding = getattr(IfcDoorPanelOperationEnum, 'SLIDING', INDETERMINATE)
folding = getattr(IfcDoorPanelOperationEnum, 'FOLDING', INDETERMINATE)
revolving = getattr(IfcDoorPanelOperationEnum, 'REVOLVING', INDETERMINATE)
rollingup = getattr(IfcDoorPanelOperationEnum, 'ROLLINGUP', INDETERMINATE)
fixedpanel = getattr(IfcDoorPanelOperationEnum, 'FIXEDPANEL', INDETERMINATE)
userdefined = getattr(IfcDoorPanelOperationEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcDoorPanelOperationEnum, 'NOTDEFINED', INDETERMINATE)
IfcDoorPanelPositionEnum = enum_namespace()
left = getattr(IfcDoorPanelPositionEnum, 'LEFT', INDETERMINATE)
middle = getattr(IfcDoorPanelPositionEnum, 'MIDDLE', INDETERMINATE)
right = getattr(IfcDoorPanelPositionEnum, 'RIGHT', INDETERMINATE)
notdefined = getattr(IfcDoorPanelPositionEnum, 'NOTDEFINED', INDETERMINATE)
IfcDoorStyleConstructionEnum = enum_namespace()
aluminium = getattr(IfcDoorStyleConstructionEnum, 'ALUMINIUM', INDETERMINATE)
high_grade_steel = getattr(IfcDoorStyleConstructionEnum, 'HIGH_GRADE_STEEL', INDETERMINATE)
steel = getattr(IfcDoorStyleConstructionEnum, 'STEEL', INDETERMINATE)
wood = getattr(IfcDoorStyleConstructionEnum, 'WOOD', INDETERMINATE)
aluminium_wood = getattr(IfcDoorStyleConstructionEnum, 'ALUMINIUM_WOOD', INDETERMINATE)
aluminium_plastic = getattr(IfcDoorStyleConstructionEnum, 'ALUMINIUM_PLASTIC', INDETERMINATE)
plastic = getattr(IfcDoorStyleConstructionEnum, 'PLASTIC', INDETERMINATE)
userdefined = getattr(IfcDoorStyleConstructionEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcDoorStyleConstructionEnum, 'NOTDEFINED', INDETERMINATE)
IfcDoorStyleOperationEnum = enum_namespace()
single_swing_left = getattr(IfcDoorStyleOperationEnum, 'SINGLE_SWING_LEFT', INDETERMINATE)
single_swing_right = getattr(IfcDoorStyleOperationEnum, 'SINGLE_SWING_RIGHT', INDETERMINATE)
double_door_single_swing = getattr(IfcDoorStyleOperationEnum, 'DOUBLE_DOOR_SINGLE_SWING', INDETERMINATE)
double_door_single_swing_opposite_left = getattr(IfcDoorStyleOperationEnum, 'DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_LEFT', INDETERMINATE)
double_door_single_swing_opposite_right = getattr(IfcDoorStyleOperationEnum, 'DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_RIGHT', INDETERMINATE)
double_swing_left = getattr(IfcDoorStyleOperationEnum, 'DOUBLE_SWING_LEFT', INDETERMINATE)
double_swing_right = getattr(IfcDoorStyleOperationEnum, 'DOUBLE_SWING_RIGHT', INDETERMINATE)
double_door_double_swing = getattr(IfcDoorStyleOperationEnum, 'DOUBLE_DOOR_DOUBLE_SWING', INDETERMINATE)
sliding_to_left = getattr(IfcDoorStyleOperationEnum, 'SLIDING_TO_LEFT', INDETERMINATE)
sliding_to_right = getattr(IfcDoorStyleOperationEnum, 'SLIDING_TO_RIGHT', INDETERMINATE)
double_door_sliding = getattr(IfcDoorStyleOperationEnum, 'DOUBLE_DOOR_SLIDING', INDETERMINATE)
folding_to_left = getattr(IfcDoorStyleOperationEnum, 'FOLDING_TO_LEFT', INDETERMINATE)
folding_to_right = getattr(IfcDoorStyleOperationEnum, 'FOLDING_TO_RIGHT', INDETERMINATE)
double_door_folding = getattr(IfcDoorStyleOperationEnum, 'DOUBLE_DOOR_FOLDING', INDETERMINATE)
revolving = getattr(IfcDoorStyleOperationEnum, 'REVOLVING', INDETERMINATE)
rollingup = getattr(IfcDoorStyleOperationEnum, 'ROLLINGUP', INDETERMINATE)
userdefined = getattr(IfcDoorStyleOperationEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcDoorStyleOperationEnum, 'NOTDEFINED', INDETERMINATE)
IfcDoorTypeEnum = enum_namespace()
door = getattr(IfcDoorTypeEnum, 'DOOR', INDETERMINATE)
gate = getattr(IfcDoorTypeEnum, 'GATE', INDETERMINATE)
trapdoor = getattr(IfcDoorTypeEnum, 'TRAPDOOR', INDETERMINATE)
userdefined = getattr(IfcDoorTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcDoorTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcDoorTypeOperationEnum = enum_namespace()
single_swing_left = getattr(IfcDoorTypeOperationEnum, 'SINGLE_SWING_LEFT', INDETERMINATE)
single_swing_right = getattr(IfcDoorTypeOperationEnum, 'SINGLE_SWING_RIGHT', INDETERMINATE)
double_door_single_swing = getattr(IfcDoorTypeOperationEnum, 'DOUBLE_DOOR_SINGLE_SWING', INDETERMINATE)
double_door_single_swing_opposite_left = getattr(IfcDoorTypeOperationEnum, 'DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_LEFT', INDETERMINATE)
double_door_single_swing_opposite_right = getattr(IfcDoorTypeOperationEnum, 'DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_RIGHT', INDETERMINATE)
double_swing_left = getattr(IfcDoorTypeOperationEnum, 'DOUBLE_SWING_LEFT', INDETERMINATE)
double_swing_right = getattr(IfcDoorTypeOperationEnum, 'DOUBLE_SWING_RIGHT', INDETERMINATE)
double_door_double_swing = getattr(IfcDoorTypeOperationEnum, 'DOUBLE_DOOR_DOUBLE_SWING', INDETERMINATE)
sliding_to_left = getattr(IfcDoorTypeOperationEnum, 'SLIDING_TO_LEFT', INDETERMINATE)
sliding_to_right = getattr(IfcDoorTypeOperationEnum, 'SLIDING_TO_RIGHT', INDETERMINATE)
double_door_sliding = getattr(IfcDoorTypeOperationEnum, 'DOUBLE_DOOR_SLIDING', INDETERMINATE)
folding_to_left = getattr(IfcDoorTypeOperationEnum, 'FOLDING_TO_LEFT', INDETERMINATE)
folding_to_right = getattr(IfcDoorTypeOperationEnum, 'FOLDING_TO_RIGHT', INDETERMINATE)
double_door_folding = getattr(IfcDoorTypeOperationEnum, 'DOUBLE_DOOR_FOLDING', INDETERMINATE)
revolving = getattr(IfcDoorTypeOperationEnum, 'REVOLVING', INDETERMINATE)
rollingup = getattr(IfcDoorTypeOperationEnum, 'ROLLINGUP', INDETERMINATE)
swing_fixed_left = getattr(IfcDoorTypeOperationEnum, 'SWING_FIXED_LEFT', INDETERMINATE)
swing_fixed_right = getattr(IfcDoorTypeOperationEnum, 'SWING_FIXED_RIGHT', INDETERMINATE)
userdefined = getattr(IfcDoorTypeOperationEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcDoorTypeOperationEnum, 'NOTDEFINED', INDETERMINATE)
IfcDuctFittingTypeEnum = enum_namespace()
bend = getattr(IfcDuctFittingTypeEnum, 'BEND', INDETERMINATE)
connector = getattr(IfcDuctFittingTypeEnum, 'CONNECTOR', INDETERMINATE)
entry = getattr(IfcDuctFittingTypeEnum, 'ENTRY', INDETERMINATE)
exit = getattr(IfcDuctFittingTypeEnum, 'EXIT', INDETERMINATE)
junction = getattr(IfcDuctFittingTypeEnum, 'JUNCTION', INDETERMINATE)
obstruction = getattr(IfcDuctFittingTypeEnum, 'OBSTRUCTION', INDETERMINATE)
transition = getattr(IfcDuctFittingTypeEnum, 'TRANSITION', INDETERMINATE)
userdefined = getattr(IfcDuctFittingTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcDuctFittingTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcDuctSegmentTypeEnum = enum_namespace()
rigidsegment = getattr(IfcDuctSegmentTypeEnum, 'RIGIDSEGMENT', INDETERMINATE)
flexiblesegment = getattr(IfcDuctSegmentTypeEnum, 'FLEXIBLESEGMENT', INDETERMINATE)
userdefined = getattr(IfcDuctSegmentTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcDuctSegmentTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcDuctSilencerTypeEnum = enum_namespace()
flatoval = getattr(IfcDuctSilencerTypeEnum, 'FLATOVAL', INDETERMINATE)
rectangular = getattr(IfcDuctSilencerTypeEnum, 'RECTANGULAR', INDETERMINATE)
round = getattr(IfcDuctSilencerTypeEnum, 'ROUND', INDETERMINATE)
userdefined = getattr(IfcDuctSilencerTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcDuctSilencerTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcElectricApplianceTypeEnum = enum_namespace()
dishwasher = getattr(IfcElectricApplianceTypeEnum, 'DISHWASHER', INDETERMINATE)
electriccooker = getattr(IfcElectricApplianceTypeEnum, 'ELECTRICCOOKER', INDETERMINATE)
freestandingelectricheater = getattr(IfcElectricApplianceTypeEnum, 'FREESTANDINGELECTRICHEATER', INDETERMINATE)
freestandingfan = getattr(IfcElectricApplianceTypeEnum, 'FREESTANDINGFAN', INDETERMINATE)
freestandingwaterheater = getattr(IfcElectricApplianceTypeEnum, 'FREESTANDINGWATERHEATER', INDETERMINATE)
freestandingwatercooler = getattr(IfcElectricApplianceTypeEnum, 'FREESTANDINGWATERCOOLER', INDETERMINATE)
freezer = getattr(IfcElectricApplianceTypeEnum, 'FREEZER', INDETERMINATE)
fridge_freezer = getattr(IfcElectricApplianceTypeEnum, 'FRIDGE_FREEZER', INDETERMINATE)
handdryer = getattr(IfcElectricApplianceTypeEnum, 'HANDDRYER', INDETERMINATE)
kitchenmachine = getattr(IfcElectricApplianceTypeEnum, 'KITCHENMACHINE', INDETERMINATE)
microwave = getattr(IfcElectricApplianceTypeEnum, 'MICROWAVE', INDETERMINATE)
photocopier = getattr(IfcElectricApplianceTypeEnum, 'PHOTOCOPIER', INDETERMINATE)
refrigerator = getattr(IfcElectricApplianceTypeEnum, 'REFRIGERATOR', INDETERMINATE)
tumbledryer = getattr(IfcElectricApplianceTypeEnum, 'TUMBLEDRYER', INDETERMINATE)
vendingmachine = getattr(IfcElectricApplianceTypeEnum, 'VENDINGMACHINE', INDETERMINATE)
washingmachine = getattr(IfcElectricApplianceTypeEnum, 'WASHINGMACHINE', INDETERMINATE)
userdefined = getattr(IfcElectricApplianceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcElectricApplianceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcElectricDistributionBoardTypeEnum = enum_namespace()
consumerunit = getattr(IfcElectricDistributionBoardTypeEnum, 'CONSUMERUNIT', INDETERMINATE)
distributionboard = getattr(IfcElectricDistributionBoardTypeEnum, 'DISTRIBUTIONBOARD', INDETERMINATE)
motorcontrolcentre = getattr(IfcElectricDistributionBoardTypeEnum, 'MOTORCONTROLCENTRE', INDETERMINATE)
switchboard = getattr(IfcElectricDistributionBoardTypeEnum, 'SWITCHBOARD', INDETERMINATE)
userdefined = getattr(IfcElectricDistributionBoardTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcElectricDistributionBoardTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcElectricFlowStorageDeviceTypeEnum = enum_namespace()
battery = getattr(IfcElectricFlowStorageDeviceTypeEnum, 'BATTERY', INDETERMINATE)
capacitorbank = getattr(IfcElectricFlowStorageDeviceTypeEnum, 'CAPACITORBANK', INDETERMINATE)
harmonicfilter = getattr(IfcElectricFlowStorageDeviceTypeEnum, 'HARMONICFILTER', INDETERMINATE)
inductorbank = getattr(IfcElectricFlowStorageDeviceTypeEnum, 'INDUCTORBANK', INDETERMINATE)
ups = getattr(IfcElectricFlowStorageDeviceTypeEnum, 'UPS', INDETERMINATE)
userdefined = getattr(IfcElectricFlowStorageDeviceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcElectricFlowStorageDeviceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcElectricGeneratorTypeEnum = enum_namespace()
chp = getattr(IfcElectricGeneratorTypeEnum, 'CHP', INDETERMINATE)
enginegenerator = getattr(IfcElectricGeneratorTypeEnum, 'ENGINEGENERATOR', INDETERMINATE)
standalone = getattr(IfcElectricGeneratorTypeEnum, 'STANDALONE', INDETERMINATE)
userdefined = getattr(IfcElectricGeneratorTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcElectricGeneratorTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcElectricMotorTypeEnum = enum_namespace()
dc = getattr(IfcElectricMotorTypeEnum, 'DC', INDETERMINATE)
induction = getattr(IfcElectricMotorTypeEnum, 'INDUCTION', INDETERMINATE)
polyphase = getattr(IfcElectricMotorTypeEnum, 'POLYPHASE', INDETERMINATE)
reluctancesynchronous = getattr(IfcElectricMotorTypeEnum, 'RELUCTANCESYNCHRONOUS', INDETERMINATE)
synchronous = getattr(IfcElectricMotorTypeEnum, 'SYNCHRONOUS', INDETERMINATE)
userdefined = getattr(IfcElectricMotorTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcElectricMotorTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcElectricTimeControlTypeEnum = enum_namespace()
timeclock = getattr(IfcElectricTimeControlTypeEnum, 'TIMECLOCK', INDETERMINATE)
timedelay = getattr(IfcElectricTimeControlTypeEnum, 'TIMEDELAY', INDETERMINATE)
relay = getattr(IfcElectricTimeControlTypeEnum, 'RELAY', INDETERMINATE)
userdefined = getattr(IfcElectricTimeControlTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcElectricTimeControlTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcElementAssemblyTypeEnum = enum_namespace()
accessory_assembly = getattr(IfcElementAssemblyTypeEnum, 'ACCESSORY_ASSEMBLY', INDETERMINATE)
arch = getattr(IfcElementAssemblyTypeEnum, 'ARCH', INDETERMINATE)
beam_grid = getattr(IfcElementAssemblyTypeEnum, 'BEAM_GRID', INDETERMINATE)
braced_frame = getattr(IfcElementAssemblyTypeEnum, 'BRACED_FRAME', INDETERMINATE)
girder = getattr(IfcElementAssemblyTypeEnum, 'GIRDER', INDETERMINATE)
reinforcement_unit = getattr(IfcElementAssemblyTypeEnum, 'REINFORCEMENT_UNIT', INDETERMINATE)
rigid_frame = getattr(IfcElementAssemblyTypeEnum, 'RIGID_FRAME', INDETERMINATE)
slab_field = getattr(IfcElementAssemblyTypeEnum, 'SLAB_FIELD', INDETERMINATE)
truss = getattr(IfcElementAssemblyTypeEnum, 'TRUSS', INDETERMINATE)
userdefined = getattr(IfcElementAssemblyTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcElementAssemblyTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcElementCompositionEnum = enum_namespace()
complex = getattr(IfcElementCompositionEnum, 'COMPLEX', INDETERMINATE)
element = getattr(IfcElementCompositionEnum, 'ELEMENT', INDETERMINATE)
partial = getattr(IfcElementCompositionEnum, 'PARTIAL', INDETERMINATE)
IfcEngineTypeEnum = enum_namespace()
externalcombustion = getattr(IfcEngineTypeEnum, 'EXTERNALCOMBUSTION', INDETERMINATE)
internalcombustion = getattr(IfcEngineTypeEnum, 'INTERNALCOMBUSTION', INDETERMINATE)
userdefined = getattr(IfcEngineTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcEngineTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcEvaporativeCoolerTypeEnum = enum_namespace()
directevaporativerandommediaaircooler = getattr(IfcEvaporativeCoolerTypeEnum, 'DIRECTEVAPORATIVERANDOMMEDIAAIRCOOLER', INDETERMINATE)
directevaporativerigidmediaaircooler = getattr(IfcEvaporativeCoolerTypeEnum, 'DIRECTEVAPORATIVERIGIDMEDIAAIRCOOLER', INDETERMINATE)
directevaporativeslingerspackagedaircooler = getattr(IfcEvaporativeCoolerTypeEnum, 'DIRECTEVAPORATIVESLINGERSPACKAGEDAIRCOOLER', INDETERMINATE)
directevaporativepackagedrotaryaircooler = getattr(IfcEvaporativeCoolerTypeEnum, 'DIRECTEVAPORATIVEPACKAGEDROTARYAIRCOOLER', INDETERMINATE)
directevaporativeairwasher = getattr(IfcEvaporativeCoolerTypeEnum, 'DIRECTEVAPORATIVEAIRWASHER', INDETERMINATE)
indirectevaporativepackageaircooler = getattr(IfcEvaporativeCoolerTypeEnum, 'INDIRECTEVAPORATIVEPACKAGEAIRCOOLER', INDETERMINATE)
indirectevaporativewetcoil = getattr(IfcEvaporativeCoolerTypeEnum, 'INDIRECTEVAPORATIVEWETCOIL', INDETERMINATE)
indirectevaporativecoolingtowerorcoilcooler = getattr(IfcEvaporativeCoolerTypeEnum, 'INDIRECTEVAPORATIVECOOLINGTOWERORCOILCOOLER', INDETERMINATE)
indirectdirectcombination = getattr(IfcEvaporativeCoolerTypeEnum, 'INDIRECTDIRECTCOMBINATION', INDETERMINATE)
userdefined = getattr(IfcEvaporativeCoolerTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcEvaporativeCoolerTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcEvaporatorTypeEnum = enum_namespace()
directexpansion = getattr(IfcEvaporatorTypeEnum, 'DIRECTEXPANSION', INDETERMINATE)
directexpansionshellandtube = getattr(IfcEvaporatorTypeEnum, 'DIRECTEXPANSIONSHELLANDTUBE', INDETERMINATE)
directexpansiontubeintube = getattr(IfcEvaporatorTypeEnum, 'DIRECTEXPANSIONTUBEINTUBE', INDETERMINATE)
directexpansionbrazedplate = getattr(IfcEvaporatorTypeEnum, 'DIRECTEXPANSIONBRAZEDPLATE', INDETERMINATE)
floodedshellandtube = getattr(IfcEvaporatorTypeEnum, 'FLOODEDSHELLANDTUBE', INDETERMINATE)
shellandcoil = getattr(IfcEvaporatorTypeEnum, 'SHELLANDCOIL', INDETERMINATE)
userdefined = getattr(IfcEvaporatorTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcEvaporatorTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcEventTriggerTypeEnum = enum_namespace()
eventrule = getattr(IfcEventTriggerTypeEnum, 'EVENTRULE', INDETERMINATE)
eventmessage = getattr(IfcEventTriggerTypeEnum, 'EVENTMESSAGE', INDETERMINATE)
eventtime = getattr(IfcEventTriggerTypeEnum, 'EVENTTIME', INDETERMINATE)
eventcomplex = getattr(IfcEventTriggerTypeEnum, 'EVENTCOMPLEX', INDETERMINATE)
userdefined = getattr(IfcEventTriggerTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcEventTriggerTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcEventTypeEnum = enum_namespace()
startevent = getattr(IfcEventTypeEnum, 'STARTEVENT', INDETERMINATE)
endevent = getattr(IfcEventTypeEnum, 'ENDEVENT', INDETERMINATE)
intermediateevent = getattr(IfcEventTypeEnum, 'INTERMEDIATEEVENT', INDETERMINATE)
userdefined = getattr(IfcEventTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcEventTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcExternalSpatialElementTypeEnum = enum_namespace()
external = getattr(IfcExternalSpatialElementTypeEnum, 'EXTERNAL', INDETERMINATE)
external_earth = getattr(IfcExternalSpatialElementTypeEnum, 'EXTERNAL_EARTH', INDETERMINATE)
external_water = getattr(IfcExternalSpatialElementTypeEnum, 'EXTERNAL_WATER', INDETERMINATE)
external_fire = getattr(IfcExternalSpatialElementTypeEnum, 'EXTERNAL_FIRE', INDETERMINATE)
userdefined = getattr(IfcExternalSpatialElementTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcExternalSpatialElementTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcFanTypeEnum = enum_namespace()
centrifugalforwardcurved = getattr(IfcFanTypeEnum, 'CENTRIFUGALFORWARDCURVED', INDETERMINATE)
centrifugalradial = getattr(IfcFanTypeEnum, 'CENTRIFUGALRADIAL', INDETERMINATE)
centrifugalbackwardinclinedcurved = getattr(IfcFanTypeEnum, 'CENTRIFUGALBACKWARDINCLINEDCURVED', INDETERMINATE)
centrifugalairfoil = getattr(IfcFanTypeEnum, 'CENTRIFUGALAIRFOIL', INDETERMINATE)
tubeaxial = getattr(IfcFanTypeEnum, 'TUBEAXIAL', INDETERMINATE)
vaneaxial = getattr(IfcFanTypeEnum, 'VANEAXIAL', INDETERMINATE)
propelloraxial = getattr(IfcFanTypeEnum, 'PROPELLORAXIAL', INDETERMINATE)
userdefined = getattr(IfcFanTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcFanTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcFastenerTypeEnum = enum_namespace()
glue = getattr(IfcFastenerTypeEnum, 'GLUE', INDETERMINATE)
mortar = getattr(IfcFastenerTypeEnum, 'MORTAR', INDETERMINATE)
weld = getattr(IfcFastenerTypeEnum, 'WELD', INDETERMINATE)
userdefined = getattr(IfcFastenerTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcFastenerTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcFilterTypeEnum = enum_namespace()
airparticlefilter = getattr(IfcFilterTypeEnum, 'AIRPARTICLEFILTER', INDETERMINATE)
compressedairfilter = getattr(IfcFilterTypeEnum, 'COMPRESSEDAIRFILTER', INDETERMINATE)
odorfilter = getattr(IfcFilterTypeEnum, 'ODORFILTER', INDETERMINATE)
oilfilter = getattr(IfcFilterTypeEnum, 'OILFILTER', INDETERMINATE)
strainer = getattr(IfcFilterTypeEnum, 'STRAINER', INDETERMINATE)
waterfilter = getattr(IfcFilterTypeEnum, 'WATERFILTER', INDETERMINATE)
userdefined = getattr(IfcFilterTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcFilterTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcFireSuppressionTerminalTypeEnum = enum_namespace()
breechinginlet = getattr(IfcFireSuppressionTerminalTypeEnum, 'BREECHINGINLET', INDETERMINATE)
firehydrant = getattr(IfcFireSuppressionTerminalTypeEnum, 'FIREHYDRANT', INDETERMINATE)
hosereel = getattr(IfcFireSuppressionTerminalTypeEnum, 'HOSEREEL', INDETERMINATE)
sprinkler = getattr(IfcFireSuppressionTerminalTypeEnum, 'SPRINKLER', INDETERMINATE)
sprinklerdeflector = getattr(IfcFireSuppressionTerminalTypeEnum, 'SPRINKLERDEFLECTOR', INDETERMINATE)
userdefined = getattr(IfcFireSuppressionTerminalTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcFireSuppressionTerminalTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcFlowDirectionEnum = enum_namespace()
source = getattr(IfcFlowDirectionEnum, 'SOURCE', INDETERMINATE)
sink = getattr(IfcFlowDirectionEnum, 'SINK', INDETERMINATE)
sourceandsink = getattr(IfcFlowDirectionEnum, 'SOURCEANDSINK', INDETERMINATE)
notdefined = getattr(IfcFlowDirectionEnum, 'NOTDEFINED', INDETERMINATE)
IfcFlowInstrumentTypeEnum = enum_namespace()
pressuregauge = getattr(IfcFlowInstrumentTypeEnum, 'PRESSUREGAUGE', INDETERMINATE)
thermometer = getattr(IfcFlowInstrumentTypeEnum, 'THERMOMETER', INDETERMINATE)
ammeter = getattr(IfcFlowInstrumentTypeEnum, 'AMMETER', INDETERMINATE)
frequencymeter = getattr(IfcFlowInstrumentTypeEnum, 'FREQUENCYMETER', INDETERMINATE)
powerfactormeter = getattr(IfcFlowInstrumentTypeEnum, 'POWERFACTORMETER', INDETERMINATE)
phaseanglemeter = getattr(IfcFlowInstrumentTypeEnum, 'PHASEANGLEMETER', INDETERMINATE)
voltmeter_peak = getattr(IfcFlowInstrumentTypeEnum, 'VOLTMETER_PEAK', INDETERMINATE)
voltmeter_rms = getattr(IfcFlowInstrumentTypeEnum, 'VOLTMETER_RMS', INDETERMINATE)
userdefined = getattr(IfcFlowInstrumentTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcFlowInstrumentTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcFlowMeterTypeEnum = enum_namespace()
energymeter = getattr(IfcFlowMeterTypeEnum, 'ENERGYMETER', INDETERMINATE)
gasmeter = getattr(IfcFlowMeterTypeEnum, 'GASMETER', INDETERMINATE)
oilmeter = getattr(IfcFlowMeterTypeEnum, 'OILMETER', INDETERMINATE)
watermeter = getattr(IfcFlowMeterTypeEnum, 'WATERMETER', INDETERMINATE)
userdefined = getattr(IfcFlowMeterTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcFlowMeterTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcFootingTypeEnum = enum_namespace()
caisson_foundation = getattr(IfcFootingTypeEnum, 'CAISSON_FOUNDATION', INDETERMINATE)
footing_beam = getattr(IfcFootingTypeEnum, 'FOOTING_BEAM', INDETERMINATE)
pad_footing = getattr(IfcFootingTypeEnum, 'PAD_FOOTING', INDETERMINATE)
pile_cap = getattr(IfcFootingTypeEnum, 'PILE_CAP', INDETERMINATE)
strip_footing = getattr(IfcFootingTypeEnum, 'STRIP_FOOTING', INDETERMINATE)
userdefined = getattr(IfcFootingTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcFootingTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcFurnitureTypeEnum = enum_namespace()
chair = getattr(IfcFurnitureTypeEnum, 'CHAIR', INDETERMINATE)
table = getattr(IfcFurnitureTypeEnum, 'TABLE', INDETERMINATE)
desk = getattr(IfcFurnitureTypeEnum, 'DESK', INDETERMINATE)
bed = getattr(IfcFurnitureTypeEnum, 'BED', INDETERMINATE)
filecabinet = getattr(IfcFurnitureTypeEnum, 'FILECABINET', INDETERMINATE)
shelf = getattr(IfcFurnitureTypeEnum, 'SHELF', INDETERMINATE)
sofa = getattr(IfcFurnitureTypeEnum, 'SOFA', INDETERMINATE)
userdefined = getattr(IfcFurnitureTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcFurnitureTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcGeographicElementTypeEnum = enum_namespace()
terrain = getattr(IfcGeographicElementTypeEnum, 'TERRAIN', INDETERMINATE)
userdefined = getattr(IfcGeographicElementTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcGeographicElementTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcGeometricProjectionEnum = enum_namespace()
graph_view = getattr(IfcGeometricProjectionEnum, 'GRAPH_VIEW', INDETERMINATE)
sketch_view = getattr(IfcGeometricProjectionEnum, 'SKETCH_VIEW', INDETERMINATE)
model_view = getattr(IfcGeometricProjectionEnum, 'MODEL_VIEW', INDETERMINATE)
plan_view = getattr(IfcGeometricProjectionEnum, 'PLAN_VIEW', INDETERMINATE)
reflected_plan_view = getattr(IfcGeometricProjectionEnum, 'REFLECTED_PLAN_VIEW', INDETERMINATE)
section_view = getattr(IfcGeometricProjectionEnum, 'SECTION_VIEW', INDETERMINATE)
elevation_view = getattr(IfcGeometricProjectionEnum, 'ELEVATION_VIEW', INDETERMINATE)
userdefined = getattr(IfcGeometricProjectionEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcGeometricProjectionEnum, 'NOTDEFINED', INDETERMINATE)
IfcGlobalOrLocalEnum = enum_namespace()
global_coords = getattr(IfcGlobalOrLocalEnum, 'GLOBAL_COORDS', INDETERMINATE)
local_coords = getattr(IfcGlobalOrLocalEnum, 'LOCAL_COORDS', INDETERMINATE)
IfcGridTypeEnum = enum_namespace()
rectangular = getattr(IfcGridTypeEnum, 'RECTANGULAR', INDETERMINATE)
radial = getattr(IfcGridTypeEnum, 'RADIAL', INDETERMINATE)
triangular = getattr(IfcGridTypeEnum, 'TRIANGULAR', INDETERMINATE)
irregular = getattr(IfcGridTypeEnum, 'IRREGULAR', INDETERMINATE)
userdefined = getattr(IfcGridTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcGridTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcHeatExchangerTypeEnum = enum_namespace()
plate = getattr(IfcHeatExchangerTypeEnum, 'PLATE', INDETERMINATE)
shellandtube = getattr(IfcHeatExchangerTypeEnum, 'SHELLANDTUBE', INDETERMINATE)
userdefined = getattr(IfcHeatExchangerTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcHeatExchangerTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcHumidifierTypeEnum = enum_namespace()
steaminjection = getattr(IfcHumidifierTypeEnum, 'STEAMINJECTION', INDETERMINATE)
adiabaticairwasher = getattr(IfcHumidifierTypeEnum, 'ADIABATICAIRWASHER', INDETERMINATE)
adiabaticpan = getattr(IfcHumidifierTypeEnum, 'ADIABATICPAN', INDETERMINATE)
adiabaticwettedelement = getattr(IfcHumidifierTypeEnum, 'ADIABATICWETTEDELEMENT', INDETERMINATE)
adiabaticatomizing = getattr(IfcHumidifierTypeEnum, 'ADIABATICATOMIZING', INDETERMINATE)
adiabaticultrasonic = getattr(IfcHumidifierTypeEnum, 'ADIABATICULTRASONIC', INDETERMINATE)
adiabaticrigidmedia = getattr(IfcHumidifierTypeEnum, 'ADIABATICRIGIDMEDIA', INDETERMINATE)
adiabaticcompressedairnozzle = getattr(IfcHumidifierTypeEnum, 'ADIABATICCOMPRESSEDAIRNOZZLE', INDETERMINATE)
assistedelectric = getattr(IfcHumidifierTypeEnum, 'ASSISTEDELECTRIC', INDETERMINATE)
assistednaturalgas = getattr(IfcHumidifierTypeEnum, 'ASSISTEDNATURALGAS', INDETERMINATE)
assistedpropane = getattr(IfcHumidifierTypeEnum, 'ASSISTEDPROPANE', INDETERMINATE)
assistedbutane = getattr(IfcHumidifierTypeEnum, 'ASSISTEDBUTANE', INDETERMINATE)
assistedsteam = getattr(IfcHumidifierTypeEnum, 'ASSISTEDSTEAM', INDETERMINATE)
userdefined = getattr(IfcHumidifierTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcHumidifierTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcInterceptorTypeEnum = enum_namespace()
cyclonic = getattr(IfcInterceptorTypeEnum, 'CYCLONIC', INDETERMINATE)
grease = getattr(IfcInterceptorTypeEnum, 'GREASE', INDETERMINATE)
oil = getattr(IfcInterceptorTypeEnum, 'OIL', INDETERMINATE)
petrol = getattr(IfcInterceptorTypeEnum, 'PETROL', INDETERMINATE)
userdefined = getattr(IfcInterceptorTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcInterceptorTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcInternalOrExternalEnum = enum_namespace()
internal = getattr(IfcInternalOrExternalEnum, 'INTERNAL', INDETERMINATE)
external = getattr(IfcInternalOrExternalEnum, 'EXTERNAL', INDETERMINATE)
external_earth = getattr(IfcInternalOrExternalEnum, 'EXTERNAL_EARTH', INDETERMINATE)
external_water = getattr(IfcInternalOrExternalEnum, 'EXTERNAL_WATER', INDETERMINATE)
external_fire = getattr(IfcInternalOrExternalEnum, 'EXTERNAL_FIRE', INDETERMINATE)
notdefined = getattr(IfcInternalOrExternalEnum, 'NOTDEFINED', INDETERMINATE)
IfcInventoryTypeEnum = enum_namespace()
assetinventory = getattr(IfcInventoryTypeEnum, 'ASSETINVENTORY', INDETERMINATE)
spaceinventory = getattr(IfcInventoryTypeEnum, 'SPACEINVENTORY', INDETERMINATE)
furnitureinventory = getattr(IfcInventoryTypeEnum, 'FURNITUREINVENTORY', INDETERMINATE)
userdefined = getattr(IfcInventoryTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcInventoryTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcJunctionBoxTypeEnum = enum_namespace()
data = getattr(IfcJunctionBoxTypeEnum, 'DATA', INDETERMINATE)
power = getattr(IfcJunctionBoxTypeEnum, 'POWER', INDETERMINATE)
userdefined = getattr(IfcJunctionBoxTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcJunctionBoxTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcKnotType = enum_namespace()
uniform_knots = getattr(IfcKnotType, 'UNIFORM_KNOTS', INDETERMINATE)
quasi_uniform_knots = getattr(IfcKnotType, 'QUASI_UNIFORM_KNOTS', INDETERMINATE)
piecewise_bezier_knots = getattr(IfcKnotType, 'PIECEWISE_BEZIER_KNOTS', INDETERMINATE)
unspecified = getattr(IfcKnotType, 'UNSPECIFIED', INDETERMINATE)
IfcLaborResourceTypeEnum = enum_namespace()
administration = getattr(IfcLaborResourceTypeEnum, 'ADMINISTRATION', INDETERMINATE)
carpentry = getattr(IfcLaborResourceTypeEnum, 'CARPENTRY', INDETERMINATE)
cleaning = getattr(IfcLaborResourceTypeEnum, 'CLEANING', INDETERMINATE)
concrete = getattr(IfcLaborResourceTypeEnum, 'CONCRETE', INDETERMINATE)
drywall = getattr(IfcLaborResourceTypeEnum, 'DRYWALL', INDETERMINATE)
electric = getattr(IfcLaborResourceTypeEnum, 'ELECTRIC', INDETERMINATE)
finishing = getattr(IfcLaborResourceTypeEnum, 'FINISHING', INDETERMINATE)
flooring = getattr(IfcLaborResourceTypeEnum, 'FLOORING', INDETERMINATE)
general = getattr(IfcLaborResourceTypeEnum, 'GENERAL', INDETERMINATE)
hvac = getattr(IfcLaborResourceTypeEnum, 'HVAC', INDETERMINATE)
landscaping = getattr(IfcLaborResourceTypeEnum, 'LANDSCAPING', INDETERMINATE)
masonry = getattr(IfcLaborResourceTypeEnum, 'MASONRY', INDETERMINATE)
painting = getattr(IfcLaborResourceTypeEnum, 'PAINTING', INDETERMINATE)
paving = getattr(IfcLaborResourceTypeEnum, 'PAVING', INDETERMINATE)
plumbing = getattr(IfcLaborResourceTypeEnum, 'PLUMBING', INDETERMINATE)
roofing = getattr(IfcLaborResourceTypeEnum, 'ROOFING', INDETERMINATE)
sitegrading = getattr(IfcLaborResourceTypeEnum, 'SITEGRADING', INDETERMINATE)
steelwork = getattr(IfcLaborResourceTypeEnum, 'STEELWORK', INDETERMINATE)
surveying = getattr(IfcLaborResourceTypeEnum, 'SURVEYING', INDETERMINATE)
userdefined = getattr(IfcLaborResourceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcLaborResourceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcLampTypeEnum = enum_namespace()
compactfluorescent = getattr(IfcLampTypeEnum, 'COMPACTFLUORESCENT', INDETERMINATE)
fluorescent = getattr(IfcLampTypeEnum, 'FLUORESCENT', INDETERMINATE)
halogen = getattr(IfcLampTypeEnum, 'HALOGEN', INDETERMINATE)
highpressuremercury = getattr(IfcLampTypeEnum, 'HIGHPRESSUREMERCURY', INDETERMINATE)
highpressuresodium = getattr(IfcLampTypeEnum, 'HIGHPRESSURESODIUM', INDETERMINATE)
led = getattr(IfcLampTypeEnum, 'LED', INDETERMINATE)
metalhalide = getattr(IfcLampTypeEnum, 'METALHALIDE', INDETERMINATE)
oled = getattr(IfcLampTypeEnum, 'OLED', INDETERMINATE)
tungstenfilament = getattr(IfcLampTypeEnum, 'TUNGSTENFILAMENT', INDETERMINATE)
userdefined = getattr(IfcLampTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcLampTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcLayerSetDirectionEnum = enum_namespace()
axis1 = getattr(IfcLayerSetDirectionEnum, 'AXIS1', INDETERMINATE)
axis2 = getattr(IfcLayerSetDirectionEnum, 'AXIS2', INDETERMINATE)
axis3 = getattr(IfcLayerSetDirectionEnum, 'AXIS3', INDETERMINATE)
IfcLightDistributionCurveEnum = enum_namespace()
type_a = getattr(IfcLightDistributionCurveEnum, 'TYPE_A', INDETERMINATE)
type_b = getattr(IfcLightDistributionCurveEnum, 'TYPE_B', INDETERMINATE)
type_c = getattr(IfcLightDistributionCurveEnum, 'TYPE_C', INDETERMINATE)
notdefined = getattr(IfcLightDistributionCurveEnum, 'NOTDEFINED', INDETERMINATE)
IfcLightEmissionSourceEnum = enum_namespace()
compactfluorescent = getattr(IfcLightEmissionSourceEnum, 'COMPACTFLUORESCENT', INDETERMINATE)
fluorescent = getattr(IfcLightEmissionSourceEnum, 'FLUORESCENT', INDETERMINATE)
highpressuremercury = getattr(IfcLightEmissionSourceEnum, 'HIGHPRESSUREMERCURY', INDETERMINATE)
highpressuresodium = getattr(IfcLightEmissionSourceEnum, 'HIGHPRESSURESODIUM', INDETERMINATE)
lightemittingdiode = getattr(IfcLightEmissionSourceEnum, 'LIGHTEMITTINGDIODE', INDETERMINATE)
lowpressuresodium = getattr(IfcLightEmissionSourceEnum, 'LOWPRESSURESODIUM', INDETERMINATE)
lowvoltagehalogen = getattr(IfcLightEmissionSourceEnum, 'LOWVOLTAGEHALOGEN', INDETERMINATE)
mainvoltagehalogen = getattr(IfcLightEmissionSourceEnum, 'MAINVOLTAGEHALOGEN', INDETERMINATE)
metalhalide = getattr(IfcLightEmissionSourceEnum, 'METALHALIDE', INDETERMINATE)
tungstenfilament = getattr(IfcLightEmissionSourceEnum, 'TUNGSTENFILAMENT', INDETERMINATE)
notdefined = getattr(IfcLightEmissionSourceEnum, 'NOTDEFINED', INDETERMINATE)
IfcLightFixtureTypeEnum = enum_namespace()
pointsource = getattr(IfcLightFixtureTypeEnum, 'POINTSOURCE', INDETERMINATE)
directionsource = getattr(IfcLightFixtureTypeEnum, 'DIRECTIONSOURCE', INDETERMINATE)
securitylighting = getattr(IfcLightFixtureTypeEnum, 'SECURITYLIGHTING', INDETERMINATE)
userdefined = getattr(IfcLightFixtureTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcLightFixtureTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcLoadGroupTypeEnum = enum_namespace()
load_group = getattr(IfcLoadGroupTypeEnum, 'LOAD_GROUP', INDETERMINATE)
load_case = getattr(IfcLoadGroupTypeEnum, 'LOAD_CASE', INDETERMINATE)
load_combination = getattr(IfcLoadGroupTypeEnum, 'LOAD_COMBINATION', INDETERMINATE)
userdefined = getattr(IfcLoadGroupTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcLoadGroupTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcLogicalOperatorEnum = enum_namespace()
logicaland = getattr(IfcLogicalOperatorEnum, 'LOGICALAND', INDETERMINATE)
logicalor = getattr(IfcLogicalOperatorEnum, 'LOGICALOR', INDETERMINATE)
logicalxor = getattr(IfcLogicalOperatorEnum, 'LOGICALXOR', INDETERMINATE)
logicalnotand = getattr(IfcLogicalOperatorEnum, 'LOGICALNOTAND', INDETERMINATE)
logicalnotor = getattr(IfcLogicalOperatorEnum, 'LOGICALNOTOR', INDETERMINATE)
IfcMechanicalFastenerTypeEnum = enum_namespace()
anchorbolt = getattr(IfcMechanicalFastenerTypeEnum, 'ANCHORBOLT', INDETERMINATE)
bolt = getattr(IfcMechanicalFastenerTypeEnum, 'BOLT', INDETERMINATE)
dowel = getattr(IfcMechanicalFastenerTypeEnum, 'DOWEL', INDETERMINATE)
nail = getattr(IfcMechanicalFastenerTypeEnum, 'NAIL', INDETERMINATE)
nailplate = getattr(IfcMechanicalFastenerTypeEnum, 'NAILPLATE', INDETERMINATE)
rivet = getattr(IfcMechanicalFastenerTypeEnum, 'RIVET', INDETERMINATE)
screw = getattr(IfcMechanicalFastenerTypeEnum, 'SCREW', INDETERMINATE)
shearconnector = getattr(IfcMechanicalFastenerTypeEnum, 'SHEARCONNECTOR', INDETERMINATE)
staple = getattr(IfcMechanicalFastenerTypeEnum, 'STAPLE', INDETERMINATE)
studshearconnector = getattr(IfcMechanicalFastenerTypeEnum, 'STUDSHEARCONNECTOR', INDETERMINATE)
userdefined = getattr(IfcMechanicalFastenerTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcMechanicalFastenerTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcMedicalDeviceTypeEnum = enum_namespace()
airstation = getattr(IfcMedicalDeviceTypeEnum, 'AIRSTATION', INDETERMINATE)
feedairunit = getattr(IfcMedicalDeviceTypeEnum, 'FEEDAIRUNIT', INDETERMINATE)
oxygengenerator = getattr(IfcMedicalDeviceTypeEnum, 'OXYGENGENERATOR', INDETERMINATE)
oxygenplant = getattr(IfcMedicalDeviceTypeEnum, 'OXYGENPLANT', INDETERMINATE)
vacuumstation = getattr(IfcMedicalDeviceTypeEnum, 'VACUUMSTATION', INDETERMINATE)
userdefined = getattr(IfcMedicalDeviceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcMedicalDeviceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcMemberTypeEnum = enum_namespace()
brace = getattr(IfcMemberTypeEnum, 'BRACE', INDETERMINATE)
chord = getattr(IfcMemberTypeEnum, 'CHORD', INDETERMINATE)
collar = getattr(IfcMemberTypeEnum, 'COLLAR', INDETERMINATE)
member = getattr(IfcMemberTypeEnum, 'MEMBER', INDETERMINATE)
mullion = getattr(IfcMemberTypeEnum, 'MULLION', INDETERMINATE)
plate = getattr(IfcMemberTypeEnum, 'PLATE', INDETERMINATE)
post = getattr(IfcMemberTypeEnum, 'POST', INDETERMINATE)
purlin = getattr(IfcMemberTypeEnum, 'PURLIN', INDETERMINATE)
rafter = getattr(IfcMemberTypeEnum, 'RAFTER', INDETERMINATE)
stringer = getattr(IfcMemberTypeEnum, 'STRINGER', INDETERMINATE)
strut = getattr(IfcMemberTypeEnum, 'STRUT', INDETERMINATE)
stud = getattr(IfcMemberTypeEnum, 'STUD', INDETERMINATE)
userdefined = getattr(IfcMemberTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcMemberTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcMotorConnectionTypeEnum = enum_namespace()
beltdrive = getattr(IfcMotorConnectionTypeEnum, 'BELTDRIVE', INDETERMINATE)
coupling = getattr(IfcMotorConnectionTypeEnum, 'COUPLING', INDETERMINATE)
directdrive = getattr(IfcMotorConnectionTypeEnum, 'DIRECTDRIVE', INDETERMINATE)
userdefined = getattr(IfcMotorConnectionTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcMotorConnectionTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcNullStyle = enum_namespace()
null = getattr(IfcNullStyle, 'NULL', INDETERMINATE)
IfcObjectTypeEnum = enum_namespace()
product = getattr(IfcObjectTypeEnum, 'PRODUCT', INDETERMINATE)
process = getattr(IfcObjectTypeEnum, 'PROCESS', INDETERMINATE)
control = getattr(IfcObjectTypeEnum, 'CONTROL', INDETERMINATE)
resource = getattr(IfcObjectTypeEnum, 'RESOURCE', INDETERMINATE)
actor = getattr(IfcObjectTypeEnum, 'ACTOR', INDETERMINATE)
group = getattr(IfcObjectTypeEnum, 'GROUP', INDETERMINATE)
project = getattr(IfcObjectTypeEnum, 'PROJECT', INDETERMINATE)
notdefined = getattr(IfcObjectTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcObjectiveEnum = enum_namespace()
codecompliance = getattr(IfcObjectiveEnum, 'CODECOMPLIANCE', INDETERMINATE)
codewaiver = getattr(IfcObjectiveEnum, 'CODEWAIVER', INDETERMINATE)
designintent = getattr(IfcObjectiveEnum, 'DESIGNINTENT', INDETERMINATE)
external = getattr(IfcObjectiveEnum, 'EXTERNAL', INDETERMINATE)
healthandsafety = getattr(IfcObjectiveEnum, 'HEALTHANDSAFETY', INDETERMINATE)
mergeconflict = getattr(IfcObjectiveEnum, 'MERGECONFLICT', INDETERMINATE)
modelview = getattr(IfcObjectiveEnum, 'MODELVIEW', INDETERMINATE)
parameter = getattr(IfcObjectiveEnum, 'PARAMETER', INDETERMINATE)
requirement = getattr(IfcObjectiveEnum, 'REQUIREMENT', INDETERMINATE)
specification = getattr(IfcObjectiveEnum, 'SPECIFICATION', INDETERMINATE)
triggercondition = getattr(IfcObjectiveEnum, 'TRIGGERCONDITION', INDETERMINATE)
userdefined = getattr(IfcObjectiveEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcObjectiveEnum, 'NOTDEFINED', INDETERMINATE)
IfcOccupantTypeEnum = enum_namespace()
assignee = getattr(IfcOccupantTypeEnum, 'ASSIGNEE', INDETERMINATE)
assignor = getattr(IfcOccupantTypeEnum, 'ASSIGNOR', INDETERMINATE)
lessee = getattr(IfcOccupantTypeEnum, 'LESSEE', INDETERMINATE)
lessor = getattr(IfcOccupantTypeEnum, 'LESSOR', INDETERMINATE)
lettingagent = getattr(IfcOccupantTypeEnum, 'LETTINGAGENT', INDETERMINATE)
owner = getattr(IfcOccupantTypeEnum, 'OWNER', INDETERMINATE)
tenant = getattr(IfcOccupantTypeEnum, 'TENANT', INDETERMINATE)
userdefined = getattr(IfcOccupantTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcOccupantTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcOpeningElementTypeEnum = enum_namespace()
opening = getattr(IfcOpeningElementTypeEnum, 'OPENING', INDETERMINATE)
recess = getattr(IfcOpeningElementTypeEnum, 'RECESS', INDETERMINATE)
userdefined = getattr(IfcOpeningElementTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcOpeningElementTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcOutletTypeEnum = enum_namespace()
audiovisualoutlet = getattr(IfcOutletTypeEnum, 'AUDIOVISUALOUTLET', INDETERMINATE)
communicationsoutlet = getattr(IfcOutletTypeEnum, 'COMMUNICATIONSOUTLET', INDETERMINATE)
poweroutlet = getattr(IfcOutletTypeEnum, 'POWEROUTLET', INDETERMINATE)
dataoutlet = getattr(IfcOutletTypeEnum, 'DATAOUTLET', INDETERMINATE)
telephoneoutlet = getattr(IfcOutletTypeEnum, 'TELEPHONEOUTLET', INDETERMINATE)
userdefined = getattr(IfcOutletTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcOutletTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcPerformanceHistoryTypeEnum = enum_namespace()
userdefined = getattr(IfcPerformanceHistoryTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcPerformanceHistoryTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcPermeableCoveringOperationEnum = enum_namespace()
grill = getattr(IfcPermeableCoveringOperationEnum, 'GRILL', INDETERMINATE)
louver = getattr(IfcPermeableCoveringOperationEnum, 'LOUVER', INDETERMINATE)
screen = getattr(IfcPermeableCoveringOperationEnum, 'SCREEN', INDETERMINATE)
userdefined = getattr(IfcPermeableCoveringOperationEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcPermeableCoveringOperationEnum, 'NOTDEFINED', INDETERMINATE)
IfcPermitTypeEnum = enum_namespace()
access = getattr(IfcPermitTypeEnum, 'ACCESS', INDETERMINATE)
building = getattr(IfcPermitTypeEnum, 'BUILDING', INDETERMINATE)
work = getattr(IfcPermitTypeEnum, 'WORK', INDETERMINATE)
userdefined = getattr(IfcPermitTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcPermitTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcPhysicalOrVirtualEnum = enum_namespace()
physical = getattr(IfcPhysicalOrVirtualEnum, 'PHYSICAL', INDETERMINATE)
virtual = getattr(IfcPhysicalOrVirtualEnum, 'VIRTUAL', INDETERMINATE)
notdefined = getattr(IfcPhysicalOrVirtualEnum, 'NOTDEFINED', INDETERMINATE)
IfcPileConstructionEnum = enum_namespace()
cast_in_place = getattr(IfcPileConstructionEnum, 'CAST_IN_PLACE', INDETERMINATE)
composite = getattr(IfcPileConstructionEnum, 'COMPOSITE', INDETERMINATE)
precast_concrete = getattr(IfcPileConstructionEnum, 'PRECAST_CONCRETE', INDETERMINATE)
prefab_steel = getattr(IfcPileConstructionEnum, 'PREFAB_STEEL', INDETERMINATE)
userdefined = getattr(IfcPileConstructionEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcPileConstructionEnum, 'NOTDEFINED', INDETERMINATE)
IfcPileTypeEnum = enum_namespace()
bored = getattr(IfcPileTypeEnum, 'BORED', INDETERMINATE)
driven = getattr(IfcPileTypeEnum, 'DRIVEN', INDETERMINATE)
jetgrouting = getattr(IfcPileTypeEnum, 'JETGROUTING', INDETERMINATE)
cohesion = getattr(IfcPileTypeEnum, 'COHESION', INDETERMINATE)
friction = getattr(IfcPileTypeEnum, 'FRICTION', INDETERMINATE)
support = getattr(IfcPileTypeEnum, 'SUPPORT', INDETERMINATE)
userdefined = getattr(IfcPileTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcPileTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcPipeFittingTypeEnum = enum_namespace()
bend = getattr(IfcPipeFittingTypeEnum, 'BEND', INDETERMINATE)
connector = getattr(IfcPipeFittingTypeEnum, 'CONNECTOR', INDETERMINATE)
entry = getattr(IfcPipeFittingTypeEnum, 'ENTRY', INDETERMINATE)
exit = getattr(IfcPipeFittingTypeEnum, 'EXIT', INDETERMINATE)
junction = getattr(IfcPipeFittingTypeEnum, 'JUNCTION', INDETERMINATE)
obstruction = getattr(IfcPipeFittingTypeEnum, 'OBSTRUCTION', INDETERMINATE)
transition = getattr(IfcPipeFittingTypeEnum, 'TRANSITION', INDETERMINATE)
userdefined = getattr(IfcPipeFittingTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcPipeFittingTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcPipeSegmentTypeEnum = enum_namespace()
culvert = getattr(IfcPipeSegmentTypeEnum, 'CULVERT', INDETERMINATE)
flexiblesegment = getattr(IfcPipeSegmentTypeEnum, 'FLEXIBLESEGMENT', INDETERMINATE)
rigidsegment = getattr(IfcPipeSegmentTypeEnum, 'RIGIDSEGMENT', INDETERMINATE)
gutter = getattr(IfcPipeSegmentTypeEnum, 'GUTTER', INDETERMINATE)
spool = getattr(IfcPipeSegmentTypeEnum, 'SPOOL', INDETERMINATE)
userdefined = getattr(IfcPipeSegmentTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcPipeSegmentTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcPlateTypeEnum = enum_namespace()
curtain_panel = getattr(IfcPlateTypeEnum, 'CURTAIN_PANEL', INDETERMINATE)
sheet = getattr(IfcPlateTypeEnum, 'SHEET', INDETERMINATE)
userdefined = getattr(IfcPlateTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcPlateTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcPreferredSurfaceCurveRepresentation = enum_namespace()
curve3d = getattr(IfcPreferredSurfaceCurveRepresentation, 'CURVE3D', INDETERMINATE)
pcurve_s1 = getattr(IfcPreferredSurfaceCurveRepresentation, 'PCURVE_S1', INDETERMINATE)
pcurve_s2 = getattr(IfcPreferredSurfaceCurveRepresentation, 'PCURVE_S2', INDETERMINATE)
IfcProcedureTypeEnum = enum_namespace()
advice_caution = getattr(IfcProcedureTypeEnum, 'ADVICE_CAUTION', INDETERMINATE)
advice_note = getattr(IfcProcedureTypeEnum, 'ADVICE_NOTE', INDETERMINATE)
advice_warning = getattr(IfcProcedureTypeEnum, 'ADVICE_WARNING', INDETERMINATE)
calibration = getattr(IfcProcedureTypeEnum, 'CALIBRATION', INDETERMINATE)
diagnostic = getattr(IfcProcedureTypeEnum, 'DIAGNOSTIC', INDETERMINATE)
shutdown = getattr(IfcProcedureTypeEnum, 'SHUTDOWN', INDETERMINATE)
startup = getattr(IfcProcedureTypeEnum, 'STARTUP', INDETERMINATE)
userdefined = getattr(IfcProcedureTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcProcedureTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcProfileTypeEnum = enum_namespace()
curve = getattr(IfcProfileTypeEnum, 'CURVE', INDETERMINATE)
area = getattr(IfcProfileTypeEnum, 'AREA', INDETERMINATE)
IfcProjectOrderTypeEnum = enum_namespace()
changeorder = getattr(IfcProjectOrderTypeEnum, 'CHANGEORDER', INDETERMINATE)
maintenanceworkorder = getattr(IfcProjectOrderTypeEnum, 'MAINTENANCEWORKORDER', INDETERMINATE)
moveorder = getattr(IfcProjectOrderTypeEnum, 'MOVEORDER', INDETERMINATE)
purchaseorder = getattr(IfcProjectOrderTypeEnum, 'PURCHASEORDER', INDETERMINATE)
workorder = getattr(IfcProjectOrderTypeEnum, 'WORKORDER', INDETERMINATE)
userdefined = getattr(IfcProjectOrderTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcProjectOrderTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcProjectedOrTrueLengthEnum = enum_namespace()
projected_length = getattr(IfcProjectedOrTrueLengthEnum, 'PROJECTED_LENGTH', INDETERMINATE)
true_length = getattr(IfcProjectedOrTrueLengthEnum, 'TRUE_LENGTH', INDETERMINATE)
IfcProjectionElementTypeEnum = enum_namespace()
userdefined = getattr(IfcProjectionElementTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcProjectionElementTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcPropertySetTemplateTypeEnum = enum_namespace()
pset_typedrivenonly = getattr(IfcPropertySetTemplateTypeEnum, 'PSET_TYPEDRIVENONLY', INDETERMINATE)
pset_typedrivenoverride = getattr(IfcPropertySetTemplateTypeEnum, 'PSET_TYPEDRIVENOVERRIDE', INDETERMINATE)
pset_occurrencedriven = getattr(IfcPropertySetTemplateTypeEnum, 'PSET_OCCURRENCEDRIVEN', INDETERMINATE)
pset_performancedriven = getattr(IfcPropertySetTemplateTypeEnum, 'PSET_PERFORMANCEDRIVEN', INDETERMINATE)
qto_typedrivenonly = getattr(IfcPropertySetTemplateTypeEnum, 'QTO_TYPEDRIVENONLY', INDETERMINATE)
qto_typedrivenoverride = getattr(IfcPropertySetTemplateTypeEnum, 'QTO_TYPEDRIVENOVERRIDE', INDETERMINATE)
qto_occurrencedriven = getattr(IfcPropertySetTemplateTypeEnum, 'QTO_OCCURRENCEDRIVEN', INDETERMINATE)
notdefined = getattr(IfcPropertySetTemplateTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcProtectiveDeviceTrippingUnitTypeEnum = enum_namespace()
electronic = getattr(IfcProtectiveDeviceTrippingUnitTypeEnum, 'ELECTRONIC', INDETERMINATE)
electromagnetic = getattr(IfcProtectiveDeviceTrippingUnitTypeEnum, 'ELECTROMAGNETIC', INDETERMINATE)
residualcurrent = getattr(IfcProtectiveDeviceTrippingUnitTypeEnum, 'RESIDUALCURRENT', INDETERMINATE)
thermal = getattr(IfcProtectiveDeviceTrippingUnitTypeEnum, 'THERMAL', INDETERMINATE)
userdefined = getattr(IfcProtectiveDeviceTrippingUnitTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcProtectiveDeviceTrippingUnitTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcProtectiveDeviceTypeEnum = enum_namespace()
circuitbreaker = getattr(IfcProtectiveDeviceTypeEnum, 'CIRCUITBREAKER', INDETERMINATE)
earthleakagecircuitbreaker = getattr(IfcProtectiveDeviceTypeEnum, 'EARTHLEAKAGECIRCUITBREAKER', INDETERMINATE)
earthingswitch = getattr(IfcProtectiveDeviceTypeEnum, 'EARTHINGSWITCH', INDETERMINATE)
fusedisconnector = getattr(IfcProtectiveDeviceTypeEnum, 'FUSEDISCONNECTOR', INDETERMINATE)
residualcurrentcircuitbreaker = getattr(IfcProtectiveDeviceTypeEnum, 'RESIDUALCURRENTCIRCUITBREAKER', INDETERMINATE)
residualcurrentswitch = getattr(IfcProtectiveDeviceTypeEnum, 'RESIDUALCURRENTSWITCH', INDETERMINATE)
varistor = getattr(IfcProtectiveDeviceTypeEnum, 'VARISTOR', INDETERMINATE)
userdefined = getattr(IfcProtectiveDeviceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcProtectiveDeviceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcPumpTypeEnum = enum_namespace()
circulator = getattr(IfcPumpTypeEnum, 'CIRCULATOR', INDETERMINATE)
endsuction = getattr(IfcPumpTypeEnum, 'ENDSUCTION', INDETERMINATE)
splitcase = getattr(IfcPumpTypeEnum, 'SPLITCASE', INDETERMINATE)
submersiblepump = getattr(IfcPumpTypeEnum, 'SUBMERSIBLEPUMP', INDETERMINATE)
sumppump = getattr(IfcPumpTypeEnum, 'SUMPPUMP', INDETERMINATE)
verticalinline = getattr(IfcPumpTypeEnum, 'VERTICALINLINE', INDETERMINATE)
verticalturbine = getattr(IfcPumpTypeEnum, 'VERTICALTURBINE', INDETERMINATE)
userdefined = getattr(IfcPumpTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcPumpTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcRailingTypeEnum = enum_namespace()
handrail = getattr(IfcRailingTypeEnum, 'HANDRAIL', INDETERMINATE)
guardrail = getattr(IfcRailingTypeEnum, 'GUARDRAIL', INDETERMINATE)
balustrade = getattr(IfcRailingTypeEnum, 'BALUSTRADE', INDETERMINATE)
userdefined = getattr(IfcRailingTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcRailingTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcRampFlightTypeEnum = enum_namespace()
straight = getattr(IfcRampFlightTypeEnum, 'STRAIGHT', INDETERMINATE)
spiral = getattr(IfcRampFlightTypeEnum, 'SPIRAL', INDETERMINATE)
userdefined = getattr(IfcRampFlightTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcRampFlightTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcRampTypeEnum = enum_namespace()
straight_run_ramp = getattr(IfcRampTypeEnum, 'STRAIGHT_RUN_RAMP', INDETERMINATE)
two_straight_run_ramp = getattr(IfcRampTypeEnum, 'TWO_STRAIGHT_RUN_RAMP', INDETERMINATE)
quarter_turn_ramp = getattr(IfcRampTypeEnum, 'QUARTER_TURN_RAMP', INDETERMINATE)
two_quarter_turn_ramp = getattr(IfcRampTypeEnum, 'TWO_QUARTER_TURN_RAMP', INDETERMINATE)
half_turn_ramp = getattr(IfcRampTypeEnum, 'HALF_TURN_RAMP', INDETERMINATE)
spiral_ramp = getattr(IfcRampTypeEnum, 'SPIRAL_RAMP', INDETERMINATE)
userdefined = getattr(IfcRampTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcRampTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcRecurrenceTypeEnum = enum_namespace()
daily = getattr(IfcRecurrenceTypeEnum, 'DAILY', INDETERMINATE)
weekly = getattr(IfcRecurrenceTypeEnum, 'WEEKLY', INDETERMINATE)
monthly_by_day_of_month = getattr(IfcRecurrenceTypeEnum, 'MONTHLY_BY_DAY_OF_MONTH', INDETERMINATE)
monthly_by_position = getattr(IfcRecurrenceTypeEnum, 'MONTHLY_BY_POSITION', INDETERMINATE)
by_day_count = getattr(IfcRecurrenceTypeEnum, 'BY_DAY_COUNT', INDETERMINATE)
by_weekday_count = getattr(IfcRecurrenceTypeEnum, 'BY_WEEKDAY_COUNT', INDETERMINATE)
yearly_by_day_of_month = getattr(IfcRecurrenceTypeEnum, 'YEARLY_BY_DAY_OF_MONTH', INDETERMINATE)
yearly_by_position = getattr(IfcRecurrenceTypeEnum, 'YEARLY_BY_POSITION', INDETERMINATE)
IfcReferentTypeEnum = enum_namespace()
kilopoint = getattr(IfcReferentTypeEnum, 'KILOPOINT', INDETERMINATE)
milepoint = getattr(IfcReferentTypeEnum, 'MILEPOINT', INDETERMINATE)
station = getattr(IfcReferentTypeEnum, 'STATION', INDETERMINATE)
userdefined = getattr(IfcReferentTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcReferentTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcReflectanceMethodEnum = enum_namespace()
blinn = getattr(IfcReflectanceMethodEnum, 'BLINN', INDETERMINATE)
flat = getattr(IfcReflectanceMethodEnum, 'FLAT', INDETERMINATE)
glass = getattr(IfcReflectanceMethodEnum, 'GLASS', INDETERMINATE)
matt = getattr(IfcReflectanceMethodEnum, 'MATT', INDETERMINATE)
metal = getattr(IfcReflectanceMethodEnum, 'METAL', INDETERMINATE)
mirror = getattr(IfcReflectanceMethodEnum, 'MIRROR', INDETERMINATE)
phong = getattr(IfcReflectanceMethodEnum, 'PHONG', INDETERMINATE)
plastic = getattr(IfcReflectanceMethodEnum, 'PLASTIC', INDETERMINATE)
strauss = getattr(IfcReflectanceMethodEnum, 'STRAUSS', INDETERMINATE)
notdefined = getattr(IfcReflectanceMethodEnum, 'NOTDEFINED', INDETERMINATE)
IfcReinforcingBarRoleEnum = enum_namespace()
main = getattr(IfcReinforcingBarRoleEnum, 'MAIN', INDETERMINATE)
shear = getattr(IfcReinforcingBarRoleEnum, 'SHEAR', INDETERMINATE)
ligature = getattr(IfcReinforcingBarRoleEnum, 'LIGATURE', INDETERMINATE)
stud = getattr(IfcReinforcingBarRoleEnum, 'STUD', INDETERMINATE)
punching = getattr(IfcReinforcingBarRoleEnum, 'PUNCHING', INDETERMINATE)
edge = getattr(IfcReinforcingBarRoleEnum, 'EDGE', INDETERMINATE)
ring = getattr(IfcReinforcingBarRoleEnum, 'RING', INDETERMINATE)
anchoring = getattr(IfcReinforcingBarRoleEnum, 'ANCHORING', INDETERMINATE)
userdefined = getattr(IfcReinforcingBarRoleEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcReinforcingBarRoleEnum, 'NOTDEFINED', INDETERMINATE)
IfcReinforcingBarSurfaceEnum = enum_namespace()
plain = getattr(IfcReinforcingBarSurfaceEnum, 'PLAIN', INDETERMINATE)
textured = getattr(IfcReinforcingBarSurfaceEnum, 'TEXTURED', INDETERMINATE)
IfcReinforcingBarTypeEnum = enum_namespace()
anchoring = getattr(IfcReinforcingBarTypeEnum, 'ANCHORING', INDETERMINATE)
edge = getattr(IfcReinforcingBarTypeEnum, 'EDGE', INDETERMINATE)
ligature = getattr(IfcReinforcingBarTypeEnum, 'LIGATURE', INDETERMINATE)
main = getattr(IfcReinforcingBarTypeEnum, 'MAIN', INDETERMINATE)
punching = getattr(IfcReinforcingBarTypeEnum, 'PUNCHING', INDETERMINATE)
ring = getattr(IfcReinforcingBarTypeEnum, 'RING', INDETERMINATE)
shear = getattr(IfcReinforcingBarTypeEnum, 'SHEAR', INDETERMINATE)
stud = getattr(IfcReinforcingBarTypeEnum, 'STUD', INDETERMINATE)
userdefined = getattr(IfcReinforcingBarTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcReinforcingBarTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcReinforcingMeshTypeEnum = enum_namespace()
userdefined = getattr(IfcReinforcingMeshTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcReinforcingMeshTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcRoleEnum = enum_namespace()
supplier = getattr(IfcRoleEnum, 'SUPPLIER', INDETERMINATE)
manufacturer = getattr(IfcRoleEnum, 'MANUFACTURER', INDETERMINATE)
contractor = getattr(IfcRoleEnum, 'CONTRACTOR', INDETERMINATE)
subcontractor = getattr(IfcRoleEnum, 'SUBCONTRACTOR', INDETERMINATE)
architect = getattr(IfcRoleEnum, 'ARCHITECT', INDETERMINATE)
structuralengineer = getattr(IfcRoleEnum, 'STRUCTURALENGINEER', INDETERMINATE)
costengineer = getattr(IfcRoleEnum, 'COSTENGINEER', INDETERMINATE)
client = getattr(IfcRoleEnum, 'CLIENT', INDETERMINATE)
buildingowner = getattr(IfcRoleEnum, 'BUILDINGOWNER', INDETERMINATE)
buildingoperator = getattr(IfcRoleEnum, 'BUILDINGOPERATOR', INDETERMINATE)
mechanicalengineer = getattr(IfcRoleEnum, 'MECHANICALENGINEER', INDETERMINATE)
electricalengineer = getattr(IfcRoleEnum, 'ELECTRICALENGINEER', INDETERMINATE)
projectmanager = getattr(IfcRoleEnum, 'PROJECTMANAGER', INDETERMINATE)
facilitiesmanager = getattr(IfcRoleEnum, 'FACILITIESMANAGER', INDETERMINATE)
civilengineer = getattr(IfcRoleEnum, 'CIVILENGINEER', INDETERMINATE)
commissioningengineer = getattr(IfcRoleEnum, 'COMMISSIONINGENGINEER', INDETERMINATE)
engineer = getattr(IfcRoleEnum, 'ENGINEER', INDETERMINATE)
owner = getattr(IfcRoleEnum, 'OWNER', INDETERMINATE)
consultant = getattr(IfcRoleEnum, 'CONSULTANT', INDETERMINATE)
constructionmanager = getattr(IfcRoleEnum, 'CONSTRUCTIONMANAGER', INDETERMINATE)
fieldconstructionmanager = getattr(IfcRoleEnum, 'FIELDCONSTRUCTIONMANAGER', INDETERMINATE)
reseller = getattr(IfcRoleEnum, 'RESELLER', INDETERMINATE)
userdefined = getattr(IfcRoleEnum, 'USERDEFINED', INDETERMINATE)
IfcRoofTypeEnum = enum_namespace()
flat_roof = getattr(IfcRoofTypeEnum, 'FLAT_ROOF', INDETERMINATE)
shed_roof = getattr(IfcRoofTypeEnum, 'SHED_ROOF', INDETERMINATE)
gable_roof = getattr(IfcRoofTypeEnum, 'GABLE_ROOF', INDETERMINATE)
hip_roof = getattr(IfcRoofTypeEnum, 'HIP_ROOF', INDETERMINATE)
hipped_gable_roof = getattr(IfcRoofTypeEnum, 'HIPPED_GABLE_ROOF', INDETERMINATE)
gambrel_roof = getattr(IfcRoofTypeEnum, 'GAMBREL_ROOF', INDETERMINATE)
mansard_roof = getattr(IfcRoofTypeEnum, 'MANSARD_ROOF', INDETERMINATE)
barrel_roof = getattr(IfcRoofTypeEnum, 'BARREL_ROOF', INDETERMINATE)
rainbow_roof = getattr(IfcRoofTypeEnum, 'RAINBOW_ROOF', INDETERMINATE)
butterfly_roof = getattr(IfcRoofTypeEnum, 'BUTTERFLY_ROOF', INDETERMINATE)
pavilion_roof = getattr(IfcRoofTypeEnum, 'PAVILION_ROOF', INDETERMINATE)
dome_roof = getattr(IfcRoofTypeEnum, 'DOME_ROOF', INDETERMINATE)
freeform = getattr(IfcRoofTypeEnum, 'FREEFORM', INDETERMINATE)
userdefined = getattr(IfcRoofTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcRoofTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcSIPrefix = enum_namespace()
exa = getattr(IfcSIPrefix, 'EXA', INDETERMINATE)
peta = getattr(IfcSIPrefix, 'PETA', INDETERMINATE)
tera = getattr(IfcSIPrefix, 'TERA', INDETERMINATE)
giga = getattr(IfcSIPrefix, 'GIGA', INDETERMINATE)
mega = getattr(IfcSIPrefix, 'MEGA', INDETERMINATE)
kilo = getattr(IfcSIPrefix, 'KILO', INDETERMINATE)
hecto = getattr(IfcSIPrefix, 'HECTO', INDETERMINATE)
deca = getattr(IfcSIPrefix, 'DECA', INDETERMINATE)
deci = getattr(IfcSIPrefix, 'DECI', INDETERMINATE)
centi = getattr(IfcSIPrefix, 'CENTI', INDETERMINATE)
milli = getattr(IfcSIPrefix, 'MILLI', INDETERMINATE)
micro = getattr(IfcSIPrefix, 'MICRO', INDETERMINATE)
nano = getattr(IfcSIPrefix, 'NANO', INDETERMINATE)
pico = getattr(IfcSIPrefix, 'PICO', INDETERMINATE)
femto = getattr(IfcSIPrefix, 'FEMTO', INDETERMINATE)
atto = getattr(IfcSIPrefix, 'ATTO', INDETERMINATE)
IfcSIUnitName = enum_namespace()
ampere = getattr(IfcSIUnitName, 'AMPERE', INDETERMINATE)
becquerel = getattr(IfcSIUnitName, 'BECQUEREL', INDETERMINATE)
candela = getattr(IfcSIUnitName, 'CANDELA', INDETERMINATE)
coulomb = getattr(IfcSIUnitName, 'COULOMB', INDETERMINATE)
cubic_metre = getattr(IfcSIUnitName, 'CUBIC_METRE', INDETERMINATE)
degree_celsius = getattr(IfcSIUnitName, 'DEGREE_CELSIUS', INDETERMINATE)
farad = getattr(IfcSIUnitName, 'FARAD', INDETERMINATE)
gram = getattr(IfcSIUnitName, 'GRAM', INDETERMINATE)
gray = getattr(IfcSIUnitName, 'GRAY', INDETERMINATE)
henry = getattr(IfcSIUnitName, 'HENRY', INDETERMINATE)
hertz = getattr(IfcSIUnitName, 'HERTZ', INDETERMINATE)
joule = getattr(IfcSIUnitName, 'JOULE', INDETERMINATE)
kelvin = getattr(IfcSIUnitName, 'KELVIN', INDETERMINATE)
lumen = getattr(IfcSIUnitName, 'LUMEN', INDETERMINATE)
lux = getattr(IfcSIUnitName, 'LUX', INDETERMINATE)
metre = getattr(IfcSIUnitName, 'METRE', INDETERMINATE)
mole = getattr(IfcSIUnitName, 'MOLE', INDETERMINATE)
newton = getattr(IfcSIUnitName, 'NEWTON', INDETERMINATE)
ohm = getattr(IfcSIUnitName, 'OHM', INDETERMINATE)
pascal = getattr(IfcSIUnitName, 'PASCAL', INDETERMINATE)
radian = getattr(IfcSIUnitName, 'RADIAN', INDETERMINATE)
second = getattr(IfcSIUnitName, 'SECOND', INDETERMINATE)
siemens = getattr(IfcSIUnitName, 'SIEMENS', INDETERMINATE)
sievert = getattr(IfcSIUnitName, 'SIEVERT', INDETERMINATE)
square_metre = getattr(IfcSIUnitName, 'SQUARE_METRE', INDETERMINATE)
steradian = getattr(IfcSIUnitName, 'STERADIAN', INDETERMINATE)
tesla = getattr(IfcSIUnitName, 'TESLA', INDETERMINATE)
volt = getattr(IfcSIUnitName, 'VOLT', INDETERMINATE)
watt = getattr(IfcSIUnitName, 'WATT', INDETERMINATE)
weber = getattr(IfcSIUnitName, 'WEBER', INDETERMINATE)
IfcSanitaryTerminalTypeEnum = enum_namespace()
bath = getattr(IfcSanitaryTerminalTypeEnum, 'BATH', INDETERMINATE)
bidet = getattr(IfcSanitaryTerminalTypeEnum, 'BIDET', INDETERMINATE)
cistern = getattr(IfcSanitaryTerminalTypeEnum, 'CISTERN', INDETERMINATE)
shower = getattr(IfcSanitaryTerminalTypeEnum, 'SHOWER', INDETERMINATE)
sink = getattr(IfcSanitaryTerminalTypeEnum, 'SINK', INDETERMINATE)
sanitaryfountain = getattr(IfcSanitaryTerminalTypeEnum, 'SANITARYFOUNTAIN', INDETERMINATE)
toiletpan = getattr(IfcSanitaryTerminalTypeEnum, 'TOILETPAN', INDETERMINATE)
urinal = getattr(IfcSanitaryTerminalTypeEnum, 'URINAL', INDETERMINATE)
washhandbasin = getattr(IfcSanitaryTerminalTypeEnum, 'WASHHANDBASIN', INDETERMINATE)
wcseat = getattr(IfcSanitaryTerminalTypeEnum, 'WCSEAT', INDETERMINATE)
userdefined = getattr(IfcSanitaryTerminalTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcSanitaryTerminalTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcSectionTypeEnum = enum_namespace()
uniform = getattr(IfcSectionTypeEnum, 'UNIFORM', INDETERMINATE)
tapered = getattr(IfcSectionTypeEnum, 'TAPERED', INDETERMINATE)
IfcSensorTypeEnum = enum_namespace()
cosensor = getattr(IfcSensorTypeEnum, 'COSENSOR', INDETERMINATE)
co2sensor = getattr(IfcSensorTypeEnum, 'CO2SENSOR', INDETERMINATE)
conductancesensor = getattr(IfcSensorTypeEnum, 'CONDUCTANCESENSOR', INDETERMINATE)
contactsensor = getattr(IfcSensorTypeEnum, 'CONTACTSENSOR', INDETERMINATE)
firesensor = getattr(IfcSensorTypeEnum, 'FIRESENSOR', INDETERMINATE)
flowsensor = getattr(IfcSensorTypeEnum, 'FLOWSENSOR', INDETERMINATE)
frostsensor = getattr(IfcSensorTypeEnum, 'FROSTSENSOR', INDETERMINATE)
gassensor = getattr(IfcSensorTypeEnum, 'GASSENSOR', INDETERMINATE)
heatsensor = getattr(IfcSensorTypeEnum, 'HEATSENSOR', INDETERMINATE)
humiditysensor = getattr(IfcSensorTypeEnum, 'HUMIDITYSENSOR', INDETERMINATE)
identifiersensor = getattr(IfcSensorTypeEnum, 'IDENTIFIERSENSOR', INDETERMINATE)
ionconcentrationsensor = getattr(IfcSensorTypeEnum, 'IONCONCENTRATIONSENSOR', INDETERMINATE)
levelsensor = getattr(IfcSensorTypeEnum, 'LEVELSENSOR', INDETERMINATE)
lightsensor = getattr(IfcSensorTypeEnum, 'LIGHTSENSOR', INDETERMINATE)
moisturesensor = getattr(IfcSensorTypeEnum, 'MOISTURESENSOR', INDETERMINATE)
movementsensor = getattr(IfcSensorTypeEnum, 'MOVEMENTSENSOR', INDETERMINATE)
phsensor = getattr(IfcSensorTypeEnum, 'PHSENSOR', INDETERMINATE)
pressuresensor = getattr(IfcSensorTypeEnum, 'PRESSURESENSOR', INDETERMINATE)
radiationsensor = getattr(IfcSensorTypeEnum, 'RADIATIONSENSOR', INDETERMINATE)
radioactivitysensor = getattr(IfcSensorTypeEnum, 'RADIOACTIVITYSENSOR', INDETERMINATE)
smokesensor = getattr(IfcSensorTypeEnum, 'SMOKESENSOR', INDETERMINATE)
soundsensor = getattr(IfcSensorTypeEnum, 'SOUNDSENSOR', INDETERMINATE)
temperaturesensor = getattr(IfcSensorTypeEnum, 'TEMPERATURESENSOR', INDETERMINATE)
windsensor = getattr(IfcSensorTypeEnum, 'WINDSENSOR', INDETERMINATE)
userdefined = getattr(IfcSensorTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcSensorTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcSequenceEnum = enum_namespace()
start_start = getattr(IfcSequenceEnum, 'START_START', INDETERMINATE)
start_finish = getattr(IfcSequenceEnum, 'START_FINISH', INDETERMINATE)
finish_start = getattr(IfcSequenceEnum, 'FINISH_START', INDETERMINATE)
finish_finish = getattr(IfcSequenceEnum, 'FINISH_FINISH', INDETERMINATE)
userdefined = getattr(IfcSequenceEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcSequenceEnum, 'NOTDEFINED', INDETERMINATE)
IfcShadingDeviceTypeEnum = enum_namespace()
jalousie = getattr(IfcShadingDeviceTypeEnum, 'JALOUSIE', INDETERMINATE)
shutter = getattr(IfcShadingDeviceTypeEnum, 'SHUTTER', INDETERMINATE)
awning = getattr(IfcShadingDeviceTypeEnum, 'AWNING', INDETERMINATE)
userdefined = getattr(IfcShadingDeviceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcShadingDeviceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcSimplePropertyTemplateTypeEnum = enum_namespace()
p_singlevalue = getattr(IfcSimplePropertyTemplateTypeEnum, 'P_SINGLEVALUE', INDETERMINATE)
p_enumeratedvalue = getattr(IfcSimplePropertyTemplateTypeEnum, 'P_ENUMERATEDVALUE', INDETERMINATE)
p_boundedvalue = getattr(IfcSimplePropertyTemplateTypeEnum, 'P_BOUNDEDVALUE', INDETERMINATE)
p_listvalue = getattr(IfcSimplePropertyTemplateTypeEnum, 'P_LISTVALUE', INDETERMINATE)
p_tablevalue = getattr(IfcSimplePropertyTemplateTypeEnum, 'P_TABLEVALUE', INDETERMINATE)
p_referencevalue = getattr(IfcSimplePropertyTemplateTypeEnum, 'P_REFERENCEVALUE', INDETERMINATE)
q_length = getattr(IfcSimplePropertyTemplateTypeEnum, 'Q_LENGTH', INDETERMINATE)
q_area = getattr(IfcSimplePropertyTemplateTypeEnum, 'Q_AREA', INDETERMINATE)
q_volume = getattr(IfcSimplePropertyTemplateTypeEnum, 'Q_VOLUME', INDETERMINATE)
q_count = getattr(IfcSimplePropertyTemplateTypeEnum, 'Q_COUNT', INDETERMINATE)
q_weight = getattr(IfcSimplePropertyTemplateTypeEnum, 'Q_WEIGHT', INDETERMINATE)
q_time = getattr(IfcSimplePropertyTemplateTypeEnum, 'Q_TIME', INDETERMINATE)
IfcSlabTypeEnum = enum_namespace()
floor = getattr(IfcSlabTypeEnum, 'FLOOR', INDETERMINATE)
roof = getattr(IfcSlabTypeEnum, 'ROOF', INDETERMINATE)
landing = getattr(IfcSlabTypeEnum, 'LANDING', INDETERMINATE)
baseslab = getattr(IfcSlabTypeEnum, 'BASESLAB', INDETERMINATE)
userdefined = getattr(IfcSlabTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcSlabTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcSolarDeviceTypeEnum = enum_namespace()
solarcollector = getattr(IfcSolarDeviceTypeEnum, 'SOLARCOLLECTOR', INDETERMINATE)
solarpanel = getattr(IfcSolarDeviceTypeEnum, 'SOLARPANEL', INDETERMINATE)
userdefined = getattr(IfcSolarDeviceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcSolarDeviceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcSpaceHeaterTypeEnum = enum_namespace()
convector = getattr(IfcSpaceHeaterTypeEnum, 'CONVECTOR', INDETERMINATE)
radiator = getattr(IfcSpaceHeaterTypeEnum, 'RADIATOR', INDETERMINATE)
userdefined = getattr(IfcSpaceHeaterTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcSpaceHeaterTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcSpaceTypeEnum = enum_namespace()
space = getattr(IfcSpaceTypeEnum, 'SPACE', INDETERMINATE)
parking = getattr(IfcSpaceTypeEnum, 'PARKING', INDETERMINATE)
gfa = getattr(IfcSpaceTypeEnum, 'GFA', INDETERMINATE)
internal = getattr(IfcSpaceTypeEnum, 'INTERNAL', INDETERMINATE)
external = getattr(IfcSpaceTypeEnum, 'EXTERNAL', INDETERMINATE)
userdefined = getattr(IfcSpaceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcSpaceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcSpatialZoneTypeEnum = enum_namespace()
construction = getattr(IfcSpatialZoneTypeEnum, 'CONSTRUCTION', INDETERMINATE)
firesafety = getattr(IfcSpatialZoneTypeEnum, 'FIRESAFETY', INDETERMINATE)
lighting = getattr(IfcSpatialZoneTypeEnum, 'LIGHTING', INDETERMINATE)
occupancy = getattr(IfcSpatialZoneTypeEnum, 'OCCUPANCY', INDETERMINATE)
security = getattr(IfcSpatialZoneTypeEnum, 'SECURITY', INDETERMINATE)
thermal = getattr(IfcSpatialZoneTypeEnum, 'THERMAL', INDETERMINATE)
transport = getattr(IfcSpatialZoneTypeEnum, 'TRANSPORT', INDETERMINATE)
ventilation = getattr(IfcSpatialZoneTypeEnum, 'VENTILATION', INDETERMINATE)
userdefined = getattr(IfcSpatialZoneTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcSpatialZoneTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcStackTerminalTypeEnum = enum_namespace()
birdcage = getattr(IfcStackTerminalTypeEnum, 'BIRDCAGE', INDETERMINATE)
cowl = getattr(IfcStackTerminalTypeEnum, 'COWL', INDETERMINATE)
rainwaterhopper = getattr(IfcStackTerminalTypeEnum, 'RAINWATERHOPPER', INDETERMINATE)
userdefined = getattr(IfcStackTerminalTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcStackTerminalTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcStairFlightTypeEnum = enum_namespace()
straight = getattr(IfcStairFlightTypeEnum, 'STRAIGHT', INDETERMINATE)
winder = getattr(IfcStairFlightTypeEnum, 'WINDER', INDETERMINATE)
spiral = getattr(IfcStairFlightTypeEnum, 'SPIRAL', INDETERMINATE)
curved = getattr(IfcStairFlightTypeEnum, 'CURVED', INDETERMINATE)
freeform = getattr(IfcStairFlightTypeEnum, 'FREEFORM', INDETERMINATE)
userdefined = getattr(IfcStairFlightTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcStairFlightTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcStairTypeEnum = enum_namespace()
straight_run_stair = getattr(IfcStairTypeEnum, 'STRAIGHT_RUN_STAIR', INDETERMINATE)
two_straight_run_stair = getattr(IfcStairTypeEnum, 'TWO_STRAIGHT_RUN_STAIR', INDETERMINATE)
quarter_winding_stair = getattr(IfcStairTypeEnum, 'QUARTER_WINDING_STAIR', INDETERMINATE)
quarter_turn_stair = getattr(IfcStairTypeEnum, 'QUARTER_TURN_STAIR', INDETERMINATE)
half_winding_stair = getattr(IfcStairTypeEnum, 'HALF_WINDING_STAIR', INDETERMINATE)
half_turn_stair = getattr(IfcStairTypeEnum, 'HALF_TURN_STAIR', INDETERMINATE)
two_quarter_winding_stair = getattr(IfcStairTypeEnum, 'TWO_QUARTER_WINDING_STAIR', INDETERMINATE)
two_quarter_turn_stair = getattr(IfcStairTypeEnum, 'TWO_QUARTER_TURN_STAIR', INDETERMINATE)
three_quarter_winding_stair = getattr(IfcStairTypeEnum, 'THREE_QUARTER_WINDING_STAIR', INDETERMINATE)
three_quarter_turn_stair = getattr(IfcStairTypeEnum, 'THREE_QUARTER_TURN_STAIR', INDETERMINATE)
spiral_stair = getattr(IfcStairTypeEnum, 'SPIRAL_STAIR', INDETERMINATE)
double_return_stair = getattr(IfcStairTypeEnum, 'DOUBLE_RETURN_STAIR', INDETERMINATE)
curved_run_stair = getattr(IfcStairTypeEnum, 'CURVED_RUN_STAIR', INDETERMINATE)
two_curved_run_stair = getattr(IfcStairTypeEnum, 'TWO_CURVED_RUN_STAIR', INDETERMINATE)
userdefined = getattr(IfcStairTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcStairTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcStateEnum = enum_namespace()
readwrite = getattr(IfcStateEnum, 'READWRITE', INDETERMINATE)
readonly = getattr(IfcStateEnum, 'READONLY', INDETERMINATE)
locked = getattr(IfcStateEnum, 'LOCKED', INDETERMINATE)
readwritelocked = getattr(IfcStateEnum, 'READWRITELOCKED', INDETERMINATE)
readonlylocked = getattr(IfcStateEnum, 'READONLYLOCKED', INDETERMINATE)
IfcStructuralCurveActivityTypeEnum = enum_namespace()
const = getattr(IfcStructuralCurveActivityTypeEnum, 'CONST', INDETERMINATE)
linear = getattr(IfcStructuralCurveActivityTypeEnum, 'LINEAR', INDETERMINATE)
polygonal = getattr(IfcStructuralCurveActivityTypeEnum, 'POLYGONAL', INDETERMINATE)
equidistant = getattr(IfcStructuralCurveActivityTypeEnum, 'EQUIDISTANT', INDETERMINATE)
sinus = getattr(IfcStructuralCurveActivityTypeEnum, 'SINUS', INDETERMINATE)
parabola = getattr(IfcStructuralCurveActivityTypeEnum, 'PARABOLA', INDETERMINATE)
discrete = getattr(IfcStructuralCurveActivityTypeEnum, 'DISCRETE', INDETERMINATE)
userdefined = getattr(IfcStructuralCurveActivityTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcStructuralCurveActivityTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcStructuralCurveMemberTypeEnum = enum_namespace()
rigid_joined_member = getattr(IfcStructuralCurveMemberTypeEnum, 'RIGID_JOINED_MEMBER', INDETERMINATE)
pin_joined_member = getattr(IfcStructuralCurveMemberTypeEnum, 'PIN_JOINED_MEMBER', INDETERMINATE)
cable = getattr(IfcStructuralCurveMemberTypeEnum, 'CABLE', INDETERMINATE)
tension_member = getattr(IfcStructuralCurveMemberTypeEnum, 'TENSION_MEMBER', INDETERMINATE)
compression_member = getattr(IfcStructuralCurveMemberTypeEnum, 'COMPRESSION_MEMBER', INDETERMINATE)
userdefined = getattr(IfcStructuralCurveMemberTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcStructuralCurveMemberTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcStructuralSurfaceActivityTypeEnum = enum_namespace()
const = getattr(IfcStructuralSurfaceActivityTypeEnum, 'CONST', INDETERMINATE)
bilinear = getattr(IfcStructuralSurfaceActivityTypeEnum, 'BILINEAR', INDETERMINATE)
discrete = getattr(IfcStructuralSurfaceActivityTypeEnum, 'DISCRETE', INDETERMINATE)
isocontour = getattr(IfcStructuralSurfaceActivityTypeEnum, 'ISOCONTOUR', INDETERMINATE)
userdefined = getattr(IfcStructuralSurfaceActivityTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcStructuralSurfaceActivityTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcStructuralSurfaceMemberTypeEnum = enum_namespace()
bending_element = getattr(IfcStructuralSurfaceMemberTypeEnum, 'BENDING_ELEMENT', INDETERMINATE)
membrane_element = getattr(IfcStructuralSurfaceMemberTypeEnum, 'MEMBRANE_ELEMENT', INDETERMINATE)
shell = getattr(IfcStructuralSurfaceMemberTypeEnum, 'SHELL', INDETERMINATE)
userdefined = getattr(IfcStructuralSurfaceMemberTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcStructuralSurfaceMemberTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcSubContractResourceTypeEnum = enum_namespace()
purchase = getattr(IfcSubContractResourceTypeEnum, 'PURCHASE', INDETERMINATE)
work = getattr(IfcSubContractResourceTypeEnum, 'WORK', INDETERMINATE)
userdefined = getattr(IfcSubContractResourceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcSubContractResourceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcSurfaceFeatureTypeEnum = enum_namespace()
mark = getattr(IfcSurfaceFeatureTypeEnum, 'MARK', INDETERMINATE)
tag = getattr(IfcSurfaceFeatureTypeEnum, 'TAG', INDETERMINATE)
treatment = getattr(IfcSurfaceFeatureTypeEnum, 'TREATMENT', INDETERMINATE)
userdefined = getattr(IfcSurfaceFeatureTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcSurfaceFeatureTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcSurfaceSide = enum_namespace()
positive = getattr(IfcSurfaceSide, 'POSITIVE', INDETERMINATE)
negative = getattr(IfcSurfaceSide, 'NEGATIVE', INDETERMINATE)
both = getattr(IfcSurfaceSide, 'BOTH', INDETERMINATE)
IfcSwitchingDeviceTypeEnum = enum_namespace()
contactor = getattr(IfcSwitchingDeviceTypeEnum, 'CONTACTOR', INDETERMINATE)
dimmerswitch = getattr(IfcSwitchingDeviceTypeEnum, 'DIMMERSWITCH', INDETERMINATE)
emergencystop = getattr(IfcSwitchingDeviceTypeEnum, 'EMERGENCYSTOP', INDETERMINATE)
keypad = getattr(IfcSwitchingDeviceTypeEnum, 'KEYPAD', INDETERMINATE)
momentaryswitch = getattr(IfcSwitchingDeviceTypeEnum, 'MOMENTARYSWITCH', INDETERMINATE)
selectorswitch = getattr(IfcSwitchingDeviceTypeEnum, 'SELECTORSWITCH', INDETERMINATE)
starter = getattr(IfcSwitchingDeviceTypeEnum, 'STARTER', INDETERMINATE)
switchdisconnector = getattr(IfcSwitchingDeviceTypeEnum, 'SWITCHDISCONNECTOR', INDETERMINATE)
toggleswitch = getattr(IfcSwitchingDeviceTypeEnum, 'TOGGLESWITCH', INDETERMINATE)
userdefined = getattr(IfcSwitchingDeviceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcSwitchingDeviceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcSystemFurnitureElementTypeEnum = enum_namespace()
panel = getattr(IfcSystemFurnitureElementTypeEnum, 'PANEL', INDETERMINATE)
worksurface = getattr(IfcSystemFurnitureElementTypeEnum, 'WORKSURFACE', INDETERMINATE)
userdefined = getattr(IfcSystemFurnitureElementTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcSystemFurnitureElementTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcTankTypeEnum = enum_namespace()
basin = getattr(IfcTankTypeEnum, 'BASIN', INDETERMINATE)
breakpressure = getattr(IfcTankTypeEnum, 'BREAKPRESSURE', INDETERMINATE)
expansion = getattr(IfcTankTypeEnum, 'EXPANSION', INDETERMINATE)
feedandexpansion = getattr(IfcTankTypeEnum, 'FEEDANDEXPANSION', INDETERMINATE)
pressurevessel = getattr(IfcTankTypeEnum, 'PRESSUREVESSEL', INDETERMINATE)
storage = getattr(IfcTankTypeEnum, 'STORAGE', INDETERMINATE)
vessel = getattr(IfcTankTypeEnum, 'VESSEL', INDETERMINATE)
userdefined = getattr(IfcTankTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcTankTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcTaskDurationEnum = enum_namespace()
elapsedtime = getattr(IfcTaskDurationEnum, 'ELAPSEDTIME', INDETERMINATE)
worktime = getattr(IfcTaskDurationEnum, 'WORKTIME', INDETERMINATE)
notdefined = getattr(IfcTaskDurationEnum, 'NOTDEFINED', INDETERMINATE)
IfcTaskTypeEnum = enum_namespace()
attendance = getattr(IfcTaskTypeEnum, 'ATTENDANCE', INDETERMINATE)
construction = getattr(IfcTaskTypeEnum, 'CONSTRUCTION', INDETERMINATE)
demolition = getattr(IfcTaskTypeEnum, 'DEMOLITION', INDETERMINATE)
dismantle = getattr(IfcTaskTypeEnum, 'DISMANTLE', INDETERMINATE)
disposal = getattr(IfcTaskTypeEnum, 'DISPOSAL', INDETERMINATE)
installation = getattr(IfcTaskTypeEnum, 'INSTALLATION', INDETERMINATE)
logistic = getattr(IfcTaskTypeEnum, 'LOGISTIC', INDETERMINATE)
maintenance = getattr(IfcTaskTypeEnum, 'MAINTENANCE', INDETERMINATE)
move = getattr(IfcTaskTypeEnum, 'MOVE', INDETERMINATE)
operation = getattr(IfcTaskTypeEnum, 'OPERATION', INDETERMINATE)
removal = getattr(IfcTaskTypeEnum, 'REMOVAL', INDETERMINATE)
renovation = getattr(IfcTaskTypeEnum, 'RENOVATION', INDETERMINATE)
userdefined = getattr(IfcTaskTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcTaskTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcTendonAnchorTypeEnum = enum_namespace()
coupler = getattr(IfcTendonAnchorTypeEnum, 'COUPLER', INDETERMINATE)
fixed_end = getattr(IfcTendonAnchorTypeEnum, 'FIXED_END', INDETERMINATE)
tensioning_end = getattr(IfcTendonAnchorTypeEnum, 'TENSIONING_END', INDETERMINATE)
userdefined = getattr(IfcTendonAnchorTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcTendonAnchorTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcTendonTypeEnum = enum_namespace()
bar = getattr(IfcTendonTypeEnum, 'BAR', INDETERMINATE)
coated = getattr(IfcTendonTypeEnum, 'COATED', INDETERMINATE)
strand = getattr(IfcTendonTypeEnum, 'STRAND', INDETERMINATE)
wire = getattr(IfcTendonTypeEnum, 'WIRE', INDETERMINATE)
userdefined = getattr(IfcTendonTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcTendonTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcTextPath = enum_namespace()
left = getattr(IfcTextPath, 'LEFT', INDETERMINATE)
right = getattr(IfcTextPath, 'RIGHT', INDETERMINATE)
up = getattr(IfcTextPath, 'UP', INDETERMINATE)
down = getattr(IfcTextPath, 'DOWN', INDETERMINATE)
IfcTimeSeriesDataTypeEnum = enum_namespace()
continuous = getattr(IfcTimeSeriesDataTypeEnum, 'CONTINUOUS', INDETERMINATE)
discrete = getattr(IfcTimeSeriesDataTypeEnum, 'DISCRETE', INDETERMINATE)
discretebinary = getattr(IfcTimeSeriesDataTypeEnum, 'DISCRETEBINARY', INDETERMINATE)
piecewisebinary = getattr(IfcTimeSeriesDataTypeEnum, 'PIECEWISEBINARY', INDETERMINATE)
piecewiseconstant = getattr(IfcTimeSeriesDataTypeEnum, 'PIECEWISECONSTANT', INDETERMINATE)
piecewisecontinuous = getattr(IfcTimeSeriesDataTypeEnum, 'PIECEWISECONTINUOUS', INDETERMINATE)
notdefined = getattr(IfcTimeSeriesDataTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcTransformerTypeEnum = enum_namespace()
current = getattr(IfcTransformerTypeEnum, 'CURRENT', INDETERMINATE)
frequency = getattr(IfcTransformerTypeEnum, 'FREQUENCY', INDETERMINATE)
inverter = getattr(IfcTransformerTypeEnum, 'INVERTER', INDETERMINATE)
rectifier = getattr(IfcTransformerTypeEnum, 'RECTIFIER', INDETERMINATE)
voltage = getattr(IfcTransformerTypeEnum, 'VOLTAGE', INDETERMINATE)
userdefined = getattr(IfcTransformerTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcTransformerTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcTransitionCode = enum_namespace()
discontinuous = getattr(IfcTransitionCode, 'DISCONTINUOUS', INDETERMINATE)
continuous = getattr(IfcTransitionCode, 'CONTINUOUS', INDETERMINATE)
contsamegradient = getattr(IfcTransitionCode, 'CONTSAMEGRADIENT', INDETERMINATE)
contsamegradientsamecurvature = getattr(IfcTransitionCode, 'CONTSAMEGRADIENTSAMECURVATURE', INDETERMINATE)
IfcTransitionCurveType = enum_namespace()
biquadraticparabola = getattr(IfcTransitionCurveType, 'BIQUADRATICPARABOLA', INDETERMINATE)
blosscurve = getattr(IfcTransitionCurveType, 'BLOSSCURVE', INDETERMINATE)
clothoidcurve = getattr(IfcTransitionCurveType, 'CLOTHOIDCURVE', INDETERMINATE)
cosinecurve = getattr(IfcTransitionCurveType, 'COSINECURVE', INDETERMINATE)
cubicparabola = getattr(IfcTransitionCurveType, 'CUBICPARABOLA', INDETERMINATE)
sinecurve = getattr(IfcTransitionCurveType, 'SINECURVE', INDETERMINATE)
IfcTransportElementTypeEnum = enum_namespace()
elevator = getattr(IfcTransportElementTypeEnum, 'ELEVATOR', INDETERMINATE)
escalator = getattr(IfcTransportElementTypeEnum, 'ESCALATOR', INDETERMINATE)
movingwalkway = getattr(IfcTransportElementTypeEnum, 'MOVINGWALKWAY', INDETERMINATE)
craneway = getattr(IfcTransportElementTypeEnum, 'CRANEWAY', INDETERMINATE)
liftinggear = getattr(IfcTransportElementTypeEnum, 'LIFTINGGEAR', INDETERMINATE)
userdefined = getattr(IfcTransportElementTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcTransportElementTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcTrimmingPreference = enum_namespace()
cartesian = getattr(IfcTrimmingPreference, 'CARTESIAN', INDETERMINATE)
parameter = getattr(IfcTrimmingPreference, 'PARAMETER', INDETERMINATE)
unspecified = getattr(IfcTrimmingPreference, 'UNSPECIFIED', INDETERMINATE)
IfcTubeBundleTypeEnum = enum_namespace()
finned = getattr(IfcTubeBundleTypeEnum, 'FINNED', INDETERMINATE)
userdefined = getattr(IfcTubeBundleTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcTubeBundleTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcUnitEnum = enum_namespace()
absorbeddoseunit = getattr(IfcUnitEnum, 'ABSORBEDDOSEUNIT', INDETERMINATE)
amountofsubstanceunit = getattr(IfcUnitEnum, 'AMOUNTOFSUBSTANCEUNIT', INDETERMINATE)
areaunit = getattr(IfcUnitEnum, 'AREAUNIT', INDETERMINATE)
doseequivalentunit = getattr(IfcUnitEnum, 'DOSEEQUIVALENTUNIT', INDETERMINATE)
electriccapacitanceunit = getattr(IfcUnitEnum, 'ELECTRICCAPACITANCEUNIT', INDETERMINATE)
electricchargeunit = getattr(IfcUnitEnum, 'ELECTRICCHARGEUNIT', INDETERMINATE)
electricconductanceunit = getattr(IfcUnitEnum, 'ELECTRICCONDUCTANCEUNIT', INDETERMINATE)
electriccurrentunit = getattr(IfcUnitEnum, 'ELECTRICCURRENTUNIT', INDETERMINATE)
electricresistanceunit = getattr(IfcUnitEnum, 'ELECTRICRESISTANCEUNIT', INDETERMINATE)
electricvoltageunit = getattr(IfcUnitEnum, 'ELECTRICVOLTAGEUNIT', INDETERMINATE)
energyunit = getattr(IfcUnitEnum, 'ENERGYUNIT', INDETERMINATE)
forceunit = getattr(IfcUnitEnum, 'FORCEUNIT', INDETERMINATE)
frequencyunit = getattr(IfcUnitEnum, 'FREQUENCYUNIT', INDETERMINATE)
illuminanceunit = getattr(IfcUnitEnum, 'ILLUMINANCEUNIT', INDETERMINATE)
inductanceunit = getattr(IfcUnitEnum, 'INDUCTANCEUNIT', INDETERMINATE)
lengthunit = getattr(IfcUnitEnum, 'LENGTHUNIT', INDETERMINATE)
luminousfluxunit = getattr(IfcUnitEnum, 'LUMINOUSFLUXUNIT', INDETERMINATE)
luminousintensityunit = getattr(IfcUnitEnum, 'LUMINOUSINTENSITYUNIT', INDETERMINATE)
magneticfluxdensityunit = getattr(IfcUnitEnum, 'MAGNETICFLUXDENSITYUNIT', INDETERMINATE)
magneticfluxunit = getattr(IfcUnitEnum, 'MAGNETICFLUXUNIT', INDETERMINATE)
massunit = getattr(IfcUnitEnum, 'MASSUNIT', INDETERMINATE)
planeangleunit = getattr(IfcUnitEnum, 'PLANEANGLEUNIT', INDETERMINATE)
powerunit = getattr(IfcUnitEnum, 'POWERUNIT', INDETERMINATE)
pressureunit = getattr(IfcUnitEnum, 'PRESSUREUNIT', INDETERMINATE)
radioactivityunit = getattr(IfcUnitEnum, 'RADIOACTIVITYUNIT', INDETERMINATE)
solidangleunit = getattr(IfcUnitEnum, 'SOLIDANGLEUNIT', INDETERMINATE)
thermodynamictemperatureunit = getattr(IfcUnitEnum, 'THERMODYNAMICTEMPERATUREUNIT', INDETERMINATE)
timeunit = getattr(IfcUnitEnum, 'TIMEUNIT', INDETERMINATE)
volumeunit = getattr(IfcUnitEnum, 'VOLUMEUNIT', INDETERMINATE)
userdefined = getattr(IfcUnitEnum, 'USERDEFINED', INDETERMINATE)
IfcUnitaryControlElementTypeEnum = enum_namespace()
alarmpanel = getattr(IfcUnitaryControlElementTypeEnum, 'ALARMPANEL', INDETERMINATE)
controlpanel = getattr(IfcUnitaryControlElementTypeEnum, 'CONTROLPANEL', INDETERMINATE)
gasdetectionpanel = getattr(IfcUnitaryControlElementTypeEnum, 'GASDETECTIONPANEL', INDETERMINATE)
indicatorpanel = getattr(IfcUnitaryControlElementTypeEnum, 'INDICATORPANEL', INDETERMINATE)
mimicpanel = getattr(IfcUnitaryControlElementTypeEnum, 'MIMICPANEL', INDETERMINATE)
humidistat = getattr(IfcUnitaryControlElementTypeEnum, 'HUMIDISTAT', INDETERMINATE)
thermostat = getattr(IfcUnitaryControlElementTypeEnum, 'THERMOSTAT', INDETERMINATE)
weatherstation = getattr(IfcUnitaryControlElementTypeEnum, 'WEATHERSTATION', INDETERMINATE)
userdefined = getattr(IfcUnitaryControlElementTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcUnitaryControlElementTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcUnitaryEquipmentTypeEnum = enum_namespace()
airhandler = getattr(IfcUnitaryEquipmentTypeEnum, 'AIRHANDLER', INDETERMINATE)
airconditioningunit = getattr(IfcUnitaryEquipmentTypeEnum, 'AIRCONDITIONINGUNIT', INDETERMINATE)
dehumidifier = getattr(IfcUnitaryEquipmentTypeEnum, 'DEHUMIDIFIER', INDETERMINATE)
splitsystem = getattr(IfcUnitaryEquipmentTypeEnum, 'SPLITSYSTEM', INDETERMINATE)
rooftopunit = getattr(IfcUnitaryEquipmentTypeEnum, 'ROOFTOPUNIT', INDETERMINATE)
userdefined = getattr(IfcUnitaryEquipmentTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcUnitaryEquipmentTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcValveTypeEnum = enum_namespace()
airrelease = getattr(IfcValveTypeEnum, 'AIRRELEASE', INDETERMINATE)
antivacuum = getattr(IfcValveTypeEnum, 'ANTIVACUUM', INDETERMINATE)
changeover = getattr(IfcValveTypeEnum, 'CHANGEOVER', INDETERMINATE)
check = getattr(IfcValveTypeEnum, 'CHECK', INDETERMINATE)
commissioning = getattr(IfcValveTypeEnum, 'COMMISSIONING', INDETERMINATE)
diverting = getattr(IfcValveTypeEnum, 'DIVERTING', INDETERMINATE)
drawoffcock = getattr(IfcValveTypeEnum, 'DRAWOFFCOCK', INDETERMINATE)
doublecheck = getattr(IfcValveTypeEnum, 'DOUBLECHECK', INDETERMINATE)
doubleregulating = getattr(IfcValveTypeEnum, 'DOUBLEREGULATING', INDETERMINATE)
faucet = getattr(IfcValveTypeEnum, 'FAUCET', INDETERMINATE)
flushing = getattr(IfcValveTypeEnum, 'FLUSHING', INDETERMINATE)
gascock = getattr(IfcValveTypeEnum, 'GASCOCK', INDETERMINATE)
gastap = getattr(IfcValveTypeEnum, 'GASTAP', INDETERMINATE)
isolating = getattr(IfcValveTypeEnum, 'ISOLATING', INDETERMINATE)
mixing = getattr(IfcValveTypeEnum, 'MIXING', INDETERMINATE)
pressurereducing = getattr(IfcValveTypeEnum, 'PRESSUREREDUCING', INDETERMINATE)
pressurerelief = getattr(IfcValveTypeEnum, 'PRESSURERELIEF', INDETERMINATE)
regulating = getattr(IfcValveTypeEnum, 'REGULATING', INDETERMINATE)
safetycutoff = getattr(IfcValveTypeEnum, 'SAFETYCUTOFF', INDETERMINATE)
steamtrap = getattr(IfcValveTypeEnum, 'STEAMTRAP', INDETERMINATE)
stopcock = getattr(IfcValveTypeEnum, 'STOPCOCK', INDETERMINATE)
userdefined = getattr(IfcValveTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcValveTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcVibrationIsolatorTypeEnum = enum_namespace()
compression = getattr(IfcVibrationIsolatorTypeEnum, 'COMPRESSION', INDETERMINATE)
spring = getattr(IfcVibrationIsolatorTypeEnum, 'SPRING', INDETERMINATE)
userdefined = getattr(IfcVibrationIsolatorTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcVibrationIsolatorTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcVoidingFeatureTypeEnum = enum_namespace()
cutout = getattr(IfcVoidingFeatureTypeEnum, 'CUTOUT', INDETERMINATE)
notch = getattr(IfcVoidingFeatureTypeEnum, 'NOTCH', INDETERMINATE)
hole = getattr(IfcVoidingFeatureTypeEnum, 'HOLE', INDETERMINATE)
miter = getattr(IfcVoidingFeatureTypeEnum, 'MITER', INDETERMINATE)
chamfer = getattr(IfcVoidingFeatureTypeEnum, 'CHAMFER', INDETERMINATE)
edge = getattr(IfcVoidingFeatureTypeEnum, 'EDGE', INDETERMINATE)
userdefined = getattr(IfcVoidingFeatureTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcVoidingFeatureTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcWallTypeEnum = enum_namespace()
movable = getattr(IfcWallTypeEnum, 'MOVABLE', INDETERMINATE)
parapet = getattr(IfcWallTypeEnum, 'PARAPET', INDETERMINATE)
partitioning = getattr(IfcWallTypeEnum, 'PARTITIONING', INDETERMINATE)
plumbingwall = getattr(IfcWallTypeEnum, 'PLUMBINGWALL', INDETERMINATE)
shear = getattr(IfcWallTypeEnum, 'SHEAR', INDETERMINATE)
solidwall = getattr(IfcWallTypeEnum, 'SOLIDWALL', INDETERMINATE)
standard = getattr(IfcWallTypeEnum, 'STANDARD', INDETERMINATE)
polygonal = getattr(IfcWallTypeEnum, 'POLYGONAL', INDETERMINATE)
elementedwall = getattr(IfcWallTypeEnum, 'ELEMENTEDWALL', INDETERMINATE)
userdefined = getattr(IfcWallTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcWallTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcWasteTerminalTypeEnum = enum_namespace()
floortrap = getattr(IfcWasteTerminalTypeEnum, 'FLOORTRAP', INDETERMINATE)
floorwaste = getattr(IfcWasteTerminalTypeEnum, 'FLOORWASTE', INDETERMINATE)
gullysump = getattr(IfcWasteTerminalTypeEnum, 'GULLYSUMP', INDETERMINATE)
gullytrap = getattr(IfcWasteTerminalTypeEnum, 'GULLYTRAP', INDETERMINATE)
roofdrain = getattr(IfcWasteTerminalTypeEnum, 'ROOFDRAIN', INDETERMINATE)
wastedisposalunit = getattr(IfcWasteTerminalTypeEnum, 'WASTEDISPOSALUNIT', INDETERMINATE)
wastetrap = getattr(IfcWasteTerminalTypeEnum, 'WASTETRAP', INDETERMINATE)
userdefined = getattr(IfcWasteTerminalTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcWasteTerminalTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcWindowPanelOperationEnum = enum_namespace()
sidehungrighthand = getattr(IfcWindowPanelOperationEnum, 'SIDEHUNGRIGHTHAND', INDETERMINATE)
sidehunglefthand = getattr(IfcWindowPanelOperationEnum, 'SIDEHUNGLEFTHAND', INDETERMINATE)
tiltandturnrighthand = getattr(IfcWindowPanelOperationEnum, 'TILTANDTURNRIGHTHAND', INDETERMINATE)
tiltandturnlefthand = getattr(IfcWindowPanelOperationEnum, 'TILTANDTURNLEFTHAND', INDETERMINATE)
tophung = getattr(IfcWindowPanelOperationEnum, 'TOPHUNG', INDETERMINATE)
bottomhung = getattr(IfcWindowPanelOperationEnum, 'BOTTOMHUNG', INDETERMINATE)
pivothorizontal = getattr(IfcWindowPanelOperationEnum, 'PIVOTHORIZONTAL', INDETERMINATE)
pivotvertical = getattr(IfcWindowPanelOperationEnum, 'PIVOTVERTICAL', INDETERMINATE)
slidinghorizontal = getattr(IfcWindowPanelOperationEnum, 'SLIDINGHORIZONTAL', INDETERMINATE)
slidingvertical = getattr(IfcWindowPanelOperationEnum, 'SLIDINGVERTICAL', INDETERMINATE)
removablecasement = getattr(IfcWindowPanelOperationEnum, 'REMOVABLECASEMENT', INDETERMINATE)
fixedcasement = getattr(IfcWindowPanelOperationEnum, 'FIXEDCASEMENT', INDETERMINATE)
otheroperation = getattr(IfcWindowPanelOperationEnum, 'OTHEROPERATION', INDETERMINATE)
notdefined = getattr(IfcWindowPanelOperationEnum, 'NOTDEFINED', INDETERMINATE)
IfcWindowPanelPositionEnum = enum_namespace()
left = getattr(IfcWindowPanelPositionEnum, 'LEFT', INDETERMINATE)
middle = getattr(IfcWindowPanelPositionEnum, 'MIDDLE', INDETERMINATE)
right = getattr(IfcWindowPanelPositionEnum, 'RIGHT', INDETERMINATE)
bottom = getattr(IfcWindowPanelPositionEnum, 'BOTTOM', INDETERMINATE)
top = getattr(IfcWindowPanelPositionEnum, 'TOP', INDETERMINATE)
notdefined = getattr(IfcWindowPanelPositionEnum, 'NOTDEFINED', INDETERMINATE)
IfcWindowStyleConstructionEnum = enum_namespace()
aluminium = getattr(IfcWindowStyleConstructionEnum, 'ALUMINIUM', INDETERMINATE)
high_grade_steel = getattr(IfcWindowStyleConstructionEnum, 'HIGH_GRADE_STEEL', INDETERMINATE)
steel = getattr(IfcWindowStyleConstructionEnum, 'STEEL', INDETERMINATE)
wood = getattr(IfcWindowStyleConstructionEnum, 'WOOD', INDETERMINATE)
aluminium_wood = getattr(IfcWindowStyleConstructionEnum, 'ALUMINIUM_WOOD', INDETERMINATE)
plastic = getattr(IfcWindowStyleConstructionEnum, 'PLASTIC', INDETERMINATE)
other_construction = getattr(IfcWindowStyleConstructionEnum, 'OTHER_CONSTRUCTION', INDETERMINATE)
notdefined = getattr(IfcWindowStyleConstructionEnum, 'NOTDEFINED', INDETERMINATE)
IfcWindowStyleOperationEnum = enum_namespace()
single_panel = getattr(IfcWindowStyleOperationEnum, 'SINGLE_PANEL', INDETERMINATE)
double_panel_vertical = getattr(IfcWindowStyleOperationEnum, 'DOUBLE_PANEL_VERTICAL', INDETERMINATE)
double_panel_horizontal = getattr(IfcWindowStyleOperationEnum, 'DOUBLE_PANEL_HORIZONTAL', INDETERMINATE)
triple_panel_vertical = getattr(IfcWindowStyleOperationEnum, 'TRIPLE_PANEL_VERTICAL', INDETERMINATE)
triple_panel_bottom = getattr(IfcWindowStyleOperationEnum, 'TRIPLE_PANEL_BOTTOM', INDETERMINATE)
triple_panel_top = getattr(IfcWindowStyleOperationEnum, 'TRIPLE_PANEL_TOP', INDETERMINATE)
triple_panel_left = getattr(IfcWindowStyleOperationEnum, 'TRIPLE_PANEL_LEFT', INDETERMINATE)
triple_panel_right = getattr(IfcWindowStyleOperationEnum, 'TRIPLE_PANEL_RIGHT', INDETERMINATE)
triple_panel_horizontal = getattr(IfcWindowStyleOperationEnum, 'TRIPLE_PANEL_HORIZONTAL', INDETERMINATE)
userdefined = getattr(IfcWindowStyleOperationEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcWindowStyleOperationEnum, 'NOTDEFINED', INDETERMINATE)
IfcWindowTypeEnum = enum_namespace()
window = getattr(IfcWindowTypeEnum, 'WINDOW', INDETERMINATE)
skylight = getattr(IfcWindowTypeEnum, 'SKYLIGHT', INDETERMINATE)
lightdome = getattr(IfcWindowTypeEnum, 'LIGHTDOME', INDETERMINATE)
userdefined = getattr(IfcWindowTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcWindowTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcWindowTypePartitioningEnum = enum_namespace()
single_panel = getattr(IfcWindowTypePartitioningEnum, 'SINGLE_PANEL', INDETERMINATE)
double_panel_vertical = getattr(IfcWindowTypePartitioningEnum, 'DOUBLE_PANEL_VERTICAL', INDETERMINATE)
double_panel_horizontal = getattr(IfcWindowTypePartitioningEnum, 'DOUBLE_PANEL_HORIZONTAL', INDETERMINATE)
triple_panel_vertical = getattr(IfcWindowTypePartitioningEnum, 'TRIPLE_PANEL_VERTICAL', INDETERMINATE)
triple_panel_bottom = getattr(IfcWindowTypePartitioningEnum, 'TRIPLE_PANEL_BOTTOM', INDETERMINATE)
triple_panel_top = getattr(IfcWindowTypePartitioningEnum, 'TRIPLE_PANEL_TOP', INDETERMINATE)
triple_panel_left = getattr(IfcWindowTypePartitioningEnum, 'TRIPLE_PANEL_LEFT', INDETERMINATE)
triple_panel_right = getattr(IfcWindowTypePartitioningEnum, 'TRIPLE_PANEL_RIGHT', INDETERMINATE)
triple_panel_horizontal = getattr(IfcWindowTypePartitioningEnum, 'TRIPLE_PANEL_HORIZONTAL', INDETERMINATE)
userdefined = getattr(IfcWindowTypePartitioningEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcWindowTypePartitioningEnum, 'NOTDEFINED', INDETERMINATE)
IfcWorkCalendarTypeEnum = enum_namespace()
firstshift = getattr(IfcWorkCalendarTypeEnum, 'FIRSTSHIFT', INDETERMINATE)
secondshift = getattr(IfcWorkCalendarTypeEnum, 'SECONDSHIFT', INDETERMINATE)
thirdshift = getattr(IfcWorkCalendarTypeEnum, 'THIRDSHIFT', INDETERMINATE)
userdefined = getattr(IfcWorkCalendarTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcWorkCalendarTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcWorkPlanTypeEnum = enum_namespace()
actual = getattr(IfcWorkPlanTypeEnum, 'ACTUAL', INDETERMINATE)
baseline = getattr(IfcWorkPlanTypeEnum, 'BASELINE', INDETERMINATE)
planned = getattr(IfcWorkPlanTypeEnum, 'PLANNED', INDETERMINATE)
userdefined = getattr(IfcWorkPlanTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcWorkPlanTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcWorkScheduleTypeEnum = enum_namespace()
actual = getattr(IfcWorkScheduleTypeEnum, 'ACTUAL', INDETERMINATE)
baseline = getattr(IfcWorkScheduleTypeEnum, 'BASELINE', INDETERMINATE)
planned = getattr(IfcWorkScheduleTypeEnum, 'PLANNED', INDETERMINATE)
userdefined = getattr(IfcWorkScheduleTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcWorkScheduleTypeEnum, 'NOTDEFINED', INDETERMINATE)

def IfcActionRequest(*args, **kwargs):
    return ifcopenshell.create_entity('IfcActionRequest', 'IFC4X1', *args, **kwargs)

def IfcActor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcActor', 'IFC4X1', *args, **kwargs)

def IfcActorRole(*args, **kwargs):
    return ifcopenshell.create_entity('IfcActorRole', 'IFC4X1', *args, **kwargs)

def IfcActuator(*args, **kwargs):
    return ifcopenshell.create_entity('IfcActuator', 'IFC4X1', *args, **kwargs)

def IfcActuatorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcActuatorType', 'IFC4X1', *args, **kwargs)

def IfcAddress(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAddress', 'IFC4X1', *args, **kwargs)

def IfcAdvancedBrep(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAdvancedBrep', 'IFC4X1', *args, **kwargs)

def IfcAdvancedBrepWithVoids(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAdvancedBrepWithVoids', 'IFC4X1', *args, **kwargs)

def IfcAdvancedFace(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAdvancedFace', 'IFC4X1', *args, **kwargs)

def IfcAirTerminal(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAirTerminal', 'IFC4X1', *args, **kwargs)

def IfcAirTerminalBox(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAirTerminalBox', 'IFC4X1', *args, **kwargs)

def IfcAirTerminalBoxType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAirTerminalBoxType', 'IFC4X1', *args, **kwargs)

def IfcAirTerminalType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAirTerminalType', 'IFC4X1', *args, **kwargs)

def IfcAirToAirHeatRecovery(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAirToAirHeatRecovery', 'IFC4X1', *args, **kwargs)

def IfcAirToAirHeatRecoveryType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAirToAirHeatRecoveryType', 'IFC4X1', *args, **kwargs)

def IfcAlarm(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlarm', 'IFC4X1', *args, **kwargs)

def IfcAlarmType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlarmType', 'IFC4X1', *args, **kwargs)

def IfcAlignment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlignment', 'IFC4X1', *args, **kwargs)

def IfcAlignment2DHorizontal(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlignment2DHorizontal', 'IFC4X1', *args, **kwargs)

def IfcAlignment2DHorizontalSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlignment2DHorizontalSegment', 'IFC4X1', *args, **kwargs)

def IfcAlignment2DSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlignment2DSegment', 'IFC4X1', *args, **kwargs)

def IfcAlignment2DVerSegCircularArc(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlignment2DVerSegCircularArc', 'IFC4X1', *args, **kwargs)

def IfcAlignment2DVerSegLine(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlignment2DVerSegLine', 'IFC4X1', *args, **kwargs)

def IfcAlignment2DVerSegParabolicArc(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlignment2DVerSegParabolicArc', 'IFC4X1', *args, **kwargs)

def IfcAlignment2DVertical(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlignment2DVertical', 'IFC4X1', *args, **kwargs)

def IfcAlignment2DVerticalSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlignment2DVerticalSegment', 'IFC4X1', *args, **kwargs)

def IfcAlignmentCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlignmentCurve', 'IFC4X1', *args, **kwargs)

def IfcAnnotation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAnnotation', 'IFC4X1', *args, **kwargs)

def IfcAnnotationFillArea(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAnnotationFillArea', 'IFC4X1', *args, **kwargs)

def IfcApplication(*args, **kwargs):
    return ifcopenshell.create_entity('IfcApplication', 'IFC4X1', *args, **kwargs)

def IfcAppliedValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAppliedValue', 'IFC4X1', *args, **kwargs)

def IfcApproval(*args, **kwargs):
    return ifcopenshell.create_entity('IfcApproval', 'IFC4X1', *args, **kwargs)

def IfcApprovalRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcApprovalRelationship', 'IFC4X1', *args, **kwargs)

def IfcArbitraryClosedProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcArbitraryClosedProfileDef', 'IFC4X1', *args, **kwargs)

def IfcArbitraryOpenProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcArbitraryOpenProfileDef', 'IFC4X1', *args, **kwargs)

def IfcArbitraryProfileDefWithVoids(*args, **kwargs):
    return ifcopenshell.create_entity('IfcArbitraryProfileDefWithVoids', 'IFC4X1', *args, **kwargs)

def IfcAsset(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAsset', 'IFC4X1', *args, **kwargs)

def IfcAsymmetricIShapeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAsymmetricIShapeProfileDef', 'IFC4X1', *args, **kwargs)

def IfcAudioVisualAppliance(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAudioVisualAppliance', 'IFC4X1', *args, **kwargs)

def IfcAudioVisualApplianceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAudioVisualApplianceType', 'IFC4X1', *args, **kwargs)

def IfcAxis1Placement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAxis1Placement', 'IFC4X1', *args, **kwargs)

def IfcAxis2Placement2D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAxis2Placement2D', 'IFC4X1', *args, **kwargs)

def IfcAxis2Placement3D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAxis2Placement3D', 'IFC4X1', *args, **kwargs)

def IfcBSplineCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBSplineCurve', 'IFC4X1', *args, **kwargs)

def IfcBSplineCurveWithKnots(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBSplineCurveWithKnots', 'IFC4X1', *args, **kwargs)

def IfcBSplineSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBSplineSurface', 'IFC4X1', *args, **kwargs)

def IfcBSplineSurfaceWithKnots(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBSplineSurfaceWithKnots', 'IFC4X1', *args, **kwargs)

def IfcBeam(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBeam', 'IFC4X1', *args, **kwargs)

def IfcBeamStandardCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBeamStandardCase', 'IFC4X1', *args, **kwargs)

def IfcBeamType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBeamType', 'IFC4X1', *args, **kwargs)

def IfcBlobTexture(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBlobTexture', 'IFC4X1', *args, **kwargs)

def IfcBlock(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBlock', 'IFC4X1', *args, **kwargs)

def IfcBoiler(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoiler', 'IFC4X1', *args, **kwargs)

def IfcBoilerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoilerType', 'IFC4X1', *args, **kwargs)

def IfcBooleanClippingResult(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBooleanClippingResult', 'IFC4X1', *args, **kwargs)

def IfcBooleanResult(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBooleanResult', 'IFC4X1', *args, **kwargs)

def IfcBoundaryCondition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundaryCondition', 'IFC4X1', *args, **kwargs)

def IfcBoundaryCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundaryCurve', 'IFC4X1', *args, **kwargs)

def IfcBoundaryEdgeCondition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundaryEdgeCondition', 'IFC4X1', *args, **kwargs)

def IfcBoundaryFaceCondition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundaryFaceCondition', 'IFC4X1', *args, **kwargs)

def IfcBoundaryNodeCondition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundaryNodeCondition', 'IFC4X1', *args, **kwargs)

def IfcBoundaryNodeConditionWarping(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundaryNodeConditionWarping', 'IFC4X1', *args, **kwargs)

def IfcBoundedCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundedCurve', 'IFC4X1', *args, **kwargs)

def IfcBoundedSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundedSurface', 'IFC4X1', *args, **kwargs)

def IfcBoundingBox(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundingBox', 'IFC4X1', *args, **kwargs)

def IfcBoxedHalfSpace(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoxedHalfSpace', 'IFC4X1', *args, **kwargs)

def IfcBuilding(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuilding', 'IFC4X1', *args, **kwargs)

def IfcBuildingElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuildingElement', 'IFC4X1', *args, **kwargs)

def IfcBuildingElementPart(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuildingElementPart', 'IFC4X1', *args, **kwargs)

def IfcBuildingElementPartType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuildingElementPartType', 'IFC4X1', *args, **kwargs)

def IfcBuildingElementProxy(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuildingElementProxy', 'IFC4X1', *args, **kwargs)

def IfcBuildingElementProxyType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuildingElementProxyType', 'IFC4X1', *args, **kwargs)

def IfcBuildingElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuildingElementType', 'IFC4X1', *args, **kwargs)

def IfcBuildingStorey(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuildingStorey', 'IFC4X1', *args, **kwargs)

def IfcBuildingSystem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuildingSystem', 'IFC4X1', *args, **kwargs)

def IfcBurner(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBurner', 'IFC4X1', *args, **kwargs)

def IfcBurnerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBurnerType', 'IFC4X1', *args, **kwargs)

def IfcCShapeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCShapeProfileDef', 'IFC4X1', *args, **kwargs)

def IfcCableCarrierFitting(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCableCarrierFitting', 'IFC4X1', *args, **kwargs)

def IfcCableCarrierFittingType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCableCarrierFittingType', 'IFC4X1', *args, **kwargs)

def IfcCableCarrierSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCableCarrierSegment', 'IFC4X1', *args, **kwargs)

def IfcCableCarrierSegmentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCableCarrierSegmentType', 'IFC4X1', *args, **kwargs)

def IfcCableFitting(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCableFitting', 'IFC4X1', *args, **kwargs)

def IfcCableFittingType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCableFittingType', 'IFC4X1', *args, **kwargs)

def IfcCableSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCableSegment', 'IFC4X1', *args, **kwargs)

def IfcCableSegmentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCableSegmentType', 'IFC4X1', *args, **kwargs)

def IfcCartesianPoint(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianPoint', 'IFC4X1', *args, **kwargs)

def IfcCartesianPointList(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianPointList', 'IFC4X1', *args, **kwargs)

def IfcCartesianPointList2D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianPointList2D', 'IFC4X1', *args, **kwargs)

def IfcCartesianPointList3D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianPointList3D', 'IFC4X1', *args, **kwargs)

def IfcCartesianTransformationOperator(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianTransformationOperator', 'IFC4X1', *args, **kwargs)

def IfcCartesianTransformationOperator2D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianTransformationOperator2D', 'IFC4X1', *args, **kwargs)

def IfcCartesianTransformationOperator2DnonUniform(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianTransformationOperator2DnonUniform', 'IFC4X1', *args, **kwargs)

def IfcCartesianTransformationOperator3D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianTransformationOperator3D', 'IFC4X1', *args, **kwargs)

def IfcCartesianTransformationOperator3DnonUniform(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianTransformationOperator3DnonUniform', 'IFC4X1', *args, **kwargs)

def IfcCenterLineProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCenterLineProfileDef', 'IFC4X1', *args, **kwargs)

def IfcChiller(*args, **kwargs):
    return ifcopenshell.create_entity('IfcChiller', 'IFC4X1', *args, **kwargs)

def IfcChillerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcChillerType', 'IFC4X1', *args, **kwargs)

def IfcChimney(*args, **kwargs):
    return ifcopenshell.create_entity('IfcChimney', 'IFC4X1', *args, **kwargs)

def IfcChimneyType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcChimneyType', 'IFC4X1', *args, **kwargs)

def IfcCircle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCircle', 'IFC4X1', *args, **kwargs)

def IfcCircleHollowProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCircleHollowProfileDef', 'IFC4X1', *args, **kwargs)

def IfcCircleProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCircleProfileDef', 'IFC4X1', *args, **kwargs)

def IfcCircularArcSegment2D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCircularArcSegment2D', 'IFC4X1', *args, **kwargs)

def IfcCivilElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCivilElement', 'IFC4X1', *args, **kwargs)

def IfcCivilElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCivilElementType', 'IFC4X1', *args, **kwargs)

def IfcClassification(*args, **kwargs):
    return ifcopenshell.create_entity('IfcClassification', 'IFC4X1', *args, **kwargs)

def IfcClassificationReference(*args, **kwargs):
    return ifcopenshell.create_entity('IfcClassificationReference', 'IFC4X1', *args, **kwargs)

def IfcClosedShell(*args, **kwargs):
    return ifcopenshell.create_entity('IfcClosedShell', 'IFC4X1', *args, **kwargs)

def IfcCoil(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCoil', 'IFC4X1', *args, **kwargs)

def IfcCoilType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCoilType', 'IFC4X1', *args, **kwargs)

def IfcColourRgb(*args, **kwargs):
    return ifcopenshell.create_entity('IfcColourRgb', 'IFC4X1', *args, **kwargs)

def IfcColourRgbList(*args, **kwargs):
    return ifcopenshell.create_entity('IfcColourRgbList', 'IFC4X1', *args, **kwargs)

def IfcColourSpecification(*args, **kwargs):
    return ifcopenshell.create_entity('IfcColourSpecification', 'IFC4X1', *args, **kwargs)

def IfcColumn(*args, **kwargs):
    return ifcopenshell.create_entity('IfcColumn', 'IFC4X1', *args, **kwargs)

def IfcColumnStandardCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcColumnStandardCase', 'IFC4X1', *args, **kwargs)

def IfcColumnType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcColumnType', 'IFC4X1', *args, **kwargs)

def IfcCommunicationsAppliance(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCommunicationsAppliance', 'IFC4X1', *args, **kwargs)

def IfcCommunicationsApplianceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCommunicationsApplianceType', 'IFC4X1', *args, **kwargs)

def IfcComplexProperty(*args, **kwargs):
    return ifcopenshell.create_entity('IfcComplexProperty', 'IFC4X1', *args, **kwargs)

def IfcComplexPropertyTemplate(*args, **kwargs):
    return ifcopenshell.create_entity('IfcComplexPropertyTemplate', 'IFC4X1', *args, **kwargs)

def IfcCompositeCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCompositeCurve', 'IFC4X1', *args, **kwargs)

def IfcCompositeCurveOnSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCompositeCurveOnSurface', 'IFC4X1', *args, **kwargs)

def IfcCompositeCurveSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCompositeCurveSegment', 'IFC4X1', *args, **kwargs)

def IfcCompositeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCompositeProfileDef', 'IFC4X1', *args, **kwargs)

def IfcCompressor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCompressor', 'IFC4X1', *args, **kwargs)

def IfcCompressorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCompressorType', 'IFC4X1', *args, **kwargs)

def IfcCondenser(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCondenser', 'IFC4X1', *args, **kwargs)

def IfcCondenserType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCondenserType', 'IFC4X1', *args, **kwargs)

def IfcConic(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConic', 'IFC4X1', *args, **kwargs)

def IfcConnectedFaceSet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConnectedFaceSet', 'IFC4X1', *args, **kwargs)

def IfcConnectionCurveGeometry(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConnectionCurveGeometry', 'IFC4X1', *args, **kwargs)

def IfcConnectionGeometry(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConnectionGeometry', 'IFC4X1', *args, **kwargs)

def IfcConnectionPointEccentricity(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConnectionPointEccentricity', 'IFC4X1', *args, **kwargs)

def IfcConnectionPointGeometry(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConnectionPointGeometry', 'IFC4X1', *args, **kwargs)

def IfcConnectionSurfaceGeometry(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConnectionSurfaceGeometry', 'IFC4X1', *args, **kwargs)

def IfcConnectionVolumeGeometry(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConnectionVolumeGeometry', 'IFC4X1', *args, **kwargs)

def IfcConstraint(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstraint', 'IFC4X1', *args, **kwargs)

def IfcConstructionEquipmentResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstructionEquipmentResource', 'IFC4X1', *args, **kwargs)

def IfcConstructionEquipmentResourceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstructionEquipmentResourceType', 'IFC4X1', *args, **kwargs)

def IfcConstructionMaterialResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstructionMaterialResource', 'IFC4X1', *args, **kwargs)

def IfcConstructionMaterialResourceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstructionMaterialResourceType', 'IFC4X1', *args, **kwargs)

def IfcConstructionProductResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstructionProductResource', 'IFC4X1', *args, **kwargs)

def IfcConstructionProductResourceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstructionProductResourceType', 'IFC4X1', *args, **kwargs)

def IfcConstructionResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstructionResource', 'IFC4X1', *args, **kwargs)

def IfcConstructionResourceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstructionResourceType', 'IFC4X1', *args, **kwargs)

def IfcContext(*args, **kwargs):
    return ifcopenshell.create_entity('IfcContext', 'IFC4X1', *args, **kwargs)

def IfcContextDependentUnit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcContextDependentUnit', 'IFC4X1', *args, **kwargs)

def IfcControl(*args, **kwargs):
    return ifcopenshell.create_entity('IfcControl', 'IFC4X1', *args, **kwargs)

def IfcController(*args, **kwargs):
    return ifcopenshell.create_entity('IfcController', 'IFC4X1', *args, **kwargs)

def IfcControllerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcControllerType', 'IFC4X1', *args, **kwargs)

def IfcConversionBasedUnit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConversionBasedUnit', 'IFC4X1', *args, **kwargs)

def IfcConversionBasedUnitWithOffset(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConversionBasedUnitWithOffset', 'IFC4X1', *args, **kwargs)

def IfcCooledBeam(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCooledBeam', 'IFC4X1', *args, **kwargs)

def IfcCooledBeamType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCooledBeamType', 'IFC4X1', *args, **kwargs)

def IfcCoolingTower(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCoolingTower', 'IFC4X1', *args, **kwargs)

def IfcCoolingTowerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCoolingTowerType', 'IFC4X1', *args, **kwargs)

def IfcCoordinateOperation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCoordinateOperation', 'IFC4X1', *args, **kwargs)

def IfcCoordinateReferenceSystem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCoordinateReferenceSystem', 'IFC4X1', *args, **kwargs)

def IfcCostItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCostItem', 'IFC4X1', *args, **kwargs)

def IfcCostSchedule(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCostSchedule', 'IFC4X1', *args, **kwargs)

def IfcCostValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCostValue', 'IFC4X1', *args, **kwargs)

def IfcCovering(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCovering', 'IFC4X1', *args, **kwargs)

def IfcCoveringType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCoveringType', 'IFC4X1', *args, **kwargs)

def IfcCrewResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCrewResource', 'IFC4X1', *args, **kwargs)

def IfcCrewResourceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCrewResourceType', 'IFC4X1', *args, **kwargs)

def IfcCsgPrimitive3D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCsgPrimitive3D', 'IFC4X1', *args, **kwargs)

def IfcCsgSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCsgSolid', 'IFC4X1', *args, **kwargs)

def IfcCurrencyRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurrencyRelationship', 'IFC4X1', *args, **kwargs)

def IfcCurtainWall(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurtainWall', 'IFC4X1', *args, **kwargs)

def IfcCurtainWallType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurtainWallType', 'IFC4X1', *args, **kwargs)

def IfcCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurve', 'IFC4X1', *args, **kwargs)

def IfcCurveBoundedPlane(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurveBoundedPlane', 'IFC4X1', *args, **kwargs)

def IfcCurveBoundedSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurveBoundedSurface', 'IFC4X1', *args, **kwargs)

def IfcCurveSegment2D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurveSegment2D', 'IFC4X1', *args, **kwargs)

def IfcCurveStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurveStyle', 'IFC4X1', *args, **kwargs)

def IfcCurveStyleFont(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurveStyleFont', 'IFC4X1', *args, **kwargs)

def IfcCurveStyleFontAndScaling(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurveStyleFontAndScaling', 'IFC4X1', *args, **kwargs)

def IfcCurveStyleFontPattern(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurveStyleFontPattern', 'IFC4X1', *args, **kwargs)

def IfcCylindricalSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCylindricalSurface', 'IFC4X1', *args, **kwargs)

def IfcDamper(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDamper', 'IFC4X1', *args, **kwargs)

def IfcDamperType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDamperType', 'IFC4X1', *args, **kwargs)

def IfcDerivedProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDerivedProfileDef', 'IFC4X1', *args, **kwargs)

def IfcDerivedUnit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDerivedUnit', 'IFC4X1', *args, **kwargs)

def IfcDerivedUnitElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDerivedUnitElement', 'IFC4X1', *args, **kwargs)

def IfcDimensionalExponents(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDimensionalExponents', 'IFC4X1', *args, **kwargs)

def IfcDirection(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDirection', 'IFC4X1', *args, **kwargs)

def IfcDiscreteAccessory(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDiscreteAccessory', 'IFC4X1', *args, **kwargs)

def IfcDiscreteAccessoryType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDiscreteAccessoryType', 'IFC4X1', *args, **kwargs)

def IfcDistanceExpression(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistanceExpression', 'IFC4X1', *args, **kwargs)

def IfcDistributionChamberElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionChamberElement', 'IFC4X1', *args, **kwargs)

def IfcDistributionChamberElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionChamberElementType', 'IFC4X1', *args, **kwargs)

def IfcDistributionCircuit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionCircuit', 'IFC4X1', *args, **kwargs)

def IfcDistributionControlElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionControlElement', 'IFC4X1', *args, **kwargs)

def IfcDistributionControlElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionControlElementType', 'IFC4X1', *args, **kwargs)

def IfcDistributionElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionElement', 'IFC4X1', *args, **kwargs)

def IfcDistributionElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionElementType', 'IFC4X1', *args, **kwargs)

def IfcDistributionFlowElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionFlowElement', 'IFC4X1', *args, **kwargs)

def IfcDistributionFlowElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionFlowElementType', 'IFC4X1', *args, **kwargs)

def IfcDistributionPort(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionPort', 'IFC4X1', *args, **kwargs)

def IfcDistributionSystem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionSystem', 'IFC4X1', *args, **kwargs)

def IfcDocumentInformation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDocumentInformation', 'IFC4X1', *args, **kwargs)

def IfcDocumentInformationRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDocumentInformationRelationship', 'IFC4X1', *args, **kwargs)

def IfcDocumentReference(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDocumentReference', 'IFC4X1', *args, **kwargs)

def IfcDoor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDoor', 'IFC4X1', *args, **kwargs)

def IfcDoorLiningProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDoorLiningProperties', 'IFC4X1', *args, **kwargs)

def IfcDoorPanelProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDoorPanelProperties', 'IFC4X1', *args, **kwargs)

def IfcDoorStandardCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDoorStandardCase', 'IFC4X1', *args, **kwargs)

def IfcDoorStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDoorStyle', 'IFC4X1', *args, **kwargs)

def IfcDoorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDoorType', 'IFC4X1', *args, **kwargs)

def IfcDraughtingPreDefinedColour(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDraughtingPreDefinedColour', 'IFC4X1', *args, **kwargs)

def IfcDraughtingPreDefinedCurveFont(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDraughtingPreDefinedCurveFont', 'IFC4X1', *args, **kwargs)

def IfcDuctFitting(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDuctFitting', 'IFC4X1', *args, **kwargs)

def IfcDuctFittingType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDuctFittingType', 'IFC4X1', *args, **kwargs)

def IfcDuctSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDuctSegment', 'IFC4X1', *args, **kwargs)

def IfcDuctSegmentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDuctSegmentType', 'IFC4X1', *args, **kwargs)

def IfcDuctSilencer(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDuctSilencer', 'IFC4X1', *args, **kwargs)

def IfcDuctSilencerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDuctSilencerType', 'IFC4X1', *args, **kwargs)

def IfcEdge(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEdge', 'IFC4X1', *args, **kwargs)

def IfcEdgeCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEdgeCurve', 'IFC4X1', *args, **kwargs)

def IfcEdgeLoop(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEdgeLoop', 'IFC4X1', *args, **kwargs)

def IfcElectricAppliance(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricAppliance', 'IFC4X1', *args, **kwargs)

def IfcElectricApplianceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricApplianceType', 'IFC4X1', *args, **kwargs)

def IfcElectricDistributionBoard(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricDistributionBoard', 'IFC4X1', *args, **kwargs)

def IfcElectricDistributionBoardType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricDistributionBoardType', 'IFC4X1', *args, **kwargs)

def IfcElectricFlowStorageDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricFlowStorageDevice', 'IFC4X1', *args, **kwargs)

def IfcElectricFlowStorageDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricFlowStorageDeviceType', 'IFC4X1', *args, **kwargs)

def IfcElectricGenerator(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricGenerator', 'IFC4X1', *args, **kwargs)

def IfcElectricGeneratorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricGeneratorType', 'IFC4X1', *args, **kwargs)

def IfcElectricMotor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricMotor', 'IFC4X1', *args, **kwargs)

def IfcElectricMotorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricMotorType', 'IFC4X1', *args, **kwargs)

def IfcElectricTimeControl(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricTimeControl', 'IFC4X1', *args, **kwargs)

def IfcElectricTimeControlType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricTimeControlType', 'IFC4X1', *args, **kwargs)

def IfcElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElement', 'IFC4X1', *args, **kwargs)

def IfcElementAssembly(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElementAssembly', 'IFC4X1', *args, **kwargs)

def IfcElementAssemblyType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElementAssemblyType', 'IFC4X1', *args, **kwargs)

def IfcElementComponent(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElementComponent', 'IFC4X1', *args, **kwargs)

def IfcElementComponentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElementComponentType', 'IFC4X1', *args, **kwargs)

def IfcElementQuantity(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElementQuantity', 'IFC4X1', *args, **kwargs)

def IfcElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElementType', 'IFC4X1', *args, **kwargs)

def IfcElementarySurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElementarySurface', 'IFC4X1', *args, **kwargs)

def IfcEllipse(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEllipse', 'IFC4X1', *args, **kwargs)

def IfcEllipseProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEllipseProfileDef', 'IFC4X1', *args, **kwargs)

def IfcEnergyConversionDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEnergyConversionDevice', 'IFC4X1', *args, **kwargs)

def IfcEnergyConversionDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEnergyConversionDeviceType', 'IFC4X1', *args, **kwargs)

def IfcEngine(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEngine', 'IFC4X1', *args, **kwargs)

def IfcEngineType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEngineType', 'IFC4X1', *args, **kwargs)

def IfcEvaporativeCooler(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEvaporativeCooler', 'IFC4X1', *args, **kwargs)

def IfcEvaporativeCoolerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEvaporativeCoolerType', 'IFC4X1', *args, **kwargs)

def IfcEvaporator(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEvaporator', 'IFC4X1', *args, **kwargs)

def IfcEvaporatorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEvaporatorType', 'IFC4X1', *args, **kwargs)

def IfcEvent(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEvent', 'IFC4X1', *args, **kwargs)

def IfcEventTime(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEventTime', 'IFC4X1', *args, **kwargs)

def IfcEventType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEventType', 'IFC4X1', *args, **kwargs)

def IfcExtendedProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExtendedProperties', 'IFC4X1', *args, **kwargs)

def IfcExternalInformation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExternalInformation', 'IFC4X1', *args, **kwargs)

def IfcExternalReference(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExternalReference', 'IFC4X1', *args, **kwargs)

def IfcExternalReferenceRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExternalReferenceRelationship', 'IFC4X1', *args, **kwargs)

def IfcExternalSpatialElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExternalSpatialElement', 'IFC4X1', *args, **kwargs)

def IfcExternalSpatialStructureElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExternalSpatialStructureElement', 'IFC4X1', *args, **kwargs)

def IfcExternallyDefinedHatchStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExternallyDefinedHatchStyle', 'IFC4X1', *args, **kwargs)

def IfcExternallyDefinedSurfaceStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExternallyDefinedSurfaceStyle', 'IFC4X1', *args, **kwargs)

def IfcExternallyDefinedTextFont(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExternallyDefinedTextFont', 'IFC4X1', *args, **kwargs)

def IfcExtrudedAreaSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExtrudedAreaSolid', 'IFC4X1', *args, **kwargs)

def IfcExtrudedAreaSolidTapered(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExtrudedAreaSolidTapered', 'IFC4X1', *args, **kwargs)

def IfcFace(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFace', 'IFC4X1', *args, **kwargs)

def IfcFaceBasedSurfaceModel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFaceBasedSurfaceModel', 'IFC4X1', *args, **kwargs)

def IfcFaceBound(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFaceBound', 'IFC4X1', *args, **kwargs)

def IfcFaceOuterBound(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFaceOuterBound', 'IFC4X1', *args, **kwargs)

def IfcFaceSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFaceSurface', 'IFC4X1', *args, **kwargs)

def IfcFacetedBrep(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFacetedBrep', 'IFC4X1', *args, **kwargs)

def IfcFacetedBrepWithVoids(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFacetedBrepWithVoids', 'IFC4X1', *args, **kwargs)

def IfcFailureConnectionCondition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFailureConnectionCondition', 'IFC4X1', *args, **kwargs)

def IfcFan(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFan', 'IFC4X1', *args, **kwargs)

def IfcFanType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFanType', 'IFC4X1', *args, **kwargs)

def IfcFastener(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFastener', 'IFC4X1', *args, **kwargs)

def IfcFastenerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFastenerType', 'IFC4X1', *args, **kwargs)

def IfcFeatureElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFeatureElement', 'IFC4X1', *args, **kwargs)

def IfcFeatureElementAddition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFeatureElementAddition', 'IFC4X1', *args, **kwargs)

def IfcFeatureElementSubtraction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFeatureElementSubtraction', 'IFC4X1', *args, **kwargs)

def IfcFillAreaStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFillAreaStyle', 'IFC4X1', *args, **kwargs)

def IfcFillAreaStyleHatching(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFillAreaStyleHatching', 'IFC4X1', *args, **kwargs)

def IfcFillAreaStyleTiles(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFillAreaStyleTiles', 'IFC4X1', *args, **kwargs)

def IfcFilter(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFilter', 'IFC4X1', *args, **kwargs)

def IfcFilterType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFilterType', 'IFC4X1', *args, **kwargs)

def IfcFireSuppressionTerminal(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFireSuppressionTerminal', 'IFC4X1', *args, **kwargs)

def IfcFireSuppressionTerminalType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFireSuppressionTerminalType', 'IFC4X1', *args, **kwargs)

def IfcFixedReferenceSweptAreaSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFixedReferenceSweptAreaSolid', 'IFC4X1', *args, **kwargs)

def IfcFlowController(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowController', 'IFC4X1', *args, **kwargs)

def IfcFlowControllerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowControllerType', 'IFC4X1', *args, **kwargs)

def IfcFlowFitting(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowFitting', 'IFC4X1', *args, **kwargs)

def IfcFlowFittingType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowFittingType', 'IFC4X1', *args, **kwargs)

def IfcFlowInstrument(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowInstrument', 'IFC4X1', *args, **kwargs)

def IfcFlowInstrumentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowInstrumentType', 'IFC4X1', *args, **kwargs)

def IfcFlowMeter(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowMeter', 'IFC4X1', *args, **kwargs)

def IfcFlowMeterType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowMeterType', 'IFC4X1', *args, **kwargs)

def IfcFlowMovingDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowMovingDevice', 'IFC4X1', *args, **kwargs)

def IfcFlowMovingDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowMovingDeviceType', 'IFC4X1', *args, **kwargs)

def IfcFlowSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowSegment', 'IFC4X1', *args, **kwargs)

def IfcFlowSegmentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowSegmentType', 'IFC4X1', *args, **kwargs)

def IfcFlowStorageDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowStorageDevice', 'IFC4X1', *args, **kwargs)

def IfcFlowStorageDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowStorageDeviceType', 'IFC4X1', *args, **kwargs)

def IfcFlowTerminal(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowTerminal', 'IFC4X1', *args, **kwargs)

def IfcFlowTerminalType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowTerminalType', 'IFC4X1', *args, **kwargs)

def IfcFlowTreatmentDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowTreatmentDevice', 'IFC4X1', *args, **kwargs)

def IfcFlowTreatmentDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowTreatmentDeviceType', 'IFC4X1', *args, **kwargs)

def IfcFooting(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFooting', 'IFC4X1', *args, **kwargs)

def IfcFootingType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFootingType', 'IFC4X1', *args, **kwargs)

def IfcFurnishingElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFurnishingElement', 'IFC4X1', *args, **kwargs)

def IfcFurnishingElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFurnishingElementType', 'IFC4X1', *args, **kwargs)

def IfcFurniture(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFurniture', 'IFC4X1', *args, **kwargs)

def IfcFurnitureType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFurnitureType', 'IFC4X1', *args, **kwargs)

def IfcGeographicElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeographicElement', 'IFC4X1', *args, **kwargs)

def IfcGeographicElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeographicElementType', 'IFC4X1', *args, **kwargs)

def IfcGeometricCurveSet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeometricCurveSet', 'IFC4X1', *args, **kwargs)

def IfcGeometricRepresentationContext(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeometricRepresentationContext', 'IFC4X1', *args, **kwargs)

def IfcGeometricRepresentationItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeometricRepresentationItem', 'IFC4X1', *args, **kwargs)

def IfcGeometricRepresentationSubContext(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeometricRepresentationSubContext', 'IFC4X1', *args, **kwargs)

def IfcGeometricSet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeometricSet', 'IFC4X1', *args, **kwargs)

def IfcGrid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGrid', 'IFC4X1', *args, **kwargs)

def IfcGridAxis(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGridAxis', 'IFC4X1', *args, **kwargs)

def IfcGridPlacement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGridPlacement', 'IFC4X1', *args, **kwargs)

def IfcGroup(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGroup', 'IFC4X1', *args, **kwargs)

def IfcHalfSpaceSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcHalfSpaceSolid', 'IFC4X1', *args, **kwargs)

def IfcHeatExchanger(*args, **kwargs):
    return ifcopenshell.create_entity('IfcHeatExchanger', 'IFC4X1', *args, **kwargs)

def IfcHeatExchangerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcHeatExchangerType', 'IFC4X1', *args, **kwargs)

def IfcHumidifier(*args, **kwargs):
    return ifcopenshell.create_entity('IfcHumidifier', 'IFC4X1', *args, **kwargs)

def IfcHumidifierType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcHumidifierType', 'IFC4X1', *args, **kwargs)

def IfcIShapeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIShapeProfileDef', 'IFC4X1', *args, **kwargs)

def IfcImageTexture(*args, **kwargs):
    return ifcopenshell.create_entity('IfcImageTexture', 'IFC4X1', *args, **kwargs)

def IfcIndexedColourMap(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIndexedColourMap', 'IFC4X1', *args, **kwargs)

def IfcIndexedPolyCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIndexedPolyCurve', 'IFC4X1', *args, **kwargs)

def IfcIndexedPolygonalFace(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIndexedPolygonalFace', 'IFC4X1', *args, **kwargs)

def IfcIndexedPolygonalFaceWithVoids(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIndexedPolygonalFaceWithVoids', 'IFC4X1', *args, **kwargs)

def IfcIndexedTextureMap(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIndexedTextureMap', 'IFC4X1', *args, **kwargs)

def IfcIndexedTriangleTextureMap(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIndexedTriangleTextureMap', 'IFC4X1', *args, **kwargs)

def IfcInterceptor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcInterceptor', 'IFC4X1', *args, **kwargs)

def IfcInterceptorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcInterceptorType', 'IFC4X1', *args, **kwargs)

def IfcIntersectionCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIntersectionCurve', 'IFC4X1', *args, **kwargs)

def IfcInventory(*args, **kwargs):
    return ifcopenshell.create_entity('IfcInventory', 'IFC4X1', *args, **kwargs)

def IfcIrregularTimeSeries(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIrregularTimeSeries', 'IFC4X1', *args, **kwargs)

def IfcIrregularTimeSeriesValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIrregularTimeSeriesValue', 'IFC4X1', *args, **kwargs)

def IfcJunctionBox(*args, **kwargs):
    return ifcopenshell.create_entity('IfcJunctionBox', 'IFC4X1', *args, **kwargs)

def IfcJunctionBoxType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcJunctionBoxType', 'IFC4X1', *args, **kwargs)

def IfcLShapeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLShapeProfileDef', 'IFC4X1', *args, **kwargs)

def IfcLaborResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLaborResource', 'IFC4X1', *args, **kwargs)

def IfcLaborResourceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLaborResourceType', 'IFC4X1', *args, **kwargs)

def IfcLagTime(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLagTime', 'IFC4X1', *args, **kwargs)

def IfcLamp(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLamp', 'IFC4X1', *args, **kwargs)

def IfcLampType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLampType', 'IFC4X1', *args, **kwargs)

def IfcLibraryInformation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLibraryInformation', 'IFC4X1', *args, **kwargs)

def IfcLibraryReference(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLibraryReference', 'IFC4X1', *args, **kwargs)

def IfcLightDistributionData(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightDistributionData', 'IFC4X1', *args, **kwargs)

def IfcLightFixture(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightFixture', 'IFC4X1', *args, **kwargs)

def IfcLightFixtureType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightFixtureType', 'IFC4X1', *args, **kwargs)

def IfcLightIntensityDistribution(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightIntensityDistribution', 'IFC4X1', *args, **kwargs)

def IfcLightSource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightSource', 'IFC4X1', *args, **kwargs)

def IfcLightSourceAmbient(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightSourceAmbient', 'IFC4X1', *args, **kwargs)

def IfcLightSourceDirectional(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightSourceDirectional', 'IFC4X1', *args, **kwargs)

def IfcLightSourceGoniometric(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightSourceGoniometric', 'IFC4X1', *args, **kwargs)

def IfcLightSourcePositional(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightSourcePositional', 'IFC4X1', *args, **kwargs)

def IfcLightSourceSpot(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightSourceSpot', 'IFC4X1', *args, **kwargs)

def IfcLine(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLine', 'IFC4X1', *args, **kwargs)

def IfcLineSegment2D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLineSegment2D', 'IFC4X1', *args, **kwargs)

def IfcLinearPlacement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLinearPlacement', 'IFC4X1', *args, **kwargs)

def IfcLinearPositioningElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLinearPositioningElement', 'IFC4X1', *args, **kwargs)

def IfcLocalPlacement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLocalPlacement', 'IFC4X1', *args, **kwargs)

def IfcLoop(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLoop', 'IFC4X1', *args, **kwargs)

def IfcManifoldSolidBrep(*args, **kwargs):
    return ifcopenshell.create_entity('IfcManifoldSolidBrep', 'IFC4X1', *args, **kwargs)

def IfcMapConversion(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMapConversion', 'IFC4X1', *args, **kwargs)

def IfcMappedItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMappedItem', 'IFC4X1', *args, **kwargs)

def IfcMaterial(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterial', 'IFC4X1', *args, **kwargs)

def IfcMaterialClassificationRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialClassificationRelationship', 'IFC4X1', *args, **kwargs)

def IfcMaterialConstituent(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialConstituent', 'IFC4X1', *args, **kwargs)

def IfcMaterialConstituentSet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialConstituentSet', 'IFC4X1', *args, **kwargs)

def IfcMaterialDefinition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialDefinition', 'IFC4X1', *args, **kwargs)

def IfcMaterialDefinitionRepresentation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialDefinitionRepresentation', 'IFC4X1', *args, **kwargs)

def IfcMaterialLayer(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialLayer', 'IFC4X1', *args, **kwargs)

def IfcMaterialLayerSet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialLayerSet', 'IFC4X1', *args, **kwargs)

def IfcMaterialLayerSetUsage(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialLayerSetUsage', 'IFC4X1', *args, **kwargs)

def IfcMaterialLayerWithOffsets(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialLayerWithOffsets', 'IFC4X1', *args, **kwargs)

def IfcMaterialList(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialList', 'IFC4X1', *args, **kwargs)

def IfcMaterialProfile(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialProfile', 'IFC4X1', *args, **kwargs)

def IfcMaterialProfileSet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialProfileSet', 'IFC4X1', *args, **kwargs)

def IfcMaterialProfileSetUsage(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialProfileSetUsage', 'IFC4X1', *args, **kwargs)

def IfcMaterialProfileSetUsageTapering(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialProfileSetUsageTapering', 'IFC4X1', *args, **kwargs)

def IfcMaterialProfileWithOffsets(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialProfileWithOffsets', 'IFC4X1', *args, **kwargs)

def IfcMaterialProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialProperties', 'IFC4X1', *args, **kwargs)

def IfcMaterialRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialRelationship', 'IFC4X1', *args, **kwargs)

def IfcMaterialUsageDefinition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialUsageDefinition', 'IFC4X1', *args, **kwargs)

def IfcMeasureWithUnit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMeasureWithUnit', 'IFC4X1', *args, **kwargs)

def IfcMechanicalFastener(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMechanicalFastener', 'IFC4X1', *args, **kwargs)

def IfcMechanicalFastenerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMechanicalFastenerType', 'IFC4X1', *args, **kwargs)

def IfcMedicalDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMedicalDevice', 'IFC4X1', *args, **kwargs)

def IfcMedicalDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMedicalDeviceType', 'IFC4X1', *args, **kwargs)

def IfcMember(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMember', 'IFC4X1', *args, **kwargs)

def IfcMemberStandardCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMemberStandardCase', 'IFC4X1', *args, **kwargs)

def IfcMemberType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMemberType', 'IFC4X1', *args, **kwargs)

def IfcMetric(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMetric', 'IFC4X1', *args, **kwargs)

def IfcMirroredProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMirroredProfileDef', 'IFC4X1', *args, **kwargs)

def IfcMonetaryUnit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMonetaryUnit', 'IFC4X1', *args, **kwargs)

def IfcMotorConnection(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMotorConnection', 'IFC4X1', *args, **kwargs)

def IfcMotorConnectionType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMotorConnectionType', 'IFC4X1', *args, **kwargs)

def IfcNamedUnit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcNamedUnit', 'IFC4X1', *args, **kwargs)

def IfcObject(*args, **kwargs):
    return ifcopenshell.create_entity('IfcObject', 'IFC4X1', *args, **kwargs)

def IfcObjectDefinition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcObjectDefinition', 'IFC4X1', *args, **kwargs)

def IfcObjectPlacement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcObjectPlacement', 'IFC4X1', *args, **kwargs)

def IfcObjective(*args, **kwargs):
    return ifcopenshell.create_entity('IfcObjective', 'IFC4X1', *args, **kwargs)

def IfcOccupant(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOccupant', 'IFC4X1', *args, **kwargs)

def IfcOffsetCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOffsetCurve', 'IFC4X1', *args, **kwargs)

def IfcOffsetCurve2D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOffsetCurve2D', 'IFC4X1', *args, **kwargs)

def IfcOffsetCurve3D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOffsetCurve3D', 'IFC4X1', *args, **kwargs)

def IfcOffsetCurveByDistances(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOffsetCurveByDistances', 'IFC4X1', *args, **kwargs)

def IfcOpenShell(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOpenShell', 'IFC4X1', *args, **kwargs)

def IfcOpeningElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOpeningElement', 'IFC4X1', *args, **kwargs)

def IfcOpeningStandardCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOpeningStandardCase', 'IFC4X1', *args, **kwargs)

def IfcOrganization(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOrganization', 'IFC4X1', *args, **kwargs)

def IfcOrganizationRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOrganizationRelationship', 'IFC4X1', *args, **kwargs)

def IfcOrientationExpression(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOrientationExpression', 'IFC4X1', *args, **kwargs)

def IfcOrientedEdge(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOrientedEdge', 'IFC4X1', *args, **kwargs)

def IfcOuterBoundaryCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOuterBoundaryCurve', 'IFC4X1', *args, **kwargs)

def IfcOutlet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOutlet', 'IFC4X1', *args, **kwargs)

def IfcOutletType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOutletType', 'IFC4X1', *args, **kwargs)

def IfcOwnerHistory(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOwnerHistory', 'IFC4X1', *args, **kwargs)

def IfcParameterizedProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcParameterizedProfileDef', 'IFC4X1', *args, **kwargs)

def IfcPath(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPath', 'IFC4X1', *args, **kwargs)

def IfcPcurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPcurve', 'IFC4X1', *args, **kwargs)

def IfcPerformanceHistory(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPerformanceHistory', 'IFC4X1', *args, **kwargs)

def IfcPermeableCoveringProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPermeableCoveringProperties', 'IFC4X1', *args, **kwargs)

def IfcPermit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPermit', 'IFC4X1', *args, **kwargs)

def IfcPerson(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPerson', 'IFC4X1', *args, **kwargs)

def IfcPersonAndOrganization(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPersonAndOrganization', 'IFC4X1', *args, **kwargs)

def IfcPhysicalComplexQuantity(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPhysicalComplexQuantity', 'IFC4X1', *args, **kwargs)

def IfcPhysicalQuantity(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPhysicalQuantity', 'IFC4X1', *args, **kwargs)

def IfcPhysicalSimpleQuantity(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPhysicalSimpleQuantity', 'IFC4X1', *args, **kwargs)

def IfcPile(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPile', 'IFC4X1', *args, **kwargs)

def IfcPileType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPileType', 'IFC4X1', *args, **kwargs)

def IfcPipeFitting(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPipeFitting', 'IFC4X1', *args, **kwargs)

def IfcPipeFittingType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPipeFittingType', 'IFC4X1', *args, **kwargs)

def IfcPipeSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPipeSegment', 'IFC4X1', *args, **kwargs)

def IfcPipeSegmentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPipeSegmentType', 'IFC4X1', *args, **kwargs)

def IfcPixelTexture(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPixelTexture', 'IFC4X1', *args, **kwargs)

def IfcPlacement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPlacement', 'IFC4X1', *args, **kwargs)

def IfcPlanarBox(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPlanarBox', 'IFC4X1', *args, **kwargs)

def IfcPlanarExtent(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPlanarExtent', 'IFC4X1', *args, **kwargs)

def IfcPlane(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPlane', 'IFC4X1', *args, **kwargs)

def IfcPlate(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPlate', 'IFC4X1', *args, **kwargs)

def IfcPlateStandardCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPlateStandardCase', 'IFC4X1', *args, **kwargs)

def IfcPlateType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPlateType', 'IFC4X1', *args, **kwargs)

def IfcPoint(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPoint', 'IFC4X1', *args, **kwargs)

def IfcPointOnCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPointOnCurve', 'IFC4X1', *args, **kwargs)

def IfcPointOnSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPointOnSurface', 'IFC4X1', *args, **kwargs)

def IfcPolyLoop(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPolyLoop', 'IFC4X1', *args, **kwargs)

def IfcPolygonalBoundedHalfSpace(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPolygonalBoundedHalfSpace', 'IFC4X1', *args, **kwargs)

def IfcPolygonalFaceSet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPolygonalFaceSet', 'IFC4X1', *args, **kwargs)

def IfcPolyline(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPolyline', 'IFC4X1', *args, **kwargs)

def IfcPort(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPort', 'IFC4X1', *args, **kwargs)

def IfcPositioningElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPositioningElement', 'IFC4X1', *args, **kwargs)

def IfcPostalAddress(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPostalAddress', 'IFC4X1', *args, **kwargs)

def IfcPreDefinedColour(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPreDefinedColour', 'IFC4X1', *args, **kwargs)

def IfcPreDefinedCurveFont(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPreDefinedCurveFont', 'IFC4X1', *args, **kwargs)

def IfcPreDefinedItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPreDefinedItem', 'IFC4X1', *args, **kwargs)

def IfcPreDefinedProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPreDefinedProperties', 'IFC4X1', *args, **kwargs)

def IfcPreDefinedPropertySet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPreDefinedPropertySet', 'IFC4X1', *args, **kwargs)

def IfcPreDefinedTextFont(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPreDefinedTextFont', 'IFC4X1', *args, **kwargs)

def IfcPresentationItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPresentationItem', 'IFC4X1', *args, **kwargs)

def IfcPresentationLayerAssignment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPresentationLayerAssignment', 'IFC4X1', *args, **kwargs)

def IfcPresentationLayerWithStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPresentationLayerWithStyle', 'IFC4X1', *args, **kwargs)

def IfcPresentationStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPresentationStyle', 'IFC4X1', *args, **kwargs)

def IfcPresentationStyleAssignment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPresentationStyleAssignment', 'IFC4X1', *args, **kwargs)

def IfcProcedure(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProcedure', 'IFC4X1', *args, **kwargs)

def IfcProcedureType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProcedureType', 'IFC4X1', *args, **kwargs)

def IfcProcess(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProcess', 'IFC4X1', *args, **kwargs)

def IfcProduct(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProduct', 'IFC4X1', *args, **kwargs)

def IfcProductDefinitionShape(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProductDefinitionShape', 'IFC4X1', *args, **kwargs)

def IfcProductRepresentation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProductRepresentation', 'IFC4X1', *args, **kwargs)

def IfcProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProfileDef', 'IFC4X1', *args, **kwargs)

def IfcProfileProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProfileProperties', 'IFC4X1', *args, **kwargs)

def IfcProject(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProject', 'IFC4X1', *args, **kwargs)

def IfcProjectLibrary(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProjectLibrary', 'IFC4X1', *args, **kwargs)

def IfcProjectOrder(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProjectOrder', 'IFC4X1', *args, **kwargs)

def IfcProjectedCRS(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProjectedCRS', 'IFC4X1', *args, **kwargs)

def IfcProjectionElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProjectionElement', 'IFC4X1', *args, **kwargs)

def IfcProperty(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProperty', 'IFC4X1', *args, **kwargs)

def IfcPropertyAbstraction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyAbstraction', 'IFC4X1', *args, **kwargs)

def IfcPropertyBoundedValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyBoundedValue', 'IFC4X1', *args, **kwargs)

def IfcPropertyDefinition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyDefinition', 'IFC4X1', *args, **kwargs)

def IfcPropertyDependencyRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyDependencyRelationship', 'IFC4X1', *args, **kwargs)

def IfcPropertyEnumeratedValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyEnumeratedValue', 'IFC4X1', *args, **kwargs)

def IfcPropertyEnumeration(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyEnumeration', 'IFC4X1', *args, **kwargs)

def IfcPropertyListValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyListValue', 'IFC4X1', *args, **kwargs)

def IfcPropertyReferenceValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyReferenceValue', 'IFC4X1', *args, **kwargs)

def IfcPropertySet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertySet', 'IFC4X1', *args, **kwargs)

def IfcPropertySetDefinition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertySetDefinition', 'IFC4X1', *args, **kwargs)

def IfcPropertySetTemplate(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertySetTemplate', 'IFC4X1', *args, **kwargs)

def IfcPropertySingleValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertySingleValue', 'IFC4X1', *args, **kwargs)

def IfcPropertyTableValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyTableValue', 'IFC4X1', *args, **kwargs)

def IfcPropertyTemplate(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyTemplate', 'IFC4X1', *args, **kwargs)

def IfcPropertyTemplateDefinition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyTemplateDefinition', 'IFC4X1', *args, **kwargs)

def IfcProtectiveDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProtectiveDevice', 'IFC4X1', *args, **kwargs)

def IfcProtectiveDeviceTrippingUnit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProtectiveDeviceTrippingUnit', 'IFC4X1', *args, **kwargs)

def IfcProtectiveDeviceTrippingUnitType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProtectiveDeviceTrippingUnitType', 'IFC4X1', *args, **kwargs)

def IfcProtectiveDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProtectiveDeviceType', 'IFC4X1', *args, **kwargs)

def IfcProxy(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProxy', 'IFC4X1', *args, **kwargs)

def IfcPump(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPump', 'IFC4X1', *args, **kwargs)

def IfcPumpType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPumpType', 'IFC4X1', *args, **kwargs)

def IfcQuantityArea(*args, **kwargs):
    return ifcopenshell.create_entity('IfcQuantityArea', 'IFC4X1', *args, **kwargs)

def IfcQuantityCount(*args, **kwargs):
    return ifcopenshell.create_entity('IfcQuantityCount', 'IFC4X1', *args, **kwargs)

def IfcQuantityLength(*args, **kwargs):
    return ifcopenshell.create_entity('IfcQuantityLength', 'IFC4X1', *args, **kwargs)

def IfcQuantitySet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcQuantitySet', 'IFC4X1', *args, **kwargs)

def IfcQuantityTime(*args, **kwargs):
    return ifcopenshell.create_entity('IfcQuantityTime', 'IFC4X1', *args, **kwargs)

def IfcQuantityVolume(*args, **kwargs):
    return ifcopenshell.create_entity('IfcQuantityVolume', 'IFC4X1', *args, **kwargs)

def IfcQuantityWeight(*args, **kwargs):
    return ifcopenshell.create_entity('IfcQuantityWeight', 'IFC4X1', *args, **kwargs)

def IfcRailing(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRailing', 'IFC4X1', *args, **kwargs)

def IfcRailingType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRailingType', 'IFC4X1', *args, **kwargs)

def IfcRamp(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRamp', 'IFC4X1', *args, **kwargs)

def IfcRampFlight(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRampFlight', 'IFC4X1', *args, **kwargs)

def IfcRampFlightType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRampFlightType', 'IFC4X1', *args, **kwargs)

def IfcRampType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRampType', 'IFC4X1', *args, **kwargs)

def IfcRationalBSplineCurveWithKnots(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRationalBSplineCurveWithKnots', 'IFC4X1', *args, **kwargs)

def IfcRationalBSplineSurfaceWithKnots(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRationalBSplineSurfaceWithKnots', 'IFC4X1', *args, **kwargs)

def IfcRectangleHollowProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRectangleHollowProfileDef', 'IFC4X1', *args, **kwargs)

def IfcRectangleProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRectangleProfileDef', 'IFC4X1', *args, **kwargs)

def IfcRectangularPyramid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRectangularPyramid', 'IFC4X1', *args, **kwargs)

def IfcRectangularTrimmedSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRectangularTrimmedSurface', 'IFC4X1', *args, **kwargs)

def IfcRecurrencePattern(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRecurrencePattern', 'IFC4X1', *args, **kwargs)

def IfcReference(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReference', 'IFC4X1', *args, **kwargs)

def IfcReferent(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReferent', 'IFC4X1', *args, **kwargs)

def IfcRegularTimeSeries(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRegularTimeSeries', 'IFC4X1', *args, **kwargs)

def IfcReinforcementBarProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReinforcementBarProperties', 'IFC4X1', *args, **kwargs)

def IfcReinforcementDefinitionProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReinforcementDefinitionProperties', 'IFC4X1', *args, **kwargs)

def IfcReinforcingBar(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReinforcingBar', 'IFC4X1', *args, **kwargs)

def IfcReinforcingBarType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReinforcingBarType', 'IFC4X1', *args, **kwargs)

def IfcReinforcingElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReinforcingElement', 'IFC4X1', *args, **kwargs)

def IfcReinforcingElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReinforcingElementType', 'IFC4X1', *args, **kwargs)

def IfcReinforcingMesh(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReinforcingMesh', 'IFC4X1', *args, **kwargs)

def IfcReinforcingMeshType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReinforcingMeshType', 'IFC4X1', *args, **kwargs)

def IfcRelAggregates(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAggregates', 'IFC4X1', *args, **kwargs)

def IfcRelAssigns(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssigns', 'IFC4X1', *args, **kwargs)

def IfcRelAssignsToActor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssignsToActor', 'IFC4X1', *args, **kwargs)

def IfcRelAssignsToControl(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssignsToControl', 'IFC4X1', *args, **kwargs)

def IfcRelAssignsToGroup(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssignsToGroup', 'IFC4X1', *args, **kwargs)

def IfcRelAssignsToGroupByFactor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssignsToGroupByFactor', 'IFC4X1', *args, **kwargs)

def IfcRelAssignsToProcess(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssignsToProcess', 'IFC4X1', *args, **kwargs)

def IfcRelAssignsToProduct(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssignsToProduct', 'IFC4X1', *args, **kwargs)

def IfcRelAssignsToResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssignsToResource', 'IFC4X1', *args, **kwargs)

def IfcRelAssociates(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssociates', 'IFC4X1', *args, **kwargs)

def IfcRelAssociatesApproval(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssociatesApproval', 'IFC4X1', *args, **kwargs)

def IfcRelAssociatesClassification(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssociatesClassification', 'IFC4X1', *args, **kwargs)

def IfcRelAssociatesConstraint(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssociatesConstraint', 'IFC4X1', *args, **kwargs)

def IfcRelAssociatesDocument(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssociatesDocument', 'IFC4X1', *args, **kwargs)

def IfcRelAssociatesLibrary(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssociatesLibrary', 'IFC4X1', *args, **kwargs)

def IfcRelAssociatesMaterial(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssociatesMaterial', 'IFC4X1', *args, **kwargs)

def IfcRelConnects(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnects', 'IFC4X1', *args, **kwargs)

def IfcRelConnectsElements(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsElements', 'IFC4X1', *args, **kwargs)

def IfcRelConnectsPathElements(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsPathElements', 'IFC4X1', *args, **kwargs)

def IfcRelConnectsPortToElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsPortToElement', 'IFC4X1', *args, **kwargs)

def IfcRelConnectsPorts(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsPorts', 'IFC4X1', *args, **kwargs)

def IfcRelConnectsStructuralActivity(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsStructuralActivity', 'IFC4X1', *args, **kwargs)

def IfcRelConnectsStructuralMember(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsStructuralMember', 'IFC4X1', *args, **kwargs)

def IfcRelConnectsWithEccentricity(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsWithEccentricity', 'IFC4X1', *args, **kwargs)

def IfcRelConnectsWithRealizingElements(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsWithRealizingElements', 'IFC4X1', *args, **kwargs)

def IfcRelContainedInSpatialStructure(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelContainedInSpatialStructure', 'IFC4X1', *args, **kwargs)

def IfcRelCoversBldgElements(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelCoversBldgElements', 'IFC4X1', *args, **kwargs)

def IfcRelCoversSpaces(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelCoversSpaces', 'IFC4X1', *args, **kwargs)

def IfcRelDeclares(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelDeclares', 'IFC4X1', *args, **kwargs)

def IfcRelDecomposes(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelDecomposes', 'IFC4X1', *args, **kwargs)

def IfcRelDefines(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelDefines', 'IFC4X1', *args, **kwargs)

def IfcRelDefinesByObject(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelDefinesByObject', 'IFC4X1', *args, **kwargs)

def IfcRelDefinesByProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelDefinesByProperties', 'IFC4X1', *args, **kwargs)

def IfcRelDefinesByTemplate(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelDefinesByTemplate', 'IFC4X1', *args, **kwargs)

def IfcRelDefinesByType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelDefinesByType', 'IFC4X1', *args, **kwargs)

def IfcRelFillsElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelFillsElement', 'IFC4X1', *args, **kwargs)

def IfcRelFlowControlElements(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelFlowControlElements', 'IFC4X1', *args, **kwargs)

def IfcRelInterferesElements(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelInterferesElements', 'IFC4X1', *args, **kwargs)

def IfcRelNests(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelNests', 'IFC4X1', *args, **kwargs)

def IfcRelProjectsElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelProjectsElement', 'IFC4X1', *args, **kwargs)

def IfcRelReferencedInSpatialStructure(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelReferencedInSpatialStructure', 'IFC4X1', *args, **kwargs)

def IfcRelSequence(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelSequence', 'IFC4X1', *args, **kwargs)

def IfcRelServicesBuildings(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelServicesBuildings', 'IFC4X1', *args, **kwargs)

def IfcRelSpaceBoundary(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelSpaceBoundary', 'IFC4X1', *args, **kwargs)

def IfcRelSpaceBoundary1stLevel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelSpaceBoundary1stLevel', 'IFC4X1', *args, **kwargs)

def IfcRelSpaceBoundary2ndLevel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelSpaceBoundary2ndLevel', 'IFC4X1', *args, **kwargs)

def IfcRelVoidsElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelVoidsElement', 'IFC4X1', *args, **kwargs)

def IfcRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelationship', 'IFC4X1', *args, **kwargs)

def IfcReparametrisedCompositeCurveSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReparametrisedCompositeCurveSegment', 'IFC4X1', *args, **kwargs)

def IfcRepresentation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRepresentation', 'IFC4X1', *args, **kwargs)

def IfcRepresentationContext(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRepresentationContext', 'IFC4X1', *args, **kwargs)

def IfcRepresentationItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRepresentationItem', 'IFC4X1', *args, **kwargs)

def IfcRepresentationMap(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRepresentationMap', 'IFC4X1', *args, **kwargs)

def IfcResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcResource', 'IFC4X1', *args, **kwargs)

def IfcResourceApprovalRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcResourceApprovalRelationship', 'IFC4X1', *args, **kwargs)

def IfcResourceConstraintRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcResourceConstraintRelationship', 'IFC4X1', *args, **kwargs)

def IfcResourceLevelRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcResourceLevelRelationship', 'IFC4X1', *args, **kwargs)

def IfcResourceTime(*args, **kwargs):
    return ifcopenshell.create_entity('IfcResourceTime', 'IFC4X1', *args, **kwargs)

def IfcRevolvedAreaSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRevolvedAreaSolid', 'IFC4X1', *args, **kwargs)

def IfcRevolvedAreaSolidTapered(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRevolvedAreaSolidTapered', 'IFC4X1', *args, **kwargs)

def IfcRightCircularCone(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRightCircularCone', 'IFC4X1', *args, **kwargs)

def IfcRightCircularCylinder(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRightCircularCylinder', 'IFC4X1', *args, **kwargs)

def IfcRoof(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRoof', 'IFC4X1', *args, **kwargs)

def IfcRoofType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRoofType', 'IFC4X1', *args, **kwargs)

def IfcRoot(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRoot', 'IFC4X1', *args, **kwargs)

def IfcRoundedRectangleProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRoundedRectangleProfileDef', 'IFC4X1', *args, **kwargs)

def IfcSIUnit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSIUnit', 'IFC4X1', *args, **kwargs)

def IfcSanitaryTerminal(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSanitaryTerminal', 'IFC4X1', *args, **kwargs)

def IfcSanitaryTerminalType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSanitaryTerminalType', 'IFC4X1', *args, **kwargs)

def IfcSchedulingTime(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSchedulingTime', 'IFC4X1', *args, **kwargs)

def IfcSeamCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSeamCurve', 'IFC4X1', *args, **kwargs)

def IfcSectionProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSectionProperties', 'IFC4X1', *args, **kwargs)

def IfcSectionReinforcementProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSectionReinforcementProperties', 'IFC4X1', *args, **kwargs)

def IfcSectionedSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSectionedSolid', 'IFC4X1', *args, **kwargs)

def IfcSectionedSolidHorizontal(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSectionedSolidHorizontal', 'IFC4X1', *args, **kwargs)

def IfcSectionedSpine(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSectionedSpine', 'IFC4X1', *args, **kwargs)

def IfcSensor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSensor', 'IFC4X1', *args, **kwargs)

def IfcSensorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSensorType', 'IFC4X1', *args, **kwargs)

def IfcShadingDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcShadingDevice', 'IFC4X1', *args, **kwargs)

def IfcShadingDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcShadingDeviceType', 'IFC4X1', *args, **kwargs)

def IfcShapeAspect(*args, **kwargs):
    return ifcopenshell.create_entity('IfcShapeAspect', 'IFC4X1', *args, **kwargs)

def IfcShapeModel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcShapeModel', 'IFC4X1', *args, **kwargs)

def IfcShapeRepresentation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcShapeRepresentation', 'IFC4X1', *args, **kwargs)

def IfcShellBasedSurfaceModel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcShellBasedSurfaceModel', 'IFC4X1', *args, **kwargs)

def IfcSimpleProperty(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSimpleProperty', 'IFC4X1', *args, **kwargs)

def IfcSimplePropertyTemplate(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSimplePropertyTemplate', 'IFC4X1', *args, **kwargs)

def IfcSite(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSite', 'IFC4X1', *args, **kwargs)

def IfcSlab(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSlab', 'IFC4X1', *args, **kwargs)

def IfcSlabElementedCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSlabElementedCase', 'IFC4X1', *args, **kwargs)

def IfcSlabStandardCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSlabStandardCase', 'IFC4X1', *args, **kwargs)

def IfcSlabType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSlabType', 'IFC4X1', *args, **kwargs)

def IfcSlippageConnectionCondition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSlippageConnectionCondition', 'IFC4X1', *args, **kwargs)

def IfcSolarDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSolarDevice', 'IFC4X1', *args, **kwargs)

def IfcSolarDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSolarDeviceType', 'IFC4X1', *args, **kwargs)

def IfcSolidModel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSolidModel', 'IFC4X1', *args, **kwargs)

def IfcSpace(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpace', 'IFC4X1', *args, **kwargs)

def IfcSpaceHeater(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpaceHeater', 'IFC4X1', *args, **kwargs)

def IfcSpaceHeaterType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpaceHeaterType', 'IFC4X1', *args, **kwargs)

def IfcSpaceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpaceType', 'IFC4X1', *args, **kwargs)

def IfcSpatialElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpatialElement', 'IFC4X1', *args, **kwargs)

def IfcSpatialElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpatialElementType', 'IFC4X1', *args, **kwargs)

def IfcSpatialStructureElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpatialStructureElement', 'IFC4X1', *args, **kwargs)

def IfcSpatialStructureElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpatialStructureElementType', 'IFC4X1', *args, **kwargs)

def IfcSpatialZone(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpatialZone', 'IFC4X1', *args, **kwargs)

def IfcSpatialZoneType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpatialZoneType', 'IFC4X1', *args, **kwargs)

def IfcSphere(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSphere', 'IFC4X1', *args, **kwargs)

def IfcSphericalSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSphericalSurface', 'IFC4X1', *args, **kwargs)

def IfcStackTerminal(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStackTerminal', 'IFC4X1', *args, **kwargs)

def IfcStackTerminalType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStackTerminalType', 'IFC4X1', *args, **kwargs)

def IfcStair(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStair', 'IFC4X1', *args, **kwargs)

def IfcStairFlight(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStairFlight', 'IFC4X1', *args, **kwargs)

def IfcStairFlightType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStairFlightType', 'IFC4X1', *args, **kwargs)

def IfcStairType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStairType', 'IFC4X1', *args, **kwargs)

def IfcStructuralAction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralAction', 'IFC4X1', *args, **kwargs)

def IfcStructuralActivity(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralActivity', 'IFC4X1', *args, **kwargs)

def IfcStructuralAnalysisModel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralAnalysisModel', 'IFC4X1', *args, **kwargs)

def IfcStructuralConnection(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralConnection', 'IFC4X1', *args, **kwargs)

def IfcStructuralConnectionCondition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralConnectionCondition', 'IFC4X1', *args, **kwargs)

def IfcStructuralCurveAction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralCurveAction', 'IFC4X1', *args, **kwargs)

def IfcStructuralCurveConnection(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralCurveConnection', 'IFC4X1', *args, **kwargs)

def IfcStructuralCurveMember(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralCurveMember', 'IFC4X1', *args, **kwargs)

def IfcStructuralCurveMemberVarying(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralCurveMemberVarying', 'IFC4X1', *args, **kwargs)

def IfcStructuralCurveReaction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralCurveReaction', 'IFC4X1', *args, **kwargs)

def IfcStructuralItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralItem', 'IFC4X1', *args, **kwargs)

def IfcStructuralLinearAction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLinearAction', 'IFC4X1', *args, **kwargs)

def IfcStructuralLoad(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoad', 'IFC4X1', *args, **kwargs)

def IfcStructuralLoadCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadCase', 'IFC4X1', *args, **kwargs)

def IfcStructuralLoadConfiguration(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadConfiguration', 'IFC4X1', *args, **kwargs)

def IfcStructuralLoadGroup(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadGroup', 'IFC4X1', *args, **kwargs)

def IfcStructuralLoadLinearForce(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadLinearForce', 'IFC4X1', *args, **kwargs)

def IfcStructuralLoadOrResult(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadOrResult', 'IFC4X1', *args, **kwargs)

def IfcStructuralLoadPlanarForce(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadPlanarForce', 'IFC4X1', *args, **kwargs)

def IfcStructuralLoadSingleDisplacement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadSingleDisplacement', 'IFC4X1', *args, **kwargs)

def IfcStructuralLoadSingleDisplacementDistortion(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadSingleDisplacementDistortion', 'IFC4X1', *args, **kwargs)

def IfcStructuralLoadSingleForce(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadSingleForce', 'IFC4X1', *args, **kwargs)

def IfcStructuralLoadSingleForceWarping(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadSingleForceWarping', 'IFC4X1', *args, **kwargs)

def IfcStructuralLoadStatic(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadStatic', 'IFC4X1', *args, **kwargs)

def IfcStructuralLoadTemperature(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadTemperature', 'IFC4X1', *args, **kwargs)

def IfcStructuralMember(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralMember', 'IFC4X1', *args, **kwargs)

def IfcStructuralPlanarAction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralPlanarAction', 'IFC4X1', *args, **kwargs)

def IfcStructuralPointAction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralPointAction', 'IFC4X1', *args, **kwargs)

def IfcStructuralPointConnection(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralPointConnection', 'IFC4X1', *args, **kwargs)

def IfcStructuralPointReaction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralPointReaction', 'IFC4X1', *args, **kwargs)

def IfcStructuralReaction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralReaction', 'IFC4X1', *args, **kwargs)

def IfcStructuralResultGroup(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralResultGroup', 'IFC4X1', *args, **kwargs)

def IfcStructuralSurfaceAction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralSurfaceAction', 'IFC4X1', *args, **kwargs)

def IfcStructuralSurfaceConnection(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralSurfaceConnection', 'IFC4X1', *args, **kwargs)

def IfcStructuralSurfaceMember(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralSurfaceMember', 'IFC4X1', *args, **kwargs)

def IfcStructuralSurfaceMemberVarying(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralSurfaceMemberVarying', 'IFC4X1', *args, **kwargs)

def IfcStructuralSurfaceReaction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralSurfaceReaction', 'IFC4X1', *args, **kwargs)

def IfcStyleModel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStyleModel', 'IFC4X1', *args, **kwargs)

def IfcStyledItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStyledItem', 'IFC4X1', *args, **kwargs)

def IfcStyledRepresentation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStyledRepresentation', 'IFC4X1', *args, **kwargs)

def IfcSubContractResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSubContractResource', 'IFC4X1', *args, **kwargs)

def IfcSubContractResourceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSubContractResourceType', 'IFC4X1', *args, **kwargs)

def IfcSubedge(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSubedge', 'IFC4X1', *args, **kwargs)

def IfcSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurface', 'IFC4X1', *args, **kwargs)

def IfcSurfaceCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceCurve', 'IFC4X1', *args, **kwargs)

def IfcSurfaceCurveSweptAreaSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceCurveSweptAreaSolid', 'IFC4X1', *args, **kwargs)

def IfcSurfaceFeature(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceFeature', 'IFC4X1', *args, **kwargs)

def IfcSurfaceOfLinearExtrusion(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceOfLinearExtrusion', 'IFC4X1', *args, **kwargs)

def IfcSurfaceOfRevolution(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceOfRevolution', 'IFC4X1', *args, **kwargs)

def IfcSurfaceReinforcementArea(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceReinforcementArea', 'IFC4X1', *args, **kwargs)

def IfcSurfaceStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceStyle', 'IFC4X1', *args, **kwargs)

def IfcSurfaceStyleLighting(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceStyleLighting', 'IFC4X1', *args, **kwargs)

def IfcSurfaceStyleRefraction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceStyleRefraction', 'IFC4X1', *args, **kwargs)

def IfcSurfaceStyleRendering(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceStyleRendering', 'IFC4X1', *args, **kwargs)

def IfcSurfaceStyleShading(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceStyleShading', 'IFC4X1', *args, **kwargs)

def IfcSurfaceStyleWithTextures(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceStyleWithTextures', 'IFC4X1', *args, **kwargs)

def IfcSurfaceTexture(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceTexture', 'IFC4X1', *args, **kwargs)

def IfcSweptAreaSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSweptAreaSolid', 'IFC4X1', *args, **kwargs)

def IfcSweptDiskSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSweptDiskSolid', 'IFC4X1', *args, **kwargs)

def IfcSweptDiskSolidPolygonal(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSweptDiskSolidPolygonal', 'IFC4X1', *args, **kwargs)

def IfcSweptSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSweptSurface', 'IFC4X1', *args, **kwargs)

def IfcSwitchingDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSwitchingDevice', 'IFC4X1', *args, **kwargs)

def IfcSwitchingDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSwitchingDeviceType', 'IFC4X1', *args, **kwargs)

def IfcSystem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSystem', 'IFC4X1', *args, **kwargs)

def IfcSystemFurnitureElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSystemFurnitureElement', 'IFC4X1', *args, **kwargs)

def IfcSystemFurnitureElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSystemFurnitureElementType', 'IFC4X1', *args, **kwargs)

def IfcTShapeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTShapeProfileDef', 'IFC4X1', *args, **kwargs)

def IfcTable(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTable', 'IFC4X1', *args, **kwargs)

def IfcTableColumn(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTableColumn', 'IFC4X1', *args, **kwargs)

def IfcTableRow(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTableRow', 'IFC4X1', *args, **kwargs)

def IfcTank(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTank', 'IFC4X1', *args, **kwargs)

def IfcTankType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTankType', 'IFC4X1', *args, **kwargs)

def IfcTask(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTask', 'IFC4X1', *args, **kwargs)

def IfcTaskTime(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTaskTime', 'IFC4X1', *args, **kwargs)

def IfcTaskTimeRecurring(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTaskTimeRecurring', 'IFC4X1', *args, **kwargs)

def IfcTaskType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTaskType', 'IFC4X1', *args, **kwargs)

def IfcTelecomAddress(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTelecomAddress', 'IFC4X1', *args, **kwargs)

def IfcTendon(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTendon', 'IFC4X1', *args, **kwargs)

def IfcTendonAnchor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTendonAnchor', 'IFC4X1', *args, **kwargs)

def IfcTendonAnchorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTendonAnchorType', 'IFC4X1', *args, **kwargs)

def IfcTendonType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTendonType', 'IFC4X1', *args, **kwargs)

def IfcTessellatedFaceSet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTessellatedFaceSet', 'IFC4X1', *args, **kwargs)

def IfcTessellatedItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTessellatedItem', 'IFC4X1', *args, **kwargs)

def IfcTextLiteral(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextLiteral', 'IFC4X1', *args, **kwargs)

def IfcTextLiteralWithExtent(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextLiteralWithExtent', 'IFC4X1', *args, **kwargs)

def IfcTextStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextStyle', 'IFC4X1', *args, **kwargs)

def IfcTextStyleFontModel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextStyleFontModel', 'IFC4X1', *args, **kwargs)

def IfcTextStyleForDefinedFont(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextStyleForDefinedFont', 'IFC4X1', *args, **kwargs)

def IfcTextStyleTextModel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextStyleTextModel', 'IFC4X1', *args, **kwargs)

def IfcTextureCoordinate(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextureCoordinate', 'IFC4X1', *args, **kwargs)

def IfcTextureCoordinateGenerator(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextureCoordinateGenerator', 'IFC4X1', *args, **kwargs)

def IfcTextureMap(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextureMap', 'IFC4X1', *args, **kwargs)

def IfcTextureVertex(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextureVertex', 'IFC4X1', *args, **kwargs)

def IfcTextureVertexList(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextureVertexList', 'IFC4X1', *args, **kwargs)

def IfcTimePeriod(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTimePeriod', 'IFC4X1', *args, **kwargs)

def IfcTimeSeries(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTimeSeries', 'IFC4X1', *args, **kwargs)

def IfcTimeSeriesValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTimeSeriesValue', 'IFC4X1', *args, **kwargs)

def IfcTopologicalRepresentationItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTopologicalRepresentationItem', 'IFC4X1', *args, **kwargs)

def IfcTopologyRepresentation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTopologyRepresentation', 'IFC4X1', *args, **kwargs)

def IfcToroidalSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcToroidalSurface', 'IFC4X1', *args, **kwargs)

def IfcTransformer(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTransformer', 'IFC4X1', *args, **kwargs)

def IfcTransformerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTransformerType', 'IFC4X1', *args, **kwargs)

def IfcTransitionCurveSegment2D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTransitionCurveSegment2D', 'IFC4X1', *args, **kwargs)

def IfcTransportElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTransportElement', 'IFC4X1', *args, **kwargs)

def IfcTransportElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTransportElementType', 'IFC4X1', *args, **kwargs)

def IfcTrapeziumProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTrapeziumProfileDef', 'IFC4X1', *args, **kwargs)

def IfcTriangulatedFaceSet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTriangulatedFaceSet', 'IFC4X1', *args, **kwargs)

def IfcTriangulatedIrregularNetwork(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTriangulatedIrregularNetwork', 'IFC4X1', *args, **kwargs)

def IfcTrimmedCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTrimmedCurve', 'IFC4X1', *args, **kwargs)

def IfcTubeBundle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTubeBundle', 'IFC4X1', *args, **kwargs)

def IfcTubeBundleType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTubeBundleType', 'IFC4X1', *args, **kwargs)

def IfcTypeObject(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTypeObject', 'IFC4X1', *args, **kwargs)

def IfcTypeProcess(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTypeProcess', 'IFC4X1', *args, **kwargs)

def IfcTypeProduct(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTypeProduct', 'IFC4X1', *args, **kwargs)

def IfcTypeResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTypeResource', 'IFC4X1', *args, **kwargs)

def IfcUShapeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcUShapeProfileDef', 'IFC4X1', *args, **kwargs)

def IfcUnitAssignment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcUnitAssignment', 'IFC4X1', *args, **kwargs)

def IfcUnitaryControlElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcUnitaryControlElement', 'IFC4X1', *args, **kwargs)

def IfcUnitaryControlElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcUnitaryControlElementType', 'IFC4X1', *args, **kwargs)

def IfcUnitaryEquipment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcUnitaryEquipment', 'IFC4X1', *args, **kwargs)

def IfcUnitaryEquipmentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcUnitaryEquipmentType', 'IFC4X1', *args, **kwargs)

def IfcValve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcValve', 'IFC4X1', *args, **kwargs)

def IfcValveType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcValveType', 'IFC4X1', *args, **kwargs)

def IfcVector(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVector', 'IFC4X1', *args, **kwargs)

def IfcVertex(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVertex', 'IFC4X1', *args, **kwargs)

def IfcVertexLoop(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVertexLoop', 'IFC4X1', *args, **kwargs)

def IfcVertexPoint(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVertexPoint', 'IFC4X1', *args, **kwargs)

def IfcVibrationIsolator(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVibrationIsolator', 'IFC4X1', *args, **kwargs)

def IfcVibrationIsolatorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVibrationIsolatorType', 'IFC4X1', *args, **kwargs)

def IfcVirtualElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVirtualElement', 'IFC4X1', *args, **kwargs)

def IfcVirtualGridIntersection(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVirtualGridIntersection', 'IFC4X1', *args, **kwargs)

def IfcVoidingFeature(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVoidingFeature', 'IFC4X1', *args, **kwargs)

def IfcWall(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWall', 'IFC4X1', *args, **kwargs)

def IfcWallElementedCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWallElementedCase', 'IFC4X1', *args, **kwargs)

def IfcWallStandardCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWallStandardCase', 'IFC4X1', *args, **kwargs)

def IfcWallType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWallType', 'IFC4X1', *args, **kwargs)

def IfcWasteTerminal(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWasteTerminal', 'IFC4X1', *args, **kwargs)

def IfcWasteTerminalType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWasteTerminalType', 'IFC4X1', *args, **kwargs)

def IfcWindow(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWindow', 'IFC4X1', *args, **kwargs)

def IfcWindowLiningProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWindowLiningProperties', 'IFC4X1', *args, **kwargs)

def IfcWindowPanelProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWindowPanelProperties', 'IFC4X1', *args, **kwargs)

def IfcWindowStandardCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWindowStandardCase', 'IFC4X1', *args, **kwargs)

def IfcWindowStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWindowStyle', 'IFC4X1', *args, **kwargs)

def IfcWindowType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWindowType', 'IFC4X1', *args, **kwargs)

def IfcWorkCalendar(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWorkCalendar', 'IFC4X1', *args, **kwargs)

def IfcWorkControl(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWorkControl', 'IFC4X1', *args, **kwargs)

def IfcWorkPlan(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWorkPlan', 'IFC4X1', *args, **kwargs)

def IfcWorkSchedule(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWorkSchedule', 'IFC4X1', *args, **kwargs)

def IfcWorkTime(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWorkTime', 'IFC4X1', *args, **kwargs)

def IfcZShapeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcZShapeProfileDef', 'IFC4X1', *args, **kwargs)

def IfcZone(*args, **kwargs):
    return ifcopenshell.create_entity('IfcZone', 'IFC4X1', *args, **kwargs)

class IfcBoxAlignment_WR1:
    SCOPE = 'type'
    TYPE_NAME = 'IfcBoxAlignment'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (getattr(self, 'lower', INDETERMINATE)() in ['top-left', 'top-middle', 'top-right', 'middle-left', 'center', 'middle-right', 'bottom-left', 'bottom-middle', 'bottom-right']) is not False

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
        assert (getattr(self, 'lower', INDETERMINATE)() in ['normal', 'italic', 'oblique']) is not False

class IfcFontVariant_WR1:
    SCOPE = 'type'
    TYPE_NAME = 'IfcFontVariant'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (getattr(self, 'lower', INDETERMINATE)() in ['normal', 'small-caps']) is not False

class IfcFontWeight_WR1:
    SCOPE = 'type'
    TYPE_NAME = 'IfcFontWeight'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (getattr(self, 'lower', INDETERMINATE)() in ['normal', 'small-caps', '100', '200', '300', '400', '500', '600', '700', '800', '900']) is not False

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
        assert (getattr(self, 'lower', INDETERMINATE)() in ['left', 'right', 'center', 'justify']) is not False

class IfcTextDecoration_WR1:
    SCOPE = 'type'
    TYPE_NAME = 'IfcTextDecoration'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (getattr(self, 'lower', INDETERMINATE)() in ['none', 'underline', 'overline', 'line-through', 'blink']) is not False

class IfcTextTransformation_WR1:
    SCOPE = 'type'
    TYPE_NAME = 'IfcTextTransformation'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (getattr(self, 'lower', INDETERMINATE)() in ['capitalize', 'uppercase', 'lowercase', 'none']) is not False

class IfcActorRole_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcActorRole'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        role = getattr(self, 'Role', INDETERMINATE)
        assert (role != getattr(IfcRoleEnum, 'USERDEFINED', INDETERMINATE) or (role == getattr(IfcRoleEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'UserDefinedRole', INDETERMINATE)))) is not False

class IfcActuator_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcActuator'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcActuatorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcActuatorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcActuator_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcActuator'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcactuatortype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcActuatorType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcActuatorType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcActuatorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcActuatorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcAddress_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAddress'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        purpose = getattr(self, 'Purpose', INDETERMINATE)
        assert (not exists(purpose) or (purpose != getattr(IfcAddressTypeEnum, 'USERDEFINED', INDETERMINATE) or (purpose == getattr(IfcAddressTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'UserDefinedPurpose', INDETERMINATE))))) is not False

class IfcAdvancedBrep_HasAdvancedFaces:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAdvancedBrep'
    RULE_NAME = 'HasAdvancedFaces'

    @staticmethod
    def __call__(self):
        assert (sizeof([afs for afs in getattr(getattr(self, 'Outer', INDETERMINATE), 'CfsFaces', INDETERMINATE) if not 'ifc4x1.ifcadvancedface' in typeof(afs)]) == 0) is not False

class IfcAdvancedBrepWithVoids_VoidsHaveAdvancedFaces:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAdvancedBrepWithVoids'
    RULE_NAME = 'VoidsHaveAdvancedFaces'

    @staticmethod
    def __call__(self):
        voids = getattr(self, 'Voids', INDETERMINATE)
        assert (sizeof([vsh for vsh in voids if sizeof([afs for afs in getattr(vsh, 'CfsFaces', INDETERMINATE) if not 'ifc4x1.ifcadvancedface' in typeof(afs)]) == 0]) == 0) is not False

class IfcAdvancedFace_ApplicableSurface:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAdvancedFace'
    RULE_NAME = 'ApplicableSurface'

    @staticmethod
    def __call__(self):
        assert (sizeof(['ifc4x1.ifcelementarysurface', 'ifc4x1.ifcsweptsurface', 'ifc4x1.ifcbsplinesurface'] * typeof(getattr(self, 'FaceSurface', INDETERMINATE))) == 1) is not False

class IfcAdvancedFace_RequiresEdgeCurve:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAdvancedFace'
    RULE_NAME = 'RequiresEdgeCurve'

    @staticmethod
    def __call__(self):
        assert (sizeof([elpfbnds for elpfbnds in [bnds for bnds in getattr(self, 'Bounds', INDETERMINATE) if 'ifc4x1.ifcedgeloop' in typeof(getattr(bnds, 'Bound', INDETERMINATE))] if not sizeof([oe for oe in getattr(getattr(elpfbnds, 'Bound', INDETERMINATE), 'EdgeList', INDETERMINATE) if not 'ifc4x1.ifcedgecurve' in typeof(getattr(oe, 'EdgeElement', INDETERMINATE))]) == 0]) == 0) is not False

class IfcAdvancedFace_ApplicableEdgeCurves:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAdvancedFace'
    RULE_NAME = 'ApplicableEdgeCurves'

    @staticmethod
    def __call__(self):
        assert (sizeof([elpfbnds for elpfbnds in [bnds for bnds in getattr(self, 'Bounds', INDETERMINATE) if 'ifc4x1.ifcedgeloop' in typeof(getattr(bnds, 'Bound', INDETERMINATE))] if not sizeof([oe for oe in getattr(getattr(elpfbnds, 'Bound', INDETERMINATE), 'EdgeList', INDETERMINATE) if not sizeof(['ifc4x1.ifcline', 'ifc4x1.ifcconic', 'ifc4x1.ifcpolyline', 'ifc4x1.ifcbsplinecurve'] * typeof(getattr(getattr(oe, 'EdgeElement', INDETERMINATE), 'EdgeGeometry', INDETERMINATE))) == 1]) == 0]) == 0) is not False

class IfcAirTerminal_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAirTerminal'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcAirTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcAirTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcAirTerminal_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAirTerminal'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcairterminaltype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcAirTerminalBox_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAirTerminalBox'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcAirTerminalBoxTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcAirTerminalBoxTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcAirTerminalBox_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAirTerminalBox'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcairterminalboxtype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcAirTerminalBoxType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAirTerminalBoxType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcAirTerminalBoxTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcAirTerminalBoxTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcAirTerminalType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAirTerminalType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcAirTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcAirTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcAirToAirHeatRecovery_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAirToAirHeatRecovery'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcAirToAirHeatRecoveryTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcAirToAirHeatRecoveryTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcAirToAirHeatRecovery_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAirToAirHeatRecovery'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcairtoairheatrecoverytype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcAirToAirHeatRecoveryType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAirToAirHeatRecoveryType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcAirToAirHeatRecoveryTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcAirToAirHeatRecoveryTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcAlarm_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAlarm'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcAlarmTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcAlarmTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcAlarm_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAlarm'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcalarmtype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcAlarmType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAlarmType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcAlarmTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcAlarmTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcApproval_HasIdentifierOrName:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcApproval'
    RULE_NAME = 'HasIdentifierOrName'

    @staticmethod
    def __call__(self):
        identifier = getattr(self, 'Identifier', INDETERMINATE)
        name = getattr(self, 'Name', INDETERMINATE)
        assert (exists(identifier) or exists(name)) is not False

class IfcArbitraryClosedProfileDef_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcArbitraryClosedProfileDef'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        outercurve = getattr(self, 'OuterCurve', INDETERMINATE)
        assert (getattr(outercurve, 'Dim', INDETERMINATE) == 2) is not False

class IfcArbitraryClosedProfileDef_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcArbitraryClosedProfileDef'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        outercurve = getattr(self, 'OuterCurve', INDETERMINATE)
        assert (not 'ifc4x1.ifcline' in typeof(outercurve)) is not False

class IfcArbitraryClosedProfileDef_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcArbitraryClosedProfileDef'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        outercurve = getattr(self, 'OuterCurve', INDETERMINATE)
        assert (not 'ifc4x1.ifcoffsetcurve2d' in typeof(outercurve)) is not False

class IfcArbitraryOpenProfileDef_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcArbitraryOpenProfileDef'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        assert ('ifc4x1.ifccenterlineprofiledef' in typeof(self) or getattr(self, 'ProfileType', INDETERMINATE) == getattr(IfcProfileTypeEnum, 'CURVE', INDETERMINATE)) is not False

class IfcArbitraryOpenProfileDef_WR12:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcArbitraryOpenProfileDef'
    RULE_NAME = 'WR12'

    @staticmethod
    def __call__(self):
        curve = getattr(self, 'Curve', INDETERMINATE)
        assert (getattr(curve, 'Dim', INDETERMINATE) == 2) is not False

class IfcArbitraryProfileDefWithVoids_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcArbitraryProfileDefWithVoids'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (getattr(self, 'ProfileType', INDETERMINATE) == area) is not False

class IfcArbitraryProfileDefWithVoids_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcArbitraryProfileDefWithVoids'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        innercurves = getattr(self, 'InnerCurves', INDETERMINATE)
        assert (sizeof([temp for temp in innercurves if getattr(temp, 'Dim', INDETERMINATE) != 2]) == 0) is not False

class IfcArbitraryProfileDefWithVoids_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcArbitraryProfileDefWithVoids'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        innercurves = getattr(self, 'InnerCurves', INDETERMINATE)
        assert (sizeof([temp for temp in innercurves if 'ifc4x1.ifcline' in typeof(temp)]) == 0) is not False

class IfcAsymmetricIShapeProfileDef_ValidFlangeThickness:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAsymmetricIShapeProfileDef'
    RULE_NAME = 'ValidFlangeThickness'

    @staticmethod
    def __call__(self):
        overalldepth = getattr(self, 'OverallDepth', INDETERMINATE)
        bottomflangethickness = getattr(self, 'BottomFlangeThickness', INDETERMINATE)
        topflangethickness = getattr(self, 'TopFlangeThickness', INDETERMINATE)
        assert (not exists(topflangethickness) or bottomflangethickness + topflangethickness < overalldepth) is not False

class IfcAsymmetricIShapeProfileDef_ValidWebThickness:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAsymmetricIShapeProfileDef'
    RULE_NAME = 'ValidWebThickness'

    @staticmethod
    def __call__(self):
        bottomflangewidth = getattr(self, 'BottomFlangeWidth', INDETERMINATE)
        webthickness = getattr(self, 'WebThickness', INDETERMINATE)
        topflangewidth = getattr(self, 'TopFlangeWidth', INDETERMINATE)
        assert (webthickness < bottomflangewidth and webthickness < topflangewidth) is not False

class IfcAsymmetricIShapeProfileDef_ValidBottomFilletRadius:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAsymmetricIShapeProfileDef'
    RULE_NAME = 'ValidBottomFilletRadius'

    @staticmethod
    def __call__(self):
        bottomflangewidth = getattr(self, 'BottomFlangeWidth', INDETERMINATE)
        webthickness = getattr(self, 'WebThickness', INDETERMINATE)
        bottomflangefilletradius = getattr(self, 'BottomFlangeFilletRadius', INDETERMINATE)
        assert (not exists(bottomflangefilletradius) or bottomflangefilletradius <= (bottomflangewidth - webthickness) / 2.0) is not False

class IfcAsymmetricIShapeProfileDef_ValidTopFilletRadius:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAsymmetricIShapeProfileDef'
    RULE_NAME = 'ValidTopFilletRadius'

    @staticmethod
    def __call__(self):
        webthickness = getattr(self, 'WebThickness', INDETERMINATE)
        topflangewidth = getattr(self, 'TopFlangeWidth', INDETERMINATE)
        topflangefilletradius = getattr(self, 'TopFlangeFilletRadius', INDETERMINATE)
        assert (not exists(topflangefilletradius) or topflangefilletradius <= (topflangewidth - webthickness) / 2.0) is not False

class IfcAudioVisualAppliance_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAudioVisualAppliance'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcAudioVisualApplianceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcAudioVisualApplianceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcAudioVisualAppliance_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAudioVisualAppliance'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcaudiovisualappliancetype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcAudioVisualApplianceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAudioVisualApplianceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcAudioVisualApplianceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcAudioVisualApplianceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcAxis1Placement_AxisIs3D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis1Placement'
    RULE_NAME = 'AxisIs3D'

    @staticmethod
    def __call__(self):
        axis = getattr(self, 'Axis', INDETERMINATE)
        assert (not exists(axis) or getattr(axis, 'Dim', INDETERMINATE) == 3) is not False

class IfcAxis1Placement_LocationIs3D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis1Placement'
    RULE_NAME = 'LocationIs3D'

    @staticmethod
    def __call__(self):
        assert (getattr(getattr(self, 'Location', INDETERMINATE), 'Dim', INDETERMINATE) == 3) is not False

def calc_IfcAxis1Placement_Z(self):
    axis = getattr(self, 'Axis', INDETERMINATE)
    return nvl(IfcNormalise(axis), IfcDirection(DirectionRatios=[0.0, 0.0, 1.0]))

class IfcAxis2Placement2D_RefDirIs2D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis2Placement2D'
    RULE_NAME = 'RefDirIs2D'

    @staticmethod
    def __call__(self):
        refdirection = getattr(self, 'RefDirection', INDETERMINATE)
        assert (not exists(refdirection) or getattr(refdirection, 'Dim', INDETERMINATE) == 2) is not False

class IfcAxis2Placement2D_LocationIs2D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis2Placement2D'
    RULE_NAME = 'LocationIs2D'

    @staticmethod
    def __call__(self):
        assert (getattr(getattr(self, 'Location', INDETERMINATE), 'Dim', INDETERMINATE) == 2) is not False

def calc_IfcAxis2Placement2D_P(self):
    refdirection = getattr(self, 'RefDirection', INDETERMINATE)
    return IfcBuild2Axes(refdirection)

class IfcAxis2Placement3D_LocationIs3D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis2Placement3D'
    RULE_NAME = 'LocationIs3D'

    @staticmethod
    def __call__(self):
        assert (getattr(getattr(self, 'Location', INDETERMINATE), 'Dim', INDETERMINATE) == 3) is not False

class IfcAxis2Placement3D_AxisIs3D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis2Placement3D'
    RULE_NAME = 'AxisIs3D'

    @staticmethod
    def __call__(self):
        axis = getattr(self, 'Axis', INDETERMINATE)
        assert (not exists(axis) or getattr(axis, 'Dim', INDETERMINATE) == 3) is not False

class IfcAxis2Placement3D_RefDirIs3D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis2Placement3D'
    RULE_NAME = 'RefDirIs3D'

    @staticmethod
    def __call__(self):
        refdirection = getattr(self, 'RefDirection', INDETERMINATE)
        assert (not exists(refdirection) or getattr(refdirection, 'Dim', INDETERMINATE) == 3) is not False

class IfcAxis2Placement3D_AxisToRefDirPosition:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis2Placement3D'
    RULE_NAME = 'AxisToRefDirPosition'

    @staticmethod
    def __call__(self):
        axis = getattr(self, 'Axis', INDETERMINATE)
        refdirection = getattr(self, 'RefDirection', INDETERMINATE)
        assert (not exists(axis) or not exists(refdirection) or getattr(IfcCrossProduct(axis, refdirection), 'Magnitude', INDETERMINATE) > 0.0) is not False

class IfcAxis2Placement3D_AxisAndRefDirProvision:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis2Placement3D'
    RULE_NAME = 'AxisAndRefDirProvision'

    @staticmethod
    def __call__(self):
        axis = getattr(self, 'Axis', INDETERMINATE)
        refdirection = getattr(self, 'RefDirection', INDETERMINATE)
        assert (not exists(axis) ^ exists(refdirection)) is not False

def calc_IfcAxis2Placement3D_P(self):
    axis = getattr(self, 'Axis', INDETERMINATE)
    refdirection = getattr(self, 'RefDirection', INDETERMINATE)
    return IfcBuildAxes(axis, refdirection)

class IfcBSplineCurve_SameDim:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBSplineCurve'
    RULE_NAME = 'SameDim'

    @staticmethod
    def __call__(self):
        controlpointslist = getattr(self, 'ControlPointsList', INDETERMINATE)
        assert (sizeof([temp for temp in controlpointslist if getattr(temp, 'Dim', INDETERMINATE) != getattr(express_getitem(controlpointslist, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)]) == 0) is not False

def calc_IfcBSplineCurve_UpperIndexOnControlPoints(self):
    controlpointslist = getattr(self, 'ControlPointsList', INDETERMINATE)
    return sizeof(controlpointslist) - 1

def calc_IfcBSplineCurve_ControlPoints(self):
    controlpointslist = getattr(self, 'ControlPointsList', INDETERMINATE)
    upperindexoncontrolpoints = getattr(self, 'UpperIndexOnControlPoints', INDETERMINATE)
    return IfcListToArray(controlpointslist, 0, upperindexoncontrolpoints)

class IfcBSplineCurveWithKnots_ConsistentBSpline:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBSplineCurveWithKnots'
    RULE_NAME = 'ConsistentBSpline'

    @staticmethod
    def __call__(self):
        degree = getattr(self, 'Degree', INDETERMINATE)
        upperindexoncontrolpoints = getattr(self, 'UpperIndexOnControlPoints', INDETERMINATE)
        knotmultiplicities = getattr(self, 'KnotMultiplicities', INDETERMINATE)
        knots = getattr(self, 'Knots', INDETERMINATE)
        upperindexonknots = getattr(self, 'UpperIndexOnKnots', INDETERMINATE)
        assert IfcConstraintsParamBSpline(degree, upperindexonknots, upperindexoncontrolpoints, knotmultiplicities, knots) is not False

class IfcBSplineCurveWithKnots_CorrespondingKnotLists:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBSplineCurveWithKnots'
    RULE_NAME = 'CorrespondingKnotLists'

    @staticmethod
    def __call__(self):
        knotmultiplicities = getattr(self, 'KnotMultiplicities', INDETERMINATE)
        upperindexonknots = getattr(self, 'UpperIndexOnKnots', INDETERMINATE)
        assert (sizeof(knotmultiplicities) == upperindexonknots) is not False

def calc_IfcBSplineCurveWithKnots_UpperIndexOnKnots(self):
    knots = getattr(self, 'Knots', INDETERMINATE)
    return sizeof(knots)

def calc_IfcBSplineSurface_UUpper(self):
    controlpointslist = getattr(self, 'ControlPointsList', INDETERMINATE)
    return sizeof(controlpointslist) - 1

def calc_IfcBSplineSurface_VUpper(self):
    controlpointslist = getattr(self, 'ControlPointsList', INDETERMINATE)
    return sizeof(express_getitem(controlpointslist, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) - 1

def calc_IfcBSplineSurface_ControlPoints(self):
    controlpointslist = getattr(self, 'ControlPointsList', INDETERMINATE)
    uupper = getattr(self, 'UUpper', INDETERMINATE)
    vupper = getattr(self, 'VUpper', INDETERMINATE)
    return IfcMakeArrayOfArray(controlpointslist, 0, uupper, 0, vupper)

class IfcBSplineSurfaceWithKnots_UDirectionConstraints:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBSplineSurfaceWithKnots'
    RULE_NAME = 'UDirectionConstraints'

    @staticmethod
    def __call__(self):
        umultiplicities = getattr(self, 'UMultiplicities', INDETERMINATE)
        uknots = getattr(self, 'UKnots', INDETERMINATE)
        knotuupper = getattr(self, 'KnotUUpper', INDETERMINATE)
        assert IfcConstraintsParamBSpline(getattr(self, 'UDegree', INDETERMINATE), knotuupper, getattr(self, 'UUpper', INDETERMINATE), umultiplicities, uknots) is not False

class IfcBSplineSurfaceWithKnots_VDirectionConstraints:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBSplineSurfaceWithKnots'
    RULE_NAME = 'VDirectionConstraints'

    @staticmethod
    def __call__(self):
        vmultiplicities = getattr(self, 'VMultiplicities', INDETERMINATE)
        vknots = getattr(self, 'VKnots', INDETERMINATE)
        knotvupper = getattr(self, 'KnotVUpper', INDETERMINATE)
        assert IfcConstraintsParamBSpline(getattr(self, 'VDegree', INDETERMINATE), knotvupper, getattr(self, 'VUpper', INDETERMINATE), vmultiplicities, vknots) is not False

class IfcBSplineSurfaceWithKnots_CorrespondingULists:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBSplineSurfaceWithKnots'
    RULE_NAME = 'CorrespondingULists'

    @staticmethod
    def __call__(self):
        umultiplicities = getattr(self, 'UMultiplicities', INDETERMINATE)
        knotuupper = getattr(self, 'KnotUUpper', INDETERMINATE)
        assert (sizeof(umultiplicities) == knotuupper) is not False

class IfcBSplineSurfaceWithKnots_CorrespondingVLists:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBSplineSurfaceWithKnots'
    RULE_NAME = 'CorrespondingVLists'

    @staticmethod
    def __call__(self):
        vmultiplicities = getattr(self, 'VMultiplicities', INDETERMINATE)
        knotvupper = getattr(self, 'KnotVUpper', INDETERMINATE)
        assert (sizeof(vmultiplicities) == knotvupper) is not False

def calc_IfcBSplineSurfaceWithKnots_KnotVUpper(self):
    vknots = getattr(self, 'VKnots', INDETERMINATE)
    return sizeof(vknots)

def calc_IfcBSplineSurfaceWithKnots_KnotUUpper(self):
    uknots = getattr(self, 'UKnots', INDETERMINATE)
    return sizeof(uknots)

class IfcBeam_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBeam'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcBeamTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcBeamTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcBeam_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBeam'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcbeamtype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcBeamStandardCase_HasMaterialProfileSetUsage:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBeamStandardCase'
    RULE_NAME = 'HasMaterialProfileSetUsage'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in usedin(self, 'ifc4x1.ifcrelassociates.relatedobjects') if 'ifc4x1.ifcrelassociatesmaterial' in typeof(temp) and 'ifc4x1.ifcmaterialprofilesetusage' in typeof(getattr(temp, 'RelatingMaterial', INDETERMINATE))]) == 1) is not False

class IfcBeamType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBeamType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcBeamTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcBeamTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcBlobTexture_SupportedRasterFormat:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBlobTexture'
    RULE_NAME = 'SupportedRasterFormat'

    @staticmethod
    def __call__(self):
        assert (getattr(getattr(self, 'RasterFormat', INDETERMINATE), 'lower', INDETERMINATE)() in ['bmp', 'jpg', 'gif', 'png']) is not False

class IfcBlobTexture_RasterCodeByteStream:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBlobTexture'
    RULE_NAME = 'RasterCodeByteStream'

    @staticmethod
    def __call__(self):
        rastercode = getattr(self, 'RasterCode', INDETERMINATE)
        assert (blength(rastercode) % 8 == 0) is not False

class IfcBoiler_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBoiler'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcBoilerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcBoilerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcBoiler_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBoiler'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcboilertype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcBoilerType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBoilerType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcBoilerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcBoilerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcBooleanClippingResult_FirstOperandType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBooleanClippingResult'
    RULE_NAME = 'FirstOperandType'

    @staticmethod
    def __call__(self):
        firstoperand = getattr(self, 'FirstOperand', INDETERMINATE)
        assert ('ifc4x1.ifcsweptareasolid' in typeof(firstoperand) or 'ifc4x1.ifcsweptdiscsolid' in typeof(firstoperand) or 'ifc4x1.ifcbooleanclippingresult' in typeof(firstoperand)) is not False

class IfcBooleanClippingResult_SecondOperandType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBooleanClippingResult'
    RULE_NAME = 'SecondOperandType'

    @staticmethod
    def __call__(self):
        secondoperand = getattr(self, 'SecondOperand', INDETERMINATE)
        assert ('ifc4x1.ifchalfspacesolid' in typeof(secondoperand)) is not False

class IfcBooleanClippingResult_OperatorType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBooleanClippingResult'
    RULE_NAME = 'OperatorType'

    @staticmethod
    def __call__(self):
        operator = getattr(self, 'Operator', INDETERMINATE)
        assert (operator == difference) is not False

class IfcBooleanResult_SameDim:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBooleanResult'
    RULE_NAME = 'SameDim'

    @staticmethod
    def __call__(self):
        firstoperand = getattr(self, 'FirstOperand', INDETERMINATE)
        secondoperand = getattr(self, 'SecondOperand', INDETERMINATE)
        assert (getattr(firstoperand, 'Dim', INDETERMINATE) == getattr(secondoperand, 'Dim', INDETERMINATE)) is not False

class IfcBooleanResult_FirstOperandClosed:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBooleanResult'
    RULE_NAME = 'FirstOperandClosed'

    @staticmethod
    def __call__(self):
        firstoperand = getattr(self, 'FirstOperand', INDETERMINATE)
        assert (not 'ifc4x1.ifctessellatedfaceset' in typeof(firstoperand) or (exists(getattr(firstoperand, 'Closed', INDETERMINATE)) and getattr(firstoperand, 'Closed', INDETERMINATE))) is not False

class IfcBooleanResult_SecondOperandClosed:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBooleanResult'
    RULE_NAME = 'SecondOperandClosed'

    @staticmethod
    def __call__(self):
        secondoperand = getattr(self, 'SecondOperand', INDETERMINATE)
        assert (not 'ifc4x1.ifctessellatedfaceset' in typeof(secondoperand) or (exists(getattr(secondoperand, 'Closed', INDETERMINATE)) and getattr(secondoperand, 'Closed', INDETERMINATE))) is not False

def calc_IfcBooleanResult_Dim(self):
    firstoperand = getattr(self, 'FirstOperand', INDETERMINATE)
    return getattr(firstoperand, 'Dim', INDETERMINATE)

class IfcBoundaryCurve_IsClosed:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBoundaryCurve'
    RULE_NAME = 'IsClosed'

    @staticmethod
    def __call__(self):
        assert getattr(self, 'ClosedCurve', INDETERMINATE) is not False

def calc_IfcBoundingBox_Dim(self):
    return 3

class IfcBoxedHalfSpace_UnboundedSurface:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBoxedHalfSpace'
    RULE_NAME = 'UnboundedSurface'

    @staticmethod
    def __call__(self):
        assert (not 'ifc4x1.ifccurveboundedplane' in typeof(getattr(self, 'BaseSurface', INDETERMINATE))) is not False

class IfcBuildingElement_MaxOneMaterialAssociation:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBuildingElement'
    RULE_NAME = 'MaxOneMaterialAssociation'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in getattr(self, 'HasAssociations', INDETERMINATE) if 'ifc4x1.ifcrelassociatesmaterial' in typeof(temp)]) <= 1) is not False

class IfcBuildingElementPart_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBuildingElementPart'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcBuildingElementPartTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcBuildingElementPartTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcBuildingElementPart_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBuildingElementPart'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcbuildingelementparttype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcBuildingElementPartType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBuildingElementPartType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcBuildingElementPartTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcBuildingElementPartTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcBuildingElementProxy_HasObjectName:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBuildingElementProxy'
    RULE_NAME = 'HasObjectName'

    @staticmethod
    def __call__(self):
        assert exists(getattr(self, 'Name', INDETERMINATE)) is not False

class IfcBuildingElementProxy_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBuildingElementProxy'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcBuildingElementProxyTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcBuildingElementProxyTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcBuildingElementProxy_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBuildingElementProxy'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcbuildingelementproxytype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcBuildingElementProxyType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBuildingElementProxyType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcBuildingElementProxyTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcBuildingElementProxyTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcBurner_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBurner'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcBurnerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcBurnerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcBurner_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBurner'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcburnertype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcBurnerType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBurnerType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcBurnerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcBurnerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCShapeProfileDef_ValidGirth:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCShapeProfileDef'
    RULE_NAME = 'ValidGirth'

    @staticmethod
    def __call__(self):
        depth = getattr(self, 'Depth', INDETERMINATE)
        girth = getattr(self, 'Girth', INDETERMINATE)
        assert (girth < depth / 2.0) is not False

class IfcCShapeProfileDef_ValidInternalFilletRadius:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCShapeProfileDef'
    RULE_NAME = 'ValidInternalFilletRadius'

    @staticmethod
    def __call__(self):
        depth = getattr(self, 'Depth', INDETERMINATE)
        width = getattr(self, 'Width', INDETERMINATE)
        wallthickness = getattr(self, 'WallThickness', INDETERMINATE)
        internalfilletradius = getattr(self, 'InternalFilletRadius', INDETERMINATE)
        assert (not exists(internalfilletradius) or (internalfilletradius <= width / 2.0 - wallthickness and internalfilletradius <= depth / 2.0 - wallthickness)) is not False

class IfcCShapeProfileDef_ValidWallThickness:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCShapeProfileDef'
    RULE_NAME = 'ValidWallThickness'

    @staticmethod
    def __call__(self):
        depth = getattr(self, 'Depth', INDETERMINATE)
        width = getattr(self, 'Width', INDETERMINATE)
        wallthickness = getattr(self, 'WallThickness', INDETERMINATE)
        assert (wallthickness < width / 2.0 and wallthickness < depth / 2.0) is not False

class IfcCableCarrierFitting_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCableCarrierFitting'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcCableCarrierFittingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCableCarrierFittingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcCableCarrierFitting_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCableCarrierFitting'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifccablecarrierfittingtype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcCableCarrierFittingType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCableCarrierFittingType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcCableCarrierFittingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCableCarrierFittingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCableCarrierSegment_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCableCarrierSegment'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcCableCarrierSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCableCarrierSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcCableCarrierSegment_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCableCarrierSegment'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifccablecarriersegmenttype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcCableCarrierSegmentType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCableCarrierSegmentType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcCableCarrierSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCableCarrierSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCableFitting_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCableFitting'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcCableFittingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCableFittingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcCableFitting_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCableFitting'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifccablefittingtype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcCableFittingType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCableFittingType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcCableFittingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCableFittingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCableSegment_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCableSegment'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcCableSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCableSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcCableSegment_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCableSegment'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifccablesegmenttype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcCableSegmentType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCableSegmentType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcCableSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCableSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCartesianPoint_CP2Dor3D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianPoint'
    RULE_NAME = 'CP2Dor3D'

    @staticmethod
    def __call__(self):
        coordinates = getattr(self, 'Coordinates', INDETERMINATE)
        assert (hiindex(coordinates) >= 2) is not False

def calc_IfcCartesianPoint_Dim(self):
    coordinates = getattr(self, 'Coordinates', INDETERMINATE)
    return hiindex(coordinates)

def calc_IfcCartesianPointList_Dim(self):
    return IfcPointListDim(self)

class IfcCartesianTransformationOperator_ScaleGreaterZero:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator'
    RULE_NAME = 'ScaleGreaterZero'

    @staticmethod
    def __call__(self):
        scl = getattr(self, 'Scl', INDETERMINATE)
        assert (scl > 0.0) is not False

def calc_IfcCartesianTransformationOperator_Scl(self):
    scale = getattr(self, 'Scale', INDETERMINATE)
    return nvl(scale, 1.0)

def calc_IfcCartesianTransformationOperator_Dim(self):
    localorigin = getattr(self, 'LocalOrigin', INDETERMINATE)
    return getattr(localorigin, 'Dim', INDETERMINATE)

class IfcCartesianTransformationOperator2D_DimEqual2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator2D'
    RULE_NAME = 'DimEqual2'

    @staticmethod
    def __call__(self):
        assert (getattr(self, 'Dim', INDETERMINATE) == 2) is not False

class IfcCartesianTransformationOperator2D_Axis1Is2D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator2D'
    RULE_NAME = 'Axis1Is2D'

    @staticmethod
    def __call__(self):
        assert (not exists(getattr(self, 'Axis1', INDETERMINATE)) or getattr(getattr(self, 'Axis1', INDETERMINATE), 'Dim', INDETERMINATE) == 2) is not False

class IfcCartesianTransformationOperator2D_Axis2Is2D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator2D'
    RULE_NAME = 'Axis2Is2D'

    @staticmethod
    def __call__(self):
        assert (not exists(getattr(self, 'Axis2', INDETERMINATE)) or getattr(getattr(self, 'Axis2', INDETERMINATE), 'Dim', INDETERMINATE) == 2) is not False

def calc_IfcCartesianTransformationOperator2D_U(self):
    return IfcBaseAxis(2, getattr(self, 'Axis1', INDETERMINATE), getattr(self, 'Axis2', INDETERMINATE), None)

class IfcCartesianTransformationOperator2DnonUniform_Scale2GreaterZero:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator2DnonUniform'
    RULE_NAME = 'Scale2GreaterZero'

    @staticmethod
    def __call__(self):
        scl2 = getattr(self, 'Scl2', INDETERMINATE)
        assert (scl2 > 0.0) is not False

def calc_IfcCartesianTransformationOperator2DnonUniform_Scl2(self):
    scale2 = getattr(self, 'Scale2', INDETERMINATE)
    return nvl(scale2, getattr(self, 'Scl', INDETERMINATE))

class IfcCartesianTransformationOperator3D_DimIs3D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator3D'
    RULE_NAME = 'DimIs3D'

    @staticmethod
    def __call__(self):
        assert (getattr(self, 'Dim', INDETERMINATE) == 3) is not False

class IfcCartesianTransformationOperator3D_Axis1Is3D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator3D'
    RULE_NAME = 'Axis1Is3D'

    @staticmethod
    def __call__(self):
        assert (not exists(getattr(self, 'Axis1', INDETERMINATE)) or getattr(getattr(self, 'Axis1', INDETERMINATE), 'Dim', INDETERMINATE) == 3) is not False

class IfcCartesianTransformationOperator3D_Axis2Is3D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator3D'
    RULE_NAME = 'Axis2Is3D'

    @staticmethod
    def __call__(self):
        assert (not exists(getattr(self, 'Axis2', INDETERMINATE)) or getattr(getattr(self, 'Axis2', INDETERMINATE), 'Dim', INDETERMINATE) == 3) is not False

class IfcCartesianTransformationOperator3D_Axis3Is3D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator3D'
    RULE_NAME = 'Axis3Is3D'

    @staticmethod
    def __call__(self):
        axis3 = getattr(self, 'Axis3', INDETERMINATE)
        assert (not exists(axis3) or getattr(axis3, 'Dim', INDETERMINATE) == 3) is not False

def calc_IfcCartesianTransformationOperator3D_U(self):
    axis3 = getattr(self, 'Axis3', INDETERMINATE)
    return IfcBaseAxis(3, getattr(self, 'Axis1', INDETERMINATE), getattr(self, 'Axis2', INDETERMINATE), axis3)

class IfcCartesianTransformationOperator3DnonUniform_Scale2GreaterZero:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator3DnonUniform'
    RULE_NAME = 'Scale2GreaterZero'

    @staticmethod
    def __call__(self):
        scl2 = getattr(self, 'Scl2', INDETERMINATE)
        assert (scl2 > 0.0) is not False

class IfcCartesianTransformationOperator3DnonUniform_Scale3GreaterZero:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator3DnonUniform'
    RULE_NAME = 'Scale3GreaterZero'

    @staticmethod
    def __call__(self):
        scl3 = getattr(self, 'Scl3', INDETERMINATE)
        assert (scl3 > 0.0) is not False

def calc_IfcCartesianTransformationOperator3DnonUniform_Scl2(self):
    scale2 = getattr(self, 'Scale2', INDETERMINATE)
    return nvl(scale2, getattr(self, 'Scl', INDETERMINATE))

def calc_IfcCartesianTransformationOperator3DnonUniform_Scl3(self):
    scale3 = getattr(self, 'Scale3', INDETERMINATE)
    return nvl(scale3, getattr(self, 'Scl', INDETERMINATE))

class IfcChiller_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcChiller'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcChillerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcChillerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcChiller_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcChiller'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcchillertype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcChillerType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcChillerType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcChillerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcChillerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcChimney_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcChimney'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcChimneyTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcChimneyTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcChimney_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcChimney'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcchimneytype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcChimneyType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcChimneyType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcChimneyTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcChimneyTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCircleHollowProfileDef_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCircleHollowProfileDef'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        wallthickness = getattr(self, 'WallThickness', INDETERMINATE)
        assert (wallthickness < getattr(self, 'Radius', INDETERMINATE)) is not False

class IfcCoil_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCoil'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcCoilTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCoilTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcCoil_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCoil'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifccoiltype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcCoilType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCoilType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcCoilTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCoilTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcColumn_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcColumn'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcColumnTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcColumnTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcColumn_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcColumn'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifccolumntype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcColumnStandardCase_HasMaterialProfileSetUsage:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcColumnStandardCase'
    RULE_NAME = 'HasMaterialProfileSetUsage'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in usedin(self, 'ifc4x1.ifcrelassociates.relatedobjects') if 'ifc4x1.ifcrelassociatesmaterial' in typeof(temp) and 'ifc4x1.ifcmaterialprofilesetusage' in typeof(getattr(temp, 'RelatingMaterial', INDETERMINATE))]) == 1) is not False

class IfcColumnType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcColumnType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcColumnTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcColumnTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCommunicationsAppliance_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCommunicationsAppliance'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcCommunicationsApplianceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCommunicationsApplianceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcCommunicationsAppliance_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCommunicationsAppliance'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifccommunicationsappliancetype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcCommunicationsApplianceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCommunicationsApplianceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcCommunicationsApplianceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCommunicationsApplianceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcComplexProperty_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcComplexProperty'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        hasproperties = getattr(self, 'HasProperties', INDETERMINATE)
        assert (sizeof([temp for temp in hasproperties if self == temp]) == 0) is not False

class IfcComplexProperty_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcComplexProperty'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        hasproperties = getattr(self, 'HasProperties', INDETERMINATE)
        assert IfcUniquePropertyName(hasproperties) is not False

class IfcComplexPropertyTemplate_UniquePropertyNames:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcComplexPropertyTemplate'
    RULE_NAME = 'UniquePropertyNames'

    @staticmethod
    def __call__(self):
        haspropertytemplates = getattr(self, 'HasPropertyTemplates', INDETERMINATE)
        assert IfcUniquePropertyTemplateNames(haspropertytemplates) is not False

class IfcComplexPropertyTemplate_NoSelfReference:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcComplexPropertyTemplate'
    RULE_NAME = 'NoSelfReference'

    @staticmethod
    def __call__(self):
        haspropertytemplates = getattr(self, 'HasPropertyTemplates', INDETERMINATE)
        assert (sizeof([temp for temp in haspropertytemplates if self == temp]) == 0) is not False

class IfcCompositeCurve_CurveContinuous:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCompositeCurve'
    RULE_NAME = 'CurveContinuous'

    @staticmethod
    def __call__(self):
        segments = getattr(self, 'Segments', INDETERMINATE)
        closedcurve = getattr(self, 'ClosedCurve', INDETERMINATE)
        assert (not closedcurve and sizeof([temp for temp in segments if getattr(temp, 'Transition', INDETERMINATE) == discontinuous]) == 1 or (closedcurve and sizeof([temp for temp in segments if getattr(temp, 'Transition', INDETERMINATE) == discontinuous]) == 0)) is not False

class IfcCompositeCurve_SameDim:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCompositeCurve'
    RULE_NAME = 'SameDim'

    @staticmethod
    def __call__(self):
        segments = getattr(self, 'Segments', INDETERMINATE)
        assert (sizeof([temp for temp in segments if getattr(temp, 'Dim', INDETERMINATE) != getattr(express_getitem(segments, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)]) == 0) is not False

def calc_IfcCompositeCurve_NSegments(self):
    segments = getattr(self, 'Segments', INDETERMINATE)
    return sizeof(segments)

def calc_IfcCompositeCurve_ClosedCurve(self):
    segments = getattr(self, 'Segments', INDETERMINATE)
    nsegments = getattr(self, 'NSegments', INDETERMINATE)
    return getattr(express_getitem(segments, nsegments - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Transition', INDETERMINATE) != discontinuous

class IfcCompositeCurveOnSurface_SameSurface:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCompositeCurveOnSurface'
    RULE_NAME = 'SameSurface'

    @staticmethod
    def __call__(self):
        basissurface = getattr(self, 'BasisSurface', INDETERMINATE)
        assert (sizeof(basissurface) > 0) is not False

def calc_IfcCompositeCurveOnSurface_BasisSurface(self):
    return IfcGetBasisSurface(self)

class IfcCompositeCurveSegment_ParentIsBoundedCurve:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCompositeCurveSegment'
    RULE_NAME = 'ParentIsBoundedCurve'

    @staticmethod
    def __call__(self):
        parentcurve = getattr(self, 'ParentCurve', INDETERMINATE)
        assert ('ifc4x1.ifcboundedcurve' in typeof(parentcurve)) is not False

def calc_IfcCompositeCurveSegment_Dim(self):
    parentcurve = getattr(self, 'ParentCurve', INDETERMINATE)
    return getattr(parentcurve, 'Dim', INDETERMINATE)

class IfcCompositeProfileDef_InvariantProfileType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCompositeProfileDef'
    RULE_NAME = 'InvariantProfileType'

    @staticmethod
    def __call__(self):
        profiles = getattr(self, 'Profiles', INDETERMINATE)
        assert (sizeof([temp for temp in profiles if getattr(temp, 'ProfileType', INDETERMINATE) != getattr(express_getitem(profiles, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'ProfileType', INDETERMINATE)]) == 0) is not False

class IfcCompositeProfileDef_NoRecursion:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCompositeProfileDef'
    RULE_NAME = 'NoRecursion'

    @staticmethod
    def __call__(self):
        profiles = getattr(self, 'Profiles', INDETERMINATE)
        assert (sizeof([temp for temp in profiles if 'ifc4x1.ifccompositeprofiledef' in typeof(temp)]) == 0) is not False

class IfcCompressor_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCompressor'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcCompressorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCompressorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcCompressor_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCompressor'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifccompressortype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcCompressorType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCompressorType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcCompressorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCompressorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCondenser_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCondenser'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcCondenserTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCondenserTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcCondenser_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCondenser'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifccondensertype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcCondenserType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCondenserType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcCondenserTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCondenserTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcConstraint_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConstraint'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        constraintgrade = getattr(self, 'ConstraintGrade', INDETERMINATE)
        assert (constraintgrade != getattr(IfcConstraintEnum, 'USERDEFINED', INDETERMINATE) or (constraintgrade == getattr(IfcConstraintEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'UserDefinedGrade', INDETERMINATE)))) is not False

class IfcConstructionEquipmentResource_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConstructionEquipmentResource'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcConstructionEquipmentResourceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcConstructionEquipmentResourceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcConstructionEquipmentResourceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConstructionEquipmentResourceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcConstructionEquipmentResourceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcConstructionEquipmentResourceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ResourceType', INDETERMINATE)))) is not False

class IfcConstructionMaterialResource_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConstructionMaterialResource'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcConstructionMaterialResourceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcConstructionMaterialResourceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcConstructionMaterialResourceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConstructionMaterialResourceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcConstructionMaterialResourceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcConstructionMaterialResourceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ResourceType', INDETERMINATE)))) is not False

class IfcConstructionProductResource_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConstructionProductResource'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcConstructionProductResourceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcConstructionProductResourceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcConstructionProductResourceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConstructionProductResourceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcConstructionProductResourceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcConstructionProductResourceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ResourceType', INDETERMINATE)))) is not False

class IfcController_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcController'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcControllerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcControllerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcController_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcController'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifccontrollertype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcControllerType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcControllerType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcControllerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcControllerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCooledBeam_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCooledBeam'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcCooledBeamTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCooledBeamTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcCooledBeam_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCooledBeam'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifccooledbeamtype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcCooledBeamType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCooledBeamType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcCooledBeamTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCooledBeamTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCoolingTower_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCoolingTower'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcCoolingTowerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCoolingTowerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcCoolingTower_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCoolingTower'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifccoolingtowertype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcCoolingTowerType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCoolingTowerType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcCoolingTowerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCoolingTowerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCovering_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCovering'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcCoveringTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCoveringTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcCovering_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCovering'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifccoveringtype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcCoveringType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCoveringType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcCoveringTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCoveringTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCrewResource_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCrewResource'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcCrewResourceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCrewResourceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcCrewResourceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCrewResourceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcCrewResourceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCrewResourceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ResourceType', INDETERMINATE)))) is not False

def calc_IfcCsgPrimitive3D_Dim(self):
    return 3

class IfcCurtainWall_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCurtainWall'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcCurtainWallTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCurtainWallTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcCurtainWall_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCurtainWall'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifccurtainwalltype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcCurtainWallType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCurtainWallType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcCurtainWallTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCurtainWallTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

def calc_IfcCurve_Dim(self):
    return IfcCurveDim(self)

class IfcCurveStyle_MeasureOfWidth:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCurveStyle'
    RULE_NAME = 'MeasureOfWidth'

    @staticmethod
    def __call__(self):
        curvewidth = getattr(self, 'CurveWidth', INDETERMINATE)
        assert (not exists(curvewidth) or 'ifc4x1.ifcpositivelengthmeasure' in typeof(curvewidth) or ('ifc4x1.ifcdescriptivemeasure' in typeof(curvewidth) and curvewidth == 'bylayer')) is not False

class IfcCurveStyle_IdentifiableCurveStyle:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCurveStyle'
    RULE_NAME = 'IdentifiableCurveStyle'

    @staticmethod
    def __call__(self):
        curvefont = getattr(self, 'CurveFont', INDETERMINATE)
        curvewidth = getattr(self, 'CurveWidth', INDETERMINATE)
        curvecolour = getattr(self, 'CurveColour', INDETERMINATE)
        assert (exists(curvefont) or exists(curvewidth) or exists(curvecolour)) is not False

class IfcCurveStyleFontPattern_VisibleLengthGreaterEqualZero:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCurveStyleFontPattern'
    RULE_NAME = 'VisibleLengthGreaterEqualZero'

    @staticmethod
    def __call__(self):
        visiblesegmentlength = getattr(self, 'VisibleSegmentLength', INDETERMINATE)
        assert (visiblesegmentlength >= 0.0) is not False

class IfcDamper_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDamper'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcDamperTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcDamperTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcDamper_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDamper'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcdampertype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcDamperType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDamperType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcDamperTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcDamperTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcDerivedProfileDef_InvariantProfileType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDerivedProfileDef'
    RULE_NAME = 'InvariantProfileType'

    @staticmethod
    def __call__(self):
        parentprofile = getattr(self, 'ParentProfile', INDETERMINATE)
        assert (getattr(self, 'ProfileType', INDETERMINATE) == getattr(parentprofile, 'ProfileType', INDETERMINATE)) is not False

class IfcDerivedUnit_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDerivedUnit'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        elements = getattr(self, 'Elements', INDETERMINATE)
        assert (sizeof(elements) > 1 or (sizeof(elements) == 1 and getattr(express_getitem(elements, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Exponent', INDETERMINATE) != 1)) is not False

class IfcDerivedUnit_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDerivedUnit'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        unittype = getattr(self, 'UnitType', INDETERMINATE)
        assert (unittype != getattr(IfcDerivedUnitEnum, 'USERDEFINED', INDETERMINATE) or (unittype == getattr(IfcDerivedUnitEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'UserDefinedType', INDETERMINATE)))) is not False

def calc_IfcDerivedUnit_Dimensions(self):
    elements = getattr(self, 'Elements', INDETERMINATE)
    return IfcDeriveDimensionalExponents(elements)

class IfcDirection_MagnitudeGreaterZero:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDirection'
    RULE_NAME = 'MagnitudeGreaterZero'

    @staticmethod
    def __call__(self):
        directionratios = getattr(self, 'DirectionRatios', INDETERMINATE)
        assert (sizeof([tmp for tmp in directionratios if tmp != 0.0]) > 0) is not False

def calc_IfcDirection_Dim(self):
    directionratios = getattr(self, 'DirectionRatios', INDETERMINATE)
    return hiindex(directionratios)

class IfcDiscreteAccessory_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDiscreteAccessory'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcDiscreteAccessoryTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcDiscreteAccessoryTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcDiscreteAccessory_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDiscreteAccessory'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcdiscreteaccessorytype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcDiscreteAccessoryType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDiscreteAccessoryType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcDiscreteAccessoryTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcDiscreteAccessoryTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcDistributionChamberElement_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDistributionChamberElement'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcDistributionChamberElementTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcDistributionChamberElementTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcDistributionChamberElement_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDistributionChamberElement'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcdistributionchamberelementtype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcDistributionChamberElementType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDistributionChamberElementType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcDistributionChamberElementTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcDistributionChamberElementTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcDocumentReference_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDocumentReference'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        name = getattr(self, 'Name', INDETERMINATE)
        referenceddocument = getattr(self, 'ReferencedDocument', INDETERMINATE)
        assert exists(name) ^ exists(referenceddocument) is not False

class IfcDoor_CorrectStyleAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDoor'
    RULE_NAME = 'CorrectStyleAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcdoortype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcDoorLiningProperties_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDoorLiningProperties'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        liningdepth = getattr(self, 'LiningDepth', INDETERMINATE)
        liningthickness = getattr(self, 'LiningThickness', INDETERMINATE)
        assert (not (exists(liningdepth) and (not exists(liningthickness)))) is not False

class IfcDoorLiningProperties_WR32:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDoorLiningProperties'
    RULE_NAME = 'WR32'

    @staticmethod
    def __call__(self):
        thresholddepth = getattr(self, 'ThresholdDepth', INDETERMINATE)
        thresholdthickness = getattr(self, 'ThresholdThickness', INDETERMINATE)
        assert (not (exists(thresholddepth) and (not exists(thresholdthickness)))) is not False

class IfcDoorLiningProperties_WR33:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDoorLiningProperties'
    RULE_NAME = 'WR33'

    @staticmethod
    def __call__(self):
        transomthickness = getattr(self, 'TransomThickness', INDETERMINATE)
        transomoffset = getattr(self, 'TransomOffset', INDETERMINATE)
        assert (exists(transomoffset) and exists(transomthickness)) ^ (not exists(transomoffset) and (not exists(transomthickness))) is not False

class IfcDoorLiningProperties_WR34:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDoorLiningProperties'
    RULE_NAME = 'WR34'

    @staticmethod
    def __call__(self):
        casingthickness = getattr(self, 'CasingThickness', INDETERMINATE)
        casingdepth = getattr(self, 'CasingDepth', INDETERMINATE)
        assert (exists(casingdepth) and exists(casingthickness)) ^ (not exists(casingdepth) and (not exists(casingthickness))) is not False

class IfcDoorLiningProperties_WR35:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDoorLiningProperties'
    RULE_NAME = 'WR35'

    @staticmethod
    def __call__(self):
        assert (exists(lambda : express_getitem(getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and ('ifc4x1.ifcdoortype' in typeof(express_getitem(getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) or 'ifc4x1.ifcdoorstyle' in typeof(express_getitem(getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)))) is not False

class IfcDoorPanelProperties_ApplicableToType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDoorPanelProperties'
    RULE_NAME = 'ApplicableToType'

    @staticmethod
    def __call__(self):
        assert (exists(lambda : express_getitem(getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and ('ifc4x1.ifcdoortype' in typeof(express_getitem(getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) or 'ifc4x1.ifcdoorstyle' in typeof(express_getitem(getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)))) is not False

class IfcDoorType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDoorType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcDoorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcDoorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcDraughtingPreDefinedColour_PreDefinedColourNames:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDraughtingPreDefinedColour'
    RULE_NAME = 'PreDefinedColourNames'

    @staticmethod
    def __call__(self):
        assert (getattr(getattr(self, 'Name', INDETERMINATE), 'lower', INDETERMINATE)() in ['black', 'red', 'green', 'blue', 'yellow', 'magenta', 'cyan', 'white', 'bylayer']) is not False

class IfcDraughtingPreDefinedCurveFont_PreDefinedCurveFontNames:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDraughtingPreDefinedCurveFont'
    RULE_NAME = 'PreDefinedCurveFontNames'

    @staticmethod
    def __call__(self):
        assert (getattr(getattr(self, 'Name', INDETERMINATE), 'lower', INDETERMINATE)() in ['continuous', 'chain', 'chaindoubledash', 'dashed', 'dotted', 'bylayer']) is not False

class IfcDuctFitting_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDuctFitting'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcDuctFittingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcDuctFittingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcDuctFitting_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDuctFitting'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcductfittingtype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcDuctFittingType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDuctFittingType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcDuctFittingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcDuctFittingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcDuctSegment_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDuctSegment'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcDuctSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcDuctSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcDuctSegment_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDuctSegment'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcductsegmenttype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcDuctSegmentType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDuctSegmentType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcDuctSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcDuctSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcDuctSilencer_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDuctSilencer'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcDuctSilencerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcDuctSilencerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcDuctSilencer_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDuctSilencer'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcductsilencertype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcDuctSilencerType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDuctSilencerType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcDuctSilencerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcDuctSilencerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcEdgeLoop_IsClosed:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEdgeLoop'
    RULE_NAME = 'IsClosed'

    @staticmethod
    def __call__(self):
        edgelist = getattr(self, 'EdgeList', INDETERMINATE)
        ne = getattr(self, 'Ne', INDETERMINATE)
        assert (getattr(express_getitem(edgelist, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'EdgeStart', INDETERMINATE) == getattr(express_getitem(edgelist, ne - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'EdgeEnd', INDETERMINATE)) is not False

class IfcEdgeLoop_IsContinuous:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEdgeLoop'
    RULE_NAME = 'IsContinuous'

    @staticmethod
    def __call__(self):
        assert IfcLoopHeadToTail(self) is not False

def calc_IfcEdgeLoop_Ne(self):
    edgelist = getattr(self, 'EdgeList', INDETERMINATE)
    return sizeof(edgelist)

class IfcElectricAppliance_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricAppliance'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcElectricApplianceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcElectricApplianceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcElectricAppliance_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricAppliance'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcelectricappliancetype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcElectricApplianceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricApplianceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcElectricApplianceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcElectricApplianceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcElectricDistributionBoard_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricDistributionBoard'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcElectricDistributionBoardTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcElectricDistributionBoardTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcElectricDistributionBoard_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricDistributionBoard'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcelectricdistributionboardtype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcElectricDistributionBoardType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricDistributionBoardType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcElectricDistributionBoardTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcElectricDistributionBoardTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcElectricFlowStorageDevice_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricFlowStorageDevice'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcElectricFlowStorageDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcElectricFlowStorageDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcElectricFlowStorageDevice_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricFlowStorageDevice'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcelectricflowstoragedevicetype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcElectricFlowStorageDeviceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricFlowStorageDeviceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcElectricFlowStorageDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcElectricFlowStorageDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcElectricGenerator_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricGenerator'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcElectricGeneratorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcElectricGeneratorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcElectricGenerator_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricGenerator'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcelectricgeneratortype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcElectricGeneratorType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricGeneratorType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcElectricGeneratorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcElectricGeneratorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcElectricMotor_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricMotor'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcElectricMotorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcElectricMotorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcElectricMotor_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricMotor'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcelectricmotortype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcElectricMotorType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricMotorType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcElectricMotorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcElectricMotorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcElectricTimeControl_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricTimeControl'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcElectricTimeControlTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcElectricTimeControlTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcElectricTimeControl_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricTimeControl'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcelectrictimecontroltype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcElectricTimeControlType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricTimeControlType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcElectricTimeControlTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcElectricTimeControlTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcElementAssembly_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElementAssembly'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcElementAssemblyTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcElementAssemblyTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcElementAssembly_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElementAssembly'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcelementassemblytype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcElementAssemblyType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElementAssemblyType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcElementAssemblyTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcElementAssemblyTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcElementQuantity_UniqueQuantityNames:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElementQuantity'
    RULE_NAME = 'UniqueQuantityNames'

    @staticmethod
    def __call__(self):
        quantities = getattr(self, 'Quantities', INDETERMINATE)
        assert IfcUniqueQuantityNames(quantities) is not False

class IfcEngine_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEngine'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcEngineTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcEngineTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcEngine_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEngine'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcenginetype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcEngineType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEngineType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcEngineTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcEngineTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcEvaporativeCooler_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEvaporativeCooler'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcEvaporativeCoolerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcEvaporativeCoolerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcEvaporativeCooler_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEvaporativeCooler'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcevaporativecoolertype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcEvaporativeCoolerType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEvaporativeCoolerType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcEvaporativeCoolerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcEvaporativeCoolerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcEvaporator_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEvaporator'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcEvaporatorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcEvaporatorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcEvaporator_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEvaporator'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcevaporatortype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcEvaporatorType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEvaporatorType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcEvaporatorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcEvaporatorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcEvent_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEvent'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcEventTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcEventTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcEvent_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEvent'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        eventtriggertype = getattr(self, 'EventTriggerType', INDETERMINATE)
        userdefinedeventtriggertype = getattr(self, 'UserDefinedEventTriggerType', INDETERMINATE)
        assert (not exists(eventtriggertype) or eventtriggertype != getattr(IfcEventTriggerTypeEnum, 'USERDEFINED', INDETERMINATE) or (eventtriggertype == getattr(IfcEventTriggerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(userdefinedeventtriggertype))) is not False

class IfcEventType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEventType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcEventTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcEventTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ProcessType', INDETERMINATE)))) is not False

class IfcEventType_CorrectEventTriggerType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEventType'
    RULE_NAME = 'CorrectEventTriggerType'

    @staticmethod
    def __call__(self):
        eventtriggertype = getattr(self, 'EventTriggerType', INDETERMINATE)
        userdefinedeventtriggertype = getattr(self, 'UserDefinedEventTriggerType', INDETERMINATE)
        assert (eventtriggertype != getattr(IfcEventTriggerTypeEnum, 'USERDEFINED', INDETERMINATE) or (eventtriggertype == getattr(IfcEventTriggerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(userdefinedeventtriggertype))) is not False

class IfcExternalReference_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcExternalReference'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        location = getattr(self, 'Location', INDETERMINATE)
        identification = getattr(self, 'Identification', INDETERMINATE)
        name = getattr(self, 'Name', INDETERMINATE)
        assert (exists(identification) or exists(location) or exists(name)) is not False

class IfcExtrudedAreaSolid_ValidExtrusionDirection:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcExtrudedAreaSolid'
    RULE_NAME = 'ValidExtrusionDirection'

    @staticmethod
    def __call__(self):
        assert (IfcDotProduct(IfcDirection(DirectionRatios=[0.0, 0.0, 1.0]), getattr(self, 'ExtrudedDirection', INDETERMINATE)) != 0.0) is not False

class IfcExtrudedAreaSolidTapered_CorrectProfileAssignment:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcExtrudedAreaSolidTapered'
    RULE_NAME = 'CorrectProfileAssignment'

    @staticmethod
    def __call__(self):
        assert IfcTaperedSweptAreaProfiles(getattr(self, 'SweptArea', INDETERMINATE), getattr(self, 'EndSweptArea', INDETERMINATE)) is not False

class IfcFace_HasOuterBound:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFace'
    RULE_NAME = 'HasOuterBound'

    @staticmethod
    def __call__(self):
        bounds = getattr(self, 'Bounds', INDETERMINATE)
        assert (sizeof([temp for temp in bounds if 'ifc4x1.ifcfaceouterbound' in typeof(temp)]) <= 1) is not False

def calc_IfcFaceBasedSurfaceModel_Dim(self):
    return 3

class IfcFan_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFan'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcFanTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcFanTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcFan_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFan'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcfantype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcFanType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFanType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcFanTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcFanTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcFastener_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFastener'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcFastenerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcFastenerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcFastener_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFastener'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcfastenertype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcFastenerType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFastenerType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcFastenerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcFastenerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcFeatureElementSubtraction_HasNoSubtraction:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFeatureElementSubtraction'
    RULE_NAME = 'HasNoSubtraction'

    @staticmethod
    def __call__(self):
        assert (sizeof(getattr(self, 'HasOpenings', INDETERMINATE)) == 0) is not False

class IfcFeatureElementSubtraction_IsNotFilling:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFeatureElementSubtraction'
    RULE_NAME = 'IsNotFilling'

    @staticmethod
    def __call__(self):
        assert (sizeof(getattr(self, 'FillsVoids', INDETERMINATE)) == 0) is not False

class IfcFillAreaStyle_MaxOneColour:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFillAreaStyle'
    RULE_NAME = 'MaxOneColour'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in getattr(self, 'FillStyles', INDETERMINATE) if 'ifc4x1.ifccolour' in typeof(style)]) <= 1) is not False

class IfcFillAreaStyle_MaxOneExtHatchStyle:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFillAreaStyle'
    RULE_NAME = 'MaxOneExtHatchStyle'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in getattr(self, 'FillStyles', INDETERMINATE) if 'ifc4x1.ifcexternallydefinedhatchstyle' in typeof(style)]) <= 1) is not False

class IfcFillAreaStyle_ConsistentHatchStyleDef:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFillAreaStyle'
    RULE_NAME = 'ConsistentHatchStyleDef'

    @staticmethod
    def __call__(self):
        assert IfcCorrectFillAreaStyle(getattr(self, 'FillStyles', INDETERMINATE)) is not False

class IfcFillAreaStyleHatching_PatternStart2D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFillAreaStyleHatching'
    RULE_NAME = 'PatternStart2D'

    @staticmethod
    def __call__(self):
        patternstart = getattr(self, 'PatternStart', INDETERMINATE)
        assert (not exists(patternstart) or getattr(patternstart, 'Dim', INDETERMINATE) == 2) is not False

class IfcFillAreaStyleHatching_RefHatchLine2D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFillAreaStyleHatching'
    RULE_NAME = 'RefHatchLine2D'

    @staticmethod
    def __call__(self):
        pointofreferencehatchline = getattr(self, 'PointOfReferenceHatchLine', INDETERMINATE)
        assert (not exists(pointofreferencehatchline) or getattr(pointofreferencehatchline, 'Dim', INDETERMINATE) == 2) is not False

class IfcFilter_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFilter'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcFilterTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcFilterTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcFilter_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFilter'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcfiltertype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcFilterType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFilterType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcFilterTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcFilterTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcFireSuppressionTerminal_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFireSuppressionTerminal'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcFireSuppressionTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcFireSuppressionTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcFireSuppressionTerminal_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFireSuppressionTerminal'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcfiresuppressionterminaltype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcFireSuppressionTerminalType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFireSuppressionTerminalType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcFireSuppressionTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcFireSuppressionTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcFixedReferenceSweptAreaSolid_DirectrixBounded:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFixedReferenceSweptAreaSolid'
    RULE_NAME = 'DirectrixBounded'

    @staticmethod
    def __call__(self):
        directrix = getattr(self, 'Directrix', INDETERMINATE)
        startparam = getattr(self, 'StartParam', INDETERMINATE)
        endparam = getattr(self, 'EndParam', INDETERMINATE)
        assert (exists(startparam) and exists(endparam) or sizeof(['ifc4x1.ifcconic', 'ifc4x1.ifcboundedcurve'] * typeof(directrix)) == 1) is not False

class IfcFlowInstrument_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFlowInstrument'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcFlowInstrumentTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcFlowInstrumentTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcFlowInstrument_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFlowInstrument'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcflowinstrumenttype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcFlowInstrumentType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFlowInstrumentType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcFlowInstrumentTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcFlowInstrumentTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcFlowMeter_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFlowMeter'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcFlowMeterTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcFlowMeterTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcFlowMeter_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFlowMeter'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcflowmetertype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcFlowMeterType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFlowMeterType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcFlowMeterTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcFlowMeterTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcFooting_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFooting'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcFootingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcFootingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcFooting_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFooting'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcfootingtype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcFootingType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFootingType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcFootingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcFootingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcFurniture_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFurniture'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcFurnitureTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcFurnitureTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcFurniture_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFurniture'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcfurnituretype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcFurnitureType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFurnitureType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcFurnitureTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcFurnitureTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcGeographicElement_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGeographicElement'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcGeographicElementTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcGeographicElementTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcGeographicElement_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGeographicElement'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcgeographicelementtype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcGeographicElementType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGeographicElementType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcGeographicElementTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcGeographicElementTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcGeometricCurveSet_NoSurfaces:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGeometricCurveSet'
    RULE_NAME = 'NoSurfaces'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in getattr(self, 'Elements', INDETERMINATE) if 'ifc4x1.ifcsurface' in typeof(temp)]) == 0) is not False

class IfcGeometricRepresentationContext_North2D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGeometricRepresentationContext'
    RULE_NAME = 'North2D'

    @staticmethod
    def __call__(self):
        truenorth = getattr(self, 'TrueNorth', INDETERMINATE)
        assert (not exists(truenorth) or hiindex(getattr(truenorth, 'DirectionRatios', INDETERMINATE)) == 2) is not False

class IfcGeometricRepresentationSubContext_ParentNoSub:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGeometricRepresentationSubContext'
    RULE_NAME = 'ParentNoSub'

    @staticmethod
    def __call__(self):
        parentcontext = getattr(self, 'ParentContext', INDETERMINATE)
        assert (not 'ifc4x1.ifcgeometricrepresentationsubcontext' in typeof(parentcontext)) is not False

class IfcGeometricRepresentationSubContext_UserTargetProvided:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGeometricRepresentationSubContext'
    RULE_NAME = 'UserTargetProvided'

    @staticmethod
    def __call__(self):
        targetview = getattr(self, 'TargetView', INDETERMINATE)
        userdefinedtargetview = getattr(self, 'UserDefinedTargetView', INDETERMINATE)
        assert (targetview != getattr(IfcGeometricProjectionEnum, 'USERDEFINED', INDETERMINATE) or (targetview == getattr(IfcGeometricProjectionEnum, 'USERDEFINED', INDETERMINATE) and exists(userdefinedtargetview))) is not False

class IfcGeometricRepresentationSubContext_NoCoordOperation:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGeometricRepresentationSubContext'
    RULE_NAME = 'NoCoordOperation'

    @staticmethod
    def __call__(self):
        assert (sizeof(getattr(self, 'HasCoordinateOperation', INDETERMINATE)) == 0) is not False

def calc_IfcGeometricRepresentationSubContext_WorldCoordinateSystem(self):
    parentcontext = getattr(self, 'ParentContext', INDETERMINATE)
    return getattr(parentcontext, 'WorldCoordinateSystem', INDETERMINATE)

def calc_IfcGeometricRepresentationSubContext_CoordinateSpaceDimension(self):
    parentcontext = getattr(self, 'ParentContext', INDETERMINATE)
    return getattr(parentcontext, 'CoordinateSpaceDimension', INDETERMINATE)

def calc_IfcGeometricRepresentationSubContext_TrueNorth(self):
    parentcontext = getattr(self, 'ParentContext', INDETERMINATE)
    return nvl(getattr(parentcontext, 'TrueNorth', INDETERMINATE), IfcConvertDirectionInto2D(express_getitem(getattr(getattr(self, 'WorldCoordinateSystem', INDETERMINATE), 'P', INDETERMINATE), 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)))

def calc_IfcGeometricRepresentationSubContext_Precision(self):
    parentcontext = getattr(self, 'ParentContext', INDETERMINATE)
    return nvl(getattr(parentcontext, 'Precision', INDETERMINATE), 1)

class IfcGeometricSet_ConsistentDim:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGeometricSet'
    RULE_NAME = 'ConsistentDim'

    @staticmethod
    def __call__(self):
        elements = getattr(self, 'Elements', INDETERMINATE)
        assert (sizeof([temp for temp in elements if getattr(temp, 'Dim', INDETERMINATE) != getattr(express_getitem(elements, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)]) == 0) is not False

def calc_IfcGeometricSet_Dim(self):
    elements = getattr(self, 'Elements', INDETERMINATE)
    return getattr(express_getitem(elements, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)

class IfcGridAxis_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGridAxis'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        axiscurve = getattr(self, 'AxisCurve', INDETERMINATE)
        assert (getattr(axiscurve, 'Dim', INDETERMINATE) == 2) is not False

class IfcGridAxis_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGridAxis'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        partofw = getattr(self, 'PartOfW', INDETERMINATE)
        partofv = getattr(self, 'PartOfV', INDETERMINATE)
        partofu = getattr(self, 'PartOfU', INDETERMINATE)
        assert (sizeof(partofu) == 1) ^ (sizeof(partofv) == 1) ^ (sizeof(partofw) == 1) is not False

def calc_IfcHalfSpaceSolid_Dim(self):
    return 3

class IfcHeatExchanger_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcHeatExchanger'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcHeatExchangerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcHeatExchangerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcHeatExchanger_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcHeatExchanger'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcheatexchangertype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcHeatExchangerType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcHeatExchangerType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcHeatExchangerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcHeatExchangerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcHumidifier_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcHumidifier'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcHumidifierTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcHumidifierTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcHumidifier_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcHumidifier'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifchumidifiertype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcHumidifierType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcHumidifierType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcHumidifierTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcHumidifierTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcIShapeProfileDef_ValidFlangeThickness:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcIShapeProfileDef'
    RULE_NAME = 'ValidFlangeThickness'

    @staticmethod
    def __call__(self):
        overalldepth = getattr(self, 'OverallDepth', INDETERMINATE)
        flangethickness = getattr(self, 'FlangeThickness', INDETERMINATE)
        assert (2.0 * flangethickness < overalldepth) is not False

class IfcIShapeProfileDef_ValidWebThickness:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcIShapeProfileDef'
    RULE_NAME = 'ValidWebThickness'

    @staticmethod
    def __call__(self):
        overallwidth = getattr(self, 'OverallWidth', INDETERMINATE)
        webthickness = getattr(self, 'WebThickness', INDETERMINATE)
        assert (webthickness < overallwidth) is not False

class IfcIShapeProfileDef_ValidFilletRadius:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcIShapeProfileDef'
    RULE_NAME = 'ValidFilletRadius'

    @staticmethod
    def __call__(self):
        overallwidth = getattr(self, 'OverallWidth', INDETERMINATE)
        overalldepth = getattr(self, 'OverallDepth', INDETERMINATE)
        webthickness = getattr(self, 'WebThickness', INDETERMINATE)
        flangethickness = getattr(self, 'FlangeThickness', INDETERMINATE)
        filletradius = getattr(self, 'FilletRadius', INDETERMINATE)
        assert (not exists(filletradius) or (filletradius <= (overallwidth - webthickness) / 2.0 and filletradius <= (overalldepth - 2.0 * flangethickness) / 2.0)) is not False

class IfcIndexedPolyCurve_Consecutive:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcIndexedPolyCurve'
    RULE_NAME = 'Consecutive'

    @staticmethod
    def __call__(self):
        segments = getattr(self, 'Segments', INDETERMINATE)
        assert (sizeof(segments) == 0 or IfcConsecutiveSegments(segments)) is not False

class IfcInterceptor_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcInterceptor'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcInterceptorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcInterceptorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcInterceptor_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcInterceptor'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcinterceptortype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcInterceptorType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcInterceptorType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcInterceptorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcInterceptorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcIntersectionCurve_TwoPCurves:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcIntersectionCurve'
    RULE_NAME = 'TwoPCurves'

    @staticmethod
    def __call__(self):
        assert (sizeof(getattr(self, 'AssociatedGeometry', INDETERMINATE)) == 2) is not False

class IfcIntersectionCurve_DistinctSurfaces:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcIntersectionCurve'
    RULE_NAME = 'DistinctSurfaces'

    @staticmethod
    def __call__(self):
        assert (IfcAssociatedSurface(express_getitem(getattr(self, 'AssociatedGeometry', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) != IfcAssociatedSurface(express_getitem(getattr(self, 'AssociatedGeometry', INDETERMINATE), 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))) is not False

class IfcJunctionBox_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcJunctionBox'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcJunctionBoxTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcJunctionBoxTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcJunctionBox_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcJunctionBox'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcjunctionboxtype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcJunctionBoxType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcJunctionBoxType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcJunctionBoxTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcJunctionBoxTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcLShapeProfileDef_ValidThickness:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLShapeProfileDef'
    RULE_NAME = 'ValidThickness'

    @staticmethod
    def __call__(self):
        depth = getattr(self, 'Depth', INDETERMINATE)
        width = getattr(self, 'Width', INDETERMINATE)
        thickness = getattr(self, 'Thickness', INDETERMINATE)
        assert (thickness < depth and (not exists(width) or thickness < width)) is not False

class IfcLaborResource_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLaborResource'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcLaborResourceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcLaborResourceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcLaborResourceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLaborResourceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcLaborResourceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcLaborResourceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ResourceType', INDETERMINATE)))) is not False

class IfcLamp_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLamp'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcLampTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcLampTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcLamp_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLamp'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifclamptype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcLampType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLampType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcLampTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcLampTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcLightFixture_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLightFixture'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcLightFixtureTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcLightFixtureTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcLightFixture_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLightFixture'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifclightfixturetype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcLightFixtureType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLightFixtureType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcLightFixtureTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcLightFixtureTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcLine_SameDim:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLine'
    RULE_NAME = 'SameDim'

    @staticmethod
    def __call__(self):
        pnt = getattr(self, 'Pnt', INDETERMINATE)
        dir = getattr(self, 'Dir', INDETERMINATE)
        assert (getattr(dir, 'Dim', INDETERMINATE) == getattr(pnt, 'Dim', INDETERMINATE)) is not False

class IfcLocalPlacement_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLocalPlacement'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        placementrelto = getattr(self, 'PlacementRelTo', INDETERMINATE)
        relativeplacement = getattr(self, 'RelativePlacement', INDETERMINATE)
        assert IfcCorrectLocalPlacement(relativeplacement, placementrelto) is not False

class IfcMaterialDefinitionRepresentation_OnlyStyledRepresentations:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMaterialDefinitionRepresentation'
    RULE_NAME = 'OnlyStyledRepresentations'

    @staticmethod
    def __call__(self):
        representations = getattr(self, 'Representations', INDETERMINATE)
        assert (sizeof([temp for temp in representations if not 'ifc4x1.ifcstyledrepresentation' in typeof(temp)]) == 0) is not False

class IfcMaterialLayer_NormalizedPriority:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMaterialLayer'
    RULE_NAME = 'NormalizedPriority'

    @staticmethod
    def __call__(self):
        priority = getattr(self, 'Priority', INDETERMINATE)
        assert (not exists(priority) or 0 <= priority <= 100) is not False

def calc_IfcMaterialLayerSet_TotalThickness(self):
    return IfcMlsTotalThickness(self)

class IfcMaterialProfile_NormalizedPriority:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMaterialProfile'
    RULE_NAME = 'NormalizedPriority'

    @staticmethod
    def __call__(self):
        priority = getattr(self, 'Priority', INDETERMINATE)
        assert (not exists(priority) or 0 <= priority <= 100) is not False

class IfcMechanicalFastener_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMechanicalFastener'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcMechanicalFastenerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcMechanicalFastenerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcMechanicalFastener_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMechanicalFastener'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcmechanicalfastenertype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcMechanicalFastenerType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMechanicalFastenerType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcMechanicalFastenerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcMechanicalFastenerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcMedicalDevice_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMedicalDevice'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcMedicalDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcMedicalDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcMedicalDevice_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMedicalDevice'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcmedicaldevicetype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcMedicalDeviceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMedicalDeviceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcMedicalDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcMedicalDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcMember_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMember'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcMemberTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcMemberTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcMember_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMember'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcmembertype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcMemberStandardCase_HasMaterialProfileSetUsage:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMemberStandardCase'
    RULE_NAME = 'HasMaterialProfileSetUsage'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in usedin(self, 'ifc4x1.ifcrelassociates.relatedobjects') if 'ifc4x1.ifcrelassociatesmaterial' in typeof(temp) and 'ifc4x1.ifcmaterialprofilesetusage' in typeof(getattr(temp, 'RelatingMaterial', INDETERMINATE))]) == 1) is not False

class IfcMemberType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMemberType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcMemberTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcMemberTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

def calc_IfcMirroredProfileDef_Operator(self):
    return IfcCartesianTransformationOperator2D(Axis1=IfcDirection(DirectionRatios=[-1.0, 0.0]), Axis2=IfcDirection(DirectionRatios=[0.0, 1.0]), LocalOrigin=IfcCartesianPoint(Coordinates=[0.0, 0.0]), Scale=1.0)

class IfcMotorConnection_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMotorConnection'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcMotorConnectionTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcMotorConnectionTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcMotorConnection_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMotorConnection'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcmotorconnectiontype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcMotorConnectionType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMotorConnectionType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcMotorConnectionTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcMotorConnectionTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcNamedUnit_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcNamedUnit'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert IfcCorrectDimensions(getattr(self, 'UnitType', INDETERMINATE), getattr(self, 'Dimensions', INDETERMINATE)) is not False

class IfcObject_UniquePropertySetNames:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcObject'
    RULE_NAME = 'UniquePropertySetNames'

    @staticmethod
    def __call__(self):
        isdefinedby = getattr(self, 'IsDefinedBy', INDETERMINATE)
        assert (sizeof(isdefinedby) == 0 or IfcUniqueDefinitionNames(isdefinedby)) is not False

class IfcObjective_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcObjective'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        objectivequalifier = getattr(self, 'ObjectiveQualifier', INDETERMINATE)
        assert (objectivequalifier != getattr(IfcObjectiveEnum, 'USERDEFINED', INDETERMINATE) or (objectivequalifier == getattr(IfcObjectiveEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'UserDefinedQualifier', INDETERMINATE)))) is not False

class IfcOccupant_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcOccupant'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not predefinedtype == getattr(IfcOccupantTypeEnum, 'USERDEFINED', INDETERMINATE) or exists(getattr(self, 'ObjectType', INDETERMINATE))) is not False

class IfcOffsetCurve2D_DimIs2D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcOffsetCurve2D'
    RULE_NAME = 'DimIs2D'

    @staticmethod
    def __call__(self):
        basiscurve = getattr(self, 'BasisCurve', INDETERMINATE)
        assert (getattr(basiscurve, 'Dim', INDETERMINATE) == 2) is not False

class IfcOffsetCurve3D_DimIs2D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcOffsetCurve3D'
    RULE_NAME = 'DimIs2D'

    @staticmethod
    def __call__(self):
        basiscurve = getattr(self, 'BasisCurve', INDETERMINATE)
        assert (getattr(basiscurve, 'Dim', INDETERMINATE) == 3) is not False

class IfcOrientedEdge_EdgeElementNotOriented:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcOrientedEdge'
    RULE_NAME = 'EdgeElementNotOriented'

    @staticmethod
    def __call__(self):
        edgeelement = getattr(self, 'EdgeElement', INDETERMINATE)
        assert (not 'ifc4x1.ifcorientededge' in typeof(edgeelement)) is not False

def calc_IfcOrientedEdge_EdgeStart(self):
    edgeelement = getattr(self, 'EdgeElement', INDETERMINATE)
    orientation = getattr(self, 'Orientation', INDETERMINATE)
    return IfcBooleanChoose(orientation, getattr(edgeelement, 'EdgeStart', INDETERMINATE), getattr(edgeelement, 'EdgeEnd', INDETERMINATE))

def calc_IfcOrientedEdge_EdgeEnd(self):
    edgeelement = getattr(self, 'EdgeElement', INDETERMINATE)
    orientation = getattr(self, 'Orientation', INDETERMINATE)
    return IfcBooleanChoose(orientation, getattr(edgeelement, 'EdgeEnd', INDETERMINATE), getattr(edgeelement, 'EdgeStart', INDETERMINATE))

class IfcOutlet_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcOutlet'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcOutletTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcOutletTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcOutlet_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcOutlet'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcoutlettype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcOutletType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcOutletType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcOutletTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcOutletTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcOwnerHistory_CorrectChangeAction:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcOwnerHistory'
    RULE_NAME = 'CorrectChangeAction'

    @staticmethod
    def __call__(self):
        changeaction = getattr(self, 'ChangeAction', INDETERMINATE)
        lastmodifieddate = getattr(self, 'LastModifiedDate', INDETERMINATE)
        assert (exists(lastmodifieddate) or (not exists(lastmodifieddate) and (not exists(changeaction))) or (not exists(lastmodifieddate) and exists(changeaction) and (changeaction == getattr(IfcChangeActionEnum, 'NOTDEFINED', INDETERMINATE) or changeaction == getattr(IfcChangeActionEnum, 'NOCHANGE', INDETERMINATE)))) is not False

class IfcPath_IsContinuous:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPath'
    RULE_NAME = 'IsContinuous'

    @staticmethod
    def __call__(self):
        assert IfcPathHeadToTail(self) is not False

class IfcPcurve_DimIs2D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPcurve'
    RULE_NAME = 'DimIs2D'

    @staticmethod
    def __call__(self):
        referencecurve = getattr(self, 'ReferenceCurve', INDETERMINATE)
        assert (getattr(referencecurve, 'Dim', INDETERMINATE) == 2) is not False

class IfcPerson_IdentifiablePerson:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPerson'
    RULE_NAME = 'IdentifiablePerson'

    @staticmethod
    def __call__(self):
        identification = getattr(self, 'Identification', INDETERMINATE)
        familyname = getattr(self, 'FamilyName', INDETERMINATE)
        givenname = getattr(self, 'GivenName', INDETERMINATE)
        assert (exists(identification) or exists(familyname) or exists(givenname)) is not False

class IfcPerson_ValidSetOfNames:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPerson'
    RULE_NAME = 'ValidSetOfNames'

    @staticmethod
    def __call__(self):
        familyname = getattr(self, 'FamilyName', INDETERMINATE)
        givenname = getattr(self, 'GivenName', INDETERMINATE)
        middlenames = getattr(self, 'MiddleNames', INDETERMINATE)
        assert (not exists(middlenames) or exists(familyname) or exists(givenname)) is not False

class IfcPhysicalComplexQuantity_NoSelfReference:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPhysicalComplexQuantity'
    RULE_NAME = 'NoSelfReference'

    @staticmethod
    def __call__(self):
        hasquantities = getattr(self, 'HasQuantities', INDETERMINATE)
        assert (sizeof([temp for temp in hasquantities if self == temp]) == 0) is not False

class IfcPhysicalComplexQuantity_UniqueQuantityNames:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPhysicalComplexQuantity'
    RULE_NAME = 'UniqueQuantityNames'

    @staticmethod
    def __call__(self):
        hasquantities = getattr(self, 'HasQuantities', INDETERMINATE)
        assert IfcUniqueQuantityNames(hasquantities) is not False

class IfcPile_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPile'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcPileTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcPileTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcPile_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPile'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcpiletype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcPileType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPileType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcPileTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcPileTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcPipeFitting_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPipeFitting'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcPipeFittingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcPipeFittingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcPipeFitting_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPipeFitting'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcpipefittingtype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcPipeFittingType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPipeFittingType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcPipeFittingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcPipeFittingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcPipeSegment_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPipeSegment'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcPipeSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcPipeSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcPipeSegment_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPipeSegment'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcpipesegmenttype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcPipeSegmentType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPipeSegmentType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcPipeSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcPipeSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcPixelTexture_MinPixelInS:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPixelTexture'
    RULE_NAME = 'MinPixelInS'

    @staticmethod
    def __call__(self):
        width = getattr(self, 'Width', INDETERMINATE)
        assert (width >= 1) is not False

class IfcPixelTexture_MinPixelInT:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPixelTexture'
    RULE_NAME = 'MinPixelInT'

    @staticmethod
    def __call__(self):
        height = getattr(self, 'Height', INDETERMINATE)
        assert (height >= 1) is not False

class IfcPixelTexture_NumberOfColours:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPixelTexture'
    RULE_NAME = 'NumberOfColours'

    @staticmethod
    def __call__(self):
        colourcomponents = getattr(self, 'ColourComponents', INDETERMINATE)
        assert (1 <= colourcomponents <= 4) is not False

class IfcPixelTexture_SizeOfPixelList:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPixelTexture'
    RULE_NAME = 'SizeOfPixelList'

    @staticmethod
    def __call__(self):
        width = getattr(self, 'Width', INDETERMINATE)
        height = getattr(self, 'Height', INDETERMINATE)
        pixel = getattr(self, 'Pixel', INDETERMINATE)
        assert (sizeof(pixel) == width * height) is not False

class IfcPixelTexture_PixelAsByteAndSameLength:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPixelTexture'
    RULE_NAME = 'PixelAsByteAndSameLength'

    @staticmethod
    def __call__(self):
        pixel = getattr(self, 'Pixel', INDETERMINATE)
        assert (sizeof([temp for temp in pixel if blength(temp) % 8 == 0 and blength(temp) == blength(express_getitem(pixel, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))]) == sizeof(pixel)) is not False

def calc_IfcPlacement_Dim(self):
    location = getattr(self, 'Location', INDETERMINATE)
    return getattr(location, 'Dim', INDETERMINATE)

class IfcPlate_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPlate'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcPlateTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcPlateTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcPlate_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPlate'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcplatetype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcPlateStandardCase_HasMaterialLayerSetUsage:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPlateStandardCase'
    RULE_NAME = 'HasMaterialLayerSetUsage'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in usedin(self, 'ifc4x1.ifcrelassociates.relatedobjects') if 'ifc4x1.ifcrelassociatesmaterial' in typeof(temp) and 'ifc4x1.ifcmateriallayersetusage' in typeof(getattr(temp, 'RelatingMaterial', INDETERMINATE))]) == 1) is not False

class IfcPlateType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPlateType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcPlateTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcPlateTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

def calc_IfcPointOnCurve_Dim(self):
    basiscurve = getattr(self, 'BasisCurve', INDETERMINATE)
    return getattr(basiscurve, 'Dim', INDETERMINATE)

def calc_IfcPointOnSurface_Dim(self):
    basissurface = getattr(self, 'BasisSurface', INDETERMINATE)
    return getattr(basissurface, 'Dim', INDETERMINATE)

class IfcPolyLoop_AllPointsSameDim:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPolyLoop'
    RULE_NAME = 'AllPointsSameDim'

    @staticmethod
    def __call__(self):
        polygon = getattr(self, 'Polygon', INDETERMINATE)
        assert (sizeof([temp for temp in polygon if getattr(temp, 'Dim', INDETERMINATE) != getattr(express_getitem(polygon, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)]) == 0) is not False

class IfcPolygonalBoundedHalfSpace_BoundaryDim:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPolygonalBoundedHalfSpace'
    RULE_NAME = 'BoundaryDim'

    @staticmethod
    def __call__(self):
        polygonalboundary = getattr(self, 'PolygonalBoundary', INDETERMINATE)
        assert (getattr(polygonalboundary, 'Dim', INDETERMINATE) == 2) is not False

class IfcPolygonalBoundedHalfSpace_BoundaryType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPolygonalBoundedHalfSpace'
    RULE_NAME = 'BoundaryType'

    @staticmethod
    def __call__(self):
        polygonalboundary = getattr(self, 'PolygonalBoundary', INDETERMINATE)
        assert (sizeof(typeof(polygonalboundary) * ['ifc4x1.ifcpolyline', 'ifc4x1.ifccompositecurve']) == 1) is not False

class IfcPolyline_SameDim:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPolyline'
    RULE_NAME = 'SameDim'

    @staticmethod
    def __call__(self):
        points = getattr(self, 'Points', INDETERMINATE)
        assert (sizeof([temp for temp in points if getattr(temp, 'Dim', INDETERMINATE) != getattr(express_getitem(points, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)]) == 0) is not False

class IfcPositioningElement_HasPlacement:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPositioningElement'
    RULE_NAME = 'HasPlacement'

    @staticmethod
    def __call__(self):
        assert exists(getattr(self, 'ObjectPlacement', INDETERMINATE)) is not False

class IfcPostalAddress_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPostalAddress'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        internallocation = getattr(self, 'InternalLocation', INDETERMINATE)
        addresslines = getattr(self, 'AddressLines', INDETERMINATE)
        postalbox = getattr(self, 'PostalBox', INDETERMINATE)
        town = getattr(self, 'Town', INDETERMINATE)
        region = getattr(self, 'Region', INDETERMINATE)
        postalcode = getattr(self, 'PostalCode', INDETERMINATE)
        country = getattr(self, 'Country', INDETERMINATE)
        assert (exists(internallocation) or exists(addresslines) or exists(postalbox) or exists(postalcode) or exists(town) or exists(region) or exists(country)) is not False

class IfcPresentationLayerAssignment_ApplicableItems:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPresentationLayerAssignment'
    RULE_NAME = 'ApplicableItems'

    @staticmethod
    def __call__(self):
        assigneditems = getattr(self, 'AssignedItems', INDETERMINATE)
        assert (sizeof([temp for temp in assigneditems if sizeof(typeof(temp) * ['ifc4x1.ifcshaperepresentation', 'ifc4x1.ifcgeometricrepresentationitem', 'ifc4x1.ifcmappeditem']) == 1]) == sizeof(assigneditems)) is not False

class IfcPresentationLayerWithStyle_ApplicableOnlyToItems:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPresentationLayerWithStyle'
    RULE_NAME = 'ApplicableOnlyToItems'

    @staticmethod
    def __call__(self):
        assigneditems = getattr(self, 'AssignedItems', INDETERMINATE)
        assert (sizeof([temp for temp in assigneditems if sizeof(typeof(temp) * ['ifc4x1.ifcgeometricrepresentationitem', 'ifc4x1.ifcmappeditem']) >= 1]) == sizeof(assigneditems)) is not False

class IfcProcedure_HasName:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProcedure'
    RULE_NAME = 'HasName'

    @staticmethod
    def __call__(self):
        assert exists(getattr(self, 'Name', INDETERMINATE)) is not False

class IfcProcedure_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProcedure'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcProcedureTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcProcedureTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcProcedureType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProcedureType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcProcedureTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcProcedureTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ProcessType', INDETERMINATE)))) is not False

class IfcProduct_PlacementForShapeRepresentation:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProduct'
    RULE_NAME = 'PlacementForShapeRepresentation'

    @staticmethod
    def __call__(self):
        objectplacement = getattr(self, 'ObjectPlacement', INDETERMINATE)
        representation = getattr(self, 'Representation', INDETERMINATE)
        assert (exists(representation) and exists(objectplacement) or (exists(representation) and sizeof([temp for temp in getattr(representation, 'Representations', INDETERMINATE) if 'ifc4x1.ifcshaperepresentation' in typeof(temp)]) == 0) or (not exists(representation))) is not False

class IfcProductDefinitionShape_OnlyShapeModel:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProductDefinitionShape'
    RULE_NAME = 'OnlyShapeModel'

    @staticmethod
    def __call__(self):
        representations = getattr(self, 'Representations', INDETERMINATE)
        assert (sizeof([temp for temp in representations if not 'ifc4x1.ifcshapemodel' in typeof(temp)]) == 0) is not False

class IfcProject_HasName:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProject'
    RULE_NAME = 'HasName'

    @staticmethod
    def __call__(self):
        assert exists(getattr(self, 'Name', INDETERMINATE)) is not False

class IfcProject_CorrectContext:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProject'
    RULE_NAME = 'CorrectContext'

    @staticmethod
    def __call__(self):
        assert (not exists(getattr(self, 'RepresentationContexts', INDETERMINATE)) or sizeof([temp for temp in getattr(self, 'RepresentationContexts', INDETERMINATE) if 'ifc4x1.ifcgeometricrepresentationsubcontext' in typeof(temp)]) == 0) is not False

class IfcProject_NoDecomposition:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProject'
    RULE_NAME = 'NoDecomposition'

    @staticmethod
    def __call__(self):
        assert (sizeof(getattr(self, 'Decomposes', INDETERMINATE)) == 0) is not False

class IfcProjectedCRS_IsLengthUnit:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProjectedCRS'
    RULE_NAME = 'IsLengthUnit'

    @staticmethod
    def __call__(self):
        mapunit = getattr(self, 'MapUnit', INDETERMINATE)
        assert (not exists(mapunit) or getattr(mapunit, 'UnitType', INDETERMINATE) == getattr(IfcUnitEnum, 'LENGTHUNIT', INDETERMINATE)) is not False

class IfcPropertyBoundedValue_SameUnitUpperLower:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyBoundedValue'
    RULE_NAME = 'SameUnitUpperLower'

    @staticmethod
    def __call__(self):
        upperboundvalue = getattr(self, 'UpperBoundValue', INDETERMINATE)
        lowerboundvalue = getattr(self, 'LowerBoundValue', INDETERMINATE)
        assert (not exists(upperboundvalue) or not exists(lowerboundvalue) or typeof(upperboundvalue) == typeof(lowerboundvalue)) is not False

class IfcPropertyBoundedValue_SameUnitUpperSet:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyBoundedValue'
    RULE_NAME = 'SameUnitUpperSet'

    @staticmethod
    def __call__(self):
        upperboundvalue = getattr(self, 'UpperBoundValue', INDETERMINATE)
        setpointvalue = getattr(self, 'SetPointValue', INDETERMINATE)
        assert (not exists(upperboundvalue) or not exists(setpointvalue) or typeof(upperboundvalue) == typeof(setpointvalue)) is not False

class IfcPropertyBoundedValue_SameUnitLowerSet:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyBoundedValue'
    RULE_NAME = 'SameUnitLowerSet'

    @staticmethod
    def __call__(self):
        lowerboundvalue = getattr(self, 'LowerBoundValue', INDETERMINATE)
        setpointvalue = getattr(self, 'SetPointValue', INDETERMINATE)
        assert (not exists(lowerboundvalue) or not exists(setpointvalue) or typeof(lowerboundvalue) == typeof(setpointvalue)) is not False

class IfcPropertyDependencyRelationship_NoSelfReference:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyDependencyRelationship'
    RULE_NAME = 'NoSelfReference'

    @staticmethod
    def __call__(self):
        dependingproperty = getattr(self, 'DependingProperty', INDETERMINATE)
        dependantproperty = getattr(self, 'DependantProperty', INDETERMINATE)
        assert (dependingproperty != dependantproperty) is not False

class IfcPropertyEnumeratedValue_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyEnumeratedValue'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        enumerationvalues = getattr(self, 'EnumerationValues', INDETERMINATE)
        enumerationreference = getattr(self, 'EnumerationReference', INDETERMINATE)
        assert (not exists(enumerationreference) or not exists(enumerationvalues) or sizeof([temp for temp in enumerationvalues if temp in getattr(enumerationreference, 'EnumerationValues', INDETERMINATE)]) == sizeof(enumerationvalues)) is not False

class IfcPropertyEnumeration_WR01:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyEnumeration'
    RULE_NAME = 'WR01'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in getattr(self, 'EnumerationValues', INDETERMINATE) if not typeof(express_getitem(getattr(self, 'EnumerationValues', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) == typeof(temp)]) == 0) is not False

class IfcPropertyListValue_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyListValue'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in getattr(self, 'ListValues', INDETERMINATE) if not typeof(express_getitem(getattr(self, 'ListValues', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) == typeof(temp)]) == 0) is not False

class IfcPropertySet_ExistsName:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertySet'
    RULE_NAME = 'ExistsName'

    @staticmethod
    def __call__(self):
        assert exists(getattr(self, 'Name', INDETERMINATE)) is not False

class IfcPropertySet_UniquePropertyNames:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertySet'
    RULE_NAME = 'UniquePropertyNames'

    @staticmethod
    def __call__(self):
        hasproperties = getattr(self, 'HasProperties', INDETERMINATE)
        assert IfcUniquePropertyName(hasproperties) is not False

class IfcPropertySetTemplate_ExistsName:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertySetTemplate'
    RULE_NAME = 'ExistsName'

    @staticmethod
    def __call__(self):
        assert exists(getattr(self, 'Name', INDETERMINATE)) is not False

class IfcPropertySetTemplate_UniquePropertyNames:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertySetTemplate'
    RULE_NAME = 'UniquePropertyNames'

    @staticmethod
    def __call__(self):
        haspropertytemplates = getattr(self, 'HasPropertyTemplates', INDETERMINATE)
        assert IfcUniquePropertyTemplateNames(haspropertytemplates) is not False

class IfcPropertyTableValue_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyTableValue'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        definingvalues = getattr(self, 'DefiningValues', INDETERMINATE)
        definedvalues = getattr(self, 'DefinedValues', INDETERMINATE)
        assert (not exists(definingvalues) and (not exists(definedvalues)) or sizeof(definingvalues) == sizeof(definedvalues)) is not False

class IfcPropertyTableValue_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyTableValue'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        definingvalues = getattr(self, 'DefiningValues', INDETERMINATE)
        assert (not exists(definingvalues) or sizeof([temp for temp in getattr(self, 'DefiningValues', INDETERMINATE) if typeof(temp) != typeof(express_getitem(getattr(self, 'DefiningValues', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))]) == 0) is not False

class IfcPropertyTableValue_WR23:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyTableValue'
    RULE_NAME = 'WR23'

    @staticmethod
    def __call__(self):
        definedvalues = getattr(self, 'DefinedValues', INDETERMINATE)
        assert (not exists(definedvalues) or sizeof([temp for temp in getattr(self, 'DefinedValues', INDETERMINATE) if typeof(temp) != typeof(express_getitem(getattr(self, 'DefinedValues', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))]) == 0) is not False

class IfcProtectiveDevice_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProtectiveDevice'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcProtectiveDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcProtectiveDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcProtectiveDevice_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProtectiveDevice'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcprotectivedevicetype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcProtectiveDeviceTrippingUnit_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProtectiveDeviceTrippingUnit'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcProtectiveDeviceTrippingUnitTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcProtectiveDeviceTrippingUnitTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcProtectiveDeviceTrippingUnit_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProtectiveDeviceTrippingUnit'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcprotectivedevicetrippingunittype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcProtectiveDeviceTrippingUnitType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProtectiveDeviceTrippingUnitType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcProtectiveDeviceTrippingUnitTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcProtectiveDeviceTrippingUnitTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcProtectiveDeviceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProtectiveDeviceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcProtectiveDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcProtectiveDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcProxy_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProxy'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert exists(getattr(self, 'Name', INDETERMINATE)) is not False

class IfcPump_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPump'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcPumpTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcPumpTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcPump_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPump'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcpumptype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcPumpType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPumpType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcPumpTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcPumpTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcQuantityArea_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcQuantityArea'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        assert (not exists(getattr(self, 'Unit', INDETERMINATE)) or getattr(getattr(self, 'Unit', INDETERMINATE), 'UnitType', INDETERMINATE) == getattr(IfcUnitEnum, 'AREAUNIT', INDETERMINATE)) is not False

class IfcQuantityArea_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcQuantityArea'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        areavalue = getattr(self, 'AreaValue', INDETERMINATE)
        assert (areavalue >= 0.0) is not False

class IfcQuantityCount_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcQuantityCount'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        countvalue = getattr(self, 'CountValue', INDETERMINATE)
        assert (countvalue >= 0.0) is not False

class IfcQuantityLength_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcQuantityLength'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        assert (not exists(getattr(self, 'Unit', INDETERMINATE)) or getattr(getattr(self, 'Unit', INDETERMINATE), 'UnitType', INDETERMINATE) == getattr(IfcUnitEnum, 'LENGTHUNIT', INDETERMINATE)) is not False

class IfcQuantityLength_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcQuantityLength'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        lengthvalue = getattr(self, 'LengthValue', INDETERMINATE)
        assert (lengthvalue >= 0.0) is not False

class IfcQuantityTime_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcQuantityTime'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        assert (not exists(getattr(self, 'Unit', INDETERMINATE)) or getattr(getattr(self, 'Unit', INDETERMINATE), 'UnitType', INDETERMINATE) == getattr(IfcUnitEnum, 'TIMEUNIT', INDETERMINATE)) is not False

class IfcQuantityTime_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcQuantityTime'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        timevalue = getattr(self, 'TimeValue', INDETERMINATE)
        assert (timevalue >= 0.0) is not False

class IfcQuantityVolume_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcQuantityVolume'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        assert (not exists(getattr(self, 'Unit', INDETERMINATE)) or getattr(getattr(self, 'Unit', INDETERMINATE), 'UnitType', INDETERMINATE) == getattr(IfcUnitEnum, 'VOLUMEUNIT', INDETERMINATE)) is not False

class IfcQuantityVolume_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcQuantityVolume'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        volumevalue = getattr(self, 'VolumeValue', INDETERMINATE)
        assert (volumevalue >= 0.0) is not False

class IfcQuantityWeight_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcQuantityWeight'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        assert (not exists(getattr(self, 'Unit', INDETERMINATE)) or getattr(getattr(self, 'Unit', INDETERMINATE), 'UnitType', INDETERMINATE) == getattr(IfcUnitEnum, 'MASSUNIT', INDETERMINATE)) is not False

class IfcQuantityWeight_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcQuantityWeight'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        weightvalue = getattr(self, 'WeightValue', INDETERMINATE)
        assert (weightvalue >= 0.0) is not False

class IfcRailing_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRailing'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcRailingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcRailingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcRailing_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRailing'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcrailingtype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcRailingType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRailingType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcRailingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcRailingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcRamp_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRamp'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcRampTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcRampTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcRamp_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRamp'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcramptype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcRampFlight_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRampFlight'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcRampFlightTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcRampFlightTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcRampFlight_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRampFlight'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcrampflighttype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcRampFlightType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRampFlightType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcRampFlightTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcRampFlightTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcRampType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRampType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcRampTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcRampTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcRationalBSplineCurveWithKnots_SameNumOfWeightsAndPoints:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRationalBSplineCurveWithKnots'
    RULE_NAME = 'SameNumOfWeightsAndPoints'

    @staticmethod
    def __call__(self):
        weightsdata = getattr(self, 'WeightsData', INDETERMINATE)
        assert (sizeof(weightsdata) == sizeof(getattr(self, 'ControlPointsList', INDETERMINATE))) is not False

class IfcRationalBSplineCurveWithKnots_WeightsGreaterZero:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRationalBSplineCurveWithKnots'
    RULE_NAME = 'WeightsGreaterZero'

    @staticmethod
    def __call__(self):
        assert IfcCurveWeightsPositive(self) is not False

def calc_IfcRationalBSplineCurveWithKnots_Weights(self):
    weightsdata = getattr(self, 'WeightsData', INDETERMINATE)
    return IfcListToArray(weightsdata, 0, getattr(self, 'UpperIndexOnControlPoints', INDETERMINATE))

class IfcRationalBSplineSurfaceWithKnots_CorrespondingWeightsDataLists:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRationalBSplineSurfaceWithKnots'
    RULE_NAME = 'CorrespondingWeightsDataLists'

    @staticmethod
    def __call__(self):
        weightsdata = getattr(self, 'WeightsData', INDETERMINATE)
        assert (sizeof(weightsdata) == sizeof(getattr(self, 'ControlPointsList', INDETERMINATE)) and sizeof(express_getitem(weightsdata, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) == sizeof(express_getitem(getattr(self, 'ControlPointsList', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))) is not False

class IfcRationalBSplineSurfaceWithKnots_WeightValuesGreaterZero:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRationalBSplineSurfaceWithKnots'
    RULE_NAME = 'WeightValuesGreaterZero'

    @staticmethod
    def __call__(self):
        assert IfcSurfaceWeightsPositive(self) is not False

def calc_IfcRationalBSplineSurfaceWithKnots_Weights(self):
    uupper = getattr(self, 'UUpper', INDETERMINATE)
    vupper = getattr(self, 'VUpper', INDETERMINATE)
    weightsdata = getattr(self, 'WeightsData', INDETERMINATE)
    return IfcMakeArrayOfArray(weightsdata, 0, uupper, 0, vupper)

class IfcRectangleHollowProfileDef_ValidWallThickness:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRectangleHollowProfileDef'
    RULE_NAME = 'ValidWallThickness'

    @staticmethod
    def __call__(self):
        wallthickness = getattr(self, 'WallThickness', INDETERMINATE)
        assert (wallthickness < getattr(self, 'XDim', INDETERMINATE) / 2.0 and wallthickness < getattr(self, 'YDim', INDETERMINATE) / 2.0) is not False

class IfcRectangleHollowProfileDef_ValidInnerRadius:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRectangleHollowProfileDef'
    RULE_NAME = 'ValidInnerRadius'

    @staticmethod
    def __call__(self):
        wallthickness = getattr(self, 'WallThickness', INDETERMINATE)
        innerfilletradius = getattr(self, 'InnerFilletRadius', INDETERMINATE)
        assert (not exists(innerfilletradius) or (innerfilletradius <= getattr(self, 'XDim', INDETERMINATE) / 2.0 - wallthickness and innerfilletradius <= getattr(self, 'YDim', INDETERMINATE) / 2.0 - wallthickness)) is not False

class IfcRectangleHollowProfileDef_ValidOuterRadius:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRectangleHollowProfileDef'
    RULE_NAME = 'ValidOuterRadius'

    @staticmethod
    def __call__(self):
        outerfilletradius = getattr(self, 'OuterFilletRadius', INDETERMINATE)
        assert (not exists(outerfilletradius) or (outerfilletradius <= getattr(self, 'XDim', INDETERMINATE) / 2.0 and outerfilletradius <= getattr(self, 'YDim', INDETERMINATE) / 2.0)) is not False

class IfcRectangularTrimmedSurface_U1AndU2Different:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRectangularTrimmedSurface'
    RULE_NAME = 'U1AndU2Different'

    @staticmethod
    def __call__(self):
        u1 = getattr(self, 'U1', INDETERMINATE)
        u2 = getattr(self, 'U2', INDETERMINATE)
        assert (u1 != u2) is not False

class IfcRectangularTrimmedSurface_V1AndV2Different:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRectangularTrimmedSurface'
    RULE_NAME = 'V1AndV2Different'

    @staticmethod
    def __call__(self):
        v1 = getattr(self, 'V1', INDETERMINATE)
        v2 = getattr(self, 'V2', INDETERMINATE)
        assert (v1 != v2) is not False

class IfcRectangularTrimmedSurface_UsenseCompatible:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRectangularTrimmedSurface'
    RULE_NAME = 'UsenseCompatible'

    @staticmethod
    def __call__(self):
        basissurface = getattr(self, 'BasisSurface', INDETERMINATE)
        u1 = getattr(self, 'U1', INDETERMINATE)
        u2 = getattr(self, 'U2', INDETERMINATE)
        usense = getattr(self, 'Usense', INDETERMINATE)
        assert ('ifc4x1.ifcelementarysurface' in typeof(basissurface) and (not 'ifc4x1.ifcplane' in typeof(basissurface)) or 'ifc4x1.ifcsurfaceofrevolution' in typeof(basissurface) or usense == (u2 > u1)) is not False

class IfcRectangularTrimmedSurface_VsenseCompatible:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRectangularTrimmedSurface'
    RULE_NAME = 'VsenseCompatible'

    @staticmethod
    def __call__(self):
        v1 = getattr(self, 'V1', INDETERMINATE)
        v2 = getattr(self, 'V2', INDETERMINATE)
        vsense = getattr(self, 'Vsense', INDETERMINATE)
        assert (vsense == (v2 > v1)) is not False

class IfcReinforcingBar_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcReinforcingBar'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcReinforcingBarTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcReinforcingBarTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcReinforcingBar_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcReinforcingBar'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcreinforcingbartype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcReinforcingBarType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcReinforcingBarType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcReinforcingBarTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcReinforcingBarTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcReinforcingBarType_BendingShapeCodeProvided:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcReinforcingBarType'
    RULE_NAME = 'BendingShapeCodeProvided'

    @staticmethod
    def __call__(self):
        bendingshapecode = getattr(self, 'BendingShapeCode', INDETERMINATE)
        bendingparameters = getattr(self, 'BendingParameters', INDETERMINATE)
        assert (not exists(bendingparameters) or exists(bendingshapecode)) is not False

class IfcReinforcingMesh_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcReinforcingMesh'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcReinforcingMeshTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcReinforcingMeshTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcReinforcingMesh_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcReinforcingMesh'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcreinforcingmeshtype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcReinforcingMeshType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcReinforcingMeshType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcReinforcingMeshTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcReinforcingMeshTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcReinforcingMeshType_BendingShapeCodeProvided:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcReinforcingMeshType'
    RULE_NAME = 'BendingShapeCodeProvided'

    @staticmethod
    def __call__(self):
        bendingshapecode = getattr(self, 'BendingShapeCode', INDETERMINATE)
        bendingparameters = getattr(self, 'BendingParameters', INDETERMINATE)
        assert (not exists(bendingparameters) or exists(bendingshapecode)) is not False

class IfcRelAggregates_NoSelfReference:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAggregates'
    RULE_NAME = 'NoSelfReference'

    @staticmethod
    def __call__(self):
        relatingobject = getattr(self, 'RelatingObject', INDETERMINATE)
        relatedobjects = getattr(self, 'RelatedObjects', INDETERMINATE)
        assert (sizeof([temp for temp in relatedobjects if relatingobject == temp]) == 0) is not False

class IfcRelAssigns_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssigns'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        relatedobjects = getattr(self, 'RelatedObjects', INDETERMINATE)
        relatedobjectstype = getattr(self, 'RelatedObjectsType', INDETERMINATE)
        assert IfcCorrectObjectAssignment(relatedobjectstype, relatedobjects) is not False

class IfcRelAssignsToActor_NoSelfReference:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssignsToActor'
    RULE_NAME = 'NoSelfReference'

    @staticmethod
    def __call__(self):
        relatingactor = getattr(self, 'RelatingActor', INDETERMINATE)
        assert (sizeof([temp for temp in getattr(self, 'RelatedObjects', INDETERMINATE) if relatingactor == temp]) == 0) is not False

class IfcRelAssignsToControl_NoSelfReference:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssignsToControl'
    RULE_NAME = 'NoSelfReference'

    @staticmethod
    def __call__(self):
        relatingcontrol = getattr(self, 'RelatingControl', INDETERMINATE)
        assert (sizeof([temp for temp in getattr(self, 'RelatedObjects', INDETERMINATE) if relatingcontrol == temp]) == 0) is not False

class IfcRelAssignsToGroup_NoSelfReference:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssignsToGroup'
    RULE_NAME = 'NoSelfReference'

    @staticmethod
    def __call__(self):
        relatinggroup = getattr(self, 'RelatingGroup', INDETERMINATE)
        assert (sizeof([temp for temp in getattr(self, 'RelatedObjects', INDETERMINATE) if relatinggroup == temp]) == 0) is not False

class IfcRelAssignsToProcess_NoSelfReference:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssignsToProcess'
    RULE_NAME = 'NoSelfReference'

    @staticmethod
    def __call__(self):
        relatingprocess = getattr(self, 'RelatingProcess', INDETERMINATE)
        assert (sizeof([temp for temp in getattr(self, 'RelatedObjects', INDETERMINATE) if relatingprocess == temp]) == 0) is not False

class IfcRelAssignsToProduct_NoSelfReference:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssignsToProduct'
    RULE_NAME = 'NoSelfReference'

    @staticmethod
    def __call__(self):
        relatingproduct = getattr(self, 'RelatingProduct', INDETERMINATE)
        assert (sizeof([temp for temp in getattr(self, 'RelatedObjects', INDETERMINATE) if relatingproduct == temp]) == 0) is not False

class IfcRelAssignsToResource_NoSelfReference:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssignsToResource'
    RULE_NAME = 'NoSelfReference'

    @staticmethod
    def __call__(self):
        relatingresource = getattr(self, 'RelatingResource', INDETERMINATE)
        assert (sizeof([temp for temp in getattr(self, 'RelatedObjects', INDETERMINATE) if relatingresource == temp]) == 0) is not False

class IfcRelAssociatesMaterial_NoVoidElement:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssociatesMaterial'
    RULE_NAME = 'NoVoidElement'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in getattr(self, 'RelatedObjects', INDETERMINATE) if 'ifc4x1.ifcfeatureelementsubtraction' in typeof(temp) or 'ifc4x1.ifcvirtualelement' in typeof(temp)]) == 0) is not False

class IfcRelAssociatesMaterial_AllowedElements:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssociatesMaterial'
    RULE_NAME = 'AllowedElements'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in getattr(self, 'RelatedObjects', INDETERMINATE) if sizeof(typeof(temp) * ['ifc4x1.ifcelement', 'ifc4x1.ifcelementtype', 'ifc4x1.ifcwindowstyle', 'ifc4x1.ifcdoorstyle', 'ifc4x1.ifcstructuralmember', 'ifc4x1.ifcport']) == 0]) == 0) is not False

class IfcRelConnectsElements_NoSelfReference:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelConnectsElements'
    RULE_NAME = 'NoSelfReference'

    @staticmethod
    def __call__(self):
        relatingelement = getattr(self, 'RelatingElement', INDETERMINATE)
        relatedelement = getattr(self, 'RelatedElement', INDETERMINATE)
        assert (relatingelement != relatedelement) is not False

class IfcRelConnectsPathElements_NormalizedRelatingPriorities:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelConnectsPathElements'
    RULE_NAME = 'NormalizedRelatingPriorities'

    @staticmethod
    def __call__(self):
        relatingpriorities = getattr(self, 'RelatingPriorities', INDETERMINATE)
        assert (sizeof(relatingpriorities) == 0 or sizeof([temp for temp in relatingpriorities if 0 <= temp <= 100]) == sizeof(relatingpriorities)) is not False

class IfcRelConnectsPathElements_NormalizedRelatedPriorities:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelConnectsPathElements'
    RULE_NAME = 'NormalizedRelatedPriorities'

    @staticmethod
    def __call__(self):
        relatedpriorities = getattr(self, 'RelatedPriorities', INDETERMINATE)
        assert (sizeof(relatedpriorities) == 0 or sizeof([temp for temp in relatedpriorities if 0 <= temp <= 100]) == sizeof(relatedpriorities)) is not False

class IfcRelConnectsPorts_NoSelfReference:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelConnectsPorts'
    RULE_NAME = 'NoSelfReference'

    @staticmethod
    def __call__(self):
        relatingport = getattr(self, 'RelatingPort', INDETERMINATE)
        relatedport = getattr(self, 'RelatedPort', INDETERMINATE)
        assert (relatingport != relatedport) is not False

class IfcRelContainedInSpatialStructure_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelContainedInSpatialStructure'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        relatedelements = getattr(self, 'RelatedElements', INDETERMINATE)
        assert (sizeof([temp for temp in relatedelements if 'ifc4x1.ifcspatialstructureelement' in typeof(temp)]) == 0) is not False

class IfcRelDeclares_NoSelfReference:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelDeclares'
    RULE_NAME = 'NoSelfReference'

    @staticmethod
    def __call__(self):
        relatingcontext = getattr(self, 'RelatingContext', INDETERMINATE)
        relateddefinitions = getattr(self, 'RelatedDefinitions', INDETERMINATE)
        assert (sizeof([temp for temp in relateddefinitions if relatingcontext == temp]) == 0) is not False

class IfcRelDefinesByProperties_NoRelatedTypeObject:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelDefinesByProperties'
    RULE_NAME = 'NoRelatedTypeObject'

    @staticmethod
    def __call__(self):
        assert (sizeof([types for types in getattr(self, 'RelatedObjects', INDETERMINATE) if 'ifc4x1.ifctypeobject' in typeof(types)]) == 0) is not False

class IfcRelInterferesElements_NotSelfReference:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelInterferesElements'
    RULE_NAME = 'NotSelfReference'

    @staticmethod
    def __call__(self):
        relatingelement = getattr(self, 'RelatingElement', INDETERMINATE)
        relatedelement = getattr(self, 'RelatedElement', INDETERMINATE)
        assert (relatingelement != relatedelement) is not False

class IfcRelNests_NoSelfReference:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelNests'
    RULE_NAME = 'NoSelfReference'

    @staticmethod
    def __call__(self):
        relatingobject = getattr(self, 'RelatingObject', INDETERMINATE)
        relatedobjects = getattr(self, 'RelatedObjects', INDETERMINATE)
        assert (sizeof([temp for temp in relatedobjects if relatingobject == temp]) == 0) is not False

class IfcRelReferencedInSpatialStructure_AllowedRelatedElements:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelReferencedInSpatialStructure'
    RULE_NAME = 'AllowedRelatedElements'

    @staticmethod
    def __call__(self):
        relatedelements = getattr(self, 'RelatedElements', INDETERMINATE)
        assert (sizeof([temp for temp in relatedelements if 'ifc4x1.ifcspatialstructureelement' in typeof(temp) and (not 'ifc4x1.ifcspace' in typeof(temp))]) == 0) is not False

class IfcRelSequence_AvoidInconsistentSequence:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelSequence'
    RULE_NAME = 'AvoidInconsistentSequence'

    @staticmethod
    def __call__(self):
        relatingprocess = getattr(self, 'RelatingProcess', INDETERMINATE)
        relatedprocess = getattr(self, 'RelatedProcess', INDETERMINATE)
        assert (relatingprocess != relatedprocess) is not False

class IfcRelSequence_CorrectSequenceType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelSequence'
    RULE_NAME = 'CorrectSequenceType'

    @staticmethod
    def __call__(self):
        sequencetype = getattr(self, 'SequenceType', INDETERMINATE)
        userdefinedsequencetype = getattr(self, 'UserDefinedSequenceType', INDETERMINATE)
        assert (sequencetype != getattr(IfcSequenceEnum, 'USERDEFINED', INDETERMINATE) or (sequencetype == getattr(IfcSequenceEnum, 'USERDEFINED', INDETERMINATE) and exists(userdefinedsequencetype))) is not False

class IfcRelSpaceBoundary_CorrectPhysOrVirt:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelSpaceBoundary'
    RULE_NAME = 'CorrectPhysOrVirt'

    @staticmethod
    def __call__(self):
        relatedbuildingelement = getattr(self, 'RelatedBuildingElement', INDETERMINATE)
        physicalorvirtualboundary = getattr(self, 'PhysicalOrVirtualBoundary', INDETERMINATE)
        assert (physicalorvirtualboundary == getattr(IfcPhysicalOrVirtualEnum, 'Physical', INDETERMINATE) and (not 'ifc4x1.ifcvirtualelement' in typeof(relatedbuildingelement)) or (physicalorvirtualboundary == getattr(IfcPhysicalOrVirtualEnum, 'Virtual', INDETERMINATE) and ('ifc4x1.ifcvirtualelement' in typeof(relatedbuildingelement) or 'ifc4x1.ifcopeningelement' in typeof(relatedbuildingelement))) or physicalorvirtualboundary == getattr(IfcPhysicalOrVirtualEnum, 'NotDefined', INDETERMINATE)) is not False

class IfcReparametrisedCompositeCurveSegment_PositiveLengthParameter:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcReparametrisedCompositeCurveSegment'
    RULE_NAME = 'PositiveLengthParameter'

    @staticmethod
    def __call__(self):
        paramlength = getattr(self, 'ParamLength', INDETERMINATE)
        assert (paramlength > 0.0) is not False

class IfcRepresentationMap_ApplicableMappedRepr:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRepresentationMap'
    RULE_NAME = 'ApplicableMappedRepr'

    @staticmethod
    def __call__(self):
        mappedrepresentation = getattr(self, 'MappedRepresentation', INDETERMINATE)
        assert ('ifc4x1.ifcshapemodel' in typeof(mappedrepresentation)) is not False

class IfcRevolvedAreaSolid_AxisStartInXY:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRevolvedAreaSolid'
    RULE_NAME = 'AxisStartInXY'

    @staticmethod
    def __call__(self):
        axis = getattr(self, 'Axis', INDETERMINATE)
        assert (express_getitem(getattr(getattr(axis, 'Location', INDETERMINATE), 'Coordinates', INDETERMINATE), 3 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) == 0.0) is not False

class IfcRevolvedAreaSolid_AxisDirectionInXY:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRevolvedAreaSolid'
    RULE_NAME = 'AxisDirectionInXY'

    @staticmethod
    def __call__(self):
        axis = getattr(self, 'Axis', INDETERMINATE)
        assert (express_getitem(getattr(getattr(axis, 'Z', INDETERMINATE), 'DirectionRatios', INDETERMINATE), 3 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) == 0.0) is not False

def calc_IfcRevolvedAreaSolid_AxisLine(self):
    axis = getattr(self, 'Axis', INDETERMINATE)
    return IfcLine(Pnt=getattr(axis, 'Location', INDETERMINATE), Dir=IfcVector(Orientation=getattr(axis, 'Z', INDETERMINATE), Magnitude=1.0))

class IfcRevolvedAreaSolidTapered_CorrectProfileAssignment:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRevolvedAreaSolidTapered'
    RULE_NAME = 'CorrectProfileAssignment'

    @staticmethod
    def __call__(self):
        assert IfcTaperedSweptAreaProfiles(getattr(self, 'SweptArea', INDETERMINATE), getattr(self, 'EndSweptArea', INDETERMINATE)) is not False

class IfcRoof_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRoof'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcRoofTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcRoofTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcRoof_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRoof'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcrooftype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcRoofType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRoofType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcRoofTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcRoofTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcRoundedRectangleProfileDef_ValidRadius:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRoundedRectangleProfileDef'
    RULE_NAME = 'ValidRadius'

    @staticmethod
    def __call__(self):
        roundingradius = getattr(self, 'RoundingRadius', INDETERMINATE)
        assert (roundingradius <= getattr(self, 'XDim', INDETERMINATE) / 2.0 and roundingradius <= getattr(self, 'YDim', INDETERMINATE) / 2.0) is not False

def calc_IfcSIUnit_Dimensions(self):
    return IfcDimensionsForSiUnit(getattr(self, 'Name', INDETERMINATE))

class IfcSanitaryTerminal_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSanitaryTerminal'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcSanitaryTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcSanitaryTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcSanitaryTerminal_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSanitaryTerminal'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcsanitaryterminaltype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcSanitaryTerminalType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSanitaryTerminalType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcSanitaryTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcSanitaryTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcSeamCurve_TwoPCurves:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSeamCurve'
    RULE_NAME = 'TwoPCurves'

    @staticmethod
    def __call__(self):
        assert (sizeof(getattr(self, 'AssociatedGeometry', INDETERMINATE)) == 2) is not False

class IfcSeamCurve_SameSurface:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSeamCurve'
    RULE_NAME = 'SameSurface'

    @staticmethod
    def __call__(self):
        assert (IfcAssociatedSurface(express_getitem(getattr(self, 'AssociatedGeometry', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) == IfcAssociatedSurface(express_getitem(getattr(self, 'AssociatedGeometry', INDETERMINATE), 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))) is not False

class IfcSectionedSolid_DirectrixIs3D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSectionedSolid'
    RULE_NAME = 'DirectrixIs3D'

    @staticmethod
    def __call__(self):
        directrix = getattr(self, 'Directrix', INDETERMINATE)
        assert (getattr(directrix, 'Dim', INDETERMINATE) == 3) is not False

class IfcSectionedSolid_ConsistentProfileTypes:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSectionedSolid'
    RULE_NAME = 'ConsistentProfileTypes'

    @staticmethod
    def __call__(self):
        crosssections = getattr(self, 'CrossSections', INDETERMINATE)
        assert (sizeof([temp for temp in crosssections if getattr(express_getitem(crosssections, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'ProfileType', INDETERMINATE) != getattr(temp, 'ProfileType', INDETERMINATE)]) == 0) is not False

class IfcSectionedSolid_SectionsSameType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSectionedSolid'
    RULE_NAME = 'SectionsSameType'

    @staticmethod
    def __call__(self):
        crosssections = getattr(self, 'CrossSections', INDETERMINATE)
        assert (sizeof([temp for temp in crosssections if typeof(express_getitem(crosssections, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) != typeof(temp)]) == 0) is not False

class IfcSectionedSolidHorizontal_CorrespondingSectionPositions:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSectionedSolidHorizontal'
    RULE_NAME = 'CorrespondingSectionPositions'

    @staticmethod
    def __call__(self):
        crosssections = getattr(self, 'CrossSections', INDETERMINATE)
        crosssectionpositions = getattr(self, 'CrossSectionPositions', INDETERMINATE)
        assert (sizeof(crosssections) == sizeof(crosssectionpositions)) is not False

class IfcSectionedSolidHorizontal_NoLongitudinalOffsets:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSectionedSolidHorizontal'
    RULE_NAME = 'NoLongitudinalOffsets'

    @staticmethod
    def __call__(self):
        crosssectionpositions = getattr(self, 'CrossSectionPositions', INDETERMINATE)
        assert (sizeof([temp for temp in crosssectionpositions if exists(getattr(temp, 'OffsetLongitudinal', INDETERMINATE))]) == 0) is not False

class IfcSectionedSpine_CorrespondingSectionPositions:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSectionedSpine'
    RULE_NAME = 'CorrespondingSectionPositions'

    @staticmethod
    def __call__(self):
        crosssections = getattr(self, 'CrossSections', INDETERMINATE)
        crosssectionpositions = getattr(self, 'CrossSectionPositions', INDETERMINATE)
        assert (sizeof(crosssections) == sizeof(crosssectionpositions)) is not False

class IfcSectionedSpine_ConsistentProfileTypes:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSectionedSpine'
    RULE_NAME = 'ConsistentProfileTypes'

    @staticmethod
    def __call__(self):
        crosssections = getattr(self, 'CrossSections', INDETERMINATE)
        assert (sizeof([temp for temp in crosssections if getattr(express_getitem(crosssections, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'ProfileType', INDETERMINATE) != getattr(temp, 'ProfileType', INDETERMINATE)]) == 0) is not False

class IfcSectionedSpine_SpineCurveDim:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSectionedSpine'
    RULE_NAME = 'SpineCurveDim'

    @staticmethod
    def __call__(self):
        spinecurve = getattr(self, 'SpineCurve', INDETERMINATE)
        assert (getattr(spinecurve, 'Dim', INDETERMINATE) == 3) is not False

def calc_IfcSectionedSpine_Dim(self):
    return 3

class IfcSensor_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSensor'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcSensorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcSensorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcSensor_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSensor'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcsensortype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcSensorType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSensorType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcSensorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcSensorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcShadingDevice_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcShadingDevice'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcShadingDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcShadingDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcShadingDevice_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcShadingDevice'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcshadingdevicetype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcShadingDeviceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcShadingDeviceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcShadingDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcShadingDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcShapeModel_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcShapeModel'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        ofshapeaspect = getattr(self, 'OfShapeAspect', INDETERMINATE)
        assert (sizeof(getattr(self, 'OfProductRepresentation', INDETERMINATE)) == 1) ^ (sizeof(getattr(self, 'RepresentationMap', INDETERMINATE)) == 1) ^ (sizeof(ofshapeaspect) == 1) is not False

class IfcShapeRepresentation_CorrectContext:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcShapeRepresentation'
    RULE_NAME = 'CorrectContext'

    @staticmethod
    def __call__(self):
        assert ('ifc4x1.ifcgeometricrepresentationcontext' in typeof(getattr(self, 'ContextOfItems', INDETERMINATE))) is not False

class IfcShapeRepresentation_NoTopologicalItem:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcShapeRepresentation'
    RULE_NAME = 'NoTopologicalItem'

    @staticmethod
    def __call__(self):
        items = getattr(self, 'Items', INDETERMINATE)
        assert (sizeof([temp for temp in items if 'ifc4x1.ifctopologicalrepresentationitem' in typeof(temp) and (not sizeof(['ifc4x1.ifcvertexpoint', 'ifc4x1.ifcedgecurve', 'ifc4x1.ifcfacesurface'] * typeof(temp)) == 1)]) == 0) is not False

class IfcShapeRepresentation_HasRepresentationType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcShapeRepresentation'
    RULE_NAME = 'HasRepresentationType'

    @staticmethod
    def __call__(self):
        assert exists(getattr(self, 'RepresentationType', INDETERMINATE)) is not False

class IfcShapeRepresentation_HasRepresentationIdentifier:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcShapeRepresentation'
    RULE_NAME = 'HasRepresentationIdentifier'

    @staticmethod
    def __call__(self):
        assert exists(getattr(self, 'RepresentationIdentifier', INDETERMINATE)) is not False

class IfcShapeRepresentation_CorrectItemsForType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcShapeRepresentation'
    RULE_NAME = 'CorrectItemsForType'

    @staticmethod
    def __call__(self):
        assert IfcShapeRepresentationTypes(getattr(self, 'RepresentationType', INDETERMINATE), getattr(self, 'Items', INDETERMINATE)) is not False

def calc_IfcShellBasedSurfaceModel_Dim(self):
    return 3

class IfcSlab_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSlab'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcSlabTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcSlabTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcSlab_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSlab'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcslabtype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcSlabElementedCase_HasDecomposition:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSlabElementedCase'
    RULE_NAME = 'HasDecomposition'

    @staticmethod
    def __call__(self):
        assert (hiindex(getattr(self, 'IsDecomposedBy', INDETERMINATE)) > 0) is not False

class IfcSlabStandardCase_HasMaterialLayerSetusage:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSlabStandardCase'
    RULE_NAME = 'HasMaterialLayerSetusage'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in usedin(self, 'ifc4x1.ifcrelassociates.relatedobjects') if 'ifc4x1.ifcrelassociatesmaterial' in typeof(temp) and 'ifc4x1.ifcmateriallayersetusage' in typeof(getattr(temp, 'RelatingMaterial', INDETERMINATE))]) == 1) is not False

class IfcSlabType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSlabType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcSlabTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcSlabTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcSolarDevice_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSolarDevice'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcSolarDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcSolarDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcSolarDevice_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSolarDevice'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcsolardevicetype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcSolarDeviceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSolarDeviceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcSolarDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcSolarDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

def calc_IfcSolidModel_Dim(self):
    return 3

class IfcSpace_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSpace'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcSpaceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcSpaceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcSpace_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSpace'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcspacetype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcSpaceHeater_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSpaceHeater'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcSpaceHeaterTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcSpaceHeaterTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcSpaceHeater_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSpaceHeater'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcspaceheatertype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcSpaceHeaterType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSpaceHeaterType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcSpaceHeaterTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcSpaceHeaterTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcSpaceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSpaceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcSpaceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcSpaceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcSpatialStructureElement_WR41:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSpatialStructureElement'
    RULE_NAME = 'WR41'

    @staticmethod
    def __call__(self):
        assert (hiindex(getattr(self, 'Decomposes', INDETERMINATE)) == 1 and 'ifc4x1.ifcrelaggregates' in typeof(express_getitem(getattr(self, 'Decomposes', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and ('ifc4x1.ifcproject' in typeof(getattr(express_getitem(getattr(self, 'Decomposes', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingObject', INDETERMINATE)) or 'ifc4x1.ifcspatialstructureelement' in typeof(getattr(express_getitem(getattr(self, 'Decomposes', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingObject', INDETERMINATE)))) is not False

class IfcSpatialZone_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSpatialZone'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcSpatialZoneTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcSpatialZoneTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcSpatialZone_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSpatialZone'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcspatialzonetype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcSpatialZoneType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSpatialZoneType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcSpatialZoneTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcSpatialZoneTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcStackTerminal_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStackTerminal'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcStackTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcStackTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcStackTerminal_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStackTerminal'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcstackterminaltype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcStackTerminalType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStackTerminalType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcStackTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcStackTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcStair_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStair'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcStairTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcStairTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcStair_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStair'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcstairtype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcStairFlight_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStairFlight'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcStairFlightTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcStairFlightTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcStairFlight_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStairFlight'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcstairflighttype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcStairFlightType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStairFlightType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcStairFlightTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcStairFlightTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcStairType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStairType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcStairTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcStairTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcStructuralAnalysisModel_HasObjectType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralAnalysisModel'
    RULE_NAME = 'HasObjectType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcAnalysisModelTypeEnum, 'USERDEFINED', INDETERMINATE) or exists(getattr(self, 'ObjectType', INDETERMINATE))) is not False

class IfcStructuralCurveAction_ProjectedIsGlobal:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralCurveAction'
    RULE_NAME = 'ProjectedIsGlobal'

    @staticmethod
    def __call__(self):
        projectedortrue = getattr(self, 'ProjectedOrTrue', INDETERMINATE)
        assert (not exists(projectedortrue) or (projectedortrue != projected_length or getattr(self, 'GlobalOrLocal', INDETERMINATE) == global_coords)) is not False

class IfcStructuralCurveAction_HasObjectType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralCurveAction'
    RULE_NAME = 'HasObjectType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcStructuralCurveActivityTypeEnum, 'USERDEFINED', INDETERMINATE) or exists(getattr(self, 'ObjectType', INDETERMINATE))) is not False

class IfcStructuralCurveAction_SuitablePredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralCurveAction'
    RULE_NAME = 'SuitablePredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcStructuralCurveActivityTypeEnum, 'EQUIDISTANT', INDETERMINATE)) is not False

class IfcStructuralCurveMember_HasObjectType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralCurveMember'
    RULE_NAME = 'HasObjectType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcStructuralCurveMemberTypeEnum, 'USERDEFINED', INDETERMINATE) or exists(getattr(self, 'ObjectType', INDETERMINATE))) is not False

class IfcStructuralCurveReaction_HasObjectType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralCurveReaction'
    RULE_NAME = 'HasObjectType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcStructuralCurveActivityTypeEnum, 'USERDEFINED', INDETERMINATE) or exists(getattr(self, 'ObjectType', INDETERMINATE))) is not False

class IfcStructuralCurveReaction_SuitablePredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralCurveReaction'
    RULE_NAME = 'SuitablePredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcStructuralCurveActivityTypeEnum, 'SINUS', INDETERMINATE) and predefinedtype != getattr(IfcStructuralCurveActivityTypeEnum, 'PARABOLA', INDETERMINATE)) is not False

class IfcStructuralLinearAction_SuitableLoadType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralLinearAction'
    RULE_NAME = 'SuitableLoadType'

    @staticmethod
    def __call__(self):
        assert (sizeof(['ifc4x1.ifcstructuralloadlinearforce', 'ifc4x1.ifcstructuralloadtemperature'] * typeof(getattr(self, 'AppliedLoad', INDETERMINATE))) == 1) is not False

class IfcStructuralLinearAction_ConstPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralLinearAction'
    RULE_NAME = 'ConstPredefinedType'

    @staticmethod
    def __call__(self):
        assert (getattr(self, 'PredefinedType', INDETERMINATE) == getattr(IfcStructuralCurveActivityTypeEnum, 'CONST', INDETERMINATE)) is not False

class IfcStructuralLoadCase_IsLoadCasePredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralLoadCase'
    RULE_NAME = 'IsLoadCasePredefinedType'

    @staticmethod
    def __call__(self):
        assert (getattr(self, 'PredefinedType', INDETERMINATE) == getattr(IfcLoadGroupTypeEnum, 'LOAD_CASE', INDETERMINATE)) is not False

class IfcStructuralLoadConfiguration_ValidListSize:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralLoadConfiguration'
    RULE_NAME = 'ValidListSize'

    @staticmethod
    def __call__(self):
        values = getattr(self, 'Values', INDETERMINATE)
        locations = getattr(self, 'Locations', INDETERMINATE)
        assert (not exists(locations) or sizeof(locations) == sizeof(values)) is not False

class IfcStructuralLoadGroup_HasObjectType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralLoadGroup'
    RULE_NAME = 'HasObjectType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        actiontype = getattr(self, 'ActionType', INDETERMINATE)
        actionsource = getattr(self, 'ActionSource', INDETERMINATE)
        assert (predefinedtype != getattr(IfcLoadGroupTypeEnum, 'USERDEFINED', INDETERMINATE) and actiontype != getattr(IfcActionTypeEnum, 'USERDEFINED', INDETERMINATE) and (actionsource != getattr(IfcActionSourceTypeEnum, 'USERDEFINED', INDETERMINATE)) or exists(getattr(self, 'ObjectType', INDETERMINATE))) is not False

class IfcStructuralPlanarAction_SuitableLoadType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralPlanarAction'
    RULE_NAME = 'SuitableLoadType'

    @staticmethod
    def __call__(self):
        assert (sizeof(['ifc4x1.ifcstructuralloadplanarforce', 'ifc4x1.ifcstructuralloadtemperature'] * typeof(getattr(self, 'AppliedLoad', INDETERMINATE))) == 1) is not False

class IfcStructuralPlanarAction_ConstPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralPlanarAction'
    RULE_NAME = 'ConstPredefinedType'

    @staticmethod
    def __call__(self):
        assert (getattr(self, 'PredefinedType', INDETERMINATE) == getattr(IfcStructuralSurfaceActivityTypeEnum, 'CONST', INDETERMINATE)) is not False

class IfcStructuralPointAction_SuitableLoadType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralPointAction'
    RULE_NAME = 'SuitableLoadType'

    @staticmethod
    def __call__(self):
        assert (sizeof(['ifc4x1.ifcstructuralloadsingleforce', 'ifc4x1.ifcstructuralloadsingledisplacement'] * typeof(getattr(self, 'AppliedLoad', INDETERMINATE))) == 1) is not False

class IfcStructuralPointReaction_SuitableLoadType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralPointReaction'
    RULE_NAME = 'SuitableLoadType'

    @staticmethod
    def __call__(self):
        assert (sizeof(['ifc4x1.ifcstructuralloadsingleforce', 'ifc4x1.ifcstructuralloadsingledisplacement'] * typeof(getattr(self, 'AppliedLoad', INDETERMINATE))) == 1) is not False

class IfcStructuralResultGroup_HasObjectType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralResultGroup'
    RULE_NAME = 'HasObjectType'

    @staticmethod
    def __call__(self):
        theorytype = getattr(self, 'TheoryType', INDETERMINATE)
        assert (theorytype != getattr(IfcAnalysisTheoryTypeEnum, 'USERDEFINED', INDETERMINATE) or exists(getattr(self, 'ObjectType', INDETERMINATE))) is not False

class IfcStructuralSurfaceAction_ProjectedIsGlobal:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralSurfaceAction'
    RULE_NAME = 'ProjectedIsGlobal'

    @staticmethod
    def __call__(self):
        projectedortrue = getattr(self, 'ProjectedOrTrue', INDETERMINATE)
        assert (not exists(projectedortrue) or (projectedortrue != projected_length or getattr(self, 'GlobalOrLocal', INDETERMINATE) == global_coords)) is not False

class IfcStructuralSurfaceAction_HasObjectType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralSurfaceAction'
    RULE_NAME = 'HasObjectType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcStructuralSurfaceActivityTypeEnum, 'USERDEFINED', INDETERMINATE) or exists(getattr(self, 'ObjectType', INDETERMINATE))) is not False

class IfcStructuralSurfaceMember_HasObjectType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralSurfaceMember'
    RULE_NAME = 'HasObjectType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcStructuralSurfaceMemberTypeEnum, 'USERDEFINED', INDETERMINATE) or exists(getattr(self, 'ObjectType', INDETERMINATE))) is not False

class IfcStructuralSurfaceReaction_HasPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralSurfaceReaction'
    RULE_NAME = 'HasPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcStructuralSurfaceActivityTypeEnum, 'USERDEFINED', INDETERMINATE) or exists(getattr(self, 'ObjectType', INDETERMINATE))) is not False

class IfcStyledItem_ApplicableItem:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStyledItem'
    RULE_NAME = 'ApplicableItem'

    @staticmethod
    def __call__(self):
        item = getattr(self, 'Item', INDETERMINATE)
        assert (not 'ifc4x1.ifcstyleditem' in typeof(item)) is not False

class IfcStyledRepresentation_OnlyStyledItems:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStyledRepresentation'
    RULE_NAME = 'OnlyStyledItems'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in getattr(self, 'Items', INDETERMINATE) if not 'ifc4x1.ifcstyleditem' in typeof(temp)]) == 0) is not False

class IfcSubContractResource_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSubContractResource'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcSubContractResourceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcSubContractResourceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcSubContractResourceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSubContractResourceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcSubContractResourceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcSubContractResourceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ResourceType', INDETERMINATE)))) is not False

def calc_IfcSurface_Dim(self):
    return 3

class IfcSurfaceCurve_CurveIs3D:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceCurve'
    RULE_NAME = 'CurveIs3D'

    @staticmethod
    def __call__(self):
        curve3d = getattr(self, 'Curve3D', INDETERMINATE)
        assert (getattr(curve3d, 'Dim', INDETERMINATE) == 3) is not False

class IfcSurfaceCurve_CurveIsNotPcurve:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceCurve'
    RULE_NAME = 'CurveIsNotPcurve'

    @staticmethod
    def __call__(self):
        curve3d = getattr(self, 'Curve3D', INDETERMINATE)
        assert (not 'ifc4x1.ifcpcurve' in typeof(curve3d)) is not False

def calc_IfcSurfaceCurve_BasisSurface(self):
    return IfcGetBasisSurface(self)

class IfcSurfaceCurveSweptAreaSolid_DirectrixBounded:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceCurveSweptAreaSolid'
    RULE_NAME = 'DirectrixBounded'

    @staticmethod
    def __call__(self):
        directrix = getattr(self, 'Directrix', INDETERMINATE)
        startparam = getattr(self, 'StartParam', INDETERMINATE)
        endparam = getattr(self, 'EndParam', INDETERMINATE)
        assert (exists(startparam) and exists(endparam) or sizeof(['ifc4x1.ifcconic', 'ifc4x1.ifcboundedcurve'] * typeof(directrix)) == 1) is not False

class IfcSurfaceFeature_HasObjectType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceFeature'
    RULE_NAME = 'HasObjectType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcSurfaceFeatureTypeEnum, 'USERDEFINED', INDETERMINATE) or exists(getattr(self, 'ObjectType', INDETERMINATE))) is not False

class IfcSurfaceOfLinearExtrusion_DepthGreaterZero:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceOfLinearExtrusion'
    RULE_NAME = 'DepthGreaterZero'

    @staticmethod
    def __call__(self):
        depth = getattr(self, 'Depth', INDETERMINATE)
        assert (depth > 0.0) is not False

def calc_IfcSurfaceOfLinearExtrusion_ExtrusionAxis(self):
    extrudeddirection = getattr(self, 'ExtrudedDirection', INDETERMINATE)
    depth = getattr(self, 'Depth', INDETERMINATE)
    return IfcVector(Orientation=extrudeddirection, Magnitude=depth)

def calc_IfcSurfaceOfRevolution_AxisLine(self):
    axisposition = getattr(self, 'AxisPosition', INDETERMINATE)
    return IfcLine(Pnt=getattr(axisposition, 'Location', INDETERMINATE), Dir=IfcVector(Orientation=getattr(axisposition, 'Z', INDETERMINATE), Magnitude=1.0))

class IfcSurfaceReinforcementArea_SurfaceAndOrShearAreaSpecified:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceReinforcementArea'
    RULE_NAME = 'SurfaceAndOrShearAreaSpecified'

    @staticmethod
    def __call__(self):
        surfacereinforcement1 = getattr(self, 'SurfaceReinforcement1', INDETERMINATE)
        surfacereinforcement2 = getattr(self, 'SurfaceReinforcement2', INDETERMINATE)
        shearreinforcement = getattr(self, 'ShearReinforcement', INDETERMINATE)
        assert (exists(surfacereinforcement1) or exists(surfacereinforcement2) or exists(shearreinforcement)) is not False

class IfcSurfaceReinforcementArea_NonnegativeArea1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceReinforcementArea'
    RULE_NAME = 'NonnegativeArea1'

    @staticmethod
    def __call__(self):
        surfacereinforcement1 = getattr(self, 'SurfaceReinforcement1', INDETERMINATE)
        assert (not exists(surfacereinforcement1) or (express_getitem(surfacereinforcement1, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) >= 0.0 and express_getitem(surfacereinforcement1, 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) >= 0.0 and (sizeof(surfacereinforcement1) == 1 or express_getitem(surfacereinforcement1, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) >= 0.0))) is not False

class IfcSurfaceReinforcementArea_NonnegativeArea2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceReinforcementArea'
    RULE_NAME = 'NonnegativeArea2'

    @staticmethod
    def __call__(self):
        surfacereinforcement2 = getattr(self, 'SurfaceReinforcement2', INDETERMINATE)
        assert (not exists(surfacereinforcement2) or (express_getitem(surfacereinforcement2, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) >= 0.0 and express_getitem(surfacereinforcement2, 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) >= 0.0 and (sizeof(surfacereinforcement2) == 1 or express_getitem(surfacereinforcement2, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) >= 0.0))) is not False

class IfcSurfaceReinforcementArea_NonnegativeArea3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceReinforcementArea'
    RULE_NAME = 'NonnegativeArea3'

    @staticmethod
    def __call__(self):
        shearreinforcement = getattr(self, 'ShearReinforcement', INDETERMINATE)
        assert (not exists(shearreinforcement) or shearreinforcement >= 0.0) is not False

class IfcSurfaceStyle_MaxOneShading:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceStyle'
    RULE_NAME = 'MaxOneShading'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in getattr(self, 'Styles', INDETERMINATE) if 'ifc4x1.ifcsurfacestyleshading' in typeof(style)]) <= 1) is not False

class IfcSurfaceStyle_MaxOneLighting:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceStyle'
    RULE_NAME = 'MaxOneLighting'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in getattr(self, 'Styles', INDETERMINATE) if 'ifc4x1.ifcsurfacestylelighting' in typeof(style)]) <= 1) is not False

class IfcSurfaceStyle_MaxOneRefraction:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceStyle'
    RULE_NAME = 'MaxOneRefraction'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in getattr(self, 'Styles', INDETERMINATE) if 'ifc4x1.ifcsurfacestylerefraction' in typeof(style)]) <= 1) is not False

class IfcSurfaceStyle_MaxOneTextures:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceStyle'
    RULE_NAME = 'MaxOneTextures'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in getattr(self, 'Styles', INDETERMINATE) if 'ifc4x1.ifcsurfacestylewithtextures' in typeof(style)]) <= 1) is not False

class IfcSurfaceStyle_MaxOneExtDefined:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceStyle'
    RULE_NAME = 'MaxOneExtDefined'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in getattr(self, 'Styles', INDETERMINATE) if 'ifc4x1.ifcexternallydefinedsurfacestyle' in typeof(style)]) <= 1) is not False

class IfcSweptAreaSolid_SweptAreaType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSweptAreaSolid'
    RULE_NAME = 'SweptAreaType'

    @staticmethod
    def __call__(self):
        sweptarea = getattr(self, 'SweptArea', INDETERMINATE)
        assert (getattr(sweptarea, 'ProfileType', INDETERMINATE) == getattr(IfcProfileTypeEnum, 'Area', INDETERMINATE)) is not False

class IfcSweptDiskSolid_DirectrixDim:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSweptDiskSolid'
    RULE_NAME = 'DirectrixDim'

    @staticmethod
    def __call__(self):
        directrix = getattr(self, 'Directrix', INDETERMINATE)
        assert (getattr(directrix, 'Dim', INDETERMINATE) == 3) is not False

class IfcSweptDiskSolid_InnerRadiusSize:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSweptDiskSolid'
    RULE_NAME = 'InnerRadiusSize'

    @staticmethod
    def __call__(self):
        radius = getattr(self, 'Radius', INDETERMINATE)
        innerradius = getattr(self, 'InnerRadius', INDETERMINATE)
        assert (not exists(innerradius) or radius > innerradius) is not False

class IfcSweptDiskSolid_DirectrixBounded:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSweptDiskSolid'
    RULE_NAME = 'DirectrixBounded'

    @staticmethod
    def __call__(self):
        directrix = getattr(self, 'Directrix', INDETERMINATE)
        startparam = getattr(self, 'StartParam', INDETERMINATE)
        endparam = getattr(self, 'EndParam', INDETERMINATE)
        assert (exists(startparam) and exists(endparam) or sizeof(['ifc4x1.ifcconic', 'ifc4x1.ifcboundedcurve'] * typeof(directrix)) == 1) is not False

class IfcSweptDiskSolidPolygonal_CorrectRadii:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSweptDiskSolidPolygonal'
    RULE_NAME = 'CorrectRadii'

    @staticmethod
    def __call__(self):
        filletradius = getattr(self, 'FilletRadius', INDETERMINATE)
        assert (not exists(filletradius) or filletradius >= getattr(self, 'Radius', INDETERMINATE)) is not False

class IfcSweptDiskSolidPolygonal_DirectrixIsPolyline:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSweptDiskSolidPolygonal'
    RULE_NAME = 'DirectrixIsPolyline'

    @staticmethod
    def __call__(self):
        assert ('ifc4x1.ifcpolyline' in typeof(getattr(self, 'Directrix', INDETERMINATE)) or ('ifc4x1.ifcindexedpolycurve' in typeof(getattr(self, 'Directrix', INDETERMINATE)) and (not exists(getattr(getattr(self, 'Directrix', INDETERMINATE), 'Segments', INDETERMINATE))))) is not False

class IfcSweptSurface_SweptCurveType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSweptSurface'
    RULE_NAME = 'SweptCurveType'

    @staticmethod
    def __call__(self):
        sweptcurve = getattr(self, 'SweptCurve', INDETERMINATE)
        assert (getattr(sweptcurve, 'ProfileType', INDETERMINATE) == getattr(IfcProfileTypeEnum, 'Curve', INDETERMINATE)) is not False

class IfcSwitchingDevice_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSwitchingDevice'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcSwitchingDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcSwitchingDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcSwitchingDevice_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSwitchingDevice'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcswitchingdevicetype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcSwitchingDeviceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSwitchingDeviceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcSwitchingDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcSwitchingDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcSystemFurnitureElement_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSystemFurnitureElement'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcSystemFurnitureElementTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcSystemFurnitureElementTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcSystemFurnitureElement_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSystemFurnitureElement'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcsystemfurnitureelementtype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcSystemFurnitureElementType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSystemFurnitureElementType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcSystemFurnitureElementTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcSystemFurnitureElementTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcTShapeProfileDef_ValidFlangeThickness:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTShapeProfileDef'
    RULE_NAME = 'ValidFlangeThickness'

    @staticmethod
    def __call__(self):
        depth = getattr(self, 'Depth', INDETERMINATE)
        flangethickness = getattr(self, 'FlangeThickness', INDETERMINATE)
        assert (flangethickness < depth) is not False

class IfcTShapeProfileDef_ValidWebThickness:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTShapeProfileDef'
    RULE_NAME = 'ValidWebThickness'

    @staticmethod
    def __call__(self):
        flangewidth = getattr(self, 'FlangeWidth', INDETERMINATE)
        webthickness = getattr(self, 'WebThickness', INDETERMINATE)
        assert (webthickness < flangewidth) is not False

class IfcTable_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTable'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        rows = getattr(self, 'Rows', INDETERMINATE)
        assert (sizeof([temp for temp in rows if hiindex(getattr(temp, 'RowCells', INDETERMINATE)) != hiindex(getattr(express_getitem(rows, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RowCells', INDETERMINATE))]) == 0) is not False

class IfcTable_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTable'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        numberofheadings = getattr(self, 'NumberOfHeadings', INDETERMINATE)
        assert (0 <= numberofheadings <= 1) is not False

def calc_IfcTable_NumberOfCellsInRow(self):
    rows = getattr(self, 'Rows', INDETERMINATE)
    return hiindex(getattr(express_getitem(rows, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RowCells', INDETERMINATE))

def calc_IfcTable_NumberOfHeadings(self):
    rows = getattr(self, 'Rows', INDETERMINATE)
    return sizeof([temp for temp in rows if getattr(temp, 'IsHeading', INDETERMINATE)])

def calc_IfcTable_NumberOfDataRows(self):
    rows = getattr(self, 'Rows', INDETERMINATE)
    return sizeof([temp for temp in rows if not getattr(temp, 'IsHeading', INDETERMINATE)])

class IfcTank_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTank'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcTankTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcTankTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcTank_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTank'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifctanktype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcTankType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTankType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcTankTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcTankTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcTask_HasName:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTask'
    RULE_NAME = 'HasName'

    @staticmethod
    def __call__(self):
        assert exists(getattr(self, 'Name', INDETERMINATE)) is not False

class IfcTask_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTask'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcTaskTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcTaskTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcTaskType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTaskType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcTaskTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcTaskTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ProcessType', INDETERMINATE)))) is not False

class IfcTelecomAddress_MinimumDataProvided:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTelecomAddress'
    RULE_NAME = 'MinimumDataProvided'

    @staticmethod
    def __call__(self):
        telephonenumbers = getattr(self, 'TelephoneNumbers', INDETERMINATE)
        facsimilenumbers = getattr(self, 'FacsimileNumbers', INDETERMINATE)
        pagernumber = getattr(self, 'PagerNumber', INDETERMINATE)
        electronicmailaddresses = getattr(self, 'ElectronicMailAddresses', INDETERMINATE)
        wwwhomepageurl = getattr(self, 'WWWHomePageURL', INDETERMINATE)
        messagingids = getattr(self, 'MessagingIDs', INDETERMINATE)
        assert (exists(telephonenumbers) or exists(facsimilenumbers) or exists(pagernumber) or exists(electronicmailaddresses) or exists(wwwhomepageurl) or exists(messagingids)) is not False

class IfcTendon_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTendon'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcTendonTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcTendonTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcTendon_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTendon'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifctendontype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcTendonAnchor_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTendonAnchor'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcTendonAnchorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcTendonAnchorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcTendonAnchor_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTendonAnchor'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifctendonanchortype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcTendonAnchorType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTendonAnchorType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcTendonAnchorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcTendonAnchorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcTendonType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTendonType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcTendonTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcTendonTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

def calc_IfcTessellatedFaceSet_Dim(self):
    return 3

class IfcTextLiteralWithExtent_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTextLiteralWithExtent'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        extent = getattr(self, 'Extent', INDETERMINATE)
        assert (not 'ifc4x1.ifcplanarbox' in typeof(extent)) is not False

class IfcTextStyleFontModel_MeasureOfFontSize:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTextStyleFontModel'
    RULE_NAME = 'MeasureOfFontSize'

    @staticmethod
    def __call__(self):
        assert ('ifc4x1.ifclengthmeasure' in typeof(getattr(self, 'FontSize', INDETERMINATE)) and getattr(self, 'FontSize', INDETERMINATE) > 0.0) is not False

class IfcTopologyRepresentation_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTopologyRepresentation'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in getattr(self, 'Items', INDETERMINATE) if not 'ifc4x1.ifctopologicalrepresentationitem' in typeof(temp)]) == 0) is not False

class IfcTopologyRepresentation_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTopologyRepresentation'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        assert exists(getattr(self, 'RepresentationType', INDETERMINATE)) is not False

class IfcTopologyRepresentation_WR23:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTopologyRepresentation'
    RULE_NAME = 'WR23'

    @staticmethod
    def __call__(self):
        assert IfcTopologyRepresentationTypes(getattr(self, 'RepresentationType', INDETERMINATE), getattr(self, 'Items', INDETERMINATE)) is not False

class IfcToroidalSurface_MajorLargerMinor:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcToroidalSurface'
    RULE_NAME = 'MajorLargerMinor'

    @staticmethod
    def __call__(self):
        majorradius = getattr(self, 'MajorRadius', INDETERMINATE)
        minorradius = getattr(self, 'MinorRadius', INDETERMINATE)
        assert (minorradius < majorradius) is not False

class IfcTransformer_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTransformer'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcTransformerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcTransformerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcTransformer_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTransformer'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifctranformertype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcTransformerType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTransformerType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcTransformerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcTransformerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcTransportElement_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTransportElement'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcTransportElementTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcTransportElementTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcTransportElement_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTransportElement'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifctransportelementtype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcTransportElementType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTransportElementType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcTransportElementTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcTransportElementTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

def calc_IfcTriangulatedFaceSet_NumberOfTriangles(self):
    coordindex = getattr(self, 'CoordIndex', INDETERMINATE)
    return sizeof(coordindex)

class IfcTriangulatedIrregularNetwork_NotClosed:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTriangulatedIrregularNetwork'
    RULE_NAME = 'NotClosed'

    @staticmethod
    def __call__(self):
        assert (getattr(self, 'Closed', INDETERMINATE) == False) is not False

class IfcTrimmedCurve_Trim1ValuesConsistent:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTrimmedCurve'
    RULE_NAME = 'Trim1ValuesConsistent'

    @staticmethod
    def __call__(self):
        trim1 = getattr(self, 'Trim1', INDETERMINATE)
        assert (hiindex(trim1) == 1 or typeof(express_getitem(trim1, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) != typeof(express_getitem(trim1, 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))) is not False

class IfcTrimmedCurve_Trim2ValuesConsistent:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTrimmedCurve'
    RULE_NAME = 'Trim2ValuesConsistent'

    @staticmethod
    def __call__(self):
        trim2 = getattr(self, 'Trim2', INDETERMINATE)
        assert (hiindex(trim2) == 1 or typeof(express_getitem(trim2, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) != typeof(express_getitem(trim2, 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))) is not False

class IfcTrimmedCurve_NoTrimOfBoundedCurves:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTrimmedCurve'
    RULE_NAME = 'NoTrimOfBoundedCurves'

    @staticmethod
    def __call__(self):
        basiscurve = getattr(self, 'BasisCurve', INDETERMINATE)
        assert (not 'ifc4x1.ifcboundedcurve' in typeof(basiscurve)) is not False

class IfcTubeBundle_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTubeBundle'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcTubeBundleTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcTubeBundleTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcTubeBundle_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTubeBundle'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifctubebundletype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcTubeBundleType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTubeBundleType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcTubeBundleTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcTubeBundleTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcTypeObject_NameRequired:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTypeObject'
    RULE_NAME = 'NameRequired'

    @staticmethod
    def __call__(self):
        assert exists(getattr(self, 'Name', INDETERMINATE)) is not False

class IfcTypeObject_UniquePropertySetNames:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTypeObject'
    RULE_NAME = 'UniquePropertySetNames'

    @staticmethod
    def __call__(self):
        haspropertysets = getattr(self, 'HasPropertySets', INDETERMINATE)
        assert (not exists(haspropertysets) or IfcUniquePropertySetNames(haspropertysets)) is not False

class IfcTypeProduct_ApplicableOccurrence:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTypeProduct'
    RULE_NAME = 'ApplicableOccurrence'

    @staticmethod
    def __call__(self):
        assert (not exists(lambda : express_getitem(getattr(self, 'Types', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) or sizeof([temp for temp in getattr(express_getitem(getattr(self, 'Types', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatedObjects', INDETERMINATE) if not 'ifc4x1.ifcproduct' in typeof(temp)]) == 0) is not False

class IfcUShapeProfileDef_ValidFlangeThickness:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcUShapeProfileDef'
    RULE_NAME = 'ValidFlangeThickness'

    @staticmethod
    def __call__(self):
        depth = getattr(self, 'Depth', INDETERMINATE)
        flangethickness = getattr(self, 'FlangeThickness', INDETERMINATE)
        assert (flangethickness < depth / 2.0) is not False

class IfcUShapeProfileDef_ValidWebThickness:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcUShapeProfileDef'
    RULE_NAME = 'ValidWebThickness'

    @staticmethod
    def __call__(self):
        flangewidth = getattr(self, 'FlangeWidth', INDETERMINATE)
        webthickness = getattr(self, 'WebThickness', INDETERMINATE)
        assert (webthickness < flangewidth) is not False

class IfcUnitAssignment_WR01:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcUnitAssignment'
    RULE_NAME = 'WR01'

    @staticmethod
    def __call__(self):
        units = getattr(self, 'Units', INDETERMINATE)
        assert IfcCorrectUnitAssignment(units) is not False

class IfcUnitaryControlElement_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcUnitaryControlElement'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcUnitaryControlElementTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcUnitaryControlElementTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcUnitaryControlElement_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcUnitaryControlElement'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcunitarycontrolelementtype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcUnitaryControlElementType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcUnitaryControlElementType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcUnitaryControlElementTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcUnitaryControlElementTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcUnitaryEquipment_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcUnitaryEquipment'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcUnitaryEquipmentTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcUnitaryEquipmentTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcUnitaryEquipment_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcUnitaryEquipment'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcunitaryequipmenttype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcUnitaryEquipmentType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcUnitaryEquipmentType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcUnitaryEquipmentTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcUnitaryEquipmentTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcValve_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcValve'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcValveTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcValveTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcValve_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcValve'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcvalvetype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcValveType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcValveType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcValveTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcValveTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcVector_MagGreaterOrEqualZero:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcVector'
    RULE_NAME = 'MagGreaterOrEqualZero'

    @staticmethod
    def __call__(self):
        magnitude = getattr(self, 'Magnitude', INDETERMINATE)
        assert (magnitude >= 0.0) is not False

def calc_IfcVector_Dim(self):
    orientation = getattr(self, 'Orientation', INDETERMINATE)
    return getattr(orientation, 'Dim', INDETERMINATE)

class IfcVibrationIsolator_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcVibrationIsolator'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcVibrationIsolatorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcVibrationIsolatorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcVibrationIsolator_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcVibrationIsolator'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcvibrationisolatortype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcVibrationIsolatorType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcVibrationIsolatorType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcVibrationIsolatorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcVibrationIsolatorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcVoidingFeature_HasObjectType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcVoidingFeature'
    RULE_NAME = 'HasObjectType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcVoidingFeatureTypeEnum, 'USERDEFINED', INDETERMINATE) or exists(getattr(self, 'ObjectType', INDETERMINATE))) is not False

class IfcWall_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWall'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcWallTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcWallTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcWall_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWall'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcwalltype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcWallElementedCase_HasDecomposition:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWallElementedCase'
    RULE_NAME = 'HasDecomposition'

    @staticmethod
    def __call__(self):
        assert (hiindex(getattr(self, 'IsDecomposedBy', INDETERMINATE)) > 0) is not False

class IfcWallStandardCase_HasMaterialLayerSetUsage:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWallStandardCase'
    RULE_NAME = 'HasMaterialLayerSetUsage'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in usedin(self, 'ifc4x1.ifcrelassociates.relatedobjects') if 'ifc4x1.ifcrelassociatesmaterial' in typeof(temp) and 'ifc4x1.ifcmateriallayersetusage' in typeof(getattr(temp, 'RelatingMaterial', INDETERMINATE))]) == 1) is not False

class IfcWallType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWallType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcWallTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcWallTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcWasteTerminal_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWasteTerminal'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcWasteTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcWasteTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcWasteTerminal_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWasteTerminal'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcwasteterminaltype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcWasteTerminalType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWasteTerminalType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcWasteTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcWasteTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcWindow_CorrectStyleAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWindow'
    RULE_NAME = 'CorrectStyleAssigned'

    @staticmethod
    def __call__(self):
        istypedby = getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x1.ifcwindowtype' in typeof(getattr(express_getitem(getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcWindowLiningProperties_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWindowLiningProperties'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        liningdepth = getattr(self, 'LiningDepth', INDETERMINATE)
        liningthickness = getattr(self, 'LiningThickness', INDETERMINATE)
        assert (not (exists(liningdepth) and (not exists(liningthickness)))) is not False

class IfcWindowLiningProperties_WR32:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWindowLiningProperties'
    RULE_NAME = 'WR32'

    @staticmethod
    def __call__(self):
        firsttransomoffset = getattr(self, 'FirstTransomOffset', INDETERMINATE)
        secondtransomoffset = getattr(self, 'SecondTransomOffset', INDETERMINATE)
        assert (not (not exists(firsttransomoffset) and exists(secondtransomoffset))) is not False

class IfcWindowLiningProperties_WR33:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWindowLiningProperties'
    RULE_NAME = 'WR33'

    @staticmethod
    def __call__(self):
        firstmullionoffset = getattr(self, 'FirstMullionOffset', INDETERMINATE)
        secondmullionoffset = getattr(self, 'SecondMullionOffset', INDETERMINATE)
        assert (not (not exists(firstmullionoffset) and exists(secondmullionoffset))) is not False

class IfcWindowLiningProperties_WR34:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWindowLiningProperties'
    RULE_NAME = 'WR34'

    @staticmethod
    def __call__(self):
        assert (exists(lambda : express_getitem(getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and ('ifc4x1.ifcwindowtype' in typeof(express_getitem(getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) or 'ifc4x1.ifcwindowstyle' in typeof(express_getitem(getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)))) is not False

class IfcWindowPanelProperties_ApplicableToType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWindowPanelProperties'
    RULE_NAME = 'ApplicableToType'

    @staticmethod
    def __call__(self):
        assert (exists(lambda : express_getitem(getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and ('ifc4x1.ifcwindowtype' in typeof(express_getitem(getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) or 'ifc4x1.ifcwindowstyle' in typeof(express_getitem(getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)))) is not False

class IfcWindowType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWindowType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcWindowTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcWindowTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcWorkCalendar_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWorkCalendar'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcWorkCalendarTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcWorkCalendarTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcWorkPlan_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWorkPlan'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcWorkPlanTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcWorkPlanTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcWorkSchedule_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWorkSchedule'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcWorkScheduleTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcWorkScheduleTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcZShapeProfileDef_ValidFlangeThickness:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcZShapeProfileDef'
    RULE_NAME = 'ValidFlangeThickness'

    @staticmethod
    def __call__(self):
        depth = getattr(self, 'Depth', INDETERMINATE)
        flangethickness = getattr(self, 'FlangeThickness', INDETERMINATE)
        assert (flangethickness < depth / 2.0) is not False

class IfcZone_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcZone'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (sizeof(getattr(self, 'IsGroupedBy', INDETERMINATE)) == 0 or sizeof([temp for temp in getattr(express_getitem(getattr(self, 'IsGroupedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatedObjects', INDETERMINATE) if not ('ifc4x1.ifczone' in typeof(temp) or 'ifc4x1.ifcspace' in typeof(temp) or 'ifc4x1.ifcspatialzone' in typeof(temp))]) == 0) is not False

class IfcRepresentationContextSameWCS:
    SCOPE = 'file'

    @staticmethod
    def __call__(file):
        IfcGeometricRepresentationContext = getattr(file, 'by_type', INDETERMINATE)('IfcGeometricRepresentationContext')
        isdifferent = False
        if sizeof(IfcGeometricRepresentationContext) > 1:
            for i in range(2, hiindex(IfcGeometricRepresentationContext) + 1):
                if getattr(express_getitem(IfcGeometricRepresentationContext, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'WorldCoordinateSystem', INDETERMINATE) != getattr(express_getitem(IfcGeometricRepresentationContext, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'WorldCoordinateSystem', INDETERMINATE):
                    isdifferent = not IfcSameValidPrecision(getattr(express_getitem(IfcGeometricRepresentationContext, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Precision', INDETERMINATE), getattr(express_getitem(IfcGeometricRepresentationContext, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Precision', INDETERMINATE)) or not IfcSameAxis2Placement(getattr(express_getitem(IfcGeometricRepresentationContext, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'WorldCoordinateSystem', INDETERMINATE), getattr(express_getitem(IfcGeometricRepresentationContext, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'WorldCoordinateSystem', INDETERMINATE), getattr(express_getitem(IfcGeometricRepresentationContext, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Precision', INDETERMINATE))
                    if isdifferent == True:
                        break
        assert (isdifferent == False) is not False

class IfcSingleProjectInstance:
    SCOPE = 'file'

    @staticmethod
    def __call__(file):
        IfcProject = getattr(file, 'by_type', INDETERMINATE)('IfcProject')
        assert (sizeof(IfcProject) <= 1) is not False

def IfcAssociatedSurface(arg):
    surf = getattr(arg, 'BasisSurface', INDETERMINATE)
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
                u[2 - EXPRESS_ONE_BASED_INDEXING].DirectionRatios[1 - EXPRESS_ONE_BASED_INDEXING] = -express_getitem(getattr(express_getitem(u, 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'DirectionRatios', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
                u[2 - EXPRESS_ONE_BASED_INDEXING].DirectionRatios[2 - EXPRESS_ONE_BASED_INDEXING] = -express_getitem(getattr(express_getitem(u, 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'DirectionRatios', INDETERMINATE), 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    elif exists(axis2):
        d1 = IfcNormalise(axis2)
        u = [IfcOrthogonalComplement(d1), d1]
        u[1 - EXPRESS_ONE_BASED_INDEXING].DirectionRatios[1 - EXPRESS_ONE_BASED_INDEXING] = -express_getitem(getattr(express_getitem(u, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'DirectionRatios', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
        u[1 - EXPRESS_ONE_BASED_INDEXING].DirectionRatios[2 - EXPRESS_ONE_BASED_INDEXING] = -express_getitem(getattr(express_getitem(u, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'DirectionRatios', INDETERMINATE), 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
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
    return [d2, getattr(IfcNormalise(IfcCrossProduct(d1, d2)), 'Orientation', INDETERMINATE), d1]

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
    temp = list(getattr(direction2d, 'DirectionRatios', INDETERMINATE))
    temp[1 - EXPRESS_ONE_BASED_INDEXING] = express_getitem(getattr(direction, 'DirectionRatios', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    direction2d.DirectionRatios = temp
    temp = list(getattr(direction2d, 'DirectionRatios', INDETERMINATE))
    temp[2 - EXPRESS_ONE_BASED_INDEXING] = express_getitem(getattr(direction, 'DirectionRatios', INDETERMINATE), 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
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
    external = sizeof([style for style in styles if 'ifc4x1.ifcexternallydefinedhatchstyle' in typeof(style)])
    hatching = sizeof([style for style in styles if 'ifc4x1.ifcfillareastylehatching' in typeof(style)])
    tiles = sizeof([style for style in styles if 'ifc4x1.ifcfillareastyletiles' in typeof(style)])
    colour = sizeof([style for style in styles if 'ifc4x1.ifccolour' in typeof(style)])
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
        if 'ifc4x1.ifcgridplacement' in typeof(relplacement):
            return None
        if 'ifc4x1.ifclocalplacement' in typeof(relplacement):
            if 'ifc4x1.ifcaxis2placement2d' in typeof(axisplacement):
                return True
            if 'ifc4x1.ifcaxis2placement3d' in typeof(axisplacement):
                if getattr(getattr(relplacement, 'RelativePlacement', INDETERMINATE), 'Dim', INDETERMINATE) == 3:
                    return True
                else:
                    return False
        return True
    return None

def IfcCorrectObjectAssignment(constraint, objects):
    count = 0
    if not exists(constraint):
        return True
    if constraint == getattr(IfcObjectTypeEnum, 'NOTDEFINED', INDETERMINATE):
        return True
    elif constraint == getattr(IfcObjectTypeEnum, 'PRODUCT', INDETERMINATE):
        count = sizeof([temp for temp in objects if not 'ifc4x1.ifcproduct' in typeof(temp)])
        return count == 0
    elif constraint == getattr(IfcObjectTypeEnum, 'PROCESS', INDETERMINATE):
        count = sizeof([temp for temp in objects if not 'ifc4x1.ifcprocess' in typeof(temp)])
        return count == 0
    elif constraint == getattr(IfcObjectTypeEnum, 'CONTROL', INDETERMINATE):
        count = sizeof([temp for temp in objects if not 'ifc4x1.ifccontrol' in typeof(temp)])
        return count == 0
    elif constraint == getattr(IfcObjectTypeEnum, 'RESOURCE', INDETERMINATE):
        count = sizeof([temp for temp in objects if not 'ifc4x1.ifcresource' in typeof(temp)])
        return count == 0
    elif constraint == getattr(IfcObjectTypeEnum, 'ACTOR', INDETERMINATE):
        count = sizeof([temp for temp in objects if not 'ifc4x1.ifcactor' in typeof(temp)])
        return count == 0
    elif constraint == getattr(IfcObjectTypeEnum, 'GROUP', INDETERMINATE):
        count = sizeof([temp for temp in objects if not 'ifc4x1.ifcgroup' in typeof(temp)])
        return count == 0
    elif constraint == getattr(IfcObjectTypeEnum, 'PROJECT', INDETERMINATE):
        count = sizeof([temp for temp in objects if not 'ifc4x1.ifcproject' in typeof(temp)])
        return count == 0
    else:
        return None

def IfcCorrectUnitAssignment(units):
    namedunitnumber = 0
    derivedunitnumber = 0
    monetaryunitnumber = 0
    namedunitnames = express_set([])
    derivedunitnames = express_set([])
    namedunitnumber = sizeof([temp for temp in units if 'ifc4x1.ifcnamedunit' in typeof(temp) and (not getattr(temp, 'UnitType', INDETERMINATE) == getattr(IfcUnitEnum, 'USERDEFINED', INDETERMINATE))])
    derivedunitnumber = sizeof([temp for temp in units if 'ifc4x1.ifcderivedunit' in typeof(temp) and (not getattr(temp, 'UnitType', INDETERMINATE) == getattr(IfcDerivedUnitEnum, 'USERDEFINED', INDETERMINATE))])
    monetaryunitnumber = sizeof([temp for temp in units if 'ifc4x1.ifcmonetaryunit' in typeof(temp)])
    for i in range(1, sizeof(units) + 1):
        if 'ifc4x1.ifcnamedunit' in typeof(express_getitem(units, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and (not getattr(express_getitem(units, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'UnitType', INDETERMINATE) == getattr(IfcUnitEnum, 'USERDEFINED', INDETERMINATE)):
            namedunitnames = namedunitnames + getattr(express_getitem(units, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'UnitType', INDETERMINATE)
        if 'ifc4x1.ifcderivedunit' in typeof(express_getitem(units, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and (not getattr(express_getitem(units, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'UnitType', INDETERMINATE) == getattr(IfcDerivedUnitEnum, 'USERDEFINED', INDETERMINATE)):
            derivedunitnames = derivedunitnames + getattr(express_getitem(units, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'UnitType', INDETERMINATE)
    return sizeof(namedunitnames) == namedunitnumber and sizeof(derivedunitnames) == derivedunitnumber and (monetaryunitnumber <= 1)

def IfcCrossProduct(arg1, arg2):
    if (not exists(arg1) or getattr(arg1, 'Dim', INDETERMINATE) == 2) or (not exists(arg2) or getattr(arg2, 'Dim', INDETERMINATE) == 2):
        return None
    else:
        v1 = getattr(IfcNormalise(arg1), 'DirectionRatios', INDETERMINATE)
        v2 = getattr(IfcNormalise(arg2), 'DirectionRatios', INDETERMINATE)
        res = IfcDirection(DirectionRatios=[express_getitem(v1, 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) * express_getitem(v2, 3 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) - express_getitem(v1, 3 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) * express_getitem(v2, 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), express_getitem(v1, 3 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) * express_getitem(v2, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) - express_getitem(v1, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) * express_getitem(v2, 3 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), express_getitem(v1, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) * express_getitem(v2, 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) - express_getitem(v1, 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) * express_getitem(v2, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)])
        mag = 0.0
        for i in range(1, 3 + 1):
            mag = mag + express_getitem(getattr(res, 'DirectionRatios', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) * express_getitem(getattr(res, 'DirectionRatios', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
        if mag > 0.0:
            result = IfcVector(Orientation=res, Magnitude=sqrt(mag))
        else:
            result = IfcVector(Orientation=arg1, Magnitude=0.0)
        return result

def IfcCurveDim(curve):
    if 'ifc4x1.ifcline' in typeof(curve):
        return getattr(getattr(curve, 'Pnt', INDETERMINATE), 'Dim', INDETERMINATE)
    if 'ifc4x1.ifcconic' in typeof(curve):
        return getattr(getattr(curve, 'Position', INDETERMINATE), 'Dim', INDETERMINATE)
    if 'ifc4x1.ifcpolyline' in typeof(curve):
        return getattr(express_getitem(getattr(curve, 'Points', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)
    if 'ifc4x1.ifctrimmedcurve' in typeof(curve):
        return IfcCurveDim(getattr(curve, 'BasisCurve', INDETERMINATE))
    if 'ifc4x1.ifccompositecurve' in typeof(curve):
        return getattr(express_getitem(getattr(curve, 'Segments', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)
    if 'ifc4x1.ifcbsplinecurve' in typeof(curve):
        return getattr(express_getitem(getattr(curve, 'ControlPointsList', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)
    if 'ifc4x1.ifcoffsetcurve2d' in typeof(curve):
        return 2
    if 'ifc4x1.ifcoffsetcurve3d' in typeof(curve):
        return 3
    if 'ifc4x1.ifcoffsetcurvebydistances' in typeof(curve):
        return 3
    if 'ifc4x1.ifccurvesegment2d' in typeof(curve):
        return 2
    if 'ifc4x1.ifcalignmentcurve' in typeof(curve):
        return 3
    if 'ifc4x1.ifcpcurve' in typeof(curve):
        return 3
    if 'ifc4x1.ifcindexedpolycurve' in typeof(curve):
        return getattr(getattr(curve, 'Points', INDETERMINATE), 'Dim', INDETERMINATE)
    return None

def IfcCurveWeightsPositive(b):
    result = True
    for i in range(0, getattr(b, 'UpperIndexOnControlPoints', INDETERMINATE) + 1):
        if express_getitem(getattr(b, 'Weights', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) <= 0.0:
            result = False
            return result
    return result

def IfcDeriveDimensionalExponents(unitelements):
    result = IfcDimensionalExponents(0, 0, 0, 0, 0, 0, 0)
    for i in range(loindex(unitelements), hiindex(unitelements) + 1):
        result.LengthExponent = getattr(result, 'LengthExponent', INDETERMINATE) + getattr(express_getitem(unitelements, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Exponent', INDETERMINATE) * getattr(getattr(getattr(express_getitem(unitelements, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Unit', INDETERMINATE), 'Dimensions', INDETERMINATE), 'LengthExponent', INDETERMINATE)
        result.MassExponent = getattr(result, 'MassExponent', INDETERMINATE) + getattr(express_getitem(unitelements, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Exponent', INDETERMINATE) * getattr(getattr(getattr(express_getitem(unitelements, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Unit', INDETERMINATE), 'Dimensions', INDETERMINATE), 'MassExponent', INDETERMINATE)
        result.TimeExponent = getattr(result, 'TimeExponent', INDETERMINATE) + getattr(express_getitem(unitelements, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Exponent', INDETERMINATE) * getattr(getattr(getattr(express_getitem(unitelements, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Unit', INDETERMINATE), 'Dimensions', INDETERMINATE), 'TimeExponent', INDETERMINATE)
        result.ElectricCurrentExponent = getattr(result, 'ElectricCurrentExponent', INDETERMINATE) + getattr(express_getitem(unitelements, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Exponent', INDETERMINATE) * getattr(getattr(getattr(express_getitem(unitelements, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Unit', INDETERMINATE), 'Dimensions', INDETERMINATE), 'ElectricCurrentExponent', INDETERMINATE)
        result.ThermodynamicTemperatureExponent = getattr(result, 'ThermodynamicTemperatureExponent', INDETERMINATE) + getattr(express_getitem(unitelements, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Exponent', INDETERMINATE) * getattr(getattr(getattr(express_getitem(unitelements, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Unit', INDETERMINATE), 'Dimensions', INDETERMINATE), 'ThermodynamicTemperatureExponent', INDETERMINATE)
        result.AmountOfSubstanceExponent = getattr(result, 'AmountOfSubstanceExponent', INDETERMINATE) + getattr(express_getitem(unitelements, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Exponent', INDETERMINATE) * getattr(getattr(getattr(express_getitem(unitelements, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Unit', INDETERMINATE), 'Dimensions', INDETERMINATE), 'AmountOfSubstanceExponent', INDETERMINATE)
        result.LuminousIntensityExponent = getattr(result, 'LuminousIntensityExponent', INDETERMINATE) + getattr(express_getitem(unitelements, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Exponent', INDETERMINATE) * getattr(getattr(getattr(express_getitem(unitelements, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Unit', INDETERMINATE), 'Dimensions', INDETERMINATE), 'LuminousIntensityExponent', INDETERMINATE)
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
    elif getattr(arg1, 'Dim', INDETERMINATE) != getattr(arg2, 'Dim', INDETERMINATE):
        scalar = None
    else:
        vec1 = IfcNormalise(arg1)
        vec2 = IfcNormalise(arg2)
        ndim = getattr(arg1, 'Dim', INDETERMINATE)
        scalar = 0.0
        for i in range(1, ndim + 1):
            scalar = scalar + express_getitem(getattr(vec1, 'DirectionRatios', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) * express_getitem(getattr(vec2, 'DirectionRatios', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    return scalar

def IfcFirstProjAxis(zaxis, arg):
    if not exists(zaxis):
        return None
    else:
        z = IfcNormalise(zaxis)
        if not exists(arg):
            if getattr(z, 'DirectionRatios', INDETERMINATE) != [1.0, 0.0, 0.0]:
                v = IfcDirection(DirectionRatios=[1.0, 0.0, 0.0])
            else:
                v = IfcDirection(DirectionRatios=[0.0, 1.0, 0.0])
        else:
            if getattr(arg, 'Dim', INDETERMINATE) != 3:
                return None
            if getattr(IfcCrossProduct(arg, z), 'Magnitude', INDETERMINATE) == 0.0:
                return None
            else:
                v = IfcNormalise(arg)
        xvec = IfcScalarTimesVector(IfcDotProduct(v, z), z)
        xaxis = getattr(IfcVectorDifference(v, xvec), 'Orientation', INDETERMINATE)
        xaxis = IfcNormalise(xaxis)
    return xaxis

def IfcGetBasisSurface(c):
    surfs = []
    if 'ifc4x1.ifcpcurve' in typeof(c):
        surfs = [getattr(c, 'BasisSurface', INDETERMINATE)]
    elif 'ifc4x1.ifcsurfacecurve' in typeof(c):
        n = sizeof(getattr(c, 'AssociatedGeometry', INDETERMINATE))
        for i in range(1, n + 1):
            surfs = surfs + IfcAssociatedSurface(express_getitem(getattr(c, 'AssociatedGeometry', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))
    if 'ifc4x1.ifccompositecurveonsurface' in typeof(c):
        n = sizeof(getattr(c, 'Segments', INDETERMINATE))
        surfs = IfcGetBasisSurface(getattr(express_getitem(getattr(c, 'Segments', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'ParentCurve', INDETERMINATE))
        if n > 1:
            for i in range(2, n + 1):
                surfs = surfs * IfcGetBasisSurface(getattr(express_getitem(getattr(c, 'Segments', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'ParentCurve', INDETERMINATE))
    return surfs

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
    n = sizeof(getattr(aloop, 'EdgeList', INDETERMINATE))
    for i in range(2, n + 1):
        p = p and getattr(express_getitem(getattr(aloop, 'EdgeList', INDETERMINATE), i - 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'EdgeEnd', INDETERMINATE) == getattr(express_getitem(getattr(aloop, 'EdgeList', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'EdgeStart', INDETERMINATE)
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
    max = getattr(express_getitem(getattr(layerset, 'MaterialLayers', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'LayerThickness', INDETERMINATE)
    if sizeof(getattr(layerset, 'MaterialLayers', INDETERMINATE)) > 1:
        for i in range(2, hiindex(getattr(layerset, 'MaterialLayers', INDETERMINATE)) + 1):
            max = max + getattr(express_getitem(getattr(layerset, 'MaterialLayers', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'LayerThickness', INDETERMINATE)
    return max

def IfcNormalise(arg):
    v = IfcDirection(DirectionRatios=[1.0, 0.0])
    vec = IfcVector(Orientation=IfcDirection(DirectionRatios=[1.0, 0.0]), Magnitude=1.0)
    result = v
    if not exists(arg):
        return None
    else:
        if 'ifc4x1.ifcvector' in typeof(arg):
            ndim = getattr(arg, 'Dim', INDETERMINATE)
            v.DirectionRatios = getattr(getattr(arg, 'Orientation', INDETERMINATE), 'DirectionRatios', INDETERMINATE)
            vec.Magnitude = getattr(arg, 'Magnitude', INDETERMINATE)
            vec.Orientation = v
            if getattr(arg, 'Magnitude', INDETERMINATE) == 0.0:
                return None
            else:
                vec.Magnitude = 1.0
        else:
            ndim = getattr(arg, 'Dim', INDETERMINATE)
            v.DirectionRatios = getattr(arg, 'DirectionRatios', INDETERMINATE)
        mag = 0.0
        for i in range(1, ndim + 1):
            mag = mag + express_getitem(getattr(v, 'DirectionRatios', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) * express_getitem(getattr(v, 'DirectionRatios', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
        if mag > 0.0:
            mag = sqrt(mag)
            for i in range(1, ndim + 1):
                temp = list(getattr(v, 'DirectionRatios', INDETERMINATE))
                temp[i - EXPRESS_ONE_BASED_INDEXING] = express_getitem(getattr(v, 'DirectionRatios', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) / mag
                v.DirectionRatios = temp
            if 'ifc4x1.ifcvector' in typeof(arg):
                vec.Orientation = v
                result = vec
            else:
                result = v
        else:
            return None
    return result

def IfcOrthogonalComplement(vec):
    if not exists(vec) or getattr(vec, 'Dim', INDETERMINATE) != 2:
        return None
    else:
        result = IfcDirection(DirectionRatios=[-express_getitem(getattr(vec, 'DirectionRatios', INDETERMINATE), 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), express_getitem(getattr(vec, 'DirectionRatios', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)])
        return result

def IfcPathHeadToTail(apath):
    n = 0
    p = unknown
    n = sizeof(getattr(apath, 'EdgeList', INDETERMINATE))
    for i in range(2, n + 1):
        p = p and getattr(express_getitem(getattr(apath, 'EdgeList', INDETERMINATE), i - 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'EdgeEnd', INDETERMINATE) == getattr(express_getitem(getattr(apath, 'EdgeList', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'EdgeStart', INDETERMINATE)
    return p

def IfcPointListDim(pointlist):
    if 'ifc4x1.ifccartesianpointlist2d' in typeof(pointlist):
        return 2
    if 'ifc4x1.ifccartesianpointlist3d' in typeof(pointlist):
        return 3
    return None

def IfcSameAxis2Placement(ap1, ap2, epsilon):
    return IfcSameDirection(express_getitem(getattr(ap1, 'P', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), express_getitem(getattr(ap2, 'P', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), epsilon) and IfcSameDirection(express_getitem(getattr(ap1, 'P', INDETERMINATE), 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), express_getitem(getattr(ap2, 'P', INDETERMINATE), 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), epsilon) and IfcSameCartesianPoint(getattr(ap1, 'Location', INDETERMINATE), getattr(ap1, 'Location', INDETERMINATE), epsilon)

def IfcSameCartesianPoint(cp1, cp2, epsilon):
    cp1x = express_getitem(getattr(cp1, 'Coordinates', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    cp1y = express_getitem(getattr(cp1, 'Coordinates', INDETERMINATE), 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    cp1z = 0
    cp2x = express_getitem(getattr(cp2, 'Coordinates', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    cp2y = express_getitem(getattr(cp2, 'Coordinates', INDETERMINATE), 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    cp2z = 0
    if sizeof(getattr(cp1, 'Coordinates', INDETERMINATE)) > 2:
        cp1z = express_getitem(getattr(cp1, 'Coordinates', INDETERMINATE), 3 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    if sizeof(getattr(cp2, 'Coordinates', INDETERMINATE)) > 2:
        cp2z = express_getitem(getattr(cp2, 'Coordinates', INDETERMINATE), 3 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    return IfcSameValue(cp1x, cp2x, epsilon) and IfcSameValue(cp1y, cp2y, epsilon) and IfcSameValue(cp1z, cp2z, epsilon)

def IfcSameDirection(dir1, dir2, epsilon):
    dir1x = express_getitem(getattr(dir1, 'DirectionRatios', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    dir1y = express_getitem(getattr(dir1, 'DirectionRatios', INDETERMINATE), 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    dir1z = 0
    dir2x = express_getitem(getattr(dir2, 'DirectionRatios', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    dir2y = express_getitem(getattr(dir2, 'DirectionRatios', INDETERMINATE), 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    dir2z = 0
    if sizeof(getattr(dir1, 'DirectionRatios', INDETERMINATE)) > 2:
        dir1z = express_getitem(getattr(dir1, 'DirectionRatios', INDETERMINATE), 3 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    if sizeof(getattr(dir2, 'DirectionRatios', INDETERMINATE)) > 2:
        dir2z = express_getitem(getattr(dir2, 'DirectionRatios', INDETERMINATE), 3 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
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
        if 'ifc4x1.ifcvector' in typeof(vec):
            v = getattr(vec, 'Orientation', INDETERMINATE)
            mag = scalar * getattr(vec, 'Magnitude', INDETERMINATE)
        else:
            v = vec
            mag = scalar
        if mag < 0.0:
            for i in range(1, sizeof(getattr(v, 'DirectionRatios', INDETERMINATE)) + 1):
                temp = list(getattr(v, 'DirectionRatios', INDETERMINATE))
                temp[i - EXPRESS_ONE_BASED_INDEXING] = -express_getitem(getattr(v, 'DirectionRatios', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
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
    return getattr(yaxis, 'Orientation', INDETERMINATE)

def IfcShapeRepresentationTypes(reptype, items):
    count = 0
    if getattr(reptype, 'lower', INDETERMINATE)() == 'point':
        count = sizeof([temp for temp in items if 'ifc4x1.ifcpoint' in typeof(temp)])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'pointcloud':
        count = sizeof([temp for temp in items if 'ifc4x1.ifccartesianpointlist3d' in typeof(temp)])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'curve':
        count = sizeof([temp for temp in items if 'ifc4x1.ifccurve' in typeof(temp)])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'curve2d':
        count = sizeof([temp for temp in items if 'ifc4x1.ifccurve' in typeof(temp) and getattr(temp, 'Dim', INDETERMINATE) == 2])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'curve3d':
        count = sizeof([temp for temp in items if 'ifc4x1.ifccurve' in typeof(temp) and getattr(temp, 'Dim', INDETERMINATE) == 3])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'surface':
        count = sizeof([temp for temp in items if 'ifc4x1.ifcsurface' in typeof(temp)])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'surface2d':
        count = sizeof([temp for temp in items if 'ifc4x1.ifcsurface' in typeof(temp) and getattr(temp, 'Dim', INDETERMINATE) == 2])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'surface3d':
        count = sizeof([temp for temp in items if 'ifc4x1.ifcsurface' in typeof(temp) and getattr(temp, 'Dim', INDETERMINATE) == 3])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'fillarea':
        count = sizeof([temp for temp in items if 'ifc4x1.ifcannotationfillarea' in typeof(temp)])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'text':
        count = sizeof([temp for temp in items if 'ifc4x1.ifctextliteral' in typeof(temp)])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'advancedsurface':
        count = sizeof([temp for temp in items if 'ifc4x1.ifcbsplinesurface' in typeof(temp)])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'annotation2d':
        count = sizeof([temp for temp in items if sizeof(typeof(temp) * ['ifc4x1.ifcpoint', 'ifc4x1.ifccurve', 'ifc4x1.ifcgeometriccurveset', 'ifc4x1.ifcannotationfillarea', 'ifc4x1.ifctextliteral']) == 1])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'geometricset':
        count = sizeof([temp for temp in items if 'ifc4x1.ifcgeometricset' in typeof(temp) or 'ifc4x1.ifcpoint' in typeof(temp) or 'ifc4x1.ifccurve' in typeof(temp) or ('ifc4x1.ifcsurface' in typeof(temp))])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'geometriccurveset':
        count = sizeof([temp for temp in items if 'ifc4x1.ifcgeometriccurveset' in typeof(temp) or 'ifc4x1.ifcgeometricset' in typeof(temp) or 'ifc4x1.ifcpoint' in typeof(temp) or ('ifc4x1.ifccurve' in typeof(temp))])
        for i in range(1, hiindex(items) + 1):
            if 'ifc4x1.ifcgeometricset' in typeof(express_getitem(items, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)):
                if sizeof([temp for temp in getattr(express_getitem(items, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Elements', INDETERMINATE) if 'ifc4x1.ifcsurface' in typeof(temp)]) > 0:
                    count = count - 1
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'tessellation':
        count = sizeof([temp for temp in items if 'ifc4x1.ifctessellateditem' in typeof(temp)])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'surfaceorsolidmodel':
        count = sizeof([temp for temp in items if sizeof(['ifc4x1.ifctessellateditem', 'ifc4x1.ifcshellbasedsurfacemodel', 'ifc4x1.ifcfacebasedsurfacemodel', 'ifc4x1.ifcsolidmodel'] * typeof(temp)) >= 1])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'surfacemodel':
        count = sizeof([temp for temp in items if sizeof(['ifc4x1.ifctessellateditem', 'ifc4x1.ifcshellbasedsurfacemodel', 'ifc4x1.ifcfacebasedsurfacemodel'] * typeof(temp)) >= 1])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'solidmodel':
        count = sizeof([temp for temp in items if 'ifc4x1.ifcsolidmodel' in typeof(temp)])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'sweptsolid':
        count = sizeof([temp for temp in items if sizeof(['ifc4x1.ifcextrudedareasolid', 'ifc4x1.ifcrevolvedareasolid'] * typeof(temp)) >= 1 and sizeof(['ifc4x1.ifcextrudedareasolidtapered', 'ifc4x1.ifcrevolvedareasolidtapered'] * typeof(temp)) == 0])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'advancedsweptsolid':
        count = sizeof([temp for temp in items if sizeof(['ifc4x1.ifcsweptareasolid', 'ifc4x1.ifcsweptdisksolid'] * typeof(temp)) >= 1])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'csg':
        count = sizeof([temp for temp in items if sizeof(['ifc4x1.ifcbooleanresult', 'ifc4x1.ifccsgprimitive3d', 'ifc4x1.ifccsgsolid'] * typeof(temp)) >= 1])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'clipping':
        count = sizeof([temp for temp in items if sizeof(['ifc4x1.ifccsgsolid', 'ifc4x1.ifcbooleanclippingresult'] * typeof(temp)) >= 1])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'brep':
        count = sizeof([temp for temp in items if 'ifc4x1.ifcfacetedbrep' in typeof(temp)])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'advancedbrep':
        count = sizeof([temp for temp in items if 'ifc4x1.ifcmanifoldsolidbrep' in typeof(temp)])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'boundingbox':
        count = sizeof([temp for temp in items if 'ifc4x1.ifcboundingbox' in typeof(temp)])
        if sizeof(items) > 1:
            count = 0
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'sectionedspine':
        count = sizeof([temp for temp in items if 'ifc4x1.ifcsectionedspine' in typeof(temp)])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'lightsource':
        count = sizeof([temp for temp in items if 'ifc4x1.ifclightsource' in typeof(temp)])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'mappedrepresentation':
        count = sizeof([temp for temp in items if 'ifc4x1.ifcmappeditem' in typeof(temp)])
    else:
        return None
    return count == sizeof(items)

def IfcSurfaceWeightsPositive(b):
    result = True
    weights = getattr(b, 'Weights', INDETERMINATE)
    for i in range(0, getattr(b, 'UUpper', INDETERMINATE) + 1):
        for j in range(0, getattr(b, 'VUpper', INDETERMINATE) + 1):
            if express_getitem(express_getitem(weights, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), j - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) <= 0.0:
                result = False
                return result
    return result

def IfcTaperedSweptAreaProfiles(startarea, endarea):
    result = False
    if 'ifc4x1.ifcparameterizedprofiledef' in typeof(startarea):
        if 'ifc4x1.ifcderivedprofiledef' in typeof(endarea):
            result = startarea == getattr(endarea, 'ParentProfile', INDETERMINATE)
        else:
            result = typeof(startarea) == typeof(endarea)
    elif 'ifc4x1.ifcderivedprofiledef' in typeof(endarea):
        result = startarea == getattr(endarea, 'ParentProfile', INDETERMINATE)
    else:
        result = False
    return result

def IfcTopologyRepresentationTypes(reptype, items):
    count = 0
    if getattr(reptype, 'lower', INDETERMINATE)() == 'vertex':
        count = sizeof([temp for temp in items if 'ifc4x1.ifcvertex' in typeof(temp)])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'edge':
        count = sizeof([temp for temp in items if 'ifc4x1.ifcedge' in typeof(temp)])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'path':
        count = sizeof([temp for temp in items if 'ifc4x1.ifcpath' in typeof(temp)])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'face':
        count = sizeof([temp for temp in items if 'ifc4x1.ifcface' in typeof(temp)])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'shell':
        count = sizeof([temp for temp in items if 'ifc4x1.ifcopenshell' in typeof(temp) or 'ifc4x1.ifcclosedshell' in typeof(temp)])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'undefined':
        return True
    else:
        return None
    return count == sizeof(items)

def IfcUniqueDefinitionNames(relations):
    properties = express_set([])
    if sizeof(relations) == 0:
        return True
    for i in range(1, hiindex(relations) + 1):
        definition = getattr(express_getitem(relations, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingPropertyDefinition', INDETERMINATE)
        if 'ifc4x1.ifcpropertysetdefinition' in typeof(definition):
            properties = properties + definition
        elif 'ifc4x1.ifcpropertysetdefinitionset' in typeof(definition):
            definitionset = definition
            for j in range(1, hiindex(definitionset) + 1):
                properties = properties + express_getitem(definitionset, j - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
    result = IfcUniquePropertySetNames(properties)
    return result

def IfcUniquePropertyName(properties):
    names = express_set([])
    for i in range(1, hiindex(properties) + 1):
        names = names + getattr(express_getitem(properties, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Name', INDETERMINATE)
    return sizeof(names) == sizeof(properties)

def IfcUniquePropertySetNames(properties):
    names = express_set([])
    unnamed = 0
    for i in range(1, hiindex(properties) + 1):
        if 'ifc4x1.ifcpropertyset' in typeof(express_getitem(properties, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)):
            names = names + getattr(express_getitem(properties, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Name', INDETERMINATE)
        else:
            unnamed = unnamed + 1
    return sizeof(names) + unnamed == sizeof(properties)

def IfcUniquePropertyTemplateNames(properties):
    names = express_set([])
    for i in range(1, hiindex(properties) + 1):
        names = names + getattr(express_getitem(properties, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Name', INDETERMINATE)
    return sizeof(names) == sizeof(properties)

def IfcUniqueQuantityNames(properties):
    names = express_set([])
    for i in range(1, hiindex(properties) + 1):
        names = names + getattr(express_getitem(properties, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Name', INDETERMINATE)
    return sizeof(names) == sizeof(properties)

def IfcVectorDifference(arg1, arg2):
    if (not exists(arg1) or not exists(arg2)) or getattr(arg1, 'Dim', INDETERMINATE) != getattr(arg2, 'Dim', INDETERMINATE):
        return None
    else:
        if 'ifc4x1.ifcvector' in typeof(arg1):
            mag1 = getattr(arg1, 'Magnitude', INDETERMINATE)
            vec1 = getattr(arg1, 'Orientation', INDETERMINATE)
        else:
            mag1 = 1.0
            vec1 = arg1
        if 'ifc4x1.ifcvector' in typeof(arg2):
            mag2 = getattr(arg2, 'Magnitude', INDETERMINATE)
            vec2 = getattr(arg2, 'Orientation', INDETERMINATE)
        else:
            mag2 = 1.0
            vec2 = arg2
        vec1 = IfcNormalise(vec1)
        vec2 = IfcNormalise(vec2)
        ndim = sizeof(getattr(vec1, 'DirectionRatios', INDETERMINATE))
        mag = 0.0
        res = IfcDirection(DirectionRatios=[0.0] * ndim)
        for i in range(1, ndim + 1):
            temp = list(getattr(res, 'DirectionRatios', INDETERMINATE))
            temp[i - EXPRESS_ONE_BASED_INDEXING] = mag1 * express_getitem(getattr(vec1, 'DirectionRatios', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) - mag2 * express_getitem(getattr(vec2, 'DirectionRatios', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
            res.DirectionRatios = temp
            mag = mag + express_getitem(getattr(res, 'DirectionRatios', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) * express_getitem(getattr(res, 'DirectionRatios', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
        if mag > 0.0:
            result = IfcVector(Orientation=res, Magnitude=sqrt(mag))
        else:
            result = IfcVector(Orientation=vec1, Magnitude=0.0)
    return result

def IfcVectorSum(arg1, arg2):
    if (not exists(arg1) or not exists(arg2)) or getattr(arg1, 'Dim', INDETERMINATE) != getattr(arg2, 'Dim', INDETERMINATE):
        return None
    else:
        if 'ifc4x1.ifcvector' in typeof(arg1):
            mag1 = getattr(arg1, 'Magnitude', INDETERMINATE)
            vec1 = getattr(arg1, 'Orientation', INDETERMINATE)
        else:
            mag1 = 1.0
            vec1 = arg1
        if 'ifc4x1.ifcvector' in typeof(arg2):
            mag2 = getattr(arg2, 'Magnitude', INDETERMINATE)
            vec2 = getattr(arg2, 'Orientation', INDETERMINATE)
        else:
            mag2 = 1.0
            vec2 = arg2
        vec1 = IfcNormalise(vec1)
        vec2 = IfcNormalise(vec2)
        ndim = sizeof(getattr(vec1, 'DirectionRatios', INDETERMINATE))
        mag = 0.0
        res = IfcDirection(DirectionRatios=[0.0] * ndim)
        for i in range(1, ndim + 1):
            temp = list(getattr(res, 'DirectionRatios', INDETERMINATE))
            temp[i - EXPRESS_ONE_BASED_INDEXING] = mag1 * express_getitem(getattr(vec1, 'DirectionRatios', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) + mag2 * express_getitem(getattr(vec2, 'DirectionRatios', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
            res.DirectionRatios = temp
            mag = mag + express_getitem(getattr(res, 'DirectionRatios', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) * express_getitem(getattr(res, 'DirectionRatios', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
        if mag > 0.0:
            result = IfcVector(Orientation=res, Magnitude=sqrt(mag))
        else:
            result = IfcVector(Orientation=vec1, Magnitude=0.0)
    return result