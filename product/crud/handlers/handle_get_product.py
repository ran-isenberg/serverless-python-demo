from typing import Any

from aws_lambda_env_modeler import get_environment_variables, init_environment_variables
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext

from product.crud.domain_logic.get_product import get_product
from product.crud.handlers.constants import PRODUCT_PATH
from product.crud.handlers.schemas.env_vars import GetVars
from product.crud.handlers.utils.observability import logger, metrics, tracer
from product.crud.handlers.utils.rest_api_resolver import app
from product.crud.schemas.input import GetProductRequest
from product.crud.schemas.output import GetProductOutput


@app.get(PRODUCT_PATH)
def handle_get_product(product_id: str) -> dict[str, Any]:
    env_vars: GetVars = get_environment_variables(model=GetVars)
    logger.debug('environment variables', env_vars=env_vars.model_dump())

    GetProductRequest.model_validate(app.current_event.raw_event)

    logger.append_keys(product_id=product_id)
    logger.info('got a get product request')
    metrics.add_metric(name='GetProductEvents', unit=MetricUnit.Count, value=1)

    response: GetProductOutput = get_product(product_id=product_id, table_name=env_vars.TABLE_NAME)

    logger.info('finished handling get product request, product was not found')
    return response.model_dump()


@init_environment_variables(model=GetVars)
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@metrics.log_metrics
@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
