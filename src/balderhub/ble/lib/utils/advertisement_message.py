import dataclasses
from typing import Union

from balderhub.ble.lib.utils.ble_device_information import BLEDeviceInformation


@dataclasses.dataclass
class AdvertisementMessage:
    """Base data class for BLE advertisement messages"""
    timestamp: float
    device: BLEDeviceInformation
    local_name: Union[str, None]
    manufacturer_data: dict[int, bytes]
    rssi: int
    service_data: dict[str, bytes]
    service_uuids: list[str]
