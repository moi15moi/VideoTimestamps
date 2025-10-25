#include <nanobind/nanobind.h>
#include <nanobind/stl/string.h>

class ABCVideoProvider
{
public:
    virtual ~ABCVideoProvider() = default;
    virtual nanobind::tuple get_pts(const std::string &filename, int index) = 0;
};
