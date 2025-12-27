from fractions import Fraction
from io import TextIOBase
from re import compile


class RangeV1:
    def __init__(self, start_frame: int, end_frame: int, fps: Fraction):
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.fps = fps


class TimestampsFileParser:
    @staticmethod
    def parse_file(file_content: TextIOBase) -> tuple[list[Fraction], Fraction | None, int]:
        """Parse timestamps from a [timestamps file](https://mkvtoolnix.download/doc/mkvmerge.html#mkvmerge.external_timestamp_files) and return them.

        Inspired by: https://gitlab.com/mbunkus/mkvtoolnix/-/blob/72dfe260effcbd0e7d7cf6998c12bb35308c004f/src/merge/timestamp_factory.cpp#L27-74

        Parameters:
            file_content: The timestamps content.

        Returns:
            A tuple containing these 3 informations:
                1. A list of each frame timestamps (in milliseconds).
                2. The fps (if supported by the timestamps file format).
                3. The version of the timestamps file (1, 2 or 4).
        """

        regex_timestamps = compile("^# *time(?:code|stamp) *format v(\\d+).*")
        line = file_content.readline()
        match = regex_timestamps.search(line)
        if match is None:
            raise ValueError("The line 0 is invalid doesn't contain the version of the timestamps file.")

        version = int(match.group(1))

        if version == 1:
            timestamps, fps = TimestampsFileParser._parse_v1_file(file_content)
        elif version == 2 or version == 4:
            timestamps = TimestampsFileParser._parse_v2_and_v4_file(file_content, version)
            fps = None
        else:
            raise NotImplementedError(
                f"The file uses version {version}, but this format is currently not supported."
            )

        return timestamps, fps, version


    @staticmethod
    def _parse_v1_file(file_content: TextIOBase) -> tuple[list[Fraction], Fraction]:
        """Create timestamps based on the timestamps v1 file provided.

        Inspired by: https://gitlab.com/mbunkus/mkvtoolnix/-/blob/72dfe260effcbd0e7d7cf6998c12bb35308c004f/src/merge/timestamp_factory.cpp#L82-175

        Parameters:
            file_content: The timestamps content

        Returns:
            A tuple containing these 2 informations:
                1. A list of each frame timestamps (in milliseconds).
                2. The fps.
        """
        timestamps: list[Fraction] = []
        ranges_v1: list[RangeV1] = []
        line: str = ""

        file_lines = file_content.read().splitlines()
        file_iterator = iter(file_lines)

        for line in file_iterator:
            if not line:
                raise ValueError(
                    "The timestamps file does not contain a valid 'Assume' line with the default number of frames per second."
                )
            line = line.strip(" \t")

            if line and not line.startswith("#"):
                break

        if not line.lower().startswith("assume "):
            raise ValueError(
                "The timestamps file does not contain a valid 'Assume' line with the default number of frames per second."
            )

        line = line[7:].strip(" \t")
        try:
            default_fps = Fraction(line)
        except ValueError:
            raise ValueError(
                "The timestamps file does not contain a valid 'Assume' line with the default number of frames per second."
            )

        for line in file_iterator:
            line = line.strip(" \t")

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
                timestamps.append(time)
                time += Fraction(1000) / default_fps
                frame += 1

            while frame <= range_v1.end_frame:
                timestamps.append(time)
                time += Fraction(1000) / range_v1.fps
                frame += 1

        timestamps.append(time)
        return timestamps, default_fps


    @staticmethod
    def _parse_v2_and_v4_file(
        file_content: TextIOBase, version: int
    ) -> list[Fraction]:
        """Create timestamps based on the timestamps v2 or v4 file provided.

        Inspired by: https://gitlab.com/mbunkus/mkvtoolnix/-/blob/72dfe260effcbd0e7d7cf6998c12bb35308c004f/src/merge/timestamp_factory.cpp#L201-267

        Parameters:
            file_content: The timestamps content
            version: The version of the timestamps (only 2 or 4 is allowed)

        Returns:
            A list of each frame timestamps (in milliseconds).
        """

        if version not in (2, 4):
            raise ValueError("You can only specify version 2 or 4.")

        timestamps: list[Fraction] = []
        previous_timestamp: Fraction | None = None

        for line in file_content.read().splitlines():
            line = line.strip(" \t")

            if not line or line.startswith("#"):
                continue

            try:
                timestamp = Fraction(line)
            except ValueError:
                raise ValueError(
                    f'The timestamps file contain a invalid line. Here is it: "{line}"'
                )

            if version == 2 and previous_timestamp is not None and timestamp < previous_timestamp:
                raise ValueError(
                    "The timestamps file contain timestamps NOT in ascending order."
                )

            previous_timestamp = timestamp
            timestamps.append(timestamp)

        if not len(timestamps):
            raise ValueError("The timestamps file is empty.")

        if version == 4:
            timestamps.sort()

        return timestamps
