from collections import defaultdict
from concurrent.futures import thread
from enum import Enum

import queue
import threading
from typing import Any, Callable
from time import time, sleep
# import serial
from serial import Serial, SerialException
from dgus.display.communication.dgus_cmd import DGUSCmd
from dgus.display.communication.request import Request
from dgus.display.serialization.json_serializable import JsonSerializable

RESERVED_MEMORY_ADDRESS = 0x0FFF


class ComThreadState(Enum):
    WAIT_FOR_NEW_RESPONSE = 0
    WAIT_FOR_RESPONSE_TO_COMPLETE = 1
    RESPONSE_COMPLETE = 2
    SEND_REQUEST = 3


class SerialCommunication(JsonSerializable):
    ser = Serial()
    com_thread: thread

    response_buffer: bytearray = bytearray()

    requests = queue.Queue()
    mutex = threading.Lock()

    spontaneous_callbacks = defaultdict(list)

    awaited_bytes = 0
    current_request : Request = None

    wait_for_response_timeout = 1
    time_send = None

    run_com_thread = False


    def __init__(self, serial_port) -> None:
        self.ser.port = serial_port
        self.ser.baudrate = 115200

    def queue_request(self, request: Request):
        self.mutex.acquire()
        self.requests.put(request)
        self.mutex.release()

    def open_com_port(self) -> bool:
        try:
            self.ser.open()
            return True
        except SerialException:
            print(f"Opening Serial Interface: {self.ser.port} failed!")
            return False

    def start_com_thread(self):
        if self.open_com_port():
            self.com_thread = threading.Thread(target=self.com_thread_function)
            self.run_com_thread = True
            self.com_thread.start()
            print("Started serial display communication...")
            return True
        return False

    def stop(self):
        if self.run_com_thread:
            self.run_com_thread = False
            self.com_thread.join()
            print("Stopped serial display communication...")

    def com_thread_function(self):

        state = ComThreadState.SEND_REQUEST

        while self.run_com_thread:
            state = self.do_serial_communication(state)

            #sleep(0.2)

    def do_serial_communication(self, state: ComThreadState) -> ComThreadState:
        if state == ComThreadState.SEND_REQUEST:
            #print("SEND_REQUEST")
            self.time_send = time()
            with self.mutex:
                if self.requests.empty():
                    return ComThreadState.WAIT_FOR_NEW_RESPONSE
                else:
                    self.current_request = self.requests.get()
                    # print("processing: " + currentRequest.name)
                    req_bytes = self.current_request.get_request_data()
                    print("--> ", end='')
                    print([hex(x) for x in req_bytes])
                    self.ser.write(req_bytes)
                    self.time_send = time()
                    return ComThreadState.WAIT_FOR_NEW_RESPONSE
                
            #    self.mutex.release()
            #last_send = time()
            

        if state == ComThreadState.WAIT_FOR_NEW_RESPONSE:
            #print("WAIT_FOR_NEW_RESPONSE")
            if self.ser.in_waiting >= 3:
                header_data = self.ser.read(3)
                self.awaited_bytes = header_data[2]
                self.response_buffer.extend(header_data)
                return ComThreadState.WAIT_FOR_RESPONSE_TO_COMPLETE

            if time() - self.time_send > self.wait_for_response_timeout:
                if not self.requests.empty():
                    return ComThreadState.SEND_REQUEST
            
            sleep(0.1)


        if state == ComThreadState.WAIT_FOR_RESPONSE_TO_COMPLETE:
            #print("WAIT_FOR_RESPONSE_TO_COMPLETE")
            if self.ser.in_waiting >= self.awaited_bytes:
                data_read = self.ser.read(self.awaited_bytes)
                self.response_buffer.extend(data_read)
                state = ComThreadState.RESPONSE_COMPLETE

        if state == ComThreadState.RESPONSE_COMPLETE:
            
            function = self.response_buffer[3]
            address = int.from_bytes(self.response_buffer[4:6], byteorder='big', signed=False)

            # print(f"function: {function}")
            # print(f"address:  {address}")

            print("<-- ", end='')
            print([hex(x) for x in self.response_buffer])

            
            if function == DGUSCmd.READ_VPS:
                if address <= RESERVED_MEMORY_ADDRESS:
                    # we got a spontanous data transmission in between, 
                    # handle it an jump back to reading
                    self.spontaneous_message(self.response_buffer)
                    self.response_buffer.clear()
                    state = ComThreadState.WAIT_FOR_NEW_RESPONSE
                    return state
            # TODO: Add checking for confirmation message
            if self.current_request is not None:
                if self.current_request.response_callback is not None:
                    data_copy = bytes(self.response_buffer)
                    self.current_request.response_callback(data_copy)

            self.response_buffer.clear()
            self.current_request = None 
            state = ComThreadState.SEND_REQUEST

        return state
            

    
    def spontaneous_message(self, resp : bytes):
        print("Spontanous Response:")
        print([hex(x) for x in resp])
        address = int.from_bytes(self.response_buffer[4:6], byteorder='big', signed=False)

        callbacks = self.spontaneous_callbacks.get(address, None)
        if callbacks is not None:
            for callback in callbacks:
                callback(resp)
       
    def register_spontaneous_callback(self, address : int, callback : Callable[[bytes], Any]):
        self.spontaneous_callbacks[address].append(callback)


    # JSONSerializable implementation
    def from_json(self, json_data : dict):
        com_interface_object = json_data.get("com_interface")

        if com_interface_object is None:
            print("Malformed ComInterface.json: 'com_interface' entry missing!")
            return False

        serial_port_object = com_interface_object.get("serial_port")

        if serial_port_object is None:
            print("Malformed ComInterface.json: 'serial_port' entry missing!")
            return False
        
        self.ser.setPort(serial_port_object)

    def to_json(self):
        com_interface_json = {
            "com_interface" : {
                "serial_port" : self.ser.port,
            }
        }

        return com_interface_json
    