from dgus.display.communication.dgus_cmd import DGUSCmd

def _build_request(command : int, data : bytes):
    cmd_sequence = [0x5a, 0xa5 ]

    byte_count = len(data) + 1
    cmd_sequence.append(byte_count)
    cmd_sequence.append(command)
    cmd_sequence.extend(data)

    return cmd_sequence


def build_mask_switch_request(mask_idx : int):
    cmd_data = [0x00, 0x84, 0x5a, 0x01]
    mask_idx_data = mask_idx.to_bytes(length=2, signed=False, byteorder='big')
    cmd_data.extend(mask_idx_data)

    return _build_request(DGUSCmd.WRITE_VPS, bytes(cmd_data))

def build_write_vp(address: int, data : bytes):
               
    cmd_data = bytearray(address.to_bytes(length=2, signed=False, byteorder='big'))
    cmd_data.extend(data)
    
    cmd_seq = _build_request(DGUSCmd.WRITE_VPS, cmd_data)

    return cmd_seq

def build_read_vp(address :int, register_count : int):
    cmd_data = bytearray(address.to_bytes(length=2, byteorder='big'))
    cmd_data.extend(register_count.to_bytes(length=1, byteorder='big'))

    cmd_seq = _build_request(DGUSCmd.READ_VPS, cmd_data)
    return cmd_seq
