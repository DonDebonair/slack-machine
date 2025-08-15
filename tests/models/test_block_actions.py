from machine.models.interactive import BlockActionsPayload, InteractivePayload
from tests.models.example_payloads.block_action_button import payload as button_payload
from tests.models.example_payloads.block_action_button2 import payload as button_payload2
from tests.models.example_payloads.block_action_button_enterprise import payload as button_enterprise_payload
from tests.models.example_payloads.block_action_button_no_value import payload as button_no_value_payload
from tests.models.example_payloads.block_action_checkboxes import payload as checkboxes_payload
from tests.models.example_payloads.block_action_checkboxes2 import payload as checkboxes_payload2
from tests.models.example_payloads.block_action_datepicker import payload as datepicker_payload
from tests.models.example_payloads.block_action_datepicker2 import payload as datepicker_payload2
from tests.models.example_payloads.block_action_in_modal import payload as in_modal_payload
from tests.models.example_payloads.block_action_multi_select import payload as multi_static_select_payload
from tests.models.example_payloads.block_action_multi_select_channel import payload as multi_channels_select_payload
from tests.models.example_payloads.block_action_overflow import payload as overflow_payload
from tests.models.example_payloads.block_action_radio_button import payload as radio_button_payload
from tests.models.example_payloads.block_action_select import payload as static_select_payload
from tests.models.example_payloads.block_action_select_conversation import payload as conversations_select_payload
from tests.models.example_payloads.block_action_timepicker import payload as timepicker_payload
from tests.models.example_payloads.block_action_url_input import payload as url_payload


def test_block_action_radio_button():
    validated_radio_button_payload = InteractivePayload.validate_python(radio_button_payload)
    assert validated_radio_button_payload is not None
    assert isinstance(validated_radio_button_payload, BlockActionsPayload)


def test_block_action_button():
    validated_button_payload = InteractivePayload.validate_python(button_payload)
    assert validated_button_payload is not None
    assert isinstance(validated_button_payload, BlockActionsPayload)
    validated_button_payload2 = InteractivePayload.validate_python(button_payload2)
    assert validated_button_payload2 is not None
    assert isinstance(validated_button_payload2, BlockActionsPayload)
    validated_button_no_value_payload = InteractivePayload.validate_python(button_no_value_payload)
    assert validated_button_no_value_payload is not None
    assert isinstance(validated_button_no_value_payload, BlockActionsPayload)


def test_block_action_button_enterprise():
    validated_button_enterprise_payload = InteractivePayload.validate_python(button_enterprise_payload)
    assert validated_button_enterprise_payload is not None
    assert isinstance(validated_button_enterprise_payload, BlockActionsPayload)


def test_block_action_checkboxes():
    validated_checkboxes_payload = InteractivePayload.validate_python(checkboxes_payload)
    assert validated_checkboxes_payload is not None
    assert isinstance(validated_checkboxes_payload, BlockActionsPayload)
    validated_checkboxes_payload2 = InteractivePayload.validate_python(checkboxes_payload2)
    assert validated_checkboxes_payload2 is not None
    assert isinstance(validated_checkboxes_payload2, BlockActionsPayload)


def test_block_action_datepicker():
    validated_datepicker_payload = InteractivePayload.validate_python(datepicker_payload)
    assert validated_datepicker_payload is not None
    assert isinstance(validated_datepicker_payload, BlockActionsPayload)
    validated_datepicker_payload2 = InteractivePayload.validate_python(datepicker_payload2)
    assert validated_datepicker_payload2 is not None
    assert isinstance(validated_datepicker_payload2, BlockActionsPayload)


def test_block_action_static_select():
    validated_static_select_payload = InteractivePayload.validate_python(static_select_payload)
    assert validated_static_select_payload is not None
    assert isinstance(validated_static_select_payload, BlockActionsPayload)


def test_block_action_conversations_select():
    validated_conversations_select_payload = InteractivePayload.validate_python(conversations_select_payload)
    assert validated_conversations_select_payload is not None
    assert isinstance(validated_conversations_select_payload, BlockActionsPayload)


def test_block_action_multi_static_select():
    validated_multi_static_select_payload = InteractivePayload.validate_python(multi_static_select_payload)
    assert validated_multi_static_select_payload is not None
    assert isinstance(validated_multi_static_select_payload, BlockActionsPayload)


def test_block_action_multi_channels_select():
    validated_multi_channels_select_payload = InteractivePayload.validate_python(multi_channels_select_payload)
    assert validated_multi_channels_select_payload is not None
    assert isinstance(validated_multi_channels_select_payload, BlockActionsPayload)


def test_block_action_timepicker():
    validated_timepicker_payload = InteractivePayload.validate_python(timepicker_payload)
    assert validated_timepicker_payload is not None
    assert isinstance(validated_timepicker_payload, BlockActionsPayload)


def test_block_action_url_input():
    validated_url_payload = InteractivePayload.validate_python(url_payload)
    assert validated_url_payload is not None
    assert isinstance(validated_url_payload, BlockActionsPayload)


def test_block_action_overflow():
    validated_overflow_payload = InteractivePayload.validate_python(overflow_payload)
    assert validated_overflow_payload is not None
    assert isinstance(validated_overflow_payload, BlockActionsPayload)


def test_block_action_in_modal():
    validated_in_modal_payload = InteractivePayload.validate_python(in_modal_payload)
    assert validated_in_modal_payload is not None
    assert isinstance(validated_in_modal_payload, BlockActionsPayload)
