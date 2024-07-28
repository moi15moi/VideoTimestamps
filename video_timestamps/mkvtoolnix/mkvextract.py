from .utils import MKVUtils
from tempfile import TemporaryDirectory
from pathlib import Path

__all__ = ["MKVExtract"]


class MKVExtract:
    """
    This class is a collection of static methods that will help
    the user to interact with mkvextract.
    """

    PROGRAM_NAME = "mkvextract"
    PROGRAM_PATH = MKVUtils.get_program_path(PROGRAM_NAME)

    @staticmethod
    def is_mkv_extract_installed() -> bool:
        """
        Checks if the `mkvextract` program is installed and available in the system's PATH.

        Returns:
            True if `mkvextract` is installed, False otherwise.
        """
        return MKVExtract.PROGRAM_PATH is not None


    @staticmethod
    def verify_if_mkvextract_installed() -> None:
        """
        Verifies if the `mkvextract` program is installed. Raises an error if not found.

        Raises:
            Exception: If `mkvextract` is not found in the system's PATH.
        """
        if not MKVExtract.is_mkv_extract_installed():
            raise Exception(
                f'{MKVExtract.PROGRAM_NAME} is isn\'t found. You need to correct your environnements variable or correctly install the program'
            )


    @staticmethod
    def get_timestamps_file_content(mkv_file_path: Path, index: int) -> str:
        """Extracts the timestamps from an MKV file for a specific track index.

        Parameters:
            mkv_file_path (Path): The path to the MKV file.
            index (int): Index of the video stream.

        Returns:
            The content of the timestamps file.
        """

        MKVExtract.verify_if_mkvextract_installed()
        MKVUtils.verify_if_file_mkv(mkv_file_path)

        with TemporaryDirectory() as tmpdirname:
            timestamps_file_path = Path(tmpdirname, "temp timestamps.txt")
            cmd = [
                MKVExtract.PROGRAM_PATH,
                mkv_file_path,
                "timestamps_v2",
                f"{index}:{timestamps_file_path}",
            ]

            MKVUtils.run_command(MKVExtract.PROGRAM_NAME, cmd)
            with open(timestamps_file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            # Ignore the last line due to this issue: https://gitlab.com/mbunkus/mkvtoolnix/-/issues/3075
            content = "".join(lines[:-1])

        return content