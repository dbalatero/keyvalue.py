from keyvalue.requests import (
    DeleteRequest,
    GetRequest,
    KeysRequest,
    Request,
    RequestParseError,
    SetRequest,
    parse_request,
)
from keyvalue.responses import (
    ErrorResponse,
    GetSuccessResponse,
    KeysSuccessResponse,
    MutationSuccessResponse,
    Response,
    encode_response,
)
from keyvalue.store import Store


# Given a request that has come in from the server, we talk to the store and
# handle it.
#
# Returns a response to send back.
def handle_command(store: Store, request: Request) -> Response:
    match request:
        case DeleteRequest(key=key):
            store.delete(key)
            return MutationSuccessResponse(ok=True)
        case GetRequest(key=key):
            return GetSuccessResponse(ok=True, value=store.get(key))
        case SetRequest(key=key, value=value):
            store.set(key, value)
            return MutationSuccessResponse(ok=True)
        case KeysRequest():
            return KeysSuccessResponse(ok=True, keys=store.keys())


def process_request(store: Store, raw: str) -> bytes:
    try:
        request = parse_request(raw)
        response = handle_command(store, request)
    except (RequestParseError, ValueError, OSError) as error:
        response = ErrorResponse(ok=False, message=str(error))

    return encode_response(response)
