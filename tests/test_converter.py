from pathlib import Path

from converter import MarkdownConverter


def test_supported_extension():
    converter = MarkdownConverter()
    assert converter.is_supported("document.docx")
    assert converter.is_supported("photo.PNG")
    assert not converter.is_supported("archive.zip")


def test_next_available_path(tmp_path: Path):
    first = tmp_path / "archivo.md"
    first.write_text("uno", encoding="utf-8")

    result = MarkdownConverter._next_available_path(first)

    assert result.name == "archivo (1).md"
