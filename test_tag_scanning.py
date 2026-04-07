import asyncio
import tempfile
from pathlib import Path

import memory


def _with_temp_memory_db():
    temp_dir = tempfile.TemporaryDirectory()
    original_db_path = memory.DB_PATH
    memory.DB_PATH = str(Path(temp_dir.name) / "memory.db")
    asyncio.run(memory.init_db())
    return temp_dir, original_db_path


def test_scan_messages_for_tags_matches_existing_tags_only():
    messages = [
        "recipe: chocolate cake",
        "just chatting here",
        "TODO buy oat milk",
        "recipe - banana bread",
        "untagged reminder",
    ]

    matched, counts = memory.scan_messages_for_tags(messages, ["recipe", "todo"])

    assert matched == [
        "recipe: chocolate cake",
        "TODO buy oat milk",
        "recipe - banana bread",
    ]
    assert counts == {"recipe": 2, "todo": 1}


def test_scan_messages_for_tags_prefers_longest_matching_tag():
    messages = ["favorite food sushi", "fav quick note"]

    matched, counts = memory.scan_messages_for_tags(messages, ["fav", "favorite food"])

    assert matched == ["favorite food sushi", "fav quick note"]
    assert counts == {"fav": 1, "favorite food": 1}


def test_add_notes_batch_can_ignore_existing_exact_duplicates():
    temp_dir, original_db_path = _with_temp_memory_db()
    try:
        asyncio.run(memory.add_note("recipe: banana bread"))

        added = asyncio.run(
            memory.add_notes_batch(
                [
                    "recipe: banana bread",
                    "recipe: banana bread",
                    "recipe: blueberry muffins",
                    "recipe: blueberry muffins",
                ],
                ignore_exact_duplicates=True,
            )
        )
        notes = list(reversed(asyncio.run(memory.list_notes())))

        assert added == 1
        assert [note_text for _, note_text, _ in notes] == [
            "recipe: banana bread",
            "recipe: blueberry muffins",
        ]
    finally:
        memory.DB_PATH = original_db_path
        temp_dir.cleanup()


def test_prune_duplicate_notes_keeps_earlier_exact_and_newer_similar():
    temp_dir, original_db_path = _with_temp_memory_db()
    try:
        asyncio.run(memory.add_note("recipe: banana bread"))
        asyncio.run(memory.add_note("recipe: banana bread"))
        asyncio.run(memory.add_note("meeting with Alex at 3pm"))
        asyncio.run(memory.add_note("meeting with Alex at 4pm"))

        summary = asyncio.run(memory.prune_duplicate_notes())
        notes = list(reversed(asyncio.run(memory.list_notes())))

        assert summary == {"exact_removed": 1, "similar_removed": 1, "total_removed": 2}
        assert [note_text for _, note_text, _ in notes] == [
            "recipe: banana bread",
            "meeting with Alex at 4pm",
        ]
    finally:
        memory.DB_PATH = original_db_path
        temp_dir.cleanup()
