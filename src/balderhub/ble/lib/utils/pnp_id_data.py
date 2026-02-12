import struct
import dataclasses


@dataclasses.dataclass
class PnpIdData:
    """PNP ID Data object"""
    vendor_id_source: bytes
    vendor_id: bytes
    product_id: bytes
    product_version: tuple[int, int, int]

    def validate(self) -> None:
        """
        Validates the PNP ID Data object according to the requirements of the HR-Profile
        """
        if len(self.vendor_id_source) != 1:
            raise ValueError('vendor_id_source needs to be exactly one bytes1')
        if len(self.vendor_id) != 2:
            raise ValueError('vendor_id needs to be exactly two bytes')
        if len(self.product_id) != 2:
            raise ValueError('product_id needs to be exactly two bytes')
        if len(self.product_version) != 3:
            raise ValueError('product_version needs to be a tuple of exactly three numbers (major, minor, sub-minor)')

        if not isinstance(self.product_version[0], int) or not 0 <= self.product_version[0] <= 255:
            raise ValueError('major number of product_version needs to be an integer between 0 and 255')
        if not isinstance(self.product_version[1], int) or not 0 <= self.product_version[1] <= 16:
            raise ValueError('minor number of product_version needs to be an integer between 0 and 16')
        if not isinstance(self.product_version[2], int) or not 0 <= self.product_version[2] <= 16:
            raise ValueError('sub-minor number of product_version needs to be an integer between 0 and 16')

    def to_bytes(self) -> bytes:
        """
        :return: converts the dataclass into a GATT compliant bytes object
        """
        self.validate()

        version = struct.pack(
            '>BB',
            self.product_version[0],
            (self.product_version[1] << 4) | (self.product_version[2])
        )

        return version + self.product_id + self.vendor_id + self.vendor_id_source
