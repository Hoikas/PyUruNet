#    PyUruNet
#    Copyright (C) 2016  Adam 'Hoikas' Johnson <AdamJohnso AT gmail DOT com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

cmake_minimum_required(VERSION 3.15)
project(_urunet LANGUAGES CXX)

# ==============================================================================

# Shouldn't be needed due to pybind11
#[[
include(CheckIPOSupported)
message(STATUS "checking for IPO support...")
check_ipo_supported(RESULT _IPO_SUPPORTED OUTPUT _IPO_OUTPUT LANGUAGES CXX)
message(STATUS "checking for IPO support... ${_IPO_SUPPORTED} ${_IPO_OUTPUT}")
set(CMAKE_INTERPROCEDURAL_OPTIMIZATION_DEBUG FALSE CACHE BOOL "")
set(CMAKE_INTERPROCEDURAL_OPTIMIZATION_MINSIZEREL ${_IPO_SUPPORTED} CACHE BOOL "")
set(CMAKE_INTERPROCEDURAL_OPTIMIZATION_RELWITHDEBINFO ${_IPO_SUPPORTED} CACHE BOOL "")
set(CMAKE_INTERPROCEDURAL_OPTIMIZATION_RELEASE ${_IPO_SUPPORTED} CACHE BOOL "")
#]]

# ==============================================================================

include(FetchContent)
FetchContent_Declare(pybind11
    GIT_REPOSITORY "https://github.com/pybind/pybind11.git"
    GIT_TAG "v2.7.1"
)
FetchContent_Declare(catch2
    GIT_REPOSITORY "https://github.com/catchorg/Catch2.git"
    GIT_TAG "v2.13.7"
)

# ==============================================================================

find_package(Python3 REQUIRED COMPONENTS Interpreter Development)

set(CATCH_INSTALL_DOCS OFF)

# ==============================================================================

# Add all the dependency libraries here so they become part of our build process.
# Note that this will only work as expected for CMake-based libraries that support
# NOT being a top-level project. SOL on autotools, etc. junk.
FetchContent_MakeAvailable(pybind11 catch2)

# ==============================================================================

set(URUNET_SOURCES
    rc4.cpp
    sha.cpp
)
set(URUNET_HEADERS
    urunet.h
)

add_library(urunet OBJECT ${URUNET_SOURCES} ${URUNET_HEADERS})
target_compile_features(urunet PUBLIC cxx_std_20)
target_link_libraries(urunet PUBLIC Catch2::Catch2)

pybind11_add_module(urunet_module module.cpp)
target_link_libraries(urunet_module PRIVATE urunet)
set_target_properties(urunet_module PROPERTIES OUTPUT_NAME _urunet)

set(BUILD_TESTING ON CACHE BOOL "Build tests with catch2")
if(BUILD_TESTING)
    add_executable(urunet_test test.cpp)
    target_link_libraries(urunet_test PRIVATE urunet)

    include(CTest)
    include("${catch2_SOURCE_DIR}/contrib/Catch.cmake")
    catch_discover_tests(urunet_test)
endif()
