from product.stream_processor.dal.events.base import chunk_from_list


def test_chunk_from_list_returns_empty_list_when_list_is_empty():
    # GIVEN an empty list of items and a chunk size of 3
    list_of_items = []
    chunk_size = 3
    expected_chunk = []

    # WHEN we call chunk_from_list
    actual_chunk = chunk_from_list(list_of_items, chunk_size)

    # THEN we get an empty chunk
    assert actual_chunk == expected_chunk


def test_chunk_from_list_returns_single_chunk_when_list_size_is_less_than_chunk_size():
    # GIVEN a list of items and a chunk size of 3
    list_of_items = [1, 2, 3]
    chunk_size = 3
    expected_chunk = [1, 2, 3]

    # WHEN we call chunk_from_list
    actual_chunk = next(chunk_from_list(list_of_items, chunk_size))

    # THEN we get a chunk of the same size as the list
    assert actual_chunk == expected_chunk
    assert len(actual_chunk) == len(expected_chunk)
    assert len(actual_chunk) == len(list_of_items)


def test_chunk_from_list_returns_multiple_chunks_when_list_size_is_greater_than_chunk_size():
    # GIVEN a list of items and a chunk size of 3
    list_of_items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    chunk_size = 3
    expected_chunks = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10]]

    # WHEN we call chunk_from_list
    actual_chunks = list(chunk_from_list(list_of_items, chunk_size))

    # THEN we get a chunk of the same size as the list
    assert actual_chunks == expected_chunks
