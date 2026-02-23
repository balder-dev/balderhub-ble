import time

import balder
import balderhub.heart.lib.scenario_features

from balderhub.ble.lib.scenario_features import BleDeviceConfig
from balderhub.ble.lib.scenario_features.gatt import GattControllerFeature, GattHeartRateServiceFeature


class RRValueReaderFeature(balderhub.heart.lib.scenario_features.RRValueReaderFeature):
    """
    Setup Level feature implementation of the ``balderhub.heart.lib.scenario_features.RRValueReaderFeature`` while
    reading the values over BLE
    """
    controller = GattControllerFeature()

    class DUT(balder.VDevice):
        """device under test specifying the HRM profile"""
        config = BleDeviceConfig()
        hrs = GattHeartRateServiceFeature()

    @property
    def timeout_to_wait_for_new_rr_value_sec(self):
        """maximum time to wait for a RR value"""
        return 3

    def prepare(self):
        self.controller.connect(self.DUT.config.mac_address, pair_on_connect=True)
        self.controller.start_notify(self.DUT.hrs.MeasurementCharacteristic)

    def read_last_rr_value_in_sec(self) -> float:
        start_time = time.perf_counter()
        while time.perf_counter() - start_time < self.timeout_to_wait_for_new_rr_value_sec:
            msg = self.controller.wait_for_a_new_message_of(
                self.DUT.hrs.MeasurementCharacteristic,
                timeout=self.timeout_to_wait_for_new_rr_value_sec - (time.perf_counter() - start_time)
            )
            if msg.rr_values:
                return msg.rr_values[-1]
        raise TimeoutError(f'did not received more than one heart beat messages with an RR-Value within '
                           f'{self.timeout_to_wait_for_new_rr_value_sec} seconds')

    def cleanup(self):
        self.controller.cancel_notify(self.DUT.hrs.MeasurementCharacteristic)
        self.controller.unpair()
