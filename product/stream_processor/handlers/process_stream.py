from typing import Any

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.data_classes.dynamo_db_stream_event import DynamoDBStreamEvent
from aws_lambda_powertools.utilities.typing import LambdaContext

from product.models.products.product import ProductChangeNotification
from product.stream_processor.domain_logic.product_notification import notify_product_updates
from product.stream_processor.integrations.events.event_handler import EventHandler
from product.stream_processor.integrations.events.models.output import EventReceipt

logger = Logger()


@logger.inject_lambda_context(log_event=True)
def process_stream(
    event: dict[str, Any],
    context: LambdaContext,
    event_handler: EventHandler | None = None,
) -> EventReceipt:
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
    event_handler : EventHandler | None, optional
        Event Handler to use to notify product changes, by default `EventHandler`

    Integrations
    ------------

    # Domain

    * `notify_product_updates` to notify `ProductChangeNotification` changes

    Returns
    -------
    EventReceipt
        Receipts for unsuccessfully and successfully published events.

    Raises
    ------
    ProductChangeNotificationDeliveryError
        Partial or total failures when sending notification. It allows the stream to stop at the exact same sequence number.

        This means sending notifications are at least once.
    """
    # Until we create our handler product stream change input
    stream_records = DynamoDBStreamEvent(event)

    product_updates = []
    for record in stream_records.records:
        product_id = record.dynamodb.keys.get('id', '')  # type: ignore[union-attr]

        match record.event_name:
            case record.event_name.INSERT:  # type: ignore[union-attr]
                product_updates.append(ProductChangeNotification(product_id=product_id, status='ADDED'))
            case record.event_name.MODIFY:  # type: ignore[union-attr]
                product_updates.append(ProductChangeNotification(product_id=product_id, status='UPDATED'))
            case record.event_name.REMOVE:  # type: ignore[union-attr]
                product_updates.append(ProductChangeNotification(product_id=product_id, status='REMOVED'))

    return notify_product_updates(update=product_updates, event_handler=event_handler)
