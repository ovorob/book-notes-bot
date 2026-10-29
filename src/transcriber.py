from openai import AsyncOpenAI


class Transcriber:
    def __init__(self, client: AsyncOpenAI, model: str) -> None:
        self.client = client
        self.model = model

    async def transcribe(self, audio: bytes) -> str:
        transcription = await self.client.audio.transcriptions.create(
            model=self.model, file=("voice.ogg", audio, "audio/ogg")
        )
        return transcription.text
