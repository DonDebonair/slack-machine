from machine.clients.slack import SlackClient
from machine.models.interactive import ViewClosedPayload, ViewSubmissionPayload


class ModalSubmission:
    payload: ViewSubmissionPayload

    def __init__(self, client: SlackClient, payload: ViewSubmissionPayload):
        self._client = client
        self.payload = payload


class ModalClosure:
    payload: ViewClosedPayload

    def __init__(self, client: SlackClient, payload: ViewClosedPayload):
        self._client = client
        self.payload = payload
