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
import json
import os
from dgus.display.communication.communication_interface import RESERVED_MEMORY_ADDRESS
from dgus.display.controls.control import ControlTypeEnum
from dgus.display.display import Display


def deserialize_json_check(disp : Display) -> bool:
    display_json_file = os.path.join(os.getcwd(), "config", "display.json")

    display_json_deserialized = False
    with open(display_json_file, encoding="utf-8") as json_file:
        json_data = json.load(json_file)
        display_json_deserialized = disp.from_json(json_data)
        if display_json_deserialized is True:
            print("JSON Config: OK")

    return display_json_deserialized

def generate_data_area_dict_and_print_masks_and_ctrl(disp : Display) -> defaultdict(list):
    generated_data_area_dict = defaultdict(list)
    print("Listing of all Display Masks and Controls:")
    for mask in disp.displayMasks:
        print(f'Mask {mask.mask_no:02}')
        ctrl_idx = 0
        for ctrl in mask.controls:
            print()
            print(f"Mask[{mask.mask_no}] Ctrl[{ctrl_idx}] ({ControlTypeEnum.get_serialization_repr(ctrl.control_type)})")
            print(f"Data:   {hex(ctrl.dataAddress)} {hex(ctrl.dataAddress + ctrl.dataLength)}")
            print(f"Config: {hex(ctrl.configAddress)} {hex(ctrl.configAddress + ctrl.configLength)}")
            print("")

            i = ctrl.dataAddress
            while i < ctrl.dataAddress + ctrl.dataLength:
                generated_data_area_dict[i].append(f'Mask[{mask.mask_no}] Ctrl[{ctrl_idx}] DataAddress')
                i += 1

            i = ctrl.configAddress
            while i <= ctrl.configAddress + ctrl.configLength:
                generated_data_area_dict[i].append(f'Mask[{mask.mask_no}] Ctrl[{ctrl_idx}] ConfigAddress')
                i += 1

            ctrl_idx += 1

    return generated_data_area_dict

def print_overlapping_memory_areas(data_area_dictonary : defaultdict(list)) -> bool:
    print("Overlapping Memory Areas:")
    address = "Address"
    controls = "Controls"
    found_an_overlapping_addresses = False
    print(f"{address:<10}{controls:<12}")
    for key, value in data_area_dictonary.items():
        if len(value) > 1:
            found_an_overlapping_addresses = True
            print(f'{hex(key):<10}{value}')

    if found_an_overlapping_addresses:
        print("\nOverlapping Address found!")
    else:
        print("\nNo overlapping Address found!")

    return found_an_overlapping_addresses


def check_reserved_ram_area() -> bool:
    print("\nChecking reserved address space (for 'Auto Upload')")
    found_a_reserved_ram_area_conflict = False
    for key, value in data_area_dict.items():
        if key < RESERVED_MEMORY_ADDRESS:
            found_a_reserved_ram_area_conflict = True
            print(f'{hex(key)} {value} conflicts with reserved RAM address space')

    return found_a_reserved_ram_area_conflict


if __name__ == "__main__":

    display = Display(None)

    json_ok = deserialize_json_check(display)

    data_area_dict = generate_data_area_dict_and_print_masks_and_ctrl(display)

    FOUND_OVERLAPPING_ADDRESS = print_overlapping_memory_areas(data_area_dict)

    FOUND_RESERVED_RAM_AREA_CONFLICT = check_reserved_ram_area()


if FOUND_OVERLAPPING_ADDRESS is False and FOUND_RESERVED_RAM_AREA_CONFLICT and json_ok:
    print('\nSanity check passed!')
else:
    print("\nSanity check FAILED!")
