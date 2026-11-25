from __future__ import annotations

from pathlib import Path
from typing import Iterable

from markitdown import MarkItDown


SUPPORTED_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".html", ".htm", ".txt", ".md", ".csv", ".json", ".xml",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp",
}


class ConversionError(Exception):
    pass


class MarkdownConverter:
    def __init__(self) -> None:
        self.engine = MarkItDown(enable_plugins=False)

    def is_supported(self, path: str | Path) -> bool:
        return Path(path).suffix.lower() in SUPPORTED_EXTENSIONS

    def convert(self, source: str | Path, destination: str | Path | None = None) -> Path:
        source_path = Path(source).expanduser()
        if not source_path.is_file():
            raise ConversionError(f"No existe el archivo: {source_path}")
        if not self.is_supported(source_path):
            raise ConversionError(f"Formato no admitido: {source_path.suffix or '(sin extensión)'}")

        try:
            result = self.engine.convert(str(source_path))
            content = result.text_content
        except Exception as exc:
            raise ConversionError(f"No se pudo convertir {source_path.name}: {exc}") from exc

        if destination is None:
            output_path = source_path.with_suffix(".md")
        else:
            output_path = Path(destination).expanduser() / f"{source_path.stem}.md"

        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.exists():
            output_path = self._next_available_path(output_path)

        output_path.write_text(content, encoding="utf-8")
        return output_path

    def convert_many(
        self,
        sources: Iterable[str | Path],
        destination: str | Path | None = None,
        progress_callback=None,
    ) -> tuple[list[Path], list[str]]:
        items = [Path(item).expanduser() for item in sources]
        successful: list[Path] = []
        errors: list[str] = []

        for index, source in enumerate(items, start=1):
            if progress_callback:
                progress_callback(index - 1, len(items), source.name)
            try:
                successful.append(self.convert(source, destination))
            except ConversionError as exc:
                errors.append(str(exc))

        if progress_callback:
            progress_callback(len(items), len(items), "Completado")
        return successful, errors

    @staticmethod
    def _next_available_path(path: Path) -> Path:
        counter = 1
        candidate = path
        while candidate.exists():
            candidate = path.with_name(f"{path.stem} ({counter}){path.suffix}")
            counter += 1
        return candidate
