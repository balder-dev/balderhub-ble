import dataclasses

@dataclasses.dataclass
class BLEDeviceInformation:
    """
    provides general information about a Bluetooth Low-Energy device
    """
    #: the address of the device
    address: str
    #: the name of the device
    name: str
