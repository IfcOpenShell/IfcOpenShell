import ifcopenshell

def is_indeterminate(v):
    return v is None or type(v).__name__ == 'indeterminate_type'

def exists(v):
    if callable(v):
        try:
            return v() is not None
        except IndexError as e:
            return False
    else:
        return not is_indeterminate(v)

def nvl(v, default):
    return v if not is_indeterminate(v) else default

def is_entity(inst):
    if isinstance(inst, ifcopenshell.entity_instance):
        schema_name = inst.is_a(True).split('.')[0].lower()
        decl = ifcopenshell.ifcopenshell_wrapper.schema_by_name(schema_name).declaration_by_name(inst.is_a())
        return isinstance(decl, ifcopenshell.ifcopenshell_wrapper.entity)
    return False

def express_len(v):
    if isinstance(v, ifcopenshell.entity_instance) and (not is_entity(v)):
        v = v[0]
    elif is_indeterminate(v):
        return INDETERMINATE
    return len(v)
old_range = range

def range(*args):
    if any(map(is_indeterminate, args)):
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
email = IfcActionRequestTypeEnum.EMAIL
fax = IfcActionRequestTypeEnum.FAX
phone = IfcActionRequestTypeEnum.PHONE
post = IfcActionRequestTypeEnum.POST
verbal = IfcActionRequestTypeEnum.VERBAL
userdefined = IfcActionRequestTypeEnum.USERDEFINED
notdefined = IfcActionRequestTypeEnum.NOTDEFINED
IfcActionSourceTypeEnum = enum_namespace()
dead_load_g = IfcActionSourceTypeEnum.DEAD_LOAD_G
completion_g1 = IfcActionSourceTypeEnum.COMPLETION_G1
live_load_q = IfcActionSourceTypeEnum.LIVE_LOAD_Q
snow_s = IfcActionSourceTypeEnum.SNOW_S
wind_w = IfcActionSourceTypeEnum.WIND_W
prestressing_p = IfcActionSourceTypeEnum.PRESTRESSING_P
settlement_u = IfcActionSourceTypeEnum.SETTLEMENT_U
temperature_t = IfcActionSourceTypeEnum.TEMPERATURE_T
earthquake_e = IfcActionSourceTypeEnum.EARTHQUAKE_E
fire = IfcActionSourceTypeEnum.FIRE
impulse = IfcActionSourceTypeEnum.IMPULSE
impact = IfcActionSourceTypeEnum.IMPACT
transport = IfcActionSourceTypeEnum.TRANSPORT
erection = IfcActionSourceTypeEnum.ERECTION
propping = IfcActionSourceTypeEnum.PROPPING
system_imperfection = IfcActionSourceTypeEnum.SYSTEM_IMPERFECTION
shrinkage = IfcActionSourceTypeEnum.SHRINKAGE
creep = IfcActionSourceTypeEnum.CREEP
lack_of_fit = IfcActionSourceTypeEnum.LACK_OF_FIT
buoyancy = IfcActionSourceTypeEnum.BUOYANCY
ice = IfcActionSourceTypeEnum.ICE
current = IfcActionSourceTypeEnum.CURRENT
wave = IfcActionSourceTypeEnum.WAVE
rain = IfcActionSourceTypeEnum.RAIN
brakes = IfcActionSourceTypeEnum.BRAKES
userdefined = IfcActionSourceTypeEnum.USERDEFINED
notdefined = IfcActionSourceTypeEnum.NOTDEFINED
IfcActionTypeEnum = enum_namespace()
permanent_g = IfcActionTypeEnum.PERMANENT_G
variable_q = IfcActionTypeEnum.VARIABLE_Q
extraordinary_a = IfcActionTypeEnum.EXTRAORDINARY_A
userdefined = IfcActionTypeEnum.USERDEFINED
notdefined = IfcActionTypeEnum.NOTDEFINED
IfcActuatorTypeEnum = enum_namespace()
electricactuator = IfcActuatorTypeEnum.ELECTRICACTUATOR
handoperatedactuator = IfcActuatorTypeEnum.HANDOPERATEDACTUATOR
hydraulicactuator = IfcActuatorTypeEnum.HYDRAULICACTUATOR
pneumaticactuator = IfcActuatorTypeEnum.PNEUMATICACTUATOR
thermostaticactuator = IfcActuatorTypeEnum.THERMOSTATICACTUATOR
userdefined = IfcActuatorTypeEnum.USERDEFINED
notdefined = IfcActuatorTypeEnum.NOTDEFINED
IfcAddressTypeEnum = enum_namespace()
office = IfcAddressTypeEnum.OFFICE
site = IfcAddressTypeEnum.SITE
home = IfcAddressTypeEnum.HOME
distributionpoint = IfcAddressTypeEnum.DISTRIBUTIONPOINT
userdefined = IfcAddressTypeEnum.USERDEFINED
IfcAirTerminalBoxTypeEnum = enum_namespace()
constantflow = IfcAirTerminalBoxTypeEnum.CONSTANTFLOW
variableflowpressuredependant = IfcAirTerminalBoxTypeEnum.VARIABLEFLOWPRESSUREDEPENDANT
variableflowpressureindependant = IfcAirTerminalBoxTypeEnum.VARIABLEFLOWPRESSUREINDEPENDANT
userdefined = IfcAirTerminalBoxTypeEnum.USERDEFINED
notdefined = IfcAirTerminalBoxTypeEnum.NOTDEFINED
IfcAirTerminalTypeEnum = enum_namespace()
diffuser = IfcAirTerminalTypeEnum.DIFFUSER
grille = IfcAirTerminalTypeEnum.GRILLE
louvre = IfcAirTerminalTypeEnum.LOUVRE
register = IfcAirTerminalTypeEnum.REGISTER
userdefined = IfcAirTerminalTypeEnum.USERDEFINED
notdefined = IfcAirTerminalTypeEnum.NOTDEFINED
IfcAirToAirHeatRecoveryTypeEnum = enum_namespace()
fixedplatecounterflowexchanger = IfcAirToAirHeatRecoveryTypeEnum.FIXEDPLATECOUNTERFLOWEXCHANGER
fixedplatecrossflowexchanger = IfcAirToAirHeatRecoveryTypeEnum.FIXEDPLATECROSSFLOWEXCHANGER
fixedplateparallelflowexchanger = IfcAirToAirHeatRecoveryTypeEnum.FIXEDPLATEPARALLELFLOWEXCHANGER
rotarywheel = IfcAirToAirHeatRecoveryTypeEnum.ROTARYWHEEL
runaroundcoilloop = IfcAirToAirHeatRecoveryTypeEnum.RUNAROUNDCOILLOOP
heatpipe = IfcAirToAirHeatRecoveryTypeEnum.HEATPIPE
twintowerenthalpyrecoveryloops = IfcAirToAirHeatRecoveryTypeEnum.TWINTOWERENTHALPYRECOVERYLOOPS
thermosiphonsealedtubeheatexchangers = IfcAirToAirHeatRecoveryTypeEnum.THERMOSIPHONSEALEDTUBEHEATEXCHANGERS
thermosiphoncoiltypeheatexchangers = IfcAirToAirHeatRecoveryTypeEnum.THERMOSIPHONCOILTYPEHEATEXCHANGERS
userdefined = IfcAirToAirHeatRecoveryTypeEnum.USERDEFINED
notdefined = IfcAirToAirHeatRecoveryTypeEnum.NOTDEFINED
IfcAlarmTypeEnum = enum_namespace()
bell = IfcAlarmTypeEnum.BELL
breakglassbutton = IfcAlarmTypeEnum.BREAKGLASSBUTTON
light = IfcAlarmTypeEnum.LIGHT
manualpullbox = IfcAlarmTypeEnum.MANUALPULLBOX
siren = IfcAlarmTypeEnum.SIREN
whistle = IfcAlarmTypeEnum.WHISTLE
userdefined = IfcAlarmTypeEnum.USERDEFINED
notdefined = IfcAlarmTypeEnum.NOTDEFINED
IfcAlignmentTypeEnum = enum_namespace()
userdefined = IfcAlignmentTypeEnum.USERDEFINED
notdefined = IfcAlignmentTypeEnum.NOTDEFINED
IfcAnalysisModelTypeEnum = enum_namespace()
in_plane_loading_2d = IfcAnalysisModelTypeEnum.IN_PLANE_LOADING_2D
out_plane_loading_2d = IfcAnalysisModelTypeEnum.OUT_PLANE_LOADING_2D
loading_3d = IfcAnalysisModelTypeEnum.LOADING_3D
userdefined = IfcAnalysisModelTypeEnum.USERDEFINED
notdefined = IfcAnalysisModelTypeEnum.NOTDEFINED
IfcAnalysisTheoryTypeEnum = enum_namespace()
first_order_theory = IfcAnalysisTheoryTypeEnum.FIRST_ORDER_THEORY
second_order_theory = IfcAnalysisTheoryTypeEnum.SECOND_ORDER_THEORY
third_order_theory = IfcAnalysisTheoryTypeEnum.THIRD_ORDER_THEORY
full_nonlinear_theory = IfcAnalysisTheoryTypeEnum.FULL_NONLINEAR_THEORY
userdefined = IfcAnalysisTheoryTypeEnum.USERDEFINED
notdefined = IfcAnalysisTheoryTypeEnum.NOTDEFINED
IfcArithmeticOperatorEnum = enum_namespace()
add = IfcArithmeticOperatorEnum.ADD
divide = IfcArithmeticOperatorEnum.DIVIDE
multiply = IfcArithmeticOperatorEnum.MULTIPLY
subtract = IfcArithmeticOperatorEnum.SUBTRACT
IfcAssemblyPlaceEnum = enum_namespace()
site = IfcAssemblyPlaceEnum.SITE
factory = IfcAssemblyPlaceEnum.FACTORY
notdefined = IfcAssemblyPlaceEnum.NOTDEFINED
IfcAudioVisualApplianceTypeEnum = enum_namespace()
amplifier = IfcAudioVisualApplianceTypeEnum.AMPLIFIER
camera = IfcAudioVisualApplianceTypeEnum.CAMERA
display = IfcAudioVisualApplianceTypeEnum.DISPLAY
microphone = IfcAudioVisualApplianceTypeEnum.MICROPHONE
player = IfcAudioVisualApplianceTypeEnum.PLAYER
projector = IfcAudioVisualApplianceTypeEnum.PROJECTOR
receiver = IfcAudioVisualApplianceTypeEnum.RECEIVER
speaker = IfcAudioVisualApplianceTypeEnum.SPEAKER
switcher = IfcAudioVisualApplianceTypeEnum.SWITCHER
telephone = IfcAudioVisualApplianceTypeEnum.TELEPHONE
tuner = IfcAudioVisualApplianceTypeEnum.TUNER
userdefined = IfcAudioVisualApplianceTypeEnum.USERDEFINED
notdefined = IfcAudioVisualApplianceTypeEnum.NOTDEFINED
IfcBSplineCurveForm = enum_namespace()
polyline_form = IfcBSplineCurveForm.POLYLINE_FORM
circular_arc = IfcBSplineCurveForm.CIRCULAR_ARC
elliptic_arc = IfcBSplineCurveForm.ELLIPTIC_ARC
parabolic_arc = IfcBSplineCurveForm.PARABOLIC_ARC
hyperbolic_arc = IfcBSplineCurveForm.HYPERBOLIC_ARC
unspecified = IfcBSplineCurveForm.UNSPECIFIED
IfcBSplineSurfaceForm = enum_namespace()
plane_surf = IfcBSplineSurfaceForm.PLANE_SURF
cylindrical_surf = IfcBSplineSurfaceForm.CYLINDRICAL_SURF
conical_surf = IfcBSplineSurfaceForm.CONICAL_SURF
spherical_surf = IfcBSplineSurfaceForm.SPHERICAL_SURF
toroidal_surf = IfcBSplineSurfaceForm.TOROIDAL_SURF
surf_of_revolution = IfcBSplineSurfaceForm.SURF_OF_REVOLUTION
ruled_surf = IfcBSplineSurfaceForm.RULED_SURF
generalised_cone = IfcBSplineSurfaceForm.GENERALISED_CONE
quadric_surf = IfcBSplineSurfaceForm.QUADRIC_SURF
surf_of_linear_extrusion = IfcBSplineSurfaceForm.SURF_OF_LINEAR_EXTRUSION
unspecified = IfcBSplineSurfaceForm.UNSPECIFIED
IfcBeamTypeEnum = enum_namespace()
beam = IfcBeamTypeEnum.BEAM
joist = IfcBeamTypeEnum.JOIST
hollowcore = IfcBeamTypeEnum.HOLLOWCORE
lintel = IfcBeamTypeEnum.LINTEL
spandrel = IfcBeamTypeEnum.SPANDREL
t_beam = IfcBeamTypeEnum.T_BEAM
girder_segment = IfcBeamTypeEnum.GIRDER_SEGMENT
diaphragm = IfcBeamTypeEnum.DIAPHRAGM
piercap = IfcBeamTypeEnum.PIERCAP
hatstone = IfcBeamTypeEnum.HATSTONE
cornice = IfcBeamTypeEnum.CORNICE
edgebeam = IfcBeamTypeEnum.EDGEBEAM
userdefined = IfcBeamTypeEnum.USERDEFINED
notdefined = IfcBeamTypeEnum.NOTDEFINED
IfcBearingTypeDisplacementEnum = enum_namespace()
fixed_movement = IfcBearingTypeDisplacementEnum.FIXED_MOVEMENT
guided_longitudinal = IfcBearingTypeDisplacementEnum.GUIDED_LONGITUDINAL
guided_transversal = IfcBearingTypeDisplacementEnum.GUIDED_TRANSVERSAL
free_movement = IfcBearingTypeDisplacementEnum.FREE_MOVEMENT
notdefined = IfcBearingTypeDisplacementEnum.NOTDEFINED
IfcBearingTypeEnum = enum_namespace()
cylindrical = IfcBearingTypeEnum.CYLINDRICAL
spherical = IfcBearingTypeEnum.SPHERICAL
elastomeric = IfcBearingTypeEnum.ELASTOMERIC
pot = IfcBearingTypeEnum.POT
guide = IfcBearingTypeEnum.GUIDE
rocker = IfcBearingTypeEnum.ROCKER
roller = IfcBearingTypeEnum.ROLLER
disk = IfcBearingTypeEnum.DISK
userdefined = IfcBearingTypeEnum.USERDEFINED
notdefined = IfcBearingTypeEnum.NOTDEFINED
IfcBenchmarkEnum = enum_namespace()
greaterthan = IfcBenchmarkEnum.GREATERTHAN
greaterthanorequalto = IfcBenchmarkEnum.GREATERTHANOREQUALTO
lessthan = IfcBenchmarkEnum.LESSTHAN
lessthanorequalto = IfcBenchmarkEnum.LESSTHANOREQUALTO
equalto = IfcBenchmarkEnum.EQUALTO
notequalto = IfcBenchmarkEnum.NOTEQUALTO
includes = IfcBenchmarkEnum.INCLUDES
notincludes = IfcBenchmarkEnum.NOTINCLUDES
includedin = IfcBenchmarkEnum.INCLUDEDIN
notincludedin = IfcBenchmarkEnum.NOTINCLUDEDIN
IfcBoilerTypeEnum = enum_namespace()
water = IfcBoilerTypeEnum.WATER
steam = IfcBoilerTypeEnum.STEAM
userdefined = IfcBoilerTypeEnum.USERDEFINED
notdefined = IfcBoilerTypeEnum.NOTDEFINED
IfcBooleanOperator = enum_namespace()
union = IfcBooleanOperator.UNION
intersection = IfcBooleanOperator.INTERSECTION
difference = IfcBooleanOperator.DIFFERENCE
IfcBridgePartTypeEnum = enum_namespace()
abutment = IfcBridgePartTypeEnum.ABUTMENT
deck = IfcBridgePartTypeEnum.DECK
deck_segment = IfcBridgePartTypeEnum.DECK_SEGMENT
foundation = IfcBridgePartTypeEnum.FOUNDATION
pier = IfcBridgePartTypeEnum.PIER
pier_segment = IfcBridgePartTypeEnum.PIER_SEGMENT
pylon = IfcBridgePartTypeEnum.PYLON
substructure = IfcBridgePartTypeEnum.SUBSTRUCTURE
superstructure = IfcBridgePartTypeEnum.SUPERSTRUCTURE
surfacestructure = IfcBridgePartTypeEnum.SURFACESTRUCTURE
userdefined = IfcBridgePartTypeEnum.USERDEFINED
notdefined = IfcBridgePartTypeEnum.NOTDEFINED
IfcBridgeTypeEnum = enum_namespace()
arched = IfcBridgeTypeEnum.ARCHED
cable_stayed = IfcBridgeTypeEnum.CABLE_STAYED
cantilever = IfcBridgeTypeEnum.CANTILEVER
culvert = IfcBridgeTypeEnum.CULVERT
framework = IfcBridgeTypeEnum.FRAMEWORK
girder = IfcBridgeTypeEnum.GIRDER
suspension = IfcBridgeTypeEnum.SUSPENSION
truss = IfcBridgeTypeEnum.TRUSS
userdefined = IfcBridgeTypeEnum.USERDEFINED
notdefined = IfcBridgeTypeEnum.NOTDEFINED
IfcBuildingElementPartTypeEnum = enum_namespace()
insulation = IfcBuildingElementPartTypeEnum.INSULATION
precastpanel = IfcBuildingElementPartTypeEnum.PRECASTPANEL
apron = IfcBuildingElementPartTypeEnum.APRON
userdefined = IfcBuildingElementPartTypeEnum.USERDEFINED
notdefined = IfcBuildingElementPartTypeEnum.NOTDEFINED
IfcBuildingElementProxyTypeEnum = enum_namespace()
complex = IfcBuildingElementProxyTypeEnum.COMPLEX
element = IfcBuildingElementProxyTypeEnum.ELEMENT
partial = IfcBuildingElementProxyTypeEnum.PARTIAL
provisionforvoid = IfcBuildingElementProxyTypeEnum.PROVISIONFORVOID
provisionforspace = IfcBuildingElementProxyTypeEnum.PROVISIONFORSPACE
userdefined = IfcBuildingElementProxyTypeEnum.USERDEFINED
notdefined = IfcBuildingElementProxyTypeEnum.NOTDEFINED
IfcBuildingSystemTypeEnum = enum_namespace()
fenestration = IfcBuildingSystemTypeEnum.FENESTRATION
foundation = IfcBuildingSystemTypeEnum.FOUNDATION
loadbearing = IfcBuildingSystemTypeEnum.LOADBEARING
outershell = IfcBuildingSystemTypeEnum.OUTERSHELL
shading = IfcBuildingSystemTypeEnum.SHADING
transport = IfcBuildingSystemTypeEnum.TRANSPORT
reinforcing = IfcBuildingSystemTypeEnum.REINFORCING
prestressing = IfcBuildingSystemTypeEnum.PRESTRESSING
userdefined = IfcBuildingSystemTypeEnum.USERDEFINED
notdefined = IfcBuildingSystemTypeEnum.NOTDEFINED
IfcBurnerTypeEnum = enum_namespace()
userdefined = IfcBurnerTypeEnum.USERDEFINED
notdefined = IfcBurnerTypeEnum.NOTDEFINED
IfcCableCarrierFittingTypeEnum = enum_namespace()
bend = IfcCableCarrierFittingTypeEnum.BEND
cross = IfcCableCarrierFittingTypeEnum.CROSS
reducer = IfcCableCarrierFittingTypeEnum.REDUCER
tee = IfcCableCarrierFittingTypeEnum.TEE
userdefined = IfcCableCarrierFittingTypeEnum.USERDEFINED
notdefined = IfcCableCarrierFittingTypeEnum.NOTDEFINED
IfcCableCarrierSegmentTypeEnum = enum_namespace()
cableladdersegment = IfcCableCarrierSegmentTypeEnum.CABLELADDERSEGMENT
cabletraysegment = IfcCableCarrierSegmentTypeEnum.CABLETRAYSEGMENT
cabletrunkingsegment = IfcCableCarrierSegmentTypeEnum.CABLETRUNKINGSEGMENT
conduitsegment = IfcCableCarrierSegmentTypeEnum.CONDUITSEGMENT
userdefined = IfcCableCarrierSegmentTypeEnum.USERDEFINED
notdefined = IfcCableCarrierSegmentTypeEnum.NOTDEFINED
IfcCableFittingTypeEnum = enum_namespace()
connector = IfcCableFittingTypeEnum.CONNECTOR
entry = IfcCableFittingTypeEnum.ENTRY
exit = IfcCableFittingTypeEnum.EXIT
junction = IfcCableFittingTypeEnum.JUNCTION
transition = IfcCableFittingTypeEnum.TRANSITION
userdefined = IfcCableFittingTypeEnum.USERDEFINED
notdefined = IfcCableFittingTypeEnum.NOTDEFINED
IfcCableSegmentTypeEnum = enum_namespace()
busbarsegment = IfcCableSegmentTypeEnum.BUSBARSEGMENT
cablesegment = IfcCableSegmentTypeEnum.CABLESEGMENT
conductorsegment = IfcCableSegmentTypeEnum.CONDUCTORSEGMENT
coresegment = IfcCableSegmentTypeEnum.CORESEGMENT
userdefined = IfcCableSegmentTypeEnum.USERDEFINED
notdefined = IfcCableSegmentTypeEnum.NOTDEFINED
IfcCaissonFoundationTypeEnum = enum_namespace()
well = IfcCaissonFoundationTypeEnum.WELL
caisson = IfcCaissonFoundationTypeEnum.CAISSON
userdefined = IfcCaissonFoundationTypeEnum.USERDEFINED
notdefined = IfcCaissonFoundationTypeEnum.NOTDEFINED
IfcChangeActionEnum = enum_namespace()
nochange = IfcChangeActionEnum.NOCHANGE
modified = IfcChangeActionEnum.MODIFIED
added = IfcChangeActionEnum.ADDED
deleted = IfcChangeActionEnum.DELETED
notdefined = IfcChangeActionEnum.NOTDEFINED
IfcChillerTypeEnum = enum_namespace()
aircooled = IfcChillerTypeEnum.AIRCOOLED
watercooled = IfcChillerTypeEnum.WATERCOOLED
heatrecovery = IfcChillerTypeEnum.HEATRECOVERY
userdefined = IfcChillerTypeEnum.USERDEFINED
notdefined = IfcChillerTypeEnum.NOTDEFINED
IfcChimneyTypeEnum = enum_namespace()
userdefined = IfcChimneyTypeEnum.USERDEFINED
notdefined = IfcChimneyTypeEnum.NOTDEFINED
IfcCoilTypeEnum = enum_namespace()
dxcoolingcoil = IfcCoilTypeEnum.DXCOOLINGCOIL
electricheatingcoil = IfcCoilTypeEnum.ELECTRICHEATINGCOIL
gasheatingcoil = IfcCoilTypeEnum.GASHEATINGCOIL
hydroniccoil = IfcCoilTypeEnum.HYDRONICCOIL
steamheatingcoil = IfcCoilTypeEnum.STEAMHEATINGCOIL
watercoolingcoil = IfcCoilTypeEnum.WATERCOOLINGCOIL
waterheatingcoil = IfcCoilTypeEnum.WATERHEATINGCOIL
userdefined = IfcCoilTypeEnum.USERDEFINED
notdefined = IfcCoilTypeEnum.NOTDEFINED
IfcColumnTypeEnum = enum_namespace()
column = IfcColumnTypeEnum.COLUMN
pilaster = IfcColumnTypeEnum.PILASTER
pierstem = IfcColumnTypeEnum.PIERSTEM
pierstem_segment = IfcColumnTypeEnum.PIERSTEM_SEGMENT
standcolumn = IfcColumnTypeEnum.STANDCOLUMN
userdefined = IfcColumnTypeEnum.USERDEFINED
notdefined = IfcColumnTypeEnum.NOTDEFINED
IfcCommunicationsApplianceTypeEnum = enum_namespace()
antenna = IfcCommunicationsApplianceTypeEnum.ANTENNA
computer = IfcCommunicationsApplianceTypeEnum.COMPUTER
fax = IfcCommunicationsApplianceTypeEnum.FAX
gateway = IfcCommunicationsApplianceTypeEnum.GATEWAY
modem = IfcCommunicationsApplianceTypeEnum.MODEM
networkappliance = IfcCommunicationsApplianceTypeEnum.NETWORKAPPLIANCE
networkbridge = IfcCommunicationsApplianceTypeEnum.NETWORKBRIDGE
networkhub = IfcCommunicationsApplianceTypeEnum.NETWORKHUB
printer = IfcCommunicationsApplianceTypeEnum.PRINTER
repeater = IfcCommunicationsApplianceTypeEnum.REPEATER
router = IfcCommunicationsApplianceTypeEnum.ROUTER
scanner = IfcCommunicationsApplianceTypeEnum.SCANNER
userdefined = IfcCommunicationsApplianceTypeEnum.USERDEFINED
notdefined = IfcCommunicationsApplianceTypeEnum.NOTDEFINED
IfcComplexPropertyTemplateTypeEnum = enum_namespace()
p_complex = IfcComplexPropertyTemplateTypeEnum.P_COMPLEX
q_complex = IfcComplexPropertyTemplateTypeEnum.Q_COMPLEX
IfcCompressorTypeEnum = enum_namespace()
dynamic = IfcCompressorTypeEnum.DYNAMIC
reciprocating = IfcCompressorTypeEnum.RECIPROCATING
rotary = IfcCompressorTypeEnum.ROTARY
scroll = IfcCompressorTypeEnum.SCROLL
trochoidal = IfcCompressorTypeEnum.TROCHOIDAL
singlestage = IfcCompressorTypeEnum.SINGLESTAGE
booster = IfcCompressorTypeEnum.BOOSTER
opentype = IfcCompressorTypeEnum.OPENTYPE
hermetic = IfcCompressorTypeEnum.HERMETIC
semihermetic = IfcCompressorTypeEnum.SEMIHERMETIC
weldedshellhermetic = IfcCompressorTypeEnum.WELDEDSHELLHERMETIC
rollingpiston = IfcCompressorTypeEnum.ROLLINGPISTON
rotaryvane = IfcCompressorTypeEnum.ROTARYVANE
singlescrew = IfcCompressorTypeEnum.SINGLESCREW
twinscrew = IfcCompressorTypeEnum.TWINSCREW
userdefined = IfcCompressorTypeEnum.USERDEFINED
notdefined = IfcCompressorTypeEnum.NOTDEFINED
IfcCondenserTypeEnum = enum_namespace()
aircooled = IfcCondenserTypeEnum.AIRCOOLED
evaporativecooled = IfcCondenserTypeEnum.EVAPORATIVECOOLED
watercooled = IfcCondenserTypeEnum.WATERCOOLED
watercooledbrazedplate = IfcCondenserTypeEnum.WATERCOOLEDBRAZEDPLATE
watercooledshellcoil = IfcCondenserTypeEnum.WATERCOOLEDSHELLCOIL
watercooledshelltube = IfcCondenserTypeEnum.WATERCOOLEDSHELLTUBE
watercooledtubeintube = IfcCondenserTypeEnum.WATERCOOLEDTUBEINTUBE
userdefined = IfcCondenserTypeEnum.USERDEFINED
notdefined = IfcCondenserTypeEnum.NOTDEFINED
IfcConnectionTypeEnum = enum_namespace()
atpath = IfcConnectionTypeEnum.ATPATH
atstart = IfcConnectionTypeEnum.ATSTART
atend = IfcConnectionTypeEnum.ATEND
notdefined = IfcConnectionTypeEnum.NOTDEFINED
IfcConstraintEnum = enum_namespace()
hard = IfcConstraintEnum.HARD
soft = IfcConstraintEnum.SOFT
advisory = IfcConstraintEnum.ADVISORY
userdefined = IfcConstraintEnum.USERDEFINED
notdefined = IfcConstraintEnum.NOTDEFINED
IfcConstructionEquipmentResourceTypeEnum = enum_namespace()
demolishing = IfcConstructionEquipmentResourceTypeEnum.DEMOLISHING
earthmoving = IfcConstructionEquipmentResourceTypeEnum.EARTHMOVING
erecting = IfcConstructionEquipmentResourceTypeEnum.ERECTING
heating = IfcConstructionEquipmentResourceTypeEnum.HEATING
lighting = IfcConstructionEquipmentResourceTypeEnum.LIGHTING
paving = IfcConstructionEquipmentResourceTypeEnum.PAVING
pumping = IfcConstructionEquipmentResourceTypeEnum.PUMPING
transporting = IfcConstructionEquipmentResourceTypeEnum.TRANSPORTING
userdefined = IfcConstructionEquipmentResourceTypeEnum.USERDEFINED
notdefined = IfcConstructionEquipmentResourceTypeEnum.NOTDEFINED
IfcConstructionMaterialResourceTypeEnum = enum_namespace()
aggregates = IfcConstructionMaterialResourceTypeEnum.AGGREGATES
concrete = IfcConstructionMaterialResourceTypeEnum.CONCRETE
drywall = IfcConstructionMaterialResourceTypeEnum.DRYWALL
fuel = IfcConstructionMaterialResourceTypeEnum.FUEL
gypsum = IfcConstructionMaterialResourceTypeEnum.GYPSUM
masonry = IfcConstructionMaterialResourceTypeEnum.MASONRY
metal = IfcConstructionMaterialResourceTypeEnum.METAL
plastic = IfcConstructionMaterialResourceTypeEnum.PLASTIC
wood = IfcConstructionMaterialResourceTypeEnum.WOOD
notdefined = IfcConstructionMaterialResourceTypeEnum.NOTDEFINED
userdefined = IfcConstructionMaterialResourceTypeEnum.USERDEFINED
IfcConstructionProductResourceTypeEnum = enum_namespace()
assembly = IfcConstructionProductResourceTypeEnum.ASSEMBLY
formwork = IfcConstructionProductResourceTypeEnum.FORMWORK
userdefined = IfcConstructionProductResourceTypeEnum.USERDEFINED
notdefined = IfcConstructionProductResourceTypeEnum.NOTDEFINED
IfcControllerTypeEnum = enum_namespace()
floating = IfcControllerTypeEnum.FLOATING
programmable = IfcControllerTypeEnum.PROGRAMMABLE
proportional = IfcControllerTypeEnum.PROPORTIONAL
multiposition = IfcControllerTypeEnum.MULTIPOSITION
twoposition = IfcControllerTypeEnum.TWOPOSITION
userdefined = IfcControllerTypeEnum.USERDEFINED
notdefined = IfcControllerTypeEnum.NOTDEFINED
IfcCooledBeamTypeEnum = enum_namespace()
active = IfcCooledBeamTypeEnum.ACTIVE
passive = IfcCooledBeamTypeEnum.PASSIVE
userdefined = IfcCooledBeamTypeEnum.USERDEFINED
notdefined = IfcCooledBeamTypeEnum.NOTDEFINED
IfcCoolingTowerTypeEnum = enum_namespace()
naturaldraft = IfcCoolingTowerTypeEnum.NATURALDRAFT
mechanicalinduceddraft = IfcCoolingTowerTypeEnum.MECHANICALINDUCEDDRAFT
mechanicalforceddraft = IfcCoolingTowerTypeEnum.MECHANICALFORCEDDRAFT
userdefined = IfcCoolingTowerTypeEnum.USERDEFINED
notdefined = IfcCoolingTowerTypeEnum.NOTDEFINED
IfcCostItemTypeEnum = enum_namespace()
userdefined = IfcCostItemTypeEnum.USERDEFINED
notdefined = IfcCostItemTypeEnum.NOTDEFINED
IfcCostScheduleTypeEnum = enum_namespace()
budget = IfcCostScheduleTypeEnum.BUDGET
costplan = IfcCostScheduleTypeEnum.COSTPLAN
estimate = IfcCostScheduleTypeEnum.ESTIMATE
tender = IfcCostScheduleTypeEnum.TENDER
pricedbillofquantities = IfcCostScheduleTypeEnum.PRICEDBILLOFQUANTITIES
unpricedbillofquantities = IfcCostScheduleTypeEnum.UNPRICEDBILLOFQUANTITIES
scheduleofrates = IfcCostScheduleTypeEnum.SCHEDULEOFRATES
userdefined = IfcCostScheduleTypeEnum.USERDEFINED
notdefined = IfcCostScheduleTypeEnum.NOTDEFINED
IfcCoveringTypeEnum = enum_namespace()
ceiling = IfcCoveringTypeEnum.CEILING
flooring = IfcCoveringTypeEnum.FLOORING
cladding = IfcCoveringTypeEnum.CLADDING
roofing = IfcCoveringTypeEnum.ROOFING
molding = IfcCoveringTypeEnum.MOLDING
skirtingboard = IfcCoveringTypeEnum.SKIRTINGBOARD
insulation = IfcCoveringTypeEnum.INSULATION
membrane = IfcCoveringTypeEnum.MEMBRANE
sleeving = IfcCoveringTypeEnum.SLEEVING
wrapping = IfcCoveringTypeEnum.WRAPPING
coping = IfcCoveringTypeEnum.COPING
userdefined = IfcCoveringTypeEnum.USERDEFINED
notdefined = IfcCoveringTypeEnum.NOTDEFINED
IfcCrewResourceTypeEnum = enum_namespace()
office = IfcCrewResourceTypeEnum.OFFICE
site = IfcCrewResourceTypeEnum.SITE
userdefined = IfcCrewResourceTypeEnum.USERDEFINED
notdefined = IfcCrewResourceTypeEnum.NOTDEFINED
IfcCurtainWallTypeEnum = enum_namespace()
userdefined = IfcCurtainWallTypeEnum.USERDEFINED
notdefined = IfcCurtainWallTypeEnum.NOTDEFINED
IfcCurveInterpolationEnum = enum_namespace()
linear = IfcCurveInterpolationEnum.LINEAR
log_linear = IfcCurveInterpolationEnum.LOG_LINEAR
log_log = IfcCurveInterpolationEnum.LOG_LOG
notdefined = IfcCurveInterpolationEnum.NOTDEFINED
IfcDamperTypeEnum = enum_namespace()
backdraftdamper = IfcDamperTypeEnum.BACKDRAFTDAMPER
balancingdamper = IfcDamperTypeEnum.BALANCINGDAMPER
blastdamper = IfcDamperTypeEnum.BLASTDAMPER
controldamper = IfcDamperTypeEnum.CONTROLDAMPER
firedamper = IfcDamperTypeEnum.FIREDAMPER
firesmokedamper = IfcDamperTypeEnum.FIRESMOKEDAMPER
fumehoodexhaust = IfcDamperTypeEnum.FUMEHOODEXHAUST
gravitydamper = IfcDamperTypeEnum.GRAVITYDAMPER
gravityreliefdamper = IfcDamperTypeEnum.GRAVITYRELIEFDAMPER
reliefdamper = IfcDamperTypeEnum.RELIEFDAMPER
smokedamper = IfcDamperTypeEnum.SMOKEDAMPER
userdefined = IfcDamperTypeEnum.USERDEFINED
notdefined = IfcDamperTypeEnum.NOTDEFINED
IfcDataOriginEnum = enum_namespace()
measured = IfcDataOriginEnum.MEASURED
predicted = IfcDataOriginEnum.PREDICTED
simulated = IfcDataOriginEnum.SIMULATED
userdefined = IfcDataOriginEnum.USERDEFINED
notdefined = IfcDataOriginEnum.NOTDEFINED
IfcDerivedUnitEnum = enum_namespace()
angularvelocityunit = IfcDerivedUnitEnum.ANGULARVELOCITYUNIT
areadensityunit = IfcDerivedUnitEnum.AREADENSITYUNIT
compoundplaneangleunit = IfcDerivedUnitEnum.COMPOUNDPLANEANGLEUNIT
dynamicviscosityunit = IfcDerivedUnitEnum.DYNAMICVISCOSITYUNIT
heatfluxdensityunit = IfcDerivedUnitEnum.HEATFLUXDENSITYUNIT
integercountrateunit = IfcDerivedUnitEnum.INTEGERCOUNTRATEUNIT
isothermalmoisturecapacityunit = IfcDerivedUnitEnum.ISOTHERMALMOISTURECAPACITYUNIT
kinematicviscosityunit = IfcDerivedUnitEnum.KINEMATICVISCOSITYUNIT
linearvelocityunit = IfcDerivedUnitEnum.LINEARVELOCITYUNIT
massdensityunit = IfcDerivedUnitEnum.MASSDENSITYUNIT
massflowrateunit = IfcDerivedUnitEnum.MASSFLOWRATEUNIT
moisturediffusivityunit = IfcDerivedUnitEnum.MOISTUREDIFFUSIVITYUNIT
molecularweightunit = IfcDerivedUnitEnum.MOLECULARWEIGHTUNIT
specificheatcapacityunit = IfcDerivedUnitEnum.SPECIFICHEATCAPACITYUNIT
thermaladmittanceunit = IfcDerivedUnitEnum.THERMALADMITTANCEUNIT
thermalconductanceunit = IfcDerivedUnitEnum.THERMALCONDUCTANCEUNIT
thermalresistanceunit = IfcDerivedUnitEnum.THERMALRESISTANCEUNIT
thermaltransmittanceunit = IfcDerivedUnitEnum.THERMALTRANSMITTANCEUNIT
vaporpermeabilityunit = IfcDerivedUnitEnum.VAPORPERMEABILITYUNIT
volumetricflowrateunit = IfcDerivedUnitEnum.VOLUMETRICFLOWRATEUNIT
rotationalfrequencyunit = IfcDerivedUnitEnum.ROTATIONALFREQUENCYUNIT
torqueunit = IfcDerivedUnitEnum.TORQUEUNIT
momentofinertiaunit = IfcDerivedUnitEnum.MOMENTOFINERTIAUNIT
linearmomentunit = IfcDerivedUnitEnum.LINEARMOMENTUNIT
linearforceunit = IfcDerivedUnitEnum.LINEARFORCEUNIT
planarforceunit = IfcDerivedUnitEnum.PLANARFORCEUNIT
modulusofelasticityunit = IfcDerivedUnitEnum.MODULUSOFELASTICITYUNIT
shearmodulusunit = IfcDerivedUnitEnum.SHEARMODULUSUNIT
linearstiffnessunit = IfcDerivedUnitEnum.LINEARSTIFFNESSUNIT
rotationalstiffnessunit = IfcDerivedUnitEnum.ROTATIONALSTIFFNESSUNIT
modulusofsubgradereactionunit = IfcDerivedUnitEnum.MODULUSOFSUBGRADEREACTIONUNIT
accelerationunit = IfcDerivedUnitEnum.ACCELERATIONUNIT
curvatureunit = IfcDerivedUnitEnum.CURVATUREUNIT
heatingvalueunit = IfcDerivedUnitEnum.HEATINGVALUEUNIT
ionconcentrationunit = IfcDerivedUnitEnum.IONCONCENTRATIONUNIT
luminousintensitydistributionunit = IfcDerivedUnitEnum.LUMINOUSINTENSITYDISTRIBUTIONUNIT
massperlengthunit = IfcDerivedUnitEnum.MASSPERLENGTHUNIT
modulusoflinearsubgradereactionunit = IfcDerivedUnitEnum.MODULUSOFLINEARSUBGRADEREACTIONUNIT
modulusofrotationalsubgradereactionunit = IfcDerivedUnitEnum.MODULUSOFROTATIONALSUBGRADEREACTIONUNIT
phunit = IfcDerivedUnitEnum.PHUNIT
rotationalmassunit = IfcDerivedUnitEnum.ROTATIONALMASSUNIT
sectionareaintegralunit = IfcDerivedUnitEnum.SECTIONAREAINTEGRALUNIT
sectionmodulusunit = IfcDerivedUnitEnum.SECTIONMODULUSUNIT
soundpowerlevelunit = IfcDerivedUnitEnum.SOUNDPOWERLEVELUNIT
soundpowerunit = IfcDerivedUnitEnum.SOUNDPOWERUNIT
soundpressurelevelunit = IfcDerivedUnitEnum.SOUNDPRESSURELEVELUNIT
soundpressureunit = IfcDerivedUnitEnum.SOUNDPRESSUREUNIT
temperaturegradientunit = IfcDerivedUnitEnum.TEMPERATUREGRADIENTUNIT
temperaturerateofchangeunit = IfcDerivedUnitEnum.TEMPERATURERATEOFCHANGEUNIT
thermalexpansioncoefficientunit = IfcDerivedUnitEnum.THERMALEXPANSIONCOEFFICIENTUNIT
warpingconstantunit = IfcDerivedUnitEnum.WARPINGCONSTANTUNIT
warpingmomentunit = IfcDerivedUnitEnum.WARPINGMOMENTUNIT
userdefined = IfcDerivedUnitEnum.USERDEFINED
IfcDirectionSenseEnum = enum_namespace()
positive = IfcDirectionSenseEnum.POSITIVE
negative = IfcDirectionSenseEnum.NEGATIVE
IfcDiscreteAccessoryTypeEnum = enum_namespace()
anchorplate = IfcDiscreteAccessoryTypeEnum.ANCHORPLATE
bracket = IfcDiscreteAccessoryTypeEnum.BRACKET
shoe = IfcDiscreteAccessoryTypeEnum.SHOE
expansion_joint_device = IfcDiscreteAccessoryTypeEnum.EXPANSION_JOINT_DEVICE
userdefined = IfcDiscreteAccessoryTypeEnum.USERDEFINED
notdefined = IfcDiscreteAccessoryTypeEnum.NOTDEFINED
IfcDistributionChamberElementTypeEnum = enum_namespace()
formedduct = IfcDistributionChamberElementTypeEnum.FORMEDDUCT
inspectionchamber = IfcDistributionChamberElementTypeEnum.INSPECTIONCHAMBER
inspectionpit = IfcDistributionChamberElementTypeEnum.INSPECTIONPIT
manhole = IfcDistributionChamberElementTypeEnum.MANHOLE
meterchamber = IfcDistributionChamberElementTypeEnum.METERCHAMBER
sump = IfcDistributionChamberElementTypeEnum.SUMP
trench = IfcDistributionChamberElementTypeEnum.TRENCH
valvechamber = IfcDistributionChamberElementTypeEnum.VALVECHAMBER
userdefined = IfcDistributionChamberElementTypeEnum.USERDEFINED
notdefined = IfcDistributionChamberElementTypeEnum.NOTDEFINED
IfcDistributionPortTypeEnum = enum_namespace()
cable = IfcDistributionPortTypeEnum.CABLE
cablecarrier = IfcDistributionPortTypeEnum.CABLECARRIER
duct = IfcDistributionPortTypeEnum.DUCT
pipe = IfcDistributionPortTypeEnum.PIPE
userdefined = IfcDistributionPortTypeEnum.USERDEFINED
notdefined = IfcDistributionPortTypeEnum.NOTDEFINED
IfcDistributionSystemEnum = enum_namespace()
airconditioning = IfcDistributionSystemEnum.AIRCONDITIONING
audiovisual = IfcDistributionSystemEnum.AUDIOVISUAL
chemical = IfcDistributionSystemEnum.CHEMICAL
chilledwater = IfcDistributionSystemEnum.CHILLEDWATER
communication = IfcDistributionSystemEnum.COMMUNICATION
compressedair = IfcDistributionSystemEnum.COMPRESSEDAIR
condenserwater = IfcDistributionSystemEnum.CONDENSERWATER
control = IfcDistributionSystemEnum.CONTROL
conveying = IfcDistributionSystemEnum.CONVEYING
data = IfcDistributionSystemEnum.DATA
disposal = IfcDistributionSystemEnum.DISPOSAL
domesticcoldwater = IfcDistributionSystemEnum.DOMESTICCOLDWATER
domestichotwater = IfcDistributionSystemEnum.DOMESTICHOTWATER
drainage = IfcDistributionSystemEnum.DRAINAGE
earthing = IfcDistributionSystemEnum.EARTHING
electrical = IfcDistributionSystemEnum.ELECTRICAL
electroacoustic = IfcDistributionSystemEnum.ELECTROACOUSTIC
exhaust = IfcDistributionSystemEnum.EXHAUST
fireprotection = IfcDistributionSystemEnum.FIREPROTECTION
fuel = IfcDistributionSystemEnum.FUEL
gas = IfcDistributionSystemEnum.GAS
hazardous = IfcDistributionSystemEnum.HAZARDOUS
heating = IfcDistributionSystemEnum.HEATING
lighting = IfcDistributionSystemEnum.LIGHTING
lightningprotection = IfcDistributionSystemEnum.LIGHTNINGPROTECTION
municipalsolidwaste = IfcDistributionSystemEnum.MUNICIPALSOLIDWASTE
oil = IfcDistributionSystemEnum.OIL
operational = IfcDistributionSystemEnum.OPERATIONAL
powergeneration = IfcDistributionSystemEnum.POWERGENERATION
rainwater = IfcDistributionSystemEnum.RAINWATER
refrigeration = IfcDistributionSystemEnum.REFRIGERATION
security = IfcDistributionSystemEnum.SECURITY
sewage = IfcDistributionSystemEnum.SEWAGE
signal = IfcDistributionSystemEnum.SIGNAL
stormwater = IfcDistributionSystemEnum.STORMWATER
telephone = IfcDistributionSystemEnum.TELEPHONE
tv = IfcDistributionSystemEnum.TV
vacuum = IfcDistributionSystemEnum.VACUUM
vent = IfcDistributionSystemEnum.VENT
ventilation = IfcDistributionSystemEnum.VENTILATION
wastewater = IfcDistributionSystemEnum.WASTEWATER
watersupply = IfcDistributionSystemEnum.WATERSUPPLY
userdefined = IfcDistributionSystemEnum.USERDEFINED
notdefined = IfcDistributionSystemEnum.NOTDEFINED
IfcDocumentConfidentialityEnum = enum_namespace()
public = IfcDocumentConfidentialityEnum.PUBLIC
restricted = IfcDocumentConfidentialityEnum.RESTRICTED
confidential = IfcDocumentConfidentialityEnum.CONFIDENTIAL
personal = IfcDocumentConfidentialityEnum.PERSONAL
userdefined = IfcDocumentConfidentialityEnum.USERDEFINED
notdefined = IfcDocumentConfidentialityEnum.NOTDEFINED
IfcDocumentStatusEnum = enum_namespace()
draft = IfcDocumentStatusEnum.DRAFT
finaldraft = IfcDocumentStatusEnum.FINALDRAFT
final = IfcDocumentStatusEnum.FINAL
revision = IfcDocumentStatusEnum.REVISION
notdefined = IfcDocumentStatusEnum.NOTDEFINED
IfcDoorPanelOperationEnum = enum_namespace()
swinging = IfcDoorPanelOperationEnum.SWINGING
double_acting = IfcDoorPanelOperationEnum.DOUBLE_ACTING
sliding = IfcDoorPanelOperationEnum.SLIDING
folding = IfcDoorPanelOperationEnum.FOLDING
revolving = IfcDoorPanelOperationEnum.REVOLVING
rollingup = IfcDoorPanelOperationEnum.ROLLINGUP
fixedpanel = IfcDoorPanelOperationEnum.FIXEDPANEL
userdefined = IfcDoorPanelOperationEnum.USERDEFINED
notdefined = IfcDoorPanelOperationEnum.NOTDEFINED
IfcDoorPanelPositionEnum = enum_namespace()
left = IfcDoorPanelPositionEnum.LEFT
middle = IfcDoorPanelPositionEnum.MIDDLE
right = IfcDoorPanelPositionEnum.RIGHT
notdefined = IfcDoorPanelPositionEnum.NOTDEFINED
IfcDoorStyleConstructionEnum = enum_namespace()
aluminium = IfcDoorStyleConstructionEnum.ALUMINIUM
high_grade_steel = IfcDoorStyleConstructionEnum.HIGH_GRADE_STEEL
steel = IfcDoorStyleConstructionEnum.STEEL
wood = IfcDoorStyleConstructionEnum.WOOD
aluminium_wood = IfcDoorStyleConstructionEnum.ALUMINIUM_WOOD
aluminium_plastic = IfcDoorStyleConstructionEnum.ALUMINIUM_PLASTIC
plastic = IfcDoorStyleConstructionEnum.PLASTIC
userdefined = IfcDoorStyleConstructionEnum.USERDEFINED
notdefined = IfcDoorStyleConstructionEnum.NOTDEFINED
IfcDoorStyleOperationEnum = enum_namespace()
single_swing_left = IfcDoorStyleOperationEnum.SINGLE_SWING_LEFT
single_swing_right = IfcDoorStyleOperationEnum.SINGLE_SWING_RIGHT
double_door_single_swing = IfcDoorStyleOperationEnum.DOUBLE_DOOR_SINGLE_SWING
double_door_single_swing_opposite_left = IfcDoorStyleOperationEnum.DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_LEFT
double_door_single_swing_opposite_right = IfcDoorStyleOperationEnum.DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_RIGHT
double_swing_left = IfcDoorStyleOperationEnum.DOUBLE_SWING_LEFT
double_swing_right = IfcDoorStyleOperationEnum.DOUBLE_SWING_RIGHT
double_door_double_swing = IfcDoorStyleOperationEnum.DOUBLE_DOOR_DOUBLE_SWING
sliding_to_left = IfcDoorStyleOperationEnum.SLIDING_TO_LEFT
sliding_to_right = IfcDoorStyleOperationEnum.SLIDING_TO_RIGHT
double_door_sliding = IfcDoorStyleOperationEnum.DOUBLE_DOOR_SLIDING
folding_to_left = IfcDoorStyleOperationEnum.FOLDING_TO_LEFT
folding_to_right = IfcDoorStyleOperationEnum.FOLDING_TO_RIGHT
double_door_folding = IfcDoorStyleOperationEnum.DOUBLE_DOOR_FOLDING
revolving = IfcDoorStyleOperationEnum.REVOLVING
rollingup = IfcDoorStyleOperationEnum.ROLLINGUP
userdefined = IfcDoorStyleOperationEnum.USERDEFINED
notdefined = IfcDoorStyleOperationEnum.NOTDEFINED
IfcDoorTypeEnum = enum_namespace()
door = IfcDoorTypeEnum.DOOR
gate = IfcDoorTypeEnum.GATE
trapdoor = IfcDoorTypeEnum.TRAPDOOR
userdefined = IfcDoorTypeEnum.USERDEFINED
notdefined = IfcDoorTypeEnum.NOTDEFINED
IfcDoorTypeOperationEnum = enum_namespace()
single_swing_left = IfcDoorTypeOperationEnum.SINGLE_SWING_LEFT
single_swing_right = IfcDoorTypeOperationEnum.SINGLE_SWING_RIGHT
double_door_single_swing = IfcDoorTypeOperationEnum.DOUBLE_DOOR_SINGLE_SWING
double_door_single_swing_opposite_left = IfcDoorTypeOperationEnum.DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_LEFT
double_door_single_swing_opposite_right = IfcDoorTypeOperationEnum.DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_RIGHT
double_swing_left = IfcDoorTypeOperationEnum.DOUBLE_SWING_LEFT
double_swing_right = IfcDoorTypeOperationEnum.DOUBLE_SWING_RIGHT
double_door_double_swing = IfcDoorTypeOperationEnum.DOUBLE_DOOR_DOUBLE_SWING
sliding_to_left = IfcDoorTypeOperationEnum.SLIDING_TO_LEFT
sliding_to_right = IfcDoorTypeOperationEnum.SLIDING_TO_RIGHT
double_door_sliding = IfcDoorTypeOperationEnum.DOUBLE_DOOR_SLIDING
folding_to_left = IfcDoorTypeOperationEnum.FOLDING_TO_LEFT
folding_to_right = IfcDoorTypeOperationEnum.FOLDING_TO_RIGHT
double_door_folding = IfcDoorTypeOperationEnum.DOUBLE_DOOR_FOLDING
revolving = IfcDoorTypeOperationEnum.REVOLVING
rollingup = IfcDoorTypeOperationEnum.ROLLINGUP
swing_fixed_left = IfcDoorTypeOperationEnum.SWING_FIXED_LEFT
swing_fixed_right = IfcDoorTypeOperationEnum.SWING_FIXED_RIGHT
userdefined = IfcDoorTypeOperationEnum.USERDEFINED
notdefined = IfcDoorTypeOperationEnum.NOTDEFINED
IfcDuctFittingTypeEnum = enum_namespace()
bend = IfcDuctFittingTypeEnum.BEND
connector = IfcDuctFittingTypeEnum.CONNECTOR
entry = IfcDuctFittingTypeEnum.ENTRY
exit = IfcDuctFittingTypeEnum.EXIT
junction = IfcDuctFittingTypeEnum.JUNCTION
obstruction = IfcDuctFittingTypeEnum.OBSTRUCTION
transition = IfcDuctFittingTypeEnum.TRANSITION
userdefined = IfcDuctFittingTypeEnum.USERDEFINED
notdefined = IfcDuctFittingTypeEnum.NOTDEFINED
IfcDuctSegmentTypeEnum = enum_namespace()
rigidsegment = IfcDuctSegmentTypeEnum.RIGIDSEGMENT
flexiblesegment = IfcDuctSegmentTypeEnum.FLEXIBLESEGMENT
userdefined = IfcDuctSegmentTypeEnum.USERDEFINED
notdefined = IfcDuctSegmentTypeEnum.NOTDEFINED
IfcDuctSilencerTypeEnum = enum_namespace()
flatoval = IfcDuctSilencerTypeEnum.FLATOVAL
rectangular = IfcDuctSilencerTypeEnum.RECTANGULAR
round = IfcDuctSilencerTypeEnum.ROUND
userdefined = IfcDuctSilencerTypeEnum.USERDEFINED
notdefined = IfcDuctSilencerTypeEnum.NOTDEFINED
IfcElectricApplianceTypeEnum = enum_namespace()
dishwasher = IfcElectricApplianceTypeEnum.DISHWASHER
electriccooker = IfcElectricApplianceTypeEnum.ELECTRICCOOKER
freestandingelectricheater = IfcElectricApplianceTypeEnum.FREESTANDINGELECTRICHEATER
freestandingfan = IfcElectricApplianceTypeEnum.FREESTANDINGFAN
freestandingwaterheater = IfcElectricApplianceTypeEnum.FREESTANDINGWATERHEATER
freestandingwatercooler = IfcElectricApplianceTypeEnum.FREESTANDINGWATERCOOLER
freezer = IfcElectricApplianceTypeEnum.FREEZER
fridge_freezer = IfcElectricApplianceTypeEnum.FRIDGE_FREEZER
handdryer = IfcElectricApplianceTypeEnum.HANDDRYER
kitchenmachine = IfcElectricApplianceTypeEnum.KITCHENMACHINE
microwave = IfcElectricApplianceTypeEnum.MICROWAVE
photocopier = IfcElectricApplianceTypeEnum.PHOTOCOPIER
refrigerator = IfcElectricApplianceTypeEnum.REFRIGERATOR
tumbledryer = IfcElectricApplianceTypeEnum.TUMBLEDRYER
vendingmachine = IfcElectricApplianceTypeEnum.VENDINGMACHINE
washingmachine = IfcElectricApplianceTypeEnum.WASHINGMACHINE
userdefined = IfcElectricApplianceTypeEnum.USERDEFINED
notdefined = IfcElectricApplianceTypeEnum.NOTDEFINED
IfcElectricDistributionBoardTypeEnum = enum_namespace()
consumerunit = IfcElectricDistributionBoardTypeEnum.CONSUMERUNIT
distributionboard = IfcElectricDistributionBoardTypeEnum.DISTRIBUTIONBOARD
motorcontrolcentre = IfcElectricDistributionBoardTypeEnum.MOTORCONTROLCENTRE
switchboard = IfcElectricDistributionBoardTypeEnum.SWITCHBOARD
userdefined = IfcElectricDistributionBoardTypeEnum.USERDEFINED
notdefined = IfcElectricDistributionBoardTypeEnum.NOTDEFINED
IfcElectricFlowStorageDeviceTypeEnum = enum_namespace()
battery = IfcElectricFlowStorageDeviceTypeEnum.BATTERY
capacitorbank = IfcElectricFlowStorageDeviceTypeEnum.CAPACITORBANK
harmonicfilter = IfcElectricFlowStorageDeviceTypeEnum.HARMONICFILTER
inductorbank = IfcElectricFlowStorageDeviceTypeEnum.INDUCTORBANK
ups = IfcElectricFlowStorageDeviceTypeEnum.UPS
userdefined = IfcElectricFlowStorageDeviceTypeEnum.USERDEFINED
notdefined = IfcElectricFlowStorageDeviceTypeEnum.NOTDEFINED
IfcElectricGeneratorTypeEnum = enum_namespace()
chp = IfcElectricGeneratorTypeEnum.CHP
enginegenerator = IfcElectricGeneratorTypeEnum.ENGINEGENERATOR
standalone = IfcElectricGeneratorTypeEnum.STANDALONE
userdefined = IfcElectricGeneratorTypeEnum.USERDEFINED
notdefined = IfcElectricGeneratorTypeEnum.NOTDEFINED
IfcElectricMotorTypeEnum = enum_namespace()
dc = IfcElectricMotorTypeEnum.DC
induction = IfcElectricMotorTypeEnum.INDUCTION
polyphase = IfcElectricMotorTypeEnum.POLYPHASE
reluctancesynchronous = IfcElectricMotorTypeEnum.RELUCTANCESYNCHRONOUS
synchronous = IfcElectricMotorTypeEnum.SYNCHRONOUS
userdefined = IfcElectricMotorTypeEnum.USERDEFINED
notdefined = IfcElectricMotorTypeEnum.NOTDEFINED
IfcElectricTimeControlTypeEnum = enum_namespace()
timeclock = IfcElectricTimeControlTypeEnum.TIMECLOCK
timedelay = IfcElectricTimeControlTypeEnum.TIMEDELAY
relay = IfcElectricTimeControlTypeEnum.RELAY
userdefined = IfcElectricTimeControlTypeEnum.USERDEFINED
notdefined = IfcElectricTimeControlTypeEnum.NOTDEFINED
IfcElementAssemblyTypeEnum = enum_namespace()
accessory_assembly = IfcElementAssemblyTypeEnum.ACCESSORY_ASSEMBLY
arch = IfcElementAssemblyTypeEnum.ARCH
beam_grid = IfcElementAssemblyTypeEnum.BEAM_GRID
braced_frame = IfcElementAssemblyTypeEnum.BRACED_FRAME
girder = IfcElementAssemblyTypeEnum.GIRDER
reinforcement_unit = IfcElementAssemblyTypeEnum.REINFORCEMENT_UNIT
rigid_frame = IfcElementAssemblyTypeEnum.RIGID_FRAME
slab_field = IfcElementAssemblyTypeEnum.SLAB_FIELD
truss = IfcElementAssemblyTypeEnum.TRUSS
abutment = IfcElementAssemblyTypeEnum.ABUTMENT
pier = IfcElementAssemblyTypeEnum.PIER
pylon = IfcElementAssemblyTypeEnum.PYLON
cross_bracing = IfcElementAssemblyTypeEnum.CROSS_BRACING
deck = IfcElementAssemblyTypeEnum.DECK
userdefined = IfcElementAssemblyTypeEnum.USERDEFINED
notdefined = IfcElementAssemblyTypeEnum.NOTDEFINED
IfcElementCompositionEnum = enum_namespace()
complex = IfcElementCompositionEnum.COMPLEX
element = IfcElementCompositionEnum.ELEMENT
partial = IfcElementCompositionEnum.PARTIAL
IfcEngineTypeEnum = enum_namespace()
externalcombustion = IfcEngineTypeEnum.EXTERNALCOMBUSTION
internalcombustion = IfcEngineTypeEnum.INTERNALCOMBUSTION
userdefined = IfcEngineTypeEnum.USERDEFINED
notdefined = IfcEngineTypeEnum.NOTDEFINED
IfcEvaporativeCoolerTypeEnum = enum_namespace()
directevaporativerandommediaaircooler = IfcEvaporativeCoolerTypeEnum.DIRECTEVAPORATIVERANDOMMEDIAAIRCOOLER
directevaporativerigidmediaaircooler = IfcEvaporativeCoolerTypeEnum.DIRECTEVAPORATIVERIGIDMEDIAAIRCOOLER
directevaporativeslingerspackagedaircooler = IfcEvaporativeCoolerTypeEnum.DIRECTEVAPORATIVESLINGERSPACKAGEDAIRCOOLER
directevaporativepackagedrotaryaircooler = IfcEvaporativeCoolerTypeEnum.DIRECTEVAPORATIVEPACKAGEDROTARYAIRCOOLER
directevaporativeairwasher = IfcEvaporativeCoolerTypeEnum.DIRECTEVAPORATIVEAIRWASHER
indirectevaporativepackageaircooler = IfcEvaporativeCoolerTypeEnum.INDIRECTEVAPORATIVEPACKAGEAIRCOOLER
indirectevaporativewetcoil = IfcEvaporativeCoolerTypeEnum.INDIRECTEVAPORATIVEWETCOIL
indirectevaporativecoolingtowerorcoilcooler = IfcEvaporativeCoolerTypeEnum.INDIRECTEVAPORATIVECOOLINGTOWERORCOILCOOLER
indirectdirectcombination = IfcEvaporativeCoolerTypeEnum.INDIRECTDIRECTCOMBINATION
userdefined = IfcEvaporativeCoolerTypeEnum.USERDEFINED
notdefined = IfcEvaporativeCoolerTypeEnum.NOTDEFINED
IfcEvaporatorTypeEnum = enum_namespace()
directexpansion = IfcEvaporatorTypeEnum.DIRECTEXPANSION
directexpansionshellandtube = IfcEvaporatorTypeEnum.DIRECTEXPANSIONSHELLANDTUBE
directexpansiontubeintube = IfcEvaporatorTypeEnum.DIRECTEXPANSIONTUBEINTUBE
directexpansionbrazedplate = IfcEvaporatorTypeEnum.DIRECTEXPANSIONBRAZEDPLATE
floodedshellandtube = IfcEvaporatorTypeEnum.FLOODEDSHELLANDTUBE
shellandcoil = IfcEvaporatorTypeEnum.SHELLANDCOIL
userdefined = IfcEvaporatorTypeEnum.USERDEFINED
notdefined = IfcEvaporatorTypeEnum.NOTDEFINED
IfcEventTriggerTypeEnum = enum_namespace()
eventrule = IfcEventTriggerTypeEnum.EVENTRULE
eventmessage = IfcEventTriggerTypeEnum.EVENTMESSAGE
eventtime = IfcEventTriggerTypeEnum.EVENTTIME
eventcomplex = IfcEventTriggerTypeEnum.EVENTCOMPLEX
userdefined = IfcEventTriggerTypeEnum.USERDEFINED
notdefined = IfcEventTriggerTypeEnum.NOTDEFINED
IfcEventTypeEnum = enum_namespace()
startevent = IfcEventTypeEnum.STARTEVENT
endevent = IfcEventTypeEnum.ENDEVENT
intermediateevent = IfcEventTypeEnum.INTERMEDIATEEVENT
userdefined = IfcEventTypeEnum.USERDEFINED
notdefined = IfcEventTypeEnum.NOTDEFINED
IfcExternalSpatialElementTypeEnum = enum_namespace()
external = IfcExternalSpatialElementTypeEnum.EXTERNAL
external_earth = IfcExternalSpatialElementTypeEnum.EXTERNAL_EARTH
external_water = IfcExternalSpatialElementTypeEnum.EXTERNAL_WATER
external_fire = IfcExternalSpatialElementTypeEnum.EXTERNAL_FIRE
userdefined = IfcExternalSpatialElementTypeEnum.USERDEFINED
notdefined = IfcExternalSpatialElementTypeEnum.NOTDEFINED
IfcFanTypeEnum = enum_namespace()
centrifugalforwardcurved = IfcFanTypeEnum.CENTRIFUGALFORWARDCURVED
centrifugalradial = IfcFanTypeEnum.CENTRIFUGALRADIAL
centrifugalbackwardinclinedcurved = IfcFanTypeEnum.CENTRIFUGALBACKWARDINCLINEDCURVED
centrifugalairfoil = IfcFanTypeEnum.CENTRIFUGALAIRFOIL
tubeaxial = IfcFanTypeEnum.TUBEAXIAL
vaneaxial = IfcFanTypeEnum.VANEAXIAL
propelloraxial = IfcFanTypeEnum.PROPELLORAXIAL
userdefined = IfcFanTypeEnum.USERDEFINED
notdefined = IfcFanTypeEnum.NOTDEFINED
IfcFastenerTypeEnum = enum_namespace()
glue = IfcFastenerTypeEnum.GLUE
mortar = IfcFastenerTypeEnum.MORTAR
weld = IfcFastenerTypeEnum.WELD
userdefined = IfcFastenerTypeEnum.USERDEFINED
notdefined = IfcFastenerTypeEnum.NOTDEFINED
IfcFilterTypeEnum = enum_namespace()
airparticlefilter = IfcFilterTypeEnum.AIRPARTICLEFILTER
compressedairfilter = IfcFilterTypeEnum.COMPRESSEDAIRFILTER
odorfilter = IfcFilterTypeEnum.ODORFILTER
oilfilter = IfcFilterTypeEnum.OILFILTER
strainer = IfcFilterTypeEnum.STRAINER
waterfilter = IfcFilterTypeEnum.WATERFILTER
userdefined = IfcFilterTypeEnum.USERDEFINED
notdefined = IfcFilterTypeEnum.NOTDEFINED
IfcFireSuppressionTerminalTypeEnum = enum_namespace()
breechinginlet = IfcFireSuppressionTerminalTypeEnum.BREECHINGINLET
firehydrant = IfcFireSuppressionTerminalTypeEnum.FIREHYDRANT
hosereel = IfcFireSuppressionTerminalTypeEnum.HOSEREEL
sprinkler = IfcFireSuppressionTerminalTypeEnum.SPRINKLER
sprinklerdeflector = IfcFireSuppressionTerminalTypeEnum.SPRINKLERDEFLECTOR
userdefined = IfcFireSuppressionTerminalTypeEnum.USERDEFINED
notdefined = IfcFireSuppressionTerminalTypeEnum.NOTDEFINED
IfcFlowDirectionEnum = enum_namespace()
source = IfcFlowDirectionEnum.SOURCE
sink = IfcFlowDirectionEnum.SINK
sourceandsink = IfcFlowDirectionEnum.SOURCEANDSINK
notdefined = IfcFlowDirectionEnum.NOTDEFINED
IfcFlowInstrumentTypeEnum = enum_namespace()
pressuregauge = IfcFlowInstrumentTypeEnum.PRESSUREGAUGE
thermometer = IfcFlowInstrumentTypeEnum.THERMOMETER
ammeter = IfcFlowInstrumentTypeEnum.AMMETER
frequencymeter = IfcFlowInstrumentTypeEnum.FREQUENCYMETER
powerfactormeter = IfcFlowInstrumentTypeEnum.POWERFACTORMETER
phaseanglemeter = IfcFlowInstrumentTypeEnum.PHASEANGLEMETER
voltmeter_peak = IfcFlowInstrumentTypeEnum.VOLTMETER_PEAK
voltmeter_rms = IfcFlowInstrumentTypeEnum.VOLTMETER_RMS
userdefined = IfcFlowInstrumentTypeEnum.USERDEFINED
notdefined = IfcFlowInstrumentTypeEnum.NOTDEFINED
IfcFlowMeterTypeEnum = enum_namespace()
energymeter = IfcFlowMeterTypeEnum.ENERGYMETER
gasmeter = IfcFlowMeterTypeEnum.GASMETER
oilmeter = IfcFlowMeterTypeEnum.OILMETER
watermeter = IfcFlowMeterTypeEnum.WATERMETER
userdefined = IfcFlowMeterTypeEnum.USERDEFINED
notdefined = IfcFlowMeterTypeEnum.NOTDEFINED
IfcFootingTypeEnum = enum_namespace()
caisson_foundation = IfcFootingTypeEnum.CAISSON_FOUNDATION
footing_beam = IfcFootingTypeEnum.FOOTING_BEAM
pad_footing = IfcFootingTypeEnum.PAD_FOOTING
pile_cap = IfcFootingTypeEnum.PILE_CAP
strip_footing = IfcFootingTypeEnum.STRIP_FOOTING
userdefined = IfcFootingTypeEnum.USERDEFINED
notdefined = IfcFootingTypeEnum.NOTDEFINED
IfcFurnitureTypeEnum = enum_namespace()
chair = IfcFurnitureTypeEnum.CHAIR
table = IfcFurnitureTypeEnum.TABLE
desk = IfcFurnitureTypeEnum.DESK
bed = IfcFurnitureTypeEnum.BED
filecabinet = IfcFurnitureTypeEnum.FILECABINET
shelf = IfcFurnitureTypeEnum.SHELF
sofa = IfcFurnitureTypeEnum.SOFA
userdefined = IfcFurnitureTypeEnum.USERDEFINED
notdefined = IfcFurnitureTypeEnum.NOTDEFINED
IfcGeographicElementTypeEnum = enum_namespace()
terrain = IfcGeographicElementTypeEnum.TERRAIN
soil_boring_point = IfcGeographicElementTypeEnum.SOIL_BORING_POINT
userdefined = IfcGeographicElementTypeEnum.USERDEFINED
notdefined = IfcGeographicElementTypeEnum.NOTDEFINED
IfcGeometricProjectionEnum = enum_namespace()
graph_view = IfcGeometricProjectionEnum.GRAPH_VIEW
sketch_view = IfcGeometricProjectionEnum.SKETCH_VIEW
model_view = IfcGeometricProjectionEnum.MODEL_VIEW
plan_view = IfcGeometricProjectionEnum.PLAN_VIEW
reflected_plan_view = IfcGeometricProjectionEnum.REFLECTED_PLAN_VIEW
section_view = IfcGeometricProjectionEnum.SECTION_VIEW
elevation_view = IfcGeometricProjectionEnum.ELEVATION_VIEW
userdefined = IfcGeometricProjectionEnum.USERDEFINED
notdefined = IfcGeometricProjectionEnum.NOTDEFINED
IfcGlobalOrLocalEnum = enum_namespace()
global_coords = IfcGlobalOrLocalEnum.GLOBAL_COORDS
local_coords = IfcGlobalOrLocalEnum.LOCAL_COORDS
IfcGridTypeEnum = enum_namespace()
rectangular = IfcGridTypeEnum.RECTANGULAR
radial = IfcGridTypeEnum.RADIAL
triangular = IfcGridTypeEnum.TRIANGULAR
irregular = IfcGridTypeEnum.IRREGULAR
userdefined = IfcGridTypeEnum.USERDEFINED
notdefined = IfcGridTypeEnum.NOTDEFINED
IfcHeatExchangerTypeEnum = enum_namespace()
plate = IfcHeatExchangerTypeEnum.PLATE
shellandtube = IfcHeatExchangerTypeEnum.SHELLANDTUBE
userdefined = IfcHeatExchangerTypeEnum.USERDEFINED
notdefined = IfcHeatExchangerTypeEnum.NOTDEFINED
IfcHumidifierTypeEnum = enum_namespace()
steaminjection = IfcHumidifierTypeEnum.STEAMINJECTION
adiabaticairwasher = IfcHumidifierTypeEnum.ADIABATICAIRWASHER
adiabaticpan = IfcHumidifierTypeEnum.ADIABATICPAN
adiabaticwettedelement = IfcHumidifierTypeEnum.ADIABATICWETTEDELEMENT
adiabaticatomizing = IfcHumidifierTypeEnum.ADIABATICATOMIZING
adiabaticultrasonic = IfcHumidifierTypeEnum.ADIABATICULTRASONIC
adiabaticrigidmedia = IfcHumidifierTypeEnum.ADIABATICRIGIDMEDIA
adiabaticcompressedairnozzle = IfcHumidifierTypeEnum.ADIABATICCOMPRESSEDAIRNOZZLE
assistedelectric = IfcHumidifierTypeEnum.ASSISTEDELECTRIC
assistednaturalgas = IfcHumidifierTypeEnum.ASSISTEDNATURALGAS
assistedpropane = IfcHumidifierTypeEnum.ASSISTEDPROPANE
assistedbutane = IfcHumidifierTypeEnum.ASSISTEDBUTANE
assistedsteam = IfcHumidifierTypeEnum.ASSISTEDSTEAM
userdefined = IfcHumidifierTypeEnum.USERDEFINED
notdefined = IfcHumidifierTypeEnum.NOTDEFINED
IfcInterceptorTypeEnum = enum_namespace()
cyclonic = IfcInterceptorTypeEnum.CYCLONIC
grease = IfcInterceptorTypeEnum.GREASE
oil = IfcInterceptorTypeEnum.OIL
petrol = IfcInterceptorTypeEnum.PETROL
userdefined = IfcInterceptorTypeEnum.USERDEFINED
notdefined = IfcInterceptorTypeEnum.NOTDEFINED
IfcInternalOrExternalEnum = enum_namespace()
internal = IfcInternalOrExternalEnum.INTERNAL
external = IfcInternalOrExternalEnum.EXTERNAL
external_earth = IfcInternalOrExternalEnum.EXTERNAL_EARTH
external_water = IfcInternalOrExternalEnum.EXTERNAL_WATER
external_fire = IfcInternalOrExternalEnum.EXTERNAL_FIRE
notdefined = IfcInternalOrExternalEnum.NOTDEFINED
IfcInventoryTypeEnum = enum_namespace()
assetinventory = IfcInventoryTypeEnum.ASSETINVENTORY
spaceinventory = IfcInventoryTypeEnum.SPACEINVENTORY
furnitureinventory = IfcInventoryTypeEnum.FURNITUREINVENTORY
userdefined = IfcInventoryTypeEnum.USERDEFINED
notdefined = IfcInventoryTypeEnum.NOTDEFINED
IfcJunctionBoxTypeEnum = enum_namespace()
data = IfcJunctionBoxTypeEnum.DATA
power = IfcJunctionBoxTypeEnum.POWER
userdefined = IfcJunctionBoxTypeEnum.USERDEFINED
notdefined = IfcJunctionBoxTypeEnum.NOTDEFINED
IfcKnotType = enum_namespace()
uniform_knots = IfcKnotType.UNIFORM_KNOTS
quasi_uniform_knots = IfcKnotType.QUASI_UNIFORM_KNOTS
piecewise_bezier_knots = IfcKnotType.PIECEWISE_BEZIER_KNOTS
unspecified = IfcKnotType.UNSPECIFIED
IfcLaborResourceTypeEnum = enum_namespace()
administration = IfcLaborResourceTypeEnum.ADMINISTRATION
carpentry = IfcLaborResourceTypeEnum.CARPENTRY
cleaning = IfcLaborResourceTypeEnum.CLEANING
concrete = IfcLaborResourceTypeEnum.CONCRETE
drywall = IfcLaborResourceTypeEnum.DRYWALL
electric = IfcLaborResourceTypeEnum.ELECTRIC
finishing = IfcLaborResourceTypeEnum.FINISHING
flooring = IfcLaborResourceTypeEnum.FLOORING
general = IfcLaborResourceTypeEnum.GENERAL
hvac = IfcLaborResourceTypeEnum.HVAC
landscaping = IfcLaborResourceTypeEnum.LANDSCAPING
masonry = IfcLaborResourceTypeEnum.MASONRY
painting = IfcLaborResourceTypeEnum.PAINTING
paving = IfcLaborResourceTypeEnum.PAVING
plumbing = IfcLaborResourceTypeEnum.PLUMBING
roofing = IfcLaborResourceTypeEnum.ROOFING
sitegrading = IfcLaborResourceTypeEnum.SITEGRADING
steelwork = IfcLaborResourceTypeEnum.STEELWORK
surveying = IfcLaborResourceTypeEnum.SURVEYING
userdefined = IfcLaborResourceTypeEnum.USERDEFINED
notdefined = IfcLaborResourceTypeEnum.NOTDEFINED
IfcLampTypeEnum = enum_namespace()
compactfluorescent = IfcLampTypeEnum.COMPACTFLUORESCENT
fluorescent = IfcLampTypeEnum.FLUORESCENT
halogen = IfcLampTypeEnum.HALOGEN
highpressuremercury = IfcLampTypeEnum.HIGHPRESSUREMERCURY
highpressuresodium = IfcLampTypeEnum.HIGHPRESSURESODIUM
led = IfcLampTypeEnum.LED
metalhalide = IfcLampTypeEnum.METALHALIDE
oled = IfcLampTypeEnum.OLED
tungstenfilament = IfcLampTypeEnum.TUNGSTENFILAMENT
userdefined = IfcLampTypeEnum.USERDEFINED
notdefined = IfcLampTypeEnum.NOTDEFINED
IfcLayerSetDirectionEnum = enum_namespace()
axis1 = IfcLayerSetDirectionEnum.AXIS1
axis2 = IfcLayerSetDirectionEnum.AXIS2
axis3 = IfcLayerSetDirectionEnum.AXIS3
IfcLightDistributionCurveEnum = enum_namespace()
type_a = IfcLightDistributionCurveEnum.TYPE_A
type_b = IfcLightDistributionCurveEnum.TYPE_B
type_c = IfcLightDistributionCurveEnum.TYPE_C
notdefined = IfcLightDistributionCurveEnum.NOTDEFINED
IfcLightEmissionSourceEnum = enum_namespace()
compactfluorescent = IfcLightEmissionSourceEnum.COMPACTFLUORESCENT
fluorescent = IfcLightEmissionSourceEnum.FLUORESCENT
highpressuremercury = IfcLightEmissionSourceEnum.HIGHPRESSUREMERCURY
highpressuresodium = IfcLightEmissionSourceEnum.HIGHPRESSURESODIUM
lightemittingdiode = IfcLightEmissionSourceEnum.LIGHTEMITTINGDIODE
lowpressuresodium = IfcLightEmissionSourceEnum.LOWPRESSURESODIUM
lowvoltagehalogen = IfcLightEmissionSourceEnum.LOWVOLTAGEHALOGEN
mainvoltagehalogen = IfcLightEmissionSourceEnum.MAINVOLTAGEHALOGEN
metalhalide = IfcLightEmissionSourceEnum.METALHALIDE
tungstenfilament = IfcLightEmissionSourceEnum.TUNGSTENFILAMENT
notdefined = IfcLightEmissionSourceEnum.NOTDEFINED
IfcLightFixtureTypeEnum = enum_namespace()
pointsource = IfcLightFixtureTypeEnum.POINTSOURCE
directionsource = IfcLightFixtureTypeEnum.DIRECTIONSOURCE
securitylighting = IfcLightFixtureTypeEnum.SECURITYLIGHTING
userdefined = IfcLightFixtureTypeEnum.USERDEFINED
notdefined = IfcLightFixtureTypeEnum.NOTDEFINED
IfcLoadGroupTypeEnum = enum_namespace()
load_group = IfcLoadGroupTypeEnum.LOAD_GROUP
load_case = IfcLoadGroupTypeEnum.LOAD_CASE
load_combination = IfcLoadGroupTypeEnum.LOAD_COMBINATION
userdefined = IfcLoadGroupTypeEnum.USERDEFINED
notdefined = IfcLoadGroupTypeEnum.NOTDEFINED
IfcLogicalOperatorEnum = enum_namespace()
logicaland = IfcLogicalOperatorEnum.LOGICALAND
logicalor = IfcLogicalOperatorEnum.LOGICALOR
logicalxor = IfcLogicalOperatorEnum.LOGICALXOR
logicalnotand = IfcLogicalOperatorEnum.LOGICALNOTAND
logicalnotor = IfcLogicalOperatorEnum.LOGICALNOTOR
IfcMechanicalFastenerTypeEnum = enum_namespace()
anchorbolt = IfcMechanicalFastenerTypeEnum.ANCHORBOLT
bolt = IfcMechanicalFastenerTypeEnum.BOLT
dowel = IfcMechanicalFastenerTypeEnum.DOWEL
nail = IfcMechanicalFastenerTypeEnum.NAIL
nailplate = IfcMechanicalFastenerTypeEnum.NAILPLATE
rivet = IfcMechanicalFastenerTypeEnum.RIVET
screw = IfcMechanicalFastenerTypeEnum.SCREW
shearconnector = IfcMechanicalFastenerTypeEnum.SHEARCONNECTOR
staple = IfcMechanicalFastenerTypeEnum.STAPLE
studshearconnector = IfcMechanicalFastenerTypeEnum.STUDSHEARCONNECTOR
coupler = IfcMechanicalFastenerTypeEnum.COUPLER
userdefined = IfcMechanicalFastenerTypeEnum.USERDEFINED
notdefined = IfcMechanicalFastenerTypeEnum.NOTDEFINED
IfcMedicalDeviceTypeEnum = enum_namespace()
airstation = IfcMedicalDeviceTypeEnum.AIRSTATION
feedairunit = IfcMedicalDeviceTypeEnum.FEEDAIRUNIT
oxygengenerator = IfcMedicalDeviceTypeEnum.OXYGENGENERATOR
oxygenplant = IfcMedicalDeviceTypeEnum.OXYGENPLANT
vacuumstation = IfcMedicalDeviceTypeEnum.VACUUMSTATION
userdefined = IfcMedicalDeviceTypeEnum.USERDEFINED
notdefined = IfcMedicalDeviceTypeEnum.NOTDEFINED
IfcMemberTypeEnum = enum_namespace()
brace = IfcMemberTypeEnum.BRACE
chord = IfcMemberTypeEnum.CHORD
collar = IfcMemberTypeEnum.COLLAR
member = IfcMemberTypeEnum.MEMBER
mullion = IfcMemberTypeEnum.MULLION
plate = IfcMemberTypeEnum.PLATE
post = IfcMemberTypeEnum.POST
purlin = IfcMemberTypeEnum.PURLIN
rafter = IfcMemberTypeEnum.RAFTER
stringer = IfcMemberTypeEnum.STRINGER
strut = IfcMemberTypeEnum.STRUT
stud = IfcMemberTypeEnum.STUD
stiffening_rib = IfcMemberTypeEnum.STIFFENING_RIB
arch_segment = IfcMemberTypeEnum.ARCH_SEGMENT
suspension_cable = IfcMemberTypeEnum.SUSPENSION_CABLE
suspender = IfcMemberTypeEnum.SUSPENDER
stay_cable = IfcMemberTypeEnum.STAY_CABLE
userdefined = IfcMemberTypeEnum.USERDEFINED
notdefined = IfcMemberTypeEnum.NOTDEFINED
IfcMotorConnectionTypeEnum = enum_namespace()
beltdrive = IfcMotorConnectionTypeEnum.BELTDRIVE
coupling = IfcMotorConnectionTypeEnum.COUPLING
directdrive = IfcMotorConnectionTypeEnum.DIRECTDRIVE
userdefined = IfcMotorConnectionTypeEnum.USERDEFINED
notdefined = IfcMotorConnectionTypeEnum.NOTDEFINED
IfcNullStyle = enum_namespace()
null = IfcNullStyle.NULL
IfcObjectTypeEnum = enum_namespace()
product = IfcObjectTypeEnum.PRODUCT
process = IfcObjectTypeEnum.PROCESS
control = IfcObjectTypeEnum.CONTROL
resource = IfcObjectTypeEnum.RESOURCE
actor = IfcObjectTypeEnum.ACTOR
group = IfcObjectTypeEnum.GROUP
project = IfcObjectTypeEnum.PROJECT
notdefined = IfcObjectTypeEnum.NOTDEFINED
IfcObjectiveEnum = enum_namespace()
codecompliance = IfcObjectiveEnum.CODECOMPLIANCE
codewaiver = IfcObjectiveEnum.CODEWAIVER
designintent = IfcObjectiveEnum.DESIGNINTENT
external = IfcObjectiveEnum.EXTERNAL
healthandsafety = IfcObjectiveEnum.HEALTHANDSAFETY
mergeconflict = IfcObjectiveEnum.MERGECONFLICT
modelview = IfcObjectiveEnum.MODELVIEW
parameter = IfcObjectiveEnum.PARAMETER
requirement = IfcObjectiveEnum.REQUIREMENT
specification = IfcObjectiveEnum.SPECIFICATION
triggercondition = IfcObjectiveEnum.TRIGGERCONDITION
userdefined = IfcObjectiveEnum.USERDEFINED
notdefined = IfcObjectiveEnum.NOTDEFINED
IfcOccupantTypeEnum = enum_namespace()
assignee = IfcOccupantTypeEnum.ASSIGNEE
assignor = IfcOccupantTypeEnum.ASSIGNOR
lessee = IfcOccupantTypeEnum.LESSEE
lessor = IfcOccupantTypeEnum.LESSOR
lettingagent = IfcOccupantTypeEnum.LETTINGAGENT
owner = IfcOccupantTypeEnum.OWNER
tenant = IfcOccupantTypeEnum.TENANT
userdefined = IfcOccupantTypeEnum.USERDEFINED
notdefined = IfcOccupantTypeEnum.NOTDEFINED
IfcOpeningElementTypeEnum = enum_namespace()
opening = IfcOpeningElementTypeEnum.OPENING
recess = IfcOpeningElementTypeEnum.RECESS
userdefined = IfcOpeningElementTypeEnum.USERDEFINED
notdefined = IfcOpeningElementTypeEnum.NOTDEFINED
IfcOutletTypeEnum = enum_namespace()
audiovisualoutlet = IfcOutletTypeEnum.AUDIOVISUALOUTLET
communicationsoutlet = IfcOutletTypeEnum.COMMUNICATIONSOUTLET
poweroutlet = IfcOutletTypeEnum.POWEROUTLET
dataoutlet = IfcOutletTypeEnum.DATAOUTLET
telephoneoutlet = IfcOutletTypeEnum.TELEPHONEOUTLET
userdefined = IfcOutletTypeEnum.USERDEFINED
notdefined = IfcOutletTypeEnum.NOTDEFINED
IfcPerformanceHistoryTypeEnum = enum_namespace()
userdefined = IfcPerformanceHistoryTypeEnum.USERDEFINED
notdefined = IfcPerformanceHistoryTypeEnum.NOTDEFINED
IfcPermeableCoveringOperationEnum = enum_namespace()
grill = IfcPermeableCoveringOperationEnum.GRILL
louver = IfcPermeableCoveringOperationEnum.LOUVER
screen = IfcPermeableCoveringOperationEnum.SCREEN
userdefined = IfcPermeableCoveringOperationEnum.USERDEFINED
notdefined = IfcPermeableCoveringOperationEnum.NOTDEFINED
IfcPermitTypeEnum = enum_namespace()
access = IfcPermitTypeEnum.ACCESS
building = IfcPermitTypeEnum.BUILDING
work = IfcPermitTypeEnum.WORK
userdefined = IfcPermitTypeEnum.USERDEFINED
notdefined = IfcPermitTypeEnum.NOTDEFINED
IfcPhysicalOrVirtualEnum = enum_namespace()
physical = IfcPhysicalOrVirtualEnum.PHYSICAL
virtual = IfcPhysicalOrVirtualEnum.VIRTUAL
notdefined = IfcPhysicalOrVirtualEnum.NOTDEFINED
IfcPileConstructionEnum = enum_namespace()
cast_in_place = IfcPileConstructionEnum.CAST_IN_PLACE
composite = IfcPileConstructionEnum.COMPOSITE
precast_concrete = IfcPileConstructionEnum.PRECAST_CONCRETE
prefab_steel = IfcPileConstructionEnum.PREFAB_STEEL
userdefined = IfcPileConstructionEnum.USERDEFINED
notdefined = IfcPileConstructionEnum.NOTDEFINED
IfcPileTypeEnum = enum_namespace()
bored = IfcPileTypeEnum.BORED
driven = IfcPileTypeEnum.DRIVEN
jetgrouting = IfcPileTypeEnum.JETGROUTING
cohesion = IfcPileTypeEnum.COHESION
friction = IfcPileTypeEnum.FRICTION
support = IfcPileTypeEnum.SUPPORT
userdefined = IfcPileTypeEnum.USERDEFINED
notdefined = IfcPileTypeEnum.NOTDEFINED
IfcPipeFittingTypeEnum = enum_namespace()
bend = IfcPipeFittingTypeEnum.BEND
connector = IfcPipeFittingTypeEnum.CONNECTOR
entry = IfcPipeFittingTypeEnum.ENTRY
exit = IfcPipeFittingTypeEnum.EXIT
junction = IfcPipeFittingTypeEnum.JUNCTION
obstruction = IfcPipeFittingTypeEnum.OBSTRUCTION
transition = IfcPipeFittingTypeEnum.TRANSITION
userdefined = IfcPipeFittingTypeEnum.USERDEFINED
notdefined = IfcPipeFittingTypeEnum.NOTDEFINED
IfcPipeSegmentTypeEnum = enum_namespace()
culvert = IfcPipeSegmentTypeEnum.CULVERT
flexiblesegment = IfcPipeSegmentTypeEnum.FLEXIBLESEGMENT
rigidsegment = IfcPipeSegmentTypeEnum.RIGIDSEGMENT
gutter = IfcPipeSegmentTypeEnum.GUTTER
spool = IfcPipeSegmentTypeEnum.SPOOL
userdefined = IfcPipeSegmentTypeEnum.USERDEFINED
notdefined = IfcPipeSegmentTypeEnum.NOTDEFINED
IfcPlateTypeEnum = enum_namespace()
curtain_panel = IfcPlateTypeEnum.CURTAIN_PANEL
sheet = IfcPlateTypeEnum.SHEET
flange_plate = IfcPlateTypeEnum.FLANGE_PLATE
web_plate = IfcPlateTypeEnum.WEB_PLATE
stiffener_plate = IfcPlateTypeEnum.STIFFENER_PLATE
gusset_plate = IfcPlateTypeEnum.GUSSET_PLATE
cover_plate = IfcPlateTypeEnum.COVER_PLATE
splice_plate = IfcPlateTypeEnum.SPLICE_PLATE
base_plate = IfcPlateTypeEnum.BASE_PLATE
userdefined = IfcPlateTypeEnum.USERDEFINED
notdefined = IfcPlateTypeEnum.NOTDEFINED
IfcPreferredSurfaceCurveRepresentation = enum_namespace()
curve3d = IfcPreferredSurfaceCurveRepresentation.CURVE3D
pcurve_s1 = IfcPreferredSurfaceCurveRepresentation.PCURVE_S1
pcurve_s2 = IfcPreferredSurfaceCurveRepresentation.PCURVE_S2
IfcProcedureTypeEnum = enum_namespace()
advice_caution = IfcProcedureTypeEnum.ADVICE_CAUTION
advice_note = IfcProcedureTypeEnum.ADVICE_NOTE
advice_warning = IfcProcedureTypeEnum.ADVICE_WARNING
calibration = IfcProcedureTypeEnum.CALIBRATION
diagnostic = IfcProcedureTypeEnum.DIAGNOSTIC
shutdown = IfcProcedureTypeEnum.SHUTDOWN
startup = IfcProcedureTypeEnum.STARTUP
userdefined = IfcProcedureTypeEnum.USERDEFINED
notdefined = IfcProcedureTypeEnum.NOTDEFINED
IfcProfileTypeEnum = enum_namespace()
curve = IfcProfileTypeEnum.CURVE
area = IfcProfileTypeEnum.AREA
IfcProjectOrderTypeEnum = enum_namespace()
changeorder = IfcProjectOrderTypeEnum.CHANGEORDER
maintenanceworkorder = IfcProjectOrderTypeEnum.MAINTENANCEWORKORDER
moveorder = IfcProjectOrderTypeEnum.MOVEORDER
purchaseorder = IfcProjectOrderTypeEnum.PURCHASEORDER
workorder = IfcProjectOrderTypeEnum.WORKORDER
userdefined = IfcProjectOrderTypeEnum.USERDEFINED
notdefined = IfcProjectOrderTypeEnum.NOTDEFINED
IfcProjectedOrTrueLengthEnum = enum_namespace()
projected_length = IfcProjectedOrTrueLengthEnum.PROJECTED_LENGTH
true_length = IfcProjectedOrTrueLengthEnum.TRUE_LENGTH
IfcProjectionElementTypeEnum = enum_namespace()
blister = IfcProjectionElementTypeEnum.BLISTER
deviator = IfcProjectionElementTypeEnum.DEVIATOR
userdefined = IfcProjectionElementTypeEnum.USERDEFINED
notdefined = IfcProjectionElementTypeEnum.NOTDEFINED
IfcPropertySetTemplateTypeEnum = enum_namespace()
pset_typedrivenonly = IfcPropertySetTemplateTypeEnum.PSET_TYPEDRIVENONLY
pset_typedrivenoverride = IfcPropertySetTemplateTypeEnum.PSET_TYPEDRIVENOVERRIDE
pset_occurrencedriven = IfcPropertySetTemplateTypeEnum.PSET_OCCURRENCEDRIVEN
pset_performancedriven = IfcPropertySetTemplateTypeEnum.PSET_PERFORMANCEDRIVEN
qto_typedrivenonly = IfcPropertySetTemplateTypeEnum.QTO_TYPEDRIVENONLY
qto_typedrivenoverride = IfcPropertySetTemplateTypeEnum.QTO_TYPEDRIVENOVERRIDE
qto_occurrencedriven = IfcPropertySetTemplateTypeEnum.QTO_OCCURRENCEDRIVEN
notdefined = IfcPropertySetTemplateTypeEnum.NOTDEFINED
IfcProtectiveDeviceTrippingUnitTypeEnum = enum_namespace()
electronic = IfcProtectiveDeviceTrippingUnitTypeEnum.ELECTRONIC
electromagnetic = IfcProtectiveDeviceTrippingUnitTypeEnum.ELECTROMAGNETIC
residualcurrent = IfcProtectiveDeviceTrippingUnitTypeEnum.RESIDUALCURRENT
thermal = IfcProtectiveDeviceTrippingUnitTypeEnum.THERMAL
userdefined = IfcProtectiveDeviceTrippingUnitTypeEnum.USERDEFINED
notdefined = IfcProtectiveDeviceTrippingUnitTypeEnum.NOTDEFINED
IfcProtectiveDeviceTypeEnum = enum_namespace()
circuitbreaker = IfcProtectiveDeviceTypeEnum.CIRCUITBREAKER
earthleakagecircuitbreaker = IfcProtectiveDeviceTypeEnum.EARTHLEAKAGECIRCUITBREAKER
earthingswitch = IfcProtectiveDeviceTypeEnum.EARTHINGSWITCH
fusedisconnector = IfcProtectiveDeviceTypeEnum.FUSEDISCONNECTOR
residualcurrentcircuitbreaker = IfcProtectiveDeviceTypeEnum.RESIDUALCURRENTCIRCUITBREAKER
residualcurrentswitch = IfcProtectiveDeviceTypeEnum.RESIDUALCURRENTSWITCH
varistor = IfcProtectiveDeviceTypeEnum.VARISTOR
userdefined = IfcProtectiveDeviceTypeEnum.USERDEFINED
notdefined = IfcProtectiveDeviceTypeEnum.NOTDEFINED
IfcPumpTypeEnum = enum_namespace()
circulator = IfcPumpTypeEnum.CIRCULATOR
endsuction = IfcPumpTypeEnum.ENDSUCTION
splitcase = IfcPumpTypeEnum.SPLITCASE
submersiblepump = IfcPumpTypeEnum.SUBMERSIBLEPUMP
sumppump = IfcPumpTypeEnum.SUMPPUMP
verticalinline = IfcPumpTypeEnum.VERTICALINLINE
verticalturbine = IfcPumpTypeEnum.VERTICALTURBINE
userdefined = IfcPumpTypeEnum.USERDEFINED
notdefined = IfcPumpTypeEnum.NOTDEFINED
IfcRailingTypeEnum = enum_namespace()
handrail = IfcRailingTypeEnum.HANDRAIL
guardrail = IfcRailingTypeEnum.GUARDRAIL
balustrade = IfcRailingTypeEnum.BALUSTRADE
userdefined = IfcRailingTypeEnum.USERDEFINED
notdefined = IfcRailingTypeEnum.NOTDEFINED
IfcRampFlightTypeEnum = enum_namespace()
straight = IfcRampFlightTypeEnum.STRAIGHT
spiral = IfcRampFlightTypeEnum.SPIRAL
userdefined = IfcRampFlightTypeEnum.USERDEFINED
notdefined = IfcRampFlightTypeEnum.NOTDEFINED
IfcRampTypeEnum = enum_namespace()
straight_run_ramp = IfcRampTypeEnum.STRAIGHT_RUN_RAMP
two_straight_run_ramp = IfcRampTypeEnum.TWO_STRAIGHT_RUN_RAMP
quarter_turn_ramp = IfcRampTypeEnum.QUARTER_TURN_RAMP
two_quarter_turn_ramp = IfcRampTypeEnum.TWO_QUARTER_TURN_RAMP
half_turn_ramp = IfcRampTypeEnum.HALF_TURN_RAMP
spiral_ramp = IfcRampTypeEnum.SPIRAL_RAMP
userdefined = IfcRampTypeEnum.USERDEFINED
notdefined = IfcRampTypeEnum.NOTDEFINED
IfcRecurrenceTypeEnum = enum_namespace()
daily = IfcRecurrenceTypeEnum.DAILY
weekly = IfcRecurrenceTypeEnum.WEEKLY
monthly_by_day_of_month = IfcRecurrenceTypeEnum.MONTHLY_BY_DAY_OF_MONTH
monthly_by_position = IfcRecurrenceTypeEnum.MONTHLY_BY_POSITION
by_day_count = IfcRecurrenceTypeEnum.BY_DAY_COUNT
by_weekday_count = IfcRecurrenceTypeEnum.BY_WEEKDAY_COUNT
yearly_by_day_of_month = IfcRecurrenceTypeEnum.YEARLY_BY_DAY_OF_MONTH
yearly_by_position = IfcRecurrenceTypeEnum.YEARLY_BY_POSITION
IfcReferentTypeEnum = enum_namespace()
kilopoint = IfcReferentTypeEnum.KILOPOINT
milepoint = IfcReferentTypeEnum.MILEPOINT
station = IfcReferentTypeEnum.STATION
userdefined = IfcReferentTypeEnum.USERDEFINED
notdefined = IfcReferentTypeEnum.NOTDEFINED
IfcReflectanceMethodEnum = enum_namespace()
blinn = IfcReflectanceMethodEnum.BLINN
flat = IfcReflectanceMethodEnum.FLAT
glass = IfcReflectanceMethodEnum.GLASS
matt = IfcReflectanceMethodEnum.MATT
metal = IfcReflectanceMethodEnum.METAL
mirror = IfcReflectanceMethodEnum.MIRROR
phong = IfcReflectanceMethodEnum.PHONG
plastic = IfcReflectanceMethodEnum.PLASTIC
strauss = IfcReflectanceMethodEnum.STRAUSS
notdefined = IfcReflectanceMethodEnum.NOTDEFINED
IfcReinforcingBarRoleEnum = enum_namespace()
main = IfcReinforcingBarRoleEnum.MAIN
shear = IfcReinforcingBarRoleEnum.SHEAR
ligature = IfcReinforcingBarRoleEnum.LIGATURE
stud = IfcReinforcingBarRoleEnum.STUD
punching = IfcReinforcingBarRoleEnum.PUNCHING
edge = IfcReinforcingBarRoleEnum.EDGE
ring = IfcReinforcingBarRoleEnum.RING
anchoring = IfcReinforcingBarRoleEnum.ANCHORING
userdefined = IfcReinforcingBarRoleEnum.USERDEFINED
notdefined = IfcReinforcingBarRoleEnum.NOTDEFINED
IfcReinforcingBarSurfaceEnum = enum_namespace()
plain = IfcReinforcingBarSurfaceEnum.PLAIN
textured = IfcReinforcingBarSurfaceEnum.TEXTURED
IfcReinforcingBarTypeEnum = enum_namespace()
anchoring = IfcReinforcingBarTypeEnum.ANCHORING
edge = IfcReinforcingBarTypeEnum.EDGE
ligature = IfcReinforcingBarTypeEnum.LIGATURE
main = IfcReinforcingBarTypeEnum.MAIN
punching = IfcReinforcingBarTypeEnum.PUNCHING
ring = IfcReinforcingBarTypeEnum.RING
shear = IfcReinforcingBarTypeEnum.SHEAR
stud = IfcReinforcingBarTypeEnum.STUD
spacebar = IfcReinforcingBarTypeEnum.SPACEBAR
userdefined = IfcReinforcingBarTypeEnum.USERDEFINED
notdefined = IfcReinforcingBarTypeEnum.NOTDEFINED
IfcReinforcingMeshTypeEnum = enum_namespace()
userdefined = IfcReinforcingMeshTypeEnum.USERDEFINED
notdefined = IfcReinforcingMeshTypeEnum.NOTDEFINED
IfcRoleEnum = enum_namespace()
supplier = IfcRoleEnum.SUPPLIER
manufacturer = IfcRoleEnum.MANUFACTURER
contractor = IfcRoleEnum.CONTRACTOR
subcontractor = IfcRoleEnum.SUBCONTRACTOR
architect = IfcRoleEnum.ARCHITECT
structuralengineer = IfcRoleEnum.STRUCTURALENGINEER
costengineer = IfcRoleEnum.COSTENGINEER
client = IfcRoleEnum.CLIENT
buildingowner = IfcRoleEnum.BUILDINGOWNER
buildingoperator = IfcRoleEnum.BUILDINGOPERATOR
mechanicalengineer = IfcRoleEnum.MECHANICALENGINEER
electricalengineer = IfcRoleEnum.ELECTRICALENGINEER
projectmanager = IfcRoleEnum.PROJECTMANAGER
facilitiesmanager = IfcRoleEnum.FACILITIESMANAGER
civilengineer = IfcRoleEnum.CIVILENGINEER
commissioningengineer = IfcRoleEnum.COMMISSIONINGENGINEER
engineer = IfcRoleEnum.ENGINEER
owner = IfcRoleEnum.OWNER
consultant = IfcRoleEnum.CONSULTANT
constructionmanager = IfcRoleEnum.CONSTRUCTIONMANAGER
fieldconstructionmanager = IfcRoleEnum.FIELDCONSTRUCTIONMANAGER
reseller = IfcRoleEnum.RESELLER
userdefined = IfcRoleEnum.USERDEFINED
IfcRoofTypeEnum = enum_namespace()
flat_roof = IfcRoofTypeEnum.FLAT_ROOF
shed_roof = IfcRoofTypeEnum.SHED_ROOF
gable_roof = IfcRoofTypeEnum.GABLE_ROOF
hip_roof = IfcRoofTypeEnum.HIP_ROOF
hipped_gable_roof = IfcRoofTypeEnum.HIPPED_GABLE_ROOF
gambrel_roof = IfcRoofTypeEnum.GAMBREL_ROOF
mansard_roof = IfcRoofTypeEnum.MANSARD_ROOF
barrel_roof = IfcRoofTypeEnum.BARREL_ROOF
rainbow_roof = IfcRoofTypeEnum.RAINBOW_ROOF
butterfly_roof = IfcRoofTypeEnum.BUTTERFLY_ROOF
pavilion_roof = IfcRoofTypeEnum.PAVILION_ROOF
dome_roof = IfcRoofTypeEnum.DOME_ROOF
freeform = IfcRoofTypeEnum.FREEFORM
userdefined = IfcRoofTypeEnum.USERDEFINED
notdefined = IfcRoofTypeEnum.NOTDEFINED
IfcSIPrefix = enum_namespace()
exa = IfcSIPrefix.EXA
peta = IfcSIPrefix.PETA
tera = IfcSIPrefix.TERA
giga = IfcSIPrefix.GIGA
mega = IfcSIPrefix.MEGA
kilo = IfcSIPrefix.KILO
hecto = IfcSIPrefix.HECTO
deca = IfcSIPrefix.DECA
deci = IfcSIPrefix.DECI
centi = IfcSIPrefix.CENTI
milli = IfcSIPrefix.MILLI
micro = IfcSIPrefix.MICRO
nano = IfcSIPrefix.NANO
pico = IfcSIPrefix.PICO
femto = IfcSIPrefix.FEMTO
atto = IfcSIPrefix.ATTO
IfcSIUnitName = enum_namespace()
ampere = IfcSIUnitName.AMPERE
becquerel = IfcSIUnitName.BECQUEREL
candela = IfcSIUnitName.CANDELA
coulomb = IfcSIUnitName.COULOMB
cubic_metre = IfcSIUnitName.CUBIC_METRE
degree_celsius = IfcSIUnitName.DEGREE_CELSIUS
farad = IfcSIUnitName.FARAD
gram = IfcSIUnitName.GRAM
gray = IfcSIUnitName.GRAY
henry = IfcSIUnitName.HENRY
hertz = IfcSIUnitName.HERTZ
joule = IfcSIUnitName.JOULE
kelvin = IfcSIUnitName.KELVIN
lumen = IfcSIUnitName.LUMEN
lux = IfcSIUnitName.LUX
metre = IfcSIUnitName.METRE
mole = IfcSIUnitName.MOLE
newton = IfcSIUnitName.NEWTON
ohm = IfcSIUnitName.OHM
pascal = IfcSIUnitName.PASCAL
radian = IfcSIUnitName.RADIAN
second = IfcSIUnitName.SECOND
siemens = IfcSIUnitName.SIEMENS
sievert = IfcSIUnitName.SIEVERT
square_metre = IfcSIUnitName.SQUARE_METRE
steradian = IfcSIUnitName.STERADIAN
tesla = IfcSIUnitName.TESLA
volt = IfcSIUnitName.VOLT
watt = IfcSIUnitName.WATT
weber = IfcSIUnitName.WEBER
IfcSanitaryTerminalTypeEnum = enum_namespace()
bath = IfcSanitaryTerminalTypeEnum.BATH
bidet = IfcSanitaryTerminalTypeEnum.BIDET
cistern = IfcSanitaryTerminalTypeEnum.CISTERN
shower = IfcSanitaryTerminalTypeEnum.SHOWER
sink = IfcSanitaryTerminalTypeEnum.SINK
sanitaryfountain = IfcSanitaryTerminalTypeEnum.SANITARYFOUNTAIN
toiletpan = IfcSanitaryTerminalTypeEnum.TOILETPAN
urinal = IfcSanitaryTerminalTypeEnum.URINAL
washhandbasin = IfcSanitaryTerminalTypeEnum.WASHHANDBASIN
wcseat = IfcSanitaryTerminalTypeEnum.WCSEAT
userdefined = IfcSanitaryTerminalTypeEnum.USERDEFINED
notdefined = IfcSanitaryTerminalTypeEnum.NOTDEFINED
IfcSectionTypeEnum = enum_namespace()
uniform = IfcSectionTypeEnum.UNIFORM
tapered = IfcSectionTypeEnum.TAPERED
IfcSensorTypeEnum = enum_namespace()
cosensor = IfcSensorTypeEnum.COSENSOR
co2sensor = IfcSensorTypeEnum.CO2SENSOR
conductancesensor = IfcSensorTypeEnum.CONDUCTANCESENSOR
contactsensor = IfcSensorTypeEnum.CONTACTSENSOR
firesensor = IfcSensorTypeEnum.FIRESENSOR
flowsensor = IfcSensorTypeEnum.FLOWSENSOR
frostsensor = IfcSensorTypeEnum.FROSTSENSOR
gassensor = IfcSensorTypeEnum.GASSENSOR
heatsensor = IfcSensorTypeEnum.HEATSENSOR
humiditysensor = IfcSensorTypeEnum.HUMIDITYSENSOR
identifiersensor = IfcSensorTypeEnum.IDENTIFIERSENSOR
ionconcentrationsensor = IfcSensorTypeEnum.IONCONCENTRATIONSENSOR
levelsensor = IfcSensorTypeEnum.LEVELSENSOR
lightsensor = IfcSensorTypeEnum.LIGHTSENSOR
moisturesensor = IfcSensorTypeEnum.MOISTURESENSOR
movementsensor = IfcSensorTypeEnum.MOVEMENTSENSOR
phsensor = IfcSensorTypeEnum.PHSENSOR
pressuresensor = IfcSensorTypeEnum.PRESSURESENSOR
radiationsensor = IfcSensorTypeEnum.RADIATIONSENSOR
radioactivitysensor = IfcSensorTypeEnum.RADIOACTIVITYSENSOR
smokesensor = IfcSensorTypeEnum.SMOKESENSOR
soundsensor = IfcSensorTypeEnum.SOUNDSENSOR
temperaturesensor = IfcSensorTypeEnum.TEMPERATURESENSOR
windsensor = IfcSensorTypeEnum.WINDSENSOR
userdefined = IfcSensorTypeEnum.USERDEFINED
notdefined = IfcSensorTypeEnum.NOTDEFINED
IfcSequenceEnum = enum_namespace()
start_start = IfcSequenceEnum.START_START
start_finish = IfcSequenceEnum.START_FINISH
finish_start = IfcSequenceEnum.FINISH_START
finish_finish = IfcSequenceEnum.FINISH_FINISH
userdefined = IfcSequenceEnum.USERDEFINED
notdefined = IfcSequenceEnum.NOTDEFINED
IfcShadingDeviceTypeEnum = enum_namespace()
jalousie = IfcShadingDeviceTypeEnum.JALOUSIE
shutter = IfcShadingDeviceTypeEnum.SHUTTER
awning = IfcShadingDeviceTypeEnum.AWNING
userdefined = IfcShadingDeviceTypeEnum.USERDEFINED
notdefined = IfcShadingDeviceTypeEnum.NOTDEFINED
IfcSimplePropertyTemplateTypeEnum = enum_namespace()
p_singlevalue = IfcSimplePropertyTemplateTypeEnum.P_SINGLEVALUE
p_enumeratedvalue = IfcSimplePropertyTemplateTypeEnum.P_ENUMERATEDVALUE
p_boundedvalue = IfcSimplePropertyTemplateTypeEnum.P_BOUNDEDVALUE
p_listvalue = IfcSimplePropertyTemplateTypeEnum.P_LISTVALUE
p_tablevalue = IfcSimplePropertyTemplateTypeEnum.P_TABLEVALUE
p_referencevalue = IfcSimplePropertyTemplateTypeEnum.P_REFERENCEVALUE
q_length = IfcSimplePropertyTemplateTypeEnum.Q_LENGTH
q_area = IfcSimplePropertyTemplateTypeEnum.Q_AREA
q_volume = IfcSimplePropertyTemplateTypeEnum.Q_VOLUME
q_count = IfcSimplePropertyTemplateTypeEnum.Q_COUNT
q_weight = IfcSimplePropertyTemplateTypeEnum.Q_WEIGHT
q_time = IfcSimplePropertyTemplateTypeEnum.Q_TIME
IfcSlabTypeEnum = enum_namespace()
floor = IfcSlabTypeEnum.FLOOR
roof = IfcSlabTypeEnum.ROOF
landing = IfcSlabTypeEnum.LANDING
baseslab = IfcSlabTypeEnum.BASESLAB
approach_slab = IfcSlabTypeEnum.APPROACH_SLAB
paving = IfcSlabTypeEnum.PAVING
wearing = IfcSlabTypeEnum.WEARING
sidewalk = IfcSlabTypeEnum.SIDEWALK
userdefined = IfcSlabTypeEnum.USERDEFINED
notdefined = IfcSlabTypeEnum.NOTDEFINED
IfcSolarDeviceTypeEnum = enum_namespace()
solarcollector = IfcSolarDeviceTypeEnum.SOLARCOLLECTOR
solarpanel = IfcSolarDeviceTypeEnum.SOLARPANEL
userdefined = IfcSolarDeviceTypeEnum.USERDEFINED
notdefined = IfcSolarDeviceTypeEnum.NOTDEFINED
IfcSpaceHeaterTypeEnum = enum_namespace()
convector = IfcSpaceHeaterTypeEnum.CONVECTOR
radiator = IfcSpaceHeaterTypeEnum.RADIATOR
userdefined = IfcSpaceHeaterTypeEnum.USERDEFINED
notdefined = IfcSpaceHeaterTypeEnum.NOTDEFINED
IfcSpaceTypeEnum = enum_namespace()
space = IfcSpaceTypeEnum.SPACE
parking = IfcSpaceTypeEnum.PARKING
gfa = IfcSpaceTypeEnum.GFA
internal = IfcSpaceTypeEnum.INTERNAL
external = IfcSpaceTypeEnum.EXTERNAL
userdefined = IfcSpaceTypeEnum.USERDEFINED
notdefined = IfcSpaceTypeEnum.NOTDEFINED
IfcSpatialZoneTypeEnum = enum_namespace()
construction = IfcSpatialZoneTypeEnum.CONSTRUCTION
firesafety = IfcSpatialZoneTypeEnum.FIRESAFETY
lighting = IfcSpatialZoneTypeEnum.LIGHTING
occupancy = IfcSpatialZoneTypeEnum.OCCUPANCY
security = IfcSpatialZoneTypeEnum.SECURITY
thermal = IfcSpatialZoneTypeEnum.THERMAL
transport = IfcSpatialZoneTypeEnum.TRANSPORT
ventilation = IfcSpatialZoneTypeEnum.VENTILATION
userdefined = IfcSpatialZoneTypeEnum.USERDEFINED
notdefined = IfcSpatialZoneTypeEnum.NOTDEFINED
IfcStackTerminalTypeEnum = enum_namespace()
birdcage = IfcStackTerminalTypeEnum.BIRDCAGE
cowl = IfcStackTerminalTypeEnum.COWL
rainwaterhopper = IfcStackTerminalTypeEnum.RAINWATERHOPPER
userdefined = IfcStackTerminalTypeEnum.USERDEFINED
notdefined = IfcStackTerminalTypeEnum.NOTDEFINED
IfcStairFlightTypeEnum = enum_namespace()
straight = IfcStairFlightTypeEnum.STRAIGHT
winder = IfcStairFlightTypeEnum.WINDER
spiral = IfcStairFlightTypeEnum.SPIRAL
curved = IfcStairFlightTypeEnum.CURVED
freeform = IfcStairFlightTypeEnum.FREEFORM
userdefined = IfcStairFlightTypeEnum.USERDEFINED
notdefined = IfcStairFlightTypeEnum.NOTDEFINED
IfcStairTypeEnum = enum_namespace()
straight_run_stair = IfcStairTypeEnum.STRAIGHT_RUN_STAIR
two_straight_run_stair = IfcStairTypeEnum.TWO_STRAIGHT_RUN_STAIR
quarter_winding_stair = IfcStairTypeEnum.QUARTER_WINDING_STAIR
quarter_turn_stair = IfcStairTypeEnum.QUARTER_TURN_STAIR
half_winding_stair = IfcStairTypeEnum.HALF_WINDING_STAIR
half_turn_stair = IfcStairTypeEnum.HALF_TURN_STAIR
two_quarter_winding_stair = IfcStairTypeEnum.TWO_QUARTER_WINDING_STAIR
two_quarter_turn_stair = IfcStairTypeEnum.TWO_QUARTER_TURN_STAIR
three_quarter_winding_stair = IfcStairTypeEnum.THREE_QUARTER_WINDING_STAIR
three_quarter_turn_stair = IfcStairTypeEnum.THREE_QUARTER_TURN_STAIR
spiral_stair = IfcStairTypeEnum.SPIRAL_STAIR
double_return_stair = IfcStairTypeEnum.DOUBLE_RETURN_STAIR
curved_run_stair = IfcStairTypeEnum.CURVED_RUN_STAIR
two_curved_run_stair = IfcStairTypeEnum.TWO_CURVED_RUN_STAIR
userdefined = IfcStairTypeEnum.USERDEFINED
notdefined = IfcStairTypeEnum.NOTDEFINED
IfcStateEnum = enum_namespace()
readwrite = IfcStateEnum.READWRITE
readonly = IfcStateEnum.READONLY
locked = IfcStateEnum.LOCKED
readwritelocked = IfcStateEnum.READWRITELOCKED
readonlylocked = IfcStateEnum.READONLYLOCKED
IfcStructuralCurveActivityTypeEnum = enum_namespace()
const = IfcStructuralCurveActivityTypeEnum.CONST
linear = IfcStructuralCurveActivityTypeEnum.LINEAR
polygonal = IfcStructuralCurveActivityTypeEnum.POLYGONAL
equidistant = IfcStructuralCurveActivityTypeEnum.EQUIDISTANT
sinus = IfcStructuralCurveActivityTypeEnum.SINUS
parabola = IfcStructuralCurveActivityTypeEnum.PARABOLA
discrete = IfcStructuralCurveActivityTypeEnum.DISCRETE
userdefined = IfcStructuralCurveActivityTypeEnum.USERDEFINED
notdefined = IfcStructuralCurveActivityTypeEnum.NOTDEFINED
IfcStructuralCurveMemberTypeEnum = enum_namespace()
rigid_joined_member = IfcStructuralCurveMemberTypeEnum.RIGID_JOINED_MEMBER
pin_joined_member = IfcStructuralCurveMemberTypeEnum.PIN_JOINED_MEMBER
cable = IfcStructuralCurveMemberTypeEnum.CABLE
tension_member = IfcStructuralCurveMemberTypeEnum.TENSION_MEMBER
compression_member = IfcStructuralCurveMemberTypeEnum.COMPRESSION_MEMBER
userdefined = IfcStructuralCurveMemberTypeEnum.USERDEFINED
notdefined = IfcStructuralCurveMemberTypeEnum.NOTDEFINED
IfcStructuralSurfaceActivityTypeEnum = enum_namespace()
const = IfcStructuralSurfaceActivityTypeEnum.CONST
bilinear = IfcStructuralSurfaceActivityTypeEnum.BILINEAR
discrete = IfcStructuralSurfaceActivityTypeEnum.DISCRETE
isocontour = IfcStructuralSurfaceActivityTypeEnum.ISOCONTOUR
userdefined = IfcStructuralSurfaceActivityTypeEnum.USERDEFINED
notdefined = IfcStructuralSurfaceActivityTypeEnum.NOTDEFINED
IfcStructuralSurfaceMemberTypeEnum = enum_namespace()
bending_element = IfcStructuralSurfaceMemberTypeEnum.BENDING_ELEMENT
membrane_element = IfcStructuralSurfaceMemberTypeEnum.MEMBRANE_ELEMENT
shell = IfcStructuralSurfaceMemberTypeEnum.SHELL
userdefined = IfcStructuralSurfaceMemberTypeEnum.USERDEFINED
notdefined = IfcStructuralSurfaceMemberTypeEnum.NOTDEFINED
IfcSubContractResourceTypeEnum = enum_namespace()
purchase = IfcSubContractResourceTypeEnum.PURCHASE
work = IfcSubContractResourceTypeEnum.WORK
userdefined = IfcSubContractResourceTypeEnum.USERDEFINED
notdefined = IfcSubContractResourceTypeEnum.NOTDEFINED
IfcSurfaceFeatureTypeEnum = enum_namespace()
mark = IfcSurfaceFeatureTypeEnum.MARK
tag = IfcSurfaceFeatureTypeEnum.TAG
treatment = IfcSurfaceFeatureTypeEnum.TREATMENT
defect = IfcSurfaceFeatureTypeEnum.DEFECT
userdefined = IfcSurfaceFeatureTypeEnum.USERDEFINED
notdefined = IfcSurfaceFeatureTypeEnum.NOTDEFINED
IfcSurfaceSide = enum_namespace()
positive = IfcSurfaceSide.POSITIVE
negative = IfcSurfaceSide.NEGATIVE
both = IfcSurfaceSide.BOTH
IfcSwitchingDeviceTypeEnum = enum_namespace()
contactor = IfcSwitchingDeviceTypeEnum.CONTACTOR
dimmerswitch = IfcSwitchingDeviceTypeEnum.DIMMERSWITCH
emergencystop = IfcSwitchingDeviceTypeEnum.EMERGENCYSTOP
keypad = IfcSwitchingDeviceTypeEnum.KEYPAD
momentaryswitch = IfcSwitchingDeviceTypeEnum.MOMENTARYSWITCH
selectorswitch = IfcSwitchingDeviceTypeEnum.SELECTORSWITCH
starter = IfcSwitchingDeviceTypeEnum.STARTER
switchdisconnector = IfcSwitchingDeviceTypeEnum.SWITCHDISCONNECTOR
toggleswitch = IfcSwitchingDeviceTypeEnum.TOGGLESWITCH
userdefined = IfcSwitchingDeviceTypeEnum.USERDEFINED
notdefined = IfcSwitchingDeviceTypeEnum.NOTDEFINED
IfcSystemFurnitureElementTypeEnum = enum_namespace()
panel = IfcSystemFurnitureElementTypeEnum.PANEL
worksurface = IfcSystemFurnitureElementTypeEnum.WORKSURFACE
userdefined = IfcSystemFurnitureElementTypeEnum.USERDEFINED
notdefined = IfcSystemFurnitureElementTypeEnum.NOTDEFINED
IfcTankTypeEnum = enum_namespace()
basin = IfcTankTypeEnum.BASIN
breakpressure = IfcTankTypeEnum.BREAKPRESSURE
expansion = IfcTankTypeEnum.EXPANSION
feedandexpansion = IfcTankTypeEnum.FEEDANDEXPANSION
pressurevessel = IfcTankTypeEnum.PRESSUREVESSEL
storage = IfcTankTypeEnum.STORAGE
vessel = IfcTankTypeEnum.VESSEL
userdefined = IfcTankTypeEnum.USERDEFINED
notdefined = IfcTankTypeEnum.NOTDEFINED
IfcTaskDurationEnum = enum_namespace()
elapsedtime = IfcTaskDurationEnum.ELAPSEDTIME
worktime = IfcTaskDurationEnum.WORKTIME
notdefined = IfcTaskDurationEnum.NOTDEFINED
IfcTaskTypeEnum = enum_namespace()
attendance = IfcTaskTypeEnum.ATTENDANCE
construction = IfcTaskTypeEnum.CONSTRUCTION
demolition = IfcTaskTypeEnum.DEMOLITION
dismantle = IfcTaskTypeEnum.DISMANTLE
disposal = IfcTaskTypeEnum.DISPOSAL
installation = IfcTaskTypeEnum.INSTALLATION
logistic = IfcTaskTypeEnum.LOGISTIC
maintenance = IfcTaskTypeEnum.MAINTENANCE
move = IfcTaskTypeEnum.MOVE
operation = IfcTaskTypeEnum.OPERATION
removal = IfcTaskTypeEnum.REMOVAL
renovation = IfcTaskTypeEnum.RENOVATION
userdefined = IfcTaskTypeEnum.USERDEFINED
notdefined = IfcTaskTypeEnum.NOTDEFINED
IfcTendonAnchorTypeEnum = enum_namespace()
coupler = IfcTendonAnchorTypeEnum.COUPLER
fixed_end = IfcTendonAnchorTypeEnum.FIXED_END
tensioning_end = IfcTendonAnchorTypeEnum.TENSIONING_END
userdefined = IfcTendonAnchorTypeEnum.USERDEFINED
notdefined = IfcTendonAnchorTypeEnum.NOTDEFINED
IfcTendonConduitTypeEnum = enum_namespace()
duct = IfcTendonConduitTypeEnum.DUCT
coupler = IfcTendonConduitTypeEnum.COUPLER
grouting_duct = IfcTendonConduitTypeEnum.GROUTING_DUCT
trumpet = IfcTendonConduitTypeEnum.TRUMPET
diabolo = IfcTendonConduitTypeEnum.DIABOLO
userdefined = IfcTendonConduitTypeEnum.USERDEFINED
notdefined = IfcTendonConduitTypeEnum.NOTDEFINED
IfcTendonTypeEnum = enum_namespace()
bar = IfcTendonTypeEnum.BAR
coated = IfcTendonTypeEnum.COATED
strand = IfcTendonTypeEnum.STRAND
wire = IfcTendonTypeEnum.WIRE
userdefined = IfcTendonTypeEnum.USERDEFINED
notdefined = IfcTendonTypeEnum.NOTDEFINED
IfcTextPath = enum_namespace()
left = IfcTextPath.LEFT
right = IfcTextPath.RIGHT
up = IfcTextPath.UP
down = IfcTextPath.DOWN
IfcTimeSeriesDataTypeEnum = enum_namespace()
continuous = IfcTimeSeriesDataTypeEnum.CONTINUOUS
discrete = IfcTimeSeriesDataTypeEnum.DISCRETE
discretebinary = IfcTimeSeriesDataTypeEnum.DISCRETEBINARY
piecewisebinary = IfcTimeSeriesDataTypeEnum.PIECEWISEBINARY
piecewiseconstant = IfcTimeSeriesDataTypeEnum.PIECEWISECONSTANT
piecewisecontinuous = IfcTimeSeriesDataTypeEnum.PIECEWISECONTINUOUS
notdefined = IfcTimeSeriesDataTypeEnum.NOTDEFINED
IfcTransformerTypeEnum = enum_namespace()
current = IfcTransformerTypeEnum.CURRENT
frequency = IfcTransformerTypeEnum.FREQUENCY
inverter = IfcTransformerTypeEnum.INVERTER
rectifier = IfcTransformerTypeEnum.RECTIFIER
voltage = IfcTransformerTypeEnum.VOLTAGE
userdefined = IfcTransformerTypeEnum.USERDEFINED
notdefined = IfcTransformerTypeEnum.NOTDEFINED
IfcTransitionCode = enum_namespace()
discontinuous = IfcTransitionCode.DISCONTINUOUS
continuous = IfcTransitionCode.CONTINUOUS
contsamegradient = IfcTransitionCode.CONTSAMEGRADIENT
contsamegradientsamecurvature = IfcTransitionCode.CONTSAMEGRADIENTSAMECURVATURE
IfcTransitionCurveType = enum_namespace()
biquadraticparabola = IfcTransitionCurveType.BIQUADRATICPARABOLA
blosscurve = IfcTransitionCurveType.BLOSSCURVE
clothoidcurve = IfcTransitionCurveType.CLOTHOIDCURVE
cosinecurve = IfcTransitionCurveType.COSINECURVE
cubicparabola = IfcTransitionCurveType.CUBICPARABOLA
sinecurve = IfcTransitionCurveType.SINECURVE
IfcTransportElementTypeEnum = enum_namespace()
elevator = IfcTransportElementTypeEnum.ELEVATOR
escalator = IfcTransportElementTypeEnum.ESCALATOR
movingwalkway = IfcTransportElementTypeEnum.MOVINGWALKWAY
craneway = IfcTransportElementTypeEnum.CRANEWAY
liftinggear = IfcTransportElementTypeEnum.LIFTINGGEAR
userdefined = IfcTransportElementTypeEnum.USERDEFINED
notdefined = IfcTransportElementTypeEnum.NOTDEFINED
IfcTrimmingPreference = enum_namespace()
cartesian = IfcTrimmingPreference.CARTESIAN
parameter = IfcTrimmingPreference.PARAMETER
unspecified = IfcTrimmingPreference.UNSPECIFIED
IfcTubeBundleTypeEnum = enum_namespace()
finned = IfcTubeBundleTypeEnum.FINNED
userdefined = IfcTubeBundleTypeEnum.USERDEFINED
notdefined = IfcTubeBundleTypeEnum.NOTDEFINED
IfcUnitEnum = enum_namespace()
absorbeddoseunit = IfcUnitEnum.ABSORBEDDOSEUNIT
amountofsubstanceunit = IfcUnitEnum.AMOUNTOFSUBSTANCEUNIT
areaunit = IfcUnitEnum.AREAUNIT
doseequivalentunit = IfcUnitEnum.DOSEEQUIVALENTUNIT
electriccapacitanceunit = IfcUnitEnum.ELECTRICCAPACITANCEUNIT
electricchargeunit = IfcUnitEnum.ELECTRICCHARGEUNIT
electricconductanceunit = IfcUnitEnum.ELECTRICCONDUCTANCEUNIT
electriccurrentunit = IfcUnitEnum.ELECTRICCURRENTUNIT
electricresistanceunit = IfcUnitEnum.ELECTRICRESISTANCEUNIT
electricvoltageunit = IfcUnitEnum.ELECTRICVOLTAGEUNIT
energyunit = IfcUnitEnum.ENERGYUNIT
forceunit = IfcUnitEnum.FORCEUNIT
frequencyunit = IfcUnitEnum.FREQUENCYUNIT
illuminanceunit = IfcUnitEnum.ILLUMINANCEUNIT
inductanceunit = IfcUnitEnum.INDUCTANCEUNIT
lengthunit = IfcUnitEnum.LENGTHUNIT
luminousfluxunit = IfcUnitEnum.LUMINOUSFLUXUNIT
luminousintensityunit = IfcUnitEnum.LUMINOUSINTENSITYUNIT
magneticfluxdensityunit = IfcUnitEnum.MAGNETICFLUXDENSITYUNIT
magneticfluxunit = IfcUnitEnum.MAGNETICFLUXUNIT
massunit = IfcUnitEnum.MASSUNIT
planeangleunit = IfcUnitEnum.PLANEANGLEUNIT
powerunit = IfcUnitEnum.POWERUNIT
pressureunit = IfcUnitEnum.PRESSUREUNIT
radioactivityunit = IfcUnitEnum.RADIOACTIVITYUNIT
solidangleunit = IfcUnitEnum.SOLIDANGLEUNIT
thermodynamictemperatureunit = IfcUnitEnum.THERMODYNAMICTEMPERATUREUNIT
timeunit = IfcUnitEnum.TIMEUNIT
volumeunit = IfcUnitEnum.VOLUMEUNIT
userdefined = IfcUnitEnum.USERDEFINED
IfcUnitaryControlElementTypeEnum = enum_namespace()
alarmpanel = IfcUnitaryControlElementTypeEnum.ALARMPANEL
controlpanel = IfcUnitaryControlElementTypeEnum.CONTROLPANEL
gasdetectionpanel = IfcUnitaryControlElementTypeEnum.GASDETECTIONPANEL
indicatorpanel = IfcUnitaryControlElementTypeEnum.INDICATORPANEL
mimicpanel = IfcUnitaryControlElementTypeEnum.MIMICPANEL
humidistat = IfcUnitaryControlElementTypeEnum.HUMIDISTAT
thermostat = IfcUnitaryControlElementTypeEnum.THERMOSTAT
weatherstation = IfcUnitaryControlElementTypeEnum.WEATHERSTATION
userdefined = IfcUnitaryControlElementTypeEnum.USERDEFINED
notdefined = IfcUnitaryControlElementTypeEnum.NOTDEFINED
IfcUnitaryEquipmentTypeEnum = enum_namespace()
airhandler = IfcUnitaryEquipmentTypeEnum.AIRHANDLER
airconditioningunit = IfcUnitaryEquipmentTypeEnum.AIRCONDITIONINGUNIT
dehumidifier = IfcUnitaryEquipmentTypeEnum.DEHUMIDIFIER
splitsystem = IfcUnitaryEquipmentTypeEnum.SPLITSYSTEM
rooftopunit = IfcUnitaryEquipmentTypeEnum.ROOFTOPUNIT
userdefined = IfcUnitaryEquipmentTypeEnum.USERDEFINED
notdefined = IfcUnitaryEquipmentTypeEnum.NOTDEFINED
IfcValveTypeEnum = enum_namespace()
airrelease = IfcValveTypeEnum.AIRRELEASE
antivacuum = IfcValveTypeEnum.ANTIVACUUM
changeover = IfcValveTypeEnum.CHANGEOVER
check = IfcValveTypeEnum.CHECK
commissioning = IfcValveTypeEnum.COMMISSIONING
diverting = IfcValveTypeEnum.DIVERTING
drawoffcock = IfcValveTypeEnum.DRAWOFFCOCK
doublecheck = IfcValveTypeEnum.DOUBLECHECK
doubleregulating = IfcValveTypeEnum.DOUBLEREGULATING
faucet = IfcValveTypeEnum.FAUCET
flushing = IfcValveTypeEnum.FLUSHING
gascock = IfcValveTypeEnum.GASCOCK
gastap = IfcValveTypeEnum.GASTAP
isolating = IfcValveTypeEnum.ISOLATING
mixing = IfcValveTypeEnum.MIXING
pressurereducing = IfcValveTypeEnum.PRESSUREREDUCING
pressurerelief = IfcValveTypeEnum.PRESSURERELIEF
regulating = IfcValveTypeEnum.REGULATING
safetycutoff = IfcValveTypeEnum.SAFETYCUTOFF
steamtrap = IfcValveTypeEnum.STEAMTRAP
stopcock = IfcValveTypeEnum.STOPCOCK
userdefined = IfcValveTypeEnum.USERDEFINED
notdefined = IfcValveTypeEnum.NOTDEFINED
IfcVibrationDamperTypeEnum = enum_namespace()
bending_yield = IfcVibrationDamperTypeEnum.BENDING_YIELD
shear_yield = IfcVibrationDamperTypeEnum.SHEAR_YIELD
axial_yield = IfcVibrationDamperTypeEnum.AXIAL_YIELD
friction = IfcVibrationDamperTypeEnum.FRICTION
viscous = IfcVibrationDamperTypeEnum.VISCOUS
rubber = IfcVibrationDamperTypeEnum.RUBBER
userdefined = IfcVibrationDamperTypeEnum.USERDEFINED
notdefined = IfcVibrationDamperTypeEnum.NOTDEFINED
IfcVibrationIsolatorTypeEnum = enum_namespace()
compression = IfcVibrationIsolatorTypeEnum.COMPRESSION
spring = IfcVibrationIsolatorTypeEnum.SPRING
base = IfcVibrationIsolatorTypeEnum.BASE
userdefined = IfcVibrationIsolatorTypeEnum.USERDEFINED
notdefined = IfcVibrationIsolatorTypeEnum.NOTDEFINED
IfcVoidingFeatureTypeEnum = enum_namespace()
cutout = IfcVoidingFeatureTypeEnum.CUTOUT
notch = IfcVoidingFeatureTypeEnum.NOTCH
hole = IfcVoidingFeatureTypeEnum.HOLE
miter = IfcVoidingFeatureTypeEnum.MITER
chamfer = IfcVoidingFeatureTypeEnum.CHAMFER
edge = IfcVoidingFeatureTypeEnum.EDGE
userdefined = IfcVoidingFeatureTypeEnum.USERDEFINED
notdefined = IfcVoidingFeatureTypeEnum.NOTDEFINED
IfcWallTypeEnum = enum_namespace()
movable = IfcWallTypeEnum.MOVABLE
parapet = IfcWallTypeEnum.PARAPET
partitioning = IfcWallTypeEnum.PARTITIONING
plumbingwall = IfcWallTypeEnum.PLUMBINGWALL
shear = IfcWallTypeEnum.SHEAR
solidwall = IfcWallTypeEnum.SOLIDWALL
standard = IfcWallTypeEnum.STANDARD
polygonal = IfcWallTypeEnum.POLYGONAL
elementedwall = IfcWallTypeEnum.ELEMENTEDWALL
retainingwall = IfcWallTypeEnum.RETAININGWALL
userdefined = IfcWallTypeEnum.USERDEFINED
notdefined = IfcWallTypeEnum.NOTDEFINED
IfcWasteTerminalTypeEnum = enum_namespace()
floortrap = IfcWasteTerminalTypeEnum.FLOORTRAP
floorwaste = IfcWasteTerminalTypeEnum.FLOORWASTE
gullysump = IfcWasteTerminalTypeEnum.GULLYSUMP
gullytrap = IfcWasteTerminalTypeEnum.GULLYTRAP
roofdrain = IfcWasteTerminalTypeEnum.ROOFDRAIN
wastedisposalunit = IfcWasteTerminalTypeEnum.WASTEDISPOSALUNIT
wastetrap = IfcWasteTerminalTypeEnum.WASTETRAP
userdefined = IfcWasteTerminalTypeEnum.USERDEFINED
notdefined = IfcWasteTerminalTypeEnum.NOTDEFINED
IfcWindowPanelOperationEnum = enum_namespace()
sidehungrighthand = IfcWindowPanelOperationEnum.SIDEHUNGRIGHTHAND
sidehunglefthand = IfcWindowPanelOperationEnum.SIDEHUNGLEFTHAND
tiltandturnrighthand = IfcWindowPanelOperationEnum.TILTANDTURNRIGHTHAND
tiltandturnlefthand = IfcWindowPanelOperationEnum.TILTANDTURNLEFTHAND
tophung = IfcWindowPanelOperationEnum.TOPHUNG
bottomhung = IfcWindowPanelOperationEnum.BOTTOMHUNG
pivothorizontal = IfcWindowPanelOperationEnum.PIVOTHORIZONTAL
pivotvertical = IfcWindowPanelOperationEnum.PIVOTVERTICAL
slidinghorizontal = IfcWindowPanelOperationEnum.SLIDINGHORIZONTAL
slidingvertical = IfcWindowPanelOperationEnum.SLIDINGVERTICAL
removablecasement = IfcWindowPanelOperationEnum.REMOVABLECASEMENT
fixedcasement = IfcWindowPanelOperationEnum.FIXEDCASEMENT
otheroperation = IfcWindowPanelOperationEnum.OTHEROPERATION
notdefined = IfcWindowPanelOperationEnum.NOTDEFINED
IfcWindowPanelPositionEnum = enum_namespace()
left = IfcWindowPanelPositionEnum.LEFT
middle = IfcWindowPanelPositionEnum.MIDDLE
right = IfcWindowPanelPositionEnum.RIGHT
bottom = IfcWindowPanelPositionEnum.BOTTOM
top = IfcWindowPanelPositionEnum.TOP
notdefined = IfcWindowPanelPositionEnum.NOTDEFINED
IfcWindowStyleConstructionEnum = enum_namespace()
aluminium = IfcWindowStyleConstructionEnum.ALUMINIUM
high_grade_steel = IfcWindowStyleConstructionEnum.HIGH_GRADE_STEEL
steel = IfcWindowStyleConstructionEnum.STEEL
wood = IfcWindowStyleConstructionEnum.WOOD
aluminium_wood = IfcWindowStyleConstructionEnum.ALUMINIUM_WOOD
plastic = IfcWindowStyleConstructionEnum.PLASTIC
other_construction = IfcWindowStyleConstructionEnum.OTHER_CONSTRUCTION
notdefined = IfcWindowStyleConstructionEnum.NOTDEFINED
IfcWindowStyleOperationEnum = enum_namespace()
single_panel = IfcWindowStyleOperationEnum.SINGLE_PANEL
double_panel_vertical = IfcWindowStyleOperationEnum.DOUBLE_PANEL_VERTICAL
double_panel_horizontal = IfcWindowStyleOperationEnum.DOUBLE_PANEL_HORIZONTAL
triple_panel_vertical = IfcWindowStyleOperationEnum.TRIPLE_PANEL_VERTICAL
triple_panel_bottom = IfcWindowStyleOperationEnum.TRIPLE_PANEL_BOTTOM
triple_panel_top = IfcWindowStyleOperationEnum.TRIPLE_PANEL_TOP
triple_panel_left = IfcWindowStyleOperationEnum.TRIPLE_PANEL_LEFT
triple_panel_right = IfcWindowStyleOperationEnum.TRIPLE_PANEL_RIGHT
triple_panel_horizontal = IfcWindowStyleOperationEnum.TRIPLE_PANEL_HORIZONTAL
userdefined = IfcWindowStyleOperationEnum.USERDEFINED
notdefined = IfcWindowStyleOperationEnum.NOTDEFINED
IfcWindowTypeEnum = enum_namespace()
window = IfcWindowTypeEnum.WINDOW
skylight = IfcWindowTypeEnum.SKYLIGHT
lightdome = IfcWindowTypeEnum.LIGHTDOME
userdefined = IfcWindowTypeEnum.USERDEFINED
notdefined = IfcWindowTypeEnum.NOTDEFINED
IfcWindowTypePartitioningEnum = enum_namespace()
single_panel = IfcWindowTypePartitioningEnum.SINGLE_PANEL
double_panel_vertical = IfcWindowTypePartitioningEnum.DOUBLE_PANEL_VERTICAL
double_panel_horizontal = IfcWindowTypePartitioningEnum.DOUBLE_PANEL_HORIZONTAL
triple_panel_vertical = IfcWindowTypePartitioningEnum.TRIPLE_PANEL_VERTICAL
triple_panel_bottom = IfcWindowTypePartitioningEnum.TRIPLE_PANEL_BOTTOM
triple_panel_top = IfcWindowTypePartitioningEnum.TRIPLE_PANEL_TOP
triple_panel_left = IfcWindowTypePartitioningEnum.TRIPLE_PANEL_LEFT
triple_panel_right = IfcWindowTypePartitioningEnum.TRIPLE_PANEL_RIGHT
triple_panel_horizontal = IfcWindowTypePartitioningEnum.TRIPLE_PANEL_HORIZONTAL
userdefined = IfcWindowTypePartitioningEnum.USERDEFINED
notdefined = IfcWindowTypePartitioningEnum.NOTDEFINED
IfcWorkCalendarTypeEnum = enum_namespace()
firstshift = IfcWorkCalendarTypeEnum.FIRSTSHIFT
secondshift = IfcWorkCalendarTypeEnum.SECONDSHIFT
thirdshift = IfcWorkCalendarTypeEnum.THIRDSHIFT
userdefined = IfcWorkCalendarTypeEnum.USERDEFINED
notdefined = IfcWorkCalendarTypeEnum.NOTDEFINED
IfcWorkPlanTypeEnum = enum_namespace()
actual = IfcWorkPlanTypeEnum.ACTUAL
baseline = IfcWorkPlanTypeEnum.BASELINE
planned = IfcWorkPlanTypeEnum.PLANNED
userdefined = IfcWorkPlanTypeEnum.USERDEFINED
notdefined = IfcWorkPlanTypeEnum.NOTDEFINED
IfcWorkScheduleTypeEnum = enum_namespace()
actual = IfcWorkScheduleTypeEnum.ACTUAL
baseline = IfcWorkScheduleTypeEnum.BASELINE
planned = IfcWorkScheduleTypeEnum.PLANNED
userdefined = IfcWorkScheduleTypeEnum.USERDEFINED
notdefined = IfcWorkScheduleTypeEnum.NOTDEFINED

def IfcActionRequest(*args, **kwargs):
    return ifcopenshell.create_entity('IfcActionRequest', 'IFC4X2', *args, **kwargs)

def IfcActor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcActor', 'IFC4X2', *args, **kwargs)

def IfcActorRole(*args, **kwargs):
    return ifcopenshell.create_entity('IfcActorRole', 'IFC4X2', *args, **kwargs)

def IfcActuator(*args, **kwargs):
    return ifcopenshell.create_entity('IfcActuator', 'IFC4X2', *args, **kwargs)

def IfcActuatorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcActuatorType', 'IFC4X2', *args, **kwargs)

def IfcAddress(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAddress', 'IFC4X2', *args, **kwargs)

def IfcAdvancedBrep(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAdvancedBrep', 'IFC4X2', *args, **kwargs)

def IfcAdvancedBrepWithVoids(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAdvancedBrepWithVoids', 'IFC4X2', *args, **kwargs)

def IfcAdvancedFace(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAdvancedFace', 'IFC4X2', *args, **kwargs)

def IfcAirTerminal(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAirTerminal', 'IFC4X2', *args, **kwargs)

def IfcAirTerminalBox(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAirTerminalBox', 'IFC4X2', *args, **kwargs)

def IfcAirTerminalBoxType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAirTerminalBoxType', 'IFC4X2', *args, **kwargs)

def IfcAirTerminalType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAirTerminalType', 'IFC4X2', *args, **kwargs)

def IfcAirToAirHeatRecovery(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAirToAirHeatRecovery', 'IFC4X2', *args, **kwargs)

def IfcAirToAirHeatRecoveryType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAirToAirHeatRecoveryType', 'IFC4X2', *args, **kwargs)

def IfcAlarm(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlarm', 'IFC4X2', *args, **kwargs)

def IfcAlarmType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlarmType', 'IFC4X2', *args, **kwargs)

def IfcAlignment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlignment', 'IFC4X2', *args, **kwargs)

def IfcAlignment2DHorizontal(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlignment2DHorizontal', 'IFC4X2', *args, **kwargs)

def IfcAlignment2DHorizontalSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlignment2DHorizontalSegment', 'IFC4X2', *args, **kwargs)

def IfcAlignment2DSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlignment2DSegment', 'IFC4X2', *args, **kwargs)

def IfcAlignment2DVerSegCircularArc(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlignment2DVerSegCircularArc', 'IFC4X2', *args, **kwargs)

def IfcAlignment2DVerSegLine(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlignment2DVerSegLine', 'IFC4X2', *args, **kwargs)

def IfcAlignment2DVerSegParabolicArc(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlignment2DVerSegParabolicArc', 'IFC4X2', *args, **kwargs)

def IfcAlignment2DVertical(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlignment2DVertical', 'IFC4X2', *args, **kwargs)

def IfcAlignment2DVerticalSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlignment2DVerticalSegment', 'IFC4X2', *args, **kwargs)

def IfcAlignmentCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAlignmentCurve', 'IFC4X2', *args, **kwargs)

def IfcAnnotation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAnnotation', 'IFC4X2', *args, **kwargs)

def IfcAnnotationFillArea(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAnnotationFillArea', 'IFC4X2', *args, **kwargs)

def IfcApplication(*args, **kwargs):
    return ifcopenshell.create_entity('IfcApplication', 'IFC4X2', *args, **kwargs)

def IfcAppliedValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAppliedValue', 'IFC4X2', *args, **kwargs)

def IfcApproval(*args, **kwargs):
    return ifcopenshell.create_entity('IfcApproval', 'IFC4X2', *args, **kwargs)

def IfcApprovalRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcApprovalRelationship', 'IFC4X2', *args, **kwargs)

def IfcArbitraryClosedProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcArbitraryClosedProfileDef', 'IFC4X2', *args, **kwargs)

def IfcArbitraryOpenProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcArbitraryOpenProfileDef', 'IFC4X2', *args, **kwargs)

def IfcArbitraryProfileDefWithVoids(*args, **kwargs):
    return ifcopenshell.create_entity('IfcArbitraryProfileDefWithVoids', 'IFC4X2', *args, **kwargs)

def IfcAsset(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAsset', 'IFC4X2', *args, **kwargs)

def IfcAsymmetricIShapeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAsymmetricIShapeProfileDef', 'IFC4X2', *args, **kwargs)

def IfcAudioVisualAppliance(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAudioVisualAppliance', 'IFC4X2', *args, **kwargs)

def IfcAudioVisualApplianceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAudioVisualApplianceType', 'IFC4X2', *args, **kwargs)

def IfcAxis1Placement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAxis1Placement', 'IFC4X2', *args, **kwargs)

def IfcAxis2Placement2D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAxis2Placement2D', 'IFC4X2', *args, **kwargs)

def IfcAxis2Placement3D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcAxis2Placement3D', 'IFC4X2', *args, **kwargs)

def IfcBSplineCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBSplineCurve', 'IFC4X2', *args, **kwargs)

def IfcBSplineCurveWithKnots(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBSplineCurveWithKnots', 'IFC4X2', *args, **kwargs)

def IfcBSplineSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBSplineSurface', 'IFC4X2', *args, **kwargs)

def IfcBSplineSurfaceWithKnots(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBSplineSurfaceWithKnots', 'IFC4X2', *args, **kwargs)

def IfcBeam(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBeam', 'IFC4X2', *args, **kwargs)

def IfcBeamStandardCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBeamStandardCase', 'IFC4X2', *args, **kwargs)

def IfcBeamType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBeamType', 'IFC4X2', *args, **kwargs)

def IfcBearing(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBearing', 'IFC4X2', *args, **kwargs)

def IfcBearingType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBearingType', 'IFC4X2', *args, **kwargs)

def IfcBlobTexture(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBlobTexture', 'IFC4X2', *args, **kwargs)

def IfcBlock(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBlock', 'IFC4X2', *args, **kwargs)

def IfcBoiler(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoiler', 'IFC4X2', *args, **kwargs)

def IfcBoilerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoilerType', 'IFC4X2', *args, **kwargs)

def IfcBooleanClippingResult(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBooleanClippingResult', 'IFC4X2', *args, **kwargs)

def IfcBooleanResult(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBooleanResult', 'IFC4X2', *args, **kwargs)

def IfcBoundaryCondition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundaryCondition', 'IFC4X2', *args, **kwargs)

def IfcBoundaryCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundaryCurve', 'IFC4X2', *args, **kwargs)

def IfcBoundaryEdgeCondition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundaryEdgeCondition', 'IFC4X2', *args, **kwargs)

def IfcBoundaryFaceCondition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundaryFaceCondition', 'IFC4X2', *args, **kwargs)

def IfcBoundaryNodeCondition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundaryNodeCondition', 'IFC4X2', *args, **kwargs)

def IfcBoundaryNodeConditionWarping(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundaryNodeConditionWarping', 'IFC4X2', *args, **kwargs)

def IfcBoundedCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundedCurve', 'IFC4X2', *args, **kwargs)

def IfcBoundedSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundedSurface', 'IFC4X2', *args, **kwargs)

def IfcBoundingBox(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoundingBox', 'IFC4X2', *args, **kwargs)

def IfcBoxedHalfSpace(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBoxedHalfSpace', 'IFC4X2', *args, **kwargs)

def IfcBridge(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBridge', 'IFC4X2', *args, **kwargs)

def IfcBridgePart(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBridgePart', 'IFC4X2', *args, **kwargs)

def IfcBuilding(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuilding', 'IFC4X2', *args, **kwargs)

def IfcBuildingElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuildingElement', 'IFC4X2', *args, **kwargs)

def IfcBuildingElementPart(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuildingElementPart', 'IFC4X2', *args, **kwargs)

def IfcBuildingElementPartType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuildingElementPartType', 'IFC4X2', *args, **kwargs)

def IfcBuildingElementProxy(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuildingElementProxy', 'IFC4X2', *args, **kwargs)

def IfcBuildingElementProxyType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuildingElementProxyType', 'IFC4X2', *args, **kwargs)

def IfcBuildingElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuildingElementType', 'IFC4X2', *args, **kwargs)

def IfcBuildingStorey(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuildingStorey', 'IFC4X2', *args, **kwargs)

def IfcBuildingSystem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBuildingSystem', 'IFC4X2', *args, **kwargs)

def IfcBurner(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBurner', 'IFC4X2', *args, **kwargs)

def IfcBurnerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcBurnerType', 'IFC4X2', *args, **kwargs)

def IfcCShapeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCShapeProfileDef', 'IFC4X2', *args, **kwargs)

def IfcCableCarrierFitting(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCableCarrierFitting', 'IFC4X2', *args, **kwargs)

def IfcCableCarrierFittingType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCableCarrierFittingType', 'IFC4X2', *args, **kwargs)

def IfcCableCarrierSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCableCarrierSegment', 'IFC4X2', *args, **kwargs)

def IfcCableCarrierSegmentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCableCarrierSegmentType', 'IFC4X2', *args, **kwargs)

def IfcCableFitting(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCableFitting', 'IFC4X2', *args, **kwargs)

def IfcCableFittingType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCableFittingType', 'IFC4X2', *args, **kwargs)

def IfcCableSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCableSegment', 'IFC4X2', *args, **kwargs)

def IfcCableSegmentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCableSegmentType', 'IFC4X2', *args, **kwargs)

def IfcCaissonFoundation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCaissonFoundation', 'IFC4X2', *args, **kwargs)

def IfcCaissonFoundationType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCaissonFoundationType', 'IFC4X2', *args, **kwargs)

def IfcCartesianPoint(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianPoint', 'IFC4X2', *args, **kwargs)

def IfcCartesianPointList(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianPointList', 'IFC4X2', *args, **kwargs)

def IfcCartesianPointList2D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianPointList2D', 'IFC4X2', *args, **kwargs)

def IfcCartesianPointList3D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianPointList3D', 'IFC4X2', *args, **kwargs)

def IfcCartesianTransformationOperator(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianTransformationOperator', 'IFC4X2', *args, **kwargs)

def IfcCartesianTransformationOperator2D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianTransformationOperator2D', 'IFC4X2', *args, **kwargs)

def IfcCartesianTransformationOperator2DnonUniform(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianTransformationOperator2DnonUniform', 'IFC4X2', *args, **kwargs)

def IfcCartesianTransformationOperator3D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianTransformationOperator3D', 'IFC4X2', *args, **kwargs)

def IfcCartesianTransformationOperator3DnonUniform(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCartesianTransformationOperator3DnonUniform', 'IFC4X2', *args, **kwargs)

def IfcCenterLineProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCenterLineProfileDef', 'IFC4X2', *args, **kwargs)

def IfcChiller(*args, **kwargs):
    return ifcopenshell.create_entity('IfcChiller', 'IFC4X2', *args, **kwargs)

def IfcChillerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcChillerType', 'IFC4X2', *args, **kwargs)

def IfcChimney(*args, **kwargs):
    return ifcopenshell.create_entity('IfcChimney', 'IFC4X2', *args, **kwargs)

def IfcChimneyType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcChimneyType', 'IFC4X2', *args, **kwargs)

def IfcCircle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCircle', 'IFC4X2', *args, **kwargs)

def IfcCircleHollowProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCircleHollowProfileDef', 'IFC4X2', *args, **kwargs)

def IfcCircleProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCircleProfileDef', 'IFC4X2', *args, **kwargs)

def IfcCircularArcSegment2D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCircularArcSegment2D', 'IFC4X2', *args, **kwargs)

def IfcCivilElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCivilElement', 'IFC4X2', *args, **kwargs)

def IfcCivilElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCivilElementType', 'IFC4X2', *args, **kwargs)

def IfcClassification(*args, **kwargs):
    return ifcopenshell.create_entity('IfcClassification', 'IFC4X2', *args, **kwargs)

def IfcClassificationReference(*args, **kwargs):
    return ifcopenshell.create_entity('IfcClassificationReference', 'IFC4X2', *args, **kwargs)

def IfcClosedShell(*args, **kwargs):
    return ifcopenshell.create_entity('IfcClosedShell', 'IFC4X2', *args, **kwargs)

def IfcCoil(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCoil', 'IFC4X2', *args, **kwargs)

def IfcCoilType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCoilType', 'IFC4X2', *args, **kwargs)

def IfcColourRgb(*args, **kwargs):
    return ifcopenshell.create_entity('IfcColourRgb', 'IFC4X2', *args, **kwargs)

def IfcColourRgbList(*args, **kwargs):
    return ifcopenshell.create_entity('IfcColourRgbList', 'IFC4X2', *args, **kwargs)

def IfcColourSpecification(*args, **kwargs):
    return ifcopenshell.create_entity('IfcColourSpecification', 'IFC4X2', *args, **kwargs)

def IfcColumn(*args, **kwargs):
    return ifcopenshell.create_entity('IfcColumn', 'IFC4X2', *args, **kwargs)

def IfcColumnStandardCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcColumnStandardCase', 'IFC4X2', *args, **kwargs)

def IfcColumnType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcColumnType', 'IFC4X2', *args, **kwargs)

def IfcCommunicationsAppliance(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCommunicationsAppliance', 'IFC4X2', *args, **kwargs)

def IfcCommunicationsApplianceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCommunicationsApplianceType', 'IFC4X2', *args, **kwargs)

def IfcComplexProperty(*args, **kwargs):
    return ifcopenshell.create_entity('IfcComplexProperty', 'IFC4X2', *args, **kwargs)

def IfcComplexPropertyTemplate(*args, **kwargs):
    return ifcopenshell.create_entity('IfcComplexPropertyTemplate', 'IFC4X2', *args, **kwargs)

def IfcCompositeCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCompositeCurve', 'IFC4X2', *args, **kwargs)

def IfcCompositeCurveOnSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCompositeCurveOnSurface', 'IFC4X2', *args, **kwargs)

def IfcCompositeCurveSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCompositeCurveSegment', 'IFC4X2', *args, **kwargs)

def IfcCompositeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCompositeProfileDef', 'IFC4X2', *args, **kwargs)

def IfcCompressor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCompressor', 'IFC4X2', *args, **kwargs)

def IfcCompressorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCompressorType', 'IFC4X2', *args, **kwargs)

def IfcCondenser(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCondenser', 'IFC4X2', *args, **kwargs)

def IfcCondenserType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCondenserType', 'IFC4X2', *args, **kwargs)

def IfcConic(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConic', 'IFC4X2', *args, **kwargs)

def IfcConnectedFaceSet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConnectedFaceSet', 'IFC4X2', *args, **kwargs)

def IfcConnectionCurveGeometry(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConnectionCurveGeometry', 'IFC4X2', *args, **kwargs)

def IfcConnectionGeometry(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConnectionGeometry', 'IFC4X2', *args, **kwargs)

def IfcConnectionPointEccentricity(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConnectionPointEccentricity', 'IFC4X2', *args, **kwargs)

def IfcConnectionPointGeometry(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConnectionPointGeometry', 'IFC4X2', *args, **kwargs)

def IfcConnectionSurfaceGeometry(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConnectionSurfaceGeometry', 'IFC4X2', *args, **kwargs)

def IfcConnectionVolumeGeometry(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConnectionVolumeGeometry', 'IFC4X2', *args, **kwargs)

def IfcConstraint(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstraint', 'IFC4X2', *args, **kwargs)

def IfcConstructionEquipmentResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstructionEquipmentResource', 'IFC4X2', *args, **kwargs)

def IfcConstructionEquipmentResourceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstructionEquipmentResourceType', 'IFC4X2', *args, **kwargs)

def IfcConstructionMaterialResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstructionMaterialResource', 'IFC4X2', *args, **kwargs)

def IfcConstructionMaterialResourceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstructionMaterialResourceType', 'IFC4X2', *args, **kwargs)

def IfcConstructionProductResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstructionProductResource', 'IFC4X2', *args, **kwargs)

def IfcConstructionProductResourceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstructionProductResourceType', 'IFC4X2', *args, **kwargs)

def IfcConstructionResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstructionResource', 'IFC4X2', *args, **kwargs)

def IfcConstructionResourceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConstructionResourceType', 'IFC4X2', *args, **kwargs)

def IfcContext(*args, **kwargs):
    return ifcopenshell.create_entity('IfcContext', 'IFC4X2', *args, **kwargs)

def IfcContextDependentUnit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcContextDependentUnit', 'IFC4X2', *args, **kwargs)

def IfcControl(*args, **kwargs):
    return ifcopenshell.create_entity('IfcControl', 'IFC4X2', *args, **kwargs)

def IfcController(*args, **kwargs):
    return ifcopenshell.create_entity('IfcController', 'IFC4X2', *args, **kwargs)

def IfcControllerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcControllerType', 'IFC4X2', *args, **kwargs)

def IfcConversionBasedUnit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConversionBasedUnit', 'IFC4X2', *args, **kwargs)

def IfcConversionBasedUnitWithOffset(*args, **kwargs):
    return ifcopenshell.create_entity('IfcConversionBasedUnitWithOffset', 'IFC4X2', *args, **kwargs)

def IfcCooledBeam(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCooledBeam', 'IFC4X2', *args, **kwargs)

def IfcCooledBeamType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCooledBeamType', 'IFC4X2', *args, **kwargs)

def IfcCoolingTower(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCoolingTower', 'IFC4X2', *args, **kwargs)

def IfcCoolingTowerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCoolingTowerType', 'IFC4X2', *args, **kwargs)

def IfcCoordinateOperation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCoordinateOperation', 'IFC4X2', *args, **kwargs)

def IfcCoordinateReferenceSystem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCoordinateReferenceSystem', 'IFC4X2', *args, **kwargs)

def IfcCostItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCostItem', 'IFC4X2', *args, **kwargs)

def IfcCostSchedule(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCostSchedule', 'IFC4X2', *args, **kwargs)

def IfcCostValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCostValue', 'IFC4X2', *args, **kwargs)

def IfcCovering(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCovering', 'IFC4X2', *args, **kwargs)

def IfcCoveringType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCoveringType', 'IFC4X2', *args, **kwargs)

def IfcCrewResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCrewResource', 'IFC4X2', *args, **kwargs)

def IfcCrewResourceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCrewResourceType', 'IFC4X2', *args, **kwargs)

def IfcCsgPrimitive3D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCsgPrimitive3D', 'IFC4X2', *args, **kwargs)

def IfcCsgSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCsgSolid', 'IFC4X2', *args, **kwargs)

def IfcCurrencyRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurrencyRelationship', 'IFC4X2', *args, **kwargs)

def IfcCurtainWall(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurtainWall', 'IFC4X2', *args, **kwargs)

def IfcCurtainWallType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurtainWallType', 'IFC4X2', *args, **kwargs)

def IfcCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurve', 'IFC4X2', *args, **kwargs)

def IfcCurveBoundedPlane(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurveBoundedPlane', 'IFC4X2', *args, **kwargs)

def IfcCurveBoundedSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurveBoundedSurface', 'IFC4X2', *args, **kwargs)

def IfcCurveSegment2D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurveSegment2D', 'IFC4X2', *args, **kwargs)

def IfcCurveStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurveStyle', 'IFC4X2', *args, **kwargs)

def IfcCurveStyleFont(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurveStyleFont', 'IFC4X2', *args, **kwargs)

def IfcCurveStyleFontAndScaling(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurveStyleFontAndScaling', 'IFC4X2', *args, **kwargs)

def IfcCurveStyleFontPattern(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCurveStyleFontPattern', 'IFC4X2', *args, **kwargs)

def IfcCylindricalSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcCylindricalSurface', 'IFC4X2', *args, **kwargs)

def IfcDamper(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDamper', 'IFC4X2', *args, **kwargs)

def IfcDamperType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDamperType', 'IFC4X2', *args, **kwargs)

def IfcDeepFoundation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDeepFoundation', 'IFC4X2', *args, **kwargs)

def IfcDeepFoundationType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDeepFoundationType', 'IFC4X2', *args, **kwargs)

def IfcDerivedProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDerivedProfileDef', 'IFC4X2', *args, **kwargs)

def IfcDerivedUnit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDerivedUnit', 'IFC4X2', *args, **kwargs)

def IfcDerivedUnitElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDerivedUnitElement', 'IFC4X2', *args, **kwargs)

def IfcDimensionalExponents(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDimensionalExponents', 'IFC4X2', *args, **kwargs)

def IfcDirection(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDirection', 'IFC4X2', *args, **kwargs)

def IfcDiscreteAccessory(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDiscreteAccessory', 'IFC4X2', *args, **kwargs)

def IfcDiscreteAccessoryType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDiscreteAccessoryType', 'IFC4X2', *args, **kwargs)

def IfcDistanceExpression(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistanceExpression', 'IFC4X2', *args, **kwargs)

def IfcDistributionChamberElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionChamberElement', 'IFC4X2', *args, **kwargs)

def IfcDistributionChamberElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionChamberElementType', 'IFC4X2', *args, **kwargs)

def IfcDistributionCircuit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionCircuit', 'IFC4X2', *args, **kwargs)

def IfcDistributionControlElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionControlElement', 'IFC4X2', *args, **kwargs)

def IfcDistributionControlElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionControlElementType', 'IFC4X2', *args, **kwargs)

def IfcDistributionElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionElement', 'IFC4X2', *args, **kwargs)

def IfcDistributionElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionElementType', 'IFC4X2', *args, **kwargs)

def IfcDistributionFlowElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionFlowElement', 'IFC4X2', *args, **kwargs)

def IfcDistributionFlowElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionFlowElementType', 'IFC4X2', *args, **kwargs)

def IfcDistributionPort(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionPort', 'IFC4X2', *args, **kwargs)

def IfcDistributionSystem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDistributionSystem', 'IFC4X2', *args, **kwargs)

def IfcDocumentInformation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDocumentInformation', 'IFC4X2', *args, **kwargs)

def IfcDocumentInformationRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDocumentInformationRelationship', 'IFC4X2', *args, **kwargs)

def IfcDocumentReference(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDocumentReference', 'IFC4X2', *args, **kwargs)

def IfcDoor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDoor', 'IFC4X2', *args, **kwargs)

def IfcDoorLiningProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDoorLiningProperties', 'IFC4X2', *args, **kwargs)

def IfcDoorPanelProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDoorPanelProperties', 'IFC4X2', *args, **kwargs)

def IfcDoorStandardCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDoorStandardCase', 'IFC4X2', *args, **kwargs)

def IfcDoorStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDoorStyle', 'IFC4X2', *args, **kwargs)

def IfcDoorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDoorType', 'IFC4X2', *args, **kwargs)

def IfcDraughtingPreDefinedColour(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDraughtingPreDefinedColour', 'IFC4X2', *args, **kwargs)

def IfcDraughtingPreDefinedCurveFont(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDraughtingPreDefinedCurveFont', 'IFC4X2', *args, **kwargs)

def IfcDuctFitting(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDuctFitting', 'IFC4X2', *args, **kwargs)

def IfcDuctFittingType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDuctFittingType', 'IFC4X2', *args, **kwargs)

def IfcDuctSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDuctSegment', 'IFC4X2', *args, **kwargs)

def IfcDuctSegmentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDuctSegmentType', 'IFC4X2', *args, **kwargs)

def IfcDuctSilencer(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDuctSilencer', 'IFC4X2', *args, **kwargs)

def IfcDuctSilencerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcDuctSilencerType', 'IFC4X2', *args, **kwargs)

def IfcEdge(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEdge', 'IFC4X2', *args, **kwargs)

def IfcEdgeCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEdgeCurve', 'IFC4X2', *args, **kwargs)

def IfcEdgeLoop(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEdgeLoop', 'IFC4X2', *args, **kwargs)

def IfcElectricAppliance(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricAppliance', 'IFC4X2', *args, **kwargs)

def IfcElectricApplianceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricApplianceType', 'IFC4X2', *args, **kwargs)

def IfcElectricDistributionBoard(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricDistributionBoard', 'IFC4X2', *args, **kwargs)

def IfcElectricDistributionBoardType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricDistributionBoardType', 'IFC4X2', *args, **kwargs)

def IfcElectricFlowStorageDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricFlowStorageDevice', 'IFC4X2', *args, **kwargs)

def IfcElectricFlowStorageDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricFlowStorageDeviceType', 'IFC4X2', *args, **kwargs)

def IfcElectricGenerator(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricGenerator', 'IFC4X2', *args, **kwargs)

def IfcElectricGeneratorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricGeneratorType', 'IFC4X2', *args, **kwargs)

def IfcElectricMotor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricMotor', 'IFC4X2', *args, **kwargs)

def IfcElectricMotorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricMotorType', 'IFC4X2', *args, **kwargs)

def IfcElectricTimeControl(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricTimeControl', 'IFC4X2', *args, **kwargs)

def IfcElectricTimeControlType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElectricTimeControlType', 'IFC4X2', *args, **kwargs)

def IfcElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElement', 'IFC4X2', *args, **kwargs)

def IfcElementAssembly(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElementAssembly', 'IFC4X2', *args, **kwargs)

def IfcElementAssemblyType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElementAssemblyType', 'IFC4X2', *args, **kwargs)

def IfcElementComponent(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElementComponent', 'IFC4X2', *args, **kwargs)

def IfcElementComponentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElementComponentType', 'IFC4X2', *args, **kwargs)

def IfcElementQuantity(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElementQuantity', 'IFC4X2', *args, **kwargs)

def IfcElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElementType', 'IFC4X2', *args, **kwargs)

def IfcElementarySurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcElementarySurface', 'IFC4X2', *args, **kwargs)

def IfcEllipse(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEllipse', 'IFC4X2', *args, **kwargs)

def IfcEllipseProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEllipseProfileDef', 'IFC4X2', *args, **kwargs)

def IfcEnergyConversionDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEnergyConversionDevice', 'IFC4X2', *args, **kwargs)

def IfcEnergyConversionDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEnergyConversionDeviceType', 'IFC4X2', *args, **kwargs)

def IfcEngine(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEngine', 'IFC4X2', *args, **kwargs)

def IfcEngineType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEngineType', 'IFC4X2', *args, **kwargs)

def IfcEvaporativeCooler(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEvaporativeCooler', 'IFC4X2', *args, **kwargs)

def IfcEvaporativeCoolerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEvaporativeCoolerType', 'IFC4X2', *args, **kwargs)

def IfcEvaporator(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEvaporator', 'IFC4X2', *args, **kwargs)

def IfcEvaporatorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEvaporatorType', 'IFC4X2', *args, **kwargs)

def IfcEvent(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEvent', 'IFC4X2', *args, **kwargs)

def IfcEventTime(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEventTime', 'IFC4X2', *args, **kwargs)

def IfcEventType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcEventType', 'IFC4X2', *args, **kwargs)

def IfcExtendedProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExtendedProperties', 'IFC4X2', *args, **kwargs)

def IfcExternalInformation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExternalInformation', 'IFC4X2', *args, **kwargs)

def IfcExternalReference(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExternalReference', 'IFC4X2', *args, **kwargs)

def IfcExternalReferenceRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExternalReferenceRelationship', 'IFC4X2', *args, **kwargs)

def IfcExternalSpatialElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExternalSpatialElement', 'IFC4X2', *args, **kwargs)

def IfcExternalSpatialStructureElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExternalSpatialStructureElement', 'IFC4X2', *args, **kwargs)

def IfcExternallyDefinedHatchStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExternallyDefinedHatchStyle', 'IFC4X2', *args, **kwargs)

def IfcExternallyDefinedSurfaceStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExternallyDefinedSurfaceStyle', 'IFC4X2', *args, **kwargs)

def IfcExternallyDefinedTextFont(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExternallyDefinedTextFont', 'IFC4X2', *args, **kwargs)

def IfcExtrudedAreaSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExtrudedAreaSolid', 'IFC4X2', *args, **kwargs)

def IfcExtrudedAreaSolidTapered(*args, **kwargs):
    return ifcopenshell.create_entity('IfcExtrudedAreaSolidTapered', 'IFC4X2', *args, **kwargs)

def IfcFace(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFace', 'IFC4X2', *args, **kwargs)

def IfcFaceBasedSurfaceModel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFaceBasedSurfaceModel', 'IFC4X2', *args, **kwargs)

def IfcFaceBound(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFaceBound', 'IFC4X2', *args, **kwargs)

def IfcFaceOuterBound(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFaceOuterBound', 'IFC4X2', *args, **kwargs)

def IfcFaceSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFaceSurface', 'IFC4X2', *args, **kwargs)

def IfcFacetedBrep(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFacetedBrep', 'IFC4X2', *args, **kwargs)

def IfcFacetedBrepWithVoids(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFacetedBrepWithVoids', 'IFC4X2', *args, **kwargs)

def IfcFacility(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFacility', 'IFC4X2', *args, **kwargs)

def IfcFacilityPart(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFacilityPart', 'IFC4X2', *args, **kwargs)

def IfcFailureConnectionCondition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFailureConnectionCondition', 'IFC4X2', *args, **kwargs)

def IfcFan(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFan', 'IFC4X2', *args, **kwargs)

def IfcFanType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFanType', 'IFC4X2', *args, **kwargs)

def IfcFastener(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFastener', 'IFC4X2', *args, **kwargs)

def IfcFastenerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFastenerType', 'IFC4X2', *args, **kwargs)

def IfcFeatureElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFeatureElement', 'IFC4X2', *args, **kwargs)

def IfcFeatureElementAddition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFeatureElementAddition', 'IFC4X2', *args, **kwargs)

def IfcFeatureElementSubtraction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFeatureElementSubtraction', 'IFC4X2', *args, **kwargs)

def IfcFillAreaStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFillAreaStyle', 'IFC4X2', *args, **kwargs)

def IfcFillAreaStyleHatching(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFillAreaStyleHatching', 'IFC4X2', *args, **kwargs)

def IfcFillAreaStyleTiles(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFillAreaStyleTiles', 'IFC4X2', *args, **kwargs)

def IfcFilter(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFilter', 'IFC4X2', *args, **kwargs)

def IfcFilterType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFilterType', 'IFC4X2', *args, **kwargs)

def IfcFireSuppressionTerminal(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFireSuppressionTerminal', 'IFC4X2', *args, **kwargs)

def IfcFireSuppressionTerminalType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFireSuppressionTerminalType', 'IFC4X2', *args, **kwargs)

def IfcFixedReferenceSweptAreaSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFixedReferenceSweptAreaSolid', 'IFC4X2', *args, **kwargs)

def IfcFlowController(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowController', 'IFC4X2', *args, **kwargs)

def IfcFlowControllerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowControllerType', 'IFC4X2', *args, **kwargs)

def IfcFlowFitting(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowFitting', 'IFC4X2', *args, **kwargs)

def IfcFlowFittingType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowFittingType', 'IFC4X2', *args, **kwargs)

def IfcFlowInstrument(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowInstrument', 'IFC4X2', *args, **kwargs)

def IfcFlowInstrumentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowInstrumentType', 'IFC4X2', *args, **kwargs)

def IfcFlowMeter(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowMeter', 'IFC4X2', *args, **kwargs)

def IfcFlowMeterType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowMeterType', 'IFC4X2', *args, **kwargs)

def IfcFlowMovingDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowMovingDevice', 'IFC4X2', *args, **kwargs)

def IfcFlowMovingDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowMovingDeviceType', 'IFC4X2', *args, **kwargs)

def IfcFlowSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowSegment', 'IFC4X2', *args, **kwargs)

def IfcFlowSegmentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowSegmentType', 'IFC4X2', *args, **kwargs)

def IfcFlowStorageDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowStorageDevice', 'IFC4X2', *args, **kwargs)

def IfcFlowStorageDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowStorageDeviceType', 'IFC4X2', *args, **kwargs)

def IfcFlowTerminal(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowTerminal', 'IFC4X2', *args, **kwargs)

def IfcFlowTerminalType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowTerminalType', 'IFC4X2', *args, **kwargs)

def IfcFlowTreatmentDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowTreatmentDevice', 'IFC4X2', *args, **kwargs)

def IfcFlowTreatmentDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFlowTreatmentDeviceType', 'IFC4X2', *args, **kwargs)

def IfcFooting(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFooting', 'IFC4X2', *args, **kwargs)

def IfcFootingType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFootingType', 'IFC4X2', *args, **kwargs)

def IfcFurnishingElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFurnishingElement', 'IFC4X2', *args, **kwargs)

def IfcFurnishingElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFurnishingElementType', 'IFC4X2', *args, **kwargs)

def IfcFurniture(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFurniture', 'IFC4X2', *args, **kwargs)

def IfcFurnitureType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcFurnitureType', 'IFC4X2', *args, **kwargs)

def IfcGeographicElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeographicElement', 'IFC4X2', *args, **kwargs)

def IfcGeographicElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeographicElementType', 'IFC4X2', *args, **kwargs)

def IfcGeometricCurveSet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeometricCurveSet', 'IFC4X2', *args, **kwargs)

def IfcGeometricRepresentationContext(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeometricRepresentationContext', 'IFC4X2', *args, **kwargs)

def IfcGeometricRepresentationItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeometricRepresentationItem', 'IFC4X2', *args, **kwargs)

def IfcGeometricRepresentationSubContext(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeometricRepresentationSubContext', 'IFC4X2', *args, **kwargs)

def IfcGeometricSet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGeometricSet', 'IFC4X2', *args, **kwargs)

def IfcGrid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGrid', 'IFC4X2', *args, **kwargs)

def IfcGridAxis(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGridAxis', 'IFC4X2', *args, **kwargs)

def IfcGridPlacement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGridPlacement', 'IFC4X2', *args, **kwargs)

def IfcGroup(*args, **kwargs):
    return ifcopenshell.create_entity('IfcGroup', 'IFC4X2', *args, **kwargs)

def IfcHalfSpaceSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcHalfSpaceSolid', 'IFC4X2', *args, **kwargs)

def IfcHeatExchanger(*args, **kwargs):
    return ifcopenshell.create_entity('IfcHeatExchanger', 'IFC4X2', *args, **kwargs)

def IfcHeatExchangerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcHeatExchangerType', 'IFC4X2', *args, **kwargs)

def IfcHumidifier(*args, **kwargs):
    return ifcopenshell.create_entity('IfcHumidifier', 'IFC4X2', *args, **kwargs)

def IfcHumidifierType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcHumidifierType', 'IFC4X2', *args, **kwargs)

def IfcIShapeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIShapeProfileDef', 'IFC4X2', *args, **kwargs)

def IfcImageTexture(*args, **kwargs):
    return ifcopenshell.create_entity('IfcImageTexture', 'IFC4X2', *args, **kwargs)

def IfcIndexedColourMap(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIndexedColourMap', 'IFC4X2', *args, **kwargs)

def IfcIndexedPolyCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIndexedPolyCurve', 'IFC4X2', *args, **kwargs)

def IfcIndexedPolygonalFace(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIndexedPolygonalFace', 'IFC4X2', *args, **kwargs)

def IfcIndexedPolygonalFaceWithVoids(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIndexedPolygonalFaceWithVoids', 'IFC4X2', *args, **kwargs)

def IfcIndexedTextureMap(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIndexedTextureMap', 'IFC4X2', *args, **kwargs)

def IfcIndexedTriangleTextureMap(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIndexedTriangleTextureMap', 'IFC4X2', *args, **kwargs)

def IfcInterceptor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcInterceptor', 'IFC4X2', *args, **kwargs)

def IfcInterceptorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcInterceptorType', 'IFC4X2', *args, **kwargs)

def IfcIntersectionCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIntersectionCurve', 'IFC4X2', *args, **kwargs)

def IfcInventory(*args, **kwargs):
    return ifcopenshell.create_entity('IfcInventory', 'IFC4X2', *args, **kwargs)

def IfcIrregularTimeSeries(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIrregularTimeSeries', 'IFC4X2', *args, **kwargs)

def IfcIrregularTimeSeriesValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcIrregularTimeSeriesValue', 'IFC4X2', *args, **kwargs)

def IfcJunctionBox(*args, **kwargs):
    return ifcopenshell.create_entity('IfcJunctionBox', 'IFC4X2', *args, **kwargs)

def IfcJunctionBoxType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcJunctionBoxType', 'IFC4X2', *args, **kwargs)

def IfcLShapeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLShapeProfileDef', 'IFC4X2', *args, **kwargs)

def IfcLaborResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLaborResource', 'IFC4X2', *args, **kwargs)

def IfcLaborResourceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLaborResourceType', 'IFC4X2', *args, **kwargs)

def IfcLagTime(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLagTime', 'IFC4X2', *args, **kwargs)

def IfcLamp(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLamp', 'IFC4X2', *args, **kwargs)

def IfcLampType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLampType', 'IFC4X2', *args, **kwargs)

def IfcLibraryInformation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLibraryInformation', 'IFC4X2', *args, **kwargs)

def IfcLibraryReference(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLibraryReference', 'IFC4X2', *args, **kwargs)

def IfcLightDistributionData(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightDistributionData', 'IFC4X2', *args, **kwargs)

def IfcLightFixture(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightFixture', 'IFC4X2', *args, **kwargs)

def IfcLightFixtureType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightFixtureType', 'IFC4X2', *args, **kwargs)

def IfcLightIntensityDistribution(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightIntensityDistribution', 'IFC4X2', *args, **kwargs)

def IfcLightSource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightSource', 'IFC4X2', *args, **kwargs)

def IfcLightSourceAmbient(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightSourceAmbient', 'IFC4X2', *args, **kwargs)

def IfcLightSourceDirectional(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightSourceDirectional', 'IFC4X2', *args, **kwargs)

def IfcLightSourceGoniometric(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightSourceGoniometric', 'IFC4X2', *args, **kwargs)

def IfcLightSourcePositional(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightSourcePositional', 'IFC4X2', *args, **kwargs)

def IfcLightSourceSpot(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLightSourceSpot', 'IFC4X2', *args, **kwargs)

def IfcLine(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLine', 'IFC4X2', *args, **kwargs)

def IfcLineSegment2D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLineSegment2D', 'IFC4X2', *args, **kwargs)

def IfcLinearPlacement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLinearPlacement', 'IFC4X2', *args, **kwargs)

def IfcLinearPositioningElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLinearPositioningElement', 'IFC4X2', *args, **kwargs)

def IfcLocalPlacement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLocalPlacement', 'IFC4X2', *args, **kwargs)

def IfcLoop(*args, **kwargs):
    return ifcopenshell.create_entity('IfcLoop', 'IFC4X2', *args, **kwargs)

def IfcManifoldSolidBrep(*args, **kwargs):
    return ifcopenshell.create_entity('IfcManifoldSolidBrep', 'IFC4X2', *args, **kwargs)

def IfcMapConversion(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMapConversion', 'IFC4X2', *args, **kwargs)

def IfcMappedItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMappedItem', 'IFC4X2', *args, **kwargs)

def IfcMaterial(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterial', 'IFC4X2', *args, **kwargs)

def IfcMaterialClassificationRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialClassificationRelationship', 'IFC4X2', *args, **kwargs)

def IfcMaterialConstituent(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialConstituent', 'IFC4X2', *args, **kwargs)

def IfcMaterialConstituentSet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialConstituentSet', 'IFC4X2', *args, **kwargs)

def IfcMaterialDefinition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialDefinition', 'IFC4X2', *args, **kwargs)

def IfcMaterialDefinitionRepresentation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialDefinitionRepresentation', 'IFC4X2', *args, **kwargs)

def IfcMaterialLayer(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialLayer', 'IFC4X2', *args, **kwargs)

def IfcMaterialLayerSet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialLayerSet', 'IFC4X2', *args, **kwargs)

def IfcMaterialLayerSetUsage(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialLayerSetUsage', 'IFC4X2', *args, **kwargs)

def IfcMaterialLayerWithOffsets(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialLayerWithOffsets', 'IFC4X2', *args, **kwargs)

def IfcMaterialList(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialList', 'IFC4X2', *args, **kwargs)

def IfcMaterialProfile(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialProfile', 'IFC4X2', *args, **kwargs)

def IfcMaterialProfileSet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialProfileSet', 'IFC4X2', *args, **kwargs)

def IfcMaterialProfileSetUsage(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialProfileSetUsage', 'IFC4X2', *args, **kwargs)

def IfcMaterialProfileSetUsageTapering(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialProfileSetUsageTapering', 'IFC4X2', *args, **kwargs)

def IfcMaterialProfileWithOffsets(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialProfileWithOffsets', 'IFC4X2', *args, **kwargs)

def IfcMaterialProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialProperties', 'IFC4X2', *args, **kwargs)

def IfcMaterialRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialRelationship', 'IFC4X2', *args, **kwargs)

def IfcMaterialUsageDefinition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMaterialUsageDefinition', 'IFC4X2', *args, **kwargs)

def IfcMeasureWithUnit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMeasureWithUnit', 'IFC4X2', *args, **kwargs)

def IfcMechanicalFastener(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMechanicalFastener', 'IFC4X2', *args, **kwargs)

def IfcMechanicalFastenerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMechanicalFastenerType', 'IFC4X2', *args, **kwargs)

def IfcMedicalDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMedicalDevice', 'IFC4X2', *args, **kwargs)

def IfcMedicalDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMedicalDeviceType', 'IFC4X2', *args, **kwargs)

def IfcMember(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMember', 'IFC4X2', *args, **kwargs)

def IfcMemberStandardCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMemberStandardCase', 'IFC4X2', *args, **kwargs)

def IfcMemberType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMemberType', 'IFC4X2', *args, **kwargs)

def IfcMetric(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMetric', 'IFC4X2', *args, **kwargs)

def IfcMirroredProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMirroredProfileDef', 'IFC4X2', *args, **kwargs)

def IfcMonetaryUnit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMonetaryUnit', 'IFC4X2', *args, **kwargs)

def IfcMotorConnection(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMotorConnection', 'IFC4X2', *args, **kwargs)

def IfcMotorConnectionType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcMotorConnectionType', 'IFC4X2', *args, **kwargs)

def IfcNamedUnit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcNamedUnit', 'IFC4X2', *args, **kwargs)

def IfcObject(*args, **kwargs):
    return ifcopenshell.create_entity('IfcObject', 'IFC4X2', *args, **kwargs)

def IfcObjectDefinition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcObjectDefinition', 'IFC4X2', *args, **kwargs)

def IfcObjectPlacement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcObjectPlacement', 'IFC4X2', *args, **kwargs)

def IfcObjective(*args, **kwargs):
    return ifcopenshell.create_entity('IfcObjective', 'IFC4X2', *args, **kwargs)

def IfcOccupant(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOccupant', 'IFC4X2', *args, **kwargs)

def IfcOffsetCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOffsetCurve', 'IFC4X2', *args, **kwargs)

def IfcOffsetCurve2D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOffsetCurve2D', 'IFC4X2', *args, **kwargs)

def IfcOffsetCurve3D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOffsetCurve3D', 'IFC4X2', *args, **kwargs)

def IfcOffsetCurveByDistances(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOffsetCurveByDistances', 'IFC4X2', *args, **kwargs)

def IfcOpenShell(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOpenShell', 'IFC4X2', *args, **kwargs)

def IfcOpeningElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOpeningElement', 'IFC4X2', *args, **kwargs)

def IfcOpeningStandardCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOpeningStandardCase', 'IFC4X2', *args, **kwargs)

def IfcOrganization(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOrganization', 'IFC4X2', *args, **kwargs)

def IfcOrganizationRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOrganizationRelationship', 'IFC4X2', *args, **kwargs)

def IfcOrientationExpression(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOrientationExpression', 'IFC4X2', *args, **kwargs)

def IfcOrientedEdge(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOrientedEdge', 'IFC4X2', *args, **kwargs)

def IfcOuterBoundaryCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOuterBoundaryCurve', 'IFC4X2', *args, **kwargs)

def IfcOutlet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOutlet', 'IFC4X2', *args, **kwargs)

def IfcOutletType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOutletType', 'IFC4X2', *args, **kwargs)

def IfcOwnerHistory(*args, **kwargs):
    return ifcopenshell.create_entity('IfcOwnerHistory', 'IFC4X2', *args, **kwargs)

def IfcParameterizedProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcParameterizedProfileDef', 'IFC4X2', *args, **kwargs)

def IfcPath(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPath', 'IFC4X2', *args, **kwargs)

def IfcPcurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPcurve', 'IFC4X2', *args, **kwargs)

def IfcPerformanceHistory(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPerformanceHistory', 'IFC4X2', *args, **kwargs)

def IfcPermeableCoveringProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPermeableCoveringProperties', 'IFC4X2', *args, **kwargs)

def IfcPermit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPermit', 'IFC4X2', *args, **kwargs)

def IfcPerson(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPerson', 'IFC4X2', *args, **kwargs)

def IfcPersonAndOrganization(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPersonAndOrganization', 'IFC4X2', *args, **kwargs)

def IfcPhysicalComplexQuantity(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPhysicalComplexQuantity', 'IFC4X2', *args, **kwargs)

def IfcPhysicalQuantity(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPhysicalQuantity', 'IFC4X2', *args, **kwargs)

def IfcPhysicalSimpleQuantity(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPhysicalSimpleQuantity', 'IFC4X2', *args, **kwargs)

def IfcPile(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPile', 'IFC4X2', *args, **kwargs)

def IfcPileType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPileType', 'IFC4X2', *args, **kwargs)

def IfcPipeFitting(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPipeFitting', 'IFC4X2', *args, **kwargs)

def IfcPipeFittingType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPipeFittingType', 'IFC4X2', *args, **kwargs)

def IfcPipeSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPipeSegment', 'IFC4X2', *args, **kwargs)

def IfcPipeSegmentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPipeSegmentType', 'IFC4X2', *args, **kwargs)

def IfcPixelTexture(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPixelTexture', 'IFC4X2', *args, **kwargs)

def IfcPlacement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPlacement', 'IFC4X2', *args, **kwargs)

def IfcPlanarBox(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPlanarBox', 'IFC4X2', *args, **kwargs)

def IfcPlanarExtent(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPlanarExtent', 'IFC4X2', *args, **kwargs)

def IfcPlane(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPlane', 'IFC4X2', *args, **kwargs)

def IfcPlate(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPlate', 'IFC4X2', *args, **kwargs)

def IfcPlateStandardCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPlateStandardCase', 'IFC4X2', *args, **kwargs)

def IfcPlateType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPlateType', 'IFC4X2', *args, **kwargs)

def IfcPoint(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPoint', 'IFC4X2', *args, **kwargs)

def IfcPointOnCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPointOnCurve', 'IFC4X2', *args, **kwargs)

def IfcPointOnSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPointOnSurface', 'IFC4X2', *args, **kwargs)

def IfcPolyLoop(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPolyLoop', 'IFC4X2', *args, **kwargs)

def IfcPolygonalBoundedHalfSpace(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPolygonalBoundedHalfSpace', 'IFC4X2', *args, **kwargs)

def IfcPolygonalFaceSet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPolygonalFaceSet', 'IFC4X2', *args, **kwargs)

def IfcPolyline(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPolyline', 'IFC4X2', *args, **kwargs)

def IfcPort(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPort', 'IFC4X2', *args, **kwargs)

def IfcPositioningElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPositioningElement', 'IFC4X2', *args, **kwargs)

def IfcPostalAddress(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPostalAddress', 'IFC4X2', *args, **kwargs)

def IfcPreDefinedColour(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPreDefinedColour', 'IFC4X2', *args, **kwargs)

def IfcPreDefinedCurveFont(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPreDefinedCurveFont', 'IFC4X2', *args, **kwargs)

def IfcPreDefinedItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPreDefinedItem', 'IFC4X2', *args, **kwargs)

def IfcPreDefinedProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPreDefinedProperties', 'IFC4X2', *args, **kwargs)

def IfcPreDefinedPropertySet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPreDefinedPropertySet', 'IFC4X2', *args, **kwargs)

def IfcPreDefinedTextFont(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPreDefinedTextFont', 'IFC4X2', *args, **kwargs)

def IfcPresentationItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPresentationItem', 'IFC4X2', *args, **kwargs)

def IfcPresentationLayerAssignment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPresentationLayerAssignment', 'IFC4X2', *args, **kwargs)

def IfcPresentationLayerWithStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPresentationLayerWithStyle', 'IFC4X2', *args, **kwargs)

def IfcPresentationStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPresentationStyle', 'IFC4X2', *args, **kwargs)

def IfcPresentationStyleAssignment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPresentationStyleAssignment', 'IFC4X2', *args, **kwargs)

def IfcProcedure(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProcedure', 'IFC4X2', *args, **kwargs)

def IfcProcedureType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProcedureType', 'IFC4X2', *args, **kwargs)

def IfcProcess(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProcess', 'IFC4X2', *args, **kwargs)

def IfcProduct(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProduct', 'IFC4X2', *args, **kwargs)

def IfcProductDefinitionShape(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProductDefinitionShape', 'IFC4X2', *args, **kwargs)

def IfcProductRepresentation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProductRepresentation', 'IFC4X2', *args, **kwargs)

def IfcProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProfileDef', 'IFC4X2', *args, **kwargs)

def IfcProfileProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProfileProperties', 'IFC4X2', *args, **kwargs)

def IfcProject(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProject', 'IFC4X2', *args, **kwargs)

def IfcProjectLibrary(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProjectLibrary', 'IFC4X2', *args, **kwargs)

def IfcProjectOrder(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProjectOrder', 'IFC4X2', *args, **kwargs)

def IfcProjectedCRS(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProjectedCRS', 'IFC4X2', *args, **kwargs)

def IfcProjectionElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProjectionElement', 'IFC4X2', *args, **kwargs)

def IfcProperty(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProperty', 'IFC4X2', *args, **kwargs)

def IfcPropertyAbstraction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyAbstraction', 'IFC4X2', *args, **kwargs)

def IfcPropertyBoundedValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyBoundedValue', 'IFC4X2', *args, **kwargs)

def IfcPropertyDefinition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyDefinition', 'IFC4X2', *args, **kwargs)

def IfcPropertyDependencyRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyDependencyRelationship', 'IFC4X2', *args, **kwargs)

def IfcPropertyEnumeratedValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyEnumeratedValue', 'IFC4X2', *args, **kwargs)

def IfcPropertyEnumeration(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyEnumeration', 'IFC4X2', *args, **kwargs)

def IfcPropertyListValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyListValue', 'IFC4X2', *args, **kwargs)

def IfcPropertyReferenceValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyReferenceValue', 'IFC4X2', *args, **kwargs)

def IfcPropertySet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertySet', 'IFC4X2', *args, **kwargs)

def IfcPropertySetDefinition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertySetDefinition', 'IFC4X2', *args, **kwargs)

def IfcPropertySetTemplate(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertySetTemplate', 'IFC4X2', *args, **kwargs)

def IfcPropertySingleValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertySingleValue', 'IFC4X2', *args, **kwargs)

def IfcPropertyTableValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyTableValue', 'IFC4X2', *args, **kwargs)

def IfcPropertyTemplate(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyTemplate', 'IFC4X2', *args, **kwargs)

def IfcPropertyTemplateDefinition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPropertyTemplateDefinition', 'IFC4X2', *args, **kwargs)

def IfcProtectiveDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProtectiveDevice', 'IFC4X2', *args, **kwargs)

def IfcProtectiveDeviceTrippingUnit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProtectiveDeviceTrippingUnit', 'IFC4X2', *args, **kwargs)

def IfcProtectiveDeviceTrippingUnitType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProtectiveDeviceTrippingUnitType', 'IFC4X2', *args, **kwargs)

def IfcProtectiveDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProtectiveDeviceType', 'IFC4X2', *args, **kwargs)

def IfcProxy(*args, **kwargs):
    return ifcopenshell.create_entity('IfcProxy', 'IFC4X2', *args, **kwargs)

def IfcPump(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPump', 'IFC4X2', *args, **kwargs)

def IfcPumpType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcPumpType', 'IFC4X2', *args, **kwargs)

def IfcQuantityArea(*args, **kwargs):
    return ifcopenshell.create_entity('IfcQuantityArea', 'IFC4X2', *args, **kwargs)

def IfcQuantityCount(*args, **kwargs):
    return ifcopenshell.create_entity('IfcQuantityCount', 'IFC4X2', *args, **kwargs)

def IfcQuantityLength(*args, **kwargs):
    return ifcopenshell.create_entity('IfcQuantityLength', 'IFC4X2', *args, **kwargs)

def IfcQuantitySet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcQuantitySet', 'IFC4X2', *args, **kwargs)

def IfcQuantityTime(*args, **kwargs):
    return ifcopenshell.create_entity('IfcQuantityTime', 'IFC4X2', *args, **kwargs)

def IfcQuantityVolume(*args, **kwargs):
    return ifcopenshell.create_entity('IfcQuantityVolume', 'IFC4X2', *args, **kwargs)

def IfcQuantityWeight(*args, **kwargs):
    return ifcopenshell.create_entity('IfcQuantityWeight', 'IFC4X2', *args, **kwargs)

def IfcRailing(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRailing', 'IFC4X2', *args, **kwargs)

def IfcRailingType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRailingType', 'IFC4X2', *args, **kwargs)

def IfcRamp(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRamp', 'IFC4X2', *args, **kwargs)

def IfcRampFlight(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRampFlight', 'IFC4X2', *args, **kwargs)

def IfcRampFlightType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRampFlightType', 'IFC4X2', *args, **kwargs)

def IfcRampType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRampType', 'IFC4X2', *args, **kwargs)

def IfcRationalBSplineCurveWithKnots(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRationalBSplineCurveWithKnots', 'IFC4X2', *args, **kwargs)

def IfcRationalBSplineSurfaceWithKnots(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRationalBSplineSurfaceWithKnots', 'IFC4X2', *args, **kwargs)

def IfcRectangleHollowProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRectangleHollowProfileDef', 'IFC4X2', *args, **kwargs)

def IfcRectangleProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRectangleProfileDef', 'IFC4X2', *args, **kwargs)

def IfcRectangularPyramid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRectangularPyramid', 'IFC4X2', *args, **kwargs)

def IfcRectangularTrimmedSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRectangularTrimmedSurface', 'IFC4X2', *args, **kwargs)

def IfcRecurrencePattern(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRecurrencePattern', 'IFC4X2', *args, **kwargs)

def IfcReference(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReference', 'IFC4X2', *args, **kwargs)

def IfcReferent(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReferent', 'IFC4X2', *args, **kwargs)

def IfcRegularTimeSeries(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRegularTimeSeries', 'IFC4X2', *args, **kwargs)

def IfcReinforcementBarProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReinforcementBarProperties', 'IFC4X2', *args, **kwargs)

def IfcReinforcementDefinitionProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReinforcementDefinitionProperties', 'IFC4X2', *args, **kwargs)

def IfcReinforcingBar(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReinforcingBar', 'IFC4X2', *args, **kwargs)

def IfcReinforcingBarType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReinforcingBarType', 'IFC4X2', *args, **kwargs)

def IfcReinforcingElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReinforcingElement', 'IFC4X2', *args, **kwargs)

def IfcReinforcingElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReinforcingElementType', 'IFC4X2', *args, **kwargs)

def IfcReinforcingMesh(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReinforcingMesh', 'IFC4X2', *args, **kwargs)

def IfcReinforcingMeshType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReinforcingMeshType', 'IFC4X2', *args, **kwargs)

def IfcRelAggregates(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAggregates', 'IFC4X2', *args, **kwargs)

def IfcRelAssigns(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssigns', 'IFC4X2', *args, **kwargs)

def IfcRelAssignsToActor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssignsToActor', 'IFC4X2', *args, **kwargs)

def IfcRelAssignsToControl(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssignsToControl', 'IFC4X2', *args, **kwargs)

def IfcRelAssignsToGroup(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssignsToGroup', 'IFC4X2', *args, **kwargs)

def IfcRelAssignsToGroupByFactor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssignsToGroupByFactor', 'IFC4X2', *args, **kwargs)

def IfcRelAssignsToProcess(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssignsToProcess', 'IFC4X2', *args, **kwargs)

def IfcRelAssignsToProduct(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssignsToProduct', 'IFC4X2', *args, **kwargs)

def IfcRelAssignsToResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssignsToResource', 'IFC4X2', *args, **kwargs)

def IfcRelAssociates(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssociates', 'IFC4X2', *args, **kwargs)

def IfcRelAssociatesApproval(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssociatesApproval', 'IFC4X2', *args, **kwargs)

def IfcRelAssociatesClassification(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssociatesClassification', 'IFC4X2', *args, **kwargs)

def IfcRelAssociatesConstraint(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssociatesConstraint', 'IFC4X2', *args, **kwargs)

def IfcRelAssociatesDocument(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssociatesDocument', 'IFC4X2', *args, **kwargs)

def IfcRelAssociatesLibrary(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssociatesLibrary', 'IFC4X2', *args, **kwargs)

def IfcRelAssociatesMaterial(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelAssociatesMaterial', 'IFC4X2', *args, **kwargs)

def IfcRelConnects(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnects', 'IFC4X2', *args, **kwargs)

def IfcRelConnectsElements(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsElements', 'IFC4X2', *args, **kwargs)

def IfcRelConnectsPathElements(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsPathElements', 'IFC4X2', *args, **kwargs)

def IfcRelConnectsPortToElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsPortToElement', 'IFC4X2', *args, **kwargs)

def IfcRelConnectsPorts(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsPorts', 'IFC4X2', *args, **kwargs)

def IfcRelConnectsStructuralActivity(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsStructuralActivity', 'IFC4X2', *args, **kwargs)

def IfcRelConnectsStructuralMember(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsStructuralMember', 'IFC4X2', *args, **kwargs)

def IfcRelConnectsWithEccentricity(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsWithEccentricity', 'IFC4X2', *args, **kwargs)

def IfcRelConnectsWithRealizingElements(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelConnectsWithRealizingElements', 'IFC4X2', *args, **kwargs)

def IfcRelContainedInSpatialStructure(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelContainedInSpatialStructure', 'IFC4X2', *args, **kwargs)

def IfcRelCoversBldgElements(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelCoversBldgElements', 'IFC4X2', *args, **kwargs)

def IfcRelCoversSpaces(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelCoversSpaces', 'IFC4X2', *args, **kwargs)

def IfcRelDeclares(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelDeclares', 'IFC4X2', *args, **kwargs)

def IfcRelDecomposes(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelDecomposes', 'IFC4X2', *args, **kwargs)

def IfcRelDefines(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelDefines', 'IFC4X2', *args, **kwargs)

def IfcRelDefinesByObject(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelDefinesByObject', 'IFC4X2', *args, **kwargs)

def IfcRelDefinesByProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelDefinesByProperties', 'IFC4X2', *args, **kwargs)

def IfcRelDefinesByTemplate(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelDefinesByTemplate', 'IFC4X2', *args, **kwargs)

def IfcRelDefinesByType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelDefinesByType', 'IFC4X2', *args, **kwargs)

def IfcRelFillsElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelFillsElement', 'IFC4X2', *args, **kwargs)

def IfcRelFlowControlElements(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelFlowControlElements', 'IFC4X2', *args, **kwargs)

def IfcRelInterferesElements(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelInterferesElements', 'IFC4X2', *args, **kwargs)

def IfcRelNests(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelNests', 'IFC4X2', *args, **kwargs)

def IfcRelPositions(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelPositions', 'IFC4X2', *args, **kwargs)

def IfcRelProjectsElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelProjectsElement', 'IFC4X2', *args, **kwargs)

def IfcRelReferencedInSpatialStructure(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelReferencedInSpatialStructure', 'IFC4X2', *args, **kwargs)

def IfcRelSequence(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelSequence', 'IFC4X2', *args, **kwargs)

def IfcRelServicesBuildings(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelServicesBuildings', 'IFC4X2', *args, **kwargs)

def IfcRelSpaceBoundary(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelSpaceBoundary', 'IFC4X2', *args, **kwargs)

def IfcRelSpaceBoundary1stLevel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelSpaceBoundary1stLevel', 'IFC4X2', *args, **kwargs)

def IfcRelSpaceBoundary2ndLevel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelSpaceBoundary2ndLevel', 'IFC4X2', *args, **kwargs)

def IfcRelVoidsElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelVoidsElement', 'IFC4X2', *args, **kwargs)

def IfcRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRelationship', 'IFC4X2', *args, **kwargs)

def IfcReparametrisedCompositeCurveSegment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcReparametrisedCompositeCurveSegment', 'IFC4X2', *args, **kwargs)

def IfcRepresentation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRepresentation', 'IFC4X2', *args, **kwargs)

def IfcRepresentationContext(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRepresentationContext', 'IFC4X2', *args, **kwargs)

def IfcRepresentationItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRepresentationItem', 'IFC4X2', *args, **kwargs)

def IfcRepresentationMap(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRepresentationMap', 'IFC4X2', *args, **kwargs)

def IfcResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcResource', 'IFC4X2', *args, **kwargs)

def IfcResourceApprovalRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcResourceApprovalRelationship', 'IFC4X2', *args, **kwargs)

def IfcResourceConstraintRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcResourceConstraintRelationship', 'IFC4X2', *args, **kwargs)

def IfcResourceLevelRelationship(*args, **kwargs):
    return ifcopenshell.create_entity('IfcResourceLevelRelationship', 'IFC4X2', *args, **kwargs)

def IfcResourceTime(*args, **kwargs):
    return ifcopenshell.create_entity('IfcResourceTime', 'IFC4X2', *args, **kwargs)

def IfcRevolvedAreaSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRevolvedAreaSolid', 'IFC4X2', *args, **kwargs)

def IfcRevolvedAreaSolidTapered(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRevolvedAreaSolidTapered', 'IFC4X2', *args, **kwargs)

def IfcRightCircularCone(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRightCircularCone', 'IFC4X2', *args, **kwargs)

def IfcRightCircularCylinder(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRightCircularCylinder', 'IFC4X2', *args, **kwargs)

def IfcRoof(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRoof', 'IFC4X2', *args, **kwargs)

def IfcRoofType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRoofType', 'IFC4X2', *args, **kwargs)

def IfcRoot(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRoot', 'IFC4X2', *args, **kwargs)

def IfcRoundedRectangleProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcRoundedRectangleProfileDef', 'IFC4X2', *args, **kwargs)

def IfcSIUnit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSIUnit', 'IFC4X2', *args, **kwargs)

def IfcSanitaryTerminal(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSanitaryTerminal', 'IFC4X2', *args, **kwargs)

def IfcSanitaryTerminalType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSanitaryTerminalType', 'IFC4X2', *args, **kwargs)

def IfcSchedulingTime(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSchedulingTime', 'IFC4X2', *args, **kwargs)

def IfcSeamCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSeamCurve', 'IFC4X2', *args, **kwargs)

def IfcSectionProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSectionProperties', 'IFC4X2', *args, **kwargs)

def IfcSectionReinforcementProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSectionReinforcementProperties', 'IFC4X2', *args, **kwargs)

def IfcSectionedSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSectionedSolid', 'IFC4X2', *args, **kwargs)

def IfcSectionedSolidHorizontal(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSectionedSolidHorizontal', 'IFC4X2', *args, **kwargs)

def IfcSectionedSpine(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSectionedSpine', 'IFC4X2', *args, **kwargs)

def IfcSensor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSensor', 'IFC4X2', *args, **kwargs)

def IfcSensorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSensorType', 'IFC4X2', *args, **kwargs)

def IfcShadingDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcShadingDevice', 'IFC4X2', *args, **kwargs)

def IfcShadingDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcShadingDeviceType', 'IFC4X2', *args, **kwargs)

def IfcShapeAspect(*args, **kwargs):
    return ifcopenshell.create_entity('IfcShapeAspect', 'IFC4X2', *args, **kwargs)

def IfcShapeModel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcShapeModel', 'IFC4X2', *args, **kwargs)

def IfcShapeRepresentation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcShapeRepresentation', 'IFC4X2', *args, **kwargs)

def IfcShellBasedSurfaceModel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcShellBasedSurfaceModel', 'IFC4X2', *args, **kwargs)

def IfcSimpleProperty(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSimpleProperty', 'IFC4X2', *args, **kwargs)

def IfcSimplePropertyTemplate(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSimplePropertyTemplate', 'IFC4X2', *args, **kwargs)

def IfcSite(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSite', 'IFC4X2', *args, **kwargs)

def IfcSlab(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSlab', 'IFC4X2', *args, **kwargs)

def IfcSlabElementedCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSlabElementedCase', 'IFC4X2', *args, **kwargs)

def IfcSlabStandardCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSlabStandardCase', 'IFC4X2', *args, **kwargs)

def IfcSlabType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSlabType', 'IFC4X2', *args, **kwargs)

def IfcSlippageConnectionCondition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSlippageConnectionCondition', 'IFC4X2', *args, **kwargs)

def IfcSolarDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSolarDevice', 'IFC4X2', *args, **kwargs)

def IfcSolarDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSolarDeviceType', 'IFC4X2', *args, **kwargs)

def IfcSolidModel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSolidModel', 'IFC4X2', *args, **kwargs)

def IfcSpace(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpace', 'IFC4X2', *args, **kwargs)

def IfcSpaceHeater(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpaceHeater', 'IFC4X2', *args, **kwargs)

def IfcSpaceHeaterType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpaceHeaterType', 'IFC4X2', *args, **kwargs)

def IfcSpaceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpaceType', 'IFC4X2', *args, **kwargs)

def IfcSpatialElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpatialElement', 'IFC4X2', *args, **kwargs)

def IfcSpatialElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpatialElementType', 'IFC4X2', *args, **kwargs)

def IfcSpatialStructureElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpatialStructureElement', 'IFC4X2', *args, **kwargs)

def IfcSpatialStructureElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpatialStructureElementType', 'IFC4X2', *args, **kwargs)

def IfcSpatialZone(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpatialZone', 'IFC4X2', *args, **kwargs)

def IfcSpatialZoneType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSpatialZoneType', 'IFC4X2', *args, **kwargs)

def IfcSphere(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSphere', 'IFC4X2', *args, **kwargs)

def IfcSphericalSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSphericalSurface', 'IFC4X2', *args, **kwargs)

def IfcStackTerminal(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStackTerminal', 'IFC4X2', *args, **kwargs)

def IfcStackTerminalType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStackTerminalType', 'IFC4X2', *args, **kwargs)

def IfcStair(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStair', 'IFC4X2', *args, **kwargs)

def IfcStairFlight(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStairFlight', 'IFC4X2', *args, **kwargs)

def IfcStairFlightType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStairFlightType', 'IFC4X2', *args, **kwargs)

def IfcStairType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStairType', 'IFC4X2', *args, **kwargs)

def IfcStructuralAction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralAction', 'IFC4X2', *args, **kwargs)

def IfcStructuralActivity(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralActivity', 'IFC4X2', *args, **kwargs)

def IfcStructuralAnalysisModel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralAnalysisModel', 'IFC4X2', *args, **kwargs)

def IfcStructuralConnection(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralConnection', 'IFC4X2', *args, **kwargs)

def IfcStructuralConnectionCondition(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralConnectionCondition', 'IFC4X2', *args, **kwargs)

def IfcStructuralCurveAction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralCurveAction', 'IFC4X2', *args, **kwargs)

def IfcStructuralCurveConnection(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralCurveConnection', 'IFC4X2', *args, **kwargs)

def IfcStructuralCurveMember(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralCurveMember', 'IFC4X2', *args, **kwargs)

def IfcStructuralCurveMemberVarying(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralCurveMemberVarying', 'IFC4X2', *args, **kwargs)

def IfcStructuralCurveReaction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralCurveReaction', 'IFC4X2', *args, **kwargs)

def IfcStructuralItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralItem', 'IFC4X2', *args, **kwargs)

def IfcStructuralLinearAction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLinearAction', 'IFC4X2', *args, **kwargs)

def IfcStructuralLoad(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoad', 'IFC4X2', *args, **kwargs)

def IfcStructuralLoadCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadCase', 'IFC4X2', *args, **kwargs)

def IfcStructuralLoadConfiguration(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadConfiguration', 'IFC4X2', *args, **kwargs)

def IfcStructuralLoadGroup(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadGroup', 'IFC4X2', *args, **kwargs)

def IfcStructuralLoadLinearForce(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadLinearForce', 'IFC4X2', *args, **kwargs)

def IfcStructuralLoadOrResult(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadOrResult', 'IFC4X2', *args, **kwargs)

def IfcStructuralLoadPlanarForce(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadPlanarForce', 'IFC4X2', *args, **kwargs)

def IfcStructuralLoadSingleDisplacement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadSingleDisplacement', 'IFC4X2', *args, **kwargs)

def IfcStructuralLoadSingleDisplacementDistortion(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadSingleDisplacementDistortion', 'IFC4X2', *args, **kwargs)

def IfcStructuralLoadSingleForce(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadSingleForce', 'IFC4X2', *args, **kwargs)

def IfcStructuralLoadSingleForceWarping(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadSingleForceWarping', 'IFC4X2', *args, **kwargs)

def IfcStructuralLoadStatic(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadStatic', 'IFC4X2', *args, **kwargs)

def IfcStructuralLoadTemperature(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralLoadTemperature', 'IFC4X2', *args, **kwargs)

def IfcStructuralMember(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralMember', 'IFC4X2', *args, **kwargs)

def IfcStructuralPlanarAction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralPlanarAction', 'IFC4X2', *args, **kwargs)

def IfcStructuralPointAction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralPointAction', 'IFC4X2', *args, **kwargs)

def IfcStructuralPointConnection(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralPointConnection', 'IFC4X2', *args, **kwargs)

def IfcStructuralPointReaction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralPointReaction', 'IFC4X2', *args, **kwargs)

def IfcStructuralReaction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralReaction', 'IFC4X2', *args, **kwargs)

def IfcStructuralResultGroup(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralResultGroup', 'IFC4X2', *args, **kwargs)

def IfcStructuralSurfaceAction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralSurfaceAction', 'IFC4X2', *args, **kwargs)

def IfcStructuralSurfaceConnection(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralSurfaceConnection', 'IFC4X2', *args, **kwargs)

def IfcStructuralSurfaceMember(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralSurfaceMember', 'IFC4X2', *args, **kwargs)

def IfcStructuralSurfaceMemberVarying(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralSurfaceMemberVarying', 'IFC4X2', *args, **kwargs)

def IfcStructuralSurfaceReaction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStructuralSurfaceReaction', 'IFC4X2', *args, **kwargs)

def IfcStyleModel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStyleModel', 'IFC4X2', *args, **kwargs)

def IfcStyledItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStyledItem', 'IFC4X2', *args, **kwargs)

def IfcStyledRepresentation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcStyledRepresentation', 'IFC4X2', *args, **kwargs)

def IfcSubContractResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSubContractResource', 'IFC4X2', *args, **kwargs)

def IfcSubContractResourceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSubContractResourceType', 'IFC4X2', *args, **kwargs)

def IfcSubedge(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSubedge', 'IFC4X2', *args, **kwargs)

def IfcSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurface', 'IFC4X2', *args, **kwargs)

def IfcSurfaceCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceCurve', 'IFC4X2', *args, **kwargs)

def IfcSurfaceCurveSweptAreaSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceCurveSweptAreaSolid', 'IFC4X2', *args, **kwargs)

def IfcSurfaceFeature(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceFeature', 'IFC4X2', *args, **kwargs)

def IfcSurfaceOfLinearExtrusion(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceOfLinearExtrusion', 'IFC4X2', *args, **kwargs)

def IfcSurfaceOfRevolution(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceOfRevolution', 'IFC4X2', *args, **kwargs)

def IfcSurfaceReinforcementArea(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceReinforcementArea', 'IFC4X2', *args, **kwargs)

def IfcSurfaceStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceStyle', 'IFC4X2', *args, **kwargs)

def IfcSurfaceStyleLighting(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceStyleLighting', 'IFC4X2', *args, **kwargs)

def IfcSurfaceStyleRefraction(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceStyleRefraction', 'IFC4X2', *args, **kwargs)

def IfcSurfaceStyleRendering(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceStyleRendering', 'IFC4X2', *args, **kwargs)

def IfcSurfaceStyleShading(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceStyleShading', 'IFC4X2', *args, **kwargs)

def IfcSurfaceStyleWithTextures(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceStyleWithTextures', 'IFC4X2', *args, **kwargs)

def IfcSurfaceTexture(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSurfaceTexture', 'IFC4X2', *args, **kwargs)

def IfcSweptAreaSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSweptAreaSolid', 'IFC4X2', *args, **kwargs)

def IfcSweptDiskSolid(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSweptDiskSolid', 'IFC4X2', *args, **kwargs)

def IfcSweptDiskSolidPolygonal(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSweptDiskSolidPolygonal', 'IFC4X2', *args, **kwargs)

def IfcSweptSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSweptSurface', 'IFC4X2', *args, **kwargs)

def IfcSwitchingDevice(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSwitchingDevice', 'IFC4X2', *args, **kwargs)

def IfcSwitchingDeviceType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSwitchingDeviceType', 'IFC4X2', *args, **kwargs)

def IfcSystem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSystem', 'IFC4X2', *args, **kwargs)

def IfcSystemFurnitureElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSystemFurnitureElement', 'IFC4X2', *args, **kwargs)

def IfcSystemFurnitureElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcSystemFurnitureElementType', 'IFC4X2', *args, **kwargs)

def IfcTShapeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTShapeProfileDef', 'IFC4X2', *args, **kwargs)

def IfcTable(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTable', 'IFC4X2', *args, **kwargs)

def IfcTableColumn(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTableColumn', 'IFC4X2', *args, **kwargs)

def IfcTableRow(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTableRow', 'IFC4X2', *args, **kwargs)

def IfcTank(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTank', 'IFC4X2', *args, **kwargs)

def IfcTankType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTankType', 'IFC4X2', *args, **kwargs)

def IfcTask(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTask', 'IFC4X2', *args, **kwargs)

def IfcTaskTime(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTaskTime', 'IFC4X2', *args, **kwargs)

def IfcTaskTimeRecurring(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTaskTimeRecurring', 'IFC4X2', *args, **kwargs)

def IfcTaskType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTaskType', 'IFC4X2', *args, **kwargs)

def IfcTelecomAddress(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTelecomAddress', 'IFC4X2', *args, **kwargs)

def IfcTendon(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTendon', 'IFC4X2', *args, **kwargs)

def IfcTendonAnchor(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTendonAnchor', 'IFC4X2', *args, **kwargs)

def IfcTendonAnchorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTendonAnchorType', 'IFC4X2', *args, **kwargs)

def IfcTendonConduit(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTendonConduit', 'IFC4X2', *args, **kwargs)

def IfcTendonConduitType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTendonConduitType', 'IFC4X2', *args, **kwargs)

def IfcTendonType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTendonType', 'IFC4X2', *args, **kwargs)

def IfcTessellatedFaceSet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTessellatedFaceSet', 'IFC4X2', *args, **kwargs)

def IfcTessellatedItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTessellatedItem', 'IFC4X2', *args, **kwargs)

def IfcTextLiteral(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextLiteral', 'IFC4X2', *args, **kwargs)

def IfcTextLiteralWithExtent(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextLiteralWithExtent', 'IFC4X2', *args, **kwargs)

def IfcTextStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextStyle', 'IFC4X2', *args, **kwargs)

def IfcTextStyleFontModel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextStyleFontModel', 'IFC4X2', *args, **kwargs)

def IfcTextStyleForDefinedFont(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextStyleForDefinedFont', 'IFC4X2', *args, **kwargs)

def IfcTextStyleTextModel(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextStyleTextModel', 'IFC4X2', *args, **kwargs)

def IfcTextureCoordinate(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextureCoordinate', 'IFC4X2', *args, **kwargs)

def IfcTextureCoordinateGenerator(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextureCoordinateGenerator', 'IFC4X2', *args, **kwargs)

def IfcTextureMap(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextureMap', 'IFC4X2', *args, **kwargs)

def IfcTextureVertex(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextureVertex', 'IFC4X2', *args, **kwargs)

def IfcTextureVertexList(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTextureVertexList', 'IFC4X2', *args, **kwargs)

def IfcTimePeriod(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTimePeriod', 'IFC4X2', *args, **kwargs)

def IfcTimeSeries(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTimeSeries', 'IFC4X2', *args, **kwargs)

def IfcTimeSeriesValue(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTimeSeriesValue', 'IFC4X2', *args, **kwargs)

def IfcTopologicalRepresentationItem(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTopologicalRepresentationItem', 'IFC4X2', *args, **kwargs)

def IfcTopologyRepresentation(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTopologyRepresentation', 'IFC4X2', *args, **kwargs)

def IfcToroidalSurface(*args, **kwargs):
    return ifcopenshell.create_entity('IfcToroidalSurface', 'IFC4X2', *args, **kwargs)

def IfcTransformer(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTransformer', 'IFC4X2', *args, **kwargs)

def IfcTransformerType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTransformerType', 'IFC4X2', *args, **kwargs)

def IfcTransitionCurveSegment2D(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTransitionCurveSegment2D', 'IFC4X2', *args, **kwargs)

def IfcTransportElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTransportElement', 'IFC4X2', *args, **kwargs)

def IfcTransportElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTransportElementType', 'IFC4X2', *args, **kwargs)

def IfcTrapeziumProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTrapeziumProfileDef', 'IFC4X2', *args, **kwargs)

def IfcTriangulatedFaceSet(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTriangulatedFaceSet', 'IFC4X2', *args, **kwargs)

def IfcTriangulatedIrregularNetwork(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTriangulatedIrregularNetwork', 'IFC4X2', *args, **kwargs)

def IfcTrimmedCurve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTrimmedCurve', 'IFC4X2', *args, **kwargs)

def IfcTubeBundle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTubeBundle', 'IFC4X2', *args, **kwargs)

def IfcTubeBundleType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTubeBundleType', 'IFC4X2', *args, **kwargs)

def IfcTypeObject(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTypeObject', 'IFC4X2', *args, **kwargs)

def IfcTypeProcess(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTypeProcess', 'IFC4X2', *args, **kwargs)

def IfcTypeProduct(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTypeProduct', 'IFC4X2', *args, **kwargs)

def IfcTypeResource(*args, **kwargs):
    return ifcopenshell.create_entity('IfcTypeResource', 'IFC4X2', *args, **kwargs)

def IfcUShapeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcUShapeProfileDef', 'IFC4X2', *args, **kwargs)

def IfcUnitAssignment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcUnitAssignment', 'IFC4X2', *args, **kwargs)

def IfcUnitaryControlElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcUnitaryControlElement', 'IFC4X2', *args, **kwargs)

def IfcUnitaryControlElementType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcUnitaryControlElementType', 'IFC4X2', *args, **kwargs)

def IfcUnitaryEquipment(*args, **kwargs):
    return ifcopenshell.create_entity('IfcUnitaryEquipment', 'IFC4X2', *args, **kwargs)

def IfcUnitaryEquipmentType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcUnitaryEquipmentType', 'IFC4X2', *args, **kwargs)

def IfcValve(*args, **kwargs):
    return ifcopenshell.create_entity('IfcValve', 'IFC4X2', *args, **kwargs)

def IfcValveType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcValveType', 'IFC4X2', *args, **kwargs)

def IfcVector(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVector', 'IFC4X2', *args, **kwargs)

def IfcVertex(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVertex', 'IFC4X2', *args, **kwargs)

def IfcVertexLoop(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVertexLoop', 'IFC4X2', *args, **kwargs)

def IfcVertexPoint(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVertexPoint', 'IFC4X2', *args, **kwargs)

def IfcVibrationDamper(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVibrationDamper', 'IFC4X2', *args, **kwargs)

def IfcVibrationDamperType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVibrationDamperType', 'IFC4X2', *args, **kwargs)

def IfcVibrationIsolator(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVibrationIsolator', 'IFC4X2', *args, **kwargs)

def IfcVibrationIsolatorType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVibrationIsolatorType', 'IFC4X2', *args, **kwargs)

def IfcVirtualElement(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVirtualElement', 'IFC4X2', *args, **kwargs)

def IfcVirtualGridIntersection(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVirtualGridIntersection', 'IFC4X2', *args, **kwargs)

def IfcVoidingFeature(*args, **kwargs):
    return ifcopenshell.create_entity('IfcVoidingFeature', 'IFC4X2', *args, **kwargs)

def IfcWall(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWall', 'IFC4X2', *args, **kwargs)

def IfcWallElementedCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWallElementedCase', 'IFC4X2', *args, **kwargs)

def IfcWallStandardCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWallStandardCase', 'IFC4X2', *args, **kwargs)

def IfcWallType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWallType', 'IFC4X2', *args, **kwargs)

def IfcWasteTerminal(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWasteTerminal', 'IFC4X2', *args, **kwargs)

def IfcWasteTerminalType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWasteTerminalType', 'IFC4X2', *args, **kwargs)

def IfcWindow(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWindow', 'IFC4X2', *args, **kwargs)

def IfcWindowLiningProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWindowLiningProperties', 'IFC4X2', *args, **kwargs)

def IfcWindowPanelProperties(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWindowPanelProperties', 'IFC4X2', *args, **kwargs)

def IfcWindowStandardCase(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWindowStandardCase', 'IFC4X2', *args, **kwargs)

def IfcWindowStyle(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWindowStyle', 'IFC4X2', *args, **kwargs)

def IfcWindowType(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWindowType', 'IFC4X2', *args, **kwargs)

def IfcWorkCalendar(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWorkCalendar', 'IFC4X2', *args, **kwargs)

def IfcWorkControl(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWorkControl', 'IFC4X2', *args, **kwargs)

def IfcWorkPlan(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWorkPlan', 'IFC4X2', *args, **kwargs)

def IfcWorkSchedule(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWorkSchedule', 'IFC4X2', *args, **kwargs)

def IfcWorkTime(*args, **kwargs):
    return ifcopenshell.create_entity('IfcWorkTime', 'IFC4X2', *args, **kwargs)

def IfcZShapeProfileDef(*args, **kwargs):
    return ifcopenshell.create_entity('IfcZShapeProfileDef', 'IFC4X2', *args, **kwargs)

def IfcZone(*args, **kwargs):
    return ifcopenshell.create_entity('IfcZone', 'IFC4X2', *args, **kwargs)

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcactuatortype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof([afs for afs in express_getattr(express_getattr(self, 'Outer', INDETERMINATE), 'CfsFaces', INDETERMINATE) if not 'ifc4x2.ifcadvancedface' in typeof(afs)]) == 0) is not False

class IfcAdvancedBrepWithVoids_VoidsHaveAdvancedFaces:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAdvancedBrepWithVoids'
    RULE_NAME = 'VoidsHaveAdvancedFaces'

    @staticmethod
    def __call__(self):
        voids = express_getattr(self, 'Voids', INDETERMINATE)
        assert (sizeof([vsh for vsh in voids if sizeof([afs for afs in express_getattr(vsh, 'CfsFaces', INDETERMINATE) if not 'ifc4x2.ifcadvancedface' in typeof(afs)]) == 0]) == 0) is not False

class IfcAdvancedFace_ApplicableSurface:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAdvancedFace'
    RULE_NAME = 'ApplicableSurface'

    @staticmethod
    def __call__(self):
        assert (sizeof(['ifc4x2.ifcelementarysurface', 'ifc4x2.ifcsweptsurface', 'ifc4x2.ifcbsplinesurface'] * typeof(express_getattr(self, 'FaceSurface', INDETERMINATE))) == 1) is not False

class IfcAdvancedFace_RequiresEdgeCurve:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAdvancedFace'
    RULE_NAME = 'RequiresEdgeCurve'

    @staticmethod
    def __call__(self):
        assert (sizeof([elpfbnds for elpfbnds in [bnds for bnds in express_getattr(self, 'Bounds', INDETERMINATE) if 'ifc4x2.ifcedgeloop' in typeof(express_getattr(bnds, 'Bound', INDETERMINATE))] if not sizeof([oe for oe in express_getattr(express_getattr(elpfbnds, 'Bound', INDETERMINATE), 'EdgeList', INDETERMINATE) if not 'ifc4x2.ifcedgecurve' in typeof(express_getattr(oe, 'EdgeElement', INDETERMINATE))]) == 0]) == 0) is not False

class IfcAdvancedFace_ApplicableEdgeCurves:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAdvancedFace'
    RULE_NAME = 'ApplicableEdgeCurves'

    @staticmethod
    def __call__(self):
        assert (sizeof([elpfbnds for elpfbnds in [bnds for bnds in express_getattr(self, 'Bounds', INDETERMINATE) if 'ifc4x2.ifcedgeloop' in typeof(express_getattr(bnds, 'Bound', INDETERMINATE))] if not sizeof([oe for oe in express_getattr(express_getattr(elpfbnds, 'Bound', INDETERMINATE), 'EdgeList', INDETERMINATE) if not sizeof(['ifc4x2.ifcline', 'ifc4x2.ifcconic', 'ifc4x2.ifcpolyline', 'ifc4x2.ifcbsplinecurve'] * typeof(express_getattr(express_getattr(oe, 'EdgeElement', INDETERMINATE), 'EdgeGeometry', INDETERMINATE))) == 1]) == 0]) == 0) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcairterminaltype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcairterminalboxtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcairtoairheatrecoverytype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcalarmtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (not 'ifc4x2.ifcline' in typeof(outercurve)) is not False

class IfcArbitraryClosedProfileDef_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcArbitraryClosedProfileDef'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        outercurve = express_getattr(self, 'OuterCurve', INDETERMINATE)
        assert (not 'ifc4x2.ifcoffsetcurve2d' in typeof(outercurve)) is not False

class IfcArbitraryOpenProfileDef_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcArbitraryOpenProfileDef'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        assert ('ifc4x2.ifccenterlineprofiledef' in typeof(self) or express_getattr(self, 'ProfileType', INDETERMINATE) == express_getattr(IfcProfileTypeEnum, 'CURVE', INDETERMINATE)) is not False

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
        assert (sizeof([temp for temp in innercurves if 'ifc4x2.ifcline' in typeof(temp)]) == 0) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcaudiovisualappliancetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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

def calc_IfcAxis2Placement3D_P(self):
    axis = express_getattr(self, 'Axis', INDETERMINATE)
    refdirection = express_getattr(self, 'RefDirection', INDETERMINATE)
    return IfcBuildAxes(axis, refdirection)

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcbeamtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcBeamStandardCase_HasMaterialProfileSetUsage:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBeamStandardCase'
    RULE_NAME = 'HasMaterialProfileSetUsage'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in usedin(self, 'ifc4x2.ifcrelassociates.relatedobjects') if 'ifc4x2.ifcrelassociatesmaterial' in typeof(temp) and 'ifc4x2.ifcmaterialprofilesetusage' in typeof(express_getattr(temp, 'RelatingMaterial', INDETERMINATE))]) == 1) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcbearingtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcboilertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert ('ifc4x2.ifcsweptareasolid' in typeof(firstoperand) or 'ifc4x2.ifcsweptdiscsolid' in typeof(firstoperand) or 'ifc4x2.ifcbooleanclippingresult' in typeof(firstoperand)) is not False

class IfcBooleanClippingResult_SecondOperandType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBooleanClippingResult'
    RULE_NAME = 'SecondOperandType'

    @staticmethod
    def __call__(self):
        secondoperand = express_getattr(self, 'SecondOperand', INDETERMINATE)
        assert ('ifc4x2.ifchalfspacesolid' in typeof(secondoperand)) is not False

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
        assert (not 'ifc4x2.ifctessellatedfaceset' in typeof(firstoperand) or (exists(express_getattr(firstoperand, 'Closed', INDETERMINATE)) and express_getattr(firstoperand, 'Closed', INDETERMINATE))) is not False

class IfcBooleanResult_SecondOperandClosed:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBooleanResult'
    RULE_NAME = 'SecondOperandClosed'

    @staticmethod
    def __call__(self):
        secondoperand = express_getattr(self, 'SecondOperand', INDETERMINATE)
        assert (not 'ifc4x2.ifctessellatedfaceset' in typeof(secondoperand) or (exists(express_getattr(secondoperand, 'Closed', INDETERMINATE)) and express_getattr(secondoperand, 'Closed', INDETERMINATE))) is not False

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
        assert (not 'ifc4x2.ifccurveboundedplane' in typeof(express_getattr(self, 'BaseSurface', INDETERMINATE))) is not False

class IfcBuildingElement_MaxOneMaterialAssociation:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBuildingElement'
    RULE_NAME = 'MaxOneMaterialAssociation'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in express_getattr(self, 'HasAssociations', INDETERMINATE) if 'ifc4x2.ifcrelassociatesmaterial' in typeof(temp)]) <= 1) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcbuildingelementparttype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcbuildingelementproxytype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcBuildingElementProxyType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBuildingElementProxyType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcBuildingElementProxyTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcBuildingElementProxyTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcburnertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifccablecarrierfittingtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifccablecarriersegmenttype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifccablefittingtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifccablesegmenttype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifccaissonfoundationtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcchillertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcchimneytype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifccoiltype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifccolumntype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcColumnStandardCase_HasMaterialProfileSetUsage:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcColumnStandardCase'
    RULE_NAME = 'HasMaterialProfileSetUsage'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in usedin(self, 'ifc4x2.ifcrelassociates.relatedobjects') if 'ifc4x2.ifcrelassociatesmaterial' in typeof(temp) and 'ifc4x2.ifcmaterialprofilesetusage' in typeof(express_getattr(temp, 'RelatingMaterial', INDETERMINATE))]) == 1) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifccommunicationsappliancetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert ('ifc4x2.ifcboundedcurve' in typeof(parentcurve)) is not False

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
        assert (sizeof([temp for temp in profiles if 'ifc4x2.ifccompositeprofiledef' in typeof(temp)]) == 0) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifccompressortype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifccondensertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifccontrollertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcControllerType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcControllerType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcControllerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcControllerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifccooledbeamtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifccoolingtowertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcCoolingTowerType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCoolingTowerType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcCoolingTowerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCoolingTowerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifccoveringtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifccurtainwalltype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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

class IfcCurveStyle_MeasureOfWidth:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCurveStyle'
    RULE_NAME = 'MeasureOfWidth'

    @staticmethod
    def __call__(self):
        curvewidth = express_getattr(self, 'CurveWidth', INDETERMINATE)
        assert (not exists(curvewidth) or 'ifc4x2.ifcpositivelengthmeasure' in typeof(curvewidth) or ('ifc4x2.ifcdescriptivemeasure' in typeof(curvewidth) and curvewidth == 'bylayer')) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcdampertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcdeepfoundationtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcdiscreteaccessorytype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcDiscreteAccessoryType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDiscreteAccessoryType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcDiscreteAccessoryTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcDiscreteAccessoryTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcdistributionchamberelementtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcDistributionChamberElementType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDistributionChamberElementType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcDistributionChamberElementTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcDistributionChamberElementTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcdoortype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (exists(lambda : express_getitem(express_getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and ('ifc4x2.ifcdoortype' in typeof(express_getitem(express_getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) or 'ifc4x2.ifcdoorstyle' in typeof(express_getitem(express_getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)))) is not False

class IfcDoorPanelProperties_ApplicableToType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDoorPanelProperties'
    RULE_NAME = 'ApplicableToType'

    @staticmethod
    def __call__(self):
        assert (exists(lambda : express_getitem(express_getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and ('ifc4x2.ifcdoortype' in typeof(express_getitem(express_getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) or 'ifc4x2.ifcdoorstyle' in typeof(express_getitem(express_getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcductfittingtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcductsegmenttype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcductsilencertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcDuctSilencerType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDuctSilencerType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcDuctSilencerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcDuctSilencerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcelectricappliancetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcelectricdistributionboardtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcelectricflowstoragedevicetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcElectricFlowStorageDeviceType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricFlowStorageDeviceType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcElectricFlowStorageDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcElectricFlowStorageDeviceTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcelectricgeneratortype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcelectricmotortype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcelectrictimecontroltype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcelementassemblytype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcenginetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcevaporativecoolertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcevaporatortype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof([temp for temp in bounds if 'ifc4x2.ifcfaceouterbound' in typeof(temp)]) <= 1) is not False

def calc_IfcFaceBasedSurfaceModel_Dim(self):
    return 3

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcfantype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcfastenertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcFastenerType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFastenerType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcFastenerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcFastenerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

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
        assert (sizeof([style for style in express_getattr(self, 'FillStyles', INDETERMINATE) if 'ifc4x2.ifccolour' in typeof(style)]) <= 1) is not False

class IfcFillAreaStyle_MaxOneExtHatchStyle:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFillAreaStyle'
    RULE_NAME = 'MaxOneExtHatchStyle'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in express_getattr(self, 'FillStyles', INDETERMINATE) if 'ifc4x2.ifcexternallydefinedhatchstyle' in typeof(style)]) <= 1) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcfiltertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcfiresuppressionterminaltype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcFireSuppressionTerminalType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFireSuppressionTerminalType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcFireSuppressionTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcFireSuppressionTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcFixedReferenceSweptAreaSolid_DirectrixBounded:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFixedReferenceSweptAreaSolid'
    RULE_NAME = 'DirectrixBounded'

    @staticmethod
    def __call__(self):
        directrix = express_getattr(self, 'Directrix', INDETERMINATE)
        startparam = express_getattr(self, 'StartParam', INDETERMINATE)
        endparam = express_getattr(self, 'EndParam', INDETERMINATE)
        assert (exists(startparam) and exists(endparam) or sizeof(['ifc4x2.ifcconic', 'ifc4x2.ifcboundedcurve'] * typeof(directrix)) == 1) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcflowinstrumenttype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcflowmetertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcfootingtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcfurnituretype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcgeographicelementtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof([temp for temp in express_getattr(self, 'Elements', INDETERMINATE) if 'ifc4x2.ifcsurface' in typeof(temp)]) == 0) is not False

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
        assert (not 'ifc4x2.ifcgeometricrepresentationsubcontext' in typeof(parentcontext)) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcheatexchangertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifchumidifiertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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

class IfcIndexedPolyCurve_Consecutive:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcIndexedPolyCurve'
    RULE_NAME = 'Consecutive'

    @staticmethod
    def __call__(self):
        segments = express_getattr(self, 'Segments', INDETERMINATE)
        assert (sizeof(segments) == 0 or IfcConsecutiveSegments(segments)) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcinterceptortype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcjunctionboxtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifclamptype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifclightfixturetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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

class IfcLocalPlacement_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLocalPlacement'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        placementrelto = express_getattr(self, 'PlacementRelTo', INDETERMINATE)
        relativeplacement = express_getattr(self, 'RelativePlacement', INDETERMINATE)
        assert IfcCorrectLocalPlacement(relativeplacement, placementrelto) is not False

class IfcMaterialDefinitionRepresentation_OnlyStyledRepresentations:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMaterialDefinitionRepresentation'
    RULE_NAME = 'OnlyStyledRepresentations'

    @staticmethod
    def __call__(self):
        representations = express_getattr(self, 'Representations', INDETERMINATE)
        assert (sizeof([temp for temp in representations if not 'ifc4x2.ifcstyledrepresentation' in typeof(temp)]) == 0) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcmechanicalfastenertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcmedicaldevicetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcmembertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcMemberStandardCase_HasMaterialProfileSetUsage:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMemberStandardCase'
    RULE_NAME = 'HasMaterialProfileSetUsage'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in usedin(self, 'ifc4x2.ifcrelassociates.relatedobjects') if 'ifc4x2.ifcrelassociatesmaterial' in typeof(temp) and 'ifc4x2.ifcmaterialprofilesetusage' in typeof(express_getattr(temp, 'RelatingMaterial', INDETERMINATE))]) == 1) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcmotorconnectiontype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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

class IfcOrientedEdge_EdgeElementNotOriented:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcOrientedEdge'
    RULE_NAME = 'EdgeElementNotOriented'

    @staticmethod
    def __call__(self):
        edgeelement = express_getattr(self, 'EdgeElement', INDETERMINATE)
        assert (not 'ifc4x2.ifcorientededge' in typeof(edgeelement)) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcoutlettype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcpiletype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcpipefittingtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcpipesegmenttype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcplatetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcPlateStandardCase_HasMaterialLayerSetUsage:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPlateStandardCase'
    RULE_NAME = 'HasMaterialLayerSetUsage'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in usedin(self, 'ifc4x2.ifcrelassociates.relatedobjects') if 'ifc4x2.ifcrelassociatesmaterial' in typeof(temp) and 'ifc4x2.ifcmateriallayersetusage' in typeof(express_getattr(temp, 'RelatingMaterial', INDETERMINATE))]) == 1) is not False

class IfcPlateType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPlateType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcPlateTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcPlateTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

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
        assert (sizeof(typeof(polygonalboundary) * ['ifc4x2.ifcpolyline', 'ifc4x2.ifccompositecurve']) == 1) is not False

class IfcPolyline_SameDim:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPolyline'
    RULE_NAME = 'SameDim'

    @staticmethod
    def __call__(self):
        points = express_getattr(self, 'Points', INDETERMINATE)
        assert (sizeof([temp for temp in points if express_getattr(temp, 'Dim', INDETERMINATE) != express_getattr(express_getitem(points, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)]) == 0) is not False

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
        assert (sizeof([temp for temp in assigneditems if sizeof(typeof(temp) * ['ifc4x2.ifcshaperepresentation', 'ifc4x2.ifcgeometricrepresentationitem', 'ifc4x2.ifcmappeditem']) == 1]) == sizeof(assigneditems)) is not False

class IfcPresentationLayerWithStyle_ApplicableOnlyToItems:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPresentationLayerWithStyle'
    RULE_NAME = 'ApplicableOnlyToItems'

    @staticmethod
    def __call__(self):
        assigneditems = express_getattr(self, 'AssignedItems', INDETERMINATE)
        assert (sizeof([temp for temp in assigneditems if sizeof(typeof(temp) * ['ifc4x2.ifcgeometricrepresentationitem', 'ifc4x2.ifcmappeditem']) >= 1]) == sizeof(assigneditems)) is not False

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
        assert (exists(representation) and exists(objectplacement) or (exists(representation) and sizeof([temp for temp in express_getattr(representation, 'Representations', INDETERMINATE) if 'ifc4x2.ifcshaperepresentation' in typeof(temp)]) == 0) or (not exists(representation))) is not False

class IfcProductDefinitionShape_OnlyShapeModel:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProductDefinitionShape'
    RULE_NAME = 'OnlyShapeModel'

    @staticmethod
    def __call__(self):
        representations = express_getattr(self, 'Representations', INDETERMINATE)
        assert (sizeof([temp for temp in representations if not 'ifc4x2.ifcshapemodel' in typeof(temp)]) == 0) is not False

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
        assert (not exists(express_getattr(self, 'RepresentationContexts', INDETERMINATE)) or sizeof([temp for temp in express_getattr(self, 'RepresentationContexts', INDETERMINATE) if 'ifc4x2.ifcgeometricrepresentationsubcontext' in typeof(temp)]) == 0) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcprotectivedevicetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcprotectivedevicetrippingunittype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcpumptype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcrailingtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcRailingType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRailingType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcRailingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcRailingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcramptype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcrampflighttype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert ('ifc4x2.ifcelementarysurface' in typeof(basissurface) and (not 'ifc4x2.ifcplane' in typeof(basissurface)) or 'ifc4x2.ifcsurfaceofrevolution' in typeof(basissurface) or usense == (u2 > u1)) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcreinforcingbartype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcreinforcingmeshtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof([temp for temp in express_getattr(self, 'RelatedObjects', INDETERMINATE) if 'ifc4x2.ifcfeatureelementsubtraction' in typeof(temp) or 'ifc4x2.ifcvirtualelement' in typeof(temp)]) == 0) is not False

class IfcRelAssociatesMaterial_AllowedElements:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssociatesMaterial'
    RULE_NAME = 'AllowedElements'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in express_getattr(self, 'RelatedObjects', INDETERMINATE) if sizeof(typeof(temp) * ['ifc4x2.ifcelement', 'ifc4x2.ifcelementtype', 'ifc4x2.ifcwindowstyle', 'ifc4x2.ifcdoorstyle', 'ifc4x2.ifcstructuralmember', 'ifc4x2.ifcport']) == 0]) == 0) is not False

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
        assert (sizeof([temp for temp in relatedelements if 'ifc4x2.ifcspatialstructureelement' in typeof(temp)]) == 0) is not False

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
        assert (sizeof([types for types in express_getattr(self, 'RelatedObjects', INDETERMINATE) if 'ifc4x2.ifctypeobject' in typeof(types)]) == 0) is not False

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
        assert (sizeof([temp for temp in relatedelements if 'ifc4x2.ifcspatialstructureelement' in typeof(temp) and (not 'ifc4x2.ifcspace' in typeof(temp))]) == 0) is not False

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
        assert (physicalorvirtualboundary == express_getattr(IfcPhysicalOrVirtualEnum, 'Physical', INDETERMINATE) and (not 'ifc4x2.ifcvirtualelement' in typeof(relatedbuildingelement)) or (physicalorvirtualboundary == express_getattr(IfcPhysicalOrVirtualEnum, 'Virtual', INDETERMINATE) and ('ifc4x2.ifcvirtualelement' in typeof(relatedbuildingelement) or 'ifc4x2.ifcopeningelement' in typeof(relatedbuildingelement))) or physicalorvirtualboundary == express_getattr(IfcPhysicalOrVirtualEnum, 'NotDefined', INDETERMINATE)) is not False

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
        assert ('ifc4x2.ifcshapemodel' in typeof(mappedrepresentation)) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcrooftype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcsanitaryterminaltype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof([temp for temp in crosssectionpositions if exists(express_getattr(temp, 'OffsetLongitudinal', INDETERMINATE))]) == 0) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcsensortype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcshadingdevicetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert ('ifc4x2.ifcgeometricrepresentationcontext' in typeof(express_getattr(self, 'ContextOfItems', INDETERMINATE))) is not False

class IfcShapeRepresentation_NoTopologicalItem:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcShapeRepresentation'
    RULE_NAME = 'NoTopologicalItem'

    @staticmethod
    def __call__(self):
        items = express_getattr(self, 'Items', INDETERMINATE)
        assert (sizeof([temp for temp in items if 'ifc4x2.ifctopologicalrepresentationitem' in typeof(temp) and (not sizeof(['ifc4x2.ifcvertexpoint', 'ifc4x2.ifcedgecurve', 'ifc4x2.ifcfacesurface'] * typeof(temp)) == 1)]) == 0) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcslabtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof([temp for temp in usedin(self, 'ifc4x2.ifcrelassociates.relatedobjects') if 'ifc4x2.ifcrelassociatesmaterial' in typeof(temp) and 'ifc4x2.ifcmateriallayersetusage' in typeof(express_getattr(temp, 'RelatingMaterial', INDETERMINATE))]) == 1) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcsolardevicetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcspacetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcspaceheatertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (hiindex(express_getattr(self, 'Decomposes', INDETERMINATE)) == 1 and 'ifc4x2.ifcrelaggregates' in typeof(express_getitem(express_getattr(self, 'Decomposes', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and ('ifc4x2.ifcproject' in typeof(express_getattr(express_getitem(express_getattr(self, 'Decomposes', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingObject', INDETERMINATE)) or 'ifc4x2.ifcspatialstructureelement' in typeof(express_getattr(express_getitem(express_getattr(self, 'Decomposes', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingObject', INDETERMINATE)))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcspatialzonetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcstackterminaltype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcstairtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcstairflighttype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(['ifc4x2.ifcstructuralloadlinearforce', 'ifc4x2.ifcstructuralloadtemperature'] * typeof(express_getattr(self, 'AppliedLoad', INDETERMINATE))) == 1) is not False

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
        assert (sizeof(['ifc4x2.ifcstructuralloadplanarforce', 'ifc4x2.ifcstructuralloadtemperature'] * typeof(express_getattr(self, 'AppliedLoad', INDETERMINATE))) == 1) is not False

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
        assert (sizeof(['ifc4x2.ifcstructuralloadsingleforce', 'ifc4x2.ifcstructuralloadsingledisplacement'] * typeof(express_getattr(self, 'AppliedLoad', INDETERMINATE))) == 1) is not False

class IfcStructuralPointReaction_SuitableLoadType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralPointReaction'
    RULE_NAME = 'SuitableLoadType'

    @staticmethod
    def __call__(self):
        assert (sizeof(['ifc4x2.ifcstructuralloadsingleforce', 'ifc4x2.ifcstructuralloadsingledisplacement'] * typeof(express_getattr(self, 'AppliedLoad', INDETERMINATE))) == 1) is not False

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
        assert (not 'ifc4x2.ifcstyleditem' in typeof(item)) is not False

class IfcStyledRepresentation_OnlyStyledItems:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStyledRepresentation'
    RULE_NAME = 'OnlyStyledItems'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in express_getattr(self, 'Items', INDETERMINATE) if not 'ifc4x2.ifcstyleditem' in typeof(temp)]) == 0) is not False

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
        assert (not 'ifc4x2.ifcpcurve' in typeof(curve3d)) is not False

def calc_IfcSurfaceCurve_BasisSurface(self):
    return IfcGetBasisSurface(self)

class IfcSurfaceCurveSweptAreaSolid_DirectrixBounded:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceCurveSweptAreaSolid'
    RULE_NAME = 'DirectrixBounded'

    @staticmethod
    def __call__(self):
        directrix = express_getattr(self, 'Directrix', INDETERMINATE)
        startparam = express_getattr(self, 'StartParam', INDETERMINATE)
        endparam = express_getattr(self, 'EndParam', INDETERMINATE)
        assert (exists(startparam) and exists(endparam) or sizeof(['ifc4x2.ifcconic', 'ifc4x2.ifcboundedcurve'] * typeof(directrix)) == 1) is not False

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
        assert (sizeof([style for style in express_getattr(self, 'Styles', INDETERMINATE) if 'ifc4x2.ifcsurfacestyleshading' in typeof(style)]) <= 1) is not False

class IfcSurfaceStyle_MaxOneLighting:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceStyle'
    RULE_NAME = 'MaxOneLighting'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in express_getattr(self, 'Styles', INDETERMINATE) if 'ifc4x2.ifcsurfacestylelighting' in typeof(style)]) <= 1) is not False

class IfcSurfaceStyle_MaxOneRefraction:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceStyle'
    RULE_NAME = 'MaxOneRefraction'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in express_getattr(self, 'Styles', INDETERMINATE) if 'ifc4x2.ifcsurfacestylerefraction' in typeof(style)]) <= 1) is not False

class IfcSurfaceStyle_MaxOneTextures:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceStyle'
    RULE_NAME = 'MaxOneTextures'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in express_getattr(self, 'Styles', INDETERMINATE) if 'ifc4x2.ifcsurfacestylewithtextures' in typeof(style)]) <= 1) is not False

class IfcSurfaceStyle_MaxOneExtDefined:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceStyle'
    RULE_NAME = 'MaxOneExtDefined'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in express_getattr(self, 'Styles', INDETERMINATE) if 'ifc4x2.ifcexternallydefinedsurfacestyle' in typeof(style)]) <= 1) is not False

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
        assert (exists(startparam) and exists(endparam) or sizeof(['ifc4x2.ifcconic', 'ifc4x2.ifcboundedcurve'] * typeof(directrix)) == 1) is not False

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
        assert ('ifc4x2.ifcpolyline' in typeof(express_getattr(self, 'Directrix', INDETERMINATE)) or ('ifc4x2.ifcindexedpolycurve' in typeof(express_getattr(self, 'Directrix', INDETERMINATE)) and (not exists(express_getattr(express_getattr(self, 'Directrix', INDETERMINATE), 'Segments', INDETERMINATE))))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcswitchingdevicetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcsystemfurnitureelementtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifctanktype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifctendontype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifctendonanchortype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifctendonconduittype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (not 'ifc4x2.ifcplanarbox' in typeof(extent)) is not False

class IfcTextStyleFontModel_MeasureOfFontSize:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTextStyleFontModel'
    RULE_NAME = 'MeasureOfFontSize'

    @staticmethod
    def __call__(self):
        assert ('ifc4x2.ifclengthmeasure' in typeof(express_getattr(self, 'FontSize', INDETERMINATE)) and express_getattr(self, 'FontSize', INDETERMINATE) > 0.0) is not False

class IfcTopologyRepresentation_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTopologyRepresentation'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in express_getattr(self, 'Items', INDETERMINATE) if not 'ifc4x2.ifctopologicalrepresentationitem' in typeof(temp)]) == 0) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifctranformertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcTransportElementTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcTransportElementTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcTransportElement_CorrectTypeAssigned:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTransportElement'
    RULE_NAME = 'CorrectTypeAssigned'

    @staticmethod
    def __call__(self):
        istypedby = express_getattr(self, 'IsTypedBy', INDETERMINATE)
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifctransportelementtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

class IfcTransportElementType_CorrectPredefinedType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTransportElementType'
    RULE_NAME = 'CorrectPredefinedType'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcTransportElementTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcTransportElementTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

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
        assert (not 'ifc4x2.ifcboundedcurve' in typeof(basiscurve)) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifctubebundletype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (not exists(lambda : express_getitem(express_getattr(self, 'Types', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) or sizeof([temp for temp in express_getattr(express_getitem(express_getattr(self, 'Types', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatedObjects', INDETERMINATE) if not 'ifc4x2.ifcproduct' in typeof(temp)]) == 0) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcunitarycontrolelementtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcunitaryequipmenttype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcvalvetype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcvibrationdampertype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcvibrationisolatortype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcwalltype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof([temp for temp in usedin(self, 'ifc4x2.ifcrelassociates.relatedobjects') if 'ifc4x2.ifcrelassociatesmaterial' in typeof(temp) and 'ifc4x2.ifcmateriallayersetusage' in typeof(express_getattr(temp, 'RelatingMaterial', INDETERMINATE))]) == 1) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcwasteterminaltype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (sizeof(istypedby) == 0 or 'ifc4x2.ifcwindowtype' in typeof(express_getattr(express_getitem(express_getattr(self, 'IsTypedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingType', INDETERMINATE))) is not False

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
        assert (exists(lambda : express_getitem(express_getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and ('ifc4x2.ifcwindowtype' in typeof(express_getitem(express_getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) or 'ifc4x2.ifcwindowstyle' in typeof(express_getitem(express_getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)))) is not False

class IfcWindowPanelProperties_ApplicableToType:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWindowPanelProperties'
    RULE_NAME = 'ApplicableToType'

    @staticmethod
    def __call__(self):
        assert (exists(lambda : express_getitem(express_getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and ('ifc4x2.ifcwindowtype' in typeof(express_getitem(express_getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) or 'ifc4x2.ifcwindowstyle' in typeof(express_getitem(express_getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)))) is not False

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
        assert (sizeof(express_getattr(self, 'IsGroupedBy', INDETERMINATE)) == 0 or sizeof([temp for temp in express_getattr(express_getitem(express_getattr(self, 'IsGroupedBy', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatedObjects', INDETERMINATE) if not ('ifc4x2.ifczone' in typeof(temp) or 'ifc4x2.ifcspace' in typeof(temp) or 'ifc4x2.ifcspatialzone' in typeof(temp))]) == 0) is not False

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
    external = sizeof([style for style in styles if 'ifc4x2.ifcexternallydefinedhatchstyle' in typeof(style)])
    hatching = sizeof([style for style in styles if 'ifc4x2.ifcfillareastylehatching' in typeof(style)])
    tiles = sizeof([style for style in styles if 'ifc4x2.ifcfillareastyletiles' in typeof(style)])
    colour = sizeof([style for style in styles if 'ifc4x2.ifccolour' in typeof(style)])
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
        if 'ifc4x2.ifcgridplacement' in typeof(relplacement):
            return None
        if 'ifc4x2.ifclocalplacement' in typeof(relplacement):
            if 'ifc4x2.ifcaxis2placement2d' in typeof(axisplacement):
                return True
            if 'ifc4x2.ifcaxis2placement3d' in typeof(axisplacement):
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
        count = sizeof([temp for temp in objects if not 'ifc4x2.ifcproduct' in typeof(temp)])
        return count == 0
    elif constraint == express_getattr(IfcObjectTypeEnum, 'PROCESS', INDETERMINATE):
        count = sizeof([temp for temp in objects if not 'ifc4x2.ifcprocess' in typeof(temp)])
        return count == 0
    elif constraint == express_getattr(IfcObjectTypeEnum, 'CONTROL', INDETERMINATE):
        count = sizeof([temp for temp in objects if not 'ifc4x2.ifccontrol' in typeof(temp)])
        return count == 0
    elif constraint == express_getattr(IfcObjectTypeEnum, 'RESOURCE', INDETERMINATE):
        count = sizeof([temp for temp in objects if not 'ifc4x2.ifcresource' in typeof(temp)])
        return count == 0
    elif constraint == express_getattr(IfcObjectTypeEnum, 'ACTOR', INDETERMINATE):
        count = sizeof([temp for temp in objects if not 'ifc4x2.ifcactor' in typeof(temp)])
        return count == 0
    elif constraint == express_getattr(IfcObjectTypeEnum, 'GROUP', INDETERMINATE):
        count = sizeof([temp for temp in objects if not 'ifc4x2.ifcgroup' in typeof(temp)])
        return count == 0
    elif constraint == express_getattr(IfcObjectTypeEnum, 'PROJECT', INDETERMINATE):
        count = sizeof([temp for temp in objects if not 'ifc4x2.ifcproject' in typeof(temp)])
        return count == 0
    else:
        return None

def IfcCorrectUnitAssignment(units):
    namedunitnumber = 0
    derivedunitnumber = 0
    monetaryunitnumber = 0
    namedunitnames = express_set([])
    derivedunitnames = express_set([])
    namedunitnumber = sizeof([temp for temp in units if 'ifc4x2.ifcnamedunit' in typeof(temp) and (not express_getattr(temp, 'UnitType', INDETERMINATE) == express_getattr(IfcUnitEnum, 'USERDEFINED', INDETERMINATE))])
    derivedunitnumber = sizeof([temp for temp in units if 'ifc4x2.ifcderivedunit' in typeof(temp) and (not express_getattr(temp, 'UnitType', INDETERMINATE) == express_getattr(IfcDerivedUnitEnum, 'USERDEFINED', INDETERMINATE))])
    monetaryunitnumber = sizeof([temp for temp in units if 'ifc4x2.ifcmonetaryunit' in typeof(temp)])
    for i in range(1, sizeof(units) + 1):
        if 'ifc4x2.ifcnamedunit' in typeof(express_getitem(units, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and (not express_getattr(express_getitem(units, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'UnitType', INDETERMINATE) == express_getattr(IfcUnitEnum, 'USERDEFINED', INDETERMINATE)):
            namedunitnames = namedunitnames + express_getattr(express_getitem(units, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'UnitType', INDETERMINATE)
        if 'ifc4x2.ifcderivedunit' in typeof(express_getitem(units, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and (not express_getattr(express_getitem(units, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'UnitType', INDETERMINATE) == express_getattr(IfcDerivedUnitEnum, 'USERDEFINED', INDETERMINATE)):
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
    if 'ifc4x2.ifcline' in typeof(curve):
        return express_getattr(express_getattr(curve, 'Pnt', INDETERMINATE), 'Dim', INDETERMINATE)
    if 'ifc4x2.ifcconic' in typeof(curve):
        return express_getattr(express_getattr(curve, 'Position', INDETERMINATE), 'Dim', INDETERMINATE)
    if 'ifc4x2.ifcpolyline' in typeof(curve):
        return express_getattr(express_getitem(express_getattr(curve, 'Points', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)
    if 'ifc4x2.ifctrimmedcurve' in typeof(curve):
        return IfcCurveDim(express_getattr(curve, 'BasisCurve', INDETERMINATE))
    if 'ifc4x2.ifccompositecurve' in typeof(curve):
        return express_getattr(express_getitem(express_getattr(curve, 'Segments', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)
    if 'ifc4x2.ifcbsplinecurve' in typeof(curve):
        return express_getattr(express_getitem(express_getattr(curve, 'ControlPointsList', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)
    if 'ifc4x2.ifcoffsetcurve2d' in typeof(curve):
        return 2
    if 'ifc4x2.ifcoffsetcurve3d' in typeof(curve):
        return 3
    if 'ifc4x2.ifcoffsetcurvebydistances' in typeof(curve):
        return 3
    if 'ifc4x2.ifccurvesegment2d' in typeof(curve):
        return 2
    if 'ifc4x2.ifcalignmentcurve' in typeof(curve):
        return 3
    if 'ifc4x2.ifcpcurve' in typeof(curve):
        return 3
    if 'ifc4x2.ifcindexedpolycurve' in typeof(curve):
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
    if 'ifc4x2.ifcpcurve' in typeof(c):
        surfs = [express_getattr(c, 'BasisSurface', INDETERMINATE)]
    elif 'ifc4x2.ifcsurfacecurve' in typeof(c):
        n = sizeof(express_getattr(c, 'AssociatedGeometry', INDETERMINATE))
        for i in range(1, n + 1):
            surfs = surfs + IfcAssociatedSurface(express_getitem(express_getattr(c, 'AssociatedGeometry', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))
    if 'ifc4x2.ifccompositecurveonsurface' in typeof(c):
        n = sizeof(express_getattr(c, 'Segments', INDETERMINATE))
        surfs = IfcGetBasisSurface(express_getattr(express_getitem(express_getattr(c, 'Segments', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'ParentCurve', INDETERMINATE))
        if n > 1:
            for i in range(2, n + 1):
                surfs = surfs * IfcGetBasisSurface(express_getattr(express_getitem(express_getattr(c, 'Segments', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'ParentCurve', INDETERMINATE))
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
        if 'ifc4x2.ifcvector' in typeof(arg):
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
            if 'ifc4x2.ifcvector' in typeof(arg):
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
    if 'ifc4x2.ifccartesianpointlist2d' in typeof(pointlist):
        return 2
    if 'ifc4x2.ifccartesianpointlist3d' in typeof(pointlist):
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
        if 'ifc4x2.ifcvector' in typeof(vec):
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
        count = sizeof([temp for temp in items if 'ifc4x2.ifcpoint' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'pointcloud':
        count = sizeof([temp for temp in items if 'ifc4x2.ifccartesianpointlist3d' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'curve':
        count = sizeof([temp for temp in items if 'ifc4x2.ifccurve' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'curve2d':
        count = sizeof([temp for temp in items if 'ifc4x2.ifccurve' in typeof(temp) and express_getattr(temp, 'Dim', INDETERMINATE) == 2])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'curve3d':
        count = sizeof([temp for temp in items if 'ifc4x2.ifccurve' in typeof(temp) and express_getattr(temp, 'Dim', INDETERMINATE) == 3])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'surface':
        count = sizeof([temp for temp in items if 'ifc4x2.ifcsurface' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'surface2d':
        count = sizeof([temp for temp in items if 'ifc4x2.ifcsurface' in typeof(temp) and express_getattr(temp, 'Dim', INDETERMINATE) == 2])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'surface3d':
        count = sizeof([temp for temp in items if 'ifc4x2.ifcsurface' in typeof(temp) and express_getattr(temp, 'Dim', INDETERMINATE) == 3])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'fillarea':
        count = sizeof([temp for temp in items if 'ifc4x2.ifcannotationfillarea' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'text':
        count = sizeof([temp for temp in items if 'ifc4x2.ifctextliteral' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'advancedsurface':
        count = sizeof([temp for temp in items if 'ifc4x2.ifcbsplinesurface' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'annotation2d':
        count = sizeof([temp for temp in items if sizeof(typeof(temp) * ['ifc4x2.ifcpoint', 'ifc4x2.ifccurve', 'ifc4x2.ifcgeometriccurveset', 'ifc4x2.ifcannotationfillarea', 'ifc4x2.ifctextliteral']) == 1])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'geometricset':
        count = sizeof([temp for temp in items if 'ifc4x2.ifcgeometricset' in typeof(temp) or 'ifc4x2.ifcpoint' in typeof(temp) or 'ifc4x2.ifccurve' in typeof(temp) or ('ifc4x2.ifcsurface' in typeof(temp))])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'geometriccurveset':
        count = sizeof([temp for temp in items if 'ifc4x2.ifcgeometriccurveset' in typeof(temp) or 'ifc4x2.ifcgeometricset' in typeof(temp) or 'ifc4x2.ifcpoint' in typeof(temp) or ('ifc4x2.ifccurve' in typeof(temp))])
        for i in range(1, hiindex(items) + 1):
            if 'ifc4x2.ifcgeometricset' in typeof(express_getitem(items, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)):
                if sizeof([temp for temp in express_getattr(express_getitem(items, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Elements', INDETERMINATE) if 'ifc4x2.ifcsurface' in typeof(temp)]) > 0:
                    count = count - 1
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'tessellation':
        count = sizeof([temp for temp in items if 'ifc4x2.ifctessellateditem' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'surfaceorsolidmodel':
        count = sizeof([temp for temp in items if sizeof(['ifc4x2.ifctessellateditem', 'ifc4x2.ifcshellbasedsurfacemodel', 'ifc4x2.ifcfacebasedsurfacemodel', 'ifc4x2.ifcsolidmodel'] * typeof(temp)) >= 1])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'surfacemodel':
        count = sizeof([temp for temp in items if sizeof(['ifc4x2.ifctessellateditem', 'ifc4x2.ifcshellbasedsurfacemodel', 'ifc4x2.ifcfacebasedsurfacemodel'] * typeof(temp)) >= 1])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'solidmodel':
        count = sizeof([temp for temp in items if 'ifc4x2.ifcsolidmodel' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'sweptsolid':
        count = sizeof([temp for temp in items if sizeof(['ifc4x2.ifcextrudedareasolid', 'ifc4x2.ifcrevolvedareasolid'] * typeof(temp)) >= 1 and sizeof(['ifc4x2.ifcextrudedareasolidtapered', 'ifc4x2.ifcrevolvedareasolidtapered'] * typeof(temp)) == 0])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'advancedsweptsolid':
        count = sizeof([temp for temp in items if sizeof(['ifc4x2.ifcsweptareasolid', 'ifc4x2.ifcsweptdisksolid'] * typeof(temp)) >= 1])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'csg':
        count = sizeof([temp for temp in items if sizeof(['ifc4x2.ifcbooleanresult', 'ifc4x2.ifccsgprimitive3d', 'ifc4x2.ifccsgsolid'] * typeof(temp)) >= 1])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'clipping':
        count = sizeof([temp for temp in items if sizeof(['ifc4x2.ifccsgsolid', 'ifc4x2.ifcbooleanclippingresult'] * typeof(temp)) >= 1])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'brep':
        count = sizeof([temp for temp in items if 'ifc4x2.ifcfacetedbrep' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'advancedbrep':
        count = sizeof([temp for temp in items if 'ifc4x2.ifcmanifoldsolidbrep' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'boundingbox':
        count = sizeof([temp for temp in items if 'ifc4x2.ifcboundingbox' in typeof(temp)])
        if sizeof(items) > 1:
            count = 0
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'sectionedspine':
        count = sizeof([temp for temp in items if 'ifc4x2.ifcsectionedspine' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'lightsource':
        count = sizeof([temp for temp in items if 'ifc4x2.ifclightsource' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'mappedrepresentation':
        count = sizeof([temp for temp in items if 'ifc4x2.ifcmappeditem' in typeof(temp)])
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
    if 'ifc4x2.ifcparameterizedprofiledef' in typeof(startarea):
        if 'ifc4x2.ifcderivedprofiledef' in typeof(endarea):
            result = startarea == express_getattr(endarea, 'ParentProfile', INDETERMINATE)
        else:
            result = typeof(startarea) == typeof(endarea)
    elif 'ifc4x2.ifcderivedprofiledef' in typeof(endarea):
        result = startarea == express_getattr(endarea, 'ParentProfile', INDETERMINATE)
    else:
        result = False
    return result

def IfcTopologyRepresentationTypes(reptype, items):
    count = 0
    if express_getattr(reptype, 'lower', INDETERMINATE)() == 'vertex':
        count = sizeof([temp for temp in items if 'ifc4x2.ifcvertex' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'edge':
        count = sizeof([temp for temp in items if 'ifc4x2.ifcedge' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'path':
        count = sizeof([temp for temp in items if 'ifc4x2.ifcpath' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'face':
        count = sizeof([temp for temp in items if 'ifc4x2.ifcface' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'shell':
        count = sizeof([temp for temp in items if 'ifc4x2.ifcopenshell' in typeof(temp) or 'ifc4x2.ifcclosedshell' in typeof(temp)])
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
        if 'ifc4x2.ifcpropertysetdefinition' in typeof(definition):
            properties = properties + definition
        elif 'ifc4x2.ifcpropertysetdefinitionset' in typeof(definition):
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
        if 'ifc4x2.ifcpropertyset' in typeof(express_getitem(properties, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)):
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
        if 'ifc4x2.ifcvector' in typeof(arg1):
            mag1 = express_getattr(arg1, 'Magnitude', INDETERMINATE)
            vec1 = express_getattr(arg1, 'Orientation', INDETERMINATE)
        else:
            mag1 = 1.0
            vec1 = arg1
        if 'ifc4x2.ifcvector' in typeof(arg2):
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
        if 'ifc4x2.ifcvector' in typeof(arg1):
            mag1 = express_getattr(arg1, 'Magnitude', INDETERMINATE)
            vec1 = express_getattr(arg1, 'Orientation', INDETERMINATE)
        else:
            mag1 = 1.0
            vec1 = arg1
        if 'ifc4x2.ifcvector' in typeof(arg2):
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