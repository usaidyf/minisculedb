import json
from dataclasses import dataclass
from typing import Literal


@dataclass
class Response:
    code: dict[Literal["status", "action"], str]
    value: str | None = None
    message: str | None = None

    def serialize(
        self, mode: Literal["json", "plain_text", "python_tuple"] | None = None
    ) -> str:

        if mode == "json":
            return json.dumps(
                {
                    "response_code": f"{self.code['status']}:{self.code['action']}",
                    "value": self.value,
                    "message": self.message,
                }
            )

        if mode == "python_tuple":
            return (f"{self.code['status']}:{self.code['action']}", self.value, self.message)

        parts = [f"{self.code['status']}:{self.code['action']}"]
        if self.value:
            parts.append(self.value)
        if self.message:
            parts.append(self.message)
        return "\n".join(parts)
