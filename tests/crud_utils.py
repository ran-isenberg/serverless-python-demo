import json
import uuid
from typing import Any, Dict, Optional

from product.crud.schemas.input import PutProductBody
from tests.utils import generate_random_integer, generate_random_string


# example taken from AWS Lambda Powertools test files
# https://github.com/awslabs/aws-lambda-powertools-python/blob/develop/tests/events/apiGatewayProxyEvent.json
def generate_api_gw_event(body: Optional[Dict[str, Any]] = None, path_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {
        'version': '1.0',
        'resource': '/api/product',
        'path': '/api/product',
        'httpMethod': 'PUT',
        'headers': {
            'Header1': 'value1',
            'Header2': 'value2'
        },
        'multiValueHeaders': {
            'Header1': ['value1'],
            'Header2': ['value1', 'value2']
        },
        'queryStringParameters': {
            'parameter1': 'value1',
            'parameter2': 'value'
        },
        'multiValueQueryStringParameters': {
            'parameter1': ['value1', 'value2'],
            'parameter2': ['value']
        },
        'requestContext': {
            'accountId': '123456789012',
            'apiId': 'id',
            'authorizer': {
                'claims': None,
                'scopes': None
            },
            'domainName': 'id.execute-api.us-east-1.amazonaws.com',
            'domainPrefix': 'id',
            'extendedRequestId': 'request-id',
            'httpMethod': 'PUT',
            'identity': {
                'accessKey': None,
                'accountId': None,
                'caller': None,
                'cognitoAuthenticationProvider': None,
                'cognitoAuthenticationType': None,
                'cognitoIdentityId': None,
                'cognitoIdentityPoolId': None,
                'principalOrgId': None,
                'sourceIp': '192.168.0.1/32',
                'user': None,
                'userAgent': 'user-agent',
                'userArn': None,
                'clientCert': {
                    'clientCertPem': 'CERT_CONTENT',
                    'subjectDN': 'www.example.com',
                    'issuerDN': 'Example issuer',
                    'serialNumber': 'a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1',
                    'validity': {
                        'notBefore': 'May 28 12:30:02 2019 GMT',
                        'notAfter': 'Aug  5 09:36:04 2021 GMT'
                    }
                }
            },
            'path': '/api/product',
            'protocol': 'HTTP/1.1',
            'requestId': 'id=',
            'requestTime': '04/Mar/2020:19:15:17 +0000',
            'requestTimeEpoch': 1583349317135,
            'resourceId': None,
            'resourcePath': '/api/product',
            'stage': '$default'
        },
        'pathParameters': path_params,
        'stageVariables': None,
        'body': 'Hello from Lambda!' if body is None else json.dumps(body),
        'isBase64Encoded': True
    }


def generate_product_id() -> str:
    return str(uuid.uuid4())


def generate_create_product_request_body() -> PutProductBody:
    return PutProductBody(name=generate_random_string(), price=generate_random_integer())
