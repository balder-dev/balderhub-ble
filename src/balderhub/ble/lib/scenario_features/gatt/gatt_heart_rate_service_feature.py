import uuid
from typing import Union

from .base_gatt_service_feature import BaseGattServiceFeature
from ...utils import Characteristic, CharacteristicProperty, CharacteristicSecurity
from ...utils.base_gatt_message import BaseGattMessage


class HeartRateServiceMessage(BaseGattMessage):
    """
    GATT Message for :class:`GattHeartRateServiceFeature.MeasurementCharacteristic`
    """
    # TODO unit testen

    min_allowed_length_bytes = 2
    max_allowed_length_bytes = None


    @property
    def _flags_field(self):
        """the full flag field byte"""
        return self._raw_data[0]

    @property
    def bit_hr_format(self):
        """
        the Heart Rate Value Format bit: indicates if the data format of the heart-rate measurement value field is
        UINT8 (bit=0) or UINT16 (bit=1)
        """
        return bool(self._flags_field & (1 << 0))

    @property
    def bit_sensor_contact_status(self):
        """
        the sensor contact status bit: indicates if the sensor is attached at the moment (attached when bit is 1;
        if sensor does not detect skin contact or has poor skin contact this bit should be set to 0)
        """
        return bool(self._flags_field & (1 << 1))

    @property
    def bit_sensor_contact_support(self):
        """
        the sensor contact support bit: indicates if the sensor can detect skin contact and the value of
        `bit_sensor_contact_status` can be interpreted
        """
        return bool(self._flags_field & (1 << 2))

    @property
    def bit_energy_expended_support(self):
        """
        the energy expended support bit: indicates if the energy expended value is available within the data
        """
        return bool(self._flags_field & (1 << 3))

    @property
    def bit_rr_value_support(self):
        """
        the RR-Value support bit: indicates if the RR-Value is available within the data
        """
        return bool(self._flags_field & (1 << 4))

    @property
    def bpm(self) -> int:
        """returns the bpm value of the heart rate"""
        if self.bit_hr_format:
            return int.from_bytes(self._raw_data[1:3], byteorder='little')
        return int(self.raw_data[1])

    @property
    def sensor_has_contact(self) -> Union[bool, None]:
        """
        :return: returns True if the sensor has skin contact or False if it has no skin contact; returns None if
                 this information is not supported by the client
        """
        if self.bit_sensor_contact_support:
            return self.bit_sensor_contact_status
        return None

    @property
    def energy_expended_value(self) -> Union[int, None]:
        """represents the accumulated energy expended in kilo joules or None if no support is given"""
        if not self.bit_energy_expended_support:
            return None

        idx = 1
        idx = (idx + 2) if self.bit_hr_format else (idx + 1)
        return int.from_bytes(self.raw_data[idx:idx+2], byteorder=self.BYTE_ORDER)

    @property
    def rr_values(self) -> Union[list[int], None]:
        """returns a list of all rr-values or None if RR-Values are not supported"""
        if not self.bit_rr_value_support:
            return None

        idx = 1
        idx = (idx + 2) if self.bit_hr_format else (idx + 1)
        idx = (idx + 2) if self.bit_energy_expended_support else idx

        remaining_raw_data = self.raw_data[idx:]

        if len(remaining_raw_data) % 2 != 0:
            # length of remaining elements is not equal
            raise ValueError('can not resolve data because remaining length for RR-values is uneven')
        return [
            int.from_bytes(remaining_raw_data[i:i+2], byteorder=self.BYTE_ORDER)
            for i in range(0, len(remaining_raw_data), 2)
        ]


class GattHeartRateServiceFeature(BaseGattServiceFeature):
    """
    GATT Service Feature for Heart-Rate-Service
    """

    class MeasurementCharacteristic(Characteristic):
        """characteristic representing the Heart Rate Measurement"""
        uuid = uuid.UUID('00002a37-0000-1000-8000-00805f9b34fb')
        name = 'Heart Rate Messurement'
        optional = False
        mandatory_properties = [CharacteristicProperty.NOTIFY]
        security = CharacteristicSecurity.NONE
        message_type = HeartRateServiceMessage

    class BodySensorLocation(Characteristic):
        """characteristic representing the body sensor location"""
        uuid = uuid.UUID('00002a38-0000-1000-8000-00805f9b34fb')
        name = 'Body Sensor Location'
        optional = True
        mandatory_properties = [CharacteristicProperty.READ]
        security = CharacteristicSecurity.NONE
        message_type = HeartRateServiceMessage
