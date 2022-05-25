from struct import unpack, pack
from dgus.display.communication.communication_interface import SerialCommunication
from dgus.display.controls.control import Control, ControlTypeEnum

from dgus.display.communication.protocol import build_read_vp, build_write_vp
from dgus.display.communication.request import Request

class DataVariable(Control):

    com_interface : SerialCommunication = None
    
    CONFIG_LENGTH = 13

    x_pos : int = 0
    y_pos : int = 0
    color : int = 0
    font_id : int = 0
    font_width : int = 0
    alignment : int = 0
    digits : int = 0
    decimal_places : int = 0
    vp_mode : int = 0
    unit_text_len : int = 0
    unit_string = ""


    

    def __init__(self, comInterface : SerialCommunication,
        dataAddress:int, dataLength : int,
        configAddress:int) -> None:

        super().__init__(ControlTypeEnum.DATA_VARIABLE, dataAddress, dataLength, configAddress, 
        self.CONFIG_LENGTH)

        self.com_interface = comInterface
        self.get_control_data_cb = self.get_control_data


    def get_read_config_request(self):
        request_bytes = build_read_vp(self.config_address, self.CONFIG_LENGTH)
        return request_bytes

    def set_config_data_from_response(self, response: bytes):
        data = response[7:]

        unpacked_data = unpack(">H H H H B B B B B B B 11s", data)

        

        #print("ConfigData:")
        #print(unpacked_data)

        self.data_address = unpacked_data[0]
        self.x_pos = unpacked_data[1]
        self.y_pos = unpacked_data[2]
        self.color = unpacked_data[3]
        self.font_id = unpacked_data[4]
        self.font_width = unpacked_data[5]
        self.alignment = unpacked_data[6]
        self.digits = unpacked_data[7]
        self.decimal_places = unpacked_data[8]
        self.vp_mode = unpacked_data[9]
        self.unit_text_len = unpacked_data[10]

        self.unit_string = str(unpacked_data[11][:self.unit_text_len], encoding="ascii")

        self.config_data_has_been_read = True

       
    def write_config_async(self):
        req = Request(self.build_write_config_request, None, "DataVariable: ReadConfig")
        self.com_interface.queue_request(req)

    def build_write_config_request(self):

        string_bytes = str.encode(str(self.unit_string), encoding="ascii")
        self.unit_text_len = len(self.unit_string)
        
        data = pack(">H H H H B B B B B B B 11s",
        self.data_address,
        self.x_pos,
        self.y_pos,
        self.color,
        self.font_id,
        self.font_width,
        self.alignment,
        self.digits,
        self.decimal_places,
        self.vp_mode,
        self.unit_text_len,
        string_bytes
        )

        return build_write_vp(self.config_address, data)

    def get_set_value_request(self):
        data_bytes = self.get_control_data_cb()
        return build_write_vp(self.data_address, data_bytes)


    def get_control_data(self) -> bytes:
        #TODO Renintroduce callback
        return bytes()

    
    # DGUSDisplayControl implementation
    def _read_config_data_implementation(self):
        req = Request(self.get_read_config_request, self.set_config_data_from_response,
        "DataVariable: ReadConfig" )
        
        self.com_interface.queue_request(req)

       
    def _send_config_data_implementation(self):
        set_config_req = Request(self.build_write_config_request, None, "DataVariable SetConfig")
        self.com_interface.queue_request(set_config_req)
   
    def send_data(self):
        req = Request(self.get_set_value_request, None, "DataVariable: Write Data")
        self.com_interface.queue_request(req)


    def settings_from_json(self):
        pass

    def settings_to_json(self):
        settings_json = {
            "x" : self.x_pos,
            "y" : self.y_pos,
            "color" : self.color,
            "fontID" : self.font_id,
            "alignement" : self.alignment,
            "digits" : self.digits,
            "decimal_places" : self.decimal_places,
            "vpMode" : self.vp_mode,
            "lenUnitText" : self.unit_text_len,
            "unitString" : self.unit_string
        }
        return settings_json
