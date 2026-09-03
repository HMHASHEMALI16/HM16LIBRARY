import datetime
import html
import os
import urllib.parse
import uuid
import xml.etree.ElementTree as ET

from library_config import (
    BASE_URL,
    BOOK_DIR,
    ICON_URL,
    SUPPORTED_EXTS,
    UNKNOWN_AUTHOR_OPDS,
    iter_book_files,
    parse_filename,
)

xml_path = "catalog.xml"

ATOM_NS = "http://www.w3.org/2005/Atom"
OPDS_NS = "http://opds-spec.org/2010/catalog"
ET.register_namespace("", ATOM_NS)
ET.register_namespace("opds", OPDS_NS)


def qn(ns, tag):
    return f"{{{ns}}}{tag}"


# Single timestamp for the whole feed (deterministic per run,
# per-entry timestamps use file mtime so unchanged books don't churn).
now = datetime.datetime.now(datetime.timezone.utc)
now_iso = now.isoformat().replace("+00:00", "Z")

feed = ET.Element(qn(ATOM_NS, "feed"))
ET.SubElement(feed, qn(ATOM_NS, "id")).text = "urn:uuid:hmhashemali-opds-library"
ET.SubElement(feed, qn(ATOM_NS, "title")).text = "HM 16 LIBRARY"
ET.SubElement(feed, qn(ATOM_NS, "updated")).text = now_iso
author_el = ET.SubElement(feed, qn(ATOM_NS, "author"))
ET.SubElement(author_el, qn(ATOM_NS, "name")).text = "HM Hashem Ali"
ET.SubElement(
    feed,
    qn(ATOM_NS, "link"),
    {
        "rel": "self",
        "href": f"{BASE_URL}/catalog.xml",
        "type": "application/atom+xml;profile=opds-catalog;kind=navigation",
    },
)
ET.SubElement(
    feed,
    qn(ATOM_NS, "link"),
    {
        "rel": "start",
        "href": f"{BASE_URL}/catalog.xml",
        "type": "application/atom+xml;profile=opds-catalog;kind=navigation",
    },
)

books = []
seen = set()
for filename in iter_book_files(BOOK_DIR):
    key = filename.lower()
    if key in seen:
        print(f"Warning: duplicate file skipped: {filename}")
        continue
    seen.add(key)

    title, author, _fmt = parse_filename(filename)
    if not author:
        author = UNKNOWN_AUTHOR_OPDS
    books.append({"title": title, "author": author, "filename": filename})

books.sort(key=lambda x: x["title"])

for book in books:
    path = os.path.join(BOOK_DIR, book["filename"])
    try:
        mtime = os.path.getmtime(path)
        updated = datetime.datetime.fromtimestamp(
            mtime, tz=datetime.timezone.utc
        ).isoformat().replace("+00:00", "Z")
    except OSError:
        updated = now_iso

    encoded_filename = urllib.parse.quote(book["filename"])
    download_url = f"{BASE_URL}/{encoded_filename}"
    # Stable ID: uuid5 from URL so renames don't collide and IDs are valid UUIDs
    stable_id = uuid.uuid5(uuid.NAMESPACE_URL, f"{BASE_URL}/{book['filename']}")

    _, ext = os.path.splitext(book["filename"])
    mime = SUPPORTED_EXTS.get(ext.lower(), "application/octet-stream")

    # ElementTree handles XML escaping automatically (incl. URLs)
    entry = ET.SubElement(feed, qn(ATOM_NS, "entry"))
    ET.SubElement(entry, qn(ATOM_NS, "title")).text = book["title"]
    entry_author = ET.SubElement(entry, qn(ATOM_NS, "author"))
    ET.SubElement(entry_author, qn(ATOM_NS, "name")).text = book["author"]
    ET.SubElement(entry, qn(ATOM_NS, "id")).text = f"urn:uuid:{stable_id}"
    ET.SubElement(entry, qn(ATOM_NS, "updated")).text = updated
    ET.SubElement(
        entry,
        qn(ATOM_NS, "link"),
        {
            "rel": "http://opds-spec.org/image/thumbnail",
            "href": ICON_URL,
            "type": "image/png",
        },
    )
    ET.SubElement(
        entry,
        qn(ATOM_NS, "link"),
        {"rel": "http://opds-spec.org/image", "href": ICON_URL, "type": "image/png"},
    )
    ET.SubElement(
        entry,
        qn(ATOM_NS, "link"),
        {"rel": "http://opds-spec.org/acquisition", "href": download_url, "type": mime},
    )

tree = ET.ElementTree(feed)
ET.indent(tree, space="  ")
try:
    with open(xml_path, "wb") as f:
        tree.write(f, encoding="utf-8", xml_declaration=True)
    # html import kept for backward-compat; escaping is now done by ElementTree
    assert html is not None
    print(f"Success! catalog.xml generated with {len(books)} entries.")
except OSError as e:
    print(f"Error writing {xml_path}: {e}")
    raise
