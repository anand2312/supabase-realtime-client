from __future__ import annotations

import asyncio
import json
import logging
from collections import defaultdict
from functools import wraps
from typing import Any, Callable

import websockets

from realtime.channel import Channel
from realtime.exceptions import ConnectionFailedError, NotConnectedError
from realtime.message import HEARTBEAT_PAYLOAD, PHOENIX_CHANNEL, ChannelEvents, Message

logging.basicConfig(
    format="%(asctime)s:%(levelname)s - %(message)s", level=logging.INFO
)


def ensure_connection(func: Callable):
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        if not args[0].connected:
            raise NotConnectedError(func.__name__)

        return func(*args, **kwargs)

    return wrapper


class Socket:
    def __init__(self, url: str, params: dict = {}, hb_interval: int = 5) -> None:
        """
        `Socket` is the abstraction for an actual socket connection that receives and 'reroutes' `Message` according to its `topic` and `event`.
        Socket-Channel has a 1-many relationship.
        Socket-Topic has a 1-many relationship.

        Args:
            url: Websocket URL of the Realtime server. starts with `ws://` or `wss://`
            params: Optional parameters for connection.
            hb_interval: WS connection is kept alive by sending a heartbeat message every few seconds.
        """
        self.url = url
        self.channels: dict[str, list[Channel]] = defaultdict(list)
        self.connected = False
        self.params = params
        self.hb_interval = hb_interval
        self.ws_connection: websockets.client.WebSocketClientProtocol  # type: ignore
        self.kept_alive = False

    @ensure_connection
    async def listen(self) -> None:
        """
        An infinite loop that keeps listening..
        """
        while True:
            try:
                msg = await self.ws_connection.recv()
                msg = Message(**json.loads(msg))
                if msg.event == ChannelEvents.reply:
                    continue
                for channel in self.channels.get(msg.topic, []):
                    for cl in channel.listeners:
                        if cl.event == msg.event:
                            cl.callback(msg.payload)
            except websockets.exceptions.ConnectionClosed:  # type: ignore
                logging.exception("Connection closed")
                break

    async def connect(self) -> None:
        """
        Connect to the realtime server.
        """
        ws_connection = await websockets.connect(self.url)  # type: ignore

        if ws_connection.open:
            logging.info("Connection was successful")
            self.ws_connection = ws_connection
            self.connected = True

        else:
            raise ConnectionFailedError("Connection Failed")

    async def _keep_alive(self) -> None:
        """
        Sending heartbeat to server every 5 seconds
        Ping - pong messages to verify connection is alive
        """
        while True:
            try:
                data = dict(
                    topic=PHOENIX_CHANNEL,
                    event=ChannelEvents.heartbeat,
                    payload=HEARTBEAT_PAYLOAD,
                    ref=None,
                )
                await self.ws_connection.send(json.dumps(data))
                await asyncio.sleep(self.hb_interval)
            except websockets.exceptions.ConnectionClosed:  # type: ignore
                logging.exception("Connection with server closed")
                break

    @ensure_connection
    def set_channel(self, topic: str) -> Channel:
        """
        Args:
            topic: Initializes a channel and creates a two-way association with the socket
        Returns:
            [Channel][realtime.channel.Channel]
        """

        chan = Channel(self, topic, self.params)
        self.channels[topic].append(chan)

        return chan

    def summary(self) -> dict[str, list[Channel]]:
        """
        Gets the list of sockets and events being listened for.
        """
        return self.channels
