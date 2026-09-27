```ruby
#!/usr/bin/env ruby
# engine.rb
#
# Cross-platform engine project orchestrator.
#
# Examples:
#   ruby engine.rb configure
#   ruby engine.rb build
#   ruby engine.rb build --release
#   ruby engine.rb clean
#   ruby engine.rb run
#   ruby engine.rb test
#   ruby engine.rb assets
#   ruby engine.rb fonts
#   ruby engine.rb tools
#   ruby engine.rb package
#   ruby engine.rb all
#
# The script intentionally does not hard-code a particular compiler.
# It uses CMake when available and falls back to the existing Makefile.

require "fileutils"
require "open3"
require "optparse"
require "pathname"

ROOT = Pathname.new(__dir__).realpath

DIRS = {
  src:      ROOT / "src",
  include:  ROOT / "include",
  build:    ROOT / "build",
  bin:      ROOT / "bin",
  assets:   ROOT / "assets",
  tools:    ROOT / "tools",
  tests:    ROOT / "tests",
  third:    ROOT / "third_party",
  scripts:  ROOT / "scripts",
  dist:     ROOT / "dist"
}.freeze

OPTIONS = {
  release: false,
  verbose: false,
  platform: nil,
  renderer: nil
}

def log(message)
  puts "[engine] #{message}"
end

def fail!(message)
  warn "[engine] ERROR: #{message}"
  exit 1
end

def command_exists?(command)
  ENV.fetch("PATH", "").split(File::PATH_SEPARATOR).any? do |path|
    candidate = File.join(path, command)
    File.file?(candidate) && File.executable?(candidate)
  end
end

def run!(*command, env: {})
  log("$ #{command.join(" ")}")

  ok = if OPTIONS[:verbose]
         system(env, *command)
       else
         system(env, *command)
       end

  fail!("command failed: #{command.join(" ")}") unless ok
end

def capture(*command)
  stdout, stderr, status = Open3.capture3(*command)

  return stdout.strip if status.success?

  nil
end

def ensure_directories
  DIRS.each_value do |dir|
    FileUtils.mkdir_p(dir)
  end
end

def cmake?
  command_exists?("cmake")
end

def make?
  command_exists?("make")
end

def compiler?
  command_exists?("g++") ||
    command_exists?("clang++") ||
    command_exists?("cl")
end

def cmake_generator
  return "Ninja" if command_exists?("ninja")
  return "Unix Makefiles"
end

# ---------------------------------------------------------------------------
# Dependency checks
# ---------------------------------------------------------------------------

def check_dependencies
  log "Checking build dependencies..."

  unless cmake? || make?
    fail!("Neither cmake nor make was found.")
  end

  unless compiler?
    fail!("No C++ compiler was found.")
  end

  log "Build dependencies OK."

  puts
  puts "Optional components:"
  puts "  CMake:       #{cmake? ? "yes" : "no"}"
  puts "  Make:        #{make? ? "yes" : "no"}"
  puts "  Ninja:       #{command_exists?("ninja") ? "yes" : "no"}"
  puts "  Ruby:        #{RUBY_VERSION}"
  puts
end

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def configure
  ensure_directories

  if cmake?
    generator = cmake_generator

    args = [
      "cmake",
      "-S", ROOT.to_s,
      "-B", DIRS[:build].to_s,
      "-G", generator
    ]

    args << "-DCMAKE_BUILD_TYPE=Release" if OPTIONS[:release]
    args << "-DCMAKE_BUILD_TYPE=Debug" unless OPTIONS[:release]

    args << "-DENGINE_PLATFORM=#{OPTIONS[:platform]}" if OPTIONS[:platform]
    args << "-DENGINE_RENDERER=#{OPTIONS[:renderer]}" if OPTIONS[:renderer]

    run!(*args)
  elsif File.exist?(ROOT / "Makefile")
    log "Using existing Makefile."
  else
    fail!("No CMakeLists.txt or Makefile found.")
  end
end

# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build
  configure if !File.directory?(DIRS[:build]) || Dir.empty?(DIRS[:build])

  if cmake? && File.exist?(DIRS[:build] / "CMakeCache.txt")
    args = [
      "cmake",
      "--build", DIRS[:build].to_s
    ]

    args += ["--config", OPTIONS[:release] ? "Release" : "Debug"]

    run!(*args)
  elsif make?
    target = OPTIONS[:release] ? "release" : "debug"
    run!("make", target)
  else
    fail!("Unable to determine how to build the project.")
  end
end

# ---------------------------------------------------------------------------
# Clean
# ---------------------------------------------------------------------------

def clean
  log "Cleaning build artifacts..."

  if File.directory?(DIRS[:build])
    FileUtils.rm_rf(DIRS[:build])
  end

  if File.directory?(DIRS[:bin])
    FileUtils.rm_rf(DIRS[:bin])
  end

  log "Clean complete."
end

# ---------------------------------------------------------------------------
# Components
# ---------------------------------------------------------------------------

COMPONENTS = {
  "stb" => "STB image loading",
  "lz4" => "LZ4 compression",
  "schrift" => "libschrift font rasterization",
  "gl" => "OpenGL loader",
  "audio" => "OpenAL/audio",
  "physics" => "physics",
  "filesystem" => "PAF/PKD/file system",
  "renderer" => "renderer backends",
  "input" => "keyboard/mouse/controller/touch",
  "ui" => "UI system",
  "server" => "network/server"
}.freeze

def component_status
  puts
  puts "Engine components"
  puts "================="
  puts

  COMPONENTS.each do |name, description|
    source_candidates = [
      DIRS[:src] / name,
      DIRS[:src] / "#{name}.cpp",
      DIRS[:include] / name,
      DIRS[:include] / "#{name}.hpp"
    ]

    present = source_candidates.any?(&:exist?)

    status = present ? "present" : "planned"

    puts format(
      "  %-14s %-10s %s",
      name,
      status,
      description
    )
  end

  puts
end

# ---------------------------------------------------------------------------
# Asset pipeline
# ---------------------------------------------------------------------------

def assets
  ensure_directories

  log "Processing assets..."

  asset_script = DIRS[:scripts] / "assets.rb"

  if asset_script.exist?
    run!("ruby", asset_script.to_s)
    return
  end

  asset_batch = DIRS[:scripts] / "fetch_assets.bat"

  if asset_batch.exist? && Gem.win_platform?
    run!("cmd", "/c", asset_batch.to_s)
    return
  end

  log "No asset processing script found."
  log "Assets directory: #{DIRS[:assets]}"
end

# ---------------------------------------------------------------------------
# Font pipeline
# ---------------------------------------------------------------------------

def fonts
  log "Checking font assets..."

  font_dirs = [
    DIRS[:assets] / "fonts",
    DIRS[:assets] / "font"
  ]

  font_dir = font_dirs.find(&:directory?)

  unless font_dir
    log "No font directory found."
    return
  end

  fonts = Dir.glob(
    font_dir / "**/*.{ttf,otf,woff,woff2}"
  )

  puts
  puts "Fonts:"
  fonts.each do |font|
    puts "  #{Pathname.new(font).relative_path_from(ROOT)}"
  end

  puts
  puts "libschrift: #{fonts.empty? ? "no fonts found" : "ready"}"
end

# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

def tools
  log "Running engine tools..."

  tool_dir = DIRS[:tools]

  unless tool_dir.directory?
    log "No tools directory."
    return
  end

  ruby_tools = Dir.glob(tool_dir / "*.rb")

  ruby_tools.each do |tool|
    log "Tool: #{Pathname.new(tool).basename}"
  end

  log "#{ruby_tools.length} Ruby tools found."
end

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test
  log "Running tests..."

  if cmake? && File.exist?(DIRS[:build] / "CTestTestfile.cmake")
    run!(
      "ctest",
      "--test-dir", DIRS[:build].to_s,
      "--output-on-failure"
    )
    return
  end

  test_binary = DIRS[:bin] / "engine_tests"

  if test_binary.file?
    run!(test_binary.to_s)
    return
  end

  log "No test runner found."
end

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

def executable_path
  names = Gem.win_platform? ?
    ["engine.exe", "game.exe"] :
    ["engine", "game"]

  names.each do |name|
    candidate = DIRS[:bin] / name
    return candidate if candidate.file?
  end

  nil
end

def run_game
  exe = executable_path

  unless exe
    fail!(
      "Engine executable not found. Build the project first."
    )
  end

  run!(exe.to_s)
end

# ---------------------------------------------------------------------------
# Package
# ---------------------------------------------------------------------------

def package
  ensure_directories

  log "Creating distribution package..."

  FileUtils.rm_rf(DIRS[:dist])
  FileUtils.mkdir_p(DIRS[:dist])

  [
    DIRS[:bin],
    DIRS[:assets]
  ].each do |source|
    next unless source.exist?

    destination = DIRS[:dist] / source.basename
    FileUtils.cp_r(source, destination)
  end

  manifest = DIRS[:dist] / "engine-manifest.txt"

  File.open(manifest, "w") do |file|
    file.puts "Engine package"
    file.puts "=============="
    file.puts "Platform: #{OPTIONS[:platform] || "default"}"
    file.puts "Renderer: #{OPTIONS[:renderer] || "default"}"
    file.puts "Build: #{OPTIONS[:release] ? "Release" : "Debug"}"
    file.puts "Ruby: #{RUBY_VERSION}"
  end

  log "Package written to #{DIRS[:dist]}"
end

# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------

def all
  check_dependencies
  ensure_directories
  assets
  configure
  build
  test
  package
end

# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------

def status
  puts
  puts "Engine project"
  puts "=============="
  puts
  puts "Root:     #{ROOT}"
  puts "Build:    #{DIRS[:build]}"
  puts "Assets:   #{DIRS[:assets]}"
  puts "Platform: #{OPTIONS[:platform] || "default"}"
  puts "Renderer: #{OPTIONS[:renderer] || "default"}"
  puts "Build:    #{OPTIONS[:release] ? "Release" : "Debug"}"
  puts

  component_status
end

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

parser = OptionParser do |opts|
  opts.banner = <<~BANNER
    Engine build/orchestration utility

    Usage:
      ruby engine.rb COMMAND [options]

  BANNER

  opts.on("--release", "Use Release configuration") do
    OPTIONS[:release] = true
  end

  opts.on("--platform NAME", "Select target platform") do |name|
    OPTIONS[:platform] = name
  end

  opts.on("--renderer NAME", "Select renderer backend") do |name|
    OPTIONS[:renderer] = name
  end

  opts.on("-v", "--verbose", "Verbose command output") do
    OPTIONS[:verbose] = true
  end

  opts.on("-h", "--help", "Show help") do
    puts opts
    exit
  end
end

begin
  parser.parse!

  command = ARGV.shift || "status"

  case command
  when "check"
    check_dependencies

  when "configure"
    configure

  when "build"
    build

  when "clean"
    clean

  when "rebuild"
    clean
    build

  when "run"
    run_game

  when "test"
    test

  when "assets"
    assets

  when "fonts"
    fonts

  when "tools"
    tools

  when "components"
    component_status

  when "package"
    package

  when "all"
    all

  when "status"
    status

  else
    fail!("Unknown command: #{command}")
  end

rescue Interrupt
  warn "\n[engine] Interrupted."
  exit 130
end
```

### Suggested project layout

```text id="9k3p7m"
engine/
├── CMakeLists.txt
├── Makefile
├── engine.rb
│
├── include/
│   ├── engine/
│   │   ├── renderer/
│   │   ├── audio/
│   │   ├── physics/
│   │   ├── filesystem/
│   │   ├── input/
│   │   └── ui/
│   │
│   └── third_party/
│       ├── schrift_loader.hpp
│       ├── stb_loader.hpp
│       └── lz4_loader.hpp
│
├── src/
│   ├── renderer/
│   │   ├── gl11/
│   │   ├── gl20/
│   │   ├── gl33/
│   │   ├── d3d7/
│   │   ├── d3d8/
│   │   ├── d3d11/
│   │   ├── xgu/
│   │   ├── gskit/
│   │   ├── pvr/
│   │   ├── citro3d/
│   │   ├── gx/
│   │   └── software/
│   │
│   ├── audio/
│   │   ├── openal/
│   │   └── aica/
│   │
│   ├── filesystem/
│   │   ├── paf/
│   │   ├── pkd/
│   │   └── compression/
│   │       └── lz4/
│   │
│   ├── fonts/
│   │   └── schrift/
│   │
│   ├── image/
│   │   └── stb/
│   │
│   ├── physics/
│   ├── input/
│   ├── ui/
│   ├── server/
│   └── main.cpp
│
├── third_party/
│   ├── stb/
│   ├── lz4/
│   └── schrift/
│
├── assets/
│   ├── fonts/
│   ├── textures/
│   ├── models/
│   ├── maps/
│   ├── audio/
│   └── scripts/
│
├── tools/
│   ├── paf/
│   ├── pkd/
│   ├── p3m/
│   ├── ptm/
│   └── ptf/
│
├── scripts/
│   └── fetch_assets.bat
│
├── tests/
├── build/
├── bin/
└── dist/
```

The important part is that the Ruby script becomes the **top-level coordinator**:

```text
                         engine.rb
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
      Assets              Build               Tools
        │                   │                   │
     PAF/PKD            CMake/Make          P3M/PTM/PTF
        │                   │
        └──────────────┬────┘
                       │
                    Engine
                       │
       ┌───────────────┼────────────────┐
       │               │                │
    Rendering         Audio          Filesystem
       │               │                │
 GL/D3D/PVR/GX     OpenAL/AICA       LZ4/PAF/PKD
       │
   ┌───┴─────────────────────────────┐
   │                                 │
 libschrift                         STB
   │                                 │
 Fonts                              Images
```

### Typical commands

```text id="j5v8rr"
# Show engine/component status
ruby engine.rb status

# Check compiler/build dependencies
ruby engine.rb check

# Configure
ruby engine.rb configure

# Debug build
ruby engine.rb build

# Release build
ruby engine.rb build --release

# Rebuild
ruby engine.rb rebuild

# Build a specific backend
ruby engine.rb build --renderer gl33

# Build for a platform
ruby engine.rb build --platform windows

# Fetch/process assets
ruby engine.rb assets

# Inspect fonts
ruby engine.rb fonts

# Run tools
ruby engine.rb tools

# Run tests
ruby engine.rb test

# Run the game
ruby engine.rb run

# Create distribution
ruby engine.rb package

# Complete pipeline
ruby engine.rb all
```

This keeps the **Ruby layer independent of the actual engine runtime**: C++ owns rendering/audio/filesystem/etc., while Ruby coordinates configuration, asset processing, building, testing, and packaging.
