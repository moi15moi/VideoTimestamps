from collections.abc import Callable
from enum import Enum
from fractions import Fraction
from math import ceil, floor

__all__ = ["RoundingMethod"]


RoundingCallType = Callable[[Fraction], int]

def floor_method(number: Fraction) -> int:
    return floor(number)

def round_method(number: Fraction) -> int:
    if number >= 0:
        return floor(number + Fraction(1, 2))
    else:
        return ceil(number - Fraction(1, 2))

class RoundingMethod(Enum):
    """Method used to adjust presentation timestamps (PTS).
    """
    FLOOR = floor_method
    """Floor"""

    ROUND = round_method
    """Round half up"""

    def __call__(self, number: Fraction) -> int:
        method: RoundingCallType = self.value
        return method(number)
