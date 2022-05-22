from dgus.display.communication.communication_interface import SerialCommunication
from dgus.display.controls.control import Control
from dgus.display.controls.data_variable import DataVariable
from dgus.display.controls.text_variable import TextVariable

from dgus.display.serialization.json_serializable import JsonSerializable
class Mask(JsonSerializable):

    controls = list[Control]
    _com_interface : SerialCommunication = None
    mask_no : int = 0

    def __init__(self, mask_no, com_interface : SerialCommunication) -> None:
        self.controls = []
        self.mask_no = mask_no
        self._com_interface = com_interface


    def read_control_config(self):
        for ctrl in self.controls:
            ctrl.read_config_data()

    def send_control_data(self):
        for ctrl in self.controls:
            ctrl.send_data()


    def print_address_space_usage(self):
        for ctrl in self.controls:
            print(ctrl.get_used_addres_space())


    def from_json(self, json):
        mask_object = json.get("mask")
        if mask_object is None:
            print("Malformed Mask JSON: 'mask' object not found!")
            return False
        mask_index_object = mask_object.get("mask_index")
        if mask_index_object is None:
            print("Malformed Mask JSON: 'mask_index' not found")
            return False
        else:
            self.mask_no = mask_index_object

        controls_object = mask_object.get("controls")
        if controls_object is None:
            print("Malformed Mask JSON: 'controls' array not found!")
            return False

        self.controls.clear()

        for ctrl in controls_object:
            control_object = ctrl.get("control")
            if control_object is None:
                print("Malformed Mask JSON: Missing 'control' object in 'controls' array!")
                return False

            control_type_object = control_object.get("control_type")
            if control_type_object is None:
                print("Malformed Mask JSON no 'control_type' entry found!")
                return False


            data_address_object = control_object.get("data_address")
            if data_address_object is None:
                print("Malformed Mask JSON no 'data_adress' entry found!")
                return False

            data_length_object = control_object.get("data_length")
            if data_length_object is None:
                print("Malformed Mask JSON: No 'data_length' entry found!")
                return False

            config_address_object = control_object.get("config_address")
            if config_address_object is None:
                print("Malformed Mask JSON: No 'config_address' entry found!")
                return False

            moonraker_data_object = control_object.get("moonraker_data")
            if moonraker_data_object is None:
                print("Malformed Mask JSON: No 'moonraker_data' entry found!")
                return False

            controls_ctor_dict = {
                "DataVariable" : DataVariable,
                "TextVariable" : TextVariable
            }

            ctor = controls_ctor_dict.get(control_type_object)

            if ctor is None:
                raise ValueError( f"{control_type_object} is a undefined control_type_enum value!")

            #print("Found Control in JSON:")
            #print(f"Type:           {control_type_object}")
            #print(f"DataAddress:    {data_address_object}")
            #print(f"DataLength:     {data_length_object}")
            #print(f"ConfigAddress:  {config_address_object}")
            #print(f'Moonraker Data: {moonraker_data_object}')

            ctrl = ctor(self._com_interface, data_address_object, data_length_object,
            config_address_object, moonraker_data_object)

            #TODO: Pass settings
            self.controls.append(ctrl)

        return True


    def to_json(self):
        mask_json = {
            "mask" : {
                "mask_index" : self.mask_no,
                "controls" : []
            }
        }

        for ctrl in self.controls:
            mask_json["mask"]["controls"].append(ctrl.to_json())

        return mask_json
            