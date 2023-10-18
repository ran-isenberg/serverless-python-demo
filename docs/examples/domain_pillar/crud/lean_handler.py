import os
from http import HTTPStatus
from typing import Annotated, Any

from aws_lambda_powertools.utilities.parser import parse
from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventModel
from pydantic import BaseModel, Field, Json, PositiveInt

from product.crud.domain_logic.create_product import create_product
from product.crud.schemas.output import CreateProductOutput
from product.models.products.product import Product
from product.observability import logger

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
    create_input: CreateProductRequest = parse(event=event, model=CreateProductRequest)
    logger.info('got create product request', product=create_input.model_dump())

    response: CreateProductOutput = create_product(
        product=Product(
            id=create_input.pathParameters.product,
            name=create_input.body.name,
            price=create_input.body.price,
        ),
        table_name=os.getenv('TABLE_NAME', ''),
    )

    logger.info('finished handling create product request')
    return {
        'statusCode': HTTPStatus.OK,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': response.model_dump(),
    }
