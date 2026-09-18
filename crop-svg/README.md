# crop-svg

Clean up SVG topology exports from the Containerlab VS Code extension’s TopoViewer: convert supported text annotations into native SVG text, crop excess whitespace, and add a small margin.

## Why this exists

TopoViewer exports can look fine in a browser but lose annotations when opened in Inkscape. In the exports that prompted this tool, text boxes were stored as HTML inside SVG `<foreignObject>` elements. Inkscape did not render that HTML, so labels such as link subnets and loopback addresses appeared to be missing. The exported canvas also contained far more whitespace than the topology needed.

`crop-svg` addresses both problems:

1. Converts supported TopoViewer HTML annotations into editable SVG `<text>` and `<tspan>` elements.
2. Uses Inkscape to fit the exported page to the drawing.
3. Adds a configurable margin and saves a new SVG.

The original file stays unchanged. By default, `topology.svg` becomes `topology-cropped.svg` in the same directory.

## Prerequisites

- **Python 3.9 or newer**.
- **Inkscape 1.x**, including its command-line executable.
- The **`crop-svg`** script, saved without a `.py` extension.

No Python packages or `pip install` steps are required. Containerlab, Docker, and VS Code are not needed to process an SVG that has already been exported.

## Install on Linux

### 1. Install dependencies

On Ubuntu or Debian:

```bash
sudo apt update
sudo apt install python3 inkscape
```

Check the installed versions:

```bash
python3 --version
inkscape --version
```

On other distributions, install Python 3 and Inkscape using your distribution’s package manager. Ensure Python meets the minimum version above.

### 2. Install the command

From the directory containing the downloaded `crop-svg` file:

```bash
mkdir -p "$HOME/.local/bin"
install -m 755 ./crop-svg "$HOME/.local/bin/crop-svg"
```

This makes the script executable and installs it for your user without `sudo`.

### 3. Add it to PATH

For Bash, add this line to `~/.bashrc` if it is not already present:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Reload your configuration:

```bash
source ~/.bashrc
```

If you use Zsh, put the line in `~/.zshrc` instead and run `source ~/.zshrc`.

## Install on macOS

### 1. Install dependencies

If you use [Homebrew](https://brew.sh/):

```bash
brew install python
brew install --cask inkscape
```

Alternatively, install Python from [python.org](https://www.python.org/downloads/macos/) and Inkscape from [inkscape.org](https://inkscape.org/release/). Place Inkscape in `/Applications` or your user’s `~/Applications` directory.

Check Python:

```bash
python3 --version
```

The script searches for Inkscape on PATH and in common macOS application locations. Inkscape itself does not need to be added to PATH when it is installed in one of those locations.

### 2. Install the command

From the directory containing the downloaded `crop-svg` file:

```bash
mkdir -p "$HOME/.local/bin"
install -m 755 ./crop-svg "$HOME/.local/bin/crop-svg"
```

### 3. Add it to PATH

For Zsh, the default shell on recent macOS installations, add this line to `~/.zshrc` if it is not already present:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Reload your configuration:

```bash
source ~/.zshrc
```

If you use Bash, add the line to `~/.bash_profile` and run `source ~/.bash_profile` instead.

## Verify installation

On either operating system:

```bash
command -v crop-svg
crop-svg --help
```

The first command should show the installed script under your home directory’s `.local/bin` folder. You can now run `crop-svg` from any directory.

## Usage

Export the topology as an SVG from TopoViewer, including the annotations you want to keep. Then run:

```bash
crop-svg ./topology.svg
```

Output: `./topology-cropped.svg`.

Choose the output filename:

```bash
crop-svg ./topology.svg -o ./topology-clean.svg
```

Adjust the margin:

```bash
crop-svg ./topology.svg --margin 60
```

Crop with no added margin:

```bash
crop-svg ./topology.svg --margin 0
```

Replace an existing output file:

```bash
crop-svg ./topology.svg -o ./topology-clean.svg --force
```

Specify a custom Inkscape executable:

```bash
crop-svg ./topology.svg --inkscape /usr/bin/inkscape
```

On macOS, for example:

```bash
crop-svg ./topology.svg --inkscape /Applications/Inkscape.app/Contents/MacOS/inkscape
```

Quote filenames that contain spaces:

```bash
crop-svg "./My Network.svg"
```

### Options

| Option | Purpose |
| --- | --- |
| `-h`, `--help` | Show usage and available options. |
| `-o`, `--output` | Choose the output path. Defaults to `<input-stem>-cropped.svg`. |
| `--margin` | Add a nonnegative margin on each side. Default: `20` SVG coordinate units, normally pixels. |
| `--inkscape` | Specify the path to the Inkscape executable. |
| `--force` | Allow replacement of an existing output file. |

The input and output must be different files, even when using `--force`. The tool accepts one SVG per invocation; it does not read topology JSON or Containerlab YAML.

## Use the result in a README

Reference the cropped SVG normally:

```markdown
![Network topology](./topology-cropped.svg)
```

Or use an HTML image element to request a display width:

```html
<img src="./topology-cropped.svg" alt="Network topology" width="700">
```

Cropping changes the SVG’s canvas. The image width in your README controls how large that canvas is displayed.

## Troubleshooting

### `crop-svg: command not found`

Check that the script exists at `~/.local/bin/crop-svg`, and reload the shell configuration containing the PATH line. You can also test it directly:

```bash
"$HOME/.local/bin/crop-svg" --help
```

### Inkscape cannot be found

Install Inkscape or supply its executable path using `--inkscape`. On macOS, the executable lives inside `Inkscape.app`; pass the executable path, not the application directory.

### Inkscape crashes from a Snap-installed VS Code terminal

An error such as this can indicate that Inkscape inherited incompatible library settings from the terminal environment:

```text
/snap/core20/current/lib/x86_64-linux-gnu/libpthread.so.0:
undefined symbol: __libc_pthread_init, version GLIBC_PRIVATE
```

First try running `crop-svg` from a regular system terminal outside VS Code. If it works there, try this process-local workaround inside VS Code:

```bash
env -u LD_LIBRARY_PATH \
    -u LD_PRELOAD \
    -u GTK_PATH \
    -u GTK_EXE_PREFIX \
    -u GTK_DATA_PREFIX \
    -u GIO_MODULE_DIR \
    crop-svg ./topology.svg
```

This removes those variables only for that command. The script does not sanitize the environment automatically, and this workaround may not resolve every Inkscape installation issue. A related failure is documented in [VS Code issue #179274](https://github.com/microsoft/vscode/issues/179274).

### An annotation is still missing

The tool can convert annotations present in the exported SVG. It cannot recover text that TopoViewer omitted entirely. Open the original export in a browser to check whether the annotation is present before converting it.

### The crop still contains whitespace

Inkscape crops to drawing bounds. Large background rectangles or other geometry can extend those bounds beyond the visible topology. Remove unwanted background objects and run the conversion again.

## Limitations

- Annotation conversion targets TopoViewer `<foreignObject>` elements whose immediate parent has the `annotation-text` class. It is not a general HTML-to-SVG converter.
- Explicit line breaks are retained, but automatic HTML text wrapping and exact paragraph layout are not reproduced.
- Nested rich text styling is flattened to the outer annotation style with a warning. Unsupported HTML, colored annotation backgrounds, and unsupported CSS lengths may cause conversion to stop with an error.
- Font availability affects text layout. Install the fonts used by the original export for the closest match.
- This is a conversion and cropping tool, not a general topology layout engine. Review the result for overlapping labels.

## Update

Download the replacement script and repeat the installation command from the directory containing it:

```bash
install -m 755 ./crop-svg "$HOME/.local/bin/crop-svg"
```

Your PATH configuration does not need to change.
