from enum import IntEnum

class DGUSCmd(IntEnum):
    WRITE_CTRL_REGISTER = 0x80
    READ_CTRL_REGISTER = 0x81
    WRITE_VPS = 0x82
    READ_VPS = 0x83
