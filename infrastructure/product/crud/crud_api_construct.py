from aws_cdk import CfnOutput, Duration, aws_apigateway
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion
from aws_cdk.aws_logs import RetentionDays
from constructs import Construct

import infrastructure.product.constants as constants
from infrastructure.product.crud.crud_api_db_construct import ApiDbConstruct
from infrastructure.product.crud.crud_monitoring import CrudMonitoring
from infrastructure.product.crud.identity_provider_construct import IdentityProviderConstruct
from infrastructure.product.crud.waf_construct import WafToApiGatewayConstruct


class CrudApiConstruct(Construct):
    def __init__(self, scope: Construct, id_: str, lambda_layer: PythonLayerVersion, is_production: bool) -> None:
        super().__init__(scope, id_)
        self.api_db = ApiDbConstruct(self, f'{id_}db')
        self.common_layer = lambda_layer
        self.idp = IdentityProviderConstruct(self, f'{id_}users', is_production)
        self.rest_api = self._build_api_gw()
        api_resource: aws_apigateway.Resource = self.rest_api.root.add_resource('api')
        product_resource = api_resource.add_resource(constants.PRODUCT_RESOURCE).add_resource('{product}')
        authorizer = aws_apigateway.CognitoUserPoolsAuthorizer(self, 'ProductsAuthorizer', cognito_user_pools=[self.idp.user_pool])
        self.create_prod_func = self._add_put_product_lambda_integration(product_resource, self.api_db.db, self.api_db.idempotency_db, authorizer)
        self.delete_prod_func = self._add_delete_product_lambda_integration(product_resource, self.api_db.db, authorizer)
        self.get_prod_func = self._add_get_product_lambda_integration(product_resource, self.api_db.db, authorizer)
        products_resource: aws_apigateway.Resource = api_resource.add_resource(constants.PRODUCTS_RESOURCE)
        self.list_prods_func = self._add_list_products_lambda_integration(products_resource, self.api_db.db, authorizer)
        # add CW dashboards
        self.dashboard = CrudMonitoring(
            self,
            id_,
            crud_api=self.rest_api,
            db=self.api_db.db,
            idempotency_table=self.api_db.idempotency_db,
            functions=[self.create_prod_func, self.delete_prod_func, self.get_prod_func, self.list_prods_func],
        )
        if is_production:
            # add WAF
            self.waf = WafToApiGatewayConstruct(self, f'{id_}waf', self.rest_api)

    def _build_api_gw(self) -> aws_apigateway.RestApi:
        rest_api: aws_apigateway.RestApi = aws_apigateway.RestApi(
            self,
            constants.REST_API_NAME,
            rest_api_name='Product CRUD Rest API',
            description='This service handles /api/product requests',
            deploy_options=aws_apigateway.StageOptions(throttling_rate_limit=2, throttling_burst_limit=10),
            cloud_watch_role=False,
        )

        CfnOutput(self, id=constants.APIGATEWAY, value=rest_api.url).override_logical_id(constants.APIGATEWAY)
        return rest_api

    def _build_create_product_lambda_role(self, db: dynamodb.Table, idempotency_table: dynamodb.Table) -> iam.Role:
        return iam.Role(
            self,
            constants.CREATE_PRODUCT_ROLE,
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            inline_policies={
                'dynamodb_db': iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=['dynamodb:PutItem'],
                            resources=[db.table_arn],
                            effect=iam.Effect.ALLOW,
                        )
                    ]
                ),
                'idempotency_table': iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=['dynamodb:PutItem', 'dynamodb:GetItem', 'dynamodb:UpdateItem', 'dynamodb:DeleteItem'],
                            resources=[idempotency_table.table_arn],
                            effect=iam.Effect.ALLOW,
                        )
                    ]
                ),
            },
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name=(f'service-role/{constants.LAMBDA_BASIC_EXECUTION_ROLE}'))
            ],
        )

    def _build_delete_product_lambda_role(self, db: dynamodb.Table) -> iam.Role:
        return iam.Role(
            self,
            constants.DELETE_PRODUCT_ROLE,
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            inline_policies={
                'dynamodb_db': iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=['dynamodb:DeleteItem'],
                            resources=[db.table_arn],
                            effect=iam.Effect.ALLOW,
                        )
                    ]
                ),
            },
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name=(f'service-role/{constants.LAMBDA_BASIC_EXECUTION_ROLE}'))
            ],
        )

    def _build_get_product_lambda_role(self, db: dynamodb.Table) -> iam.Role:
        return iam.Role(
            self,
            constants.GET_PRODUCT_ROLE,
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            inline_policies={
                'dynamodb_db': iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=['dynamodb:GetItem'],
                            resources=[db.table_arn],
                            effect=iam.Effect.ALLOW,
                        )
                    ]
                ),
            },
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name=(f'service-role/{constants.LAMBDA_BASIC_EXECUTION_ROLE}'))
            ],
        )

    def _build_list_products_lambda_role(self, db: dynamodb.Table) -> iam.Role:
        return iam.Role(
            self,
            constants.LIST_PRODUCTS_ROLE,
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            inline_policies={
                'dynamodb_db': iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=['dynamodb:Scan'],
                            resources=[db.table_arn],
                            effect=iam.Effect.ALLOW,
                        )
                    ]
                ),
            },
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name=(f'service-role/{constants.LAMBDA_BASIC_EXECUTION_ROLE}'))
            ],
        )

    def _add_put_product_lambda_integration(
        self,
        put_resource: aws_apigateway.Resource,
        db: dynamodb.Table,
        idempotency_table: dynamodb.Table,
        auth: aws_apigateway.CognitoUserPoolsAuthorizer,
    ) -> _lambda.Function:
        role = self._build_create_product_lambda_role(db, idempotency_table)
        lambda_function = _lambda.Function(
            self,
            constants.CREATE_LAMBDA,
            runtime=_lambda.Runtime.PYTHON_3_13,
            code=_lambda.Code.from_asset(constants.BUILD_FOLDER),
            handler='product.crud.handlers.handle_create_product.lambda_handler',
            environment={
                constants.POWERTOOLS_SERVICE_NAME: constants.SERVICE_NAME,  # for logger, tracer and metrics
                constants.POWER_TOOLS_LOG_LEVEL: 'DEBUG',  # for logger
                'TABLE_NAME': db.table_name,
                'IDEMPOTENCY_TABLE_NAME': idempotency_table.table_name,
            },
            tracing=_lambda.Tracing.ACTIVE,
            retry_attempts=0,
            timeout=Duration.seconds(constants.API_HANDLER_LAMBDA_TIMEOUT),
            memory_size=constants.API_HANDLER_LAMBDA_MEMORY_SIZE,
            layers=[self.common_layer],
            role=role,
            log_retention=RetentionDays.ONE_DAY,
            log_format=_lambda.LogFormat.JSON.value,
            system_log_level=_lambda.SystemLogLevel.INFO.value,
        )

        # PUT /api/product/{product}/
        put_resource.add_method(
            http_method='PUT',
            integration=aws_apigateway.LambdaIntegration(handler=lambda_function),
            authorization_type=aws_apigateway.AuthorizationType.COGNITO,
            authorizer=auth,
        )
        return lambda_function

    def _add_delete_product_lambda_integration(
        self,
        resource: aws_apigateway.Resource,
        db: dynamodb.Table,
        auth: aws_apigateway.CognitoUserPoolsAuthorizer,
    ) -> _lambda.Function:
        role = self._build_delete_product_lambda_role(db)
        lambda_function = _lambda.Function(
            self,
            constants.DELETE_LAMBDA,
            runtime=_lambda.Runtime.PYTHON_3_13,
            code=_lambda.Code.from_asset(constants.BUILD_FOLDER),
            handler='product.crud.handlers.handle_delete_product.lambda_handler',
            environment={
                constants.POWERTOOLS_SERVICE_NAME: constants.SERVICE_NAME,  # for logger, tracer and metrics
                constants.POWER_TOOLS_LOG_LEVEL: 'DEBUG',  # for logger
                'TABLE_NAME': db.table_name,
            },
            tracing=_lambda.Tracing.ACTIVE,
            retry_attempts=0,
            timeout=Duration.seconds(constants.API_HANDLER_LAMBDA_TIMEOUT),
            memory_size=constants.API_HANDLER_LAMBDA_MEMORY_SIZE,
            layers=[self.common_layer],
            role=role,
            log_retention=RetentionDays.ONE_DAY,
            log_format=_lambda.LogFormat.JSON.value,
            system_log_level=_lambda.SystemLogLevel.INFO.value,
        )

        # DELETE /api/product/{product}/
        resource.add_method(
            http_method='DELETE',
            integration=aws_apigateway.LambdaIntegration(handler=lambda_function),
            authorization_type=aws_apigateway.AuthorizationType.COGNITO,
            authorizer=auth,
        )
        return lambda_function

    def _add_get_product_lambda_integration(
        self,
        resource: aws_apigateway.Resource,
        db: dynamodb.Table,
        auth: aws_apigateway.CognitoUserPoolsAuthorizer,
    ) -> _lambda.Function:
        role = self._build_get_product_lambda_role(db)
        lambda_function = _lambda.Function(
            self,
            constants.GET_LAMBDA,
            runtime=_lambda.Runtime.PYTHON_3_13,
            code=_lambda.Code.from_asset(constants.BUILD_FOLDER),
            handler='product.crud.handlers.handle_get_product.lambda_handler',
            environment={
                constants.POWERTOOLS_SERVICE_NAME: constants.SERVICE_NAME,  # for logger, tracer and metrics
                constants.POWER_TOOLS_LOG_LEVEL: 'DEBUG',  # for logger
                'TABLE_NAME': db.table_name,
            },
            tracing=_lambda.Tracing.ACTIVE,
            retry_attempts=0,
            timeout=Duration.seconds(constants.API_HANDLER_LAMBDA_TIMEOUT),
            memory_size=constants.API_HANDLER_LAMBDA_MEMORY_SIZE,
            layers=[self.common_layer],
            role=role,
            log_retention=RetentionDays.ONE_DAY,
            log_format=_lambda.LogFormat.JSON.value,
            system_log_level=_lambda.SystemLogLevel.INFO.value,
        )

        # GET /api/product/{product}/
        resource.add_method(
            http_method='GET',
            integration=aws_apigateway.LambdaIntegration(handler=lambda_function),
            authorization_type=aws_apigateway.AuthorizationType.COGNITO,
            authorizer=auth,
        )
        return lambda_function

    def _add_list_products_lambda_integration(
        self,
        api_resource: aws_apigateway.Resource,
        db: dynamodb.Table,
        auth: aws_apigateway.CognitoUserPoolsAuthorizer,
    ) -> _lambda.Function:
        role = self._build_list_products_lambda_role(db)
        lambda_function = _lambda.Function(
            self,
            constants.LIST_LAMBDA,
            runtime=_lambda.Runtime.PYTHON_3_13,
            code=_lambda.Code.from_asset(constants.BUILD_FOLDER),
            handler='product.crud.handlers.handle_list_products.lambda_handler',
            environment={
                constants.POWERTOOLS_SERVICE_NAME: constants.SERVICE_NAME,  # for logger, tracer and metrics
                constants.POWER_TOOLS_LOG_LEVEL: 'DEBUG',  # for logger
                'TABLE_NAME': db.table_name,
            },
            tracing=_lambda.Tracing.ACTIVE,
            retry_attempts=0,
            timeout=Duration.seconds(constants.API_HANDLER_LAMBDA_TIMEOUT),
            memory_size=constants.API_HANDLER_LAMBDA_MEMORY_SIZE,
            layers=[self.common_layer],
            role=role,
            log_retention=RetentionDays.ONE_DAY,
            log_format=_lambda.LogFormat.JSON.value,
            system_log_level=_lambda.SystemLogLevel.INFO.value,
        )

        # GET /api/products/
        api_resource.add_method(
            http_method='GET',
            integration=aws_apigateway.LambdaIntegration(handler=lambda_function),
            authorization_type=aws_apigateway.AuthorizationType.COGNITO,
            authorizer=auth,
        )

        return lambda_function
