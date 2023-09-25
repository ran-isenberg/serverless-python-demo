import pytest
from botocore.stub import Stubber

from product.crud.dal.dynamo_dal_handler import DynamoDalHandler
from product.crud.schemas.exceptions import InternalServerException


def test_raise_exception(product_id):
    dummy_table_name = 'table'
    db_handler: DynamoDalHandler = DynamoDalHandler(dummy_table_name)
    table = db_handler._get_db_handler(dummy_table_name)
    with Stubber(table.meta.client) as stubber:
        stubber.add_client_error(method='put_item', service_error_code='ValidationException')
        with pytest.raises(InternalServerException):
            db_handler.create_product(product_id=product_id, product_name='aaa', product_price=5)
