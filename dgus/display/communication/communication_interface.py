 # 
 # This file is part of python-dgus (https://github.com/seho85/python-dgus).
 # Copyright (c) 2022 Sebastian Holzgreve
 # 
 # This program is free software: you can redistribute it and/or modify  
 # it under the terms of the GNU General Public License as published by  
 # the Free Software Foundation, version 3.
 #
 # This program is distributed in the hope that it will be useful, but 
 # WITHOUT ANY WARRANTY; without even the implied warranty of 
 # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
 # General Public License for more details.
 #
 # You should have received a copy of the GNU General Public License 
 # along with this program. If not, see <http://www.gnu.org/licenses/>.
 #


from collections import defaultdict
from concurrent.futures import thread
from enum import Enum
import json

import queue
import threading
from typing import Any, Callable
from time import time, sleep
# import serial
from serial import Serial, SerialException
from dgus.display.communication.dgus_cmd import DGUSCmd
from dgus.display.communication.request import Request
from dgus.display.serialization.json_serializable import JsonSerializable


import logging

RESERVED_MEMORY_ADDRESS = 0x0FFF
READ_RESPONSE_SLEEP = 0.02

class ComThreadState(Enum):
    WAIT_FOR_NEW_RESPONSE = 0
    WAIT_FOR_RESPONSE_TO_COMPLETE = 1
    RESPONSE_COMPLETE = 2
    SEND_REQUEST = 3


class SerialCommunication(JsonSerializable):
    _ser = Serial()
    _com_thread: thread

    _response_buffer: bytearray = bytearray()

    requests = queue.Queue()
    _mutex = threading.Lock()

    _spontaneous_callbacks = defaultdict(list)

    _awaited_bytes = 0
    _current_request : Request = None

    _wait_for_response_timeout = 1
    _time_send = 0

    _run_com_thread = False

    _com_opened = False

    _serial_port_com_event_changed_receiver : Callable[[bool], Any] = None
    
    logger = logging.getLogger(__name__)

    def __init__(self, serial_port : str, baudrate : int = 115200) -> None:
        self._ser.port = serial_port
        self._ser.baudrate = baudrate

    def __del__(self):
        self.requests.queue.clear()

    def queue_request(self, request: Request):
        with self._mutex:
            self.requests.put(request)

    def _open_com_port(self) -> bool:
        try:
            self._ser.open()

            if  self._serial_port_com_event_changed_receiver is not None:
                 self._serial_port_com_event_changed_receiver(True)
            return True
        except SerialException:
            #self.logger.error("Unable to open serial interface %s", self._ser.port)
            return False

    def start_com_thread(self):
        self._com_opened = self._open_com_port()
        if self._com_opened:
            self._com_thread = threading.Thread(target=self._com_thread_function)
            self._run_com_thread = True
            self._com_thread.start()
            self.logger.info("Started serial communication...")
            return True
        return False

    def stop(self):
        if self._run_com_thread:
            self._run_com_thread = False
            self._com_thread.join()
            self.logger.info("Stopped serial display communication...")

    def _com_thread_function(self):

        state = ComThreadState.SEND_REQUEST

        while self._run_com_thread:

            if self._com_opened:
                try:
                    state = self._do_serial_communication(state)
                except OSError as error:
                    if error.errno == 5:
                        print('An exception occurred: {}'.format(error))
                        self._com_opened = False
                        self._ser.cancel_read()
                        self._ser.cancel_write()
                        self._ser.close()

            else:
                try:
                    self._com_opened = self._open_com_port()

                    if self._com_opened == False:
                        sleep(2)
                    else:
                        state = ComThreadState.SEND_REQUEST
                        self._response_buffer.clear()

                except OSError as error:
                    sleep(1)

                

            #sleep(0.2)

    def _do_serial_communication(self, state: ComThreadState) -> ComThreadState:
        if state == ComThreadState.SEND_REQUEST:
            self._time_send = time()
            with self._mutex:
                if self.requests.empty():
                    return ComThreadState.WAIT_FOR_NEW_RESPONSE

                self._current_request = self.requests.get()
                req_bytes = self._current_request.get_request_data()

                self.logger.info("Sending Request '%s'", self._current_request.name)
                self.logger.debug('Tx: %s', [hex(x) for x in req_bytes])
                
                self._ser.write(req_bytes)
                self._time_send = time()
                return ComThreadState.WAIT_FOR_NEW_RESPONSE
                
            

        if state == ComThreadState.WAIT_FOR_NEW_RESPONSE:
            if self._ser.in_waiting >= 3:
                header_data = self._ser.read(3)
                self._awaited_bytes = header_data[2]
                self._response_buffer.extend(header_data)
                return ComThreadState.WAIT_FOR_RESPONSE_TO_COMPLETE

            if time() - self._time_send > self._wait_for_response_timeout:
                if not self.requests.empty():
                    return ComThreadState.SEND_REQUEST
            
            sleep(READ_RESPONSE_SLEEP)


        if state == ComThreadState.WAIT_FOR_RESPONSE_TO_COMPLETE:
            if self._ser.in_waiting >= self._awaited_bytes:
                data_read = self._ser.read(self._awaited_bytes)
                self._response_buffer.extend(data_read)
                #state = ComThreadState.RESPONSE_COMPLETE
                return ComThreadState.RESPONSE_COMPLETE
            
            return ComThreadState.WAIT_FOR_RESPONSE_TO_COMPLETE

        if state == ComThreadState.RESPONSE_COMPLETE:
            
            function = self._response_buffer[3]
            address = int.from_bytes(self._response_buffer[4:6], byteorder='big', signed=False)

            

            
            
            
            if function == DGUSCmd.READ_VPS:
                if address <= RESERVED_MEMORY_ADDRESS:
                    # we got a spontanous data transmission in between, 
                    # handle it an jump back to reading
                    data_copy = bytes(self._response_buffer)
                    

                    self._spontaneous_message_received(data_copy)
                    self._response_buffer.clear()
                    state = ComThreadState.WAIT_FOR_NEW_RESPONSE
                    return state
            # TODO: Add checking for confirmation message
            if self._current_request is not None:
                self.logger.info("Received response for '%s'", self._current_request.name)
                self.logger.debug('Rx: %s', [hex(x) for x in self._response_buffer])
                self.logger.info("Calling ResponseCallback: '%s'", self._current_request.response_callback)
                if self._current_request.response_callback is not None:
                    data_copy = bytes(self._response_buffer)
                    self._current_request.response_callback(data_copy)
            #TODO: Add Warning when data is received when current request is None, and which is not a spontanous transmission
            self._response_buffer.clear()
            self._current_request = None 
            return ComThreadState.SEND_REQUEST

        return state
            

    
    def _spontaneous_message_received(self, resp : bytes):
        self.logger.info("Received Spontanous data")
        self.logger.debug('Rx: %s', [hex(x) for x in resp])        

        address = int.from_bytes(resp[4:6], byteorder='big', signed=False)

        callbacks = self._spontaneous_callbacks.get(address, None)
        if callbacks is not None:
            self.logger.info("Calling registered callbacks for address %s", address)
            self.logger.debug('Callbacks: %s', callbacks)#[x for x in callbacks])        
            for callback in callbacks:
                callback(resp)
       
    def register_spontaneous_callback(self, address : int, callback : Callable[[bytes], Any]):
        self._spontaneous_callbacks[address].append(callback)
        self.logger.info("Spontanous callback '%s' for address %s registered", callback, address)


    # JSONSerializable implementation
    def from_json(self, json_data : dict):
        com_interface_object = json_data.get("com_interface")

        if com_interface_object is None:
            self.logger.error("JSON deserialization failed: JSON data doesn't contain 'com_interface' object!")
            return False

        serial_port_object = com_interface_object.get("serial_port")

        if serial_port_object is None:
            self.logger.error("JSON deserialization failed: JSON data doesn't contain 'serial_port' element!")
            return False
        
        self._ser.setPort(serial_port_object)
        return True

    def to_json(self):
        com_interface_json = {
            "com_interface" : {
                "serial_port" : self._ser.port,
            }
        }

        return com_interface_json
    
    def write_json_config(self, serial_config_json_file):
        try:
            with open(serial_config_json_file, "w") as json_file:
                json_file.write(json.dumps(self.to_json(), indent=3))
                
        except FileNotFoundError:
            self.logger.critical("Could not open: %s", serial_config_json_file)
        

    def read_json_config(self, serial_config_json_file):
        try:
            with open(serial_config_json_file) as json_file:
                json_data = json.load(json_file)
                return self.from_json(json_data)
                
        except FileNotFoundError:
            self.logger.critical("Could not open: %s", serial_config_json_file)
            return False