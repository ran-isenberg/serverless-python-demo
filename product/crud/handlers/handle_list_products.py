from http import HTTPMethod
from typing import Any

from aws_lambda_env_modeler import get_environment_variables, init_environment_variables
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext

from product.crud.domain_logic.list_products import list_products
from product.crud.handlers.constants import PRODUCTS_PATH
from product.crud.handlers.schemas.env_vars import ListVars
from product.crud.handlers.utils.observability import logger, metrics, tracer
from product.crud.handlers.utils.rest_api_resolver import app
from product.crud.schemas.output import ListProductsOutput


@app.route(PRODUCTS_PATH, method=HTTPMethod.GET)
def handle_list_products() -> dict[str, Any]:
    env_vars: ListVars = get_environment_variables(model=ListVars)
    logger.debug('environment variables', env_vars=env_vars.model_dump())
    metrics.add_metric(name='ListProductsEvents', unit=MetricUnit.Count, value=1)

    response: ListProductsOutput = list_products(table_name=env_vars.TABLE_NAME)
    logger.info('finished handling list products request')
    return response.model_dump()


@init_environment_variables(model=ListVars)
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@metrics.log_metrics
@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
