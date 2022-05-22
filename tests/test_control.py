from tests.controls.call_monitoring_control import CallMonitoringControl
from dgus.display.controls.control import Control, ControlTypeEnum

#CallMonitoringControl.__test__ = False


def test_when_config_address_is_to_ffff_read_config_implemenation_is_not_called():
    testing_control = CallMonitoringControl(ControlTypeEnum.DATA_VARIABLE, 0x0000, 2, 0xFFFF, 2)
    testing_control.read_config_data()

    assert not testing_control.read_config_data_implementation_was_called