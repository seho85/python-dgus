from dgus.display.controls.control import ControlTypeEnum, Control
from dgus.display.mask import Mask
from tests.controls.call_monitoring_control import CallMonitoringControl


def test_read_control_config_calls_read_config_data_on_all_assigned_controls():

    mask = Mask(0, None)

    test_control1 = CallMonitoringControl(ControlTypeEnum.DATA_VARIABLE, 0x1000, 2, 0x2000, 2)
    mask.controls.append(test_control1)

    test_control2 = CallMonitoringControl(ControlTypeEnum.DATA_VARIABLE, 0x1000, 2, 0x2000, 2)
    mask.controls.append(test_control2)

    mask.read_control_config()

    assert test_control1.read_config_data_implementation_was_called
    assert test_control2.read_config_data_implementation_was_called


