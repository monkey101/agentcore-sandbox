import argparse
import json
import operator
import math
import os, subprocess
import random
import string
from bedrock_agentcore.runtime import BedrockAgentCoreApp

ROOT_DIR = "/app" 

app = BedrockAgentCoreApp()

def run_nextflow_lint():
    """Run Nextflow lint on payload.nf file"""
    file_path = ROOT_DIR + "/payload.nf"
    cmd = ["nextflow", "lint", file_path]

    try:
        p = subprocess.run(cmd, capture_output=True, text=True, check=True)
        output = p.stdout + "\n" + p.stderr
        print(output)
        return output
    except subprocess.CalledProcessError as e:
        error_output = f"Lint failed with exit code {e.returncode}\n"
        error_output += f"STDOUT: {e.stdout}\n"
        error_output += f"STDERR: {e.stderr}"
        print(error_output)
        return error_output

def write_nextflow_file(file_content):
    """Write content to payload.nf file, overwriting any existing content"""
    file_path = ROOT_DIR + "/payload.nf"
    with open(file_path, 'w') as f:
        f.write(file_content)
    return f"Successfully wrote {len(file_content)} characters to {file_path}"


@app.entrypoint
def invoke(payload):
    """
    Invoke the agent with a payload
    """
    cmd = payload.get("cmd")
    if (cmd == "write_file"):
        file_content = payload.get("file_content")
        output = write_nextflow_file(file_content)
    elif (cmd == "run_nextflow_lint"):
        output = run_nextflow_lint()
    else:
        output = "Unknown command"

    print(f"Output: {output}")
    return {"output": output}


if __name__ == "__main__":
    if (False):  # Change to False to run as a Bedrock app
        ROOT_DIR = "."
        parser = argparse.ArgumentParser()
        parser.add_argument("payload", type=str)
        args = parser.parse_args()
        response = invoke(json.loads(args.payload))
        print(response)
    else:
        app.run()

