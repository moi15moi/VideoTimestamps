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
#include "videosource.h"
#include "tracklist.h"
#include "bsshared.h"
extern "C" {
#include <libavutil/avutil.h>
#include <libavutil/log.h>
}

pybind11::tuple get_pts(const std::string &filename, int index) {

    SetFFmpegLogLevel(AV_LOG_ERROR);

	std::map<std::string, std::string> opts;
	BestTrackList tracklist(filename, &opts);
    if (index >=tracklist.GetNumTracks()) {
        throw std::invalid_argument(std::format("The index {} is not in the file {}.", index, filename));    
    }

    BestTrackList::TrackInfo info = tracklist.GetTrackInfo(index);
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

        throw std::invalid_argument(std::format("The index {} is not a video stream. It is an \"{}\" stream.", index, steam_media_type));    
    }


    std::map<std::string, std::string> bsopts;
    std::unique_ptr<BestVideoSource> bs = std::make_unique<BestVideoSource>(filename, "", 0, index, 0, 1, 3, filename, &bsopts);
    BSVideoProperties properties = bs->GetVideoProperties();

    std::vector<int64_t> pts_list;

    for (int n = 0; n < properties.NumFrames; n++) {
        const BestVideoSource::FrameInfo &info = bs->GetFrameInfo(n);
        if (info.PTS == AV_NOPTS_VALUE) {
            continue;
            // TODO Not sure what I should do in this case
            //throw std::invalid_argument("Error PTS");    
        }
        pts_list.push_back(info.PTS);
    }

    std::sort(pts_list.begin(), pts_list.end());

    pybind11::object fraction_class = pybind11::module_::import("fractions").attr("Fraction");
    pybind11::object time_base = fraction_class(properties.TimeBase.Num, properties.TimeBase.Den);
    pybind11::object fps = fraction_class(properties.FPS.Num, properties.FPS.Den);

    return pybind11::make_tuple(pts_list, time_base, fps);
}

PYBIND11_MODULE(best_source, m) {
    m.def("get_pts", &get_pts, pybind11::arg("filename"), pybind11::arg("index"));
}
