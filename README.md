# VideoTimestamps
[![VideoTimestamps - CI Build Status](https://github.com/moi15moi/VideoTimestamps/actions/workflows/run_test.yml/badge.svg?branch=main)](https://github.com/moi15moi/VideoTimestamps/actions/workflows/run_test.yml?query=branch:main)
[![VideoTimestamps - Version](https://img.shields.io/pypi/v/videotimestamps.svg)](https://pypi.org/project/VideoTimestamps)
[![VideoTimestamps - Python Version](https://img.shields.io/pypi/pyversions/videotimestamps.svg)](https://pypi.org/project/VideoTimestamps)
[![VideoTimestamps - Coverage](https://img.shields.io/codecov/c/github/moi15moi/VideoTimestamps)](https://app.codecov.io/github/moi15moi/VideoTimestamps)
[![VideoTimestamps - mypy](https://img.shields.io/badge/mypy-checked-blue)](https://github.com/moi15moi/VideoTimestamps/actions?query=branch:main)
[![VideoTimestamps - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

This tool allows to recover the timestamps of each frame in a video in any units (seconds, milliseconds, nanoseconds, etc).
It also help to convert a frame to a time in any units and vice-versa.

## Installation
```
pip install VideoTimestamps
```

## How to use it?
See the [example file](./examples/get_timestamps.py) and/or read the [documentation](https://moi15moi.github.io/VideoTimestamps/).

## How to build the project from scratch?
### Unix
1. Run: `./build_dependencies.sh`
2. Run: `export PKG_CONFIG_PATH="$(pwd)/build_dependencies/usr/local/lib/pkgconfig"`
3. Run `python -m build` to create a wheel. To perform an editable install, first run `pip install meson meson-python` and then `pip install --no-build-isolation --editable .`
### Windows
1. In MSYS2 (any environment), run `./build_dependencies.sh`
2. In Windows CMD, run `C:\msys64\usr\bin\env.exe MSYSTEM=CLANG64 MSYS2_PATH_TYPE=inherit /usr/bin/bash -l` (replace the **MSYSTEM** value with the one you used in the first step)
3. Run `export PKG_CONFIG_PATH="$(cygpath -w "$(pwd)/build_dependencies/usr/local/lib/pkgconfig")"`
4. Repeat step 3 from the Unix section. Verify that `python` refers to your Windows installation, not the MSYS2 one, by running `which python`. If it points to the MSYS2 Python, use the absolute path to your Windows Python installation instead.
