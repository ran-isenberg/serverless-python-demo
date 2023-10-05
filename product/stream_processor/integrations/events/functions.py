"""Standalone functions related to events integration. These are reused in more than one location, and tested separately"""

from typing import Generator, TypeVar

T = TypeVar('T')
"""Generic type for a list of events"""


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
