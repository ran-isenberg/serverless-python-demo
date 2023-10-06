from uuid import UUID


def validate_product_id(product_id: str) -> str:
    """Validates Product IDs are valid UUIDs

    Parameters
    ----------
    product_id : str
        Product ID as a string

    Returns
    -------
    str
        Validated product ID value

    Raises
    ------
    ValueError
        When a product ID doesn't conform with the UUID spec.
    """
    try:
        UUID(product_id, version=4)
    except Exception as exc:  # pragma: no cover
        raise ValueError(str(exc)) from exc
    return product_id
