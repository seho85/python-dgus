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

import logging
from queue import LifoQueue
from typing import Any, Callable
from dgus.display.communication.communication_interface import SerialCommunication
from dgus.display.communication.protocol import build_mask_switch_request
from dgus.display.communication.request import Request
from dgus.display.mask import Mask


class Display():
    serial_communication_interface : SerialCommunication = None
    
    _active_mask : Mask = None
    
    previous_masks : LifoQueue = LifoQueue()
    
    _display_masks : dict = {}
    logger = logging.getLogger(__name__)

    def __init__(self, serial_communication_interface) -> None:
        self.act_mask_idx = 0
        self.serial_communication_interface = serial_communication_interface
        if serial_communication_interface is not None:
            serial_communication_interface.register_spontaneous_callback(0x0004, self._display_changed_mask)

    
    def _display_changed_mask(self, data : bytes):
        mask_bytes = data[7:]
        mask_index = int.from_bytes(mask_bytes,  byteorder='big')

        self.logger.info("Spontanous 'Change Display Mask' to MaskNo: %s'", mask_index)

        show_previous_mask = mask_index == 0xFFFF

        if show_previous_mask:
            
            if(self.previous_masks.qsize() > 0):

                prev_mask = self.previous_masks.get()

                self.logger.info("Switching to previous Mask %s", prev_mask.mask_no)
                
                self.switch_to_mask(prev_mask.mask_no, False)

            else:
                self.logger.warning("Switch to previous mask: No mask in history!")
                   
        else:
            mask = self._display_masks.get(mask_index)

            if mask is not None:
                self.logger.info("Switching to Mask %s", mask_index)
                self.switch_to_mask(mask_index)
            else:
                self.logger.warning("No Mask register with for maskNo %s", mask_index)


    def add_mask(self, msk : Mask):
        self._display_masks[msk.mask_no] = msk


    def _mask_switch_response(self, data):
        self._active_mask.mask_shown()

    def switch_to_mask(self, mask_idx : int, add_to_history : bool = True) -> bool:
        msk = self._display_masks.get(mask_idx)

        if msk is None:
            self.logger.error("Can't switch to MaskNo %s, no Mask found with the MaskNo %s", mask_idx, mask_idx)
            return False

        

        if add_to_history:
            if self._active_mask is not None:
                self.previous_masks.put(self._active_mask)
                self.logger.debug("Add MaskNo %s to Mask history", mask_idx)


        if self._active_mask is not None:
            self._active_mask.mask_suppressed()
            
        self._active_mask = msk

        req = Request(self._get_switch_mask_request, self._mask_switch_response, f"Display - Switch to Image {mask_idx}")
        self.serial_communication_interface.queue_request(req)
            
        return True
            
    def _get_switch_mask_request(self):
        switch_mask_cmd = build_mask_switch_request(self._active_mask.mask_no)
        return switch_mask_cmd

    def read_config_data_for_all_controls(self):
        ##TODO: Check if serial_comm_interface is running - when if not we run into while true forever

        for msk in self._display_masks.values():
            for ctrl in msk.controls:
                ctrl.config_data_has_been_read = False
                ctrl.read_config_data()

        
        while True:
            all_config_has_been_read = True

            for msk in self._display_masks.values():
                for ctrl in msk.controls:
                    if not ctrl.config_data_has_been_read:
                        all_config_has_been_read = False

            if all_config_has_been_read:
                break

    def write_config_data_for_all_controls(self):
        for msk in self._display_masks.values():
            for ctrl in msk.controls:
                ctrl.send_config_data()

    def update_current_mask(self):
        for ctrl in self._active_mask.controls:
            ctrl.send_data()


    #TODO: Move to communication_interface
    def register_spontaneous_response_cb(self, address : int, callback : Callable[[bytes], Any]):
        self.serial_communication_interface.register_spontaneous_callback(address, callback)
