from product.stream_processor.integrations.events.models.output import EventReceiptFail


class ProductNotificationDeliveryError(Exception):

    def __init__(self, message: str, receipts: list[EventReceiptFail]):
        super().__init__(message)
        self.message = message
        self.receipts = receipts
