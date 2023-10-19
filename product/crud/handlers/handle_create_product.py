from http import HTTPMethod
from typing import Any

from aws_lambda_env_modeler import get_environment_variables, init_environment_variables
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext

from product.crud.domain_logic.create_product import create_product
from product.crud.handlers.constants import PRODUCT_PATH
from product.crud.handlers.models.env_vars import CreateVars
from product.crud.handlers.utils.rest_api_resolver import app
from product.crud.models.input import CreateProductInput
from product.crud.models.output import CreateProductOutput
from product.crud.models.product import Product
from product.observability import logger, metrics, tracer


@app.route(PRODUCT_PATH, method=HTTPMethod.PUT)
def handle_create_product(product_id: str) -> dict[str, Any]:
    env_vars: CreateVars = get_environment_variables(model=CreateVars)
    logger.debug('environment variables', env_vars=env_vars.model_dump())

    # we want to extract and parse the HTTP body from the api gw envelope
    create_input: CreateProductInput = CreateProductInput.model_validate(app.current_event.raw_event)
    logger.append_keys(product_id=product_id)

    logger.info('got a valid create product request', product=create_input.model_dump())
    metrics.add_metric(name='CreateProductEvents', unit=MetricUnit.Count, value=1)

    response: CreateProductOutput = create_product(
        product=Product(
            id=product_id,
            name=create_input.body.name,
            price=create_input.body.price,
        ),
        table_name=env_vars.TABLE_NAME,
    )

    logger.info('finished handling create product request, product created', product=create_input.model_dump(), product_id=product_id)
    return response.model_dump()


@init_environment_variables(model=CreateVars)
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@metrics.log_metrics
@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
