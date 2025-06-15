project(
    'VideoTimestamps',
    'cpp',
    version: '0.2.0',
    default_options: ['cpp_std=c++20'],
)

cc = meson.get_compiler('cpp')
py = import('python').find_installation(pure: false)
pybind11_dep = dependency('pybind11')
bestsource_dep = dependency('bestsource')
libavutil_dep = dependency('libavutil')

subdir('video_timestamps')
