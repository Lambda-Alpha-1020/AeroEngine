cmake_minimum_required(VERSION 3.16)
project(AeroEngineQt LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 COMPONENTS Widgets REQUIRED)

add_executable(AeroEngineQt
    src/main.cpp
    src/loginwidget.cpp
    src/loginwidget.h
)

set_target_properties(AeroEngineQt PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
    AUTOMOC ON
    AUTOUIC ON
    AUTORCC ON
)

target_link_libraries(AeroEngineQt PRIVATE Qt6::Widgets)
target_compile_options(AeroEngineQt PRIVATE -finput-charset=UTF-8)
