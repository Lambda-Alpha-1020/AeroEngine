# AeroEngine - Minimal C++ Win32 App

This folder contains a minimal Qt Widgets GUI application implemented in C++ and a `CMakeLists.txt` to build it.

## Files

- `src/main.cpp`: Qt Widgets "Hello, Qt!" sample.
- `CMakeLists.txt`: CMake project to build the application using Qt6.

## Requirements

- CMake >= 3.16
- Qt 6 development libraries (or adjust to Qt5 in `CMakeLists.txt`)

## Build (Linux / macOS)

```bash
mkdir build
cd build
cmake ..
cmake --build . --config Release
```

可选使用 `-G "Ninja"` 或其它生成器。

## Build on Windows (Visual Studio)

1. 安装 Qt 开发包并打开对应的 Visual Studio 命令提示符。
2. 使用 CMake 生成 Visual Studio 解决方案：

```powershell
mkdir build
cd build
cmake -G "Visual Studio 17 2022" ..
cmake --build . --config Release
```

生成后可在 `build/bin/` 下找到可执行文件。

## Notes

- 如需使用 Qt5，将 `CMakeLists.txt` 中的 `find_package(Qt6 COMPONENTS Widgets REQUIRED)` 改为 `find_package(Qt5 COMPONENTS Widgets REQUIRED)` 并将 `target_link_libraries` 指向 `Qt5::Widgets`。
- 在 Linux 上需要安装对应的 `qtbase` 开发包，例如在 Ubuntu 上：`sudo apt install qt6-base-dev`（或 `qtbase5-dev` 用于 Qt5）。
