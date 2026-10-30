# Origin, false origin, federation

## The world

The viewer has one world, and it exists before anything is loaded. Its `0, 0, 0` is where the red and green lines cross, and they run along its X and Y. The grid lies in it too. An empty viewer shows exactly that: axes, grid, nothing else.

Loading a model puts it into that world at its own coordinates. A point the model has at `0, -2.35, 1.7` is drawn `0, -2.35, 1.7` m from the crossing. If the model carries an IfcMapConversion, its own coordinates are its map coordinates, so a building at `394221, 5812004` lands that far from the crossing, usually out of sight. Two models with different map conversions land in the same place when they describe the same site.

Nothing that follows moves a model, the axes or the grid.

## The false origin

The false origin is a point in that world. An amber survey marker shows it: a small triangle with a cross in the middle, always facing you and always the same size on screen. It is deliberately not an RGB triad, so it cannot be confused with the orbit pivot. It shows no numbers. Click it to see its world coordinates in the federation unit, grid north, and whether the point was guessed or set by you. Click it again, or anywhere else, to hide them.

The first model loaded picks one for you: the centre of its first mesh. On the sample that is about `0, -2.35, 1.7` m, so the marker sits inside the wall and shows through it. Typing your own turns the guess off and the marker moves to your point. Nothing else on screen moves.

### Why there is one at all

The GPU stores positions as 32-bit floats. Around six million metres, one float step is about half a metre, so a building drawn at its map coordinates comes out with ragged edges. To avoid that, the viewer draws everything relative to the false origin: the numbers near the building stay small and exact. The axes, the grid, the camera and section planes are converted the same way, so the shift itself is invisible. Only the survey marker tells you where it is.

Grid north is a rotation about Z, in degrees, that goes with the false origin. It turns the drawing frame, not the world: the axes still run along world X and Y.

## The federation unit

False-origin X Y Z, and a model's `b` and pivot, are all in one unit for the whole scene. The default is metres. Millimetres, centimetres, feet and inches are the same slot: changing the unit does not convert the numbers you already typed. It changes what those numbers mean.

## Several models

Adding a second file does not pick a new false origin. Every model shares the one from the first.

Each model can also have its own placement in the world:

1. Rotate it about a pivot. The pivot is in the federation unit. Rotation is degrees, X then Y then Z.
2. Slide it so that point `a` lands on point `b`.

`b` is a world point, in the federation unit. Point `a` is a point on the model:

- **global** — after the model's map conversion, in the model's map unit.
- **local** — before that conversion, in the model's own project unit.

You can set a placement before the file has finished loading. It is applied when the model arrives, so it does not jump into place afterwards.

## Scripting

Grid `origin` values are world coordinates, like everything above.

`viewer.projectWorld()`, `viewer.getCamera()` and `viewer.setCamera()` work in the drawing frame, not the world. Two helpers convert between them: `viewer.surveyPoint()` is where the survey marker is drawn (always `0, 0, 0`), and `viewer.worldOrigin()` is where world `0, 0, 0` is drawn.

The Federation card on the scripting page shows both points, and edits the unit, the false origin, and a model's placement.
