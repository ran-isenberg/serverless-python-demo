from http import HTTPStatus
from typing import Any, Dict

from aws_lambda_env_modeler import get_environment_variables, init_environment_variables
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.idempotency import idempotent
from aws_lambda_powertools.utilities.parser import ValidationError, parse
from aws_lambda_powertools.utilities.typing import LambdaContext

from product.crud.domain_logic.handle_create_request import handle_create_request
from product.crud.handlers.schemas.env_vars import CrudVars
from product.crud.handlers.utils.http_responses import build_response
from product.crud.handlers.utils.idempotency import IDEMPOTENCY_CONFIG, IDEMPOTENCY_LAYER
from product.crud.handlers.utils.observability import logger, metrics, tracer
from product.crud.schemas.exceptions import InternalServerException
from product.crud.schemas.input import CreateProductRequest
from product.crud.schemas.output import CreateProductOutput


@init_environment_variables(model=CrudVars)
@metrics.log_metrics
@idempotent(persistence_store=IDEMPOTENCY_LAYER, config=IDEMPOTENCY_CONFIG)
@tracer.capture_lambda_handler(capture_response=False)
def create_product(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    logger.set_correlation_id(context.aws_request_id)

    env_vars: CrudVars = get_environment_variables(model=CrudVars)
    logger.debug('environment variables', extra=env_vars.model_dump())

    try:
        # we want to extract and parse the HTTP body from the api gw envelope
        create_input: CreateProductRequest = parse(event=event, model=CreateProductRequest)
        logger.info('got create product request', extra={'product': create_input.model_dump()})
    except (ValidationError, TypeError) as exc:  # pragma: no cover
        logger.error('event failed input validation', extra={'error': str(exc)})
        return build_response(http_status=HTTPStatus.BAD_REQUEST, body={})

    metrics.add_metric(name='CreateProductEvents', unit=MetricUnit.Count, value=1)
    try:
        response: CreateProductOutput = handle_create_request(
            product_id=create_input.pathParameters.product,
            product_name=create_input.body.name,
            product_price=create_input.body.price,
            table_name=env_vars.TABLE_NAME,
        )
    except InternalServerException:  # pragma: no cover
        logger.error('finished handling create product request with internal error')
        return build_response(http_status=HTTPStatus.INTERNAL_SERVER_ERROR, body={})

    logger.info('finished handling create product request')
    return build_response(http_status=HTTPStatus.OK, body=response.model_dump())
