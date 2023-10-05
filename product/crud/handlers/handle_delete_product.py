from http import HTTPStatus
from typing import Any, Dict

from aws_lambda_env_modeler import get_environment_variables, init_environment_variables
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.parser import ValidationError, parse
from aws_lambda_powertools.utilities.typing import LambdaContext

from product.crud.domain_logic.delete_product import delete_product
from product.crud.handlers.schemas.env_vars import DeleteVars
from product.crud.handlers.utils.http_responses import build_response
from product.crud.handlers.utils.observability import logger, metrics, tracer
from product.crud.schemas.exceptions import InternalServerException
from product.crud.schemas.input import DeleteProductRequest


@init_environment_variables(model=DeleteVars)
@metrics.log_metrics
@tracer.capture_lambda_handler(capture_response=False)
def handle_delete_product(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    logger.set_correlation_id(context.aws_request_id)
    env_vars: DeleteVars = get_environment_variables(model=DeleteVars)
    logger.debug('environment variables', env_vars=env_vars.model_dump())

    try:
        # we want to extract and parse the HTTP body from the api gw envelope
        delete_input: DeleteProductRequest = parse(event=event, model=DeleteProductRequest)
        logger.append_keys(product_id=delete_input.pathParameters.product)
        logger.info('got a delete product request', product=delete_input.model_dump())

    except (ValidationError, TypeError):  # pragma: no cover
        logger.exception('event failed input validation')
        return build_response(http_status=HTTPStatus.BAD_REQUEST, body={})

    metrics.add_metric(name='DeleteProductEvents', unit=MetricUnit.Count, value=1)

    try:
        delete_product(
            product_id=delete_input.pathParameters.product,
            table_name=env_vars.TABLE_NAME,
        )
    except InternalServerException:  # pragma: no cover
        logger.exception('finished handling delete product request with internal error')
        return build_response(http_status=HTTPStatus.INTERNAL_SERVER_ERROR, body={})

    logger.info('finished handling delete product request')
    return build_response(http_status=HTTPStatus.NO_CONTENT, body={})
