from aws_lambda_env_modeler import get_environment_variables
from aws_lambda_powertools.utilities.idempotency import DynamoDBPersistenceLayer, IdempotencyConfig

from service.crud.handlers.schemas.env_vars import Idempotency

IDEMPOTENCY_LAYER = DynamoDBPersistenceLayer(table_name=get_environment_variables(model=Idempotency).IDEMPOTENCY_TABLE_NAME)
IDEMPOTENCY_CONFIG = IdempotencyConfig(
    expires_after_seconds=60,  # 1 minutes
    event_key_jmespath='powertools_json(body).[name, id, price]',
)
