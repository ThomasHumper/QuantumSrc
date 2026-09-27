# QuantumSrc

![Thumbnail](/internal/thumbnail.png)

**QuantumSrc** is a cross-platform game engine focused on portability, low-level rendering, custom asset formats, and support for both modern and legacy gaming hardware.

The engine is designed around a modular architecture, allowing the same core systems to be adapted to a wide range of graphics APIs, consoles, and platforms. Rendering backends can target APIs such as OpenGL and Direct3D, while platform-specific backends can support hardware such as the Dreamcast, PlayStation 2, Nintendo GameCube/Wii, Nintendo 3DS, and other specialized targets.

## Features

- Cross-platform C++ engine core
- Modular renderer architecture
- OpenGL 1.1/2.0/3.3 support
- OpenGL ES and WebGL targets
- Direct3D support
- Software rendering
- Platform-specific renderers
- Dreamcast PVR support
- PlayStation 2 GSKit support
- GameCube/Wii GX support
- Nintendo 3DS Citro3D support
- Xbox/NXDK rendering support
- Hardware-accelerated and software audio paths
- OpenAL audio support
- Custom PAF and PKD asset formats
- LZ4 and other compression support
- libschrift font rasterization
- STB image loading
- Custom map, model, texture, and material pipelines
- PBASIC scripting support
- Physics system
- Keyboard, mouse, controller, and touch input
- UI framework
- Client/server networking
- Built-in dedicated server support
- Cross-platform asset and development tools
- Blender integration
- PTM music tracker
- PAF archive tools
- PTF image conversion tools

## Architecture

QuantumSrc separates the engine into several independent subsystems:

```text
                         QuantumSrc
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
        Core               Rendering            Audio
          │                   │                   │
      ┌───┼───┐        ┌─────┼─────┐        ┌────┼────┐
      │   │   │        │     │     │        │    │    │
   Files  UI Input    OpenGL D3D  Software  OpenAL AICA
      │
   ┌──┴───────────────┐
   │                  │
  PAF                PKD
   │                  │
 Asset/Archive      Database
```

The renderer and platform layers are intentionally separated from the engine core so that platform-specific implementations can be added without rewriting gameplay, asset management, networking, or other core systems.

## Asset Pipeline

QuantumSrc uses a custom asset pipeline designed around the project's native formats and development tools.

```text
Blender
   │
   ├── P3M
   ├── PTF
   └── Map/Project data
          │
          ▼
       Tools
          │
     ┌────┼────┐
     │    │    │
    PAF  PKD  PMF
     │    │    │
     └────┼────┘
          ▼
       QuantumSrc
```

The tooling ecosystem includes Blender plugins, archive utilities, image conversion tools, music tools, syntax definitions, and platform-specific project templates.

## Design Goals

QuantumSrc is intended to make it possible to develop a game once while retaining control over the platform-specific portions of the engine.

The primary goals are:

- **Portability** — support a broad range of platforms and graphics hardware.
- **Modularity** — keep platform implementations isolated from engine systems.
- **Low-level control** — expose the capabilities of each target rather than requiring every platform to behave identically.
- **Custom formats** — provide efficient formats for distributing and loading game data.
- **Tooling** — maintain a complete workflow from content creation to the final game build.
- **Longevity** — avoid making the engine dependent on a single graphics API, operating system, or hardware generation.

QuantumSrc is ultimately intended to serve as both a modern cross-platform engine and a framework for experimenting with rendering, audio, asset formats, and game development across generations of hardware.
