from typing import Annotated, Literal

from pydantic import BaseModel, Field, TypeAdapter, ValidationError, field_validator

from keyvalue.keys import validate_key


class GetRequest(BaseModel):
    command: Literal["get"]
    key: str

    _validate_key = field_validator("key")(validate_key)


class SetRequest(BaseModel):
    command: Literal["set"]
    key: str
    value: str

    _validate_key = field_validator("key")(validate_key)


class DeleteRequest(BaseModel):
    command: Literal["delete"]
    key: str

    _validate_key = field_validator("key")(validate_key)


class KeysRequest(BaseModel):
    command: Literal["keys"]


Request = Annotated[
    GetRequest | SetRequest | DeleteRequest | KeysRequest,
    Field(discriminator="command"),
]

_request_adapter = TypeAdapter(Request)


class RequestParseError(ValueError):
    pass


def parse_request(raw: str) -> Request:
    try:
        return _request_adapter.validate_json(raw)
    except ValidationError as error:
        raise RequestParseError(str(error)) from error
