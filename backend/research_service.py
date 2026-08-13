import re

import httpx
from bs4 import BeautifulSoup


SEARCH_URL = "https://html.duckduckgo.com/html/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0 Safari/537.36"
    )
}


def _clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "")
    return text.strip()


async def _search_web(
    client: httpx.AsyncClient,
    query: str,
    limit: int = 5,
):
    results = []

    response = await client.get(
        SEARCH_URL,
        headers=HEADERS,
        params={"q": query},
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for result in soup.select(".result"):
        link = result.select_one(".result__a")
        snippet = result.select_one(".result__snippet")

        if not link:
            continue

        title = _clean_text(
            link.get_text(" ", strip=True)
        )

        url = link.get("href", "")

        snippet_text = (
            _clean_text(
                snippet.get_text(" ", strip=True)
            )
            if snippet
            else ""
        )

        if not title or not url:
            continue

        results.append(
            {
                "title": title,
                "source": "DuckDuckGo Web Search",
                "url": url,
                "snippet": snippet_text,
                "source_type": "General Web Content",
            }
        )

        if len(results) >= limit:
            break

    return results


async def research_process(
    name: str,
    industry: str,
    description: str,
):
    results = []
    seen_urls = set()

    queries = [
        f'"{name}" "{industry}" business process',
        f'"{name}" operations {industry}',
        f'"{name}" AI automation {industry}',
    ]

    try:
        async with httpx.AsyncClient(
            timeout=15.0,
            follow_redirects=True,
            headers=HEADERS,
        ) as client:

            for query in queries:

                try:
                    search_results = await _search_web(
                        client,
                        query,
                        limit=5,
                    )

                    for result in search_results:
                        url = result["url"]

                        if url in seen_urls:
                            continue

                        seen_urls.add(url)
                        results.append(result)

                        if len(results) >= 5:
                            break

                except Exception as exc:
                    print(
                        f"Search failed for query "
                        f"'{query}': {exc}"
                    )

                if len(results) >= 5:
                    break

    except Exception as exc:
        print(
            f"Research service failed for "
            f"'{name}': {exc}"
        )

    if not results:
        results.append(
            {
                "title": f"Research unavailable: {name}",
                "source": "Research Service",
                "url": "",
                "snippet": (
                    f"No external public source was retrieved "
                    f"for '{name}'. The analysis may use the "
                    f"supplied process description, but this "
                    f"record is not external research evidence."
                ),
                "source_type": "Research Status",
            }
        )

    return results