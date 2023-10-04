from typing import Any

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.data_classes.dynamo_db_stream_event import DynamoDBStreamEvent
from aws_lambda_powertools.utilities.typing import LambdaContext

from product.models.products.product import ProductChangeNotification
from product.stream_processor.domain_logic.product_notification import notify_product_updates
from product.stream_processor.integrations.events.event_handler import ProductChangeNotificationHandler

logger = Logger()


@logger.inject_lambda_context(log_event=True)
def process_stream(
    event: dict[str, Any],
    context: LambdaContext,
    event_handler: ProductChangeNotificationHandler | None = None,
) -> list[ProductChangeNotification]:
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
