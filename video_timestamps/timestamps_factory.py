from __future__ import annotations
from .abc_video_parser import ABCVideoParser
from .rounding_method import RoundingMethod
from .timestamps_file_parser import TimestampsFileParser
from .timestamps import Timestamps
from .ffprobe.timestamps import FFprobeTimestamps
from .mkvtoolnix.timestamps import MKVToolNixTimestamps
from .mkvtoolnix.utils import MKVUtils
from decimal import Decimal
from fractions import Fraction
from io import StringIO
from pathlib import Path
from typing import Optional, Union
from warnings import warn

__all__ = ["TimestampsFactory"]

class TimestampsFactory:

    @staticmethod
    def from_fps(
        fps: Union[int, float, Fraction, Decimal],
        rounding_method: RoundingMethod = RoundingMethod.ROUND,
    ) -> Timestamps:
        """Create timestamps based on the `fps` provided.

        Parameters:
            fps (int | float | Fraction | Decimal): Frames per second. Need to be in the interval ]0, 1000]
            rounding_method (RoundingMethod, optional): A rounding method. See the comment in Timestamps class about FLOOR vs ROUND.

        Returns:
            A Timestamps instance.
        
        Note:
            This assume a constant fps. You cannot use this method with video with drop frame.
        """
        if not 0 < fps <= 1000:
            raise ValueError(
                "Parameter ``fps`` must be between 0 and 1000 (0 not included)."
            )

        fpms = Fraction(fps) / Fraction(1000)

        timestamps = Timestamps(
            rounding_method=rounding_method,
            fpms=fpms,
        )
        return timestamps


    @staticmethod
    def from_timestamps_file(
        path_to_timestamps_file_or_content: Union[str, Path],
        normalize: bool = True,
        rounding_method: RoundingMethod = RoundingMethod.ROUND,
    ) -> Timestamps:
        """Create timestamps based on a [timestamps file](https://mkvtoolnix.download/doc/mkvmerge.html#mkvmerge.external_timestamp_files).

        To extract the timestamps file, you have 2 options:
            - Open the video with Aegisub. "Video" --> "Save Timecodes File";
            - Using [gMKVExtractGUI](https://sourceforge.net/projects/gmkvextractgui/)
                Warning: it will produce one timestamp too many at the end of the file, and you will need to manually remove it
                    See: https://gitlab.com/mbunkus/mkvtoolnix/-/issues/3075

        Parameters:
            path_to_timestamps_file_or_content (str | os.PathLike[str]):
                Path for the timestamps file (either relative to your .py file or absolute).
                Or, it can directly be a string of the timestamps file content.
            normalize (bool, optional): If True, it will shift the timestamps to make them start from 0. If false, the option does nothing.
            rounding_method (RoundingMethod, optional): A rounding method. See the comment in Timestamps class about FLOOR vs ROUND.

        Returns:
            A Timestamps instance.
        """

        if isinstance(path_to_timestamps_file_or_content, Path):
            with open(path_to_timestamps_file_or_content, "r", encoding="utf-8") as f:
                timestamps, last_frame_time, fpms = TimestampsFileParser.parse_file(f, rounding_method)
        else:
            f = StringIO(path_to_timestamps_file_or_content)
            timestamps, last_frame_time, fpms = TimestampsFileParser.parse_file(f, rounding_method)

        return Timestamps(
            rounding_method=rounding_method,
            timestamps=timestamps,
            normalize=normalize,
            fpms=fpms,
            last_frame_time=last_frame_time,
        )


    @staticmethod
    def from_video_file(
        video_path: Path,
        index: int = 0,
        normalize: bool = True,
        rounding_method: RoundingMethod = RoundingMethod.ROUND,
    ) -> Timestamps:
        """Create timestamps based on the ``video_path`` provided.

        Note:
            This method requires the ``ffprobe`` or ``mkvextract/mkvmerge`` programs to be available.

        Parameters:
            video_path (Path): A video path.
            index (int, optional): Index of the video stream.
            normalize (bool, optional): If True, it will shift the timestamps to make them start from 0. If false, the option does nothing.
            rounding_method (RoundingMethod, optional): A rounding method. See the comment in Timestamps class about FLOOR vs ROUND.
        Returns:
            An Timestamps instance.
        """

        if not video_path.is_file():
            raise FileNotFoundError(f'Invalid path for the video file: "{video_path}"')
        
        is_file_mkv = MKVUtils.is_mkv(video_path)

        video_parser: Optional[ABCVideoParser] = None
        if is_file_mkv and MKVToolNixTimestamps.is_available():
            video_parser = MKVToolNixTimestamps()
        elif FFprobeTimestamps.is_available():
            video_parser = FFprobeTimestamps()
        else:
            raise OSError("MKVToolNix and/or FFprobe aren't in your environment variable. Note that if your video isn't a mkv, you absolutely need FFprobe.")

        timestamps, time_scale = video_parser.get_timestamps(video_path, index, normalize, rounding_method)
    
        if is_file_mkv:
            # We only do this check for .mkv file. See the note about mkv in the Timestamps class documentation.
            # 1/1000 represent 1 ms. If the time_base cannot divided by 1/1000, then it means that the timestamps aren't rounded to milliseconds.
            precision_ms = Fraction(1, 1000)
            is_precision_higher_ms = time_scale % precision_ms

            if is_precision_higher_ms and rounding_method == RoundingMethod.ROUND:
                warn(
                    "Your mkv file isn't perfectly rounded to ms or cs. In this situation, you may prefer to use RoundingMethod.FLOOR then RoundingMethod.ROUND.",
                    UserWarning,
                )
            elif not is_precision_higher_ms and rounding_method == RoundingMethod.FLOOR:
                warn(
                    "Your mkv file is perfectly rounded to ms or cs. In this situation, you may prefer to use RoundingMethod.ROUND then RoundingMethod.FLOOR.",
                    UserWarning,
                )

        return timestamps
