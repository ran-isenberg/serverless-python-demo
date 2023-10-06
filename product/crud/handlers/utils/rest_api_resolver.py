import json
from http import HTTPStatus

from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response, content_types
from pydantic import ValidationError

from product.crud.handlers.utils.observability import logger
from product.crud.schemas.exceptions import InternalServerException, ProductAlreadyExistsException, ProductNotFoundException

app = APIGatewayRestResolver()


@app.exception_handler(ProductNotFoundException)
def handle_product_not_found_exception(ex: ProductNotFoundException):  # receives exception raised
    logger.exception('finished handling request with an error, product was not found')
    return Response(
        status_code=HTTPStatus.NOT_FOUND,
        content_type=content_types.APPLICATION_JSON,
        body=json.dumps({'error': 'product was not found'}),
    )


@app.exception_handler(ValidationError)
def handle_input_validation_error(ex: ValidationError):  # receives exception raised
    logger.exception('event failed input validation')
    return Response(
        status_code=HTTPStatus.BAD_REQUEST,
        content_type=content_types.APPLICATION_JSON,
        body=json.dumps({'error': 'invalid input'}),  # readiness: change pydantic error to a user friendly error
    )


@app.exception_handler(InternalServerException)
def handle_internal_server_error(ex: InternalServerException):  # receives exception raised
    logger.exception('finished handling request with internal error')
    return Response(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content_type=content_types.APPLICATION_JSON,
        body=json.dumps({'error': 'internal server error'}),
    )


@app.exception_handler(ProductAlreadyExistsException)
def handle_product_already_exists_exception(ex: ProductAlreadyExistsException):  # receives exception raised
    logger.exception('finished handling request with an error, product already exists')
    return Response(
        status_code=HTTPStatus.BAD_REQUEST,
        content_type=content_types.APPLICATION_JSON,
        body=json.dumps({'error': 'product already exists'}),
    )
