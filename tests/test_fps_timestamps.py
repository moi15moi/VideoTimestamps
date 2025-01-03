import pytest
from fractions import Fraction
from video_timestamps import FPSTimestamps, RoundingMethod


def test__init__() -> None:
    rounding_method = RoundingMethod.ROUND
    time_scale = Fraction(1000)
    fps = Fraction(24000, 1001)
    timestamps = FPSTimestamps(
        rounding_method,
        time_scale,
        fps,
    )

    assert timestamps.rounding_method == rounding_method
    assert timestamps.time_scale == time_scale
    assert timestamps.fps == fps
    assert timestamps.first_pts == 0


def test_invalid_time_scale() -> None:
    rounding_method = RoundingMethod.ROUND
    time_scale = Fraction(-1)
    fps = Fraction(24000, 1001)

    with pytest.raises(ValueError) as exc_info:
        FPSTimestamps(rounding_method, time_scale, fps)
    assert str(exc_info.value) == "Parameter ``time_scale`` must be higher than 0."


def test_invalid_fps() -> None:
    rounding_method = RoundingMethod.ROUND
    time_scale = Fraction(1000)
    fps = Fraction(-1)

    with pytest.raises(ValueError) as exc_info:
        FPSTimestamps(rounding_method, time_scale, fps)
    assert str(exc_info.value) == "Parameter ``fps`` must be higher than 0."


def test__eq__and__hash__() -> None:
    fps_1 = FPSTimestamps(RoundingMethod.ROUND, Fraction(1000), Fraction(24000, 1001), 0)
    fps_2 = FPSTimestamps(RoundingMethod.ROUND, Fraction(1000), Fraction(24000, 1001), 0)
    assert fps_1 == fps_2
    assert hash(fps_1) == hash(fps_2)

    fps_3 = FPSTimestamps(
        RoundingMethod.FLOOR, # different
        Fraction(1000),
        Fraction(24000, 1001),
        0
    )
    assert fps_1 != fps_3
    assert hash(fps_1) != hash(fps_3)

    fps_4 = FPSTimestamps(
        RoundingMethod.ROUND,
        Fraction(1001), # different
        Fraction(24000, 1001),
        0
    )
    assert fps_1 != fps_4
    assert hash(fps_1) != hash(fps_4)

    fps_5 = FPSTimestamps(
        RoundingMethod.ROUND,
        Fraction(1000),
        Fraction(1), # different
        0
    )
    assert fps_1 != fps_5
    assert hash(fps_1) != hash(fps_5)

    fps_6 = FPSTimestamps(
        RoundingMethod.ROUND,
        Fraction(1000),
        Fraction(24000, 1001),
        10 # different
    )
    assert fps_1 != fps_6
    assert hash(fps_1) != hash(fps_6)
