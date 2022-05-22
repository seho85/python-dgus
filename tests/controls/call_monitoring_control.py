from dgus.display.controls.control import Control

class CallMonitoringControl(Control):

    read_config_data_implementation_was_called = False

    def __init__(self, control_type, data_address, data_length, config_address, config_length) -> None:
        super().__init__(control_type, data_address, data_length, config_address, config_length)

    def _read_config_data_implementation(self):
        self.read_config_data_implementation_was_called = True
    
    def send_data(self):
        pass

    
    def settings_from_json(self):
        pass

    
    def settings_to_json(self):
        pass