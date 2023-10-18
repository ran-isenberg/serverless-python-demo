from aws_cdk import CfnOutput, Duration, RemovalPolicy
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_events as events
from aws_cdk import aws_events_targets as targets
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_stepfunctions as sfn
from aws_cdk import aws_stepfunctions_tasks as tasks
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion
from aws_cdk.aws_logs import LogGroup, RetentionDays
from constructs import Construct

import infrastructure.product.constants as constants


class StreamProcessorTestingConstruct(Construct):

    def __init__(self, scope: Construct, id_: str, lambda_layer: PythonLayerVersion, events: events.EventBus) -> None:
        super().__init__(scope, id_)
        self.id_ = id_
        self.test_results_db = self._build_test_results_db(id_)
        self.lambda_function = self._build_test_lambda(lambda_layer, self.test_results_db)
        self.rule = self._build_event_bridge_rule(events)
        self.state_machine = self._build_state_machine(lambda_func=self.lambda_function, event_bus=events, rule=self.rule)

    def _build_test_results_db(self, id_prefix: str) -> dynamodb.Table:
        table_id = f'{id_prefix}{constants.STREAM_TESTS_TABLE_NAME}'
        table = dynamodb.Table(
            self,
            table_id,
            table_name=table_id,
            partition_key=dynamodb.Attribute(name='id', type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            point_in_time_recovery=True,
            removal_policy=RemovalPolicy.DESTROY,
        )
        CfnOutput(self, id=constants.STREAM_TESTS_TABLE_NAME_OUTPUT,
                  value=table.table_name).override_logical_id(constants.STREAM_TESTS_TABLE_NAME_OUTPUT)
        return table

    def _build_event_bridge_rule(self, event_bus: events.EventBus) -> events.Rule:
        return events.Rule(
            self,
            f'{self.id_}TestRule',
            event_pattern=events.EventPattern(source=[constants.EVENT_SOURCE]),
            enabled=True,
            event_bus=event_bus,
        )

    def _build_state_machine(self, lambda_func: _lambda.Function, event_bus: events.EventBus, rule: events.Rule) -> sfn.StateMachine:
        # Create a role for the Step Function
        step_function_role = iam.Role(
            self,
            f'{self.id_}StepFunctionRole',
            assumed_by=iam.ServicePrincipal('states.amazonaws.com'),
        )

        # Define a task to run the Lambda function
        lambda_task = tasks.LambdaInvoke(
            self,
            f'{self.id_}InvokeTask',
            lambda_function=lambda_func,
            input_path='$.detail',  # Assuming the input to the Lambda is located here, modify accordingly
            result_path='$.lambda_output',
        )

        # Define the state machine
        state_machine = sfn.StateMachine(
            self,
            f'{self.id_}StateMachine',
            definition=lambda_task,  # Set the start state of the state machine to the Lambda task
            role=step_function_role,
            tracing_enabled=True,
            logs=sfn.LogOptions(
                destination=LogGroup(
                    self,
                    f'{self.id_}TestStateMachineLogGroup',
                    removal_policy=RemovalPolicy.DESTROY,
                ),
                level=sfn.LogLevel.ALL,
                include_execution_data=True,
            ),
        )

        # Add the state machine as a target to the EventBridge rule
        rule.add_target(targets.SfnStateMachine(state_machine))
        return state_machine

    def _build_lambda_role(self, test_results_db: dynamodb.Table) -> iam.Role:
        return iam.Role(
            self,
            id=constants.STREAM_PROCESSOR_TEST_LAMBDA_ROLE_ARN,
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            inline_policies={
                'test_results':
                    iam.PolicyDocument(statements=[
                        iam.PolicyStatement(
                            actions=['dynamodb:PutItem'],
                            resources=[test_results_db.table_arn],
                            effect=iam.Effect.ALLOW,
                        )
                    ]),
            },
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name=(f'service-role/{constants.LAMBDA_BASIC_EXECUTION_ROLE}'))
            ],
        )

    def _build_test_lambda(self, lambda_layer: PythonLayerVersion, dynamodb_table: dynamodb.Table) -> _lambda.Function:
        role = self._build_lambda_role(test_results_db=dynamodb_table)
        lambda_function = _lambda.Function(
            self,
            id=constants.STREAM_PROCESSOR_TEST_LAMBDA,
            runtime=_lambda.Runtime.PYTHON_3_11,
            code=_lambda.Code.from_asset(constants.BUILD_FOLDER),
            handler='product.stream_processor.handlers.process_stream.lambda_layer',  # TODO change
            environment={
                constants.POWERTOOLS_SERVICE_NAME: constants.SERVICE_NAME,  # for logger, tracer and metrics
                constants.POWER_TOOLS_LOG_LEVEL: 'DEBUG',  # for logger
                'TABLE': dynamodb_table.table_name,
            },
            tracing=_lambda.Tracing.ACTIVE,
            retry_attempts=0,
            timeout=Duration.seconds(constants.STREAM_PROCESSOR_LAMBDA_TIMEOUT),
            memory_size=constants.STREAM_PROCESSOR_LAMBDA_MEMORY_SIZE,
            layers=[lambda_layer],
            role=role,
            log_retention=RetentionDays.ONE_DAY,
        )
        return lambda_function
