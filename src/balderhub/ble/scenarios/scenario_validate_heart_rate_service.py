from __future__ import annotations
import logging
import time

import balder

from balderhub.ble.lib.scenario_features import DeviceInformationConfig
from balderhub.ble.lib.scenario_features.gatt.gatt_controller_feature import GattControllerFeature
from balderhub.ble.lib.scenario_features.gatt.gatt_heart_rate_service_feature import GattHeartRateServiceFeature, \
    HeartRateServiceMessage
from balderhub.heart.lib.scenario_features import HeartBeatFeature, StrapDockingFeature

logger = logging.getLogger(__name__)


# TODO split up this scenario into single components to make sure that subset of tests can run even without test hw
class ScenarioHeartRateService(balder.Scenario):
    """Test scenario that validates a heart rate sensor according the definitions made from HeartRateService"""

    class Heart(balder.Device):
        """device simulating the heart beat"""
        heart = HeartBeatFeature()

    @balder.connect(Heart, over_connection=balder.Connection)  # pylint: disable=undefined-variable
    class HeartRateSensor(balder.Device):
        """device detecting the row heart rate"""
        # _is_cnn = IsConnected()  # TODO
        config = DeviceInformationConfig()
        hrs = GattHeartRateServiceFeature()
        strap = StrapDockingFeature()

    @balder.connect(HeartRateSensor, over_connection=balder.Connection)  # pylint: disable=undefined-variable
    class HeartRateHost(balder.Device):
        """device receiving the heart rate data"""
        gatt_controller = GattControllerFeature()

    @property
    def active_characteristic(self):
        """
        :return: helper property for getting the Measurement characteristic
        """
        return self.HeartRateSensor.hrs.MeasurementCharacteristic

    @balder.fixture('variation')
    def make_sure_that_we_are_connected(self):
        """fixture that ensures that controller is connected"""
        yield from self.HeartRateHost.gatt_controller.fixt_make_sure_to_be_connected_to(
            with_address=self.HeartRateSensor.config.mac_address,
            restore_entry_state=True
        )

    @balder.fixture('testcase')
    def start_notification(self):
        """
        :return: register the notification for the measurement characteristic
        """
        self.HeartRateHost.gatt_controller.start_notify(self.active_characteristic)
        yield
        self.HeartRateHost.gatt_controller.cancel_notify(self.active_characteristic)

    def test_validate_heart_rate(self):
        """
        Simple test that validates the heart beats sent by the sensor
        """
        self.Heart.heart.start(60)

        logger.info("wait to get first data package")
        first_msg: HeartRateServiceMessage = self.HeartRateHost.gatt_controller.wait_for_first_notification_of(
            self.active_characteristic, timeout=10
        )
        logger.info(f"received data {first_msg.bpm}")
        assert first_msg.bpm == 60, f"received {first_msg.bpm} bpm"

    def test_sensorcontact_bit(self):
        """test that validates that the sensor contact support and status bit are handled correctly"""
        self.Heart.heart.start(60)

        first_msg: HeartRateServiceMessage = self.HeartRateHost.gatt_controller.wait_for_first_notification_of(
            self.active_characteristic
        )
        if not first_msg.bit_sensor_contact_support:
            assert first_msg.bit_sensor_contact_status is False
            return

        assert first_msg.bit_sensor_contact_status is True

        self.HeartRateSensor.strap.put_off()
        time.sleep(2)
        next_msg: HeartRateServiceMessage = self.HeartRateHost.gatt_controller.wait_for_a_new_message_of(
            self.active_characteristic
        )

        assert next_msg.bit_sensor_contact_support is True
        assert next_msg.bit_sensor_contact_status is False

        self.HeartRateSensor.strap.put_on()
        time.sleep(2)
        next_msg: HeartRateServiceMessage = self.HeartRateHost.gatt_controller.wait_for_a_new_message_of(
            self.active_characteristic
        )

        assert next_msg.bit_sensor_contact_support is True
        assert next_msg.bit_sensor_contact_status is True
