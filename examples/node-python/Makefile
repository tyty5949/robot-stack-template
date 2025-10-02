build-pi:
	python3 -m venv venv && ./venv/bin/pip install -U pip -r requirements.txt
build-amd64: build-pi
build-docker:
	cp Dockerfile.docker Dockerfile
