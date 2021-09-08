import os
import json

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, ValidationError, constr, conint

app = FastAPI()


HTML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'index.html')


@app.get("/")
async def get():
    with open(HTML_PATH) as html_file:
        return HTMLResponse(html_file.read())


class Message(BaseModel):
    message: constr(min_length=1)
    number: conint(ge=0)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = {'status': 'OK'}
        raw_data = await websocket.receive_text()
        try:
            data.update(Message.parse_raw(raw_data).dict())
            data['number'] += 1
        except ValidationError:
            data = {'status': 'error', 'message': 'Нужно заполнить поле message'}
        await websocket.send_text(json.dumps(data))