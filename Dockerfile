FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim
WORKDIR /app

# Install Java (required for Nextflow) and other system dependencies
RUN apt-get update && apt-get install -y \
    openjdk-17-jre-headless \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Nextflow
RUN curl -s https://get.nextflow.io | bash && \
    mv nextflow /usr/local/bin/ && \
    chmod +x /usr/local/bin/nextflow

# Configure UV for container environment
ENV UV_SYSTEM_PYTHON=1 UV_COMPILE_BYTECODE=1



COPY requirements.txt requirements.txt
# Install from requirements file
RUN uv pip install -r requirements.txt




RUN uv pip install aws-opentelemetry-distro>=0.10.1


# Set AWS region environment variable

ENV AWS_REGION=us-west-2
ENV AWS_DEFAULT_REGION=us-west-2


# Signal that this is running in Docker for host binding logic
ENV DOCKER_CONTAINER=1

# Copy entire project (respecting .dockerignore)
COPY . .

# Create non-root user and make /app writable
RUN useradd -m -u 1000 bedrock_agentcore \
 && chown -R bedrock_agentcore:bedrock_agentcore /app
USER bedrock_agentcore

EXPOSE 8080
EXPOSE 8000

# Use the full module path

CMD ["opentelemetry-instrument", "python", "-m", "agent"]
