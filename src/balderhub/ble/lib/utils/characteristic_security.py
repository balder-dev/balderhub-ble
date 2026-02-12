import enum


class CharacteristicSecurity(enum.Enum):
    """enumeration to describe the security of a characteristic"""
    NONE = 'NONE'
    AUTHORIZATION_REQUIRED = 'AUTHORIZATION_REQUIRED'
