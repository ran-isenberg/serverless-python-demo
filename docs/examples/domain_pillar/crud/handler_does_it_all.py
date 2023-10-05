import os
from http import HTTPStatus
from typing import Annotated, Any, Dict

import boto3
from aws_lambda_powertools.utilities.parser import ValidationError, parse
from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventModel
from botocore.exceptions import ClientError
from pydantic import BaseModel, Field, Json, PositiveInt

from product.crud.handlers.utils.http_responses import build_response
from product.crud.handlers.utils.observability import logger

ProductId = Annotated[str, Field(min_length=36, max_length=36)]


class PutProduct(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=20)]
    price: PositiveInt


class PathParams(BaseModel):
    product: ProductId


class CreateProductRequest(APIGatewayProxyEventModel):
    body: Json[PutProduct]  # type: ignore
    pathParameters: PathParams  # type: ignore


def create_product(event, context) -> Dict[str, Any]:
    try:
        create_input: CreateProductRequest = parse(event=event, model=CreateProductRequest)
        logger.info('got create product request', product=create_input.model_dump())
    except (ValidationError, TypeError):
        logger.exception('failed to parse input')
        return build_response(http_status=HTTPStatus.BAD_REQUEST, body={})

    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.getenv('TABLE_NAME', ''))
        table.put_item(Item={
            'name': create_input.body.name,
            'id': create_input.pathParameters.product,
            'price': create_input.body.price,
        })
    except ClientError:
        logger.exception('failed to create product')
        return build_response(http_status=HTTPStatus.INTERNAL_SERVER_ERROR, body={})

    return build_response(http_status=HTTPStatus.OK, body={
        'id': create_input.pathParameters.product,
    })
