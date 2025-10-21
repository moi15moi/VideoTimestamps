project(
    'ffms2',
    'cpp',
    version : run_command('sh', 'version.sh', check: true).stdout().strip()
)

mod = import('unstable-external_project')

ffmpeg_proj = subproject('ffmpeg')
libavformat = ffmpeg_proj.get_variable('libavformat')
libavcodec = ffmpeg_proj.get_variable('libavcodec')
libswscale = ffmpeg_proj.get_variable('libswscale')
libavutil = ffmpeg_proj.get_variable('libavutil')
libswresample = ffmpeg_proj.get_variable('libswresample')

run_command('./autogen.sh', check: true, env: ['NOCONFIGURE=1'])

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
    verbose: true,
    depends: [libavformat, libavcodec, libswscale, libavutil, libswresample]
)

libffms2_dep = p.dependency('ffms2')
libffms2_dep = declare_dependency(
  dependencies: libffms2_dep,
  compile_args: ['-DFFMS_STATIC']
)
meson.override_dependency('ffms2', libffms2_dep)
