import os
import runpy
from pathlib import Path

import pytest

dir_path = os.path.dirname(os.path.realpath(__file__))


def test_extracttimestamps(monkeypatch: pytest.MonkeyPatch) -> None:
    expected_timestamps_file = Path(os.path.join(dir_path, "files", "test_video_10_frames_0.txt"))
    assert not expected_timestamps_file.is_file()

    monkeypatch.setattr(
        "sys.argv",
        [
            "extracttimestamps",
            os.path.join(dir_path, "files", "test_video_10_frames.mkv"),
        ],
    )

    runpy.run_module(
        "video_timestamps.extract_timestamps",
        run_name="__main__",
    )

    assert expected_timestamps_file.is_file()

    expected = (
        "# timestamp format v2\n"
        "0\n"
        "50\n"
        "100\n"
        "150\n"
        "200\n"
        "250\n"
        "300\n"
        "350\n"
        "400\n"
        "450\n"
        "475\n"
    )

    content = expected_timestamps_file.read_text(encoding="utf-8")
    assert content == expected

    expected_timestamps_file.unlink()


def test_extracttimestamps_precision_round(monkeypatch: pytest.MonkeyPatch) -> None:
    expected_timestamps_file = Path(os.path.join(dir_path, "files", "test_extracttimestamps_precision_round.txt"))
    assert not expected_timestamps_file.is_file()

    monkeypatch.setattr(
        "sys.argv",
        [
            "extracttimestamps",
            os.path.join(dir_path, "files", "test_video.mp4"),
            "-o", str(expected_timestamps_file.resolve()),
            "--precision", "15"
        ],
    )

    runpy.run_module(
        "video_timestamps.extract_timestamps",
        run_name="__main__",
    )

    assert expected_timestamps_file.is_file()

    expected = (
        "# timestamp format v2\n"
        "0\n"
        "41.708333333333\n"
        "83.416666666667\n"
        "125.125\n"
        "166.833333333333\n"
        "208.541666666667\n"
        "250.25\n"
        "291.958333333333\n"
        "333.666666666667\n"
        "375.375\n"
    )

    content = expected_timestamps_file.read_text(encoding="utf-8")
    assert content.startswith(expected)

    expected_timestamps_file.unlink()


def test_extracttimestamps_precision_floor(monkeypatch: pytest.MonkeyPatch) -> None:
    expected_timestamps_file = Path(os.path.join(dir_path, "files", "test_extracttimestamps_precision_floor.txt"))
    assert not expected_timestamps_file.is_file()

    monkeypatch.setattr(
        "sys.argv",
        [
            "extracttimestamps",
            os.path.join(dir_path, "files", "test_video.mp4"),
            "-o", str(expected_timestamps_file.resolve()),
            "--precision", "15",
            "--precision-rounding", "floor"
        ],
    )

    runpy.run_module(
        "video_timestamps.extract_timestamps",
        run_name="__main__",
    )

    assert expected_timestamps_file.is_file()

    expected = (
        "# timestamp format v2\n"
        "0\n"
        "41.708333333333\n"
        "83.416666666666\n"
        "125.125\n"
        "166.833333333333\n"
        "208.541666666666\n"
        "250.25\n"
        "291.958333333333\n"
        "333.666666666666\n"
        "375.375\n"
    )

    content = expected_timestamps_file.read_text(encoding="utf-8")
    assert content.startswith(expected)

    expected_timestamps_file.unlink()


def test_extracttimestamps_use_fraction(monkeypatch: pytest.MonkeyPatch) -> None:
    expected_timestamps_file = Path(os.path.join(dir_path, "files", "test_extracttimestamps_use_fraction.txt"))
    assert not expected_timestamps_file.is_file()

    monkeypatch.setattr(
        "sys.argv",
        [
            "extracttimestamps",
            os.path.join(dir_path, "files", "test_video.mp4"),
            "-o", str(expected_timestamps_file.resolve()),
            "--use-fraction"
        ],
    )

    runpy.run_module(
        "video_timestamps.extract_timestamps",
        run_name="__main__",
    )

    assert expected_timestamps_file.is_file()

    expected = (
        "# timestamp format v2\n"
        "0\n"
        "1001/24\n"
        "1001/12\n"
        "1001/8\n"
        "1001/6\n"
        "5005/24\n"
        "1001/4\n"
        "7007/24\n"
        "1001/3\n"
        "3003/8\n"
    )

    content = expected_timestamps_file.read_text(encoding="utf-8")
    assert content.startswith(expected)

    expected_timestamps_file.unlink()
