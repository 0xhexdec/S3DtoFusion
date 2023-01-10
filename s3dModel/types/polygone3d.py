from __future__ import annotations

from typing import List
from xml.dom.minidom import Element

from .point3d import Point3d
from .utils import getInt


class Polygone3d():

    numberOfPoints: int
    open: int
    symmetry: int
    symmetrieCenter: Point3d
    plan: int
    points: List[Point3d]

    def __init__(self):
        self.symmetrieCenter = Point3d()
        self.points = []


    def fromXML(self, poly: Element):
        self.numberOfPoints = getInt(poly, "Nb_of_points")
        self.open = getInt(poly, "Open")
        self.symmetry = getInt(poly, "Symmetry")
        self.plan = getInt(poly, "Plan")
        self.symmetrieCenter.fromXML(poly.getElementsByTagName("Symmetry_center")[0].childNodes[1])
        for elem in poly.getElementsByTagName("Point3d")[1:]:
            p = Point3d()
            p.fromXML(elem)
            self.points.append(p)

    def getMirrored(self, mirrorX: bool, mirrorY: bool, mirrorZ: bool) -> Polygone3d:
        mirrored = Polygone3d()
        mirrored.numberOfPoints = self.numberOfPoints
        mirrored.open = self.open
        mirrored.symmetry = self.symmetry
        mirrored.symmetrieCenter = self.symmetrieCenter.getMirrored(mirrorX, mirrorY, mirrorZ)
        mirrored.plan = self.plan
        for point in self.points:
            mirrored.points.append(point.getMirrored(mirrorX, mirrorY, mirrorZ))
        return mirrored
