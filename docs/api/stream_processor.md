
## Product notification

### Lambda Handlers

Process stream is connected to Amazon DynamoDB Stream that polls product changes in the product table.

We convert them into `ProductChangeNotification` model depending on the DynamoDB Stream Event Name (e.g., `INSERT` -> `ADDED`).

::: product.stream_processor.handlers.process_stream

### Domain logic

Domain logic to notify product changes, e.g., `ADDED`, `REMOVED`, `UPDATED`.

::: product.stream_processor.domain_logic.product_notification
