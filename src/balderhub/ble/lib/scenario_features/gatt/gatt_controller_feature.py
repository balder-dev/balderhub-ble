from typing import Union, Generator
import logging

import balder

from balderhub.ble.lib.utils import Characteristic
from balderhub.ble.lib.utils.base_gatt_message import BaseGattMessageTypeT
from balderhub.ble.lib.utils.ble_device_information import BLEDeviceInformation

logger = logging.getLogger(__name__)


class GattControllerFeature(balder.Feature):
    """
    Universal GATT controller feature for interacting with BLE devices that implement one or more GATT
    services/profiles.
    """

    class CharacteristicNotFoundError(Exception):
        """used when the provided characteristic was not found at the connected device"""

    def discover(
            self,
            limit_to_address: Union[str, None] = None,
            timeout_discover: float = 20
    ) -> list[BLEDeviceInformation]:
        """
        Discover available devices that are in Advertising mode at the moment

        :param limit_to_address: if given, the discover procedure is limited to the provided address
        :param timeout_discover: the maximum time to discover devices (timeout, if `limit_to_address` is given)
        :return: the discovered devices
        """
        raise NotImplementedError

    def connect(
            self,
            mac_address: str,
            pair_on_connect: bool = False,
            timeout_discover=20,
            timeout_connect=60
    ) -> None:
        """
        This method connects the controller to the device with the given mac address.

        As soon as a connection is established, this feature is bound to the connected device. You can reconnect with
        another device after running the method :meth:`GattControllerFeature.disconnect`.

        :param mac_address: the mac address of the device to connect with
        :param pair_on_connect: True if the device should be paired directly while connecting
        :param timeout_discover: timeout to discover the device
        :param timeout_connect: timeout till the connection should be established
        """
        raise NotImplementedError

    def unpair(self) -> None:
        """
        Unpairs the current connected device.
        """
        raise NotImplementedError

    def disconnect(self, timeout=10) -> None:
        """
        Executed the disconnect procedure with the connected device.

        :param timeout: max time till the device needs to be disconnected
        """
        raise NotImplementedError

    @property
    def connected_address(self) -> Union[str, None]:
        """
        :return: returns the current connected device's mac address or None if this feature is not connected with a
                 device yet
        """
        raise NotImplementedError

    @property
    def is_connected(self) -> bool:
        """
        :return: returns True if the feature is connected with a device, otherwise False
        """
        return self.connected_address is not None

    def read(self, characteristic: type[Characteristic]) -> BaseGattMessageTypeT:
        """
        This method reads the value of a specific characteristic. It returns the related message.

        :param characteristic: the characteristic to read
        :return: the response for the given characteristic
        """
        raise NotImplementedError

    def write(self, characteristic: type[Characteristic], value: bytearray) -> BaseGattMessageTypeT:
        """
        This method writes the value of a specific characteristic. It returns the related response.

        :param characteristic: the characteristic to write
        :param value: the value to write
        :return: the response from the device
        """
        raise NotImplementedError

    def write_without_response(self, characteristic: type[Characteristic], value: bytearray) -> None:
        """
        This method writes the value of a specific characteristic. It does not return anything, because the method uses
        the write-without-response method.

        :param characteristic: the characteristic to write
        :param value: the value to write
        """
        raise NotImplementedError

    def start_notify(self, characteristic: type[Characteristic]) -> None:
        """
        This method starts the notification for a specific characteristic.

        :param characteristic: the characteristic the notification should be started for
        """
        raise NotImplementedError

    def cancel_notify(self, characteristic: type[Characteristic]) -> None:
        """
        This method cancels the nofify for a specific characteristic.

        :param characteristic: the characteristic the notification should be canceled for
        """
        raise NotImplementedError

    def is_notification_active(self, characteristic: type[Characteristic]) -> bool:
        """
        Checks if the notification is active for the given characteristic.

        :param characteristic: the characteristic that should be checked
        :return: True if there was a nofification registered, False otherwise
        """
        raise NotImplementedError

    # TODO
    # def start_indicate(self, characteristic: Characteristic):
    #     pass

    # def stop_indicate(self, characteristic: Characteristic):
    #     pass

    def get_all_notify_messages_of(
            self,
            characteristic: type[Characteristic]
    ) -> list[BaseGattMessageTypeT]:
        """
        This method returns all received notification messages for a given characteristic.
        :param characteristic: the characteristic the notification needs to be from
        :return: a collection with all messages ordered by timestamp
        """
        raise NotImplementedError

    def wait_for_first_notification_of(
            self,
            characteristic: type[Characteristic],
            timeout: float = 10
    ) -> BaseGattMessageTypeT:
        """
        This method waits for the first notification of the given characteristic and returns it. If a message was
        already received before this method was called, it will be returned.

        If there is no notification received within the given timeout, the method raises a TimeoutError.

        :param characteristic: the characteristic the notification needs to be from
        :param timeout: the maximum time in seconds to block, if this timeout is reached the method raises a
                        TimeoutError
        :return: the newly received GATT message
        """
        raise NotImplementedError

    def wait_for_a_new_message_of(
            self,
            characteristic: type[Characteristic],
            timeout: float = 10
    ) -> BaseGattMessageTypeT:
        """
        This method waits for a specific notification and returns as soon as it detects a new one. All buffered
        notification that were received before entering this method are ignored.

        If there is no notification received within the given timeout, the method raises a TimeoutError.

        :param characteristic: the characterisitic the notification needs to be from
        :param timeout: the maximum time in seconds to block, if this timeout is reached the method raises a
                        TimeoutError
        :return: the newly received GATT message
        """
        raise NotImplementedError

    def _fixt_teardown(self, with_address: str, controller_was_connected: bool):
        if controller_was_connected:
            if self.is_connected:
                logger.info('BLE Controller was connected before entering this fixture and it is still connected '
                            '-> do nothing')
            else:
                logger.info('BLE Controller was connected before entering this fixture, but it is not connected now '
                            '-> connect it again')
                self.connect(with_address)
        else:
            # controller was connected before this fixture
            if self.is_connected:
                logger.info('BLE Controller was disconnected before entering this fixture but it is connected now '
                            '-> disconnect it again')
                self.disconnect()
            else:
                logger.info('BLE Controller was disconnected before entering this fixture and it is still disconnected '
                            '-> do nothing')

    def fixt_make_sure_to_be_connected_to(
            self,
            with_address: str,
            restore_entry_state: bool = True
    ) -> Generator[None, None, None]:
        """
        Fixture that makes sure that the BLE connection is established with the given address. If there is another
        connection established, the method will disconnect it and reconnect with the given address.

        .. note::

            You can use this fixture directly by using:

            .. code-block:: python

                @balder.fixture(...)
                def my_fixture(...):
                    yield from feat.fixt_make_sure_to_be_connected_to(...)

        :param with_address: the address to connect with
        :param restore_entry_state: True if the previous state (either connected or disconnected) should be
                                    reestablished in the teardown part of this fixture
        :return: the ready to use fixture generator, but without any values
        """
        controller_was_connected = self.is_connected

        reconnect_afterwards_to = with_address
        if controller_was_connected:
            connected_to_mac = self.connected_address
            if with_address == connected_to_mac:
                logger.info(f'BLE Controller is already connected to {with_address} -> do nothing')
            else:
                logger.info(f'BLE Controller is connected to another device {connected_to_mac} -> disconnect it and '
                            f'connect with {with_address}')
                reconnect_afterwards_to = self.connected_address
                self.disconnect()
                self.connect(with_address)
        else:
            logger.info('BLE Controller is not connected yet -> connect it')
            self.connect(with_address)

        yield None

        if not restore_entry_state:
            return
        self._fixt_teardown(with_address=reconnect_afterwards_to, controller_was_connected=controller_was_connected)

    def fixt_make_sure_to_be_disconnected_from(
            self,
            with_address: str,
            restore_entry_state: bool = True
    ) -> Generator[None, None, None]:
        """
        Fixture that makes sure that the BLE connection is disconnected before finishing the construction part of this
        fixture. If there is another connection established to another device like the given address, the fixture will
        do nothing. If it is connected to the device with the given address it will disconnect before finishing the
        construction part.
        If `restore_entry_state` is True, the method will reestablish the state that was given before entering this
        fixture.

        .. note::

            You can use this fixture directly by using:

            .. code-block:: python

                @balder.fixture(...)
                def my_fixture(...):
                    yield from feat.fixt_make_sure_to_be_disconnected_from(...)

        :param with_address: the address the connection should be disconnected from
        :param restore_entry_state: True if the previous state (either connected or disconnected) should be
                                    reestablished in the teardown part of this fixture
        :return: the ready to use fixture generator, but without any values
        """
        controller_was_connected = self.is_connected
        should_reconnect_afterwards = controller_was_connected
        if controller_was_connected:
            connected_to_mac = self.connected_address
            if with_address == connected_to_mac:
                logger.info(f'BLE Controller is already connected to {with_address} -> disconnect it')
                self.disconnect()
            else:
                logger.info(f'BLE Controller is connected to another device {connected_to_mac} -> do nothing')
                should_reconnect_afterwards = False
        else:
            logger.info('BLE Controller is already disconnected -> do nothing')

        yield None

        if not restore_entry_state:
            return
        self._fixt_teardown(with_address=with_address, controller_was_connected=should_reconnect_afterwards)
