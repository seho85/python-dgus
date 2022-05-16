
from time import sleep
from dgus.display.communication.communication_interface import SerialCommunication
from dgus.display.display import Display

from overview_display_mask import OverviewDisplayMask


 

if __name__ == "__main__":
    
    SERIAL_PORT = "/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller-if00-port0"
    PRINTER_IP = "10.0.1.69"
    PORT = 7125

    serialCom = SerialCommunication(SERIAL_PORT)
    
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

    
