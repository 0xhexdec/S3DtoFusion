from enum import Enum, auto
from typing import Union

import adsk.fusion
from adsk.fusion import Sketch


class BezierPlane(Enum):
    XY = auto()
    XZ = auto()
    YZ = auto()

def fixAllLinesInSketch(sketch: Sketch):
    # Lines
    for i in range(sketch.sketchCurves.sketchLines.count):
        sketch.sketchCurves.sketchLines.item(i).isFixed = True
    # Arcs
    for i in range(sketch.sketchCurves.sketchArcs.count):
        sketch.sketchCurves.sketchArcs.item(i).isFixed = True
    # Circles
    for i in range(sketch.sketchCurves.sketchCircles.count):
        sketch.sketchCurves.sketchCircles.item(i).isFixed = True
    # Splines
    for i in range(sketch.sketchCurves.sketchControlPointSplines.count):
        sketch.sketchCurves.sketchControlPointSplines.item(i).isFixed = True
    # Ellipses
    for i in range(sketch.sketchCurves.sketchEllipses.count):
        sketch.sketchCurves.sketchEllipses.item(i).isFixed = True
