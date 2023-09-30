from uuid import UUID


def validate_product_id(product_id: str) -> str:
    try:
        UUID(product_id, version=4)
    except Exception as exc:
        raise ValueError(str(exc)) from exc
    return product_id
