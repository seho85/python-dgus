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


'''
This script can used to detected overlapping elements that should be flashed to the DGUS Display.

The creator of the display application is responsible that the different elements that are flashed
to DGUS Display are not overlapping each other.

See "3.2.1 FLASH Space" in "DGUS Application Development Guide"
'''

from collections import defaultdict
from dataclasses import dataclass
from math import ceil
from os import listdir, stat
from os.path import join, basename
import re
from sys import argv
import sys

@dataclass
class FlashFile:
    file_name : str
    start : int
    end : int

    def __init__(self, filename, start, end) -> None:
        self.file_name = filename
        self.start = start
        self.end = end


def get_length_in_slots(file_path):
    size = stat(file_path).st_size
    
    len_in_slots = size / (256 * 1024)

    return ceil(len_in_slots)

def get_start_slot_from_filename(filename):
    
    match = re.search(r'(\d{1,})(?:[a-zA-Z\._-])', filename)
    #print(file)
    #if(match):
    #    print(match.group(1))
    return(int(match.group(1)))


def print_usage():
    print("Usage:")
    print(f'{basename(__file__)} <Path to DWIN_SET folder>')
    


if len(argv) != 2:
    print("Invalid parameters!\n")
    print_usage()
    sys.exit()

dwin_folder = argv[1]

print("DWIN Folder Sanity Check\n")
print(f"Searching DWIN folder {dwin_folder} for colliding files\n\n")

files = listdir(dwin_folder)

files_written_to_flash = []

for file in files:
    #if isfile(file):
    path = join(dwin_folder, file)
    #print(f"{file} : {stat(path).st_size}")

    if ".icl" in file:
        files_written_to_flash.append(file)

    if ".bin" in file:
        files_written_to_flash.append(file)

    if ".HZK" in file:
        files_written_to_flash.append(file)


slot_file_mapping = defaultdict(list)

file = "File"
start_slot = "Start Slot"
end_slot = "Length (Slots)"

print(f'{file:<32}{start_slot:<20}{end_slot:<20}')

for file in files_written_to_flash:
    path = join(dwin_folder, file)
    
    file_name = file
    start_slot = get_start_slot_from_filename(file)
    end_slot = get_length_in_slots(path)
    
    print(f'{file:<32}{start_slot:<20}{end_slot-1:<20}')
    

    i = start_slot
    while i < end_slot:
        slot_file_mapping[i].append(file)
        i += 1

    #print(f'{file} {start_slot} {end_slot}')

sorted_items = sorted(slot_file_mapping.items())
print("\n\nOverlapping Files:")
found_overlapping_files = False
for key, value in sorted_items:
    if len(value) > 1:
        print(f'{key} : {value}')
        found_overlapping_files = True
    
if not found_overlapping_files:
    print("No overlapping files found...")
