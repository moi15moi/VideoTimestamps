project(
    'VideoTimestamps',
    'cpp',
    default_options: ['cpp_std=c++17', 'buildtype=release'],
    meson_version: '>=1.3.0',
    version: '1.0.0rc1',
)

cc = meson.get_compiler('cpp')
py = import('python').find_installation(pure: false)

nanobind_dep = dependency('nanobind')
bestsource_dep = dependency('bestsource')
libavutil_dep = dependency('libavutil')
ffms2_dep = dependency('ffms2', static: true)

subdir('video_timestamps')
