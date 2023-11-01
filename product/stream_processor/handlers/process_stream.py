from typing import Any

from aws_lambda_env_modeler import get_environment_variables, init_environment_variables
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.data_classes.dynamo_db_stream_event import DynamoDBStreamEvent
from aws_lambda_powertools.utilities.typing import LambdaContext

from product.observability import logger, metrics, tracer
from product.stream_processor.domain_logic.product_notification import notify_product_updates
from product.stream_processor.handlers.models.env_vars import PrcStreamVars
from product.stream_processor.integrations.events.base import BaseEventHandler
from product.stream_processor.integrations.events.event_handler import EventHandler
from product.stream_processor.models.product import ProductChangeNotification


@init_environment_variables(model=PrcStreamVars)
@logger.inject_lambda_context(log_event=True)
@metrics.log_metrics
@tracer.capture_lambda_handler(capture_response=False)
def process_stream(
    event: dict[str, Any],
    context: LambdaContext,
    event_handler: BaseEventHandler | None = None,
) -> dict:
    """Process batch of Amazon DynamoDB Stream containing product changes.


    Parameters
    ----------
    event : dict[str, Any]
        DynamoDB Stream event.

        See [sample](https://docs.aws.amazon.com/lambda/latest/dg/with-ddb.html#events-sample-dynamodb)
    context : LambdaContext
        Lambda Context object.

        It is used to enrich our structured logging via Powertools for AWS Lambda.

        See [sample](https://docs.aws.amazon.com/lambda/latest/dg/python-context.html)
    event_handler : BaseEventHandler | None, optional
        Event Handler to use to notify product changes, by default `EventHandler` with EventBridge as a provider

    Integrations
    ------------

    # Domain

    * `notify_product_updates` to notify `ProductChangeNotification` changes

    Returns
    -------
    Dict
        Receipts for unsuccessfully and successfully published events.

    Raises
    ------
    ProductChangeNotificationDeliveryError
        Partial or total failures when sending notification. It allows the stream to stop at the exact same sequence number.

        This means sending notifications are at least once.
    """
    # Until we create our handler product stream change input
    stream_records = DynamoDBStreamEvent(event)

    env_vars = get_environment_variables(model=PrcStreamVars)
    logger.debug('environment variables', env_vars=env_vars.model_dump())

    metrics.add_metric(name='StreamRecords', unit=MetricUnit.Count, value=len(stream_records.keys()))

    product_updates = []
    for record in stream_records.records:
        product_id = record.dynamodb.keys.get('id', '')  # type: ignore[union-attr]
        logger.append_keys(product_id=product_id)
        logger.info('handling record', event_name=record.event_name)

        match record.event_name:
            case record.event_name.INSERT:  # type: ignore[union-attr]
                product_updates.append(ProductChangeNotification(product_id=product_id, status='ADDED'))
            case record.event_name.REMOVE:  # type: ignore[union-attr]
                product_updates.append(ProductChangeNotification(product_id=product_id, status='REMOVED'))

    if event_handler is None:  # pragma: no cover
        event_handler = EventHandler(event_source=env_vars.EVENT_SOURCE, event_bus=env_vars.EVENT_BUS)

    receipt = notify_product_updates(update=product_updates, event_handler=event_handler)

    return receipt.model_dump()
