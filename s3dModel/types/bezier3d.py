from __future__ import annotations

from typing import Any, List
from xml.dom.minidom import Element, Node, Text

from .enums import ControlType, TangentType
from .polygone3d import Polygone3d
from .utils import getInt, getStr


class Bezier3D():
    name: str
    degree: int
    open: int
    symmetry: int
    plan: int
    controlPoints: Polygone3d
    tangents1: Polygone3d
    tangents2: Polygone3d
    tangentsM: Polygone3d
    # controlTypes: List[ControlType]
    tangentTypes: List[TangentType]
    controlTypes: List[int]

    def __init__(self):
        self.controlPoints = Polygone3d()
        self.tangents1 = Polygone3d()
        self.tangents2 = Polygone3d()
        self.tangentsM = Polygone3d()
        self.controlTypes = []
        self.tangentTypes = []

    def fromXML(self, bezier: Element):
        self.name = getStr(bezier, "Name")
        self.degree = getInt(bezier, "Degree")
        self.open = getInt(bezier, "Open")
        self.symmetry = getInt(bezier, "Symmetry")
        self.plan = getInt(bezier, "Plan")
        self.controlPoints.fromXML(bezier.getElementsByTagName("Control_points")[0].childNodes[1])
        self.tangents1.fromXML(bezier.getElementsByTagName("Tangents_1")[0].childNodes[1])
        self.tangents2.fromXML(bezier.getElementsByTagName("Tangents_2")[0].childNodes[1])
        self.tangentsM.fromXML(bezier.getElementsByTagName("Tangents_m")[0].childNodes[1])

        for i in range(self.controlPoints.numberOfPoints):
            self.controlTypes.append(getInt(bezier, "Control_type_point_" + str(i)))
            self.tangentTypes.append(TangentType(getInt(bezier, "Tangent_type_point_" + str(i))))

    def fromXMLAndGet(self, bezier: Element) -> Bezier3D:
        self.fromXML(bezier)
        return self

    def getMirrored(self, mirrorX: bool, mirrorY: bool, mirrorZ: bool) -> Bezier3D:
        mirrored = Bezier3D()
        mirrored.name = self.name
        mirrored.degree = self.degree
        mirrored.open = self.open
        mirrored.symmetry = self.symmetry
        mirrored.plan = self.plan
        mirrored.controlPoints = self.controlPoints.getMirrored(mirrorX, mirrorY, mirrorZ)
        mirrored.tangents1 = self.tangents1.getMirrored(mirrorX, mirrorY, mirrorZ)
        mirrored.tangents2 = self.tangents2.getMirrored(mirrorX, mirrorY, mirrorZ)
        mirrored.tangentsM = self.tangentsM.getMirrored(mirrorX, mirrorY, mirrorZ)
        mirrored.controlTypes = self.controlTypes.copy()
        mirrored.tangentTypes = self.tangentTypes.copy()
        return mirrored
