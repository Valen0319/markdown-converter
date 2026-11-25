from pathlib import Path

from converter import MarkdownConverter


def test_convert_text_file(tmp_path: Path):
    source = tmp_path / "prueba.txt"
    source.write_text("# Prueba\n\nTexto convertido.", encoding="utf-8")

    converter = MarkdownConverter()
    result = converter.convert(source, tmp_path)

    assert result.exists()
    assert "Prueba" in result.read_text(encoding="utf-8")
