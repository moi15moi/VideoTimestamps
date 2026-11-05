from fractions import Fraction
from io import StringIO

import pytest

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


def test_v1_only_assume_line() -> None:
    timestamps_str = "# timestamp format v1\nAssume 25"
    f = StringIO(timestamps_str)

    timestamps, fps, version = TimestampsFileParser.parse_file(f)

    assert timestamps == [Fraction(0), Fraction(40)]
    assert fps == Fraction(25)
    assert version == 1


def test_v1_zero_fps_range_is_ignored() -> None:
    timestamps_str = "# timestamp format v1\nAssume 25\n0,1,0\n2,2,50"
    f = StringIO(timestamps_str)

    timestamps, fps, version = TimestampsFileParser.parse_file(f)

    assert timestamps == [Fraction(0), Fraction(40), Fraction(80), Fraction(100)]
    assert fps == Fraction(25)
    assert version == 1


def test_v1_negative_fps_range() -> None:
    timestamps_str = "# timestamp format v1\nAssume 25\n0,10,-1"
    f = StringIO(timestamps_str)

    with pytest.raises(ValueError) as exc_info:
        TimestampsFileParser.parse_file(f)
    assert str(exc_info.value) == "FPS must be greater than or equal to zero."
