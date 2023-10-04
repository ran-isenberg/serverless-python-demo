"""Standalone functions related to events integration. These are reused in more than one location, and tested separately"""

import re
from typing import Any, Generator, Sequence, TypeVar
from uuid import uuid4

from product.stream_processor.integrations.events.constants import DEFAULT_EVENT_VERSION
from product.stream_processor.integrations.events.models.input import AnyModel, Event, EventMetadata

T = TypeVar('T')
"""Generic type for a list of events"""

_exclude_underscores = r'(?!^)(?<!_)'
_pascal_case = r'[A-Z][a-z]+'
_followed_by_lower_case_or_digit = r'(?<=[a-z0-9])[A-Z])'  # V1ProductNotification
_or = r'|'
_pascal_to_snake_pattern = re.compile(rf'({_exclude_underscores}{_pascal_case}{_or}{_followed_by_lower_case_or_digit}')


def convert_model_to_event_name(model_name: str) -> str:
    """Derives a standard event name from the name of the model.

    It uses snake_case in uppercase letters, e.g., `ProductNotification` -> `PRODUCT_NOTIFICATION`.

    Parameters
    ----------
    model_name : str
        Name of the model to derive from.

    # Examples

    ```python
    from pydantic import BaseModel

    class SampleNotification(BaseModel):
        message: str

    notification = SampleNotification(message='testing')
    event_name = convert_model_to_event_name(notification.__class__.__name__)

    assert event_name == "SAMPLE_NOTIFICATION"
    ```

    Returns
    -------
    str
        Standard event name in snake_case upper letters.
    """
    return _pascal_to_snake_pattern.sub(r'_\1', model_name).upper()


def build_events_from_models(models: Sequence[AnyModel], event_source: str, metadata: dict[str, Any] | None = None,
                             correlation_id: str = '') -> list[Event]:
    """Converts a Pydantic model into a standard event.

    Parameters
    ----------
    models : Sequence[AnyModel]
        List of Pydantic models to convert into events.
    event_source : str
        Event source name to inject into event metadata.
    metadata : dict[str, Any] | None, optional
        Additional metadata to inject, by default None
    correlation_id : str, optional
        Correlation ID to use in event metadata. If not provided, we generate one using UUID4.

    Returns
    -------
    list[Event]
        List of events created from model ready to be emitted.
    """
    metadata = metadata or {}
    correlation_id = correlation_id or f'{uuid4()}'

    events: list[Event] = []

    for model in models:
        event_name = convert_model_to_event_name(model_name=model.__class__.__name__)
        event_version = getattr(model, '__version__', DEFAULT_EVENT_VERSION)  # defaults to v1

        events.append(
            Event(
                data=model, metadata=EventMetadata(event_name=event_name, event_source=event_source, event_version=event_version,
                                                   correlation_id=correlation_id, **metadata)))

    return events


def chunk_from_list(events: list[T], max_items: int) -> Generator[list[T], None, None]:
    """Slices a list of items into a generator, respecting the max number of items.

    Parameters
    ----------
    events : list[T]
        List of events to slice.
    max_items : int
        Maximum number of items per chunk.

    Yields
    ------
    Generator[list[T], None, None]
        Generator containing batches of events with maximum number of items requested.
    """
    for idx in range(0, len(events), max_items):  # start, stop, step
        # slice the first 10 items, then the next 10 items starting from the index
        yield from [events[idx:idx + max_items]]
