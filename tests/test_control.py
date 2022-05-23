from tests.controls.call_monitoring_control import CallMonitoringControl
from dgus.display.controls.control import ControlTypeEnum

#CallMonitoringControl.__test__ = False


def test_when_config_address_is_to_ffff_read_config_implemenation_is_not_called():
    testing_control = CallMonitoringControl(ControlTypeEnum.TESTING_CONTROL, 0x0000, 2, 0xFFFF, 2)
    testing_control.read_config_data()

    assert not testing_control.read_config_data_implementation_was_called


def test_json_serialization():
    testing_control = CallMonitoringControl(ControlTypeEnum.TESTING_CONTROL, 0x0000, 2, 0xFFFF, 2)
    serialized_json = testing_control.to_json()

    control_obj = serialized_json.get("control")
    assert control_obj is not None

    ctrl_type_obj = control_obj.get("control_type")
    assert ctrl_type_obj is not None
    assert str(ctrl_type_obj) == ControlTypeEnum.get_serialization_repr(ControlTypeEnum.TESTING_CONTROL)

    data_address_obj = control_obj.get("data_address")
    assert data_address_obj is not None
    assert int(data_address_obj) == 0x0000

    data_length_obj = control_obj.get("data_length")
    assert data_length_obj is not None
    assert int(data_length_obj) == 2

    config_address_obj = control_obj.get("config_address")
    assert config_address_obj is not None
    assert int(config_address_obj) == 0xffff