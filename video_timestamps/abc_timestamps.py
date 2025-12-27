from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from fractions import Fraction
from math import ceil, floor
from typing import overload

from .rounding_method import RoundingMethod
from .time_type import TimeType

__all__ = ["ABCTimestamps"]


class ABCTimestamps(ABC):
    """Timestamps object contains informations about the timestamps of an video.
    Constant Frame Rate (CFR) and Variable Frame Rate (VFR) videos are supported.

    Depending of the software you use to create the video, the PTS (Presentation Time Stamp)
    may be rounded of floored.

    In general, the PTS are floored, so you should use [`RoundingMethod.FLOOR`][video_timestamps.rounding_method.RoundingMethod.FLOOR].

    But, Matroska (.mkv) file are an exception because they are rounded.
    If you want to be compatible with mkv, use [`RoundingMethod.ROUND`][video_timestamps.rounding_method.RoundingMethod.ROUND].
    By default, they only have a precision to milliseconds instead of nanoseconds like most format.

    For more detail see:
        1. [mkvmerge timestamp scale documentation](https://mkvtoolnix.download/doc/mkvmerge.html#mkvmerge.description.timestamp_scale)
        2. [Matroska timestamp scale rounding notes](https://www.matroska.org/technical/notes.html#timestampscale-rounding)
    """

    @property
    @abstractmethod
    def fps(self) -> Fraction:
        """
        Returns:
            The framerate of the video.
        """
        pass

    @property
    @abstractmethod
    def time_scale(self) -> Fraction:
        """
        Returns:
            Unit of time (in seconds) in terms of which frame PTS are represented.

                **Important**: Don't confuse time_scale with the time_base. As a reminder, time_base = 1 / time_scale.
        """
        pass

    @property
    @abstractmethod
    def first_timestamps(self) -> Fraction:
        """
        Returns:
            Time (in seconds) of the first frame of the video.

                **Warning**: Depending on the subclass, the first_timestamps may not be rounded, so it won't really be first_timestamps.
        """
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
        time: int | Fraction,
        time_type: TimeType,
        input_unit: int | None = None
    ) -> int:
        """Converts a given time value into the corresponding frame number based on the specified time type.

        Parameters:
            time: The time value to convert.

                - If `time` is an int, the unit of the value is specified by `input_unit` parameter.

                - If `time` is a Fraction, the value is expected to be in seconds.
            time_type: The type of timing to use for conversion.
            input_unit: The unit of the `time` parameter when it is an int.
                Must be a non-negative integer if specified.

                Common values:

                - 3 means milliseconds
                - 6 means microseconds
                - 9 means nanoseconds

                If None, the `time` will be a Fraction representing seconds.

        Returns:
            The corresponding frame number for the given time.

        Examples:
            >>> timestamps.time_to_frame(50, TimeType.START, 3)
            2
            >>> timestamps.time_to_frame(Fraction(50/1000), TimeType.START)
            2
            # Example with FPS = 24000/1001, time_scale = 90000, rounding method = FLOOR.
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

        first_timestamps = self.frame_to_time(0, TimeType.EXACT)

        if time_in_second < first_timestamps and time_type == TimeType.EXACT:
            raise ValueError(f"You cannot specify a time under the first timestamps {first_timestamps} with the TimeType.EXACT.")
        if time_in_second <= first_timestamps:
            if time_type == TimeType.START:
                return 0
            elif time_type == TimeType.END:
                raise ValueError(f"You cannot specify a time under or equals the first timestamps {first_timestamps} with the TimeType.END.")

        frame = self._time_to_frame(time_in_second, time_type)
        return frame


    @abstractmethod
    def _frame_to_time(
        self,
        frame: int,
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
        output_unit: int | None = None,
        center_time: bool = False,
    ) -> int | Fraction:
        """Converts a given frame number into the corresponding time value based on the specified time type.

        Parameters:
            frame: The frame number to convert.
            time_type: The type of timing to use for conversion.
            output_unit: The unit of the output time value.
                Must be a non-negative integer if specified.

                Common values:

                - 3 means milliseconds
                - 6 means microseconds
                - 9 means nanoseconds

                If None, the output will be a Fraction representing seconds.
            center_time: If True, the output time will represent the time at the center of two frames.
                This option is only applicable when `time_type` is either [`TimeType.START`][video_timestamps.time_type.TimeType.START] or [`TimeType.END`][video_timestamps.time_type.TimeType.END].

        Returns:
            The corresponding time for the given frame number.

        Examples:
            >>> timestamps.frame_to_time(2, TimeType.START, 3)
            83
            >>> timestamps.frame_to_time(2, TimeType.START)
            7507/90000
            >>> timestamps.frame_to_time(2, TimeType.START, 3, True)
            63
            # Example with FPS = 24000/1001, time_scale = 90000, rounding method = FLOOR.
        """

        if output_unit is not None and output_unit < 0:
            raise ValueError("The output_unit needs to be above or equal to 0.")

        if frame < 0:
            raise ValueError("You cannot specify a frame under 0.")

        if time_type == TimeType.EXACT and center_time:
            raise ValueError("It doesn't make sense to use the time in the center of two frame for TimeType.EXACT.")

        if time_type == TimeType.START:
            upper_bound = self._frame_to_time(frame)

            if center_time and frame > 0:
                lower_bound = self._frame_to_time(frame - 1)
                time = (lower_bound + upper_bound) / 2
            else:
                time = upper_bound
        elif time_type == TimeType.END:
            upper_bound = self._frame_to_time(frame + 1)

            if center_time:
                lower_bound = self._frame_to_time(frame)
                time = (lower_bound + upper_bound) / 2
            else:
                time = upper_bound
        elif time_type == TimeType.EXACT:
            time = self._frame_to_time(frame)
        else:
            raise ValueError(f'The TimeType "{time_type}" isn\'t supported.')

        if output_unit is None:
            return time

        if time_type == TimeType.EXACT:
            time_output = ceil(time * Fraction(10) ** output_unit)
        elif center_time and not (time_type == TimeType.START and frame == 0):
            time_output = RoundingMethod.ROUND(time * 10 ** output_unit)
        else:
            time_output = floor(time * Fraction(10) ** output_unit)

        result_frame = self.time_to_frame(time_output, time_type, output_unit)

        if frame != result_frame:
            raise ValueError(
                f"The frame {frame} cannot be represented exactly at output_unit={output_unit}. "
                f"The conversion gave the time {time_output} which correspond to the frame {result_frame} which is different then {frame}. "
                f"Try using a finer output_unit then {time_output}."
            )

        return time_output


    def pts_to_frame(
        self,
        pts: int,
        time_type: TimeType,
        time_scale: Fraction | None = None
    ) -> int:
        """Converts a given PTS into the corresponding frame number based on the specified time type.

        Parameters:
            pts: The Presentation Time Stamp value to convert.
            time_type: The type of timing to use for conversion.
            time_scale: The time scale to interpret the `pts` parameter.
                If None, it is assumed that the `pts` parameter uses the same time scale as the Timestamps object.

        Returns:
            The corresponding frame number for the given PTS.

        Examples:
            >>> timestamps.pts_to_frame(7507, TimeType.START, Fraction(90000))
            2
            # Example with FPS = 24000/1001, time_scale = 90000, rounding method = FLOOR.
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
        time_scale: Fraction | None = None
    ) -> int:
        """Converts a given frame number into the corresponding PTS based on the specified time type.

        Parameters:
            frame: The frame number to convert.
            time_type: The type of timing to use for conversion.
            time_scale: The time scale to interpret the `pts` parameter.
                If None, it is assumed that the `pts` parameter uses the same time scale as the Timestamps object.

        Returns:
            The corresponding PTS for the given frame number.

        Examples:
            >>> timestamps.frame_to_pts(2, TimeType.START, Fraction(90000))
            7507
            # Example with FPS = 24000/1001, time_scale = 90000, rounding method = FLOOR.
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
        time: int | Fraction,
        time_type: TimeType,
        output_unit: None,
        input_unit: int | None = None,
        center_time: bool = False
    ) -> Fraction:
        ...

    @overload
    def move_time_to_frame(
        self,
        time: int | Fraction,
        time_type: TimeType,
        output_unit: int,
        input_unit: int | None = None,
        center_time: bool = False
    ) -> int:
        ...

    def move_time_to_frame(
        self,
        time: int | Fraction,
        time_type: TimeType,
        output_unit: int | None = None,
        input_unit: int | None = None,
        center_time: bool = False
    ) -> int | Fraction:
        """
        Moves the time to the corresponding frame time.
        It is something close to using "CTRL + 3" and "CTRL + 4" on Aegisub.

        Parameters:
            time: The time value to convert.

                - If `time` is an int, the unit of the value is specified by `input_unit` parameter.

                - If `time` is a Fraction, the value is expected to be in seconds.
            time_type: The type of timing to use for conversion.
            output_unit: The unit of the output time value.
                Must be a non-negative integer if specified.

                Common values:

                - 3 means milliseconds
                - 6 means microseconds
                - 9 means nanoseconds

                If None, the output will be a Fraction representing seconds.
            input_unit: The unit of the `time` parameter when it is an int.
                Must be a non-negative integer if specified.

                Common values:

                - 3 means milliseconds
                - 6 means microseconds
                - 9 means nanoseconds

                If None, the `time` will be a Fraction representing seconds.
            center_time: If True, the output time will represent the time at the center of two frames.
                This option is only applicable when `time_type` is either [`TimeType.START`][video_timestamps.time_type.TimeType.START] or [`TimeType.END`][video_timestamps.time_type.TimeType.END].

        Returns:
            The output represents `time` moved to the frame time.

        Examples:
            >>> timestamps.move_time_to_frame(50, TimeType.START, 3, 3)
            83
            >>> timestamps.move_time_to_frame(50, TimeType.START, 9, 3)
            83411111
            # Example with FPS = 24000/1001, time_scale = 90000, rounding method = FLOOR.
        """

        return self.frame_to_time(self.time_to_frame(time, time_type, input_unit), time_type, output_unit, center_time)


    def pts_to_time(
        self,
        pts: int,
        time_type: TimeType,
        output_unit: int,
        time_scale: Fraction | None = None
    ) -> int:
        """
        Converts a given PTS into the corresponding time, ensuring that
        the resulting value corresponds to the same frame.

        Parameters:
            pts: The Presentation Time Stamp value to convert.
            time_type: The type of timing to use for conversion.
            time_scale: The time scale to interpret the `pts` parameter.
                If None, it is assumed that the `pts` parameter uses the same time scale as the Timestamps object.

        Returns:
            The corresponding time for the given PTS.

        Examples:
            >>> timestamps.pts_to_time(7507, TimeType.START, 3, Fraction(90000))
            83
            >>> timestamps.pts_to_time(7507, TimeType.START, 9, Fraction(90000))
            83411111
            # Example with FPS = 24000/1001, time_scale = 90000, rounding method = FLOOR.
        """

        if time_scale is None:
            time = pts / self.time_scale
        else:
            time = pts / time_scale

        return self.time_to_time(time, time_type, output_unit)


    @overload
    def time_to_pts(
        self,
        time: int,
        time_type: TimeType,
        input_unit: int,
        time_scale: Fraction | None = None,
    ) -> int:
        ...

    @overload
    def time_to_pts(
        self,
        time: Fraction,
        time_type: TimeType,
        input_unit: None = None,
        time_scale: Fraction | None = None,
    ) -> int:
        ...

    def time_to_pts(
        self,
        time: int | Fraction,
        time_type: TimeType,
        input_unit: int | None = None,
        time_scale: Fraction | None = None,
    ) -> int:
        """
        Converts a given time value into the corresponding PTS, ensuring that
        the resulting value corresponds to the same frame.

        Parameters:
            time: The time value to convert.

                - If `time` is an int, the unit of the value is specified by `input_unit` parameter.

                - If `time` is a Fraction, the value is expected to be in seconds.
            time_type: The type of timing to use for conversion.
            input_unit: The unit of the `time` parameter when it is an int.
                Must be a non-negative integer if specified.

                Common values:

                - 3 means milliseconds
                - 6 means microseconds
                - 9 means nanoseconds

                If None, the `time` will be a `Fraction` representing seconds.
            time_scale: The time scale to interpret the `pts` that will be returned by this function.
                - If None, the `pts` that will be returned will uses the same time scale as the Timestamps object.

        Returns:
            The corresponding PTS for the given time.

        Examples:
            >>> timestamps.time_to_pts(83, TimeType.START, 3, Fraction(90000))
            7470
            >>> timestamps.time_to_pts(83411111, TimeType.START, 9, Fraction(90000))
            7507
            # Example with FPS = 24000/1001, time_scale = 90000, rounding method = FLOOR.
        """

        if input_unit is None:
            time_in_second = time
        else:
            time_in_second = time * Fraction(1, 10 ** input_unit)

        if time_scale is None:
            output_time_scale = self.time_scale
        else:
            output_time_scale = time_scale

        frame = self.time_to_frame(time, time_type, input_unit)
        pts_output = time_in_second * output_time_scale

        # Try with round first because we want to get the closest result
        pts_output_round = RoundingMethod.ROUND(pts_output)
        frame_round = self.pts_to_frame(pts_output_round, time_type, output_time_scale)
        if frame_round == frame:
            return pts_output_round

        # Try with the opposite of round
        pts_output_other = floor(pts_output) if pts_output_round == ceil(pts_output) else ceil(pts_output)
        frame_other = self.pts_to_frame(pts_output_other, time_type, output_time_scale)
        if frame_other == frame:
            return pts_output_other

        raise ValueError(f"It is not possible to convert the time {time_in_second} to a PTS with a timescale of {output_time_scale} accurately.")


    @overload
    def time_to_time(
        self,
        time: int,
        time_type: TimeType,
        output_unit: int,
        input_unit: int,
    ) -> int:
        ...

    @overload
    def time_to_time(
        self,
        time: Fraction,
        time_type: TimeType,
        output_unit: int,
        input_unit: None = None,
    ) -> int:
        ...

    def time_to_time(
        self,
        time: int | Fraction,
        time_type: TimeType,
        output_unit: int,
        input_unit: int | None = None,
    ) -> int:
        """
        Converts a given time value from one unit to another, ensuring that
        the resulting value corresponds to the same frame.

        Parameters:
            time: The time value to convert.

                - If `time` is an int, the unit of the value is specified by `input_unit` parameter.

                - If `time` is a Fraction, the value is expected to be in seconds.
            time_type: The type of timing to use for conversion.
            output_unit: The unit of the output time value.
                Must be a non-negative integer.

                Common values:

                - 3 means milliseconds
                - 6 means microseconds
                - 9 means nanoseconds
            input_unit: The unit of the `time` parameter when it is an `int`.
                - Must be a non-negative integer if specified.

                Common values:

                - 3 means milliseconds
                - 6 means microseconds
                - 9 means nanoseconds

                If None, the `time` will be a `Fraction` representing seconds.

        Returns:
            The converted time value expressed in `output_unit`.

        Examples:
            >>> timestamps.time_to_time(83411111, TimeType.START, 3, 9)
            83
            >>> timestamps.time_to_time(83411112, TimeType.START, 3, 9)
            84
            # Example with FPS = 24000/1001, time_scale = 90000, rounding method = FLOOR.
        """
        if input_unit is not None and input_unit < 0:
            raise ValueError("The input_unit needs to be above or equal to 0.")

        if output_unit < 0:
            raise ValueError("The output_unit needs to be above or equal to 0.")

        if input_unit == output_unit and isinstance(time, int): # Just to make mypy happy, use isinstance so it doesn't report int | Fraction.
            return time
        elif input_unit is not None and input_unit < output_unit:
            return RoundingMethod.ROUND(time * 10 ** (output_unit - input_unit)) # Just to make mypy happy, round the result, but it is impossible to get a float from this.
        else:
            frame = self.time_to_frame(time, time_type, input_unit)
            if isinstance(time, int) and input_unit is not None: # Just to make mypy happy, verify if input_unit is not None even if it can't.
                time_output = Fraction(time, 10 ** (input_unit - output_unit))
            else:
                time_output = time * Fraction(10 ** output_unit)

            # Try with round first because we want to get the closest result
            time_output_round = RoundingMethod.ROUND(time_output)
            try:
                frame_round = self.time_to_frame(time_output_round, time_type, output_unit)
            except ValueError:
                frame_round = None
            if frame_round == frame:
                return time_output_round

            # Try with the opposite of round
            time_output_other = floor(time_output) if time_output_round == ceil(time_output) else ceil(time_output)
            try:
                frame_other = self.time_to_frame(time_output_other, time_type, output_unit)
            except ValueError:
                frame_other = None
            if frame_other == frame:
                return time_output_other

            raise ValueError(f"It is not possible to convert the time {time} from {input_unit} to {output_unit} accurately.")


    @abstractmethod
    def __eq__(self, other: object) -> bool:
        pass


    @abstractmethod
    def __hash__(self) -> int:
        pass
