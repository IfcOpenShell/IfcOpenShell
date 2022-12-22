import ifcopenshell
def exists(v): return v is not None


def nvl(v, default): return v if v is not None else default


sizeof = len
hiindex = len
from math import *
unknown = 'UNKNOWN'

class rmult_set(set):
    def __rmul__(self, other):
        return rmult_set(set(other) & self)
    def __repr__(self):
        return repr(set(self))


def typeof(inst):
    schema_name = inst.is_a(True).split('.')[0].lower()
    def inner():
        decl = ifcopenshell.ifcopenshell_wrapper.schema_by_name(schema_name).declaration_by_name(inst.is_a())
        while decl:
            yield '.'.join((schema_name, decl.name().lower()))
            decl = decl.supertype()
    return rmult_set(inner())

class enum_namespace:
    def __getattr__(self, k):
        return k


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


def Ifc2DCompositeCurve(*args, **kwargs): return ifcopenshell.create_entity('Ifc2DCompositeCurve', 'IFC2X3', *args, **kwargs)


def IfcActionRequest(*args, **kwargs): return ifcopenshell.create_entity('IfcActionRequest', 'IFC2X3', *args, **kwargs)


def IfcActor(*args, **kwargs): return ifcopenshell.create_entity('IfcActor', 'IFC2X3', *args, **kwargs)


def IfcActorRole(*args, **kwargs): return ifcopenshell.create_entity('IfcActorRole', 'IFC2X3', *args, **kwargs)


def IfcActuatorType(*args, **kwargs): return ifcopenshell.create_entity('IfcActuatorType', 'IFC2X3', *args, **kwargs)


def IfcAddress(*args, **kwargs): return ifcopenshell.create_entity('IfcAddress', 'IFC2X3', *args, **kwargs)


def IfcAirTerminalBoxType(*args, **kwargs): return ifcopenshell.create_entity('IfcAirTerminalBoxType', 'IFC2X3', *args, **kwargs)


def IfcAirTerminalType(*args, **kwargs): return ifcopenshell.create_entity('IfcAirTerminalType', 'IFC2X3', *args, **kwargs)


def IfcAirToAirHeatRecoveryType(*args, **kwargs): return ifcopenshell.create_entity('IfcAirToAirHeatRecoveryType', 'IFC2X3', *args, **kwargs)


def IfcAlarmType(*args, **kwargs): return ifcopenshell.create_entity('IfcAlarmType', 'IFC2X3', *args, **kwargs)


def IfcAngularDimension(*args, **kwargs): return ifcopenshell.create_entity('IfcAngularDimension', 'IFC2X3', *args, **kwargs)


def IfcAnnotation(*args, **kwargs): return ifcopenshell.create_entity('IfcAnnotation', 'IFC2X3', *args, **kwargs)


def IfcAnnotationCurveOccurrence(*args, **kwargs): return ifcopenshell.create_entity('IfcAnnotationCurveOccurrence', 'IFC2X3', *args, **kwargs)


def IfcAnnotationFillArea(*args, **kwargs): return ifcopenshell.create_entity('IfcAnnotationFillArea', 'IFC2X3', *args, **kwargs)


def IfcAnnotationFillAreaOccurrence(*args, **kwargs): return ifcopenshell.create_entity('IfcAnnotationFillAreaOccurrence', 'IFC2X3', *args, **kwargs)


def IfcAnnotationOccurrence(*args, **kwargs): return ifcopenshell.create_entity('IfcAnnotationOccurrence', 'IFC2X3', *args, **kwargs)


def IfcAnnotationSurface(*args, **kwargs): return ifcopenshell.create_entity('IfcAnnotationSurface', 'IFC2X3', *args, **kwargs)


def IfcAnnotationSurfaceOccurrence(*args, **kwargs): return ifcopenshell.create_entity('IfcAnnotationSurfaceOccurrence', 'IFC2X3', *args, **kwargs)


def IfcAnnotationSymbolOccurrence(*args, **kwargs): return ifcopenshell.create_entity('IfcAnnotationSymbolOccurrence', 'IFC2X3', *args, **kwargs)


def IfcAnnotationTextOccurrence(*args, **kwargs): return ifcopenshell.create_entity('IfcAnnotationTextOccurrence', 'IFC2X3', *args, **kwargs)


def IfcApplication(*args, **kwargs): return ifcopenshell.create_entity('IfcApplication', 'IFC2X3', *args, **kwargs)


def IfcAppliedValue(*args, **kwargs): return ifcopenshell.create_entity('IfcAppliedValue', 'IFC2X3', *args, **kwargs)


def IfcAppliedValueRelationship(*args, **kwargs): return ifcopenshell.create_entity('IfcAppliedValueRelationship', 'IFC2X3', *args, **kwargs)


def IfcApproval(*args, **kwargs): return ifcopenshell.create_entity('IfcApproval', 'IFC2X3', *args, **kwargs)


def IfcApprovalActorRelationship(*args, **kwargs): return ifcopenshell.create_entity('IfcApprovalActorRelationship', 'IFC2X3', *args, **kwargs)


def IfcApprovalPropertyRelationship(*args, **kwargs): return ifcopenshell.create_entity('IfcApprovalPropertyRelationship', 'IFC2X3', *args, **kwargs)


def IfcApprovalRelationship(*args, **kwargs): return ifcopenshell.create_entity('IfcApprovalRelationship', 'IFC2X3', *args, **kwargs)


def IfcArbitraryClosedProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcArbitraryClosedProfileDef', 'IFC2X3', *args, **kwargs)


def IfcArbitraryOpenProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcArbitraryOpenProfileDef', 'IFC2X3', *args, **kwargs)


def IfcArbitraryProfileDefWithVoids(*args, **kwargs): return ifcopenshell.create_entity('IfcArbitraryProfileDefWithVoids', 'IFC2X3', *args, **kwargs)


def IfcAsset(*args, **kwargs): return ifcopenshell.create_entity('IfcAsset', 'IFC2X3', *args, **kwargs)


def IfcAsymmetricIShapeProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcAsymmetricIShapeProfileDef', 'IFC2X3', *args, **kwargs)


def IfcAxis1Placement(*args, **kwargs): return ifcopenshell.create_entity('IfcAxis1Placement', 'IFC2X3', *args, **kwargs)


def IfcAxis2Placement2D(*args, **kwargs): return ifcopenshell.create_entity('IfcAxis2Placement2D', 'IFC2X3', *args, **kwargs)


def IfcAxis2Placement3D(*args, **kwargs): return ifcopenshell.create_entity('IfcAxis2Placement3D', 'IFC2X3', *args, **kwargs)


def IfcBSplineCurve(*args, **kwargs): return ifcopenshell.create_entity('IfcBSplineCurve', 'IFC2X3', *args, **kwargs)


def IfcBeam(*args, **kwargs): return ifcopenshell.create_entity('IfcBeam', 'IFC2X3', *args, **kwargs)


def IfcBeamType(*args, **kwargs): return ifcopenshell.create_entity('IfcBeamType', 'IFC2X3', *args, **kwargs)


def IfcBezierCurve(*args, **kwargs): return ifcopenshell.create_entity('IfcBezierCurve', 'IFC2X3', *args, **kwargs)


def IfcBlobTexture(*args, **kwargs): return ifcopenshell.create_entity('IfcBlobTexture', 'IFC2X3', *args, **kwargs)


def IfcBlock(*args, **kwargs): return ifcopenshell.create_entity('IfcBlock', 'IFC2X3', *args, **kwargs)


def IfcBoilerType(*args, **kwargs): return ifcopenshell.create_entity('IfcBoilerType', 'IFC2X3', *args, **kwargs)


def IfcBooleanClippingResult(*args, **kwargs): return ifcopenshell.create_entity('IfcBooleanClippingResult', 'IFC2X3', *args, **kwargs)


def IfcBooleanResult(*args, **kwargs): return ifcopenshell.create_entity('IfcBooleanResult', 'IFC2X3', *args, **kwargs)


def IfcBoundaryCondition(*args, **kwargs): return ifcopenshell.create_entity('IfcBoundaryCondition', 'IFC2X3', *args, **kwargs)


def IfcBoundaryEdgeCondition(*args, **kwargs): return ifcopenshell.create_entity('IfcBoundaryEdgeCondition', 'IFC2X3', *args, **kwargs)


def IfcBoundaryFaceCondition(*args, **kwargs): return ifcopenshell.create_entity('IfcBoundaryFaceCondition', 'IFC2X3', *args, **kwargs)


def IfcBoundaryNodeCondition(*args, **kwargs): return ifcopenshell.create_entity('IfcBoundaryNodeCondition', 'IFC2X3', *args, **kwargs)


def IfcBoundaryNodeConditionWarping(*args, **kwargs): return ifcopenshell.create_entity('IfcBoundaryNodeConditionWarping', 'IFC2X3', *args, **kwargs)


def IfcBoundedCurve(*args, **kwargs): return ifcopenshell.create_entity('IfcBoundedCurve', 'IFC2X3', *args, **kwargs)


def IfcBoundedSurface(*args, **kwargs): return ifcopenshell.create_entity('IfcBoundedSurface', 'IFC2X3', *args, **kwargs)


def IfcBoundingBox(*args, **kwargs): return ifcopenshell.create_entity('IfcBoundingBox', 'IFC2X3', *args, **kwargs)


def IfcBoxedHalfSpace(*args, **kwargs): return ifcopenshell.create_entity('IfcBoxedHalfSpace', 'IFC2X3', *args, **kwargs)


def IfcBuilding(*args, **kwargs): return ifcopenshell.create_entity('IfcBuilding', 'IFC2X3', *args, **kwargs)


def IfcBuildingElement(*args, **kwargs): return ifcopenshell.create_entity('IfcBuildingElement', 'IFC2X3', *args, **kwargs)


def IfcBuildingElementComponent(*args, **kwargs): return ifcopenshell.create_entity('IfcBuildingElementComponent', 'IFC2X3', *args, **kwargs)


def IfcBuildingElementPart(*args, **kwargs): return ifcopenshell.create_entity('IfcBuildingElementPart', 'IFC2X3', *args, **kwargs)


def IfcBuildingElementProxy(*args, **kwargs): return ifcopenshell.create_entity('IfcBuildingElementProxy', 'IFC2X3', *args, **kwargs)


def IfcBuildingElementProxyType(*args, **kwargs): return ifcopenshell.create_entity('IfcBuildingElementProxyType', 'IFC2X3', *args, **kwargs)


def IfcBuildingElementType(*args, **kwargs): return ifcopenshell.create_entity('IfcBuildingElementType', 'IFC2X3', *args, **kwargs)


def IfcBuildingStorey(*args, **kwargs): return ifcopenshell.create_entity('IfcBuildingStorey', 'IFC2X3', *args, **kwargs)


def IfcCShapeProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcCShapeProfileDef', 'IFC2X3', *args, **kwargs)


def IfcCableCarrierFittingType(*args, **kwargs): return ifcopenshell.create_entity('IfcCableCarrierFittingType', 'IFC2X3', *args, **kwargs)


def IfcCableCarrierSegmentType(*args, **kwargs): return ifcopenshell.create_entity('IfcCableCarrierSegmentType', 'IFC2X3', *args, **kwargs)


def IfcCableSegmentType(*args, **kwargs): return ifcopenshell.create_entity('IfcCableSegmentType', 'IFC2X3', *args, **kwargs)


def IfcCalendarDate(*args, **kwargs): return ifcopenshell.create_entity('IfcCalendarDate', 'IFC2X3', *args, **kwargs)


def IfcCartesianPoint(*args, **kwargs): return ifcopenshell.create_entity('IfcCartesianPoint', 'IFC2X3', *args, **kwargs)


def IfcCartesianTransformationOperator(*args, **kwargs): return ifcopenshell.create_entity('IfcCartesianTransformationOperator', 'IFC2X3', *args, **kwargs)


def IfcCartesianTransformationOperator2D(*args, **kwargs): return ifcopenshell.create_entity('IfcCartesianTransformationOperator2D', 'IFC2X3', *args, **kwargs)


def IfcCartesianTransformationOperator2DnonUniform(*args, **kwargs): return ifcopenshell.create_entity('IfcCartesianTransformationOperator2DnonUniform', 'IFC2X3', *args, **kwargs)


def IfcCartesianTransformationOperator3D(*args, **kwargs): return ifcopenshell.create_entity('IfcCartesianTransformationOperator3D', 'IFC2X3', *args, **kwargs)


def IfcCartesianTransformationOperator3DnonUniform(*args, **kwargs): return ifcopenshell.create_entity('IfcCartesianTransformationOperator3DnonUniform', 'IFC2X3', *args, **kwargs)


def IfcCenterLineProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcCenterLineProfileDef', 'IFC2X3', *args, **kwargs)


def IfcChamferEdgeFeature(*args, **kwargs): return ifcopenshell.create_entity('IfcChamferEdgeFeature', 'IFC2X3', *args, **kwargs)


def IfcChillerType(*args, **kwargs): return ifcopenshell.create_entity('IfcChillerType', 'IFC2X3', *args, **kwargs)


def IfcCircle(*args, **kwargs): return ifcopenshell.create_entity('IfcCircle', 'IFC2X3', *args, **kwargs)


def IfcCircleHollowProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcCircleHollowProfileDef', 'IFC2X3', *args, **kwargs)


def IfcCircleProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcCircleProfileDef', 'IFC2X3', *args, **kwargs)


def IfcClassification(*args, **kwargs): return ifcopenshell.create_entity('IfcClassification', 'IFC2X3', *args, **kwargs)


def IfcClassificationItem(*args, **kwargs): return ifcopenshell.create_entity('IfcClassificationItem', 'IFC2X3', *args, **kwargs)


def IfcClassificationItemRelationship(*args, **kwargs): return ifcopenshell.create_entity('IfcClassificationItemRelationship', 'IFC2X3', *args, **kwargs)


def IfcClassificationNotation(*args, **kwargs): return ifcopenshell.create_entity('IfcClassificationNotation', 'IFC2X3', *args, **kwargs)


def IfcClassificationNotationFacet(*args, **kwargs): return ifcopenshell.create_entity('IfcClassificationNotationFacet', 'IFC2X3', *args, **kwargs)


def IfcClassificationReference(*args, **kwargs): return ifcopenshell.create_entity('IfcClassificationReference', 'IFC2X3', *args, **kwargs)


def IfcClosedShell(*args, **kwargs): return ifcopenshell.create_entity('IfcClosedShell', 'IFC2X3', *args, **kwargs)


def IfcCoilType(*args, **kwargs): return ifcopenshell.create_entity('IfcCoilType', 'IFC2X3', *args, **kwargs)


def IfcColourRgb(*args, **kwargs): return ifcopenshell.create_entity('IfcColourRgb', 'IFC2X3', *args, **kwargs)


def IfcColourSpecification(*args, **kwargs): return ifcopenshell.create_entity('IfcColourSpecification', 'IFC2X3', *args, **kwargs)


def IfcColumn(*args, **kwargs): return ifcopenshell.create_entity('IfcColumn', 'IFC2X3', *args, **kwargs)


def IfcColumnType(*args, **kwargs): return ifcopenshell.create_entity('IfcColumnType', 'IFC2X3', *args, **kwargs)


def IfcComplexProperty(*args, **kwargs): return ifcopenshell.create_entity('IfcComplexProperty', 'IFC2X3', *args, **kwargs)


def IfcCompositeCurve(*args, **kwargs): return ifcopenshell.create_entity('IfcCompositeCurve', 'IFC2X3', *args, **kwargs)


def IfcCompositeCurveSegment(*args, **kwargs): return ifcopenshell.create_entity('IfcCompositeCurveSegment', 'IFC2X3', *args, **kwargs)


def IfcCompositeProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcCompositeProfileDef', 'IFC2X3', *args, **kwargs)


def IfcCompressorType(*args, **kwargs): return ifcopenshell.create_entity('IfcCompressorType', 'IFC2X3', *args, **kwargs)


def IfcCondenserType(*args, **kwargs): return ifcopenshell.create_entity('IfcCondenserType', 'IFC2X3', *args, **kwargs)


def IfcCondition(*args, **kwargs): return ifcopenshell.create_entity('IfcCondition', 'IFC2X3', *args, **kwargs)


def IfcConditionCriterion(*args, **kwargs): return ifcopenshell.create_entity('IfcConditionCriterion', 'IFC2X3', *args, **kwargs)


def IfcConic(*args, **kwargs): return ifcopenshell.create_entity('IfcConic', 'IFC2X3', *args, **kwargs)


def IfcConnectedFaceSet(*args, **kwargs): return ifcopenshell.create_entity('IfcConnectedFaceSet', 'IFC2X3', *args, **kwargs)


def IfcConnectionCurveGeometry(*args, **kwargs): return ifcopenshell.create_entity('IfcConnectionCurveGeometry', 'IFC2X3', *args, **kwargs)


def IfcConnectionGeometry(*args, **kwargs): return ifcopenshell.create_entity('IfcConnectionGeometry', 'IFC2X3', *args, **kwargs)


def IfcConnectionPointEccentricity(*args, **kwargs): return ifcopenshell.create_entity('IfcConnectionPointEccentricity', 'IFC2X3', *args, **kwargs)


def IfcConnectionPointGeometry(*args, **kwargs): return ifcopenshell.create_entity('IfcConnectionPointGeometry', 'IFC2X3', *args, **kwargs)


def IfcConnectionPortGeometry(*args, **kwargs): return ifcopenshell.create_entity('IfcConnectionPortGeometry', 'IFC2X3', *args, **kwargs)


def IfcConnectionSurfaceGeometry(*args, **kwargs): return ifcopenshell.create_entity('IfcConnectionSurfaceGeometry', 'IFC2X3', *args, **kwargs)


def IfcConstraint(*args, **kwargs): return ifcopenshell.create_entity('IfcConstraint', 'IFC2X3', *args, **kwargs)


def IfcConstraintAggregationRelationship(*args, **kwargs): return ifcopenshell.create_entity('IfcConstraintAggregationRelationship', 'IFC2X3', *args, **kwargs)


def IfcConstraintClassificationRelationship(*args, **kwargs): return ifcopenshell.create_entity('IfcConstraintClassificationRelationship', 'IFC2X3', *args, **kwargs)


def IfcConstraintRelationship(*args, **kwargs): return ifcopenshell.create_entity('IfcConstraintRelationship', 'IFC2X3', *args, **kwargs)


def IfcConstructionEquipmentResource(*args, **kwargs): return ifcopenshell.create_entity('IfcConstructionEquipmentResource', 'IFC2X3', *args, **kwargs)


def IfcConstructionMaterialResource(*args, **kwargs): return ifcopenshell.create_entity('IfcConstructionMaterialResource', 'IFC2X3', *args, **kwargs)


def IfcConstructionProductResource(*args, **kwargs): return ifcopenshell.create_entity('IfcConstructionProductResource', 'IFC2X3', *args, **kwargs)


def IfcConstructionResource(*args, **kwargs): return ifcopenshell.create_entity('IfcConstructionResource', 'IFC2X3', *args, **kwargs)


def IfcContextDependentUnit(*args, **kwargs): return ifcopenshell.create_entity('IfcContextDependentUnit', 'IFC2X3', *args, **kwargs)


def IfcControl(*args, **kwargs): return ifcopenshell.create_entity('IfcControl', 'IFC2X3', *args, **kwargs)


def IfcControllerType(*args, **kwargs): return ifcopenshell.create_entity('IfcControllerType', 'IFC2X3', *args, **kwargs)


def IfcConversionBasedUnit(*args, **kwargs): return ifcopenshell.create_entity('IfcConversionBasedUnit', 'IFC2X3', *args, **kwargs)


def IfcCooledBeamType(*args, **kwargs): return ifcopenshell.create_entity('IfcCooledBeamType', 'IFC2X3', *args, **kwargs)


def IfcCoolingTowerType(*args, **kwargs): return ifcopenshell.create_entity('IfcCoolingTowerType', 'IFC2X3', *args, **kwargs)


def IfcCoordinatedUniversalTimeOffset(*args, **kwargs): return ifcopenshell.create_entity('IfcCoordinatedUniversalTimeOffset', 'IFC2X3', *args, **kwargs)


def IfcCostItem(*args, **kwargs): return ifcopenshell.create_entity('IfcCostItem', 'IFC2X3', *args, **kwargs)


def IfcCostSchedule(*args, **kwargs): return ifcopenshell.create_entity('IfcCostSchedule', 'IFC2X3', *args, **kwargs)


def IfcCostValue(*args, **kwargs): return ifcopenshell.create_entity('IfcCostValue', 'IFC2X3', *args, **kwargs)


def IfcCovering(*args, **kwargs): return ifcopenshell.create_entity('IfcCovering', 'IFC2X3', *args, **kwargs)


def IfcCoveringType(*args, **kwargs): return ifcopenshell.create_entity('IfcCoveringType', 'IFC2X3', *args, **kwargs)


def IfcCraneRailAShapeProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcCraneRailAShapeProfileDef', 'IFC2X3', *args, **kwargs)


def IfcCraneRailFShapeProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcCraneRailFShapeProfileDef', 'IFC2X3', *args, **kwargs)


def IfcCrewResource(*args, **kwargs): return ifcopenshell.create_entity('IfcCrewResource', 'IFC2X3', *args, **kwargs)


def IfcCsgPrimitive3D(*args, **kwargs): return ifcopenshell.create_entity('IfcCsgPrimitive3D', 'IFC2X3', *args, **kwargs)


def IfcCsgSolid(*args, **kwargs): return ifcopenshell.create_entity('IfcCsgSolid', 'IFC2X3', *args, **kwargs)


def IfcCurrencyRelationship(*args, **kwargs): return ifcopenshell.create_entity('IfcCurrencyRelationship', 'IFC2X3', *args, **kwargs)


def IfcCurtainWall(*args, **kwargs): return ifcopenshell.create_entity('IfcCurtainWall', 'IFC2X3', *args, **kwargs)


def IfcCurtainWallType(*args, **kwargs): return ifcopenshell.create_entity('IfcCurtainWallType', 'IFC2X3', *args, **kwargs)


def IfcCurve(*args, **kwargs): return ifcopenshell.create_entity('IfcCurve', 'IFC2X3', *args, **kwargs)


def IfcCurveBoundedPlane(*args, **kwargs): return ifcopenshell.create_entity('IfcCurveBoundedPlane', 'IFC2X3', *args, **kwargs)


def IfcCurveStyle(*args, **kwargs): return ifcopenshell.create_entity('IfcCurveStyle', 'IFC2X3', *args, **kwargs)


def IfcCurveStyleFont(*args, **kwargs): return ifcopenshell.create_entity('IfcCurveStyleFont', 'IFC2X3', *args, **kwargs)


def IfcCurveStyleFontAndScaling(*args, **kwargs): return ifcopenshell.create_entity('IfcCurveStyleFontAndScaling', 'IFC2X3', *args, **kwargs)


def IfcCurveStyleFontPattern(*args, **kwargs): return ifcopenshell.create_entity('IfcCurveStyleFontPattern', 'IFC2X3', *args, **kwargs)


def IfcDamperType(*args, **kwargs): return ifcopenshell.create_entity('IfcDamperType', 'IFC2X3', *args, **kwargs)


def IfcDateAndTime(*args, **kwargs): return ifcopenshell.create_entity('IfcDateAndTime', 'IFC2X3', *args, **kwargs)


def IfcDefinedSymbol(*args, **kwargs): return ifcopenshell.create_entity('IfcDefinedSymbol', 'IFC2X3', *args, **kwargs)


def IfcDerivedProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcDerivedProfileDef', 'IFC2X3', *args, **kwargs)


def IfcDerivedUnit(*args, **kwargs): return ifcopenshell.create_entity('IfcDerivedUnit', 'IFC2X3', *args, **kwargs)


def IfcDerivedUnitElement(*args, **kwargs): return ifcopenshell.create_entity('IfcDerivedUnitElement', 'IFC2X3', *args, **kwargs)


def IfcDiameterDimension(*args, **kwargs): return ifcopenshell.create_entity('IfcDiameterDimension', 'IFC2X3', *args, **kwargs)


def IfcDimensionCalloutRelationship(*args, **kwargs): return ifcopenshell.create_entity('IfcDimensionCalloutRelationship', 'IFC2X3', *args, **kwargs)


def IfcDimensionCurve(*args, **kwargs): return ifcopenshell.create_entity('IfcDimensionCurve', 'IFC2X3', *args, **kwargs)


def IfcDimensionCurveDirectedCallout(*args, **kwargs): return ifcopenshell.create_entity('IfcDimensionCurveDirectedCallout', 'IFC2X3', *args, **kwargs)


def IfcDimensionCurveTerminator(*args, **kwargs): return ifcopenshell.create_entity('IfcDimensionCurveTerminator', 'IFC2X3', *args, **kwargs)


def IfcDimensionPair(*args, **kwargs): return ifcopenshell.create_entity('IfcDimensionPair', 'IFC2X3', *args, **kwargs)


def IfcDimensionalExponents(*args, **kwargs): return ifcopenshell.create_entity('IfcDimensionalExponents', 'IFC2X3', *args, **kwargs)


def IfcDirection(*args, **kwargs): return ifcopenshell.create_entity('IfcDirection', 'IFC2X3', *args, **kwargs)


def IfcDiscreteAccessory(*args, **kwargs): return ifcopenshell.create_entity('IfcDiscreteAccessory', 'IFC2X3', *args, **kwargs)


def IfcDiscreteAccessoryType(*args, **kwargs): return ifcopenshell.create_entity('IfcDiscreteAccessoryType', 'IFC2X3', *args, **kwargs)


def IfcDistributionChamberElement(*args, **kwargs): return ifcopenshell.create_entity('IfcDistributionChamberElement', 'IFC2X3', *args, **kwargs)


def IfcDistributionChamberElementType(*args, **kwargs): return ifcopenshell.create_entity('IfcDistributionChamberElementType', 'IFC2X3', *args, **kwargs)


def IfcDistributionControlElement(*args, **kwargs): return ifcopenshell.create_entity('IfcDistributionControlElement', 'IFC2X3', *args, **kwargs)


def IfcDistributionControlElementType(*args, **kwargs): return ifcopenshell.create_entity('IfcDistributionControlElementType', 'IFC2X3', *args, **kwargs)


def IfcDistributionElement(*args, **kwargs): return ifcopenshell.create_entity('IfcDistributionElement', 'IFC2X3', *args, **kwargs)


def IfcDistributionElementType(*args, **kwargs): return ifcopenshell.create_entity('IfcDistributionElementType', 'IFC2X3', *args, **kwargs)


def IfcDistributionFlowElement(*args, **kwargs): return ifcopenshell.create_entity('IfcDistributionFlowElement', 'IFC2X3', *args, **kwargs)


def IfcDistributionFlowElementType(*args, **kwargs): return ifcopenshell.create_entity('IfcDistributionFlowElementType', 'IFC2X3', *args, **kwargs)


def IfcDistributionPort(*args, **kwargs): return ifcopenshell.create_entity('IfcDistributionPort', 'IFC2X3', *args, **kwargs)


def IfcDocumentElectronicFormat(*args, **kwargs): return ifcopenshell.create_entity('IfcDocumentElectronicFormat', 'IFC2X3', *args, **kwargs)


def IfcDocumentInformation(*args, **kwargs): return ifcopenshell.create_entity('IfcDocumentInformation', 'IFC2X3', *args, **kwargs)


def IfcDocumentInformationRelationship(*args, **kwargs): return ifcopenshell.create_entity('IfcDocumentInformationRelationship', 'IFC2X3', *args, **kwargs)


def IfcDocumentReference(*args, **kwargs): return ifcopenshell.create_entity('IfcDocumentReference', 'IFC2X3', *args, **kwargs)


def IfcDoor(*args, **kwargs): return ifcopenshell.create_entity('IfcDoor', 'IFC2X3', *args, **kwargs)


def IfcDoorLiningProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcDoorLiningProperties', 'IFC2X3', *args, **kwargs)


def IfcDoorPanelProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcDoorPanelProperties', 'IFC2X3', *args, **kwargs)


def IfcDoorStyle(*args, **kwargs): return ifcopenshell.create_entity('IfcDoorStyle', 'IFC2X3', *args, **kwargs)


def IfcDraughtingCallout(*args, **kwargs): return ifcopenshell.create_entity('IfcDraughtingCallout', 'IFC2X3', *args, **kwargs)


def IfcDraughtingCalloutRelationship(*args, **kwargs): return ifcopenshell.create_entity('IfcDraughtingCalloutRelationship', 'IFC2X3', *args, **kwargs)


def IfcDraughtingPreDefinedColour(*args, **kwargs): return ifcopenshell.create_entity('IfcDraughtingPreDefinedColour', 'IFC2X3', *args, **kwargs)


def IfcDraughtingPreDefinedCurveFont(*args, **kwargs): return ifcopenshell.create_entity('IfcDraughtingPreDefinedCurveFont', 'IFC2X3', *args, **kwargs)


def IfcDraughtingPreDefinedTextFont(*args, **kwargs): return ifcopenshell.create_entity('IfcDraughtingPreDefinedTextFont', 'IFC2X3', *args, **kwargs)


def IfcDuctFittingType(*args, **kwargs): return ifcopenshell.create_entity('IfcDuctFittingType', 'IFC2X3', *args, **kwargs)


def IfcDuctSegmentType(*args, **kwargs): return ifcopenshell.create_entity('IfcDuctSegmentType', 'IFC2X3', *args, **kwargs)


def IfcDuctSilencerType(*args, **kwargs): return ifcopenshell.create_entity('IfcDuctSilencerType', 'IFC2X3', *args, **kwargs)


def IfcEdge(*args, **kwargs): return ifcopenshell.create_entity('IfcEdge', 'IFC2X3', *args, **kwargs)


def IfcEdgeCurve(*args, **kwargs): return ifcopenshell.create_entity('IfcEdgeCurve', 'IFC2X3', *args, **kwargs)


def IfcEdgeFeature(*args, **kwargs): return ifcopenshell.create_entity('IfcEdgeFeature', 'IFC2X3', *args, **kwargs)


def IfcEdgeLoop(*args, **kwargs): return ifcopenshell.create_entity('IfcEdgeLoop', 'IFC2X3', *args, **kwargs)


def IfcElectricApplianceType(*args, **kwargs): return ifcopenshell.create_entity('IfcElectricApplianceType', 'IFC2X3', *args, **kwargs)


def IfcElectricDistributionPoint(*args, **kwargs): return ifcopenshell.create_entity('IfcElectricDistributionPoint', 'IFC2X3', *args, **kwargs)


def IfcElectricFlowStorageDeviceType(*args, **kwargs): return ifcopenshell.create_entity('IfcElectricFlowStorageDeviceType', 'IFC2X3', *args, **kwargs)


def IfcElectricGeneratorType(*args, **kwargs): return ifcopenshell.create_entity('IfcElectricGeneratorType', 'IFC2X3', *args, **kwargs)


def IfcElectricHeaterType(*args, **kwargs): return ifcopenshell.create_entity('IfcElectricHeaterType', 'IFC2X3', *args, **kwargs)


def IfcElectricMotorType(*args, **kwargs): return ifcopenshell.create_entity('IfcElectricMotorType', 'IFC2X3', *args, **kwargs)


def IfcElectricTimeControlType(*args, **kwargs): return ifcopenshell.create_entity('IfcElectricTimeControlType', 'IFC2X3', *args, **kwargs)


def IfcElectricalBaseProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcElectricalBaseProperties', 'IFC2X3', *args, **kwargs)


def IfcElectricalCircuit(*args, **kwargs): return ifcopenshell.create_entity('IfcElectricalCircuit', 'IFC2X3', *args, **kwargs)


def IfcElectricalElement(*args, **kwargs): return ifcopenshell.create_entity('IfcElectricalElement', 'IFC2X3', *args, **kwargs)


def IfcElement(*args, **kwargs): return ifcopenshell.create_entity('IfcElement', 'IFC2X3', *args, **kwargs)


def IfcElementAssembly(*args, **kwargs): return ifcopenshell.create_entity('IfcElementAssembly', 'IFC2X3', *args, **kwargs)


def IfcElementComponent(*args, **kwargs): return ifcopenshell.create_entity('IfcElementComponent', 'IFC2X3', *args, **kwargs)


def IfcElementComponentType(*args, **kwargs): return ifcopenshell.create_entity('IfcElementComponentType', 'IFC2X3', *args, **kwargs)


def IfcElementQuantity(*args, **kwargs): return ifcopenshell.create_entity('IfcElementQuantity', 'IFC2X3', *args, **kwargs)


def IfcElementType(*args, **kwargs): return ifcopenshell.create_entity('IfcElementType', 'IFC2X3', *args, **kwargs)


def IfcElementarySurface(*args, **kwargs): return ifcopenshell.create_entity('IfcElementarySurface', 'IFC2X3', *args, **kwargs)


def IfcEllipse(*args, **kwargs): return ifcopenshell.create_entity('IfcEllipse', 'IFC2X3', *args, **kwargs)


def IfcEllipseProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcEllipseProfileDef', 'IFC2X3', *args, **kwargs)


def IfcEnergyConversionDevice(*args, **kwargs): return ifcopenshell.create_entity('IfcEnergyConversionDevice', 'IFC2X3', *args, **kwargs)


def IfcEnergyConversionDeviceType(*args, **kwargs): return ifcopenshell.create_entity('IfcEnergyConversionDeviceType', 'IFC2X3', *args, **kwargs)


def IfcEnergyProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcEnergyProperties', 'IFC2X3', *args, **kwargs)


def IfcEnvironmentalImpactValue(*args, **kwargs): return ifcopenshell.create_entity('IfcEnvironmentalImpactValue', 'IFC2X3', *args, **kwargs)


def IfcEquipmentElement(*args, **kwargs): return ifcopenshell.create_entity('IfcEquipmentElement', 'IFC2X3', *args, **kwargs)


def IfcEquipmentStandard(*args, **kwargs): return ifcopenshell.create_entity('IfcEquipmentStandard', 'IFC2X3', *args, **kwargs)


def IfcEvaporativeCoolerType(*args, **kwargs): return ifcopenshell.create_entity('IfcEvaporativeCoolerType', 'IFC2X3', *args, **kwargs)


def IfcEvaporatorType(*args, **kwargs): return ifcopenshell.create_entity('IfcEvaporatorType', 'IFC2X3', *args, **kwargs)


def IfcExtendedMaterialProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcExtendedMaterialProperties', 'IFC2X3', *args, **kwargs)


def IfcExternalReference(*args, **kwargs): return ifcopenshell.create_entity('IfcExternalReference', 'IFC2X3', *args, **kwargs)


def IfcExternallyDefinedHatchStyle(*args, **kwargs): return ifcopenshell.create_entity('IfcExternallyDefinedHatchStyle', 'IFC2X3', *args, **kwargs)


def IfcExternallyDefinedSurfaceStyle(*args, **kwargs): return ifcopenshell.create_entity('IfcExternallyDefinedSurfaceStyle', 'IFC2X3', *args, **kwargs)


def IfcExternallyDefinedSymbol(*args, **kwargs): return ifcopenshell.create_entity('IfcExternallyDefinedSymbol', 'IFC2X3', *args, **kwargs)


def IfcExternallyDefinedTextFont(*args, **kwargs): return ifcopenshell.create_entity('IfcExternallyDefinedTextFont', 'IFC2X3', *args, **kwargs)


def IfcExtrudedAreaSolid(*args, **kwargs): return ifcopenshell.create_entity('IfcExtrudedAreaSolid', 'IFC2X3', *args, **kwargs)


def IfcFace(*args, **kwargs): return ifcopenshell.create_entity('IfcFace', 'IFC2X3', *args, **kwargs)


def IfcFaceBasedSurfaceModel(*args, **kwargs): return ifcopenshell.create_entity('IfcFaceBasedSurfaceModel', 'IFC2X3', *args, **kwargs)


def IfcFaceBound(*args, **kwargs): return ifcopenshell.create_entity('IfcFaceBound', 'IFC2X3', *args, **kwargs)


def IfcFaceOuterBound(*args, **kwargs): return ifcopenshell.create_entity('IfcFaceOuterBound', 'IFC2X3', *args, **kwargs)


def IfcFaceSurface(*args, **kwargs): return ifcopenshell.create_entity('IfcFaceSurface', 'IFC2X3', *args, **kwargs)


def IfcFacetedBrep(*args, **kwargs): return ifcopenshell.create_entity('IfcFacetedBrep', 'IFC2X3', *args, **kwargs)


def IfcFacetedBrepWithVoids(*args, **kwargs): return ifcopenshell.create_entity('IfcFacetedBrepWithVoids', 'IFC2X3', *args, **kwargs)


def IfcFailureConnectionCondition(*args, **kwargs): return ifcopenshell.create_entity('IfcFailureConnectionCondition', 'IFC2X3', *args, **kwargs)


def IfcFanType(*args, **kwargs): return ifcopenshell.create_entity('IfcFanType', 'IFC2X3', *args, **kwargs)


def IfcFastener(*args, **kwargs): return ifcopenshell.create_entity('IfcFastener', 'IFC2X3', *args, **kwargs)


def IfcFastenerType(*args, **kwargs): return ifcopenshell.create_entity('IfcFastenerType', 'IFC2X3', *args, **kwargs)


def IfcFeatureElement(*args, **kwargs): return ifcopenshell.create_entity('IfcFeatureElement', 'IFC2X3', *args, **kwargs)


def IfcFeatureElementAddition(*args, **kwargs): return ifcopenshell.create_entity('IfcFeatureElementAddition', 'IFC2X3', *args, **kwargs)


def IfcFeatureElementSubtraction(*args, **kwargs): return ifcopenshell.create_entity('IfcFeatureElementSubtraction', 'IFC2X3', *args, **kwargs)


def IfcFillAreaStyle(*args, **kwargs): return ifcopenshell.create_entity('IfcFillAreaStyle', 'IFC2X3', *args, **kwargs)


def IfcFillAreaStyleHatching(*args, **kwargs): return ifcopenshell.create_entity('IfcFillAreaStyleHatching', 'IFC2X3', *args, **kwargs)


def IfcFillAreaStyleTileSymbolWithStyle(*args, **kwargs): return ifcopenshell.create_entity('IfcFillAreaStyleTileSymbolWithStyle', 'IFC2X3', *args, **kwargs)


def IfcFillAreaStyleTiles(*args, **kwargs): return ifcopenshell.create_entity('IfcFillAreaStyleTiles', 'IFC2X3', *args, **kwargs)


def IfcFilterType(*args, **kwargs): return ifcopenshell.create_entity('IfcFilterType', 'IFC2X3', *args, **kwargs)


def IfcFireSuppressionTerminalType(*args, **kwargs): return ifcopenshell.create_entity('IfcFireSuppressionTerminalType', 'IFC2X3', *args, **kwargs)


def IfcFlowController(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowController', 'IFC2X3', *args, **kwargs)


def IfcFlowControllerType(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowControllerType', 'IFC2X3', *args, **kwargs)


def IfcFlowFitting(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowFitting', 'IFC2X3', *args, **kwargs)


def IfcFlowFittingType(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowFittingType', 'IFC2X3', *args, **kwargs)


def IfcFlowInstrumentType(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowInstrumentType', 'IFC2X3', *args, **kwargs)


def IfcFlowMeterType(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowMeterType', 'IFC2X3', *args, **kwargs)


def IfcFlowMovingDevice(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowMovingDevice', 'IFC2X3', *args, **kwargs)


def IfcFlowMovingDeviceType(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowMovingDeviceType', 'IFC2X3', *args, **kwargs)


def IfcFlowSegment(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowSegment', 'IFC2X3', *args, **kwargs)


def IfcFlowSegmentType(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowSegmentType', 'IFC2X3', *args, **kwargs)


def IfcFlowStorageDevice(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowStorageDevice', 'IFC2X3', *args, **kwargs)


def IfcFlowStorageDeviceType(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowStorageDeviceType', 'IFC2X3', *args, **kwargs)


def IfcFlowTerminal(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowTerminal', 'IFC2X3', *args, **kwargs)


def IfcFlowTerminalType(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowTerminalType', 'IFC2X3', *args, **kwargs)


def IfcFlowTreatmentDevice(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowTreatmentDevice', 'IFC2X3', *args, **kwargs)


def IfcFlowTreatmentDeviceType(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowTreatmentDeviceType', 'IFC2X3', *args, **kwargs)


def IfcFluidFlowProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcFluidFlowProperties', 'IFC2X3', *args, **kwargs)


def IfcFooting(*args, **kwargs): return ifcopenshell.create_entity('IfcFooting', 'IFC2X3', *args, **kwargs)


def IfcFuelProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcFuelProperties', 'IFC2X3', *args, **kwargs)


def IfcFurnishingElement(*args, **kwargs): return ifcopenshell.create_entity('IfcFurnishingElement', 'IFC2X3', *args, **kwargs)


def IfcFurnishingElementType(*args, **kwargs): return ifcopenshell.create_entity('IfcFurnishingElementType', 'IFC2X3', *args, **kwargs)


def IfcFurnitureStandard(*args, **kwargs): return ifcopenshell.create_entity('IfcFurnitureStandard', 'IFC2X3', *args, **kwargs)


def IfcFurnitureType(*args, **kwargs): return ifcopenshell.create_entity('IfcFurnitureType', 'IFC2X3', *args, **kwargs)


def IfcGasTerminalType(*args, **kwargs): return ifcopenshell.create_entity('IfcGasTerminalType', 'IFC2X3', *args, **kwargs)


def IfcGeneralMaterialProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcGeneralMaterialProperties', 'IFC2X3', *args, **kwargs)


def IfcGeneralProfileProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcGeneralProfileProperties', 'IFC2X3', *args, **kwargs)


def IfcGeometricCurveSet(*args, **kwargs): return ifcopenshell.create_entity('IfcGeometricCurveSet', 'IFC2X3', *args, **kwargs)


def IfcGeometricRepresentationContext(*args, **kwargs): return ifcopenshell.create_entity('IfcGeometricRepresentationContext', 'IFC2X3', *args, **kwargs)


def IfcGeometricRepresentationItem(*args, **kwargs): return ifcopenshell.create_entity('IfcGeometricRepresentationItem', 'IFC2X3', *args, **kwargs)


def IfcGeometricRepresentationSubContext(*args, **kwargs): return ifcopenshell.create_entity('IfcGeometricRepresentationSubContext', 'IFC2X3', *args, **kwargs)


def IfcGeometricSet(*args, **kwargs): return ifcopenshell.create_entity('IfcGeometricSet', 'IFC2X3', *args, **kwargs)


def IfcGrid(*args, **kwargs): return ifcopenshell.create_entity('IfcGrid', 'IFC2X3', *args, **kwargs)


def IfcGridAxis(*args, **kwargs): return ifcopenshell.create_entity('IfcGridAxis', 'IFC2X3', *args, **kwargs)


def IfcGridPlacement(*args, **kwargs): return ifcopenshell.create_entity('IfcGridPlacement', 'IFC2X3', *args, **kwargs)


def IfcGroup(*args, **kwargs): return ifcopenshell.create_entity('IfcGroup', 'IFC2X3', *args, **kwargs)


def IfcHalfSpaceSolid(*args, **kwargs): return ifcopenshell.create_entity('IfcHalfSpaceSolid', 'IFC2X3', *args, **kwargs)


def IfcHeatExchangerType(*args, **kwargs): return ifcopenshell.create_entity('IfcHeatExchangerType', 'IFC2X3', *args, **kwargs)


def IfcHumidifierType(*args, **kwargs): return ifcopenshell.create_entity('IfcHumidifierType', 'IFC2X3', *args, **kwargs)


def IfcHygroscopicMaterialProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcHygroscopicMaterialProperties', 'IFC2X3', *args, **kwargs)


def IfcIShapeProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcIShapeProfileDef', 'IFC2X3', *args, **kwargs)


def IfcImageTexture(*args, **kwargs): return ifcopenshell.create_entity('IfcImageTexture', 'IFC2X3', *args, **kwargs)


def IfcInventory(*args, **kwargs): return ifcopenshell.create_entity('IfcInventory', 'IFC2X3', *args, **kwargs)


def IfcIrregularTimeSeries(*args, **kwargs): return ifcopenshell.create_entity('IfcIrregularTimeSeries', 'IFC2X3', *args, **kwargs)


def IfcIrregularTimeSeriesValue(*args, **kwargs): return ifcopenshell.create_entity('IfcIrregularTimeSeriesValue', 'IFC2X3', *args, **kwargs)


def IfcJunctionBoxType(*args, **kwargs): return ifcopenshell.create_entity('IfcJunctionBoxType', 'IFC2X3', *args, **kwargs)


def IfcLShapeProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcLShapeProfileDef', 'IFC2X3', *args, **kwargs)


def IfcLaborResource(*args, **kwargs): return ifcopenshell.create_entity('IfcLaborResource', 'IFC2X3', *args, **kwargs)


def IfcLampType(*args, **kwargs): return ifcopenshell.create_entity('IfcLampType', 'IFC2X3', *args, **kwargs)


def IfcLibraryInformation(*args, **kwargs): return ifcopenshell.create_entity('IfcLibraryInformation', 'IFC2X3', *args, **kwargs)


def IfcLibraryReference(*args, **kwargs): return ifcopenshell.create_entity('IfcLibraryReference', 'IFC2X3', *args, **kwargs)


def IfcLightDistributionData(*args, **kwargs): return ifcopenshell.create_entity('IfcLightDistributionData', 'IFC2X3', *args, **kwargs)


def IfcLightFixtureType(*args, **kwargs): return ifcopenshell.create_entity('IfcLightFixtureType', 'IFC2X3', *args, **kwargs)


def IfcLightIntensityDistribution(*args, **kwargs): return ifcopenshell.create_entity('IfcLightIntensityDistribution', 'IFC2X3', *args, **kwargs)


def IfcLightSource(*args, **kwargs): return ifcopenshell.create_entity('IfcLightSource', 'IFC2X3', *args, **kwargs)


def IfcLightSourceAmbient(*args, **kwargs): return ifcopenshell.create_entity('IfcLightSourceAmbient', 'IFC2X3', *args, **kwargs)


def IfcLightSourceDirectional(*args, **kwargs): return ifcopenshell.create_entity('IfcLightSourceDirectional', 'IFC2X3', *args, **kwargs)


def IfcLightSourceGoniometric(*args, **kwargs): return ifcopenshell.create_entity('IfcLightSourceGoniometric', 'IFC2X3', *args, **kwargs)


def IfcLightSourcePositional(*args, **kwargs): return ifcopenshell.create_entity('IfcLightSourcePositional', 'IFC2X3', *args, **kwargs)


def IfcLightSourceSpot(*args, **kwargs): return ifcopenshell.create_entity('IfcLightSourceSpot', 'IFC2X3', *args, **kwargs)


def IfcLine(*args, **kwargs): return ifcopenshell.create_entity('IfcLine', 'IFC2X3', *args, **kwargs)


def IfcLinearDimension(*args, **kwargs): return ifcopenshell.create_entity('IfcLinearDimension', 'IFC2X3', *args, **kwargs)


def IfcLocalPlacement(*args, **kwargs): return ifcopenshell.create_entity('IfcLocalPlacement', 'IFC2X3', *args, **kwargs)


def IfcLocalTime(*args, **kwargs): return ifcopenshell.create_entity('IfcLocalTime', 'IFC2X3', *args, **kwargs)


def IfcLoop(*args, **kwargs): return ifcopenshell.create_entity('IfcLoop', 'IFC2X3', *args, **kwargs)


def IfcManifoldSolidBrep(*args, **kwargs): return ifcopenshell.create_entity('IfcManifoldSolidBrep', 'IFC2X3', *args, **kwargs)


def IfcMappedItem(*args, **kwargs): return ifcopenshell.create_entity('IfcMappedItem', 'IFC2X3', *args, **kwargs)


def IfcMaterial(*args, **kwargs): return ifcopenshell.create_entity('IfcMaterial', 'IFC2X3', *args, **kwargs)


def IfcMaterialClassificationRelationship(*args, **kwargs): return ifcopenshell.create_entity('IfcMaterialClassificationRelationship', 'IFC2X3', *args, **kwargs)


def IfcMaterialDefinitionRepresentation(*args, **kwargs): return ifcopenshell.create_entity('IfcMaterialDefinitionRepresentation', 'IFC2X3', *args, **kwargs)


def IfcMaterialLayer(*args, **kwargs): return ifcopenshell.create_entity('IfcMaterialLayer', 'IFC2X3', *args, **kwargs)


def IfcMaterialLayerSet(*args, **kwargs): return ifcopenshell.create_entity('IfcMaterialLayerSet', 'IFC2X3', *args, **kwargs)


def IfcMaterialLayerSetUsage(*args, **kwargs): return ifcopenshell.create_entity('IfcMaterialLayerSetUsage', 'IFC2X3', *args, **kwargs)


def IfcMaterialList(*args, **kwargs): return ifcopenshell.create_entity('IfcMaterialList', 'IFC2X3', *args, **kwargs)


def IfcMaterialProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcMaterialProperties', 'IFC2X3', *args, **kwargs)


def IfcMeasureWithUnit(*args, **kwargs): return ifcopenshell.create_entity('IfcMeasureWithUnit', 'IFC2X3', *args, **kwargs)


def IfcMechanicalConcreteMaterialProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcMechanicalConcreteMaterialProperties', 'IFC2X3', *args, **kwargs)


def IfcMechanicalFastener(*args, **kwargs): return ifcopenshell.create_entity('IfcMechanicalFastener', 'IFC2X3', *args, **kwargs)


def IfcMechanicalFastenerType(*args, **kwargs): return ifcopenshell.create_entity('IfcMechanicalFastenerType', 'IFC2X3', *args, **kwargs)


def IfcMechanicalMaterialProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcMechanicalMaterialProperties', 'IFC2X3', *args, **kwargs)


def IfcMechanicalSteelMaterialProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcMechanicalSteelMaterialProperties', 'IFC2X3', *args, **kwargs)


def IfcMember(*args, **kwargs): return ifcopenshell.create_entity('IfcMember', 'IFC2X3', *args, **kwargs)


def IfcMemberType(*args, **kwargs): return ifcopenshell.create_entity('IfcMemberType', 'IFC2X3', *args, **kwargs)


def IfcMetric(*args, **kwargs): return ifcopenshell.create_entity('IfcMetric', 'IFC2X3', *args, **kwargs)


def IfcMonetaryUnit(*args, **kwargs): return ifcopenshell.create_entity('IfcMonetaryUnit', 'IFC2X3', *args, **kwargs)


def IfcMotorConnectionType(*args, **kwargs): return ifcopenshell.create_entity('IfcMotorConnectionType', 'IFC2X3', *args, **kwargs)


def IfcMove(*args, **kwargs): return ifcopenshell.create_entity('IfcMove', 'IFC2X3', *args, **kwargs)


def IfcNamedUnit(*args, **kwargs): return ifcopenshell.create_entity('IfcNamedUnit', 'IFC2X3', *args, **kwargs)


def IfcObject(*args, **kwargs): return ifcopenshell.create_entity('IfcObject', 'IFC2X3', *args, **kwargs)


def IfcObjectDefinition(*args, **kwargs): return ifcopenshell.create_entity('IfcObjectDefinition', 'IFC2X3', *args, **kwargs)


def IfcObjectPlacement(*args, **kwargs): return ifcopenshell.create_entity('IfcObjectPlacement', 'IFC2X3', *args, **kwargs)


def IfcObjective(*args, **kwargs): return ifcopenshell.create_entity('IfcObjective', 'IFC2X3', *args, **kwargs)


def IfcOccupant(*args, **kwargs): return ifcopenshell.create_entity('IfcOccupant', 'IFC2X3', *args, **kwargs)


def IfcOffsetCurve2D(*args, **kwargs): return ifcopenshell.create_entity('IfcOffsetCurve2D', 'IFC2X3', *args, **kwargs)


def IfcOffsetCurve3D(*args, **kwargs): return ifcopenshell.create_entity('IfcOffsetCurve3D', 'IFC2X3', *args, **kwargs)


def IfcOneDirectionRepeatFactor(*args, **kwargs): return ifcopenshell.create_entity('IfcOneDirectionRepeatFactor', 'IFC2X3', *args, **kwargs)


def IfcOpenShell(*args, **kwargs): return ifcopenshell.create_entity('IfcOpenShell', 'IFC2X3', *args, **kwargs)


def IfcOpeningElement(*args, **kwargs): return ifcopenshell.create_entity('IfcOpeningElement', 'IFC2X3', *args, **kwargs)


def IfcOpticalMaterialProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcOpticalMaterialProperties', 'IFC2X3', *args, **kwargs)


def IfcOrderAction(*args, **kwargs): return ifcopenshell.create_entity('IfcOrderAction', 'IFC2X3', *args, **kwargs)


def IfcOrganization(*args, **kwargs): return ifcopenshell.create_entity('IfcOrganization', 'IFC2X3', *args, **kwargs)


def IfcOrganizationRelationship(*args, **kwargs): return ifcopenshell.create_entity('IfcOrganizationRelationship', 'IFC2X3', *args, **kwargs)


def IfcOrientedEdge(*args, **kwargs): return ifcopenshell.create_entity('IfcOrientedEdge', 'IFC2X3', *args, **kwargs)


def IfcOutletType(*args, **kwargs): return ifcopenshell.create_entity('IfcOutletType', 'IFC2X3', *args, **kwargs)


def IfcOwnerHistory(*args, **kwargs): return ifcopenshell.create_entity('IfcOwnerHistory', 'IFC2X3', *args, **kwargs)


def IfcParameterizedProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcParameterizedProfileDef', 'IFC2X3', *args, **kwargs)


def IfcPath(*args, **kwargs): return ifcopenshell.create_entity('IfcPath', 'IFC2X3', *args, **kwargs)


def IfcPerformanceHistory(*args, **kwargs): return ifcopenshell.create_entity('IfcPerformanceHistory', 'IFC2X3', *args, **kwargs)


def IfcPermeableCoveringProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcPermeableCoveringProperties', 'IFC2X3', *args, **kwargs)


def IfcPermit(*args, **kwargs): return ifcopenshell.create_entity('IfcPermit', 'IFC2X3', *args, **kwargs)


def IfcPerson(*args, **kwargs): return ifcopenshell.create_entity('IfcPerson', 'IFC2X3', *args, **kwargs)


def IfcPersonAndOrganization(*args, **kwargs): return ifcopenshell.create_entity('IfcPersonAndOrganization', 'IFC2X3', *args, **kwargs)


def IfcPhysicalComplexQuantity(*args, **kwargs): return ifcopenshell.create_entity('IfcPhysicalComplexQuantity', 'IFC2X3', *args, **kwargs)


def IfcPhysicalQuantity(*args, **kwargs): return ifcopenshell.create_entity('IfcPhysicalQuantity', 'IFC2X3', *args, **kwargs)


def IfcPhysicalSimpleQuantity(*args, **kwargs): return ifcopenshell.create_entity('IfcPhysicalSimpleQuantity', 'IFC2X3', *args, **kwargs)


def IfcPile(*args, **kwargs): return ifcopenshell.create_entity('IfcPile', 'IFC2X3', *args, **kwargs)


def IfcPipeFittingType(*args, **kwargs): return ifcopenshell.create_entity('IfcPipeFittingType', 'IFC2X3', *args, **kwargs)


def IfcPipeSegmentType(*args, **kwargs): return ifcopenshell.create_entity('IfcPipeSegmentType', 'IFC2X3', *args, **kwargs)


def IfcPixelTexture(*args, **kwargs): return ifcopenshell.create_entity('IfcPixelTexture', 'IFC2X3', *args, **kwargs)


def IfcPlacement(*args, **kwargs): return ifcopenshell.create_entity('IfcPlacement', 'IFC2X3', *args, **kwargs)


def IfcPlanarBox(*args, **kwargs): return ifcopenshell.create_entity('IfcPlanarBox', 'IFC2X3', *args, **kwargs)


def IfcPlanarExtent(*args, **kwargs): return ifcopenshell.create_entity('IfcPlanarExtent', 'IFC2X3', *args, **kwargs)


def IfcPlane(*args, **kwargs): return ifcopenshell.create_entity('IfcPlane', 'IFC2X3', *args, **kwargs)


def IfcPlate(*args, **kwargs): return ifcopenshell.create_entity('IfcPlate', 'IFC2X3', *args, **kwargs)


def IfcPlateType(*args, **kwargs): return ifcopenshell.create_entity('IfcPlateType', 'IFC2X3', *args, **kwargs)


def IfcPoint(*args, **kwargs): return ifcopenshell.create_entity('IfcPoint', 'IFC2X3', *args, **kwargs)


def IfcPointOnCurve(*args, **kwargs): return ifcopenshell.create_entity('IfcPointOnCurve', 'IFC2X3', *args, **kwargs)


def IfcPointOnSurface(*args, **kwargs): return ifcopenshell.create_entity('IfcPointOnSurface', 'IFC2X3', *args, **kwargs)


def IfcPolyLoop(*args, **kwargs): return ifcopenshell.create_entity('IfcPolyLoop', 'IFC2X3', *args, **kwargs)


def IfcPolygonalBoundedHalfSpace(*args, **kwargs): return ifcopenshell.create_entity('IfcPolygonalBoundedHalfSpace', 'IFC2X3', *args, **kwargs)


def IfcPolyline(*args, **kwargs): return ifcopenshell.create_entity('IfcPolyline', 'IFC2X3', *args, **kwargs)


def IfcPort(*args, **kwargs): return ifcopenshell.create_entity('IfcPort', 'IFC2X3', *args, **kwargs)


def IfcPostalAddress(*args, **kwargs): return ifcopenshell.create_entity('IfcPostalAddress', 'IFC2X3', *args, **kwargs)


def IfcPreDefinedColour(*args, **kwargs): return ifcopenshell.create_entity('IfcPreDefinedColour', 'IFC2X3', *args, **kwargs)


def IfcPreDefinedCurveFont(*args, **kwargs): return ifcopenshell.create_entity('IfcPreDefinedCurveFont', 'IFC2X3', *args, **kwargs)


def IfcPreDefinedDimensionSymbol(*args, **kwargs): return ifcopenshell.create_entity('IfcPreDefinedDimensionSymbol', 'IFC2X3', *args, **kwargs)


def IfcPreDefinedItem(*args, **kwargs): return ifcopenshell.create_entity('IfcPreDefinedItem', 'IFC2X3', *args, **kwargs)


def IfcPreDefinedPointMarkerSymbol(*args, **kwargs): return ifcopenshell.create_entity('IfcPreDefinedPointMarkerSymbol', 'IFC2X3', *args, **kwargs)


def IfcPreDefinedSymbol(*args, **kwargs): return ifcopenshell.create_entity('IfcPreDefinedSymbol', 'IFC2X3', *args, **kwargs)


def IfcPreDefinedTerminatorSymbol(*args, **kwargs): return ifcopenshell.create_entity('IfcPreDefinedTerminatorSymbol', 'IFC2X3', *args, **kwargs)


def IfcPreDefinedTextFont(*args, **kwargs): return ifcopenshell.create_entity('IfcPreDefinedTextFont', 'IFC2X3', *args, **kwargs)


def IfcPresentationLayerAssignment(*args, **kwargs): return ifcopenshell.create_entity('IfcPresentationLayerAssignment', 'IFC2X3', *args, **kwargs)


def IfcPresentationLayerWithStyle(*args, **kwargs): return ifcopenshell.create_entity('IfcPresentationLayerWithStyle', 'IFC2X3', *args, **kwargs)


def IfcPresentationStyle(*args, **kwargs): return ifcopenshell.create_entity('IfcPresentationStyle', 'IFC2X3', *args, **kwargs)


def IfcPresentationStyleAssignment(*args, **kwargs): return ifcopenshell.create_entity('IfcPresentationStyleAssignment', 'IFC2X3', *args, **kwargs)


def IfcProcedure(*args, **kwargs): return ifcopenshell.create_entity('IfcProcedure', 'IFC2X3', *args, **kwargs)


def IfcProcess(*args, **kwargs): return ifcopenshell.create_entity('IfcProcess', 'IFC2X3', *args, **kwargs)


def IfcProduct(*args, **kwargs): return ifcopenshell.create_entity('IfcProduct', 'IFC2X3', *args, **kwargs)


def IfcProductDefinitionShape(*args, **kwargs): return ifcopenshell.create_entity('IfcProductDefinitionShape', 'IFC2X3', *args, **kwargs)


def IfcProductRepresentation(*args, **kwargs): return ifcopenshell.create_entity('IfcProductRepresentation', 'IFC2X3', *args, **kwargs)


def IfcProductsOfCombustionProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcProductsOfCombustionProperties', 'IFC2X3', *args, **kwargs)


def IfcProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcProfileDef', 'IFC2X3', *args, **kwargs)


def IfcProfileProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcProfileProperties', 'IFC2X3', *args, **kwargs)


def IfcProject(*args, **kwargs): return ifcopenshell.create_entity('IfcProject', 'IFC2X3', *args, **kwargs)


def IfcProjectOrder(*args, **kwargs): return ifcopenshell.create_entity('IfcProjectOrder', 'IFC2X3', *args, **kwargs)


def IfcProjectOrderRecord(*args, **kwargs): return ifcopenshell.create_entity('IfcProjectOrderRecord', 'IFC2X3', *args, **kwargs)


def IfcProjectionCurve(*args, **kwargs): return ifcopenshell.create_entity('IfcProjectionCurve', 'IFC2X3', *args, **kwargs)


def IfcProjectionElement(*args, **kwargs): return ifcopenshell.create_entity('IfcProjectionElement', 'IFC2X3', *args, **kwargs)


def IfcProperty(*args, **kwargs): return ifcopenshell.create_entity('IfcProperty', 'IFC2X3', *args, **kwargs)


def IfcPropertyBoundedValue(*args, **kwargs): return ifcopenshell.create_entity('IfcPropertyBoundedValue', 'IFC2X3', *args, **kwargs)


def IfcPropertyConstraintRelationship(*args, **kwargs): return ifcopenshell.create_entity('IfcPropertyConstraintRelationship', 'IFC2X3', *args, **kwargs)


def IfcPropertyDefinition(*args, **kwargs): return ifcopenshell.create_entity('IfcPropertyDefinition', 'IFC2X3', *args, **kwargs)


def IfcPropertyDependencyRelationship(*args, **kwargs): return ifcopenshell.create_entity('IfcPropertyDependencyRelationship', 'IFC2X3', *args, **kwargs)


def IfcPropertyEnumeratedValue(*args, **kwargs): return ifcopenshell.create_entity('IfcPropertyEnumeratedValue', 'IFC2X3', *args, **kwargs)


def IfcPropertyEnumeration(*args, **kwargs): return ifcopenshell.create_entity('IfcPropertyEnumeration', 'IFC2X3', *args, **kwargs)


def IfcPropertyListValue(*args, **kwargs): return ifcopenshell.create_entity('IfcPropertyListValue', 'IFC2X3', *args, **kwargs)


def IfcPropertyReferenceValue(*args, **kwargs): return ifcopenshell.create_entity('IfcPropertyReferenceValue', 'IFC2X3', *args, **kwargs)


def IfcPropertySet(*args, **kwargs): return ifcopenshell.create_entity('IfcPropertySet', 'IFC2X3', *args, **kwargs)


def IfcPropertySetDefinition(*args, **kwargs): return ifcopenshell.create_entity('IfcPropertySetDefinition', 'IFC2X3', *args, **kwargs)


def IfcPropertySingleValue(*args, **kwargs): return ifcopenshell.create_entity('IfcPropertySingleValue', 'IFC2X3', *args, **kwargs)


def IfcPropertyTableValue(*args, **kwargs): return ifcopenshell.create_entity('IfcPropertyTableValue', 'IFC2X3', *args, **kwargs)


def IfcProtectiveDeviceType(*args, **kwargs): return ifcopenshell.create_entity('IfcProtectiveDeviceType', 'IFC2X3', *args, **kwargs)


def IfcProxy(*args, **kwargs): return ifcopenshell.create_entity('IfcProxy', 'IFC2X3', *args, **kwargs)


def IfcPumpType(*args, **kwargs): return ifcopenshell.create_entity('IfcPumpType', 'IFC2X3', *args, **kwargs)


def IfcQuantityArea(*args, **kwargs): return ifcopenshell.create_entity('IfcQuantityArea', 'IFC2X3', *args, **kwargs)


def IfcQuantityCount(*args, **kwargs): return ifcopenshell.create_entity('IfcQuantityCount', 'IFC2X3', *args, **kwargs)


def IfcQuantityLength(*args, **kwargs): return ifcopenshell.create_entity('IfcQuantityLength', 'IFC2X3', *args, **kwargs)


def IfcQuantityTime(*args, **kwargs): return ifcopenshell.create_entity('IfcQuantityTime', 'IFC2X3', *args, **kwargs)


def IfcQuantityVolume(*args, **kwargs): return ifcopenshell.create_entity('IfcQuantityVolume', 'IFC2X3', *args, **kwargs)


def IfcQuantityWeight(*args, **kwargs): return ifcopenshell.create_entity('IfcQuantityWeight', 'IFC2X3', *args, **kwargs)


def IfcRadiusDimension(*args, **kwargs): return ifcopenshell.create_entity('IfcRadiusDimension', 'IFC2X3', *args, **kwargs)


def IfcRailing(*args, **kwargs): return ifcopenshell.create_entity('IfcRailing', 'IFC2X3', *args, **kwargs)


def IfcRailingType(*args, **kwargs): return ifcopenshell.create_entity('IfcRailingType', 'IFC2X3', *args, **kwargs)


def IfcRamp(*args, **kwargs): return ifcopenshell.create_entity('IfcRamp', 'IFC2X3', *args, **kwargs)


def IfcRampFlight(*args, **kwargs): return ifcopenshell.create_entity('IfcRampFlight', 'IFC2X3', *args, **kwargs)


def IfcRampFlightType(*args, **kwargs): return ifcopenshell.create_entity('IfcRampFlightType', 'IFC2X3', *args, **kwargs)


def IfcRationalBezierCurve(*args, **kwargs): return ifcopenshell.create_entity('IfcRationalBezierCurve', 'IFC2X3', *args, **kwargs)


def IfcRectangleHollowProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcRectangleHollowProfileDef', 'IFC2X3', *args, **kwargs)


def IfcRectangleProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcRectangleProfileDef', 'IFC2X3', *args, **kwargs)


def IfcRectangularPyramid(*args, **kwargs): return ifcopenshell.create_entity('IfcRectangularPyramid', 'IFC2X3', *args, **kwargs)


def IfcRectangularTrimmedSurface(*args, **kwargs): return ifcopenshell.create_entity('IfcRectangularTrimmedSurface', 'IFC2X3', *args, **kwargs)


def IfcReferencesValueDocument(*args, **kwargs): return ifcopenshell.create_entity('IfcReferencesValueDocument', 'IFC2X3', *args, **kwargs)


def IfcRegularTimeSeries(*args, **kwargs): return ifcopenshell.create_entity('IfcRegularTimeSeries', 'IFC2X3', *args, **kwargs)


def IfcReinforcementBarProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcReinforcementBarProperties', 'IFC2X3', *args, **kwargs)


def IfcReinforcementDefinitionProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcReinforcementDefinitionProperties', 'IFC2X3', *args, **kwargs)


def IfcReinforcingBar(*args, **kwargs): return ifcopenshell.create_entity('IfcReinforcingBar', 'IFC2X3', *args, **kwargs)


def IfcReinforcingElement(*args, **kwargs): return ifcopenshell.create_entity('IfcReinforcingElement', 'IFC2X3', *args, **kwargs)


def IfcReinforcingMesh(*args, **kwargs): return ifcopenshell.create_entity('IfcReinforcingMesh', 'IFC2X3', *args, **kwargs)


def IfcRelAggregates(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAggregates', 'IFC2X3', *args, **kwargs)


def IfcRelAssigns(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssigns', 'IFC2X3', *args, **kwargs)


def IfcRelAssignsTasks(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssignsTasks', 'IFC2X3', *args, **kwargs)


def IfcRelAssignsToActor(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssignsToActor', 'IFC2X3', *args, **kwargs)


def IfcRelAssignsToControl(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssignsToControl', 'IFC2X3', *args, **kwargs)


def IfcRelAssignsToGroup(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssignsToGroup', 'IFC2X3', *args, **kwargs)


def IfcRelAssignsToProcess(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssignsToProcess', 'IFC2X3', *args, **kwargs)


def IfcRelAssignsToProduct(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssignsToProduct', 'IFC2X3', *args, **kwargs)


def IfcRelAssignsToProjectOrder(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssignsToProjectOrder', 'IFC2X3', *args, **kwargs)


def IfcRelAssignsToResource(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssignsToResource', 'IFC2X3', *args, **kwargs)


def IfcRelAssociates(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssociates', 'IFC2X3', *args, **kwargs)


def IfcRelAssociatesAppliedValue(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssociatesAppliedValue', 'IFC2X3', *args, **kwargs)


def IfcRelAssociatesApproval(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssociatesApproval', 'IFC2X3', *args, **kwargs)


def IfcRelAssociatesClassification(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssociatesClassification', 'IFC2X3', *args, **kwargs)


def IfcRelAssociatesConstraint(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssociatesConstraint', 'IFC2X3', *args, **kwargs)


def IfcRelAssociatesDocument(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssociatesDocument', 'IFC2X3', *args, **kwargs)


def IfcRelAssociatesLibrary(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssociatesLibrary', 'IFC2X3', *args, **kwargs)


def IfcRelAssociatesMaterial(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssociatesMaterial', 'IFC2X3', *args, **kwargs)


def IfcRelAssociatesProfileProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssociatesProfileProperties', 'IFC2X3', *args, **kwargs)


def IfcRelConnects(*args, **kwargs): return ifcopenshell.create_entity('IfcRelConnects', 'IFC2X3', *args, **kwargs)


def IfcRelConnectsElements(*args, **kwargs): return ifcopenshell.create_entity('IfcRelConnectsElements', 'IFC2X3', *args, **kwargs)


def IfcRelConnectsPathElements(*args, **kwargs): return ifcopenshell.create_entity('IfcRelConnectsPathElements', 'IFC2X3', *args, **kwargs)


def IfcRelConnectsPortToElement(*args, **kwargs): return ifcopenshell.create_entity('IfcRelConnectsPortToElement', 'IFC2X3', *args, **kwargs)


def IfcRelConnectsPorts(*args, **kwargs): return ifcopenshell.create_entity('IfcRelConnectsPorts', 'IFC2X3', *args, **kwargs)


def IfcRelConnectsStructuralActivity(*args, **kwargs): return ifcopenshell.create_entity('IfcRelConnectsStructuralActivity', 'IFC2X3', *args, **kwargs)


def IfcRelConnectsStructuralElement(*args, **kwargs): return ifcopenshell.create_entity('IfcRelConnectsStructuralElement', 'IFC2X3', *args, **kwargs)


def IfcRelConnectsStructuralMember(*args, **kwargs): return ifcopenshell.create_entity('IfcRelConnectsStructuralMember', 'IFC2X3', *args, **kwargs)


def IfcRelConnectsWithEccentricity(*args, **kwargs): return ifcopenshell.create_entity('IfcRelConnectsWithEccentricity', 'IFC2X3', *args, **kwargs)


def IfcRelConnectsWithRealizingElements(*args, **kwargs): return ifcopenshell.create_entity('IfcRelConnectsWithRealizingElements', 'IFC2X3', *args, **kwargs)


def IfcRelContainedInSpatialStructure(*args, **kwargs): return ifcopenshell.create_entity('IfcRelContainedInSpatialStructure', 'IFC2X3', *args, **kwargs)


def IfcRelCoversBldgElements(*args, **kwargs): return ifcopenshell.create_entity('IfcRelCoversBldgElements', 'IFC2X3', *args, **kwargs)


def IfcRelCoversSpaces(*args, **kwargs): return ifcopenshell.create_entity('IfcRelCoversSpaces', 'IFC2X3', *args, **kwargs)


def IfcRelDecomposes(*args, **kwargs): return ifcopenshell.create_entity('IfcRelDecomposes', 'IFC2X3', *args, **kwargs)


def IfcRelDefines(*args, **kwargs): return ifcopenshell.create_entity('IfcRelDefines', 'IFC2X3', *args, **kwargs)


def IfcRelDefinesByProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcRelDefinesByProperties', 'IFC2X3', *args, **kwargs)


def IfcRelDefinesByType(*args, **kwargs): return ifcopenshell.create_entity('IfcRelDefinesByType', 'IFC2X3', *args, **kwargs)


def IfcRelFillsElement(*args, **kwargs): return ifcopenshell.create_entity('IfcRelFillsElement', 'IFC2X3', *args, **kwargs)


def IfcRelFlowControlElements(*args, **kwargs): return ifcopenshell.create_entity('IfcRelFlowControlElements', 'IFC2X3', *args, **kwargs)


def IfcRelInteractionRequirements(*args, **kwargs): return ifcopenshell.create_entity('IfcRelInteractionRequirements', 'IFC2X3', *args, **kwargs)


def IfcRelNests(*args, **kwargs): return ifcopenshell.create_entity('IfcRelNests', 'IFC2X3', *args, **kwargs)


def IfcRelOccupiesSpaces(*args, **kwargs): return ifcopenshell.create_entity('IfcRelOccupiesSpaces', 'IFC2X3', *args, **kwargs)


def IfcRelOverridesProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcRelOverridesProperties', 'IFC2X3', *args, **kwargs)


def IfcRelProjectsElement(*args, **kwargs): return ifcopenshell.create_entity('IfcRelProjectsElement', 'IFC2X3', *args, **kwargs)


def IfcRelReferencedInSpatialStructure(*args, **kwargs): return ifcopenshell.create_entity('IfcRelReferencedInSpatialStructure', 'IFC2X3', *args, **kwargs)


def IfcRelSchedulesCostItems(*args, **kwargs): return ifcopenshell.create_entity('IfcRelSchedulesCostItems', 'IFC2X3', *args, **kwargs)


def IfcRelSequence(*args, **kwargs): return ifcopenshell.create_entity('IfcRelSequence', 'IFC2X3', *args, **kwargs)


def IfcRelServicesBuildings(*args, **kwargs): return ifcopenshell.create_entity('IfcRelServicesBuildings', 'IFC2X3', *args, **kwargs)


def IfcRelSpaceBoundary(*args, **kwargs): return ifcopenshell.create_entity('IfcRelSpaceBoundary', 'IFC2X3', *args, **kwargs)


def IfcRelVoidsElement(*args, **kwargs): return ifcopenshell.create_entity('IfcRelVoidsElement', 'IFC2X3', *args, **kwargs)


def IfcRelationship(*args, **kwargs): return ifcopenshell.create_entity('IfcRelationship', 'IFC2X3', *args, **kwargs)


def IfcRelaxation(*args, **kwargs): return ifcopenshell.create_entity('IfcRelaxation', 'IFC2X3', *args, **kwargs)


def IfcRepresentation(*args, **kwargs): return ifcopenshell.create_entity('IfcRepresentation', 'IFC2X3', *args, **kwargs)


def IfcRepresentationContext(*args, **kwargs): return ifcopenshell.create_entity('IfcRepresentationContext', 'IFC2X3', *args, **kwargs)


def IfcRepresentationItem(*args, **kwargs): return ifcopenshell.create_entity('IfcRepresentationItem', 'IFC2X3', *args, **kwargs)


def IfcRepresentationMap(*args, **kwargs): return ifcopenshell.create_entity('IfcRepresentationMap', 'IFC2X3', *args, **kwargs)


def IfcResource(*args, **kwargs): return ifcopenshell.create_entity('IfcResource', 'IFC2X3', *args, **kwargs)


def IfcRevolvedAreaSolid(*args, **kwargs): return ifcopenshell.create_entity('IfcRevolvedAreaSolid', 'IFC2X3', *args, **kwargs)


def IfcRibPlateProfileProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcRibPlateProfileProperties', 'IFC2X3', *args, **kwargs)


def IfcRightCircularCone(*args, **kwargs): return ifcopenshell.create_entity('IfcRightCircularCone', 'IFC2X3', *args, **kwargs)


def IfcRightCircularCylinder(*args, **kwargs): return ifcopenshell.create_entity('IfcRightCircularCylinder', 'IFC2X3', *args, **kwargs)


def IfcRoof(*args, **kwargs): return ifcopenshell.create_entity('IfcRoof', 'IFC2X3', *args, **kwargs)


def IfcRoot(*args, **kwargs): return ifcopenshell.create_entity('IfcRoot', 'IFC2X3', *args, **kwargs)


def IfcRoundedEdgeFeature(*args, **kwargs): return ifcopenshell.create_entity('IfcRoundedEdgeFeature', 'IFC2X3', *args, **kwargs)


def IfcRoundedRectangleProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcRoundedRectangleProfileDef', 'IFC2X3', *args, **kwargs)


def IfcSIUnit(*args, **kwargs): return ifcopenshell.create_entity('IfcSIUnit', 'IFC2X3', *args, **kwargs)


def IfcSanitaryTerminalType(*args, **kwargs): return ifcopenshell.create_entity('IfcSanitaryTerminalType', 'IFC2X3', *args, **kwargs)


def IfcScheduleTimeControl(*args, **kwargs): return ifcopenshell.create_entity('IfcScheduleTimeControl', 'IFC2X3', *args, **kwargs)


def IfcSectionProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcSectionProperties', 'IFC2X3', *args, **kwargs)


def IfcSectionReinforcementProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcSectionReinforcementProperties', 'IFC2X3', *args, **kwargs)


def IfcSectionedSpine(*args, **kwargs): return ifcopenshell.create_entity('IfcSectionedSpine', 'IFC2X3', *args, **kwargs)


def IfcSensorType(*args, **kwargs): return ifcopenshell.create_entity('IfcSensorType', 'IFC2X3', *args, **kwargs)


def IfcServiceLife(*args, **kwargs): return ifcopenshell.create_entity('IfcServiceLife', 'IFC2X3', *args, **kwargs)


def IfcServiceLifeFactor(*args, **kwargs): return ifcopenshell.create_entity('IfcServiceLifeFactor', 'IFC2X3', *args, **kwargs)


def IfcShapeAspect(*args, **kwargs): return ifcopenshell.create_entity('IfcShapeAspect', 'IFC2X3', *args, **kwargs)


def IfcShapeModel(*args, **kwargs): return ifcopenshell.create_entity('IfcShapeModel', 'IFC2X3', *args, **kwargs)


def IfcShapeRepresentation(*args, **kwargs): return ifcopenshell.create_entity('IfcShapeRepresentation', 'IFC2X3', *args, **kwargs)


def IfcShellBasedSurfaceModel(*args, **kwargs): return ifcopenshell.create_entity('IfcShellBasedSurfaceModel', 'IFC2X3', *args, **kwargs)


def IfcSimpleProperty(*args, **kwargs): return ifcopenshell.create_entity('IfcSimpleProperty', 'IFC2X3', *args, **kwargs)


def IfcSite(*args, **kwargs): return ifcopenshell.create_entity('IfcSite', 'IFC2X3', *args, **kwargs)


def IfcSlab(*args, **kwargs): return ifcopenshell.create_entity('IfcSlab', 'IFC2X3', *args, **kwargs)


def IfcSlabType(*args, **kwargs): return ifcopenshell.create_entity('IfcSlabType', 'IFC2X3', *args, **kwargs)


def IfcSlippageConnectionCondition(*args, **kwargs): return ifcopenshell.create_entity('IfcSlippageConnectionCondition', 'IFC2X3', *args, **kwargs)


def IfcSolidModel(*args, **kwargs): return ifcopenshell.create_entity('IfcSolidModel', 'IFC2X3', *args, **kwargs)


def IfcSoundProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcSoundProperties', 'IFC2X3', *args, **kwargs)


def IfcSoundValue(*args, **kwargs): return ifcopenshell.create_entity('IfcSoundValue', 'IFC2X3', *args, **kwargs)


def IfcSpace(*args, **kwargs): return ifcopenshell.create_entity('IfcSpace', 'IFC2X3', *args, **kwargs)


def IfcSpaceHeaterType(*args, **kwargs): return ifcopenshell.create_entity('IfcSpaceHeaterType', 'IFC2X3', *args, **kwargs)


def IfcSpaceProgram(*args, **kwargs): return ifcopenshell.create_entity('IfcSpaceProgram', 'IFC2X3', *args, **kwargs)


def IfcSpaceThermalLoadProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcSpaceThermalLoadProperties', 'IFC2X3', *args, **kwargs)


def IfcSpaceType(*args, **kwargs): return ifcopenshell.create_entity('IfcSpaceType', 'IFC2X3', *args, **kwargs)


def IfcSpatialStructureElement(*args, **kwargs): return ifcopenshell.create_entity('IfcSpatialStructureElement', 'IFC2X3', *args, **kwargs)


def IfcSpatialStructureElementType(*args, **kwargs): return ifcopenshell.create_entity('IfcSpatialStructureElementType', 'IFC2X3', *args, **kwargs)


def IfcSphere(*args, **kwargs): return ifcopenshell.create_entity('IfcSphere', 'IFC2X3', *args, **kwargs)


def IfcStackTerminalType(*args, **kwargs): return ifcopenshell.create_entity('IfcStackTerminalType', 'IFC2X3', *args, **kwargs)


def IfcStair(*args, **kwargs): return ifcopenshell.create_entity('IfcStair', 'IFC2X3', *args, **kwargs)


def IfcStairFlight(*args, **kwargs): return ifcopenshell.create_entity('IfcStairFlight', 'IFC2X3', *args, **kwargs)


def IfcStairFlightType(*args, **kwargs): return ifcopenshell.create_entity('IfcStairFlightType', 'IFC2X3', *args, **kwargs)


def IfcStructuralAction(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralAction', 'IFC2X3', *args, **kwargs)


def IfcStructuralActivity(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralActivity', 'IFC2X3', *args, **kwargs)


def IfcStructuralAnalysisModel(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralAnalysisModel', 'IFC2X3', *args, **kwargs)


def IfcStructuralConnection(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralConnection', 'IFC2X3', *args, **kwargs)


def IfcStructuralConnectionCondition(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralConnectionCondition', 'IFC2X3', *args, **kwargs)


def IfcStructuralCurveConnection(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralCurveConnection', 'IFC2X3', *args, **kwargs)


def IfcStructuralCurveMember(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralCurveMember', 'IFC2X3', *args, **kwargs)


def IfcStructuralCurveMemberVarying(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralCurveMemberVarying', 'IFC2X3', *args, **kwargs)


def IfcStructuralItem(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralItem', 'IFC2X3', *args, **kwargs)


def IfcStructuralLinearAction(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralLinearAction', 'IFC2X3', *args, **kwargs)


def IfcStructuralLinearActionVarying(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralLinearActionVarying', 'IFC2X3', *args, **kwargs)


def IfcStructuralLoad(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralLoad', 'IFC2X3', *args, **kwargs)


def IfcStructuralLoadGroup(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralLoadGroup', 'IFC2X3', *args, **kwargs)


def IfcStructuralLoadLinearForce(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralLoadLinearForce', 'IFC2X3', *args, **kwargs)


def IfcStructuralLoadPlanarForce(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralLoadPlanarForce', 'IFC2X3', *args, **kwargs)


def IfcStructuralLoadSingleDisplacement(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralLoadSingleDisplacement', 'IFC2X3', *args, **kwargs)


def IfcStructuralLoadSingleDisplacementDistortion(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralLoadSingleDisplacementDistortion', 'IFC2X3', *args, **kwargs)


def IfcStructuralLoadSingleForce(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralLoadSingleForce', 'IFC2X3', *args, **kwargs)


def IfcStructuralLoadSingleForceWarping(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralLoadSingleForceWarping', 'IFC2X3', *args, **kwargs)


def IfcStructuralLoadStatic(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralLoadStatic', 'IFC2X3', *args, **kwargs)


def IfcStructuralLoadTemperature(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralLoadTemperature', 'IFC2X3', *args, **kwargs)


def IfcStructuralMember(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralMember', 'IFC2X3', *args, **kwargs)


def IfcStructuralPlanarAction(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralPlanarAction', 'IFC2X3', *args, **kwargs)


def IfcStructuralPlanarActionVarying(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralPlanarActionVarying', 'IFC2X3', *args, **kwargs)


def IfcStructuralPointAction(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralPointAction', 'IFC2X3', *args, **kwargs)


def IfcStructuralPointConnection(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralPointConnection', 'IFC2X3', *args, **kwargs)


def IfcStructuralPointReaction(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralPointReaction', 'IFC2X3', *args, **kwargs)


def IfcStructuralProfileProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralProfileProperties', 'IFC2X3', *args, **kwargs)


def IfcStructuralReaction(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralReaction', 'IFC2X3', *args, **kwargs)


def IfcStructuralResultGroup(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralResultGroup', 'IFC2X3', *args, **kwargs)


def IfcStructuralSteelProfileProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralSteelProfileProperties', 'IFC2X3', *args, **kwargs)


def IfcStructuralSurfaceConnection(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralSurfaceConnection', 'IFC2X3', *args, **kwargs)


def IfcStructuralSurfaceMember(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralSurfaceMember', 'IFC2X3', *args, **kwargs)


def IfcStructuralSurfaceMemberVarying(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralSurfaceMemberVarying', 'IFC2X3', *args, **kwargs)


def IfcStructuredDimensionCallout(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuredDimensionCallout', 'IFC2X3', *args, **kwargs)


def IfcStyleModel(*args, **kwargs): return ifcopenshell.create_entity('IfcStyleModel', 'IFC2X3', *args, **kwargs)


def IfcStyledItem(*args, **kwargs): return ifcopenshell.create_entity('IfcStyledItem', 'IFC2X3', *args, **kwargs)


def IfcStyledRepresentation(*args, **kwargs): return ifcopenshell.create_entity('IfcStyledRepresentation', 'IFC2X3', *args, **kwargs)


def IfcSubContractResource(*args, **kwargs): return ifcopenshell.create_entity('IfcSubContractResource', 'IFC2X3', *args, **kwargs)


def IfcSubedge(*args, **kwargs): return ifcopenshell.create_entity('IfcSubedge', 'IFC2X3', *args, **kwargs)


def IfcSurface(*args, **kwargs): return ifcopenshell.create_entity('IfcSurface', 'IFC2X3', *args, **kwargs)


def IfcSurfaceCurveSweptAreaSolid(*args, **kwargs): return ifcopenshell.create_entity('IfcSurfaceCurveSweptAreaSolid', 'IFC2X3', *args, **kwargs)


def IfcSurfaceOfLinearExtrusion(*args, **kwargs): return ifcopenshell.create_entity('IfcSurfaceOfLinearExtrusion', 'IFC2X3', *args, **kwargs)


def IfcSurfaceOfRevolution(*args, **kwargs): return ifcopenshell.create_entity('IfcSurfaceOfRevolution', 'IFC2X3', *args, **kwargs)


def IfcSurfaceStyle(*args, **kwargs): return ifcopenshell.create_entity('IfcSurfaceStyle', 'IFC2X3', *args, **kwargs)


def IfcSurfaceStyleLighting(*args, **kwargs): return ifcopenshell.create_entity('IfcSurfaceStyleLighting', 'IFC2X3', *args, **kwargs)


def IfcSurfaceStyleRefraction(*args, **kwargs): return ifcopenshell.create_entity('IfcSurfaceStyleRefraction', 'IFC2X3', *args, **kwargs)


def IfcSurfaceStyleRendering(*args, **kwargs): return ifcopenshell.create_entity('IfcSurfaceStyleRendering', 'IFC2X3', *args, **kwargs)


def IfcSurfaceStyleShading(*args, **kwargs): return ifcopenshell.create_entity('IfcSurfaceStyleShading', 'IFC2X3', *args, **kwargs)


def IfcSurfaceStyleWithTextures(*args, **kwargs): return ifcopenshell.create_entity('IfcSurfaceStyleWithTextures', 'IFC2X3', *args, **kwargs)


def IfcSurfaceTexture(*args, **kwargs): return ifcopenshell.create_entity('IfcSurfaceTexture', 'IFC2X3', *args, **kwargs)


def IfcSweptAreaSolid(*args, **kwargs): return ifcopenshell.create_entity('IfcSweptAreaSolid', 'IFC2X3', *args, **kwargs)


def IfcSweptDiskSolid(*args, **kwargs): return ifcopenshell.create_entity('IfcSweptDiskSolid', 'IFC2X3', *args, **kwargs)


def IfcSweptSurface(*args, **kwargs): return ifcopenshell.create_entity('IfcSweptSurface', 'IFC2X3', *args, **kwargs)


def IfcSwitchingDeviceType(*args, **kwargs): return ifcopenshell.create_entity('IfcSwitchingDeviceType', 'IFC2X3', *args, **kwargs)


def IfcSymbolStyle(*args, **kwargs): return ifcopenshell.create_entity('IfcSymbolStyle', 'IFC2X3', *args, **kwargs)


def IfcSystem(*args, **kwargs): return ifcopenshell.create_entity('IfcSystem', 'IFC2X3', *args, **kwargs)


def IfcSystemFurnitureElementType(*args, **kwargs): return ifcopenshell.create_entity('IfcSystemFurnitureElementType', 'IFC2X3', *args, **kwargs)


def IfcTShapeProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcTShapeProfileDef', 'IFC2X3', *args, **kwargs)


def IfcTable(*args, **kwargs): return ifcopenshell.create_entity('IfcTable', 'IFC2X3', *args, **kwargs)


def IfcTableRow(*args, **kwargs): return ifcopenshell.create_entity('IfcTableRow', 'IFC2X3', *args, **kwargs)


def IfcTankType(*args, **kwargs): return ifcopenshell.create_entity('IfcTankType', 'IFC2X3', *args, **kwargs)


def IfcTask(*args, **kwargs): return ifcopenshell.create_entity('IfcTask', 'IFC2X3', *args, **kwargs)


def IfcTelecomAddress(*args, **kwargs): return ifcopenshell.create_entity('IfcTelecomAddress', 'IFC2X3', *args, **kwargs)


def IfcTendon(*args, **kwargs): return ifcopenshell.create_entity('IfcTendon', 'IFC2X3', *args, **kwargs)


def IfcTendonAnchor(*args, **kwargs): return ifcopenshell.create_entity('IfcTendonAnchor', 'IFC2X3', *args, **kwargs)


def IfcTerminatorSymbol(*args, **kwargs): return ifcopenshell.create_entity('IfcTerminatorSymbol', 'IFC2X3', *args, **kwargs)


def IfcTextLiteral(*args, **kwargs): return ifcopenshell.create_entity('IfcTextLiteral', 'IFC2X3', *args, **kwargs)


def IfcTextLiteralWithExtent(*args, **kwargs): return ifcopenshell.create_entity('IfcTextLiteralWithExtent', 'IFC2X3', *args, **kwargs)


def IfcTextStyle(*args, **kwargs): return ifcopenshell.create_entity('IfcTextStyle', 'IFC2X3', *args, **kwargs)


def IfcTextStyleFontModel(*args, **kwargs): return ifcopenshell.create_entity('IfcTextStyleFontModel', 'IFC2X3', *args, **kwargs)


def IfcTextStyleForDefinedFont(*args, **kwargs): return ifcopenshell.create_entity('IfcTextStyleForDefinedFont', 'IFC2X3', *args, **kwargs)


def IfcTextStyleTextModel(*args, **kwargs): return ifcopenshell.create_entity('IfcTextStyleTextModel', 'IFC2X3', *args, **kwargs)


def IfcTextStyleWithBoxCharacteristics(*args, **kwargs): return ifcopenshell.create_entity('IfcTextStyleWithBoxCharacteristics', 'IFC2X3', *args, **kwargs)


def IfcTextureCoordinate(*args, **kwargs): return ifcopenshell.create_entity('IfcTextureCoordinate', 'IFC2X3', *args, **kwargs)


def IfcTextureCoordinateGenerator(*args, **kwargs): return ifcopenshell.create_entity('IfcTextureCoordinateGenerator', 'IFC2X3', *args, **kwargs)


def IfcTextureMap(*args, **kwargs): return ifcopenshell.create_entity('IfcTextureMap', 'IFC2X3', *args, **kwargs)


def IfcTextureVertex(*args, **kwargs): return ifcopenshell.create_entity('IfcTextureVertex', 'IFC2X3', *args, **kwargs)


def IfcThermalMaterialProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcThermalMaterialProperties', 'IFC2X3', *args, **kwargs)


def IfcTimeSeries(*args, **kwargs): return ifcopenshell.create_entity('IfcTimeSeries', 'IFC2X3', *args, **kwargs)


def IfcTimeSeriesReferenceRelationship(*args, **kwargs): return ifcopenshell.create_entity('IfcTimeSeriesReferenceRelationship', 'IFC2X3', *args, **kwargs)


def IfcTimeSeriesSchedule(*args, **kwargs): return ifcopenshell.create_entity('IfcTimeSeriesSchedule', 'IFC2X3', *args, **kwargs)


def IfcTimeSeriesValue(*args, **kwargs): return ifcopenshell.create_entity('IfcTimeSeriesValue', 'IFC2X3', *args, **kwargs)


def IfcTopologicalRepresentationItem(*args, **kwargs): return ifcopenshell.create_entity('IfcTopologicalRepresentationItem', 'IFC2X3', *args, **kwargs)


def IfcTopologyRepresentation(*args, **kwargs): return ifcopenshell.create_entity('IfcTopologyRepresentation', 'IFC2X3', *args, **kwargs)


def IfcTransformerType(*args, **kwargs): return ifcopenshell.create_entity('IfcTransformerType', 'IFC2X3', *args, **kwargs)


def IfcTransportElement(*args, **kwargs): return ifcopenshell.create_entity('IfcTransportElement', 'IFC2X3', *args, **kwargs)


def IfcTransportElementType(*args, **kwargs): return ifcopenshell.create_entity('IfcTransportElementType', 'IFC2X3', *args, **kwargs)


def IfcTrapeziumProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcTrapeziumProfileDef', 'IFC2X3', *args, **kwargs)


def IfcTrimmedCurve(*args, **kwargs): return ifcopenshell.create_entity('IfcTrimmedCurve', 'IFC2X3', *args, **kwargs)


def IfcTubeBundleType(*args, **kwargs): return ifcopenshell.create_entity('IfcTubeBundleType', 'IFC2X3', *args, **kwargs)


def IfcTwoDirectionRepeatFactor(*args, **kwargs): return ifcopenshell.create_entity('IfcTwoDirectionRepeatFactor', 'IFC2X3', *args, **kwargs)


def IfcTypeObject(*args, **kwargs): return ifcopenshell.create_entity('IfcTypeObject', 'IFC2X3', *args, **kwargs)


def IfcTypeProduct(*args, **kwargs): return ifcopenshell.create_entity('IfcTypeProduct', 'IFC2X3', *args, **kwargs)


def IfcUShapeProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcUShapeProfileDef', 'IFC2X3', *args, **kwargs)


def IfcUnitAssignment(*args, **kwargs): return ifcopenshell.create_entity('IfcUnitAssignment', 'IFC2X3', *args, **kwargs)


def IfcUnitaryEquipmentType(*args, **kwargs): return ifcopenshell.create_entity('IfcUnitaryEquipmentType', 'IFC2X3', *args, **kwargs)


def IfcValveType(*args, **kwargs): return ifcopenshell.create_entity('IfcValveType', 'IFC2X3', *args, **kwargs)


def IfcVector(*args, **kwargs): return ifcopenshell.create_entity('IfcVector', 'IFC2X3', *args, **kwargs)


def IfcVertex(*args, **kwargs): return ifcopenshell.create_entity('IfcVertex', 'IFC2X3', *args, **kwargs)


def IfcVertexBasedTextureMap(*args, **kwargs): return ifcopenshell.create_entity('IfcVertexBasedTextureMap', 'IFC2X3', *args, **kwargs)


def IfcVertexLoop(*args, **kwargs): return ifcopenshell.create_entity('IfcVertexLoop', 'IFC2X3', *args, **kwargs)


def IfcVertexPoint(*args, **kwargs): return ifcopenshell.create_entity('IfcVertexPoint', 'IFC2X3', *args, **kwargs)


def IfcVibrationIsolatorType(*args, **kwargs): return ifcopenshell.create_entity('IfcVibrationIsolatorType', 'IFC2X3', *args, **kwargs)


def IfcVirtualElement(*args, **kwargs): return ifcopenshell.create_entity('IfcVirtualElement', 'IFC2X3', *args, **kwargs)


def IfcVirtualGridIntersection(*args, **kwargs): return ifcopenshell.create_entity('IfcVirtualGridIntersection', 'IFC2X3', *args, **kwargs)


def IfcWall(*args, **kwargs): return ifcopenshell.create_entity('IfcWall', 'IFC2X3', *args, **kwargs)


def IfcWallStandardCase(*args, **kwargs): return ifcopenshell.create_entity('IfcWallStandardCase', 'IFC2X3', *args, **kwargs)


def IfcWallType(*args, **kwargs): return ifcopenshell.create_entity('IfcWallType', 'IFC2X3', *args, **kwargs)


def IfcWasteTerminalType(*args, **kwargs): return ifcopenshell.create_entity('IfcWasteTerminalType', 'IFC2X3', *args, **kwargs)


def IfcWaterProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcWaterProperties', 'IFC2X3', *args, **kwargs)


def IfcWindow(*args, **kwargs): return ifcopenshell.create_entity('IfcWindow', 'IFC2X3', *args, **kwargs)


def IfcWindowLiningProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcWindowLiningProperties', 'IFC2X3', *args, **kwargs)


def IfcWindowPanelProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcWindowPanelProperties', 'IFC2X3', *args, **kwargs)


def IfcWindowStyle(*args, **kwargs): return ifcopenshell.create_entity('IfcWindowStyle', 'IFC2X3', *args, **kwargs)


def IfcWorkControl(*args, **kwargs): return ifcopenshell.create_entity('IfcWorkControl', 'IFC2X3', *args, **kwargs)


def IfcWorkPlan(*args, **kwargs): return ifcopenshell.create_entity('IfcWorkPlan', 'IFC2X3', *args, **kwargs)


def IfcWorkSchedule(*args, **kwargs): return ifcopenshell.create_entity('IfcWorkSchedule', 'IFC2X3', *args, **kwargs)


def IfcZShapeProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcZShapeProfileDef', 'IFC2X3', *args, **kwargs)


def IfcZone(*args, **kwargs): return ifcopenshell.create_entity('IfcZone', 'IFC2X3', *args, **kwargs)



def calc_IfcSIUnit_Dimensions(self):
    prefix = self.Prefix
    name = self.Name
    return \
    IfcDimensionsForSiUnit(self.Name)




class IfcNamedUnit_WR1:
    SCOPE = "entity"
    TYPE_NAME = "IfcNamedUnit"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):
        dimensions = self.Dimensions
        unittype = self.UnitType
        
        assert IfcCorrectDimensions(self.UnitType,self.Dimensions)
        



def IfcCorrectDimensions(m, dim):

    if m == lengthunit:
        if dim == IfcDimensionalExponents(1,0,0,0,0,0,0):
            return True
        else:
            return False
    if m == massunit:
        if dim == IfcDimensionalExponents(0,1,0,0,0,0,0):
            return True
        else:
            return False
    if m == timeunit:
        if dim == IfcDimensionalExponents(0,0,1,0,0,0,0):
            return True
        else:
            return False
    if m == electriccurrentunit:
        if dim == IfcDimensionalExponents(0,0,0,1,0,0,0):
            return True
        else:
            return False
    if m == thermodynamictemperatureunit:
        if dim == IfcDimensionalExponents(0,0,0,0,1,0,0):
            return True
        else:
            return False
    if m == amountofsubstanceunit:
        if dim == IfcDimensionalExponents(0,0,0,0,0,1,0):
            return True
        else:
            return False
    if m == luminousintensityunit:
        if dim == IfcDimensionalExponents(0,0,0,0,0,0,1):
            return True
        else:
            return False
    if m == planeangleunit:
        if dim == IfcDimensionalExponents(0,0,0,0,0,0,0):
            return True
        else:
            return False
    if m == solidangleunit:
        if dim == IfcDimensionalExponents(0,0,0,0,0,0,0):
            return True
        else:
            return False
    if m == areaunit:
        if dim == IfcDimensionalExponents(2,0,0,0,0,0,0):
            return True
        else:
            return False
    if m == volumeunit:
        if dim == IfcDimensionalExponents(3,0,0,0,0,0,0):
            return True
        else:
            return False
    if m == absorbeddoseunit:
        if dim == IfcDimensionalExponents(2,0,-2,0,0,0,0):
            return True
        else:
            return False
    if m == radioactivityunit:
        if dim == IfcDimensionalExponents(0,0,-1,0,0,0,0):
            return True
        else:
            return False
    if m == electriccapacitanceunit:
        if dim == IfcDimensionalExponents(-2,1,4,1,0,0,0):
            return True
        else:
            return False
    if m == doseequivalentunit:
        if dim == IfcDimensionalExponents(2,0,-2,0,0,0,0):
            return True
        else:
            return False
    if m == electricchargeunit:
        if dim == IfcDimensionalExponents(0,0,1,1,0,0,0):
            return True
        else:
            return False
    if m == electricconductanceunit:
        if dim == IfcDimensionalExponents(-2,-1,3,2,0,0,0):
            return True
        else:
            return False
    if m == electricvoltageunit:
        if dim == IfcDimensionalExponents(2,1,-3,-1,0,0,0):
            return True
        else:
            return False
    if m == electricresistanceunit:
        if dim == IfcDimensionalExponents(2,1,-3,-2,0,0,0):
            return True
        else:
            return False
    if m == energyunit:
        if dim == IfcDimensionalExponents(2,1,-2,0,0,0,0):
            return True
        else:
            return False
    if m == forceunit:
        if dim == IfcDimensionalExponents(1,1,-2,0,0,0,0):
            return True
        else:
            return False
    if m == frequencyunit:
        if dim == IfcDimensionalExponents(0,0,-1,0,0,0,0):
            return True
        else:
            return False
    if m == inductanceunit:
        if dim == IfcDimensionalExponents(2,1,-2,-2,0,0,0):
            return True
        else:
            return False
    if m == illuminanceunit:
        if dim == IfcDimensionalExponents(-2,0,0,0,0,0,1):
            return True
        else:
            return False
    if m == luminousfluxunit:
        if dim == IfcDimensionalExponents(0,0,0,0,0,0,1):
            return True
        else:
            return False
    if m == magneticfluxunit:
        if dim == IfcDimensionalExponents(2,1,-2,-1,0,0,0):
            return True
        else:
            return False
    if m == magneticfluxdensityunit:
        if dim == IfcDimensionalExponents(0,1,-2,-1,0,0,0):
            return True
        else:
            return False
    if m == powerunit:
        if dim == IfcDimensionalExponents(2,1,-3,0,0,0,0):
            return True
        else:
            return False
    if m == pressureunit:
        if dim == IfcDimensionalExponents(-1,1,-2,0,0,0,0):
            return True
        else:
            return False
    return unknown


def IfcDimensionsForSiUnit(n):

    if n == metre:
        return IfcDimensionalExponents(1,0,0,0,0,0,0)
    if n == square_metre:
        return IfcDimensionalExponents(2,0,0,0,0,0,0)
    if n == cubic_metre:
        return IfcDimensionalExponents(3,0,0,0,0,0,0)
    if n == gram:
        return IfcDimensionalExponents(0,1,0,0,0,0,0)
    if n == second:
        return IfcDimensionalExponents(0,0,1,0,0,0,0)
    if n == ampere:
        return IfcDimensionalExponents(0,0,0,1,0,0,0)
    if n == kelvin:
        return IfcDimensionalExponents(0,0,0,0,1,0,0)
    if n == mole:
        return IfcDimensionalExponents(0,0,0,0,0,1,0)
    if n == candela:
        return IfcDimensionalExponents(0,0,0,0,0,0,1)
    if n == radian:
        return IfcDimensionalExponents(0,0,0,0,0,0,0)
    if n == steradian:
        return IfcDimensionalExponents(0,0,0,0,0,0,0)
    if n == hertz:
        return IfcDimensionalExponents(0,0,-1,0,0,0,0)
    if n == newton:
        return IfcDimensionalExponents(1,1,-2,0,0,0,0)
    if n == pascal:
        return IfcDimensionalExponents(-1,1,-2,0,0,0,0)
    if n == joule:
        return IfcDimensionalExponents(2,1,-2,0,0,0,0)
    if n == watt:
        return IfcDimensionalExponents(2,1,-3,0,0,0,0)
    if n == coulomb:
        return IfcDimensionalExponents(0,0,1,1,0,0,0)
    if n == volt:
        return IfcDimensionalExponents(2,1,-3,-1,0,0,0)
    if n == farad:
        return IfcDimensionalExponents(-2,-1,4,1,0,0,0)
    if n == ohm:
        return IfcDimensionalExponents(2,1,-3,-2,0,0,0)
    if n == siemens:
        return IfcDimensionalExponents(-2,-1,3,2,0,0,0)
    if n == weber:
        return IfcDimensionalExponents(2,1,-2,-1,0,0,0)
    if n == tesla:
        return IfcDimensionalExponents(0,1,-2,-1,0,0,0)
    if n == henry:
        return IfcDimensionalExponents(2,1,-2,-2,0,0,0)
    if n == degree_celsius:
        return IfcDimensionalExponents(0,0,0,0,1,0,0)
    if n == lumen:
        return IfcDimensionalExponents(0,0,0,0,0,0,1)
    if n == lux:
        return IfcDimensionalExponents(-2,0,0,0,0,0,1)
    if n == becquerel:
        return IfcDimensionalExponents(0,0,-1,0,0,0,0)
    if n == gray:
        return IfcDimensionalExponents(2,0,-2,0,0,0,0)
    if n == sievert:
        return IfcDimensionalExponents(2,0,-2,0,0,0,0)
    return IfcDimensionalExponents(0,0,0,0,0,0,0)


