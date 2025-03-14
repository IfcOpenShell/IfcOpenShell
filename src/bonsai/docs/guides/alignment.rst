Road and Rail Alignments
========================

.. Note::

    Bonsai lacks modeling features for road and rail alignments. This feature is intended to be a stop-gap measure to allow alignments
    to be defined and imported into an IFC model. This feature is most likely temporary and will be phased out as robust alignment
    modeling capabilities are developed.

Alignments may be defined by the PI method in a CSV file for import into an IFC4X3 Bonsai project. The format of the CSV file is as follows:

.. csv-table:: Alignment by PI Method

   "X1","Y1","R1","X2","Y2","R2","...,","Xn-1","Yn-1","Rn-1","Xn","Yn","Rn"
   "D1","Z1","L1","D2","Z2","L2","...,","Dn-1","Zn-1","Ln-1","Dn","Zn","Ln"
   "D1","Z1","L1","D2","Z2","L2","...,","Dn-1","Zn-1","Ln-1","Dn","Zn","Ln"
   
   
where:
   Xi,Yi are horizontal alignment PI points
   Ri are horizontal curve radii.
   Di,Zi are vertical alignment PI points as Distance_Along,Elevation
   Li are the horizontal length of parabolic vertical transition curves
   
R1 and Rn, as well as L1 and Ln, are placeholder values and should be set to 0.0

The CSV file must contain exactly one horizontal alignment definition with a minimum of three points.
X1,Y1 is the Point of Beginning (POB). Xn,Yn is the Point of Ending (POE).

The CSV file may contain zero, one or more vertical alignment definitions.

Alignments with a single horizontal layout and zero or one vertical layout are modeled per `IFC Concept Template 4.1.4.4.1.1, Alignment Layout - Horizontal, Vertical, and Cant, <https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Object_Composition/Nesting/Alignment_Layouts/Alignment_Layout_-_Horizontal,_Vertical_and_Cant/content.html>`_. Alignments with multiple vertical layouts are modeled per `IFC Concept Template 4.1.4.4.1.2, Alignment Layout - Reusing Horizontal Layout, <https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Object_Composition/Nesting/Alignment_Layouts/Alignment_Layout_-_Reusing_Horizontal_Layout/content.html>`_.

Example based on the `FHWA Bridge Geometry Manual <https://www.fhwa.dot.gov/bridge/pubs/hif22034.pdf>`_:

500,2500,0.0,3340,660,1000,4340,5000,1250,7600,4560,950,8480,2010,0
0,100,0,2000,135,1600,5000,105,1200,7400,153,2000,9800,105,800,12800,90,0