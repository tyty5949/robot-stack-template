# -------- Config --------
VENV         ?= venv
PYTHON       ?= python3
PIP          := $(VENV)/bin/pip
REQ_DEFAULT  ?= requirements.txt
REQ_JETSON   ?= requirements-jetson.txt

.PHONY: build-pi build-pi5 build-amd64 build-jetson build-docker clean distclean

# ---- Helpers ----
$(VENV)/bin/activate:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install -U pip setuptools wheel

install-reqs:
	@if [ -f "$(REQ_DEFAULT)" ]; then \
		echo "Installing $(REQ_DEFAULT)"; \
		$(PIP) install -r $(REQ_DEFAULT); \
	else \
		echo "No $(REQ_DEFAULT); skipping."; \
	fi

install-reqs-jetson:
	@if [ -f "$(REQ_JETSON)" ]; then \
		echo "Installing $(REQ_JETSON) (Jetson-specific wheels)"; \
		$(PIP) install -r $(REQ_JETSON); \
	else \
		echo "No $(REQ_JETSON) found; falling back to $(REQ_DEFAULT)"; \
		$(PIP) install -r $(REQ_DEFAULT); \
	fi

# ---- Native builds (on device/host) ----
build-pi: $(VENV)/bin/activate install-reqs            ## Raspberry Pi 4/64-bit (arm64) default
	@echo "✅ Python node ready for Pi (venv at $(VENV))"

build-pi5: build-pi                                     ## Raspberry Pi 5 uses same deps by default
	@echo "✅ Python node ready for Pi 5 (venv at $(VENV))"

build-amd64: $(VENV)/bin/activate install-reqs          ## Desktop/dev (x86_64)
	@echo "✅ Python node ready for amd64 (venv at $(VENV))"

build-jetson: $(VENV)/bin/activate install-reqs-jetson  ## Jetson (arm64 + CUDA-friendly wheels)
	@echo "✅ Python node ready for Jetson (venv at $(VENV))"

# ---- Docker build context for Compose ----
build-docker:
	@cp -f Dockerfile.docker Dockerfile
	@echo "✅ Dockerfile prepared for Compose builds"

# ---- Cleanup ----
clean:
	@rm -rf $(VENV)
	@find . -name "__pycache__" -type d -exec rm -rf {} +

distclean: clean
	@rm -f Dockerfile
