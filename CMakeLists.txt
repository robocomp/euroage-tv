# RoboComp global CMake
cmake_minimum_required(VERSION 2.8 FATAL_ERROR)

ADD_DEFINITIONS(-O3  -std=c++17 -std=gnu++17)
set(CMAKE_CXX_STANDARD 17)
cmake_policy(SET CMP0048 OLD)
project(EuroageTv)
string(TOLOWER ${PROJECT_NAME} PROJECT_NAME_LOWER)
set_property(GLOBAL PROPERTY ALLOW_DUPLICATE_CUSTOM_TARGETS 1)

#Set RoboComp directories
set(RoboComp_LIBS_DIR ${RoboComp_SOURCE_DIR}/libs)
set(RoboComp_CLASSES_DIR ${RoboComp_SOURCE_DIR}/classes)
set(RoboComp_INTERFACES_DIR ${RoboComp_SOURCE_DIR}/interfaces)
# Find universal dependencies
set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake/modules/" ${CMAKE_MODULE_PATH})

add_subdirectory(components/tvGames)
add_subdirectory(components/gameManager)


if(NOT EXISTS ${EuroageTv_SOURCE_DIR}/components/bbdd/prueba1.db)
    message("Downloading ddbb file ${EuroageTv_SOURCE_DIR}/components/bbdd/prueba1.db")
    file(DOWNLOAD "https://robocloud.unex.es/index.php/s/ruKpLWSxCpVasZA/download" ${EuroageTv_SOURCE_DIR}/components/bbdd/prueba1.db SHOW_PROGRESS)
    message("File downloaded")
endif()



if(EXISTS $ENV{HOME}/Desktop/)
    message("$ENV{HOME}/Desktop/  exist")
    install(FILES "tools/Euroage.desktop" DESTINATION $ENV{HOME}/Desktop/ PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE WORLD_READ WORLD_WRITE WORLD_EXECUTE)
else()
    message("$ENV{HOME}/Desktop/ don't exist")
    install(FILES "tools/Euroage.desktop" DESTINATION $ENV{HOME}/Escritorio/ PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE WORLD_READ WORLD_WRITE WORLD_EXECUTE)
endif()
install(FILES "tools/Euroage.desktop" DESTINATION $ENV{HOME}/.config/autostart/ PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE WORLD_READ WORLD_WRITE WORLD_EXECUTE)
install(DIRECTORY "interfaces" DESTINATION /opt/robocomp/ OPTIONAL)





