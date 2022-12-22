import ifcopenshell
def exists(v): return v is not None


sizeof = len
hiindex = len
from math import *

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


def IfcCrossProduct(arg1, arg2):
    
    
    
    
    if ((not exists(arg1)) or (arg1.Dim == 2)) or ((not exists(arg2)) or (arg2.Dim == 2)):
        return None
    else:
        v1 = IfcNormalise(arg1).DirectionRatios
        v2 = IfcNormalise(arg2).DirectionRatios
        res = ifcopenshell.create_entity('IfcDirection', schema='IFC2X3', DirectionRatios=[((v1[2 - 1]) * (v2[3 - 1])) - ((v1[3 - 1]) * (v2[2 - 1])),((v1[3 - 1]) * (v2[1 - 1])) - ((v1[1 - 1]) * (v2[3 - 1])),((v1[1 - 1]) * (v2[2 - 1])) - ((v1[2 - 1]) * (v2[1 - 1]))])
        mag = 0.0
        for i in range(1, 3 + 1):
            mag = mag + ((res.DirectionRatios[i - 1]) * (res.DirectionRatios[i - 1]))
        if mag > 0.0:
            result = ifcopenshell.create_entity('IfcVector', schema='IFC2X3', Orientation=res, Magnitude=sqrt(mag))
        else:
            result = ifcopenshell.create_entity('IfcVector', schema='IFC2X3', Orientation=arg1, Magnitude=0.0)
        return result


def IfcNormalise(arg):
    
    v = ifcopenshell.create_entity('IfcDirection', schema='IFC2X3', DirectionRatios=[1.,0.])
    vec = ifcopenshell.create_entity('IfcVector', schema='IFC2X3', Orientation=ifcopenshell.create_entity('IfcDirection', schema='IFC2X3', DirectionRatios=[1.,0.]), Magnitude=1.)
    
    result = v
    if not exists(arg):
        return None
    else:
        ndim = arg.Dim
        if 'ifc2x3.ifcvector' in typeof(arg):
            v.DirectionRatios = arg.Orientation.DirectionRatios
            vec.Magnitude = arg.Magnitude
            vec.Orientation = v
            if arg.Magnitude == 0.0:
                return None
            else:
                vec.Magnitude = 1.0
        else:
            v.DirectionRatios = arg.DirectionRatios
        mag = 0.0
        for i in range(1, ndim + 1):
            mag = mag + ((v.DirectionRatios[i - 1]) * (v.DirectionRatios[i - 1]))
        if mag > 0.0:
            mag = sqrt(mag)
            for i in range(1, ndim + 1):
                temp = list(v.DirectionRatios)
                temp[i - 1] = (v.DirectionRatios[i - 1]) / mag
                v.DirectionRatios = temp
            if 'ifc2x3.ifcvector' in typeof(arg):
                vec.Orientation = v
                result = vec
            else:
                result = v
        else:
            return None
    return result



class IfcAxis2Placement3D_WR1:
    SCOPE = "entity"
    TYPE_NAME = "IfcAxis2Placement3D"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):
        axis = self.Axis
        refdirection = self.RefDirection
        
        assert self.Location.Dim == 3
        



class IfcAxis2Placement3D_WR2:
    SCOPE = "entity"
    TYPE_NAME = "IfcAxis2Placement3D"
    RULE_NAME = "WR2"

    @staticmethod    
    def __call__(self):
        axis = self.Axis
        refdirection = self.RefDirection
        
        assert (not exists(axis)) or (axis.Dim == 3)
        



class IfcAxis2Placement3D_WR3:
    SCOPE = "entity"
    TYPE_NAME = "IfcAxis2Placement3D"
    RULE_NAME = "WR3"

    @staticmethod    
    def __call__(self):
        axis = self.Axis
        refdirection = self.RefDirection
        
        assert (not exists(refdirection)) or (refdirection.Dim == 3)
        



class IfcAxis2Placement3D_WR4:
    SCOPE = "entity"
    TYPE_NAME = "IfcAxis2Placement3D"
    RULE_NAME = "WR4"

    @staticmethod    
    def __call__(self):
        axis = self.Axis
        refdirection = self.RefDirection
        
        assert (not exists(axis)) or (not exists(refdirection)) or (IfcCrossProduct(axis,refdirection).Magnitude > 0.0)
        



class IfcAxis2Placement3D_WR5:
    SCOPE = "entity"
    TYPE_NAME = "IfcAxis2Placement3D"
    RULE_NAME = "WR5"

    @staticmethod    
    def __call__(self):
        axis = self.Axis
        refdirection = self.RefDirection
        
        assert not exists(axis) ^ exists(refdirection)
        



def calc_IfcAxis2Placement3D_P(self):
    axis = self.Axis
    refdirection = self.RefDirection
    return \
    IfcBuildAxes(axis,refdirection)




class IfcCartesianPoint_WR1:
    SCOPE = "entity"
    TYPE_NAME = "IfcCartesianPoint"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):
        coordinates = self.Coordinates
        
        assert hiindex(coordinates) >= 2
        



def calc_IfcCartesianPoint_Dim(self):
    coordinates = self.Coordinates
    return \
    hiindex(coordinates)




def calc_IfcDirection_Dim(self):
    directionratios = self.DirectionRatios
    return \
    hiindex(directionratios)



