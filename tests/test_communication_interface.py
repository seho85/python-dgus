from operator import le
from os import stat
from unittest.mock import PropertyMock, patch

from serial import SerialException
from dgus.display.communication.communication_interface import ComThreadState, SerialCommunication
from dgus.display.communication.request import Request


@patch("dgus.display.communication.communication_interface.Serial.open", return_value=None)
def test_open_com_port_function_return_true_when_serial_port_was_opened_propery(open_mock):
    com = SerialCommunication("wedontcare")

    assert com.open_com_port()

@patch("dgus.display.communication.communication_interface.Serial.open", 
side_effect=SerialException("blubb"))
def test_open_com_port_function_return_false_when_serial_port_was_not_opened_propery(open_mock):
    com = SerialCommunication("wedontcare")

    assert not com.open_com_port()

#@patch("dgus.display.communication.communication_interface.Serial.write", return_value=None)
def test_do_serial_communication_returns_WAIT_FOR_NEW_RESPONSE_when_called_with_SEND_REQUEST():#write_mock):
    com = SerialCommunication("wedontcare")

    state = ComThreadState.SEND_REQUEST
    awaited_state = ComThreadState.WAIT_FOR_NEW_RESPONSE

    returned_state = com.do_serial_communication(state)

    assert awaited_state == returned_state

@patch("dgus.display.communication.communication_interface.Serial.write", return_value=None)
def test_do_serial_communication_sends_request_when_called_with_SEND_REQUEST(write_mock):
    com = SerialCommunication("wedontcare")

    state = ComThreadState.SEND_REQUEST
    
    val = 12345;
    data = val.to_bytes(length=4, byteorder='big')

    def get_data() -> bytes:
        return data

    req = Request(get_data, None, "WeDontCare")

    com.queue_request(req)


    com.do_serial_communication(state)

    call_args = write_mock.call_args.args[0]

    assert data == call_args

    #assert write_mock.write.assert_called_with(data)
    
@patch("dgus.display.communication.communication_interface.Serial.read")
@patch("dgus.display.communication.communication_interface.Serial.in_waiting", new_callable=PropertyMock, return_value=3)
def test_do_serial_communication_reads_serial_data_when_at_least_three_bytes_arrived(in_waiting_mock, read_mock):
    
    
    data = bytes([0x00, 0x00, 0x0A])
    read_mock.return_value = data
    
    com = SerialCommunication("wedontcare")
    state = ComThreadState.WAIT_FOR_NEW_RESPONSE

    returned_state = com.do_serial_communication(state)

    assert read_mock.called
    assert in_waiting_mock.called
    assert returned_state == ComThreadState.WAIT_FOR_RESPONSE_TO_COMPLETE
    assert len(com.response_buffer) == len(data)

@patch("dgus.display.communication.communication_interface.Serial.in_waiting", new_callable=PropertyMock, return_value=1)    
def test_do_serial_communication_returs_WAIT_FOR_RESPONSE_TO_COMPLETE_when_WAIT_FOR_NEW_RESPONSE_was_passed_and_no_data_is_availabe_and_no_request_is_queued(in_waiting_mock):

    com = SerialCommunication("wedontcare")
    returned_state = com.do_serial_communication(ComThreadState.WAIT_FOR_NEW_RESPONSE)

    assert returned_state == ComThreadState.WAIT_FOR_NEW_RESPONSE



@patch("dgus.display.communication.communication_interface.Serial.in_waiting", new_callable=PropertyMock, return_value=1)    
def test_do_serial_communication_returns_SEND_REQUEST_when_WAIT_FOR_NEW_RESPONSE_request_is_queued(in_waiting_mock):

    com = SerialCommunication("wedontcare")
    com.queue_request(Request(None, None, "WeDontCare"))
    returned_state = com.do_serial_communication(ComThreadState.WAIT_FOR_NEW_RESPONSE)

    assert returned_state == ComThreadState.SEND_REQUEST
