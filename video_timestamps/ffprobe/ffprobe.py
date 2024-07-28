from ..rounding_method import RoundingMethod
import json
import sys
from fractions import Fraction
from subprocess import CompletedProcess, run
from pathlib import Path
from shutil import which
from typing import Any

__all__ = ["FFprobe"]


class FFprobe:
    """
    This class is a collection of static methods that will help
    the user to interact with FFprobe.
    """

    PROGRAM_NAME = "ffprobe"

    @staticmethod
    def is_ffprobe_installed() -> bool:
        """
        Checks if the `ffprobe` program is installed and available in the system's PATH.

        Returns:
            True if `ffprobe` is installed, False otherwise.
        """
        return which("ffprobe") is not None

    @staticmethod
    def verify_if_ffprobe_is_installed() -> None:
        """
        Verifies if the `mkvextract` program is installed. Raises an error if not found.

        Raises:
            Exception: If `mkvextract` is not found in the system's PATH.
        """
        if not FFprobe.is_ffprobe_installed():
            raise Exception("ffprobe is not in the environment variable.")


    @staticmethod
    def verify_if_command_fails(cmd_output: CompletedProcess[str]) -> None:
        """Checks the result of a command execution and raises an error or warning based on the exit code.

        Parameters:
            cmd_output (CompletedProcess): The result of the command execution.

        Raises:
            OSError: If the command reported an error.
        """

        if cmd_output.returncode != 0:
            raise OSError(f"{FFprobe.PROGRAM_NAME} reported an error: '{cmd_output.stderr}'.")


    @staticmethod
    def run_command(cmd: list[Any]) -> CompletedProcess[str]:
        """Runs a command and verifies if it fails.

        Parameters:
            cmd (List[Any]): The command to be run, including its arguments.

        Returns:
            The result of the command execution.
        """

        FFprobe.verify_if_ffprobe_is_installed()
        output = run(cmd, capture_output=True, text=True, encoding="utf-8")
        FFprobe.verify_if_command_fails(output)

        return output


    @staticmethod
    def get_timestamps(video_path: Path, index: int, rounding_method: RoundingMethod) -> tuple[list[int], Fraction, Fraction, Fraction]:
        """

        Parameters:
            video_path (Path): A video path.
            index (int): Index of the video stream.
            rounding_method (RoundingMethod): A rounding method. See the comment in Timestamps class about FLOOR vs ROUND.
        Returns:
            A tuple containing these 3 informations:
                1. A list of each timestamps rounded to milliseconds
                2. The time_base
                3. The first timestamps not rounded
                4. The last timestamps not rounded
        """

        cmd = [
            FFprobe.PROGRAM_NAME,
            "-hide_banner",
            "-select_streams",
            str(index),
            "-show_entries",
            # Technically, we should use frame=pts_time,dts_time instead of packet=pts_time,dts_time
            # But, using frame make the execution really slow
            # I tried to ask [here](https://ffmpeg.org/pipermail/ffmpeg-user/2024-July/058509.html) if I could use a heuristic
            # to know when I need to switch to frame, but I never got an answer.
            "packet=pts_time,dts_time:stream=codec_type,time_base", #todo
            video_path,
            "-print_format",
            "json",
        ]
        ffprobe_output = FFprobe.run_command(cmd)

        ffprobe_output_dict = json.loads(ffprobe_output.stdout)

        if len(ffprobe_output_dict["streams"]) == 0:
            raise ValueError(f"The index {index} is not in the file {video_path}.")

        if ffprobe_output_dict["streams"][0]["codec_type"] != "video":
            raise ValueError(
                f'The index {index} is not a video stream. It is an "{ffprobe_output_dict["streams"][0]["codec_type"]}" stream.'
            )

        time_base = Fraction(ffprobe_output_dict["streams"][0]["time_base"])

        timestamps = []
        lowest_timestamp: Fraction = None # type: ignore
        highest_timestamp: Fraction = None # type: ignore

        for packet in ffprobe_output_dict["packets"]:
            timestamp = Fraction(
                # Sometimes, pts_time isn't available.
                # If it is the case, fallback to dts_time
                packet.get("pts_time", packet.get("dts_time"))
            ) * Fraction(1000)
            if highest_timestamp is None or highest_timestamp < timestamp:
                highest_timestamp = timestamp
            if lowest_timestamp is None or lowest_timestamp > timestamp:
                lowest_timestamp = timestamp


            timestamps.append(rounding_method(timestamp))
        timestamps.sort()

        return timestamps, time_base, lowest_timestamp, highest_timestamp
