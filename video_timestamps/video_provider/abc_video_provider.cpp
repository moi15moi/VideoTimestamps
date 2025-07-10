#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/complex.h>
#include <pybind11/functional.h>
#include <pybind11/chrono.h>
#include <stdio.h>
#include <filesystem>
#include <memory>
#include <stdexcept>
#include <algorithm> 
#include "abc_video_provider.hpp"

PYBIND11_MODULE(abc_video_provider, m) {
    pybind11::class_<ABCVideoProvider>(m, "ABCVideoProvider")
        .def("get_pts", &ABCVideoProvider::get_pts, pybind11::arg("filename"), pybind11::arg("index"));
}
