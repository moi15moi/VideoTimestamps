python_sources = [
    '__init__.py',
    'abc_video_provider.pyi',
    'best_source_video_provider.pyi',
    'ffms2_video_provider.pyi',
]

py.install_sources(
    python_sources,
    subdir: 'video_timestamps/video_provider'
)

symbolic_link_args = []
if cc.has_link_argument('-Wl,-Bsymbolic')
    # We need these link. See: https://ffmpeg.org/platform.html#Advanced-linking-configuration + https://github.com/mesonbuild/meson-python/discussions/765
    symbolic_link_args += ['-Wl,-Bsymbolic']
endif

py.extension_module(
    'abc_video_provider',
    'abc_video_provider.cpp',
    install: true,
    dependencies : [nanobind_dep],
    subdir: 'video_timestamps/video_provider',
)

py.extension_module(
    'best_source_video_provider',
    'best_source_video_provider.cpp',
    install: true,
    dependencies : [nanobind_dep, bestsource_dep, libavutil_dep],
    link_args: symbolic_link_args,
    subdir: 'video_timestamps/video_provider',
)

py.extension_module(
    'ffms2_video_provider',
    'ffms2_video_provider.cpp',
    install: true,
    dependencies : [nanobind_dep, ffms2_dep],
    cpp_args: ['-DFFMS_STATIC'],
    link_args: symbolic_link_args,
    subdir: 'video_timestamps/video_provider',
)
