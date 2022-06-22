 # 
 # This file is part of python-dgus (https://github.com/seho85/python-dgus).
 # Copyright (c) 2022 Sebastian Holzgreve
 # 
 # This program is free software: you can redistribute it and/or modify  
 # it under the terms of the GNU General Public License as published by  
 # the Free Software Foundation, version 3.
 #
 # This program is distributed in the hope that it will be useful, but 
 # WITHOUT ANY WARRANTY; without even the implied warranty of 
 # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
 # General Public License for more details.
 #
 # You should have received a copy of the GNU General Public License 
 # along with this program. If not, see <http://www.gnu.org/licenses/>.
 #
 
import abc
from enum import Enum, unique 
from typing import Callable

from dgus.display.serialization.json_serializable import JsonSerializable

@unique
class ControlTypeEnum(Enum):
    TESTING_CONTROL = 0
    DATA_VARIABLE = 1
    TEXT_VARIABLE = 2
    
    @staticmethod
    def get_serialization_repr(control_type):
        serialization_repr = {
            ControlTypeEnum.DATA_VARIABLE : "DataVariable",
            ControlTypeEnum.TEXT_VARIABLE : "TextVariable",
            ControlTypeEnum.TESTING_CONTROL : "TestingControl"
        }

        return serialization_repr.get(control_type, "Undefined!")

class Control(metaclass=abc.ABCMeta):
    get_control_data_cb : Callable[..., bytes]

    data_address : int
    data_length : int
    config_address : int
    config_length : int

    control_type : ControlTypeEnum

    config_data_has_been_read : bool = False
    waiting_for_data_response : bool = False

    def __init__(self, control_type, data_address, data_length, config_address, 
    config_length) -> None:
    
        self.get_control_data_cb = self.return_nothing_cb
        self.control_type = control_type
        self.data_address = data_address
        self.data_length = data_length
        self.config_address = config_address
        self.config_length = config_length


    def return_nothing_cb(self) -> bytes:
        return bytes()

    def read_config_data(self):
        if self.config_address != 0xFFFF:
            self._read_config_data_implementation()
        else:
            self.config_data_has_been_read = True

    def send_config_data(self):
        if self.config_address != 0xFFFF:
            self._send_config_data_implementation()

    @abc.abstractmethod
    def _read_config_data_implementation(self):
        pass

    @abc.abstractmethod
    def _send_config_data_implementation(self):
        pass

    @abc.abstractmethod
    def send_data(self):
        pass

    """
    @abc.abstractmethod
    def settings_from_json(self):
        pass

    @abc.abstractmethod
    def settings_to_json(self):
        pass



    def from_json(self, json_data):
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
    """