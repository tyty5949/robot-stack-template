# CMakeLists.txt (snippet)
option(ARM64 "Build for ARM64" OFF)
option(JETSON "Enable Jetson-specific features" OFF)
option(ENABLE_CUDA "Enable CUDA acceleration" OFF)
option(PI5 "Tweak settings for Raspberry Pi 5" OFF)

if(PI5)
  add_definitions(-DPI5)
  # Example: set more aggressive compiler flags if desired
endif()

if(JETSON)
  add_definitions(-DJETSON)
endif()

if(ENABLE_CUDA)
  find_package(CUDAToolkit REQUIRED)
  add_definitions(-DENABLE_CUDA)
  # Link your CUDA bits here …
endif()
