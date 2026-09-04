"""Shared config for HM16LIBRARY generators.

Single source of truth for base URL, parsing, and file discovery
so generate_api.py and generate_opds.py stay consistent.
"""
import os

# Repo was renamed HM16_LIBRARY -> HM16LIBRARY, so Pages URL has no underscore.
BASE_URL = "https://hmhashemali16.github.io/HM16LIBRARY"
ICON_URL = f"{BASE_URL}/Bookicon.png"

BOOK_DIR = "."
SKIP_DIRS = {".git", ".github", "api", ".opencode"}

SUPPORTED_EXTS = {
    ".epub": "application/epub+zip",
    ".pdf": "application/pdf",
}

UNKNOWN_AUTHOR_API = "অজানা"
UNKNOWN_AUTHOR_OPDS = "অজানা লেখক"


def iter_book_files(book_dir=BOOK_DIR):
    """Yield book filenames sorted, case-insensitive ext, skip dirs."""
    try:
        names = sorted(os.listdir(book_dir))
    except OSError:
        return
    for name in names:
        if name in SKIP_DIRS:
            continue
        path = os.path.join(book_dir, name)
        try:
            if not os.path.isfile(path):
                continue
        except OSError:
            continue
        _, ext = os.path.splitext(name)
        if ext.lower() in SUPPORTED_EXTS:
            yield name


def parse_filename(filename):
    """Parse 'Title_-_Author.ext' -> (title, author, format).

    Uses partition (first separator only) so titles containing _-_ don't diverge.
    """
    stem, _ = os.path.splitext(filename)
    _, ext = os.path.splitext(filename)
    title_part, sep, author_part = stem.partition("_-_")
    if sep:
        title = title_part.replace("_", " ").strip() or stem
        author = author_part.replace("_", " ").strip()
    else:
        title = stem.replace("_", " ").strip()
        author = ""
    fmt = ext.lower().lstrip(".")
    return title, author, fmt
