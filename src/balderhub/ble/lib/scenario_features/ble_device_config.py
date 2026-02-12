import balder


class BleDeviceConfig(balder.Feature):
    """general scenario level feature for a BLE device"""

    @property
    def mac_address(self) -> str:
        """the device's MAC address"""
        raise NotImplementedError()
