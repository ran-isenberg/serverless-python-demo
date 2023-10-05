from http import HTTPStatus
from typing import Any, Dict

from aws_lambda_env_modeler import get_environment_variables, init_environment_variables
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext

from product.crud.domain_logic.list_products import list_products
from product.crud.handlers.schemas.env_vars import ListVars
from product.crud.handlers.utils.http_responses import build_response
from product.crud.handlers.utils.observability import logger, metrics, tracer
from product.crud.schemas.exceptions import InternalServerException
from product.crud.schemas.output import ListProductsOutput


@init_environment_variables(model=ListVars)
@metrics.log_metrics
@tracer.capture_lambda_handler(capture_response=False)
def handle_list_products(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    logger.set_correlation_id(context.aws_request_id)

    env_vars: ListVars = get_environment_variables(model=ListVars)
    logger.debug('environment variables', env_vars=env_vars.model_dump())

    metrics.add_metric(name='ListProductsEvents', unit=MetricUnit.Count, value=1)

    try:
        response: ListProductsOutput = list_products(table_name=env_vars.TABLE_NAME)
    except InternalServerException:  # pragma: no cover
        logger.exception('finished handling list products request with internal error')
        return build_response(http_status=HTTPStatus.INTERNAL_SERVER_ERROR, body={})

    logger.info('finished handling list products request')
    return build_response(http_status=HTTPStatus.OK, body=response.model_dump())
