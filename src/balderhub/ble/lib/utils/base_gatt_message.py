from abc import ABC, abstractmethod
from typing import Literal, TypeVar, Union


class BaseGattMessage(ABC):
    """
    Base Gatt Message class that is used for all GATT messages within this project
    """

    BYTE_ORDER: Literal["big", "little"] = 'little'

    def __init__(self, raw_data: bytearray):

        if not isinstance(raw_data, bytearray):
            raise TypeError("raw_data must be bytearray")

        if len(raw_data) < self.min_allowed_length_bytes:
            raise ValueError(f'received less bytes than expected: raw data length {len(raw_data)} < expected max '
                             f'length of {self.min_allowed_length_bytes} (raw data: `{raw_data}`)')

        if self.max_allowed_length_bytes and len(raw_data) > self.max_allowed_length_bytes:
            raise ValueError(f'received more bytes than expected: raw data length {len(raw_data)} > expected max '
                             f'length of {self.max_allowed_length_bytes} (raw data: `{raw_data}`)')

        self._raw_data = raw_data


    @property
    @abstractmethod
    def min_allowed_length_bytes(self) -> int:
        """min allowed message length in bytes (<=min_allowed_length_bytes)"""

    @property
    @abstractmethod
    def max_allowed_length_bytes(self) -> Union[int, None]:
        """max allowed message length in bytes (>=min_allowed_length_bytes) (None means no limit)"""

    @classmethod
    def from_bytearray(cls, raw_data: bytearray) -> 'BaseGattMessage':
        """
        Creates the GATT message from a bytearray

        :param raw_data: the raw bytes that describe the GATT message
        :return: a new GATT message of own type
        """
        return cls(raw_data)

    @property
    def raw_data(self) -> bytearray:
        """returns a copy of the raw byte data"""
        return self._raw_data.copy()


BaseGattMessageTypeT = TypeVar("BaseGattMessageTypeT", bound=BaseGattMessage)
