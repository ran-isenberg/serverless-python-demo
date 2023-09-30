"""This will be replaced with hypothesis later"""
import random
import time
from typing import Any


def generate_dynamodb_stream_events(
    product_id: str = '8c18c85a-0f10-4b73-b54a-07ab0d381018',
) -> dict[str, Any]:
    return {
        'Records': [
            {
                'eventID': 'af0065970f39f49c7d014079db1b86ce',
                'eventName': 'INSERT',
                'eventVersion': '1.1',
                'eventSource': 'aws:dynamodb',
                'awsRegion': 'eu-west-1',
                'dynamodb': {
                    'ApproximateCreationDateTime': time.time(),
                    'Keys': {'id': {'S': f'{product_id}'}},
                    'NewImage': {
                        'price': {'N': '1'},
                        'name': {'S': 'test'},
                        'id': {'S': f'{product_id}'},
                    },
                    'SequenceNumber': f'{random.randint(a=10**24, b=10**25 - 1)}',
                    'SizeBytes': 91,
                    'StreamViewType': 'NEW_AND_OLD_IMAGES',
                },
                'eventSourceARN': 'arn:aws:dynamodb:eu-west-1:123456789012:table/lessa-stream-processor-ProductCruddbproducts/stream/2023-09-29T09:00:01.491',
            },
            {
                'eventID': '4ef9babf010f884033a2bd761105f392',
                'eventName': 'REMOVE',
                'eventVersion': '1.1',
                'eventSource': 'aws:dynamodb',
                'awsRegion': 'eu-west-1',
                'dynamodb': {
                    'ApproximateCreationDateTime': time.time(),
                    'Keys': {'id': {'S': f'{product_id}'}},
                    'OldImage': {
                        'price': {'N': '1'},
                        'name': {'S': 'test'},
                        'id': {'S': f'{product_id}'},
                    },
                    'SequenceNumber': f'{random.randint(a=10**24, b=10**25 - 1)}',
                    'SizeBytes': 91,
                    'StreamViewType': 'NEW_AND_OLD_IMAGES',
                },
                'eventSourceARN': 'arn:aws:dynamodb:eu-west-1:123456789012:table/lessa-stream-processor-ProductCruddbproducts/stream/2023-09-29T09:00:01.491',
            },
        ]
    }
