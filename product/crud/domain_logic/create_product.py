from aws_lambda_env_modeler import get_environment_variables
from aws_lambda_powertools.utilities.idempotency import DynamoDBPersistenceLayer, IdempotencyConfig, idempotent_function
from aws_lambda_powertools.utilities.idempotency.serialization.pydantic import PydanticSerializer

from product.crud.handlers.models.env_vars import Idempotency
from product.crud.integration import get_db_handler
from product.crud.integration.db_handler import DbHandler
from product.crud.models.output import CreateProductOutput
from product.crud.models.product import Product
from product.observability import logger, tracer

IDEMPOTENCY_LAYER = DynamoDBPersistenceLayer(table_name=get_environment_variables(model=Idempotency).IDEMPOTENCY_TABLE_NAME)
IDEMPOTENCY_CONFIG = IdempotencyConfig(
    expires_after_seconds=60,  # 1 minute
)


@idempotent_function(
    data_keyword_argument='product',
    config=IDEMPOTENCY_CONFIG,
    persistence_store=IDEMPOTENCY_LAYER,
    output_serializer=PydanticSerializer,
)
@tracer.capture_method(capture_response=False)
def create_product(product: Product, table_name: str) -> CreateProductOutput:
    logger.info('handling create product request')

    db_handler: DbHandler = get_db_handler(table_name)
    db_handler.create_product(product=product)
    # convert from db entry to output, they won't always be the same
    logger.info('created product successfully')
    return CreateProductOutput(id=product.id)
