import balder
import balderhub.heart.lib.scenario_features

from balderhub.ble.lib.scenario_features import BleDeviceConfig
from balderhub.ble.lib.scenario_features.gatt import GattControllerFeature, GattHeartRateServiceFeature


class BpmValueReaderFeature(balderhub.heart.lib.scenario_features.BpmValueReaderFeature):
    """
    Setup Level feature implementation of the ``balderhub.heart.lib.scenario_features.BpmValueReaderFeature`` while
    reading the values over BLE
    """
    controller = GattControllerFeature()

    class DUT(balder.VDevice):
        """device under test specifying the HRM profile"""
        config = BleDeviceConfig()
        hrs = GattHeartRateServiceFeature()

    @property
    def timeout_to_wait_for_new_message(self):
        """
        Maximum time to wait for a new BLE message
        """
        return 3

    def prepare(self):
        self.controller.connect(self.DUT.config.mac_address, pair_on_connect=True)
        self.controller.start_notify(self.DUT.hrs.MeasurementCharacteristic)

    def read_last_bpm_value(self):

        msg = self.controller.wait_for_a_new_message_of(
            self.DUT.hrs.MeasurementCharacteristic,
            timeout=self.timeout_to_wait_for_new_message
        )
        return msg.bpm

    def cleanup(self):
        self.controller.cancel_notify(self.DUT.hrs.MeasurementCharacteristic)
        self.controller.unpair()
