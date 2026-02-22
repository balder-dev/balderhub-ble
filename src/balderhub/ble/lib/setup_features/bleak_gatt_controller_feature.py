from typing import Union
import logging
import platform
import time
import queue

from bleak import BleakClient, BleakScanner, BleakGATTCharacteristic, BleakCharacteristicNotFoundError, BLEDevice

from ..scenario_features.gatt.gatt_controller_feature import GattControllerFeature
from ..utils import Characteristic
from ..utils.async_manager_thread import AsyncManagerThread
from ..utils.base_gatt_message import BaseGattMessageTypeT
from ..utils.ble_device_information import BLEDeviceInformation

logger = logging.getLogger(__name__)


class BleakGattControllerFeature(GattControllerFeature):
    """bleak implementation of the feature :class:`GattControllerFeature`"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._thread: Union[AsyncManagerThread, None] = None
        self._bleak_client: Union[BleakClient, None] = None

        self._active_notifications = []
        self._queues_for_notifies_of: dict[type[Characteristic], queue.Queue] = {}
        self._stored_data_of_notifies_for = {}

        if platform.system() != 'Linux':
            # TODO provide support for this
            raise RuntimeError('the Bleak feature is not supported on your operating system')

    @property
    def adapter(self) -> Union[str, None]:
        """
        :return: the BLE adapter to use, or None if no specific adapter should be selected (auto use)
        """
        return None

    @property
    def connected_address(self) -> Union[str, None]:
        if self._bleak_client is None or not self._bleak_client.is_connected:
            return None
        return self._bleak_client.address  # TODO returns UUID on mac!!

    def create_and_start_thread(self) -> None:
        """
        This method creates and starts the internal connection management thread. This method needs to be called before
        doing anything with this feature.
        """
        if self._thread is not None:
            raise ValueError('another thread object exists -> can not create a new one')
        self._thread = AsyncManagerThread()
        self._thread.start()

    def stop_and_wait_for_thread(self, timeout: float = 10):
        """
        This method stops and cleans up the internal connection management thread. This method needs to be called to
        clean up all internal resources.
        """
        if self._thread is None:
            return
        logger.debug('stop internal async thread')
        self._thread.stop_and_wait_for_thread(timeout=timeout)
        self._thread = None

    async def _async_discover(
            self,
            limit_to_address: Union[str, None],
            timeout_discover: float
    ) -> list[BLEDevice]:
        if limit_to_address:
            device = await BleakScanner.find_device_by_address(
                limit_to_address, timeout=timeout_discover, adapter=self.adapter
            )
            devices = [] if device is None else [device]
        else:
            devices = await BleakScanner.discover(timeout=timeout_discover, adapter=self.adapter)
        return devices

    def discover(
            self,
            limit_to_address: Union[str, None] = None,
            timeout_discover: float = 20
    ) -> list[BLEDeviceInformation]:
        self._queues_for_notifies_of = {}
        self._stored_data_of_notifies_for = {}
        if self._thread is None:
            self.create_and_start_thread()

        result: list[BLEDevice] = self._thread.run_in_async_thread_and_wait_for_result(
            self._async_discover, limit_to_address, timeout_discover
        )
        if len(result) == 0:
            return []
        return [BLEDeviceInformation(dev.address, dev.name) for dev in result]

    async def _async_connect(self, mac_address: str, pair_on_connect, timeout_discover, timeout_connect):
        # TODO
        device = await BleakScanner.find_device_by_address(mac_address, timeout=timeout_discover, adapter=self.adapter)
        if device is None:
            raise ValueError(f'unable to connect with device at address {mac_address}')
        self._bleak_client = BleakClient(device, pair=pair_on_connect, timeout=timeout_connect,
                                         adapter=self.adapter)  # TODO should we save it like that?
        # TODO what is with Pair=True - we do not want this always (need to check when pairing is necessary)
        await self._bleak_client.connect()

    def connect(self, mac_address: str, pair_on_connect: bool = False, timeout_discover=20, timeout_connect=60):
        self._queues_for_notifies_of = {}
        self._stored_data_of_notifies_for = {}
        if self._thread is None:
            self.create_and_start_thread()

        self._thread.run_in_async_thread_and_wait_for_result(
            self._async_connect, mac_address, pair_on_connect, timeout_discover, timeout_connect
        )

    async def _async_unpair(self):
        if self._bleak_client is None:
            return
        await self._bleak_client.unpair()

    def unpair(self):
        self._thread.run_in_async_thread_and_wait_for_result(self._async_unpair)

    async def _async_disconnect(self):
        if self._bleak_client is None:
            return
        await self._bleak_client.disconnect()
        self._bleak_client = None

    def disconnect(self, timeout=10):
        start_time = time.perf_counter()
        self._thread.run_in_async_thread_and_wait_for_result(self._async_disconnect)
        self.stop_and_wait_for_thread(timeout=timeout - (time.perf_counter() - start_time))

        # read all queues
        for cur_characteristic in self._queues_for_notifies_of.keys():
            self.get_all_notify_messages_of(cur_characteristic)
        self._queues_for_notifies_of = {}

    async def _async_read(self, characteristic: type[Characteristic]):
        try:
            return await self._bleak_client.read_gatt_char(characteristic.uuid)
        except BleakCharacteristicNotFoundError as exc:
            raise self.CharacteristicNotFoundError from exc

    def read(self, characteristic: type[Characteristic]) -> BaseGattMessageTypeT:
        raw_data = self._thread.run_in_async_thread_and_wait_for_result(self._async_read, characteristic)
        return characteristic.message_type.from_bytearray(raw_data)

    async def _async_write(self, characteristic: type[Characteristic], value: bytearray, response: bool):
        try:
            return await self._bleak_client.write_gatt_char(characteristic.uuid, value, response)
        except BleakCharacteristicNotFoundError as exc:
            raise self.CharacteristicNotFoundError from exc

    def write(
            self,
            characteristic: type[Characteristic],
            value: bytearray
    ):
        self._thread.run_in_async_thread_and_wait_for_result(self._async_write, characteristic, value, False)

    def write_without_response(
            self,
            characteristic: type[Characteristic],
            value: bytearray
    ) -> None:
        return self._thread.run_in_async_thread_and_wait_for_result(self._async_write, characteristic, value, True)

    async def _async_start_notify(
            self,
            characteristic: type[Characteristic]
    ):
        def callback(sender, data):
            logger.info(f"received {data} from {sender}")
            # TODO what's about `sender`
            self._queues_for_notifies_of[characteristic].put((sender, data))
            # TODO send data by Queue

        await self._bleak_client.start_notify(characteristic.uuid, callback)

    def start_notify(
            self,
            characteristic: type[Characteristic]
    ):
        self._queues_for_notifies_of[characteristic] = queue.Queue()
        if characteristic not in self._stored_data_of_notifies_for:
            self._stored_data_of_notifies_for[characteristic] = []
        try:
            self._thread.run_in_async_thread_and_wait_for_result(self._async_start_notify, characteristic)
            self._active_notifications.append(characteristic)
        except BleakCharacteristicNotFoundError as exc:
            # TODO should we clean up `_stored_data_of_notifies_for` and `_queues_for_notifies_of`
            raise self.CharacteristicNotFoundError from exc

    def is_notification_active(self, characteristic: type[Characteristic]) -> bool:
        return characteristic in self._active_notifications

    async def _async_cancel_notify(self, characteristic: Characteristic):
        await self._bleak_client.stop_notify(characteristic.uuid)
        if characteristic in self._active_notifications:
            self._active_notifications.remove(characteristic)

    def cancel_notify(
            self,
            characteristic: Characteristic
    ):
        try:
            self._thread.run_in_async_thread_and_wait_for_result(self._async_cancel_notify, characteristic)
        except BleakCharacteristicNotFoundError as exc:
            # TODO should we clean up `_stored_data_of_notifies_for` and `_queues_for_notifies_of`
            raise self.CharacteristicNotFoundError from exc

    def _get_next_notify_message_from_queue(
            self,
            characteristic: type[Characteristic],
            timeout: Union[float, None] = 10
    ) -> Union[tuple[BleakGATTCharacteristic, bytearray], None]:
        if characteristic not in self._queues_for_notifies_of:
            return None
        try:
            sender, msg = self._queues_for_notifies_of[characteristic].get(block=timeout is not None, timeout=timeout)
            self._stored_data_of_notifies_for[characteristic].append((sender, msg))
            return sender, msg
        except queue.Empty:
            return None

    def get_all_notify_messages_of(
            self,
            characteristic: type[Characteristic]
    ) -> list[BaseGattMessageTypeT]:
        if characteristic not in (list(self._queues_for_notifies_of) + list(self._stored_data_of_notifies_for)):
            raise KeyError(f'no notify was registered for characteristic {characteristic}')
        # check if there are some new messages
        if characteristic in self._stored_data_of_notifies_for:
            while True:
                if not self._get_next_notify_message_from_queue(characteristic, timeout=None):
                    break
        return [
            characteristic.message_type.from_bytearray(m)
            for _, m in self._stored_data_of_notifies_for[characteristic]
        ]

    def wait_for_first_notification_of(
            self,
            characteristic: type[Characteristic],
            timeout: float = 10
    ) -> BaseGattMessageTypeT:
        start_time = time.perf_counter()
        msgs = self.get_all_notify_messages_of(characteristic)
        if len(msgs) > 0:
            return msgs[0]
        first_entry = self._get_next_notify_message_from_queue(characteristic,
                                                               timeout=timeout - (time.perf_counter() - start_time))
        if first_entry is None:
            raise TimeoutError(f'no values received within {timeout} seconds')
        return characteristic.message_type.from_bytearray(first_entry[1])

    def wait_for_a_new_message_of(
            self,
            characteristic: type[Characteristic],
            timeout: float = 10
    ) -> BaseGattMessageTypeT:
        start_time = time.perf_counter()
        # load all prevoius received messages from queue
        self.get_all_notify_messages_of(characteristic)
        first_entry = self._get_next_notify_message_from_queue(characteristic,
                                                               timeout=timeout - (time.perf_counter() - start_time))
        if first_entry is None:
            raise TimeoutError(f'no values received within {timeout} seconds')
        return characteristic.message_type.from_bytearray(first_entry[1])
