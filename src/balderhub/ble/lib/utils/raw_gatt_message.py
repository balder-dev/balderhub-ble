from .base_gatt_message import BaseGattMessage


class RawGattMessage(BaseGattMessage):
    """Raw GATT message without any interpretation"""
    min_allowed_length_bytes = 0
    max_allowed_length_bytes = None
