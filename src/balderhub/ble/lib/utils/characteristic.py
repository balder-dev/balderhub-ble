import uuid
import dataclasses

from balderhub.ble.lib.utils.base_gatt_message import BaseGattMessage
from balderhub.ble.lib.utils.raw_gatt_message import RawGattMessage
from balderhub.ble.lib.utils.characteristic_property import CharacteristicProperty
from balderhub.ble.lib.utils.characteristic_security import CharacteristicSecurity


@dataclasses.dataclass
class Characteristic:
    """Base data class for describing a BLE GATT characteristic"""
    uuid: uuid.UUID
    name: str
    optional: bool = False
    mandatory_properties: list[CharacteristicProperty] = dataclasses.field(default_factory=list)
    optional_properties: list[CharacteristicProperty] = dataclasses.field(default_factory=list)
    security: list[CharacteristicSecurity] = CharacteristicSecurity.NONE
    message_type: type[BaseGattMessage] = RawGattMessage

    def __hash__(self):
        return hash(self.uuid)

    def __repr__(self):
        return f"Characteristic<{self.name}({self.uuid})>"
