"""Datamodellen die tussen de verschillende onderdelen worden uitgewisseld."""

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ParsedLogEntry:
    """Een succesvol geparste syslogregel."""

    datetime: str
    server: str
    service: str
    message: str


@dataclass(frozen=True, slots=True)
class ImportResult:
    """Samenvatting van één importactie."""

    imported_count: int
    failed_count: int
    skipped_empty_count: int = 0
    failed_line_numbers: tuple[int, ...] = field(default_factory=tuple)
