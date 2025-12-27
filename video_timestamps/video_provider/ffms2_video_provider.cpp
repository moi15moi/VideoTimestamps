#include <nanobind/nanobind.h>
#include <nanobind/stl/shared_ptr.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/vector.h>
#include <ffms.h>
#include "abc_video_provider.hpp"

class FFMS2VideoProvider: public ABCVideoProvider {
public:
    nanobind::tuple get_pts(const std::string &filename, int index) {
        char errmsg[1024];
        FFMS_ErrorInfo errinfo;
        errinfo.Buffer      = errmsg;
        errinfo.BufferSize  = sizeof(errmsg);
        errinfo.ErrorType   = FFMS_ERROR_SUCCESS;
        errinfo.SubType     = FFMS_ERROR_SUCCESS;

        FFMS_Init(0, 0);

        FFMS_Indexer *indexer = FFMS_CreateIndexer(filename.c_str(), &errinfo);
        if (!indexer)
            throw std::runtime_error("ffms2 reported an error while calling FFMS_CreateIndexer: " + std::string(errinfo.Buffer) + ".");

        int num_tracks = FFMS_GetNumTracksI(indexer);
        if (index >= num_tracks)
            throw std::invalid_argument("The index " + std::to_string(index) + " is not in the file " + filename + ".");

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

            throw std::invalid_argument("The index " + std::to_string(index) + " is not a video stream. It is an \"" + steam_media_type + "\" stream.");
        }

        auto ffms2_index = std::unique_ptr<FFMS_Index, void(*)(FFMS_Index*)>(
            FFMS_DoIndexing2(indexer, FFMS_IEH_ABORT, &errinfo),
            FFMS_DestroyIndex
        );
        if (!ffms2_index)
            throw std::runtime_error("ffms2 reported an error while calling FFMS_DoIndexing2: " + std::string(errinfo.Buffer) + ".");

        int threads = 1;
        int seek_mode = FFMS_SEEK_NORMAL;
        auto video_source = std::unique_ptr<FFMS_VideoSource, void(*)(FFMS_VideoSource*)>(
            FFMS_CreateVideoSource(filename.c_str(), index, ffms2_index.get(), threads, seek_mode, &errinfo),
            FFMS_DestroyVideoSource
        );
        if (!video_source)
            throw std::runtime_error("ffms2 reported an error while calling FFMS_CreateVideoSource: " + std::string(errinfo.Buffer) + ".");

        FFMS_Track *track = FFMS_GetTrackFromVideo(video_source.get());
        if (!track)
            throw std::runtime_error("ffms2 reported an error while calling FFMS_GetTrackFromVideo");

        const FFMS_VideoProperties *videoprops = FFMS_GetVideoProperties(video_source.get());

        std::vector<int64_t> pts_list;
        for (int n = 0; n < videoprops->NumFrames; n++) {
            const FFMS_FrameInfo *frame_info = FFMS_GetFrameInfo(track, n);
            if (!frame_info)
                throw std::runtime_error("ffms2 reported an error while calling FFMS_GetFrameInfo with frame " + std::to_string(n) + ".");

            pts_list.push_back(frame_info->PTS);
        }

        if (pts_list.size() > 0)
            pts_list.push_back(videoprops->LastEndPTS);

        const FFMS_TrackTimeBase *ffms2_time_base = FFMS_GetTimeBase(track);
        if (!ffms2_time_base)
            throw std::runtime_error("ffms2 reported an error while calling FFMS_GetTimeBase");

        nanobind::object fraction_class = nanobind::module_::import_("fractions").attr("Fraction");
        nanobind::object time_base = fraction_class(ffms2_time_base->Num, ffms2_time_base->Den) / fraction_class(1000, 1);
        nanobind::object fps = fraction_class(videoprops->FPSNumerator, videoprops->FPSDenominator);

        return nanobind::make_tuple(pts_list, time_base, fps);
    }
};

NB_MODULE(ffms2_video_provider, m) {
    nanobind::module_::import_("video_timestamps.video_provider.abc_video_provider");

    nanobind::class_<FFMS2VideoProvider, ABCVideoProvider>(m, "FFMS2VideoProvider")
        .def(nanobind::init<>())
        .def("get_pts", &FFMS2VideoProvider::get_pts, nanobind::arg("filename"), nanobind::arg("index"));
}
