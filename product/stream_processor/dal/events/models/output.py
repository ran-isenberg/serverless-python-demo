from pydantic import BaseModel


class EventReceiptSuccessfulNotification(BaseModel):
    receipt_id: str


class EventReceiptUnsuccessfulNotification(BaseModel):
    receipt_id: str
    error: str
    details: dict


class EventReceipt(BaseModel):
    successful_notifications: list[EventReceiptSuccessfulNotification]
    unsuccessful_notifications: list[EventReceiptUnsuccessfulNotification]
