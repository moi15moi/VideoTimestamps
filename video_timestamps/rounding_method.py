from enum import Enum
from fractions import Fraction
from math import ceil, floor
from typing import Callable

__all__ = ["RoundingMethod"]


CallType = Callable[[Fraction], int]

def floor_method(number: Fraction) -> int:
    return floor(number)

def round_method(number: Fraction) -> int:
    if number >= 0:
        return floor(number + Fraction(1, 2))
    else:
        return ceil(number - Fraction(1, 2))

class RoundingMethod(Enum):
    FLOOR = floor_method
    ROUND = round_method

    def __call__(self, number: Fraction) -> int:
        method: CallType = self.value
        return method(number)
