from enum import Enum


# TODO find out what the controlType is and migrate to enum style
class ControlType(Enum):
    A = 1
    B = 2
    C = 4
    D = 8
    E = 16
    F = 32

class TangentType(Enum):
    ANGULOUS = 0
    CONTINUOUS = 2
    VERTICAL = 16
    HORIZONTAL = 32
    FIXED_ANGLE = 64
    PASSIVE = 128
    CONTINUOUS_C2 = 258
    VERTICAL_C2 = 272
    HORIZONTAL_C2 = 288
    FIXED_ANGLE_C2 = 320
    UNDEFINED = -1

    @classmethod
    def _missing_(cls, value):
        return cls.UNDEFINED
