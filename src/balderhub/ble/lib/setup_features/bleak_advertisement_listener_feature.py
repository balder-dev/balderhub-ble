import platform
import time
from typing import Union, Optional
import logging

import queue

from bleak import BleakScanner, AdvertisementData, BLEDevice

import balderhub.ble.lib.scenario_features
from balderhub.ble.lib.utils.advertisement_message import AdvertisementMessage
from balderhub.ble.lib.utils.ble_device_information import BLEDeviceInformation
from balderhub.ble.lib.utils.async_manager_thread import AsyncManagerThread

logger = logging.getLogger(__name__)


class BleakAdvertisementObserverFeature(balderhub.ble.lib.scenario_features.AdvertisementObserverFeature):
    """
    Feature implementation with bleak for :class:`AdvertisementObserverFeature`

    .. note::
        This feature uses bleak as backend. Bleak does not receive every Advertisement. Consider that in mind, when
        using this feature.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._start_time = None

        self._advertisement_queue = queue.Queue()

        self._already_read_advertisements: list[AdvertisementMessage] = []

        self._thread: Union[AsyncManagerThread, None] = None

        self._bleak_scanner: Union[BleakScanner, None] = None

        if platform.system() != 'Linux':
            # TODO provide support for this
            raise RuntimeError('the Bleak feature is not supported on your operating system')

    @property
    def adapter(self) -> Union[str, None]:
        """
        :return: the BLE adapter to use, or None if no specific adapter should be selected (auto use)
        """
        return None

    async def _detection_callback(self, device, adv_data):
        logger.debug(f'received a new advertisement {adv_data} from device {device}')
        self._advertisement_queue.put((time.perf_counter(), device, adv_data))

    async def _async_create_bleak_scanner(self):
        self._bleak_scanner = BleakScanner(
            detection_callback=self._detection_callback,  # TODO should we save it like that?
            adapter=self.adapter
        )
        await self._bleak_scanner.start()
        self._start_time = time.perf_counter()

    async def _async_stop_scanner(self):
        await self._bleak_scanner.stop()

    def start_observer(self):
        if self._thread is not None:
            raise ValueError('observer is already active, can not start it again')
        self._already_read_advertisements = []
        self._thread = AsyncManagerThread()
        self._thread.start()

        self._thread.run_in_async_thread_and_wait_for_result(
            self._async_create_bleak_scanner
        )

    def is_alive(self):
        return self._thread is not None and self._thread.is_alive()

    def shutdown_observer(self, timeout=10):
        if self._thread is None:
            return

        self._thread.run_in_async_thread_and_wait_for_result(
            self._async_stop_scanner
        )

        logger.debug('stop internal async thread')
        self._thread.stop_and_wait_for_thread(timeout=timeout)
        self._thread = None

    def _read_all_new_advertisement_from_queue(self) -> list[AdvertisementMessage]:
        new_ones = []
        while not self._advertisement_queue.empty():
            data: tuple[float, BLEDevice, AdvertisementData] = self._advertisement_queue.get(block=False, timeout=None)
            timestamp, device, msg = data

            device = BLEDeviceInformation(
                address=device.address,
                name=device.name
            )

            new_ones.append(
                AdvertisementMessage(
                    timestamp=timestamp,
                    device=device,
                    local_name=msg.local_name,
                    manufacturer_data=msg.manufacturer_data,
                    rssi=msg.rssi,
                    service_data=msg.service_data,
                    service_uuids=msg.service_uuids
                )
            )
        self._already_read_advertisements.extend(new_ones)
        return new_ones

    def wait_for_new_advertisement(self, with_mac: Optional[str] = None, timeout_sec=10):
        start_time = time.perf_counter()
        while (time.perf_counter() - start_time) < timeout_sec:
            new_messages = self._read_all_new_advertisement_from_queue()
            if len(new_messages) > 0:

                filtered_msgs = new_messages \
                    if with_mac is None \
                    else [msg for msg in new_messages if msg.device.address == with_mac]

                if len(filtered_msgs) > 0:
                    return filtered_msgs[0]
            else:
                time.sleep(0.01)

        raise TimeoutError(f'no new advertisement received within {timeout_sec} seconds')

    def __validate_time(self, value: float, variable_name: str):
        if not isinstance(value, float):
            raise TypeError(f'time value `{variable_name}` needs to be an float')
        if value < self._start_time:
            raise ValueError(f'{variable_name} is less than or equal to start time - can not be the case')
        if value > time.perf_counter():
            raise ValueError('{variable_name} is in the future - can not be the case')

    def filter_advertisements(
            self,
            by_mac: Optional[str] = None,
            from_start_time: Optional[float] = None,
            till_end_time: Optional[float] = None
    ) -> list[AdvertisementMessage]:
        # read all advertisements from queu
        self._read_all_new_advertisement_from_queue()

        all_msgs = self._already_read_advertisements
        if by_mac is not None:
            all_msgs = [msg for msg in all_msgs if msg.device.address == by_mac]

        if from_start_time is not None:
            self.__validate_time(from_start_time, 'from_start_time')
            all_msgs = [msg for msg in all_msgs if msg.timestamp >= from_start_time]

        if till_end_time is not None:
            self.__validate_time(till_end_time, 'till_end_time')

            if from_start_time:
                if from_start_time > till_end_time:
                    raise ValueError('start time can not be higher than end time')

            all_msgs = [msg for msg in all_msgs if msg.timestamp <= till_end_time]

        return all_msgs
