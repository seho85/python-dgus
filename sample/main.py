
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
 
from time import sleep
from overview_display_mask import OverviewDisplayMask
from dgus.display.communication.communication_interface import SerialCommunication
from dgus.display.display import Display



 

if __name__ == "__main__":
    
    SERIAL_PORT = "/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller-if00-port0"
    

    serialCom = SerialCommunication(SERIAL_PORT)
    serialCom.show_transmission_data = True
    
    if serialCom.start_com_thread():
    
        display = Display(serialCom)
        
        overviewMask = OverviewDisplayMask(serialCom)

        display.add_mask(overviewMask)

        #Step on read all config data for a defined controls
        display.read_config_data_for_all_controls()

        if display.switch_to_mask(0):

            while True:
                display.update_current_mask()
                sleep(0.1)

    
