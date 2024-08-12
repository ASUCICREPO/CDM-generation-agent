import aws_cdk as cdk
from bedrock_agent_cdk.bedrock_agent_cdk_stack import BedrockAgentStack

app = cdk.App()
BedrockAgentStack(app, "BedrockAgentStack")
app.synth()
