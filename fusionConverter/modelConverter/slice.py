
import adsk.core
import adsk.fusion
from adsk.fusion import ConstructionPlane

from ...s3dModel.types.slice import Slice
from ..converterSettings import ConverterSettings
from ..typeConverter.bezierToSketch import bezier2dToSketch
from ..typeConverter.lines import pointsToLine
from ..typeConverter.utils import BezierPlane, fixAllLinesInSketch


def convert(comp: adsk.fusion.Component, tailPlane: ConstructionPlane, slice: Slice, name: str, settings: ConverterSettings):
    # tail slice does not neet a new construction plane
    distance = slice.bezier.controlPoints.points[0].x
    if distance == 0:
        plane = tailPlane
    else:
        planeInput: adsk.fusion.ConstructionPlaneInput = comp.constructionPlanes.createInput()
        planeInput.setByOffset(tailPlane, adsk.core.ValueInput.createByReal(distance))
        plane = comp.constructionPlanes.add(planeInput)
        plane.name = f"{name} (Construction Plane)"
    sliceSketch: adsk.fusion.Sketch = comp.sketches.add(plane)
    sliceSketch.name = name
    if settings.mirrorSlices:
        bezier2dToSketch(sliceSketch, slice.bezier.getMirrored(False, True, False), BezierPlane.YZ, settings)
    bezier2dToSketch(sliceSketch, slice.bezier, BezierPlane.YZ, settings)

    if settings.closedSlices:
        nbOPoints = slice.bezier.controlPoints.numberOfPoints - 1
        pointsToLine(sliceSketch, slice.bezier.controlPoints.points[0], slice.bezier.controlPoints.points[nbOPoints], BezierPlane.YZ, settings)

    if settings.fixedPoints:
        for i in range(sliceSketch.sketchPoints.count):
            sliceSketch.sketchPoints.item(i).isFixed = True
        
    if settings.fixedLines:
        fixAllLinesInSketch(sliceSketch)
