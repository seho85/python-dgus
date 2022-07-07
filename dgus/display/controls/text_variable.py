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

from struct import pack, unpack
from dgus.display.communication.communication_interface import SerialCommunication
from dgus.display.controls.control import Control, ControlTypeEnum
from dgus.display.communication.protocol import build_read_vp, build_write_vp
from dgus.display.communication.request import Request

class TextVariable(Control):
    
    # pylint: disable=too-many-instance-attributes
    # maybe settings should be moved to own @dataclass
    com_interface  : SerialCommunication = None

    CONFIG_LENGTH = 13
       
    x_pos : int = 0
    y_pos : int = 0
    color : int = 0
    upperleft_x : int = 0
    upperleft_y : int = 0
    lowerright_x : int = 0
    lowerright_y : int = 0
    text_length : int = 0
    font0_id : int = 0
    font1_id : int = 0
    font_width : int = 0
    font_height : int = 0
    encode_mode : int = 0
    hor_dis : int = 0
    ver_dis : int = 0


    def __init__(self, comInterface : SerialCommunication, 
        dataAddress:int, configAddress:int, TextLength:int) -> None:

        super().__init__(ControlTypeEnum.TEXT_VARIABLE, dataAddress, TextLength, configAddress, 
        self.CONFIG_LENGTH)

        self.com_interface = comInterface

    def text_data_set_response(self, data):
        self.waiting_for_data_response = False

    def get_text_data_set_request(self):
        string_bytes = self.get_control_data_cb()
        
        req_bytes = build_write_vp(self.data_address, string_bytes)
        return req_bytes
    
    def parse_read_config_data_response(self, response_data : bytes):

        #header = response_data[0:2]
        #byte_count = response_data[2:3]
        #func = response_data[3:4]
        #addr = response_data[4:6]
        #reg_cnt = response_data[6:7]
        data = response_data[7:]

        
        unpacked_config_data = unpack("!H H H H H H H H H B B B B B B B B", data)

        #self.dataAddress = unpacked_config_data[0]
        self.x_pos = unpacked_config_data[1]
        self.y_pos = unpacked_config_data[2]
        self.color = unpacked_config_data[3]
        self.upperleft_x = unpacked_config_data[4]
        self.upperleft_y = unpacked_config_data[5]
        self.lowerright_x = unpacked_config_data[6]
        self.lowerright_y = unpacked_config_data[7]
        self.text_length = unpacked_config_data[8]
        self.font0_id = unpacked_config_data[9]
        self.font1_id = unpacked_config_data[10]
        self.font_width = unpacked_config_data[11]
        self.font_height = unpacked_config_data[12]
        self.encode_mode = unpacked_config_data[13]
        self.hor_dis = unpacked_config_data[14]
        self.ver_dis = unpacked_config_data[15]

        self.config_data_has_been_read = True


    def build_read_config_request(self):
        req_data = build_read_vp(self.config_address, self.CONFIG_LENGTH)
        return req_data

       

    def set_config_async(self):
        req = Request(self.build_write_config_request, self.set_config_performed_callback,
        "setConfig")

        self.com_interface.queue_request(req)

    def build_write_config_request(self):
        data_bytes = pack("!H H H H H H H H H B B B B B B B B", 
        self.data_address,  
        self.x_pos,
        self.y_pos,
        self.color,
        self.upperleft_x,
        self.upperleft_y,
        self.lowerright_x,
        self.lowerright_y,
        self.text_length,
        self.font0_id,
        self.font1_id,
        self.font_width,
        self.font_height,
        self.encode_mode,
        self.hor_dis,
        self.ver_dis,
        0)

        req_bytes = build_write_vp(self.config_address, data_bytes)
        return req_bytes

    #DGUSDisplayControl Implementation
   
    def _read_config_data_implementation(self):
        req = Request(self.build_read_config_request, self.parse_read_config_data_response, 
        f"TextVariable - Read Config Data - Address: {hex(self.config_address)}")
        self.com_interface.queue_request(req)

    def _send_config_data_implementation(self):
        send_config_req = Request(self.build_write_config_request, None, 
        f"TextVariable - Write Config Data - Address: {hex(self.config_address)}")
        self.com_interface.queue_request(send_config_req)


    def set_config_performed_callback(self, data):
        pass
   
    def send_data(self):
        if not self.waiting_for_data_response:
            req = Request(self.get_text_data_set_request, self.text_data_set_response,
            f"TextVariable - Write Data - Address: {hex(self.data_address)}")
            self.waiting_for_data_response = True
            self.com_interface.queue_request(req)


    def data_was_send(self, response):
        self.waiting_for_data_response = False

