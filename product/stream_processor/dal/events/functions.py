import re
from typing import Any, Generator, Sequence, TypeVar
from uuid import uuid4

from product.stream_processor.dal.events.constants import DEFAULT_EVENT_VERSION
from product.stream_processor.dal.events.models.input import AnyModel, Event, EventMetadata

T = TypeVar('T')

_exclude_underscores = r'(?!^)(?<!_)'
_pascal_case = r'[A-Z][a-z]+'
_followed_by_lower_case_or_digit = r'(?<=[a-z0-9])[A-Z])'  # V1ProductNotification
_or = r'|'
_pascal_to_snake_pattern = re.compile(rf'({_exclude_underscores}{_pascal_case}{_or}{_followed_by_lower_case_or_digit}')


def convert_model_to_event_name(model_name: str) -> str:
    """ Convert ModelName (pascal) to MODEL_NAME (snake, uppercase)"""
    return _pascal_to_snake_pattern.sub(r'_\1', model_name).upper()


def build_events_from_models(models: Sequence[AnyModel], event_source: str, metadata: dict[str, Any] | None = None,
                             correlation_id: str = '') -> list[Event]:
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
    for idx in range(0, len(events), max_items):  # start, stop, step
        # slice the first 10 items, then the next 10 items starting from the index
        yield from [events[idx:idx + max_items]]
