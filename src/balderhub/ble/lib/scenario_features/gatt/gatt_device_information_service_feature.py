import uuid

from .base_gatt_service_feature import BaseGattServiceFeature
from ...utils import Characteristic, CharacteristicProperty, CharacteristicSecurity


class GattDeviceInformationServiceFeature(BaseGattServiceFeature):
    """
    GATT Service Feature for Device-Information-Service
    """

    class SystemId(Characteristic):
        """characteristic representing the System ID"""

        uuid = uuid.UUID('00002a23-0000-1000-8000-00805f9b34fb')
        name = 'System ID'
        optional = True
        mandatory_properties = [CharacteristicProperty.READ]
        security = CharacteristicSecurity.NONE

    class ModelNumberCharacteristic(Characteristic):
        """characteristic representing the Model Number String"""
        uuid = uuid.UUID('00002a24-0000-1000-8000-00805f9b34fb')
        name = 'Model Number String'
        optional = True
        mandatory_properties = [CharacteristicProperty.READ]
        security = CharacteristicSecurity.NONE

    class SerialNumberCharacteristic(Characteristic):
        """characteristic representing the Serial Number"""
        uuid = uuid.UUID('00002a25-0000-1000-8000-00805f9b34fb')
        name = 'Serial Number String'
        optional = True
        mandatory_properties = [CharacteristicProperty.READ]
        security = CharacteristicSecurity.NONE

    class FirmwareRevisionCharacteristic(Characteristic):
        """characteristic representing the Firmware Revision"""
        uuid = uuid.UUID('00002a26-0000-1000-8000-00805f9b34fb')
        name = 'Firmware Revision String'
        optional = True
        mandatory_properties = [CharacteristicProperty.READ]
        security = CharacteristicSecurity.NONE

    class HardwareRevisionCharacteristic(Characteristic):
        """characteristic representing the Hardware Revision"""
        uuid = uuid.UUID('00002a27-0000-1000-8000-00805f9b34fb')
        name = 'Hardware Revision String'
        optional = True
        mandatory_properties = [CharacteristicProperty.READ]
        security = CharacteristicSecurity.NONE

    class SoftwareRevisionCharacteristic(Characteristic):
        """characteristic representing the Software Revision"""
        uuid = uuid.UUID('00002a28-0000-1000-8000-00805f9b34fb')
        name = 'Software Revision String'
        optional = True
        mandatory_properties = [CharacteristicProperty.READ]
        security = CharacteristicSecurity.NONE

    class ManufacturerCharacteristic(Characteristic):
        """characteristic representing the Manufacturer Name"""
        uuid = uuid.UUID('00002a29-0000-1000-8000-00805f9b34fb')
        name = 'Manufacturer Name String'
        optional = True
        mandatory_properties = [CharacteristicProperty.READ]
        security = CharacteristicSecurity.NONE

    class IeeeRegulatoryCertDataListCharacteristic(Characteristic):
        """characteristic representing the IEEE 11073-20601 Regulatory Certification Data List"""
        uuid = uuid.UUID('00002a2a-0000-1000-8000-00805f9b34fb')
        name = 'IEEE 11073-20601 Regulatory Certification Data List'
        optional = True
        mandatory_properties = [CharacteristicProperty.READ]
        security = CharacteristicSecurity.NONE

    class PnpIdCharacteristic(Characteristic):
        """characteristic representing the PNP ID"""
        uuid = uuid.UUID('00002a50-0000-1000-8000-00805f9b34fb')
        name = 'PnP ID'
        optional = True
        mandatory_properties = [CharacteristicProperty.READ]
        security = CharacteristicSecurity.NONE

    class UdiForMedicalDevicesCharacteristic(Characteristic):
        """characteristic representing the UDI for medical devices"""
        uuid = uuid.UUID('00002bff-0000-1000-8000-00805f9b34fb')
        name = 'UDI for Medical Devices'
        optional = True
        mandatory_properties = [CharacteristicProperty.READ]
        security = CharacteristicSecurity.NONE
