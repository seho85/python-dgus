from struct import pack
from unicodedata import decimal
from dgus.display.controls.data_variable import DataVariable


def test_data_variable_sets_config_correctly_when_set_config_data_from_response_is_called():
    config_data_response = bytearray()

    for fill_byte in range(0,7):
        config_data_response.append(fill_byte)

    
    unit_string = "blubb"


    unit_string_bytes = str.encode(str(unit_string), encoding="ascii")
    unit_text_len = len(unit_string)
    data_address = 1
    x_pos = 2
    y_pos = 3
    color = 4
    font_id = 5
    font_width = 6
    alignment = 7
    digits = 8
    decimal_places = 9
    vp_mode = 10
    
        
    config_data_bytes = pack(">H H H H B B B B B B B 11s",
    data_address,
    x_pos,
    y_pos,
    color,
    font_id,
    font_width,
    alignment,
    digits,
    decimal_places,
    vp_mode,
    unit_text_len,
    unit_string_bytes
    )

    config_data_response.extend(config_data_bytes)


    data_variable = DataVariable(None, 0x1000, 2, 0x2000)
    data_variable.set_config_data_from_response(config_data_response)

    assert data_variable.data_address == data_address
    assert data_variable.x_pos == x_pos
    assert data_variable.y_pos == y_pos
    assert data_variable.color == color
    assert data_variable.font_id == font_id
    assert data_variable.font_width == font_width
    assert data_variable.alignment == alignment
    assert data_variable.digits == digits
    assert data_variable.decimal_places == decimal_places
    assert data_variable.vp_mode == vp_mode
    assert data_variable.unit_string == unit_string
    assert data_variable.unit_text_len == unit_text_len



def test_data_variable_build_write_config_request_creates_correct_response():
    awaited_request = [0x5a, 0xa5, 0x1d, 0x82, 0x20, 0x0, 0x0, 0x1, 0x0, 0x2, 0x0, 0x3, 0x0, 0x4, 0x5, 0x6, 0x7, 0x8, 0x9, 0xa, 0x3, 0x61, 0x73, 0x64, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]
    
    data_variable = DataVariable(None, 0x1000, 2, 0x2000)
    
    data_variable.data_address = 1
    data_variable.x_pos = 2
    data_variable.y_pos = 3
    data_variable.color = 4
    data_variable.font_id = 5
    data_variable.font_width = 6
    data_variable.alignment = 7
    data_variable.digits = 8
    data_variable.decimal_places = 9
    data_variable.vp_mode = 10
    data_variable.unit_text_len = 11
    data_variable.unit_string = "asd"

    write_config_data_request = data_variable.build_write_config_request()

    assert write_config_data_request == awaited_request


def test_data_variable_settings_to_json_has_correct_settings_set():
    data_variable = DataVariable(None, 0x1000, 2, 0x2000)
    
    data_variable.data_address = 1
    data_variable.x_pos = 2
    data_variable.y_pos = 3
    data_variable.color = 4
    data_variable.font_id = 5
    data_variable.font_width = 6
    data_variable.alignment = 7
    data_variable.digits = 8
    data_variable.decimal_places = 9
    data_variable.vp_mode = 10
    data_variable.unit_text_len = 11
    data_variable.unit_string = "asd"

    settings_json = data_variable.settings_to_json()

    x_json = settings_json.get("x")
    assert int(x_json) == data_variable.x_pos

    y_json = settings_json.get("y")
    assert int(y_json) == data_variable.y_pos

    color_json = settings_json.get("color")
    assert int(color_json) == data_variable.color

    fontid_json = settings_json.get("fontID")
    assert int(fontid_json) == data_variable.font_id

    alignement_json = settings_json.get("alignement")
    assert int(alignement_json) == data_variable.alignment

    digits_json = settings_json.get("digits")
    assert int(digits_json) == data_variable.digits

    decimal_places_json = settings_json.get("decimal_places")
    assert int(decimal_places_json) == data_variable.decimal_places

    vp_mode_json = settings_json.get("vpMode")
    assert int(vp_mode_json) == data_variable.vp_mode

    len_unit_text_json = settings_json.get("lenUnitText")
    assert int(len_unit_text_json) == data_variable.unit_text_len

    unit_string_json = settings_json.get("unitString")
    assert str(unit_string_json) == data_variable.unit_string