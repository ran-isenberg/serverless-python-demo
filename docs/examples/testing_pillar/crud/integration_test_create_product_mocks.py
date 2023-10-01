from http import HTTPStatus

from botocore.stub import Stubber

from product.crud.dal.dynamo_dal_handler import DynamoDalHandler
from product.crud.handlers.create_product import create_product
from tests.crud_utils import generate_api_gw_event, generate_create_product_request_body, generate_product_id
from tests.utils import generate_context


def test_internal_server_error(table_name: str) -> None:
    db_handler: DynamoDalHandler = DynamoDalHandler('table')
    table = db_handler._get_db_handler(table_name)
    stubber = Stubber(table.meta.client)
    stubber.add_client_error(method='put_item', service_error_code='ValidationException')
    stubber.activate()
    body = generate_create_product_request_body()
    response = create_product(
        event=generate_api_gw_event(
            body=body.model_dump(),
            path_params={'product': generate_product_id()},
        ),
        context=generate_context(),
    )

    assert response['statusCode'] == HTTPStatus.INTERNAL_SERVER_ERROR
    stubber.deactivate()
    DynamoDalHandler._instances = {}
