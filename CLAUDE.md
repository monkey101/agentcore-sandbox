# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Bedrock AgentCore runtime environment that provides Nextflow file management and linting capabilities. The agent runs as a containerized service on AWS and can be invoked via the AgentCore SDK to write Nextflow workflow files and run lint checks.

## Architecture

### Core Components

- **agent.py**: Main entrypoint that defines the Bedrock AgentCore application with command-based routing
  - `invoke()` function: Decorated with `@app.entrypoint`, handles incoming payloads with command routing
  - `write_nextflow_file()`: Writes Nextflow content to `payload.nf`
  - `run_nextflow_lint()`: Executes Nextflow lint on `payload.nf`
- **BedrockAgentCoreApp**: The runtime framework that handles HTTP server setup, AWS authentication, and request routing
- **Nextflow Integration**: The agent executes Nextflow lint via subprocess. Nextflow is installed in the Docker container and requires Java runtime.

### Command API

The agent accepts payloads with the following structure:

```json
{
  "cmd": "write_file" | "run_nextflow_lint",
  "file_content": "..." // Required for write_file command
}
```

**Available Commands:**
- `write_file`: Writes the provided `file_content` to `/app/payload.nf`, overwriting any existing content
- `run_nextflow_lint`: Runs `nextflow lint` on `/app/payload.nf` and returns results

### Execution Flow

1. Agent receives payload via AgentCore invoke
2. `invoke()` function extracts the `cmd` parameter
3. Routes to appropriate handler:
   - `write_file` → `write_nextflow_file(file_content)`
   - `run_nextflow_lint` → `run_nextflow_lint()`
4. Response with output is returned to caller

### Container Architecture

The application runs in a Docker container built on `ghcr.io/astral-sh/uv:python3.14-bookworm-slim` with:
- Java 17 JRE (required for Nextflow)
- Nextflow installed to `/usr/local/bin/`
- UV package manager for Python dependencies
- Non-root user (bedrock_agentcore, UID 1000) with write permissions to `/app`
- AWS OpenTelemetry instrumentation for observability

**Important Docker Build Order:**
The Dockerfile copies files BEFORE switching to the non-root user, then runs `chown` to transfer ownership. This ensures the `bedrock_agentcore` user can write to `/app/payload.nf`.

## Development Commands

### Local Development

```bash
# Install dependencies (using virtual environment)
source myvenv/bin/activate
pip install -r requirements.txt

# Run locally for testing using LOCAL_MODE environment variable
LOCAL_MODE=1 python agent.py '{"cmd": "write_file", "file_content": "test"}'
LOCAL_MODE=1 python agent.py '{"cmd": "run_nextflow_lint"}'

# Or export the variable
export LOCAL_MODE=1
python agent.py '{"cmd": "write_file", "file_content": "process test { script: \"echo test\" }"}'
```

**Note:** When `LOCAL_MODE=1` is set, the agent:
- Uses `ROOT_DIR="."` instead of `ROOT_DIR="/app"`
- Accepts JSON payload via command line argument
- Prints response to stdout instead of running as HTTP server

### Testing with Test Harness

The project includes `test_agent.py` for invoking the deployed agent:

```bash
# Write a Nextflow file
python test_agent.py --write "process sayHello { script: 'echo Hello' }"

# Write and lint
python test_agent.py --write "process test { script: 'echo test' }" --lint

# Write from file
python test_agent.py --write-file example.nf --lint

# Just run lint (on existing payload.nf)
python test_agent.py --lint

# Use custom session ID (must be 33+ characters)
python test_agent.py --write "test" --session-id "my-custom-session-id-that-is-long-enough"
```

### AgentCore Operations

```bash
# Note: agentcore CLI requires installation via pip
# The bedrock-agentcore package provides the SDK but not the CLI tool

# Deploy using AWS CodeBuild (configured in .bedrock_agentcore.yaml)
# The agent is deployed to ECR and invoked via boto3
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

**Core agent dependencies:**
- **bedrock-agentcore**: Core runtime framework (pinned to <=0.1.5)
- **aws-opentelemetry-distro**: OpenTelemetry instrumentation (required by Dockerfile CMD)

**Test harness dependencies:**
- **boto3**: AWS SDK for Python (used by test_agent.py)
- **botocore**: AWS SDK core functionality

### System Dependencies

- Java 17 JRE (openjdk-17-jre-headless)
- Nextflow (installed via curl from get.nextflow.io)
- curl

## Important Notes

### File Paths and Local Mode

The agent uses the `LOCAL_MODE` environment variable to determine the root directory:
- **Production mode** (default, `LOCAL_MODE` not set): `ROOT_DIR = "/app"`
- **Local mode** (`LOCAL_MODE=1`): `ROOT_DIR = "."`

All file operations target `{ROOT_DIR}/payload.nf`. Set `LOCAL_MODE=1` when running the agent locally for testing.

### AWS Authentication

The agent uses the IAM execution role defined in `.bedrock_agentcore.yaml`. No credentials should be committed to the repository.

### Test Harness

`test_agent.py` uses the boto3 `bedrock-agentcore` client to invoke the agent:
- Client: `boto3.client('bedrock-agentcore')`
- Method: `invoke_agent_runtime()`
- Session IDs must be 33+ characters
- Returns JSON response with output

### Ports

- Port 8080: Main application server
- Port 8000: Secondary port (exposed but usage not defined in current code)

### Module Execution

The container CMD uses `opentelemetry-instrument python -m agent` which runs agent.py as a module with automatic OpenTelemetry instrumentation.

### Git Configuration

The `.gitignore` has been configured to ignore:
- Python artifacts (`__pycache__`, `*.pyc`)
- Virtual environments (`.venv/`, `myvenv/`)
- Nextflow working directories (`.nextflow/`, `work/`)
- Temporary files (`*.txt`, `*.log`, `*.tmp`)

Source files like `agent.py`, `Dockerfile`, and configuration files are tracked.
