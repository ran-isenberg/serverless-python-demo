from product.stream_processor.integrations.events.models.output import EventReceiptFail


class NotificationDeliveryError(Exception):
    def __init__(self, message: str, receipts: list[EventReceiptFail]):
        """Exception raised when a notification delivery fails.

        Parameters
        ----------
        message : str
            error message
        receipts : list[EventReceiptFail]
            list of receipts failed notification deliveries along with details
        """
        super().__init__(message)
        self.message = message
        self.receipts = receipts


class ProductChangeNotificationDeliveryError(NotificationDeliveryError):
    """Raised when one or all product change notification deliveries fail."""

    def __init__(self, message: str, receipts: list[EventReceiptFail]):
        super().__init__(message, receipts)
