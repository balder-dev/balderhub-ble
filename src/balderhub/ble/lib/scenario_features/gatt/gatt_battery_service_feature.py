import uuid

from .base_gatt_service_feature import BaseGattServiceFeature
from ...utils import Characteristic, CharacteristicProperty, CharacteristicSecurity
from ...utils.base_gatt_message import BaseGattMessage


class BatteryLevelMessage(BaseGattMessage):
    """
    GATT Message for :class:`GattBatteryServiceFeature.BatteryLevel`
    """
    min_allowed_length_bytes = 1
    max_allowed_length_bytes = None

    @property
    def level_percent(self) -> int:
        """returns the level in percent (should be between 0 and 100)"""
        return int.from_bytes(self.raw_data, self.BYTE_ORDER)


class GattBatteryServiceFeature(BaseGattServiceFeature):
    """
    GATT Service Feature for Heart-Rate-Service
    """
    # TODO also implement stuff for other characteristics!!!

    class BatteryLevel(Characteristic):
        """characteristic representing the Battery Level"""
        uuid = uuid.UUID('00002a19-0000-1000-8000-00805f9b34fb')
        name = 'Battery Level'
        optional = True
        mandatory_properties = [CharacteristicProperty.READ]
        security = CharacteristicSecurity.NONE
        message_type = BatteryLevelMessage
