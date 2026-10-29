from enum import StrEnum

from pydantic import BaseModel


class EntryType(StrEnum):
    character = "character"
    thought = "thought"
    lesson = "lesson"
    quote = "quote"
    summary = "summary"


class Entry(BaseModel):
    type: EntryType
    content: str
    character_name: str | None


class ParsedNote(BaseModel):
    book: str | None
    author: str | None
    entries: list[Entry]


def format_note(note: ParsedNote):
    format_list = []

    book = "not specified" if not note.book else note.book
    format_list.append(f"Book: {book}")
    if note.author:
        format_list.append(f"Author: {note.author}")

    for entry in note.entries:
        if entry.character_name:
            format_list.append(
                f"{entry.type.capitalize()} ({entry.character_name}): {entry.content}"
            )
            continue
        format_list.append(f"{entry.type.capitalize()}: {entry.content}")
    return "\n".join(format_list)
