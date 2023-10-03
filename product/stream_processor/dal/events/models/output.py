from pydantic import BaseModel, Field


class EventReceiptSuccess(BaseModel):
    receipt_id: str


class EventReceiptFail(BaseModel):
    receipt_id: str
    error: str
    details: dict


class EventReceipt(BaseModel):
    success: list[EventReceiptSuccess]
    failed: list[EventReceiptFail] = Field(default_factory=list)
