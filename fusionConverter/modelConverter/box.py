from typing import List

import adsk.core
import adsk.fusion
from adsk.fusion import ConstructionPlane

from ...s3dModel.types.box import Box
from ..converterSettings import ConverterSettings
from ..typeConverter.bezierToSketch import bezier2dToSketch
from ..typeConverter.lines import ellipse, pointsToLine, rectangle
from ..typeConverter.utils import BezierPlane, fixAllLinesInSketch


def convertEasy(comp: adsk.fusion.Component, outlinePlane: ConstructionPlane, boxes: List[Box], settings: ConverterSettings):
    sketch: adsk.fusion.Sketch = comp.sketches.add(outlinePlane)  # type: ignore
    sketch.name = "Boxes"
    for box in boxes:
        if box.style2 == 0: # change to enum, this is a rectangle
            rectangle(sketch, box.pointReference, box.length, box.width, box.cornerRadius)
            if box.even:
                rectangle(sketch, box.pointReference.getMirrored(False, True, False), box.length, box.width, box.cornerRadius)
        elif box.style2 == 23: # Cylinder
            ellipse(sketch, box.pointCenter, box.length, box.width)
            if box.even:
                ellipse(sketch, box.pointReference.getMirrored(False, True, False), box.length, box.width)
        else:
            rectangle(sketch, box.pointReference, box.length, box.width)
            if box.even:
                rectangle(sketch, box.pointReference.getMirrored(False, True, False), box.length, box.width)

    if settings.fixedPoints:
        for i in range(sketch.sketchPoints.count):
            sketch.sketchPoints.item(i).isFixed = True

    if settings.fixedLines:
        fixAllLinesInSketch(sketch)


def convert(comp: adsk.fusion.Component, basePlane: ConstructionPlane, box: Box, settings: ConverterSettings):
    # TODO create construction Plane tangent to surface and put the Box on that plane
    raise NotImplementedError()
