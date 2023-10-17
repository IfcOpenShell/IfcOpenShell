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
IfcAheadOrBehind = enum_namespace()
ahead = getattr(IfcAheadOrBehind, 'AHEAD', INDETERMINATE)
behind = getattr(IfcAheadOrBehind, 'BEHIND', INDETERMINATE)
IfcAirTerminalBoxTypeEnum = enum_namespace()
constantflow = getattr(IfcAirTerminalBoxTypeEnum, 'CONSTANTFLOW', INDETERMINATE)
variableflowpressuredependant = getattr(IfcAirTerminalBoxTypeEnum, 'VARIABLEFLOWPRESSUREDEPENDANT', INDETERMINATE)
variableflowpressureindependant = getattr(IfcAirTerminalBoxTypeEnum, 'VARIABLEFLOWPRESSUREINDEPENDANT', INDETERMINATE)
userdefined = getattr(IfcAirTerminalBoxTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcAirTerminalBoxTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcAirTerminalTypeEnum = enum_namespace()
grille = getattr(IfcAirTerminalTypeEnum, 'GRILLE', INDETERMINATE)
register = getattr(IfcAirTerminalTypeEnum, 'REGISTER', INDETERMINATE)
diffuser = getattr(IfcAirTerminalTypeEnum, 'DIFFUSER', INDETERMINATE)
eyeball = getattr(IfcAirTerminalTypeEnum, 'EYEBALL', INDETERMINATE)
iris = getattr(IfcAirTerminalTypeEnum, 'IRIS', INDETERMINATE)
lineargrille = getattr(IfcAirTerminalTypeEnum, 'LINEARGRILLE', INDETERMINATE)
lineardiffuser = getattr(IfcAirTerminalTypeEnum, 'LINEARDIFFUSER', INDETERMINATE)
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
IfcBSplineCurveForm = enum_namespace()
polyline_form = getattr(IfcBSplineCurveForm, 'POLYLINE_FORM', INDETERMINATE)
circular_arc = getattr(IfcBSplineCurveForm, 'CIRCULAR_ARC', INDETERMINATE)
elliptic_arc = getattr(IfcBSplineCurveForm, 'ELLIPTIC_ARC', INDETERMINATE)
parabolic_arc = getattr(IfcBSplineCurveForm, 'PARABOLIC_ARC', INDETERMINATE)
hyperbolic_arc = getattr(IfcBSplineCurveForm, 'HYPERBOLIC_ARC', INDETERMINATE)
unspecified = getattr(IfcBSplineCurveForm, 'UNSPECIFIED', INDETERMINATE)
IfcBeamTypeEnum = enum_namespace()
beam = getattr(IfcBeamTypeEnum, 'BEAM', INDETERMINATE)
joist = getattr(IfcBeamTypeEnum, 'JOIST', INDETERMINATE)
lintel = getattr(IfcBeamTypeEnum, 'LINTEL', INDETERMINATE)
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
IfcBoilerTypeEnum = enum_namespace()
water = getattr(IfcBoilerTypeEnum, 'WATER', INDETERMINATE)
steam = getattr(IfcBoilerTypeEnum, 'STEAM', INDETERMINATE)
userdefined = getattr(IfcBoilerTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcBoilerTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcBooleanOperator = enum_namespace()
union = getattr(IfcBooleanOperator, 'UNION', INDETERMINATE)
intersection = getattr(IfcBooleanOperator, 'INTERSECTION', INDETERMINATE)
difference = getattr(IfcBooleanOperator, 'DIFFERENCE', INDETERMINATE)
IfcBuildingElementProxyTypeEnum = enum_namespace()
userdefined = getattr(IfcBuildingElementProxyTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcBuildingElementProxyTypeEnum, 'NOTDEFINED', INDETERMINATE)
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
IfcCableSegmentTypeEnum = enum_namespace()
cablesegment = getattr(IfcCableSegmentTypeEnum, 'CABLESEGMENT', INDETERMINATE)
conductorsegment = getattr(IfcCableSegmentTypeEnum, 'CONDUCTORSEGMENT', INDETERMINATE)
userdefined = getattr(IfcCableSegmentTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcCableSegmentTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcChangeActionEnum = enum_namespace()
nochange = getattr(IfcChangeActionEnum, 'NOCHANGE', INDETERMINATE)
modified = getattr(IfcChangeActionEnum, 'MODIFIED', INDETERMINATE)
added = getattr(IfcChangeActionEnum, 'ADDED', INDETERMINATE)
deleted = getattr(IfcChangeActionEnum, 'DELETED', INDETERMINATE)
modifiedadded = getattr(IfcChangeActionEnum, 'MODIFIEDADDED', INDETERMINATE)
modifieddeleted = getattr(IfcChangeActionEnum, 'MODIFIEDDELETED', INDETERMINATE)
IfcChillerTypeEnum = enum_namespace()
aircooled = getattr(IfcChillerTypeEnum, 'AIRCOOLED', INDETERMINATE)
watercooled = getattr(IfcChillerTypeEnum, 'WATERCOOLED', INDETERMINATE)
heatrecovery = getattr(IfcChillerTypeEnum, 'HEATRECOVERY', INDETERMINATE)
userdefined = getattr(IfcChillerTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcChillerTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCoilTypeEnum = enum_namespace()
dxcoolingcoil = getattr(IfcCoilTypeEnum, 'DXCOOLINGCOIL', INDETERMINATE)
watercoolingcoil = getattr(IfcCoilTypeEnum, 'WATERCOOLINGCOIL', INDETERMINATE)
steamheatingcoil = getattr(IfcCoilTypeEnum, 'STEAMHEATINGCOIL', INDETERMINATE)
waterheatingcoil = getattr(IfcCoilTypeEnum, 'WATERHEATINGCOIL', INDETERMINATE)
electricheatingcoil = getattr(IfcCoilTypeEnum, 'ELECTRICHEATINGCOIL', INDETERMINATE)
gasheatingcoil = getattr(IfcCoilTypeEnum, 'GASHEATINGCOIL', INDETERMINATE)
userdefined = getattr(IfcCoilTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcCoilTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcColumnTypeEnum = enum_namespace()
column = getattr(IfcColumnTypeEnum, 'COLUMN', INDETERMINATE)
userdefined = getattr(IfcColumnTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcColumnTypeEnum, 'NOTDEFINED', INDETERMINATE)
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
watercooledshelltube = getattr(IfcCondenserTypeEnum, 'WATERCOOLEDSHELLTUBE', INDETERMINATE)
watercooledshellcoil = getattr(IfcCondenserTypeEnum, 'WATERCOOLEDSHELLCOIL', INDETERMINATE)
watercooledtubeintube = getattr(IfcCondenserTypeEnum, 'WATERCOOLEDTUBEINTUBE', INDETERMINATE)
watercooledbrazedplate = getattr(IfcCondenserTypeEnum, 'WATERCOOLEDBRAZEDPLATE', INDETERMINATE)
aircooled = getattr(IfcCondenserTypeEnum, 'AIRCOOLED', INDETERMINATE)
evaporativecooled = getattr(IfcCondenserTypeEnum, 'EVAPORATIVECOOLED', INDETERMINATE)
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
IfcControllerTypeEnum = enum_namespace()
floating = getattr(IfcControllerTypeEnum, 'FLOATING', INDETERMINATE)
proportional = getattr(IfcControllerTypeEnum, 'PROPORTIONAL', INDETERMINATE)
proportionalintegral = getattr(IfcControllerTypeEnum, 'PROPORTIONALINTEGRAL', INDETERMINATE)
proportionalintegralderivative = getattr(IfcControllerTypeEnum, 'PROPORTIONALINTEGRALDERIVATIVE', INDETERMINATE)
timedtwoposition = getattr(IfcControllerTypeEnum, 'TIMEDTWOPOSITION', INDETERMINATE)
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
insulation = getattr(IfcCoveringTypeEnum, 'INSULATION', INDETERMINATE)
membrane = getattr(IfcCoveringTypeEnum, 'MEMBRANE', INDETERMINATE)
sleeving = getattr(IfcCoveringTypeEnum, 'SLEEVING', INDETERMINATE)
wrapping = getattr(IfcCoveringTypeEnum, 'WRAPPING', INDETERMINATE)
userdefined = getattr(IfcCoveringTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcCoveringTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcCurrencyEnum = enum_namespace()
aed = getattr(IfcCurrencyEnum, 'AED', INDETERMINATE)
aes = getattr(IfcCurrencyEnum, 'AES', INDETERMINATE)
ats = getattr(IfcCurrencyEnum, 'ATS', INDETERMINATE)
aud = getattr(IfcCurrencyEnum, 'AUD', INDETERMINATE)
bbd = getattr(IfcCurrencyEnum, 'BBD', INDETERMINATE)
beg = getattr(IfcCurrencyEnum, 'BEG', INDETERMINATE)
bgl = getattr(IfcCurrencyEnum, 'BGL', INDETERMINATE)
bhd = getattr(IfcCurrencyEnum, 'BHD', INDETERMINATE)
bmd = getattr(IfcCurrencyEnum, 'BMD', INDETERMINATE)
bnd = getattr(IfcCurrencyEnum, 'BND', INDETERMINATE)
brl = getattr(IfcCurrencyEnum, 'BRL', INDETERMINATE)
bsd = getattr(IfcCurrencyEnum, 'BSD', INDETERMINATE)
bwp = getattr(IfcCurrencyEnum, 'BWP', INDETERMINATE)
bzd = getattr(IfcCurrencyEnum, 'BZD', INDETERMINATE)
cad = getattr(IfcCurrencyEnum, 'CAD', INDETERMINATE)
cbd = getattr(IfcCurrencyEnum, 'CBD', INDETERMINATE)
chf = getattr(IfcCurrencyEnum, 'CHF', INDETERMINATE)
clp = getattr(IfcCurrencyEnum, 'CLP', INDETERMINATE)
cny = getattr(IfcCurrencyEnum, 'CNY', INDETERMINATE)
cys = getattr(IfcCurrencyEnum, 'CYS', INDETERMINATE)
czk = getattr(IfcCurrencyEnum, 'CZK', INDETERMINATE)
ddp = getattr(IfcCurrencyEnum, 'DDP', INDETERMINATE)
dem = getattr(IfcCurrencyEnum, 'DEM', INDETERMINATE)
dkk = getattr(IfcCurrencyEnum, 'DKK', INDETERMINATE)
egl = getattr(IfcCurrencyEnum, 'EGL', INDETERMINATE)
est = getattr(IfcCurrencyEnum, 'EST', INDETERMINATE)
eur = getattr(IfcCurrencyEnum, 'EUR', INDETERMINATE)
fak = getattr(IfcCurrencyEnum, 'FAK', INDETERMINATE)
fim = getattr(IfcCurrencyEnum, 'FIM', INDETERMINATE)
fjd = getattr(IfcCurrencyEnum, 'FJD', INDETERMINATE)
fkp = getattr(IfcCurrencyEnum, 'FKP', INDETERMINATE)
frf = getattr(IfcCurrencyEnum, 'FRF', INDETERMINATE)
gbp = getattr(IfcCurrencyEnum, 'GBP', INDETERMINATE)
gip = getattr(IfcCurrencyEnum, 'GIP', INDETERMINATE)
gmd = getattr(IfcCurrencyEnum, 'GMD', INDETERMINATE)
grx = getattr(IfcCurrencyEnum, 'GRX', INDETERMINATE)
hkd = getattr(IfcCurrencyEnum, 'HKD', INDETERMINATE)
huf = getattr(IfcCurrencyEnum, 'HUF', INDETERMINATE)
ick = getattr(IfcCurrencyEnum, 'ICK', INDETERMINATE)
idr = getattr(IfcCurrencyEnum, 'IDR', INDETERMINATE)
ils = getattr(IfcCurrencyEnum, 'ILS', INDETERMINATE)
inr = getattr(IfcCurrencyEnum, 'INR', INDETERMINATE)
irp = getattr(IfcCurrencyEnum, 'IRP', INDETERMINATE)
itl = getattr(IfcCurrencyEnum, 'ITL', INDETERMINATE)
jmd = getattr(IfcCurrencyEnum, 'JMD', INDETERMINATE)
jod = getattr(IfcCurrencyEnum, 'JOD', INDETERMINATE)
jpy = getattr(IfcCurrencyEnum, 'JPY', INDETERMINATE)
kes = getattr(IfcCurrencyEnum, 'KES', INDETERMINATE)
krw = getattr(IfcCurrencyEnum, 'KRW', INDETERMINATE)
kwd = getattr(IfcCurrencyEnum, 'KWD', INDETERMINATE)
kyd = getattr(IfcCurrencyEnum, 'KYD', INDETERMINATE)
lkr = getattr(IfcCurrencyEnum, 'LKR', INDETERMINATE)
luf = getattr(IfcCurrencyEnum, 'LUF', INDETERMINATE)
mtl = getattr(IfcCurrencyEnum, 'MTL', INDETERMINATE)
mur = getattr(IfcCurrencyEnum, 'MUR', INDETERMINATE)
mxn = getattr(IfcCurrencyEnum, 'MXN', INDETERMINATE)
myr = getattr(IfcCurrencyEnum, 'MYR', INDETERMINATE)
nlg = getattr(IfcCurrencyEnum, 'NLG', INDETERMINATE)
nzd = getattr(IfcCurrencyEnum, 'NZD', INDETERMINATE)
omr = getattr(IfcCurrencyEnum, 'OMR', INDETERMINATE)
pgk = getattr(IfcCurrencyEnum, 'PGK', INDETERMINATE)
php = getattr(IfcCurrencyEnum, 'PHP', INDETERMINATE)
pkr = getattr(IfcCurrencyEnum, 'PKR', INDETERMINATE)
pln = getattr(IfcCurrencyEnum, 'PLN', INDETERMINATE)
ptn = getattr(IfcCurrencyEnum, 'PTN', INDETERMINATE)
qar = getattr(IfcCurrencyEnum, 'QAR', INDETERMINATE)
rur = getattr(IfcCurrencyEnum, 'RUR', INDETERMINATE)
sar = getattr(IfcCurrencyEnum, 'SAR', INDETERMINATE)
scr = getattr(IfcCurrencyEnum, 'SCR', INDETERMINATE)
sek = getattr(IfcCurrencyEnum, 'SEK', INDETERMINATE)
sgd = getattr(IfcCurrencyEnum, 'SGD', INDETERMINATE)
skp = getattr(IfcCurrencyEnum, 'SKP', INDETERMINATE)
thb = getattr(IfcCurrencyEnum, 'THB', INDETERMINATE)
trl = getattr(IfcCurrencyEnum, 'TRL', INDETERMINATE)
ttd = getattr(IfcCurrencyEnum, 'TTD', INDETERMINATE)
twd = getattr(IfcCurrencyEnum, 'TWD', INDETERMINATE)
usd = getattr(IfcCurrencyEnum, 'USD', INDETERMINATE)
veb = getattr(IfcCurrencyEnum, 'VEB', INDETERMINATE)
vnd = getattr(IfcCurrencyEnum, 'VND', INDETERMINATE)
xeu = getattr(IfcCurrencyEnum, 'XEU', INDETERMINATE)
zar = getattr(IfcCurrencyEnum, 'ZAR', INDETERMINATE)
zwd = getattr(IfcCurrencyEnum, 'ZWD', INDETERMINATE)
nok = getattr(IfcCurrencyEnum, 'NOK', INDETERMINATE)
IfcCurtainWallTypeEnum = enum_namespace()
userdefined = getattr(IfcCurtainWallTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcCurtainWallTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcDamperTypeEnum = enum_namespace()
controldamper = getattr(IfcDamperTypeEnum, 'CONTROLDAMPER', INDETERMINATE)
firedamper = getattr(IfcDamperTypeEnum, 'FIREDAMPER', INDETERMINATE)
smokedamper = getattr(IfcDamperTypeEnum, 'SMOKEDAMPER', INDETERMINATE)
firesmokedamper = getattr(IfcDamperTypeEnum, 'FIRESMOKEDAMPER', INDETERMINATE)
backdraftdamper = getattr(IfcDamperTypeEnum, 'BACKDRAFTDAMPER', INDETERMINATE)
reliefdamper = getattr(IfcDamperTypeEnum, 'RELIEFDAMPER', INDETERMINATE)
blastdamper = getattr(IfcDamperTypeEnum, 'BLASTDAMPER', INDETERMINATE)
gravitydamper = getattr(IfcDamperTypeEnum, 'GRAVITYDAMPER', INDETERMINATE)
gravityreliefdamper = getattr(IfcDamperTypeEnum, 'GRAVITYRELIEFDAMPER', INDETERMINATE)
balancingdamper = getattr(IfcDamperTypeEnum, 'BALANCINGDAMPER', INDETERMINATE)
fumehoodexhaust = getattr(IfcDamperTypeEnum, 'FUMEHOODEXHAUST', INDETERMINATE)
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
soundpowerunit = getattr(IfcDerivedUnitEnum, 'SOUNDPOWERUNIT', INDETERMINATE)
soundpressureunit = getattr(IfcDerivedUnitEnum, 'SOUNDPRESSUREUNIT', INDETERMINATE)
temperaturegradientunit = getattr(IfcDerivedUnitEnum, 'TEMPERATUREGRADIENTUNIT', INDETERMINATE)
thermalexpansioncoefficientunit = getattr(IfcDerivedUnitEnum, 'THERMALEXPANSIONCOEFFICIENTUNIT', INDETERMINATE)
warpingconstantunit = getattr(IfcDerivedUnitEnum, 'WARPINGCONSTANTUNIT', INDETERMINATE)
warpingmomentunit = getattr(IfcDerivedUnitEnum, 'WARPINGMOMENTUNIT', INDETERMINATE)
userdefined = getattr(IfcDerivedUnitEnum, 'USERDEFINED', INDETERMINATE)
IfcDimensionExtentUsage = enum_namespace()
origin = getattr(IfcDimensionExtentUsage, 'ORIGIN', INDETERMINATE)
target = getattr(IfcDimensionExtentUsage, 'TARGET', INDETERMINATE)
IfcDirectionSenseEnum = enum_namespace()
positive = getattr(IfcDirectionSenseEnum, 'POSITIVE', INDETERMINATE)
negative = getattr(IfcDirectionSenseEnum, 'NEGATIVE', INDETERMINATE)
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
computer = getattr(IfcElectricApplianceTypeEnum, 'COMPUTER', INDETERMINATE)
directwaterheater = getattr(IfcElectricApplianceTypeEnum, 'DIRECTWATERHEATER', INDETERMINATE)
dishwasher = getattr(IfcElectricApplianceTypeEnum, 'DISHWASHER', INDETERMINATE)
electriccooker = getattr(IfcElectricApplianceTypeEnum, 'ELECTRICCOOKER', INDETERMINATE)
electricheater = getattr(IfcElectricApplianceTypeEnum, 'ELECTRICHEATER', INDETERMINATE)
facsimile = getattr(IfcElectricApplianceTypeEnum, 'FACSIMILE', INDETERMINATE)
freestandingfan = getattr(IfcElectricApplianceTypeEnum, 'FREESTANDINGFAN', INDETERMINATE)
freezer = getattr(IfcElectricApplianceTypeEnum, 'FREEZER', INDETERMINATE)
fridge_freezer = getattr(IfcElectricApplianceTypeEnum, 'FRIDGE_FREEZER', INDETERMINATE)
handdryer = getattr(IfcElectricApplianceTypeEnum, 'HANDDRYER', INDETERMINATE)
indirectwaterheater = getattr(IfcElectricApplianceTypeEnum, 'INDIRECTWATERHEATER', INDETERMINATE)
microwave = getattr(IfcElectricApplianceTypeEnum, 'MICROWAVE', INDETERMINATE)
photocopier = getattr(IfcElectricApplianceTypeEnum, 'PHOTOCOPIER', INDETERMINATE)
printer = getattr(IfcElectricApplianceTypeEnum, 'PRINTER', INDETERMINATE)
refrigerator = getattr(IfcElectricApplianceTypeEnum, 'REFRIGERATOR', INDETERMINATE)
radiantheater = getattr(IfcElectricApplianceTypeEnum, 'RADIANTHEATER', INDETERMINATE)
scanner = getattr(IfcElectricApplianceTypeEnum, 'SCANNER', INDETERMINATE)
telephone = getattr(IfcElectricApplianceTypeEnum, 'TELEPHONE', INDETERMINATE)
tumbledryer = getattr(IfcElectricApplianceTypeEnum, 'TUMBLEDRYER', INDETERMINATE)
tv = getattr(IfcElectricApplianceTypeEnum, 'TV', INDETERMINATE)
vendingmachine = getattr(IfcElectricApplianceTypeEnum, 'VENDINGMACHINE', INDETERMINATE)
washingmachine = getattr(IfcElectricApplianceTypeEnum, 'WASHINGMACHINE', INDETERMINATE)
waterheater = getattr(IfcElectricApplianceTypeEnum, 'WATERHEATER', INDETERMINATE)
watercooler = getattr(IfcElectricApplianceTypeEnum, 'WATERCOOLER', INDETERMINATE)
userdefined = getattr(IfcElectricApplianceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcElectricApplianceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcElectricCurrentEnum = enum_namespace()
alternating = getattr(IfcElectricCurrentEnum, 'ALTERNATING', INDETERMINATE)
direct = getattr(IfcElectricCurrentEnum, 'DIRECT', INDETERMINATE)
notdefined = getattr(IfcElectricCurrentEnum, 'NOTDEFINED', INDETERMINATE)
IfcElectricDistributionPointFunctionEnum = enum_namespace()
alarmpanel = getattr(IfcElectricDistributionPointFunctionEnum, 'ALARMPANEL', INDETERMINATE)
consumerunit = getattr(IfcElectricDistributionPointFunctionEnum, 'CONSUMERUNIT', INDETERMINATE)
controlpanel = getattr(IfcElectricDistributionPointFunctionEnum, 'CONTROLPANEL', INDETERMINATE)
distributionboard = getattr(IfcElectricDistributionPointFunctionEnum, 'DISTRIBUTIONBOARD', INDETERMINATE)
gasdetectorpanel = getattr(IfcElectricDistributionPointFunctionEnum, 'GASDETECTORPANEL', INDETERMINATE)
indicatorpanel = getattr(IfcElectricDistributionPointFunctionEnum, 'INDICATORPANEL', INDETERMINATE)
mimicpanel = getattr(IfcElectricDistributionPointFunctionEnum, 'MIMICPANEL', INDETERMINATE)
motorcontrolcentre = getattr(IfcElectricDistributionPointFunctionEnum, 'MOTORCONTROLCENTRE', INDETERMINATE)
switchboard = getattr(IfcElectricDistributionPointFunctionEnum, 'SWITCHBOARD', INDETERMINATE)
userdefined = getattr(IfcElectricDistributionPointFunctionEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcElectricDistributionPointFunctionEnum, 'NOTDEFINED', INDETERMINATE)
IfcElectricFlowStorageDeviceTypeEnum = enum_namespace()
battery = getattr(IfcElectricFlowStorageDeviceTypeEnum, 'BATTERY', INDETERMINATE)
capacitorbank = getattr(IfcElectricFlowStorageDeviceTypeEnum, 'CAPACITORBANK', INDETERMINATE)
harmonicfilter = getattr(IfcElectricFlowStorageDeviceTypeEnum, 'HARMONICFILTER', INDETERMINATE)
inductorbank = getattr(IfcElectricFlowStorageDeviceTypeEnum, 'INDUCTORBANK', INDETERMINATE)
ups = getattr(IfcElectricFlowStorageDeviceTypeEnum, 'UPS', INDETERMINATE)
userdefined = getattr(IfcElectricFlowStorageDeviceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcElectricFlowStorageDeviceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcElectricGeneratorTypeEnum = enum_namespace()
userdefined = getattr(IfcElectricGeneratorTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcElectricGeneratorTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcElectricHeaterTypeEnum = enum_namespace()
electricpointheater = getattr(IfcElectricHeaterTypeEnum, 'ELECTRICPOINTHEATER', INDETERMINATE)
electriccableheater = getattr(IfcElectricHeaterTypeEnum, 'ELECTRICCABLEHEATER', INDETERMINATE)
electricmatheater = getattr(IfcElectricHeaterTypeEnum, 'ELECTRICMATHEATER', INDETERMINATE)
userdefined = getattr(IfcElectricHeaterTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcElectricHeaterTypeEnum, 'NOTDEFINED', INDETERMINATE)
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
IfcEnergySequenceEnum = enum_namespace()
primary = getattr(IfcEnergySequenceEnum, 'PRIMARY', INDETERMINATE)
secondary = getattr(IfcEnergySequenceEnum, 'SECONDARY', INDETERMINATE)
tertiary = getattr(IfcEnergySequenceEnum, 'TERTIARY', INDETERMINATE)
auxiliary = getattr(IfcEnergySequenceEnum, 'AUXILIARY', INDETERMINATE)
userdefined = getattr(IfcEnergySequenceEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcEnergySequenceEnum, 'NOTDEFINED', INDETERMINATE)
IfcEnvironmentalImpactCategoryEnum = enum_namespace()
combinedvalue = getattr(IfcEnvironmentalImpactCategoryEnum, 'COMBINEDVALUE', INDETERMINATE)
disposal = getattr(IfcEnvironmentalImpactCategoryEnum, 'DISPOSAL', INDETERMINATE)
extraction = getattr(IfcEnvironmentalImpactCategoryEnum, 'EXTRACTION', INDETERMINATE)
installation = getattr(IfcEnvironmentalImpactCategoryEnum, 'INSTALLATION', INDETERMINATE)
manufacture = getattr(IfcEnvironmentalImpactCategoryEnum, 'MANUFACTURE', INDETERMINATE)
transportation = getattr(IfcEnvironmentalImpactCategoryEnum, 'TRANSPORTATION', INDETERMINATE)
userdefined = getattr(IfcEnvironmentalImpactCategoryEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcEnvironmentalImpactCategoryEnum, 'NOTDEFINED', INDETERMINATE)
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
directexpansionshellandtube = getattr(IfcEvaporatorTypeEnum, 'DIRECTEXPANSIONSHELLANDTUBE', INDETERMINATE)
directexpansiontubeintube = getattr(IfcEvaporatorTypeEnum, 'DIRECTEXPANSIONTUBEINTUBE', INDETERMINATE)
directexpansionbrazedplate = getattr(IfcEvaporatorTypeEnum, 'DIRECTEXPANSIONBRAZEDPLATE', INDETERMINATE)
floodedshellandtube = getattr(IfcEvaporatorTypeEnum, 'FLOODEDSHELLANDTUBE', INDETERMINATE)
shellandcoil = getattr(IfcEvaporatorTypeEnum, 'SHELLANDCOIL', INDETERMINATE)
userdefined = getattr(IfcEvaporatorTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcEvaporatorTypeEnum, 'NOTDEFINED', INDETERMINATE)
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
IfcFilterTypeEnum = enum_namespace()
airparticlefilter = getattr(IfcFilterTypeEnum, 'AIRPARTICLEFILTER', INDETERMINATE)
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
electricmeter = getattr(IfcFlowMeterTypeEnum, 'ELECTRICMETER', INDETERMINATE)
energymeter = getattr(IfcFlowMeterTypeEnum, 'ENERGYMETER', INDETERMINATE)
flowmeter = getattr(IfcFlowMeterTypeEnum, 'FLOWMETER', INDETERMINATE)
gasmeter = getattr(IfcFlowMeterTypeEnum, 'GASMETER', INDETERMINATE)
oilmeter = getattr(IfcFlowMeterTypeEnum, 'OILMETER', INDETERMINATE)
watermeter = getattr(IfcFlowMeterTypeEnum, 'WATERMETER', INDETERMINATE)
userdefined = getattr(IfcFlowMeterTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcFlowMeterTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcFootingTypeEnum = enum_namespace()
footing_beam = getattr(IfcFootingTypeEnum, 'FOOTING_BEAM', INDETERMINATE)
pad_footing = getattr(IfcFootingTypeEnum, 'PAD_FOOTING', INDETERMINATE)
pile_cap = getattr(IfcFootingTypeEnum, 'PILE_CAP', INDETERMINATE)
strip_footing = getattr(IfcFootingTypeEnum, 'STRIP_FOOTING', INDETERMINATE)
userdefined = getattr(IfcFootingTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcFootingTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcGasTerminalTypeEnum = enum_namespace()
gasappliance = getattr(IfcGasTerminalTypeEnum, 'GASAPPLIANCE', INDETERMINATE)
gasbooster = getattr(IfcGasTerminalTypeEnum, 'GASBOOSTER', INDETERMINATE)
gasburner = getattr(IfcGasTerminalTypeEnum, 'GASBURNER', INDETERMINATE)
userdefined = getattr(IfcGasTerminalTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcGasTerminalTypeEnum, 'NOTDEFINED', INDETERMINATE)
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
IfcInternalOrExternalEnum = enum_namespace()
internal = getattr(IfcInternalOrExternalEnum, 'INTERNAL', INDETERMINATE)
external = getattr(IfcInternalOrExternalEnum, 'EXTERNAL', INDETERMINATE)
notdefined = getattr(IfcInternalOrExternalEnum, 'NOTDEFINED', INDETERMINATE)
IfcInventoryTypeEnum = enum_namespace()
assetinventory = getattr(IfcInventoryTypeEnum, 'ASSETINVENTORY', INDETERMINATE)
spaceinventory = getattr(IfcInventoryTypeEnum, 'SPACEINVENTORY', INDETERMINATE)
furnitureinventory = getattr(IfcInventoryTypeEnum, 'FURNITUREINVENTORY', INDETERMINATE)
userdefined = getattr(IfcInventoryTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcInventoryTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcJunctionBoxTypeEnum = enum_namespace()
userdefined = getattr(IfcJunctionBoxTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcJunctionBoxTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcLampTypeEnum = enum_namespace()
compactfluorescent = getattr(IfcLampTypeEnum, 'COMPACTFLUORESCENT', INDETERMINATE)
fluorescent = getattr(IfcLampTypeEnum, 'FLUORESCENT', INDETERMINATE)
highpressuremercury = getattr(IfcLampTypeEnum, 'HIGHPRESSUREMERCURY', INDETERMINATE)
highpressuresodium = getattr(IfcLampTypeEnum, 'HIGHPRESSURESODIUM', INDETERMINATE)
metalhalide = getattr(IfcLampTypeEnum, 'METALHALIDE', INDETERMINATE)
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
userdefined = getattr(IfcLightFixtureTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcLightFixtureTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcLoadGroupTypeEnum = enum_namespace()
load_group = getattr(IfcLoadGroupTypeEnum, 'LOAD_GROUP', INDETERMINATE)
load_case = getattr(IfcLoadGroupTypeEnum, 'LOAD_CASE', INDETERMINATE)
load_combination_group = getattr(IfcLoadGroupTypeEnum, 'LOAD_COMBINATION_GROUP', INDETERMINATE)
load_combination = getattr(IfcLoadGroupTypeEnum, 'LOAD_COMBINATION', INDETERMINATE)
userdefined = getattr(IfcLoadGroupTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcLoadGroupTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcLogicalOperatorEnum = enum_namespace()
logicaland = getattr(IfcLogicalOperatorEnum, 'LOGICALAND', INDETERMINATE)
logicalor = getattr(IfcLogicalOperatorEnum, 'LOGICALOR', INDETERMINATE)
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
designintent = getattr(IfcObjectiveEnum, 'DESIGNINTENT', INDETERMINATE)
healthandsafety = getattr(IfcObjectiveEnum, 'HEALTHANDSAFETY', INDETERMINATE)
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
IfcOutletTypeEnum = enum_namespace()
audiovisualoutlet = getattr(IfcOutletTypeEnum, 'AUDIOVISUALOUTLET', INDETERMINATE)
communicationsoutlet = getattr(IfcOutletTypeEnum, 'COMMUNICATIONSOUTLET', INDETERMINATE)
poweroutlet = getattr(IfcOutletTypeEnum, 'POWEROUTLET', INDETERMINATE)
userdefined = getattr(IfcOutletTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcOutletTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcPermeableCoveringOperationEnum = enum_namespace()
grill = getattr(IfcPermeableCoveringOperationEnum, 'GRILL', INDETERMINATE)
louver = getattr(IfcPermeableCoveringOperationEnum, 'LOUVER', INDETERMINATE)
screen = getattr(IfcPermeableCoveringOperationEnum, 'SCREEN', INDETERMINATE)
userdefined = getattr(IfcPermeableCoveringOperationEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcPermeableCoveringOperationEnum, 'NOTDEFINED', INDETERMINATE)
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
IfcProjectOrderRecordTypeEnum = enum_namespace()
change = getattr(IfcProjectOrderRecordTypeEnum, 'CHANGE', INDETERMINATE)
maintenance = getattr(IfcProjectOrderRecordTypeEnum, 'MAINTENANCE', INDETERMINATE)
move = getattr(IfcProjectOrderRecordTypeEnum, 'MOVE', INDETERMINATE)
purchase = getattr(IfcProjectOrderRecordTypeEnum, 'PURCHASE', INDETERMINATE)
work = getattr(IfcProjectOrderRecordTypeEnum, 'WORK', INDETERMINATE)
userdefined = getattr(IfcProjectOrderRecordTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcProjectOrderRecordTypeEnum, 'NOTDEFINED', INDETERMINATE)
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
IfcPropertySourceEnum = enum_namespace()
design = getattr(IfcPropertySourceEnum, 'DESIGN', INDETERMINATE)
designmaximum = getattr(IfcPropertySourceEnum, 'DESIGNMAXIMUM', INDETERMINATE)
designminimum = getattr(IfcPropertySourceEnum, 'DESIGNMINIMUM', INDETERMINATE)
simulated = getattr(IfcPropertySourceEnum, 'SIMULATED', INDETERMINATE)
asbuilt = getattr(IfcPropertySourceEnum, 'ASBUILT', INDETERMINATE)
commissioning = getattr(IfcPropertySourceEnum, 'COMMISSIONING', INDETERMINATE)
measured = getattr(IfcPropertySourceEnum, 'MEASURED', INDETERMINATE)
userdefined = getattr(IfcPropertySourceEnum, 'USERDEFINED', INDETERMINATE)
notknown = getattr(IfcPropertySourceEnum, 'NOTKNOWN', INDETERMINATE)
IfcProtectiveDeviceTypeEnum = enum_namespace()
fusedisconnector = getattr(IfcProtectiveDeviceTypeEnum, 'FUSEDISCONNECTOR', INDETERMINATE)
circuitbreaker = getattr(IfcProtectiveDeviceTypeEnum, 'CIRCUITBREAKER', INDETERMINATE)
earthfailuredevice = getattr(IfcProtectiveDeviceTypeEnum, 'EARTHFAILUREDEVICE', INDETERMINATE)
residualcurrentcircuitbreaker = getattr(IfcProtectiveDeviceTypeEnum, 'RESIDUALCURRENTCIRCUITBREAKER', INDETERMINATE)
residualcurrentswitch = getattr(IfcProtectiveDeviceTypeEnum, 'RESIDUALCURRENTSWITCH', INDETERMINATE)
varistor = getattr(IfcProtectiveDeviceTypeEnum, 'VARISTOR', INDETERMINATE)
userdefined = getattr(IfcProtectiveDeviceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcProtectiveDeviceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcPumpTypeEnum = enum_namespace()
circulator = getattr(IfcPumpTypeEnum, 'CIRCULATOR', INDETERMINATE)
endsuction = getattr(IfcPumpTypeEnum, 'ENDSUCTION', INDETERMINATE)
splitcase = getattr(IfcPumpTypeEnum, 'SPLITCASE', INDETERMINATE)
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
userdefined = getattr(IfcReinforcingBarRoleEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcReinforcingBarRoleEnum, 'NOTDEFINED', INDETERMINATE)
IfcReinforcingBarSurfaceEnum = enum_namespace()
plain = getattr(IfcReinforcingBarSurfaceEnum, 'PLAIN', INDETERMINATE)
textured = getattr(IfcReinforcingBarSurfaceEnum, 'TEXTURED', INDETERMINATE)
IfcResourceConsumptionEnum = enum_namespace()
consumed = getattr(IfcResourceConsumptionEnum, 'CONSUMED', INDETERMINATE)
partiallyconsumed = getattr(IfcResourceConsumptionEnum, 'PARTIALLYCONSUMED', INDETERMINATE)
notconsumed = getattr(IfcResourceConsumptionEnum, 'NOTCONSUMED', INDETERMINATE)
occupied = getattr(IfcResourceConsumptionEnum, 'OCCUPIED', INDETERMINATE)
partiallyoccupied = getattr(IfcResourceConsumptionEnum, 'PARTIALLYOCCUPIED', INDETERMINATE)
notoccupied = getattr(IfcResourceConsumptionEnum, 'NOTOCCUPIED', INDETERMINATE)
userdefined = getattr(IfcResourceConsumptionEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcResourceConsumptionEnum, 'NOTDEFINED', INDETERMINATE)
IfcRibPlateDirectionEnum = enum_namespace()
direction_x = getattr(IfcRibPlateDirectionEnum, 'DIRECTION_X', INDETERMINATE)
direction_y = getattr(IfcRibPlateDirectionEnum, 'DIRECTION_Y', INDETERMINATE)
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
comissioningengineer = getattr(IfcRoleEnum, 'COMISSIONINGENGINEER', INDETERMINATE)
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
co2sensor = getattr(IfcSensorTypeEnum, 'CO2SENSOR', INDETERMINATE)
firesensor = getattr(IfcSensorTypeEnum, 'FIRESENSOR', INDETERMINATE)
flowsensor = getattr(IfcSensorTypeEnum, 'FLOWSENSOR', INDETERMINATE)
gassensor = getattr(IfcSensorTypeEnum, 'GASSENSOR', INDETERMINATE)
heatsensor = getattr(IfcSensorTypeEnum, 'HEATSENSOR', INDETERMINATE)
humiditysensor = getattr(IfcSensorTypeEnum, 'HUMIDITYSENSOR', INDETERMINATE)
lightsensor = getattr(IfcSensorTypeEnum, 'LIGHTSENSOR', INDETERMINATE)
moisturesensor = getattr(IfcSensorTypeEnum, 'MOISTURESENSOR', INDETERMINATE)
movementsensor = getattr(IfcSensorTypeEnum, 'MOVEMENTSENSOR', INDETERMINATE)
pressuresensor = getattr(IfcSensorTypeEnum, 'PRESSURESENSOR', INDETERMINATE)
smokesensor = getattr(IfcSensorTypeEnum, 'SMOKESENSOR', INDETERMINATE)
soundsensor = getattr(IfcSensorTypeEnum, 'SOUNDSENSOR', INDETERMINATE)
temperaturesensor = getattr(IfcSensorTypeEnum, 'TEMPERATURESENSOR', INDETERMINATE)
userdefined = getattr(IfcSensorTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcSensorTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcSequenceEnum = enum_namespace()
start_start = getattr(IfcSequenceEnum, 'START_START', INDETERMINATE)
start_finish = getattr(IfcSequenceEnum, 'START_FINISH', INDETERMINATE)
finish_start = getattr(IfcSequenceEnum, 'FINISH_START', INDETERMINATE)
finish_finish = getattr(IfcSequenceEnum, 'FINISH_FINISH', INDETERMINATE)
notdefined = getattr(IfcSequenceEnum, 'NOTDEFINED', INDETERMINATE)
IfcServiceLifeFactorTypeEnum = enum_namespace()
a_qualityofcomponents = getattr(IfcServiceLifeFactorTypeEnum, 'A_QUALITYOFCOMPONENTS', INDETERMINATE)
b_designlevel = getattr(IfcServiceLifeFactorTypeEnum, 'B_DESIGNLEVEL', INDETERMINATE)
c_workexecutionlevel = getattr(IfcServiceLifeFactorTypeEnum, 'C_WORKEXECUTIONLEVEL', INDETERMINATE)
d_indoorenvironment = getattr(IfcServiceLifeFactorTypeEnum, 'D_INDOORENVIRONMENT', INDETERMINATE)
e_outdoorenvironment = getattr(IfcServiceLifeFactorTypeEnum, 'E_OUTDOORENVIRONMENT', INDETERMINATE)
f_inuseconditions = getattr(IfcServiceLifeFactorTypeEnum, 'F_INUSECONDITIONS', INDETERMINATE)
g_maintenancelevel = getattr(IfcServiceLifeFactorTypeEnum, 'G_MAINTENANCELEVEL', INDETERMINATE)
userdefined = getattr(IfcServiceLifeFactorTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcServiceLifeFactorTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcServiceLifeTypeEnum = enum_namespace()
actualservicelife = getattr(IfcServiceLifeTypeEnum, 'ACTUALSERVICELIFE', INDETERMINATE)
expectedservicelife = getattr(IfcServiceLifeTypeEnum, 'EXPECTEDSERVICELIFE', INDETERMINATE)
optimisticreferenceservicelife = getattr(IfcServiceLifeTypeEnum, 'OPTIMISTICREFERENCESERVICELIFE', INDETERMINATE)
pessimisticreferenceservicelife = getattr(IfcServiceLifeTypeEnum, 'PESSIMISTICREFERENCESERVICELIFE', INDETERMINATE)
referenceservicelife = getattr(IfcServiceLifeTypeEnum, 'REFERENCESERVICELIFE', INDETERMINATE)
IfcSlabTypeEnum = enum_namespace()
floor = getattr(IfcSlabTypeEnum, 'FLOOR', INDETERMINATE)
roof = getattr(IfcSlabTypeEnum, 'ROOF', INDETERMINATE)
landing = getattr(IfcSlabTypeEnum, 'LANDING', INDETERMINATE)
baseslab = getattr(IfcSlabTypeEnum, 'BASESLAB', INDETERMINATE)
userdefined = getattr(IfcSlabTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcSlabTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcSoundScaleEnum = enum_namespace()
dba = getattr(IfcSoundScaleEnum, 'DBA', INDETERMINATE)
dbb = getattr(IfcSoundScaleEnum, 'DBB', INDETERMINATE)
dbc = getattr(IfcSoundScaleEnum, 'DBC', INDETERMINATE)
nc = getattr(IfcSoundScaleEnum, 'NC', INDETERMINATE)
nr = getattr(IfcSoundScaleEnum, 'NR', INDETERMINATE)
userdefined = getattr(IfcSoundScaleEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcSoundScaleEnum, 'NOTDEFINED', INDETERMINATE)
IfcSpaceHeaterTypeEnum = enum_namespace()
sectionalradiator = getattr(IfcSpaceHeaterTypeEnum, 'SECTIONALRADIATOR', INDETERMINATE)
panelradiator = getattr(IfcSpaceHeaterTypeEnum, 'PANELRADIATOR', INDETERMINATE)
tubularradiator = getattr(IfcSpaceHeaterTypeEnum, 'TUBULARRADIATOR', INDETERMINATE)
convector = getattr(IfcSpaceHeaterTypeEnum, 'CONVECTOR', INDETERMINATE)
baseboardheater = getattr(IfcSpaceHeaterTypeEnum, 'BASEBOARDHEATER', INDETERMINATE)
finnedtubeunit = getattr(IfcSpaceHeaterTypeEnum, 'FINNEDTUBEUNIT', INDETERMINATE)
unitheater = getattr(IfcSpaceHeaterTypeEnum, 'UNITHEATER', INDETERMINATE)
userdefined = getattr(IfcSpaceHeaterTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcSpaceHeaterTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcSpaceTypeEnum = enum_namespace()
userdefined = getattr(IfcSpaceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcSpaceTypeEnum, 'NOTDEFINED', INDETERMINATE)
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
IfcStructuralCurveTypeEnum = enum_namespace()
rigid_joined_member = getattr(IfcStructuralCurveTypeEnum, 'RIGID_JOINED_MEMBER', INDETERMINATE)
pin_joined_member = getattr(IfcStructuralCurveTypeEnum, 'PIN_JOINED_MEMBER', INDETERMINATE)
cable = getattr(IfcStructuralCurveTypeEnum, 'CABLE', INDETERMINATE)
tension_member = getattr(IfcStructuralCurveTypeEnum, 'TENSION_MEMBER', INDETERMINATE)
compression_member = getattr(IfcStructuralCurveTypeEnum, 'COMPRESSION_MEMBER', INDETERMINATE)
userdefined = getattr(IfcStructuralCurveTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcStructuralCurveTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcStructuralSurfaceTypeEnum = enum_namespace()
bending_element = getattr(IfcStructuralSurfaceTypeEnum, 'BENDING_ELEMENT', INDETERMINATE)
membrane_element = getattr(IfcStructuralSurfaceTypeEnum, 'MEMBRANE_ELEMENT', INDETERMINATE)
shell = getattr(IfcStructuralSurfaceTypeEnum, 'SHELL', INDETERMINATE)
userdefined = getattr(IfcStructuralSurfaceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcStructuralSurfaceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcSurfaceSide = enum_namespace()
positive = getattr(IfcSurfaceSide, 'POSITIVE', INDETERMINATE)
negative = getattr(IfcSurfaceSide, 'NEGATIVE', INDETERMINATE)
both = getattr(IfcSurfaceSide, 'BOTH', INDETERMINATE)
IfcSurfaceTextureEnum = enum_namespace()
bump = getattr(IfcSurfaceTextureEnum, 'BUMP', INDETERMINATE)
opacity = getattr(IfcSurfaceTextureEnum, 'OPACITY', INDETERMINATE)
reflection = getattr(IfcSurfaceTextureEnum, 'REFLECTION', INDETERMINATE)
selfillumination = getattr(IfcSurfaceTextureEnum, 'SELFILLUMINATION', INDETERMINATE)
shininess = getattr(IfcSurfaceTextureEnum, 'SHININESS', INDETERMINATE)
specular = getattr(IfcSurfaceTextureEnum, 'SPECULAR', INDETERMINATE)
texture = getattr(IfcSurfaceTextureEnum, 'TEXTURE', INDETERMINATE)
transparencymap = getattr(IfcSurfaceTextureEnum, 'TRANSPARENCYMAP', INDETERMINATE)
notdefined = getattr(IfcSurfaceTextureEnum, 'NOTDEFINED', INDETERMINATE)
IfcSwitchingDeviceTypeEnum = enum_namespace()
contactor = getattr(IfcSwitchingDeviceTypeEnum, 'CONTACTOR', INDETERMINATE)
emergencystop = getattr(IfcSwitchingDeviceTypeEnum, 'EMERGENCYSTOP', INDETERMINATE)
starter = getattr(IfcSwitchingDeviceTypeEnum, 'STARTER', INDETERMINATE)
switchdisconnector = getattr(IfcSwitchingDeviceTypeEnum, 'SWITCHDISCONNECTOR', INDETERMINATE)
toggleswitch = getattr(IfcSwitchingDeviceTypeEnum, 'TOGGLESWITCH', INDETERMINATE)
userdefined = getattr(IfcSwitchingDeviceTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcSwitchingDeviceTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcTankTypeEnum = enum_namespace()
preformed = getattr(IfcTankTypeEnum, 'PREFORMED', INDETERMINATE)
sectional = getattr(IfcTankTypeEnum, 'SECTIONAL', INDETERMINATE)
expansion = getattr(IfcTankTypeEnum, 'EXPANSION', INDETERMINATE)
pressurevessel = getattr(IfcTankTypeEnum, 'PRESSUREVESSEL', INDETERMINATE)
userdefined = getattr(IfcTankTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcTankTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcTendonTypeEnum = enum_namespace()
strand = getattr(IfcTendonTypeEnum, 'STRAND', INDETERMINATE)
wire = getattr(IfcTendonTypeEnum, 'WIRE', INDETERMINATE)
bar = getattr(IfcTendonTypeEnum, 'BAR', INDETERMINATE)
coated = getattr(IfcTendonTypeEnum, 'COATED', INDETERMINATE)
userdefined = getattr(IfcTendonTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcTendonTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcTextPath = enum_namespace()
left = getattr(IfcTextPath, 'LEFT', INDETERMINATE)
right = getattr(IfcTextPath, 'RIGHT', INDETERMINATE)
up = getattr(IfcTextPath, 'UP', INDETERMINATE)
down = getattr(IfcTextPath, 'DOWN', INDETERMINATE)
IfcThermalLoadSourceEnum = enum_namespace()
people = getattr(IfcThermalLoadSourceEnum, 'PEOPLE', INDETERMINATE)
lighting = getattr(IfcThermalLoadSourceEnum, 'LIGHTING', INDETERMINATE)
equipment = getattr(IfcThermalLoadSourceEnum, 'EQUIPMENT', INDETERMINATE)
ventilationindoorair = getattr(IfcThermalLoadSourceEnum, 'VENTILATIONINDOORAIR', INDETERMINATE)
ventilationoutsideair = getattr(IfcThermalLoadSourceEnum, 'VENTILATIONOUTSIDEAIR', INDETERMINATE)
recirculatedair = getattr(IfcThermalLoadSourceEnum, 'RECIRCULATEDAIR', INDETERMINATE)
exhaustair = getattr(IfcThermalLoadSourceEnum, 'EXHAUSTAIR', INDETERMINATE)
airexchangerate = getattr(IfcThermalLoadSourceEnum, 'AIREXCHANGERATE', INDETERMINATE)
drybulbtemperature = getattr(IfcThermalLoadSourceEnum, 'DRYBULBTEMPERATURE', INDETERMINATE)
relativehumidity = getattr(IfcThermalLoadSourceEnum, 'RELATIVEHUMIDITY', INDETERMINATE)
infiltration = getattr(IfcThermalLoadSourceEnum, 'INFILTRATION', INDETERMINATE)
userdefined = getattr(IfcThermalLoadSourceEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcThermalLoadSourceEnum, 'NOTDEFINED', INDETERMINATE)
IfcThermalLoadTypeEnum = enum_namespace()
sensible = getattr(IfcThermalLoadTypeEnum, 'SENSIBLE', INDETERMINATE)
latent = getattr(IfcThermalLoadTypeEnum, 'LATENT', INDETERMINATE)
radiant = getattr(IfcThermalLoadTypeEnum, 'RADIANT', INDETERMINATE)
notdefined = getattr(IfcThermalLoadTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcTimeSeriesDataTypeEnum = enum_namespace()
continuous = getattr(IfcTimeSeriesDataTypeEnum, 'CONTINUOUS', INDETERMINATE)
discrete = getattr(IfcTimeSeriesDataTypeEnum, 'DISCRETE', INDETERMINATE)
discretebinary = getattr(IfcTimeSeriesDataTypeEnum, 'DISCRETEBINARY', INDETERMINATE)
piecewisebinary = getattr(IfcTimeSeriesDataTypeEnum, 'PIECEWISEBINARY', INDETERMINATE)
piecewiseconstant = getattr(IfcTimeSeriesDataTypeEnum, 'PIECEWISECONSTANT', INDETERMINATE)
piecewisecontinuous = getattr(IfcTimeSeriesDataTypeEnum, 'PIECEWISECONTINUOUS', INDETERMINATE)
notdefined = getattr(IfcTimeSeriesDataTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcTimeSeriesScheduleTypeEnum = enum_namespace()
annual = getattr(IfcTimeSeriesScheduleTypeEnum, 'ANNUAL', INDETERMINATE)
monthly = getattr(IfcTimeSeriesScheduleTypeEnum, 'MONTHLY', INDETERMINATE)
weekly = getattr(IfcTimeSeriesScheduleTypeEnum, 'WEEKLY', INDETERMINATE)
daily = getattr(IfcTimeSeriesScheduleTypeEnum, 'DAILY', INDETERMINATE)
userdefined = getattr(IfcTimeSeriesScheduleTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcTimeSeriesScheduleTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcTransformerTypeEnum = enum_namespace()
current = getattr(IfcTransformerTypeEnum, 'CURRENT', INDETERMINATE)
frequency = getattr(IfcTransformerTypeEnum, 'FREQUENCY', INDETERMINATE)
voltage = getattr(IfcTransformerTypeEnum, 'VOLTAGE', INDETERMINATE)
userdefined = getattr(IfcTransformerTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcTransformerTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcTransitionCode = enum_namespace()
discontinuous = getattr(IfcTransitionCode, 'DISCONTINUOUS', INDETERMINATE)
continuous = getattr(IfcTransitionCode, 'CONTINUOUS', INDETERMINATE)
contsamegradient = getattr(IfcTransitionCode, 'CONTSAMEGRADIENT', INDETERMINATE)
contsamegradientsamecurvature = getattr(IfcTransitionCode, 'CONTSAMEGRADIENTSAMECURVATURE', INDETERMINATE)
IfcTransportElementTypeEnum = enum_namespace()
elevator = getattr(IfcTransportElementTypeEnum, 'ELEVATOR', INDETERMINATE)
escalator = getattr(IfcTransportElementTypeEnum, 'ESCALATOR', INDETERMINATE)
movingwalkway = getattr(IfcTransportElementTypeEnum, 'MOVINGWALKWAY', INDETERMINATE)
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
IfcUnitaryEquipmentTypeEnum = enum_namespace()
airhandler = getattr(IfcUnitaryEquipmentTypeEnum, 'AIRHANDLER', INDETERMINATE)
airconditioningunit = getattr(IfcUnitaryEquipmentTypeEnum, 'AIRCONDITIONINGUNIT', INDETERMINATE)
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
IfcWallTypeEnum = enum_namespace()
standard = getattr(IfcWallTypeEnum, 'STANDARD', INDETERMINATE)
polygonal = getattr(IfcWallTypeEnum, 'POLYGONAL', INDETERMINATE)
shear = getattr(IfcWallTypeEnum, 'SHEAR', INDETERMINATE)
elementedwall = getattr(IfcWallTypeEnum, 'ELEMENTEDWALL', INDETERMINATE)
plumbingwall = getattr(IfcWallTypeEnum, 'PLUMBINGWALL', INDETERMINATE)
userdefined = getattr(IfcWallTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcWallTypeEnum, 'NOTDEFINED', INDETERMINATE)
IfcWasteTerminalTypeEnum = enum_namespace()
floortrap = getattr(IfcWasteTerminalTypeEnum, 'FLOORTRAP', INDETERMINATE)
floorwaste = getattr(IfcWasteTerminalTypeEnum, 'FLOORWASTE', INDETERMINATE)
gullysump = getattr(IfcWasteTerminalTypeEnum, 'GULLYSUMP', INDETERMINATE)
gullytrap = getattr(IfcWasteTerminalTypeEnum, 'GULLYTRAP', INDETERMINATE)
greaseinterceptor = getattr(IfcWasteTerminalTypeEnum, 'GREASEINTERCEPTOR', INDETERMINATE)
oilinterceptor = getattr(IfcWasteTerminalTypeEnum, 'OILINTERCEPTOR', INDETERMINATE)
petrolinterceptor = getattr(IfcWasteTerminalTypeEnum, 'PETROLINTERCEPTOR', INDETERMINATE)
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
IfcWorkControlTypeEnum = enum_namespace()
actual = getattr(IfcWorkControlTypeEnum, 'ACTUAL', INDETERMINATE)
baseline = getattr(IfcWorkControlTypeEnum, 'BASELINE', INDETERMINATE)
planned = getattr(IfcWorkControlTypeEnum, 'PLANNED', INDETERMINATE)
userdefined = getattr(IfcWorkControlTypeEnum, 'USERDEFINED', INDETERMINATE)
notdefined = getattr(IfcWorkControlTypeEnum, 'NOTDEFINED', INDETERMINATE)

def Ifc2DCompositeCurve(*args, **kwargs):
    return ifcopenshell.create_entity('Ifc2DCompositeCurve', 'IFC2X3', *args, **kwargs)

def IfcActionRequest(*args, **kwargs):
    return ifcopenshell.create_entity('IfcActionRequest', 'IFC2X3', *args, **kwargs)

def IfcActor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcActor', 'IFC2X3', *args, **kwargs)

def IfcActorRole(*args, **kwargs):
    return ifcopenshell.create_entity('IfcActorRole', 'IFC2X3', *args, **kwargs)

def IfcActuatorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcActuatorType', 'IFC2X3', *args, **kwargs)

def IfcAddress(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAddress', 'IFC2X3', *args, **kwargs)

def IfcAirTerminalBoxType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAirTerminalBoxType', 'IFC2X3', *args, **kwargs)

def IfcAirTerminalType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAirTerminalType', 'IFC2X3', *args, **kwargs)

def IfcAirToAirHeatRecoveryType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAirToAirHeatRecoveryType', 'IFC2X3', *args, **kwargs)

def IfcAlarmType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlarmType', 'IFC2X3', *args, **kwargs)

def IfcAngularDimension(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAngularDimension', 'IFC2X3', *args, **kwargs)

def IfcAnnotation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAnnotation', 'IFC2X3', *args, **kwargs)

def IfcAnnotationCurveOccurrence(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAnnotationCurveOccurrence', 'IFC2X3', *args, **kwargs)

def IfcAnnotationFillArea(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAnnotationFillArea', 'IFC2X3', *args, **kwargs)

def IfcAnnotationFillAreaOccurrence(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAnnotationFillAreaOccurrence', 'IFC2X3', *args, **kwargs)

def IfcAnnotationOccurrence(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAnnotationOccurrence', 'IFC2X3', *args, **kwargs)

def IfcAnnotationSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAnnotationSurface', 'IFC2X3', *args, **kwargs)

def IfcAnnotationSurfaceOccurrence(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAnnotationSurfaceOccurrence', 'IFC2X3', *args, **kwargs)

def IfcAnnotationSymbolOccurrence(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAnnotationSymbolOccurrence', 'IFC2X3', *args, **kwargs)

def IfcAnnotationTextOccurrence(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAnnotationTextOccurrence', 'IFC2X3', *args, **kwargs)

def IfcApplication(*args, **kwargs):
    return ifcopenshell.create_entity('IfcApplication', 'IFC2X3', *args, **kwargs)

def IfcAppliedValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAppliedValue', 'IFC2X3', *args, **kwargs)

def IfcAppliedValueRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAppliedValueRelationship', 'IFC2X3', *args, **kwargs)

def IfcApproval(*args, **kwargs):
    return ifcopenshell.create_entity('IfcApproval', 'IFC2X3', *args, **kwargs)

def IfcApprovalActorRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcApprovalActorRelationship', 'IFC2X3', *args, **kwargs)

def IfcApprovalPropertyRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcApprovalPropertyRelationship', 'IFC2X3', *args, **kwargs)

def IfcApprovalRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcApprovalRelationship', 'IFC2X3', *args, **kwargs)

def IfcArbitraryClosedProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcArbitraryClosedProfileDef', 'IFC2X3', *args, **kwargs)

def IfcArbitraryOpenProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcArbitraryOpenProfileDef', 'IFC2X3', *args, **kwargs)

def IfcArbitraryProfileDefWithVoids(*args, **kwargs):
    return ifcopenshell.create_entity('IfcArbitraryProfileDefWithVoids', 'IFC2X3', *args, **kwargs)

def IfcAsset(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAsset', 'IFC2X3', *args, **kwargs)

def IfcAsymmetricIShapeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAsymmetricIShapeProfileDef', 'IFC2X3', *args, **kwargs)

def IfcAxis1Placement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAxis1Placement', 'IFC2X3', *args, **kwargs)

def IfcAxis2Placement2D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAxis2Placement2D', 'IFC2X3', *args, **kwargs)

def IfcAxis2Placement3D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAxis2Placement3D', 'IFC2X3', *args, **kwargs)

def IfcBSplineCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBSplineCurve', 'IFC2X3', *args, **kwargs)

def IfcBeam(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBeam', 'IFC2X3', *args, **kwargs)

def IfcBeamType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBeamType', 'IFC2X3', *args, **kwargs)

def IfcBezierCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBezierCurve', 'IFC2X3', *args, **kwargs)

def IfcBlobTexture(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBlobTexture', 'IFC2X3', *args, **kwargs)

def IfcBlock(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBlock', 'IFC2X3', *args, **kwargs)

def IfcBoilerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoilerType', 'IFC2X3', *args, **kwargs)

def IfcBooleanClippingResult(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBooleanClippingResult', 'IFC2X3', *args, **kwargs)

def IfcBooleanResult(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBooleanResult', 'IFC2X3', *args, **kwargs)

def IfcBoundaryCondition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundaryCondition', 'IFC2X3', *args, **kwargs)

def IfcBoundaryEdgeCondition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundaryEdgeCondition', 'IFC2X3', *args, **kwargs)

def IfcBoundaryFaceCondition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundaryFaceCondition', 'IFC2X3', *args, **kwargs)

def IfcBoundaryNodeCondition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundaryNodeCondition', 'IFC2X3', *args, **kwargs)

def IfcBoundaryNodeConditionWarping(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundaryNodeConditionWarping', 'IFC2X3', *args, **kwargs)

def IfcBoundedCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundedCurve', 'IFC2X3', *args, **kwargs)

def IfcBoundedSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundedSurface', 'IFC2X3', *args, **kwargs)

def IfcBoundingBox(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundingBox', 'IFC2X3', *args, **kwargs)

def IfcBoxedHalfSpace(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoxedHalfSpace', 'IFC2X3', *args, **kwargs)

def IfcBuilding(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuilding', 'IFC2X3', *args, **kwargs)

def IfcBuildingElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuildingElement', 'IFC2X3', *args, **kwargs)

def IfcBuildingElementComponent(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuildingElementComponent', 'IFC2X3', *args, **kwargs)

def IfcBuildingElementPart(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuildingElementPart', 'IFC2X3', *args, **kwargs)

def IfcBuildingElementProxy(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuildingElementProxy', 'IFC2X3', *args, **kwargs)

def IfcBuildingElementProxyType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuildingElementProxyType', 'IFC2X3', *args, **kwargs)

def IfcBuildingElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuildingElementType', 'IFC2X3', *args, **kwargs)

def IfcBuildingStorey(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuildingStorey', 'IFC2X3', *args, **kwargs)

def IfcCShapeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCShapeProfileDef', 'IFC2X3', *args, **kwargs)

def IfcCableCarrierFittingType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCableCarrierFittingType', 'IFC2X3', *args, **kwargs)

def IfcCableCarrierSegmentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCableCarrierSegmentType', 'IFC2X3', *args, **kwargs)

def IfcCableSegmentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCableSegmentType', 'IFC2X3', *args, **kwargs)

def IfcCalendarDate(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCalendarDate', 'IFC2X3', *args, **kwargs)

def IfcCartesianPoint(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianPoint', 'IFC2X3', *args, **kwargs)

def IfcCartesianTransformationOperator(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianTransformationOperator', 'IFC2X3', *args, **kwargs)

def IfcCartesianTransformationOperator2D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianTransformationOperator2D', 'IFC2X3', *args, **kwargs)

def IfcCartesianTransformationOperator2DnonUniform(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianTransformationOperator2DnonUniform', 'IFC2X3', *args, **kwargs)

def IfcCartesianTransformationOperator3D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianTransformationOperator3D', 'IFC2X3', *args, **kwargs)

def IfcCartesianTransformationOperator3DnonUniform(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianTransformationOperator3DnonUniform', 'IFC2X3', *args, **kwargs)

def IfcCenterLineProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCenterLineProfileDef', 'IFC2X3', *args, **kwargs)

def IfcChamferEdgeFeature(*args, **kwargs):
    return ifcopenshell.create_entity('IfcChamferEdgeFeature', 'IFC2X3', *args, **kwargs)

def IfcChillerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcChillerType', 'IFC2X3', *args, **kwargs)

def IfcCircle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCircle', 'IFC2X3', *args, **kwargs)

def IfcCircleHollowProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCircleHollowProfileDef', 'IFC2X3', *args, **kwargs)

def IfcCircleProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCircleProfileDef', 'IFC2X3', *args, **kwargs)

def IfcClassification(*args, **kwargs):
    return ifcopenshell.create_entity('IfcClassification', 'IFC2X3', *args, **kwargs)

def IfcClassificationItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcClassificationItem', 'IFC2X3', *args, **kwargs)

def IfcClassificationItemRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcClassificationItemRelationship', 'IFC2X3', *args, **kwargs)

def IfcClassificationNotation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcClassificationNotation', 'IFC2X3', *args, **kwargs)

def IfcClassificationNotationFacet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcClassificationNotationFacet', 'IFC2X3', *args, **kwargs)

def IfcClassificationReference(*args, **kwargs):
    return ifcopenshell.create_entity('IfcClassificationReference', 'IFC2X3', *args, **kwargs)

def IfcClosedShell(*args, **kwargs):
    return ifcopenshell.create_entity('IfcClosedShell', 'IFC2X3', *args, **kwargs)

def IfcCoilType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCoilType', 'IFC2X3', *args, **kwargs)

def IfcColourRgb(*args, **kwargs):
    return ifcopenshell.create_entity('IfcColourRgb', 'IFC2X3', *args, **kwargs)

def IfcColourSpecification(*args, **kwargs):
    return ifcopenshell.create_entity('IfcColourSpecification', 'IFC2X3', *args, **kwargs)

def IfcColumn(*args, **kwargs):
    return ifcopenshell.create_entity('IfcColumn', 'IFC2X3', *args, **kwargs)

def IfcColumnType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcColumnType', 'IFC2X3', *args, **kwargs)

def IfcComplexProperty(*args, **kwargs):
    return ifcopenshell.create_entity('IfcComplexProperty', 'IFC2X3', *args, **kwargs)

def IfcCompositeCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCompositeCurve', 'IFC2X3', *args, **kwargs)

def IfcCompositeCurveSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCompositeCurveSegment', 'IFC2X3', *args, **kwargs)

def IfcCompositeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCompositeProfileDef', 'IFC2X3', *args, **kwargs)

def IfcCompressorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCompressorType', 'IFC2X3', *args, **kwargs)

def IfcCondenserType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCondenserType', 'IFC2X3', *args, **kwargs)

def IfcCondition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCondition', 'IFC2X3', *args, **kwargs)

def IfcConditionCriterion(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConditionCriterion', 'IFC2X3', *args, **kwargs)

def IfcConic(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConic', 'IFC2X3', *args, **kwargs)

def IfcConnectedFaceSet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConnectedFaceSet', 'IFC2X3', *args, **kwargs)

def IfcConnectionCurveGeometry(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConnectionCurveGeometry', 'IFC2X3', *args, **kwargs)

def IfcConnectionGeometry(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConnectionGeometry', 'IFC2X3', *args, **kwargs)

def IfcConnectionPointEccentricity(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConnectionPointEccentricity', 'IFC2X3', *args, **kwargs)

def IfcConnectionPointGeometry(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConnectionPointGeometry', 'IFC2X3', *args, **kwargs)

def IfcConnectionPortGeometry(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConnectionPortGeometry', 'IFC2X3', *args, **kwargs)

def IfcConnectionSurfaceGeometry(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConnectionSurfaceGeometry', 'IFC2X3', *args, **kwargs)

def IfcConstraint(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstraint', 'IFC2X3', *args, **kwargs)

def IfcConstraintAggregationRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstraintAggregationRelationship', 'IFC2X3', *args, **kwargs)

def IfcConstraintClassificationRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstraintClassificationRelationship', 'IFC2X3', *args, **kwargs)

def IfcConstraintRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstraintRelationship', 'IFC2X3', *args, **kwargs)

def IfcConstructionEquipmentResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstructionEquipmentResource', 'IFC2X3', *args, **kwargs)

def IfcConstructionMaterialResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstructionMaterialResource', 'IFC2X3', *args, **kwargs)

def IfcConstructionProductResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstructionProductResource', 'IFC2X3', *args, **kwargs)

def IfcConstructionResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstructionResource', 'IFC2X3', *args, **kwargs)

def IfcContextDependentUnit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcContextDependentUnit', 'IFC2X3', *args, **kwargs)

def IfcControl(*args, **kwargs):
    return ifcopenshell.create_entity('IfcControl', 'IFC2X3', *args, **kwargs)

def IfcControllerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcControllerType', 'IFC2X3', *args, **kwargs)

def IfcConversionBasedUnit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConversionBasedUnit', 'IFC2X3', *args, **kwargs)

def IfcCooledBeamType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCooledBeamType', 'IFC2X3', *args, **kwargs)

def IfcCoolingTowerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCoolingTowerType', 'IFC2X3', *args, **kwargs)

def IfcCoordinatedUniversalTimeOffset(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCoordinatedUniversalTimeOffset', 'IFC2X3', *args, **kwargs)

def IfcCostItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCostItem', 'IFC2X3', *args, **kwargs)

def IfcCostSchedule(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCostSchedule', 'IFC2X3', *args, **kwargs)

def IfcCostValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCostValue', 'IFC2X3', *args, **kwargs)

def IfcCovering(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCovering', 'IFC2X3', *args, **kwargs)

def IfcCoveringType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCoveringType', 'IFC2X3', *args, **kwargs)

def IfcCraneRailAShapeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCraneRailAShapeProfileDef', 'IFC2X3', *args, **kwargs)

def IfcCraneRailFShapeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCraneRailFShapeProfileDef', 'IFC2X3', *args, **kwargs)

def IfcCrewResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCrewResource', 'IFC2X3', *args, **kwargs)

def IfcCsgPrimitive3D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCsgPrimitive3D', 'IFC2X3', *args, **kwargs)

def IfcCsgSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCsgSolid', 'IFC2X3', *args, **kwargs)

def IfcCurrencyRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurrencyRelationship', 'IFC2X3', *args, **kwargs)

def IfcCurtainWall(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurtainWall', 'IFC2X3', *args, **kwargs)

def IfcCurtainWallType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurtainWallType', 'IFC2X3', *args, **kwargs)

def IfcCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurve', 'IFC2X3', *args, **kwargs)

def IfcCurveBoundedPlane(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurveBoundedPlane', 'IFC2X3', *args, **kwargs)

def IfcCurveStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurveStyle', 'IFC2X3', *args, **kwargs)

def IfcCurveStyleFont(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurveStyleFont', 'IFC2X3', *args, **kwargs)

def IfcCurveStyleFontAndScaling(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurveStyleFontAndScaling', 'IFC2X3', *args, **kwargs)

def IfcCurveStyleFontPattern(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurveStyleFontPattern', 'IFC2X3', *args, **kwargs)

def IfcDamperType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDamperType', 'IFC2X3', *args, **kwargs)

def IfcDateAndTime(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDateAndTime', 'IFC2X3', *args, **kwargs)

def IfcDefinedSymbol(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDefinedSymbol', 'IFC2X3', *args, **kwargs)

def IfcDerivedProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDerivedProfileDef', 'IFC2X3', *args, **kwargs)

def IfcDerivedUnit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDerivedUnit', 'IFC2X3', *args, **kwargs)

def IfcDerivedUnitElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDerivedUnitElement', 'IFC2X3', *args, **kwargs)

def IfcDiameterDimension(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDiameterDimension', 'IFC2X3', *args, **kwargs)

def IfcDimensionCalloutRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDimensionCalloutRelationship', 'IFC2X3', *args, **kwargs)

def IfcDimensionCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDimensionCurve', 'IFC2X3', *args, **kwargs)

def IfcDimensionCurveDirectedCallout(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDimensionCurveDirectedCallout', 'IFC2X3', *args, **kwargs)

def IfcDimensionCurveTerminator(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDimensionCurveTerminator', 'IFC2X3', *args, **kwargs)

def IfcDimensionPair(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDimensionPair', 'IFC2X3', *args, **kwargs)

def IfcDimensionalExponents(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDimensionalExponents', 'IFC2X3', *args, **kwargs)

def IfcDirection(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDirection', 'IFC2X3', *args, **kwargs)

def IfcDiscreteAccessory(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDiscreteAccessory', 'IFC2X3', *args, **kwargs)

def IfcDiscreteAccessoryType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDiscreteAccessoryType', 'IFC2X3', *args, **kwargs)

def IfcDistributionChamberElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionChamberElement', 'IFC2X3', *args, **kwargs)

def IfcDistributionChamberElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionChamberElementType', 'IFC2X3', *args, **kwargs)

def IfcDistributionControlElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionControlElement', 'IFC2X3', *args, **kwargs)

def IfcDistributionControlElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionControlElementType', 'IFC2X3', *args, **kwargs)

def IfcDistributionElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionElement', 'IFC2X3', *args, **kwargs)

def IfcDistributionElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionElementType', 'IFC2X3', *args, **kwargs)

def IfcDistributionFlowElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionFlowElement', 'IFC2X3', *args, **kwargs)

def IfcDistributionFlowElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionFlowElementType', 'IFC2X3', *args, **kwargs)

def IfcDistributionPort(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionPort', 'IFC2X3', *args, **kwargs)

def IfcDocumentElectronicFormat(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDocumentElectronicFormat', 'IFC2X3', *args, **kwargs)

def IfcDocumentInformation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDocumentInformation', 'IFC2X3', *args, **kwargs)

def IfcDocumentInformationRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDocumentInformationRelationship', 'IFC2X3', *args, **kwargs)

def IfcDocumentReference(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDocumentReference', 'IFC2X3', *args, **kwargs)

def IfcDoor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDoor', 'IFC2X3', *args, **kwargs)

def IfcDoorLiningProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDoorLiningProperties', 'IFC2X3', *args, **kwargs)

def IfcDoorPanelProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDoorPanelProperties', 'IFC2X3', *args, **kwargs)

def IfcDoorStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDoorStyle', 'IFC2X3', *args, **kwargs)

def IfcDraughtingCallout(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDraughtingCallout', 'IFC2X3', *args, **kwargs)

def IfcDraughtingCalloutRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDraughtingCalloutRelationship', 'IFC2X3', *args, **kwargs)

def IfcDraughtingPreDefinedColour(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDraughtingPreDefinedColour', 'IFC2X3', *args, **kwargs)

def IfcDraughtingPreDefinedCurveFont(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDraughtingPreDefinedCurveFont', 'IFC2X3', *args, **kwargs)

def IfcDraughtingPreDefinedTextFont(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDraughtingPreDefinedTextFont', 'IFC2X3', *args, **kwargs)

def IfcDuctFittingType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDuctFittingType', 'IFC2X3', *args, **kwargs)

def IfcDuctSegmentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDuctSegmentType', 'IFC2X3', *args, **kwargs)

def IfcDuctSilencerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDuctSilencerType', 'IFC2X3', *args, **kwargs)

def IfcEdge(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEdge', 'IFC2X3', *args, **kwargs)

def IfcEdgeCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEdgeCurve', 'IFC2X3', *args, **kwargs)

def IfcEdgeFeature(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEdgeFeature', 'IFC2X3', *args, **kwargs)

def IfcEdgeLoop(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEdgeLoop', 'IFC2X3', *args, **kwargs)

def IfcElectricApplianceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricApplianceType', 'IFC2X3', *args, **kwargs)

def IfcElectricDistributionPoint(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricDistributionPoint', 'IFC2X3', *args, **kwargs)

def IfcElectricFlowStorageDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricFlowStorageDeviceType', 'IFC2X3', *args, **kwargs)

def IfcElectricGeneratorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricGeneratorType', 'IFC2X3', *args, **kwargs)

def IfcElectricHeaterType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricHeaterType', 'IFC2X3', *args, **kwargs)

def IfcElectricMotorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricMotorType', 'IFC2X3', *args, **kwargs)

def IfcElectricTimeControlType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricTimeControlType', 'IFC2X3', *args, **kwargs)

def IfcElectricalBaseProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricalBaseProperties', 'IFC2X3', *args, **kwargs)

def IfcElectricalCircuit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricalCircuit', 'IFC2X3', *args, **kwargs)

def IfcElectricalElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricalElement', 'IFC2X3', *args, **kwargs)

def IfcElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElement', 'IFC2X3', *args, **kwargs)

def IfcElementAssembly(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElementAssembly', 'IFC2X3', *args, **kwargs)

def IfcElementComponent(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElementComponent', 'IFC2X3', *args, **kwargs)

def IfcElementComponentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElementComponentType', 'IFC2X3', *args, **kwargs)

def IfcElementQuantity(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElementQuantity', 'IFC2X3', *args, **kwargs)

def IfcElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElementType', 'IFC2X3', *args, **kwargs)

def IfcElementarySurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElementarySurface', 'IFC2X3', *args, **kwargs)

def IfcEllipse(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEllipse', 'IFC2X3', *args, **kwargs)

def IfcEllipseProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEllipseProfileDef', 'IFC2X3', *args, **kwargs)

def IfcEnergyConversionDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEnergyConversionDevice', 'IFC2X3', *args, **kwargs)

def IfcEnergyConversionDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEnergyConversionDeviceType', 'IFC2X3', *args, **kwargs)

def IfcEnergyProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEnergyProperties', 'IFC2X3', *args, **kwargs)

def IfcEnvironmentalImpactValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEnvironmentalImpactValue', 'IFC2X3', *args, **kwargs)

def IfcEquipmentElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEquipmentElement', 'IFC2X3', *args, **kwargs)

def IfcEquipmentStandard(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEquipmentStandard', 'IFC2X3', *args, **kwargs)

def IfcEvaporativeCoolerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEvaporativeCoolerType', 'IFC2X3', *args, **kwargs)

def IfcEvaporatorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEvaporatorType', 'IFC2X3', *args, **kwargs)

def IfcExtendedMaterialProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExtendedMaterialProperties', 'IFC2X3', *args, **kwargs)

def IfcExternalReference(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExternalReference', 'IFC2X3', *args, **kwargs)

def IfcExternallyDefinedHatchStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExternallyDefinedHatchStyle', 'IFC2X3', *args, **kwargs)

def IfcExternallyDefinedSurfaceStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExternallyDefinedSurfaceStyle', 'IFC2X3', *args, **kwargs)

def IfcExternallyDefinedSymbol(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExternallyDefinedSymbol', 'IFC2X3', *args, **kwargs)

def IfcExternallyDefinedTextFont(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExternallyDefinedTextFont', 'IFC2X3', *args, **kwargs)

def IfcExtrudedAreaSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExtrudedAreaSolid', 'IFC2X3', *args, **kwargs)

def IfcFace(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFace', 'IFC2X3', *args, **kwargs)

def IfcFaceBasedSurfaceModel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFaceBasedSurfaceModel', 'IFC2X3', *args, **kwargs)

def IfcFaceBound(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFaceBound', 'IFC2X3', *args, **kwargs)

def IfcFaceOuterBound(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFaceOuterBound', 'IFC2X3', *args, **kwargs)

def IfcFaceSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFaceSurface', 'IFC2X3', *args, **kwargs)

def IfcFacetedBrep(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFacetedBrep', 'IFC2X3', *args, **kwargs)

def IfcFacetedBrepWithVoids(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFacetedBrepWithVoids', 'IFC2X3', *args, **kwargs)

def IfcFailureConnectionCondition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFailureConnectionCondition', 'IFC2X3', *args, **kwargs)

def IfcFanType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFanType', 'IFC2X3', *args, **kwargs)

def IfcFastener(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFastener', 'IFC2X3', *args, **kwargs)

def IfcFastenerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFastenerType', 'IFC2X3', *args, **kwargs)

def IfcFeatureElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFeatureElement', 'IFC2X3', *args, **kwargs)

def IfcFeatureElementAddition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFeatureElementAddition', 'IFC2X3', *args, **kwargs)

def IfcFeatureElementSubtraction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFeatureElementSubtraction', 'IFC2X3', *args, **kwargs)

def IfcFillAreaStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFillAreaStyle', 'IFC2X3', *args, **kwargs)

def IfcFillAreaStyleHatching(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFillAreaStyleHatching', 'IFC2X3', *args, **kwargs)

def IfcFillAreaStyleTileSymbolWithStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFillAreaStyleTileSymbolWithStyle', 'IFC2X3', *args, **kwargs)

def IfcFillAreaStyleTiles(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFillAreaStyleTiles', 'IFC2X3', *args, **kwargs)

def IfcFilterType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFilterType', 'IFC2X3', *args, **kwargs)

def IfcFireSuppressionTerminalType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFireSuppressionTerminalType', 'IFC2X3', *args, **kwargs)

def IfcFlowController(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowController', 'IFC2X3', *args, **kwargs)

def IfcFlowControllerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowControllerType', 'IFC2X3', *args, **kwargs)

def IfcFlowFitting(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowFitting', 'IFC2X3', *args, **kwargs)

def IfcFlowFittingType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowFittingType', 'IFC2X3', *args, **kwargs)

def IfcFlowInstrumentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowInstrumentType', 'IFC2X3', *args, **kwargs)

def IfcFlowMeterType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowMeterType', 'IFC2X3', *args, **kwargs)

def IfcFlowMovingDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowMovingDevice', 'IFC2X3', *args, **kwargs)

def IfcFlowMovingDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowMovingDeviceType', 'IFC2X3', *args, **kwargs)

def IfcFlowSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowSegment', 'IFC2X3', *args, **kwargs)

def IfcFlowSegmentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowSegmentType', 'IFC2X3', *args, **kwargs)

def IfcFlowStorageDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowStorageDevice', 'IFC2X3', *args, **kwargs)

def IfcFlowStorageDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowStorageDeviceType', 'IFC2X3', *args, **kwargs)

def IfcFlowTerminal(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowTerminal', 'IFC2X3', *args, **kwargs)

def IfcFlowTerminalType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowTerminalType', 'IFC2X3', *args, **kwargs)

def IfcFlowTreatmentDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowTreatmentDevice', 'IFC2X3', *args, **kwargs)

def IfcFlowTreatmentDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowTreatmentDeviceType', 'IFC2X3', *args, **kwargs)

def IfcFluidFlowProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFluidFlowProperties', 'IFC2X3', *args, **kwargs)

def IfcFooting(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFooting', 'IFC2X3', *args, **kwargs)

def IfcFuelProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFuelProperties', 'IFC2X3', *args, **kwargs)

def IfcFurnishingElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFurnishingElement', 'IFC2X3', *args, **kwargs)

def IfcFurnishingElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFurnishingElementType', 'IFC2X3', *args, **kwargs)

def IfcFurnitureStandard(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFurnitureStandard', 'IFC2X3', *args, **kwargs)

def IfcFurnitureType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFurnitureType', 'IFC2X3', *args, **kwargs)

def IfcGasTerminalType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGasTerminalType', 'IFC2X3', *args, **kwargs)

def IfcGeneralMaterialProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeneralMaterialProperties', 'IFC2X3', *args, **kwargs)

def IfcGeneralProfileProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeneralProfileProperties', 'IFC2X3', *args, **kwargs)

def IfcGeometricCurveSet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeometricCurveSet', 'IFC2X3', *args, **kwargs)

def IfcGeometricRepresentationContext(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeometricRepresentationContext', 'IFC2X3', *args, **kwargs)

def IfcGeometricRepresentationItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeometricRepresentationItem', 'IFC2X3', *args, **kwargs)

def IfcGeometricRepresentationSubContext(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeometricRepresentationSubContext', 'IFC2X3', *args, **kwargs)

def IfcGeometricSet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeometricSet', 'IFC2X3', *args, **kwargs)

def IfcGrid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGrid', 'IFC2X3', *args, **kwargs)

def IfcGridAxis(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGridAxis', 'IFC2X3', *args, **kwargs)

def IfcGridPlacement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGridPlacement', 'IFC2X3', *args, **kwargs)

def IfcGroup(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGroup', 'IFC2X3', *args, **kwargs)

def IfcHalfSpaceSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcHalfSpaceSolid', 'IFC2X3', *args, **kwargs)

def IfcHeatExchangerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcHeatExchangerType', 'IFC2X3', *args, **kwargs)

def IfcHumidifierType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcHumidifierType', 'IFC2X3', *args, **kwargs)

def IfcHygroscopicMaterialProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcHygroscopicMaterialProperties', 'IFC2X3', *args, **kwargs)

def IfcIShapeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIShapeProfileDef', 'IFC2X3', *args, **kwargs)

def IfcImageTexture(*args, **kwargs):
    return ifcopenshell.create_entity('IfcImageTexture', 'IFC2X3', *args, **kwargs)

def IfcInventory(*args, **kwargs):
    return ifcopenshell.create_entity('IfcInventory', 'IFC2X3', *args, **kwargs)

def IfcIrregularTimeSeries(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIrregularTimeSeries', 'IFC2X3', *args, **kwargs)

def IfcIrregularTimeSeriesValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIrregularTimeSeriesValue', 'IFC2X3', *args, **kwargs)

def IfcJunctionBoxType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcJunctionBoxType', 'IFC2X3', *args, **kwargs)

def IfcLShapeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLShapeProfileDef', 'IFC2X3', *args, **kwargs)

def IfcLaborResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLaborResource', 'IFC2X3', *args, **kwargs)

def IfcLampType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLampType', 'IFC2X3', *args, **kwargs)

def IfcLibraryInformation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLibraryInformation', 'IFC2X3', *args, **kwargs)

def IfcLibraryReference(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLibraryReference', 'IFC2X3', *args, **kwargs)

def IfcLightDistributionData(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightDistributionData', 'IFC2X3', *args, **kwargs)

def IfcLightFixtureType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightFixtureType', 'IFC2X3', *args, **kwargs)

def IfcLightIntensityDistribution(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightIntensityDistribution', 'IFC2X3', *args, **kwargs)

def IfcLightSource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightSource', 'IFC2X3', *args, **kwargs)

def IfcLightSourceAmbient(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightSourceAmbient', 'IFC2X3', *args, **kwargs)

def IfcLightSourceDirectional(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightSourceDirectional', 'IFC2X3', *args, **kwargs)

def IfcLightSourceGoniometric(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightSourceGoniometric', 'IFC2X3', *args, **kwargs)

def IfcLightSourcePositional(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightSourcePositional', 'IFC2X3', *args, **kwargs)

def IfcLightSourceSpot(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightSourceSpot', 'IFC2X3', *args, **kwargs)

def IfcLine(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLine', 'IFC2X3', *args, **kwargs)

def IfcLinearDimension(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLinearDimension', 'IFC2X3', *args, **kwargs)

def IfcLocalPlacement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLocalPlacement', 'IFC2X3', *args, **kwargs)

def IfcLocalTime(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLocalTime', 'IFC2X3', *args, **kwargs)

def IfcLoop(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLoop', 'IFC2X3', *args, **kwargs)

def IfcManifoldSolidBrep(*args, **kwargs):
    return ifcopenshell.create_entity('IfcManifoldSolidBrep', 'IFC2X3', *args, **kwargs)

def IfcMappedItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMappedItem', 'IFC2X3', *args, **kwargs)

def IfcMaterial(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterial', 'IFC2X3', *args, **kwargs)

def IfcMaterialClassificationRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialClassificationRelationship', 'IFC2X3', *args, **kwargs)

def IfcMaterialDefinitionRepresentation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialDefinitionRepresentation', 'IFC2X3', *args, **kwargs)

def IfcMaterialLayer(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialLayer', 'IFC2X3', *args, **kwargs)

def IfcMaterialLayerSet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialLayerSet', 'IFC2X3', *args, **kwargs)

def IfcMaterialLayerSetUsage(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialLayerSetUsage', 'IFC2X3', *args, **kwargs)

def IfcMaterialList(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialList', 'IFC2X3', *args, **kwargs)

def IfcMaterialProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialProperties', 'IFC2X3', *args, **kwargs)

def IfcMeasureWithUnit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMeasureWithUnit', 'IFC2X3', *args, **kwargs)

def IfcMechanicalConcreteMaterialProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMechanicalConcreteMaterialProperties', 'IFC2X3', *args, **kwargs)

def IfcMechanicalFastener(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMechanicalFastener', 'IFC2X3', *args, **kwargs)

def IfcMechanicalFastenerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMechanicalFastenerType', 'IFC2X3', *args, **kwargs)

def IfcMechanicalMaterialProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMechanicalMaterialProperties', 'IFC2X3', *args, **kwargs)

def IfcMechanicalSteelMaterialProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMechanicalSteelMaterialProperties', 'IFC2X3', *args, **kwargs)

def IfcMember(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMember', 'IFC2X3', *args, **kwargs)

def IfcMemberType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMemberType', 'IFC2X3', *args, **kwargs)

def IfcMetric(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMetric', 'IFC2X3', *args, **kwargs)

def IfcMonetaryUnit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMonetaryUnit', 'IFC2X3', *args, **kwargs)

def IfcMotorConnectionType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMotorConnectionType', 'IFC2X3', *args, **kwargs)

def IfcMove(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMove', 'IFC2X3', *args, **kwargs)

def IfcNamedUnit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcNamedUnit', 'IFC2X3', *args, **kwargs)

def IfcObject(*args, **kwargs):
    return ifcopenshell.create_entity('IfcObject', 'IFC2X3', *args, **kwargs)

def IfcObjectDefinition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcObjectDefinition', 'IFC2X3', *args, **kwargs)

def IfcObjectPlacement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcObjectPlacement', 'IFC2X3', *args, **kwargs)

def IfcObjective(*args, **kwargs):
    return ifcopenshell.create_entity('IfcObjective', 'IFC2X3', *args, **kwargs)

def IfcOccupant(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOccupant', 'IFC2X3', *args, **kwargs)

def IfcOffsetCurve2D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOffsetCurve2D', 'IFC2X3', *args, **kwargs)

def IfcOffsetCurve3D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOffsetCurve3D', 'IFC2X3', *args, **kwargs)

def IfcOneDirectionRepeatFactor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOneDirectionRepeatFactor', 'IFC2X3', *args, **kwargs)

def IfcOpenShell(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOpenShell', 'IFC2X3', *args, **kwargs)

def IfcOpeningElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOpeningElement', 'IFC2X3', *args, **kwargs)

def IfcOpticalMaterialProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOpticalMaterialProperties', 'IFC2X3', *args, **kwargs)

def IfcOrderAction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOrderAction', 'IFC2X3', *args, **kwargs)

def IfcOrganization(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOrganization', 'IFC2X3', *args, **kwargs)

def IfcOrganizationRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOrganizationRelationship', 'IFC2X3', *args, **kwargs)

def IfcOrientedEdge(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOrientedEdge', 'IFC2X3', *args, **kwargs)

def IfcOutletType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOutletType', 'IFC2X3', *args, **kwargs)

def IfcOwnerHistory(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOwnerHistory', 'IFC2X3', *args, **kwargs)

def IfcParameterizedProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcParameterizedProfileDef', 'IFC2X3', *args, **kwargs)

def IfcPath(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPath', 'IFC2X3', *args, **kwargs)

def IfcPerformanceHistory(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPerformanceHistory', 'IFC2X3', *args, **kwargs)

def IfcPermeableCoveringProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPermeableCoveringProperties', 'IFC2X3', *args, **kwargs)

def IfcPermit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPermit', 'IFC2X3', *args, **kwargs)

def IfcPerson(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPerson', 'IFC2X3', *args, **kwargs)

def IfcPersonAndOrganization(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPersonAndOrganization', 'IFC2X3', *args, **kwargs)

def IfcPhysicalComplexQuantity(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPhysicalComplexQuantity', 'IFC2X3', *args, **kwargs)

def IfcPhysicalQuantity(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPhysicalQuantity', 'IFC2X3', *args, **kwargs)

def IfcPhysicalSimpleQuantity(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPhysicalSimpleQuantity', 'IFC2X3', *args, **kwargs)

def IfcPile(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPile', 'IFC2X3', *args, **kwargs)

def IfcPipeFittingType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPipeFittingType', 'IFC2X3', *args, **kwargs)

def IfcPipeSegmentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPipeSegmentType', 'IFC2X3', *args, **kwargs)

def IfcPixelTexture(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPixelTexture', 'IFC2X3', *args, **kwargs)

def IfcPlacement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPlacement', 'IFC2X3', *args, **kwargs)

def IfcPlanarBox(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPlanarBox', 'IFC2X3', *args, **kwargs)

def IfcPlanarExtent(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPlanarExtent', 'IFC2X3', *args, **kwargs)

def IfcPlane(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPlane', 'IFC2X3', *args, **kwargs)

def IfcPlate(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPlate', 'IFC2X3', *args, **kwargs)

def IfcPlateType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPlateType', 'IFC2X3', *args, **kwargs)

def IfcPoint(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPoint', 'IFC2X3', *args, **kwargs)

def IfcPointOnCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPointOnCurve', 'IFC2X3', *args, **kwargs)

def IfcPointOnSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPointOnSurface', 'IFC2X3', *args, **kwargs)

def IfcPolyLoop(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPolyLoop', 'IFC2X3', *args, **kwargs)

def IfcPolygonalBoundedHalfSpace(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPolygonalBoundedHalfSpace', 'IFC2X3', *args, **kwargs)

def IfcPolyline(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPolyline', 'IFC2X3', *args, **kwargs)

def IfcPort(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPort', 'IFC2X3', *args, **kwargs)

def IfcPostalAddress(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPostalAddress', 'IFC2X3', *args, **kwargs)

def IfcPreDefinedColour(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPreDefinedColour', 'IFC2X3', *args, **kwargs)

def IfcPreDefinedCurveFont(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPreDefinedCurveFont', 'IFC2X3', *args, **kwargs)

def IfcPreDefinedDimensionSymbol(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPreDefinedDimensionSymbol', 'IFC2X3', *args, **kwargs)

def IfcPreDefinedItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPreDefinedItem', 'IFC2X3', *args, **kwargs)

def IfcPreDefinedPointMarkerSymbol(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPreDefinedPointMarkerSymbol', 'IFC2X3', *args, **kwargs)

def IfcPreDefinedSymbol(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPreDefinedSymbol', 'IFC2X3', *args, **kwargs)

def IfcPreDefinedTerminatorSymbol(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPreDefinedTerminatorSymbol', 'IFC2X3', *args, **kwargs)

def IfcPreDefinedTextFont(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPreDefinedTextFont', 'IFC2X3', *args, **kwargs)

def IfcPresentationLayerAssignment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPresentationLayerAssignment', 'IFC2X3', *args, **kwargs)

def IfcPresentationLayerWithStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPresentationLayerWithStyle', 'IFC2X3', *args, **kwargs)

def IfcPresentationStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPresentationStyle', 'IFC2X3', *args, **kwargs)

def IfcPresentationStyleAssignment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPresentationStyleAssignment', 'IFC2X3', *args, **kwargs)

def IfcProcedure(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProcedure', 'IFC2X3', *args, **kwargs)

def IfcProcess(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProcess', 'IFC2X3', *args, **kwargs)

def IfcProduct(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProduct', 'IFC2X3', *args, **kwargs)

def IfcProductDefinitionShape(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProductDefinitionShape', 'IFC2X3', *args, **kwargs)

def IfcProductRepresentation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProductRepresentation', 'IFC2X3', *args, **kwargs)

def IfcProductsOfCombustionProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProductsOfCombustionProperties', 'IFC2X3', *args, **kwargs)

def IfcProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProfileDef', 'IFC2X3', *args, **kwargs)

def IfcProfileProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProfileProperties', 'IFC2X3', *args, **kwargs)

def IfcProject(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProject', 'IFC2X3', *args, **kwargs)

def IfcProjectOrder(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProjectOrder', 'IFC2X3', *args, **kwargs)

def IfcProjectOrderRecord(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProjectOrderRecord', 'IFC2X3', *args, **kwargs)

def IfcProjectionCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProjectionCurve', 'IFC2X3', *args, **kwargs)

def IfcProjectionElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProjectionElement', 'IFC2X3', *args, **kwargs)

def IfcProperty(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProperty', 'IFC2X3', *args, **kwargs)

def IfcPropertyBoundedValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyBoundedValue', 'IFC2X3', *args, **kwargs)

def IfcPropertyConstraintRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyConstraintRelationship', 'IFC2X3', *args, **kwargs)

def IfcPropertyDefinition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyDefinition', 'IFC2X3', *args, **kwargs)

def IfcPropertyDependencyRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyDependencyRelationship', 'IFC2X3', *args, **kwargs)

def IfcPropertyEnumeratedValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyEnumeratedValue', 'IFC2X3', *args, **kwargs)

def IfcPropertyEnumeration(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyEnumeration', 'IFC2X3', *args, **kwargs)

def IfcPropertyListValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyListValue', 'IFC2X3', *args, **kwargs)

def IfcPropertyReferenceValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyReferenceValue', 'IFC2X3', *args, **kwargs)

def IfcPropertySet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertySet', 'IFC2X3', *args, **kwargs)

def IfcPropertySetDefinition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertySetDefinition', 'IFC2X3', *args, **kwargs)

def IfcPropertySingleValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertySingleValue', 'IFC2X3', *args, **kwargs)

def IfcPropertyTableValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyTableValue', 'IFC2X3', *args, **kwargs)

def IfcProtectiveDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProtectiveDeviceType', 'IFC2X3', *args, **kwargs)

def IfcProxy(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProxy', 'IFC2X3', *args, **kwargs)

def IfcPumpType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPumpType', 'IFC2X3', *args, **kwargs)

def IfcQuantityArea(*args, **kwargs):
    return ifcopenshell.create_entity('IfcQuantityArea', 'IFC2X3', *args, **kwargs)

def IfcQuantityCount(*args, **kwargs):
    return ifcopenshell.create_entity('IfcQuantityCount', 'IFC2X3', *args, **kwargs)

def IfcQuantityLength(*args, **kwargs):
    return ifcopenshell.create_entity('IfcQuantityLength', 'IFC2X3', *args, **kwargs)

def IfcQuantityTime(*args, **kwargs):
    return ifcopenshell.create_entity('IfcQuantityTime', 'IFC2X3', *args, **kwargs)

def IfcQuantityVolume(*args, **kwargs):
    return ifcopenshell.create_entity('IfcQuantityVolume', 'IFC2X3', *args, **kwargs)

def IfcQuantityWeight(*args, **kwargs):
    return ifcopenshell.create_entity('IfcQuantityWeight', 'IFC2X3', *args, **kwargs)

def IfcRadiusDimension(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRadiusDimension', 'IFC2X3', *args, **kwargs)

def IfcRailing(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRailing', 'IFC2X3', *args, **kwargs)

def IfcRailingType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRailingType', 'IFC2X3', *args, **kwargs)

def IfcRamp(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRamp', 'IFC2X3', *args, **kwargs)

def IfcRampFlight(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRampFlight', 'IFC2X3', *args, **kwargs)

def IfcRampFlightType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRampFlightType', 'IFC2X3', *args, **kwargs)

def IfcRationalBezierCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRationalBezierCurve', 'IFC2X3', *args, **kwargs)

def IfcRectangleHollowProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRectangleHollowProfileDef', 'IFC2X3', *args, **kwargs)

def IfcRectangleProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRectangleProfileDef', 'IFC2X3', *args, **kwargs)

def IfcRectangularPyramid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRectangularPyramid', 'IFC2X3', *args, **kwargs)

def IfcRectangularTrimmedSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRectangularTrimmedSurface', 'IFC2X3', *args, **kwargs)

def IfcReferencesValueDocument(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReferencesValueDocument', 'IFC2X3', *args, **kwargs)

def IfcRegularTimeSeries(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRegularTimeSeries', 'IFC2X3', *args, **kwargs)

def IfcReinforcementBarProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReinforcementBarProperties', 'IFC2X3', *args, **kwargs)

def IfcReinforcementDefinitionProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReinforcementDefinitionProperties', 'IFC2X3', *args, **kwargs)

def IfcReinforcingBar(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReinforcingBar', 'IFC2X3', *args, **kwargs)

def IfcReinforcingElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReinforcingElement', 'IFC2X3', *args, **kwargs)

def IfcReinforcingMesh(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReinforcingMesh', 'IFC2X3', *args, **kwargs)

def IfcRelAggregates(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAggregates', 'IFC2X3', *args, **kwargs)

def IfcRelAssigns(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssigns', 'IFC2X3', *args, **kwargs)

def IfcRelAssignsTasks(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssignsTasks', 'IFC2X3', *args, **kwargs)

def IfcRelAssignsToActor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssignsToActor', 'IFC2X3', *args, **kwargs)

def IfcRelAssignsToControl(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssignsToControl', 'IFC2X3', *args, **kwargs)

def IfcRelAssignsToGroup(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssignsToGroup', 'IFC2X3', *args, **kwargs)

def IfcRelAssignsToProcess(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssignsToProcess', 'IFC2X3', *args, **kwargs)

def IfcRelAssignsToProduct(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssignsToProduct', 'IFC2X3', *args, **kwargs)

def IfcRelAssignsToProjectOrder(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssignsToProjectOrder', 'IFC2X3', *args, **kwargs)

def IfcRelAssignsToResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssignsToResource', 'IFC2X3', *args, **kwargs)

def IfcRelAssociates(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssociates', 'IFC2X3', *args, **kwargs)

def IfcRelAssociatesAppliedValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssociatesAppliedValue', 'IFC2X3', *args, **kwargs)

def IfcRelAssociatesApproval(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssociatesApproval', 'IFC2X3', *args, **kwargs)

def IfcRelAssociatesClassification(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssociatesClassification', 'IFC2X3', *args, **kwargs)

def IfcRelAssociatesConstraint(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssociatesConstraint', 'IFC2X3', *args, **kwargs)

def IfcRelAssociatesDocument(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssociatesDocument', 'IFC2X3', *args, **kwargs)

def IfcRelAssociatesLibrary(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssociatesLibrary', 'IFC2X3', *args, **kwargs)

def IfcRelAssociatesMaterial(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssociatesMaterial', 'IFC2X3', *args, **kwargs)

def IfcRelAssociatesProfileProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssociatesProfileProperties', 'IFC2X3', *args, **kwargs)

def IfcRelConnects(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnects', 'IFC2X3', *args, **kwargs)

def IfcRelConnectsElements(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsElements', 'IFC2X3', *args, **kwargs)

def IfcRelConnectsPathElements(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsPathElements', 'IFC2X3', *args, **kwargs)

def IfcRelConnectsPortToElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsPortToElement', 'IFC2X3', *args, **kwargs)

def IfcRelConnectsPorts(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsPorts', 'IFC2X3', *args, **kwargs)

def IfcRelConnectsStructuralActivity(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsStructuralActivity', 'IFC2X3', *args, **kwargs)

def IfcRelConnectsStructuralElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsStructuralElement', 'IFC2X3', *args, **kwargs)

def IfcRelConnectsStructuralMember(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsStructuralMember', 'IFC2X3', *args, **kwargs)

def IfcRelConnectsWithEccentricity(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsWithEccentricity', 'IFC2X3', *args, **kwargs)

def IfcRelConnectsWithRealizingElements(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsWithRealizingElements', 'IFC2X3', *args, **kwargs)

def IfcRelContainedInSpatialStructure(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelContainedInSpatialStructure', 'IFC2X3', *args, **kwargs)

def IfcRelCoversBldgElements(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelCoversBldgElements', 'IFC2X3', *args, **kwargs)

def IfcRelCoversSpaces(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelCoversSpaces', 'IFC2X3', *args, **kwargs)

def IfcRelDecomposes(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelDecomposes', 'IFC2X3', *args, **kwargs)

def IfcRelDefines(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelDefines', 'IFC2X3', *args, **kwargs)

def IfcRelDefinesByProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelDefinesByProperties', 'IFC2X3', *args, **kwargs)

def IfcRelDefinesByType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelDefinesByType', 'IFC2X3', *args, **kwargs)

def IfcRelFillsElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelFillsElement', 'IFC2X3', *args, **kwargs)

def IfcRelFlowControlElements(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelFlowControlElements', 'IFC2X3', *args, **kwargs)

def IfcRelInteractionRequirements(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelInteractionRequirements', 'IFC2X3', *args, **kwargs)

def IfcRelNests(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelNests', 'IFC2X3', *args, **kwargs)

def IfcRelOccupiesSpaces(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelOccupiesSpaces', 'IFC2X3', *args, **kwargs)

def IfcRelOverridesProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelOverridesProperties', 'IFC2X3', *args, **kwargs)

def IfcRelProjectsElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelProjectsElement', 'IFC2X3', *args, **kwargs)

def IfcRelReferencedInSpatialStructure(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelReferencedInSpatialStructure', 'IFC2X3', *args, **kwargs)

def IfcRelSchedulesCostItems(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelSchedulesCostItems', 'IFC2X3', *args, **kwargs)

def IfcRelSequence(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelSequence', 'IFC2X3', *args, **kwargs)

def IfcRelServicesBuildings(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelServicesBuildings', 'IFC2X3', *args, **kwargs)

def IfcRelSpaceBoundary(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelSpaceBoundary', 'IFC2X3', *args, **kwargs)

def IfcRelVoidsElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelVoidsElement', 'IFC2X3', *args, **kwargs)

def IfcRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelationship', 'IFC2X3', *args, **kwargs)

def IfcRelaxation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelaxation', 'IFC2X3', *args, **kwargs)

def IfcRepresentation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRepresentation', 'IFC2X3', *args, **kwargs)

def IfcRepresentationContext(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRepresentationContext', 'IFC2X3', *args, **kwargs)

def IfcRepresentationItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRepresentationItem', 'IFC2X3', *args, **kwargs)

def IfcRepresentationMap(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRepresentationMap', 'IFC2X3', *args, **kwargs)

def IfcResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcResource', 'IFC2X3', *args, **kwargs)

def IfcRevolvedAreaSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRevolvedAreaSolid', 'IFC2X3', *args, **kwargs)

def IfcRibPlateProfileProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRibPlateProfileProperties', 'IFC2X3', *args, **kwargs)

def IfcRightCircularCone(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRightCircularCone', 'IFC2X3', *args, **kwargs)

def IfcRightCircularCylinder(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRightCircularCylinder', 'IFC2X3', *args, **kwargs)

def IfcRoof(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRoof', 'IFC2X3', *args, **kwargs)

def IfcRoot(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRoot', 'IFC2X3', *args, **kwargs)

def IfcRoundedEdgeFeature(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRoundedEdgeFeature', 'IFC2X3', *args, **kwargs)

def IfcRoundedRectangleProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRoundedRectangleProfileDef', 'IFC2X3', *args, **kwargs)

def IfcSIUnit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSIUnit', 'IFC2X3', *args, **kwargs)

def IfcSanitaryTerminalType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSanitaryTerminalType', 'IFC2X3', *args, **kwargs)

def IfcScheduleTimeControl(*args, **kwargs):
    return ifcopenshell.create_entity('IfcScheduleTimeControl', 'IFC2X3', *args, **kwargs)

def IfcSectionProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSectionProperties', 'IFC2X3', *args, **kwargs)

def IfcSectionReinforcementProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSectionReinforcementProperties', 'IFC2X3', *args, **kwargs)

def IfcSectionedSpine(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSectionedSpine', 'IFC2X3', *args, **kwargs)

def IfcSensorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSensorType', 'IFC2X3', *args, **kwargs)

def IfcServiceLife(*args, **kwargs):
    return ifcopenshell.create_entity('IfcServiceLife', 'IFC2X3', *args, **kwargs)

def IfcServiceLifeFactor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcServiceLifeFactor', 'IFC2X3', *args, **kwargs)

def IfcShapeAspect(*args, **kwargs):
    return ifcopenshell.create_entity('IfcShapeAspect', 'IFC2X3', *args, **kwargs)

def IfcShapeModel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcShapeModel', 'IFC2X3', *args, **kwargs)

def IfcShapeRepresentation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcShapeRepresentation', 'IFC2X3', *args, **kwargs)

def IfcShellBasedSurfaceModel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcShellBasedSurfaceModel', 'IFC2X3', *args, **kwargs)

def IfcSimpleProperty(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSimpleProperty', 'IFC2X3', *args, **kwargs)

def IfcSite(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSite', 'IFC2X3', *args, **kwargs)

def IfcSlab(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSlab', 'IFC2X3', *args, **kwargs)

def IfcSlabType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSlabType', 'IFC2X3', *args, **kwargs)

def IfcSlippageConnectionCondition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSlippageConnectionCondition', 'IFC2X3', *args, **kwargs)

def IfcSolidModel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSolidModel', 'IFC2X3', *args, **kwargs)

def IfcSoundProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSoundProperties', 'IFC2X3', *args, **kwargs)

def IfcSoundValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSoundValue', 'IFC2X3', *args, **kwargs)

def IfcSpace(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpace', 'IFC2X3', *args, **kwargs)

def IfcSpaceHeaterType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpaceHeaterType', 'IFC2X3', *args, **kwargs)

def IfcSpaceProgram(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpaceProgram', 'IFC2X3', *args, **kwargs)

def IfcSpaceThermalLoadProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpaceThermalLoadProperties', 'IFC2X3', *args, **kwargs)

def IfcSpaceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpaceType', 'IFC2X3', *args, **kwargs)

def IfcSpatialStructureElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpatialStructureElement', 'IFC2X3', *args, **kwargs)

def IfcSpatialStructureElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpatialStructureElementType', 'IFC2X3', *args, **kwargs)

def IfcSphere(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSphere', 'IFC2X3', *args, **kwargs)

def IfcStackTerminalType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStackTerminalType', 'IFC2X3', *args, **kwargs)

def IfcStair(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStair', 'IFC2X3', *args, **kwargs)

def IfcStairFlight(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStairFlight', 'IFC2X3', *args, **kwargs)

def IfcStairFlightType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStairFlightType', 'IFC2X3', *args, **kwargs)

def IfcStructuralAction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralAction', 'IFC2X3', *args, **kwargs)

def IfcStructuralActivity(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralActivity', 'IFC2X3', *args, **kwargs)

def IfcStructuralAnalysisModel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralAnalysisModel', 'IFC2X3', *args, **kwargs)

def IfcStructuralConnection(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralConnection', 'IFC2X3', *args, **kwargs)

def IfcStructuralConnectionCondition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralConnectionCondition', 'IFC2X3', *args, **kwargs)

def IfcStructuralCurveConnection(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralCurveConnection', 'IFC2X3', *args, **kwargs)

def IfcStructuralCurveMember(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralCurveMember', 'IFC2X3', *args, **kwargs)

def IfcStructuralCurveMemberVarying(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralCurveMemberVarying', 'IFC2X3', *args, **kwargs)

def IfcStructuralItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralItem', 'IFC2X3', *args, **kwargs)

def IfcStructuralLinearAction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLinearAction', 'IFC2X3', *args, **kwargs)

def IfcStructuralLinearActionVarying(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLinearActionVarying', 'IFC2X3', *args, **kwargs)

def IfcStructuralLoad(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoad', 'IFC2X3', *args, **kwargs)

def IfcStructuralLoadGroup(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadGroup', 'IFC2X3', *args, **kwargs)

def IfcStructuralLoadLinearForce(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadLinearForce', 'IFC2X3', *args, **kwargs)

def IfcStructuralLoadPlanarForce(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadPlanarForce', 'IFC2X3', *args, **kwargs)

def IfcStructuralLoadSingleDisplacement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadSingleDisplacement', 'IFC2X3', *args, **kwargs)

def IfcStructuralLoadSingleDisplacementDistortion(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadSingleDisplacementDistortion', 'IFC2X3', *args, **kwargs)

def IfcStructuralLoadSingleForce(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadSingleForce', 'IFC2X3', *args, **kwargs)

def IfcStructuralLoadSingleForceWarping(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadSingleForceWarping', 'IFC2X3', *args, **kwargs)

def IfcStructuralLoadStatic(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadStatic', 'IFC2X3', *args, **kwargs)

def IfcStructuralLoadTemperature(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadTemperature', 'IFC2X3', *args, **kwargs)

def IfcStructuralMember(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralMember', 'IFC2X3', *args, **kwargs)

def IfcStructuralPlanarAction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralPlanarAction', 'IFC2X3', *args, **kwargs)

def IfcStructuralPlanarActionVarying(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralPlanarActionVarying', 'IFC2X3', *args, **kwargs)

def IfcStructuralPointAction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralPointAction', 'IFC2X3', *args, **kwargs)

def IfcStructuralPointConnection(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralPointConnection', 'IFC2X3', *args, **kwargs)

def IfcStructuralPointReaction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralPointReaction', 'IFC2X3', *args, **kwargs)

def IfcStructuralProfileProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralProfileProperties', 'IFC2X3', *args, **kwargs)

def IfcStructuralReaction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralReaction', 'IFC2X3', *args, **kwargs)

def IfcStructuralResultGroup(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralResultGroup', 'IFC2X3', *args, **kwargs)

def IfcStructuralSteelProfileProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralSteelProfileProperties', 'IFC2X3', *args, **kwargs)

def IfcStructuralSurfaceConnection(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralSurfaceConnection', 'IFC2X3', *args, **kwargs)

def IfcStructuralSurfaceMember(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralSurfaceMember', 'IFC2X3', *args, **kwargs)

def IfcStructuralSurfaceMemberVarying(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralSurfaceMemberVarying', 'IFC2X3', *args, **kwargs)

def IfcStructuredDimensionCallout(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuredDimensionCallout', 'IFC2X3', *args, **kwargs)

def IfcStyleModel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStyleModel', 'IFC2X3', *args, **kwargs)

def IfcStyledItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStyledItem', 'IFC2X3', *args, **kwargs)

def IfcStyledRepresentation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStyledRepresentation', 'IFC2X3', *args, **kwargs)

def IfcSubContractResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSubContractResource', 'IFC2X3', *args, **kwargs)

def IfcSubedge(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSubedge', 'IFC2X3', *args, **kwargs)

def IfcSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurface', 'IFC2X3', *args, **kwargs)

def IfcSurfaceCurveSweptAreaSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceCurveSweptAreaSolid', 'IFC2X3', *args, **kwargs)

def IfcSurfaceOfLinearExtrusion(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceOfLinearExtrusion', 'IFC2X3', *args, **kwargs)

def IfcSurfaceOfRevolution(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceOfRevolution', 'IFC2X3', *args, **kwargs)

def IfcSurfaceStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceStyle', 'IFC2X3', *args, **kwargs)

def IfcSurfaceStyleLighting(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceStyleLighting', 'IFC2X3', *args, **kwargs)

def IfcSurfaceStyleRefraction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceStyleRefraction', 'IFC2X3', *args, **kwargs)

def IfcSurfaceStyleRendering(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceStyleRendering', 'IFC2X3', *args, **kwargs)

def IfcSurfaceStyleShading(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceStyleShading', 'IFC2X3', *args, **kwargs)

def IfcSurfaceStyleWithTextures(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceStyleWithTextures', 'IFC2X3', *args, **kwargs)

def IfcSurfaceTexture(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceTexture', 'IFC2X3', *args, **kwargs)

def IfcSweptAreaSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSweptAreaSolid', 'IFC2X3', *args, **kwargs)

def IfcSweptDiskSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSweptDiskSolid', 'IFC2X3', *args, **kwargs)

def IfcSweptSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSweptSurface', 'IFC2X3', *args, **kwargs)

def IfcSwitchingDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSwitchingDeviceType', 'IFC2X3', *args, **kwargs)

def IfcSymbolStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSymbolStyle', 'IFC2X3', *args, **kwargs)

def IfcSystem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSystem', 'IFC2X3', *args, **kwargs)

def IfcSystemFurnitureElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSystemFurnitureElementType', 'IFC2X3', *args, **kwargs)

def IfcTShapeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTShapeProfileDef', 'IFC2X3', *args, **kwargs)

def IfcTable(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTable', 'IFC2X3', *args, **kwargs)

def IfcTableRow(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTableRow', 'IFC2X3', *args, **kwargs)

def IfcTankType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTankType', 'IFC2X3', *args, **kwargs)

def IfcTask(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTask', 'IFC2X3', *args, **kwargs)

def IfcTelecomAddress(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTelecomAddress', 'IFC2X3', *args, **kwargs)

def IfcTendon(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTendon', 'IFC2X3', *args, **kwargs)

def IfcTendonAnchor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTendonAnchor', 'IFC2X3', *args, **kwargs)

def IfcTerminatorSymbol(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTerminatorSymbol', 'IFC2X3', *args, **kwargs)

def IfcTextLiteral(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextLiteral', 'IFC2X3', *args, **kwargs)

def IfcTextLiteralWithExtent(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextLiteralWithExtent', 'IFC2X3', *args, **kwargs)

def IfcTextStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextStyle', 'IFC2X3', *args, **kwargs)

def IfcTextStyleFontModel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextStyleFontModel', 'IFC2X3', *args, **kwargs)

def IfcTextStyleForDefinedFont(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextStyleForDefinedFont', 'IFC2X3', *args, **kwargs)

def IfcTextStyleTextModel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextStyleTextModel', 'IFC2X3', *args, **kwargs)

def IfcTextStyleWithBoxCharacteristics(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextStyleWithBoxCharacteristics', 'IFC2X3', *args, **kwargs)

def IfcTextureCoordinate(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextureCoordinate', 'IFC2X3', *args, **kwargs)

def IfcTextureCoordinateGenerator(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextureCoordinateGenerator', 'IFC2X3', *args, **kwargs)

def IfcTextureMap(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextureMap', 'IFC2X3', *args, **kwargs)

def IfcTextureVertex(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextureVertex', 'IFC2X3', *args, **kwargs)

def IfcThermalMaterialProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcThermalMaterialProperties', 'IFC2X3', *args, **kwargs)

def IfcTimeSeries(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTimeSeries', 'IFC2X3', *args, **kwargs)

def IfcTimeSeriesReferenceRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTimeSeriesReferenceRelationship', 'IFC2X3', *args, **kwargs)

def IfcTimeSeriesSchedule(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTimeSeriesSchedule', 'IFC2X3', *args, **kwargs)

def IfcTimeSeriesValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTimeSeriesValue', 'IFC2X3', *args, **kwargs)

def IfcTopologicalRepresentationItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTopologicalRepresentationItem', 'IFC2X3', *args, **kwargs)

def IfcTopologyRepresentation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTopologyRepresentation', 'IFC2X3', *args, **kwargs)

def IfcTransformerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTransformerType', 'IFC2X3', *args, **kwargs)

def IfcTransportElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTransportElement', 'IFC2X3', *args, **kwargs)

def IfcTransportElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTransportElementType', 'IFC2X3', *args, **kwargs)

def IfcTrapeziumProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTrapeziumProfileDef', 'IFC2X3', *args, **kwargs)

def IfcTrimmedCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTrimmedCurve', 'IFC2X3', *args, **kwargs)

def IfcTubeBundleType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTubeBundleType', 'IFC2X3', *args, **kwargs)

def IfcTwoDirectionRepeatFactor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTwoDirectionRepeatFactor', 'IFC2X3', *args, **kwargs)

def IfcTypeObject(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTypeObject', 'IFC2X3', *args, **kwargs)

def IfcTypeProduct(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTypeProduct', 'IFC2X3', *args, **kwargs)

def IfcUShapeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcUShapeProfileDef', 'IFC2X3', *args, **kwargs)

def IfcUnitAssignment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcUnitAssignment', 'IFC2X3', *args, **kwargs)

def IfcUnitaryEquipmentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcUnitaryEquipmentType', 'IFC2X3', *args, **kwargs)

def IfcValveType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcValveType', 'IFC2X3', *args, **kwargs)

def IfcVector(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVector', 'IFC2X3', *args, **kwargs)

def IfcVertex(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVertex', 'IFC2X3', *args, **kwargs)

def IfcVertexBasedTextureMap(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVertexBasedTextureMap', 'IFC2X3', *args, **kwargs)

def IfcVertexLoop(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVertexLoop', 'IFC2X3', *args, **kwargs)

def IfcVertexPoint(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVertexPoint', 'IFC2X3', *args, **kwargs)

def IfcVibrationIsolatorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVibrationIsolatorType', 'IFC2X3', *args, **kwargs)

def IfcVirtualElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVirtualElement', 'IFC2X3', *args, **kwargs)

def IfcVirtualGridIntersection(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVirtualGridIntersection', 'IFC2X3', *args, **kwargs)

def IfcWall(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWall', 'IFC2X3', *args, **kwargs)

def IfcWallStandardCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWallStandardCase', 'IFC2X3', *args, **kwargs)

def IfcWallType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWallType', 'IFC2X3', *args, **kwargs)

def IfcWasteTerminalType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWasteTerminalType', 'IFC2X3', *args, **kwargs)

def IfcWaterProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWaterProperties', 'IFC2X3', *args, **kwargs)

def IfcWindow(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWindow', 'IFC2X3', *args, **kwargs)

def IfcWindowLiningProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWindowLiningProperties', 'IFC2X3', *args, **kwargs)

def IfcWindowPanelProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWindowPanelProperties', 'IFC2X3', *args, **kwargs)

def IfcWindowStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWindowStyle', 'IFC2X3', *args, **kwargs)

def IfcWorkControl(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWorkControl', 'IFC2X3', *args, **kwargs)

def IfcWorkPlan(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWorkPlan', 'IFC2X3', *args, **kwargs)

def IfcWorkSchedule(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWorkSchedule', 'IFC2X3', *args, **kwargs)

def IfcZShapeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcZShapeProfileDef', 'IFC2X3', *args, **kwargs)

def IfcZone(*args, **kwargs):
    return ifcopenshell.create_entity('IfcZone', 'IFC2X3', *args, **kwargs)

class IfcBoxAlignment_WR1:
    SCOPE = 'type'
    TYPE_NAME = 'IfcBoxAlignment'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (getattr(self, 'lower', INDETERMINATE)() in ['top-left', 'top-middle', 'top-right', 'middle-left', 'center', 'middle-right', 'bottom-left', 'bottom-middle', 'bottom-right']) is not False

class IfcCompoundPlaneAngleMeasure_WR1:
    SCOPE = 'type'
    TYPE_NAME = 'IfcCompoundPlaneAngleMeasure'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (-360 <= express_getitem(self, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) < 360) is not False

class IfcCompoundPlaneAngleMeasure_WR2:
    SCOPE = 'type'
    TYPE_NAME = 'IfcCompoundPlaneAngleMeasure'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        assert (-60 <= express_getitem(self, 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) < 60) is not False

class IfcCompoundPlaneAngleMeasure_WR3:
    SCOPE = 'type'
    TYPE_NAME = 'IfcCompoundPlaneAngleMeasure'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        assert (-60 <= express_getitem(self, 3 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) < 60) is not False

class IfcCompoundPlaneAngleMeasure_WR4:
    SCOPE = 'type'
    TYPE_NAME = 'IfcCompoundPlaneAngleMeasure'
    RULE_NAME = 'WR4'

    @staticmethod
    def __call__(self):
        assert (express_getitem(self, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) >= 0 and express_getitem(self, 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) >= 0 and (express_getitem(self, 3 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) >= 0) or (express_getitem(self, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) <= 0 and express_getitem(self, 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) <= 0 and (express_getitem(self, 3 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) <= 0))) is not False

class IfcDaylightSavingHour_WR1:
    SCOPE = 'type'
    TYPE_NAME = 'IfcDaylightSavingHour'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (0 <= self <= 2) is not False

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

class IfcHourInDay_WR1:
    SCOPE = 'type'
    TYPE_NAME = 'IfcHourInDay'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (0 <= self < 24) is not False

class IfcMinuteInHour_WR1:
    SCOPE = 'type'
    TYPE_NAME = 'IfcMinuteInHour'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (0 <= self <= 59) is not False

class IfcMonthInYearNumber_WR1:
    SCOPE = 'type'
    TYPE_NAME = 'IfcMonthInYearNumber'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (1 <= self <= 12) is not False

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

class IfcSecondInMinute_WR1:
    SCOPE = 'type'
    TYPE_NAME = 'IfcSecondInMinute'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (0.0 <= self < 60.0) is not False

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

class Ifc2DCompositeCurve_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'Ifc2DCompositeCurve'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert getattr(self, 'ClosedCurve', INDETERMINATE) is not False

class Ifc2DCompositeCurve_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'Ifc2DCompositeCurve'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        assert (getattr(self, 'Dim', INDETERMINATE) == 2) is not False

class IfcActorRole_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcActorRole'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        role = getattr(self, 'Role', INDETERMINATE)
        assert (role != getattr(IfcRoleEnum, 'USERDEFINED', INDETERMINATE) or (role == getattr(IfcRoleEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'UserDefinedRole', INDETERMINATE)))) is not False

class IfcAddress_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAddress'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        purpose = getattr(self, 'Purpose', INDETERMINATE)
        assert (not exists(purpose) or (purpose != getattr(IfcAddressTypeEnum, 'USERDEFINED', INDETERMINATE) or (purpose == getattr(IfcAddressTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'UserDefinedPurpose', INDETERMINATE))))) is not False

class IfcAirTerminalBoxType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAirTerminalBoxType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcAirTerminalBoxTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcAirTerminalBoxTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcAirTerminalType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAirTerminalType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcAirTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcAirTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcAirToAirHeatRecoveryType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAirToAirHeatRecoveryType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcAirToAirHeatRecoveryTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcAirToAirHeatRecoveryTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcAnnotationCurveOccurrence_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAnnotationCurveOccurrence'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert (not exists(getattr(self, 'Item', INDETERMINATE)) or 'ifc2x3.ifccurve' in typeof(getattr(self, 'Item', INDETERMINATE))) is not False

class IfcAnnotationFillAreaOccurrence_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAnnotationFillAreaOccurrence'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert (not exists(getattr(self, 'Item', INDETERMINATE)) or 'ifc2x3.ifcannotationfillarea' in typeof(getattr(self, 'Item', INDETERMINATE))) is not False

class IfcAnnotationSurface_WR01:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAnnotationSurface'
    RULE_NAME = 'WR01'

    @staticmethod
    def __call__(self):
        item = getattr(self, 'Item', INDETERMINATE)
        assert (sizeof(['ifc2x3.ifcsurface', 'ifc2x3.ifcshellbasedsurfacemodel', 'ifc2x3.ifcfacebasedsurfacemodel', 'ifc2x3.ifcsolidmodel', 'ifc2x3.ifcbooleanresult', 'ifc2x3.ifccsgprimitive3d'] * typeof(item)) >= 1) is not False

class IfcAnnotationSurfaceOccurrence_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAnnotationSurfaceOccurrence'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert (not exists(getattr(self, 'Item', INDETERMINATE)) or sizeof(['ifc2x3.ifcsurface', 'ifc2x3.ifcfacebasedsurfacemodel', 'ifc2x3.ifcshellbasedsurfacemodel', 'ifc2x3.ifcsolidmodel'] * typeof(getattr(self, 'Item', INDETERMINATE))) > 0) is not False

class IfcAnnotationSymbolOccurrence_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAnnotationSymbolOccurrence'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert (not exists(getattr(self, 'Item', INDETERMINATE)) or 'ifc2x3.ifcdefinedsymbol' in typeof(getattr(self, 'Item', INDETERMINATE))) is not False

class IfcAnnotationTextOccurrence_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAnnotationTextOccurrence'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert (not exists(getattr(self, 'Item', INDETERMINATE)) or 'ifc2x3.ifctextliteral' in typeof(getattr(self, 'Item', INDETERMINATE))) is not False

class IfcAppliedValue_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAppliedValue'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        appliedvalue = getattr(self, 'AppliedValue', INDETERMINATE)
        valueofcomponents = getattr(self, 'ValueOfComponents', INDETERMINATE)
        assert (exists(appliedvalue) or exists(valueofcomponents)) is not False

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
        assert (not 'ifc2x3.ifcline' in typeof(outercurve)) is not False

class IfcArbitraryClosedProfileDef_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcArbitraryClosedProfileDef'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        outercurve = getattr(self, 'OuterCurve', INDETERMINATE)
        assert (not 'ifc2x3.ifcoffsetcurve2d' in typeof(outercurve)) is not False

class IfcArbitraryOpenProfileDef_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcArbitraryOpenProfileDef'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        assert ('ifc2x3.ifccenterlineprofiledef' in typeof(self) or getattr(self, 'ProfileType', INDETERMINATE) == getattr(IfcProfileTypeEnum, 'CURVE', INDETERMINATE)) is not False

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
        assert (sizeof([temp for temp in innercurves if 'ifc2x3.ifcline' in typeof(temp)]) == 0) is not False

class IfcAsset_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAsset'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in getattr(getattr(self, 'IsGroupedBy', INDETERMINATE), 'RelatedObjects', INDETERMINATE) if not 'ifc2x3.ifcelement' in typeof(temp)]) == 0) is not False

class IfcAxis1Placement_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis1Placement'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        axis = getattr(self, 'Axis', INDETERMINATE)
        assert (not exists(axis) or getattr(axis, 'Dim', INDETERMINATE) == 3) is not False

class IfcAxis1Placement_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis1Placement'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        assert (getattr(getattr(self, 'Location', INDETERMINATE), 'Dim', INDETERMINATE) == 3) is not False

def calc_IfcAxis1Placement_Z(self):
    axis = getattr(self, 'Axis', INDETERMINATE)
    return nvl(IfcNormalise(axis), IfcDirection(DirectionRatios=[0.0, 0.0, 1.0]))

class IfcAxis2Placement2D_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis2Placement2D'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        refdirection = getattr(self, 'RefDirection', INDETERMINATE)
        assert (not exists(refdirection) or getattr(refdirection, 'Dim', INDETERMINATE) == 2) is not False

class IfcAxis2Placement2D_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis2Placement2D'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        assert (getattr(getattr(self, 'Location', INDETERMINATE), 'Dim', INDETERMINATE) == 2) is not False

def calc_IfcAxis2Placement2D_P(self):
    refdirection = getattr(self, 'RefDirection', INDETERMINATE)
    return IfcBuild2Axes(refdirection)

class IfcAxis2Placement3D_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis2Placement3D'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (getattr(getattr(self, 'Location', INDETERMINATE), 'Dim', INDETERMINATE) == 3) is not False

class IfcAxis2Placement3D_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis2Placement3D'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        axis = getattr(self, 'Axis', INDETERMINATE)
        assert (not exists(axis) or getattr(axis, 'Dim', INDETERMINATE) == 3) is not False

class IfcAxis2Placement3D_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis2Placement3D'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        refdirection = getattr(self, 'RefDirection', INDETERMINATE)
        assert (not exists(refdirection) or getattr(refdirection, 'Dim', INDETERMINATE) == 3) is not False

class IfcAxis2Placement3D_WR4:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis2Placement3D'
    RULE_NAME = 'WR4'

    @staticmethod
    def __call__(self):
        axis = getattr(self, 'Axis', INDETERMINATE)
        refdirection = getattr(self, 'RefDirection', INDETERMINATE)
        assert (not exists(axis) or not exists(refdirection) or getattr(IfcCrossProduct(axis, refdirection), 'Magnitude', INDETERMINATE) > 0.0) is not False

class IfcAxis2Placement3D_WR5:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis2Placement3D'
    RULE_NAME = 'WR5'

    @staticmethod
    def __call__(self):
        axis = getattr(self, 'Axis', INDETERMINATE)
        refdirection = getattr(self, 'RefDirection', INDETERMINATE)
        assert (not exists(axis) ^ exists(refdirection)) is not False

def calc_IfcAxis2Placement3D_P(self):
    axis = getattr(self, 'Axis', INDETERMINATE)
    refdirection = getattr(self, 'RefDirection', INDETERMINATE)
    return IfcBuildAxes(axis, refdirection)

class IfcBSplineCurve_WR41:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBSplineCurve'
    RULE_NAME = 'WR41'

    @staticmethod
    def __call__(self):
        controlpointslist = getattr(self, 'ControlPointsList', INDETERMINATE)
        assert (sizeof([temp for temp in controlpointslist if getattr(temp, 'Dim', INDETERMINATE) != getattr(express_getitem(controlpointslist, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)]) == 0) is not False

def calc_IfcBSplineCurve_ControlPoints(self):
    controlpointslist = getattr(self, 'ControlPointsList', INDETERMINATE)
    upperindexoncontrolpoints = getattr(self, 'UpperIndexOnControlPoints', INDETERMINATE)
    return IfcListToArray(controlpointslist, 0, upperindexoncontrolpoints)

def calc_IfcBSplineCurve_UpperIndexOnControlPoints(self):
    controlpointslist = getattr(self, 'ControlPointsList', INDETERMINATE)
    return sizeof(controlpointslist) - 1

class IfcBlobTexture_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBlobTexture'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        assert (getattr(getattr(self, 'RasterFormat', INDETERMINATE), 'lower', INDETERMINATE)() in ['bmp', 'jpg', 'gif', 'png']) is not False

class IfcBoilerType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBoilerType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcBoilerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcBoilerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcBooleanClippingResult_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBooleanClippingResult'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        firstoperand = getattr(self, 'FirstOperand', INDETERMINATE)
        assert ('ifc2x3.ifcsweptareasolid' in typeof(firstoperand) or 'ifc2x3.ifcbooleanclippingresult' in typeof(firstoperand)) is not False

class IfcBooleanClippingResult_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBooleanClippingResult'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        secondoperand = getattr(self, 'SecondOperand', INDETERMINATE)
        assert ('ifc2x3.ifchalfspacesolid' in typeof(secondoperand)) is not False

class IfcBooleanClippingResult_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBooleanClippingResult'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        operator = getattr(self, 'Operator', INDETERMINATE)
        assert (operator == difference) is not False

class IfcBooleanResult_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBooleanResult'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        firstoperand = getattr(self, 'FirstOperand', INDETERMINATE)
        secondoperand = getattr(self, 'SecondOperand', INDETERMINATE)
        assert (getattr(firstoperand, 'Dim', INDETERMINATE) == getattr(secondoperand, 'Dim', INDETERMINATE)) is not False

def calc_IfcBooleanResult_Dim(self):
    firstoperand = getattr(self, 'FirstOperand', INDETERMINATE)
    return getattr(firstoperand, 'Dim', INDETERMINATE)

def calc_IfcBoundingBox_Dim(self):
    return 3

class IfcBoxedHalfSpace_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBoxedHalfSpace'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (not 'ifc2x3.ifccurveboundedplane' in typeof(getattr(self, 'BaseSurface', INDETERMINATE))) is not False

class IfcBuildingElementProxy_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBuildingElementProxy'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert exists(getattr(self, 'Name', INDETERMINATE)) is not False

class IfcCShapeProfileDef_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCShapeProfileDef'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        depth = getattr(self, 'Depth', INDETERMINATE)
        girth = getattr(self, 'Girth', INDETERMINATE)
        assert (girth < depth / 2.0) is not False

class IfcCShapeProfileDef_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCShapeProfileDef'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        depth = getattr(self, 'Depth', INDETERMINATE)
        width = getattr(self, 'Width', INDETERMINATE)
        internalfilletradius = getattr(self, 'InternalFilletRadius', INDETERMINATE)
        assert (not exists(internalfilletradius) or (internalfilletradius <= width / 2.0 and internalfilletradius <= depth / 2.0)) is not False

class IfcCShapeProfileDef_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCShapeProfileDef'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        depth = getattr(self, 'Depth', INDETERMINATE)
        width = getattr(self, 'Width', INDETERMINATE)
        wallthickness = getattr(self, 'WallThickness', INDETERMINATE)
        assert (wallthickness < width / 2.0 and wallthickness < depth / 2.0) is not False

class IfcCableCarrierFittingType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCableCarrierFittingType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcCableCarrierFittingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCableCarrierFittingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCalendarDate_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCalendarDate'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        assert IfcValidCalendarDate(self) is not False

class IfcCartesianPoint_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianPoint'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        coordinates = getattr(self, 'Coordinates', INDETERMINATE)
        assert (hiindex(coordinates) >= 2) is not False

def calc_IfcCartesianPoint_Dim(self):
    coordinates = getattr(self, 'Coordinates', INDETERMINATE)
    return hiindex(coordinates)

class IfcCartesianTransformationOperator_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator'
    RULE_NAME = 'WR1'

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

class IfcCartesianTransformationOperator2D_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator2D'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (getattr(self, 'Dim', INDETERMINATE) == 2) is not False

class IfcCartesianTransformationOperator2D_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator2D'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        assert (not exists(getattr(self, 'Axis1', INDETERMINATE)) or getattr(getattr(self, 'Axis1', INDETERMINATE), 'Dim', INDETERMINATE) == 2) is not False

class IfcCartesianTransformationOperator2D_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator2D'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        assert (not exists(getattr(self, 'Axis2', INDETERMINATE)) or getattr(getattr(self, 'Axis2', INDETERMINATE), 'Dim', INDETERMINATE) == 2) is not False

def calc_IfcCartesianTransformationOperator2D_U(self):
    return IfcBaseAxis(2, getattr(self, 'Axis1', INDETERMINATE), getattr(self, 'Axis2', INDETERMINATE), None)

class IfcCartesianTransformationOperator2DnonUniform_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator2DnonUniform'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        scl2 = getattr(self, 'Scl2', INDETERMINATE)
        assert (scl2 > 0.0) is not False

def calc_IfcCartesianTransformationOperator2DnonUniform_Scl2(self):
    scale2 = getattr(self, 'Scale2', INDETERMINATE)
    return nvl(scale2, getattr(self, 'Scl', INDETERMINATE))

class IfcCartesianTransformationOperator3D_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator3D'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (getattr(self, 'Dim', INDETERMINATE) == 3) is not False

class IfcCartesianTransformationOperator3D_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator3D'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        assert (not exists(getattr(self, 'Axis1', INDETERMINATE)) or getattr(getattr(self, 'Axis1', INDETERMINATE), 'Dim', INDETERMINATE) == 3) is not False

class IfcCartesianTransformationOperator3D_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator3D'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        assert (not exists(getattr(self, 'Axis2', INDETERMINATE)) or getattr(getattr(self, 'Axis2', INDETERMINATE), 'Dim', INDETERMINATE) == 3) is not False

class IfcCartesianTransformationOperator3D_WR4:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator3D'
    RULE_NAME = 'WR4'

    @staticmethod
    def __call__(self):
        axis3 = getattr(self, 'Axis3', INDETERMINATE)
        assert (not exists(axis3) or getattr(axis3, 'Dim', INDETERMINATE) == 3) is not False

def calc_IfcCartesianTransformationOperator3D_U(self):
    axis3 = getattr(self, 'Axis3', INDETERMINATE)
    return IfcBaseAxis(3, getattr(self, 'Axis1', INDETERMINATE), getattr(self, 'Axis2', INDETERMINATE), axis3)

class IfcCartesianTransformationOperator3DnonUniform_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator3DnonUniform'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        scl2 = getattr(self, 'Scl2', INDETERMINATE)
        assert (scl2 > 0.0) is not False

class IfcCartesianTransformationOperator3DnonUniform_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator3DnonUniform'
    RULE_NAME = 'WR2'

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

class IfcChillerType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcChillerType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcChillerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcChillerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCircleHollowProfileDef_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCircleHollowProfileDef'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        wallthickness = getattr(self, 'WallThickness', INDETERMINATE)
        assert (wallthickness < getattr(self, 'Radius', INDETERMINATE)) is not False

class IfcCoilType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCoilType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcCoilTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCoilTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

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

class IfcCompositeCurve_WR41:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCompositeCurve'
    RULE_NAME = 'WR41'

    @staticmethod
    def __call__(self):
        segments = getattr(self, 'Segments', INDETERMINATE)
        closedcurve = getattr(self, 'ClosedCurve', INDETERMINATE)
        assert (not closedcurve and sizeof([temp for temp in segments if getattr(temp, 'Transition', INDETERMINATE) == discontinuous]) == 1 or (closedcurve and sizeof([temp for temp in segments if getattr(temp, 'Transition', INDETERMINATE) == discontinuous]) == 0)) is not False

class IfcCompositeCurve_WR42:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCompositeCurve'
    RULE_NAME = 'WR42'

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

class IfcCompositeCurveSegment_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCompositeCurveSegment'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        parentcurve = getattr(self, 'ParentCurve', INDETERMINATE)
        assert ('ifc2x3.ifcboundedcurve' in typeof(parentcurve)) is not False

def calc_IfcCompositeCurveSegment_Dim(self):
    parentcurve = getattr(self, 'ParentCurve', INDETERMINATE)
    return getattr(parentcurve, 'Dim', INDETERMINATE)

class IfcCompositeProfileDef_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCompositeProfileDef'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        profiles = getattr(self, 'Profiles', INDETERMINATE)
        assert (sizeof([temp for temp in profiles if getattr(temp, 'ProfileType', INDETERMINATE) != getattr(express_getitem(profiles, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'ProfileType', INDETERMINATE)]) == 0) is not False

class IfcCompositeProfileDef_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCompositeProfileDef'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        profiles = getattr(self, 'Profiles', INDETERMINATE)
        assert (sizeof([temp for temp in profiles if 'ifc2x3.ifccompositeprofiledef' in typeof(temp)]) == 0) is not False

class IfcCompressorType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCompressorType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcCompressorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCompressorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCondenserType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCondenserType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcCondenserTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCondenserTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcConditionCriterion_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConditionCriterion'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert exists(getattr(self, 'Name', INDETERMINATE)) is not False

class IfcConstraint_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConstraint'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        constraintgrade = getattr(self, 'ConstraintGrade', INDETERMINATE)
        assert (constraintgrade != getattr(IfcConstraintEnum, 'USERDEFINED', INDETERMINATE) or (constraintgrade == getattr(IfcConstraintEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'UserDefinedGrade', INDETERMINATE)))) is not False

class IfcConstraintAggregationRelationship_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConstraintAggregationRelationship'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        relatingconstraint = getattr(self, 'RelatingConstraint', INDETERMINATE)
        relatedconstraints = getattr(self, 'RelatedConstraints', INDETERMINATE)
        assert (sizeof([temp for temp in relatedconstraints if temp == relatingconstraint]) == 0) is not False

class IfcConstraintRelationship_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConstraintRelationship'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        relatingconstraint = getattr(self, 'RelatingConstraint', INDETERMINATE)
        relatedconstraints = getattr(self, 'RelatedConstraints', INDETERMINATE)
        assert (sizeof([temp for temp in relatedconstraints if temp == relatingconstraint]) == 0) is not False

class IfcConstructionMaterialResource_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConstructionMaterialResource'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (sizeof(getattr(self, 'ResourceOf', INDETERMINATE)) <= 1) is not False

class IfcConstructionMaterialResource_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConstructionMaterialResource'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        assert (not exists(lambda : express_getitem(getattr(self, 'ResourceOf', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) or getattr(express_getitem(getattr(self, 'ResourceOf', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatedObjectsType', INDETERMINATE) == getattr(IfcObjectTypeEnum, 'PRODUCT', INDETERMINATE)) is not False

class IfcConstructionProductResource_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConstructionProductResource'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (sizeof(getattr(self, 'ResourceOf', INDETERMINATE)) <= 1) is not False

class IfcConstructionProductResource_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConstructionProductResource'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        assert (not exists(lambda : express_getitem(getattr(self, 'ResourceOf', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) or getattr(express_getitem(getattr(self, 'ResourceOf', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatedObjectsType', INDETERMINATE) == getattr(IfcObjectTypeEnum, 'PRODUCT', INDETERMINATE)) is not False

class IfcCooledBeamType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCooledBeamType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcCooledBeamTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCooledBeamTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCoolingTowerType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCoolingTowerType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcCoolingTowerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCoolingTowerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCovering_WR61:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCovering'
    RULE_NAME = 'WR61'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcCoveringTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcCoveringTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

def calc_IfcCsgPrimitive3D_Dim(self):
    return 3

def calc_IfcCurve_Dim(self):
    return IfcCurveDim(self)

def calc_IfcCurveBoundedPlane_Dim(self):
    basissurface = getattr(self, 'BasisSurface', INDETERMINATE)
    return getattr(basissurface, 'Dim', INDETERMINATE)

class IfcCurveStyle_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCurveStyle'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        curvewidth = getattr(self, 'CurveWidth', INDETERMINATE)
        assert (not exists(curvewidth) or 'ifc2x3.ifcpositivelengthmeasure' in typeof(curvewidth) or ('ifc2x3.ifcdescriptivemeasure' in typeof(curvewidth) and curvewidth == 'bylayer')) is not False

class IfcCurveStyleFontPattern_WR01:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCurveStyleFontPattern'
    RULE_NAME = 'WR01'

    @staticmethod
    def __call__(self):
        visiblesegmentlength = getattr(self, 'VisibleSegmentLength', INDETERMINATE)
        assert (visiblesegmentlength >= 0.0) is not False

class IfcDamperType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDamperType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcDamperTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcDamperTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcDerivedProfileDef_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDerivedProfileDef'
    RULE_NAME = 'WR1'

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

class IfcDimensionCalloutRelationship_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDimensionCalloutRelationship'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        assert (getattr(getattr(self, 'Name', INDETERMINATE), 'lower', INDETERMINATE)() in ['primary', 'secondary']) is not False

class IfcDimensionCalloutRelationship_WR12:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDimensionCalloutRelationship'
    RULE_NAME = 'WR12'

    @staticmethod
    def __call__(self):
        assert (sizeof(typeof(getattr(self, 'RelatingDraughtingCallout', INDETERMINATE)) * ['ifc2x3.ifcangulardimension', 'ifc2x3.ifcdiameterdimension', 'ifc2x3.ifclineardimension', 'ifc2x3.ifcradiusdimension']) == 1) is not False

class IfcDimensionCalloutRelationship_WR13:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDimensionCalloutRelationship'
    RULE_NAME = 'WR13'

    @staticmethod
    def __call__(self):
        assert (not 'ifc2x3.ifcdimensioncurvedirectedcallout' in typeof(getattr(self, 'RelatedDraughtingCallout', INDETERMINATE))) is not False

class IfcDimensionCurve_WR51:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDimensionCurve'
    RULE_NAME = 'WR51'

    @staticmethod
    def __call__(self):
        assert (sizeof(usedin(self, 'ifc2x3.ifcdraughtingcallout.contents')) >= 1) is not False

class IfcDimensionCurve_WR52:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDimensionCurve'
    RULE_NAME = 'WR52'

    @staticmethod
    def __call__(self):
        assert (sizeof([dct1 for dct1 in usedin(self, 'ifc2x3.' + 'ifcterminatorsymbol.annotatedcurve') if getattr(dct1, 'Role', INDETERMINATE) == getattr(IfcDimensionExtentUsage, 'ORIGIN', INDETERMINATE)]) <= 1 and sizeof([dct2 for dct2 in usedin(self, 'ifc2x3.' + 'ifcterminatorsymbol.annotatedcurve') if getattr(dct2, 'Role', INDETERMINATE) == getattr(IfcDimensionExtentUsage, 'TARGET', INDETERMINATE)]) <= 1) is not False

class IfcDimensionCurve_WR53:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDimensionCurve'
    RULE_NAME = 'WR53'

    @staticmethod
    def __call__(self):
        annotatedbysymbols = getattr(self, 'AnnotatedBySymbols', INDETERMINATE)
        assert (sizeof([dct for dct in annotatedbysymbols if not 'ifc2x3.ifcdimensioncurveterminator' in typeof(dct)]) == 0) is not False

class IfcDimensionCurveDirectedCallout_WR41:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDimensionCurveDirectedCallout'
    RULE_NAME = 'WR41'

    @staticmethod
    def __call__(self):
        assert (sizeof([dc for dc in getattr(self, 'Contents', INDETERMINATE) if 'ifc2x3.ifcdimensioncurve' in typeof(dc)]) == 1) is not False

class IfcDimensionCurveDirectedCallout_WR42:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDimensionCurveDirectedCallout'
    RULE_NAME = 'WR42'

    @staticmethod
    def __call__(self):
        contents = getattr(self, 'Contents', INDETERMINATE)
        assert (sizeof([dc for dc in getattr(self, 'contents', INDETERMINATE) if 'ifc2x3.ifcprojectioncurve' in typeof(dc)]) <= 2) is not False

class IfcDimensionCurveTerminator_WR61:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDimensionCurveTerminator'
    RULE_NAME = 'WR61'

    @staticmethod
    def __call__(self):
        assert ('ifc2x3.ifcdimensioncurve' in typeof(getattr(self, 'AnnotatedCurve', INDETERMINATE))) is not False

class IfcDimensionPair_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDimensionPair'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        assert (getattr(getattr(self, 'Name', INDETERMINATE), 'lower', INDETERMINATE)() in ['chained', 'parallel']) is not False

class IfcDimensionPair_WR12:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDimensionPair'
    RULE_NAME = 'WR12'

    @staticmethod
    def __call__(self):
        assert (sizeof(typeof(getattr(self, 'RelatingDraughtingCallout', INDETERMINATE)) * ['ifc2x3.ifcangulardimension', 'ifc2x3.ifcdiameterdimension', 'ifc2x3.ifclineardimension', 'ifc2x3.ifcradiusdimension']) == 1) is not False

class IfcDimensionPair_WR13:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDimensionPair'
    RULE_NAME = 'WR13'

    @staticmethod
    def __call__(self):
        assert (sizeof(typeof(getattr(self, 'RelatedDraughtingCallout', INDETERMINATE)) * ['ifc2x3.ifcangulardimension', 'ifc2x3.ifcdiameterdimension', 'ifc2x3.ifclineardimension', 'ifc2x3.ifcradiusdimension']) == 1) is not False

def calc_IfcDirection_Dim(self):
    directionratios = getattr(self, 'DirectionRatios', INDETERMINATE)
    return hiindex(directionratios)

class IfcDocumentElectronicFormat_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDocumentElectronicFormat'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        fileextension = getattr(self, 'FileExtension', INDETERMINATE)
        mimecontenttype = getattr(self, 'MimeContentType', INDETERMINATE)
        assert (exists(fileextension) or exists(mimecontenttype)) is not False

class IfcDocumentReference_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDocumentReference'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        name = getattr(self, 'Name', INDETERMINATE)
        referencetodocument = getattr(self, 'ReferenceToDocument', INDETERMINATE)
        assert exists(name) ^ exists(lambda : express_getitem(referencetodocument, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) is not False

class IfcDoorLiningProperties_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDoorLiningProperties'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        liningdepth = getattr(self, 'LiningDepth', INDETERMINATE)
        liningthickness = getattr(self, 'LiningThickness', INDETERMINATE)
        assert (not (not exists(liningdepth) and exists(liningthickness))) is not False

class IfcDoorLiningProperties_WR32:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDoorLiningProperties'
    RULE_NAME = 'WR32'

    @staticmethod
    def __call__(self):
        thresholddepth = getattr(self, 'ThresholdDepth', INDETERMINATE)
        thresholdthickness = getattr(self, 'ThresholdThickness', INDETERMINATE)
        assert (not (not exists(thresholddepth) and exists(thresholdthickness))) is not False

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
        assert (exists(lambda : express_getitem(getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and 'ifc2x3.ifcdoorstyle' in typeof(express_getitem(getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))) is not False

class IfcDoorPanelProperties_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDoorPanelProperties'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert (exists(lambda : express_getitem(getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and 'ifc2x3.ifcdoorstyle' in typeof(express_getitem(getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))) is not False

class IfcDraughtingPreDefinedColour_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDraughtingPreDefinedColour'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert (getattr(getattr(self, 'Name', INDETERMINATE), 'lower', INDETERMINATE)() in ['black', 'red', 'green', 'blue', 'yellow', 'magenta', 'cyan', 'white', 'bylayer']) is not False

class IfcDraughtingPreDefinedCurveFont_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDraughtingPreDefinedCurveFont'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert (getattr(getattr(self, 'Name', INDETERMINATE), 'lower', INDETERMINATE)() in ['continuous', 'chain', 'chaindoubledash', 'dashed', 'dotted', 'bylayer']) is not False

class IfcDraughtingPreDefinedTextFont_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDraughtingPreDefinedTextFont'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert (getattr(getattr(self, 'Name', INDETERMINATE), 'lower', INDETERMINATE)() in ['iso3098-1fonta', 'iso3098-1fontb']) is not False

class IfcDuctFittingType_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDuctFittingType'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcDuctFittingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcDuctFittingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcDuctSegmentType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDuctSegmentType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcDuctSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcDuctSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcDuctSilencerType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDuctSilencerType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcDuctSilencerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcDuctSilencerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcEdgeLoop_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEdgeLoop'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        edgelist = getattr(self, 'EdgeList', INDETERMINATE)
        ne = getattr(self, 'Ne', INDETERMINATE)
        assert (getattr(express_getitem(edgelist, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'EdgeStart', INDETERMINATE) == getattr(express_getitem(edgelist, ne - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'EdgeEnd', INDETERMINATE)) is not False

class IfcEdgeLoop_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEdgeLoop'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        assert IfcLoopHeadToTail(self) is not False

def calc_IfcEdgeLoop_Ne(self):
    edgelist = getattr(self, 'EdgeList', INDETERMINATE)
    return sizeof(edgelist)

class IfcElectricDistributionPoint_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricDistributionPoint'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        distributionpointfunction = getattr(self, 'DistributionPointFunction', INDETERMINATE)
        assert (distributionpointfunction != getattr(IfcElectricDistributionPointFunctionEnum, 'USERDEFINED', INDETERMINATE) or (distributionpointfunction == getattr(IfcElectricDistributionPointFunctionEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'UserDefinedFunction', INDETERMINATE)))) is not False

class IfcElementAssembly_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElementAssembly'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcElementAssemblyTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcElementAssemblyTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

def calc_IfcElementarySurface_Dim(self):
    position = getattr(self, 'Position', INDETERMINATE)
    return getattr(position, 'Dim', INDETERMINATE)

class IfcEnvironmentalImpactValue_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEnvironmentalImpactValue'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        category = getattr(self, 'Category', INDETERMINATE)
        assert (category != getattr(IfcEnvironmentalImpactCategoryEnum, 'USERDEFINED', INDETERMINATE) or (category == getattr(IfcEnvironmentalImpactCategoryEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'UserDefinedCategory', INDETERMINATE)))) is not False

class IfcEvaporativeCoolerType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEvaporativeCoolerType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcEvaporativeCoolerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcEvaporativeCoolerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcEvaporatorType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEvaporatorType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcEvaporatorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcEvaporatorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcExternalReference_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcExternalReference'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        location = getattr(self, 'Location', INDETERMINATE)
        itemreference = getattr(self, 'ItemReference', INDETERMINATE)
        name = getattr(self, 'Name', INDETERMINATE)
        assert (exists(itemreference) or exists(location) or exists(name)) is not False

class IfcExtrudedAreaSolid_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcExtrudedAreaSolid'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert (IfcDotProduct(IfcDirection(DirectionRatios=[0.0, 0.0, 1.0]), getattr(self, 'ExtrudedDirection', INDETERMINATE)) != 0.0) is not False

class IfcFace_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFace'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        bounds = getattr(self, 'Bounds', INDETERMINATE)
        assert (sizeof([temp for temp in bounds if 'ifc2x3.ifcfaceouterbound' in typeof(temp)]) <= 1) is not False

def calc_IfcFaceBasedSurfaceModel_Dim(self):
    return 3

class IfcFanType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFanType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcFanTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcFanTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcFillAreaStyle_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFillAreaStyle'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in getattr(self, 'FillStyles', INDETERMINATE) if 'ifc2x3.ifccolour' in typeof(style)]) <= 1) is not False

class IfcFillAreaStyle_WR12:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFillAreaStyle'
    RULE_NAME = 'WR12'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in getattr(self, 'FillStyles', INDETERMINATE) if 'ifc2x3.ifcexternallydefinedhatchstyle' in typeof(style)]) <= 1) is not False

class IfcFillAreaStyle_WR13:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFillAreaStyle'
    RULE_NAME = 'WR13'

    @staticmethod
    def __call__(self):
        assert IfcCorrectFillAreaStyle(getattr(self, 'FillStyles', INDETERMINATE)) is not False

class IfcFillAreaStyleHatching_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFillAreaStyleHatching'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        startofnexthatchline = getattr(self, 'StartOfNextHatchLine', INDETERMINATE)
        assert (not 'ifc2x3.ifctwodirectionrepeatfactor' in typeof(startofnexthatchline)) is not False

class IfcFillAreaStyleHatching_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFillAreaStyleHatching'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        patternstart = getattr(self, 'PatternStart', INDETERMINATE)
        assert (not exists(patternstart) or getattr(patternstart, 'Dim', INDETERMINATE) == 2) is not False

class IfcFillAreaStyleHatching_WR23:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFillAreaStyleHatching'
    RULE_NAME = 'WR23'

    @staticmethod
    def __call__(self):
        pointofreferencehatchline = getattr(self, 'PointOfReferenceHatchLine', INDETERMINATE)
        assert (not exists(pointofreferencehatchline) or getattr(pointofreferencehatchline, 'Dim', INDETERMINATE) == 2) is not False

class IfcFilterType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFilterType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcFilterTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcFilterTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcFlowMeterType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFlowMeterType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcFlowMeterTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcFlowMeterTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcFooting_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFooting'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcFootingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcFootingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcGasTerminalType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGasTerminalType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcGasTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcGasTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcGeneralProfileProperties_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGeneralProfileProperties'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        crosssectionarea = getattr(self, 'CrossSectionArea', INDETERMINATE)
        assert (not exists(crosssectionarea) or crosssectionarea > 0.0) is not False

class IfcGeometricCurveSet_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGeometricCurveSet'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in getattr(self, 'Elements', INDETERMINATE) if 'ifc2x3.ifcsurface' in typeof(temp)]) == 0) is not False

class IfcGeometricRepresentationSubContext_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGeometricRepresentationSubContext'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        parentcontext = getattr(self, 'ParentContext', INDETERMINATE)
        assert (not 'ifc2x3.ifcgeometricrepresentationsubcontext' in typeof(parentcontext)) is not False

class IfcGeometricRepresentationSubContext_WR32:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGeometricRepresentationSubContext'
    RULE_NAME = 'WR32'

    @staticmethod
    def __call__(self):
        targetview = getattr(self, 'TargetView', INDETERMINATE)
        userdefinedtargetview = getattr(self, 'UserDefinedTargetView', INDETERMINATE)
        assert (targetview != getattr(IfcGeometricProjectionEnum, 'USERDEFINED', INDETERMINATE) or (targetview == getattr(IfcGeometricProjectionEnum, 'USERDEFINED', INDETERMINATE) and exists(userdefinedtargetview))) is not False

def calc_IfcGeometricRepresentationSubContext_WorldCoordinateSystem(self):
    parentcontext = getattr(self, 'ParentContext', INDETERMINATE)
    return getattr(parentcontext, 'WorldCoordinateSystem', INDETERMINATE)

def calc_IfcGeometricRepresentationSubContext_CoordinateSpaceDimension(self):
    parentcontext = getattr(self, 'ParentContext', INDETERMINATE)
    return getattr(parentcontext, 'CoordinateSpaceDimension', INDETERMINATE)

def calc_IfcGeometricRepresentationSubContext_TrueNorth(self):
    parentcontext = getattr(self, 'ParentContext', INDETERMINATE)
    return nvl(getattr(parentcontext, 'TrueNorth', INDETERMINATE), express_getitem(getattr(getattr(self, 'WorldCoordinateSystem', INDETERMINATE), 'P', INDETERMINATE), 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))

def calc_IfcGeometricRepresentationSubContext_Precision(self):
    parentcontext = getattr(self, 'ParentContext', INDETERMINATE)
    return nvl(getattr(parentcontext, 'Precision', INDETERMINATE), 1)

class IfcGeometricSet_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGeometricSet'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        elements = getattr(self, 'Elements', INDETERMINATE)
        assert (sizeof([temp for temp in elements if getattr(temp, 'Dim', INDETERMINATE) != getattr(express_getitem(elements, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)]) == 0) is not False

def calc_IfcGeometricSet_Dim(self):
    elements = getattr(self, 'Elements', INDETERMINATE)
    return getattr(express_getitem(elements, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)

class IfcGrid_WR41:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGrid'
    RULE_NAME = 'WR41'

    @staticmethod
    def __call__(self):
        assert exists(getattr(self, 'ObjectPlacement', INDETERMINATE)) is not False

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

class IfcHeatExchangerType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcHeatExchangerType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcHeatExchangerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcHeatExchangerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcHumidifierType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcHumidifierType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcHumidifierTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcHumidifierTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcIShapeProfileDef_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcIShapeProfileDef'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        overalldepth = getattr(self, 'OverallDepth', INDETERMINATE)
        flangethickness = getattr(self, 'FlangeThickness', INDETERMINATE)
        assert (flangethickness < overalldepth / 2.0) is not False

class IfcIShapeProfileDef_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcIShapeProfileDef'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        overallwidth = getattr(self, 'OverallWidth', INDETERMINATE)
        webthickness = getattr(self, 'WebThickness', INDETERMINATE)
        assert (webthickness < overallwidth) is not False

class IfcIShapeProfileDef_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcIShapeProfileDef'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        overallwidth = getattr(self, 'OverallWidth', INDETERMINATE)
        overalldepth = getattr(self, 'OverallDepth', INDETERMINATE)
        webthickness = getattr(self, 'WebThickness', INDETERMINATE)
        flangethickness = getattr(self, 'FlangeThickness', INDETERMINATE)
        filletradius = getattr(self, 'FilletRadius', INDETERMINATE)
        assert (not exists(filletradius) or (filletradius <= (overallwidth - webthickness) / 2.0 and filletradius <= (overalldepth - 2.0 * flangethickness) / 2.0)) is not False

class IfcInventory_WR41:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcInventory'
    RULE_NAME = 'WR41'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in getattr(getattr(self, 'IsGroupedBy', INDETERMINATE), 'RelatedObjects', INDETERMINATE) if not ('ifc2x3.ifcspace' in typeof(temp) or 'ifc2x3.ifcasset' in typeof(temp) or 'ifc2x3.ifcfurnishingelement' in typeof(temp))]) == 0) is not False

class IfcLShapeProfileDef_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLShapeProfileDef'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        depth = getattr(self, 'Depth', INDETERMINATE)
        thickness = getattr(self, 'Thickness', INDETERMINATE)
        assert (thickness < depth) is not False

class IfcLShapeProfileDef_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLShapeProfileDef'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        width = getattr(self, 'Width', INDETERMINATE)
        thickness = getattr(self, 'Thickness', INDETERMINATE)
        assert (not exists(width) or thickness < width) is not False

class IfcLine_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLine'
    RULE_NAME = 'WR1'

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

class IfcLocalTime_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLocalTime'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        assert IfcValidTime(self) is not False

class IfcMaterialDefinitionRepresentation_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMaterialDefinitionRepresentation'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        representations = getattr(self, 'Representations', INDETERMINATE)
        assert (sizeof([temp for temp in representations if not 'ifc2x3.ifcstyledrepresentation' in typeof(temp)]) == 0) is not False

def calc_IfcMaterialLayerSet_TotalThickness(self):
    return IfcMlsTotalThickness(self)

class IfcMechanicalMaterialProperties_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMechanicalMaterialProperties'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        youngmodulus = getattr(self, 'YoungModulus', INDETERMINATE)
        assert (not exists(youngmodulus) or youngmodulus >= 0.0) is not False

class IfcMechanicalMaterialProperties_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMechanicalMaterialProperties'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        shearmodulus = getattr(self, 'ShearModulus', INDETERMINATE)
        assert (not exists(shearmodulus) or shearmodulus >= 0.0) is not False

class IfcMechanicalSteelMaterialProperties_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMechanicalSteelMaterialProperties'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        yieldstress = getattr(self, 'YieldStress', INDETERMINATE)
        assert (not exists(yieldstress) or yieldstress >= 0.0) is not False

class IfcMechanicalSteelMaterialProperties_WR32:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMechanicalSteelMaterialProperties'
    RULE_NAME = 'WR32'

    @staticmethod
    def __call__(self):
        ultimatestress = getattr(self, 'UltimateStress', INDETERMINATE)
        assert (not exists(ultimatestress) or ultimatestress >= 0.0) is not False

class IfcMechanicalSteelMaterialProperties_WR33:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMechanicalSteelMaterialProperties'
    RULE_NAME = 'WR33'

    @staticmethod
    def __call__(self):
        hardeningmodule = getattr(self, 'HardeningModule', INDETERMINATE)
        assert (not exists(hardeningmodule) or hardeningmodule >= 0.0) is not False

class IfcMechanicalSteelMaterialProperties_WR34:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMechanicalSteelMaterialProperties'
    RULE_NAME = 'WR34'

    @staticmethod
    def __call__(self):
        proportionalstress = getattr(self, 'ProportionalStress', INDETERMINATE)
        assert (not exists(proportionalstress) or proportionalstress >= 0.0) is not False

class IfcMove_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMove'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (sizeof(getattr(self, 'OperatesOn', INDETERMINATE)) >= 1) is not False

class IfcMove_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMove'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        operateson = getattr(self, 'OperatesOn', INDETERMINATE)
        assert (sizeof([temp for temp in operateson if sizeof([temp2 for temp2 in getattr(temp, 'RelatedObjects', INDETERMINATE) if 'ifc2x3.ifcactor' in typeof(temp2) or 'ifc2x3.ifcequipmentelement' in typeof(temp2) or 'ifc2x3.ifcfurnishingelement' in typeof(temp2)]) >= 1]) >= 1) is not False

class IfcMove_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMove'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        assert exists(getattr(self, 'Name', INDETERMINATE)) is not False

class IfcNamedUnit_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcNamedUnit'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert IfcCorrectDimensions(getattr(self, 'UnitType', INDETERMINATE), getattr(self, 'Dimensions', INDETERMINATE)) is not False

class IfcObject_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcObject'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        isdefinedby = getattr(self, 'IsDefinedBy', INDETERMINATE)
        assert (sizeof([temp for temp in isdefinedby if 'ifc2x3.ifcreldefinesbytype' in typeof(temp)]) <= 1) is not False

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

class IfcOffsetCurve2D_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcOffsetCurve2D'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        basiscurve = getattr(self, 'BasisCurve', INDETERMINATE)
        assert (getattr(basiscurve, 'Dim', INDETERMINATE) == 2) is not False

class IfcOffsetCurve3D_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcOffsetCurve3D'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        basiscurve = getattr(self, 'BasisCurve', INDETERMINATE)
        assert (getattr(basiscurve, 'Dim', INDETERMINATE) == 3) is not False

class IfcOrientedEdge_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcOrientedEdge'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        edgeelement = getattr(self, 'EdgeElement', INDETERMINATE)
        assert (not 'ifc2x3.ifcorientededge' in typeof(edgeelement)) is not False

def calc_IfcOrientedEdge_EdgeStart(self):
    edgeelement = getattr(self, 'EdgeElement', INDETERMINATE)
    orientation = getattr(self, 'Orientation', INDETERMINATE)
    return IfcBooleanChoose(orientation, getattr(edgeelement, 'EdgeStart', INDETERMINATE), getattr(edgeelement, 'EdgeEnd', INDETERMINATE))

def calc_IfcOrientedEdge_EdgeEnd(self):
    edgeelement = getattr(self, 'EdgeElement', INDETERMINATE)
    orientation = getattr(self, 'Orientation', INDETERMINATE)
    return IfcBooleanChoose(orientation, getattr(edgeelement, 'EdgeEnd', INDETERMINATE), getattr(edgeelement, 'EdgeStart', INDETERMINATE))

class IfcPath_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPath'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert IfcPathHeadToTail(self) is not False

class IfcPerson_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPerson'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        familyname = getattr(self, 'FamilyName', INDETERMINATE)
        givenname = getattr(self, 'GivenName', INDETERMINATE)
        assert (exists(familyname) or exists(givenname)) is not False

class IfcPhysicalComplexQuantity_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPhysicalComplexQuantity'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        hasquantities = getattr(self, 'HasQuantities', INDETERMINATE)
        assert (sizeof([temp for temp in hasquantities if self == temp]) == 0) is not False

class IfcPile_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPile'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcPileTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcPileTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcPipeFittingType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPipeFittingType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcPipeFittingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcPipeFittingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcPipeSegmentType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPipeSegmentType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcPipeSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcPipeSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcPixelTexture_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPixelTexture'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        width = getattr(self, 'Width', INDETERMINATE)
        assert (width >= 1) is not False

class IfcPixelTexture_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPixelTexture'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        height = getattr(self, 'Height', INDETERMINATE)
        assert (height >= 1) is not False

class IfcPixelTexture_WR23:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPixelTexture'
    RULE_NAME = 'WR23'

    @staticmethod
    def __call__(self):
        colourcomponents = getattr(self, 'ColourComponents', INDETERMINATE)
        assert (1 <= colourcomponents <= 4) is not False

class IfcPixelTexture_WR24:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPixelTexture'
    RULE_NAME = 'WR24'

    @staticmethod
    def __call__(self):
        width = getattr(self, 'Width', INDETERMINATE)
        height = getattr(self, 'Height', INDETERMINATE)
        pixel = getattr(self, 'Pixel', INDETERMINATE)
        assert (sizeof(pixel) == width * height) is not False

def calc_IfcPlacement_Dim(self):
    location = getattr(self, 'Location', INDETERMINATE)
    return getattr(location, 'Dim', INDETERMINATE)

def calc_IfcPointOnCurve_Dim(self):
    basiscurve = getattr(self, 'BasisCurve', INDETERMINATE)
    return getattr(basiscurve, 'Dim', INDETERMINATE)

def calc_IfcPointOnSurface_Dim(self):
    basissurface = getattr(self, 'BasisSurface', INDETERMINATE)
    return getattr(basissurface, 'Dim', INDETERMINATE)

class IfcPolyLoop_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPolyLoop'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        polygon = getattr(self, 'Polygon', INDETERMINATE)
        assert (sizeof([temp for temp in polygon if getattr(temp, 'Dim', INDETERMINATE) != getattr(express_getitem(polygon, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)]) == 0) is not False

class IfcPolygonalBoundedHalfSpace_WR41:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPolygonalBoundedHalfSpace'
    RULE_NAME = 'WR41'

    @staticmethod
    def __call__(self):
        polygonalboundary = getattr(self, 'PolygonalBoundary', INDETERMINATE)
        assert (getattr(polygonalboundary, 'Dim', INDETERMINATE) == 2) is not False

class IfcPolygonalBoundedHalfSpace_WR42:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPolygonalBoundedHalfSpace'
    RULE_NAME = 'WR42'

    @staticmethod
    def __call__(self):
        polygonalboundary = getattr(self, 'PolygonalBoundary', INDETERMINATE)
        assert (sizeof(typeof(polygonalboundary) * ['ifc2x3.ifcpolyline', 'ifc2x3.ifccompositecurve']) == 1) is not False

class IfcPolyline_WR41:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPolyline'
    RULE_NAME = 'WR41'

    @staticmethod
    def __call__(self):
        points = getattr(self, 'Points', INDETERMINATE)
        assert (sizeof([temp for temp in points if getattr(temp, 'Dim', INDETERMINATE) != getattr(express_getitem(points, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)]) == 0) is not False

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

class IfcPreDefinedDimensionSymbol_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPreDefinedDimensionSymbol'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert (getattr(getattr(self, 'Name', INDETERMINATE), 'lower', INDETERMINATE)() in ['arclength', 'conicaltaper', 'counterbore', 'countersink', 'depth', 'diameter', 'plusminus', 'radius', 'slope', 'sphericaldiameter', 'sphericalradius', 'square']) is not False

class IfcPreDefinedPointMarkerSymbol_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPreDefinedPointMarkerSymbol'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert (getattr(getattr(self, 'Name', INDETERMINATE), 'lower', INDETERMINATE)() in ['asterisk', 'circle', 'dot', 'plus', 'square', 'triangle', 'x']) is not False

class IfcPreDefinedTerminatorSymbol_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPreDefinedTerminatorSymbol'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert (getattr(getattr(self, 'Name', INDETERMINATE), 'lower', INDETERMINATE)() in ['blankedarrow', 'blankedbox', 'blankeddot', 'dimensionorigin', 'filledarrow', 'filledbox', 'filleddot', 'integralsymbol', 'openarrow', 'slash', 'unfilledarrow']) is not False

class IfcProcedure_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProcedure'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in getattr(self, 'Decomposes', INDETERMINATE) if not 'ifc2x3.ifcrelnests' in typeof(temp)]) == 0) is not False

class IfcProcedure_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProcedure'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in getattr(self, 'IsDecomposedBy', INDETERMINATE) if not 'ifc2x3.ifcrelnests' in typeof(temp)]) == 0) is not False

class IfcProcedure_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProcedure'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        assert exists(getattr(self, 'Name', INDETERMINATE)) is not False

class IfcProcedure_WR4:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProcedure'
    RULE_NAME = 'WR4'

    @staticmethod
    def __call__(self):
        proceduretype = getattr(self, 'ProcedureType', INDETERMINATE)
        assert (proceduretype != getattr(IfcProcedureTypeEnum, 'USERDEFINED', INDETERMINATE) or (proceduretype == getattr(IfcProcedureTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'UserDefinedProcedureType', INDETERMINATE)))) is not False

class IfcProduct_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProduct'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        objectplacement = getattr(self, 'ObjectPlacement', INDETERMINATE)
        representation = getattr(self, 'Representation', INDETERMINATE)
        assert (exists(representation) and exists(objectplacement) or (exists(representation) and (not 'ifc2x3.ifcproductdefinitionshape' in typeof(representation))) or (not exists(representation))) is not False

class IfcProductDefinitionShape_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProductDefinitionShape'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        representations = getattr(self, 'Representations', INDETERMINATE)
        assert (sizeof([temp for temp in representations if not 'ifc2x3.ifcshapemodel' in typeof(temp)]) == 0) is not False

class IfcProject_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProject'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert exists(getattr(self, 'Name', INDETERMINATE)) is not False

class IfcProject_WR32:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProject'
    RULE_NAME = 'WR32'

    @staticmethod
    def __call__(self):
        representationcontexts = getattr(self, 'RepresentationContexts', INDETERMINATE)
        assert (sizeof([temp for temp in representationcontexts if 'ifc2x3.ifcgeometricrepresentationsubcontext' in typeof(temp)]) == 0) is not False

class IfcProject_WR33:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProject'
    RULE_NAME = 'WR33'

    @staticmethod
    def __call__(self):
        assert (sizeof(getattr(self, 'Decomposes', INDETERMINATE)) == 0) is not False

class IfcPropertyBoundedValue_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyBoundedValue'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        upperboundvalue = getattr(self, 'UpperBoundValue', INDETERMINATE)
        lowerboundvalue = getattr(self, 'LowerBoundValue', INDETERMINATE)
        assert (not exists(upperboundvalue) or not exists(lowerboundvalue) or typeof(upperboundvalue) == typeof(lowerboundvalue)) is not False

class IfcPropertyBoundedValue_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyBoundedValue'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        upperboundvalue = getattr(self, 'UpperBoundValue', INDETERMINATE)
        lowerboundvalue = getattr(self, 'LowerBoundValue', INDETERMINATE)
        assert (exists(upperboundvalue) or exists(lowerboundvalue)) is not False

class IfcPropertyDependencyRelationship_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyDependencyRelationship'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        dependingproperty = getattr(self, 'DependingProperty', INDETERMINATE)
        dependantproperty = getattr(self, 'DependantProperty', INDETERMINATE)
        assert (dependingproperty != dependantproperty) is not False

class IfcPropertyEnumeratedValue_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyEnumeratedValue'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        enumerationvalues = getattr(self, 'EnumerationValues', INDETERMINATE)
        enumerationreference = getattr(self, 'EnumerationReference', INDETERMINATE)
        assert (not exists(enumerationreference) or sizeof([temp for temp in enumerationvalues if temp in getattr(enumerationreference, 'EnumerationValues', INDETERMINATE)]) == sizeof(enumerationvalues)) is not False

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

class IfcPropertySet_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertySet'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert exists(getattr(self, 'Name', INDETERMINATE)) is not False

class IfcPropertySet_WR32:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertySet'
    RULE_NAME = 'WR32'

    @staticmethod
    def __call__(self):
        hasproperties = getattr(self, 'HasProperties', INDETERMINATE)
        assert IfcUniquePropertyName(hasproperties) is not False

class IfcPropertyTableValue_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyTableValue'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        definingvalues = getattr(self, 'DefiningValues', INDETERMINATE)
        definedvalues = getattr(self, 'DefinedValues', INDETERMINATE)
        assert (sizeof(definingvalues) == sizeof(definedvalues)) is not False

class IfcPropertyTableValue_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyTableValue'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in getattr(self, 'DefiningValues', INDETERMINATE) if typeof(temp) != typeof(express_getitem(getattr(self, 'DefiningValues', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))]) == 0) is not False

class IfcPropertyTableValue_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyTableValue'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in getattr(self, 'DefinedValues', INDETERMINATE) if typeof(temp) != typeof(express_getitem(getattr(self, 'DefinedValues', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))]) == 0) is not False

class IfcProxy_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProxy'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert exists(getattr(self, 'Name', INDETERMINATE)) is not False

class IfcPumpType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPumpType'
    RULE_NAME = 'WR1'

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

class IfcRailing_WR61:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRailing'
    RULE_NAME = 'WR61'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcRailingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcRailingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcRamp_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRamp'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (hiindex(getattr(self, 'IsDecomposedBy', INDETERMINATE)) == 0 or (hiindex(getattr(self, 'IsDecomposedBy', INDETERMINATE)) == 1 and (not exists(getattr(self, 'Representation', INDETERMINATE))))) is not False

class IfcRationalBezierCurve_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRationalBezierCurve'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        weightsdata = getattr(self, 'WeightsData', INDETERMINATE)
        assert (sizeof(weightsdata) == sizeof(getattr(self, 'ControlPointsList', INDETERMINATE))) is not False

class IfcRationalBezierCurve_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRationalBezierCurve'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        assert IfcCurveWeightsPositive(self) is not False

def calc_IfcRationalBezierCurve_Weights(self):
    weightsdata = getattr(self, 'WeightsData', INDETERMINATE)
    return IfcListToArray(weightsdata, 0, getattr(self, 'UpperIndexOnControlPoints', INDETERMINATE))

class IfcRectangleHollowProfileDef_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRectangleHollowProfileDef'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        wallthickness = getattr(self, 'WallThickness', INDETERMINATE)
        assert (wallthickness < getattr(self, 'XDim', INDETERMINATE) / 2.0 and wallthickness < getattr(self, 'YDim', INDETERMINATE) / 2.0) is not False

class IfcRectangleHollowProfileDef_WR32:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRectangleHollowProfileDef'
    RULE_NAME = 'WR32'

    @staticmethod
    def __call__(self):
        outerfilletradius = getattr(self, 'OuterFilletRadius', INDETERMINATE)
        assert (not exists(outerfilletradius) or (outerfilletradius <= getattr(self, 'XDim', INDETERMINATE) / 2.0 and outerfilletradius <= getattr(self, 'YDim', INDETERMINATE) / 2.0)) is not False

class IfcRectangleHollowProfileDef_WR33:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRectangleHollowProfileDef'
    RULE_NAME = 'WR33'

    @staticmethod
    def __call__(self):
        wallthickness = getattr(self, 'WallThickness', INDETERMINATE)
        innerfilletradius = getattr(self, 'InnerFilletRadius', INDETERMINATE)
        assert (not exists(innerfilletradius) or (innerfilletradius <= getattr(self, 'XDim', INDETERMINATE) / 2.0 - wallthickness and innerfilletradius <= getattr(self, 'YDim', INDETERMINATE) / 2.0 - wallthickness)) is not False

class IfcRectangularTrimmedSurface_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRectangularTrimmedSurface'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        u1 = getattr(self, 'U1', INDETERMINATE)
        u2 = getattr(self, 'U2', INDETERMINATE)
        assert (u1 != u2) is not False

class IfcRectangularTrimmedSurface_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRectangularTrimmedSurface'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        v1 = getattr(self, 'V1', INDETERMINATE)
        v2 = getattr(self, 'V2', INDETERMINATE)
        assert (v1 != v2) is not False

class IfcRectangularTrimmedSurface_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRectangularTrimmedSurface'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        basissurface = getattr(self, 'BasisSurface', INDETERMINATE)
        u1 = getattr(self, 'U1', INDETERMINATE)
        u2 = getattr(self, 'U2', INDETERMINATE)
        usense = getattr(self, 'Usense', INDETERMINATE)
        assert ('ifc2x3.ifcelementarysurface' in typeof(basissurface) and (not 'ifc2x3.ifcplane' in typeof(basissurface)) or 'ifc2x3.ifcsurfaceofrevolution' in typeof(basissurface) or usense == (u2 > u1)) is not False

class IfcRectangularTrimmedSurface_WR4:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRectangularTrimmedSurface'
    RULE_NAME = 'WR4'

    @staticmethod
    def __call__(self):
        v1 = getattr(self, 'V1', INDETERMINATE)
        v2 = getattr(self, 'V2', INDETERMINATE)
        vsense = getattr(self, 'Vsense', INDETERMINATE)
        assert (vsense == (v2 > v1)) is not False

def calc_IfcRectangularTrimmedSurface_Dim(self):
    basissurface = getattr(self, 'BasisSurface', INDETERMINATE)
    return getattr(basissurface, 'Dim', INDETERMINATE)

class IfcReinforcingBar_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcReinforcingBar'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        barrole = getattr(self, 'BarRole', INDETERMINATE)
        assert (barrole != getattr(IfcReinforcingBarRoleEnum, 'USERDEFINED', INDETERMINATE) or (barrole == getattr(IfcReinforcingBarRoleEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcRelAssigns_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssigns'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        relatedobjects = getattr(self, 'RelatedObjects', INDETERMINATE)
        relatedobjectstype = getattr(self, 'RelatedObjectsType', INDETERMINATE)
        assert IfcCorrectObjectAssignment(relatedobjectstype, relatedobjects) is not False

class IfcRelAssignsTasks_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssignsTasks'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (hiindex(getattr(self, 'RelatedObjects', INDETERMINATE)) == 1) is not False

class IfcRelAssignsTasks_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssignsTasks'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        assert ('ifc2x3.ifctask' in typeof(express_getitem(getattr(self, 'RelatedObjects', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))) is not False

class IfcRelAssignsTasks_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssignsTasks'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        assert ('ifc2x3.ifcworkcontrol' in typeof(getattr(self, 'RelatingControl', INDETERMINATE))) is not False

class IfcRelAssignsToActor_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssignsToActor'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        relatingactor = getattr(self, 'RelatingActor', INDETERMINATE)
        assert (sizeof([temp for temp in getattr(self, 'RelatedObjects', INDETERMINATE) if relatingactor == temp]) == 0) is not False

class IfcRelAssignsToControl_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssignsToControl'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        relatingcontrol = getattr(self, 'RelatingControl', INDETERMINATE)
        assert (sizeof([temp for temp in getattr(self, 'RelatedObjects', INDETERMINATE) if relatingcontrol == temp]) == 0) is not False

class IfcRelAssignsToGroup_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssignsToGroup'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        relatinggroup = getattr(self, 'RelatingGroup', INDETERMINATE)
        assert (sizeof([temp for temp in getattr(self, 'RelatedObjects', INDETERMINATE) if relatinggroup == temp]) == 0) is not False

class IfcRelAssignsToProcess_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssignsToProcess'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        relatingprocess = getattr(self, 'RelatingProcess', INDETERMINATE)
        assert (sizeof([temp for temp in getattr(self, 'RelatedObjects', INDETERMINATE) if relatingprocess == temp]) == 0) is not False

class IfcRelAssignsToProduct_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssignsToProduct'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        relatingproduct = getattr(self, 'RelatingProduct', INDETERMINATE)
        assert (sizeof([temp for temp in getattr(self, 'RelatedObjects', INDETERMINATE) if relatingproduct == temp]) == 0) is not False

class IfcRelAssignsToResource_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssignsToResource'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        relatingresource = getattr(self, 'RelatingResource', INDETERMINATE)
        assert (sizeof([temp for temp in getattr(self, 'RelatedObjects', INDETERMINATE) if relatingresource == temp]) == 0) is not False

class IfcRelAssociates_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssociates'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        relatedobjects = getattr(self, 'RelatedObjects', INDETERMINATE)
        assert (sizeof([temp for temp in relatedobjects if not ('ifc2x3.ifcobjectdefinition' in typeof(temp) or 'ifc2x3.ifcpropertydefinition' in typeof(temp))]) == 0) is not False

class IfcRelAssociatesMaterial_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssociatesMaterial'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in getattr(self, 'RelatedObjects', INDETERMINATE) if 'ifc2x3.ifcfeatureelementsubtraction' in typeof(temp) or 'ifc2x3.ifcvirtualelement' in typeof(temp)]) == 0) is not False

class IfcRelAssociatesMaterial_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssociatesMaterial'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in getattr(self, 'RelatedObjects', INDETERMINATE) if not 'ifc2x3.ifcproduct' in typeof(temp) and (not 'ifc2x3.ifctypeproduct' in typeof(temp))]) == 0) is not False

class IfcRelConnectsElements_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelConnectsElements'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        relatingelement = getattr(self, 'RelatingElement', INDETERMINATE)
        relatedelement = getattr(self, 'RelatedElement', INDETERMINATE)
        assert (relatingelement != relatedelement) is not False

class IfcRelContainedInSpatialStructure_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelContainedInSpatialStructure'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        relatedelements = getattr(self, 'RelatedElements', INDETERMINATE)
        assert (sizeof([temp for temp in relatedelements if 'ifc2x3.ifcspatialstructureelement' in typeof(temp)]) == 0) is not False

class IfcRelDecomposes_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelDecomposes'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        relatingobject = getattr(self, 'RelatingObject', INDETERMINATE)
        relatedobjects = getattr(self, 'RelatedObjects', INDETERMINATE)
        assert (sizeof([temp for temp in relatedobjects if relatingobject == temp]) == 0) is not False

class IfcRelNests_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelNests'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in getattr(self, 'RelatedObjects', INDETERMINATE) if not typeof(getattr(self, 'RelatingObject', INDETERMINATE)) == typeof(temp)]) == 0) is not False

class IfcRelOverridesProperties_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelOverridesProperties'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (sizeof(getattr(self, 'RelatedObjects', INDETERMINATE)) == 1) is not False

class IfcRelReferencedInSpatialStructure_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelReferencedInSpatialStructure'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        relatedelements = getattr(self, 'RelatedElements', INDETERMINATE)
        assert (sizeof([temp for temp in relatedelements if 'ifc2x3.ifcspatialstructureelement' in typeof(temp)]) == 0) is not False

class IfcRelSchedulesCostItems_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelSchedulesCostItems'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in getattr(self, 'RelatedObjects', INDETERMINATE) if not 'ifc2x3.ifccostitem' in typeof(temp)]) == 0) is not False

class IfcRelSchedulesCostItems_WR12:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelSchedulesCostItems'
    RULE_NAME = 'WR12'

    @staticmethod
    def __call__(self):
        assert ('ifc2x3.ifccostschedule' in typeof(getattr(self, 'RelatingControl', INDETERMINATE))) is not False

class IfcRelSequence_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelSequence'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        relatingprocess = getattr(self, 'RelatingProcess', INDETERMINATE)
        relatedprocess = getattr(self, 'RelatedProcess', INDETERMINATE)
        assert (relatingprocess != relatedprocess) is not False

class IfcRelSpaceBoundary_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelSpaceBoundary'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        relatedbuildingelement = getattr(self, 'RelatedBuildingElement', INDETERMINATE)
        physicalorvirtualboundary = getattr(self, 'PhysicalOrVirtualBoundary', INDETERMINATE)
        assert (physicalorvirtualboundary == getattr(IfcPhysicalOrVirtualEnum, 'Physical', INDETERMINATE) and (exists(relatedbuildingelement) and (not 'ifc2x3.ifcvirtualelement' in typeof(relatedbuildingelement))) or (physicalorvirtualboundary == getattr(IfcPhysicalOrVirtualEnum, 'Virtual', INDETERMINATE) and (not exists(relatedbuildingelement) or 'ifc2x3.ifcvirtualelement' in typeof(relatedbuildingelement))) or physicalorvirtualboundary == getattr(IfcPhysicalOrVirtualEnum, 'NotDefined', INDETERMINATE)) is not False

class IfcRevolvedAreaSolid_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRevolvedAreaSolid'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        axis = getattr(self, 'Axis', INDETERMINATE)
        assert (express_getitem(getattr(getattr(axis, 'Location', INDETERMINATE), 'Coordinates', INDETERMINATE), 3 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) == 0.0) is not False

class IfcRevolvedAreaSolid_WR32:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRevolvedAreaSolid'
    RULE_NAME = 'WR32'

    @staticmethod
    def __call__(self):
        axis = getattr(self, 'Axis', INDETERMINATE)
        assert (express_getitem(getattr(getattr(axis, 'Z', INDETERMINATE), 'DirectionRatios', INDETERMINATE), 3 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) == 0.0) is not False

def calc_IfcRevolvedAreaSolid_AxisLine(self):
    axis = getattr(self, 'Axis', INDETERMINATE)
    return IfcLine(Pnt=getattr(axis, 'Location', INDETERMINATE), Dir=IfcVector(Orientation=getattr(axis, 'Z', INDETERMINATE), Magnitude=1.0))

class IfcRoof_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRoof'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (hiindex(getattr(self, 'IsDecomposedBy', INDETERMINATE)) == 0 or (hiindex(getattr(self, 'IsDecomposedBy', INDETERMINATE)) == 1 and (not exists(getattr(self, 'Representation', INDETERMINATE))))) is not False

class IfcRoundedRectangleProfileDef_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRoundedRectangleProfileDef'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        roundingradius = getattr(self, 'RoundingRadius', INDETERMINATE)
        assert (roundingradius <= getattr(self, 'XDim', INDETERMINATE) / 2.0 and roundingradius <= getattr(self, 'YDim', INDETERMINATE) / 2.0) is not False

def calc_IfcSIUnit_Dimensions(self):
    return IfcDimensionsForSiUnit(getattr(self, 'Name', INDETERMINATE))

class IfcSectionedSpine_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSectionedSpine'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        crosssections = getattr(self, 'CrossSections', INDETERMINATE)
        crosssectionpositions = getattr(self, 'CrossSectionPositions', INDETERMINATE)
        assert (sizeof(crosssections) == sizeof(crosssectionpositions)) is not False

class IfcSectionedSpine_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSectionedSpine'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        crosssections = getattr(self, 'CrossSections', INDETERMINATE)
        assert (sizeof([temp for temp in crosssections if getattr(express_getitem(crosssections, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'ProfileType', INDETERMINATE) != getattr(temp, 'ProfileType', INDETERMINATE)]) == 0) is not False

class IfcSectionedSpine_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSectionedSpine'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        spinecurve = getattr(self, 'SpineCurve', INDETERMINATE)
        assert (getattr(spinecurve, 'Dim', INDETERMINATE) == 3) is not False

def calc_IfcSectionedSpine_Dim(self):
    return 3

class IfcServiceLifeFactor_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcServiceLifeFactor'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not predefinedtype == getattr(IfcServiceLifeFactorTypeEnum, 'USERDEFINED', INDETERMINATE) or exists(getattr(self, 'ObjectType', INDETERMINATE))) is not False

class IfcShapeModel_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcShapeModel'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        ofshapeaspect = getattr(self, 'OfShapeAspect', INDETERMINATE)
        assert (sizeof(getattr(self, 'OfProductRepresentation', INDETERMINATE)) == 1) ^ (sizeof(getattr(self, 'RepresentationMap', INDETERMINATE)) == 1) ^ (sizeof(ofshapeaspect) == 1) is not False

class IfcShapeRepresentation_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcShapeRepresentation'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        assert ('ifc2x3.ifcgeometricrepresentationcontext' in typeof(getattr(self, 'ContextOfItems', INDETERMINATE))) is not False

class IfcShapeRepresentation_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcShapeRepresentation'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        items = getattr(self, 'Items', INDETERMINATE)
        assert (sizeof([temp for temp in items if 'ifc2x3.ifctopologicalrepresentationitem' in typeof(temp) and (not sizeof(['ifc2x3.ifcvertexpoint', 'ifc2x3.ifcedgecurve', 'ifc2x3.ifcfacesurface'] * typeof(temp)) == 1)]) == 0) is not False

class IfcShapeRepresentation_WR23:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcShapeRepresentation'
    RULE_NAME = 'WR23'

    @staticmethod
    def __call__(self):
        assert exists(getattr(self, 'RepresentationType', INDETERMINATE)) is not False

class IfcShapeRepresentation_WR24:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcShapeRepresentation'
    RULE_NAME = 'WR24'

    @staticmethod
    def __call__(self):
        assert IfcShapeRepresentationTypes(getattr(self, 'RepresentationType', INDETERMINATE), getattr(self, 'Items', INDETERMINATE)) is not False

def calc_IfcShellBasedSurfaceModel_Dim(self):
    return 3

class IfcSlab_WR61:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSlab'
    RULE_NAME = 'WR61'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != getattr(IfcSlabTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcSlabTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

def calc_IfcSolidModel_Dim(self):
    return 3

class IfcSpaceHeaterType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSpaceHeaterType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcSpaceHeaterTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcSpaceHeaterTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcSpatialStructureElement_WR41:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSpatialStructureElement'
    RULE_NAME = 'WR41'

    @staticmethod
    def __call__(self):
        assert (hiindex(getattr(self, 'Decomposes', INDETERMINATE)) == 1 and 'ifc2x3.ifcrelaggregates' in typeof(express_getitem(getattr(self, 'Decomposes', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and ('ifc2x3.ifcproject' in typeof(getattr(express_getitem(getattr(self, 'Decomposes', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingObject', INDETERMINATE)) or 'ifc2x3.ifcspatialstructureelement' in typeof(getattr(express_getitem(getattr(self, 'Decomposes', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingObject', INDETERMINATE)))) is not False

class IfcStair_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStair'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (hiindex(getattr(self, 'IsDecomposedBy', INDETERMINATE)) == 0 or (hiindex(getattr(self, 'IsDecomposedBy', INDETERMINATE)) == 1 and (not exists(getattr(self, 'Representation', INDETERMINATE))))) is not False

class IfcStructuralLinearAction_WR61:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralLinearAction'
    RULE_NAME = 'WR61'

    @staticmethod
    def __call__(self):
        assert (sizeof(['ifc2x3.ifcstructuralloadlinearforce', 'ifc2x3.ifcstructuralloadtemperature'] * typeof(getattr(self, 'AppliedLoad', INDETERMINATE))) == 1) is not False

def calc_IfcStructuralLinearActionVarying_VaryingAppliedLoads(self):
    subsequentappliedloads = getattr(self, 'SubsequentAppliedLoads', INDETERMINATE)
    return IfcAddToBeginOfList(getattr(self, 'AppliedLoad', INDETERMINATE), subsequentappliedloads)

class IfcStructuralPlanarAction_WR61:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralPlanarAction'
    RULE_NAME = 'WR61'

    @staticmethod
    def __call__(self):
        assert (sizeof(['ifc2x3.ifcstructuralloadplanarforce', 'ifc2x3.ifcstructuralloadtemperature'] * typeof(getattr(self, 'AppliedLoad', INDETERMINATE))) == 1) is not False

def calc_IfcStructuralPlanarActionVarying_VaryingAppliedLoads(self):
    subsequentappliedloads = getattr(self, 'SubsequentAppliedLoads', INDETERMINATE)
    return IfcAddToBeginOfList(getattr(self, 'AppliedLoad', INDETERMINATE), subsequentappliedloads)

class IfcStructuralPointAction_WR61:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralPointAction'
    RULE_NAME = 'WR61'

    @staticmethod
    def __call__(self):
        assert (sizeof(['ifc2x3.ifcstructuralloadsingleforce', 'ifc2x3.ifcstructuralloadsingledisplacement'] * typeof(getattr(self, 'AppliedLoad', INDETERMINATE))) == 1) is not False

class IfcStructuralPointReaction_WR61:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralPointReaction'
    RULE_NAME = 'WR61'

    @staticmethod
    def __call__(self):
        assert (sizeof(['ifc2x3.ifcstructuralloadsingleforce', 'ifc2x3.ifcstructuralloadsingledisplacement'] * typeof(getattr(self, 'AppliedLoad', INDETERMINATE))) == 1) is not False

class IfcStructuralProfileProperties_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralProfileProperties'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        sheardeformationareay = getattr(self, 'ShearDeformationAreaY', INDETERMINATE)
        assert (not exists(sheardeformationareay) or sheardeformationareay >= 0.0) is not False

class IfcStructuralProfileProperties_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralProfileProperties'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        sheardeformationareaz = getattr(self, 'ShearDeformationAreaZ', INDETERMINATE)
        assert (not exists(sheardeformationareaz) or sheardeformationareaz >= 0.0) is not False

class IfcStructuralSteelProfileProperties_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralSteelProfileProperties'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        shearareay = getattr(self, 'ShearAreaY', INDETERMINATE)
        assert (not exists(shearareay) or shearareay >= 0.0) is not False

class IfcStructuralSteelProfileProperties_WR32:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralSteelProfileProperties'
    RULE_NAME = 'WR32'

    @staticmethod
    def __call__(self):
        shearareaz = getattr(self, 'ShearAreaZ', INDETERMINATE)
        assert (not exists(shearareaz) or shearareaz >= 0.0) is not False

class IfcStructuralSurfaceMemberVarying_WR61:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralSurfaceMemberVarying'
    RULE_NAME = 'WR61'

    @staticmethod
    def __call__(self):
        assert exists(getattr(self, 'Thickness', INDETERMINATE)) is not False

class IfcStructuralSurfaceMemberVarying_WR62:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralSurfaceMemberVarying'
    RULE_NAME = 'WR62'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in getattr(getattr(self, 'VaryingThicknessLocation', INDETERMINATE), 'ShapeRepresentations', INDETERMINATE) if not sizeof(getattr(temp, 'Items', INDETERMINATE)) == 1]) == 0) is not False

class IfcStructuralSurfaceMemberVarying_WR63:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralSurfaceMemberVarying'
    RULE_NAME = 'WR63'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in getattr(getattr(self, 'VaryingThicknessLocation', INDETERMINATE), 'ShapeRepresentations', INDETERMINATE) if not ('ifc2x3.ifccartesianpoint' in typeof(express_getitem(getattr(temp, 'Items', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) or 'ifc2x3.ifcpointonsurface' in typeof(express_getitem(getattr(temp, 'Items', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)))]) == 0) is not False

def calc_IfcStructuralSurfaceMemberVarying_VaryingThickness(self):
    subsequentthickness = getattr(self, 'SubsequentThickness', INDETERMINATE)
    return IfcAddToBeginOfList(getattr(self, 'Thickness', INDETERMINATE), subsequentthickness)

class IfcStructuredDimensionCallout_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuredDimensionCallout'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        contents = getattr(self, 'Contents', INDETERMINATE)
        assert (sizeof([ato for ato in [con for con in getattr(self, 'contents', INDETERMINATE) if 'ifc2x3.ifcannotationtextoccurrence' in typeof(con)] if not getattr(getattr(ato, 'Name', INDETERMINATE), 'lower', INDETERMINATE)() in ['dimensionvalue', 'tolerancevalue', 'unittext', 'prefixtext', 'suffixtext']]) == 0) is not False

class IfcStyledItem_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStyledItem'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        styles = getattr(self, 'Styles', INDETERMINATE)
        assert (sizeof(styles) == 1) is not False

class IfcStyledItem_WR12:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStyledItem'
    RULE_NAME = 'WR12'

    @staticmethod
    def __call__(self):
        item = getattr(self, 'Item', INDETERMINATE)
        assert (not 'ifc2x3.ifcstyleditem' in typeof(item)) is not False

class IfcStyledRepresentation_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStyledRepresentation'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in getattr(self, 'Items', INDETERMINATE) if not 'ifc2x3.ifcstyleditem' in typeof(temp)]) == 0) is not False

class IfcSurfaceOfLinearExtrusion_WR41:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceOfLinearExtrusion'
    RULE_NAME = 'WR41'

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

class IfcSurfaceStyle_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceStyle'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in getattr(self, 'Styles', INDETERMINATE) if 'ifc2x3.ifcsurfacestyleshading' in typeof(style)]) <= 1) is not False

class IfcSurfaceStyle_WR12:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceStyle'
    RULE_NAME = 'WR12'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in getattr(self, 'Styles', INDETERMINATE) if 'ifc2x3.ifcsurfacestylelighting' in typeof(style)]) <= 1) is not False

class IfcSurfaceStyle_WR13:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceStyle'
    RULE_NAME = 'WR13'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in getattr(self, 'Styles', INDETERMINATE) if 'ifc2x3.ifcsurfacestylerefraction' in typeof(style)]) <= 1) is not False

class IfcSurfaceStyle_WR14:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceStyle'
    RULE_NAME = 'WR14'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in getattr(self, 'Styles', INDETERMINATE) if 'ifc2x3.ifcsurfacestylewithtextures' in typeof(style)]) <= 1) is not False

class IfcSurfaceStyle_WR15:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceStyle'
    RULE_NAME = 'WR15'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in getattr(self, 'Styles', INDETERMINATE) if 'ifc2x3.ifcexternallydefinedsurfacestyle' in typeof(style)]) <= 1) is not False

class IfcSweptAreaSolid_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSweptAreaSolid'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        sweptarea = getattr(self, 'SweptArea', INDETERMINATE)
        assert (getattr(sweptarea, 'ProfileType', INDETERMINATE) == getattr(IfcProfileTypeEnum, 'Area', INDETERMINATE)) is not False

class IfcSweptDiskSolid_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSweptDiskSolid'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        directrix = getattr(self, 'Directrix', INDETERMINATE)
        assert (getattr(directrix, 'Dim', INDETERMINATE) == 3) is not False

class IfcSweptDiskSolid_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSweptDiskSolid'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        radius = getattr(self, 'Radius', INDETERMINATE)
        innerradius = getattr(self, 'InnerRadius', INDETERMINATE)
        assert (not exists(innerradius) or radius > innerradius) is not False

class IfcSweptSurface_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSweptSurface'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        sweptcurve = getattr(self, 'SweptCurve', INDETERMINATE)
        assert (not 'ifc2x3.ifcderivedprofiledef' in typeof(sweptcurve)) is not False

class IfcSweptSurface_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSweptSurface'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        sweptcurve = getattr(self, 'SweptCurve', INDETERMINATE)
        assert (getattr(sweptcurve, 'ProfileType', INDETERMINATE) == getattr(IfcProfileTypeEnum, 'Curve', INDETERMINATE)) is not False

def calc_IfcSweptSurface_Dim(self):
    position = getattr(self, 'Position', INDETERMINATE)
    return getattr(position, 'Dim', INDETERMINATE)

class IfcTShapeProfileDef_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTShapeProfileDef'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        depth = getattr(self, 'Depth', INDETERMINATE)
        flangethickness = getattr(self, 'FlangeThickness', INDETERMINATE)
        assert (flangethickness < depth) is not False

class IfcTShapeProfileDef_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTShapeProfileDef'
    RULE_NAME = 'WR2'

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
        rows = getattr(self, 'Rows', INDETERMINATE)
        assert (sizeof([temp for temp in rows if hiindex(getattr(temp, 'RowCells', INDETERMINATE)) != hiindex(getattr(express_getitem(rows, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RowCells', INDETERMINATE))]) == 0) is not False

class IfcTable_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTable'
    RULE_NAME = 'WR3'

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

class IfcTankType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTankType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcTankTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcTankTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcTask_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTask'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in getattr(self, 'Decomposes', INDETERMINATE) if not 'ifc2x3.ifcrelnests' in typeof(temp)]) == 0) is not False

class IfcTask_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTask'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in getattr(self, 'IsDecomposedBy', INDETERMINATE) if not 'ifc2x3.ifcrelnests' in typeof(temp)]) == 0) is not False

class IfcTask_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTask'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        assert exists(getattr(self, 'Name', INDETERMINATE)) is not False

class IfcTelecomAddress_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTelecomAddress'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        telephonenumbers = getattr(self, 'TelephoneNumbers', INDETERMINATE)
        facsimilenumbers = getattr(self, 'FacsimileNumbers', INDETERMINATE)
        pagernumber = getattr(self, 'PagerNumber', INDETERMINATE)
        electronicmailaddresses = getattr(self, 'ElectronicMailAddresses', INDETERMINATE)
        wwwhomepageurl = getattr(self, 'WWWHomePageURL', INDETERMINATE)
        assert (exists(telephonenumbers) or exists(pagernumber) or exists(facsimilenumbers) or exists(electronicmailaddresses) or exists(wwwhomepageurl)) is not False

class IfcTendon_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTendon'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcTendonTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcTendonTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcTextLiteralWithExtent_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTextLiteralWithExtent'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        extent = getattr(self, 'Extent', INDETERMINATE)
        assert (not 'ifc2x3.ifcplanarbox' in typeof(extent)) is not False

class IfcTextStyleFontModel_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTextStyleFontModel'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert ('ifc2x3.ifclengthmeasure' in typeof(getattr(self, 'FontSize', INDETERMINATE)) and getattr(self, 'FontSize', INDETERMINATE) > 0.0) is not False

class IfcTextureMap_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTextureMap'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        assert (sizeof(['ifc2x3.ifcshellbasedsurfacemodel', 'ifc2x3.ifcfacebasedsurfacemodel', 'ifc2x3.ifcfacetedbrep', 'ifc2x3.ifcfacetedbrepwithvoids'] * typeof(getattr(express_getitem(getattr(self, 'AnnotatedSurface', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Item', INDETERMINATE))) >= 1) is not False

class IfcTimeSeriesSchedule_WR41:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTimeSeriesSchedule'
    RULE_NAME = 'WR41'

    @staticmethod
    def __call__(self):
        timeseriesscheduletype = getattr(self, 'TimeSeriesScheduleType', INDETERMINATE)
        assert (not timeseriesscheduletype == getattr(IfcTimeSeriesScheduleTypeEnum, 'USERDEFINED', INDETERMINATE) or exists(getattr(self, 'ObjectType', INDETERMINATE))) is not False

class IfcTopologyRepresentation_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTopologyRepresentation'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in getattr(self, 'Items', INDETERMINATE) if not 'ifc2x3.ifctopologicalrepresentationitem' in typeof(temp)]) == 0) is not False

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

class IfcTrimmedCurve_WR41:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTrimmedCurve'
    RULE_NAME = 'WR41'

    @staticmethod
    def __call__(self):
        trim1 = getattr(self, 'Trim1', INDETERMINATE)
        assert (hiindex(trim1) == 1 or typeof(express_getitem(trim1, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) != typeof(express_getitem(trim1, 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))) is not False

class IfcTrimmedCurve_WR42:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTrimmedCurve'
    RULE_NAME = 'WR42'

    @staticmethod
    def __call__(self):
        trim2 = getattr(self, 'Trim2', INDETERMINATE)
        assert (hiindex(trim2) == 1 or typeof(express_getitem(trim2, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) != typeof(express_getitem(trim2, 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))) is not False

class IfcTrimmedCurve_WR43:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTrimmedCurve'
    RULE_NAME = 'WR43'

    @staticmethod
    def __call__(self):
        basiscurve = getattr(self, 'BasisCurve', INDETERMINATE)
        assert (not 'ifc2x3.ifcboundedcurve' in typeof(basiscurve)) is not False

class IfcTubeBundleType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTubeBundleType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcTubeBundleTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcTubeBundleTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcTypeObject_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTypeObject'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert exists(getattr(self, 'Name', INDETERMINATE)) is not False

class IfcTypeProduct_WR41:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTypeProduct'
    RULE_NAME = 'WR41'

    @staticmethod
    def __call__(self):
        assert (not exists(lambda : express_getitem(getattr(self, 'ObjectTypeOf', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) or sizeof([temp for temp in getattr(express_getitem(getattr(self, 'ObjectTypeOf', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatedObjects', INDETERMINATE) if not 'ifc2x3.ifcproduct' in typeof(temp)]) == 0) is not False

class IfcUShapeProfileDef_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcUShapeProfileDef'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        depth = getattr(self, 'Depth', INDETERMINATE)
        flangethickness = getattr(self, 'FlangeThickness', INDETERMINATE)
        assert (flangethickness < depth / 2.0) is not False

class IfcUShapeProfileDef_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcUShapeProfileDef'
    RULE_NAME = 'WR22'

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

class IfcUnitaryEquipmentType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcUnitaryEquipmentType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcUnitaryEquipmentTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcUnitaryEquipmentTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcValveType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcValveType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcValveTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcValveTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcVector_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcVector'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        magnitude = getattr(self, 'Magnitude', INDETERMINATE)
        assert (magnitude >= 0.0) is not False

def calc_IfcVector_Dim(self):
    orientation = getattr(self, 'Orientation', INDETERMINATE)
    return getattr(orientation, 'Dim', INDETERMINATE)

class IfcVibrationIsolatorType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcVibrationIsolatorType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != getattr(IfcVibrationIsolatorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == getattr(IfcVibrationIsolatorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcWall_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWall'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in getattr(self, 'HasAssociations', INDETERMINATE) if 'ifc2x3.ifcrelassociatesmaterial' in typeof(temp)]) <= 1) is not False

class IfcWallStandardCase_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWallStandardCase'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in usedin(self, 'ifc2x3.ifcrelassociates.relatedobjects') if 'ifc2x3.ifcrelassociatesmaterial' in typeof(temp) and 'ifc2x3.ifcmateriallayersetusage' in typeof(getattr(temp, 'RelatingMaterial', INDETERMINATE))]) == 1) is not False

class IfcWindowLiningProperties_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWindowLiningProperties'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        liningdepth = getattr(self, 'LiningDepth', INDETERMINATE)
        liningthickness = getattr(self, 'LiningThickness', INDETERMINATE)
        assert (not (not exists(liningdepth) and exists(liningthickness))) is not False

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
        assert (exists(lambda : express_getitem(getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and 'ifc2x3.ifcwindowstyle' in typeof(express_getitem(getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))) is not False

class IfcWorkControl_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWorkControl'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        workcontroltype = getattr(self, 'WorkControlType', INDETERMINATE)
        assert (workcontroltype != getattr(IfcWorkControlTypeEnum, 'USERDEFINED', INDETERMINATE) or (workcontroltype == getattr(IfcWorkControlTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(getattr(self, 'UserDefinedControlType', INDETERMINATE)))) is not False

class IfcZShapeProfileDef_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcZShapeProfileDef'
    RULE_NAME = 'WR21'

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
        assert (sizeof([temp for temp in getattr(getattr(self, 'IsGroupedBy', INDETERMINATE), 'RelatedObjects', INDETERMINATE) if not ('ifc2x3.ifczone' in typeof(temp) or 'ifc2x3.ifcspace' in typeof(temp))]) == 0) is not False

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

def IfcAddToBeginOfList(ascalar, alist):
    result = []
    if not exists(ascalar):
        result = alist
    else:
        result = result + ascalar
        if hiindex(alist) >= 1:
            for i in range(1, hiindex(alist) + 1):
                temp = list(result)
                temp[i + 1 - EXPRESS_ONE_BASED_INDEXING] = express_getitem(alist, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)
                result = temp
    return result

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
        if dim == IfcDimensionalExponents(-2, 1, 4, 1, 0, 0, 0):
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
    external = sizeof([style for style in styles if 'ifc2x3.ifcexternallydefinedhatchstyle' in typeof(style)])
    hatching = sizeof([style for style in styles if 'ifc2x3.ifcfillareastylehatching' in typeof(style)])
    tiles = sizeof([style for style in styles if 'ifc2x3.ifcfillareastyletiles' in typeof(style)])
    colour = sizeof([style for style in styles if 'ifc2x3.ifccolour' in typeof(style)])
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
        if 'ifc2x3.ifcgridplacement' in typeof(relplacement):
            return None
        if 'ifc2x3.ifclocalplacement' in typeof(relplacement):
            if 'ifc2x3.ifcaxis2placement2d' in typeof(axisplacement):
                return True
            if 'ifc2x3.ifcaxis2placement3d' in typeof(axisplacement):
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
        count = sizeof([temp for temp in objects if not 'ifc2x3.ifcproduct' in typeof(temp)])
        return count == 0
    elif constraint == getattr(IfcObjectTypeEnum, 'PROCESS', INDETERMINATE):
        count = sizeof([temp for temp in objects if not 'ifc2x3.ifcprocess' in typeof(temp)])
        return count == 0
    elif constraint == getattr(IfcObjectTypeEnum, 'CONTROL', INDETERMINATE):
        count = sizeof([temp for temp in objects if not 'ifc2x3.ifccontrol' in typeof(temp)])
        return count == 0
    elif constraint == getattr(IfcObjectTypeEnum, 'RESOURCE', INDETERMINATE):
        count = sizeof([temp for temp in objects if not 'ifc2x3.ifcresource' in typeof(temp)])
        return count == 0
    elif constraint == getattr(IfcObjectTypeEnum, 'ACTOR', INDETERMINATE):
        count = sizeof([temp for temp in objects if not 'ifc2x3.ifcactor' in typeof(temp)])
        return count == 0
    elif constraint == getattr(IfcObjectTypeEnum, 'GROUP', INDETERMINATE):
        count = sizeof([temp for temp in objects if not 'ifc2x3.ifcgroup' in typeof(temp)])
        return count == 0
    elif constraint == getattr(IfcObjectTypeEnum, 'PROJECT', INDETERMINATE):
        count = sizeof([temp for temp in objects if not 'ifc2x3.ifcproject' in typeof(temp)])
        return count == 0
    else:
        return None

def IfcCorrectUnitAssignment(units):
    namedunitnumber = 0
    derivedunitnumber = 0
    monetaryunitnumber = 0
    namedunitnames = express_set([])
    derivedunitnames = express_set([])
    namedunitnumber = sizeof([temp for temp in units if 'ifc2x3.ifcnamedunit' in typeof(temp) and (not getattr(temp, 'UnitType', INDETERMINATE) == getattr(IfcUnitEnum, 'USERDEFINED', INDETERMINATE))])
    derivedunitnumber = sizeof([temp for temp in units if 'ifc2x3.ifcderivedunit' in typeof(temp) and (not getattr(temp, 'UnitType', INDETERMINATE) == getattr(IfcDerivedUnitEnum, 'USERDEFINED', INDETERMINATE))])
    monetaryunitnumber = sizeof([temp for temp in units if 'ifc2x3.ifcmonetaryunit' in typeof(temp)])
    for i in range(1, sizeof(units) + 1):
        if 'ifc2x3.ifcnamedunit' in typeof(express_getitem(units, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and (not getattr(express_getitem(units, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'UnitType', INDETERMINATE) == getattr(IfcUnitEnum, 'USERDEFINED', INDETERMINATE)):
            namedunitnames = namedunitnames + getattr(express_getitem(units, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'UnitType', INDETERMINATE)
        if 'ifc2x3.ifcderivedunit' in typeof(express_getitem(units, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and (not getattr(express_getitem(units, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'UnitType', INDETERMINATE) == getattr(IfcDerivedUnitEnum, 'USERDEFINED', INDETERMINATE)):
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
    if 'ifc2x3.ifcline' in typeof(curve):
        return getattr(getattr(curve, 'Pnt', INDETERMINATE), 'Dim', INDETERMINATE)
    if 'ifc2x3.ifcconic' in typeof(curve):
        return getattr(getattr(curve, 'Position', INDETERMINATE), 'Dim', INDETERMINATE)
    if 'ifc2x3.ifcpolyline' in typeof(curve):
        return getattr(express_getitem(getattr(curve, 'Points', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)
    if 'ifc2x3.ifctrimmedcurve' in typeof(curve):
        return IfcCurveDim(getattr(curve, 'BasisCurve', INDETERMINATE))
    if 'ifc2x3.ifccompositecurve' in typeof(curve):
        return getattr(express_getitem(getattr(curve, 'Segments', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)
    if 'ifc2x3.ifcbsplinecurve' in typeof(curve):
        return getattr(express_getitem(getattr(curve, 'ControlPointsList', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)
    if 'ifc2x3.ifcoffsetcurve2d' in typeof(curve):
        return 2
    if 'ifc2x3.ifcoffsetcurve3d' in typeof(curve):
        return 3
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
        return IfcDimensionalExponents(-2, -1, 4, 1, 0, 0, 0)
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

def IfcLeapYear(year):
    if year % 4 == 0 and year % 100 != 0 or year % 400 == 0:
        return True
    else:
        return False

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
        ndim = getattr(arg, 'Dim', INDETERMINATE)
        if 'ifc2x3.ifcvector' in typeof(arg):
            v.DirectionRatios = getattr(getattr(arg, 'Orientation', INDETERMINATE), 'DirectionRatios', INDETERMINATE)
            vec.Magnitude = getattr(arg, 'Magnitude', INDETERMINATE)
            vec.Orientation = v
            if getattr(arg, 'Magnitude', INDETERMINATE) == 0.0:
                return None
            else:
                vec.Magnitude = 1.0
        else:
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
            if 'ifc2x3.ifcvector' in typeof(arg):
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
        if 'ifc2x3.ifcvector' in typeof(vec):
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
    if getattr(reptype, 'lower', INDETERMINATE)() == 'curve2d':
        count = sizeof([temp for temp in items if 'ifc2x3.ifccurve' in typeof(temp) and getattr(temp, 'Dim', INDETERMINATE) == 2])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'annotation2d':
        count = sizeof([temp for temp in items if sizeof(typeof(temp) * ['ifc2x3.ifcpoint', 'ifc2x3.ifccurve', 'ifc2x3.ifcgeometriccurveset', 'ifc2x3.ifcannotationfillarea', 'ifc2x3.ifcdefinedsymbol', 'ifc2x3.ifctextliteral', 'ifc2x3.ifcdraughtingcallout']) == 1])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'geometricset':
        count = sizeof([temp for temp in items if 'ifc2x3.ifcgeometricset' in typeof(temp) or 'ifc2x3.ifcpoint' in typeof(temp) or 'ifc2x3.ifccurve' in typeof(temp) or ('ifc2x3.ifcsurface' in typeof(temp))])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'geometriccurveset':
        count = sizeof([temp for temp in items if 'ifc2x3.ifcgeometriccurveset' in typeof(temp) or 'ifc2x3.ifcgeometricset' in typeof(temp) or 'ifc2x3.ifcpoint' in typeof(temp) or ('ifc2x3.ifccurve' in typeof(temp))])
        for i in range(1, hiindex(items) + 1):
            if 'ifc2x3.ifcgeometricset' in typeof(express_getitem(items, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)):
                if sizeof([temp for temp in getattr(express_getitem(items, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Elements', INDETERMINATE) if 'ifc2x3.ifcsurface' in typeof(temp)]) > 0:
                    count = count - 1
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'surfacemodel':
        count = sizeof([temp for temp in items if sizeof(['ifc2x3.ifcshellbasedsurfacemodel', 'ifc2x3.ifcfacebasedsurfacemodel', 'ifc2x3.ifcfacetedbrep', 'ifc2x3.ifcfacetedbrepwithvoids'] * typeof(temp)) >= 1])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'solidmodel':
        count = sizeof([temp for temp in items if 'ifc2x3.ifcsolidmodel' in typeof(temp)])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'sweptsolid':
        count = sizeof([temp for temp in items if 'ifc2x3.ifcsweptareasolid' in typeof(temp)])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'csg':
        count = sizeof([temp for temp in items if 'ifc2x3.ifcbooleanresult' in typeof(temp)])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'clipping':
        count = sizeof([temp for temp in items if 'ifc2x3.ifcbooleanclippingresult' in typeof(temp)])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'advancedsweptsolid':
        count = sizeof([temp for temp in items if 'ifc2x3.ifcsurfacecurvesweptareasolid' in typeof(temp) or 'ifc2x3.ifcsweptdisksolid' in typeof(temp)])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'brep':
        count = sizeof([temp for temp in items if 'ifc2x3.ifcfacetedbrep' in typeof(temp) or 'ifc2x3.ifcfacetedbrepwithvoids' in typeof(temp)])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'boundingbox':
        count = sizeof([temp for temp in items if 'ifc2x3.ifcboundingbox' in typeof(temp)])
        if sizeof(items) > 1:
            count = 0
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'sectionedspine':
        count = sizeof([temp for temp in items if 'ifc2x3.ifcsectionedspine' in typeof(temp)])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'mappedrepresentation':
        count = sizeof([temp for temp in items if 'ifc2x3.ifcmappeditem' in typeof(temp)])
    else:
        return None
    return count == sizeof(items)

def IfcTopologyRepresentationTypes(reptype, items):
    count = 0
    if getattr(reptype, 'lower', INDETERMINATE)() == 'vertex':
        count = sizeof([temp for temp in items if 'ifc2x3.ifcvertex' in typeof(temp)])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'edge':
        count = sizeof([temp for temp in items if 'ifc2x3.ifcedge' in typeof(temp)])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'path':
        count = sizeof([temp for temp in items if 'ifc2x3.ifcpath' in typeof(temp)])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'face':
        count = sizeof([temp for temp in items if 'ifc2x3.ifcface' in typeof(temp)])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'shell':
        count = sizeof([temp for temp in items if 'ifc2x3.ifcopenshell' in typeof(temp) or 'ifc2x3.ifcclosedshell' in typeof(temp)])
    elif getattr(reptype, 'lower', INDETERMINATE)() == 'undefined':
        return True
    else:
        return None
    return count == sizeof(items)

def IfcUniquePropertyName(properties):
    names = express_set([])
    for i in range(1, hiindex(properties) + 1):
        names = names + getattr(express_getitem(properties, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Name', INDETERMINATE)
    return sizeof(names) == sizeof(properties)

def IfcValidCalendarDate(date):
    if not 1 <= getattr(date, 'DayComponent', INDETERMINATE) <= 31:
        return False
    if getattr(date, 'MonthComponent', INDETERMINATE) == 4:
        return 1 <= getattr(date, 'DayComponent', INDETERMINATE) <= 30
    elif getattr(date, 'MonthComponent', INDETERMINATE) == 6:
        return 1 <= getattr(date, 'DayComponent', INDETERMINATE) <= 30
    elif getattr(date, 'MonthComponent', INDETERMINATE) == 9:
        return 1 <= getattr(date, 'DayComponent', INDETERMINATE) <= 30
    elif getattr(date, 'MonthComponent', INDETERMINATE) == 11:
        return 1 <= getattr(date, 'DayComponent', INDETERMINATE) <= 30
    elif getattr(date, 'MonthComponent', INDETERMINATE) == 2:
        if IfcLeapYear(getattr(date, 'YearComponent', INDETERMINATE)):
            return 1 <= getattr(date, 'DayComponent', INDETERMINATE) <= 29
        else:
            return 1 <= getattr(date, 'DayComponent', INDETERMINATE) <= 28
    else:
        return True

def IfcValidTime(time):
    if exists(getattr(time, 'SecondComponent', INDETERMINATE)):
        return exists(getattr(time, 'MinuteComponent', INDETERMINATE))
    else:
        return True

def IfcVectorDifference(arg1, arg2):
    if (not exists(arg1) or not exists(arg2)) or getattr(arg1, 'Dim', INDETERMINATE) != getattr(arg2, 'Dim', INDETERMINATE):
        return None
    else:
        if 'ifc2x3.ifcvector' in typeof(arg1):
            mag1 = getattr(arg1, 'Magnitude', INDETERMINATE)
            vec1 = getattr(arg1, 'Orientation', INDETERMINATE)
        else:
            mag1 = 1.0
            vec1 = arg1
        if 'ifc2x3.ifcvector' in typeof(arg2):
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
        if 'ifc2x3.ifcvector' in typeof(arg1):
            mag1 = getattr(arg1, 'Magnitude', INDETERMINATE)
            vec1 = getattr(arg1, 'Orientation', INDETERMINATE)
        else:
            mag1 = 1.0
            vec1 = arg1
        if 'ifc2x3.ifcvector' in typeof(arg2):
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