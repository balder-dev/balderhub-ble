from typing import Optional

import balder

from balderhub.ble.lib.utils.advertisement_message import AdvertisementMessage


class AdvertisementObserverFeature(balder.Feature):
    """
    Base scenario-level feature that manage an Advertisement observing device. It saves all received advertisements
    within the :class:`AdvertisementMessage` and provides them over the method
    :meth:`AdvertisementObserverFeature.filter_advertisements`.
    """

    def is_alive(self) -> bool:
        """
        This method returns True if the observer is currently alive and False otherwise. This could be a thread or
        a remote device.

        :return: True if the observer is alive, False otherwise
        """
        raise NotImplementedError

    def start_observer(self) -> None:
        """starts the observer"""
        raise NotImplementedError

    def shutdown_observer(self) -> None:
        """stops and shuts down the observer"""
        raise NotImplementedError

    def filter_advertisements(
            self,
            by_mac: Optional[str] = None,
            from_start_time: Optional[float] = None,
            till_end_time: Optional[float] = None
    ) -> list[AdvertisementMessage]:
        """
        This method returns all stored :class:`AdvertisementMessage` that were stored over all sessions made with this
        feature as long as it was active.

        :param by_mac: if given, this filters the messages for the given mac address
        :param from_start_time: if given, this filters the messages for the start time - all messages that occurred
                                after the provided timestamp will be returned (use ``time.perf_counter()``)
        :param till_end_time: if given, this filters the messages for the end time - all messages that occurred BEFORE
                              the provided timestamp will be returned (use ``time.perf_counter()``)
        :return: a list with all relevant advertisement messages
        """
        raise NotImplementedError


    def wait_for_new_advertisement(self, with_mac: Optional[str] = None, timeout_sec=10) -> AdvertisementMessage:
        """
        THis message wait for a new advertisement that occurs AFTER the message call was made. If ``with_mac`` is given,
        it will wait explicitly for a message from the specified mac address. If no message is received within
        ``timeout_sec`` the method will raise a :class:`TimeoutError`.

        .. note::
            Make sure to store these messages in internal buffers too, so it still is returned by
            :meth:`AdvertisementObserverFeature.filter_advertisements` too.

        :param with_mac: if given, the method will wait for a new message explicity from this mac address
        :param timeout_sec: maximum time to wait in seconds before raising an :class:`TimeoutError`
        :return: the new advertisement message
        """
        raise NotImplementedError
