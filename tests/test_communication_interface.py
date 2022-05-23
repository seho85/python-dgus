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
    
    val = 12345
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
    assert len(com._response_buffer) == len(data)

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



@patch("dgus.display.communication.communication_interface.Serial.read" )
@patch("dgus.display.communication.communication_interface.Serial.in_waiting", new_callable=PropertyMock, return_value=10)
def test_does_do_serial_communication_returns_RESPONSE_COMPLETE_when_a_complete_response_is_available(in_waiting_mock, read_mock):
    
    read_return_data = { 0x1, 0x2, 0x3}
    read_mock.return_value=bytearray( read_return_data )
    
    com = SerialCommunication("wedontcare")
    com._awaited_bytes = 3

    com._response_buffer.clear()
    assert len(com._response_buffer) == 0
    returned_state = com.do_serial_communication(ComThreadState.WAIT_FOR_RESPONSE_TO_COMPLETE)


    #check that read is called with 'awaited_bytes'
    assert 3 == read_mock.call_args.args[0]

    #check that data is placed in response buffer
    assert len(read_return_data) == len(com._response_buffer)

    assert read_mock.called
    assert in_waiting_mock.called

    assert returned_state == ComThreadState.RESPONSE_COMPLETE


@patch("dgus.display.communication.communication_interface.Serial.in_waiting", new_callable=PropertyMock, return_value=1)
def test_does_do_serial_communication_returns_WAIT_FOR_RESPONSE_TO_COMPLETE_when_less_then_awaited_bytes_are_available(in_waiting_mock):
    
    com = SerialCommunication("wedontcare")
    com._awaited_bytes = 3

    returned_state = com.do_serial_communication(ComThreadState.WAIT_FOR_RESPONSE_TO_COMPLETE)


    assert in_waiting_mock.called

    assert returned_state == ComThreadState.WAIT_FOR_RESPONSE_TO_COMPLETE


@patch("dgus.display.communication.communication_interface.SerialCommunication.spontaneous_message")
def test_do_serial_communication_calls_spontanous_message_function_when_a_response_from_a_reserved_address_is_read(spontanous_message_mock):
    response_data = bytearray([0x5a, 0xa5, 0x6, 0x83, 0x0f, 0xff, 0x1, 0xff, 0xff])
    

    com = SerialCommunication("wedontcare")
    com._response_buffer = bytearray(response_data)

    returned_state = com.do_serial_communication(ComThreadState.RESPONSE_COMPLETE)

    #when a spontanous message was processed we jump back to collect the message we were awaiting
    assert returned_state == ComThreadState.WAIT_FOR_NEW_RESPONSE

    #check that any data has been passed
    assert len(spontanous_message_mock.call_args.args[0]) > 0

    #check that 'spontanous_message' was called with the response buffer
    assert response_data == spontanous_message_mock.call_args.args[0]

    #'response_buffer' should be cleared
    assert 0 == len(com._response_buffer)



def test_do_serial_communication_calls_cb_on_request_when_response_was_read():

    response_data = bytearray([0x5a, 0xa5, 0x6, 0x83, 0x1f, 0xff, 0x1, 0xff, 0xff])

    com = SerialCommunication("wedontcare")
    com._response_buffer = bytearray(response_data)

    data_passed_to_response_cb = []

    def response_callback(data : bytes):
        #global data_passed_to_response_cb
        nonlocal data_passed_to_response_cb
        data_passed_to_response_cb = data

    req = Request(None, response_callback, "Testing" )

    com._current_request = req

    returned_state = com.do_serial_communication(ComThreadState.RESPONSE_COMPLETE)

    assert len(com._response_buffer) == 0
    assert response_data == data_passed_to_response_cb
    assert returned_state == ComThreadState.SEND_REQUEST


def test_spontanous_message_calls_callbacks_which_are_assigned_to_the_address_provided_in_response():
    response_data = bytearray([0x5a, 0xa5, 0x6, 0x83, 0x0f, 0xff, 0x1, 0xff, 0xff])

    com = SerialCommunication("wedontcare")

    callback1_data = []

    def callback1(data : bytes):
        nonlocal callback1_data
        callback1_data = data

    callback2_data = []

    def callback2(data : bytes):
        nonlocal callback2_data
        callback2_data = data

    com.register_spontaneous_callback(0x0fff, callback1)
    com.register_spontaneous_callback(0x0fff, callback2)

    com.spontaneous_message(response_data)

    assert callback1_data == response_data
    assert callback2_data == response_data