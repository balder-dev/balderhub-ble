from typing import Union
import time

import balder

import balderhub.ble.lib.scenario_features
import balderhub.ble.lib.scenario_features.gatt
import balderhub.ble.lib.setup_features
import balderhub.battery.lib.scenario_features


class BatteryLevelReader(balderhub.battery.lib.scenario_features.BatteryLevelReader):
    """Setup Level implementation over BLE for reading the battery level"""
    controller = balderhub.ble.lib.setup_features.BleakGattControllerFeature()

    class DUT(balder.VDevice):
        """vdevice representing the device under test that implements the ``GattBatteryServiceFeature``"""
        config = balderhub.ble.lib.scenario_features.BleDeviceConfig()
        gatt = balderhub.ble.lib.scenario_features.gatt.GattBatteryServiceFeature()

    def read_current_battery_level(self) -> Union[float, None]:

        try:
            self.controller.connect(self.DUT.config.mac_address)
            time.sleep(10)  # TODO
            return self.controller.read(self.DUT.gatt.BatteryLevel).level_percent / 100
        except ValueError as exc:
            # TODO improve
            if "unable to connect with device at address" in str(exc):
                return None
            raise exc
        finally:
            self.controller.unpair()
            #self.controller.disconnect()
