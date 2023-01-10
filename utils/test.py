import adsk.core
import adsk.fusion

from .measure import distance


def printPoint(point: adsk.fusion.SketchPoint):
    print(f"X:{point.geometry.x} Y:{point.geometry.y} Z:{point.geometry.z}")

def test():
    app: adsk.core.Application = adsk.core.Application.get()
    ui: adsk.core.UserInterface = app.userInterface
    comp = adsk.fusion.Design.cast(app.activeProduct).rootComponent
    # for name in ["Rail 3D", "Deck 1 3D", "Apex 3D"]:
    #     copySketch(name)
    # for name in ["Copy of Rail 3D", "Copy of Deck 1 3D", "Copy of Apex 3D"]:
        # sketch = comp.sketches.itemByName(name)
        # print(str(sketch.sketchCurves.sketchControlPointSplines.count))
        # # for id in range(sketch.sketchCurves.sketchControlPointSplines.count -1, -1, -1):
        # #     sketch.sketchCurves.sketchControlPointSplines[id].deleteMe()
        # for spline in sketch.sketchCurves.sketchControlPointSplines:
        #     print(name + " -> " + ("Normal" if spline.startSketchPoint.geometry.x < spline.endSketchPoint.geometry.x else "Reversed"))
    
    # do this for every "pair" of splines
    # for i in range(sketch.sketchCurves.sketchControlPointSplines.count - 1):
    #     spline1 = sketch.sketchCurves.sketchControlPointSplines[i]
    #     spline2 = sketch.sketchCurves.sketchControlPointSplines[i+1]
    #     # set the startpoint to the endpoint of the last
    #     spline2.startSketchPoint.geometry.x = spline1.endSketchPoint.geometry.x
    #     spline2.startSketchPoint.geometry.y = spline1.endSketchPoint.geometry.y
    #     spline2.startSketchPoint.geometry.z = spline1.endSketchPoint.geometry.z


    # zeroIndex = [0, 12, 23, sketch.sketchCurves.sketchControlPointSplines.count]
    # for zi in range(len(zeroIndex)-1):
    #     for i in range(zeroIndex[zi], zeroIndex[zi+1]):
    #         spline1 = sketch.sketchCurves.sketchControlPointSplines[i]
    #         # spline2 = sketch.sketchCurves.sketchControlPointSplines[i+1]
    #         # points = []
    #         # points.append(spline1.controlPoints[len(spline1.controlPoints)-1].geometry)
    #         # points.append(spline1.controlPoints[len(spline1.controlPoints)-2].geometry)
    #         # print(distance(spline2.controlPoints[1].geometry, points))
    #         # input1: adsk.fusion.ConstructionAxisInput = comp.constructionAxes.createInput()
    #         # input1.setByTwoPoints(spline1.controlPoints[len(spline1.controlPoints)-1], spline1.controlPoints[len(spline1.controlPoints)-2])
    #         # comp.constructionAxes.add(input1)

    #         input2: adsk.fusion.ConstructionPointInput = comp.constructionPoints.createInput()
    #         # input2.setByPoint(spline1.controlPoints[0])
    #         input2.setByPoint(spline1.startSketchPoint)
    #         cp = comp.constructionPoints.add(input2)
    #         cp.name = str(i)

    sketch = comp.sketches.itemByName("Copy of Rail 3D")
    print(sketch.sketchCurves.sketchLines.count)

    # getting the last splineLine of a spline
    # easy approach
    constraints = sketch.geometricConstraints
    lineIndex = -1
    for i in range(sketch.sketchCurves.sketchControlPointSplines.count - 1):
        lineIndex += len(sketch.sketchCurves.sketchControlPointSplines[i].controlPoints) - 1
        # sketch.sketchCurves.sketchLines[lineIndex].isFixed = False
        constraints.addCollinear(sketch.sketchCurves.sketchLines[lineIndex], sketch.sketchCurves.sketchLines[lineIndex + 1])



def copySketch(name: str):
    app: adsk.core.Application = adsk.core.Application.get()
    ui: adsk.core.UserInterface = app.userInterface
    comp = adsk.fusion.Design.cast(app.activeProduct).rootComponent
    sketch = comp.sketches.itemByName(name)
    print(sketch.sketchCurves.sketchControlPointSplines.count)
    # duplicate sketch
    copy: adsk.fusion.Sketch = comp.sketches.add(comp.xYConstructionPlane)  # type: ignore
    copy.name = "Copy of " + sketch.name
    for spline in sketch.sketchCurves.sketchControlPointSplines:
        points = []
        for point in spline.controlPoints:
            points.append(adsk.core.Point3D.create(point.geometry.x, point.geometry.y, point.geometry.z))
        copy.sketchCurves.sketchControlPointSplines.add(points, 3)  # type: ignore
