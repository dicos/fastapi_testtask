import os
import sys
import json
import random

from fastapi import FastAPI, WebSocket, Cookie, status, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, ValidationError, constr

app = FastAPI()


HTML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')


SESSIONS = {}


@app.get("/")
async def get(number: str = Cookie(None)):
    if number in SESSIONS:
        del SESSIONS[number]
    session_num = str(random.randint(0, sys.maxsize))
    SESSIONS[session_num] = 0
    with open(HTML_PATH) as html_file:
        response = HTMLResponse(html_file.read())
        response.set_cookie(key="number", value=session_num)
        return response


class Message(BaseModel):
    message: constr(min_length=1)


async def get_cookie(
    websocket: WebSocket,
    number: str = Cookie(None)
):
    if number is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    return number


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, number: str = Depends(get_cookie)):
    await websocket.accept()
    while True:
        data = {'status': 'OK'}
        raw_data = await websocket.receive_text()
        try:
            data.update(Message.parse_raw(raw_data).dict())
            SESSIONS[number] += 1
            data['number'] = SESSIONS[number]
        except ValidationError:
            data = {'status': 'error', 'message': 'Нужно заполнить поле message'}
        await websocket.send_text(json.dumps(data))