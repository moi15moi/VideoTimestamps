import pytest
from io import StringIO
from video_timestamps.timestamps_file_parser import TimestampsFileParser


def test_missing_timestamps_version() -> None:
    timestamps_str = "invalid timestamps"
    f = StringIO(timestamps_str)

    with pytest.raises(ValueError) as exc_info:
        TimestampsFileParser.parse_file(f)
    assert str(exc_info.value) == "The line 0 is invalid doesn't contain the version of the timestamps file."


def test_invalid_timestamps_version() -> None:
    timestamps_str = "# timecode format v3"
    f = StringIO(timestamps_str)

    with pytest.raises(NotImplementedError) as exc_info:
        TimestampsFileParser.parse_file(f)
    assert str(exc_info.value) == "The file uses version 3, but this format is currently not supported."
