from aws_cdk import Aspects, RemovalPolicy, Stack, Tags
from aws_cdk import aws_lambda as _lambda
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion
from cdk_nag import AwsSolutionsChecks, NagSuppressions
from constructs import Construct

import cdk.service.constants as constants
from cdk.service.async_construct import AsyncConstruct
from cdk.service.crud_api_construct import CrudApiConstruct
from cdk.service.utils import get_construct_name, get_username


class ServiceStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        self._add_stack_tags()
        self.shared_layer = self._build_common_lambda_layer(id)

        self.api = CrudApiConstruct(
            self,
            id_=get_construct_name(id, constants.CRUD_CONSTRUCT_NAME),
            lambda_layer=self.shared_layer,
        )

        self.async_flow = AsyncConstruct(
            self,
            id_=get_construct_name(id, constants.ASYNC_CONSTRUCT_NAME),
            lambda_layer=self.shared_layer,
            dynamodb_table=self.api.api_db.db,
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
