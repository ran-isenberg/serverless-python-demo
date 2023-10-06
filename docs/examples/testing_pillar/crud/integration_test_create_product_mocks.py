from http import HTTPMethod, HTTPStatus

from botocore.stub import Stubber

from product.crud.handlers.handle_create_product import handle_create_product
from product.crud.integration.dynamo_db_handler import DynamoDbHandler
from tests.crud_utils import generate_create_product_request_body, generate_product_api_gw_event, generate_product_id
from tests.utils import generate_context


def test_internal_server_error(table_name: str) -> None:
    db_handler: DynamoDbHandler = DynamoDbHandler('table')
    table = db_handler._get_db_handler(table_name)
    stubber = Stubber(table.meta.client)
    stubber.add_client_error(method='put_item', service_error_code='ValidationException')
    stubber.activate()
    body = generate_create_product_request_body()
    product_id = generate_product_id()
    response = handle_create_product(
        event=generate_product_api_gw_event(
            body=body.model_dump(),
            http_method=HTTPMethod.PUT,
            path_params={'product': product_id},
            product_id=product_id,
        ),
        context=generate_context(),
    )

    assert response['statusCode'] == HTTPStatus.INTERNAL_SERVER_ERROR
    stubber.deactivate()
    DynamoDbHandler._instances = {}
