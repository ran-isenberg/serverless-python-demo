import json
import os
from typing import Annotated, Any

import boto3
from aws_lambda_powertools.utilities.parser import parse
from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventModel
from pydantic import BaseModel, Field, Json, PositiveInt

ProductId = Annotated[str, Field(min_length=36, max_length=36)]


class PutProduct(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=20)]
    price: PositiveInt


class PathParams(BaseModel):
    product: ProductId


class CreateProductRequest(APIGatewayProxyEventModel):
    body: Json[PutProduct]  # type: ignore
    pathParameters: PathParams  # type: ignore


def create_product(event, context) -> dict[str, Any]:
    create_input = parse(event=event, model=CreateProductRequest)
    product_id = create_input.pathParameters.product
    table_name = os.getenv('TABLE_NAME', '')
    table = boto3.resource('dynamodb').Table(table_name)
    table.put_item(Item={
        'name': create_input.body.name,
        'id': product_id,
        'price': create_input.body.price,
    })

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({'id': product_id}),
    }
