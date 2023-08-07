import os
from pathlib import Path

from aws_cdk import Aspects, Stack, Tags
from cdk_nag import AwsSolutionsChecks, NagSuppressions
from constructs import Construct
from git import Repo

from cdk.service.api_construct import ApiConstruct
from cdk.service.constants import SERVICE_NAME
from cdk.service.async_construct import AsyncConstruct


def get_username() -> str:
    try:
        return os.getlogin().replace('.', '-')
    except Exception:
        return 'github'


def get_stack_name() -> str:
    repo = Repo(Path.cwd())
    username = get_username()
    try:
        return f'{username}-{repo.active_branch}-{SERVICE_NAME}'
    except TypeError:
        return f'{username}-{SERVICE_NAME}'


def get_construct_name(stack_prefix: str, construct_name: str) -> str:
    return f'{stack_prefix}{construct_name}'[0:64]


class ServiceStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        Tags.of(self).add('service_name', SERVICE_NAME)

        self.api = ApiConstruct(self, get_construct_name(id, 'Crud'))
        self.async_flow = AsyncConstruct(self, get_construct_name(id, 'Async'))
        # add security check
        self._add_security_tests()

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
