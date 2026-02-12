import balder

from balderhub.ble.lib.utils import Characteristic


class BaseGattServiceFeature(balder.Feature):
    """
    Base abstract GATT service feature which is used as base class for every GATT service feature within this project
    """

    @classmethod
    def get_expected_characteristics(cls) -> list[type[Characteristic]]:
        """
        Determines the expected characteristics of the GATT service

        .. note::
            This is a helper method to auto determine the characteristics based on inner classes that inherit from
            :class:`Characteristic`.

        :return: returns a list of expected characteristics this service feature should handle
        """
        result = []

        for base in cls.__mro__:
            for _, val in base.__dict__.items():
                # it is a subclass of `Characteristic` and is defined within the current module
                if isinstance(val, type) and issubclass(val, Characteristic) and val.__module__ == base.__module__:
                    # make sure that it is really a nested class
                    if '.' in val.__qualname__:
                        if val not in result:
                            result.append(val)

        return result
