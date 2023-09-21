from http import HTTPStatus
from typing import Any, Dict

from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext

from product.crud.handlers.utils.http_responses import build_response
from product.crud.handlers.utils.observability import logger, metrics, tracer


@metrics.log_metrics
@tracer.capture_lambda_handler(capture_response=False)
def list_products(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    logger.set_correlation_id(context.aws_request_id)

    metrics.add_metric(name='ListProductsEvents', unit=MetricUnit.Count, value=1)

    logger.info('finished handling list products request')
    return build_response(http_status=HTTPStatus.NOT_IMPLEMENTED, body={})
