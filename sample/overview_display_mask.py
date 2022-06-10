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

from dgus.display.communication.communication_interface import SerialCommunication
from dgus.display.controls.data_variable import DataVariable
from dgus.display.mask import Mask

class OverviewDisplayMask(Mask):
    #websock : WebsocketInterface = None
    #com_interface: SerialCommunication = None

    temp_extruder = DataVariable
    target_temp_extruder = DataVariable
    temp_bed = DataVariable
    target_temp_bed = DataVariable

    data = 0
    
    def __init__(self, com_interface: SerialCommunication) -> None:
        super().__init__(0, com_interface)
        
        self.temp_extruder = DataVariable(self._com_interface, 0x1000, 2, 0x2000)
        self.temp_extruder.get_control_data_cb = self.static_value_value_cb
        self.controls.append(self.temp_extruder)

        self.target_temp_extruder = DataVariable(self._com_interface, 0x1020,2, 0x2020)
        self.target_temp_extruder.get_control_data_cb = self.static_value_value_cb
        self.controls.append(self.target_temp_extruder)

        self.temp_bed = DataVariable(self._com_interface, 0x1010, 2, 0x2010)
        self.temp_bed.get_control_data_cb = self.static_value_value_cb
        self.controls.append(self.temp_bed)

        self.target_temp_bed = DataVariable(self._com_interface, 0x1030,2, 0x2030)
        self.target_temp_bed.get_control_data_cb = self.static_value_value_cb
        self.controls.append(self.target_temp_bed)


    def static_value_value_cb(self):
        self.data += 1

        return self.data.to_bytes(length=2, byteorder='big')