from typing import Union

from balderhub.ble.lib.scenario_features.ble_device_config import BleDeviceConfig
from balderhub.ble.lib.utils.pnp_id_data import PnpIdData


class DeviceInformationConfig(BleDeviceConfig):
    """configuration feature for testing the :class:`GattDeviceInformationServiceFeature`"""

    @property
    def manufacturer_name_string(self) -> Union[bytes, None]:
        """
        expected manufacturer name that should be transmitted within the DeviceInformation-Service
        (None, if this value is not expected to exist as a characteristic within the DUT)
        """
        raise NotImplementedError()

    @property
    def model_number_string(self) -> Union[bytes, None]:
        """
        expected model number that should be transmitted within the DeviceInformation-Service
        (None, if this value is not expected to exist as a characteristic within the DUT)
        """
        raise NotImplementedError()

    @property
    def serial_number_string(self) -> Union[bytes, None]:
        """
        expected serial number that should be transmitted within the DeviceInformation-Service
        (None, if this value is not expected to exist as a characteristic within the DUT)
        """
        raise NotImplementedError()

    @property
    def hardware_revision_string(self) -> Union[bytes, None]:
        """
        expected hardware revision that should be transmitted within the DeviceInformation-Service
        (None, if this value is not expected to exist as a characteristic within the DUT)
        """
        raise NotImplementedError()

    @property
    def firmware_revision_string(self) -> Union[bytes, None]:
        """
        expected firmware revision that should be transmitted within the DeviceInformation-Service
        (None, if this value is not expected to exist as a characteristic within the DUT)
        """
        raise NotImplementedError()

    @property
    def software_revision_string(self) -> Union[bytes, None]:
        """
        expected software revision that should be transmitted within the DeviceInformation-Service
        (None, if this value is not expected to exist as a characteristic within the DUT)
        """
        raise NotImplementedError()

    @property
    def system_id(self) -> Union[bytes, None]:
        """
        expected system ID that should be transmitted within the DeviceInformation-Service
        (None, if this value is not expected to exist as a characteristic within the DUT)
        """
        raise NotImplementedError()

    @property
    def iee11073_20601_regulatory_cert_data_list(self) -> Union[bytes, None]:
        """
        expected IEE11073-20601 Regulatory Certification Data List that should be transmitted within the
        DeviceInformation-Service (None, if this value is not expected to exist as a characteristic within the DUT)
        """
        raise NotImplementedError()

    @property
    def pnp_id(self) -> Union[PnpIdData, None]:
        """
        expected PNP ID that should be transmitted within the DeviceInformation-Service
        (None, if this value is not expected to exist as a characteristic within the DUT)
        """
        raise NotImplementedError()

    @property
    def udi_for_medical(self) -> Union[bytes, None]:
        """
        expected UDI for medical devices that should be transmitted within the DeviceInformation-Service
        (None, if this value is not expected to exist as a characteristic within the DUT)
        """
        raise NotImplementedError()
