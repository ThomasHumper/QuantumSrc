# TODO

## Status Legend

- [ ] **Planned** — not started
- [~] **In Progress** — currently being worked on
- [?] **Investigate** — requires research, design, or a decision
- [x] **Done** — completed
- [!] **Blocked** — waiting on a dependency or external information

---

## Engine

### Rendering

#### Rendering Architecture
- [ ] Define renderer abstraction/API
- [ ] Define GPU capability detection
- [ ] Define feature levels and fallback paths
- [ ] Define shader/material abstraction
- [ ] Define texture abstraction
- [ ] Define vertex/index buffer abstraction
- [ ] Define framebuffer/render-target abstraction
- [ ] Define render-state abstraction
- [ ] Define command/submission model
- [ ] Define software-rendering fallback

#### OpenGL / OpenGL ES / WebGL

- [ ] **OpenGL 1.1**
  - [ ] Core renderer
  - [ ] Capability detection
  - [ ] Optional extensions
    - [ ] `GL_ARB_multitexture`
    - [ ] `GL_ARB_texture_border_clamp`
      - [ ] Fall back to `GL_CLAMP`
    - [ ] `GL_ARB_vertex_program`
    - [ ] `GL_ARB_fragment_program`

- [ ] **OpenGL 2.0 / OpenGL ES 2.0 / WebGL 1.0**
  - [ ] Renderer
  - [ ] Shader pipeline
  - [ ] Texture handling
  - [ ] Buffer management

- [ ] **OpenGL 3.3 / OpenGL ES 3.0 / WebGL 2.0**
  - [ ] Renderer
  - [ ] Modern shader pipeline
  - [ ] VAO/VBO handling
  - [ ] Framebuffers
  - [ ] Instancing

#### Direct3D

- [ ] **Direct3D 7 / 8**
  - [ ] Windows backend
  - [ ] XDK backend
  - [ ] Capability detection
  - [ ] Fixed-function rendering

- [ ] **Direct3D 11**
  - [ ] Windows backend
  - [ ] GDK backend
  - [ ] Shader pipeline
  - [ ] Resource management

#### Console / Embedded Rendering

- [ ] **XGU / PBKit**
  - [ ] NXDK backend

-
