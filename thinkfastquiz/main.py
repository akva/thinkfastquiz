import fastapi
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from thinkfastquiz import utils
from thinkfastquiz import gamelib


BROADCASTER = utils.Broadcaster()


class Game(BaseModel):
    position: int
    question: str


class Attempt(BaseModel):
    position: int
    answer: str


class Response(BaseModel):
    game: Game
    message: str | None


def game_at(position):
    q, _ = gamelib.qna_at(position)
    return Game(position=position, question=q)


async def join(ws):
    """User first joins the game"""
    game = game_at(gamelib.current_position())
    resp = Response(game=game, message=None)
    await ws.send_text(resp.model_dump_json())


async def attempt(ws, attempt: Attempt):
    """User attempts to answer a question"""
    pos = attempt.position
    _, a = gamelib.qna_at(pos)
    if a == attempt.answer:
        new_pos = gamelib.claim_answer(pos)
        if new_pos is not None:
            game = game_at(new_pos)
            await ws.send_text(Response(
                game=game,
                message="Correct!"
            ).model_dump_json())
            await BROADCASTER.broadcast(Response(
                game=game,
                message="Too slow!"
            ).model_dump_json(), ws)
        # else don't need to do anything.
        # sombody already answered this question and notifications have been sent.
    else:
        # don't retrieve the actual current position as it is pretty slow.
        # the user will get the actual position eventually.
        await ws.send_text(Response(
            game=game_at(pos),
            message="Oops (: Try harder"
        ).model_dump_json())


RPC = utils.WcRpc([join, attempt])


api = fastapi.FastAPI(title="api")
@api.websocket("/ws")
async def handle_websocket(ws: fastapi.WebSocket):
    await BROADCASTER.accept(ws)
    while True:
        try:
            text = await ws.receive_text()
        except fastapi.WebSocketDisconnect:
            BROADCASTER.forget(ws)
        else:
            await RPC.dispatch(ws, text)


def make_app():
    app = fastapi.FastAPI(title="app")
    app.mount("/api", api)
    app.mount("/", StaticFiles(directory="thinkfastquiz/web", html=True), name="web")
    return app


app = make_app()
