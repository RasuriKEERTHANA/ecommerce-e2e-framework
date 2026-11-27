PRODUCT_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "category", "price", "stock"],
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "category": {"type": "string"},
        "price": {"type": "number"},
        "stock": {"type": "integer"},
    },
    "additionalProperties": False,
}

LOGIN_SCHEMA = {
    "type": "object",
    "required": ["token", "user"],
    "properties": {
        "token": {"type": "string"},
        "user": {
            "type": "object",
            "required": ["id", "email", "name"],
            "properties": {
                "id": {"type": "integer"},
                "email": {"type": "string"},
                "name": {"type": "string"},
            },
            "additionalProperties": False,
        },
    },
    "additionalProperties": False,
}

CART_ITEM_SCHEMA = {
    "type": "object",
    "required": ["product_id", "name", "price", "quantity", "line_total"],
    "properties": {
        "product_id": {"type": "integer"},
        "name": {"type": "string"},
        "price": {"type": "number"},
        "quantity": {"type": "integer"},
        "line_total": {"type": "number"},
    },
    "additionalProperties": False,
}

CART_SCHEMA = {
    "type": "object",
    "required": ["items", "total"],
    "properties": {
        "items": {"type": "array", "items": CART_ITEM_SCHEMA},
        "total": {"type": "number"},
    },
    "additionalProperties": False,
}

ORDER_CREATED_SCHEMA = {
    "type": "object",
    "required": ["order_id", "total", "status"],
    "properties": {
        "order_id": {"type": "integer"},
        "total": {"type": "number"},
        "status": {"type": "string", "enum": ["confirmed"]},
    },
    "additionalProperties": False,
}

ORDER_SCHEMA = {
    "type": "object",
    "required": ["id", "total", "status", "created_at"],
    "properties": {
        "id": {"type": "integer"},
        "total": {"type": "number"},
        "status": {"type": "string"},
        "created_at": {"type": "string"},
    },
    "additionalProperties": False,
}

ERROR_SCHEMA = {
    "type": "object",
    "required": ["detail"],
}