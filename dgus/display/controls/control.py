import abc
from enum import Enum, unique 
from typing import Callable

from dgus.display.serialization.json_serializable import JsonSerializable

@unique
class ControlTypeEnum(Enum):
    DATA_VARIABLE = 1
    TEXT_VARIABLE = 2

    def get_serialization_repr(type):
        serialization_repr = {
            ControlTypeEnum.DATA_VARIABLE : "DataVariable",
            ControlTypeEnum.TEXT_VARIABLE : "TextVariable"
        }

        return serialization_repr.get(type, "Undefined!")

class Control(JsonSerializable, metaclass=abc.ABCMeta):
    read_data_callback : Callable[..., bytes]

    data_address : int
    data_length : int
    config_address : int
    config_length : int
    moonraker_data : list

    control_type : ControlTypeEnum

    config_data_has_been_read : bool = False

    def __init__(self, control_type, data_address, data_length, config_address, 
    config_length) -> None:
    
        self.read_data_callback = self.return_nothing_cb
        self.control_type = control_type
        self.data_address = data_address
        self.data_length = data_length
        self.config_address = config_address
        self.config_length = config_length


    def return_nothing_cb(self) -> bytes:
        return bytes()

    @abc.abstractmethod
    def read_config_data(self):
        pass

    @abc.abstractmethod
    def send_data(self):
        pass

    @abc.abstractmethod
    def settings_from_json(self):
        pass

    @abc.abstractmethod
    def settings_to_json(self):
        pass


    
    def get_used_addres_space(self):
        data_address_space = { self.data_address, self.data_length }
        config_address_space = { self.config_address, self.config_length }

        used_address_space = list()

        used_address_space.append(self.control_type)

        if self.data_address != 0xFFFF:
            used_address_space.append(data_address_space)

        if self.config_address != 0xFFFF:
            used_address_space.append(config_address_space)

        return used_address_space

    
    
    def from_json(self, json):
        pass

    def to_json(self):
        control_json = {
            "control": {
                "control_type" : ControlTypeEnum.get_serialization_repr(self.control_type),
                "data_address" : self.data_address,
                "data_length" : self.data_length,
                "config_address" : self.config_address,

                "settings" :  self.settings_to_json()
            }
        }

        return control_json
