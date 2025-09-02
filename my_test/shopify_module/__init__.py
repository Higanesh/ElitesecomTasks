# __init__.py
from .create_module import (
    create_customer,
    create_order,
    create_product,
    create_manual_collection,
    create_smart_collection
    )

__all__ = ["create_customer", "create_order", "create_product", "create_manual_collection", "create_smart_collection"]
