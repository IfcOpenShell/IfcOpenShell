from dataclasses import dataclass, field

# From: src\bonsai\bonsai\bim\module\model\prop.py
# Adapted to use dataclasses instead of bpy props

@dataclass
class BIMWindowProperties:
    non_si_units_props = ("is_editing", "window_type")
    window_types = (
        ("SINGLE_PANEL", "SINGLE_PANEL", ""),
        ("DOUBLE_PANEL_HORIZONTAL", "DOUBLE_PANEL_HORIZONTAL", ""),
        ("DOUBLE_PANEL_VERTICAL", "DOUBLE_PANEL_VERTICAL", ""),
        ("TRIPLE_PANEL_BOTTOM", "TRIPLE_PANEL_BOTTOM", ""),
        ("TRIPLE_PANEL_TOP", "TRIPLE_PANEL_TOP", ""),
        ("TRIPLE_PANEL_LEFT", "TRIPLE_PANEL_LEFT", ""),
        ("TRIPLE_PANEL_RIGHT", "TRIPLE_PANEL_RIGHT", ""),
        ("TRIPLE_PANEL_HORIZONTAL", "TRIPLE_PANEL_HORIZONTAL", ""),
        ("TRIPLE_PANEL_VERTICAL", "TRIPLE_PANEL_VERTICAL", ""),
    )

    # number of panels and default mullion/transom values
    window_types_panels = {
        "SINGLE_PANEL":            (1, ((0,   0  ), (0,    0  ))),
        "DOUBLE_PANEL_HORIZONTAL": (2, ((0,   0  ), (0.45, 0  ))),
        "DOUBLE_PANEL_VERTICAL":   (2, ((0.3, 0  ), (0,    0  ))),
        "TRIPLE_PANEL_BOTTOM":     (3, ((0.3, 0  ), (0.45, 0  ))),
        "TRIPLE_PANEL_TOP":        (3, ((0.3, 0  ), (0.45, 0  ))),
        "TRIPLE_PANEL_LEFT":       (3, ((0.3, 0  ), (0.45, 0  ))),
        "TRIPLE_PANEL_RIGHT":      (3, ((0.3, 0  ), (0.45, 0  ))),
        "TRIPLE_PANEL_HORIZONTAL": (3, ((0,   0  ), (0.3,  0.6))),
        "TRIPLE_PANEL_VERTICAL":   (3, ((0.2, 0.4), (0,    0  ))),
    }

    is_editing: bool = False
    window_type: str = "SINGLE_PANEL"
    overall_height: float = 0.9
    overall_width: float = 0.6

    # lining properties
    lining_depth: float = 0.050
    lining_thickness: float = 0.050
    lining_offset: float = 0.050
    lining_to_panel_offset_x: float = 0.025
    lining_to_panel_offset_y: float = 0.025
    mullion_thickness: float = 0.050
    first_mullion_offset: float = 0.3
    second_mullion_offset: float = 0.45
    transom_thickness: float = 0.050
    first_transom_offset: float = 0.3
    second_transom_offset: float = 0.6

    # panel properties
    frame_depth: list = field(default_factory = lambda: [0.035] * 3)
    frame_thickness: list = field(default_factory = lambda: [0.035] * 3)

    def to_dict(self, si_conversion=1.):
        di = {
            "partition_type": self.window_type,
            "overall_height": self.overall_height / si_conversion,
            "overall_width": self.overall_width / si_conversion,
            "lining_properties": {
                "LiningDepth": self.lining_depth / si_conversion,
                "LiningThickness": self.lining_thickness / si_conversion,
                "LiningOffset": self.lining_offset / si_conversion,
                "LiningToPanelOffsetX": self.lining_to_panel_offset_x / si_conversion,
                "LiningToPanelOffsetY": self.lining_to_panel_offset_y / si_conversion,
                "MullionThickness": self.mullion_thickness / si_conversion,
                "FirstMullionOffset": self.first_mullion_offset / si_conversion,
                "SecondMullionOffset": self.second_mullion_offset / si_conversion,
                "TransomThickness": self.transom_thickness / si_conversion,
                "FirstTransomOffset": self.first_transom_offset / si_conversion,
                "SecondTransomOffset": self.second_transom_offset / si_conversion,
            },
            "panel_properties": [],
        }
        number_of_panels, panels_data = self.window_types_panels[self.window_type]
        for panel_i in range(number_of_panels):
            panel_data = {
                "FrameDepth": self.frame_depth[panel_i] / si_conversion,
                "FrameThickness": self.frame_thickness[panel_i] / si_conversion,
            }
            di["panel_properties"].append(panel_data)
        return di


@dataclass
class BIMDoorProperties:
    non_si_units_props = ("is_editing", "door_type", "panel_width_ratio")
    door_types = (
        ("SINGLE_SWING_LEFT", "SINGLE_SWING_LEFT", ""),
        ("SINGLE_SWING_RIGHT", "SINGLE_SWING_RIGHT", ""),
        ("DOUBLE_SWING_LEFT", "DOUBLE_SWING_LEFT", ""),
        ("DOUBLE_SWING_RIGHT", "DOUBLE_SWING_RIGHT", ""),
        ("DOUBLE_DOOR_SINGLE_SWING", "DOUBLE_DOOR_SINGLE_SWING", ""),
        ("SLIDING_TO_LEFT", "SLIDING_TO_LEFT", ""),
        ("SLIDING_TO_RIGHT", "SLIDING_TO_RIGHT", ""),
        ("DOUBLE_DOOR_SLIDING", "DOUBLE_DOOR_SLIDING", ""),
    )

    is_editing: bool = False
    door_type: str = "SINGLE_SWING_LEFT"
    overall_height: float = 2.0
    overall_width: float = 0.9

    # lining properties
    lining_depth: float = 0.050
    lining_thickness: float = 0.050
    lining_offset: float = 0.0
    lining_to_panel_offset_x: float = 0.025
    lining_to_panel_offset_y: float = 0.025
    transom_thickness: float = 0.000
    transom_offset: float = 1.525

    casing_thickness: float = 0.075
    casing_depth: float = 0.005

    threshold_thickness: float = 0.025
    threshold_depth: float = 0.1
    threshold_offset: float = 0.000

    # panel properties
    panel_depth: float = 0.035
    panel_width_ratio: float = 1.0
    frame_thickness: float = 0.035
    frame_depth: float = 0.035

    def to_dict(self, si_conversion=1.):
        return {
            "operation_type": self.door_type,
            "overall_height": self.overall_height / si_conversion,
            "overall_width": self.overall_width / si_conversion,
            "lining_properties": {
                "LiningDepth": self.lining_depth / si_conversion,
                "LiningThickness": self.lining_thickness / si_conversion,
                "LiningOffset": self.lining_offset / si_conversion,
                "LiningToPanelOffsetX": self.lining_to_panel_offset_x / si_conversion,
                "LiningToPanelOffsetY": self.lining_to_panel_offset_y / si_conversion,
                "TransomThickness": self.transom_thickness / si_conversion,
                "TransomOffset": self.transom_offset / si_conversion,
                "CasingThickness": self.casing_thickness / si_conversion,
                "CasingDepth": self.casing_depth / si_conversion,
                "ThresholdThickness": self.threshold_thickness / si_conversion,
                "ThresholdDepth": self.threshold_depth / si_conversion,
                "ThresholdOffset": self.threshold_offset / si_conversion,
            },
            "panel_properties": {
                "PanelDepth": self.panel_depth / si_conversion,
                "PanelWidth": self.panel_width_ratio,
                "FrameDepth": self.frame_depth / si_conversion,
                "FrameThickness": self.frame_thickness / si_conversion,
            },
        }
