import enum


class CharacteristicProperty(enum.Enum):
    """enum with all properties a characteristic can have"""
    READ = 'read'
    WRITE = 'write'
    WRITE_WITHOUT_RESPONSE = 'write-without-response'
    NOTIFY = 'notify'
    INDICATE = 'indicate'
