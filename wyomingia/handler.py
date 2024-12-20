"""Event handler for clients of the server"""

import argparse
import asyncio
import logging

from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioChunk, AudioStop
from wyoming.event import Event
from wyoming.info import Describe, Info
from wyoming.server import AsyncEventHandler

from .transcriber import GladiaTranscriber

_LOGGER = logging.getLogger(__name__)


class GladiaEventHandler(AsyncEventHandler):
    """Event handler for clients."""

    def __init__(
        self,
        wyoming_info: Info,
        cli_args: argparse.Namespace,
        lock: asyncio.Lock,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.cli_args = cli_args
        self.wyoming_info_event = wyoming_info.event()
        self.lock = lock
        self._chunks: list[AudioChunk] = []
        self._language = self.cli_args.language
        self._transcriber = GladiaTranscriber()

    async def handle_event(self, event: Event) -> bool:
        if AudioChunk.is_type(event.type):
            chunk = AudioChunk.from_event(event)
            self._chunks.append(chunk)
            return True

        if AudioStop.is_type(event.type):
            _LOGGER.debug(
                "Audio stopped. Transcribing…",
            )
            assert len(self._chunks) > 0

            async with self.lock:
                text = await self._transcriber.transcribe(self._chunks, self._language)

            _LOGGER.info(text)

            await self.write_event(Transcript(text=text).event())
            _LOGGER.debug("Completed request")

            # Reset
            self._chunks = []
            self._language = self.cli_args.language

            return False

        if Transcribe.is_type(event.type):
            transcribe = Transcribe.from_event(event)
            if transcribe.language:
                self._language = transcribe.language
                _LOGGER.debug("Language set to %s", transcribe.language)
            return True

        if Describe.is_type(event.type):
            await self.write_event(self.wyoming_info_event)
            _LOGGER.debug("Sent info")
            return True

        return True
