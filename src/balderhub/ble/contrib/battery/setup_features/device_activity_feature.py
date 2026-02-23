import balder
import balderhub.battery.lib.scenario_features
from balderhub.ble.lib.scenario_features.ble_device_config import BleDeviceConfig
from balderhub.ble.lib.setup_features import BleakAdvertisementObserverFeature


class DeviceActivityFeature(balderhub.battery.lib.scenario_features.DeviceActivityFeature):
    """Setup Level implementation for returning the activity of an ANT device by checking if it sends messages"""

    ble_advertise = BleakAdvertisementObserverFeature()

    class DUT(balder.VDevice):
        """vdevice describing the device under test"""
        config = BleDeviceConfig()

    @property
    def timeout_to_wait_for_advertisements_sec(self) -> float:
        """
        :return: timeout to use to wait for advertisements
        """
        return 10

    def is_active(self) -> bool:
        if not self.ble_advertise.is_alive():
            self.ble_advertise.start_observer()  # TODO move in prepare/cleanup methods

        try:
            self.ble_advertise.wait_for_new_advertisement(
                self.DUT.config.mac_address,
                timeout_sec=self.timeout_to_wait_for_advertisements_sec
            )
            return True
        except TimeoutError:
            return False
