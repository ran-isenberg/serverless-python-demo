
## Product notification

### Lambda Handlers

Process stream is connected to Amazon DynamoDB Stream that polls product changes in the product table.

We convert them into `ProductChangeNotification` model depending on the DynamoDB Stream Event Name (e.g., `INSERT` -> `ADDED`).

::: product.stream_processor.handlers.process_stream

### Domain logic

Domain logic to notify product changes, e.g., `ADDED`, `REMOVED`, `UPDATED`.

::: product.stream_processor.domain_logic.product_notification

### Integrations

These are integrations with external services. As of now, we only use one integration to send events, by default `Amazon EventBridge`.

> NOTE: We could make a single Event Handler. For now, we're using one event handler closely aligned with the model we want to convert into event for type safety.

::: product.stream_processor.integrations.events.event_handler

#### Interfaces

::: product.stream_processor.integrations.events.base

### Utility functions

::: product.stream_processor.integrations.events.functions
::: product.stream_processor.integrations.events.constants

### Exceptions

::: product.stream_processor.integrations.events.exceptions
