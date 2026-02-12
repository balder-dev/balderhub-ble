import logging

import balder

from balderhub.ble.lib.scenario_features.gatt import GattDeviceInformationServiceFeature
from balderhub.ble.lib.scenario_features.gatt.gatt_controller_feature import GattControllerFeature
from balderhub.ble.lib.scenario_features.device_information_config import DeviceInformationConfig
from balderhub.ble.lib.utils import Characteristic

logger = logging.getLogger(__name__)


# TODO split up this scenario into single components to make sure that subset of tests can run even without test hw
class ScenarioDeviceInformationService(balder.Scenario):
    """Test scenario that validates the device information service"""

    class DeviceUnderTest(balder.Device):
        """device detecting the row heart rate"""
        # _is_cnn = IsConnected()  # TODO
        config = DeviceInformationConfig()
        gatt = GattDeviceInformationServiceFeature()

    @balder.connect(DeviceUnderTest, over_connection=balder.Connection)  # pylint: disable=undefined-variable
    class Controller(balder.Device):
        """device receiving the heart rate data"""
        gatt_controller = GattControllerFeature()

    @balder.fixture('variation')
    def make_sure_that_we_are_connected(self):
        """fixture that ensures that controller is connected"""
        yield from self.Controller.gatt_controller.fixt_make_sure_to_be_connected_to(
            with_address=self.DeviceUnderTest.config.mac_address
        )

    @balder.parametrize('config_and_char', [
        ('manufacturer_name_string', DeviceUnderTest.gatt.ManufacturerCharacteristic),
        ('model_number_string', DeviceUnderTest.gatt.ModelNumberCharacteristic),
        ('serial_number_string', DeviceUnderTest.gatt.SerialNumberCharacteristic),
        ('hardware_revision_string', DeviceUnderTest.gatt.HardwareRevisionCharacteristic),
        ('firmware_revision_string', DeviceUnderTest.gatt.FirmwareRevisionCharacteristic),
        ('software_revision_string', DeviceUnderTest.gatt.SoftwareRevisionCharacteristic),
        ('system_id', DeviceUnderTest.gatt.SystemId),
        ('iee11073_20601_regulatory_cert_data_list', DeviceUnderTest.gatt.IeeeRegulatoryCertDataListCharacteristic),
        ('udi_for_medical', DeviceUnderTest.gatt.UdiForMedicalDevicesCharacteristic)
    ])
    def test_value(self, config_and_char: tuple[str, type[Characteristic]]):
        """
        This test will be executed for every existing characteristic in the Device-Information Service and validates if
        it response with the correct values. In case the characteristic is marked as non-active (see properties in
        :class:`balderhub.ble.lib.scenario_features.DeviceInformationConfig`), it will check that it raises an
        exception that the characteristic was not found.

        :param config_and_char: parametrized configuration with the property name as first element and the
                                characteristic as second
        """
        config_prop_name, characteristic_type = config_and_char

        expected_val = getattr(self.DeviceUnderTest.config, config_prop_name)
        if expected_val is not None:
            logger.info(f'validate that `{config_prop_name}` is returned correctly')
            data = self.Controller.gatt_controller.read(characteristic_type).raw_data
            logger.info(f'received `{data}` (expected `{expected_val}`)')
            assert data == expected_val, f"received `{data}` for `{config_prop_name}` (expected `{expected_val}`)"

        else:
            logger.info(f'no `{config_prop_name}` characteristic expected -> check for error while reading')
            try:
                data = self.Controller.gatt_controller.read(characteristic_type).raw_data
                assert False, \
                    f'was able to receive a value `{data}` for `{config_prop_name}`, but no value was expected'
            except self.Controller.gatt_controller.CharacteristicNotFoundError as exc:
                logger.info(f'error {exc} caught - check successful')

    def test_pnp_id(self):
        """
        Special test for the PNP-ID object.

        It validates if it response with the correct values. In case the characteristic is marked as non-active
        (see property :meth:`balderhub.ble.lib.scenario_features.DeviceInformationConfig.pnp_id`),
        it will check that it raises an exception that the characteristic was not found.
        """
        expected_val = self.DeviceUnderTest.config.pnp_id
        if expected_val is not None:
            logger.info('validate that `pnp_id` is returned correctly')
            data = self.Controller.gatt_controller.read(self.DeviceUnderTest.gatt.PnpIdCharacteristic).raw_data
            logger.info(f'received `{data}` for `pnp` (expected `{expected_val}`)')
            assert data == expected_val.to_bytes(), \
                f"received `{data}` for `pnp` (expected `{expected_val}` - as bytes: {expected_val.to_bytes()})"

        else:
            logger.info('no `pnp_id` characteristic expected -> check for error while reading')
            try:
                data = self.Controller.gatt_controller.read(self.DeviceUnderTest.gatt.PnpIdCharacteristic).raw_data
                assert False, f'was able to receive a value `{data}` for `pnp`, but no value was expected'
            except self.Controller.gatt_controller.CharacteristicNotFoundError as exc:
                logger.info(f'error {exc} caught - check successful')
