set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 QUIET)

if(NOT pybind11_FOUND)
    message(STATUS "pybind11 not found, skipping Python bindings")
    return()
endif()

pybind11_add_module(SerialCommPython bindings.cpp)
target_link_libraries(SerialCommPython
        PRIVATE SerialComm::SerialComm
)

set_target_properties(SerialCommPython PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/bindings/python
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/bindings/python
)