```cmake
cmake_minimum_required(VERSION 3.20)

project(
    CrossPlatformEngine
    VERSION 0.1.0
    DESCRIPTION "Cross-platform C++ game engine"
    LANGUAGES C CXX
)

# ---------------------------------------------------------------------------
# C++ standard
# ---------------------------------------------------------------------------

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Put executables in bin/ and libraries in lib/
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/bin")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/bin")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/lib")

# ---------------------------------------------------------------------------
# Build options
# ---------------------------------------------------------------------------

option(ENGINE_BUILD_TESTS
    "Build engine tests"
    ON
)

option(ENGINE_BUILD_TOOLS
    "Build engine tools"
    ON
)

option(ENGINE_BUILD_EDITOR
    "Build the engine editor"
    OFF
)

option(ENGINE_BUILD_SERVER
    "Build the dedicated server"
    ON
)

option(ENGINE_ENABLE_OPENGL
    "Enable OpenGL renderer"
    ON
)

option(ENGINE_ENABLE_OPENAL
    "Enable OpenAL audio"
    ON
)

option(ENGINE_ENABLE_D3D
    "Enable Direct3D renderers"
    ON
)

option(ENGINE_ENABLE_SOFTWARE_RENDERER
    "Enable software renderer"
    ON
)

option(ENGINE_ENABLE_SDL
    "Enable SDL platform layer"
    OFF
)

# Renderer:
#   auto
#   software
#   gl11
#   gl20
#   gl33
#
set(
    ENGINE_RENDERER
    "auto"
    CACHE STRING
    "Default renderer backend"
)

set_property(
    CACHE ENGINE_RENDERER
    PROPERTY STRINGS
        auto
        software
        gl11
        gl20
        gl33
)

# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------

if(WIN32)
    set(ENGINE_PLATFORM "windows")
elseif(APPLE)
    set(ENGINE_PLATFORM "macos")
elseif(UNIX)
    set(ENGINE_PLATFORM "linux")
else()
    set(ENGINE_PLATFORM "unknown")
endif()

message(STATUS "Engine platform: ${ENGINE_PLATFORM}")
message(STATUS "Engine renderer: ${ENGINE_RENDERER}")

# ---------------------------------------------------------------------------
# Include directories
# ---------------------------------------------------------------------------

include_directories(
    "${CMAKE_SOURCE_DIR}/include"
    "${CMAKE_SOURCE_DIR}/src"
    "${CMAKE_SOURCE_DIR}/third_party"
)

# ---------------------------------------------------------------------------
# Third-party libraries
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# STB
# ---------------------------------------------------------------------------

add_library(engine_stb STATIC
    src/image/stb/stb_loader.cpp
)

target_include_directories(
    engine_stb
    PUBLIC
        "${CMAKE_SOURCE_DIR}/include"
        "${CMAKE_SOURCE_DIR}/third_party"
)

# ---------------------------------------------------------------------------
# LZ4
# ---------------------------------------------------------------------------

find_package(PkgConfig QUIET)

find_path(
    LZ4_INCLUDE_DIR
    NAMES lz4.h
    PATHS
        "${CMAKE_SOURCE_DIR}/third_party/lz4"
        "${CMAKE_SOURCE_DIR}/third_party"
)

find_library(
    LZ4_LIBRARY
    NAMES lz4
)

if(LZ4_INCLUDE_DIR AND LZ4_LIBRARY)

    add_library(engine_lz4 STATIC
        src/filesystem/compression/lz4/lz4_loader.cpp
    )

    target_include_directories(
        engine_lz4
        PUBLIC
            "${CMAKE_SOURCE_DIR}/include"
            "${LZ4_INCLUDE_DIR}"
    )

    target_link_libraries(
        engine_lz4
        PUBLIC
            "${LZ4_LIBRARY}"
    )

else()

    message(WARNING
        "LZ4 was not found. engine_lz4 will not be built."
    )

endif()

# ---------------------------------------------------------------------------
# libschrift
# ---------------------------------------------------------------------------

find_path(
    SCHRIFT_INCLUDE_DIR
    NAMES schrift.h
    PATHS
        "${CMAKE_SOURCE_DIR}/third_party/schrift"
        "${CMAKE_SOURCE_DIR}/third_party"
)

find_library(
    SCHRIFT_LIBRARY
    NAMES schrift
)

if(SCHRIFT_INCLUDE_DIR AND SCHRIFT_LIBRARY)

    add_library(engine_schrift STATIC
        src/fonts/schrift/schrift_loader.cpp
    )

    target_include_directories(
        engine_schrift
        PUBLIC
            "${CMAKE_SOURCE_DIR}/include"
            "${SCHRIFT_INCLUDE_DIR}"
    )

    target_link_libraries(
        engine_schrift
        PUBLIC
            "${SCHRIFT_LIBRARY}"
    )

else()

    message(WARNING
        "libschrift was not found. engine_schrift will not be built."
    )

endif()

# ---------------------------------------------------------------------------
# Core engine
# ---------------------------------------------------------------------------

set(ENGINE_CORE_SOURCES

    # Core
    src/main.cpp

    # Filesystem
    src/filesystem/filesystem.cpp
    src/filesystem/paf/paf.cpp
    src/filesystem/pkd/pkd.cpp

    # Input
    src/input/input.cpp

    # UI
    src/ui/ui.cpp

    # Physics
    src/physics/physics.cpp

    # Audio
    src/audio/audio.cpp

    # Server
    src/server/server.cpp
)

add_library(engine_core STATIC
    ${ENGINE_CORE_SOURCES}
)

target_include_directories(
    engine_core
    PUBLIC
        "${CMAKE_SOURCE_DIR}/include"
)

target_compile_definitions(
    engine_core
    PUBLIC
        ENGINE_PLATFORM="${ENGINE_PLATFORM}"
)

target_compile_features(
    engine_core
    PUBLIC
        cxx_std_20
)

# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------

set(ENGINE_RENDERER_SOURCES
    src/renderer/renderer.cpp
)

# Software renderer
if(ENGINE_ENABLE_SOFTWARE_RENDERER)

    list(APPEND ENGINE_RENDERER_SOURCES
        src/renderer/software/software_renderer.cpp
    )

    add_compile_definitions(
        ENGINE_HAS_SOFTWARE_RENDERER=1
    )

endif()

# OpenGL
if(ENGINE_ENABLE_OPENGL)

    find_package(OpenGL QUIET)

    if(OpenGL_FOUND)

        list(APPEND ENGINE_RENDERER_SOURCES
            src/renderer/opengl/opengl_renderer.cpp
        )

        add_compile_definitions(
            ENGINE_HAS_OPENGL=1
        )

    else()

        message(WARNING
            "OpenGL was requested but was not found."
        )

    endif()

endif()

# Direct3D
if(WIN32 AND ENGINE_ENABLE_D3D)

    list(APPEND ENGINE_RENDERER_SOURCES
        src/renderer/d3d11/d3d11_renderer.cpp
    )

    add_compile_definitions(
       
