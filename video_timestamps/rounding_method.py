from enum import Enum
from fractions import Fraction
from typing import Callable

__all__ = ["RoundingMethod"]


CallType = Callable[[Fraction], int]

def floor_method(ms: Fraction) -> int:
    return int(ms)

def round_method(ms: Fraction) -> int:
    return int(ms + Fraction("0.5"))

class RoundingMethod(Enum):
    FLOOR: CallType = floor_method
    ROUND: CallType = round_method

    def __call__(self, ms: Fraction) -> int:
        method: CallType = self.value
        return method(ms)
