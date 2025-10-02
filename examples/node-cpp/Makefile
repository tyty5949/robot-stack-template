# -------- Config --------
BUILD_DIR        ?= build
CMAKE_BUILD_TYPE ?= Release
GEN              ?= Ninja

# Feature toggles (adjust if your CMakeLists uses them)
JETSON_FLAGS     ?= -DJETSON=ON -DENABLE_CUDA=ON
ARM64_FLAGS      ?= -DARM64=ON

.PHONY: build-pi build-pi5 build-amd64 build-jetson build-docker clean distclean

# ---- Helpers ----
define CMAKE_CONFIGURE
cmake -S . -B $(BUILD_DIR) -G $(GEN) -DCMAKE_BUILD_TYPE=$(CMAKE_BUILD_TYPE) $(1)
endef

define CMAKE_BUILD
cmake --build $(BUILD_DIR) -j
endef

# ---- Native builds ----
build-amd64:
	$(call CMAKE_CONFIGURE,)
	$(call CMAKE_BUILD)
	@echo "✅ C++ node built for amd64 → $(BUILD_DIR)/"

# Pi 4 (arm64 on-device build)
build-pi:
	$(call CMAKE_CONFIGURE,$(ARM64_FLAGS))
	$(call CMAKE_BUILD)
	@echo "✅ C++ node built for Pi (arm64) → $(BUILD_DIR)/"

# Pi 5 uses same arm64 flags; add extra opts if you detect neon/v8 features in CMake
build-pi5:
	$(call CMAKE_CONFIGURE,$(ARM64_FLAGS) -DPI5=ON)
	$(call CMAKE_BUILD)
	@echo "✅ C++ node built for Pi 5 (arm64) → $(BUILD_DIR)/"

# Jetson (arm64 + CUDA)
build-jetson:
	$(call CMAKE_CONFIGURE,$(ARM64_FLAGS) $(JETSON_FLAGS))
	$(call CMAKE_BUILD)
	@echo "✅ C++ node built for Jetson (arm64 + CUDA) → $(BUILD_DIR)/"

# ---- Docker build context for Compose ----
build-docker:
	@cp -f Dockerfile.docker Dockerfile
	@echo "✅ Dockerfile prepared for Compose builds"

# ---- Cleanup ----
clean:
	@rm -rf $(BUILD_DIR)

distclean: clean
	@rm -f Dockerfile
