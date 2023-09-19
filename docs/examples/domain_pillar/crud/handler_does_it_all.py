import os
from http import HTTPStatus
from typing import Any, Dict

import boto3
from aws_lambda_powertools.utilities.parser import ValidationError, parse
from botocore.exceptions import ClientError

from product.crud.handlers.utils.http_responses import build_response
from product.crud.handlers.utils.observability import logger
from product.crud.schemas.input import CreateProductRequest


def create_product(event, context) -> Dict[str, Any]:
    try:
        create_input: CreateProductRequest = parse(event=event, model=CreateProductRequest)
        logger.info('got create product request', extra={'product': create_input.model_dump()})
    except (ValidationError, TypeError) as exc:
        logger.exception('failed to parse input', extra={'exception': str(exc)})
        return build_response(http_status=HTTPStatus.BAD_REQUEST, body={})

    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.getenv('TABLE_NAME', ''))
        table.put_item(Item={
            'name': create_input.body.name,
            'id': create_input.pathParameters.product,
            'price': create_input.body.price,
        })
    except ClientError as exc:
        logger.exception('failed to create product', extra={'exception': str(exc)})
        return build_response(http_status=HTTPStatus.INTERNAL_SERVER_ERROR, body={})

    return build_response(http_status=HTTPStatus.OK, body={
        'id': create_input.pathParameters.product,
    })
