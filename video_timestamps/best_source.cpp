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
#include <ffms.h>
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
    std::unique_ptr<BestVideoSource> bs = std::make_unique<BestVideoSource>(filename, "", 0, index, 0, 0, 3, filename, &bsopts);
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


pybind11::tuple ffms2_get_pts(const std::string &filename, int index) {
    char errmsg[1024];
    FFMS_ErrorInfo errinfo;
    errinfo.Buffer      = errmsg;
    errinfo.BufferSize  = sizeof(errmsg);
    errinfo.ErrorType   = FFMS_ERROR_SUCCESS;
    errinfo.SubType     = FFMS_ERROR_SUCCESS;
    
    FFMS_Init(0, 0);

    FFMS_Indexer *indexer = FFMS_CreateIndexer(filename.c_str(), &errinfo);
    if (!indexer)
        throw std::runtime_error(std::format("ffms2 reported an error while calling FFMS_CreateIndexer: {}.", std::string(errinfo.Buffer)));    

    int num_tracks = FFMS_GetNumTracksI(indexer);
    if (index >= num_tracks)
        throw std::invalid_argument(std::format("The index {} is not in the file {}.", index, filename));    

    int track_type = FFMS_GetTrackTypeI(indexer, index);
    if (track_type != FFMS_TYPE_VIDEO) {
        std::string steam_media_type = "";
        switch (track_type) {
            case FFMS_TYPE_AUDIO:
                steam_media_type = "audio";
                break;
            case FFMS_TYPE_DATA:
                steam_media_type = "data";
                break;
            case FFMS_TYPE_SUBTITLE:
                steam_media_type = "subtitle";
                break;
            case FFMS_TYPE_ATTACHMENT:
                steam_media_type = "attachment";
                break;
            default:
                steam_media_type = "unknown";
                break;
        }

        throw std::invalid_argument(std::format("The index {} is not a video stream. It is an \"{}\" stream.", index, steam_media_type));    
    }

    auto ffms2_index = std::unique_ptr<FFMS_Index, void(*)(FFMS_Index*)>(
        FFMS_DoIndexing2(indexer, FFMS_IEH_ABORT, &errinfo),
        FFMS_DestroyIndex
    );
    if (!ffms2_index)
        throw std::runtime_error(std::format("ffms2 reported an error while calling FFMS_DoIndexing2: {}.", errinfo.Buffer));    

    int threads = 1;
    int seek_mode = FFMS_SEEK_NORMAL;
    auto video_source = std::unique_ptr<FFMS_VideoSource, void(*)(FFMS_VideoSource*)>(
        FFMS_CreateVideoSource(filename.c_str(), index, ffms2_index.get(), threads, seek_mode, &errinfo),
        FFMS_DestroyVideoSource
    );
	if (!video_source)
        throw std::runtime_error(std::format("ffms2 reported an error while calling FFMS_CreateVideoSource: {}", errinfo.Buffer));    

	FFMS_Track *track = FFMS_GetTrackFromVideo(video_source.get());
	if (!track)
        throw std::runtime_error("ffms2 reported an error while calling FFMS_GetTrackFromVideo");    


    const FFMS_VideoProperties *videoprops = FFMS_GetVideoProperties(video_source.get());

    std::vector<int64_t> pts_list;
    for (int n = 0; n < videoprops->NumFrames; n++) {
		const FFMS_FrameInfo *frame_info = FFMS_GetFrameInfo(track, n);
		if (!frame_info)
			throw std::runtime_error(std::format("ffms2 reported an error while calling FFMS_GetFrameInfo with frame {}", n));

        pts_list.push_back(frame_info->PTS);
	}

	const FFMS_TrackTimeBase *ffms2_time_base = FFMS_GetTimeBase(track);
	if (!ffms2_time_base)
        throw std::runtime_error("ffms2 reported an error while calling FFMS_GetTimeBase");

    pybind11::object fraction_class = pybind11::module_::import("fractions").attr("Fraction");
    pybind11::object time_base = fraction_class(ffms2_time_base->Num, ffms2_time_base->Den) / fraction_class(1000, 1);
    pybind11::object fps = fraction_class(videoprops->FPSNumerator, videoprops->FPSDenominator);

    return pybind11::make_tuple(pts_list, time_base, fps);
}

PYBIND11_MODULE(best_source, m) {
    m.def("bestsource_get_pts", &get_pts, pybind11::arg("filename"), pybind11::arg("index"));
    m.def("get_pts", &ffms2_get_pts, pybind11::arg("filename"), pybind11::arg("index"));
}
