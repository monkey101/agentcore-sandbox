#!/usr/bin/env python3
"""
Test harness for invoking the Bedrock AgentCore agent via boto3
"""
import argparse
import json
import boto3


# Agent configuration (from .bedrock_agentcore.yaml)
AGENT_ARN = "arn:aws:bedrock-agentcore:us-west-2:468199119368:runtime/agent-QM6HsbF0sK"
REGION = "us-west-2"


def invoke_agent(cmd, file_content=None, session_id=None):
    """
    Invoke the Bedrock AgentCore agent using boto3 client

    Args:
        cmd: Command to execute ('write_file' or 'run_nextflow_lint')
        file_content: Content to write (required for 'write_file' command)
        session_id: Optional session ID for the agent (must be 33+ characters)

    Returns:
        Response from the agent
    """
    # Build payload
    payload_data = {"cmd": cmd}
    if file_content:
        payload_data["file_content"] = file_content

    # Create boto3 client for bedrock-agentcore
    agent_core_client = boto3.client('bedrock-agentcore', region_name=REGION)

    # Generate a valid session ID if not provided (must be 33+ chars)
    if not session_id:
        import uuid
        session_id = f"test-session-{str(uuid.uuid4())}"  # This will be >33 chars

    print(f"Using session_id: {session_id}")

    payload = json.dumps(payload_data)

    try:
        # Invoke the agent runtime
        response = agent_core_client.invoke_agent_runtime(
            agentRuntimeArn=AGENT_ARN,
            runtimeSessionId=session_id,
            payload=payload,
            qualifier="DEFAULT"
        )

        # Read and parse the response
        response_body = response['response'].read()
        response_data = json.loads(response_body)
        return response_data

    except Exception as e:
        print(f"Error invoking agent: {e}")
        return None


def test_write_file(content, session_id=None):
    """Test writing a Nextflow file"""
    print("Testing write_file command...")
    print(f"Content to write:\n{content}\n")

    response = invoke_agent("write_file", file_content=content, session_id=session_id)
    print(f"Response: {response}\n")
    return response


def test_lint(session_id=None):
    """Test running Nextflow lint"""
    print("Testing run_nextflow_lint command...")

    response = invoke_agent("run_nextflow_lint", session_id=session_id)
    print(f"Response: {response}\n")
    return response


def main():
    parser = argparse.ArgumentParser(
        description="Test harness for Bedrock AgentCore agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Write a file and lint it
  python test_agent.py --write "process sayHello { script: 'echo Hello' }" --lint

  # Just write a file
  python test_agent.py --write "process test { script: 'echo test' }"

  # Read file content and write it
  python test_agent.py --write-file example.nf --lint

  # Just run lint
  python test_agent.py --lint
        """
    )

    parser.add_argument(
        '--write',
        type=str,
        help='Nextflow content to write to payload.nf'
    )

    parser.add_argument(
        '--write-file',
        type=str,
        metavar='FILE',
        help='Read Nextflow content from file and write to payload.nf'
    )

    parser.add_argument(
        '--lint',
        action='store_true',
        help='Run Nextflow lint on payload.nf'
    )

    parser.add_argument(
        '--session-id',
        type=str,
        help='Optional session ID for the agent'
    )

    args = parser.parse_args()

    # Validate arguments
    if not any([args.write, args.write_file, args.lint]):
        parser.error("Must specify at least one of: --write, --write-file, or --lint")

    # Execute commands
    if args.write:
        test_write_file(args.write, session_id=args.session_id)

    elif args.write_file:
        try:
            with open(args.write_file, 'r') as f:
                content = f.read()
            test_write_file(content, session_id=args.session_id)
        except FileNotFoundError:
            print(f"Error: File '{args.write_file}' not found")
            return 1

    if args.lint:
        test_lint(session_id=args.session_id)

    return 0


if __name__ == "__main__":
    exit(main())
