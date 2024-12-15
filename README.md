# Wyomingia

_Implementation of the [Wyoming Protocol](https://github.com/rhasspy/wyoming) using [Gladia](https://www.gladia.io)'s Realtime v2 API_

It can be used inside [Home Assistant](https://www.home-assistant.io/integrations/wyoming/) to enable [**Assist**](https://www.home-assistant.io/voice_control/) (Voice Assistant), especially its [Speech-to-Text](https://www.home-assistant.io/integrations/stt/) capability.

## Setup

This project was setup using [uv](https://docs.astral.sh/uv/) package manager.

You can install dependencies using `uv sync`.

## Build and Run

You can run the Wyoming server using:

1. Python's virtual environment

```bash
uv run --env-file .env -- python3 -m wyomingia --uri tcp://0.0.0.0:3000
```

The `.env` file should contain at least the `GLADIA_KEY` variable.

```ini
GLADIA_KEY=…
```

2. Docker

```bash
docker build . -t wyomingia:latest
docker run -p 3000:3000 -e GLADIA_KEY=XXX -it wyomingia
```

The server will be available on port 3000.

## Configuration

- `GLADIA_KEY` (_Required_): Your Gladia API key, available following Gladia's [documentation](https://docs.gladia.io/chapters/introduction/getting-started#get-your-api-key)
- `CUSTOM_VOCABULARY` (_Optional_): A list of **comma-separated** words that will be used to enhanced your transcription. See Gladia's [documentation](https://docs.gladia.io/chapters/live-stt/features#custom-vocabulary) for more details

## Footer

> [!NOTE]  
> This project is **not** affiliated with Gladia or any of its subsidiaries.
