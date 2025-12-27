#!/bin/bash

build_dav1d() {
    echo "Building dav1d..."
    cd "$BUILD_DIR"

    DAV1D_VERSION=$(grep '^dav1d=' "${SCRIPT_DIR}/dependencies.txt" | cut -d= -f2)

    echo "Downloading and extracting dav1d..."
    wget -O dav1d.tar.gz "https://code.videolan.org/videolan/dav1d/-/archive/${DAV1D_VERSION}/dav1d-${DAV1D_VERSION}.tar.gz?ref_type=tags"
    tar -xf dav1d.tar.gz

    cd "dav1d-${DAV1D_VERSION}"

    meson setup build \
        --prefix=$ABS_BUILD_PATH/usr/local \
        --libdir=lib \
        --buildtype=release \
        --default-library=static \
        --wrap-mode=nodownload \
        -Denable_tests=false

    ninja -C build
    ninja -C build install

    cd "$BUILD_DIR"
    rm dav1d.tar.gz
}

build_ffmpeg() {
    echo "Building ffmpeg..."
    cd "$BUILD_DIR"

    FFMPEG_VERSION=$(grep '^ffmpeg=' "${SCRIPT_DIR}/dependencies.txt" | cut -d= -f2)

    echo "Downloading and extracting ffmpeg..."
    wget -O ffmpeg.tar.gz "https://github.com/FFmpeg/FFmpeg/archive/refs/tags/${FFMPEG_VERSION}.tar.gz"
    tar -xf ffmpeg.tar.gz

    cd "FFmpeg-${FFMPEG_VERSION}"

    # FFMPEG doesn't try to read the env var CC, so let's do it
    cc=""
    if [ -n "${CC-}" ]; then
        cc="--cc=$CC"
    fi

    # FFMPEG doesn't try to read the env var CXX, so let's do it
    cxx=""
    if [ -n "${CXX-}" ]; then
        cxx="--cxx=$CXX"
    fi

    if ! ./configure --prefix="$ABS_BUILD_PATH/usr/local" \
                    --enable-static \
                    --disable-shared \
                    --enable-pic \
                    --disable-programs \
                    --disable-debug \
                    --disable-doc \
                    --disable-autodetect \
                    --enable-libdav1d \
                    $cc \
                    $cxx; then
        echo "configure failed! Showing config.log:"
        cat ffbuild/config.log
        exit 1
    fi

    make
    make install

    cd "$BUILD_DIR"
    rm ffmpeg.tar.gz
}

build_ffms2() {
    echo "Building ffms2..."
    cd "$BUILD_DIR"

    echo "Downloading and extracting ffms2..."
    wget -O ffms2.tar.gz https://github.com/FFMS/ffms2/archive/refs/heads/master.tar.gz
    tar -xf ffms2.tar.gz

    cd ffms2-master

    NOCONFIGURE=1 ./autogen.sh
    if ! ./configure --prefix=$ABS_BUILD_PATH/usr/local \
                    --enable-static \
                    --disable-shared \
                    --with-pic; then
        echo "configure failed! Showing config.log:"
        cat config.log
        exit 1
    fi

    make
    make install

    cd "$BUILD_DIR"
    rm ffms2.tar.gz
}

main() {
    # If an error occurs, stop the script
    set -eu

    # Base directory (where the script is located)
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

    # Build directory
    rm -rf build_dependencies
    mkdir "build_dependencies"
    BUILD_DIR="$SCRIPT_DIR/build_dependencies"

    # Configure dependencies build path
    ABS_BUILD_PATH=$(realpath "$BUILD_DIR")

    # PKG_CONFIG configuration
    export PKG_CONFIG_PATH="$ABS_BUILD_PATH/usr/local/lib/pkgconfig"
    if [ -n "${MSYS2_PATH_TYPE-}" ]; then
        if [ "$MSYS2_PATH_TYPE" = "inherit" ]; then
            # Convert to Windows-style path
            PKG_CONFIG_PATH_WIN=$(cygpath -w "$PKG_CONFIG_PATH")
            export PKG_CONFIG_PATH="$PKG_CONFIG_PATH_WIN"
        fi
    fi

    # Configure CC/CXX on msys2 on clang system.
    # Otherwise, it use gcc/g++
    if [ -n "${MSYSTEM-}" ]; then
        case "$MSYSTEM" in
            CLANG64|CLANGARM64)
                export CC=clang
                export CXX=clang++
                ;;
        esac
    fi

    # Build dependencies
    echo "--------------------------------------------------------------"
    build_dav1d
    echo "--------------------------------------------------------------"
    build_ffmpeg
    echo "--------------------------------------------------------------"
    build_ffms2
}

main
