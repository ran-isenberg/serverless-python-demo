from http import HTTPStatus
from typing import Any, Dict

from aws_lambda_env_modeler import get_environment_variables, init_environment_variables
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.parser import ValidationError, parse
from aws_lambda_powertools.utilities.typing import LambdaContext

from product.crud.domain_logic.get_product import get_product
from product.crud.handlers.schemas.env_vars import GetVars
from product.crud.handlers.utils.http_responses import build_response
from product.crud.handlers.utils.observability import logger, metrics, tracer
from product.crud.schemas.exceptions import InternalServerException, ProductNotFoundException
from product.crud.schemas.input import GetProductRequest
from product.crud.schemas.output import GetProductOutput


@init_environment_variables(model=GetVars)
@metrics.log_metrics
@tracer.capture_lambda_handler(capture_response=False)
def handle_get_product(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    logger.set_correlation_id(context.aws_request_id)

    env_vars: GetVars = get_environment_variables(model=GetVars)
    logger.debug('environment variables', env_vars=env_vars.model_dump())

    try:
        # we want to extract and parse the HTTP body from the api gw envelope
        get_input: GetProductRequest = parse(event=event, model=GetProductRequest)
        logger.info('got a get product request', product=get_input.model_dump())
    except (ValidationError, TypeError):  # pragma: no cover
        logger.exception('event failed input validation')
        return build_response(http_status=HTTPStatus.BAD_REQUEST, body={})

    metrics.add_metric(name='GetProductEvents', unit=MetricUnit.Count, value=1)
    try:
        response: GetProductOutput = get_product(
            product_id=get_input.pathParameters.product,
            table_name=env_vars.TABLE_NAME,
        )
    except InternalServerException:  # pragma: no cover
        logger.exception('finished handling get product request with internal error')
        return build_response(http_status=HTTPStatus.INTERNAL_SERVER_ERROR, body={})
    except ProductNotFoundException:  # pragma: no cover
        logger.exception('finished handling get product request - product not found')
        return build_response(http_status=HTTPStatus.NOT_FOUND, body={})

    logger.info('finished handling get product request, product was found')
    return build_response(http_status=HTTPStatus.OK, body=response.model_dump())
