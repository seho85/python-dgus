from struct import pack, unpack
from dgus.display.communication.communication_interface import SerialCommunication
from dgus.display.controls.control import Control, ControlTypeEnum
from dgus.display.communication.protocol import build_read_vp, build_write_vp
from dgus.display.communication.request import Request

class TextVariable(Control):
    
    com_interface  : SerialCommunication = None

    CONFIG_LENGTH = 13
       
    x_pos : int
    y_pos : int
    color : int
    upperleft_x : int
    upperleft_y : int
    lowerright_x : int
    lowerright_y : int
    text_length : int
    font0_id : int
    font1_id : int
    font_width : int
    font_height : int
    encode_mode : int
    hor_dis : int
    ver_dis : int



    x_pos = 0
    y_pos = 0
    color = 0
    upperleft_x = 0
    upperleft_y = 0
    lowerright_x = 0
    lowerright_y = 0
    text_length = 0
    font0_id = 0
    font1_id = 0
    font_width = 0
    font_height = 0
    encode_mode = 0
    hor_dis = 0
    ver_dis = 0

    def __init__(self, comInterface : SerialCommunication, 
        dataAddress:int, configAddress:int, TextLength:int) -> None:

        super().__init__(ControlTypeEnum.TEXT_VARIABLE, dataAddress, TextLength, configAddress, 
        self.CONFIG_LENGTH)

        self.com_interface = comInterface
        

    def set_text_performed_cb(self, data):
        pass

    def set_text_async(self):
        req = Request(self.get_set_text_data_request, self.set_text_performed_cb, "updateText")
        self.com_interface.queue_request(req)

    def get_set_text_data_request(self):
        string_bytes = self.get_control_data_cb()
        
        req_bytes = build_write_vp(self.data_address, string_bytes)
        return req_bytes
        
    
    def config_data_response_cb(self, resp : bytes):

        header = resp[0:2]
        byte_count = resp[2:3]
        func = resp[3:4]
        addr = resp[4:6]
        reg_cnt = resp[6:7]
        data = resp[7:]

        
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


    def read_config_async(self):
        req = Request(self.get_read_config_request, self.config_data_response_cb, "read Config")

        self.com_interface.queue_request(req)

    def get_read_config_request(self):
        address = bytearray(self.config_address.to_bytes(length=2, signed=False, byteorder='big'))
        req_data = build_read_vp(address, self.CONFIG_LENGTH)

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
        self.set_config_async()

    def set_config_performed_callback(self, data):
        #print("setConfigPerformedCB....")
        #print([hex(x) for x in data])
        pass
   
    def send_data(self):
        self.set_text_async()

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
