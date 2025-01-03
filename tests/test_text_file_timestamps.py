import os
from fractions import Fraction
from pathlib import Path
from video_timestamps import RoundingMethod, TextFileTimestamps

dir_path = Path(os.path.dirname(os.path.realpath(__file__)))


def test_init_v2() -> None:
    timestamps_str = (
        "# timecode format v2\n"
        "0\n"
        "1000\n"
        "1500\n"
        "2000\n"
        "2001\n"
        "2002\n"
        "2003\n"
    )
    time_scale = Fraction(1000)
    rounding_method = RoundingMethod.ROUND

    timestamps = TextFileTimestamps(timestamps_str, time_scale, rounding_method, approximate_pts_from_last_pts=True)

    assert timestamps.time_scale == Fraction(1000)
    assert timestamps.rounding_method == RoundingMethod.ROUND
    assert timestamps.fps == Fraction(6, Fraction(2003, 1000))
    assert timestamps.approximate_pts_from_last_pts is True
    assert timestamps.pts_list == [0, 1000, 1500, 2000, 2001, 2002, 2003]


def test_init_from_file() -> None:
    timestamp_file_path = dir_path.joinpath("files", "timestamps.txt")
    time_scale = Fraction(1000)
    rounding_method = RoundingMethod.ROUND

    timestamps = TextFileTimestamps(timestamp_file_path, time_scale, rounding_method)

    assert timestamps.time_scale == Fraction(1000)
    assert timestamps.rounding_method == RoundingMethod.ROUND
    assert timestamps.fps == Fraction(2, Fraction(100, 1000))
    assert timestamps.approximate_pts_from_last_pts is False
    assert timestamps.pts_list == [0, 50, 100]


def test__eq__and__hash__() -> None:
    timestamps_str = (
        "# timecode format v2\n"
        "0\n"
        "1000\n"
        "1500\n"
        "2000\n"
        "2001\n"
        "2002\n"
        "2003\n"
    )
    timestamps_1 = TextFileTimestamps(timestamps_str, Fraction(1000), RoundingMethod.ROUND, True, None, True)
    timestamps_2 = TextFileTimestamps(timestamps_str, Fraction(1000), RoundingMethod.ROUND, True, None, True)
    assert timestamps_1 == timestamps_2
    assert hash(timestamps_1) == hash(timestamps_2)

    timestamps_3_str = (
        "# timecode format v2\n"
        "0\n"
        "1000\n"
        "1500\n"
    )
    timestamps_3 = TextFileTimestamps(
        timestamps_3_str, # different
        Fraction(1000),
        RoundingMethod.ROUND,
        True,
        None,
        True
    )
    assert timestamps_1 != timestamps_3
    assert hash(timestamps_1) != hash(timestamps_3)

    timestamps_4 = TextFileTimestamps(
        timestamps_str,
        Fraction(1001), # different
        RoundingMethod.ROUND,
        True,
        None,
        True
    )
    assert timestamps_1 != timestamps_4
    assert hash(timestamps_1) != hash(timestamps_4)

    timestamps_5 = TextFileTimestamps(
        timestamps_str,
        Fraction(1000),
        RoundingMethod.FLOOR, # different
        True,
        None,
        True
    )
    assert timestamps_1 != timestamps_5
    assert hash(timestamps_1) != hash(timestamps_5)

    timestamps_6 = TextFileTimestamps(
        timestamps_str,
        Fraction(1000),
        RoundingMethod.ROUND,
        True,
        Fraction(1), # different
        True
    )
    assert timestamps_1 != timestamps_6
    assert hash(timestamps_1) != hash(timestamps_6)

    timestamps_7 = TextFileTimestamps(
        timestamps_str,
        Fraction(1000),
        RoundingMethod.ROUND,
        True,
        None,
        False # different
    )
    assert timestamps_1 != timestamps_7
    assert hash(timestamps_1) != hash(timestamps_7)
