from .abc_timestamps import ABCTimestamps
from .rounding_method import RoundingMethod
from .time_type import TimeType
from decimal import Decimal
from fractions import Fraction
from math import ceil, floor
from typing import Union

__all__ = ["FPSTimestamps"]


class FPSTimestamps(ABCTimestamps):
    """Create a Timestamps object from a fps.

    See `ABCTimestamps` for more details.

    Attributes:
        rounding_method (RoundingMethod): The rounding method used to round/floor the PTS (Presentation Time Stamp).
        time_scale (Fraction): Unit of time (in seconds) in terms of which frame timestamps are represented.
            Important: Don't confuse time_scale with the time_base. As a reminder, time_base = 1 / time_scale.
        fps (Fraction): The frames per second of the video.
        first_pts (int): PTS (Presentation Time Stamp) of the first frame of the video.
        first_timestamps (int): Time (in seconds) of the first frame of the video.
    """

    def __init__(
        self,
        rounding_method: RoundingMethod,
        time_scale: Fraction,
        fps: Union[int, float, Fraction, Decimal],
        first_pts: int = 0
    ):
        if time_scale <= 0:
            raise ValueError("Parameter ``time_scale`` must be higher than 0.")

        if fps <= 0:
            raise ValueError("Parameter ``fps`` must be higher than 0.")

        self.__rounding_method = rounding_method
        self.__time_scale = time_scale
        self.__fps = Fraction(fps)
        self.__first_pts = first_pts
        self.__first_timestamps = self.first_pts / self.time_scale

    @property
    def rounding_method(self) -> RoundingMethod:
        return self.__rounding_method

    @property
    def fps(self) -> Fraction:
        return self.__fps

    @property
    def time_scale(self) -> Fraction:
        return self.__time_scale

    @property
    def first_pts(self) -> int:
        return self.__first_pts

    @property
    def first_timestamps(self) -> Fraction:
        return self.__first_timestamps


    def _time_to_frame(
        self,
        time: Fraction,
        time_type: TimeType,
    ) -> int:

        if time_type == TimeType.START:
            if self.rounding_method == RoundingMethod.ROUND:
                frame = ceil((ceil((time - self.first_timestamps) * self.time_scale) - Fraction(1, 2)) * self.fps / self.time_scale + Fraction(1, 1)) - 1
            elif self.rounding_method == RoundingMethod.FLOOR:
                frame = ceil(ceil((time - self.first_timestamps) * self.time_scale) * self.fps / self.time_scale + Fraction(1, 1)) - 1
        elif time_type == TimeType.END:
            if self.rounding_method == RoundingMethod.ROUND:
                frame = ceil((ceil((time - self.first_timestamps) * self.time_scale) - Fraction(1, 2)) * self.fps/self.time_scale) - 1
            elif self.rounding_method == RoundingMethod.FLOOR:
                frame = ceil(ceil((time - self.first_timestamps) * self.time_scale) * self.fps/self.time_scale) - 1
        elif time_type == TimeType.EXACT:
            if self.rounding_method == RoundingMethod.ROUND:
                frame = ceil((floor((time - self.first_timestamps) * self.time_scale) + Fraction(1, 2)) * self.fps/self.time_scale) - 1
            elif self.rounding_method == RoundingMethod.FLOOR:
                frame = ceil((floor((time - self.first_timestamps) * self.time_scale) + Fraction(1)) * self.fps/self.time_scale) - 1
        else:
            raise ValueError(f'The TimeType "{time_type}" isn\'t supported.')

        return frame


    def _frame_to_time(
        self,
        frame: int,
        time_type: TimeType,
        center_time: bool,
    ) -> Fraction:

        if time_type == TimeType.START:
            if frame == 0:
                return self.first_timestamps

            upper_bound = self.rounding_method(frame * self.time_scale/self.fps) * 1/self.time_scale + self.first_timestamps

            if center_time:
                lower_bound = self.rounding_method((frame-1) * self.time_scale/self.fps) * 1/self.time_scale + self.first_timestamps
                time = (lower_bound + upper_bound) / 2
            else:
                time = upper_bound

        elif time_type == TimeType.END:
            upper_bound = self.rounding_method((frame+1) * self.time_scale/self.fps) * 1/self.time_scale + self.first_timestamps

            if center_time:
                lower_bound = self.rounding_method(frame * self.time_scale/self.fps) * 1/self.time_scale + self.first_timestamps
                time = (lower_bound + upper_bound) / 2
            else:
                time = upper_bound

        elif time_type == TimeType.EXACT:
            time = self.rounding_method(frame * self.time_scale/self.fps) * 1/self.time_scale + self.first_timestamps

        else:
            raise ValueError(f'The TimeType "{time_type}" isn\'t supported.')

        return time


    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FPSTimestamps):
            return False
        return (self.rounding_method, self.fps, self.time_scale, self.first_pts, self.first_timestamps) == (
            other.rounding_method, other.fps, other.time_scale, other.first_pts, other.first_timestamps
        )


    def __hash__(self) -> int:
        return hash(
            (
                self.rounding_method,
                self.fps,
                self.time_scale,
                self.first_pts,
                self.first_timestamps,
            )
        )
