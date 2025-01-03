from __future__ import annotations
from .rounding_method import RoundingMethod
from .time_type import TimeType
from abc import ABC, abstractmethod
from fractions import Fraction
from math import ceil, floor
from typing import Callable, Optional, Union, overload

__all__ = ["ABCTimestamps"]


class ABCTimestamps(ABC):
    """Timestamps object contains informations about the timestamps of an video.
    Constant Frame Rate (CFR) and Variable Frame Rate (VFR) videos are supported.

    Depending of the software you use to create the video, the PTS (Presentation Time Stamp)
    may be rounded of floored.
    In general, the PTS are floored, so you should use RoundingMethod.FLOOR.
    But, Matroska (.mkv) file are an exception because they are rounded, so you should use RoundingMethod.ROUND.

             file are an exception !!!
        If you want to be compatible with mkv, use RoundingMethod.ROUND.
        By default, they only have a precision to milliseconds instead of nanoseconds like most format.
            For more detail see:
                1- https://mkvtoolnix.download/doc/mkvmerge.html#mkvmerge.description.timestamp_scale
                2- https://matroska.org/technical/notes.html#timestampscale-rounding

    Attributes:
        rounding_method (RoundingMethod): The rounding method used to round/floor the PTS (Presentation Time Stamp).
            See the comment above about floor vs round.
        fps (Fraction): The frames per second of the video.
        time_scale (Fraction): Unit of time (in seconds) in terms of which frame timestamps are represented.
            Important: Don't confuse time_scale with the time_base. As a reminder, time_base = 1 / time_scale.
        first_pts (int): PTS (Presentation Time Stamp) of the first frame of the video.
        first_timestamps (int): Time (in seconds) of the first frame of the video.
    """

    @property
    @abstractmethod
    def rounding_method(self) -> RoundingMethod:
        pass

    @property
    @abstractmethod
    def fps(self) -> Fraction:
        pass

    @property
    @abstractmethod
    def time_scale(self) -> Fraction:
        pass

    @property
    @abstractmethod
    def first_pts(self) -> int:
        pass

    @property
    @abstractmethod
    def first_timestamps(self) -> Fraction:
        pass

    @abstractmethod
    def _time_to_frame(
        self,
        time: Fraction,
        time_type: TimeType,
    ) -> int:
        pass

    def time_to_frame(
        self,
        time: Union[int, Fraction],
        time_type: TimeType,
        input_unit: Optional[int] = None
    ) -> int:
        """Converts a given time value into the corresponding frame number based on the specified time type.

        Parameters:
            time (Union[int, Fraction]): The time value to convert.
                - If `time` is an `int`, the unit of the value is specified by `input_unit`.
                - If `time` is a `Fraction`, the value is expected to be in seconds.
            time_type (TimeType): The type of timing to use for conversion.
            input_unit (Optional[int]): The unit of the `time` parameter when it is an `int`.
                - Must be a non-negative integer if specified.
                - Common values:
                    - 3 means milliseconds
                    - 6 means microseconds
                    - 9 means nanoseconds
                - If None, the `time` will be a `Fraction` representing seconds.

        Returns:
            The corresponding frame number for the given time.
        """

        if input_unit is None:
            if not isinstance(time, Fraction):
                raise ValueError("If input_unit is none, the time needs to be a Fraction.")
            time_in_second = time
        else:
            if not isinstance(time, int):
                raise ValueError("If you specify a input_unit, the time needs to be a int.")

            if input_unit < 0:
                raise ValueError("The input_unit needs to be above or equal to 0.")

            time_in_second = time * Fraction(1, 10 ** input_unit)

        if time_in_second < self.first_timestamps and time_type == TimeType.EXACT:
            raise ValueError(f"You cannot specify a time under the first timestamps {self.first_timestamps} with the TimeType.EXACT.")
        if time_in_second <= self.first_timestamps:
            if time_type == TimeType.START:
                return 0
            elif time_type == TimeType.END:
                raise ValueError(f"You cannot specify a time under or equals the first timestamps {self.first_timestamps} with the TimeType.END.")

        frame = self._time_to_frame(time_in_second, time_type)
        return frame


    @abstractmethod
    def _frame_to_time(
        self,
        frame: int,
        time_type: TimeType,
        center_time: bool,
    ) -> Fraction:
        pass

    @overload
    def frame_to_time(
        self,
        frame: int,
        time_type: TimeType,
        output_unit: None = None,
        center_time: bool = False,
    ) -> Fraction:
        ...

    @overload
    def frame_to_time(
        self,
        frame: int,
        time_type: TimeType,
        output_unit: int,
        center_time: bool = False,
    ) -> int:
        ...

    def frame_to_time(
        self,
        frame: int,
        time_type: TimeType,
        output_unit: Optional[int] = None,
        center_time: bool = False,
    ) -> Union[int, Fraction]:
        """Converts a given frame number into the corresponding time value based on the specified time type.

        Parameters:
            frame (int): The frame number to convert.
            time_type (TimeType): The type of timing to use for conversion.
            output_unit (Optional[int]): The unit of the output time value.
                - Must be a non-negative integer if specified.
                - Common values:
                    - 3: milliseconds
                    - 6: microseconds
                    - 9: nanoseconds
                - If None, the output will be a Fraction representing seconds.
            center_time (bool): If True, the output time will represent the time at the center of two frames.
                This option is only applicable when `time_type` is either `TimeType.START` or `TimeType.END`.

        Returns:
            The corresponding time for the given frame number.
        """

        if output_unit is not None and output_unit < 0:
            raise ValueError("The output_unit needs to be above or equal to 0.")

        if frame < 0:
            raise ValueError("You cannot specify a frame under 0.")

        if time_type == TimeType.EXACT and center_time:
            raise ValueError("It doesn't make sense to use the time in the center of two frame for TimeType.EXACT.")

        time = self._frame_to_time(frame, time_type, center_time)

        if output_unit is None:
            return time

        if time_type == TimeType.EXACT:
            return ceil(time * Fraction(10) ** output_unit)
        elif center_time and not (time_type == TimeType.START and frame == 0):
            return RoundingMethod.ROUND(time * 10 ** output_unit)
        else:
            return floor(time * Fraction(10) ** output_unit)


    def pts_to_frame(
        self,
        pts: int,
        time_type: TimeType,
        time_scale: Optional[Fraction] = None
    ) -> int:
        """Converts a given PTS into the corresponding frame number based on the specified time type.

        Parameters:
            pts (int): The Presentation Time Stamp value to convert.
            time_type (TimeType): The type of timing to use for conversion.
            time_scale (Optional[Fraction]): The time scale to interpret the `pts` parameter.
                - If None, it is assumed that the `pts` parameter uses the same time scale as the Timestamps object.

        Returns:
            The corresponding frame number for the given PTS.
        """

        if time_scale is None:
            time = pts / self.time_scale
        else:
            time = pts / time_scale

        frame = self.time_to_frame(time, time_type)
        return frame


    def frame_to_pts(
        self,
        frame: int,
        time_type: TimeType,
        time_scale: Optional[Fraction] = None
    ) -> int:
        """Converts a given frame number into the corresponding PTS based on the specified time type.

        Parameters:
            frame (int): The frame number to convert.
            time_type (TimeType): The type of timing to use for conversion.
            time_scale (Optional[Fraction]): The time scale to interpret the `pts` parameter.
                - If None, it is assumed that the `pts` parameter uses the same time scale as the Timestamps object.

        Returns:
            The corresponding PTS for the given frame number.
        """

        time = self.frame_to_time(frame, time_type)

        round_pts_method: Callable[[Fraction], int]
        if time_type == TimeType.EXACT:
            round_pts_method = ceil
        else:
            round_pts_method = floor

        if time_scale is None:
            pts = time * self.time_scale
            if pts != round_pts_method(pts):
                raise ValueError(f"An unexpected error occured. The generated pts {pts} isn't an integer. The requested frame is {frame} and the requested time_type is {time_type}. The object is {repr(self)}. Please, open an issue on GitHub.")
        else:
            pts = time * time_scale

        return round_pts_method(pts)


    @overload
    def move_time_to_frame(
        self,
        time: Union[int, Fraction],
        time_type: TimeType,
        output_unit: None,
        input_unit: Optional[int] = None,
        center_time: bool = False
    ) -> Fraction:
        ...

    @overload
    def move_time_to_frame(
        self,
        time: Union[int, Fraction],
        time_type: TimeType,
        output_unit: int,
        input_unit: Optional[int] = None,
        center_time: bool = False
    ) -> int:
        ...

    def move_time_to_frame(
        self,
        time: Union[int, Fraction],
        time_type: TimeType,
        output_unit: Optional[int] = None,
        input_unit: Optional[int] = None,
        center_time: bool = False
    ) -> Union[int, Fraction]:
        """
        Moves the time to the corresponding frame time.
        It is something close to using "CTRL + 3" and "CTRL + 4" on Aegisub.

        Parameters:
            time (Union[int, Fraction]): The time value to convert.
                - If `time` is an `int`, the unit of the value is specified by `input_unit`.
                - If `time` is a `Fraction`, the value is expected to be in seconds.
            time_type (TimeType): The type of timing to use for conversion.
            output_unit (Optional[int]): The unit of the output time value.
                - Must be a non-negative integer if specified.
                - Common values:
                    - 3: milliseconds
                    - 6: microseconds
                    - 9: nanoseconds
                - If None, the output will be a Fraction representing seconds.
            input_unit (Optional[int]): The unit of the `time` parameter when it is an `int`.
                - Must be a non-negative integer if specified.
                - Common values:
                    - 3 means milliseconds
                    - 6 means microseconds
                    - 9 means nanoseconds
                - If None, the `time` will be a `Fraction` representing seconds.
            center_time (bool): If True, the output time will represent the time at the center of two frames.
                This option is only applicable when `time_type` is either `TimeType.START` or `TimeType.END`.

        Returns:
            The output represents `time` moved to the frame time.
        """

        return self.frame_to_time(self.time_to_frame(time, time_type, input_unit), time_type, output_unit, center_time)


    @abstractmethod
    def __eq__(self, other: object) -> bool:
        pass


    @abstractmethod
    def __hash__(self) -> int:
        pass
