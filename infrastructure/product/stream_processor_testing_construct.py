from pathlib import Path

from aws_cdk import CfnOutput, RemovalPolicy
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_events as events
from aws_cdk import aws_events_targets as targets
from aws_cdk import aws_iam as iam
from aws_cdk import aws_stepfunctions as sfn
from aws_cdk.aws_logs import LogGroup
from constructs import Construct

import infrastructure.product.constants as constants


class StreamProcessorTestingConstruct(Construct):
    STATE_MACHINE_FILE = Path(__file__).parent.joinpath('store_intercepted_events.asl')

    def __init__(self, scope: Construct, id_: str, events: events.EventBus) -> None:
        super().__init__(scope, id_)
        self.id_ = id_
        self.test_results_db = self._build_test_results_db(id_)
        self.state_machine = self._build_state_machine(table=self.test_results_db)
        self.rule = self._build_event_bridge_rule(event_bus=events, state_machine=self.state_machine)

    def _build_test_results_db(self, id_prefix: str) -> dynamodb.Table:
        table_id = f'{id_prefix}{constants.STREAM_PROCESSOR_TEST_TABLE_NAME}'
        table = dynamodb.Table(
            self,
            table_id,
            table_name=table_id,
            partition_key=dynamodb.Attribute(name='pk', type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name='sk', type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            point_in_time_recovery=True,
            removal_policy=RemovalPolicy.DESTROY,
        )
        CfnOutput(self, id=constants.STREAM_PROCESSOR_TEST_TABLE_NAME_OUTPUT, value=table.table_name).override_logical_id(
            constants.STREAM_PROCESSOR_TEST_TABLE_NAME_OUTPUT
        )
        return table

    def _build_event_bridge_rule(self, event_bus: events.EventBus, state_machine: sfn.StateMachine) -> events.Rule:
        # Rule to intercept test and prod events
        rule = events.Rule(
            self,
            f'{self.id_}TestRule',
            event_pattern=events.EventPattern(
                source=events.Match.any_of(events.Match.prefix('test_'), events.Match.exact_string(constants.STREAM_PROCESSOR_EVENT_SOURCE_NAME))
            ),
            enabled=True,
            event_bus=event_bus,
        )

        # When matched, kick off our state machine
        rule.add_target(targets.SfnStateMachine(state_machine))

        return rule

    def _build_state_machine(self, table: dynamodb.Table) -> sfn.StateMachine:
        # Create a role for the Step Function
        step_function_role = iam.Role(
            self,
            f'{self.id_}StepFunctionRole',
            assumed_by=iam.ServicePrincipal('states.amazonaws.com'),
            inline_policies={
                'write_events': iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=['dynamodb:PutItem'],
                            resources=[table.table_arn],
                            effect=iam.Effect.ALLOW,
                        )
                    ]
                )
            },
        )

        # Define the state machine
        state_machine_definition = sfn.DefinitionBody.from_file(f'{self.STATE_MACHINE_FILE}')

        # Log group and logging configuration
        state_machine_log_group = LogGroup(
            self,
            f'{self.id_}TestStateMachineLogGroup',
            removal_policy=RemovalPolicy.DESTROY,
            log_group_name=f'/aws/vendedlogs/states/{self.id_}',
        )

        state_machine_log_config = sfn.LogOptions(destination=state_machine_log_group, level=sfn.LogLevel.ALL, include_execution_data=True)

        return sfn.StateMachine(
            self,
            f'{self.id_}StateMachine',
            definition_body=state_machine_definition,
            definition_substitutions={'TABLE_NAME': table.table_name},
            role=step_function_role,
            tracing_enabled=True,
            logs=state_machine_log_config,
            state_machine_type=sfn.StateMachineType.EXPRESS,
        )
