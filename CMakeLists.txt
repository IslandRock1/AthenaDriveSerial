cmake_minimum_required(VERSION 3.15)
project(AthenaDriveSerial)

set(CMAKE_CXX_STANDARD 20)

include(FetchContent)
FetchContent_Declare(
        serial_cpp
        GIT_REPOSITORY https://github.com/ami-iit/serial_cpp.git
        GIT_TAG v1.3.4
)
FetchContent_MakeAvailable(serial_cpp)

add_executable(AthenaDriveSerial main.cpp SerialComm.cpp)
target_link_libraries(AthenaDriveSerial PRIVATE serial_cpp::serial_cpp)