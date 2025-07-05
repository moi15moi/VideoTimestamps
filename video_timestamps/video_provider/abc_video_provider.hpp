#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/complex.h>
#include <pybind11/functional.h>
#include <pybind11/chrono.h>
#include <stdio.h>
#include <filesystem>
#include <memory>
#include <stdexcept>
#include <format>
#include <algorithm> 


class ABCVideoProvider
{
public:
    virtual ~ABCVideoProvider() = default;
    virtual pybind11::tuple get_pts(const std::string &filename, int index) = 0;

};
