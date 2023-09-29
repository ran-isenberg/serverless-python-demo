from typing import Any
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools import Logger

logger = Logger()

@logger.inject_lambda_context(log_event=True)
def process_stream(event: dict[str, Any], context: LambdaContext):
    return 'Hello from the stream!'
