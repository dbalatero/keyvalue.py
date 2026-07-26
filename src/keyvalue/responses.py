from typing import Literal

from pydantic import BaseModel, ConfigDict, TypeAdapter


class ResponseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


# Used for set and delete
class MutationSuccessResponse(ResponseModel):
    ok: Literal[True]


class KeysSuccessResponse(ResponseModel):
    ok: Literal[True]
    keys: list[str]


class GetSuccessResponse(ResponseModel):
    ok: Literal[True]
    value: None | str


class ErrorResponse(ResponseModel):
    ok: Literal[False]
    message: str


Response = (
    MutationSuccessResponse | KeysSuccessResponse | GetSuccessResponse | ErrorResponse
)

_response_adapter = TypeAdapter(Response)


def encode_response(response: Response) -> bytes:
    return response.model_dump_json().encode("utf-8") + b"\n"
