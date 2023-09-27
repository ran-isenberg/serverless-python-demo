from typing import Annotated

from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventModel
from pydantic import BaseModel, Field, Json, PositiveInt

from product.crud.schemas.shared_types import ProductId


class PutProductBody(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=20)]
    price: PositiveInt


class PutPathParams(BaseModel):
    product: ProductId


class CreateProductRequest(APIGatewayProxyEventModel):
    body: Json[PutProductBody]  # type: ignore
    pathParameters: PutPathParams  # type: ignore


class ProductPathParams(BaseModel):
    product: ProductId


class GetProductRequest(APIGatewayProxyEventModel):
    pathParameters: ProductPathParams  # type: ignore


class DeleteProductRequest(APIGatewayProxyEventModel):
    pathParameters: ProductPathParams  # type: ignore
