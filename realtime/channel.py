from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Callable, NamedTuple

from realtime.exceptions import RealtimeError

if TYPE_CHECKING:
    from realtime.connection import Socket


class CallbackListener(NamedTuple):
    event: str
    callback: Callable[[Any], Any]  # TODO: improve annotation for callback and payload


class Channel:
    """
    `Channel` is an abstraction for a topic listener for an existing socket connection.
    Each Channel has its own topic and a list of event-callbacks that responds to messages.
    Should only be instantiated through `connection.Socket().set_chanel(topic)`
    Topic-Channel has a 1-many relationship.
    """

    def __init__(self, socket: Socket, topic: str, params: dict = {}) -> None:
        """
        Args:
            socket: Socket object
            topic: Topic to subcribe to on the realtime server
            params:
        """
        self.socket = socket
        self.topic = topic
        self.params: dict = params
        self.listeners: list[CallbackListener] = []
        self.joined: bool = False

    async def join(self) -> None:
        """
        Attempt to join Phoenix Realtime server for a certain topic.
        """
        join_req = {
            "topic": self.topic,
            "event": "phx_join",
            "payload": {},
            "ref": None,
        }

        try:
            await self.socket.ws_connection.send(json.dumps(join_req))
        except Exception as e:
            raise RealtimeError(e)

    def on(self, event: str, callback: Callable[[Any], Any]) -> Channel:
        """
        Args:
            event: A specific event will have a specific callback
            callback: Callback that takes msg payload as its first argument
        Returns:
            [Channel][realtime.channel.Channel]
        """

        cl = CallbackListener(event=event, callback=callback)
        self.listeners.append(cl)
        return self

    def off(self, event: str) -> None:
        """
        Stop listening to a particular event.

        Args:
            event: event to stop responding to
        """
        self.listeners = [
            callback for callback in self.listeners if callback.event != event
        ]
