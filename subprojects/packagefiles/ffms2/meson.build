project(
    'ffms2',
    'cpp',
)

mod = import('unstable-external_project')

ffmpeg_proj = subproject('ffmpeg')
libavformat = ffmpeg_proj.get_variable('libavformat')
libavcodec = ffmpeg_proj.get_variable('libavcodec')
libswscale = ffmpeg_proj.get_variable('libswscale')
libavutil = ffmpeg_proj.get_variable('libavutil')
libswresample = ffmpeg_proj.get_variable('libswresample')

run_command('./autogen.sh', check: true)

p = mod.add_project('configure',
    configure_options : [
        '--prefix=@PREFIX@',
        '--libdir=@PREFIX@/@LIBDIR@',
        '--includedir=@PREFIX@/@INCLUDEDIR@',
        '--bindir=@PREFIX@/@BINDIR@',
        '--enable-static',
        '--disable-shared',
        '--with-pic',
    ],
    env: {
        'LDFLAGS': '-Wl,-Bsymbolic',
    },
    depends: [libavformat, libavcodec, libswscale, libavutil, libswresample]
)

libffms2_dep = p.dependency('ffms2')
meson.override_dependency('ffms2', libffms2_dep)
