// This file was generated with the assistance of an AI coding tool.
import { expect, it } from 'vitest';
import * as ifcopenshell from 'ifcopenshell';
import * as geom from 'ifcopenshell/geom';
import { describeOrSkip } from '../_helper.js';

describeOrSkip('createShape', () => {
  it.each(['opencascade', 'manifold'])('creates the same triangulation as the %s iterator', async (kernel) => {
    const runtime = await ifcopenshell.init();
    await runtime.loadPlugin('schema', 'ifc4');
    await runtime.loadPlugin('mapping', 'ifc4');
    await runtime.loadPlugin('kernel', kernel);
    const source = `ISO-10303-21;
HEADER;
FILE_DESCRIPTION((''),'2;1');
FILE_NAME('','',(),(),'','','');
FILE_SCHEMA(('IFC4'));
ENDSEC;
DATA;
#1=IFCCARTESIANPOINT((0.,0.,0.));
#2=IFCAXIS2PLACEMENT3D(#1,$,$);
#3=IFCRECTANGLEPROFILEDEF(.AREA.,$,$,1.,1.);
#4=IFCDIRECTION((0.,0.,1.));
#5=IFCEXTRUDEDAREASOLID(#3,#2,#4,1.);
#6=IFCGEOMETRICREPRESENTATIONCONTEXT($,'Model',3,1.E-5,#2,$);
#7=IFCSHAPEREPRESENTATION(#6,'Body','SweptSolid',(#5));
#8=IFCPRODUCTDEFINITIONSHAPE($,$,(#7));
#9=IFCLOCALPLACEMENT($,#2);
#10=IFCBUILDINGELEMENTPROXY('0YvctVUKr0kugbFTf53O9L',$,'Box',$,$,#9,#8,$,.NOTDEFINED.);
ENDSEC;
END-ISO-10303-21;`;
    const model = ifcopenshell.open(new TextEncoder().encode(source));
    const product = model.byId(10)!;
    const settings = new geom.Settings();
    settings.set('weld-vertices', false);
    const shape = geom.createShape(settings, product, undefined, kernel)!;
    const triangulation = shape.asTriangulationElement()!;
    const geometry = triangulation.geometry();
    expect(geometry.facesBuffer(Uint32Array).length).toBe(36);
    using iterator = new geom.Iterator(settings, model, { geometryLibrary: kernel });
    expect(iterator.initialize()).toBe(true);
    const iterated = iterator.get()!;
    const iteratedTriangulation = iterated.asTriangulationElement()!;
    const iteratedGeometry = iteratedTriangulation.geometry();
    expect(iteratedGeometry.vertsBuffer(Float32Array)).toEqual(geometry.vertsBuffer(Float32Array));
    expect(iterator.next()).toBe(false);
  });
});
