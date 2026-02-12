import logging

import balder

from balderhub.ble.lib.scenario_features.gatt import GattBatteryServiceFeature
from balderhub.ble.lib.scenario_features.gatt.gatt_controller_feature import GattControllerFeature
from balderhub.ble.lib.scenario_features.device_information_config import DeviceInformationConfig

logger = logging.getLogger(__name__)


# TODO split up this scenario into single components to make sure that subset of tests can run even without test hw
class ScenarioBatteryService(balder.Scenario):
    """Test scenario that validates the device information service"""

    class DeviceUnderTest(balder.Device):
        """device detecting the row heart rate"""
        # _is_cnn = IsConnected()  # TODO
        config = DeviceInformationConfig()
        bat = GattBatteryServiceFeature()

    @balder.connect(DeviceUnderTest, over_connection=balder.Connection)  # pylint: disable=undefined-variable
    class Controller(balder.Device):
        """device receiving the heart rate data"""
        gatt_controller = GattControllerFeature()

    @balder.fixture('variation')
    def make_sure_that_we_are_connected(self):
        """fixture that ensures that controller is connected"""
        yield from self.Controller.gatt_controller.fixt_make_sure_to_be_connected_to(
            with_address=self.DeviceUnderTest.config.mac_address,
            restore_entry_state=True
        )

    def test_read_battery_level_once(self) -> None:
        """
        Simple test that reads the battery level once and validates that it is between 0 and 100
        """
        msg = self.Controller.gatt_controller.read(self.DeviceUnderTest.bat.BatteryLevel)
        logger.info(f'read battery level of {msg.level_percent}%')
        assert 0 <= msg.level_percent <= 100, \
            f"battery level needs to be between 0 and 100, is {msg.level_percent} (raw data: {msg.raw_data})"
