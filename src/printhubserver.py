import websocket
import json
import threading
import time

from src.printhubqueue import PrintHubQueue

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler('printer.log', mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class PrintHubServer(websocket.WebSocketApp):
    def __init__(self, url, queue, topic="realtime:demo-topic", access_token=""):
        self.queue = queue
        self.topic = topic
        self.access_token = access_token
        super().__init__(url, on_open=self.on_connect, on_message=self.on_message, on_close=self.on_close)
    
    def send_auth_token(self):
        if(self.access_token):
            auth_token = {
                "event": "access_token",
                "topic": self.topic,
                "payload": {
                    "access_token": self.access_token
                },
                "ref": None
            }
            self.send(json.dumps(auth_token))
    
    def send_refresh_token(self):
        heartbeat_token = {
            "event": "heartbeat",
            "topic": self.topic,
            "payload": {},
            "ref": None
        }
        while True:
            logger.debug("Sending heartbeat")
            self.send(json.dumps(heartbeat_token))
            time.sleep(30)
    
    def on_connect(self, ws):
        logger.info("Connected to PrintHub Server")
        # TODO update channel config to file server
        channel_config = {
            "event": "phx_join",
            "topic": self.topic,
            "payload": {
                "config": {
                    "postgres_changes": [
                        {
                        "event": "*",
                        "schema": "public",
                        "table": "file_storage"
                        }
                    ]
                }
            },
            "ref": None
        }
        self.send(json.dumps(channel_config))
        self.send_auth_token()
        self.refreshThread = threading.Timer(30, self.send_refresh_token)
        self.refreshThread.start()
        self.queueExecuter = threading.Thread(target=lambda : self.queue.execute())
        self.queueExecuter.start()

    def on_message(self, ws, message):
        msg = json.loads(message)
        if msg["event"] == "postgres_changes":    
            # print("Received update: ", msg["payload"]["data"]["record"])
            record = msg["payload"]["data"]["record"]
            if (record["status"][0] == "PENDING"):
                self.queue.add(record)

    def on_close(self, ws):
        logger.info("Disconnected from PrintHub Server")
        self.refreshThread.cancel()    
        self.queueExecuter.cancel()