from models import Entry, EntryType, ParsedNote, format_note


def test_book_line_shows_title():

    note = ParsedNote(
        book="Dune",
        author=None,
        entries=[
            Entry(
                type=EntryType.lesson,
                content="Fear is the mind-killer.",
                character_name=None,
            ),
        ],
    )

    formatted_note = format_note(note=note)

    assert formatted_note.startswith("Book: Dune")


def test_missing_book_shows_not_specified():

    note = ParsedNote(
        book=None,
        author=None,
        entries=[
            Entry(type=EntryType.quote, content="Life is great!", character_name=None)
        ],
    )

    formatted_note = format_note(note=note)

    assert "Book: not specified" in formatted_note


def test_character_formating():

    note = ParsedNote(
        book=None,
        author=None,
        entries=[
            Entry(
                type=EntryType.character,
                content="Dmitri is the oldest brother, really hot-tempered, always in debt.",
                character_name="Dmitri",
            ),
            Entry(
                type=EntryType.thought,
                content="I think honestly he’s the most honest of the three, which is weird.",
                character_name="Dmitri",
            ),
        ],
    )

    formatted_note = format_note(note=note)

    assert (
        "Character (Dmitri):" in formatted_note
        and "Thought (Dmitri):" in formatted_note
    )


def test_no_character():

    note = ParsedNote(
        book=None,
        author=None,
        entries=[
            Entry(
                type=EntryType.character,
                content="Dmitri is the oldest brother, really hot-tempered, always in debt.",
                character_name=None,
            ),
            Entry(
                type=EntryType.thought,
                content="I think honestly he’s the most honest of the three, which is weird.",
                character_name=None,
            ),
        ],
    )

    formatted_note = format_note(note=note)

    assert "Character:" in formatted_note
    assert "Thought:" in formatted_note


def test_book_author_present():

    note = ParsedNote(
        book="Dune",
        author="Frank Herbert",
        entries=[
            Entry(
                type=EntryType.lesson,
                content="Fear is the mind-killer.",
                character_name=None,
            ),
        ],
    )

    formatted_note = format_note(note=note)

    assert "Author: Frank Herbert" in formatted_note


def test_book_author_not_present():

    note = ParsedNote(
        book="Dune",
        author=None,
        entries=[
            Entry(
                type=EntryType.lesson,
                content="Fear is the mind-killer.",
                character_name=None,
            ),
        ],
    )

    formatted_note = format_note(note=note)

    assert "Author:" not in formatted_note
