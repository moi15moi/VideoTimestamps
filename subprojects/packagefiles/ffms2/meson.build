project(
    'ffms2',
    'cpp',
)

mod = import('unstable-external_project')


libavformat_dep = dependency('libavformat')
libavcodec_dep = dependency('libavcodec')
libswscale_dep = dependency('libswscale')
libavutil_dep = dependency('libavutil')
libswresample_dep = dependency('libswresample')

# sh -c 'cd C:/Users/moi15moi/Documents/GitHub/VideoTimestamps/subprojects/ffms2 && ./autogen.sh'
#run_command('sh', '-c', 'cd ' + meson.current_source_dir() + ' && ./autogen.sh', check: true)

#run_command('sh', '-c', 'cd', meson.current_source_dir(), '&&', './autogen.sh', check: true)
run_command('./autogen.sh', check: true)

message('Jeremie test')

p = mod.add_project('configure',
    configure_options : ['--prefix=@PREFIX@',
                       '--libdir=@LIBDIR@',
                       '--incdir=@INCLUDEDIR@',
                       '--enable-foo',
                      ],
  #depends: [libavformat_dep, libavcodec_dep, libswscale_dep, libavutil_dep, libswresample_dep]
)

libffms2_dep = p.dependency('ffms2')
meson.override_dependency('libffms2', libffms2_dep)
