import os
from fractions import Fraction
from pathlib import Path

import pytest

from video_timestamps import TimeUnitConverter

dir_path = Path(os.path.dirname(os.path.realpath(__file__)))


def test_time_base_to_time_scale() -> None:
    time_base = Fraction(1, 75)
    expected_time_scale = Fraction(75)
    assert TimeUnitConverter.time_base_to_time_scale(time_base) == expected_time_scale

    time_base = Fraction(24000, 1001)
    expected_time_scale = Fraction(1001, 24000)
    assert TimeUnitConverter.time_base_to_time_scale(time_base) == expected_time_scale


def test_time_scale_to_time_base() -> None:
    time_scale = Fraction(75)
    expected_time_base = Fraction(1, 75)
    assert TimeUnitConverter.time_scale_to_time_base(time_scale) == expected_time_base

    time_scale = Fraction(1001, 24000)
    expected_time_base = Fraction(24000, 1001)
    assert TimeUnitConverter.time_scale_to_time_base(time_scale) == expected_time_base


def test_timestamp_scale_to_time_scale() -> None:
    timestamp_scale = 1000
    expected_time_scale = Fraction(pow(10, 6))
    assert TimeUnitConverter.timestamp_scale_to_time_scale(timestamp_scale) == expected_time_scale


def test_time_scale_to_timestamp_scale() -> None:
    time_scale = Fraction(pow(10, 6))
    expected_timestamp_scale = 1000
    assert TimeUnitConverter.time_scale_to_timestamp_scale(time_scale) == expected_timestamp_scale

    time_scale = Fraction(90000)
    with pytest.raises(ValueError) as exc_info:
        TimeUnitConverter.time_scale_to_timestamp_scale(time_scale)
    assert str(exc_info.value) == f"The timescale {time_scale} cannot be converted to a timestamp scale because the result 100000/9 isn't a integer."


def test_timestamp_scale_to_time_base() -> None:
    timestamp_scale = 1000
    expected_time_base = Fraction(1, pow(10, 6))
    assert TimeUnitConverter.timestamp_scale_to_time_base(timestamp_scale) == expected_time_base


def test_time_base_to_timestamp_scale() -> None:
    time_base = Fraction(1, pow(10, 6))
    expected_timestamp_scale = 1000
    assert TimeUnitConverter.time_base_to_timestamp_scale(time_base) == expected_timestamp_scale

    time_base = Fraction(1, 90000)
    with pytest.raises(ValueError) as exc_info:
        TimeUnitConverter.time_base_to_timestamp_scale(time_base)
    assert str(exc_info.value) == f"The timebase {time_base} cannot be converted to a timestamp scale because the result 100000/9 isn't a integer."
