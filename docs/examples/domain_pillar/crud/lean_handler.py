import os
from http import HTTPStatus
from typing import Annotated, Any, Dict

from aws_lambda_powertools.utilities.parser import ValidationError, parse
from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventModel
from pydantic import BaseModel, Field, Json, PositiveInt

from product.crud.domain_logic.create_product import create_product
from product.crud.handlers.utils.http_responses import build_response
from product.crud.handlers.utils.observability import logger
from product.crud.schemas.output import CreateProductOutput

ProductId = Annotated[str, Field(min_length=36, max_length=36)]


class PutProduct(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=20)]
    price: PositiveInt


class PathParams(BaseModel):
    product: ProductId


class CreateProductRequest(APIGatewayProxyEventModel):
    body: Json[PutProduct]  # type: ignore
    pathParameters: PathParams  # type: ignore


def handle_create_product(event, context) -> Dict[str, Any]:
    try:
        create_input: CreateProductRequest = parse(event=event, model=CreateProductRequest)
        logger.info('got create product request', extra={'product': create_input.model_dump()})
    except (ValidationError, TypeError):
        logger.exception('failed to parse input')
        return build_response(http_status=HTTPStatus.BAD_REQUEST, body={})

    try:
        response: CreateProductOutput = create_product(
            product_id=create_input.pathParameters.product,
            product_name=create_input.body.name,
            product_price=create_input.body.price,
            table_name=os.getenv('TABLE_NAME', ''),
        )
    except Exception:
        logger.exception('caught an internal error')
        return build_response(http_status=HTTPStatus.INTERNAL_SERVER_ERROR, body={})

    logger.info('finished handling create product request')
    return build_response(http_status=HTTPStatus.OK, body=response.model_dump())
