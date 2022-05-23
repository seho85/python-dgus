from requests import request
from dgus.display.communication.protocol import build_mask_switch_request, build_write_vp, build_read_vp

def test_build_mask_switch_request_returns_correct_bytes():
    mask1_awaited_request_data = [0x5a, 0xa5, 0x7, 0x82, 0x0, 0x84, 0x5a, 0x1, 0x0, 0x1]
    mask9_awaited_request_data = [0x5a, 0xa5, 0x7, 0x82, 0x0, 0x84, 0x5a, 0x1, 0x0, 0x9]

    request_data_mask1 = build_mask_switch_request(1)
    request_data_mask9 = build_mask_switch_request(9)

    assert request_data_mask1 == mask1_awaited_request_data
    assert request_data_mask9 == mask9_awaited_request_data


def test_build_write_vp_returns_correct_bytes():
    awaited_bytes = [0x5a, 0xa5, 0x7, 0x82, 0x10, 0x0, 0x1, 0x2, 0x3, 0x4]

    address = 0x1000
    data_to_be_written = [ 0x01, 0x02, 0x03, 0x04 ]

    request_data = build_write_vp(address, data_to_be_written)

    print("Generated Request Data:")
    print([hex(x) for x in request_data])
    print("Awaited Request Data:")
    print([hex(x) for x in awaited_bytes])


    assert request_data == awaited_bytes



def test_build_read_vp_returns_correct_bytes():
    awaited_bytes = [0x5a, 0xa5, 0x4, 0x83, 0x10, 0x0, 0xa]
    
    address = 0x1000
    register_count = 10

    request_data = build_read_vp(address, register_count)

    print("Generated Request Data:")
    print([hex(x) for x in request_data])
    print("Awaited Request Data:")
    print([hex(x) for x in awaited_bytes])

    assert request_data == awaited_bytes


