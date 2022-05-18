
from collections import defaultdict, namedtuple
from dataclasses import dataclass
from math import ceil
import sys
from os import listdir, stat
from os.path import isfile, getsize, join
import re

@dataclass
class FlashFile:
    file_name : str
    start : int
    end : int

    def __init__(self, file_name, start, end) -> None:
        self.file_name = file_name
        self.start = start
        self.end = end


def get_length_in_slots(file_path):
    size = stat(file_path).st_size
    
    len_in_slots = size / (256 * 1024)

    return ceil(len_in_slots)

def get_start_slot_from_filename(filename):
    
    match = re.search('(\d{1,})(?:[a-zA-Z\._-])', filename)
    #print(file)
    #if(match):
    #    print(match.group(1))
    return(int(match.group(1)))


#if len(sys.argv) == 2:
dwin_folder = "/home/sebastian/OHP/VBoxShare/DGUS_GFX/dgus_project/DWIN_SET"#sys.argv[1]

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
end_slot = "End Slot"

print(f'{file:<32}{start_slot:<20}{end_slot:<20}')

for file in files_written_to_flash:
    path = join(dwin_folder, file)
    
    file_name = file
    start_slot = get_start_slot_from_filename(file)
    end_slot = start_slot + get_length_in_slots(path)
    
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