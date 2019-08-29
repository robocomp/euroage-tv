# RoboComp global CMake
cmake_minimum_required(VERSION 2.8 FATAL_ERROR)

ADD_DEFINITIONS(-O3  -std=c++17 -std=gnu++17)
set(CMAKE_CXX_STANDARD 17)

cmake_policy(SET CMP0048 OLD)
project(RoboComp)
string(TOLOWER ${PROJECT_NAME} PROJECT_NAME_LOWER)

#Set RoboComp directories
set(RoboComp_LIBS_DIR ${RoboComp_SOURCE_DIR}/libs)
set(RoboComp_CLASSES_DIR ${RoboComp_SOURCE_DIR}/classes)
set(RoboComp_INTERFACES_DIR ${RoboComp_SOURCE_DIR}/interfaces)
# Find universal dependencies
set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake/modules/" ${CMAKE_MODULE_PATH})

INSTALL(DIRECTORY "interfaces" DESTINATION /opt/robocomp/ )
