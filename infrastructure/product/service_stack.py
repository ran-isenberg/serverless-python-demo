from aws_cdk import Aspects, RemovalPolicy, Stack, Tags
from aws_cdk import aws_lambda as _lambda
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion
from cdk_nag import AwsSolutionsChecks, NagSuppressions
from constructs import Construct

import infrastructure.product.constants as constants
from infrastructure.product.crud_api_construct import CrudApiConstruct
from infrastructure.product.stream_processor_construct import StreamProcessorConstruct
from infrastructure.product.stream_processor_testing_construct import StreamProcessorTestingConstruct
from infrastructure.product.utils import get_construct_name, get_username


class ServiceStack(Stack):

    def __init__(self, scope: Construct, id: str, is_production: bool, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        self._add_stack_tags()
        self.shared_layer = self._build_common_lambda_layer(id)

        self.api = CrudApiConstruct(
            self,
            id_=get_construct_name(id, constants.CRUD_CONSTRUCT_NAME),
            lambda_layer=self.shared_layer,
        )

        self.stream_processor = StreamProcessorConstruct(
            self,
            id_=get_construct_name(id, constants.STREAM_PROCESSOR_CONSTRUCT_NAME),
            lambda_layer=self.shared_layer,
            dynamodb_table=self.api.api_db.db,
        )

        # deploy testing construct only in non production accounts
        if not is_production:
            StreamProcessorTestingConstruct(
                self,
                id_=get_construct_name(id, constants.STREAM_PROCESSOR_TEST_CONSTRUCT_NAME),
                lambda_layer=self.shared_layer,
                events=self.stream_processor.event_bus,
            )

        # add security check
        self._add_security_tests()

    def _build_common_lambda_layer(self, id_: str) -> PythonLayerVersion:
        return PythonLayerVersion(
            self,
            f'{id_}{constants.LAMBDA_LAYER_NAME}',
            entry=constants.COMMON_LAYER_BUILD_FOLDER,
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_11],
            removal_policy=RemovalPolicy.DESTROY,
        )

    def _add_stack_tags(self) -> None:
        # best practice to help identify resources in the console
        Tags.of(self).add(constants.SERVICE_NAME_TAG, constants.SERVICE_NAME)
        Tags.of(self).add(constants.OWNER_TAG, get_username())

    def _add_security_tests(self) -> None:
        Aspects.of(self).add(AwsSolutionsChecks(verbose=True))
        # Suppress a specific rule for this resource
        NagSuppressions.add_stack_suppressions(
            self,
            [
                {
                    'id': 'AwsSolutions-IAM4',
                    'reason': 'policy for cloudwatch logs.'
                },
                {
                    'id': 'AwsSolutions-IAM5',
                    'reason': 'policy for cloudwatch logs.'
                },
                {
                    'id': 'AwsSolutions-APIG2',
                    'reason': 'lambda does input validation'
                },
                {
                    'id': 'AwsSolutions-APIG1',
                    'reason': 'not mandatory in a sample template'
                },
                {
                    'id': 'AwsSolutions-APIG3',
                    'reason': 'not mandatory in a sample template'
                },
                {
                    'id': 'AwsSolutions-APIG6',
                    'reason': 'not mandatory in a sample template'
                },
                {
                    'id': 'AwsSolutions-APIG4',
                    'reason': 'authorization not mandatory in a sample template'
                },
                {
                    'id': 'AwsSolutions-COG4',
                    'reason': 'not using cognito'
                },
            ],
        )
