import os
import pytest
from fractions import Fraction
from pathlib import Path
from video_timestamps import RoundingMethod, VideoTimestamps

dir_path = Path(os.path.dirname(os.path.realpath(__file__)))


def test__init__() -> None:
    pts_list = [0, 42, 83, 125, 167, 209, 250, 292, 334, 375]
    time_scale = Fraction(1000)
    normalize = False
    fps = Fraction(24000, 1001)
    rounding_method = RoundingMethod.ROUND
    timestamps = VideoTimestamps(
        pts_list,
        time_scale,
        normalize,
        fps,
        rounding_method
    )

    assert timestamps.pts_list == pts_list
    assert timestamps.time_scale == time_scale
    assert timestamps.fps == fps
    assert timestamps.rounding_method == rounding_method
    assert timestamps.timestamps == [
        Fraction(0, 1000),
        Fraction(42, 1000),
        Fraction(83, 1000),
        Fraction(125, 1000),
        Fraction(167, 1000),
        Fraction(209, 1000),
        Fraction(250, 1000),
        Fraction(292, 1000),
        Fraction(334, 1000),
        Fraction(375, 1000)
    ]


def test__init__validate() -> None:
    with pytest.raises(ValueError) as exc_info:
        VideoTimestamps([0], Fraction(1000))
    assert str(exc_info.value) == "There must be at least 2 timestamps."

    with pytest.raises(ValueError) as exc_info:
        VideoTimestamps([0, 42, 20], Fraction(1000))
    assert str(exc_info.value) == "Timestamps must be in non-decreasing order."

    with pytest.raises(ValueError) as exc_info:
        VideoTimestamps([20, 20], Fraction(1000))
    assert str(exc_info.value) == "Timestamps must be in non-decreasing order."

    with pytest.raises(ValueError) as exc_info:
        VideoTimestamps([0, 40, 50, 50], Fraction(1000))
    assert str(exc_info.value) == "Timestamps must be in non-decreasing order."



def test__init__fps() -> None:
    timestamps = VideoTimestamps([0, 3000, 3500], Fraction(90000))
    assert timestamps.fps == Fraction(2, Fraction(3500, 90000))


def test_from_video() -> None:
    video_file_path = dir_path.joinpath("files", "test_video.mkv")
    timestamps = VideoTimestamps.from_video_file(video_file_path)
    assert timestamps.pts_list[:10] == [0, 42, 83, 125, 167, 209, 250, 292, 334, 375]
    assert timestamps.time_scale == Fraction(1000)
    assert timestamps.fps == Fraction(24000, 1001)


def test_normalize() -> None:
    pts_list = [10, 20, 30]
    assert VideoTimestamps.normalize(pts_list) == [0, 10, 20]

    pts_list = [0, 10, 20]
    assert VideoTimestamps.normalize(pts_list) == [0, 10, 20]

    timestamps = VideoTimestamps([10, 20, 30], Fraction(1000))
    assert timestamps.pts_list == [0, 10, 20]

    timestamps = VideoTimestamps([10, 20, 30], Fraction(1000), False)
    assert timestamps.pts_list == [10, 20, 30]


def test_guess_rounding_method_round() -> None:
    pts_list = [0, 42, 83, 125, 167, 209, 250, 292, 334, 375]
    time_scale = Fraction(1000)
    fps = Fraction(24000, 1001)

    assert VideoTimestamps.guess_rounding_method(pts_list, time_scale, fps) == RoundingMethod.ROUND


def test_guess_rounding_method_floor() -> None:
    pts_list = [0, 41, 83, 125, 166, 208, 250, 291, 333, 375]
    time_scale = Fraction(1000)
    fps = Fraction(24000, 1001)

    assert VideoTimestamps.guess_rounding_method(pts_list, time_scale, fps) == RoundingMethod.FLOOR


def test_guess_rounding_method_vfr() -> None:
    pts_list = [0, 40, 60, 100, 110]
    time_scale = Fraction(1000)
    fps = Fraction(24000, 1001)

    assert VideoTimestamps.guess_rounding_method(pts_list, time_scale, fps) == RoundingMethod.FLOOR


def test__eq__and__hash__() -> None:
    video_1 = VideoTimestamps([0, 42, 83], Fraction(1000), True, None, RoundingMethod.FLOOR, False)
    video_2 = VideoTimestamps([0, 42, 83], Fraction(1000), True, None, RoundingMethod.FLOOR, False)
    assert video_1 == video_2
    assert hash(video_1) == hash(video_2)

    video_3 = VideoTimestamps(
        [0, 42, 100], # different
        Fraction(1000),
        True,
        None,
        RoundingMethod.FLOOR,
        False
    )
    assert video_1 != video_3
    assert hash(video_1) != hash(video_3)

    video_4 = VideoTimestamps(
        [0, 42, 83],
        Fraction(1001), # different
        True,
        None,
        RoundingMethod.FLOOR,
        False
    )
    assert video_1 != video_4
    assert hash(video_1) != hash(video_4)

    video_5 = VideoTimestamps(
        [0, 42, 83],
        Fraction(1000),
        True,
        Fraction(1), # different
        RoundingMethod.FLOOR,
        False
    )
    assert video_1 != video_5
    assert hash(video_1) != hash(video_5)

    video_6 = VideoTimestamps(
        [0, 42, 83],
        Fraction(1000),
        True,
        None,
        RoundingMethod.ROUND, # different
        False
    )
    assert video_1 != video_6
    assert hash(video_1) != hash(video_6)

    video_7 = VideoTimestamps(
        [0, 42, 83],
        Fraction(1000),
        True,
        None,
        RoundingMethod.FLOOR,
        True # different
    )
    assert video_1 != video_7
    assert hash(video_1) != hash(video_7)
