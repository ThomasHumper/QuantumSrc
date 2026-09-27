```cpp
// stb_loader.hpp
#pragma once

/*
 * Central STB include/loader.
 *
 * Usage:
 *
 *     #include "stb_loader.hpp"
 *
 * The implementation definitions live in stb_loader.cpp, so STB
 * implementations are compiled exactly once.
 */

#include <cstddef>
#include <cstdint>

namespace stb {

    /*
     * -------------------------------------------------------------------------
     * Image loading
     * -------------------------------------------------------------------------
     */

    class Image {
    public:
        Image() = default;

        Image(const Image&) = delete;
        Image& operator=(const Image&) = delete;

        Image(Image&& other) noexcept
            : data_(other.data_),
              width_(other.width_),
              height_(other.height_),
              channels_(other.channels_) {
            other.data_ = nullptr;
            other.width_ = 0;
            other.height_ = 0;
            other.channels_ = 0;
        }

        Image& operator=(Image&& other) noexcept {
            if (this != &other) {
                free();

                data_ = other.data_;
                width_ = other.width_;
                height_ = other.height_;
                channels_ = other.channels_;

                other.data_ = nullptr;
                other.width_ = 0;
                other.height_ = 0;
                other.channels_ = 0;
            }

            return *this;
        }

        ~Image() {
            free();
        }

        bool load(const char* filename, int desired_channels = 0);

        bool load_from_memory(
            const void* data,
            std::size_t size,
            int desired_channels = 0
        );

        void free();

        [[nodiscard]]
        const std::uint8_t* data() const {
            return data_;
        }

        [[nodiscard]]
        std::uint8_t* data() {
            return data_;
        }

        [[nodiscard]]
        int width() const {
            return width_;
        }

        [[nodiscard]]
        int height() const {
            return height_;
        }

        [[nodiscard]]
        int channels() const {
            return channels_;
        }

        [[nodiscard]]
        bool valid() const {
            return data_ != nullptr;
        }

    private:
        std::uint8_t* data_ = nullptr;
        int width_ = 0;
        int height_ = 0;
        int channels_ = 0;
    };


    /*
     * -------------------------------------------------------------------------
     * STB utilities
     * -------------------------------------------------------------------------
     */

    const char* failure_reason();

}
```

And the implementation:

```cpp
// stb_loader.cpp

#include "stb_loader.hpp"

/*
 * STB implementation definitions must occur in exactly ONE translation unit.
 */

#define STB_IMAGE_IMPLEMENTATION
#include <stb_image.h>

namespace stb {

bool Image::load(
    const char* filename,
    int desired_channels
) {
    free();

    int width = 0;
    int height = 0;
    int channels = 0;

    stbi_uc* pixels = stbi_load(
        filename,
        &width,
        &height,
        &channels,
        desired_channels
    );

    if (!pixels) {
        return false;
    }

    data_ = pixels;
    width_ = width;
    height_ = height;

    if (desired_channels != 0) {
        channels_ = desired_channels;
    } else {
        channels_ = channels;
    }

    return true;
}

bool Image::load_from_memory(
    const void* data,
    std::size_t size,
    int desired_channels
) {
    free();

    if (!data || size == 0) {
        return false;
    }

    int width = 0;
    int height = 0;
    int channels = 0;

    stbi_uc* pixels = stbi_load_from_memory(
        static_cast<const stbi_uc*>(data),
        static_cast<int>(size),
        &width,
        &height,
        &channels,
        desired_channels
    );

    if (!pixels) {
        return false;
    }

    data_ = pixels;
    width_ = width;
    height_ = height;

    if (desired_channels != 0) {
        channels_ = desired_channels;
    } else {
        channels_ = channels;
    }

    return true;
}

void Image::free() {

    if (data_) {
        stbi_image_free(data_);

        data_ = nullptr;
    }

    width_ = 0;
    height_ = 0;
    channels_ = 0;
}

const char* failure_reason() {
    return stbi_failure_reason();
}

}
```

### Adding more STB libraries

You can keep the implementation definitions centralized in `stb_loader.cpp`:

```cpp
#define STB_IMAGE_IMPLEMENTATION
#define STB_IMAGE_WRITE_IMPLEMENTATION
#define STB_IMAGE_RESIZE_IMPLEMENTATION
#define STB_TRUETYPE_IMPLEMENTATION

#include <stb_image.h>
#include <stb_image_write.h>
#include <stb_image_resize2.h>
#include <stb_truetype.h>
```

Then expose your own engine-facing API rather than spreading raw STB calls throughout the engine.

For example:

```text
engine/
├── core/
├── graphics/
│   ├── Texture.cpp
│   ├── Texture.hpp
│   └── stb_loader.cpp
├── audio/
├── input/
└── third_party/
    └── stb/
        ├── stb_image.h
        ├── stb_image_write.h
        ├── stb_image_resize2.h
        └── stb_truetype.h
```

And with your Makefile:

```makefile
SOURCES := \
    src/main.cpp \
    src/graphics/Texture.cpp \
    src/graphics/stb_loader.cpp
```

**Important:** STB isn't really a runtime "loader" like a GLAD loader. STB libraries are single-header libraries whose implementation is enabled at compile time with `STB_*_IMPLEMENTATION`. The wrapper above gives your engine a clean **STB subsystem** while ensuring each implementation is compiled only once.
