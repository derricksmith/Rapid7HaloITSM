FROM rapid7/insightconnect-python-3-slim-plugin:5

LABEL organization=derricksmith
LABEL sdk=python

WORKDIR /python/src

# Copy only what's needed for dependencies first (layer caching)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache /tmp/*

# Copy spec file
COPY plugin.spec.yaml /plugin.spec.yaml

# Copy only necessary source files (no tests, builds, or cache)
COPY bin ./bin
COPY icon_haloitsm ./icon_haloitsm
COPY setup.py ./
COPY help.md CONFIGURATION.md ./

# Build and install, then clean up in same layer to reduce size
RUN python setup.py build && \
    python setup.py install && \
    rm -rf /python/src/build /root/.cache /tmp/* /var/tmp/* && \
    find /python/src -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true && \
    find /python/src -type f -name "*.pyc" -delete && \
    find /python/src -type f -name "*.pyo" -delete

# User to run plugin code
USER nobody

ENTRYPOINT ["python", "/python/src/bin/icon_haloitsm"]
