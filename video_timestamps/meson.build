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

symbolic_link_args = []
if cc.has_link_argument('-Wl,-Bsymbolic')
    # We need these link. See: https://ffmpeg.org/platform.html#Advanced-linking-configuration + https://github.com/mesonbuild/meson-python/discussions/765
    symbolic_link_args += ['-Wl,-Bsymbolic']
endif

py.extension_module(
    'best_source',
    'best_source.cpp',
    install: true,
    dependencies : [pybind11_dep, bestsource_dep, libavformat_dep, libavcodec_dep, libswscale_dep, libavutil_dep, libswresample_dep, ffms2_dep],
    link_args: symbolic_link_args,
    subdir: 'video_timestamps'
)
