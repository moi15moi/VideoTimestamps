import sys
from fractions import Fraction

__all__ = ["TimeUnitConverter"]


class TimeUnitConverter:
    """Utility class for converting between time units."""

    @staticmethod
    def time_base_to_time_scale(time_base: Fraction) -> Fraction:
        """
        Convert a time base to a time scale.

        Parameters:
            time_base: The time base to convert.

        Returns:
            The corresponding time scale.
        """
        return 1 / time_base


    @staticmethod
    def time_scale_to_time_base(time_scale: Fraction) -> Fraction:
        """
        Convert a time scale to a time base.

        Parameters:
            time_scale: The time scale to convert.

        Returns:
            The corresponding time base.
        """
        return 1 / time_scale


    @staticmethod
    def timestamp_scale_to_time_scale(timestamp_scale: int) -> Fraction:
        """
        Convert a timestamp scale to a time scale.

        Parameters:
            timestamp_scale: The timestamp scale (e.g., nanoseconds per tick).

        Returns:
            The corresponding time scale.
        """
        return Fraction(pow(10, 9), timestamp_scale)


    @staticmethod
    def time_scale_to_timestamp_scale(time_scale: Fraction) -> int:
        """
        Convert a time scale to a timestamp scale.

        Parameters:
            time_scale: The time scale to convert.

        Returns:
            The corresponding timestamp scale.
        """
        timestamp_scale = Fraction(pow(10, 9), time_scale)

        if sys.version_info >= (3, 12):
            is_integer = timestamp_scale.is_integer()
        else:
            is_integer = timestamp_scale.denominator == 1

        if not is_integer:
            raise ValueError(f"The timescale {time_scale} cannot be converted to a timestamp scale because the result {timestamp_scale} isn't a integer.")

        return int(timestamp_scale)


    @staticmethod
    def timestamp_scale_to_time_base(timestamp_scale: int) -> Fraction:
        """
        Convert a timestamp scale to a time base.

        Parameters:
            timestamp_scale: The timestamp scale.

        Returns:
            The corresponding time base.
        """
        return Fraction(timestamp_scale, pow(10, 9))


    @staticmethod
    def time_base_to_timestamp_scale(time_base: Fraction) -> int:
        """
        Convert a time base to a timestamp scale.

        Parameters:
            time_base: The time base to convert.

        Returns:
            The corresponding timestamp scale.
        """
        timestamp_scale = time_base * pow(10, 9)

        if sys.version_info >= (3, 12):
            is_integer = timestamp_scale.is_integer()
        else:
            is_integer = timestamp_scale.denominator == 1

        if not is_integer:
            raise ValueError(f"The timebase {time_base} cannot be converted to a timestamp scale because the result {timestamp_scale} isn't a integer.")

        return int(timestamp_scale)
