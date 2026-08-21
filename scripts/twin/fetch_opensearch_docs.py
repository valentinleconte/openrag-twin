import httpx
from bs4 import BeautifulSoup
from markitdown import MarkItDown
import io
import os
import re
import sys

URLS = [
    "https://docs.opensearch.org/latest/getting-started/intro/",
    "https://docs.opensearch.org/latest/getting-started/concepts/",
    "https://docs.opensearch.org/latest/getting-started/",
    "https://docs.opensearch.org/latest/getting-started/ingest-data/",
    "https://docs.opensearch.org/latest/getting-started/search-data/",
    "https://docs.opensearch.org/latest/aggregations/",
    "https://docs.opensearch.org/latest/aggregations/bucket/global/",
    "https://docs.opensearch.org/latest/vector-search/getting-started/concepts/",
    "https://docs.opensearch.org/latest/vector-search/ai-search/hybrid-search/aggregations/",
    "https://docs.opensearch.org/latest/tutorials/",
    "https://docs.opensearch.org/latest/dashboards/getting-started/index/",
]

OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else "opensearch-docs-md"
os.makedirs(OUT_DIR, exist_ok=True)

md_converter = MarkItDown()


def slug_from_url(url: str) -> str:
    path = url.replace("https://docs.opensearch.org/latest/", "").strip("/")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", path).strip("-") or "index"
    return slug


results = []
for url in URLS:
    try:
        r = httpx.get(url, follow_redirects=True, timeout=30, headers={"User-Agent": "openrag-twin/1.0"})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        main = soup.find("main") or soup.body
        title_tag = soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else url
        for tag in main.find_all(["nav", "aside", "script", "style", "button", "footer"]):
            tag.decompose()
        html_str = str(main)
        result = md_converter.convert_stream(io.BytesIO(html_str.encode("utf-8")), file_extension=".html")
        content = result.text_content.strip()

        slug = slug_from_url(url)
        filename = f"{slug}.md"
        filepath = os.path.join(OUT_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"---\ntitle: {title}\nsource_url: {url}\n---\n\n")
            f.write(f"# {title}\n\n")
            f.write(f"Source: {url}\n\n")
            f.write(content)
            f.write("\n")

        results.append((url, filepath, len(content), True, None))
        print(f"OK  {url} -> {filepath} ({len(content)} chars)")
    except Exception as e:
        results.append((url, None, 0, False, str(e)))
        print(f"FAIL {url}: {e}")

ok = sum(1 for r in results if r[3])
print(f"\n{ok}/{len(URLS)} pages converties avec succès dans {OUT_DIR}/")
