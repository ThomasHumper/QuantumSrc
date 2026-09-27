```cpp
// schrift_loader.hpp
#pragma once

#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

#include <schrift.h>

namespace schrift {

struct Bitmap {
    int width = 0;
    int height = 0;
    int stride = 0;

    std::vector<std::uint8_t> pixels;

    [[nodiscard]]
    bool empty() const noexcept {
        return pixels.empty();
    }

    [[nodiscard]]
    const std::uint8_t* data() const noexcept {
        return pixels.data();
    }

    [[nodiscard]]
    std::uint8_t* data() noexcept {
        return pixels.data();
    }
};

class Font {
public:
    Font() = default;

    Font(const Font&) = delete;
    Font& operator=(const Font&) = delete;

    Font(Font&& other) noexcept
        : font_(other.font_) {
        other.font_ = nullptr;
    }

    Font& operator=(Font&& other) noexcept {
        if (this != &other) {
            reset();

            font_ = other.font_;
            other.font_ = nullptr;
        }

        return *this;
    }

    ~Font() {
        reset();
    }

    bool load(const std::string& filename);

    bool load_memory(
        const void* data,
        std::size_t size
    );

    void reset() noexcept;

    [[nodiscard]]
    bool valid() const noexcept {
        return font_ != nullptr;
    }

    /*
     * Rasterize a single glyph.
     *
     * The glyph bitmap uses 8-bit grayscale coverage:
     *
     *   0   = transparent
     *   255 = fully covered
     */
    bool rasterize(
        int codepoint,
        float size,
        Bitmap& bitmap
    ) const;

    [[nodiscard]]
    SFT* native_handle() noexcept {
        return font_;
    }

    [[nodiscard]]
    const SFT* native_handle() const noexcept {
        return font_;
    }

private:
    SFT* font_ = nullptr;
};

} // namespace schrift
```

```cpp
// schrift_loader.cpp

#include "schrift_loader.hpp"

#include <fstream>

namespace schrift {

bool Font::load(const std::string& filename) {
    reset();

    /*
     * Read the complete font file.
     */
    std::ifstream file(
        filename,
        std::ios::binary | std::ios::ate
    );

    if (!file) {
        return false;
    }

    const std::streamsize size = file.tellg();

    if (size <= 0) {
        return false;
    }

    file.seekg(0, std::ios::beg);

    std::vector<std::uint8_t> data(
        static_cast<std::size_t>(size)
    );

    if (!file.read(
        reinterpret_cast<char*>(data.data()),
        size
    )) {
        return false;
    }

    return load_memory(data.data(), data.size());
}

bool Font::load_memory(
    const void* data,
    std::size_t size
) {
    reset();

    if (!data || size == 0) {
        return false;
    }

    /*
     * libschrift expects the font data to remain available for the
     * lifetime of the SFT object. Therefore this simple wrapper is
     * intended for font data with a lifetime longer than the Font.
     *
     * For a production asset manager, keep the original font buffer
     * in the Font object as an additional member.
     */

    font_ = sft_load_font(
        data,
        size
    );

    return font_ != nullptr;
}

void Font::reset() noexcept {
    if (font_) {
        sft_freefont(font_);
        font_ = nullptr;
    }
}

bool Font::rasterize(
    int codepoint,
    float size,
    Bitmap& bitmap
) const {
    bitmap = {};

    if (!font_ || size <= 0.0f) {
        return false;
    }

    SFT sft = *font_;

    sft.xScale = size;
    sft.yScale = size;

    /*
     * Ask libschrift for the glyph metrics.
     */
    SFT_Glyph glyph;

    if (sft_lookup(&sft, codepoint, &glyph) < 0) {
        return false;
    }

    SFT_LMetrics metrics;

    if (sft_lmetrics(
        &sft,
        codepoint,
        &metrics
    ) < 0) {
        return false;
    }

    /*
     * Determine glyph bitmap dimensions.
     */
    SFT_GMetrics gmetrics;

    if (sft_gmetrics(
        &sft,
        codepoint,
        &gmetrics
    ) < 0) {
        return false;
    }

    const int width = gmetrics.minWidth;
    const int height = gmetrics.minHeight;

    if (width <= 0 || height <= 0) {
        return true;
    }

    bitmap.width = width;
    bitmap.height = height;
    bitmap.stride = width;

    bitmap.pixels.resize(
        static_cast<std::size_t>(width) *
        static_cast<std::size_t>(height)
    );

    /*
     * Rasterize into an 8-bit grayscale bitmap.
     */
    if (sft_render(
        &sft,
        codepoint,
        bitmap.pixels.data()
    ) < 0) {
        bitmap = {};
        return false;
    }

    return true;
}

} // namespace schrift
```

### Usage

```cpp
schrift::Font font;

if (!font.load("assets/fonts/engine.ttf")) {
    std::cerr << "Failed to load font\n";
    return;
}

schrift::Bitmap glyph;

if (!font.rasterize(
        'A',
        32.0f,
        glyph)) {

    std::cerr << "Failed to rasterize glyph\n";
    return;
}

std::cout
    << "Glyph: "
    << glyph.width
    << "x"
    << glyph.height
    << '\n';
```

### Engine integration

I'd put it behind your engine's font abstraction rather than exposing libschrift throughout the renderer:

```text
Engine
└── Text
    ├── Font
    ├── FontManager
    ├── Glyph
    ├── FontAtlas
    └── Rasterizer
          └── libschrift
```

Then your renderer only needs to deal with an engine-owned `Glyph`/`FontAtlas`, allowing libschrift to be replaced later without changing the rendering API.

**One correction for a production implementation:** the `load_memory()` example above needs to retain the font byte buffer for as long as libschrift references it. For an asset system, I'd make `Font` own a `std::vector<std::uint8_t>` alongside the `SFT*`; that avoids dangling font-data pointers when loading from memory.
