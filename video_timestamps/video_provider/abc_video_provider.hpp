#include <pybind11/pybind11.h>

class ABCVideoProvider
{
public:
    virtual ~ABCVideoProvider() = default;
    virtual pybind11::tuple get_pts(const std::string &filename, int index) = 0;
};
