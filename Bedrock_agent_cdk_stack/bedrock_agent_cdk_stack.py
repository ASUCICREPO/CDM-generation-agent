from aws_cdk import (
    CfnOutput,
    Stack,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_s3 as s3,
    aws_s3_notifications as s3_notifications,
    aws_bedrock as bedrock,
    Duration
)
from constructs import Construct

class BedrockAgentStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define the custom policies
        foundation_model_policy = iam.PolicyDocument(
            statements=[
                iam.PolicyStatement(
                    sid="AmazonBedrockAgentBedrockFoundationModelPolicyProd",
                    effect=iam.Effect.ALLOW,
                    actions=["bedrock:InvokeModel"],
                    resources=[
                        "arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-3-opus-20240229-v1:0"
                    ]
                )
            ]
        )

        # Define the IAM role for the Bedrock Agent
        agent_role = iam.Role(self, "BedrockAgentRole",
            role_name="AmazonBedrockExecutionRoleForAgents_agent_test",
            assumed_by=iam.ServicePrincipal("bedrock.amazonaws.com"),
            inline_policies={
                "FoundationModelPolicy": foundation_model_policy
            }
        )

        # Define the IAM role for the Lambda function
        lambda_role = iam.Role(self, "BedrockAgentLambdaFunctionRole",
            role_name="BedrockAgentLambdaFunctionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            inline_policies={
                "LambdaLoggingPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents"
                            ],
                            resources=["*"]
                        )
                    ]
                )
            }
        )

        # Create the Lambda function for the action group
        action_group_function = _lambda.Function(self, "ActionGroupFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="action_group.lambda_handler",
            code=_lambda.Code.from_asset("lambda"),
            role=lambda_role,
            timeout=Duration.minutes(1)
        )

        # Add a resource policy to the Lambda function to allow Bedrock service to invoke it
        action_group_function.add_permission("AllowBedrockInvoke",
            principal=iam.ServicePrincipal("bedrock.amazonaws.com"),
            action="lambda:InvokeFunction"
        )

        # Define the Bedrock Agent with one action group containing four functions
        bedrock_agent = bedrock.CfnAgent(self, "BedrockAgent",
            agent_name="CDM-Genaration-Agent",
            agent_resource_role_arn=agent_role.role_arn,
            foundation_model="anthropic.claude-3-opus-20240229-v1:0",
            action_groups=[
                bedrock.CfnAgent.AgentActionGroupProperty(
                    action_group_name="MyActionGroup",
                    action_group_executor=bedrock.CfnAgent.ActionGroupExecutorProperty(
                        lambda_=action_group_function.function_arn
                    ),
                    description="Contains multiple functions with CDM json generation rules for these clauses: Base Currency, Eligible Currency, Rounding, Minimum Transfer Amount, Threshold.",
                    function_schema=bedrock.CfnAgent.FunctionSchemaProperty(
                        functions=[
                            bedrock.CfnAgent.FunctionProperty(
                                name="Currency_clause",
                                description="Rules for CDM json generation for Base Currency and Eligible Currency are present here. Contains details of Base Currency and Eligible Currency clauses' variants and their Common Domain Model (CDM) JSON representations."
                            ),
                            bedrock.CfnAgent.FunctionProperty(
                                name="Rounding_clause",
                                description="Rules for CDM json generation for rounding clause are present here. Contains details of the Rounding clause variants and their Common Domain Model (CDM) JSON representations."
                            ),
                            bedrock.CfnAgent.FunctionProperty(
                                name="Minimum_Transfer_Amount_clause",
                                description="Rules for CDM json generation for Minimum Transfer Amount clause are present here. Contains details of the Minimum Transfer Amount clause variants and their Common Domain Model (CDM) JSON representations."
                            ),
                            bedrock.CfnAgent.FunctionProperty(
                                name="Threshold_clause",
                                description="Rules for CDM json generation for Threshold  clause are present here. Contains details of the Threshold clause variants and their Common Domain Model (CDM) JSON representations."
                            )
                        ]
                    )
                )
            ],
            auto_prepare=False,
            description="Clause CDM processing agent",
            instruction="You are an agent who reads through the ISDA master agreements. When asked about clause names, you will identify the clauses, classify them, and generate their individual Common Domain Model (CDM) JSON outputs. Always follow the CDM JSON generation rules provided in the action group functions.",
            idle_session_ttl_in_seconds=600,
            skip_resource_in_use_check_on_delete=False
        )

        cfn_agent_alias = bedrock.CfnAgentAlias(self, "MyCfnAgentAlias",
            agent_alias_name="agentAlias",
            agent_id=bedrock_agent.attr_agent_id,
            description="This is the alias for CDM-Generation-Agent",
        )

        # Create the S3 bucket to store the PDFs
        pdf_bucket = s3.Bucket(self, "ma-pdf-input-bucket")

        # Create the output S3 bucket
        output_bucket = s3.Bucket(self, "cdm-output-bucket")

        # Define the IAM role for the S3-triggered Lambda function
        s3_trigger_lambda_role = iam.Role(self, "S3TriggerLambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchLogsFullAccess")
            ],
            inline_policies={
                "InvokeBedrockAgentPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=["bedrock:InvokeAgent"],
                            resources=["*"],
                            effect=iam.Effect.ALLOW
                        )
                    ]
                )
            }
        )

        # Create the Lambda layer
        layer = _lambda.LayerVersion(self, "MyLayer",
            code=_lambda.Code.from_asset("lambda_layer/my_layer.zip"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_12]
        )

        # Define the S3-triggered Lambda function
        trigger_function = _lambda.Function(self, "TriggerFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="trigger_handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda"),
            role=s3_trigger_lambda_role,
            environment={
                'PDF_BUCKET': pdf_bucket.bucket_name,
                'AGENT_ID': bedrock_agent.ref,  # Use the logical ID of the agent
                'AGENT_ALIAS_ID': cfn_agent_alias.attr_agent_alias_id,  # Use the actual agent alias ID
                'OUTPUT_BUCKET': output_bucket.bucket_name
            },
            timeout=Duration.minutes(5),
            memory_size=1024,
            layers=[layer]
        )

        # Add the S3 event notification to trigger the Lambda function upon PDF upload
        pdf_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3_notifications.LambdaDestination(trigger_function),
            s3.NotificationKeyFilter(suffix=".pdf")
        )

        # Grant the Lambda function permissions to write to the output S3 bucket
        output_bucket.grant_write(trigger_function)

        # Output the function ARN and S3 bucket names for reference
        CfnOutput(self, "TriggerFunctionArn",
            value=trigger_function.function_arn
        )
        CfnOutput(self, "PdfBucketName",
            value=pdf_bucket.bucket_name
        )
        CfnOutput(self, "OutputBucketName",
            value=output_bucket.bucket_name
        )
        CfnOutput(self, "BedrockAgentArn",
            value=bedrock_agent.attr_agent_arn
        )
        CfnOutput(self, "BedrockAgentAliasArn",
            value=cfn_agent_alias.attr_agent_alias_arn
        )
