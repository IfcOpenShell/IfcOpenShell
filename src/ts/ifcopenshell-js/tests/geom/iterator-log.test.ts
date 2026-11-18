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
#15=IFCRECTANGLEPROFILEDEF(.AREA.,$,$,1.,1.);
#16=IFCEXTRUDEDAREASOLID(#15,#2,#8,1.);
#17=IFCSHAPEREPRESENTATION(#10,'Body','SweptSolid',(#16));
#18=IFCPRODUCTDEFINITIONSHAPE($,$,(#17));
#19=IFCBUILDINGELEMENTPROXY('0YvctVUKr0kugbFTf53O9M',$,'Valid',$,$,#13,#18,$,.NOTDEFINED.);
#20=IFCEXTRUDEDAREASOLID(#7,#2,#8,2.);
#21=IFCSHAPEREPRESENTATION(#10,'Body','SweptSolid',(#20));
#22=IFCPRODUCTDEFINITIONSHAPE($,$,(#21));
#23=IFCBUILDINGELEMENTPROXY('0YvctVUKr0kugbFTf53O9N',$,'Degenerate',$,$,#13,#22,$,.NOTDEFINED.);
#24=IFCEXTRUDEDAREASOLID(#15,#2,#8,2.);
#25=IFCSHAPEREPRESENTATION(#10,'Body','SweptSolid',(#24));
#26=IFCPRODUCTDEFINITIONSHAPE($,$,(#25));
#27=IFCBUILDINGELEMENTPROXY('0YvctVUKr0kugbFTf53O9O',$,'Valid',$,$,#13,#26,$,.NOTDEFINED.);
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
    expect(iterator.initialize()).toBe(true);
    while (iterator.next());
    const entries: geom.IteratorLogEntry[] = iterator.getLog();
    expect(entries).toEqual(expect.arrayContaining([
      expect.objectContaining({
        level: 'warning',
        message: expect.stringContaining('Manifold kernel: failed to convert extrusion'),
        time: expect.any(String),
        product: expect.stringContaining("'Degenerate'"),
      }),
    ]));
    expect(iterator.getLog()).toEqual(entries);
  });

  it.each([undefined, [14, 19, 23, 27], ['IfcBuildingElementProxy']])(
    'keeps interleaved iterators isolated with include %j',
    async (include) => {
      const runtime = await ifcopenshell.init();
      await runtime.loadPlugin('schema', 'ifc4');
      await runtime.loadPlugin('mapping', 'ifc4');
      await runtime.loadPlugin('kernel', 'manifold');
      using firstModel = ifcopenshell.open(new TextEncoder().encode(source.replaceAll('Degenerate', 'First "job"')));
      using secondModel = ifcopenshell.open(new TextEncoder().encode(source.replaceAll('Degenerate', 'Second job')));
      using first = new geom.Iterator(new geom.Settings(), firstModel, { geometryLibrary: 'manifold', include });
      using second = new geom.Iterator(new geom.Settings(), secondModel, { geometryLibrary: 'manifold', include });
      expect(first.initialize()).toBe(true);
      expect(second.initialize()).toBe(true);
      const firstIds = [first.get()!.id()];
      const secondIds = [second.get()!.id()];
      let firstActive = true;
      let secondActive = true;
      while (firstActive || secondActive) {
        if (firstActive) {
          firstActive = first.next();
          if (firstActive) firstIds.push(first.get()!.id());
        }
        if (secondActive) {
          secondActive = second.next();
          if (secondActive) secondIds.push(second.get()!.id());
        }
      }
      expect(firstIds.sort((a, b) => a - b)).toEqual([19, 27]);
      expect(secondIds.sort((a, b) => a - b)).toEqual([19, 27]);
      const firstEntries = first.getLog();
      const secondEntries = second.getLog();
      for (const [entries, ownName, otherName] of [
        [firstEntries, 'First "job"', 'Second job'],
        [secondEntries, 'Second job', 'First "job"'],
      ] as const) {
        const warnings = entries.filter(entry => entry.message.includes('Manifold kernel: failed to convert extrusion'));
        expect(warnings).toHaveLength(2);
        expect(warnings.every(entry => entry.product?.includes(ownName))).toBe(true);
        expect(entries.every(entry => !entry.product?.includes(otherName))).toBe(true);
      }
      runtime.raw.parse.getLog();
      expect(first.getLog()).toEqual(firstEntries);
      expect(second.getLog()).toEqual(secondEntries);
    },
  );
});
