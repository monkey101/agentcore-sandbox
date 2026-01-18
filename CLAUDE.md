# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Bedrock AgentCore runtime environment that integrates Nextflow for workflow execution. The agent runs as a containerized service on AWS and can be invoked via the AgentCore SDK.

## Architecture

### Core Components

- **agent.py**: Main entrypoint that defines the Bedrock AgentCore application. The `langgraph_bedrock` function is decorated with `@app.entrypoint` and serves as the primary handler for agent invocations.
- **BedrockAgentCoreApp**: The runtime framework that handles HTTP server setup, AWS authentication, and request routing. Initialized at module level (`app = BedrockAgentCoreApp()`).
- **Nextflow Integration**: The agent executes Nextflow commands via subprocess. Nextflow is installed in the Docker container and requires Java runtime.

### Execution Flow

1. Agent receives payload via AgentCore invoke
2. `langgraph_bedrock` function executes
3. Calls `run_nextflow()` which:
   - Creates a random test file to demonstrate filesystem state preservation
   - Executes the `nextflow` command
   - Returns stdout/stderr output
4. Response is returned to the caller

### Container Architecture

The application runs in a Docker container built on `ghcr.io/astral-sh/uv:python3.14-bookworm-slim` with:
- Java 17 JRE (required for Nextflow)
- Nextflow installed to `/usr/local/bin/`
- UV package manager for Python dependencies
- Non-root user (bedrock_agentcore, UID 1000)
- AWS OpenTelemetry instrumentation for observability

## Development Commands

### Local Development

```bash
# Install dependencies
uv pip install -r requirements.txt

# Run locally (requires AWS credentials)
python agent.py
```

### AgentCore Operations

```bash
# Configure the agent (accept all defaults)
agentcore configure -e agent.py

# Launch the agent to AWS
agentcore launch

# Invoke the agent
agentcore invoke '{"prompt": "Hello"}'
```

### Docker Operations

```bash
# Build container
docker build -t agent .

# Run container locally
docker run -p 8080:8080 agent
```

## Configuration

### .bedrock_agentcore.yaml

This file contains the complete agent configuration including:
- AWS account and region settings
- ECR repository location
- IAM execution role
- Network configuration (PUBLIC mode, HTTP protocol)
- Agent ID and ARN for deployed instance
- Observability settings (enabled by default)

Key configuration values are set for account 468199119368 in us-west-2 region.

### Environment Variables

The Dockerfile sets:
- `AWS_REGION=us-west-2`
- `AWS_DEFAULT_REGION=us-west-2`
- `DOCKER_CONTAINER=1` (signals container environment)
- `UV_SYSTEM_PYTHON=1` (UV configuration)
- `UV_COMPILE_BYTECODE=1` (UV configuration)

## Dependencies

### Python Packages (requirements.txt)

- **bedrock-agentcore**: Core runtime framework (pinned to <=0.1.5)
- **bedrock-agentcore-starter-toolkit**: Utilities and templates (pinned to 0.1.14)
- **langchain[aws]**: LangChain with AWS integrations
- **langgraph**: Graph-based agent orchestration
- **langsmith[otel]**: Observability and tracing
- **opentelemetry-instrumentation-langchain**: LangChain telemetry

### System Dependencies

- Java 17 JRE (openjdk-17-jre-headless)
- Nextflow (installed via curl from get.nextflow.io)
- curl

## Important Notes

### Filesystem State

The agent creates random test files on each invocation to verify filesystem state is preserved between runs. This is part of testing the runtime environment's persistence behavior.

### AWS Authentication

The agent uses the IAM execution role defined in `.bedrock_agentcore.yaml`. No credentials should be committed to the repository.

### Ports

- Port 8080: Main application server
- Port 8000: Secondary port (exposed but usage not defined in current code)

### Module Execution

The container CMD uses `opentelemetry-instrument python -m agent` which runs agent.py as a module with automatic OpenTelemetry instrumentation.
