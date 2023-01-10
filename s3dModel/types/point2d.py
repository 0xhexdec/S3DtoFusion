from xml.dom.minidom import Element

from .utils import getFloat, getInt


class Point2d():

    x: float
    y: float
    color: int

    def __init__(self):
        pass

    def fromXML(self, point2d: Element):
        self.x = getFloat(point2d, "x")
        self.y = getFloat(point2d, "y")
        self.color = getInt(point2d, "color")
