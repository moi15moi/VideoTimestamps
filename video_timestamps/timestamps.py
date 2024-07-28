from .rounding_method import RoundingMethod
from .time_type import TimeType
from bisect import bisect_right
from fractions import Fraction
from math import ceil
from typing import Any, Optional

__all__ = ["Timestamps"]

class Timestamps:
    """Timestamps object contains informations about the timestamps of an video.
    Constant Frame Rate (CFR) and Variable Frame Rate (VFR) videos are supported.

    Video player have 2 methods to deal with timestamps. Some floor them and other round them.
    This can lead to difference when displaying the subtitle.
        Ex:
            Player - Method - proof
            mpv    - round  - https://github.com/mpv-player/mpv/blob/7480efa62c0a2a1779b4fdaa804a6512aa488400/sub/sd_ass.c#L499
            FFmpeg - floor  - https://github.com/FFmpeg/FFmpeg/blob/fd1712b6fb8b7acc04ccaa7c02b9a5c9f233cfb3/libavfilter/vf_subtitles.c#L194-L196
            VLC    - floor  - https://code.videolan.org/videolan/vlc/-/blob/df6394ea8003e035a281b6818e6432c7d492ed2f/modules/codec/libass.c#L453-454
                              https://code.videolan.org/videolan/vlc/-/blob/df6394ea8003e035a281b6818e6432c7d492ed2f/include/vlc_tick.h#L120-132
            MPC-HC - floor  - https://github.com/clsid2/mpc-hc/blob/0994fd605a9fb4d15806d0efdd6399ba1bc5f984/src/Subtitles/LibassContext.cpp#L843
    Important note:
        Matroska (.mkv) file are an exception !!!
        If you want to be compatible with mkv, use RoundingMethod.ROUND.
        By default, they only have a precision to milliseconds instead of nanoseconds like most format.
            For more detail see:
                1- https://mkvtoolnix.download/doc/mkvmerge.html#mkvmerge.description.timestamp_scale
                2- https://matroska.org/technical/notes.html#timestampscale-rounding

    Parameters:
        rounding_method (RoundingMethod): A rounding method. See the comment above about floor vs round.
            99% of the time, you want to use RoundingMethod.ROUND.
        timestamps (List[int], optional): A list of [timestamps](https://en.wikipedia.org/wiki/Timestamp) in milliseconds encoded as integers.
                                It represent each frame [presentation timestamp (PTS)](https://en.wikipedia.org/wiki/Presentation_timestamp)
        normalize (bool, optional): If True, it will shift the timestamps to make them start from 0. If false, the option does nothing.
        fpms (Fraction, optional): Frames per milliseconds.
        last_frame_time (Fraction, optional): The last frame time not rounded in milliseconds.
    """

    def __init__(
        self,
        rounding_method: RoundingMethod,
        timestamps: Optional[list[int]] = None,
        normalize: Optional[bool] = True,
        fpms: Optional[Fraction] = None,
        last_frame_time: Optional[Fraction] = None,
    ):
        self.__rounding_method = rounding_method

        if timestamps is None:
            if fpms is None:
                raise ValueError(
                    "If you don't specify a value for ``timestamps``, you must specify a value for ``fpms``"
                )
            if last_frame_time is not None:
                raise ValueError(
                    "If you don't specify a value for ``timestamps``, you cannot specify a value for ``last_frame_time``"
                )

            self.fpms = fpms
            self.timestamps = [0]
            self.last_frame_time = Fraction(0)
        else:
            if last_frame_time is None:
                raise ValueError(
                    "If you specify a value for ``timestamps``, you must specify a value for ``last_frame_time``"
                )
            self.last_frame_time = last_frame_time

            # Validate the timestamps
            if len(timestamps) <= 1:
                raise ValueError("There must be at least 2 timestamps.")

            if any(timestamps[i] > timestamps[i + 1] for i in range(len(timestamps) - 1)):
                raise ValueError("Timestamps must be in non-decreasing order.")

            if timestamps.count(timestamps[0]) == len(timestamps):
                raise ValueError("Timestamps must not be all identical.")

            self.timestamps = timestamps

            if normalize:
                self.timestamps, self.last_frame_time = Timestamps.normalize(self.timestamps, self.last_frame_time)

            if fpms is None:
                # Approximation of the fpms
                self.fpms = Fraction(len(timestamps) - 1, self.timestamps[-1] - self.timestamps[0])
            else:
                self.fpms = fpms

    @property
    def rounding_method(self) -> RoundingMethod:
        return self.__rounding_method

    @rounding_method.setter
    def rounding_method(self, value: Any) -> None:
        raise AttributeError("You cannot change the value of rounding_method")


    @staticmethod
    def normalize(
        timestamps: list[int], last_frame_time: Fraction
    ) -> tuple[list[int], Fraction]:
        """Shift the timestamps to make them start from 0. This way, frame 0 will start at time 0.

        Parameters:
            timestamps (list of int): A list of [timestamps](https://en.wikipedia.org/wiki/Timestamp) encoded as integers.
            last_frame_time (Fraction): The last frame time not rounded.

        Returns:
            The timestamps normalized and the last frame time normalized.
        """
        if timestamps[0]:
            return (
                list(map(lambda t: t - timestamps[0], timestamps)),
                last_frame_time - timestamps[0],
            )
        return timestamps, last_frame_time


    def ms_to_frames(
        self,
        ms: int,
        time_type: TimeType,
    ) -> int:
        """Converts milliseconds to frames.

        Parameters:
            ms (int): Milliseconds.
            time_type (TimeType): The type of the provided time (start/end).

        Returns:
            The output represents ``ms`` converted into ``frames``.
        """
        if ms < self.timestamps[0]:
            raise ValueError(f"You cannot specify a time under the first timestamps: {self.timestamps[0]}.")

        if time_type == TimeType.START:
            if ms == self.timestamps[0]:
                return 0
            return self.ms_to_frames(ms - 1, TimeType.EXACT) + 1
        elif time_type == TimeType.END:
            if ms == self.timestamps[0]:
                raise ValueError(f'You cannot specify a time equals to the first timestamps {self.timestamps[0]} with the TimeType.END.')

            return self.ms_to_frames(ms - 1, TimeType.EXACT)

        if ms > self.timestamps[-1]:
            # For explanation of this, see docs/Proof algorithm - ms_to_frames.md
            if self.rounding_method == RoundingMethod.ROUND:
                return ceil((ms + Fraction("0.5") - self.last_frame_time) * self.fpms + len(self.timestamps) - 1) - 1
            elif self.rounding_method == RoundingMethod.FLOOR:
                return ceil((ms + 1 - self.last_frame_time) * self.fpms + len(self.timestamps) - 1) - 1
            else:
                raise NotImplementedError(
                    f'The method "{self.rounding_method}" is not supported.'
                )

        # Employing bisect_right as a faster alternative to:
        # for i, timecode in reversed(list(enumerate(timestamps))):
        #     if timecode <= ms:
        #         return i
        return bisect_right(self.timestamps, ms) - 1


    def frames_to_ms(
        self,
        frame: int,
        time_type: TimeType,
    ) -> int:
        """Converts frames to milliseconds.

        Parameters:
            frame (int): Frame.
            time_type (TimeType): The type of the provided time (start/end).

        Returns:
            The output represents ``frame`` converted into ``ms``.
        """
        if frame < 0:
            raise ValueError("You cannot specify a frame under 0.")

        if time_type == TimeType.START:
            if frame == 0:
                return self.timestamps[0]

            # Previous image excluded
            prev_ms = self.frames_to_ms(frame - 1, TimeType.EXACT) + 1
            # Current image inclued
            curr_ms = self.frames_to_ms(frame, TimeType.EXACT)

            return prev_ms + (curr_ms - prev_ms) // 2

        elif time_type == TimeType.END:
            # Current image excluded
            curr_ms = self.frames_to_ms(frame, TimeType.EXACT) + 1
            # Next image inclued
            next_ms = self.frames_to_ms(frame + 1, TimeType.EXACT)

            return curr_ms + (next_ms - curr_ms) // 2

        if frame > len(self.timestamps) - 1:
            frames_past_end = frame - len(self.timestamps) + 1
            return self.rounding_method(
                frames_past_end * 1 / self.fpms + self.last_frame_time
            )

        return self.timestamps[frame]


    def move_ms_to_frame(self, ms: int, time_type: TimeType) -> int:
        """
        Moves the ms to when the corresponding frame starts or ends
        It is something close to using "CTRL + 3" and "CTRL + 4" on Aegisub.

        Parameters:
            ms (int): Milliseconds.
            time_type (TimeType): The type of the provided time (start/end).

        Returns:
            The output represents ``ms`` converted.
        """

        return self.frames_to_ms(self.ms_to_frames(ms, time_type), time_type)
