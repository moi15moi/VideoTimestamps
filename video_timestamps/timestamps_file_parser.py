from .rounding_method import RoundingMethod
from fractions import Fraction
from io import TextIOWrapper
from re import compile
from typing import List, Tuple


class RangeV1:
    def __init__(self, start_frame: int, end_frame: int, fps: Fraction):
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.fps = fps


class TimestampsFileParser:
    @staticmethod
    def parse_file(
        file_content: TextIOWrapper, rounding_method: RoundingMethod
    ) -> Tuple[List[int], Fraction, Fraction]:
        """Parse timestamps from a [timestamps file](https://mkvtoolnix.download/doc/mkvmerge.html#mkvmerge.external_timestamp_files) and return them.

        Inspired by: https://gitlab.com/mbunkus/mkvtoolnix/-/blob/72dfe260effcbd0e7d7cf6998c12bb35308c004f/src/merge/timestamp_factory.cpp#L27-74

        Parameters:
            file_content (TextIOWrapper): The timestamps content
            rounding_method (RoundingMethod): A rounding method

        Returns:
            A tuple containing these 3 informations:
                1. A list of each timestamps rounded or floored to milliseconds.
                2. The last timestamps not rounded
                3. If the format of timestamps is 1, then it return the fpms of the Assume section
                   If the format of timestamps is 2 or 4, then it approximate the fpms.
                        It calculate the fps like this: (1000 * nbr_frame) / (last_timestamps - first_timestamps)
        """

        regex_timestamps = compile("^# time(?:code|stamp) *format v(\\d+).*")

        line = file_content.readline()
        match = regex_timestamps.search(line)
        if match is None:
            raise ValueError(
                f'The timestamps at line 0 is invalid. Here is the line: "{line}"'
            )

        version = int(match.group(1))

        if version == 1:
            timestamps, last_frame_time, fpms = TimestampsFileParser._parse_v1_file(
                file_content, rounding_method
            )
        elif version == 2 or version == 4:
            (
                timestamps,
                last_frame_time,
                fpms,
            ) = TimestampsFileParser._parse_v2_and_v4_file(
                file_content, version, rounding_method
            )
        else:
            raise NotImplementedError(
                f"The file uses version {version} for its timestamps, but this format is currently not compatible with PyonFX."
            )

        return timestamps, last_frame_time, fpms


    @staticmethod
    def _parse_v1_file(
        file_content: TextIOWrapper, rounding_method: RoundingMethod
    ) -> Tuple[List[int], Fraction, Fraction]:
        """Create timestamps based on the timestamps v1 file provided.

        Inspired by: https://gitlab.com/mbunkus/mkvtoolnix/-/blob/72dfe260effcbd0e7d7cf6998c12bb35308c004f/src/merge/timestamp_factory.cpp#L82-175

        Parameters:
            file_content (TextIOWrapper): The timestamps content
            rounding_method (RoundingMethod): A rounding method

        Returns:
            A tuple containing these 3 informations:
                1. A list of each timestamps rounded to milliseconds
                2. The last timestamps not rounded
                3. The fpms (frame(s) per milliseconds)
        """
        timestamps: List[int] = []
        ranges_v1: List[RangeV1] = []
        line: str = ""

        for line in file_content:
            if not line:
                raise ValueError(
                    f"The timestamps file does not contain a valid 'Assume' line with the default number of frames per second."
                )
            line = line.strip(" \t")

            if line and not line.startswith("#"):
                break

        if not line.lower().startswith("assume "):
            raise ValueError(
                f"The timestamps file does not contain a valid 'Assume' line with the default number of frames per second."
            )

        line = line[7:].strip(" \t")
        try:
            default_fps = Fraction(line)
        except ValueError:
            raise ValueError(
                f"The timestamps file does not contain a valid 'Assume' line with the default number of frames per second."
            )

        for line in file_content:
            line = line.strip(" \t\n\r")

            if not line or line.startswith("#"):
                continue

            line_splitted = line.split(",")
            if len(line_splitted) != 3:
                raise ValueError(
                    f'The timestamps file contain a invalid line. Here is it: "{line}"'
                )
            try:
                start_frame = int(line_splitted[0])
                end_frame = int(line_splitted[1])
                fps = Fraction(line_splitted[2])
            except ValueError:
                raise ValueError(
                    f'The timestamps file contain a invalid line. Here is it: "{line}"'
                )

            range_v1 = RangeV1(start_frame, end_frame, fps)

            if range_v1.start_frame < 0 or range_v1.end_frame < 0:
                raise ValueError("Cannot specify frame rate for negative frames.")
            if range_v1.end_frame < range_v1.start_frame:
                raise ValueError(
                    "End frame must be greater than or equal to start frame."
                )
            if range_v1.fps <= 0:
                raise ValueError("FPS must be greater than zero.")
            elif range_v1.fps == 0:
                # mkvmerge allow fps to 0, but we can ignore them, since they won't impact the timestamps
                continue

            ranges_v1.append(range_v1)

        ranges_v1.sort(key=lambda x: x.start_frame)

        time: Fraction = Fraction(0)
        frame: int = 0
        for range_v1 in ranges_v1:
            if frame > range_v1.start_frame:
                raise ValueError("Override ranges must not overlap.")

            while frame < range_v1.start_frame:
                timestamps.append(rounding_method(time)) 
                time += Fraction(1000) / default_fps
                frame += 1

            while frame <= range_v1.end_frame:
                timestamps.append(rounding_method(time)) 
                time += Fraction(1000) / range_v1.fps
                frame += 1

        timestamps.append(rounding_method(time)) 
        fpms = default_fps / Fraction(1000)
        return timestamps, time, fpms


    @staticmethod
    def _parse_v2_and_v4_file(
        file_content: TextIOWrapper, version: int, rounding_method: RoundingMethod
    ) -> Tuple[List[int], Fraction, Fraction]:
        """Create timestamps based on the timestamps v2 or v4 file provided.

        Inspired by: https://gitlab.com/mbunkus/mkvtoolnix/-/blob/72dfe260effcbd0e7d7cf6998c12bb35308c004f/src/merge/timestamp_factory.cpp#L201-267

        Parameters:
            file_content (TextIOWrapper): The timestamps content
            version (int): The version of the timestamps (only 2 or 4 is allowed)
            rounding_method (RoundingMethod): A rounding method

        Returns:
            A tuple containing these 3 informations:
                1. A list of each timestamps rounded to milliseconds
                2. The last timestamps not rounded
                3. The fpms (frame(s) per milliseconds)
        """

        if version not in (2, 4):
            raise ValueError("You can only specify version 2 or 4.")

        timestamps: List[int] = []
        previous_timestamp: int = 0
        lowest_timestamp: Fraction = None # type: ignore
        highest_timestamp: Fraction = None # type: ignore

        for line in file_content:
            line = line.strip(" \t")

            if not line or line.startswith("#"):
                continue

            try:
                timestamp = Fraction(line)
            except ValueError:
                raise ValueError(
                    f'The timestamps file contain a invalid line. Here is it: "{line}"'
                )

            if highest_timestamp is None or highest_timestamp < timestamp:
                highest_timestamp = timestamp
            if lowest_timestamp is None or lowest_timestamp > timestamp:
                lowest_timestamp = timestamp

            rounded_timestamp = rounding_method(timestamp) 

            if version == 2 and rounded_timestamp < previous_timestamp:
                raise ValueError(
                    f"The timestamps file contain timestamps NOT in ascending order."
                )

            previous_timestamp = rounded_timestamp
            timestamps.append(rounded_timestamp)

        if not len(timestamps):
            raise ValueError(f"The timestamps file is empty.")

        if version == 4:
            timestamps.sort()

        duration = highest_timestamp - lowest_timestamp
        if duration:
            fpms = Fraction(len(timestamps) - 1) / (highest_timestamp - lowest_timestamp)
        else:
            fpms = Fraction(0)
        return timestamps, highest_timestamp, fpms
