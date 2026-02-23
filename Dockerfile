FROM python:3.11-slim

LABEL maintainer="cc_copt" \
      description="Batch codon optimization CLI using DnaChisel"

# procps is required by Nextflow for process monitoring (ps command)
RUN apt-get update && apt-get install -y --no-install-recommends procps \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install the package and its dependencies
COPY pyproject.toml README.md ./
COPY cc_copt/ cc_copt/

RUN pip install --no-cache-dir .

# Copy examples so they're available inside the container
COPY examples/ examples/
