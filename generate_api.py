import json
import os
import urllib.parse

from library_config import (
    BASE_URL,
    BOOK_DIR,
    SUPPORTED_EXTS,
    UNKNOWN_AUTHOR_API,
    iter_book_files,
    parse_filename,
)

print("Starting JSON API generation...")
books_api_data = []
seen_files = set()
seen_books = set()

for filename in iter_book_files(BOOK_DIR):
    key = filename.lower()
    if key in seen_files:
        print(f"Warning: duplicate file skipped: {filename}")
        continue
    seen_files.add(key)

    title, author, fmt = parse_filename(filename)
    if not author:
        author = UNKNOWN_AUTHOR_API

    book_key = (title.lower(), author.lower())
    if book_key in seen_books:
        print(f"Warning: duplicate book skipped: {title} - {author}")
        continue
    seen_books.add(book_key)

    # URL-encode Bengali filenames so links don't break
    encoded_filename = urllib.parse.quote(filename)
    download_url = f"{BASE_URL}/{encoded_filename}"

    _, ext = os.path.splitext(filename)
    mime = SUPPORTED_EXTS.get(ext.lower(), "application/octet-stream")

    books_api_data.append(
        {
            "title": title,
            "author": author,
            "file_name": filename,
            "format": fmt,
            "mime_type": mime,
            "download_link": download_url,
        }
    )

# Deterministic order: sort by title (OPDS does the same)
books_api_data.sort(key=lambda b: b["title"])

os.makedirs("api", exist_ok=True)
out_path = os.path.join("api", "books.json")
new_content = json.dumps(books_api_data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"

# Avoid empty churn commits: only write when content changed
old_content = None
if os.path.exists(out_path):
    with open(out_path, "r", encoding="utf-8") as f:
        old_content = f.read()

if old_content != new_content:
    with open(out_path, "w", encoding="utf-8") as json_file:
        json_file.write(new_content)
    print(f"Success: JSON API updated at {out_path} ({len(books_api_data)} books)")
else:
    print(f"No changes: {out_path} already up to date ({len(books_api_data)} books)")
