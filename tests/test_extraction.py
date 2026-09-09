from pathlib import Path

import pytest

from backend.app.extraction import ExtractionError, clean_text, extract_text


def test_clean_text_preserves_words_and_removes_blank_lines():
    assert clean_text("  Water   is blue. \n\n Plants grow. ") == "Water is blue.\nPlants grow."


def test_unsupported_file_is_rejected(tmp_path: Path):
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")
    with pytest.raises(ExtractionError, match="Unsupported"):
        extract_text(path)

