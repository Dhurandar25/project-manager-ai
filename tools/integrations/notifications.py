"""Injectable Teams and Outlook notification services."""

from __future__ import annotations

from typing import Any, Protocol


class NotificationTransport(Protocol):
    """Transport adapter responsible for authentication and delivery."""

    def send(self, destination: str, subject: str, body: str) -> Any: ...


class TeamsNotificationService:
    """Send notification types using an injected Teams transport."""

    def __init__(self, transport: NotificationTransport, destination: str) -> None:
        if not destination.strip():
            raise ValueError("Teams destination must be configured")
        self._transport = transport
        self._destination = destination

    def risk_notification(self, message: str) -> Any:
        return self._transport.send(self._destination, "Project risk notification", message)

    def daily_executive_summary(self, summary: str) -> Any:
        return self._transport.send(self._destination, "Daily executive summary", summary)

    def approval_request(self, request: str) -> Any:
        return self._transport.send(self._destination, "Approval requested", request)


class OutlookNotificationService:
    """Send email notification types using an injected Outlook transport."""

    def __init__(self, transport: NotificationTransport, recipient: str) -> None:
        if not recipient.strip():
            raise ValueError("Outlook recipient must be configured")
        self._transport = transport
        self._recipient = recipient

    def approval_request(self, request: str) -> Any:
        return self._transport.send(self._recipient, "Project approval requested", request)

    def executive_summary(self, summary: str) -> Any:
        return self._transport.send(self._recipient, "Project executive summary", summary)

    def escalation(self, escalation: str) -> Any:
        return self._transport.send(self._recipient, "Project escalation", escalation)
