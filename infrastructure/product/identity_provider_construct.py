from os import path

from aws_cdk import CfnOutput, CustomResource, Duration, Fn, RemovalPolicy
from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_secretsmanager as secrets
from aws_cdk.custom_resources import AwsCustomResource, AwsCustomResourcePolicy, PhysicalResourceId, Provider
from constructs import Construct

import infrastructure.product.constants as constants


class IdentityProviderConstruct(Construct):
    def __init__(self, scope: Construct, id_: str, is_production: bool = False) -> None:
        super().__init__(scope, id_)
        self.id_ = id_

        # Create the Cognito User Pool with recommended settings
        user_pool = cognito.UserPool(
            self,
            'UserPool',
            user_pool_name=constants.IDENTITY_USER_NAME,
            advanced_security_mode=cognito.AdvancedSecurityMode.ENFORCED,
            # Password policy
            password_policy=cognito.PasswordPolicy(
                min_length=12,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=True,
                temp_password_validity=Duration.days(7),
            ),
            sign_in_aliases=cognito.SignInAliases(username=True, email=True),
            removal_policy=RemovalPolicy.DESTROY,
            mfa=cognito.Mfa.OPTIONAL if not is_production else cognito.Mfa.REQUIRED,
        )

        CfnOutput(self, id=constants.IDENTITY_USER_POOL_ID_OUTPUT, value=user_pool.user_pool_id).override_logical_id(
            constants.IDENTITY_USER_POOL_ID_OUTPUT
        )

        app_client = cognito.UserPoolClient(
            self,
            'UserPoolClient',
            user_pool=user_pool,
            auth_flows=cognito.AuthFlow(user_password=True),  # Allow username/password authentication
        )

        CfnOutput(self, id=constants.IDENTITY_APP_CLIENT_ID_OUTPUT, value=app_client.user_pool_client_id).override_logical_id(
            constants.IDENTITY_APP_CLIENT_ID_OUTPUT
        )

        # Custom Resource to set user password directly
        create_test_user = AwsCustomResource(
            self,
            'AwsCustomResource-CreateUser',
            on_create={
                'service': 'CognitoIdentityServiceProvider',
                'action': 'adminCreateUser',
                'parameters': {
                    'UserPoolId': user_pool.user_pool_id,
                    'Username': constants.TEST_USER_USERNAME,
                    'MessageAction': 'SUPPRESS',
                    'TemporaryPassword': constants.TEST_USER_TEMP_PWD,
                },
                'physical_resource_id': PhysicalResourceId.of(f'{self.id_}CreateTestUserResource'),
            },
            # on_delete={
            #    'service': 'CognitoIdentityServiceProvider',
            #    'action': 'adminDeleteUser',
            #    'parameters': {
            #        'UserPoolId': user_pool.user_pool_id,
            #        'Username': constants.TEST_USER_USERNAME,
            #    },
            # },
            policy=AwsCustomResourcePolicy.from_sdk_calls(resources=[user_pool.user_pool_arn]),
            install_latest_aws_sdk=True,
            removal_policy=RemovalPolicy.DESTROY,
            timeout=Duration.minutes(1),
        )
        create_test_user.node.add_dependency(user_pool.node.default_child)

        # Save the user's credentials to AWS Secrets Manager
        user_credentials_secret = secrets.Secret(
            self,
            'TestUserCredentials',
            description='Credentials for the test user in the Cognito User Pool',
            generate_secret_string=secrets.SecretStringGenerator(
                secret_string_template=Fn.sub('{"username": "${user}"}', {'user': constants.TEST_USER_USERNAME}),
                generate_string_key='password',
                exclude_punctuation=False,
                include_space=False,
                password_length=16,
            ),
        )

        CfnOutput(self, id=constants.TEST_USER_IDENTITY_SECRET_NAME_OUTPUT, value=user_credentials_secret.secret_name).override_logical_id(
            constants.TEST_USER_IDENTITY_SECRET_NAME_OUTPUT
        )

        with open(path.join(path.dirname(__file__), 'custom_resource_handler.py'), encoding='utf-8') as file:
            handler_code = file.read()

            # Lambda Function
        lambda_function = _lambda.Function(
            self,
            'MyLambdaFunction',
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler='index.handler',
            code=_lambda.InlineCode(handler_code),
        )

        # Grant permission to Lambda to get secrets and interact with Cognito
        user_credentials_secret.grant_read(lambda_function)
        lambda_function.add_to_role_policy(iam.PolicyStatement(actions=['cognito-idp:AdminSetUserPassword'], resources=[user_pool.user_pool_arn]))

        provider = Provider(scope=self, id=f'{id_}Provider', on_event_handler=lambda_function)
        lambda_resource = CustomResource(
            scope=self,
            id=f'{id_}SetAdminFunc',
            service_token=provider.service_token,
            removal_policy=RemovalPolicy.DESTROY,
            properties={
                'SecretName': user_credentials_secret.secret_name,
                'UserPoolId': user_pool.user_pool_id,
            },
            resource_type='Custom::IdentitySetTestPassword',
        )

        lambda_resource.node.add_dependency(user_credentials_secret)
