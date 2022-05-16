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

    #displayMasks : list[Mask] = []
    
    display_masks : dict = {}

    def __init__(self, serial_communication_interface) -> None:
        self.act_mask_idx = 0
        self.serial_communication_interface = serial_communication_interface

    def add_mask(self, msk : Mask):
        self.display_masks[msk.mask_no] = msk

    def switch_to_mask(self, mask_idx : int) -> bool:
        msk = self.display_masks.get(mask_idx)
        if msk is not None:
            self.active_mask = msk
            req = Request(self.get_switch_mask_request, None, "Switch Image")
            self.serial_communication_interface.queue_request(req)
            return True

        else:
            print(f"Error: Can't switch to MaskNo {mask_idx}, no Mask found with the MaskNo {mask_idx}")
            return False


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
            for msk in self.display_masks.values():
                for ctrl in msk.controls:
                    if not ctrl.config_data_has_been_read:
                        sleep(0.2)
                        continue

            break

    def update_current_mask(self):
        for ctrl in self.active_mask.controls:
            ctrl.send_data()




    #TODO: Move to communication_interface
    def register_spontaneous_response_cb(self, address : int, callback : Callable[[bytes], Any]):
        self.serial_communication_interface.register_spontaneous_callback(address, callback)
