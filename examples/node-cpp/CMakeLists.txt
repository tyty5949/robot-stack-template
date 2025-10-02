cmake_minimum_required(VERSION 3.16)
project(node-cpp LANGUAGES CXX)

# ---------------- Settings ----------------
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Place runtime output in build/ (or build/bin if you prefer)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
# If you like a bin/ subdir, uncomment:
# set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# ---------------- Options -----------------
option(ARM64 "Build for ARM64" OFF)
option(JETSON "Enable Jetson-specific features" OFF)
option(ENABLE_CUDA "Enable CUDA acceleration" OFF)
option(PI5 "Tweak settings for Raspberry Pi 5" OFF)

# ---------------- Compile flags/defs ------
if(PI5)
  add_compile_definitions(PI5)
  # Example: Pi5-specific tuning (adjust as needed)
  add_compile_options(-O3 -mcpu=cortex-a76)
endif()

if(JETSON)
  add_compile_definitions(JETSON)
  # Jetson SOCs are ARM64; tune if you want:
  if(ARM64)
    add_compile_options(-O3)
  endif()
endif()

if(ARM64)
  add_compile_definitions(ARM64)
  # Safe generic AArch64 tuning (don’t over-specify micro-arch unless you know it’s available)
  add_compile_options(-O2)
endif()

# ---------------- Sources -----------------
# Prefer explicit listing over GLOB for reproducible builds
set(SOURCES
        src/main.cpp
)

# If you have headers:
# target_include_directories(node-cpp PRIVATE include)

# ---------------- Target ------------------
add_executable(node-cpp ${SOURCES})

# ---------------- CUDA (optional) ---------
if(ENABLE_CUDA)
  find_package(CUDAToolkit REQUIRED)
  target_compile_definitions(node-cpp PRIVATE ENABLE_CUDA)
  # Link CUDA runtime as needed; add more libs if you use cuBLAS/CUFFT/etc.
  target_link_libraries(node-cpp PRIVATE CUDA::cudart)
endif()

# ---------------- Threads (optional) ------
# find_package(Threads REQUIRED)
# target_link_libraries(node-cpp PRIVATE Threads::Threads)

# ---------------- MQTT (optional) ---------
# If you later add Eclipse Paho MQTT C library:
# find_package(PahoMqttC CONFIG QUIET)
# if(PahoMqttC_FOUND)
#   target_link_libraries(node-cpp PRIVATE PahoMqttC::PahoMqttC)
#   target_compile_definitions(node-cpp PRIVATE HAVE_PAHO)
# endif()

# ---------------- Warnings ----------------
if (MSVC)
  target_compile_options(node-cpp PRIVATE /W4 /permissive-)
else()
  target_compile_options(node-cpp PRIVATE -Wall -Wextra -Wpedantic)
endif()
