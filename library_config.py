"""Shared config for HM16LIBRARY generators.

Single source of truth for base URL, parsing, and file discovery
so generate_api.py and generate_opds.py stay consistent.
"""
import os

# Repo was renamed HM16_LIBRARY -> HM16LIBRARY, so Pages URL has no underscore.
BASE_URL = "https://hmhashemali16.github.io/HM16LIBRARY"
ICON_URL = f"{BASE_URL}/Bookicon.png"

BOOK_DIR = "."
SKIP_DIRS = {".git", ".github", "api", ".opencode", "node_modules"}

SUPPORTED_EXTS = {
    ".epub": "application/epub+zip",
    ".pdf": "application/pdf",
}

UNKNOWN_AUTHOR_API = "অজানা"
UNKNOWN_AUTHOR_OPDS = "অজানা লেখক"


def iter_book_files(book_dir=BOOK_DIR):
    """Yield book paths (relative, sorted) from BOOK_DIR and subfolders.

    Books live in Book1/, Book2/, ... Skips tooling dirs. Case-insensitive ext.
    """
    for root, dirs, files in os.walk(book_dir):
        dirs[:] = sorted(
            d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")
        )
        for name in sorted(files):
            _, ext = os.path.splitext(name)
            if ext.lower() not in SUPPORTED_EXTS:
                continue
            full = os.path.join(root, name)
            try:
                if not os.path.isfile(full):
                    continue
            except OSError:
                continue
            yield os.path.relpath(full, book_dir).replace(os.sep, "/")


def parse_filename(path):
    """Parse 'Title_-_Author.ext' -> (title, author, format).

    Accepts subfolder paths (Book1/Title_-_Author.epub); parses the basename.
    Uses partition (first separator only) so titles containing _-_ don't diverge.
    """
    filename = os.path.basename(path)
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
