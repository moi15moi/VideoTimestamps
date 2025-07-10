project(
    'VideoTimestamps',
    'cpp',
    version: '0.2.0',
    default_options: ['cpp_std=c++17', 'buildtype=release'],
)

cc = meson.get_compiler('cpp')
py = import('python').find_installation(pure: false)
pybind11_dep = dependency('pybind11')
bestsource_dep = dependency('bestsource')
libavformat_dep = dependency('libavformat')
libavcodec_dep = dependency('libavcodec')
libswscale_dep = dependency('libswscale')
libavutil_dep = dependency('libavutil')
libswresample_dep = dependency('libswresample')
ffms2_dep = dependency('ffms2')

subdir('video_timestamps')
