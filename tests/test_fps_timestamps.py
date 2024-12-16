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
