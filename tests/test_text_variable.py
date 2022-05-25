from struct import pack

from pyparsing import col
from dgus.display.communication.communication_interface import SerialCommunication

from dgus.display.controls.text_variable import TextVariable


def get_config_data_read_response():
    config_data_response = bytearray()

    for fill_byte in range(0,7):
        config_data_response.append(fill_byte)


    data_address = 0x1000
    x_pos = 1
    y_pos = 2
    color = 3
    upperleft_x = 4
    upperleft_y = 5
    lowerright_x = 6
    lowerright_y = 7
    text_length = 8
    font0_id = 9
    font1_id = 10
    font_width = 11
    font_height = 12
    encode_mode = 13
    hor_dis = 14
    ver_dis = 15


    config_data_bytes = pack("!H H H H H H H H H B B B B B B B B", 
        data_address,  
        x_pos,
        y_pos,
        color,
        upperleft_x,
        upperleft_y,
        lowerright_x,
        lowerright_y,
        text_length,
        font0_id,
        font1_id,
        font_width,
        font_height,
        encode_mode,
        hor_dis,
        ver_dis,
        0)

    config_data_response.extend(config_data_bytes)

    return config_data_response

def test_text_variable_parses_read_config_data_correct():

    config_data_response = bytearray()

    for fill_byte in range(0,7):
        config_data_response.append(fill_byte)


    data_address = 0x1000
    x_pos = 1
    y_pos = 2
    color = 3
    upperleft_x = 4
    upperleft_y = 5
    lowerright_x = 6
    lowerright_y = 7
    text_length = 8
    font0_id = 9
    font1_id = 10
    font_width = 11
    font_height = 12
    encode_mode = 13
    hor_dis = 14
    ver_dis = 15


    config_data_bytes = pack("!H H H H H H H H H B B B B B B B B", 
        data_address,  
        x_pos,
        y_pos,
        color,
        upperleft_x,
        upperleft_y,
        lowerright_x,
        lowerright_y,
        text_length,
        font0_id,
        font1_id,
        font_width,
        font_height,
        encode_mode,
        hor_dis,
        ver_dis,
        0)

    config_data_response.extend(config_data_bytes)

    textVar = TextVariable(None, 0x1000, 0x4242, 10)

    textVar.parse_read_config_data_response(config_data_response)


    assert textVar.data_address == data_address
    assert textVar.x_pos == x_pos
    assert textVar.y_pos == y_pos
    assert textVar.color == color
    assert textVar.upperleft_x == upperleft_x
    assert textVar.upperleft_y == upperleft_y
    assert textVar.lowerright_x == lowerright_x
    assert textVar.lowerright_y == lowerright_y
    assert textVar.text_length == text_length
    assert textVar.font0_id == font0_id
    assert textVar.font1_id == font1_id
    assert textVar.font_height == font_height
    assert textVar.font_width == font_width
    assert textVar.encode_mode == encode_mode
    assert textVar.hor_dis == hor_dis
    assert textVar.ver_dis == ver_dis


def test_textvariable_sends_config_data_correct():
    awaited_request_bytes = [0x5a, 0xa5, 0x1d, 0x82, 0x42, 0x42, 0x0, 0x1, 0x0, 0x2, 0x0, 0x3, 0x0, 0x4, 0x0, 0x5, 0x0, 0x6, 0x0, 0x7, 0x0, 0x8, 0x0, 0x9, 0xa, 0xb, 0xd, 0xc, 0xe, 0xf, 0x10, 0x0]
    
    textVar = TextVariable(None, 0x1000, 0x4242, 10)

    textVar.data_address = 1
    textVar.x_pos = 2
    textVar.y_pos = 3
    textVar.color = 4
    textVar.upperleft_x = 5
    textVar.upperleft_y = 6
    textVar.lowerright_x = 7
    textVar.lowerright_y = 8
    textVar.text_length = 9
    textVar.font0_id = 10
    textVar.font1_id = 11
    textVar.font_height = 12
    textVar.font_width = 13
    textVar.encode_mode = 14
    textVar.hor_dis = 15
    textVar.ver_dis = 16

    request = textVar.build_write_config_request()

    assert request == awaited_request_bytes

    

def test_textvariable_settings_to_json_contains_settings_set_text_variable():
    textVar = TextVariable(None, 0x1000, 0x4242, 10)

    textVar.data_address = 1
    textVar.x_pos = 2
    textVar.y_pos = 3
    textVar.color = 4
    textVar.upperleft_x = 5
    textVar.upperleft_y = 6
    textVar.lowerright_x = 7
    textVar.lowerright_y = 8
    textVar.text_length = 9
    textVar.font0_id = 10
    textVar.font1_id = 11
    textVar.font_height = 12
    textVar.font_width = 13
    textVar.encode_mode = 14
    textVar.hor_dis = 15
    textVar.ver_dis = 16

    settings_json = textVar.settings_to_json()

    x_obj = settings_json.get("x")
    assert int(x_obj) == textVar.x_pos

    y_obj = settings_json.get("y")
    assert int(y_obj) == textVar.y_pos

    color_obj = settings_json.get("color")
    assert int(color_obj) == textVar.color

    upperleft_x_obj = settings_json.get("upper_left_x")
    assert int(upperleft_x_obj) == textVar.upperleft_x

    upperleft_y_obj = settings_json.get("upper_left_y")
    assert int(upperleft_y_obj) == textVar.upperleft_y

    lower_right_x_obj = settings_json.get("lower_right_x")
    assert int(lower_right_x_obj) == textVar.lowerright_x
    
    lower_right_y_obj = settings_json.get("lower_right_y")
    assert int(lower_right_y_obj) == textVar.lowerright_y

    text_length_obj = settings_json.get("text_length")
    assert int(text_length_obj) == textVar.text_length

    font0_id_obj = settings_json.get("font0_id")
    assert int(font0_id_obj) == textVar.font0_id

    font1_id_obj = settings_json.get("font1_id")
    assert int(font1_id_obj) == textVar.font1_id

    font_width_obj = settings_json.get("font_width")
    assert int(font_width_obj) == textVar.font_width

    font_height_obj = settings_json.get("font_height")
    assert int(font_height_obj) == textVar.font_height

    encode_mode_obj = settings_json.get("encode_mode")
    assert int(encode_mode_obj) == textVar.encode_mode

    hor_dis_obj = settings_json.get("horizontal_distance")
    assert int(hor_dis_obj) == textVar.hor_dis

    ver_dis_obj = settings_json.get("vertical_distance")
    assert int(ver_dis_obj) == textVar.ver_dis


def test_textvariable_read_config_data_implementation_adds_request_on_com_interface():
    com = SerialCommunication("wedontcare")
    
    
    text_var = TextVariable(com, 0x1000, 0x4242, 10)

    
    assert com.requests.qsize() == 0

    text_var._read_config_data_implementation()

    assert com.requests.qsize() == 1

    com.__del__()
    

def test_textvariable_send_data_adds_request_on_com_interface():
    com = SerialCommunication("wedontcare")
    text_var = TextVariable(com, 0x1000, 0x4242, 10)

    assert com.requests.qsize() == 0

    text_var.send_data()

    assert com.requests.qsize() == 1

    com.__del__()





