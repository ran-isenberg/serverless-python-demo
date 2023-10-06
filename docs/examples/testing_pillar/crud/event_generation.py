import json
from typing import Any, Dict, Optional


def generate_api_gw_event(
    body: Optional[Dict[str, Any]] = None,
    path_params: Optional[Dict[str, Any]] = None,
) -> dict[str, Any]:
    return {
        'version': '1.0',
        'resource': '/api/product',
        'path': '/api/product',
        'httpMethod': 'PUT',
        'headers': {
            'Header1': 'value1',
            'Header2': 'value2'
        },
        'requestContext': {
            'accountId': '123456789012',
            'apiId': 'id',
            'authorizer': {
                'claims': None,
                'scopes': None
            },
            'httpMethod': 'PUT',
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
        'body': '' if body is None else json.dumps(body),
        'isBase64Encoded': True
    }
