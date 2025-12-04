# Makefile for HaloITSM Plugin
# Based on official Rapid7 plugin build process from github.com/rapid7/insightconnect-plugins

YELLOW := "\033[0;33m"
NORMAL := "\033[0m"

# Plugin metadata (must match plugin.spec.yaml)
VENDOR := derricksmith
NAME := haloitsm
VERSION := 2.1.0

.PHONY: default image export test validate clean install lint

default: image

# Build Docker image
image:
	$(info [$(YELLOW)*$(NORMAL)] Building Docker image)
	@printf "\n ---> Building Docker image $(VENDOR)/$(NAME):$(VERSION)\n"
	sudo docker build --no-cache -t $(VENDOR)/$(NAME):$(VERSION) .
	@printf "\n ---> Image built successfully\n"

# Export plugin as .tar file (InsightConnect format)
export: image
	$(info [$(YELLOW)*$(NORMAL)] Exporting docker image)
	@printf "\n ---> Exporting Docker image to ./$(VENDOR)_$(NAME)_$(VERSION).tar\n"
	@sudo docker save $(VENDOR)/$(NAME):$(VERSION) | gzip > $(VENDOR)_$(NAME)_$(VERSION).tar
	@ls -lh $(VENDOR)_$(NAME)_$(VERSION).tar
	@printf "\n ---> ✅ Plugin exported successfully!\n"
	@printf "\n ---> 📦 Upload this file to InsightConnect: $(VENDOR)_$(NAME)_$(VERSION).tar\n"

# Run tests
test:
	$(info [$(YELLOW)*$(NORMAL)] Running tests)
	python -m pytest tests/ -v

# Validate plugin spec
validate:
	$(info [$(YELLOW)*$(NORMAL)] Validating plugin spec)
	@python -c "import yaml; yaml.safe_load(open('plugin.spec.yaml'))" && echo "✓ plugin.spec.yaml is valid YAML"

# Clean up
clean:
	$(info [$(YELLOW)*$(NORMAL)] Cleaning up)
	@docker rmi $(VENDOR)/$(NAME):$(VERSION) 2>/dev/null || true
	@rm -f $(VENDOR)_$(NAME)_$(VERSION).tar *.plg
	@printf "\n ---> Cleanup complete\n"

# Install dependencies
install:
	$(info [$(YELLOW)*$(NORMAL)] Installing dependencies)
	pip install -r requirements.txt

# Run linting
lint:
	$(info [$(YELLOW)*$(NORMAL)] Running linter)
	flake8 icon_haloitsm/