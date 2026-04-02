cmake_minimum_required(VERSION 3.15)
project(AthenaDriveSerial VERSION 1.0.0 LANGUAGES CXX)

include(FetchContent)
FetchContent_Declare(
        serial_cpp
        GIT_REPOSITORY https://github.com/ami-iit/serial_cpp.git
        GIT_TAG v1.3.4
)
FetchContent_MakeAvailable(serial_cpp)

add_library(SerialComm src/SerialComm.cpp)
target_link_libraries(SerialComm PUBLIC serial_cpp)
target_include_directories(SerialComm
        PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)

target_compile_features(SerialComm PUBLIC cxx_std_20)
add_library(SerialComm::SerialComm ALIAS SerialComm)

option(SERIALCOMM_BUILD_PYTHON "Build python bindings" ON)
if(SERIALCOMM_BUILD_PYTHON)
    add_subdirectory(bindings/python)
endif()

add_subdirectory(examples)