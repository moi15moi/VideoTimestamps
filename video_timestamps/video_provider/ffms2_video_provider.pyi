from __future__ import annotations
from fractions import Fraction
from .abc_video_provider import ABCVideoProvider

__all__ = ['FFMS2VideoProvider']

class FFMS2VideoProvider(ABCVideoProvider):
    def __init__(self) -> None:
        ...
    def get_pts(self, filename: str, index: int) -> tuple[list[int], Fraction, Fraction]:
        ...
