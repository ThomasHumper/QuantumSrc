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
        ENGINE_HAS_D3D11=1
    )

endif()

add_library(engine_renderer STATIC
    ${ENGINE_RENDERER_SOURCES}
)

target_include_directories(
    engine_renderer
    PUBLIC
        "${CMAKE_SOURCE_DIR}/include"
)

target_link_libraries(
    engine_renderer
    PUBLIC
        engine_core
)

if(OpenGL_FOUND)
    target_link_libraries(
        engine_renderer
        PUBLIC
            OpenGL::GL
    )
endif()

if(WIN32 AND ENGINE_ENABLE_D3D)

    target_link_libraries(
        engine_renderer
        PUBLIC
            d3d11
            dxgi
    )

endif()

# ---------------------------------------------------------------------------
# Audio
# ---------------------------------------------------------------------------

set(ENGINE_AUDIO_SOURCES
    src/audio/audio.cpp
)

if(ENGINE_ENABLE_OPENAL)

    find_package(OpenAL QUIET)

    if(OpenAL_FOUND)

        list(APPEND ENGINE_AUDIO_SOURCES
            src/audio/openal/openal_audio.cpp
        )

        add_compile_definitions(
            ENGINE_HAS_OPENAL=1
        )

    else()

        message(WARNING
            "OpenAL was requested but was not found."
        )

    endif()

endif()

add_library(engine_audio STATIC
    ${ENGINE_AUDIO_SOURCES}
)

target_include_directories(
    engine_audio
    PUBLIC
        "${CMAKE_SOURCE_DIR}/include"
)

if(OpenAL_FOUND)

    target_link_libraries(
        engine_audio
        PUBLIC
            OpenAL::OpenAL
    )

endif()

# ---------------------------------------------------------------------------
# Engine aggregate library
# ---------------------------------------------------------------------------

add_library(engine STATIC)

target_link_libraries(
    engine
    PUBLIC
        engine_core
        engine_renderer
        engine_audio
        engine_stb
)

if(TARGET engine_lz4)
    target_link_libraries(
        engine
        PUBLIC
            engine_lz4
    )
endif()

if(TARGET engine_schrift)
    target_link_libraries(
        engine
        PUBLIC
            engine_schrift
    )
endif()

target_include_directories(
    engine
    PUBLIC
        "${CMAKE_SOURCE_DIR}/include"
)

# ---------------------------------------------------------------------------
# Main executable
# ---------------------------------------------------------------------------

add_executable(game
    src/game/main.cpp
)

target_link_libraries(
    game
    PRIVATE
        engine
)

# ---------------------------------------------------------------------------
# Dedicated server
# ---------------------------------------------------------------------------

if(ENGINE_BUILD_SERVER)

    add_executable(engine_server
        src/server/main.cpp
    )

    target_link_libraries(
        engine_server
        PRIVATE
            engine_core
    )

endif()

# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

if(ENGINE_BUILD_TOOLS)

    if(EXISTS "${CMAKE_SOURCE_DIR}/tools/paf/paf_tool.cpp")

        add_executable(paf_tool
            tools/paf/paf_tool.cpp
        )

        target_link_libraries(
            paf_tool
            PRIVATE
                engine_core
        )

    endif()

    if(EXISTS "${CMAKE_SOURCE_DIR}/tools/pkd/pkd_tool.cpp")

        add_executable(pkd_tool
            tools/pkd/pkd_tool.cpp
        )

        target_link_libraries(
            pkd_tool
            PRIVATE
                engine_core
        )

    endif()

endif()

# ---------------------------------------------------------------------------
# Editor
# ---------------------------------------------------------------------------

if(ENGINE_BUILD_EDITOR)

    if(EXISTS "${CMAKE_SOURCE_DIR}/src/editor/main.cpp")

        add_executable(engine_editor
            src/editor/main.cpp
        )

        target_link_libraries(
            engine_editor
            PRIVATE
                engine
        )

    endif()

endif()

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

if(ENGINE_BUILD_TESTS)

    enable_testing()

    if(EXISTS "${CMAKE_SOURCE_DIR}/tests/engine_tests.cpp")

        add_executable(engine_tests
            tests/engine_tests.cpp
        )

        target_link_libraries(
            engine_tests
            PRIVATE
                engine
        )

        add_test(
            NAME engine_tests
            COMMAND engine_tests
        )

    endif()

endif()

# ---------------------------------------------------------------------------
# Compiler warnings
# ---------------------------------------------------------------------------

if(MSVC)

    target_compile_options(
        engine_core
        PRIVATE
            /W4
        )

else()

    target_compile_options(
        engine_core
        PRIVATE
            -Wall
            -Wextra
            -Wpedantic
        )

endif()

# ---------------------------------------------------------------------------
# Debug / release definitions
# ---------------------------------------------------------------------------

target_compile_definitions(
    engine_core
    PUBLIC
        $<$<CONFIG:Debug>:ENGINE_DEBUG=1>
        $<$<CONFIG:Release>:ENGINE_RELEASE=1>
)

# ---------------------------------------------------------------------------
# Install
# ---------------------------------------------------------------------------

include(GNUInstallDirs)

install(
    TARGETS
        game
        engine
    RUNTIME DESTINATION
        ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION
        ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION
        ${CMAKE_INSTALL_LIBDIR}
)

install(
    DIRECTORY
        include/
    DESTINATION
        ${CMAKE_INSTALL_INCLUDEDIR}
)

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

message(STATUS "")
message(STATUS "======================================")
message(STATUS " CrossPlatformEngine configuration")
message(STATUS "======================================")
message(STATUS " Platform:          ${ENGINE_PLATFORM}")
message(STATUS " Renderer:          ${ENGINE_RENDERER}")
message(STATUS " OpenGL:            ${ENGINE_ENABLE_OPENGL}")
message(STATUS " OpenAL:            ${ENGINE_ENABLE_OPENAL}")
message(STATUS " Direct3D:          ${ENGINE_ENABLE_D3D}")
message(STATUS " Software renderer: ${ENGINE_ENABLE_SOFTWARE_RENDERER}")
message(STATUS " Tests:             ${ENGINE_BUILD_TESTS}")
message(STATUS " Tools:             ${ENGINE_BUILD_TOOLS}")
message(STATUS " Editor:            ${ENGINE_BUILD_EDITOR}")
message(STATUS " Server:            ${ENGINE_BUILD_SERVER}")
message(STATUS "======================================")
message(STATUS "")
```

### Build it

From the engine root:

```bash
cmake -S . -B build
cmake --build build
```

For a release build:

```bash
cmake -S . -B build \
    -DCMAKE_BUILD_TYPE=Release

cmake --build build
```

Or with the Ruby orchestrator from earlier:

```bash
ruby engine.rb configure
ruby engine.rb build --release
```

### Useful backend configurations

```bash
# OpenGL 3.3
cmake -S . -B build \
    -DENGINE_RENDERER=gl33

# Software renderer
cmake -S . -B build \
    -DENGINE_RENDERER=software

# No OpenAL
cmake -S . -B build \
    -DENGINE_ENABLE_OPENAL=OFF

# No tests/tools, useful for a minimal target build
cmake -S . -B build \
    -DENGINE_BUILD_TESTS=OFF \
    -DENGINE_BUILD_TOOLS=OFF
```

One structural recommendation: keep the **platform-specific renderers as separate CMake targets** once you add the legacy backends (`D3D7`, `D3D8`, `XGU/PBKit`, `GSKit`, `PVR`, `GX`, `Citro3D`). That lets the same engine core link against exactly one backend per target instead of trying to compile every backend together.
