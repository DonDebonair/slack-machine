from machine.models.interactive import InteractivePayload, ViewClosedPayload, ViewSubmissionPayload
from tests.models.example_payloads.view_closed import payload as view_closed_payload
from tests.models.example_payloads.view_submission import payload as view_submission_payload


def test_view_submission():
    validated_view_submission_payload = InteractivePayload.validate_python(view_submission_payload)
    assert validated_view_submission_payload is not None
    assert isinstance(validated_view_submission_payload, ViewSubmissionPayload)


def test_view_closed():
    validated_view_closed_payload = InteractivePayload.validate_python(view_closed_payload)
    assert validated_view_closed_payload is not None
    assert isinstance(validated_view_closed_payload, ViewClosedPayload)
