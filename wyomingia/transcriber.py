import asyncio
import json
import logging
import os
import time

import requests
import websockets
import websockets.asyncio
import websockets.asyncio.client
import websockets.asyncio.connection
from wyoming.audio import AudioChunk

_LOGGER = logging.getLogger(__name__)


class GladiaTranscriber:
    custom_vocabulary: list[str]
    gladia_key: str

    data: dict[str, str] = {}

    def __init__(self):
        key: str | None = os.environ.get("GLADIA_KEY")
        if key is None:
            raise ValueError(
                "A valid GLADIA_KEY (API key) is required by this transcriber"
            )
        self.gladia_key = key
        self.custom_vocabulary = [
            word for word in os.environ.get("CUSTOM_VOCABULARY", "").split(",") if word
        ]
        if len(self.custom_vocabulary):
            _LOGGER.info(f"Using custom vocabulary config: {self.custom_vocabulary}")

    async def transcribe(self, chunks: list[AudioChunk], language: str) -> str:
        _LOGGER.debug("Transcription started…")
        first_chunk = chunks[0]
        _LOGGER.debug("Getting websocket URL…")
        id, url = self._get_websocket_url(
            language, first_chunk.rate, first_chunk.width, first_chunk.channels
        )
        _LOGGER.debug(f"Connecting to Gladia: {url}")
        async with websockets.asyncio.client.connect(url) as ws:
            _LOGGER.debug("Connected")
            await asyncio.gather(self.producer(ws, chunks), self.consumer(ws, id))
            _LOGGER.debug("Transcription complete")
        text = self.data.pop(id)
        return text

    async def producer(
        self,
        ws: websockets.asyncio.client.ClientConnection,
        chunks: list[AudioChunk],
    ) -> None:
        _LOGGER.debug("Sending audio chunks…")
        for audio_chunk in chunks:
            start = time.time()
            await ws.send(audio_chunk.audio)
            end = time.time()
            if (end - start) < audio_chunk.seconds:
                await asyncio.sleep(audio_chunk.seconds - (end - start))
            else:
                await asyncio.sleep(0)
        _LOGGER.debug(f"{len(chunks)} audio chunks sent")
        await ws.send(json.dumps({"type": "stop_recording"}))

    async def consumer(
        self, ws: websockets.asyncio.client.ClientConnection, id: str
    ) -> str:
        async for data in ws:
            message = json.loads(data)
            _LOGGER.debug(message)
            if message["type"] == "post_transcript":
                self.data[id] = message["data"]["full_transcript"]
            await asyncio.sleep(0)

    def _get_websocket_url(
        self, language: str, rate: int, width: int, channels: int
    ) -> tuple[str, str]:
        config = {
            "language_config": {"languages": [language]},
            "sample_rate": rate,
            "bit_depth": 8 * width,
            "channels": channels,
            "messages_config": {
                "receive_acknowledgments": False,
                "receive_partial_transcripts": False,
            },
        }
        if len(self.custom_vocabulary):
            config["realtime_processing"] = {
                "custom_vocabulary": True,
                "custom_vocabulary_config": {"vocabulary": self.custom_vocabulary},
            }
        request = requests.post(
            "https://api.gladia.io/v2/live",
            json=config,
            headers={"X-Gladia-Key": self.gladia_key},
        )
        data = request.json()
        _LOGGER.debug(data)
        if "url" in data:
            return data["id"], data["url"]
        else:
            _LOGGER.error(data)
            raise Exception("Limit reached")
