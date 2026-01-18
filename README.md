# Bedrock AgentCore - Nextflow Linting Agent

A Bedrock AgentCore runtime environment that provides Nextflow file management and linting capabilities. This agent runs as a containerized service on AWS and can be invoked to write Nextflow workflow files and run lint checks.

## Overview

This agent provides two main capabilities:
1. **Write Nextflow Files**: Accept Nextflow workflow content and write it to a file
2. **Lint Nextflow Files**: Run Nextflow's lint command to validate workflow syntax

## Prerequisites

* AWS CLI version 2.0 or later
* Python 3.10 or later
* Docker (for local container testing)
* AWS credentials configured with appropriate permissions
* Java 17+ (for local Nextflow testing)

## Project Structure

```
.
├── agent.py                    # Main agent entrypoint with command routing
├── test_agent.py              # Test harness for invoking deployed agent
├── Dockerfile                 # Container definition with Nextflow and Java
├── requirements.txt           # Python dependencies
├── .bedrock_agentcore.yaml    # Agent configuration and AWS settings
├── CLAUDE.md                  # Detailed technical documentation
└── README.md                  # This file
```

## Quick Start

### 1. Install Dependencies

```bash
# Create and activate virtual environment
python -m venv myvenv
source myvenv/bin/activate  # On Windows: myvenv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Deploy to AWS

The agent is deployed via AWS CodeBuild and ECR (configuration in `.bedrock_agentcore.yaml`):

```bash
# Deploy using agentcore CLI (if available)
agentcore configure -e agent.py
agentcore launch
```

### 3. Test the Agent

Use the included test harness to invoke the deployed agent:

```bash
# Write a Nextflow file
python test_agent.py --write "process sayHello { script: 'echo Hello World' }"

# Write and immediately lint
python test_agent.py --write "process test { script: 'echo test' }" --lint

# Write content from a file
python test_agent.py --write-file my-workflow.nf --lint

# Just run lint on existing file
python test_agent.py --lint

# Use a custom session ID (must be 33+ characters)
python test_agent.py --write "test" --session-id "my-custom-session-id-that-is-long-enough"
```

## Agent API

The agent accepts JSON payloads with the following structure:

### Write File Command

```json
{
  "cmd": "write_file",
  "file_content": "process myProcess {\n  script:\n  'echo Hello'\n}"
}
```

**Response:**
```json
{
  "output": "Successfully wrote 45 characters to /app/payload.nf"
}
```

### Lint Command

```json
{
  "cmd": "run_nextflow_lint"
}
```

**Response:**
```json
{
  "output": "Nextflow lint output...\n"
}
```

## Direct Invocation with boto3

You can invoke the agent programmatically:

```python
import boto3
import json

client = boto3.client('bedrock-agentcore', region_name='us-west-2')

payload = json.dumps({
    "cmd": "write_file",
    "file_content": "process test { script: 'echo test' }"
})

response = client.invoke_agent_runtime(
    agentRuntimeArn='arn:aws:bedrock-agentcore:us-west-2:468199119368:runtime/agent-QM6HsbF0sK',
    runtimeSessionId='my-session-id-at-least-33-characters-long',
    payload=payload,
    qualifier="DEFAULT"
)

result = json.loads(response['response'].read())
print(result)
```

## Local Development

To run the agent locally, use the `LOCAL_MODE` environment variable:

```bash
# Run in local mode (uses ROOT_DIR=".")
LOCAL_MODE=1 python agent.py '{"cmd": "write_file", "file_content": "process test { script: \"echo test\" }"}'

# Or export it first
export LOCAL_MODE=1
python agent.py '{"cmd": "write_file", "file_content": "test content"}'
python agent.py '{"cmd": "run_nextflow_lint"}'
```

When `LOCAL_MODE=1`:
- `ROOT_DIR` is set to `"."` (current directory)
- Agent accepts JSON payload via command line argument
- Output is printed to stdout

## Docker

Build and run the container locally:

```bash
# Build
docker build -t nextflow-agent .

# Run
docker run -p 8080:8080 -e AWS_REGION=us-west-2 nextflow-agent
```

## Configuration

Agent configuration is stored in `.bedrock_agentcore.yaml`:
- **Agent ID**: `agent-QM6HsbF0sK`
- **Region**: `us-west-2`
- **Account**: `468199119368`
- **ECR Repository**: `468199119368.dkr.ecr.us-west-2.amazonaws.com/bedrock-agentcore-agent`
- **Execution Role**: `AmazonBedrockAgentCoreSDKRuntime-us-west-2-d4f0bc5a29`

## Troubleshooting


### Session ID Errors

Session IDs must be at least 33 characters long. The test harness auto-generates valid session IDs if not provided.

### agentcore CLI Not Found

The `bedrock-agentcore` Python package provides the SDK but not the CLI tool. You may need to install the CLI separately or use boto3 directly.

## Documentation

See [CLAUDE.md](CLAUDE.md) for detailed technical documentation including:
- Architecture overview
- Command execution flow
- Container architecture
- Development guidelines
- Dependency information

## License

[Add your license here]
