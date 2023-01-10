from __future__ import annotations

from xml.dom.minidom import Element

from .utils import getFloat, getInt


class Point3d():

    x: float
    y: float
    z: float
    u: float
    color: int

    def __init__(self):
        pass

    def fromXML(self, point3d: Element):
        self.x = getFloat(point3d, "x")
        self.y = getFloat(point3d, "y")
        self.z = getFloat(point3d, "z")
        self.u = getFloat(point3d, "u")
        self.color = getInt(point3d, "color")

    @staticmethod
    def new(x, y, z):
        p = Point3d()
        p.x = x
        p.y = y
        p.z = z
        return p

    def getMirrored(self, mirrorX: bool, mirrorY: bool, mirrorZ: bool) -> Point3d:
        mirrored = Point3d()
        mirrored.u = self.u
        mirrored.color = self.color
        mirrored.x = -self.x if mirrorX else self.x
        mirrored.y = -self.y if mirrorY else self.y
        mirrored.z = -self.z if mirrorZ else self.z
        return mirrored
