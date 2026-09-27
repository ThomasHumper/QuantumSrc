# PlatinumSrc Tools

A collection of tools, plugins, language definitions, and project files used by **PlatinumSrc**.

Each directory contains a separate component. Refer to the component's own README when additional documentation is available.

## Contents

| Directory | Description |
|---|---|
| `blender/` | Blender plugins for PlatinumSrc |
| `crc/` | CRC utility |
| `gtksourceview/` | GtkSourceView syntax highlighting |
| `paftool/` | PAF archive utility |
| `platinum/` | PTM music tracker |
| `projects/` | Platform-specific project files and templates |
| `ptftool/` | PTF image conversion utility |

---

## `blender/`

Blender plugins for importing and exporting PlatinumSrc assets.

Individual plugins may have additional installation and usage instructions. See the README in each plugin's directory.

### Installation

1. Open Blender.
2. Add the `blender/` directory to Blender's script directories.
3. Open Blender's **System** menu from the Blender icon menu.
4. Select **Reload Scripts**.

---

## `crc/`

A small utility for calculating and printing the CRC values used by PlatinumSrc.

### Build

```sh
cd crc
make
```

### Usage

Run the resulting `crc` executable. Input can be provided through standard input and/or command-line arguments.

```sh
./crc
```

For example:

```sh
echo "example" | ./crc
```

---

## `gtksourceview/`

GtkSourceView language definitions for PlatinumSrc-related file formats and scripting languages.

The `.lang` files can be installed system-wide or for the current user.

### Installation

Copy or link the `.lang` files into one of the following GtkSourceView language-spec directories:

```text
/usr/share/gtksourceview-4/language-specs/
/usr/share/gtksourceview-3.0/language-specs/
~/.local/share/gtksourceview-4/language-specs/
~/.local/share/gtksourceview-3.0/language-specs/
```

The exact directory depends on the GtkSourceView version installed on your system.

After installing the files, restart applications using GtkSourceView.

---

## `paftool/`

A command-line utility for creating, inspecting, extracting, and modifying **PAF archives**.

### Build

```sh
cd paftool
make
```

### Usage

```sh
./paftool --help
```

See the built-in help for the available commands and options.

---

## `platinum/`

A music tracker for composing and editing **PTM** (`.ptm`) music files.

### Build

```sh
cd platinum
make
```

### Run

```sh
./platinum
```

---

## `projects/`

Project files and templates for platforms that cannot use the standard PlatinumSrc Makefile directly.

This directory may contain platform-specific project files, build configurations, and templates.

See the documentation within each project directory for platform-specific instructions.

---

## `ptftool/`

A command-line utility for converting images into the **PTF** image format.

### Build

```sh
cd ptftool
make
```

### Usage

```sh
./ptftool --help
```

See the built-in help for supported input formats, output options, and conversion settings.

---

## Building

Most command-line tools use a local Makefile and can be built independently:

```sh
cd <tool>
make
```

For example:

```sh
cd paftool
make
```

The resulting executable will normally be located in the same directory.

## License

See the license files included with the project and its individual components.
