from decimal import Decimal
from fractions import Fraction
from math import ceil, floor

from .abc_timestamps import ABCTimestamps
from .rounding_method import RoundingMethod
from .time_type import TimeType

__all__ = ["FPSTimestamps"]


class FPSTimestamps(ABCTimestamps):
    """Create a Timestamps object from a fps.
    """

    def __init__(
        self,
        rounding_method: RoundingMethod,
        time_scale: Fraction,
        fps: int | float | Fraction | Decimal,
        first_timestamps: Fraction = Fraction(0)
    ):
        """Initialize the FPSTimestamps object.

        To understand why the `rounding_method` and the `time_scale` are needed, see the detailed explanation in the
        [frame_to_time](../Algorithm conversion explanation.md#frame_to_time) section.
        If after reading the [frame_to_time](../Algorithm conversion explanation.md#frame_to_time) section,
        you still think you need to have `time = frame * (1/fps)` instead of `time = pts * timebase`, use **any** `rounding_method` and use the same value for the `time_scale` as for the `fps`.
        It will be the equivalent.

        Parameters:
            rounding_method: The rounding method used to round/floor the PTS (Presentation Time Stamp).
            time_scale: Unit of time (in seconds) in terms of which frame PTS are represented.
            fps: Frames per second (must be > 0).
            first_timestamps: The first timestamp of the video. By default, 0.
        """
        if time_scale <= 0:
            raise ValueError("Parameter ``time_scale`` must be higher than 0.")

        if fps <= 0:
            raise ValueError("Parameter ``fps`` must be higher than 0.")

        self.__rounding_method = rounding_method
        self.__time_scale = time_scale
        self.__fps = Fraction(fps)
        self.__first_timestamps = first_timestamps

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
    def first_timestamps(self) -> Fraction:
        return self.__first_timestamps


    def _time_to_frame(
        self,
        time: Fraction,
        time_type: TimeType,
    ) -> int:
        # To understand this, refer to docs/Algorithm conversion explanation.md
        if time_type == TimeType.START:
            if self.rounding_method == RoundingMethod.ROUND:
                frame = ceil(((ceil(time * self.time_scale) - Fraction(1, 2)) / self.time_scale - self.first_timestamps) * self.fps + Fraction(1)) - 1
            elif self.rounding_method == RoundingMethod.FLOOR:
                frame = ceil(((ceil(time * self.time_scale)) / self.time_scale - self.first_timestamps) * self.fps + Fraction(1)) - 1
        elif time_type == TimeType.END:
            if self.rounding_method == RoundingMethod.ROUND:
                frame = ceil(((ceil(time * self.time_scale) - Fraction(1, 2)) / self.time_scale - self.first_timestamps) * self.fps) - 1
            elif self.rounding_method == RoundingMethod.FLOOR:
                frame = ceil(((ceil(time * self.time_scale)) / self.time_scale - self.first_timestamps) * self.fps) - 1
        elif time_type == TimeType.EXACT:
            if self.rounding_method == RoundingMethod.ROUND:
                frame = ceil(((floor(time * self.time_scale) + Fraction(1, 2)) / self.time_scale - self.first_timestamps) * self.fps) - 1
            elif self.rounding_method == RoundingMethod.FLOOR:
                frame = ceil(((floor(time * self.time_scale) + Fraction(1)) / self.time_scale - self.first_timestamps) * self.fps) - 1
        else:
            raise ValueError(f'The TimeType "{time_type}" isn\'t supported.')

        return frame


    def _frame_to_time(
        self,
        frame: int,
    ) -> Fraction:
        # To understand this, refer to docs/Algorithm conversion explanation.md
        return self.rounding_method((frame/self.fps + self.first_timestamps) * self.time_scale) / self.time_scale


    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FPSTimestamps):
            return False
        return (self.rounding_method, self.fps, self.time_scale, self.first_timestamps) == (
            other.rounding_method, other.fps, other.time_scale, other.first_timestamps
        )


    def __hash__(self) -> int:
        return hash(
            (
                self.rounding_method,
                self.fps,
                self.time_scale,
                self.first_timestamps,
            )
        )
