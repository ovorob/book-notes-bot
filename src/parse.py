from openai import AsyncOpenAI

from models import ParsedNote


class NoteParser:
    parse_instructions = """
        You are an assistant that turns a reader's dictated notes into structured reading notes.

        The text is a speech transcript, so names and titles may be misheard or spelled wrongly.

        Split the text into entries. One dictation often contains several entries of different
        types. If the reader says the type ("lesson", "my thought", "quote"), use it. Otherwise
        infer the type from the content.

        Entry types:
        - character: facts from the book about a person: who they are, what they do, what
        happens to them. Set character_name to the person's name.
        - thought: the reader's own opinion, reaction, question or connection to their life.
        This includes opinions about a character or the author. If the reader judges a
        character ("I think he is the most honest"), it is a thought, not a character entry,
        and character_name is set to that character.
        - lesson: a takeaway or principle the reader wants to remember and apply.
        - quote: a passage the reader quotes from the book. Keep the quoted words as said.
        - summary: what happens in the plot or in a chapter.

        Cleanup rules:
        - Remove filler words, false starts and repetitions.
        - Fix grammar and spelling.
        - Keep the reader's own words and first person. Do not summarise or rephrase.
        - Do not add any facts the reader did not say.
        - Write in the language the reader used.

        Book and author:
        - book: the title the reader mentions. You may complete a partial title (for example
        "Karamazov" to "The Brothers Karamazov") only if you are confident. Otherwise use the
        title as heard. If no book is mentioned, return null.
        - author: only if the reader says it. Never add it from your own knowledge.
        - character_name: null for entries that are not about a specific character.
    """

    def __init__(self, client: AsyncOpenAI, model: str):
        self.client = client
        self.model = model

    async def parse_message(self, message: str) -> ParsedNote:
        parsed_msg = await self.client.responses.parse(
            model=self.model,
            input=message,
            instructions=self.parse_instructions,
            text_format=ParsedNote,
        )
        return parsed_msg.output_parsed
