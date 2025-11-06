# Production Makefile for HaloITSM Plugin
# Usage: make [target]

.PHONY: help install clean test validate build image export deploy-test deploy-prod

# Default target
help: ## Show this help message
	@echo "HaloITSM Plugin - Production Build System"
	@echo "==========================================="
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Environment Variables:"
	@echo "  PLUGIN_VERSION    - Plugin version (default: auto-detected from git)"
	@echo "  BUILD_NUMBER      - CI build number (optional)"
	@echo "  REGISTRY          - Docker registry for image (optional)"

# Variables
PLUGIN_NAME := haloitsm
PLUGIN_DIR := plugins/$(PLUGIN_NAME)
VERSION := $(shell git describe --tags --always --dirty 2>/dev/null || echo "dev")
BUILD_NUMBER ?= local
IMAGE_NAME := rapid7-$(PLUGIN_NAME)
REGISTRY ?= 

# Build info
BUILD_DATE := $(shell date -u +'%Y-%m-%dT%H:%M:%SZ')
GIT_COMMIT := $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")
BUILD_USER := $(shell whoami)

install: ## Install plugin dependencies
	@echo "Installing plugin dependencies..."
	cd $(PLUGIN_DIR) && pip install -r requirements.txt
	@echo "Installing development dependencies..."
	pip install insightconnect-plugin-runtime pytest pytest-cov black flake8

clean: ## Clean build artifacts
	@echo "Cleaning build artifacts..."
	cd $(PLUGIN_DIR) && rm -rf build/ dist/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	docker rmi $(IMAGE_NAME):$(VERSION) 2>/dev/null || true
	docker rmi $(IMAGE_NAME):latest 2>/dev/null || true

lint: ## Run code linting
	@echo "Running code linting..."
	cd $(PLUGIN_DIR) && black --check --line-length 100 komand_$(PLUGIN_NAME)/
	cd $(PLUGIN_DIR) && flake8 --max-line-length=100 --ignore=E203,W503 komand_$(PLUGIN_NAME)/

format: ## Format code with black
	@echo "Formatting code..."
	cd $(PLUGIN_DIR) && black --line-length 100 komand_$(PLUGIN_NAME)/

test: ## Run unit tests
	@echo "Running unit tests..."
	cd $(PLUGIN_DIR) && python -m pytest tests/ -v --tb=short
	@echo "Tests completed successfully!"

test-coverage: ## Run tests with coverage report
	@echo "Running tests with coverage..."
	cd $(PLUGIN_DIR) && python -m pytest tests/ -v --cov=komand_$(PLUGIN_NAME) --cov-report=html --cov-report=term

validate: ## Validate plugin specification
	@echo "Validating plugin specification..."
	cd $(PLUGIN_DIR) && insight-plugin validate
	@echo "Plugin validation successful!"

security-scan: ## Run security scanning
	@echo "Running security scan..."
	cd $(PLUGIN_DIR) && pip install bandit safety
	cd $(PLUGIN_DIR) && bandit -r komand_$(PLUGIN_NAME)/ -f json -o security-report.json || true
	cd $(PLUGIN_DIR) && safety check --json --output safety-report.json || true
	@echo "Security scan completed. Check reports for issues."

build: clean lint test validate ## Build plugin (clean, lint, test, validate)
	@echo "Building plugin $(PLUGIN_NAME) version $(VERSION)..."
	@echo "Build Date: $(BUILD_DATE)"
	@echo "Git Commit: $(GIT_COMMIT)"
	@echo "Build User: $(BUILD_USER)"
	@echo "Build completed successfully!"

image: ## Build Docker image
	@echo "Building Docker image..."
	cd $(PLUGIN_DIR) && docker build \
		--build-arg BUILD_DATE="$(BUILD_DATE)" \
		--build-arg VERSION="$(VERSION)" \
		--build-arg GIT_COMMIT="$(GIT_COMMIT)" \
		-t $(IMAGE_NAME):$(VERSION) \
		-t $(IMAGE_NAME):latest \
		.
	@echo "Docker image built: $(IMAGE_NAME):$(VERSION)"

export: build ## Export plugin as .plg file
	@echo "Exporting plugin to .plg file..."
	cd $(PLUGIN_DIR) && insight-plugin export
	@ls -la $(PLUGIN_DIR)/*.plg
	@echo "Plugin exported successfully!"

package: export ## Create release package with documentation
	@echo "Creating release package..."
	mkdir -p dist/$(PLUGIN_NAME)-$(VERSION)
	cp $(PLUGIN_DIR)/*.plg dist/$(PLUGIN_NAME)-$(VERSION)/
	cp README.md dist/$(PLUGIN_NAME)-$(VERSION)/
	cp CONFIGURATION.md dist/$(PLUGIN_NAME)-$(VERSION)/
	cp PRODUCTION.md dist/$(PLUGIN_NAME)-$(VERSION)/
	cp ProjectDescription.md dist/$(PLUGIN_NAME)-$(VERSION)/
	cd dist && tar -czf $(PLUGIN_NAME)-$(VERSION).tar.gz $(PLUGIN_NAME)-$(VERSION)/
	@echo "Release package created: dist/$(PLUGIN_NAME)-$(VERSION).tar.gz"

# Testing targets
test-integration: ## Run integration tests (requires environment variables)
	@echo "Running integration tests..."
	@echo "Checking required environment variables..."
	@test -n "$(HALO_CLIENT_ID)" || (echo "HALO_CLIENT_ID not set" && exit 1)
	@test -n "$(HALO_CLIENT_SECRET)" || (echo "HALO_CLIENT_SECRET not set" && exit 1)
	@test -n "$(HALO_AUTH_SERVER)" || (echo "HALO_AUTH_SERVER not set" && exit 1)
	@test -n "$(HALO_RESOURCE_SERVER)" || (echo "HALO_RESOURCE_SERVER not set" && exit 1)
	cd $(PLUGIN_DIR) && python -m pytest tests/test_integration.py -v --tb=short

test-smoke: ## Run smoke tests against production
	@echo "Running smoke tests..."
	cd $(PLUGIN_DIR) && python tests/smoke_test.py

# Deployment targets
deploy-staging: package ## Deploy to staging environment
	@echo "Deploying to staging environment..."
	@echo "This would typically involve:"
	@echo "1. Uploading package to staging InsightConnect"
	@echo "2. Running automated tests"
	@echo "3. Notifying team of deployment"
	@echo "Manual step: Upload dist/$(PLUGIN_NAME)-$(VERSION).tar.gz to staging"

deploy-prod: package ## Deploy to production environment
	@echo "Deploying to production environment..."
	@echo "This would typically involve:"
	@echo "1. Final validation checks"
	@echo "2. Uploading to production InsightConnect"
	@echo "3. Monitoring deployment"
	@echo "4. Notifying stakeholders"
	@echo "Manual step: Upload dist/$(PLUGIN_NAME)-$(VERSION).tar.gz to production"

# Quality gates
quality-gate: lint test validate security-scan ## Run all quality gates
	@echo "All quality gates passed!"

# CI/CD helpers
ci-build: ## CI build target
	@echo "CI Build $(BUILD_NUMBER) - $(VERSION)"
	make quality-gate
	make image
	make export
	make package

version: ## Show version information
	@echo "Plugin: $(PLUGIN_NAME)"
	@echo "Version: $(VERSION)"
	@echo "Build Date: $(BUILD_DATE)"
	@echo "Git Commit: $(GIT_COMMIT)"
	@echo "Build User: $(BUILD_USER)"
	@echo "Build Number: $(BUILD_NUMBER)"

# Development helpers
dev-setup: install ## Set up development environment
	@echo "Setting up development environment..."
	cd $(PLUGIN_DIR) && pre-commit install 2>/dev/null || echo "pre-commit not available"
	@echo "Development environment ready!"

dev-test: ## Quick development test cycle
	@echo "Running development test cycle..."
	make lint
	make test
	make validate
	@echo "Development test cycle completed!"

# Monitoring and health
health-check: ## Check plugin health in production
	@echo "Checking plugin health..."
	@echo "This would typically check:"
	@echo "1. Plugin status in InsightConnect"
	@echo "2. Recent execution statistics"
	@echo "3. Error rates and performance metrics"
	@echo "4. API connectivity to HaloITSM"

# Documentation
docs: ## Generate documentation
	@echo "Generating documentation..."
	cd $(PLUGIN_DIR) && python -c "\
import json; \
import yaml; \
with open('plugin.spec.yaml', 'r') as f: \
    spec = yaml.safe_load(f); \
print('# Plugin Documentation'); \
print(f'## {spec[\"name\"]} v{spec[\"version\"]}'); \
print(f'{spec[\"description\"]}');"
	@echo "Documentation generated!"

# Release management
release: ## Create a new release
	@echo "Creating release $(VERSION)..."
	git tag -a v$(VERSION) -m "Release version $(VERSION)"
	make package
	@echo "Release v$(VERSION) created!"
	@echo "Next steps:"
	@echo "1. git push origin v$(VERSION)"
	@echo "2. Upload dist/$(PLUGIN_NAME)-$(VERSION).tar.gz to releases"
	@echo "3. Update release notes"

# Default target when no target is specified
.DEFAULT_GOAL := help