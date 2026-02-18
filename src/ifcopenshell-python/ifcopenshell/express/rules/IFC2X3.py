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
IfcAheadOrBehind = enum_namespace()
ahead = IfcAheadOrBehind.AHEAD
behind = IfcAheadOrBehind.BEHIND
IfcAirTerminalBoxTypeEnum = enum_namespace()
constantflow = IfcAirTerminalBoxTypeEnum.CONSTANTFLOW
variableflowpressuredependant = IfcAirTerminalBoxTypeEnum.VARIABLEFLOWPRESSUREDEPENDANT
variableflowpressureindependant = IfcAirTerminalBoxTypeEnum.VARIABLEFLOWPRESSUREINDEPENDANT
userdefined = IfcAirTerminalBoxTypeEnum.USERDEFINED
notdefined = IfcAirTerminalBoxTypeEnum.NOTDEFINED
IfcAirTerminalTypeEnum = enum_namespace()
grille = IfcAirTerminalTypeEnum.GRILLE
register = IfcAirTerminalTypeEnum.REGISTER
diffuser = IfcAirTerminalTypeEnum.DIFFUSER
eyeball = IfcAirTerminalTypeEnum.EYEBALL
iris = IfcAirTerminalTypeEnum.IRIS
lineargrille = IfcAirTerminalTypeEnum.LINEARGRILLE
lineardiffuser = IfcAirTerminalTypeEnum.LINEARDIFFUSER
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
IfcBSplineCurveForm = enum_namespace()
polyline_form = IfcBSplineCurveForm.POLYLINE_FORM
circular_arc = IfcBSplineCurveForm.CIRCULAR_ARC
elliptic_arc = IfcBSplineCurveForm.ELLIPTIC_ARC
parabolic_arc = IfcBSplineCurveForm.PARABOLIC_ARC
hyperbolic_arc = IfcBSplineCurveForm.HYPERBOLIC_ARC
unspecified = IfcBSplineCurveForm.UNSPECIFIED
IfcBeamTypeEnum = enum_namespace()
beam = IfcBeamTypeEnum.BEAM
joist = IfcBeamTypeEnum.JOIST
lintel = IfcBeamTypeEnum.LINTEL
t_beam = IfcBeamTypeEnum.T_BEAM
userdefined = IfcBeamTypeEnum.USERDEFINED
notdefined = IfcBeamTypeEnum.NOTDEFINED
IfcBenchmarkEnum = enum_namespace()
greaterthan = IfcBenchmarkEnum.GREATERTHAN
greaterthanorequalto = IfcBenchmarkEnum.GREATERTHANOREQUALTO
lessthan = IfcBenchmarkEnum.LESSTHAN
lessthanorequalto = IfcBenchmarkEnum.LESSTHANOREQUALTO
equalto = IfcBenchmarkEnum.EQUALTO
notequalto = IfcBenchmarkEnum.NOTEQUALTO
IfcBoilerTypeEnum = enum_namespace()
water = IfcBoilerTypeEnum.WATER
steam = IfcBoilerTypeEnum.STEAM
userdefined = IfcBoilerTypeEnum.USERDEFINED
notdefined = IfcBoilerTypeEnum.NOTDEFINED
IfcBooleanOperator = enum_namespace()
union = IfcBooleanOperator.UNION
intersection = IfcBooleanOperator.INTERSECTION
difference = IfcBooleanOperator.DIFFERENCE
IfcBuildingElementProxyTypeEnum = enum_namespace()
userdefined = IfcBuildingElementProxyTypeEnum.USERDEFINED
notdefined = IfcBuildingElementProxyTypeEnum.NOTDEFINED
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
IfcCableSegmentTypeEnum = enum_namespace()
cablesegment = IfcCableSegmentTypeEnum.CABLESEGMENT
conductorsegment = IfcCableSegmentTypeEnum.CONDUCTORSEGMENT
userdefined = IfcCableSegmentTypeEnum.USERDEFINED
notdefined = IfcCableSegmentTypeEnum.NOTDEFINED
IfcChangeActionEnum = enum_namespace()
nochange = IfcChangeActionEnum.NOCHANGE
modified = IfcChangeActionEnum.MODIFIED
added = IfcChangeActionEnum.ADDED
deleted = IfcChangeActionEnum.DELETED
modifiedadded = IfcChangeActionEnum.MODIFIEDADDED
modifieddeleted = IfcChangeActionEnum.MODIFIEDDELETED
IfcChillerTypeEnum = enum_namespace()
aircooled = IfcChillerTypeEnum.AIRCOOLED
watercooled = IfcChillerTypeEnum.WATERCOOLED
heatrecovery = IfcChillerTypeEnum.HEATRECOVERY
userdefined = IfcChillerTypeEnum.USERDEFINED
notdefined = IfcChillerTypeEnum.NOTDEFINED
IfcCoilTypeEnum = enum_namespace()
dxcoolingcoil = IfcCoilTypeEnum.DXCOOLINGCOIL
watercoolingcoil = IfcCoilTypeEnum.WATERCOOLINGCOIL
steamheatingcoil = IfcCoilTypeEnum.STEAMHEATINGCOIL
waterheatingcoil = IfcCoilTypeEnum.WATERHEATINGCOIL
electricheatingcoil = IfcCoilTypeEnum.ELECTRICHEATINGCOIL
gasheatingcoil = IfcCoilTypeEnum.GASHEATINGCOIL
userdefined = IfcCoilTypeEnum.USERDEFINED
notdefined = IfcCoilTypeEnum.NOTDEFINED
IfcColumnTypeEnum = enum_namespace()
column = IfcColumnTypeEnum.COLUMN
userdefined = IfcColumnTypeEnum.USERDEFINED
notdefined = IfcColumnTypeEnum.NOTDEFINED
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
watercooledshelltube = IfcCondenserTypeEnum.WATERCOOLEDSHELLTUBE
watercooledshellcoil = IfcCondenserTypeEnum.WATERCOOLEDSHELLCOIL
watercooledtubeintube = IfcCondenserTypeEnum.WATERCOOLEDTUBEINTUBE
watercooledbrazedplate = IfcCondenserTypeEnum.WATERCOOLEDBRAZEDPLATE
aircooled = IfcCondenserTypeEnum.AIRCOOLED
evaporativecooled = IfcCondenserTypeEnum.EVAPORATIVECOOLED
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
IfcControllerTypeEnum = enum_namespace()
floating = IfcControllerTypeEnum.FLOATING
proportional = IfcControllerTypeEnum.PROPORTIONAL
proportionalintegral = IfcControllerTypeEnum.PROPORTIONALINTEGRAL
proportionalintegralderivative = IfcControllerTypeEnum.PROPORTIONALINTEGRALDERIVATIVE
timedtwoposition = IfcControllerTypeEnum.TIMEDTWOPOSITION
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
insulation = IfcCoveringTypeEnum.INSULATION
membrane = IfcCoveringTypeEnum.MEMBRANE
sleeving = IfcCoveringTypeEnum.SLEEVING
wrapping = IfcCoveringTypeEnum.WRAPPING
userdefined = IfcCoveringTypeEnum.USERDEFINED
notdefined = IfcCoveringTypeEnum.NOTDEFINED
IfcCurrencyEnum = enum_namespace()
aed = IfcCurrencyEnum.AED
aes = IfcCurrencyEnum.AES
ats = IfcCurrencyEnum.ATS
aud = IfcCurrencyEnum.AUD
bbd = IfcCurrencyEnum.BBD
beg = IfcCurrencyEnum.BEG
bgl = IfcCurrencyEnum.BGL
bhd = IfcCurrencyEnum.BHD
bmd = IfcCurrencyEnum.BMD
bnd = IfcCurrencyEnum.BND
brl = IfcCurrencyEnum.BRL
bsd = IfcCurrencyEnum.BSD
bwp = IfcCurrencyEnum.BWP
bzd = IfcCurrencyEnum.BZD
cad = IfcCurrencyEnum.CAD
cbd = IfcCurrencyEnum.CBD
chf = IfcCurrencyEnum.CHF
clp = IfcCurrencyEnum.CLP
cny = IfcCurrencyEnum.CNY
cys = IfcCurrencyEnum.CYS
czk = IfcCurrencyEnum.CZK
ddp = IfcCurrencyEnum.DDP
dem = IfcCurrencyEnum.DEM
dkk = IfcCurrencyEnum.DKK
egl = IfcCurrencyEnum.EGL
est = IfcCurrencyEnum.EST
eur = IfcCurrencyEnum.EUR
fak = IfcCurrencyEnum.FAK
fim = IfcCurrencyEnum.FIM
fjd = IfcCurrencyEnum.FJD
fkp = IfcCurrencyEnum.FKP
frf = IfcCurrencyEnum.FRF
gbp = IfcCurrencyEnum.GBP
gip = IfcCurrencyEnum.GIP
gmd = IfcCurrencyEnum.GMD
grx = IfcCurrencyEnum.GRX
hkd = IfcCurrencyEnum.HKD
huf = IfcCurrencyEnum.HUF
ick = IfcCurrencyEnum.ICK
idr = IfcCurrencyEnum.IDR
ils = IfcCurrencyEnum.ILS
inr = IfcCurrencyEnum.INR
irp = IfcCurrencyEnum.IRP
itl = IfcCurrencyEnum.ITL
jmd = IfcCurrencyEnum.JMD
jod = IfcCurrencyEnum.JOD
jpy = IfcCurrencyEnum.JPY
kes = IfcCurrencyEnum.KES
krw = IfcCurrencyEnum.KRW
kwd = IfcCurrencyEnum.KWD
kyd = IfcCurrencyEnum.KYD
lkr = IfcCurrencyEnum.LKR
luf = IfcCurrencyEnum.LUF
mtl = IfcCurrencyEnum.MTL
mur = IfcCurrencyEnum.MUR
mxn = IfcCurrencyEnum.MXN
myr = IfcCurrencyEnum.MYR
nlg = IfcCurrencyEnum.NLG
nzd = IfcCurrencyEnum.NZD
omr = IfcCurrencyEnum.OMR
pgk = IfcCurrencyEnum.PGK
php = IfcCurrencyEnum.PHP
pkr = IfcCurrencyEnum.PKR
pln = IfcCurrencyEnum.PLN
ptn = IfcCurrencyEnum.PTN
qar = IfcCurrencyEnum.QAR
rur = IfcCurrencyEnum.RUR
sar = IfcCurrencyEnum.SAR
scr = IfcCurrencyEnum.SCR
sek = IfcCurrencyEnum.SEK
sgd = IfcCurrencyEnum.SGD
skp = IfcCurrencyEnum.SKP
thb = IfcCurrencyEnum.THB
trl = IfcCurrencyEnum.TRL
ttd = IfcCurrencyEnum.TTD
twd = IfcCurrencyEnum.TWD
usd = IfcCurrencyEnum.USD
veb = IfcCurrencyEnum.VEB
vnd = IfcCurrencyEnum.VND
xeu = IfcCurrencyEnum.XEU
zar = IfcCurrencyEnum.ZAR
zwd = IfcCurrencyEnum.ZWD
nok = IfcCurrencyEnum.NOK
IfcCurtainWallTypeEnum = enum_namespace()
userdefined = IfcCurtainWallTypeEnum.USERDEFINED
notdefined = IfcCurtainWallTypeEnum.NOTDEFINED
IfcDamperTypeEnum = enum_namespace()
controldamper = IfcDamperTypeEnum.CONTROLDAMPER
firedamper = IfcDamperTypeEnum.FIREDAMPER
smokedamper = IfcDamperTypeEnum.SMOKEDAMPER
firesmokedamper = IfcDamperTypeEnum.FIRESMOKEDAMPER
backdraftdamper = IfcDamperTypeEnum.BACKDRAFTDAMPER
reliefdamper = IfcDamperTypeEnum.RELIEFDAMPER
blastdamper = IfcDamperTypeEnum.BLASTDAMPER
gravitydamper = IfcDamperTypeEnum.GRAVITYDAMPER
gravityreliefdamper = IfcDamperTypeEnum.GRAVITYRELIEFDAMPER
balancingdamper = IfcDamperTypeEnum.BALANCINGDAMPER
fumehoodexhaust = IfcDamperTypeEnum.FUMEHOODEXHAUST
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
soundpowerunit = IfcDerivedUnitEnum.SOUNDPOWERUNIT
soundpressureunit = IfcDerivedUnitEnum.SOUNDPRESSUREUNIT
temperaturegradientunit = IfcDerivedUnitEnum.TEMPERATUREGRADIENTUNIT
thermalexpansioncoefficientunit = IfcDerivedUnitEnum.THERMALEXPANSIONCOEFFICIENTUNIT
warpingconstantunit = IfcDerivedUnitEnum.WARPINGCONSTANTUNIT
warpingmomentunit = IfcDerivedUnitEnum.WARPINGMOMENTUNIT
userdefined = IfcDerivedUnitEnum.USERDEFINED
IfcDimensionExtentUsage = enum_namespace()
origin = IfcDimensionExtentUsage.ORIGIN
target = IfcDimensionExtentUsage.TARGET
IfcDirectionSenseEnum = enum_namespace()
positive = IfcDirectionSenseEnum.POSITIVE
negative = IfcDirectionSenseEnum.NEGATIVE
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
computer = IfcElectricApplianceTypeEnum.COMPUTER
directwaterheater = IfcElectricApplianceTypeEnum.DIRECTWATERHEATER
dishwasher = IfcElectricApplianceTypeEnum.DISHWASHER
electriccooker = IfcElectricApplianceTypeEnum.ELECTRICCOOKER
electricheater = IfcElectricApplianceTypeEnum.ELECTRICHEATER
facsimile = IfcElectricApplianceTypeEnum.FACSIMILE
freestandingfan = IfcElectricApplianceTypeEnum.FREESTANDINGFAN
freezer = IfcElectricApplianceTypeEnum.FREEZER
fridge_freezer = IfcElectricApplianceTypeEnum.FRIDGE_FREEZER
handdryer = IfcElectricApplianceTypeEnum.HANDDRYER
indirectwaterheater = IfcElectricApplianceTypeEnum.INDIRECTWATERHEATER
microwave = IfcElectricApplianceTypeEnum.MICROWAVE
photocopier = IfcElectricApplianceTypeEnum.PHOTOCOPIER
printer = IfcElectricApplianceTypeEnum.PRINTER
refrigerator = IfcElectricApplianceTypeEnum.REFRIGERATOR
radiantheater = IfcElectricApplianceTypeEnum.RADIANTHEATER
scanner = IfcElectricApplianceTypeEnum.SCANNER
telephone = IfcElectricApplianceTypeEnum.TELEPHONE
tumbledryer = IfcElectricApplianceTypeEnum.TUMBLEDRYER
tv = IfcElectricApplianceTypeEnum.TV
vendingmachine = IfcElectricApplianceTypeEnum.VENDINGMACHINE
washingmachine = IfcElectricApplianceTypeEnum.WASHINGMACHINE
waterheater = IfcElectricApplianceTypeEnum.WATERHEATER
watercooler = IfcElectricApplianceTypeEnum.WATERCOOLER
userdefined = IfcElectricApplianceTypeEnum.USERDEFINED
notdefined = IfcElectricApplianceTypeEnum.NOTDEFINED
IfcElectricCurrentEnum = enum_namespace()
alternating = IfcElectricCurrentEnum.ALTERNATING
direct = IfcElectricCurrentEnum.DIRECT
notdefined = IfcElectricCurrentEnum.NOTDEFINED
IfcElectricDistributionPointFunctionEnum = enum_namespace()
alarmpanel = IfcElectricDistributionPointFunctionEnum.ALARMPANEL
consumerunit = IfcElectricDistributionPointFunctionEnum.CONSUMERUNIT
controlpanel = IfcElectricDistributionPointFunctionEnum.CONTROLPANEL
distributionboard = IfcElectricDistributionPointFunctionEnum.DISTRIBUTIONBOARD
gasdetectorpanel = IfcElectricDistributionPointFunctionEnum.GASDETECTORPANEL
indicatorpanel = IfcElectricDistributionPointFunctionEnum.INDICATORPANEL
mimicpanel = IfcElectricDistributionPointFunctionEnum.MIMICPANEL
motorcontrolcentre = IfcElectricDistributionPointFunctionEnum.MOTORCONTROLCENTRE
switchboard = IfcElectricDistributionPointFunctionEnum.SWITCHBOARD
userdefined = IfcElectricDistributionPointFunctionEnum.USERDEFINED
notdefined = IfcElectricDistributionPointFunctionEnum.NOTDEFINED
IfcElectricFlowStorageDeviceTypeEnum = enum_namespace()
battery = IfcElectricFlowStorageDeviceTypeEnum.BATTERY
capacitorbank = IfcElectricFlowStorageDeviceTypeEnum.CAPACITORBANK
harmonicfilter = IfcElectricFlowStorageDeviceTypeEnum.HARMONICFILTER
inductorbank = IfcElectricFlowStorageDeviceTypeEnum.INDUCTORBANK
ups = IfcElectricFlowStorageDeviceTypeEnum.UPS
userdefined = IfcElectricFlowStorageDeviceTypeEnum.USERDEFINED
notdefined = IfcElectricFlowStorageDeviceTypeEnum.NOTDEFINED
IfcElectricGeneratorTypeEnum = enum_namespace()
userdefined = IfcElectricGeneratorTypeEnum.USERDEFINED
notdefined = IfcElectricGeneratorTypeEnum.NOTDEFINED
IfcElectricHeaterTypeEnum = enum_namespace()
electricpointheater = IfcElectricHeaterTypeEnum.ELECTRICPOINTHEATER
electriccableheater = IfcElectricHeaterTypeEnum.ELECTRICCABLEHEATER
electricmatheater = IfcElectricHeaterTypeEnum.ELECTRICMATHEATER
userdefined = IfcElectricHeaterTypeEnum.USERDEFINED
notdefined = IfcElectricHeaterTypeEnum.NOTDEFINED
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
userdefined = IfcElementAssemblyTypeEnum.USERDEFINED
notdefined = IfcElementAssemblyTypeEnum.NOTDEFINED
IfcElementCompositionEnum = enum_namespace()
complex = IfcElementCompositionEnum.COMPLEX
element = IfcElementCompositionEnum.ELEMENT
partial = IfcElementCompositionEnum.PARTIAL
IfcEnergySequenceEnum = enum_namespace()
primary = IfcEnergySequenceEnum.PRIMARY
secondary = IfcEnergySequenceEnum.SECONDARY
tertiary = IfcEnergySequenceEnum.TERTIARY
auxiliary = IfcEnergySequenceEnum.AUXILIARY
userdefined = IfcEnergySequenceEnum.USERDEFINED
notdefined = IfcEnergySequenceEnum.NOTDEFINED
IfcEnvironmentalImpactCategoryEnum = enum_namespace()
combinedvalue = IfcEnvironmentalImpactCategoryEnum.COMBINEDVALUE
disposal = IfcEnvironmentalImpactCategoryEnum.DISPOSAL
extraction = IfcEnvironmentalImpactCategoryEnum.EXTRACTION
installation = IfcEnvironmentalImpactCategoryEnum.INSTALLATION
manufacture = IfcEnvironmentalImpactCategoryEnum.MANUFACTURE
transportation = IfcEnvironmentalImpactCategoryEnum.TRANSPORTATION
userdefined = IfcEnvironmentalImpactCategoryEnum.USERDEFINED
notdefined = IfcEnvironmentalImpactCategoryEnum.NOTDEFINED
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
directexpansionshellandtube = IfcEvaporatorTypeEnum.DIRECTEXPANSIONSHELLANDTUBE
directexpansiontubeintube = IfcEvaporatorTypeEnum.DIRECTEXPANSIONTUBEINTUBE
directexpansionbrazedplate = IfcEvaporatorTypeEnum.DIRECTEXPANSIONBRAZEDPLATE
floodedshellandtube = IfcEvaporatorTypeEnum.FLOODEDSHELLANDTUBE
shellandcoil = IfcEvaporatorTypeEnum.SHELLANDCOIL
userdefined = IfcEvaporatorTypeEnum.USERDEFINED
notdefined = IfcEvaporatorTypeEnum.NOTDEFINED
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
IfcFilterTypeEnum = enum_namespace()
airparticlefilter = IfcFilterTypeEnum.AIRPARTICLEFILTER
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
electricmeter = IfcFlowMeterTypeEnum.ELECTRICMETER
energymeter = IfcFlowMeterTypeEnum.ENERGYMETER
flowmeter = IfcFlowMeterTypeEnum.FLOWMETER
gasmeter = IfcFlowMeterTypeEnum.GASMETER
oilmeter = IfcFlowMeterTypeEnum.OILMETER
watermeter = IfcFlowMeterTypeEnum.WATERMETER
userdefined = IfcFlowMeterTypeEnum.USERDEFINED
notdefined = IfcFlowMeterTypeEnum.NOTDEFINED
IfcFootingTypeEnum = enum_namespace()
footing_beam = IfcFootingTypeEnum.FOOTING_BEAM
pad_footing = IfcFootingTypeEnum.PAD_FOOTING
pile_cap = IfcFootingTypeEnum.PILE_CAP
strip_footing = IfcFootingTypeEnum.STRIP_FOOTING
userdefined = IfcFootingTypeEnum.USERDEFINED
notdefined = IfcFootingTypeEnum.NOTDEFINED
IfcGasTerminalTypeEnum = enum_namespace()
gasappliance = IfcGasTerminalTypeEnum.GASAPPLIANCE
gasbooster = IfcGasTerminalTypeEnum.GASBOOSTER
gasburner = IfcGasTerminalTypeEnum.GASBURNER
userdefined = IfcGasTerminalTypeEnum.USERDEFINED
notdefined = IfcGasTerminalTypeEnum.NOTDEFINED
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
IfcInternalOrExternalEnum = enum_namespace()
internal = IfcInternalOrExternalEnum.INTERNAL
external = IfcInternalOrExternalEnum.EXTERNAL
notdefined = IfcInternalOrExternalEnum.NOTDEFINED
IfcInventoryTypeEnum = enum_namespace()
assetinventory = IfcInventoryTypeEnum.ASSETINVENTORY
spaceinventory = IfcInventoryTypeEnum.SPACEINVENTORY
furnitureinventory = IfcInventoryTypeEnum.FURNITUREINVENTORY
userdefined = IfcInventoryTypeEnum.USERDEFINED
notdefined = IfcInventoryTypeEnum.NOTDEFINED
IfcJunctionBoxTypeEnum = enum_namespace()
userdefined = IfcJunctionBoxTypeEnum.USERDEFINED
notdefined = IfcJunctionBoxTypeEnum.NOTDEFINED
IfcLampTypeEnum = enum_namespace()
compactfluorescent = IfcLampTypeEnum.COMPACTFLUORESCENT
fluorescent = IfcLampTypeEnum.FLUORESCENT
highpressuremercury = IfcLampTypeEnum.HIGHPRESSUREMERCURY
highpressuresodium = IfcLampTypeEnum.HIGHPRESSURESODIUM
metalhalide = IfcLampTypeEnum.METALHALIDE
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
userdefined = IfcLightFixtureTypeEnum.USERDEFINED
notdefined = IfcLightFixtureTypeEnum.NOTDEFINED
IfcLoadGroupTypeEnum = enum_namespace()
load_group = IfcLoadGroupTypeEnum.LOAD_GROUP
load_case = IfcLoadGroupTypeEnum.LOAD_CASE
load_combination_group = IfcLoadGroupTypeEnum.LOAD_COMBINATION_GROUP
load_combination = IfcLoadGroupTypeEnum.LOAD_COMBINATION
userdefined = IfcLoadGroupTypeEnum.USERDEFINED
notdefined = IfcLoadGroupTypeEnum.NOTDEFINED
IfcLogicalOperatorEnum = enum_namespace()
logicaland = IfcLogicalOperatorEnum.LOGICALAND
logicalor = IfcLogicalOperatorEnum.LOGICALOR
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
designintent = IfcObjectiveEnum.DESIGNINTENT
healthandsafety = IfcObjectiveEnum.HEALTHANDSAFETY
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
IfcOutletTypeEnum = enum_namespace()
audiovisualoutlet = IfcOutletTypeEnum.AUDIOVISUALOUTLET
communicationsoutlet = IfcOutletTypeEnum.COMMUNICATIONSOUTLET
poweroutlet = IfcOutletTypeEnum.POWEROUTLET
userdefined = IfcOutletTypeEnum.USERDEFINED
notdefined = IfcOutletTypeEnum.NOTDEFINED
IfcPermeableCoveringOperationEnum = enum_namespace()
grill = IfcPermeableCoveringOperationEnum.GRILL
louver = IfcPermeableCoveringOperationEnum.LOUVER
screen = IfcPermeableCoveringOperationEnum.SCREEN
userdefined = IfcPermeableCoveringOperationEnum.USERDEFINED
notdefined = IfcPermeableCoveringOperationEnum.NOTDEFINED
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
flexiblesegment = IfcPipeSegmentTypeEnum.FLEXIBLESEGMENT
rigidsegment = IfcPipeSegmentTypeEnum.RIGIDSEGMENT
gutter = IfcPipeSegmentTypeEnum.GUTTER
spool = IfcPipeSegmentTypeEnum.SPOOL
userdefined = IfcPipeSegmentTypeEnum.USERDEFINED
notdefined = IfcPipeSegmentTypeEnum.NOTDEFINED
IfcPlateTypeEnum = enum_namespace()
curtain_panel = IfcPlateTypeEnum.CURTAIN_PANEL
sheet = IfcPlateTypeEnum.SHEET
userdefined = IfcPlateTypeEnum.USERDEFINED
notdefined = IfcPlateTypeEnum.NOTDEFINED
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
IfcProjectOrderRecordTypeEnum = enum_namespace()
change = IfcProjectOrderRecordTypeEnum.CHANGE
maintenance = IfcProjectOrderRecordTypeEnum.MAINTENANCE
move = IfcProjectOrderRecordTypeEnum.MOVE
purchase = IfcProjectOrderRecordTypeEnum.PURCHASE
work = IfcProjectOrderRecordTypeEnum.WORK
userdefined = IfcProjectOrderRecordTypeEnum.USERDEFINED
notdefined = IfcProjectOrderRecordTypeEnum.NOTDEFINED
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
IfcPropertySourceEnum = enum_namespace()
design = IfcPropertySourceEnum.DESIGN
designmaximum = IfcPropertySourceEnum.DESIGNMAXIMUM
designminimum = IfcPropertySourceEnum.DESIGNMINIMUM
simulated = IfcPropertySourceEnum.SIMULATED
asbuilt = IfcPropertySourceEnum.ASBUILT
commissioning = IfcPropertySourceEnum.COMMISSIONING
measured = IfcPropertySourceEnum.MEASURED
userdefined = IfcPropertySourceEnum.USERDEFINED
notknown = IfcPropertySourceEnum.NOTKNOWN
IfcProtectiveDeviceTypeEnum = enum_namespace()
fusedisconnector = IfcProtectiveDeviceTypeEnum.FUSEDISCONNECTOR
circuitbreaker = IfcProtectiveDeviceTypeEnum.CIRCUITBREAKER
earthfailuredevice = IfcProtectiveDeviceTypeEnum.EARTHFAILUREDEVICE
residualcurrentcircuitbreaker = IfcProtectiveDeviceTypeEnum.RESIDUALCURRENTCIRCUITBREAKER
residualcurrentswitch = IfcProtectiveDeviceTypeEnum.RESIDUALCURRENTSWITCH
varistor = IfcProtectiveDeviceTypeEnum.VARISTOR
userdefined = IfcProtectiveDeviceTypeEnum.USERDEFINED
notdefined = IfcProtectiveDeviceTypeEnum.NOTDEFINED
IfcPumpTypeEnum = enum_namespace()
circulator = IfcPumpTypeEnum.CIRCULATOR
endsuction = IfcPumpTypeEnum.ENDSUCTION
splitcase = IfcPumpTypeEnum.SPLITCASE
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
userdefined = IfcReinforcingBarRoleEnum.USERDEFINED
notdefined = IfcReinforcingBarRoleEnum.NOTDEFINED
IfcReinforcingBarSurfaceEnum = enum_namespace()
plain = IfcReinforcingBarSurfaceEnum.PLAIN
textured = IfcReinforcingBarSurfaceEnum.TEXTURED
IfcResourceConsumptionEnum = enum_namespace()
consumed = IfcResourceConsumptionEnum.CONSUMED
partiallyconsumed = IfcResourceConsumptionEnum.PARTIALLYCONSUMED
notconsumed = IfcResourceConsumptionEnum.NOTCONSUMED
occupied = IfcResourceConsumptionEnum.OCCUPIED
partiallyoccupied = IfcResourceConsumptionEnum.PARTIALLYOCCUPIED
notoccupied = IfcResourceConsumptionEnum.NOTOCCUPIED
userdefined = IfcResourceConsumptionEnum.USERDEFINED
notdefined = IfcResourceConsumptionEnum.NOTDEFINED
IfcRibPlateDirectionEnum = enum_namespace()
direction_x = IfcRibPlateDirectionEnum.DIRECTION_X
direction_y = IfcRibPlateDirectionEnum.DIRECTION_Y
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
comissioningengineer = IfcRoleEnum.COMISSIONINGENGINEER
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
co2sensor = IfcSensorTypeEnum.CO2SENSOR
firesensor = IfcSensorTypeEnum.FIRESENSOR
flowsensor = IfcSensorTypeEnum.FLOWSENSOR
gassensor = IfcSensorTypeEnum.GASSENSOR
heatsensor = IfcSensorTypeEnum.HEATSENSOR
humiditysensor = IfcSensorTypeEnum.HUMIDITYSENSOR
lightsensor = IfcSensorTypeEnum.LIGHTSENSOR
moisturesensor = IfcSensorTypeEnum.MOISTURESENSOR
movementsensor = IfcSensorTypeEnum.MOVEMENTSENSOR
pressuresensor = IfcSensorTypeEnum.PRESSURESENSOR
smokesensor = IfcSensorTypeEnum.SMOKESENSOR
soundsensor = IfcSensorTypeEnum.SOUNDSENSOR
temperaturesensor = IfcSensorTypeEnum.TEMPERATURESENSOR
userdefined = IfcSensorTypeEnum.USERDEFINED
notdefined = IfcSensorTypeEnum.NOTDEFINED
IfcSequenceEnum = enum_namespace()
start_start = IfcSequenceEnum.START_START
start_finish = IfcSequenceEnum.START_FINISH
finish_start = IfcSequenceEnum.FINISH_START
finish_finish = IfcSequenceEnum.FINISH_FINISH
notdefined = IfcSequenceEnum.NOTDEFINED
IfcServiceLifeFactorTypeEnum = enum_namespace()
a_qualityofcomponents = IfcServiceLifeFactorTypeEnum.A_QUALITYOFCOMPONENTS
b_designlevel = IfcServiceLifeFactorTypeEnum.B_DESIGNLEVEL
c_workexecutionlevel = IfcServiceLifeFactorTypeEnum.C_WORKEXECUTIONLEVEL
d_indoorenvironment = IfcServiceLifeFactorTypeEnum.D_INDOORENVIRONMENT
e_outdoorenvironment = IfcServiceLifeFactorTypeEnum.E_OUTDOORENVIRONMENT
f_inuseconditions = IfcServiceLifeFactorTypeEnum.F_INUSECONDITIONS
g_maintenancelevel = IfcServiceLifeFactorTypeEnum.G_MAINTENANCELEVEL
userdefined = IfcServiceLifeFactorTypeEnum.USERDEFINED
notdefined = IfcServiceLifeFactorTypeEnum.NOTDEFINED
IfcServiceLifeTypeEnum = enum_namespace()
actualservicelife = IfcServiceLifeTypeEnum.ACTUALSERVICELIFE
expectedservicelife = IfcServiceLifeTypeEnum.EXPECTEDSERVICELIFE
optimisticreferenceservicelife = IfcServiceLifeTypeEnum.OPTIMISTICREFERENCESERVICELIFE
pessimisticreferenceservicelife = IfcServiceLifeTypeEnum.PESSIMISTICREFERENCESERVICELIFE
referenceservicelife = IfcServiceLifeTypeEnum.REFERENCESERVICELIFE
IfcSlabTypeEnum = enum_namespace()
floor = IfcSlabTypeEnum.FLOOR
roof = IfcSlabTypeEnum.ROOF
landing = IfcSlabTypeEnum.LANDING
baseslab = IfcSlabTypeEnum.BASESLAB
userdefined = IfcSlabTypeEnum.USERDEFINED
notdefined = IfcSlabTypeEnum.NOTDEFINED
IfcSoundScaleEnum = enum_namespace()
dba = IfcSoundScaleEnum.DBA
dbb = IfcSoundScaleEnum.DBB
dbc = IfcSoundScaleEnum.DBC
nc = IfcSoundScaleEnum.NC
nr = IfcSoundScaleEnum.NR
userdefined = IfcSoundScaleEnum.USERDEFINED
notdefined = IfcSoundScaleEnum.NOTDEFINED
IfcSpaceHeaterTypeEnum = enum_namespace()
sectionalradiator = IfcSpaceHeaterTypeEnum.SECTIONALRADIATOR
panelradiator = IfcSpaceHeaterTypeEnum.PANELRADIATOR
tubularradiator = IfcSpaceHeaterTypeEnum.TUBULARRADIATOR
convector = IfcSpaceHeaterTypeEnum.CONVECTOR
baseboardheater = IfcSpaceHeaterTypeEnum.BASEBOARDHEATER
finnedtubeunit = IfcSpaceHeaterTypeEnum.FINNEDTUBEUNIT
unitheater = IfcSpaceHeaterTypeEnum.UNITHEATER
userdefined = IfcSpaceHeaterTypeEnum.USERDEFINED
notdefined = IfcSpaceHeaterTypeEnum.NOTDEFINED
IfcSpaceTypeEnum = enum_namespace()
userdefined = IfcSpaceTypeEnum.USERDEFINED
notdefined = IfcSpaceTypeEnum.NOTDEFINED
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
IfcStructuralCurveTypeEnum = enum_namespace()
rigid_joined_member = IfcStructuralCurveTypeEnum.RIGID_JOINED_MEMBER
pin_joined_member = IfcStructuralCurveTypeEnum.PIN_JOINED_MEMBER
cable = IfcStructuralCurveTypeEnum.CABLE
tension_member = IfcStructuralCurveTypeEnum.TENSION_MEMBER
compression_member = IfcStructuralCurveTypeEnum.COMPRESSION_MEMBER
userdefined = IfcStructuralCurveTypeEnum.USERDEFINED
notdefined = IfcStructuralCurveTypeEnum.NOTDEFINED
IfcStructuralSurfaceTypeEnum = enum_namespace()
bending_element = IfcStructuralSurfaceTypeEnum.BENDING_ELEMENT
membrane_element = IfcStructuralSurfaceTypeEnum.MEMBRANE_ELEMENT
shell = IfcStructuralSurfaceTypeEnum.SHELL
userdefined = IfcStructuralSurfaceTypeEnum.USERDEFINED
notdefined = IfcStructuralSurfaceTypeEnum.NOTDEFINED
IfcSurfaceSide = enum_namespace()
positive = IfcSurfaceSide.POSITIVE
negative = IfcSurfaceSide.NEGATIVE
both = IfcSurfaceSide.BOTH
IfcSurfaceTextureEnum = enum_namespace()
bump = IfcSurfaceTextureEnum.BUMP
opacity = IfcSurfaceTextureEnum.OPACITY
reflection = IfcSurfaceTextureEnum.REFLECTION
selfillumination = IfcSurfaceTextureEnum.SELFILLUMINATION
shininess = IfcSurfaceTextureEnum.SHININESS
specular = IfcSurfaceTextureEnum.SPECULAR
texture = IfcSurfaceTextureEnum.TEXTURE
transparencymap = IfcSurfaceTextureEnum.TRANSPARENCYMAP
notdefined = IfcSurfaceTextureEnum.NOTDEFINED
IfcSwitchingDeviceTypeEnum = enum_namespace()
contactor = IfcSwitchingDeviceTypeEnum.CONTACTOR
emergencystop = IfcSwitchingDeviceTypeEnum.EMERGENCYSTOP
starter = IfcSwitchingDeviceTypeEnum.STARTER
switchdisconnector = IfcSwitchingDeviceTypeEnum.SWITCHDISCONNECTOR
toggleswitch = IfcSwitchingDeviceTypeEnum.TOGGLESWITCH
userdefined = IfcSwitchingDeviceTypeEnum.USERDEFINED
notdefined = IfcSwitchingDeviceTypeEnum.NOTDEFINED
IfcTankTypeEnum = enum_namespace()
preformed = IfcTankTypeEnum.PREFORMED
sectional = IfcTankTypeEnum.SECTIONAL
expansion = IfcTankTypeEnum.EXPANSION
pressurevessel = IfcTankTypeEnum.PRESSUREVESSEL
userdefined = IfcTankTypeEnum.USERDEFINED
notdefined = IfcTankTypeEnum.NOTDEFINED
IfcTendonTypeEnum = enum_namespace()
strand = IfcTendonTypeEnum.STRAND
wire = IfcTendonTypeEnum.WIRE
bar = IfcTendonTypeEnum.BAR
coated = IfcTendonTypeEnum.COATED
userdefined = IfcTendonTypeEnum.USERDEFINED
notdefined = IfcTendonTypeEnum.NOTDEFINED
IfcTextPath = enum_namespace()
left = IfcTextPath.LEFT
right = IfcTextPath.RIGHT
up = IfcTextPath.UP
down = IfcTextPath.DOWN
IfcThermalLoadSourceEnum = enum_namespace()
people = IfcThermalLoadSourceEnum.PEOPLE
lighting = IfcThermalLoadSourceEnum.LIGHTING
equipment = IfcThermalLoadSourceEnum.EQUIPMENT
ventilationindoorair = IfcThermalLoadSourceEnum.VENTILATIONINDOORAIR
ventilationoutsideair = IfcThermalLoadSourceEnum.VENTILATIONOUTSIDEAIR
recirculatedair = IfcThermalLoadSourceEnum.RECIRCULATEDAIR
exhaustair = IfcThermalLoadSourceEnum.EXHAUSTAIR
airexchangerate = IfcThermalLoadSourceEnum.AIREXCHANGERATE
drybulbtemperature = IfcThermalLoadSourceEnum.DRYBULBTEMPERATURE
relativehumidity = IfcThermalLoadSourceEnum.RELATIVEHUMIDITY
infiltration = IfcThermalLoadSourceEnum.INFILTRATION
userdefined = IfcThermalLoadSourceEnum.USERDEFINED
notdefined = IfcThermalLoadSourceEnum.NOTDEFINED
IfcThermalLoadTypeEnum = enum_namespace()
sensible = IfcThermalLoadTypeEnum.SENSIBLE
latent = IfcThermalLoadTypeEnum.LATENT
radiant = IfcThermalLoadTypeEnum.RADIANT
notdefined = IfcThermalLoadTypeEnum.NOTDEFINED
IfcTimeSeriesDataTypeEnum = enum_namespace()
continuous = IfcTimeSeriesDataTypeEnum.CONTINUOUS
discrete = IfcTimeSeriesDataTypeEnum.DISCRETE
discretebinary = IfcTimeSeriesDataTypeEnum.DISCRETEBINARY
piecewisebinary = IfcTimeSeriesDataTypeEnum.PIECEWISEBINARY
piecewiseconstant = IfcTimeSeriesDataTypeEnum.PIECEWISECONSTANT
piecewisecontinuous = IfcTimeSeriesDataTypeEnum.PIECEWISECONTINUOUS
notdefined = IfcTimeSeriesDataTypeEnum.NOTDEFINED
IfcTimeSeriesScheduleTypeEnum = enum_namespace()
annual = IfcTimeSeriesScheduleTypeEnum.ANNUAL
monthly = IfcTimeSeriesScheduleTypeEnum.MONTHLY
weekly = IfcTimeSeriesScheduleTypeEnum.WEEKLY
daily = IfcTimeSeriesScheduleTypeEnum.DAILY
userdefined = IfcTimeSeriesScheduleTypeEnum.USERDEFINED
notdefined = IfcTimeSeriesScheduleTypeEnum.NOTDEFINED
IfcTransformerTypeEnum = enum_namespace()
current = IfcTransformerTypeEnum.CURRENT
frequency = IfcTransformerTypeEnum.FREQUENCY
voltage = IfcTransformerTypeEnum.VOLTAGE
userdefined = IfcTransformerTypeEnum.USERDEFINED
notdefined = IfcTransformerTypeEnum.NOTDEFINED
IfcTransitionCode = enum_namespace()
discontinuous = IfcTransitionCode.DISCONTINUOUS
continuous = IfcTransitionCode.CONTINUOUS
contsamegradient = IfcTransitionCode.CONTSAMEGRADIENT
contsamegradientsamecurvature = IfcTransitionCode.CONTSAMEGRADIENTSAMECURVATURE
IfcTransportElementTypeEnum = enum_namespace()
elevator = IfcTransportElementTypeEnum.ELEVATOR
escalator = IfcTransportElementTypeEnum.ESCALATOR
movingwalkway = IfcTransportElementTypeEnum.MOVINGWALKWAY
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
IfcUnitaryEquipmentTypeEnum = enum_namespace()
airhandler = IfcUnitaryEquipmentTypeEnum.AIRHANDLER
airconditioningunit = IfcUnitaryEquipmentTypeEnum.AIRCONDITIONINGUNIT
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
IfcVibrationIsolatorTypeEnum = enum_namespace()
compression = IfcVibrationIsolatorTypeEnum.COMPRESSION
spring = IfcVibrationIsolatorTypeEnum.SPRING
userdefined = IfcVibrationIsolatorTypeEnum.USERDEFINED
notdefined = IfcVibrationIsolatorTypeEnum.NOTDEFINED
IfcWallTypeEnum = enum_namespace()
standard = IfcWallTypeEnum.STANDARD
polygonal = IfcWallTypeEnum.POLYGONAL
shear = IfcWallTypeEnum.SHEAR
elementedwall = IfcWallTypeEnum.ELEMENTEDWALL
plumbingwall = IfcWallTypeEnum.PLUMBINGWALL
userdefined = IfcWallTypeEnum.USERDEFINED
notdefined = IfcWallTypeEnum.NOTDEFINED
IfcWasteTerminalTypeEnum = enum_namespace()
floortrap = IfcWasteTerminalTypeEnum.FLOORTRAP
floorwaste = IfcWasteTerminalTypeEnum.FLOORWASTE
gullysump = IfcWasteTerminalTypeEnum.GULLYSUMP
gullytrap = IfcWasteTerminalTypeEnum.GULLYTRAP
greaseinterceptor = IfcWasteTerminalTypeEnum.GREASEINTERCEPTOR
oilinterceptor = IfcWasteTerminalTypeEnum.OILINTERCEPTOR
petrolinterceptor = IfcWasteTerminalTypeEnum.PETROLINTERCEPTOR
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
IfcWorkControlTypeEnum = enum_namespace()
actual = IfcWorkControlTypeEnum.ACTUAL
baseline = IfcWorkControlTypeEnum.BASELINE
planned = IfcWorkControlTypeEnum.PLANNED
userdefined = IfcWorkControlTypeEnum.USERDEFINED
notdefined = IfcWorkControlTypeEnum.NOTDEFINED

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
        assert (express_getattr(self, 'lower', INDETERMINATE)() in ['top-left', 'top-middle', 'top-right', 'middle-left', 'center', 'middle-right', 'bottom-left', 'bottom-middle', 'bottom-right']) is not False

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

class Ifc2DCompositeCurve_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'Ifc2DCompositeCurve'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert express_getattr(self, 'ClosedCurve', INDETERMINATE) is not False

class Ifc2DCompositeCurve_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'Ifc2DCompositeCurve'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        assert (express_getattr(self, 'Dim', INDETERMINATE) == 2) is not False

class IfcActorRole_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcActorRole'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        role = express_getattr(self, 'Role', INDETERMINATE)
        assert (role != express_getattr(IfcRoleEnum, 'USERDEFINED', INDETERMINATE) or (role == express_getattr(IfcRoleEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'UserDefinedRole', INDETERMINATE)))) is not False

class IfcAddress_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAddress'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        purpose = express_getattr(self, 'Purpose', INDETERMINATE)
        assert (not exists(purpose) or (purpose != express_getattr(IfcAddressTypeEnum, 'USERDEFINED', INDETERMINATE) or (purpose == express_getattr(IfcAddressTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'UserDefinedPurpose', INDETERMINATE))))) is not False

class IfcAirTerminalBoxType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAirTerminalBoxType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcAirTerminalBoxTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcAirTerminalBoxTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcAirTerminalType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAirTerminalType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcAirTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcAirTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcAirToAirHeatRecoveryType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAirToAirHeatRecoveryType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcAirToAirHeatRecoveryTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcAirToAirHeatRecoveryTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcAnnotationCurveOccurrence_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAnnotationCurveOccurrence'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert (not exists(express_getattr(self, 'Item', INDETERMINATE)) or 'ifc2x3.ifccurve' in typeof(express_getattr(self, 'Item', INDETERMINATE))) is not False

class IfcAnnotationFillAreaOccurrence_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAnnotationFillAreaOccurrence'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert (not exists(express_getattr(self, 'Item', INDETERMINATE)) or 'ifc2x3.ifcannotationfillarea' in typeof(express_getattr(self, 'Item', INDETERMINATE))) is not False

class IfcAnnotationSurface_WR01:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAnnotationSurface'
    RULE_NAME = 'WR01'

    @staticmethod
    def __call__(self):
        item = express_getattr(self, 'Item', INDETERMINATE)
        assert (sizeof(['ifc2x3.ifcsurface', 'ifc2x3.ifcshellbasedsurfacemodel', 'ifc2x3.ifcfacebasedsurfacemodel', 'ifc2x3.ifcsolidmodel', 'ifc2x3.ifcbooleanresult', 'ifc2x3.ifccsgprimitive3d'] * typeof(item)) >= 1) is not False

class IfcAnnotationSurfaceOccurrence_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAnnotationSurfaceOccurrence'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert (not exists(express_getattr(self, 'Item', INDETERMINATE)) or sizeof(['ifc2x3.ifcsurface', 'ifc2x3.ifcfacebasedsurfacemodel', 'ifc2x3.ifcshellbasedsurfacemodel', 'ifc2x3.ifcsolidmodel'] * typeof(express_getattr(self, 'Item', INDETERMINATE))) > 0) is not False

class IfcAnnotationSymbolOccurrence_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAnnotationSymbolOccurrence'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert (not exists(express_getattr(self, 'Item', INDETERMINATE)) or 'ifc2x3.ifcdefinedsymbol' in typeof(express_getattr(self, 'Item', INDETERMINATE))) is not False

class IfcAnnotationTextOccurrence_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAnnotationTextOccurrence'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert (not exists(express_getattr(self, 'Item', INDETERMINATE)) or 'ifc2x3.ifctextliteral' in typeof(express_getattr(self, 'Item', INDETERMINATE))) is not False

class IfcAppliedValue_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAppliedValue'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        appliedvalue = express_getattr(self, 'AppliedValue', INDETERMINATE)
        valueofcomponents = express_getattr(self, 'ValueOfComponents', INDETERMINATE)
        assert (exists(appliedvalue) or exists(valueofcomponents)) is not False

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
        assert (not 'ifc2x3.ifcline' in typeof(outercurve)) is not False

class IfcArbitraryClosedProfileDef_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcArbitraryClosedProfileDef'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        outercurve = express_getattr(self, 'OuterCurve', INDETERMINATE)
        assert (not 'ifc2x3.ifcoffsetcurve2d' in typeof(outercurve)) is not False

class IfcArbitraryOpenProfileDef_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcArbitraryOpenProfileDef'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        assert ('ifc2x3.ifccenterlineprofiledef' in typeof(self) or express_getattr(self, 'ProfileType', INDETERMINATE) == express_getattr(IfcProfileTypeEnum, 'CURVE', INDETERMINATE)) is not False

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
        assert (sizeof([temp for temp in innercurves if 'ifc2x3.ifcline' in typeof(temp)]) == 0) is not False

class IfcAsset_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAsset'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in express_getattr(express_getattr(self, 'IsGroupedBy', INDETERMINATE), 'RelatedObjects', INDETERMINATE) if not 'ifc2x3.ifcelement' in typeof(temp)]) == 0) is not False

class IfcAxis1Placement_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis1Placement'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        axis = express_getattr(self, 'Axis', INDETERMINATE)
        assert (not exists(axis) or express_getattr(axis, 'Dim', INDETERMINATE) == 3) is not False

class IfcAxis1Placement_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis1Placement'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        assert (express_getattr(express_getattr(self, 'Location', INDETERMINATE), 'Dim', INDETERMINATE) == 3) is not False

def calc_IfcAxis1Placement_Z(self):
    axis = express_getattr(self, 'Axis', INDETERMINATE)
    return nvl(IfcNormalise(axis), IfcDirection(DirectionRatios=[0.0, 0.0, 1.0]))

class IfcAxis2Placement2D_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis2Placement2D'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        refdirection = express_getattr(self, 'RefDirection', INDETERMINATE)
        assert (not exists(refdirection) or express_getattr(refdirection, 'Dim', INDETERMINATE) == 2) is not False

class IfcAxis2Placement2D_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis2Placement2D'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        assert (express_getattr(express_getattr(self, 'Location', INDETERMINATE), 'Dim', INDETERMINATE) == 2) is not False

def calc_IfcAxis2Placement2D_P(self):
    refdirection = express_getattr(self, 'RefDirection', INDETERMINATE)
    return IfcBuild2Axes(refdirection)

class IfcAxis2Placement3D_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis2Placement3D'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (express_getattr(express_getattr(self, 'Location', INDETERMINATE), 'Dim', INDETERMINATE) == 3) is not False

class IfcAxis2Placement3D_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis2Placement3D'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        axis = express_getattr(self, 'Axis', INDETERMINATE)
        assert (not exists(axis) or express_getattr(axis, 'Dim', INDETERMINATE) == 3) is not False

class IfcAxis2Placement3D_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis2Placement3D'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        refdirection = express_getattr(self, 'RefDirection', INDETERMINATE)
        assert (not exists(refdirection) or express_getattr(refdirection, 'Dim', INDETERMINATE) == 3) is not False

class IfcAxis2Placement3D_WR4:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis2Placement3D'
    RULE_NAME = 'WR4'

    @staticmethod
    def __call__(self):
        axis = express_getattr(self, 'Axis', INDETERMINATE)
        refdirection = express_getattr(self, 'RefDirection', INDETERMINATE)
        assert (not exists(axis) or not exists(refdirection) or express_getattr(IfcCrossProduct(axis, refdirection), 'Magnitude', INDETERMINATE) > 0.0) is not False

class IfcAxis2Placement3D_WR5:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcAxis2Placement3D'
    RULE_NAME = 'WR5'

    @staticmethod
    def __call__(self):
        axis = express_getattr(self, 'Axis', INDETERMINATE)
        refdirection = express_getattr(self, 'RefDirection', INDETERMINATE)
        assert (not exists(axis) ^ exists(refdirection)) is not False

def calc_IfcAxis2Placement3D_P(self):
    axis = express_getattr(self, 'Axis', INDETERMINATE)
    refdirection = express_getattr(self, 'RefDirection', INDETERMINATE)
    return IfcBuildAxes(axis, refdirection)

class IfcBSplineCurve_WR41:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBSplineCurve'
    RULE_NAME = 'WR41'

    @staticmethod
    def __call__(self):
        controlpointslist = express_getattr(self, 'ControlPointsList', INDETERMINATE)
        assert (sizeof([temp for temp in controlpointslist if express_getattr(temp, 'Dim', INDETERMINATE) != express_getattr(express_getitem(controlpointslist, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)]) == 0) is not False

def calc_IfcBSplineCurve_ControlPoints(self):
    controlpointslist = express_getattr(self, 'ControlPointsList', INDETERMINATE)
    upperindexoncontrolpoints = express_getattr(self, 'UpperIndexOnControlPoints', INDETERMINATE)
    return IfcListToArray(controlpointslist, 0, upperindexoncontrolpoints)

def calc_IfcBSplineCurve_UpperIndexOnControlPoints(self):
    controlpointslist = express_getattr(self, 'ControlPointsList', INDETERMINATE)
    return sizeof(controlpointslist) - 1

class IfcBlobTexture_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBlobTexture'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        assert (express_getattr(express_getattr(self, 'RasterFormat', INDETERMINATE), 'lower', INDETERMINATE)() in ['bmp', 'jpg', 'gif', 'png']) is not False

class IfcBoilerType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBoilerType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcBoilerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcBoilerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcBooleanClippingResult_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBooleanClippingResult'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        firstoperand = express_getattr(self, 'FirstOperand', INDETERMINATE)
        assert ('ifc2x3.ifcsweptareasolid' in typeof(firstoperand) or 'ifc2x3.ifcbooleanclippingresult' in typeof(firstoperand)) is not False

class IfcBooleanClippingResult_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBooleanClippingResult'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        secondoperand = express_getattr(self, 'SecondOperand', INDETERMINATE)
        assert ('ifc2x3.ifchalfspacesolid' in typeof(secondoperand)) is not False

class IfcBooleanClippingResult_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBooleanClippingResult'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        operator = express_getattr(self, 'Operator', INDETERMINATE)
        assert (operator == difference) is not False

class IfcBooleanResult_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBooleanResult'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        firstoperand = express_getattr(self, 'FirstOperand', INDETERMINATE)
        secondoperand = express_getattr(self, 'SecondOperand', INDETERMINATE)
        assert (express_getattr(firstoperand, 'Dim', INDETERMINATE) == express_getattr(secondoperand, 'Dim', INDETERMINATE)) is not False

def calc_IfcBooleanResult_Dim(self):
    firstoperand = express_getattr(self, 'FirstOperand', INDETERMINATE)
    return express_getattr(firstoperand, 'Dim', INDETERMINATE)

def calc_IfcBoundingBox_Dim(self):
    return 3

class IfcBoxedHalfSpace_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBoxedHalfSpace'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (not 'ifc2x3.ifccurveboundedplane' in typeof(express_getattr(self, 'BaseSurface', INDETERMINATE))) is not False

class IfcBuildingElementProxy_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcBuildingElementProxy'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert exists(express_getattr(self, 'Name', INDETERMINATE)) is not False

class IfcCShapeProfileDef_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCShapeProfileDef'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        depth = express_getattr(self, 'Depth', INDETERMINATE)
        girth = express_getattr(self, 'Girth', INDETERMINATE)
        assert (girth < depth / 2.0) is not False

class IfcCShapeProfileDef_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCShapeProfileDef'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        depth = express_getattr(self, 'Depth', INDETERMINATE)
        width = express_getattr(self, 'Width', INDETERMINATE)
        internalfilletradius = express_getattr(self, 'InternalFilletRadius', INDETERMINATE)
        assert (not exists(internalfilletradius) or (internalfilletradius <= width / 2.0 and internalfilletradius <= depth / 2.0)) is not False

class IfcCShapeProfileDef_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCShapeProfileDef'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        depth = express_getattr(self, 'Depth', INDETERMINATE)
        width = express_getattr(self, 'Width', INDETERMINATE)
        wallthickness = express_getattr(self, 'WallThickness', INDETERMINATE)
        assert (wallthickness < width / 2.0 and wallthickness < depth / 2.0) is not False

class IfcCableCarrierFittingType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCableCarrierFittingType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcCableCarrierFittingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCableCarrierFittingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

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
        coordinates = express_getattr(self, 'Coordinates', INDETERMINATE)
        assert (hiindex(coordinates) >= 2) is not False

def calc_IfcCartesianPoint_Dim(self):
    coordinates = express_getattr(self, 'Coordinates', INDETERMINATE)
    return hiindex(coordinates)

class IfcCartesianTransformationOperator_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator'
    RULE_NAME = 'WR1'

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

class IfcCartesianTransformationOperator2D_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator2D'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (express_getattr(self, 'Dim', INDETERMINATE) == 2) is not False

class IfcCartesianTransformationOperator2D_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator2D'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        assert (not exists(express_getattr(self, 'Axis1', INDETERMINATE)) or express_getattr(express_getattr(self, 'Axis1', INDETERMINATE), 'Dim', INDETERMINATE) == 2) is not False

class IfcCartesianTransformationOperator2D_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator2D'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        assert (not exists(express_getattr(self, 'Axis2', INDETERMINATE)) or express_getattr(express_getattr(self, 'Axis2', INDETERMINATE), 'Dim', INDETERMINATE) == 2) is not False

def calc_IfcCartesianTransformationOperator2D_U(self):
    return IfcBaseAxis(2, express_getattr(self, 'Axis1', INDETERMINATE), express_getattr(self, 'Axis2', INDETERMINATE), None)

class IfcCartesianTransformationOperator2DnonUniform_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator2DnonUniform'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        scl2 = express_getattr(self, 'Scl2', INDETERMINATE)
        assert (scl2 > 0.0) is not False

def calc_IfcCartesianTransformationOperator2DnonUniform_Scl2(self):
    scale2 = express_getattr(self, 'Scale2', INDETERMINATE)
    return nvl(scale2, express_getattr(self, 'Scl', INDETERMINATE))

class IfcCartesianTransformationOperator3D_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator3D'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (express_getattr(self, 'Dim', INDETERMINATE) == 3) is not False

class IfcCartesianTransformationOperator3D_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator3D'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        assert (not exists(express_getattr(self, 'Axis1', INDETERMINATE)) or express_getattr(express_getattr(self, 'Axis1', INDETERMINATE), 'Dim', INDETERMINATE) == 3) is not False

class IfcCartesianTransformationOperator3D_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator3D'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        assert (not exists(express_getattr(self, 'Axis2', INDETERMINATE)) or express_getattr(express_getattr(self, 'Axis2', INDETERMINATE), 'Dim', INDETERMINATE) == 3) is not False

class IfcCartesianTransformationOperator3D_WR4:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator3D'
    RULE_NAME = 'WR4'

    @staticmethod
    def __call__(self):
        axis3 = express_getattr(self, 'Axis3', INDETERMINATE)
        assert (not exists(axis3) or express_getattr(axis3, 'Dim', INDETERMINATE) == 3) is not False

def calc_IfcCartesianTransformationOperator3D_U(self):
    axis3 = express_getattr(self, 'Axis3', INDETERMINATE)
    return IfcBaseAxis(3, express_getattr(self, 'Axis1', INDETERMINATE), express_getattr(self, 'Axis2', INDETERMINATE), axis3)

class IfcCartesianTransformationOperator3DnonUniform_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator3DnonUniform'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        scl2 = express_getattr(self, 'Scl2', INDETERMINATE)
        assert (scl2 > 0.0) is not False

class IfcCartesianTransformationOperator3DnonUniform_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCartesianTransformationOperator3DnonUniform'
    RULE_NAME = 'WR2'

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

class IfcChillerType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcChillerType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcChillerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcChillerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCircleHollowProfileDef_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCircleHollowProfileDef'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        wallthickness = express_getattr(self, 'WallThickness', INDETERMINATE)
        assert (wallthickness < express_getattr(self, 'Radius', INDETERMINATE)) is not False

class IfcCoilType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCoilType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcCoilTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCoilTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

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

class IfcCompositeCurve_WR41:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCompositeCurve'
    RULE_NAME = 'WR41'

    @staticmethod
    def __call__(self):
        segments = express_getattr(self, 'Segments', INDETERMINATE)
        closedcurve = express_getattr(self, 'ClosedCurve', INDETERMINATE)
        assert (not closedcurve and sizeof([temp for temp in segments if express_getattr(temp, 'Transition', INDETERMINATE) == discontinuous]) == 1 or (closedcurve and sizeof([temp for temp in segments if express_getattr(temp, 'Transition', INDETERMINATE) == discontinuous]) == 0)) is not False

class IfcCompositeCurve_WR42:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCompositeCurve'
    RULE_NAME = 'WR42'

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

class IfcCompositeCurveSegment_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCompositeCurveSegment'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        parentcurve = express_getattr(self, 'ParentCurve', INDETERMINATE)
        assert ('ifc2x3.ifcboundedcurve' in typeof(parentcurve)) is not False

def calc_IfcCompositeCurveSegment_Dim(self):
    parentcurve = express_getattr(self, 'ParentCurve', INDETERMINATE)
    return express_getattr(parentcurve, 'Dim', INDETERMINATE)

class IfcCompositeProfileDef_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCompositeProfileDef'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        profiles = express_getattr(self, 'Profiles', INDETERMINATE)
        assert (sizeof([temp for temp in profiles if express_getattr(temp, 'ProfileType', INDETERMINATE) != express_getattr(express_getitem(profiles, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'ProfileType', INDETERMINATE)]) == 0) is not False

class IfcCompositeProfileDef_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCompositeProfileDef'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        profiles = express_getattr(self, 'Profiles', INDETERMINATE)
        assert (sizeof([temp for temp in profiles if 'ifc2x3.ifccompositeprofiledef' in typeof(temp)]) == 0) is not False

class IfcCompressorType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCompressorType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcCompressorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCompressorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCondenserType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCondenserType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcCondenserTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCondenserTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcConditionCriterion_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConditionCriterion'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert exists(express_getattr(self, 'Name', INDETERMINATE)) is not False

class IfcConstraint_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConstraint'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        constraintgrade = express_getattr(self, 'ConstraintGrade', INDETERMINATE)
        assert (constraintgrade != express_getattr(IfcConstraintEnum, 'USERDEFINED', INDETERMINATE) or (constraintgrade == express_getattr(IfcConstraintEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'UserDefinedGrade', INDETERMINATE)))) is not False

class IfcConstraintAggregationRelationship_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConstraintAggregationRelationship'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        relatingconstraint = express_getattr(self, 'RelatingConstraint', INDETERMINATE)
        relatedconstraints = express_getattr(self, 'RelatedConstraints', INDETERMINATE)
        assert (sizeof([temp for temp in relatedconstraints if temp == relatingconstraint]) == 0) is not False

class IfcConstraintRelationship_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConstraintRelationship'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        relatingconstraint = express_getattr(self, 'RelatingConstraint', INDETERMINATE)
        relatedconstraints = express_getattr(self, 'RelatedConstraints', INDETERMINATE)
        assert (sizeof([temp for temp in relatedconstraints if temp == relatingconstraint]) == 0) is not False

class IfcConstructionMaterialResource_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConstructionMaterialResource'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (sizeof(express_getattr(self, 'ResourceOf', INDETERMINATE)) <= 1) is not False

class IfcConstructionMaterialResource_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConstructionMaterialResource'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        assert (not exists(lambda : express_getitem(express_getattr(self, 'ResourceOf', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) or express_getattr(express_getitem(express_getattr(self, 'ResourceOf', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatedObjectsType', INDETERMINATE) == express_getattr(IfcObjectTypeEnum, 'PRODUCT', INDETERMINATE)) is not False

class IfcConstructionProductResource_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConstructionProductResource'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (sizeof(express_getattr(self, 'ResourceOf', INDETERMINATE)) <= 1) is not False

class IfcConstructionProductResource_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcConstructionProductResource'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        assert (not exists(lambda : express_getitem(express_getattr(self, 'ResourceOf', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) or express_getattr(express_getitem(express_getattr(self, 'ResourceOf', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatedObjectsType', INDETERMINATE) == express_getattr(IfcObjectTypeEnum, 'PRODUCT', INDETERMINATE)) is not False

class IfcCooledBeamType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCooledBeamType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcCooledBeamTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCooledBeamTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCoolingTowerType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCoolingTowerType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcCoolingTowerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCoolingTowerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcCovering_WR61:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCovering'
    RULE_NAME = 'WR61'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcCoveringTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcCoveringTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

def calc_IfcCsgPrimitive3D_Dim(self):
    return 3

def calc_IfcCurve_Dim(self):
    return IfcCurveDim(self)

def calc_IfcCurveBoundedPlane_Dim(self):
    basissurface = express_getattr(self, 'BasisSurface', INDETERMINATE)
    return express_getattr(basissurface, 'Dim', INDETERMINATE)

class IfcCurveStyle_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCurveStyle'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        curvewidth = express_getattr(self, 'CurveWidth', INDETERMINATE)
        assert (not exists(curvewidth) or 'ifc2x3.ifcpositivelengthmeasure' in typeof(curvewidth) or ('ifc2x3.ifcdescriptivemeasure' in typeof(curvewidth) and curvewidth == 'bylayer')) is not False

class IfcCurveStyleFontPattern_WR01:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcCurveStyleFontPattern'
    RULE_NAME = 'WR01'

    @staticmethod
    def __call__(self):
        visiblesegmentlength = express_getattr(self, 'VisibleSegmentLength', INDETERMINATE)
        assert (visiblesegmentlength >= 0.0) is not False

class IfcDamperType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDamperType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcDamperTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcDamperTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcDerivedProfileDef_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDerivedProfileDef'
    RULE_NAME = 'WR1'

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

class IfcDimensionCalloutRelationship_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDimensionCalloutRelationship'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        assert (express_getattr(express_getattr(self, 'Name', INDETERMINATE), 'lower', INDETERMINATE)() in ['primary', 'secondary']) is not False

class IfcDimensionCalloutRelationship_WR12:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDimensionCalloutRelationship'
    RULE_NAME = 'WR12'

    @staticmethod
    def __call__(self):
        assert (sizeof(typeof(express_getattr(self, 'RelatingDraughtingCallout', INDETERMINATE)) * ['ifc2x3.ifcangulardimension', 'ifc2x3.ifcdiameterdimension', 'ifc2x3.ifclineardimension', 'ifc2x3.ifcradiusdimension']) == 1) is not False

class IfcDimensionCalloutRelationship_WR13:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDimensionCalloutRelationship'
    RULE_NAME = 'WR13'

    @staticmethod
    def __call__(self):
        assert (not 'ifc2x3.ifcdimensioncurvedirectedcallout' in typeof(express_getattr(self, 'RelatedDraughtingCallout', INDETERMINATE))) is not False

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
        assert (sizeof([dct1 for dct1 in usedin(self, 'ifc2x3.' + 'ifcterminatorsymbol.annotatedcurve') if express_getattr(dct1, 'Role', INDETERMINATE) == express_getattr(IfcDimensionExtentUsage, 'ORIGIN', INDETERMINATE)]) <= 1 and sizeof([dct2 for dct2 in usedin(self, 'ifc2x3.' + 'ifcterminatorsymbol.annotatedcurve') if express_getattr(dct2, 'Role', INDETERMINATE) == express_getattr(IfcDimensionExtentUsage, 'TARGET', INDETERMINATE)]) <= 1) is not False

class IfcDimensionCurve_WR53:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDimensionCurve'
    RULE_NAME = 'WR53'

    @staticmethod
    def __call__(self):
        annotatedbysymbols = express_getattr(self, 'AnnotatedBySymbols', INDETERMINATE)
        assert (sizeof([dct for dct in annotatedbysymbols if not 'ifc2x3.ifcdimensioncurveterminator' in typeof(dct)]) == 0) is not False

class IfcDimensionCurveDirectedCallout_WR41:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDimensionCurveDirectedCallout'
    RULE_NAME = 'WR41'

    @staticmethod
    def __call__(self):
        assert (sizeof([dc for dc in express_getattr(self, 'Contents', INDETERMINATE) if 'ifc2x3.ifcdimensioncurve' in typeof(dc)]) == 1) is not False

class IfcDimensionCurveDirectedCallout_WR42:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDimensionCurveDirectedCallout'
    RULE_NAME = 'WR42'

    @staticmethod
    def __call__(self):
        contents = express_getattr(self, 'Contents', INDETERMINATE)
        assert (sizeof([dc for dc in express_getattr(self, 'contents', INDETERMINATE) if 'ifc2x3.ifcprojectioncurve' in typeof(dc)]) <= 2) is not False

class IfcDimensionCurveTerminator_WR61:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDimensionCurveTerminator'
    RULE_NAME = 'WR61'

    @staticmethod
    def __call__(self):
        assert ('ifc2x3.ifcdimensioncurve' in typeof(express_getattr(self, 'AnnotatedCurve', INDETERMINATE))) is not False

class IfcDimensionPair_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDimensionPair'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        assert (express_getattr(express_getattr(self, 'Name', INDETERMINATE), 'lower', INDETERMINATE)() in ['chained', 'parallel']) is not False

class IfcDimensionPair_WR12:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDimensionPair'
    RULE_NAME = 'WR12'

    @staticmethod
    def __call__(self):
        assert (sizeof(typeof(express_getattr(self, 'RelatingDraughtingCallout', INDETERMINATE)) * ['ifc2x3.ifcangulardimension', 'ifc2x3.ifcdiameterdimension', 'ifc2x3.ifclineardimension', 'ifc2x3.ifcradiusdimension']) == 1) is not False

class IfcDimensionPair_WR13:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDimensionPair'
    RULE_NAME = 'WR13'

    @staticmethod
    def __call__(self):
        assert (sizeof(typeof(express_getattr(self, 'RelatedDraughtingCallout', INDETERMINATE)) * ['ifc2x3.ifcangulardimension', 'ifc2x3.ifcdiameterdimension', 'ifc2x3.ifclineardimension', 'ifc2x3.ifcradiusdimension']) == 1) is not False

def calc_IfcDirection_Dim(self):
    directionratios = express_getattr(self, 'DirectionRatios', INDETERMINATE)
    return hiindex(directionratios)

class IfcDocumentElectronicFormat_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDocumentElectronicFormat'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        fileextension = express_getattr(self, 'FileExtension', INDETERMINATE)
        mimecontenttype = express_getattr(self, 'MimeContentType', INDETERMINATE)
        assert (exists(fileextension) or exists(mimecontenttype)) is not False

class IfcDocumentReference_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDocumentReference'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        name = express_getattr(self, 'Name', INDETERMINATE)
        referencetodocument = express_getattr(self, 'ReferenceToDocument', INDETERMINATE)
        assert exists(name) ^ exists(lambda : express_getitem(referencetodocument, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) is not False

class IfcDoorLiningProperties_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDoorLiningProperties'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        liningdepth = express_getattr(self, 'LiningDepth', INDETERMINATE)
        liningthickness = express_getattr(self, 'LiningThickness', INDETERMINATE)
        assert (not (not exists(liningdepth) and exists(liningthickness))) is not False

class IfcDoorLiningProperties_WR32:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDoorLiningProperties'
    RULE_NAME = 'WR32'

    @staticmethod
    def __call__(self):
        thresholddepth = express_getattr(self, 'ThresholdDepth', INDETERMINATE)
        thresholdthickness = express_getattr(self, 'ThresholdThickness', INDETERMINATE)
        assert (not (not exists(thresholddepth) and exists(thresholdthickness))) is not False

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
        assert (exists(lambda : express_getitem(express_getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and 'ifc2x3.ifcdoorstyle' in typeof(express_getitem(express_getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))) is not False

class IfcDoorPanelProperties_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDoorPanelProperties'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert (exists(lambda : express_getitem(express_getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and 'ifc2x3.ifcdoorstyle' in typeof(express_getitem(express_getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))) is not False

class IfcDraughtingPreDefinedColour_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDraughtingPreDefinedColour'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert (express_getattr(express_getattr(self, 'Name', INDETERMINATE), 'lower', INDETERMINATE)() in ['black', 'red', 'green', 'blue', 'yellow', 'magenta', 'cyan', 'white', 'bylayer']) is not False

class IfcDraughtingPreDefinedCurveFont_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDraughtingPreDefinedCurveFont'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert (express_getattr(express_getattr(self, 'Name', INDETERMINATE), 'lower', INDETERMINATE)() in ['continuous', 'chain', 'chaindoubledash', 'dashed', 'dotted', 'bylayer']) is not False

class IfcDraughtingPreDefinedTextFont_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDraughtingPreDefinedTextFont'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert (express_getattr(express_getattr(self, 'Name', INDETERMINATE), 'lower', INDETERMINATE)() in ['iso3098-1fonta', 'iso3098-1fontb']) is not False

class IfcDuctFittingType_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDuctFittingType'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcDuctFittingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcDuctFittingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcDuctSegmentType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDuctSegmentType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcDuctSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcDuctSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcDuctSilencerType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcDuctSilencerType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcDuctSilencerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcDuctSilencerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcEdgeLoop_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEdgeLoop'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        edgelist = express_getattr(self, 'EdgeList', INDETERMINATE)
        ne = express_getattr(self, 'Ne', INDETERMINATE)
        assert (express_getattr(express_getitem(edgelist, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'EdgeStart', INDETERMINATE) == express_getattr(express_getitem(edgelist, ne - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'EdgeEnd', INDETERMINATE)) is not False

class IfcEdgeLoop_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEdgeLoop'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        assert IfcLoopHeadToTail(self) is not False

def calc_IfcEdgeLoop_Ne(self):
    edgelist = express_getattr(self, 'EdgeList', INDETERMINATE)
    return sizeof(edgelist)

class IfcElectricDistributionPoint_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElectricDistributionPoint'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        distributionpointfunction = express_getattr(self, 'DistributionPointFunction', INDETERMINATE)
        assert (distributionpointfunction != express_getattr(IfcElectricDistributionPointFunctionEnum, 'USERDEFINED', INDETERMINATE) or (distributionpointfunction == express_getattr(IfcElectricDistributionPointFunctionEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'UserDefinedFunction', INDETERMINATE)))) is not False

class IfcElementAssembly_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcElementAssembly'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcElementAssemblyTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcElementAssemblyTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

def calc_IfcElementarySurface_Dim(self):
    position = express_getattr(self, 'Position', INDETERMINATE)
    return express_getattr(position, 'Dim', INDETERMINATE)

class IfcEnvironmentalImpactValue_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEnvironmentalImpactValue'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        category = express_getattr(self, 'Category', INDETERMINATE)
        assert (category != express_getattr(IfcEnvironmentalImpactCategoryEnum, 'USERDEFINED', INDETERMINATE) or (category == express_getattr(IfcEnvironmentalImpactCategoryEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'UserDefinedCategory', INDETERMINATE)))) is not False

class IfcEvaporativeCoolerType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEvaporativeCoolerType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcEvaporativeCoolerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcEvaporativeCoolerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcEvaporatorType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcEvaporatorType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcEvaporatorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcEvaporatorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcExternalReference_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcExternalReference'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        location = express_getattr(self, 'Location', INDETERMINATE)
        itemreference = express_getattr(self, 'ItemReference', INDETERMINATE)
        name = express_getattr(self, 'Name', INDETERMINATE)
        assert (exists(itemreference) or exists(location) or exists(name)) is not False

class IfcExtrudedAreaSolid_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcExtrudedAreaSolid'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert (IfcDotProduct(IfcDirection(DirectionRatios=[0.0, 0.0, 1.0]), express_getattr(self, 'ExtrudedDirection', INDETERMINATE)) != 0.0) is not False

class IfcFace_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFace'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        bounds = express_getattr(self, 'Bounds', INDETERMINATE)
        assert (sizeof([temp for temp in bounds if 'ifc2x3.ifcfaceouterbound' in typeof(temp)]) <= 1) is not False

def calc_IfcFaceBasedSurfaceModel_Dim(self):
    return 3

class IfcFanType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFanType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcFanTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcFanTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcFillAreaStyle_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFillAreaStyle'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in express_getattr(self, 'FillStyles', INDETERMINATE) if 'ifc2x3.ifccolour' in typeof(style)]) <= 1) is not False

class IfcFillAreaStyle_WR12:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFillAreaStyle'
    RULE_NAME = 'WR12'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in express_getattr(self, 'FillStyles', INDETERMINATE) if 'ifc2x3.ifcexternallydefinedhatchstyle' in typeof(style)]) <= 1) is not False

class IfcFillAreaStyle_WR13:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFillAreaStyle'
    RULE_NAME = 'WR13'

    @staticmethod
    def __call__(self):
        assert IfcCorrectFillAreaStyle(express_getattr(self, 'FillStyles', INDETERMINATE)) is not False

class IfcFillAreaStyleHatching_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFillAreaStyleHatching'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        startofnexthatchline = express_getattr(self, 'StartOfNextHatchLine', INDETERMINATE)
        assert (not 'ifc2x3.ifctwodirectionrepeatfactor' in typeof(startofnexthatchline)) is not False

class IfcFillAreaStyleHatching_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFillAreaStyleHatching'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        patternstart = express_getattr(self, 'PatternStart', INDETERMINATE)
        assert (not exists(patternstart) or express_getattr(patternstart, 'Dim', INDETERMINATE) == 2) is not False

class IfcFillAreaStyleHatching_WR23:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFillAreaStyleHatching'
    RULE_NAME = 'WR23'

    @staticmethod
    def __call__(self):
        pointofreferencehatchline = express_getattr(self, 'PointOfReferenceHatchLine', INDETERMINATE)
        assert (not exists(pointofreferencehatchline) or express_getattr(pointofreferencehatchline, 'Dim', INDETERMINATE) == 2) is not False

class IfcFilterType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFilterType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcFilterTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcFilterTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcFlowMeterType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFlowMeterType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcFlowMeterTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcFlowMeterTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcFooting_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcFooting'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcFootingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcFootingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcGasTerminalType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGasTerminalType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcGasTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcGasTerminalTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcGeneralProfileProperties_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGeneralProfileProperties'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        crosssectionarea = express_getattr(self, 'CrossSectionArea', INDETERMINATE)
        assert (not exists(crosssectionarea) or crosssectionarea > 0.0) is not False

class IfcGeometricCurveSet_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGeometricCurveSet'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in express_getattr(self, 'Elements', INDETERMINATE) if 'ifc2x3.ifcsurface' in typeof(temp)]) == 0) is not False

class IfcGeometricRepresentationSubContext_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGeometricRepresentationSubContext'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        parentcontext = express_getattr(self, 'ParentContext', INDETERMINATE)
        assert (not 'ifc2x3.ifcgeometricrepresentationsubcontext' in typeof(parentcontext)) is not False

class IfcGeometricRepresentationSubContext_WR32:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGeometricRepresentationSubContext'
    RULE_NAME = 'WR32'

    @staticmethod
    def __call__(self):
        targetview = express_getattr(self, 'TargetView', INDETERMINATE)
        userdefinedtargetview = express_getattr(self, 'UserDefinedTargetView', INDETERMINATE)
        assert (targetview != express_getattr(IfcGeometricProjectionEnum, 'USERDEFINED', INDETERMINATE) or (targetview == express_getattr(IfcGeometricProjectionEnum, 'USERDEFINED', INDETERMINATE) and exists(userdefinedtargetview))) is not False

def calc_IfcGeometricRepresentationSubContext_WorldCoordinateSystem(self):
    parentcontext = express_getattr(self, 'ParentContext', INDETERMINATE)
    return express_getattr(parentcontext, 'WorldCoordinateSystem', INDETERMINATE)

def calc_IfcGeometricRepresentationSubContext_CoordinateSpaceDimension(self):
    parentcontext = express_getattr(self, 'ParentContext', INDETERMINATE)
    return express_getattr(parentcontext, 'CoordinateSpaceDimension', INDETERMINATE)

def calc_IfcGeometricRepresentationSubContext_TrueNorth(self):
    parentcontext = express_getattr(self, 'ParentContext', INDETERMINATE)
    return nvl(express_getattr(parentcontext, 'TrueNorth', INDETERMINATE), express_getitem(express_getattr(express_getattr(self, 'WorldCoordinateSystem', INDETERMINATE), 'P', INDETERMINATE), 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))

def calc_IfcGeometricRepresentationSubContext_Precision(self):
    parentcontext = express_getattr(self, 'ParentContext', INDETERMINATE)
    return nvl(express_getattr(parentcontext, 'Precision', INDETERMINATE), 1)

class IfcGeometricSet_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGeometricSet'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        elements = express_getattr(self, 'Elements', INDETERMINATE)
        assert (sizeof([temp for temp in elements if express_getattr(temp, 'Dim', INDETERMINATE) != express_getattr(express_getitem(elements, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)]) == 0) is not False

def calc_IfcGeometricSet_Dim(self):
    elements = express_getattr(self, 'Elements', INDETERMINATE)
    return express_getattr(express_getitem(elements, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)

class IfcGrid_WR41:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcGrid'
    RULE_NAME = 'WR41'

    @staticmethod
    def __call__(self):
        assert exists(express_getattr(self, 'ObjectPlacement', INDETERMINATE)) is not False

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

class IfcHeatExchangerType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcHeatExchangerType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcHeatExchangerTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcHeatExchangerTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcHumidifierType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcHumidifierType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcHumidifierTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcHumidifierTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcIShapeProfileDef_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcIShapeProfileDef'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        overalldepth = express_getattr(self, 'OverallDepth', INDETERMINATE)
        flangethickness = express_getattr(self, 'FlangeThickness', INDETERMINATE)
        assert (flangethickness < overalldepth / 2.0) is not False

class IfcIShapeProfileDef_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcIShapeProfileDef'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        overallwidth = express_getattr(self, 'OverallWidth', INDETERMINATE)
        webthickness = express_getattr(self, 'WebThickness', INDETERMINATE)
        assert (webthickness < overallwidth) is not False

class IfcIShapeProfileDef_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcIShapeProfileDef'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        overallwidth = express_getattr(self, 'OverallWidth', INDETERMINATE)
        overalldepth = express_getattr(self, 'OverallDepth', INDETERMINATE)
        webthickness = express_getattr(self, 'WebThickness', INDETERMINATE)
        flangethickness = express_getattr(self, 'FlangeThickness', INDETERMINATE)
        filletradius = express_getattr(self, 'FilletRadius', INDETERMINATE)
        assert (not exists(filletradius) or (filletradius <= (overallwidth - webthickness) / 2.0 and filletradius <= (overalldepth - 2.0 * flangethickness) / 2.0)) is not False

class IfcInventory_WR41:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcInventory'
    RULE_NAME = 'WR41'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in express_getattr(express_getattr(self, 'IsGroupedBy', INDETERMINATE), 'RelatedObjects', INDETERMINATE) if not ('ifc2x3.ifcspace' in typeof(temp) or 'ifc2x3.ifcasset' in typeof(temp) or 'ifc2x3.ifcfurnishingelement' in typeof(temp))]) == 0) is not False

class IfcLShapeProfileDef_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLShapeProfileDef'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        depth = express_getattr(self, 'Depth', INDETERMINATE)
        thickness = express_getattr(self, 'Thickness', INDETERMINATE)
        assert (thickness < depth) is not False

class IfcLShapeProfileDef_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLShapeProfileDef'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        width = express_getattr(self, 'Width', INDETERMINATE)
        thickness = express_getattr(self, 'Thickness', INDETERMINATE)
        assert (not exists(width) or thickness < width) is not False

class IfcLine_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcLine'
    RULE_NAME = 'WR1'

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
        representations = express_getattr(self, 'Representations', INDETERMINATE)
        assert (sizeof([temp for temp in representations if not 'ifc2x3.ifcstyledrepresentation' in typeof(temp)]) == 0) is not False

def calc_IfcMaterialLayerSet_TotalThickness(self):
    return IfcMlsTotalThickness(self)

class IfcMechanicalMaterialProperties_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMechanicalMaterialProperties'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        youngmodulus = express_getattr(self, 'YoungModulus', INDETERMINATE)
        assert (not exists(youngmodulus) or youngmodulus >= 0.0) is not False

class IfcMechanicalMaterialProperties_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMechanicalMaterialProperties'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        shearmodulus = express_getattr(self, 'ShearModulus', INDETERMINATE)
        assert (not exists(shearmodulus) or shearmodulus >= 0.0) is not False

class IfcMechanicalSteelMaterialProperties_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMechanicalSteelMaterialProperties'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        yieldstress = express_getattr(self, 'YieldStress', INDETERMINATE)
        assert (not exists(yieldstress) or yieldstress >= 0.0) is not False

class IfcMechanicalSteelMaterialProperties_WR32:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMechanicalSteelMaterialProperties'
    RULE_NAME = 'WR32'

    @staticmethod
    def __call__(self):
        ultimatestress = express_getattr(self, 'UltimateStress', INDETERMINATE)
        assert (not exists(ultimatestress) or ultimatestress >= 0.0) is not False

class IfcMechanicalSteelMaterialProperties_WR33:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMechanicalSteelMaterialProperties'
    RULE_NAME = 'WR33'

    @staticmethod
    def __call__(self):
        hardeningmodule = express_getattr(self, 'HardeningModule', INDETERMINATE)
        assert (not exists(hardeningmodule) or hardeningmodule >= 0.0) is not False

class IfcMechanicalSteelMaterialProperties_WR34:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMechanicalSteelMaterialProperties'
    RULE_NAME = 'WR34'

    @staticmethod
    def __call__(self):
        proportionalstress = express_getattr(self, 'ProportionalStress', INDETERMINATE)
        assert (not exists(proportionalstress) or proportionalstress >= 0.0) is not False

class IfcMove_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMove'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (sizeof(express_getattr(self, 'OperatesOn', INDETERMINATE)) >= 1) is not False

class IfcMove_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMove'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        operateson = express_getattr(self, 'OperatesOn', INDETERMINATE)
        assert (sizeof([temp for temp in operateson if sizeof([temp2 for temp2 in express_getattr(temp, 'RelatedObjects', INDETERMINATE) if 'ifc2x3.ifcactor' in typeof(temp2) or 'ifc2x3.ifcequipmentelement' in typeof(temp2) or 'ifc2x3.ifcfurnishingelement' in typeof(temp2)]) >= 1]) >= 1) is not False

class IfcMove_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcMove'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        assert exists(express_getattr(self, 'Name', INDETERMINATE)) is not False

class IfcNamedUnit_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcNamedUnit'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert IfcCorrectDimensions(express_getattr(self, 'UnitType', INDETERMINATE), express_getattr(self, 'Dimensions', INDETERMINATE)) is not False

class IfcObject_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcObject'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        isdefinedby = express_getattr(self, 'IsDefinedBy', INDETERMINATE)
        assert (sizeof([temp for temp in isdefinedby if 'ifc2x3.ifcreldefinesbytype' in typeof(temp)]) <= 1) is not False

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

class IfcOffsetCurve2D_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcOffsetCurve2D'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        basiscurve = express_getattr(self, 'BasisCurve', INDETERMINATE)
        assert (express_getattr(basiscurve, 'Dim', INDETERMINATE) == 2) is not False

class IfcOffsetCurve3D_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcOffsetCurve3D'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        basiscurve = express_getattr(self, 'BasisCurve', INDETERMINATE)
        assert (express_getattr(basiscurve, 'Dim', INDETERMINATE) == 3) is not False

class IfcOrientedEdge_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcOrientedEdge'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        edgeelement = express_getattr(self, 'EdgeElement', INDETERMINATE)
        assert (not 'ifc2x3.ifcorientededge' in typeof(edgeelement)) is not False

def calc_IfcOrientedEdge_EdgeStart(self):
    edgeelement = express_getattr(self, 'EdgeElement', INDETERMINATE)
    orientation = express_getattr(self, 'Orientation', INDETERMINATE)
    return IfcBooleanChoose(orientation, express_getattr(edgeelement, 'EdgeStart', INDETERMINATE), express_getattr(edgeelement, 'EdgeEnd', INDETERMINATE))

def calc_IfcOrientedEdge_EdgeEnd(self):
    edgeelement = express_getattr(self, 'EdgeElement', INDETERMINATE)
    orientation = express_getattr(self, 'Orientation', INDETERMINATE)
    return IfcBooleanChoose(orientation, express_getattr(edgeelement, 'EdgeEnd', INDETERMINATE), express_getattr(edgeelement, 'EdgeStart', INDETERMINATE))

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
        familyname = express_getattr(self, 'FamilyName', INDETERMINATE)
        givenname = express_getattr(self, 'GivenName', INDETERMINATE)
        assert (exists(familyname) or exists(givenname)) is not False

class IfcPhysicalComplexQuantity_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPhysicalComplexQuantity'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        hasquantities = express_getattr(self, 'HasQuantities', INDETERMINATE)
        assert (sizeof([temp for temp in hasquantities if self == temp]) == 0) is not False

class IfcPile_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPile'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcPileTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcPileTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcPipeFittingType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPipeFittingType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcPipeFittingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcPipeFittingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcPipeSegmentType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPipeSegmentType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcPipeSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcPipeSegmentTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcPixelTexture_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPixelTexture'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        width = express_getattr(self, 'Width', INDETERMINATE)
        assert (width >= 1) is not False

class IfcPixelTexture_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPixelTexture'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        height = express_getattr(self, 'Height', INDETERMINATE)
        assert (height >= 1) is not False

class IfcPixelTexture_WR23:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPixelTexture'
    RULE_NAME = 'WR23'

    @staticmethod
    def __call__(self):
        colourcomponents = express_getattr(self, 'ColourComponents', INDETERMINATE)
        assert (1 <= colourcomponents <= 4) is not False

class IfcPixelTexture_WR24:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPixelTexture'
    RULE_NAME = 'WR24'

    @staticmethod
    def __call__(self):
        width = express_getattr(self, 'Width', INDETERMINATE)
        height = express_getattr(self, 'Height', INDETERMINATE)
        pixel = express_getattr(self, 'Pixel', INDETERMINATE)
        assert (sizeof(pixel) == width * height) is not False

def calc_IfcPlacement_Dim(self):
    location = express_getattr(self, 'Location', INDETERMINATE)
    return express_getattr(location, 'Dim', INDETERMINATE)

def calc_IfcPointOnCurve_Dim(self):
    basiscurve = express_getattr(self, 'BasisCurve', INDETERMINATE)
    return express_getattr(basiscurve, 'Dim', INDETERMINATE)

def calc_IfcPointOnSurface_Dim(self):
    basissurface = express_getattr(self, 'BasisSurface', INDETERMINATE)
    return express_getattr(basissurface, 'Dim', INDETERMINATE)

class IfcPolyLoop_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPolyLoop'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        polygon = express_getattr(self, 'Polygon', INDETERMINATE)
        assert (sizeof([temp for temp in polygon if express_getattr(temp, 'Dim', INDETERMINATE) != express_getattr(express_getitem(polygon, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)]) == 0) is not False

class IfcPolygonalBoundedHalfSpace_WR41:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPolygonalBoundedHalfSpace'
    RULE_NAME = 'WR41'

    @staticmethod
    def __call__(self):
        polygonalboundary = express_getattr(self, 'PolygonalBoundary', INDETERMINATE)
        assert (express_getattr(polygonalboundary, 'Dim', INDETERMINATE) == 2) is not False

class IfcPolygonalBoundedHalfSpace_WR42:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPolygonalBoundedHalfSpace'
    RULE_NAME = 'WR42'

    @staticmethod
    def __call__(self):
        polygonalboundary = express_getattr(self, 'PolygonalBoundary', INDETERMINATE)
        assert (sizeof(typeof(polygonalboundary) * ['ifc2x3.ifcpolyline', 'ifc2x3.ifccompositecurve']) == 1) is not False

class IfcPolyline_WR41:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPolyline'
    RULE_NAME = 'WR41'

    @staticmethod
    def __call__(self):
        points = express_getattr(self, 'Points', INDETERMINATE)
        assert (sizeof([temp for temp in points if express_getattr(temp, 'Dim', INDETERMINATE) != express_getattr(express_getitem(points, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)]) == 0) is not False

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

class IfcPreDefinedDimensionSymbol_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPreDefinedDimensionSymbol'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert (express_getattr(express_getattr(self, 'Name', INDETERMINATE), 'lower', INDETERMINATE)() in ['arclength', 'conicaltaper', 'counterbore', 'countersink', 'depth', 'diameter', 'plusminus', 'radius', 'slope', 'sphericaldiameter', 'sphericalradius', 'square']) is not False

class IfcPreDefinedPointMarkerSymbol_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPreDefinedPointMarkerSymbol'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert (express_getattr(express_getattr(self, 'Name', INDETERMINATE), 'lower', INDETERMINATE)() in ['asterisk', 'circle', 'dot', 'plus', 'square', 'triangle', 'x']) is not False

class IfcPreDefinedTerminatorSymbol_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPreDefinedTerminatorSymbol'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert (express_getattr(express_getattr(self, 'Name', INDETERMINATE), 'lower', INDETERMINATE)() in ['blankedarrow', 'blankedbox', 'blankeddot', 'dimensionorigin', 'filledarrow', 'filledbox', 'filleddot', 'integralsymbol', 'openarrow', 'slash', 'unfilledarrow']) is not False

class IfcProcedure_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProcedure'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in express_getattr(self, 'Decomposes', INDETERMINATE) if not 'ifc2x3.ifcrelnests' in typeof(temp)]) == 0) is not False

class IfcProcedure_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProcedure'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in express_getattr(self, 'IsDecomposedBy', INDETERMINATE) if not 'ifc2x3.ifcrelnests' in typeof(temp)]) == 0) is not False

class IfcProcedure_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProcedure'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        assert exists(express_getattr(self, 'Name', INDETERMINATE)) is not False

class IfcProcedure_WR4:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProcedure'
    RULE_NAME = 'WR4'

    @staticmethod
    def __call__(self):
        proceduretype = express_getattr(self, 'ProcedureType', INDETERMINATE)
        assert (proceduretype != express_getattr(IfcProcedureTypeEnum, 'USERDEFINED', INDETERMINATE) or (proceduretype == express_getattr(IfcProcedureTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'UserDefinedProcedureType', INDETERMINATE)))) is not False

class IfcProduct_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProduct'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        objectplacement = express_getattr(self, 'ObjectPlacement', INDETERMINATE)
        representation = express_getattr(self, 'Representation', INDETERMINATE)
        assert (exists(representation) and exists(objectplacement) or (exists(representation) and (not 'ifc2x3.ifcproductdefinitionshape' in typeof(representation))) or (not exists(representation))) is not False

class IfcProductDefinitionShape_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProductDefinitionShape'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        representations = express_getattr(self, 'Representations', INDETERMINATE)
        assert (sizeof([temp for temp in representations if not 'ifc2x3.ifcshapemodel' in typeof(temp)]) == 0) is not False

class IfcProject_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProject'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert exists(express_getattr(self, 'Name', INDETERMINATE)) is not False

class IfcProject_WR32:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProject'
    RULE_NAME = 'WR32'

    @staticmethod
    def __call__(self):
        representationcontexts = express_getattr(self, 'RepresentationContexts', INDETERMINATE)
        assert (sizeof([temp for temp in representationcontexts if 'ifc2x3.ifcgeometricrepresentationsubcontext' in typeof(temp)]) == 0) is not False

class IfcProject_WR33:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProject'
    RULE_NAME = 'WR33'

    @staticmethod
    def __call__(self):
        assert (sizeof(express_getattr(self, 'Decomposes', INDETERMINATE)) == 0) is not False

class IfcPropertyBoundedValue_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyBoundedValue'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        upperboundvalue = express_getattr(self, 'UpperBoundValue', INDETERMINATE)
        lowerboundvalue = express_getattr(self, 'LowerBoundValue', INDETERMINATE)
        assert (not exists(upperboundvalue) or not exists(lowerboundvalue) or typeof(upperboundvalue) == typeof(lowerboundvalue)) is not False

class IfcPropertyBoundedValue_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyBoundedValue'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        upperboundvalue = express_getattr(self, 'UpperBoundValue', INDETERMINATE)
        lowerboundvalue = express_getattr(self, 'LowerBoundValue', INDETERMINATE)
        assert (exists(upperboundvalue) or exists(lowerboundvalue)) is not False

class IfcPropertyDependencyRelationship_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyDependencyRelationship'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        dependingproperty = express_getattr(self, 'DependingProperty', INDETERMINATE)
        dependantproperty = express_getattr(self, 'DependantProperty', INDETERMINATE)
        assert (dependingproperty != dependantproperty) is not False

class IfcPropertyEnumeratedValue_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyEnumeratedValue'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        enumerationvalues = express_getattr(self, 'EnumerationValues', INDETERMINATE)
        enumerationreference = express_getattr(self, 'EnumerationReference', INDETERMINATE)
        assert (not exists(enumerationreference) or sizeof([temp for temp in enumerationvalues if temp in express_getattr(enumerationreference, 'EnumerationValues', INDETERMINATE)]) == sizeof(enumerationvalues)) is not False

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

class IfcPropertySet_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertySet'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert exists(express_getattr(self, 'Name', INDETERMINATE)) is not False

class IfcPropertySet_WR32:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertySet'
    RULE_NAME = 'WR32'

    @staticmethod
    def __call__(self):
        hasproperties = express_getattr(self, 'HasProperties', INDETERMINATE)
        assert IfcUniquePropertyName(hasproperties) is not False

class IfcPropertyTableValue_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyTableValue'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        definingvalues = express_getattr(self, 'DefiningValues', INDETERMINATE)
        definedvalues = express_getattr(self, 'DefinedValues', INDETERMINATE)
        assert (sizeof(definingvalues) == sizeof(definedvalues)) is not False

class IfcPropertyTableValue_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyTableValue'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in express_getattr(self, 'DefiningValues', INDETERMINATE) if typeof(temp) != typeof(express_getitem(express_getattr(self, 'DefiningValues', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))]) == 0) is not False

class IfcPropertyTableValue_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPropertyTableValue'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in express_getattr(self, 'DefinedValues', INDETERMINATE) if typeof(temp) != typeof(express_getitem(express_getattr(self, 'DefinedValues', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))]) == 0) is not False

class IfcProxy_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcProxy'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert exists(express_getattr(self, 'Name', INDETERMINATE)) is not False

class IfcPumpType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcPumpType'
    RULE_NAME = 'WR1'

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

class IfcRailing_WR61:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRailing'
    RULE_NAME = 'WR61'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcRailingTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcRailingTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcRamp_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRamp'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (hiindex(express_getattr(self, 'IsDecomposedBy', INDETERMINATE)) == 0 or (hiindex(express_getattr(self, 'IsDecomposedBy', INDETERMINATE)) == 1 and (not exists(express_getattr(self, 'Representation', INDETERMINATE))))) is not False

class IfcRationalBezierCurve_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRationalBezierCurve'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        weightsdata = express_getattr(self, 'WeightsData', INDETERMINATE)
        assert (sizeof(weightsdata) == sizeof(express_getattr(self, 'ControlPointsList', INDETERMINATE))) is not False

class IfcRationalBezierCurve_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRationalBezierCurve'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        assert IfcCurveWeightsPositive(self) is not False

def calc_IfcRationalBezierCurve_Weights(self):
    weightsdata = express_getattr(self, 'WeightsData', INDETERMINATE)
    return IfcListToArray(weightsdata, 0, express_getattr(self, 'UpperIndexOnControlPoints', INDETERMINATE))

class IfcRectangleHollowProfileDef_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRectangleHollowProfileDef'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        wallthickness = express_getattr(self, 'WallThickness', INDETERMINATE)
        assert (wallthickness < express_getattr(self, 'XDim', INDETERMINATE) / 2.0 and wallthickness < express_getattr(self, 'YDim', INDETERMINATE) / 2.0) is not False

class IfcRectangleHollowProfileDef_WR32:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRectangleHollowProfileDef'
    RULE_NAME = 'WR32'

    @staticmethod
    def __call__(self):
        outerfilletradius = express_getattr(self, 'OuterFilletRadius', INDETERMINATE)
        assert (not exists(outerfilletradius) or (outerfilletradius <= express_getattr(self, 'XDim', INDETERMINATE) / 2.0 and outerfilletradius <= express_getattr(self, 'YDim', INDETERMINATE) / 2.0)) is not False

class IfcRectangleHollowProfileDef_WR33:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRectangleHollowProfileDef'
    RULE_NAME = 'WR33'

    @staticmethod
    def __call__(self):
        wallthickness = express_getattr(self, 'WallThickness', INDETERMINATE)
        innerfilletradius = express_getattr(self, 'InnerFilletRadius', INDETERMINATE)
        assert (not exists(innerfilletradius) or (innerfilletradius <= express_getattr(self, 'XDim', INDETERMINATE) / 2.0 - wallthickness and innerfilletradius <= express_getattr(self, 'YDim', INDETERMINATE) / 2.0 - wallthickness)) is not False

class IfcRectangularTrimmedSurface_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRectangularTrimmedSurface'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        u1 = express_getattr(self, 'U1', INDETERMINATE)
        u2 = express_getattr(self, 'U2', INDETERMINATE)
        assert (u1 != u2) is not False

class IfcRectangularTrimmedSurface_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRectangularTrimmedSurface'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        v1 = express_getattr(self, 'V1', INDETERMINATE)
        v2 = express_getattr(self, 'V2', INDETERMINATE)
        assert (v1 != v2) is not False

class IfcRectangularTrimmedSurface_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRectangularTrimmedSurface'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        basissurface = express_getattr(self, 'BasisSurface', INDETERMINATE)
        u1 = express_getattr(self, 'U1', INDETERMINATE)
        u2 = express_getattr(self, 'U2', INDETERMINATE)
        usense = express_getattr(self, 'Usense', INDETERMINATE)
        assert ('ifc2x3.ifcelementarysurface' in typeof(basissurface) and (not 'ifc2x3.ifcplane' in typeof(basissurface)) or 'ifc2x3.ifcsurfaceofrevolution' in typeof(basissurface) or usense == (u2 > u1)) is not False

class IfcRectangularTrimmedSurface_WR4:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRectangularTrimmedSurface'
    RULE_NAME = 'WR4'

    @staticmethod
    def __call__(self):
        v1 = express_getattr(self, 'V1', INDETERMINATE)
        v2 = express_getattr(self, 'V2', INDETERMINATE)
        vsense = express_getattr(self, 'Vsense', INDETERMINATE)
        assert (vsense == (v2 > v1)) is not False

def calc_IfcRectangularTrimmedSurface_Dim(self):
    basissurface = express_getattr(self, 'BasisSurface', INDETERMINATE)
    return express_getattr(basissurface, 'Dim', INDETERMINATE)

class IfcReinforcingBar_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcReinforcingBar'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        barrole = express_getattr(self, 'BarRole', INDETERMINATE)
        assert (barrole != express_getattr(IfcReinforcingBarRoleEnum, 'USERDEFINED', INDETERMINATE) or (barrole == express_getattr(IfcReinforcingBarRoleEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcRelAssigns_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssigns'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        relatedobjects = express_getattr(self, 'RelatedObjects', INDETERMINATE)
        relatedobjectstype = express_getattr(self, 'RelatedObjectsType', INDETERMINATE)
        assert IfcCorrectObjectAssignment(relatedobjectstype, relatedobjects) is not False

class IfcRelAssignsTasks_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssignsTasks'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (hiindex(express_getattr(self, 'RelatedObjects', INDETERMINATE)) == 1) is not False

class IfcRelAssignsTasks_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssignsTasks'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        assert ('ifc2x3.ifctask' in typeof(express_getitem(express_getattr(self, 'RelatedObjects', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))) is not False

class IfcRelAssignsTasks_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssignsTasks'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        assert ('ifc2x3.ifcworkcontrol' in typeof(express_getattr(self, 'RelatingControl', INDETERMINATE))) is not False

class IfcRelAssignsToActor_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssignsToActor'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        relatingactor = express_getattr(self, 'RelatingActor', INDETERMINATE)
        assert (sizeof([temp for temp in express_getattr(self, 'RelatedObjects', INDETERMINATE) if relatingactor == temp]) == 0) is not False

class IfcRelAssignsToControl_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssignsToControl'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        relatingcontrol = express_getattr(self, 'RelatingControl', INDETERMINATE)
        assert (sizeof([temp for temp in express_getattr(self, 'RelatedObjects', INDETERMINATE) if relatingcontrol == temp]) == 0) is not False

class IfcRelAssignsToGroup_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssignsToGroup'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        relatinggroup = express_getattr(self, 'RelatingGroup', INDETERMINATE)
        assert (sizeof([temp for temp in express_getattr(self, 'RelatedObjects', INDETERMINATE) if relatinggroup == temp]) == 0) is not False

class IfcRelAssignsToProcess_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssignsToProcess'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        relatingprocess = express_getattr(self, 'RelatingProcess', INDETERMINATE)
        assert (sizeof([temp for temp in express_getattr(self, 'RelatedObjects', INDETERMINATE) if relatingprocess == temp]) == 0) is not False

class IfcRelAssignsToProduct_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssignsToProduct'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        relatingproduct = express_getattr(self, 'RelatingProduct', INDETERMINATE)
        assert (sizeof([temp for temp in express_getattr(self, 'RelatedObjects', INDETERMINATE) if relatingproduct == temp]) == 0) is not False

class IfcRelAssignsToResource_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssignsToResource'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        relatingresource = express_getattr(self, 'RelatingResource', INDETERMINATE)
        assert (sizeof([temp for temp in express_getattr(self, 'RelatedObjects', INDETERMINATE) if relatingresource == temp]) == 0) is not False

class IfcRelAssociates_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssociates'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        relatedobjects = express_getattr(self, 'RelatedObjects', INDETERMINATE)
        assert (sizeof([temp for temp in relatedobjects if not ('ifc2x3.ifcobjectdefinition' in typeof(temp) or 'ifc2x3.ifcpropertydefinition' in typeof(temp))]) == 0) is not False

class IfcRelAssociatesMaterial_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssociatesMaterial'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in express_getattr(self, 'RelatedObjects', INDETERMINATE) if 'ifc2x3.ifcfeatureelementsubtraction' in typeof(temp) or 'ifc2x3.ifcvirtualelement' in typeof(temp)]) == 0) is not False

class IfcRelAssociatesMaterial_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelAssociatesMaterial'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in express_getattr(self, 'RelatedObjects', INDETERMINATE) if not 'ifc2x3.ifcproduct' in typeof(temp) and (not 'ifc2x3.ifctypeproduct' in typeof(temp))]) == 0) is not False

class IfcRelConnectsElements_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelConnectsElements'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        relatingelement = express_getattr(self, 'RelatingElement', INDETERMINATE)
        relatedelement = express_getattr(self, 'RelatedElement', INDETERMINATE)
        assert (relatingelement != relatedelement) is not False

class IfcRelContainedInSpatialStructure_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelContainedInSpatialStructure'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        relatedelements = express_getattr(self, 'RelatedElements', INDETERMINATE)
        assert (sizeof([temp for temp in relatedelements if 'ifc2x3.ifcspatialstructureelement' in typeof(temp)]) == 0) is not False

class IfcRelDecomposes_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelDecomposes'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        relatingobject = express_getattr(self, 'RelatingObject', INDETERMINATE)
        relatedobjects = express_getattr(self, 'RelatedObjects', INDETERMINATE)
        assert (sizeof([temp for temp in relatedobjects if relatingobject == temp]) == 0) is not False

class IfcRelNests_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelNests'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in express_getattr(self, 'RelatedObjects', INDETERMINATE) if not typeof(express_getattr(self, 'RelatingObject', INDETERMINATE)) == typeof(temp)]) == 0) is not False

class IfcRelOverridesProperties_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelOverridesProperties'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (sizeof(express_getattr(self, 'RelatedObjects', INDETERMINATE)) == 1) is not False

class IfcRelReferencedInSpatialStructure_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelReferencedInSpatialStructure'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        relatedelements = express_getattr(self, 'RelatedElements', INDETERMINATE)
        assert (sizeof([temp for temp in relatedelements if 'ifc2x3.ifcspatialstructureelement' in typeof(temp)]) == 0) is not False

class IfcRelSchedulesCostItems_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelSchedulesCostItems'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in express_getattr(self, 'RelatedObjects', INDETERMINATE) if not 'ifc2x3.ifccostitem' in typeof(temp)]) == 0) is not False

class IfcRelSchedulesCostItems_WR12:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelSchedulesCostItems'
    RULE_NAME = 'WR12'

    @staticmethod
    def __call__(self):
        assert ('ifc2x3.ifccostschedule' in typeof(express_getattr(self, 'RelatingControl', INDETERMINATE))) is not False

class IfcRelSequence_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelSequence'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        relatingprocess = express_getattr(self, 'RelatingProcess', INDETERMINATE)
        relatedprocess = express_getattr(self, 'RelatedProcess', INDETERMINATE)
        assert (relatingprocess != relatedprocess) is not False

class IfcRelSpaceBoundary_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRelSpaceBoundary'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        relatedbuildingelement = express_getattr(self, 'RelatedBuildingElement', INDETERMINATE)
        physicalorvirtualboundary = express_getattr(self, 'PhysicalOrVirtualBoundary', INDETERMINATE)
        assert (physicalorvirtualboundary == express_getattr(IfcPhysicalOrVirtualEnum, 'Physical', INDETERMINATE) and (exists(relatedbuildingelement) and (not 'ifc2x3.ifcvirtualelement' in typeof(relatedbuildingelement))) or (physicalorvirtualboundary == express_getattr(IfcPhysicalOrVirtualEnum, 'Virtual', INDETERMINATE) and (not exists(relatedbuildingelement) or 'ifc2x3.ifcvirtualelement' in typeof(relatedbuildingelement))) or physicalorvirtualboundary == express_getattr(IfcPhysicalOrVirtualEnum, 'NotDefined', INDETERMINATE)) is not False

class IfcRevolvedAreaSolid_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRevolvedAreaSolid'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        axis = express_getattr(self, 'Axis', INDETERMINATE)
        assert (express_getitem(express_getattr(express_getattr(axis, 'Location', INDETERMINATE), 'Coordinates', INDETERMINATE), 3 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) == 0.0) is not False

class IfcRevolvedAreaSolid_WR32:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRevolvedAreaSolid'
    RULE_NAME = 'WR32'

    @staticmethod
    def __call__(self):
        axis = express_getattr(self, 'Axis', INDETERMINATE)
        assert (express_getitem(express_getattr(express_getattr(axis, 'Z', INDETERMINATE), 'DirectionRatios', INDETERMINATE), 3 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE) == 0.0) is not False

def calc_IfcRevolvedAreaSolid_AxisLine(self):
    axis = express_getattr(self, 'Axis', INDETERMINATE)
    return IfcLine(Pnt=express_getattr(axis, 'Location', INDETERMINATE), Dir=IfcVector(Orientation=express_getattr(axis, 'Z', INDETERMINATE), Magnitude=1.0))

class IfcRoof_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRoof'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (hiindex(express_getattr(self, 'IsDecomposedBy', INDETERMINATE)) == 0 or (hiindex(express_getattr(self, 'IsDecomposedBy', INDETERMINATE)) == 1 and (not exists(express_getattr(self, 'Representation', INDETERMINATE))))) is not False

class IfcRoundedRectangleProfileDef_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcRoundedRectangleProfileDef'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        roundingradius = express_getattr(self, 'RoundingRadius', INDETERMINATE)
        assert (roundingradius <= express_getattr(self, 'XDim', INDETERMINATE) / 2.0 and roundingradius <= express_getattr(self, 'YDim', INDETERMINATE) / 2.0) is not False

def calc_IfcSIUnit_Dimensions(self):
    return IfcDimensionsForSiUnit(express_getattr(self, 'Name', INDETERMINATE))

class IfcSectionedSpine_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSectionedSpine'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        crosssections = express_getattr(self, 'CrossSections', INDETERMINATE)
        crosssectionpositions = express_getattr(self, 'CrossSectionPositions', INDETERMINATE)
        assert (sizeof(crosssections) == sizeof(crosssectionpositions)) is not False

class IfcSectionedSpine_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSectionedSpine'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        crosssections = express_getattr(self, 'CrossSections', INDETERMINATE)
        assert (sizeof([temp for temp in crosssections if express_getattr(express_getitem(crosssections, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'ProfileType', INDETERMINATE) != express_getattr(temp, 'ProfileType', INDETERMINATE)]) == 0) is not False

class IfcSectionedSpine_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSectionedSpine'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        spinecurve = express_getattr(self, 'SpineCurve', INDETERMINATE)
        assert (express_getattr(spinecurve, 'Dim', INDETERMINATE) == 3) is not False

def calc_IfcSectionedSpine_Dim(self):
    return 3

class IfcServiceLifeFactor_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcServiceLifeFactor'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not predefinedtype == express_getattr(IfcServiceLifeFactorTypeEnum, 'USERDEFINED', INDETERMINATE) or exists(express_getattr(self, 'ObjectType', INDETERMINATE))) is not False

class IfcShapeModel_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcShapeModel'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        ofshapeaspect = express_getattr(self, 'OfShapeAspect', INDETERMINATE)
        assert (sizeof(express_getattr(self, 'OfProductRepresentation', INDETERMINATE)) == 1) ^ (sizeof(express_getattr(self, 'RepresentationMap', INDETERMINATE)) == 1) ^ (sizeof(ofshapeaspect) == 1) is not False

class IfcShapeRepresentation_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcShapeRepresentation'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        assert ('ifc2x3.ifcgeometricrepresentationcontext' in typeof(express_getattr(self, 'ContextOfItems', INDETERMINATE))) is not False

class IfcShapeRepresentation_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcShapeRepresentation'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        items = express_getattr(self, 'Items', INDETERMINATE)
        assert (sizeof([temp for temp in items if 'ifc2x3.ifctopologicalrepresentationitem' in typeof(temp) and (not sizeof(['ifc2x3.ifcvertexpoint', 'ifc2x3.ifcedgecurve', 'ifc2x3.ifcfacesurface'] * typeof(temp)) == 1)]) == 0) is not False

class IfcShapeRepresentation_WR23:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcShapeRepresentation'
    RULE_NAME = 'WR23'

    @staticmethod
    def __call__(self):
        assert exists(express_getattr(self, 'RepresentationType', INDETERMINATE)) is not False

class IfcShapeRepresentation_WR24:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcShapeRepresentation'
    RULE_NAME = 'WR24'

    @staticmethod
    def __call__(self):
        assert IfcShapeRepresentationTypes(express_getattr(self, 'RepresentationType', INDETERMINATE), express_getattr(self, 'Items', INDETERMINATE)) is not False

def calc_IfcShellBasedSurfaceModel_Dim(self):
    return 3

class IfcSlab_WR61:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSlab'
    RULE_NAME = 'WR61'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (not exists(predefinedtype) or predefinedtype != express_getattr(IfcSlabTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcSlabTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

def calc_IfcSolidModel_Dim(self):
    return 3

class IfcSpaceHeaterType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSpaceHeaterType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcSpaceHeaterTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcSpaceHeaterTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcSpatialStructureElement_WR41:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSpatialStructureElement'
    RULE_NAME = 'WR41'

    @staticmethod
    def __call__(self):
        assert (hiindex(express_getattr(self, 'Decomposes', INDETERMINATE)) == 1 and 'ifc2x3.ifcrelaggregates' in typeof(express_getitem(express_getattr(self, 'Decomposes', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and ('ifc2x3.ifcproject' in typeof(express_getattr(express_getitem(express_getattr(self, 'Decomposes', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingObject', INDETERMINATE)) or 'ifc2x3.ifcspatialstructureelement' in typeof(express_getattr(express_getitem(express_getattr(self, 'Decomposes', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatingObject', INDETERMINATE)))) is not False

class IfcStair_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStair'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (hiindex(express_getattr(self, 'IsDecomposedBy', INDETERMINATE)) == 0 or (hiindex(express_getattr(self, 'IsDecomposedBy', INDETERMINATE)) == 1 and (not exists(express_getattr(self, 'Representation', INDETERMINATE))))) is not False

class IfcStructuralLinearAction_WR61:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralLinearAction'
    RULE_NAME = 'WR61'

    @staticmethod
    def __call__(self):
        assert (sizeof(['ifc2x3.ifcstructuralloadlinearforce', 'ifc2x3.ifcstructuralloadtemperature'] * typeof(express_getattr(self, 'AppliedLoad', INDETERMINATE))) == 1) is not False

def calc_IfcStructuralLinearActionVarying_VaryingAppliedLoads(self):
    subsequentappliedloads = express_getattr(self, 'SubsequentAppliedLoads', INDETERMINATE)
    return IfcAddToBeginOfList(express_getattr(self, 'AppliedLoad', INDETERMINATE), subsequentappliedloads)

class IfcStructuralPlanarAction_WR61:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralPlanarAction'
    RULE_NAME = 'WR61'

    @staticmethod
    def __call__(self):
        assert (sizeof(['ifc2x3.ifcstructuralloadplanarforce', 'ifc2x3.ifcstructuralloadtemperature'] * typeof(express_getattr(self, 'AppliedLoad', INDETERMINATE))) == 1) is not False

def calc_IfcStructuralPlanarActionVarying_VaryingAppliedLoads(self):
    subsequentappliedloads = express_getattr(self, 'SubsequentAppliedLoads', INDETERMINATE)
    return IfcAddToBeginOfList(express_getattr(self, 'AppliedLoad', INDETERMINATE), subsequentappliedloads)

class IfcStructuralPointAction_WR61:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralPointAction'
    RULE_NAME = 'WR61'

    @staticmethod
    def __call__(self):
        assert (sizeof(['ifc2x3.ifcstructuralloadsingleforce', 'ifc2x3.ifcstructuralloadsingledisplacement'] * typeof(express_getattr(self, 'AppliedLoad', INDETERMINATE))) == 1) is not False

class IfcStructuralPointReaction_WR61:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralPointReaction'
    RULE_NAME = 'WR61'

    @staticmethod
    def __call__(self):
        assert (sizeof(['ifc2x3.ifcstructuralloadsingleforce', 'ifc2x3.ifcstructuralloadsingledisplacement'] * typeof(express_getattr(self, 'AppliedLoad', INDETERMINATE))) == 1) is not False

class IfcStructuralProfileProperties_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralProfileProperties'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        sheardeformationareay = express_getattr(self, 'ShearDeformationAreaY', INDETERMINATE)
        assert (not exists(sheardeformationareay) or sheardeformationareay >= 0.0) is not False

class IfcStructuralProfileProperties_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralProfileProperties'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        sheardeformationareaz = express_getattr(self, 'ShearDeformationAreaZ', INDETERMINATE)
        assert (not exists(sheardeformationareaz) or sheardeformationareaz >= 0.0) is not False

class IfcStructuralSteelProfileProperties_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralSteelProfileProperties'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        shearareay = express_getattr(self, 'ShearAreaY', INDETERMINATE)
        assert (not exists(shearareay) or shearareay >= 0.0) is not False

class IfcStructuralSteelProfileProperties_WR32:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralSteelProfileProperties'
    RULE_NAME = 'WR32'

    @staticmethod
    def __call__(self):
        shearareaz = express_getattr(self, 'ShearAreaZ', INDETERMINATE)
        assert (not exists(shearareaz) or shearareaz >= 0.0) is not False

class IfcStructuralSurfaceMemberVarying_WR61:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralSurfaceMemberVarying'
    RULE_NAME = 'WR61'

    @staticmethod
    def __call__(self):
        assert exists(express_getattr(self, 'Thickness', INDETERMINATE)) is not False

class IfcStructuralSurfaceMemberVarying_WR62:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralSurfaceMemberVarying'
    RULE_NAME = 'WR62'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in express_getattr(express_getattr(self, 'VaryingThicknessLocation', INDETERMINATE), 'ShapeRepresentations', INDETERMINATE) if not sizeof(express_getattr(temp, 'Items', INDETERMINATE)) == 1]) == 0) is not False

class IfcStructuralSurfaceMemberVarying_WR63:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuralSurfaceMemberVarying'
    RULE_NAME = 'WR63'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in express_getattr(express_getattr(self, 'VaryingThicknessLocation', INDETERMINATE), 'ShapeRepresentations', INDETERMINATE) if not ('ifc2x3.ifccartesianpoint' in typeof(express_getitem(express_getattr(temp, 'Items', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) or 'ifc2x3.ifcpointonsurface' in typeof(express_getitem(express_getattr(temp, 'Items', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)))]) == 0) is not False

def calc_IfcStructuralSurfaceMemberVarying_VaryingThickness(self):
    subsequentthickness = express_getattr(self, 'SubsequentThickness', INDETERMINATE)
    return IfcAddToBeginOfList(express_getattr(self, 'Thickness', INDETERMINATE), subsequentthickness)

class IfcStructuredDimensionCallout_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStructuredDimensionCallout'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        contents = express_getattr(self, 'Contents', INDETERMINATE)
        assert (sizeof([ato for ato in [con for con in express_getattr(self, 'contents', INDETERMINATE) if 'ifc2x3.ifcannotationtextoccurrence' in typeof(con)] if not express_getattr(express_getattr(ato, 'Name', INDETERMINATE), 'lower', INDETERMINATE)() in ['dimensionvalue', 'tolerancevalue', 'unittext', 'prefixtext', 'suffixtext']]) == 0) is not False

class IfcStyledItem_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStyledItem'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        styles = express_getattr(self, 'Styles', INDETERMINATE)
        assert (sizeof(styles) == 1) is not False

class IfcStyledItem_WR12:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStyledItem'
    RULE_NAME = 'WR12'

    @staticmethod
    def __call__(self):
        item = express_getattr(self, 'Item', INDETERMINATE)
        assert (not 'ifc2x3.ifcstyleditem' in typeof(item)) is not False

class IfcStyledRepresentation_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcStyledRepresentation'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in express_getattr(self, 'Items', INDETERMINATE) if not 'ifc2x3.ifcstyleditem' in typeof(temp)]) == 0) is not False

class IfcSurfaceOfLinearExtrusion_WR41:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceOfLinearExtrusion'
    RULE_NAME = 'WR41'

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

class IfcSurfaceStyle_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceStyle'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in express_getattr(self, 'Styles', INDETERMINATE) if 'ifc2x3.ifcsurfacestyleshading' in typeof(style)]) <= 1) is not False

class IfcSurfaceStyle_WR12:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceStyle'
    RULE_NAME = 'WR12'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in express_getattr(self, 'Styles', INDETERMINATE) if 'ifc2x3.ifcsurfacestylelighting' in typeof(style)]) <= 1) is not False

class IfcSurfaceStyle_WR13:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceStyle'
    RULE_NAME = 'WR13'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in express_getattr(self, 'Styles', INDETERMINATE) if 'ifc2x3.ifcsurfacestylerefraction' in typeof(style)]) <= 1) is not False

class IfcSurfaceStyle_WR14:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceStyle'
    RULE_NAME = 'WR14'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in express_getattr(self, 'Styles', INDETERMINATE) if 'ifc2x3.ifcsurfacestylewithtextures' in typeof(style)]) <= 1) is not False

class IfcSurfaceStyle_WR15:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSurfaceStyle'
    RULE_NAME = 'WR15'

    @staticmethod
    def __call__(self):
        assert (sizeof([style for style in express_getattr(self, 'Styles', INDETERMINATE) if 'ifc2x3.ifcexternallydefinedsurfacestyle' in typeof(style)]) <= 1) is not False

class IfcSweptAreaSolid_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSweptAreaSolid'
    RULE_NAME = 'WR22'

    @staticmethod
    def __call__(self):
        sweptarea = express_getattr(self, 'SweptArea', INDETERMINATE)
        assert (express_getattr(sweptarea, 'ProfileType', INDETERMINATE) == express_getattr(IfcProfileTypeEnum, 'Area', INDETERMINATE)) is not False

class IfcSweptDiskSolid_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSweptDiskSolid'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        directrix = express_getattr(self, 'Directrix', INDETERMINATE)
        assert (express_getattr(directrix, 'Dim', INDETERMINATE) == 3) is not False

class IfcSweptDiskSolid_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSweptDiskSolid'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        radius = express_getattr(self, 'Radius', INDETERMINATE)
        innerradius = express_getattr(self, 'InnerRadius', INDETERMINATE)
        assert (not exists(innerradius) or radius > innerradius) is not False

class IfcSweptSurface_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSweptSurface'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        sweptcurve = express_getattr(self, 'SweptCurve', INDETERMINATE)
        assert (not 'ifc2x3.ifcderivedprofiledef' in typeof(sweptcurve)) is not False

class IfcSweptSurface_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcSweptSurface'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        sweptcurve = express_getattr(self, 'SweptCurve', INDETERMINATE)
        assert (express_getattr(sweptcurve, 'ProfileType', INDETERMINATE) == express_getattr(IfcProfileTypeEnum, 'Curve', INDETERMINATE)) is not False

def calc_IfcSweptSurface_Dim(self):
    position = express_getattr(self, 'Position', INDETERMINATE)
    return express_getattr(position, 'Dim', INDETERMINATE)

class IfcTShapeProfileDef_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTShapeProfileDef'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        depth = express_getattr(self, 'Depth', INDETERMINATE)
        flangethickness = express_getattr(self, 'FlangeThickness', INDETERMINATE)
        assert (flangethickness < depth) is not False

class IfcTShapeProfileDef_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTShapeProfileDef'
    RULE_NAME = 'WR2'

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
        rows = express_getattr(self, 'Rows', INDETERMINATE)
        assert (sizeof([temp for temp in rows if hiindex(express_getattr(temp, 'RowCells', INDETERMINATE)) != hiindex(express_getattr(express_getitem(rows, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RowCells', INDETERMINATE))]) == 0) is not False

class IfcTable_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTable'
    RULE_NAME = 'WR3'

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

class IfcTankType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTankType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcTankTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcTankTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcTask_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTask'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in express_getattr(self, 'Decomposes', INDETERMINATE) if not 'ifc2x3.ifcrelnests' in typeof(temp)]) == 0) is not False

class IfcTask_WR2:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTask'
    RULE_NAME = 'WR2'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in express_getattr(self, 'IsDecomposedBy', INDETERMINATE) if not 'ifc2x3.ifcrelnests' in typeof(temp)]) == 0) is not False

class IfcTask_WR3:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTask'
    RULE_NAME = 'WR3'

    @staticmethod
    def __call__(self):
        assert exists(express_getattr(self, 'Name', INDETERMINATE)) is not False

class IfcTelecomAddress_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTelecomAddress'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        telephonenumbers = express_getattr(self, 'TelephoneNumbers', INDETERMINATE)
        facsimilenumbers = express_getattr(self, 'FacsimileNumbers', INDETERMINATE)
        pagernumber = express_getattr(self, 'PagerNumber', INDETERMINATE)
        electronicmailaddresses = express_getattr(self, 'ElectronicMailAddresses', INDETERMINATE)
        wwwhomepageurl = express_getattr(self, 'WWWHomePageURL', INDETERMINATE)
        assert (exists(telephonenumbers) or exists(pagernumber) or exists(facsimilenumbers) or exists(electronicmailaddresses) or exists(wwwhomepageurl)) is not False

class IfcTendon_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTendon'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcTendonTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcTendonTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ObjectType', INDETERMINATE)))) is not False

class IfcTextLiteralWithExtent_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTextLiteralWithExtent'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        extent = express_getattr(self, 'Extent', INDETERMINATE)
        assert (not 'ifc2x3.ifcplanarbox' in typeof(extent)) is not False

class IfcTextStyleFontModel_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTextStyleFontModel'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        assert ('ifc2x3.ifclengthmeasure' in typeof(express_getattr(self, 'FontSize', INDETERMINATE)) and express_getattr(self, 'FontSize', INDETERMINATE) > 0.0) is not False

class IfcTextureMap_WR11:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTextureMap'
    RULE_NAME = 'WR11'

    @staticmethod
    def __call__(self):
        assert (sizeof(['ifc2x3.ifcshellbasedsurfacemodel', 'ifc2x3.ifcfacebasedsurfacemodel', 'ifc2x3.ifcfacetedbrep', 'ifc2x3.ifcfacetedbrepwithvoids'] * typeof(express_getattr(express_getitem(express_getattr(self, 'AnnotatedSurface', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Item', INDETERMINATE))) >= 1) is not False

class IfcTimeSeriesSchedule_WR41:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTimeSeriesSchedule'
    RULE_NAME = 'WR41'

    @staticmethod
    def __call__(self):
        timeseriesscheduletype = express_getattr(self, 'TimeSeriesScheduleType', INDETERMINATE)
        assert (not timeseriesscheduletype == express_getattr(IfcTimeSeriesScheduleTypeEnum, 'USERDEFINED', INDETERMINATE) or exists(express_getattr(self, 'ObjectType', INDETERMINATE))) is not False

class IfcTopologyRepresentation_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTopologyRepresentation'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in express_getattr(self, 'Items', INDETERMINATE) if not 'ifc2x3.ifctopologicalrepresentationitem' in typeof(temp)]) == 0) is not False

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

class IfcTrimmedCurve_WR41:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTrimmedCurve'
    RULE_NAME = 'WR41'

    @staticmethod
    def __call__(self):
        trim1 = express_getattr(self, 'Trim1', INDETERMINATE)
        assert (hiindex(trim1) == 1 or typeof(express_getitem(trim1, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) != typeof(express_getitem(trim1, 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))) is not False

class IfcTrimmedCurve_WR42:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTrimmedCurve'
    RULE_NAME = 'WR42'

    @staticmethod
    def __call__(self):
        trim2 = express_getattr(self, 'Trim2', INDETERMINATE)
        assert (hiindex(trim2) == 1 or typeof(express_getitem(trim2, 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) != typeof(express_getitem(trim2, 2 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))) is not False

class IfcTrimmedCurve_WR43:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTrimmedCurve'
    RULE_NAME = 'WR43'

    @staticmethod
    def __call__(self):
        basiscurve = express_getattr(self, 'BasisCurve', INDETERMINATE)
        assert (not 'ifc2x3.ifcboundedcurve' in typeof(basiscurve)) is not False

class IfcTubeBundleType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTubeBundleType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcTubeBundleTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcTubeBundleTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcTypeObject_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTypeObject'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert exists(express_getattr(self, 'Name', INDETERMINATE)) is not False

class IfcTypeProduct_WR41:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcTypeProduct'
    RULE_NAME = 'WR41'

    @staticmethod
    def __call__(self):
        assert (not exists(lambda : express_getitem(express_getattr(self, 'ObjectTypeOf', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) or sizeof([temp for temp in express_getattr(express_getitem(express_getattr(self, 'ObjectTypeOf', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'RelatedObjects', INDETERMINATE) if not 'ifc2x3.ifcproduct' in typeof(temp)]) == 0) is not False

class IfcUShapeProfileDef_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcUShapeProfileDef'
    RULE_NAME = 'WR21'

    @staticmethod
    def __call__(self):
        depth = express_getattr(self, 'Depth', INDETERMINATE)
        flangethickness = express_getattr(self, 'FlangeThickness', INDETERMINATE)
        assert (flangethickness < depth / 2.0) is not False

class IfcUShapeProfileDef_WR22:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcUShapeProfileDef'
    RULE_NAME = 'WR22'

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

class IfcUnitaryEquipmentType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcUnitaryEquipmentType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcUnitaryEquipmentTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcUnitaryEquipmentTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcValveType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcValveType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcValveTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcValveTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcVector_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcVector'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        magnitude = express_getattr(self, 'Magnitude', INDETERMINATE)
        assert (magnitude >= 0.0) is not False

def calc_IfcVector_Dim(self):
    orientation = express_getattr(self, 'Orientation', INDETERMINATE)
    return express_getattr(orientation, 'Dim', INDETERMINATE)

class IfcVibrationIsolatorType_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcVibrationIsolatorType'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        predefinedtype = express_getattr(self, 'PredefinedType', INDETERMINATE)
        assert (predefinedtype != express_getattr(IfcVibrationIsolatorTypeEnum, 'USERDEFINED', INDETERMINATE) or (predefinedtype == express_getattr(IfcVibrationIsolatorTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'ElementType', INDETERMINATE)))) is not False

class IfcWall_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWall'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in express_getattr(self, 'HasAssociations', INDETERMINATE) if 'ifc2x3.ifcrelassociatesmaterial' in typeof(temp)]) <= 1) is not False

class IfcWallStandardCase_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWallStandardCase'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        assert (sizeof([temp for temp in usedin(self, 'ifc2x3.ifcrelassociates.relatedobjects') if 'ifc2x3.ifcrelassociatesmaterial' in typeof(temp) and 'ifc2x3.ifcmateriallayersetusage' in typeof(express_getattr(temp, 'RelatingMaterial', INDETERMINATE))]) == 1) is not False

class IfcWindowLiningProperties_WR31:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWindowLiningProperties'
    RULE_NAME = 'WR31'

    @staticmethod
    def __call__(self):
        liningdepth = express_getattr(self, 'LiningDepth', INDETERMINATE)
        liningthickness = express_getattr(self, 'LiningThickness', INDETERMINATE)
        assert (not (not exists(liningdepth) and exists(liningthickness))) is not False

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
        assert (exists(lambda : express_getitem(express_getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and 'ifc2x3.ifcwindowstyle' in typeof(express_getitem(express_getattr(self, 'DefinesType', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE))) is not False

class IfcWorkControl_WR1:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcWorkControl'
    RULE_NAME = 'WR1'

    @staticmethod
    def __call__(self):
        workcontroltype = express_getattr(self, 'WorkControlType', INDETERMINATE)
        assert (workcontroltype != express_getattr(IfcWorkControlTypeEnum, 'USERDEFINED', INDETERMINATE) or (workcontroltype == express_getattr(IfcWorkControlTypeEnum, 'USERDEFINED', INDETERMINATE) and exists(express_getattr(self, 'UserDefinedControlType', INDETERMINATE)))) is not False

class IfcZShapeProfileDef_WR21:
    SCOPE = 'entity'
    TYPE_NAME = 'IfcZShapeProfileDef'
    RULE_NAME = 'WR21'

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
        assert (sizeof([temp for temp in express_getattr(express_getattr(self, 'IsGroupedBy', INDETERMINATE), 'RelatedObjects', INDETERMINATE) if not ('ifc2x3.ifczone' in typeof(temp) or 'ifc2x3.ifcspace' in typeof(temp))]) == 0) is not False

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
        count = sizeof([temp for temp in objects if not 'ifc2x3.ifcproduct' in typeof(temp)])
        return count == 0
    elif constraint == express_getattr(IfcObjectTypeEnum, 'PROCESS', INDETERMINATE):
        count = sizeof([temp for temp in objects if not 'ifc2x3.ifcprocess' in typeof(temp)])
        return count == 0
    elif constraint == express_getattr(IfcObjectTypeEnum, 'CONTROL', INDETERMINATE):
        count = sizeof([temp for temp in objects if not 'ifc2x3.ifccontrol' in typeof(temp)])
        return count == 0
    elif constraint == express_getattr(IfcObjectTypeEnum, 'RESOURCE', INDETERMINATE):
        count = sizeof([temp for temp in objects if not 'ifc2x3.ifcresource' in typeof(temp)])
        return count == 0
    elif constraint == express_getattr(IfcObjectTypeEnum, 'ACTOR', INDETERMINATE):
        count = sizeof([temp for temp in objects if not 'ifc2x3.ifcactor' in typeof(temp)])
        return count == 0
    elif constraint == express_getattr(IfcObjectTypeEnum, 'GROUP', INDETERMINATE):
        count = sizeof([temp for temp in objects if not 'ifc2x3.ifcgroup' in typeof(temp)])
        return count == 0
    elif constraint == express_getattr(IfcObjectTypeEnum, 'PROJECT', INDETERMINATE):
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
    namedunitnumber = sizeof([temp for temp in units if 'ifc2x3.ifcnamedunit' in typeof(temp) and (not express_getattr(temp, 'UnitType', INDETERMINATE) == express_getattr(IfcUnitEnum, 'USERDEFINED', INDETERMINATE))])
    derivedunitnumber = sizeof([temp for temp in units if 'ifc2x3.ifcderivedunit' in typeof(temp) and (not express_getattr(temp, 'UnitType', INDETERMINATE) == express_getattr(IfcDerivedUnitEnum, 'USERDEFINED', INDETERMINATE))])
    monetaryunitnumber = sizeof([temp for temp in units if 'ifc2x3.ifcmonetaryunit' in typeof(temp)])
    for i in range(1, sizeof(units) + 1):
        if 'ifc2x3.ifcnamedunit' in typeof(express_getitem(units, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and (not express_getattr(express_getitem(units, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'UnitType', INDETERMINATE) == express_getattr(IfcUnitEnum, 'USERDEFINED', INDETERMINATE)):
            namedunitnames = namedunitnames + express_getattr(express_getitem(units, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'UnitType', INDETERMINATE)
        if 'ifc2x3.ifcderivedunit' in typeof(express_getitem(units, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)) and (not express_getattr(express_getitem(units, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'UnitType', INDETERMINATE) == express_getattr(IfcDerivedUnitEnum, 'USERDEFINED', INDETERMINATE)):
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
    if 'ifc2x3.ifcline' in typeof(curve):
        return express_getattr(express_getattr(curve, 'Pnt', INDETERMINATE), 'Dim', INDETERMINATE)
    if 'ifc2x3.ifcconic' in typeof(curve):
        return express_getattr(express_getattr(curve, 'Position', INDETERMINATE), 'Dim', INDETERMINATE)
    if 'ifc2x3.ifcpolyline' in typeof(curve):
        return express_getattr(express_getitem(express_getattr(curve, 'Points', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)
    if 'ifc2x3.ifctrimmedcurve' in typeof(curve):
        return IfcCurveDim(express_getattr(curve, 'BasisCurve', INDETERMINATE))
    if 'ifc2x3.ifccompositecurve' in typeof(curve):
        return express_getattr(express_getitem(express_getattr(curve, 'Segments', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)
    if 'ifc2x3.ifcbsplinecurve' in typeof(curve):
        return express_getattr(express_getitem(express_getattr(curve, 'ControlPointsList', INDETERMINATE), 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Dim', INDETERMINATE)
    if 'ifc2x3.ifcoffsetcurve2d' in typeof(curve):
        return 2
    if 'ifc2x3.ifcoffsetcurve3d' in typeof(curve):
        return 3
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
    n = sizeof(express_getattr(aloop, 'EdgeList', INDETERMINATE))
    for i in range(2, n + 1):
        p = p and express_getattr(express_getitem(express_getattr(aloop, 'EdgeList', INDETERMINATE), i - 1 - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'EdgeEnd', INDETERMINATE) == express_getattr(express_getitem(express_getattr(aloop, 'EdgeList', INDETERMINATE), i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'EdgeStart', INDETERMINATE)
    return p

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
        ndim = express_getattr(arg, 'Dim', INDETERMINATE)
        if 'ifc2x3.ifcvector' in typeof(arg):
            v.DirectionRatios = express_getattr(express_getattr(arg, 'Orientation', INDETERMINATE), 'DirectionRatios', INDETERMINATE)
            vec.Magnitude = express_getattr(arg, 'Magnitude', INDETERMINATE)
            vec.Orientation = v
            if express_getattr(arg, 'Magnitude', INDETERMINATE) == 0.0:
                return None
            else:
                vec.Magnitude = 1.0
        else:
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
            if 'ifc2x3.ifcvector' in typeof(arg):
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
        if 'ifc2x3.ifcvector' in typeof(vec):
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
    if express_getattr(reptype, 'lower', INDETERMINATE)() == 'curve2d':
        count = sizeof([temp for temp in items if 'ifc2x3.ifccurve' in typeof(temp) and express_getattr(temp, 'Dim', INDETERMINATE) == 2])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'annotation2d':
        count = sizeof([temp for temp in items if sizeof(typeof(temp) * ['ifc2x3.ifcpoint', 'ifc2x3.ifccurve', 'ifc2x3.ifcgeometriccurveset', 'ifc2x3.ifcannotationfillarea', 'ifc2x3.ifcdefinedsymbol', 'ifc2x3.ifctextliteral', 'ifc2x3.ifcdraughtingcallout']) == 1])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'geometricset':
        count = sizeof([temp for temp in items if 'ifc2x3.ifcgeometricset' in typeof(temp) or 'ifc2x3.ifcpoint' in typeof(temp) or 'ifc2x3.ifccurve' in typeof(temp) or ('ifc2x3.ifcsurface' in typeof(temp))])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'geometriccurveset':
        count = sizeof([temp for temp in items if 'ifc2x3.ifcgeometriccurveset' in typeof(temp) or 'ifc2x3.ifcgeometricset' in typeof(temp) or 'ifc2x3.ifcpoint' in typeof(temp) or ('ifc2x3.ifccurve' in typeof(temp))])
        for i in range(1, hiindex(items) + 1):
            if 'ifc2x3.ifcgeometricset' in typeof(express_getitem(items, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE)):
                if sizeof([temp for temp in express_getattr(express_getitem(items, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Elements', INDETERMINATE) if 'ifc2x3.ifcsurface' in typeof(temp)]) > 0:
                    count = count - 1
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'surfacemodel':
        count = sizeof([temp for temp in items if sizeof(['ifc2x3.ifcshellbasedsurfacemodel', 'ifc2x3.ifcfacebasedsurfacemodel', 'ifc2x3.ifcfacetedbrep', 'ifc2x3.ifcfacetedbrepwithvoids'] * typeof(temp)) >= 1])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'solidmodel':
        count = sizeof([temp for temp in items if 'ifc2x3.ifcsolidmodel' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'sweptsolid':
        count = sizeof([temp for temp in items if 'ifc2x3.ifcsweptareasolid' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'csg':
        count = sizeof([temp for temp in items if 'ifc2x3.ifcbooleanresult' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'clipping':
        count = sizeof([temp for temp in items if 'ifc2x3.ifcbooleanclippingresult' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'advancedsweptsolid':
        count = sizeof([temp for temp in items if 'ifc2x3.ifcsurfacecurvesweptareasolid' in typeof(temp) or 'ifc2x3.ifcsweptdisksolid' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'brep':
        count = sizeof([temp for temp in items if 'ifc2x3.ifcfacetedbrep' in typeof(temp) or 'ifc2x3.ifcfacetedbrepwithvoids' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'boundingbox':
        count = sizeof([temp for temp in items if 'ifc2x3.ifcboundingbox' in typeof(temp)])
        if sizeof(items) > 1:
            count = 0
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'sectionedspine':
        count = sizeof([temp for temp in items if 'ifc2x3.ifcsectionedspine' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'mappedrepresentation':
        count = sizeof([temp for temp in items if 'ifc2x3.ifcmappeditem' in typeof(temp)])
    else:
        return None
    return count == sizeof(items)

def IfcTopologyRepresentationTypes(reptype, items):
    count = 0
    if express_getattr(reptype, 'lower', INDETERMINATE)() == 'vertex':
        count = sizeof([temp for temp in items if 'ifc2x3.ifcvertex' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'edge':
        count = sizeof([temp for temp in items if 'ifc2x3.ifcedge' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'path':
        count = sizeof([temp for temp in items if 'ifc2x3.ifcpath' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'face':
        count = sizeof([temp for temp in items if 'ifc2x3.ifcface' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'shell':
        count = sizeof([temp for temp in items if 'ifc2x3.ifcopenshell' in typeof(temp) or 'ifc2x3.ifcclosedshell' in typeof(temp)])
    elif express_getattr(reptype, 'lower', INDETERMINATE)() == 'undefined':
        return True
    else:
        return None
    return count == sizeof(items)

def IfcUniquePropertyName(properties):
    names = express_set([])
    for i in range(1, hiindex(properties) + 1):
        names = names + express_getattr(express_getitem(properties, i - EXPRESS_ONE_BASED_INDEXING, INDETERMINATE), 'Name', INDETERMINATE)
    return sizeof(names) == sizeof(properties)

def IfcValidCalendarDate(date):
    if not 1 <= express_getattr(date, 'DayComponent', INDETERMINATE) <= 31:
        return False
    if express_getattr(date, 'MonthComponent', INDETERMINATE) == 4:
        return 1 <= express_getattr(date, 'DayComponent', INDETERMINATE) <= 30
    elif express_getattr(date, 'MonthComponent', INDETERMINATE) == 6:
        return 1 <= express_getattr(date, 'DayComponent', INDETERMINATE) <= 30
    elif express_getattr(date, 'MonthComponent', INDETERMINATE) == 9:
        return 1 <= express_getattr(date, 'DayComponent', INDETERMINATE) <= 30
    elif express_getattr(date, 'MonthComponent', INDETERMINATE) == 11:
        return 1 <= express_getattr(date, 'DayComponent', INDETERMINATE) <= 30
    elif express_getattr(date, 'MonthComponent', INDETERMINATE) == 2:
        if IfcLeapYear(express_getattr(date, 'YearComponent', INDETERMINATE)):
            return 1 <= express_getattr(date, 'DayComponent', INDETERMINATE) <= 29
        else:
            return 1 <= express_getattr(date, 'DayComponent', INDETERMINATE) <= 28
    else:
        return True

def IfcValidTime(time):
    if exists(express_getattr(time, 'SecondComponent', INDETERMINATE)):
        return exists(express_getattr(time, 'MinuteComponent', INDETERMINATE))
    else:
        return True

def IfcVectorDifference(arg1, arg2):
    if (not exists(arg1) or not exists(arg2)) or express_getattr(arg1, 'Dim', INDETERMINATE) != express_getattr(arg2, 'Dim', INDETERMINATE):
        return None
    else:
        if 'ifc2x3.ifcvector' in typeof(arg1):
            mag1 = express_getattr(arg1, 'Magnitude', INDETERMINATE)
            vec1 = express_getattr(arg1, 'Orientation', INDETERMINATE)
        else:
            mag1 = 1.0
            vec1 = arg1
        if 'ifc2x3.ifcvector' in typeof(arg2):
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
        if 'ifc2x3.ifcvector' in typeof(arg1):
            mag1 = express_getattr(arg1, 'Magnitude', INDETERMINATE)
            vec1 = express_getattr(arg1, 'Orientation', INDETERMINATE)
        else:
            mag1 = 1.0
            vec1 = arg1
        if 'ifc2x3.ifcvector' in typeof(arg2):
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