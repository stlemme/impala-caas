cmake_minimum_required(VERSION 3.1)

project(impalapy)

find_package(SWIG)
include(UseSWIG)

find_package(PythonLibs)
include_directories(${PYTHON_INCLUDE_PATH})

find_package(IMPALA REQUIRED)

find_path(IMPALA_INCLUDE_DIR impala/impala.h
	PATHS ${IMPALA_ROOT_DIR}
	PATH_SUFFIXES include src)
find_package(THORIN REQUIRED)
set(IMPALA_INCLUDE_DIRS
	${IMPALA_INCLUDE_DIR}
	${THORIN_INCLUDE_DIRS})
include_directories(${IMPALA_INCLUDE_DIRS})

add_library(libimpala SHARED IMPORTED)
set_property(TARGET libimpala PROPERTY IMPORTED_IMPLIB_DEBUG ${IMPALA_BUILD_DIR}/lib/Debug/libimpala.lib)
set_property(TARGET libimpala PROPERTY IMPORTED_LOCATION_DEBUG ${IMPALA_BUILD_DIR}/bin/Debug/libimpala.dll)
set_property(TARGET libimpala PROPERTY IMPORTED_IMPLIB_RELEASE ${IMPALA_BUILD_DIR}/lib/Release/libimpala.lib)
set_property(TARGET libimpala PROPERTY IMPORTED_LOCATION_RELEASE ${IMPALA_BUILD_DIR}/bin/Release/libimpala.dll)
set(IMPALA_LIBRARIES libimpala ${THORIN_LIBRARIES})

message(STATUS "IMPALA_BUILD_DIR: ${IMPALA_BUILD_DIR}")
message(STATUS "IMPALA_INCLUDE_DIRS: ${IMPALA_INCLUDE_DIRS}")

include_directories(${CMAKE_CURRENT_SOURCE_DIR})

set(_interface_file impalapy.i)
set_source_files_properties(${_interface_file} PROPERTIES CPLUSPLUS ON)

set(CMAKE_SWIG_FLAGS -py3)
set(CMAKE_SWIG_OUTDIR ${CMAKE_CFG_INTDIR})

swig_add_module(impalapy python ${_interface_file} impalapymodule.cpp)
swig_link_libraries(impalapy ${PYTHON_LIBRARIES} ${IMPALA_LIBRARIES})

