from typing import Dict, List

import adsk.core
import adsk.fusion
from adsk.fusion import ConstructionPlane, Sketch

from ...s3dModel.types.bezierDef import BezierDef
from ..converterSettings import ConverterSettings
from ..typeConverter.bezierToSketch import bezier2dToSketch
from ..typeConverter.utils import BezierPlane, fixAllLinesInSketch


def convert(comp: adsk.fusion.Component, outlinePlane: ConstructionPlane, rockerPlane: ConstructionPlane, tops: Dict[str, BezierDef], sides: Dict[str, BezierDef], settings: ConverterSettings):

    for key, value in tops.items():
        sketch: Sketch = comp.sketches.add(outlinePlane)
        sketch.name = f"{key} (Top)" if (value.bezier3d.name == "" or value.bezier3d.name is None) else f"{value.bezier3d.name} (Top)"
        if settings.flipOutline:
            line = value.bezier3d.getMirrored(False, True, False)
        else:
            line = value.bezier3d
        bezier2dToSketch(sketch, line, BezierPlane.XY, settings)

        if settings.fixedPoints:
            for i in range(sketch.sketchPoints.count):
                sketch.sketchPoints.item(i).isFixed = True
            
        if settings.fixedLines:
            fixAllLinesInSketch(sketch)

    for key, value in sides.items():
        sketch: Sketch = comp.sketches.add(rockerPlane)
        sketch.name = f"{key} (Side)" if (value.bezier3d.name == "" or value.bezier3d.name is None) else f"{value.bezier3d.name} (Side)"
        bezier2dToSketch(sketch, value.bezier3d, BezierPlane.XZ, settings)

        if settings.fixedPoints:
            for i in range(sketch.sketchPoints.count):
                sketch.sketchPoints.item(i).isFixed = True
            
        if settings.fixedLines:
            fixAllLinesInSketch(sketch)
