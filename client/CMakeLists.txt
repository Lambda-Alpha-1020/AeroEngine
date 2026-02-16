cmake_minimum_required(VERSION 3.16)
project(login LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_INCLUDE_CURRENT_DIR ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_BUILD_TYPE Debug CACHE STRING "Build type" FORCE)

find_package(Qt6 REQUIRED COMPONENTS Core Widgets Gui)
find_package(OpenSSL REQUIRED)
find_package(CURL REQUIRED)

aux_source_directory(./src srcs)
aux_source_directory(./src/pages pages)

# Specify MSVC UTF-8 encoding   
add_compile_options("$<$<C_COMPILER_ID:MSVC>:/utf-8>")
add_compile_options("$<$<CXX_COMPILER_ID:MSVC>:/utf-8>")

add_executable(${PROJECT_NAME}
    # WIN32 是否开启控制台
    ${srcs} 
    ${pages}
) 
target_link_libraries(${PROJECT_NAME} PRIVATE Qt6::Widgets )

set(CURL_INCLUDE_DIR "D:/Development/programs/client/libs/libcurl/include")
set(CURL_LIBRARY "D:/Development/programs/client/libs/libcurl/lib/libcurl.dll.a")

target_include_directories(login PRIVATE ${CURL_INCLUDE_DIR})
target_link_libraries(login PRIVATE ${CURL_LIBRARY})

