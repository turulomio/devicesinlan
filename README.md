# DevicesInLan [![PyPI - Downloads](https://img.shields.io/pypi/dm/devicesinlan?label=Pypi%20downloads)](https://pypi.org/project/devicesinlan/) [![GitHub Downloads](https://img.shields.io/github/downloads/turulomio/devicesinlan/total?label=Github%20downloads)](https://github.com/turulomio/devicesinlan/releases)

## Snapshots

![Snapshot](https://raw.githubusercontent.com/turulomio/devicesinlan/qt5/doc/devicesinlan_snapshots_01.png)

## Links
  
- **Project web page**: <https://github.com/turulomio/devicesinlan/>
- **Releases and Downloads**: <https://github.com/turulomio/devicesinlan/releases>

## Installation

### Standalone Binaries (Linux & Windows)

You can download portable standalone executables directly from **[GitHub Releases](https://github.com/turulomio/devicesinlan/releases)** without needing Python or dependencies installed:

- **Linux (64-bit)**:
  - `devicesinlan-<version>-linux-64bits`: Command-line interface (CLI).
  - `devicesinlan_gui-<version>-linux-64bits`: Graphical interface (GUI).
  - *Usage*: Grant execution permissions (`chmod +x <binary>`) and run it.

- **Windows (64-bit)**:
  - `devicesinlan-<version>-windows-64bits.exe`: Command-line interface (CLI).
  - `devicesinlan_gui-<version>-windows-64bits.exe`: Graphical interface (GUI).
  - *Usage*: Run the `.exe` file directly.

### Linux (pip)

If you use Gentoo, you can find an ebuild at <https://github.com/turulomio/myportage/tree/master/net-analyzer/devicesinlan>.

If you use another distribution compatible with `pip`:

```bash
pip install devicesinlan
```

### Windows (pip)

1. You need to install Python from <https://www.python.org> and add it to the `PATH`.
2. Open a console with Administrator privileges and run:

```cmd
pip install devicesinlan
```

3. If you want to create a Desktop shortcut to launch DevicesInLan, run:

```cmd
devicesinlan_shortcut.exe
```