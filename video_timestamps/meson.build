python_sources = [
    '__init__.py',
    'abc_timestamps.py',
    'best_source.pyi',
    'fps_timestamps.py',
    'rounding_method.py',
    'text_file_timestamps.py',
    'time_type.py',
    'time_unit_converter.py',
    'timestamps_file_parser.py',
    'video_timestamps.py'
]

py.install_sources(
    python_sources,
    subdir: 'video_timestamps'
)

py.extension_module(
    'best_source',
    'best_source.cpp',
    install: true,
    dependencies : [pybind11_dep, bestsource_dep, libavutil_dep],
    # We need these link. See: https://ffmpeg.org/platform.html#Advanced-linking-configuration + https://github.com/mesonbuild/meson-python/discussions/765
    link_args: ['-Wl,-Bsymbolic'],
    subdir: 'video_timestamps'
)
