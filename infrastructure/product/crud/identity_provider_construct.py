from aws_cdk import CfnOutput, Duration, Fn, RemovalPolicy
from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_secretsmanager as secrets
from constructs import Construct

import infrastructure.product.constants as constants


class IdentityProviderConstruct(Construct):
    def __init__(self, scope: Construct, id_: str, is_production: bool) -> None:
        super().__init__(scope, id_)
        self.id_ = id_
        self.user_pool = self._create_user_pool(is_production)
        self.app_client = self._create_app_client(self.user_pool)
        if not is_production:
            self._create_test_user_password(self.user_pool)

    def _create_app_client(self, user_pool: cognito.UserPool) -> cognito.UserPoolClient:
        app_client = cognito.UserPoolClient(
            self,
            'UserPoolClient',
            user_pool=user_pool,
            auth_flows=cognito.AuthFlow(user_password=True),  # Allow username/password authentication
        )

        CfnOutput(self, id=constants.IDENTITY_APP_CLIENT_ID_OUTPUT, value=app_client.user_pool_client_id).override_logical_id(
            constants.IDENTITY_APP_CLIENT_ID_OUTPUT
        )
        return app_client

    def _create_user_pool(self, is_production: bool) -> cognito.UserPool:
        user_pool = cognito.UserPool(
            self,
            'UserPool',
            user_pool_name=constants.IDENTITY_USER_NAME,
            advanced_security_mode=cognito.AdvancedSecurityMode.ENFORCED,
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
            mfa=cognito.Mfa.OPTIONAL,
        )

        CfnOutput(self, id=constants.IDENTITY_USER_POOL_ID_OUTPUT, value=user_pool.user_pool_id).override_logical_id(
            constants.IDENTITY_USER_POOL_ID_OUTPUT
        )
        return user_pool

    def _create_test_user_password(self, user_pool: cognito.UserPool):
        # Save the user's credentials to AWS Secrets Manager
        user_credentials_secret = secrets.Secret(
            self,
            f'{self.id_}TestsUserSecret',
            description='Credentials for the test user in the Cognito User Pool',
            generate_secret_string=secrets.SecretStringGenerator(
                secret_string_template=Fn.sub('{"username": "${user}"}', {'user': constants.TEST_USER_USERNAME}),
                generate_string_key='password',
                exclude_punctuation=False,
                exclude_lowercase=False,
                exclude_numbers=False,
                exclude_uppercase=False,
                include_space=False,
                password_length=16,
                require_each_included_type=True,
            ),
        )

        CfnOutput(self, id=constants.TEST_USER_IDENTITY_SECRET_NAME_OUTPUT, value=user_credentials_secret.secret_name).override_logical_id(
            constants.TEST_USER_IDENTITY_SECRET_NAME_OUTPUT
        )
