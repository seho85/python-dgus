from dgus.display.controls.control import ControlTypeEnum, Control
from dgus.display.mask import Mask
from tests.controls.call_monitoring_control import CallMonitoringControl
from json import dumps

def test_read_control_config_calls_read_config_data_on_all_assigned_controls():

    mask = Mask(0, None)

    test_control1 = CallMonitoringControl(ControlTypeEnum.TESTING_CONTROL, 0x1000, 2, 0x2000, 2)
    mask.controls.append(test_control1)

    test_control2 = CallMonitoringControl(ControlTypeEnum.TESTING_CONTROL, 0x1000, 2, 0x2000, 2)
    mask.controls.append(test_control2)

    mask.read_control_config()

    assert test_control1.read_config_data_implementation_was_called
    assert test_control2.read_config_data_implementation_was_called



def test_mask_send_control_data_calls_send_data_on_all_assigned_controls():
    mask = Mask(0, None)

    test_control1 = CallMonitoringControl(ControlTypeEnum.TESTING_CONTROL, 0x1000, 2, 0x2000, 2)
    mask.controls.append(test_control1)

    test_control2 = CallMonitoringControl(ControlTypeEnum.TESTING_CONTROL, 0x1000, 2, 0x2000, 2)
    mask.controls.append(test_control2)

    mask.send_control_data()

    assert test_control1.send_data_was_called
    assert test_control2.send_data_was_called

'''
def test_mask_to_json_returns_correct_json():
    mask = Mask(0, None)

    test_control1 = CallMonitoringControl(ControlTypeEnum.TESTING_CONTROL, 0x1000, 2, 0x2000, 2)
    mask.controls.append(test_control1)

    test_control2 = CallMonitoringControl(ControlTypeEnum.TESTING_CONTROL, 0x1000, 2, 0x2000, 2)
    mask.controls.append(test_control2)

    serialized_mask_json = mask.to_json()
    #mask_str = dumps(mask_json, indent=3)
    #bp = 1

    mask_json = serialized_mask_json.get("mask")
    assert mask_json is not None

    mask_no_json = mask_json.get("mask_index")
    assert int(mask_no_json) == mask.mask_no

    control_json = mask_json.get("controls")

    # we don't check the controls json, as its already tested in tests_control.py
    # just check that for every ctrl an entry in controls array is created
    assert len(control_json) == len(mask.controls)
'''

def test_mask_to_json_returns_false_when_mask_entry_is_missing():
    mask = Mask(0, None)

    mask_json = { 
        "blubb" : {

        }
    }

    deserialized = mask.from_json(mask_json)

    assert not deserialized


def test_mask_to_json_returns_false_when_mask_index_is_missing():
    mask = Mask(0, None)

    mask_json = { 
        "mask" : {

        }
    }

    deserialized = mask.from_json(mask_json)

    assert not deserialized


def test_mask_from_json_sets_mask_no_accordingly():
    mask = Mask(0, None)

    mask_json = { 
        "mask" : {
            "mask_index" : 42

        }
    }

    mask.from_json(mask_json)

    assert mask.mask_no == 42


def test_mask_to_json_returns_false_when_controls_is_missing():
    mask = Mask(0, None)

    mask_json = { 
        "mask" : {
            "mask_index" : 1

        }
    }

    deserialized = mask.from_json(mask_json)

    assert not deserialized


def test_mask_from_json_returns_false_when_control_is_missing():
    mask = Mask(0, None)

    mask_json = { 
        "mask" : {
            "mask_index" : 1,
            "controls" : [
                {
                    "here_should_be_control" : {}
                }
            ],
        }
    }

    deserialized = mask.from_json(mask_json)

    assert not deserialized

def test_mask_from_json_returns_false_when_control_type_is_missing():
    mask = Mask(0, None)

    mask_json = { 
        "mask" : {
            "mask_index" : 1,
            "controls" : [
                {
                    "control" : {}
                }
            ],
        }
    }

    deserialized = mask.from_json(mask_json)

    assert not deserialized


def test_mask_from_json_returns_false_when_data_address_is_missing():
    mask = Mask(0, None)

    mask_json = { 
        "mask" : {
            "mask_index" : 1,
            "controls" : [
                {
                    "control" : {
                        "control_type" : 42
                    }
                }
            ],
        }
    }

    deserialized = mask.from_json(mask_json)

    assert not deserialized


def test_mask_from_json_returns_false_when_data_length_is_missing():
    mask = Mask(0, None)

    mask_json = { 
        "mask" : {
            "mask_index" : 1,
            "controls" : [
                {
                    "control" : {
                        "control_type" : 42,
                        "data_address" : 42
                    }
                }
            ],
        }
    }

    deserialized = mask.from_json(mask_json)

    assert not deserialized

def test_mask_from_json_returns_false_when_config_address_is_missing():
    mask = Mask(0, None)

    mask_json = { 
        "mask" : {
            "mask_index" : 1,
            "controls" : [
                {
                    "control" : {
                        "control_type" : 42,
                        "data_address" : 42,
                        "data_length" : 42
                    }
                }
            ],
        }
    }

    deserialized = mask.from_json(mask_json)

    assert not deserialized

def test_mask_from_json_raised_value_error_when_control_type_is_not_known():
    mask = Mask(0, None)

    mask_json = { 
        "mask" : {
            "mask_index" : 1,
            "controls" : [
                {
                    "control" : {
                        "control_type" : 42,
                        "data_address" : 42,
                        "data_length" : 42,
                        "config_address" : 42
                    }
                }
            ],
        }
    }

    value_error_raised = False

    try:
        deserialized = mask.from_json(mask_json)
    except ValueError:
        value_error_raised = True

    assert value_error_raised
    

    