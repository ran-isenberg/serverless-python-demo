import pytest
from botocore.stub import Stubber

from service.crud.dal.dynamo_dal_handler import DynamoDalHandler
from service.crud.schemas.exceptions import InternalServerException


def test_raise_exception(product_id):
    db_handler: DynamoDalHandler = DynamoDalHandler('table')
    table = db_handler._get_db_handler()
    stubber = Stubber(table.meta.client)
    stubber.add_client_error(method='put_item', service_error_code='ValidationException')
    stubber.activate()
    with pytest.raises(InternalServerException):
        db_handler.create_product_in_db(product_id=product_id, product_name='aaa', product_price=5)
    stubber.deactivate()
    DynamoDalHandler._instances = {}
