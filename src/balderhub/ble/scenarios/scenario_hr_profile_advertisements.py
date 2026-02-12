import logging
import time

import balder

from balderhub.ble.lib.scenario_features import BleDeviceConfig
from balderhub.ble.lib.scenario_features.advertisement_observer_feature import AdvertisementObserverFeature
from balderhub.ble.lib.scenario_features.gatt.gatt_heart_rate_profile_feature import GattHeartRateProfileFeature
from balderhub.heart.lib.scenario_features import HeartBeatFeature
from balderhub.heart.lib.scenario_features.strap_docking_feature import StrapDockingFeature

logger = logging.getLogger(__name__)


# TODO split up this scenario into single components to make sure that subset of tests can run even without test hw
class ScenarioHrProfileAdvertisements(balder.Scenario):
    """Test scenario that validates if heart-rate sensor with active hr-profile sends Advertisements correctly"""
    # TODO we just need to restart chip before starting a test

    # TODO this needs to be configurable
    TIMEOUT_TO_AWAKE_SEC = 20
    TIMEOUT_TO_SLEEP_SEC = 60

    class Heart(balder.Device):
        """device simulating the heart beat"""
        heart = HeartBeatFeature()

    @balder.connect(Heart, over_connection=balder.Connection)  # pylint: disable=undefined-variable
    class HeartRateSensor(balder.Device):
        """device detecting the row heart rate"""
        # _is_not_cnn = IsNotConnected()  # TODO
        # _has_no_attached_strap = HasAttachedStrap()
        config = BleDeviceConfig()
        hrs = GattHeartRateProfileFeature()
        strap = StrapDockingFeature()

    @balder.connect(HeartRateSensor, over_connection=balder.Connection)  # pylint: disable=undefined-variable
    class HeartRateHost(balder.Device):
        """device receiving the heart rate data"""
        adv_observer = AdvertisementObserverFeature()

    @balder.fixture('testcase')
    def start_observer(self):
        """starts the advertisement observer"""
        self.HeartRateHost.adv_observer.start_observer()
        yield
        self.HeartRateHost.adv_observer.shutdown_observer()

    @balder.fixture('testcase')
    def make_sure_to_stop_advertising(self, start_observer):  # pylint: disable=unused-argument
        """
        fixture that ensures that no advertisements are sent (and the device is really shut down) before entering
        the test
        """
        # TODO bleak does not receive all packages!!!
        self.HeartRateSensor.strap.put_off()
        start_time = time.perf_counter()
        while (time.perf_counter() - start_time) < self.TIMEOUT_TO_SLEEP_SEC * 3:
            try:
                if self.HeartRateHost.adv_observer.wait_for_new_advertisement(
                        with_mac=self.HeartRateSensor.config.mac_address, timeout_sec=self.TIMEOUT_TO_SLEEP_SEC
                ):
                    # there are still some messages -> continue
                    continue
            except TimeoutError:
                logger.info(
                    f'received timeout: did not received any advertisements since {self.TIMEOUT_TO_SLEEP_SEC} seconds'
                )
                return
        raise TimeoutError('still received advertisements')

    @balder.parametrize("with_heart_beat", [True, False])
    def test_is_advertising_as_soon_as_strap_attached(self, with_heart_beat):  # pylint: disable=unused-argument
        """
        This test makes sure that the DUT is advertising as soon as the strap is attached
        :param with_heart_beat: test will be executed once with heart beat and another time without active heart beat
        """
        start_time = time.perf_counter()
        try:
            adv_msgs = self.HeartRateHost.adv_observer.wait_for_new_advertisement(
                with_mac=self.HeartRateSensor.config.mac_address,
                timeout_sec=self.TIMEOUT_TO_SLEEP_SEC
            )
            assert False, f"received unexpected advertisement packages `{adv_msgs}`"
        except TimeoutError:
            logger.info('received timeout - no more advertisements detected -> continue test')

        try:
            self.HeartRateSensor.strap.put_on()
            time.sleep(self.TIMEOUT_TO_AWAKE_SEC)
            # check that we receive at least one
            all_received_advertisements = self.HeartRateHost.adv_observer.filter_advertisements(
                by_mac=self.HeartRateSensor.config.mac_address,
                from_start_time=start_time
            )
            assert len(all_received_advertisements) > 1, \
                (f"does not receive any advertising messages {self.TIMEOUT_TO_AWAKE_SEC} seconds after the strap was "
                 f"attached")
        finally:
            self.HeartRateSensor.strap.put_off()

    @balder.parametrize('strap_remains_attached', [True, False])
    def test_is_advertising_when_pulse_is_gone(self, strap_remains_attached):
        """
        This test validates if the DUT is still advertising when the pulse is gone.
        :param strap_remains_attached:  test will be executed once with strap attached and once without attached strap
        """
        try:
            self.HeartRateSensor.strap.put_on()
            time.sleep(self.TIMEOUT_TO_AWAKE_SEC)
            # check that we receive at least one
            all_received_advertisements = self.HeartRateHost.adv_observer.filter_advertisements(
                by_mac=self.HeartRateSensor.config.mac_address,
            )
            assert len(all_received_advertisements) > 1, \
                (f"does not receive any advertising messages {self.TIMEOUT_TO_AWAKE_SEC} seconds after the strap was "
                 f"attached")

            self.Heart.heart.stop()
            if not strap_remains_attached:
                self.HeartRateSensor.strap.put_off()
            filter_time = time.perf_counter()
            time.sleep(self.TIMEOUT_TO_SLEEP_SEC)
            all_received_advertisements = self.HeartRateHost.adv_observer.filter_advertisements(
                by_mac=self.HeartRateSensor.config.mac_address,
                from_start_time=filter_time
            )
            assert len(all_received_advertisements) > 1, \
                (f"does not receive any advertising messages within {self.TIMEOUT_TO_SLEEP_SEC} seconds after heart "
                 f"has stopped")

            # now it is expected that server stops sending advertisements
            filter_time = time.perf_counter()
            time.sleep(self.TIMEOUT_TO_SLEEP_SEC)
            all_received_advertisements = self.HeartRateHost.adv_observer.filter_advertisements(
                by_mac=self.HeartRateSensor.config.mac_address,
                from_start_time=filter_time
            )
            assert len(all_received_advertisements) == 0, \
                f"receive some advertisement messages after {self.TIMEOUT_TO_SLEEP_SEC} seconds after heart has stopped"

        finally:
            self.HeartRateSensor.strap.put_off()
