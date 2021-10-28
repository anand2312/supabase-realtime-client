# supabase-realtime-client

Python Client Library to interface with the Phoenix Realtime Server
This is a fork of the [supabase community realtime client library](https://github.com/supabase-community/realtime-py).
I am maintaining this fork, to use it under the hood in another project.

## Quick Start

```python
import asyncio
from realtime.connection import Socket

def callback1(payload):
    print("Callback 1: ", payload)

def callback2(payload):
    print("Callback 2: ", payload)

async def main() -> None:
    URL = "ws://localhost:4000/socket/websocket"
    s = Socket(URL)
    await s.connect()

    # join channels
    channel_1 = s.set_channel("realtime:public:todos")
    await channel_1.join()
    channel_2 = s.set_channel("realtime:public:users")
    await channel_2.join()

    # register callbacks
    channel_1.on("UPDATE", callback1)
    channel_2.on("*", callback2)

    s.listen()  # infinite loop
```

## Sample usage with Supabase

Here's how you could connect to your realtime endpoint using Supabase endpoint. Correct as of 5th June 2021. Please replace `SUPABASE_ID` and `API_KEY` with your own `SUPABASE_ID` and `API_KEY`. The variables shown below are fake and they will not work if you try to run the snippet.

```python
import asyncio
from realtime.connection import Socket

SUPABASE_ID = "dlzlllxhaakqdmaapvji"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYW5vbiIsImlhdCI6MT"


def callback1(payload):
    print("Callback 1: ", payload)

async def main() -> None:
    URL = f"wss://{SUPABASE_ID}.supabase.co/realtime/v1/websocket?apikey={API_KEY}&vsn=1.0.0"
    s = Socket(URL)
    await s.connect()

    channel_1 = s.set_channel("realtime:*")
    await channel_1.join()
    channel_1.on("UPDATE", callback1)

    s.listen()
```

Then, go to the Supabase interface and toggle a row in a table. You should see a corresponding payload show up in your console/terminal.
