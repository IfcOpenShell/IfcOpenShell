import ifcopenshell

def exists(v):
    if callable(v):
        try: return v() is not None
        except IndexError as e: return False
    else: return v is not None



def nvl(v, default): return v if v is not None else default


sizeof = len
hiindex = len
blength = len
loindex = lambda x: 1
from math import *
unknown = 'UNKNOWN'

def usedin(inst, ref_name):
    if inst is None:
        return []
    _, __, attr = ref_name.split('.')
    def filter():
        for ref, attr_idx in inst.wrapped_data.file.get_inverse(inst, allow_duplicate=True, with_attribute_indices=True):
            if ref.wrapped_data.get_attribute_names()[attr_idx].lower() == attr:
                yield ref
    return list(filter())


class express_set(set):
    def __rmul__(self, other):
        return express_set(set(other) & self)
    def __add__(self, other):
        def make_list(v):
            # Comply with 12.6.3 Union operator
            if isinstance(v, (list, tuple, set, express_set)):
                return list(v)
            else:
                return [v]
        return express_set(list(self) + make_list(other))
    __radd__ = __add__
    def __repr__(self):
        return repr(set(self))


def typeof(inst):
    if not inst:
        # If V evaluates to indeterminate (?), an empty set is returned.
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

class enum_namespace:
    def __getattr__(self, k):
        return k.upper()


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


userdefined = IfcBeamTypeEnum.USERDEFINED


notdefined = IfcBeamTypeEnum.NOTDEFINED


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


IfcBuildingElementPartTypeEnum = enum_namespace()


insulation = IfcBuildingElementPartTypeEnum.INSULATION


precastpanel = IfcBuildingElementPartTypeEnum.PRECASTPANEL


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


IfcVibrationIsolatorTypeEnum = enum_namespace()


compression = IfcVibrationIsolatorTypeEnum.COMPRESSION


spring = IfcVibrationIsolatorTypeEnum.SPRING


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


def IfcActionRequest(*args, **kwargs): return ifcopenshell.create_entity('IfcActionRequest', 'IFC4', *args, **kwargs)


def IfcActor(*args, **kwargs): return ifcopenshell.create_entity('IfcActor', 'IFC4', *args, **kwargs)


def IfcActorRole(*args, **kwargs): return ifcopenshell.create_entity('IfcActorRole', 'IFC4', *args, **kwargs)


def IfcActuator(*args, **kwargs): return ifcopenshell.create_entity('IfcActuator', 'IFC4', *args, **kwargs)


def IfcActuatorType(*args, **kwargs): return ifcopenshell.create_entity('IfcActuatorType', 'IFC4', *args, **kwargs)


def IfcAddress(*args, **kwargs): return ifcopenshell.create_entity('IfcAddress', 'IFC4', *args, **kwargs)


def IfcAdvancedBrep(*args, **kwargs): return ifcopenshell.create_entity('IfcAdvancedBrep', 'IFC4', *args, **kwargs)


def IfcAdvancedBrepWithVoids(*args, **kwargs): return ifcopenshell.create_entity('IfcAdvancedBrepWithVoids', 'IFC4', *args, **kwargs)


def IfcAdvancedFace(*args, **kwargs): return ifcopenshell.create_entity('IfcAdvancedFace', 'IFC4', *args, **kwargs)


def IfcAirTerminal(*args, **kwargs): return ifcopenshell.create_entity('IfcAirTerminal', 'IFC4', *args, **kwargs)


def IfcAirTerminalBox(*args, **kwargs): return ifcopenshell.create_entity('IfcAirTerminalBox', 'IFC4', *args, **kwargs)


def IfcAirTerminalBoxType(*args, **kwargs): return ifcopenshell.create_entity('IfcAirTerminalBoxType', 'IFC4', *args, **kwargs)


def IfcAirTerminalType(*args, **kwargs): return ifcopenshell.create_entity('IfcAirTerminalType', 'IFC4', *args, **kwargs)


def IfcAirToAirHeatRecovery(*args, **kwargs): return ifcopenshell.create_entity('IfcAirToAirHeatRecovery', 'IFC4', *args, **kwargs)


def IfcAirToAirHeatRecoveryType(*args, **kwargs): return ifcopenshell.create_entity('IfcAirToAirHeatRecoveryType', 'IFC4', *args, **kwargs)


def IfcAlarm(*args, **kwargs): return ifcopenshell.create_entity('IfcAlarm', 'IFC4', *args, **kwargs)


def IfcAlarmType(*args, **kwargs): return ifcopenshell.create_entity('IfcAlarmType', 'IFC4', *args, **kwargs)


def IfcAnnotation(*args, **kwargs): return ifcopenshell.create_entity('IfcAnnotation', 'IFC4', *args, **kwargs)


def IfcAnnotationFillArea(*args, **kwargs): return ifcopenshell.create_entity('IfcAnnotationFillArea', 'IFC4', *args, **kwargs)


def IfcApplication(*args, **kwargs): return ifcopenshell.create_entity('IfcApplication', 'IFC4', *args, **kwargs)


def IfcAppliedValue(*args, **kwargs): return ifcopenshell.create_entity('IfcAppliedValue', 'IFC4', *args, **kwargs)


def IfcApproval(*args, **kwargs): return ifcopenshell.create_entity('IfcApproval', 'IFC4', *args, **kwargs)


def IfcApprovalRelationship(*args, **kwargs): return ifcopenshell.create_entity('IfcApprovalRelationship', 'IFC4', *args, **kwargs)


def IfcArbitraryClosedProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcArbitraryClosedProfileDef', 'IFC4', *args, **kwargs)


def IfcArbitraryOpenProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcArbitraryOpenProfileDef', 'IFC4', *args, **kwargs)


def IfcArbitraryProfileDefWithVoids(*args, **kwargs): return ifcopenshell.create_entity('IfcArbitraryProfileDefWithVoids', 'IFC4', *args, **kwargs)


def IfcAsset(*args, **kwargs): return ifcopenshell.create_entity('IfcAsset', 'IFC4', *args, **kwargs)


def IfcAsymmetricIShapeProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcAsymmetricIShapeProfileDef', 'IFC4', *args, **kwargs)


def IfcAudioVisualAppliance(*args, **kwargs): return ifcopenshell.create_entity('IfcAudioVisualAppliance', 'IFC4', *args, **kwargs)


def IfcAudioVisualApplianceType(*args, **kwargs): return ifcopenshell.create_entity('IfcAudioVisualApplianceType', 'IFC4', *args, **kwargs)


def IfcAxis1Placement(*args, **kwargs): return ifcopenshell.create_entity('IfcAxis1Placement', 'IFC4', *args, **kwargs)


def IfcAxis2Placement2D(*args, **kwargs): return ifcopenshell.create_entity('IfcAxis2Placement2D', 'IFC4', *args, **kwargs)


def IfcAxis2Placement3D(*args, **kwargs): return ifcopenshell.create_entity('IfcAxis2Placement3D', 'IFC4', *args, **kwargs)


def IfcBSplineCurve(*args, **kwargs): return ifcopenshell.create_entity('IfcBSplineCurve', 'IFC4', *args, **kwargs)


def IfcBSplineCurveWithKnots(*args, **kwargs): return ifcopenshell.create_entity('IfcBSplineCurveWithKnots', 'IFC4', *args, **kwargs)


def IfcBSplineSurface(*args, **kwargs): return ifcopenshell.create_entity('IfcBSplineSurface', 'IFC4', *args, **kwargs)


def IfcBSplineSurfaceWithKnots(*args, **kwargs): return ifcopenshell.create_entity('IfcBSplineSurfaceWithKnots', 'IFC4', *args, **kwargs)


def IfcBeam(*args, **kwargs): return ifcopenshell.create_entity('IfcBeam', 'IFC4', *args, **kwargs)


def IfcBeamStandardCase(*args, **kwargs): return ifcopenshell.create_entity('IfcBeamStandardCase', 'IFC4', *args, **kwargs)


def IfcBeamType(*args, **kwargs): return ifcopenshell.create_entity('IfcBeamType', 'IFC4', *args, **kwargs)


def IfcBlobTexture(*args, **kwargs): return ifcopenshell.create_entity('IfcBlobTexture', 'IFC4', *args, **kwargs)


def IfcBlock(*args, **kwargs): return ifcopenshell.create_entity('IfcBlock', 'IFC4', *args, **kwargs)


def IfcBoiler(*args, **kwargs): return ifcopenshell.create_entity('IfcBoiler', 'IFC4', *args, **kwargs)


def IfcBoilerType(*args, **kwargs): return ifcopenshell.create_entity('IfcBoilerType', 'IFC4', *args, **kwargs)


def IfcBooleanClippingResult(*args, **kwargs): return ifcopenshell.create_entity('IfcBooleanClippingResult', 'IFC4', *args, **kwargs)


def IfcBooleanResult(*args, **kwargs): return ifcopenshell.create_entity('IfcBooleanResult', 'IFC4', *args, **kwargs)


def IfcBoundaryCondition(*args, **kwargs): return ifcopenshell.create_entity('IfcBoundaryCondition', 'IFC4', *args, **kwargs)


def IfcBoundaryCurve(*args, **kwargs): return ifcopenshell.create_entity('IfcBoundaryCurve', 'IFC4', *args, **kwargs)


def IfcBoundaryEdgeCondition(*args, **kwargs): return ifcopenshell.create_entity('IfcBoundaryEdgeCondition', 'IFC4', *args, **kwargs)


def IfcBoundaryFaceCondition(*args, **kwargs): return ifcopenshell.create_entity('IfcBoundaryFaceCondition', 'IFC4', *args, **kwargs)


def IfcBoundaryNodeCondition(*args, **kwargs): return ifcopenshell.create_entity('IfcBoundaryNodeCondition', 'IFC4', *args, **kwargs)


def IfcBoundaryNodeConditionWarping(*args, **kwargs): return ifcopenshell.create_entity('IfcBoundaryNodeConditionWarping', 'IFC4', *args, **kwargs)


def IfcBoundedCurve(*args, **kwargs): return ifcopenshell.create_entity('IfcBoundedCurve', 'IFC4', *args, **kwargs)


def IfcBoundedSurface(*args, **kwargs): return ifcopenshell.create_entity('IfcBoundedSurface', 'IFC4', *args, **kwargs)


def IfcBoundingBox(*args, **kwargs): return ifcopenshell.create_entity('IfcBoundingBox', 'IFC4', *args, **kwargs)


def IfcBoxedHalfSpace(*args, **kwargs): return ifcopenshell.create_entity('IfcBoxedHalfSpace', 'IFC4', *args, **kwargs)


def IfcBuilding(*args, **kwargs): return ifcopenshell.create_entity('IfcBuilding', 'IFC4', *args, **kwargs)


def IfcBuildingElement(*args, **kwargs): return ifcopenshell.create_entity('IfcBuildingElement', 'IFC4', *args, **kwargs)


def IfcBuildingElementPart(*args, **kwargs): return ifcopenshell.create_entity('IfcBuildingElementPart', 'IFC4', *args, **kwargs)


def IfcBuildingElementPartType(*args, **kwargs): return ifcopenshell.create_entity('IfcBuildingElementPartType', 'IFC4', *args, **kwargs)


def IfcBuildingElementProxy(*args, **kwargs): return ifcopenshell.create_entity('IfcBuildingElementProxy', 'IFC4', *args, **kwargs)


def IfcBuildingElementProxyType(*args, **kwargs): return ifcopenshell.create_entity('IfcBuildingElementProxyType', 'IFC4', *args, **kwargs)


def IfcBuildingElementType(*args, **kwargs): return ifcopenshell.create_entity('IfcBuildingElementType', 'IFC4', *args, **kwargs)


def IfcBuildingStorey(*args, **kwargs): return ifcopenshell.create_entity('IfcBuildingStorey', 'IFC4', *args, **kwargs)


def IfcBuildingSystem(*args, **kwargs): return ifcopenshell.create_entity('IfcBuildingSystem', 'IFC4', *args, **kwargs)


def IfcBurner(*args, **kwargs): return ifcopenshell.create_entity('IfcBurner', 'IFC4', *args, **kwargs)


def IfcBurnerType(*args, **kwargs): return ifcopenshell.create_entity('IfcBurnerType', 'IFC4', *args, **kwargs)


def IfcCShapeProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcCShapeProfileDef', 'IFC4', *args, **kwargs)


def IfcCableCarrierFitting(*args, **kwargs): return ifcopenshell.create_entity('IfcCableCarrierFitting', 'IFC4', *args, **kwargs)


def IfcCableCarrierFittingType(*args, **kwargs): return ifcopenshell.create_entity('IfcCableCarrierFittingType', 'IFC4', *args, **kwargs)


def IfcCableCarrierSegment(*args, **kwargs): return ifcopenshell.create_entity('IfcCableCarrierSegment', 'IFC4', *args, **kwargs)


def IfcCableCarrierSegmentType(*args, **kwargs): return ifcopenshell.create_entity('IfcCableCarrierSegmentType', 'IFC4', *args, **kwargs)


def IfcCableFitting(*args, **kwargs): return ifcopenshell.create_entity('IfcCableFitting', 'IFC4', *args, **kwargs)


def IfcCableFittingType(*args, **kwargs): return ifcopenshell.create_entity('IfcCableFittingType', 'IFC4', *args, **kwargs)


def IfcCableSegment(*args, **kwargs): return ifcopenshell.create_entity('IfcCableSegment', 'IFC4', *args, **kwargs)


def IfcCableSegmentType(*args, **kwargs): return ifcopenshell.create_entity('IfcCableSegmentType', 'IFC4', *args, **kwargs)


def IfcCartesianPoint(*args, **kwargs): return ifcopenshell.create_entity('IfcCartesianPoint', 'IFC4', *args, **kwargs)


def IfcCartesianPointList(*args, **kwargs): return ifcopenshell.create_entity('IfcCartesianPointList', 'IFC4', *args, **kwargs)


def IfcCartesianPointList2D(*args, **kwargs): return ifcopenshell.create_entity('IfcCartesianPointList2D', 'IFC4', *args, **kwargs)


def IfcCartesianPointList3D(*args, **kwargs): return ifcopenshell.create_entity('IfcCartesianPointList3D', 'IFC4', *args, **kwargs)


def IfcCartesianTransformationOperator(*args, **kwargs): return ifcopenshell.create_entity('IfcCartesianTransformationOperator', 'IFC4', *args, **kwargs)


def IfcCartesianTransformationOperator2D(*args, **kwargs): return ifcopenshell.create_entity('IfcCartesianTransformationOperator2D', 'IFC4', *args, **kwargs)


def IfcCartesianTransformationOperator2DnonUniform(*args, **kwargs): return ifcopenshell.create_entity('IfcCartesianTransformationOperator2DnonUniform', 'IFC4', *args, **kwargs)


def IfcCartesianTransformationOperator3D(*args, **kwargs): return ifcopenshell.create_entity('IfcCartesianTransformationOperator3D', 'IFC4', *args, **kwargs)


def IfcCartesianTransformationOperator3DnonUniform(*args, **kwargs): return ifcopenshell.create_entity('IfcCartesianTransformationOperator3DnonUniform', 'IFC4', *args, **kwargs)


def IfcCenterLineProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcCenterLineProfileDef', 'IFC4', *args, **kwargs)


def IfcChiller(*args, **kwargs): return ifcopenshell.create_entity('IfcChiller', 'IFC4', *args, **kwargs)


def IfcChillerType(*args, **kwargs): return ifcopenshell.create_entity('IfcChillerType', 'IFC4', *args, **kwargs)


def IfcChimney(*args, **kwargs): return ifcopenshell.create_entity('IfcChimney', 'IFC4', *args, **kwargs)


def IfcChimneyType(*args, **kwargs): return ifcopenshell.create_entity('IfcChimneyType', 'IFC4', *args, **kwargs)


def IfcCircle(*args, **kwargs): return ifcopenshell.create_entity('IfcCircle', 'IFC4', *args, **kwargs)


def IfcCircleHollowProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcCircleHollowProfileDef', 'IFC4', *args, **kwargs)


def IfcCircleProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcCircleProfileDef', 'IFC4', *args, **kwargs)


def IfcCivilElement(*args, **kwargs): return ifcopenshell.create_entity('IfcCivilElement', 'IFC4', *args, **kwargs)


def IfcCivilElementType(*args, **kwargs): return ifcopenshell.create_entity('IfcCivilElementType', 'IFC4', *args, **kwargs)


def IfcClassification(*args, **kwargs): return ifcopenshell.create_entity('IfcClassification', 'IFC4', *args, **kwargs)


def IfcClassificationReference(*args, **kwargs): return ifcopenshell.create_entity('IfcClassificationReference', 'IFC4', *args, **kwargs)


def IfcClosedShell(*args, **kwargs): return ifcopenshell.create_entity('IfcClosedShell', 'IFC4', *args, **kwargs)


def IfcCoil(*args, **kwargs): return ifcopenshell.create_entity('IfcCoil', 'IFC4', *args, **kwargs)


def IfcCoilType(*args, **kwargs): return ifcopenshell.create_entity('IfcCoilType', 'IFC4', *args, **kwargs)


def IfcColourRgb(*args, **kwargs): return ifcopenshell.create_entity('IfcColourRgb', 'IFC4', *args, **kwargs)


def IfcColourRgbList(*args, **kwargs): return ifcopenshell.create_entity('IfcColourRgbList', 'IFC4', *args, **kwargs)


def IfcColourSpecification(*args, **kwargs): return ifcopenshell.create_entity('IfcColourSpecification', 'IFC4', *args, **kwargs)


def IfcColumn(*args, **kwargs): return ifcopenshell.create_entity('IfcColumn', 'IFC4', *args, **kwargs)


def IfcColumnStandardCase(*args, **kwargs): return ifcopenshell.create_entity('IfcColumnStandardCase', 'IFC4', *args, **kwargs)


def IfcColumnType(*args, **kwargs): return ifcopenshell.create_entity('IfcColumnType', 'IFC4', *args, **kwargs)


def IfcCommunicationsAppliance(*args, **kwargs): return ifcopenshell.create_entity('IfcCommunicationsAppliance', 'IFC4', *args, **kwargs)


def IfcCommunicationsApplianceType(*args, **kwargs): return ifcopenshell.create_entity('IfcCommunicationsApplianceType', 'IFC4', *args, **kwargs)


def IfcComplexProperty(*args, **kwargs): return ifcopenshell.create_entity('IfcComplexProperty', 'IFC4', *args, **kwargs)


def IfcComplexPropertyTemplate(*args, **kwargs): return ifcopenshell.create_entity('IfcComplexPropertyTemplate', 'IFC4', *args, **kwargs)


def IfcCompositeCurve(*args, **kwargs): return ifcopenshell.create_entity('IfcCompositeCurve', 'IFC4', *args, **kwargs)


def IfcCompositeCurveOnSurface(*args, **kwargs): return ifcopenshell.create_entity('IfcCompositeCurveOnSurface', 'IFC4', *args, **kwargs)


def IfcCompositeCurveSegment(*args, **kwargs): return ifcopenshell.create_entity('IfcCompositeCurveSegment', 'IFC4', *args, **kwargs)


def IfcCompositeProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcCompositeProfileDef', 'IFC4', *args, **kwargs)


def IfcCompressor(*args, **kwargs): return ifcopenshell.create_entity('IfcCompressor', 'IFC4', *args, **kwargs)


def IfcCompressorType(*args, **kwargs): return ifcopenshell.create_entity('IfcCompressorType', 'IFC4', *args, **kwargs)


def IfcCondenser(*args, **kwargs): return ifcopenshell.create_entity('IfcCondenser', 'IFC4', *args, **kwargs)


def IfcCondenserType(*args, **kwargs): return ifcopenshell.create_entity('IfcCondenserType', 'IFC4', *args, **kwargs)


def IfcConic(*args, **kwargs): return ifcopenshell.create_entity('IfcConic', 'IFC4', *args, **kwargs)


def IfcConnectedFaceSet(*args, **kwargs): return ifcopenshell.create_entity('IfcConnectedFaceSet', 'IFC4', *args, **kwargs)


def IfcConnectionCurveGeometry(*args, **kwargs): return ifcopenshell.create_entity('IfcConnectionCurveGeometry', 'IFC4', *args, **kwargs)


def IfcConnectionGeometry(*args, **kwargs): return ifcopenshell.create_entity('IfcConnectionGeometry', 'IFC4', *args, **kwargs)


def IfcConnectionPointEccentricity(*args, **kwargs): return ifcopenshell.create_entity('IfcConnectionPointEccentricity', 'IFC4', *args, **kwargs)


def IfcConnectionPointGeometry(*args, **kwargs): return ifcopenshell.create_entity('IfcConnectionPointGeometry', 'IFC4', *args, **kwargs)


def IfcConnectionSurfaceGeometry(*args, **kwargs): return ifcopenshell.create_entity('IfcConnectionSurfaceGeometry', 'IFC4', *args, **kwargs)


def IfcConnectionVolumeGeometry(*args, **kwargs): return ifcopenshell.create_entity('IfcConnectionVolumeGeometry', 'IFC4', *args, **kwargs)


def IfcConstraint(*args, **kwargs): return ifcopenshell.create_entity('IfcConstraint', 'IFC4', *args, **kwargs)


def IfcConstructionEquipmentResource(*args, **kwargs): return ifcopenshell.create_entity('IfcConstructionEquipmentResource', 'IFC4', *args, **kwargs)


def IfcConstructionEquipmentResourceType(*args, **kwargs): return ifcopenshell.create_entity('IfcConstructionEquipmentResourceType', 'IFC4', *args, **kwargs)


def IfcConstructionMaterialResource(*args, **kwargs): return ifcopenshell.create_entity('IfcConstructionMaterialResource', 'IFC4', *args, **kwargs)


def IfcConstructionMaterialResourceType(*args, **kwargs): return ifcopenshell.create_entity('IfcConstructionMaterialResourceType', 'IFC4', *args, **kwargs)


def IfcConstructionProductResource(*args, **kwargs): return ifcopenshell.create_entity('IfcConstructionProductResource', 'IFC4', *args, **kwargs)


def IfcConstructionProductResourceType(*args, **kwargs): return ifcopenshell.create_entity('IfcConstructionProductResourceType', 'IFC4', *args, **kwargs)


def IfcConstructionResource(*args, **kwargs): return ifcopenshell.create_entity('IfcConstructionResource', 'IFC4', *args, **kwargs)


def IfcConstructionResourceType(*args, **kwargs): return ifcopenshell.create_entity('IfcConstructionResourceType', 'IFC4', *args, **kwargs)


def IfcContext(*args, **kwargs): return ifcopenshell.create_entity('IfcContext', 'IFC4', *args, **kwargs)


def IfcContextDependentUnit(*args, **kwargs): return ifcopenshell.create_entity('IfcContextDependentUnit', 'IFC4', *args, **kwargs)


def IfcControl(*args, **kwargs): return ifcopenshell.create_entity('IfcControl', 'IFC4', *args, **kwargs)


def IfcController(*args, **kwargs): return ifcopenshell.create_entity('IfcController', 'IFC4', *args, **kwargs)


def IfcControllerType(*args, **kwargs): return ifcopenshell.create_entity('IfcControllerType', 'IFC4', *args, **kwargs)


def IfcConversionBasedUnit(*args, **kwargs): return ifcopenshell.create_entity('IfcConversionBasedUnit', 'IFC4', *args, **kwargs)


def IfcConversionBasedUnitWithOffset(*args, **kwargs): return ifcopenshell.create_entity('IfcConversionBasedUnitWithOffset', 'IFC4', *args, **kwargs)


def IfcCooledBeam(*args, **kwargs): return ifcopenshell.create_entity('IfcCooledBeam', 'IFC4', *args, **kwargs)


def IfcCooledBeamType(*args, **kwargs): return ifcopenshell.create_entity('IfcCooledBeamType', 'IFC4', *args, **kwargs)


def IfcCoolingTower(*args, **kwargs): return ifcopenshell.create_entity('IfcCoolingTower', 'IFC4', *args, **kwargs)


def IfcCoolingTowerType(*args, **kwargs): return ifcopenshell.create_entity('IfcCoolingTowerType', 'IFC4', *args, **kwargs)


def IfcCoordinateOperation(*args, **kwargs): return ifcopenshell.create_entity('IfcCoordinateOperation', 'IFC4', *args, **kwargs)


def IfcCoordinateReferenceSystem(*args, **kwargs): return ifcopenshell.create_entity('IfcCoordinateReferenceSystem', 'IFC4', *args, **kwargs)


def IfcCostItem(*args, **kwargs): return ifcopenshell.create_entity('IfcCostItem', 'IFC4', *args, **kwargs)


def IfcCostSchedule(*args, **kwargs): return ifcopenshell.create_entity('IfcCostSchedule', 'IFC4', *args, **kwargs)


def IfcCostValue(*args, **kwargs): return ifcopenshell.create_entity('IfcCostValue', 'IFC4', *args, **kwargs)


def IfcCovering(*args, **kwargs): return ifcopenshell.create_entity('IfcCovering', 'IFC4', *args, **kwargs)


def IfcCoveringType(*args, **kwargs): return ifcopenshell.create_entity('IfcCoveringType', 'IFC4', *args, **kwargs)


def IfcCrewResource(*args, **kwargs): return ifcopenshell.create_entity('IfcCrewResource', 'IFC4', *args, **kwargs)


def IfcCrewResourceType(*args, **kwargs): return ifcopenshell.create_entity('IfcCrewResourceType', 'IFC4', *args, **kwargs)


def IfcCsgPrimitive3D(*args, **kwargs): return ifcopenshell.create_entity('IfcCsgPrimitive3D', 'IFC4', *args, **kwargs)


def IfcCsgSolid(*args, **kwargs): return ifcopenshell.create_entity('IfcCsgSolid', 'IFC4', *args, **kwargs)


def IfcCurrencyRelationship(*args, **kwargs): return ifcopenshell.create_entity('IfcCurrencyRelationship', 'IFC4', *args, **kwargs)


def IfcCurtainWall(*args, **kwargs): return ifcopenshell.create_entity('IfcCurtainWall', 'IFC4', *args, **kwargs)


def IfcCurtainWallType(*args, **kwargs): return ifcopenshell.create_entity('IfcCurtainWallType', 'IFC4', *args, **kwargs)


def IfcCurve(*args, **kwargs): return ifcopenshell.create_entity('IfcCurve', 'IFC4', *args, **kwargs)


def IfcCurveBoundedPlane(*args, **kwargs): return ifcopenshell.create_entity('IfcCurveBoundedPlane', 'IFC4', *args, **kwargs)


def IfcCurveBoundedSurface(*args, **kwargs): return ifcopenshell.create_entity('IfcCurveBoundedSurface', 'IFC4', *args, **kwargs)


def IfcCurveStyle(*args, **kwargs): return ifcopenshell.create_entity('IfcCurveStyle', 'IFC4', *args, **kwargs)


def IfcCurveStyleFont(*args, **kwargs): return ifcopenshell.create_entity('IfcCurveStyleFont', 'IFC4', *args, **kwargs)


def IfcCurveStyleFontAndScaling(*args, **kwargs): return ifcopenshell.create_entity('IfcCurveStyleFontAndScaling', 'IFC4', *args, **kwargs)


def IfcCurveStyleFontPattern(*args, **kwargs): return ifcopenshell.create_entity('IfcCurveStyleFontPattern', 'IFC4', *args, **kwargs)


def IfcCylindricalSurface(*args, **kwargs): return ifcopenshell.create_entity('IfcCylindricalSurface', 'IFC4', *args, **kwargs)


def IfcDamper(*args, **kwargs): return ifcopenshell.create_entity('IfcDamper', 'IFC4', *args, **kwargs)


def IfcDamperType(*args, **kwargs): return ifcopenshell.create_entity('IfcDamperType', 'IFC4', *args, **kwargs)


def IfcDerivedProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcDerivedProfileDef', 'IFC4', *args, **kwargs)


def IfcDerivedUnit(*args, **kwargs): return ifcopenshell.create_entity('IfcDerivedUnit', 'IFC4', *args, **kwargs)


def IfcDerivedUnitElement(*args, **kwargs): return ifcopenshell.create_entity('IfcDerivedUnitElement', 'IFC4', *args, **kwargs)


def IfcDimensionalExponents(*args, **kwargs): return ifcopenshell.create_entity('IfcDimensionalExponents', 'IFC4', *args, **kwargs)


def IfcDirection(*args, **kwargs): return ifcopenshell.create_entity('IfcDirection', 'IFC4', *args, **kwargs)


def IfcDiscreteAccessory(*args, **kwargs): return ifcopenshell.create_entity('IfcDiscreteAccessory', 'IFC4', *args, **kwargs)


def IfcDiscreteAccessoryType(*args, **kwargs): return ifcopenshell.create_entity('IfcDiscreteAccessoryType', 'IFC4', *args, **kwargs)


def IfcDistributionChamberElement(*args, **kwargs): return ifcopenshell.create_entity('IfcDistributionChamberElement', 'IFC4', *args, **kwargs)


def IfcDistributionChamberElementType(*args, **kwargs): return ifcopenshell.create_entity('IfcDistributionChamberElementType', 'IFC4', *args, **kwargs)


def IfcDistributionCircuit(*args, **kwargs): return ifcopenshell.create_entity('IfcDistributionCircuit', 'IFC4', *args, **kwargs)


def IfcDistributionControlElement(*args, **kwargs): return ifcopenshell.create_entity('IfcDistributionControlElement', 'IFC4', *args, **kwargs)


def IfcDistributionControlElementType(*args, **kwargs): return ifcopenshell.create_entity('IfcDistributionControlElementType', 'IFC4', *args, **kwargs)


def IfcDistributionElement(*args, **kwargs): return ifcopenshell.create_entity('IfcDistributionElement', 'IFC4', *args, **kwargs)


def IfcDistributionElementType(*args, **kwargs): return ifcopenshell.create_entity('IfcDistributionElementType', 'IFC4', *args, **kwargs)


def IfcDistributionFlowElement(*args, **kwargs): return ifcopenshell.create_entity('IfcDistributionFlowElement', 'IFC4', *args, **kwargs)


def IfcDistributionFlowElementType(*args, **kwargs): return ifcopenshell.create_entity('IfcDistributionFlowElementType', 'IFC4', *args, **kwargs)


def IfcDistributionPort(*args, **kwargs): return ifcopenshell.create_entity('IfcDistributionPort', 'IFC4', *args, **kwargs)


def IfcDistributionSystem(*args, **kwargs): return ifcopenshell.create_entity('IfcDistributionSystem', 'IFC4', *args, **kwargs)


def IfcDocumentInformation(*args, **kwargs): return ifcopenshell.create_entity('IfcDocumentInformation', 'IFC4', *args, **kwargs)


def IfcDocumentInformationRelationship(*args, **kwargs): return ifcopenshell.create_entity('IfcDocumentInformationRelationship', 'IFC4', *args, **kwargs)


def IfcDocumentReference(*args, **kwargs): return ifcopenshell.create_entity('IfcDocumentReference', 'IFC4', *args, **kwargs)


def IfcDoor(*args, **kwargs): return ifcopenshell.create_entity('IfcDoor', 'IFC4', *args, **kwargs)


def IfcDoorLiningProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcDoorLiningProperties', 'IFC4', *args, **kwargs)


def IfcDoorPanelProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcDoorPanelProperties', 'IFC4', *args, **kwargs)


def IfcDoorStandardCase(*args, **kwargs): return ifcopenshell.create_entity('IfcDoorStandardCase', 'IFC4', *args, **kwargs)


def IfcDoorStyle(*args, **kwargs): return ifcopenshell.create_entity('IfcDoorStyle', 'IFC4', *args, **kwargs)


def IfcDoorType(*args, **kwargs): return ifcopenshell.create_entity('IfcDoorType', 'IFC4', *args, **kwargs)


def IfcDraughtingPreDefinedColour(*args, **kwargs): return ifcopenshell.create_entity('IfcDraughtingPreDefinedColour', 'IFC4', *args, **kwargs)


def IfcDraughtingPreDefinedCurveFont(*args, **kwargs): return ifcopenshell.create_entity('IfcDraughtingPreDefinedCurveFont', 'IFC4', *args, **kwargs)


def IfcDuctFitting(*args, **kwargs): return ifcopenshell.create_entity('IfcDuctFitting', 'IFC4', *args, **kwargs)


def IfcDuctFittingType(*args, **kwargs): return ifcopenshell.create_entity('IfcDuctFittingType', 'IFC4', *args, **kwargs)


def IfcDuctSegment(*args, **kwargs): return ifcopenshell.create_entity('IfcDuctSegment', 'IFC4', *args, **kwargs)


def IfcDuctSegmentType(*args, **kwargs): return ifcopenshell.create_entity('IfcDuctSegmentType', 'IFC4', *args, **kwargs)


def IfcDuctSilencer(*args, **kwargs): return ifcopenshell.create_entity('IfcDuctSilencer', 'IFC4', *args, **kwargs)


def IfcDuctSilencerType(*args, **kwargs): return ifcopenshell.create_entity('IfcDuctSilencerType', 'IFC4', *args, **kwargs)


def IfcEdge(*args, **kwargs): return ifcopenshell.create_entity('IfcEdge', 'IFC4', *args, **kwargs)


def IfcEdgeCurve(*args, **kwargs): return ifcopenshell.create_entity('IfcEdgeCurve', 'IFC4', *args, **kwargs)


def IfcEdgeLoop(*args, **kwargs): return ifcopenshell.create_entity('IfcEdgeLoop', 'IFC4', *args, **kwargs)


def IfcElectricAppliance(*args, **kwargs): return ifcopenshell.create_entity('IfcElectricAppliance', 'IFC4', *args, **kwargs)


def IfcElectricApplianceType(*args, **kwargs): return ifcopenshell.create_entity('IfcElectricApplianceType', 'IFC4', *args, **kwargs)


def IfcElectricDistributionBoard(*args, **kwargs): return ifcopenshell.create_entity('IfcElectricDistributionBoard', 'IFC4', *args, **kwargs)


def IfcElectricDistributionBoardType(*args, **kwargs): return ifcopenshell.create_entity('IfcElectricDistributionBoardType', 'IFC4', *args, **kwargs)


def IfcElectricFlowStorageDevice(*args, **kwargs): return ifcopenshell.create_entity('IfcElectricFlowStorageDevice', 'IFC4', *args, **kwargs)


def IfcElectricFlowStorageDeviceType(*args, **kwargs): return ifcopenshell.create_entity('IfcElectricFlowStorageDeviceType', 'IFC4', *args, **kwargs)


def IfcElectricGenerator(*args, **kwargs): return ifcopenshell.create_entity('IfcElectricGenerator', 'IFC4', *args, **kwargs)


def IfcElectricGeneratorType(*args, **kwargs): return ifcopenshell.create_entity('IfcElectricGeneratorType', 'IFC4', *args, **kwargs)


def IfcElectricMotor(*args, **kwargs): return ifcopenshell.create_entity('IfcElectricMotor', 'IFC4', *args, **kwargs)


def IfcElectricMotorType(*args, **kwargs): return ifcopenshell.create_entity('IfcElectricMotorType', 'IFC4', *args, **kwargs)


def IfcElectricTimeControl(*args, **kwargs): return ifcopenshell.create_entity('IfcElectricTimeControl', 'IFC4', *args, **kwargs)


def IfcElectricTimeControlType(*args, **kwargs): return ifcopenshell.create_entity('IfcElectricTimeControlType', 'IFC4', *args, **kwargs)


def IfcElement(*args, **kwargs): return ifcopenshell.create_entity('IfcElement', 'IFC4', *args, **kwargs)


def IfcElementAssembly(*args, **kwargs): return ifcopenshell.create_entity('IfcElementAssembly', 'IFC4', *args, **kwargs)


def IfcElementAssemblyType(*args, **kwargs): return ifcopenshell.create_entity('IfcElementAssemblyType', 'IFC4', *args, **kwargs)


def IfcElementComponent(*args, **kwargs): return ifcopenshell.create_entity('IfcElementComponent', 'IFC4', *args, **kwargs)


def IfcElementComponentType(*args, **kwargs): return ifcopenshell.create_entity('IfcElementComponentType', 'IFC4', *args, **kwargs)


def IfcElementQuantity(*args, **kwargs): return ifcopenshell.create_entity('IfcElementQuantity', 'IFC4', *args, **kwargs)


def IfcElementType(*args, **kwargs): return ifcopenshell.create_entity('IfcElementType', 'IFC4', *args, **kwargs)


def IfcElementarySurface(*args, **kwargs): return ifcopenshell.create_entity('IfcElementarySurface', 'IFC4', *args, **kwargs)


def IfcEllipse(*args, **kwargs): return ifcopenshell.create_entity('IfcEllipse', 'IFC4', *args, **kwargs)


def IfcEllipseProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcEllipseProfileDef', 'IFC4', *args, **kwargs)


def IfcEnergyConversionDevice(*args, **kwargs): return ifcopenshell.create_entity('IfcEnergyConversionDevice', 'IFC4', *args, **kwargs)


def IfcEnergyConversionDeviceType(*args, **kwargs): return ifcopenshell.create_entity('IfcEnergyConversionDeviceType', 'IFC4', *args, **kwargs)


def IfcEngine(*args, **kwargs): return ifcopenshell.create_entity('IfcEngine', 'IFC4', *args, **kwargs)


def IfcEngineType(*args, **kwargs): return ifcopenshell.create_entity('IfcEngineType', 'IFC4', *args, **kwargs)


def IfcEvaporativeCooler(*args, **kwargs): return ifcopenshell.create_entity('IfcEvaporativeCooler', 'IFC4', *args, **kwargs)


def IfcEvaporativeCoolerType(*args, **kwargs): return ifcopenshell.create_entity('IfcEvaporativeCoolerType', 'IFC4', *args, **kwargs)


def IfcEvaporator(*args, **kwargs): return ifcopenshell.create_entity('IfcEvaporator', 'IFC4', *args, **kwargs)


def IfcEvaporatorType(*args, **kwargs): return ifcopenshell.create_entity('IfcEvaporatorType', 'IFC4', *args, **kwargs)


def IfcEvent(*args, **kwargs): return ifcopenshell.create_entity('IfcEvent', 'IFC4', *args, **kwargs)


def IfcEventTime(*args, **kwargs): return ifcopenshell.create_entity('IfcEventTime', 'IFC4', *args, **kwargs)


def IfcEventType(*args, **kwargs): return ifcopenshell.create_entity('IfcEventType', 'IFC4', *args, **kwargs)


def IfcExtendedProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcExtendedProperties', 'IFC4', *args, **kwargs)


def IfcExternalInformation(*args, **kwargs): return ifcopenshell.create_entity('IfcExternalInformation', 'IFC4', *args, **kwargs)


def IfcExternalReference(*args, **kwargs): return ifcopenshell.create_entity('IfcExternalReference', 'IFC4', *args, **kwargs)


def IfcExternalReferenceRelationship(*args, **kwargs): return ifcopenshell.create_entity('IfcExternalReferenceRelationship', 'IFC4', *args, **kwargs)


def IfcExternalSpatialElement(*args, **kwargs): return ifcopenshell.create_entity('IfcExternalSpatialElement', 'IFC4', *args, **kwargs)


def IfcExternalSpatialStructureElement(*args, **kwargs): return ifcopenshell.create_entity('IfcExternalSpatialStructureElement', 'IFC4', *args, **kwargs)


def IfcExternallyDefinedHatchStyle(*args, **kwargs): return ifcopenshell.create_entity('IfcExternallyDefinedHatchStyle', 'IFC4', *args, **kwargs)


def IfcExternallyDefinedSurfaceStyle(*args, **kwargs): return ifcopenshell.create_entity('IfcExternallyDefinedSurfaceStyle', 'IFC4', *args, **kwargs)


def IfcExternallyDefinedTextFont(*args, **kwargs): return ifcopenshell.create_entity('IfcExternallyDefinedTextFont', 'IFC4', *args, **kwargs)


def IfcExtrudedAreaSolid(*args, **kwargs): return ifcopenshell.create_entity('IfcExtrudedAreaSolid', 'IFC4', *args, **kwargs)


def IfcExtrudedAreaSolidTapered(*args, **kwargs): return ifcopenshell.create_entity('IfcExtrudedAreaSolidTapered', 'IFC4', *args, **kwargs)


def IfcFace(*args, **kwargs): return ifcopenshell.create_entity('IfcFace', 'IFC4', *args, **kwargs)


def IfcFaceBasedSurfaceModel(*args, **kwargs): return ifcopenshell.create_entity('IfcFaceBasedSurfaceModel', 'IFC4', *args, **kwargs)


def IfcFaceBound(*args, **kwargs): return ifcopenshell.create_entity('IfcFaceBound', 'IFC4', *args, **kwargs)


def IfcFaceOuterBound(*args, **kwargs): return ifcopenshell.create_entity('IfcFaceOuterBound', 'IFC4', *args, **kwargs)


def IfcFaceSurface(*args, **kwargs): return ifcopenshell.create_entity('IfcFaceSurface', 'IFC4', *args, **kwargs)


def IfcFacetedBrep(*args, **kwargs): return ifcopenshell.create_entity('IfcFacetedBrep', 'IFC4', *args, **kwargs)


def IfcFacetedBrepWithVoids(*args, **kwargs): return ifcopenshell.create_entity('IfcFacetedBrepWithVoids', 'IFC4', *args, **kwargs)


def IfcFailureConnectionCondition(*args, **kwargs): return ifcopenshell.create_entity('IfcFailureConnectionCondition', 'IFC4', *args, **kwargs)


def IfcFan(*args, **kwargs): return ifcopenshell.create_entity('IfcFan', 'IFC4', *args, **kwargs)


def IfcFanType(*args, **kwargs): return ifcopenshell.create_entity('IfcFanType', 'IFC4', *args, **kwargs)


def IfcFastener(*args, **kwargs): return ifcopenshell.create_entity('IfcFastener', 'IFC4', *args, **kwargs)


def IfcFastenerType(*args, **kwargs): return ifcopenshell.create_entity('IfcFastenerType', 'IFC4', *args, **kwargs)


def IfcFeatureElement(*args, **kwargs): return ifcopenshell.create_entity('IfcFeatureElement', 'IFC4', *args, **kwargs)


def IfcFeatureElementAddition(*args, **kwargs): return ifcopenshell.create_entity('IfcFeatureElementAddition', 'IFC4', *args, **kwargs)


def IfcFeatureElementSubtraction(*args, **kwargs): return ifcopenshell.create_entity('IfcFeatureElementSubtraction', 'IFC4', *args, **kwargs)


def IfcFillAreaStyle(*args, **kwargs): return ifcopenshell.create_entity('IfcFillAreaStyle', 'IFC4', *args, **kwargs)


def IfcFillAreaStyleHatching(*args, **kwargs): return ifcopenshell.create_entity('IfcFillAreaStyleHatching', 'IFC4', *args, **kwargs)


def IfcFillAreaStyleTiles(*args, **kwargs): return ifcopenshell.create_entity('IfcFillAreaStyleTiles', 'IFC4', *args, **kwargs)


def IfcFilter(*args, **kwargs): return ifcopenshell.create_entity('IfcFilter', 'IFC4', *args, **kwargs)


def IfcFilterType(*args, **kwargs): return ifcopenshell.create_entity('IfcFilterType', 'IFC4', *args, **kwargs)


def IfcFireSuppressionTerminal(*args, **kwargs): return ifcopenshell.create_entity('IfcFireSuppressionTerminal', 'IFC4', *args, **kwargs)


def IfcFireSuppressionTerminalType(*args, **kwargs): return ifcopenshell.create_entity('IfcFireSuppressionTerminalType', 'IFC4', *args, **kwargs)


def IfcFixedReferenceSweptAreaSolid(*args, **kwargs): return ifcopenshell.create_entity('IfcFixedReferenceSweptAreaSolid', 'IFC4', *args, **kwargs)


def IfcFlowController(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowController', 'IFC4', *args, **kwargs)


def IfcFlowControllerType(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowControllerType', 'IFC4', *args, **kwargs)


def IfcFlowFitting(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowFitting', 'IFC4', *args, **kwargs)


def IfcFlowFittingType(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowFittingType', 'IFC4', *args, **kwargs)


def IfcFlowInstrument(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowInstrument', 'IFC4', *args, **kwargs)


def IfcFlowInstrumentType(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowInstrumentType', 'IFC4', *args, **kwargs)


def IfcFlowMeter(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowMeter', 'IFC4', *args, **kwargs)


def IfcFlowMeterType(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowMeterType', 'IFC4', *args, **kwargs)


def IfcFlowMovingDevice(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowMovingDevice', 'IFC4', *args, **kwargs)


def IfcFlowMovingDeviceType(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowMovingDeviceType', 'IFC4', *args, **kwargs)


def IfcFlowSegment(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowSegment', 'IFC4', *args, **kwargs)


def IfcFlowSegmentType(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowSegmentType', 'IFC4', *args, **kwargs)


def IfcFlowStorageDevice(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowStorageDevice', 'IFC4', *args, **kwargs)


def IfcFlowStorageDeviceType(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowStorageDeviceType', 'IFC4', *args, **kwargs)


def IfcFlowTerminal(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowTerminal', 'IFC4', *args, **kwargs)


def IfcFlowTerminalType(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowTerminalType', 'IFC4', *args, **kwargs)


def IfcFlowTreatmentDevice(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowTreatmentDevice', 'IFC4', *args, **kwargs)


def IfcFlowTreatmentDeviceType(*args, **kwargs): return ifcopenshell.create_entity('IfcFlowTreatmentDeviceType', 'IFC4', *args, **kwargs)


def IfcFooting(*args, **kwargs): return ifcopenshell.create_entity('IfcFooting', 'IFC4', *args, **kwargs)


def IfcFootingType(*args, **kwargs): return ifcopenshell.create_entity('IfcFootingType', 'IFC4', *args, **kwargs)


def IfcFurnishingElement(*args, **kwargs): return ifcopenshell.create_entity('IfcFurnishingElement', 'IFC4', *args, **kwargs)


def IfcFurnishingElementType(*args, **kwargs): return ifcopenshell.create_entity('IfcFurnishingElementType', 'IFC4', *args, **kwargs)


def IfcFurniture(*args, **kwargs): return ifcopenshell.create_entity('IfcFurniture', 'IFC4', *args, **kwargs)


def IfcFurnitureType(*args, **kwargs): return ifcopenshell.create_entity('IfcFurnitureType', 'IFC4', *args, **kwargs)


def IfcGeographicElement(*args, **kwargs): return ifcopenshell.create_entity('IfcGeographicElement', 'IFC4', *args, **kwargs)


def IfcGeographicElementType(*args, **kwargs): return ifcopenshell.create_entity('IfcGeographicElementType', 'IFC4', *args, **kwargs)


def IfcGeometricCurveSet(*args, **kwargs): return ifcopenshell.create_entity('IfcGeometricCurveSet', 'IFC4', *args, **kwargs)


def IfcGeometricRepresentationContext(*args, **kwargs): return ifcopenshell.create_entity('IfcGeometricRepresentationContext', 'IFC4', *args, **kwargs)


def IfcGeometricRepresentationItem(*args, **kwargs): return ifcopenshell.create_entity('IfcGeometricRepresentationItem', 'IFC4', *args, **kwargs)


def IfcGeometricRepresentationSubContext(*args, **kwargs): return ifcopenshell.create_entity('IfcGeometricRepresentationSubContext', 'IFC4', *args, **kwargs)


def IfcGeometricSet(*args, **kwargs): return ifcopenshell.create_entity('IfcGeometricSet', 'IFC4', *args, **kwargs)


def IfcGrid(*args, **kwargs): return ifcopenshell.create_entity('IfcGrid', 'IFC4', *args, **kwargs)


def IfcGridAxis(*args, **kwargs): return ifcopenshell.create_entity('IfcGridAxis', 'IFC4', *args, **kwargs)


def IfcGridPlacement(*args, **kwargs): return ifcopenshell.create_entity('IfcGridPlacement', 'IFC4', *args, **kwargs)


def IfcGroup(*args, **kwargs): return ifcopenshell.create_entity('IfcGroup', 'IFC4', *args, **kwargs)


def IfcHalfSpaceSolid(*args, **kwargs): return ifcopenshell.create_entity('IfcHalfSpaceSolid', 'IFC4', *args, **kwargs)


def IfcHeatExchanger(*args, **kwargs): return ifcopenshell.create_entity('IfcHeatExchanger', 'IFC4', *args, **kwargs)


def IfcHeatExchangerType(*args, **kwargs): return ifcopenshell.create_entity('IfcHeatExchangerType', 'IFC4', *args, **kwargs)


def IfcHumidifier(*args, **kwargs): return ifcopenshell.create_entity('IfcHumidifier', 'IFC4', *args, **kwargs)


def IfcHumidifierType(*args, **kwargs): return ifcopenshell.create_entity('IfcHumidifierType', 'IFC4', *args, **kwargs)


def IfcIShapeProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcIShapeProfileDef', 'IFC4', *args, **kwargs)


def IfcImageTexture(*args, **kwargs): return ifcopenshell.create_entity('IfcImageTexture', 'IFC4', *args, **kwargs)


def IfcIndexedColourMap(*args, **kwargs): return ifcopenshell.create_entity('IfcIndexedColourMap', 'IFC4', *args, **kwargs)


def IfcIndexedPolyCurve(*args, **kwargs): return ifcopenshell.create_entity('IfcIndexedPolyCurve', 'IFC4', *args, **kwargs)


def IfcIndexedPolygonalFace(*args, **kwargs): return ifcopenshell.create_entity('IfcIndexedPolygonalFace', 'IFC4', *args, **kwargs)


def IfcIndexedPolygonalFaceWithVoids(*args, **kwargs): return ifcopenshell.create_entity('IfcIndexedPolygonalFaceWithVoids', 'IFC4', *args, **kwargs)


def IfcIndexedTextureMap(*args, **kwargs): return ifcopenshell.create_entity('IfcIndexedTextureMap', 'IFC4', *args, **kwargs)


def IfcIndexedTriangleTextureMap(*args, **kwargs): return ifcopenshell.create_entity('IfcIndexedTriangleTextureMap', 'IFC4', *args, **kwargs)


def IfcInterceptor(*args, **kwargs): return ifcopenshell.create_entity('IfcInterceptor', 'IFC4', *args, **kwargs)


def IfcInterceptorType(*args, **kwargs): return ifcopenshell.create_entity('IfcInterceptorType', 'IFC4', *args, **kwargs)


def IfcIntersectionCurve(*args, **kwargs): return ifcopenshell.create_entity('IfcIntersectionCurve', 'IFC4', *args, **kwargs)


def IfcInventory(*args, **kwargs): return ifcopenshell.create_entity('IfcInventory', 'IFC4', *args, **kwargs)


def IfcIrregularTimeSeries(*args, **kwargs): return ifcopenshell.create_entity('IfcIrregularTimeSeries', 'IFC4', *args, **kwargs)


def IfcIrregularTimeSeriesValue(*args, **kwargs): return ifcopenshell.create_entity('IfcIrregularTimeSeriesValue', 'IFC4', *args, **kwargs)


def IfcJunctionBox(*args, **kwargs): return ifcopenshell.create_entity('IfcJunctionBox', 'IFC4', *args, **kwargs)


def IfcJunctionBoxType(*args, **kwargs): return ifcopenshell.create_entity('IfcJunctionBoxType', 'IFC4', *args, **kwargs)


def IfcLShapeProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcLShapeProfileDef', 'IFC4', *args, **kwargs)


def IfcLaborResource(*args, **kwargs): return ifcopenshell.create_entity('IfcLaborResource', 'IFC4', *args, **kwargs)


def IfcLaborResourceType(*args, **kwargs): return ifcopenshell.create_entity('IfcLaborResourceType', 'IFC4', *args, **kwargs)


def IfcLagTime(*args, **kwargs): return ifcopenshell.create_entity('IfcLagTime', 'IFC4', *args, **kwargs)


def IfcLamp(*args, **kwargs): return ifcopenshell.create_entity('IfcLamp', 'IFC4', *args, **kwargs)


def IfcLampType(*args, **kwargs): return ifcopenshell.create_entity('IfcLampType', 'IFC4', *args, **kwargs)


def IfcLibraryInformation(*args, **kwargs): return ifcopenshell.create_entity('IfcLibraryInformation', 'IFC4', *args, **kwargs)


def IfcLibraryReference(*args, **kwargs): return ifcopenshell.create_entity('IfcLibraryReference', 'IFC4', *args, **kwargs)


def IfcLightDistributionData(*args, **kwargs): return ifcopenshell.create_entity('IfcLightDistributionData', 'IFC4', *args, **kwargs)


def IfcLightFixture(*args, **kwargs): return ifcopenshell.create_entity('IfcLightFixture', 'IFC4', *args, **kwargs)


def IfcLightFixtureType(*args, **kwargs): return ifcopenshell.create_entity('IfcLightFixtureType', 'IFC4', *args, **kwargs)


def IfcLightIntensityDistribution(*args, **kwargs): return ifcopenshell.create_entity('IfcLightIntensityDistribution', 'IFC4', *args, **kwargs)


def IfcLightSource(*args, **kwargs): return ifcopenshell.create_entity('IfcLightSource', 'IFC4', *args, **kwargs)


def IfcLightSourceAmbient(*args, **kwargs): return ifcopenshell.create_entity('IfcLightSourceAmbient', 'IFC4', *args, **kwargs)


def IfcLightSourceDirectional(*args, **kwargs): return ifcopenshell.create_entity('IfcLightSourceDirectional', 'IFC4', *args, **kwargs)


def IfcLightSourceGoniometric(*args, **kwargs): return ifcopenshell.create_entity('IfcLightSourceGoniometric', 'IFC4', *args, **kwargs)


def IfcLightSourcePositional(*args, **kwargs): return ifcopenshell.create_entity('IfcLightSourcePositional', 'IFC4', *args, **kwargs)


def IfcLightSourceSpot(*args, **kwargs): return ifcopenshell.create_entity('IfcLightSourceSpot', 'IFC4', *args, **kwargs)


def IfcLine(*args, **kwargs): return ifcopenshell.create_entity('IfcLine', 'IFC4', *args, **kwargs)


def IfcLocalPlacement(*args, **kwargs): return ifcopenshell.create_entity('IfcLocalPlacement', 'IFC4', *args, **kwargs)


def IfcLoop(*args, **kwargs): return ifcopenshell.create_entity('IfcLoop', 'IFC4', *args, **kwargs)


def IfcManifoldSolidBrep(*args, **kwargs): return ifcopenshell.create_entity('IfcManifoldSolidBrep', 'IFC4', *args, **kwargs)


def IfcMapConversion(*args, **kwargs): return ifcopenshell.create_entity('IfcMapConversion', 'IFC4', *args, **kwargs)


def IfcMappedItem(*args, **kwargs): return ifcopenshell.create_entity('IfcMappedItem', 'IFC4', *args, **kwargs)


def IfcMaterial(*args, **kwargs): return ifcopenshell.create_entity('IfcMaterial', 'IFC4', *args, **kwargs)


def IfcMaterialClassificationRelationship(*args, **kwargs): return ifcopenshell.create_entity('IfcMaterialClassificationRelationship', 'IFC4', *args, **kwargs)


def IfcMaterialConstituent(*args, **kwargs): return ifcopenshell.create_entity('IfcMaterialConstituent', 'IFC4', *args, **kwargs)


def IfcMaterialConstituentSet(*args, **kwargs): return ifcopenshell.create_entity('IfcMaterialConstituentSet', 'IFC4', *args, **kwargs)


def IfcMaterialDefinition(*args, **kwargs): return ifcopenshell.create_entity('IfcMaterialDefinition', 'IFC4', *args, **kwargs)


def IfcMaterialDefinitionRepresentation(*args, **kwargs): return ifcopenshell.create_entity('IfcMaterialDefinitionRepresentation', 'IFC4', *args, **kwargs)


def IfcMaterialLayer(*args, **kwargs): return ifcopenshell.create_entity('IfcMaterialLayer', 'IFC4', *args, **kwargs)


def IfcMaterialLayerSet(*args, **kwargs): return ifcopenshell.create_entity('IfcMaterialLayerSet', 'IFC4', *args, **kwargs)


def IfcMaterialLayerSetUsage(*args, **kwargs): return ifcopenshell.create_entity('IfcMaterialLayerSetUsage', 'IFC4', *args, **kwargs)


def IfcMaterialLayerWithOffsets(*args, **kwargs): return ifcopenshell.create_entity('IfcMaterialLayerWithOffsets', 'IFC4', *args, **kwargs)


def IfcMaterialList(*args, **kwargs): return ifcopenshell.create_entity('IfcMaterialList', 'IFC4', *args, **kwargs)


def IfcMaterialProfile(*args, **kwargs): return ifcopenshell.create_entity('IfcMaterialProfile', 'IFC4', *args, **kwargs)


def IfcMaterialProfileSet(*args, **kwargs): return ifcopenshell.create_entity('IfcMaterialProfileSet', 'IFC4', *args, **kwargs)


def IfcMaterialProfileSetUsage(*args, **kwargs): return ifcopenshell.create_entity('IfcMaterialProfileSetUsage', 'IFC4', *args, **kwargs)


def IfcMaterialProfileSetUsageTapering(*args, **kwargs): return ifcopenshell.create_entity('IfcMaterialProfileSetUsageTapering', 'IFC4', *args, **kwargs)


def IfcMaterialProfileWithOffsets(*args, **kwargs): return ifcopenshell.create_entity('IfcMaterialProfileWithOffsets', 'IFC4', *args, **kwargs)


def IfcMaterialProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcMaterialProperties', 'IFC4', *args, **kwargs)


def IfcMaterialRelationship(*args, **kwargs): return ifcopenshell.create_entity('IfcMaterialRelationship', 'IFC4', *args, **kwargs)


def IfcMaterialUsageDefinition(*args, **kwargs): return ifcopenshell.create_entity('IfcMaterialUsageDefinition', 'IFC4', *args, **kwargs)


def IfcMeasureWithUnit(*args, **kwargs): return ifcopenshell.create_entity('IfcMeasureWithUnit', 'IFC4', *args, **kwargs)


def IfcMechanicalFastener(*args, **kwargs): return ifcopenshell.create_entity('IfcMechanicalFastener', 'IFC4', *args, **kwargs)


def IfcMechanicalFastenerType(*args, **kwargs): return ifcopenshell.create_entity('IfcMechanicalFastenerType', 'IFC4', *args, **kwargs)


def IfcMedicalDevice(*args, **kwargs): return ifcopenshell.create_entity('IfcMedicalDevice', 'IFC4', *args, **kwargs)


def IfcMedicalDeviceType(*args, **kwargs): return ifcopenshell.create_entity('IfcMedicalDeviceType', 'IFC4', *args, **kwargs)


def IfcMember(*args, **kwargs): return ifcopenshell.create_entity('IfcMember', 'IFC4', *args, **kwargs)


def IfcMemberStandardCase(*args, **kwargs): return ifcopenshell.create_entity('IfcMemberStandardCase', 'IFC4', *args, **kwargs)


def IfcMemberType(*args, **kwargs): return ifcopenshell.create_entity('IfcMemberType', 'IFC4', *args, **kwargs)


def IfcMetric(*args, **kwargs): return ifcopenshell.create_entity('IfcMetric', 'IFC4', *args, **kwargs)


def IfcMirroredProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcMirroredProfileDef', 'IFC4', *args, **kwargs)


def IfcMonetaryUnit(*args, **kwargs): return ifcopenshell.create_entity('IfcMonetaryUnit', 'IFC4', *args, **kwargs)


def IfcMotorConnection(*args, **kwargs): return ifcopenshell.create_entity('IfcMotorConnection', 'IFC4', *args, **kwargs)


def IfcMotorConnectionType(*args, **kwargs): return ifcopenshell.create_entity('IfcMotorConnectionType', 'IFC4', *args, **kwargs)


def IfcNamedUnit(*args, **kwargs): return ifcopenshell.create_entity('IfcNamedUnit', 'IFC4', *args, **kwargs)


def IfcObject(*args, **kwargs): return ifcopenshell.create_entity('IfcObject', 'IFC4', *args, **kwargs)


def IfcObjectDefinition(*args, **kwargs): return ifcopenshell.create_entity('IfcObjectDefinition', 'IFC4', *args, **kwargs)


def IfcObjectPlacement(*args, **kwargs): return ifcopenshell.create_entity('IfcObjectPlacement', 'IFC4', *args, **kwargs)


def IfcObjective(*args, **kwargs): return ifcopenshell.create_entity('IfcObjective', 'IFC4', *args, **kwargs)


def IfcOccupant(*args, **kwargs): return ifcopenshell.create_entity('IfcOccupant', 'IFC4', *args, **kwargs)


def IfcOffsetCurve2D(*args, **kwargs): return ifcopenshell.create_entity('IfcOffsetCurve2D', 'IFC4', *args, **kwargs)


def IfcOffsetCurve3D(*args, **kwargs): return ifcopenshell.create_entity('IfcOffsetCurve3D', 'IFC4', *args, **kwargs)


def IfcOpenShell(*args, **kwargs): return ifcopenshell.create_entity('IfcOpenShell', 'IFC4', *args, **kwargs)


def IfcOpeningElement(*args, **kwargs): return ifcopenshell.create_entity('IfcOpeningElement', 'IFC4', *args, **kwargs)


def IfcOpeningStandardCase(*args, **kwargs): return ifcopenshell.create_entity('IfcOpeningStandardCase', 'IFC4', *args, **kwargs)


def IfcOrganization(*args, **kwargs): return ifcopenshell.create_entity('IfcOrganization', 'IFC4', *args, **kwargs)


def IfcOrganizationRelationship(*args, **kwargs): return ifcopenshell.create_entity('IfcOrganizationRelationship', 'IFC4', *args, **kwargs)


def IfcOrientedEdge(*args, **kwargs): return ifcopenshell.create_entity('IfcOrientedEdge', 'IFC4', *args, **kwargs)


def IfcOuterBoundaryCurve(*args, **kwargs): return ifcopenshell.create_entity('IfcOuterBoundaryCurve', 'IFC4', *args, **kwargs)


def IfcOutlet(*args, **kwargs): return ifcopenshell.create_entity('IfcOutlet', 'IFC4', *args, **kwargs)


def IfcOutletType(*args, **kwargs): return ifcopenshell.create_entity('IfcOutletType', 'IFC4', *args, **kwargs)


def IfcOwnerHistory(*args, **kwargs): return ifcopenshell.create_entity('IfcOwnerHistory', 'IFC4', *args, **kwargs)


def IfcParameterizedProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcParameterizedProfileDef', 'IFC4', *args, **kwargs)


def IfcPath(*args, **kwargs): return ifcopenshell.create_entity('IfcPath', 'IFC4', *args, **kwargs)


def IfcPcurve(*args, **kwargs): return ifcopenshell.create_entity('IfcPcurve', 'IFC4', *args, **kwargs)


def IfcPerformanceHistory(*args, **kwargs): return ifcopenshell.create_entity('IfcPerformanceHistory', 'IFC4', *args, **kwargs)


def IfcPermeableCoveringProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcPermeableCoveringProperties', 'IFC4', *args, **kwargs)


def IfcPermit(*args, **kwargs): return ifcopenshell.create_entity('IfcPermit', 'IFC4', *args, **kwargs)


def IfcPerson(*args, **kwargs): return ifcopenshell.create_entity('IfcPerson', 'IFC4', *args, **kwargs)


def IfcPersonAndOrganization(*args, **kwargs): return ifcopenshell.create_entity('IfcPersonAndOrganization', 'IFC4', *args, **kwargs)


def IfcPhysicalComplexQuantity(*args, **kwargs): return ifcopenshell.create_entity('IfcPhysicalComplexQuantity', 'IFC4', *args, **kwargs)


def IfcPhysicalQuantity(*args, **kwargs): return ifcopenshell.create_entity('IfcPhysicalQuantity', 'IFC4', *args, **kwargs)


def IfcPhysicalSimpleQuantity(*args, **kwargs): return ifcopenshell.create_entity('IfcPhysicalSimpleQuantity', 'IFC4', *args, **kwargs)


def IfcPile(*args, **kwargs): return ifcopenshell.create_entity('IfcPile', 'IFC4', *args, **kwargs)


def IfcPileType(*args, **kwargs): return ifcopenshell.create_entity('IfcPileType', 'IFC4', *args, **kwargs)


def IfcPipeFitting(*args, **kwargs): return ifcopenshell.create_entity('IfcPipeFitting', 'IFC4', *args, **kwargs)


def IfcPipeFittingType(*args, **kwargs): return ifcopenshell.create_entity('IfcPipeFittingType', 'IFC4', *args, **kwargs)


def IfcPipeSegment(*args, **kwargs): return ifcopenshell.create_entity('IfcPipeSegment', 'IFC4', *args, **kwargs)


def IfcPipeSegmentType(*args, **kwargs): return ifcopenshell.create_entity('IfcPipeSegmentType', 'IFC4', *args, **kwargs)


def IfcPixelTexture(*args, **kwargs): return ifcopenshell.create_entity('IfcPixelTexture', 'IFC4', *args, **kwargs)


def IfcPlacement(*args, **kwargs): return ifcopenshell.create_entity('IfcPlacement', 'IFC4', *args, **kwargs)


def IfcPlanarBox(*args, **kwargs): return ifcopenshell.create_entity('IfcPlanarBox', 'IFC4', *args, **kwargs)


def IfcPlanarExtent(*args, **kwargs): return ifcopenshell.create_entity('IfcPlanarExtent', 'IFC4', *args, **kwargs)


def IfcPlane(*args, **kwargs): return ifcopenshell.create_entity('IfcPlane', 'IFC4', *args, **kwargs)


def IfcPlate(*args, **kwargs): return ifcopenshell.create_entity('IfcPlate', 'IFC4', *args, **kwargs)


def IfcPlateStandardCase(*args, **kwargs): return ifcopenshell.create_entity('IfcPlateStandardCase', 'IFC4', *args, **kwargs)


def IfcPlateType(*args, **kwargs): return ifcopenshell.create_entity('IfcPlateType', 'IFC4', *args, **kwargs)


def IfcPoint(*args, **kwargs): return ifcopenshell.create_entity('IfcPoint', 'IFC4', *args, **kwargs)


def IfcPointOnCurve(*args, **kwargs): return ifcopenshell.create_entity('IfcPointOnCurve', 'IFC4', *args, **kwargs)


def IfcPointOnSurface(*args, **kwargs): return ifcopenshell.create_entity('IfcPointOnSurface', 'IFC4', *args, **kwargs)


def IfcPolyLoop(*args, **kwargs): return ifcopenshell.create_entity('IfcPolyLoop', 'IFC4', *args, **kwargs)


def IfcPolygonalBoundedHalfSpace(*args, **kwargs): return ifcopenshell.create_entity('IfcPolygonalBoundedHalfSpace', 'IFC4', *args, **kwargs)


def IfcPolygonalFaceSet(*args, **kwargs): return ifcopenshell.create_entity('IfcPolygonalFaceSet', 'IFC4', *args, **kwargs)


def IfcPolyline(*args, **kwargs): return ifcopenshell.create_entity('IfcPolyline', 'IFC4', *args, **kwargs)


def IfcPort(*args, **kwargs): return ifcopenshell.create_entity('IfcPort', 'IFC4', *args, **kwargs)


def IfcPostalAddress(*args, **kwargs): return ifcopenshell.create_entity('IfcPostalAddress', 'IFC4', *args, **kwargs)


def IfcPreDefinedColour(*args, **kwargs): return ifcopenshell.create_entity('IfcPreDefinedColour', 'IFC4', *args, **kwargs)


def IfcPreDefinedCurveFont(*args, **kwargs): return ifcopenshell.create_entity('IfcPreDefinedCurveFont', 'IFC4', *args, **kwargs)


def IfcPreDefinedItem(*args, **kwargs): return ifcopenshell.create_entity('IfcPreDefinedItem', 'IFC4', *args, **kwargs)


def IfcPreDefinedProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcPreDefinedProperties', 'IFC4', *args, **kwargs)


def IfcPreDefinedPropertySet(*args, **kwargs): return ifcopenshell.create_entity('IfcPreDefinedPropertySet', 'IFC4', *args, **kwargs)


def IfcPreDefinedTextFont(*args, **kwargs): return ifcopenshell.create_entity('IfcPreDefinedTextFont', 'IFC4', *args, **kwargs)


def IfcPresentationItem(*args, **kwargs): return ifcopenshell.create_entity('IfcPresentationItem', 'IFC4', *args, **kwargs)


def IfcPresentationLayerAssignment(*args, **kwargs): return ifcopenshell.create_entity('IfcPresentationLayerAssignment', 'IFC4', *args, **kwargs)


def IfcPresentationLayerWithStyle(*args, **kwargs): return ifcopenshell.create_entity('IfcPresentationLayerWithStyle', 'IFC4', *args, **kwargs)


def IfcPresentationStyle(*args, **kwargs): return ifcopenshell.create_entity('IfcPresentationStyle', 'IFC4', *args, **kwargs)


def IfcPresentationStyleAssignment(*args, **kwargs): return ifcopenshell.create_entity('IfcPresentationStyleAssignment', 'IFC4', *args, **kwargs)


def IfcProcedure(*args, **kwargs): return ifcopenshell.create_entity('IfcProcedure', 'IFC4', *args, **kwargs)


def IfcProcedureType(*args, **kwargs): return ifcopenshell.create_entity('IfcProcedureType', 'IFC4', *args, **kwargs)


def IfcProcess(*args, **kwargs): return ifcopenshell.create_entity('IfcProcess', 'IFC4', *args, **kwargs)


def IfcProduct(*args, **kwargs): return ifcopenshell.create_entity('IfcProduct', 'IFC4', *args, **kwargs)


def IfcProductDefinitionShape(*args, **kwargs): return ifcopenshell.create_entity('IfcProductDefinitionShape', 'IFC4', *args, **kwargs)


def IfcProductRepresentation(*args, **kwargs): return ifcopenshell.create_entity('IfcProductRepresentation', 'IFC4', *args, **kwargs)


def IfcProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcProfileDef', 'IFC4', *args, **kwargs)


def IfcProfileProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcProfileProperties', 'IFC4', *args, **kwargs)


def IfcProject(*args, **kwargs): return ifcopenshell.create_entity('IfcProject', 'IFC4', *args, **kwargs)


def IfcProjectLibrary(*args, **kwargs): return ifcopenshell.create_entity('IfcProjectLibrary', 'IFC4', *args, **kwargs)


def IfcProjectOrder(*args, **kwargs): return ifcopenshell.create_entity('IfcProjectOrder', 'IFC4', *args, **kwargs)


def IfcProjectedCRS(*args, **kwargs): return ifcopenshell.create_entity('IfcProjectedCRS', 'IFC4', *args, **kwargs)


def IfcProjectionElement(*args, **kwargs): return ifcopenshell.create_entity('IfcProjectionElement', 'IFC4', *args, **kwargs)


def IfcProperty(*args, **kwargs): return ifcopenshell.create_entity('IfcProperty', 'IFC4', *args, **kwargs)


def IfcPropertyAbstraction(*args, **kwargs): return ifcopenshell.create_entity('IfcPropertyAbstraction', 'IFC4', *args, **kwargs)


def IfcPropertyBoundedValue(*args, **kwargs): return ifcopenshell.create_entity('IfcPropertyBoundedValue', 'IFC4', *args, **kwargs)


def IfcPropertyDefinition(*args, **kwargs): return ifcopenshell.create_entity('IfcPropertyDefinition', 'IFC4', *args, **kwargs)


def IfcPropertyDependencyRelationship(*args, **kwargs): return ifcopenshell.create_entity('IfcPropertyDependencyRelationship', 'IFC4', *args, **kwargs)


def IfcPropertyEnumeratedValue(*args, **kwargs): return ifcopenshell.create_entity('IfcPropertyEnumeratedValue', 'IFC4', *args, **kwargs)


def IfcPropertyEnumeration(*args, **kwargs): return ifcopenshell.create_entity('IfcPropertyEnumeration', 'IFC4', *args, **kwargs)


def IfcPropertyListValue(*args, **kwargs): return ifcopenshell.create_entity('IfcPropertyListValue', 'IFC4', *args, **kwargs)


def IfcPropertyReferenceValue(*args, **kwargs): return ifcopenshell.create_entity('IfcPropertyReferenceValue', 'IFC4', *args, **kwargs)


def IfcPropertySet(*args, **kwargs): return ifcopenshell.create_entity('IfcPropertySet', 'IFC4', *args, **kwargs)


def IfcPropertySetDefinition(*args, **kwargs): return ifcopenshell.create_entity('IfcPropertySetDefinition', 'IFC4', *args, **kwargs)


def IfcPropertySetTemplate(*args, **kwargs): return ifcopenshell.create_entity('IfcPropertySetTemplate', 'IFC4', *args, **kwargs)


def IfcPropertySingleValue(*args, **kwargs): return ifcopenshell.create_entity('IfcPropertySingleValue', 'IFC4', *args, **kwargs)


def IfcPropertyTableValue(*args, **kwargs): return ifcopenshell.create_entity('IfcPropertyTableValue', 'IFC4', *args, **kwargs)


def IfcPropertyTemplate(*args, **kwargs): return ifcopenshell.create_entity('IfcPropertyTemplate', 'IFC4', *args, **kwargs)


def IfcPropertyTemplateDefinition(*args, **kwargs): return ifcopenshell.create_entity('IfcPropertyTemplateDefinition', 'IFC4', *args, **kwargs)


def IfcProtectiveDevice(*args, **kwargs): return ifcopenshell.create_entity('IfcProtectiveDevice', 'IFC4', *args, **kwargs)


def IfcProtectiveDeviceTrippingUnit(*args, **kwargs): return ifcopenshell.create_entity('IfcProtectiveDeviceTrippingUnit', 'IFC4', *args, **kwargs)


def IfcProtectiveDeviceTrippingUnitType(*args, **kwargs): return ifcopenshell.create_entity('IfcProtectiveDeviceTrippingUnitType', 'IFC4', *args, **kwargs)


def IfcProtectiveDeviceType(*args, **kwargs): return ifcopenshell.create_entity('IfcProtectiveDeviceType', 'IFC4', *args, **kwargs)


def IfcProxy(*args, **kwargs): return ifcopenshell.create_entity('IfcProxy', 'IFC4', *args, **kwargs)


def IfcPump(*args, **kwargs): return ifcopenshell.create_entity('IfcPump', 'IFC4', *args, **kwargs)


def IfcPumpType(*args, **kwargs): return ifcopenshell.create_entity('IfcPumpType', 'IFC4', *args, **kwargs)


def IfcQuantityArea(*args, **kwargs): return ifcopenshell.create_entity('IfcQuantityArea', 'IFC4', *args, **kwargs)


def IfcQuantityCount(*args, **kwargs): return ifcopenshell.create_entity('IfcQuantityCount', 'IFC4', *args, **kwargs)


def IfcQuantityLength(*args, **kwargs): return ifcopenshell.create_entity('IfcQuantityLength', 'IFC4', *args, **kwargs)


def IfcQuantitySet(*args, **kwargs): return ifcopenshell.create_entity('IfcQuantitySet', 'IFC4', *args, **kwargs)


def IfcQuantityTime(*args, **kwargs): return ifcopenshell.create_entity('IfcQuantityTime', 'IFC4', *args, **kwargs)


def IfcQuantityVolume(*args, **kwargs): return ifcopenshell.create_entity('IfcQuantityVolume', 'IFC4', *args, **kwargs)


def IfcQuantityWeight(*args, **kwargs): return ifcopenshell.create_entity('IfcQuantityWeight', 'IFC4', *args, **kwargs)


def IfcRailing(*args, **kwargs): return ifcopenshell.create_entity('IfcRailing', 'IFC4', *args, **kwargs)


def IfcRailingType(*args, **kwargs): return ifcopenshell.create_entity('IfcRailingType', 'IFC4', *args, **kwargs)


def IfcRamp(*args, **kwargs): return ifcopenshell.create_entity('IfcRamp', 'IFC4', *args, **kwargs)


def IfcRampFlight(*args, **kwargs): return ifcopenshell.create_entity('IfcRampFlight', 'IFC4', *args, **kwargs)


def IfcRampFlightType(*args, **kwargs): return ifcopenshell.create_entity('IfcRampFlightType', 'IFC4', *args, **kwargs)


def IfcRampType(*args, **kwargs): return ifcopenshell.create_entity('IfcRampType', 'IFC4', *args, **kwargs)


def IfcRationalBSplineCurveWithKnots(*args, **kwargs): return ifcopenshell.create_entity('IfcRationalBSplineCurveWithKnots', 'IFC4', *args, **kwargs)


def IfcRationalBSplineSurfaceWithKnots(*args, **kwargs): return ifcopenshell.create_entity('IfcRationalBSplineSurfaceWithKnots', 'IFC4', *args, **kwargs)


def IfcRectangleHollowProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcRectangleHollowProfileDef', 'IFC4', *args, **kwargs)


def IfcRectangleProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcRectangleProfileDef', 'IFC4', *args, **kwargs)


def IfcRectangularPyramid(*args, **kwargs): return ifcopenshell.create_entity('IfcRectangularPyramid', 'IFC4', *args, **kwargs)


def IfcRectangularTrimmedSurface(*args, **kwargs): return ifcopenshell.create_entity('IfcRectangularTrimmedSurface', 'IFC4', *args, **kwargs)


def IfcRecurrencePattern(*args, **kwargs): return ifcopenshell.create_entity('IfcRecurrencePattern', 'IFC4', *args, **kwargs)


def IfcReference(*args, **kwargs): return ifcopenshell.create_entity('IfcReference', 'IFC4', *args, **kwargs)


def IfcRegularTimeSeries(*args, **kwargs): return ifcopenshell.create_entity('IfcRegularTimeSeries', 'IFC4', *args, **kwargs)


def IfcReinforcementBarProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcReinforcementBarProperties', 'IFC4', *args, **kwargs)


def IfcReinforcementDefinitionProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcReinforcementDefinitionProperties', 'IFC4', *args, **kwargs)


def IfcReinforcingBar(*args, **kwargs): return ifcopenshell.create_entity('IfcReinforcingBar', 'IFC4', *args, **kwargs)


def IfcReinforcingBarType(*args, **kwargs): return ifcopenshell.create_entity('IfcReinforcingBarType', 'IFC4', *args, **kwargs)


def IfcReinforcingElement(*args, **kwargs): return ifcopenshell.create_entity('IfcReinforcingElement', 'IFC4', *args, **kwargs)


def IfcReinforcingElementType(*args, **kwargs): return ifcopenshell.create_entity('IfcReinforcingElementType', 'IFC4', *args, **kwargs)


def IfcReinforcingMesh(*args, **kwargs): return ifcopenshell.create_entity('IfcReinforcingMesh', 'IFC4', *args, **kwargs)


def IfcReinforcingMeshType(*args, **kwargs): return ifcopenshell.create_entity('IfcReinforcingMeshType', 'IFC4', *args, **kwargs)


def IfcRelAggregates(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAggregates', 'IFC4', *args, **kwargs)


def IfcRelAssigns(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssigns', 'IFC4', *args, **kwargs)


def IfcRelAssignsToActor(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssignsToActor', 'IFC4', *args, **kwargs)


def IfcRelAssignsToControl(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssignsToControl', 'IFC4', *args, **kwargs)


def IfcRelAssignsToGroup(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssignsToGroup', 'IFC4', *args, **kwargs)


def IfcRelAssignsToGroupByFactor(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssignsToGroupByFactor', 'IFC4', *args, **kwargs)


def IfcRelAssignsToProcess(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssignsToProcess', 'IFC4', *args, **kwargs)


def IfcRelAssignsToProduct(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssignsToProduct', 'IFC4', *args, **kwargs)


def IfcRelAssignsToResource(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssignsToResource', 'IFC4', *args, **kwargs)


def IfcRelAssociates(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssociates', 'IFC4', *args, **kwargs)


def IfcRelAssociatesApproval(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssociatesApproval', 'IFC4', *args, **kwargs)


def IfcRelAssociatesClassification(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssociatesClassification', 'IFC4', *args, **kwargs)


def IfcRelAssociatesConstraint(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssociatesConstraint', 'IFC4', *args, **kwargs)


def IfcRelAssociatesDocument(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssociatesDocument', 'IFC4', *args, **kwargs)


def IfcRelAssociatesLibrary(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssociatesLibrary', 'IFC4', *args, **kwargs)


def IfcRelAssociatesMaterial(*args, **kwargs): return ifcopenshell.create_entity('IfcRelAssociatesMaterial', 'IFC4', *args, **kwargs)


def IfcRelConnects(*args, **kwargs): return ifcopenshell.create_entity('IfcRelConnects', 'IFC4', *args, **kwargs)


def IfcRelConnectsElements(*args, **kwargs): return ifcopenshell.create_entity('IfcRelConnectsElements', 'IFC4', *args, **kwargs)


def IfcRelConnectsPathElements(*args, **kwargs): return ifcopenshell.create_entity('IfcRelConnectsPathElements', 'IFC4', *args, **kwargs)


def IfcRelConnectsPortToElement(*args, **kwargs): return ifcopenshell.create_entity('IfcRelConnectsPortToElement', 'IFC4', *args, **kwargs)


def IfcRelConnectsPorts(*args, **kwargs): return ifcopenshell.create_entity('IfcRelConnectsPorts', 'IFC4', *args, **kwargs)


def IfcRelConnectsStructuralActivity(*args, **kwargs): return ifcopenshell.create_entity('IfcRelConnectsStructuralActivity', 'IFC4', *args, **kwargs)


def IfcRelConnectsStructuralMember(*args, **kwargs): return ifcopenshell.create_entity('IfcRelConnectsStructuralMember', 'IFC4', *args, **kwargs)


def IfcRelConnectsWithEccentricity(*args, **kwargs): return ifcopenshell.create_entity('IfcRelConnectsWithEccentricity', 'IFC4', *args, **kwargs)


def IfcRelConnectsWithRealizingElements(*args, **kwargs): return ifcopenshell.create_entity('IfcRelConnectsWithRealizingElements', 'IFC4', *args, **kwargs)


def IfcRelContainedInSpatialStructure(*args, **kwargs): return ifcopenshell.create_entity('IfcRelContainedInSpatialStructure', 'IFC4', *args, **kwargs)


def IfcRelCoversBldgElements(*args, **kwargs): return ifcopenshell.create_entity('IfcRelCoversBldgElements', 'IFC4', *args, **kwargs)


def IfcRelCoversSpaces(*args, **kwargs): return ifcopenshell.create_entity('IfcRelCoversSpaces', 'IFC4', *args, **kwargs)


def IfcRelDeclares(*args, **kwargs): return ifcopenshell.create_entity('IfcRelDeclares', 'IFC4', *args, **kwargs)


def IfcRelDecomposes(*args, **kwargs): return ifcopenshell.create_entity('IfcRelDecomposes', 'IFC4', *args, **kwargs)


def IfcRelDefines(*args, **kwargs): return ifcopenshell.create_entity('IfcRelDefines', 'IFC4', *args, **kwargs)


def IfcRelDefinesByObject(*args, **kwargs): return ifcopenshell.create_entity('IfcRelDefinesByObject', 'IFC4', *args, **kwargs)


def IfcRelDefinesByProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcRelDefinesByProperties', 'IFC4', *args, **kwargs)


def IfcRelDefinesByTemplate(*args, **kwargs): return ifcopenshell.create_entity('IfcRelDefinesByTemplate', 'IFC4', *args, **kwargs)


def IfcRelDefinesByType(*args, **kwargs): return ifcopenshell.create_entity('IfcRelDefinesByType', 'IFC4', *args, **kwargs)


def IfcRelFillsElement(*args, **kwargs): return ifcopenshell.create_entity('IfcRelFillsElement', 'IFC4', *args, **kwargs)


def IfcRelFlowControlElements(*args, **kwargs): return ifcopenshell.create_entity('IfcRelFlowControlElements', 'IFC4', *args, **kwargs)


def IfcRelInterferesElements(*args, **kwargs): return ifcopenshell.create_entity('IfcRelInterferesElements', 'IFC4', *args, **kwargs)


def IfcRelNests(*args, **kwargs): return ifcopenshell.create_entity('IfcRelNests', 'IFC4', *args, **kwargs)


def IfcRelProjectsElement(*args, **kwargs): return ifcopenshell.create_entity('IfcRelProjectsElement', 'IFC4', *args, **kwargs)


def IfcRelReferencedInSpatialStructure(*args, **kwargs): return ifcopenshell.create_entity('IfcRelReferencedInSpatialStructure', 'IFC4', *args, **kwargs)


def IfcRelSequence(*args, **kwargs): return ifcopenshell.create_entity('IfcRelSequence', 'IFC4', *args, **kwargs)


def IfcRelServicesBuildings(*args, **kwargs): return ifcopenshell.create_entity('IfcRelServicesBuildings', 'IFC4', *args, **kwargs)


def IfcRelSpaceBoundary(*args, **kwargs): return ifcopenshell.create_entity('IfcRelSpaceBoundary', 'IFC4', *args, **kwargs)


def IfcRelSpaceBoundary1stLevel(*args, **kwargs): return ifcopenshell.create_entity('IfcRelSpaceBoundary1stLevel', 'IFC4', *args, **kwargs)


def IfcRelSpaceBoundary2ndLevel(*args, **kwargs): return ifcopenshell.create_entity('IfcRelSpaceBoundary2ndLevel', 'IFC4', *args, **kwargs)


def IfcRelVoidsElement(*args, **kwargs): return ifcopenshell.create_entity('IfcRelVoidsElement', 'IFC4', *args, **kwargs)


def IfcRelationship(*args, **kwargs): return ifcopenshell.create_entity('IfcRelationship', 'IFC4', *args, **kwargs)


def IfcReparametrisedCompositeCurveSegment(*args, **kwargs): return ifcopenshell.create_entity('IfcReparametrisedCompositeCurveSegment', 'IFC4', *args, **kwargs)


def IfcRepresentation(*args, **kwargs): return ifcopenshell.create_entity('IfcRepresentation', 'IFC4', *args, **kwargs)


def IfcRepresentationContext(*args, **kwargs): return ifcopenshell.create_entity('IfcRepresentationContext', 'IFC4', *args, **kwargs)


def IfcRepresentationItem(*args, **kwargs): return ifcopenshell.create_entity('IfcRepresentationItem', 'IFC4', *args, **kwargs)


def IfcRepresentationMap(*args, **kwargs): return ifcopenshell.create_entity('IfcRepresentationMap', 'IFC4', *args, **kwargs)


def IfcResource(*args, **kwargs): return ifcopenshell.create_entity('IfcResource', 'IFC4', *args, **kwargs)


def IfcResourceApprovalRelationship(*args, **kwargs): return ifcopenshell.create_entity('IfcResourceApprovalRelationship', 'IFC4', *args, **kwargs)


def IfcResourceConstraintRelationship(*args, **kwargs): return ifcopenshell.create_entity('IfcResourceConstraintRelationship', 'IFC4', *args, **kwargs)


def IfcResourceLevelRelationship(*args, **kwargs): return ifcopenshell.create_entity('IfcResourceLevelRelationship', 'IFC4', *args, **kwargs)


def IfcResourceTime(*args, **kwargs): return ifcopenshell.create_entity('IfcResourceTime', 'IFC4', *args, **kwargs)


def IfcRevolvedAreaSolid(*args, **kwargs): return ifcopenshell.create_entity('IfcRevolvedAreaSolid', 'IFC4', *args, **kwargs)


def IfcRevolvedAreaSolidTapered(*args, **kwargs): return ifcopenshell.create_entity('IfcRevolvedAreaSolidTapered', 'IFC4', *args, **kwargs)


def IfcRightCircularCone(*args, **kwargs): return ifcopenshell.create_entity('IfcRightCircularCone', 'IFC4', *args, **kwargs)


def IfcRightCircularCylinder(*args, **kwargs): return ifcopenshell.create_entity('IfcRightCircularCylinder', 'IFC4', *args, **kwargs)


def IfcRoof(*args, **kwargs): return ifcopenshell.create_entity('IfcRoof', 'IFC4', *args, **kwargs)


def IfcRoofType(*args, **kwargs): return ifcopenshell.create_entity('IfcRoofType', 'IFC4', *args, **kwargs)


def IfcRoot(*args, **kwargs): return ifcopenshell.create_entity('IfcRoot', 'IFC4', *args, **kwargs)


def IfcRoundedRectangleProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcRoundedRectangleProfileDef', 'IFC4', *args, **kwargs)


def IfcSIUnit(*args, **kwargs): return ifcopenshell.create_entity('IfcSIUnit', 'IFC4', *args, **kwargs)


def IfcSanitaryTerminal(*args, **kwargs): return ifcopenshell.create_entity('IfcSanitaryTerminal', 'IFC4', *args, **kwargs)


def IfcSanitaryTerminalType(*args, **kwargs): return ifcopenshell.create_entity('IfcSanitaryTerminalType', 'IFC4', *args, **kwargs)


def IfcSchedulingTime(*args, **kwargs): return ifcopenshell.create_entity('IfcSchedulingTime', 'IFC4', *args, **kwargs)


def IfcSeamCurve(*args, **kwargs): return ifcopenshell.create_entity('IfcSeamCurve', 'IFC4', *args, **kwargs)


def IfcSectionProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcSectionProperties', 'IFC4', *args, **kwargs)


def IfcSectionReinforcementProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcSectionReinforcementProperties', 'IFC4', *args, **kwargs)


def IfcSectionedSpine(*args, **kwargs): return ifcopenshell.create_entity('IfcSectionedSpine', 'IFC4', *args, **kwargs)


def IfcSensor(*args, **kwargs): return ifcopenshell.create_entity('IfcSensor', 'IFC4', *args, **kwargs)


def IfcSensorType(*args, **kwargs): return ifcopenshell.create_entity('IfcSensorType', 'IFC4', *args, **kwargs)


def IfcShadingDevice(*args, **kwargs): return ifcopenshell.create_entity('IfcShadingDevice', 'IFC4', *args, **kwargs)


def IfcShadingDeviceType(*args, **kwargs): return ifcopenshell.create_entity('IfcShadingDeviceType', 'IFC4', *args, **kwargs)


def IfcShapeAspect(*args, **kwargs): return ifcopenshell.create_entity('IfcShapeAspect', 'IFC4', *args, **kwargs)


def IfcShapeModel(*args, **kwargs): return ifcopenshell.create_entity('IfcShapeModel', 'IFC4', *args, **kwargs)


def IfcShapeRepresentation(*args, **kwargs): return ifcopenshell.create_entity('IfcShapeRepresentation', 'IFC4', *args, **kwargs)


def IfcShellBasedSurfaceModel(*args, **kwargs): return ifcopenshell.create_entity('IfcShellBasedSurfaceModel', 'IFC4', *args, **kwargs)


def IfcSimpleProperty(*args, **kwargs): return ifcopenshell.create_entity('IfcSimpleProperty', 'IFC4', *args, **kwargs)


def IfcSimplePropertyTemplate(*args, **kwargs): return ifcopenshell.create_entity('IfcSimplePropertyTemplate', 'IFC4', *args, **kwargs)


def IfcSite(*args, **kwargs): return ifcopenshell.create_entity('IfcSite', 'IFC4', *args, **kwargs)


def IfcSlab(*args, **kwargs): return ifcopenshell.create_entity('IfcSlab', 'IFC4', *args, **kwargs)


def IfcSlabElementedCase(*args, **kwargs): return ifcopenshell.create_entity('IfcSlabElementedCase', 'IFC4', *args, **kwargs)


def IfcSlabStandardCase(*args, **kwargs): return ifcopenshell.create_entity('IfcSlabStandardCase', 'IFC4', *args, **kwargs)


def IfcSlabType(*args, **kwargs): return ifcopenshell.create_entity('IfcSlabType', 'IFC4', *args, **kwargs)


def IfcSlippageConnectionCondition(*args, **kwargs): return ifcopenshell.create_entity('IfcSlippageConnectionCondition', 'IFC4', *args, **kwargs)


def IfcSolarDevice(*args, **kwargs): return ifcopenshell.create_entity('IfcSolarDevice', 'IFC4', *args, **kwargs)


def IfcSolarDeviceType(*args, **kwargs): return ifcopenshell.create_entity('IfcSolarDeviceType', 'IFC4', *args, **kwargs)


def IfcSolidModel(*args, **kwargs): return ifcopenshell.create_entity('IfcSolidModel', 'IFC4', *args, **kwargs)


def IfcSpace(*args, **kwargs): return ifcopenshell.create_entity('IfcSpace', 'IFC4', *args, **kwargs)


def IfcSpaceHeater(*args, **kwargs): return ifcopenshell.create_entity('IfcSpaceHeater', 'IFC4', *args, **kwargs)


def IfcSpaceHeaterType(*args, **kwargs): return ifcopenshell.create_entity('IfcSpaceHeaterType', 'IFC4', *args, **kwargs)


def IfcSpaceType(*args, **kwargs): return ifcopenshell.create_entity('IfcSpaceType', 'IFC4', *args, **kwargs)


def IfcSpatialElement(*args, **kwargs): return ifcopenshell.create_entity('IfcSpatialElement', 'IFC4', *args, **kwargs)


def IfcSpatialElementType(*args, **kwargs): return ifcopenshell.create_entity('IfcSpatialElementType', 'IFC4', *args, **kwargs)


def IfcSpatialStructureElement(*args, **kwargs): return ifcopenshell.create_entity('IfcSpatialStructureElement', 'IFC4', *args, **kwargs)


def IfcSpatialStructureElementType(*args, **kwargs): return ifcopenshell.create_entity('IfcSpatialStructureElementType', 'IFC4', *args, **kwargs)


def IfcSpatialZone(*args, **kwargs): return ifcopenshell.create_entity('IfcSpatialZone', 'IFC4', *args, **kwargs)


def IfcSpatialZoneType(*args, **kwargs): return ifcopenshell.create_entity('IfcSpatialZoneType', 'IFC4', *args, **kwargs)


def IfcSphere(*args, **kwargs): return ifcopenshell.create_entity('IfcSphere', 'IFC4', *args, **kwargs)


def IfcSphericalSurface(*args, **kwargs): return ifcopenshell.create_entity('IfcSphericalSurface', 'IFC4', *args, **kwargs)


def IfcStackTerminal(*args, **kwargs): return ifcopenshell.create_entity('IfcStackTerminal', 'IFC4', *args, **kwargs)


def IfcStackTerminalType(*args, **kwargs): return ifcopenshell.create_entity('IfcStackTerminalType', 'IFC4', *args, **kwargs)


def IfcStair(*args, **kwargs): return ifcopenshell.create_entity('IfcStair', 'IFC4', *args, **kwargs)


def IfcStairFlight(*args, **kwargs): return ifcopenshell.create_entity('IfcStairFlight', 'IFC4', *args, **kwargs)


def IfcStairFlightType(*args, **kwargs): return ifcopenshell.create_entity('IfcStairFlightType', 'IFC4', *args, **kwargs)


def IfcStairType(*args, **kwargs): return ifcopenshell.create_entity('IfcStairType', 'IFC4', *args, **kwargs)


def IfcStructuralAction(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralAction', 'IFC4', *args, **kwargs)


def IfcStructuralActivity(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralActivity', 'IFC4', *args, **kwargs)


def IfcStructuralAnalysisModel(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralAnalysisModel', 'IFC4', *args, **kwargs)


def IfcStructuralConnection(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralConnection', 'IFC4', *args, **kwargs)


def IfcStructuralConnectionCondition(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralConnectionCondition', 'IFC4', *args, **kwargs)


def IfcStructuralCurveAction(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralCurveAction', 'IFC4', *args, **kwargs)


def IfcStructuralCurveConnection(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralCurveConnection', 'IFC4', *args, **kwargs)


def IfcStructuralCurveMember(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralCurveMember', 'IFC4', *args, **kwargs)


def IfcStructuralCurveMemberVarying(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralCurveMemberVarying', 'IFC4', *args, **kwargs)


def IfcStructuralCurveReaction(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralCurveReaction', 'IFC4', *args, **kwargs)


def IfcStructuralItem(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralItem', 'IFC4', *args, **kwargs)


def IfcStructuralLinearAction(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralLinearAction', 'IFC4', *args, **kwargs)


def IfcStructuralLoad(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralLoad', 'IFC4', *args, **kwargs)


def IfcStructuralLoadCase(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralLoadCase', 'IFC4', *args, **kwargs)


def IfcStructuralLoadConfiguration(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralLoadConfiguration', 'IFC4', *args, **kwargs)


def IfcStructuralLoadGroup(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralLoadGroup', 'IFC4', *args, **kwargs)


def IfcStructuralLoadLinearForce(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralLoadLinearForce', 'IFC4', *args, **kwargs)


def IfcStructuralLoadOrResult(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralLoadOrResult', 'IFC4', *args, **kwargs)


def IfcStructuralLoadPlanarForce(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralLoadPlanarForce', 'IFC4', *args, **kwargs)


def IfcStructuralLoadSingleDisplacement(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralLoadSingleDisplacement', 'IFC4', *args, **kwargs)


def IfcStructuralLoadSingleDisplacementDistortion(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralLoadSingleDisplacementDistortion', 'IFC4', *args, **kwargs)


def IfcStructuralLoadSingleForce(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralLoadSingleForce', 'IFC4', *args, **kwargs)


def IfcStructuralLoadSingleForceWarping(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralLoadSingleForceWarping', 'IFC4', *args, **kwargs)


def IfcStructuralLoadStatic(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralLoadStatic', 'IFC4', *args, **kwargs)


def IfcStructuralLoadTemperature(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralLoadTemperature', 'IFC4', *args, **kwargs)


def IfcStructuralMember(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralMember', 'IFC4', *args, **kwargs)


def IfcStructuralPlanarAction(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralPlanarAction', 'IFC4', *args, **kwargs)


def IfcStructuralPointAction(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralPointAction', 'IFC4', *args, **kwargs)


def IfcStructuralPointConnection(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralPointConnection', 'IFC4', *args, **kwargs)


def IfcStructuralPointReaction(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralPointReaction', 'IFC4', *args, **kwargs)


def IfcStructuralReaction(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralReaction', 'IFC4', *args, **kwargs)


def IfcStructuralResultGroup(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralResultGroup', 'IFC4', *args, **kwargs)


def IfcStructuralSurfaceAction(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralSurfaceAction', 'IFC4', *args, **kwargs)


def IfcStructuralSurfaceConnection(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralSurfaceConnection', 'IFC4', *args, **kwargs)


def IfcStructuralSurfaceMember(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralSurfaceMember', 'IFC4', *args, **kwargs)


def IfcStructuralSurfaceMemberVarying(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralSurfaceMemberVarying', 'IFC4', *args, **kwargs)


def IfcStructuralSurfaceReaction(*args, **kwargs): return ifcopenshell.create_entity('IfcStructuralSurfaceReaction', 'IFC4', *args, **kwargs)


def IfcStyleModel(*args, **kwargs): return ifcopenshell.create_entity('IfcStyleModel', 'IFC4', *args, **kwargs)


def IfcStyledItem(*args, **kwargs): return ifcopenshell.create_entity('IfcStyledItem', 'IFC4', *args, **kwargs)


def IfcStyledRepresentation(*args, **kwargs): return ifcopenshell.create_entity('IfcStyledRepresentation', 'IFC4', *args, **kwargs)


def IfcSubContractResource(*args, **kwargs): return ifcopenshell.create_entity('IfcSubContractResource', 'IFC4', *args, **kwargs)


def IfcSubContractResourceType(*args, **kwargs): return ifcopenshell.create_entity('IfcSubContractResourceType', 'IFC4', *args, **kwargs)


def IfcSubedge(*args, **kwargs): return ifcopenshell.create_entity('IfcSubedge', 'IFC4', *args, **kwargs)


def IfcSurface(*args, **kwargs): return ifcopenshell.create_entity('IfcSurface', 'IFC4', *args, **kwargs)


def IfcSurfaceCurve(*args, **kwargs): return ifcopenshell.create_entity('IfcSurfaceCurve', 'IFC4', *args, **kwargs)


def IfcSurfaceCurveSweptAreaSolid(*args, **kwargs): return ifcopenshell.create_entity('IfcSurfaceCurveSweptAreaSolid', 'IFC4', *args, **kwargs)


def IfcSurfaceFeature(*args, **kwargs): return ifcopenshell.create_entity('IfcSurfaceFeature', 'IFC4', *args, **kwargs)


def IfcSurfaceOfLinearExtrusion(*args, **kwargs): return ifcopenshell.create_entity('IfcSurfaceOfLinearExtrusion', 'IFC4', *args, **kwargs)


def IfcSurfaceOfRevolution(*args, **kwargs): return ifcopenshell.create_entity('IfcSurfaceOfRevolution', 'IFC4', *args, **kwargs)


def IfcSurfaceReinforcementArea(*args, **kwargs): return ifcopenshell.create_entity('IfcSurfaceReinforcementArea', 'IFC4', *args, **kwargs)


def IfcSurfaceStyle(*args, **kwargs): return ifcopenshell.create_entity('IfcSurfaceStyle', 'IFC4', *args, **kwargs)


def IfcSurfaceStyleLighting(*args, **kwargs): return ifcopenshell.create_entity('IfcSurfaceStyleLighting', 'IFC4', *args, **kwargs)


def IfcSurfaceStyleRefraction(*args, **kwargs): return ifcopenshell.create_entity('IfcSurfaceStyleRefraction', 'IFC4', *args, **kwargs)


def IfcSurfaceStyleRendering(*args, **kwargs): return ifcopenshell.create_entity('IfcSurfaceStyleRendering', 'IFC4', *args, **kwargs)


def IfcSurfaceStyleShading(*args, **kwargs): return ifcopenshell.create_entity('IfcSurfaceStyleShading', 'IFC4', *args, **kwargs)


def IfcSurfaceStyleWithTextures(*args, **kwargs): return ifcopenshell.create_entity('IfcSurfaceStyleWithTextures', 'IFC4', *args, **kwargs)


def IfcSurfaceTexture(*args, **kwargs): return ifcopenshell.create_entity('IfcSurfaceTexture', 'IFC4', *args, **kwargs)


def IfcSweptAreaSolid(*args, **kwargs): return ifcopenshell.create_entity('IfcSweptAreaSolid', 'IFC4', *args, **kwargs)


def IfcSweptDiskSolid(*args, **kwargs): return ifcopenshell.create_entity('IfcSweptDiskSolid', 'IFC4', *args, **kwargs)


def IfcSweptDiskSolidPolygonal(*args, **kwargs): return ifcopenshell.create_entity('IfcSweptDiskSolidPolygonal', 'IFC4', *args, **kwargs)


def IfcSweptSurface(*args, **kwargs): return ifcopenshell.create_entity('IfcSweptSurface', 'IFC4', *args, **kwargs)


def IfcSwitchingDevice(*args, **kwargs): return ifcopenshell.create_entity('IfcSwitchingDevice', 'IFC4', *args, **kwargs)


def IfcSwitchingDeviceType(*args, **kwargs): return ifcopenshell.create_entity('IfcSwitchingDeviceType', 'IFC4', *args, **kwargs)


def IfcSystem(*args, **kwargs): return ifcopenshell.create_entity('IfcSystem', 'IFC4', *args, **kwargs)


def IfcSystemFurnitureElement(*args, **kwargs): return ifcopenshell.create_entity('IfcSystemFurnitureElement', 'IFC4', *args, **kwargs)


def IfcSystemFurnitureElementType(*args, **kwargs): return ifcopenshell.create_entity('IfcSystemFurnitureElementType', 'IFC4', *args, **kwargs)


def IfcTShapeProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcTShapeProfileDef', 'IFC4', *args, **kwargs)


def IfcTable(*args, **kwargs): return ifcopenshell.create_entity('IfcTable', 'IFC4', *args, **kwargs)


def IfcTableColumn(*args, **kwargs): return ifcopenshell.create_entity('IfcTableColumn', 'IFC4', *args, **kwargs)


def IfcTableRow(*args, **kwargs): return ifcopenshell.create_entity('IfcTableRow', 'IFC4', *args, **kwargs)


def IfcTank(*args, **kwargs): return ifcopenshell.create_entity('IfcTank', 'IFC4', *args, **kwargs)


def IfcTankType(*args, **kwargs): return ifcopenshell.create_entity('IfcTankType', 'IFC4', *args, **kwargs)


def IfcTask(*args, **kwargs): return ifcopenshell.create_entity('IfcTask', 'IFC4', *args, **kwargs)


def IfcTaskTime(*args, **kwargs): return ifcopenshell.create_entity('IfcTaskTime', 'IFC4', *args, **kwargs)


def IfcTaskTimeRecurring(*args, **kwargs): return ifcopenshell.create_entity('IfcTaskTimeRecurring', 'IFC4', *args, **kwargs)


def IfcTaskType(*args, **kwargs): return ifcopenshell.create_entity('IfcTaskType', 'IFC4', *args, **kwargs)


def IfcTelecomAddress(*args, **kwargs): return ifcopenshell.create_entity('IfcTelecomAddress', 'IFC4', *args, **kwargs)


def IfcTendon(*args, **kwargs): return ifcopenshell.create_entity('IfcTendon', 'IFC4', *args, **kwargs)


def IfcTendonAnchor(*args, **kwargs): return ifcopenshell.create_entity('IfcTendonAnchor', 'IFC4', *args, **kwargs)


def IfcTendonAnchorType(*args, **kwargs): return ifcopenshell.create_entity('IfcTendonAnchorType', 'IFC4', *args, **kwargs)


def IfcTendonType(*args, **kwargs): return ifcopenshell.create_entity('IfcTendonType', 'IFC4', *args, **kwargs)


def IfcTessellatedFaceSet(*args, **kwargs): return ifcopenshell.create_entity('IfcTessellatedFaceSet', 'IFC4', *args, **kwargs)


def IfcTessellatedItem(*args, **kwargs): return ifcopenshell.create_entity('IfcTessellatedItem', 'IFC4', *args, **kwargs)


def IfcTextLiteral(*args, **kwargs): return ifcopenshell.create_entity('IfcTextLiteral', 'IFC4', *args, **kwargs)


def IfcTextLiteralWithExtent(*args, **kwargs): return ifcopenshell.create_entity('IfcTextLiteralWithExtent', 'IFC4', *args, **kwargs)


def IfcTextStyle(*args, **kwargs): return ifcopenshell.create_entity('IfcTextStyle', 'IFC4', *args, **kwargs)


def IfcTextStyleFontModel(*args, **kwargs): return ifcopenshell.create_entity('IfcTextStyleFontModel', 'IFC4', *args, **kwargs)


def IfcTextStyleForDefinedFont(*args, **kwargs): return ifcopenshell.create_entity('IfcTextStyleForDefinedFont', 'IFC4', *args, **kwargs)


def IfcTextStyleTextModel(*args, **kwargs): return ifcopenshell.create_entity('IfcTextStyleTextModel', 'IFC4', *args, **kwargs)


def IfcTextureCoordinate(*args, **kwargs): return ifcopenshell.create_entity('IfcTextureCoordinate', 'IFC4', *args, **kwargs)


def IfcTextureCoordinateGenerator(*args, **kwargs): return ifcopenshell.create_entity('IfcTextureCoordinateGenerator', 'IFC4', *args, **kwargs)


def IfcTextureMap(*args, **kwargs): return ifcopenshell.create_entity('IfcTextureMap', 'IFC4', *args, **kwargs)


def IfcTextureVertex(*args, **kwargs): return ifcopenshell.create_entity('IfcTextureVertex', 'IFC4', *args, **kwargs)


def IfcTextureVertexList(*args, **kwargs): return ifcopenshell.create_entity('IfcTextureVertexList', 'IFC4', *args, **kwargs)


def IfcTimePeriod(*args, **kwargs): return ifcopenshell.create_entity('IfcTimePeriod', 'IFC4', *args, **kwargs)


def IfcTimeSeries(*args, **kwargs): return ifcopenshell.create_entity('IfcTimeSeries', 'IFC4', *args, **kwargs)


def IfcTimeSeriesValue(*args, **kwargs): return ifcopenshell.create_entity('IfcTimeSeriesValue', 'IFC4', *args, **kwargs)


def IfcTopologicalRepresentationItem(*args, **kwargs): return ifcopenshell.create_entity('IfcTopologicalRepresentationItem', 'IFC4', *args, **kwargs)


def IfcTopologyRepresentation(*args, **kwargs): return ifcopenshell.create_entity('IfcTopologyRepresentation', 'IFC4', *args, **kwargs)


def IfcToroidalSurface(*args, **kwargs): return ifcopenshell.create_entity('IfcToroidalSurface', 'IFC4', *args, **kwargs)


def IfcTransformer(*args, **kwargs): return ifcopenshell.create_entity('IfcTransformer', 'IFC4', *args, **kwargs)


def IfcTransformerType(*args, **kwargs): return ifcopenshell.create_entity('IfcTransformerType', 'IFC4', *args, **kwargs)


def IfcTransportElement(*args, **kwargs): return ifcopenshell.create_entity('IfcTransportElement', 'IFC4', *args, **kwargs)


def IfcTransportElementType(*args, **kwargs): return ifcopenshell.create_entity('IfcTransportElementType', 'IFC4', *args, **kwargs)


def IfcTrapeziumProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcTrapeziumProfileDef', 'IFC4', *args, **kwargs)


def IfcTriangulatedFaceSet(*args, **kwargs): return ifcopenshell.create_entity('IfcTriangulatedFaceSet', 'IFC4', *args, **kwargs)


def IfcTrimmedCurve(*args, **kwargs): return ifcopenshell.create_entity('IfcTrimmedCurve', 'IFC4', *args, **kwargs)


def IfcTubeBundle(*args, **kwargs): return ifcopenshell.create_entity('IfcTubeBundle', 'IFC4', *args, **kwargs)


def IfcTubeBundleType(*args, **kwargs): return ifcopenshell.create_entity('IfcTubeBundleType', 'IFC4', *args, **kwargs)


def IfcTypeObject(*args, **kwargs): return ifcopenshell.create_entity('IfcTypeObject', 'IFC4', *args, **kwargs)


def IfcTypeProcess(*args, **kwargs): return ifcopenshell.create_entity('IfcTypeProcess', 'IFC4', *args, **kwargs)


def IfcTypeProduct(*args, **kwargs): return ifcopenshell.create_entity('IfcTypeProduct', 'IFC4', *args, **kwargs)


def IfcTypeResource(*args, **kwargs): return ifcopenshell.create_entity('IfcTypeResource', 'IFC4', *args, **kwargs)


def IfcUShapeProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcUShapeProfileDef', 'IFC4', *args, **kwargs)


def IfcUnitAssignment(*args, **kwargs): return ifcopenshell.create_entity('IfcUnitAssignment', 'IFC4', *args, **kwargs)


def IfcUnitaryControlElement(*args, **kwargs): return ifcopenshell.create_entity('IfcUnitaryControlElement', 'IFC4', *args, **kwargs)


def IfcUnitaryControlElementType(*args, **kwargs): return ifcopenshell.create_entity('IfcUnitaryControlElementType', 'IFC4', *args, **kwargs)


def IfcUnitaryEquipment(*args, **kwargs): return ifcopenshell.create_entity('IfcUnitaryEquipment', 'IFC4', *args, **kwargs)


def IfcUnitaryEquipmentType(*args, **kwargs): return ifcopenshell.create_entity('IfcUnitaryEquipmentType', 'IFC4', *args, **kwargs)


def IfcValve(*args, **kwargs): return ifcopenshell.create_entity('IfcValve', 'IFC4', *args, **kwargs)


def IfcValveType(*args, **kwargs): return ifcopenshell.create_entity('IfcValveType', 'IFC4', *args, **kwargs)


def IfcVector(*args, **kwargs): return ifcopenshell.create_entity('IfcVector', 'IFC4', *args, **kwargs)


def IfcVertex(*args, **kwargs): return ifcopenshell.create_entity('IfcVertex', 'IFC4', *args, **kwargs)


def IfcVertexLoop(*args, **kwargs): return ifcopenshell.create_entity('IfcVertexLoop', 'IFC4', *args, **kwargs)


def IfcVertexPoint(*args, **kwargs): return ifcopenshell.create_entity('IfcVertexPoint', 'IFC4', *args, **kwargs)


def IfcVibrationIsolator(*args, **kwargs): return ifcopenshell.create_entity('IfcVibrationIsolator', 'IFC4', *args, **kwargs)


def IfcVibrationIsolatorType(*args, **kwargs): return ifcopenshell.create_entity('IfcVibrationIsolatorType', 'IFC4', *args, **kwargs)


def IfcVirtualElement(*args, **kwargs): return ifcopenshell.create_entity('IfcVirtualElement', 'IFC4', *args, **kwargs)


def IfcVirtualGridIntersection(*args, **kwargs): return ifcopenshell.create_entity('IfcVirtualGridIntersection', 'IFC4', *args, **kwargs)


def IfcVoidingFeature(*args, **kwargs): return ifcopenshell.create_entity('IfcVoidingFeature', 'IFC4', *args, **kwargs)


def IfcWall(*args, **kwargs): return ifcopenshell.create_entity('IfcWall', 'IFC4', *args, **kwargs)


def IfcWallElementedCase(*args, **kwargs): return ifcopenshell.create_entity('IfcWallElementedCase', 'IFC4', *args, **kwargs)


def IfcWallStandardCase(*args, **kwargs): return ifcopenshell.create_entity('IfcWallStandardCase', 'IFC4', *args, **kwargs)


def IfcWallType(*args, **kwargs): return ifcopenshell.create_entity('IfcWallType', 'IFC4', *args, **kwargs)


def IfcWasteTerminal(*args, **kwargs): return ifcopenshell.create_entity('IfcWasteTerminal', 'IFC4', *args, **kwargs)


def IfcWasteTerminalType(*args, **kwargs): return ifcopenshell.create_entity('IfcWasteTerminalType', 'IFC4', *args, **kwargs)


def IfcWindow(*args, **kwargs): return ifcopenshell.create_entity('IfcWindow', 'IFC4', *args, **kwargs)


def IfcWindowLiningProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcWindowLiningProperties', 'IFC4', *args, **kwargs)


def IfcWindowPanelProperties(*args, **kwargs): return ifcopenshell.create_entity('IfcWindowPanelProperties', 'IFC4', *args, **kwargs)


def IfcWindowStandardCase(*args, **kwargs): return ifcopenshell.create_entity('IfcWindowStandardCase', 'IFC4', *args, **kwargs)


def IfcWindowStyle(*args, **kwargs): return ifcopenshell.create_entity('IfcWindowStyle', 'IFC4', *args, **kwargs)


def IfcWindowType(*args, **kwargs): return ifcopenshell.create_entity('IfcWindowType', 'IFC4', *args, **kwargs)


def IfcWorkCalendar(*args, **kwargs): return ifcopenshell.create_entity('IfcWorkCalendar', 'IFC4', *args, **kwargs)


def IfcWorkControl(*args, **kwargs): return ifcopenshell.create_entity('IfcWorkControl', 'IFC4', *args, **kwargs)


def IfcWorkPlan(*args, **kwargs): return ifcopenshell.create_entity('IfcWorkPlan', 'IFC4', *args, **kwargs)


def IfcWorkSchedule(*args, **kwargs): return ifcopenshell.create_entity('IfcWorkSchedule', 'IFC4', *args, **kwargs)


def IfcWorkTime(*args, **kwargs): return ifcopenshell.create_entity('IfcWorkTime', 'IFC4', *args, **kwargs)


def IfcZShapeProfileDef(*args, **kwargs): return ifcopenshell.create_entity('IfcZShapeProfileDef', 'IFC4', *args, **kwargs)


def IfcZone(*args, **kwargs): return ifcopenshell.create_entity('IfcZone', 'IFC4', *args, **kwargs)









































































































class IfcBoxAlignment_WR1:
    SCOPE = "type"
    TYPE_NAME = "IfcBoxAlignment"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):

        
        assert (self in ['top-left','top-middle','top-right','middle-left','center','middle-right','bottom-left','bottom-middle','bottom-right']) is not False
        




























class IfcCardinalPointReference_GreaterThanZero:
    SCOPE = "type"
    TYPE_NAME = "IfcCardinalPointReference"
    RULE_NAME = "GreaterThanZero"

    @staticmethod    
    def __call__(self):

        
        assert (self > 0) is not False
        








































class IfcCompoundPlaneAngleMeasure_MinutesInRange:
    SCOPE = "type"
    TYPE_NAME = "IfcCompoundPlaneAngleMeasure"
    RULE_NAME = "MinutesInRange"

    @staticmethod    
    def __call__(self):

        
        assert ((abs(self[2 - 1])) < 60) is not False
        



class IfcCompoundPlaneAngleMeasure_SecondsInRange:
    SCOPE = "type"
    TYPE_NAME = "IfcCompoundPlaneAngleMeasure"
    RULE_NAME = "SecondsInRange"

    @staticmethod    
    def __call__(self):

        
        assert ((abs(self[3 - 1])) < 60) is not False
        



class IfcCompoundPlaneAngleMeasure_MicrosecondsInRange:
    SCOPE = "type"
    TYPE_NAME = "IfcCompoundPlaneAngleMeasure"
    RULE_NAME = "MicrosecondsInRange"

    @staticmethod    
    def __call__(self):

        
        assert ((sizeof(self) == 3) or ((abs(self[4 - 1])) < 1000000)) is not False
        



class IfcCompoundPlaneAngleMeasure_ConsistentSign:
    SCOPE = "type"
    TYPE_NAME = "IfcCompoundPlaneAngleMeasure"
    RULE_NAME = "ConsistentSign"

    @staticmethod    
    def __call__(self):

        
        assert ((((self[1 - 1]) >= 0) and ((self[2 - 1]) >= 0) and ((self[3 - 1]) >= 0) and ((sizeof(self) == 3) or ((self[4 - 1]) >= 0))) or (((self[1 - 1]) <= 0) and ((self[2 - 1]) <= 0) and ((self[3 - 1]) <= 0) and ((sizeof(self) == 3) or ((self[4 - 1]) <= 0)))) is not False
        



























































































class IfcDayInMonthNumber_ValidRange:
    SCOPE = "type"
    TYPE_NAME = "IfcDayInMonthNumber"
    RULE_NAME = "ValidRange"

    @staticmethod    
    def __call__(self):

        
        assert (1 <= self <= 31) is not False
        




class IfcDayInWeekNumber_ValidRange:
    SCOPE = "type"
    TYPE_NAME = "IfcDayInWeekNumber"
    RULE_NAME = "ValidRange"

    @staticmethod    
    def __call__(self):

        
        assert (1 <= self <= 7) is not False
        
















class IfcDimensionCount_WR1:
    SCOPE = "type"
    TYPE_NAME = "IfcDimensionCount"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):

        
        assert (0 < self <= 3) is not False
        























































































































































class IfcFontStyle_WR1:
    SCOPE = "type"
    TYPE_NAME = "IfcFontStyle"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):

        
        assert (self in ['normal','italic','oblique']) is not False
        




class IfcFontVariant_WR1:
    SCOPE = "type"
    TYPE_NAME = "IfcFontVariant"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):

        
        assert (self in ['normal','small-caps']) is not False
        




class IfcFontWeight_WR1:
    SCOPE = "type"
    TYPE_NAME = "IfcFontWeight"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):

        
        assert (self in ['normal','small-caps','100','200','300','400','500','600','700','800','900']) is not False
        














































class IfcHeatingValueMeasure_WR1:
    SCOPE = "type"
    TYPE_NAME = "IfcHeatingValueMeasure"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):

        
        assert (self > 0.) is not False
        
























































































































































































class IfcMonthInYearNumber_ValidRange:
    SCOPE = "type"
    TYPE_NAME = "IfcMonthInYearNumber"
    RULE_NAME = "ValidRange"

    @staticmethod    
    def __call__(self):

        
        assert (1 <= self <= 12) is not False
        







class IfcNonNegativeLengthMeasure_NotNegative:
    SCOPE = "type"
    TYPE_NAME = "IfcNonNegativeLengthMeasure"
    RULE_NAME = "NotNegative"

    @staticmethod    
    def __call__(self):

        
        assert (self >= 0.) is not False
        




class IfcNormalisedRatioMeasure_WR1:
    SCOPE = "type"
    TYPE_NAME = "IfcNormalisedRatioMeasure"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):

        
        assert (0.0 <= self <= 1.0) is not False
        




























class IfcPHMeasure_WR21:
    SCOPE = "type"
    TYPE_NAME = "IfcPHMeasure"
    RULE_NAME = "WR21"

    @staticmethod    
    def __call__(self):

        
        assert (0.0 <= self <= 14.0) is not False
        











































class IfcPositiveInteger_WR1:
    SCOPE = "type"
    TYPE_NAME = "IfcPositiveInteger"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):

        
        assert (self > 0) is not False
        




class IfcPositiveLengthMeasure_WR1:
    SCOPE = "type"
    TYPE_NAME = "IfcPositiveLengthMeasure"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):

        
        assert (self > 0.) is not False
        




class IfcPositivePlaneAngleMeasure_WR1:
    SCOPE = "type"
    TYPE_NAME = "IfcPositivePlaneAngleMeasure"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):

        
        assert (self > 0.) is not False
        




class IfcPositiveRatioMeasure_WR1:
    SCOPE = "type"
    TYPE_NAME = "IfcPositiveRatioMeasure"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):

        
        assert (self > 0.) is not False
        



















































































































































































































class IfcSpecularRoughness_WR1:
    SCOPE = "type"
    TYPE_NAME = "IfcSpecularRoughness"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):

        
        assert (0.0 <= self <= 1.0) is not False
        















































































class IfcTextAlignment_WR1:
    SCOPE = "type"
    TYPE_NAME = "IfcTextAlignment"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):

        
        assert (self in ['left','right','center','justify']) is not False
        




class IfcTextDecoration_WR1:
    SCOPE = "type"
    TYPE_NAME = "IfcTextDecoration"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):

        
        assert (self in ['none','underline','overline','line-through','blink']) is not False
        













class IfcTextTransformation_WR1:
    SCOPE = "type"
    TYPE_NAME = "IfcTextTransformation"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):

        
        assert (self in ['capitalize','uppercase','lowercase','none']) is not False
        




















































































































































class IfcActorRole_WR1:
    SCOPE = "entity"
    TYPE_NAME = "IfcActorRole"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):
        role = self.Role
        
        assert ((role != IfcRoleEnum.USERDEFINED) or ((role == IfcRoleEnum.USERDEFINED) and exists(self.UserDefinedRole))) is not False
        




class IfcActuator_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcActuator"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcActuatorTypeEnum.USERDEFINED) or ((predefinedtype == IfcActuatorTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcActuator_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcActuator"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcactuatortype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcActuatorType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcActuatorType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcActuatorTypeEnum.USERDEFINED) or ((predefinedtype == IfcActuatorTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcAddress_WR1:
    SCOPE = "entity"
    TYPE_NAME = "IfcAddress"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):
        purpose = self.Purpose
        
        assert ((not exists(purpose)) or ((purpose != IfcAddressTypeEnum.USERDEFINED) or ((purpose == IfcAddressTypeEnum.USERDEFINED) and exists(self.UserDefinedPurpose)))) is not False
        




class IfcAdvancedBrep_HasAdvancedFaces:
    SCOPE = "entity"
    TYPE_NAME = "IfcAdvancedBrep"
    RULE_NAME = "HasAdvancedFaces"

    @staticmethod    
    def __call__(self):

        
        assert ((sizeof([afs for afs in self.Outer.CfsFaces if not 'ifc4.ifcadvancedface' in typeof(afs)])) == 0) is not False
        




class IfcAdvancedBrepWithVoids_VoidsHaveAdvancedFaces:
    SCOPE = "entity"
    TYPE_NAME = "IfcAdvancedBrepWithVoids"
    RULE_NAME = "VoidsHaveAdvancedFaces"

    @staticmethod    
    def __call__(self):
        voids = self.Voids
        
        assert ((sizeof([vsh for vsh in voids if (sizeof([afs for afs in vsh.CfsFaces if not 'ifc4.ifcadvancedface' in typeof(afs)])) == 0])) == 0) is not False
        




class IfcAdvancedFace_ApplicableSurface:
    SCOPE = "entity"
    TYPE_NAME = "IfcAdvancedFace"
    RULE_NAME = "ApplicableSurface"

    @staticmethod    
    def __call__(self):

        
        assert ((sizeof(['ifc4.ifcelementarysurface','ifc4.ifcsweptsurface','ifc4.ifcbsplinesurface'] * typeof(self.FaceSurface))) == 1) is not False
        



class IfcAdvancedFace_RequiresEdgeCurve:
    SCOPE = "entity"
    TYPE_NAME = "IfcAdvancedFace"
    RULE_NAME = "RequiresEdgeCurve"

    @staticmethod    
    def __call__(self):

        
        assert ((sizeof([elpfbnds for elpfbnds in [bnds for bnds in self.Bounds if 'ifc4.ifcedgeloop' in typeof(bnds.Bound)] if not (sizeof([oe for oe in elpfbnds.Bound.EdgeList if not 'ifc4.ifcedgecurve' in typeof(oe.EdgeElement)])) == 0])) == 0) is not False
        



class IfcAdvancedFace_ApplicableEdgeCurves:
    SCOPE = "entity"
    TYPE_NAME = "IfcAdvancedFace"
    RULE_NAME = "ApplicableEdgeCurves"

    @staticmethod    
    def __call__(self):

        
        assert ((sizeof([elpfbnds for elpfbnds in [bnds for bnds in self.Bounds if 'ifc4.ifcedgeloop' in typeof(bnds.Bound)] if not (sizeof([oe for oe in elpfbnds.Bound.EdgeList if not (sizeof(['ifc4.ifcline','ifc4.ifcconic','ifc4.ifcpolyline','ifc4.ifcbsplinecurve'] * typeof(oe.EdgeElement.EdgeGeometry))) == 1])) == 0])) == 0) is not False
        




class IfcAirTerminal_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcAirTerminal"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcAirTerminalTypeEnum.USERDEFINED) or ((predefinedtype == IfcAirTerminalTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcAirTerminal_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcAirTerminal"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcairterminaltype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcAirTerminalBox_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcAirTerminalBox"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcAirTerminalBoxTypeEnum.USERDEFINED) or ((predefinedtype == IfcAirTerminalBoxTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcAirTerminalBox_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcAirTerminalBox"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcairterminalboxtype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcAirTerminalBoxType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcAirTerminalBoxType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcAirTerminalBoxTypeEnum.USERDEFINED) or ((predefinedtype == IfcAirTerminalBoxTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcAirTerminalType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcAirTerminalType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcAirTerminalTypeEnum.USERDEFINED) or ((predefinedtype == IfcAirTerminalTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcAirToAirHeatRecovery_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcAirToAirHeatRecovery"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcAirToAirHeatRecoveryTypeEnum.USERDEFINED) or ((predefinedtype == IfcAirToAirHeatRecoveryTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcAirToAirHeatRecovery_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcAirToAirHeatRecovery"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcairtoairheatrecoverytype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcAirToAirHeatRecoveryType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcAirToAirHeatRecoveryType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcAirToAirHeatRecoveryTypeEnum.USERDEFINED) or ((predefinedtype == IfcAirToAirHeatRecoveryTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcAlarm_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcAlarm"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcAlarmTypeEnum.USERDEFINED) or ((predefinedtype == IfcAlarmTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcAlarm_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcAlarm"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcalarmtype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcAlarmType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcAlarmType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcAlarmTypeEnum.USERDEFINED) or ((predefinedtype == IfcAlarmTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        
















class IfcApproval_HasIdentifierOrName:
    SCOPE = "entity"
    TYPE_NAME = "IfcApproval"
    RULE_NAME = "HasIdentifierOrName"

    @staticmethod    
    def __call__(self):
        identifier = self.Identifier
        name = self.Name
        
        assert (exists(identifier) or exists(name)) is not False
        







class IfcArbitraryClosedProfileDef_WR1:
    SCOPE = "entity"
    TYPE_NAME = "IfcArbitraryClosedProfileDef"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):
        outercurve = self.OuterCurve
        
        assert (outercurve.Dim == 2) is not False
        



class IfcArbitraryClosedProfileDef_WR2:
    SCOPE = "entity"
    TYPE_NAME = "IfcArbitraryClosedProfileDef"
    RULE_NAME = "WR2"

    @staticmethod    
    def __call__(self):
        outercurve = self.OuterCurve
        
        assert (not 'ifc4.ifcline' in typeof(outercurve)) is not False
        



class IfcArbitraryClosedProfileDef_WR3:
    SCOPE = "entity"
    TYPE_NAME = "IfcArbitraryClosedProfileDef"
    RULE_NAME = "WR3"

    @staticmethod    
    def __call__(self):
        outercurve = self.OuterCurve
        
        assert (not 'ifc4.ifcoffsetcurve2d' in typeof(outercurve)) is not False
        




class IfcArbitraryOpenProfileDef_WR11:
    SCOPE = "entity"
    TYPE_NAME = "IfcArbitraryOpenProfileDef"
    RULE_NAME = "WR11"

    @staticmethod    
    def __call__(self):

        
        assert (('ifc4.ifccenterlineprofiledef' in typeof(self)) or (self.ProfileType == IfcProfileTypeEnum.CURVE)) is not False
        



class IfcArbitraryOpenProfileDef_WR12:
    SCOPE = "entity"
    TYPE_NAME = "IfcArbitraryOpenProfileDef"
    RULE_NAME = "WR12"

    @staticmethod    
    def __call__(self):
        curve = self.Curve
        
        assert (curve.Dim == 2) is not False
        




class IfcArbitraryProfileDefWithVoids_WR1:
    SCOPE = "entity"
    TYPE_NAME = "IfcArbitraryProfileDefWithVoids"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):

        
        assert (self.ProfileType == area) is not False
        



class IfcArbitraryProfileDefWithVoids_WR2:
    SCOPE = "entity"
    TYPE_NAME = "IfcArbitraryProfileDefWithVoids"
    RULE_NAME = "WR2"

    @staticmethod    
    def __call__(self):
        innercurves = self.InnerCurves
        
        assert ((sizeof([temp for temp in innercurves if temp.Dim != 2])) == 0) is not False
        



class IfcArbitraryProfileDefWithVoids_WR3:
    SCOPE = "entity"
    TYPE_NAME = "IfcArbitraryProfileDefWithVoids"
    RULE_NAME = "WR3"

    @staticmethod    
    def __call__(self):
        innercurves = self.InnerCurves
        
        assert ((sizeof([temp for temp in innercurves if 'ifc4.ifcline' in typeof(temp)])) == 0) is not False
        







class IfcAsymmetricIShapeProfileDef_ValidFlangeThickness:
    SCOPE = "entity"
    TYPE_NAME = "IfcAsymmetricIShapeProfileDef"
    RULE_NAME = "ValidFlangeThickness"

    @staticmethod    
    def __call__(self):
        overalldepth = self.OverallDepth
        bottomflangethickness = self.BottomFlangeThickness
        topflangethickness = self.TopFlangeThickness
        
        assert ((not exists(topflangethickness)) or ((bottomflangethickness + topflangethickness) < overalldepth)) is not False
        



class IfcAsymmetricIShapeProfileDef_ValidWebThickness:
    SCOPE = "entity"
    TYPE_NAME = "IfcAsymmetricIShapeProfileDef"
    RULE_NAME = "ValidWebThickness"

    @staticmethod    
    def __call__(self):
        bottomflangewidth = self.BottomFlangeWidth
        webthickness = self.WebThickness
        topflangewidth = self.TopFlangeWidth
        
        assert ((webthickness < bottomflangewidth) and (webthickness < topflangewidth)) is not False
        



class IfcAsymmetricIShapeProfileDef_ValidBottomFilletRadius:
    SCOPE = "entity"
    TYPE_NAME = "IfcAsymmetricIShapeProfileDef"
    RULE_NAME = "ValidBottomFilletRadius"

    @staticmethod    
    def __call__(self):
        bottomflangewidth = self.BottomFlangeWidth
        webthickness = self.WebThickness
        bottomflangefilletradius = self.BottomFlangeFilletRadius
        
        assert ((not exists(bottomflangefilletradius)) or (bottomflangefilletradius <= ((bottomflangewidth - webthickness) / 2.))) is not False
        



class IfcAsymmetricIShapeProfileDef_ValidTopFilletRadius:
    SCOPE = "entity"
    TYPE_NAME = "IfcAsymmetricIShapeProfileDef"
    RULE_NAME = "ValidTopFilletRadius"

    @staticmethod    
    def __call__(self):
        webthickness = self.WebThickness
        topflangewidth = self.TopFlangeWidth
        topflangefilletradius = self.TopFlangeFilletRadius
        
        assert ((not exists(topflangefilletradius)) or (topflangefilletradius <= ((topflangewidth - webthickness) / 2.))) is not False
        




class IfcAudioVisualAppliance_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcAudioVisualAppliance"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcAudioVisualApplianceTypeEnum.USERDEFINED) or ((predefinedtype == IfcAudioVisualApplianceTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcAudioVisualAppliance_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcAudioVisualAppliance"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcaudiovisualappliancetype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcAudioVisualApplianceType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcAudioVisualApplianceType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcAudioVisualApplianceTypeEnum.USERDEFINED) or ((predefinedtype == IfcAudioVisualApplianceTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcAxis1Placement_AxisIs3D:
    SCOPE = "entity"
    TYPE_NAME = "IfcAxis1Placement"
    RULE_NAME = "AxisIs3D"

    @staticmethod    
    def __call__(self):
        axis = self.Axis
        
        assert ((not exists(axis)) or (axis.Dim == 3)) is not False
        



class IfcAxis1Placement_LocationIs3D:
    SCOPE = "entity"
    TYPE_NAME = "IfcAxis1Placement"
    RULE_NAME = "LocationIs3D"

    @staticmethod    
    def __call__(self):

        
        assert (self.Location.Dim == 3) is not False
        



def calc_IfcAxis1Placement_Z(self):
    axis = self.Axis
    return \
    nvl(IfcNormalise(axis),IfcDirection(DirectionRatios=[0.0,0.0,1.0]))




class IfcAxis2Placement2D_RefDirIs2D:
    SCOPE = "entity"
    TYPE_NAME = "IfcAxis2Placement2D"
    RULE_NAME = "RefDirIs2D"

    @staticmethod    
    def __call__(self):
        refdirection = self.RefDirection
        
        assert ((not exists(refdirection)) or (refdirection.Dim == 2)) is not False
        



class IfcAxis2Placement2D_LocationIs2D:
    SCOPE = "entity"
    TYPE_NAME = "IfcAxis2Placement2D"
    RULE_NAME = "LocationIs2D"

    @staticmethod    
    def __call__(self):

        
        assert (self.Location.Dim == 2) is not False
        



def calc_IfcAxis2Placement2D_P(self):
    refdirection = self.RefDirection
    return \
    IfcBuild2Axes(refdirection)




class IfcAxis2Placement3D_LocationIs3D:
    SCOPE = "entity"
    TYPE_NAME = "IfcAxis2Placement3D"
    RULE_NAME = "LocationIs3D"

    @staticmethod    
    def __call__(self):

        
        assert (self.Location.Dim == 3) is not False
        



class IfcAxis2Placement3D_AxisIs3D:
    SCOPE = "entity"
    TYPE_NAME = "IfcAxis2Placement3D"
    RULE_NAME = "AxisIs3D"

    @staticmethod    
    def __call__(self):
        axis = self.Axis
        
        assert ((not exists(axis)) or (axis.Dim == 3)) is not False
        



class IfcAxis2Placement3D_RefDirIs3D:
    SCOPE = "entity"
    TYPE_NAME = "IfcAxis2Placement3D"
    RULE_NAME = "RefDirIs3D"

    @staticmethod    
    def __call__(self):
        refdirection = self.RefDirection
        
        assert ((not exists(refdirection)) or (refdirection.Dim == 3)) is not False
        



class IfcAxis2Placement3D_AxisToRefDirPosition:
    SCOPE = "entity"
    TYPE_NAME = "IfcAxis2Placement3D"
    RULE_NAME = "AxisToRefDirPosition"

    @staticmethod    
    def __call__(self):
        axis = self.Axis
        refdirection = self.RefDirection
        
        assert ((not exists(axis)) or (not exists(refdirection)) or (IfcCrossProduct(axis,refdirection).Magnitude > 0.0)) is not False
        



class IfcAxis2Placement3D_AxisAndRefDirProvision:
    SCOPE = "entity"
    TYPE_NAME = "IfcAxis2Placement3D"
    RULE_NAME = "AxisAndRefDirProvision"

    @staticmethod    
    def __call__(self):
        axis = self.Axis
        refdirection = self.RefDirection
        
        assert (not exists(axis) ^ exists(refdirection)) is not False
        



def calc_IfcAxis2Placement3D_P(self):
    axis = self.Axis
    refdirection = self.RefDirection
    return \
    IfcBuildAxes(axis,refdirection)




class IfcBSplineCurve_SameDim:
    SCOPE = "entity"
    TYPE_NAME = "IfcBSplineCurve"
    RULE_NAME = "SameDim"

    @staticmethod    
    def __call__(self):
        controlpointslist = self.ControlPointsList
        
        assert ((sizeof([temp for temp in controlpointslist if temp.Dim != (controlpointslist[1 - 1].Dim)])) == 0) is not False
        



def calc_IfcBSplineCurve_UpperIndexOnControlPoints(self):
    controlpointslist = self.ControlPointsList
    return \
    sizeof(controlpointslist) - 1



def calc_IfcBSplineCurve_ControlPoints(self):
    controlpointslist = self.ControlPointsList
    upperindexoncontrolpoints = self.UpperIndexOnControlPoints
    return \
    IfcListToArray(controlpointslist,0,upperindexoncontrolpoints)




class IfcBSplineCurveWithKnots_ConsistentBSpline:
    SCOPE = "entity"
    TYPE_NAME = "IfcBSplineCurveWithKnots"
    RULE_NAME = "ConsistentBSpline"

    @staticmethod    
    def __call__(self):
        degree = self.Degree
        upperindexoncontrolpoints = self.UpperIndexOnControlPoints
        knotmultiplicities = self.KnotMultiplicities
        knots = self.Knots
        upperindexonknots = self.UpperIndexOnKnots
        
        assert (IfcConstraintsParamBSpline(degree,upperindexonknots,upperindexoncontrolpoints,knotmultiplicities,knots)) is not False
        



class IfcBSplineCurveWithKnots_CorrespondingKnotLists:
    SCOPE = "entity"
    TYPE_NAME = "IfcBSplineCurveWithKnots"
    RULE_NAME = "CorrespondingKnotLists"

    @staticmethod    
    def __call__(self):
        knotmultiplicities = self.KnotMultiplicities
        upperindexonknots = self.UpperIndexOnKnots
        
        assert (sizeof(knotmultiplicities) == upperindexonknots) is not False
        



def calc_IfcBSplineCurveWithKnots_UpperIndexOnKnots(self):
    knots = self.Knots
    return \
    sizeof(knots)




def calc_IfcBSplineSurface_UUpper(self):
    controlpointslist = self.ControlPointsList
    return \
    sizeof(controlpointslist) - 1



def calc_IfcBSplineSurface_VUpper(self):
    controlpointslist = self.ControlPointsList
    return \
    (sizeof(controlpointslist[1 - 1])) - 1



def calc_IfcBSplineSurface_ControlPoints(self):
    controlpointslist = self.ControlPointsList
    uupper = self.UUpper
    vupper = self.VUpper
    return \
    IfcMakeArrayOfArray(controlpointslist,0,uupper,0,vupper)




class IfcBSplineSurfaceWithKnots_UDirectionConstraints:
    SCOPE = "entity"
    TYPE_NAME = "IfcBSplineSurfaceWithKnots"
    RULE_NAME = "UDirectionConstraints"

    @staticmethod    
    def __call__(self):
        umultiplicities = self.UMultiplicities
        uknots = self.UKnots
        knotuupper = self.KnotUUpper
        
        assert (IfcConstraintsParamBSpline(self.UDegree,knotuupper,self.UUpper,umultiplicities,uknots)) is not False
        



class IfcBSplineSurfaceWithKnots_VDirectionConstraints:
    SCOPE = "entity"
    TYPE_NAME = "IfcBSplineSurfaceWithKnots"
    RULE_NAME = "VDirectionConstraints"

    @staticmethod    
    def __call__(self):
        vmultiplicities = self.VMultiplicities
        vknots = self.VKnots
        knotvupper = self.KnotVUpper
        
        assert (IfcConstraintsParamBSpline(self.VDegree,knotvupper,self.VUpper,vmultiplicities,vknots)) is not False
        



class IfcBSplineSurfaceWithKnots_CorrespondingULists:
    SCOPE = "entity"
    TYPE_NAME = "IfcBSplineSurfaceWithKnots"
    RULE_NAME = "CorrespondingULists"

    @staticmethod    
    def __call__(self):
        umultiplicities = self.UMultiplicities
        knotuupper = self.KnotUUpper
        
        assert (sizeof(umultiplicities) == knotuupper) is not False
        



class IfcBSplineSurfaceWithKnots_CorrespondingVLists:
    SCOPE = "entity"
    TYPE_NAME = "IfcBSplineSurfaceWithKnots"
    RULE_NAME = "CorrespondingVLists"

    @staticmethod    
    def __call__(self):
        vmultiplicities = self.VMultiplicities
        knotvupper = self.KnotVUpper
        
        assert (sizeof(vmultiplicities) == knotvupper) is not False
        



def calc_IfcBSplineSurfaceWithKnots_KnotVUpper(self):
    vknots = self.VKnots
    return \
    sizeof(vknots)



def calc_IfcBSplineSurfaceWithKnots_KnotUUpper(self):
    uknots = self.UKnots
    return \
    sizeof(uknots)




class IfcBeam_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcBeam"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcBeamTypeEnum.USERDEFINED) or ((predefinedtype == IfcBeamTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcBeam_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcBeam"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcbeamtype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcBeamStandardCase_HasMaterialProfileSetUsage:
    SCOPE = "entity"
    TYPE_NAME = "IfcBeamStandardCase"
    RULE_NAME = "HasMaterialProfileSetUsage"

    @staticmethod    
    def __call__(self):

        
        assert ((sizeof([temp for temp in usedin(self,'ifc4.ifcrelassociates.relatedobjects') if ('ifc4.ifcrelassociatesmaterial' in typeof(temp)) and ('ifc4.ifcmaterialprofilesetusage' in typeof(temp.RelatingMaterial))])) == 1) is not False
        




class IfcBeamType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcBeamType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcBeamTypeEnum.USERDEFINED) or ((predefinedtype == IfcBeamTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcBlobTexture_SupportedRasterFormat:
    SCOPE = "entity"
    TYPE_NAME = "IfcBlobTexture"
    RULE_NAME = "SupportedRasterFormat"

    @staticmethod    
    def __call__(self):

        
        assert (self.RasterFormat in ['bmp','jpg','gif','png']) is not False
        



class IfcBlobTexture_RasterCodeByteStream:
    SCOPE = "entity"
    TYPE_NAME = "IfcBlobTexture"
    RULE_NAME = "RasterCodeByteStream"

    @staticmethod    
    def __call__(self):
        rastercode = self.RasterCode
        
        assert ((blength(rastercode) % 8) == 0) is not False
        







class IfcBoiler_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcBoiler"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcBoilerTypeEnum.USERDEFINED) or ((predefinedtype == IfcBoilerTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcBoiler_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcBoiler"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcboilertype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcBoilerType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcBoilerType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcBoilerTypeEnum.USERDEFINED) or ((predefinedtype == IfcBoilerTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcBooleanClippingResult_FirstOperandType:
    SCOPE = "entity"
    TYPE_NAME = "IfcBooleanClippingResult"
    RULE_NAME = "FirstOperandType"

    @staticmethod    
    def __call__(self):
        firstoperand = self.FirstOperand
        
        assert (('ifc4.ifcsweptareasolid' in typeof(firstoperand)) or ('ifc4.ifcsweptdiscsolid' in typeof(firstoperand)) or ('ifc4.ifcbooleanclippingresult' in typeof(firstoperand))) is not False
        



class IfcBooleanClippingResult_SecondOperandType:
    SCOPE = "entity"
    TYPE_NAME = "IfcBooleanClippingResult"
    RULE_NAME = "SecondOperandType"

    @staticmethod    
    def __call__(self):
        secondoperand = self.SecondOperand
        
        assert ('ifc4.ifchalfspacesolid' in typeof(secondoperand)) is not False
        



class IfcBooleanClippingResult_OperatorType:
    SCOPE = "entity"
    TYPE_NAME = "IfcBooleanClippingResult"
    RULE_NAME = "OperatorType"

    @staticmethod    
    def __call__(self):
        operator = self.Operator
        
        assert (operator == difference) is not False
        




class IfcBooleanResult_SameDim:
    SCOPE = "entity"
    TYPE_NAME = "IfcBooleanResult"
    RULE_NAME = "SameDim"

    @staticmethod    
    def __call__(self):
        firstoperand = self.FirstOperand
        secondoperand = self.SecondOperand
        
        assert (firstoperand.Dim == secondoperand.Dim) is not False
        



class IfcBooleanResult_FirstOperandClosed:
    SCOPE = "entity"
    TYPE_NAME = "IfcBooleanResult"
    RULE_NAME = "FirstOperandClosed"

    @staticmethod    
    def __call__(self):
        firstoperand = self.FirstOperand
        
        assert ((not 'ifc4.ifctessellatedfaceset' in typeof(firstoperand)) or (exists(firstoperand.Closed) and firstoperand.Closed)) is not False
        



class IfcBooleanResult_SecondOperandClosed:
    SCOPE = "entity"
    TYPE_NAME = "IfcBooleanResult"
    RULE_NAME = "SecondOperandClosed"

    @staticmethod    
    def __call__(self):
        secondoperand = self.SecondOperand
        
        assert ((not 'ifc4.ifctessellatedfaceset' in typeof(secondoperand)) or (exists(secondoperand.Closed) and secondoperand.Closed)) is not False
        



def calc_IfcBooleanResult_Dim(self):
    firstoperand = self.FirstOperand
    return \
    firstoperand.Dim







class IfcBoundaryCurve_IsClosed:
    SCOPE = "entity"
    TYPE_NAME = "IfcBoundaryCurve"
    RULE_NAME = "IsClosed"

    @staticmethod    
    def __call__(self):

        
        assert (self.ClosedCurve) is not False
        






















def calc_IfcBoundingBox_Dim(self):

    return \
    3




class IfcBoxedHalfSpace_UnboundedSurface:
    SCOPE = "entity"
    TYPE_NAME = "IfcBoxedHalfSpace"
    RULE_NAME = "UnboundedSurface"

    @staticmethod    
    def __call__(self):

        
        assert (not 'ifc4.ifccurveboundedplane' in typeof(self.BaseSurface)) is not False
        







class IfcBuildingElement_MaxOneMaterialAssociation:
    SCOPE = "entity"
    TYPE_NAME = "IfcBuildingElement"
    RULE_NAME = "MaxOneMaterialAssociation"

    @staticmethod    
    def __call__(self):

        
        assert ((sizeof([temp for temp in self.HasAssociations if 'ifc4.ifcrelassociatesmaterial' in typeof(temp)])) <= 1) is not False
        




class IfcBuildingElementPart_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcBuildingElementPart"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcBuildingElementPartTypeEnum.USERDEFINED) or ((predefinedtype == IfcBuildingElementPartTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcBuildingElementPart_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcBuildingElementPart"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcbuildingelementparttype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcBuildingElementPartType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcBuildingElementPartType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcBuildingElementPartTypeEnum.USERDEFINED) or ((predefinedtype == IfcBuildingElementPartTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcBuildingElementProxy_HasObjectName:
    SCOPE = "entity"
    TYPE_NAME = "IfcBuildingElementProxy"
    RULE_NAME = "HasObjectName"

    @staticmethod    
    def __call__(self):

        
        assert (exists(self.Name)) is not False
        



class IfcBuildingElementProxy_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcBuildingElementProxy"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcBuildingElementProxyTypeEnum.USERDEFINED) or ((predefinedtype == IfcBuildingElementProxyTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcBuildingElementProxy_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcBuildingElementProxy"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcbuildingelementproxytype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcBuildingElementProxyType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcBuildingElementProxyType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcBuildingElementProxyTypeEnum.USERDEFINED) or ((predefinedtype == IfcBuildingElementProxyTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        













class IfcBurner_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcBurner"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcBurnerTypeEnum.USERDEFINED) or ((predefinedtype == IfcBurnerTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcBurner_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcBurner"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcburnertype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcBurnerType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcBurnerType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcBurnerTypeEnum.USERDEFINED) or ((predefinedtype == IfcBurnerTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcCShapeProfileDef_ValidGirth:
    SCOPE = "entity"
    TYPE_NAME = "IfcCShapeProfileDef"
    RULE_NAME = "ValidGirth"

    @staticmethod    
    def __call__(self):
        depth = self.Depth
        girth = self.Girth
        
        assert (girth < (depth / 2.)) is not False
        



class IfcCShapeProfileDef_ValidInternalFilletRadius:
    SCOPE = "entity"
    TYPE_NAME = "IfcCShapeProfileDef"
    RULE_NAME = "ValidInternalFilletRadius"

    @staticmethod    
    def __call__(self):
        depth = self.Depth
        width = self.Width
        wallthickness = self.WallThickness
        internalfilletradius = self.InternalFilletRadius
        
        assert ((not exists(internalfilletradius)) or ((internalfilletradius <= ((width / 2.) - wallthickness)) and (internalfilletradius <= ((depth / 2.) - wallthickness)))) is not False
        



class IfcCShapeProfileDef_ValidWallThickness:
    SCOPE = "entity"
    TYPE_NAME = "IfcCShapeProfileDef"
    RULE_NAME = "ValidWallThickness"

    @staticmethod    
    def __call__(self):
        depth = self.Depth
        width = self.Width
        wallthickness = self.WallThickness
        
        assert ((wallthickness < (width / 2.)) and (wallthickness < (depth / 2.))) is not False
        




class IfcCableCarrierFitting_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcCableCarrierFitting"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcCableCarrierFittingTypeEnum.USERDEFINED) or ((predefinedtype == IfcCableCarrierFittingTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcCableCarrierFitting_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcCableCarrierFitting"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifccablecarrierfittingtype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcCableCarrierFittingType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcCableCarrierFittingType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcCableCarrierFittingTypeEnum.USERDEFINED) or ((predefinedtype == IfcCableCarrierFittingTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcCableCarrierSegment_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcCableCarrierSegment"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcCableCarrierSegmentTypeEnum.USERDEFINED) or ((predefinedtype == IfcCableCarrierSegmentTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcCableCarrierSegment_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcCableCarrierSegment"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifccablecarriersegmenttype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcCableCarrierSegmentType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcCableCarrierSegmentType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcCableCarrierSegmentTypeEnum.USERDEFINED) or ((predefinedtype == IfcCableCarrierSegmentTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcCableFitting_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcCableFitting"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcCableFittingTypeEnum.USERDEFINED) or ((predefinedtype == IfcCableFittingTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcCableFitting_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcCableFitting"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifccablefittingtype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcCableFittingType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcCableFittingType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcCableFittingTypeEnum.USERDEFINED) or ((predefinedtype == IfcCableFittingTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcCableSegment_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcCableSegment"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcCableSegmentTypeEnum.USERDEFINED) or ((predefinedtype == IfcCableSegmentTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcCableSegment_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcCableSegment"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifccablesegmenttype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcCableSegmentType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcCableSegmentType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcCableSegmentTypeEnum.USERDEFINED) or ((predefinedtype == IfcCableSegmentTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcCartesianPoint_CP2Dor3D:
    SCOPE = "entity"
    TYPE_NAME = "IfcCartesianPoint"
    RULE_NAME = "CP2Dor3D"

    @staticmethod    
    def __call__(self):
        coordinates = self.Coordinates
        
        assert (hiindex(coordinates) >= 2) is not False
        



def calc_IfcCartesianPoint_Dim(self):
    coordinates = self.Coordinates
    return \
    hiindex(coordinates)




def calc_IfcCartesianPointList_Dim(self):

    return \
    IfcPointListDim(self)










class IfcCartesianTransformationOperator_ScaleGreaterZero:
    SCOPE = "entity"
    TYPE_NAME = "IfcCartesianTransformationOperator"
    RULE_NAME = "ScaleGreaterZero"

    @staticmethod    
    def __call__(self):
        scl = self.Scl
        
        assert (scl > 0.0) is not False
        



def calc_IfcCartesianTransformationOperator_Scl(self):
    scale = self.Scale
    return \
    nvl(scale,1.0)



def calc_IfcCartesianTransformationOperator_Dim(self):
    localorigin = self.LocalOrigin
    return \
    localorigin.Dim




class IfcCartesianTransformationOperator2D_DimEqual2:
    SCOPE = "entity"
    TYPE_NAME = "IfcCartesianTransformationOperator2D"
    RULE_NAME = "DimEqual2"

    @staticmethod    
    def __call__(self):

        
        assert (self.Dim == 2) is not False
        



class IfcCartesianTransformationOperator2D_Axis1Is2D:
    SCOPE = "entity"
    TYPE_NAME = "IfcCartesianTransformationOperator2D"
    RULE_NAME = "Axis1Is2D"

    @staticmethod    
    def __call__(self):

        
        assert ((not exists(self.Axis1)) or (self.Axis1.Dim == 2)) is not False
        



class IfcCartesianTransformationOperator2D_Axis2Is2D:
    SCOPE = "entity"
    TYPE_NAME = "IfcCartesianTransformationOperator2D"
    RULE_NAME = "Axis2Is2D"

    @staticmethod    
    def __call__(self):

        
        assert ((not exists(self.Axis2)) or (self.Axis2.Dim == 2)) is not False
        



def calc_IfcCartesianTransformationOperator2D_U(self):

    return \
    IfcBaseAxis(2,self.Axis1,self.Axis2,None)




class IfcCartesianTransformationOperator2DnonUniform_Scale2GreaterZero:
    SCOPE = "entity"
    TYPE_NAME = "IfcCartesianTransformationOperator2DnonUniform"
    RULE_NAME = "Scale2GreaterZero"

    @staticmethod    
    def __call__(self):
        scl2 = self.Scl2
        
        assert (scl2 > 0.0) is not False
        



def calc_IfcCartesianTransformationOperator2DnonUniform_Scl2(self):
    scale2 = self.Scale2
    return \
    nvl(scale2,self.Scl)




class IfcCartesianTransformationOperator3D_DimIs3D:
    SCOPE = "entity"
    TYPE_NAME = "IfcCartesianTransformationOperator3D"
    RULE_NAME = "DimIs3D"

    @staticmethod    
    def __call__(self):

        
        assert (self.Dim == 3) is not False
        



class IfcCartesianTransformationOperator3D_Axis1Is3D:
    SCOPE = "entity"
    TYPE_NAME = "IfcCartesianTransformationOperator3D"
    RULE_NAME = "Axis1Is3D"

    @staticmethod    
    def __call__(self):

        
        assert ((not exists(self.Axis1)) or (self.Axis1.Dim == 3)) is not False
        



class IfcCartesianTransformationOperator3D_Axis2Is3D:
    SCOPE = "entity"
    TYPE_NAME = "IfcCartesianTransformationOperator3D"
    RULE_NAME = "Axis2Is3D"

    @staticmethod    
    def __call__(self):

        
        assert ((not exists(self.Axis2)) or (self.Axis2.Dim == 3)) is not False
        



class IfcCartesianTransformationOperator3D_Axis3Is3D:
    SCOPE = "entity"
    TYPE_NAME = "IfcCartesianTransformationOperator3D"
    RULE_NAME = "Axis3Is3D"

    @staticmethod    
    def __call__(self):
        axis3 = self.Axis3
        
        assert ((not exists(axis3)) or (axis3.Dim == 3)) is not False
        



def calc_IfcCartesianTransformationOperator3D_U(self):
    axis3 = self.Axis3
    return \
    IfcBaseAxis(3,self.Axis1,self.Axis2,axis3)




class IfcCartesianTransformationOperator3DnonUniform_Scale2GreaterZero:
    SCOPE = "entity"
    TYPE_NAME = "IfcCartesianTransformationOperator3DnonUniform"
    RULE_NAME = "Scale2GreaterZero"

    @staticmethod    
    def __call__(self):
        scl2 = self.Scl2
        
        assert (scl2 > 0.0) is not False
        



class IfcCartesianTransformationOperator3DnonUniform_Scale3GreaterZero:
    SCOPE = "entity"
    TYPE_NAME = "IfcCartesianTransformationOperator3DnonUniform"
    RULE_NAME = "Scale3GreaterZero"

    @staticmethod    
    def __call__(self):
        scl3 = self.Scl3
        
        assert (scl3 > 0.0) is not False
        



def calc_IfcCartesianTransformationOperator3DnonUniform_Scl2(self):
    scale2 = self.Scale2
    return \
    nvl(scale2,self.Scl)



def calc_IfcCartesianTransformationOperator3DnonUniform_Scl3(self):
    scale3 = self.Scale3
    return \
    nvl(scale3,self.Scl)







class IfcChiller_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcChiller"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcChillerTypeEnum.USERDEFINED) or ((predefinedtype == IfcChillerTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcChiller_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcChiller"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcchillertype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcChillerType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcChillerType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcChillerTypeEnum.USERDEFINED) or ((predefinedtype == IfcChillerTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcChimney_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcChimney"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcChimneyTypeEnum.USERDEFINED) or ((predefinedtype == IfcChimneyTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcChimney_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcChimney"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcchimneytype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcChimneyType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcChimneyType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcChimneyTypeEnum.USERDEFINED) or ((predefinedtype == IfcChimneyTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        







class IfcCircleHollowProfileDef_WR1:
    SCOPE = "entity"
    TYPE_NAME = "IfcCircleHollowProfileDef"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):
        wallthickness = self.WallThickness
        
        assert (wallthickness < self.Radius) is not False
        






















class IfcCoil_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcCoil"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcCoilTypeEnum.USERDEFINED) or ((predefinedtype == IfcCoilTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcCoil_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcCoil"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifccoiltype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcCoilType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcCoilType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcCoilTypeEnum.USERDEFINED) or ((predefinedtype == IfcCoilTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        













class IfcColumn_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcColumn"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcColumnTypeEnum.USERDEFINED) or ((predefinedtype == IfcColumnTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcColumn_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcColumn"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifccolumntype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcColumnStandardCase_HasMaterialProfileSetUsage:
    SCOPE = "entity"
    TYPE_NAME = "IfcColumnStandardCase"
    RULE_NAME = "HasMaterialProfileSetUsage"

    @staticmethod    
    def __call__(self):

        
        assert ((sizeof([temp for temp in usedin(self,'ifc4.ifcrelassociates.relatedobjects') if ('ifc4.ifcrelassociatesmaterial' in typeof(temp)) and ('ifc4.ifcmaterialprofilesetusage' in typeof(temp.RelatingMaterial))])) == 1) is not False
        




class IfcColumnType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcColumnType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcColumnTypeEnum.USERDEFINED) or ((predefinedtype == IfcColumnTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcCommunicationsAppliance_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcCommunicationsAppliance"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcCommunicationsApplianceTypeEnum.USERDEFINED) or ((predefinedtype == IfcCommunicationsApplianceTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcCommunicationsAppliance_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcCommunicationsAppliance"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifccommunicationsappliancetype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcCommunicationsApplianceType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcCommunicationsApplianceType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcCommunicationsApplianceTypeEnum.USERDEFINED) or ((predefinedtype == IfcCommunicationsApplianceTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcComplexProperty_WR21:
    SCOPE = "entity"
    TYPE_NAME = "IfcComplexProperty"
    RULE_NAME = "WR21"

    @staticmethod    
    def __call__(self):
        hasproperties = self.HasProperties
        
        assert ((sizeof([temp for temp in hasproperties if self == temp])) == 0) is not False
        



class IfcComplexProperty_WR22:
    SCOPE = "entity"
    TYPE_NAME = "IfcComplexProperty"
    RULE_NAME = "WR22"

    @staticmethod    
    def __call__(self):
        hasproperties = self.HasProperties
        
        assert (IfcUniquePropertyName(hasproperties)) is not False
        




class IfcComplexPropertyTemplate_UniquePropertyNames:
    SCOPE = "entity"
    TYPE_NAME = "IfcComplexPropertyTemplate"
    RULE_NAME = "UniquePropertyNames"

    @staticmethod    
    def __call__(self):
        haspropertytemplates = self.HasPropertyTemplates
        
        assert (IfcUniquePropertyTemplateNames(haspropertytemplates)) is not False
        



class IfcComplexPropertyTemplate_NoSelfReference:
    SCOPE = "entity"
    TYPE_NAME = "IfcComplexPropertyTemplate"
    RULE_NAME = "NoSelfReference"

    @staticmethod    
    def __call__(self):
        haspropertytemplates = self.HasPropertyTemplates
        
        assert ((sizeof([temp for temp in haspropertytemplates if self == temp])) == 0) is not False
        




class IfcCompositeCurve_CurveContinuous:
    SCOPE = "entity"
    TYPE_NAME = "IfcCompositeCurve"
    RULE_NAME = "CurveContinuous"

    @staticmethod    
    def __call__(self):
        segments = self.Segments
        closedcurve = self.ClosedCurve
        
        assert (((not closedcurve) and ((sizeof([temp for temp in segments if temp.Transition == discontinuous])) == 1)) or (closedcurve and ((sizeof([temp for temp in segments if temp.Transition == discontinuous])) == 0))) is not False
        



class IfcCompositeCurve_SameDim:
    SCOPE = "entity"
    TYPE_NAME = "IfcCompositeCurve"
    RULE_NAME = "SameDim"

    @staticmethod    
    def __call__(self):
        segments = self.Segments
        
        assert ((sizeof([temp for temp in segments if temp.Dim != (segments[1 - 1].Dim)])) == 0) is not False
        



def calc_IfcCompositeCurve_NSegments(self):
    segments = self.Segments
    return \
    sizeof(segments)



def calc_IfcCompositeCurve_ClosedCurve(self):
    segments = self.Segments
    nsegments = self.NSegments
    return \
    (segments[nsegments - 1].Transition) != discontinuous




class IfcCompositeCurveOnSurface_SameSurface:
    SCOPE = "entity"
    TYPE_NAME = "IfcCompositeCurveOnSurface"
    RULE_NAME = "SameSurface"

    @staticmethod    
    def __call__(self):
        basissurface = self.BasisSurface
        
        assert (sizeof(basissurface) > 0) is not False
        



def calc_IfcCompositeCurveOnSurface_BasisSurface(self):

    return \
    IfcGetBasisSurface(self)




class IfcCompositeCurveSegment_ParentIsBoundedCurve:
    SCOPE = "entity"
    TYPE_NAME = "IfcCompositeCurveSegment"
    RULE_NAME = "ParentIsBoundedCurve"

    @staticmethod    
    def __call__(self):
        parentcurve = self.ParentCurve
        
        assert ('ifc4.ifcboundedcurve' in typeof(parentcurve)) is not False
        



def calc_IfcCompositeCurveSegment_Dim(self):
    parentcurve = self.ParentCurve
    return \
    parentcurve.Dim




class IfcCompositeProfileDef_InvariantProfileType:
    SCOPE = "entity"
    TYPE_NAME = "IfcCompositeProfileDef"
    RULE_NAME = "InvariantProfileType"

    @staticmethod    
    def __call__(self):
        profiles = self.Profiles
        
        assert ((sizeof([temp for temp in profiles if temp.ProfileType != (profiles[1 - 1].ProfileType)])) == 0) is not False
        



class IfcCompositeProfileDef_NoRecursion:
    SCOPE = "entity"
    TYPE_NAME = "IfcCompositeProfileDef"
    RULE_NAME = "NoRecursion"

    @staticmethod    
    def __call__(self):
        profiles = self.Profiles
        
        assert ((sizeof([temp for temp in profiles if 'ifc4.ifccompositeprofiledef' in typeof(temp)])) == 0) is not False
        




class IfcCompressor_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcCompressor"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcCompressorTypeEnum.USERDEFINED) or ((predefinedtype == IfcCompressorTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcCompressor_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcCompressor"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifccompressortype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcCompressorType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcCompressorType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcCompressorTypeEnum.USERDEFINED) or ((predefinedtype == IfcCompressorTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcCondenser_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcCondenser"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcCondenserTypeEnum.USERDEFINED) or ((predefinedtype == IfcCondenserTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcCondenser_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcCondenser"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifccondensertype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcCondenserType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcCondenserType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcCondenserTypeEnum.USERDEFINED) or ((predefinedtype == IfcCondenserTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




























class IfcConstraint_WR11:
    SCOPE = "entity"
    TYPE_NAME = "IfcConstraint"
    RULE_NAME = "WR11"

    @staticmethod    
    def __call__(self):
        constraintgrade = self.ConstraintGrade
        
        assert ((constraintgrade != IfcConstraintEnum.USERDEFINED) or ((constraintgrade == IfcConstraintEnum.USERDEFINED) and exists(self.UserDefinedGrade))) is not False
        




class IfcConstructionEquipmentResource_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcConstructionEquipmentResource"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcConstructionEquipmentResourceTypeEnum.USERDEFINED) or ((predefinedtype == IfcConstructionEquipmentResourceTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        




class IfcConstructionEquipmentResourceType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcConstructionEquipmentResourceType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcConstructionEquipmentResourceTypeEnum.USERDEFINED) or ((predefinedtype == IfcConstructionEquipmentResourceTypeEnum.USERDEFINED) and exists(self.ResourceType))) is not False
        




class IfcConstructionMaterialResource_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcConstructionMaterialResource"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcConstructionMaterialResourceTypeEnum.USERDEFINED) or ((predefinedtype == IfcConstructionMaterialResourceTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        




class IfcConstructionMaterialResourceType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcConstructionMaterialResourceType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcConstructionMaterialResourceTypeEnum.USERDEFINED) or ((predefinedtype == IfcConstructionMaterialResourceTypeEnum.USERDEFINED) and exists(self.ResourceType))) is not False
        




class IfcConstructionProductResource_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcConstructionProductResource"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcConstructionProductResourceTypeEnum.USERDEFINED) or ((predefinedtype == IfcConstructionProductResourceTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        




class IfcConstructionProductResourceType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcConstructionProductResourceType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcConstructionProductResourceTypeEnum.USERDEFINED) or ((predefinedtype == IfcConstructionProductResourceTypeEnum.USERDEFINED) and exists(self.ResourceType))) is not False
        



















class IfcController_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcController"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcControllerTypeEnum.USERDEFINED) or ((predefinedtype == IfcControllerTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcController_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcController"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifccontrollertype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcControllerType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcControllerType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcControllerTypeEnum.USERDEFINED) or ((predefinedtype == IfcControllerTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        










class IfcCooledBeam_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcCooledBeam"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcCooledBeamTypeEnum.USERDEFINED) or ((predefinedtype == IfcCooledBeamTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcCooledBeam_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcCooledBeam"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifccooledbeamtype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcCooledBeamType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcCooledBeamType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcCooledBeamTypeEnum.USERDEFINED) or ((predefinedtype == IfcCooledBeamTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcCoolingTower_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcCoolingTower"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcCoolingTowerTypeEnum.USERDEFINED) or ((predefinedtype == IfcCoolingTowerTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcCoolingTower_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcCoolingTower"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifccoolingtowertype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcCoolingTowerType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcCoolingTowerType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcCoolingTowerTypeEnum.USERDEFINED) or ((predefinedtype == IfcCoolingTowerTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        



















class IfcCovering_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcCovering"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcCoveringTypeEnum.USERDEFINED) or ((predefinedtype == IfcCoveringTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcCovering_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcCovering"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifccoveringtype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcCoveringType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcCoveringType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcCoveringTypeEnum.USERDEFINED) or ((predefinedtype == IfcCoveringTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcCrewResource_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcCrewResource"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcCrewResourceTypeEnum.USERDEFINED) or ((predefinedtype == IfcCrewResourceTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        




class IfcCrewResourceType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcCrewResourceType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcCrewResourceTypeEnum.USERDEFINED) or ((predefinedtype == IfcCrewResourceTypeEnum.USERDEFINED) and exists(self.ResourceType))) is not False
        




def calc_IfcCsgPrimitive3D_Dim(self):

    return \
    3










class IfcCurtainWall_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcCurtainWall"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcCurtainWallTypeEnum.USERDEFINED) or ((predefinedtype == IfcCurtainWallTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcCurtainWall_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcCurtainWall"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifccurtainwalltype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcCurtainWallType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcCurtainWallType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcCurtainWallTypeEnum.USERDEFINED) or ((predefinedtype == IfcCurtainWallTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




def calc_IfcCurve_Dim(self):

    return \
    IfcCurveDim(self)










class IfcCurveStyle_MeasureOfWidth:
    SCOPE = "entity"
    TYPE_NAME = "IfcCurveStyle"
    RULE_NAME = "MeasureOfWidth"

    @staticmethod    
    def __call__(self):
        curvewidth = self.CurveWidth
        
        assert ((not exists(curvewidth)) or ('ifc4.ifcpositivelengthmeasure' in typeof(curvewidth)) or (('ifc4.ifcdescriptivemeasure' in typeof(curvewidth)) and (curvewidth == 'bylayer'))) is not False
        



class IfcCurveStyle_IdentifiableCurveStyle:
    SCOPE = "entity"
    TYPE_NAME = "IfcCurveStyle"
    RULE_NAME = "IdentifiableCurveStyle"

    @staticmethod    
    def __call__(self):
        curvefont = self.CurveFont
        curvewidth = self.CurveWidth
        curvecolour = self.CurveColour
        
        assert (exists(curvefont) or exists(curvewidth) or exists(curvecolour)) is not False
        










class IfcCurveStyleFontPattern_VisibleLengthGreaterEqualZero:
    SCOPE = "entity"
    TYPE_NAME = "IfcCurveStyleFontPattern"
    RULE_NAME = "VisibleLengthGreaterEqualZero"

    @staticmethod    
    def __call__(self):
        visiblesegmentlength = self.VisibleSegmentLength
        
        assert (visiblesegmentlength >= 0.) is not False
        







class IfcDamper_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcDamper"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcDamperTypeEnum.USERDEFINED) or ((predefinedtype == IfcDamperTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcDamper_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcDamper"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcdampertype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcDamperType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcDamperType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcDamperTypeEnum.USERDEFINED) or ((predefinedtype == IfcDamperTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcDerivedProfileDef_InvariantProfileType:
    SCOPE = "entity"
    TYPE_NAME = "IfcDerivedProfileDef"
    RULE_NAME = "InvariantProfileType"

    @staticmethod    
    def __call__(self):
        parentprofile = self.ParentProfile
        
        assert (self.ProfileType == parentprofile.ProfileType) is not False
        




class IfcDerivedUnit_WR1:
    SCOPE = "entity"
    TYPE_NAME = "IfcDerivedUnit"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):
        elements = self.Elements
        
        assert ((sizeof(elements) > 1) or ((sizeof(elements) == 1) and ((elements[1 - 1].Exponent) != 1))) is not False
        



class IfcDerivedUnit_WR2:
    SCOPE = "entity"
    TYPE_NAME = "IfcDerivedUnit"
    RULE_NAME = "WR2"

    @staticmethod    
    def __call__(self):
        unittype = self.UnitType
        
        assert ((unittype != IfcDerivedUnitEnum.USERDEFINED) or ((unittype == IfcDerivedUnitEnum.USERDEFINED) and exists(self.UserDefinedType))) is not False
        



def calc_IfcDerivedUnit_Dimensions(self):
    elements = self.Elements
    return \
    IfcDeriveDimensionalExponents(elements)










class IfcDirection_MagnitudeGreaterZero:
    SCOPE = "entity"
    TYPE_NAME = "IfcDirection"
    RULE_NAME = "MagnitudeGreaterZero"

    @staticmethod    
    def __call__(self):
        directionratios = self.DirectionRatios
        
        assert ((sizeof([tmp for tmp in directionratios if tmp != 0.0])) > 0) is not False
        



def calc_IfcDirection_Dim(self):
    directionratios = self.DirectionRatios
    return \
    hiindex(directionratios)




class IfcDiscreteAccessory_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcDiscreteAccessory"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcDiscreteAccessoryTypeEnum.USERDEFINED) or ((predefinedtype == IfcDiscreteAccessoryTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcDiscreteAccessory_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcDiscreteAccessory"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcdiscreteaccessorytype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcDiscreteAccessoryType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcDiscreteAccessoryType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcDiscreteAccessoryTypeEnum.USERDEFINED) or ((predefinedtype == IfcDiscreteAccessoryTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcDistributionChamberElement_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcDistributionChamberElement"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcDistributionChamberElementTypeEnum.USERDEFINED) or ((predefinedtype == IfcDistributionChamberElementTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcDistributionChamberElement_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcDistributionChamberElement"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcdistributionchamberelementtype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcDistributionChamberElementType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcDistributionChamberElementType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcDistributionChamberElementTypeEnum.USERDEFINED) or ((predefinedtype == IfcDistributionChamberElementTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        





































class IfcDocumentReference_WR1:
    SCOPE = "entity"
    TYPE_NAME = "IfcDocumentReference"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):
        name = self.Name
        referenceddocument = self.ReferencedDocument
        
        assert (exists(name) ^ exists(referenceddocument)) is not False
        




class IfcDoor_CorrectStyleAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcDoor"
    RULE_NAME = "CorrectStyleAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcdoortype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcDoorLiningProperties_WR31:
    SCOPE = "entity"
    TYPE_NAME = "IfcDoorLiningProperties"
    RULE_NAME = "WR31"

    @staticmethod    
    def __call__(self):
        liningdepth = self.LiningDepth
        liningthickness = self.LiningThickness
        
        assert (not exists(liningdepth) and (not exists(liningthickness))) is not False
        



class IfcDoorLiningProperties_WR32:
    SCOPE = "entity"
    TYPE_NAME = "IfcDoorLiningProperties"
    RULE_NAME = "WR32"

    @staticmethod    
    def __call__(self):
        thresholddepth = self.ThresholdDepth
        thresholdthickness = self.ThresholdThickness
        
        assert (not exists(thresholddepth) and (not exists(thresholdthickness))) is not False
        



class IfcDoorLiningProperties_WR33:
    SCOPE = "entity"
    TYPE_NAME = "IfcDoorLiningProperties"
    RULE_NAME = "WR33"

    @staticmethod    
    def __call__(self):
        transomthickness = self.TransomThickness
        transomoffset = self.TransomOffset
        
        assert ((exists(transomoffset) and exists(transomthickness)) ^ ((not exists(transomoffset)) and (not exists(transomthickness)))) is not False
        



class IfcDoorLiningProperties_WR34:
    SCOPE = "entity"
    TYPE_NAME = "IfcDoorLiningProperties"
    RULE_NAME = "WR34"

    @staticmethod    
    def __call__(self):
        casingthickness = self.CasingThickness
        casingdepth = self.CasingDepth
        
        assert ((exists(casingdepth) and exists(casingthickness)) ^ ((not exists(casingdepth)) and (not exists(casingthickness)))) is not False
        



class IfcDoorLiningProperties_WR35:
    SCOPE = "entity"
    TYPE_NAME = "IfcDoorLiningProperties"
    RULE_NAME = "WR35"

    @staticmethod    
    def __call__(self):

        
        assert ((exists(lambda: self.DefinesType[1 - 1])) and (('ifc4.ifcdoortype' in (typeof(self.DefinesType[1 - 1]))) or ('ifc4.ifcdoorstyle' in (typeof(self.DefinesType[1 - 1]))))) is not False
        




class IfcDoorPanelProperties_ApplicableToType:
    SCOPE = "entity"
    TYPE_NAME = "IfcDoorPanelProperties"
    RULE_NAME = "ApplicableToType"

    @staticmethod    
    def __call__(self):

        
        assert ((exists(lambda: self.DefinesType[1 - 1])) and (('ifc4.ifcdoortype' in (typeof(self.DefinesType[1 - 1]))) or ('ifc4.ifcdoorstyle' in (typeof(self.DefinesType[1 - 1]))))) is not False
        










class IfcDoorType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcDoorType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcDoorTypeEnum.USERDEFINED) or ((predefinedtype == IfcDoorTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcDraughtingPreDefinedColour_PreDefinedColourNames:
    SCOPE = "entity"
    TYPE_NAME = "IfcDraughtingPreDefinedColour"
    RULE_NAME = "PreDefinedColourNames"

    @staticmethod    
    def __call__(self):

        
        assert (self.Name in ['black','red','green','blue','yellow','magenta','cyan','white','bylayer']) is not False
        




class IfcDraughtingPreDefinedCurveFont_PreDefinedCurveFontNames:
    SCOPE = "entity"
    TYPE_NAME = "IfcDraughtingPreDefinedCurveFont"
    RULE_NAME = "PreDefinedCurveFontNames"

    @staticmethod    
    def __call__(self):

        
        assert (self.Name in ['continuous','chain','chaindoubledash','dashed','dotted','bylayer']) is not False
        




class IfcDuctFitting_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcDuctFitting"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcDuctFittingTypeEnum.USERDEFINED) or ((predefinedtype == IfcDuctFittingTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcDuctFitting_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcDuctFitting"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcductfittingtype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcDuctFittingType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcDuctFittingType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcDuctFittingTypeEnum.USERDEFINED) or ((predefinedtype == IfcDuctFittingTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcDuctSegment_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcDuctSegment"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcDuctSegmentTypeEnum.USERDEFINED) or ((predefinedtype == IfcDuctSegmentTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcDuctSegment_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcDuctSegment"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcductsegmenttype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcDuctSegmentType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcDuctSegmentType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcDuctSegmentTypeEnum.USERDEFINED) or ((predefinedtype == IfcDuctSegmentTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcDuctSilencer_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcDuctSilencer"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcDuctSilencerTypeEnum.USERDEFINED) or ((predefinedtype == IfcDuctSilencerTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcDuctSilencer_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcDuctSilencer"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcductsilencertype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcDuctSilencerType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcDuctSilencerType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcDuctSilencerTypeEnum.USERDEFINED) or ((predefinedtype == IfcDuctSilencerTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        










class IfcEdgeLoop_IsClosed:
    SCOPE = "entity"
    TYPE_NAME = "IfcEdgeLoop"
    RULE_NAME = "IsClosed"

    @staticmethod    
    def __call__(self):
        edgelist = self.EdgeList
        ne = self.Ne
        
        assert ((edgelist[1 - 1].EdgeStart) == (edgelist[ne - 1].EdgeEnd)) is not False
        



class IfcEdgeLoop_IsContinuous:
    SCOPE = "entity"
    TYPE_NAME = "IfcEdgeLoop"
    RULE_NAME = "IsContinuous"

    @staticmethod    
    def __call__(self):

        
        assert (IfcLoopHeadToTail(self)) is not False
        



def calc_IfcEdgeLoop_Ne(self):
    edgelist = self.EdgeList
    return \
    sizeof(edgelist)




class IfcElectricAppliance_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcElectricAppliance"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcElectricApplianceTypeEnum.USERDEFINED) or ((predefinedtype == IfcElectricApplianceTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcElectricAppliance_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcElectricAppliance"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcelectricappliancetype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcElectricApplianceType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcElectricApplianceType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcElectricApplianceTypeEnum.USERDEFINED) or ((predefinedtype == IfcElectricApplianceTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcElectricDistributionBoard_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcElectricDistributionBoard"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcElectricDistributionBoardTypeEnum.USERDEFINED) or ((predefinedtype == IfcElectricDistributionBoardTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcElectricDistributionBoard_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcElectricDistributionBoard"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcelectricdistributionboardtype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcElectricDistributionBoardType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcElectricDistributionBoardType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcElectricDistributionBoardTypeEnum.USERDEFINED) or ((predefinedtype == IfcElectricDistributionBoardTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcElectricFlowStorageDevice_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcElectricFlowStorageDevice"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcElectricFlowStorageDeviceTypeEnum.USERDEFINED) or ((predefinedtype == IfcElectricFlowStorageDeviceTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcElectricFlowStorageDevice_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcElectricFlowStorageDevice"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcelectricflowstoragedevicetype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcElectricFlowStorageDeviceType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcElectricFlowStorageDeviceType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcElectricFlowStorageDeviceTypeEnum.USERDEFINED) or ((predefinedtype == IfcElectricFlowStorageDeviceTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcElectricGenerator_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcElectricGenerator"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcElectricGeneratorTypeEnum.USERDEFINED) or ((predefinedtype == IfcElectricGeneratorTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcElectricGenerator_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcElectricGenerator"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcelectricgeneratortype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcElectricGeneratorType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcElectricGeneratorType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcElectricGeneratorTypeEnum.USERDEFINED) or ((predefinedtype == IfcElectricGeneratorTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcElectricMotor_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcElectricMotor"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcElectricMotorTypeEnum.USERDEFINED) or ((predefinedtype == IfcElectricMotorTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcElectricMotor_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcElectricMotor"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcelectricmotortype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcElectricMotorType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcElectricMotorType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcElectricMotorTypeEnum.USERDEFINED) or ((predefinedtype == IfcElectricMotorTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcElectricTimeControl_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcElectricTimeControl"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcElectricTimeControlTypeEnum.USERDEFINED) or ((predefinedtype == IfcElectricTimeControlTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcElectricTimeControl_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcElectricTimeControl"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcelectrictimecontroltype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcElectricTimeControlType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcElectricTimeControlType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcElectricTimeControlTypeEnum.USERDEFINED) or ((predefinedtype == IfcElectricTimeControlTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        







class IfcElementAssembly_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcElementAssembly"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcElementAssemblyTypeEnum.USERDEFINED) or ((predefinedtype == IfcElementAssemblyTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcElementAssembly_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcElementAssembly"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcelementassemblytype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcElementAssemblyType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcElementAssemblyType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcElementAssemblyTypeEnum.USERDEFINED) or ((predefinedtype == IfcElementAssemblyTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        










class IfcElementQuantity_UniqueQuantityNames:
    SCOPE = "entity"
    TYPE_NAME = "IfcElementQuantity"
    RULE_NAME = "UniqueQuantityNames"

    @staticmethod    
    def __call__(self):
        quantities = self.Quantities
        
        assert (IfcUniqueQuantityNames(quantities)) is not False
        






















class IfcEngine_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcEngine"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcEngineTypeEnum.USERDEFINED) or ((predefinedtype == IfcEngineTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcEngine_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcEngine"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcenginetype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcEngineType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcEngineType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcEngineTypeEnum.USERDEFINED) or ((predefinedtype == IfcEngineTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcEvaporativeCooler_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcEvaporativeCooler"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcEvaporativeCoolerTypeEnum.USERDEFINED) or ((predefinedtype == IfcEvaporativeCoolerTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcEvaporativeCooler_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcEvaporativeCooler"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcevaporativecoolertype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcEvaporativeCoolerType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcEvaporativeCoolerType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcEvaporativeCoolerTypeEnum.USERDEFINED) or ((predefinedtype == IfcEvaporativeCoolerTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcEvaporator_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcEvaporator"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcEvaporatorTypeEnum.USERDEFINED) or ((predefinedtype == IfcEvaporatorTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcEvaporator_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcEvaporator"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcevaporatortype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcEvaporatorType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcEvaporatorType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcEvaporatorTypeEnum.USERDEFINED) or ((predefinedtype == IfcEvaporatorTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcEvent_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcEvent"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcEventTypeEnum.USERDEFINED) or ((predefinedtype == IfcEventTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcEvent_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcEvent"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        eventtriggertype = self.EventTriggerType
        userdefinedeventtriggertype = self.UserDefinedEventTriggerType
        
        assert ((not exists(eventtriggertype)) or (eventtriggertype != IfcEventTriggerTypeEnum.USERDEFINED) or ((eventtriggertype == IfcEventTriggerTypeEnum.USERDEFINED) and exists(userdefinedeventtriggertype))) is not False
        







class IfcEventType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcEventType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcEventTypeEnum.USERDEFINED) or ((predefinedtype == IfcEventTypeEnum.USERDEFINED) and exists(self.ProcessType))) is not False
        



class IfcEventType_CorrectEventTriggerType:
    SCOPE = "entity"
    TYPE_NAME = "IfcEventType"
    RULE_NAME = "CorrectEventTriggerType"

    @staticmethod    
    def __call__(self):
        eventtriggertype = self.EventTriggerType
        userdefinedeventtriggertype = self.UserDefinedEventTriggerType
        
        assert ((eventtriggertype != IfcEventTriggerTypeEnum.USERDEFINED) or ((eventtriggertype == IfcEventTriggerTypeEnum.USERDEFINED) and exists(userdefinedeventtriggertype))) is not False
        










class IfcExternalReference_WR1:
    SCOPE = "entity"
    TYPE_NAME = "IfcExternalReference"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):
        location = self.Location
        identification = self.Identification
        name = self.Name
        
        assert (exists(identification) or exists(location) or exists(name)) is not False
        






















class IfcExtrudedAreaSolid_ValidExtrusionDirection:
    SCOPE = "entity"
    TYPE_NAME = "IfcExtrudedAreaSolid"
    RULE_NAME = "ValidExtrusionDirection"

    @staticmethod    
    def __call__(self):

        
        assert (IfcDotProduct(IfcDirection(DirectionRatios=[0.0,0.0,1.0]),self.ExtrudedDirection) != 0.0) is not False
        




class IfcExtrudedAreaSolidTapered_CorrectProfileAssignment:
    SCOPE = "entity"
    TYPE_NAME = "IfcExtrudedAreaSolidTapered"
    RULE_NAME = "CorrectProfileAssignment"

    @staticmethod    
    def __call__(self):

        
        assert (IfcTaperedSweptAreaProfiles(self.SweptArea,self.EndSweptArea)) is not False
        




class IfcFace_HasOuterBound:
    SCOPE = "entity"
    TYPE_NAME = "IfcFace"
    RULE_NAME = "HasOuterBound"

    @staticmethod    
    def __call__(self):
        bounds = self.Bounds
        
        assert ((sizeof([temp for temp in bounds if 'ifc4.ifcfaceouterbound' in typeof(temp)])) <= 1) is not False
        




def calc_IfcFaceBasedSurfaceModel_Dim(self):

    return \
    3






















class IfcFan_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcFan"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcFanTypeEnum.USERDEFINED) or ((predefinedtype == IfcFanTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcFan_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcFan"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcfantype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcFanType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcFanType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcFanTypeEnum.USERDEFINED) or ((predefinedtype == IfcFanTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcFastener_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcFastener"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcFastenerTypeEnum.USERDEFINED) or ((predefinedtype == IfcFastenerTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcFastener_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcFastener"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcfastenertype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcFastenerType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcFastenerType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcFastenerTypeEnum.USERDEFINED) or ((predefinedtype == IfcFastenerTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        










class IfcFeatureElementSubtraction_HasNoSubtraction:
    SCOPE = "entity"
    TYPE_NAME = "IfcFeatureElementSubtraction"
    RULE_NAME = "HasNoSubtraction"

    @staticmethod    
    def __call__(self):

        
        assert (sizeof(self.HasOpenings) == 0) is not False
        



class IfcFeatureElementSubtraction_IsNotFilling:
    SCOPE = "entity"
    TYPE_NAME = "IfcFeatureElementSubtraction"
    RULE_NAME = "IsNotFilling"

    @staticmethod    
    def __call__(self):

        
        assert (sizeof(self.FillsVoids) == 0) is not False
        




class IfcFillAreaStyle_MaxOneColour:
    SCOPE = "entity"
    TYPE_NAME = "IfcFillAreaStyle"
    RULE_NAME = "MaxOneColour"

    @staticmethod    
    def __call__(self):

        
        assert ((sizeof([style for style in self.FillStyles if 'ifc4.ifccolour' in typeof(style)])) <= 1) is not False
        



class IfcFillAreaStyle_MaxOneExtHatchStyle:
    SCOPE = "entity"
    TYPE_NAME = "IfcFillAreaStyle"
    RULE_NAME = "MaxOneExtHatchStyle"

    @staticmethod    
    def __call__(self):

        
        assert ((sizeof([style for style in self.FillStyles if 'ifc4.ifcexternallydefinedhatchstyle' in typeof(style)])) <= 1) is not False
        



class IfcFillAreaStyle_ConsistentHatchStyleDef:
    SCOPE = "entity"
    TYPE_NAME = "IfcFillAreaStyle"
    RULE_NAME = "ConsistentHatchStyleDef"

    @staticmethod    
    def __call__(self):

        
        assert (IfcCorrectFillAreaStyle(self.FillStyles)) is not False
        




class IfcFillAreaStyleHatching_PatternStart2D:
    SCOPE = "entity"
    TYPE_NAME = "IfcFillAreaStyleHatching"
    RULE_NAME = "PatternStart2D"

    @staticmethod    
    def __call__(self):
        patternstart = self.PatternStart
        
        assert ((not exists(patternstart)) or (patternstart.Dim == 2)) is not False
        



class IfcFillAreaStyleHatching_RefHatchLine2D:
    SCOPE = "entity"
    TYPE_NAME = "IfcFillAreaStyleHatching"
    RULE_NAME = "RefHatchLine2D"

    @staticmethod    
    def __call__(self):
        pointofreferencehatchline = self.PointOfReferenceHatchLine
        
        assert ((not exists(pointofreferencehatchline)) or (pointofreferencehatchline.Dim == 2)) is not False
        







class IfcFilter_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcFilter"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcFilterTypeEnum.USERDEFINED) or ((predefinedtype == IfcFilterTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcFilter_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcFilter"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcfiltertype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcFilterType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcFilterType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcFilterTypeEnum.USERDEFINED) or ((predefinedtype == IfcFilterTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcFireSuppressionTerminal_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcFireSuppressionTerminal"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcFireSuppressionTerminalTypeEnum.USERDEFINED) or ((predefinedtype == IfcFireSuppressionTerminalTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcFireSuppressionTerminal_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcFireSuppressionTerminal"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcfiresuppressionterminaltype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcFireSuppressionTerminalType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcFireSuppressionTerminalType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcFireSuppressionTerminalTypeEnum.USERDEFINED) or ((predefinedtype == IfcFireSuppressionTerminalTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcFixedReferenceSweptAreaSolid_DirectrixBounded:
    SCOPE = "entity"
    TYPE_NAME = "IfcFixedReferenceSweptAreaSolid"
    RULE_NAME = "DirectrixBounded"

    @staticmethod    
    def __call__(self):
        directrix = self.Directrix
        startparam = self.StartParam
        endparam = self.EndParam
        
        assert ((exists(startparam) and exists(endparam)) or ((sizeof(['ifc4.ifcconic','ifc4.ifcboundedcurve'] * typeof(directrix))) == 1)) is not False
        
















class IfcFlowInstrument_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcFlowInstrument"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcFlowInstrumentTypeEnum.USERDEFINED) or ((predefinedtype == IfcFlowInstrumentTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcFlowInstrument_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcFlowInstrument"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcflowinstrumenttype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcFlowInstrumentType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcFlowInstrumentType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcFlowInstrumentTypeEnum.USERDEFINED) or ((predefinedtype == IfcFlowInstrumentTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcFlowMeter_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcFlowMeter"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcFlowMeterTypeEnum.USERDEFINED) or ((predefinedtype == IfcFlowMeterTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcFlowMeter_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcFlowMeter"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcflowmetertype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcFlowMeterType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcFlowMeterType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcFlowMeterTypeEnum.USERDEFINED) or ((predefinedtype == IfcFlowMeterTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        


































class IfcFooting_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcFooting"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcFootingTypeEnum.USERDEFINED) or ((predefinedtype == IfcFootingTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcFooting_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcFooting"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcfootingtype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcFootingType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcFootingType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcFootingTypeEnum.USERDEFINED) or ((predefinedtype == IfcFootingTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        










class IfcFurniture_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcFurniture"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcFurnitureTypeEnum.USERDEFINED) or ((predefinedtype == IfcFurnitureTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcFurniture_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcFurniture"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcfurnituretype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcFurnitureType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcFurnitureType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcFurnitureTypeEnum.USERDEFINED) or ((predefinedtype == IfcFurnitureTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcGeographicElement_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcGeographicElement"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcGeographicElementTypeEnum.USERDEFINED) or ((predefinedtype == IfcGeographicElementTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcGeographicElement_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcGeographicElement"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcgeographicelementtype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcGeographicElementType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcGeographicElementType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcGeographicElementTypeEnum.USERDEFINED) or ((predefinedtype == IfcGeographicElementTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcGeometricCurveSet_NoSurfaces:
    SCOPE = "entity"
    TYPE_NAME = "IfcGeometricCurveSet"
    RULE_NAME = "NoSurfaces"

    @staticmethod    
    def __call__(self):

        
        assert ((sizeof([temp for temp in self.Elements if 'ifc4.ifcsurface' in typeof(temp)])) == 0) is not False
        




class IfcGeometricRepresentationContext_North2D:
    SCOPE = "entity"
    TYPE_NAME = "IfcGeometricRepresentationContext"
    RULE_NAME = "North2D"

    @staticmethod    
    def __call__(self):
        truenorth = self.TrueNorth
        
        assert ((not exists(truenorth)) or (hiindex(truenorth.DirectionRatios) == 2)) is not False
        







class IfcGeometricRepresentationSubContext_ParentNoSub:
    SCOPE = "entity"
    TYPE_NAME = "IfcGeometricRepresentationSubContext"
    RULE_NAME = "ParentNoSub"

    @staticmethod    
    def __call__(self):
        parentcontext = self.ParentContext
        
        assert (not 'ifc4.ifcgeometricrepresentationsubcontext' in typeof(parentcontext)) is not False
        



class IfcGeometricRepresentationSubContext_UserTargetProvided:
    SCOPE = "entity"
    TYPE_NAME = "IfcGeometricRepresentationSubContext"
    RULE_NAME = "UserTargetProvided"

    @staticmethod    
    def __call__(self):
        targetview = self.TargetView
        userdefinedtargetview = self.UserDefinedTargetView
        
        assert ((targetview != IfcGeometricProjectionEnum.USERDEFINED) or ((targetview == IfcGeometricProjectionEnum.USERDEFINED) and exists(userdefinedtargetview))) is not False
        



class IfcGeometricRepresentationSubContext_NoCoordOperation:
    SCOPE = "entity"
    TYPE_NAME = "IfcGeometricRepresentationSubContext"
    RULE_NAME = "NoCoordOperation"

    @staticmethod    
    def __call__(self):

        
        assert (sizeof(self.HasCoordinateOperation) == 0) is not False
        



def calc_IfcGeometricRepresentationSubContext_WorldCoordinateSystem(self):
    parentcontext = self.ParentContext
    return \
    parentcontext.WorldCoordinateSystem



def calc_IfcGeometricRepresentationSubContext_CoordinateSpaceDimension(self):
    parentcontext = self.ParentContext
    return \
    parentcontext.CoordinateSpaceDimension



def calc_IfcGeometricRepresentationSubContext_TrueNorth(self):
    parentcontext = self.ParentContext
    return \
    nvl(parentcontext.TrueNorth,IfcConvertDirectionInto2D(self.WorldCoordinateSystem.P[2 - 1]))



def calc_IfcGeometricRepresentationSubContext_Precision(self):
    parentcontext = self.ParentContext
    return \
    nvl(parentcontext.Precision,1)




class IfcGeometricSet_ConsistentDim:
    SCOPE = "entity"
    TYPE_NAME = "IfcGeometricSet"
    RULE_NAME = "ConsistentDim"

    @staticmethod    
    def __call__(self):
        elements = self.Elements
        
        assert ((sizeof([temp for temp in elements if temp.Dim != (elements[1 - 1].Dim)])) == 0) is not False
        



def calc_IfcGeometricSet_Dim(self):
    elements = self.Elements
    return \
    elements[1 - 1].Dim




class IfcGrid_HasPlacement:
    SCOPE = "entity"
    TYPE_NAME = "IfcGrid"
    RULE_NAME = "HasPlacement"

    @staticmethod    
    def __call__(self):

        
        assert (exists(self.ObjectPlacement)) is not False
        




class IfcGridAxis_WR1:
    SCOPE = "entity"
    TYPE_NAME = "IfcGridAxis"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):
        axiscurve = self.AxisCurve
        
        assert (axiscurve.Dim == 2) is not False
        



class IfcGridAxis_WR2:
    SCOPE = "entity"
    TYPE_NAME = "IfcGridAxis"
    RULE_NAME = "WR2"

    @staticmethod    
    def __call__(self):
        partofw = self.PartOfW
        partofv = self.PartOfV
        partofu = self.PartOfU
        
        assert ((sizeof(partofu) == 1) ^ (sizeof(partofv) == 1) ^ (sizeof(partofw) == 1)) is not False
        










def calc_IfcHalfSpaceSolid_Dim(self):

    return \
    3




class IfcHeatExchanger_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcHeatExchanger"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcHeatExchangerTypeEnum.USERDEFINED) or ((predefinedtype == IfcHeatExchangerTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcHeatExchanger_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcHeatExchanger"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcheatexchangertype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcHeatExchangerType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcHeatExchangerType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcHeatExchangerTypeEnum.USERDEFINED) or ((predefinedtype == IfcHeatExchangerTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcHumidifier_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcHumidifier"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcHumidifierTypeEnum.USERDEFINED) or ((predefinedtype == IfcHumidifierTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcHumidifier_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcHumidifier"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifchumidifiertype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcHumidifierType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcHumidifierType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcHumidifierTypeEnum.USERDEFINED) or ((predefinedtype == IfcHumidifierTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcIShapeProfileDef_ValidFlangeThickness:
    SCOPE = "entity"
    TYPE_NAME = "IfcIShapeProfileDef"
    RULE_NAME = "ValidFlangeThickness"

    @staticmethod    
    def __call__(self):
        overalldepth = self.OverallDepth
        flangethickness = self.FlangeThickness
        
        assert ((2. * flangethickness) < overalldepth) is not False
        



class IfcIShapeProfileDef_ValidWebThickness:
    SCOPE = "entity"
    TYPE_NAME = "IfcIShapeProfileDef"
    RULE_NAME = "ValidWebThickness"

    @staticmethod    
    def __call__(self):
        overallwidth = self.OverallWidth
        webthickness = self.WebThickness
        
        assert (webthickness < overallwidth) is not False
        



class IfcIShapeProfileDef_ValidFilletRadius:
    SCOPE = "entity"
    TYPE_NAME = "IfcIShapeProfileDef"
    RULE_NAME = "ValidFilletRadius"

    @staticmethod    
    def __call__(self):
        overallwidth = self.OverallWidth
        overalldepth = self.OverallDepth
        webthickness = self.WebThickness
        flangethickness = self.FlangeThickness
        filletradius = self.FilletRadius
        
        assert ((not exists(filletradius)) or ((filletradius <= ((overallwidth - webthickness) / 2.)) and (filletradius <= ((overalldepth - (2. * flangethickness)) / 2.)))) is not False
        










class IfcIndexedPolyCurve_Consecutive:
    SCOPE = "entity"
    TYPE_NAME = "IfcIndexedPolyCurve"
    RULE_NAME = "Consecutive"

    @staticmethod    
    def __call__(self):
        segments = self.Segments
        
        assert ((sizeof(segments) == 0) or IfcConsecutiveSegments(segments)) is not False
        
















class IfcInterceptor_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcInterceptor"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcInterceptorTypeEnum.USERDEFINED) or ((predefinedtype == IfcInterceptorTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcInterceptor_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcInterceptor"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcinterceptortype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcInterceptorType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcInterceptorType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcInterceptorTypeEnum.USERDEFINED) or ((predefinedtype == IfcInterceptorTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcIntersectionCurve_TwoPCurves:
    SCOPE = "entity"
    TYPE_NAME = "IfcIntersectionCurve"
    RULE_NAME = "TwoPCurves"

    @staticmethod    
    def __call__(self):

        
        assert (sizeof(self.AssociatedGeometry) == 2) is not False
        



class IfcIntersectionCurve_DistinctSurfaces:
    SCOPE = "entity"
    TYPE_NAME = "IfcIntersectionCurve"
    RULE_NAME = "DistinctSurfaces"

    @staticmethod    
    def __call__(self):

        
        assert ((IfcAssociatedSurface(self.AssociatedGeometry[1 - 1])) != (IfcAssociatedSurface(self.AssociatedGeometry[2 - 1]))) is not False
        













class IfcJunctionBox_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcJunctionBox"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcJunctionBoxTypeEnum.USERDEFINED) or ((predefinedtype == IfcJunctionBoxTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcJunctionBox_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcJunctionBox"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcjunctionboxtype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcJunctionBoxType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcJunctionBoxType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcJunctionBoxTypeEnum.USERDEFINED) or ((predefinedtype == IfcJunctionBoxTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcLShapeProfileDef_ValidThickness:
    SCOPE = "entity"
    TYPE_NAME = "IfcLShapeProfileDef"
    RULE_NAME = "ValidThickness"

    @staticmethod    
    def __call__(self):
        depth = self.Depth
        width = self.Width
        thickness = self.Thickness
        
        assert ((thickness < depth) and ((not exists(width)) or (thickness < width))) is not False
        




class IfcLaborResource_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcLaborResource"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcLaborResourceTypeEnum.USERDEFINED) or ((predefinedtype == IfcLaborResourceTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        




class IfcLaborResourceType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcLaborResourceType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcLaborResourceTypeEnum.USERDEFINED) or ((predefinedtype == IfcLaborResourceTypeEnum.USERDEFINED) and exists(self.ResourceType))) is not False
        







class IfcLamp_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcLamp"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcLampTypeEnum.USERDEFINED) or ((predefinedtype == IfcLampTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcLamp_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcLamp"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifclamptype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcLampType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcLampType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcLampTypeEnum.USERDEFINED) or ((predefinedtype == IfcLampTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        













class IfcLightFixture_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcLightFixture"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcLightFixtureTypeEnum.USERDEFINED) or ((predefinedtype == IfcLightFixtureTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcLightFixture_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcLightFixture"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifclightfixturetype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcLightFixtureType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcLightFixtureType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcLightFixtureTypeEnum.USERDEFINED) or ((predefinedtype == IfcLightFixtureTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        

























class IfcLine_SameDim:
    SCOPE = "entity"
    TYPE_NAME = "IfcLine"
    RULE_NAME = "SameDim"

    @staticmethod    
    def __call__(self):
        pnt = self.Pnt
        dir = self.Dir
        
        assert (dir.Dim == pnt.Dim) is not False
        




class IfcLocalPlacement_WR21:
    SCOPE = "entity"
    TYPE_NAME = "IfcLocalPlacement"
    RULE_NAME = "WR21"

    @staticmethod    
    def __call__(self):
        placementrelto = self.PlacementRelTo
        relativeplacement = self.RelativePlacement
        
        assert (IfcCorrectLocalPlacement(relativeplacement,placementrelto)) is not False
        































class IfcMaterialDefinitionRepresentation_OnlyStyledRepresentations:
    SCOPE = "entity"
    TYPE_NAME = "IfcMaterialDefinitionRepresentation"
    RULE_NAME = "OnlyStyledRepresentations"

    @staticmethod    
    def __call__(self):
        representations = self.Representations
        
        assert ((sizeof([temp for temp in representations if not 'ifc4.ifcstyledrepresentation' in typeof(temp)])) == 0) is not False
        




class IfcMaterialLayer_NormalizedPriority:
    SCOPE = "entity"
    TYPE_NAME = "IfcMaterialLayer"
    RULE_NAME = "NormalizedPriority"

    @staticmethod    
    def __call__(self):
        priority = self.Priority
        
        assert ((not exists(priority)) or (0 <= priority <= 100)) is not False
        




def calc_IfcMaterialLayerSet_TotalThickness(self):

    return \
    IfcMlsTotalThickness(self)













class IfcMaterialProfile_NormalizedPriority:
    SCOPE = "entity"
    TYPE_NAME = "IfcMaterialProfile"
    RULE_NAME = "NormalizedPriority"

    @staticmethod    
    def __call__(self):
        priority = self.Priority
        
        assert ((not exists(priority)) or (0 <= priority <= 100)) is not False
        




























class IfcMechanicalFastener_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcMechanicalFastener"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcMechanicalFastenerTypeEnum.USERDEFINED) or ((predefinedtype == IfcMechanicalFastenerTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcMechanicalFastener_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcMechanicalFastener"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcmechanicalfastenertype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcMechanicalFastenerType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcMechanicalFastenerType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcMechanicalFastenerTypeEnum.USERDEFINED) or ((predefinedtype == IfcMechanicalFastenerTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcMedicalDevice_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcMedicalDevice"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcMedicalDeviceTypeEnum.USERDEFINED) or ((predefinedtype == IfcMedicalDeviceTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcMedicalDevice_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcMedicalDevice"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcmedicaldevicetype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcMedicalDeviceType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcMedicalDeviceType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcMedicalDeviceTypeEnum.USERDEFINED) or ((predefinedtype == IfcMedicalDeviceTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcMember_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcMember"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcMemberTypeEnum.USERDEFINED) or ((predefinedtype == IfcMemberTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcMember_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcMember"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcmembertype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcMemberStandardCase_HasMaterialProfileSetUsage:
    SCOPE = "entity"
    TYPE_NAME = "IfcMemberStandardCase"
    RULE_NAME = "HasMaterialProfileSetUsage"

    @staticmethod    
    def __call__(self):

        
        assert ((sizeof([temp for temp in usedin(self,'ifc4.ifcrelassociates.relatedobjects') if ('ifc4.ifcrelassociatesmaterial' in typeof(temp)) and ('ifc4.ifcmaterialprofilesetusage' in typeof(temp.RelatingMaterial))])) == 1) is not False
        




class IfcMemberType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcMemberType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcMemberTypeEnum.USERDEFINED) or ((predefinedtype == IfcMemberTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        







def calc_IfcMirroredProfileDef_Operator(self):

    return \
    IfcCartesianTransformationOperator2D(Axis1=IfcDirection(DirectionRatios=[-1.,0.]), Axis2=IfcDirection(DirectionRatios=[0.,1.]), LocalOrigin=IfcCartesianPoint(Coordinates=[0.,0.]), Scale=1.)







class IfcMotorConnection_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcMotorConnection"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcMotorConnectionTypeEnum.USERDEFINED) or ((predefinedtype == IfcMotorConnectionTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcMotorConnection_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcMotorConnection"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcmotorconnectiontype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcMotorConnectionType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcMotorConnectionType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcMotorConnectionTypeEnum.USERDEFINED) or ((predefinedtype == IfcMotorConnectionTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcNamedUnit_WR1:
    SCOPE = "entity"
    TYPE_NAME = "IfcNamedUnit"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):

        
        assert (IfcCorrectDimensions(self.UnitType,self.Dimensions)) is not False
        




class IfcObject_UniquePropertySetNames:
    SCOPE = "entity"
    TYPE_NAME = "IfcObject"
    RULE_NAME = "UniquePropertySetNames"

    @staticmethod    
    def __call__(self):
        isdefinedby = self.IsDefinedBy
        
        assert ((sizeof(isdefinedby) == 0) or IfcUniqueDefinitionNames(isdefinedby)) is not False
        










class IfcObjective_WR21:
    SCOPE = "entity"
    TYPE_NAME = "IfcObjective"
    RULE_NAME = "WR21"

    @staticmethod    
    def __call__(self):
        objectivequalifier = self.ObjectiveQualifier
        
        assert ((objectivequalifier != IfcObjectiveEnum.USERDEFINED) or ((objectivequalifier == IfcObjectiveEnum.USERDEFINED) and exists(self.UserDefinedQualifier))) is not False
        




class IfcOccupant_WR31:
    SCOPE = "entity"
    TYPE_NAME = "IfcOccupant"
    RULE_NAME = "WR31"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not predefinedtype == IfcOccupantTypeEnum.USERDEFINED) or exists(self.ObjectType)) is not False
        




class IfcOffsetCurve2D_DimIs2D:
    SCOPE = "entity"
    TYPE_NAME = "IfcOffsetCurve2D"
    RULE_NAME = "DimIs2D"

    @staticmethod    
    def __call__(self):
        basiscurve = self.BasisCurve
        
        assert (basiscurve.Dim == 2) is not False
        




class IfcOffsetCurve3D_DimIs2D:
    SCOPE = "entity"
    TYPE_NAME = "IfcOffsetCurve3D"
    RULE_NAME = "DimIs2D"

    @staticmethod    
    def __call__(self):
        basiscurve = self.BasisCurve
        
        assert (basiscurve.Dim == 3) is not False
        



















class IfcOrientedEdge_EdgeElementNotOriented:
    SCOPE = "entity"
    TYPE_NAME = "IfcOrientedEdge"
    RULE_NAME = "EdgeElementNotOriented"

    @staticmethod    
    def __call__(self):
        edgeelement = self.EdgeElement
        
        assert (not 'ifc4.ifcorientededge' in typeof(edgeelement)) is not False
        



def calc_IfcOrientedEdge_EdgeStart(self):
    edgeelement = self.EdgeElement
    orientation = self.Orientation
    return \
    IfcBooleanChoose(orientation,edgeelement.EdgeStart,edgeelement.EdgeEnd)



def calc_IfcOrientedEdge_EdgeEnd(self):
    edgeelement = self.EdgeElement
    orientation = self.Orientation
    return \
    IfcBooleanChoose(orientation,edgeelement.EdgeEnd,edgeelement.EdgeStart)







class IfcOutlet_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcOutlet"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcOutletTypeEnum.USERDEFINED) or ((predefinedtype == IfcOutletTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcOutlet_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcOutlet"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcoutlettype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcOutletType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcOutletType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcOutletTypeEnum.USERDEFINED) or ((predefinedtype == IfcOutletTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcOwnerHistory_CorrectChangeAction:
    SCOPE = "entity"
    TYPE_NAME = "IfcOwnerHistory"
    RULE_NAME = "CorrectChangeAction"

    @staticmethod    
    def __call__(self):
        changeaction = self.ChangeAction
        lastmodifieddate = self.LastModifiedDate
        
        assert (exists(lastmodifieddate) or ((not exists(lastmodifieddate)) and (not exists(changeaction))) or ((not exists(lastmodifieddate)) and exists(changeaction) and ((changeaction == IfcChangeActionEnum.NOTDEFINED) or (changeaction == IfcChangeActionEnum.NOCHANGE)))) is not False
        







class IfcPath_IsContinuous:
    SCOPE = "entity"
    TYPE_NAME = "IfcPath"
    RULE_NAME = "IsContinuous"

    @staticmethod    
    def __call__(self):

        
        assert (IfcPathHeadToTail(self)) is not False
        




class IfcPcurve_DimIs2D:
    SCOPE = "entity"
    TYPE_NAME = "IfcPcurve"
    RULE_NAME = "DimIs2D"

    @staticmethod    
    def __call__(self):
        referencecurve = self.ReferenceCurve
        
        assert (referencecurve.Dim == 2) is not False
        













class IfcPerson_IdentifiablePerson:
    SCOPE = "entity"
    TYPE_NAME = "IfcPerson"
    RULE_NAME = "IdentifiablePerson"

    @staticmethod    
    def __call__(self):
        identification = self.Identification
        familyname = self.FamilyName
        givenname = self.GivenName
        
        assert (exists(identification) or exists(familyname) or exists(givenname)) is not False
        



class IfcPerson_ValidSetOfNames:
    SCOPE = "entity"
    TYPE_NAME = "IfcPerson"
    RULE_NAME = "ValidSetOfNames"

    @staticmethod    
    def __call__(self):
        familyname = self.FamilyName
        givenname = self.GivenName
        middlenames = self.MiddleNames
        
        assert ((not exists(middlenames)) or exists(familyname) or exists(givenname)) is not False
        







class IfcPhysicalComplexQuantity_NoSelfReference:
    SCOPE = "entity"
    TYPE_NAME = "IfcPhysicalComplexQuantity"
    RULE_NAME = "NoSelfReference"

    @staticmethod    
    def __call__(self):
        hasquantities = self.HasQuantities
        
        assert ((sizeof([temp for temp in hasquantities if self == temp])) == 0) is not False
        



class IfcPhysicalComplexQuantity_UniqueQuantityNames:
    SCOPE = "entity"
    TYPE_NAME = "IfcPhysicalComplexQuantity"
    RULE_NAME = "UniqueQuantityNames"

    @staticmethod    
    def __call__(self):
        hasquantities = self.HasQuantities
        
        assert (IfcUniqueQuantityNames(hasquantities)) is not False
        










class IfcPile_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcPile"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcPileTypeEnum.USERDEFINED) or ((predefinedtype == IfcPileTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcPile_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcPile"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcpiletype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcPileType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcPileType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcPileTypeEnum.USERDEFINED) or ((predefinedtype == IfcPileTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcPipeFitting_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcPipeFitting"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcPipeFittingTypeEnum.USERDEFINED) or ((predefinedtype == IfcPipeFittingTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcPipeFitting_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcPipeFitting"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcpipefittingtype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcPipeFittingType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcPipeFittingType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcPipeFittingTypeEnum.USERDEFINED) or ((predefinedtype == IfcPipeFittingTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcPipeSegment_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcPipeSegment"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcPipeSegmentTypeEnum.USERDEFINED) or ((predefinedtype == IfcPipeSegmentTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcPipeSegment_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcPipeSegment"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcpipesegmenttype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcPipeSegmentType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcPipeSegmentType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcPipeSegmentTypeEnum.USERDEFINED) or ((predefinedtype == IfcPipeSegmentTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcPixelTexture_MinPixelInS:
    SCOPE = "entity"
    TYPE_NAME = "IfcPixelTexture"
    RULE_NAME = "MinPixelInS"

    @staticmethod    
    def __call__(self):
        width = self.Width
        
        assert (width >= 1) is not False
        



class IfcPixelTexture_MinPixelInT:
    SCOPE = "entity"
    TYPE_NAME = "IfcPixelTexture"
    RULE_NAME = "MinPixelInT"

    @staticmethod    
    def __call__(self):
        height = self.Height
        
        assert (height >= 1) is not False
        



class IfcPixelTexture_NumberOfColours:
    SCOPE = "entity"
    TYPE_NAME = "IfcPixelTexture"
    RULE_NAME = "NumberOfColours"

    @staticmethod    
    def __call__(self):
        colourcomponents = self.ColourComponents
        
        assert (1 <= colourcomponents <= 4) is not False
        



class IfcPixelTexture_SizeOfPixelList:
    SCOPE = "entity"
    TYPE_NAME = "IfcPixelTexture"
    RULE_NAME = "SizeOfPixelList"

    @staticmethod    
    def __call__(self):
        width = self.Width
        height = self.Height
        pixel = self.Pixel
        
        assert (sizeof(pixel) == (width * height)) is not False
        



class IfcPixelTexture_PixelAsByteAndSameLength:
    SCOPE = "entity"
    TYPE_NAME = "IfcPixelTexture"
    RULE_NAME = "PixelAsByteAndSameLength"

    @staticmethod    
    def __call__(self):
        pixel = self.Pixel
        
        assert ((sizeof([temp for temp in pixel if ((blength(temp) % 8) == 0) and (blength(temp) == (blength(pixel[1 - 1])))])) == sizeof(pixel)) is not False
        




def calc_IfcPlacement_Dim(self):
    location = self.Location
    return \
    location.Dim













class IfcPlate_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcPlate"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcPlateTypeEnum.USERDEFINED) or ((predefinedtype == IfcPlateTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcPlate_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcPlate"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcplatetype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcPlateStandardCase_HasMaterialLayerSetUsage:
    SCOPE = "entity"
    TYPE_NAME = "IfcPlateStandardCase"
    RULE_NAME = "HasMaterialLayerSetUsage"

    @staticmethod    
    def __call__(self):

        
        assert ((sizeof([temp for temp in usedin(self,'ifc4.ifcrelassociates.relatedobjects') if ('ifc4.ifcrelassociatesmaterial' in typeof(temp)) and ('ifc4.ifcmateriallayersetusage' in typeof(temp.RelatingMaterial))])) == 1) is not False
        




class IfcPlateType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcPlateType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcPlateTypeEnum.USERDEFINED) or ((predefinedtype == IfcPlateTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        







def calc_IfcPointOnCurve_Dim(self):
    basiscurve = self.BasisCurve
    return \
    basiscurve.Dim




def calc_IfcPointOnSurface_Dim(self):
    basissurface = self.BasisSurface
    return \
    basissurface.Dim




class IfcPolyLoop_AllPointsSameDim:
    SCOPE = "entity"
    TYPE_NAME = "IfcPolyLoop"
    RULE_NAME = "AllPointsSameDim"

    @staticmethod    
    def __call__(self):
        polygon = self.Polygon
        
        assert ((sizeof([temp for temp in polygon if temp.Dim != (polygon[1 - 1].Dim)])) == 0) is not False
        




class IfcPolygonalBoundedHalfSpace_BoundaryDim:
    SCOPE = "entity"
    TYPE_NAME = "IfcPolygonalBoundedHalfSpace"
    RULE_NAME = "BoundaryDim"

    @staticmethod    
    def __call__(self):
        polygonalboundary = self.PolygonalBoundary
        
        assert (polygonalboundary.Dim == 2) is not False
        



class IfcPolygonalBoundedHalfSpace_BoundaryType:
    SCOPE = "entity"
    TYPE_NAME = "IfcPolygonalBoundedHalfSpace"
    RULE_NAME = "BoundaryType"

    @staticmethod    
    def __call__(self):
        polygonalboundary = self.PolygonalBoundary
        
        assert ((sizeof(typeof(polygonalboundary) * ['ifc4.ifcpolyline','ifc4.ifccompositecurve'])) == 1) is not False
        







class IfcPolyline_SameDim:
    SCOPE = "entity"
    TYPE_NAME = "IfcPolyline"
    RULE_NAME = "SameDim"

    @staticmethod    
    def __call__(self):
        points = self.Points
        
        assert ((sizeof([temp for temp in points if temp.Dim != (points[1 - 1].Dim)])) == 0) is not False
        







class IfcPostalAddress_WR1:
    SCOPE = "entity"
    TYPE_NAME = "IfcPostalAddress"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):
        internallocation = self.InternalLocation
        addresslines = self.AddressLines
        postalbox = self.PostalBox
        town = self.Town
        region = self.Region
        postalcode = self.PostalCode
        country = self.Country
        
        assert (exists(internallocation) or exists(addresslines) or exists(postalbox) or exists(postalcode) or exists(town) or exists(region) or exists(country)) is not False
        

























class IfcPresentationLayerAssignment_ApplicableItems:
    SCOPE = "entity"
    TYPE_NAME = "IfcPresentationLayerAssignment"
    RULE_NAME = "ApplicableItems"

    @staticmethod    
    def __call__(self):
        assigneditems = self.AssignedItems
        
        assert ((sizeof([temp for temp in assigneditems if (sizeof(typeof(temp) * ['ifc4.ifcshaperepresentation','ifc4.ifcgeometricrepresentationitem','ifc4.ifcmappeditem'])) == 1])) == sizeof(assigneditems)) is not False
        




class IfcPresentationLayerWithStyle_ApplicableOnlyToItems:
    SCOPE = "entity"
    TYPE_NAME = "IfcPresentationLayerWithStyle"
    RULE_NAME = "ApplicableOnlyToItems"

    @staticmethod    
    def __call__(self):
        assigneditems = self.AssignedItems
        
        assert ((sizeof([temp for temp in assigneditems if (sizeof(typeof(temp) * ['ifc4.ifcgeometricrepresentationitem','ifc4.ifcmappeditem'])) == 1])) == sizeof(assigneditems)) is not False
        










class IfcProcedure_HasName:
    SCOPE = "entity"
    TYPE_NAME = "IfcProcedure"
    RULE_NAME = "HasName"

    @staticmethod    
    def __call__(self):

        
        assert (exists(self.Name)) is not False
        



class IfcProcedure_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcProcedure"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcProcedureTypeEnum.USERDEFINED) or ((predefinedtype == IfcProcedureTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        




class IfcProcedureType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcProcedureType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcProcedureTypeEnum.USERDEFINED) or ((predefinedtype == IfcProcedureTypeEnum.USERDEFINED) and exists(self.ProcessType))) is not False
        







class IfcProduct_PlacementForShapeRepresentation:
    SCOPE = "entity"
    TYPE_NAME = "IfcProduct"
    RULE_NAME = "PlacementForShapeRepresentation"

    @staticmethod    
    def __call__(self):
        objectplacement = self.ObjectPlacement
        representation = self.Representation
        
        assert ((exists(representation) and exists(objectplacement)) or (exists(representation) and ((sizeof([temp for temp in representation.Representations if 'ifc4.ifcshaperepresentation' in typeof(temp)])) == 0)) or (not exists(representation))) is not False
        




class IfcProductDefinitionShape_OnlyShapeModel:
    SCOPE = "entity"
    TYPE_NAME = "IfcProductDefinitionShape"
    RULE_NAME = "OnlyShapeModel"

    @staticmethod    
    def __call__(self):
        representations = self.Representations
        
        assert ((sizeof([temp for temp in representations if not 'ifc4.ifcshapemodel' in typeof(temp)])) == 0) is not False
        













class IfcProject_HasName:
    SCOPE = "entity"
    TYPE_NAME = "IfcProject"
    RULE_NAME = "HasName"

    @staticmethod    
    def __call__(self):

        
        assert (exists(self.Name)) is not False
        



class IfcProject_CorrectContext:
    SCOPE = "entity"
    TYPE_NAME = "IfcProject"
    RULE_NAME = "CorrectContext"

    @staticmethod    
    def __call__(self):

        
        assert ((not exists(self.RepresentationContexts)) or ((sizeof([temp for temp in self.RepresentationContexts if 'ifc4.ifcgeometricrepresentationsubcontext' in typeof(temp)])) == 0)) is not False
        



class IfcProject_NoDecomposition:
    SCOPE = "entity"
    TYPE_NAME = "IfcProject"
    RULE_NAME = "NoDecomposition"

    @staticmethod    
    def __call__(self):

        
        assert (sizeof(self.Decomposes) == 0) is not False
        










class IfcProjectedCRS_IsLengthUnit:
    SCOPE = "entity"
    TYPE_NAME = "IfcProjectedCRS"
    RULE_NAME = "IsLengthUnit"

    @staticmethod    
    def __call__(self):
        mapunit = self.MapUnit
        
        assert ((not exists(mapunit)) or (mapunit.UnitType == IfcUnitEnum.LENGTHUNIT)) is not False
        













class IfcPropertyBoundedValue_SameUnitUpperLower:
    SCOPE = "entity"
    TYPE_NAME = "IfcPropertyBoundedValue"
    RULE_NAME = "SameUnitUpperLower"

    @staticmethod    
    def __call__(self):
        upperboundvalue = self.UpperBoundValue
        lowerboundvalue = self.LowerBoundValue
        
        assert ((not exists(upperboundvalue)) or (not exists(lowerboundvalue)) or (typeof(upperboundvalue) == typeof(lowerboundvalue))) is not False
        



class IfcPropertyBoundedValue_SameUnitUpperSet:
    SCOPE = "entity"
    TYPE_NAME = "IfcPropertyBoundedValue"
    RULE_NAME = "SameUnitUpperSet"

    @staticmethod    
    def __call__(self):
        upperboundvalue = self.UpperBoundValue
        setpointvalue = self.SetPointValue
        
        assert ((not exists(upperboundvalue)) or (not exists(setpointvalue)) or (typeof(upperboundvalue) == typeof(setpointvalue))) is not False
        



class IfcPropertyBoundedValue_SameUnitLowerSet:
    SCOPE = "entity"
    TYPE_NAME = "IfcPropertyBoundedValue"
    RULE_NAME = "SameUnitLowerSet"

    @staticmethod    
    def __call__(self):
        lowerboundvalue = self.LowerBoundValue
        setpointvalue = self.SetPointValue
        
        assert ((not exists(lowerboundvalue)) or (not exists(setpointvalue)) or (typeof(lowerboundvalue) == typeof(setpointvalue))) is not False
        







class IfcPropertyDependencyRelationship_NoSelfReference:
    SCOPE = "entity"
    TYPE_NAME = "IfcPropertyDependencyRelationship"
    RULE_NAME = "NoSelfReference"

    @staticmethod    
    def __call__(self):
        dependingproperty = self.DependingProperty
        dependantproperty = self.DependantProperty
        
        assert (dependingproperty != dependantproperty) is not False
        




class IfcPropertyEnumeratedValue_WR21:
    SCOPE = "entity"
    TYPE_NAME = "IfcPropertyEnumeratedValue"
    RULE_NAME = "WR21"

    @staticmethod    
    def __call__(self):
        enumerationvalues = self.EnumerationValues
        enumerationreference = self.EnumerationReference
        
        assert ((not exists(enumerationreference)) or (not exists(enumerationvalues)) or ((sizeof([temp for temp in enumerationvalues if temp in enumerationreference.EnumerationValues])) == sizeof(enumerationvalues))) is not False
        




class IfcPropertyEnumeration_WR01:
    SCOPE = "entity"
    TYPE_NAME = "IfcPropertyEnumeration"
    RULE_NAME = "WR01"

    @staticmethod    
    def __call__(self):

        
        assert ((sizeof([temp for temp in self.EnumerationValues if not (typeof(self.EnumerationValues[1 - 1])) == typeof(temp)])) == 0) is not False
        




class IfcPropertyListValue_WR31:
    SCOPE = "entity"
    TYPE_NAME = "IfcPropertyListValue"
    RULE_NAME = "WR31"

    @staticmethod    
    def __call__(self):

        
        assert ((sizeof([temp for temp in self.ListValues if not (typeof(self.ListValues[1 - 1])) == typeof(temp)])) == 0) is not False
        







class IfcPropertySet_ExistsName:
    SCOPE = "entity"
    TYPE_NAME = "IfcPropertySet"
    RULE_NAME = "ExistsName"

    @staticmethod    
    def __call__(self):

        
        assert (exists(self.Name)) is not False
        



class IfcPropertySet_UniquePropertyNames:
    SCOPE = "entity"
    TYPE_NAME = "IfcPropertySet"
    RULE_NAME = "UniquePropertyNames"

    @staticmethod    
    def __call__(self):
        hasproperties = self.HasProperties
        
        assert (IfcUniquePropertyName(hasproperties)) is not False
        







class IfcPropertySetTemplate_ExistsName:
    SCOPE = "entity"
    TYPE_NAME = "IfcPropertySetTemplate"
    RULE_NAME = "ExistsName"

    @staticmethod    
    def __call__(self):

        
        assert (exists(self.Name)) is not False
        



class IfcPropertySetTemplate_UniquePropertyNames:
    SCOPE = "entity"
    TYPE_NAME = "IfcPropertySetTemplate"
    RULE_NAME = "UniquePropertyNames"

    @staticmethod    
    def __call__(self):
        haspropertytemplates = self.HasPropertyTemplates
        
        assert (IfcUniquePropertyTemplateNames(haspropertytemplates)) is not False
        







class IfcPropertyTableValue_WR21:
    SCOPE = "entity"
    TYPE_NAME = "IfcPropertyTableValue"
    RULE_NAME = "WR21"

    @staticmethod    
    def __call__(self):
        definingvalues = self.DefiningValues
        definedvalues = self.DefinedValues
        
        assert (((not exists(definingvalues)) and (not exists(definedvalues))) or (sizeof(definingvalues) == sizeof(definedvalues))) is not False
        



class IfcPropertyTableValue_WR22:
    SCOPE = "entity"
    TYPE_NAME = "IfcPropertyTableValue"
    RULE_NAME = "WR22"

    @staticmethod    
    def __call__(self):
        definingvalues = self.DefiningValues
        
        assert ((not exists(definingvalues)) or ((sizeof([temp for temp in self.DefiningValues if typeof(temp) != (typeof(self.DefiningValues[1 - 1]))])) == 0)) is not False
        



class IfcPropertyTableValue_WR23:
    SCOPE = "entity"
    TYPE_NAME = "IfcPropertyTableValue"
    RULE_NAME = "WR23"

    @staticmethod    
    def __call__(self):
        definedvalues = self.DefinedValues
        
        assert ((not exists(definedvalues)) or ((sizeof([temp for temp in self.DefinedValues if typeof(temp) != (typeof(self.DefinedValues[1 - 1]))])) == 0)) is not False
        










class IfcProtectiveDevice_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcProtectiveDevice"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcProtectiveDeviceTypeEnum.USERDEFINED) or ((predefinedtype == IfcProtectiveDeviceTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcProtectiveDevice_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcProtectiveDevice"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcprotectivedevicetype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcProtectiveDeviceTrippingUnit_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcProtectiveDeviceTrippingUnit"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcProtectiveDeviceTrippingUnitTypeEnum.USERDEFINED) or ((predefinedtype == IfcProtectiveDeviceTrippingUnitTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcProtectiveDeviceTrippingUnit_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcProtectiveDeviceTrippingUnit"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcprotectivedevicetrippingunittype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcProtectiveDeviceTrippingUnitType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcProtectiveDeviceTrippingUnitType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcProtectiveDeviceTrippingUnitTypeEnum.USERDEFINED) or ((predefinedtype == IfcProtectiveDeviceTrippingUnitTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcProtectiveDeviceType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcProtectiveDeviceType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcProtectiveDeviceTypeEnum.USERDEFINED) or ((predefinedtype == IfcProtectiveDeviceTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcProxy_WR1:
    SCOPE = "entity"
    TYPE_NAME = "IfcProxy"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):

        
        assert (exists(self.Name)) is not False
        




class IfcPump_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcPump"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcPumpTypeEnum.USERDEFINED) or ((predefinedtype == IfcPumpTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcPump_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcPump"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcpumptype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcPumpType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcPumpType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcPumpTypeEnum.USERDEFINED) or ((predefinedtype == IfcPumpTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcQuantityArea_WR21:
    SCOPE = "entity"
    TYPE_NAME = "IfcQuantityArea"
    RULE_NAME = "WR21"

    @staticmethod    
    def __call__(self):

        
        assert ((not exists(self.Unit)) or (self.Unit.UnitType == IfcUnitEnum.AREAUNIT)) is not False
        



class IfcQuantityArea_WR22:
    SCOPE = "entity"
    TYPE_NAME = "IfcQuantityArea"
    RULE_NAME = "WR22"

    @staticmethod    
    def __call__(self):
        areavalue = self.AreaValue
        
        assert (areavalue >= 0.) is not False
        




class IfcQuantityCount_WR21:
    SCOPE = "entity"
    TYPE_NAME = "IfcQuantityCount"
    RULE_NAME = "WR21"

    @staticmethod    
    def __call__(self):
        countvalue = self.CountValue
        
        assert (countvalue >= 0.) is not False
        




class IfcQuantityLength_WR21:
    SCOPE = "entity"
    TYPE_NAME = "IfcQuantityLength"
    RULE_NAME = "WR21"

    @staticmethod    
    def __call__(self):

        
        assert ((not exists(self.Unit)) or (self.Unit.UnitType == IfcUnitEnum.LENGTHUNIT)) is not False
        



class IfcQuantityLength_WR22:
    SCOPE = "entity"
    TYPE_NAME = "IfcQuantityLength"
    RULE_NAME = "WR22"

    @staticmethod    
    def __call__(self):
        lengthvalue = self.LengthValue
        
        assert (lengthvalue >= 0.) is not False
        







class IfcQuantityTime_WR21:
    SCOPE = "entity"
    TYPE_NAME = "IfcQuantityTime"
    RULE_NAME = "WR21"

    @staticmethod    
    def __call__(self):

        
        assert ((not exists(self.Unit)) or (self.Unit.UnitType == IfcUnitEnum.TIMEUNIT)) is not False
        



class IfcQuantityTime_WR22:
    SCOPE = "entity"
    TYPE_NAME = "IfcQuantityTime"
    RULE_NAME = "WR22"

    @staticmethod    
    def __call__(self):
        timevalue = self.TimeValue
        
        assert (timevalue >= 0.) is not False
        




class IfcQuantityVolume_WR21:
    SCOPE = "entity"
    TYPE_NAME = "IfcQuantityVolume"
    RULE_NAME = "WR21"

    @staticmethod    
    def __call__(self):

        
        assert ((not exists(self.Unit)) or (self.Unit.UnitType == IfcUnitEnum.VOLUMEUNIT)) is not False
        



class IfcQuantityVolume_WR22:
    SCOPE = "entity"
    TYPE_NAME = "IfcQuantityVolume"
    RULE_NAME = "WR22"

    @staticmethod    
    def __call__(self):
        volumevalue = self.VolumeValue
        
        assert (volumevalue >= 0.) is not False
        




class IfcQuantityWeight_WR21:
    SCOPE = "entity"
    TYPE_NAME = "IfcQuantityWeight"
    RULE_NAME = "WR21"

    @staticmethod    
    def __call__(self):

        
        assert ((not exists(self.Unit)) or (self.Unit.UnitType == IfcUnitEnum.MASSUNIT)) is not False
        



class IfcQuantityWeight_WR22:
    SCOPE = "entity"
    TYPE_NAME = "IfcQuantityWeight"
    RULE_NAME = "WR22"

    @staticmethod    
    def __call__(self):
        weightvalue = self.WeightValue
        
        assert (weightvalue >= 0.) is not False
        




class IfcRailing_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcRailing"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcRailingTypeEnum.USERDEFINED) or ((predefinedtype == IfcRailingTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcRailing_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcRailing"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcrailingtype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcRailingType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcRailingType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcRailingTypeEnum.USERDEFINED) or ((predefinedtype == IfcRailingTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcRamp_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcRamp"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcRampTypeEnum.USERDEFINED) or ((predefinedtype == IfcRampTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcRamp_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcRamp"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcramptype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcRampFlight_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcRampFlight"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcRampFlightTypeEnum.USERDEFINED) or ((predefinedtype == IfcRampFlightTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcRampFlight_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcRampFlight"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcrampflighttype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcRampFlightType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcRampFlightType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcRampFlightTypeEnum.USERDEFINED) or ((predefinedtype == IfcRampFlightTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcRampType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcRampType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcRampTypeEnum.USERDEFINED) or ((predefinedtype == IfcRampTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcRationalBSplineCurveWithKnots_SameNumOfWeightsAndPoints:
    SCOPE = "entity"
    TYPE_NAME = "IfcRationalBSplineCurveWithKnots"
    RULE_NAME = "SameNumOfWeightsAndPoints"

    @staticmethod    
    def __call__(self):
        weightsdata = self.WeightsData
        
        assert (sizeof(weightsdata) == sizeof(self.ControlPointsList)) is not False
        



class IfcRationalBSplineCurveWithKnots_WeightsGreaterZero:
    SCOPE = "entity"
    TYPE_NAME = "IfcRationalBSplineCurveWithKnots"
    RULE_NAME = "WeightsGreaterZero"

    @staticmethod    
    def __call__(self):

        
        assert (IfcCurveWeightsPositive(self)) is not False
        



def calc_IfcRationalBSplineCurveWithKnots_Weights(self):
    weightsdata = self.WeightsData
    return \
    IfcListToArray(weightsdata,0,self.UpperIndexOnControlPoints)




class IfcRationalBSplineSurfaceWithKnots_CorrespondingWeightsDataLists:
    SCOPE = "entity"
    TYPE_NAME = "IfcRationalBSplineSurfaceWithKnots"
    RULE_NAME = "CorrespondingWeightsDataLists"

    @staticmethod    
    def __call__(self):
        weightsdata = self.WeightsData
        
        assert ((sizeof(weightsdata) == sizeof(self.ControlPointsList)) and ((sizeof(weightsdata[1 - 1])) == (sizeof(self.ControlPointsList[1 - 1])))) is not False
        



class IfcRationalBSplineSurfaceWithKnots_WeightValuesGreaterZero:
    SCOPE = "entity"
    TYPE_NAME = "IfcRationalBSplineSurfaceWithKnots"
    RULE_NAME = "WeightValuesGreaterZero"

    @staticmethod    
    def __call__(self):

        
        assert (IfcSurfaceWeightsPositive(self)) is not False
        



def calc_IfcRationalBSplineSurfaceWithKnots_Weights(self):
    uupper = self.UUpper
    vupper = self.VUpper
    weightsdata = self.WeightsData
    return \
    IfcMakeArrayOfArray(weightsdata,0,uupper,0,vupper)




class IfcRectangleHollowProfileDef_ValidWallThickness:
    SCOPE = "entity"
    TYPE_NAME = "IfcRectangleHollowProfileDef"
    RULE_NAME = "ValidWallThickness"

    @staticmethod    
    def __call__(self):
        wallthickness = self.WallThickness
        
        assert ((wallthickness < (self.XDim / 2.)) and (wallthickness < (self.YDim / 2.))) is not False
        



class IfcRectangleHollowProfileDef_ValidInnerRadius:
    SCOPE = "entity"
    TYPE_NAME = "IfcRectangleHollowProfileDef"
    RULE_NAME = "ValidInnerRadius"

    @staticmethod    
    def __call__(self):
        wallthickness = self.WallThickness
        innerfilletradius = self.InnerFilletRadius
        
        assert ((not exists(innerfilletradius)) or ((innerfilletradius <= ((self.XDim / 2.) - wallthickness)) and (innerfilletradius <= ((self.YDim / 2.) - wallthickness)))) is not False
        



class IfcRectangleHollowProfileDef_ValidOuterRadius:
    SCOPE = "entity"
    TYPE_NAME = "IfcRectangleHollowProfileDef"
    RULE_NAME = "ValidOuterRadius"

    @staticmethod    
    def __call__(self):
        outerfilletradius = self.OuterFilletRadius
        
        assert ((not exists(outerfilletradius)) or ((outerfilletradius <= (self.XDim / 2.)) and (outerfilletradius <= (self.YDim / 2.)))) is not False
        










class IfcRectangularTrimmedSurface_U1AndU2Different:
    SCOPE = "entity"
    TYPE_NAME = "IfcRectangularTrimmedSurface"
    RULE_NAME = "U1AndU2Different"

    @staticmethod    
    def __call__(self):
        u1 = self.U1
        u2 = self.U2
        
        assert (u1 != u2) is not False
        



class IfcRectangularTrimmedSurface_V1AndV2Different:
    SCOPE = "entity"
    TYPE_NAME = "IfcRectangularTrimmedSurface"
    RULE_NAME = "V1AndV2Different"

    @staticmethod    
    def __call__(self):
        v1 = self.V1
        v2 = self.V2
        
        assert (v1 != v2) is not False
        



class IfcRectangularTrimmedSurface_UsenseCompatible:
    SCOPE = "entity"
    TYPE_NAME = "IfcRectangularTrimmedSurface"
    RULE_NAME = "UsenseCompatible"

    @staticmethod    
    def __call__(self):
        basissurface = self.BasisSurface
        u1 = self.U1
        u2 = self.U2
        usense = self.Usense
        
        assert ((('ifc4.ifcelementarysurface' in typeof(basissurface)) and (not 'ifc4.ifcplane' in typeof(basissurface))) or ('ifc4.ifcsurfaceofrevolution' in typeof(basissurface)) or (usense == (u2 > u1))) is not False
        



class IfcRectangularTrimmedSurface_VsenseCompatible:
    SCOPE = "entity"
    TYPE_NAME = "IfcRectangularTrimmedSurface"
    RULE_NAME = "VsenseCompatible"

    @staticmethod    
    def __call__(self):
        v1 = self.V1
        v2 = self.V2
        vsense = self.Vsense
        
        assert (vsense == (v2 > v1)) is not False
        



















class IfcReinforcingBar_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcReinforcingBar"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcReinforcingBarTypeEnum.USERDEFINED) or ((predefinedtype == IfcReinforcingBarTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcReinforcingBar_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcReinforcingBar"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcreinforcingbartype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcReinforcingBarType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcReinforcingBarType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcReinforcingBarTypeEnum.USERDEFINED) or ((predefinedtype == IfcReinforcingBarTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        



class IfcReinforcingBarType_BendingShapeCodeProvided:
    SCOPE = "entity"
    TYPE_NAME = "IfcReinforcingBarType"
    RULE_NAME = "BendingShapeCodeProvided"

    @staticmethod    
    def __call__(self):
        bendingshapecode = self.BendingShapeCode
        bendingparameters = self.BendingParameters
        
        assert ((not exists(bendingparameters)) or exists(bendingshapecode)) is not False
        










class IfcReinforcingMesh_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcReinforcingMesh"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcReinforcingMeshTypeEnum.USERDEFINED) or ((predefinedtype == IfcReinforcingMeshTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcReinforcingMesh_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcReinforcingMesh"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcreinforcingmeshtype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcReinforcingMeshType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcReinforcingMeshType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcReinforcingMeshTypeEnum.USERDEFINED) or ((predefinedtype == IfcReinforcingMeshTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        



class IfcReinforcingMeshType_BendingShapeCodeProvided:
    SCOPE = "entity"
    TYPE_NAME = "IfcReinforcingMeshType"
    RULE_NAME = "BendingShapeCodeProvided"

    @staticmethod    
    def __call__(self):
        bendingshapecode = self.BendingShapeCode
        bendingparameters = self.BendingParameters
        
        assert ((not exists(bendingparameters)) or exists(bendingshapecode)) is not False
        




class IfcRelAggregates_NoSelfReference:
    SCOPE = "entity"
    TYPE_NAME = "IfcRelAggregates"
    RULE_NAME = "NoSelfReference"

    @staticmethod    
    def __call__(self):
        relatingobject = self.RelatingObject
        relatedobjects = self.RelatedObjects
        
        assert ((sizeof([temp for temp in relatedobjects if relatingobject == temp])) == 0) is not False
        




class IfcRelAssigns_WR1:
    SCOPE = "entity"
    TYPE_NAME = "IfcRelAssigns"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):
        relatedobjects = self.RelatedObjects
        relatedobjectstype = self.RelatedObjectsType
        
        assert (IfcCorrectObjectAssignment(relatedobjectstype,relatedobjects)) is not False
        




class IfcRelAssignsToActor_NoSelfReference:
    SCOPE = "entity"
    TYPE_NAME = "IfcRelAssignsToActor"
    RULE_NAME = "NoSelfReference"

    @staticmethod    
    def __call__(self):
        relatingactor = self.RelatingActor
        
        assert ((sizeof([temp for temp in self.RelatedObjects if relatingactor == temp])) == 0) is not False
        




class IfcRelAssignsToControl_NoSelfReference:
    SCOPE = "entity"
    TYPE_NAME = "IfcRelAssignsToControl"
    RULE_NAME = "NoSelfReference"

    @staticmethod    
    def __call__(self):
        relatingcontrol = self.RelatingControl
        
        assert ((sizeof([temp for temp in self.RelatedObjects if relatingcontrol == temp])) == 0) is not False
        




class IfcRelAssignsToGroup_NoSelfReference:
    SCOPE = "entity"
    TYPE_NAME = "IfcRelAssignsToGroup"
    RULE_NAME = "NoSelfReference"

    @staticmethod    
    def __call__(self):
        relatinggroup = self.RelatingGroup
        
        assert ((sizeof([temp for temp in self.RelatedObjects if relatinggroup == temp])) == 0) is not False
        







class IfcRelAssignsToProcess_NoSelfReference:
    SCOPE = "entity"
    TYPE_NAME = "IfcRelAssignsToProcess"
    RULE_NAME = "NoSelfReference"

    @staticmethod    
    def __call__(self):
        relatingprocess = self.RelatingProcess
        
        assert ((sizeof([temp for temp in self.RelatedObjects if relatingprocess == temp])) == 0) is not False
        




class IfcRelAssignsToProduct_NoSelfReference:
    SCOPE = "entity"
    TYPE_NAME = "IfcRelAssignsToProduct"
    RULE_NAME = "NoSelfReference"

    @staticmethod    
    def __call__(self):
        relatingproduct = self.RelatingProduct
        
        assert ((sizeof([temp for temp in self.RelatedObjects if relatingproduct == temp])) == 0) is not False
        




class IfcRelAssignsToResource_NoSelfReference:
    SCOPE = "entity"
    TYPE_NAME = "IfcRelAssignsToResource"
    RULE_NAME = "NoSelfReference"

    @staticmethod    
    def __call__(self):
        relatingresource = self.RelatingResource
        
        assert ((sizeof([temp for temp in self.RelatedObjects if relatingresource == temp])) == 0) is not False
        






















class IfcRelAssociatesMaterial_NoVoidElement:
    SCOPE = "entity"
    TYPE_NAME = "IfcRelAssociatesMaterial"
    RULE_NAME = "NoVoidElement"

    @staticmethod    
    def __call__(self):

        
        assert ((sizeof([temp for temp in self.RelatedObjects if ('ifc4.ifcfeatureelementsubtraction' in typeof(temp)) or ('ifc4.ifcvirtualelement' in typeof(temp))])) == 0) is not False
        



class IfcRelAssociatesMaterial_AllowedElements:
    SCOPE = "entity"
    TYPE_NAME = "IfcRelAssociatesMaterial"
    RULE_NAME = "AllowedElements"

    @staticmethod    
    def __call__(self):

        
        assert ((sizeof([temp for temp in self.RelatedObjects if (sizeof(typeof(temp) * ['ifc4.ifcelement','ifc4.ifcelementtype','ifc4.ifcwindowstyle','ifc4.ifcdoorstyle','ifc4.ifcstructuralmember','ifc4.ifcport'])) == 0])) == 0) is not False
        







class IfcRelConnectsElements_NoSelfReference:
    SCOPE = "entity"
    TYPE_NAME = "IfcRelConnectsElements"
    RULE_NAME = "NoSelfReference"

    @staticmethod    
    def __call__(self):
        relatingelement = self.RelatingElement
        relatedelement = self.RelatedElement
        
        assert (relatingelement != relatedelement) is not False
        




class IfcRelConnectsPathElements_NormalizedRelatingPriorities:
    SCOPE = "entity"
    TYPE_NAME = "IfcRelConnectsPathElements"
    RULE_NAME = "NormalizedRelatingPriorities"

    @staticmethod    
    def __call__(self):
        relatingpriorities = self.RelatingPriorities
        
        assert ((sizeof(relatingpriorities) == 0) or ((sizeof([temp for temp in relatingpriorities if 0 <= temp <= 100])) == sizeof(relatingpriorities))) is not False
        



class IfcRelConnectsPathElements_NormalizedRelatedPriorities:
    SCOPE = "entity"
    TYPE_NAME = "IfcRelConnectsPathElements"
    RULE_NAME = "NormalizedRelatedPriorities"

    @staticmethod    
    def __call__(self):
        relatedpriorities = self.RelatedPriorities
        
        assert ((sizeof(relatedpriorities) == 0) or ((sizeof([temp for temp in relatedpriorities if 0 <= temp <= 100])) == sizeof(relatedpriorities))) is not False
        







class IfcRelConnectsPorts_NoSelfReference:
    SCOPE = "entity"
    TYPE_NAME = "IfcRelConnectsPorts"
    RULE_NAME = "NoSelfReference"

    @staticmethod    
    def __call__(self):
        relatingport = self.RelatingPort
        relatedport = self.RelatedPort
        
        assert (relatingport != relatedport) is not False
        
















class IfcRelContainedInSpatialStructure_WR31:
    SCOPE = "entity"
    TYPE_NAME = "IfcRelContainedInSpatialStructure"
    RULE_NAME = "WR31"

    @staticmethod    
    def __call__(self):
        relatedelements = self.RelatedElements
        
        assert ((sizeof([temp for temp in relatedelements if 'ifc4.ifcspatialstructureelement' in typeof(temp)])) == 0) is not False
        










class IfcRelDeclares_NoSelfReference:
    SCOPE = "entity"
    TYPE_NAME = "IfcRelDeclares"
    RULE_NAME = "NoSelfReference"

    @staticmethod    
    def __call__(self):
        relatingcontext = self.RelatingContext
        relateddefinitions = self.RelatedDefinitions
        
        assert ((sizeof([temp for temp in relateddefinitions if relatingcontext == temp])) == 0) is not False
        













class IfcRelDefinesByProperties_NoRelatedTypeObject:
    SCOPE = "entity"
    TYPE_NAME = "IfcRelDefinesByProperties"
    RULE_NAME = "NoRelatedTypeObject"

    @staticmethod    
    def __call__(self):

        
        assert ((sizeof([types for types in self.RelatedObjects if 'ifc4.ifctypeobject' in typeof(types)])) == 0) is not False
        
















class IfcRelInterferesElements_NotSelfReference:
    SCOPE = "entity"
    TYPE_NAME = "IfcRelInterferesElements"
    RULE_NAME = "NotSelfReference"

    @staticmethod    
    def __call__(self):
        relatingelement = self.RelatingElement
        relatedelement = self.RelatedElement
        
        assert (relatingelement != relatedelement) is not False
        




class IfcRelNests_NoSelfReference:
    SCOPE = "entity"
    TYPE_NAME = "IfcRelNests"
    RULE_NAME = "NoSelfReference"

    @staticmethod    
    def __call__(self):
        relatingobject = self.RelatingObject
        relatedobjects = self.RelatedObjects
        
        assert ((sizeof([temp for temp in relatedobjects if relatingobject == temp])) == 0) is not False
        







class IfcRelReferencedInSpatialStructure_AllowedRelatedElements:
    SCOPE = "entity"
    TYPE_NAME = "IfcRelReferencedInSpatialStructure"
    RULE_NAME = "AllowedRelatedElements"

    @staticmethod    
    def __call__(self):
        relatedelements = self.RelatedElements
        
        assert ((sizeof([temp for temp in relatedelements if ('ifc4.ifcspatialstructureelement' in typeof(temp)) and (not 'ifc4.ifcspace' in typeof(temp))])) == 0) is not False
        




class IfcRelSequence_AvoidInconsistentSequence:
    SCOPE = "entity"
    TYPE_NAME = "IfcRelSequence"
    RULE_NAME = "AvoidInconsistentSequence"

    @staticmethod    
    def __call__(self):
        relatingprocess = self.RelatingProcess
        relatedprocess = self.RelatedProcess
        
        assert (relatingprocess != relatedprocess) is not False
        



class IfcRelSequence_CorrectSequenceType:
    SCOPE = "entity"
    TYPE_NAME = "IfcRelSequence"
    RULE_NAME = "CorrectSequenceType"

    @staticmethod    
    def __call__(self):
        sequencetype = self.SequenceType
        userdefinedsequencetype = self.UserDefinedSequenceType
        
        assert ((sequencetype != IfcSequenceEnum.USERDEFINED) or ((sequencetype == IfcSequenceEnum.USERDEFINED) and exists(userdefinedsequencetype))) is not False
        







class IfcRelSpaceBoundary_CorrectPhysOrVirt:
    SCOPE = "entity"
    TYPE_NAME = "IfcRelSpaceBoundary"
    RULE_NAME = "CorrectPhysOrVirt"

    @staticmethod    
    def __call__(self):
        relatedbuildingelement = self.RelatedBuildingElement
        physicalorvirtualboundary = self.PhysicalOrVirtualBoundary
        
        assert (((physicalorvirtualboundary == IfcPhysicalOrVirtualEnum.Physical) and (not 'ifc4.ifcvirtualelement' in typeof(relatedbuildingelement))) or ((physicalorvirtualboundary == IfcPhysicalOrVirtualEnum.Virtual) and (('ifc4.ifcvirtualelement' in typeof(relatedbuildingelement)) or ('ifc4.ifcopeningelement' in typeof(relatedbuildingelement)))) or (physicalorvirtualboundary == IfcPhysicalOrVirtualEnum.NotDefined)) is not False
        
















class IfcReparametrisedCompositeCurveSegment_PositiveLengthParameter:
    SCOPE = "entity"
    TYPE_NAME = "IfcReparametrisedCompositeCurveSegment"
    RULE_NAME = "PositiveLengthParameter"

    @staticmethod    
    def __call__(self):
        paramlength = self.ParamLength
        
        assert (paramlength > 0.0) is not False
        













class IfcRepresentationMap_ApplicableMappedRepr:
    SCOPE = "entity"
    TYPE_NAME = "IfcRepresentationMap"
    RULE_NAME = "ApplicableMappedRepr"

    @staticmethod    
    def __call__(self):
        mappedrepresentation = self.MappedRepresentation
        
        assert ('ifc4.ifcshapemodel' in typeof(mappedrepresentation)) is not False
        



















class IfcRevolvedAreaSolid_AxisStartInXY:
    SCOPE = "entity"
    TYPE_NAME = "IfcRevolvedAreaSolid"
    RULE_NAME = "AxisStartInXY"

    @staticmethod    
    def __call__(self):
        axis = self.Axis
        
        assert ((axis.Location.Coordinates[3 - 1]) == 0.0) is not False
        



class IfcRevolvedAreaSolid_AxisDirectionInXY:
    SCOPE = "entity"
    TYPE_NAME = "IfcRevolvedAreaSolid"
    RULE_NAME = "AxisDirectionInXY"

    @staticmethod    
    def __call__(self):
        axis = self.Axis
        
        assert ((axis.Z.DirectionRatios[3 - 1]) == 0.0) is not False
        



def calc_IfcRevolvedAreaSolid_AxisLine(self):
    axis = self.Axis
    return \
    IfcLine(Pnt=axis.Location, Dir=IfcVector(Orientation=axis.Z, Magnitude=1.0))




class IfcRevolvedAreaSolidTapered_CorrectProfileAssignment:
    SCOPE = "entity"
    TYPE_NAME = "IfcRevolvedAreaSolidTapered"
    RULE_NAME = "CorrectProfileAssignment"

    @staticmethod    
    def __call__(self):

        
        assert (IfcTaperedSweptAreaProfiles(self.SweptArea,self.EndSweptArea)) is not False
        










class IfcRoof_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcRoof"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcRoofTypeEnum.USERDEFINED) or ((predefinedtype == IfcRoofTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcRoof_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcRoof"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcrooftype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcRoofType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcRoofType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcRoofTypeEnum.USERDEFINED) or ((predefinedtype == IfcRoofTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        







class IfcRoundedRectangleProfileDef_ValidRadius:
    SCOPE = "entity"
    TYPE_NAME = "IfcRoundedRectangleProfileDef"
    RULE_NAME = "ValidRadius"

    @staticmethod    
    def __call__(self):
        roundingradius = self.RoundingRadius
        
        assert ((roundingradius <= (self.XDim / 2.)) and (roundingradius <= (self.YDim / 2.))) is not False
        




def calc_IfcSIUnit_Dimensions(self):

    return \
    IfcDimensionsForSiUnit(self.Name)




class IfcSanitaryTerminal_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcSanitaryTerminal"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcSanitaryTerminalTypeEnum.USERDEFINED) or ((predefinedtype == IfcSanitaryTerminalTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcSanitaryTerminal_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcSanitaryTerminal"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcsanitaryterminaltype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcSanitaryTerminalType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcSanitaryTerminalType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcSanitaryTerminalTypeEnum.USERDEFINED) or ((predefinedtype == IfcSanitaryTerminalTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        







class IfcSeamCurve_TwoPCurves:
    SCOPE = "entity"
    TYPE_NAME = "IfcSeamCurve"
    RULE_NAME = "TwoPCurves"

    @staticmethod    
    def __call__(self):

        
        assert (sizeof(self.AssociatedGeometry) == 2) is not False
        



class IfcSeamCurve_SameSurface:
    SCOPE = "entity"
    TYPE_NAME = "IfcSeamCurve"
    RULE_NAME = "SameSurface"

    @staticmethod    
    def __call__(self):

        
        assert ((IfcAssociatedSurface(self.AssociatedGeometry[1 - 1])) == (IfcAssociatedSurface(self.AssociatedGeometry[2 - 1]))) is not False
        










class IfcSectionedSpine_CorrespondingSectionPositions:
    SCOPE = "entity"
    TYPE_NAME = "IfcSectionedSpine"
    RULE_NAME = "CorrespondingSectionPositions"

    @staticmethod    
    def __call__(self):
        crosssections = self.CrossSections
        crosssectionpositions = self.CrossSectionPositions
        
        assert (sizeof(crosssections) == sizeof(crosssectionpositions)) is not False
        



class IfcSectionedSpine_ConsistentProfileTypes:
    SCOPE = "entity"
    TYPE_NAME = "IfcSectionedSpine"
    RULE_NAME = "ConsistentProfileTypes"

    @staticmethod    
    def __call__(self):
        crosssections = self.CrossSections
        
        assert ((sizeof([temp for temp in crosssections if (crosssections[1 - 1].ProfileType) != temp.ProfileType])) == 0) is not False
        



class IfcSectionedSpine_SpineCurveDim:
    SCOPE = "entity"
    TYPE_NAME = "IfcSectionedSpine"
    RULE_NAME = "SpineCurveDim"

    @staticmethod    
    def __call__(self):
        spinecurve = self.SpineCurve
        
        assert (spinecurve.Dim == 3) is not False
        



def calc_IfcSectionedSpine_Dim(self):

    return \
    3




class IfcSensor_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcSensor"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcSensorTypeEnum.USERDEFINED) or ((predefinedtype == IfcSensorTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcSensor_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcSensor"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcsensortype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcSensorType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcSensorType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcSensorTypeEnum.USERDEFINED) or ((predefinedtype == IfcSensorTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcShadingDevice_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcShadingDevice"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcShadingDeviceTypeEnum.USERDEFINED) or ((predefinedtype == IfcShadingDeviceTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcShadingDevice_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcShadingDevice"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcshadingdevicetype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcShadingDeviceType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcShadingDeviceType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcShadingDeviceTypeEnum.USERDEFINED) or ((predefinedtype == IfcShadingDeviceTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        







class IfcShapeModel_WR11:
    SCOPE = "entity"
    TYPE_NAME = "IfcShapeModel"
    RULE_NAME = "WR11"

    @staticmethod    
    def __call__(self):
        ofshapeaspect = self.OfShapeAspect
        
        assert ((sizeof(self.OfProductRepresentation) == 1) ^ (sizeof(self.RepresentationMap) == 1) ^ (sizeof(ofshapeaspect) == 1)) is not False
        




class IfcShapeRepresentation_CorrectContext:
    SCOPE = "entity"
    TYPE_NAME = "IfcShapeRepresentation"
    RULE_NAME = "CorrectContext"

    @staticmethod    
    def __call__(self):

        
        assert ('ifc4.ifcgeometricrepresentationcontext' in typeof(self.ContextOfItems)) is not False
        



class IfcShapeRepresentation_NoTopologicalItem:
    SCOPE = "entity"
    TYPE_NAME = "IfcShapeRepresentation"
    RULE_NAME = "NoTopologicalItem"

    @staticmethod    
    def __call__(self):
        items = self.Items
        
        assert ((sizeof([temp for temp in items if ('ifc4.ifctopologicalrepresentationitem' in typeof(temp)) and (not (sizeof(['ifc4.ifcvertexpoint','ifc4.ifcedgecurve','ifc4.ifcfacesurface'] * typeof(temp))) == 1)])) == 0) is not False
        



class IfcShapeRepresentation_HasRepresentationType:
    SCOPE = "entity"
    TYPE_NAME = "IfcShapeRepresentation"
    RULE_NAME = "HasRepresentationType"

    @staticmethod    
    def __call__(self):

        
        assert (exists(self.RepresentationType)) is not False
        



class IfcShapeRepresentation_HasRepresentationIdentifier:
    SCOPE = "entity"
    TYPE_NAME = "IfcShapeRepresentation"
    RULE_NAME = "HasRepresentationIdentifier"

    @staticmethod    
    def __call__(self):

        
        assert (exists(self.RepresentationIdentifier)) is not False
        



class IfcShapeRepresentation_CorrectItemsForType:
    SCOPE = "entity"
    TYPE_NAME = "IfcShapeRepresentation"
    RULE_NAME = "CorrectItemsForType"

    @staticmethod    
    def __call__(self):

        
        assert (IfcShapeRepresentationTypes(self.RepresentationType,self.Items)) is not False
        




def calc_IfcShellBasedSurfaceModel_Dim(self):

    return \
    3













class IfcSlab_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcSlab"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcSlabTypeEnum.USERDEFINED) or ((predefinedtype == IfcSlabTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcSlab_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcSlab"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcslabtype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcSlabElementedCase_HasDecomposition:
    SCOPE = "entity"
    TYPE_NAME = "IfcSlabElementedCase"
    RULE_NAME = "HasDecomposition"

    @staticmethod    
    def __call__(self):

        
        assert (hiindex(self.IsDecomposedBy) > 0) is not False
        




class IfcSlabStandardCase_HasMaterialLayerSetusage:
    SCOPE = "entity"
    TYPE_NAME = "IfcSlabStandardCase"
    RULE_NAME = "HasMaterialLayerSetusage"

    @staticmethod    
    def __call__(self):

        
        assert ((sizeof([temp for temp in usedin(self,'ifc4.ifcrelassociates.relatedobjects') if ('ifc4.ifcrelassociatesmaterial' in typeof(temp)) and ('ifc4.ifcmateriallayersetusage' in typeof(temp.RelatingMaterial))])) == 1) is not False
        




class IfcSlabType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcSlabType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcSlabTypeEnum.USERDEFINED) or ((predefinedtype == IfcSlabTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        







class IfcSolarDevice_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcSolarDevice"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcSolarDeviceTypeEnum.USERDEFINED) or ((predefinedtype == IfcSolarDeviceTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcSolarDevice_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcSolarDevice"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcsolardevicetype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcSolarDeviceType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcSolarDeviceType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcSolarDeviceTypeEnum.USERDEFINED) or ((predefinedtype == IfcSolarDeviceTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




def calc_IfcSolidModel_Dim(self):

    return \
    3




class IfcSpace_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcSpace"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcSpaceTypeEnum.USERDEFINED) or ((predefinedtype == IfcSpaceTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcSpace_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcSpace"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcspacetype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcSpaceHeater_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcSpaceHeater"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcSpaceHeaterTypeEnum.USERDEFINED) or ((predefinedtype == IfcSpaceHeaterTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcSpaceHeater_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcSpaceHeater"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcspaceheatertype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcSpaceHeaterType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcSpaceHeaterType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcSpaceHeaterTypeEnum.USERDEFINED) or ((predefinedtype == IfcSpaceHeaterTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcSpaceType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcSpaceType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcSpaceTypeEnum.USERDEFINED) or ((predefinedtype == IfcSpaceTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        










class IfcSpatialStructureElement_WR41:
    SCOPE = "entity"
    TYPE_NAME = "IfcSpatialStructureElement"
    RULE_NAME = "WR41"

    @staticmethod    
    def __call__(self):

        
        assert ((hiindex(self.Decomposes) == 1) and ('ifc4.ifcrelaggregates' in (typeof(self.Decomposes[1 - 1]))) and (('ifc4.ifcproject' in (typeof(self.Decomposes[1 - 1].RelatingObject))) or ('ifc4.ifcspatialstructureelement' in (typeof(self.Decomposes[1 - 1].RelatingObject))))) is not False
        







class IfcSpatialZone_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcSpatialZone"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcSpatialZoneTypeEnum.USERDEFINED) or ((predefinedtype == IfcSpatialZoneTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcSpatialZone_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcSpatialZone"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcspatialzonetype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcSpatialZoneType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcSpatialZoneType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcSpatialZoneTypeEnum.USERDEFINED) or ((predefinedtype == IfcSpatialZoneTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        










class IfcStackTerminal_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcStackTerminal"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcStackTerminalTypeEnum.USERDEFINED) or ((predefinedtype == IfcStackTerminalTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcStackTerminal_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcStackTerminal"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcstackterminaltype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcStackTerminalType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcStackTerminalType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcStackTerminalTypeEnum.USERDEFINED) or ((predefinedtype == IfcStackTerminalTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcStair_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcStair"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcStairTypeEnum.USERDEFINED) or ((predefinedtype == IfcStairTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcStair_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcStair"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcstairtype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcStairFlight_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcStairFlight"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcStairFlightTypeEnum.USERDEFINED) or ((predefinedtype == IfcStairFlightTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcStairFlight_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcStairFlight"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcstairflighttype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcStairFlightType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcStairFlightType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcStairFlightTypeEnum.USERDEFINED) or ((predefinedtype == IfcStairFlightTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcStairType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcStairType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcStairTypeEnum.USERDEFINED) or ((predefinedtype == IfcStairTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        










class IfcStructuralAnalysisModel_HasObjectType:
    SCOPE = "entity"
    TYPE_NAME = "IfcStructuralAnalysisModel"
    RULE_NAME = "HasObjectType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcAnalysisModelTypeEnum.USERDEFINED) or exists(self.ObjectType)) is not False
        










class IfcStructuralCurveAction_ProjectedIsGlobal:
    SCOPE = "entity"
    TYPE_NAME = "IfcStructuralCurveAction"
    RULE_NAME = "ProjectedIsGlobal"

    @staticmethod    
    def __call__(self):
        projectedortrue = self.ProjectedOrTrue
        
        assert ((not exists(projectedortrue)) or ((projectedortrue != projected_length) or (self.GlobalOrLocal == global_coords))) is not False
        



class IfcStructuralCurveAction_HasObjectType:
    SCOPE = "entity"
    TYPE_NAME = "IfcStructuralCurveAction"
    RULE_NAME = "HasObjectType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcStructuralCurveActivityTypeEnum.USERDEFINED) or exists(self.ObjectType)) is not False
        



class IfcStructuralCurveAction_SuitablePredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcStructuralCurveAction"
    RULE_NAME = "SuitablePredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert (predefinedtype != IfcStructuralCurveActivityTypeEnum.EQUIDISTANT) is not False
        







class IfcStructuralCurveMember_HasObjectType:
    SCOPE = "entity"
    TYPE_NAME = "IfcStructuralCurveMember"
    RULE_NAME = "HasObjectType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcStructuralCurveMemberTypeEnum.USERDEFINED) or exists(self.ObjectType)) is not False
        







class IfcStructuralCurveReaction_HasObjectType:
    SCOPE = "entity"
    TYPE_NAME = "IfcStructuralCurveReaction"
    RULE_NAME = "HasObjectType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcStructuralCurveActivityTypeEnum.USERDEFINED) or exists(self.ObjectType)) is not False
        



class IfcStructuralCurveReaction_SuitablePredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcStructuralCurveReaction"
    RULE_NAME = "SuitablePredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcStructuralCurveActivityTypeEnum.SINUS) and (predefinedtype != IfcStructuralCurveActivityTypeEnum.PARABOLA)) is not False
        







class IfcStructuralLinearAction_SuitableLoadType:
    SCOPE = "entity"
    TYPE_NAME = "IfcStructuralLinearAction"
    RULE_NAME = "SuitableLoadType"

    @staticmethod    
    def __call__(self):

        
        assert ((sizeof(['ifc4.ifcstructuralloadlinearforce','ifc4.ifcstructuralloadtemperature'] * typeof(self.AppliedLoad))) == 1) is not False
        



class IfcStructuralLinearAction_ConstPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcStructuralLinearAction"
    RULE_NAME = "ConstPredefinedType"

    @staticmethod    
    def __call__(self):

        
        assert (self.PredefinedType == IfcStructuralCurveActivityTypeEnum.CONST) is not False
        







class IfcStructuralLoadCase_IsLoadCasePredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcStructuralLoadCase"
    RULE_NAME = "IsLoadCasePredefinedType"

    @staticmethod    
    def __call__(self):

        
        assert (self.PredefinedType == IfcLoadGroupTypeEnum.LOAD_CASE) is not False
        




class IfcStructuralLoadConfiguration_ValidListSize:
    SCOPE = "entity"
    TYPE_NAME = "IfcStructuralLoadConfiguration"
    RULE_NAME = "ValidListSize"

    @staticmethod    
    def __call__(self):
        values = self.Values
        locations = self.Locations
        
        assert ((not exists(locations)) or (sizeof(locations) == sizeof(values))) is not False
        




class IfcStructuralLoadGroup_HasObjectType:
    SCOPE = "entity"
    TYPE_NAME = "IfcStructuralLoadGroup"
    RULE_NAME = "HasObjectType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        actiontype = self.ActionType
        actionsource = self.ActionSource
        
        assert (((predefinedtype != IfcLoadGroupTypeEnum.USERDEFINED) and (actiontype != IfcActionTypeEnum.USERDEFINED) and (actionsource != IfcActionSourceTypeEnum.USERDEFINED)) or exists(self.ObjectType)) is not False
        


































class IfcStructuralPlanarAction_SuitableLoadType:
    SCOPE = "entity"
    TYPE_NAME = "IfcStructuralPlanarAction"
    RULE_NAME = "SuitableLoadType"

    @staticmethod    
    def __call__(self):

        
        assert ((sizeof(['ifc4.ifcstructuralloadplanarforce','ifc4.ifcstructuralloadtemperature'] * typeof(self.AppliedLoad))) == 1) is not False
        



class IfcStructuralPlanarAction_ConstPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcStructuralPlanarAction"
    RULE_NAME = "ConstPredefinedType"

    @staticmethod    
    def __call__(self):

        
        assert (self.PredefinedType == IfcStructuralSurfaceActivityTypeEnum.CONST) is not False
        




class IfcStructuralPointAction_SuitableLoadType:
    SCOPE = "entity"
    TYPE_NAME = "IfcStructuralPointAction"
    RULE_NAME = "SuitableLoadType"

    @staticmethod    
    def __call__(self):

        
        assert ((sizeof(['ifc4.ifcstructuralloadsingleforce','ifc4.ifcstructuralloadsingledisplacement'] * typeof(self.AppliedLoad))) == 1) is not False
        







class IfcStructuralPointReaction_SuitableLoadType:
    SCOPE = "entity"
    TYPE_NAME = "IfcStructuralPointReaction"
    RULE_NAME = "SuitableLoadType"

    @staticmethod    
    def __call__(self):

        
        assert ((sizeof(['ifc4.ifcstructuralloadsingleforce','ifc4.ifcstructuralloadsingledisplacement'] * typeof(self.AppliedLoad))) == 1) is not False
        







class IfcStructuralResultGroup_HasObjectType:
    SCOPE = "entity"
    TYPE_NAME = "IfcStructuralResultGroup"
    RULE_NAME = "HasObjectType"

    @staticmethod    
    def __call__(self):
        theorytype = self.TheoryType
        
        assert ((theorytype != IfcAnalysisTheoryTypeEnum.USERDEFINED) or exists(self.ObjectType)) is not False
        




class IfcStructuralSurfaceAction_ProjectedIsGlobal:
    SCOPE = "entity"
    TYPE_NAME = "IfcStructuralSurfaceAction"
    RULE_NAME = "ProjectedIsGlobal"

    @staticmethod    
    def __call__(self):
        projectedortrue = self.ProjectedOrTrue
        
        assert ((not exists(projectedortrue)) or ((projectedortrue != projected_length) or (self.GlobalOrLocal == global_coords))) is not False
        



class IfcStructuralSurfaceAction_HasObjectType:
    SCOPE = "entity"
    TYPE_NAME = "IfcStructuralSurfaceAction"
    RULE_NAME = "HasObjectType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcStructuralSurfaceActivityTypeEnum.USERDEFINED) or exists(self.ObjectType)) is not False
        







class IfcStructuralSurfaceMember_HasObjectType:
    SCOPE = "entity"
    TYPE_NAME = "IfcStructuralSurfaceMember"
    RULE_NAME = "HasObjectType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcStructuralSurfaceMemberTypeEnum.USERDEFINED) or exists(self.ObjectType)) is not False
        







class IfcStructuralSurfaceReaction_HasPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcStructuralSurfaceReaction"
    RULE_NAME = "HasPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcStructuralSurfaceActivityTypeEnum.USERDEFINED) or exists(self.ObjectType)) is not False
        







class IfcStyledItem_ApplicableItem:
    SCOPE = "entity"
    TYPE_NAME = "IfcStyledItem"
    RULE_NAME = "ApplicableItem"

    @staticmethod    
    def __call__(self):
        item = self.Item
        
        assert (not 'ifc4.ifcstyleditem' in typeof(item)) is not False
        




class IfcStyledRepresentation_OnlyStyledItems:
    SCOPE = "entity"
    TYPE_NAME = "IfcStyledRepresentation"
    RULE_NAME = "OnlyStyledItems"

    @staticmethod    
    def __call__(self):

        
        assert ((sizeof([temp for temp in self.Items if not 'ifc4.ifcstyleditem' in typeof(temp)])) == 0) is not False
        




class IfcSubContractResource_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcSubContractResource"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcSubContractResourceTypeEnum.USERDEFINED) or ((predefinedtype == IfcSubContractResourceTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        




class IfcSubContractResourceType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcSubContractResourceType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcSubContractResourceTypeEnum.USERDEFINED) or ((predefinedtype == IfcSubContractResourceTypeEnum.USERDEFINED) and exists(self.ResourceType))) is not False
        







def calc_IfcSurface_Dim(self):

    return \
    3




class IfcSurfaceCurve_CurveIs3D:
    SCOPE = "entity"
    TYPE_NAME = "IfcSurfaceCurve"
    RULE_NAME = "CurveIs3D"

    @staticmethod    
    def __call__(self):
        curve3d = self.Curve3D
        
        assert (curve3d.Dim == 3) is not False
        



class IfcSurfaceCurve_CurveIsNotPcurve:
    SCOPE = "entity"
    TYPE_NAME = "IfcSurfaceCurve"
    RULE_NAME = "CurveIsNotPcurve"

    @staticmethod    
    def __call__(self):
        curve3d = self.Curve3D
        
        assert (not 'ifc4.ifcpcurve' in typeof(curve3d)) is not False
        



def calc_IfcSurfaceCurve_BasisSurface(self):

    return \
    IfcGetBasisSurface(self)




class IfcSurfaceCurveSweptAreaSolid_DirectrixBounded:
    SCOPE = "entity"
    TYPE_NAME = "IfcSurfaceCurveSweptAreaSolid"
    RULE_NAME = "DirectrixBounded"

    @staticmethod    
    def __call__(self):
        directrix = self.Directrix
        startparam = self.StartParam
        endparam = self.EndParam
        
        assert ((exists(startparam) and exists(endparam)) or ((sizeof(['ifc4.ifcconic','ifc4.ifcboundedcurve'] * typeof(directrix))) == 1)) is not False
        




class IfcSurfaceFeature_HasObjectType:
    SCOPE = "entity"
    TYPE_NAME = "IfcSurfaceFeature"
    RULE_NAME = "HasObjectType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcSurfaceFeatureTypeEnum.USERDEFINED) or exists(self.ObjectType)) is not False
        




class IfcSurfaceOfLinearExtrusion_DepthGreaterZero:
    SCOPE = "entity"
    TYPE_NAME = "IfcSurfaceOfLinearExtrusion"
    RULE_NAME = "DepthGreaterZero"

    @staticmethod    
    def __call__(self):
        depth = self.Depth
        
        assert (depth > 0.) is not False
        



def calc_IfcSurfaceOfLinearExtrusion_ExtrusionAxis(self):
    extrudeddirection = self.ExtrudedDirection
    depth = self.Depth
    return \
    IfcVector(Orientation=extrudeddirection, Magnitude=depth)




def calc_IfcSurfaceOfRevolution_AxisLine(self):
    axisposition = self.AxisPosition
    return \
    IfcLine(Pnt=axisposition.Location, Dir=IfcVector(Orientation=axisposition.Z, Magnitude=1.0))




class IfcSurfaceReinforcementArea_SurfaceAndOrShearAreaSpecified:
    SCOPE = "entity"
    TYPE_NAME = "IfcSurfaceReinforcementArea"
    RULE_NAME = "SurfaceAndOrShearAreaSpecified"

    @staticmethod    
    def __call__(self):
        surfacereinforcement1 = self.SurfaceReinforcement1
        surfacereinforcement2 = self.SurfaceReinforcement2
        shearreinforcement = self.ShearReinforcement
        
        assert (exists(surfacereinforcement1) or exists(surfacereinforcement2) or exists(shearreinforcement)) is not False
        



class IfcSurfaceReinforcementArea_NonnegativeArea1:
    SCOPE = "entity"
    TYPE_NAME = "IfcSurfaceReinforcementArea"
    RULE_NAME = "NonnegativeArea1"

    @staticmethod    
    def __call__(self):
        surfacereinforcement1 = self.SurfaceReinforcement1
        
        assert ((not exists(surfacereinforcement1)) or (((surfacereinforcement1[1 - 1]) >= 0.) and ((surfacereinforcement1[2 - 1]) >= 0.) and ((sizeof(surfacereinforcement1) == 1) or ((surfacereinforcement1[1 - 1]) >= 0.)))) is not False
        



class IfcSurfaceReinforcementArea_NonnegativeArea2:
    SCOPE = "entity"
    TYPE_NAME = "IfcSurfaceReinforcementArea"
    RULE_NAME = "NonnegativeArea2"

    @staticmethod    
    def __call__(self):
        surfacereinforcement2 = self.SurfaceReinforcement2
        
        assert ((not exists(surfacereinforcement2)) or (((surfacereinforcement2[1 - 1]) >= 0.) and ((surfacereinforcement2[2 - 1]) >= 0.) and ((sizeof(surfacereinforcement2) == 1) or ((surfacereinforcement2[1 - 1]) >= 0.)))) is not False
        



class IfcSurfaceReinforcementArea_NonnegativeArea3:
    SCOPE = "entity"
    TYPE_NAME = "IfcSurfaceReinforcementArea"
    RULE_NAME = "NonnegativeArea3"

    @staticmethod    
    def __call__(self):
        shearreinforcement = self.ShearReinforcement
        
        assert ((not exists(shearreinforcement)) or (shearreinforcement >= 0.)) is not False
        




class IfcSurfaceStyle_MaxOneShading:
    SCOPE = "entity"
    TYPE_NAME = "IfcSurfaceStyle"
    RULE_NAME = "MaxOneShading"

    @staticmethod    
    def __call__(self):

        
        assert ((sizeof([style for style in self.Styles if 'ifc4.ifcsurfacestyleshading' in typeof(style)])) <= 1) is not False
        



class IfcSurfaceStyle_MaxOneLighting:
    SCOPE = "entity"
    TYPE_NAME = "IfcSurfaceStyle"
    RULE_NAME = "MaxOneLighting"

    @staticmethod    
    def __call__(self):

        
        assert ((sizeof([style for style in self.Styles if 'ifc4.ifcsurfacestylelighting' in typeof(style)])) <= 1) is not False
        



class IfcSurfaceStyle_MaxOneRefraction:
    SCOPE = "entity"
    TYPE_NAME = "IfcSurfaceStyle"
    RULE_NAME = "MaxOneRefraction"

    @staticmethod    
    def __call__(self):

        
        assert ((sizeof([style for style in self.Styles if 'ifc4.ifcsurfacestylerefraction' in typeof(style)])) <= 1) is not False
        



class IfcSurfaceStyle_MaxOneTextures:
    SCOPE = "entity"
    TYPE_NAME = "IfcSurfaceStyle"
    RULE_NAME = "MaxOneTextures"

    @staticmethod    
    def __call__(self):

        
        assert ((sizeof([style for style in self.Styles if 'ifc4.ifcsurfacestylewithtextures' in typeof(style)])) <= 1) is not False
        



class IfcSurfaceStyle_MaxOneExtDefined:
    SCOPE = "entity"
    TYPE_NAME = "IfcSurfaceStyle"
    RULE_NAME = "MaxOneExtDefined"

    @staticmethod    
    def __call__(self):

        
        assert ((sizeof([style for style in self.Styles if 'ifc4.ifcexternallydefinedsurfacestyle' in typeof(style)])) <= 1) is not False
        






















class IfcSweptAreaSolid_SweptAreaType:
    SCOPE = "entity"
    TYPE_NAME = "IfcSweptAreaSolid"
    RULE_NAME = "SweptAreaType"

    @staticmethod    
    def __call__(self):
        sweptarea = self.SweptArea
        
        assert (sweptarea.ProfileType == IfcProfileTypeEnum.Area) is not False
        




class IfcSweptDiskSolid_DirectrixDim:
    SCOPE = "entity"
    TYPE_NAME = "IfcSweptDiskSolid"
    RULE_NAME = "DirectrixDim"

    @staticmethod    
    def __call__(self):
        directrix = self.Directrix
        
        assert (directrix.Dim == 3) is not False
        



class IfcSweptDiskSolid_InnerRadiusSize:
    SCOPE = "entity"
    TYPE_NAME = "IfcSweptDiskSolid"
    RULE_NAME = "InnerRadiusSize"

    @staticmethod    
    def __call__(self):
        radius = self.Radius
        innerradius = self.InnerRadius
        
        assert ((not exists(innerradius)) or (radius > innerradius)) is not False
        



class IfcSweptDiskSolid_DirectrixBounded:
    SCOPE = "entity"
    TYPE_NAME = "IfcSweptDiskSolid"
    RULE_NAME = "DirectrixBounded"

    @staticmethod    
    def __call__(self):
        directrix = self.Directrix
        startparam = self.StartParam
        endparam = self.EndParam
        
        assert ((exists(startparam) and exists(endparam)) or ((sizeof(['ifc4.ifcconic','ifc4.ifcboundedcurve'] * typeof(directrix))) == 1)) is not False
        




class IfcSweptDiskSolidPolygonal_CorrectRadii:
    SCOPE = "entity"
    TYPE_NAME = "IfcSweptDiskSolidPolygonal"
    RULE_NAME = "CorrectRadii"

    @staticmethod    
    def __call__(self):
        filletradius = self.FilletRadius
        
        assert ((not exists(filletradius)) or (filletradius >= self.Radius)) is not False
        



class IfcSweptDiskSolidPolygonal_DirectrixIsPolyline:
    SCOPE = "entity"
    TYPE_NAME = "IfcSweptDiskSolidPolygonal"
    RULE_NAME = "DirectrixIsPolyline"

    @staticmethod    
    def __call__(self):

        
        assert (('ifc4.ifcpolyline' in typeof(self.Directrix)) or (('ifc4.ifcindexedpolycurve' in typeof(self.Directrix)) and (not exists(self.Directrix.Segments)))) is not False
        




class IfcSweptSurface_SweptCurveType:
    SCOPE = "entity"
    TYPE_NAME = "IfcSweptSurface"
    RULE_NAME = "SweptCurveType"

    @staticmethod    
    def __call__(self):
        sweptcurve = self.SweptCurve
        
        assert (sweptcurve.ProfileType == IfcProfileTypeEnum.Curve) is not False
        




class IfcSwitchingDevice_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcSwitchingDevice"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcSwitchingDeviceTypeEnum.USERDEFINED) or ((predefinedtype == IfcSwitchingDeviceTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcSwitchingDevice_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcSwitchingDevice"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcswitchingdevicetype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcSwitchingDeviceType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcSwitchingDeviceType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcSwitchingDeviceTypeEnum.USERDEFINED) or ((predefinedtype == IfcSwitchingDeviceTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        







class IfcSystemFurnitureElement_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcSystemFurnitureElement"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcSystemFurnitureElementTypeEnum.USERDEFINED) or ((predefinedtype == IfcSystemFurnitureElementTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcSystemFurnitureElement_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcSystemFurnitureElement"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcsystemfurnitureelementtype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcSystemFurnitureElementType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcSystemFurnitureElementType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcSystemFurnitureElementTypeEnum.USERDEFINED) or ((predefinedtype == IfcSystemFurnitureElementTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcTShapeProfileDef_ValidFlangeThickness:
    SCOPE = "entity"
    TYPE_NAME = "IfcTShapeProfileDef"
    RULE_NAME = "ValidFlangeThickness"

    @staticmethod    
    def __call__(self):
        depth = self.Depth
        flangethickness = self.FlangeThickness
        
        assert (flangethickness < depth) is not False
        



class IfcTShapeProfileDef_ValidWebThickness:
    SCOPE = "entity"
    TYPE_NAME = "IfcTShapeProfileDef"
    RULE_NAME = "ValidWebThickness"

    @staticmethod    
    def __call__(self):
        flangewidth = self.FlangeWidth
        webthickness = self.WebThickness
        
        assert (webthickness < flangewidth) is not False
        




class IfcTable_WR1:
    SCOPE = "entity"
    TYPE_NAME = "IfcTable"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):
        rows = self.Rows
        
        assert ((sizeof([temp for temp in rows if hiindex(temp.RowCells) != (hiindex(rows[1 - 1].RowCells))])) == 0) is not False
        



class IfcTable_WR2:
    SCOPE = "entity"
    TYPE_NAME = "IfcTable"
    RULE_NAME = "WR2"

    @staticmethod    
    def __call__(self):
        numberofheadings = self.NumberOfHeadings
        
        assert (0 <= numberofheadings <= 1) is not False
        



def calc_IfcTable_NumberOfCellsInRow(self):
    rows = self.Rows
    return \
    hiindex(rows[1 - 1].RowCells)



def calc_IfcTable_NumberOfHeadings(self):
    rows = self.Rows
    return \
    sizeof([temp for temp in rows if temp.IsHeading])



def calc_IfcTable_NumberOfDataRows(self):
    rows = self.Rows
    return \
    sizeof([temp for temp in rows if not temp.IsHeading])










class IfcTank_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcTank"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcTankTypeEnum.USERDEFINED) or ((predefinedtype == IfcTankTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcTank_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcTank"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifctanktype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcTankType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcTankType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcTankTypeEnum.USERDEFINED) or ((predefinedtype == IfcTankTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcTask_HasName:
    SCOPE = "entity"
    TYPE_NAME = "IfcTask"
    RULE_NAME = "HasName"

    @staticmethod    
    def __call__(self):

        
        assert (exists(self.Name)) is not False
        



class IfcTask_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcTask"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcTaskTypeEnum.USERDEFINED) or ((predefinedtype == IfcTaskTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        










class IfcTaskType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcTaskType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcTaskTypeEnum.USERDEFINED) or ((predefinedtype == IfcTaskTypeEnum.USERDEFINED) and exists(self.ProcessType))) is not False
        




class IfcTelecomAddress_MinimumDataProvided:
    SCOPE = "entity"
    TYPE_NAME = "IfcTelecomAddress"
    RULE_NAME = "MinimumDataProvided"

    @staticmethod    
    def __call__(self):
        telephonenumbers = self.TelephoneNumbers
        facsimilenumbers = self.FacsimileNumbers
        pagernumber = self.PagerNumber
        electronicmailaddresses = self.ElectronicMailAddresses
        wwwhomepageurl = self.WWWHomePageURL
        messagingids = self.MessagingIDs
        
        assert (exists(telephonenumbers) or exists(facsimilenumbers) or exists(pagernumber) or exists(electronicmailaddresses) or exists(wwwhomepageurl) or exists(messagingids)) is not False
        




class IfcTendon_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcTendon"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcTendonTypeEnum.USERDEFINED) or ((predefinedtype == IfcTendonTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcTendon_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcTendon"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifctendontype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcTendonAnchor_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcTendonAnchor"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcTendonAnchorTypeEnum.USERDEFINED) or ((predefinedtype == IfcTendonAnchorTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcTendonAnchor_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcTendonAnchor"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifctendonanchortype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcTendonAnchorType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcTendonAnchorType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcTendonAnchorTypeEnum.USERDEFINED) or ((predefinedtype == IfcTendonAnchorTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcTendonType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcTendonType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcTendonTypeEnum.USERDEFINED) or ((predefinedtype == IfcTendonTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




def calc_IfcTessellatedFaceSet_Dim(self):

    return \
    3










class IfcTextLiteralWithExtent_WR31:
    SCOPE = "entity"
    TYPE_NAME = "IfcTextLiteralWithExtent"
    RULE_NAME = "WR31"

    @staticmethod    
    def __call__(self):
        extent = self.Extent
        
        assert (not 'ifc4.ifcplanarbox' in typeof(extent)) is not False
        







class IfcTextStyleFontModel_MeasureOfFontSize:
    SCOPE = "entity"
    TYPE_NAME = "IfcTextStyleFontModel"
    RULE_NAME = "MeasureOfFontSize"

    @staticmethod    
    def __call__(self):

        
        assert (('ifc4.ifclengthmeasure' in typeof(self.FontSize)) and (self.FontSize > 0.)) is not False
        





































class IfcTopologyRepresentation_WR21:
    SCOPE = "entity"
    TYPE_NAME = "IfcTopologyRepresentation"
    RULE_NAME = "WR21"

    @staticmethod    
    def __call__(self):

        
        assert ((sizeof([temp for temp in self.Items if not 'ifc4.ifctopologicalrepresentationitem' in typeof(temp)])) == 0) is not False
        



class IfcTopologyRepresentation_WR22:
    SCOPE = "entity"
    TYPE_NAME = "IfcTopologyRepresentation"
    RULE_NAME = "WR22"

    @staticmethod    
    def __call__(self):

        
        assert (exists(self.RepresentationType)) is not False
        



class IfcTopologyRepresentation_WR23:
    SCOPE = "entity"
    TYPE_NAME = "IfcTopologyRepresentation"
    RULE_NAME = "WR23"

    @staticmethod    
    def __call__(self):

        
        assert (IfcTopologyRepresentationTypes(self.RepresentationType,self.Items)) is not False
        




class IfcToroidalSurface_MajorLargerMinor:
    SCOPE = "entity"
    TYPE_NAME = "IfcToroidalSurface"
    RULE_NAME = "MajorLargerMinor"

    @staticmethod    
    def __call__(self):
        majorradius = self.MajorRadius
        minorradius = self.MinorRadius
        
        assert (minorradius < majorradius) is not False
        




class IfcTransformer_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcTransformer"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcTransformerTypeEnum.USERDEFINED) or ((predefinedtype == IfcTransformerTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcTransformer_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcTransformer"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifctranformertype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcTransformerType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcTransformerType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcTransformerTypeEnum.USERDEFINED) or ((predefinedtype == IfcTransformerTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcTransportElement_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcTransportElement"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcTransportElementTypeEnum.USERDEFINED) or ((predefinedtype == IfcTransportElementTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcTransportElement_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcTransportElement"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifctransportelementtype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcTransportElementType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcTransportElementType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcTransportElementTypeEnum.USERDEFINED) or ((predefinedtype == IfcTransportElementTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        







def calc_IfcTriangulatedFaceSet_NumberOfTriangles(self):
    coordindex = self.CoordIndex
    return \
    sizeof(coordindex)




class IfcTrimmedCurve_Trim1ValuesConsistent:
    SCOPE = "entity"
    TYPE_NAME = "IfcTrimmedCurve"
    RULE_NAME = "Trim1ValuesConsistent"

    @staticmethod    
    def __call__(self):
        trim1 = self.Trim1
        
        assert ((hiindex(trim1) == 1) or ((typeof(trim1[1 - 1])) != (typeof(trim1[2 - 1])))) is not False
        



class IfcTrimmedCurve_Trim2ValuesConsistent:
    SCOPE = "entity"
    TYPE_NAME = "IfcTrimmedCurve"
    RULE_NAME = "Trim2ValuesConsistent"

    @staticmethod    
    def __call__(self):
        trim2 = self.Trim2
        
        assert ((hiindex(trim2) == 1) or ((typeof(trim2[1 - 1])) != (typeof(trim2[2 - 1])))) is not False
        



class IfcTrimmedCurve_NoTrimOfBoundedCurves:
    SCOPE = "entity"
    TYPE_NAME = "IfcTrimmedCurve"
    RULE_NAME = "NoTrimOfBoundedCurves"

    @staticmethod    
    def __call__(self):
        basiscurve = self.BasisCurve
        
        assert (not 'ifc4.ifcboundedcurve' in typeof(basiscurve)) is not False
        




class IfcTubeBundle_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcTubeBundle"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcTubeBundleTypeEnum.USERDEFINED) or ((predefinedtype == IfcTubeBundleTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcTubeBundle_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcTubeBundle"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifctubebundletype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcTubeBundleType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcTubeBundleType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcTubeBundleTypeEnum.USERDEFINED) or ((predefinedtype == IfcTubeBundleTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcTypeObject_NameRequired:
    SCOPE = "entity"
    TYPE_NAME = "IfcTypeObject"
    RULE_NAME = "NameRequired"

    @staticmethod    
    def __call__(self):

        
        assert (exists(self.Name)) is not False
        



class IfcTypeObject_UniquePropertySetNames:
    SCOPE = "entity"
    TYPE_NAME = "IfcTypeObject"
    RULE_NAME = "UniquePropertySetNames"

    @staticmethod    
    def __call__(self):
        haspropertysets = self.HasPropertySets
        
        assert ((not exists(haspropertysets)) or IfcUniquePropertySetNames(haspropertysets)) is not False
        







class IfcTypeProduct_ApplicableOccurrence:
    SCOPE = "entity"
    TYPE_NAME = "IfcTypeProduct"
    RULE_NAME = "ApplicableOccurrence"

    @staticmethod    
    def __call__(self):

        
        assert ((not exists(lambda: self.Types[1 - 1])) or ((sizeof([temp for temp in self.Types[1 - 1].RelatedObjects if not 'ifc4.ifcproduct' in typeof(temp)])) == 0)) is not False
        







class IfcUShapeProfileDef_ValidFlangeThickness:
    SCOPE = "entity"
    TYPE_NAME = "IfcUShapeProfileDef"
    RULE_NAME = "ValidFlangeThickness"

    @staticmethod    
    def __call__(self):
        depth = self.Depth
        flangethickness = self.FlangeThickness
        
        assert (flangethickness < (depth / 2.)) is not False
        



class IfcUShapeProfileDef_ValidWebThickness:
    SCOPE = "entity"
    TYPE_NAME = "IfcUShapeProfileDef"
    RULE_NAME = "ValidWebThickness"

    @staticmethod    
    def __call__(self):
        flangewidth = self.FlangeWidth
        webthickness = self.WebThickness
        
        assert (webthickness < flangewidth) is not False
        




class IfcUnitAssignment_WR01:
    SCOPE = "entity"
    TYPE_NAME = "IfcUnitAssignment"
    RULE_NAME = "WR01"

    @staticmethod    
    def __call__(self):
        units = self.Units
        
        assert (IfcCorrectUnitAssignment(units)) is not False
        




class IfcUnitaryControlElement_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcUnitaryControlElement"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcUnitaryControlElementTypeEnum.USERDEFINED) or ((predefinedtype == IfcUnitaryControlElementTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcUnitaryControlElement_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcUnitaryControlElement"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcunitarycontrolelementtype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcUnitaryControlElementType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcUnitaryControlElementType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcUnitaryControlElementTypeEnum.USERDEFINED) or ((predefinedtype == IfcUnitaryControlElementTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcUnitaryEquipment_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcUnitaryEquipment"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcUnitaryEquipmentTypeEnum.USERDEFINED) or ((predefinedtype == IfcUnitaryEquipmentTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcUnitaryEquipment_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcUnitaryEquipment"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcunitaryequipmenttype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcUnitaryEquipmentType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcUnitaryEquipmentType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcUnitaryEquipmentTypeEnum.USERDEFINED) or ((predefinedtype == IfcUnitaryEquipmentTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcValve_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcValve"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcValveTypeEnum.USERDEFINED) or ((predefinedtype == IfcValveTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcValve_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcValve"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcvalvetype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcValveType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcValveType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcValveTypeEnum.USERDEFINED) or ((predefinedtype == IfcValveTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcVector_MagGreaterOrEqualZero:
    SCOPE = "entity"
    TYPE_NAME = "IfcVector"
    RULE_NAME = "MagGreaterOrEqualZero"

    @staticmethod    
    def __call__(self):
        magnitude = self.Magnitude
        
        assert (magnitude >= 0.0) is not False
        



def calc_IfcVector_Dim(self):
    orientation = self.Orientation
    return \
    orientation.Dim













class IfcVibrationIsolator_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcVibrationIsolator"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcVibrationIsolatorTypeEnum.USERDEFINED) or ((predefinedtype == IfcVibrationIsolatorTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcVibrationIsolator_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcVibrationIsolator"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcvibrationisolatortype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcVibrationIsolatorType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcVibrationIsolatorType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcVibrationIsolatorTypeEnum.USERDEFINED) or ((predefinedtype == IfcVibrationIsolatorTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        










class IfcVoidingFeature_HasObjectType:
    SCOPE = "entity"
    TYPE_NAME = "IfcVoidingFeature"
    RULE_NAME = "HasObjectType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcVoidingFeatureTypeEnum.USERDEFINED) or exists(self.ObjectType)) is not False
        




class IfcWall_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcWall"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcWallTypeEnum.USERDEFINED) or ((predefinedtype == IfcWallTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcWall_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcWall"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcwalltype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcWallElementedCase_HasDecomposition:
    SCOPE = "entity"
    TYPE_NAME = "IfcWallElementedCase"
    RULE_NAME = "HasDecomposition"

    @staticmethod    
    def __call__(self):

        
        assert (hiindex(self.IsDecomposedBy) > 0) is not False
        




class IfcWallStandardCase_HasMaterialLayerSetUsage:
    SCOPE = "entity"
    TYPE_NAME = "IfcWallStandardCase"
    RULE_NAME = "HasMaterialLayerSetUsage"

    @staticmethod    
    def __call__(self):

        
        assert ((sizeof([temp for temp in usedin(self,'ifc4.ifcrelassociates.relatedobjects') if ('ifc4.ifcrelassociatesmaterial' in typeof(temp)) and ('ifc4.ifcmateriallayersetusage' in typeof(temp.RelatingMaterial))])) == 1) is not False
        




class IfcWallType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcWallType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcWallTypeEnum.USERDEFINED) or ((predefinedtype == IfcWallTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcWasteTerminal_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcWasteTerminal"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcWasteTerminalTypeEnum.USERDEFINED) or ((predefinedtype == IfcWasteTerminalTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        



class IfcWasteTerminal_CorrectTypeAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcWasteTerminal"
    RULE_NAME = "CorrectTypeAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcwasteterminaltype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcWasteTerminalType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcWasteTerminalType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcWasteTerminalTypeEnum.USERDEFINED) or ((predefinedtype == IfcWasteTerminalTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcWindow_CorrectStyleAssigned:
    SCOPE = "entity"
    TYPE_NAME = "IfcWindow"
    RULE_NAME = "CorrectStyleAssigned"

    @staticmethod    
    def __call__(self):
        istypedby = self.IsTypedBy
        
        assert ((sizeof(istypedby) == 0) or ('ifc4.ifcwindowtype' in (typeof(self.IsTypedBy[1 - 1].RelatingType)))) is not False
        




class IfcWindowLiningProperties_WR31:
    SCOPE = "entity"
    TYPE_NAME = "IfcWindowLiningProperties"
    RULE_NAME = "WR31"

    @staticmethod    
    def __call__(self):
        liningdepth = self.LiningDepth
        liningthickness = self.LiningThickness
        
        assert (not exists(liningdepth) and (not exists(liningthickness))) is not False
        



class IfcWindowLiningProperties_WR32:
    SCOPE = "entity"
    TYPE_NAME = "IfcWindowLiningProperties"
    RULE_NAME = "WR32"

    @staticmethod    
    def __call__(self):
        firsttransomoffset = self.FirstTransomOffset
        secondtransomoffset = self.SecondTransomOffset
        
        assert (not (not exists(firsttransomoffset)) and exists(secondtransomoffset)) is not False
        



class IfcWindowLiningProperties_WR33:
    SCOPE = "entity"
    TYPE_NAME = "IfcWindowLiningProperties"
    RULE_NAME = "WR33"

    @staticmethod    
    def __call__(self):
        firstmullionoffset = self.FirstMullionOffset
        secondmullionoffset = self.SecondMullionOffset
        
        assert (not (not exists(firstmullionoffset)) and exists(secondmullionoffset)) is not False
        



class IfcWindowLiningProperties_WR34:
    SCOPE = "entity"
    TYPE_NAME = "IfcWindowLiningProperties"
    RULE_NAME = "WR34"

    @staticmethod    
    def __call__(self):

        
        assert ((exists(lambda: self.DefinesType[1 - 1])) and (('ifc4.ifcwindowtype' in (typeof(self.DefinesType[1 - 1]))) or ('ifc4.ifcwindowstyle' in (typeof(self.DefinesType[1 - 1]))))) is not False
        




class IfcWindowPanelProperties_ApplicableToType:
    SCOPE = "entity"
    TYPE_NAME = "IfcWindowPanelProperties"
    RULE_NAME = "ApplicableToType"

    @staticmethod    
    def __call__(self):

        
        assert ((exists(lambda: self.DefinesType[1 - 1])) and (('ifc4.ifcwindowtype' in (typeof(self.DefinesType[1 - 1]))) or ('ifc4.ifcwindowstyle' in (typeof(self.DefinesType[1 - 1]))))) is not False
        










class IfcWindowType_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcWindowType"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((predefinedtype != IfcWindowTypeEnum.USERDEFINED) or ((predefinedtype == IfcWindowTypeEnum.USERDEFINED) and exists(self.ElementType))) is not False
        




class IfcWorkCalendar_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcWorkCalendar"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcWorkCalendarTypeEnum.USERDEFINED) or ((predefinedtype == IfcWorkCalendarTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        







class IfcWorkPlan_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcWorkPlan"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcWorkPlanTypeEnum.USERDEFINED) or ((predefinedtype == IfcWorkPlanTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        




class IfcWorkSchedule_CorrectPredefinedType:
    SCOPE = "entity"
    TYPE_NAME = "IfcWorkSchedule"
    RULE_NAME = "CorrectPredefinedType"

    @staticmethod    
    def __call__(self):
        predefinedtype = self.PredefinedType
        
        assert ((not exists(predefinedtype)) or (predefinedtype != IfcWorkScheduleTypeEnum.USERDEFINED) or ((predefinedtype == IfcWorkScheduleTypeEnum.USERDEFINED) and exists(self.ObjectType))) is not False
        







class IfcZShapeProfileDef_ValidFlangeThickness:
    SCOPE = "entity"
    TYPE_NAME = "IfcZShapeProfileDef"
    RULE_NAME = "ValidFlangeThickness"

    @staticmethod    
    def __call__(self):
        depth = self.Depth
        flangethickness = self.FlangeThickness
        
        assert (flangethickness < (depth / 2.)) is not False
        




class IfcZone_WR1:
    SCOPE = "entity"
    TYPE_NAME = "IfcZone"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):

        
        assert ((sizeof(self.IsGroupedBy) == 0) or ((sizeof([temp for temp in self.IsGroupedBy[1 - 1].RelatedObjects if not ('ifc4.ifczone' in typeof(temp)) or ('ifc4.ifcspace' in typeof(temp)) or ('ifc4.ifcspatialzone' in typeof(temp))])) == 0)) is not False
        




class IfcRepresentationContextSameWCS:
    SCOPE = "file"

    @staticmethod    
    def __call__(file):
        IfcGeometricRepresentationContext = file.by_type("IfcGeometricRepresentationContext")
        isdifferent = False
        if sizeof(IfcGeometricRepresentationContext) > 1:
            for i in range(2, hiindex(IfcGeometricRepresentationContext) + 1):
                if (IfcGeometricRepresentationContext[1 - 1].WorldCoordinateSystem) != (IfcGeometricRepresentationContext[i - 1].WorldCoordinateSystem):
                    isdifferent = (not IfcSameValidPrecision(IfcGeometricRepresentationContext[1 - 1].Precision,IfcGeometricRepresentationContext[i - 1].Precision)) or (not IfcSameAxis2Placement(IfcGeometricRepresentationContext[1 - 1].WorldCoordinateSystem,IfcGeometricRepresentationContext[i - 1].WorldCoordinateSystem,IfcGeometricRepresentationContext[1 - 1].Precision))
                    if isdifferent == True:
                        break
        
        assert (isdifferent == False) is not False
        




class IfcSingleProjectInstance:
    SCOPE = "file"

    @staticmethod    
    def __call__(file):
        IfcProject = file.by_type("IfcProject")


        
        assert (sizeof(IfcProject) <= 1) is not False
        



def IfcAssociatedSurface(arg):
    
    surf = arg.BasisSurface
    return surf


def IfcBaseAxis(dim, axis1, axis2, axis3):
    
    
    
    if dim == 3:
        d1 = nvl(IfcNormalise(axis3),IfcDirection(DirectionRatios=[0.0,0.0,1.0]))
        d2 = IfcFirstProjAxis(d1,axis1)
        u = [d2,IfcSecondProjAxis(d1,d2,axis2),d1]
    else:
        if exists(axis1):
            d1 = IfcNormalise(axis1)
            u = [d1,IfcOrthogonalComplement(d1)]
            if exists(axis2):
                factor = IfcDotProduct(axis2,u[2 - 1])
                if factor < 0.0:
                    u[2 - 1].DirectionRatios[1 - 1] = -u[2 - 1].DirectionRatios[1 - 1]
                    u[2 - 1].DirectionRatios[2 - 1] = -u[2 - 1].DirectionRatios[2 - 1]
        else:
            if exists(axis2):
                d1 = IfcNormalise(axis2)
                u = [IfcOrthogonalComplement(d1),d1]
                u[1 - 1].DirectionRatios[1 - 1] = -u[1 - 1].DirectionRatios[1 - 1]
                u[1 - 1].DirectionRatios[2 - 1] = -u[1 - 1].DirectionRatios[2 - 1]
            else:
                u = [IfcDirection(DirectionRatios=[1.0,0.0]),IfcDirection(DirectionRatios=[0.0,1.0])]
    return u


def IfcBooleanChoose(b, choice1, choice2):

    if b:
        return choice1
    else:
        return choice2


def IfcBuild2Axes(refdirection):
    d = nvl(IfcNormalise(refdirection),IfcDirection(DirectionRatios=[1.0,0.0]))
    return [d,IfcOrthogonalComplement(d)]


def IfcBuildAxes(axis, refdirection):
    
    d1 = nvl(IfcNormalise(axis),IfcDirection(DirectionRatios=[0.0,0.0,1.0]))
    d2 = IfcFirstProjAxis(d1,refdirection)
    return [d2,IfcNormalise(IfcCrossProduct(d1,d2)).Orientation,d1]


def IfcConsecutiveSegments(segments):
    result = True
    for i in range(1, hiindex(segments) - 1 + 1):
        if (segments[i - 1][hiindex(segments[i - 1]) - 1]) != (segments[i - 1][1 - 1]):
            result = False
            break
    return result


def IfcConstraintsParamBSpline(degree, upknots, upcp, knotmult, knots):
    result = True
    
    sum = knotmult[1 - 1]
    for i in range(2, upknots + 1):
        sum = sum + (knotmult[i - 1])
    if (degree < 1) or (upknots < 2) or (upcp < degree) or (sum != (degree + upcp + 2)):
        result = False
        return result
    k = knotmult[1 - 1]
    if (k < 1) or (k > (degree + 1)):
        result = False
        return result
    for i in range(2, upknots + 1):
        if ((knotmult[i - 1]) < 1) or ((knots[i - 1]) <= (knots[i - 1])):
            result = False
            return result
        k = knotmult[i - 1]
        if (i < upknots) and (k > degree):
            result = False
            return result
        if (i == upknots) and (k > (degree + 1)):
            result = False
            return result
    return result


def IfcConvertDirectionInto2D(direction):
    direction2d = IfcDirection(DirectionRatios=[0.,1.])
    temp = list(direction2d.DirectionRatios)
    temp[1 - 1] = direction.DirectionRatios[1 - 1]
    direction2d.DirectionRatios = temp
    temp = list(direction2d.DirectionRatios)
    temp[2 - 1] = direction.DirectionRatios[2 - 1]
    direction2d.DirectionRatios = temp
    return direction2d


def IfcCorrectDimensions(m, dim):

    if m == lengthunit:
        if dim == IfcDimensionalExponents(1,0,0,0,0,0,0):
            return True
        else:
            return False
    elif m == massunit:
        if dim == IfcDimensionalExponents(0,1,0,0,0,0,0):
            return True
        else:
            return False
    elif m == timeunit:
        if dim == IfcDimensionalExponents(0,0,1,0,0,0,0):
            return True
        else:
            return False
    elif m == electriccurrentunit:
        if dim == IfcDimensionalExponents(0,0,0,1,0,0,0):
            return True
        else:
            return False
    elif m == thermodynamictemperatureunit:
        if dim == IfcDimensionalExponents(0,0,0,0,1,0,0):
            return True
        else:
            return False
    elif m == amountofsubstanceunit:
        if dim == IfcDimensionalExponents(0,0,0,0,0,1,0):
            return True
        else:
            return False
    elif m == luminousintensityunit:
        if dim == IfcDimensionalExponents(0,0,0,0,0,0,1):
            return True
        else:
            return False
    elif m == planeangleunit:
        if dim == IfcDimensionalExponents(0,0,0,0,0,0,0):
            return True
        else:
            return False
    elif m == solidangleunit:
        if dim == IfcDimensionalExponents(0,0,0,0,0,0,0):
            return True
        else:
            return False
    elif m == areaunit:
        if dim == IfcDimensionalExponents(2,0,0,0,0,0,0):
            return True
        else:
            return False
    elif m == volumeunit:
        if dim == IfcDimensionalExponents(3,0,0,0,0,0,0):
            return True
        else:
            return False
    elif m == absorbeddoseunit:
        if dim == IfcDimensionalExponents(2,0,-2,0,0,0,0):
            return True
        else:
            return False
    elif m == radioactivityunit:
        if dim == IfcDimensionalExponents(0,0,-1,0,0,0,0):
            return True
        else:
            return False
    elif m == electriccapacitanceunit:
        if dim == IfcDimensionalExponents(-2,-1,4,2,0,0,0):
            return True
        else:
            return False
    elif m == doseequivalentunit:
        if dim == IfcDimensionalExponents(2,0,-2,0,0,0,0):
            return True
        else:
            return False
    elif m == electricchargeunit:
        if dim == IfcDimensionalExponents(0,0,1,1,0,0,0):
            return True
        else:
            return False
    elif m == electricconductanceunit:
        if dim == IfcDimensionalExponents(-2,-1,3,2,0,0,0):
            return True
        else:
            return False
    elif m == electricvoltageunit:
        if dim == IfcDimensionalExponents(2,1,-3,-1,0,0,0):
            return True
        else:
            return False
    elif m == electricresistanceunit:
        if dim == IfcDimensionalExponents(2,1,-3,-2,0,0,0):
            return True
        else:
            return False
    elif m == energyunit:
        if dim == IfcDimensionalExponents(2,1,-2,0,0,0,0):
            return True
        else:
            return False
    elif m == forceunit:
        if dim == IfcDimensionalExponents(1,1,-2,0,0,0,0):
            return True
        else:
            return False
    elif m == frequencyunit:
        if dim == IfcDimensionalExponents(0,0,-1,0,0,0,0):
            return True
        else:
            return False
    elif m == inductanceunit:
        if dim == IfcDimensionalExponents(2,1,-2,-2,0,0,0):
            return True
        else:
            return False
    elif m == illuminanceunit:
        if dim == IfcDimensionalExponents(-2,0,0,0,0,0,1):
            return True
        else:
            return False
    elif m == luminousfluxunit:
        if dim == IfcDimensionalExponents(0,0,0,0,0,0,1):
            return True
        else:
            return False
    elif m == magneticfluxunit:
        if dim == IfcDimensionalExponents(2,1,-2,-1,0,0,0):
            return True
        else:
            return False
    elif m == magneticfluxdensityunit:
        if dim == IfcDimensionalExponents(0,1,-2,-1,0,0,0):
            return True
        else:
            return False
    elif m == powerunit:
        if dim == IfcDimensionalExponents(2,1,-3,0,0,0,0):
            return True
        else:
            return False
    elif m == pressureunit:
        if dim == IfcDimensionalExponents(-1,1,-2,0,0,0,0):
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
    external = sizeof([style for style in styles if 'ifc4.ifcexternallydefinedhatchstyle' in typeof(style)])
    hatching = sizeof([style for style in styles if 'ifc4.ifcfillareastylehatching' in typeof(style)])
    tiles = sizeof([style for style in styles if 'ifc4.ifcfillareastyletiles' in typeof(style)])
    colour = sizeof([style for style in styles if 'ifc4.ifccolour' in typeof(style)])
    if external > 1:
        return False
    if (external == 1) and ((hatching > 0) or (tiles > 0) or (colour > 0)):
        return False
    if colour > 1:
        return False
    if (hatching > 0) and (tiles > 0):
        return False
    return True


def IfcCorrectLocalPlacement(axisplacement, relplacement):

    if exists(relplacement):
        if 'ifc4.ifcgridplacement' in typeof(relplacement):
            return None
        if 'ifc4.ifclocalplacement' in typeof(relplacement):
            if 'ifc4.ifcaxis2placement2d' in typeof(axisplacement):
                return True
            if 'ifc4.ifcaxis2placement3d' in typeof(axisplacement):
                if relplacement.RelativePlacement.Dim == 3:
                    return True
                else:
                    return False
        return True
    return None


def IfcCorrectObjectAssignment(constraint, objects):
    count = 0
    if not exists(constraint):
        return True
    if constraint == IfcObjectTypeEnum.NOTDEFINED:
        return True
    elif constraint == IfcObjectTypeEnum.PRODUCT:
        count = sizeof([temp for temp in objects if not 'ifc4.ifcproduct' in typeof(temp)])
        return count == 0
    elif constraint == IfcObjectTypeEnum.PROCESS:
        count = sizeof([temp for temp in objects if not 'ifc4.ifcprocess' in typeof(temp)])
        return count == 0
    elif constraint == IfcObjectTypeEnum.CONTROL:
        count = sizeof([temp for temp in objects if not 'ifc4.ifccontrol' in typeof(temp)])
        return count == 0
    elif constraint == IfcObjectTypeEnum.RESOURCE:
        count = sizeof([temp for temp in objects if not 'ifc4.ifcresource' in typeof(temp)])
        return count == 0
    elif constraint == IfcObjectTypeEnum.ACTOR:
        count = sizeof([temp for temp in objects if not 'ifc4.ifcactor' in typeof(temp)])
        return count == 0
    elif constraint == IfcObjectTypeEnum.GROUP:
        count = sizeof([temp for temp in objects if not 'ifc4.ifcgroup' in typeof(temp)])
        return count == 0
    elif constraint == IfcObjectTypeEnum.PROJECT:
        count = sizeof([temp for temp in objects if not 'ifc4.ifcproject' in typeof(temp)])
        return count == 0
    else:
        return None


def IfcCorrectUnitAssignment(units):
    namedunitnumber = 0
    derivedunitnumber = 0
    monetaryunitnumber = 0
    namedunitnames = express_set([])
    derivedunitnames = express_set([])
    namedunitnumber = sizeof([temp for temp in units if ('ifc4.ifcnamedunit' in typeof(temp)) and (not temp.UnitType == IfcUnitEnum.USERDEFINED)])
    derivedunitnumber = sizeof([temp for temp in units if ('ifc4.ifcderivedunit' in typeof(temp)) and (not temp.UnitType == IfcDerivedUnitEnum.USERDEFINED)])
    monetaryunitnumber = sizeof([temp for temp in units if 'ifc4.ifcmonetaryunit' in typeof(temp)])
    for i in range(1, sizeof(units) + 1):
        if ('ifc4.ifcnamedunit' in (typeof(units[i - 1]))) and (not (units[i - 1].UnitType) == IfcUnitEnum.USERDEFINED):
            namedunitnames = namedunitnames + (units[i - 1].UnitType)
        if ('ifc4.ifcderivedunit' in (typeof(units[i - 1]))) and (not (units[i - 1].UnitType) == IfcDerivedUnitEnum.USERDEFINED):
            derivedunitnames = derivedunitnames + (units[i - 1].UnitType)
    return (sizeof(namedunitnames) == namedunitnumber) and (sizeof(derivedunitnames) == derivedunitnumber) and (monetaryunitnumber <= 1)


def IfcCrossProduct(arg1, arg2):
    
    
    
    
    if ((not exists(arg1)) or (arg1.Dim == 2)) or ((not exists(arg2)) or (arg2.Dim == 2)):
        return None
    else:
        v1 = IfcNormalise(arg1).DirectionRatios
        v2 = IfcNormalise(arg2).DirectionRatios
        res = IfcDirection(DirectionRatios=[((v1[2 - 1]) * (v2[3 - 1])) - ((v1[3 - 1]) * (v2[2 - 1])),((v1[3 - 1]) * (v2[1 - 1])) - ((v1[1 - 1]) * (v2[3 - 1])),((v1[1 - 1]) * (v2[2 - 1])) - ((v1[2 - 1]) * (v2[1 - 1]))])
        mag = 0.0
        for i in range(1, 3 + 1):
            mag = mag + ((res.DirectionRatios[i - 1]) * (res.DirectionRatios[i - 1]))
        if mag > 0.0:
            result = IfcVector(Orientation=res, Magnitude=sqrt(mag))
        else:
            result = IfcVector(Orientation=arg1, Magnitude=0.0)
        return result


def IfcCurveDim(curve):

    if 'ifc4.ifcline' in typeof(curve):
        return curve.Pnt.Dim
    if 'ifc4.ifcconic' in typeof(curve):
        return curve.Position.Dim
    if 'ifc4.ifcpolyline' in typeof(curve):
        return curve.Points[1 - 1].Dim
    if 'ifc4.ifctrimmedcurve' in typeof(curve):
        return IfcCurveDim(curve.BasisCurve)
    if 'ifc4.ifccompositecurve' in typeof(curve):
        return curve.Segments[1 - 1].Dim
    if 'ifc4.ifcbsplinecurve' in typeof(curve):
        return curve.ControlPointsList[1 - 1].Dim
    if 'ifc4.ifcoffsetcurve2d' in typeof(curve):
        return 2
    if 'ifc4.ifcoffsetcurve3d' in typeof(curve):
        return 3
    if 'ifc4.ifcpcurve' in typeof(curve):
        return 3
    if 'ifc4.ifcindexedpolycurve' in typeof(curve):
        return curve.Points.Dim
    return None


def IfcCurveWeightsPositive(b):
    result = True
    for i in range(0, b.UpperIndexOnControlPoints + 1):
        if (b.Weights[i - 1]) <= 0.0:
            result = False
            return result
    return result


def IfcDeriveDimensionalExponents(unitelements):
    result = IfcDimensionalExponents(0,0,0,0,0,0,0)
    for i in range(loindex(unitelements), hiindex(unitelements) + 1):
        result.LengthExponent = result.LengthExponent + ((unitelements[i - 1].Exponent) * (unitelements[i - 1].Unit.Dimensions.LengthExponent))
        result.MassExponent = result.MassExponent + ((unitelements[i - 1].Exponent) * (unitelements[i - 1].Unit.Dimensions.MassExponent))
        result.TimeExponent = result.TimeExponent + ((unitelements[i - 1].Exponent) * (unitelements[i - 1].Unit.Dimensions.TimeExponent))
        result.ElectricCurrentExponent = result.ElectricCurrentExponent + ((unitelements[i - 1].Exponent) * (unitelements[i - 1].Unit.Dimensions.ElectricCurrentExponent))
        result.ThermodynamicTemperatureExponent = result.ThermodynamicTemperatureExponent + ((unitelements[i - 1].Exponent) * (unitelements[i - 1].Unit.Dimensions.ThermodynamicTemperatureExponent))
        result.AmountOfSubstanceExponent = result.AmountOfSubstanceExponent + ((unitelements[i - 1].Exponent) * (unitelements[i - 1].Unit.Dimensions.AmountOfSubstanceExponent))
        result.LuminousIntensityExponent = result.LuminousIntensityExponent + ((unitelements[i - 1].Exponent) * (unitelements[i - 1].Unit.Dimensions.LuminousIntensityExponent))
    return result


def IfcDimensionsForSiUnit(n):

    if n == metre:
        return IfcDimensionalExponents(1,0,0,0,0,0,0)
    elif n == square_metre:
        return IfcDimensionalExponents(2,0,0,0,0,0,0)
    elif n == cubic_metre:
        return IfcDimensionalExponents(3,0,0,0,0,0,0)
    elif n == gram:
        return IfcDimensionalExponents(0,1,0,0,0,0,0)
    elif n == second:
        return IfcDimensionalExponents(0,0,1,0,0,0,0)
    elif n == ampere:
        return IfcDimensionalExponents(0,0,0,1,0,0,0)
    elif n == kelvin:
        return IfcDimensionalExponents(0,0,0,0,1,0,0)
    elif n == mole:
        return IfcDimensionalExponents(0,0,0,0,0,1,0)
    elif n == candela:
        return IfcDimensionalExponents(0,0,0,0,0,0,1)
    elif n == radian:
        return IfcDimensionalExponents(0,0,0,0,0,0,0)
    elif n == steradian:
        return IfcDimensionalExponents(0,0,0,0,0,0,0)
    elif n == hertz:
        return IfcDimensionalExponents(0,0,-1,0,0,0,0)
    elif n == newton:
        return IfcDimensionalExponents(1,1,-2,0,0,0,0)
    elif n == pascal:
        return IfcDimensionalExponents(-1,1,-2,0,0,0,0)
    elif n == joule:
        return IfcDimensionalExponents(2,1,-2,0,0,0,0)
    elif n == watt:
        return IfcDimensionalExponents(2,1,-3,0,0,0,0)
    elif n == coulomb:
        return IfcDimensionalExponents(0,0,1,1,0,0,0)
    elif n == volt:
        return IfcDimensionalExponents(2,1,-3,-1,0,0,0)
    elif n == farad:
        return IfcDimensionalExponents(-2,-1,4,2,0,0,0)
    elif n == ohm:
        return IfcDimensionalExponents(2,1,-3,-2,0,0,0)
    elif n == siemens:
        return IfcDimensionalExponents(-2,-1,3,2,0,0,0)
    elif n == weber:
        return IfcDimensionalExponents(2,1,-2,-1,0,0,0)
    elif n == tesla:
        return IfcDimensionalExponents(0,1,-2,-1,0,0,0)
    elif n == henry:
        return IfcDimensionalExponents(2,1,-2,-2,0,0,0)
    elif n == degree_celsius:
        return IfcDimensionalExponents(0,0,0,0,1,0,0)
    elif n == lumen:
        return IfcDimensionalExponents(0,0,0,0,0,0,1)
    elif n == lux:
        return IfcDimensionalExponents(-2,0,0,0,0,0,1)
    elif n == becquerel:
        return IfcDimensionalExponents(0,0,-1,0,0,0,0)
    elif n == gray:
        return IfcDimensionalExponents(2,0,-2,0,0,0,0)
    elif n == sievert:
        return IfcDimensionalExponents(2,0,-2,0,0,0,0)
    else:
        return IfcDimensionalExponents(0,0,0,0,0,0,0)


def IfcDotProduct(arg1, arg2):
    
    
    
    if (not exists(arg1)) or (not exists(arg2)):
        scalar = None
    else:
        if arg1.Dim != arg2.Dim:
            scalar = None
        else:
            vec1 = IfcNormalise(arg1)
            vec2 = IfcNormalise(arg2)
            ndim = arg1.Dim
            scalar = 0.0
            for i in range(1, ndim + 1):
                scalar = scalar + ((vec1.DirectionRatios[i - 1]) * (vec2.DirectionRatios[i - 1]))
    return scalar


def IfcFirstProjAxis(zaxis, arg):
    
    
    
    
    if not exists(zaxis):
        return None
    else:
        z = IfcNormalise(zaxis)
        if not exists(arg):
            if z.DirectionRatios != [1.0,0.0,0.0]:
                v = IfcDirection(DirectionRatios=[1.0,0.0,0.0])
            else:
                v = IfcDirection(DirectionRatios=[0.0,1.0,0.0])
        else:
            if arg.Dim != 3:
                return None
            if IfcCrossProduct(arg,z).Magnitude == 0.0:
                return None
            else:
                v = IfcNormalise(arg)
        xvec = IfcScalarTimesVector(IfcDotProduct(v,z),z)
        xaxis = IfcVectorDifference(v,xvec).Orientation
        xaxis = IfcNormalise(xaxis)
    return xaxis


def IfcGetBasisSurface(c):
    
    
    surfs = []
    if 'ifc4.ifcpcurve' in typeof(c):
        surfs = [c.BasisSurface]
    else:
        if 'ifc4.ifcsurfacecurve' in typeof(c):
            n = sizeof(c.AssociatedGeometry)
            for i in range(1, n + 1):
                surfs = surfs + (IfcAssociatedSurface(c.AssociatedGeometry[i - 1]))
    if 'ifc4.ifccompositecurveonsurface' in typeof(c):
        n = sizeof(c.Segments)
        surfs = IfcGetBasisSurface(c.Segments[1 - 1].ParentCurve)
        if n > 1:
            for i in range(2, n + 1):
                surfs = surfs * (IfcGetBasisSurface(c.Segments[1 - 1].ParentCurve))
    return surfs


def IfcListToArray(lis, low, u):
    
    
    n = sizeof(lis)
    if n != (u - low + 1):
        return None
    else:
        res = ([lis[1 - 1]] * n)
        for i in range(2, n + 1):
            temp = list(res)
            temp[low - 1] = lis[i - 1]
            res = temp
        return res


def IfcLoopHeadToTail(aloop):
    
    p = True
    n = sizeof(aloop.EdgeList)
    for i in range(2, n + 1):
        p = p and ((aloop.EdgeList[i - 1].EdgeEnd) == (aloop.EdgeList[i - 1].EdgeStart))
    return p


def IfcMakeArrayOfArray(lis, low1, u1, low2, u2):
    
    if (u1 - low1 + 1) != sizeof(lis):
        return None
    if (u2 - low2 + 1) != (sizeof(lis[1 - 1])):
        return None
    res = ([IfcListToArray(lis[1 - 1],low2,u2)] * u1 - low1 + 1)
    for i in range(2, hiindex(lis) + 1):
        if (u2 - low2 + 1) != (sizeof(lis[i - 1])):
            return None
        temp = list(res)
        temp[low1 - 1] = IfcListToArray(lis[i - 1],low2,u2)
        res = temp
    return res


def IfcMlsTotalThickness(layerset):
    max = layerset.MaterialLayers[1 - 1].LayerThickness
    if sizeof(layerset.MaterialLayers) > 1:
        for i in range(2, hiindex(layerset.MaterialLayers) + 1):
            max = max + (layerset.MaterialLayers[i - 1].LayerThickness)
    return max


def IfcNormalise(arg):
    
    v = IfcDirection(DirectionRatios=[1.,0.])
    vec = IfcVector(Orientation=IfcDirection(DirectionRatios=[1.,0.]), Magnitude=1.)
    
    result = v
    if not exists(arg):
        return None
    else:
        if 'ifc4.ifcvector' in typeof(arg):
            ndim = arg.Dim
            v.DirectionRatios = arg.Orientation.DirectionRatios
            vec.Magnitude = arg.Magnitude
            vec.Orientation = v
            if arg.Magnitude == 0.0:
                return None
            else:
                vec.Magnitude = 1.0
        else:
            ndim = arg.Dim
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
            if 'ifc4.ifcvector' in typeof(arg):
                vec.Orientation = v
                result = vec
            else:
                result = v
        else:
            return None
    return result


def IfcOrthogonalComplement(vec):
    
    if (not exists(vec)) or (vec.Dim != 2):
        return None
    else:
        result = IfcDirection(DirectionRatios=[-vec.DirectionRatios[2 - 1],vec.DirectionRatios[1 - 1]])
        return result


def IfcPathHeadToTail(apath):
    n = 0
    p = unknown
    n = sizeof(apath.EdgeList)
    for i in range(2, n + 1):
        p = p and ((apath.EdgeList[i - 1].EdgeEnd) == (apath.EdgeList[i - 1].EdgeStart))
    return p


def IfcPointListDim(pointlist):

    if 'ifc4.ifccartesianpointlist2d' in typeof(pointlist):
        return 2
    if 'ifc4.ifccartesianpointlist3d' in typeof(pointlist):
        return 3
    return None


def IfcSameAxis2Placement(ap1, ap2, epsilon):

    return (IfcSameDirection(ap1.P[1 - 1],ap2.P[1 - 1],epsilon)) and (IfcSameDirection(ap1.P[2 - 1],ap2.P[2 - 1],epsilon)) and IfcSameCartesianPoint(ap1.Location,ap1.Location,epsilon)


def IfcSameCartesianPoint(cp1, cp2, epsilon):
    cp1x = cp1.Coordinates[1 - 1]
    cp1y = cp1.Coordinates[2 - 1]
    cp1z = 0
    cp2x = cp2.Coordinates[1 - 1]
    cp2y = cp2.Coordinates[2 - 1]
    cp2z = 0
    if sizeof(cp1.Coordinates) > 2:
        cp1z = cp1.Coordinates[3 - 1]
    if sizeof(cp2.Coordinates) > 2:
        cp2z = cp2.Coordinates[3 - 1]
    return IfcSameValue(cp1x,cp2x,epsilon) and IfcSameValue(cp1y,cp2y,epsilon) and IfcSameValue(cp1z,cp2z,epsilon)


def IfcSameDirection(dir1, dir2, epsilon):
    dir1x = dir1.DirectionRatios[1 - 1]
    dir1y = dir1.DirectionRatios[2 - 1]
    dir1z = 0
    dir2x = dir2.DirectionRatios[1 - 1]
    dir2y = dir2.DirectionRatios[2 - 1]
    dir2z = 0
    if sizeof(dir1.DirectionRatios) > 2:
        dir1z = dir1.DirectionRatios[3 - 1]
    if sizeof(dir2.DirectionRatios) > 2:
        dir2z = dir2.DirectionRatios[3 - 1]
    return IfcSameValue(dir1x,dir2x,epsilon) and IfcSameValue(dir1y,dir2y,epsilon) and IfcSameValue(dir1z,dir2z,epsilon)


def IfcSameValidPrecision(epsilon1, epsilon2):
    
    defaulteps = 0.000001
    derivationofeps = 1.001
    uppereps = 1.0
    valideps1 = nvl(epsilon1,defaulteps)
    valideps2 = nvl(epsilon2,defaulteps)
    return (0.0 < valideps1) and (valideps1 <= (derivationofeps * valideps2)) and (valideps2 <= (derivationofeps * valideps1)) and (valideps2 < uppereps)


def IfcSameValue(value1, value2, epsilon):
    
    defaulteps = 0.000001
    valideps = nvl(epsilon,defaulteps)
    return ((value1 + valideps) > value2) and (value1 < (value2 + valideps))


def IfcScalarTimesVector(scalar, vec):
    
    
    
    if (not exists(scalar)) or (not exists(vec)):
        return None
    else:
        if 'ifc4.ifcvector' in typeof(vec):
            v = vec.Orientation
            mag = scalar * vec.Magnitude
        else:
            v = vec
            mag = scalar
        if mag < 0.0:
            for i in range(1, sizeof(v.DirectionRatios) + 1):
                temp = list(v.DirectionRatios)
                temp[i - 1] = -v.DirectionRatios[i - 1]
                v.DirectionRatios = temp
            mag = -mag
        result = IfcVector(Orientation=IfcNormalise(v), Magnitude=mag)
    return result


def IfcSecondProjAxis(zaxis, xaxis, arg):
    
    
    
    if not exists(arg):
        v = IfcDirection(DirectionRatios=[0.0,1.0,0.0])
    else:
        v = arg
    temp = IfcScalarTimesVector(IfcDotProduct(v,zaxis),zaxis)
    yaxis = IfcVectorDifference(v,temp)
    temp = IfcScalarTimesVector(IfcDotProduct(v,xaxis),xaxis)
    yaxis = IfcVectorDifference(yaxis,temp)
    yaxis = IfcNormalise(yaxis)
    return yaxis.Orientation


def IfcShapeRepresentationTypes(reptype, items):
    count = 0
    if reptype.lower() == 'point':
        count = sizeof([temp for temp in items if 'ifc4.ifcpoint' in typeof(temp)])
    elif reptype.lower() == 'pointcloud':
        count = sizeof([temp for temp in items if 'ifc4.ifccartesianpointlist3d' in typeof(temp)])
    elif reptype.lower() == 'curve':
        count = sizeof([temp for temp in items if 'ifc4.ifccurve' in typeof(temp)])
    elif reptype.lower() == 'curve2d':
        count = sizeof([temp for temp in items if ('ifc4.ifccurve' in typeof(temp)) and (temp.Dim == 2)])
    elif reptype.lower() == 'curve3d':
        count = sizeof([temp for temp in items if ('ifc4.ifccurve' in typeof(temp)) and (temp.Dim == 3)])
    elif reptype.lower() == 'surface':
        count = sizeof([temp for temp in items if 'ifc4.ifcsurface' in typeof(temp)])
    elif reptype.lower() == 'surface2d':
        count = sizeof([temp for temp in items if ('ifc4.ifcsurface' in typeof(temp)) and (temp.Dim == 2)])
    elif reptype.lower() == 'surface3d':
        count = sizeof([temp for temp in items if ('ifc4.ifcsurface' in typeof(temp)) and (temp.Dim == 3)])
    elif reptype.lower() == 'fillarea':
        count = sizeof([temp for temp in items if 'ifc4.ifcannotationfillarea' in typeof(temp)])
    elif reptype.lower() == 'text':
        count = sizeof([temp for temp in items if 'ifc4.ifctextliteral' in typeof(temp)])
    elif reptype.lower() == 'advancedsurface':
        count = sizeof([temp for temp in items if 'ifc4.ifcbsplinesurface' in typeof(temp)])
    elif reptype.lower() == 'annotation2d':
        count = sizeof([temp for temp in items if (sizeof(typeof(temp) * ['ifc4.ifcpoint','ifc4.ifccurve','ifc4.ifcgeometriccurveset','ifc4.ifcannotationfillarea','ifc4.ifctextliteral'])) == 1])
    elif reptype.lower() == 'geometricset':
        count = sizeof([temp for temp in items if ('ifc4.ifcgeometricset' in typeof(temp)) or ('ifc4.ifcpoint' in typeof(temp)) or ('ifc4.ifccurve' in typeof(temp)) or ('ifc4.ifcsurface' in typeof(temp))])
    elif reptype.lower() == 'geometriccurveset':
        count = sizeof([temp for temp in items if ('ifc4.ifcgeometriccurveset' in typeof(temp)) or ('ifc4.ifcgeometricset' in typeof(temp)) or ('ifc4.ifcpoint' in typeof(temp)) or ('ifc4.ifccurve' in typeof(temp))])
        for i in range(1, hiindex(items) + 1):
            if 'ifc4.ifcgeometricset' in (typeof(items[i - 1])):
                if (sizeof([temp for temp in items[i - 1].Elements if 'ifc4.ifcsurface' in typeof(temp)])) > 0:
                    count = count - 1
    elif reptype.lower() == 'tessellation':
        count = sizeof([temp for temp in items if 'ifc4.ifctessellateditem' in typeof(temp)])
    elif reptype.lower() == 'surfaceorsolidmodel':
        count = sizeof([temp for temp in items if (sizeof(['ifc4.ifctessellateditem','ifc4.ifcshellbasedsurfacemodel','ifc4.ifcfacebasedsurfacemodel','ifc4.ifcsolidmodel'] * typeof(temp))) >= 1])
    elif reptype.lower() == 'surfacemodel':
        count = sizeof([temp for temp in items if (sizeof(['ifc4.ifctessellateditem','ifc4.ifcshellbasedsurfacemodel','ifc4.ifcfacebasedsurfacemodel'] * typeof(temp))) >= 1])
    elif reptype.lower() == 'solidmodel':
        count = sizeof([temp for temp in items if 'ifc4.ifcsolidmodel' in typeof(temp)])
    elif reptype.lower() == 'sweptsolid':
        count = sizeof([temp for temp in items if ((sizeof(['ifc4.ifcextrudedareasolid','ifc4.ifcrevolvedareasolid'] * typeof(temp))) >= 1) and ((sizeof(['ifc4.ifcextrudedareasolidtapered','ifc4.ifcrevolvedareasolidtapered'] * typeof(temp))) == 0)])
    elif reptype.lower() == 'advancedsweptsolid':
        count = sizeof([temp for temp in items if (sizeof(['ifc4.ifcsweptareasolid','ifc4.ifcsweptdisksolid'] * typeof(temp))) >= 1])
    elif reptype.lower() == 'csg':
        count = sizeof([temp for temp in items if (sizeof(['ifc4.ifcbooleanresult','ifc4.ifccsgprimitive3d','ifc4.ifccsgsolid'] * typeof(temp))) >= 1])
    elif reptype.lower() == 'clipping':
        count = sizeof([temp for temp in items if (sizeof(['ifc4.ifccsgsolid','ifc4.ifcbooleanclippingresult'] * typeof(temp))) >= 1])
    elif reptype.lower() == 'brep':
        count = sizeof([temp for temp in items if 'ifc4.ifcfacetedbrep' in typeof(temp)])
    elif reptype.lower() == 'advancedbrep':
        count = sizeof([temp for temp in items if 'ifc4.ifcmanifoldsolidbrep' in typeof(temp)])
    elif reptype.lower() == 'boundingbox':
        count = sizeof([temp for temp in items if 'ifc4.ifcboundingbox' in typeof(temp)])
        if sizeof(items) > 1:
            count = 0
    elif reptype.lower() == 'sectionedspine':
        count = sizeof([temp for temp in items if 'ifc4.ifcsectionedspine' in typeof(temp)])
    elif reptype.lower() == 'lightsource':
        count = sizeof([temp for temp in items if 'ifc4.ifclightsource' in typeof(temp)])
    elif reptype.lower() == 'mappedrepresentation':
        count = sizeof([temp for temp in items if 'ifc4.ifcmappeditem' in typeof(temp)])
    else:
        return None
    return count == sizeof(items)


def IfcSurfaceWeightsPositive(b):
    result = True
    weights = b.Weights
    for i in range(0, b.UUpper + 1):
        for j in range(0, b.VUpper + 1):
            if (weights[i - 1][j - 1]) <= 0.0:
                result = False
                return result
    return result


def IfcTaperedSweptAreaProfiles(startarea, endarea):
    result = False
    if 'ifc4.ifcparameterizedprofiledef' in typeof(startarea):
        if 'ifc4.ifcderivedprofiledef' in typeof(endarea):
            result = startarea == endarea.ParentProfile
        else:
            result = typeof(startarea) == typeof(endarea)
    else:
        if 'ifc4.ifcderivedprofiledef' in typeof(endarea):
            result = startarea == endarea.ParentProfile
        else:
            result = False
    return result


def IfcTopologyRepresentationTypes(reptype, items):
    count = 0
    if reptype.lower() == 'vertex':
        count = sizeof([temp for temp in items if 'ifc4.ifcvertex' in typeof(temp)])
    elif reptype.lower() == 'edge':
        count = sizeof([temp for temp in items if 'ifc4.ifcedge' in typeof(temp)])
    elif reptype.lower() == 'path':
        count = sizeof([temp for temp in items if 'ifc4.ifcpath' in typeof(temp)])
    elif reptype.lower() == 'face':
        count = sizeof([temp for temp in items if 'ifc4.ifcface' in typeof(temp)])
    elif reptype.lower() == 'shell':
        count = sizeof([temp for temp in items if ('ifc4.ifcopenshell' in typeof(temp)) or ('ifc4.ifcclosedshell' in typeof(temp))])
    elif reptype.lower() == 'undefined':
        return True
    else:
        return None
    return count == sizeof(items)


def IfcUniqueDefinitionNames(relations):
    
    
    properties = express_set([])
    
    if sizeof(relations) == 0:
        return True
    for i in range(1, hiindex(relations) + 1):
        definition = relations[i - 1].RelatingPropertyDefinition
        if 'ifc4.ifcpropertysetdefinition' in typeof(definition):
            properties = properties + definition
        else:
            if 'ifc4.ifcpropertysetdefinitionset' in typeof(definition):
                definitionset = definition
                for j in range(1, hiindex(definitionset) + 1):
                    properties = properties + (definitionset[j - 1])
    result = IfcUniquePropertySetNames(properties)
    return result


def IfcUniquePropertyName(properties):
    names = express_set([])
    for i in range(1, hiindex(properties) + 1):
        names = names + (properties[i - 1].Name)
    return sizeof(names) == sizeof(properties)


def IfcUniquePropertySetNames(properties):
    names = express_set([])
    unnamed = 0
    for i in range(1, hiindex(properties) + 1):
        if 'ifc4.ifcpropertyset' in (typeof(properties[i - 1])):
            names = names + (properties[i - 1].Name)
        else:
            unnamed = unnamed + 1
    return (sizeof(names) + unnamed) == sizeof(properties)


def IfcUniquePropertyTemplateNames(properties):
    names = express_set([])
    for i in range(1, hiindex(properties) + 1):
        names = names + (properties[i - 1].Name)
    return sizeof(names) == sizeof(properties)


def IfcUniqueQuantityNames(properties):
    names = express_set([])
    for i in range(1, hiindex(properties) + 1):
        names = names + (properties[i - 1].Name)
    return sizeof(names) == sizeof(properties)


def IfcVectorDifference(arg1, arg2):
    
    
    
    
    if ((not exists(arg1)) or (not exists(arg2))) or (arg1.Dim != arg2.Dim):
        return None
    else:
        if 'ifc4.ifcvector' in typeof(arg1):
            mag1 = arg1.Magnitude
            vec1 = arg1.Orientation
        else:
            mag1 = 1.0
            vec1 = arg1
        if 'ifc4.ifcvector' in typeof(arg2):
            mag2 = arg2.Magnitude
            vec2 = arg2.Orientation
        else:
            mag2 = 1.0
            vec2 = arg2
        vec1 = IfcNormalise(vec1)
        vec2 = IfcNormalise(vec2)
        ndim = sizeof(vec1.DirectionRatios)
        mag = 0.0
        res = IfcDirection(DirectionRatios=([0.0] * ndim))
        for i in range(1, ndim + 1):
            temp = list(res.DirectionRatios)
            temp[i - 1] = (mag1 * (vec1.DirectionRatios[i - 1])) - (mag2 * (vec2.DirectionRatios[i - 1]))
            res.DirectionRatios = temp
            mag = mag + ((res.DirectionRatios[i - 1]) * (res.DirectionRatios[i - 1]))
        if mag > 0.0:
            result = IfcVector(Orientation=res, Magnitude=sqrt(mag))
        else:
            result = IfcVector(Orientation=vec1, Magnitude=0.0)
    return result


def IfcVectorSum(arg1, arg2):
    
    
    
    
    if ((not exists(arg1)) or (not exists(arg2))) or (arg1.Dim != arg2.Dim):
        return None
    else:
        if 'ifc4.ifcvector' in typeof(arg1):
            mag1 = arg1.Magnitude
            vec1 = arg1.Orientation
        else:
            mag1 = 1.0
            vec1 = arg1
        if 'ifc4.ifcvector' in typeof(arg2):
            mag2 = arg2.Magnitude
            vec2 = arg2.Orientation
        else:
            mag2 = 1.0
            vec2 = arg2
        vec1 = IfcNormalise(vec1)
        vec2 = IfcNormalise(vec2)
        ndim = sizeof(vec1.DirectionRatios)
        mag = 0.0
        res = IfcDirection(DirectionRatios=([0.0] * ndim))
        for i in range(1, ndim + 1):
            temp = list(res.DirectionRatios)
            temp[i - 1] = (mag1 * (vec1.DirectionRatios[i - 1])) + (mag2 * (vec2.DirectionRatios[i - 1]))
            res.DirectionRatios = temp
            mag = mag + ((res.DirectionRatios[i - 1]) * (res.DirectionRatios[i - 1]))
        if mag > 0.0:
            result = IfcVector(Orientation=res, Magnitude=sqrt(mag))
        else:
            result = IfcVector(Orientation=vec1, Magnitude=0.0)
    return result


