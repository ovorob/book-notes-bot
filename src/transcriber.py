from openai import AsyncOpenAI


class Transcriber:

    def __init__(self, client: AsyncOpenAI) -> None:
        self.client = client

    async def transcribe(self, audio: bytes) -> str:
        transcription = await self.client.audio.transcriptions.create(
            model="gpt-transcribe",
            file=("voice.ogg", audio, "audio/ogg")
        )
        return transcription.text