from typing import Annotated

from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventModel
from pydantic import BaseModel, Field, PositiveInt

from product.crud.schemas.shared_types import ProductId


class CreateProductInput(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=20)]
    price: PositiveInt


class ProductPathParams(BaseModel):
    product: ProductId


class GetProductRequest(APIGatewayProxyEventModel):
    pathParameters: ProductPathParams  # type: ignore


class DeleteProductRequest(APIGatewayProxyEventModel):
    pathParameters: ProductPathParams  # type: ignore
