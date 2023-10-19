import os

from aws_cdk import App
from aws_cdk.assertions import Template

from infrastructure.product.service_stack import ServiceStack


def test_synthesizes_properly():
    app = App()
    environment = os.getenv('ENVIRONMENT', 'dev'),
    is_production = True if environment == 'production' else False,
    service_stack = ServiceStack(app, 'service-test', is_production)

    # Prepare the stack for assertions.
    template = Template.from_stack(service_stack)

    # verify that we have one API GW, that is it not deleted by mistake
    template.resource_count_is('AWS::ApiGateway::RestApi', 1)
    template.resource_count_is('AWS::DynamoDB::Table', 3)  # main db and one for idempotency and one for tests
    template.resource_count_is('AWS::Events::EventBus', 1)
