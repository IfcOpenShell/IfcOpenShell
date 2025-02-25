# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.guid
import ifcopenshell.util.stationing
import ifcopenshell.api
from ifcopenshell import entity_instance
from ifcopenshell.api.alignment import segments

import math
from typing import Sequence

import csv

def create_horizontal_alignment(
    file: ifcopenshell.file,
    name: str,
    hpoints: Sequence[Sequence[float]],
    radii: Sequence[float],
    placement: entity_instance,
    include_geometry: bool = True,
):
    """
    Create a horizontal alignment using the PI layout method.

    @param name: value for Name attribute
    @param description: value for Description attribute
    @param points: (X, Y) pairs denoting the location of the horizontal PIs, including start (POB) and end (POE).
    @param radii: radii values to use for transition
    @param placement: placement used for geometric representations if geometry is included
    @param include_geometry: optionally create the alignment geometric representation as well as the semantic business logic
    """
    horizontal_segments = list()  # business logic
    horizontal_curve_segments = list()  # geometry

    xBT, yBT = hpoints[0]
    xPI, yPI = hpoints[1]

    i = 1

    for radius in radii:
        # back tangent
        dxBT = xPI - xBT
        dyBT = yPI - yBT
        angleBT = math.atan2(dyBT, dxBT)
        lengthBT = math.sqrt(dxBT * dxBT + dyBT * dyBT)

        # forward tangent
        i += 1
        xFT, yFT = hpoints[i]
        dxFT = xFT - xPI
        dyFT = yFT - yPI
        angleFT = math.atan2(dyFT, dxFT)

        delta = angleFT - angleBT

        tangent = abs(radius * math.tan(delta / 2))

        lc = abs(radius * delta)

        radius *= delta / abs(delta)

        xPC = xPI - tangent * math.cos(angleBT)
        yPC = yPI - tangent * math.sin(angleBT)

        xPT = xPI + tangent * math.cos(angleFT)
        yPT = yPI + tangent * math.sin(angleFT)

        tangent_run = lengthBT - tangent

        # create back tangent run
        pt = file.create_entity(
            type="IfcCartesianPoint",
            Coordinates=(xBT, yBT),
        )
        design_parameters = file.create_entity(
            type="IfcAlignmentHorizontalSegment",
            StartTag=None,
            EndTag=None,
            StartPoint=pt,
            StartDirection=angleBT,
            StartRadiusOfCurvature=0.0,
            EndRadiusOfCurvature=0.0,
            SegmentLength=tangent_run,
            GravityCenterLineHeight=None,
            PredefinedType="LINE",
        )
        alignment_segment = file.create_entity(
            type="IfcAlignmentSegment",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=None,
            Name=None,
            Description=None,
            ObjectType=None,
            ObjectPlacement=None,
            Representation=None,
            DesignParameters=design_parameters,
        )
        horizontal_segments.append(alignment_segment)

        if include_geometry:
            horizontal_curve_segments.append(segments.map_alignment_horizontal_segment(file,design_parameters)[0])

        # create circular curve
        pc = file.create_entity(
            type="IfcCartesianPoint",
            Coordinates=(xPC, yPC),
        )
        design_parameters = file.create_entity(
            type="IfcAlignmentHorizontalSegment",
            StartTag=None,
            EndTag=None,
            StartPoint=pc,
            StartDirection=angleBT,
            StartRadiusOfCurvature=float(radius),
            EndRadiusOfCurvature=float(radius),
            SegmentLength=lc,
            GravityCenterLineHeight=None,
            PredefinedType="CIRCULARARC",
        )
        alignment_segment = file.create_entity(
            type="IfcAlignmentSegment",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=None,
            Name=None,
            Description=None,
            ObjectType=None,
            ObjectPlacement=None,
            Representation=None,
            DesignParameters=design_parameters,
        )
        horizontal_segments.append(alignment_segment)

        if include_geometry:
            horizontal_curve_segments.append(segments.map_alignment_horizontal_segment(file,design_parameters)[0])

        xBT = xPT
        yBT = yPT
        xPI = xFT
        yPI = yFT

    # done processing radii
    # create last tangent run
    dx = xPI - xBT
    dy = yPI - yBT
    angleBT = math.atan2(dy, dx)
    tangent_run = math.sqrt(dx * dx + dy * dy)
    pt = file.create_entity(type="IfcCartesianPoint", Coordinates=(xBT, yBT))

    design_parameters = file.create_entity(
        type="IfcAlignmentHorizontalSegment",
        StartTag=None,
        EndTag=None,
        StartPoint=pt,
        StartDirection=angleBT,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=tangent_run,
        GravityCenterLineHeight=None,
        PredefinedType="LINE",
    )
    alignment_segment = file.create_entity(
        type="IfcAlignmentSegment",
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=None,
        Name=None,
        Description=None,
        ObjectType=None,
        ObjectPlacement=None,
        Representation=None,
        DesignParameters=design_parameters,
    )
    horizontal_segments.append(alignment_segment)
    if include_geometry:
        horizontal_curve_segments.append(segments.map_alignment_horizontal_segment(file,design_parameters)[0])

    # create zero length terminator segment
    poe = file.create_entity(type="IfcCartesianPoint", Coordinates=(xPI, yPI))

    design_parameters = file.create_entity(
        type="IfcAlignmentHorizontalSegment",
        StartTag="POE",
        EndTag="POE",
        StartPoint=poe,
        StartDirection=angleBT,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=0.0,
        GravityCenterLineHeight=None,
        PredefinedType="LINE",
    )
    alignment_segment = file.create_entity(
        type="IfcAlignmentSegment",
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=None,
        Name=None,
        Description=None,
        ObjectType=None,
        ObjectPlacement=None,
        Representation=None,
        DesignParameters=design_parameters,
    )
    horizontal_segments.append(alignment_segment)
    if include_geometry:
        horizontal_curve_segments.append(segments.map_alignment_horizontal_segment(file,design_parameters)[0])

    if include_geometry:
        composite_curve = file.create_entity(
            type="IfcCompositeCurve",
            Segments=horizontal_curve_segments,
            SelfIntersect=False,
        )
    else:
        composite_curve = None


    segments.name_segments(prefix="H",segments=horizontal_segments)

    # create representations for each segment
    if include_geometry:
        segments.create_segment_representations(file,placement, horizontal_curve_segments, horizontal_segments)

    # Create the horizontal alignment (IfcAlignmentHorizontal) and nest alignment segments
    horizontal_alignment = file.create_entity(
        type="IfcAlignmentHorizontal",
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=None,
        Name=f"{name} - Horizontal",
        Description=None,
        ObjectType=None,
        ObjectPlacement=None,
        Representation=None,
    )

    nests_horizontal_segments = file.create_entity(
        type="IfcRelNests",
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=None,
        Name="Nests horizontal alignment segments under horizontal alignment",
        RelatingObject=horizontal_alignment,
        RelatedObjects=horizontal_segments,
    )

    return horizontal_alignment, composite_curve



def create_vertical_alignment(
    file: ifcopenshell.file,
    name: str,
    base_curve: entity_instance,
    vpoints: Sequence[Sequence[float]],
    lengths: Sequence[float],
    placement: entity_instance
):
    """
    Create a vertical alignment using the PI layout method.
    If a base curve is provided, geometric representation is created

    @param name: value for Name attribute
    @param base_curve: base curve representing the 2D projection of the gradient curve
    @param vpoints: (distance_along, Z_height) pairs denoting the location of the vertical PIs, including start and end.
    @param lengths: horizontal length of parabolic vertical curves
    @param placement: placement used for geometric representations if geometry is included
    """
    vertical_segments = list() # business logic
    vertical_curve_segments = list() # geometry
    xPBG, yPBG = vpoints[0]
    xPVI, yPVI = vpoints[1]
    i = 1
    for length in lengths:
        # back gradient
        dxBG = xPVI - xPBG
        dyBG = yPVI - yPBG
        start_slope = math.tan(math.atan2(dyBG,dxBG))

        #forward gradient
        i += 1
        xPFG, yPFG = vpoints[i]
        dxFG = xPFG - xPVI
        dyFG = yPFG - yPVI
        end_slope = math.tan(math.atan2(dyFG,dxFG))

        xEVC = xPVI + length/2.0
        yEVC = yPVI + end_slope * length/2.0

        # create gradient
        gradient_length = dxBG - length/2.0
        design_parameters = file.create_entity(
            type="IfcAlignmentVerticalSegment",
            StartTag=None,
            EndTag=None,
            StartDistAlong=xPBG,
            HorizontalLength=gradient_length,
            StartHeight=yPBG,
            StartGradient=start_slope,
            EndGradient=start_slope,
            RadiusOfCurvature=None,
            PredefinedType="CONSTANTGRADIENT"
        )
        alignment_segment = file.create_entity(
            type="IfcAlignmentSegment",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=None,
            Name=None,
            Description=None,
            ObjectType=None,
            ObjectPlacement=None,
            Representation=None,
            DesignParameters=design_parameters,
        )
        vertical_segments.append(alignment_segment)

        if base_curve:
            vertical_curve_segments.append(segments.map_alignment_vertical_segment(file,design_parameters)[0])

        # create vertical curve
        k = (end_slope - start_slope)/length
        xBVC = xPVI - length/2.0
        yBVC = yPVI - start_slope*length/2.0

        design_parameters = file.create_entity(
            type="IfcAlignmentVerticalSegment",
            StartTag=None,
            EndTag=None,
            StartDistAlong=xBVC,
            HorizontalLength=length,
            StartHeight=yBVC,
            StartGradient=start_slope,
            EndGradient=end_slope,
            RadiusOfCurvature=1/k,
            PredefinedType="PARABOLICARC"
        )
        alignment_segment = file.create_entity(
            type="IfcAlignmentSegment",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=None,
            Name=None,
            Description=None,
            ObjectType=None,
            ObjectPlacement=None,
            Representation=None,
            DesignParameters=design_parameters,
        )
        vertical_segments.append(alignment_segment)

        if base_curve:
            vertical_curve_segments.append(segments.map_alignment_vertical_segment(file,design_parameters)[0])            

        # start of next curve is end of this curve
        xPBG = xEVC
        yPBG = yEVC
        xPVI = xPFG
        yPVI = yPFG


    # create last gradient run
    dx = xPVI - xPBG
    dy = yPVI - yPBG
    slope = math.tan(math.atan2(dy,dx))
    gradient_length = dx

    design_parameters = file.create_entity(
        type="IfcAlignmentVerticalSegment",
        StartTag=None,
        EndTag=None,
        StartDistAlong=xPBG,
        HorizontalLength=gradient_length,
        StartHeight=yPBG,
        StartGradient=slope,
        EndGradient=slope,
        RadiusOfCurvature=None,
        PredefinedType="CONSTANTGRADIENT"
    )
    alignment_segment = file.create_entity(
        type="IfcAlignmentSegment",
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=None,
        Name=None,
        Description=None,
        ObjectType=None,
        ObjectPlacement=None,
        Representation=None,
        DesignParameters=design_parameters,
    )
    vertical_segments.append(alignment_segment)

    if base_curve:
        vertical_curve_segments.append(segments.map_alignment_vertical_segment(file,design_parameters)[0])

    # create zero length terminator segment
    design_parameters = file.create_entity(
        type="IfcAlignmentVerticalSegment",
        StartTag="VPOE",
        EndTag="VPOE",
        StartDistAlong=xPVI,
        HorizontalLength=0.0,
        StartHeight=yPVI,
        StartGradient=slope,
        EndGradient=slope,
        RadiusOfCurvature=None,
        PredefinedType="CONSTANTGRADIENT"
    )
    alignment_segment = file.create_entity(
        type="IfcAlignmentSegment",
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=None,
        Name=None,
        Description=None,
        ObjectType=None,
        ObjectPlacement=None,
        Representation=None,
        DesignParameters=design_parameters,
    )
    vertical_segments.append(alignment_segment)

    if base_curve:
        vertical_curve_segments.append(segments.map_alignment_vertical_segment(file,design_parameters)[0])

    if base_curve:
        gradient_curve = file.create_entity(
            type="IfcGradientCurve",
            Segments=vertical_curve_segments,
            SelfIntersect=False,
            BaseCurve=base_curve,
            EndPoint=None
        )
    else:
        gradient_curve = None

    segments.name_segments(prefix="V",segments=vertical_segments)

    # create representations for each segment
    if base_curve:
        segments.create_segment_representations(file, placement, vertical_curve_segments, vertical_segments)


    # Create the vertical alignment (IfcAlignmentVertical) and nest alignment segments
    vertical_alignment = file.create_entity(
        type="IfcAlignmentVertical",
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=None,
        Name=f"{name} - Vertical",
        Description=None,
        ObjectType=None,
        ObjectPlacement=None,
        Representation=None,
    )

    nests_vertical_segments = file.create_entity(
        type="IfcRelNests",
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=None,
        Name=None,
        RelatingObject=vertical_alignment,
        RelatedObjects=vertical_segments,
    )

    return vertical_alignment, gradient_curve



def set_stationing(file: ifcopenshell.file,alignment: entity_instance,basis_curve:entity_instance,start_station:float=1000.0):
    """
    Creates an IfcReferent with the Pset_Stationing property set to establish the stationing at the start of the alignment.
    Note - this function assumes the stationing has not been previously defined

    @param alignment: the alignment to be stationed
    @param basis_curve: the basis curve on which the stationing is located (typically IfcCompositeCurve)
    @para start_station: station value at the start of the alignment
    """
    # create referent for start station
    start_station_name = "Start Station ({})".format(ifcopenshell.util.stationing.station_as_string(start_station))
    start_referent = file.createIfcReferent(
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=None,
        Name=start_station_name,
        Description=None,
        ObjectType=None,
        ObjectPlacement=file.createIfcLinearPlacement(
            RelativePlacement=file.createIfcAxis2PlacementLinear(
                Location=file.createIfcPointByDistanceExpression(
                    DistanceAlong=file.createIfcLengthMeasure(0.0),
                    OffsetLateral=None,
                    OffsetVertical=None,
                    OffsetLongitudinal=None,
                    BasisCurve=basis_curve,
                ),
            ),
            CartesianPosition=None,
        ),
        Representation=None,
        PredefinedType="STATION",
    )
    pset_stationing = ifcopenshell.api.pset.add_pset(file,product=start_referent,name="Pset_Stationing")
    ifcopenshell.api.pset.edit_pset(file,pset=pset_stationing,properties={"Station":start_station})
    nesting_of_alignment = file.create_entity(
        type="IfcRelNests",
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=None,
        Name=None,
        RelatingObject=alignment,
        RelatedObjects=(start_referent,),
    )


def create_alignment_by_pi_method(
    file: ifcopenshell.file,
    alignment_name: str,
    hpoints: Sequence[Sequence[float]],
    radii: Sequence[float],
    vpoints: Sequence[Sequence[float]],
    lengths: Sequence[float],
    alignment_description: str = None,
    start_station: float = 1000.0,
    include_geometry: bool = True
):
    """
    Create an alignment using the PI layout method for both horizontal and vertical alignments.

    @param alignment_name: value for Name attribute
    @param alignment_description: value for Description attribute
    @param points: (X,Y) pairs denoting the location of the horizontal PIs, including start and end
    @param radii: radii values to use for transition
    @param vpoints: (distance_along, Z_height) pairs denoting the location of the vertical PIs, including start and end.
    @param lengths: parabolic vertical curve horizontal length values to use for transition
    @param start_station: station value at the start of the alignment
    @param include_geometry: optionally create the alignment geometric representation as well as the semantic business logic
    """

    placement = file.createIfcLocalPlacement(
        PlacementRelTo=None,
        RelativePlacement=file.createIfcAxis2Placement2D(
            Location=file.createIfcCartesianPoint(Coordinates=(0.0, 0.0))
        ),
    )

    horizontal_alignment, composite_curve = create_horizontal_alignment(file,alignment_name,hpoints,radii,placement,include_geometry)
    vertical_alignment, gradient_curve = create_vertical_alignment(file,alignment_name,composite_curve,vpoints,lengths,placement)

    # create the alignment
    alignment = file.create_entity(
        type="IfcAlignment",
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=None,
        Name=alignment_name,
        Description=alignment_description,
        ObjectType=None,
        ObjectPlacement=placement,
        Representation=None,
        PredefinedType=None,
    )

    # nest the horizontal and vertical under the alignment
    nesting_of_alignment = file.create_entity(
        type="IfcRelNests",
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=None,
        Name=None,
        RelatingObject=alignment,
        RelatedObjects=(horizontal_alignment, vertical_alignment,),
    )

    # create geometric representation
    if include_geometry:
        axis_geom_subcontext = segments.get_axis_subcontext(file)
        # create the footprint representation
        footprint_shape_representation = file.create_entity(
            type="IfcShapeRepresentation",
            ContextOfItems=axis_geom_subcontext,
            RepresentationIdentifier="FootPrint",
            RepresentationType="Curve2D",
            Items=(composite_curve,),
        )

        # create the Curve3D representation
        axis3d_shape_representation = file.create_entity(
            type="IfcShapeRepresentation",
            ContextOfItems=axis_geom_subcontext,
            RepresentationIdentifier="Axis",
            RepresentationType="Curve3D",
            Items=(gradient_curve,),
        )

        # create the alignment product definition
        product_definition_shape = file.create_entity(
            type="IfcProductDefinitionShape",
            Name="Alignment Product Definition Shape",
            Description=None,
            Representations=(footprint_shape_representation,axis3d_shape_representation,),
        )

        # add the representation to the alignment
        alignment.Representation = product_definition_shape
       
    
    set_stationing(file,alignment,composite_curve,start_station)
    
    # IFC 4.1.4.1.1 Alignment Aggregation To Project
    project = file.by_type("IfcProject")[0]
    ifcopenshell.api.aggregate.assign_object(file,products=[alignment],relating_object=project)

    return alignment


def create_horizontal_alignment_by_pi_method(
    file: ifcopenshell.file,
    name: str,
    hpoints: Sequence[Sequence[float]],
    radii: Sequence[float],
    include_geometry: bool = True,
    description: str = None,
    start_station: float = 1000.0,
):
    """
    Create a new alignment with a horizontal alignment using the PI layout method
    """
    placement = file.createIfcLocalPlacement(
        PlacementRelTo=None,
        RelativePlacement=file.createIfcAxis2Placement2D(
            Location=file.createIfcCartesianPoint(Coordinates=(0.0, 0.0))
        ),
    )

    horizontal_alignment, composite_curve = create_horizontal_alignment(
        file,
        name,
        hpoints,
        radii,
        placement,
        include_geometry,
    )

    # create the alignment
    alignment = file.create_entity(
        type="IfcAlignment",
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=None,
        Name=name,
        Description=description,
        ObjectType=None,
        ObjectPlacement=placement,
        Representation=None,
        PredefinedType=None,
    )

    # nest the horizontal under the alignment
    nesting_of_alignment = file.create_entity(
        type="IfcRelNests",
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=None,
        Name=None,
        RelatingObject=alignment,
        RelatedObjects=(horizontal_alignment,),
    )

    # create geometric representation
    if include_geometry:
        axis_geom_subcontext = segments.get_axis_subcontext(file)
        # create the footprint representation
        footprint_shape_representation = file.create_entity(
            type="IfcShapeRepresentation",
            ContextOfItems=axis_geom_subcontext,
            RepresentationIdentifier="FootPrint",
            RepresentationType="Curve2D",
            Items=(composite_curve,),
        )

        # create the alignment product definition
        product_definition_shape = file.create_entity(
            type="IfcProductDefinitionShape",
            Name="Alignment Product Definition Shape",
            Description=None,
            Representations=(footprint_shape_representation,),
        )

        # add the representation to the alignment
        alignment.Representation = product_definition_shape


    set_stationing(file,alignment,composite_curve,start_station)
    
    # IFC 4.1.4.1.1 Alignment Aggregation To Project
    project = file.by_type("IfcProject")[0]
    ifcopenshell.api.aggregate.assign_object(file,products=[alignment],relating_object=project)

    return alignment

def _move_vertical_to_child_alignment(
        file:ifcopenshell.file,
        parent_alignment: entity_instance
):
    # Find the nested IfcAlignmentVertical and remove it from the parent alignment
    alignment_vertical = None
    for rel_nests in parent_alignment.IsNestedBy:
        for related_object in rel_nests.RelatedObjects:
            if related_object.is_a().upper() == "IFCALIGNMENTVERTICAL":
                # the correct IfcRelNests has been found
                alignment_vertical = related_object
                rel_nests.RelatedObjects = tuple(set(rel_nests.RelatedObjects) - {related_object})
                break
        
        if alignment_vertical:
            break # alignment_vertical found, break from outer loop

    # Create the child IfcAlignment
    child_alignment = file.create_entity(
        type="IfcAlignment",
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=None,
        Name=f"Child of {parent_alignment.Name}",
        Description=None,
        ObjectType=None,
        ObjectPlacement=parent_alignment.ObjectPlacement,
        Representation=None,
        PredefinedType=None,
    )

    # Nest the vertical under the child alignment
    nesting_of_alignment = file.create_entity(
        type="IfcRelNests",
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=None,
        Name=None,
        RelatingObject=child_alignment,
        RelatedObjects=(alignment_vertical,),
    )

    # Aggregate the child alignment to the parent alignment
    aggregate_of_alignments = file.create_entity(
        type = "IfcRelAggregates",
        GlobalId = ifcopenshell.guid.new(),
        OwnerHistory = None,
        Name = None,
        RelatingObject=parent_alignment,
        RelatedObjects=(child_alignment,)
    )

    # If the parent_alignment has a Axis, Curve3D representation, move it to the new child alignment
    # Get the representation
    if parent_alignment.Representation:
        for representation in parent_alignment.Representation.Representations:
            if representation.RepresentationIdentifier.upper() == "AXIS" and representation.RepresentationType.upper() == "CURVE3D":
                axis3d_shape_representation = representation
                break

    if axis3d_shape_representation:
        parent_alignment.Representation.Representations = tuple(set(parent_alignment.Representation.Representations) - {axis3d_shape_representation})

        # create the child alignment product definition
        product_definition_shape = file.create_entity(
            type="IfcProductDefinitionShape",
            Name="Alignment Product Definition Shape",
            Description=None,
            Representations=(axis3d_shape_representation,),
        )

        # add the representation to the child alignment
        child_alignment.Representation = product_definition_shape



def add_vertical_alignment(
        file:ifcopenshell.file,
        alignment: entity_instance,
        vpoints: Sequence[Sequence[float]],
        lengths: Sequence[float]
        ):
    
    placement = alignment.ObjectPlacement
    composite_curve = alignment.Representation.Representations[0].Items[0]

    # determine if the alignment has child alignments
    # this would be the case if there are multiple vertical alignments
    has_children_alignments = False
    for rel_aggregates in alignment.IsDecomposedBy:
        for related_object in rel_aggregates.RelatedObjects:
            if(related_object.is_a().upper() == "IFCALIGNMENT"):
                has_children_alignments = True
                break
        
        if has_children_alignments:
            break # break from outer loop
    
    # find the horizontal alignment
    for rel_nests in alignment.IsNestedBy:
        for related_object in rel_nests.RelatedObjects:
            if related_object.is_a().upper() == "IFCALIGNMENTHORIZONTAL":
                # create the new vertical alignment
                vertical_alignment, gradient_curve = create_vertical_alignment(file,alignment.Name,composite_curve,vpoints,lengths,placement)

                # if there is only one nested object and it is IfcAlignmentHorizontal
                # and the alignment does not have aggregated children alignments
                # then nest the IfcAlignmentVertical with the same IfcRelNests
                # per CT 4.1.4.4.1.1 - Alignment Layout
                if len(rel_nests.RelatedObjects) == 1 and not has_children_alignments:
                    rel_nests.RelatedObjects += (vertical_alignment,)

                    if composite_curve:
                        axis_geom_subcontext = segments.get_axis_subcontext(file)

                        # create the Curve3D representation
                        axis3d_shape_representation = file.create_entity(
                            type="IfcShapeRepresentation",
                            ContextOfItems=axis_geom_subcontext,
                            RepresentationIdentifier="Axis",
                            RepresentationType="Curve3D",
                            Items=(gradient_curve,),
                        )

                        alignment.Representation.Representations += (axis3d_shape_representation,)

                else:
                    if not has_children_alignments:
                        _move_vertical_to_child_alignment(file,alignment)

                    # create the child alignment for the new vertical
                    child_alignment = file.create_entity(
                        type="IfcAlignment",
                        GlobalId=ifcopenshell.guid.new(),
                        OwnerHistory=None,
                        Name=f"Child of {alignment.Name}",
                        Description=None,
                        ObjectType=None,
                        ObjectPlacement=placement,
                        Representation=None,
                        PredefinedType=None,
                    )

                    # nest the vertical under the child alignment
                    nesting_of_alignment = file.create_entity(
                        type="IfcRelNests",
                        GlobalId=ifcopenshell.guid.new(),
                        OwnerHistory=None,
                        Name=None,
                        RelatingObject=child_alignment,
                        RelatedObjects=(vertical_alignment,),
                    )

                    # Add the child alignment to the parent alignment IfcRelAggregates
                    ifcopenshell.api.aggregate.assign_object(file,(child_alignment,),alignment)


                    if composite_curve:
                        axis_geom_subcontext = segments.get_axis_subcontext(file)

                        # create the Curve3D representation
                        axis3d_shape_representation = file.create_entity(
                            type="IfcShapeRepresentation",
                            ContextOfItems=axis_geom_subcontext,
                            RepresentationIdentifier="Axis",
                            RepresentationType="Curve3D",
                            Items=(gradient_curve,),
                        )

                        # create the alignment product definition
                        product_definition_shape = file.create_entity(
                            type="IfcProductDefinitionShape",
                            Name="Alignment Product Definition Shape",
                            Description=None,
                            Representations=(axis3d_shape_representation,),
                        )

                        # add the representation to the alignment
                        child_alignment.Representation = product_definition_shape




def create_alignment_from_csv(file:ifcopenshell.file,filepath:str):

    with open(filepath, newline='') as csvfile:
        reader = csv.reader(csvfile)
        row_count = 0
        for row in reader:
            data = list(map(float, row))  # Convert all values to float
            coordinates: list[list[float]] = []
            radii: list[float] = []

            row_count += 1
            
            i = 0
            while i < len(data):
                if i + 1 < len(data):
                    x,y = float(data[i]), float(data[i+1])
                    coordinates.append((x,y))  # Store (X, Y) pair
                    i += 2
                if i < len(data) and (i + 1) % 3 == 0:  # Every third element after an (X,Y) pair is R
                    radii.append(data[i])
                    i += 1
            
            if 2 == len(radii):
                radii = radii[1:]
            elif 2 < len(radii):
                radii = radii[1:-1]  # The first and last radius values are placeholders, remove them

            if row_count == 1:
                alignment = create_horizontal_alignment_by_pi_method(file,"Alignment_from_csv",coordinates,radii)
            else:
                add_vertical_alignment(file,alignment,coordinates,radii)

    return alignment