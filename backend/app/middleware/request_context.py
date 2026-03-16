from contextvars import ContextVar, Token
from uuid import uuid4

from fastapi import FastAPI, Request, Response

REQUEST_ID_HEADER = "X-Request-ID"
_request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


def get_request_id() -> str | None:
	return _request_id_ctx.get()

def register_request_context_middleware(app: FastAPI) -> None:
	@app.middleware("http")
	async def request_context_middleware(request: Request, call_next):
		incoming_request_id = request.headers.get(REQUEST_ID_HEADER)
		request_id = (incoming_request_id or "").strip() or uuid4().hex

		token: Token[str | None] = _request_id_ctx.set(request_id)
		try:
			response: Response = await call_next(request)
		finally:
			_request_id_ctx.reset(token)

		response.headers[REQUEST_ID_HEADER] = request_id
		return response
