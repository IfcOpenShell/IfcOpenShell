// This file was generated with the assistance of an AI coding tool.
import { expect, it } from 'vitest';
import * as ifcopenshell from 'ifcopenshell';
import * as geom from 'ifcopenshell/geom';
import { describeOrSkip } from '../_helper.js';

// The profile is three collinear points, which the manifold kernel cannot extrude.
const source = `ISO-10303-21;
HEADER;
FILE_DESCRIPTION((''),'2;1');
FILE_NAME('','',(),(),'','','');
FILE_SCHEMA(('IFC4'));
ENDSEC;
DATA;
#1=IFCCARTESIANPOINT((0.,0.,0.));
#2=IFCAXIS2PLACEMENT3D(#1,$,$);
#3=IFCCARTESIANPOINT((0.,0.));
#4=IFCCARTESIANPOINT((1.,0.));
#5=IFCCARTESIANPOINT((2.,0.));
#6=IFCPOLYLINE((#3,#4,#5,#3));
#7=IFCARBITRARYCLOSEDPROFILEDEF(.AREA.,$,#6);
#8=IFCDIRECTION((0.,0.,1.));
#9=IFCEXTRUDEDAREASOLID(#7,#2,#8,1.);
#10=IFCGEOMETRICREPRESENTATIONCONTEXT($,'Model',3,1.E-5,#2,$);
#11=IFCSHAPEREPRESENTATION(#10,'Body','SweptSolid',(#9));
#12=IFCPRODUCTDEFINITIONSHAPE($,$,(#11));
#13=IFCLOCALPLACEMENT($,#2);
#14=IFCBUILDINGELEMENTPROXY('0YvctVUKr0kugbFTf53O9L',$,'Degenerate',$,$,#13,#12,$,.NOTDEFINED.);
ENDSEC;
END-ISO-10303-21;`;

describeOrSkip('Iterator.getLog', () => {
  it('reports why the manifold kernel skipped an element', async () => {
    const runtime = await ifcopenshell.init();
    await runtime.loadPlugin('schema', 'ifc4');
    await runtime.loadPlugin('mapping', 'ifc4');
    await runtime.loadPlugin('kernel', 'manifold');
    using model = ifcopenshell.open(new TextEncoder().encode(source));
    using iterator = new geom.Iterator(new geom.Settings(), model, { geometryLibrary: 'manifold' });
    if (iterator.initialize()) while (iterator.next());
    expect(iterator.getLog()).toContain('Manifold kernel: failed to convert extrusion');
    expect(iterator.getLog()).toBe('');
  });
});
