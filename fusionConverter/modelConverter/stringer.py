import adsk.core
import adsk.fusion
from adsk.fusion import ConstructionPlane, Sketch

from ...s3dModel.types.bezier3d import Bezier3D
from ..converterSettings import ConverterSettings
from ..typeConverter.bezierToSketch import bezier2dToSketch
from ..typeConverter.lines import pointsToLine
from ..typeConverter.utils import BezierPlane, fixAllLinesInSketch


def convert(comp: adsk.fusion.Component, stringerPlane: ConstructionPlane, stringerDeck: Bezier3D, stringerBottom: Bezier3D, settings: ConverterSettings):
    # create sketch on plane
    stringerSketch: Sketch = comp.sketches.add(stringerPlane)
    stringerSketch.name = "Stringer"
    bezier2dToSketch(stringerSketch, stringerDeck, BezierPlane.XZ, settings)
    bezier2dToSketch(stringerSketch, stringerBottom, BezierPlane.XZ, settings)
    if settings.closedStringer:
        pointsToLine(stringerSketch, stringerDeck.controlPoints.points[0], stringerBottom.controlPoints.points[0], BezierPlane.XZ, settings)
        nbOfDeckPoints = stringerDeck.controlPoints.numberOfPoints - 1
        nbOfBotPoints = stringerBottom.controlPoints.numberOfPoints - 1
        pointsToLine(stringerSketch, stringerDeck.controlPoints.points[nbOfDeckPoints], stringerBottom.controlPoints.points[nbOfBotPoints], BezierPlane.XZ, settings)

    if settings.fixedPoints:
        for i in range(stringerSketch.sketchPoints.count):
            stringerSketch.sketchPoints.item(i).isFixed = True
    
    if settings.fixedLines:
        fixAllLinesInSketch(stringerSketch)
