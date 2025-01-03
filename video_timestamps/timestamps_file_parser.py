from fractions import Fraction
from io import TextIOBase
from re import compile
from typing import Optional


class TimestampsFileParser:
    @staticmethod
    def parse_file(file_content: TextIOBase) -> list[Fraction]:
        """Parse timestamps from a [timestamps file](https://mkvtoolnix.download/doc/mkvmerge.html#mkvmerge.external_timestamp_files) and return them.

        Inspired by: https://gitlab.com/mbunkus/mkvtoolnix/-/blob/72dfe260effcbd0e7d7cf6998c12bb35308c004f/src/merge/timestamp_factory.cpp#L27-74

        Parameters:
            file_content (TextIOBase): The timestamps content.

        Returns:
            A list of each frame timestamps (in milliseconds).
        """

        regex_timestamps = compile("^# *time(?:code|stamp) *format v(\\d+).*")
        line = file_content.readline()
        match = regex_timestamps.search(line)
        if match is None:
            raise ValueError("The line 0 is invalid doesn't contain the version of the timestamps file.")

        version = int(match.group(1))

        if version == 2 or version == 4:
            timestamps = TimestampsFileParser._parse_v2_and_v4_file(file_content, version)
        else:
            raise NotImplementedError(
                f"The file uses version {version}, but this format is currently not supported."
            )

        return timestamps


    @staticmethod
    def _parse_v2_and_v4_file(
        file_content: TextIOBase, version: int
    ) -> list[Fraction]:
        """Create timestamps based on the timestamps v2 or v4 file provided.

        Inspired by: https://gitlab.com/mbunkus/mkvtoolnix/-/blob/72dfe260effcbd0e7d7cf6998c12bb35308c004f/src/merge/timestamp_factory.cpp#L201-267

        Parameters:
            file_content (TextIOBase): The timestamps content
            version (int): The version of the timestamps (only 2 or 4 is allowed)

        Returns:
            A list of each frame timestamps (in milliseconds).
        """

        if version not in (2, 4):
            raise ValueError("You can only specify version 2 or 4.")

        timestamps: list[Fraction] = []
        previous_timestamp: Optional[Fraction] = None

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
