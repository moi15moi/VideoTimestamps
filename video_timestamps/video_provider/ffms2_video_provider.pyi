from __future__ import annotations

from fractions import Fraction

from .abc_video_provider import ABCVideoProvider

__all__ = ['FFMS2VideoProvider']

class FFMS2VideoProvider(ABCVideoProvider):
    """
    Video provider that is based on [FFMS2](https://github.com/FFMS/ffms2).
    """
    def __init__(self) -> None:
        ...
    def get_pts(self, filename: str, index: int) -> tuple[list[int], Fraction, Fraction]:
        ...
