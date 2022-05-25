#from asyncore import write
import json
import os
from time import sleep
from typing import Any, Callable
from dgus.display.communication.communication_interface import SerialCommunication
from dgus.display.communication.protocol import build_mask_switch_request
from dgus.display.communication.request import Request
from dgus.display.mask import Mask
from dgus.display.serialization.json_serializable import JsonSerializable

class Display(JsonSerializable):
    serial_communication_interface : SerialCommunication = None
    
    #act_mask_idx : int = 0
    active_mask : Mask = None
    previous_mask : Mask = None

    #displayMasks : list[Mask] = []
    
    display_masks : dict = {}

    def __init__(self, serial_communication_interface) -> None:
        self.act_mask_idx = 0
        self.serial_communication_interface = serial_communication_interface
        if serial_communication_interface is not None:
            serial_communication_interface.register_spontaneous_callback(0x0004, self.display_changed_mask)

    
    def display_changed_mask(self, data : bytes):
        mask_bytes = data[7:]
        mask_index = int.from_bytes(mask_bytes,  byteorder='big')

        if mask_index == 0xFFFF:
            if self.previous_mask is not None:
                print(f'Switched to previous Mask index: {self.previous_mask.mask_no}')
                self.switch_to_mask(self.previous_mask.mask_no)
               
        else:
            mask = self.display_masks.get(mask_index)

            if mask is not None:
                self.previous_mask = self.active_mask
                self.active_mask = mask
            else:
                print(f'Warning: No DisplayMask for Index {mask_index} registered')


    def add_mask(self, msk : Mask):
        self.display_masks[msk.mask_no] = msk

    def switch_to_mask(self, mask_idx : int, previous_mask_idx : int = -1) -> bool:
        msk = self.display_masks.get(mask_idx)
        mask_found = False
        if msk is not None:
            self.previous_mask = self.active_mask
            self.active_mask = msk
            req = Request(self.get_switch_mask_request, None, "Switch Image")
            self.serial_communication_interface.queue_request(req)
            mask_found = True

        if previous_mask_idx >= 0:
            prev_mask = self.display_masks.get(previous_mask_idx)
            if prev_mask is not None:
                self.previous_mask = prev_mask

        if not mask_found:
            print(f"Error: Can't switch to MaskNo {mask_idx}, no Mask found with the MaskNo {mask_idx}")
            
        return mask_found


    def get_switch_mask_request(self):
        switch_mask_cmd = build_mask_switch_request(self.active_mask.mask_no)
        return switch_mask_cmd

    def write_settings_to_file(self, path):
        file = os.path.join(path, "display.json")

        json_content = json.dumps(self.to_json(), indent=3)
        with open(file, "w") as conf_file:
            conf_file.write(json_content)

    def write_masks_to_file(self, path):
        for value in self.display_masks.items():
            file = os.path.join(path, f"mask{value.mask_no:02}.json")
            with open(file, "w") as mask_file:
                mask_file.write(json.dumps(value.to_json(), indent=3))


    #json_serializable implementation
    def from_json(self, json_data : dict):

        display_object = json_data.get("dgus_display")
        if display_object is None:
            print("Malformed JSON: Missing 'dgus_display' object")
            return False

        self.display_masks.clear()
        masks_object = display_object.get("masks")
        for mask_json_file in masks_object:
            mask_file = os.path.join(os.getcwd(), "config", mask_json_file)
            with open(mask_file) as json_file:
                mask_json_data = json.load(json_file)
                
                msk = Mask(0, self.serial_communication_interface, self.web_sock)
                msk.from_json(mask_json_data)
                self.display_masks[msk.mask_no] = msk


        return True

    def to_json(self):

        display_json = {
            "dgus_display" : {
                "masks" : []
            }
        }

        return display_json


    def read_config_data_for_all_controls(self):
        ##TODO: Check if serial_comm_interface is running - when if not we run into while true forever

        for msk in self.display_masks.values():
            for ctrl in msk.controls:
                ctrl.config_data_has_been_read = False
                ctrl.read_config_data()

        
        while True:
            all_config_has_been_read = True

            for msk in self.display_masks.values():
                for ctrl in msk.controls:
                    if not ctrl.config_data_has_been_read:
                        all_config_has_been_read = False

            if all_config_has_been_read:
                break

    def write_config_data_for_all_controls(self):
        for msk in self.display_masks.values():
            for ctrl in msk.controls:
                ctrl.send_config_data()

    def update_current_mask(self):
        for ctrl in self.active_mask.controls:
            ctrl.send_data()




    #TODO: Move to communication_interface
    def register_spontaneous_response_cb(self, address : int, callback : Callable[[bytes], Any]):
        self.serial_communication_interface.register_spontaneous_callback(address, callback)
