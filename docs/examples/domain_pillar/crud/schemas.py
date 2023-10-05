from typing import Annotated

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
