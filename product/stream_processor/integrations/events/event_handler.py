import re
from typing import Any
from uuid import uuid4

from product.stream_processor.integrations.events.base import BaseEventHandler, BaseEventProvider
from product.stream_processor.integrations.events.constants import DEFAULT_EVENT_VERSION
from product.stream_processor.integrations.events.models.input import AnyModel, Event, EventMetadata
from product.stream_processor.integrations.events.models.output import EventReceipt
from product.stream_processor.integrations.events.providers.eventbridge import EventBridge

_exclude_underscores = r'(?!^)(?<!_)'  # _ProductNotification
_pascal_case = r'[A-Z][a-z]+'  # ProductNotification
_followed_by_lower_case_or_digit = r'(?<=[a-z0-9])[A-Z])'  # V1ProductNotification
_or = r'|'
_pascal_to_snake_pattern = re.compile(rf'({_exclude_underscores}{_pascal_case}{_or}{_followed_by_lower_case_or_digit}')


class EventHandler(BaseEventHandler[AnyModel]):

    def __init__(self, event_source: str, event_bus: str, provider: BaseEventProvider | None = None) -> None:
        """Event Handler for emitting events with a given provider.

        Parameters
        ----------
        event_source : str
            Event source to inject in event metadata, following 'myorg.service_name.feature_name'
        event_bus: str
            Event bus to send events to
        provider : BaseEventProvider
            An event provider to send events to, by default EventBridge if omitted.
        """
        self.provider = provider or EventBridge(bus_name=event_bus)
        super().__init__(event_source=event_source, event_bus=event_bus, provider=self.provider)

    def emit(self, payload: list[AnyModel], metadata: dict[str, Any] | None = None, correlation_id='') -> EventReceipt:
        """Converts and emits a list of models into standard events with extra metadata and correlation ID.

        Parameters
        ----------
        payload : list[AnyModel]
        payload : list[AnyModel]
            List of product change notifications models to be sent.
        metadata : dict[str, Any] | None, optional
            Additional metadata to be injected into the event before sending, by default None
        correlation_id : str, optional
            Correlation ID to inject in event metadata. We generate one if not provided.

        Returns
        -------
        EventReceipt
            Receipts for unsuccessfully and successfully published events.
        """
        event_payload = EventHandler.build_events_from_models(models=payload, metadata=metadata, correlation_id=correlation_id,
                                                              event_source=self.event_source)
        return self.provider.send(payload=event_payload)

    @staticmethod
    def extract_event_name_from_model(model: AnyModel) -> str:
        """Derives a standard event name from the name of the model.

        It uses snake_case in uppercase letters, e.g., `ProductNotification` -> `PRODUCT_NOTIFICATION`.

        It also keeps numbers and acronyms that are typically abbreviation for something intact, e.g.: "ProductHTTP" -> "PRODUCT_HTTP"

        Parameters
        ----------
        model : AnyModel
            BaseModel to derive name from.

        # Examples

        Building event name from a given model

        ```python
        from pydantic import BaseModel
        from product.stream_processor.integrations.events.event_handler import EventHandler

        class SampleNotification(BaseModel):
            message: str

        notification = SampleNotification(message='testing')
        event_name = EventHandler.convert_model_to_event_name(notification)

        assert event_name == "SAMPLE_NOTIFICATION"
        ```

        Returns
        -------
        str
            Standard event name in snake_case upper letters.
        """
        model_name: str = model.__class__.__name__
        return _pascal_to_snake_pattern.sub(r'_\1', model_name).upper()

    @staticmethod
    def build_events_from_models(models: list[AnyModel], event_source: str, metadata: dict[str, Any] | None = None,
                                 correlation_id: str = '') -> list[Event]:
        """Converts a Pydantic model into a standard event.

        Parameters
        ----------
        models : list[AnyModel]
            List of Pydantic models to convert into events.
        event_source : str
            Event source name to inject into event metadata.
        metadata : dict[str, Any] | None, optional
            Additional metadata to inject, by default None
        correlation_id : str, optional
            Correlation ID to use in event metadata. If not provided, we generate one using UUID4.


        # Examples

        Building standard events from a list of models

        ```python
        from pydantic import BaseModel
        from product.stream_processor.integrations.events.event_handler import EventHandler

        class SampleNotification(BaseModel):
            message: str

        notification = SampleNotification(message='testing')
        event_source = "myorg.product.product_change_stream"
        events = EventHandler.build_events_from_models(models=[notification], event_source=event_source)

        event = events[0]

        assert event.event_source == event_source
        assert event.data == notification
        ```

        Returns
        -------
        list[Event]
            List of events created from model ready to be emitted.
        """
        metadata = metadata or {}
        correlation_id = correlation_id or f'{uuid4()}'

        events: list[Event] = []

        for model in models:
            event_name = EventHandler.extract_event_name_from_model(model=model)
            event_version = getattr(model, '__version__', DEFAULT_EVENT_VERSION)  # defaults to v1

            events.append(
                Event(
                    data=model, metadata=EventMetadata(event_name=event_name, event_source=event_source, event_version=event_version,
                                                       correlation_id=correlation_id, **metadata)))

        return events
