#include <nanobind/nanobind.h>
#include "abc_video_provider.hpp"

NB_MODULE(abc_video_provider, m) {
    nanobind::class_<ABCVideoProvider>(m, "ABCVideoProvider")
        .def("get_pts", &ABCVideoProvider::get_pts, nanobind::arg("filename"), nanobind::arg("index"));
}
