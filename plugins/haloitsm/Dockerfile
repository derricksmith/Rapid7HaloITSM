FROM rapid7/insightconnect-python-3-slim-plugin:5.0.0

# Copy plugin source
WORKDIR /python/src
ADD ./komand_haloitsm /python/src/komand_haloitsm
ADD ./plugin.spec.yaml /plugin.spec.yaml

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set plugin entry point
ENTRYPOINT ["/usr/local/bin/python3", "/python/src/komand_haloitsm/bin/komand_haloitsm"]