from aws_cdk import Duration
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_events as events
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk.aws_lambda_event_sources import DynamoEventSource
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion
from aws_cdk.aws_logs import RetentionDays
from constructs import Construct

import cdk.service.constants as constants


class AsyncConstruct(Construct):

    def __init__(self, scope: Construct, id_: str, lambda_layer: PythonLayerVersion, dynamodb_table: dynamodb.Table) -> None:
        super().__init__(scope, id_)
        bus_name = f'{id_}{constants.EVENT_BUS_NAME}'
        self.event_bus = events.EventBus(self, bus_name, event_bus_name=bus_name)
        self.role = self._build_lambda_role(dynamodb_table, self.event_bus)

        self.lambda_function = self._build_async_lambda(self.role, lambda_layer, dynamodb_table)

    def _build_lambda_role(self, db: dynamodb.Table, bus: events.EventBus) -> iam.Role:
        return iam.Role(
            self,
            constants.ASYNC_SERVICE_ROLE_ARN,
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            inline_policies={
                'streams':
                    iam.PolicyDocument(statements=[
                        iam.PolicyStatement(
                            actions=['dynamodb:DescribeStream', 'dynamodb:GetRecords', 'dynamodb:GetShardIterator', 'dynamodb:ListStreams'],
                            resources=[db.table_arn],
                            effect=iam.Effect.ALLOW,
                        )
                    ]),
                'event_bus':
                    iam.PolicyDocument(
                        statements=[iam.PolicyStatement(
                            actions=['events:PutEvents'],
                            resources=[bus.event_bus_arn],
                            effect=iam.Effect.ALLOW,
                        )]),
            },
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name=(f'service-role/{constants.LAMBDA_BASIC_EXECUTION_ROLE}'))
            ],
        )

    def _build_async_lambda(self, role: iam.Role, lambda_layer: PythonLayerVersion, dynamodb_table: dynamodb.Table) -> _lambda.Function:
        lambda_function = _lambda.Function(
            self,
            constants.ASYNC_LAMBDA,
            runtime=_lambda.Runtime.PYTHON_3_11,
            code=_lambda.Code.from_asset(constants.BUILD_FOLDER),
            handler='service.async.handlers.async_handler.handle_events',
            environment={
                constants.POWERTOOLS_SERVICE_NAME: constants.SERVICE_NAME,  # for logger, tracer and metrics
                constants.POWER_TOOLS_LOG_LEVEL: 'DEBUG',  # for logger
            },
            tracing=_lambda.Tracing.ACTIVE,
            retry_attempts=0,
            timeout=Duration.seconds(constants.API_HANDLER_LAMBDA_TIMEOUT),
            memory_size=constants.API_HANDLER_LAMBDA_MEMORY_SIZE,
            layers=[lambda_layer],
            role=role,
            log_retention=RetentionDays.ONE_DAY,
        )
        # Add DynamoDB Stream as an event source for the Lambda function
        lambda_function.add_event_source(DynamoEventSource(dynamodb_table, starting_position=_lambda.StartingPosition.LATEST))
        return lambda_function
