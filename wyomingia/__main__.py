#!/usr/bin/env python3
import argparse
import asyncio
import logging
from functools import partial

from wyoming.info import AsrModel, AsrProgram, Attribution, Info
from wyoming.server import AsyncServer

from . import __version__
from .handler import GladiaEventHandler

_LOGGER = logging.getLogger(__name__)


async def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--uri", required=True, help="unix:// or tcp://")
    parser.add_argument(
        "--language",
        help="Default language to set for transcription",
    )
    parser.add_argument("--debug", action="store_true", help="Log DEBUG messages")
    parser.add_argument(
        "--log-format", default=logging.BASIC_FORMAT, help="Format for log messages"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=__version__,
        help="Print version and exit",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO, format=args.log_format
    )
    _LOGGER.debug(args)

    wyoming_info = Info(
        asr=[
            AsrProgram(
                name="wyomingia",
                description="Gladia Real-Time Speech-To-Text (STT)",
                attribution=Attribution(
                    name="Wyomingia",
                    url="https://github.com/tnesztler/wyomingia",
                ),
                installed=True,
                version=__version__,
                models=[
                    AsrModel(
                        name="fast",
                        description="Fast model",
                        attribution=Attribution(
                            name="Gladia",
                            url="https://gladia.io",
                        ),
                        installed=True,
                        languages=[
                            "af",
                            "am",
                            "ar",
                            "as",
                            "az",
                            "ba",
                            "be",
                            "bg",
                            "bn",
                            "bo",
                            "br",
                            "bs",
                            "ca",
                            "cs",
                            "cy",
                            "da",
                            "de",
                            "el",
                            "en",
                            "es",
                            "et",
                            "eu",
                            "fa",
                            "fi",
                            "fo",
                            "fr",
                            "gl",
                            "gu",
                            "ha",
                            "haw",
                            "he",
                            "hi",
                            "hr",
                            "ht",
                            "hu",
                            "hy",
                            "id",
                            "is",
                            "it",
                            "ja",
                            "jw",
                            "ka",
                            "kk",
                            "km",
                            "kn",
                            "ko",
                            "la",
                            "lb",
                            "ln",
                            "lo",
                            "lt",
                            "lv",
                            "mg",
                            "mi",
                            "mk",
                            "ml",
                            "mn",
                            "mr",
                            "ms",
                            "mt",
                            "my",
                            "ne",
                            "nl",
                            "nn",
                            "no",
                            "oc",
                            "pa",
                            "pl",
                            "ps",
                            "pt",
                            "ro",
                            "ru",
                            "sa",
                            "sd",
                            "si",
                            "sk",
                            "sl",
                            "sn",
                            "so",
                            "sq",
                            "sr",
                            "su",
                            "sv",
                            "sw",
                            "ta",
                            "te",
                            "tg",
                            "th",
                            "tk",
                            "tl",
                            "tr",
                            "tt",
                            "uk",
                            "ur",
                            "uz",
                            "vi",
                            "yi",
                            "yo",
                            "yue",
                            "zh",
                        ],
                        version="2",
                    )
                ],
            )
        ],
    )

    server = AsyncServer.from_uri(args.uri)
    _LOGGER.info("Ready")
    lock = asyncio.Lock()
    await server.run(
        partial(
            GladiaEventHandler,
            wyoming_info,
            args,
            lock,
        )
    )


# -----------------------------------------------------------------------------


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        pass
