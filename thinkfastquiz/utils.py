import typing
import inspect

from pydantic import BaseModel


class Broadcaster:
    def __init__(self):
        self._websockets = []

    async def accept(self, websocket):
        await websocket.accept()
        self._websockets.append(websocket)

    def forget(self, ws):
        self._websockets.remove(ws)

    async def broadcast(self, text, but=None):
        for ws in self._websockets:
            if ws != but:
                try:
                    await ws.send_text(text)
                except Exception:  # RuntimeError?
                    self.forget(ws)


# Ad-hoc RPC over websockets

class Request(BaseModel):
    name: str
    body: typing.Any = None


class WcRpc:
    def __init__(self, handlers):
        self._routes = {}
        for f in handlers:
            sig = inspect.signature(f)
            params = list(sig.parameters.values())
            self._routes[f.__name__] = (
                params[1].annotation if len(params) > 1 else None,
                f
            )

    async def dispatch(self, ws, text):
        call = Request.model_validate_json(text)
        h = self._routes.get(call.name)
        if h:
            body_model, f = h
            if body_model:
                await f(ws, body_model.model_validate(call.body))
            else:
                await f(ws)
