#include <nanobind/nanobind.h>
#include <nanobind/stl/optional.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/vector.h>
#include <videosource.h>
#include <tracklist.h>
extern "C" {
#include <libavutil/avutil.h>
#include <libavutil/log.h>
}
#include <algorithm>
#include "abc_video_provider.hpp"

class BestSourceVideoProvider: public ABCVideoProvider {
public:
    nanobind::tuple get_pts(const std::string &filename, std::optional<int> index, std::optional<int> video_stream_index) {
        if (index.has_value() == video_stream_index.has_value())
            throw std::invalid_argument("You must specify exactly one of \"index\" or \"video_stream_index\".");

        SetFFmpegLogLevel(AV_LOG_ERROR);

        std::map<std::string, std::string> opts;
        BestTrackList tracklist(filename, &opts);
        int num_tracks = tracklist.GetNumTracks();
        int resolved_index;

        if (index.has_value()) {
            resolved_index = index.value();
            if (resolved_index < 0 || resolved_index >= num_tracks) {
                throw std::invalid_argument("The index " + std::to_string(resolved_index) + " is not in the file " + filename + ".");
            }

            BestTrackList::TrackInfo info = tracklist.GetTrackInfo(resolved_index);
            if (info.MediaType != AVMEDIA_TYPE_VIDEO) {
                std::string steam_media_type = "";
                switch (info.MediaType) {
                    case AVMEDIA_TYPE_AUDIO:
                        steam_media_type = "audio";
                        break;
                    case AVMEDIA_TYPE_DATA:
                        steam_media_type = "data";
                        break;
                    case AVMEDIA_TYPE_SUBTITLE:
                        steam_media_type = "subtitle";
                        break;
                    case AVMEDIA_TYPE_ATTACHMENT:
                        steam_media_type = "attachment";
                        break;
                    case AVMEDIA_TYPE_NB:
                        steam_media_type = "nb";
                        break;
                    default:
                        steam_media_type = "unknown";
                        break;
                }

                throw std::invalid_argument("The index " + std::to_string(resolved_index) + " is not a video stream. It is an \"" + steam_media_type + "\" stream.");
            }
        } else {
            int target_video_stream_index = video_stream_index.value();
            if (target_video_stream_index < 0) {
                throw std::invalid_argument("The video_stream_index " + std::to_string(target_video_stream_index) + " must be a positive integer.");
            }

            int video_track_count = 0;
            resolved_index = -1;
            for (int i = 0; i < num_tracks; i++) {
                if (tracklist.GetTrackInfo(i).MediaType == AVMEDIA_TYPE_VIDEO) {
                    if (video_track_count == target_video_stream_index) {
                        resolved_index = i;
                        break;
                    }
                    video_track_count++;
                }
            }

            if (resolved_index == -1) {
                throw std::invalid_argument("The video_stream_index " + std::to_string(target_video_stream_index) + " is not in the file " + filename + ". It only contains " + std::to_string(video_track_count) + " video stream(s).");
            }
        }

        std::map<std::string, std::string> bsopts;
        std::unique_ptr<BestVideoSource> bs = std::make_unique<BestVideoSource>(filename, "", 0, resolved_index, 0, 0, 3, filename, &bsopts);
        BSVideoProperties properties = bs->GetVideoProperties();

        std::vector<int64_t> pts_list;
        for (int64_t n = 0; n < properties.NumFrames; n++) {
            const BestVideoSource::FrameInfo &info = bs->GetFrameInfo(n);
            if (info.PTS == AV_NOPTS_VALUE) {
                continue;
            }
            pts_list.push_back(info.PTS);
        }

        if (pts_list.size() > 0)
            pts_list.push_back(pts_list.front() + properties.Duration);

        nanobind::object fraction_class = nanobind::module_::import_("fractions").attr("Fraction");
        nanobind::object time_base = fraction_class(properties.TimeBase.Num, properties.TimeBase.Den);
        nanobind::object fps = fraction_class(properties.FPS.Num, properties.FPS.Den);

        return nanobind::make_tuple(pts_list, time_base, fps);
    }
};

NB_MODULE(best_source_video_provider, m) {
    nanobind::module_::import_("video_timestamps.video_provider.abc_video_provider");

    nanobind::class_<BestSourceVideoProvider, ABCVideoProvider>(m, "BestSourceVideoProvider")
        .def(nanobind::init<>())
        .def("get_pts", &BestSourceVideoProvider::get_pts, nanobind::arg("filename"), nanobind::arg("index"), nanobind::arg("video_stream_index") = nanobind::none());
}
