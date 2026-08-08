#include <nanobind/nanobind.h>
#include <nanobind/stl/optional.h>
#include <nanobind/stl/string.h>

class ABCVideoProvider
{
public:
    virtual ~ABCVideoProvider() = default;
    virtual nanobind::tuple get_pts(const std::string &filename, std::optional<int> index, std::optional<int> video_stream_index) = 0;
};
