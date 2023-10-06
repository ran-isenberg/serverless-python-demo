from http import HTTPMethod, HTTPStatus

from aws_lambda_env_modeler import get_environment_variables, init_environment_variables
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext

from product.crud.domain_logic.delete_product import delete_product
from product.crud.handlers.constants import PRODUCT_PATH
from product.crud.handlers.schemas.env_vars import DeleteVars
from product.crud.handlers.utils.observability import logger, metrics, tracer
from product.crud.handlers.utils.rest_api_resolver import app
from product.crud.schemas.input import DeleteProductRequest


@app.route(PRODUCT_PATH, method=HTTPMethod.DELETE)
def handle_delete_product(product_id: str) -> tuple[None, HTTPStatus]:
    env_vars: DeleteVars = get_environment_variables(model=DeleteVars)
    logger.debug('environment variables', env_vars=env_vars.model_dump())

    DeleteProductRequest.model_validate(app.current_event.raw_event)

    logger.append_keys(product_id=product_id)
    logger.info('got a delete product request')
    metrics.add_metric(name='DeleteProductEvents', unit=MetricUnit.Count, value=1)

    delete_product(product_id=product_id, table_name=env_vars.TABLE_NAME)

    logger.info('finished handling delete product request')
    return None, HTTPStatus.NO_CONTENT


@init_environment_variables(model=DeleteVars)
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@metrics.log_metrics
@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
