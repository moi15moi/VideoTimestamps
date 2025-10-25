project(
    'VideoTimestamps',
    'cpp',
    default_options: ['cpp_std=c++17', 'buildtype=release'],
    meson_version: '>=1.3.0',
    version: '0.2.1',
)

cc = meson.get_compiler('cpp')
py = import('python').find_installation(pure: false)

pybind11_dep = dependency('pybind11')
bestsource_dep = dependency('bestsource')
libavutil_dep = dependency('libavutil')
ffms2_dep = dependency('ffms2', static: true)

subdir('video_timestamps')
