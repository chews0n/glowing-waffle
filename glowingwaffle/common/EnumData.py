from enum import Enum


class Features(Enum):
    WELL_LENGTH = 1
    FLUID_PER_METER = 2


class Targets(Enum):
    IP90 = 1
    IP180 = 2
