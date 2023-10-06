import os
from http import HTTPStatus
from typing import Annotated, Any

from aws_lambda_powertools.utilities.parser import ValidationError, parse
from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventModel
from pydantic import BaseModel, Field, Json, PositiveInt

from product.crud.domain_logic.create_product import create_product
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


def handle_create_product(event, context) -> dict[str, Any]:
    try:
        create_input: CreateProductRequest = parse(event=event, model=CreateProductRequest)
        logger.info('got create product request', product=create_input.model_dump())
    except (ValidationError, TypeError):
        logger.exception('failed to parse input')
        return {'statusCode': HTTPStatus.BAD_REQUEST, 'headers': {'Content-Type': 'application/json'}, 'body': ''}

    try:
        response: CreateProductOutput = create_product(
            product_id=create_input.pathParameters.product,
            product_name=create_input.body.name,
            product_price=create_input.body.price,
            table_name=os.getenv('TABLE_NAME', ''),
        )
    except Exception:
        logger.exception('caught an internal error')
        return {'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'headers': {'Content-Type': 'application/json'}, 'body': ''}

    logger.info('finished handling create product request')
    return {'statusCode': HTTPStatus.OK, 'headers': {'Content-Type': 'application/json'}, 'body': response.model_dump()}
