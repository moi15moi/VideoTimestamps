from .abc_timestamps import ABCTimestamps
from .rounding_method import RoundingMethod
from .time_type import TimeType
from decimal import Decimal
from fractions import Fraction
from math import ceil, floor
from typing import Any, Optional, Union

__all__ = ["FPSTimestamps"]


class FPSTimestamps(ABCTimestamps):

    def __init__(
        self,
        rounding_method: RoundingMethod,
        timescale: Fraction,
        fps: Union[int, float, Fraction, Decimal],
    ):
        self.__rounding_method = rounding_method
        self.__timescale = timescale
        self.__fps = Fraction(fps)


    @property
    def rounding_method(self) -> RoundingMethod:
        return self.__rounding_method

    @property
    def timescale(self) -> Fraction:
        return self.__timescale

    @timescale.setter
    def timescale(self, value: Any) -> None:
        raise AttributeError("You cannot change the value of timescale")

    @property
    def timestamps(self) -> list[int]:
        return []

    @property
    def fps(self) -> Fraction:
        return self.__fps


    def time_to_frame(
        self,
        time: Union[int, Fraction],
        time_type: TimeType,
        input_unit: Optional[int] = None,
    ) -> int:

        if input_unit is None:
            if not isinstance(time, Fraction):
                raise ValueError("If input_unit is none, the time needs to be a Fraction.")
            time_in_second = time
        else:
            if not isinstance(time, int):
                raise ValueError("If you specify a input_unit, the time needs to be a int.")

            time_in_second = time * Fraction(1, 10 ** input_unit)

        if time_type == TimeType.START:
            if self.rounding_method == RoundingMethod.ROUND:
                frame = ceil((ceil(time_in_second * self.timescale) - Fraction(1, 2)) * self.fps / self.timescale + Fraction(1, 1)) - 1
            elif self.rounding_method == RoundingMethod.FLOOR:
                frame = ceil(ceil(time_in_second * self.timescale) * self.fps / self.timescale + Fraction(1, 1)) - 1
        elif time_type == TimeType.END:
            if time == 0:
                # TODO changer le 0 pour le premier timstamps self.timestamps[0]
                raise ValueError(f'You cannot specify a time equals to the first timestamps {0} with the TimeType.END.')

            if self.rounding_method == RoundingMethod.ROUND:
                frame = ceil((ceil(time_in_second * self.timescale) - Fraction(1, 2)) * self.fps/self.timescale) - 1
            elif self.rounding_method == RoundingMethod.FLOOR:
                frame = ceil(ceil(time_in_second * self.timescale) * self.fps/self.timescale) - 1
        elif time_type == TimeType.EXACT:
            if self.rounding_method == RoundingMethod.ROUND:
                frame = ceil((floor(time_in_second * self.timescale) + Fraction(1, 2)) * self.fps/self.timescale) - 1
            elif self.rounding_method == RoundingMethod.FLOOR:
                frame = ceil((floor(time_in_second * self.timescale) + Fraction(1)) * self.fps/self.timescale) - 1

        return frame


    def frame_to_time(
        self,
        frame: int,
        time_type: TimeType,
        output_unit: Optional[int] = None,
        center_time: Optional[bool] = False,
    ) -> Union[int, Fraction]:

        if output_unit is not None and output_unit < 0:
            raise ValueError("The output_unit needs to be above or equal to 0.")

        if frame < 0:
            raise ValueError("You cannot specify a frame under 0.")

        if time_type == TimeType.START:
            if frame == 0:
                return 0

            upper_bound = self.rounding_method(frame * self.timescale/self.fps) * 1/self.timescale

            if center_time:
                lower_bound = self.rounding_method((frame-1) * self.timescale/self.fps) * 1/self.timescale
                time = (lower_bound + upper_bound) / 2
            else:
                time = upper_bound

        elif time_type == TimeType.END:
            upper_bound = self.rounding_method((frame+1) * self.timescale/self.fps) * 1/self.timescale

            if center_time:
                lower_bound = self.rounding_method(frame * self.timescale/self.fps) * 1/self.timescale
                time = (lower_bound + upper_bound) / 2
            else:
                time = upper_bound

        elif time_type == TimeType.EXACT:
            time = self.rounding_method(frame * self.timescale/self.fps) * 1/self.timescale

            if center_time:
                raise ValueError("It doesn't make sense to use the time in the center of two frame for TimeType.EXACT.")

        else:
            raise ValueError(f'The TimeType "{time_type}" isn\'t supported.')


        if output_unit is None:
            return time

        if time_type == TimeType.EXACT:
            return ceil(time * 10 ** output_unit)
        elif center_time:
            return RoundingMethod.ROUND(time * 10 ** output_unit)
        else:
            return floor(time * 10 ** output_unit)
