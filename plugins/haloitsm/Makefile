# Makefile for HaloITSM Plugin

.PHONY: image test validate clean

PLUGIN_NAME = haloitsm
VERSION = 1.0.0

# Build Docker image
image:
	docker build -t rapid7/$(PLUGIN_NAME):$(VERSION) .
	docker tag rapid7/$(PLUGIN_NAME):$(VERSION) rapid7/$(PLUGIN_NAME):latest

# Run tests
test:
	python -m pytest tests/ -v

# Validate plugin spec
validate:
	insight-plugin validate plugin.spec.yaml

# Export plugin
export:
	insight-plugin export plugin.spec.yaml

# Clean up
clean:
	docker rmi rapid7/$(PLUGIN_NAME):$(VERSION) || true
	docker rmi rapid7/$(PLUGIN_NAME):latest || true
	rm -f *.plg

# Install dependencies
install:
	pip install -r requirements.txt

# Run linting
lint:
	flake8 komand_haloitsm/