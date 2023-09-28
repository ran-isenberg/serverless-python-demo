from aws_lambda_env_modeler import get_environment_variables  # pragma: no cover
from aws_lambda_powertools.utilities.idempotency import DynamoDBPersistenceLayer, IdempotencyConfig  # pragma: no cover

from product.crud.handlers.schemas.env_vars import Idempotency  # pragma: no cover

IDEMPOTENCY_LAYER = DynamoDBPersistenceLayer(table_name=get_environment_variables(model=Idempotency).IDEMPOTENCY_TABLE_NAME)  # pragma: no cover
IDEMPOTENCY_CONFIG = IdempotencyConfig(
    expires_after_seconds=60,  # 1 minute
    event_key_jmespath='["pathParameters"]',
)  # pragma: no cover
