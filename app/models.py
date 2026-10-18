"""Validated API payloads shared by the routers."""

from datetime import date as CalendarDate
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Payload(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class DataItemCreate(Payload):
    date: CalendarDate
    value: float = Field(allow_inf_nan=False)
    memo: str = Field(default="", max_length=1000)


class DataItemUpdate(Payload):
    date: CalendarDate | None = None
    value: float | None = Field(default=None, allow_inf_nan=False)
    memo: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def validate_changes(self):
        if not self.model_fields_set or any(
            getattr(self, name) is None for name in self.model_fields_set
        ):
            raise ValueError("Provide at least one non-null field")
        return self


class DataItemResponse(DataItemCreate):
    id: str


class Message(Payload):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=8000)


class ConversationCreate(Payload):
    title: str = Field(min_length=1, max_length=100)
    messages: list[Message] = Field(min_length=1, max_length=100)


class ChatRequest(Payload):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = Field(
        default=None, pattern=r"^[A-Za-z0-9_-]{1,128}$"
    )
