# Origin, false origin, federation

Two different points get called "the origin". They are not the same thing.

## The axes origin

The red and green lines cross at one fixed place: viewer coordinates `0, 0, 0`.

That crossing does not move. It is the ifcviewer origin, not the survey point. Models are drawn around it. The GPU stores each object's position as a 32-bit float, and a float that big is coarse: around six million metres, one step is about half a metre. Keeping the building near `0, 0, 0` is what keeps edges sharp.

## The false origin

The false origin is the survey point. A small triad marks it — the same kind of axes as the orbit pivot, shorter, with X, Y and Z. It sits at that coordinate, in metres, measured from the axes crossing, and it moves when the point changes.

A small model with no map reference still gets one. The viewer takes a point on the first model (the centre of its first mesh) and uses that. On the sample that point is about `0, -2.35, 1.7` m, so the triad sits a couple of metres off the crossing. The numbers look like ordinary model coordinates. They are. "False origin" does not mean the point is far away.

If you set the false origin to `394221, 5812004, 42` metres, the triad moves out to that survey coordinate. The building that lives there is still drawn at the crossing: the models shift by the opposite of the survey point, and the lines stay at viewer zero. That shift is what keeps the edges sharp. The triad is the survey point itself, so you can see the offset.

You can type your own. That turns the guess off. The lines stay put, the triad moves, and the models move the other way, so your point is drawn on the crossing.

Grid north is a rotation about Z, in degrees, applied with that shift. Zero means the model's X axis stays along the viewer's X axis.

## The federation unit

False-origin X Y Z, and a model's `b` and pivot, are all in one unit for the whole scene. The default is metres. Millimetres, centimetres, feet and inches are the same slot: changing the unit does not convert the numbers you already typed. It changes what those numbers mean.

## Several models

Adding a second file does not pick a new false origin. Every model shares the one from the first.

Each model can also have its own placement:

1. Rotate it about a pivot. The pivot is in the federation unit. Rotation is degrees, X then Y then Z.
2. Slide it so that point `a` lands on point `b`.

`b` is in the federation unit. Point `a` is a point on the model:

- **global** — after the model's map conversion, in the model's map unit. This is the real-world coordinate.
- **local** — before that conversion, in the model's own project unit.

A model with an IfcMapConversion already carries that conversion inside the `.ifcview`. Models with different map conversions line up because of it, and the shared false origin then brings the group back to the axes.

You can set a placement before the file has finished loading. It is applied when the model arrives, so it does not jump into place afterwards.

## What the screen shows

The tag follows the small triad. It is the false origin's numbers, in the federation unit. When the survey point moves, the tag leads with how far. If the triad is outside the view, the same line sits at the top of the canvas. The axes crossing is not labelled: it is viewer `0, 0, 0`.

The Federation card on the scripting page is where you read which of the two is which, and where you edit the unit, the false origin, and a model's placement.
