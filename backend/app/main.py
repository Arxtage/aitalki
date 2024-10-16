# BACKEND

from fastapi import FastAPI, WebSocket

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


# New WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # Accept the WebSocket connection
    while True:
        data = await websocket.receive_text()  # Receive message from client
        await websocket.send_text(f"Message received: {data}")  # Echo the message back
