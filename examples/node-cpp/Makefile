build-pi:
	cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
	cmake --build build -j

build-amd64: build-pi

build-docker:
	cp Dockerfile.docker Dockerfile
