from fractions import Fraction
from io import StringIO
from pathlib import Path

from .abc_timestamps import ABCTimestamps
from .fps_timestamps import FPSTimestamps
from .rounding_method import RoundingMethod
from .time_type import TimeType
from .timestamps_file_parser import TimestampsFileParser
from .video_timestamps import VideoTimestamps

__all__ = ["TextFileTimestamps"]

class TextFileTimestamps(ABCTimestamps):
    """Create a Timestamps object from a mkv [timestamps file](https://mkvtoolnix.download/doc/mkvmerge.html#mkvmerge.external_timestamp_files).
    We only support the v1, v2 and v4 format.
    """

    def __init__(
        self,
        path_to_timestamps_file_or_content: str | Path,
        time_scale: Fraction,
        rounding_method: RoundingMethod,
        normalize: bool = True,
    ):
        """Initialize the TextFileTimestamps object.

        The `time_scale` and `rounding_method` are required because, in reality, if you provide a timestamps file to `mkvmerge`, it can round the result.
        For example, let's say we use this timestamps file with this command `mkvmerge --output output.mkv --timestamps 0:input_timestamps_file.txt input.mkv`
        ```
        # timestamp format v2
        0
        50.5
        100.4
        150.8
        200.9
        250
        ```

        Since mkvmerge set a default `timescale` of 1000 and use the `rounding_method` [`RoundingMethod.ROUND`][video_timestamps.rounding_method.RoundingMethod.ROUND],
        it cannot properly represent the provided timestamps.
        If you extract the timestamps with `mkvextract output.mkv timestamps_v2 0:final_timestamps_file.txt`, you will get this result:
        ```
        # timestamp format v2
        0
        51
        100
        151
        201
        250
        ```

        Parameters:
            path_to_timestamps_file_or_content: If is it a Path, the path to the timestamps file.

                If it is a str, a timestamps file content.
            time_scale: Unit of time (in seconds) in terms of which frame timestamps are represented.

                Important: Don't confuse time_scale with the time_base. As a reminder, time_base = 1 / time_scale.
            rounding_method: The rounding method used to round/floor the PTS (Presentation Time Stamp).
            normalize: If True, it will shift the PTS to make them start from 0. If false, the option does nothing.
        """

        if isinstance(path_to_timestamps_file_or_content, Path):
            with open(path_to_timestamps_file_or_content, encoding="utf-8") as f:
                timestamps, fps, version = TimestampsFileParser.parse_file(f)
        else:
            file = StringIO(path_to_timestamps_file_or_content)
            timestamps, fps, version = TimestampsFileParser.parse_file(file)

        self.__rounding_method = rounding_method
        self.__version = version

        pts_list = [self.rounding_method(Fraction(time, pow(10, 3)) * time_scale) for time in timestamps]

        self._video_timestamps = VideoTimestamps(pts_list, time_scale, normalize, fps)

        self._fps_timestamps = None
        if self.version == 1:
            assert isinstance(fps, Fraction)
            self._fps_timestamps = FPSTimestamps(self.rounding_method, time_scale, fps, Fraction(timestamps[-1], pow(10, 3)))

    @property
    def rounding_method(self) -> RoundingMethod:
        return self.__rounding_method

    @property
    def fps(self) -> Fraction:
        if self._fps_timestamps is not None:
            return self._fps_timestamps.fps
        else:
            return self._video_timestamps.fps

    @property
    def time_scale(self) -> Fraction:
        return self._video_timestamps.time_scale

    @property
    def first_timestamps(self) -> Fraction:
        return self._video_timestamps.first_timestamps

    @property
    def version(self) -> int:
        """
        Returns:
            The version of the timestamps file (1, 2 or 4).
        """
        return self.__version

    @property
    def nbr_frames(self) -> int:
        """
        Returns:
            The number of frames of the timestamps file. Note that you cannot use this property with v1 timestamps file.
        """
        if self.version in (2, 4):
            return self._video_timestamps.nbr_frames
        else:
            raise ValueError("V1 timestamps file doesn't specify a number of frames.")


    def _time_to_frame(
        self,
        time: Fraction,
        time_type: TimeType,
    ) -> int:
        if self._fps_timestamps is not None and time > self._video_timestamps.timestamps[-1]:
            return self._video_timestamps.nbr_frames + self._fps_timestamps._time_to_frame(time, time_type)
        else:
            return self._video_timestamps._time_to_frame(time, time_type)


    def _frame_to_time(
        self,
        frame: int,
    ) -> Fraction:
        if self._fps_timestamps is not None and frame > self._video_timestamps.nbr_frames:
            return self._fps_timestamps._frame_to_time(frame - self._video_timestamps.nbr_frames)
        else:
            return self._video_timestamps._frame_to_time(frame)


    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TextFileTimestamps):
            return False
        return (self.rounding_method, self.version, self._video_timestamps, self._fps_timestamps) == (
            other.rounding_method, other.version, other._video_timestamps, other._fps_timestamps
        )


    def __hash__(self) -> int:
        return hash(
            (
                self.rounding_method,
                self.__version,
                self._video_timestamps,
                self._fps_timestamps,
            )
        )
