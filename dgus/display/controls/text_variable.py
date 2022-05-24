from struct import pack, unpack
from dgus.display.communication.communication_interface import SerialCommunication
from dgus.display.controls.control import Control, ControlTypeEnum
from dgus.display.communication.protocol import build_read_vp, build_write_vp
from dgus.display.communication.request import Request

class TextVariable(Control):
    
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
        #TODO: Check response for confirmation
        pass

           

    def get_text_data_set_request(self):
        string_bytes = self.get_control_data_cb()
        
        req_bytes = build_write_vp(self.data_address, string_bytes)
        return req_bytes
        
    
    def parse_read_config_data_response(self, response_data : bytes):

        header = response_data[0:2]
        byte_count = response_data[2:3]
        func = response_data[3:4]
        addr = response_data[4:6]
        reg_cnt = response_data[6:7]
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

        #print([hex(x) for x in data])



    def build_read_config_request(self):
        req_data = build_read_vp(self.config_address, self.CONFIG_LENGTH)
        return req_data

       

    def set_config_async(self):
        req = Request(self.get_set_config_data_request, self.set_config_performed_callback,
        "setConfig")

        self.com_interface.queue_request(req)

    def get_set_config_data_request(self):
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
        req = Request(self.build_read_config_request, self.parse_read_config_data_response, "read Config")
        self.com_interface.queue_request(req)

    def set_config_performed_callback(self, data):
        #print("setConfigPerformedCB....")
        #print([hex(x) for x in data])
        pass
   
    def send_data(self):
        req = Request(self.get_text_data_set_request, self.text_data_set_response, "updateText")
        self.com_interface.queue_request(req)

    def settings_from_json(self):
        pass

    def settings_to_json(self):
        settings_json = {
            "x" : self.x_pos,
            "y" : self.y_pos,
            "color" : self.color,
            "upper_left_x" : self.upperleft_x,
            "upper_left_y" : self.upperleft_y,
            "lower_right_x" : self.lowerright_x,
            "lower_right_y" : self.lowerright_y,
            "text_length" : self.text_length,
            "font0_id" :  self.font0_id,
            "font1_id" : self.font1_id,
            "font_width" : self.font_width,
            "font_height" : self.font_height,
            "encode_mode" : self.encode_mode,
            "horizontal_distance" : self.hor_dis,
            "vertical_distance" : self.ver_dis,
        }

        return settings_json
