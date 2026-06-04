import json
from datetime import datetime
from pathlib import Path

from app.interfaces.email_service import EmailService


class FileEmailService(EmailService):
    def __init__(self, output_path: str | Path) -> None:
        self.output_path = Path(output_path)

    def send(self, to: str, subject: str, body: str) -> None:
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "to": to,
            "subject": subject,
            "body": body,
            "sent_at": datetime.now().isoformat(),
        }
        with self.output_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload) + "\n")
