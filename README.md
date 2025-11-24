# Pre-reqs
* AWS CLI version 2.0 or later
* Python 3.10 or later
* Permission to use haiku on bedrock

# Deploy AgentCore and the agent
```
agentcore configure -e agent.py (accept all defaults)
agentcore launch
agentcore invoke '{"prompt": "Hello"}'}
```
